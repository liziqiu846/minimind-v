"""Build P/S adapters directly from frozen Stage 2 primitives."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from experiments.stage2_model import build_stage2_model
from experiments.stage2_protocol import Stage2Protocol, load_target_registry
from model.global_subspace_lora import (
    FactorMapping, HashedLoRALinear, TargetSpec, _get_child, _resolve_parent,
    _set_child, deterministic_mapping, freeze_all_parameters, target_specs,
)

from .parameterization import CoordinateStore, assert_storage_contract


def _group(structure: str, spec: TargetSpec) -> str:
    return spec.module_group if structure == "P" else "shared"


def build_mappings(structure: str, seed: int, specs: Sequence[TargetSpec],
                   dimensions: Mapping[str, int]) -> dict[tuple[str, str], FactorMapping]:
    counts = {
        name: torch.zeros(int(size), dtype=torch.int64)
        for name, size in dimensions.items()
    }
    raw = {}
    for spec in specs:
        group = _group(structure, spec)
        for factor, elements in (("A", spec.a_elements), ("B", spec.b_elements)):
            indices, signs = deterministic_mapping(
                seed, spec.canonical_name, factor, elements, int(dimensions[group])
            )
            counts[group].scatter_add_(0, indices, torch.ones_like(indices))
            raw[(spec.canonical_name, factor)] = (group, indices, signs)
    if any(torch.any(value == 0) for value in counts.values()):
        raise RuntimeError("frozen projection leaves an unused coordinate")
    return {
        key: FactorMapping(
            indices=indices,
            scales=signs.float() / counts[group][indices].float().sqrt(),
        )
        for key, (group, indices, signs) in raw.items()
    }


def build_candidate_model(config: Mapping[str, Any], stage2: Stage2Protocol,
                          *, device: str | torch.device = "cpu") -> nn.Module:
    structure = str(config["structure"])
    legacy_group = "M2" if structure == "P" else "M3"
    model = build_stage2_model(
        legacy_group, stage2, int(config["seed"]), device="cpu", dtype=torch.float32
    )
    registry = load_target_registry()
    specs = target_specs(registry, ("vision", "projector", "language"))
    bases = {}
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        if not isinstance(child, HashedLoRALinear):
            raise TypeError("Stage 2 target is not a hashed LoRA wrapper")
        bases[spec.canonical_name] = child.base
        _set_child(parent, child_name, child.base)
    delattr(model, "stage2_coordinates")
    freeze_all_parameters(model)
    dimensions = OrderedDict(
        (name, int(size)) for name, size in config["coordinate_dimensions"].items()
    )
    store = CoordinateStore(structure, dimensions)
    model.stage2_coordinates = store
    mappings = build_mappings(structure, int(config["seed"]), specs, dimensions)
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        group = _group(structure, spec)
        _set_child(parent, child_name, HashedLoRALinear(
            base=bases[spec.canonical_name],
            spec=spec,
            coordinate_store=store,
            coordinate_group=group,
            a_mapping=mappings[(spec.canonical_name, "A")],
            b_mapping=mappings[(spec.canonical_name, "B")],
        ))
    model.stage2_adapter = {
        "structure": structure,
        "mapping_root": int(config["seed"]),
        "coordinate_dimensions": dict(dimensions),
        "wrapped_names": [spec.canonical_name for spec in specs],
    }
    model.vision_encoder.stage2_gradient_enabled = True
    assert_storage_contract(store)
    model.to(device=device, dtype=torch.float32)
    return model
