#!/usr/bin/env python3
"""Evaluate one curve model on the frozen Phase 3 development-only inputs."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.exploratory_bounds import exploratory_upper
from experiments.phase3_risk_v1.risk_metrics import derive_risk_rows
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    environment_receipt,
    seed_everything,
    sha256_file,
)
from experiments.phase3_v6.scoring.hull_scorer import (
    group_pairs_by_filename,
    score_filename_group,
)
from experiments.phase3_v6.scoring.image_feature_cache import (
    ProjectedFeatureCache,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_MISMATCH_IMAGE_COUNT,
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
)
from experiments.phase3_v6.scoring.protocol import verify_protocol
from experiments.phase3_v6.scoring.run_scoring import (
    CANDIDATE_EVIDENCE_PATH,
    CANDIDATE_SUMMARY_PATH,
    _cache_equivalence_for_model,
    prepare_candidates,
)
from experiments.stage2_protocol import Stage2Protocol

from .codec import assert_round_trip
from .formal_plan import verify_formal_run_plan
from .formal_runtime import _training_config
from .parameterization import build_candidate_model

EVALUATION_ROLE = "development_only"
DEVELOPMENT_PROTOCOL_ID = "phase3-v6-module-curve-development-reuse-v1"
CANDIDATE_FAMILY_SIZE = 75
FAMILYWISE_DELTA = 0.05
STAGE2_PROTOCOL_PATH = (
    Path(__file__).resolve().parents[1] / "stage2_protocol_v2.json"
)


def _selected_run(plan: Mapping[str, Any], run_id: str) -> Mapping[str, Any]:
    matches = [run for run in plan["runs"] if run["run_id"] == run_id]
    if len(matches) != 1:
        raise ValueError("development evaluation run_id is absent or duplicated")
    return matches[0]


def _validate_environment(device: str, protocol: Mapping[str, Any]) -> dict[str, Any]:
    if device != "cuda:0" or torch.cuda.device_count() != 1:
        raise RuntimeError(
            "development evaluation requires one visible GPU at logical cuda:0"
        )
    live = environment_receipt(device)
    expected = protocol["environment_at_freeze"]
    for key in (
        "Pillow",
        "numpy",
        "scipy",
        "torch",
        "transformers",
        "cuda",
        "cudnn",
    ):
        if live.get(key) != expected.get(key):
            raise ValueError(
                f"Phase 3 v6 environment differs for {key}: "
                f"{live.get(key)} != {expected.get(key)}"
            )
    expected_flags = {
        "autocast_enabled": False,
        "cuda_matmul_allow_tf32": False,
        "cudnn_allow_tf32": False,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "model_dtype": "float32",
    }
    for key, value in expected_flags.items():
        if live.get(key) != value:
            raise ValueError(
                f"Phase 3 v6 execution flag differs for {key}: "
                f"{live.get(key)} != {value}"
            )
    expected_gpu = expected["gpu"]
    live_gpu = live["gpu"]
    if (
        live_gpu.get("name") != expected_gpu.get("name")
        or live_gpu.get("compute_capability")
        != expected_gpu.get("compute_capability")
    ):
        raise ValueError("development evaluation GPU differs from the frozen A40")
    return live


def _load_archives(codec_root: Path) -> dict[str, bytes]:
    archives = {
        module: (codec_root / f"{module}.mmb1").read_bytes()
        for module in ("vision", "projector", "language")
    }
    assert_round_trip(archives)
    return archives


def _load_quantized_model(
    run: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    codec_root: Path,
    device: str,
) -> tuple[Any, dict[str, torch.Tensor]]:
    stage2 = Stage2Protocol.load(STAGE2_PROTOCOL_PATH, require_frozen=True)
    config = _training_config(
        run, plan["anchor_config"]["coordinate_dimensions"]
    )
    model = build_candidate_model(config, stage2, device=device)
    decoded = assert_round_trip(_load_archives(codec_root))
    coordinates = model.stage2_coordinates.coordinates
    if {
        module: int(coordinates[module].numel()) for module in coordinates
    } != dict(run["coordinate_dimensions"]):
        raise ValueError("constructed development model dimensions differ")
    with torch.no_grad():
        for module, value in decoded.items():
            coordinates[module].copy_(value.to(device=device))
    model.eval()
    return model, decoded


def _write_shard(
    path: Path,
    rows: list[dict[str, Any]],
    *,
    run_id: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    for row in rows:
        row.update(
            {
                "model_id": run_id,
                "method": "M2",
                "evaluation_role": EVALUATION_ROLE,
                "protocol_sha256": protocol_sha256,
            }
        )
    atomic_write_jsonl(path, rows)
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "record_count": len(rows),
    }


def evaluate(
    *,
    plan_path: Path,
    run_id: str,
    codec_root: Path,
    checkpoint_path: Path,
    output_dir: Path,
    device: str,
) -> dict[str, Any]:
    """Run the unchanged v6 scorer and established risk aggregation once."""
    started = time.time()
    plan = verify_formal_run_plan(plan_path)
    run = _selected_run(plan, run_id)
    protocol, protocol_sha256 = verify_protocol()
    seed_everything()
    environment = _validate_environment(device, protocol)
    frozen, tokenizer, pairs = prepare_candidates(write=False)
    if (
        sha256_file(CANDIDATE_EVIDENCE_PATH)
        != protocol["frozen_inputs"]["candidate_preflight_evidence_sha256"]
        or sha256_file(CANDIDATE_SUMMARY_PATH)
        != protocol["frozen_inputs"]["candidate_preflight_summary_sha256"]
    ):
        raise ValueError("frozen Phase 3 development candidate evidence changed")
    if (
        len(pairs) != EXPECTED_VALID_RECORD_COUNT
        or frozen["valid_image_count"] != EXPECTED_VALID_IMAGE_COUNT
        or frozen["mismatch_image_count"] != EXPECTED_MISMATCH_IMAGE_COUNT
    ):
        raise ValueError("Phase 3 development input counts changed")

    output = output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    model, decoded = _load_quantized_model(
        run, plan, codec_root=codec_root.resolve(), device=device
    )
    cache = ProjectedFeatureCache(
        model,
        model_id=run_id,
        checkpoint_sha256=sha256_file(checkpoint_path),
        image_entries=frozen["image_entries"],
        device=device,
    )
    cache.precompute(
        frozen["image_entries"].keys(),
        batch_size=int(
            protocol["execution"]["vision_cache"]["precompute_batch_size"]
        ),
    )
    if cache.encoded_image_count != EXPECTED_MISMATCH_IMAGE_COUNT:
        raise RuntimeError("development visual cache did not encode all images")
    cache_equivalence = _cache_equivalence_for_model(
        model, cache, pairs[0], tokenizer, device
    )

    groups = group_pairs_by_filename(pairs)
    filenames = list(groups)
    shard_size = int(protocol["execution"]["shard_size_target_images"])
    all_rows: list[dict[str, Any]] = []
    shard_receipts = []
    for start in range(0, len(filenames), shard_size):
        end = min(start + shard_size, len(filenames))
        shard_rows: list[dict[str, Any]] = []
        for filename in filenames[start:end]:
            shard_rows.extend(
                score_filename_group(
                    model,
                    groups[filename],
                    mismatch_row=frozen["mismatch_by_target"][filename],
                    model_method="M2",
                    tokenizer=tokenizer,
                    device=device,
                    feature_cache=cache,
                )
            )
        shard_path = output / "shards" / f"{start:04d}_{end:04d}.jsonl"
        receipt = _write_shard(
            shard_path,
            shard_rows,
            run_id=run_id,
            protocol_sha256=protocol_sha256,
        )
        receipt.update({"start_image": start, "end_image": end})
        shard_receipts.append(receipt)
        all_rows.extend(shard_rows)
        print(
            f"run={run_id} development_images={end}/{len(filenames)} "
            f"records={len(all_rows)}",
            flush=True,
        )

    if (
        len(all_rows) != EXPECTED_VALID_RECORD_COUNT
        or len({row["sample_id"] for row in all_rows}) != len(all_rows)
    ):
        raise RuntimeError("development scoring record identity differs")
    record_scores_path = output / "record_scores.jsonl"
    atomic_write_jsonl(record_scores_path, all_rows)
    risk_rows = derive_risk_rows(all_rows)
    record_risks_path = output / "record_risks.jsonl"
    atomic_write_jsonl(record_risks_path, risk_rows)
    image_rows, risk_summary = summarize_model(
        risk_rows, expected_image_count=EXPECTED_VALID_IMAGE_COUNT
    )
    image_risks_path = output / "image_group_risks.jsonl"
    atomic_write_jsonl(image_risks_path, image_rows)
    risk_summary_path = output / "risk_summary.json"
    atomic_write_json(risk_summary_path, risk_summary)

    risks = risk_summary["empirical_risks"]
    development_task_risk = float(risks["total_semantic_risk"])
    semantic = exploratory_upper(
        development_task_risk,
        EXPECTED_VALID_IMAGE_COUNT,
        FAMILYWISE_DELTA / CANDIDATE_FAMILY_SIZE,
    )
    visual = exploratory_upper(
        float(risks["visual_risk"]),
        EXPECTED_VALID_IMAGE_COUNT,
        FAMILYWISE_DELTA / (2.0 * CANDIDATE_FAMILY_SIZE),
    )
    visual_gain_guardrail = 1.0 - 2.0 * float(
        visual["exploratory_upper_bound_capped"]
    )
    result = {
        "schema_version": 1,
        "status": "complete",
        "run_id": run_id,
        "config_id": run["config_id"],
        "seed": int(run["seed"]),
        "evaluation_role": EVALUATION_ROLE,
        "curve_run_plan_sha256": sha256_file(plan_path),
        "development_protocol_id": DEVELOPMENT_PROTOCOL_ID,
        "development_protocol_sha256": protocol_sha256,
        "development_assignment_core_sha256": frozen[
            "assignment_core_sha256"
        ],
        "development_input_sha256": frozen["input_sha256"],
        "development_record_count": EXPECTED_VALID_RECORD_COUNT,
        "development_image_count": EXPECTED_VALID_IMAGE_COUNT,
        "development_mismatch_image_count": EXPECTED_MISMATCH_IMAGE_COUNT,
        "development_task_risk": development_task_risk,
        "development_task_risk_definition": "image_equal_mean(1-q_correct)",
        "semantic_risk_bound": float(
            semantic["exploratory_upper_bound_capped"]
        ),
        "semantic_risk_bound_role": "development_exploratory_guardrail",
        "semantic_risk_bound_details": semantic,
        "visual_gain_guardrail": visual_gain_guardrail,
        "visual_gain_empirical": float(risks["visual_gain"]),
        "visual_gain_guardrail_role": "development_exploratory_guardrail_only",
        "visual_gain_guardrail_details": visual,
        "candidate_family_size": CANDIDATE_FAMILY_SIZE,
        "familywise_delta": FAMILYWISE_DELTA,
        "record_scores_path": str(record_scores_path),
        "record_scores_sha256": sha256_file(record_scores_path),
        "record_risks_path": str(record_risks_path),
        "record_risks_sha256": sha256_file(record_risks_path),
        "image_group_risks_path": str(image_risks_path),
        "image_group_risks_sha256": sha256_file(image_risks_path),
        "risk_summary_path": str(risk_summary_path),
        "risk_summary_sha256": sha256_file(risk_summary_path),
        "checkpoint_path": str(checkpoint_path.resolve()),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "codec_root": str(codec_root.resolve()),
        "decoded_coordinate_dimensions": {
            module: int(value.numel()) for module, value in decoded.items()
        },
        "cache_receipt": cache.receipt(),
        "cache_no_cache_equivalence": cache_equivalence,
        "shards": shard_receipts,
        "environment": environment,
        "runtime_seconds": time.time() - started,
    }
    numeric = (
        development_task_risk,
        result["semantic_risk_bound"],
        visual_gain_guardrail,
    )
    if not all(math.isfinite(value) for value in numeric):
        raise FloatingPointError("development evaluation produced non-finite results")
    result_path = output / "development_result.json"
    atomic_write_json(result_path, result)
    del model, cache
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--codec-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    result = evaluate(
        plan_path=args.plan,
        run_id=args.run_id,
        codec_root=args.codec_root,
        checkpoint_path=args.checkpoint,
        output_dir=args.output_dir,
        device=args.device,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
