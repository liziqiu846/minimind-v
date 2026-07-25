"""Bridge one M4 quantized state to MMS2 v2 and the frozen conditional code."""

from __future__ import annotations

import struct
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
import torch

from experiments.phase4_complexity_v1.conditional_codec import (
    QuantizedBlock,
    decode_conditional_message,
    dequantize_block,
    encode_conditional_message,
    quantize_coordinates,
)
from experiments.phase4_formal_v1 import FORMAL_CANDIDATE_ID
from experiments.phase4_formal_v1.runtime_gate import (
    sha256_bytes,
    verify_zlib_runtime,
)
from experiments.phase4_m4_v1.mms2_v2 import (
    decode_mms2_v2,
    encode_mms2_v2,
)
from experiments.quantize_stage2_adapter import quantize_coordinate


BLOCK_NAME_MAP = OrderedDict(
    (
        ("shared", "shared_coordinates"),
        ("vision_private", "vision_private_coordinates"),
        ("projector_private", "projector_private_coordinates"),
        ("language_private", "language_private_coordinates"),
    )
)


@dataclass(frozen=True)
class CodecVerification:
    archive: bytes
    conditional_message: bytes
    archive_coordinates: Mapping[str, torch.Tensor]
    conditional_coordinates: Mapping[str, torch.Tensor]
    complexity_receipt: Mapping[str, Any]
    verification_receipt: Mapping[str, Any]


def quantized_blocks_from_coordinates(
    coordinates: Mapping[str, torch.Tensor],
) -> dict[str, QuantizedBlock]:
    if set(coordinates) != set(BLOCK_NAME_MAP.values()):
        raise ValueError("formal codec requires exactly four M4 coordinate blocks")
    return {
        short_name: quantize_coordinates(coordinates[long_name])
        for short_name, long_name in BLOCK_NAME_MAP.items()
    }


def coordinates_from_quantized_blocks(
    blocks: Mapping[str, QuantizedBlock],
) -> dict[str, torch.Tensor]:
    if set(blocks) != set(BLOCK_NAME_MAP):
        raise ValueError("conditional state has the wrong M4 block set")
    return {
        long_name: torch.from_numpy(
            np.array(dequantize_block(blocks[short_name]), copy=True)
        )
        for short_name, long_name in BLOCK_NAME_MAP.items()
    }


def _same_quantized_blocks(
    left: Mapping[str, QuantizedBlock],
    right: Mapping[str, QuantizedBlock],
) -> bool:
    return set(left) == set(right) and all(
        left[name].scale_bytes == right[name].scale_bytes
        and np.array_equal(left[name].symbols, right[name].symbols)
        for name in left
    )


def _mms2_rule_equivalence(
    coordinates: Mapping[str, torch.Tensor],
    blocks: Mapping[str, QuantizedBlock],
) -> dict[str, Any]:
    rows = []
    for short_name, long_name in BLOCK_NAME_MAP.items():
        scale, unsigned_symbols = quantize_coordinate(coordinates[long_name])
        expected_scale = struct.pack("<f", float(scale))
        expected_symbols = unsigned_symbols.astype(np.int16) - 3
        scale_equal = expected_scale == blocks[short_name].scale_bytes
        symbols_equal = np.array_equal(
            expected_symbols, blocks[short_name].symbols
        )
        if not scale_equal or not symbols_equal:
            raise RuntimeError(
                f"MMS2 and conditional quantization differ for {short_name}"
            )
        rows.append(
            {
                "block_name": short_name,
                "mms2_coordinate_name": long_name,
                "scale_bytes_exact": scale_equal,
                "symbols_exact": symbols_equal,
            }
        )
    return {
        "status": "passed",
        "all_scale_bytes_exact": True,
        "all_symbols_exact": True,
        "blocks": rows,
    }


def _coordinate_state_equal(
    left: Mapping[str, torch.Tensor],
    right: Mapping[str, torch.Tensor],
) -> bool:
    return set(left) == set(right) and all(
        torch.equal(
            left[name].detach().cpu().float(),
            right[name].detach().cpu().float(),
        )
        for name in left
    )


