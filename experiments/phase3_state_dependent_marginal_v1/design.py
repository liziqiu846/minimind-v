"""Exact three-state, one-up-step experimental design."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping
from typing import Any

from . import MODULES, PROTOCOL_ID, PROTOCOL_VERSION, SEEDS, STRUCTURE

BASE_STATES = OrderedDict(
    (
        ("original", {"vision": 582, "projector": 2327, "language": 1187}),
        (
            "language_rich",
            {"vision": 582, "projector": 2327, "language": 3561},
        ),
        (
            "projector_rich",
            {"vision": 582, "projector": 6981, "language": 1187},
        ),
    )
)

UPPER_DIMENSIONS = {
    "original": {"vision": 766, "projector": 3063, "language": 1562},
    "language_rich": {"vision": 766, "projector": 3063, "language": 4686},
    "projector_rich": {"vision": 766, "projector": 9187, "language": 1562},
}


def normalize_dimensions(values: Mapping[str, Any]) -> dict[str, int]:
    if tuple(values) != MODULES and set(values) != set(MODULES):
        raise ValueError(f"dimensions must contain exactly {MODULES}")
    result = OrderedDict()
    for module in MODULES:
        value = values[module]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("coordinate dimensions must be positive integers")
        result[module] = value
    return dict(result)


def candidate_dimensions(base_state: str, module: str) -> dict[str, int]:
    if base_state not in BASE_STATES:
        raise ValueError("unknown base state")
    if module not in MODULES:
        raise ValueError("unknown module")
    dimensions = dict(BASE_STATES[base_state])
    dimensions[module] = UPPER_DIMENSIONS[base_state][module]
    if dimensions[module] <= BASE_STATES[base_state][module]:
        raise ValueError("candidate dimension must increase")
    changed = [
        name
        for name in MODULES
        if dimensions[name] != BASE_STATES[base_state][name]
    ]
    if changed != [module]:
        raise AssertionError("candidate changes a non-target module")
    return normalize_dimensions(dimensions)


def base_run_id(base_state: str, seed: int) -> str:
    return f"state-{base_state}-base-seed-{seed}"


def candidate_config_id(base_state: str, module: str) -> str:
    dimension = UPPER_DIMENSIONS[base_state][module]
    return f"state-{base_state}-{module}-coords-{dimension}"


def candidate_run_id(base_state: str, module: str, seed: int) -> str:
    return f"{candidate_config_id(base_state, module)}-seed-{seed}"


def training_config(run: Mapping[str, Any]) -> dict[str, Any]:
    """Return the established private-coordinate model-builder config shape."""
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
            if run["run_type"] == "reused_base"
            else base_run_id(str(run["base_state"]), int(run["seed"]))
        ),
        "base_state": str(run["base_state"]),
        "capacity_control": "coordinate_dimension",
        "scientific_budget_measure": "actual_encoded_bits",
        "projection_rule": "stage2-map-v1/module-specific-fixed-map",
    }


def assert_design() -> None:
    if tuple(BASE_STATES) != ("original", "language_rich", "projector_rich"):
        raise AssertionError("base-state set changed")
    if tuple(SEEDS) != (43101, 43102, 43103):
        raise AssertionError("seed set changed")
    expected = {
        "original": {
            "vision": {"vision": 766, "projector": 2327, "language": 1187},
            "projector": {"vision": 582, "projector": 3063, "language": 1187},
            "language": {"vision": 582, "projector": 2327, "language": 1562},
        },
        "language_rich": {
            "vision": {"vision": 766, "projector": 2327, "language": 3561},
            "projector": {"vision": 582, "projector": 3063, "language": 3561},
            "language": {"vision": 582, "projector": 2327, "language": 4686},
        },
        "projector_rich": {
            "vision": {"vision": 766, "projector": 6981, "language": 1187},
            "projector": {"vision": 582, "projector": 9187, "language": 1187},
            "language": {"vision": 582, "projector": 6981, "language": 1562},
        },
    }
    observed = {
        state: {module: candidate_dimensions(state, module) for module in MODULES}
        for state in BASE_STATES
    }
    if observed != expected:
        raise AssertionError("state-dependent candidate grid changed")


assert_design()
