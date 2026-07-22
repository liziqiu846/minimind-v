#!/usr/bin/env python3
"""Run the frozen Phase 3 v5 formal evaluation with verified resumable shards."""

from __future__ import annotations

import argparse
import fcntl
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.artifact_validation import (
    validate_model_verification_receipt, validate_overlap_receipt, validate_prepared_data,
)
from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, canonical_json_bytes, fsync_directory,
    inventory_files, load_json_snapshot, load_jsonl_snapshot, sha256_bytes,
    snapshot_file, validate_disjoint_roots,
)
from experiments.phase3.nll_diagnostics import STRATA, validate_nll_store
from experiments.phase3.phase3_protocol import MODEL_ORDER
from experiments.phase3.phase3_protocol_v5 import (
    PROTOCOL_TAG_V5, Phase3ProtocolV5, frozen_repository_binding_v5, verify_code_manifest_v5,
)
from experiments.phase3.runner_common import build_metrics_summary, execute_evaluation
from experiments.phase3.status import (
    Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output,
)
from experiments.phase3.theory_metrics_v5 import aggregate_category_rows_v5, aggregate_rows_v5


SHARD_SIZE = 32


def shard_plan_v5(model_ids: list[str], filenames: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "shard_id": f"{model_id}__{start:04d}_{start + len(filenames[start:start + SHARD_SIZE]):04d}",
            "model_id": model_id,
            "start_index": start,
            "filenames": filenames[start:start + SHARD_SIZE],
        }
        for model_id in model_ids
        for start in range(0, len(filenames), SHARD_SIZE)
    ]


def validate_finalized_shard_v5(
    directory: Path, expected: dict[str, Any], run_config_sha256: str,
    protocol_sha256: str, code_manifest_sha256: str,
) -> dict[str, Any]:
    manifest = load_json_snapshot(directory / "shard_manifest.json", root=directory)
    required = {
        "schema_version", "metric_version", "shard_id", "run_config_sha256",
        "protocol_sha256", "code_manifest_sha256", "model_id", "filenames",
        "row_count", "image_group_count", "files", "exclusion_rule",
    }
    if set(manifest) != required or manifest.get("schema_version") != 1 or manifest.get("metric_version") != "v5":
        raise ValueError("v5 shard manifest schema mismatch")
    if (
        manifest["shard_id"] != expected["shard_id"]
        or manifest["model_id"] != expected["model_id"]
        or manifest["filenames"] != expected["filenames"]
        or manifest["run_config_sha256"] != run_config_sha256
        or manifest["protocol_sha256"] != protocol_sha256
        or manifest["code_manifest_sha256"] != code_manifest_sha256
    ):
        raise ValueError("v5 shard identity or binding mismatch")
    actual = inventory_files(directory, excluded=("shard_manifest.json",))
    if actual != manifest["files"]:
        raise ValueError("v5 shard file inventory mismatch")
    payload = directory / "payload"
    rows = load_jsonl_snapshot(payload / "row_level_results.jsonl", root=directory)
    groups = load_jsonl_snapshot(payload / "image_group_results.jsonl", root=directory)
    if (
        len(rows) != manifest["row_count"] or len(groups) != len(expected["filenames"])
        or manifest["image_group_count"] != len(groups)
        or [row.get("filename") for row in groups] != expected["filenames"]
        or any(row.get("model_id") != expected["model_id"] for row in rows + groups)
        or any(row.get("filename") not in expected["filenames"] for row in rows)
    ):
        raise ValueError("v5 shard result identity/count mismatch")
    run_manifest = load_json_snapshot(payload / "run_manifest.json", root=directory)
    if (
        run_manifest.get("metric_version") != "v5"
        or run_manifest.get("run_status") != "success"
        or run_manifest.get("ordered_model_ids") != [expected["model_id"]]
        or run_manifest.get("protocol_sha256") != protocol_sha256
        or run_manifest.get("phase3_code_manifest_sha256") != code_manifest_sha256
    ):
        raise ValueError("v5 shard run manifest mismatch")
    return manifest


def _approval_matches(approval: dict[str, Any], protocol_sha: str, code_sha: str) -> bool:
    return (
        set(approval) == {
            "approval_statement", "protocol_sha256", "code_manifest_sha256",
            "protocol_tag", "approved_by", "approval_date_utc",
        }
        and approval.get("approval_statement")
        == "Phase 3 v5 primary risks, model set, formal split, confidence allocation, compression accounting, and reporting rules are frozen. I approve formal execution."
        and approval.get("protocol_sha256") == protocol_sha
        and approval.get("code_manifest_sha256") == code_sha
        and approval.get("protocol_tag") == PROTOCOL_TAG_V5
        and isinstance(approval.get("approved_by"), str) and bool(approval["approved_by"].strip())
        and isinstance(approval.get("approval_date_utc"), str) and bool(approval["approval_date_utc"].strip())
    )


