"""Configurable M2/M3 coordinate stores built from frozen Stage 2 primitives."""

from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from model.global_subspace_lora import (
    GROUP_DIMENSIONS,
    MAPPING_ROOTS,
    FactorMapping,
    HashedLoRALinear,
    TargetSpec,
    _coordinate_group,
    _get_child,
    _resolve_parent,
    _set_child,
    _string,
    build_factor_mappings,
    deterministic_mapping,
    freeze_all_parameters,
    load_coordinate_state,
    target_specs,
)


class ConfigurableCoordinateStore(nn.Module):
    def __init__(self, model_group: str, dimensions: Mapping[str, int]) -> None:
        super().__init__()
        if model_group not in ("M2", "M3"):
            raise ValueError("budget coordinate stores apply only to M2 and M3")
        expected_names = (
            ("vision", "projector", "language")
            if model_group == "M2"
            else ("shared",)
        )
        if set(dimensions) != set(expected_names):
            raise ValueError(
                f"{model_group} coordinate group names are invalid"
            )
        clean = OrderedDict()
        for name in expected_names:
            dimension = dimensions[name]
            if isinstance(dimension, bool) or int(dimension) <= 0:
                raise ValueError("coordinate dimensions must be positive")
            clean[name] = int(dimension)
        self.model_group = model_group
        self.dimensions = clean
        self.coordinates = nn.ParameterDict(
            {
                name: nn.Parameter(torch.zeros(dimension, dtype=torch.float32))
                for name, dimension in clean.items()
            }
        )

    def ordered(self) -> list[tuple[str, nn.Parameter]]:
        return [(name, self.coordinates[name]) for name in self.dimensions]


def build_factor_mappings_for_dimensions(
    model_group: str,
    mapping_root: int,
    specs: Sequence[TargetSpec],
    dimensions: Mapping[str, int],
) -> tuple[dict[tuple[str, str], FactorMapping], dict[str, dict[str, Any]]]:
    """Frozen SHA mapping with dimensions supplied by a predeclared budget."""

    if model_group not in ("M2", "M3") or mapping_root not in MAPPING_ROOTS:
        raise ValueError("invalid budget mapping identity")
    expected_names = (
        ("vision", "projector", "language")
        if model_group == "M2"
        else ("shared",)
    )
    if set(dimensions) != set(expected_names):
        raise ValueError("budget mapping dimension groups are invalid")
    dimensions = OrderedDict(
        (name, int(dimensions[name])) for name in expected_names
    )
    if any(dimension <= 0 for dimension in dimensions.values()):
        raise ValueError("budget mapping dimensions must be positive")

    raw: dict[
        tuple[str, str], tuple[str, torch.Tensor, torch.Tensor]
    ] = {}
    counts = {
        group: torch.zeros(dimension, dtype=torch.int64)
        for group, dimension in dimensions.items()
    }
    for spec in specs:
        group = _coordinate_group(model_group, spec)
        for factor_name, elements in (
            ("A", spec.a_elements),
            ("B", spec.b_elements),
        ):
            indices, signs = deterministic_mapping(
                mapping_root,
                spec.canonical_name,
                factor_name,
                elements,
                dimensions[group],
            )
            counts[group].scatter_add_(
                0, indices, torch.ones_like(indices)
            )
            raw[(spec.canonical_name, factor_name)] = (
                group,
                indices,
                signs,
            )
    unused = {
        group: int((values == 0).sum().item())
        for group, values in counts.items()
        if torch.any(values == 0)
    }
    if unused:
        raise RuntimeError(
            f"mapping root {mapping_root} leaves unused {model_group} "
            f"coordinates: {unused}"
        )

    mappings = {}
    for key, (group, indices, signs) in raw.items():
        scales = (
            signs.to(torch.float32)
            / counts[group][indices].to(torch.float32).sqrt()
        )
        mappings[key] = FactorMapping(indices=indices, scales=scales)

    mapping_digests = {
        group: hashlib.sha256(b"stage2-factor-mapping-v1\0")
        for group in counts
    }
    for spec in specs:
        group = _coordinate_group(model_group, spec)
        for factor_name in ("A", "B"):
            _, indices, signs = raw[(spec.canonical_name, factor_name)]
            digest = mapping_digests[group]
            digest.update(_string(spec.canonical_name))
            digest.update(_string(factor_name))
            digest.update(
                indices.numpy().astype("<u8", copy=False).tobytes()
            )
            digest.update(signs.numpy().astype("i1", copy=False).tobytes())

    statistics: dict[str, dict[str, Any]] = {}
    for group, values in counts.items():
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
        statistics[group] = {
            "dimension": int(values.numel()),
            "minimum": int(values.min().item()),
            "maximum": int(values.max().item()),
            "mean": float(values.to(torch.float64).mean().item()),
            "histogram": histogram,
            "histogram_serialization": (
                "canonical JSON object count->frequency"
            ),
            "histogram_sha256": hashlib.sha256(
                histogram_bytes
            ).hexdigest(),
            "mapping_sha256": mapping_digests[group].hexdigest(),
        }
    return mappings, statistics


