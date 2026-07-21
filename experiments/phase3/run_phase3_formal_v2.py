#!/usr/bin/env python3
"""Formal runner with exhaustive, side-effect-free preflight gates."""

from __future__ import annotations

import argparse
import fcntl
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.aggregate_by_image import aggregate_rows
from experiments.phase3.artifact_validation import (
    validate_model_verification_receipt, validate_overlap_receipt, validate_prepared_data,
)
from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, atomic_write_jsonl, canonical_json_bytes,
    fsync_directory, inventory_files, load_json_snapshot, load_jsonl_snapshot, sha256_bytes, snapshot_file,
    validate_disjoint_roots,
)
from experiments.phase3.nll_diagnostics import validate_nll_store, write_nll_store
from experiments.phase3.phase3_protocol import (
    PROTOCOL_TAG, REPO_ROOT, STAGE2_REFERENCE_COMMIT, Phase3Protocol, verify_code_manifest,
)
from experiments.phase3.runner_common import (
    NLL_DISCLAIMER, _copy_snapshot, _degenerate_sensitivity, _environment,
    build_metrics_summary, execute_evaluation,
)
from experiments.phase3.stage2_adapter_loader import MODELS, verify_stage2_source_integrity
from experiments.phase3.status import Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output


def shard_plan(model_ids: list[str], filenames: list[str], shard_size: int = 32) -> list[dict[str, Any]]:
    plan = []
    for model_id in model_ids:
        for start in range(0, len(filenames), shard_size):
            selected = filenames[start : start + shard_size]
            plan.append(
                {
                    "shard_id": f"{model_id}__{start:04d}_{start + len(selected):04d}",
                    "model_id": model_id,
                    "start_index": start,
                    "filenames": selected,
                }
            )
    return plan


def validate_resume_state(payload: dict[str, Any], expected_hashes: dict[str, Any], plan: list[dict[str, Any]]) -> None:
    required = {
        "schema_version", "run_config_sha256", "protocol_sha256",
        "phase3_source_commit", "protocol_repository_commit", "code_manifest_sha256",
        "expected_registry_sha256", "verification_receipt_sha256", "data_manifest_sha256",
        "split_manifest_sha256", "overlap_receipt_sha256", "approval_sha256",
        "ordered_model_ids", "ordered_filenames_sha256", "shard_size_unique_images",
        "shard_plan", "completed_shards", "run_status",
    }
    if set(payload) != required or payload.get("schema_version") != 1 or payload.get("shard_size_unique_images") != 32:
        raise ValueError("resume state schema mismatch")
    for key, value in expected_hashes.items():
        if payload.get(key) != value:
            raise ValueError(f"resume hash mismatch: {key}")
    if payload.get("shard_plan") != plan:
        raise ValueError("resume shard plan mismatch")
    plan_ids = [row["shard_id"] for row in plan]
    completed = payload.get("completed_shards")
    if (
        not isinstance(completed, list)
        or completed != [shard_id for shard_id in plan_ids if shard_id in set(completed)]
        or len(completed) != len(set(completed))
        or payload.get("run_status") not in ("in_progress", "success")
        or (payload.get("run_status") == "success" and completed != plan_ids)
    ):
        raise ValueError("resume completion ledger is invalid")


def validate_finalized_shard(directory: Path, expected: dict[str, Any], run_config_sha256: str) -> dict[str, Any]:
    manifest_path = directory / "shard_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("finalized shard has no manifest")
    manifest = load_json_snapshot(manifest_path, root=directory)
    required = {
        "schema_version", "shard_id", "run_config_sha256", "model_id", "filenames",
        "row_count", "image_group_count", "files", "exclusion_rule",
    }
    if set(manifest) != required or manifest["schema_version"] != 1:
        raise ValueError("shard manifest schema mismatch")
    if (
        manifest["shard_id"] != expected["shard_id"]
        or manifest["model_id"] != expected["model_id"]
        or manifest["filenames"] != expected["filenames"]
        or manifest["run_config_sha256"] != run_config_sha256
    ):
        raise ValueError("shard identity/config mismatch")
    actual = inventory_files(directory, excluded=("shard_manifest.json",))
    if actual != manifest["files"]:
        raise ValueError("shard file inventory mismatch")
    forbidden_final_outputs = {
        "payload/metrics_summary.json",
        "payload/degenerate_sensitivity_summary.json",
    }
    if forbidden_final_outputs & {row["relative_path"] for row in actual}:
        raise ValueError("formal shard contains a premature final summary")
    if int(manifest["row_count"]) <= 0 or int(manifest["image_group_count"]) != len(expected["filenames"]):
        raise ValueError("shard result counts are invalid")
    payload_root = directory / "payload"
    rows = load_jsonl_snapshot(payload_root / "row_level_results.jsonl", root=directory)
    groups = load_jsonl_snapshot(payload_root / "image_group_results.jsonl", root=directory)
    if (
        len(rows) != manifest["row_count"]
        or len(groups) != manifest["image_group_count"]
        or any(row.get("model_id") != expected["model_id"] or row.get("filename") not in expected["filenames"] for row in rows)
        or [row.get("filename") for row in groups] != expected["filenames"]
        or any(row.get("model_id") != expected["model_id"] for row in groups)
    ):
        raise ValueError("shard result payload identity/count mismatch")
    run_manifest = load_json_snapshot(payload_root / "run_manifest.json", root=directory)
    payload_inventory = inventory_files(payload_root, excluded=("run_manifest.json",))
    if (
        run_manifest.get("run_mode") != "formal"
        or run_manifest.get("run_status") != "success"
        or run_manifest.get("ordered_model_ids") != [expected["model_id"]]
        or run_manifest.get("ordered_filenames_sha256")
        != sha256_bytes(("\n".join(expected["filenames"]) + "\n").encode("utf-8"))
        or run_manifest.get("row_result_count") != len(rows)
        or run_manifest.get("image_group_result_count") != len(groups)
        or run_manifest.get("files") != payload_inventory
    ):
        raise ValueError("shard payload run manifest mismatch")
    return manifest


