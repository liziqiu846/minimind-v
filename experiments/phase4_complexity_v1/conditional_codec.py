"""Canonical conditional-message codec under frozen public information A."""

from __future__ import annotations

import hashlib
import hmac
import math
import struct
import zlib
from dataclasses import dataclass
from typing import Any, Dict, Mapping

import numpy as np

from experiments.phase4_complexity_v1 import (
    CANDIDATE_ID_BITS,
    INVALID_CANDIDATE_ID,
)
from experiments.phase4_complexity_v1.candidate_registry import (
    Candidate,
    candidate_by_id,
)


SCALE = struct.Struct("<f")
COMPRESSED_LENGTH = struct.Struct("<I")
MESSAGE_DIGEST_BYTES = 32
MESSAGE_DIGEST_BITS = MESSAGE_DIGEST_BYTES * 8
ALIGNMENT_BITS = 4
LENGTH_BITS_PER_BLOCK = 32
SCALE_BITS_PER_BLOCK = 32
MAX_COMPRESSED_BLOCK_BYTES = 65536
FROZEN_ZLIB_VERSION = "1.3.1"
POSITIVE_ZERO_FLOAT32 = b"\x00\x00\x00\x00"
NEGATIVE_ZERO_FLOAT32 = b"\x00\x00\x00\x80"


@dataclass(frozen=True)
class QuantizedBlock:
    """An exact float32 scale bit pattern and signed seven-level symbols."""

    scale_bytes: bytes
    symbols: np.ndarray

    @property
    def scale_float32(self) -> np.float32:
        return np.float32(SCALE.unpack(self.scale_bytes)[0])


def _signed_symbols(value: Any, *, expected_dimension: int) -> np.ndarray:
    symbols = np.asarray(value)
    if (
        symbols.ndim != 1
        or int(symbols.size) != expected_dimension
        or not np.issubdtype(symbols.dtype, np.integer)
    ):
        raise ValueError("quantized symbols have the wrong shape or dtype")
    signed = symbols.astype(np.int16, copy=True)
    if np.any(signed < -3) or np.any(signed > 3):
        raise ValueError("quantized symbols must lie in -3 through 3")
    signed.setflags(write=False)
    return signed


def make_quantized_block(
    scale: Any,
    symbols: Any,
    *,
    expected_dimension: int,
) -> QuantizedBlock:
    if isinstance(scale, (bytes, bytearray, memoryview)):
        scale_bytes = bytes(scale)
        if len(scale_bytes) != SCALE.size:
            raise ValueError("scale byte representation must contain four bytes")
    else:
        try:
            scale_bytes = SCALE.pack(float(np.float32(scale)))
        except (TypeError, ValueError, OverflowError, struct.error) as error:
            raise ValueError("scale is not representable as float32") from error
    signed = _signed_symbols(symbols, expected_dimension=expected_dimension)
    numeric_scale = SCALE.unpack(scale_bytes)[0]
    if (
        not math.isfinite(numeric_scale)
        or numeric_scale < 0.0
        or scale_bytes == NEGATIVE_ZERO_FLOAT32
    ):
        raise ValueError("scale must be finite, nonnegative, and not negative zero")
    if numeric_scale == 0.0:
        if scale_bytes != POSITIVE_ZERO_FLOAT32 or np.any(signed != 0):
            raise ValueError("zero scale is canonical only for an all-zero block")
    elif not np.any(np.abs(signed) == 3):
        raise ValueError("nonzero quantization must contain an extreme symbol")
    return QuantizedBlock(scale_bytes=scale_bytes, symbols=signed)


def quantize_coordinates(value: Any) -> QuantizedBlock:
    """Apply the frozen seven-level float32 numerical quantization rule."""

    if hasattr(value, "detach"):
        value = value.detach().cpu().float()
        if hasattr(value, "numpy"):
            value = value.numpy()
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float32))
    if array.ndim != 1 or array.size <= 0:
        raise ValueError("coordinates must be a nonempty one-dimensional vector")
    maximum = np.max(np.abs(array), initial=np.float32(0)).astype(np.float32)
    if maximum == 0:
        scale = np.float32(0)
        signed = np.zeros(array.shape, dtype=np.int16)
    else:
        scale = np.float32(maximum / np.float32(3))
        signed = np.clip(np.rint(array / scale), -3, 3).astype(np.int16)
    return make_quantized_block(
        SCALE.pack(float(scale)),
        signed,
        expected_dimension=int(array.size),
    )


