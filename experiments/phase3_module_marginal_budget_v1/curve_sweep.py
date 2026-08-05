"""Generate deduplicated plans for three one-module capacity curves."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping, Sequence
from typing import Any

from experiments.phase3_private_vs_shared_v1 import SEEDS

from . import (
    CURVE_NAMES,
    MODULES,
    PROTOCOL_ID,
    PROTOCOL_VERSION,
    SEED_PLACEHOLDER,
)
from .anchor import resolve_p4096_anchor
from .configs import (
    coordinate_dimensions,
    make_baseline,
    make_single_module_candidate,
)


def _validate_points(module: str, points: Sequence[int], anchor: int) -> list[int]:
    values = list(points)
    if not values:
        raise ValueError(f"{module} capacity list is empty")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in values
    ):
        raise ValueError("capacity points must be positive integers")
    if len(values) != len(set(values)):
        raise ValueError(f"{module} capacity list contains duplicates")
    if anchor not in values:
        raise ValueError(
            f"{module} capacity list must explicitly include P-4096 anchor"
        )
    return values


def _authoritative_anchor(
    anchor_config: Mapping[str, Any] | None,
) -> dict[str, Any]:
    authority = resolve_p4096_anchor()
    if anchor_config is None:
        return authority
    if "coordinate_dimensions" in anchor_config:
        supplied_dimensions = coordinate_dimensions(
            anchor_config["coordinate_dimensions"]
        )
        if anchor_config.get("anchor_id", "P-4096") != "P-4096":
            raise ValueError("anchor_config must identify P-4096")
    else:
        supplied_dimensions = coordinate_dimensions(anchor_config)
    if supplied_dimensions != authority["coordinate_dimensions"]:
        raise ValueError(
            "anchor_config differs from the authoritative frozen P-4096 allocation"
        )
    return authority


def _validate_seed(seed: int) -> None:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed not in SEEDS:
        raise ValueError("seed is outside the frozen fixed-projection roots")


def build_module_curve(
    *,
    anchor_config: Mapping[str, Any],
    target_module: str,
    capacity_points: Sequence[int],
    seed: int,
) -> list[dict[str, Any]]:
    """Build one curve while holding both non-target modules at P-4096."""
    if target_module not in MODULES:
        raise ValueError(f"target_module must be one of {MODULES}")
    _validate_seed(seed)
    authority = _authoritative_anchor(anchor_config)
    anchor_dimensions = authority["coordinate_dimensions"]
    points = _validate_points(
        target_module, capacity_points, anchor_dimensions[target_module]
    )
    baseline = make_baseline(f"P-4096-anchor-seed-{seed}", anchor_dimensions, seed)
    curve = []
    for sweep_index, dimension in enumerate(points):
        if dimension == anchor_dimensions[target_module]:
            config = baseline
            is_anchor = True
        else:
            config = make_single_module_candidate(
                baseline,
                target_module,
                dimension,
                config_id=(f"P-4096-{target_module}-coords-{dimension}-seed-{seed}"),
                allow_decrease=True,
            )
            is_anchor = False
        dimensions = config.coordinate_dimensions
        if any(
            dimensions[module] != anchor_dimensions[module]
            for module in MODULES
            if module != target_module
        ):
            raise AssertionError("a non-target module differs from P-4096")
        curve.append(
            {
                "curve_name": CURVE_NAMES[target_module],
                "target_module": target_module,
                "anchor_config": deepcopy(authority),
                "coordinate_dimensions": dimensions,
                "sweep_index": sweep_index,
                "seed": seed,
                "config_id": config.config_id,
                "is_anchor": is_anchor,
                "training_config": config.as_training_config(),
            }
        )
    return curve


def build_curve_sweep_plan(
    capacity_points: Mapping[str, Sequence[int]],
    *,
    seed: int,
    anchor_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build all curves; capacity values are caller supplied and never inferred."""
    if set(capacity_points) != set(MODULES):
        raise ValueError(f"capacity_points must contain exactly {MODULES}")
    _validate_seed(seed)
    authority = _authoritative_anchor(anchor_config)
    anchor_dimensions = authority["coordinate_dimensions"]
    baseline = make_baseline(f"P-4096-anchor-seed-{seed}", anchor_dimensions, seed)
    anchor_record = {
        "curve_name": "shared_anchor",
        "target_module": None,
        "anchor_config": deepcopy(authority),
        "coordinate_dimensions": baseline.coordinate_dimensions,
        "sweep_index": None,
        "seed": seed,
        "config_id": baseline.config_id,
        "is_anchor": True,
        "training_config": baseline.as_training_config(),
        "curve_memberships": [],
    }
    configs = [anchor_record]
    curves: dict[str, list[dict[str, Any]]] = {}
    for module in MODULES:
        curve = build_module_curve(
            anchor_config=authority,
            target_module=module,
            capacity_points=capacity_points[module],
            seed=seed,
        )
        curves[module] = curve
        for point in curve:
            membership = {
                key: point[key]
                for key in (
                    "curve_name",
                    "target_module",
                    "sweep_index",
                    "config_id",
                    "is_anchor",
                )
            }
            if point["is_anchor"]:
                anchor_record["curve_memberships"].append(membership)
            else:
                configs.append(
                    {
                        **point,
                        "is_anchor": False,
                        "curve_memberships": [membership],
                    }
                )
    ids = [config["config_id"] for config in configs]
    if len(ids) != len(set(ids)):
        raise AssertionError("sweep plan contains duplicate training configs")
    if len(anchor_record["curve_memberships"]) != len(MODULES):
        raise AssertionError("all three curves must share the one P-4096 anchor")
    return {
        "schema_version": 1,
        "protocol_id": PROTOCOL_ID,
        "anchor_config": deepcopy(authority),
        "seed": seed,
        "configs": configs,
        "curves": curves,
        "curve_names": dict(CURVE_NAMES),
        "budget_measure": "target_module_encoded_bits",
        "coordinate_dimension_role": "trainable_capacity_control_only",
    }


