"""Summarize development-only curve points using adjacent actual-bit differences."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic

from . import CURVE_NAMES, MODULES
from .results import validated_encoded_bits


def _validated_metrics(result: Mapping[str, Any], target_module: str) -> dict[str, Any]:
    if result.get("evaluation_role") != "development_only":
        raise ValueError("curve result is not marked development_only")
    bit_fields = validated_encoded_bits(result)
    target_bits = result.get("target_module_encoded_bits")
    if (
        isinstance(target_bits, bool)
        or not isinstance(target_bits, int)
        or target_bits != bit_fields[f"{target_module}_encoded_bits"]
    ):
        raise ValueError(
            "target_module_encoded_bits differs from the target module codec result"
        )
    risk = float(result["development_task_risk"])
    if not math.isfinite(risk):
        raise ValueError("development task risk must be finite")
    for field in ("semantic_risk_bound", "visual_gain_guardrail"):
        if field not in result:
            raise ValueError(f"completed result must retain {field}")
        if result.get(field) is not None and not math.isfinite(float(result[field])):
            raise ValueError(f"{field} must be finite or null")
    return {
        **bit_fields,
        "target_module_encoded_bits": target_bits,
        "evaluation_role": "development_only",
        "development_task_risk": risk,
        "semantic_risk_bound": result.get("semantic_risk_bound"),
        "visual_gain_guardrail": result.get("visual_gain_guardrail"),
    }


def _validate_completed_result(
    result: Mapping[str, Any],
    planned_point: Mapping[str, Any],
) -> dict[str, Any]:
    target_module = result.get("target_module")
    if target_module != planned_point["target_module"]:
        raise ValueError("completed result target_module differs from its curve")
    if result.get("curve_name") != planned_point["curve_name"]:
        raise ValueError("completed result curve_name differs from its curve")
    result_config_id = result.get("sweep_config_id", result.get("config_id"))
    if result_config_id != planned_point["config_id"]:
        raise ValueError("completed result config_id differs from its curve point")
    if dict(result.get("coordinate_dimensions", {})) != dict(
        planned_point["coordinate_dimensions"]
    ):
        raise ValueError("completed result coordinate dimensions differ from its plan")
    for field in ("seed", "sweep_index"):
        if result.get(field) != planned_point[field]:
            raise ValueError(f"completed result {field} differs from its plan")
    return _validated_metrics(result, target_module)


def _adjacent_differences(points: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    adjacent = []
    for lower, upper in zip(points, points[1:]):
        delta_risk = (
            upper["development_task_risk"] - lower["development_task_risk"]
        )
        delta_bits = (
            upper["target_module_encoded_bits"]
            - lower["target_module_encoded_bits"]
        )
        valid = delta_bits > 0
        adjacent.append(
            {
                "lower_config_id": lower["config_id"],
                "upper_config_id": upper["config_id"],
                "delta_risk": delta_risk,
                "delta_bits": delta_bits,
                "marginal_value": -delta_risk / delta_bits if valid else None,
                "status": "valid" if valid else "invalid_nonpositive_delta_bits",
            }
        )
    return adjacent


def _plan_points(plan: Mapping[str, Any]) -> dict[tuple[str, str], Mapping[str, Any]]:
    planned = {}
    for module in MODULES:
        for point in plan["curves"][module]:
            if (
                point.get("target_module") != module
                or point.get("curve_name") != CURVE_NAMES[module]
            ):
                raise ValueError("curve plan has inconsistent module metadata")
            key = (module, str(point["config_id"]))
            if key in planned:
                raise ValueError("curve plan contains a duplicate point")
            planned[key] = point
    return planned


def summarize_curve_results(
    plan: Mapping[str, Any],
    completed_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Sort completed curve records by target codec bits and difference neighbors."""
    planned = _plan_points(plan)
    by_point: dict[tuple[str, str], dict[str, Any]] = {}
    for result in completed_results:
        target_module = result.get("target_module")
        config_id = str(result["config_id"])
        key = (target_module, config_id)
        if key not in planned:
            raise ValueError(f"completed result is not in the curve plan: {key}")
        if key in by_point:
            raise ValueError(f"duplicate completed result for {key}")
        by_point[key] = _validate_completed_result(result, planned[key])

    summaries = {}
    for module in MODULES:
        points = []
        for membership in plan["curves"][module]:
            config_id = membership["config_id"]
            key = (module, config_id)
            if key not in by_point:
                continue
            result = by_point[key]
            point = {
                **membership,
                **result,
            }
            points.append(point)
        points.sort(key=lambda point: point["target_module_encoded_bits"])
        summaries[module] = {
            "curve_name": CURVE_NAMES[module],
            "target_module": module,
            "sort_key": "target_module_encoded_bits",
            "optimality_metric": "development_task_risk",
            "evaluation_role": "development_only",
            "visual_gain_role": "guardrail_only",
            "points": points,
            "adjacent_differences": _adjacent_differences(points),
        }
    return {
        "schema_version": 1,
        "evaluation_role": "development_only",
        "anchor_config": plan["anchor_config"],
        "curves": summaries,
    }


