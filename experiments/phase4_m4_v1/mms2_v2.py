"""Self-describing, independently sectioned MMS2 v2 codec for M4."""

from __future__ import annotations

import base64
import hashlib
import json
import math
import struct
import zlib
from collections import OrderedDict
from typing import Any, Mapping

import numpy as np
import torch

from experiments.phase4_m4_v1.m4_configs import (
    CANDIDATE_SELECTION_BITS,
    TOTAL_BUDGET,
    canonical_json_bytes,
    validate_config,
)
from experiments.quantize_stage2_adapter import (
    decode_mms2 as decode_mms2_v1,
    quantize_coordinate,
)
from model.hybrid_subspace_lora import (
    A0_DOMAIN,
    COORDINATE_BLOCKS,
    MAPPING_DOMAIN,
    MAPPING_ROOTS,
)


MAGIC = b"MMS2"
FORMAT_VERSION = 2
FLAGS = 0
COMPRESSION_ALGORITHM_ID = 1
COMPRESSION_ALGORITHM = "zlib"
COMPRESSION_VERSION = 1
COMPRESSION_LEVEL = 9
DECODER_SCHEMA = "phase4-m4-mms2-v2-decoder-v1"
STRUCTURE_SCHEMA = "phase4-m4-structure-metadata-v1"
HEADER = struct.Struct("<4sBBHQQ")
DIRECTORY_ENTRY = struct.Struct("<BBBBQQQ32s")
SECTION_IDS = OrderedDict(
    (
        ("structure_metadata", 1),
        ("shared_coordinates", 2),
        ("vision_private_coordinates", 3),
        ("projector_private_coordinates", 4),
        ("language_private_coordinates", 5),
    )
)
SECTION_NAMES = {value: key for key, value in SECTION_IDS.items()}
SECTION_COUNT = len(SECTION_IDS)
MAX_SECTION_BYTES = 64 * 1024 * 1024


def _normalized_structure(config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "config_id": config["config_id"],
        "budgets": {
            "total": config["total_coordinate_budget"],
            "shared": config["shared_budget"],
            "vision_private": config["vision_private_budget"],
            "projector_private": config["projector_private_budget"],
            "language_private": config["language_private_budget"],
        },
        "mapping_root": config["mapping_root"],
        "targets": config["target_registry"]["targets"],
        "mapping": {
            "mapping_domain": config["mapping"]["mapping_domain"],
            "a0_domain": config["mapping"]["a0_domain"],
            "mapping_message_fields": config["mapping"][
                "mapping_message_fields"
            ],
            "a0_message_fields": config["mapping"]["a0_message_fields"],
            "summary": config["mapping_summary"],
        },
        "quantization": config["quantization"],
        "base_assets": config["base_assets"],
        "section_schema": {
            "order": list(SECTION_IDS),
            "ids": dict(SECTION_IDS),
            "compression_algorithm": COMPRESSION_ALGORITHM,
            "compression_algorithm_id": COMPRESSION_ALGORITHM_ID,
            "compression_version": COMPRESSION_VERSION,
            "compression_level": COMPRESSION_LEVEL,
            "directory_sha256_scope": "uncompressed_section_bytes",
        },
        "decoder": {
            "schema": DECODER_SCHEMA,
            "format": "MMS2",
            "format_version": FORMAT_VERSION,
        },
    }


def build_structure_metadata(config: Mapping[str, Any]) -> bytes:
    """Embed canonical config bytes plus a directly readable normalized view."""

    validate_config(config)
    config_bytes = canonical_json_bytes(config)
    payload = {
        "schema": STRUCTURE_SCHEMA,
        "canonical_config_json_encoding": "base64_of_canonical_utf8_json",
        "canonical_config_json_base64": base64.b64encode(
            config_bytes
        ).decode("ascii"),
        "canonical_config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "normalized_configuration": _normalized_structure(config),
    }
    return canonical_json_bytes(payload)