def verify_codecs_from_coordinates(
    coordinates: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
    *,
    archive: bytes | None = None,
    candidate_id: int = FORMAL_CANDIDATE_ID,
) -> CodecVerification:
    """Use one post-training state for both codecs and prove exact identity."""

    verify_zlib_runtime()
    if candidate_id != FORMAL_CANDIDATE_ID:
        raise ValueError("formal codec integration accepts only candidate ID 9")
    generated_archive, generated_summary = encode_mms2_v2(coordinates, config)
    if archive is None:
        archive = generated_archive
    elif generated_archive != archive:
        raise RuntimeError(
            "stored MMS2 v2 archive differs from the same coordinate state"
        )
    archive_coordinates, archive_metadata = decode_mms2_v2(archive)
    if (
        archive_metadata["config_id"] != config["config_id"]
        or archive_metadata["archive_bits"] != len(archive) * 8
    ):
        raise RuntimeError("MMS2 v2 decoded identity or length differs")

    input_blocks = quantized_blocks_from_coordinates(coordinates)
    quantization_equivalence = _mms2_rule_equivalence(
        coordinates, input_blocks
    )
    message, message_summary = encode_conditional_message(
        candidate_id, input_blocks
    )
    decoded_blocks, decoded_summary = decode_conditional_message(message)
    reencoded, reencoded_summary = encode_conditional_message(
        candidate_id, decoded_blocks
    )
    if (
        reencoded != message
        or decoded_summary != message_summary
        or reencoded_summary != message_summary
        or not _same_quantized_blocks(input_blocks, decoded_blocks)
    ):
        raise RuntimeError("conditional message round trip is not byte/bit exact")

    conditional_coordinates = coordinates_from_quantized_blocks(decoded_blocks)
    if not _coordinate_state_equal(
        archive_coordinates, conditional_coordinates
    ):
        raise RuntimeError(
            "MMS2 and conditional decoders recovered different coordinates"
        )

    block_scale_bits = {
        row["block_name"]: int(row["scale_bits"])
        for row in message_summary["coordinate_blocks"]
    }
    block_symbol_bits = {
        row["block_name"]: int(row["compressed_symbol_bits"])
        for row in message_summary["coordinate_blocks"]
    }
    paid_sum = (
        int(message_summary["candidate_id_bits"])
        + int(message_summary["framing_bits"])
        + sum(block_scale_bits.values())
        + sum(block_symbol_bits.values())
    )
    if (
        paid_sum != int(message_summary["conditional_message_bits"])
        or paid_sum != len(message) * 8
    ):
        raise RuntimeError("formal conditional paid fields do not add exactly")

    complexity = {
        "schema_version": 1,
        "status": "passed",
        "candidate_id": candidate_id,
        "candidate_id_bits": int(message_summary["candidate_id_bits"]),
        "framing_bits": int(message_summary["framing_bits"]),
        "coordinate_blocks": message_summary["coordinate_blocks"],
        "block_scale_bits": block_scale_bits,
        "block_compressed_symbol_bits": block_symbol_bits,
        "total_scale_bits": int(message_summary["total_scale_bits"]),
        "total_compressed_symbol_bits": int(
            message_summary["total_compressed_symbol_bits"]
        ),
        "conditional_message_bits": int(
            message_summary["conditional_message_bits"]
        ),
        "conditional_message_sha256": sha256_bytes(message),
        "paid_field_bits_sum": paid_sum,
        "paid_fields_sum_exact": True,
        "full_archive_bits": len(archive) * 8,
        "full_archive_sha256": sha256_bytes(archive),
        "full_archive_role": "engineering_reference_only",
        "structure_metadata_in_conditional_message": False,
        "formal_complexity_definition": "C_conditional(h | A)",
        "zlib_compile_version": verify_zlib_runtime()["compile_version"],
        "zlib_runtime_version": verify_zlib_runtime()["runtime_version"],
    }
    verification = {
        "schema_version": 1,
        "status": "passed",
        "candidate_id": candidate_id,
        "config_id": config["config_id"],
        "mms2_decode_reencode_byte_exact": generated_archive == archive,
        "conditional_decode_reencode_byte_exact": True,
        "conditional_scale_and_symbols_exact": True,
        "mms2_conditional_quantization_rule_equivalence": (
            quantization_equivalence
        ),
        "mms2_conditional_decoded_coordinates_exact": True,
        "mms2_archive_summary": generated_summary,
        "mms2_archive_decode_summary": archive_metadata,
    }
    return CodecVerification(
        archive=archive,
        conditional_message=message,
        archive_coordinates=archive_coordinates,
        conditional_coordinates=conditional_coordinates,
        complexity_receipt=complexity,
        verification_receipt=verification,
    )
