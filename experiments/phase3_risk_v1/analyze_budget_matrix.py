#!/usr/bin/env python3
"""Combine 12 new runs with six frozen current models into the 18-model matrix."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import statistics
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_risk_v1.budget_configs import (
    BUDGET_TOTALS,
    MAPPING_ROOTS,
)
from experiments.phase3_risk_v1.budget_runtime import load_frozen_config
from experiments.phase3_risk_v1.exploratory_bounds import (
    analyze_model_summaries,
)
from experiments.phase3_risk_v1.summarize_and_plot import (
    paired_differences,
    render_plots,
)
from experiments.phase3_v6.scoring.common import (
    REPO_ROOT,
    atomic_write_json,
    sha256_file,
)


BACKFILL_ROOT = (
    REPO_ROOT / "experiments/phase3_risk_v1/results/v6_backfill"
)
CURRENT_COMPLEXITY = (
    REPO_ROOT / "experiments/phase3_risk_v1/results/v6_complexity.json"
)
INVALID_REASONS = [
    "post_hoc_metric_design",
    "coupled_mismatch_donors",
]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    columns = list(rows[0])
    if any(list(row) != columns for row in rows):
        raise ValueError(f"inconsistent CSV columns for {path}")
    csv_rows = [
        {
            key: (
                "|".join(str(item) for item in value)
                if isinstance(value, (list, tuple))
                else value
            )
            for key, value in row.items()
        }
        for row in rows
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(csv_rows)


def _current_inputs() -> tuple[dict[str, dict], dict[str, dict]]:
    complexity = _load_json(CURRENT_COMPLEXITY)
    codes = {
        str(row["model_id"]): row for row in complexity["models"]
    }
    risks = {}
    for method in ("M2", "M3"):
        for root in MAPPING_ROOTS:
            old_id = f"{method}-root-{root}"
            risks[old_id] = _load_json(
                BACKFILL_ROOT / f"model_summaries/{old_id}.json"
            )
    return codes, risks


def _load_all(
    artifact_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    current_codes, current_risks = _current_inputs()
    preliminary = []
    risk_summaries = []
    category_rows = []
    for budget in ("low", "current", "high"):
        for root in MAPPING_ROOTS:
            for method in ("M2", "M3"):
                config_id = f"{method}-{budget}-seed-{root}"
                config, config_receipt = load_frozen_config(config_id)
                if budget == "current":
                    old_id = f"{method}-root-{root}"
                    risk = dict(current_risks[old_id])
                    risk["model_id"] = config_id
                    code = current_codes[old_id]
                    archive_bits = int(code["archive_bits"])
                    source = {
                        "source": "frozen_existing_current_v6_backfill",
                        "source_model_id": old_id,
                        "risk_summary_path": str(
                            BACKFILL_ROOT
                            / f"model_summaries/{old_id}.json"
                        ),
                        "archive_complexity_path": str(CURRENT_COMPLEXITY),
                    }
                else:
                    run_dir = (
                        artifact_root.resolve()
                        / config["output_relative_path"]
                    )
                    run = _load_json(run_dir / "run_receipt.json")
                    if run.get("status") != "complete":
                        raise RuntimeError(f"incomplete run: {config_id}")
                    risk = _load_json(run_dir / "scoring/risk_summary.json")
                    adapter = _load_json(
                        run_dir / "encode/adapter_summary.json"
                    )
                    if (
                        adapter.get("config", {}).get("sha256")
                        != config_receipt["sha256"]
                    ):
                        raise ValueError(
                            f"adapter config hash mismatch: {config_id}"
                        )
                    archive_bits = int(adapter["archive_bits"])
                    source = {
                        "source": "new_budget_run",
                        "run_dir": str(run_dir),
                        "run_receipt": str(run_dir / "run_receipt.json"),
                        "risk_summary_path": str(
                            run_dir / "scoring/risk_summary.json"
                        ),
                        "adapter_summary_path": str(
                            run_dir / "encode/adapter_summary.json"
                        ),
                    }
                if (
                    risk.get("method") != method
                    or int(risk.get("image_count", 0)) != 1343
                    or risk.get("identity_check", {}).get("passes") is not True
                ):
                    raise ValueError(f"invalid risk summary: {config_id}")
                risk = dict(risk)
                risk["model_id"] = config_id
                risk_summaries.append(risk)
                external_selection = int(config["external_selection_bits"])
                external_hyper = int(
                    config["external_hyperparameter_bits"]
                )
                preliminary.append(
                    {
                        "model_id": config_id,
                        "budget": budget,
                        "model_group": method,
                        "method": method,
                        "mapping_root": root,
                        "experiment_seed": root,
                        "coordinate_count": config[
                            "total_coordinate_budget"
                        ],
                        "total_coordinate_budget": config[
                            "total_coordinate_budget"
                        ],
                        "archive_bits": archive_bits,
                        "external_selection_bits": external_selection,
                        "external_hyperparameter_bits": external_hyper,
                        "total_description_bits": (
                            archive_bits
                            + external_selection
                            + external_hyper
                        ),
                        "empirical_language_risk": risk["empirical_risks"][
                            "language_risk"
                        ],
                        "empirical_visual_risk": risk["empirical_risks"][
                            "visual_risk"
                        ],
                        "empirical_total_semantic_risk": risk[
                            "empirical_risks"
                        ]["total_semantic_risk"],
                        "empirical_visual_gain": risk["empirical_risks"][
                            "visual_gain"
                        ],
                        "maximum_identity_error": max(
                            risk["identity_check"][
                                "maximum_error_record"
                            ],
                            risk["identity_check"][
                                "maximum_error_image_group"
                            ],
                        ),
                        "certified": False,
                        "invalid_for_formal_certification_reasons": list(
                            INVALID_REASONS
                        ),
                        "comparison_claim": (
                            "equal_coordinate_budget_not_equal_"
                            "description_length"
                        ),
                        "result_source": source["source"],
                        "result_path": source.get(
                            "run_dir", source["risk_summary_path"]
                        ),
                    }
                )
                for category in risk["category_summaries"]:
                    row = {
                        "model_id": config_id,
                        "budget": budget,
                        "method": method,
                        "mapping_root": root,
                        "category": category["category"],
                        "record_count": category["record_count"],
                        "image_count": category["image_count"],
                    }
                    for metric in (
                        "language_risk",
                        "visual_risk",
                        "total_semantic_risk",
                        "visual_gain",
                    ):
                        row[f"{metric}_mean"] = category["metrics"][
                            metric
                        ]["mean"]
                        row[
                            f"{metric}_standard_deviation_population"
                        ] = category["metrics"][metric][
                            "standard_deviation_population"
                        ]
                    category_rows.append(row)
    return preliminary, risk_summaries, category_rows


def _budget_summary(
    models: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_model: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(
        list
    )
    for row in models:
        by_model[(str(row["budget"]), str(row["method"]))].append(row)
    by_pair: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in pairs:
        by_pair[str(row["budget"])].append(row)
    metrics = (
        "empirical_language_risk",
        "empirical_visual_risk",
        "empirical_total_semantic_risk",
        "empirical_visual_gain",
        "archive_bits",
        "total_description_bits",
    )
    deltas = (
        "delta_language_risk",
        "delta_visual_risk",
        "delta_total_semantic_risk",
        "delta_description_bits",
    )
    output = []
    for budget in ("low", "current", "high"):
        pair_rows = by_pair[budget]
        for method in ("M2", "M3"):
            rows = by_model[(budget, method)]
            if len(rows) != 3 or len(pair_rows) != 3:
                raise ValueError(f"incomplete three-root summary: {budget}")
            result: dict[str, Any] = {
                "budget": budget,
                "method": method,
                "root_count": 3,
                "standard_deviation_definition": "population",
            }
            for metric in metrics:
                values = [float(row[metric]) for row in rows]
                result[f"{metric}_mean"] = statistics.fmean(values)
                result[
                    f"{metric}_standard_deviation"
                ] = statistics.pstdev(values)
            for metric in deltas:
                values = [float(row[metric]) for row in pair_rows]
                signs = [
                    "positive"
                    if value > 0
                    else "negative"
                    if value < 0
                    else "zero"
                    for value in values
                ]
                result[f"{metric}_mean"] = statistics.fmean(values)
                result[
                    f"{metric}_standard_deviation"
                ] = statistics.pstdev(values)
                result[f"{metric}_signs"] = "|".join(signs)
                result[f"{metric}_sign_consistent"] = len(set(signs)) == 1
            output.append(result)
    return output


def analyze(artifact_root: Path, output_dir: Path) -> dict:
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    started = time.time()
    try:
        rows, risk_summaries, category_rows = _load_all(artifact_root)
        bounds = analyze_model_summaries(
            risk_summaries,
            candidate_family_size=18,
            delta=0.05,
            analysis_mode="current_coupled_post_hoc",
            metrics_predeclared=False,
            fresh_confirmation_set=False,
            independent_frozen_donor_bank=False,
        )
        if bounds["certified"] is not False or bounds[
            "invalid_for_formal_certification_reasons"
        ] != INVALID_REASONS:
            raise RuntimeError("exploratory certification status is invalid")
        bound_by = {row["model_id"]: row for row in bounds["models"]}
        for row in rows:
            bound = bound_by[row["model_id"]]
            row["exploratory_language_radius"] = bound["language_risk"][
                "exploratory_radius"
            ]
            row["exploratory_visual_radius"] = bound["visual_risk"][
                "exploratory_radius"
            ]
            row["exploratory_total_semantic_radius"] = bound[
                "total_semantic_risk_separate_exploratory_family"
            ]["exploratory_radius"]
            row["exploratory_hoeffding_radius"] = bound["visual_risk"][
                "exploratory_radius"
            ]
        pairs = paired_differences(rows)
        budget_rank = {"low": 0, "current": 1, "high": 2}
        pairs.sort(
            key=lambda row: (
                budget_rank[str(row["budget"])],
                int(row["experiment_seed"]),
            )
        )
        if len(rows) != 18 or len(pairs) != 9:
            raise RuntimeError("unified matrix dimensions are not 18/9")
        budget_summary = _budget_summary(rows, pairs)

        _write_csv(temporary / "model_summary.csv", rows)
        atomic_write_json(
            temporary / "model_summary.json",
            {
                "schema_version": 1,
                "model_count": len(rows),
                "comparison_claim": (
                    "equal_coordinate_budget_not_equal_description_length"
                ),
                "certified": False,
                "invalid_for_formal_certification_reasons": INVALID_REASONS,
                "models": rows,
            },
        )
        _write_csv(temporary / "paired_differences.csv", pairs)
        atomic_write_json(
            temporary / "paired_differences.json",
            {"schema_version": 1, "pair_count": len(pairs), "pairs": pairs},
        )
        _write_csv(temporary / "budget_summary.csv", budget_summary)
        atomic_write_json(
            temporary / "budget_summary.json",
            {"schema_version": 1, "summaries": budget_summary},
        )
        _write_csv(temporary / "category_summary.csv", category_rows)
        atomic_write_json(
            temporary / "category_summary.json",
            {
                "schema_version": 1,
                "model_count": len(rows),
                "categories": category_rows,
            },
        )
        atomic_write_json(
            temporary / "exploratory_bounds.json", bounds
        )
        render_plots(rows, pairs, temporary / "plots")

        tracked = [
            path
            for path in temporary.rglob("*")
            if path.is_file() and path.name != "run_receipt.json"
        ]
        file_hashes = {
            str(path.relative_to(temporary)): sha256_file(path)
            for path in sorted(tracked)
        }
        receipt = {
            "schema_version": 1,
            "status": "passed",
            "model_count": len(rows),
            "new_model_count": 12,
            "existing_current_model_count": 6,
            "pair_count": len(pairs),
            "budget_count": len(BUDGET_TOTALS),
            "roots": list(MAPPING_ROOTS),
            "comparison_claim": (
                "equal_coordinate_budget_not_equal_description_length"
            ),
            "certified": False,
            "invalid_for_formal_certification_reasons": INVALID_REASONS,
            "all_identity_errors_at_most_1e_6": all(
                float(row["maximum_identity_error"]) <= 1e-6
                for row in rows
            ),
            "all_risks_in_range": all(
                0.0 <= float(row[metric]) <= 1.0
                for row in rows
                for metric in (
                    "empirical_language_risk",
                    "empirical_visual_risk",
                    "empirical_total_semantic_risk",
                )
            ),
            "file_sha256": file_hashes,
            "artifact_root": str(artifact_root.resolve()),
            "seconds": time.time() - started,
        }
        atomic_write_json(temporary / "run_receipt.json", receipt)
        temporary.replace(destination)
        return receipt
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.artifact_root, args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
