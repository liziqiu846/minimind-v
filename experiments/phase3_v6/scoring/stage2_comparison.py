"""Descriptive correspondence between frozen Stage 2 and Phase 3 v6."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from experiments.phase3_v6.scoring.common import read_json, sha256_file
from experiments.phase3_v6.scoring.input_validation import EXPECTED_MODEL_IDS


def _average_ranks(values: Sequence[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: (item[1], item[0]))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average = ((index + 1) + end) / 2.0
        for position in range(index, end):
            ranks[ordered[position][0]] = average
        index = end
    return ranks


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("correlation vectors have invalid lengths")
    left_mean = math.fsum(left) / len(left)
    right_mean = math.fsum(right) / len(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    denominator = math.sqrt(
        math.fsum(value * value for value in left_centered)
        * math.fsum(value * value for value in right_centered)
    )
    if denominator == 0.0:
        return None
    result = math.fsum(
        x_value * y_value
        for x_value, y_value in zip(left_centered, right_centered)
    ) / denominator
    return max(-1.0, min(1.0, result))


def descriptive_correlations(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    metrics = (
        "stage2_empirical_risk_bits",
        "stage2_code_length_bits",
        "stage2_generalization_upper_bound_bits",
    )
    output: dict[str, Any] = {
        "model_count": len(rows),
        "label": "descriptive_only",
        "p_values_reported": False,
        "confidence_intervals_reported": False,
        "raw_variable_direction": {
            "stage2_empirical_risk_bits": "smaller_is_better",
            "stage2_code_length_bits": "smaller_is_better",
            "stage2_generalization_upper_bound_bits": "smaller_is_better",
            "v6_mu_k5": "larger_is_better",
            "variables_sign_flipped": False,
        },
        "metrics": {},
    }
    gains = [float(row["v6_mu_k5"]) for row in rows]
    for metric in metrics:
        values = [float(row[metric]) for row in rows]
        output["metrics"][metric] = {
            "pearson": _pearson(values, gains),
            "spearman": _pearson(
                _average_ranks(values), _average_ranks(gains)
            ),
        }
    return output


def _stage2_bound_path(
    artifact_root: str | Path, model_row: Mapping[str, Any]
) -> Path:
    adapter = Path(artifact_root) / str(model_row["artifact_relative_path"])
    if adapter.name != "adapter.mms2" or adapter.parent.name != "encode":
        raise ValueError("unexpected Stage2 adapter relative path")
    return adapter.parent.parent / "bound.json"


def load_stage2_metrics(
    artifact_root: str | Path,
    registry_models: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    output = []
    for model in registry_models:
        path = _stage2_bound_path(artifact_root, model)
        if not path.is_file():
            raise FileNotFoundError(f"frozen Stage2 bound is absent: {path}")
        value = read_json(path)
        if value.get("formal") is not True:
            raise ValueError(f"Stage2 bound is not formal: {path}")
        if value.get("model_group") != model["method"]:
            raise ValueError(f"Stage2 bound model group mismatch: {path}")
        if value.get("mapping_root") != model["mapping_root"]:
            raise ValueError(f"Stage2 bound mapping root mismatch: {path}")
        if (
            value.get("protocol", {}).get("protocol_sha256")
            != "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
        ):
            raise ValueError(f"Stage2 bound protocol mismatch: {path}")
        metrics = {
            "model_id": model["model_id"],
            "method": model["method"],
            "mapping_root": model["mapping_root"],
            "stage2_bound_path": str(path.resolve()),
            "stage2_bound_sha256": sha256_file(path),
            "stage2_empirical_risk_bits": float(
                value["risk"]["decoded_training_bits"]
            ),
            "stage2_code_length_bits": int(
                value["complexity"]["adapter_bits"]
            ),
            "stage2_generalization_upper_bound_bits": float(
                value["bound"]["raw_compression_upper_bound_bits"]
            ),
            "stage2_metric_field_mapping": {
                "empirical_risk": "risk.decoded_training_bits",
                "code_length": "complexity.adapter_bits",
                "generalization_upper_bound": (
                    "bound.raw_compression_upper_bound_bits"
                ),
            },
        }
        if metrics["stage2_code_length_bits"] != int(
            model["description_bits"]
        ):
            raise ValueError(
                f"Stage2 code length/registry mismatch for {model['model_id']}"
            )
        if not all(
            math.isfinite(value)
            for value in (
                metrics["stage2_empirical_risk_bits"],
                metrics["stage2_generalization_upper_bound_bits"],
            )
        ):
            raise FloatingPointError("Stage2 metric is non-finite")
        output.append(metrics)
    if [row["model_id"] for row in output] != EXPECTED_MODEL_IDS:
        raise ValueError("Stage2 metric order differs from frozen model order")
    return output


def build_stage2_stage3_comparison(
    artifact_root: str | Path,
    registry_models: Sequence[Mapping[str, Any]],
    model_summaries: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    stage2 = load_stage2_metrics(artifact_root, registry_models)
    rows = []
    for source in stage2:
        model_id = source["model_id"]
        if model_id not in model_summaries:
            raise ValueError(f"missing v6 summary for {model_id}")
        summary = model_summaries[model_id]
        rows.append(
            {
                **source,
                "v6_mu_k1": float(summary["mu_k1"]),
                "v6_mu_k3": float(summary["mu_k3"]),
                "v6_mu_k5": float(summary["mu_k5"]),
                "v6_win_rate_k5": float(summary["win_rate_k5"]),
            }
        )
    all_models = descriptive_correlations(rows)
    non_m0_rows = [row for row in rows if row["method"] != "M0"]
    non_m0 = descriptive_correlations(non_m0_rows)
    by_identity = {
        (row["method"], row["mapping_root"]): row for row in rows
    }
    paired = []
    for root in (43101, 43102, 43103):
        m2 = by_identity[("M2", root)]
        m3 = by_identity[("M3", root)]
        paired.append(
            {
                "mapping_root": root,
                "difference_direction": "M3_minus_M2",
                "stage2_generalization_upper_bound_difference": (
                    m3["stage2_generalization_upper_bound_bits"]
                    - m2["stage2_generalization_upper_bound_bits"]
                ),
                "stage2_code_length_difference_bits": (
                    m3["stage2_code_length_bits"]
                    - m2["stage2_code_length_bits"]
                ),
                "v6_visual_gain_mu_k5_difference": (
                    m3["v6_mu_k5"] - m2["v6_mu_k5"]
                ),
                "directional_reference_only": {
                    "smaller_stage2_bound": (
                        "negative generalization-bound difference"
                    ),
                    "larger_v6_visual_gain": (
                        "positive mu_k5 difference"
                    ),
                    "used_as_success_threshold": False,
                },
            }
        )
    m0_rows = [row for row in rows if row["method"] == "M0"]
    return {
        "schema_version": 1,
        "analysis_label": "descriptive_only",
        "strong_generalization_claim": False,
        "models": rows,
        "scatter_data": [
            {
                "model_id": row["model_id"],
                "method": row["method"],
                "mapping_root": row["mapping_root"],
                "stage2_generalization_upper_bound_bits": row[
                    "stage2_generalization_upper_bound_bits"
                ],
                "v6_visual_gain_mu_k5": row["v6_mu_k5"],
            }
            for row in rows
        ],
        "all_ten_models_correlations": all_models,
        "seven_non_m0_models_sensitivity_correlations": {
            **non_m0,
            "analysis_label": "auxiliary_non_m0_sensitivity_descriptive_only",
        },
        "same_root_M2_M3_paired_differences": paired,
        "m0_zero_gain_check": {
            "model_count": len(m0_rows),
            "maximum_abs_mu_k5": max(
                abs(float(row["v6_mu_k5"])) for row in m0_rows
            ),
            "tolerance": 1e-8,
            "passes": all(
                abs(float(row["v6_mu_k5"])) <= 1e-8 for row in m0_rows
            ),
        },
    }

