#!/usr/bin/env python3
"""Score one budget MMS2 model with the unchanged frozen Phase 3 v6 scorer."""

from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import time
from pathlib import Path

import torch

from experiments.phase3_risk_v1.aggregate_risks import (
    summarize_model as summarize_risks,
)
from experiments.phase3_risk_v1.budget_codec import decode_budget_mms2
from experiments.phase3_risk_v1.budget_runtime import (
    build_budget_model,
    load_frozen_config,
    verify_budget_runtime,
)
from experiments.phase3_risk_v1.exploratory_bounds import (
    CURRENT_INVALID_REASONS,
    exploratory_upper,
)
from experiments.phase3_risk_v1.risk_metrics import derive_risk_rows
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
from model.global_subspace_lora import load_coordinate_state


def _write_category_csv(path: Path, summary: dict) -> None:
    rows = []
    for category in summary["category_summaries"]:
        row = {
            "model_id": summary["model_id"],
            "method": summary["method"],
            "category": category["category"],
            "record_count": category["record_count"],
            "image_count": category["image_count"],
        }
        for metric, distribution in category["metrics"].items():
            row[f"{metric}_mean"] = distribution["mean"]
            row[f"{metric}_standard_deviation_population"] = distribution[
                "standard_deviation_population"
            ]
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def _single_model_summary(
    config: dict,
    adapter: dict,
    risk_summary: dict,
) -> dict:
    risks = risk_summary["empirical_risks"]
    count = int(risk_summary["image_count"])
    delta_main = 0.05 / (2.0 * int(config["candidate_family_size"]))
    delta_total = 0.05 / int(config["candidate_family_size"])
    language = exploratory_upper(
        risks["language_risk"], count, delta_main
    )
    visual = exploratory_upper(risks["visual_risk"], count, delta_main)
    total = exploratory_upper(
        risks["total_semantic_risk"], count, delta_total
    )
    return {
        "schema_version": 1,
        "status": "complete",
        "model_id": config["config_id"],
        "config_id": config["config_id"],
        "budget": config["budget"],
        "method": config["method"],
        "model_group": config["method"],
        "mapping_root": config["mapping_root"],
        "experiment_seed": config["experiment_seed"],
        "total_coordinate_budget": config["total_coordinate_budget"],
        "coordinate_dimensions": config["coordinate_dimensions"],
        "archive_bits": adapter["archive_bits"],
        "external_selection_bits": config["external_selection_bits"],
        "external_hyperparameter_bits": config[
            "external_hyperparameter_bits"
        ],
        "total_description_bits": adapter["total_description_bits"],
        "empirical_risks": risks,
        "exploratory_hoeffding": {
            "analysis_type": "exploratory_concentration_analysis",
            "language_risk": language,
            "visual_risk": visual,
            "total_semantic_risk_separate_exploratory_family": total,
        },
        "exploratory_hoeffding_radius": visual["exploratory_radius"],
        "certified": False,
        "invalid_for_formal_certification_reasons": list(
            CURRENT_INVALID_REASONS
        ),
        "comparison_claim": (
            "equal_coordinate_budget_not_equal_description_length"
        ),
        "actual_description_length_is_an_observed_result": True,
        "risk_checks": {
            "range_checks": risk_summary["range_checks"],
            "identity_check": risk_summary["identity_check"],
            "m0_check": "not_applicable_to_M2_M3",
        },
    }


