"""CPU legality preflight and immutable manifest freeze for curve sweeps."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import torch

from experiments.phase3_private_vs_shared_v1 import SEEDS
from experiments.phase3_private_vs_shared_v1.adapter_runtime import build_mappings
from experiments.stage2_protocol import (
    REPO_ROOT,
    Stage2Protocol,
    load_target_registry,
    sha256_file,
)
from model.global_subspace_lora import target_specs

from . import MODULES, PROTOCOL_VERSION, SEED_PLACEHOLDER
from .configs import (
    coordinate_dimensions,
    make_baseline,
    make_single_module_candidate,
)
from .curve_sweep import build_seed_placeholder_sweep_manifest
from .parameterization import (
    assert_storage_contract,
    build_candidate_model,
)
from .training import private_trainable_parameters

DEFAULT_STAGE2_PROTOCOL = REPO_ROOT / "experiments/stage2_protocol_v2.json"
DEFAULT_MANIFEST = Path(__file__).with_name("curve_sweep_manifest_9point.json")


def _mapping_sha256(mappings: Mapping[tuple[str, str], Any]) -> str:
    digest = hashlib.sha256(b"phase3-module-curve-fixed-mapping-v1\0")
    for name, factor in sorted(mappings):
        mapping = mappings[(name, factor)]
        for value in (name, factor):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(4, "little"))
            digest.update(encoded)
        indices = (
            mapping.indices.detach()
            .cpu()
            .contiguous()
            .numpy()
            .astype("<i8", copy=False)
        )
        scales = (
            mapping.scales.detach().cpu().contiguous().numpy().astype("<f4", copy=False)
        )
        digest.update(indices.tobytes())
        digest.update(scales.tobytes())
    return digest.hexdigest()


def _usage_statistics(
    mappings: Mapping[tuple[str, str], Any],
    specs: Sequence[Any],
    dimensions: Mapping[str, int],
) -> dict[str, dict[str, int]]:
    counts = {
        module: torch.zeros(dimensions[module], dtype=torch.int64) for module in MODULES
    }
    for spec in specs:
        for factor in ("A", "B"):
            indices = mappings[(spec.canonical_name, factor)].indices
            counts[spec.module_group].scatter_add_(0, indices, torch.ones_like(indices))
    return {
        module: {
            "coordinate_dimension": dimensions[module],
            "unused_coordinate_count": int((counts[module] == 0).sum().item()),
            "minimum_uses_per_coordinate": int(counts[module].min().item()),
            "maximum_uses_per_coordinate": int(counts[module].max().item()),
        }
        for module in MODULES
    }


def fixed_projection_preflight(
    dimensions: Mapping[str, int],
    *,
    seeds: Sequence[int] = SEEDS,
) -> dict[str, Any]:
    """Check coverage and byte-level reproducibility for every allowed seed."""
    normalized = coordinate_dimensions(dimensions)
    specs = target_specs(load_target_registry(), ("vision", "projector", "language"))
    roots = {}
    for seed in seeds:
        first = build_mappings("P", seed, specs, normalized)
        second = build_mappings("P", seed, specs, normalized)
        first_sha256 = _mapping_sha256(first)
        second_sha256 = _mapping_sha256(second)
        usage = _usage_statistics(first, specs, normalized)
        roots[str(seed)] = {
            "mapping_sha256": first_sha256,
            "repeated_mapping_sha256": second_sha256,
            "reproducible": first_sha256 == second_sha256,
            "module_usage": usage,
        }
        if first_sha256 != second_sha256:
            raise AssertionError(
                "fixed projection differs across identical constructions"
            )
        if any(receipt["unused_coordinate_count"] != 0 for receipt in usage.values()):
            raise RuntimeError("fixed projection leaves an unused coordinate")
    return {
        "validated_projection_roots": list(seeds),
        "all_roots_reproducible": True,
        "all_coordinates_used": True,
        "roots": roots,
    }


def _training_config(
    config: Mapping[str, Any],
    anchor_dimensions: Mapping[str, int],
    construction_seed: int,
) -> dict[str, Any]:
    baseline = make_baseline(
        f"{config['anchor_config']}-preflight-seed-{construction_seed}",
        anchor_dimensions,
        construction_seed,
    )
    if config["is_anchor"]:
        return baseline.as_training_config()
    candidate = make_single_module_candidate(
        baseline,
        str(config["target_module"]),
        int(config["coordinate_dimensions"][config["target_module"]]),
        config_id=f"{config['config_id']}-preflight-seed-{construction_seed}",
        allow_decrease=True,
    )
    return candidate.as_training_config()


def _model_construction_preflight(
    config: Mapping[str, Any],
    *,
    anchor_dimensions: Mapping[str, int],
    construction_seed: int,
    stage2: Stage2Protocol,
) -> dict[str, Any]:
    dimensions = coordinate_dimensions(config["coordinate_dimensions"])
    target_module = config["target_module"]
    non_target_match = all(
        dimensions[module] == anchor_dimensions[module]
        for module in MODULES
        if target_module is not None and module != target_module
    )
    if config["is_anchor"]:
        non_target_match = dimensions == anchor_dimensions
    if not non_target_match:
        raise ValueError("a non-target module differs from the P-4096 anchor")
    training_config = _training_config(config, anchor_dimensions, construction_seed)
    model = None
    try:
        model = build_candidate_model(training_config, stage2, device="cpu")
        store = model.stage2_coordinates
        assert_storage_contract(store)
        if dict(store.dimensions) != dimensions:
            raise AssertionError("constructed coordinate dimensions differ from config")
        coordinate_parameters = [store.for_module(module) for module in MODULES]
        private_objects = (
            len({id(parameter) for parameter in coordinate_parameters}) == 3
        )
        private_storage = (
            len(
                {
                    parameter.untyped_storage().data_ptr()
                    for parameter in coordinate_parameters
                }
            )
            == 3
        )
        if not private_objects or not private_storage:
            raise AssertionError("the three modules do not retain private parameters")
        trainable = private_trainable_parameters(model)
        trainable_names = sorted(
            name
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        )
        expected_names = sorted(
            f"stage2_coordinates.coordinates.{module}" for module in MODULES
        )
        trainable_count = sum(parameter.numel() for parameter in trainable)
        expected_count = sum(dimensions.values())
        if trainable_names != expected_names or trainable_count != expected_count:
            raise AssertionError("trainable parameter set differs from coordinates")
        return {
            "model_constructed": True,
            "construction_device": "cpu",
            "construction_seed": construction_seed,
            "target_dimension_legal": True,
            "non_target_modules_match_anchor": True,
            "three_module_parameters_private": True,
            "private_parameter_object_count": 3,
            "private_parameter_storage_count": 3,
            "trainable_parameter_names": trainable_names,
            "trainable_parameter_count": trainable_count,
            "expected_trainable_parameter_count": expected_count,
            "trainable_parameter_set_matches_expected": True,
        }
    finally:
        if model is not None:
            del model
        gc.collect()


def _nearest_legal_capacity(
    target_module: str,
    requested: int,
    anchor_dimensions: Mapping[str, int],
) -> dict[str, int] | None:
    registry = load_target_registry()
    maximum = int(registry["modules"][target_module]["factor_elements"])
    for distance in range(1, maximum + 1):
        candidates = (requested - distance, requested + distance)
        for candidate in candidates:
            if candidate <= 0 or candidate > maximum:
                continue
            dimensions = dict(anchor_dimensions)
            dimensions[target_module] = candidate
            try:
                fixed_projection_preflight(dimensions)
            except (AssertionError, RuntimeError, ValueError):
                continue
            return {
                "requested_capacity": requested,
                "nearest_legal_capacity": candidate,
                "distance": distance,
            }
    return None


def run_curve_preflight(
    plan: Mapping[str, Any],
    *,
    stage2_protocol_path: Path = DEFAULT_STAGE2_PROTOCOL,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Run every construction and projection invariant for unique configs."""
    if plan.get("seed") != SEED_PLACEHOLDER:
        raise ValueError("formal preflight plan must retain the seed placeholder")
    if int(plan.get("distinct_config_count", -1)) != 25:
        raise ValueError("formal nine-point preflight requires 25 distinct configs")
    stage2 = Stage2Protocol.load(stage2_protocol_path, require_frozen=True)
    anchor_dimensions = coordinate_dimensions(
        plan["anchor_config"]["coordinate_dimensions"]
    )
    construction_seed = SEEDS[0]
    receipts = []
    for index, config in enumerate(plan["configs"], start=1):
        receipt = {
            "config_id": config["config_id"],
            "curve_name": config["curve_name"],
            "target_module": config["target_module"],
            "coordinate_dimensions": dict(config["coordinate_dimensions"]),
            "status": "illegal",
            "checks": {},
            "error": None,
            "nearest_legal_capacity_candidate": None,
        }
        try:
            projection = fixed_projection_preflight(config["coordinate_dimensions"])
            construction = _model_construction_preflight(
                config,
                anchor_dimensions=anchor_dimensions,
                construction_seed=construction_seed,
                stage2=stage2,
            )
            receipt["checks"] = {
                **construction,
                "fixed_projection_reproducible": projection["all_roots_reproducible"],
                "unused_coordinates_absent": projection["all_coordinates_used"],
                "projection_roots": projection["roots"],
            }
            receipt["status"] = "legal"
        except (AssertionError, RuntimeError, TypeError, ValueError) as error:
            receipt["error"] = {
                "type": type(error).__name__,
                "message": str(error),
            }
            target_module = config["target_module"]
            if target_module is not None:
                requested = int(config["coordinate_dimensions"][target_module])
                receipt["nearest_legal_capacity_candidate"] = _nearest_legal_capacity(
                    target_module, requested, anchor_dimensions
                )
        receipts.append(receipt)
        if progress is not None:
            progress(
                f"{index:02d}/{len(plan['configs'])} "
                f"{config['config_id']}: {receipt['status']}"
            )
    illegal = [
        {
            "config_id": receipt["config_id"],
            "target_module": receipt["target_module"],
            "coordinate_dimensions": receipt["coordinate_dimensions"],
            "error": receipt["error"],
            "nearest_legal_capacity_candidate": receipt[
                "nearest_legal_capacity_candidate"
            ],
        }
        for receipt in receipts
        if receipt["status"] != "legal"
    ]
    return {
        "status": "passed" if not illegal else "failed",
        "distinct_configs_checked": len(receipts),
        "legal_config_count": len(receipts) - len(illegal),
        "illegal_config_count": len(illegal),
        "stage2_protocol": stage2.reference(),
        "model_construction_seed": construction_seed,
        "model_construction_seed_role": "preflight_only_not_formal_seed",
        "validated_projection_roots": list(SEEDS),
        "results": receipts,
        "illegal_configs": illegal,
    }