def _summary(values: list[float]) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("NLL diagnostic vector is invalid")
    return {
        "count": int(array.size), "minimum": float(np.min(array)),
        "mean": float(np.mean(array, dtype=np.float64)),
        "standard_deviation": float(np.std(array, dtype=np.float64)),
        "p50": float(np.quantile(array, 0.5)), "p90": float(np.quantile(array, 0.9)),
        "p95": float(np.quantile(array, 0.95)), "p99": float(np.quantile(array, 0.99)),
        "p99_5": float(np.quantile(array, 0.995)), "maximum": float(np.max(array)),
    }


def _persist_exact_json(path: Path, payload: Any, *, root: Path) -> None:
    expected = canonical_json_bytes(payload)
    if path.exists():
        if snapshot_file(path, root=root) != expected:
            raise ValueError(f"existing finalized JSON differs: {path.name}")
    else:
        atomic_write_bytes(path, expected, overwrite=False)


def _persist_exact_jsonl(path: Path, rows: list[dict[str, Any]], *, root: Path) -> None:
    expected = b"".join(canonical_json_bytes(row) for row in rows)
    if path.exists():
        if snapshot_file(path, root=root) != expected:
            raise ValueError(f"existing finalized JSONL differs: {path.name}")
    else:
        atomic_write_bytes(path, expected, overwrite=False)


