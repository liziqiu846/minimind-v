#!/usr/bin/env python3
"""Select Stage 2 development LRs or summarize the ten formal results."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import DEFAULT_DRAFT, Stage2Protocol, sha256_file, write_json_atomic


def bound_files(run_root: Path) -> list[Path]:
    return sorted(run_root.glob("[0-9][0-9]_*/bound.json"))


def choose_lr(rows: list[dict], tie_width: float = 1e-4) -> tuple[float, dict[str, float]]:
    means = {
        str(lr): statistics.fmean(
            row["bound"]["raw_compression_upper_bound_bits"]
            for row in rows if row["learning_rate"] == lr
        )
        for lr in sorted({row["learning_rate"] for row in rows})
    }
    minimum = min(means.values())
    selected = min(float(lr) for lr, mean in means.items() if mean <= minimum + tie_width)
    return selected, means


def development_summary(protocol: Stage2Protocol, run_root: Path) -> dict:
    paths = bound_files(run_root)
    if len(paths) != 36:
        raise ValueError(f"expected 36 development bounds, found {len(paths)}")
    rows = []
    for path in paths:
        bound = json.loads(path.read_text(encoding="utf-8"))
        training = json.loads((path.parent / "train/training_manifest.json").read_text())
        if bound["formal"] or bound["protocol"] != protocol.reference():
            raise ValueError("development bound provenance mismatch")
        rows.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "model_group": bound["model_group"],
                "mapping_root": bound["mapping_root"],
                "train_seed": training["train_seed"],
                "learning_rate": training["learning_rate"],
                "bound": bound["bound"],
                "risk": bound["risk"],
                "complexity": bound["complexity"],
            }
        )
    counts = {group: sum(row["model_group"] == group for row in rows) for group in ("M0", "M1", "M2", "M3")}
    if counts != {group: 9 for group in counts}:
        raise ValueError(f"development group counts are wrong: {counts}")
    m0, m0_means = choose_lr([row for row in rows if row["model_group"] == "M0"])
    m1, m1_means = choose_lr([row for row in rows if row["model_group"] == "M1"])
    joint, joint_means = choose_lr([row for row in rows if row["model_group"] in ("M2", "M3")])
    return {
        "schema_version": 1,
        "purpose": "learning-rate selection only; not formal evidence",
        "protocol": protocol.reference(),
        "run_count": len(rows),
        "selection_delta": protocol.payload["development"]["selection_delta"],
        "tie_rule": protocol.payload["development"]["tie_rule"],
        "mean_raw_bounds_by_learning_rate": {
            "M0": m0_means, "M1": m1_means, "M2_M3_joint": joint_means
        },
        "selected_learning_rates": {"M0": m0, "M1": m1, "M2_M3": joint},
        "runs": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("development", "formal"), required=True)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"summary already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=args.mode == "formal")
    if args.mode == "development":
        summary = development_summary(protocol, args.run_root)
    else:
        paths = bound_files(args.run_root)
        if len(paths) != 10:
            raise ValueError(f"expected ten formal bounds, found {len(paths)}")
        bounds = [json.loads(path.read_text()) | {"path": str(path), "sha256": sha256_file(path)} for path in paths]
        if any(not row["formal"] or row["protocol"] != protocol.reference() for row in bounds):
            raise ValueError("formal bound provenance mismatch")
        keyed = {(row["model_group"], row["mapping_root"]): row for row in bounds}
        paired = []
        for root in (43101, 43102, 43103):
            m0 = keyed[("M0", root)]["bound"]["raw_compression_upper_bound_bits"]
            m2 = keyed[("M2", root)]["bound"]["raw_compression_upper_bound_bits"]
            m3 = keyed[("M3", root)]["bound"]["raw_compression_upper_bound_bits"]
            paired.append({
                "mapping_root": root,
                "vision_cost_T_bits": m3 - m0,
                "shared_gain_G_bits": m2 - m3,
            })
        summary = {
            "schema_version": 1,
            "protocol": protocol.reference(),
            "formal_model_count": 10,
            "bounds": bounds,
            "paired_differences": paired,
            "descriptive_means": {
                "vision_cost_T_bits": statistics.fmean(row["vision_cost_T_bits"] for row in paired),
                "shared_gain_G_bits": statistics.fmean(row["shared_gain_G_bits"] for row in paired),
            },
            "best_mapping_root_selected": False,
        }
    write_json_atomic(args.output, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
