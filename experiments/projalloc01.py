"""Frozen constants and model construction for PROJALLOC-01."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3_module_marginal_budget_v1.preflight import (
    fixed_projection_preflight,
)
from experiments.phase3_private_vs_shared_v1.adapter_runtime import build_mappings
from experiments.phase3_private_vs_shared_v1.parameterization import (
    CoordinateStore,
    assert_storage_contract,
)
from experiments.stage2_model import build_stage2_model
from experiments.stage2_protocol import (
    Stage2Protocol,
    load_target_registry,
    sha256_file,
)
from model.global_subspace_lora import (
    HashedLoRALinear,
    _get_child,
    _resolve_parent,
    _set_child,
    coordinate_parameters,
    freeze_all_parameters,
    target_specs,
)


CANDIDATE = "PROJALLOC-01"
ROUND = 1
CONDITIONS = ("current-allocation", "projector-dominant")
MAPPING_ROOTS = (43201, 43202, 43203)
PILOT_ROOT = 43201
BOOTSTRAP_ROOT = 43101
TOTAL_COORDINATES = 4_096
MAPPING_FACTOR_COUNT = 22
DATA_CONDITION = "visual-necessary"
EXPECTED_DIMENSIONS = {
    "current-allocation": {
        "vision": 582,
        "projector": 2_327,
        "language": 1_187,
    },
    "projector-dominant": {
        "vision": 1,
        "projector": 4_094,
        "language": 1,
    },
}
PREPARED_SHA256 = {
    "data_audit.json": (
        "26999a4451bc094ce6e148bcb1481d44efc5f9da58d9c727609d3b67d7400bea"
    ),
    "cvbench_audit.json": (
        "33360a8d0e54ecf3b250e6c581af3b5ee51d790219aae94aa88b9b48d1f7b43a"
    ),
    "train_injection_manifest.json": (
        "aca223f139f5e16c76a2a70b4fe71e8c85d6db44b3fa7eb883fd3b9aed1df8d7"
    ),
    "heldout_rotation_manifest.json": (
        "131be931c243b863b91121664b8e60db817d82a234d4fe3c26d206531f8311cf"
    ),
    "cvbench_manifest.json": (
        "32b9b6212e2e3578e447d9d73c33e08d8296ab7038f4b7c6e8be0e7c750f2949"
    ),
}
TRAIN_PARQUET_SHA256 = (
    "52cd2672a60c1dcf834ad8795585412b8f0c96ac9f921d83bfd353e1e5628ee5"
)


class CandidateCoordinateStore(CoordinateStore):
    """Private store with the Stage 2 coordinate-state compatibility method."""

    def ordered(self):
        return list(self.coordinates.items())


def dimensions_for(condition: str) -> dict[str, int]:
    if condition not in CONDITIONS:
        raise ValueError("unknown PROJALLOC-01 condition")
    dimensions = dict(EXPECTED_DIMENSIONS[condition])
    if tuple(dimensions) != ("vision", "projector", "language"):
        raise AssertionError("coordinate dimension order differs from private store")
    if sum(dimensions.values()) != TOTAL_COORDINATES:
        raise AssertionError("allocation does not total 4,096 coordinates")
    return dimensions


def verify_prepared_dir(prepared_dir: str | Path) -> dict[str, str]:
    prepared = Path(prepared_dir).resolve()
    observed = {}
    for name, expected in PREPARED_SHA256.items():
        path = prepared / name
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"frozen prepared artifact differs: {name}")
        observed[name] = actual
    audit = json.loads(
        (prepared / "data_audit.json").read_text(encoding="utf-8")
    )
    info = audit["data"][DATA_CONDITION]
    parquet = Path(info["path"]).resolve()
    if (
        int(info["rows"]) != 11_008
        or info["sha256"] != TRAIN_PARQUET_SHA256
        or sha256_file(parquet) != TRAIN_PARQUET_SHA256
    ):
        raise ValueError("frozen visual-necessary parquet differs from plan")
    observed["train_visual_necessary.parquet"] = TRAIN_PARQUET_SHA256
    return observed


def projection_preflight(condition: str, mapping_root: int) -> dict[str, Any]:
    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is outside PROJALLOC-01")
    dimensions = dimensions_for(condition)
    receipt = fixed_projection_preflight(dimensions, seeds=(mapping_root,))
    root = receipt["roots"][str(mapping_root)]
    if (
        receipt["all_roots_reproducible"] is not True
        or receipt["all_coordinates_used"] is not True
        or any(
            value["unused_coordinate_count"] != 0
            for value in root["module_usage"].values()
        )
    ):
        raise RuntimeError("fixed projection preflight failed")
    return {
        **receipt,
        "condition": condition,
        "coordinate_dimensions": dimensions,
        "total_coordinates": sum(dimensions.values()),
        "mapping_factor_count": MAPPING_FACTOR_COUNT,
    }


def build_model(
    protocol: Stage2Protocol,
    mapping_root: int,
    dimensions: Mapping[str, int],
    *,
    device: str | torch.device,
):
    """Build arbitrary private dimensions without broadening Stage 2 root authority."""
    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is outside PROJALLOC-01")
    normalized = OrderedDict(
        (name, int(dimensions[name]))
        for name in ("vision", "projector", "language")
    )
    if dict(normalized) not in EXPECTED_DIMENSIONS.values():
        raise ValueError("dimensions are outside the two frozen allocations")
    if sum(normalized.values()) != TOTAL_COORDINATES:
        raise ValueError("PROJALLOC-01 requires exactly 4,096 coordinates")

    # The temporary legacy wrappers are removed before the candidate mappings
    # are created. An already-authorized Stage 2 root is therefore used only
    # to construct and validate the identical frozen base.
    model = build_stage2_model(
        "M2",
        protocol,
        BOOTSTRAP_ROOT,
        device="cpu",
        dtype=torch.float32,
    )
    bootstrap_adapter = dict(model.stage2_adapter)
    specs = target_specs(
        load_target_registry(), ("vision", "projector", "language")
    )
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

    store = CandidateCoordinateStore("P", normalized)
    assert_storage_contract(store)
    model.stage2_coordinates = store
    mappings = build_mappings("P", mapping_root, specs, normalized)
    if len(mappings) != MAPPING_FACTOR_COUNT:
        raise RuntimeError("candidate mapping count differs from 22")
    for spec in specs:
        parent, child_name = _resolve_parent(model, spec.canonical_name)
        _set_child(
            parent,
            child_name,
            HashedLoRALinear(
                base=bases[spec.canonical_name],
                spec=spec,
                coordinate_store=store,
                coordinate_group=spec.module_group,
                a_mapping=mappings[(spec.canonical_name, "A")],
                b_mapping=mappings[(spec.canonical_name, "B")],
            ),
        )
    model.stage2_adapter = {
        "model_group": "M2",
        "structure": "P",
        "mapping_root": mapping_root,
        "base_construction_mapping_root": BOOTSTRAP_ROOT,
        "base_construction_root_affects_candidate_mapping": False,
        "coordinate_dimensions": dict(normalized),
        "wrapped_names": [spec.canonical_name for spec in specs],
        "mapping_factor_count": len(mappings),
        "initial_llm_sha256": bootstrap_adapter["initial_llm_sha256"],
        "initial_llm_load": bootstrap_adapter["initial_llm_load"],
        "protocol": bootstrap_adapter["protocol"],
    }
    model.vision_encoder.stage2_gradient_enabled = True
    model.to(device=device, dtype=torch.float32)
    trainable = [
        (name, parameter)
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    ]
    coordinate_count = sum(
        parameter.numel() for _, parameter in coordinate_parameters(model)
    )
    if (
        sum(parameter.numel() for _, parameter in trainable)
        != coordinate_count
        or coordinate_count != TOTAL_COORDINATES
    ):
        raise RuntimeError("trainable parameters differ from frozen coordinates")
    return model


TRAINING_SPEC = {
    "candidate": CANDIDATE,
    "round": ROUND,
    "conditions": CONDITIONS,
    "mapping_roots": MAPPING_ROOTS,
    "dimensions_by_condition": EXPECTED_DIMENSIONS,
    "data_condition_by_condition": {
        condition: DATA_CONDITION for condition in CONDITIONS
    },
    "model_builder": build_model,
    "projection_preflight": projection_preflight,
}


SCORING_SPEC = {
    "candidate": CANDIDATE,
    "round": ROUND,
    "conditions": CONDITIONS,
    "mapping_roots": MAPPING_ROOTS,
    "dimensions_by_condition": EXPECTED_DIMENSIONS,
    "model_builder": build_model,
}
