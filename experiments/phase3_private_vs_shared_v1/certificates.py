"""Adapters for frozen smoothed NLL and bounded Phase 3 v6 q scores."""

from __future__ import annotations

import math
from typing import Any, Sequence

from experiments.generalization_bound import prediction_smoothing_interval

from . import CANDIDATE_COUNT
from .complexity import bits_to_nats


def semantic_certificate(empirical_smoothed_nll: float, sample_count: int,
                         coded_bits: float, delta: float, *,
                         vocab_size: int, alpha: float) -> dict[str, Any]:
    risk = float(empirical_smoothed_nll)
    if not math.isfinite(risk) or risk < 0 or sample_count <= 0 or not 0 < delta < 1:
        raise ValueError("invalid semantic certificate inputs")
    complexity_nats = bits_to_nats(coded_bits)
    interval = prediction_smoothing_interval(vocab_size, alpha)
    unit_interval_radius = math.sqrt(
        (complexity_nats + math.log(1.0 / delta)) / (2.0 * sample_count)
    )
    penalty = interval.width_bits * unit_interval_radius
    return {
        "risk_implementation": "existing_prediction_smoothed_conditional_nll",
        "empirical_risk": risk,
        "complexity_penalty": penalty,
        "unit_interval_radius": unit_interval_radius,
        "loss_range_width": interval.width_bits,
        "loss_range_unit": "bit_NLL",
        "smoothing_alpha": float(alpha),
        "vocab_size": int(vocab_size),
        "semantic_bound": risk + penalty,
        "coded_bits": float(coded_bits),
        "bit_to_nat_multiplier": math.log(2.0),
        "delta": float(delta),
        "sample_count": int(sample_count),
    }


def symmetric_pair_gain(q_ii: float, q_ji: float,
                        q_jj: float, q_ij: float) -> float:
    values = [float(value) for value in (q_ii, q_ji, q_jj, q_ij)]
    if any(not math.isfinite(x) or not 0 <= x <= 1 for x in values):
        raise ValueError("Phase 3 v6 q score is outside [0,1]")
    gain = 0.5 * ((values[0] - values[1]) + (values[2] - values[3]))
    if not -1 <= gain <= 1:
        raise AssertionError("symmetric visual gain is outside [-1,1]")
    return gain


def visual_gain_certificate(q_ii: Sequence[float], q_ji: Sequence[float],
                            q_jj: Sequence[float], q_ij: Sequence[float],
                            delta: float, *,
                            candidate_count: int = CANDIDATE_COUNT) -> dict[str, Any]:
    lengths = {len(q_ii), len(q_ji), len(q_jj), len(q_ij)}
    if (lengths != {len(q_ii)} or not q_ii or not 0 < delta < 1
            or isinstance(candidate_count, bool) or candidate_count <= 0):
        raise ValueError("invalid visual certificate inputs")
    gains = [
        symmetric_pair_gain(a, b, c, d)
        for a, b, c, d in zip(q_ii, q_ji, q_jj, q_ij)
    ]
    empirical = math.fsum(gains) / len(gains)
    selection_bits = math.log2(candidate_count)
    selection_nats = bits_to_nats(selection_bits)
    radius = math.sqrt(
        2.0 * (selection_nats + math.log(1.0 / delta)) / len(gains)
    )
    return {
        "score_implementation": "phase3_v6_bounded_visual_semantic_contrast_q",
        "estimand": "symmetric_disjoint_pair_gain",
        "formula": "0.5*((q_ii-q_ji)+(q_jj-q_ij))",
        "empirical_visual_gain": empirical,
        "support": [-1.0, 1.0],
        "confidence_radius": radius,
        "candidate_count": int(candidate_count),
        "candidate_selection_bits": selection_bits,
        "candidate_selection_nats": selection_nats,
        "selection_rule": "predeclared_finite_family_union_bound",
        "visual_gain_lower_bound": max(-1.0, empirical - radius),
        "pair_count": len(gains),
        "delta": float(delta),
    }
