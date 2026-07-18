#!/usr/bin/env python3
"""Compute the predeclared paired visual diagnostic bootstrap intervals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import DEFAULT_FROZEN, Stage2Protocol, sha256_file, write_json_atomic


def bootstrap_mean_interval(
    units: np.ndarray,
    repetitions: int,
    seed: int,
    *,
    chunk_size: int = 250,
) -> tuple[float, float, str]:
    if units.ndim != 1 or len(units) < 2 or not np.all(np.isfinite(units)):
        raise ValueError("bootstrap units must be a finite one-dimensional array")
    rng = np.random.Generator(np.random.PCG64(seed))
    means = np.empty(repetitions, dtype=np.float64)
    offset = 0
    while offset < repetitions:
        count = min(chunk_size, repetitions - offset)
        indices = rng.integers(0, len(units), size=(count, len(units)))
        means[offset:offset + count] = units[indices].mean(axis=1, dtype=np.float64)
        offset += count
    lower, upper = np.quantile(means, (0.025, 0.975), method="linear")
    digest = __import__("hashlib").sha256(means.astype("<f8").tobytes()).hexdigest()
    return float(lower), float(upper), digest


def load_risk(path: Path, condition: str, protocol: Stage2Protocol) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (
        payload.get("protocol") != protocol.reference()
        or payload.get("model_kind") != "decoded_quantized"
        or payload.get("image_condition") != condition
        or payload.get("data", {}).get("role") != "validation"
    ):
        raise ValueError(f"diagnostic provenance mismatch: {path}")
    return payload


def analyze_run(run_dir: Path, protocol: Stage2Protocol) -> dict:
    correct_path = run_dir / "risk_decoded_validation_correct.json"
    shuffled_path = run_dir / "risk_decoded_validation_paired_shuffled.json"
    none_path = run_dir / "risk_decoded_validation_none.json"
    correct = load_risk(correct_path, "correct", protocol)
    shuffled = load_risk(shuffled_path, "paired_shuffled", protocol)
    absent = load_risk(none_path, "none", protocol)
    identities = [
        (
            payload["risk"]["sample_image_sha256"],
            payload["risk"].get("sample_id"),
        )
        for payload in (correct, shuffled, absent)
    ]
    if identities[0] != identities[1] or identities[0] != identities[2]:
        raise ValueError("diagnostic sample identity/order differs between conditions")
    correct_values = np.asarray(correct["risk"]["sample_risk_bits"], dtype=np.float64)
    shuffled_values = np.asarray(shuffled["risk"]["sample_risk_bits"], dtype=np.float64)
    none_values = np.asarray(absent["risk"]["sample_risk_bits"], dtype=np.float64)
    permutation = tuple(shuffled["pair_swap"]["permutation"])
    if len(permutation) != len(correct_values):
        raise ValueError("diagnostic permutation length is inconsistent")
    pairs = [(index, donor) for index, donor in enumerate(permutation) if index < donor]
    if len(pairs) * 2 != len(permutation):
        raise ValueError("diagnostic permutation is not a disjoint involution")
    hashes = correct["risk"]["sample_image_sha256"]
    if any(hashes[left] == hashes[right] for left, right in pairs):
        raise ValueError("diagnostic pairing contains an equal-image pair")
    mismatch_effect = shuffled_values - correct_values
    pair_units = np.asarray(
        [(mismatch_effect[left] + mismatch_effect[right]) / 2 for left, right in pairs],
        dtype=np.float64,
    )
    none_units = none_values - correct_values
    diagnostics = protocol.payload["diagnostics"]
    pair_lower, pair_upper, pair_bootstrap_hash = bootstrap_mean_interval(
        pair_units,
        diagnostics["shuffle_bootstrap"]["repetitions"],
        diagnostics["shuffle_bootstrap"]["seed"],
    )
    none_lower, none_upper, none_bootstrap_hash = bootstrap_mean_interval(
        none_units,
        diagnostics["none_bootstrap"]["repetitions"],
        diagnostics["none_bootstrap"]["seed"],
    )
    return {
        "model_group": correct["model_group"],
        "mapping_root": correct["mapping_root"],
        "sample_count": len(correct_values),
        "pair_count": len(pair_units),
        "mean_risk_bits": {
            "correct": float(correct_values.mean()),
            "paired_shuffled": float(shuffled_values.mean()),
            "none": float(none_values.mean()),
        },
        "paired_shuffled_minus_correct": {
            "unit": "mean of two sample effects inside each disjoint image pair",
            "units": len(pair_units),
            "mean_bits": float(pair_units.mean()),
            "bootstrap_ci95_lower_bits": pair_lower,
            "bootstrap_ci95_upper_bits": pair_upper,
            "bootstrap_means_sha256": pair_bootstrap_hash,
        },
        "none_minus_correct": {
            "unit": "per-image paired difference",
            "units": len(none_units),
            "mean_bits": float(none_units.mean()),
            "bootstrap_ci95_lower_bits": none_lower,
            "bootstrap_ci95_upper_bits": none_upper,
            "bootstrap_means_sha256": none_bootstrap_hash,
        },
        "inputs": {
            "correct_sha256": sha256_file(correct_path),
            "paired_shuffled_sha256": sha256_file(shuffled_path),
            "none_sha256": sha256_file(none_path),
            "pair_permutation_sha256": shuffled["pair_swap"]["permutation_sha256"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"diagnostic summary already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    if protocol.payload.get("schema_version") == 2:
        protocol.verify_runtime_integrity()
    rows = []
    for run_dir in sorted(args.run_root.glob("[0-9][0-9]_M[123]_*")):
        if (run_dir / "risk_decoded_validation_paired_shuffled.json").exists():
            rows.append(analyze_run(run_dir, protocol))
    if len(rows) != 7:
        raise ValueError(f"expected seven visual diagnostic models, found {len(rows)}")
    expected = {("M1", None)} | {
        (group, root) for group in ("M2", "M3") for root in (43101, 43102, 43103)
    }
    if {(row["model_group"], row["mapping_root"]) for row in rows} != expected:
        raise ValueError("visual diagnostic model set is incomplete")
    output = {
        "schema_version": protocol.payload.get("schema_version", 1),
        "status": "secondary descriptive only",
        "model_selection_use": False,
        "formal_hypothesis_test": False,
        "protocol": protocol.reference(),
        "bootstrap": {
            "rng": "numpy Generator PCG64",
            "repetitions": 10000,
            "interval": "percentile 95% using numpy.quantile method=linear",
            "paired_shuffle_seed": protocol.payload["diagnostics"]["shuffle_bootstrap"]["seed"],
            "none_seed": protocol.payload["diagnostics"]["none_bootstrap"]["seed"],
        },
        "models": rows,
    }
    write_json_atomic(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
