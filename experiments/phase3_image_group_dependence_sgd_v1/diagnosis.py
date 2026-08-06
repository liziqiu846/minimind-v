"""Pure gradient diagnostics that leave the formal trajectory untouched."""

from __future__ import annotations

import hashlib
import random
import struct
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import torch

from . import PROTOCOL_ID


@dataclass(frozen=True)
class RNGSnapshot:
    python: object
    numpy: tuple
    torch_cpu: torch.Tensor
    torch_cuda: tuple[torch.Tensor, ...]


def capture_rng() -> RNGSnapshot:
    return RNGSnapshot(
        python=random.getstate(),
        numpy=np.random.get_state(),
        torch_cpu=torch.get_rng_state().clone(),
        torch_cuda=tuple(state.clone() for state in torch.cuda.get_rng_state_all())
        if torch.cuda.is_available()
        else (),
    )


def restore_rng(snapshot: RNGSnapshot) -> None:
    random.setstate(snapshot.python)
    np.random.set_state(snapshot.numpy)
    torch.set_rng_state(snapshot.torch_cpu)
    if snapshot.torch_cuda:
        torch.cuda.set_rng_state_all(list(snapshot.torch_cuda))


def rng_equal(left: RNGSnapshot, right: RNGSnapshot) -> bool:
    numpy_equal = (
        left.numpy[0] == right.numpy[0]
        and np.array_equal(left.numpy[1], right.numpy[1])
        and left.numpy[2:] == right.numpy[2:]
    )
    return (
        left.python == right.python
        and numpy_equal
        and torch.equal(left.torch_cpu, right.torch_cpu)
        and len(left.torch_cuda) == len(right.torch_cuda)
        and all(torch.equal(a, b) for a, b in zip(left.torch_cuda, right.torch_cuda))
    )


def fixed_index(seed: int, optimizer_step: int, role: str, modulus: int) -> int:
    if modulus <= 0 or role not in ("batch-position", "ghost"):
        raise ValueError("invalid fixed-index request")
    digest = hashlib.sha256(
        f"{PROTOCOL_ID}|{seed}|{optimizer_step}|{role}".encode("utf-8")
    ).digest()
    return struct.unpack("<Q", digest[:8])[0] % modulus


def _clone_gradients(parameters: Sequence[torch.nn.Parameter]) -> list[torch.Tensor]:
    return [
        torch.zeros_like(parameter) if parameter.grad is None else parameter.grad.detach().clone()
        for parameter in parameters
    ]


def _restore_gradients(
    parameters: Sequence[torch.nn.Parameter],
    gradients: Sequence[torch.Tensor | None],
) -> None:
    for parameter, gradient in zip(parameters, gradients):
        parameter.grad = None if gradient is None else gradient.clone()


def replace_group(
    batch: tuple[torch.Tensor, torch.Tensor, Any],
    position: int,
    ghost: tuple[torch.Tensor, torch.Tensor, Any],
) -> tuple[torch.Tensor, torch.Tensor, Any]:
    input_ids, labels, pixels = batch
    ghost_ids, ghost_labels, ghost_pixels = ghost
    replaced_ids = input_ids.clone()
    replaced_labels = labels.clone()
    replaced_ids[position].copy_(ghost_ids)
    replaced_labels[position].copy_(ghost_labels)
    if isinstance(pixels, Mapping):
        replaced_pixels = {key: value.clone() for key, value in pixels.items()}
        for key in replaced_pixels:
            replaced_pixels[key][position].copy_(ghost_pixels[key])
    elif pixels is None:
        replaced_pixels = None
    else:
        replaced_pixels = pixels.clone()
        replaced_pixels[position].copy_(ghost_pixels)
    return replaced_ids, replaced_labels, replaced_pixels


def _gradient(
    model: torch.nn.Module,
    parameters: Sequence[torch.nn.Parameter],
    batch: tuple[torch.Tensor, torch.Tensor, Any],
    accumulation: int,
) -> list[torch.Tensor]:
    input_ids, labels, pixels = batch
    if input_ids.shape[0] % accumulation:
        raise ValueError("effective batch cannot be split into accumulation chunks")
    micro = input_ids.shape[0] // accumulation
    model.zero_grad(set_to_none=True)
    for start in range(0, input_ids.shape[0], micro):
        end = start + micro
        chunk_pixels = (
            {key: value[start:end] for key, value in pixels.items()}
            if isinstance(pixels, Mapping)
            else None if pixels is None else pixels[start:end]
        )
        with torch.autocast(
            device_type=input_ids.device.type,
            dtype=torch.bfloat16,
            enabled=input_ids.device.type == "cuda",
        ):
            loss = model(
                input_ids=input_ids[start:end],
                labels=labels[start:end],
                pixel_values=chunk_pixels,
            ).loss
        (loss / accumulation).backward()
    return _clone_gradients(parameters)


def diagnose_replacement(
    model: torch.nn.Module,
    parameters: Sequence[torch.nn.Parameter],
    batch: tuple[torch.Tensor, torch.Tensor, Any],
    ghost: tuple[torch.Tensor, torch.Tensor, Any],
    *,
    selected_position: int,
    accumulation: int,
) -> dict[str, float]:
    """Compute true and whole-group-replacement gradients without state changes."""
    rng_before = capture_rng()
    saved_grads = [
        None if parameter.grad is None else parameter.grad.detach().clone()
        for parameter in parameters
    ]
    saved_buffers = {
        name: buffer.detach().clone() for name, buffer in model.named_buffers()
    }
    parameter_versions = [parameter._version for parameter in parameters]
    try:
        true = _gradient(model, parameters, batch, accumulation)
        ghost_batch = replace_group(batch, selected_position, ghost)
        replaced = _gradient(model, parameters, ghost_batch, accumulation)
        squared_l2 = float(
            sum(
                torch.sum((left.float() - right.float()) ** 2).double()
                for left, right in zip(true, replaced)
            ).item()
        )
        true_norm2 = float(
            sum(torch.sum(value.float() ** 2).double() for value in true).item()
        )
        ghost_norm2 = float(
            sum(torch.sum(value.float() ** 2).double() for value in replaced).item()
        )
    finally:
        with torch.no_grad():
            for name, buffer in model.named_buffers():
                buffer.copy_(saved_buffers[name])
        _restore_gradients(parameters, saved_grads)
        restore_rng(rng_before)
    if [parameter._version for parameter in parameters] != parameter_versions:
        raise RuntimeError("diagnosis changed a trainable parameter")
    if not rng_equal(rng_before, capture_rng()):
        raise RuntimeError("diagnosis changed RNG state")
    return {
        "squared_l2_gradient_difference": squared_l2,
        "true_gradient_squared_l2": true_norm2,
        "ghost_gradient_squared_l2": ghost_norm2,
    }

