#!/usr/bin/env python3
"""Dispatch exactly six existing raw checkpoints across selected GPUs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import REPO_ROOT, write_json


def _one(manifest: Path, model: dict, checkpoint_root: Path,
         output_root: Path, device: str) -> dict:
    config_id = model["config_id"]
    output = output_root / config_id
    receipt = output / "receipt.json"
    if receipt.exists():
        return json.loads(receipt.read_text())
    environment = dict(os.environ)
    environment.update({
        "CUDA_VISIBLE_DEVICES": device,
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "PYTHONUNBUFFERED": "1",
    })
    log = output_root.parent / "logs" / f"{config_id}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "experiments.phase3_di_crossed_probe_pilot_v1.run_one",
        "--manifest", str(manifest.resolve()),
        "--config-id", config_id,
        "--checkpoint", str((checkpoint_root / config_id / "checkpoint.pt").resolve()),
        "--output", str(output.resolve()),
        "--device", "cuda:0",
    ]
    with log.open("wb") as handle:
        completed = subprocess.run(
            command, cwd=REPO_ROOT, env=environment,
            stdout=handle, stderr=subprocess.STDOUT, check=False,
        )
    if completed.returncode:
        raise RuntimeError(f"{config_id} failed; see {log}")
    return json.loads(receipt.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--devices", nargs="+", required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if manifest["identity_audit"]["status"] != "PASS":
        raise RuntimeError("pre-run identity audit failed")
    completed = {}
    with ThreadPoolExecutor(max_workers=len(args.devices)) as pool:
        futures = {
            pool.submit(
                _one, args.manifest, model, args.checkpoint_root,
                args.output_root, args.devices[index % len(args.devices)]
            ): model["config_id"]
            for index, model in enumerate(manifest["models"])
        }
        for future in as_completed(futures):
            completed[futures[future]] = future.result()
            print(json.dumps({
                "config_id": futures[future],
                "row_count": completed[futures[future]]["row_count"],
            }), flush=True)
    write_json(args.output_root / "dispatch_receipt.json", {
        "status": "complete",
        "completed_model_count": len(completed),
        "completed": completed,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
