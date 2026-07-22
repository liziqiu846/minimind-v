#!/usr/bin/env python3
"""Create the engineering-only Phase 3 v5 pilot summary."""

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

from experiments.phase3.canonical_io import atomic_write_bytes, atomic_write_json, load_json_snapshot, load_jsonl_snapshot


def summarize_pilot_v5(run_dir: Path, bundle_verification: dict[str, Any]) -> dict[str, Any]:
    rows = load_jsonl_snapshot(run_dir / "row_level_results.jsonl", root=run_dir)
    groups = load_jsonl_snapshot(run_dir / "image_group_results.jsonl", root=run_dir)
    timing = load_json_snapshot(run_dir / "timing.json", root=run_dir)
    numerical = load_json_snapshot(run_dir / "numerical_diagnostics.json", root=run_dir)
    models = ["M1-root-none", "M3-root-43101"]
    if (
        len(rows) != 1038
        or len(groups) != 306
        or bundle_verification.get("status") != "verified"
        or bundle_verification.get("run_mode") != "pilot"
        or bundle_verification.get("row_count") != 1038
        or bundle_verification.get("image_group_count") != 306
    ):
        raise ValueError("pilot row/group/bundle completeness mismatch")
    row_identities: dict[str, list[tuple[int, str, str]]] = {}
    for model in models:
        selected = [row for row in groups if row["model_id"] == model]
        if len(selected) != 153 or len({row["filename"] for row in selected}) != 153:
            raise ValueError(f"pilot image count mismatch: {model}")
        model_rows = [row for row in rows if row["model_id"] == model]
        if len(model_rows) != 519:
            raise ValueError(f"pilot source-row count mismatch: {model}")
        row_identities[model] = [
            (int(row["row_index"]), str(row["row_key"]), str(row["filename"]))
            for row in model_rows
        ]
    if row_identities[models[0]] != row_identities[models[1]]:
        raise ValueError("pilot models did not evaluate exactly the same source rows in the same order")
    maximum_identity_error = 0.0
    for row in rows:
        error = abs(row["robust_positive_brier_risk"] - (row["positive_brier_mean"] + row["positive_brier_dispersion"]))
        maximum_identity_error = max(maximum_identity_error, error)
        if error > 1e-12 or not 0.0 <= row["robust_positive_brier_risk"] <= 2.0 or not 0.0 <= row["visual_semantic_loss"] <= 1.0:
            raise ValueError("pilot v5 algebra/support check failed")
    if any(int(numerical.get(key, -1)) != 0 for key in (
        "caption_clip_low_count", "caption_clip_high_count", "nan_inf_count",
    )):
        raise ValueError("pilot numerical diagnostics failed")
    if (
        not isinstance(timing.get("elapsed_seconds"), (int, float))
        or not math.isfinite(float(timing["elapsed_seconds"]))
        or float(timing["elapsed_seconds"]) <= 0.0
        or not isinstance(timing.get("max_memory_allocated_bytes"), int)
        or timing["max_memory_allocated_bytes"] < 0
    ):
        raise ValueError("pilot timing/peak-memory record is invalid")
    return {
        "schema_version": 1, "summary_type": "phase3_v5_engineering_pilot",
        "status": "passed", "conclusion_scope": "engineering_feasibility_only_no_model_ranking",
        "model_ids": models, "unique_images_per_model": 153, "row_results": len(rows),
        "model_image_groups": len(groups), "maximum_max_mean_dispersion_identity_error": maximum_identity_error,
        "elapsed_seconds": timing["elapsed_seconds"],
        "seconds_per_unique_image_model_pair": timing["elapsed_seconds"] / 306.0,
        "max_memory_allocated_bytes": timing["max_memory_allocated_bytes"],
        "bundle_content_hash": bundle_verification["bundle_content_hash"],
        "bundle_verification_status": "verified",
        "protocol_change_after_pilot": False,
    }


def render_pilot_markdown(summary: dict[str, Any]) -> str:
    return (
        "# Phase 3 v5 Pilot 工程摘要\n\n"
        "Pilot 仅验证工程可行性，不比较模型优劣，也不用于修改正式指标。\n\n"
        f"- 状态：{summary['status']}\n"
        f"- 模型：{', '.join(summary['model_ids'])}\n"
        f"- 每模型唯一图片：{summary['unique_images_per_model']}\n"
        f"- 模型—图片组：{summary['model_image_groups']}\n"
        f"- 最大代数恒等式误差：{summary['maximum_max_mean_dispersion_identity_error']:.3g}\n"
        f"- 总运行秒数：{summary['elapsed_seconds']:.6f}\n"
        f"- 峰值显存字节：{summary['max_memory_allocated_bytes']}\n"
        f"- CPU bundle 复核：{summary['bundle_verification_status']}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--bundle-verification", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if any(path.exists() for path in (args.output_json, args.output_md)):
        raise FileExistsError("pilot summary output already exists")
    verification = load_json_snapshot(args.bundle_verification)
    summary = summarize_pilot_v5(args.run_dir, verification)
    atomic_write_json(args.output_json, summary, overwrite=False)
    atomic_write_bytes(args.output_md, render_pilot_markdown(summary).encode("utf-8"), overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
