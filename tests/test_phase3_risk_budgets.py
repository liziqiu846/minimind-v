import json

import torch

from experiments.phase3_risk_v1.budget_adapter import (
    build_factor_mappings_for_dimensions,
    check_current_mapping_equivalence,
)
from experiments.phase3_risk_v1.budget_codec import (
    check_current_codec_equivalence,
    decode_budget_mms2,
    encode_budget_mms2,
)
from experiments.phase3_risk_v1.budget_configs import (
    BUDGET_TOTALS,
    MAPPING_ROOTS,
    build_config,
    generate_configs,
    load_and_validate_directory,
    m2_allocation,
)
from experiments.phase3_risk_v1.budget_runtime import load_frozen_config
from experiments.stage2_protocol import load_target_registry
from model.global_subspace_lora import target_specs


def test_actual_budget_values_and_largest_remainder_receipt():
    assert m2_allocation(2048)[0] == {
        "vision": 291,
        "projector": 1163,
        "language": 594,
    }
    assert m2_allocation(4096)[0] == {
        "vision": 582,
        "projector": 2327,
        "language": 1187,
    }
    assert m2_allocation(8192)[0] == {
        "vision": 1163,
        "projector": 4654,
        "language": 2375,
    }


def test_generate_18_configs_and_validate_all_pairs(tmp_path):
    config_dir = tmp_path / "configs"
    manifest = generate_configs(config_dir)
    assert manifest["config_count"] == 18
    assert manifest["pair_count"] == 9
    assert manifest["external_selection_bits"] == 5
    assert (
        manifest["comparison_claim"]
        == "equal_coordinate_budget_not_equal_description_length"
    )
    assert load_and_validate_directory(config_dir)["status"] == "passed"


def test_all_budget_mappings_use_every_coordinate():
    registry = load_target_registry()
    specs = target_specs(registry, ("vision", "projector", "language"))
    for budget, total in BUDGET_TOTALS.items():
        for method in ("M2", "M3"):
            config = build_config(method, budget, MAPPING_ROOTS[0])
            _, statistics = build_factor_mappings_for_dimensions(
                method,
                MAPPING_ROOTS[0],
                specs,
                config["coordinate_dimensions"],
            )
            assert sum(
                value["dimension"] for value in statistics.values()
            ) == total
            assert all(value["minimum"] >= 1 for value in statistics.values())


def test_current_mapping_and_codec_are_exactly_equivalent():
    mapping = check_current_mapping_equivalence(load_target_registry())
    codec = check_current_codec_equivalence()
    assert mapping["status"] == "passed"
    assert codec["status"] == "passed"
    assert len(mapping["checks"]) == 6
    assert len(codec["checks"]) == 6


def test_low_and_high_budget_codec_round_trip():
    for budget in ("low", "high"):
        config = build_config("M2", budget, 43101)
        dimensions = config["coordinate_dimensions"]
        coordinates = {
            name: torch.linspace(-0.5, 0.5, dimension)
            for name, dimension in dimensions.items()
        }
        payload, summary = encode_budget_mms2(
            coordinates, "M2", 43101, dimensions
        )
        decoded, identity = decode_budget_mms2(payload, dimensions)
        assert identity["model_group"] == "M2"
        assert summary["archive_bits"] == len(payload) * 8
        assert set(decoded) == set(dimensions)


def test_runtime_loader_verifies_selected_config_and_complete_manifest():
    config, receipt = load_frozen_config("M2-low-seed-43101")
    assert config["config_id"] == "M2-low-seed-43101"
    assert config["candidate_family_size"] == 18
    assert config["external_selection_bits"] == 5
    assert len(receipt["sha256"]) == 64
    assert receipt["directory_validation"]["status"] == "passed"
