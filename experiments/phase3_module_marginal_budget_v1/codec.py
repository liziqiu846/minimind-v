"""Module-separable encoding using the existing MMS2 quantizer and zlib rule."""

from __future__ import annotations

import struct
import zlib
from typing import Any, Mapping

import numpy as np
import torch

from experiments.quantize_stage2_adapter import quantize_coordinate

from . import MODULES

MAGIC = b"MMB1"
VERSION = 1
MODULE_IDS = {name: index for index, name in enumerate(MODULES)}
MODULE_NAMES = {value: key for key, value in MODULE_IDS.items()}
HEADER = struct.Struct("<4sBBII")


def _encode_module(name: str, value: torch.Tensor) -> tuple[bytes, dict[str, Any]]:
    if name not in MODULE_IDS:
        raise ValueError("unknown module")
    tensor = value.detach().cpu().float()
    if tensor.ndim != 1 or tensor.numel() <= 0:
        raise ValueError("coordinate tensor must be a non-empty vector")
    scale, symbols = quantize_coordinate(tensor)
    body = struct.pack("<If", tensor.numel(), scale) + symbols.tobytes()
    compressed = zlib.compress(body, level=9)
    archive = (
        HEADER.pack(MAGIC, VERSION, MODULE_IDS[name], len(body), len(compressed))
        + compressed
    )
    return archive, {
        "module": name,
        "coordinate_dimension": tensor.numel(),
        "scale_float32": float(scale),
        "symbol_histogram": {
            str(level): int(np.count_nonzero(symbols == level + 3))
            for level in range(-3, 4)
        },
        "encoded_bytes": len(archive),
        "encoded_bits": len(archive) * 8,
    }


def encode_coordinates(
    coordinates: Mapping[str, torch.Tensor],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    if set(coordinates) != set(MODULES):
        raise ValueError(f"private coordinates must contain exactly {MODULES}")
    archives: dict[str, bytes] = {}
    groups: dict[str, dict[str, Any]] = {}
    for name in MODULES:
        archives[name], groups[name] = _encode_module(name, coordinates[name])
    module_bits = {name: groups[name]["encoded_bits"] for name in MODULES}
    total_bits = sum(module_bits.values())
    return archives, {
        "format": "MMB1-module-separable",
        "format_version": VERSION,
        "quantizer": "existing-MMS2-seven-level-float32-scale",
        "codec": "zlib-9-per-module",
        "coordinate_groups": groups,
        "module_wise_encoded_bits": module_bits,
        "vision_encoded_bits": module_bits["vision"],
        "projector_encoded_bits": module_bits["projector"],
        "language_encoded_bits": module_bits["language"],
        "total_encoded_bits": total_bits,
        "total_encoded_bytes": sum(len(archives[name]) for name in MODULES),
        "budget_measure": "actual_encoded_bits",
    }


def decode_module(payload: bytes) -> tuple[str, torch.Tensor]:
    if len(payload) < HEADER.size:
        raise ValueError("module archive is shorter than its header")
    magic, version, module_id, body_length, compressed_length = HEADER.unpack_from(
        payload
    )
    if magic != MAGIC or version != VERSION or module_id not in MODULE_NAMES:
        raise ValueError("unsupported module archive header")
    if len(payload) != HEADER.size + compressed_length:
        raise ValueError("module archive compressed length mismatch")
    body = zlib.decompress(payload[HEADER.size :])
    if len(body) != body_length or len(body) < 8:
        raise ValueError("module archive body length mismatch")
    dimension, scale = struct.unpack_from("<If", body)
    symbols = np.frombuffer(body, dtype=np.uint8, offset=8).copy()
    if (
        dimension <= 0
        or symbols.size != dimension
        or np.any(symbols > 6)
        or not np.isfinite(scale)
        or scale < 0
    ):
        raise ValueError("module archive body is invalid")
    values = (symbols.astype(np.int16) - 3).astype(np.float32) * np.float32(scale)
    return MODULE_NAMES[module_id], torch.from_numpy(values.copy())


def decode_coordinates(archives: Mapping[str, bytes]) -> dict[str, torch.Tensor]:
    if set(archives) != set(MODULES):
        raise ValueError(f"module archives must contain exactly {MODULES}")
    decoded = {}
    for expected in MODULES:
        observed, tensor = decode_module(archives[expected])
        if observed != expected:
            raise ValueError("module archive is stored under the wrong name")
        decoded[expected] = tensor
    return decoded


def assert_round_trip(archives: Mapping[str, bytes]) -> dict[str, torch.Tensor]:
    decoded = decode_coordinates(archives)
    reencoded, _ = encode_coordinates(decoded)
    if dict(archives) != reencoded:
        raise AssertionError("module codec decode/re-encode is not byte exact")
    return decoded


def load_decoded_coordinates(
    store: torch.nn.Module, archives: Mapping[str, bytes]
) -> dict[str, torch.Tensor]:
    """Load quantized coordinates and verify the model-side state exactly."""
    decoded = assert_round_trip(archives)
    coordinates = getattr(store, "coordinates", None)
    if coordinates is None or set(coordinates) != set(MODULES):
        raise ValueError("target is not a private three-module coordinate store")
    with torch.no_grad():
        for name in MODULES:
            if coordinates[name].shape != decoded[name].shape:
                raise ValueError(f"decoded coordinate shape differs for {name}")
            coordinates[name].copy_(decoded[name])
    reconstructed = {name: coordinates[name].detach().cpu() for name in MODULES}
    if any(not torch.equal(reconstructed[name], decoded[name]) for name in MODULES):
        raise AssertionError("decoded coordinates do not load into the model exactly")
    return decoded
