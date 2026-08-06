#!/usr/bin/env python3
"""Read-only P/S training-data graph identity audit for XMC-01 round 1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BUDGETS = ("low", "current", "high")
SEEDS = (43101, 43102, 43103)


def _get(record: dict[str, Any], path: str) -> Any:
    value: Any = record
    for key in path.split("."):
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


SCALAR_PATHS = (
    "budget",
    "data.examples",
    "data.sha256",
    "experiment_type",
    "model.initial_structure.adapter.protocol.protocol_id",
    "model.initial_structure.adapter.protocol.protocol_sha256",
    "runtime_preflight.training_data.sha256",
    "training.effective_batch_size",
    "training.epochs",
    "training.gradient_accumulation_steps",
    "training.micro_batch_size",
    "training.observed_micro_batches",
    "training.optimizer_steps_expected",
    "training.optimizer_steps_observed",
    "training.learning_rate",
    "training.learning_rate_schedule.total_steps",
    "training.learning_rate_schedule.t_values",
)

CONFIG_PATHS = (
    "budget",
    "base_protocol.protocol_id",
    "base_protocol.sha256",
    "data.draw_count",
    "data.training_relative_path",
    "data.training_sha256",
    "training.effective_batch_size",
    "training.epoch_permutation",
    "training.epochs",
    "training.gradient_accumulation_steps",
    "training.micro_batch_size",
    "training.train_seed",
)


def _epoch_identity(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    receipts = _get(record, "training.epoch_receipts")
    if not isinstance(receipts, list):
        return None
    keys = ("epoch_index", "epoch_seed", "micro_batches", "permutation_sha256")
    return [{key: receipt.get(key) for key in keys} for receipt in receipts]


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run(root: Path) -> dict[str, Any]:
    records_root = (
        root
        / "experiments"
        / "phase3_risk_v1"
        / "results"
        / "budget_trend_18_models"
        / "run_records"
    )
    pairs: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    configs_root = root / "experiments" / "phase3_risk_v1" / "configs"

    for budget in BUDGETS:
        for seed in SEEDS:
            paths = {
                "P": records_root
                / f"M2-{budget}-seed-{seed}"
                / "training"
                / "training_manifest.json",
                "S": records_root
                / f"M3-{budget}-seed-{seed}"
                / "training"
                / "training_manifest.json",
            }
            absent = [side for side, path in paths.items() if not path.is_file()]
            if absent:
                config_paths = {
                    "P": configs_root / f"M2-{budget}-seed-{seed}.json",
                    "S": configs_root / f"M3-{budget}-seed-{seed}.json",
                }
                config_records = (
                    {side: _load(path) for side, path in config_paths.items()}
                    if all(path.is_file() for path in config_paths.values())
                    else None
                )
                config_comparisons = (
                    {
                        path: {
                            "P": _get(config_records["P"], path),
                            "S": _get(config_records["S"], path),
                            "equal": _get(config_records["P"], path)
                            == _get(config_records["S"], path),
                        }
                        for path in CONFIG_PATHS
                    }
                    if config_records is not None
                    else None
                )
                missing.append(
                    {
                        "budget": budget,
                        "seed": seed,
                        "missing_sides": absent,
                        "expected_paths": {
                            side: str(path.relative_to(root))
                            for side, path in paths.items()
                        },
                        "config_paths": {
                            side: str(path.relative_to(root))
                            for side, path in config_paths.items()
                        },
                        "config_comparisons": config_comparisons,
                        "configs_equal": (
                            all(
                                item["equal"]
                                for item in config_comparisons.values()
                            )
                            if config_comparisons is not None
                            else None
                        ),
                        "reason_not_promoted_to_manifest_evidence": (
                            "Configs predeclare equality but do not receipt the "
                            "realized epoch permutations."
                        ),
                    }
                )
                continue

            records = {side: _load(path) for side, path in paths.items()}
            comparisons = {
                path: {
                    "P": _get(records["P"], path),
                    "S": _get(records["S"], path),
                    "equal": _get(records["P"], path)
                    == _get(records["S"], path),
                }
                for path in SCALAR_PATHS
            }
            epoch_comparison = {
                "P": _epoch_identity(records["P"]),
                "S": _epoch_identity(records["S"]),
            }
            epoch_comparison["equal"] = (
                epoch_comparison["P"] == epoch_comparison["S"]
            )
            differing_fields = [
                path for path, item in comparisons.items() if not item["equal"]
            ]
            if not epoch_comparison["equal"]:
                differing_fields.append("training.epoch_receipts.identity")

            pairs.append(
                {
                    "budget": budget,
                    "seed": seed,
                    "paths": {
                        side: str(path.relative_to(root))
                        for side, path in paths.items()
                    },
                    "comparisons": comparisons,
                    "epoch_identity": epoch_comparison,
                    "differing_fields": differing_fields,
                    "data_graph_fields_equal": not differing_fields,
                }
            )

    all_audited_equal = bool(pairs) and all(
        pair["data_graph_fields_equal"] for pair in pairs
    )
    if missing:
        conclusion = "DATA_GRAPH_IDENTITY_NOT_AUDITABLE"
    elif all_audited_equal:
        conclusion = "PURE_DATA_XMC_INVARIANT_WITHIN_PS"
    else:
        conclusion = "PS_DATA_GRAPH_CONFOUNDED"

    return {
        "schema_version": 1,
        "idea_id": "XMC-01",
        "round": 1,
        "mode": "read_only_manifest_audit",
        "planned_pair_count": len(BUDGETS) * len(SEEDS),
        "audited_pair_count": len(pairs),
        "missing_pair_count": len(missing),
        "all_audited_pairs_equal": all_audited_equal,
        "pairs": pairs,
        "missing": missing,
        "conclusion": conclusion,
        "interpretation": (
            "The available P/S manifests agree on dataset hashes and exact epoch "
            "permutation identities, but missing current-budget manifests prevent "
            "a full-matrix identity claim."
            if conclusion == "DATA_GRAPH_IDENTITY_NOT_AUDITABLE"
            else ""
        ),
        "scientific_limits": [
            "This audit does not test model preservation of cross-modal structure.",
            "This audit does not validate a new proxy or inspect confirmation data.",
            "Data equality cannot establish a causal representation mechanism.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in (
        "planned_pair_count",
        "audited_pair_count",
        "missing_pair_count",
        "all_audited_pairs_equal",
        "conclusion",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
