import inspect
import struct

import pytest
import torch

from experiments.phase4_m4_v1.complexity_audit import (
    COMPONENT_FIELDS,
    audit_archive,
)
from experiments.phase4_m4_v1.m4_configs import load_frozen_config
from experiments.phase4_m4_v1.mms2_v2 import (
    DIRECTORY_ENTRY,
    HEADER,
    SECTION_IDS,
    decode_mms2_v2,
    encode_mms2_v2,
    inspect_mms2_v2_directory,
)


@pytest.fixture(scope="module")
def encoded_archive():
    config, _ = load_frozen_config("M4-shared-2048-root-43102")
    coordinates = {
        name: torch.linspace(
            -1.0 - index * 0.1,
            1.0 + index * 0.1,
            dimension,
        )
        for index, (name, dimension) in enumerate(
            config["coordinate_dimensions"].items()
        )
    }
    archive, summary = encode_mms2_v2(coordinates, config)
    return config, coordinates, archive, summary


def test_shared_section_occurs_once_and_five_bits_sum(encoded_archive):
    _, _, archive, summary = encoded_archive
    directory = inspect_mms2_v2_directory(archive)
    assert [row["section_name"] for row in directory] == list(SECTION_IDS)
    assert (
        [row["section_name"] for row in directory].count(
            "shared_coordinates"
        )
        == 1
    )
    assert sum(summary[name] for name in COMPONENT_FIELDS) == len(archive) * 8
    assert summary["archive_bits"] == len(archive) * 8
    assert summary["candidate_selection_bits"] == 4
    assert summary["candidate_selection_bits_in_archive"] is False
    receipt = audit_archive(archive)
    assert receipt["component_bits_equal_archive_bits"] is True
    assert receipt["candidate_selection_bits_added_to_bound"] is False


def test_decoder_is_self_describing_and_accepts_only_archive_bytes(
    encoded_archive,
):
    config, _, archive, _ = encoded_archive
    signature = inspect.signature(decode_mms2_v2)
    assert list(signature.parameters) == ["payload"]
    decoded, metadata = decode_mms2_v2(archive)
    assert metadata["config_id"] == config["config_id"]
    assert metadata["config"]["coordinate_dimensions"] == config[
        "coordinate_dimensions"
    ]
    assert metadata["config"]["target_registry"]["targets"] == config[
        "target_registry"
    ]["targets"]
    assert {
        name: value.numel() for name, value in decoded.items()
    } == config["coordinate_dimensions"]
    structure = metadata["structure"]["normalized_configuration"]
    assert structure["mapping_root"] == config["mapping_root"]
    assert structure["mapping"]["summary"] == config["mapping_summary"]
    assert structure["base_assets"] == config["base_assets"]
    assert structure["quantization"] == config["quantization"]


def _mutate_directory(
    archive: bytes, entry_index: int, field_offset: int, fmt: str, value: int
) -> bytes:
    output = bytearray(archive)
    start = HEADER.size + entry_index * DIRECTORY_ENTRY.size + field_offset
    struct.pack_into(fmt, output, start, value)
    return bytes(output)


def test_corrupted_section_is_rejected(encoded_archive):
    _, _, archive, _ = encoded_archive
    corrupted = bytearray(archive)
    corrupted[-1] ^= 0x40
    with pytest.raises(ValueError):
        decode_mms2_v2(bytes(corrupted))


def test_duplicate_section_is_rejected(encoded_archive):
    _, _, archive, _ = encoded_archive
    duplicate = _mutate_directory(archive, 1, 0, "<B", 1)
    with pytest.raises(ValueError, match="duplicated|missing|reordered"):
        decode_mms2_v2(duplicate)


def test_missing_section_is_rejected(encoded_archive):
    _, _, archive, _ = encoded_archive
    output = bytearray(archive)
    # section_count starts after magic/version/flags.
    struct.pack_into("<H", output, 6, 4)
    with pytest.raises(ValueError, match="section count"):
        decode_mms2_v2(bytes(output))


def test_out_of_bounds_section_is_rejected(encoded_archive):
    _, _, archive, _ = encoded_archive
    # Four one-byte fields precede the uint64 offset.
    invalid = _mutate_directory(
        archive, 2, 4, "<Q", len(archive) + 100
    )
    with pytest.raises(ValueError, match="out of bounds|overlapping"):
        decode_mms2_v2(invalid)
