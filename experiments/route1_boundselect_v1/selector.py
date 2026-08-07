#!/usr/bin/env python3
"""Select the unique minimum raw full compression bound without risk input."""

from __future__ import annotations

import argparse
import json
import math
from decimal import Decimal
from pathlib import Path
from typing import Any

from . import PROTOCOL_ID, SCHEMA_VERSION
from .common import (
    DEFAULT_REGISTRY,
    DEFAULT_SELECTION,
    PACKAGE_ROOT,
    sha256_file,
    write_json_exclusive,
)


def _load_decimal_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    if not isinstance(payload, dict):
        raise ValueError("registry must be a JSON object")
    return payload


def _plain(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def validate_registry(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("protocol_id") != PROTOCOL_ID
        or registry.get("status") != "frozen_before_selection"
        or registry.get("leakage_control", {}).get(
            "registry_contains_heldout_risk_values"
        )
        is not False
    ):
        raise ValueError("candidate registry identity/leakage status differs")
    candidates = registry.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != registry.get(
        "candidate_count"
    ):
        raise ValueError("candidate count differs")
    allowed = set(
        registry["leakage_control"]["selector_allowed_candidate_fields"]
    )
    eligible = []
    for row in candidates:
        if not isinstance(row, dict) or set(row) != allowed:
            raise ValueError("selector candidate schema differs")
        if row["heldout_evaluation"].get("value_in_registry") is not False:
            raise ValueError("registry contains a held-out value")
        if set(row["heldout_evaluation"]) != {
            "path",
            "sha256",
            "role",
            "sample_count",
            "value_in_registry",
        }:
            raise ValueError("held-out provenance schema differs")
        if row["eligibility"].get("eligible") is True:
            bound = row["raw_full_compression_bound"]
            bits = row["actual_encoded_bits"]
            bound_valid = (
                bound.is_finite()
                if isinstance(bound, Decimal)
                else (
                    isinstance(bound, (int, float))
                    and not isinstance(bound, bool)
                    and math.isfinite(float(bound))
                )
            )
            if not bound_valid:
                raise ValueError("raw full bound is invalid")
            if (
                isinstance(bits, bool)
                or not isinstance(bits, int)
                or bits <= 0
            ):
                raise ValueError("actual encoded bits are invalid")
            eligible.append(row)
    if len(eligible) != registry["candidate_count"]:
        raise ValueError("frozen family contains an ineligible candidate")
    baselines = [row for row in eligible if row["baseline"] is True]
    if (
        len(baselines) != 1
        or baselines[0]["candidate_id"]
        != registry["baseline"]["candidate_id"]
    ):
        raise ValueError("baseline is not unique")
    return eligible


def select_candidate(registry: dict[str, Any]) -> dict[str, Any]:
    candidates = validate_registry(registry)
    minimum = min(row["raw_full_compression_bound"] for row in candidates)
    winners = [
        row
        for row in candidates
        if row["raw_full_compression_bound"] == minimum
    ]
    if len(winners) != 1:
        raise ValueError("raw full compression bound is exactly tied")
    selected = winners[0]
    baseline = next(row for row in candidates if row["baseline"])
    return {
        "selected": selected,
        "baseline": baseline,
        "candidate_count": len(candidates),
    }


def build_selection_receipt(
    registry: dict[str, Any], registry_path: Path
) -> dict[str, Any]:
    outcome = select_candidate(registry)
    selected = outcome["selected"]
    baseline = outcome["baseline"]

    def public(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "candidate_id": row["candidate_id"],
            "structure": row["structure"],
            "budget": row["budget"],
            "actual_encoded_bits": row["actual_encoded_bits"],
            "raw_full_compression_bound": row[
                "raw_full_compression_bound"
            ],
            "provenance": row["provenance"],
        }

    return _plain(
        {
            "schema_version": SCHEMA_VERSION,
            "protocol_id": PROTOCOL_ID,
            "status": "selected_before_heldout_risk_read",
            "registry_path": str(registry_path.resolve()),
            "registry_sha256": sha256_file(registry_path),
            "selector_source_path": str(
                (PACKAGE_ROOT / "selector.py").resolve()
            ),
            "selector_source_sha256": sha256_file(PACKAGE_ROOT / "selector.py"),
            "selection_input_contains_heldout_risk_values": False,
            "selection_rule": registry["selection_rule"],
            "candidate_count": outcome["candidate_count"],
            "selection_cost": registry["selection_cost"],
            "selected": public(selected),
            "baseline": public(baseline),
            "bound_difference_selected_minus_baseline": (
                selected["raw_full_compression_bound"]
                - baseline["raw_full_compression_bound"]
            ),
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_SELECTION)
    args = parser.parse_args()
    registry = _load_decimal_json(args.registry)
    receipt = build_selection_receipt(registry, args.registry)
    write_json_exclusive(args.output, receipt)
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "candidate_count": receipt["candidate_count"],
                "selected_candidate_id": receipt["selected"][
                    "candidate_id"
                ],
                "baseline_candidate_id": receipt["baseline"][
                    "candidate_id"
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
