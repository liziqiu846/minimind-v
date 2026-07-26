"""Bit-only complexity accounting with disjoint certificate scopes."""

from __future__ import annotations

import math
from typing import Any, Mapping

from . import CANDIDATE_COUNT, SEEDS, STRUCTURES
from .parameterization import CoordinateStore


def candidate_identity_bits() -> float:
    return math.log2(CANDIDATE_COUNT)


def bits_to_nats(bits: float) -> float:
    return float(bits) * math.log(2.0)


def training_certificate_bits(
    store: CoordinateStore,
    *,
    encoded_parameter_bits: Mapping[str, int],
    structure_bits: float = math.log2(len(STRUCTURES)),
    budget_identity_bits: float = math.log2(3),
) -> dict[str, Any]:
    expected = tuple(store.coordinates.keys())
    if set(encoded_parameter_bits) != set(expected):
        raise ValueError("encoded groups do not equal unique registered coordinate groups")
    parameter_bits = float(sum(int(encoded_parameter_bits[name]) for name in expected))
    if parameter_bits < 0:
        raise ValueError("parameter bit length must be non-negative")
    structural = float(structure_bits) + float(budget_identity_bits)
    total = parameter_bits + structural
    return {
        "scope": "training_certificate",
        "unit": "bit",
        "parameter_bits": parameter_bits,
        "structure_bits": float(structure_bits),
        "budget_identity_bits": float(budget_identity_bits),
        "seed_integer_bits": 0.0,
        "candidate_identity_bits": 0.0,
        "seed_rule": f"predeclared_set_of_{len(SEEDS)}_charged_only_via_candidate_identity",
        "coded_bits": total,
        "coded_nats_for_natural_log_formula": bits_to_nats(total),
    }


def confirmation_selection_bits() -> dict[str, Any]:
    bits = candidate_identity_bits()
    return {
        "scope": "fresh_confirmation_candidate_selection",
        "unit": "bit",
        "candidate_count": CANDIDATE_COUNT,
        "candidate_identity_bits": bits,
        "checkpoint_bits": 0.0,
        "seed_integer_bits": 0.0,
        "training_certificate_bits_recharged": 0.0,
        "coded_bits": bits,
        "coded_nats_for_natural_log_formula": bits_to_nats(bits),
    }
