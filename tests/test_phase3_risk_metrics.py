import math

import pytest

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.risk_metrics import (
    K_MISMATCH,
    derive_risk_row,
)
from experiments.phase3_v6.scoring.common import canonical_json_bytes


def source_row(*, method="M2", q_correct=0.8, mismatch=None, sample_id="s1"):
    mismatch = mismatch or [0.4, 0.5, 0.6, 0.5, 0.5]
    mean = math.fsum(mismatch) / 5
    return {
        "sample_id": sample_id,
        "filename": "image.jpg",
        "negative_type": "replace_object",
        "model_id": f"{method}-root-43101",
        "method": method,
        "q_correct": q_correct,
        **{
            f"q_mismatch_round_{index}": value
            for index, value in enumerate(mismatch, 1)
        },
        "q_mismatch_k5": mean,
        "d_k5": q_correct - mean,
        "historical_field": "preserved",
    }


def test_risk_formulas_ranges_identity_and_historical_fields():
    row = derive_risk_row(source_row())
    assert K_MISMATCH == 5
    assert row["q_mismatch_mean"] == 0.5
    assert row["language_risk"] == 0.5
    assert row["visual_gain"] == pytest.approx(0.3)
    assert row["visual_risk"] == pytest.approx(0.35)
    assert row["total_semantic_risk"] == pytest.approx(0.2)
    assert row["identity_error"] <= 1e-6
    assert row["historical_field"] == "preserved"
    assert [row[f"q_mismatch_{index}"] for index in range(1, 6)] == [
        0.4,
        0.5,
        0.6,
        0.5,
        0.5,
    ]


def test_missing_or_inconsistent_q_fields_fail_explicitly():
    missing = source_row()
    del missing["q_mismatch_round_5"]
    with pytest.raises(ValueError, match="q_mismatch_round_5"):
        derive_risk_row(missing)
    inconsistent = source_row()
    inconsistent["q_mismatch_k5"] += 1e-4
    with pytest.raises(ValueError, match="historical q_mismatch_k5"):
        derive_risk_row(inconsistent)


def test_m0_invariant_includes_q_gain_and_half_risk():
    rows = [
        derive_risk_row(
            source_row(
                method="M0",
                q_correct=value,
                mismatch=[value] * 5,
                sample_id=f"s{index}",
            )
        )
        for index, value in enumerate((0.2, 0.8), 1)
    ]
    _, summary = summarize_model(rows, expected_image_count=1)
    invariant = summary["m0_invariant"]
    assert invariant["passes"] is True
    assert invariant["maximum_context_q_abs_difference"] == 0.0
    assert invariant["maximum_abs_visual_gain"] == 0.0
    assert invariant["maximum_abs_visual_risk_minus_half"] == 0.0


def test_probability_out_of_range_is_not_clipped():
    row = source_row()
    row["q_correct"] = 1.01
    with pytest.raises(ValueError, match="outside"):
        derive_risk_row(row)


def test_repeated_derivation_is_byte_identical():
    source = source_row()
    first = canonical_json_bytes(derive_risk_row(source))
    second = canonical_json_bytes(derive_risk_row(source))
    assert first == second
