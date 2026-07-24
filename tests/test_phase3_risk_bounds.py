import math

import pytest

from experiments.phase3_risk_v1.exploratory_bounds import (
    CURRENT_INVALID_REASONS,
    analyze_model_summaries,
    exploratory_upper,
)


def summary(model_id="M2-root-43101"):
    return {
        "model_id": model_id,
        "method": model_id.split("-", 1)[0],
        "image_count": 100,
        "empirical_risks": {
            "language_risk": 0.2,
            "visual_risk": 0.4,
            "total_semantic_risk": 0.0,
            "visual_gain": 0.2,
        },
    }


def test_exploratory_radius_matches_hand_calculation():
    result = exploratory_upper(0.25, 20, 0.01)
    expected = math.sqrt(math.log(100.0) / 40.0)
    assert result["exploratory_radius"] == pytest.approx(expected)
    assert result["exploratory_upper_bound_raw"] == pytest.approx(
        0.25 + expected
    )


def test_current_analysis_is_never_certified():
    result = analyze_model_summaries(
        [summary()],
        candidate_family_size=1,
        analysis_mode="current_coupled_post_hoc",
    )
    assert result["certified"] is False
    assert result["invalid_for_formal_certification_reasons"] == (
        CURRENT_INVALID_REASONS
    )
    model = result["models"][0]
    assert model["certified"] is False
    assert (
        model["visual_risk"]["formally_certified_below_0_5"] is False
    )
    assert model["visual_gain"]["support_min"] == -1.0
    assert model["visual_gain"]["support_max"] == 1.0


def test_future_mode_requires_all_independence_and_predeclaration_gates():
    result = analyze_model_summaries(
        [summary()],
        candidate_family_size=1,
        analysis_mode="fresh_confirmation_independent_donor_bank",
        metrics_predeclared=True,
        fresh_confirmation_set=True,
        independent_frozen_donor_bank=True,
    )
    assert result["certified"] is True
    assert result["invalid_for_formal_certification_reasons"] == []


def test_candidate_family_size_cannot_shrink_to_available_subset():
    with pytest.raises(ValueError, match="predeclared model family"):
        analyze_model_summaries(
            [summary()],
            candidate_family_size=2,
            analysis_mode="current_coupled_post_hoc",
        )
