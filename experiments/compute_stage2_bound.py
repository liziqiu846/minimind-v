#!/usr/bin/env python3
"""Compute the predeclared Stage 2 smoothed compression bound."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.generalization_bound import (
    description_complexity_nats,
    finite_hypothesis_bound,
    prediction_smoothing_interval,
)
from experiments.stage2_protocol import (
    DEFAULT_DRAFT,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--adapter-summary", type=Path, required=True)
    parser.add_argument("--decoded-model-hash", type=Path, required=True)
    parser.add_argument("--decoded-training-risk", type=Path, required=True)
    parser.add_argument("--decoded-validation-risk", type=Path)
    parser.add_argument("--unquantized-training-risk", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--formal", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"bound output already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=args.formal)
    if args.formal and protocol.payload.get("schema_version") == 2:
        protocol.verify_runtime_integrity()
    summary = json.loads(args.adapter_summary.read_text(encoding="utf-8"))
    decoded_hash = json.loads(args.decoded_model_hash.read_text(encoding="utf-8"))
    training = json.loads(args.decoded_training_risk.read_text(encoding="utf-8"))
    validation = (
        json.loads(args.decoded_validation_risk.read_text(encoding="utf-8"))
        if args.decoded_validation_risk else None
    )
    unquantized = (
        json.loads(args.unquantized_training_risk.read_text(encoding="utf-8"))
        if args.unquantized_training_risk else None
    )
    reference = protocol.reference()
    artifacts = [summary, decoded_hash, training]
    if validation:
        artifacts.append(validation)
    if unquantized:
        artifacts.append(unquantized)
    if any(artifact.get("protocol") != reference for artifact in artifacts):
        raise ValueError("bound input does not reference the selected Stage 2 protocol")
    group_root = (summary["model_group"], summary["mapping_root"])
    if any(
        (artifact.get("model_group"), artifact.get("mapping_root")) != group_root
        for artifact in [training] + ([validation] if validation else []) + ([unquantized] if unquantized else [])
    ):
        raise ValueError("bound inputs do not describe the same model")
    if training["model_kind"] != "decoded_quantized" or training["image_condition"] != "correct":
        raise ValueError("bound requires decoded quantized correct-image training risk")
    if training["data"]["role"] != "train":
        raise ValueError("bound empirical risk must come from training images")
    if training["model_state_sha256"] != decoded_hash["decoded_model_state_sha256"]:
        raise ValueError("training risk model differs from clean decoded model")
    archive = Path(summary["archive_path"])
    if (
        sha256_file(archive) != summary["archive_sha256"]
        or archive.stat().st_size * 8 != summary["complexity_bits"]
        or training["adapter"]["sha256"] != summary["archive_sha256"]
    ):
        raise ValueError("transmitted adapter provenance is inconsistent")
    if validation:
        if (
            validation["model_kind"] != "decoded_quantized"
            or validation["image_condition"] != "correct"
            or validation["data"]["role"] != "validation"
            or validation["model_state_sha256"] != decoded_hash["decoded_model_state_sha256"]
        ):
            raise ValueError("validation risk provenance is inconsistent")
    if unquantized and (
        unquantized["model_kind"] != "unquantized"
        or unquantized["image_condition"] != "correct"
        or unquantized["data"]["role"] != "train"
    ):
        raise ValueError("unquantized training risk provenance is inconsistent")

    evaluation = protocol.payload["evaluation"]
    delta = evaluation["per_model_delta"] if args.formal else protocol.payload["development"]["selection_delta"]
    complexity_bits = int(summary["complexity_bits"])
    complexity_nats = description_complexity_nats(complexity_bits)
    empirical = float(training["risk"]["mean_sample_risk_bits"])
    sample_count = int(training["data"]["sample_count"])
    interval = prediction_smoothing_interval(evaluation["vocab_size"], evaluation["alpha"])
    result = finite_hypothesis_bound(
        empirical,
        interval,
        complexity_nats,
        sample_count,
        delta,
    )
    output = {
        "schema_version": 1,
        "formal": args.formal,
        "model_group": group_root[0],
        "mapping_root": group_root[1],
        "protocol": reference,
        "confidence_delta": delta,
        "independent_train_samples": sample_count,
        "alpha": evaluation["alpha"],
        "vocab_size": evaluation["vocab_size"],
        "complexity": {
            "adapter_bytes": archive.stat().st_size,
            "adapter_bits": complexity_bits,
            "description_complexity_nats": complexity_nats,
            "formula": "C*ln(2)+2*ln(C)",
        },
        "risk": {
            "unquantized_training_bits": (
                None if unquantized is None else unquantized["risk"]["mean_sample_risk_bits"]
            ),
            "decoded_training_bits": empirical,
            "decoded_validation_bits": (
                None if validation is None else validation["risk"]["mean_sample_risk_bits"]
            ),
            "quantization_increase_bits": (
                None if unquantized is None else empirical - unquantized["risk"]["mean_sample_risk_bits"]
            ),
            "observed_generalization_gap_bits": (
                None if validation is None else validation["risk"]["mean_sample_risk_bits"] - empirical
            ),
        },
        "bound": {
            "loss_lower_bits": result.loss_interval.lower_bits,
            "loss_upper_bits": result.loss_interval.upper_bits,
            "loss_width_bits": result.loss_interval.width_bits,
            "generalization_penalty_bits": result.generalization_penalty_bits,
            "raw_compression_upper_bound_bits": result.compression_upper_bound_bits,
            "clipped_certified_upper_bits": result.clipped_certified_upper_bits,
            "random_baseline_bits": result.random_guess_bits,
            "nonvacuous_margin_bits": result.random_guess_margin_bits,
            "beats_random_baseline": result.beats_random_guess,
            "exceeds_smoothed_loss_maximum": result.exceeds_theoretical_max,
            "primary_is_raw_unclipped": True,
        },
        "inputs": {
            "adapter_summary_sha256": sha256_file(args.adapter_summary),
            "decoded_model_hash_sha256": sha256_file(args.decoded_model_hash),
            "decoded_training_risk_sha256": sha256_file(args.decoded_training_risk),
            "decoded_validation_risk_sha256": (
                None if args.decoded_validation_risk is None else sha256_file(args.decoded_validation_risk)
            ),
            "unquantized_training_risk_sha256": (
                None if args.unquantized_training_risk is None else sha256_file(args.unquantized_training_risk)
            ),
        },
    }
    if not math.isfinite(output["bound"]["raw_compression_upper_bound_bits"]):
        raise FloatingPointError("Stage 2 bound is not finite")
    write_json_atomic(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
