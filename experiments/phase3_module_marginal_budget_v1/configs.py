"""Explicit private-coordinate baseline and one-module candidate configs."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Mapping

from . import MODULES, PROTOCOL_ID, STRUCTURE


def coordinate_dimensions(values: Mapping[str, int]) -> dict[str, int]:
    if set(values) != set(MODULES):
        raise ValueError(f"coordinate dimensions must contain exactly {MODULES}")
    dimensions = OrderedDict()
    for module in MODULES:
        value = values[module]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("coordinate dimensions must be positive integers")
        dimensions[module] = value
    return dict(dimensions)


@dataclass(frozen=True)
class PrivateConfig:
    config_id: str
    dimensions: Mapping[str, int]
    projection_seed: int
    candidate_module: str | None = None
    baseline_config_id: str | None = None

    def __post_init__(self) -> None:
        if not self.config_id:
            raise ValueError("config_id must be non-empty")
        object.__setattr__(self, "dimensions", coordinate_dimensions(self.dimensions))
        if isinstance(self.projection_seed, bool) or not isinstance(
            self.projection_seed, int
        ):
            raise ValueError("projection_seed must be an integer")
        if (self.candidate_module is None) != (self.baseline_config_id is None):
            raise ValueError(
                "candidate_module and baseline_config_id must both be set or both be null"
            )
        if self.candidate_module is not None and self.candidate_module not in MODULES:
            raise ValueError("unknown candidate module")

    @property
    def coordinate_dimensions(self) -> dict[str, int]:
        return dict(self.dimensions)

    def as_training_config(self) -> dict[str, Any]:
        """Shape expected by the reused Phase 3 P model builder."""
        return {
            "protocol_id": PROTOCOL_ID,
            "config_id": self.config_id,
            "structure": STRUCTURE,
            "seed": self.projection_seed,
            "coordinate_dimensions": self.coordinate_dimensions,
            "candidate_module": self.candidate_module,
            "baseline_config_id": self.baseline_config_id,
            "capacity_control": "coordinate_dimension",
            "scientific_budget_measure": "actual_encoded_bits",
            "projection_rule": "stage2-map-v1/module-specific-fixed-map",
        }


def make_baseline(
    config_id: str, dimensions: Mapping[str, int], projection_seed: int
) -> PrivateConfig:
    return PrivateConfig(config_id, dimensions, projection_seed)


def make_single_module_candidate(
    baseline: PrivateConfig,
    module: str,
    new_dimension: int,
    *,
    config_id: str,
    allow_decrease: bool = False,
) -> PrivateConfig:
    if baseline.candidate_module is not None:
        raise ValueError("candidate must be derived directly from a baseline")
    if module not in MODULES:
        raise ValueError("unknown candidate module")
    dimensions = baseline.coordinate_dimensions
    if isinstance(new_dimension, bool) or not isinstance(new_dimension, int):
        raise ValueError("new dimension must be an integer")
    if new_dimension == dimensions[module] or (
        not allow_decrease and new_dimension < dimensions[module]
    ):
        raise ValueError(
            "candidate must change its target dimension"
            if allow_decrease
            else "a marginal candidate must increase exactly one dimension"
        )
    if new_dimension <= 0:
        raise ValueError("new dimension must be positive")
    dimensions[module] = new_dimension
    candidate = PrivateConfig(
        config_id=config_id,
        dimensions=dimensions,
        projection_seed=baseline.projection_seed,
        candidate_module=module,
        baseline_config_id=baseline.config_id,
    )
    assert_single_module_change(
        baseline, candidate, require_increase=not allow_decrease
    )
    return candidate


def candidates_from_baseline(
    baseline: PrivateConfig, increases: Mapping[str, int]
) -> dict[str, PrivateConfig]:
    if set(increases) != set(MODULES):
        raise ValueError(f"increases must contain exactly {MODULES}")
    return {
        module: make_single_module_candidate(
            baseline,
            module,
            baseline.dimensions[module] + increases[module],
            config_id=f"{baseline.config_id}+{module}-{increases[module]}coords",
        )
        for module in MODULES
    }


def assert_single_module_increment(
    baseline: PrivateConfig, candidate: PrivateConfig
) -> None:
    assert_single_module_change(baseline, candidate, require_increase=True)


def assert_single_module_change(
    baseline: PrivateConfig,
    candidate: PrivateConfig,
    *,
    require_increase: bool = False,
) -> None:
    module = candidate.candidate_module
    if module not in MODULES:
        raise ValueError("candidate module is not declared")
    if candidate.baseline_config_id != baseline.config_id:
        raise ValueError("candidate refers to a different baseline")
    if candidate.projection_seed != baseline.projection_seed:
        raise ValueError("candidate changes the fixed projection seed")
    changed = [
        name
        for name in MODULES
        if candidate.dimensions[name] != baseline.dimensions[name]
    ]
    if changed != [module]:
        raise ValueError("candidate must change only its declared module dimension")
    if require_increase and candidate.dimensions[module] <= baseline.dimensions[module]:
        raise ValueError("candidate must increase its declared module dimension")
