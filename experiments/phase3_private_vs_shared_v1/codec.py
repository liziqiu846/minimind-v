"""Variable-dimension MMS2 encoding without legacy experiment dependencies."""

from __future__ import annotations

import struct
import zlib
from typing import Any, Mapping

import numpy as np
import torch

from experiments.quantize_stage2_adapter import (
    FORMAT_VERSION, HEADER, MAGIC, MODEL_GROUP_IDS, QUANTIZATION_BITS_LABEL,
    ROOT_IDS, quantize_coordinate,
)


def encode_coordinates(coordinates: Mapping[str, torch.Tensor], structure: str,
                       seed: int) -> tuple[bytes, dict[str, Any]]:
    model_group = "M2" if structure == "P" else "M3"
    expected = ("vision", "projector", "language") if structure == "P" else ("shared",)
    if set(coordinates) != set(expected):
        raise ValueError("coordinate groups differ from frozen structure")
    body_parts = []
    groups = []
    for name in expected:
        value = coordinates[name].detach().cpu().float()
        if value.ndim != 1:
            raise ValueError("coordinate tensor must be one-dimensional")
        scale, symbols = quantize_coordinate(value)
        body_parts.extend((
            struct.pack("<I", value.numel()),
            struct.pack("<f", scale),
            symbols.tobytes(),
        ))
        groups.append({
            "name": name,
            "dimension": value.numel(),
            "scale_float32": float(scale),
            "symbol_histogram": {
                str(level): int(np.count_nonzero(symbols == level + 3))
                for level in range(-3, 4)
            },
        })
    body = b"".join(body_parts)
    compressed = zlib.compress(body, level=9)
    header = HEADER.pack(
        MAGIC, FORMAT_VERSION, MODEL_GROUP_IDS[model_group], ROOT_IDS[seed],
        len(expected), QUANTIZATION_BITS_LABEL, len(body), len(compressed),
    )
    archive = header + compressed
    return archive, {
        "format": "MMS2",
        "format_version": FORMAT_VERSION,
        "codec": "zlib-9",
        "structure": structure,
        "mapping_root": seed,
        "coordinate_groups": groups,
        "archive_bytes": len(archive),
        "archive_bits": len(archive) * 8,
    }
