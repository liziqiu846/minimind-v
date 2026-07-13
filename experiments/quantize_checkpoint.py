#!/usr/bin/env python3
"""Quantize trainable parameter deltas into a deterministic checkpoint archive."""

import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path

import numpy as np
import torch


TIED_ALIASES = {"lm_head.weight": "model.embed_tokens.weight"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pack_codes(codes: torch.Tensor, bits: int) -> bytes:
    values = codes.to(torch.uint8).cpu().numpy().reshape(-1)
    shifts = np.arange(bits - 1, -1, -1, dtype=np.uint8)
    bit_stream = ((values[:, None] >> shifts) & 1).reshape(-1)
    return np.packbits(bit_stream, bitorder="big").tobytes()


def unpack_codes(payload: bytes, bits: int, count: int) -> torch.Tensor:
    bit_stream = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="big")
    bit_stream = bit_stream[: count * bits].reshape(count, bits)
    shifts = np.arange(bits - 1, -1, -1, dtype=np.uint8)
    values = (bit_stream << shifts).sum(axis=1, dtype=np.uint16)
    return torch.from_numpy(values.astype(np.int16))


def quantize_delta(delta: torch.Tensor, bits: int) -> tuple[float, torch.Tensor]:
    qmax = (1 << (bits - 1)) - 1
    maximum = delta.abs().max().item()
    scale = maximum / qmax if maximum else 0.0
    quantized = (
        torch.zeros_like(delta, dtype=torch.int16)
        if scale == 0.0
        else torch.round(delta / scale).clamp(-qmax, qmax).to(torch.int16)
    )
    return scale, quantized + qmax


def zip_entry(name: str) -> zipfile.ZipInfo:
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_STORED
    entry.external_attr = 0o600 << 16
    return entry


def encode_archive(
    trained_checkpoint: Path,
    reference_checkpoint: Path,
    trainable_names: list[str],
    bits: int,
    archive_path: Path,
) -> dict:
    if bits < 2 or bits > 8:
        raise ValueError("bits must be between 2 and 8")
    trained = torch.load(trained_checkpoint, map_location="cpu", weights_only=True)
    reference = torch.load(reference_checkpoint, map_location="cpu", weights_only=True)
    trainable = set(trainable_names)
    aliases = {
        alias: canonical
        for alias, canonical in TIED_ALIASES.items()
        if canonical in trainable and alias in trained
    }
    if any(not torch.equal(trained[alias], trained[canonical]) for alias, canonical in aliases.items()):
        raise ValueError("tied checkpoint weights are inconsistent")
    changed_frozen = [
        name
        for name in (trained.keys() & reference.keys()) - trainable - aliases.keys()
        if not torch.equal(trained[name], reference[name])
    ]
    unexplained = set(trained) - set(reference) - trainable - aliases.keys()
    if changed_frozen or unexplained or not trainable.issubset(trained):
        raise ValueError("checkpoint changes do not match manifest trainable parameters")

    tensors, payloads = [], []
    for index, name in enumerate(trainable_names):
        value = trained[name].float()
        baseline = reference[name].float() if name in reference else torch.zeros_like(value)
        scale, codes = quantize_delta(value - baseline, bits)
        entry = f"tensors/{index:04d}.bin"
        payload = pack_codes(codes, bits)
        tensors.append(
            {
                "name": name,
                "shape": list(value.shape),
                "numel": value.numel(),
                "scale": scale,
                "baseline": "reference" if name in reference else "zero",
                "entry": entry,
                "payload_bits": value.numel() * bits,
                "stored_bytes": len(payload),
            }
        )
        payloads.append((entry, payload))

    metadata = {
        "schema_version": 1,
        "algorithm": "per_tensor_symmetric_uniform_delta",
        "quantization_bits": bits,
        "reference_sha256": sha256_file(reference_checkpoint),
        "trained_checkpoint_sha256": sha256_file(trained_checkpoint),
        "parameter_count": sum(item["numel"] for item in tensors),
        "tied_aliases": aliases,
        "tensors": tensors,
    }
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        encoded_metadata = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        archive.writestr(zip_entry("metadata.json"), encoded_metadata.encode("utf-8"))
        for entry, payload in payloads:
            archive.writestr(zip_entry(entry), payload)
    os.replace(temporary, archive_path)
    return metadata


def read_metadata(archive_path: Path) -> dict:
    with zipfile.ZipFile(archive_path) as archive:
        return json.loads(archive.read("metadata.json"))


def decode_archive(
    archive_path: Path, reference_checkpoint: Path, output_checkpoint: Path
) -> dict:
    reference = torch.load(reference_checkpoint, map_location="cpu", weights_only=True)
    with zipfile.ZipFile(archive_path) as archive:
        metadata = json.loads(archive.read("metadata.json"))
        if sha256_file(reference_checkpoint) != metadata["reference_sha256"]:
            raise ValueError("reference checkpoint hash does not match archive")
        bits = metadata["quantization_bits"]
        qmax = (1 << (bits - 1)) - 1
        decoded = dict(reference)
        for item in metadata["tensors"]:
            codes = unpack_codes(archive.read(item["entry"]), bits, item["numel"])
            delta = (codes - qmax).float().mul_(item["scale"]).reshape(item["shape"])
            baseline = reference[item["name"]].float() if item["baseline"] == "reference" else 0.0
            decoded[item["name"]] = (baseline + delta).half()
        for alias, canonical in metadata["tied_aliases"].items():
            decoded[alias] = decoded[canonical]

    output_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_checkpoint.with_suffix(output_checkpoint.suffix + ".tmp")
    torch.save(decoded, temporary)
    os.replace(temporary, output_checkpoint)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bits", type=int, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--decoded-checkpoint", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = args.run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    run_id = manifest["run_id"]
    hidden_size = manifest["model"]["hidden_size"]
    trained = args.run_dir / "weights" / f"{run_id}_{hidden_size}.pth"
    reference = Path(manifest["initial_weight"]["path"])
    summary_path = args.summary or args.archive.with_suffix(".json")
    outputs = (args.archive, args.decoded_checkpoint, summary_path)
    if not args.overwrite and any(path.exists() for path in outputs):
        raise FileExistsError("one or more output files already exist")

    metadata = encode_archive(
        trained,
        reference,
        manifest["model"]["trainable_parameter_names"],
        args.bits,
        args.archive,
    )
    decode_archive(args.archive, reference, args.decoded_checkpoint)
    result = {
        "run_id": run_id,
        "archive": str(args.archive.resolve()),
        "archive_sha256": sha256_file(args.archive),
        "encoded_weight_bits": args.archive.stat().st_size * 8,
        "decoded_checkpoint": str(args.decoded_checkpoint.resolve()),
        "decoded_checkpoint_sha256": sha256_file(args.decoded_checkpoint),
        "quantization_bits": args.bits,
        "parameter_count": metadata["parameter_count"],
        "fixed_width_payload_bits": metadata["parameter_count"] * args.bits,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
