#!/usr/bin/env python3
"""Build an auditable, deterministic index for the frozen LITMAP-03 searches."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any


ATOM = {"a": "http://www.w3.org/2005/Atom"}
ARXIV_ID = re.compile(r"arxiv\.org/(?:abs|pdf)/([^/?#]+)")
QUERY_FAMILIES = {
    "frozen_encoder",
    "gradient_routing",
    "module_tuning",
    "peft_modules",
    "visual_target_peft",
}


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def reconstruct_abstract(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        words.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(words))


def family_from_path(path: Path) -> str:
    match = re.match(r"research_litmap03_(.+)_(?:arxiv|openalex)$", path.stem)
    if not match:
        raise ValueError(f"unexpected LITMAP-03 filename: {path}")
    return match.group(1)


def discovery_paths(source_dir: Path, backend: str) -> list[Path]:
    paths = sorted(source_dir.glob(f"research_litmap03_*_{backend}.*"))
    return [path for path in paths if family_from_path(path) in QUERY_FAMILIES]


def add_arxiv(path: Path, records: dict[str, dict[str, Any]]) -> None:
    family = family_from_path(path)
    root = ET.parse(path).getroot()
    for entry in root.findall("a:entry", ATOM):
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


def add_openalex(path: Path, records: dict[str, dict[str, Any]]) -> None:
    family = family_from_path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    for work in payload.get("results", []):
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
                if clean(location.get(field)):
                    rec["urls"].add(clean(location[field]))
        for location in locations:
            for field in ("landing_page_url", "pdf_url"):
                match = ARXIV_ID.search(clean(location.get(field)))
                if match:
                    rec["arxiv_ids"].add(match.group(1))


def base_record(title: str) -> dict[str, Any]:
    return {
        "title": title,
        "families": set(),
        "backends": set(),
        "arxiv_ids": set(),
        "openalex_ids": set(),
        "dois": set(),
        "published": set(),
        "types": set(),
        "venues": set(),
        "authors": set(),
        "urls": set(),
        "abstracts": [],
        "cited_by_count": 0,
    }


def prior_titles(source_dir: Path) -> set[str]:
    prior: set[str] = set()
    for path in sorted(source_dir.glob("research_*.xml")):
        if "litmap03" in path.name:
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for entry in root.findall("a:entry", ATOM):
            title = clean(entry.findtext("a:title", default="", namespaces=ATOM))
            if title:
                prior.add(normalized_title(title))
    for path in sorted(source_dir.glob("research_*.json")):
        if "litmap03" in path.name:
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
    reasons: list[str] = []
    score = 0
    groups = [
        (6, "autoregressive-lvlm", ("large vision-language model", "large vision language model",
                                   "multimodal large language model", "multimodal llm", "mllm", "llava")),
        (5, "module-intervention", ("which modules", "module selection", "module-wise",
                                    "vision tower", "vision encoder", "visual encoder", "projector",
                                    "connector", "adapter", "lora", "fine-tun")),
        (5, "competition-routing", ("gradient conflict", "gradient routing", "modality imbalance",
                                    "modality competition", "language dominance", "gradient interference")),
        (3, "frozen-unfrozen", ("frozen", "freeze", "unfreeze", "trainable")),
        (3, "visual-target", ("visual reconstruction", "visual target", "masked image",
                              "latent prediction", "visual token")),
        (2, "matched-control-language", ("ablation", "controlled", "same parameter",
                                         "parameter-matched", "parameter efficient", "peft")),
    ]
    for points, label, phrases in groups:
        if any(phrase in text for phrase in phrases):
            score += points
            reasons.append(label)
    title = rec["title"].casefold()
    penalties = [
        (-8, "survey", ("survey", "review", "overview")),
        (-6, "non-general-domain", ("medical", "radiology", "pathology", "remote sensing",
                                    "autonomous driving", "point cloud", "audio")),
        (-4, "video-only", ("video",)),
        (-4, "benchmark-only", ("benchmark", "evaluation", "hallucination detection")),
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
    abstract = max(rec["abstracts"], key=len, default="")
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
        "abstract": abstract,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("sources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/LITMAP-03_round1/SEARCH_INDEX.tsv"),
    )
    args = parser.parse_args()

    records: dict[str, dict[str, Any]] = {}
    arxiv_paths = discovery_paths(args.source_dir, "arxiv")
    openalex_paths = discovery_paths(args.source_dir, "openalex")
    for path in arxiv_paths:
        add_arxiv(path, records)
    for path in openalex_paths:
        add_openalex(path, records)
    prior = prior_titles(args.source_dir)
    rows = [serialise(rec, prior) for rec in records.values()]
    rows.sort(key=lambda row: (-row["score"], -row["cited_by_count"], row["title"].casefold()))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "raw_records": sum(
                    len(json.loads(path.read_text(encoding="utf-8")).get("results", []))
                    for path in openalex_paths
                )
                + sum(
                    len(ET.parse(path).getroot().findall("a:entry", ATOM))
                    for path in arxiv_paths
                ),
                "unique_titles": len(rows),
                "prior_search_duplicates": sum(row["prior_search_duplicate"] for row in rows),
                "score_ge_10": sum(row["score"] >= 10 for row in rows),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
