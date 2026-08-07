#!/usr/bin/env python3
"""Reproduce the read-only COVER-01 local/official lineage audit.

This audit deliberately tests only data lineage.  Exact assistant-text matches show
that official ALLaVA source IDs can be reconstructed for the sampled English rows;
they do not establish full-dataset recovery or a controlled coverage contrast.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import polars as pl


SOURCE_SPECS = (
    (
        "laion",
        Path("sources/cover01_official_allava_laion_first_rows.json"),
    ),
    (
        "vflan",
        Path("sources/cover01_official_allava_vflan_first_rows.json"),
    ),
)
SOURCE_TOKENS = (
    "allava_laion",
    "allava_vflan",
    "source_id",
    "original_caption",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_path_record(value: Any, expected_path: str) -> dict[str, Any]:
    if isinstance(value, dict):
        if value.get("path") == expected_path:
            return value
        for child in value.values():
            try:
                return find_path_record(child, expected_path)
            except KeyError:
                pass
    elif isinstance(value, list):
        for child in value:
            try:
                return find_path_record(child, expected_path)
            except KeyError:
                pass
    raise KeyError(expected_path)


def official_samples() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    samples: list[dict[str, str]] = []
    receipts: list[dict[str, Any]] = []
    for source_name, path in SOURCE_SPECS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        source_samples: list[dict[str, str]] = []
        for entry in payload.get("rows", []):
            if entry.get("truncated_cells"):
                continue
            row = entry.get("row") or {}
            assistant_values = [
                turn.get("value")
                for turn in row.get("conversations") or []
                if turn.get("from") == "gpt"
                and isinstance(turn.get("value"), str)
            ]
            if not assistant_values:
                continue
            source_samples.append(
                {
                    "source": source_name,
                    "official_row_index": entry["row_idx"],
                    "official_id": row["id"],
                    "official_image_path": row["image"],
                    "assistant": assistant_values[-1],
                }
            )
        samples.extend(source_samples)
        id_counts = Counter(sample["official_id"] for sample in source_samples)
        receipts.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "dataset": payload.get("dataset"),
                "config": payload.get("config"),
                "split": payload.get("split"),
                "raw_rows": len(payload.get("rows", [])),
                "usable_rows": len(source_samples),
                "unique_official_ids": len(id_counts),
                "duplicate_official_ids": {
                    official_id: count
                    for official_id, count in sorted(id_counts.items())
                    if count > 1
                },
                "truncated_rows_excluded": sum(
                    bool(entry.get("truncated_cells"))
                    for entry in payload.get("rows", [])
                ),
            }
        )
    return samples, receipts


def schema_records(schema: dict[str, pl.DataType]) -> list[dict[str, str]]:
    return [{"name": name, "dtype": str(dtype)} for name, dtype in schema.items()]


def ensure_unique(values: Iterable[str], label: str) -> None:
    values = list(values)
    if len(values) != len(set(values)):
        raise RuntimeError(f"{label} are not unique")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parquet",
        type=Path,
        default=Path("dataset/pretrain_i2t.parquet"),
    )
    parser.add_argument(
        "--minimind-api",
        type=Path,
        default=Path("sources/cover01_official_minimind_dataset_api.json"),
    )
    parser.add_argument(
        "--minimind-tree",
        type=Path,
        default=Path("sources/cover01_official_minimind_dataset_tree.json"),
    )
    parser.add_argument(
        "--allava-api",
        type=Path,
        default=Path("sources/cover01_official_allava4v_api.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/results/COVER-01_round1/LINEAGE_AUDIT.json"
        ),
    )
    args = parser.parse_args()

    minimind_api = json.loads(args.minimind_api.read_text(encoding="utf-8"))
    minimind_tree = json.loads(args.minimind_tree.read_text(encoding="utf-8"))
    allava_api = json.loads(args.allava_api.read_text(encoding="utf-8"))
    official_record = find_path_record(minimind_tree, "pretrain_i2t.parquet")

    samples, sample_receipts = official_samples()
    ensure_unique((sample["assistant"] for sample in samples), "official answers")

    lazy = pl.scan_parquet(args.parquet)
    schema = lazy.schema
    assistant = pl.col("conversations").str.json_path_match("$[1].content")
    summary_exprs = [pl.len().alias("row_count")]
    summary_exprs.extend(
        pl.col("conversations")
        .str.contains(token, literal=True)
        .sum()
        .alias(token)
        for token in SOURCE_TOKENS
    )
    local_summary = lazy.select(summary_exprs).collect(streaming=True).row(
        0, named=True
    )

    answer_to_sample = {sample["assistant"]: sample for sample in samples}
    matching = (
        lazy.with_row_index("local_row_index")
        .with_columns(assistant.alias("assistant"))
        .filter(pl.col("assistant").is_in(list(answer_to_sample)))
        .select("local_row_index", "assistant")
        .collect(streaming=True)
    )
    matched_answers = matching.get_column("assistant").to_list()
    match_counts = Counter(matched_answers)
    duplicate_matches = sorted(
        answer for answer, count in match_counts.items() if count != 1
    )
    missing_answers = sorted(set(answer_to_sample) - set(matched_answers))
    if duplicate_matches or missing_answers:
        raise RuntimeError(
            "official sample matching was not one-to-one: "
            f"duplicates={len(duplicate_matches)}, missing={len(missing_answers)}"
        )

    matches = []
    for local_row_index, answer in matching.iter_rows():
        sample = answer_to_sample[answer]
        matches.append(
            {
                "source": sample["source"],
                "official_row_index": sample["official_row_index"],
                "official_id": sample["official_id"],
                "official_image_path": sample["official_image_path"],
                "local_row_index": local_row_index,
                "assistant_sha256": hashlib.sha256(
                    answer.encode("utf-8")
                ).hexdigest(),
            }
        )
    matches.sort(
        key=lambda row: (
            row["source"],
            row["official_row_index"],
            row["official_id"],
        )
    )

    parquet_sha256 = sha256_file(args.parquet)
    # Hugging Face's tree API names the LFS content SHA-256 field ``oid``.
    expected_lfs_sha256 = (official_record.get("lfs") or {}).get("oid")
    source_match_counts = Counter(row["source"] for row in matches)
    result = {
        "audit": "COVER-01 local/official lineage audit",
        "audit_version": 1,
        "read_only": True,
        "local_parquet": {
            "path": str(args.parquet),
            "size_bytes": args.parquet.stat().st_size,
            "sha256": parquet_sha256,
            "row_count": local_summary["row_count"],
            "schema": schema_records(schema),
            "embedded_source_token_row_counts": {
                token: local_summary[token] for token in SOURCE_TOKENS
            },
            "official_minimind_dataset_revision": minimind_api.get("sha"),
            "official_tree_lfs_sha256": expected_lfs_sha256,
            "official_tree_size_bytes": official_record.get("size"),
            "hash_matches_official_tree": parquet_sha256 == expected_lfs_sha256,
            "size_matches_official_tree": (
                args.parquet.stat().st_size == official_record.get("size")
            ),
        },
        "upstream": {
            "official_allava_dataset_revision": allava_api.get("sha"),
            "official_allava_license": (allava_api.get("cardData") or {}).get(
                "license"
            ),
            "minimind_card_license": (minimind_api.get("cardData") or {}).get(
                "license"
            ),
            "sample_receipts": sample_receipts,
        },
        "sample_reconstruction": {
            "official_records": len(samples),
            "unique_official_ids": len(
                {sample["official_id"] for sample in samples}
            ),
            "duplicated_official_id_values": {
                official_id: count
                for official_id, count in sorted(
                    Counter(sample["official_id"] for sample in samples).items()
                )
                if count > 1
            },
            "exact_assistant_matches": len(matches),
            "unique_exact_assistant_matches": len(set(matched_answers)),
            "one_to_one": len(matches) == len(samples),
            "source_counts": {
                source: source_match_counts[source]
                for source in sorted(source_match_counts)
            },
            "matches": matches,
        },
        "inference_boundary": {
            "demonstrated": (
                "For all 169 saved official caption samples, exact English "
                "assistant text reconstructs the corresponding authoritative "
                "ALLaVA row occurrence, source ID, and image path in the local "
                "parquet."
            ),
            "not_demonstrated": [
                "Full-dataset source-ID reconstruction coverage.",
                "Global example-key uniqueness of the official ID field: three "
                "VFLAN ID values are duplicated in the saved sample.",
                "Source-ID propagation from an English row to translated rows via "
                "identical image bytes.",
                "A source-defined single-factor complementary-coverage versus "
                "same-domain-redundancy contrast.",
                "A frozen held-out target whose direction is unconfounded by "
                "source, task, style, quality, or difficulty.",
            ],
            "interpretation": (
                "The local schema omits IDs, but sample reconstruction is "
                "demonstrated; full coverage remains unproved. This audit does "
                "not by itself accept or reject the upper-level coverage "
                "mechanism."
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "local_rows": result["local_parquet"]["row_count"],
                "official_samples": len(samples),
                "exact_matches": len(matches),
                "hash_matches_official_tree": result["local_parquet"][
                    "hash_matches_official_tree"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
