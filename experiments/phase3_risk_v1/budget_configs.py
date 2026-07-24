#!/usr/bin/env python3
"""Generate and statically validate the 18 equal-coordinate-budget configs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1 import PROTOCOL_ID
from experiments.phase3_risk_v1.complexity_audit import external_selection_bits
from experiments.phase3_v6.scoring.common import (
    REPO_ROOT,
    canonical_json_bytes,
    sha256_file,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_ASSIGNMENT_CORE_SHA256,
    EXPECTED_INPUT_SHA256,
)


BASE_PROTOCOL_PATH = REPO_ROOT / "experiments/stage2_protocol_v2.json"
BASE_PROTOCOL_SHA256 = (
    "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
)
BUDGET_TOTALS = {"low": 2048, "current": 4096, "high": 8192}
BUDGET_MULTIPLIERS = {"low": 0.5, "current": 1.0, "high": 2.0}
MAPPING_ROOTS = (43101, 43102, 43103)
MODULE_FACTOR_ELEMENTS = {
    "vision": 24576,
    "projector": 98304,
    "language": 50176,
}
MODULE_ORDER = tuple(MODULE_FACTOR_ELEMENTS)
METHODS = ("M2", "M3")
CONFIG_SCHEMA_VERSION = 1
CANDIDATE_FAMILY_SIZE = len(BUDGET_TOTALS) * len(MAPPING_ROOTS) * len(METHODS)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def m2_allocation(total: int) -> tuple[dict[str, int], dict[str, Fraction]]:
    if isinstance(total, bool) or int(total) <= 0:
        raise ValueError("coordinate total must be positive")
    total = int(total)
    denominator = sum(MODULE_FACTOR_ELEMENTS.values())
    raw = {
        name: Fraction(total * weight, denominator)
        for name, weight in MODULE_FACTOR_ELEMENTS.items()
    }
    allocation = {name: math.floor(value) for name, value in raw.items()}
    remaining = total - sum(allocation.values())
    priority = sorted(
        MODULE_ORDER,
        key=lambda name: (
            -(raw[name] - allocation[name]),
            MODULE_ORDER.index(name),
        ),
    )
    for name in priority[:remaining]:
        allocation[name] += 1
    if sum(allocation.values()) != total:
        raise AssertionError("largest-remainder allocation does not sum to total")
    return allocation, raw


def _raw_allocation_receipt(raw: Mapping[str, Fraction]) -> dict[str, Any]:
    return {
        name: {
            "exact_fraction": f"{value.numerator}/{value.denominator}",
            "decimal": float(value),
        }
        for name, value in raw.items()
    }


def _base_payload() -> dict[str, Any]:
    if sha256_file(BASE_PROTOCOL_PATH) != BASE_PROTOCOL_SHA256:
        raise ValueError("Stage 2 v2 base protocol SHA-256 mismatch")
    protocol = _load_json(BASE_PROTOCOL_PATH)
    training = protocol["training"]
    reused = protocol["data"]["reused_confirmation"]
    return {
        "base_protocol": {
            "relative_path": str(BASE_PROTOCOL_PATH.relative_to(REPO_ROOT)),
            "sha256": BASE_PROTOCOL_SHA256,
            "protocol_id": protocol["protocol_id"],
        },
        "data": {
            "root_argument": "--artifact-root",
            "training_relative_path": (
                "dataset/stage2_confirm_v2_seed2028/train.parquet"
            ),
            "training_sha256": reused["train_sha256"],
            "draw_count": protocol["data"]["train_draws"],
            "same_data_for_all_models": True,
        },
        "training": {
            "train_seed": training["formal_seed"],
            "epoch_permutation": training["epoch_permutation"],
            "epochs": training["epochs"],
            "micro_batch_size": training["micro_batch_size"],
            "gradient_accumulation_steps": training[
                "gradient_accumulation_steps"
            ],
            "effective_batch_size": training["effective_batch_size"],
            "optimizer": training["optimizer"],
            "learning_rate": protocol["development"][
                "selected_learning_rates"
            ]["M2_M3"],
            "learning_rate_schedule": training["learning_rate_schedule"],
            "gradient_clip_global_l2": training[
                "gradient_clip_global_l2"
            ],
            "autocast_dtype": training["autocast_dtype"],
            "loss": "unchanged Stage 2 teacher-forced training loss",
        },
        "quantization": {
            "format": protocol["compression"]["format"],
            "levels": protocol["compression"]["levels"],
            "quantization_bits_label": protocol["compression"][
                "quantization_bits_label"
            ],
            "codec": protocol["compression"]["codec"],
        },
        "evaluation": {
            "evaluation_seed": 3407,
            "candidate_and_hull_rule": (
                "unchanged frozen Phase 3 v6 contrast-hull scorer"
            ),
            "mismatch_k": 5,
            "assignment_core_sha256": EXPECTED_ASSIGNMENT_CORE_SHA256,
            "frozen_input_sha256": dict(EXPECTED_INPUT_SHA256),
            "analysis_mode": "current_coupled_post_hoc",
            "certified": False,
            "invalid_for_formal_certification_reasons": [
                "post_hoc_metric_design",
                "coupled_mismatch_donors",
            ],
        },
    }


def build_config(method: str, budget: str, experiment_seed: int) -> dict[str, Any]:
    if method not in METHODS or budget not in BUDGET_TOTALS:
        raise ValueError("unknown method or budget")
    if experiment_seed not in MAPPING_ROOTS:
        raise ValueError("experiment_seed is not a frozen mapping root")
    total = BUDGET_TOTALS[budget]
    m2_dimensions, raw = m2_allocation(total)
    coordinate_dimensions = (
        m2_dimensions if method == "M2" else {"shared": total}
    )
    config_id = f"{method}-{budget}-seed-{experiment_seed}"
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "config_id": config_id,
        "comparison_label": "equal_coordinate_budget_not_equal_description_length",
        "comparison_label_zh": "相同坐标预算下的公平比较",
        "method": method,
        "budget": budget,
        "budget_multiplier_from_current": BUDGET_MULTIPLIERS[budget],
        "total_coordinate_budget": total,
        "coordinate_dimensions": coordinate_dimensions,
        "m2_allocation_protocol": {
            "method": (
                "largest_remainder_proportional_to_frozen_A_B_factor_elements"
            ),
            "factor_elements": dict(MODULE_FACTOR_ELEMENTS),
            "raw_before_rounding": _raw_allocation_receipt(raw),
            "rounded_dimensions": m2_dimensions,
        },
        "experiment_seed": experiment_seed,
        "experiment_seed_semantics": "deterministic_mapping_root",
        "mapping_root": experiment_seed,
        "candidate_family_size": CANDIDATE_FAMILY_SIZE,
        "external_selection_bits": external_selection_bits(
            CANDIDATE_FAMILY_SIZE
        ),
        "external_hyperparameter_bits": 0,
        "external_hyperparameter_bits_note": (
            "all budget levels, seeds, optimizer settings, and quantization "
            "rules are predeclared in this 18-member manifest"
        ),
        "actual_description_length_is_an_observed_result": True,
        "output_relative_path": (
            f"experiments/runs/phase3_risk_v1/{config_id}"
        ),
        **_base_payload(),
    }


def _pair_common(config: Mapping[str, Any]) -> dict[str, Any]:
    ignored = {
        "config_id",
        "method",
        "coordinate_dimensions",
        "output_relative_path",
    }
    return {key: value for key, value in config.items() if key not in ignored}


def validate_configs(configs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(configs) != CANDIDATE_FAMILY_SIZE:
        raise ValueError(f"expected {CANDIDATE_FAMILY_SIZE} configs")
    identifiers = [str(config.get("config_id")) for config in configs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("config IDs are duplicated")
    by_key: dict[tuple[str, int, str], Mapping[str, Any]] = {}
    for config in configs:
        method = str(config.get("method"))
        budget = str(config.get("budget"))
        seed = int(config.get("experiment_seed", -1))
        if (
            config.get("schema_version") != CONFIG_SCHEMA_VERSION
            or config.get("protocol_id") != PROTOCOL_ID
            or method not in METHODS
            or budget not in BUDGET_TOTALS
            or seed not in MAPPING_ROOTS
            or config.get("comparison_label")
            != "equal_coordinate_budget_not_equal_description_length"
            or config.get("actual_description_length_is_an_observed_result")
            is not True
        ):
            raise ValueError(f"invalid config metadata: {config.get('config_id')}")
        expected = build_config(method, budget, seed)
        if dict(config) != expected:
            raise ValueError(f"config differs from generator: {config['config_id']}")
        dimensions = config["coordinate_dimensions"]
        if sum(int(value) for value in dimensions.values()) != BUDGET_TOTALS[budget]:
            raise ValueError("coordinate dimensions do not sum to budget")
        by_key[(budget, seed, method)] = config
    for budget in BUDGET_TOTALS:
        for seed in MAPPING_ROOTS:
            m2 = by_key[(budget, seed, "M2")]
            m3 = by_key[(budget, seed, "M3")]
            if (
                sum(m2["coordinate_dimensions"].values())
                != m3["coordinate_dimensions"]["shared"]
            ):
                raise ValueError("M2/M3 coordinate budgets are unequal")
            if _pair_common(m2) != _pair_common(m3):
                raise ValueError(
                    f"M2/M3 fairness fields differ for {budget}/{seed}"
                )
    return {
        "status": "passed",
        "config_count": len(configs),
        "pair_count": len(BUDGET_TOTALS) * len(MAPPING_ROOTS),
        "comparison_claim": "equal_coordinate_budget_not_equal_description_length",
        "candidate_family_size": CANDIDATE_FAMILY_SIZE,
        "external_selection_bits": external_selection_bits(
            CANDIDATE_FAMILY_SIZE
        ),
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
            build_config(method, budget, seed)
            for method in METHODS
            for budget in BUDGET_TOTALS
            for seed in MAPPING_ROOTS
        ]
        validation = validate_configs(configs)
        entries = []
        for config in configs:
            filename = f"{config['config_id']}.json"
            payload = canonical_json_bytes(config, pretty=True)
            path = temporary / filename
            path.write_bytes(payload)
            entries.append(
                {
                    "config_id": config["config_id"],
                    "relative_path": filename,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
        manifest = {
            "schema_version": 1,
            "protocol_id": PROTOCOL_ID,
            **validation,
            "entries": entries,
        }
        (temporary / "manifest.json").write_bytes(
            canonical_json_bytes(manifest, pretty=True)
        )
        temporary.replace(destination)
        return manifest
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def load_and_validate_directory(config_dir: Path) -> dict[str, Any]:
    manifest = _load_json(config_dir / "manifest.json")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("config manifest lacks entries")
    configs = []
    for entry in entries:
        path = config_dir / str(entry["relative_path"])
        if sha256_file(path) != entry["sha256"]:
            raise ValueError(f"config SHA-256 mismatch: {path}")
        config = _load_json(path)
        if config.get("config_id") != entry.get("config_id"):
            raise ValueError("manifest/config ID mismatch")
        configs.append(config)
    validation = validate_configs(configs)
    for key, value in validation.items():
        if manifest.get(key) != value:
            raise ValueError(f"manifest validation receipt mismatch: {key}")
    return validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--output-dir", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--config-dir", type=Path, required=True)
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
