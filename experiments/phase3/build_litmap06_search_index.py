#!/usr/bin/env python3
"""Build a deterministic index for the frozen LITMAP-06 mechanism searches."""

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


BACKENDS = ("arxiv", "openalex", "semanticscholar")


def family_from_path(path: Path) -> str:
    match = re.match(r"(.+)_(?:arxiv|openalex|semanticscholar)$", path.stem)
    if not match:
        raise ValueError(f"unexpected LITMAP-06 filename: {path}")
    return match.group(1)


def mechanism_from_family(family: str) -> str:
    if family.startswith("ar_credit"):
        return "ar_visual_credit"
    if family.startswith("composition"):
        return "cross_modal_composition"
    if family.startswith("coverage"):
        return "joint_support_coverage"
    if family.startswith("xid"):
        return "interaction_identifiability"
    if family == "mpa_exact":
        return "ar_visual_credit"
    if family == "iccg_exact":
        return "cross_modal_composition"
    raise ValueError(f"unexpected query family: {family}")


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
        rec["abstracts"].append(
            clean(entry.findtext("a:summary", default="", namespaces=ATOM))
        )
        rec["published"].add(
            clean(entry.findtext("a:published", default="", namespaces=ATOM))[:10]
        )
        rec["authors"].update(
            clean(author.findtext("a:name", default="", namespaces=ATOM))
            for author in entry.findall("a:author", ATOM)
        )
        identifier = clean(entry.findtext("a:id", default="", namespaces=ATOM))
        match = ARXIV_ID.search(identifier)
        if match:
            rec["arxiv_ids"].add(match.group(1))
        for link in entry.findall("a:link", ATOM):
            url = clean(link.attrib.get("href"))
            if url:
                rec["urls"].add(url)
    return len(entries)


def add_openalex(path: Path, records: dict[str, dict[str, Any]]) -> int:
    family = family_from_path(path)
    works = json.loads(path.read_text(encoding="utf-8")).get("results", [])
    for work in works:
        title = clean(work.get("title") or work.get("display_name"))
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
        rec["cited_by_count"] = max(
            rec["cited_by_count"], int(work.get("cited_by_count") or 0)
        )
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
                if not url:
                    continue
                rec["urls"].add(url)
                match = ARXIV_ID.search(url)
                if match:
                    rec["arxiv_ids"].add(match.group(1))
    return len(works)


def add_semantic_scholar(path: Path, records: dict[str, dict[str, Any]]) -> int:
    family = family_from_path(path)
    works = json.loads(path.read_text(encoding="utf-8")).get("data", [])
    for work in works:
        title = clean(work.get("title"))
        key = normalized_title(title)
        if not key:
            continue
        rec = records.setdefault(key, base_record(title))
        rec["families"].add(family)
        rec["backends"].add("semanticscholar")
        rec["published"].add(clean(work.get("publicationDate") or str(work.get("year") or "")))
        rec["venues"].add(clean(work.get("venue")))
        rec["authors"].update(clean(author.get("name")) for author in work.get("authors", []))
        rec["cited_by_count"] = max(
            rec["cited_by_count"], int(work.get("citationCount") or 0)
        )
        if clean(work.get("abstract")):
            rec["abstracts"].append(clean(work["abstract"]))
        external = work.get("externalIds") or {}
        if clean(external.get("DOI")):
            rec["dois"].add(f"https://doi.org/{clean(external['DOI'])}")
        if clean(external.get("ArXiv")):
            rec["arxiv_ids"].add(clean(external["ArXiv"]))
        for url in (
            clean(work.get("url")),
            clean((work.get("openAccessPdf") or {}).get("url")),
        ):
            if url:
                rec["urls"].add(url)
    return len(works)


def prior_titles(project_sources: Path, current_source_dir: Path) -> set[str]:
    prior: set[str] = set()
    for path in sorted(project_sources.rglob("*.xml")):
        if current_source_dir in path.parents:
            continue
        try:
            entries = ET.parse(path).getroot().findall("a:entry", ATOM)
        except ET.ParseError:
            continue
        for entry in entries:
            title = clean(entry.findtext("a:title", default="", namespaces=ATOM))
            if title:
                prior.add(normalized_title(title))
    for path in sorted(project_sources.rglob("*.json")):
        if current_source_dir in path.parents:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        works = payload.get("results", []) if isinstance(payload, dict) else []
        for work in works:
            title = clean(work.get("title") or work.get("display_name"))
            if title:
                prior.add(normalized_title(title))
    return prior


def relevance_score(rec: dict[str, Any]) -> tuple[int, list[str]]:
    text = f"{rec['title']} {' '.join(rec['abstracts'])}".casefold()
    score = 0
    reasons: list[str] = []
    groups = [
        (
            7,
            "autoregressive-lvlm",
            (
                "multimodal large language model",
                "large vision-language model",
                "large vision language model",
                "multimodal llm",
                "mllm",
                "llava",
            ),
        ),
        (
            6,
            "mechanism",
            (
                "language shortcut",
                "language bias",
                "modality imbalance",
                "language dominance",
                "credit assignment",
                "compositional generalization",
                "systematic generalization",
                "relation binding",
                "joint support",
                "support coverage",
                "data coverage",
            ),
        ),
        (
            4,
            "generalization",
            (
                "held-out",
                "unseen",
                "out-of-distribution",
                "out of distribution",
                "transferable",
                "generalization",
            ),
        ),
        (
            3,
            "controlled-or-formal",
            (
                "theorem",
                "bound",
                "theoretical",
                "controlled",
                "matched",
                "causal",
                "factorial",
            ),
        ),
        (
            2,
            "algorithmic-exit",
            (
                "training objective",
                "data selection",
                "sampling",
                "curriculum",
                "hard negative",
                "regularization",
            ),
        ),
    ]
    for points, label, phrases in groups:
        if any(phrase in text for phrase in phrases):
            score += points
            reasons.append(label)
    title = rec["title"].casefold()
    penalties = [
        (-7, "survey", ("survey", "review", "overview")),
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
        "openalex_ids": ";".join(sorted(value for value in rec["openalex_ids"] if value)),
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
    parser.add_argument("--source-dir", type=Path, default=Path("sources/litmap06"))
    parser.add_argument("--project-sources", type=Path, default=Path("sources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/LITMAP-06_round1/SEARCH_INDEX.tsv"),
    )
    args = parser.parse_args()

    records: dict[str, dict[str, Any]] = {}
    raw_records = 0
    for path in sorted(args.source_dir.glob("*_arxiv.xml")):
        raw_records += add_arxiv(path, records)
    for path in sorted(args.source_dir.glob("*_openalex.json")):
        raw_records += add_openalex(path, records)
    for path in sorted(args.source_dir.glob("*_semanticscholar.json")):
        raw_records += add_semantic_scholar(path, records)

    prior = prior_titles(args.project_sources, args.source_dir)
    rows = [serialise(record, prior) for record in records.values()]
    rows.sort(key=lambda row: (-row["score"], -row["cited_by_count"], row["title"].casefold()))
    if not rows:
        raise RuntimeError("no LITMAP-06 discovery records found")

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
        "score_ge_10": sum(row["score"] >= 10 for row in rows),
        "backend_files": {
            backend: len(list(args.source_dir.glob(f"*_{backend}.*")))
            for backend in BACKENDS
        },
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
