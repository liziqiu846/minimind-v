#!/usr/bin/env python3
"""Backfill frozen v6 q-scores with decomposed risks and exploratory radii."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.exploratory_bounds import (
    ANALYSIS_MODES,
    analyze_model_summaries,
)
from experiments.phase3_risk_v1.risk_metrics import derive_risk_rows
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    read_json,
    read_jsonl,
    sha256_file,
    utf8_key,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
)


def _model_identity(model_id: str, method: str) -> dict[str, Any]:
    root_text = model_id.rsplit("-root-", 1)[-1]
    mapping_root = None if root_text == "none" else int(root_text)
    return {
        "model_id": model_id,
        "method": method,
        "mapping_root": mapping_root,
        "experiment_seed": mapping_root,
        "budget": "current" if method in ("M2", "M3") else "legacy",
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    columns = list(rows[0])
    if any(list(row) != columns for row in rows):
        raise ValueError("CSV rows do not have one stable schema")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="raise", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def _model_csv_row(
    summary: Mapping[str, Any], bound: Mapping[str, Any]
) -> dict[str, Any]:
    identity = _model_identity(
        str(summary["model_id"]), str(summary["method"])
    )
    distributions = summary["image_equal_primary_distributions"]
    return {
        **identity,
        "record_count": summary["record_count"],
        "image_count": summary["image_count"],
        "empirical_language_risk": distributions["language_risk"]["mean"],
        "language_risk_standard_deviation": distributions["language_risk"][
            "standard_deviation_population"
        ],
        "language_risk_median": distributions["language_risk"]["median"],
        "language_risk_p25": distributions["language_risk"]["p25"],
        "language_risk_p75": distributions["language_risk"]["p75"],
        "empirical_visual_risk": distributions["visual_risk"]["mean"],
        "visual_risk_standard_deviation": distributions["visual_risk"][
            "standard_deviation_population"
        ],
        "visual_risk_median": distributions["visual_risk"]["median"],
        "visual_risk_p25": distributions["visual_risk"]["p25"],
        "visual_risk_p75": distributions["visual_risk"]["p75"],
        "empirical_visual_gain": distributions["visual_gain"]["mean"],
        "empirical_total_semantic_risk": distributions[
            "total_semantic_risk"
        ]["mean"],
        "total_semantic_risk_standard_deviation": distributions[
            "total_semantic_risk"
        ]["standard_deviation_population"],
        "total_semantic_risk_median": distributions[
            "total_semantic_risk"
        ]["median"],
        "total_semantic_risk_p25": distributions["total_semantic_risk"][
            "p25"
        ],
        "total_semantic_risk_p75": distributions["total_semantic_risk"][
            "p75"
        ],
        "maximum_identity_error": summary["identity_check"][
            "maximum_error_record"
        ],
        "exploratory_language_radius": bound["language_risk"][
            "exploratory_radius"
        ],
        "exploratory_language_upper": bound["language_risk"][
            "exploratory_upper_bound_capped"
        ],
        "exploratory_visual_radius": bound["visual_risk"][
            "exploratory_radius"
        ],
        "exploratory_visual_upper": bound["visual_risk"][
            "exploratory_upper_bound_capped"
        ],
        "exploratory_visual_upper_below_0_5": bound["visual_risk"][
            "exploratory_upper_below_0_5"
        ],
        "formally_certified_visual_risk_below_0_5": bound["visual_risk"][
            "formally_certified_below_0_5"
        ],
        "certified": bound["certified"],
        "invalid_for_formal_certification_reasons": "|".join(
            bound["invalid_for_formal_certification_reasons"]
        ),
    }


def _category_csv_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    output = []
    for category in summary["category_summaries"]:
        metrics = category["metrics"]
        output.append(
            {
                "model_id": summary["model_id"],
                "method": summary["method"],
                "category": category["category"],
                "record_count": category["record_count"],
                "image_count": category["image_count"],
                "language_risk_mean": metrics["language_risk"]["mean"],
                "language_risk_standard_deviation": metrics["language_risk"][
                    "standard_deviation_population"
                ],
                "language_risk_median": metrics["language_risk"]["median"],
                "language_risk_p25": metrics["language_risk"]["p25"],
                "language_risk_p75": metrics["language_risk"]["p75"],
                "visual_risk_mean": metrics["visual_risk"]["mean"],
                "visual_risk_standard_deviation": metrics["visual_risk"][
                    "standard_deviation_population"
                ],
                "visual_risk_median": metrics["visual_risk"]["median"],
                "visual_risk_p25": metrics["visual_risk"]["p25"],
                "visual_risk_p75": metrics["visual_risk"]["p75"],
                "total_semantic_risk_mean": metrics[
                    "total_semantic_risk"
                ]["mean"],
                "total_semantic_risk_standard_deviation": metrics[
                    "total_semantic_risk"
                ]["standard_deviation_population"],
                "total_semantic_risk_median": metrics[
                    "total_semantic_risk"
                ]["median"],
                "total_semantic_risk_p25": metrics["total_semantic_risk"][
                    "p25"
                ],
                "total_semantic_risk_p75": metrics["total_semantic_risk"][
                    "p75"
                ],
                "visual_gain_mean": metrics["visual_gain"]["mean"],
            }
        )
    return output


def backfill_v6(
    input_root: Path,
    legacy_summary_root: Path,
    output_dir: Path,
    *,
    candidate_family_size: int,
    delta: float,
    analysis_mode: str,
    metrics_predeclared: bool,
    fresh_confirmation_set: bool,
    independent_frozen_donor_bank: bool,
) -> dict[str, Any]:
    source_paths = sorted(input_root.glob("*.jsonl"), key=lambda p: utf8_key(p.name))
    if len(source_paths) != candidate_family_size:
        raise ValueError(
            "input result count differs from predeclared candidate family size"
        )
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        record_root = temporary / "record_risks"
        image_root = temporary / "image_group_risks"
        model_root = temporary / "model_summaries"
        record_root.mkdir()
        image_root.mkdir()
        model_root.mkdir()
        summaries = []
        input_hashes = {}
        for source_path in source_paths:
            rows = read_jsonl(source_path)
            if len(rows) != EXPECTED_VALID_RECORD_COUNT:
                raise ValueError(
                    f"{source_path.name} has {len(rows)} records, expected "
                    f"{EXPECTED_VALID_RECORD_COUNT}"
                )
            enriched = derive_risk_rows(rows)
            image_rows, summary = summarize_model(
                enriched, expected_image_count=EXPECTED_VALID_IMAGE_COUNT
            )
            model_id = str(summary["model_id"])
            if source_path.stem != model_id:
                raise ValueError("record filename/model_id mismatch")
            legacy_path = legacy_summary_root / f"{model_id}.json"
            legacy = read_json(legacy_path)
            visual_gain_mean = summary["empirical_risks"]["visual_gain"]
            compatibility_error = abs(
                float(legacy["mu_k5"]) - float(visual_gain_mean)
            )
            if compatibility_error > 1e-15:
                raise AssertionError(
                    f"new visual_gain mean differs from v6 mu_k5 for {model_id}"
                )
            summary["legacy_v6_compatibility"] = {
                "legacy_summary_path": str(legacy_path),
                "legacy_mu_k5": legacy["mu_k5"],
                "visual_gain_mean": visual_gain_mean,
                "absolute_error": compatibility_error,
                "historical_fields_preserved_in_record_rows": True,
            }
            atomic_write_jsonl(record_root / source_path.name, enriched)
            atomic_write_jsonl(image_root / source_path.name, image_rows)
            atomic_write_json(model_root / f"{model_id}.json", summary)
            summaries.append(summary)
            input_hashes[str(source_path)] = sha256_file(source_path)

        analysis = analyze_model_summaries(
            summaries,
            candidate_family_size=candidate_family_size,
            delta=delta,
            analysis_mode=analysis_mode,
            metrics_predeclared=metrics_predeclared,
            fresh_confirmation_set=fresh_confirmation_set,
            independent_frozen_donor_bank=independent_frozen_donor_bank,
        )
        bounds_by_model = {
            row["model_id"]: row for row in analysis["models"]
        }
        model_csv = [
            _model_csv_row(summary, bounds_by_model[summary["model_id"]])
            for summary in summaries
        ]
        category_csv = [
            row for summary in summaries for row in _category_csv_rows(summary)
        ]
        atomic_write_json(
            temporary / "model_summary.json",
            {
                "schema_version": 1,
                "analysis_type": "phase3_risk_v1_v6_backfill",
                "models": summaries,
            },
        )
        _write_csv(temporary / "model_summary.csv", model_csv)
        atomic_write_json(
            temporary / "category_summary.json",
            {
                "schema_version": 1,
                "models": [
                    {
                        "model_id": summary["model_id"],
                        "method": summary["method"],
                        "categories": summary["category_summaries"],
                    }
                    for summary in summaries
                ],
                "flat_results": category_csv,
            },
        )
        _write_csv(temporary / "category_summary.csv", category_csv)
        atomic_write_json(
            temporary / "exploratory_bounds.json", analysis
        )
        receipt = {
            "schema_version": 1,
            "status": "passed",
            "analysis_type": "phase3_risk_v1_v6_backfill",
            "analysis_mode": analysis_mode,
            "certified": analysis["certified"],
            "invalid_for_formal_certification_reasons": analysis[
                "invalid_for_formal_certification_reasons"
            ],
            "candidate_family_size": candidate_family_size,
            "model_count": len(summaries),
            "record_count_total": sum(
                int(summary["record_count"]) for summary in summaries
            ),
            "image_group_count_total": sum(
                int(summary["image_count"]) for summary in summaries
            ),
            "maximum_identity_error": max(
                float(summary["identity_check"]["maximum_error_record"])
                for summary in summaries
            ),
            "all_m0_invariants_pass": all(
                summary["m0_invariant"]["passes"]
                for summary in summaries
                if summary["method"] == "M0"
            ),
            "input_sha256": input_hashes,
            "historical_v6_outputs_modified": False,
        }
        atomic_write_json(temporary / "run_receipt.json", receipt)
        temporary.replace(destination)
        return receipt
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    backfill = subparsers.add_parser("backfill-v6")
    backfill.add_argument("--input-root", type=Path, required=True)
    backfill.add_argument("--legacy-summary-root", type=Path, required=True)
    backfill.add_argument("--output-dir", type=Path, required=True)
    backfill.add_argument("--candidate-family-size", type=int, required=True)
    backfill.add_argument("--delta", type=float, default=0.05)
    backfill.add_argument(
        "--analysis-mode", choices=ANALYSIS_MODES, required=True
    )
    backfill.add_argument("--metrics-predeclared", action="store_true")
    backfill.add_argument("--fresh-confirmation-set", action="store_true")
    backfill.add_argument(
        "--independent-frozen-donor-bank", action="store_true"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    receipt = backfill_v6(
        args.input_root,
        args.legacy_summary_root,
        args.output_dir,
        candidate_family_size=args.candidate_family_size,
        delta=args.delta,
        analysis_mode=args.analysis_mode,
        metrics_predeclared=args.metrics_predeclared,
        fresh_confirmation_set=args.fresh_confirmation_set,
        independent_frozen_donor_bank=args.independent_frozen_donor_bank,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