def reconfigure_budget_adapter(
    model: nn.Module,
    model_group: str,
    mapping_root: int,
    registry: Mapping[str, Any],
    dimensions: Mapping[str, int],
) -> dict[str, Any]:
    """Replace only the old coordinate store/mappings, preserving every base."""

    if model_group not in ("M2", "M3"):
        raise ValueError("only M2/M3 support budget reconfiguration")
    metadata = getattr(model, "stage2_adapter", None)
    if not isinstance(metadata, Mapping) or metadata.get("model_group") != model_group:
        raise ValueError("model does not contain the expected Stage 2 adapter")
    specs = target_specs(registry, ("vision", "projector", "language"))
    expected_names = [spec.canonical_name for spec in specs]
    if list(metadata.get("wrapped_names", [])) != expected_names:
        raise ValueError("existing wrapped target order differs from registry")

    first_parameter = next(model.parameters())
    device = first_parameter.device
    dtype = first_parameter.dtype
    bases: dict[str, nn.Linear] = {}
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        if not isinstance(child, HashedLoRALinear):
            raise TypeError(f"{spec.canonical_name} is not HashedLoRALinear")
        bases[spec.canonical_name] = child.base
        _set_child(parent, child_name, child.base)
    if hasattr(model, "stage2_coordinates"):
        delattr(model, "stage2_coordinates")

    freeze_all_parameters(model)
    store = ConfigurableCoordinateStore(model_group, dimensions)
    model.stage2_coordinates = store  # type: ignore[attr-defined]
    mappings, statistics = build_factor_mappings_for_dimensions(
        model_group, mapping_root, specs, dimensions
    )
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        group = _coordinate_group(model_group, spec)
        wrapper = HashedLoRALinear(
            base=bases[spec.canonical_name],
            spec=spec,
            coordinate_store=store,
            coordinate_group=group,
            a_mapping=mappings[(spec.canonical_name, "A")],
            b_mapping=mappings[(spec.canonical_name, "B")],
        )
        _set_child(parent, child_name, wrapper)
    if hasattr(model, "vision_encoder"):
        model.vision_encoder.stage2_gradient_enabled = True
    model.stage2_adapter = {  # type: ignore[attr-defined]
        "model_group": model_group,
        "mapping_root": mapping_root,
        "wrapped_names": expected_names,
        "mapping_statistics": statistics,
        "coordinate_dimensions": dict(dimensions),
        "comparison_label": (
            "equal_coordinate_budget_not_equal_description_length"
        ),
    }
    model.to(device=device, dtype=dtype)
    return model.stage2_adapter  # type: ignore[attr-defined]


def check_current_mapping_equivalence(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    checks = []
    specs = target_specs(registry, ("vision", "projector", "language"))
    for model_group in ("M2", "M3"):
        dimensions = GROUP_DIMENSIONS[model_group]
        for root in MAPPING_ROOTS:
            old_mappings, old_statistics = build_factor_mappings(
                model_group, root, specs
            )
            new_mappings, new_statistics = (
                build_factor_mappings_for_dimensions(
                    model_group, root, specs, dimensions
                )
            )
            if old_statistics != new_statistics:
                raise AssertionError("current mapping statistics differ")
            for key in old_mappings:
                if not torch.equal(
                    old_mappings[key].indices, new_mappings[key].indices
                ) or not torch.equal(
                    old_mappings[key].scales, new_mappings[key].scales
                ):
                    raise AssertionError(
                        f"current mapping tensor differs: {model_group}/{root}/{key}"
                    )
            checks.append(
                {
                    "method": model_group,
                    "mapping_root": root,
                    "coordinate_dimensions": dict(dimensions),
                    "mapping_tensor_equivalence": "exact",
                    "statistics_equivalence": "exact",
                }
            )
    return {"status": "passed", "checks": checks}


def check_current_model_construction_equivalence(
    model: nn.Module,
    model_group: str,
    mapping_root: int,
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare every reconstructed A/B factor before and after reconfiguration."""

    dimensions = GROUP_DIMENSIONS[model_group]
    coordinates = {}
    for group_index, (name, parameter) in enumerate(
        model.stage2_coordinates.ordered()  # type: ignore[attr-defined]
    ):
        value = torch.linspace(
            -0.25 - group_index * 0.01,
            0.25 + group_index * 0.01,
            parameter.numel(),
            device=parameter.device,
            dtype=parameter.dtype,
        )
        with torch.no_grad():
            parameter.copy_(value)
        coordinates[name] = parameter.detach().cpu().clone()
    specs = target_specs(registry, ("vision", "projector", "language"))
    before = {}
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        before[spec.canonical_name] = tuple(
            value.detach().cpu().clone() for value in child.factors()
        )
    reconfigure_budget_adapter(
        model, model_group, mapping_root, registry, dimensions
    )
    load_coordinate_state(model, coordinates)
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        after = tuple(value.detach().cpu() for value in child.factors())
        if any(
            not torch.equal(left, right)
            for left, right in zip(
                before[spec.canonical_name], after, strict=True
            )
        ):
            raise AssertionError(
                f"current reconstructed factors differ: {spec.canonical_name}"
            )
    return {
        "status": "passed",
        "method": model_group,
        "mapping_root": mapping_root,
        "coordinate_dimensions": dict(dimensions),
        "wrapped_target_count": len(specs),
        "reconstructed_factor_equivalence": "exact",
    }
