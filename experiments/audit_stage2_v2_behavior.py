#!/usr/bin/env python3
"""Certify that v2 changes do not reopen Stage 2 learning-rate selection."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import sha256_file, write_json_atomic
from experiments.stage2_protocol import Stage2Protocol
from experiments.stage2_model import build_stage2_model, tensor_state_sha256


BASE_COMMIT = "d1ebfb463e6f3c2ae7cd9436ade5994396b2f9e7"


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def ast_function_hash(source: bytes, function_names: tuple[str, ...]) -> str:
    tree = ast.parse(source.decode("utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    missing = [name for name in function_names if name not in functions]
    if missing:
        raise ValueError(f"source lacks audited functions: {missing}")
    canonical = "\n".join(ast.dump(functions[name], include_attributes=False) for name in function_names)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compare_functions(path: str, names: tuple[str, ...]) -> dict:
    historical = ast_function_hash(git_blob(BASE_COMMIT, path), names)
    current = ast_function_hash((REPO_ROOT / path).read_bytes(), names)
    return {
        "path": path,
        "functions": list(names),
        "base_ast_sha256": historical,
        "current_ast_sha256": current,
        "unchanged": historical == current,
    }


def compare_whole_file(path: str) -> dict:
    historical = hashlib.sha256(git_blob(BASE_COMMIT, path)).hexdigest()
    current = sha256_file(REPO_ROOT / path)
    return {
        "path": path,
        "base_sha256": historical,
        "current_sha256": current,
        "unchanged": historical == current,
    }


def smoke_receipt(path: Path, group: str) -> dict:
    manifest_path = path / "training_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_dimensions = {
        "M0": {"language": 4096},
        "M1": {"projector_layer_1": 2048, "projector_layer_2": 2048},
        "M2": {"vision": 582, "projector": 2327, "language": 1187},
        "M3": {"shared": 4096},
    }
    coordinates = torch.load(path / "coordinates.pt", map_location="cpu", weights_only=True)
    coordinate_state = coordinates.get("coordinates", coordinates)
    invariants = {
        "status_complete": payload.get("status") == "complete",
        "model_group": payload.get("model_group") == group,
        "sample_count_256": payload.get("data", {}).get("examples") == 256,
        "optimizer_steps_48": payload.get("training", {}).get("optimizer_steps") == 48,
        "epochs_3": payload.get("training", {}).get("epochs") == 3,
        "coordinate_dimensions": payload.get("coordinates", {}).get("dimensions")
        == expected_dimensions[group],
        "only_coordinates_trainable": payload.get("model", {})
        .get("initial_structure", {})
        .get("trainable_parameter_count")
        == 4096,
        "frozen_parameters_unchanged": payload.get("model", {}).get(
            "initial_frozen_parameter_sha256"
        )
        == payload.get("model", {}).get("final_frozen_parameter_sha256"),
        "initial_llm_exact": payload.get("model", {})
        .get("initial_structure", {})
        .get("adapter", {})
        .get("initial_llm_load", {})
        .get("exact_initial_tensor_match")
        is True,
        "coordinates_nonzero_after_training": any(
            torch.count_nonzero(value).item() > 0 for value in coordinate_state.values()
        ),
    }
    if not all(invariants.values()):
        raise ValueError(f"{group} behavior smoke has a failed invariant: {invariants}")
    return {
        "model_group": group,
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": sha256_file(manifest_path),
        "coordinates_sha256": sha256_file(path / "coordinates.pt"),
        "mean_micro_batch_loss": payload["training"]["mean_micro_batch_loss"],
        "invariants": invariants,
    }


def cross_protocol_model_equivalence() -> list[dict]:
    v1 = Stage2Protocol.load(REPO_ROOT / "experiments/stage2_protocol.draft.json")
    v2 = Stage2Protocol.load(REPO_ROOT / "experiments/stage2_protocol_v2.draft.json")
    rows = []
    for group in ("M0", "M1", "M2", "M3"):
        root = None if group == "M1" else 43101
        v1_model = build_stage2_model(group, v1, root, device="cpu")
        v1_hash = tensor_state_sha256(v1_model.state_dict())
        del v1_model
        v2_model = build_stage2_model(group, v2, root, device="cpu")
        v2_hash = tensor_state_sha256(v2_model.state_dict())
        del v2_model
        if v1_hash != v2_hash:
            raise ValueError(f"{group} initial model state differs between v1 and v2")
        rows.append(
            {
                "model_group": group,
                "mapping_root": root,
                "v1_model_state_sha256": v1_hash,
                "v2_model_state_sha256": v2_hash,
                "exactly_equal": True,
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"behavior audit output exists: {args.output}")
    whole_files = [
        compare_whole_file(path)
        for path in (
            "model/model_vlm.py",
            "model/global_subspace_lora.py",
            "dataset/stage2_dataset.py",
            "experiments/generalization_bound.py",
        )
    ]
    function_groups = [
        compare_functions(
            "trainer/train_stage2.py",
            (
                "seed_everything",
                "permutation_for_epoch",
                "permutation_sha256",
                "learning_rate_at",
                "move_pixels",
                "frozen_parameter_hash",
            ),
        ),
        compare_functions(
            "experiments/quantize_stage2_adapter.py",
            (
                "ordered_coordinate_names",
                "quantize_coordinate",
                "encode_mms2",
                "decode_mms2",
            ),
        ),
        compare_functions(
            "experiments/evaluate_stage2_risk.py", ("sample_risk_bits",)
        ),
        compare_functions(
            "experiments/compute_stage2_bound.py", ("parse_args",)
        ),
    ]
    smoke = [smoke_receipt(args.smoke_root / group, group) for group in ("M0", "M1", "M2", "M3")]
    model_equivalence = cross_protocol_model_equivalence()
    unchanged = all(row["unchanged"] for row in whole_files + function_groups)
    if not unchanged:
        raise ValueError("a behavior-critical v1 implementation component changed")
    result = {
        "schema_version": 1,
        "status": "passed",
        "base_commit": BASE_COMMIT,
        "purpose": "gate reuse of v1-selected learning rates for v2",
        "whole_file_equivalence": whole_files,
        "function_ast_equivalence": function_groups,
        "smoke_sample_count_per_group": 256,
        "smoke_runs": smoke,
        "cross_protocol_initial_model_state": model_equivalence,
        "allowed_v2_changes": [
            "confirmation sampling and duplicate-aware identity bookkeeping",
            "duplicate-aware visual diagnostic pairing",
            "strict model-load validation and runtime-integrity guards",
            "receipt schema and final-report scope language",
        ],
        "conclusion": {
            "model_training_codec_risk_bound_behavior_changed": False,
            "reuse_v1_selected_learning_rates": True,
            "rerun_36_development_experiments": False,
        },
    }
    write_json_atomic(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