def _formal_bindings(args: argparse.Namespace, protocol: Phase3Protocol) -> dict[str, Any]:
    authority = args.code_manifest.parent / "phase3_stage2_authority_manifest_v2.json"
    peeled = _git("rev-parse", f"refs/tags/{PROTOCOL_TAG}^{{commit}}")
    if peeled[0] != 0:
        raise ValueError("formal protocol tag cannot be resolved")
    tag_object = _git("rev-parse", f"refs/tags/{PROTOCOL_TAG}")
    if tag_object[0] != 0:
        raise ValueError("formal annotated tag object cannot be resolved")
    files = {
        "phase3_code_manifest_sha256": args.code_manifest,
        "expected_registry_sha256": args.expected_registry,
        "verification_receipt_sha256": args.verification_receipt,
        "data_manifest_sha256": args.prepared_data_dir / "data_manifest.json",
        "split_manifest_sha256": args.split_manifest,
        "overlap_receipt_sha256": args.overlap_audit_receipt,
        "approval_sha256": args.approval,
    }
    result = {key: sha256_bytes(snapshot_file(path)) for key, path in files.items()}
    result.update(
        {
            "protocol_sha256": protocol.raw_sha256,
            "phase3_source_commit": protocol.payload["phase3_source_commit"],
            "protocol_repository_commit": peeled[1],
            "protocol_tag_object": tag_object[1],
            "stage2_authority_manifest_sha256": sha256_bytes(snapshot_file(authority)),
        }
    )
    return result


def _formal_run_config(
    args: argparse.Namespace,
    protocol: Phase3Protocol,
    model_ids: list[str],
    filenames: list[str],
    bindings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_mode": "formal",
        "model_ids": model_ids,
        "filenames": filenames,
        "ordered_filenames_sha256": sha256_bytes(("\n".join(filenames) + "\n").encode("utf-8")),
        "global_seed": 3407,
        "item_batch_size": 1,
        "device": args.device,
        "stage2_artifact_root": str(args.stage2_artifact_root.resolve()),
        "coco_root": str(args.coco_root.resolve()),
        **bindings,
    }


def _resume_payload(
    run_config_sha256: str,
    config: dict[str, Any],
    bindings: dict[str, Any],
    plan: list[dict[str, Any]],
    completed: list[str],
    status: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_config_sha256": run_config_sha256,
        "protocol_sha256": bindings["protocol_sha256"],
        "phase3_source_commit": bindings["phase3_source_commit"],
        "protocol_repository_commit": bindings["protocol_repository_commit"],
        "code_manifest_sha256": bindings["phase3_code_manifest_sha256"],
        "expected_registry_sha256": bindings["expected_registry_sha256"],
        "verification_receipt_sha256": bindings["verification_receipt_sha256"],
        "data_manifest_sha256": bindings["data_manifest_sha256"],
        "split_manifest_sha256": bindings["split_manifest_sha256"],
        "overlap_receipt_sha256": bindings["overlap_receipt_sha256"],
        "approval_sha256": bindings["approval_sha256"],
        "ordered_model_ids": config["model_ids"],
        "ordered_filenames_sha256": config["ordered_filenames_sha256"],
        "shard_size_unique_images": 32,
        "shard_plan": plan,
        "completed_shards": completed,
        "run_status": status,
    }


def _read_jsonl(path: Path, root: Path) -> list[dict[str, Any]]:
    rows = load_jsonl_snapshot(path, root=root)
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"JSONL rows must be objects: {path.name}")
    return rows


