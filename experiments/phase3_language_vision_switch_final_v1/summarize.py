#!/usr/bin/env python3
"""Integrity-audit and summarize the final full-bound switch decision."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from experiments.generalization_bound import description_complexity_nats
from experiments.phase3_module_marginal_budget_v1.codec import assert_round_trip
from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic
from experiments.phase3_private_vs_shared_v1.common import sha256_file

from . import ACTION_MODULES, COORDINATE_MODULES, EVALUATION_ROLE, SEEDS
from .design import BASE_STATES, DECISION_RULE, training_config
from .manifest import DEFAULT_MANIFEST, verify_frozen_manifest
from .run_experiment import DEFAULT_RESULTS_ROOT, validate_result


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
    if (
        sha256_file(Path(result["checkpoint_path"]))
        != result["checkpoint_sha256"]
        or sha256_file(Path(result["training_manifest_path"]))
        != result["training_manifest_sha256"]
    ):
        raise ValueError("checkpoint or training-manifest hash differs")
    training_manifest = json.loads(
        Path(result["training_manifest_path"]).read_text(encoding="utf-8")
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
            or result["training_status"] != "reused_complete_base_result"
            or result["source_run_result_sha256"]
            != source["source_run_result_sha256"]
        ):
            raise ValueError("complete base-result reuse differs")
    codec_paths = {
        module: Path(result["module_codec_paths"][module])
        for module in COORDINATE_MODULES
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
        or codec_receipt.get("total_encoded_bits")
        != result["total_encoded_bits"]
    ):
        raise ValueError("module codec receipt bit accounting differs")
    evaluation_path = Path(result["development_evaluation_result_path"])
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    expected_evaluation_run_id = (
        run["run_id"]
        if run["run_type"] == "new_candidate"
        else run["source"]["source_run_id"]
    )
    if (
        sha256_file(evaluation_path)
        != result["development_evaluation_result_sha256"]
        or evaluation.get("run_id") != expected_evaluation_run_id
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
        result["training_status"] == "new_training"
        for result in results.values()
    )
    reuse_count = sum(
        result["training_status"] == "reused_complete_base_result"
        for result in results.values()
    )
    if len(results) != 18 or new_count != 12 or reuse_count != 6:
        raise AssertionError("completed training/reuse counts differ")
    report = {
        "schema_version": 1,
        "status": "passed",
        "experiment_manifest_path": str(manifest_path.resolve()),
        "experiment_manifest_sha256": manifest_sha256,
        "results_root": str(results_root.resolve()),
        "completed_model_run_count": len(results),
        "new_training_count": new_count,
        "reused_complete_base_result_count": reuse_count,
        "comparison_count": 12,
        "all_training_freeze_checks_passed": True,
        "all_codec_round_trips_passed": True,
        "all_development_evaluations_complete": True,
        "source_artifacts_unchanged": True,
        "runs": receipts,
    }
    return report, results


def full_bound(
    result: Mapping[str, Any], bound_spec: Mapping[str, Any]
) -> dict[str, float]:
    risk = float(result["development_task_risk"])
    bits = float(result["total_encoded_bits"])
    sample_count = int(bound_spec["independent_sample_count"])
    delta_each = float(bound_spec["delta_each"])
    if (
        not 0.0 <= risk <= 1.0
        or bits < 1.0
        or sample_count <= 0
        or not 0.0 < delta_each < 1.0
    ):
        raise ValueError("invalid full-bound input")
    complexity = description_complexity_nats(bits)
    penalty = math.sqrt(
        (complexity + math.log(1.0 / delta_each))
        / (2.0 * sample_count)
    )
    return {
        "empirical_risk": risk,
        "actual_total_encoded_bits": bits,
        "complexity_nats": complexity,
        "generalization_penalty": penalty,
        "B_raw_unclipped": risk + penalty,
    }


def _comparison(
    row: Mapping[str, Any],
    results: Mapping[str, Mapping[str, Any]],
    bound_spec: Mapping[str, Any],
    bit_gate: Mapping[str, Any],
) -> dict[str, Any]:
    base = results[row["base_run_id"]]
    candidate = results[row["candidate_run_id"]]
    module = str(row["module"])
    base_bound = full_bound(base, bound_spec)
    candidate_bound = full_bound(candidate, bound_spec)
    delta_target_bits = (
        int(candidate["module_wise_encoded_bits"][module])
        - int(base["module_wise_encoded_bits"][module])
    )
    minimum = int(bit_gate["minimum_target_module_delta_bits_each_seed"])
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
        "base_development_task_risk": float(
            base["development_task_risk"]
        ),
        "candidate_development_task_risk": float(
            candidate["development_task_risk"]
        ),
        "base_total_actual_encoded_bits": int(base["total_encoded_bits"]),
        "candidate_total_actual_encoded_bits": int(
            candidate["total_encoded_bits"]
        ),
        "delta_total_actual_encoded_bits": int(
            candidate["total_encoded_bits"]
        )
        - int(base["total_encoded_bits"]),
        "base_target_module_actual_encoded_bits": int(
            base["module_wise_encoded_bits"][module]
        ),
        "candidate_target_module_actual_encoded_bits": int(
            candidate["module_wise_encoded_bits"][module]
        ),
        "delta_target_module_actual_encoded_bits": delta_target_bits,
        "target_bit_minimum_gate_passed": delta_target_bits >= minimum,
        "B_base": base_bound["B_raw_unclipped"],
        "B_candidate": candidate_bound["B_raw_unclipped"],
        "delta_B": (
            base_bound["B_raw_unclipped"]
            - candidate_bound["B_raw_unclipped"]
        ),
        "base_bound_components": base_bound,
        "candidate_bound_components": candidate_bound,
        "evaluation_role": EVALUATION_ROLE,
    }


def build_summary(
    manifest: Mapping[str, Any],
    results: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    bit_gate = manifest["calibration"]["bit_adequacy_gate"]
    comparisons = [
        _comparison(row, results, manifest["bound"], bit_gate)
        for row in manifest["comparisons"]
    ]
    state_results = {}
    ratio_checks = []
    for state in BASE_STATES:
        state_rows = [
            row for row in comparisons if row["base_state"] == state
        ]
        by_seed = {}
        for seed in SEEDS:
            seed_rows = [
                row for row in state_rows if row["seed"] == seed
            ]
            if len(seed_rows) != 2:
                raise ValueError("state/seed action comparison is incomplete")
            by_module = {row["module"]: row for row in seed_rows}
            ordered = sorted(
                ACTION_MODULES,
                key=lambda module: (
                    -by_module[module]["delta_B"],
                    ACTION_MODULES.index(module),
                ),
            )
            deltas = [
                by_module[module][
                    "delta_target_module_actual_encoded_bits"
                ]
                for module in ACTION_MODULES
            ]
            positive = all(value > 0 for value in deltas)
            ratio = (
                max(deltas) / min(deltas)
                if positive
                else math.inf
            )
            ratio_pass = (
                positive
                and ratio
                <= float(
                    bit_gate[
                        "maximum_within_state_seed_action_ratio"
                    ]
                )
            )
            ratio_checks.append(
                {
                    "base_state": state,
                    "seed": seed,
                    "vision_delta_target_bits": by_module["vision"][
                        "delta_target_module_actual_encoded_bits"
                    ],
                    "language_delta_target_bits": by_module["language"][
                        "delta_target_module_actual_encoded_bits"
                    ],
                    "larger_to_smaller_ratio": ratio,
                    "ratio_gate_passed": ratio_pass,
                }
            )
            by_seed[str(seed)] = {
                "seed": seed,
                "ranking": ordered,
                "delta_B_by_module": {
                    module: by_module[module]["delta_B"]
                    for module in ACTION_MODULES
                },
                "bit_ratio_gate_passed": ratio_pass,
            }
        median_delta = {
            module: statistics.median(
                row["delta_B"]
                for row in state_rows
                if row["module"] == module
            )
            for module in ACTION_MODULES
        }
        median_ranking = sorted(
            ACTION_MODULES,
            key=lambda module: (
                -median_delta[module],
                ACTION_MODULES.index(module),
            ),
        )
        expected = (
            DECISION_RULE["original_expected_order"]
            if state == "original"
            else DECISION_RULE["language_rich_expected_order"]
        )
        matching_seed_count = sum(
            by_seed[str(seed)]["ranking"] == expected
            for seed in SEEDS
        )
        order_pass = (
            matching_seed_count
            >= int(DECISION_RULE["required_seed_majority"])
            and median_ranking == expected
        )
        state_results[state] = {
            "expected_ranking": expected,
            "ranking_by_seed": by_seed,
            "matching_seed_count": matching_seed_count,
            "median_delta_B_by_module": median_delta,
            "median_ranking": median_ranking,
            "order_gate_passed": order_pass,
        }
    minimum_gate_pass = all(
        row["target_bit_minimum_gate_passed"] for row in comparisons
    )
    ratio_gate_pass = all(
        row["ratio_gate_passed"] for row in ratio_checks
    )
    bit_adequacy_pass = minimum_gate_pass and ratio_gate_pass
    switch_pass = (
        bit_adequacy_pass
        and all(
            state_results[state]["order_gate_passed"]
            for state in BASE_STATES
        )
    )
    decision = (
        DECISION_RULE["pass_decision"]
        if switch_pass
        else DECISION_RULE["fail_decision"]
    )
    return {
        "schema_version": 1,
        "status": "complete",
        "evaluation_role": EVALUATION_ROLE,
        "primary_metric": "delta_B=B_base-B_candidate",
        "bound_specification": dict(manifest["bound"]),
        "comparison_count": len(comparisons),
        "comparisons": comparisons,
        "bit_adequacy": {
            "gate_specification": dict(bit_gate),
            "minimum_gate_passed": minimum_gate_pass,
            "within_state_seed_ratio_checks": ratio_checks,
            "ratio_gate_passed": ratio_gate_pass,
            "overall_passed": bit_adequacy_pass,
        },
        "state_results": state_results,
        "decision_rule": dict(DECISION_RULE),
        "switch_validation_passed": switch_pass,
        "route_decision": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--results-root", type=Path, default=DEFAULT_RESULTS_ROOT
    )
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
        or args.results_root.resolve()
        / "language_vision_switch_summary.json"
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
                "reused_complete_base_result_count": report[
                    "reused_complete_base_result_count"
                ],
                "bit_adequacy": summary["bit_adequacy"],
                "state_results": summary["state_results"],
                "route_decision": summary["route_decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