def pack_three_bit_symbols(symbols: np.ndarray) -> bytes:
    """Pack signed symbols MSB-first with zero low-bit tail padding."""

    signed = np.asarray(symbols, dtype=np.int16)
    if signed.ndim != 1 or np.any(signed < -3) or np.any(signed > 3):
        raise ValueError("cannot pack symbols outside the frozen seven levels")
    output = bytearray((3 * int(signed.size) + 7) // 8)
    for index, signed_value in enumerate(signed):
        code = int(signed_value) + 3
        start = index * 3
        for bit_index in range(3):
            bit = (code >> (2 - bit_index)) & 1
            absolute_bit = start + bit_index
            output[absolute_bit // 8] |= bit << (7 - absolute_bit % 8)
    return bytes(output)


def unpack_three_bit_symbols(payload: bytes, dimension: int) -> np.ndarray:
    expected_bytes = (3 * dimension + 7) // 8
    if len(payload) != expected_bytes:
        raise ValueError("packed symbol byte length differs from public dimension")
    total_symbol_bits = 3 * dimension
    padding_bits = expected_bytes * 8 - total_symbol_bits
    if padding_bits and payload[-1] & ((1 << padding_bits) - 1):
        raise ValueError("packed symbol tail padding is not zero")
    output = np.empty(dimension, dtype=np.int16)
    for index in range(dimension):
        start = index * 3
        code = 0
        for bit_index in range(3):
            absolute_bit = start + bit_index
            bit = (payload[absolute_bit // 8] >> (7 - absolute_bit % 8)) & 1
            code = (code << 1) | bit
        if code == 7:
            raise ValueError("packed symbol stream contains reserved code seven")
        output[index] = code - 3
    output.setflags(write=False)
    return output


def _normalize_blocks(
    candidate: Candidate,
    blocks: Mapping[str, QuantizedBlock],
) -> Dict[str, QuantizedBlock]:
    if tuple(blocks) != candidate.block_order or set(blocks) != set(
        candidate.block_order
    ):
        raise ValueError("coordinate block set or order differs from candidate")
    normalized: Dict[str, QuantizedBlock] = {}
    for block_name in candidate.block_order:
        block = blocks[block_name]
        if not isinstance(block, QuantizedBlock):
            raise ValueError("encoder requires exact QuantizedBlock values")
        normalized[block_name] = make_quantized_block(
            block.scale_bytes,
            block.symbols,
            expected_dimension=candidate.block_dimensions[block_name],
        )
    return normalized


def _summary(
    candidate: Candidate,
    block_rows: list[dict[str, Any]],
    message: bytes,
) -> dict[str, Any]:
    framing_bits = (
        ALIGNMENT_BITS
        + LENGTH_BITS_PER_BLOCK * len(candidate.block_order)
        + MESSAGE_DIGEST_BITS
    )
    scale_bits = sum(row["scale_bits"] for row in block_rows)
    compressed_bits = sum(
        row["compressed_symbol_bits"] for row in block_rows
    )
    paid_sum = (
        CANDIDATE_ID_BITS + framing_bits + scale_bits + compressed_bits
    )
    message_bits = len(message) * 8
    if paid_sum != message_bits:
        raise AssertionError("conditional message bit accounting is inconsistent")
    return {
        "schema": "phase4-conditional-message-receipt-v1",
        "candidate_id": candidate.candidate_id,
        "candidate_name": candidate.candidate_name,
        "method": candidate.method,
        "mapping_root": candidate.mapping_root,
        "candidate_id_bits": CANDIDATE_ID_BITS,
        "framing_bits": framing_bits,
        "alignment_bits": ALIGNMENT_BITS,
        "length_prefix_bits": LENGTH_BITS_PER_BLOCK
        * len(candidate.block_order),
        "integrity_bits": MESSAGE_DIGEST_BITS,
        "coordinate_blocks": block_rows,
        "total_scale_bits": scale_bits,
        "total_compressed_symbol_bits": compressed_bits,
        "conditional_message_bytes": len(message),
        "conditional_message_bits": message_bits,
        "message_sha256": hashlib.sha256(message).hexdigest(),
        "paid_field_bits_sum": paid_sum,
        "full_archive_bits_included": False,
        "public_information_A_bits_included": False,
    }


def encode_conditional_message(
    candidate_id: int,
    quantized_blocks: Mapping[str, QuantizedBlock],
) -> tuple[bytes, dict[str, Any]]:
    if (
        zlib.ZLIB_VERSION != FROZEN_ZLIB_VERSION
        or zlib.ZLIB_RUNTIME_VERSION != FROZEN_ZLIB_VERSION
    ):
        raise RuntimeError("conditional encoder zlib version differs from protocol")
    candidate = candidate_by_id(candidate_id)
    blocks = _normalize_blocks(candidate, quantized_blocks)
    prefix = bytearray([(candidate_id << 4) & 0xF0])
    block_rows = []
    for block_name in candidate.block_order:
        block = blocks[block_name]
        packed = pack_three_bit_symbols(block.symbols)
        compressed = zlib.compress(packed, level=9)
        if not compressed or len(compressed) > MAX_COMPRESSED_BLOCK_BYTES:
            raise ValueError("compressed symbol stream length is invalid")
        prefix.extend(block.scale_bytes)
        prefix.extend(COMPRESSED_LENGTH.pack(len(compressed)))
        prefix.extend(compressed)
        block_rows.append(
            {
                "block_name": block_name,
                "dimension": candidate.block_dimensions[block_name],
                "scale_bits": SCALE_BITS_PER_BLOCK,
                "scale_float32": float(block.scale_float32),
                "scale_bytes_hex": block.scale_bytes.hex(),
                "compressed_length_prefix_bits": LENGTH_BITS_PER_BLOCK,
                "compressed_symbol_bytes": len(compressed),
                "compressed_symbol_bits": len(compressed) * 8,
                "packed_symbol_bytes_before_compression": len(packed),
            }
        )
    message = bytes(prefix) + hashlib.sha256(prefix).digest()
    return message, _summary(candidate, block_rows, message)


def _decompress_exact(compressed: bytes, expected_bytes: int) -> bytes:
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(compressed, expected_bytes + 1)
        if (
            len(raw) > expected_bytes
            or decompressor.unconsumed_tail
        ):
            raise ValueError(
                "conditional symbol stream exceeds its public dimension"
            )
        raw += decompressor.flush()
    except zlib.error as error:
        raise ValueError("conditional symbol zlib stream is invalid") from error
    if (
        not decompressor.eof
        or decompressor.unused_data
        or len(raw) != expected_bytes
    ):
        raise ValueError("conditional symbol decompressed length is invalid")
    if zlib.compress(raw, level=9) != compressed:
        raise ValueError("conditional symbol stream is not canonical zlib-9")
    return raw


def decode_conditional_message(
    message: bytes,
) -> tuple[Dict[str, QuantizedBlock], dict[str, Any]]:
    if (
        zlib.ZLIB_VERSION != FROZEN_ZLIB_VERSION
        or zlib.ZLIB_RUNTIME_VERSION != FROZEN_ZLIB_VERSION
    ):
        raise RuntimeError("conditional decoder zlib version differs from protocol")
    payload = bytes(message)
    if len(payload) < 1 + MESSAGE_DIGEST_BYTES:
        raise ValueError("conditional message is truncated")
    prefix = payload[:-MESSAGE_DIGEST_BYTES]
    supplied_digest = payload[-MESSAGE_DIGEST_BYTES:]
    if not hmac.compare_digest(hashlib.sha256(prefix).digest(), supplied_digest):
        raise ValueError("conditional message SHA256 mismatch")
    candidate_id = prefix[0] >> 4
    if candidate_id == INVALID_CANDIDATE_ID or prefix[0] & 0x0F:
        raise ValueError("candidate header is invalid or has nonzero framing bits")
    candidate = candidate_by_id(candidate_id)
    offset = 1
    blocks: Dict[str, QuantizedBlock] = {}
    block_rows = []
    for block_name in candidate.block_order:
        if offset + SCALE.size + COMPRESSED_LENGTH.size > len(prefix):
            raise ValueError("conditional block header is truncated")
        scale_bytes = prefix[offset : offset + SCALE.size]
        offset += SCALE.size
        compressed_bytes = COMPRESSED_LENGTH.unpack_from(prefix, offset)[0]
        offset += COMPRESSED_LENGTH.size
        if (
            compressed_bytes < 1
            or compressed_bytes > MAX_COMPRESSED_BLOCK_BYTES
            or offset + compressed_bytes > len(prefix)
        ):
            raise ValueError("conditional compressed length is invalid")
        compressed = prefix[offset : offset + compressed_bytes]
        offset += compressed_bytes
        dimension = candidate.block_dimensions[block_name]
        expected_packed_bytes = (3 * dimension + 7) // 8
        packed = _decompress_exact(compressed, expected_packed_bytes)
        symbols = unpack_three_bit_symbols(packed, dimension)
        blocks[block_name] = make_quantized_block(
            scale_bytes,
            symbols,
            expected_dimension=dimension,
        )
        block_rows.append(
            {
                "block_name": block_name,
                "dimension": dimension,
                "scale_bits": SCALE_BITS_PER_BLOCK,
                "scale_float32": float(blocks[block_name].scale_float32),
                "scale_bytes_hex": scale_bytes.hex(),
                "compressed_length_prefix_bits": LENGTH_BITS_PER_BLOCK,
                "compressed_symbol_bytes": compressed_bytes,
                "compressed_symbol_bits": compressed_bytes * 8,
                "packed_symbol_bytes_before_compression": len(packed),
            }
        )
    if offset != len(prefix):
        raise ValueError("conditional message has trailing content")
    return blocks, _summary(candidate, block_rows, payload)


def dequantize_block(block: QuantizedBlock) -> np.ndarray:
    decoded = (
        block.symbols.astype(np.float32)
        * np.float32(block.scale_float32)
    ).astype(np.float32)
    decoded.setflags(write=False)
    return decoded


def inspect_conditional_message(message: bytes) -> dict[str, Any]:
    _, receipt = decode_conditional_message(message)
    return receipt
