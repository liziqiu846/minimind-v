"""Exploratory concentration radii for the coupled, post-hoc v6 analysis."""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


CURRENT_INVALID_REASONS = [
    "post_hoc_metric_design",
    "coupled_mismatch_donors",
]
ANALYSIS_MODES = (
    "current_coupled_post_hoc",
    "fresh_confirmation_independent_donor_bank",
)


def _inputs(
    empirical_mean: float, sample_size: int, delta_each: float
) -> tuple[float, int, float]:
    value = float(empirical_mean)
    if (
        not math.isfinite(value)
        or not 0.0 <= value <= 1.0
        or isinstance(sample_size, bool)
        or int(sample_size) <= 0
        or not math.isfinite(delta_each)
        or not 0.0 < delta_each < 1.0
    ):
        raise ValueError("invalid exploratory Hoeffding inputs")
    return value, int(sample_size), float(delta_each)


def exploratory_upper(
    empirical_mean: float, sample_size: int, delta_each: float
) -> dict[str, Any]:
    value, count, probability = _inputs(
        empirical_mean, sample_size, delta_each
    )
    radius = math.sqrt(math.log(1.0 / probability) / (2.0 * count))
    raw = value + radius
    return {
        "bound_type": "exploratory_hoeffding_radius",
        "empirical_mean": value,
        "support_min": 0.0,
        "support_max": 1.0,
        "sample_size_image_groups": count,
        "delta_each": probability,
        "exploratory_radius": radius,
        "exploratory_upper_bound_raw": raw,
        "exploratory_upper_bound_capped": min(1.0, raw),
    }


def _certification_status(
    *,
    analysis_mode: str,
    metrics_predeclared: bool,
    fresh_confirmation_set: bool,
    independent_frozen_donor_bank: bool,
) -> tuple[bool, list[str]]:
    if analysis_mode not in ANALYSIS_MODES:
        raise ValueError(f"unknown analysis mode: {analysis_mode}")
    reasons = []
    if not metrics_predeclared:
        reasons.append("post_hoc_metric_design")
    if not fresh_confirmation_set:
        reasons.append("not_fresh_confirmation_set")
    if not independent_frozen_donor_bank:
        reasons.append("coupled_mismatch_donors")
    certified = (
        analysis_mode == "fresh_confirmation_independent_donor_bank"
        and not reasons
    )
    return certified, reasons


def analyze_model_summaries(
    summaries: Sequence[Mapping[str, Any]],
    *,
    candidate_family_size: int,
    delta: float = 0.05,
    analysis_mode: str = "current_coupled_post_hoc",
    metrics_predeclared: bool = False,
    fresh_confirmation_set: bool = False,
    independent_frozen_donor_bank: bool = False,
) -> dict[str, Any]:
    if not summaries:
        raise ValueError("exploratory analysis requires at least one model")
    if (
        isinstance(candidate_family_size, bool)
        or int(candidate_family_size) <= 0
        or len(summaries) != int(candidate_family_size)
    ):
        raise ValueError(
            "candidate_family_size must equal the predeclared model family"
        )
    if not math.isfinite(delta) or not 0.0 < delta < 1.0:
        raise ValueError("delta must lie in (0,1)")
    certified, reasons = _certification_status(
        analysis_mode=analysis_mode,
        metrics_predeclared=metrics_predeclared,
        fresh_confirmation_set=fresh_confirmation_set,
        independent_frozen_donor_bank=independent_frozen_donor_bank,
    )
    if analysis_mode == "current_coupled_post_hoc":
        if certified or metrics_predeclared or fresh_confirmation_set or independent_frozen_donor_bank:
            raise ValueError("current coupled post-hoc mode cannot be certified")
        reasons = list(CURRENT_INVALID_REASONS)

    model_count = int(candidate_family_size)
    delta_each_main = delta / (2.0 * model_count)
    delta_each_total = delta / model_count
    models = []
    for summary in summaries:
        risks = summary.get("empirical_risks")
        image_count = int(summary.get("image_count", 0))
        if not isinstance(risks, Mapping) or image_count <= 0:
            raise ValueError("model summary lacks empirical risks or image count")
        language = exploratory_upper(
            float(risks["language_risk"]), image_count, delta_each_main
        )
        visual = exploratory_upper(
            float(risks["visual_risk"]), image_count, delta_each_main
        )
        total = exploratory_upper(
            float(risks["total_semantic_risk"]),
            image_count,
            delta_each_total,
        )
        visual_gain_lower = 1.0 - 2.0 * float(
            visual["exploratory_upper_bound_capped"]
        )
        models.append(
            {
                "model_id": summary["model_id"],
                "method": summary["method"],
                "certified": certified,
                "invalid_for_formal_certification_reasons": reasons,
                "language_risk": language,
                "visual_risk": {
                    **visual,
                    "exploratory_upper_below_0_5": (
                        visual["exploratory_upper_bound_capped"] < 0.5
                    ),
                    "formally_certified_below_0_5": (
                        certified
                        and visual["exploratory_upper_bound_capped"] < 0.5
                    ),
                },
                "visual_gain": {
                    "empirical_mean": float(risks["visual_gain"]),
                    "support_min": -1.0,
                    "support_max": 1.0,
                    "exploratory_lower_bound_derived_from_visual_risk": (
                        visual_gain_lower
                    ),
                },
                "total_semantic_risk_separate_exploratory_family": total,
            }
        )
    return {
        "schema_version": 1,
        "analysis_type": "exploratory_concentration_analysis",
        "analysis_mode": analysis_mode,
        "certified": certified,
        "invalid_for_formal_certification_reasons": reasons,
        "candidate_family_size": model_count,
        "model_count": len(models),
        "familywise_delta": delta,
        "main_risk_family": {
            "metrics": ["language_risk", "visual_risk"],
            "delta_each": delta_each_main,
            "simultaneous_slots": 2 * model_count,
        },
        "total_risk_family": {
            "metrics": ["total_semantic_risk"],
            "delta_each": delta_each_total,
            "simultaneous_slots": model_count,
            "separate_from_main_family": True,
        },
        "formal_certification_gate": {
            "required_analysis_mode": (
                "fresh_confirmation_independent_donor_bank"
            ),
            "metrics_predeclared": metrics_predeclared,
            "fresh_confirmation_set": fresh_confirmation_set,
            "independent_frozen_donor_bank": independent_frozen_donor_bank,
        },
        "models": models,
    }
