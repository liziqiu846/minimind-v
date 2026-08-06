#!/usr/bin/env python3
"""Apply the immutable PROJALLOC-01 pilot or three-root decision."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    read_jsonl,
)
from experiments.projalloc01 import (
    CANDIDATE,
    CONDITIONS,
    EXPECTED_DIMENSIONS,
    MAPPING_FACTOR_COUNT,
    MAPPING_ROOTS,
    PILOT_ROOT,
    ROUND,
    TOTAL_COORDINATES,
    TRAIN_PARQUET_SHA256,
    verify_prepared_dir,
)
from experiments.vissup01 import sha256_file


BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260807
CURRENT = "current-allocation"
PROJECTOR = "projector-dominant"


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
    if set(roots) not in ({PILOT_ROOT}, set(MAPPING_ROOTS)):
        raise ValueError("analysis requires pilot root or all three roots")
    return roots


def _load_condition(
    root_dir: Path, condition: str
) -> tuple[dict, dict, list[dict[str, Any]]]:
    training_path = root_dir / condition / "training/training_manifest.json"
    scoring_path = root_dir / condition / "scoring/scoring_receipt.json"
    raw_path = root_dir / condition / "scoring/item_scores.jsonl"
    training = json.loads(training_path.read_text(encoding="utf-8"))
    scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
    rows = read_jsonl(raw_path)
    if (
        training.get("status") != "complete"
        or scoring.get("status") != "complete"
        or training.get("candidate") != CANDIDATE
        or scoring.get("candidate") != CANDIDATE
        or training.get("round") != ROUND
        or scoring.get("round") != ROUND
        or scoring.get("mode") != "full"
        or training.get("condition") != condition
        or scoring.get("condition") != condition
        or training.get("final_confirmation_accessed") is not False
        or scoring.get("final_confirmation_accessed") is not False
        or scoring["scoring"]["raw_rows_sha256"] != sha256_file(raw_path)
    ):
        raise ValueError("condition training/scoring receipt is invalid")
    return training, scoring, rows


def _projection_check(training: dict, condition: str) -> bool:
    receipt = training["model"].get("projection_preflight")
    if not isinstance(receipt, dict):
        return False
    root = str(training["mapping_root"])
    return (
        receipt.get("condition") == condition
        and receipt.get("coordinate_dimensions")
        == EXPECTED_DIMENSIONS[condition]
        and receipt.get("total_coordinates") == TOTAL_COORDINATES
        and receipt.get("mapping_factor_count") == MAPPING_FACTOR_COUNT
        and receipt.get("all_roots_reproducible") is True
        and receipt.get("all_coordinates_used") is True
        and set(receipt.get("roots", {})) == {root}
        and all(
            row["unused_coordinate_count"] == 0
            for row in receipt["roots"][root]["module_usage"].values()
        )
    )


def _training_pair_checks(
    current: dict, projector: dict
) -> dict[str, bool]:
    current_epochs = current["training"]["epoch_receipts"]
    projector_epochs = projector["training"]["epoch_receipts"]
    current_structure = current["model"]["initial_structure"]
    projector_structure = projector["model"]["initial_structure"]
    current_dimensions = current["model"]["coordinate_dimensions"]
    projector_dimensions = projector["model"]["coordinate_dimensions"]
    return {
        "mapping_root_matches": current["mapping_root"]
        == projector["mapping_root"],
        "current_dimensions_match_plan": current_dimensions
        == EXPECTED_DIMENSIONS[CURRENT],
        "projector_dimensions_match_plan": projector_dimensions
        == EXPECTED_DIMENSIONS[PROJECTOR],
        "both_total_4096": sum(current_dimensions.values())
        == sum(projector_dimensions.values())
        == TOTAL_COORDINATES,
        "target_names_match": current_structure["adapter"]["wrapped_names"]
        == projector_structure["adapter"]["wrapped_names"]
        and len(current_structure["adapter"]["wrapped_names"]) == 11,
        "mapping_factor_counts_match_plan": current_structure["adapter"][
            "mapping_factor_count"
        ]
        == projector_structure["adapter"]["mapping_factor_count"]
        == MAPPING_FACTOR_COUNT,
        "projection_preflight_current_pass": _projection_check(
            current, CURRENT
        ),
        "projection_preflight_projector_pass": _projection_check(
            projector, PROJECTOR
        ),
        "initial_frozen_hash_matches": current["model"][
            "initial_frozen_parameter_sha256"
        ]
        == projector["model"]["initial_frozen_parameter_sha256"],
        "final_frozen_hash_matches": current["model"][
            "final_frozen_parameter_sha256"
        ]
        == projector["model"]["final_frozen_parameter_sha256"],
        "data_sha_matches": current["data"]["sha256"]
        == projector["data"]["sha256"]
        == TRAIN_PARQUET_SHA256,
        "data_rows_match": current["data"]["rows"]
        == projector["data"]["rows"]
        == 11_008,
        "data_condition_matches": current["data"]["condition"]
        == projector["data"]["condition"]
        == "visual-necessary",
        "training_configuration_matches": all(
            current["training"][key] == projector["training"][key]
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
            row["permutation_sha256"] for row in current_epochs
        ]
        == [
            row["permutation_sha256"] for row in projector_epochs
        ],
        "losses_finite": current["training"]["all_losses_finite"]
        and projector["training"]["all_losses_finite"],
        "gradient_norms_finite": current["training"][
            "all_gradient_norms_finite"
        ]
        and projector["training"]["all_gradient_norms_finite"],
        "frozen_parameters_unchanged": current["model"][
            "frozen_parameters_unchanged"
        ]
        and projector["model"]["frozen_parameters_unchanged"],
    }


def _pair_rows(
    current: list[dict[str, Any]],
    projector: list[dict[str, Any]],
    *,
    root: int,
) -> list[dict[str, Any]]:
    if [row["item_id"] for row in current] != [
        row["item_id"] for row in projector
    ]:
        raise ValueError("paired scoring item order differs")
    invariant_keys = (
        "panel",
        "item_id",
        "gold_label",
        "legal_labels",
        "choice_count",
        "normalized_pixel_sha256",
    )
    output = []
    for left, right in zip(current, projector, strict=True):
        if any(left[key] != right[key] for key in invariant_keys):
            raise ValueError("paired scoring row metadata differs")
        row = {
            "mapping_root": root,
            "panel": left["panel"],
            "item_id": left["item_id"],
            "normalized_pixel_sha256": left[
                "normalized_pixel_sha256"
            ],
            "current_correct": bool(left["correct"]),
            "projector_correct": bool(right["correct"]),
            "accuracy_difference": float(right["correct"])
            - float(left["correct"]),
            "current_margin_bits_per_token": float(
                left["gold_margin_bits_per_token"]
            ),
            "projector_margin_bits_per_token": float(
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
            row.update({"task": left["task"], "source": left["source"]})
        output.append(row)
    return output


def _group_rows(
    rows: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["normalized_pixel_sha256"]].append(row)
    output = []
    for group, values in sorted(groups.items()):
        output.append(
            {
                "normalized_pixel_sha256": group,
                "current_accuracy": float(
                    np.mean([row["current_correct"] for row in values])
                ),
                "projector_accuracy": float(
                    np.mean([row["projector_correct"] for row in values])
                ),
                "accuracy_difference": float(
                    np.mean(
                        [row["accuracy_difference"] for row in values]
                    )
                ),
                "current_margin_bits_per_token": float(
                    np.mean(
                        [
                            row["current_margin_bits_per_token"]
                            for row in values
                        ]
                    )
                ),
                "projector_margin_bits_per_token": float(
                    np.mean(
                        [
                            row["projector_margin_bits_per_token"]
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
    strata: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        strata[str(row[key])].append(row)
    output = {}
    for name, values in sorted(strata.items()):
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
        failed = [key for key, passed in training_checks.items() if not passed]
        raise ValueError(f"paired training invariants failed: {failed}")
    panels = {}
    for panel_index, panel in enumerate(("rotation", "cvbench")):
        panel_rows = [row for row in paired if row["panel"] == panel]
        grouped = _group_rows(panel_rows)
        summary = {
            "rows": len(panel_rows),
            "independent_image_groups": len(grouped),
            "current_accuracy": float(
                np.mean([row["current_accuracy"] for row in grouped])
            ),
            "projector_accuracy": float(
                np.mean([row["projector_accuracy"] for row in grouped])
            ),
            "accuracy_difference": float(
                np.mean(
                    [row["accuracy_difference"] for row in grouped]
                )
            ),
            "current_margin_bits_per_token": float(
                np.mean(
                    [
                        row["current_margin_bits_per_token"]
                        for row in grouped
                    ]
                )
            ),
            "projector_margin_bits_per_token": float(
                np.mean(
                    [
                        row["projector_margin_bits_per_token"]
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
                seed_offset=(root - 43200) * 10 + panel_index,
            ),
        }
        if panel == "cvbench":
            summary["by_task"] = _stratum_summary(panel_rows, "task")
            summary["by_source"] = _stratum_summary(panel_rows, "source")
        panels[panel] = summary
    return {
        "mapping_root": root,
        "training_pair_checks": training_checks,
        "panels": panels,
    }


def pilot_judgment(summary: dict[str, Any]) -> dict[str, Any]:
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
        "projector_rotation_accuracy_at_least_0p30": rotation[
            "projector_accuracy"
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


def final_judgment(
    summaries: list[dict[str, Any]]
) -> dict[str, Any]:
    rotations = [row["panels"]["rotation"] for row in summaries]
    cvbench = [row["panels"]["cvbench"] for row in summaries]
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
                    [
                        row["by_task"][task]["accuracy_difference"]
                        for row in cvbench
                    ]
                )
            )
            > 0.0
            for task in ("Count", "Relation")
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
    verify_prepared_dir(args.prepared_dir)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"analysis output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    summaries = []
    all_paired = []
    input_receipts = {}
    for root, root_dir in sorted(roots.items()):
        current_train, current_score, current_rows = _load_condition(
            root_dir, CURRENT
        )
        projector_train, projector_score, projector_rows = _load_condition(
            root_dir, PROJECTOR
        )
        if any(
            receipt["mapping_root"] != root
            for receipt in (
                current_train,
                current_score,
                projector_train,
                projector_score,
            )
        ):
            raise ValueError("root directory contains wrong mapping root")
        checks = _training_pair_checks(current_train, projector_train)
        paired = _pair_rows(current_rows, projector_rows, root=root)
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
        pilot_judgment(summaries[0])
        if set(roots) == {PILOT_ROOT}
        else final_judgment(summaries)
    )
    result = {
        "schema_version": 1,
        "status": "complete",
        "candidate": CANDIDATE,
        "round": ROUND,
        "analysis_type": (
            "paired_pilot"
            if set(roots) == {PILOT_ROOT}
            else "three_root_final"
        ),
        "comparison": {
            "control": CURRENT,
            "intervention": PROJECTOR,
            "difference": "projector-dominant minus current-allocation",
        },
        "mapping_roots": sorted(roots),
        "root_summaries": summaries,
        "judgment": judgment,
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "base_seed": BOOTSTRAP_SEED,
            "unit": "independent normalized pixel group",
        },
        "inputs": input_receipts,
        "prepared_artifact_sha256": verify_prepared_dir(
            args.prepared_dir
        ),
        "final_confirmation_accessed": False,
    }
    atomic_write_jsonl(
        output / "paired_item_differences.jsonl", all_paired
    )
    atomic_write_json(output / "analysis.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    analyze(parse_args())


if __name__ == "__main__":
    main()
