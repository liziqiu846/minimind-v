#!/usr/bin/env python3
"""Audit the immutable Stage 2 v1 evidence without changing its artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import (  # noqa: E402
    DEFAULT_FROZEN,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM  # noqa: E402
from model.model_vlm import MiniMindVLM, VLMConfig  # noqa: E402


DEFAULT_FINAL_DIR = REPO_ROOT / "experiments/runs/stage2/final"
DEFAULT_FORMAL_ROOT = REPO_ROOT / "experiments/runs/stage2/formal"
DEFAULT_FORMAL_SUMMARY = REPO_ROOT / "experiments/runs/stage2/formal_summary.json"
DEFAULT_DIAGNOSTICS = REPO_ROOT / "experiments/runs/stage2/formal_diagnostics.json"


def run_git(*arguments: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--final-dir", type=Path, default=DEFAULT_FINAL_DIR)
    parser.add_argument("--formal-root", type=Path, default=DEFAULT_FORMAL_ROOT)
    parser.add_argument("--formal-summary", type=Path, default=DEFAULT_FORMAL_SUMMARY)
    parser.add_argument("--diagnostics", type=Path, default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def instantiate_before_initial_load(model_group: str, protocol: Stage2Protocol):
    model_config = protocol.payload["model"]
    common = dict(
        hidden_size=model_config["hidden_size"],
        num_hidden_layers=model_config["num_hidden_layers"],
        vocab_size=model_config["vocab_size"],
        use_moe=model_config["use_moe"],
        max_position_embeddings=protocol.payload["training"]["max_sequence_length"],
    )
    if model_group == "M0":
        return MiniMindForCausalLM(MiniMindConfig(**common))
    config = VLMConfig(
        **common,
        image_hidden_size=model_config["image_hidden_size"],
        image_token_len=model_config["image_token_count"],
        projector_type="subspace" if model_group == "M1" else "stage2_base",
        subspace_dim=4096,
        subspace_seed=model_config["projector_base"]["source_seed_layer_1"],
        subspace_train_norm=False,
    )
    return MiniMindVLM(
        config=config,
        vision_model_path=str(protocol.asset_path("vision_encoder")),
    )


def audit_model_loading(protocol: Stage2Protocol) -> dict[str, Any]:
    initial_path = protocol.asset_path("initial_llm")
    initial = torch.load(initial_path, map_location="cpu", weights_only=True)
    groups = []
    for model_group in ("M0", "M1", "M2", "M3"):
        model = instantiate_before_initial_load(model_group, protocol)
        incompatible = model.load_state_dict(initial, strict=False)
        missing = list(incompatible.missing_keys)
        unexpected = list(incompatible.unexpected_keys)
        allowed_prefixes = () if model_group == "M0" else (
            "vision_encoder.",
            "vision_proj.",
        )
        disallowed_missing = [
            name for name in missing if not name.startswith(allowed_prefixes)
        ]
        model_state = model.state_dict()
        absent_initial_keys = [name for name in initial if name not in model_state]
        tensor_mismatches = [
            name
            for name, value in initial.items()
            if name in model_state
            and not torch.equal(
                model_state[name].detach().cpu(), value.detach().cpu()
            )
        ]
        passed = not (
            unexpected
            or disallowed_missing
            or absent_initial_keys
            or tensor_mismatches
        )
        groups.append(
            {
                "model_group": model_group,
                "allowed_missing_prefixes": list(allowed_prefixes),
                "missing_keys": missing,
                "missing_key_count": len(missing),
                "unexpected_keys": unexpected,
                "disallowed_missing_keys": disallowed_missing,
                "initial_keys_absent_from_model": absent_initial_keys,
                "loaded_initial_tensor_mismatches": tensor_mismatches,
                "language_or_lm_head_missing": [
                    name
                    for name in missing
                    if name == "lm_head.weight" or name.startswith("model.")
                ],
                "status": "passed" if passed else "failed",
            }
        )
        del model
    passed = all(row["status"] == "passed" for row in groups)
    return {
        "schema_version": 1,
        "audit_id": "minimind-v-stage2-v1-model-load-audit",
        "status": "passed" if passed else "failed",
        "protocol": protocol.reference(),
        "initial_llm": {
            "path": str(initial_path.resolve()),
            "sha256": sha256_file(initial_path),
            "state_key_count": len(initial),
        },
        "criterion": (
            "every initial LLM tensor loads exactly; no unexpected keys; M0 has no "
            "missing keys; VLM missing keys are limited to separately constructed "
            "vision_encoder and vision_proj modules"
        ),
        "groups": groups,
    }


def audit_artifact_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    mismatches = []
    for item in manifest["artifacts"]:
        artifact = Path(item["path"])
        if not artifact.exists():
            mismatches.append({"path": str(artifact), "reason": "missing"})
            continue
        actual_bytes = artifact.stat().st_size
        actual_sha256 = sha256_file(artifact)
        if actual_bytes != item["bytes"] or actual_sha256 != item["sha256"]:
            mismatches.append(
                {
                    "path": str(artifact),
                    "reason": "size_or_sha256_mismatch",
                    "expected_bytes": item["bytes"],
                    "actual_bytes": actual_bytes,
                    "expected_sha256": item["sha256"],
                    "actual_sha256": actual_sha256,
                }
            )
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "declared_artifact_count": manifest["artifact_count"],
        "observed_artifact_count": len(manifest["artifacts"]),
        "mismatches": mismatches,
        "status": (
            "passed"
            if manifest["artifact_count"] == len(manifest["artifacts"])
            and not mismatches
            else "failed"
        ),
    }


def audit_integrity(
    protocol: Stage2Protocol,
    final_dir: Path,
    formal_root: Path,
    formal_summary_path: Path,
    diagnostics_path: Path,
) -> dict[str, Any]:
    protocol.verify_immutable_inputs()
    report_path = final_dir / "stage2_final_report.json"
    report_md_path = final_dir / "stage2_final_report.md"
    manifest_path = final_dir / "stage2_artifact_manifest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = json.loads(formal_summary_path.read_text(encoding="utf-8"))
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    progress_path = formal_root / "pipeline_progress.json"
    progress = json.loads(progress_path.read_text(encoding="utf-8"))

    tag_name = protocol.payload["git"]["annotated_tag"]
    tag_type = str(run_git("cat-file", "-t", tag_name)).strip()
    tag_commit = str(run_git("rev-parse", f"{tag_name}^{{}}")).strip()
    implementation_commit = protocol.payload["git"]["frozen_implementation_commit"]
    changed_paths = [
        line.split("\t", 1)
        for line in str(
            run_git("diff", "--name-status", f"{implementation_commit}..{tag_commit}")
        ).splitlines()
        if line
    ]
    expected_changed_paths = [["A", "experiments/stage2_protocol.json"]]

    implementation_mismatches = []
    for relative, expected in protocol.payload["implementation"][
        "implementation_file_sha256"
    ].items():
        blob = run_git("show", f"{implementation_commit}:{relative}", binary=True)
        assert isinstance(blob, bytes)
        actual = sha256_bytes(blob)
        if actual != expected:
            implementation_mismatches.append(
                {"path": relative, "expected_sha256": expected, "actual_sha256": actual}
            )

    protocol_blob = run_git(
        "show", f"{tag_commit}:experiments/stage2_protocol.json", binary=True
    )
    assert isinstance(protocol_blob, bytes)
    protocol_blob_sha256 = sha256_bytes(protocol_blob)
    artifact_manifest = audit_artifact_manifest(manifest_path)
    confirmation_train = protocol.verify_confirmation_data(
        protocol.confirmation_directory() / "train.parquet", "train"
    )
    confirmation_validation = protocol.verify_confirmation_data(
        protocol.confirmation_directory() / "validation.parquet", "validation"
    )
    tracked_status = str(
        run_git("status", "--short", "--untracked-files=no")
    ).splitlines()

    checks = {
        "annotated_tag_object": tag_type == "tag",
        "tag_commit_matches_final_report": tag_commit == report["git_commit"],
        "tag_listed_in_final_report": tag_name in report["git_tags_at_report_commit"],
        "protocol_blob_matches_report_reference": (
            protocol_blob_sha256 == report["protocol"]["protocol_sha256"]
            == protocol.sha256
        ),
        "implementation_to_protocol_diff_is_only_protocol": (
            changed_paths == expected_changed_paths
        ),
        "implementation_blobs_match_protocol_hashes": not implementation_mismatches,
        "artifact_manifest_replay_passed": artifact_manifest["status"] == "passed",
        "formal_summary_complete": summary.get("formal_model_count") == 10,
        "diagnostics_complete": len(diagnostics.get("models", [])) == 7,
        "pipeline_complete": (
            progress.get("status") == "complete"
            and progress.get("completed_runs") == 10
        ),
        "no_formal_failure_receipts": not (
            list(formal_root.rglob("failure_receipt.json"))
            or list(formal_root.glob("pipeline_failure.json"))
        ),
        "tracked_worktree_clean_at_audit": not tracked_status,
    }
    passed = all(checks.values())
    return {
        "schema_version": 1,
        "audit_id": "minimind-v-stage2-v1-integrity-audit",
        "status": "passed" if passed else "failed",
        "protocol": protocol.reference(),
        "git": {
            "tag": tag_name,
            "tag_object_type": tag_type,
            "tag_commit": tag_commit,
            "final_report_commit": report["git_commit"],
            "frozen_implementation_commit": implementation_commit,
            "changed_paths_from_implementation_to_tag": changed_paths,
            "tracked_status_at_audit": tracked_status,
        },
        "implementation_hash_mismatches": implementation_mismatches,
        "final_files": {
            "report_json": {
                "path": str(report_path.resolve()),
                "sha256": sha256_file(report_path),
            },
            "report_markdown": {
                "path": str(report_md_path.resolve()),
                "sha256": sha256_file(report_md_path),
            },
            "formal_summary": {
                "path": str(formal_summary_path.resolve()),
                "sha256": sha256_file(formal_summary_path),
            },
            "diagnostics": {
                "path": str(diagnostics_path.resolve()),
                "sha256": sha256_file(diagnostics_path),
            },
            "pipeline_progress": {
                "path": str(progress_path.resolve()),
                "sha256": sha256_file(progress_path),
            },
        },
        "artifact_manifest_replay": artifact_manifest,
        "confirmation_data": {
            "train": confirmation_train,
            "validation": confirmation_validation,
        },
        "checks": checks,
    }


def audit_sampling_assumption(protocol: Stage2Protocol) -> dict[str, Any]:
    builder_path = REPO_ROOT / "experiments/build_stage2_dataset.py"
    source = builder_path.read_text(encoding="utf-8")
    evidence = {
        "deduplicates_exact_images_before_selection": "if image_sha in seen:" in source,
        "candidate_rank_depends_on_image_value": (
            "candidate_rank(seed, image_sha)" in source
        ),
        "selected_phash_enters_forbidden_set": "forbidden.add(phash_value)" in source,
        "protocol_requires_pairwise_selected_phash_distance": (
            "already-selected image"
            in protocol.payload["data"]["phash"]["acceptance_rule"]
        ),
        "protocol_requires_exact_unique_and_disjoint": (
            any(
                "internally unique and disjoint" in requirement
                for requirement in protocol.payload["tests"]["data"]
            )
        ),
    }
    all_present = all(evidence.values())
    return {
        "schema_version": 1,
        "audit_id": "minimind-v-stage2-v1-sampling-assumption-audit",
        "status": (
            "theorem_independence_not_established" if all_present else "audit_incomplete"
        ),
        "severity": "critical_for_strict_certificate",
        "protocol": protocol.reference(),
        "implementation": {
            "path": str(builder_path.resolve()),
            "sha256": sha256_file(builder_path),
        },
        "evidence": evidence,
        "finding": (
            "The selected image units are adaptively coupled because every selected "
            "pHash changes eligibility of later candidates. Exact-value deduplication "
            "and value-dependent top-k selection also do not implement independent "
            "draws from a declared distribution. Therefore the v1 sample count cannot "
            "be used as independent_train_samples under Equation (1) without an "
            "additional theorem."
        ),
        "unaffected_observations": [
            "training and validation risks as computed on the frozen v1 datasets",
            "MMS2 archive byte lengths and clean decode hashes",
            "all predeclared M2 versus M3 computed-value comparisons",
            "secondary correct, paired-shuffled, and absent-image diagnostics",
        ],
        "invalid_without_additional_theory": [
            "strict 95 percent population generalization certificate",
            "treating all 10000 v1 training images as independent samples in Equation (1)",
            "unqualified non-vacuous certificate language for the ten v1 models",
        ],
        "required_v2_repair": (
            "declare a fixed eligible unit distribution and draw training and validation "
            "units independently with replacement; history filtering may be fixed, but "
            "no draw may change later-draw eligibility"
        ),
    }


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    if protocol.payload["protocol_id"] != "minimind-v-stage2-joint-compression-v1":
        raise ValueError("this audit is only for the frozen Stage 2 v1 protocol")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "model_load": args.output_dir / "model_load_audit.json",
        "integrity": args.output_dir / "integrity_audit.json",
        "sampling": args.output_dir / "sampling_assumption_audit.json",
        "summary": args.output_dir / "audit_summary.json",
    }
    if any(path.exists() for path in outputs.values()):
        raise FileExistsError("one or more v1 audit outputs already exist")

    model_load = audit_model_loading(protocol)
    write_json_atomic(outputs["model_load"], model_load)
    integrity = audit_integrity(
        protocol,
        args.final_dir,
        args.formal_root,
        args.formal_summary,
        args.diagnostics,
    )
    write_json_atomic(outputs["integrity"], integrity)
    sampling = audit_sampling_assumption(protocol)
    write_json_atomic(outputs["sampling"], sampling)
    summary = {
        "schema_version": 1,
        "audit_id": "minimind-v-stage2-v1-closeout-audit",
        "status": (
            "empirical_results_preserved_certificate_exploratory"
            if model_load["status"] == "passed"
            and integrity["status"] == "passed"
            and sampling["status"] == "theorem_independence_not_established"
            else "requires_investigation"
        ),
        "protocol": protocol.reference(),
        "receipts": {
            name: {"path": str(path.resolve()), "sha256": sha256_file(path)}
            for name, path in outputs.items()
            if name != "summary"
        },
        "conclusion": (
            "v1 model loading and artifact integrity passed, but the formal sampling "
            "independence premise was not established. Preserve v1 empirical and "
            "compression observations; label its bound values exploratory; use v2 for "
            "strict certificate claims."
        ),
    }
    write_json_atomic(outputs["summary"], summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
