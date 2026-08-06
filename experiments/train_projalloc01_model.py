#!/usr/bin/env python3
"""Train one frozen PROJALLOC-01 allocation condition and mapping root."""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.projalloc01 import (
    CONDITIONS,
    MAPPING_ROOTS,
    TRAINING_SPEC,
    verify_prepared_dir,
)
from experiments.train_vissup01_model import train


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument(
        "--mapping-root", type=int, choices=MAPPING_ROOTS, required=True
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verify_prepared_dir(args.prepared_dir)
    train(args, spec=TRAINING_SPEC)


if __name__ == "__main__":
    main()