def score(args: argparse.Namespace) -> dict:
    config, config_receipt = load_frozen_config(args.config_id)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"scoring output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    try:
        stage2_protocol, runtime = verify_budget_runtime(
            config,
            artifact_root=args.artifact_root,
            require_gpu=True,
            environment_mode="v6",
        )
        if args.device != "cuda:0" or torch.cuda.device_count() != 1:
            raise RuntimeError(
                "frozen v6 scoring requires cuda:0 with one visible GPU"
            )
        frozen_protocol, frozen_protocol_sha = verify_protocol()
        frozen_device = frozen_protocol["execution"]["device"]
        frozen, tokenizer, pairs = prepare_candidates(write=False)
        if sha256_file(CANDIDATE_EVIDENCE_PATH) != frozen_protocol[
            "frozen_inputs"
        ]["candidate_preflight_evidence_sha256"]:
            raise ValueError("candidate evidence changed after v6 freeze")
        if sha256_file(CANDIDATE_SUMMARY_PATH) != frozen_protocol[
            "frozen_inputs"
        ]["candidate_preflight_summary_sha256"]:
            raise ValueError("candidate summary changed after v6 freeze")
        if (
            frozen["assignment_core_sha256"]
            != config["evaluation"]["assignment_core_sha256"]
            or frozen["input_sha256"]
            != config["evaluation"]["frozen_input_sha256"]
        ):
            raise ValueError("frozen v6 inputs differ from budget config")

        adapter = read_json(args.adapter_summary)
        if (
            adapter.get("status") != "complete"
            or adapter.get("config_id") != config["config_id"]
            or adapter.get("config", {}).get("sha256")
            != config_receipt["sha256"]
        ):
            raise ValueError("adapter summary differs from frozen config")
        archive_path = Path(adapter["archive_path"]).resolve()
        if sha256_file(archive_path) != adapter["archive_sha256"]:
            raise ValueError("MMS2 archive hash differs from adapter summary")
        coordinates, metadata = decode_budget_mms2(
            archive_path.read_bytes(), config["coordinate_dimensions"]
        )
        if (
            metadata["model_group"] != config["method"]
            or metadata["mapping_root"] != config["mapping_root"]
        ):
            raise ValueError("decoded MMS2 identity differs from config")

        seed_everything(int(config["evaluation"]["evaluation_seed"]))
        live_environment = environment_receipt(args.device)
        expected_environment = frozen_protocol["environment_at_freeze"]
        for key in (
            "Pillow",
            "numpy",
            "scipy",
            "torch",
            "transformers",
            "cuda",
            "cudnn",
        ):
            if live_environment.get(key) != expected_environment.get(key):
                raise ValueError(
                    f"v6 scoring environment differs for {key}: "
                    f"{live_environment.get(key)} != "
                    f"{expected_environment.get(key)}"
                )
        expected_execution_flags = {
            "autocast_enabled": False,
            "cuda_matmul_allow_tf32": False,
            "cudnn_allow_tf32": False,
            "cudnn_deterministic": True,
            "cudnn_benchmark": False,
            "model_dtype": "float32",
        }
        for key, expected in expected_execution_flags.items():
            if live_environment.get(key) != expected:
                raise ValueError(
                    f"v6 execution flag differs for {key}: "
                    f"{live_environment.get(key)} != {expected}"
                )
        if (
            live_environment.get("gpu", {}).get("name")
            != expected_environment.get("gpu", {}).get("name")
            or live_environment.get("gpu", {}).get("compute_capability")
            != expected_environment.get("gpu", {}).get(
                "compute_capability"
            )
        ):
            raise ValueError("v6 scoring GPU type differs from frozen A40")
        model = build_budget_model(
            config,
            stage2_protocol,
            device=args.device,
            dtype=torch.float32,
        )
        load_coordinate_state(model, coordinates)
        model.eval()
        cache = ProjectedFeatureCache(
            model,
            model_id=config["config_id"],
            checkpoint_sha256=adapter["archive_sha256"],
            image_entries=frozen["image_entries"],
            device=args.device,
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
            raise RuntimeError(
                "visual cache did not encode every frozen v6 image"
            )
        cache_equivalence = _cache_equivalence_for_model(
            model, cache, pairs[0], tokenizer, args.device
        )

        groups = group_pairs_by_filename(pairs)
        filenames = list(groups)
        shard_size = int(
            frozen_protocol["execution"]["shard_size_target_images"]
        )
        all_rows = []
        shard_receipts = []
        for start in range(0, len(filenames), shard_size):
            end = min(start + shard_size, len(filenames))
            shard_rows = []
            for filename in filenames[start:end]:
                rows = score_filename_group(
                    model,
                    groups[filename],
                    mismatch_row=frozen["mismatch_by_target"][filename],
                    model_method=config["method"],
                    tokenizer=tokenizer,
                    device=args.device,
                    feature_cache=cache,
                )
                for row in rows:
                    row.update(
                        {
                            "model_id": config["config_id"],
                            "method": config["method"],
                            "protocol_sha256": frozen_protocol_sha,
                        }
                    )
                shard_rows.extend(rows)
            shard_path = (
                output / "shards" / f"{start:04d}_{end:04d}.jsonl"
            )
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
                f"config={config['config_id']} scored_images={end}/"
                f"{len(filenames)} records={len(all_rows)}",
                flush=True,
            )
        if len(all_rows) != EXPECTED_VALID_RECORD_COUNT:
            raise RuntimeError("scoring record count differs from frozen v6")
        if len({row["sample_id"] for row in all_rows}) != len(all_rows):
            raise RuntimeError("scoring output contains duplicate sample IDs")
        required_q = {
            "q_correct",
            "q_mismatch_round_1",
            "q_mismatch_round_2",
            "q_mismatch_round_3",
            "q_mismatch_round_4",
            "q_mismatch_round_5",
        }
        if any(
            not required_q.issubset(row)
            or row.get("all_scores_finite") is not True
            for row in all_rows
        ):
            raise RuntimeError("a scored sample lacks required finite q fields")

        raw_path = output / "record_scores_v6.jsonl"
        atomic_write_jsonl(raw_path, all_rows)
        v6_image_rows, v6_summary = summarize_v6(
            config["config_id"], config["method"], all_rows
        )
        v6_image_path = output / "image_scores_v6.jsonl"
        atomic_write_jsonl(v6_image_path, v6_image_rows)
        atomic_write_json(output / "v6_summary.json", v6_summary)

        risk_rows = derive_risk_rows(all_rows)
        risk_path = output / "record_risks.jsonl"
        atomic_write_jsonl(risk_path, risk_rows)
        image_risks, risk_summary = summarize_risks(
            risk_rows, expected_image_count=EXPECTED_VALID_IMAGE_COUNT
        )
        image_risk_path = output / "image_group_risks.jsonl"
        atomic_write_jsonl(image_risk_path, image_risks)
        atomic_write_json(output / "risk_summary.json", risk_summary)
        atomic_write_json(
            output / "category_summary.json",
            {
                "schema_version": 1,
                "model_id": config["config_id"],
                "categories": risk_summary["category_summaries"],
            },
        )
        _write_category_csv(
            output / "category_summary.csv", risk_summary
        )

        summary = _single_model_summary(config, adapter, risk_summary)
        summary.update(
            {
                "config": config_receipt,
                "frozen_v6_protocol_sha256": frozen_protocol_sha,
                "record_scores_v6_path": str(raw_path),
                "record_scores_v6_sha256": sha256_file(raw_path),
                "record_risks_path": str(risk_path),
                "record_risks_sha256": sha256_file(risk_path),
                "image_group_risks_path": str(image_risk_path),
                "image_group_risks_sha256": sha256_file(image_risk_path),
            }
        )
        atomic_write_json(output / "model_summary.json", summary)
        cache_receipt = cache.receipt()
        cache_receipt["cache_no_cache_equivalence"] = cache_equivalence
        atomic_write_json(output / "cache_receipt.json", cache_receipt)
        receipt = {
            "schema_version": 1,
            "status": "complete",
            "config_id": config["config_id"],
            "config": config_receipt,
            "runtime_preflight": runtime,
            "environment": live_environment,
            "frozen_v6_logical_device": frozen_device,
            "runtime_single_visible_gpu_logical_device": args.device,
            "logical_device_remap_only": True,
            "frozen_v6_protocol_sha256": frozen_protocol_sha,
            "evaluation_seed": config["evaluation"]["evaluation_seed"],
            "candidate_and_hull_rule": config["evaluation"][
                "candidate_and_hull_rule"
            ],
            "mismatch_k": config["evaluation"]["mismatch_k"],
            "record_count": len(risk_rows),
            "image_count": len(image_risks),
            "q_correct_and_five_mismatch_per_sample": True,
            "old_v6_fields_retained": True,
            "all_scores_finite": True,
            "risk_ranges_passed": all(
                risk_summary["range_checks"].values()
            ),
            "identity_tolerance": risk_summary["identity_check"][
                "tolerance"
            ],
            "maximum_identity_error": max(
                risk_summary["identity_check"]["maximum_error_record"],
                risk_summary["identity_check"][
                    "maximum_error_image_group"
                ],
            ),
            "identity_check_passed": risk_summary["identity_check"]["passes"],
            "m0_check": "not_applicable_to_M2_M3",
            "certified": False,
            "invalid_for_formal_certification_reasons": list(
                CURRENT_INVALID_REASONS
            ),
            "cache_no_cache_equivalence": cache_equivalence,
            "cache_receipt_path": str(output / "cache_receipt.json"),
            "shards": shard_receipts,
            "model_summary_path": str(output / "model_summary.json"),
            "model_summary_sha256": sha256_file(
                output / "model_summary.json"
            ),
            "seconds": time.time() - started,
            "automatic_retry": False,
            "evaluation_rule_changed": False,
        }
        if (
            not receipt["risk_ranges_passed"]
            or not receipt["identity_check_passed"]
            or receipt["maximum_identity_error"] > 1e-6
            or not math.isfinite(receipt["maximum_identity_error"])
        ):
            raise RuntimeError("post-scoring risk checks failed")
        atomic_write_json(output / "scoring_receipt.json", receipt)
        del model, cache
        gc.collect()
        torch.cuda.empty_cache()
        return receipt
    except BaseException as error:
        atomic_write_json(
            output / "failure_receipt.json",
            {
                "status": "failed",
                "config_id": args.config_id,
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--adapter-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    result = score(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
