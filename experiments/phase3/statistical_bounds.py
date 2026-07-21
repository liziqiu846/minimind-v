"""Frozen Phase 3 Hoeffding and exploratory compression bounds."""

from __future__ import annotations

import math
from typing import Any


DELTA_MAIN_TOTAL = 0.05
MAIN_COMPARISON_SLOTS = 30
DELTA_MAIN_EACH = DELTA_MAIN_TOTAL / MAIN_COMPARISON_SLOTS
DELTA_COMPRESSION_TOTAL = 0.05
COMPRESSION_COMPARISON_SLOTS = 30
DELTA_COMPRESSION_EACH = DELTA_COMPRESSION_TOTAL / COMPRESSION_COMPARISON_SLOTS


def hoeffding_upper(
    empirical_mean: float,
    lower: float,
    upper: float,
    n: int,
    *,
    observed_min: float | None = None,
    observed_max: float | None = None,
) -> dict[str, Any]:
    if n <= 0 or not lower <= empirical_mean <= upper or upper < lower:
        raise ValueError("invalid Hoeffding inputs")
    width = upper - lower
    radius = width * math.sqrt(math.log(1.0 / DELTA_MAIN_EACH) / (2.0 * n))
    raw = empirical_mean + radius
    return {
        "empirical_mean": empirical_mean,
        "nominal_metric_range_min": lower,
        "nominal_metric_range_max": upper,
        "bound_support_min": lower,
        "bound_support_max": upper,
        "interval_width": width,
        "observed_group_min": empirical_mean if observed_min is None else observed_min,
        "observed_group_max": empirical_mean if observed_max is None else observed_max,
        "hoeffding_radius": radius,
        "raw_upper_bound": raw,
        "capped_upper_bound": min(raw, upper),
        "n_unique_image_groups": n,
        "delta_family": "main",
        "delta_family_total": DELTA_MAIN_TOTAL,
        "delta_each": DELTA_MAIN_EACH,
        "comparison_slots": MAIN_COMPARISON_SLOTS,
        "bound_method": "hoeffding_iid_superpopulation",
    }


def definition_constant(value: float, n: int) -> dict[str, Any]:
    return {
        "empirical_mean": value,
        "nominal_metric_range_min": 0.0,
        "nominal_metric_range_max": 1.0,
        "bound_support_min": value,
        "bound_support_max": value,
        "interval_width": 0.0,
        "observed_group_min": value,
        "observed_group_max": value,
        "hoeffding_radius": 0.0,
        "raw_upper_bound": value,
        "capped_upper_bound": value,
        "n_unique_image_groups": n,
        "delta_family": "main",
        "delta_family_total": DELTA_MAIN_TOTAL,
        "delta_each": DELTA_MAIN_EACH,
        "comparison_slots": MAIN_COMPARISON_SLOTS,
        "bound_method": "definition_constant",
    }


def compression_upper(
    empirical_mean: float, lower: float, upper: float, n: int, description_bits: int
) -> dict[str, Any]:
    if n <= 0 or description_bits <= 0 or not lower <= empirical_mean <= upper:
        raise ValueError("invalid compression-bound inputs")
    width = upper - lower
    penalty = width * math.sqrt(
        (
            description_bits * math.log(2)
            + 2 * math.log(description_bits)
            + math.log(1.0 / DELTA_COMPRESSION_EACH)
        )
        / (2.0 * n)
    )
    raw = empirical_mean + penalty
    return {
        "description_bits": description_bits,
        "exploratory_compression_bound_raw": raw,
        "exploratory_compression_bound_capped": min(raw, upper),
        "delta_family": "compression",
        "delta_family_total": DELTA_COMPRESSION_TOTAL,
        "delta_each": DELTA_COMPRESSION_EACH,
        "comparison_slots": COMPRESSION_COMPARISON_SLOTS,
    }
