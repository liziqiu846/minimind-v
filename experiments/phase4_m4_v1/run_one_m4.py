#!/usr/bin/env python3
"""Run one frozen M4 config; no hyperparameter override arguments exist."""

from __future__ import annotations

import argparse
import json
from typing import Any

from experiments.phase4_m4_v1.m4_configs import (
    load_frozen_config,
    reject_runtime_overrides,
)
from experiments.phase4_m4_v1.quantize_m4 import quantize
from experiments.phase4_m4_v1.score_m4 import inspect_config_adapter
from experiments.phase4_m4_v1.train_m4 import train


def run(config_id: str, *, runtime_overrides: dict[str, Any] | None = None):
    reject_runtime_overrides(runtime_overrides)
    config, receipt = load_frozen_config(config_id)
    training = train(config_id)
    quantization = quantize(config_id)
    scoring_adapter = inspect_config_adapter(config_id)
    return {
        "schema_version": 1,
        "status": "engineering_pipeline_complete",
        "config_id": config["config_id"],
        "config": receipt,
        "training_manifest": training,
        "quantization_summary": quantization,
        "scoring_adapter": scoring_adapter,
        "full_risk_scoring_executed": False,
        "certified": False,
        "exploratory": True,
        "u_statistic_implemented": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run(args.config_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
