#!/usr/bin/env python3
"""Score one PROJALLOC-01 model on rotation and CV-Bench-2D."""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.projalloc01 import (
    CONDITIONS,
    MAPPING_ROOTS,
    SCORING_SPEC,
    verify_prepared_dir,
)
from experiments.score_vissup01_model import score


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument(
        "--mapping-root", type=int, choices=MAPPING_ROOTS, required=True
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--training-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--item-batch-size", type=int, default=8)
    parser.add_argument(
        "--mode", choices=("smoke", "full"), default="full"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verify_prepared_dir(args.prepared_dir)
    score(args, spec=SCORING_SPEC)


if __name__ == "__main__":
    main()