def recompute_nll_diagnostics_v5(output: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    model_tokens: dict[str, list[float]] = {}
    model_means: dict[str, list[float]] = {}
    model_strata: dict[str, dict[str, dict[str, list[float]]]] = {}
    for shard in plan:
        model_id = shard["model_id"]
        root = output / "shards" / shard["shard_id"] / "payload" / "nll" / model_id
        arrays = validate_nll_store(root)
        index = load_jsonl_snapshot(root / "nll_index.jsonl", root=root)
        if len(index) != len(arrays["offsets"]) - 1:
            raise ValueError("NLL index length mismatch during formal reduction")
        for sequence, row in enumerate(index):
            start, end = int(arrays["offsets"][sequence]), int(arrays["offsets"][sequence + 1])
            values = arrays["values"][start:end].astype(np.float64)
            mean = float(np.mean(values, dtype=np.float64))
            stratum = STRATA[(int(row["condition_code"]), int(row["caption_role_code"]))]
            model_tokens.setdefault(model_id, []).extend(values.tolist())
            model_means.setdefault(model_id, []).append(mean)
            target = model_strata.setdefault(model_id, {}).setdefault(stratum, {"tokens": [], "means": []})
            target["tokens"].extend(values.tolist())
            target["means"].append(mean)
    models = {}
    for model_id in MODEL_ORDER:
        models[model_id] = {
            "token_level": _summary(model_tokens[model_id]),
            "caption_level": _summary(model_means[model_id]),
            "strata": {
                name: {"token_level": _summary(value["tokens"]), "caption_level": _summary(value["means"])}
                for name, value in sorted(model_strata[model_id].items())
            },
        }
    return {
        "schema_version": 1,
        "disclaimer": "未平滑 NLL 尾部诊断，仅为后续理论选型提供证据，不构成泛化保证。",
        "models": models,
    }


def _preflight(args: argparse.Namespace) -> tuple[Phase3ProtocolV5, list[str], dict[str, Any]]:
    protocol = Phase3ProtocolV5.load(args.protocol)
    protocol.require_frozen()
    if snapshot_file(args.protocol.with_suffix(".sha256")).decode("ascii") != protocol.raw_sha256 + "\n":
        raise ValueError("frozen v5 protocol sidecar mismatch")
    manifest = verify_code_manifest_v5(args.code_manifest)
    code_sha = sha256_bytes(canonical_json_bytes(manifest))
    if code_sha != protocol.payload["phase3_code_manifest_sha256"]:
        raise ValueError("v5 protocol/code manifest binding mismatch")
    binding = frozen_repository_binding_v5(protocol)
    approval = load_json_snapshot(args.approval)
    if not _approval_matches(approval, protocol.raw_sha256, code_sha):
        raise Phase3Blocked("formal_approval_invalid", "formal approval does not bind the frozen v5 protocol and code manifest")
    registry_receipt = validate_model_verification_receipt(
        args.verification_receipt, args.expected_registry, require_all=True,
    )
    if registry_receipt.get("overall_status") != "verified" or len(registry_receipt.get("models", [])) != 10:
        raise Phase3Blocked("models_not_all_verified", "exactly ten verified models are required")
    registry_raw = snapshot_file(args.expected_registry)
    if sha256_bytes(registry_raw) != protocol.payload["expected_model_registry_sha256"]:
        raise ValueError("expected-model registry differs from frozen v5 binding")
    prepared = validate_prepared_data(args.prepared_data_dir)
    if (
        prepared["data_manifest_sha256"] != protocol.payload["data_manifest_sha256"]
        or prepared["split_manifest_sha256"] != protocol.payload["split_manifest_sha256"]
    ):
        raise ValueError("prepared data differs from frozen v5 bindings")
    overlap = validate_overlap_receipt(
        args.overlap_audit_receipt,
        split_manifest_path=args.prepared_data_dir / "split_manifest.json",
        formal_image_manifest_path=args.prepared_data_dir / "coco_formal_images_manifest.jsonl",
    )
    filenames = overlap["certifying_names"]
    if len(filenames) != 1345 or sha256_bytes(("\n".join(filenames) + "\n").encode("utf-8")) != protocol.payload["certifying_formal_filenames_sha256"]:
        raise ValueError("certifying filename set/order mismatch")
    audit = load_json_snapshot(args.description_bits_audit)
    audit_raw = snapshot_file(args.description_bits_audit)
    if snapshot_file(args.description_bits_audit.with_suffix(".sha256")).decode("ascii") != sha256_bytes(audit_raw) + "\n":
        raise ValueError("description-bit audit sidecar mismatch")
    registry = load_json_snapshot(args.expected_registry)
    registry_by = {row["model_id"]: row for row in registry["models"]}
    audit_rows = audit.get("models", [])
    if (
        audit.get("overall_status") != "verified"
        or len(audit_rows) != 10
        or [row.get("model_id") for row in audit_rows] != list(MODEL_ORDER)
        or any(
            row.get("artifact_size_bytes") != registry_by[row["model_id"]]["artifact_size_bytes"]
            or row.get("sha256") != registry_by[row["model_id"]]["artifact_sha256"]
            or row.get("total_description_bits") != row.get("artifact_size_bytes") * 8 + 4
            for row in audit_rows
        )
    ):
        raise ValueError("complete MMS2 description-bit audit has not passed")
    return protocol, filenames, {
        "protocol_sha256": protocol.raw_sha256,
        "code_manifest_sha256": code_sha,
        "protocol_repository_commit": binding["protocol_repository_commit"],
        "protocol_tag": binding["protocol_tag"],
        "approval_sha256": sha256_bytes(snapshot_file(args.approval)),
        "expected_registry_sha256": sha256_bytes(registry_raw),
        "verification_receipt_sha256": sha256_bytes(snapshot_file(args.verification_receipt)),
        "data_manifest_sha256": sha256_bytes(snapshot_file(args.prepared_data_dir / "data_manifest.json")),
        "split_manifest_sha256": sha256_bytes(snapshot_file(args.prepared_data_dir / "split_manifest.json")),
        "overlap_receipt_sha256": sha256_bytes(snapshot_file(args.overlap_audit_receipt)),
        "description_bits_audit_sha256": sha256_bytes(audit_raw),
    }


def _finalize(
    args: argparse.Namespace, protocol: Phase3ProtocolV5, filenames: list[str],
    bindings: dict[str, Any], plan: list[dict[str, Any]], config_sha: str,
) -> dict[str, Any]:
    output = args.output_dir
    rows: list[dict[str, Any]] = []
    numerical: dict[str, int] = {}
    timings = []
    raw_root = output / "raw_rows"
    raw_root.mkdir(exist_ok=True)
    if raw_root.is_symlink() or not raw_root.is_dir():
        raise ValueError("formal raw_rows path is not a regular directory")
    for shard in plan:
        directory = output / "shards" / shard["shard_id"]
        validate_finalized_shard_v5(
            directory, shard, config_sha, bindings["protocol_sha256"], bindings["code_manifest_sha256"],
        )
        payload = directory / "payload"
        shard_rows_path = payload / "row_level_results.jsonl"
        rows.extend(load_jsonl_snapshot(shard_rows_path, root=directory))
        raw_target = raw_root / f"{shard['shard_id']}.jsonl"
        shard_raw = snapshot_file(shard_rows_path, root=directory)
        if raw_target.exists():
            if snapshot_file(raw_target, root=output) != shard_raw:
                raise ValueError("existing formal raw-row shard differs from verified payload")
        else:
            atomic_write_bytes(raw_target, shard_raw, overwrite=False)
        shard_numerical = load_json_snapshot(payload / "numerical_diagnostics.json", root=directory)
        for key, value in shard_numerical.items():
            numerical[key] = numerical.get(key, 0) + int(value)
        timings.append(load_json_snapshot(payload / "timing.json", root=directory))
    expected_numerical = {
        "token_brier_below_zero_count", "token_brier_above_two_count",
        "caption_clip_low_count", "caption_clip_high_count", "nan_inf_count",
    }
    if (
        set(numerical) != expected_numerical
        or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in numerical.values())
        or any(numerical[key] != 0 for key in ("caption_clip_low_count", "caption_clip_high_count", "nan_inf_count"))
    ):
        raise ValueError("formal numerical diagnostics failed")
    order = {model_id: index for index, model_id in enumerate(MODEL_ORDER)}
    rows.sort(key=lambda row: (order[row["model_id"]], int(row["row_index"])))
    groups = aggregate_rows_v5(rows)
    groups.sort(key=lambda row: (order[row["model_id"]], row["filename"].encode("utf-8")))
    if len(groups) != 13450:
        raise ValueError("formal v5 must produce exactly 13,450 model-image groups")
    category = aggregate_category_rows_v5(rows)
    registry = load_json_snapshot(args.expected_registry)
    overall = build_metrics_summary("formal", list(MODEL_ORDER), groups, registry, "v5")
    fixed = {
        "schema_version": 1, "selection_status": overall["selection_status"],
        "simultaneous_coverage_claim": False,
        "models": [{"model_id": row["model_id"], "bounds": row["fixed_model_bounds"]} for row in overall["models"]],
    }
    compression = {
        "schema_version": 1, "selection_status": overall["selection_status"],
        "simultaneous_coverage_claim": False,
        "models": [{"model_id": row["model_id"], "bounds": row["compression_bounds"]} for row in overall["models"]],
    }
    nll = recompute_nll_diagnostics_v5(output, plan)
    receipt = {
        "schema_version": 1, "metric_version": "v5", "status": "success",
        "post_hoc": True, "simultaneous_coverage_claim": False,
        "model_count": 10, "certifying_unique_images": 1345,
        "model_image_group_count": len(groups), "formal_shard_count": len(plan),
        "ordered_model_ids": list(MODEL_ORDER),
        "ordered_filenames_sha256": sha256_bytes(("\n".join(filenames) + "\n").encode("utf-8")),
        "shard_elapsed_seconds_total": float(sum(float(row["elapsed_seconds"]) for row in timings)),
        "max_memory_allocated_bytes": max(int(row["max_memory_allocated_bytes"]) for row in timings),
        "numerical_diagnostics": numerical,
        **bindings,
    }
    status = {
        "schema_version": 1, "status": "success", "completed_shards": len(plan),
        "total_shards": len(plan), "model_image_group_count": len(groups),
    }
    _persist_exact_jsonl(output / "image_groups.jsonl", groups, root=output)
    _persist_exact_json(output / "overall_summary.json", overall, root=output)
    _persist_exact_json(output / "category_summary.json", {"schema_version": 1, "results": category}, root=output)
    _persist_exact_json(output / "fixed_model_bounds.json", fixed, root=output)
    _persist_exact_json(output / "compression_bounds.json", compression, root=output)
    _persist_exact_json(output / "nll_diagnostics.json", nll, root=output)
    _persist_exact_json(output / "run_receipt.json", receipt, root=output)
    _persist_exact_json(output / "status.json", status, root=output)
    atomic_write_json(output / "resume_state.json", {
        "schema_version": 1, "metric_version": "v5", "run_config_sha256": config_sha,
        "completed_shards": [row["shard_id"] for row in plan],
        "total_shards": len(plan), "status": "success",
    })
    return {"run_dir": str(output), "image_groups": len(groups), "shards": len(plan)}


