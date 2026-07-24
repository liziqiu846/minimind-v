#!/usr/bin/env python3
"""Static dry-run and current-equivalence checks for budget experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.phase3_risk_v1.budget_adapter import (
    build_factor_mappings_for_dimensions,
    check_current_mapping_equivalence,
)
from experiments.phase3_risk_v1.budget_codec import (
    check_current_codec_equivalence,
)
from experiments.phase3_risk_v1.budget_configs import (
    BASE_PROTOCOL_PATH,
    build_config,
    load_and_validate_directory,
)
from experiments.phase3_v6.scoring.common import sha256_file
from experiments.stage2_protocol import load_target_registry
from model.global_subspace_lora import target_specs


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dry_run_config(config: dict[str, Any], artifact_root: Path | None) -> dict[str, Any]:
    expected = build_config(
        str(config["method"]),
        str(config["budget"]),
        int(config["experiment_seed"]),
    )
    if config != expected:
        raise ValueError(f"config differs from generator: {config.get('config_id')}")
    registry = load_target_registry()
    specs = target_specs(
        registry, ("vision", "projector", "language")
    )
    _, statistics = build_factor_mappings_for_dimensions(
        config["method"],
        config["mapping_root"],
        specs,
        config["coordinate_dimensions"],
    )
    if any(value["minimum"] < 1 for value in statistics.values()):
        raise AssertionError("a configured coordinate is unused")
    data_status = "not_checked_no_artifact_root"
    if artifact_root is not None:
        data_path = artifact_root / config["data"]["training_relative_path"]
        if not data_path.is_file():
            raise FileNotFoundError(data_path)
        if sha256_file(data_path) != config["data"]["training_sha256"]:
            raise ValueError("training data SHA-256 mismatch")
        data_status = "verified"
    return {
        "config_id": config["config_id"],
        "status": "passed",
        "comparison_label": config["comparison_label"],
        "total_coordinate_budget": config["total_coordinate_budget"],
        "coordinate_dimensions": config["coordinate_dimensions"],
        "mapping_usage": statistics,
        "training_data_status": data_status,
        "training_started": False,
    }


def matrix_dry_run(
    config_dir: Path, artifact_root: Path | None
) -> dict[str, Any]:
    directory_validation = load_and_validate_directory(config_dir)
    manifest = _load_json(config_dir / "manifest.json")
    configs = [
        _load_json(config_dir / entry["relative_path"])
        for entry in manifest["entries"]
    ]
    data_status = "not_checked_no_artifact_root"
    if artifact_root is not None:
        first = configs[0]
        data_path = artifact_root / first["data"]["training_relative_path"]
        if not data_path.is_file():
            raise FileNotFoundError(data_path)
        if sha256_file(data_path) != first["data"]["training_sha256"]:
            raise ValueError("training data SHA-256 mismatch")
        data_status = "verified_once_for_shared_frozen_data"
    rows = [dry_run_config(config, None) for config in configs]
    for row in rows:
        row["training_data_status"] = data_status
    return {
        "status": "passed",
        "dry_run_type": "static_no_training",
        "directory_validation": directory_validation,
        "config_count": len(rows),
        "training_started": False,
        "configs": rows,
    }


def equivalence_check() -> dict[str, Any]:
    if not BASE_PROTOCOL_PATH.is_file():
        raise FileNotFoundError(BASE_PROTOCOL_PATH)
    registry = load_target_registry()
    return {
        "status": "passed",
        "mapping": check_current_mapping_equivalence(registry),
        "codec": check_current_codec_equivalence(),
        "full_model_construction_check": (
            "available through check_current_model_construction_equivalence; "
            "requires immutable model assets and is run separately"
        ),
        "training_started": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    dry = subparsers.add_parser("dry-run-matrix")
    dry.add_argument("--config-dir", type=Path, required=True)
    dry.add_argument("--artifact-root", type=Path)
    subparsers.add_parser("check-current-equivalence")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = (
        matrix_dry_run(args.config_dir, args.artifact_root)
        if args.command == "dry-run-matrix"
        else equivalence_check()
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
