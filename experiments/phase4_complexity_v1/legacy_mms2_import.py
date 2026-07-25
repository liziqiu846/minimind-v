"""Read-only import of exact quantized state from frozen current MMS2 v1."""

from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path
from typing import Any, Dict

import numpy as np

from experiments.phase4_complexity_v1.candidate_registry import candidate_by_id
from experiments.phase4_complexity_v1.conditional_codec import (
    QuantizedBlock,
    dequantize_block,
    make_quantized_block,
)


MMS2_V1_HEADER = struct.Struct("<4sBBBBBII")
MMS2_MAGIC = b"MMS2"
MMS2_V1_VERSION = 1
QUANTIZATION_BITS_LABEL = 3
METHOD_IDS = {"M2": 2, "M3": 3}
ROOT_IDS = {43101: 1, 43102: 2, 43103: 3}


def _decompress_body(compressed: bytes, expected_length: int) -> bytes:
    decompressor = zlib.decompressobj()
    try:
        body = decompressor.decompress(compressed, expected_length + 1)
        body += decompressor.flush()
    except zlib.error as error:
        raise ValueError("legacy MMS2 v1 zlib body is invalid") from error
    if (
        not decompressor.eof
        or decompressor.unused_data
        or decompressor.unconsumed_tail
        or len(body) != expected_length
    ):
        raise ValueError("legacy MMS2 v1 body length is invalid")
    return body


def import_legacy_mms2_v1(
    archive: bytes,
    candidate_id: int,
    *,
    cross_check_frozen_decoder: bool = True,
) -> tuple[Dict[str, QuantizedBlock], dict[str, Any]]:
    """Extract exact scale bytes and symbols without requantizing floats."""

    candidate = candidate_by_id(candidate_id)
    if candidate.method not in ("M2", "M3"):
        raise ValueError("legacy MMS2 v1 import accepts only M2/M3 candidates")
    payload = bytes(archive)
    if len(payload) < MMS2_V1_HEADER.size:
        raise ValueError("legacy MMS2 v1 archive is shorter than its header")
    (
        magic,
        version,
        method_id,
        root_id,
        group_count,
        bits_label,
        body_length,
        compressed_length,
    ) = MMS2_V1_HEADER.unpack_from(payload)
    if (
        magic != MMS2_MAGIC
        or version != MMS2_V1_VERSION
        or method_id != METHOD_IDS[candidate.method]
        or root_id != ROOT_IDS[candidate.mapping_root]
        or group_count != len(candidate.block_order)
        or bits_label != QUANTIZATION_BITS_LABEL
        or len(payload) != MMS2_V1_HEADER.size + compressed_length
    ):
        raise ValueError("legacy MMS2 v1 identity differs from candidate")
    body = _decompress_body(payload[MMS2_V1_HEADER.size :], body_length)
    offset = 0
    blocks: Dict[str, QuantizedBlock] = {}
    groups = []
    for block_name in candidate.block_order:
        dimension = candidate.block_dimensions[block_name]
        if offset + 8 + dimension > len(body):
            raise ValueError("legacy MMS2 v1 coordinate group is truncated")
        stored_dimension = struct.unpack_from("<I", body, offset)[0]
        scale_bytes = body[offset + 4 : offset + 8]
        offset += 8
        if stored_dimension != dimension:
            raise ValueError("legacy MMS2 v1 dimension differs from candidate")
        unsigned = np.frombuffer(
            body, dtype=np.uint8, count=dimension, offset=offset
        ).copy()
        offset += dimension
        if np.any(unsigned > 6):
            raise ValueError("legacy MMS2 v1 contains an invalid seven-level code")
        signed = unsigned.astype(np.int16) - 3
        blocks[block_name] = make_quantized_block(
            scale_bytes,
            signed,
            expected_dimension=dimension,
        )
        groups.append(
            {
                "block_name": block_name,
                "dimension": dimension,
                "scale_bytes_hex": scale_bytes.hex(),
                "scale_float32": float(blocks[block_name].scale_float32),
            }
        )
    if offset != len(body):
        raise ValueError("legacy MMS2 v1 body has trailing bytes")

    frozen_decoder_exact = False
    if cross_check_frozen_decoder:
        from experiments.quantize_stage2_adapter import decode_mms2

        decoded, metadata = decode_mms2(payload)
        if (
            metadata.get("model_group") != candidate.method
            or metadata.get("mapping_root") != candidate.mapping_root
            or tuple(decoded) != candidate.block_order
        ):
            raise RuntimeError("frozen MMS2 decoder identity cross-check failed")
        for block_name in candidate.block_order:
            observed = (
                decoded[block_name]
                .detach()
                .cpu()
                .to(dtype=decoded[block_name].dtype)
                .numpy()
                .astype(np.float32, copy=False)
            )
            expected = dequantize_block(blocks[block_name])
            if not np.array_equal(observed, expected):
                raise RuntimeError(
                    "frozen MMS2 decoder coordinate cross-check failed"
                )
        frozen_decoder_exact = True
    return blocks, {
        "schema": "phase4-legacy-mms2-import-v1",
        "candidate_id": candidate.candidate_id,
        "candidate_name": candidate.candidate_name,
        "method": candidate.method,
        "mapping_root": candidate.mapping_root,
        "archive_bytes": len(payload),
        "archive_bits": len(payload) * 8,
        "archive_sha256": hashlib.sha256(payload).hexdigest(),
        "coordinate_groups": groups,
        "exact_scale_bytes_and_symbols_extracted": True,
        "frozen_decoder_coordinate_cross_check": frozen_decoder_exact,
        "legacy_archive_modified": False,
    }


def import_legacy_mms2_v1_file(
    path: Path,
    candidate_id: int,
) -> tuple[Dict[str, QuantizedBlock], dict[str, Any]]:
    before = path.stat()
    payload = path.read_bytes()
    blocks, receipt = import_legacy_mms2_v1(payload, candidate_id)
    after = path.stat()
    if (
        before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
        or hashlib.sha256(path.read_bytes()).hexdigest()
        != receipt["archive_sha256"]
    ):
        raise RuntimeError("legacy MMS2 source changed during read-only import")
    return blocks, {
        **receipt,
        "source_path": str(path.resolve()),
        "source_size_unchanged": True,
        "source_mtime_unchanged": True,
        "source_sha256_unchanged": True,
    }

