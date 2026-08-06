#!/usr/bin/env python3
"""Mechanically audit all formal artifacts and P/S fairness receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import load_protocol, sha256_file, write_json_atomic
from .configs import generate_matrix


def audit(results_root: Path, output: Path) -> dict:
    protocol = load_protocol()
    matrix = generate_matrix()
    failures = []
    receipts = []
    loaded = {}
    for config in matrix:
        root = results_root / config["config_id"]
        training_path = root / "training_manifest.json"
        development_path = root / "development" / "development_result.json"
        if not training_path.is_file() or not development_path.is_file():
            failures.append(f"{config['config_id']}: missing terminal artifact")
            continue
        training = json.loads(training_path.read_text())
        development = json.loads(development_path.read_text())
        loaded[config["config_id"]] = training
        checks = {
            "status_complete": training["status"] == development["status"] == "complete",
            "identity_exact": all(
                training[key] == config[key] for key in ("structure", "budget", "seed")
            ),
            "optimizer_plain_sgd": (
                training["optimizer"]["name"] == "torch.optim.SGD"
                and training["optimizer"]["momentum"] == 0.0
                and training["optimizer"]["weight_decay"] == 0.0
            ),
            "optimizer_steps_exact": (
                training["actual_optimizer_steps"]
                == protocol["training"]["total_optimizer_steps"]
            ),
            "diagnosis_steps_exact": (
                training["diagnosis_step_count"]
                == len(protocol["diagnosis"]["optimizer_steps"])
            ),
            "checkpoint_sha256_exact": (
                sha256_file(training["checkpoint"]["path"])
                == training["checkpoint"]["sha256"]
            ),
            "mms2_sha256_exact": (
                sha256_file(training["MMS2"]["path"]) == training["MMS2"]["sha256"]
            ),
            "diagnosis_sha256_exact": (
                sha256_file(training["diagnosis"]["path"])
                == training["diagnosis"]["sha256"]
            ),
            "development_bindings_exact": (
                development["mms2_sha256"] == training["MMS2"]["sha256"]
                and development["checkpoint_sha256"] == training["checkpoint"]["sha256"]
            ),
        }
        if not all(checks.values()):
            failures.append(f"{config['config_id']}: failed {checks}")
        receipts.append({
            "config_id": config["config_id"],
            "checks": checks,
            "training_manifest_sha256": sha256_file(training_path),
            "development_result_sha256": sha256_file(development_path),
        })
    pair_checks = []
    for budget in (2048, 8192):
        for seed in (43101, 43102, 43103):
            p = loaded[f"P-budget-{budget}-seed-{seed}"]
            s = loaded[f"S-budget-{budget}-seed-{seed}"]
            check = {
                "budget": budget,
                "seed": seed,
                "same_epoch_permutations": (
                    [row["permutation_sha256"] for row in p["epoch_receipts"]]
                    == [row["permutation_sha256"] for row in s["epoch_receipts"]]
                ),
                "same_optimizer": p["optimizer"] == s["optimizer"],
                "same_optimizer_steps": (
                    p["actual_optimizer_steps"] == s["actual_optimizer_steps"] == 1875
                ),
                "same_diagnosis_step_count": (
                    p["diagnosis_step_count"] == s["diagnosis_step_count"] == 11
                ),
            }
            if not all(value for key, value in check.items() if key.startswith("same_")):
                failures.append(f"P/S fairness failure: {check}")
            pair_checks.append(check)
    result = {
        "schema_version": 1,
        "status": "PASS" if not failures and len(receipts) == 12 else "FAIL",
        "model_count": len(receipts),
        "matrix_has_no_4096": all(row["budget"] != 4096 for row in matrix),
        "artifact_receipts": receipts,
        "pair_fairness_checks": pair_checks,
        "failures": failures,
    }
    write_json_atomic(output, result)
    if result["status"] != "PASS":
        raise RuntimeError("formal result audit failed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.results_root, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
