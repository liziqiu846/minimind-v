"""Construct Stage 2 models from immutable assets and attach adapters."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Mapping, Sequence

import torch
from torch import nn

from experiments.stage2_protocol import Stage2Protocol, load_target_registry, sha256_file
from model.global_subspace_lora import (
    MAPPING_ROOTS,
    configure_m1_coordinates,
    coordinate_parameters,
    inject_hashed_lora,
    projector_base_receipt,
)
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM
from model.model_vlm import MiniMindVLM, VLMConfig


VLM_INITIAL_LLM_ALLOWED_MISSING_PREFIXES = ("vision_encoder.", "vision_proj.")


def validate_initial_llm_load(
    model_group: str,
    model: nn.Module,
    initial_state: Mapping[str, torch.Tensor],
    missing_keys: Sequence[str],
    unexpected_keys: Sequence[str],
) -> dict:
    """Reject every incomplete or non-exact language-model initialization."""
    unexpected = list(unexpected_keys)
    missing = list(missing_keys)
    if unexpected:
        raise ValueError(f"initial LLM has unexpected keys: {unexpected}")
    allowed_prefixes = () if model_group == "M0" else VLM_INITIAL_LLM_ALLOWED_MISSING_PREFIXES
    disallowed_missing = [
        key for key in missing if not key.startswith(allowed_prefixes)
    ]
    if disallowed_missing:
        raise ValueError(
            "initial LLM is incomplete outside separately constructed vision modules: "
            f"{disallowed_missing}"
        )
    model_state = model.state_dict()
    initial_absent = [key for key in initial_state if key not in model_state]
    if initial_absent:
        raise ValueError(f"initial LLM tensors are absent from model: {initial_absent}")
    mismatches = [
        key
        for key, tensor in initial_state.items()
        if not torch.equal(model_state[key].detach().cpu(), tensor.detach().cpu())
    ]
    if mismatches:
        raise ValueError(f"initial LLM tensors did not load exactly: {mismatches}")
    return {
        "initial_state_key_count": len(initial_state),
        "missing_key_count": len(missing),
        "allowed_missing_prefixes": list(allowed_prefixes),
        "unexpected_keys": unexpected,
        "exact_initial_tensor_match": True,
    }


def build_stage2_model(
    model_group: str,
    protocol: Stage2Protocol,
    mapping_root: int | None = None,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
) -> nn.Module:
    if model_group not in ("M0", "M1", "M2", "M3"):
        raise ValueError(f"unknown Stage 2 model group {model_group}")
    if model_group == "M1":
        if mapping_root is not None:
            raise ValueError("M1 does not use a mapping root")
    elif mapping_root not in MAPPING_ROOTS:
        raise ValueError("M0, M2, and M3 require a predeclared mapping root")

    model_config = protocol.payload["model"]
    common = dict(
        hidden_size=model_config["hidden_size"],
        num_hidden_layers=model_config["num_hidden_layers"],
        vocab_size=model_config["vocab_size"],
        use_moe=model_config["use_moe"],
        max_position_embeddings=protocol.payload["training"]["max_sequence_length"],
    )
    if model_group == "M0":
        model = MiniMindForCausalLM(MiniMindConfig(**common))
    else:
        projector_type = "subspace" if model_group == "M1" else "stage2_base"
        config = VLMConfig(
            **common,
            image_hidden_size=model_config["image_hidden_size"],
            image_token_len=model_config["image_token_count"],
            projector_type=projector_type,
            subspace_dim=4096,
            subspace_seed=model_config["projector_base"]["source_seed_layer_1"],
            subspace_train_norm=False,
        )
        model = MiniMindVLM(
            config=config,
            vision_model_path=str(protocol.asset_path("vision_encoder")),
        )
        if model.vision_encoder is None or model.processor is None:
            raise RuntimeError("immutable Stage 2 vision model could not be loaded")

    initial_path = protocol.asset_path("initial_llm")
    initial = torch.load(initial_path, map_location="cpu", weights_only=True)
    incompatible = model.load_state_dict(initial, strict=False)
    load_receipt = validate_initial_llm_load(
        model_group,
        model,
        initial,
        incompatible.missing_keys,
        incompatible.unexpected_keys,
    )
    if model_group == "M1":
        adapter = configure_m1_coordinates(model)
    else:
        adapter = inject_hashed_lora(
            model, model_group, int(mapping_root), load_target_registry()
        )
    model.stage2_adapter.update(  # type: ignore[attr-defined]
        {
            "initial_llm_sha256": sha256_file(initial_path),
            "initial_llm_load": load_receipt,
            "protocol": protocol.reference(),
        }
    )
    model.to(device=device, dtype=dtype)
    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    expected_parameters = sum(
        parameter.numel() for _, parameter in coordinate_parameters(model)
    )
    if sum(parameter.numel() for _, parameter in trainable) != expected_parameters:
        raise RuntimeError("parameters outside the Stage 2 coordinates are trainable")
    return model


def tensor_state_sha256(tensors: Mapping[str, torch.Tensor]) -> str:
    """Canonical hash for a small named tensor collection."""
    digest = hashlib.sha256(b"stage2-tensor-state-v1\0")
    for name in sorted(tensors, key=lambda value: value.encode("utf-8")):
        tensor = tensors[name].detach().cpu().contiguous()
        name_bytes = name.encode("utf-8")
        dtype_bytes = str(tensor.dtype).encode("ascii")
        raw = tensor.view(torch.uint8).numpy().tobytes()
        digest.update(struct.pack("<I", len(name_bytes)))
        digest.update(name_bytes)
        digest.update(struct.pack("<I", len(dtype_bytes)))
        digest.update(dtype_bytes)
        digest.update(struct.pack("<I", tensor.ndim))
        for dimension in tensor.shape:
            digest.update(struct.pack("<Q", dimension))
        digest.update(struct.pack("<Q", len(raw)))
        digest.update(raw)
    return digest.hexdigest()


def model_structure_receipt(model: nn.Module) -> dict:
    coordinates = coordinate_parameters(model)
    receipt = {
        "adapter": model.stage2_adapter,  # type: ignore[attr-defined]
        "coordinate_dimensions": {name: value.numel() for name, value in coordinates},
        "coordinate_state_sha256": tensor_state_sha256(dict(coordinates)),
        "trainable_parameter_names": [
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        ],
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
    }
    if hasattr(model, "vision_proj"):
        receipt["projector_base"] = projector_base_receipt(model)
    return receipt
