#!/usr/bin/env python3
"""Sequential, resumable dispatcher for the frozen 18-model COMP-01 matrix."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from experiments.phase3_risk_v1.budget_configs import (
    load_and_validate_directory,
)
from experiments.phase3_risk_v1.budget_runtime import CONFIG_DIR
from experiments.phase3_v6.scoring.common import atomic_write_json, sha256_file


BUDGET_ORDER = {"low": 0, "current": 1, "high": 2}
METHOD_ORDER = {"M2": 0, "M3": 1}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--panel-audit", type=Path, required=True)
    parser.add_argument("--collision-diagnostic", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--pair-batch-size", type=int, default=8)
    return parser.parse_args()


def model_order() -> list[str]:
    validation = load_and_validate_directory(CONFIG_DIR)
    if validation["config_count"] != 18:
        raise ValueError("frozen budget config family is not 18 models")
    manifest = json.loads(
        (CONFIG_DIR / "manifest.json").read_text(encoding="utf-8")
    )
    configs = []
    for entry in manifest["entries"]:
        path = CONFIG_DIR / entry["relative_path"]
        if sha256_file(path) != entry["sha256"]:
            raise ValueError("config manifest SHA-256 mismatch")
        configs.append(json.loads(path.read_text(encoding="utf-8")))
    configs.sort(
        key=lambda row: (
            BUDGET_ORDER[row["budget"]],
            int(row["mapping_root"]),
            METHOD_ORDER[row["method"]],
        )
    )
    ids = [row["config_id"] for row in configs]
    if len(ids) != 18 or len(set(ids)) != 18:
        raise ValueError("model dispatch identity is incomplete or duplicated")
    return ids


def completed_receipt(path: Path, config_id: str) -> bool:
    if not path.is_file():
        return False
    receipt = json.loads(path.read_text(encoding="utf-8"))
    return (
        receipt.get("status") == "complete"
        and receipt.get("mode") == "full"
        and receipt.get("config_id") == config_id
        and receipt.get("scoring", {}).get("pair_count") == 410
        and receipt.get("scoring", {}).get("aggregate_scientific_result_computed")
        is False
    )


def main() -> None:
    args = parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES", "").count(",") or not os.environ.get(
        "CUDA_VISIBLE_DEVICES", ""
    ).startswith("GPU-"):
        raise ValueError("dispatcher requires exactly one physical GPU UUID")
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "matrix_state.json"
    logs = output / "logs"
    logs.mkdir(exist_ok=True)
    ids = model_order()
    started = time.time()
    completed = []
    for config_id in ids:
        model_output = output / "models" / config_id
        receipt_path = model_output / "run_receipt.json"
        if completed_receipt(receipt_path, config_id):
            completed.append(config_id)
            continue
        if model_output.exists() and any(model_output.iterdir()):
            raise FileExistsError(
                f"incomplete nonempty model output requires explicit diagnosis: {model_output}"
            )
        atomic_write_json(
            state_path,
            {
                "schema_version": 1,
                "status": "running",
                "model_order": ids,
                "completed": completed,
                "current": config_id,
                "final_confirmation_accessed": False,
                "scientific_aggregation_performed": False,
            },
        )
        command = [
            sys.executable,
            "-m",
            "experiments.score_comp01_model",
            "--config-id",
            config_id,
            "--artifact-root",
            str(args.artifact_root),
            "--panel-manifest",
            str(args.panel_manifest),
            "--panel-audit",
            str(args.panel_audit),
            "--collision-diagnostic",
            str(args.collision_diagnostic),
            "--output-dir",
            str(model_output),
            "--mode",
            "full",
            "--device",
            "cuda:0",
            "--pair-batch-size",
            str(args.pair_batch_size),
        ]
        log_path = logs / f"{config_id}.log"
        with log_path.open("wb") as handle:
            result = subprocess.run(
                command,
                cwd=Path(__file__).resolve().parents[1],
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=False,
            )
        if result.returncode != 0 or not completed_receipt(
            receipt_path, config_id
        ):
            atomic_write_json(
                state_path,
                {
                    "schema_version": 1,
                    "status": "failed",
                    "model_order": ids,
                    "completed": completed,
                    "failed": config_id,
                    "returncode": result.returncode,
                    "log_path": str(log_path),
                    "final_confirmation_accessed": False,
                    "scientific_aggregation_performed": False,
                },
            )
            raise RuntimeError(f"COMP-01 scoring failed for {config_id}")
        completed.append(config_id)
        print(
            f"completed={len(completed)}/{len(ids)} config={config_id}",
            flush=True,
        )
    atomic_write_json(
        state_path,
        {
            "schema_version": 1,
            "status": "complete",
            "model_order": ids,
            "completed": completed,
            "current": None,
            "elapsed_seconds": time.time() - started,
            "final_confirmation_accessed": False,
            "scientific_aggregation_performed": False,
        },
    )
    print(f"status=complete models={len(completed)}", flush=True)


if __name__ == "__main__":
    main()
