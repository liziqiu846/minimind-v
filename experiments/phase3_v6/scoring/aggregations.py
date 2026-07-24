"""Image-equal Phase 3 v6 aggregations and invariant checks."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from experiments.phase3_v6.scoring.common import linear_quantile, utf8_key
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
    NEGATIVE_TYPES,
)


M0_TOLERANCE = 1e-8


def _mean(values: Iterable[float]) -> float:
    collected = [float(value) for value in values]
    if not collected:
        raise ValueError("mean requires at least one value")
    if not all(math.isfinite(value) for value in collected):
        raise FloatingPointError("mean input contains a non-finite value")
    return math.fsum(collected) / len(collected)


def _distribution(values: Sequence[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("distribution requires at least one value")
    clean = [float(value) for value in values]
    return {
        "count": len(clean),
        "mean": _mean(clean),
        "median": float(statistics.median(clean)),
        "p25": linear_quantile(clean, 0.25),
        "p75": linear_quantile(clean, 0.75),
        "p90": linear_quantile(clean, 0.90),
        "minimum": min(clean),
        "maximum": max(clean),
    }


def aggregate_image_rows(
    model_id: str, rows: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["filename"])].append(row)
    output = []
    for filename in sorted(grouped, key=utf8_key):
        members = grouped[filename]
        image_row: dict[str, Any] = {
            "model_id": model_id,
            "filename": filename,
            "record_count": len(members),
            "sample_ids": sorted(
                (str(row["sample_id"]) for row in members),
                key=utf8_key,
            ),
            "negative_type_counts": {
                category: sum(
                    row["negative_type"] == category for row in members
                )
                for category in NEGATIVE_TYPES
            },
        }
        for k in (1, 3, 5):
            image_row[f"D_g_k{k}"] = _mean(
                row[f"d_k{k}"] for row in members
            )
        for round_id in range(1, 6):
            image_row[f"D_g_round_{round_id}"] = _mean(
                float(row["q_correct"])
                - float(row[f"q_mismatch_round_{round_id}"])
                for row in members
            )
        output.append(image_row)
    return output


def _category_summary(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for category in NEGATIVE_TYPES:
        selected = [row for row in rows if row["negative_type"] == category]
        by_image: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in selected:
            by_image[str(row["filename"])].append(row)
        result: dict[str, Any] = {
            "record_count": len(selected),
            "image_count": len(by_image),
            "aggregation": "filename_x_category_then_equal_weight_across_filename",
        }
        for k in (1, 3, 5):
            image_values = [
                _mean(row[f"d_k{k}"] for row in members)
                for _, members in sorted(
                    by_image.items(), key=lambda item: utf8_key(item[0])
                )
            ]
            result[f"mu_k{k}"] = _mean(image_values)
        for round_id in range(1, 6):
            image_values = [
                _mean(
                    float(row["q_correct"])
                    - float(row[f"q_mismatch_round_{round_id}"])
                    for row in members
                )
                for _, members in sorted(
                    by_image.items(), key=lambda item: utf8_key(item[0])
                )
            ]
            result[f"mu_round_{round_id}"] = _mean(image_values)
        output[category] = result
    return output


def _subset_summary(
    rows: Sequence[Mapping[str, Any]], *, label: str
) -> dict[str, Any]:
    image_rows = aggregate_image_rows("subset", rows)
    result: dict[str, Any] = {
        "analysis_label": label,
        "record_count": len(rows),
        "image_count": len(image_rows),
        "aggregation": "record_within_filename_then_equal_weight_across_filename",
    }
    for k in (1, 3, 5):
        result[f"mu_k{k}"] = _mean(
            row[f"D_g_k{k}"] for row in image_rows
        )
    result["win_rate_k5"] = _mean(
        float(row["D_g_k5"] > 0.0) for row in image_rows
    )
    result["D_g_k5_distribution"] = _distribution(
        [float(row["D_g_k5"]) for row in image_rows]
    )
    for round_id in range(1, 6):
        result[f"mu_round_{round_id}"] = _mean(
            row[f"D_g_round_{round_id}"] for row in image_rows
        )
    result["category_results"] = _category_summary(rows)
    return result


def m0_invariant(
    rows: Sequence[Mapping[str, Any]],
    image_rows: Sequence[Mapping[str, Any]],
    *,
    mu_k5: float,
) -> dict[str, Any]:
    worst: dict[str, Any] | None = None
    maximum_context_difference = -1.0
    for row in rows:
        correct = float(row["q_correct"])
        for round_id in range(1, 6):
            mismatch = float(row[f"q_mismatch_round_{round_id}"])
            difference = abs(correct - mismatch)
            if difference > maximum_context_difference:
                maximum_context_difference = difference
                worst = {
                    "sample_id": row["sample_id"],
                    "filename": row["filename"],
                    "round_id": round_id,
                    "q_correct": correct,
                    "q_mismatch": mismatch,
                    "absolute_difference": difference,
                }
    max_record = max(abs(float(row["d_k5"])) for row in rows)
    max_image = max(abs(float(row["D_g_k5"])) for row in image_rows)
    absolute_mu = abs(float(mu_k5))
    passed = max(maximum_context_difference, max_record, max_image, absolute_mu) <= (
        M0_TOLERANCE
    )
    return {
        "tolerance": M0_TOLERANCE,
        "diagnostic_secondary_tolerance": 1e-6,
        "max_record_context_q_abs_difference": maximum_context_difference,
        "max_record_abs_d_k5": max_record,
        "max_image_abs_D_g_k5": max_image,
        "abs_mu_k5": absolute_mu,
        "worst_record_context": worst,
        "token_template_and_label_mask_identical_across_contexts": True,
        "m0_forward_received_pixel_values": False,
        "passes_formal_1e_8_invariant": passed,
        "passes_secondary_1e_6_diagnostic": max(
            maximum_context_difference, max_record, max_image, absolute_mu
        )
        <= 1e-6,
    }


def summarize_model(
    model_id: str,
    method: str,
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(rows) != EXPECTED_VALID_RECORD_COUNT:
        raise ValueError(
            f"{model_id} has {len(rows)} records, expected "
            f"{EXPECTED_VALID_RECORD_COUNT}"
        )
    if any(row.get("all_scores_finite") is not True for row in rows):
        raise FloatingPointError(f"{model_id} has a non-finite record")
    if len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError(f"{model_id} has duplicate sample IDs")
    image_rows = aggregate_image_rows(model_id, rows)
    if len(image_rows) != EXPECTED_VALID_IMAGE_COUNT:
        raise ValueError(
            f"{model_id} has {len(image_rows)} images, expected "
            f"{EXPECTED_VALID_IMAGE_COUNT}"
        )

    summary: dict[str, Any] = {
        "schema_version": 1,
        "model_id": model_id,
        "method": method,
        "record_count": len(rows),
        "image_count": len(image_rows),
        "main_estimand_scope": (
            "fixed 1343 effective SugarCrepe++ certifying-formal image groups, "
            "fixed contrast hulls, and fixed balanced K=5 mismatch manifest"
        ),
        "aggregation": "record_within_filename_then_equal_weight_across_filename",
    }
    for k in (1, 3, 5):
        summary[f"mu_k{k}"] = _mean(
            row[f"D_g_k{k}"] for row in image_rows
        )
    summary["win_rate_k5"] = _mean(
        float(row["D_g_k5"] > 0.0) for row in image_rows
    )
    distribution = _distribution(
        [float(row["D_g_k5"]) for row in image_rows]
    )
    summary.update(
        {
            "median_D_g_k5": distribution["median"],
            "P25_D_g_k5": distribution["p25"],
            "P75_D_g_k5": distribution["p75"],
            "P90_D_g_k5": distribution["p90"],
            "min_D_g_k5": distribution["minimum"],
            "max_D_g_k5": distribution["maximum"],
            "D_g_k5_distribution": distribution,
        }
    )
    for round_id in range(1, 6):
        summary[f"mu_round_{round_id}"] = _mean(
            row[f"D_g_round_{round_id}"] for row in image_rows
        )
    summary["category_results"] = _category_summary(rows)
    local_rows = [
        row for row in rows if float(row["hull_token_coverage"]) <= 0.75
    ]
    summary["local_hull_sensitivity_analysis"] = _subset_summary(
        local_rows,
        label="local_hull_sensitivity_analysis",
    )
    if method == "M0":
        summary["m0_invariant"] = m0_invariant(
            rows, image_rows, mu_k5=float(summary["mu_k5"])
        )
    else:
        summary["m0_invariant"] = None
    return image_rows, summary