def build_seed_placeholder_sweep_manifest(
    capacity_points: Mapping[str, Sequence[int]],
    *,
    anchor_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the seed-independent 25-config plan to be frozen after preflight."""
    if set(capacity_points) != set(MODULES):
        raise ValueError(f"capacity_points must contain exactly {MODULES}")
    authority = _authoritative_anchor(anchor_config)
    anchor_dimensions = authority["coordinate_dimensions"]
    anchor_id = "P-4096-anchor"
    anchor_record = {
        "curve_name": "shared_anchor",
        "target_module": None,
        "anchor_config": anchor_id,
        "coordinate_dimensions": dict(anchor_dimensions),
        "sweep_index": None,
        "seed": SEED_PLACEHOLDER,
        "config_id": anchor_id,
        "protocol_version": PROTOCOL_VERSION,
        "is_anchor": True,
        "curve_memberships": [],
    }
    configs = [anchor_record]
    curves: dict[str, list[dict[str, Any]]] = {}
    for module in MODULES:
        points = _validate_points(
            module, capacity_points[module], anchor_dimensions[module]
        )
        curve = []
        for sweep_index, dimension in enumerate(points):
            dimensions = dict(anchor_dimensions)
            dimensions[module] = dimension
            is_anchor = dimensions == anchor_dimensions
            config_id = (
                anchor_id if is_anchor else f"P-4096-{module}-coords-{dimension}"
            )
            point = {
                "curve_name": CURVE_NAMES[module],
                "target_module": module,
                "anchor_config": anchor_id,
                "coordinate_dimensions": dimensions,
                "sweep_index": sweep_index,
                "seed": SEED_PLACEHOLDER,
                "config_id": config_id,
                "protocol_version": PROTOCOL_VERSION,
                "is_anchor": is_anchor,
            }
            curve.append(point)
            membership = {
                key: point[key]
                for key in (
                    "curve_name",
                    "target_module",
                    "sweep_index",
                    "config_id",
                    "is_anchor",
                )
            }
            if is_anchor:
                anchor_record["curve_memberships"].append(membership)
            else:
                configs.append(
                    {
                        **point,
                        "curve_memberships": [membership],
                    }
                )
        curves[module] = curve
    ids = [config["config_id"] for config in configs]
    if len(ids) != 25 or len(ids) != len(set(ids)):
        raise ValueError("a three-by-nine sweep must contain 25 distinct configs")
    if len(anchor_record["curve_memberships"]) != len(MODULES):
        raise AssertionError("all curves must reference the one anchor config")
    return {
        "schema_version": 1,
        "status": "pending_preflight",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "anchor_config": {
            **deepcopy(authority),
            "config_id": anchor_id,
        },
        "seed": SEED_PLACEHOLDER,
        "seed_status": "placeholder",
        "capacity_points": {
            module: list(capacity_points[module]) for module in MODULES
        },
        "distinct_config_count": len(configs),
        "curve_point_membership_count": sum(map(len, curves.values())),
        "configs": configs,
        "curves": curves,
        "curve_names": dict(CURVE_NAMES),
        "budget_measure_after_training": "target_module_encoded_bits",
        "coordinate_dimension_role": "trainable_capacity_control_only",
    }
