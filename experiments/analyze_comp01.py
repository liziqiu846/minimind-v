#!/usr/bin/env python3
"""One-shot preregistered aggregation and decision for COMP-01 round 1."""

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


BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_807
EXPECTED_BUDGETS = ("low", "current", "high")
EXPECTED_ROOTS = (43101, 43102, 43103)
EXPECTED_FAMILIES = ("horizontal", "vertical", "depth")


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


def summarize_model_rows(
    model_id: str, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(rows) != 410 or len({row["pair_id"] for row in rows}) != 410:
        raise ValueError(f"{model_id} does not have 410 unique pair rows")
    group_counts = Counter(row["group_id"] for row in rows)
    if len(group_counts) != 205 or set(group_counts.values()) != {2}:
        raise ValueError(f"{model_id} does not preserve 205 two-pair clusters")
    family_counts = Counter(row["relation_family"] for row in rows)
    if family_counts != Counter(
        {"horizontal": 205, "vertical": 103, "depth": 102}
    ):
        raise ValueError(f"{model_id} relation-family counts differ")
    dataset_counts = Counter(row["dataset_id"] for row in rows)
    if dataset_counts != Counter(
        {"controlled_images": 206, "controlled_clevr": 204}
    ):
        raise ValueError(f"{model_id} dataset pair counts differ")
    if any(row.get("all_scores_finite") is not True for row in rows):
        raise ValueError(f"{model_id} contains a non-finite score row")

    margins = [float(row["binding_margin_bits_per_token"]) for row in rows]
    image_correct = [
        bool(row[key])
        for row in rows
        for key in ("image_0_correct", "image_1_correct")
    ]

    def subset(field: str, value: str) -> dict[str, Any]:
        selected = [row for row in rows if row[field] == value]
        selected_margins = [
            float(row["binding_margin_bits_per_token"])
            for row in selected
        ]
        return {
            "name": value,
            "pair_count": len(selected),
            "mean_binding_margin_bits_per_token": mean(selected_margins),
            "group_accuracy": mean(
                float(row["group_correct"]) for row in selected
            ),
            "image_accuracy": mean(
                float(row[key])
                for row in selected
                for key in ("image_0_correct", "image_1_correct")
            ),
        }

    return {
        "model_id": model_id,
        "pair_count": len(rows),
        "official_object_group_count": len(group_counts),
        "image_count": 2 * len(rows),
        "mean_binding_margin_bits_per_token": mean(margins),
        "binding_margin_population_sd": float(np.std(margins, ddof=0)),
        "binding_margin_minimum": min(margins),
        "binding_margin_maximum": max(margins),
        "group_accuracy": mean(
            float(row["group_correct"]) for row in rows
        ),
        "image_accuracy": mean(float(value) for value in image_correct),
        "relation_families": [
            subset("relation_family", family)
            for family in EXPECTED_FAMILIES
        ],
        "datasets": [
            subset("dataset_id", dataset)
            for dataset in ("controlled_images", "controlled_clevr")
        ],
    }


def cluster_bootstrap_delta(
    m2_rows: list[dict[str, Any]],
    m3_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    m2 = {row["pair_id"]: row for row in m2_rows}
    m3 = {row["pair_id"]: row for row in m3_rows}
    if set(m2) != set(m3) or len(m2) != 410:
        raise ValueError("paired models do not have identical pair IDs")
    by_group: dict[str, list[float]] = defaultdict(list)
    pair_differences = []
    for pair_id in sorted(m2):
        if m2[pair_id]["group_id"] != m3[pair_id]["group_id"]:
            raise ValueError("paired models disagree on official group ID")
        difference = (
            float(m3[pair_id]["binding_margin_bits_per_token"])
            - float(m2[pair_id]["binding_margin_bits_per_token"])
        )
        pair_differences.append(difference)
        by_group[m2[pair_id]["group_id"]].append(difference)
    if len(by_group) != 205 or {
        len(values) for values in by_group.values()
    } != {2}:
        raise ValueError("bootstrap clusters are not 205 two-pair groups")
    cluster_means = np.asarray(
        [mean(by_group[key]) for key in sorted(by_group)],
        dtype=np.float64,
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    indices = rng.integers(
        0,
        len(cluster_means),
        size=(BOOTSTRAP_REPLICATES, len(cluster_means)),
    )
    replicates = cluster_means[indices].mean(axis=1, dtype=np.float64)
    lower, upper = np.quantile(
        replicates, [0.025, 0.975], method="linear"
    )
    estimate = mean(pair_differences)
    if not math.isclose(
        estimate, float(cluster_means.mean()), rel_tol=0.0, abs_tol=1e-15
    ):
        raise ArithmeticError("pair and equal-cluster estimates differ")
    return {
        "delta_G_bits_per_token": estimate,
        "bootstrap_unit": "official four-image object group; both relation-pair deltas averaged within cluster",
        "cluster_count": len(cluster_means),
        "pairs_per_cluster": 2,
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
        "percentile_method": "numpy.quantile method=linear",
        "confidence_level": 0.95,
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "bootstrap_standard_deviation": float(
            np.std(replicates, ddof=1)
        ),
    }


def subset_margin(
    summary: dict[str, Any], section: str, name: str
) -> float:
    matches = [
        row
        for row in summary[section]
        if row["name"] == name
    ]
    if len(matches) != 1:
        raise ValueError(f"missing/duplicate summary subset: {section}/{name}")
    return float(matches[0]["mean_binding_margin_bits_per_token"])


def preregistered_decision(pair_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(pair_rows) != 9:
        raise ValueError("decision requires exactly nine M2/M3 pairs")
    concordant = sum(row["prediction_concordant"] for row in pair_rows)
    significant_predicted = sum(
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
        row["delta_G_bits_per_token"] < 0.0 for row in decoupled
    )
    decoupled_proportion = (
        decoupled_predicted / len(decoupled)
        if decoupled
        else float("nan")
    )

    family_oriented = {}
    for family in EXPECTED_FAMILIES:
        effects = []
        for row in pair_rows:
            delta_family = row["relation_family_delta_G"][family]
            effects.append(row["predicted_delta_G_sign"] * delta_family)
        family_oriented[family] = mean(effects)
    positive_families = [
        family
        for family, effect in family_oriented.items()
        if effect > 0.0
    ]

    support_checks = {
        "at_least_7_of_9_sign_concordant": concordant >= 7,
        "at_least_5_predicted_direction_CIs_exclude_zero": (
            significant_predicted >= 5
        ),
        "each_budget_at_least_2_of_3_concordant": all(
            value >= 2 for value in budget_concordance.values()
        ),
        "delta_R_positive_pairs_at_least_75_percent_delta_G_negative": (
            bool(decoupled) and decoupled_proportion >= 0.75
        ),
        "at_least_two_relation_families_have_positive_prediction_oriented_effect": (
            len(positive_families) >= 2
        ),
    }
    rejection_checks = {
        "sign_concordance_at_most_5_of_9": concordant <= 5,
        "any_budget_all_three_opposite": any(
            value == 0 for value in budget_concordance.values()
        ),
        "all_models_near_zero_random_no_direction": False,
        "direction_driven_by_at_most_one_relation_family": (
            len(positive_families) <= 1
        ),
        "delta_R_positive_pairs_less_than_50_percent_delta_G_negative": (
            bool(decoupled) and decoupled_proportion < 0.50
        ),
    }
    if all(support_checks.values()):
        status = "PROMISING"
        rationale = "all five preregistered support criteria were met"
    elif any(rejection_checks.values()):
        status = "REJECT_IDEA"
        rationale = "at least one preregistered rejection criterion was met"
    else:
        status = "INCONCLUSIVE"
        rationale = (
            "neither all support criteria nor any operationalized rejection "
            "criterion was met"
        )
    return {
        "status": status,
        "rationale": rationale,
        "concordant_pair_count": concordant,
        "predicted_direction_CI_excludes_zero_count": significant_predicted,
        "budget_concordance": budget_concordance,
        "delta_R_positive_pair_count": len(decoupled),
        "delta_R_positive_and_delta_G_negative_count": decoupled_predicted,
        "delta_R_positive_prediction_proportion": decoupled_proportion,
        "prediction_oriented_relation_family_effects": family_oriented,
        "positive_prediction_oriented_relation_families": positive_families,
        "support_checks": support_checks,
        "rejection_checks": rejection_checks,
        "nonoperationalized_clause": {
            "clause": "all models G near zero / group accuracy near random and no direction",
            "reason": (
                "the immutable plan supplied no numerical near-zero/random "
                "tolerance; this clause is reported descriptively and cannot be "
                "activated post hoc"
            ),
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("CSV requires nonempty rows")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
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
        raise ValueError("matrix is not complete and aggregation-safe")

    panel = json.loads(args.panel_manifest.read_text(encoding="utf-8"))
    expected_pair_ids = [row["pair_id"] for row in panel["pairs"]]
    if (
        len(expected_pair_ids) != 410
        or len(set(expected_pair_ids)) != 410
    ):
        raise ValueError("panel manifest pair IDs are invalid")

    model_rows = {}
    model_summaries = {}
    receipts = {}
    input_hash_sets: dict[str, set[str]] = defaultdict(set)
    commits = set()
    for model_id in matrix_state["model_order"]:
        model_dir = matrix_root / "models" / model_id
        receipt_path = model_dir / "run_receipt.json"
        raw_path = model_dir / "pair_scores.jsonl"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            receipt.get("status") != "complete"
            or receipt.get("mode") != "full"
            or receipt.get("config_id") != model_id
            or receipt["scoring"]["pair_count"] != 410
            or receipt["scoring"]["aggregate_scientific_result_computed"]
            is not False
            or receipt["inputs"]["final_confirmation_accessed"] is not False
            or sha256_file(raw_path)
            != receipt["scoring"]["raw_rows_sha256"]
        ):
            raise ValueError(f"invalid scoring receipt/raw rows for {model_id}")
        rows = read_jsonl(raw_path)
        if [row["pair_id"] for row in rows] != expected_pair_ids:
            raise ValueError(f"{model_id} pair order differs from panel manifest")
        summary = summarize_model_rows(model_id, rows)
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
        for key in (
            "panel_manifest",
            "panel_audit",
            "collision_diagnostic",
        ):
            input_hash_sets[key].add(receipt["inputs"][key]["sha256"])
        commits.add(receipt["git"]["commit"])
    if any(len(values) != 1 for values in input_hash_sets.values()):
        raise ValueError("models were scored from different gate inputs")
    if len(commits) != 1:
        raise ValueError("models were scored at different git commits")

    development = json.loads(
        args.development_risks.read_text(encoding="utf-8")
    )
    risk_by_id = {
        row["model_id"]: row for row in development["models"]
    }
    if set(risk_by_id) != set(model_rows):
        raise ValueError("development-risk model family differs from scoring family")

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
                raise ValueError("preregistered prediction has zero delta_R")
            predicted_sign = -1 if delta_r > 0.0 else 1
            bootstrap = cluster_bootstrap_delta(
                model_rows[m2_id], model_rows[m3_id]
            )
            delta_g = bootstrap["delta_G_bits_per_token"]
            observed_sign = 1 if delta_g > 0.0 else -1 if delta_g < 0.0 else 0
            ci_predicted = (
                bootstrap["ci_upper"] < 0.0
                if predicted_sign < 0
                else bootstrap["ci_lower"] > 0.0
            )
            family_delta = {
                family: (
                    subset_margin(
                        m3_summary, "relation_families", family
                    )
                    - subset_margin(
                        m2_summary, "relation_families", family
                    )
                )
                for family in EXPECTED_FAMILIES
            }
            dataset_delta = {
                dataset: (
                    subset_margin(m3_summary, "datasets", dataset)
                    - subset_margin(m2_summary, "datasets", dataset)
                )
                for dataset in ("controlled_images", "controlled_clevr")
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
                    "predicted_delta_G_sign": predicted_sign,
                    **bootstrap,
                    "observed_delta_G_sign": observed_sign,
                    "prediction_concordant": observed_sign == predicted_sign,
                    "ci_excludes_zero_in_predicted_direction": ci_predicted,
                    "relation_family_delta_G": family_delta,
                    "dataset_delta_G": dataset_delta,
                }
            )

    decision = preregistered_decision(paired)
    model_list = [
        model_summaries[model_id]
        for model_id in matrix_state["model_order"]
    ]
    model_json_path = output / "model_binding_summary.json"
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
    write_csv(
        output / "model_binding_summary.csv",
        [
            {
                key: summary[key]
                for key in (
                    "model_id",
                    "method",
                    "budget",
                    "mapping_root",
                    "mean_binding_margin_bits_per_token",
                    "binding_margin_population_sd",
                    "group_accuracy",
                    "image_accuracy",
                )
            }
            for summary in model_list
        ],
    )
    write_csv(
        output / "paired_differences.csv",
        [
            {
                "budget": row["budget"],
                "mapping_root": row["mapping_root"],
                "m2_model_id": row["m2_model_id"],
                "m3_model_id": row["m3_model_id"],
                "delta_R": row["delta_R"],
                "predicted_delta_G_sign": row["predicted_delta_G_sign"],
                "delta_G_bits_per_token": row[
                    "delta_G_bits_per_token"
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
        "analysis_id": "COMP-01-round1-preregistered-decision",
        "status": "complete",
        "decision_status": decision["status"],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED,
            "unit": "205 official object groups, two pair deltas averaged within group",
            "interval": "95% percentile, numpy method=linear",
            "normality_assumption_required": False,
        },
        "multiplicity": (
            "No post-hoc subset selection or separate discovery claim; all nine "
            "predeclared CIs enter the frozen count-based decision rule."
        ),
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
                output / "model_binding_summary.csv",
                pair_json_path,
                output / "paired_differences.csv",
                decision_path,
            )
        },
        "interpretation_scope": (
            "external operational composition-binding margin; not mutual "
            "information, formal visual risk, or a certified generalization bound"
        ),
    }
    atomic_write_json(output / "analysis_receipt.json", receipt)
    print(
        f"status=complete decision={decision['status']} "
        f"concordant={decision['concordant_pair_count']}/9 "
        f"ci_predicted={decision['predicted_direction_CI_excludes_zero_count']}/9",
        flush=True,
    )


if __name__ == "__main__":
    main()
