#!/usr/bin/env python3
"""Run and preserve the frozen LITMAP-07 targeted literature searches."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


QUERIES = {
    "factorization_shared_rule": (
        '"vision language" compositional representation factorization shared rule'
    ),
    "factorization_multimodal_composition": (
        "multimodal compositional generalization modular factorized representation"
    ),
    "factorization_rule_reuse": (
        '"systematic compositional generalization" multimodal shared features rule reuse'
    ),
    "factorization_generative_vlm": (
        '"multimodal large language model" compositional generalization training'
    ),
    "credit_visual_gradient": (
        '"vision language" autoregressive visual credit assignment modality imbalance gradient'
    ),
    "credit_task_specific_absorption": (
        '"multimodal large language model" language bias visual shortcut training dynamics'
    ),
    "credit_modality_imbalance": (
        '"modality imbalance" multimodal learning gradient optimization'
    ),
    "credit_language_dominance": (
        '"language dominance" vision language model visual training'
    ),
    "trainability_frozen_encoder": (
        '"vision language" frozen vision encoder compositional generalization expressivity'
    ),
    "trainability_adapter_expressivity": (
        "multimodal adapter projector expressivity frozen features interaction learning"
    ),
    "trainability_frozen_interactions": (
        '"frozen features" interaction learning neural network expressivity'
    ),
    "trainability_vision_connector": (
        '"vision-language connector" frozen encoder representation expressivity'
    ),
    "theory_compositional_implicit_bias": (
        "gradient descent compositional generalization factorized rule implicit bias"
    ),
    "theory_identifiability_optimization_gap": (
        "identifiability optimization gap neural representation population minimizer"
    ),
    "theory_modular_generalization": (
        '"modular neural networks" compositional generalization theorem'
    ),
    "theory_spurious_feature_dynamics": (
        '"gradient descent" spurious features shortcut learning theorem'
    ),
}

SEMANTIC_FIELDS = (
    "title,abstract,authors,year,publicationDate,venue,citationCount,"
    "externalIds,url,openAccessPdf"
)


def fetch(url: str, destination: Path) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "MiniMind-V-LITMAP-07/1.0 "
                "(academic reproducibility search; contact: local-research-agent)"
            )
        },
    )
    started = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
        destination.write_bytes(payload)
        return {
            "ok": True,
            "status": status,
            "content_type": content_type,
            "bytes": len(payload),
            "started_utc": started.isoformat(),
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "destination": str(destination),
        }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "ok": False,
            "error": repr(exc),
            "started_utc": started.isoformat(),
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "destination": str(destination),
        }


def arxiv_url(query: str) -> str:
    params = urllib.parse.urlencode(
        {
            "search_query": f'all:"{query}"',
            "start": 0,
            "max_results": 100,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )
    return f"https://export.arxiv.org/api/query?{params}"


def openalex_url(query: str) -> str:
    params = urllib.parse.urlencode(
        {
            "search": query,
            "filter": "from_publication_date:2018-01-01,to_publication_date:2026-12-31",
            "per-page": 100,
        }
    )
    return f"https://api.openalex.org/works?{params}"


def semantic_url(query: str) -> str:
    params = urllib.parse.urlencode(
        {"query": query, "limit": 100, "fields": SEMANTIC_FIELDS}
    )
    return f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("sources/litmap07"))
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = args.output_dir / "SEARCH_RECEIPTS.json"
    if manifest_path.exists():
        prior_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        receipts: list[dict[str, Any]] = list(prior_manifest.get("receipts", []))
    else:
        receipts = []
    attempted = {
        (item.get("family"), item.get("backend"))
        for item in receipts
        if item.get("family") and item.get("backend")
    }
    parallel = subprocess.run(
        ["bash", "-lc", "command -v parallel-cli"],
        check=False,
        capture_output=True,
        text=True,
    )
    if not any(item.get("backend") == "parallel-cli" for item in receipts):
        receipts.append(
            {
                "backend": "parallel-cli",
                "ok": parallel.returncode == 0,
                "returncode": parallel.returncode,
                "stdout": parallel.stdout.strip(),
                "stderr": parallel.stderr.strip(),
                "checked_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

    backends = (
        ("arxiv", arxiv_url, "xml"),
        ("openalex", openalex_url, "json"),
        ("semanticscholar", semantic_url, "json"),
    )
    for family, query in QUERIES.items():
        for backend, build_url, extension in backends:
            if (family, backend) in attempted:
                continue
            destination = args.output_dir / f"{family}_{backend}.{extension}"
            receipt = fetch(build_url(query), destination)
            receipt.update({"backend": backend, "family": family, "query": query})
            receipts.append(receipt)
            manifest = {
                "protocol": "LITMAP-07_round1",
                "queries": QUERIES,
                "receipts": receipts,
            }
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            time.sleep(args.delay_seconds)

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "successful": sum(
                    bool(item.get("ok")) for item in receipts if item.get("family")
                ),
                "failed": sum(
                    not bool(item.get("ok"))
                    for item in receipts
                    if item.get("family")
                ),
                "parallel_cli_available": bool(receipts[0]["ok"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
