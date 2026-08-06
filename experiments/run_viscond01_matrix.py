#!/usr/bin/env python3
"""Sequential, resumable dispatcher for the 18-model VISCOND-01 matrix."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from experiments.phase3_v6.scoring.common import atomic_write_json
from experiments.run_comp01_matrix import model_order


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--panel-audit", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--item-batch-size", type=int, default=8)
    return parser.parse_args()


def completed_receipt(path: Path, config_id: str, item_count: int) -> bool:
    if not path.is_file():
        return False
    receipt = json.loads(path.read_text(encoding="utf-8"))
    return (
        receipt.get("status") == "complete"
        and receipt.get("mode") == "full"
        and receipt.get("config_id") == config_id
        and receipt.get("scoring", {}).get("item_count") == item_count
        and receipt.get("scoring", {}).get(
            "aggregate_scientific_result_computed"
        )
        is False
    )


def main() -> None:
    args = parse_args()
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if visible.count(",") or not visible.startswith("GPU-"):
        raise ValueError("dispatcher requires exactly one physical GPU UUID")
    manifest = json.loads(
        args.panel_manifest.resolve().read_text(encoding="utf-8")
    )
    item_count = len(manifest.get("rows", []))
    if item_count < 1_350:
        raise ValueError("VISCOND panel manifest has too few eligible rows")
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
        if completed_receipt(receipt_path, config_id, item_count):
            completed.append(config_id)
            continue
        if model_output.exists() and any(model_output.iterdir()):
            raise FileExistsError(
                "incomplete nonempty model output requires explicit diagnosis: "
                f"{model_output}"
            )
        atomic_write_json(
            state_path,
            {
                "schema_version": 1,
                "status": "running",
                "model_order": ids,
                "completed": completed,
                "current": config_id,
                "item_count": item_count,
                "final_confirmation_accessed": False,
                "scientific_aggregation_performed": False,
            },
        )
        command = [
            sys.executable,
            "-m",
            "experiments.score_viscond01_model",
            "--config-id",
            config_id,
            "--artifact-root",
            str(args.artifact_root),
            "--panel-manifest",
            str(args.panel_manifest),
            "--panel-audit",
            str(args.panel_audit),
            "--output-dir",
            str(model_output),
            "--mode",
            "full",
            "--device",
            "cuda:0",
            "--item-batch-size",
            str(args.item_batch_size),
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
            receipt_path, config_id, item_count
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
                    "item_count": item_count,
                    "final_confirmation_accessed": False,
                    "scientific_aggregation_performed": False,
                },
            )
            raise RuntimeError(f"VISCOND scoring failed for {config_id}")
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
            "item_count": item_count,
            "elapsed_seconds": time.time() - started,
            "final_confirmation_accessed": False,
            "scientific_aggregation_performed": False,
        },
    )
    print(f"status=complete models={len(completed)}", flush=True)


if __name__ == "__main__":
    main()
