#!/usr/bin/env python3
"""Deterministically verify the XID-01 finite identifiability proposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable, Tuple


Cell = Tuple[int, str]

REDUNDANT: tuple[Cell, ...] = (
    (0, "a"),
    (1, "b"),
    (0, "c"),
    (1, "a"),
)
IDENTIFYING: tuple[Cell, ...] = (
    (0, "b"),
    (1, "a"),
    (0, "c"),
    (1, "a"),
)
TARGET: Cell = (1, "c")
DIAGNOSTIC: Cell = (0, "b")
INTERACTION_CELLS = frozenset((DIAGNOSTIC, TARGET))
ETAS = (0.05, 0.10, 0.25)


def rule(theta: int, cell: Cell) -> int:
    if theta not in (0, 1):
        raise ValueError(f"theta must be binary, got {theta}")
    return theta if cell in INTERACTION_CELLS else 0


def token_probability(hypothesis: int, cell: Cell, token: int, eta: float) -> float:
    predicted = rule(hypothesis, cell)
    return 1.0 - eta if token == predicted else eta


def nll_risk(
    support: Iterable[Cell], ground_truth: int, hypothesis: int, eta: float
) -> float:
    cells = tuple(support)
    return sum(
        -math.log(
            token_probability(hypothesis, cell, rule(ground_truth, cell), eta)
        )
        for cell in cells
    ) / len(cells)


def marginals(support: Iterable[Cell]) -> dict[str, dict[str, int]]:
    cells = tuple(support)
    return {
        "V": {str(key): value for key, value in sorted(Counter(v for v, _ in cells).items())},
        "L": dict(sorted(Counter(language for _, language in cells).items())),
    }


def argmin_hypotheses(risks: dict[int, float], tolerance: float = 1e-12) -> list[int]:
    minimum = min(risks.values())
    return sorted(
        hypothesis
        for hypothesis, risk in risks.items()
        if risk <= minimum + tolerance
    )


def target_zero_one_error(ground_truth: int, hypothesis: int) -> int:
    return int(rule(ground_truth, TARGET) != rule(hypothesis, TARGET))


def verify() -> dict[str, object]:
    redundant_marginals = marginals(REDUNDANT)
    identifying_marginals = marginals(IDENTIFYING)
    invariants = {
        "sample_count_equal": len(REDUNDANT) == len(IDENTIFYING) == 4,
        "visual_marginals_equal": (
            redundant_marginals["V"] == identifying_marginals["V"] == {"0": 2, "1": 2}
        ),
        "language_marginals_equal": (
            redundant_marginals["L"]
            == identifying_marginals["L"]
            == {"a": 2, "b": 1, "c": 1}
        ),
        "target_absent_redundant": TARGET not in REDUNDANT,
        "target_absent_identifying": TARGET not in IDENTIFYING,
        "target_factor_values_seen_redundant": (
            any(v == TARGET[0] for v, _ in REDUNDANT)
            and any(language == TARGET[1] for _, language in REDUNDANT)
        ),
        "target_factor_values_seen_identifying": (
            any(v == TARGET[0] for v, _ in IDENTIFYING)
            and any(language == TARGET[1] for _, language in IDENTIFYING)
        ),
        "diagnostic_absent_redundant": DIAGNOSTIC not in REDUNDANT,
        "diagnostic_present_identifying": DIAGNOSTIC in IDENTIFYING,
        "shared_parameter_controls_diagnostic_and_target": all(
            rule(1, cell) == 1 and rule(0, cell) == 0
            for cell in (DIAGNOSTIC, TARGET)
        ),
    }
    if not all(invariants.values()):
        raise AssertionError(f"construction invariant failed: {invariants}")

    label_tables = {
        str(theta): {
            "redundant": [rule(theta, cell) for cell in REDUNDANT],
            "identifying": [rule(theta, cell) for cell in IDENTIFYING],
            "target": rule(theta, TARGET),
        }
        for theta in (0, 1)
    }
    if label_tables["0"]["redundant"] != label_tables["1"]["redundant"]:
        raise AssertionError("redundant training worlds are not observationally identical")

    eta_results: list[dict[str, object]] = []
    for eta in ETAS:
        analytic_gap = 0.25 * math.log((1.0 - eta) / eta)
        per_world: dict[str, object] = {}
        for theta in (0, 1):
            redundant_risks = {
                hypothesis: nll_risk(REDUNDANT, theta, hypothesis, eta)
                for hypothesis in (0, 1)
            }
            identifying_risks = {
                hypothesis: nll_risk(IDENTIFYING, theta, hypothesis, eta)
                for hypothesis in (0, 1)
            }
            redundant_minimizers = argmin_hypotheses(redundant_risks)
            identifying_minimizers = argmin_hypotheses(identifying_risks)
            measured_gap = (
                identifying_risks[1 - theta] - identifying_risks[theta]
            )
            target_nlls = {
                hypothesis: nll_risk((TARGET,), theta, hypothesis, eta)
                for hypothesis in (0, 1)
            }
            target_diameter_redundant = abs(target_nlls[1] - target_nlls[0])
            if redundant_minimizers != [0, 1]:
                raise AssertionError(
                    f"eta={eta}, theta={theta}: redundant minimizers "
                    f"{redundant_minimizers}"
                )
            if identifying_minimizers != [theta]:
                raise AssertionError(
                    f"eta={eta}, theta={theta}: identifying minimizers "
                    f"{identifying_minimizers}"
                )
            if not math.isclose(measured_gap, analytic_gap, abs_tol=1e-12):
                raise AssertionError(
                    f"eta={eta}, theta={theta}: measured gap {measured_gap} "
                    f"!= analytic {analytic_gap}"
                )
            if target_zero_one_error(theta, identifying_minimizers[0]) != 0:
                raise AssertionError("identified rule failed on the unseen target")
            expected_diameter = math.log((1.0 - eta) / eta)
            if not math.isclose(
                target_diameter_redundant, expected_diameter, abs_tol=1e-12
            ):
                raise AssertionError(
                    f"target diameter {target_diameter_redundant} "
                    f"!= {expected_diameter}"
                )
            per_world[str(theta)] = {
                "redundant_nll": redundant_risks,
                "identifying_nll": identifying_risks,
                "redundant_exact_minimizers": redundant_minimizers,
                "identifying_exact_minimizers": identifying_minimizers,
                "measured_identifying_gap": measured_gap,
                "target_nll": target_nlls,
                "redundant_target_nll_diameter": target_diameter_redundant,
                "identifying_target_nll_diameter": 0.0,
                "identified_target_zero_one_error": 0,
            }
        eta_results.append(
            {
                "eta": eta,
                "analytic_identifying_gap": analytic_gap,
                "analytic_redundant_target_nll_diameter": math.log(
                    (1.0 - eta) / eta
                ),
                "worlds": per_world,
            }
        )

    # With identical redundant training observations, a randomized learner predicts
    # target token 1 with probability q. Its errors are q in world 0 and 1-q in
    # world 1, so the best possible worst-case error is attained at q=1/2.
    minimax_grid = [
        {
            "q_predict_one": q / 100,
            "world_0_error": q / 100,
            "world_1_error": 1.0 - q / 100,
            "worst_case_error": max(q / 100, 1.0 - q / 100),
        }
        for q in range(101)
    ]
    best_grid = min(minimax_grid, key=lambda row: row["worst_case_error"])
    if best_grid != {
        "q_predict_one": 0.5,
        "world_0_error": 0.5,
        "world_1_error": 0.5,
        "worst_case_error": 0.5,
    }:
        raise AssertionError(f"unexpected minimax result: {best_grid}")

    script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "status": "PASS",
        "construction": {
            "redundant_support": REDUNDANT,
            "identifying_support": IDENTIFYING,
            "target": TARGET,
            "diagnostic": DIAGNOSTIC,
            "redundant_marginals": redundant_marginals,
            "identifying_marginals": identifying_marginals,
        },
        "invariants": invariants,
        "label_tables": label_tables,
        "eta_results": eta_results,
        "redundant_worlds_identical": True,
        "redundant_minimax_target_zero_one_error": best_grid,
        "script_sha256": script_sha,
        "inference_boundary": (
            "This verifies a two-rule finite construction only; it does not establish "
            "neural-LVLM optimization, approximation, or empirical generalization."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/XID-01_round1/VERIFICATION.json"),
    )
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(args.output), "status": result["status"]}))


if __name__ == "__main__":
    main()
