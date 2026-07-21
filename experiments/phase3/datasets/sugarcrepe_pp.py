"""Frozen SugarCrepe++ source loading and canonical row construction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

from experiments.phase3.canonical_io import canonical_json_bytes, sha256_bytes


REPO_ID = "Aman-J/SugarCrepe_pp"
REVISION = "dea2a1b6f9e1069c609f676aa55ec61e9b65fb61"
SPLIT = "train"
SOURCES = (
    ("replace_attribute", "data/replace_att.json", 788, "6826413592894754eeca02aeebbcbbc8b95a7456998abcc714e71c033ce6fe87"),
    ("replace_object", "data/replace_obj.json", 1652, "5c6dc499ec8f511a8aa4ec1b7b5eb0eca90317488abe36ec39573355e2d361ab"),
    ("replace_relation", "data/replace_rel.json", 1406, "040fb95d3f0619bf515db60879e99709a87a5e9b4f524ec3403b127243480fd4"),
    ("swap_atribute", "data/swap_att.json", 666, "450d0fd9fcad3e6f44950dc634e7f901ab1c6d9c60a569ade5ae8ffb3d203ad8"),
    ("swap_object", "data/swap_obj.json", 245, "5f33cae824de431a7ecd3c5de6301f689815f9497aa36d96b154bbaf117b201b"),
)
FILENAME_RE = re.compile(r"^[0-9]{12}\.jpg$")


def parse_source(payload: bytes, category: str, expected_rows: int) -> list[dict[str, Any]]:
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, list) or len(data) != expected_rows:
        raise ValueError(f"{category} expected {expected_rows} source rows")
    rows = []
    for source in data:
        if not isinstance(source, dict):
            raise ValueError("SugarCrepe++ source row must be an object")
        required = ("id", "filename", "caption", "caption2", "negative_caption")
        if any(key not in source for key in required):
            raise ValueError(f"SugarCrepe++ row is missing fields: {required}")
        numeric_id = source["id"]
        if not isinstance(numeric_id, int) or isinstance(numeric_id, bool) or numeric_id < 0:
            raise ValueError("SugarCrepe++ id must be a nonnegative integer")
        for key in ("filename", "caption", "caption2", "negative_caption"):
            if not isinstance(source[key], str):
                raise ValueError(f"SugarCrepe++ {key} must be a string")
        if not FILENAME_RE.fullmatch(source["filename"]):
            raise ValueError(f"invalid COCO filename: {source['filename']}")
        rows.append(
            {
                "caption": source["caption"],
                "caption2": source["caption2"],
                "category": category,
                "filename": source["filename"],
                "negative_caption": source["negative_caption"],
                "numeric_id": numeric_id,
                "row_key": f"{category}:{numeric_id}",
            }
        )
    return rows


def canonicalize_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = sorted(
        rows,
        key=lambda row: (
            row["category"].encode("utf-8"),
            int(row["numeric_id"]),
            row["filename"].encode("utf-8"),
        ),
    )
    keys = [row["row_key"] for row in result]
    if len(keys) != len(set(keys)):
        raise ValueError("SugarCrepe++ row_key is not globally unique")
    return result


def row_index(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "row_index": index,
            "row_key": row["row_key"],
            "category": row["category"],
            "numeric_id": row["numeric_id"],
            "filename": row["filename"],
            "source_row_sha256": sha256_bytes(canonical_json_bytes(row)),
        }
        for index, row in enumerate(rows)
    ]


def canonical_row_commitment(index_rows: Iterable[dict[str, Any]]) -> str:
    payload = b"".join(
        str(int(row["row_index"])).encode("ascii")
        + b"\0"
        + str(row["source_row_sha256"]).encode("ascii")
        + b"\n"
        for row in index_rows
    )
    return sha256_bytes(payload)

