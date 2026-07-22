#!/usr/bin/env python3
"""Verify the two fixed Phase 3 v5 smoke runs and CPU bundle receipts."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import atomic_write_json, load_json_snapshot, load_jsonl_snapshot


def _compare(left: Any, right: Any, path: str, maximum: list[float]) -> None:
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            raise ValueError(f"smoke object keys differ at {path}")
        for key in left:
            _compare(left[key], right[key], f"{path}.{key}", maximum)
    elif isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            raise ValueError(f"smoke list lengths differ at {path}")
        for index, values in enumerate(zip(left, right)):
            _compare(values[0], values[1], f"{path}[{index}]", maximum)
    elif isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        if not math.isfinite(float(left)) or not math.isfinite(float(right)):
            raise ValueError(f"nonfinite smoke value at {path}")
        difference = abs(float(left) - float(right))
        maximum[0] = max(maximum[0], difference)
        if difference > 1e-7:
            raise ValueError(f"smoke determinism tolerance exceeded at {path}: {difference}")
    elif left != right:
        raise ValueError(f"smoke value differs at {path}")


def verify_two_smokes_v5(first: Path, second: Path, first_bundle: dict[str, Any], second_bundle: dict[str, Any]) -> dict[str, Any]:
    for position, verification in enumerate((first_bundle, second_bundle), start=1):
        if (
            verification.get("status") != "verified"
            or verification.get("run_mode") != "smoke"
            or verification.get("image_group_count") != 8
        ):
            raise ValueError(f"smoke {position} CPU bundle verification did not pass")
    first_groups = load_jsonl_snapshot(first / "image_group_results.jsonl", root=first)
    second_groups = load_jsonl_snapshot(second / "image_group_results.jsonl", root=second)
    if (
        len(first_groups) != 8 or len(second_groups) != 8
        or {row.get("model_id") for row in first_groups + second_groups} != {"M1-root-none"}
    ):
        raise ValueError("each smoke must contain M1-root-none on exactly eight image groups")
    maximum = [0.0]
    for name, loader in (
        ("row_level_results.jsonl", load_jsonl_snapshot),
        ("image_group_results.jsonl", load_jsonl_snapshot),
        ("metrics_summary.json", load_json_snapshot),
        ("nll_tail_summary.json", load_json_snapshot),
        ("numerical_diagnostics.json", load_json_snapshot),
    ):
        _compare(loader(first / name, root=first), loader(second / name, root=second), name, maximum)
    for root in (first, second):
        numerical = load_json_snapshot(root / "numerical_diagnostics.json", root=root)
        if any(numerical.get(key) != 0 for key in (
            "nan_inf_count", "caption_clip_low_count", "caption_clip_high_count",
        )):
            raise ValueError("smoke numerical acceptance failed")
        metrics = load_json_snapshot(root / "metrics_summary.json", root=root)
        model = metrics["models"][0]
        if any(value is not None for value in model["fixed_model_bounds"].values()):
            raise ValueError("smoke fixed bounds must be null")
        if any(value is not None for value in model["compression_bounds"].values()):
            raise ValueError("smoke compression bounds must be null")
    return {
        "schema_version": 1, "audit_type": "phase3_v5_two_smoke_determinism",
        "status": "passed", "absolute_tolerance": 1e-7,
        "maximum_observed_absolute_difference": maximum[0],
        "smoke_runs": 2, "model_id": "M1-root-none", "unique_images_per_run": 8,
        "cpu_bundle_verifications": 2,
        "bundle_content_hashes": [first_bundle["bundle_content_hash"], second_bundle["bundle_content_hash"]],
        "shared_input_ids_and_labels_contract": "same tensors passed to correct-image and no-pixel scorer",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-run", type=Path, required=True)
    parser.add_argument("--second-run", type=Path, required=True)
    parser.add_argument("--first-bundle-verification", type=Path, required=True)
    parser.add_argument("--second-bundle-verification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify_two_smokes_v5(
        args.first_run, args.second_run,
        load_json_snapshot(args.first_bundle_verification), load_json_snapshot(args.second_bundle_verification),
    )
    atomic_write_json(args.output, result, overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
