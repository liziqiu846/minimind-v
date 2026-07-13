#!/usr/bin/env python3
"""Summarize completed A/B/C runs into one JSON and CSV table."""

import argparse
import csv
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def risk_at(result: dict, alpha: float) -> float:
    return next(
        item["mean_sample_risk_bits"]
        for item in result["risks"]
        if item["alpha"] == alpha
    )


def summarize_run(run_dir: Path, alpha: float) -> dict:
    manifest = load(run_dir / "manifest.json")
    encoding = load(run_dir / "compression/q4.json")
    bound = load(run_dir / "bound_q4.json")
    train_raw = load(run_dir / "risk_train_unquantized.json")
    validation_raw = load(run_dir / "risk_validation_unquantized.json")
    train_q4 = load(run_dir / "risk_train_q4.json")
    validation_q4 = load(run_dir / "risk_validation_q4.json")

    raw_train = risk_at(train_raw, alpha)
    raw_validation = risk_at(validation_raw, alpha)
    q4_train = risk_at(train_q4, alpha)
    q4_validation = risk_at(validation_q4, alpha)
    return {
        "run_id": manifest["run_id"],
        "freeze_llm": manifest["model"]["freeze_llm"],
        "trainable_parameters": manifest["model"]["trainable_parameters"],
        "encoded_weight_bits": encoding["encoded_weight_bits"],
        "risk_alpha": alpha,
        "unquantized_train_risk_bits": raw_train,
        "unquantized_validation_risk_bits": raw_validation,
        "unquantized_gap_bits": raw_validation - raw_train,
        "q4_train_risk_bits": q4_train,
        "q4_validation_risk_bits": q4_validation,
        "q4_gap_bits": q4_validation - q4_train,
        "q4_train_degradation_bits": q4_train - raw_train,
        "best_bound_alpha": bound["best_alpha"],
        "best_compression_upper_bound_bits": bound[
            "best_compression_upper_bound_bits"
        ],
        "best_bound_beats_random_guess": bound["best_beats_random_guess"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha", type=float, default=0.0001)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dirs = sorted(args.run_root.glob(f"*_seed{args.seed}"))
    rows = [summarize_run(run_dir, args.alpha) for run_dir in run_dirs]
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(rows, indent=2) + "\n")
    with args.output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
