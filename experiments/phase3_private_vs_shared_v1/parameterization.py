"""P/S coordinate stores and module-specific fixed projections."""

from __future__ import annotations

from collections import OrderedDict
from typing import Mapping

import torch
from torch import nn


class CoordinateStore(nn.Module):
    def __init__(self, structure: str, dimensions: Mapping[str, int]) -> None:
        super().__init__()
        expected = ("vision", "projector", "language") if structure == "P" else ("shared",)
        if structure not in ("P", "S") or tuple(dimensions) != expected:
            raise ValueError("coordinate groups do not match structure")
        self.structure = structure
        self.dimensions = OrderedDict((name, int(dimensions[name])) for name in expected)
        if any(value <= 0 for value in self.dimensions.values()):
            raise ValueError("coordinate dimensions must be positive")
        self.coordinates = nn.ParameterDict({
            name: nn.Parameter(torch.zeros(size, dtype=torch.float32))
            for name, size in self.dimensions.items()
        })

    def for_module(self, module: str) -> nn.Parameter:
        if module not in ("vision", "projector", "language"):
            raise ValueError("unknown module")
        return self.coordinates[module if self.structure == "P" else "shared"]

    def unique_parameters(self) -> list[nn.Parameter]:
        return list(self.coordinates.values())

    @property
    def free_parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.unique_parameters())


class ProjectedUpdate(nn.Module):
    """Compute Δθ_m=P_m w; maps may differ while w is the same object."""

    def __init__(self, store: CoordinateStore, module: str, projection: torch.Tensor):
        super().__init__()
        coordinate = store.for_module(module)
        if projection.ndim != 2 or projection.shape[1] != coordinate.numel():
            raise ValueError("projection shape is incompatible with coordinate vector")
        self.store = store
        self.module_name = module
        self.register_buffer("projection", projection.detach().clone())

    def forward(self) -> torch.Tensor:
        return self.projection @ self.store.for_module(self.module_name)


def assert_storage_contract(store: CoordinateStore) -> None:
    parameters = [store.for_module(name) for name in ("vision", "projector", "language")]
    if store.structure == "S":
        if not (parameters[0] is parameters[1] is parameters[2]):
            raise AssertionError("S modules do not reference one shared parameter object")
        if len(store.state_dict()) != 1:
            raise AssertionError("S coordinate vector is stored more than once")
    else:
        pointers = [parameter.untyped_storage().data_ptr() for parameter in parameters]
        if len(set(pointers)) != 3:
            raise AssertionError("P coordinate vectors share storage")


def frozen_snapshot(module: nn.Module, trainable_ids: set[int]) -> dict[str, torch.Tensor]:
    return {
        name: parameter.detach().cpu().clone()
        for name, parameter in module.named_parameters()
        if id(parameter) not in trainable_ids
    }


def assert_frozen_unchanged(module: nn.Module, snapshot: Mapping[str, torch.Tensor],
                            trainable_ids: set[int]) -> None:
    current = {name: p.detach().cpu() for name, p in module.named_parameters()
               if id(p) not in trainable_ids}
    if current.keys() != snapshot.keys() or any(
        not torch.equal(current[name], before) for name, before in snapshot.items()
    ):
        raise AssertionError("a frozen parameter changed")
