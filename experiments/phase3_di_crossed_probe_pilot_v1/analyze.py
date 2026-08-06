#!/usr/bin/env python3
"""Analyze crossed probe stability without performance outcomes."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

from .common import sha256_file, write_json


def _icc_a1(matrix: np.ndarray) -> float:
    """McGraw-Wong ICC(A,1): two-way random, absolute agreement, single panel."""
    n, k = matrix.shape
    grand = matrix.mean()
    row_means = matrix.mean(axis=1)
    column_means = matrix.mean(axis=0)
    ms_rows = k * np.sum((row_means - grand) ** 2) / (n - 1)
    ms_columns = n * np.sum((column_means - grand) ** 2) / (k - 1)
    residual = (
        matrix - row_means[:, None] - column_means[None, :] + grand
    )
    ms_error = np.sum(residual ** 2) / ((n - 1) * (k - 1))
    return float(
        (ms_rows - ms_error)
        / (
            ms_rows
            + (k - 1) * ms_error
            + k * (ms_columns - ms_error) / n
        )
    )


def _read(manifest: dict, run_root: Path) -> list[dict]:
    rows = []
    expected_assignment = manifest["probe_assignment_sha256"]
    for model in manifest["models"]:
        root = run_root / model["config_id"]
        receipt = json.loads((root / "receipt.json").read_text())
        if (
            receipt["status"] != "complete"
            or receipt["probe_assignment_sha256"] != expected_assignment
            or receipt["row_count"] != 99
        ):
            raise ValueError("run receipt identity mismatch")
        with (root / "per_probe_results.csv").open() as handle:
            for row in csv.DictReader(handle):
                for key in ("model_seed", "panel_id", "probe_seed", "probe_slot"):
                    row[key] = int(row[key])
                for key in (
                    "squared_l2_gradient_difference",
                    "log10_squared_l2_gradient_difference",
                    "normalized_gradient_difference",
                ):
                    row[key] = float(row[key])
                rows.append(row)
    if len(rows) != 594:
        raise ValueError("combined pilot row count is not 594")
    return rows


def _identity_audit(rows: list[dict], manifest: dict) -> dict:
    fields = (
        "probe_seed",
        "train_group_id",
        "train_image_sha256",
        "train_conversation_sha256",
        "ghost_group_id",
        "ghost_image_sha256",
        "ghost_conversation_sha256",
        "selected_position",
    )
    failures = []
    for panel in range(3):
        for slot in range(33):
            members = [
                row for row in rows
                if row["panel_id"] == panel and row["probe_slot"] == slot
            ]
            for field in fields:
                if len({str(row[field]) for row in members}) != 1:
                    failures.append({"panel": panel, "slot": slot, "field": field})
    return {
        "status": "PASS" if not failures else "FAIL",
        "checked_panel_slots": 99,
        "checked_models_per_slot": 6,
        "fields": list(fields),
        "failures": failures,
        "manifest_identity_status": manifest["identity_audit"]["status"],
    }


def analyze(manifest_path: Path, run_root: Path, output_root: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    rows = _read(manifest, run_root)
    identity = _identity_audit(rows, manifest)
    if identity["status"] != "PASS":
        raise RuntimeError("post-run shared-probe identity audit failed")
    rng = np.random.default_rng(94017)
    metric_names = {
        "raw": "squared_l2_gradient_difference",
        "log": "log10_squared_l2_gradient_difference",
    }
    lookup = {
        (row["structure"], row["model_seed"], row["panel_id"], row["probe_slot"]): row
        for row in rows
    }

    paired = []
    directions_by_seed = {}
    for seed in (43101, 43102, 43103):
        directions = []
        for panel in range(3):
            p = np.array([
                lookup[("P", seed, panel, slot)][metric_names["raw"]]
                for slot in range(33)
            ])
            s = np.array([
                lookup[("S", seed, panel, slot)][metric_names["raw"]]
                for slot in range(33)
            ])
            difference = float(p.mean() - s.mean())
            direction = "P>S" if difference > 0 else "P<S" if difference < 0 else "tie"
            directions.append(direction)
            paired.append({
                "model_seed": seed,
                "panel_id": panel,
                "P_mean_raw": float(p.mean()),
                "S_mean_raw": float(s.mean()),
                "P_minus_S_raw": difference,
                "direction": direction,
            })
        directions_by_seed[str(seed)] = {
            "directions": directions,
            "consistent": len(set(directions)) == 1,
            "ranking_flip_across_panels": len(set(directions)) > 1,
        }

    panel_calibration = {}
    for T in (11, 22, 33):
        panel_calibration[str(T)] = {}
        for scale, metric in metric_names.items():
            values = np.empty((3, 2, 3))
            for seed_index, seed in enumerate((43101, 43102, 43103)):
                for structure_index, structure in enumerate(("P", "S")):
                    for panel in range(3):
                        values[seed_index, structure_index, panel] = np.mean([
                            lookup[(structure, seed, panel, slot)][metric]
                            for slot in range(T)
                        ])
            panel_calibration[str(T)][scale] = {}
            for K in (1, 2, 3):
                draws = rng.integers(0, 3, size=(30000, K))
                sampled = values[:, :, draws].mean(axis=3)
                pair_mean = sampled.mean(axis=1)
                probe_sd = math.sqrt(float(np.mean(np.var(
                    pair_mean, axis=1, ddof=1
                ))))
                structure_rms = math.sqrt(float(np.mean(
                    (sampled[:, 0, :] - sampled[:, 1, :]) ** 2
                )))
                panel_calibration[str(T)][scale][str(K)] = {
                    "probe_induced_variation": probe_sd,
                    "structure_variation": structure_rms,
                    "ratio": probe_sd / structure_rms,
                    "definition": (
                        "probe=sqrt(mean_model_seed(var_bootstrap_panel_average("
                        "pair_mean(P,S)))); structure=sqrt(mean_seed_draw("
                        "(P_panel_average-S_panel_average)^2))"
                    ),
                }

    step_stability = {}
    concentration = {}
    for T in (11, 22, 33):
        stability_rows = []
        concentration_rows = []
        for panel in range(3):
            for seed in (43101, 43102, 43103):
                p = np.array([
                    lookup[("P", seed, panel, slot)][metric_names["raw"]]
                    for slot in range(T)
                ])
                s = np.array([
                    lookup[("S", seed, panel, slot)][metric_names["raw"]]
                    for slot in range(T)
                ])
                indices = rng.integers(0, T, size=(30000, T))
                for structure, values in (("P", p), ("S", s)):
                    means = values[indices].mean(axis=1)
                    stability_rows.append({
                        "panel_id": panel,
                        "model_seed": seed,
                        "structure": structure,
                        "aggregate_mean": float(values.mean()),
                        "bootstrap_cv": float(means.std(ddof=1) / means.mean()),
                    })
                    ordered = np.sort(values)
                    concentration_rows.append({
                        "panel_id": panel,
                        "model_seed": seed,
                        "structure": structure,
                        "max_share": float(ordered[-1] / ordered.sum()),
                        "top3_share": float(ordered[-3:].sum() / ordered.sum()),
                    })
                differences = (p - s)[indices].mean(axis=1)
                observed = np.sign(np.mean(p - s))
                stability_rows.append({
                    "panel_id": panel,
                    "model_seed": seed,
                    "structure": "paired_P_minus_S",
                    "aggregate_mean": float(np.mean(p - s)),
                    "bootstrap_sign_retention": float(
                        np.mean(np.sign(differences) == observed)
                    ),
                    "bootstrap_p05": float(np.quantile(differences, 0.05)),
                    "bootstrap_p95": float(np.quantile(differences, 0.95)),
                })
        model_rows = [row for row in stability_rows if row["structure"] != "paired_P_minus_S"]
        pair_rows = [row for row in stability_rows if row["structure"] == "paired_P_minus_S"]
        step_stability[str(T)] = {
            "rows": stability_rows,
            "bootstrap_cv_range": [
                min(row["bootstrap_cv"] for row in model_rows),
                max(row["bootstrap_cv"] for row in model_rows),
            ],
            "paired_sign_retention_range": [
                min(row["bootstrap_sign_retention"] for row in pair_rows),
                max(row["bootstrap_sign_retention"] for row in pair_rows),
            ],
        }
        concentration[str(T)] = {
            "rows": concentration_rows,
            "max_share_range": [
                min(row["max_share"] for row in concentration_rows),
                max(row["max_share"] for row in concentration_rows),
            ],
            "top3_share_range": [
                min(row["top3_share"] for row in concentration_rows),
                max(row["top3_share"] for row in concentration_rows),
            ],
        }

    crossed = {}
    for scale, metric in metric_names.items():
        matrix = np.empty((6, 3))
        model_order = []
        index = 0
        for structure in ("P", "S"):
            for seed in (43101, 43102, 43103):
                model_order.append(f"{structure}-{seed}")
                for panel in range(3):
                    matrix[index, panel] = np.mean([
                        lookup[(structure, seed, panel, slot)][metric]
                        for slot in range(33)
                    ])
                index += 1
        pairwise = []
        for left, right in itertools.combinations(range(3), 2):
            pairwise.append({
                "panels": [left, right],
                "pearson": float(pearsonr(matrix[:, left], matrix[:, right]).statistic),
                "spearman": float(spearmanr(matrix[:, left], matrix[:, right]).statistic),
            })
        crossed[scale] = {
            "icc_a1": _icc_a1(matrix),
            "icc_definition": (
                "McGraw-Wong ICC(A,1), two-way random-effects absolute agreement, "
                "single panel; targets=six raw checkpoints, raters=three panels"
            ),
            "pairwise_panel_correlations": pairwise,
            "model_order": model_order,
            "panel_aggregate_matrix": matrix.tolist(),
        }

    thresholds = manifest["decision_thresholds_frozen_before_results"]
    candidates = []
    for K in (1, 2, 3):
        for T in (11, 22, 33):
            ratio_ok = all(
                panel_calibration[str(T)][scale][str(K)]["ratio"]
                <= thresholds["probe_to_structure_ratio_raw_and_log_at_most"]
                for scale in ("raw", "log")
            )
            cv_ok = (
                step_stability[str(T)]["bootstrap_cv_range"][1]
                <= thresholds["bootstrap_aggregate_cv_at_most"]
            )
            sign_ok = (
                step_stability[str(T)]["paired_sign_retention_range"][0]
                >= thresholds["paired_sign_retention_at_least"]
            )
            concentration_ok = (
                concentration[str(T)]["max_share_range"][1]
                <= thresholds["maximum_single_probe_share_at_most"]
                and concentration[str(T)]["top3_share_range"][1]
                <= thresholds["top3_probe_share_at_most"]
            )
            direction_ok = all(
                row["consistent"] for row in directions_by_seed.values()
            )
            candidates.append({
                "K": K,
                "T": T,
                "ratio_pass": ratio_ok,
                "cv_pass": cv_ok,
                "sign_retention_pass": sign_ok,
                "concentration_pass": concentration_ok,
                "panel_direction_pass": direction_ok,
                "all_pass": all((
                    ratio_ok, cv_ok, sign_ok, concentration_ok, direction_ok
                )),
            })
    passing = [row for row in candidates if row["all_pass"]]
    recommendation = (
        min(passing, key=lambda row: (row["K"] * row["T"], row["K"], row["T"]))
        if passing else None
    )
    status = (
        "READY_TO_FREEZE_FORMAL_RESCUE"
        if recommendation is not None
        else "DI_MEASUREMENT_STILL_UNSTABLE"
    )
    result = {
        "schema_version": 1,
        "status": status,
        "role": manifest["role"],
        "pilot_manifest_sha256": sha256_file(manifest_path),
        "identity_audit": identity,
        "paired_structure_differences": paired,
        "directions_by_model_seed": directions_by_seed,
        "panel_calibration": panel_calibration,
        "step_stability": step_stability,
        "contribution_concentration": concentration,
        "crossed_stability": crossed,
        "decision_thresholds": thresholds,
        "candidate_decisions": candidates,
        "formal_recommendation": recommendation,
        "trajectory_T_limitation": (
            "fixed-checkpoint probes calibrate atom sampling only; they do not "
            "measure additional variance from changing W_t along an SGD trajectory"
        ),
        "held_out_performance_correlation_computed": False,
        "final_confirmation_accessed": False,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    write_json(output_root / "stability_summary.json", result)
    combined_path = output_root / "per_probe_results.csv"
    fieldnames = list(rows[0])
    with combined_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        analyze(args.manifest, args.run_root, args.output_root),
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