def _validate_embedded_config(config: Mapping[str, Any]) -> None:
    """Validate the embedded schema without consulting external files."""

    if (
        config.get("schema_version") != 1
        or config.get("method") != "M4"
        or not isinstance(config.get("config_id"), str)
        or int(config.get("total_coordinate_budget", -1)) != TOTAL_BUDGET
        or int(config.get("mapping_root", -1)) not in MAPPING_ROOTS
        or config.get("runtime_overrides") != "forbidden"
    ):
        raise ValueError("embedded M4 config identity is invalid")
    dimensions = config.get("coordinate_dimensions")
    if (
        not isinstance(dimensions, Mapping)
        or set(dimensions) != set(COORDINATE_BLOCKS)
        or any(
            isinstance(value, bool) or int(value) <= 0
            for value in dimensions.values()
        )
        or sum(int(value) for value in dimensions.values()) != TOTAL_BUDGET
        or list(config.get("coordinate_block_order", ()))
        != list(COORDINATE_BLOCKS)
    ):
        raise ValueError("embedded M4 coordinate budgets are invalid")
    budget_fields = {
        "shared_coordinates": "shared_budget",
        "vision_private_coordinates": "vision_private_budget",
        "projector_private_coordinates": "projector_private_budget",
        "language_private_coordinates": "language_private_budget",
    }
    if any(
        int(dimensions[block_id]) != int(config.get(field, -1))
        for block_id, field in budget_fields.items()
    ):
        raise ValueError("embedded M4 named budgets disagree")
    private_total = sum(
        int(dimensions[name]) for name in COORDINATE_BLOCKS[1:]
    )
    if private_total != int(config.get("private_total_budget", -1)):
        raise ValueError("embedded M4 private total disagrees")

    mapping = config.get("mapping")
    if (
        not isinstance(mapping, Mapping)
        or mapping.get("mapping_domain") != MAPPING_DOMAIN
        or mapping.get("a0_domain") != A0_DOMAIN
        or set(config.get("mapping_summary", {}))
        != set(COORDINATE_BLOCKS)
    ):
        raise ValueError("embedded M4 mapping schema is invalid")
    for block_id in COORDINATE_BLOCKS:
        row = config["mapping_summary"][block_id]
        if (
            int(row.get("dimension", -1)) != int(dimensions[block_id])
            or not isinstance(row.get("mapping_sha256"), str)
            or len(row["mapping_sha256"]) != 64
        ):
            raise ValueError("embedded M4 mapping summary is invalid")

    targets = config.get("target_registry", {}).get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("embedded M4 target list is absent")
    names = []
    for target in targets:
        old_rank = int(target.get("old_rank", -1))
        shared_rank = int(target.get("shared_rank", -1))
        private_rank = int(target.get("private_rank", -1))
        if (
            target.get("module_group")
            not in ("vision", "projector", "language")
            or old_rank not in (4, 32)
            or shared_rank + private_rank != old_rank
            or shared_rank != private_rank
            or float(target.get("outer_scale", math.nan)) != 1.0
            or int(target.get("in_features", 0)) <= 0
            or int(target.get("out_features", 0)) <= 0
        ):
            raise ValueError("embedded M4 target rank/scale is invalid")
        names.append(str(target.get("canonical_name", "")))
    if (
        names != sorted(names, key=lambda value: value.encode("utf-8"))
        or len(names) != len(set(names))
        or any(not name for name in names)
    ):
        raise ValueError("embedded M4 target order is invalid")

    quantization = config.get("quantization")
    if (
        not isinstance(quantization, Mapping)
        or quantization.get("levels") != list(range(-3, 4))
        or quantization.get("quantization_bits_label") != 3
        or quantization.get("decoded_dtype") != "float32"
    ):
        raise ValueError("embedded M4 quantization rule is invalid")
    if (
        int(config.get("candidate_selection_bits", -1))
        != CANDIDATE_SELECTION_BITS
        or config.get("candidate_selection_bits_in_archive") is not False
    ):
        raise ValueError("embedded candidate-selection accounting is invalid")


