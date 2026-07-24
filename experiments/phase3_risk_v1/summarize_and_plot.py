#!/usr/bin/env python3
"""Join risks with observed code lengths and render the four requested figures."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_v6.scoring.common import atomic_write_json


METHOD_COLORS = {"M2": "#0072B2", "M3": "#D55E00"}
BUDGET_MARKERS = {"low": "v", "current": "o", "high": "^", "legacy": "s"}
DELTA_COLORS = {"nonpositive": "#009E73", "positive": "#E69F00"}


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    columns = list(rows[0])
    if any(list(row) != columns for row in rows):
        raise ValueError("CSV rows have inconsistent columns")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="raise", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def join_summary_rows(
    model_summary_csv: Path, complexity_json: Path
) -> list[dict[str, Any]]:
    risk_rows = _load_csv(model_summary_csv)
    complexity = _load_json(complexity_json)
    complexity_by = {
        str(row["model_id"]): row for row in complexity["models"]
    }
    output = []
    for row in risk_rows:
        if row["method"] not in ("M2", "M3"):
            continue
        model_id = row["model_id"]
        if model_id not in complexity_by:
            raise ValueError(f"complexity result is missing for {model_id}")
        code = complexity_by[model_id]
        output.append(
            {
                "model_id": model_id,
                "method": row["method"],
                "budget": row["budget"],
                "experiment_seed": int(row["experiment_seed"]),
                "total_coordinate_budget": int(
                    code["coordinate_count_total"]
                ),
                "archive_bits": int(code["archive_bits"]),
                "external_selection_bits": int(
                    code["external_selection_bits"]
                ),
                "external_hyperparameter_bits": int(
                    code["external_hyperparameter_bits"]
                ),
                "total_description_bits": int(
                    code["total_description_bits"]
                ),
                "empirical_language_risk": float(
                    row["empirical_language_risk"]
                ),
                "empirical_visual_risk": float(
                    row["empirical_visual_risk"]
                ),
                "empirical_total_semantic_risk": float(
                    row["empirical_total_semantic_risk"]
                ),
                "empirical_visual_gain": float(
                    row["empirical_visual_gain"]
                ),
                "exploratory_language_radius": float(
                    row["exploratory_language_radius"]
                ),
                "exploratory_visual_radius": float(
                    row["exploratory_visual_radius"]
                ),
                "certified": row["certified"].lower() == "true",
                "comparison_claim": (
                    "equal_coordinate_budget_not_equal_description_length"
                ),
            }
        )
    output.sort(
        key=lambda row: (
            row["budget"].encode("utf-8"),
            row["experiment_seed"],
            row["method"].encode("utf-8"),
        )
    )
    if not output:
        raise ValueError("no M2/M3 summary rows were found")
    return output


def paired_differences(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (
            str(row["budget"]),
            int(row["experiment_seed"]),
            str(row["method"]),
        ): row
        for row in rows
    }
    pair_keys = sorted(
        {
            (str(row["budget"]), int(row["experiment_seed"]))
            for row in rows
        },
        key=lambda value: (value[0].encode("utf-8"), value[1]),
    )
    output = []
    for budget, seed in pair_keys:
        missing = [
            method
            for method in ("M2", "M3")
            if (budget, seed, method) not in by_key
        ]
        if missing:
            raise ValueError(
                f"incomplete M2/M3 pair for {budget}/{seed}: {missing}"
            )
        m2 = by_key[(budget, seed, "M2")]
        m3 = by_key[(budget, seed, "M3")]
        if int(m2["total_coordinate_budget"]) != int(
            m3["total_coordinate_budget"]
        ):
            raise ValueError("paired M2/M3 coordinate budgets differ")
        output.append(
            {
                "budget": budget,
                "experiment_seed": seed,
                "difference_direction": "M3_minus_M2",
                "total_coordinate_budget": int(
                    m2["total_coordinate_budget"]
                ),
                "delta_language_risk": float(
                    m3["empirical_language_risk"]
                )
                - float(m2["empirical_language_risk"]),
                "delta_visual_risk": float(m3["empirical_visual_risk"])
                - float(m2["empirical_visual_risk"]),
                "delta_total_semantic_risk": float(
                    m3["empirical_total_semantic_risk"]
                )
                - float(m2["empirical_total_semantic_risk"]),
                "delta_description_bits": int(
                    m3["total_description_bits"]
                )
                - int(m2["total_description_bits"]),
            }
        )
    return output


def render_plots(
    rows: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
    output_dir: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError as error:
        raise RuntimeError(
            "plot rendering requires matplotlib from the repository requirements"
        ) from error

    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = sorted({int(row["experiment_seed"]) for row in rows})
    seed_rank = {seed: index for index, seed in enumerate(seeds)}

    def scatter_style(row: Mapping[str, Any]) -> dict[str, Any]:
        color = METHOD_COLORS[str(row["method"])]
        return {
            "marker": BUDGET_MARKERS[str(row["budget"])],
            "facecolors": color if row["method"] == "M2" else "none",
            "edgecolors": color,
            "linewidths": 1.2,
            "s": 58,
        }

    def annotation_style(row: Mapping[str, Any]) -> dict[str, Any]:
        rank = seed_rank[int(row["experiment_seed"])]
        offsets = (
            ((5, 7), (5, 18), (5, -15))
            if row["method"] == "M2"
            else ((5, -15), (5, 7), (5, 18))
        )
        return {
            "text": str(row["experiment_seed"]),
            "xytext": offsets[rank % len(offsets)],
        }

    def add_encoding_legend(axis) -> None:
        method_handles = [
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                markerfacecolor=(
                    METHOD_COLORS[method] if method == "M2" else "none"
                ),
                markeredgecolor=METHOD_COLORS[method],
                markeredgewidth=1.2,
                label=method,
            )
            for method in ("M2", "M3")
        ]
        budget_handles = [
            Line2D(
                [0],
                [0],
                marker=BUDGET_MARKERS[budget],
                linestyle="none",
                markerfacecolor="none",
                markeredgecolor="black",
                label=budget,
            )
            for budget in ("low", "current", "high")
        ]
        axis.legend(
            handles=method_handles + budget_handles,
            fontsize=7,
            ncol=2,
            loc="best",
            frameon=True,
        )

    def save_figure(figure, filename: str) -> None:
        stem = Path(filename).stem
        figure.savefig(
            output_dir / f"{stem}.png",
            dpi=300,
            bbox_inches="tight",
        )
        figure.savefig(
            output_dir / f"{stem}.pdf",
            bbox_inches="tight",
        )

    def scatter_bits(metric: str, ylabel: str, filename: str, reference=None):
        figure, axis = plt.subplots(figsize=(8, 5))
        for row in rows:
            axis.errorbar(
                row["total_description_bits"],
                row[metric],
                yerr=row[
                    "exploratory_language_radius"
                    if metric == "empirical_language_risk"
                    else "exploratory_visual_radius"
                ],
                color=METHOD_COLORS[row["method"]],
                capsize=2.5,
                elinewidth=0.8,
                alpha=0.8,
                fmt="none",
                zorder=1,
            )
            axis.scatter(
                row["total_description_bits"],
                row[metric],
                **scatter_style(row),
                zorder=2,
            )
            annotation = annotation_style(row)
            axis.annotate(
                annotation["text"],
                (row["total_description_bits"], row[metric]),
                xytext=annotation["xytext"],
                textcoords="offset points",
                fontsize=7,
            )
        if reference is not None:
            axis.axhline(reference, color="black", linestyle="--", linewidth=1)
        axis.set_xlabel("total_description_bits (observed)")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.2)
        add_encoding_legend(axis)
        figure.text(
            0.5,
            0.01,
            "Labels show seeds. Vertical bars are exploratory Hoeffding "
            "radii, not formal certification intervals.",
            ha="center",
            fontsize=8,
        )
        figure.tight_layout(rect=(0, 0.045, 1, 1))
        save_figure(figure, filename)
        plt.close(figure)

    scatter_bits(
        "empirical_language_risk",
        "empirical operational language risk",
        "figure1_description_bits_vs_language_risk.png",
    )
    scatter_bits(
        "empirical_visual_risk",
        "empirical visual risk",
        "figure2_description_bits_vs_visual_risk.png",
        reference=0.5,
    )

    figure, axis = plt.subplots(figsize=(8, 5))
    for row in rows:
        axis.errorbar(
            row["empirical_language_risk"],
            row["empirical_visual_risk"],
            xerr=row["exploratory_language_radius"],
            yerr=row["exploratory_visual_radius"],
            color=METHOD_COLORS[row["method"]],
            capsize=2.5,
            elinewidth=0.8,
            alpha=0.8,
            fmt="none",
            zorder=1,
        )
        axis.scatter(
            row["empirical_language_risk"],
            row["empirical_visual_risk"],
            **scatter_style(row),
            zorder=2,
        )
    axis.axhline(0.5, color="black", linestyle="--", linewidth=1)
    axis.set_xlabel("empirical operational language risk")
    axis.set_ylabel("empirical visual risk")
    axis.grid(alpha=0.2)
    add_encoding_legend(axis)
    figure.text(
        0.5,
        0.01,
        "Bars are exploratory Hoeffding radii, not formal certification "
        "intervals; model identifiers are in the companion CSV.",
        ha="center",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.045, 1, 1))
    save_figure(figure, "figure3_language_risk_vs_visual_risk.png")
    plt.close(figure)

    labels = [
        f"{row['budget']}\n{row['experiment_seed']}" for row in pairs
    ]
    metrics = (
        ("delta_language_risk", "Δ language risk"),
        ("delta_visual_risk", "Δ visual risk"),
        ("delta_total_semantic_risk", "Δ total semantic risk"),
        ("delta_description_bits", "Δ description bits"),
    )
    figure, axes = plt.subplots(2, 2, figsize=(11, 7))
    for panel_label, axis, (metric, title) in zip(
        "ABCD", axes.flat, metrics, strict=True
    ):
        values = [float(row[metric]) for row in pairs]
        colors = [
            DELTA_COLORS["nonpositive"]
            if value <= 0
            else DELTA_COLORS["positive"]
            for value in values
        ]
        axis.bar(range(len(values)), values, color=colors)
        axis.axhline(0.0, color="black", linewidth=0.8)
        axis.set_xticks(range(len(labels)), labels, fontsize=7)
        axis.set_title(f"{title} (M3−M2)")
        axis.grid(axis="y", alpha=0.2)
        axis.text(
            -0.12,
            1.05,
            panel_label,
            transform=axis.transAxes,
            fontsize=11,
            fontweight="bold",
        )
    figure.tight_layout()
    save_figure(figure, "figure4_paired_m3_minus_m2.png")
    plt.close(figure)


def summarize(
    model_summary_csv: Path,
    complexity_json: Path,
    output_dir: Path,
    *,
    skip_plots: bool,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        rows = join_summary_rows(model_summary_csv, complexity_json)
        pairs = paired_differences(rows)
        _write_csv(temporary / "unified_model_summary.csv", rows)
        atomic_write_json(
            temporary / "unified_model_summary.json",
            {
                "schema_version": 1,
                "comparison_claim": (
                    "equal_coordinate_budget_not_equal_description_length"
                ),
                "models": rows,
            },
        )
        _write_csv(temporary / "paired_differences.csv", pairs)
        atomic_write_json(
            temporary / "paired_differences.json",
            {"schema_version": 1, "pairs": pairs},
        )
        if not skip_plots:
            render_plots(rows, pairs, temporary / "plots")
        plot_files = (
            sorted(path.name for path in (temporary / "plots").iterdir())
            if not skip_plots
            else []
        )
        receipt = {
            "status": "passed",
            "model_count": len(rows),
            "pair_count": len(pairs),
            "plots_rendered": not skip_plots,
            "plot_files": plot_files,
            "comparison_claim": (
                "equal_coordinate_budget_not_equal_description_length"
            ),
            "certified_model_count": sum(bool(row["certified"]) for row in rows),
        }
        atomic_write_json(temporary / "summary_receipt.json", receipt)
        temporary.replace(destination)
        return receipt
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-summary-csv", type=Path, required=True)
    parser.add_argument("--complexity-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-plots", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = summarize(
        args.model_summary_csv,
        args.complexity_json,
        args.output_dir,
        skip_plots=args.skip_plots,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
