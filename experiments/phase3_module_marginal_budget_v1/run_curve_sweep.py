#!/usr/bin/env python3
"""Select and dispatch development-only module-budget curve runs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from experiments.phase3_private_vs_shared_v1.artifacts import (
    write_json_atomic,
    write_json_exclusive,
)
from experiments.phase3_private_vs_shared_v1.common import sha256_file

from . import CURVE_NAMES
from .formal_plan import DEFAULT_RUN_PLAN, verify_formal_run_plan

Worker = Callable[..., Mapping[str, Any]]
TERMINAL_COMPLETE = {"complete"}


def _curve_name(value: str) -> str:
    if value in CURVE_NAMES:
        return CURVE_NAMES[value]
    if value in CURVE_NAMES.values():
        return value
    raise ValueError(f"curve must be a module or one of {tuple(CURVE_NAMES.values())}")


def _belongs_to_curve(run: Mapping[str, Any], curve_name: str) -> bool:
    return run["curve_name"] == curve_name or any(
        membership["curve_name"] == curve_name
        for membership in run["curve_memberships"]
    )


def select_runs(
    plan: Mapping[str, Any],
    *,
    run_id: str | None = None,
    config_id: str | None = None,
    seed: int | None = None,
    curve: str | None = None,
    all_runs: bool = False,
) -> list[dict[str, Any]]:
    selectors = sum(
        value is not None and value is not False
        for value in (run_id, config_id, curve, all_runs)
    )
    if selectors != 1:
        raise ValueError("select exactly one of run_id, config_id, curve, or all")
    runs = list(plan["runs"])
    if run_id is not None:
        selected = [run for run in runs if run["run_id"] == run_id]
        if seed is not None and selected and selected[0]["seed"] != seed:
            selected = []
    elif config_id is not None:
        selected = [
            run
            for run in runs
            if run["sweep_config_id"] == config_id or run["config_id"] == config_id
        ]
        if seed is None and len(selected) > 1:
            raise ValueError("a sweep config selection requires an explicit seed")
        if seed is not None:
            selected = [run for run in selected if run["seed"] == seed]
    elif curve is not None:
        selected_curve = _curve_name(curve)
        selected = [run for run in runs if _belongs_to_curve(run, selected_curve)]
        if seed is not None:
            selected = [run for run in selected if run["seed"] == seed]
    else:
        selected = runs
        if seed is not None:
            selected = [run for run in selected if run["seed"] == seed]
    if not selected:
        raise ValueError("run selection is empty")
    return selected


def _result_path(results_root: Path, run: Mapping[str, Any]) -> Path:
    return results_root.resolve() / run["result_relative_directory"] / "run_result.json"


def _status_path(results_root: Path, run: Mapping[str, Any]) -> Path:
    return results_root.resolve() / run["result_relative_directory"] / "run_status.json"


def _validate_result(
    result: Mapping[str, Any],
    run: Mapping[str, Any],
    plan_sha256: str,
) -> None:
    required = {
        "config_id",
        "curve_name",
        "target_module",
        "coordinate_dimensions",
        "seed",
        "checkpoint_path",
        "vision_encoded_bits",
        "projector_encoded_bits",
        "language_encoded_bits",
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
        raise ValueError("curve run result is missing required fields")
    if (
        result["config_id"] != run["config_id"]
        or result["coordinate_dimensions"] != run["coordinate_dimensions"]
        or result["seed"] != run["seed"]
        or result.get("curve_run_plan_sha256") != plan_sha256
        or result["run_status"] != "complete"
        or result["evaluation_role"] != "development_only"
    ):
        raise ValueError("curve run result identity or binding differs")
    module_bits = [
        result["vision_encoded_bits"],
        result["projector_encoded_bits"],
        result["language_encoded_bits"],
    ]
    grouped_bits = result["module_wise_encoded_bits"]
    if (
        any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in module_bits
        )
        or grouped_bits
        != {
            "vision": module_bits[0],
            "projector": module_bits[1],
            "language": module_bits[2],
        }
        or sum(module_bits) != result["total_encoded_bits"]
    ):
        raise ValueError("curve run result encoded-bit accounting differs")
    target_module = run["target_module"]
    target_bits = result["target_module_encoded_bits"]
    if target_module is None:
        if target_bits is not None:
            raise ValueError(
                "shared anchor must not select one target-module bit count"
            )
    elif target_bits != grouped_bits[target_module]:
        raise ValueError("target-module encoded bits differ from the module codec")


def _load_status(
    path: Path,
    *,
    run: Mapping[str, Any],
    plan_sha256: str,
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    status = json.loads(path.read_text(encoding="utf-8"))
    if (
        status.get("run_id") != run["run_id"]
        or status.get("curve_run_plan_sha256") != plan_sha256
    ):
        raise ValueError("existing run status has stale bindings")
    return status


def dispatch(
    plan_path: Path,
    results_root: Path,
    *,
    selected_runs: Sequence[Mapping[str, Any]],
    execute: bool,
    retry_failed: bool,
    resume_running: bool = False,
    worker: Worker | None = None,
    artifact_root: Path | None = None,
    device: str = "cuda:0",
) -> dict[str, Any]:
    plan = verify_formal_run_plan(plan_path)
    plan_sha256 = sha256_file(plan_path)
    authoritative = {run["run_id"]: run for run in plan["runs"]}
    selected = []
    for requested in selected_runs:
        run_id = requested["run_id"]
        if run_id not in authoritative or dict(requested) != authoritative[run_id]:
            raise ValueError("selected run differs from the frozen plan")
        selected.append(authoritative[run_id])
    if not execute:
        return {
            "mode": "dry_run",
            "curve_run_plan_sha256": plan_sha256,
            "selected_run_count": len(selected),
            "selected_training_run_count": sum(
                run["training_required"] for run in selected
            ),
            "selected_anchor_reuse_count": sum(run["anchor_reuse"] for run in selected),
            "selected_run_ids": [run["run_id"] for run in selected],
        }
    if worker is None:
        from .formal_runtime import execute_formal_run

        worker = execute_formal_run
    completed = []
    skipped = []
    failed = []
    retried = []
    resumed = []
    skipped_running = []
    for run in selected:
        result_path = _result_path(results_root, run)
        status_path = _status_path(results_root, run)
        status = _load_status(status_path, run=run, plan_sha256=plan_sha256)
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            _validate_result(result, run, plan_sha256)
            if status is None or status.get("status") not in TERMINAL_COMPLETE:
                raise ValueError("complete result lacks a matching terminal status")
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
            elif status.get("status") in TERMINAL_COMPLETE:
                raise ValueError("complete status exists without a result")
            else:
                raise ValueError("existing run status is invalid")
        write_json_atomic(
            status_path,
            {
                "schema_version": 1,
                "run_id": run["run_id"],
                "config_id": run["config_id"],
                "seed": run["seed"],
                "curve_run_plan_sha256": plan_sha256,
                "status": "running",
                "retry": run["run_id"] in retried,
                "resume": run["run_id"] in resumed,
                "automatic_configuration_change": False,
            },
        )
        try:
            result = dict(
                worker(
                    run,
                    plan_path=plan_path,
                    results_root=results_root,
                    artifact_root=artifact_root,
                    device=device,
                )
            )
            _validate_result(result, run, plan_sha256)
            write_json_exclusive(result_path, result)
            write_json_atomic(
                status_path,
                {
                    "schema_version": 1,
                    "run_id": run["run_id"],
                    "config_id": run["config_id"],
                    "seed": run["seed"],
                    "curve_run_plan_sha256": plan_sha256,
                    "result_sha256": sha256_file(result_path),
                    "status": "complete",
                    "training_status": result.get("training_status"),
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
                    "curve_run_plan_sha256": plan_sha256,
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
        "curve_run_plan_sha256": plan_sha256,
        "selected_run_count": len(selected),
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
        "retried": retried,
        "resumed": resumed,
        "skipped_running": skipped_running,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_RUN_PLAN)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--device", default="cuda:0")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--run-id")
    selection.add_argument("--config-id")
    selection.add_argument("--curve")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument(
        "--resume-running",
        action="store_true",
        help="explicitly resume a stale running run from its bound recovery artifacts",
    )
    args = parser.parse_args()
    plan = verify_formal_run_plan(args.plan)
    selected = select_runs(
        plan,
        run_id=args.run_id,
        config_id=args.config_id,
        seed=args.seed,
        curve=args.curve,
        all_runs=args.all,
    )
    result = dispatch(
        args.plan,
        args.results_root,
        selected_runs=selected,
        execute=args.execute,
        retry_failed=args.retry_failed,
        resume_running=args.resume_running,
        artifact_root=args.artifact_root,
        device=args.device,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