def _manifest_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write_frozen_manifest(path: Path, payload: Mapping[str, Any]) -> str:
    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    raw = _manifest_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    sidecar_raw = f"{digest}  {path.name}\n".encode("ascii")
    if path.exists() or sidecar.exists():
        if (
            path.is_file()
            and sidecar.is_file()
            and path.read_bytes() == raw
            and sidecar.read_bytes() == sidecar_raw
        ):
            return digest
        raise FileExistsError("frozen manifest or sidecar already exists and differs")
    path.write_bytes(raw)
    sidecar.write_bytes(sidecar_raw)
    return digest


def preflight_and_freeze(
    capacity_points: Mapping[str, Sequence[int]],
    *,
    output_path: Path = DEFAULT_MANIFEST,
    stage2_protocol_path: Path = DEFAULT_STAGE2_PROTOCOL,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Freeze only when all 25 distinct configurations pass CPU preflight."""
    plan = build_seed_placeholder_sweep_manifest(capacity_points)
    preflight = run_curve_preflight(
        plan,
        stage2_protocol_path=stage2_protocol_path,
        progress=progress,
    )
    if preflight["status"] != "passed":
        return {
            "manifest_frozen": False,
            "preflight": preflight,
        }
    payload = {
        **plan,
        "status": "frozen",
        "seed_policy": {
            "seed_placeholder": SEED_PLACEHOLDER,
            "formal_seed_unresolved": True,
            "allowed_fixed_projection_roots": list(SEEDS),
            "all_allowed_roots_preflighted": True,
        },
        "preflight": preflight,
        "execution_scope": {
            "formal_training_executed": False,
            "risk_evaluation_executed": False,
            "formal_codec_statistics_executed": False,
        },
    }
    digest = _write_frozen_manifest(output_path, payload)
    return {
        "manifest_frozen": True,
        "manifest_path": str(output_path.resolve()),
        "manifest_sha256": digest,
        "preflight": preflight,
    }


def verify_frozen_manifest(path: Path = DEFAULT_MANIFEST) -> str:
    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = sha256_file(path)
    expected_sidecar = f"{digest}  {path.name}\n"
    if sidecar.read_text(encoding="ascii") != expected_sidecar:
        raise ValueError("curve sweep manifest SHA-256 sidecar differs")
    if (
        payload.get("status") != "frozen"
        or payload.get("protocol_version") != PROTOCOL_VERSION
        or payload.get("seed") != SEED_PLACEHOLDER
        or payload.get("distinct_config_count") != 25
        or payload.get("preflight", {}).get("status") != "passed"
        or payload["preflight"].get("legal_config_count") != 25
        or payload["preflight"].get("illegal_config_count") != 0
    ):
        raise ValueError("curve sweep manifest does not contain a complete frozen pass")
    rebuilt = build_seed_placeholder_sweep_manifest(payload["capacity_points"])
    for field in (
        "protocol_id",
        "protocol_version",
        "anchor_config",
        "seed",
        "capacity_points",
        "distinct_config_count",
        "curve_point_membership_count",
        "configs",
        "curves",
        "curve_names",
    ):
        if payload[field] != rebuilt[field]:
            raise ValueError(f"frozen curve sweep manifest differs at {field}")
    config_ids = [config["config_id"] for config in payload["configs"]]
    if (
        len(config_ids) != len(set(config_ids))
        or sum(config["is_anchor"] for config in payload["configs"]) != 1
    ):
        raise ValueError("frozen curve sweep configs are not uniquely anchored")
    receipt_ids = [receipt["config_id"] for receipt in payload["preflight"]["results"]]
    if receipt_ids != config_ids or any(
        receipt["status"] != "legal" for receipt in payload["preflight"]["results"]
    ):
        raise ValueError("frozen preflight receipts do not cover every config")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capacity-points", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--stage2-protocol", type=Path, default=DEFAULT_STAGE2_PROTOCOL)
    args = parser.parse_args()
    capacity_points = json.loads(args.capacity_points.read_text(encoding="utf-8"))
    result = preflight_and_freeze(
        capacity_points,
        output_path=args.output,
        stage2_protocol_path=args.stage2_protocol,
        progress=print,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["manifest_frozen"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
