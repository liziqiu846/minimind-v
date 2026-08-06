#!/usr/bin/env python3
"""One-shot preregistered aggregation and decision for VISCOND-01 round 1."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    read_jsonl,
    sha256_file,
)
from experiments.viscond01 import EXPECTED_CATEGORIES


BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_807
EXPECTED_BUDGETS = ("low", "current", "high")
EXPECTED_ROOTS = (43101, 43102, 43103)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-root", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--development-risks", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def mean(values: Iterable[float]) -> float:
    clean = [float(value) for value in values]
    if not clean or not all(math.isfinite(value) for value in clean):
        raise ValueError("mean requires a nonempty finite sequence")
    return math.fsum(clean) / len(clean)


def grouped_means(
    rows: Iterable[dict[str, Any]],
    field: str,
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["normalized_pixel_sha256"])].append(float(row[field]))
    if not grouped:
        raise ValueError("image-group aggregation received no rows")
    return {
        key: mean(values)
        for key, values in sorted(grouped.items())
    }


def bootstrap_mean(values: Iterable[float]) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.ndim != 1 or array.size < 2 or not np.isfinite(array).all():
        raise ValueError("bootstrap requires a finite one-dimensional sample")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    indices = rng.integers(
        0,
        array.size,
        size=(BOOTSTRAP_REPLICATES, array.size),
    )
    replicates = array[indices].mean(axis=1, dtype=np.float64)
    lower, upper = np.quantile(
        replicates, [0.025, 0.975], method="linear"
    )
    return {
        "estimate": float(array.mean()),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "bootstrap_standard_deviation": float(
            np.std(replicates, ddof=1)
        ),
        "group_count": int(array.size),
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
        "confidence_level": 0.95,
        "percentile_method": "numpy.quantile method=linear",
    }


def summarize_model_rows(
    model_id: str,
    rows: list[dict[str, Any]],
    expected_indices: list[int],
) -> dict[str, Any]:
    if [int(row["index"]) for row in rows] != expected_indices:
        raise ValueError(f"{model_id} item order differs from panel manifest")
    if any(row.get("all_scores_finite") is not True for row in rows):
        raise ValueError(f"{model_id} contains a non-finite row")
    group_v = grouped_means(rows, "visual_increment_bits_per_token")
    group_correct_margin = grouped_means(
        rows, "correct_margin_bits_per_token"
    )
    group_none_margin = grouped_means(
        rows, "no_pixel_margin_bits_per_token"
    )
    bootstrap = bootstrap_mean(group_v.values())

    categories = []
    for category in EXPECTED_CATEGORIES:
        selected = [row for row in rows if row["category"] == category]
        if not selected:
            raise ValueError(f"{model_id} lacks category {category}")
        category_groups = grouped_means(
            selected, "visual_increment_bits_per_token"
        )
        categories.append(
            {
                "category": category,
                "item_count": len(selected),
                "image_group_count": len(category_groups),
                "mean_visual_increment_bits_per_token": mean(
                    category_groups.values()
                ),
                "correct_accuracy": mean(
                    float(row["correct_is_accurate"]) for row in selected
                ),
                "no_pixel_accuracy": mean(
                    float(row["no_pixel_is_accurate"]) for row in selected
                ),
            }
        )
    return {
        "model_id": model_id,
        "item_count": len(rows),
        "image_group_count": len(group_v),
        "mean_visual_increment_bits_per_token": mean(group_v.values()),
        "visual_increment_population_sd": float(
            np.std(list(group_v.values()), ddof=0)
        ),
        "visual_increment_minimum": min(group_v.values()),
        "visual_increment_maximum": max(group_v.values()),
        "correct_margin_bits_per_token": mean(group_correct_margin.values()),
        "no_pixel_margin_bits_per_token": mean(group_none_margin.values()),
        "correct_accuracy": mean(
            float(row["correct_is_accurate"]) for row in rows
        ),
        "no_pixel_accuracy": mean(
            float(row["no_pixel_is_accurate"]) for row in rows
        ),
        "accuracy_gain": mean(
            float(row["correct_is_accurate"])
            - float(row["no_pixel_is_accurate"])
            for row in rows
        ),
        "bootstrap": bootstrap,
        "categories": categories,
    }


def category_increment(summary: dict[str, Any], category: str) -> float:
    matches = [
        row
        for row in summary["categories"]
        if row["category"] == category
    ]
    if len(matches) != 1:
        raise ValueError(f"missing or duplicate category summary: {category}")
    return float(matches[0]["mean_visual_increment_bits_per_token"])


def paired_bootstrap_delta(
    m2_rows: list[dict[str, Any]],
    m3_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    m2 = grouped_means(m2_rows, "visual_increment_bits_per_token")
    m3 = grouped_means(m3_rows, "visual_increment_bits_per_token")
    if set(m2) != set(m3):
        raise ValueError("paired models have different image groups")
    differences = np.asarray(
        [m3[key] - m2[key] for key in sorted(m2)],
        dtype=np.float64,
    )
    result = bootstrap_mean(differences)
    return {
        "delta_V_bits_per_token": result.pop("estimate"),
        "bootstrap_unit": (
            "normalized-pixel SHA-256 image group; questions averaged within group"
        ),
        **result,
    }


def pooled_model_bootstrap(
    model_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    by_model = {
        model_id: grouped_means(rows, "visual_increment_bits_per_token")
        for model_id, rows in model_rows.items()
    }
    group_sets = {frozenset(values) for values in by_model.values()}
    if len(group_sets) != 1:
        raise ValueError("models differ in independent image groups")
    groups = sorted(next(iter(group_sets)))
    pooled = [
        mean(by_model[model_id][group] for model_id in sorted(by_model))
        for group in groups
    ]
    result = bootstrap_mean(pooled)
    result["model_count"] = len(by_model)
    result["definition"] = (
        "per image group mean visual increment across the 18 fixed models"
    )
    return result


def preregistered_decision(
    pair_rows: list[dict[str, Any]],
    model_summaries: list[dict[str, Any]],
    pooled: dict[str, Any],
) -> dict[str, Any]:
    if len(pair_rows) != 9 or len(model_summaries) != 18:
        raise ValueError("decision requires nine pairs and eighteen models")
    concordant = sum(row["prediction_concordant"] for row in pair_rows)
    significant = sum(
        row["ci_excludes_zero_in_predicted_direction"]
        for row in pair_rows
    )
    budget_concordance = {
        budget: sum(
            row["prediction_concordant"]
            for row in pair_rows
            if row["budget"] == budget
        )
        for budget in EXPECTED_BUDGETS
    }
    decoupled = [row for row in pair_rows if row["delta_R"] > 0.0]
    decoupled_predicted = sum(
        row["delta_V_bits_per_token"] < 0.0 for row in decoupled
    )
    decoupled_proportion = (
        decoupled_predicted / len(decoupled)
        if decoupled
        else float("nan")
    )
    positive_models = sum(
        summary["mean_visual_increment_bits_per_token"] > 0.0
        for summary in model_summaries
    )
    category_effects = {}
    for category in EXPECTED_CATEGORIES:
        category_effects[category] = mean(
            row["predicted_delta_V_sign"]
            * row["category_delta_V"][category]
            for row in pair_rows
        )
    positive_categories = [
        category
        for category, value in category_effects.items()
        if value > 0.0
    ]

    support_checks = {
        "pooled_95_CI_lower_above_zero": pooled["ci_lower"] > 0.0,
        "at_least_12_of_18_model_V_positive": positive_models >= 12,
        "at_least_7_of_9_sign_concordant": concordant >= 7,
        "at_least_5_predicted_direction_CIs_exclude_zero": significant >= 5,
        "each_budget_at_least_2_of_3_concordant": all(
            value >= 2 for value in budget_concordance.values()
        ),
        "delta_R_positive_pairs_at_least_75_percent_delta_V_negative": (
            bool(decoupled) and decoupled_proportion >= 0.75
        ),
        "at_least_4_of_6_categories_prediction_oriented_positive": (
            len(positive_categories) >= 4
        ),
    }
    rejection_checks = {
        "sign_concordance_at_most_5_of_9": concordant <= 5,
        "any_budget_all_three_opposite": any(
            value == 0 for value in budget_concordance.values()
        ),
        "pooled_V_not_positive_or_fewer_than_9_models_positive": (
            pooled["estimate"] <= 0.0 or positive_models < 9
        ),
        "delta_R_positive_pairs_less_than_50_percent_delta_V_negative": (
            bool(decoupled) and decoupled_proportion < 0.50
        ),
        "at_most_2_of_6_categories_prediction_oriented_positive": (
            len(positive_categories) <= 2
        ),
    }
    if all(support_checks.values()):
        status = "PROMISING"
        rationale = "all preregistered VISCOND support criteria were met"
    elif any(rejection_checks.values()):
        status = "REJECT_IDEA"
        rationale = "at least one preregistered VISCOND rejection criterion was met"
    else:
        status = "INCONCLUSIVE"
        rationale = (
            "neither all support criteria nor any rejection criterion was met"
        )
    return {
        "status": status,
        "rationale": rationale,
        "concordant_pair_count": concordant,
        "predicted_direction_CI_excludes_zero_count": significant,
        "budget_concordance": budget_concordance,
        "positive_model_V_count": positive_models,
        "pooled_visual_increment": pooled,
        "delta_R_positive_pair_count": len(decoupled),
        "delta_R_positive_and_delta_V_negative_count": decoupled_predicted,
        "delta_R_positive_prediction_proportion": decoupled_proportion,
        "prediction_oriented_category_effects": category_effects,
        "positive_prediction_oriented_categories": positive_categories,
        "support_checks": support_checks,
        "rejection_checks": rejection_checks,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("CSV requires nonempty rows")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"analysis output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    matrix_root = args.matrix_root.resolve()
    matrix_state_path = matrix_root / "matrix_state.json"
    matrix_state = json.loads(matrix_state_path.read_text(encoding="utf-8"))
    if (
        matrix_state.get("status") != "complete"
        or len(matrix_state.get("completed", [])) != 18
        or matrix_state.get("scientific_aggregation_performed") is not False
        or matrix_state.get("final_confirmation_accessed") is not False
    ):
        raise ValueError("VISCOND matrix is not complete and aggregation-safe")

    manifest = json.loads(
        args.panel_manifest.resolve().read_text(encoding="utf-8")
    )
    expected_indices = [int(row["index"]) for row in manifest["rows"]]
    if (
        len(expected_indices) < 1_350
        or len(set(expected_indices)) != len(expected_indices)
    ):
        raise ValueError("VISCOND panel manifest indices are invalid")

    model_rows: dict[str, list[dict[str, Any]]] = {}
    model_summaries: dict[str, dict[str, Any]] = {}
    receipts = {}
    input_hash_sets: dict[str, set[str]] = defaultdict(set)
    commits = set()
    for model_id in matrix_state["model_order"]:
        model_dir = matrix_root / "models" / model_id
        receipt_path = model_dir / "run_receipt.json"
        raw_path = model_dir / "item_scores.jsonl"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            receipt.get("status") != "complete"
            or receipt.get("mode") != "full"
            or receipt.get("config_id") != model_id
            or receipt["scoring"]["item_count"] != len(expected_indices)
            or receipt["scoring"]["aggregate_scientific_result_computed"]
            is not False
            or receipt["inputs"]["final_confirmation_accessed"] is not False
            or sha256_file(raw_path)
            != receipt["scoring"]["raw_rows_sha256"]
        ):
            raise ValueError(f"invalid VISCOND receipt/raw rows for {model_id}")
        rows = read_jsonl(raw_path)
        summary = summarize_model_rows(model_id, rows, expected_indices)
        summary.update(
            {
                "method": receipt["method"],
                "budget": receipt["budget"],
                "mapping_root": int(receipt["mapping_root"]),
                "checkpoint_archive_sha256": receipt["checkpoint"][
                    "archive_sha256"
                ],
            }
        )
        model_rows[model_id] = rows
        model_summaries[model_id] = summary
        receipts[model_id] = {
            "path": str(receipt_path),
            "sha256": sha256_file(receipt_path),
            "raw_path": str(raw_path),
            "raw_sha256": sha256_file(raw_path),
        }
        for key in ("panel_manifest", "panel_audit"):
            input_hash_sets[key].add(receipt["inputs"][key]["sha256"])
        commits.add(receipt["git"]["commit"])
    if any(len(values) != 1 for values in input_hash_sets.values()):
        raise ValueError("VISCOND models used different gate inputs")
    if len(commits) != 1:
        raise ValueError("VISCOND models were scored at different git commits")

    development = json.loads(
        args.development_risks.resolve().read_text(encoding="utf-8")
    )
    risk_by_id = {
        row["model_id"]: row for row in development["models"]
    }
    if set(risk_by_id) != set(model_rows):
        raise ValueError("development-risk family differs from VISCOND family")

    paired = []
    for budget in EXPECTED_BUDGETS:
        for root in EXPECTED_ROOTS:
            m2_id = f"M2-{budget}-seed-{root}"
            m3_id = f"M3-{budget}-seed-{root}"
            m2_summary = model_summaries[m2_id]
            m3_summary = model_summaries[m3_id]
            delta_r = (
                float(risk_by_id[m3_id]["empirical_total_semantic_risk"])
                - float(risk_by_id[m2_id]["empirical_total_semantic_risk"])
            )
            if delta_r == 0.0:
                raise ValueError("VISCOND prediction has zero delta_R")
            predicted_sign = -1 if delta_r > 0.0 else 1
            bootstrap = paired_bootstrap_delta(
                model_rows[m2_id], model_rows[m3_id]
            )
            delta_v = bootstrap["delta_V_bits_per_token"]
            observed_sign = (
                1 if delta_v > 0.0 else -1 if delta_v < 0.0 else 0
            )
            ci_predicted = (
                bootstrap["ci_upper"] < 0.0
                if predicted_sign < 0
                else bootstrap["ci_lower"] > 0.0
            )
            category_delta = {
                category: (
                    category_increment(m3_summary, category)
                    - category_increment(m2_summary, category)
                )
                for category in EXPECTED_CATEGORIES
            }
            paired.append(
                {
                    "budget": budget,
                    "mapping_root": root,
                    "m2_model_id": m2_id,
                    "m3_model_id": m3_id,
                    "m2_development_total_semantic_risk": float(
                        risk_by_id[m2_id][
                            "empirical_total_semantic_risk"
                        ]
                    ),
                    "m3_development_total_semantic_risk": float(
                        risk_by_id[m3_id][
                            "empirical_total_semantic_risk"
                        ]
                    ),
                    "delta_R": delta_r,
                    "predicted_delta_V_sign": predicted_sign,
                    **bootstrap,
                    "observed_delta_V_sign": observed_sign,
                    "prediction_concordant": observed_sign
                    == predicted_sign,
                    "ci_excludes_zero_in_predicted_direction": ci_predicted,
                    "category_delta_V": category_delta,
                }
            )

    model_list = [
        model_summaries[model_id]
        for model_id in matrix_state["model_order"]
    ]
    pooled = pooled_model_bootstrap(model_rows)
    decision = preregistered_decision(paired, model_list, pooled)

    model_json_path = output / "model_visual_increment_summary.json"
    pair_json_path = output / "paired_differences.json"
    decision_path = output / "decision.json"
    atomic_write_json(
        model_json_path,
        {
            "schema_version": 1,
            "model_count": 18,
            "models": model_list,
        },
    )
    atomic_write_json(
        pair_json_path,
        {
            "schema_version": 1,
            "pair_count": 9,
            "pairs": paired,
        },
    )
    atomic_write_json(decision_path, decision)
    model_csv_path = output / "model_visual_increment_summary.csv"
    pair_csv_path = output / "paired_differences.csv"
    write_csv(
        model_csv_path,
        [
            {
                key: summary[key]
                for key in (
                    "model_id",
                    "method",
                    "budget",
                    "mapping_root",
                    "mean_visual_increment_bits_per_token",
                    "visual_increment_population_sd",
                    "correct_margin_bits_per_token",
                    "no_pixel_margin_bits_per_token",
                    "correct_accuracy",
                    "no_pixel_accuracy",
                    "accuracy_gain",
                )
            }
            for summary in model_list
        ],
    )
    write_csv(
        pair_csv_path,
        [
            {
                "budget": row["budget"],
                "mapping_root": row["mapping_root"],
                "m2_model_id": row["m2_model_id"],
                "m3_model_id": row["m3_model_id"],
                "delta_R": row["delta_R"],
                "predicted_delta_V_sign": row["predicted_delta_V_sign"],
                "delta_V_bits_per_token": row[
                    "delta_V_bits_per_token"
                ],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "prediction_concordant": row["prediction_concordant"],
                "ci_excludes_zero_in_predicted_direction": row[
                    "ci_excludes_zero_in_predicted_direction"
                ],
            }
            for row in paired
        ],
    )
    receipt = {
        "schema_version": 1,
        "analysis_id": "VISCOND-01-round1-preregistered-decision",
        "status": "complete",
        "decision_status": decision["status"],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED,
            "unit": "normalized-pixel SHA-256 image group",
            "interval": "95% percentile, numpy method=linear",
            "normality_assumption_required": False,
        },
        "inputs": {
            "matrix_state": {
                "path": str(matrix_state_path),
                "sha256": sha256_file(matrix_state_path),
            },
            "panel_manifest": {
                "path": str(args.panel_manifest.resolve()),
                "sha256": sha256_file(args.panel_manifest),
            },
            "development_risks": {
                "path": str(args.development_risks.resolve()),
                "sha256": sha256_file(args.development_risks),
                "role": "pre-existing development-only operational risk ordering",
            },
            "model_runs": receipts,
            "scoring_git_commit": next(iter(commits)),
            "final_confirmation_accessed": False,
        },
        "outputs": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in (
                model_json_path,
                model_csv_path,
                pair_json_path,
                pair_csv_path,
                decision_path,
            )
        },
        "interpretation_scope": (
            "MMStar correct-image relative to no-pixel operational answer-"
            "discrimination increment; not mutual information, formal visual "
            "risk, causal mediation, or a certified generalization bound"
        ),
    }
    atomic_write_json(output / "analysis_receipt.json", receipt)
    print(
        f"status=complete decision={decision['status']} "
        f"pooled_V={pooled['estimate']:.9g} "
        f"positive_models={decision['positive_model_V_count']}/18 "
        f"concordant={decision['concordant_pair_count']}/9 "
        f"ci_predicted={decision['predicted_direction_CI_excludes_zero_count']}/9",
        flush=True,
    )


if __name__ == "__main__":
    main()
