"""Thin private-only facade over the established Phase 3 training primitives."""

from __future__ import annotations

from typing import Iterable

import torch
from torch import nn

from experiments.phase3_private_vs_shared_v1.parameterization import (
    assert_frozen_unchanged,
    frozen_snapshot,
)
from trainer.train_stage2 import (
    frozen_parameter_hash,
    learning_rate_at,
    move_pixels,
    permutation_for_epoch,
    permutation_sha256,
    seed_everything,
)


def private_trainable_parameters(model: nn.Module) -> list[nn.Parameter]:
    store = getattr(model, "stage2_coordinates", None)
    if store is None or getattr(store, "structure", None) != "P":
        raise ValueError("model is not a private-coordinate candidate")
    parameters = list(store.unique_parameters())
    if len(parameters) != 3 or any(
        not parameter.requires_grad for parameter in parameters
    ):
        raise AssertionError(
            "private candidate must expose three trainable coordinates"
        )
    allowed = {id(parameter) for parameter in parameters}
    unexpected = [
        name
        for name, parameter in model.named_parameters()
        if parameter.requires_grad and id(parameter) not in allowed
    ]
    if unexpected:
        raise AssertionError(f"non-coordinate parameters are trainable: {unexpected}")
    return parameters


def make_optimizer(
    parameters: Iterable[nn.Parameter], optimizer_spec: dict
) -> torch.optim.AdamW:
    """Construct the same AdamW optimizer used by the established trainer."""
    return torch.optim.AdamW(
        list(parameters),
        lr=float(optimizer_spec["learning_rate"]),
        betas=tuple(optimizer_spec["betas"]),
        eps=float(optimizer_spec["eps"]),
        weight_decay=float(optimizer_spec["weight_decay"]),
        amsgrad=bool(optimizer_spec["amsgrad"]),
    )


__all__ = [
    "assert_frozen_unchanged",
    "frozen_parameter_hash",
    "frozen_snapshot",
    "learning_rate_at",
    "make_optimizer",
    "move_pixels",
    "permutation_for_epoch",
    "permutation_sha256",
    "private_trainable_parameters",
    "seed_everything",
]