def parse_structure_metadata(
    payload: bytes,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        structure = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("MMS2 v2 structure section is not valid JSON") from error
    if canonical_json_bytes(structure) != payload:
        raise ValueError("MMS2 v2 structure section is not canonical JSON")
    if (
        structure.get("schema") != STRUCTURE_SCHEMA
        or structure.get("canonical_config_json_encoding")
        != "base64_of_canonical_utf8_json"
    ):
        raise ValueError("MMS2 v2 structure schema is unsupported")
    try:
        config_bytes = base64.b64decode(
            structure["canonical_config_json_base64"],
            validate=True,
        )
    except Exception as error:
        raise ValueError("embedded canonical config bytes are invalid") from error
    if (
        hashlib.sha256(config_bytes).hexdigest()
        != structure.get("canonical_config_sha256")
    ):
        raise ValueError("embedded canonical config SHA-256 mismatch")
    try:
        config = json.loads(config_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("embedded canonical config is invalid JSON") from error
    if canonical_json_bytes(config) != config_bytes:
        raise ValueError("embedded config bytes are not canonical")
    _validate_embedded_config(config)
    if structure.get("normalized_configuration") != _normalized_structure(
        config
    ):
        raise ValueError("normalized structure differs from embedded config")
    return config, structure


def _coordinate_section(
    value: torch.Tensor, expected_dimension: int
) -> tuple[bytes, dict[str, Any]]:
    if value.ndim != 1 or value.numel() != expected_dimension:
        raise ValueError("M4 coordinate tensor dimension differs from config")
    scale, symbols = quantize_coordinate(value)
    raw = (
        struct.pack("<If", expected_dimension, float(scale))
        + symbols.tobytes()
    )
    return raw, {
        "dimension": expected_dimension,
        "scale_float32": float(scale),
        "symbol_histogram": {
            str(level): int(np.count_nonzero(symbols == level + 3))
            for level in range(-3, 4)
        },
    }


def _decode_coordinate_section(
    raw: bytes, expected_dimension: int
) -> tuple[torch.Tensor, dict[str, Any]]:
    if len(raw) < 8:
        raise ValueError("MMS2 v2 coordinate section is truncated")
    dimension, scale = struct.unpack_from("<If", raw)
    if dimension != expected_dimension or len(raw) != 8 + dimension:
        raise ValueError("MMS2 v2 coordinate section dimension is invalid")
    symbols = np.frombuffer(
        raw, dtype=np.uint8, count=dimension, offset=8
    ).copy()
    if np.any(symbols > 6) or not np.isfinite(scale) or scale < 0:
        raise ValueError("MMS2 v2 coordinate scale or symbol is invalid")
    quantized = symbols.astype(np.int16) - 3
    decoded = (
        quantized.astype(np.float32) * np.float32(scale)
    ).astype(np.float32)
    return torch.from_numpy(decoded.copy()), {
        "dimension": dimension,
        "scale_float32": float(scale),
    }


def quantize_coordinate_blocks(
    coordinates: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
) -> dict[str, torch.Tensor]:
    """Return the exact in-memory quantized values used by the archive."""

    validate_config(config)
    if set(coordinates) != set(COORDINATE_BLOCKS):
        raise ValueError("M4 quantization requires exactly four coordinate blocks")
    output: dict[str, torch.Tensor] = {}
    for block_id in COORDINATE_BLOCKS:
        raw, _ = _coordinate_section(
            coordinates[block_id],
            int(config["coordinate_dimensions"][block_id]),
        )
        output[block_id], _ = _decode_coordinate_section(
            raw, int(config["coordinate_dimensions"][block_id])
        )
    return output


def encode_mms2_v2(
    coordinates: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    """Encode one frozen config into exactly five independent sections."""

    validate_config(config)
    if set(coordinates) != set(COORDINATE_BLOCKS):
        raise ValueError("MMS2 v2 requires exactly four coordinate blocks")

    raw_sections: OrderedDict[str, bytes] = OrderedDict()
    raw_sections["structure_metadata"] = build_structure_metadata(config)
    coordinate_receipts = {}
    for block_id in COORDINATE_BLOCKS:
        raw, receipt = _coordinate_section(
            coordinates[block_id],
            int(config["coordinate_dimensions"][block_id]),
        )
        raw_sections[block_id] = raw
        coordinate_receipts[block_id] = receipt

    compressed_sections = OrderedDict(
        (
            name,
            zlib.compress(raw, level=COMPRESSION_LEVEL),
        )
        for name, raw in raw_sections.items()
    )
    directory_bytes = SECTION_COUNT * DIRECTORY_ENTRY.size
    first_offset = HEADER.size + directory_bytes
    offset = first_offset
    directory_parts = []
    directory_rows = []
    for name, section_id in SECTION_IDS.items():
        raw = raw_sections[name]
        compressed = compressed_sections[name]
        digest = hashlib.sha256(raw).digest()
        directory_parts.append(
            DIRECTORY_ENTRY.pack(
                section_id,
                COMPRESSION_ALGORITHM_ID,
                COMPRESSION_VERSION,
                0,
                offset,
                len(compressed),
                len(raw),
                digest,
            )
        )
        directory_rows.append(
            {
                "section_id": section_id,
                "section_name": name,
                "offset": offset,
                "compressed_bytes": len(compressed),
                "uncompressed_bytes": len(raw),
                "sha256": digest.hex(),
                "sha256_scope": "uncompressed_section_bytes",
                "compression_algorithm": COMPRESSION_ALGORITHM,
                "compression_algorithm_id": COMPRESSION_ALGORITHM_ID,
                "compression_version": COMPRESSION_VERSION,
                "compression_level": COMPRESSION_LEVEL,
            }
        )
        offset += len(compressed)
    archive_bytes = offset
    header = HEADER.pack(
        MAGIC,
        FORMAT_VERSION,
        FLAGS,
        SECTION_COUNT,
        directory_bytes,
        archive_bytes,
    )
    archive = (
        header
        + b"".join(directory_parts)
        + b"".join(compressed_sections.values())
    )
    if len(archive) != archive_bytes:
        raise AssertionError("MMS2 v2 archive length construction failed")

    payload_bits = {
        name: len(compressed_sections[name]) * 8
        for name in raw_sections
    }
    structure_bits = (
        HEADER.size
        + directory_bytes
        + len(compressed_sections["structure_metadata"])
    ) * 8
    summary = {
        "format": "MMS2",
        "format_version": FORMAT_VERSION,
        "decoder_schema": DECODER_SCHEMA,
        "config_id": config["config_id"],
        "mapping_root": config["mapping_root"],
        "archive_bytes": len(archive),
        "archive_bits": len(archive) * 8,
        "structure_metadata_bits": structure_bits,
        "shared_coordinate_bits": payload_bits["shared_coordinates"],
        "vision_private_coordinate_bits": payload_bits[
            "vision_private_coordinates"
        ],
        "projector_private_coordinate_bits": payload_bits[
            "projector_private_coordinates"
        ],
        "language_private_coordinate_bits": payload_bits[
            "language_private_coordinates"
        ],
        "candidate_selection_bits": CANDIDATE_SELECTION_BITS,
        "candidate_selection_bits_in_archive": False,
        "directory": directory_rows,
        "coordinate_groups": coordinate_receipts,
        "section_count": SECTION_COUNT,
        "shared_section_occurrences": 1,
    }
    _validate_complexity_identity(summary)
    return archive, summary


def _parse_directory(
    payload: bytes,
) -> tuple[list[dict[str, Any]], int]:
    if len(payload) < HEADER.size:
        raise ValueError("MMS2 archive is shorter than its v2 header")
    (
        magic,
        version,
        flags,
        section_count,
        directory_bytes,
        archive_bytes,
    ) = HEADER.unpack_from(payload)
    if magic != MAGIC or version != FORMAT_VERSION or flags != FLAGS:
        raise ValueError("unsupported MMS2 v2 header")
    if section_count != SECTION_COUNT:
        raise ValueError("MMS2 v2 section count is missing or excessive")
    expected_directory_bytes = SECTION_COUNT * DIRECTORY_ENTRY.size
    if directory_bytes != expected_directory_bytes:
        raise ValueError("MMS2 v2 directory byte count is invalid")
    if archive_bytes != len(payload):
        raise ValueError("MMS2 v2 complete archive length is invalid")
    directory_end = HEADER.size + directory_bytes
    if directory_end > len(payload):
        raise ValueError("MMS2 v2 directory is truncated")

    rows = []
    for index in range(SECTION_COUNT):
        start = HEADER.size + index * DIRECTORY_ENTRY.size
        (
            section_id,
            algorithm_id,
            compression_version,
            entry_flags,
            offset,
            compressed_bytes,
            uncompressed_bytes,
            digest,
        ) = DIRECTORY_ENTRY.unpack_from(payload, start)
        rows.append(
            {
                "section_id": section_id,
                "algorithm_id": algorithm_id,
                "compression_version": compression_version,
                "flags": entry_flags,
                "offset": offset,
                "compressed_bytes": compressed_bytes,
                "uncompressed_bytes": uncompressed_bytes,
                "sha256": digest.hex(),
            }
        )
    ids = [row["section_id"] for row in rows]
    if ids != list(SECTION_IDS.values()) or len(ids) != len(set(ids)):
        raise ValueError("MMS2 v2 sections are duplicated, missing, or reordered")

    expected_offset = directory_end
    for row in rows:
        if (
            row["algorithm_id"] != COMPRESSION_ALGORITHM_ID
            or row["compression_version"] != COMPRESSION_VERSION
            or row["flags"] != 0
            or row["compressed_bytes"] <= 0
            or row["uncompressed_bytes"] <= 0
            or row["uncompressed_bytes"] > MAX_SECTION_BYTES
            or row["offset"] != expected_offset
        ):
            raise ValueError(
                "MMS2 v2 section is unsupported, empty, overlapping, or out of bounds"
            )
        end = row["offset"] + row["compressed_bytes"]
        if end > len(payload):
            raise ValueError("MMS2 v2 section extends beyond the archive")
        expected_offset = end
    if expected_offset != len(payload):
        raise ValueError("MMS2 v2 archive has a hole or trailing bytes")
    return rows, directory_end


def inspect_mms2_v2_directory(payload: bytes) -> list[dict[str, Any]]:
    rows, _ = _parse_directory(payload)
    return [
        {
            **row,
            "section_name": SECTION_NAMES[row["section_id"]],
            "compression_algorithm": COMPRESSION_ALGORITHM,
        }
        for row in rows
    ]


def _decompress_section(payload: bytes, row: Mapping[str, Any]) -> bytes:
    start = int(row["offset"])
    end = start + int(row["compressed_bytes"])
    compressed = payload[start:end]
    expected = int(row["uncompressed_bytes"])
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(compressed, expected + 1)
        raw += decompressor.flush()
    except zlib.error as error:
        raise ValueError("MMS2 v2 section zlib stream is invalid") from error
    if (
        not decompressor.eof
        or decompressor.unused_data
        or decompressor.unconsumed_tail
        or len(raw) != expected
    ):
        raise ValueError("MMS2 v2 section decompressed length is invalid")
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError("MMS2 v2 section SHA-256 mismatch")
    return raw


def decode_mms2_v2(
    payload: bytes,
) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    """Decode using archive bytes alone; no dimensions or target list argument."""

    rows, _ = _parse_directory(payload)
    raw_sections = {
        SECTION_NAMES[row["section_id"]]: _decompress_section(payload, row)
        for row in rows
    }
    config, structure = parse_structure_metadata(
        raw_sections["structure_metadata"]
    )
    coordinates: dict[str, torch.Tensor] = {}
    coordinate_receipts = {}
    for block_id in COORDINATE_BLOCKS:
        coordinates[block_id], coordinate_receipts[block_id] = (
            _decode_coordinate_section(
                raw_sections[block_id],
                int(config["coordinate_dimensions"][block_id]),
            )
        )

    compressed_by_name = {
        SECTION_NAMES[row["section_id"]]: int(row["compressed_bytes"])
        for row in rows
    }
    structure_bits = (
        HEADER.size
        + SECTION_COUNT * DIRECTORY_ENTRY.size
        + compressed_by_name["structure_metadata"]
    ) * 8
    metadata = {
        "format": "MMS2",
        "format_version": FORMAT_VERSION,
        "decoder_schema": DECODER_SCHEMA,
        "config_id": config["config_id"],
        "mapping_root": config["mapping_root"],
        "config": config,
        "structure": structure,
        "coordinate_groups": coordinate_receipts,
        "archive_bytes": len(payload),
        "archive_bits": len(payload) * 8,
        "structure_metadata_bits": structure_bits,
        "shared_coordinate_bits": compressed_by_name[
            "shared_coordinates"
        ]
        * 8,
        "vision_private_coordinate_bits": compressed_by_name[
            "vision_private_coordinates"
        ]
        * 8,
        "projector_private_coordinate_bits": compressed_by_name[
            "projector_private_coordinates"
        ]
        * 8,
        "language_private_coordinate_bits": compressed_by_name[
            "language_private_coordinates"
        ]
        * 8,
        "candidate_selection_bits": CANDIDATE_SELECTION_BITS,
        "candidate_selection_bits_in_archive": False,
        "directory": inspect_mms2_v2_directory(payload),
        "section_count": SECTION_COUNT,
        "shared_section_occurrences": 1,
    }
    _validate_complexity_identity(metadata)
    return coordinates, metadata


def _validate_complexity_identity(summary: Mapping[str, Any]) -> None:
    component_sum = sum(
        int(summary[name])
        for name in (
            "structure_metadata_bits",
            "shared_coordinate_bits",
            "vision_private_coordinate_bits",
            "projector_private_coordinate_bits",
            "language_private_coordinate_bits",
        )
    )
    if component_sum != int(summary["archive_bits"]):
        raise AssertionError(
            "MMS2 v2 section complexity fields do not sum to archive_bits"
        )
    if summary.get("candidate_selection_bits_in_archive") is not False:
        raise AssertionError("candidate-selection bits entered the archive")


def decode_mms2_any(
    payload: bytes,
) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    """Dispatch v1 byte-exact compatibility or the self-describing v2 decoder."""

    if len(payload) < 5 or payload[:4] != MAGIC:
        raise ValueError("payload is not an MMS2 archive")
    if payload[4] == 1:
        coordinates, metadata = decode_mms2_v1(payload)
        return coordinates, {
            **metadata,
            "format": "MMS2",
            "format_version": 1,
            "legacy_byte_exact_decoder": True,
        }
    if payload[4] == FORMAT_VERSION:
        return decode_mms2_v2(payload)
    raise ValueError("unsupported MMS2 archive version")
