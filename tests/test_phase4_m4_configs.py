import json
import shutil

import pytest
import torch

from experiments.phase3_risk_v1.budget_configs import (
    BUDGET_TOTALS,
    m2_allocation,
)
from experiments.phase4_m4_v1.m4_configs import (
    CANDIDATE_SELECTION_BITS,
    CONFIG_DIR,
    MAPPING_ROOTS,
    SHARED_BUDGETS,
    TOTAL_BUDGET,
    load_and_validate_directory,
    load_frozen_config,
    reject_runtime_overrides,
)
from experiments.phase4_m4_v1.run_one_m4 import build_parser
from model.hybrid_subspace_lora import deterministic_mapping


EXPECTED_PRIVATE = {
    1024: {
        "vision": 436,
        "projector": 1745,
        "language": 891,
    },
    2048: {
        "vision": 291,
        "projector": 1163,
        "language": 594,
    },
    3072: {
        "vision": 145,
        "projector": 582,
        "language": 297,
    },
}


def test_nine_frozen_configs_conserve_budget_and_use_authority():
    validation = load_and_validate_directory()
    assert validation["config_count"] == 9
    assert validation["candidate_selection_bits"] == 4
    assert validation["candidate_selection_bits_in_archive"] is False
    for shared in SHARED_BUDGETS:
        private_total = TOTAL_BUDGET - shared
        authority, _ = m2_allocation(private_total)
        assert authority == EXPECTED_PRIVATE[shared]
        for root in MAPPING_ROOTS:
            config, receipt = load_frozen_config(
                f"M4-shared-{shared}-root-{root}"
            )
            assert len(receipt["sha256"]) == 64
            assert sum(config["coordinate_dimensions"].values()) == 4096
            assert config["shared_budget"] == shared
            assert config["vision_private_budget"] == authority["vision"]
            assert (
                config["projector_private_budget"]
                == authority["projector"]
            )
            assert (
                config["language_private_budget"]
                == authority["language"]
            )
            assert config["candidate_selection_bits"] == 4
            assert config["candidate_selection_bits_in_archive"] is False


def test_private_2048_matches_old_low_but_not_old_current():
    low, _ = m2_allocation(BUDGET_TOTALS["low"])
    current, _ = m2_allocation(BUDGET_TOTALS["current"])
    assert EXPECTED_PRIVATE[2048] == low
    assert all(
        allocation != current for allocation in EXPECTED_PRIVATE.values()
    )
    assert EXPECTED_PRIVATE[1024] != low
    assert EXPECTED_PRIVATE[3072] != low


def test_branch_ranks_preserve_every_old_target_rank():
    config, _ = load_frozen_config("M4-shared-1024-root-43101")
    for target in config["target_registry"]["targets"]:
        assert target["old_rank"] in (4, 32)
        assert target["shared_rank"] == target["old_rank"] // 2
        assert target["private_rank"] == target["old_rank"] // 2
        assert (
            target["shared_rank"] + target["private_rank"]
            == target["old_rank"]
        )
        assert target["outer_scale"] == 1.0


def test_same_root_mapping_repeats_and_different_root_changes():
    arguments = dict(
        canonical_target_name="vision.example",
        module_group="vision",
        coordinate_block_id="shared_coordinates",
        factor_id="A",
        element_count=64,
        coordinate_dimension=17,
    )
    first = deterministic_mapping(43101, **arguments)
    repeated = deterministic_mapping(43101, **arguments)
    changed = deterministic_mapping(43102, **arguments)
    assert torch.equal(first[0], repeated[0])
    assert torch.equal(first[1], repeated[1])
    assert not (
        torch.equal(first[0], changed[0])
        and torch.equal(first[1], changed[1])
    )


def test_config_file_modification_and_runtime_overrides_are_rejected(tmp_path):
    copied = tmp_path / "configs"
    shutil.copytree(CONFIG_DIR, copied)
    selected = copied / "M4-shared-1024-root-43101.json"
    payload = json.loads(selected.read_text(encoding="utf-8"))
    payload["shared_budget"] = 1025
    selected.write_text(
        json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_frozen_config(
            "M4-shared-1024-root-43101", config_dir=copied
        )
    with pytest.raises(ValueError, match="forbid"):
        reject_runtime_overrides({"learning_rate": 0.1})
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "--config-id",
                "M4-shared-1024-root-43101",
                "--learning-rate",
                "0.1",
            ]
        )


def test_candidate_selection_bits_are_exactly_four_and_separate():
    assert CANDIDATE_SELECTION_BITS == 4
