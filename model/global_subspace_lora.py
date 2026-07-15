"""Deterministic globally shared or module-local low-rank subspace adapters."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


A0_DOMAIN = "stage2-a0-v1"
MAP_DOMAIN = "stage2-map-v1"
MODEL_GROUPS = ("M0", "M1", "M2", "M3")
MAPPING_ROOTS = (43101, 43102, 43103)
GROUP_DIMENSIONS = {
    "M0": {"language": 4096},
    "M1": {"projector_layer_1": 2048, "projector_layer_2": 2048},
    "M2": {"vision": 582, "projector": 2327, "language": 1187},
    "M3": {"shared": 4096},
}


def _string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def _integer(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative integers are forbidden in Stage 2 hash messages")
    return struct.pack("<Q", value)


def a0_message(canonical_name: str, row_index: int, column_index: int) -> bytes:
    return b"".join(
        (
            _string(A0_DOMAIN),
            _string(canonical_name),
            _integer(row_index),
            _integer(column_index),
        )
    )


def mapping_message(
    mapping_root: int, canonical_name: str, factor_name: str, flat_index: int
) -> bytes:
    if factor_name not in ("A", "B"):
        raise ValueError("factor_name must be A or B")
    return b"".join(
        (
            _string(MAP_DOMAIN),
            _integer(mapping_root),
            _string(canonical_name),
            _string(factor_name),
            _integer(flat_index),
        )
    )


def deterministic_a0(
    canonical_name: str, rank: int, in_features: int
) -> torch.Tensor:
    values = np.empty((rank, in_features), dtype=np.float32)
    denominator = float(1 << 53)
    scale = math.sqrt(in_features)
    mask = (1 << 53) - 1
    for row in range(rank):
        for column in range(in_features):
            digest = hashlib.sha256(a0_message(canonical_name, row, column)).digest()
            raw = int.from_bytes(digest[:8], "little", signed=False)
            uniform = ((raw & mask) + 0.5) / denominator
            values[row, column] = np.float32((2.0 * uniform - 1.0) / scale)
    return torch.from_numpy(values)


def deterministic_mapping(
    mapping_root: int,
    canonical_name: str,
    factor_name: str,
    element_count: int,
    dimension: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    indices = np.empty(element_count, dtype=np.int64)
    signs = np.empty(element_count, dtype=np.int8)
    for flat_index in range(element_count):
        digest = hashlib.sha256(
            mapping_message(mapping_root, canonical_name, factor_name, flat_index)
        ).digest()
        indices[flat_index] = int.from_bytes(digest[:8], "little") % dimension
        signs[flat_index] = 1 if (digest[8] & 1) == 0 else -1
    return torch.from_numpy(indices), torch.from_numpy(signs)


@dataclass(frozen=True)
class TargetSpec:
    module_group: str
    canonical_name: str
    rank: int
    in_features: int
    out_features: int

    @property
    def a_elements(self) -> int:
        return self.rank * self.in_features

    @property
    def b_elements(self) -> int:
        return self.out_features * self.rank


@dataclass(frozen=True)
class FactorMapping:
    indices: torch.Tensor
    scales: torch.Tensor


def target_specs(registry: Mapping, modules: Iterable[str]) -> list[TargetSpec]:
    specs: list[TargetSpec] = []
    for module_group in modules:
        section = registry["modules"][module_group]
        rank = int(section["rank"])
        for entry in section["targets"]:
            specs.append(
                TargetSpec(
                    module_group=module_group,
                    canonical_name=entry["canonical_name"],
                    rank=rank,
                    in_features=int(entry["in_features"]),
                    out_features=int(entry["out_features"]),
                )
            )
    return sorted(specs, key=lambda spec: spec.canonical_name.encode("utf-8"))


def _coordinate_group(model_group: str, spec: TargetSpec) -> str:
    if model_group == "M3":
        return "shared"
    if model_group in ("M0", "M2"):
        return spec.module_group
    raise ValueError(f"hashed LoRA is not used for {model_group}")


def build_factor_mappings(
    model_group: str,
    mapping_root: int,
    specs: Sequence[TargetSpec],
) -> tuple[dict[tuple[str, str], FactorMapping], dict[str, dict]]:
    if model_group not in ("M0", "M2", "M3"):
        raise ValueError("factor mappings apply only to M0, M2, and M3")
    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    dimensions = GROUP_DIMENSIONS[model_group]
    raw: dict[tuple[str, str], tuple[str, torch.Tensor, torch.Tensor]] = {}
    counts = {
        group: torch.zeros(dimension, dtype=torch.int64)
        for group, dimension in dimensions.items()
    }
    for spec in specs:
        group = _coordinate_group(model_group, spec)
        for factor_name, elements in (("A", spec.a_elements), ("B", spec.b_elements)):
            indices, signs = deterministic_mapping(
                mapping_root, spec.canonical_name, factor_name, elements, dimensions[group]
            )
            counts[group].scatter_add_(0, indices, torch.ones_like(indices))
            raw[(spec.canonical_name, factor_name)] = (group, indices, signs)

    unused = {
        group: int((value == 0).sum().item()) for group, value in counts.items()
        if torch.any(value == 0)
    }
    if unused:
        raise RuntimeError(
            f"mapping root {mapping_root} leaves unused {model_group} coordinates: {unused}"
        )

    mappings: dict[tuple[str, str], FactorMapping] = {}
    for key, (group, indices, signs) in raw.items():
        scale = signs.to(torch.float32) / counts[group][indices].to(torch.float32).sqrt()
        mappings[key] = FactorMapping(indices=indices, scales=scale)

    statistics = {}
    for group, values in counts.items():
        unique, frequencies = torch.unique(values, sorted=True, return_counts=True)
        histogram = {
            str(int(key)): int(value)
            for key, value in zip(unique.tolist(), frequencies.tolist(), strict=True)
        }
        histogram_bytes = json.dumps(
            histogram, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
        statistics[group] = {
            "dimension": int(values.numel()),
            "minimum": int(values.min().item()),
            "maximum": int(values.max().item()),
            "mean": float(values.to(torch.float64).mean().item()),
            "histogram": histogram,
            "histogram_serialization": "canonical JSON object count->frequency",
            "histogram_sha256": hashlib.sha256(histogram_bytes).hexdigest(),
        }
    return mappings, statistics


class Stage2CoordinateStore(nn.Module):
    def __init__(self, model_group: str) -> None:
        super().__init__()
        if model_group not in GROUP_DIMENSIONS:
            raise ValueError(f"unknown model group {model_group}")
        self.model_group = model_group
        self.coordinates = nn.ParameterDict(
            {
                name: nn.Parameter(torch.zeros(dimension, dtype=torch.float32))
                for name, dimension in GROUP_DIMENSIONS[model_group].items()
            }
        )

    def ordered(self) -> list[tuple[str, nn.Parameter]]:
        return [(name, self.coordinates[name]) for name in GROUP_DIMENSIONS[self.model_group]]


class HashedLoRALinear(nn.Module):
    """A frozen Linear plus LoRA factors reconstructed from shared coordinates."""

    def __init__(
        self,
        base: nn.Linear,
        spec: TargetSpec,
        coordinate_store: Stage2CoordinateStore,
        coordinate_group: str,
        a_mapping: FactorMapping,
        b_mapping: FactorMapping,
    ) -> None:
        super().__init__()
        if not isinstance(base, nn.Linear):
            raise TypeError(f"{spec.canonical_name} is not nn.Linear")
        if (base.in_features, base.out_features) != (spec.in_features, spec.out_features):
            raise ValueError(
                f"{spec.canonical_name} shape mismatch: "
                f"expected {(spec.out_features, spec.in_features)}, "
                f"got {tuple(base.weight.shape)}"
            )
        self.base = base
        for parameter in self.base.parameters():
            parameter.requires_grad = False
        self.canonical_name = spec.canonical_name
        self.rank = spec.rank
        self.in_features = spec.in_features
        self.out_features = spec.out_features
        self.coordinate_group = coordinate_group
        self._coordinate_store_ref = weakref.ref(coordinate_store)
        self.register_buffer("a0", deterministic_a0(
            spec.canonical_name, spec.rank, spec.in_features
        ), persistent=False)
        self.register_buffer("a_indices", a_mapping.indices, persistent=False)
        self.register_buffer("a_scales", a_mapping.scales, persistent=False)
        self.register_buffer("b_indices", b_mapping.indices, persistent=False)
        self.register_buffer("b_scales", b_mapping.scales, persistent=False)

    @property
    def weight(self) -> torch.Tensor:
        return self.base.weight

    @property
    def bias(self) -> torch.Tensor | None:
        return self.base.bias

    def factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        store = self._coordinate_store_ref()
        if store is None:
            raise RuntimeError("Stage 2 coordinate store was destroyed")
        coordinates = store.coordinates[self.coordinate_group]
        a_delta = coordinates[self.a_indices] * self.a_scales
        b = coordinates[self.b_indices] * self.b_scales
        a = self.a0 + a_delta.view(self.rank, self.in_features)
        return a, b.view(self.out_features, self.rank)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        base_output = F.linear(inputs, self.base.weight, self.base.bias)
        a, b = self.factors()
        # alpha_r/r = r/r = 1. Keeping the two linear operations avoids
        # materializing a full-rank-sized delta weight on every forward pass.
        update = F.linear(F.linear(inputs, a), b)
        return base_output + update


def _resolve_parent(root: nn.Module, canonical_name: str) -> tuple[nn.Module, str]:
    components = canonical_name.split(".")
    parent: nn.Module = root
    for component in components[:-1]:
        if component.isdigit():
            parent = parent[int(component)]  # type: ignore[index]
        else:
            parent = getattr(parent, component)
    return parent, components[-1]


def _get_child(parent: nn.Module, name: str) -> nn.Module:
    return parent[int(name)] if name.isdigit() else getattr(parent, name)  # type: ignore[index]


def _set_child(parent: nn.Module, name: str, child: nn.Module) -> None:
    if name.isdigit():
        parent[int(name)] = child  # type: ignore[index]
    else:
        setattr(parent, name, child)


def freeze_all_parameters(model: nn.Module) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = False


def inject_hashed_lora(
    model: nn.Module,
    model_group: str,
    mapping_root: int,
    registry: Mapping,
) -> dict:
    modules = ("language",) if model_group == "M0" else ("vision", "projector", "language")
    specs = target_specs(registry, modules)
    mappings, statistics = build_factor_mappings(model_group, mapping_root, specs)
    freeze_all_parameters(model)
    store = Stage2CoordinateStore(model_group)
    model.stage2_coordinates = store  # type: ignore[attr-defined]
    wrapped_names = []
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        base = _get_child(parent, child_name)
        coordinate_group = _coordinate_group(model_group, spec)
        wrapper = HashedLoRALinear(
            base=base,  # type: ignore[arg-type]
            spec=spec,
            coordinate_store=store,
            coordinate_group=coordinate_group,
            a_mapping=mappings[(spec.canonical_name, "A")],
            b_mapping=mappings[(spec.canonical_name, "B")],
        )
        _set_child(parent, child_name, wrapper)
        wrapped_names.append(spec.canonical_name)
    if model_group in ("M2", "M3"):
        model.vision_encoder.stage2_gradient_enabled = True
    model.stage2_adapter = {  # type: ignore[attr-defined]
        "model_group": model_group,
        "mapping_root": mapping_root,
        "wrapped_names": wrapped_names,
        "mapping_statistics": statistics,
    }
    return model.stage2_adapter  # type: ignore[attr-defined]


def configure_m1_coordinates(model: nn.Module) -> dict:
    freeze_all_parameters(model)
    expected = {
        "projector_layer_1": model.vision_proj.input_projection.coordinates,
        "projector_layer_2": model.vision_proj.output_projection.coordinates,
    }
    actual = {name: int(parameter.numel()) for name, parameter in expected.items()}
    if actual != GROUP_DIMENSIONS["M1"]:
        raise ValueError(f"M1 coordinate dimensions are wrong: {actual}")
    for parameter in expected.values():
        parameter.requires_grad = True
    model.stage2_adapter = {  # type: ignore[attr-defined]
        "model_group": "M1",
        "mapping_root": None,
        "wrapped_names": [
            "vision_proj.input_projection",
            "vision_proj.output_projection",
        ],
        "mapping_statistics": None,
    }
    return model.stage2_adapter  # type: ignore[attr-defined]


def coordinate_parameters(model: nn.Module) -> list[tuple[str, nn.Parameter]]:
    metadata = getattr(model, "stage2_adapter", None)
    if not metadata:
        raise ValueError("model has no Stage 2 adapter")
    if metadata["model_group"] == "M1":
        return [
            ("projector_layer_1", model.vision_proj.input_projection.coordinates),
            ("projector_layer_2", model.vision_proj.output_projection.coordinates),
        ]
    return model.stage2_coordinates.ordered()


def load_coordinate_state(model: nn.Module, values: Mapping[str, torch.Tensor]) -> None:
    expected = dict(coordinate_parameters(model))
    if set(values) != set(expected):
        raise ValueError(
            f"coordinate groups mismatch: expected {sorted(expected)}, got {sorted(values)}"
        )
    with torch.no_grad():
        for name, destination in expected.items():
            source = values[name].detach().to(device=destination.device, dtype=torch.float32)
            if source.shape != destination.shape:
                raise ValueError(f"coordinate shape mismatch for {name}")
            destination.copy_(source)


def coordinate_state(model: nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: parameter.detach().cpu().to(torch.float32).contiguous().clone()
        for name, parameter in coordinate_parameters(model)
    }


def tensor_sha256(tensor: torch.Tensor) -> str:
    value = tensor.detach().cpu().to(torch.float32).contiguous().numpy().astype("<f4", copy=False)
    return hashlib.sha256(value.tobytes(order="C")).hexdigest()


def projector_base_receipt(model: nn.Module) -> dict:
    if hasattr(model.vision_proj, "mlp"):
        first, second = model.vision_proj.mlp[1], model.vision_proj.mlp[3]
        normalization = model.vision_proj.mlp[0]
        tensors = {
            "vision_proj.mlp.1.weight": first.weight,
            "vision_proj.mlp.1.bias": first.bias,
            "vision_proj.mlp.3.weight": second.weight,
            "vision_proj.mlp.3.bias": second.bias,
        }
    else:
        first = model.vision_proj.input_projection
        second = model.vision_proj.output_projection
        normalization = model.vision_proj.normalization
        tensors = {
            "vision_proj.mlp.1.weight": first.base_weight,
            "vision_proj.mlp.1.bias": first.base_bias,
            "vision_proj.mlp.3.weight": second.base_weight,
            "vision_proj.mlp.3.bias": second.base_bias,
        }
    hashes = {name: tensor_sha256(value) for name, value in tensors.items()}
    config = {
        "normalized_shape": list(normalization.normalized_shape),
        "eps": float(normalization.eps),
        "elementwise_affine": bool(normalization.elementwise_affine),
    }
    config_bytes = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    aggregate = hashlib.sha256()
    for name in sorted(hashes):
        aggregate.update(_string(name))
        aggregate.update(bytes.fromhex(hashes[name]))
    return {
        "tensor_sha256": hashes,
        "tensor_hash_protocol": "SHA256 of C-order little-endian float32 raw bytes",
        "aggregate_tensor_sha256": aggregate.hexdigest(),
        "configuration": config,
        "configuration_serialization": "canonical JSON",
        "configuration_sha256": hashlib.sha256(config_bytes).hexdigest(),
    }
