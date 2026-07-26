"""Generate and audit the frozen 2 x 3 x 3 candidate matrix."""

from __future__ import annotations

import math
import hashlib
from fractions import Fraction
from typing import Any, Mapping, Sequence

from . import BUDGETS, CANDIDATE_COUNT, PROTOCOL_ID, SEEDS, STRUCTURES
from .authority import read_m2_authority
from .common import canonical_bytes


def private_allocation(total: int) -> dict[str, int]:
    authority = read_m2_authority()
    weights = authority["factor_elements"]
    order = tuple(weights)
    denominator = sum(weights.values())
    raw = {name: Fraction(total * weights[name], denominator) for name in order}
    result = {name: math.floor(raw[name]) for name in order}
    remainder = total - sum(result.values())
    priority = sorted(order, key=lambda n: (-(raw[n] - result[n]), order.index(n)))
    for name in priority[:remainder]:
        result[name] += 1
    if sum(result.values()) != total:
        raise AssertionError("P allocation does not sum to its total budget")
    return result


def build_config(structure: str, budget: int, seed: int) -> dict[str, Any]:
    if structure not in STRUCTURES or budget not in BUDGETS or seed not in SEEDS:
        raise ValueError("candidate identity is outside the frozen matrix")
    authority = read_m2_authority()
    dimensions = private_allocation(budget) if structure == "P" else {"shared": budget}
    return {
        "protocol_id": PROTOCOL_ID,
        "config_id": f"{structure}-budget-{budget}-seed-{seed}",
        "structure": structure,
        "budget": budget,
        "seed": seed,
        "coordinate_dimensions": dimensions,
        "projection_rule": "stage2-map-v1/module-specific-fixed-map",
        "candidate_identity_bits": math.log2(CANDIDATE_COUNT),
        "seed_integer_bits": 0.0,
        "m2_allocation_authority": authority,
        "training_status": "configured",
    }


def generate_matrix() -> list[dict[str, Any]]:
    return [
        build_config(structure, budget, seed)
        for structure in STRUCTURES for budget in BUDGETS for seed in SEEDS
    ]


def matrix_sha256(configs: Sequence[Mapping[str, Any]] | None = None) -> str:
    selected = list(configs) if configs is not None else generate_matrix()
    validate_matrix(selected)
    return hashlib.sha256(canonical_bytes(selected)).hexdigest()


def load_candidate(config_id: str) -> dict[str, Any]:
    matches = [item for item in generate_matrix() if item["config_id"] == config_id]
    if len(matches) != 1:
        raise ValueError("config ID is absent or duplicated in the frozen matrix")
    return matches[0]


def validate_matrix(configs: Sequence[Mapping[str, Any]]) -> None:
    if len(configs) != CANDIDATE_COUNT:
        raise ValueError("candidate matrix must contain exactly 18 entries")
    ids = [str(item["config_id"]) for item in configs]
    identities = [(item["structure"], item["budget"], item["seed"]) for item in configs]
    if len(set(ids)) != CANDIDATE_COUNT or len(set(identities)) != CANDIDATE_COUNT:
        raise ValueError("candidate matrix contains duplicates")
    expected = generate_matrix()
    if [dict(item) for item in configs] != expected:
        raise ValueError("candidate matrix differs from the frozen generator")
    for budget in BUDGETS:
        for seed in SEEDS:
            pair = [x for x in configs if x["budget"] == budget and x["seed"] == seed]
            if {x["structure"] for x in pair} != set(STRUCTURES):
                raise ValueError("P/S pairing is incomplete")
            comparable = ("budget", "seed", "projection_rule", "m2_allocation_authority")
            if any(pair[0][key] != pair[1][key] for key in comparable):
                raise ValueError("P/S fairness fields differ")
