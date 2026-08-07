#!/usr/bin/env python3
"""Build the immutable risk-value-free BoundSelect candidate registry."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from . import PROTOCOL_ID, SCHEMA_VERSION
from .common import (
    DEFAULT_FORMAL_ROOT,
    DEFAULT_PS_ROOT,
    DEFAULT_REGISTRY,
    PHASE3_V6_PROTOCOL,
    PHASE3_V6_PROTOCOL_SHA256,
    PS_PROTOCOL,
    PS_PROTOCOL_SHA256,
    STAGE2_FINAL_REPORT,
    STAGE2_FINAL_REPORT_SHA256,
    STAGE2_PROTOCOL,
    STAGE2_PROTOCOL_SHA256,
    candidate_id,
    git_commit,
    load_json,
    sha256_file,
    write_json_exclusive,
)


def _require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise ValueError(f"{label} SHA-256 differs: {path}")


def _coordinate_allocation(group: dict[str, Any]) -> dict[str, int]:
    names = group["coordinate_groups"]
    dimensions = group["coordinate_dimensions"]
    if len(names) != len(dimensions):
        raise ValueError("coordinate group/dimension lengths differ")
    result = dict(zip(names, dimensions))
    if (
        not result
        or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
            for value in result.values()
        )
    ):
        raise ValueError("coordinate allocation is invalid")
    return result


def _validate_ps_exclusion(ps_root: Path) -> dict[str, Any]:
    aggregate = ps_root / "development_evaluation/aggregate_results.json"
    if not aggregate.is_file():
        raise FileNotFoundError("audited P/S aggregate is missing")
    payload = load_json(aggregate)
    if (
        payload.get("status") != "complete"
        or payload.get("model_count") != 18
        or payload.get("final_confirmation_accessed") is not False
        or payload.get("analysis_scope")
        != "development_only_exploratory_not_a_formal_certificate"
    ):
        raise ValueError("P/S exclusion evidence differs from the audited scope")
    return {
        "family_id": "phase3-private-vs-shared-budget-v1",
        "candidate_count": 18,
        "protocol_path": str(PS_PROTOCOL),
        "protocol_sha256": PS_PROTOCOL_SHA256,
        "aggregate_path": str(aggregate),
        "aggregate_sha256": sha256_file(aggregate),
        "aggregate_status": "complete",
        "analysis_scope": payload["analysis_scope"],
        "final_confirmation_accessed": False,
        "eligible": False,
        "exclusion_reason": (
            "no existing formal raw full compression bound; the frozen "
            "development aggregate explicitly declares itself exploratory"
        ),
    }


def build_registry(
    formal_root: Path = DEFAULT_FORMAL_ROOT,
    ps_root: Path = DEFAULT_PS_ROOT,
) -> dict[str, Any]:
    _require_hash(
        STAGE2_PROTOCOL, STAGE2_PROTOCOL_SHA256, "Stage 2 protocol"
    )
    _require_hash(
        STAGE2_FINAL_REPORT,
        STAGE2_FINAL_REPORT_SHA256,
        "Stage 2 final report",
    )
    _require_hash(PS_PROTOCOL, PS_PROTOCOL_SHA256, "P/S protocol")
    _require_hash(
        PHASE3_V6_PROTOCOL,
        PHASE3_V6_PROTOCOL_SHA256,
        "Phase 3 v6 frozen model registry",
    )
    protocol = load_json(STAGE2_PROTOCOL)
    phase3_v6 = load_json(PHASE3_V6_PROTOCOL)
    evaluation = protocol["evaluation"]
    groups = protocol["model"]["groups"]
    if (
        protocol.get("status") != "frozen"
        or protocol.get("protocol_id")
        != "minimind-v-stage2-joint-compression-v2"
        or evaluation.get("formal_model_count") != 10
        or evaluation.get("primary_bound")
        != "raw, unclipped compression upper bound"
        or evaluation.get("required_risks")
        != [
            "unquantized full training risk",
            "decoded quantized full training risk",
            "decoded quantized validation risk",
        ]
    ):
        raise ValueError("Stage 2 formal protocol identity differs")
    verified_models = phase3_v6.get("models", {}).get("verified_models")
    if (
        phase3_v6.get("status") != "frozen_before_formal_model_inference"
        or not isinstance(verified_models, list)
        or len(verified_models) != 10
        or phase3_v6["models"].get("stage2_protocol_sha256")
        != STAGE2_PROTOCOL_SHA256
        or phase3_v6["models"].get(
            "training_finetuning_or_weight_changes_allowed"
        )
        is not False
    ):
        raise ValueError("Phase 3 v6 frozen model registry differs")
    verified_by_id = {
        str(row["model_id"]): row for row in verified_models
    }
    if len(verified_by_id) != 10:
        raise ValueError("Phase 3 v6 model identifiers are duplicated")
    baseline_groups = [
        name
        for name, group in groups.items()
        if "baseline" in group["description"].lower()
    ]
    if baseline_groups != ["M1"]:
        raise ValueError("frozen protocol does not define one unique baseline")

    run_directories = sorted(
        path for path in formal_root.iterdir() if path.is_dir()
    )
    if len(run_directories) != evaluation["formal_model_count"]:
        raise ValueError("formal run count differs from frozen family size")

    candidates = []
    for run in run_directories:
        bound_path = run / "bound.json"
        adapter_path = run / "decode/adapter_summary.json"
        manifest_path = run / "train/training_manifest.json"
        validation_path = run / "risk_decoded_validation_correct.json"
        for required in (
            bound_path,
            adapter_path,
            manifest_path,
            validation_path,
        ):
            if not required.is_file():
                raise FileNotFoundError(f"formal artifact is missing: {required}")
        bound = load_json(bound_path)
        adapter = load_json(adapter_path)
        manifest = load_json(manifest_path)
        group_name = str(bound["model_group"])
        root = bound["mapping_root"]
        if root is not None:
            root = int(root)
        if group_name not in groups:
            raise ValueError("bound model group is outside frozen protocol")
        identifier = candidate_id(group_name, root)
        frozen_model = verified_by_id.get(identifier)
        if frozen_model is None:
            raise ValueError(f"{identifier} is outside frozen v6 registry")
        if (
            bound.get("formal") is not True
            or bound.get("protocol")
            != {
                "protocol_id": protocol["protocol_id"],
                "protocol_sha256": STAGE2_PROTOCOL_SHA256,
            }
            or bound["bound"].get("primary_is_raw_unclipped") is not True
            or int(bound["independent_train_samples"]) != 10000
            or float(bound["confidence_delta"])
            != float(evaluation["per_model_delta"])
            or manifest.get("status") != "complete"
            or manifest.get("formal") is not True
            or manifest.get("model_group") != group_name
            or manifest.get("mapping_root") != root
            or adapter.get("model_group") != group_name
            or adapter.get("mapping_root") != root
        ):
            raise ValueError(f"formal identity differs for {identifier}")
        bits = int(bound["complexity"]["adapter_bits"])
        raw_bound = float(
            bound["bound"]["raw_compression_upper_bound_bits"]
        )
        if (
            not math.isfinite(raw_bound)
            or bits <= 0
            or bits != int(adapter["complexity_bits"])
            or int(adapter["archive_bytes"]) * 8 != bits
            or bound["inputs"]["adapter_summary_sha256"]
            != sha256_file(adapter_path)
            or bound["inputs"]["decoded_validation_risk_sha256"]
            != sha256_file(validation_path)
        ):
            raise ValueError(f"bound/bit provenance differs for {identifier}")

        archive = Path(adapter["archive_path"])
        checkpoint = Path(manifest["checkpoint"]["path"])
        if (
            not archive.is_file()
            or not checkpoint.is_file()
            or sha256_file(archive) != adapter["archive_sha256"]
            or sha256_file(checkpoint) != manifest["checkpoint"]["sha256"]
            or frozen_model["checkpoint_path"] != str(archive)
            or frozen_model["checkpoint_sha256"]
            != adapter["archive_sha256"]
            or int(frozen_model["adapter_config"]["complexity_bits"])
            != bits
        ):
            raise ValueError(f"checkpoint/archive provenance differs for {identifier}")
        is_baseline = group_name == baseline_groups[0]
        candidates.append(
            {
                "candidate_id": identifier,
                "structure": group_name,
                "structure_description": groups[group_name]["description"],
                "budget": {
                    "total_coordinate_budget": int(
                        protocol["model"]["total_coordinate_budget"]
                    ),
                    "allocation": _coordinate_allocation(groups[group_name]),
                    "mapping_root": root,
                },
                "actual_encoded_bits": bits,
                "raw_full_compression_bound": raw_bound,
                "provenance": {
                    "formal_run_directory": str(run),
                    "protocol_id": protocol["protocol_id"],
                    "protocol_sha256": STAGE2_PROTOCOL_SHA256,
                    "formal": True,
                    "primary_bound_is_raw_unclipped": True,
                    "prediction_smoothing": evaluation["smoothing"],
                    "codec": adapter["codec"],
                    "training_sample_count": int(
                        bound["independent_train_samples"]
                    ),
                },
                "checkpoint": {
                    "path": str(archive),
                    "sha256": adapter["archive_sha256"],
                    "exists": True,
                    "sha256_verified": True,
                    "frozen_registry": "phase3_v6/scoring/protocol.json",
                },
                "training_checkpoint": {
                    "path": str(checkpoint),
                    "sha256": manifest["checkpoint"]["sha256"],
                    "exists": True,
                    "sha256_verified": True,
                },
                "encoded_model": {
                    "path": str(archive),
                    "sha256": adapter["archive_sha256"],
                },
                "raw_bound_source": {
                    "path": str(bound_path),
                    "sha256": sha256_file(bound_path),
                    "field": "bound.raw_compression_upper_bound_bits",
                },
                "actual_bits_source": {
                    "path": str(adapter_path),
                    "sha256": sha256_file(adapter_path),
                    "field": "complexity_bits",
                },
                "heldout_evaluation": {
                    "path": str(validation_path),
                    "sha256": bound["inputs"][
                        "decoded_validation_risk_sha256"
                    ],
                    "role": "decoded_quantized_validation_correct",
                    "sample_count": 2000,
                    "value_in_registry": False,
                },
                "baseline": is_baseline,
                "baseline_reason": (
                    "frozen protocol description: historical fixed hashed "
                    "projector baseline"
                    if is_baseline
                    else None
                ),
                "eligibility": {
                    "eligible": True,
                    "checkpoint_exists_and_hash_matches": True,
                    "actual_encoded_bits_formal": True,
                    "raw_full_compression_bound_formal": True,
                    "same_frozen_protocol": True,
                    "same_prediction_smoothing": True,
                    "same_codec": True,
                    "heldout_validation_artifact_exists_and_hash_matches": True,
                    "partial_or_failed": False,
                    "final_confirmation_leakage": False,
                },
            }
        )

    identifiers = [row["candidate_id"] for row in candidates]
    if len(set(identifiers)) != len(candidates):
        raise ValueError("candidate identifiers are duplicated")
    baselines = [row for row in candidates if row["baseline"]]
    if len(baselines) != 1 or baselines[0]["candidate_id"] != "M1-root-none":
        raise ValueError("candidate registry baseline differs")
    k = len(candidates)
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "frozen_before_selection",
        "authority": {
            "source_git_commit": git_commit(),
            "stage2_protocol_path": str(STAGE2_PROTOCOL),
            "stage2_protocol_sha256": STAGE2_PROTOCOL_SHA256,
            "stage2_final_report_path": str(STAGE2_FINAL_REPORT),
            "stage2_final_report_sha256": STAGE2_FINAL_REPORT_SHA256,
            "phase3_v6_protocol_path": str(PHASE3_V6_PROTOCOL),
            "phase3_v6_protocol_sha256": PHASE3_V6_PROTOCOL_SHA256,
            "candidate_family_rule": (
                "complete preregistered Stage 2 v2 formal family with exact "
                "retained checkpoints frozen by Phase 3 v6"
            ),
            "historical_stage2_final_report_role": (
                "completion evidence only; its retained numerical rows bind a "
                "different execution whose checkpoints were removed"
            ),
        },
        "audited_excluded_families": [_validate_ps_exclusion(ps_root)],
        "candidate_count": k,
        "selection_cost": {
            "ceil_log2_k_bits": math.ceil(math.log2(k)),
            "checkpoint_reencoding_bits": 0,
            "raw_bound_definition_changed": False,
            "existing_finite_family_union_bound": {
                "familywise_delta": float(evaluation["familywise_delta"]),
                "per_model_delta": float(evaluation["per_model_delta"]),
                "formal_model_count": int(evaluation["formal_model_count"]),
                "relation": "per_model_delta=familywise_delta/K",
            },
        },
        "selection_rule": {
            "objective": "minimize raw_full_compression_bound",
            "strict": True,
            "tie_policy": "fail_without_existing_tie_break",
        },
        "baseline": {
            "candidate_id": "M1-root-none",
            "frozen_before_heldout_risk": True,
            "authority": (
                "stage2_protocol_v2.json model.groups.M1.description"
            ),
        },
        "leakage_control": {
            "registry_contains_heldout_risk_values": False,
            "selector_allowed_candidate_fields": [
                "candidate_id",
                "structure",
                "structure_description",
                "budget",
                "actual_encoded_bits",
                "raw_full_compression_bound",
                "provenance",
                "checkpoint",
                "training_checkpoint",
                "encoded_model",
                "raw_bound_source",
                "actual_bits_source",
                "heldout_evaluation",
                "baseline",
                "baseline_reason",
                "eligibility",
            ],
            "heldout_evaluation_value_read_stage": (
                "only after selection_receipt exists"
            ),
        },
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--formal-root", type=Path, default=DEFAULT_FORMAL_ROOT
    )
    parser.add_argument("--ps-root", type=Path, default=DEFAULT_PS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    registry = build_registry(args.formal_root, args.ps_root)
    write_json_exclusive(args.output, registry)
    print(
        json.dumps(
            {
                "status": registry["status"],
                "candidate_count": registry["candidate_count"],
                "baseline": registry["baseline"]["candidate_id"],
                "selection_cost_bits": registry["selection_cost"][
                    "ceil_log2_k_bits"
                ],
                "output": str(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
