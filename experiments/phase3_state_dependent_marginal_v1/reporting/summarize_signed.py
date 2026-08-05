#!/usr/bin/env python3
"""Report eta using the signed, trained target-module bit difference."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic
from experiments.phase3_private_vs_shared_v1.common import sha256_file

from .. import EVALUATION_ROLE, MODULES, SEEDS
from ..design import BASE_STATES
from ..manifest import DEFAULT_MANIFEST, verify_frozen_manifest
from ..run_experiment import DEFAULT_RESULTS_ROOT
from ..summarize import audit_results


def comparison(row, results):
    base = results[row["base_run_id"]]
    candidate = results[row["candidate_run_id"]]
    module = row["module"]
    base_bits = int(base["module_wise_encoded_bits"][module])
    new_bits = int(candidate["module_wise_encoded_bits"][module])
    delta_bits = new_bits - base_bits
    delta_risk = (
        float(candidate["development_task_risk"])
        - float(base["development_task_risk"])
    )
    eta = None if delta_bits == 0 else -delta_risk / delta_bits
    if eta is not None and not math.isfinite(eta):
        raise FloatingPointError("marginal value is non-finite")
    return {
        "base_state": row["base_state"],
        "module": module,
        "seed": int(row["seed"]),
        "base_run_id": row["base_run_id"],
        "candidate_run_id": row["candidate_run_id"],
        "base_coordinate_dimensions": dict(base["coordinate_dimensions"]),
        "candidate_coordinate_dimensions": dict(
            candidate["coordinate_dimensions"]
        ),
        "base_development_task_risk": float(base["development_task_risk"]),
        "candidate_development_task_risk": float(
            candidate["development_task_risk"]
        ),
        "delta_risk_new_minus_base": delta_risk,
        "base_target_module_actual_encoded_bits": base_bits,
        "candidate_target_module_actual_encoded_bits": new_bits,
        "delta_target_module_actual_encoded_bits": delta_bits,
        "eta_marginal_value": eta,
        "status": (
            "undefined_zero_actual_bit_delta"
            if delta_bits == 0
            else (
                "valid_signed_negative_actual_bit_delta"
                if delta_bits < 0
                else "valid"
            )
        ),
        "evaluation_role": EVALUATION_ROLE,
    }


def build_signed_summary(manifest, results):
    comparisons = [comparison(row, results) for row in manifest["comparisons"]]
    if len(comparisons) != 27:
        raise AssertionError("comparison count differs")
    zero_delta = [
        row
        for row in comparisons
        if row["delta_target_module_actual_encoded_bits"] == 0
    ]
    if zero_delta:
        raise ValueError("eta is undefined for a zero actual-bit difference")
    rankings = {}
    for state in BASE_STATES:
        state_rows = [row for row in comparisons if row["base_state"] == state]
        by_seed = {}
        for seed in SEEDS:
            seed_rows = [row for row in state_rows if row["seed"] == seed]
            if len(seed_rows) != 3:
                raise ValueError("state/seed comparison set is incomplete")
            ordered = sorted(
                seed_rows,
                key=lambda row: (
                    -row["eta_marginal_value"],
                    MODULES.index(row["module"]),
                ),
            )
            by_seed[str(seed)] = {
                "seed": seed,
                "ranking": [row["module"] for row in ordered],
                "eta_by_module": {
                    row["module"]: row["eta_marginal_value"] for row in seed_rows
                },
            }
        median_eta = {
            module: statistics.median(
                row["eta_marginal_value"]
                for row in state_rows
                if row["module"] == module
            )
            for module in MODULES
        }
        ranking = sorted(
            MODULES,
            key=lambda module: (
                -median_eta[module],
                MODULES.index(module),
            ),
        )
        seed_rankings = [by_seed[str(seed)]["ranking"] for seed in SEEDS]
        rankings[state] = {
            "aggregation": "three_seed_median_eta",
            "ranking": ranking,
            "median_eta_by_module": median_eta,
            "ranking_by_seed": by_seed,
            "all_three_seeds_same_ranking": all(
                value == seed_rankings[0] for value in seed_rankings[1:]
            ),
        }
    return {
        "schema_version": 1,
        "status": "complete",
        "evaluation_role": EVALUATION_ROLE,
        "marginal_value_definition": (
            "-(R_new-R_base)/(C_M_new-C_M_base)"
        ),
        "denominator": (
            "signed_trained_target_module_actual_encoded_bit_difference"
        ),
        "comparison_count": 27,
        "negative_actual_bit_delta_count": sum(
            row["delta_target_module_actual_encoded_bits"] < 0
            for row in comparisons
        ),
        "zero_actual_bit_delta_count": 0,
        "comparisons": comparisons,
        "state_rankings": rankings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--integrity-output", type=Path)
    args = parser.parse_args()
    integrity, results = audit_results(args.manifest, args.results_root)
    manifest = verify_frozen_manifest(args.manifest)
    summary = build_signed_summary(manifest, results)
    reporting_path = Path(__file__).resolve()
    reporting_binding = {
        "reporting_source_path": str(reporting_path),
        "reporting_source_sha256": sha256_file(reporting_path),
    }
    integrity = {**integrity, **reporting_binding}
    summary = {**summary, **reporting_binding}
    integrity_path = (
        args.integrity_output
        or args.results_root.resolve() / "integrity_report.json"
    )
    summary_path = (
        args.summary_output
        or args.results_root.resolve() / "state_dependent_marginal_summary.json"
    )
    write_json_atomic(integrity_path, integrity)
    write_json_atomic(summary_path, summary)
    print(
        json.dumps(
            {
                "status": "complete",
                "integrity_report": str(integrity_path),
                "summary": str(summary_path),
                "new_training_count": integrity["new_training_count"],
                "reused_checkpoint_count": integrity[
                    "reused_checkpoint_count"
                ],
                "negative_actual_bit_delta_count": summary[
                    "negative_actual_bit_delta_count"
                ],
                "state_rankings": summary["state_rankings"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

