from __future__ import annotations

from functools import lru_cache

from transformers import AutoTokenizer

from experiments.phase3.stage2_adapter_loader import (
    verify_stage2_source_integrity,
)
from experiments.phase3_v6.scoring.candidate_builder import (
    prevalidate_candidates,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_ASSIGNMENT_CORE_SHA256,
    EXPECTED_MODEL_IDS,
    load_and_validate_frozen_inputs,
    verify_stage2_artifacts,
)


ARTIFACT_ROOT = "/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721"


@lru_cache(maxsize=1)
def _data():
    return load_and_validate_frozen_inputs()


@lru_cache(maxsize=1)
def _pairs():
    protocol = verify_stage2_source_integrity(
        "experiments/stage2_protocol_v2.json"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )
    return prevalidate_candidates(tokenizer, _data()["valid_rows"])


def test_frozen_input_hashes_assignment_and_expected_counts():
    data = _data()
    assert data["assignment_core_sha256"] == EXPECTED_ASSIGNMENT_CORE_SHA256
    assert data["valid_record_count"] == 4107
    assert data["valid_image_count"] == 1343
    assert data["mismatch_image_count"] == 1345
    assert data["local_hull_record_count"] == 3675
    assert data["local_hull_image_count"] == 1166


def test_donor_round_order_is_frozen_one_through_five():
    for row in _data()["mismatch_rows"]:
        assert [entry["round_id"] for entry in row["donor_rounds"]] == [
            1,
            2,
            3,
            4,
            5,
        ]


def test_checkpoint_hashes_and_model_registry_match_v5():
    rows = verify_stage2_artifacts(ARTIFACT_ROOT)
    assert [row["model_id"] for row in rows] == EXPECTED_MODEL_IDS
    assert len(rows) == 10


def test_all_4107_original_candidates_and_masks_prevalidate():
    pairs = _pairs()
    assert len(pairs) == 4107
    assert len({pair.filename for pair in pairs}) == 1343
    assert all(pair.common_prefix is not None for pair in pairs)
    assert all(
        pair.templates["vlm"]["positive"].target_token_ids for pair in pairs
    )
    assert all(
        pair.templates["vlm"]["negative"].target_token_ids for pair in pairs
    )
    assert all(
        pair.templates["vlm"]["positive"].input_ids[
            : pair.templates["vlm"]["positive"].target_positions[0]
        ]
        == pair.templates["vlm"]["negative"].input_ids[
            : pair.templates["vlm"]["negative"].target_positions[0]
        ]
        for pair in pairs
    )


def test_empty_prefix_single_token_multi_token_and_different_lengths_exist():
    pairs = _pairs()
    assert any(pair.common_prefix == "" for pair in pairs)
    positive_counts = [
        len(pair.templates["vlm"]["positive"].target_token_ids)
        for pair in pairs
    ]
    negative_counts = [
        len(pair.templates["vlm"]["negative"].target_token_ids)
        for pair in pairs
    ]
    assert 1 in positive_counts
    assert max(positive_counts) > 1
    assert any(
        positive != negative
        for positive, negative in zip(positive_counts, negative_counts)
    )


def test_stitch_seam_uses_each_original_boundary_separator():
    pairs = _pairs()
    changed = [
        pair
        for pair in pairs
        if pair.evidence["positive_boundary_expansion_original"]
        != pair.evidence["negative_boundary_expansion_original"]
    ]
    assert len(changed) == 8
    target = next(
        pair for pair in pairs if pair.sample_id == "replace_object:1078"
    )
    assert target.positive_candidate_text.endswith("pizza, and salad")
    assert target.negative_candidate_text.endswith("pizza and a burger")
    assert "pizzaand" not in target.negative_candidate_text


def test_local_hull_is_maximum_of_positive_and_negative_coverage():
    for row in _data()["valid_rows"]:
        assert row["maximum_hull_token_coverage"] == max(
            row["positive_hull_token_coverage"],
            row["negative_hull_token_coverage"],
        )

