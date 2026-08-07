#!/usr/bin/env python3
"""Build the deterministic index for the five frozen LITMAP-04 query families."""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from experiments.phase3.build_litmap03_search_index import (
    ARXIV_ID,
    ATOM,
    base_record,
    clean,
    normalized_title,
    reconstruct_abstract,
)


QUERY_FAMILIES = {
    "auxiliary_objective",
    "frozen_objective_match",
    "objective_competition",
    "objective_competition_gradient_expansion",
    "task_transfer",
    "visual_credit",
    "visual_credit_supervision_expansion",
}


def family_from_path(path: Path) -> str:
    match = re.match(r"research_litmap04_(.+)_(?:arxiv|openalex)$", path.stem)
    if not match:
        raise ValueError(f"unexpected LITMAP-04 filename: {path}")
    return match.group(1)


def discovery_paths(source_dir: Path, backend: str) -> list[Path]:
    paths = sorted(source_dir.glob(f"research_litmap04_*_{backend}.*"))
    return [path for path in paths if family_from_path(path) in QUERY_FAMILIES]


def add_arxiv(path: Path, records: dict[str, dict[str, Any]]) -> int:
    family = family_from_path(path)
    entries = ET.parse(path).getroot().findall("a:entry", ATOM)
    for entry in entries:
        title = clean(entry.findtext("a:title", default="", namespaces=ATOM))
        key = normalized_title(title)
        if not key:
            continue
        rec = records.setdefault(key, base_record(title))
        rec["families"].add(family)
        rec["backends"].add("arxiv")
        rec["abstracts"].append(clean(entry.findtext("a:summary", default="", namespaces=ATOM)))
        rec["published"].add(clean(entry.findtext("a:published", default="", namespaces=ATOM))[:10])
        rec["authors"].update(
            clean(author.findtext("a:name", default="", namespaces=ATOM))
            for author in entry.findall("a:author", ATOM)
        )
        identifier = clean(entry.findtext("a:id", default="", namespaces=ATOM))
        match = ARXIV_ID.search(identifier)
        if match:
            rec["arxiv_ids"].add(match.group(1))
        for link in entry.findall("a:link", ATOM):
            href = clean(link.attrib.get("href"))
            if href:
                rec["urls"].add(href)
    return len(entries)


def add_openalex(path: Path, records: dict[str, dict[str, Any]]) -> int:
    family = family_from_path(path)
    works = json.loads(path.read_text(encoding="utf-8")).get("results", [])
    for work in works:
        title = clean(work.get("title"))
        key = normalized_title(title)
        if not key:
            continue
        rec = records.setdefault(key, base_record(title))
        rec["families"].add(family)
        rec["backends"].add("openalex")
        rec["openalex_ids"].add(clean(work.get("id")))
        rec["dois"].add(clean(work.get("doi")))
        rec["published"].add(clean(work.get("publication_date")))
        rec["types"].add(clean(work.get("type")))
        rec["cited_by_count"] = max(rec["cited_by_count"], int(work.get("cited_by_count") or 0))
        rec["authors"].update(
            clean(authorship.get("author", {}).get("display_name"))
            for authorship in work.get("authorships", [])
        )
        abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
        if abstract:
            rec["abstracts"].append(abstract)
        locations = [work.get("primary_location") or {}, *work.get("locations", [])]
        for location in locations:
            source = location.get("source") or {}
            venue = clean(source.get("display_name") or location.get("raw_source_name"))
            if venue:
                rec["venues"].add(venue)
            for field in ("landing_page_url", "pdf_url"):
                url = clean(location.get(field))
                if url:
                    rec["urls"].add(url)
                    match = ARXIV_ID.search(url)
                    if match:
                        rec["arxiv_ids"].add(match.group(1))
    return len(works)


def prior_titles(source_dir: Path) -> set[str]:
    prior: set[str] = set()
    for path in sorted(source_dir.glob("research_*.xml")):
        if "litmap04" in path.name:
            continue
        try:
            entries = ET.parse(path).getroot().findall("a:entry", ATOM)
        except ET.ParseError:
            continue
        for entry in entries:
            title = clean(entry.findtext("a:title", default="", namespaces=ATOM))
            if title:
                prior.add(normalized_title(title))
    for path in sorted(source_dir.glob("research_*.json")):
        if "litmap04" in path.name:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        for work in payload.get("results", []):
            title = clean(work.get("title"))
            if title:
                prior.add(normalized_title(title))
    return prior


