"""MMS2-compatible encoding with predeclared variable coordinate dimensions."""

from __future__ import annotations

import struct
import zlib
from collections import OrderedDict
from typing import Any, Mapping

import numpy as np
import torch

from experiments.quantize_stage2_adapter import (
    FORMAT_VERSION,
    HEADER,
    MAGIC,
    MODEL_GROUP_IDS,
    MODEL_GROUP_NAMES,
    QUANTIZATION_BITS_LABEL,
    ROOT_IDS,
    ROOT_VALUES,
    encode_mms2,
    quantize_coordinate,
)
from model.global_subspace_lora import GROUP_DIMENSIONS, MAPPING_ROOTS


GROUP_NAMES = {
    "M2": ("vision", "projector", "language"),
    "M3": ("shared",),
}


def _dimensions(
    model_group: str, dimensions: Mapping[str, int]
) -> OrderedDict[str, int]:
    if (
        model_group not in GROUP_NAMES
        or set(dimensions) != set(GROUP_NAMES[model_group])
    ):
        raise ValueError("codec coordinate groups are invalid")
    clean = OrderedDict(
        (name, int(dimensions[name])) for name in GROUP_NAMES[model_group]
    )
    if any(dimension <= 0 for dimension in clean.values()):
        raise ValueError("codec dimensions must be positive")
    return clean


def encode_budget_mms2(
    coordinates: Mapping[str, torch.Tensor],
    model_group: str,
    mapping_root: int,
    dimensions: Mapping[str, int],
) -> tuple[bytes, dict[str, Any]]:
    clean_dimensions = _dimensions(model_group, dimensions)
    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    if set(coordinates) != set(clean_dimensions):
        raise ValueError("coordinate tensors do not match configured groups")
    body_parts = []
    groups = []
    for name, dimension in clean_dimensions.items():
        value = coordinates[name]
        if value.ndim != 1 or value.numel() != dimension:
            raise ValueError(f"coordinate dimension mismatch for {name}")
        scale, symbols = quantize_coordinate(value)
        body_parts.extend(
            (
                struct.pack("<I", dimension),
                struct.pack("<f", scale),
                symbols.tobytes(),
            )
        )
        groups.append(
            {
                "name": name,
                "dimension": dimension,
                "scale_float32": float(scale),
                "symbol_histogram": {
                    str(level): int(
                        np.count_nonzero(symbols == level + 3)
                    )
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
        len(clean_dimensions),
        QUANTIZATION_BITS_LABEL,
        len(body),
        len(compressed),
    )
    archive = header + compressed
    return archive, {
        "format": "MMS2",
        "format_version": FORMAT_VERSION,
        "model_group": model_group,
        "mapping_root": mapping_root,
        "coordinate_groups": groups,
        "uncompressed_body_bytes": len(body),
        "compressed_body_bytes": len(compressed),
        "archive_bytes": len(archive),
        "archive_bits": len(archive) * 8,
        "codec": "zlib-9",
        "quantization_bits_label": QUANTIZATION_BITS_LABEL,
    }


def decode_budget_mms2(
    payload: bytes, dimensions: Mapping[str, int]
) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
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
    if (
        magic != MAGIC
        or version != FORMAT_VERSION
        or bits_label != QUANTIZATION_BITS_LABEL
        or model_group_id not in MODEL_GROUP_NAMES
        or root_id not in ROOT_VALUES
    ):
        raise ValueError("unsupported budget MMS2 header")
    model_group = MODEL_GROUP_NAMES[model_group_id]
    if model_group not in GROUP_NAMES:
        raise ValueError("budget MMS2 supports only M2 and M3")
    clean_dimensions = _dimensions(model_group, dimensions)
    mapping_root = ROOT_VALUES[root_id]
    if mapping_root not in MAPPING_ROOTS or group_count != len(clean_dimensions):
        raise ValueError("budget MMS2 identity/group count is invalid")
    if len(payload) != HEADER.size + compressed_length:
        raise ValueError("budget MMS2 compressed length mismatch")
    decompressor = zlib.decompressobj()
    body = decompressor.decompress(payload[HEADER.size:]) + decompressor.flush()
    if not decompressor.eof or decompressor.unused_data or len(body) != body_length:
        raise ValueError("budget MMS2 body is invalid")
    coordinates = {}
    groups = []
    offset = 0
    for name, expected_dimension in clean_dimensions.items():
        if offset + 8 > len(body):
            raise ValueError("budget MMS2 group header is truncated")
        dimension = struct.unpack_from("<I", body, offset)[0]
        scale = struct.unpack_from("<f", body, offset + 4)[0]
        offset += 8
        if dimension != expected_dimension or offset + dimension > len(body):
            raise ValueError(f"budget MMS2 dimension is invalid for {name}")
        symbols = np.frombuffer(
            body, dtype=np.uint8, count=dimension, offset=offset
        ).copy()
        offset += dimension
        if np.any(symbols > 6) or not np.isfinite(scale) or scale < 0:
            raise ValueError("budget MMS2 contains invalid symbols or scale")
        quantized = symbols.astype(np.int16) - 3
        decoded = (
            quantized.astype(np.float32) * np.float32(scale)
        ).astype(np.float32)
        coordinates[name] = torch.from_numpy(decoded.copy())
        groups.append(
            {
                "name": name,
                "dimension": dimension,
                "scale_float32": float(scale),
            }
        )
    if offset != len(body):
        raise ValueError("budget MMS2 body has trailing bytes")
    return coordinates, {
        "format": "MMS2",
        "format_version": FORMAT_VERSION,
        "model_group": model_group,
        "mapping_root": mapping_root,
        "coordinate_groups": groups,
        "archive_bytes": len(payload),
        "archive_bits": len(payload) * 8,
        "codec": "zlib-9",
    }


def check_current_codec_equivalence() -> dict[str, Any]:
    checks = []
    for model_group in ("M2", "M3"):
        dimensions = GROUP_DIMENSIONS[model_group]
        coordinates = {
            name: torch.linspace(
                -1.0 - index * 0.1,
                1.0 + index * 0.1,
                dimension,
                dtype=torch.float32,
            )
            for index, (name, dimension) in enumerate(dimensions.items())
        }
        for root in MAPPING_ROOTS:
            old_payload, _ = encode_mms2(
                coordinates, model_group, root
            )
            new_payload, new_summary = encode_budget_mms2(
                coordinates, model_group, root, dimensions
            )
            if old_payload != new_payload:
                raise AssertionError(
                    f"current MMS2 bytes differ for {model_group}/{root}"
                )
            decoded, decoded_summary = decode_budget_mms2(
                new_payload, dimensions
            )
            reencoded, _ = encode_budget_mms2(
                decoded, model_group, root, dimensions
            )
            if reencoded != new_payload:
                raise AssertionError("budget MMS2 round trip is not byte exact")
            checks.append(
                {
                    "method": model_group,
                    "mapping_root": root,
                    "coordinate_dimensions": dict(dimensions),
                    "archive_bits": new_summary["archive_bits"],
                    "old_new_byte_equivalence": True,
                    "decode_reencode_byte_equivalence": True,
                    "decoded_model_group": decoded_summary["model_group"],
                }
            )
    return {"status": "passed", "checks": checks}
