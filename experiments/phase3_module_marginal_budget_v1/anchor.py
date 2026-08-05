"""Resolve the shared P-4096 anchor from the frozen P/S experiment."""

from __future__ import annotations

from typing import Any

from experiments.phase3_private_vs_shared_v1 import SEEDS
from experiments.phase3_private_vs_shared_v1.configs import build_config
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH,
    validate_frozen_protocol,
)

from . import MODULES


def resolve_p4096_anchor() -> dict[str, Any]:
    """Return the unique P-4096 dimensions without duplicating authority."""
    validate_frozen_protocol()
    configs = [build_config("P", 4096, seed) for seed in SEEDS]
    dimension_states = {
        tuple(config["coordinate_dimensions"][name] for name in MODULES)
        for config in configs
    }
    if len(dimension_states) != 1:
        raise RuntimeError("frozen P-4096 configs do not define one shared anchor")
    dimensions = dict(configs[0]["coordinate_dimensions"])
    if tuple(dimensions) != MODULES or sum(dimensions.values()) != 4096:
        raise RuntimeError("frozen P-4096 anchor is malformed")
    return {
        "anchor_id": "P-4096",
        "structure": "P",
        "coordinate_dimensions": dimensions,
        "authoritative_config_ids": [config["config_id"] for config in configs],
        "authoritative_seeds": list(SEEDS),
        "source_protocol": str(PROTOCOL_PATH),
        "source_protocol_id": configs[0]["protocol_id"],
        "allocation_authority": configs[0]["m2_allocation_authority"],
    }