def relevance_score(rec: dict[str, Any]) -> tuple[int, list[str]]:
    text = f"{rec['title']} {' '.join(rec['abstracts'])}".casefold()
    score = 0
    reasons: list[str] = []
    groups = [
        (
            6,
            "autoregressive-lvlm",
            (
                "multimodal large language model",
                "multimodal llm",
                "large vision-language model",
                "large vision language model",
                "mllm",
                "llava",
            ),
        ),
        (
            6,
            "objective-gradient-mechanism",
            (
                "gradient conflict",
                "gradient routing",
                "gradient interference",
                "gradient balancing",
                "modality competition",
                "modality imbalance",
                "language dominance",
                "credit assignment",
            ),
        ),
        (
            4,
            "task-transfer",
            (
                "task-specific",
                "overfitting",
                "shortcut",
                "out-of-domain",
                "held-out",
                "transfer",
                "generalization",
            ),
        ),
        (
            4,
            "feature-objective-match",
            (
                "frozen vision encoder",
                "feature mismatch",
                "representation alignment",
                "objective alignment",
                "connector bottleneck",
                "visual representation distillation",
            ),
        ),
        (
            4,
            "mechanism-intervention",
            (
                "auxiliary objective",
                "auxiliary loss",
                "gradient projection",
                "reweight",
                "decoupl",
                "detach",
                "distill",
                "routing",
            ),
        ),
        (
            3,
            "matched-control",
            (
                "ablation",
                "controlled",
                "same parameter",
                "parameter-matched",
                "matched compute",
                "same data",
            ),
        ),
    ]
    for points, label, phrases in groups:
        if any(phrase in text for phrase in phrases):
            score += points
            reasons.append(label)
    title = rec["title"].casefold()
    penalties = [
        (-8, "survey", ("survey", "review", "overview")),
        (
            -6,
            "non-general-domain",
            ("medical", "radiology", "pathology", "remote sensing", "autonomous driving",
             "point cloud", "audio"),
        ),
        (-4, "video-only", ("video",)),
        (-4, "benchmark-only", ("benchmark", "evaluation")),
    ]
    for points, label, phrases in penalties:
        if any(phrase in title for phrase in phrases):
            score += points
            reasons.append(label)
    if len(rec["families"]) >= 2:
        score += 2
        reasons.append("multi-query-hit")
    return score, reasons


def serialise(rec: dict[str, Any], prior: set[str]) -> dict[str, Any]:
    score, reasons = relevance_score(rec)
    dates = sorted(value for value in rec["published"] if value)
    return {
        "score": score,
        "title": rec["title"],
        "year": dates[0][:4] if dates else "",
        "families": ";".join(sorted(rec["families"])),
        "backends": ";".join(sorted(rec["backends"])),
        "arxiv_ids": ";".join(sorted(rec["arxiv_ids"])),
        "dois": ";".join(sorted(rec["dois"])),
        "openalex_ids": ";".join(sorted(rec["openalex_ids"])),
        "venues": ";".join(sorted(rec["venues"])),
        "types": ";".join(sorted(rec["types"])),
        "cited_by_count": rec["cited_by_count"],
        "prior_search_duplicate": normalized_title(rec["title"]) in prior,
        "relevance_reasons": ";".join(reasons),
        "authors": ";".join(sorted(author for author in rec["authors"] if author)),
        "urls": ";".join(sorted(rec["urls"])),
        "abstract": max(rec["abstracts"], key=len, default=""),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("sources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/LITMAP-04_round1/SEARCH_INDEX.tsv"),
    )
    args = parser.parse_args()

    records: dict[str, dict[str, Any]] = {}
    raw_records = 0
    for path in discovery_paths(args.source_dir, "arxiv"):
        raw_records += add_arxiv(path, records)
    for path in discovery_paths(args.source_dir, "openalex"):
        raw_records += add_openalex(path, records)
    prior = prior_titles(args.source_dir)
    rows = [serialise(record, prior) for record in records.values()]
    rows.sort(key=lambda row: (-row["score"], -row["cited_by_count"], row["title"].casefold()))
    if not rows:
        raise RuntimeError("no LITMAP-04 discovery records found")

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
    print(
        json.dumps(
            {
                "output": str(args.output),
                "raw_records": raw_records,
                "unique_titles": len(rows),
                "prior_search_duplicates": sum(row["prior_search_duplicate"] for row in rows),
                "score_ge_10": sum(row["score"] >= 10 for row in rows),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
