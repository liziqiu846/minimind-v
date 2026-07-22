"""Phase 3 v5 row risks and equal-weight image-group aggregation.

The two primary risks are fixed by the v5 theory note.  The module deliberately
does not clip invalid inputs: a value outside its mathematical support is a hard
failure, not something aggregation is allowed to repair.
"""

from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable

import numpy as np


PRIMARY_METRICS_V5 = (
    "robust_positive_brier_risk",
    "visual_semantic_loss",
)

DIAGNOSTIC_METRICS_V5 = (
    "positive_brier_mean",
    "positive_brier_dispersion",
    "image_robust_margin",
    "none_robust_margin",
    "visual_increment",
    "triplet_success",
    "lm_triplet_success",
    "visual_increment_success",
)

_BRIER_KEYS_VLM = (
    "b_img_pos1", "b_img_pos2", "b_img_neg",
    "b_none_pos1", "b_none_pos2", "b_none_neg",
)
_BRIER_KEYS_M0 = ("b_none_pos1", "b_none_pos2", "b_none_neg")


def _finite_float(values: dict[str, Any], key: str) -> float:
    if key not in values or isinstance(values[key], bool):
        raise ValueError(f"missing or non-numeric Brier field: {key}")
    value = float(values[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite Brier field: {key}")
    if not 0.0 <= value <= 2.0:
        raise ValueError(f"Brier field outside [0,2]: {key}={value}")
    return value


def _optional_raw_margin(values: dict[str, Any], prefix: str) -> float | None:
    keys = (f"b_{prefix}_pos1_raw", f"b_{prefix}_pos2_raw", f"b_{prefix}_neg_raw")
    if not any(key in values for key in keys):
        return None
    if not all(key in values for key in keys):
        raise ValueError(f"partially present raw {prefix} Brier fields")
    raw = [float(values[key]) for key in keys]
    if not all(math.isfinite(value) for value in raw):
        raise ValueError(f"non-finite raw {prefix} Brier field")
    return raw[2] - max(raw[0], raw[1])


def visual_row_metrics_v5(values: dict[str, float]) -> dict[str, Any]:
    """Calculate the v5 VLM metrics for one SugarCrepe++ source row."""

    b = {key: _finite_float(values, key) for key in _BRIER_KEYS_VLM}
    image_mean = (b["b_img_pos1"] + b["b_img_pos2"]) / 2.0
    image_dispersion = abs(b["b_img_pos1"] - b["b_img_pos2"]) / 2.0
    image_robust_positive = max(b["b_img_pos1"], b["b_img_pos2"])

    none_mean = (b["b_none_pos1"] + b["b_none_pos2"]) / 2.0
    none_dispersion = abs(b["b_none_pos1"] - b["b_none_pos2"]) / 2.0
    none_robust_positive = max(b["b_none_pos1"], b["b_none_pos2"])

    image_robust_margin = b["b_img_neg"] - image_robust_positive
    none_robust_margin = b["b_none_neg"] - none_robust_positive
    visual_increment = image_robust_margin - none_robust_margin
    visual_semantic_loss = (4.0 - visual_increment) / 8.0

    identity_error = abs(image_robust_positive - (image_mean + image_dispersion))
    if identity_error > 1e-12:
        raise AssertionError(f"max=mean+dispersion identity failed: {identity_error}")
    if not 0.0 <= image_robust_positive <= 2.0:
        raise ValueError("robust_positive_brier_risk outside [0,2]")
    if not -4.0 <= visual_increment <= 4.0:
        raise ValueError("visual_increment outside [-4,4]")
    if not 0.0 <= visual_semantic_loss <= 1.0:
        raise ValueError("visual_semantic_loss outside [0,1]")

    raw_image_margin = _optional_raw_margin(values, "img")
    raw_none_margin = _optional_raw_margin(values, "none")
    result: dict[str, Any] = {
        **values,
        "positive_brier_mean": image_mean,
        "positive_brier_dispersion": image_dispersion,
        "robust_positive_brier_risk": image_robust_positive,
        "none_positive_brier_mean": none_mean,
        "none_positive_brier_dispersion": none_dispersion,
        "none_robust_positive_brier_risk": none_robust_positive,
        "image_robust_margin": image_robust_margin,
        "none_robust_margin": none_robust_margin,
        "visual_increment": visual_increment,
        "visual_semantic_loss": visual_semantic_loss,
        "triplet_success": image_robust_margin > 0.0,
        "lm_triplet_success": none_robust_margin > 0.0,
        "visual_increment_success": visual_increment > 0.0,
        "positive_metric_source": "correct_image_observed_robust_max",
        "visual_metric_source": "correct_vs_no_pixel_robust_interaction",
    }
    if raw_image_margin is not None and raw_none_margin is not None:
        result["raw_image_robust_margin"] = raw_image_margin
        result["raw_none_robust_margin"] = raw_none_margin
        result["raw_visual_increment_v5"] = raw_image_margin - raw_none_margin
    elif raw_image_margin is not None or raw_none_margin is not None:
        raise ValueError("raw image and no-pixel Brier fields must be jointly present")
    return result


def m0_row_metrics_v5(values: dict[str, float]) -> dict[str, Any]:
    """Calculate v5 language-only metrics without fabricating image fields."""

    b = {key: _finite_float(values, key) for key in _BRIER_KEYS_M0}
    robust = max(b["b_none_pos1"], b["b_none_pos2"])
    mean = (b["b_none_pos1"] + b["b_none_pos2"]) / 2.0
    dispersion = abs(b["b_none_pos1"] - b["b_none_pos2"]) / 2.0
    none_margin = b["b_none_neg"] - robust
    if abs(robust - (mean + dispersion)) > 1e-12:
        raise AssertionError("M0 max=mean+dispersion identity failed")
    nulls = {
        key: None
        for key in (
            "b_img_pos1_raw", "b_img_pos1", "b_img_pos2_raw", "b_img_pos2",
            "b_img_neg_raw", "b_img_neg", "raw_image_robust_margin",
            "image_robust_margin", "triplet_success",
        )
    }
    raw_none_margin = _optional_raw_margin(values, "none")
    return {
        **nulls,
        **values,
        "positive_brier_mean": mean,
        "positive_brier_dispersion": dispersion,
        "robust_positive_brier_risk": robust,
        "none_positive_brier_mean": mean,
        "none_positive_brier_dispersion": dispersion,
        "none_robust_positive_brier_risk": robust,
        "raw_none_robust_margin": raw_none_margin,
        "none_robust_margin": none_margin,
        "visual_increment": 0.0,
        "visual_increment_success": False,
        "visual_semantic_loss": 0.5,
        "lm_triplet_success": none_margin > 0.0,
        "positive_metric_source": "lm_only_observed_robust_max",
        "visual_metric_source": "definition_constant_lm_only",
    }


_NON_GROUP_FIELDS = {
    "schema_version", "model_id", "filename", "row_count", "row_index", "row_key",
    "category", "numeric_id", "source_row_sha256",
}


def _aggregate_members(
    members: list[dict[str, Any]], *, model_id: str, filename: str, category: str | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 1,
        "model_id": model_id,
        "filename": filename,
        "row_count": len(members),
    }
    if category is not None:
        result["category"] = category
    keys = set().union(*(member.keys() for member in members))
    for key in sorted(keys):
        if key in _NON_GROUP_FIELDS:
            continue
        values = [member.get(key) for member in members]
        null_count = sum(value is None for value in values)
        numeric = [
            value for value in values
            if isinstance(value, (int, float, np.integer, np.floating))
        ]
        if numeric and null_count:
            raise ValueError(f"partially-null field {key} in {model_id}/{filename}")
        if len(numeric) == len(values):
            array = np.asarray(numeric, dtype=np.float64)
            if not np.all(np.isfinite(array)):
                raise ValueError(f"non-finite aggregate field {key} in {model_id}/{filename}")
            result[key] = float(np.mean(array, dtype=np.float64))
        elif null_count == len(values):
            result[key] = None
        elif all(value == values[0] for value in values):
            result[key] = values[0]
        else:
            raise ValueError(f"non-aggregatable mixed field {key} in {model_id}/{filename}")
    return result


def aggregate_rows_v5(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["model_id"]), str(row["filename"]))].append(row)
    output = [
        _aggregate_members(members, model_id=model_id, filename=filename)
        for (model_id, filename), members in grouped.items()
    ]
    output.sort(key=lambda row: (row["model_id"].encode("utf-8"), row["filename"].encode("utf-8")))
    return output


