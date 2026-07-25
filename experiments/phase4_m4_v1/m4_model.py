"""Construct and load Phase 4 M4 models without changing frozen builders."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

import torch
from torch import nn

from experiments.phase4_m4_v1.m4_configs import (
    REPO_ROOT,
    canonical_json_bytes,
    sha256_file,
    validate_config,
)
from experiments.stage2_model import build_stage2_model
from experiments.stage2_protocol import Stage2Protocol, load_target_registry
from model.global_subspace_lora import HashedLoRALinear
from model.hybrid_subspace_lora import (
    HybridSubspaceLoRALinear,
    inject_hybrid_subspace_lora,
    load_m4_coordinate_state,
    m4_coordinate_parameters,
    m4_coordinate_state,
    target_specs_from_registry,
)


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


def unwrap_frozen_m3_adapter(
    model: nn.Module, registry: Mapping[str, Any]
) -> dict[str, Any]:
    """Remove the temporary frozen M3 wrapper while preserving every base."""

    metadata = getattr(model, "stage2_adapter", None)
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("model_group") != "M3"
    ):
        raise ValueError("M4 construction requires a freshly built M3 base")
    specs = target_specs_from_registry(registry)
    expected_names = [spec.canonical_name for spec in specs]
    if list(metadata.get("wrapped_names", ())) != expected_names:
        raise ValueError("temporary M3 target order differs from registry")
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        child = _get_child(parent, child_name)
        if not isinstance(child, HashedLoRALinear):
            raise TypeError(
                f"temporary target {spec.canonical_name} is not frozen M3 LoRA"
            )
        _set_child(parent, child_name, child.base)
    if not hasattr(model, "stage2_coordinates"):
        raise ValueError("temporary M3 coordinate store is missing")
    delattr(model, "stage2_coordinates")
    delattr(model, "stage2_adapter")
    return {
        "source_builder_group": "M3",
        "unwrapped_target_count": len(specs),
        "unwrapped_names": expected_names,
        "temporary_coordinates_discarded": True,
        "base_modules_preserved": True,
    }


def _normalized_mapping_summary(
    statistics: Mapping[str, Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    return {
        block_id: {
            "dimension": int(row["dimension"]),
            "minimum_usage": int(row["minimum"]),
            "maximum_usage": int(row["maximum"]),
            "mean_usage": float(row["mean"]),
            "usage_histogram_sha256": str(row["histogram_sha256"]),
            "mapping_sha256": str(row["mapping_sha256"]),
        }
        for block_id, row in statistics.items()
    }


def _load_embedded_stage2_protocol(
    config: Mapping[str, Any], *, verify_assets: bool
) -> Stage2Protocol:
    reference = config["base_assets"]["stage2_protocol"]
    path = REPO_ROOT / reference["relative_path"]
    if sha256_file(path) != reference["sha256"]:
        raise ValueError("embedded Stage 2 protocol hash does not match")
    protocol = Stage2Protocol.load(path)
    if protocol.payload["protocol_id"] != reference["protocol_id"]:
        raise ValueError("embedded Stage 2 protocol ID does not match")
    if verify_assets:
        protocol.verify_immutable_inputs()
    return protocol


def build_m4_model(
    config: Mapping[str, Any],
    protocol: Stage2Protocol | None = None,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
    verify_assets: bool = True,
) -> nn.Module:
    """Build one exact M4 config through a disposable frozen M3 base."""

    validate_config(config)
    selected_protocol = protocol or _load_embedded_stage2_protocol(
        config, verify_assets=verify_assets
    )
    reference = config["base_assets"]["stage2_protocol"]
    if (
        selected_protocol.payload.get("protocol_id")
        != reference["protocol_id"]
    ):
        raise ValueError("supplied protocol differs from embedded asset ID")

    model = build_stage2_model(
        "M3",
        selected_protocol,
        int(config["mapping_root"]),
        device="cpu",
        dtype=torch.float32,
    )
    registry = load_target_registry()
    source_receipt = unwrap_frozen_m3_adapter(model, registry)
    adapter = inject_hybrid_subspace_lora(
        model,
        int(config["mapping_root"]),
        registry,
        config["coordinate_dimensions"],
    )
    if adapter["targets"] != config["target_registry"]["targets"]:
        raise RuntimeError("constructed M4 target structure differs from config")
    actual_mapping = _normalized_mapping_summary(
        adapter["mapping_statistics"]
    )
    if actual_mapping != config["mapping_summary"]:
        raise RuntimeError("constructed M4 mapping differs from config digest")
    adapter.update(
        {
            "config_id": config["config_id"],
            "canonical_config_sha256": hashlib.sha256(
                canonical_json_bytes(config)
            ).hexdigest(),
            "source_builder_receipt": source_receipt,
            "base_assets": config["base_assets"],
        }
    )
    model.to(device=device, dtype=dtype)

    coordinate_ids = {
        id(parameter) for _, parameter in m4_coordinate_parameters(model)
    }
    trainable = [
        (name, parameter)
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    ]
    if (
        len(trainable) != 4
        or {id(parameter) for _, parameter in trainable} != coordinate_ids
        or sum(parameter.numel() for _, parameter in trainable) != 4096
    ):
        raise RuntimeError("M4 trainable set is not exactly four coordinates")
    return model


def m4_model_structure_receipt(model: nn.Module) -> dict[str, Any]:
    layers = [
        module
        for module in model.modules()
        if isinstance(module, HybridSubspaceLoRALinear)
    ]
    layers.sort(key=lambda layer: layer.canonical_name.encode("utf-8"))
    return {
        "adapter": dict(model.m4_adapter),  # type: ignore[attr-defined]
        "coordinate_dimensions": {
            name: int(parameter.numel())
            for name, parameter in m4_coordinate_parameters(model)
        },
        "trainable_parameter_names": [
            name
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        ],
        "trainable_parameter_count": sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        ),
        "targets": [
            {
                **layer.spec.as_metadata(),
                "outer_scale_application": "once_after_branch_sum",
            }
            for layer in layers
        ],
    }


def load_m4_model_from_archive(
    archive: bytes,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
    verify_assets: bool = True,
) -> tuple[nn.Module, dict[str, Any]]:
    """Decode bytes, reconstruct the declared model, and load quantized state."""

    from experiments.phase4_m4_v1.mms2_v2 import decode_mms2_v2

    coordinates, metadata = decode_mms2_v2(archive)
    model = build_m4_model(
        metadata["config"],
        device=device,
        dtype=dtype,
        verify_assets=verify_assets,
    )
    load_m4_coordinate_state(model, coordinates)
    reloaded = m4_coordinate_state(model)
    if any(
        not torch.equal(reloaded[name], coordinates[name])
        for name in coordinates
    ):
        raise RuntimeError("decoded M4 coordinates changed during model load")
    return model, metadata
