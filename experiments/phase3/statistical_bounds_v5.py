"""Phase 3 v5 nominal fixed-model and compression formulas.

The formulas and delta allocation are frozen.  Because the v5 metrics were
selected after v4 formal results were available, outputs explicitly carry a
post-hoc status and make no unadjusted simultaneous-coverage claim.
"""

from __future__ import annotations

import math
from typing import Any


GLOBAL_DELTA_TOTAL = 0.05
FIXED_MODEL_DELTA_TOTAL = 0.025
COMPRESSION_DELTA_TOTAL = 0.025
FIXED_MODEL_SLOTS = 20
COMPRESSION_SLOTS = 20
FIXED_MODEL_DELTA_EACH = FIXED_MODEL_DELTA_TOTAL / FIXED_MODEL_SLOTS
COMPRESSION_DELTA_EACH = COMPRESSION_DELTA_TOTAL / COMPRESSION_SLOTS

METRIC_SUPPORTS_V5 = {
    "robust_positive_brier_risk": (0.0, 2.0),
    "visual_semantic_loss": (0.0, 1.0),
}

POST_HOC_STATUS = "post_hoc_metric_selected_after_v4_formal_results_available"


def _inputs(empirical_mean: float, metric_name: str, n: int) -> tuple[float, float, float]:
    if metric_name not in METRIC_SUPPORTS_V5 or n <= 0:
        raise ValueError("invalid v5 bound metric or sample size")
    value = float(empirical_mean)
    lower, upper = METRIC_SUPPORTS_V5[metric_name]
    if not math.isfinite(value) or not lower <= value <= upper:
        raise ValueError("empirical v5 metric is outside its support")
    return value, lower, upper


def _visual_lower(raw_upper: float) -> dict[str, float]:
    raw = 4.0 - 8.0 * raw_upper
    return {
        "certified_visual_increment_lower_raw": raw,
        "certified_visual_increment_lower_capped": max(-4.0, min(4.0, raw)),
    }


def fixed_model_upper_v5(
    empirical_mean: float,
    metric_name: str,
    n: int,
    *,
    observed_min: float | None = None,
    observed_max: float | None = None,
) -> dict[str, Any]:
    value, lower, upper = _inputs(empirical_mean, metric_name, n)
    width = upper - lower
    radius = width * math.sqrt(math.log(1.0 / FIXED_MODEL_DELTA_EACH) / (2.0 * n))
    raw = value + radius
    output: dict[str, Any] = {
        "metric_name": metric_name,
        "bound_type": "hoeffding_fixed_model_nominal_post_hoc",
        "empirical_mean": value,
        "support_min": lower,
        "support_max": upper,
        "interval_width": width,
        "observed_group_min": value if observed_min is None else float(observed_min),
        "observed_group_max": value if observed_max is None else float(observed_max),
        "radius": radius,
        "raw_upper_bound": raw,
        "capped_upper_bound": min(raw, upper),
        "n_unique_image_groups": n,
        "delta_family": "fixed_model",
        "delta_family_total": FIXED_MODEL_DELTA_TOTAL,
        "delta_each": FIXED_MODEL_DELTA_EACH,
        "comparison_slots": FIXED_MODEL_SLOTS,
        "selection_status": POST_HOC_STATUS,
        "simultaneous_coverage_claim": False,
    }
    if metric_name == "visual_semantic_loss":
        output.update(_visual_lower(raw))
    return output


def compression_upper_v5(
    empirical_mean: float,
    metric_name: str,
    n: int,
    description_bits: int,
) -> dict[str, Any]:
    value, lower, upper = _inputs(empirical_mean, metric_name, n)
    if isinstance(description_bits, bool) or int(description_bits) <= 0:
        raise ValueError("description_bits must be a positive integer")
    bits = int(description_bits)
    width = upper - lower
    penalty = width * math.sqrt(
        (bits * math.log(2.0) + 2.0 * math.log(bits) + math.log(1.0 / COMPRESSION_DELTA_EACH))
        / (2.0 * n)
    )
    raw = value + penalty
    output: dict[str, Any] = {
        "metric_name": metric_name,
        "bound_type": "compression_nominal_post_hoc",
        "empirical_mean": value,
        "support_min": lower,
        "support_max": upper,
        "interval_width": width,
        "description_bits": bits,
        "penalty": penalty,
        "raw_upper_bound": raw,
        "capped_upper_bound": min(raw, upper),
        "n_unique_image_groups": n,
        "delta_family": "compression",
        "delta_family_total": COMPRESSION_DELTA_TOTAL,
        "delta_each": COMPRESSION_DELTA_EACH,
        "comparison_slots": COMPRESSION_SLOTS,
        "selection_status": POST_HOC_STATUS,
        "simultaneous_coverage_claim": False,
    }
    if metric_name == "visual_semantic_loss":
        output.update(_visual_lower(raw))
    return output


def definition_constant_v5(
    value: float,
    metric_name: str,
    n: int,
    *,
    family: str,
    description_bits: int | None = None,
) -> dict[str, Any]:
    empirical, lower, upper = _inputs(value, metric_name, n)
    if family not in ("fixed_model", "compression"):
        raise ValueError("unknown constant-bound family")
    output: dict[str, Any] = {
        "metric_name": metric_name,
        "bound_type": "definition_constant",
        "empirical_mean": empirical,
        "support_min": lower,
        "support_max": upper,
        "interval_width": 0.0,
        "raw_upper_bound": empirical,
        "capped_upper_bound": empirical,
        "n_unique_image_groups": n,
        "delta_family": family,
        "delta_family_total": FIXED_MODEL_DELTA_TOTAL if family == "fixed_model" else COMPRESSION_DELTA_TOTAL,
        "delta_each": FIXED_MODEL_DELTA_EACH if family == "fixed_model" else COMPRESSION_DELTA_EACH,
        "comparison_slots": FIXED_MODEL_SLOTS if family == "fixed_model" else COMPRESSION_SLOTS,
        "uses_failure_probability": False,
        "selection_status": POST_HOC_STATUS,
        "simultaneous_coverage_claim": False,
    }
    if description_bits is not None:
        output["description_bits"] = int(description_bits)
    if metric_name == "visual_semantic_loss":
        output.update(_visual_lower(empirical))
    return output
