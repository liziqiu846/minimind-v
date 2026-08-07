#!/usr/bin/env python3
"""Build a deterministic index for the frozen LITMAP-07 searches."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from experiments.phase3.build_litmap03_search_index import normalized_title
from experiments.phase3.build_litmap06_search_index import (
    BACKENDS,
    add_arxiv,
    add_openalex,
    add_semantic_scholar,
    prior_titles,
)
from experiments.phase3.run_litmap07_search import QUERIES


def family_from_path(path: Path) -> str:
    match = re.match(r"(.+)_(?:arxiv|openalex|semanticscholar)$", path.stem)
    if not match:
        raise ValueError(f"unexpected LITMAP-07 filename: {path}")
    return match.group(1)


def discovery_paths(source_dir: Path, backend: str) -> list[Path]:
    return [
        path
        for path in sorted(source_dir.glob(f"*_{backend}.*"))
        if family_from_path(path) in QUERIES
    ]


def mechanism_from_family(family: str) -> str:
    if family.startswith("factorization_"):
        return "shared_cross_modal_factorization"
    if family.startswith("credit_"):
        return "autoregressive_visual_credit"
    if family.startswith("trainability_"):
        return "representation_trainability_ceiling"
    if family.startswith("theory_"):
        return "formal_theory_tool"
    raise ValueError(f"unexpected query family: {family}")


def relevance_score(rec: dict[str, Any]) -> tuple[int, list[str]]:
    text = f"{rec['title']} {' '.join(rec['abstracts'])}".casefold()
    title = rec["title"].casefold()
    score = 0
    reasons: list[str] = []
    groups = [
        (
            8,
            "direct-generative-vlm",
            (
                "multimodal large language model",
                "large vision-language model",
                "large vision language model",
                "vision-language model",
                "vision language model",
                "mllm",
                "llava",
            ),
        ),
        (
            7,
            "factorization-or-rule-reuse",
            (
                "factorized representation",
                "factorised representation",
                "shared representation",
                "modular representation",
                "rule reuse",
                "systematic generalization",
                "compositional generalization",
                "unseen combination",
                "unseen composition",
            ),
        ),
        (
            6,
            "credit-or-imbalance",
            (
                "credit assignment",
                "modality imbalance",
                "language dominance",
                "language bias",
                "visual shortcut",
                "gradient conflict",
                "gradient imbalance",
                "training dynamics",
            ),
        ),
        (
            6,
            "trainability-or-expressivity",
            (
                "frozen vision encoder",
                "frozen visual encoder",
                "frozen features",
                "expressivity",
                "expressive power",
                "adapter",
                "projector",
                "connector",
                "parameter-efficient",
            ),
        ),
        (
            5,
            "formal-optimization-tool",
            (
                "theorem",
                "provably",
                "implicit bias",
                "identifiability",
                "population minimizer",
                "gradient descent",
                "optimization landscape",
            ),
        ),
        (
            3,
            "directional-generalization",
            (
                "held-out",
                "out-of-distribution",
                "out of distribution",
                "transfer",
                "generalization",
            ),
        ),
        (
            2,
            "mechanism-intervention",
            (
                "controlled",
                "ablation",
                "regularization",
                "training objective",
                "curriculum",
                "balanc",
            ),
        ),
    ]
    for points, label, phrases in groups:
        if any(phrase in text for phrase in phrases):
            score += points
            reasons.append(label)
    penalties = [
        (-8, "survey", ("survey", "review", "overview")),
        (
            -7,
            "special-domain",
            (
                "medical",
                "radiology",
                "pathology",
                "remote sensing",
                "autonomous driving",
                "point cloud",
                "audio",
                "speech",
            ),
        ),
        (-5, "generation-only", ("text-to-image", "image generation", "diffusion")),
        (-4, "benchmark-only", ("benchmark", "evaluation")),
    ]
    for points, label, phrases in penalties:
        if any(phrase in title for phrase in phrases):
            score += points
            reasons.append(label)
    if len(rec["backends"]) >= 2:
        score += 2
        reasons.append("multi-backend")
    if len(rec["families"]) >= 2:
        score += 2
        reasons.append("multi-query")
    return score, reasons


def serialise(rec: dict[str, Any], prior: set[str]) -> dict[str, Any]:
    score, reasons = relevance_score(rec)
    families = sorted(rec["families"])
    mechanisms = sorted({mechanism_from_family(family) for family in families})
    dates = sorted(value for value in rec["published"] if value)
    return {
        "score": score,
        "mechanisms": ";".join(mechanisms),
        "title": rec["title"],
        "year": dates[0][:4] if dates else "",
        "families": ";".join(families),
        "backends": ";".join(sorted(rec["backends"])),
        "arxiv_ids": ";".join(sorted(rec["arxiv_ids"])),
        "dois": ";".join(sorted(value for value in rec["dois"] if value)),
        "openalex_ids": ";".join(
            sorted(value for value in rec["openalex_ids"] if value)
        ),
        "venues": ";".join(sorted(value for value in rec["venues"] if value)),
        "cited_by_count": rec["cited_by_count"],
        "prior_search_duplicate": normalized_title(rec["title"]) in prior,
        "relevance_reasons": ";".join(reasons),
        "authors": ";".join(sorted(author for author in rec["authors"] if author)),
        "urls": ";".join(sorted(rec["urls"])),
        "abstract": max(rec["abstracts"], key=len, default=""),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("sources/litmap07"))
    parser.add_argument("--project-sources", type=Path, default=Path("sources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/LITMAP-07_round1/SEARCH_INDEX.tsv"),
    )
    args = parser.parse_args()

    records: dict[str, dict[str, Any]] = {}
    raw_records = 0
    for path in discovery_paths(args.source_dir, "arxiv"):
        raw_records += add_arxiv(path, records)
    for path in discovery_paths(args.source_dir, "openalex"):
        raw_records += add_openalex(path, records)
    for path in discovery_paths(args.source_dir, "semanticscholar"):
        raw_records += add_semantic_scholar(path, records)

    prior = prior_titles(args.project_sources, args.source_dir)
    rows = [serialise(record, prior) for record in records.values()]
    rows.sort(
        key=lambda row: (-row["score"], -row["cited_by_count"], row["title"].casefold())
    )
    if not rows:
        raise RuntimeError("no LITMAP-07 discovery records found")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "output": str(args.output),
        "raw_records": raw_records,
        "unique_titles": len(rows),
        "prior_search_duplicates": sum(row["prior_search_duplicate"] for row in rows),
        "score_ge_15": sum(row["score"] >= 15 for row in rows),
        "backend_files": {
            backend: len(discovery_paths(args.source_dir, backend))
            for backend in BACKENDS
        },
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
