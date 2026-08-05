"""Result schemas and marginal-value arithmetic; no experiment matrix policy."""

from __future__ import annotations

import math
from typing import Any, Mapping

from . import CURVE_NAMES, MODULES
from .configs import PrivateConfig, assert_single_module_change


def _encoded_bit_value(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def validated_encoded_bits(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return exact codec bit fields after cross-checking all redundancies."""
    grouped = receipt.get("module_wise_encoded_bits")
    if grouped is None:
        module_bits = {
            module: _encoded_bit_value(
                receipt.get(f"{module}_encoded_bits"),
                f"{module}_encoded_bits",
            )
            for module in MODULES
        }
    else:
        if not isinstance(grouped, Mapping) or set(grouped) != set(MODULES):
            raise ValueError(f"module-wise encoded bits must contain exactly {MODULES}")
        module_bits = {
            module: _encoded_bit_value(
                grouped[module],
                f"{module}_encoded_bits",
            )
            for module in MODULES
        }
    for module in MODULES:
        field = f"{module}_encoded_bits"
        if (
            field in receipt
            and _encoded_bit_value(receipt[field], field) != module_bits[module]
        ):
            raise ValueError(f"{field} differs from module-wise encoded bits")
    total_bits = _encoded_bit_value(
        receipt.get("total_encoded_bits"), "total_encoded_bits"
    )
    if sum(module_bits.values()) != total_bits:
        raise ValueError("module-wise encoded bits do not sum to total encoded bits")
    return {
        "module_wise_encoded_bits": module_bits,
        **{f"{module}_encoded_bits": module_bits[module] for module in MODULES},
        "total_encoded_bits": total_bits,
    }


def result_template(
    baseline: PrivateConfig,
    candidate: PrivateConfig,
) -> dict[str, Any]:
    assert_single_module_change(baseline, candidate)
    return {
        "schema_version": 1,
        "baseline_config": baseline.as_training_config(),
        "candidate_config": candidate.as_training_config(),
        "candidate_module": candidate.candidate_module,
        "coordinate_dimensions": candidate.coordinate_dimensions,
        "module_wise_encoded_bits": {name: None for name in MODULES},
        "vision_encoded_bits": None,
        "projector_encoded_bits": None,
        "language_encoded_bits": None,
        "target_module_encoded_bits": None,
        "total_encoded_bits": None,
        "evaluation_role": "development_only",
        "development_task_risk": None,
        "semantic_risk_bound": None,
        "visual_gain_guardrail": None,
        "delta_risk": None,
        "delta_encoded_bits": None,
        "marginal_value": None,
        "delta_risk_definition": "baseline_risk - candidate_risk",
        "marginal_value_definition": "delta_risk / delta_encoded_bits",
    }


def curve_result_template(curve_point: Mapping[str, Any]) -> dict[str, Any]:
    """Create the result schema for one curve membership, including the anchor."""
    target_module = curve_point.get("target_module")
    if target_module not in MODULES:
        raise ValueError("curve point has no valid target_module")
    if curve_point.get("curve_name") != CURVE_NAMES[target_module]:
        raise ValueError("curve point name does not match its target_module")
    required = (
        "anchor_config",
        "coordinate_dimensions",
        "sweep_index",
        "seed",
        "config_id",
        "is_anchor",
    )
    missing = [field for field in required if field not in curve_point]
    if missing:
        raise ValueError(f"curve point is missing fields: {missing}")
    return {
        "schema_version": 1,
        "curve_name": curve_point["curve_name"],
        "target_module": target_module,
        "anchor_config": curve_point["anchor_config"],
        "coordinate_dimensions": dict(curve_point["coordinate_dimensions"]),
        "sweep_index": curve_point["sweep_index"],
        "seed": curve_point["seed"],
        "config_id": curve_point["config_id"],
        "is_anchor": curve_point["is_anchor"],
        "module_wise_encoded_bits": {name: None for name in MODULES},
        "vision_encoded_bits": None,
        "projector_encoded_bits": None,
        "language_encoded_bits": None,
        "total_encoded_bits": None,
        "target_module_encoded_bits": None,
        "evaluation_role": "development_only",
        "development_task_risk": None,
        "semantic_risk_bound": None,
        "visual_gain_guardrail": None,
        "budget_measure": "actual_encoded_bits",
        "curve_x_axis": "target_module_encoded_bits",
        "curve_optimality_metric": "development_task_risk",
        "visual_gain_role": "guardrail_only",
    }


def build_curve_result(
    curve_point: Mapping[str, Any],
    encoding_receipt: Mapping[str, Any],
    *,
    development_task_risk: float,
    semantic_risk_bound: float | None,
    visual_gain_guardrail: float | None,
) -> dict[str, Any]:
    """Bind codec-measured bits and retained risks to one planned curve point."""
    result = curve_result_template(curve_point)
    bit_fields = validated_encoded_bits(encoding_receipt)
    risk = float(development_task_risk)
    if not math.isfinite(risk):
        raise ValueError("development task risk must be finite")
    optional_risks = {
        "semantic_risk_bound": semantic_risk_bound,
        "visual_gain_guardrail": visual_gain_guardrail,
    }
    for field, value in optional_risks.items():
        if value is not None and not math.isfinite(float(value)):
            raise ValueError(f"{field} must be finite or null")
    target_module = result["target_module"]
    result.update(bit_fields)
    result.update(
        {
            "target_module_encoded_bits": bit_fields[f"{target_module}_encoded_bits"],
            "evaluation_role": "development_only",
            "development_task_risk": risk,
            "semantic_risk_bound": (
                None if semantic_risk_bound is None else float(semantic_risk_bound)
            ),
            "visual_gain_guardrail": (
                None if visual_gain_guardrail is None else float(visual_gain_guardrail)
            ),
        }
    )
    return result


def encoded_bit_delta(
    baseline_encoding: Mapping[str, Any],
    candidate_encoding: Mapping[str, Any],
) -> int:
    baseline_bits = validated_encoded_bits(baseline_encoding)
    candidate_bits = validated_encoded_bits(candidate_encoding)
    return candidate_bits["total_encoded_bits"] - baseline_bits["total_encoded_bits"]


def marginal_value(
    *,
    baseline_risk: float,
    candidate_risk: float,
    baseline_encoding: Mapping[str, Any],
    candidate_encoding: Mapping[str, Any],
) -> dict[str, float | int]:
    risks = (float(baseline_risk), float(candidate_risk))
    if any(not math.isfinite(value) for value in risks):
        raise ValueError("risks must be finite")
    delta_bits = encoded_bit_delta(baseline_encoding, candidate_encoding)
    if delta_bits <= 0:
        raise ValueError("marginal value requires a positive actual encoded-bit delta")
    delta_risk = risks[0] - risks[1]
    return {
        "delta_risk": delta_risk,
        "delta_encoded_bits": delta_bits,
        "marginal_value": delta_risk / delta_bits,
    }
