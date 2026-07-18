#!/usr/bin/env python3
"""Encode and decode Stage 2 coordinates in the frozen MMS2 v1 format."""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import zlib
from pathlib import Path
from typing import Mapping

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_model import (
    build_stage2_model,
    model_structure_receipt,
    tensor_state_sha256,
)
from experiments.stage2_protocol import (
    DEFAULT_DRAFT,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)
from model.global_subspace_lora import (
    GROUP_DIMENSIONS,
    coordinate_state,
    load_coordinate_state,
)


MAGIC = b"MMS2"
FORMAT_VERSION = 1
QUANTIZATION_BITS_LABEL = 3
MODEL_GROUP_IDS = {"M0": 0, "M1": 1, "M2": 2, "M3": 3}
MODEL_GROUP_NAMES = {value: key for key, value in MODEL_GROUP_IDS.items()}
ROOT_IDS = {None: 0, 43101: 1, 43102: 2, 43103: 3}
ROOT_VALUES = {value: key for key, value in ROOT_IDS.items()}
HEADER = struct.Struct("<4sBBBBBII")


def ordered_coordinate_names(model_group: str) -> tuple[str, ...]:
    return tuple(GROUP_DIMENSIONS[model_group])


def quantize_coordinate(value: torch.Tensor) -> tuple[np.float32, np.ndarray]:
    array = value.detach().cpu().to(torch.float32).contiguous().numpy()
    maximum = np.max(np.abs(array), initial=np.float32(0)).astype(np.float32)
    if maximum == 0:
        return np.float32(0), np.full(array.shape, 3, dtype=np.uint8)
    scale = np.float32(maximum / np.float32(3))
    quantized = np.clip(np.rint(array / scale), -3, 3).astype(np.int8)
    return scale, (quantized.astype(np.int16) + 3).astype(np.uint8)


def encode_mms2(
    coordinates: Mapping[str, torch.Tensor], model_group: str, mapping_root: int | None
) -> tuple[bytes, dict]:
    if model_group not in MODEL_GROUP_IDS:
        raise ValueError(f"unknown model group {model_group}")
    if model_group == "M1":
        if mapping_root is not None:
            raise ValueError("M1 mapping root must be null")
    elif mapping_root not in (43101, 43102, 43103):
        raise ValueError("M0/M2/M3 mapping root is not predeclared")
    names = ordered_coordinate_names(model_group)
    if set(coordinates) != set(names):
        raise ValueError("coordinate groups do not match model group")
    body_parts = []
    groups = []
    for name in names:
        value = coordinates[name]
        expected_dimension = GROUP_DIMENSIONS[model_group][name]
        if value.ndim != 1 or value.numel() != expected_dimension:
            raise ValueError(f"coordinate dimension mismatch for {name}")
        scale, symbols = quantize_coordinate(value)
        body_parts.extend(
            (struct.pack("<I", expected_dimension), struct.pack("<f", scale), symbols.tobytes())
        )
        groups.append(
            {
                "name": name,
                "dimension": expected_dimension,
                "scale_float32": float(scale),
                "symbol_histogram": {
                    str(level): int(np.count_nonzero(symbols == level + 3))
                    for level in range(-3, 4)
                },
            }
        )
    body = b"".join(body_parts)
    compressed = zlib.compress(body, level=9)
    header = HEADER.pack(
        MAGIC,
        FORMAT_VERSION,
        MODEL_GROUP_IDS[model_group],
        ROOT_IDS[mapping_root],
        len(names),
        QUANTIZATION_BITS_LABEL,
        len(body),
        len(compressed),
    )
    archive = header + compressed
    return archive, {
        "model_group": model_group,
        "mapping_root": mapping_root,
        "model_group_id": MODEL_GROUP_IDS[model_group],
        "mapping_root_id": ROOT_IDS[mapping_root],
        "coordinate_groups": groups,
        "uncompressed_body_bytes": len(body),
        "compressed_body_bytes": len(compressed),
        "archive_bytes": len(archive),
        "complexity_bits": len(archive) * 8,
    }