def run_formal(args: argparse.Namespace) -> dict[str, Any]:
    validate_disjoint_roots(
        input_roots=[
            args.protocol.parent, args.code_manifest.parent, args.expected_registry.parent,
            args.verification_receipt.parent, args.prepared_data_dir, args.coco_root,
            args.stage2_artifact_root, args.stage2_protocol.parent,
            args.overlap_audit_receipt.parent, args.approval.parent, args.description_bits_audit.parent,
        ],
        output_roots=[args.output_dir, args.status_output.parent],
        forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2]],
    )
    protocol, filenames, bindings = _preflight(args)
    output = args.output_dir
    existing_success = False
    if (output / "status.json").is_file():
        status = load_json_snapshot(output / "status.json", root=output)
        if status.get("status") != "success":
            raise ValueError("existing formal status is not a completed success")
        existing_success = True
    output.mkdir(parents=True, exist_ok=True)
    (output / "shards").mkdir(exist_ok=True)
    (output / ".tmp").mkdir(exist_ok=True)
    lock_path = output / ".phase3.lock"
    lock = lock_path.open("a+b")
    try:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Phase3Blocked("formal_lock_busy", str(lock_path)) from error
        plan = shard_plan_v5(list(MODEL_ORDER), filenames)
        if len(plan) != 430:
            raise AssertionError("formal v5 shard plan must contain exactly 430 shards")
        config = {
            "schema_version": 1, "metric_version": "v5", "model_ids": list(MODEL_ORDER),
            "filenames": filenames, "shard_size_unique_images": SHARD_SIZE,
            "global_seed": 3407, "item_batch_size": 1, "device": args.device, **bindings,
        }
        config_sha = sha256_bytes(canonical_json_bytes(config))
        config_path = output / "formal_run_config.json"
        if config_path.exists():
            if load_json_snapshot(config_path, root=output) != config:
                raise ValueError("existing formal run config differs")
        else:
            atomic_write_json(config_path, config, overwrite=False)
        if existing_success:
            result = _finalize(args, protocol, filenames, bindings, plan, config_sha)
            result["resumed_completed_run"] = True
            return result
        completed: list[str] = []
        for shard in plan:
            destination = output / "shards" / shard["shard_id"]
            if destination.exists():
                validate_finalized_shard_v5(
                    destination, shard, config_sha, bindings["protocol_sha256"], bindings["code_manifest_sha256"],
                )
                completed.append(shard["shard_id"])
                continue
            temporary = Path(tempfile.mkdtemp(prefix=f"{shard['shard_id']}.", dir=output / ".tmp"))
            try:
                payload = temporary / "payload"
                result = execute_evaluation(
                    run_mode="formal", model_ids=[shard["model_id"]], filenames=shard["filenames"],
                    protocol_path=args.protocol, expected_registry_path=args.expected_registry,
                    verification_receipt_path=args.verification_receipt,
                    prepared_data_dir=args.prepared_data_dir, coco_root=args.coco_root,
                    artifact_root=args.stage2_artifact_root, output_dir=payload,
                    device=args.device, item_batch_size=args.item_batch_size,
                    stage2_protocol_path=args.stage2_protocol,
                    overlap_audit_receipt_path=args.overlap_audit_receipt, metric_version="v5",
                )
                manifest = {
                    "schema_version": 1, "metric_version": "v5", "shard_id": shard["shard_id"],
                    "run_config_sha256": config_sha, "protocol_sha256": bindings["protocol_sha256"],
                    "code_manifest_sha256": bindings["code_manifest_sha256"],
                    "model_id": shard["model_id"], "filenames": shard["filenames"],
                    "row_count": result["row_results"], "image_group_count": result["image_groups"],
                    "files": inventory_files(temporary, excluded=("shard_manifest.json",)),
                    "exclusion_rule": "only shard_manifest.json is excluded",
                }
                atomic_write_json(temporary / "shard_manifest.json", manifest, overwrite=False)
                os.rename(temporary, destination)
                fsync_directory(output / "shards")
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)
            validate_finalized_shard_v5(
                destination, shard, config_sha, bindings["protocol_sha256"], bindings["code_manifest_sha256"],
            )
            completed.append(shard["shard_id"])
            atomic_write_json(output / "resume_state.json", {
                "schema_version": 1, "metric_version": "v5", "run_config_sha256": config_sha,
                "completed_shards": completed, "total_shards": len(plan), "status": "in_progress",
            })
        return _finalize(args, protocol, filenames, bindings, plan, config_sha)
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    for name in (
        "protocol", "code_manifest", "expected_registry", "verification_receipt",
        "prepared_data_dir", "coco_root", "stage2_artifact_root", "output_dir",
        "overlap_audit_receipt", "approval", "description_bits_audit",
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--stage2-protocol", type=Path, default=Path("experiments/stage2_protocol_v2.json"))
    parser.add_argument("--device", required=True)
    parser.add_argument("--item-batch-size", type=int, required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation():
        try:
            return run_formal(args)
        except Phase3Blocked:
            raise
        except FileNotFoundError as error:
            raise Phase3Blocked("formal_resource_missing", str(error)) from error
        except (ValueError, RuntimeError, OSError) as error:
            raise Phase3HardFailure("formal_v5_failure", str(error)) from error

    return execute_with_status("run_phase3_formal_v5", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
