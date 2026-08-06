"""Variable-dimension MMS2 codec for the preregistered P/S matrix."""

from __future__ import annotations

import struct
import zlib
from typing import Any, Mapping

import numpy as np
import torch

from experiments.phase3_private_vs_shared_v1.codec import encode_coordinates
from experiments.quantize_stage2_adapter import (
    FORMAT_VERSION,
    HEADER,
    MAGIC,
    MODEL_GROUP_NAMES,
    QUANTIZATION_BITS_LABEL,
    ROOT_VALUES,
)


def decode_coordinates(payload: bytes) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    if len(payload) < HEADER.size:
        raise ValueError("MMS2 archive is truncated")
    magic, version, group_id, root_id, count, bits, body_size, compressed_size = (
        HEADER.unpack_from(payload)
    )
    if (
        magic != MAGIC
        or version != FORMAT_VERSION
        or bits != QUANTIZATION_BITS_LABEL
        or group_id not in MODEL_GROUP_NAMES
        or root_id not in ROOT_VALUES
        or len(payload) != HEADER.size + compressed_size
    ):
        raise ValueError("invalid MMS2 header")
    structure = "P" if MODEL_GROUP_NAMES[group_id] == "M2" else "S"
    names = ("vision", "projector", "language") if structure == "P" else ("shared",)
    if count != len(names):
        raise ValueError("MMS2 group count differs from structure")
    body = zlib.decompress(payload[HEADER.size:])
    if len(body) != body_size:
        raise ValueError("MMS2 body size mismatch")
    offset = 0
    coordinates = {}
    groups = []
    for name in names:
        if offset + 8 > len(body):
            raise ValueError("MMS2 group header is truncated")
        dimension, scale = struct.unpack_from("<If", body, offset)
        offset += 8
        symbols = np.frombuffer(body, dtype=np.uint8, count=dimension, offset=offset)
        offset += dimension
        if len(symbols) != dimension or np.any(symbols > 6) or not np.isfinite(scale):
            raise ValueError("invalid MMS2 coordinate symbols")
        array = (symbols.astype(np.int16) - 3).astype(np.float32) * np.float32(scale)
        coordinates[name] = torch.from_numpy(array.copy())
        groups.append({"name": name, "dimension": dimension, "scale_float32": scale})
    if offset != len(body):
        raise ValueError("MMS2 body has trailing bytes")
    return coordinates, {
        "structure": structure,
        "mapping_root": ROOT_VALUES[root_id],
        "coordinate_groups": groups,
        "archive_bytes": len(payload),
        "archive_bits": len(payload) * 8,
    }


def encode_and_verify(
    coordinates: Mapping[str, torch.Tensor], structure: str, seed: int
) -> tuple[bytes, dict[str, Any]]:
    archive, receipt = encode_coordinates(coordinates, structure, seed)
    decoded, decoded_receipt = decode_coordinates(archive)
    if set(decoded) != set(coordinates):
        raise RuntimeError("MMS2 round trip changed coordinate groups")
    return archive, {**receipt, "decoded": decoded_receipt}