def decode_mms2(payload: bytes) -> tuple[dict[str, torch.Tensor], dict]:
    if len(payload) < HEADER.size:
        raise ValueError("MMS2 archive is shorter than its header")
    (
        magic,
        version,
        model_group_id,
        root_id,
        group_count,
        bits_label,
        body_length,
        compressed_length,
    ) = HEADER.unpack_from(payload)
    if magic != MAGIC or version != FORMAT_VERSION or bits_label != QUANTIZATION_BITS_LABEL:
        raise ValueError("unsupported MMS2 header")
    if model_group_id not in MODEL_GROUP_NAMES or root_id not in ROOT_VALUES:
        raise ValueError("unknown MMS2 model group or mapping root ID")
    model_group = MODEL_GROUP_NAMES[model_group_id]
    mapping_root = ROOT_VALUES[root_id]
    if (model_group == "M1") != (mapping_root is None):
        raise ValueError("MMS2 model group and mapping root are inconsistent")
    names = ordered_coordinate_names(model_group)
    if group_count != len(names):
        raise ValueError("MMS2 coordinate group count is inconsistent")
    if len(payload) != HEADER.size + compressed_length:
        raise ValueError("MMS2 compressed length is inconsistent")
    decompressor = zlib.decompressobj()
    body = decompressor.decompress(payload[HEADER.size:]) + decompressor.flush()
    if not decompressor.eof or decompressor.unused_data or len(body) != body_length:
        raise ValueError("MMS2 body is invalid")
    coordinates: dict[str, torch.Tensor] = {}
    groups = []
    offset = 0
    for name in names:
        if offset + 8 > len(body):
            raise ValueError("MMS2 coordinate group header is truncated")
        dimension = struct.unpack_from("<I", body, offset)[0]
        scale = struct.unpack_from("<f", body, offset + 4)[0]
        offset += 8
        expected = GROUP_DIMENSIONS[model_group][name]
        if dimension != expected or offset + dimension > len(body):
            raise ValueError(f"MMS2 coordinate dimension is invalid for {name}")
        symbols = np.frombuffer(body, dtype=np.uint8, count=dimension, offset=offset).copy()
        offset += dimension
        if np.any(symbols > 6) or not np.isfinite(scale) or scale < 0:
            raise ValueError("MMS2 contains an invalid scale or symbol")
        quantized = symbols.astype(np.int16) - 3
        decoded = (quantized.astype(np.float32) * np.float32(scale)).astype(np.float32)
        coordinates[name] = torch.from_numpy(decoded.copy())
        groups.append({"name": name, "dimension": dimension, "scale_float32": scale})
    if offset != len(body):
        raise ValueError("MMS2 body has trailing bytes")
    return coordinates, {
        "model_group": model_group,
        "mapping_root": mapping_root,
        "model_group_id": model_group_id,
        "mapping_root_id": root_id,
        "coordinate_groups": groups,
        "uncompressed_body_bytes": body_length,
        "compressed_body_bytes": compressed_length,
        "archive_bytes": len(payload),
        "complexity_bits": len(payload) * 8,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("encode", "decode"), required=True)
    parser.add_argument("--model-group", choices=tuple(MODEL_GROUP_IDS))
    parser.add_argument("--mapping-root", type=int)
    parser.add_argument("--coordinates", type=Path)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DRAFT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol)
    protocol.verify_immutable_inputs()
    if protocol.is_frozen and protocol.payload.get("schema_version") == 2:
        protocol.verify_runtime_integrity()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    decoded_path = args.output_dir / "decoded_coordinates.pt"
    summary_path = args.output_dir / "adapter_summary.json"
    model_hash_path = args.output_dir / "decoded_model_hash.json"
    outputs = (decoded_path, summary_path, model_hash_path)
    if any(path.exists() for path in outputs):
        raise FileExistsError("MMS2 output already exists")

    if args.mode == "encode":
        if not args.coordinates or not args.model_group:
            raise ValueError("encode requires --coordinates and --model-group")
        if args.archive.exists():
            raise FileExistsError(f"archive already exists: {args.archive}")
        stored = torch.load(args.coordinates, map_location="cpu", weights_only=True)
        values = stored.get("coordinates", stored)
        archive, summary = encode_mms2(values, args.model_group, args.mapping_root)
        args.archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.archive.with_name(args.archive.name + ".tmp")
        temporary.write_bytes(archive)
        os.replace(temporary, args.archive)
    else:
        archive = args.archive.read_bytes()
        values, summary = decode_mms2(archive)
        if args.model_group and summary["model_group"] != args.model_group:
            raise ValueError("decoded model group differs from command line")
        if args.mapping_root and summary["mapping_root"] != args.mapping_root:
            raise ValueError("decoded mapping root differs from command line")

    decoded, independent_summary = decode_mms2(args.archive.read_bytes())
    for key in (
        "model_group", "mapping_root", "model_group_id", "mapping_root_id",
        "uncompressed_body_bytes", "compressed_body_bytes", "archive_bytes",
        "complexity_bits",
    ):
        if independent_summary[key] != summary[key]:
            raise RuntimeError(f"independent MMS2 decode metadata differs for {key}")
    temporary = decoded_path.with_name(decoded_path.name + ".tmp")
    torch.save(decoded, temporary)
    os.replace(temporary, decoded_path)

    model = build_stage2_model(
        independent_summary["model_group"],
        protocol,
        independent_summary["mapping_root"],
        device="cpu",
    )
    load_coordinate_state(model, decoded)
    reconstructed = coordinate_state(model)
    if any(not torch.equal(decoded[name], reconstructed[name]) for name in decoded):
        raise RuntimeError("decoded coordinates do not load exactly")
    model_hash = {
        "hash_protocol": "stage2-tensor-state-v1",
        "decoded_model_state_sha256": tensor_state_sha256(model.state_dict()),
        "structure": model_structure_receipt(model),
        "adapter_sha256": sha256_file(args.archive),
        "decoded_coordinates_sha256": None,
        "protocol": protocol.reference(),
    }
    write_json_atomic(model_hash_path, model_hash)
    model_hash["decoded_coordinates_sha256"] = sha256_file(decoded_path)
    write_json_atomic(model_hash_path, model_hash)
    summary.update(
        {
            "format": "MMS2",
            "format_version": FORMAT_VERSION,
            "quantization_bits_label": QUANTIZATION_BITS_LABEL,
            "codec": "zlib-9",
            "archive_path": str(args.archive.resolve()),
            "archive_sha256": sha256_file(args.archive),
            "decoded_coordinates_path": str(decoded_path.resolve()),
            "decoded_coordinates_sha256": sha256_file(decoded_path),
            "decoded_model_hash_path": str(model_hash_path.resolve()),
            "decoded_model_hash_sha256": sha256_file(model_hash_path),
            "protocol": protocol.reference(),
        }
    )
    write_json_atomic(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
