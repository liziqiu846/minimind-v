"""Per-record operational-language, visual, and total semantic risks."""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1 import RISK_SCHEMA_VERSION


K_MISMATCH = 5
IDENTITY_TOLERANCE = 1e-6
HISTORICAL_MEAN_TOLERANCE = 1e-15
MISMATCH_SOURCE_FIELDS = tuple(
    f"q_mismatch_round_{index}" for index in range(1, K_MISMATCH + 1)
)
MISMATCH_OUTPUT_FIELDS = tuple(
    f"q_mismatch_{index}" for index in range(1, K_MISMATCH + 1)
)
RISK_FIELDS = (
    "language_risk",
    "visual_gain",
    "visual_risk",
    "total_semantic_risk",
)


def _probability(row: Mapping[str, Any], key: str) -> float:
    if key not in row or isinstance(row[key], bool):
        raise ValueError(f"missing or non-numeric required field: {key}")
    value = float(row[key])
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{key} is outside [0,1]: {value}")
    return value


def _identity_error(
    language_risk: float, visual_risk: float, total_semantic_risk: float
) -> float:
    # total = language + 2*visual - 1 must hold for every source record.
    reconstructed = math.fsum((language_risk, 2.0 * visual_risk, -1.0))
    return abs(total_semantic_risk - reconstructed)


def derive_risk_row(
    source: Mapping[str, Any],
    *,
    identity_tolerance: float = IDENTITY_TOLERANCE,
) -> dict[str, Any]:
    """Return a v6-compatible row augmented with the frozen v1 risk fields."""

    if identity_tolerance < 0.0 or not math.isfinite(identity_tolerance):
        raise ValueError("identity_tolerance must be finite and non-negative")
    q_correct = _probability(source, "q_correct")
    mismatch = [_probability(source, key) for key in MISMATCH_SOURCE_FIELDS]
    if len(mismatch) != K_MISMATCH:
        raise AssertionError("the frozen mismatch count is not five")
    q_mismatch_mean_recomputed = math.fsum(mismatch) / K_MISMATCH
    q_mismatch_mean_historical = _probability(source, "q_mismatch_k5")
    mean_error = abs(q_mismatch_mean_recomputed - q_mismatch_mean_historical)
    if mean_error > HISTORICAL_MEAN_TOLERANCE:
        raise ValueError(
            "historical q_mismatch_k5 differs from the five-round arithmetic "
            f"mean by {mean_error}"
        )

    q_mismatch_mean = q_mismatch_mean_historical
    language_risk = 1.0 - q_mismatch_mean
    visual_gain = q_correct - q_mismatch_mean
    visual_risk = (1.0 - visual_gain) / 2.0
    total_semantic_risk = 1.0 - q_correct
    identity_error = _identity_error(
        language_risk, visual_risk, total_semantic_risk
    )

    for name, value, lower, upper in (
        ("language_risk", language_risk, 0.0, 1.0),
        ("visual_gain", visual_gain, -1.0, 1.0),
        ("visual_risk", visual_risk, 0.0, 1.0),
        ("total_semantic_risk", total_semantic_risk, 0.0, 1.0),
    ):
        if not math.isfinite(value) or not lower <= value <= upper:
            raise ValueError(f"{name} is outside [{lower},{upper}]: {value}")
    if identity_error > identity_tolerance:
        identity = source.get("sample_id", "<missing-sample-id>")
        model_id = source.get("model_id", "<missing-model-id>")
        raise AssertionError(
            f"risk identity failed for {model_id}/{identity}: "
            f"error={identity_error}, tolerance={identity_tolerance}"
        )

    output = dict(source)
    output.update(
        {
            "risk_schema_version": RISK_SCHEMA_VERSION,
            **{
                output_name: value
                for output_name, value in zip(
                    MISMATCH_OUTPUT_FIELDS, mismatch, strict=True
                )
            },
            "q_mismatch_mean": q_mismatch_mean,
            "q_mismatch_mean_recomputed": q_mismatch_mean_recomputed,
            "q_mismatch_mean_compatibility_error": mean_error,
            "language_risk": language_risk,
            "language_risk_zh": "操作性语言风险",
            "visual_gain": visual_gain,
            "visual_risk": visual_risk,
            "total_semantic_risk": total_semantic_risk,
            "identity_error": identity_error,
            "identity_tolerance": identity_tolerance,
        }
    )
    return output


def derive_risk_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    identity_tolerance: float = IDENTITY_TOLERANCE,
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("risk derivation requires at least one row")
    output = [
        derive_risk_row(row, identity_tolerance=identity_tolerance)
        for row in rows
    ]
    identifiers = [row.get("sample_id") for row in output]
    if any(not isinstance(value, str) or not value for value in identifiers):
        raise ValueError("a risk row lacks a non-empty sample_id")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("risk rows contain duplicate sample_id values")
    return output
