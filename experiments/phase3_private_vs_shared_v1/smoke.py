#!/usr/bin/env python3
"""Two-batch maximum synthetic smoke test; never loads experiment data."""

from __future__ import annotations

import argparse
import json

import torch
from torch import nn

from .parameterization import (
    CoordinateStore, ProjectedUpdate, assert_frozen_unchanged,
    assert_storage_contract, frozen_snapshot,
)


class TinySyntheticModel(nn.Module):
    def __init__(self, structure: str) -> None:
        super().__init__()
        dimensions = (
            {"vision": 3, "projector": 5, "language": 2}
            if structure == "P" else {"shared": 10}
        )
        self.frozen_base = nn.Linear(4, 4)
        for parameter in self.frozen_base.parameters():
            parameter.requires_grad_(False)
        self.coordinates = CoordinateStore(structure, dimensions)
        generator = torch.Generator().manual_seed(9)
        self.updates = nn.ModuleList([
            ProjectedUpdate(
                self.coordinates, name,
                torch.randn(4, self.coordinates.for_module(name).numel(), generator=generator),
            )
            for name in ("vision", "projector", "language")
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.frozen_base(x) + sum(update() for update in self.updates)


def run(structure: str, batches: int) -> dict:
    if batches not in (1, 2):
        raise ValueError("synthetic smoke is limited to one or two batches")
    torch.manual_seed(17)
    model = TinySyntheticModel(structure)
    assert_storage_contract(model.coordinates)
    trainable = {id(parameter) for parameter in model.coordinates.parameters()}
    snapshot = frozen_snapshot(model, trainable)
    optimizer = torch.optim.SGD(model.coordinates.parameters(), lr=0.01)
    for _ in range(batches):
        optimizer.zero_grad()
        loss = model(torch.randn(2, 4)).square().mean()
        loss.backward()
        optimizer.step()
    assert_frozen_unchanged(model, snapshot, trainable)
    return {
        "status": "passed", "structure": structure, "batches": batches,
        "synthetic_data_only": True, "formal_training": False,
        "free_parameter_count": model.coordinates.free_parameter_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", choices=("P", "S"), required=True)
    parser.add_argument("--batches", type=int, default=2)
    args = parser.parse_args()
    print(json.dumps(run(args.structure, args.batches), indent=2))


if __name__ == "__main__":
    main()
