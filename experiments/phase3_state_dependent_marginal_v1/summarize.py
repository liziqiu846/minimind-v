#!/usr/bin/env python3
"""Integrity-audit and summarize state × module × seed marginal values."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from experiments.phase3_module_marginal_budget_v1.codec import assert_round_trip
from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic
from experiments.phase3_private_vs_shared_v1.common import sha256_file

from . import EVALUATION_ROLE, MODULES, SEEDS
from .design import BASE_STATES, training_config
from .manifest import DEFAULT_MANIFEST, verify_frozen_manifest
from .run_experiment import (
    DEFAULT_RESULTS_ROOT,
    validate_result,
)


def _result_path(results_root: Path, run: Mapping[str, Any]) -> Path:
    return (
        results_root.resolve()
        / run["result_relative_directory"]
        / "run_result.json"
    )


def _audit_one(
    results_root: Path,
    run: Mapping[str, Any],
    manifest_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result_path = _result_path(results_root, run)
    status_path = result_path.with_name("run_status.json")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    validate_result(result, run, manifest_sha256)
    if (
        status.get("status") != "complete"
        or status.get("result_sha256") != sha256_file(result_path)
    ):
        raise ValueError("run status/result hash differs")
    checkpoint_path = Path(result["checkpoint_path"])
    training_manifest_path = Path(result["training_manifest_path"])
    if (
        sha256_file(checkpoint_path) != result["checkpoint_sha256"]
        or sha256_file(training_manifest_path)
        != result["training_manifest_sha256"]
    ):
        raise ValueError("checkpoint or training-manifest hash differs")
    training_manifest = json.loads(
        training_manifest_path.read_text(encoding="utf-8")
    )
    if (
        training_manifest.get("status") != "complete"
        or training_manifest.get("actual_optimizer_steps") != 1875
        or training_manifest.get("frozen_parameters_unchanged") is not True
        or training_manifest.get("checkpoint", {}).get("sha256")
        != result["checkpoint_sha256"]
    ):
        raise ValueError("training completion/freeze receipt differs")
    if run["run_type"] == "new_candidate":
        if (
            training_manifest.get("config") != training_config(run)
            or result["training_status"] != "new_training"
        ):
            raise ValueError("new candidate training config differs")
    else:
        source = run["source"]
        if (
            result["checkpoint_sha256"] != source["checkpoint_sha256"]
            or result["training_manifest_sha256"]
            != source["training_manifest_sha256"]
            or result["training_status"] != "reused_previous_checkpoint"
        ):
            raise ValueError("base checkpoint reuse differs")
    codec_paths = {
        module: Path(result["module_codec_paths"][module]) for module in MODULES
    }
    decoded = assert_round_trip(
        {module: path.read_bytes() for module, path in codec_paths.items()}
    )
    if {
        module: int(value.numel()) for module, value in decoded.items()
    } != run["coordinate_dimensions"]:
        raise ValueError("module codec decoded dimensions differ")
    codec_receipt = json.loads(
        Path(result["codec_receipt_path"]).read_text(encoding="utf-8")
    )
    if (
        codec_receipt.get("module_wise_encoded_bits")
        != result["module_wise_encoded_bits"]
        or codec_receipt.get("total_encoded_bits") != result["total_encoded_bits"]
    ):
        raise ValueError("module codec receipt bit accounting differs")
    evaluation_path = Path(result["development_evaluation_result_path"])
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if (
        sha256_file(evaluation_path)
        != result["development_evaluation_result_sha256"]
        or evaluation.get("run_id") != run["run_id"]
        or evaluation.get("evaluation_role") != EVALUATION_ROLE
        or evaluation.get("status") != "complete"
        or evaluation.get("development_record_count") != 4107
        or evaluation.get("development_image_count") != 1343
        or float(evaluation["development_task_risk"])
        != float(result["development_task_risk"])
    ):
        raise ValueError("development evaluation receipt differs")
    for path_field, hash_field in (
        ("record_scores_path", "record_scores_sha256"),
        ("record_risks_path", "record_risks_sha256"),
        ("image_group_risks_path", "image_group_risks_sha256"),
        ("risk_summary_path", "risk_summary_sha256"),
    ):
        artifact = Path(evaluation[path_field])
        if sha256_file(artifact) != evaluation[hash_field]:
            raise ValueError("development evaluation child artifact differs")
    receipt = {
        "run_id": run["run_id"],
        "run_type": run["run_type"],
        "base_state": run["base_state"],
        "module": run["module"],
        "seed": run["seed"],
        "status": "verified",
        "checkpoint_sha256": result["checkpoint_sha256"],
        "training_manifest_sha256": result["training_manifest_sha256"],
        "frozen_parameters_unchanged": True,
        "actual_optimizer_steps": 1875,
        "module_codec_round_trip": True,
        "development_evaluation_complete": True,
    }
    return result, receipt


def audit_results(
    manifest_path: Path, results_root: Path
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = verify_frozen_manifest(manifest_path)
    manifest_sha256 = sha256_file(manifest_path)
    results, receipts = {}, []
    for run in manifest["runs"]:
        result, receipt = _audit_one(
            results_root, run, manifest_sha256
        )
        results[run["run_id"]] = result
        receipts.append(receipt)
    new_count = sum(
        result["training_status"] == "new_training" for result in results.values()
    )
    reuse_count = sum(
        result["training_status"] == "reused_previous_checkpoint"
        for result in results.values()
    )
    if len(results) != 36 or new_count != 27 or reuse_count != 9:
        raise AssertionError("completed training/reuse counts differ")
    report = {
        "schema_version": 1,
        "status": "passed",
        "experiment_manifest_path": str(manifest_path.resolve()),
        "experiment_manifest_sha256": manifest_sha256,
        "results_root": str(results_root.resolve()),
        "completed_model_run_count": len(results),
        "new_training_count": new_count,
        "reused_checkpoint_count": reuse_count,
        "comparison_count": 27,
        "all_training_freeze_checks_passed": True,
        "all_codec_round_trips_passed": True,
        "all_development_evaluations_complete": True,
        "source_artifacts_unchanged": True,
        "runs": receipts,
    }
    return report, results


def _comparison(
    row: Mapping[str, Any], results: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    base = results[row["base_run_id"]]
    candidate = results[row["candidate_run_id"]]
    module = str(row["module"])
    base_bits = int(base["module_wise_encoded_bits"][module])
    new_bits = int(candidate["module_wise_encoded_bits"][module])
    delta_bits = new_bits - base_bits
    delta_risk = (
        float(candidate["development_task_risk"])
        - float(base["development_task_risk"])
    )
    eta = -delta_risk / delta_bits if delta_bits > 0 else None
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
        "status": "valid" if delta_bits > 0 else "invalid_nonpositive_bit_delta",
        "evaluation_role": EVALUATION_ROLE,
    }


def build_summary(
    manifest: Mapping[str, Any],
    results: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    comparisons = [_comparison(row, results) for row in manifest["comparisons"]]
    rankings = {}
    for state in BASE_STATES:
        state_rows = [row for row in comparisons if row["base_state"] == state]
        by_seed = {}
        for seed in SEEDS:
            seed_rows = [row for row in state_rows if row["seed"] == seed]
            if len(seed_rows) != 3 or any(
                row["eta_marginal_value"] is None for row in seed_rows
            ):
                raise ValueError("state/seed marginal ranking is incomplete")
            ordered = sorted(
                seed_rows,
                key=lambda row: (-row["eta_marginal_value"], MODULES.index(row["module"])),
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
        state_ranking = sorted(
            MODULES, key=lambda module: (-median_eta[module], MODULES.index(module))
        )
        seed_rankings = [by_seed[str(seed)]["ranking"] for seed in SEEDS]
        rankings[state] = {
            "aggregation": "three_seed_median_eta",
            "ranking": state_ranking,
            "median_eta_by_module": median_eta,
            "ranking_by_seed": by_seed,
            "all_three_seeds_same_ranking": all(
                ranking == seed_rankings[0] for ranking in seed_rankings[1:]
            ),
        }
    return {
        "schema_version": 1,
        "status": "complete",
        "evaluation_role": EVALUATION_ROLE,
        "marginal_value_definition": (
            "-(R_new-R_base)/(C_M_new-C_M_base)"
        ),
        "denominator": "trained_target_module_actual_encoded_bit_difference",
        "comparison_count": len(comparisons),
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
    report, results = audit_results(args.manifest, args.results_root)
    manifest = verify_frozen_manifest(args.manifest)
    summary = build_summary(manifest, results)
    integrity_path = (
        args.integrity_output
        or args.results_root.resolve() / "integrity_report.json"
    )
    summary_path = (
        args.summary_output
        or args.results_root.resolve() / "state_dependent_marginal_summary.json"
    )
    write_json_atomic(integrity_path, report)
    write_json_atomic(summary_path, summary)
    print(
        json.dumps(
            {
                "status": "complete",
                "integrity_report": str(integrity_path),
                "summary": str(summary_path),
                "new_training_count": report["new_training_count"],
                "reused_checkpoint_count": report["reused_checkpoint_count"],
                "state_rankings": summary["state_rankings"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

