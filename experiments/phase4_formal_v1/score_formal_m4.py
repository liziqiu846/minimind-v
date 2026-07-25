#!/usr/bin/env python3
"""Score the sole formal M4 model with the unchanged frozen Phase 3 v6 rules."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3_v6.scoring.aggregations import (
    summarize_model as summarize_v6,
)
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    environment_receipt,
    read_json,
    seed_everything,
    sha256_file,
)
from experiments.phase3_v6.scoring.hull_scorer import (
    group_pairs_by_filename,
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
from experiments.phase4_formal_v1 import (
    FORMAL_CANDIDATE_ID,
    FORMAL_CONFIG_ID,
)
from experiments.phase4_formal_v1.runtime_gate import (
    assert_runtime_binding,
    verify_formal_config,
)
from experiments.phase4_m4_v1.m4_model import load_m4_model_from_archive
from experiments.phase4_m4_v1.score_m4 import (
    adapt_frozen_score_rows,
    score_filename_group_m4,
    summarize_adapted_rows,
)


INVALID_CERTIFICATION_REASONS = [
    "reuses_frozen_phase3_evaluation_data",
    "exploratory_only",
    "u_statistic_not_implemented",
    "no_formal_visual_generalization_certificate",
]


def _preferred_metrics(summary: Mapping[str, Any]) -> dict[str, float]:
    distributions = summary["image_equal_primary_distributions"]
    q_correct = float(distributions["q_correct"]["mean"])
    q_mismatch = float(distributions["q_mismatch_mean"]["mean"])
    result = {
        "q_correct": q_correct,
        "q_mismatch_mean": q_mismatch,
        "mismatch_baseline_risk": 1.0 - q_mismatch,
        "visual_gain": q_correct - q_mismatch,
        "joint_semantic_risk": 1.0 - q_correct,
    }
    if (
        abs(
            result["mismatch_baseline_risk"]
            - float(summary["mismatch_baseline_risk"])
        )
        > 1e-15
        or abs(result["visual_gain"] - float(summary["visual_gain"])) > 1e-15
        or abs(
            result["joint_semantic_risk"]
            - float(summary["joint_semantic_risk"])
        )
        > 1e-15
    ):
        raise RuntimeError("preferred M4 risk fields differ from frozen summary")
    return result


def _validate_scoring_environment(device: str) -> dict[str, Any]:
    frozen_protocol, frozen_sha = verify_protocol()
    if device != "cuda:0" or torch.cuda.device_count() != 1:
        raise RuntimeError("M4 scoring requires one visible GPU at cuda:0")
    seed_everything()
    live = environment_receipt(device)
    expected = frozen_protocol["environment_at_freeze"]
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
            raise RuntimeError(
                f"Phase 3 v6 scoring environment differs for {key}"
            )
    expected_flags = {
        "autocast_enabled": False,
        "cuda_matmul_allow_tf32": False,
        "cudnn_allow_tf32": False,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "model_dtype": "float32",
    }
    if any(live.get(key) != value for key, value in expected_flags.items()):
        raise RuntimeError("Phase 3 v6 deterministic execution flags differ")
    if (
        live.get("gpu", {}).get("name")
        != expected.get("gpu", {}).get("name")
        or live.get("gpu", {}).get("compute_capability")
        != expected.get("gpu", {}).get("compute_capability")
    ):
        raise RuntimeError("Phase 3 v6 scoring GPU type differs from frozen A40")
    return {
        "status": "passed",
        "frozen_phase3_v6_protocol_sha256": frozen_sha,
        "frozen_logical_device": frozen_protocol["execution"]["device"],
        "runtime_logical_device": device,
        "logical_device_remap_only": True,
        "environment": live,
    }


def score(
    *,
    artifact_root: Path,
    archive_path: Path,
    complexity_receipt_path: Path,
    binding_receipt_path: Path,
    output_dir: Path,
    device: str = "cuda:0",
) -> dict[str, Any]:
    output = output_dir.resolve()
    if output.exists():
        raise FileExistsError(f"M4 scoring output already exists: {output}")
    output.mkdir(parents=True)
    started = time.time()
    try:
        config, config_receipt = verify_formal_config()
        binding_document = read_json(binding_receipt_path)
        binding = assert_runtime_binding(
            binding_document["binding"], require_zlib_1_3_1=False
        )
        scoring_runtime = _validate_scoring_environment(device)
        frozen_protocol, frozen_protocol_sha = verify_protocol()
        frozen, tokenizer, pairs = prepare_candidates(write=False)
        if (
            sha256_file(CANDIDATE_EVIDENCE_PATH)
            != frozen_protocol["frozen_inputs"][
                "candidate_preflight_evidence_sha256"
            ]
            or sha256_file(CANDIDATE_SUMMARY_PATH)
            != frozen_protocol["frozen_inputs"][
                "candidate_preflight_summary_sha256"
            ]
        ):
            raise RuntimeError("Phase 3 v6 candidate evidence changed")
        if (
            str(artifact_root.resolve())
            != frozen_protocol["models"]["artifact_root"]
        ):
            raise RuntimeError("artifact root differs from frozen Phase 3 v6")

        complexity = read_json(complexity_receipt_path)
        if (
            complexity.get("status") != "passed"
            or complexity.get("candidate_id") != FORMAL_CANDIDATE_ID
            or complexity.get("paid_fields_sum_exact") is not True
            or complexity.get("conditional_message_bits")
            != complexity.get("paid_field_bits_sum")
        ):
            raise RuntimeError("formal complexity receipt is invalid")
        if (
            not archive_path.is_file()
            or sha256_file(archive_path)
            != complexity["full_archive_sha256"]
        ):
            raise RuntimeError("formal MMS2 v2 archive hash differs")

        archive = archive_path.read_bytes()
        model, archive_metadata = load_m4_model_from_archive(
            archive,
            device=device,
            dtype=torch.float32,
            verify_assets=True,
        )
        if archive_metadata["config_id"] != FORMAL_CONFIG_ID:
            raise RuntimeError("formal M4 archive has the wrong config ID")
        model.eval()
        cache = ProjectedFeatureCache(
            model,
            model_id=FORMAL_CONFIG_ID,
            checkpoint_sha256=complexity["full_archive_sha256"],
            image_entries=frozen["image_entries"],
            device=device,
        )
        cache.precompute(
            frozen["image_entries"].keys(),
            batch_size=int(
                frozen_protocol["execution"]["vision_cache"][
                    "precompute_batch_size"
                ]
            ),
        )
        if cache.encoded_image_count != EXPECTED_MISMATCH_IMAGE_COUNT:
            raise RuntimeError("M4 visual cache image count differs from v6")
        cache_equivalence = _cache_equivalence_for_model(
            model, cache, pairs[0], tokenizer, device
        )

        groups = group_pairs_by_filename(pairs)
        filenames = list(groups)
        shard_size = int(
            frozen_protocol["execution"]["shard_size_target_images"]
        )
        all_rows: list[dict[str, Any]] = []
        shard_receipts = []
        for start in range(0, len(filenames), shard_size):
            end = min(start + shard_size, len(filenames))
            shard_rows: list[dict[str, Any]] = []
            for filename in filenames[start:end]:
                rows = score_filename_group_m4(
                    model,
                    groups[filename],
                    mismatch_row=frozen["mismatch_by_target"][filename],
                    tokenizer=tokenizer,
                    device=device,
                    feature_cache=cache,
                )
                for row in rows:
                    row.update(
                        {
                            "model_id": FORMAL_CONFIG_ID,
                            "method": "M4",
                            "protocol_sha256": frozen_protocol_sha,
                        }
                    )
                shard_rows.extend(rows)
            shard_path = output / "shards" / f"{start:04d}_{end:04d}.jsonl"
            atomic_write_jsonl(shard_path, shard_rows)
            shard_receipts.append(
                {
                    "start_image": start,
                    "end_image": end,
                    "record_count": len(shard_rows),
                    "path": str(shard_path),
                    "sha256": sha256_file(shard_path),
                }
            )
            all_rows.extend(shard_rows)
            print(
                f"config={FORMAL_CONFIG_ID} scored_images={end}/"
                f"{len(filenames)} records={len(all_rows)}",
                flush=True,
            )
        if (
            len(all_rows) != EXPECTED_VALID_RECORD_COUNT
            or len({row["sample_id"] for row in all_rows}) != len(all_rows)
            or any(row.get("all_scores_finite") is not True for row in all_rows)
        ):
            raise RuntimeError("M4 scoring output failed record validation")

        record_path = output / "record_scores_v6.jsonl"
        atomic_write_jsonl(record_path, all_rows)
        v6_image_rows, v6_summary = summarize_v6(
            FORMAL_CONFIG_ID, "M4", all_rows
        )
        v6_image_path = output / "image_scores_v6.jsonl"
        atomic_write_jsonl(v6_image_path, v6_image_rows)
        atomic_write_json(output / "v6_summary.json", v6_summary)

        risk_rows = adapt_frozen_score_rows(all_rows)
        risk_path = output / "record_risks.jsonl"
        atomic_write_jsonl(risk_path, risk_rows)
        image_risks, risk_summary = summarize_adapted_rows(
            risk_rows, expected_image_count=EXPECTED_VALID_IMAGE_COUNT
        )
        image_risk_path = output / "image_group_risks.jsonl"
        atomic_write_jsonl(image_risk_path, image_risks)
        preferred = _preferred_metrics(risk_summary)
        risk_summary.update(
            {
                "preferred_metrics": preferred,
                "certified": False,
                "exploratory": True,
                "invalid_for_formal_certification_reasons": (
                    INVALID_CERTIFICATION_REASONS
                ),
            }
        )
        atomic_write_json(output / "risk_summary.json", risk_summary)
        cache_receipt = cache.receipt()
        cache_receipt["cache_no_cache_equivalence"] = cache_equivalence
        atomic_write_json(output / "cache_receipt.json", cache_receipt)

        receipt = {
            "schema_version": 1,
            "status": "complete",
            "config_id": FORMAL_CONFIG_ID,
            "candidate_id": FORMAL_CANDIDATE_ID,
            "config": config_receipt,
            "binding": binding,
            "scoring_runtime": scoring_runtime,
            "frozen_phase3_v6_protocol_sha256": frozen_protocol_sha,
            "record_count": len(risk_rows),
            "image_count": len(image_risks),
            "teacher_forcing_modified": False,
            "mismatch_k": 5,
            "image_group_equal_aggregation_modified": False,
            "scorer_modified": False,
            "u_statistic_implemented": False,
            "certified": False,
            "exploratory": True,
            "invalid_for_formal_certification_reasons": (
                INVALID_CERTIFICATION_REASONS
            ),
            **preferred,
            "language_risk": preferred["mismatch_baseline_risk"],
            "language_risk_is_legacy_alias": True,
            "cache_no_cache_equivalence": cache_equivalence,
            "record_scores_path": str(record_path),
            "record_scores_sha256": sha256_file(record_path),
            "record_risks_path": str(risk_path),
            "record_risks_sha256": sha256_file(risk_path),
            "image_group_risks_path": str(image_risk_path),
            "image_group_risks_sha256": sha256_file(image_risk_path),
            "risk_summary_path": str(output / "risk_summary.json"),
            "risk_summary_sha256": sha256_file(
                output / "risk_summary.json"
            ),
            "cache_receipt_path": str(output / "cache_receipt.json"),
            "shards": shard_receipts,
            "seconds": time.time() - started,
            "automatic_retry": False,
        }
        if (
            not all(math.isfinite(value) for value in preferred.values())
            or not 0.0 <= preferred["q_correct"] <= 1.0
            or not 0.0 <= preferred["q_mismatch_mean"] <= 1.0
            or not -1.0 <= preferred["visual_gain"] <= 1.0
        ):
            raise RuntimeError("M4 preferred scoring fields are invalid")
        atomic_write_json(output / "scoring_receipt.json", receipt)
        del model, cache
        gc.collect()
        torch.cuda.empty_cache()
        return receipt
    except BaseException as error:
        atomic_write_json(
            output / "failure_receipt.json",
            {
                "schema_version": 1,
                "status": "failed",
                "config_id": FORMAL_CONFIG_ID,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--complexity-receipt", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = score(
        artifact_root=args.artifact_root,
        archive_path=args.archive,
        complexity_receipt_path=args.complexity_receipt,
        binding_receipt_path=args.binding_receipt,
        output_dir=args.output_dir,
        device=args.device,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
