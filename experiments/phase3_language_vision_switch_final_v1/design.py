"""Frozen minimal design for the final Language/Vision switch decision."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping
from typing import Any

from . import (
    ACTION_MODULES,
    COORDINATE_MODULES,
    PROTOCOL_ID,
    PROTOCOL_VERSION,
    SEEDS,
    STRUCTURE,
)

BASE_STATES = OrderedDict(
    (
        ("original", {"vision": 582, "projector": 2327, "language": 1187}),
        (
            "language_rich",
            {"vision": 582, "projector": 2327, "language": 3561},
        ),
    )
)

# These coordinates are deliberately absent from the previous curve/state
# experiments.  Existing actual-bit curves predict roughly 2.1--2.8 kbit
# target-module increases for each action.  The intended Language-rich
# Language coordinate 6500 was lowered to the nearest smaller dimension that
# has complete fixed-projection coverage for all three frozen seeds.
UPPER_DIMENSIONS = {
    "original": {"vision": 1700, "language": 2700},
    "language_rich": {"vision": 1700, "language": 5976},
}

CALIBRATION = {
    "source": "existing_actual_module_bit_curves_and_previous_state_step",
    "selection_only_not_an_outcome_metric": True,
    "language_rich_language_projection_adjustment": {
        "intended_coordinate_dimension": 6500,
        "selected_coordinate_dimension": 5976,
        "reason": (
            "nearest_smaller_dimension_with_zero_unused_coordinates_for_all_"
            "three_frozen_seeds"
        ),
    },
    "predicted_median_target_delta_bits": {
        "original": {"vision": 2490, "language": 2749},
        "language_rich": {"vision": 2490, "language": 2113},
    },
    "bit_adequacy_gate": {
        "minimum_target_module_delta_bits_each_seed": 512,
        "maximum_within_state_seed_action_ratio": 2.0,
    },
}

DECISION_RULE = {
    "required_seed_majority": 2,
    "original_expected_order": ["language", "vision"],
    "language_rich_expected_order": ["vision", "language"],
    "median_order_must_match": True,
    "bit_adequacy_gate_must_pass": True,
    "pass_decision": "proceed_to_dynamic_budget_algorithm_design",
    "fail_decision": "stop_language_vision_switch_route_no_expansion",
}

# Seed is the paired block.  The four candidate conditions are shuffled within
# each block using Python random.Random(20260805); the schedule is frozen here.
CANDIDATE_EXECUTION_ORDER = (
    (43101, "language_rich", "language"),
    (43101, "original", "vision"),
    (43101, "language_rich", "vision"),
    (43101, "original", "language"),
    (43102, "language_rich", "vision"),
    (43102, "original", "vision"),
    (43102, "original", "language"),
    (43102, "language_rich", "language"),
    (43103, "language_rich", "language"),
    (43103, "original", "language"),
    (43103, "language_rich", "vision"),
    (43103, "original", "vision"),
)


def normalize_dimensions(values: Mapping[str, Any]) -> dict[str, int]:
    if set(values) != set(COORDINATE_MODULES):
        raise ValueError(
            f"dimensions must contain exactly {COORDINATE_MODULES}"
        )
    result = OrderedDict()
    for module in COORDINATE_MODULES:
        value = values[module]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("coordinate dimensions must be positive integers")
        result[module] = value
    return dict(result)


def candidate_dimensions(base_state: str, module: str) -> dict[str, int]:
    if base_state not in BASE_STATES:
        raise ValueError("unknown base state")
    if module not in ACTION_MODULES:
        raise ValueError("unknown action module")
    dimensions = dict(BASE_STATES[base_state])
    dimensions[module] = UPPER_DIMENSIONS[base_state][module]
    if dimensions[module] <= BASE_STATES[base_state][module]:
        raise ValueError("candidate dimension must increase")
    changed = [
        name
        for name in COORDINATE_MODULES
        if dimensions[name] != BASE_STATES[base_state][name]
    ]
    if changed != [module]:
        raise AssertionError("candidate changes a non-target module")
    return normalize_dimensions(dimensions)


def base_run_id(base_state: str, seed: int) -> str:
    return f"lv-switch-{base_state}-base-seed-{seed}"


def candidate_config_id(base_state: str, module: str) -> str:
    dimension = UPPER_DIMENSIONS[base_state][module]
    return f"lv-switch-{base_state}-{module}-coords-{dimension}"


def candidate_run_id(base_state: str, module: str, seed: int) -> str:
    return f"{candidate_config_id(base_state, module)}-seed-{seed}"


def training_config(run: Mapping[str, Any]) -> dict[str, Any]:
    dimensions = normalize_dimensions(run["coordinate_dimensions"])
    return {
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "config_id": str(run["config_id"]),
        "structure": STRUCTURE,
        "seed": int(run["seed"]),
        "coordinate_dimensions": dimensions,
        "candidate_module": run["module"],
        "baseline_config_id": (
            None
            if run["run_type"] == "reused_base_result"
            else base_run_id(str(run["base_state"]), int(run["seed"]))
        ),
        "base_state": str(run["base_state"]),
        "capacity_control": "coordinate_dimension",
        "scientific_budget_measure": "actual_encoded_bits",
        "projection_rule": "stage2-map-v1/module-specific-fixed-map",
    }


def assert_design() -> None:
    if tuple(BASE_STATES) != ("original", "language_rich"):
        raise AssertionError("base-state set changed")
    if tuple(ACTION_MODULES) != ("vision", "language"):
        raise AssertionError("action set changed")
    if tuple(SEEDS) != (43101, 43102, 43103):
        raise AssertionError("seed set changed")
    expected = {
        "original": {
            "vision": {"vision": 1700, "projector": 2327, "language": 1187},
            "language": {"vision": 582, "projector": 2327, "language": 2700},
        },
        "language_rich": {
            "vision": {"vision": 1700, "projector": 2327, "language": 3561},
            "language": {"vision": 582, "projector": 2327, "language": 5976},
        },
    }
    observed = {
        state: {
            module: candidate_dimensions(state, module)
            for module in ACTION_MODULES
        }
        for state in BASE_STATES
    }
    if observed != expected:
        raise AssertionError("final switch candidate set changed")
    identities = set(CANDIDATE_EXECUTION_ORDER)
    expected_identities = {
        (seed, state, module)
        for seed in SEEDS
        for state in BASE_STATES
        for module in ACTION_MODULES
    }
    if identities != expected_identities or len(CANDIDATE_EXECUTION_ORDER) != 12:
        raise AssertionError("candidate execution schedule changed")


assert_design()
