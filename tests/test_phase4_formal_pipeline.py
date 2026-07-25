from __future__ import annotations

import math

import pytest
import torch

from experiments.phase4_formal_v1 import (
    FORMAL_CANDIDATE_ID,
    FORMAL_CONFIG_ID,
)
from experiments.phase4_formal_v1.codec_integration import (
    BLOCK_NAME_MAP,
    verify_codecs_from_coordinates,
)
from experiments.phase4_formal_v1.run_formal_m4 import (
    _require_config,
    _synthetic_coordinates,
    build_parser,
)
from experiments.phase4_formal_v1.runtime_gate import (
    verify_formal_config,
    verify_protocol_freeze,
    verify_zlib_runtime,
)
from experiments.phase4_formal_v1.score_formal_m4 import (
    _preferred_metrics,
)
from experiments.phase4_m4_v1.m4_configs import load_frozen_config
from experiments.phase4_m4_v1.score_m4 import (
    adapt_frozen_score_rows,
    summarize_adapted_rows,
)


def _golden(sample_id, filename, q_correct, mismatch):
    return {
        "sample_id": sample_id,
        "filename": filename,
        "negative_type": "replace_object",
        "model_id": FORMAL_CONFIG_ID,
        "method": "M4",
        "q_correct": q_correct,
        **{
            f"q_mismatch_round_{index}": value
            for index, value in enumerate(mismatch, start=1)
        },
        "q_mismatch_k5": math.fsum(mismatch) / 5.0,
    }


def test_formal_candidate_and_freeze_identity_are_exact():
    config, config_receipt = verify_formal_config()
    freeze = verify_protocol_freeze()
    assert config["config_id"] == FORMAL_CONFIG_ID
    assert config["shared_budget"] == 2048
    assert config["mapping_root"] == 43101
    assert config_receipt["candidate_id"] == FORMAL_CANDIDATE_ID
    assert freeze["candidate_id"] == FORMAL_CANDIDATE_ID
    assert len(freeze["complexity_protocol_sha256"]) == 64
    assert len(freeze["candidate_manifest_sha256"]) == 64
    assert len(freeze["freeze_manifest_sha256"]) == 64
    assert verify_zlib_runtime()["runtime_version"] == "1.3.1"


def test_same_quantized_state_drives_both_codecs_and_paid_sum_is_exact():
    config, _ = load_frozen_config(FORMAL_CONFIG_ID)
    coordinates = _synthetic_coordinates(config)
    result = verify_codecs_from_coordinates(coordinates, config)
    receipt = result.complexity_receipt
    assert receipt["candidate_id"] == FORMAL_CANDIDATE_ID
    assert receipt["candidate_id_bits"] == 4
    assert receipt["paid_fields_sum_exact"] is True
    assert (
        receipt["candidate_id_bits"]
        + receipt["framing_bits"]
        + sum(receipt["block_scale_bits"].values())
        + sum(receipt["block_compressed_symbol_bits"].values())
        == receipt["conditional_message_bits"]
    )
    assert receipt["conditional_message_bits"] == len(
        result.conditional_message
    ) * 8
    assert receipt["full_archive_bits"] == len(result.archive) * 8
    assert FORMAL_CONFIG_ID.encode() not in result.conditional_message
    assert set(result.archive_coordinates) == set(BLOCK_NAME_MAP.values())
    assert all(
        torch.equal(
            result.archive_coordinates[name],
            result.conditional_coordinates[name],
        )
        for name in result.archive_coordinates
    )


def test_formal_cli_exposes_no_scientific_runtime_overrides():
    parser = build_parser()
    parsed = parser.parse_args(
        ["preflight", "--config-id", FORMAL_CONFIG_ID]
    )
    assert parsed.config_id == FORMAL_CONFIG_ID
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "run",
                "--config-id",
                FORMAL_CONFIG_ID,
                "--learning-rate",
                "0.1",
            ]
        )
    _require_config(FORMAL_CONFIG_ID)
    with pytest.raises(ValueError):
        _require_config("M4-shared-1024-root-43101")


def test_preferred_scoring_fields_are_exact_frozen_aliases():
    rows = adapt_frozen_score_rows(
        [
            _golden(
                "golden:1",
                "image-a.jpg",
                0.72,
                [0.40, 0.45, 0.50, 0.55, 0.60],
            ),
            _golden(
                "golden:2",
                "image-b.jpg",
                0.82,
                [0.50, 0.55, 0.60, 0.65, 0.70],
            ),
        ]
    )
    _, summary = summarize_adapted_rows(rows, expected_image_count=2)
    preferred = _preferred_metrics(summary)
    assert preferred["joint_semantic_risk"] == pytest.approx(summary[
        "joint_semantic_risk"
    ], abs=1e-15)
    assert preferred["mismatch_baseline_risk"] == pytest.approx(summary[
        "mismatch_baseline_risk"
    ], abs=1e-15)
    assert preferred["visual_gain"] == pytest.approx(
        summary["visual_gain"], abs=1e-15
    )
    assert preferred["joint_semantic_risk"] == 1.0 - preferred["q_correct"]
    assert preferred["mismatch_baseline_risk"] == (
        1.0 - preferred["q_mismatch_mean"]
    )
    assert preferred["visual_gain"] == (
        preferred["q_correct"] - preferred["q_mismatch_mean"]
    )
