#!/usr/bin/env python3
"""Apply the frozen first-gate checks to low M2/M3 seed 43101."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.phase3_risk_v1.budget_configs import _pair_common
from experiments.phase3_risk_v1.budget_runtime import load_frozen_config
from experiments.phase3_risk_v1.summarize_and_plot import paired_differences
from experiments.phase3_v6.scoring.common import atomic_write_json, read_json


GATE_IDS = ("M2-low-seed-43101", "M3-low-seed-43101")


def check(artifact_root: Path, output: Path) -> dict:
    root = artifact_root.resolve()
    configs = {}
    summaries = []
    checks = []
    for config_id in GATE_IDS:
        config, config_receipt = load_frozen_config(config_id)
        configs[config["method"]] = config
        run_dir = root / config["output_relative_path"]
        run = read_json(run_dir / "run_receipt.json")
        training = read_json(run_dir / "training/training_manifest.json")
        adapter = read_json(run_dir / "encode/adapter_summary.json")
        scoring = read_json(run_dir / "scoring/scoring_receipt.json")
        summary = read_json(run_dir / "scoring/model_summary.json")
        model_checks = {
            "run_complete": run.get("status") == "complete",
            "training_complete": training.get("status") == "complete",
            "no_nan_or_interruption": (
                training.get("training", {}).get("all_losses_finite") is True
                and training.get("training", {}).get(
                    "all_gradient_norms_finite"
                )
                is True
            ),
            "steps_match_frozen_config": (
                training.get("training", {}).get(
                    "optimizer_steps_observed"
                )
                == config["training"]["learning_rate_schedule"][
                    "total_steps"
                ]
                == training.get("training", {}).get(
                    "optimizer_steps_expected"
                )
            ),
            "epochs_match_frozen_config": (
                training.get("training", {}).get("epochs")
                == config["training"]["epochs"]
            ),
            "quantization_matches_protocol": (
                adapter.get("format") == "MMS2"
                and adapter.get("format_version") == 1
                and adapter.get("codec") == "zlib-9"
                and adapter.get("quantization_bits_label") == 3
                and adapter.get("quantization_levels")
                == config["quantization"]["levels"]
            ),
            "mms2_loader_passed": (
                adapter.get("decode_reencode_byte_equivalence") is True
                and adapter.get("existing_coordinate_loader_equivalence")
                is True
            ),
            "six_q_values_per_sample": scoring.get(
                "q_correct_and_five_mismatch_per_sample"
            )
            is True,
            "risk_ranges_passed": scoring.get("risk_ranges_passed") is True,
            "identity_error_at_most_1e_6": (
                float(scoring.get("maximum_identity_error", 1.0)) <= 1e-6
            ),
            "old_v6_fields_retained": scoring.get(
                "old_v6_fields_retained"
            )
            is True,
            "coordinate_budget_2048": (
                training.get("total_coordinate_budget") == 2048
                and sum(training.get("coordinate_dimensions", {}).values())
                == 2048
            ),
            "certified_false": (
                scoring.get("certified") is False
                and summary.get("certified") is False
            ),
            "invalid_reasons_exact": scoring.get(
                "invalid_for_formal_certification_reasons"
            )
            == ["post_hoc_metric_design", "coupled_mismatch_donors"],
            "no_auto_tuning_or_checkpoint_selection": (
                training.get("training", {}).get(
                    "automatic_hyperparameter_tuning"
                )
                is False
                and training.get("training", {}).get(
                    "checkpoint_selection"
                )
                == "final_frozen_schedule_state_only"
                and training.get("training", {}).get("retry_count") == 0
                and scoring.get("automatic_retry") is False
                and scoring.get("evaluation_rule_changed") is False
            ),
            "config_hash_verified": (
                training.get("config", {}).get("sha256")
                == config_receipt["sha256"]
            ),
        }
        checks.append(
            {
                "config_id": config_id,
                "checks": model_checks,
                "passed": all(model_checks.values()),
                "run_dir": str(run_dir),
            }
        )
        summaries.append(
            {
                "model_id": config_id,
                "method": config["method"],
                "budget": config["budget"],
                "experiment_seed": config["experiment_seed"],
                "total_coordinate_budget": config[
                    "total_coordinate_budget"
                ],
                "total_description_bits": summary[
                    "total_description_bits"
                ],
                "empirical_language_risk": summary["empirical_risks"][
                    "language_risk"
                ],
                "empirical_visual_risk": summary["empirical_risks"][
                    "visual_risk"
                ],
                "empirical_total_semantic_risk": summary[
                    "empirical_risks"
                ]["total_semantic_risk"],
            }
        )
    pair_conditions_equal = (
        _pair_common(configs["M2"]) == _pair_common(configs["M3"])
    )
    pair = paired_differences(summaries)[0]
    passed = all(row["passed"] for row in checks) and pair_conditions_equal
    receipt = {
        "schema_version": 1,
        "gate": "low_seed_43101_M2_M3_complete_pipeline",
        "status": "passed" if passed else "failed",
        "passed": passed,
        "models": checks,
        "pair_training_conditions_equal_except_shared_coordinate_structure": (
            pair_conditions_equal
        ),
        "pair_difference": pair,
        "automatic_protocol_changes": False,
    }
    atomic_write_json(output, receipt)
    if not passed:
        raise RuntimeError("low-43101 first execution gate failed")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.artifact_root, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
