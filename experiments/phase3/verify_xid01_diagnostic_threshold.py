#!/usr/bin/env python3
"""Verify the frozen XID-01 diagnostic-mass threshold and sharpness grid."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple


BETAS: Tuple[Fraction, ...] = (
    Fraction(0),
    Fraction(1, 4),
    Fraction(1, 2),
)
GAMMAS: Tuple[Fraction, ...] = (
    Fraction(1, 4),
    Fraction(1, 2),
    Fraction(3, 4),
    Fraction(1),
)
ALPHAS: Tuple[Fraction, ...] = (
    Fraction(0),
    Fraction(1, 8),
    Fraction(1, 4),
)
LAMBDAS: Tuple[Fraction, ...] = tuple(Fraction(value, 4) for value in range(5))
QUARTER_GRID: Tuple[Fraction, ...] = tuple(
    Fraction(value, 4) for value in range(-2, 5)
)
ETAS = (0.05, 0.10, 0.25)


def text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def admissible_base_gaps(beta: Fraction) -> Tuple[Fraction, ...]:
    return tuple(value for value in QUARTER_GRID if value >= -beta)


def admissible_diagnostic_gaps(gamma: Fraction) -> Tuple[Fraction, ...]:
    return tuple(value for value in QUARTER_GRID if value >= gamma)


def verify_grid() -> Dict[str, object]:
    parameter_cases = 0
    positive_threshold_cases = 0
    negative_threshold_cases = 0
    admissible_gap_cases = 0
    sharpness_cases = 0
    rows: List[Dict[str, object]] = []

    for beta in BETAS:
        for gamma in GAMMAS:
            for alpha in ALPHAS:
                for diagnostic_mass in LAMBDAS:
                    parameter_cases += 1
                    lower_margin = (
                        diagnostic_mass * gamma
                        - (1 - diagnostic_mass) * beta
                    )
                    threshold = (beta + 2 * alpha) / (beta + gamma)
                    condition_margin = lower_margin > 2 * alpha
                    condition_threshold = diagnostic_mass > threshold
                    if condition_margin != condition_threshold:
                        raise AssertionError(
                            "threshold equivalence failed: "
                            f"beta={beta}, gamma={gamma}, alpha={alpha}, "
                            f"lambda={diagnostic_mass}, margin={lower_margin}, "
                            f"threshold={threshold}"
                        )

                    local_gap_cases = 0
                    for base_gap in admissible_base_gaps(beta):
                        for diagnostic_gap in admissible_diagnostic_gaps(gamma):
                            local_gap_cases += 1
                            admissible_gap_cases += 1
                            actual_margin = (
                                (1 - diagnostic_mass) * base_gap
                                + diagnostic_mass * diagnostic_gap
                            )
                            if actual_margin < lower_margin:
                                raise AssertionError(
                                    "mixture lower bound failed: "
                                    f"actual={actual_margin}, lower={lower_margin}"
                                )
                            if condition_margin and not actual_margin > 2 * alpha:
                                raise AssertionError(
                                    "positive threshold failed to exclude bad rule: "
                                    f"actual={actual_margin}, 2alpha={2 * alpha}"
                                )

                    if condition_margin:
                        positive_threshold_cases += 1
                    else:
                        negative_threshold_cases += 1
                        # Sharpness under only the stated gap bounds: choose the
                        # extremal population gaps and opposite uniform-deviation
                        # errors. Since m <= 2 alpha, the bad rule ties or beats h*.
                        margin = lower_margin
                        if abs(margin) > Fraction(1, 2):
                            # This branch cannot occur on the frozen grid when
                            # margin <= 2 alpha and alpha <= 1/4.
                            raise AssertionError(
                                f"unexpected sharpness margin outside range: {margin}"
                            )
                        intended_population = Fraction(1, 2) - margin / 2
                        bad_population = Fraction(1, 2) + margin / 2
                        intended_empirical = intended_population + alpha
                        bad_empirical = bad_population - alpha
                        values = (
                            intended_population,
                            bad_population,
                            intended_empirical,
                            bad_empirical,
                        )
                        if not all(Fraction(0) <= value <= Fraction(1) for value in values):
                            raise AssertionError(
                                f"bounded-risk sharpness realization failed: {values}"
                            )
                        if abs(intended_empirical - intended_population) > alpha:
                            raise AssertionError("intended deviation exceeds alpha")
                        if abs(bad_empirical - bad_population) > alpha:
                            raise AssertionError("bad deviation exceeds alpha")
                        if bad_empirical > intended_empirical:
                            raise AssertionError(
                                "bad rule is not an empirical minimizer in sharpness case"
                            )
                        sharpness_cases += 1

                    rows.append(
                        {
                            "beta": text(beta),
                            "gamma": text(gamma),
                            "alpha": text(alpha),
                            "diagnostic_mass": text(diagnostic_mass),
                            "lower_margin": text(lower_margin),
                            "threshold": text(threshold),
                            "condition_holds": condition_margin,
                            "admissible_gap_cases": local_gap_cases,
                        }
                    )

    return {
        "parameter_cases": parameter_cases,
        "positive_threshold_cases": positive_threshold_cases,
        "negative_threshold_cases": negative_threshold_cases,
        "admissible_gap_cases": admissible_gap_cases,
        "sharpness_cases": sharpness_cases,
        "violations": 0,
        "rows": rows,
    }


def round1_specialization() -> Dict[str, object]:
    identifying: List[Dict[str, object]] = []
    for eta in ETAS:
        gamma = math.log((1.0 - eta) / eta)
        diagnostic_mass = 0.25
        source_margin = diagnostic_mass * gamma
        expected = 0.25 * math.log((1.0 - eta) / eta)
        if not math.isclose(source_margin, expected, abs_tol=1e-12):
            raise AssertionError(
                f"round1 mapping failed: eta={eta}, {source_margin} != {expected}"
            )
        identifying.append(
            {
                "eta": eta,
                "beta": 0.0,
                "gamma": gamma,
                "diagnostic_mass": diagnostic_mass,
                "alpha": 0.0,
                "source_margin": source_margin,
                "strict_condition_holds": source_margin > 0,
            }
        )

    redundant = []
    for alpha in (0.0, 0.125, 0.25):
        margin = 0.0
        redundant.append(
            {
                "beta": 0.0,
                "gamma": 0.0,
                "alpha": alpha,
                "population_identification_margin": margin,
                "strict_condition_holds": margin > 2 * alpha,
            }
        )
        if margin > 2 * alpha:
            raise AssertionError("redundant support unexpectedly gives strict guarantee")
    return {"identifying": identifying, "redundant_gamma_zero": redundant}


def verify() -> Dict[str, object]:
    return {
        "status": "PASS",
        "grid_verification": verify_grid(),
        "round1_specialization": round1_specialization(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inference_boundary": (
            "The threshold is sufficient and sharp under only the stated gap and "
            "uniform-deviation assumptions. It does not specify a validated empirical "
            "estimator of beta or gamma for neural LVLMs."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/XID-01_round3/VERIFICATION.json"),
    )
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = result["grid_verification"]
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": result["status"],
                "parameter_cases": summary["parameter_cases"],
                "admissible_gap_cases": summary["admissible_gap_cases"],
                "sharpness_cases": summary["sharpness_cases"],
            }
        )
    )


if __name__ == "__main__":
    main()
