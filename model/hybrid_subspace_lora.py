"""Phase 4 M4 hybrid shared/private deterministic subspace adapters.

This module is intentionally independent of the frozen Stage 2 adapter
implementation.  The only trainable objects it creates are the four declared
coordinate vectors.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


M4_MODEL_GROUP = "M4"
MODULE_GROUPS = ("vision", "projector", "language")
COORDINATE_BLOCKS = (
    "shared_coordinates",
    "vision_private_coordinates",
    "projector_private_coordinates",
    "language_private_coordinates",
)
PRIVATE_BLOCK_BY_MODULE = {
    "vision": "vision_private_coordinates",
    "projector": "projector_private_coordinates",
    "language": "language_private_coordinates",
}
MAPPING_ROOTS = (43101, 43102, 43103)
MAPPING_DOMAIN = "phase4-m4-map-v1"
A0_DOMAIN = "phase4-m4-a0-v1"
MAPPING_DIGEST_DOMAIN = b"phase4-m4-factor-mapping-v1\0"


def _string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def _integer(value: int) -> bytes:
    if isinstance(value, bool) or int(value) < 0:
        raise ValueError("M4 hash-message integers must be non-negative")
    return struct.pack("<Q", int(value))


def mapping_message(
    mapping_root: int,
    canonical_target_name: str,
    module_group: str,
    coordinate_block_id: str,
    factor_id: str,
    flat_index: int,
) -> bytes:
    """Return the complete frozen M4 mapping hash message."""

    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    if module_group not in MODULE_GROUPS:
        raise ValueError("unknown M4 module group")
    if coordinate_block_id not in COORDINATE_BLOCKS:
        raise ValueError("unknown M4 coordinate block")
    if factor_id not in ("A", "B"):
        raise ValueError("factor_id must be A or B")
    return b"".join(
        (
            _string(MAPPING_DOMAIN),
            _integer(mapping_root),
            _string(canonical_target_name),
            _string(module_group),
            _string(coordinate_block_id),
            _string(factor_id),
            _integer(flat_index),
        )
    )


def a0_message(
    mapping_root: int,
    canonical_target_name: str,
    module_group: str,
    coordinate_block_id: str,
    row_index: int,
    column_index: int,
) -> bytes:
    """Return the M4 fixed-A0 message, including the branch block ID."""

    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    if module_group not in MODULE_GROUPS:
        raise ValueError("unknown M4 module group")
    if coordinate_block_id not in COORDINATE_BLOCKS:
        raise ValueError("unknown M4 coordinate block")
    return b"".join(
        (
            _string(A0_DOMAIN),
            _integer(mapping_root),
            _string(canonical_target_name),
            _string(module_group),
            _string(coordinate_block_id),
            _integer(row_index),
            _integer(column_index),
        )
    )


def deterministic_mapping(
    mapping_root: int,
    canonical_target_name: str,
    module_group: str,
    coordinate_block_id: str,
    factor_id: str,
    element_count: int,
    coordinate_dimension: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if (
        isinstance(element_count, bool)
        or int(element_count) <= 0
        or isinstance(coordinate_dimension, bool)
        or int(coordinate_dimension) <= 0
    ):
        raise ValueError("mapping element count and dimension must be positive")
    indices = np.empty(int(element_count), dtype=np.int64)
    signs = np.empty(int(element_count), dtype=np.int8)
    for flat_index in range(int(element_count)):
        digest = hashlib.sha256(
            mapping_message(
                mapping_root,
                canonical_target_name,
                module_group,
                coordinate_block_id,
                factor_id,
                flat_index,
            )
        ).digest()
        indices[flat_index] = (
            int.from_bytes(digest[:8], "little", signed=False)
            % int(coordinate_dimension)
        )
        signs[flat_index] = 1 if (digest[8] & 1) == 0 else -1
    return torch.from_numpy(indices), torch.from_numpy(signs)


def deterministic_a0(
    mapping_root: int,
    canonical_target_name: str,
    module_group: str,
    coordinate_block_id: str,
    rank: int,
    in_features: int,
) -> torch.Tensor:
    if rank <= 0 or in_features <= 0:
        raise ValueError("A0 rank and input width must be positive")
    values = np.empty((rank, in_features), dtype=np.float32)
    denominator = float(1 << 53)
    mask = (1 << 53) - 1
    scale = math.sqrt(in_features)
    for row_index in range(rank):
        for column_index in range(in_features):
            digest = hashlib.sha256(
                a0_message(
                    mapping_root,
                    canonical_target_name,
                    module_group,
                    coordinate_block_id,
                    row_index,
                    column_index,
                )
            ).digest()
            raw = int.from_bytes(digest[:8], "little", signed=False)
            uniform = ((raw & mask) + 0.5) / denominator
            values[row_index, column_index] = np.float32(
                (2.0 * uniform - 1.0) / scale
            )
    return torch.from_numpy(values)


@dataclass(frozen=True)
class HybridTargetSpec:
    module_group: str
    canonical_name: str
    old_rank: int
    shared_rank: int
    private_rank: int
    in_features: int
    out_features: int
    outer_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.module_group not in MODULE_GROUPS:
            raise ValueError("unknown target module group")
        if (
            self.old_rank <= 0
            or self.shared_rank <= 0
            or self.private_rank <= 0
            or self.shared_rank + self.private_rank != self.old_rank
        ):
            raise ValueError("M4 branch ranks do not preserve the old rank")
        if self.in_features <= 0 or self.out_features <= 0:
            raise ValueError("target dimensions must be positive")
        if not math.isfinite(self.outer_scale):
            raise ValueError("target outer scale must be finite")

    def factor_elements(self, branch: str) -> tuple[int, int]:
        rank = self.shared_rank if branch == "shared" else self.private_rank
        if branch not in ("shared", "private"):
            raise ValueError("branch must be shared or private")
        return rank * self.in_features, self.out_features * rank

    def as_metadata(self) -> dict[str, Any]:
        return {
            "canonical_name": self.canonical_name,
            "module_group": self.module_group,
            "in_features": self.in_features,
            "out_features": self.out_features,
            "old_rank": self.old_rank,
            "shared_rank": self.shared_rank,
            "private_rank": self.private_rank,
            "outer_scale": self.outer_scale,
        }


@dataclass(frozen=True)
class HybridFactorMapping:
    coordinate_block_id: str
    factor_id: str
    indices: torch.Tensor
    scales: torch.Tensor


def target_specs_from_registry(
    registry: Mapping[str, Any],
    modules: Iterable[str] = MODULE_GROUPS,
) -> list[HybridTargetSpec]:
    specs: list[HybridTargetSpec] = []
    selected_modules = tuple(modules)
    if any(module not in MODULE_GROUPS for module in selected_modules):
        raise ValueError("target registry contains an unknown module group")
    for module_group in selected_modules:
        section = registry["modules"][module_group]
        old_rank = int(section["rank"])
        if old_rank not in (4, 32) or old_rank % 2:
            raise ValueError("M4 v1 supports only frozen ranks 4 and 32")
        branch_rank = old_rank // 2
        for entry in section["targets"]:
            specs.append(
                HybridTargetSpec(
                    module_group=module_group,
                    canonical_name=str(entry["canonical_name"]),
                    old_rank=old_rank,
                    shared_rank=branch_rank,
                    private_rank=branch_rank,
                    in_features=int(entry["in_features"]),
                    out_features=int(entry["out_features"]),
                    outer_scale=1.0,
                )
            )
    specs.sort(key=lambda spec: spec.canonical_name.encode("utf-8"))
    names = [spec.canonical_name for spec in specs]
    if len(names) != len(set(names)):
        raise ValueError("M4 target registry contains duplicate canonical names")
    return specs


def validate_coordinate_dimensions(
    dimensions: Mapping[str, int],
    *,
    require_total_budget: bool = True,
) -> OrderedDict[str, int]:
    if set(dimensions) != set(COORDINATE_BLOCKS):
        raise ValueError("M4 coordinate blocks differ from the frozen four blocks")
    clean: OrderedDict[str, int] = OrderedDict()
    for block_id in COORDINATE_BLOCKS:
        value = dimensions[block_id]
        if isinstance(value, bool) or int(value) <= 0:
            raise ValueError("M4 coordinate dimensions must be positive integers")
        clean[block_id] = int(value)
    if require_total_budget and sum(clean.values()) != 4096:
        raise ValueError("M4 coordinate dimensions must sum exactly to 4096")
    return clean


def _block_for_branch(spec: HybridTargetSpec, branch: str) -> str:
    if branch == "shared":
        return "shared_coordinates"
    if branch == "private":
        return PRIVATE_BLOCK_BY_MODULE[spec.module_group]
    raise ValueError("branch must be shared or private")


def build_hybrid_factor_mappings(
    mapping_root: int,
    specs: Sequence[HybridTargetSpec],
    dimensions: Mapping[str, int],
) -> tuple[
    dict[tuple[str, str, str], HybridFactorMapping],
    dict[str, dict[str, Any]],
]:
    """Build normalized A/B maps separately for every coordinate block."""

    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    clean_dimensions = validate_coordinate_dimensions(
        dimensions, require_total_budget=False
    )
    names = [spec.canonical_name for spec in specs]
    if len(names) != len(set(names)):
        raise ValueError("duplicate target names are forbidden")

    counts = {
        block_id: torch.zeros(dimension, dtype=torch.int64)
        for block_id, dimension in clean_dimensions.items()
    }
    raw: dict[
        tuple[str, str, str],
        tuple[str, torch.Tensor, torch.Tensor],
    ] = {}
    for spec in specs:
        for branch in ("shared", "private"):
            block_id = _block_for_branch(spec, branch)
            a_elements, b_elements = spec.factor_elements(branch)
            for factor_id, element_count in (
                ("A", a_elements),
                ("B", b_elements),
            ):
                indices, signs = deterministic_mapping(
                    mapping_root,
                    spec.canonical_name,
                    spec.module_group,
                    block_id,
                    factor_id,
                    element_count,
                    clean_dimensions[block_id],
                )
                counts[block_id].scatter_add_(
                    0, indices, torch.ones_like(indices)
                )
                raw[(spec.canonical_name, branch, factor_id)] = (
                    block_id,
                    indices,
                    signs,
                )

    unused = {
        block_id: int((values == 0).sum().item())
        for block_id, values in counts.items()
        if torch.any(values == 0)
    }
    if unused:
        raise RuntimeError(
            f"mapping root {mapping_root} leaves M4 coordinates unused: {unused}"
        )

    mappings: dict[tuple[str, str, str], HybridFactorMapping] = {}
    for key, (block_id, indices, signs) in raw.items():
        scales = (
            signs.to(torch.float32)
            / counts[block_id][indices].to(torch.float32).sqrt()
        )
        mappings[key] = HybridFactorMapping(
            coordinate_block_id=block_id,
            factor_id=key[2],
            indices=indices,
            scales=scales,
        )

    digests = {
        block_id: hashlib.sha256(MAPPING_DIGEST_DOMAIN)
        for block_id in COORDINATE_BLOCKS
    }
    for spec in specs:
        for branch in ("shared", "private"):
            block_id = _block_for_branch(spec, branch)
            for factor_id in ("A", "B"):
                _, indices, signs = raw[
                    (spec.canonical_name, branch, factor_id)
                ]
                digest = digests[block_id]
                digest.update(_integer(mapping_root))
                digest.update(_string(spec.canonical_name))
                digest.update(_string(spec.module_group))
                digest.update(_string(block_id))
                digest.update(_string(factor_id))
                digest.update(
                    indices.numpy().astype("<u8", copy=False).tobytes()
                )
                digest.update(
                    signs.numpy().astype("i1", copy=False).tobytes()
                )

    statistics: dict[str, dict[str, Any]] = {}
    for block_id, values in counts.items():
        unique, frequencies = torch.unique(
            values, sorted=True, return_counts=True
        )
        histogram = {
            str(int(key)): int(value)
            for key, value in zip(
                unique.tolist(), frequencies.tolist(), strict=True
            )
        }
        histogram_bytes = json.dumps(
            histogram, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
        statistics[block_id] = {
            "dimension": int(values.numel()),
            "minimum": int(values.min().item()),
            "maximum": int(values.max().item()),
            "mean": float(values.to(torch.float64).mean().item()),
            "histogram_sha256": hashlib.sha256(
                histogram_bytes
            ).hexdigest(),
            "mapping_sha256": digests[block_id].hexdigest(),
        }
    return mappings, statistics


class HybridCoordinateStore(nn.Module):
    """Exactly four trainable M4 coordinate parameters in frozen order."""

    def __init__(self, dimensions: Mapping[str, int]) -> None:
        super().__init__()
        self.dimensions = validate_coordinate_dimensions(
            dimensions, require_total_budget=False
        )
        for block_id, dimension in self.dimensions.items():
            self.register_parameter(
                block_id,
                nn.Parameter(torch.zeros(dimension, dtype=torch.float32)),
            )

    def ordered(self) -> list[tuple[str, nn.Parameter]]:
        return [
            (block_id, getattr(self, block_id))
            for block_id in COORDINATE_BLOCKS
        ]


class HybridSubspaceLoRALinear(nn.Module):
    """A frozen Linear plus disjoint shared and module-private LoRA branches."""

    def __init__(
        self,
        base: nn.Linear,
        spec: HybridTargetSpec,
        coordinate_store: HybridCoordinateStore,
        mappings: Mapping[tuple[str, str], HybridFactorMapping],
        mapping_root: int,
    ) -> None:
        super().__init__()
        if not isinstance(base, nn.Linear):
            raise TypeError(f"{spec.canonical_name} is not nn.Linear")
        if (base.in_features, base.out_features) != (
            spec.in_features,
            spec.out_features,
        ):
            raise ValueError(f"{spec.canonical_name} target shape is inconsistent")
        if set(mappings) != {
            ("shared", "A"),
            ("shared", "B"),
            ("private", "A"),
            ("private", "B"),
        }:
            raise ValueError("a target requires four distinct branch mappings")
        self.base = base
        for parameter in self.base.parameters():
            parameter.requires_grad = False
        self.spec = spec
        self.canonical_name = spec.canonical_name
        self.module_group = spec.module_group
        self.old_rank = spec.old_rank
        self.shared_rank = spec.shared_rank
        self.private_rank = spec.private_rank
        self.outer_scale = float(spec.outer_scale)
        self._coordinate_store_ref = weakref.ref(coordinate_store)
        self.shared_block_id = "shared_coordinates"
        self.private_block_id = PRIVATE_BLOCK_BY_MODULE[spec.module_group]

        for branch, block_id, rank in (
            ("shared", self.shared_block_id, spec.shared_rank),
            ("private", self.private_block_id, spec.private_rank),
        ):
            self.register_buffer(
                f"{branch}_a0",
                deterministic_a0(
                    mapping_root,
                    spec.canonical_name,
                    spec.module_group,
                    block_id,
                    rank,
                    spec.in_features,
                ),
                persistent=False,
            )
            for factor_id in ("A", "B"):
                mapping = mappings[(branch, factor_id)]
                if mapping.coordinate_block_id != block_id:
                    raise ValueError("mapping coordinate block crosses branches")
                prefix = f"{branch}_{factor_id.lower()}"
                self.register_buffer(
                    f"{prefix}_indices",
                    mapping.indices,
                    persistent=False,
                )
                self.register_buffer(
                    f"{prefix}_scales",
                    mapping.scales,
                    persistent=False,
                )

    @property
    def weight(self) -> torch.Tensor:
        return self.base.weight

    @property
    def bias(self) -> torch.Tensor | None:
        return self.base.bias

    def _store(self) -> HybridCoordinateStore:
        store = self._coordinate_store_ref()
        if store is None:
            raise RuntimeError("M4 coordinate store was destroyed")
        return store

    def _factors_from(
        self, branch: str, coordinates: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if branch == "shared":
            rank = self.shared_rank
            a0 = self.shared_a0
            a_indices = self.shared_a_indices
            a_scales = self.shared_a_scales
            b_indices = self.shared_b_indices
            b_scales = self.shared_b_scales
        elif branch == "private":
            rank = self.private_rank
            a0 = self.private_a0
            a_indices = self.private_a_indices
            a_scales = self.private_a_scales
            b_indices = self.private_b_indices
            b_scales = self.private_b_scales
        else:
            raise ValueError("branch must be shared or private")
        a_delta = coordinates[a_indices] * a_scales
        b = coordinates[b_indices] * b_scales
        a = a0 + a_delta.view(rank, self.spec.in_features)
        return a, b.view(self.spec.out_features, rank)

    def branch_factors(
        self, branch: str
    ) -> tuple[torch.Tensor, torch.Tensor]:
        store = self._store()
        block_id = (
            self.shared_block_id if branch == "shared" else self.private_block_id
        )
        return self._factors_from(branch, getattr(store, block_id))

    def delta_weight(
        self,
        shared_coordinates: torch.Tensor | None = None,
        private_coordinates: torch.Tensor | None = None,
    ) -> torch.Tensor:
        store = self._store()
        shared_value = (
            getattr(store, self.shared_block_id)
            if shared_coordinates is None
            else shared_coordinates
        )
        private_value = (
            getattr(store, self.private_block_id)
            if private_coordinates is None
            else private_coordinates
        )
        shared_a, shared_b = self._factors_from("shared", shared_value)
        private_a, private_b = self._factors_from("private", private_value)
        branch_sum = shared_b @ shared_a + private_b @ private_a
        return self.outer_scale * branch_sum

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        base_output = F.linear(inputs, self.base.weight, self.base.bias)
        shared_a, shared_b = self.branch_factors("shared")
        private_a, private_b = self.branch_factors("private")
        shared_update = F.linear(F.linear(inputs, shared_a), shared_b)
        private_update = F.linear(F.linear(inputs, private_a), private_b)
        # The old target scale is deliberately applied once, after summing
        # the two independent branches.
        update = self.outer_scale * (shared_update + private_update)
        return base_output + update


def _resolve_parent(
    root: nn.Module, canonical_name: str
) -> tuple[nn.Module, str]:
    components = canonical_name.split(".")
    parent: nn.Module = root
    for component in components[:-1]:
        parent = (
            parent[int(component)]  # type: ignore[index]
            if component.isdigit()
            else getattr(parent, component)
        )
    return parent, components[-1]


def _get_child(parent: nn.Module, name: str) -> nn.Module:
    return (
        parent[int(name)]  # type: ignore[index]
        if name.isdigit()
        else getattr(parent, name)
    )


def _set_child(parent: nn.Module, name: str, child: nn.Module) -> None:
    if name.isdigit():
        parent[int(name)] = child  # type: ignore[index]
    else:
        setattr(parent, name, child)


def freeze_all_parameters(model: nn.Module) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = False


def _storage_identity(parameter: nn.Parameter) -> tuple[Any, ...]:
    storage = parameter.untyped_storage()
    return (
        str(parameter.device),
        storage.data_ptr(),
        storage.nbytes(),
    )


def validate_target_aliases(
    model: nn.Module, specs: Sequence[HybridTargetSpec]
) -> dict[str, Any]:
    """Reject duplicate target modules, Parameters, or backing storages."""

    module_owners: dict[int, str] = {}
    parameter_owners: dict[int, str] = {}
    storage_owners: dict[tuple[Any, ...], str] = {}
    checked_parameters = 0
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        if not isinstance(child, nn.Linear):
            raise TypeError(f"{spec.canonical_name} is not a bare nn.Linear")
        module_id = id(child)
        if module_id in module_owners:
            raise ValueError(
                "target module alias: "
                f"{module_owners[module_id]} and {spec.canonical_name}"
            )
        module_owners[module_id] = spec.canonical_name
        for local_name, parameter in child.named_parameters(recurse=False):
            owner = f"{spec.canonical_name}.{local_name}"
            if id(parameter) in parameter_owners:
                raise ValueError(
                    "target Parameter alias: "
                    f"{parameter_owners[id(parameter)]} and {owner}"
                )
            parameter_owners[id(parameter)] = owner
            storage_id = _storage_identity(parameter)
            if storage_id in storage_owners:
                raise ValueError(
                    "target storage alias: "
                    f"{storage_owners[storage_id]} and {owner}"
                )
            storage_owners[storage_id] = owner
            checked_parameters += 1
    return {
        "target_module_count": len(module_owners),
        "target_parameter_count": checked_parameters,
        "target_module_aliases": 0,
        "target_parameter_aliases": 0,
        "target_storage_aliases": 0,
    }


def inject_hybrid_subspace_lora(
    model: nn.Module,
    mapping_root: int,
    registry: Mapping[str, Any],
    dimensions: Mapping[str, int],
) -> dict[str, Any]:
    """Freeze a bare model and install the Phase 4 M4 adapter."""

    if hasattr(model, "m4_coordinates"):
        raise ValueError("model already contains an M4 coordinate store")
    specs = target_specs_from_registry(registry)
    alias_receipt = validate_target_aliases(model, specs)
    clean_dimensions = validate_coordinate_dimensions(dimensions)
    mappings, statistics = build_hybrid_factor_mappings(
        mapping_root, specs, clean_dimensions
    )
    freeze_all_parameters(model)
    store = HybridCoordinateStore(clean_dimensions)
    model.m4_coordinates = store  # type: ignore[attr-defined]
    wrapped_names: list[str] = []
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        base = _get_child(parent, child_name)
        target_mappings = {
            (branch, factor_id): mappings[
                (spec.canonical_name, branch, factor_id)
            ]
            for branch in ("shared", "private")
            for factor_id in ("A", "B")
        }
        wrapper = HybridSubspaceLoRALinear(
            base=base,  # type: ignore[arg-type]
            spec=spec,
            coordinate_store=store,
            mappings=target_mappings,
            mapping_root=mapping_root,
        )
        _set_child(parent, child_name, wrapper)
        wrapped_names.append(spec.canonical_name)
    if hasattr(model, "vision_encoder"):
        model.vision_encoder.stage2_gradient_enabled = True
    metadata = {
        "model_group": M4_MODEL_GROUP,
        "parameterization_schema": "phase4-m4-hybrid-subspace-lora-v1",
        "mapping_root": mapping_root,
        "mapping_domain": MAPPING_DOMAIN,
        "a0_domain": A0_DOMAIN,
        "coordinate_dimensions": dict(clean_dimensions),
        "coordinate_block_order": list(COORDINATE_BLOCKS),
        "wrapped_names": wrapped_names,
        "targets": [spec.as_metadata() for spec in specs],
        "mapping_statistics": statistics,
        "alias_validation": alias_receipt,
        "delta_formula": (
            "outer_scale*(B_shared@A_shared+B_private@A_private)"
        ),
        "outer_scale_application": "once_after_branch_sum",
    }
    model.m4_adapter = metadata  # type: ignore[attr-defined]
    return metadata


def m4_coordinate_parameters(
    model: nn.Module,
) -> list[tuple[str, nn.Parameter]]:
    metadata = getattr(model, "m4_adapter", None)
    store = getattr(model, "m4_coordinates", None)
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("model_group") != M4_MODEL_GROUP
        or not isinstance(store, HybridCoordinateStore)
    ):
        raise ValueError("model has no valid M4 adapter")
    parameters = store.ordered()
    if tuple(name for name, _ in parameters) != COORDINATE_BLOCKS:
        raise RuntimeError("M4 coordinate order changed")
    return parameters


def m4_coordinate_state(model: nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: parameter.detach().cpu().to(torch.float32).contiguous().clone()
        for name, parameter in m4_coordinate_parameters(model)
    }


def load_m4_coordinate_state(
    model: nn.Module, values: Mapping[str, torch.Tensor]
) -> None:
    expected = dict(m4_coordinate_parameters(model))
    if set(values) != set(expected):
        raise ValueError("M4 coordinate state does not contain exactly four blocks")
    with torch.no_grad():
        for name, destination in expected.items():
            source = values[name].detach().to(
                device=destination.device, dtype=torch.float32
            )
            if source.shape != destination.shape:
                raise ValueError(f"M4 coordinate shape mismatch for {name}")
            destination.copy_(source)


def iter_hybrid_layers(
    model: nn.Module,
) -> list[HybridSubspaceLoRALinear]:
    layers = [
        module
        for module in model.modules()
        if isinstance(module, HybridSubspaceLoRALinear)
    ]
    return sorted(layers, key=lambda layer: layer.canonical_name.encode("utf-8"))
