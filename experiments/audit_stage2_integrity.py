#!/usr/bin/env python3
"""Audit frozen Stage 2 v2 runtime integrity and guarded model loading."""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_model import build_stage2_model, model_structure_receipt
from experiments.stage2_protocol import Stage2Protocol, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-model-load", action="store_true")
    parser.add_argument("--verify-confirmation", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"integrity receipt already exists: {args.output}")
    started = time.time()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    runtime = protocol.verify_runtime_integrity()
    model_loads = []
    if not args.skip_model_load:
        for group in ("M0", "M1", "M2", "M3"):
            model = build_stage2_model(
                group,
                protocol,
                None if group == "M1" else 43101,
                device="cpu",
            )
            structure = model_structure_receipt(model)
            model_loads.append(
                {
                    "model_group": group,
                    "mapping_root": None if group == "M1" else 43101,
                    "initial_llm_load": structure["adapter"]["initial_llm_load"],
                    "trainable_parameter_count": structure["trainable_parameter_count"],
                    "coordinate_dimensions": structure["coordinate_dimensions"],
                }
            )
            del model
            gc.collect()
    confirmation = None
    if args.verify_confirmation:
        directory = protocol.confirmation_directory()
        confirmation = {
            role: protocol.verify_confirmation_data(directory / f"{role}.parquet", role)
            for role in ("train", "validation")
        }
    result = {
        "schema_version": 2,
        "status": "passed",
        "protocol": protocol.reference(),
        "runtime_integrity": runtime,
        "model_load_guard": {
            "executed": not args.skip_model_load,
            "groups": model_loads,
            "all_initial_language_tensors_exact": all(
                row["initial_llm_load"]["exact_initial_tensor_match"]
                for row in model_loads
            )
            if model_loads
            else None,
        },
        "confirmation_receipts": confirmation,
        "elapsed_seconds": time.time() - started,
    }
    write_json_atomic(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
