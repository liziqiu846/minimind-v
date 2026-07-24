"""Image-equal summaries for Phase 3 v1 decomposed risks."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from experiments.phase3_risk_v1 import RISK_SCHEMA_VERSION
from experiments.phase3_risk_v1.risk_metrics import (
    IDENTITY_TOLERANCE,
    K_MISMATCH,
)
from experiments.phase3_v6.scoring.common import linear_quantile, utf8_key


SUMMARY_METRICS = (
    "q_correct",
    "q_mismatch_mean",
    "language_risk",
    "visual_gain",
    "visual_risk",
    "total_semantic_risk",
    "identity_error",
)
M0_TOLERANCE = 1e-8


def finite_mean(values: Iterable[float]) -> float:
    clean = [float(value) for value in values]
    if not clean or not all(math.isfinite(value) for value in clean):
        raise ValueError("mean input must be non-empty and finite")
    return math.fsum(clean) / len(clean)


def distribution(values: Sequence[float]) -> dict[str, float | int]:
    clean = [float(value) for value in values]
    if not clean or not all(math.isfinite(value) for value in clean):
        raise ValueError("distribution input must be non-empty and finite")
    return {
        "count": len(clean),
        "mean": finite_mean(clean),
        "standard_deviation_population": float(statistics.pstdev(clean)),
        "median": float(statistics.median(clean)),
        "p25": linear_quantile(clean, 0.25),
        "p75": linear_quantile(clean, 0.75),
        "minimum": min(clean),
        "maximum": max(clean),
    }


def _validate_row(row: Mapping[str, Any]) -> None:
    required = {
        "sample_id",
        "filename",
        "negative_type",
        "model_id",
        "method",
        "risk_schema_version",
        *SUMMARY_METRICS,
        *(f"q_mismatch_{index}" for index in range(1, K_MISMATCH + 1)),
    }
    missing = sorted(required.difference(row))
    if missing:
        raise ValueError(
            f"risk row {row.get('sample_id', '<unknown>')} lacks fields: {missing}"
        )
    if row["risk_schema_version"] != RISK_SCHEMA_VERSION:
        raise ValueError("risk schema version mismatch")
    for metric in SUMMARY_METRICS:
        value = float(row[metric])
        if not math.isfinite(value):
            raise ValueError(f"non-finite risk field: {metric}")
    for metric in ("language_risk", "visual_risk", "total_semantic_risk"):
        if not 0.0 <= float(row[metric]) <= 1.0:
            raise ValueError(f"{metric} is outside [0,1]")
    if not -1.0 <= float(row["visual_gain"]) <= 1.0:
        raise ValueError("visual_gain is outside [-1,1]")
    if float(row["identity_error"]) > IDENTITY_TOLERANCE:
        raise AssertionError("a stored row exceeds the identity tolerance")


def aggregate_image_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("image aggregation requires at least one risk row")
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        _validate_row(row)
        grouped[str(row["filename"])].append(row)
    output: list[dict[str, Any]] = []
    for filename in sorted(grouped, key=utf8_key):
        members = grouped[filename]
        model_ids = {str(row["model_id"]) for row in members}
        methods = {str(row["method"]) for row in members}
        if len(model_ids) != 1 or len(methods) != 1:
            raise ValueError("one filename group contains multiple model identities")
        result: dict[str, Any] = {
            "risk_schema_version": RISK_SCHEMA_VERSION,
            "model_id": next(iter(model_ids)),
            "method": next(iter(methods)),
            "filename": filename,
            "record_count": len(members),
            "sample_ids": sorted(
                (str(row["sample_id"]) for row in members), key=utf8_key
            ),
        }
        for metric in SUMMARY_METRICS:
            result[metric] = finite_mean(float(row[metric]) for row in members)
        output.append(result)
    return output


def _category_summaries(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["negative_type"]), str(row["filename"]))].append(row)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (category, filename), members in grouped.items():
        entry: dict[str, Any] = {
            "category": category,
            "filename": filename,
            "record_count": len(members),
        }
        for metric in SUMMARY_METRICS:
            entry[metric] = finite_mean(float(row[metric]) for row in members)
        by_category[category].append(entry)
    output: list[dict[str, Any]] = []
    for category in sorted(by_category, key=utf8_key):
        members = by_category[category]
        result: dict[str, Any] = {
            "category": category,
            "record_count": sum(int(row["record_count"]) for row in members),
            "image_count": len(members),
            "aggregation": "filename_x_category_then_equal_weight_across_filename",
            "metrics": {},
        }
        for metric in SUMMARY_METRICS:
            result["metrics"][metric] = distribution(
                [float(row[metric]) for row in members]
            )
        output.append(result)
    return output


def m0_invariant(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    maximum_context_q_difference = 0.0
    maximum_visual_gain = 0.0
    maximum_visual_risk_half_error = 0.0
    worst: dict[str, Any] | None = None
    for row in rows:
        correct = float(row["q_correct"])
        context_difference = max(
            abs(correct - float(row[f"q_mismatch_{index}"]))
            for index in range(1, K_MISMATCH + 1)
        )
        if context_difference >= maximum_context_q_difference:
            maximum_context_q_difference = context_difference
            worst = {
                "sample_id": row["sample_id"],
                "filename": row["filename"],
                "maximum_context_q_abs_difference": context_difference,
            }
        maximum_visual_gain = max(
            maximum_visual_gain, abs(float(row["visual_gain"]))
        )
        maximum_visual_risk_half_error = max(
            maximum_visual_risk_half_error,
            abs(float(row["visual_risk"]) - 0.5),
        )
    maximum = max(
        maximum_context_q_difference,
        maximum_visual_gain,
        maximum_visual_risk_half_error,
    )
    return {
        "tolerance": M0_TOLERANCE,
        "maximum_context_q_abs_difference": maximum_context_q_difference,
        "maximum_abs_visual_gain": maximum_visual_gain,
        "maximum_abs_visual_risk_minus_half": maximum_visual_risk_half_error,
        "worst_record": worst,
        "passes": maximum <= M0_TOLERANCE,
    }


def summarize_model(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_image_count: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rows:
        raise ValueError("model summary requires at least one row")
    for row in rows:
        _validate_row(row)
    model_ids = {str(row["model_id"]) for row in rows}
    methods = {str(row["method"]) for row in rows}
    if len(model_ids) != 1 or len(methods) != 1:
        raise ValueError("model summary input contains multiple models")
    model_id = next(iter(model_ids))
    method = next(iter(methods))
    image_rows = aggregate_image_rows(rows)
    if expected_image_count is not None and len(image_rows) != expected_image_count:
        raise ValueError(
            f"{model_id} has {len(image_rows)} images, expected {expected_image_count}"
        )
    summary: dict[str, Any] = {
        "schema_version": 1,
        "risk_schema_version": RISK_SCHEMA_VERSION,
        "model_id": model_id,
        "method": method,
        "record_count": len(rows),
        "image_count": len(image_rows),
        "primary_statistical_unit": "unique_filename_image_group",
        "aggregation": "record_within_filename_then_equal_weight_across_filename",
        "record_weighted_descriptive_distributions": {},
        "image_equal_primary_distributions": {},
        "category_summaries": _category_summaries(rows),
        "range_checks": {
            "language_risk": True,
            "visual_risk": True,
            "total_semantic_risk": True,
        },
        "identity_check": {
            "tolerance": IDENTITY_TOLERANCE,
            "maximum_error_record": max(float(row["identity_error"]) for row in rows),
            "maximum_error_image_group": max(
                float(row["identity_error"]) for row in image_rows
            ),
            "passes": True,
        },
    }
    for metric in SUMMARY_METRICS:
        summary["record_weighted_descriptive_distributions"][metric] = distribution(
            [float(row[metric]) for row in rows]
        )
        summary["image_equal_primary_distributions"][metric] = distribution(
            [float(row[metric]) for row in image_rows]
        )
    summary["empirical_risks"] = {
        metric: summary["image_equal_primary_distributions"][metric]["mean"]
        for metric in (
            "language_risk",
            "visual_risk",
            "total_semantic_risk",
            "visual_gain",
        )
    }
    summary["m0_invariant"] = m0_invariant(rows) if method == "M0" else None
    if method == "M0" and not summary["m0_invariant"]["passes"]:
        raise AssertionError(f"{model_id} failed the M0 invariant")
    return image_rows, summary
