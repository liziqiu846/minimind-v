from __future__ import annotations

import math

import pytest
import torch

from experiments.phase3_v6.scoring.aggregations import (
    _category_summary,
    aggregate_image_rows,
    m0_invariant,
)
from experiments.phase3_v6.scoring.candidate_builder import CandidatePair
from experiments.phase3_v6.scoring.common import stable_sigmoid
from experiments.phase3_v6.scoring.hull_scorer import (
    _record_from_scores,
    mean_target_logprob,
)


def test_only_hull_tokens_are_scored_and_causal_shift_is_exact():
    logits = torch.zeros((1, 6, 5), dtype=torch.float32)
    labels = torch.full((1, 6), -100, dtype=torch.long)
    labels[0, 2] = 3
    labels[0, 3] = 1
    logits[0, 1, 3] = 2.0
    logits[0, 2, 1] = 1.0
    means, counts = mean_target_logprob(logits, labels)
    expected = (
        torch.log_softmax(logits[0, 1], dim=-1)[3].double()
        + torch.log_softmax(logits[0, 2], dim=-1)[1].double()
    ) / 2
    assert counts == [2]
    assert means[0] == pytest.approx(expected.item(), abs=0.0)

    changed = logits.clone()
    changed[0, 0, :] = torch.tensor([100, -100, 50, -50, 20])
    changed[0, 4, :] = torch.tensor([-100, 100, 50, -50, 20])
    changed_means, _ = mean_target_logprob(changed, labels)
    assert changed_means == means


def test_single_and_multi_token_targets_and_different_lengths():
    logits = torch.zeros((2, 5, 4), dtype=torch.float32)
    labels = torch.full((2, 5), -100, dtype=torch.long)
    labels[0, 2] = 1
    labels[1, 1:4] = torch.tensor([1, 2, 3])
    means, counts = mean_target_logprob(logits, labels)
    expected = (
        torch.log_softmax(torch.zeros(4, dtype=torch.float32), dim=0)[0]
        .double()
        .item()
    )
    assert counts == [1, 3]
    assert means == pytest.approx([expected, expected], abs=0.0)


@pytest.mark.parametrize("value", [-1e6, -1000.0, -1.0, 0.0, 1.0, 1000.0, 1e6])
def test_stable_sigmoid_is_finite_and_bounded(value):
    result = stable_sigmoid(value)
    assert math.isfinite(result)
    assert 0.0 <= result <= 1.0
    if value == 0.0:
        assert result == 0.5


def _pair() -> CandidatePair:
    return CandidatePair(
        sample_id="sample",
        filename="image.jpg",
        negative_type="replace_attribute",
        selected_comparison_positive="positive",
        selected_comparison_positive_label="positive_1",
        second_round_category="one_block_local",
        common_prefix="",
        positive_hull="red",
        negative_hull="blue",
        positive_candidate_text="red",
        negative_candidate_text="blue",
        maximum_hull_token_coverage=0.25,
        positive_hull_token_count_audit=1,
        negative_hull_token_count_audit=1,
        templates={},
        evidence={},
        evidence_sha256="0" * 64,
    )


def test_k1_k3_k5_nested_means_and_d_range():
    context_values = [
        (-0.1, -1.1),
        (-0.2, -0.8),
        (-0.3, -0.7),
        (-0.4, -0.6),
        (-0.5, -0.5),
        (-0.6, -0.4),
    ]
    row = _record_from_scores(
        _pair(),
        ["correct", "r1", "r2", "r3", "r4", "r5"],
        context_values,
        [(1, 1)] * 6,
    )
    rounds = [row[f"q_mismatch_round_{index}"] for index in range(1, 6)]
    assert row["q_mismatch_k1"] == rounds[0]
    assert row["q_mismatch_k3"] == pytest.approx(sum(rounds[:3]) / 3)
    assert row["q_mismatch_k5"] == pytest.approx(sum(rounds) / 5)
    assert all(
        -1.0 <= row[key] <= 1.0 for key in ("d_k1", "d_k3", "d_k5")
    )


def _row(
    sample: str,
    filename: str,
    category: str,
    d: float,
) -> dict:
    return {
        "sample_id": sample,
        "filename": filename,
        "negative_type": category,
        "d_k1": d,
        "d_k3": d,
        "d_k5": d,
        "q_correct": 0.5 + d / 2,
        **{
            f"q_mismatch_round_{round_id}": 0.5 - d / 2
            for round_id in range(1, 6)
        },
    }


def test_records_do_not_give_an_image_extra_weight():
    rows = [
        _row("a", "one.jpg", "replace_attribute", 1.0),
        _row("b", "two.jpg", "replace_attribute", -1.0),
        _row("c", "two.jpg", "replace_attribute", -1.0),
        _row("d", "two.jpg", "replace_attribute", -1.0),
    ]
    images = aggregate_image_rows("model", rows)
    assert len(images) == 2
    assert sum(row["D_g_k5"] for row in images) / 2 == 0.0
    assert sum(row["d_k5"] for row in rows) / len(rows) == -0.5


def test_category_first_averages_within_image_then_across_images():
    rows = [
        _row("a", "one.jpg", "replace_attribute", 1.0),
        _row("b", "two.jpg", "replace_attribute", -1.0),
        _row("c", "two.jpg", "replace_attribute", -1.0),
        _row("d", "two.jpg", "replace_attribute", -1.0),
        _row("e", "three.jpg", "replace_object", 0.1),
        _row("f", "four.jpg", "replace_relation", 0.2),
        _row("g", "five.jpg", "swap_atribute", 0.3),
        _row("h", "six.jpg", "swap_object", 0.4),
    ]
    summary = _category_summary(rows)
    attribute = summary["replace_attribute"]
    assert attribute["record_count"] == 4
    assert attribute["image_count"] == 2
    assert attribute["mu_k5"] == 0.0


def test_m0_invariant_uses_real_scores_not_manual_zero():
    rows = [
        {
            **_row("a", "one.jpg", "replace_attribute", 0.0),
            "q_mismatch_k5": 0.5,
            "d_k5": 0.0,
        }
    ]
    images = aggregate_image_rows("M0", rows)
    result = m0_invariant(rows, images, mu_k5=0.0)
    assert result["passes_formal_1e_8_invariant"] is True
    assert result["max_record_abs_d_k5"] == 0.0


def test_non_finite_scores_fail():
    logits = torch.zeros((1, 3, 4), dtype=torch.float32)
    logits[0, 0, 0] = float("nan")
    labels = torch.tensor([[-100, 0, -100]])
    with pytest.raises(FloatingPointError):
        mean_target_logprob(logits, labels)
