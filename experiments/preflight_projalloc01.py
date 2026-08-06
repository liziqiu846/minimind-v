#!/usr/bin/env python3
"""Run the frozen CPU/artifact preflight for PROJALLOC-01."""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
from pathlib import Path

import torch

from experiments.projalloc01 import (
    CANDIDATE,
    CONDITIONS,
    PILOT_ROOT,
    ROUND,
    TOTAL_COORDINATES,
    build_model,
    dimensions_for,
    projection_preflight,
    verify_prepared_dir,
)
from experiments.stage2_model import model_structure_receipt
from experiments.stage2_protocol import Stage2Protocol
from experiments.vissup01 import write_json
from model.global_subspace_lora import coordinate_state
from trainer.train_stage2 import frozen_parameter_hash


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def run(args: argparse.Namespace) -> dict:
    if args.output.exists():
        raise FileExistsError(f"preflight output already exists: {args.output}")
    prepared = verify_prepared_dir(args.prepared_dir)
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    conditions = {}
    frozen_hashes = []
    target_names = []
    for condition in CONDITIONS:
        dimensions = dimensions_for(condition)
        projection = projection_preflight(condition, PILOT_ROOT)
        model = build_model(
            protocol,
            PILOT_ROOT,
            dimensions,
            device="cpu",
        )
        structure = model_structure_receipt(model)
        coordinates = coordinate_state(model)
        zero = all(
            torch.count_nonzero(value).item() == 0
            for value in coordinates.values()
        )
        frozen_hash = frozen_parameter_hash(model)
        names = structure["adapter"]["wrapped_names"]
        checks = {
            "dimensions_match": structure["coordinate_dimensions"]
            == dimensions,
            "total_trainable_coordinates_4096": structure[
                "trainable_parameter_count"
            ]
            == TOTAL_COORDINATES,
            "exact_zero_coordinates": zero,
            "eleven_target_names": len(names) == 11,
            "twenty_two_factor_mappings": structure["adapter"][
                "mapping_factor_count"
            ]
            == 22,
            "all_coordinates_used": projection[
                "all_coordinates_used"
            ],
            "mapping_reproducible": projection[
                "all_roots_reproducible"
            ],
        }
        if not all(checks.values()):
            raise RuntimeError(f"{condition} preflight failed: {checks}")
        conditions[condition] = {
            "coordinate_dimensions": dimensions,
            "model_structure": structure,
            "projection_preflight": projection,
            "initial_frozen_parameter_sha256": frozen_hash,
            "checks": checks,
        }
        frozen_hashes.append(frozen_hash)
        target_names.append(names)
        del model
        gc.collect()
    cross_checks = {
        "initial_frozen_hash_matches": len(set(frozen_hashes)) == 1,
        "target_names_match": target_names[0] == target_names[1],
        "prepared_artifacts_match_frozen_sha": True,
        "no_model_inference": True,
        "no_training": True,
        "no_final_confirmation_access": True,
    }
    if not all(cross_checks.values()):
        raise RuntimeError(f"paired preflight failed: {cross_checks}")
    result = {
        "schema_version": 1,
        "status": "passed",
        "candidate": CANDIDATE,
        "round": ROUND,
        "mapping_root": PILOT_ROOT,
        "prepared_artifact_sha256": prepared,
        "protocol": protocol.reference(),
        "conditions": conditions,
        "cross_condition_checks": cross_checks,
        "git": {
            "commit": _git("rev-parse", "HEAD"),
            "tracked_status": _git(
                "status", "--porcelain", "--untracked-files=no"
            ),
        },
        "final_confirmation_accessed": False,
    }
    write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
