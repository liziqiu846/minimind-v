#!/usr/bin/env python3
"""Render development-only module budget value curves from a frozen summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic

from . import CURVE_NAMES, MODULES

MODULE_COLORS = {
    "vision": "#0072B2",
    "projector": "#D55E00",
    "language": "#009E73",
}
CURVE_TITLES = {
    "vision": r"$R_V$ · vision",
    "projector": r"$R_C$ · projector",
    "language": r"$R_L$ · language",
}
SUPPORTED_FORMATS = ("png", "pdf", "svg")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("evaluation_role") != "development_only":
        raise ValueError("figure source must be marked development_only")
    if payload.get("complete") is not True:
        raise ValueError("figure source must be a complete formal curve summary")
    if payload.get("completed_model_count") != payload.get(
        "expected_model_count"
    ):
        raise ValueError("figure source model counts differ")

    seeds = payload.get("seeds")
    if (
        not isinstance(seeds, list)
        or not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
    ):
        raise ValueError("figure source seeds are invalid")
    by_seed = payload.get("by_seed")
    if not isinstance(by_seed, Mapping):
        raise ValueError("figure source lacks seed-wise curves")
    for seed in seeds:
        seed_payload = by_seed.get(str(seed))
        if not isinstance(seed_payload, Mapping):
            raise ValueError(f"figure source lacks seed {seed}")
        curves = seed_payload.get("curves")
        if not isinstance(curves, Mapping):
            raise ValueError(f"figure source seed {seed} lacks curves")
        for module in MODULES:
            curve = curves.get(module)
            if not isinstance(curve, Mapping):
                raise ValueError(f"figure source lacks {module} for seed {seed}")
            if (
                curve.get("curve_name") != CURVE_NAMES[module]
                or curve.get("target_module") != module
                or curve.get("evaluation_role") != "development_only"
                or curve.get("sort_key") != "target_module_encoded_bits"
                or curve.get("optimality_metric") != "development_task_risk"
                or curve.get("visual_gain_role") != "guardrail_only"
            ):
                raise ValueError(f"figure source metadata differs for {seed}/{module}")
            points = curve.get("points")
            adjacent = curve.get("adjacent_differences")
            if (
                not isinstance(points, list)
                or len(points) < 2
                or curve.get("point_count") != len(points)
                or not isinstance(adjacent, list)
                or len(adjacent) != len(points) - 1
            ):
                raise ValueError(f"figure source point count differs for {seed}/{module}")
            bits = []
            for point in points:
                encoded_bits = point.get("target_module_encoded_bits")
                risk = point.get("development_task_risk")
                if (
                    isinstance(encoded_bits, bool)
                    or not isinstance(encoded_bits, int)
                    or not math.isfinite(float(risk))
                ):
                    raise ValueError(
                        f"figure source point is invalid for {seed}/{module}"
                    )
                bits.append(encoded_bits)
            if bits != sorted(bits):
                raise ValueError(
                    f"figure source is not actual-bit sorted for {seed}/{module}"
                )
            if sum(bool(point.get("is_anchor")) for point in points) != 1:
                raise ValueError(
                    f"figure source anchor count differs for {seed}/{module}"
                )
            for index, difference in enumerate(adjacent):
                lower = points[index]
                upper = points[index + 1]
                delta_bits = (
                    upper["target_module_encoded_bits"]
                    - lower["target_module_encoded_bits"]
                )
                delta_risk = (
                    upper["development_task_risk"]
                    - lower["development_task_risk"]
                )
                if (
                    difference.get("delta_bits") != delta_bits
                    or not math.isclose(
                        float(difference.get("delta_risk")),
                        float(delta_risk),
                        rel_tol=0.0,
                        abs_tol=1e-15,
                    )
                ):
                    raise ValueError(
                        f"figure source adjacent difference differs for "
                        f"{seed}/{module}"
                    )
                marginal = difference.get("marginal_value")
                if delta_bits > 0:
                    expected = -delta_risk / delta_bits
                    if (
                        difference.get("status") != "valid"
                        or marginal is None
                        or not math.isclose(
                            float(marginal),
                            float(expected),
                            rel_tol=1e-12,
                            abs_tol=1e-18,
                        )
                    ):
                        raise ValueError(
                            f"figure source marginal value differs for "
                            f"{seed}/{module}"
                        )
                elif (
                    difference.get("status") != "invalid_nonpositive_delta_bits"
                    or marginal is not None
                ):
                    raise ValueError(
                        f"figure source invalid edge differs for {seed}/{module}"
                    )
    return dict(payload)


def _load_matplotlib(style_file: Path | None):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.ticker import StrMethodFormatter
    except ImportError as error:
        raise RuntimeError(
            "plot rendering requires matplotlib from the repository requirements"
        ) from error

    if style_file is not None:
        resolved = style_file.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"matplotlib style does not exist: {resolved}")
        plt.style.use(resolved)
    else:
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "font.family": "sans-serif",
                "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                "font.size": 8,
                "axes.labelsize": 9,
                "axes.titlesize": 9,
                "axes.spines.top": False,
                "axes.spines.right": False,
                "axes.linewidth": 0.6,
                "xtick.labelsize": 7,
                "ytick.labelsize": 7,
                "legend.fontsize": 7,
                "savefig.facecolor": "white",
            }
        )
    plt.rcParams["figure.autolayout"] = False
    plt.rcParams["figure.constrained_layout.use"] = False
    return plt, Line2D, StrMethodFormatter


def _summary_legend_handles(Line2D):
    return [
        Line2D(
            [0],
            [0],
            color="#333333",
            linestyle="-",
            marker="o",
            markerfacecolor="#333333",
            markeredgecolor="white",
            markeredgewidth=0.5,
            linewidth=1.4,
            label="3-seed median curve",
        ),
        Line2D(
            [0],
            [0],
            color="black",
            linestyle="none",
            marker="*",
            markerfacecolor="white",
            markeredgecolor="black",
            markeredgewidth=0.8,
            markersize=8,
            label="P-4096 anchor",
        ),
    ]


def _module_summary_points(
    summary: Mapping[str, Any],
    module: str,
) -> list[dict[str, Any]]:
    seeds = summary["seeds"]
    by_coordinate: dict[int, dict[int, Mapping[str, Any]]] = {}
    for seed in seeds:
        curve = summary["by_seed"][str(seed)]["curves"][module]
        for point in curve["points"]:
            coordinate = int(point["coordinate_dimensions"][module])
            if seed in by_coordinate.setdefault(coordinate, {}):
                raise ValueError(
                    f"duplicate coordinate {coordinate} for {seed}/{module}"
                )
            by_coordinate[coordinate][seed] = point

    rows = []
    for coordinate, by_seed in by_coordinate.items():
        if set(by_seed) != set(seeds):
            raise ValueError(
                f"coordinate {coordinate} is not shared by all seeds for {module}"
            )
        bits = [int(by_seed[seed]["target_module_encoded_bits"]) for seed in seeds]
        risks = [float(by_seed[seed]["development_task_risk"]) for seed in seeds]
        rows.append(
            {
                "coordinate": coordinate,
                "median_bits": float(statistics.median(bits)),
                "median_risk": float(statistics.median(risks)),
                "is_anchor": all(
                    bool(by_seed[seed]["is_anchor"]) for seed in seeds
                ),
            }
        )
    return sorted(rows, key=lambda row: row["median_bits"])


def _risk_figure(summary: Mapping[str, Any], plt, Line2D, StrMethodFormatter):
    figure, axes = plt.subplots(
        1,
        len(MODULES),
        figsize=(7.6, 3.15),
        sharey=True,
    )
    for panel_index, (axis, module) in enumerate(zip(axes, MODULES)):
        color = MODULE_COLORS[module]
        rows = _module_summary_points(summary, module)
        medians_x = [row["median_bits"] for row in rows]
        medians_y = [row["median_risk"] for row in rows]
        axis.plot(
            medians_x,
            medians_y,
            color=color,
            linewidth=1.4,
            alpha=0.9,
            marker="o",
            markersize=4.8,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.6,
            zorder=2,
        )
        for row in rows:
            if row["is_anchor"]:
                axis.scatter(
                    [row["median_bits"]],
                    [row["median_risk"]],
                    marker="*",
                    s=105,
                    facecolor="white",
                    edgecolor="black",
                    linewidth=0.9,
                    zorder=5,
                )
        axis.set_title(CURVE_TITLES[module])
        axis.set_xlabel("Target module encoded bits")
        axis.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        axis.grid(axis="y", color="#BDBDBD", linewidth=0.4, alpha=0.35)
        axis.text(
            -0.13,
            1.04,
            chr(ord("A") + panel_index),
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            va="bottom",
        )
    axes[0].set_ylabel("Development task risk")
    figure.suptitle(
        "Module budget value curves · development-only",
        fontsize=10,
        y=1.04,
    )
    figure.legend(
        handles=_summary_legend_handles(Line2D),
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=2,
        frameon=False,
    )
    figure.text(
        0.5,
        -0.035,
        "Points are coordinate-wise medians across 3 seeds. "
        "Seed-level markers are omitted. No smoothing.",
        ha="center",
        fontsize=7,
    )
    figure.tight_layout(rect=(0.0, 0.04, 1.0, 0.91), w_pad=1.4)
    return figure


def _marginal_figure(
    summary: Mapping[str, Any],
    plt,
    StrMethodFormatter,
):
    figure, axes = plt.subplots(
        1,
        len(MODULES),
        figsize=(7.6, 3.15),
        sharey=True,
    )
    invalid_edges = 0
    for panel_index, (axis, module) in enumerate(zip(axes, MODULES)):
        color = MODULE_COLORS[module]
        rows = _module_summary_points(summary, module)
        midpoints = []
        marginal_values = []
        for lower, upper in zip(rows, rows[1:]):
            lower_bits = float(lower["median_bits"])
            upper_bits = float(upper["median_bits"])
            delta_bits = upper_bits - lower_bits
            midpoints.append((lower_bits + upper_bits) / 2.0)
            if delta_bits <= 0:
                marginal_values.append(math.nan)
                invalid_edges += 1
                continue
            delta_risk = float(upper["median_risk"]) - float(
                lower["median_risk"]
            )
            marginal_values.append(-delta_risk / delta_bits * 1e6)
        axis.plot(
            midpoints,
            marginal_values,
            color=color,
            linewidth=1.4,
            alpha=0.9,
            marker="o",
            markersize=4.8,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.6,
        )
        axis.axhline(0.0, color="#777777", linewidth=0.7, alpha=0.7)
        axis.set_title(CURVE_TITLES[module])
        axis.set_xlabel("Adjacent-bit interval midpoint")
        axis.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        axis.grid(axis="y", color="#BDBDBD", linewidth=0.4, alpha=0.35)
        axis.text(
            -0.13,
            1.04,
            chr(ord("A") + panel_index),
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            va="bottom",
        )
    axes[0].set_ylabel(r"Marginal value $\eta$ ($10^{-6}$ risk/bit)")
    figure.suptitle(
        "Adjacent marginal values · development-only",
        fontsize=10,
        y=1.04,
    )
    anomaly_note = (
        f" Invalid edges marked ×: {invalid_edges}."
        if invalid_edges
        else " All adjacent bit deltas are positive."
    )
    figure.text(
        0.5,
        -0.035,
        "Adjacent finite differences of the displayed 3-seed median curves. "
        "Positive values mean lower risk at the next point. No smoothing."
        + anomaly_note,
        ha="center",
        fontsize=7,
    )
    figure.tight_layout(rect=(0.0, 0.04, 1.0, 0.91), w_pad=1.4)
    return figure, invalid_edges


def _save_figure(
    figure,
    output_dir: Path,
    stem: str,
    formats: Sequence[str],
    *,
    dpi: int,
) -> dict[str, dict[str, Any]]:
    files = {}
    for file_format in formats:
        path = output_dir / f"{stem}.{file_format}"
        figure.savefig(
            path,
            format=file_format,
            dpi=dpi if file_format == "png" else 300,
            bbox_inches="tight",
            pad_inches=0.06,
            facecolor="white",
            edgecolor="none",
        )
        files[file_format] = {
            "path": str(path.resolve()),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
    return files


def render_curve_figures(
    summary_path: Path,
    output_dir: Path,
    *,
    formats: Sequence[str] = SUPPORTED_FORMATS,
    dpi: int = 450,
    style_file: Path | None = None,
) -> dict[str, Any]:
    """Validate a formal summary and render risk and adjacent-value figures."""
    source = summary_path.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"curve summary does not exist: {source}")
    summary = _validated_summary(json.loads(source.read_text(encoding="utf-8")))
    normalized_formats = tuple(dict.fromkeys(fmt.lower() for fmt in formats))
    if not normalized_formats or any(
        fmt not in SUPPORTED_FORMATS for fmt in normalized_formats
    ):
        raise ValueError(
            f"formats must be selected from {', '.join(SUPPORTED_FORMATS)}"
        )
    if dpi < 300:
        raise ValueError("PNG resolution must be at least 300 DPI")

    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    plt, Line2D, StrMethodFormatter = _load_matplotlib(style_file)
    risk_figure = _risk_figure(summary, plt, Line2D, StrMethodFormatter)
    marginal_figure, invalid_edges = _marginal_figure(
        summary,
        plt,
        StrMethodFormatter,
    )
    try:
        figures = {
            "development_risk_curves": {
                "files": _save_figure(
                    risk_figure,
                    destination,
                    "phase3_module_budget_development_risk",
                    normalized_formats,
                    dpi=dpi,
                ),
                "x_axis": "target_module_encoded_bits",
                "y_axis": "development_task_risk",
                "summary": "coordinate-wise 3-seed median only",
                "individual_points": "omitted",
                "seed_variability": "not rendered",
                "smoothing": "none",
            },
            "marginal_value_curves": {
                "files": _save_figure(
                    marginal_figure,
                    destination,
                    "phase3_module_budget_marginal_value",
                    normalized_formats,
                    dpi=dpi,
                ),
                "x_axis": "adjacent_median_actual_bit_interval_midpoint",
                "y_axis": "median_curve_marginal_value_times_1e6",
                "rendering": "three-panel median-curve finite-difference lines",
                "aggregation": "coordinate-wise 3-seed median curve",
                "estimator": "adjacent_finite_difference_only_no_smoothing",
                "invalid_edge_count": invalid_edges,
            },
        }
    finally:
        plt.close(risk_figure)
        plt.close(marginal_figure)

    manifest = {
        "schema_version": 1,
        "status": "complete",
        "evaluation_role": "development_only",
        "source_summary_path": str(source),
        "source_summary_sha256": _sha256(source),
        "seeds": summary["seeds"],
        "formats": list(normalized_formats),
        "png_dpi": dpi,
        "style_file": None if style_file is None else str(style_file.resolve()),
        "figures": figures,
    }
    write_json_atomic(destination / "figure_manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--formats",
        nargs="+",
        default=list(SUPPORTED_FORMATS),
        choices=SUPPORTED_FORMATS,
    )
    parser.add_argument("--dpi", type=int, default=450)
    parser.add_argument("--style-file", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir or args.summary.resolve().parent / "figures"
    manifest = render_curve_figures(
        args.summary,
        output_dir,
        formats=args.formats,
        dpi=args.dpi,
        style_file=args.style_file,
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "evaluation_role": manifest["evaluation_role"],
                "source_summary_sha256": manifest["source_summary_sha256"],
                "output_dir": str(output_dir.resolve()),
                "figures": manifest["figures"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
