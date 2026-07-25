import math

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.risk_metrics import derive_risk_row
from experiments.phase4_m4_v1.score_m4 import (
    adapt_frozen_score_row,
    adapt_frozen_score_rows,
    summarize_adapted_rows,
)


def _golden(sample_id, filename, q_correct, mismatch):
    mean = math.fsum(mismatch) / 5.0
    return {
        "sample_id": sample_id,
        "filename": filename,
        "negative_type": "replace_object",
        "model_id": "M4-shared-1024-root-43101",
        "method": "M4",
        "q_correct": q_correct,
        **{
            f"q_mismatch_round_{index}": value
            for index, value in enumerate(mismatch, start=1)
        },
        "q_mismatch_k5": mean,
    }


def test_fixed_golden_input_preserves_all_frozen_risk_outputs():
    source = _golden(
        "golden:1",
        "image-a.jpg",
        0.72,
        [0.40, 0.45, 0.50, 0.55, 0.60],
    )
    frozen = derive_risk_row(source)
    adapted = adapt_frozen_score_row(source)
    for key, value in frozen.items():
        assert adapted[key] == value
    assert adapted["joint_semantic_risk"] == frozen["total_semantic_risk"]
    assert adapted["mismatch_baseline_risk"] == frozen["language_risk"]
    assert adapted["visual_gain"] == frozen["visual_gain"]
    assert adapted["language_risk_is_legacy_alias"] is True
    assert adapted["certified"] is False
    assert adapted["exploratory"] is True
    assert adapted["u_statistic_implemented"] is False


def test_image_equal_aggregation_is_delegated_without_rule_change():
    sources = [
        _golden(
            "golden:1",
            "image-a.jpg",
            0.72,
            [0.40, 0.45, 0.50, 0.55, 0.60],
        ),
        _golden(
            "golden:2",
            "image-a.jpg",
            0.62,
            [0.35, 0.40, 0.45, 0.50, 0.55],
        ),
        _golden(
            "golden:3",
            "image-b.jpg",
            0.82,
            [0.50, 0.55, 0.60, 0.65, 0.70],
        ),
    ]
    adapted = adapt_frozen_score_rows(sources)
    frozen_images, frozen_summary = summarize_model(adapted)
    image_rows, summary = summarize_adapted_rows(adapted)
    assert image_rows == frozen_images
    for key, value in frozen_summary.items():
        assert summary[key] == value
    assert summary["joint_semantic_risk"] == frozen_summary[
        "empirical_risks"
    ]["total_semantic_risk"]
    assert summary["mismatch_k"] == 5
    assert summary["teacher_forcing_modified"] is False
    assert summary["aggregation_modified"] is False
