#!/usr/bin/env python3
"""Combine an encoded model and its smoothed training risk into a bound report."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.generalization_bound import (
    description_complexity_nats,
    finite_hypothesis_bound,
    prediction_smoothing_interval,
)
from experiments.quantize_checkpoint import sha256_file


def build_report(
    encoding: dict,
    training_risk: dict,
    validation_risk: dict | None,
    confidence_delta: float,
    encoded_weight_bits: int,
) -> dict:
    decoded_sha = encoding["decoded_checkpoint_sha256"]
    if training_risk["checkpoint_sha256"] != decoded_sha:
        raise ValueError("training risk was not evaluated on the encoded hypothesis")
    if validation_risk and validation_risk["checkpoint_sha256"] != decoded_sha:
        raise ValueError("validation risk checkpoint does not match the encoded hypothesis")

    alpha_bits = training_risk["alpha_choice_bits"]
    complexity = description_complexity_nats(encoded_weight_bits, alpha_bits)
    validation_by_alpha = {
        item["alpha"]: item["mean_sample_risk_bits"]
        for item in (validation_risk or {}).get("risks", [])
    }
    rows = []
    for item in training_risk["risks"]:
        alpha = item["alpha"]
        empirical_risk = item["mean_sample_risk_bits"]
        result = finite_hypothesis_bound(
            empirical_risk,
            prediction_smoothing_interval(training_risk["vocab_size"], alpha),
            complexity,
            training_risk["sample_count"],
            confidence_delta,
        )
        row = asdict(result)
        row["alpha"] = alpha
        if alpha in validation_by_alpha:
            row["validation_risk_bits"] = validation_by_alpha[alpha]
            row["observed_generalization_gap_bits"] = (
                validation_by_alpha[alpha] - empirical_risk
            )
        rows.append(row)

    best = min(rows, key=lambda row: row["compression_upper_bound_bits"])
    return {
        "schema_version": 1,
        "run_id": training_risk["run_id"],
        "certificate_uses_training_risk_only": True,
        "confidence_delta": confidence_delta,
        "independent_train_samples": training_risk["sample_count"],
        "encoded_weight_bits": encoded_weight_bits,
        "alpha_choice_bits": alpha_bits,
        "description_complexity_nats": complexity,
        "archive_sha256": encoding["archive_sha256"],
        "decoded_checkpoint_sha256": decoded_sha,
        "best_alpha": best["alpha"],
        "best_compression_upper_bound_bits": best["compression_upper_bound_bits"],
        "best_beats_random_guess": best["beats_random_guess"],
        "bounds": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoding", type=Path, required=True)
    parser.add_argument("--training-risk", type=Path, required=True)
    parser.add_argument("--validation-risk", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confidence-delta", type=float, default=0.05)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output already exists: {args.output}")
    encoding = json.loads(args.encoding.read_text())
    training = json.loads(args.training_risk.read_text())
    validation = json.loads(args.validation_risk.read_text()) if args.validation_risk else None
    archive = Path(encoding["archive"])
    actual_bits = archive.stat().st_size * 8
    decoded = Path(encoding["decoded_checkpoint"])
    if (
        actual_bits != encoding["encoded_weight_bits"]
        or sha256_file(archive) != encoding["archive_sha256"]
        or sha256_file(decoded) != encoding["decoded_checkpoint_sha256"]
    ):
        raise ValueError("encoded artifacts do not match encoding summary")
    report = build_report(
        encoding, training, validation, args.confidence_delta, actual_bits
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n")
    temporary.replace(args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
