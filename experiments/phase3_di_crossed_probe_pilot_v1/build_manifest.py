#!/usr/bin/env python3
"""Freeze shared checkpoint-only probe panels and identity audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

from . import (
    BUDGET,
    MODEL_SEEDS,
    PANELS,
    PILOT_ID,
    PROBE_SEEDS,
    SLOTS,
    STRUCTURES,
)
from .common import canonical_bytes, sha256_file, write_json


def _permutation(size: int, seed: int, role: str) -> list[int]:
    return sorted(
        range(size),
        key=lambda index: hashlib.sha256(
            f"{PILOT_ID}|probe_seed={seed}|{role}|{index}".encode()
        ).digest(),
    )


def _position(seed: int, slot: int) -> int:
    digest = hashlib.sha256(
        f"{PILOT_ID}|probe_seed={seed}|slot={slot}|position".encode()
    ).digest()
    return int.from_bytes(digest[:8], "little") % 16


def build(data_audit_path: Path, output: Path) -> dict:
    audit = json.loads(data_audit_path.read_text())
    if audit["status"] != "PASS":
        raise RuntimeError("source data audit is not PASS")
    train_path = Path(audit["artifacts"]["train"]["path"])
    ghost_path = Path(audit["artifacts"]["ghost_pool"]["path"])
    if (
        sha256_file(train_path) != audit["artifacts"]["train"]["sha256"]
        or sha256_file(ghost_path) != audit["artifacts"]["ghost_pool"]["sha256"]
    ):
        raise ValueError("source train/ghost parquet changed")
    columns = ["catalog_unit_id", "image_sha256", "canonical_conversation"]
    train = pq.read_table(train_path, columns=columns).to_pydict()
    ghost = pq.read_table(ghost_path, columns=columns).to_pydict()
    panels = []
    for panel_id, probe_seed in enumerate(PROBE_SEEDS):
        train_order = _permutation(len(train["catalog_unit_id"]), probe_seed, "train")
        ghost_order = _permutation(len(ghost["catalog_unit_id"]), probe_seed, "ghost")
        slots = []
        for slot_id in range(SLOTS):
            indices = train_order[slot_id * 16:(slot_id + 1) * 16]
            position = _position(probe_seed, slot_id)
            ghost_index = ghost_order[slot_id]
            batch = [
                {
                    "dataset_index": index,
                    "group_id": train["catalog_unit_id"][index],
                    "image_sha256": train["image_sha256"][index],
                    "conversation_sha256": hashlib.sha256(
                        train["canonical_conversation"][index].encode()
                    ).hexdigest(),
                }
                for index in indices
            ]
            replacement = {
                "dataset_index": ghost_index,
                "group_id": ghost["catalog_unit_id"][ghost_index],
                "image_sha256": ghost["image_sha256"][ghost_index],
                "conversation_sha256": hashlib.sha256(
                    ghost["canonical_conversation"][ghost_index].encode()
                ).hexdigest(),
            }
            slots.append(
                {
                    "panel_id": panel_id,
                    "probe_seed": probe_seed,
                    "probe_slot": slot_id,
                    "selected_position": position,
                    "train_batch": batch,
                    "selected_train_group": batch[position],
                    "ghost_group": replacement,
                }
            )
        panels.append(
            {
                "panel_id": panel_id,
                "probe_seed": probe_seed,
                "slots": slots,
                "panel_core_sha256": hashlib.sha256(canonical_bytes(slots)).hexdigest(),
            }
        )
    models = [
        {
            "config_id": f"{structure}-budget-{BUDGET}-seed-{model_seed}",
            "structure": structure,
            "model_seed": model_seed,
        }
        for structure in STRUCTURES
        for model_seed in MODEL_SEEDS
    ]
    assignment = {
        "panels": [
            {
                "panel_id": panel["panel_id"],
                "probe_seed": panel["probe_seed"],
                "panel_core_sha256": panel["panel_core_sha256"],
            }
            for panel in panels
        ]
    }
    assignment_sha = hashlib.sha256(canonical_bytes(assignment)).hexdigest()
    bindings = [
        {"config_id": model["config_id"], "probe_assignment_sha256": assignment_sha}
        for model in models
    ]
    identity_pass = len({row["probe_assignment_sha256"] for row in bindings}) == 1
    manifest = {
        "schema_version": 1,
        "status": "frozen_before_execution" if identity_pass else "identity_audit_failed",
        "pilot_id": PILOT_ID,
        "role": "checkpoint_only_measurement_calibration_not_trajectory_D_I",
        "budget": BUDGET,
        "model_seeds": list(MODEL_SEEDS),
        "probe_seeds": list(PROBE_SEEDS),
        "model_seed_in_probe_sampling": False,
        "panel_count_K": PANELS,
        "slots_per_panel_T": SLOTS,
        "diagnosis_count": len(models) * PANELS * SLOTS,
        "calibration_grid": {"K": [1, 2, 3], "T": [11, 22, 33]},
        "decision_thresholds_frozen_before_results": {
            "probe_to_structure_ratio_raw_and_log_at_most": 1.0,
            "bootstrap_aggregate_cv_at_most": 0.20,
            "paired_sign_retention_at_least": 0.90,
            "maximum_single_probe_share_at_most": 0.20,
            "top3_probe_share_at_most": 0.50,
            "paired_direction_consistent_across_all_panels": True,
        },
        "models": models,
        "panels": panels,
        "probe_assignment_sha256": assignment_sha,
        "identity_audit": {
            "status": "PASS" if identity_pass else "FAIL",
            "model_bindings": bindings,
            "all_six_models_identical": identity_pass,
        },
        "source_data_audit_path": str(data_audit_path.resolve()),
        "source_data_audit_sha256": sha256_file(data_audit_path),
        "train_parquet": str(train_path.resolve()),
        "train_parquet_sha256": sha256_file(train_path),
        "ghost_parquet": str(ghost_path.resolve()),
        "ghost_parquet_sha256": sha256_file(ghost_path),
        "final_confirmation_accessed": False,
    }
    write_json(output, manifest)
    if not identity_pass:
        raise RuntimeError("shared-probe identity audit failed")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.data_audit, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
