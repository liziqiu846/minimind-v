#!/usr/bin/env python3
"""Train one XID-01 round4 M2-current condition."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

import experiments.train_vissup01_model as shared
from experiments.stage2_model import build_stage2_model
from experiments.xid01 import (
    CONDITIONS,
    MAPPING_ROOTS,
    TOTAL_STEPS,
    TOTAL_TRAIN_ROWS,
)


DIMENSIONS = {"language": 1_187, "projector": 2_327, "vision": 582}


def model_builder(protocol, mapping_root, dimensions, *, device):
    if dict(dimensions) != DIMENSIONS:
        raise ValueError("XID-01 requires frozen M2-current dimensions")
    return build_stage2_model(
        "M2", protocol, mapping_root, device=device, dtype=torch.float32
    )


SPEC = {
    "candidate": "XID-01",
    "round": 4,
    "conditions": CONDITIONS,
    "mapping_roots": MAPPING_ROOTS,
    "dimensions_by_condition": {
        condition: DIMENSIONS for condition in CONDITIONS
    },
    "data_condition_by_condition": {
        condition: condition for condition in CONDITIONS
    },
    "model_builder": model_builder,
    "projection_preflight": None,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--mapping-root", type=int, choices=MAPPING_ROOTS, required=True)
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> None:
    shared.CONDITIONS = CONDITIONS
    shared.MAPPING_ROOTS = MAPPING_ROOTS
    shared.TOTAL_TRAIN_ROWS = TOTAL_TRAIN_ROWS
    shared.TOTAL_STEPS = TOTAL_STEPS
    shared.train(parse_args(), spec=SPEC)


if __name__ == "__main__":
    main()
