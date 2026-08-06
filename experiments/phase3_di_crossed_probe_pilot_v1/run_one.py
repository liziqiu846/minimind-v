#!/usr/bin/env python3
"""Run all frozen shared probes on one existing raw checkpoint."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from pathlib import Path
from typing import Mapping

import torch
from torch.utils.data import DataLoader, Subset
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase3_image_group_dependence_sgd_v1.diagnosis import (
    diagnose_replacement,
)
from experiments.phase3_image_group_dependence_sgd_v1.train_one import (
    _concat_micro_batches,
    _ghost_item,
)
from experiments.phase3_private_vs_shared_v1.adapter_runtime import (
    build_candidate_model,
)
from experiments.stage2_protocol import Stage2Protocol

from .common import REPO_ROOT, sha256_file, write_json

STAGE2_PROTOCOL = REPO_ROOT / "experiments/stage2_protocol_v2.json"


def run(manifest_path: Path, config_id: str, checkpoint_path: Path,
        output: Path, device_name: str) -> dict:
    started = time.time()
    manifest = json.loads(manifest_path.read_text())
    if manifest["identity_audit"]["status"] != "PASS":
        raise RuntimeError("shared-probe identity audit is not PASS")
    model_row = next(row for row in manifest["models"] if row["config_id"] == config_id)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if checkpoint["config"]["config_id"] != config_id:
        raise ValueError("raw checkpoint identity mismatch")
    device = torch.device(device_name)
    torch.use_deterministic_algorithms(True)
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise RuntimeError("CUBLAS_WORKSPACE_CONFIG must equal :4096:8")
    stage2 = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
    model = build_candidate_model(checkpoint["config"], stage2, device=device)
    with torch.no_grad():
        for name, value in checkpoint["coordinates"].items():
            model.stage2_coordinates.coordinates[name].copy_(value.to(device))
    model.train()
    model.vision_encoder.eval()
    tokenizer = AutoTokenizer.from_pretrained(
        stage2.asset_path("tokenizer"), local_files_only=True
    )
    legacy = "M2" if model_row["structure"] == "P" else "M3"
    dataset_args = dict(
        tokenizer=tokenizer,
        model_group=legacy,
        processor=model.processor,
        max_length=450,
        image_token_count=64,
    )
    train = Stage2CaptionDataset(manifest["train_parquet"], **dataset_args)
    ghost = Stage2CaptionDataset(manifest["ghost_parquet"], **dataset_args)
    parameters = list(model.stage2_coordinates.parameters())
    rows = []
    for panel in manifest["panels"]:
        for slot in panel["slots"]:
            indices = [row["dataset_index"] for row in slot["train_batch"]]
            loader = DataLoader(
                Subset(train, indices),
                batch_size=4,
                shuffle=False,
                num_workers=0,
                collate_fn=stage2_collate,
            )
            batch = _concat_micro_batches(list(loader), device)
            result = diagnose_replacement(
                model,
                parameters,
                batch,
                _ghost_item(ghost, slot["ghost_group"]["dataset_index"], device),
                selected_position=slot["selected_position"],
                accumulation=4,
            )
            distance = result["squared_l2_gradient_difference"]
            denominator = (
                result["true_gradient_squared_l2"]
                + result["ghost_gradient_squared_l2"]
            )
            rows.append(
                {
                    "model": config_id,
                    "structure": model_row["structure"],
                    "model_seed": model_row["model_seed"],
                    "panel_id": panel["panel_id"],
                    "probe_seed": panel["probe_seed"],
                    "probe_slot": slot["probe_slot"],
                    "selected_position": slot["selected_position"],
                    "train_group_id": slot["selected_train_group"]["group_id"],
                    "train_image_sha256": slot["selected_train_group"]["image_sha256"],
                    "train_conversation_sha256": slot["selected_train_group"][
                        "conversation_sha256"
                    ],
                    "ghost_group_id": slot["ghost_group"]["group_id"],
                    "ghost_image_sha256": slot["ghost_group"]["image_sha256"],
                    "ghost_conversation_sha256": slot["ghost_group"][
                        "conversation_sha256"
                    ],
                    "squared_l2_gradient_difference": distance,
                    "log10_squared_l2_gradient_difference": math.log10(distance),
                    "normalized_gradient_difference": distance / denominator,
                    **result,
                }
            )
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "per_probe_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    receipt = {
        "status": "complete",
        "config_id": config_id,
        "role": manifest["role"],
        "checkpoint_path": str(checkpoint_path.resolve()),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "pilot_manifest_sha256": sha256_file(manifest_path),
        "probe_assignment_sha256": manifest["probe_assignment_sha256"],
        "row_count": len(rows),
        "per_probe_results_path": str(csv_path.resolve()),
        "per_probe_results_sha256": sha256_file(csv_path),
        "runtime_seconds": time.time() - started,
    }
    write_json(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    print(json.dumps(run(
        args.manifest, args.config_id, args.checkpoint, args.output, args.device
    ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