def _finalize_formal_run(
    args: argparse.Namespace,
    protocol: Phase3Protocol,
    config: dict[str, Any],
    bindings: dict[str, Any],
    plan: list[dict[str, Any]],
    run_config_sha256: str,
    started: float,
) -> dict[str, Any]:
    output = args.output_dir
    if (output / "run_manifest.json").exists():
        manifest = load_json_snapshot(output / "run_manifest.json", root=output)
        if manifest.get("run_status") != "success":
            raise ValueError("existing final run manifest is not successful")
        return {"run_dir": str(output), "resumed_completed_run": True}
    model_ids = config["model_ids"]
    model_order = {model_id: index for index, model_id in enumerate(model_ids)}
    rows: list[dict[str, Any]] = []
    nll_entries: dict[str, list[dict[str, Any]]] = {model_id: [] for model_id in model_ids}
    reverse_condition = {0: "correct", 1: "none", 2: "lm_only"}
    reverse_role = {0: "pos1", 1: "pos2", 2: "negative"}
    numerical: dict[str, int] = {}
    shard_timings: list[dict[str, Any]] = []
    for shard in plan:
        validate_finalized_shard(
            output / "shards" / shard["shard_id"], shard, run_config_sha256
        )
        root = output / "shards" / shard["shard_id"] / "payload"
        rows.extend(_read_jsonl(root / "row_level_results.jsonl", root))
        shard_numerical = load_json_snapshot(root / "numerical_diagnostics.json", root=root)
        for key, value in shard_numerical.items():
            numerical[key] = numerical.get(key, 0) + int(value)
        shard_timings.append(load_json_snapshot(root / "timing.json", root=root))
        model_id = shard["model_id"]
        nll_root = root / "nll" / model_id
        arrays = validate_nll_store(nll_root)
        index_rows = _read_jsonl(nll_root / "nll_index.jsonl", root)
        for index, metadata in enumerate(index_rows):
            start, end = int(arrays["offsets"][index]), int(arrays["offsets"][index + 1])
            nll_entries[model_id].append(
                {
                    "row_index": int(metadata["row_index"]),
                    "row_key": metadata["row_key"],
                    "model_id": model_id,
                    "filename": metadata["filename"],
                    "category": metadata["category"],
                    "numeric_id": int(metadata["numeric_id"]),
                    "condition": reverse_condition[int(metadata["condition_code"])],
                    "caption_role": reverse_role[int(metadata["caption_role_code"])],
                    "values": arrays["values"][start:end].copy(),
                }
            )
    rows.sort(key=lambda row: (model_order[row["model_id"]], int(row["row_index"])))
    final_temp = Path(tempfile.mkdtemp(prefix="formal-final.", dir=output / ".tmp"))
    try:
        atomic_write_jsonl(final_temp / "row_level_results.jsonl", rows)
        persisted_rows = _read_jsonl(final_temp / "row_level_results.jsonl", final_temp)
        groups = aggregate_rows(persisted_rows)
        groups.sort(key=lambda row: (model_order[row["model_id"]], row["filename"].encode("utf-8")))
        atomic_write_jsonl(final_temp / "image_group_results.jsonl", groups)
        persisted_groups = _read_jsonl(final_temp / "image_group_results.jsonl", final_temp)
        registry = load_json_snapshot(args.expected_registry)
        metrics = build_metrics_summary("formal", model_ids, persisted_groups, registry)
        atomic_write_json(final_temp / "metrics_summary.json", metrics)
        nll_summary = {"schema_version": 1, "disclaimer": NLL_DISCLAIMER, "models": {}}
        for model_id in model_ids:
            entries = sorted(
                nll_entries[model_id],
                key=lambda row: (
                    row["filename"].encode("utf-8"), row["category"].encode("utf-8"), int(row["numeric_id"]),
                    {"correct": 0, "none": 1, "lm_only": 2}[row["condition"]],
                    {"pos1": 0, "pos2": 1, "negative": 2}[row["caption_role"]],
                ),
            )
            nll_summary["models"][model_id] = write_nll_store(final_temp / "nll" / model_id, entries)
        atomic_write_json(final_temp / "nll_tail_summary.json", nll_summary)
        degenerates = load_json_snapshot(args.prepared_data_dir / "degenerate_rows.json")
        atomic_write_json(final_temp / "degenerate_sensitivity_summary.json", _degenerate_sensitivity(persisted_rows, degenerates))
        atomic_write_json(final_temp / "numerical_diagnostics.json", numerical)
        device_names = {row.get("device_name") for row in shard_timings}
        if len(device_names) != 1:
            raise ValueError("formal shard device names are inconsistent")
        atomic_write_json(
            final_temp / "timing.json",
            {
                "elapsed_seconds_current_process": time.time() - started,
                "shard_elapsed_seconds_total": float(sum(float(row["elapsed_seconds"]) for row in shard_timings)),
                "device_name": next(iter(device_names)),
                "max_memory_allocated_bytes": max(
                    (int(row["max_memory_allocated_bytes"]) for row in shard_timings if row.get("max_memory_allocated_bytes") is not None),
                    default=None,
                ),
                "max_memory_reserved_bytes": max(
                    (int(row["max_memory_reserved_bytes"]) for row in shard_timings if row.get("max_memory_reserved_bytes") is not None),
                    default=None,
                ),
                "shard_count": len(shard_timings),
            },
        )
        atomic_write_json(final_temp / "environment.json", _environment(args.device))
        atomic_write_json(final_temp / "protocol_reference.json", {"path_alias": "phase3_protocol", "sha256": protocol.raw_sha256, "protocol_kind": "frozen"})
        for source, name in (
            (args.expected_registry, "expected_model_registry.json"),
            (args.verification_receipt, "model_verification_receipt.json"),
            (args.prepared_data_dir / "data_manifest.json", "data_manifest.json"),
            (args.prepared_data_dir / "split_manifest.json", "split_manifest.json"),
            (args.prepared_data_dir / "data_diagnostics.json", "data_diagnostics.json"),
            (args.prepared_data_dir / "canonical_row_index.jsonl", "canonical_row_index.jsonl"),
            (args.prepared_data_dir / "degenerate_rows.json", "degenerate_rows.json"),
            (args.prepared_data_dir / "coco_formal_images_manifest.jsonl", "coco_formal_images_manifest.jsonl"),
            (args.overlap_audit_receipt, "overlap_audit_receipt.json"),
            (args.overlap_audit_receipt.with_suffix(".sha256"), "overlap_audit_receipt.sha256"),
            (args.approval, "formal_approval.json"),
        ):
            _copy_snapshot(source, final_temp / name)
        for name in (
            "certifying_formal_filenames.txt",
            "excluded_formal_images.jsonl",
            "exact_matches.jsonl",
            "near_duplicate_diagnostics.jsonl",
            "overlap_review.json",
            "probable_pairs.jsonl",
            "text_match_diagnostics.jsonl",
        ):
            _copy_snapshot(args.overlap_audit_receipt.parent / name, final_temp / name)
        atomic_write_json(final_temp / "run_status.json", {"schema_version": 1, "status": "success", "run_mode": "formal"})
        for path in sorted(final_temp.iterdir(), key=lambda value: value.name.encode("utf-8")):
            destination = output / path.name
            if destination.exists():
                raise ValueError(f"partial final output already exists: {path.name}")
            os.rename(path, destination)
        fsync_directory(output)
    finally:
        if final_temp.exists() and not any(final_temp.iterdir()):
            final_temp.rmdir()
    state = _resume_payload(run_config_sha256, config, bindings, plan, [row["shard_id"] for row in plan], "success")
    atomic_write_json(output / "resume_state.json", state)
    inventory = inventory_files(output, excluded=("run_manifest.json",))
    run_manifest = {
        "schema_version": 1,
        "run_mode": "formal",
        "run_status": "success",
        "protocol_sha256": protocol.raw_sha256,
        "phase3_source_commit": bindings["phase3_source_commit"],
        "protocol_repository_commit": bindings["protocol_repository_commit"],
        "protocol_tag": PROTOCOL_TAG,
        "protocol_tag_object": bindings["protocol_tag_object"],
        "phase3_code_manifest_sha256": bindings["phase3_code_manifest_sha256"],
        "stage2_authority_manifest_sha256": bindings["stage2_authority_manifest_sha256"],
        "expected_model_registry_sha256": bindings["expected_registry_sha256"],
        "model_verification_receipt_sha256": bindings["verification_receipt_sha256"],
        "data_manifest_sha256": bindings["data_manifest_sha256"],
        "split_manifest_sha256": bindings["split_manifest_sha256"],
        "overlap_audit_receipt_sha256": bindings["overlap_receipt_sha256"],
        "formal_approval_sha256": bindings["approval_sha256"],
        "ordered_model_ids": model_ids,
        "ordered_filenames_sha256": config["ordered_filenames_sha256"],
        "row_result_count": len(rows),
        "image_group_result_count": len(groups),
        "files": inventory,
        "exclusion_rule": "run_manifest.json and transient lock/temp files are excluded",
    }
    atomic_write_json(output / "run_manifest.json", run_manifest, overwrite=False)
    return {"run_dir": str(output), "row_results": len(rows), "image_groups": len(groups), "shards": len(plan)}


