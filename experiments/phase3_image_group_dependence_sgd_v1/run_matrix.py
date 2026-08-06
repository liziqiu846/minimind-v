#!/usr/bin/env python3
"""Gate, train, and development-evaluate exactly the frozen 12-model matrix."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import PROTOCOL_PATH, sha256_file, write_json_atomic
from .configs import generate_matrix

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def _run(command: list[str], device: str, log_path: Path) -> None:
    environment = dict(os.environ)
    environment.update({
        "CUDA_VISIBLE_DEVICES": device,
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "PYTHONUNBUFFERED": "1",
    })
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log:
        completed = subprocess.run(
            command, cwd=REPO_ROOT, env=environment, stdout=log,
            stderr=subprocess.STDOUT, check=False,
        )
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}); see {log_path}"
        )


def dispatch(
    data_audit_path: Path, trajectory_audit_path: Path,
    results_root: Path, devices: list[str]
) -> dict:
    data_audit = json.loads(data_audit_path.read_text())
    trajectory = json.loads(trajectory_audit_path.read_text())
    if data_audit.get("status") != "PASS" or trajectory.get("status") != "PASS":
        raise RuntimeError("formal matrix gate is not PASS/PASS")
    if _git("status", "--porcelain"):
        raise RuntimeError("formal matrix dispatch requires a clean worktree")
    matrix = generate_matrix()
    if len(matrix) != 12 or any(row["budget"] == 4096 for row in matrix):
        raise RuntimeError("formal matrix is not the frozen 12-model set")
    commit = _git("rev-parse", "HEAD")
    results_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "frozen_before_dispatch",
        "git_commit": commit,
        "git_branch": _git("branch", "--show-current"),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "data_audit_sha256": sha256_file(data_audit_path),
        "trajectory_audit_sha256": sha256_file(trajectory_audit_path),
        "devices": devices,
        "candidate_count": 12,
        "candidates": matrix,
    }
    write_json_atomic(results_root.parent / "run_manifest.json", manifest)

    def one(config: dict, device: str) -> dict:
        config_id = config["config_id"]
        root = results_root / config_id
        training_path = root / "training_manifest.json"
        if not training_path.exists():
            _run([
                sys.executable, "-m",
                "experiments.phase3_image_group_dependence_sgd_v1.train_one",
                "--config-id", config_id,
                "--data-audit", str(data_audit_path.resolve()),
                "--output-root", str(results_root.resolve()),
                "--device", "cuda:0",
            ], device, results_root.parent / "logs" / f"{config_id}.train.log")
        training = json.loads(training_path.read_text())
        development_path = root / "development" / "development_result.json"
        if not development_path.exists():
            _run([
                sys.executable, "-m",
                "experiments.phase3_image_group_dependence_sgd_v1.evaluate_development",
                "--config-id", config_id,
                "--mms2", training["MMS2"]["path"],
                "--checkpoint", training["checkpoint"]["path"],
                "--output-dir", str((root / "development").resolve()),
                "--device", "cuda:0",
            ], device, results_root.parent / "logs" / f"{config_id}.eval.log")
        return {
            "config_id": config_id, "device": device,
            "training_complete": training_path.exists(),
            "development_complete": development_path.exists(),
        }

    completed = {}
    with ThreadPoolExecutor(max_workers=len(devices)) as pool:
        pending = iter(matrix)
        futures = {}
        for device in devices:
            try:
                config = next(pending)
            except StopIteration:
                break
            futures[pool.submit(one, config, device)] = (config["config_id"], device)
        while futures:
            future = next(as_completed(futures))
            config_id, device = futures.pop(future)
            try:
                completed[config_id] = future.result()
            except BaseException:
                for active in futures:
                    active.cancel()
                raise
            print(json.dumps(completed[config_id], sort_keys=True), flush=True)
            try:
                config = next(pending)
            except StopIteration:
                continue
            futures[pool.submit(one, config, device)] = (config["config_id"], device)
    receipt = {**manifest, "status": "complete", "completed": completed}
    write_json_atomic(results_root / "dispatch_receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-audit", type=Path, required=True)
    parser.add_argument("--trajectory-audit", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--devices", nargs="+", required=True)
    args = parser.parse_args()
    dispatch(
        args.data_audit, args.trajectory_audit, args.results_root, args.devices
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
