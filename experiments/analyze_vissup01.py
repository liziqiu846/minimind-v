#!/usr/bin/env python3
"""Apply the immutable VISSUP-01 pilot or three-root decision."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    read_jsonl,
)
from experiments.vissup01 import sha256_file


BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260807
CONDITIONS = ("label-revealed", "visual-necessary")


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
        if root not in (43101, 43102, 43103) or root in roots:
            raise ValueError("root-dir has invalid or duplicate mapping root")
        roots[root] = Path(path_text).resolve()
    if set(roots) not in ({43101}, {43101, 43102, 43103}):
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
        "mapping_root_matches": left["mapping_root"]
        == right["mapping_root"],
        "coordinate_dimensions_match": left["model"][
            "coordinate_dimensions"
        ]
        == right["model"]["coordinate_dimensions"],
        "initial_frozen_hash_matches": left["model"][
            "initial_frozen_parameter_sha256"
        ]
        == right["model"]["initial_frozen_parameter_sha256"],
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
    control: list[dict[str, Any]],
    visual: list[dict[str, Any]],
    *,
    root: int,
) -> list[dict[str, Any]]:
    if [row["item_id"] for row in control] != [
        row["item_id"] for row in visual
    ]:
        raise ValueError("paired scoring item order differs")
    output = []
    invariant_keys = (
        "panel",
        "item_id",
        "gold_label",
        "legal_labels",
        "choice_count",
        "normalized_pixel_sha256",
    )
    for left, right in zip(control, visual, strict=True):
        if any(left[key] != right[key] for key in invariant_keys):
            raise ValueError("paired scoring row metadata differs")
        row = {
            "mapping_root": root,
            "panel": left["panel"],
            "item_id": left["item_id"],
            "normalized_pixel_sha256": left[
                "normalized_pixel_sha256"
            ],
            "control_correct": bool(left["correct"]),
            "visual_correct": bool(right["correct"]),
            "accuracy_difference": float(right["correct"])
            - float(left["correct"]),
            "control_margin_bits_per_token": float(
                left["gold_margin_bits_per_token"]
            ),
            "visual_margin_bits_per_token": float(
                right["gold_margin_bits_per_token"]
            ),
            "margin_difference_bits_per_token": float(
                right["gold_margin_bits_per_token"]
            )
            - float(left["gold_margin_bits_per_token"]),
        }
        if left["panel"] == "cvbench":
            if (
                left["task"] != right["task"]
                or left["source"] != right["source"]
            ):
                raise ValueError("paired CV-Bench strata differ")
            row.update(
                {
                    "task": left["task"],
                    "source": left["source"],
                }
            )
        output.append(row)
    return output


def _group_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["normalized_pixel_sha256"]].append(row)
    output = []
    for group, values in sorted(groups.items()):
        output.append(
            {
                "normalized_pixel_sha256": group,
                "control_accuracy": float(
                    np.mean([row["control_correct"] for row in values])
                ),
                "visual_accuracy": float(
                    np.mean([row["visual_correct"] for row in values])
                ),
                "accuracy_difference": float(
                    np.mean(
                        [row["accuracy_difference"] for row in values]
                    )
                ),
                "control_margin_bits_per_token": float(
                    np.mean(
                        [
                            row["control_margin_bits_per_token"]
                            for row in values
                        ]
                    )
                ),
                "visual_margin_bits_per_token": float(
                    np.mean(
                        [
                            row["visual_margin_bits_per_token"]
                            for row in values
                        ]
                    )
                ),
                "margin_difference_bits_per_token": float(
                    np.mean(
                        [
                            row["margin_difference_bits_per_token"]
                            for row in values
                        ]
                    )
                ),
                "row_count": len(values),
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
        replicate_means[start : start + count] = vector[indices].mean(
            axis=1
        )
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


def _stratum_summary(
    rows: list[dict[str, Any]], key: str
) -> dict[str, dict[str, float]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    output = {}
    for name, values in sorted(groups.items()):
        grouped = _group_rows(values)
        output[name] = {
            "rows": len(values),
            "independent_image_groups": len(grouped),
            "accuracy_difference": float(
                np.mean([row["accuracy_difference"] for row in grouped])
            ),
            "margin_difference_bits_per_token": float(
                np.mean(
                    [
                        row["margin_difference_bits_per_token"]
                        for row in grouped
                    ]
                )
            ),
        }
    return output


def _root_summary(
    root: int,
    paired: list[dict[str, Any]],
    training_checks: dict[str, bool],
) -> dict[str, Any]:
    if not all(training_checks.values()):
        raise ValueError("paired training invariants did not all pass")
    panels = {}
    for panel_index, panel in enumerate(("rotation", "cvbench")):
        panel_rows = [row for row in paired if row["panel"] == panel]
        grouped = _group_rows(panel_rows)
        panel_summary = {
            "rows": len(panel_rows),
            "independent_image_groups": len(grouped),
            "control_accuracy": float(
                np.mean([row["control_accuracy"] for row in grouped])
            ),
            "visual_accuracy": float(
                np.mean([row["visual_accuracy"] for row in grouped])
            ),
            "accuracy_difference": float(
                np.mean(
                    [row["accuracy_difference"] for row in grouped]
                )
            ),
            "control_margin_bits_per_token": float(
                np.mean(
                    [
                        row["control_margin_bits_per_token"]
                        for row in grouped
                    ]
                )
            ),
            "visual_margin_bits_per_token": float(
                np.mean(
                    [
                        row["visual_margin_bits_per_token"]
                        for row in grouped
                    ]
                )
            ),
            "margin_difference_bits_per_token": float(
                np.mean(
                    [
                        row["margin_difference_bits_per_token"]
                        for row in grouped
                    ]
                )
            ),
            "accuracy_difference_bootstrap": _bootstrap(
                [row["accuracy_difference"] for row in grouped],
                seed_offset=(root - 43100) * 10 + panel_index,
            ),
        }
        if panel == "cvbench":
            panel_summary["by_task"] = _stratum_summary(
                panel_rows, "task"
            )
            panel_summary["by_source"] = _stratum_summary(
                panel_rows, "source"
            )
        panels[panel] = panel_summary
    return {
        "mapping_root": root,
        "training_pair_checks": training_checks,
        "panels": panels,
    }


def _pilot_judgment(summary: dict[str, Any]) -> dict[str, Any]:
    rotation = summary["panels"]["rotation"]
    cvbench = summary["panels"]["cvbench"]
    criteria = {
        "paired_training_invariants_pass": all(
            summary["training_pair_checks"].values()
        ),
        "rotation_difference_at_least_0p05": rotation[
            "accuracy_difference"
        ]
        >= 0.05,
        "rotation_ci_lower_above_zero": rotation[
            "accuracy_difference_bootstrap"
        ]["ci95"][0]
        > 0.0,
        "visual_rotation_accuracy_at_least_0p30": rotation[
            "visual_accuracy"
        ]
        >= 0.30,
        "cvbench_difference_at_least_0p01": cvbench[
            "accuracy_difference"
        ]
        >= 0.01,
        "cvbench_margin_difference_positive": cvbench[
            "margin_difference_bits_per_token"
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
    rotations = [row["panels"]["rotation"] for row in summaries]
    cvbench = [row["panels"]["cvbench"] for row in summaries]
    task_names = ("Count", "Relation")
    criteria = {
        "all_rotation_differences_positive": all(
            row["accuracy_difference"] > 0.0 for row in rotations
        ),
        "at_least_two_rotation_differences_at_least_0p05_with_ci": sum(
            row["accuracy_difference"] >= 0.05
            and row["accuracy_difference_bootstrap"]["ci95"][0] > 0.0
            for row in rotations
        )
        >= 2,
        "mean_rotation_difference_at_least_0p05": float(
            np.mean([row["accuracy_difference"] for row in rotations])
        )
        >= 0.05,
        "all_cvbench_differences_positive": all(
            row["accuracy_difference"] > 0.0 for row in cvbench
        ),
        "at_least_two_cvbench_differences_at_least_0p01": sum(
            row["accuracy_difference"] >= 0.01 for row in cvbench
        )
        >= 2,
        "mean_cvbench_difference_at_least_0p01": float(
            np.mean([row["accuracy_difference"] for row in cvbench])
        )
        >= 0.01,
        "mean_cvbench_margin_difference_positive": float(
            np.mean(
                [
                    row["margin_difference_bits_per_token"]
                    for row in cvbench
                ]
            )
        )
        > 0.0,
        "both_task_mean_differences_positive": all(
            float(
                np.mean(
                    [row["by_task"][task]["accuracy_difference"] for row in cvbench]
                )
            )
            > 0.0
            for task in task_names
        ),
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
    if data_audit.get("eligible_for_training") is not True:
        raise ValueError("prepared data audit does not permit analysis")
    summaries = []
    all_paired = []
    input_receipts = {}
    for root, root_dir in sorted(roots.items()):
        control_train, control_score, control_rows = _load_condition(
            root_dir, "label-revealed"
        )
        visual_train, visual_score, visual_rows = _load_condition(
            root_dir, "visual-necessary"
        )
        if (
            control_train["mapping_root"] != root
            or visual_train["mapping_root"] != root
            or control_score["mapping_root"] != root
            or visual_score["mapping_root"] != root
        ):
            raise ValueError("root directory contains wrong mapping root")
        checks = _training_pair_checks(control_train, visual_train)
        paired = _pair_rows(control_rows, visual_rows, root=root)
        summaries.append(_root_summary(root, paired, checks))
        all_paired.extend(paired)
        input_receipts[str(root)] = {
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
        if set(roots) == {43101}
        else _final_judgment(summaries)
    )
    result = {
        "schema_version": 1,
        "status": "complete",
        "candidate": "VISSUP-01",
        "round": 2,
        "analysis_type": (
            "paired_pilot" if set(roots) == {43101} else "three_root_final"
        ),
        "mapping_roots": sorted(roots),
        "root_summaries": summaries,
        "judgment": judgment,
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "base_seed": BOOTSTRAP_SEED,
            "unit": "independent normalized pixel group",
        },
        "inputs": input_receipts,
        "prepared_data_audit_sha256": sha256_file(
            args.prepared_dir / "data_audit.json"
        ),
        "final_confirmation_accessed": False,
    }
    atomic_write_jsonl(output / "paired_item_differences.jsonl", all_paired)
    atomic_write_json(output / "analysis.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    analyze(parse_args())


if __name__ == "__main__":
    main()
