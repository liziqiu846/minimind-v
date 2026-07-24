#!/usr/bin/env python3
"""Run train, MMS2 encode, and frozen-v6 scoring for one budget config."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from experiments.phase3_risk_v1.budget_runtime import (
    V6_PYTHON_PATH,
    load_frozen_config,
)
from experiments.phase3_v6.scoring.common import (
    REPO_ROOT,
    atomic_write_json,
    sha256_file,
)


def _run_stage(
    name: str,
    command: list[str],
    *,
    log_path: Path,
    environment: dict[str, str],
) -> dict:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("wb") as log:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    receipt = {
        "stage": name,
        "command": command,
        "returncode": result.returncode,
        "seconds": time.time() - started,
        "log_path": str(log_path),
        "log_sha256": sha256_file(log_path),
    }
    if result.returncode:
        raise RuntimeError(
            f"{name} failed with return code {result.returncode}; "
            f"see {log_path}"
        )
    return receipt


def run(args: argparse.Namespace) -> dict:
    config, config_receipt = load_frozen_config(args.config_id)
    if config["budget"] == "current":
        raise ValueError("current models must not be retrained")
    root = args.artifact_root.resolve()
    run_dir = root / config["output_relative_path"]
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    started = time.time()
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    stages = []
    try:
        common = [
            "--config-id",
            config["config_id"],
            "--artifact-root",
            str(root),
        ]
        stages.append(
            _run_stage(
                "training",
                [
                    sys.executable,
                    "-m",
                    "experiments.phase3_risk_v1.train_budget_model",
                    *common,
                    "--output-dir",
                    str(run_dir / "training"),
                    "--device",
                    "cuda:0",
                ],
                log_path=run_dir / "logs/training.log",
                environment=environment,
            )
        )
        stages.append(
            _run_stage(
                "quantization",
                [
                    sys.executable,
                    "-m",
                    "experiments.phase3_risk_v1.quantize_budget_model",
                    *common,
                    "--training-manifest",
                    str(run_dir / "training/training_manifest.json"),
                    "--output-dir",
                    str(run_dir / "encode"),
                ],
                log_path=run_dir / "logs/quantization.log",
                environment=environment,
            )
        )
        stages.append(
            _run_stage(
                "scoring_and_risk",
                [
                    str(V6_PYTHON_PATH),
                    "-m",
                    "experiments.phase3_risk_v1.score_budget_model",
                    *common,
                    "--adapter-summary",
                    str(run_dir / "encode/adapter_summary.json"),
                    "--output-dir",
                    str(run_dir / "scoring"),
                    "--device",
                    "cuda:0",
                ],
                log_path=run_dir / "logs/scoring.log",
                environment=environment,
            )
        )
        receipt = {
            "schema_version": 1,
            "status": "complete",
            "config_id": config["config_id"],
            "config": config_receipt,
            "run_dir": str(run_dir),
            "gpu_uuid": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "stages": stages,
            "training_manifest": str(
                run_dir / "training/training_manifest.json"
            ),
            "adapter_summary": str(
                run_dir / "encode/adapter_summary.json"
            ),
            "scoring_receipt": str(
                run_dir / "scoring/scoring_receipt.json"
            ),
            "model_summary": str(run_dir / "scoring/model_summary.json"),
            "seconds": time.time() - started,
            "automatic_retry": False,
        }
        atomic_write_json(run_dir / "run_receipt.json", receipt)
        return receipt
    except BaseException as error:
        atomic_write_json(
            run_dir / "run_receipt.json",
            {
                "schema_version": 1,
                "status": "failed",
                "config_id": config["config_id"],
                "config": config_receipt,
                "run_dir": str(run_dir),
                "gpu_uuid": os.environ.get("CUDA_VISIBLE_DEVICES"),
                "completed_stages": stages,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
