#!/usr/bin/env python3
"""Combine an encoded model and its smoothed training risk into a bound report."""

import argparse
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.generalization_bound import (
    choice_description_bits,
    description_complexity_nats,
    finite_hypothesis_bound,
    prediction_smoothing_interval,
)
from experiments.quantize_checkpoint import sha256_file


def decoder_registry_selection(registry: dict, choice: dict) -> tuple[int, int]:
    """Validate a decoder choice and return registry size and code length."""
    total_choices = 0
    selected = False
    for family in registry["families"]:
        axes = family.get("axes")
        if axes is not None:
            family_choices = math.prod(len(values) for values in axes.values())
        elif "choices" in family:
            family_choices = len(family["choices"])
        else:
            family_choices = family["choice_count"]
        total_choices += family_choices
        if family["name"] != choice.get("family"):
            continue
        if axes is None:
            selected = (
                choice.get("choice") in family["choices"]
                if "choices" in family
                else True
            )
        else:
            selected = all(choice.get(name) in values for name, values in axes.items())
    if not selected:
        raise ValueError("encoded decoder choice is absent from the registry")
    return total_choices, choice_description_bits(total_choices)


def validate_risk_provenance(
    encoding: dict, training_risk: dict, validation_risk: dict | None
) -> None:
    run_id = encoding["run_id"]
    if training_risk["run_id"] != run_id:
        raise ValueError("training risk run_id does not match the encoding")
    if training_risk.get("model_kind") != "decoded_quantized":
        raise ValueError("training risk must use the decoded quantized model")
    if training_risk.get("image_condition") != "correct":
        raise ValueError("training risk must use correctly paired images")
    if not training_risk.get("model_assets"):
        raise ValueError("training risk must identify its fixed model assets")
    expected_alpha_bits = choice_description_bits(len(training_risk["risks"]))
    if training_risk["alpha_choice_bits"] != expected_alpha_bits:
        raise ValueError("alpha choice length does not match the evaluated grid")
    if validation_risk:
        if validation_risk["run_id"] != run_id:
            raise ValueError("validation risk run_id does not match the encoding")
        if validation_risk.get("model_kind") != "decoded_quantized":
            raise ValueError("validation risk must use the decoded quantized model")
        if validation_risk.get("image_condition") != "correct":
            raise ValueError("bound validation diagnostic must use correctly paired images")
        if training_risk.get("model_assets") != validation_risk.get("model_assets"):
            raise ValueError("training and validation risks used different model assets")


def validate_manifest(manifest: dict, encoding: dict, training_risk: dict) -> None:
    if manifest["run_id"] != encoding["run_id"]:
        raise ValueError("run manifest does not match the encoding")
    if manifest["data"]["sha256"] != training_risk["data_sha256"]:
        raise ValueError("training risk data does not match the run manifest")
    if manifest["data"]["examples"] != training_risk["sample_count"]:
        raise ValueError("training sample count does not match the run manifest")
    if manifest["initial_weight"]["sha256"] != encoding["reference_sha256"]:
        raise ValueError("encoding reference does not match the run manifest")


def build_report(
    encoding: dict,
    training_risk: dict,
    validation_risk: dict | None,
    confidence_delta: float,
    encoded_weight_bits: int,
    model_selection_bits: int = 0,
) -> dict:
    if model_selection_bits < 0:
        raise ValueError("model_selection_bits cannot be negative")
    validate_risk_provenance(encoding, training_risk, validation_risk)
    decoded_sha = encoding["decoded_checkpoint_sha256"]
    if training_risk["checkpoint_sha256"] != decoded_sha:
        raise ValueError("training risk was not evaluated on the encoded hypothesis")
    if validation_risk and validation_risk["checkpoint_sha256"] != decoded_sha:
        raise ValueError("validation risk checkpoint does not match the encoded hypothesis")

    alpha_bits = training_risk["alpha_choice_bits"]
    hyperparameter_bits = alpha_bits + model_selection_bits
    complexity = description_complexity_nats(encoded_weight_bits, hyperparameter_bits)
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
        "model_selection_bits": model_selection_bits,
        "total_hyperparameter_bits": hyperparameter_bits,
        "description_complexity_nats": complexity,
        "archive_sha256": encoding["archive_sha256"],
        "decoded_checkpoint_sha256": decoded_sha,
        "training_data_sha256": training_risk["data_sha256"],
        "validation_data_sha256": (
            validation_risk["data_sha256"] if validation_risk else None
        ),
        "model_assets": training_risk["model_assets"],
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
    parser.add_argument("--model-selection-bits", type=int, default=0)
    parser.add_argument("--decoder-registry", type=Path)
    parser.add_argument("--run-manifest", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output already exists: {args.output}")
    encoding = json.loads(args.encoding.read_text())
    training = json.loads(args.training_risk.read_text())
    validation = json.loads(args.validation_risk.read_text()) if args.validation_risk else None
    manifest_metadata = {}
    if args.run_manifest:
        validate_manifest(
            json.loads(args.run_manifest.read_text()), encoding, training
        )
        manifest_metadata = {
            "run_manifest": str(args.run_manifest.resolve()),
            "run_manifest_sha256": sha256_file(args.run_manifest),
        }
    registry_metadata = {}
    model_selection_bits = args.model_selection_bits
    if args.decoder_registry:
        if model_selection_bits:
            raise ValueError("use either decoder registry or manual selection bits")
        registry = json.loads(args.decoder_registry.read_text())
        choice_count, model_selection_bits = decoder_registry_selection(
            registry, encoding["decoder_choice"]
        )
        registry_metadata = {
            "decoder_registry": str(args.decoder_registry.resolve()),
            "decoder_registry_sha256": sha256_file(args.decoder_registry),
            "decoder_choice_count": choice_count,
            "decoder_choice": encoding["decoder_choice"],
        }
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
        encoding,
        training,
        validation,
        args.confidence_delta,
        actual_bits,
        model_selection_bits,
    )
    report.update(manifest_metadata)
    report.update(registry_metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n")
    temporary.replace(args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
