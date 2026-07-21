"""Row metric definitions and equal-weight image-group aggregation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np


MAIN_METRICS = (
    "positive_brier_risk",
    "visual_semantic_loss",
    "positive_invariance_loss",
)


def visual_row_metrics(values: dict[str, float]) -> dict[str, Any]:
    image_average = (values["b_img_pos1"] + values["b_img_pos2"]) / 2.0
    none_average = (values["b_none_pos1"] + values["b_none_pos2"]) / 2.0
    image_margin = values["b_img_neg"] - image_average
    none_margin = values["b_none_neg"] - none_average
    increment = image_margin - none_margin
    return {
        **values,
        "b_img_pos_avg": image_average,
        "b_none_pos_avg": none_average,
        "image_margin": image_margin,
        "none_margin": none_margin,
        "visual_increment": increment,
        "positive_brier_risk": image_average,
        "visual_semantic_loss": (4.0 - increment) / 8.0,
        "positive_invariance_loss": abs(values["b_img_pos1"] - values["b_img_pos2"]) / 2.0,
        "triplet_success": int(values["b_img_neg"] > max(values["b_img_pos1"], values["b_img_pos2"])),
        "lm_triplet_success": None,
        "visual_increment_success": int(increment > 0.0),
        "positive_metric_source": "correct_image_observed",
        "visual_metric_source": "correct_vs_no_pixel_observed",
    }


def m0_row_metrics(values: dict[str, float]) -> dict[str, Any]:
    average = (values["b_none_pos1"] + values["b_none_pos2"]) / 2.0
    none_margin = values["b_none_neg"] - average
    nulls = {
        key: None
        for key in (
            "b_img_pos1_raw", "b_img_pos1", "b_img_pos2_raw", "b_img_pos2",
            "b_img_neg_raw", "b_img_neg", "b_img_pos_avg", "raw_image_margin",
            "image_margin", "raw_visual_increment", "triplet_success",
            "visual_increment_success",
        )
    }
    return {
        **nulls,
        **values,
        "b_none_pos_avg": average,
        "none_margin": none_margin,
        "visual_increment": 0.0,
        "positive_brier_risk": average,
        "visual_semantic_loss": 0.5,
        "positive_invariance_loss": abs(values["b_none_pos1"] - values["b_none_pos2"]) / 2.0,
        "lm_triplet_success": int(values["b_none_neg"] > max(values["b_none_pos1"], values["b_none_pos2"])),
        "positive_metric_source": "lm_only_observed",
        "visual_metric_source": "definition_constant_lm_only",
    }


def aggregate_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["model_id"]), str(row["filename"]))].append(row)
    output = []
    for (model_id, filename), members in grouped.items():
        result: dict[str, Any] = {
            "schema_version": 1,
            "model_id": model_id,
            "filename": filename,
            "row_count": len(members),
        }
        keys = set().union(*(member.keys() for member in members))
        non_group_fields = {
            "schema_version", "model_id", "filename", "row_count", "row_index", "row_key",
            "category", "numeric_id", "source_row_sha256",
        }
        for key in sorted(keys):
            if key in non_group_fields:
                continue
            values = [member.get(key) for member in members]
            numeric = [value for value in values if isinstance(value, (int, float))]
            null_count = sum(value is None for value in values)
            if numeric and null_count:
                raise ValueError(f"partially-null field {key} in {model_id}/{filename}")
            if len(numeric) == len(values):
                result[key] = float(np.mean(np.asarray(numeric, dtype=np.float64)))
            elif null_count == len(values):
                result[key] = None
            elif all(value == values[0] for value in values):
                result[key] = values[0]
            else:
                raise ValueError(f"non-aggregatable mixed field {key} in {model_id}/{filename}")
        output.append(result)
    output.sort(key=lambda row: (row["model_id"].encode("utf-8"), row["filename"].encode("utf-8")))
    return output


def empirical_metric_means(groups: Iterable[dict[str, Any]]) -> dict[str, float]:
    rows = list(groups)
    if not rows:
        raise ValueError("no image groups")
    return {
        metric: float(np.mean(np.asarray([row[metric] for row in rows], dtype=np.float64)))
        for metric in MAIN_METRICS
    }
