from __future__ import annotations

import math
from pathlib import Path

import torch

from experiments.diagnose_phase3_shared_gradient_conflict import (
    complexity_conflict_report,
    decode_mms2,
    evaluate_criteria,
    gradient_metrics,
    sign_prediction_report,
    summarize_batch_metrics,
)
from experiments.phase3_private_vs_shared_v1.codec import encode_coordinates


def test_gradient_metrics_use_one_common_coordinate_system() -> None:
    gradients = {
        "vision": torch.tensor([1.0, 0.0]),
        "projector": torch.tensor([0.0, 1.0]),
        "language": torch.tensor([-1.0, 0.0]),
    }
    result = gradient_metrics(gradients, epsilon=0.0)
    mean = torch.tensor([0.0, 1.0 / 3.0], dtype=torch.float64)
    expected_d = sum(
        torch.dot(value.double() - mean, value.double() - mean).item()
        for value in gradients.values()
    )
    assert math.isclose(result["D"], expected_d, rel_tol=0.0, abs_tol=1e-14)
    assert math.isclose(
        result["D_norm"], expected_d / 3.0, rel_tol=0.0, abs_tol=1e-15
    )
    assert result["dot_vision_projector"] == 0.0
    assert result["dot_vision_language"] == -1.0
    assert result["dot_projector_language"] == 0.0
    assert result["cos_vision_language"] == -1.0


def test_conflict_metrics_match_registered_squared_l2_formula() -> None:
    gradients = {
        "vision": torch.tensor([3.0, 0.0]),
        "projector": torch.tensor([0.0, 4.0]),
        "language": torch.tensor([-1.0, 0.0]),
    }
    result = gradient_metrics(gradients, epsilon=0.0)
    expected_d = 58.0 / 3.0
    expected_denominator = 3.0**2 + 4.0**2 + 1.0**2
    assert math.isclose(result["D"], expected_d, rel_tol=0.0, abs_tol=1e-14)
    assert math.isclose(
        result["D_norm"],
        expected_d / expected_denominator,
        rel_tol=0.0,
        abs_tol=1e-14,
    )


def test_batch_summary_reports_sample_standard_deviation() -> None:
    summary = summarize_batch_metrics([{"D": 1.0}, {"D": 3.0}, {"D": 5.0}])
    assert summary["D_mean"] == 3.0
    assert summary["D_batch_sd"] == 2.0


def test_mms2_decoder_round_trips_frozen_format(tmp_path: Path) -> None:
    values = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
    archive, _ = encode_coordinates({"shared": values}, "S", 43101)
    path = tmp_path / "adapter.mms2"
    path.write_bytes(archive)
    decoded = decode_mms2(
        path,
        {
            "structure": "S",
            "seed": 43101,
            "coordinate_dimensions": {"shared": values.numel()},
        },
    )
    assert tuple(decoded) == ("shared",)
    reencoded, _ = encode_coordinates(decoded, "S", 43101)
    assert reencoded == archive


def _synthetic_rows() -> list[dict]:
    return [
        {
            "budget": 2048 if index < 3 else 4096 if index < 6 else 8192,
            "S_config_id": f"S-{index}",
            "D": float(index + 1),
            "D_norm": float(index + 1) / 10.0,
            "G_C": float(index + 1),
            "delta_R": -1.0 if index < 5 else 1.0,
        }
        for index in range(9)
    ]


def test_sign_and_conjunction_rules_are_outcome_independent_thresholds() -> None:
    rows = _synthetic_rows()
    sign = sign_prediction_report(rows, "D")
    conjunction = complexity_conflict_report(rows, "D")
    assert sign["global_median_descriptive_split"]["median"] == 5.0
    assert sign["global_median_descriptive_split"]["S_loss_rate_high"] == 1.0
    assert sign["global_median_descriptive_split"]["S_loss_rate_low"] == 0.0
    assert conjunction["high_high_count"] == 4
    assert conjunction["paradox_rate_high_G_C_and_high_conflict"] == 1.0


def test_scientific_criteria_require_both_conflict_metrics() -> None:
    correlations = {
        metric: {
            "pearson_r": 0.5,
            "spearman_rho": 0.5,
            "budget_residualized_pearson_r": 0.4,
            "budget_residualized_spearman_rho": 0.4,
            "leave_one_budget_out": {
                str(budget): {"pearson_r": 0.2, "spearman_rho": 0.2}
                for budget in (2048, 4096, 8192)
            },
        }
        for metric in ("D", "D_norm")
    }
    sign_predictions = {
        metric: {
            "global_median_descriptive_split": {
                "S_loss_rate_high": 0.75,
                "S_loss_rate_low": 0.2,
            },
            "prediction": {"accuracy": 0.7},
            "leave_one_out_majority_baseline": {"accuracy": 0.6},
        }
        for metric in ("D", "D_norm")
    }
    conjunctions = {
        metric: {
            "high_high_count": 2,
            "paradox_rate_high_G_C_and_high_conflict": 1.0,
            "paradox_rate_other_pairs": 0.2,
        }
        for metric in ("D", "D_norm")
    }
    result = evaluate_criteria(correlations, sign_predictions, conjunctions)
    assert result["all_three_pass"] is True
    correlations["D_norm"]["spearman_rho"] = -0.1
    result = evaluate_criteria(correlations, sign_predictions, conjunctions)
    assert result["criterion_1_stable_positive_prediction_of_delta_R"]["pass"] is False
    assert result["all_three_pass"] is False
