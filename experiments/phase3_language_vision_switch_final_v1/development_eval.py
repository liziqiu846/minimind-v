#!/usr/bin/env python3
"""Plan-bound wrapper around the unchanged Phase 3 v6 evaluator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.phase3_module_marginal_budget_v1 import (
    development_eval as reused,
)

from .design import training_config
from .manifest import verify_frozen_manifest

DEVELOPMENT_PROTOCOL_ID = "phase3-v6-language-vision-switch-final-reuse-v1"


def _adapted_manifest(path: Path):
    manifest = verify_frozen_manifest(path)
    return {
        **manifest,
        "anchor_config": {
            "coordinate_dimensions": manifest["base_states"]["original"]
        },
    }


def evaluate(
    *,
    plan_path: Path,
    run_id: str,
    codec_root: Path,
    checkpoint_path: Path,
    output_dir: Path,
    device: str,
):
    reused.verify_formal_run_plan = _adapted_manifest
    reused._training_config = (
        lambda run, _anchor_dimensions: training_config(run)
    )
    reused.DEVELOPMENT_PROTOCOL_ID = DEVELOPMENT_PROTOCOL_ID
    return reused.evaluate(
        plan_path=plan_path,
        run_id=run_id,
        codec_root=codec_root,
        checkpoint_path=checkpoint_path,
        output_dir=output_dir,
        device=device,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--codec-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    result = evaluate(
        plan_path=args.plan,
        run_id=args.run_id,
        codec_root=args.codec_root,
        checkpoint_path=args.checkpoint,
        output_dir=args.output_dir,
        device=args.device,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

