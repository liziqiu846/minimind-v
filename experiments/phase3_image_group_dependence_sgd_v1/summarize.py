#!/usr/bin/env python3
"""Compute preregistered correlations and four mechanical decisions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

from .common import sha256_file, write_json_atomic
from .configs import generate_matrix


def _corr(x, y) -> dict:
    return {
        "spearman": float(spearmanr(x, y).statistic),
        "pearson": float(pearsonr(x, y).statistic),
    }


def summarize(results_root: Path) -> dict:
    rows = []
    for config in generate_matrix():
        root = results_root / config["config_id"]
        training_path = root / "training_manifest.json"
        development_path = root / "development" / "development_result.json"
        training = json.loads(training_path.read_text())
        development = json.loads(development_path.read_text())
        row = {
            "structure": config["structure"],
            "budget": config["budget"],
            "seed": config["seed"],
            "empirical_risk": training["empirical_risk"],
            "actual_mms2_bits": training["actual_mms2_bits"],
            "D_I": training["D_I"],
            "diagnosis_step_count": training["diagnosis_step_count"],
            "new_image_development_real_visual_performance": development[
                "new_image_development_real_visual_performance"
            ],
            "error": development["error_oriented_metric"],
            "checkpoint_sha256": training["checkpoint"]["sha256"],
            "MMS2_sha256": training["MMS2"]["sha256"],
            "manifest_sha256": sha256_file(training_path),
            "diagnosis_sha256": training["diagnosis"]["sha256"],
        }
        rows.append(row)
    di = _corr([row["D_I"] for row in rows], [row["error"] for row in rows])
    complexity = _corr(
        [row["actual_mms2_bits"] for row in rows], [row["error"] for row in rows]
    )
    by_budget = {}
    for budget in (2048, 8192):
        selected = [row for row in rows if row["budget"] == budget]
        by_budget[str(budget)] = _corr(
            [row["D_I"] for row in selected], [row["error"] for row in selected]
        )
    decoupling = []
    for budget in (2048, 8192):
        for seed in (43101, 43102, 43103):
            pair = [row for row in rows if row["budget"] == budget and row["seed"] == seed]
            p = next(row for row in pair if row["structure"] == "P")
            s = next(row for row in pair if row["structure"] == "S")
            if s["actual_mms2_bits"] < p["actual_mms2_bits"] and (
                s["new_image_development_real_visual_performance"]
                <= p["new_image_development_real_visual_performance"]
            ):
                worse = s if s["error"] > p["error"] else p
                better = p if worse is s else s
                decoupling.append({
                    "budget": budget, "seed": seed,
                    "worse_structure": worse["structure"],
                    "correct_D_I_prediction": worse["D_I"] > better["D_I"],
                })
    k = len(decoupling)
    correct = sum(row["correct_D_I_prediction"] for row in decoupling)
    criterion = {
        "1": di["spearman"] >= 0.5,
        "2": abs(di["spearman"]) > abs(complexity["spearman"]),
        "3": k >= 3 and correct / k >= 5 / 6,
        "4": (
            np.isfinite(by_budget["2048"]["spearman"])
            and np.isfinite(by_budget["8192"]["spearman"])
            and by_budget["2048"]["spearman"] != 0
            and np.sign(by_budget["2048"]["spearman"])
            == np.sign(by_budget["8192"]["spearman"])
        ),
    }
    output = {
        "status": "complete",
        "model_count": len(rows),
        "D_I_vs_error": di,
        "complexity_vs_error": complexity,
        "by_budget_D_I_vs_error": by_budget,
        "decoupling_pair_count_K": k,
        "decoupling_correct_count": correct,
        "decoupling_correct_rate": correct / k if k else None,
        "decoupling_pairs": decoupling,
        "criteria": {
            key: {"status": "PASS" if value else "FAIL"} for key, value in criterion.items()
        },
        "rows": rows,
    }
    write_json_atomic(results_root / "summary.json", output)
    with (results_root / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.results_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
