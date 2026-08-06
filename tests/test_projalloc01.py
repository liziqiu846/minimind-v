from __future__ import annotations

import gc

import torch

from experiments.analyze_projalloc01 import (
    _parse_roots,
    pilot_judgment,
)
from experiments.projalloc01 import (
    CONDITIONS,
    EXPECTED_DIMENSIONS,
    MAPPING_FACTOR_COUNT,
    PILOT_ROOT,
    TOTAL_COORDINATES,
    build_model,
    dimensions_for,
    projection_preflight,
)
from experiments.stage2_protocol import Stage2Protocol
from model.global_subspace_lora import coordinate_parameters, coordinate_state
from trainer.train_stage2 import frozen_parameter_hash


def test_frozen_allocations_are_the_only_equal_total_conditions():
    assert CONDITIONS == ("current-allocation", "projector-dominant")
    assert dimensions_for("current-allocation") == {
        "vision": 582,
        "projector": 2327,
        "language": 1187,
    }
    assert dimensions_for("projector-dominant") == {
        "vision": 1,
        "projector": 4094,
        "language": 1,
    }
    assert all(
        sum(dimensions_for(condition).values()) == TOTAL_COORDINATES
        for condition in CONDITIONS
    )


def test_pilot_root_projection_is_reproducible_and_uses_every_coordinate():
    for condition in CONDITIONS:
        receipt = projection_preflight(condition, PILOT_ROOT)
        assert receipt["mapping_factor_count"] == MAPPING_FACTOR_COUNT
        assert receipt["all_roots_reproducible"] is True
        assert receipt["all_coordinates_used"] is True
        usage = receipt["roots"][str(PILOT_ROOT)]["module_usage"]
        assert all(row["unused_coordinate_count"] == 0 for row in usage.values())


def test_arbitrary_allocation_model_has_only_4096_zero_coordinates():
    protocol = Stage2Protocol.load(
        "experiments/stage2_protocol_v2.json", require_frozen=True
    )
    frozen_hashes = []
    for condition in CONDITIONS:
        model = build_model(
            protocol,
            PILOT_ROOT,
            dimensions_for(condition),
            device="cpu",
        )
        dimensions = {
            name: parameter.numel()
            for name, parameter in coordinate_parameters(model)
        }
        assert dimensions == EXPECTED_DIMENSIONS[condition]
        assert sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        ) == TOTAL_COORDINATES
        assert all(
            torch.count_nonzero(value).item() == 0
            for value in coordinate_state(model).values()
        )
        assert model.stage2_adapter["mapping_factor_count"] == 22
        assert model.stage2_adapter["mapping_root"] == PILOT_ROOT
        frozen_hashes.append(frozen_parameter_hash(model))
        del model
        gc.collect()
    assert len(set(frozen_hashes)) == 1


def _summary(
    *,
    rotation_difference: float = 0.05,
    rotation_ci_lower: float = 0.001,
    projector_accuracy: float = 0.30,
    cv_difference: float = 0.01,
    cv_margin_difference: float = 0.001,
):
    return {
        "training_pair_checks": {"all": True},
        "panels": {
            "rotation": {
                "accuracy_difference": rotation_difference,
                "accuracy_difference_bootstrap": {
                    "ci95": [rotation_ci_lower, 0.10]
                },
                "projector_accuracy": projector_accuracy,
            },
            "cvbench": {
                "accuracy_difference": cv_difference,
                "margin_difference_bits_per_token": cv_margin_difference,
            },
        },
    }


def test_pilot_judgment_uses_all_preregistered_gates():
    assert pilot_judgment(_summary())["decision"] == "PILOT_POSITIVE"
    failures = (
        {"rotation_difference": 0.049},
        {"rotation_ci_lower": 0.0},
        {"projector_accuracy": 0.299},
        {"cv_difference": 0.009},
        {"cv_margin_difference": 0.0},
    )
    for override in failures:
        result = pilot_judgment(_summary(**override))
        assert result["decision"] == "REJECT_IDEA"
        assert result["seed_escalation_authorized"] is False


def test_root_parser_forbids_partial_or_old_root_sets(tmp_path):
    assert _parse_roots([f"43201:{tmp_path}"]) == {
        43201: tmp_path.resolve()
    }
    for values in (
        [f"43101:{tmp_path}"],
        [f"43202:{tmp_path}"],
        [f"43201:{tmp_path}", f"43202:{tmp_path}"],
    ):
        try:
            _parse_roots(values)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid root set was accepted")
