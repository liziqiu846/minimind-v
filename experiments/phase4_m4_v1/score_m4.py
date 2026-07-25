#!/usr/bin/env python3
"""Thin M4 loader/field adapter for the unchanged frozen Phase 3 scorer."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.risk_metrics import derive_risk_row
from experiments.phase3_v6.scoring.hull_scorer import score_filename_group
from experiments.phase4_m4_v1.m4_configs import load_frozen_config
from experiments.phase4_m4_v1.m4_model import load_m4_model_from_archive
from experiments.phase4_m4_v1.mms2_v2 import decode_mms2_v2
from experiments.phase4_m4_v1.train_m4 import ARTIFACT_ROOT_ENV


def adapt_frozen_score_row(source: Mapping[str, Any]) -> dict[str, Any]:
    """Delegate all old metric arithmetic, then add naming/status metadata."""

    legacy = derive_risk_row(source)
    output = dict(legacy)
    output.update(
        {
            "joint_semantic_risk": legacy["total_semantic_risk"],
            "mismatch_baseline_risk": legacy["language_risk"],
            "visual_gain": legacy["visual_gain"],
            "language_risk_is_legacy_alias": True,
            "language_risk_legacy_alias_of": "mismatch_baseline_risk",
            "language_risk_interpretation": (
                "legacy compatibility alias; not a pure language-only risk"
            ),
            "certified": False,
            "exploratory": True,
            "u_statistic_implemented": False,
        }
    )
    return output


def adapt_frozen_score_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("M4 score adaptation requires at least one row")
    output = [adapt_frozen_score_row(row) for row in rows]
    identifiers = [row.get("sample_id") for row in output]
    if (
        any(not isinstance(value, str) or not value for value in identifiers)
        or len(identifiers) != len(set(identifiers))
    ):
        raise ValueError("M4 score rows have missing or duplicate sample IDs")
    return output


def summarize_adapted_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_image_count: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Reuse the frozen image-equal aggregator and expose preferred names."""

    image_rows, legacy_summary = summarize_model(
        rows, expected_image_count=expected_image_count
    )
    empirical = legacy_summary["empirical_risks"]
    summary = dict(legacy_summary)
    summary.update(
        {
            "joint_semantic_risk": empirical["total_semantic_risk"],
            "mismatch_baseline_risk": empirical["language_risk"],
            "visual_gain": empirical["visual_gain"],
            "language_risk_is_legacy_alias": True,
            "certified": False,
            "exploratory": True,
            "u_statistic_implemented": False,
            "scorer_modified": False,
            "teacher_forcing_modified": False,
            "mismatch_k": 5,
            "aggregation_modified": False,
        }
    )
    return image_rows, summary


def score_filename_group_m4(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    """Call the frozen hull scorer with M4 treated as the existing VLM mode."""

    if "model_method" in kwargs:
        raise ValueError("M4 scorer adapter fixes model_method internally")
    return score_filename_group(*args, model_method="M4", **kwargs)


def load_for_frozen_scorer(
    archive: bytes,
    *,
    device: str = "cpu",
    verify_assets: bool = True,
):
    model, metadata = load_m4_model_from_archive(
        archive,
        device=device,
        verify_assets=verify_assets,
    )
    return model, {
        "model_method_for_frozen_scorer": "M4",
        "template_mode": "vlm",
        "archive": metadata,
        "scorer_modified": False,
        "teacher_forcing_modified": False,
        "mismatch_k": 5,
        "certified": False,
        "exploratory": True,
    }


def inspect_config_adapter(config_id: str) -> dict[str, Any]:
    """Readiness check only; it deliberately does not execute full scoring."""

    config, receipt = load_frozen_config(config_id)
    root_value = os.environ.get(ARTIFACT_ROOT_ENV, "").strip()
    if not root_value:
        raise ValueError(
            f"{ARTIFACT_ROOT_ENV} must identify the immutable runtime root"
        )
    archive_path = (
        Path(root_value).resolve()
        / config["output_relative_path"]
        / "encode/adapter.mms2"
    )
    _, metadata = decode_mms2_v2(archive_path.read_bytes())
    if metadata["config_id"] != config_id:
        raise ValueError("M4 archive config ID differs from selected config")
    return {
        "status": "adapter_ready",
        "config_id": config_id,
        "config": receipt,
        "archive_path": str(archive_path),
        "scorer_modified": False,
        "teacher_forcing_modified": False,
        "mismatch_k": 5,
        "image_equal_aggregation_modified": False,
        "full_scoring_executed": False,
        "certified": False,
        "exploratory": True,
        "u_statistic_implemented": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = inspect_config_adapter(args.config_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
