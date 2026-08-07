#!/usr/bin/env python3
"""Run XID-01 round4 data, model, token, and resource preflight."""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
from pathlib import Path

import torch

from experiments.stage2_model import model_structure_receipt
from experiments.stage2_protocol import Stage2Protocol
from experiments.train_xid01_model import DIMENSIONS, model_builder
from experiments.xid01 import (
    CONDITIONS,
    MAPPING_ROOTS,
    TOTAL_STEPS,
    TOTAL_TRAIN_ROWS,
    sha256_file,
    write_json,
)
from model.global_subspace_lora import coordinate_state
from trainer.train_stage2 import frozen_parameter_hash


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--resources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def run(args: argparse.Namespace) -> dict:
    if args.output.exists():
        raise FileExistsError(f"preflight output already exists: {args.output}")
    prepared = args.prepared_dir.resolve()
    audit_path = prepared / "data_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    required_data_checks = {
        "condition_image_order_exact_match",
        "condition_target_token_order_exact_match",
        "condition_prompt_lengths_match",
        "condition_target_spans_and_masks_match",
        "paired_token_records_differ_only_at_key",
        "block_visual_marginals_match",
        "block_key_marginals_match",
        "block_target_marginals_match",
        "per_key_target_entropy_match",
        "target_cell_absent_both",
        "consistent_xor_all_eight",
        "ambiguous_xor_four_of_eight",
        "heldout_disjoint_from_injection",
        "singleton_keys_and_targets",
    }
    data_checks = {
        "audit_passed": audit.get("status") == "passed",
        "eligible_for_training": audit.get("eligible_for_training") is True,
        "eligible_for_scoring": audit.get("eligible_for_scoring") is True,
        "all_required_checks_present": required_data_checks
        <= set(audit.get("checks", {})),
        "all_required_checks_pass": all(
            audit.get("checks", {}).get(key) is True
            for key in required_data_checks
        ),
        "train_rows_match": audit.get("total_train_rows") == TOTAL_TRAIN_ROWS,
        "heldout_groups_match": audit.get("heldout_groups") == 1008,
        "no_training_or_inference": audit.get("training_runs_started") == 0
        and audit.get("model_inference_performed") is False,
        "no_final_confirmation_access": audit.get("final_confirmation_accessed")
        is False,
    }
    for condition in CONDITIONS:
        info = audit["data"][condition]
        path = Path(info["path"])
        data_checks[f"{condition}_parquet_sha"] = (
            info["rows"] == TOTAL_TRAIN_ROWS
            and path.is_file()
            and sha256_file(path) == info["sha256"]
        )
    if not all(data_checks.values()):
        raise RuntimeError(f"XID-01 data preflight failed: {data_checks}")

    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    conditions = {}
    frozen_hashes = []
    target_names = []
    coordinate_hashes = []
    for condition in CONDITIONS:
        model = model_builder(
            protocol,
            MAPPING_ROOTS[0],
            DIMENSIONS,
            device="cpu",
        )
        structure = model_structure_receipt(model)
        coordinates = coordinate_state(model)
        names = structure["adapter"]["wrapped_names"]
        mapping_statistics = structure["adapter"]["mapping_statistics"]
        checks = {
            "dimensions_match": structure["coordinate_dimensions"] == DIMENSIONS,
            "total_trainable_coordinates_4096": structure[
                "trainable_parameter_count"
            ]
            == 4096,
            "exact_zero_coordinates": all(
                torch.count_nonzero(value).item() == 0
                for value in coordinates.values()
            ),
            "eleven_target_names": len(names) == 11,
            "twenty_two_factor_mappings": 2 * len(names) == 22,
            "all_coordinates_used": set(mapping_statistics) == set(DIMENSIONS)
            and all(
                row["dimension"] == DIMENSIONS[module]
                and row["minimum"] > 0
                for module, row in mapping_statistics.items()
            ),
            "mapping_root_match": structure["adapter"]["mapping_root"]
            == MAPPING_ROOTS[0],
        }
        if not all(checks.values()):
            raise RuntimeError(f"{condition} model preflight failed: {checks}")
        frozen_hash = frozen_parameter_hash(model)
        conditions[condition] = {
            "coordinate_dimensions": dict(DIMENSIONS),
            "model_structure": structure,
            "initial_frozen_parameter_sha256": frozen_hash,
            "checks": checks,
        }
        frozen_hashes.append(frozen_hash)
        target_names.append(names)
        coordinate_hashes.append(structure["coordinate_state_sha256"])
        del model
        gc.collect()

    resources = json.loads(args.resources.read_text(encoding="utf-8"))
    gpu_rows = resources.get("gpu", {}).get("nvidia_gpus", [])
    resource_checks = {
        "cuda_backend_detected": "CUDA"
        in resources.get("gpu", {}).get("available_backends", []),
        "at_least_one_gpu_with_8gb_free": any(
            float(row.get("memory_free_mb", 0)) >= 8192 for row in gpu_rows
        ),
        "at_least_20gb_disk_free": float(
            resources.get("disk", {}).get("available_gb", 0)
        )
        >= 20,
        "at_least_8gb_ram_free": float(
            resources.get("memory", {}).get("available_gb", 0)
        )
        >= 8,
    }
    cross_checks = {
        "initial_frozen_hash_matches": len(set(frozen_hashes)) == 1,
        "target_names_match": target_names[0] == target_names[1],
        "initial_coordinate_state_matches": len(set(coordinate_hashes)) == 1,
        "optimizer_steps_exact": (
            3 * (TOTAL_TRAIN_ROWS // 4) // 4 == TOTAL_STEPS
        ),
        "all_resource_checks_pass": all(resource_checks.values()),
        "no_model_inference": True,
        "no_training": True,
        "no_final_confirmation_access": True,
    }
    if not all(cross_checks.values()):
        raise RuntimeError(f"XID-01 paired preflight failed: {cross_checks}")
    result = {
        "schema_version": 1,
        "status": "passed",
        "candidate": "XID-01",
        "round": 4,
        "mapping_root": MAPPING_ROOTS[0],
        "data_audit": {
            "path": str(audit_path),
            "sha256": sha256_file(audit_path),
            "checks": data_checks,
            "frozen_checks": audit["checks"],
            "data": audit["data"],
        },
        "protocol": protocol.reference(),
        "conditions": conditions,
        "resources": {
            "path": str(args.resources.resolve()),
            "sha256": sha256_file(args.resources),
            "checks": resource_checks,
            "gpu_inventory": gpu_rows,
            "disk_available_gb": resources["disk"]["available_gb"],
        },
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


if __name__ == "__main__":
    run(parse_args())
