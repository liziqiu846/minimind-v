#!/usr/bin/env python3
"""Independently audit frozen registry, selection, summary, and CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .common import (
    DEFAULT_AUDIT,
    DEFAULT_CSV,
    DEFAULT_REGISTRY,
    DEFAULT_SELECTION,
    DEFAULT_SUMMARY,
    load_json,
    sha256_file,
    write_json_exclusive,
)
from .evaluate import build_summary
from .selector import _load_decimal_json, select_candidate


def audit(
    registry_path: Path,
    selection_path: Path,
    summary_path: Path,
    csv_path: Path,
) -> dict:
    decimal_registry = _load_decimal_json(registry_path)
    expected_selection = select_candidate(decimal_registry)
    selection = load_json(selection_path)
    summary = load_json(summary_path)
    registry = load_json(registry_path)
    reproduced = build_summary(
        registry,
        selection,
        registry_path=registry_path,
        selection_path=selection_path,
    )
    with csv_path.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    checks = {
        "registry_status_frozen": (
            registry.get("status") == "frozen_before_selection"
        ),
        "registry_has_no_heldout_values": (
            registry["leakage_control"][
                "registry_contains_heldout_risk_values"
            ]
            is False
            and all(
                row["heldout_evaluation"]["value_in_registry"] is False
                for row in registry["candidates"]
            )
        ),
        "selection_is_unique_argmin": (
            selection["selected"]["candidate_id"]
            == expected_selection["selected"]["candidate_id"]
        ),
        "baseline_is_frozen": (
            selection["baseline"]["candidate_id"]
            == registry["baseline"]["candidate_id"]
        ),
        "summary_exactly_reproduced": reproduced == summary,
        "csv_has_one_final_comparison": (
            len(csv_rows) == 1
            and csv_rows[0]["decision"] == summary["decision"]
            and csv_rows[0]["selected_model_id"]
            == summary["selected"]["candidate_id"]
            and csv_rows[0]["baseline_model_id"]
            == summary["baseline"]["candidate_id"]
        ),
    }
    return {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "candidate_count": registry["candidate_count"],
        "selection_cost_bits": registry["selection_cost"][
            "ceil_log2_k_bits"
        ],
        "selected_candidate_id": selection["selected"]["candidate_id"],
        "baseline_candidate_id": selection["baseline"]["candidate_id"],
        "decision": summary["decision"],
        "artifact_sha256": {
            "candidate_registry": sha256_file(registry_path),
            "selection_receipt": sha256_file(selection_path),
            "boundselect_summary_json": sha256_file(summary_path),
            "boundselect_summary_csv": sha256_file(csv_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output", type=Path, default=DEFAULT_AUDIT)
    args = parser.parse_args()
    report = audit(
        args.registry, args.selection, args.summary, args.csv
    )
    write_json_exclusive(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
