from __future__ import annotations

from experiments.phase3_private_vs_shared_v1.configs import private_allocation

from . import BUDGETS, CANDIDATE_COUNT, PROTOCOL_ID, SEEDS, STRUCTURES


def build_config(structure: str, budget: int, seed: int) -> dict:
    if structure not in STRUCTURES or budget not in BUDGETS or seed not in SEEDS:
        raise ValueError("candidate is outside the preregistered 12-model matrix")
    dimensions = private_allocation(budget) if structure == "P" else {"shared": budget}
    return {
        "protocol_id": PROTOCOL_ID,
        "config_id": f"{structure}-budget-{budget}-seed-{seed}",
        "structure": structure,
        "budget": budget,
        "seed": seed,
        "coordinate_dimensions": dimensions,
        "projection_rule": "stage2-map-v1/module-specific-fixed-map",
    }


def generate_matrix() -> list[dict]:
    matrix = [
        build_config(structure, budget, seed)
        for structure in STRUCTURES
        for budget in BUDGETS
        for seed in SEEDS
    ]
    if len(matrix) != CANDIDATE_COUNT:
        raise AssertionError("candidate matrix is not exactly 12 models")
    return matrix


def load_candidate(config_id: str) -> dict:
    matches = [row for row in generate_matrix() if row["config_id"] == config_id]
    if len(matches) != 1:
        raise ValueError("unknown candidate ID")
    return matches[0]
