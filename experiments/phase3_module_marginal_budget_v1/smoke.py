"""Small CPU-only private-coordinate training smoke."""

from __future__ import annotations

import torch
from torch import nn

from .parameterization import (
    ProjectedUpdate,
    assert_frozen_unchanged,
    build_private_store,
    frozen_snapshot,
)


def run(dimensions: dict[str, int], batches: int = 2) -> dict:
    if batches not in (1, 2):
        raise ValueError("smoke is limited to one or two batches")
    store = build_private_store(dimensions)
    frozen = nn.Linear(4, 4)
    frozen.requires_grad_(False)
    generator = torch.Generator().manual_seed(9)
    updates = nn.ModuleList(
        ProjectedUpdate(
            store,
            name,
            torch.randn(4, store.for_module(name).numel(), generator=generator),
        )
        for name in ("vision", "projector", "language")
    )
    trainable_ids = {id(parameter) for parameter in store.parameters()}
    container = nn.ModuleDict({"frozen": frozen, "store": store, "updates": updates})
    snapshot = frozen_snapshot(container, trainable_ids)
    optimizer = torch.optim.SGD(store.parameters(), lr=0.01)
    torch.manual_seed(17)
    for _ in range(batches):
        optimizer.zero_grad()
        x = torch.randn(2, 4)
        loss = (frozen(x) + sum(update() for update in updates)).square().mean()
        loss.backward()
        optimizer.step()
    assert_frozen_unchanged(container, snapshot, trainable_ids)
    return {
        "status": "passed",
        "structure": "P",
        "coordinate_dimensions": dict(dimensions),
        "free_parameter_count": store.free_parameter_count,
        "batches": batches,
        "synthetic_data_only": True,
        "formal_training": False,
        "frozen_parameters_unchanged": True,
    }
