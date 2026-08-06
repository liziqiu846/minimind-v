#!/usr/bin/env python3
"""Build and audit exact-image train/ghost/development partitions."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from experiments.phase3_v6.scoring.input_validation import (
    load_and_validate_frozen_inputs,
)

from . import PROTOCOL_ID
from .common import (
    canonical_bytes,
    load_protocol,
    sha256_bytes,
    sha256_file,
    write_json_atomic,
)


def _rank(seed: int, unit_id: str) -> bytes:
    return hashlib.sha256(
        f"{PROTOCOL_ID}|{seed}|{unit_id}".encode("utf-8")
    ).digest()


def _conversation_hash(value: str) -> str:
    parsed = json.loads(value)
    canonical = json.dumps(
        parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    if canonical != value:
        raise ValueError("catalog conversation is not canonical")
    return sha256_bytes(value.encode("utf-8"))


def _development_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    frozen = load_and_validate_frozen_inputs(verify_images=True)
    rows = []
    for filename, entry in sorted(frozen["image_entries"].items()):
        descriptor = {
            "development_protocol": "phase3-v6",
            "filename": filename,
            "assignment_core_sha256": frozen["assignment_core_sha256"],
        }
        rows.append(
            {
                "unit_id": f"development:{filename}",
                "image_sha256": entry["image_sha256"],
                "conversation_sha256": sha256_bytes(canonical_bytes(descriptor)),
                "split": "development",
                "catalog_index": None,
                "conversation_hash_role": "frozen_development_assignment_descriptor",
            }
        )
    return rows, frozen


def build(catalog_path: Path, output_dir: Path) -> dict[str, Any]:
    protocol = load_protocol()
    expected_catalog_hash = protocol["data"]["source_catalog_sha256"]
    if sha256_file(catalog_path) != expected_catalog_hash:
        raise ValueError("eligible catalog SHA-256 differs from protocol")
    table = pq.read_table(catalog_path)
    required = {
        "catalog_index",
        "catalog_unit_id",
        "image_bytes",
        "image_sha256",
        "canonical_conversation",
    }
    if not required.issubset(table.column_names):
        raise ValueError("eligible catalog lacks required group fields")

    image_hashes = table["image_sha256"].to_pylist()
    unit_ids = table["catalog_unit_id"].to_pylist()
    conversations = table["canonical_conversation"].to_pylist()
    encoded_images = table["image_bytes"].to_pylist()
    if len(set(image_hashes)) != len(image_hashes):
        raise ValueError("eligible catalog contains duplicate exact images")
    if len(set(unit_ids)) != len(unit_ids):
        raise ValueError("eligible catalog contains duplicate unit IDs")
    conversation_hashes = []
    for expected, payload, conversation in zip(
        image_hashes, encoded_images, conversations
    ):
        if sha256_bytes(payload) != expected:
            raise ValueError("catalog image SHA-256 does not match image bytes")
        conversation_hashes.append(_conversation_hash(conversation))

    development, frozen = _development_rows()
    development_hashes = {row["image_sha256"] for row in development}
    if len(development_hashes) != len(development):
        raise ValueError("development set contains duplicate exact images")
    eligible_indices = [
        index
        for index, image_hash in enumerate(image_hashes)
        if image_hash not in development_hashes
    ]
    eligible_indices.sort(
        key=lambda index: (_rank(protocol["data"]["selection_seed"], unit_ids[index]),
                           unit_ids[index])
    )
    train_count = int(protocol["data"]["train_unique_image_groups"])
    if len(eligible_indices) <= train_count:
        raise ValueError("not enough groups for nonempty independent ghost pool")
    train_indices = eligible_indices[:train_count]
    ghost_indices = eligible_indices[train_count:]
    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "train.parquet"
    ghost_path = output_dir / "ghost_pool.parquet"
    pq.write_table(table.take(pa.array(train_indices)), train_path, compression="zstd")
    pq.write_table(table.take(pa.array(ghost_indices)), ghost_path, compression="zstd")

    rows = []
    for split, indices in (("train", train_indices), ("ghost_pool", ghost_indices)):
        for index in indices:
            rows.append(
                {
                    "unit_id": unit_ids[index],
                    "image_sha256": image_hashes[index],
                    "conversation_sha256": conversation_hashes[index],
                    "split": split,
                    "catalog_index": int(table["catalog_index"][index].as_py()),
                    "conversation_hash_role": "canonical_conversation",
                }
            )
    rows.extend(development)
    manifest_path = output_dir / "image_group_manifest.jsonl"
    with manifest_path.open("wb") as handle:
        for row in rows:
            handle.write(canonical_bytes(row) + b"\n")
    split_counts = Counter(row["split"] for row in rows)
    sets = {
        split: {row["image_sha256"] for row in rows if row["split"] == split}
        for split in split_counts
    }
    overlaps = {
        "train_ghost": len(sets["train"] & sets["ghost_pool"]),
        "train_development": len(sets["train"] & sets["development"]),
        "ghost_development": len(sets["ghost_pool"] & sets["development"]),
    }
    audit_pass = (
        len(sets["train"]) == split_counts["train"] == train_count
        and len(sets["ghost_pool"]) == split_counts["ghost_pool"]
        and all(value == 0 for value in overlaps.values())
    )
    audit = {
        "schema_version": 1,
        "protocol_id": PROTOCOL_ID,
        "status": "PASS" if audit_pass else "FAIL",
        "source_catalog": {
            "path": str(catalog_path.resolve()),
            "sha256": sha256_file(catalog_path),
            "row_count": len(table),
            "unique_exact_image_count": len(set(image_hashes)),
            "unique_unit_id_count": len(set(unit_ids)),
            "canonical_conversation_count": len(conversation_hashes),
        },
        "splits": dict(sorted(split_counts.items())),
        "exact_image_overlap_counts": overlaps,
        "train_exact_image_unique": len(sets["train"]) == split_counts["train"],
        "one_canonical_conversation_per_train_image": True,
        "ghost_pool_exact_image_unique": (
            len(sets["ghost_pool"]) == split_counts["ghost_pool"]
        ),
        "development_exact_image_unique": (
            len(sets["development"]) == split_counts["development"]
        ),
        "development_assignment_core_sha256": frozen["assignment_core_sha256"],
        "final_independent_confirmation_accessed": False,
        "artifacts": {
            "train": {
                "path": str(train_path.resolve()),
                "sha256": sha256_file(train_path),
                "sample_count": len(train_indices),
            },
            "ghost_pool": {
                "path": str(ghost_path.resolve()),
                "sha256": sha256_file(ghost_path),
                "sample_count": len(ghost_indices),
            },
            "manifest": {
                "path": str(manifest_path.resolve()),
                "sha256": sha256_file(manifest_path),
                "sample_count": len(rows),
            },
        },
    }
    write_json_atomic(output_dir / "data_protocol_audit.json", audit)
    if not audit_pass:
        raise RuntimeError("data protocol audit failed")
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.catalog, args.output_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
