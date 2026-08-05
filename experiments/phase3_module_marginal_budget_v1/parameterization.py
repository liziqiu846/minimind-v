"""Private-only access to the proven Phase 3 parameterization."""

from __future__ import annotations

from typing import Any, Mapping

from torch import nn

from experiments.phase3_private_vs_shared_v1.adapter_runtime import (
    build_candidate_model as _build_candidate_model,
)
from experiments.phase3_private_vs_shared_v1.parameterization import (
    CoordinateStore,
    ProjectedUpdate,
    assert_frozen_unchanged,
    assert_storage_contract,
    frozen_snapshot,
)
from experiments.stage2_protocol import Stage2Protocol


def build_private_store(dimensions: Mapping[str, int]) -> CoordinateStore:
    store = CoordinateStore("P", dimensions)
    assert_storage_contract(store)
    return store


def build_candidate_model(
    config: Mapping[str, Any],
    stage2: Stage2Protocol,
    *,
    device: str = "cpu",
) -> nn.Module:
    if config.get("structure") != "P":
        raise ValueError("module marginal budget framework only supports structure P")
    model = _build_candidate_model(config, stage2, device=device)
    assert_storage_contract(model.stage2_coordinates)
    return model


__all__ = [
    "CoordinateStore",
    "ProjectedUpdate",
    "assert_frozen_unchanged",
    "assert_storage_contract",
    "build_candidate_model",
    "build_private_store",
    "frozen_snapshot",
]
