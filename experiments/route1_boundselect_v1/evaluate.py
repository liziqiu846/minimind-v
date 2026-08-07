#!/usr/bin/env python3
"""Read held-out risk only after selection and finalize BoundSelect once."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
from typing import Any

from . import PROTOCOL_ID, SCHEMA_VERSION
from .common import (
    DEFAULT_CSV,
    DEFAULT_REGISTRY,
    DEFAULT_SELECTION,
    DEFAULT_SUMMARY,
    load_json,
    sha256_file,
    write_json_exclusive,
)


def _candidate(registry: dict[str, Any], identifier: str) -> dict[str, Any]:
    matches = [
        row
        for row in registry["candidates"]
        if row["candidate_id"] == identifier
    ]
    if len(matches) != 1:
        raise ValueError("selection candidate is absent or duplicated")
    return matches[0]


def _validation_risk(candidate: dict[str, Any]) -> float:
    source = candidate["heldout_evaluation"]
    path = Path(source["path"])
    if sha256_file(path) != source["sha256"]:
        raise ValueError("held-out validation artifact SHA-256 differs")
    payload = load_json(path)
    expected_protocol = candidate["provenance"]["protocol_sha256"]
    expected_root = candidate["budget"]["mapping_root"]
    if (
        payload.get("protocol", {}).get("protocol_sha256")
        != expected_protocol
        or payload.get("model_group") != candidate["structure"]
        or payload.get("mapping_root") != expected_root
        or payload.get("model_kind") != "decoded_quantized"
        or payload.get("image_condition") != "correct"
        or payload.get("data", {}).get("role") != "validation"
        or payload.get("data", {}).get("sample_count")
        != source["sample_count"]
        or payload.get("adapter", {}).get("sha256")
        != candidate["encoded_model"]["sha256"]
    ):
        raise ValueError("held-out validation provenance differs")
    value = float(payload["risk"]["mean_sample_risk_bits"])
    if not math.isfinite(value):
        raise ValueError("held-out validation risk is not finite")
    return value


def build_summary(
    registry: dict[str, Any],
    selection: dict[str, Any],
    *,
    registry_path: Path,
    selection_path: Path,
) -> dict[str, Any]:
    if (
        selection.get("status")
        != "selected_before_heldout_risk_read"
        or selection.get("protocol_id") != PROTOCOL_ID
        or selection.get("selection_input_contains_heldout_risk_values")
        is not False
        or selection.get("registry_sha256") != sha256_file(registry_path)
    ):
        raise ValueError("selection receipt binding/leakage status differs")
    selected = _candidate(
        registry, selection["selected"]["candidate_id"]
    )
    baseline = _candidate(
        registry, selection["baseline"]["candidate_id"]
    )
    selected_risk = _validation_risk(selected)
    baseline_risk = _validation_risk(baseline)
    selected_bound = float(selected["raw_full_compression_bound"])
    baseline_bound = float(baseline["raw_full_compression_bound"])
    bound_difference = selected_bound - baseline_bound
    risk_difference = selected_risk - baseline_risk
    criteria = {
        "selection_did_not_read_heldout_risk": True,
        "selected_bound_strictly_lower_than_baseline": (
            selected_bound < baseline_bound
        ),
        "selected_risk_strictly_lower_than_baseline": (
            selected_risk < baseline_risk
        ),
    }
    passed = all(criteria.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "complete",
        "decision": "PASS" if passed else "FAIL",
        "candidate_count": int(selection["candidate_count"]),
        "selection_cost_bits": int(
            selection["selection_cost"]["ceil_log2_k_bits"]
        ),
        "existing_finite_family_union_bound": selection["selection_cost"][
            "existing_finite_family_union_bound"
        ],
        "selection_cost_checkpoint_reencoding_bits": 0,
        "raw_bound_definition_changed": False,
        "registry_path": str(registry_path.resolve()),
        "registry_sha256": sha256_file(registry_path),
        "selection_receipt_path": str(selection_path.resolve()),
        "selection_receipt_sha256": sha256_file(selection_path),
        "selection_input_contains_heldout_risk_values": False,
        "selected": {
            "candidate_id": selected["candidate_id"],
            "structure": selected["structure"],
            "budget": selected["budget"],
            "actual_encoded_bits": selected["actual_encoded_bits"],
            "raw_full_compression_bound": selected_bound,
            "heldout_validation_answer_risk": selected_risk,
            "heldout_risk_source": selected["heldout_evaluation"],
        },
        "baseline": {
            "candidate_id": baseline["candidate_id"],
            "structure": baseline["structure"],
            "budget": baseline["budget"],
            "actual_encoded_bits": baseline["actual_encoded_bits"],
            "raw_full_compression_bound": baseline_bound,
            "heldout_validation_answer_risk": baseline_risk,
            "heldout_risk_source": baseline["heldout_evaluation"],
        },
        "differences_selected_minus_baseline": {
            "risk": risk_difference,
            "raw_full_compression_bound": bound_difference,
            "actual_encoded_bits": (
                selected["actual_encoded_bits"]
                - baseline["actual_encoded_bits"]
            ),
        },
        "pass_criteria": criteria,
        "no_additional_experiments_authorized": not passed,
        "interpretation_scope": (
            "frozen finite-catalog Stage 2 v2 family; failure does not reject "
            "compression theory or all bound-guided algorithms"
        ),
    }


def _write_csv_exclusive(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    fields = [
        "decision",
        "candidate_count",
        "selection_cost_bits",
        "selected_model_id",
        "selected_raw_full_compression_bound",
        "selected_actual_encoded_bits",
        "selected_heldout_validation_answer_risk",
        "baseline_model_id",
        "baseline_raw_full_compression_bound",
        "baseline_actual_encoded_bits",
        "baseline_heldout_validation_answer_risk",
        "risk_difference_selected_minus_baseline",
        "bound_difference_selected_minus_baseline",
        "bits_difference_selected_minus_baseline",
    ]
    row = {
        "decision": summary["decision"],
        "candidate_count": summary["candidate_count"],
        "selection_cost_bits": summary["selection_cost_bits"],
        "selected_model_id": summary["selected"]["candidate_id"],
        "selected_raw_full_compression_bound": summary["selected"][
            "raw_full_compression_bound"
        ],
        "selected_actual_encoded_bits": summary["selected"][
            "actual_encoded_bits"
        ],
        "selected_heldout_validation_answer_risk": summary["selected"][
            "heldout_validation_answer_risk"
        ],
        "baseline_model_id": summary["baseline"]["candidate_id"],
        "baseline_raw_full_compression_bound": summary["baseline"][
            "raw_full_compression_bound"
        ],
        "baseline_actual_encoded_bits": summary["baseline"][
            "actual_encoded_bits"
        ],
        "baseline_heldout_validation_answer_risk": summary["baseline"][
            "heldout_validation_answer_risk"
        ],
        "risk_difference_selected_minus_baseline": summary[
            "differences_selected_minus_baseline"
        ]["risk"],
        "bound_difference_selected_minus_baseline": summary[
            "differences_selected_minus_baseline"
        ]["raw_full_compression_bound"],
        "bits_difference_selected_minus_baseline": summary[
            "differences_selected_minus_baseline"
        ]["actual_encoded_bits"],
    }
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow(row)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    if not args.selection.is_file():
        raise FileNotFoundError(
            "selection receipt must exist before held-out evaluation"
        )
    registry = load_json(args.registry)
    selection = load_json(args.selection)
    summary = build_summary(
        registry,
        selection,
        registry_path=args.registry,
        selection_path=args.selection,
    )
    write_json_exclusive(args.summary, summary)
    _write_csv_exclusive(args.csv, summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "decision": summary["decision"],
                "selected_candidate_id": summary["selected"][
                    "candidate_id"
                ],
                "baseline_candidate_id": summary["baseline"][
                    "candidate_id"
                ],
                "summary": str(args.summary),
                "csv": str(args.csv),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