def execute_formal_resumable(args: argparse.Namespace) -> dict[str, Any]:
    protocol = Phase3Protocol.load(args.protocol)
    protocol.require_frozen()
    model_ids = [row["model_id"] for row in MODELS]
    overlap = validate_overlap_receipt(
        args.overlap_audit_receipt,
        split_manifest_path=args.split_manifest,
        formal_image_manifest_path=args.prepared_data_dir / "coco_formal_images_manifest.jsonl",
    )
    if (
        overlap["receipt"].get("overlap_audit_input_sha256")
        != protocol.payload.get("overlap_audit_input_sha256")
    ):
        raise ValueError("overlap audit input does not match the frozen protocol")
    filenames = overlap["certifying_names"]
    bindings = _formal_bindings(args, protocol)
    config = _formal_run_config(args, protocol, model_ids, filenames, bindings)
    config_bytes = canonical_json_bytes(config)
    config_sha = sha256_bytes(config_bytes)
    plan = shard_plan(model_ids, filenames)
    output = args.output_dir
    if args.resume:
        if not output.is_dir():
            raise ValueError("--resume requires an existing formal run directory")
        if snapshot_file(output / "run_config.json", root=output) != config_bytes:
            raise ValueError("resume run configuration differs")
        state = load_json_snapshot(output / "resume_state.json", root=output)
        validate_resume_state(
            state,
            {
                "run_config_sha256": config_sha,
                "protocol_sha256": bindings["protocol_sha256"],
                "code_manifest_sha256": bindings["phase3_code_manifest_sha256"],
                "expected_registry_sha256": bindings["expected_registry_sha256"],
                "verification_receipt_sha256": bindings["verification_receipt_sha256"],
                "data_manifest_sha256": bindings["data_manifest_sha256"],
                "split_manifest_sha256": bindings["split_manifest_sha256"],
                "overlap_receipt_sha256": bindings["overlap_receipt_sha256"],
                "approval_sha256": bindings["approval_sha256"],
                "phase3_source_commit": bindings["phase3_source_commit"],
                "protocol_repository_commit": bindings["protocol_repository_commit"],
                "ordered_model_ids": model_ids,
                "ordered_filenames_sha256": config["ordered_filenames_sha256"],
            },
            plan,
        )
    else:
        if output.exists():
            raise FileExistsError(output)
        output.mkdir(parents=True)
        (output / ".tmp").mkdir()
        (output / "shards").mkdir()
        atomic_write_bytes(output / "run_config.json", config_bytes, overwrite=False)
        atomic_write_json(output / "resume_state.json", _resume_payload(config_sha, config, bindings, plan, [], "in_progress"), overwrite=False)
    lock_handle = (output / ".phase3.lock").open("a+b")
    try:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Phase3Blocked("blocked_concurrent_formal_run", str(output)) from error
        expected_by_id = {row["shard_id"]: row for row in plan}
        completed = []
        for path in (output / "shards").iterdir():
            if path.name not in expected_by_id or not path.is_dir():
                raise ValueError(f"unexpected finalized shard: {path.name}")
            validate_finalized_shard(path, expected_by_id[path.name], config_sha)
            completed.append(path.name)
        completed_set = set(completed)
        ordered_completed = [row["shard_id"] for row in plan if row["shard_id"] in completed_set]
        atomic_write_json(output / "resume_state.json", _resume_payload(config_sha, config, bindings, plan, ordered_completed, "in_progress"))
        started = time.time()
        for shard in plan:
            if shard["shard_id"] in completed_set:
                continue
            if _formal_bindings(args, protocol) != bindings:
                raise ValueError("frozen formal input changed before shard execution")
            container = Path(tempfile.mkdtemp(prefix=shard["shard_id"] + ".", dir=output / ".tmp"))
            payload_dir = container / "payload"
            result = execute_evaluation(
                run_mode="formal",
                model_ids=[shard["model_id"]],
                filenames=shard["filenames"],
                protocol_path=args.protocol,
                expected_registry_path=args.expected_registry,
                verification_receipt_path=args.verification_receipt,
                prepared_data_dir=args.prepared_data_dir,
                coco_root=args.coco_root,
                artifact_root=args.stage2_artifact_root,
                output_dir=payload_dir,
                device=args.device,
                item_batch_size=args.item_batch_size,
                stage2_protocol_path=args.stage2_protocol,
                overlap_audit_receipt_path=args.overlap_audit_receipt,
            )
            shard_manifest = {
                "schema_version": 1,
                "shard_id": shard["shard_id"],
                "run_config_sha256": config_sha,
                "model_id": shard["model_id"],
                "filenames": shard["filenames"],
                "row_count": result["row_results"],
                "image_group_count": result["image_groups"],
                "files": inventory_files(container, excluded=("shard_manifest.json",)),
                "exclusion_rule": "only shard_manifest.json is excluded",
            }
            atomic_write_json(container / "shard_manifest.json", shard_manifest, overwrite=False)
            fsync_directory(container)
            final_shard = output / "shards" / shard["shard_id"]
            os.rename(container, final_shard)
            fsync_directory(output / "shards")
            validate_finalized_shard(final_shard, shard, config_sha)
            completed_set.add(shard["shard_id"])
            ordered_completed = [row["shard_id"] for row in plan if row["shard_id"] in completed_set]
            atomic_write_json(output / "resume_state.json", _resume_payload(config_sha, config, bindings, plan, ordered_completed, "in_progress"))
        if _formal_bindings(args, protocol) != bindings:
            raise ValueError("frozen formal input changed before finalization")
        return _finalize_formal_run(args, protocol, config, bindings, plan, config_sha, started)
    finally:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        finally:
            lock_handle.close()