def aggregate_category_rows_v5(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["model_id"]), str(row["category"]), str(row["filename"]))].append(row)
    image_groups = [
        _aggregate_members(members, model_id=model_id, category=category, filename=filename)
        for (model_id, category, filename), members in grouped.items()
    ]
    by_category: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in image_groups:
        by_category[(row["model_id"], row["category"])].append(row)
    output: list[dict[str, Any]] = []
    metrics = PRIMARY_METRICS_V5 + DIAGNOSTIC_METRICS_V5
    for (model_id, category), members in by_category.items():
        result: dict[str, Any] = {
            "schema_version": 1,
            "model_id": model_id,
            "category": category,
            "n_unique_images": len(members),
            "row_count": int(sum(int(row["row_count"]) for row in members)),
        }
        for metric in metrics:
            values = [row.get(metric) for row in members]
            if all(value is None for value in values):
                result[metric] = None
            elif any(value is None for value in values):
                raise ValueError(f"partially-null category metric {metric} in {model_id}/{category}")
            else:
                array = np.asarray(values, dtype=np.float64)
                if not np.all(np.isfinite(array)):
                    raise ValueError(f"non-finite category metric {metric}")
                result[metric] = float(np.mean(array, dtype=np.float64))
        output.append(result)
    output.sort(key=lambda row: (row["model_id"].encode("utf-8"), row["category"].encode("utf-8")))
    return output


def empirical_metric_means_v5(groups: Iterable[dict[str, Any]]) -> dict[str, float]:
    rows = list(groups)
    if not rows:
        raise ValueError("no image groups")
    output = {}
    for metric in PRIMARY_METRICS_V5:
        array = np.asarray([row[metric] for row in rows], dtype=np.float64)
        if not np.all(np.isfinite(array)):
            raise ValueError(f"non-finite primary metric: {metric}")
        output[metric] = float(np.mean(array, dtype=np.float64))
    return output
