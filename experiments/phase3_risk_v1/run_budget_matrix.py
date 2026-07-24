#!/usr/bin/env python3
"""Dispatch the gated 12-model budget matrix onto idle eligible A40 GPUs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from experiments.phase3.stage2_adapter_loader import (
    verify_stage2_source_integrity,
)
from experiments.phase3_risk_v1.budget_runtime import (
    STAGE2_PROTOCOL_PATH,
    available_eligible_gpus,
    load_frozen_config,
)
from experiments.phase3_v6.scoring.common import REPO_ROOT, atomic_write_json


GATE = ["M2-low-seed-43101", "M3-low-seed-43101"]
REMAINING = [
    f"{method}-{budget}-seed-{root}"
    for budget, roots in (
        ("low", (43102, 43103)),
        ("high", (43101, 43102, 43103)),
    )
    for root in roots
    for method in ("M2", "M3")
]


def _require_absent_outputs(
    artifact_root: Path, config_ids: list[str]
) -> None:
    existing = []
    for config_id in config_ids:
        config, _ = load_frozen_config(config_id)
        path = artifact_root / config["output_relative_path"]
        if path.exists():
            existing.append(str(path))
    if existing:
        raise FileExistsError(
            "refusing to overwrite or resume existing budget runs: "
            + ", ".join(existing)
        )


def _terminate_all(active: dict[str, dict]) -> None:
    for value in active.values():
        process = value["process"]
        if process.poll() is None:
            process.terminate()
    for value in active.values():
        process = value["process"]
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def dispatch(
    artifact_root: Path,
    config_ids: list[str],
    *,
    max_workers: int,
    poll_seconds: int,
    allow_shared_gpu: bool,
    minimum_free_memory_mib: int,
) -> list[dict]:
    protocol = verify_stage2_source_integrity(str(STAGE2_PROTOCOL_PATH))
    _require_absent_outputs(artifact_root, config_ids)
    pending = list(config_ids)
    active: dict[str, dict] = {}
    finished = []
    while pending or active:
        live_uuids = {value["gpu"]["uuid"] for value in active.values()}
        available = [
            gpu
            for gpu in available_eligible_gpus(
                protocol,
                allow_shared=allow_shared_gpu,
                minimum_free_memory_mib=minimum_free_memory_mib,
            )
            if gpu["uuid"] not in live_uuids
        ]
        while pending and available and len(active) < max_workers:
            config_id = pending.pop(0)
            gpu = available.pop(0)
            environment = dict(os.environ)
            environment["CUDA_VISIBLE_DEVICES"] = gpu["uuid"]
            environment["PYTHONUNBUFFERED"] = "1"
            environment["PHASE3_ALLOW_SHARED_GPU"] = (
                "1" if allow_shared_gpu else "0"
            )
            environment["PHASE3_MIN_FREE_MEMORY_MIB"] = str(
                minimum_free_memory_mib
            )
            command = [
                sys.executable,
                "-m",
                "experiments.phase3_risk_v1.run_one_budget",
                "--config-id",
                config_id,
                "--artifact-root",
                str(artifact_root),
            ]
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            active[config_id] = {
                "process": process,
                "gpu": gpu,
                "command": command,
                "started_unix_time": time.time(),
            }
            print(
                json.dumps(
                    {
                        "event": "started",
                        "config_id": config_id,
                        "gpu_uuid": gpu["uuid"],
                        "free_memory_mib_at_dispatch": gpu[
                            "free_memory_mib"
                        ],
                        "shared_gpu_execution": gpu[
                            "active_compute_process"
                        ],
                        "minimum_free_memory_mib": (
                            minimum_free_memory_mib
                        ),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        completed_ids = []
        for config_id, value in active.items():
            returncode = value["process"].poll()
            if returncode is None:
                continue
            stdout = value["process"].stdout.read()
            result = {
                "config_id": config_id,
                "gpu_uuid": value["gpu"]["uuid"],
                "returncode": returncode,
                "seconds": time.time() - value["started_unix_time"],
                "worker_stdout_tail": stdout[-8000:],
            }
            finished.append(result)
            completed_ids.append(config_id)
            print(
                json.dumps(
                    {
                        "event": "finished",
                        "config_id": config_id,
                        "gpu_uuid": value["gpu"]["uuid"],
                        "returncode": returncode,
                        "seconds": result["seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            if returncode:
                for item in completed_ids:
                    active.pop(item, None)
                _terminate_all(active)
                raise RuntimeError(
                    f"{config_id} failed; no task was retried and dispatch "
                    "has stopped"
                )
        for config_id in completed_ids:
            active.pop(config_id)
        if pending or active:
            if pending and not active and not available:
                print(
                    json.dumps(
                        {
                            "event": (
                                "waiting_for_sufficient_memory_eligible_A40"
                                if allow_shared_gpu
                                else "waiting_for_idle_eligible_A40"
                            ),
                            "pending_count": len(pending),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
            time.sleep(poll_seconds)
    return finished


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("gate", "remaining"), required=True
    )
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--max-workers", type=int, default=7)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--allow-shared-gpu", action="store_true")
    parser.add_argument("--minimum-free-memory-mib", type=int, default=0)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.max_workers <= 7:
        raise ValueError("max-workers must be between one and seven")
    if args.minimum_free_memory_mib < 0:
        raise ValueError("minimum-free-memory-mib must be non-negative")
    if not args.allow_shared_gpu and args.minimum_free_memory_mib:
        raise ValueError(
            "minimum-free-memory-mib requires --allow-shared-gpu"
        )
    root = args.artifact_root.resolve()
    gate_path = root / (
        "experiments/runs/phase3_risk_v1/gate_low_43101.json"
    )
    requested = GATE if args.phase == "gate" else REMAINING
    if args.phase == "remaining":
        if not gate_path.is_file():
            raise FileNotFoundError("passed low-43101 gate receipt is absent")
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        if gate.get("passed") is not True:
            raise RuntimeError("low-43101 gate did not pass")
    started = time.time()
    try:
        results = dispatch(
            root,
            requested,
            max_workers=args.max_workers,
            poll_seconds=args.poll_seconds,
            allow_shared_gpu=args.allow_shared_gpu,
            minimum_free_memory_mib=args.minimum_free_memory_mib,
        )
        if args.phase == "gate":
            gate_path.parent.mkdir(parents=True, exist_ok=True)
            check = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "experiments.phase3_risk_v1.check_budget_gate",
                    "--artifact-root",
                    str(root),
                    "--output",
                    str(gate_path),
                ],
                cwd=REPO_ROOT,
                check=False,
            )
            if check.returncode:
                raise RuntimeError("low-43101 pair failed the first gate")
        receipt = {
            "schema_version": 1,
            "status": "complete",
            "phase": args.phase,
            "requested_configs": requested,
            "results": results,
            "gate_receipt": str(gate_path),
            "seconds": time.time() - started,
            "automatic_retry": False,
            "resource_policy": {
                "allow_shared_gpu": args.allow_shared_gpu,
                "minimum_free_memory_mib": args.minimum_free_memory_mib,
                "user_authorized": args.allow_shared_gpu,
            },
        }
        atomic_write_json(args.receipt, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        atomic_write_json(
            args.receipt,
            {
                "schema_version": 1,
                "status": "failed",
                "phase": args.phase,
                "requested_configs": requested,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
                "resource_policy": {
                    "allow_shared_gpu": args.allow_shared_gpu,
                    "minimum_free_memory_mib": (
                        args.minimum_free_memory_mib
                    ),
                    "user_authorized": args.allow_shared_gpu,
                },
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
