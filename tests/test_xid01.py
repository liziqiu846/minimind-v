from __future__ import annotations

from types import SimpleNamespace

import torch
from PIL import Image

from experiments.analyze_xid01 import _pilot_judgment
from experiments.phase3.caption_template import MAX_SEQUENCE_LENGTH
from experiments.xid01 import (
    VISUAL_COLORS,
    add_marker,
    block_audit,
    gold_margin,
    intended_target,
    predicted_digit,
    scoring_record,
)


def test_xid01_blocks_are_matched_except_interaction_rule() -> None:
    ambiguous = block_audit("interaction-ambiguous")
    consistent = block_audit("interaction-consistent")
    for key in (
        "visual_counts",
        "key_counts",
        "target_counts",
        "key_target_counts",
    ):
        assert ambiguous[key] == consistent[key]
    assert not ambiguous["target_cell_present"]
    assert not consistent["target_cell_present"]
    assert ambiguous["xor_correct_a_through_d"] == 4
    assert consistent["xor_correct_a_through_d"] == 8


def test_xid01_marker_is_visible_and_preserves_interior() -> None:
    original = Image.new("RGB", (64, 48), (17, 23, 31))
    for visual_bit in (0, 1):
        marked = add_marker(original, visual_bit)
        assert marked.getpixel((0, 0)) == VISUAL_COLORS[visual_bit]
        assert marked.getpixel((32, 24)) == original.getpixel((32, 24))


def test_xid01_rule_and_digit_scoring_helpers() -> None:
    assert intended_target(0, "a") == 0
    assert intended_target(1, "a") == 1
    assert intended_target(0, "b") == 1
    assert intended_target(1, "b") == 0
    nll = {"0": 2.0, "1": 1.0}
    assert predicted_digit(nll) == "1"
    assert gold_margin(nll, "1") == 1.0


def test_xid01_scoring_record_masks_only_target(monkeypatch) -> None:
    tokenizer = SimpleNamespace(pad_token_id=0, eos_token_id=2)

    def fake_token_record(_tokenizer, key, candidate):
        assert key == "e"
        assert candidate == 1
        return {
            "full_token_ids": [8, 9, 52, 2],
            "assistant_target_start": 2,
            "assistant_target_end": 4,
        }

    monkeypatch.setattr("experiments.xid01.token_record", fake_token_record)
    record = scoring_record(tokenizer, "e", 1)
    assert record["input_ids"].shape == torch.Size([MAX_SEQUENCE_LENGTH])
    assert record["labels"][:4].tolist() == [-100, -100, 52, 2]
    assert record["valid_token_count"] == 2


def test_xid01_pilot_judgment_is_conjunctive() -> None:
    summary = {
        "training_pair_checks": {"paired": True},
        "target": {
            "accuracy_difference": 0.11,
            "accuracy_difference_bootstrap": {"ci95": [0.01, 0.2]},
            "consistent_accuracy": 0.70,
            "gold_margin_difference_bits_per_token": 0.1,
        },
        "mechanism": {
            "accuracy_difference": 0.06,
            "accuracy_difference_bootstrap": {"ci95": [0.01, 0.1]},
            "consistent_accuracy": 0.80,
            "full_rule_success_difference": 0.01,
        },
    }
    assert _pilot_judgment(summary)["decision"] == "PILOT_POSITIVE"
    summary["mechanism"]["accuracy_difference"] = 0.049
    assert _pilot_judgment(summary)["decision"] == "REJECT_IDEA"
