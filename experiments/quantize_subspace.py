#!/usr/bin/env python3
"""Compactly quantize the two coordinates of a fixed subspace projector."""

import argparse
import json
import math
import os
import struct
import sys
import zlib
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.quantize_checkpoint import (
    pack_codes,
    quantize_delta,
    sha256_file,
    unpack_codes,
)


COORDINATE_NAMES = (
    "vision_proj.input_projection.coordinates",
    "vision_proj.output_projection.coordinates",
)


def coordinate_spec(manifest: dict) -> tuple[tuple[str, int], ...]:
    projector = manifest["model"]["projector"]
    dimension = projector["subspace_dim"]
    names = tuple(manifest["model"]["trainable_parameter_names"])
    expected = COORDINATE_NAMES
    counts = (dimension // 2, dimension - dimension // 2)
    if projector.get("train_norm", False):
        norm_names = (
            "vision_proj.normalization_scale",
            "vision_proj.normalization_bias",
        )
        expected = norm_names + expected
        hidden_size = manifest["model"]["hidden_size"]
        counts = (hidden_size, hidden_size) + counts
    if projector["type"] != "subspace" or names != expected:
        raise ValueError("compact encoding requires the fixed two-coordinate protocol")
    return tuple(zip(names, counts, strict=True))


def validate_checkpoint(trained: dict, reference: dict, spec) -> None:
    coordinate_names = {name for name, _ in spec}
    changed_frozen = [
        name
        for name in trained.keys() & reference.keys() - coordinate_names
        if not torch.equal(trained[name], reference[name])
    ]
    unexplained = set(trained) - set(reference) - coordinate_names
    if changed_frozen or unexplained:
        raise ValueError("checkpoint contains changes outside the subspace coordinates")
    for name, count in spec:
        if name not in trained or trained[name].numel() != count:
            raise ValueError("checkpoint coordinates do not match the recorded dimension")


def encode_compact(trained: dict, spec, bits: int) -> bytes:
    chunks = []
    for name, _ in spec:
        scale, codes = quantize_delta(trained[name].float(), bits)
        chunks.extend((struct.pack("<f", scale), pack_codes(codes, bits)))
    return b"".join(chunks)


def decode_compact(payload: bytes, reference: dict, spec, bits: int) -> dict:
    decoded, offset = dict(reference), 0
    for name, count in spec:
        scale = struct.unpack_from("<f", payload, offset)[0]
        offset += 4
        stored_bytes = math.ceil(count * bits / 8)
        codes = unpack_codes(payload[offset : offset + stored_bytes], bits, count)
        offset += stored_bytes
        qmax = (1 << (bits - 1)) - 1
        decoded[name] = ((codes - qmax).float() * scale).half()
    if offset != len(payload):
        raise ValueError("compact archive has an unexpected length")
    return decoded


def encode_entropy(trained: dict, spec, bits: int) -> bytes:
    scales, all_codes = [], []
    for name, _ in spec:
        scale, codes = quantize_delta(trained[name].float(), bits)
        scales.append(struct.pack("<f", scale))
        all_codes.append(codes.to(torch.uint8))
    symbols = torch.cat(all_codes).numpy().tobytes()
    return b"".join(scales) + zlib.compress(symbols, level=9)


def decode_entropy(payload: bytes, reference: dict, spec, bits: int) -> dict:
    scale_bytes = 4 * len(spec)
    scales = struct.unpack(f"<{len(spec)}f", payload[:scale_bytes])
    decompressor = zlib.decompressobj()
    symbols = decompressor.decompress(payload[scale_bytes:]) + decompressor.flush()
    if (
        not decompressor.eof
        or decompressor.unused_data
        or len(symbols) != sum(count for _, count in spec)
    ):
        raise ValueError("entropy archive has an unexpected length")

    decoded, offset = dict(reference), 0
    qmax = (1 << (bits - 1)) - 1
    codes = torch.frombuffer(bytearray(symbols), dtype=torch.uint8).to(torch.int16)
    for (name, count), scale in zip(spec, scales, strict=True):
        decoded[name] = ((codes[offset : offset + count] - qmax).float() * scale).half()
        offset += count
    return decoded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bits", type=int, default=4)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--decoded-checkpoint", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--entropy-code", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = (args.archive, args.decoded_checkpoint, args.summary)
    if not args.overwrite and any(path.exists() for path in outputs):
        raise FileExistsError("one or more output files already exist")
    if not 2 <= args.bits <= 8:
        raise ValueError("bits must be between two and eight")

    manifest = json.loads((args.run_dir / "manifest.json").read_text())
    spec = coordinate_spec(manifest)
    run_id = manifest["run_id"]
    hidden_size = manifest["model"]["hidden_size"]
    trained_path = args.run_dir / "weights" / f"{run_id}_{hidden_size}.pth"
    reference_path = Path(manifest["initial_weight"]["path"])
    trained = torch.load(trained_path, map_location="cpu", weights_only=True)
    reference = torch.load(reference_path, map_location="cpu", weights_only=True)
    validate_checkpoint(trained, reference, spec)

    encoder = encode_entropy if args.entropy_code else encode_compact
    decoder = decode_entropy if args.entropy_code else decode_compact
    payload = encoder(trained, spec, args.bits)
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    args.decoded_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.archive.with_suffix(args.archive.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, args.archive)

    decoded = decoder(payload, reference, spec, args.bits)
    temporary = args.decoded_checkpoint.with_suffix(args.decoded_checkpoint.suffix + ".tmp")
    torch.save(decoded, temporary)
    os.replace(temporary, args.decoded_checkpoint)

    result = {
        "run_id": run_id,
        "algorithm": (
            "compact_fixed_subspace_symmetric_uniform_zlib"
            if args.entropy_code else "compact_fixed_subspace_symmetric_uniform"
        ),
        "archive": str(args.archive.resolve()),
        "archive_sha256": sha256_file(args.archive),
        "encoded_weight_bits": args.archive.stat().st_size * 8,
        "decoded_checkpoint": str(args.decoded_checkpoint.resolve()),
        "decoded_checkpoint_sha256": sha256_file(args.decoded_checkpoint),
        "reference_sha256": sha256_file(reference_path),
        "trained_checkpoint_sha256": sha256_file(trained_path),
        "quantization_bits": args.bits,
        "decoder_choice": {
            "family": "fixed_subspace",
            "subspace_dim": manifest["model"]["projector"]["subspace_dim"],
            "train_norm": manifest["model"]["projector"].get("train_norm", False),
            "quantization_bits": args.bits,
            "codec": "zlib" if args.entropy_code else "fixed_width",
        },
        "parameter_count": sum(count for _, count in spec),
        "fixed_width_payload_bits": sum(count for _, count in spec) * args.bits,
        "encoded_scale_bits": 32 * len(spec),
    }
    args.summary.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
