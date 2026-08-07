#!/usr/bin/env python3
"""Apply the immutable XID-01 round4 pilot or three-root decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    read_jsonl,
)
from experiments.xid01 import CONDITIONS, MAPPING_ROOTS, sha256_file


BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260807


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root-dir",
        action="append",
        required=True,
        help="mapping_root:/absolute/root_directory",
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def _parse_roots(values: list[str]) -> dict[int, Path]:
    roots = {}
    for value in values:
        root_text, separator, path_text = value.partition(":")
        if not separator:
            raise ValueError("root-dir must be mapping_root:path")
        root = int(root_text)
        if root not in MAPPING_ROOTS or root in roots:
            raise ValueError("root-dir has invalid or duplicate mapping root")
        roots[root] = Path(path_text).resolve()
    if set(roots) not in (
        {MAPPING_ROOTS[0]},
        set(MAPPING_ROOTS),
    ):
        raise ValueError("analysis requires pilot root or all three roots")
    return roots


def _load_condition(root_dir: Path, condition: str) -> tuple[dict, dict, list]:
    training_path = root_dir / condition / "training/training_manifest.json"
    scoring_path = root_dir / condition / "scoring/scoring_receipt.json"
    raw_path = root_dir / condition / "scoring/item_scores.jsonl"
    training = json.loads(training_path.read_text(encoding="utf-8"))
    scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
    rows = read_jsonl(raw_path)
    if (
        training.get("status") != "complete"
        or scoring.get("status") != "complete"
        or scoring.get("mode") != "full"
        or training.get("candidate") != "XID-01"
        or scoring.get("candidate") != "XID-01"
        or training.get("round") != 4
        or scoring.get("round") != 4
        or training.get("condition") != condition
        or scoring.get("condition") != condition
        or training.get("final_confirmation_accessed") is not False
        or scoring.get("final_confirmation_accessed") is not False
        or scoring["scoring"]["raw_rows_sha256"] != sha256_file(raw_path)
    ):
        raise ValueError("condition training/scoring receipt is invalid")
    return training, scoring, rows


def _training_pair_checks(left: dict, right: dict) -> dict[str, bool]:
    left_epochs = left["training"]["epoch_receipts"]
    right_epochs = right["training"]["epoch_receipts"]
    return {
        "mapping_root_matches": left["mapping_root"] == right["mapping_root"],
        "coordinate_dimensions_match": left["model"][
            "coordinate_dimensions"
        ]
        == right["model"]["coordinate_dimensions"],
        "initial_frozen_hash_matches": left["model"][
            "initial_frozen_parameter_sha256"
        ]
        == right["model"]["initial_frozen_parameter_sha256"],
        "prepared_audit_matches": left["data"]["prepared_audit_sha256"]
        == right["data"]["prepared_audit_sha256"],
        "data_rows_match": left["data"]["rows"] == right["data"]["rows"],
        "training_configuration_matches": all(
            left["training"][key] == right["training"][key]
            for key in (
                "train_seed",
                "learning_rate",
                "epochs",
                "micro_batch_size",
                "gradient_accumulation_steps",
                "effective_batch_size",
                "optimizer_steps_expected",
                "optimizer_steps_observed",
            )
        ),
        "exact_2070_steps": left["training"]["optimizer_steps_observed"]
        == right["training"]["optimizer_steps_observed"]
        == 2070,
        "epoch_permutations_match": [
            row["permutation_sha256"] for row in left_epochs
        ]
        == [
            row["permutation_sha256"] for row in right_epochs
        ],
        "losses_finite": left["training"]["all_losses_finite"]
        and right["training"]["all_losses_finite"],
        "gradient_norms_finite": left["training"][
            "all_gradient_norms_finite"
        ]
        and right["training"]["all_gradient_norms_finite"],
        "frozen_parameters_unchanged": left["model"][
            "frozen_parameters_unchanged"
        ]
        and right["model"]["frozen_parameters_unchanged"],
    }


def _pair_rows(
    ambiguous: list[dict[str, Any]],
    consistent: list[dict[str, Any]],
    *,
    root: int,
) -> list[dict[str, Any]]:
    if [row["item_id"] for row in ambiguous] != [
        row["item_id"] for row in consistent
    ]:
        raise ValueError("paired scoring item order differs")
    invariants = (
        "panel",
        "item_id",
        "group_id",
        "key",
        "visual_bit",
        "gold",
        "image_sha256",
        "normalized_pixel_sha256",
    )
    output = []
    for left, right in zip(ambiguous, consistent, strict=True):
        if any(left[key] != right[key] for key in invariants):
            raise ValueError("paired XID-01 scoring metadata differs")
        output.append(
            {
                "mapping_root": root,
                "panel": left["panel"],
                "item_id": left["item_id"],
                "group_id": left["group_id"],
                "key": left["key"],
                "visual_bit": left["visual_bit"],
                "gold": left["gold"],
                "ambiguous_correct": bool(left["correct"]),
                "consistent_correct": bool(right["correct"]),
                "accuracy_difference": float(right["correct"])
                - float(left["correct"]),
                "ambiguous_margin_bits_per_token": float(
                    left["gold_margin_bits_per_token"]
                ),
                "consistent_margin_bits_per_token": float(
                    right["gold_margin_bits_per_token"]
                ),
                "margin_difference_bits_per_token": float(
                    right["gold_margin_bits_per_token"]
                )
                - float(left["gold_margin_bits_per_token"]),
            }
        )
    return output


def _bootstrap(values: list[float], *, seed_offset: int) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    if not vector.size or not np.isfinite(vector).all():
        raise ValueError("bootstrap requires finite nonempty values")
    generator = np.random.default_rng(BOOTSTRAP_SEED + seed_offset)
    replicate_means = np.empty(BOOTSTRAP_REPLICATES, dtype=np.float64)
    chunk = 250
    for start in range(0, BOOTSTRAP_REPLICATES, chunk):
        count = min(chunk, BOOTSTRAP_REPLICATES - start)
        indices = generator.integers(
            0, vector.size, size=(count, vector.size)
        )
        replicate_means[start : start + count] = vector[indices].mean(axis=1)
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED + seed_offset,
        "unit_count": int(vector.size),
        "mean": float(vector.mean()),
        "ci95": [
            float(np.quantile(replicate_means, 0.025)),
            float(np.quantile(replicate_means, 0.975)),
        ],
    }


def _root_summary(
    root: int,
    paired: list[dict[str, Any]],
    training_checks: dict[str, bool],
) -> dict[str, Any]:
    if not all(training_checks.values()):
        raise ValueError("paired training invariants did not all pass")
    target = [row for row in paired if row["panel"] == "target"]
    mechanism = [row for row in paired if row["panel"] == "mechanism"]
    groups = sorted({row["group_id"] for row in paired})
    if len(target) != len(groups) or len(mechanism) != 8 * len(groups):
        raise ValueError("XID-01 panel does not contain 1+8 rows per group")
    target_by_group = {row["group_id"]: row for row in target}
    mechanism_by_group = {
        group: [row for row in mechanism if row["group_id"] == group]
        for group in groups
    }
    mechanism_groups = []
    for group in groups:
        rows = mechanism_by_group[group]
        if len(rows) != 8:
            raise ValueError("mechanism group does not contain eight cells")
        mechanism_groups.append(
            {
                "group_id": group,
                "ambiguous_accuracy": float(
                    np.mean([row["ambiguous_correct"] for row in rows])
                ),
                "consistent_accuracy": float(
                    np.mean([row["consistent_correct"] for row in rows])
                ),
                "accuracy_difference": float(
                    np.mean([row["accuracy_difference"] for row in rows])
                ),
                "ambiguous_full_rule_success": all(
                    row["ambiguous_correct"] for row in rows
                ),
                "consistent_full_rule_success": all(
                    row["consistent_correct"] for row in rows
                ),
            }
        )
    target_rows = [target_by_group[group] for group in groups]
    target_summary = {
        "independent_image_groups": len(groups),
        "ambiguous_accuracy": float(
            np.mean([row["ambiguous_correct"] for row in target_rows])
        ),
        "consistent_accuracy": float(
            np.mean([row["consistent_correct"] for row in target_rows])
        ),
        "accuracy_difference": float(
            np.mean([row["accuracy_difference"] for row in target_rows])
        ),
        "accuracy_difference_bootstrap": _bootstrap(
            [row["accuracy_difference"] for row in target_rows],
            seed_offset=(root - 43300) * 10,
        ),
        "ambiguous_gold_margin_bits_per_token": float(
            np.mean(
                [row["ambiguous_margin_bits_per_token"] for row in target_rows]
            )
        ),
        "consistent_gold_margin_bits_per_token": float(
            np.mean(
                [row["consistent_margin_bits_per_token"] for row in target_rows]
            )
        ),
        "gold_margin_difference_bits_per_token": float(
            np.mean(
                [row["margin_difference_bits_per_token"] for row in target_rows]
            )
        ),
    }
    mechanism_summary = {
        "independent_image_groups": len(groups),
        "ambiguous_accuracy": float(
            np.mean([row["ambiguous_accuracy"] for row in mechanism_groups])
        ),
        "consistent_accuracy": float(
            np.mean([row["consistent_accuracy"] for row in mechanism_groups])
        ),
        "accuracy_difference": float(
            np.mean([row["accuracy_difference"] for row in mechanism_groups])
        ),
        "accuracy_difference_bootstrap": _bootstrap(
            [row["accuracy_difference"] for row in mechanism_groups],
            seed_offset=(root - 43300) * 10 + 1,
        ),
        "ambiguous_full_rule_success": float(
            np.mean(
                [row["ambiguous_full_rule_success"] for row in mechanism_groups]
            )
        ),
        "consistent_full_rule_success": float(
            np.mean(
                [row["consistent_full_rule_success"] for row in mechanism_groups]
            )
        ),
        "full_rule_success_difference": float(
            np.mean(
                [
                    float(row["consistent_full_rule_success"])
                    - float(row["ambiguous_full_rule_success"])
                    for row in mechanism_groups
                ]
            )
        ),
    }
    return {
        "mapping_root": root,
        "training_pair_checks": training_checks,
        "target": target_summary,
        "mechanism": mechanism_summary,
    }


def _pilot_judgment(summary: dict[str, Any]) -> dict[str, Any]:
    target = summary["target"]
    mechanism = summary["mechanism"]
    criteria = {
        "paired_engineering_invariants_pass": all(
            summary["training_pair_checks"].values()
        ),
        "target_difference_at_least_0p10": target["accuracy_difference"]
        >= 0.10,
        "target_ci_lower_above_zero": target[
            "accuracy_difference_bootstrap"
        ]["ci95"][0]
        > 0.0,
        "consistent_target_accuracy_at_least_0p65": target[
            "consistent_accuracy"
        ]
        >= 0.65,
        "target_gold_margin_difference_positive": target[
            "gold_margin_difference_bits_per_token"
        ]
        > 0.0,
        "mechanism_difference_at_least_0p05": mechanism[
            "accuracy_difference"
        ]
        >= 0.05,
        "mechanism_ci_lower_above_zero": mechanism[
            "accuracy_difference_bootstrap"
        ]["ci95"][0]
        > 0.0,
        "consistent_mechanism_accuracy_at_least_0p75": mechanism[
            "consistent_accuracy"
        ]
        >= 0.75,
        "full_rule_success_difference_positive": mechanism[
            "full_rule_success_difference"
        ]
        > 0.0,
    }
    passed = all(criteria.values())
    return {
        "decision": "PILOT_POSITIVE" if passed else "REJECT_IDEA",
        "criteria": criteria,
        "all_criteria_met": passed,
        "seed_escalation_authorized": passed,
    }


def _final_judgment(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    targets = [row["target"] for row in summaries]
    mechanisms = [row["mechanism"] for row in summaries]
    criteria = {
        "all_primary_differences_positive": all(
            row["accuracy_difference"] > 0 for row in targets
        ),
        "two_primary_effects_at_least_0p10_with_ci": sum(
            row["accuracy_difference"] >= 0.10
            and row["accuracy_difference_bootstrap"]["ci95"][0] > 0
            for row in targets
        )
        >= 2,
        "mean_primary_difference_at_least_0p10": float(
            np.mean([row["accuracy_difference"] for row in targets])
        )
        >= 0.10,
        "mean_consistent_primary_accuracy_at_least_0p65": float(
            np.mean([row["consistent_accuracy"] for row in targets])
        )
        >= 0.65,
        "all_mechanism_differences_positive": all(
            row["accuracy_difference"] > 0 for row in mechanisms
        ),
        "mean_mechanism_difference_at_least_0p05": float(
            np.mean([row["accuracy_difference"] for row in mechanisms])
        )
        >= 0.05,
        "two_mechanism_ci_lowers_above_zero": sum(
            row["accuracy_difference_bootstrap"]["ci95"][0] > 0
            for row in mechanisms
        )
        >= 2,
        "mean_primary_margin_difference_positive": float(
            np.mean(
                [
                    row["gold_margin_difference_bits_per_token"]
                    for row in targets
                ]
            )
        )
        > 0,
        "mean_full_rule_success_difference_positive": float(
            np.mean(
                [
                    row["full_rule_success_difference"]
                    for row in mechanisms
                ]
            )
        )
        > 0,
    }
    passed = all(criteria.values())
    return {
        "decision": "PROMISING" if passed else "REJECT_IDEA",
        "criteria": criteria,
        "all_criteria_met": passed,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    roots = _parse_roots(args.root_dir)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"analysis output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    data_audit = json.loads(
        (args.prepared_dir / "data_audit.json").read_text(encoding="utf-8")
    )
    if (
        data_audit.get("eligible_for_training") is not True
        or not all(data_audit.get("checks", {}).values())
    ):
        raise ValueError("prepared data audit does not permit analysis")
    summaries = []
    all_paired = []
    inputs = {}
    for root, root_dir in sorted(roots.items()):
        ambiguous_train, ambiguous_score, ambiguous_rows = _load_condition(
            root_dir, "interaction-ambiguous"
        )
        consistent_train, consistent_score, consistent_rows = _load_condition(
            root_dir, "interaction-consistent"
        )
        if any(
            receipt["mapping_root"] != root
            for receipt in (
                ambiguous_train,
                ambiguous_score,
                consistent_train,
                consistent_score,
            )
        ):
            raise ValueError("root directory contains wrong mapping root")
        checks = _training_pair_checks(ambiguous_train, consistent_train)
        paired = _pair_rows(ambiguous_rows, consistent_rows, root=root)
        summaries.append(_root_summary(root, paired, checks))
        all_paired.extend(paired)
        inputs[str(root)] = {
            condition: {
                "training_manifest_sha256": sha256_file(
                    root_dir
                    / condition
                    / "training/training_manifest.json"
                ),
                "scoring_receipt_sha256": sha256_file(
                    root_dir
                    / condition
                    / "scoring/scoring_receipt.json"
                ),
                "item_scores_sha256": sha256_file(
                    root_dir / condition / "scoring/item_scores.jsonl"
                ),
            }
            for condition in CONDITIONS
        }
    judgment = (
        _pilot_judgment(summaries[0])
        if set(roots) == {MAPPING_ROOTS[0]}
        else _final_judgment(summaries)
    )
    result = {
        "schema_version": 1,
        "status": "complete",
        "candidate": "XID-01",
        "round": 4,
        "analysis_type": (
            "paired_pilot"
            if set(roots) == {MAPPING_ROOTS[0]}
            else "three_root_final"
        ),
        "mapping_roots": sorted(roots),
        "root_summaries": summaries,
        "judgment": judgment,
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "base_seed": BOOTSTRAP_SEED,
            "unit": "independent held-out base-image group",
        },
        "inputs": inputs,
        "prepared_data_audit_sha256": sha256_file(
            args.prepared_dir / "data_audit.json"
        ),
        "final_confirmation_accessed": False,
    }
    atomic_write_jsonl(output / "paired_item_differences.jsonl", all_paired)
    atomic_write_json(output / "analysis.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    analyze(parse_args())
