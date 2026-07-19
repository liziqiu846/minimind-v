#!/usr/bin/env python3
"""Dynamically dispatch independent Stage 2 formal models across idle A40 GPUs."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from collections import deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.run_stage2_pipeline import RunSpec, formal_specs, run_commands
from experiments.stage2_protocol import Stage2Protocol, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--max-workers", type=int)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def parse_gpu_inventory(rows: str) -> list[dict[str, Any]]:
    inventory = []
    for row in rows.splitlines():
        if not row.strip():
            continue
        values = [value.strip() for value in row.split(",")]
        if len(values) != 3:
            raise ValueError(f"unexpected nvidia-smi inventory row: {row}")
        name, uuid, free_memory = values
        inventory.append(
            {"name": name, "uuid": uuid, "free_memory_mib": int(free_memory)}
        )
    return inventory


def idle_a40s(eligible: set[str], reserved: set[str]) -> list[dict[str, Any]]:
    inventory_rows = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,uuid,memory.free",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout
    process_rows = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=gpu_uuid",
            "--format=csv,noheader,nounits",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout
    active = {
        row.strip() for row in process_rows.splitlines() if row.strip().startswith("GPU-")
    }
    candidates = [
        gpu
        for gpu in parse_gpu_inventory(inventory_rows)
        if gpu["uuid"] in eligible
        and gpu["uuid"] not in reserved
        and gpu["uuid"] not in active
        and "A40" in gpu["name"]
    ]
    return sorted(candidates, key=lambda gpu: (-gpu["free_memory_mib"], gpu["uuid"]))


def plan_rows(
    specs: list[RunSpec],
    run_root: Path,
    protocol: Stage2Protocol,
    data: Path,
    device: str,
) -> list[dict[str, Any]]:
    rows = []
    for ordinal, spec in enumerate(specs, start=1):
        run_dir = run_root / f"{ordinal:02d}_{spec.name}"
        rows.append(
            {
                "ordinal": ordinal,
                "run": spec.name,
                "directory": str(run_dir),
                "stages": [
                    {"name": name, "command": command, "completion": str(completion)}
                    for name, command, completion in run_commands(
                        spec, run_dir, protocol, "formal", data, device
                    )
                ],
            }
        )
    return rows


def execute_model(
    ordinal: int,
    total: int,
    spec: RunSpec,
    run_dir: Path,
    protocol: Stage2Protocol,
    data: Path,
    device: str,
    gpu: dict[str, Any],
    pipeline_started: float,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["CUDA_VISIBLE_DEVICES"] = gpu["uuid"]
    assignment = {
        "schema_version": 1,
        "status": "running",
        "protocol": protocol.reference(),
        "ordinal": ordinal,
        "run": spec.name,
        "gpu_uuid": gpu["uuid"],
        "gpu_name": gpu["name"],
        "started_unix": time.time(),
    }
    assignment_path = run_dir / "gpu_assignment.json"
    if assignment_path.exists():
        previous = json.loads(assignment_path.read_text(encoding="utf-8"))
        if previous.get("protocol") != protocol.reference() or previous.get("gpu_uuid") != gpu["uuid"]:
            raise ValueError(f"existing assignment differs for run {ordinal}")
    else:
        write_json_atomic(assignment_path, assignment)

    for stage_name, command, completion in run_commands(
        spec, run_dir, protocol, "formal", data, device
    ):
        if completion.exists():
            print(
                f"skip complete {ordinal:02d}/{total} {spec.name} {stage_name} on {gpu['uuid']}",
                flush=True,
            )
            continue
        log_path = run_dir / f"{stage_name}.log"
        if log_path.exists():
            raise RuntimeError(f"partial stage requires audit before restart: {log_path}")
        print(
            f"start {ordinal:02d}/{total} {spec.name} {stage_name} on {gpu['uuid']}",
            flush=True,
        )
        with log_path.open("w", encoding="utf-8") as log:
            log.write(f"CUDA_VISIBLE_DEVICES={gpu['uuid']}\n")
            log.write(shlex.join(command) + "\n")
            log.flush()
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        if result.returncode:
            failure = {
                "schema_version": 1,
                "status": "failed",
                "protocol": protocol.reference(),
                "ordinal": ordinal,
                "run": spec.name,
                "stage": stage_name,
                "returncode": result.returncode,
                "gpu_uuid": gpu["uuid"],
                "log": str(log_path),
                "elapsed_seconds": time.time() - pipeline_started,
            }
            write_json_atomic(run_dir / "failure_receipt.json", failure)
            return failure
        if not completion.exists():
            raise RuntimeError(
                f"stage exited successfully without completion artifact: {completion}"
            )

    complete = assignment | {
        "status": "complete",
        "completed_unix": time.time(),
        "elapsed_seconds": time.time() - assignment["started_unix"],
    }
    write_json_atomic(assignment_path, complete)
    return complete


def progress_payload(
    protocol: Stage2Protocol,
    started: float,
    completed: list[dict[str, Any]],
    active: dict[Future, tuple[int, RunSpec, dict[str, Any]]],
    pending: deque[tuple[int, RunSpec]],
) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "status": "running" if active or pending else "complete",
        "protocol": protocol.reference(),
        "execution_policy": "dynamic_idle_a40_pool",
        "completed_runs": len(completed),
        "completed_run_ordinals": sorted(row["ordinal"] for row in completed),
        "active": [
            {"ordinal": ordinal, "run": spec.name, "gpu_uuid": gpu["uuid"]}
            for ordinal, spec, gpu in active.values()
        ],
        "pending_run_ordinals": [ordinal for ordinal, _ in pending],
        "assignments": completed,
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    args = parse_args()
    if args.poll_seconds <= 0:
        raise ValueError("poll seconds must be positive")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    hardware = protocol.payload.get("hardware_execution")
    if not hardware or hardware.get("policy") != "dynamic_idle_a40_pool":
        raise ValueError("parallel runner requires the frozen dynamic A40 policy")
    configured_workers = hardware["max_parallel_workers"]
    max_workers = args.max_workers or configured_workers
    if not 1 <= max_workers <= configured_workers:
        raise ValueError("max workers is outside the frozen execution limit")

    protocol.verify_immutable_inputs()
    data = protocol.confirmation_directory() / "train.parquet"
    protocol.verify_confirmation_data(data, "train")
    protocol.verify_confirmation_data(
        protocol.confirmation_directory() / "validation.parquet", "validation"
    )
    specs = formal_specs(protocol)
    plan = plan_rows(specs, args.run_root, protocol, data, args.device)
    plan_payload = {
        "schema_version": 2,
        "phase": "formal",
        "protocol": protocol.reference(),
        "execution_policy": "dynamic_idle_a40_pool",
        "per_model_single_physical_gpu": True,
        "max_parallel_workers": max_workers,
        "runs": plan,
    }
    args.run_root.mkdir(parents=True, exist_ok=True)
    plan_path = args.run_root / "pipeline_plan.json"
    if plan_path.exists():
        if json.loads(plan_path.read_text(encoding="utf-8")) != plan_payload:
            raise ValueError("existing parallel plan differs from current immutable plan")
    else:
        write_json_atomic(plan_path, plan_payload)

    if not args.execute:
        print(json.dumps(plan_payload, indent=2, sort_keys=True))
        return

    eligible = set(hardware["eligible_gpu_uuids"])
    available = idle_a40s(eligible, set())
    if available:
        previous_visible = os.environ.get("CUDA_VISIBLE_DEVICES")
        os.environ["CUDA_VISIBLE_DEVICES"] = available[0]["uuid"]
        try:
            protocol.verify_runtime_integrity()
        finally:
            if previous_visible is None:
                os.environ.pop("CUDA_VISIBLE_DEVICES", None)
            else:
                os.environ["CUDA_VISIBLE_DEVICES"] = previous_visible

    started = time.time()
    pending: deque[tuple[int, RunSpec]] = deque(enumerate(specs, start=1))
    active: dict[Future, tuple[int, RunSpec, dict[str, Any]]] = {}
    completed: list[dict[str, Any]] = []
    failed: dict[str, Any] | None = None
    progress_path = args.run_root / "pipeline_progress.json"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while pending or active:
            finished = [future for future in active if future.done()]
            for future in finished:
                ordinal, spec, gpu = active.pop(future)
                try:
                    result = future.result()
                except Exception as error:
                    result = {
                        "schema_version": 1,
                        "status": "failed",
                        "protocol": protocol.reference(),
                        "ordinal": ordinal,
                        "run": spec.name,
                        "gpu_uuid": gpu["uuid"],
                        "error_type": type(error).__name__,
                        "error": str(error),
                        "elapsed_seconds": time.time() - started,
                    }
                    write_json_atomic(
                        args.run_root / f"{ordinal:02d}_{spec.name}" / "failure_receipt.json",
                        result,
                    )
                if result["status"] == "complete":
                    completed.append(result)
                    print(
                        f"complete {ordinal:02d}/{len(specs)} {spec.name} on {gpu['uuid']}",
                        flush=True,
                    )
                elif failed is None:
                    failed = result

            if failed is None and pending:
                reserved = {gpu["uuid"] for _, _, gpu in active.values()}
                candidates = idle_a40s(eligible, reserved)
                while pending and candidates and len(active) < max_workers:
                    ordinal, spec = pending.popleft()
                    gpu = candidates.pop(0)
                    run_dir = args.run_root / f"{ordinal:02d}_{spec.name}"
                    future = executor.submit(
                        execute_model,
                        ordinal,
                        len(specs),
                        spec,
                        run_dir,
                        protocol,
                        data,
                        args.device,
                        gpu,
                        started,
                    )
                    active[future] = (ordinal, spec, gpu)
                    print(
                        f"dispatch {ordinal:02d}/{len(specs)} {spec.name} to {gpu['uuid']}",
                        flush=True,
                    )

            write_json_atomic(
                progress_path,
                progress_payload(protocol, started, completed, active, pending),
            )
            if failed is not None:
                if active:
                    wait(tuple(active), timeout=args.poll_seconds, return_when=FIRST_COMPLETED)
                    continue
                break
            if active:
                wait(tuple(active), timeout=args.poll_seconds, return_when=FIRST_COMPLETED)
            elif pending:
                print("waiting for an idle eligible A40", flush=True)
                time.sleep(args.poll_seconds)

    if failed is not None:
        write_json_atomic(args.run_root / "pipeline_failure.json", failed)
        raise RuntimeError(
            f"formal run {failed.get('ordinal')} failed at {failed.get('stage', 'runner')}"
        )
    final_progress = progress_payload(protocol, started, completed, active, pending)
    final_progress["status"] = "complete"
    final_progress["completed_runs"] = len(specs)
    write_json_atomic(progress_path, final_progress)
    print(f"parallel formal pipeline complete: {len(specs)} runs", flush=True)


if __name__ == "__main__":
    main()
