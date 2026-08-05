#!/usr/bin/env python3
"""Write the seed-wise development-only summary from completed curve runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .curve_results import summarize_results_root
from .formal_plan import DEFAULT_RUN_PLAN, verify_formal_run_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_RUN_PLAN)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = verify_formal_run_plan(args.plan)
    summary = summarize_results_root(
        plan,
        args.results_root,
        output_path=args.output,
    )
    print(
        json.dumps(
            {
                "evaluation_role": summary["evaluation_role"],
                "completed_model_count": summary["completed_model_count"],
                "expected_model_count": summary["expected_model_count"],
                "complete": summary["complete"],
                "output": str(
                    (args.output or args.results_root.resolve() / "curve_summary.json")
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
