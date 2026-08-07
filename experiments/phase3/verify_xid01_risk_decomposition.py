#!/usr/bin/env python3
"""Exhaustively verify the frozen XID-01 round2 finite-risk decomposition."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


GRID: Tuple[Fraction, ...] = tuple(Fraction(value, 4) for value in range(5))
RADII: Tuple[Fraction, ...] = (Fraction(0), Fraction(1, 4), Fraction(1, 2))
ETAS = (0.05, 0.10, 0.25)
HYPOTHESES = (0, 1, 2)


def minimizers(risks: Sequence[Fraction]) -> Tuple[int, ...]:
    minimum = min(risks)
    return tuple(index for index, risk in enumerate(risks) if risk == minimum)


def near_minimizers(
    source_risks: Sequence[Fraction], epsilon: Fraction
) -> Tuple[int, ...]:
    minimum = min(source_risks)
    return tuple(
        index
        for index, risk in enumerate(source_risks)
        if risk <= minimum + epsilon
    )


def decomposition_terms(
    target_risks: Sequence[Fraction],
    exact_set: Sequence[int],
    expanded_set: Sequence[int],
    target_oracle_risk: Fraction = Fraction(0),
) -> Dict[str, Fraction]:
    best_hypothesis_risk = min(target_risks)
    exact_target = [target_risks[index] for index in exact_set]
    expanded_target = [target_risks[index] for index in expanded_set]
    approximation = best_hypothesis_risk - target_oracle_risk
    alignment = min(exact_target) - best_hypothesis_risk
    identification = max(exact_target) - min(exact_target)
    estimation_expansion = max(expanded_target) - max(exact_target)
    return {
        "approximation": approximation,
        "alignment": alignment,
        "identification": identification,
        "estimation_expansion": estimation_expansion,
        "rhs": (
            approximation
            + alignment
            + identification
            + estimation_expansion
        ),
    }


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def verify_grid() -> Dict[str, object]:
    risk_tables = tuple(itertools.product(GRID, repeat=len(HYPOTHESES)))
    by_radius: List[Dict[str, object]] = []
    total_table_cases = 0
    total_erm_cases = 0
    for radius in RADII:
        table_cases = 0
        erm_cases = 0
        max_slack = Fraction(0)
        valid_source_empirical_pairs = 0
        for source in risk_tables:
            exact_set = near_minimizers(source, Fraction(0))
            expanded_set = near_minimizers(source, 2 * radius)
            for empirical in risk_tables:
                if max(abs(a - b) for a, b in zip(source, empirical)) > radius:
                    continue
                valid_source_empirical_pairs += 1
                empirical_minimizers = minimizers(empirical)
                if not set(empirical_minimizers).issubset(expanded_set):
                    raise AssertionError(
                        "uniform-deviation membership failed: "
                        f"radius={radius}, source={source}, empirical={empirical}, "
                        f"erm={empirical_minimizers}, expanded={expanded_set}"
                    )
                for target in risk_tables:
                    terms = decomposition_terms(
                        target, exact_set, expanded_set, target_oracle_risk=Fraction(0)
                    )
                    if any(value < 0 for key, value in terms.items() if key != "rhs"):
                        raise AssertionError(
                            f"negative term: target={target}, terms={terms}"
                        )
                    expected_rhs = max(target[index] for index in expanded_set)
                    if terms["rhs"] != expected_rhs:
                        raise AssertionError(
                            f"algebra failed: rhs={terms['rhs']} != {expected_rhs}"
                        )
                    for hypothesis in empirical_minimizers:
                        excess = target[hypothesis]
                        if excess > terms["rhs"]:
                            raise AssertionError(
                                "target bound failed: "
                                f"source={source}, empirical={empirical}, "
                                f"target={target}, h={hypothesis}, terms={terms}"
                            )
                        max_slack = max(max_slack, terms["rhs"] - excess)
                        erm_cases += 1
                    table_cases += 1
        by_radius.append(
            {
                "uniform_deviation_radius": fraction_text(radius),
                "near_minimizer_epsilon": fraction_text(2 * radius),
                "valid_source_empirical_pairs": valid_source_empirical_pairs,
                "target_table_cases": table_cases,
                "empirical_erm_cases": erm_cases,
                "max_bound_slack": fraction_text(max_slack),
                "violations": 0,
            }
        )
        total_table_cases += table_cases
        total_erm_cases += erm_cases
    return {
        "hypothesis_count": len(HYPOTHESES),
        "risk_grid": [fraction_text(value) for value in GRID],
        "deviation_radii": [fraction_text(value) for value in RADII],
        "by_radius": by_radius,
        "total_target_table_cases": total_table_cases,
        "total_empirical_erm_cases": total_erm_cases,
        "violations": 0,
    }


def round1_specialization() -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for eta in ETAS:
        correct = -math.log(1.0 - eta)
        wrong = -math.log(eta)
        kappa = wrong - correct
        redundant = {
            "approximation": 0.0,
            "alignment": 0.0,
            "identification": kappa,
            "estimation_expansion": 0.0,
            "rhs": kappa,
        }
        identifying = {
            "approximation": 0.0,
            "alignment": 0.0,
            "identification": 0.0,
            "estimation_expansion": 0.0,
            "rhs": 0.0,
        }
        expected = math.log((1.0 - eta) / eta)
        if not math.isclose(kappa, expected, abs_tol=1e-12):
            raise AssertionError(f"eta={eta}: kappa={kappa} != {expected}")
        results.append(
            {
                "eta": eta,
                "correct_target_nll": correct,
                "wrong_target_nll": wrong,
                "redundant": redundant,
                "identifying": identifying,
                "identifying_source_wrong_rule_excess_nll": 0.25 * kappa,
            }
        )
    return results


def verify() -> Dict[str, object]:
    grid = verify_grid()
    specializations = round1_specialization()
    return {
        "status": "PASS",
        "grid_verification": grid,
        "round1_specialization": specializations,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inference_boundary": (
            "The exhaustive check verifies the finite-risk algebra and ERM membership "
            "under a uniform-deviation event. The terms use target risks and are not "
            "a directly computable LVLM certificate without additional assumptions."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/XID-01_round2/VERIFICATION.json"),
    )
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": result["status"],
                "target_table_cases": result["grid_verification"][
                    "total_target_table_cases"
                ],
                "empirical_erm_cases": result["grid_verification"][
                    "total_empirical_erm_cases"
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
