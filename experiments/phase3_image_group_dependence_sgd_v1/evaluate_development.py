#!/usr/bin/env python3
"""Evaluate one quantized P/S model on frozen Phase 3 development images."""

from __future__ import annotations

import argparse
import gc
import json
import math
from pathlib import Path

import torch

from experiments.phase3_risk_v1.aggregate_risks import summarize_model
from experiments.phase3_risk_v1.risk_metrics import derive_risk_rows
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    seed_everything,
    sha256_file,
)
from experiments.phase3_v6.scoring.hull_scorer import (
    group_pairs_by_filename,
    score_filename_group,
)
from experiments.phase3_v6.scoring.image_feature_cache import ProjectedFeatureCache
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_MISMATCH_IMAGE_COUNT,
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
)
from experiments.phase3_v6.scoring.run_scoring import (
    _cache_equivalence_for_model,
    prepare_candidates,
)
from experiments.stage2_protocol import Stage2Protocol

from .codec import decode_coordinates
from .common import sha256_file as local_sha256
from .configs import load_candidate
from experiments.phase3_private_vs_shared_v1.adapter_runtime import build_candidate_model

STAGE2_PROTOCOL = Path(__file__).resolve().parents[1] / "stage2_protocol_v2.json"


def evaluate(
    config_id: str, mms_path: Path, checkpoint_path: Path,
    output_dir: Path, device: str
) -> dict:
    config = load_candidate(config_id)
    stage2 = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
    decoded, codec = decode_coordinates(mms_path.read_bytes())
    if codec["structure"] != config["structure"] or codec["mapping_root"] != config["seed"]:
        raise ValueError("MMS2 identity differs from candidate")
    model = build_candidate_model(config, stage2, device=device)
    with torch.no_grad():
        for name, value in decoded.items():
            model.stage2_coordinates.coordinates[name].copy_(value.to(device))
    model.eval()
    seed_everything()
    frozen, tokenizer, pairs = prepare_candidates(write=False)
    if (
        len(pairs) != EXPECTED_VALID_RECORD_COUNT
        or frozen["valid_image_count"] != EXPECTED_VALID_IMAGE_COUNT
        or frozen["mismatch_image_count"] != EXPECTED_MISMATCH_IMAGE_COUNT
    ):
        raise ValueError("development input identity changed")
    output_dir.mkdir(parents=True, exist_ok=True)
    cache = ProjectedFeatureCache(
        model, model_id=config_id, checkpoint_sha256=local_sha256(mms_path),
        image_entries=frozen["image_entries"], device=device,
    )
    cache.precompute(frozen["image_entries"].keys(), batch_size=1)
    equivalence = _cache_equivalence_for_model(
        model, cache, pairs[0], tokenizer, device
    )
    rows = []
    for filename, group in group_pairs_by_filename(pairs).items():
        rows.extend(score_filename_group(
            model, group, mismatch_row=frozen["mismatch_by_target"][filename],
            model_method=config["structure"], tokenizer=tokenizer, device=device,
            feature_cache=cache,
        ))
    for row in rows:
        row.update({"model_id": config_id, "method": config["structure"]})
    if len(rows) != EXPECTED_VALID_RECORD_COUNT:
        raise RuntimeError("development scorer returned wrong record count")
    scores_path = output_dir / "record_scores.jsonl"
    atomic_write_jsonl(scores_path, rows)
    risk_rows = derive_risk_rows(rows)
    risks_path = output_dir / "record_risks.jsonl"
    atomic_write_jsonl(risks_path, risk_rows)
    image_rows, summary = summarize_model(
        risk_rows, expected_image_count=EXPECTED_VALID_IMAGE_COUNT
    )
    image_path = output_dir / "image_group_risks.jsonl"
    atomic_write_jsonl(image_path, image_rows)
    summary_path = output_dir / "risk_summary.json"
    atomic_write_json(summary_path, summary)
    risks = summary["empirical_risks"]
    result = {
        "schema_version": 1,
        "status": "complete",
        "config_id": config_id,
        "structure": config["structure"],
        "budget": config["budget"],
        "seed": config["seed"],
        "evaluation_role": "development_only",
        "development_image_count": EXPECTED_VALID_IMAGE_COUNT,
        "development_input_sha256": frozen["input_sha256"],
        "new_image_development_real_visual_performance": float(risks["visual_gain"]),
        "error_oriented_metric": float(risks["visual_risk"]),
        "error_oriented_metric_name": "visual_risk",
        "development_task_risk": float(risks["total_semantic_risk"]),
        "mms2_sha256": local_sha256(mms_path),
        "checkpoint_sha256": local_sha256(checkpoint_path),
        "record_scores_sha256": sha256_file(scores_path),
        "record_risks_sha256": sha256_file(risks_path),
        "image_group_risks_sha256": sha256_file(image_path),
        "risk_summary_sha256": sha256_file(summary_path),
        "cache_no_cache_equivalence": equivalence,
    }
    if not all(math.isfinite(float(result[key])) for key in (
        "new_image_development_real_visual_performance",
        "error_oriented_metric", "development_task_risk"
    )):
        raise FloatingPointError("development result is non-finite")
    atomic_write_json(output_dir / "development_result.json", result)
    del model, cache
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--mms2", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    print(json.dumps(evaluate(
        args.config_id, args.mms2, args.checkpoint, args.output_dir, args.device
    ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
