#!/usr/bin/env python3
"""Score one frozen M2/M3 checkpoint on the VISCOND-01 MMStar panel."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path
from typing import Any

import torch
from transformers import AutoTokenizer

from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    environment_receipt,
    git_output,
    seed_everything,
    sha256_file,
)
from experiments.phase3_v6.scoring.image_feature_cache import (
    ProjectedFeatureCache,
)
from experiments.score_comp01_model import load_model
from experiments.viscond01 import (
    EXPECTED_ROWS,
    image_entries,
    score_item_batch,
    score_rows_sha256,
)


SCORING_SEED = 3407


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--panel-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--item-batch-size", type=int, default=8)
    parser.add_argument("--mode", choices=("smoke", "full"), default="full")
    return parser.parse_args()


def verify_gate(
    panel_manifest: Path,
    panel_audit: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    audit = json.loads(panel_audit.read_text(encoding="utf-8"))
    manifest = json.loads(panel_manifest.read_text(encoding="utf-8"))
    if (
        audit.get("status") != "passed"
        or audit.get("eligible_for_scoring") is not True
        or audit.get("model_inference_performed") is not False
        or audit.get("scientific_model_results_accessed") is not False
        or audit.get("final_confirmation_accessed") is not False
        or manifest.get("manifest_id")
        != "VISCOND-01-MMStar-bc98d668-v1"
        or audit["outputs"]["panel_manifest"]["sha256"]
        != sha256_file(panel_manifest)
    ):
        raise ValueError("MMStar audit does not permit VISCOND-01 scoring")
    rows = manifest.get("rows", [])
    if (
        len(rows) < 1_350
        or len(rows) > EXPECTED_ROWS
        or len({int(row["index"]) for row in rows}) != len(rows)
        or len(
            {row["normalized_pixel_sha256"] for row in rows}
        )
        < 1_350
    ):
        raise ValueError("MMStar eligible panel cardinality is invalid")
    return manifest, audit


def score(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"scoring output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if args.device != "cuda:0" or torch.cuda.device_count() != 1:
        raise ValueError(
            "VISCOND-01 requires cuda:0 with exactly one visible GPU"
        )
    if args.item_batch_size < 1:
        raise ValueError("item batch size must be positive")
    manifest, audit = verify_gate(
        args.panel_manifest.resolve(),
        args.panel_audit.resolve(),
    )

    from experiments.phase3_risk_v1.budget_runtime import load_frozen_config

    config, config_receipt = load_frozen_config(args.config_id)
    seed_everything(SCORING_SEED)
    model, checkpoint, runtime, protocol = load_model(
        config,
        config_receipt,
        artifact_root=args.artifact_root,
        device=args.device,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"),
        local_files_only=True,
    )
    if tokenizer.pad_token_id is None or tokenizer.eos_token_id is None:
        raise ValueError("frozen tokenizer lacks PAD or EOS")
    items = list(manifest["rows"])
    if args.mode == "smoke":
        items = items[:2]
    entries = image_entries(items)
    cache = ProjectedFeatureCache(
        model,
        model_id=config["config_id"],
        checkpoint_sha256=checkpoint["archive_sha256"],
        image_entries=entries,
        device=args.device,
    )
    cache.precompute(entries, batch_size=32)
    cache.install()

    if args.mode == "smoke":
        first = score_item_batch(
            model,
            items,
            tokenizer=tokenizer,
            device=args.device,
            feature_cache=cache,
        )
        second = score_item_batch(
            model,
            items,
            tokenizer=tokenizer,
            device=args.device,
            feature_cache=cache,
        )
        if first != second:
            raise RuntimeError("VISCOND deterministic smoke rerun differs")
        if (
            len(first) != 2
            or any(row.get("all_scores_finite") is not True for row in first)
            or not all(
                math.isfinite(row["visual_increment_bits_per_token"])
                for row in first
            )
        ):
            raise RuntimeError("VISCOND smoke lacks two complete finite rows")
        raw_rows = first
    else:
        raw_rows = []
        for start in range(0, len(items), args.item_batch_size):
            end = min(start + args.item_batch_size, len(items))
            raw_rows.extend(
                score_item_batch(
                    model,
                    items[start:end],
                    tokenizer=tokenizer,
                    device=args.device,
                    feature_cache=cache,
                )
            )
            if end == len(items) or end % 128 == 0:
                print(
                    f"config={config['config_id']} "
                    f"scored_items={end}/{len(items)}",
                    flush=True,
                )
        if (
            len(raw_rows) != len(manifest["rows"])
            or [row["index"] for row in raw_rows]
            != [row["index"] for row in manifest["rows"]]
        ):
            raise RuntimeError("VISCOND full output is incomplete or reordered")

    raw_sha = score_rows_sha256(raw_rows)
    raw_path = output / "item_scores.jsonl"
    if args.mode == "full":
        atomic_write_jsonl(raw_path, raw_rows)
        if sha256_file(raw_path) != raw_sha:
            raise RuntimeError("written VISCOND raw SHA differs from memory")
    elapsed = time.time() - started
    receipt = {
        "schema_version": 1,
        "receipt_id": (
            f"VISCOND-01-round1-{config['config_id']}-{args.mode}"
        ),
        "status": "complete",
        "mode": args.mode,
        "config_id": config["config_id"],
        "method": config["method"],
        "budget": config["budget"],
        "mapping_root": config["mapping_root"],
        "checkpoint": checkpoint,
        "config": config_receipt,
        "inputs": {
            "panel_manifest": {
                "path": str(args.panel_manifest.resolve()),
                "sha256": sha256_file(args.panel_manifest),
            },
            "panel_audit": {
                "path": str(args.panel_audit.resolve()),
                "sha256": sha256_file(args.panel_audit),
            },
            "eligible_rows": len(manifest["rows"]),
            "independent_image_groups": audit["panel"][
                "unique_normalized_pixel_groups"
            ],
            "final_confirmation_accessed": False,
        },
        "scoring": {
            "teacher_forced_target": "option_letter_plus_EOS",
            "unit": "mean NLL bits per target token",
            "prompt_suffix": "Answer with the option letter only.",
            "conditions": ["correct_image", "no_pixel_same_VLM_tokens"],
            "item_count": len(raw_rows),
            "labels_per_condition": 4,
            "item_batch_size": args.item_batch_size,
            "raw_rows_sha256": raw_sha,
            "raw_values_persisted": args.mode == "full",
            "deterministic_rerun_exact": args.mode == "smoke",
            "aggregate_scientific_result_computed": False,
        },
        "cache": cache.receipt(),
        "runtime_preflight": runtime,
        "environment": environment_receipt(args.device),
        "git": {
            "commit": git_output("rev-parse", "HEAD"),
            "tracked_status": git_output(
                "status", "--porcelain", "--untracked-files=no"
            ),
        },
        "peak_cuda_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "elapsed_seconds": elapsed,
    }
    atomic_write_json(output / "run_receipt.json", receipt)
    print(
        f"status=complete mode={args.mode} config={config['config_id']} "
        f"items={len(raw_rows)} raw_sha256={raw_sha} "
        f"elapsed_seconds={elapsed:.1f}",
        flush=True,
    )
    del cache, model
    gc.collect()
    torch.cuda.empty_cache()
    return receipt


def main() -> None:
    score(parse_args())


if __name__ == "__main__":
    main()