def _formal_point(
    run: Mapping[str, Any],
    result: Mapping[str, Any],
    membership: Mapping[str, Any],
) -> dict[str, Any]:
    target_module = str(membership["target_module"])
    if target_module not in MODULES:
        raise ValueError("formal curve membership has an invalid target module")
    if membership.get("curve_name") != CURVE_NAMES[target_module]:
        raise ValueError("formal curve membership name differs from its module")
    result_for_curve = dict(result)
    result_for_curve["target_module_encoded_bits"] = result[
        "module_wise_encoded_bits"
    ][target_module]
    metrics = _validated_metrics(result_for_curve, target_module)
    return {
        "run_id": run["run_id"],
        "config_id": run["config_id"],
        "sweep_config_id": run["sweep_config_id"],
        "curve_name": membership["curve_name"],
        "target_module": target_module,
        "coordinate_dimensions": dict(run["coordinate_dimensions"]),
        "sweep_index": membership["sweep_index"],
        "seed": int(run["seed"]),
        "is_anchor": bool(membership["is_anchor"]),
        "checkpoint_path": result.get("checkpoint_path"),
        "module_codec_paths": result.get("module_codec_paths"),
        **metrics,
    }


def summarize_formal_curve_results(
    plan: Mapping[str, Any],
    completed_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Expand shared anchors and form R_V/R_C/R_L independently for each seed."""
    authoritative = {run["run_id"]: run for run in plan["runs"]}
    if len(authoritative) != len(plan["runs"]):
        raise ValueError("formal run plan contains duplicate run identities")
    observed: dict[str, Mapping[str, Any]] = {}
    for result in completed_results:
        run_id = str(result.get("run_id", result.get("config_id")))
        run = authoritative.get(run_id)
        if run is None:
            raise ValueError(f"completed result is absent from the formal plan: {run_id}")
        if run_id in observed:
            raise ValueError(f"duplicate completed formal result: {run_id}")
        if (
            result.get("config_id") != run["config_id"]
            or result.get("seed") != run["seed"]
            or dict(result.get("coordinate_dimensions", {}))
            != dict(run["coordinate_dimensions"])
            or result.get("run_status") != "complete"
        ):
            raise ValueError("completed formal result identity differs from its run")
        observed[run_id] = result

    by_seed: dict[str, Any] = {}
    for seed in plan["formal_seeds"]:
        curves = {}
        for module in MODULES:
            points = []
            for run in plan["runs"]:
                if run["seed"] != seed or run["run_id"] not in observed:
                    continue
                memberships = [
                    membership
                    for membership in run["curve_memberships"]
                    if membership["target_module"] == module
                ]
                for membership in memberships:
                    points.append(
                        _formal_point(run, observed[run["run_id"]], membership)
                    )
            points.sort(key=lambda point: point["target_module_encoded_bits"])
            curves[module] = {
                "curve_name": CURVE_NAMES[module],
                "target_module": module,
                "seed": seed,
                "sort_key": "target_module_encoded_bits",
                "optimality_metric": "development_task_risk",
                "evaluation_role": "development_only",
                "visual_gain_role": "guardrail_only",
                "point_count": len(points),
                "points": points,
                "adjacent_differences": _adjacent_differences(points),
            }
        by_seed[str(seed)] = {"seed": seed, "curves": curves}
    return {
        "schema_version": 1,
        "evaluation_role": "development_only",
        "completed_model_count": len(observed),
        "expected_model_count": int(plan["expanded_run_count"]),
        "complete": len(observed) == int(plan["expanded_run_count"]),
        "anchor_config": plan["anchor_config"],
        "seeds": list(plan["formal_seeds"]),
        "by_seed": by_seed,
    }


def summarize_results_root(
    plan: Mapping[str, Any],
    results_root: Path,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Load valid completed run artifacts and atomically persist a curve summary."""
    results = []
    for run in plan["runs"]:
        path = results_root.resolve() / run["result_relative_directory"] / "run_result.json"
        if path.is_file():
            results.append(json.loads(path.read_text(encoding="utf-8")))
    summary = summarize_formal_curve_results(plan, results)
    destination = output_path or results_root.resolve() / "curve_summary.json"
    write_json_atomic(destination, summary)
    return summary
