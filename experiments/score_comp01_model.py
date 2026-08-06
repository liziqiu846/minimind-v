#!/usr/bin/env python3
"""Score one frozen M2/M3 checkpoint on the complete COMP-01 panel."""

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

from experiments.comp01_scoring import (
    build_image_entries,
    score_pair_batch,
    score_rows_sha256,
)
from experiments.phase3.stage2_adapter_loader import (
    expected_model,
    load_verified_model,
)
from experiments.phase3_risk_v1.budget_codec import decode_budget_mms2
from experiments.phase3_risk_v1.budget_runtime import (
    STAGE2_PROTOCOL_PATH,
    build_budget_model,
    load_frozen_config,
    verify_budget_runtime,
)
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
from model.global_subspace_lora import load_coordinate_state


SCORING_SEED = 3407


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--panel-audit", type=Path, required=True)
    parser.add_argument("--collision-diagnostic", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--pair-batch-size", type=int, default=8)
    parser.add_argument(
        "--mode", choices=("smoke", "full"), default="full"
    )
    return parser.parse_args()


def verify_gate(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    audit = json.loads(args.panel_audit.read_text(encoding="utf-8"))
    diagnostic = json.loads(
        args.collision_diagnostic.read_text(encoding="utf-8")
    )
    if (
        audit.get("model_inference_performed") is not False
        or audit.get("scientific_results_accessed") is not False
        or audit["overlap_audit"]["exact_history_match_count"] != 0
        or audit["overlap_audit"]["exact_training_match_count"] != 0
    ):
        raise ValueError("panel audit does not permit model inference")
    if (
        diagnostic.get("status") != "passed_false_positive_phash_screen"
        or diagnostic.get("final_confirmation_accessed") is not False
        or diagnostic.get("all_neighbors_are_distinct_scenes") is not True
        or diagnostic["gate_adjudication"]["status"] != "eligible_for_scoring"
    ):
        raise ValueError("pHash collision adjudication does not permit scoring")
    return audit, diagnostic


def load_model(
    config: dict[str, Any],
    config_receipt: dict[str, Any],
    *,
    artifact_root: Path,
    device: str,
) -> tuple[Any, dict[str, Any], Any, Any]:
    protocol, runtime = verify_budget_runtime(
        config,
        artifact_root=artifact_root,
        require_gpu=True,
        environment_mode="v6",
    )
    if config["budget"] == "current":
        stage2_id = f"{config['method']}-root-{config['mapping_root']}"
        expected = expected_model(stage2_id)
        model, metadata, loaded_protocol = load_verified_model(
            stage2_id,
            artifact_root=artifact_root,
            stage2_protocol_path=STAGE2_PROTOCOL_PATH,
            device=device,
            dtype=torch.float32,
        )
        if loaded_protocol.reference() != protocol.reference():
            raise ValueError("current model protocol differs from runtime protocol")
        checkpoint = {
            "loader": "verified_stage2_current_mms2",
            "stage2_model_id": stage2_id,
            "archive_path": str(
                (
                    artifact_root.resolve()
                    / expected["artifact_relative_path"]
                )
            ),
            "archive_sha256": expected["artifact_sha256"],
            "archive_bytes": expected["artifact_size_bytes"],
            "decoded_metadata": metadata,
        }
    else:
        model_root = artifact_root.resolve() / config["output_relative_path"]
        summary_path = model_root / "encode/adapter_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if (
            summary.get("status") != "complete"
            or summary.get("config_id") != config["config_id"]
            or summary.get("config", {}).get("sha256")
            != config_receipt["sha256"]
        ):
            raise ValueError("budget adapter summary differs from frozen config")
        archive_path = Path(summary["archive_path"]).resolve()
        if (
            not archive_path.is_relative_to(artifact_root.resolve())
            or sha256_file(archive_path) != summary["archive_sha256"]
        ):
            raise ValueError("budget MMS2 path/hash differs from adapter summary")
        payload = archive_path.read_bytes()
        coordinates, metadata = decode_budget_mms2(
            payload, config["coordinate_dimensions"]
        )
        if (
            metadata["model_group"] != config["method"]
            or metadata["mapping_root"] != config["mapping_root"]
        ):
            raise ValueError("decoded budget MMS2 identity mismatch")
        model = build_budget_model(
            config, protocol, device=device, dtype=torch.float32
        )
        load_coordinate_state(model, coordinates)
        checkpoint = {
            "loader": "verified_budget_mms2",
            "archive_path": str(archive_path),
            "archive_sha256": summary["archive_sha256"],
            "archive_bytes": len(payload),
            "adapter_summary_path": str(summary_path),
            "adapter_summary_sha256": sha256_file(summary_path),
            "decoded_metadata": metadata,
        }
    model.eval()
    return model, checkpoint, runtime, protocol


def score(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"scoring output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if args.device != "cuda:0" or torch.cuda.device_count() != 1:
        raise ValueError("COMP-01 requires cuda:0 with exactly one visible GPU")
    if args.pair_batch_size < 1:
        raise ValueError("pair batch size must be positive")
    verify_gate(args)
    manifest = json.loads(args.panel_manifest.read_text(encoding="utf-8"))
    if (
        manifest.get("manifest_id") != "COMP-01-WhatUp-controlled-panel-v1"
        or len(manifest.get("images", [])) != 820
        or len(manifest.get("pairs", [])) != 410
    ):
        raise ValueError("panel manifest cardinality or identity mismatch")

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
    pairs = list(manifest["pairs"])
    if args.mode == "smoke":
        pairs = pairs[:1]
    image_entries = build_image_entries(pairs, manifest["images"])
    if args.mode == "full" and len(image_entries) != 820:
        raise RuntimeError("full scoring does not cover all 820 panel images")
    cache = ProjectedFeatureCache(
        model,
        model_id=config["config_id"],
        checkpoint_sha256=checkpoint["archive_sha256"],
        image_entries=image_entries,
        device=args.device,
    )
    cache.precompute(image_entries, batch_size=32)
    cache.install()

    if args.mode == "smoke":
        first = score_pair_batch(
            model,
            pairs,
            tokenizer=tokenizer,
            device=args.device,
            feature_cache=cache,
        )
        second = score_pair_batch(
            model,
            pairs,
            tokenizer=tokenizer,
            device=args.device,
            feature_cache=cache,
        )
        if first != second:
            raise RuntimeError("cached deterministic smoke rerun differs")
        if (
            len(first) != 1
            or not all(
                math.isfinite(first[0][key])
                for key in (
                    "nll_00_bits_per_token",
                    "nll_01_bits_per_token",
                    "nll_10_bits_per_token",
                    "nll_11_bits_per_token",
                )
            )
        ):
            raise RuntimeError("smoke did not produce one complete finite grid")
        raw_rows = first
    else:
        raw_rows = []
        for start in range(0, len(pairs), args.pair_batch_size):
            end = min(start + args.pair_batch_size, len(pairs))
            raw_rows.extend(
                score_pair_batch(
                    model,
                    pairs[start:end],
                    tokenizer=tokenizer,
                    device=args.device,
                    feature_cache=cache,
                )
            )
            if end == len(pairs) or end % 64 == 0:
                print(
                    f"config={config['config_id']} scored_pairs={end}/{len(pairs)}",
                    flush=True,
                )
        if (
            len(raw_rows) != 410
            or len({row["pair_id"] for row in raw_rows}) != 410
        ):
            raise RuntimeError("full scoring output is incomplete or duplicated")

    raw_sha = score_rows_sha256(raw_rows)
    result_path = output / "pair_scores.jsonl"
    if args.mode == "full":
        atomic_write_jsonl(result_path, raw_rows)
        if sha256_file(result_path) != raw_sha:
            raise RuntimeError("written raw-score SHA differs from in-memory rows")
    elapsed = time.time() - started
    receipt = {
        "schema_version": 1,
        "receipt_id": f"COMP-01-round1-{config['config_id']}-{args.mode}",
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
            "collision_diagnostic": {
                "path": str(args.collision_diagnostic.resolve()),
                "sha256": sha256_file(args.collision_diagnostic),
            },
            "final_confirmation_accessed": False,
        },
        "scoring": {
            "teacher_forced_target": "caption_plus_EOS",
            "unit": "mean NLL bits per target token",
            "prompt": "Describe the image in one sentence.",
            "pair_count": len(raw_rows),
            "grid_cells_per_pair": 4,
            "pair_batch_size": args.pair_batch_size,
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
        f"pairs={len(raw_rows)} raw_sha256={raw_sha} "
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
