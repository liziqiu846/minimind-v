#!/usr/bin/env python3
"""Dispatch the immutable 18-candidate matrix with resumable statuses."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .artifacts import load_bound_json, validate_bindings, write_json_atomic
from .configs import generate_matrix


def _run(command: list[str], device: str, log_path: Path, config_id: str,
         output_root: Path, binding: dict[str, str]) -> dict:
    environment = dict(os.environ)
    environment["CUDA_VISIBLE_DEVICES"] = device
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log:
        result = subprocess.run(
            command, env=environment, stdout=log, stderr=subprocess.STDOUT,
            check=False,
        )
    status_path = output_root / config_id / "status.json"
    if result.returncode and not status_path.exists():
        write_json_atomic(status_path, {
            **binding, "config_id": config_id, "status": "failed",
            "error_type": "SubprocessFailureBeforeTrainerReceipt",
            "error": f"training process exited with code {result.returncode}",
            "log_path": str(log_path),
            "automatic_configuration_change": False,
        })
    return {"returncode": result.returncode, "device": device, "command": command}


def dispatch(run_manifest: Path, *, resume: bool) -> dict:
    manifest = load_bound_json(run_manifest)
    if manifest["status"] != "frozen_before_dispatch":
        raise ValueError("run manifest is not dispatchable")
    devices = list(manifest["selected_device_indices"])
    if not devices:
        raise ValueError("run manifest contains no selected devices")
    candidates = generate_matrix()
    if len(manifest["commands"]) != len(candidates):
        raise ValueError("run manifest command count differs from frozen matrix")
    output_root = Path(manifest["output_root"])
    binding = {
        "protocol_sha256": manifest["protocol_sha256"],
        "candidate_matrix_sha256": manifest["candidate_matrix_sha256"],
    }
    jobs = []
    skipped = []
    for config, command in zip(candidates, manifest["commands"]):
        config_id = config["config_id"]
        status_path = output_root / config_id / "status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text(encoding="utf-8"))
            validate_bindings(status)
            if status["status"] == "complete":
                skipped.append(config_id)
                continue
            if status["status"] == "failed" and not resume:
                skipped.append(config_id)
                continue
        jobs.append((config_id, list(command)))
    results = {}
    with ThreadPoolExecutor(max_workers=len(devices)) as pool:
        active = {
            pool.submit(
                _run, command, devices[index % len(devices)],
                output_root / config_id / "training.log",
                config_id, output_root, binding,
            ): config_id
            for index, (config_id, command) in enumerate(jobs)
        }
        for future in as_completed(active):
            results[active[future]] = future.result()
    receipt = {
        "protocol_sha256": manifest["protocol_sha256"],
        "candidate_matrix_sha256": manifest["candidate_matrix_sha256"],
        "run_manifest": str(run_manifest.resolve()),
        "dispatched": sorted(results),
        "skipped": sorted(skipped),
        "results": results,
        "automatic_retry": False,
    }
    write_json_atomic(output_root / "dispatch_receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    result = dispatch(args.run_manifest, resume=args.resume)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(row["returncode"] == 0 for row in result["results"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
