#!/usr/bin/env python3
"""Post-execution completion audit for the hardware-amended Stage 2 v2 run."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import Stage2Protocol, sha256_file, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--final-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


class Audit:
    def __init__(self) -> None:
        self.checks: dict[str, bool] = {}
        self.details: dict[str, Any] = {}

    def require(self, label: str, condition: bool) -> None:
        if label in self.checks:
            raise ValueError(f"duplicate audit check: {label}")
        self.checks[label] = bool(condition)

    def finish(self) -> dict[str, Any]:
        failed = [label for label, passed in self.checks.items() if not passed]
        return {
            "schema_version": 1,
            "audit_id": "minimind-v-stage2-v2-fast-completion-audit",
            "status": "passed" if not failed else "failed",
            "post_execution_audit_only": True,
            "frozen_experiment_implementation_changed_by_audit": False,
            "check_count": len(self.checks),
            "passed_check_count": sum(self.checks.values()),
            "failed_checks": failed,
            "checks": self.checks,
            "details": self.details,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_text(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"completion audit already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    payload = protocol.payload
    reference = protocol.reference()
    confirmation_reference = protocol.confirmation_reference()
    formal_root = args.formal_root.resolve()
    final_root = args.final_root.resolve()
    audit = Audit()

    runtime = load_json(final_root / "runtime_integrity.json")
    runtime_body = runtime.get("runtime_integrity", {})
    tag = payload["git"]["annotated_tag"]
    tag_commit = git_text("rev-list", "-n", "1", tag)
    audit.require("protocol_tag_is_annotated", git_text("cat-file", "-t", f"refs/tags/{tag}") == "tag")
    audit.require("runtime_head_equals_protocol_tag", runtime_body.get("head_commit") == tag_commit)
    audit.require("runtime_tag_commit_matches", runtime_body.get("tag_commit") == tag_commit)
    audit.require("runtime_protocol_matches", runtime.get("protocol") == reference)
    audit.require("runtime_integrity_passed", runtime.get("status") == "passed" and runtime_body.get("status") == "passed")
    load_guard = runtime.get("model_load_guard", {})
    audit.require("all_four_model_load_guards_executed", load_guard.get("executed") is True and len(load_guard.get("groups", [])) == 4)
    audit.require("all_initial_language_tensors_exact", load_guard.get("all_initial_language_tensors_exact") is True)

    reuse = payload["data"]["reused_confirmation"]
    data_root = protocol.confirmation_directory()
    data_files = {
        "catalog": ("eligible_catalog.parquet", "catalog_sha256"),
        "catalog_manifest": ("catalog_manifest.json", "catalog_manifest_sha256"),
        "split_manifest": ("split_manifest.json", "split_manifest_sha256"),
        "train": ("train.parquet", "train_sha256"),
        "validation": ("validation.parquet", "validation_sha256"),
        "verification": ("verification.json", "independent_verification_sha256"),
        "replay": ("replay_verification.json", "replay_verification_sha256"),
    }
    for role, (name, hash_key) in data_files.items():
        audit.require(f"confirmation_{role}_hash", sha256_file(data_root / name) == reuse[hash_key])
    for name in ("catalog_manifest.json", "split_manifest.json", "verification.json", "replay_verification.json"):
        audit.require(
            f"{Path(name).stem}_binds_source_protocol",
            load_json(data_root / name).get("protocol") == confirmation_reference,
        )
    verification = load_json(data_root / "verification.json")
    replay = load_json(data_root / "replay_verification.json")
    audit.require("independent_confirmation_verification_passed", verification.get("status") == "passed")
    audit.require("independent_confirmation_verified_12000_draws", verification.get("verified_draws") == 12000)
    audit.require("independent_confirmation_replay_passed", replay.get("status") == "passed")
    audit.require(
        "confirmation_replay_counts_match",
        replay.get("train_draws") == 10000 and replay.get("validation_draws") == 2000,
    )
    source_tag_commit = git_text("rev-list", "-n", "1", reuse["source_tag"])
    source_protocol_blob = subprocess.run(
        ["git", "show", f"{source_tag_commit}:experiments/stage2_protocol_v2.json"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    audit.require(
        "confirmation_source_protocol_blob_hash",
        hashlib.sha256(source_protocol_blob).hexdigest() == confirmation_reference["protocol_sha256"],
    )

    plan = load_json(formal_root / "pipeline_plan.json")
    progress = load_json(formal_root / "pipeline_progress.json")
    expected = [
        ("M0", 43101, 0.05),
        ("M0", 43102, 0.05),
        ("M0", 43103, 0.05),
        ("M1", None, 0.015),
        ("M2", 43101, 0.05),
        ("M2", 43102, 0.05),
        ("M2", 43103, 0.05),
        ("M3", 43101, 0.05),
        ("M3", 43102, 0.05),
        ("M3", 43103, 0.05),
    ]
    audit.require("formal_plan_protocol", plan.get("protocol") == reference)
    audit.require("formal_plan_has_ten_runs", len(plan.get("runs", [])) == len(expected))
    audit.require(
        "formal_pipeline_complete",
        progress.get("status") == "complete"
        and progress.get("completed_runs") == 10
        and progress.get("completed_run_ordinals") == list(range(1, 11)),
    )
    assignments = progress.get("assignments", [])
    eligible = set(payload["hardware_execution"]["eligible_gpu_uuids"])
    audit.require(
        "ten_complete_eligible_gpu_assignments",
        len(assignments) == 10
        and {row.get("ordinal") for row in assignments} == set(range(1, 11))
        and all(row.get("status") == "complete" and row.get("gpu_uuid") in eligible for row in assignments),
    )
    audit.require(
        "no_formal_failure_receipts",
        not list(formal_root.rglob("failure_receipt.json"))
        and not (formal_root / "pipeline_failure.json").exists(),
    )

    bound_pairs: set[tuple[str, int | None]] = set()
    for ordinal, (group, root, learning_rate) in enumerate(expected, start=1):
        run_plan = plan["runs"][ordinal - 1]
        run_dir = Path(run_plan["directory"])
        prefix = f"run_{ordinal:02d}"
        audit.require(
            f"{prefix}_all_planned_completions_exist",
            all(Path(stage["completion"]).exists() for stage in run_plan["stages"]),
        )
        training = load_json(run_dir / "train/training_manifest.json")
        audit.require(
            f"{prefix}_frozen_identity",
            (
                training.get("status"),
                training.get("formal"),
                training.get("model_group"),
                training.get("mapping_root"),
                training.get("learning_rate"),
                training.get("train_seed"),
                training.get("protocol"),
            )
            == ("complete", True, group, root, learning_rate, 2026, reference),
        )
        initial_load = (
            training.get("model", {})
            .get("initial_structure", {})
            .get("adapter", {})
            .get("initial_llm_load", {})
        )
        audit.require(
            f"{prefix}_initial_model_load_exact",
            initial_load.get("exact_initial_tensor_match") is True
            and not initial_load.get("unexpected_keys"),
        )
        audit.require(
            f"{prefix}_base_parameters_frozen",
            training.get("model", {}).get("initial_frozen_parameter_sha256")
            == training.get("model", {}).get("final_frozen_parameter_sha256"),
        )
        bound = load_json(run_dir / "bound.json")
        bound_pairs.add((bound.get("model_group"), bound.get("mapping_root")))
        audit.require(
            f"{prefix}_formal_bound_identity",
            bound.get("formal") is True
            and bound.get("protocol") == reference
            and (bound.get("model_group"), bound.get("mapping_root")) == (group, root)
            and bound.get("independent_train_samples") == 10000
            and bound.get("confidence_delta") == 0.005,
        )
        bound_inputs = {
            "adapter_summary_sha256": run_dir / "decode/adapter_summary.json",
            "decoded_model_hash_sha256": run_dir / "decode/decoded_model_hash.json",
            "decoded_training_risk_sha256": run_dir / "risk_decoded_train.json",
            "decoded_validation_risk_sha256": run_dir / "risk_decoded_validation_correct.json",
            "unquantized_training_risk_sha256": run_dir / "risk_unquantized_train.json",
        }
        audit.require(
            f"{prefix}_bound_input_hashes",
            all(bound["inputs"].get(key) == sha256_file(path) for key, path in bound_inputs.items()),
        )
        conditions = ("correct",) if group == "M0" else ("correct", "paired_shuffled", "none")
        for condition in conditions:
            risk = load_json(run_dir / f"risk_decoded_validation_{condition}.json")
            audit.require(
                f"{prefix}_validation_{condition}",
                risk.get("protocol") == reference
                and risk.get("image_condition") == condition
                and risk.get("data", {}).get("sample_count") == 2000,
            )
    audit.require("exact_predeclared_model_root_set", bound_pairs == {(g, r) for g, r, _ in expected})

    summary = load_json(final_root / "formal_summary.json")
    audit.require(
        "formal_summary_complete",
        summary.get("protocol") == reference
        and summary.get("formal_model_count") == 10
        and len(summary.get("bounds", [])) == 10,
    )
    audit.require(
        "no_posthoc_mapping_root_selection",
        summary.get("best_mapping_root_selected") is False
        and [row["mapping_root"] for row in summary.get("paired_differences", [])]
        == [43101, 43102, 43103],
    )
    diagnostics = load_json(final_root / "diagnostics.json")
    expected_diagnostics = {("M1", None)} | {
        (group, root) for group in ("M2", "M3") for root in (43101, 43102, 43103)
    }
    audit.require(
        "diagnostics_secondary_only",
        diagnostics.get("protocol") == reference
        and diagnostics.get("status") == "secondary descriptive only"
        and diagnostics.get("formal_hypothesis_test") is False
        and diagnostics.get("model_selection_use") is False,
    )
    audit.require(
        "exact_seven_visual_diagnostics",
        {(row["model_group"], row["mapping_root"]) for row in diagnostics.get("models", [])}
        == expected_diagnostics,
    )

    report = load_json(final_root / "stage2_final_report.json")
    audit.require(
        "final_report_complete",
        report.get("status") == "complete"
        and report.get("protocol") == reference
        and len(report.get("formal_results", [])) == 10,
    )
    audit.require("final_report_source_data_protocol", report.get("confirmation_data_protocol") == confirmation_reference)
    audit.require(
        "final_report_certificate_scope",
        report.get("certificate", {}).get("status")
        == "strict_finite_catalog_certificate_hardware_amended"
        and report.get("certificate", {}).get("real_world_distribution") is False,
    )
    audit.require("final_report_diagnostics_hash", report.get("diagnostics_sha256") == sha256_file(final_root / "diagnostics.json"))
    audit.require(
        "final_report_manifest_hash",
        report.get("artifact_manifest_sha256")
        == sha256_file(final_root / "stage2_artifact_manifest.json"),
    )

    manifest = load_json(final_root / "stage2_artifact_manifest.json")
    mismatches = []
    for item in manifest.get("artifacts", []):
        path = Path(item["path"])
        if (
            not path.exists()
            or path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            mismatches.append(str(path))
    audit.require(
        "artifact_manifest_replay",
        manifest.get("protocol") == reference
        and manifest.get("artifact_count") == len(manifest.get("artifacts", []))
        and not mismatches,
    )

    v1_final = REPO_ROOT / "experiments/runs/stage2/final"
    v1_expected = {
        "stage2_final_report.md": "9db351916371b1a213e97b7ceec88b396ad7f3647ab73c0dac48b3bebe7e1210",
        "stage2_final_report.json": "8ef8a277f074425b44f32a20464129752620d33d1a1509c4cf6a7d80ca6ca0a7",
        "stage2_artifact_manifest.json": "716b893c2e1bc17719c574055f95a8ef78b67c1200dd7d842dca5ef525f7d7e5",
    }
    audit.require(
        "v1_final_artifacts_immutable",
        all(sha256_file(v1_final / name) == expected for name, expected in v1_expected.items()),
    )
    v1_audits = REPO_ROOT / "experiments/audits/stage2_v1"
    audit.require("v1_model_load_audit_passed", load_json(v1_audits / "model_load_audit.json").get("status") == "passed")
    audit.require("v1_integrity_audit_passed", load_json(v1_audits / "integrity_audit.json").get("status") == "passed")
    audit.require(
        "v1_sampling_limit_recorded",
        load_json(v1_audits / "sampling_assumption_audit.json").get("status")
        == "theorem_independence_not_established",
    )
    audit.require(
        "v1_closeout_status_recorded",
        load_json(v1_audits / "audit_summary.json").get("status")
        == "empirical_results_preserved_certificate_exploratory",
    )
    comparison = load_json(final_root / "stage2_v1_v2_comparison.json")
    audit.require(
        "v1_v2_comparison_complete",
        comparison.get("status") == "complete"
        and len(comparison.get("model_rows", [])) == 10
        and comparison.get("v1", {}).get("report_sha256")
        == v1_expected["stage2_final_report.json"],
    )

    behavior = payload["development"]["v2_reuse"]["behavior_preservation_audit"]
    audit.require(
        "behavior_preservation_gate",
        behavior.get("model_training_codec_risk_bound_behavior_changed") is False
        and sha256_file(REPO_ROOT / behavior["path"]) == behavior["sha256"],
    )
    audit.require(
        "selected_learning_rates_reused_exactly",
        payload["development"]["selected_learning_rates"]
        == payload["development"]["v2_reuse"]["selected_learning_rates"],
    )

    result = audit.finish()
    result["protocol"] = reference
    result["confirmation_data_protocol"] = confirmation_reference
    result["execution_tag"] = tag
    result["execution_tag_commit"] = tag_commit
    result["artifact_manifest"] = {
        "path": str((final_root / "stage2_artifact_manifest.json").resolve()),
        "sha256": sha256_file(final_root / "stage2_artifact_manifest.json"),
        "artifact_count": manifest.get("artifact_count"),
        "mismatches": mismatches,
    }
    result["details"].update(
        {
            "formal_model_count": 10,
            "visual_diagnostic_model_count": 7,
            "gpu_uuids_used": sorted({row["gpu_uuid"] for row in assignments}),
            "v1_final_hashes": v1_expected,
            "best_mapping_root_selected": False,
            "development_rerun_required": False,
        }
    )
    write_json_atomic(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