def _git(*arguments: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def _exists_hash(path: Path | None, expected: str | None = None) -> bool:
    if path is None or not path.is_file():
        return False
    actual = sha256_bytes(snapshot_file(path))
    return expected is None or actual == expected


def _frozen_history_is_exact(protocol: Phase3Protocol | None, head_sha: str) -> bool:
    if protocol is None or protocol.kind != "frozen":
        return False
    source = protocol.payload.get("phase3_source_commit")
    if not isinstance(source, str) or len(source) != 40:
        return False
    source_parents = _git("rev-list", "--parents", "-n", "1", source)
    head_parents = _git("rev-list", "--parents", "-n", "1", head_sha)
    if source_parents != (0, f"{source} {STAGE2_REFERENCE_COMMIT}") or head_parents != (0, f"{head_sha} {source}"):
        return False
    diff_a = _git("diff", "--name-status", STAGE2_REFERENCE_COMMIT, source)
    if diff_a[0] != 0:
        return False
    for line in diff_a[1].splitlines():
        status, path = line.split("\t", 1)
        if status != "A" or not (
            path.startswith("experiments/phase3/")
            or path.startswith("tests/fixtures/phase3/")
            or (path.startswith("tests/test_phase3_") and path.endswith(".py"))
        ):
            return False
    diff_b = _git("diff", "--name-status", source, head_sha)
    return diff_b == (
        0,
        "A\texperiments/phase3/phase3_protocol_frozen_v4.json\n"
        "A\texperiments/phase3/phase3_protocol_frozen_v4.sha256",
    )


def _manifest_paths_at_commit(commit: str) -> dict[str, bytes]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-tree", "-r", "--full-tree", commit],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("cannot enumerate source commit tree")
    selected: dict[str, bytes] = {}
    for line in result.stdout.splitlines():
        metadata, relative = line.split("\t", 1)
        mode, object_type, _ = metadata.split(" ", 2)
        path = Path(relative)
        include = (
            (relative.startswith("experiments/phase3/") and relative.endswith(".py"))
            or relative == "experiments/phase3/README.md"
            or (path.parent.as_posix() == "tests" and path.name.startswith("test_phase3_") and path.suffix == ".py")
            or relative.startswith("tests/fixtures/phase3/")
        )
        if relative.startswith("tests/fixtures/phase3/"):
            fixture_parts = Path(relative).relative_to("tests/fixtures/phase3").parts
            include = include and not any(part == "__pycache__" or part.startswith(".") for part in fixture_parts)
            include = include and not path.name.endswith((".pyc", ".pyo", ".swp", "~"))
        if not include:
            continue
        if mode != "100644" and mode != "100755" or object_type != "blob":
            raise ValueError(f"non-regular source-commit manifest path: {relative}")
        blob = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show", f"{commit}:{relative}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if blob.returncode != 0:
            raise ValueError(f"cannot read source-commit blob: {relative}")
        selected[relative] = blob.stdout
    return selected


def _code_manifest_matches_source(protocol: Phase3Protocol, code_manifest: Path) -> bool:
    source = protocol.payload.get("phase3_source_commit")
    if not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source):
        return False
    current = verify_code_manifest(code_manifest)
    raw = canonical_json_bytes(current)
    if sha256_bytes(raw) != protocol.payload.get("phase3_code_manifest_sha256"):
        return False
    committed_manifest = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{source}:experiments/phase3/phase3_code_manifest_v2.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    committed_sidecar = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{source}:experiments/phase3/phase3_code_manifest_v2.sha256"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if committed_manifest.returncode or committed_sidecar.returncode:
        return False
    if committed_manifest.stdout != raw or committed_sidecar.stdout != (sha256_bytes(raw) + "\n").encode("ascii"):
        return False
    blobs = _manifest_paths_at_commit(source)
    rows = current.get("files", [])
    if {row["relative_path"] for row in rows} != set(blobs) or len(rows) != len(blobs):
        return False
    return all(
        len(blobs[row["relative_path"]]) == row["size_bytes"]
        and sha256_bytes(blobs[row["relative_path"]]) == row["sha256"]
        for row in rows
    )


def _stage2_sources_are_unchanged(stage2_protocol_path: Path) -> bool:
    # This performs the reference-ancestor check, all eleven path diffs,
    # implementation SHA table, immutable receipts, and required base assets.
    verify_stage2_source_integrity(str(stage2_protocol_path.absolute()))
    return True


