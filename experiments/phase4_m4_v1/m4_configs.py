#!/usr/bin/env python3
"""Generate and strictly validate the nine frozen Phase 4 M4 v1 configs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1.budget_configs import (
    MODULE_FACTOR_ELEMENTS,
    MODULE_ORDER,
    m2_allocation,
)
from experiments.phase4_m4_v1 import CONFIG_SCHEMA_VERSION, PROTOCOL_ID
from experiments.stage2_protocol import load_target_registry
from model.hybrid_subspace_lora import (
    A0_DOMAIN,
    COORDINATE_BLOCKS,
    MAPPING_DOMAIN,
    MAPPING_ROOTS,
    build_hybrid_factor_mappings,
    target_specs_from_registry,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = PACKAGE_ROOT / "protocol.json"
CONFIG_DIR = PACKAGE_ROOT / "configs"
MANIFEST_PATH = CONFIG_DIR / "manifest.json"
TOTAL_BUDGET = 4096
SHARED_BUDGETS = (1024, 2048, 3072)
CANDIDATE_FAMILY_SIZE = len(SHARED_BUDGETS) * len(MAPPING_ROOTS)
CANDIDATE_SELECTION_BITS = 4
QUANTIZATION_LEVELS = (-3, -2, -1, 0, 1, 2, 3)
_MAPPING_SUMMARY_CACHE: dict[tuple[int, tuple[int, ...]], dict[str, Any]] = {}


def canonical_json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        return (
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction_receipt(raw: Mapping[str, Fraction]) -> dict[str, Any]:
    return {
        name: {
            "exact_fraction": f"{raw[name].numerator}/{raw[name].denominator}",
            "decimal": float(raw[name]),
        }
        for name in MODULE_ORDER
    }


def _target_metadata(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [spec.as_metadata() for spec in target_specs_from_registry(registry)]


def _mapping_summary(
    mapping_root: int,
    dimensions: Mapping[str, int],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    key = (
        mapping_root,
        tuple(int(dimensions[name]) for name in COORDINATE_BLOCKS),
    )
    if key in _MAPPING_SUMMARY_CACHE:
        return copy.deepcopy(_MAPPING_SUMMARY_CACHE[key])
    _, statistics = build_hybrid_factor_mappings(
        mapping_root,
        target_specs_from_registry(registry),
        dimensions,
    )
    summary = {
        block_id: {
            "dimension": statistics[block_id]["dimension"],
            "minimum_usage": statistics[block_id]["minimum"],
            "maximum_usage": statistics[block_id]["maximum"],
            "mean_usage": statistics[block_id]["mean"],
            "usage_histogram_sha256": statistics[block_id][
                "histogram_sha256"
            ],
            "mapping_sha256": statistics[block_id]["mapping_sha256"],
        }
        for block_id in COORDINATE_BLOCKS
    }
    _MAPPING_SUMMARY_CACHE[key] = summary
    return copy.deepcopy(summary)


def _protocol() -> dict[str, Any]:
    payload = _load_json(PROTOCOL_PATH)
    if (
        payload.get("schema_version") != 1
        or payload.get("protocol_id") != PROTOCOL_ID
        or payload.get("configuration", {}).get("total_coordinate_budget")
        != TOTAL_BUDGET
        or tuple(payload.get("configuration", {}).get("shared_budgets", ()))
        != SHARED_BUDGETS
        or tuple(payload.get("configuration", {}).get("mapping_roots", ()))
        != MAPPING_ROOTS
    ):
        raise ValueError("Phase 4 protocol identity or frozen grid is invalid")
    return payload


def build_config(shared_budget: int, mapping_root: int) -> dict[str, Any]:
    protocol = _protocol()
    if shared_budget not in SHARED_BUDGETS:
        raise ValueError("shared budget is not predeclared")
    if mapping_root not in MAPPING_ROOTS:
        raise ValueError("mapping root is not predeclared")
    private_total = TOTAL_BUDGET - shared_budget
    private, raw = m2_allocation(private_total)
    if tuple(private) != MODULE_ORDER:
        raise ValueError("frozen m2_allocation module order changed")
    if dict(MODULE_FACTOR_ELEMENTS) != protocol["parameterization"][
        "private_allocation"
    ]["factor_elements"]:
        raise ValueError("Phase 3 factor-element authority changed")

    registry = load_target_registry()
    registry_ref = protocol["base_assets"]["target_registry"]
    registry_path = REPO_ROOT / registry_ref["relative_path"]
    if (
        registry.get("registry_id") != registry_ref["registry_id"]
        or sha256_file(registry_path) != registry_ref["sha256"]
    ):
        raise ValueError("frozen target registry identity changed")

    dimensions = {
        "shared_coordinates": shared_budget,
        "vision_private_coordinates": private["vision"],
        "projector_private_coordinates": private["projector"],
        "language_private_coordinates": private["language"],
    }
    if sum(dimensions.values()) != TOTAL_BUDGET:
        raise AssertionError("M4 coordinate budget is not conserved")
    config_id = f"M4-shared-{shared_budget}-root-{mapping_root}"
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "protocol": {
            "relative_path": str(PROTOCOL_PATH.relative_to(REPO_ROOT)),
            "sha256": sha256_file(PROTOCOL_PATH),
        },
        "config_id": config_id,
        "method": "M4",
        "total_coordinate_budget": TOTAL_BUDGET,
        "shared_budget": shared_budget,
        "private_total_budget": private_total,
        "vision_private_budget": private["vision"],
        "projector_private_budget": private["projector"],
        "language_private_budget": private["language"],
        "coordinate_dimensions": dimensions,
        "coordinate_block_order": list(COORDINATE_BLOCKS),
        "private_allocation_protocol": {
            "authority_function": (
                "experiments.phase3_risk_v1.budget_configs.m2_allocation"
            ),
            "authority_source_sha256": sha256_file(
                REPO_ROOT
                / "experiments/phase3_risk_v1/budget_configs.py"
            ),
            "method": (
                "largest_remainder_proportional_to_frozen_A_B_factor_elements"
            ),
            "factor_elements": dict(MODULE_FACTOR_ELEMENTS),
            "module_order_tie_break": list(MODULE_ORDER),
            "raw_before_rounding": _fraction_receipt(raw),
            "rounded_dimensions": private,
        },
        "mapping_root": mapping_root,
        "mapping": {
            "mapping_domain": MAPPING_DOMAIN,
            "a0_domain": A0_DOMAIN,
            "mapping_message_fields": protocol["mapping"][
                "mapping_message_fields"
            ],
            "a0_message_fields": protocol["mapping"]["a0_message_fields"],
            "normalization": protocol["mapping"]["value_normalization"],
            "require_every_coordinate_used": True,
        },
        "mapping_summary": _mapping_summary(
            mapping_root, dimensions, registry
        ),
        "target_registry": {
            **registry_ref,
            "target_order": "canonical_name_utf8_ascending",
            "targets": _target_metadata(registry),
        },
        "parameterization": protocol["parameterization"],
        "base_assets": protocol["base_assets"],
        "training": protocol["training"],
        "quantization": protocol["quantization"],
        "archive": protocol["archive"],
        "risk_adapter": protocol["risk_adapter"],
        "candidate_family_size": CANDIDATE_FAMILY_SIZE,
        "candidate_selection_bits": CANDIDATE_SELECTION_BITS,
        "candidate_selection_bits_in_archive": False,
        "automatic_hyperparameter_tuning": False,
        "runtime_overrides": "forbidden",
        "output_relative_path": (
            f"experiments/runs/phase4_m4_v1/{config_id}"
        ),
    }


def validate_config(config: Mapping[str, Any]) -> dict[str, Any]:
    config_id = str(config.get("config_id", ""))
    parts = config_id.split("-")
    if (
        len(parts) != 5
        or parts[0] != "M4"
        or parts[1] != "shared"
        or parts[3] != "root"
    ):
        raise ValueError("M4 config ID is malformed")
    try:
        shared_budget = int(parts[2])
        mapping_root = int(parts[4])
    except ValueError as error:
        raise ValueError("M4 config ID contains a non-integer") from error
    expected_id = f"M4-shared-{shared_budget}-root-{mapping_root}"
    if config_id != expected_id:
        raise ValueError("M4 config ID is not canonical")
    expected = build_config(shared_budget, mapping_root)
    if dict(config) != expected:
        raise ValueError(f"config differs from generator: {config_id}")
    dimensions = config["coordinate_dimensions"]
    if (
        set(dimensions) != set(COORDINATE_BLOCKS)
        or list(config["coordinate_block_order"]) != list(COORDINATE_BLOCKS)
        or sum(int(value) for value in dimensions.values()) != TOTAL_BUDGET
    ):
        raise ValueError("M4 config violates coordinate budget conservation")
    return {
        "status": "passed",
        "config_id": config_id,
        "total_coordinate_budget": TOTAL_BUDGET,
    }


def validate_configs(configs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(configs) != CANDIDATE_FAMILY_SIZE:
        raise ValueError("M4 manifest must contain exactly nine configs")
    identifiers = [str(config.get("config_id")) for config in configs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("M4 config IDs are duplicated")
    expected_ids = {
        f"M4-shared-{shared}-root-{root}"
        for shared in SHARED_BUDGETS
        for root in MAPPING_ROOTS
    }
    if set(identifiers) != expected_ids:
        raise ValueError("M4 config grid differs from the predeclared grid")
    for config in configs:
        validate_config(config)
    return {
        "status": "passed",
        "config_count": CANDIDATE_FAMILY_SIZE,
        "candidate_family_size": CANDIDATE_FAMILY_SIZE,
        "candidate_selection_bits": CANDIDATE_SELECTION_BITS,
        "candidate_selection_bits_in_archive": False,
    }


def generate_configs(output_dir: Path) -> dict[str, Any]:
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        configs = [
            build_config(shared, root)
            for shared in SHARED_BUDGETS
            for root in MAPPING_ROOTS
        ]
        validation = validate_configs(configs)
        entries = []
        for config in configs:
            filename = f"{config['config_id']}.json"
            payload = canonical_json_bytes(config, pretty=True)
            (temporary / filename).write_bytes(payload)
            entries.append(
                {
                    "config_id": config["config_id"],
                    "relative_path": filename,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "total_coordinate_budget": TOTAL_BUDGET,
                    "coordinate_dimensions": config[
                        "coordinate_dimensions"
                    ],
                }
            )
        manifest = {
            "schema_version": 1,
            "protocol_id": PROTOCOL_ID,
            **validation,
            "entries": entries,
        }
        manifest_bytes = canonical_json_bytes(manifest, pretty=True)
        (temporary / "manifest.json").write_bytes(manifest_bytes)
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        (temporary / "manifest.sha256").write_text(
            f"{manifest_sha}  manifest.json\n", encoding="ascii"
        )
        temporary.replace(destination)
        return manifest
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def load_and_validate_directory(config_dir: Path = CONFIG_DIR) -> dict[str, Any]:
    manifest_path = config_dir / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    expected_sha_line = f"{manifest_sha}  manifest.json\n"
    if (config_dir / "manifest.sha256").read_text(
        encoding="ascii"
    ) != expected_sha_line:
        raise ValueError("M4 manifest SHA-256 sidecar mismatch")
    manifest = json.loads(manifest_bytes)
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("M4 manifest lacks entries")
    configs = []
    for entry in entries:
        path = config_dir / str(entry["relative_path"])
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != entry.get("sha256"):
            raise ValueError(f"M4 config SHA-256 mismatch: {path}")
        config = json.loads(payload)
        if config.get("config_id") != entry.get("config_id"):
            raise ValueError("M4 manifest/config ID mismatch")
        if (
            entry.get("total_coordinate_budget")
            != config.get("total_coordinate_budget")
            or entry.get("coordinate_dimensions")
            != config.get("coordinate_dimensions")
        ):
            raise ValueError("M4 manifest budget receipt mismatch")
        configs.append(config)
    validation = validate_configs(configs)
    for key, value in validation.items():
        if manifest.get(key) != value:
            raise ValueError(f"M4 manifest validation mismatch: {key}")
    return {
        **validation,
        "manifest_sha256": manifest_sha,
    }


def load_frozen_config(
    config_id: str, config_dir: Path = CONFIG_DIR
) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = load_and_validate_directory(config_dir)
    manifest_path = config_dir / "manifest.json"
    manifest = _load_json(manifest_path)
    matches = [
        entry
        for entry in manifest["entries"]
        if entry["config_id"] == config_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate frozen M4 config: {config_id}")
    entry = matches[0]
    path = config_dir / entry["relative_path"]
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("selected M4 config hash differs from manifest")
    config = json.loads(payload)
    validate_config(config)
    return config, {
        "path": str(path.resolve()),
        "sha256": digest,
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": validation["manifest_sha256"],
        "directory_validation": validation,
    }


def reject_runtime_overrides(overrides: Mapping[str, Any] | None) -> None:
    if overrides:
        raise ValueError("frozen M4 configs forbid every runtime override")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--output-dir", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = (
        generate_configs(args.output_dir)
        if args.command == "generate"
        else load_and_validate_directory(args.config_dir)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
