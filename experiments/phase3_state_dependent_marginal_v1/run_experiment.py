#!/usr/bin/env python3
"""Dry-run or execute the frozen 9-reuse/27-training experiment."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from experiments.phase3_private_vs_shared_v1.artifacts import (
    write_json_atomic,
    write_json_exclusive,
)
from experiments.phase3_private_vs_shared_v1.common import sha256_file

from . import EVALUATION_ROLE, MODULES
from .manifest import DEFAULT_MANIFEST, verify_frozen_manifest
from .runtime import execute_run

DEFAULT_RESULTS_ROOT = Path(
    "/home/lizhaohui/lzq/stage3-state-dependent-marginal-20260805"
)


def select_runs(
    manifest: Mapping[str, Any],
    *,
    run_id: str | None = None,
    state: str | None = None,
    all_runs: bool = False,
    seed: int | None = None,
    module: str | None = None,
    run_type: str | None = None,
) -> list[dict[str, Any]]:
    if sum((run_id is not None, state is not None, all_runs)) != 1:
        raise ValueError("select exactly one of run_id, state, or all")
    runs = list(manifest["runs"])
    if run_id is not None:
        selected = [run for run in runs if run["run_id"] == run_id]
    elif state is not None:
        selected = [run for run in runs if run["base_state"] == state]
    else:
        selected = runs
    if seed is not None:
        selected = [run for run in selected if run["seed"] == seed]
    if module is not None:
        if module not in MODULES:
            raise ValueError("unknown module")
        selected = [run for run in selected if run["module"] == module]
    if run_type is not None:
        selected = [run for run in selected if run["run_type"] == run_type]
    if not selected:
        raise ValueError("run selection is empty")
    return selected


def _result_path(results_root: Path, run: Mapping[str, Any]) -> Path:
    return (
        results_root.resolve()
        / run["result_relative_directory"]
        / "run_result.json"
    )


def _status_path(results_root: Path, run: Mapping[str, Any]) -> Path:
    return (
        results_root.resolve()
        / run["result_relative_directory"]
        / "run_status.json"
    )


def validate_result(
    result: Mapping[str, Any],
    run: Mapping[str, Any],
    manifest_sha256: str,
) -> None:
    required = {
        "run_id",
        "config_id",
        "run_type",
        "base_state",
        "module",
        "coordinate_dimensions",
        "seed",
        "checkpoint_path",
        "checkpoint_sha256",
        "training_manifest_path",
        "training_manifest_sha256",
        "module_wise_encoded_bits",
        "target_module_encoded_bits",
        "total_encoded_bits",
        "development_task_risk",
        "semantic_risk_bound",
        "visual_gain_guardrail",
        "evaluation_role",
        "module_codec_paths",
        "codec_receipt_path",
        "run_status",
    }
    if not required <= result.keys():
        raise ValueError("run result is missing required fields")
    if (
        result["run_id"] != run["run_id"]
        or result["config_id"] != run["config_id"]
        or result["run_type"] != run["run_type"]
        or result["base_state"] != run["base_state"]
        or result["module"] != run["module"]
        or result["coordinate_dimensions"] != run["coordinate_dimensions"]
        or result["seed"] != run["seed"]
        or result.get("experiment_manifest_sha256") != manifest_sha256
        or result["run_status"] != "complete"
        or result["evaluation_role"] != EVALUATION_ROLE
    ):
        raise ValueError("run result identity or binding differs")
    bits = result["module_wise_encoded_bits"]
    if (
        set(bits) != set(MODULES)
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in bits.values()
        )
        or sum(bits.values()) != result["total_encoded_bits"]
        or any(result[f"{module}_encoded_bits"] != bits[module] for module in MODULES)
    ):
        raise ValueError("actual module-bit accounting differs")
    if run["module"] is None:
        if result["target_module_encoded_bits"] is not None:
            raise ValueError("base result unexpectedly selects target-module bits")
    elif result["target_module_encoded_bits"] != bits[run["module"]]:
        raise ValueError("candidate target bits differ from module codec")
    expected_training = (
        "reused_previous_checkpoint"
        if run["run_type"] == "reused_base"
        else "new_training"
    )
    if result.get("training_status") != expected_training:
        raise ValueError("run training/reuse status differs")


def _load_status(
    path: Path, *, run: Mapping[str, Any], manifest_sha256: str
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    status = json.loads(path.read_text(encoding="utf-8"))
    if (
        status.get("run_id") != run["run_id"]
        or status.get("experiment_manifest_sha256") != manifest_sha256
    ):
        raise ValueError("existing run status has stale bindings")
    return status


def dispatch(
    manifest_path: Path,
    results_root: Path,
    *,
    selected_runs: Sequence[Mapping[str, Any]],
    execute: bool,
    artifact_root: Path | None = None,
    device: str = "cuda:0",
    retry_failed: bool = False,
    resume_running: bool = False,
) -> dict[str, Any]:
    manifest = verify_frozen_manifest(manifest_path)
    manifest_sha256 = sha256_file(manifest_path)
    authoritative = {run["run_id"]: run for run in manifest["runs"]}
    selected = []
    for requested in selected_runs:
        run_id = requested["run_id"]
        if run_id not in authoritative or dict(requested) != authoritative[run_id]:
            raise ValueError("selected run differs from frozen manifest")
        selected.append(authoritative[run_id])
    receipt = {
        "experiment_manifest_sha256": manifest_sha256,
        "selected_run_count": len(selected),
        "selected_new_training_count": sum(
            run["training_required"] for run in selected
        ),
        "selected_reused_checkpoint_count": sum(
            run["checkpoint_reuse"] for run in selected
        ),
        "selected_run_ids": [run["run_id"] for run in selected],
    }
    if not execute:
        return {"mode": "dry_run", **receipt}
    completed, skipped, failed = [], [], []
    retried, resumed, skipped_running = [], [], []
    for run in selected:
        result_path = _result_path(results_root, run)
        status_path = _status_path(results_root, run)
        status = _load_status(
            status_path, run=run, manifest_sha256=manifest_sha256
        )
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            validate_result(result, run, manifest_sha256)
            if status is None or status.get("status") != "complete":
                raise ValueError("complete result lacks matching status")
            skipped.append(run["run_id"])
            continue
        if status is not None:
            if status.get("status") == "failed":
                if not retry_failed:
                    skipped.append(run["run_id"])
                    continue
                retried.append(run["run_id"])
            elif status.get("status") == "running":
                if not resume_running:
                    skipped_running.append(run["run_id"])
                    continue
                resumed.append(run["run_id"])
            elif status.get("status") == "complete":
                raise ValueError("complete status exists without result")
            else:
                raise ValueError("existing run status is invalid")
        write_json_atomic(
            status_path,
            {
                "schema_version": 1,
                "run_id": run["run_id"],
                "config_id": run["config_id"],
                "seed": run["seed"],
                "experiment_manifest_sha256": manifest_sha256,
                "status": "running",
                "retry": run["run_id"] in retried,
                "resume": run["run_id"] in resumed,
                "automatic_configuration_change": False,
            },
        )
        try:
            result = execute_run(
                run,
                manifest_path=manifest_path,
                results_root=results_root,
                artifact_root=artifact_root,
                device=device,
            )
            validate_result(result, run, manifest_sha256)
            write_json_exclusive(result_path, result)
            write_json_atomic(
                status_path,
                {
                    "schema_version": 1,
                    "run_id": run["run_id"],
                    "config_id": run["config_id"],
                    "seed": run["seed"],
                    "experiment_manifest_sha256": manifest_sha256,
                    "result_sha256": sha256_file(result_path),
                    "status": "complete",
                    "training_status": result["training_status"],
                    "automatic_configuration_change": False,
                },
            )
            completed.append(run["run_id"])
        except Exception as error:
            write_json_atomic(
                status_path,
                {
                    "schema_version": 1,
                    "run_id": run["run_id"],
                    "config_id": run["config_id"],
                    "seed": run["seed"],
                    "experiment_manifest_sha256": manifest_sha256,
                    "status": "failed",
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "automatic_retry": False,
                    "automatic_configuration_change": False,
                },
            )
            failed.append(run["run_id"])
    return {
        "mode": "execute",
        **receipt,
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
        "retried": retried,
        "resumed": resumed,
        "skipped_running": skipped_running,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--device", default="cuda:0")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--run-id")
    selection.add_argument("--state")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--module")
    parser.add_argument(
        "--run-type", choices=("reused_base", "new_candidate")
    )
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--resume-running", action="store_true")
    args = parser.parse_args()
    if (
        args.shard_count <= 0
        or args.shard_index < 0
        or args.shard_index >= args.shard_count
    ):
        parser.error("shard index/count are invalid")
    manifest = verify_frozen_manifest(args.manifest)
    selected = select_runs(
        manifest,
        run_id=args.run_id,
        state=args.state,
        all_runs=args.all,
        seed=args.seed,
        module=args.module,
        run_type=args.run_type,
    )
    selected = selected[args.shard_index :: args.shard_count]
    if not selected:
        parser.error("selected shard is empty")
    result = dispatch(
        args.manifest,
        args.results_root,
        selected_runs=selected,
        execute=args.execute,
        artifact_root=args.artifact_root,
        device=args.device,
        retry_failed=args.retry_failed,
        resume_running=args.resume_running,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())