def _image_manifests_are_exact(prepared_data_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    referenced_path = prepared_data_dir / "coco_referenced_images_manifest.jsonl"
    formal_path = prepared_data_dir / "coco_formal_images_manifest.jsonl"
    referenced = load_jsonl_snapshot(referenced_path, root=prepared_data_dir)
    formal = load_jsonl_snapshot(formal_path, root=prepared_data_dir)
    required = {"coco_image_id", "error_code", "exists", "filename", "perceptual_hash", "sha256", "size_bytes", "status"}
    if len(referenced) != 1542 or any(set(row) != required for row in referenced):
        raise ValueError("referenced image manifest schema/count mismatch")
    filenames = [row["filename"] for row in referenced]
    if filenames != sorted(set(filenames), key=lambda value: value.encode("utf-8")):
        raise ValueError("referenced image manifest order/uniqueness mismatch")
    formal_names = snapshot_file(prepared_data_dir / "formal_filenames.txt", root=prepared_data_dir).decode("utf-8").splitlines()
    by_name = {row["filename"]: row for row in referenced}
    if len(formal_names) != 1389 or formal != [by_name[name] for name in formal_names]:
        raise ValueError("formal image manifest is not the exact frozen subset")
    return referenced, formal


def _all_images_ready(prepared_data_dir: Path) -> bool:
    referenced, _ = _image_manifests_are_exact(prepared_data_dir)
    hard = [row["filename"] for row in referenced if row.get("status") in ("unsafe_path", "decode_failed")]
    if hard:
        raise ValueError(f"hard-failure image rows: {len(hard)}")
    unavailable = [row["filename"] for row in referenced if row.get("status") in ("missing", "unreadable")]
    if unavailable:
        raise Phase3Blocked("formal_images_not_ready", f"missing/unreadable image rows: {len(unavailable)}")
    return all(row.get("status") == "ready" for row in referenced)


def _approval_matches(
    approval: dict[str, Any] | None,
    protocol: Phase3Protocol | None,
    args: argparse.Namespace,
    peeled_commit: str | None,
) -> bool:
    if approval is None or protocol is None:
        return False
    required = {
        "schema_version", "approval_trust_model", "approved_by", "approved_at", "statement",
        "complete_model_formal_independence_assumption_accepted", "coco_provenance_attestation",
        "protocol_sha256", "protocol_repository_commit", "phase3_source_commit",
        "phase3_code_manifest_sha256", "stage2_authority_manifest_sha256",
        "expected_model_registry_sha256", "model_verification_receipt_sha256",
        "data_manifest_sha256", "split_manifest_sha256", "overlap_audit_receipt_sha256",
        "pilot_run_manifest_sha256", "pilot_bundle_content_hash", "pilot_bundle_verification_status",
    }
    if set(approval) != required:
        return False
    hex64 = re.compile(r"[0-9a-f]{64}")
    authority = args.code_manifest.parent / "phase3_stage2_authority_manifest_v2.json"
    data_manifest = args.prepared_data_dir / "data_manifest.json"
    values = {
        "protocol_sha256": protocol.raw_sha256,
        "protocol_repository_commit": peeled_commit,
        "phase3_source_commit": protocol.payload.get("phase3_source_commit"),
        "phase3_code_manifest_sha256": sha256_bytes(snapshot_file(args.code_manifest)),
        "stage2_authority_manifest_sha256": sha256_bytes(snapshot_file(authority)),
        "expected_model_registry_sha256": sha256_bytes(snapshot_file(args.expected_registry)),
        "model_verification_receipt_sha256": sha256_bytes(snapshot_file(args.verification_receipt)),
        "data_manifest_sha256": sha256_bytes(snapshot_file(data_manifest)),
        "split_manifest_sha256": sha256_bytes(snapshot_file(args.split_manifest)),
        "overlap_audit_receipt_sha256": sha256_bytes(snapshot_file(args.overlap_audit_receipt)),
    }
    return (
        approval["schema_version"] == 1
        and approval["approval_trust_model"] == "user_supplied_unsigned_attestation"
        and isinstance(approval["approved_by"], str) and bool(approval["approved_by"])
        and isinstance(approval["approved_at"], str) and bool(approval["approved_at"])
        and approval["statement"] == "Primary metrics and formal split are frozen."
        and approval["complete_model_formal_independence_assumption_accepted"] is True
        and approval["coco_provenance_attestation"] == "I attest that the frozen image manifest was generated from official COCO val2017 images."
        and approval["pilot_bundle_verification_status"] == "passed"
        and all(approval[key] == value for key, value in values.items())
        and bool(hex64.fullmatch(str(approval["pilot_run_manifest_sha256"])))
        and bool(hex64.fullmatch(str(approval["pilot_bundle_content_hash"])))
    )


def collect_preflight(args: argparse.Namespace) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []

    def gate(gate_id: str, check: Callable[[], bool], *, missing_is_blocked: bool = True) -> None:
        try:
            passed = bool(check())
            gates.append(
                {"gate_id": gate_id, "status": "pass" if passed else ("blocked" if missing_is_blocked else "hard_failure"), "reason_code": None if passed else gate_id, "detail": ""}
            )
        except FileNotFoundError as error:
            gates.append({"gate_id": gate_id, "status": "blocked", "reason_code": "missing", "detail": str(error)})
        except Phase3Blocked as error:
            gates.append({"gate_id": gate_id, "status": "blocked", "reason_code": error.code, "detail": error.detail})
        except Exception as error:
            gates.append({"gate_id": gate_id, "status": "hard_failure", "reason_code": type(error).__name__, "detail": str(error)})

    protocol: Phase3Protocol | None = None
    try:
        protocol = Phase3Protocol.load(args.protocol)
    except Exception:
        pass
    gate(
        "protocol_is_frozen",
        lambda: protocol is not None and protocol.kind == "frozen",
        missing_is_blocked=not args.protocol.is_file() or (protocol is not None and protocol.kind != "frozen"),
    )
    gate(
        "protocol_raw_sha_matches",
        lambda: protocol is not None
        and snapshot_file(args.protocol.with_suffix(".sha256")).decode("ascii") == protocol.raw_sha256 + "\n",
        missing_is_blocked=not args.protocol.is_file() or not args.protocol.with_suffix(".sha256").is_file(),
    )
    gate("protocol_source_commit_non_null", lambda: protocol is not None and isinstance(protocol.payload.get("phase3_source_commit"), str))
    tag_type = _git("cat-file", "-t", f"refs/tags/{PROTOCOL_TAG}")
    peeled = _git("rev-parse", f"refs/tags/{PROTOCOL_TAG}^{{commit}}")
    head = _git("rev-parse", "HEAD")
    gate("protocol_tag_exists", lambda: tag_type[0] == 0)
    gate(
        "protocol_tag_is_annotated_and_peels_to_B",
        lambda: tag_type == (0, "tag") and peeled[0] == 0,
        missing_is_blocked=tag_type[0] != 0,
    )
    gate(
        "head_matches_protocol_tag_target",
        lambda: peeled[0] == 0 and head[0] == 0 and peeled[1] == head[1],
        missing_is_blocked=peeled[0] != 0,
    )
    gate(
        "A_and_B_are_direct_children_with_exact_diff_whitelists",
        lambda: head[0] == 0 and _frozen_history_is_exact(protocol, head[1]),
        missing_is_blocked=protocol is None or protocol.kind != "frozen" or peeled[0] != 0,
    )
    gate("tracked_workspace_clean", lambda: _git("status", "--porcelain", "--untracked-files=no")[1] == "", missing_is_blocked=False)

    def untracked_allowed() -> bool:
        result = _git("ls-files", "--others", "--exclude-standard")
        if result[0] != 0:
            raise ValueError("cannot enumerate untracked paths")
        allowed_roots = []
        for candidate in (
            args.prepared_data_dir,
            args.output_dir,
            args.preflight_report.parent,
            args.status_output.parent,
        ):
            if candidate is None:
                continue
            resolved = candidate.resolve(strict=False)
            try:
                allowed_roots.append(resolved.relative_to(REPO_ROOT.resolve()).as_posix())
            except ValueError:
                pass
        for relative in result[1].splitlines():
            if not any(relative == root or relative.startswith(root.rstrip("/") + "/") for root in allowed_roots):
                return False
        return True

    gate("untracked_paths_allowed", untracked_allowed, missing_is_blocked=False)
    gate(
        "code_manifest_matches",
        lambda: protocol is not None
        and _exists_hash(args.code_manifest, protocol.payload.get("phase3_code_manifest_sha256"))
        and _code_manifest_matches_source(protocol, args.code_manifest),
        missing_is_blocked=protocol is None or not args.code_manifest.is_file(),
    )
    gate("stage2_sources_unchanged", lambda: _stage2_sources_are_unchanged(args.stage2_protocol), missing_is_blocked=False)
    registry_box: dict[str, Any] = {}

    def registry_value() -> dict[str, Any] | None:
        if not args.expected_registry.is_file():
            return None
        if "value" not in registry_box:
            value = load_json_snapshot(args.expected_registry)
            if not isinstance(value, dict):
                raise ValueError("expected registry must be a JSON object")
            registry_box["value"] = value
        return registry_box["value"]

    def expected_registry_matches() -> bool:
        registry = registry_value()
        return bool(
            registry is not None
            and protocol is not None
            and registry.get("schema_version") == 2
            and registry.get("registry_id") == "phase3-v4-expected-model-registry-v2"
            and protocol.payload.get("expected_model_registry_sha256") == sha256_bytes(snapshot_file(args.expected_registry))
            and registry.get("artifact_batch_id") == protocol.payload.get("stage2_artifact_batch_id")
        )

    gate(
        "expected_registry_hash_matches",
        expected_registry_matches,
        missing_is_blocked=protocol is None or not args.expected_registry.is_file(),
    )
    verified_receipt: dict[str, Any] = {}

    def receipt_value() -> dict[str, Any] | None:
        if not args.verification_receipt.is_file():
            return None
        if "value" not in verified_receipt:
            verified_receipt["value"] = validate_model_verification_receipt(
                args.verification_receipt,
                args.expected_registry,
                require_all=False,
            )
        return verified_receipt["value"]

    def receipt_is_bound() -> bool:
        if receipt_value() is None:
            return False
        return True

    gate(
        "artifact_receipt_is_bound",
        receipt_is_bound,
        missing_is_blocked=not args.verification_receipt.is_file(),
    )

    def all_models_verified() -> bool:
        receipt = receipt_value()
        if receipt is not None and receipt.get("overall_status") == "blocked":
            raise Phase3Blocked("models_not_all_verified", "the bound artifact receipt contains missing models")
        return bool(
            receipt is not None
            and receipt.get("overall_status") == "verified"
            and len(receipt.get("models", [])) == 10
            and all(row.get("status") == "verified" for row in receipt["models"])
        )

    gate(
        "all_ten_models_verified",
        all_models_verified,
        missing_is_blocked=not args.verification_receipt.is_file(),
    )
    data_manifest_path = args.prepared_data_dir / "data_manifest.json"
    split_manifest_path = args.split_manifest
    prepared_validation: dict[str, Any] = {}

    def prepared_is_valid() -> bool:
        if "value" not in prepared_validation:
            if protocol is None:
                return False
            value = validate_prepared_data(args.prepared_data_dir)
            if (
                value["data_manifest_sha256"] != protocol.payload.get("data_manifest_sha256")
                or value["split_manifest_sha256"] != protocol.payload.get("split_manifest_sha256")
            ):
                raise ValueError("prepared data differs from the frozen protocol binding")
            prepared_split = args.prepared_data_dir / "split_manifest.json"
            if snapshot_file(args.split_manifest) != snapshot_file(prepared_split, root=args.prepared_data_dir):
                raise ValueError("explicit split manifest differs from prepared data binding")
            prepared_validation["value"] = value
        return True

    gate(
        "data_manifest_hash_matches",
        prepared_is_valid,
        missing_is_blocked=protocol is None or not data_manifest_path.is_file(),
    )
    gate(
        "split_manifest_hash_matches",
        prepared_is_valid,
        missing_is_blocked=protocol is None or not split_manifest_path.is_file(),
    )
    image_manifest_path = args.prepared_data_dir / "coco_referenced_images_manifest.jsonl"
    formal_image_path = args.prepared_data_dir / "coco_formal_images_manifest.jsonl"
    gate(
        "all_1542_image_manifest_rows_ready",
        lambda: _all_images_ready(args.prepared_data_dir),
        missing_is_blocked=not image_manifest_path.is_file(),
    )
    gate(
        "formal_image_manifest_is_exact_1389_subset",
        lambda: len(_image_manifests_are_exact(args.prepared_data_dir)[1]) == 1389,
        missing_is_blocked=not formal_image_path.is_file(),
    )
    verified_overlap: dict[str, Any] = {}

    def overlap_value() -> dict[str, Any] | None:
        if args.overlap_audit_receipt is None or not args.overlap_audit_receipt.is_file():
            return None
        if "value" not in verified_overlap:
            verified_overlap["value"] = validate_overlap_receipt(
                args.overlap_audit_receipt,
                split_manifest_path=args.split_manifest,
                formal_image_manifest_path=formal_image_path,
            )
        return verified_overlap["value"]["receipt"]

    def overlap_is_bound() -> bool:
        overlap = overlap_value()
        if overlap is None or protocol is None:
            return False
        return (
            overlap.get("overlap_audit_input_sha256")
            == protocol.payload.get("overlap_audit_input_sha256")
        )

    gate(
        "overlap_receipt_hash_matches",
        overlap_is_bound,
        missing_is_blocked=args.overlap_audit_receipt is None or not args.overlap_audit_receipt.is_file() or protocol is None,
    )
    gate(
        "audited_certifying_formal_subset_is_exact_1345",
        lambda: overlap_value() is not None
        and overlap_value().get("excluded_formal_image_count") == 44
        and overlap_value().get("certifying_formal_image_count") == 1345,
    )
    gate(
        "overlap_status_certification_subset_project_disjoint_under_frozen_checks",
        lambda: overlap_value() is not None
        and overlap_value().get("project_overlap_audit_status")
        == "certification_subset_project_disjoint_under_frozen_checks",
    )
    gate("external_pretraining_unknown_disclosed", lambda: overlap_value() is not None and overlap_value().get("external_base_pretraining_overlap") == "unknown")
    approval_box: dict[str, Any] = {}

    def approval_value() -> dict[str, Any] | None:
        if args.approval is None or not args.approval.is_file():
            return None
        if "value" not in approval_box:
            value = load_json_snapshot(args.approval)
            if not isinstance(value, dict):
                raise ValueError("formal approval must be a JSON object")
            approval_box["value"] = value
        return approval_box["value"]

    gate("complete_model_independence_assumption_accepted", lambda: approval_value() is not None and approval_value().get("complete_model_formal_independence_assumption_accepted") is True)
    gate("approval_exists", lambda: approval_value() is not None)
    gate(
        "approval_fields_match",
        lambda: _approval_matches(approval_value(), protocol, args, peeled[1] if peeled[0] == 0 else None),
        missing_is_blocked=args.approval is None or not args.approval.is_file() or protocol is None,
    )
    gate("official_coco_provenance_is_user_attested", lambda: approval_value() is not None and approval_value().get("coco_provenance_attestation") == "I attest that the frozen image manifest was generated from official COCO val2017 images.")
    gate("approval_attests_pilot_bundle_cpu_verified", lambda: approval_value() is not None and approval_value().get("pilot_bundle_verification_status") == "passed")
    gate(
        "confirm_protocol_hash_matches",
        lambda: protocol is not None and args.confirm_protocol_hash == protocol.raw_sha256,
        missing_is_blocked=protocol is None,
    )
    gate(
        "output_or_resume_state_is_valid",
        lambda: args.preflight_only
        or (args.output_dir is not None and ((not args.output_dir.exists()) or args.resume)),
        missing_is_blocked=False,
    )
    status = "hard_failure" if any(row["status"] == "hard_failure" for row in gates) else ("blocked" if any(row["status"] == "blocked" for row in gates) else "pass")
    return {"schema_version": 1, "preflight_status": status, "gates": gates}


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight-only", action="store_true")
    modes.add_argument("--execute-formal", action="store_true")
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--code-manifest", type=Path, default=Path("experiments/phase3/phase3_code_manifest_v2.json"))
    parser.add_argument("--expected-registry", type=Path, required=True)
    parser.add_argument("--verification-receipt", type=Path, required=True)
    parser.add_argument("--prepared-data-dir", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--overlap-audit-receipt", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--confirm-protocol-hash", required=True)
    parser.add_argument("--preflight-report", type=Path, required=True)
    parser.add_argument("--stage2-artifact-root", type=Path)
    parser.add_argument("--coco-root", type=Path)
    parser.add_argument("--stage2-protocol", type=Path, default=Path("experiments/stage2_protocol_v2.json"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--device")
    parser.add_argument("--item-batch-size", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation():
        input_roots = [
            args.protocol.parent, args.code_manifest.parent, args.expected_registry.parent,
            args.verification_receipt.parent, args.prepared_data_dir, args.split_manifest.parent,
            args.stage2_protocol.parent,
        ]
        if args.overlap_audit_receipt is not None:
            input_roots.append(args.overlap_audit_receipt.parent)
        if args.approval is not None:
            input_roots.append(args.approval.parent)
        if args.stage2_artifact_root is not None:
            input_roots.append(args.stage2_artifact_root)
        if args.coco_root is not None:
            input_roots.append(args.coco_root)
        output_roots = [args.preflight_report.parent, args.status_output.parent]
        if args.output_dir is not None:
            output_roots.append(args.output_dir)
        validate_disjoint_roots(
            input_roots=input_roots,
            output_roots=output_roots,
            forbidden_exact=[
                Path("/"), Path.home(), REPO_ROOT, REPO_ROOT / "experiments/phase3", REPO_ROOT / "tests",
            ],
        )
        if args.preflight_report.exists():
            raise Phase3HardFailure("preflight_report_exists", str(args.preflight_report))
        report = collect_preflight(args)
        atomic_write_json(args.preflight_report, report, overwrite=False)
        if report["preflight_status"] == "hard_failure":
            failed = [row["gate_id"] for row in report["gates"] if row["status"] == "hard_failure"]
            raise Phase3HardFailure("formal_preflight_hard_failure", ",".join(failed))
        if report["preflight_status"] == "blocked":
            failed = [row["gate_id"] for row in report["gates"] if row["status"] == "blocked"]
            raise Phase3Blocked("formal_preflight_blocked", ",".join(failed))
        if args.preflight_only:
            return {"preflight_report": str(args.preflight_report), "all_gates_passed": True}
        if not all((args.stage2_artifact_root, args.coco_root, args.output_dir, args.device)):
            raise Phase3HardFailure("formal_execute_arguments_missing", "artifact/coco/output/device are required")
        try:
            return execute_formal_resumable(args)
        except Phase3Blocked:
            raise
        except RuntimeError as error:
            message = str(error).lower()
            if "out of memory" in message:
                raise Phase3Blocked("blocked_resource_oom", str(error)) from error
            if any(token in message for token in ("unavailable", "not verified", "not all ready")):
                raise Phase3Blocked("blocked_formal_resource", str(error)) from error
            raise Phase3HardFailure("formal_runtime_invariant_failure", str(error)) from error
        except FileNotFoundError as error:
            raise Phase3Blocked("blocked_formal_resource_missing", str(error)) from error
        except (ValueError, FileExistsError, OSError) as error:
            raise Phase3HardFailure("formal_runtime_invariant_failure", str(error)) from error

    return execute_with_status("run_phase3_formal_v2", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
