#!/usr/bin/env python3
"""Build the Stage 2 v2 finite catalog and independent replacement draws."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import os
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import imagehash
import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import build_token_record, normalized_image
from experiments.build_stage2_dataset import HammingBKTree
from experiments.stage2_protocol import Stage2Protocol, sha256_file, write_json_atomic


def serialized_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def catalog_row_rank(domain: str, seed: int, row_index: int) -> bytes:
    if seed < 0 or row_index < 0:
        raise ValueError("catalog rank integer fields must be nonnegative")
    return hashlib.sha256(
        serialized_string(domain)
        + struct.pack("<Q", seed)
        + struct.pack("<Q", row_index)
    ).digest()


def select_catalog_source_indices(
    source_rows: int, capacity: int, domain: str, seed: int
) -> list[tuple[int, bytes]]:
    """Select row indices using only the declared row count, seed, and index."""
    if not 0 < capacity <= source_rows:
        raise ValueError("catalog source-row capacity must be in [1, source_rows]")
    heap: list[tuple[int, int, int, bytes]] = []
    for row_index in range(source_rows):
        rank = catalog_row_rank(domain, seed, row_index)
        entry = (-int.from_bytes(rank, "big"), -row_index, row_index, rank)
        if len(heap) < capacity:
            heapq.heappush(heap, entry)
        elif entry > heap[0]:
            heapq.heapreplace(heap, entry)
    return sorted(
        ((row_index, rank) for _, _, row_index, rank in heap),
        key=lambda item: (item[1], item[0]),
    )


def draw_catalog_index(
    domain: str, seed: int, draw_index: int, catalog_size: int
) -> tuple[int, int, str]:
    """Map one deterministic draw to an unbiased uniform catalog index."""
    if min(seed, draw_index) < 0 or catalog_size <= 0:
        raise ValueError("draw fields must be nonnegative and catalog nonempty")
    limit = (1 << 256) - ((1 << 256) % catalog_size)
    retry_index = 0
    while True:
        digest = hashlib.sha256(
            serialized_string(domain)
            + struct.pack("<Q", seed)
            + struct.pack("<Q", draw_index)
            + struct.pack("<Q", retry_index)
        ).digest()
        value = int.from_bytes(digest, "big")
        if value < limit:
            return value % catalog_size, retry_index, digest.hex()
        retry_index += 1


def source_image_bytes(value: Any) -> bytes:
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("catalog candidates must contain exactly one image")
        value = value[0]
    if not isinstance(value, bytes):
        raise ValueError("catalog image is not bytes")
    return value


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            handle.write("\n")
    os.replace(temporary, path)


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, temporary, compression="zstd", compression_level=9)
    os.replace(temporary, path)


def write_text_atomic(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


@dataclass(frozen=True)
class EligibleRow:
    image_bytes: bytes
    image_sha256: str
    phash_hex: str
    source_row_index: int
    row_rank_sha256: str
    representative_key_sha256: str
    token_record: dict[str, Any]

    @property
    def representative_key(self) -> tuple[bytes, int]:
        return bytes.fromhex(self.representative_key_sha256), self.source_row_index


def load_fixed_history(protocol: Stage2Protocol) -> tuple[set[str], HammingBKTree, int]:
    history = protocol.payload["history_exclusion"]
    exact = {
        line.strip()
        for line in (REPO_ROOT / history["exact_sha256_path"]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }
    phashes = [
        int(line.split()[1], 16)
        for line in (REPO_ROOT / history["phash_path"]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    return exact, HammingBKTree(phashes), len(phashes)


def build_eligible_catalog(
    protocol: Stage2Protocol,
    source: Path,
    selected_indices: list[tuple[int, bytes]],
    tokenizer,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    data = protocol.payload["data"]
    history_exact, history_phashes, _ = load_fixed_history(protocol)
    selected_rank = {row_index: rank for row_index, rank in selected_indices}
    selected_set = set(selected_rank)
    eligible_by_exact: dict[str, EligibleRow] = {}
    exposures: list[dict[str, Any]] = []
    counters = {
        "selected_source_rows": len(selected_indices),
        "visited_selected_source_rows": 0,
        "malformed_image": 0,
        "exact_history_rejection": 0,
        "token_or_template_ineligible": 0,
        "image_decode_or_phash_failure": 0,
        "historical_phash_rejection": 0,
        "eligible_rows_before_exact_grouping": 0,
        "eligible_exact_duplicates": 0,
        "representative_replacements": 0,
    }
    parquet = pq.ParquetFile(source)
    row_index = 0
    for batch in parquet.iter_batches(
        batch_size=4096, columns=("conversations", "image_bytes")
    ):
        conversations = batch.column(0).to_pylist()
        images = batch.column(1).to_pylist()
        for conversation, raw_image in zip(conversations, images, strict=True):
            if row_index not in selected_set:
                row_index += 1
                continue
            counters["visited_selected_source_rows"] += 1
            exposure: dict[str, Any] = {
                "source_row_index": row_index,
                "row_rank_sha256": selected_rank[row_index].hex(),
            }
            try:
                image_bytes = source_image_bytes(raw_image)
            except ValueError as error:
                counters["malformed_image"] += 1
                exposure.update(status="malformed_image", error=str(error))
                exposures.append(exposure)
                row_index += 1
                continue
            image_sha256 = hashlib.sha256(image_bytes).hexdigest()
            exposure["image_sha256"] = image_sha256
            if image_sha256 in history_exact:
                counters["exact_history_rejection"] += 1
                exposure["status"] = "exact_history_rejection"
                exposures.append(exposure)
                row_index += 1
                continue
            try:
                token_record = build_token_record(
                    conversation,
                    tokenizer,
                    image_token_count=protocol.payload["model"]["image_token_count"],
                    max_length=protocol.payload["training"]["max_sequence_length"],
                )
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                counters["token_or_template_ineligible"] += 1
                exposure.update(
                    status="token_or_template_ineligible",
                    error_type=type(error).__name__,
                )
                exposures.append(exposure)
                row_index += 1
                continue
            try:
                phash_hex = str(
                    imagehash.phash(
                        normalized_image(image_bytes),
                        hash_size=data["phash"]["hash_size"],
                        highfreq_factor=data["phash"]["highfreq_factor"],
                    )
                )
                phash_value = int(phash_hex, 16)
            except Exception as error:
                counters["image_decode_or_phash_failure"] += 1
                exposure.update(
                    status="image_decode_or_phash_failure",
                    error_type=type(error).__name__,
                )
                exposures.append(exposure)
                row_index += 1
                continue
            exposure["phash_hex"] = phash_hex
            if history_phashes.has_within(
                phash_value,
                data["phash"]["maximum_allowed_historical_hamming_distance"],
            ):
                counters["historical_phash_rejection"] += 1
                exposure["status"] = "historical_phash_rejection"
                exposures.append(exposure)
                row_index += 1
                continue
            counters["eligible_rows_before_exact_grouping"] += 1
            representative_sha = hashlib.sha256(
                token_record["canonical_conversation"].encode("utf-8")
            ).hexdigest()
            eligible = EligibleRow(
                image_bytes=image_bytes,
                image_sha256=image_sha256,
                phash_hex=phash_hex,
                source_row_index=row_index,
                row_rank_sha256=selected_rank[row_index].hex(),
                representative_key_sha256=representative_sha,
                token_record=token_record,
            )
            previous = eligible_by_exact.get(image_sha256)
            if previous is None:
                eligible_by_exact[image_sha256] = eligible
                exposure["status"] = "eligible_representative"
            else:
                counters["eligible_exact_duplicates"] += 1
                if eligible.representative_key < previous.representative_key:
                    counters["representative_replacements"] += 1
                    eligible_by_exact[image_sha256] = eligible
                    exposure["status"] = "eligible_representative_replacement"
                else:
                    exposure["status"] = "eligible_exact_duplicate"
            exposures.append(exposure)
            row_index += 1
    if row_index != parquet.metadata.num_rows:
        raise RuntimeError("source scan did not visit every row")
    if counters["visited_selected_source_rows"] != len(selected_indices):
        raise RuntimeError("source scan did not visit every selected row index")

    catalog = []
    for catalog_index, exact in enumerate(sorted(eligible_by_exact)):
        eligible = eligible_by_exact[exact]
        catalog.append(
            {
                "catalog_index": catalog_index,
                "catalog_unit_id": f"stage2-v2-unit-{catalog_index:05d}-{exact[:12]}",
                "image_bytes": eligible.image_bytes,
                "image_sha256": exact,
                "phash_hex": eligible.phash_hex,
                "source_row_index": eligible.source_row_index,
                "row_rank_sha256": eligible.row_rank_sha256,
                "representative_key_sha256": eligible.representative_key_sha256,
                **eligible.token_record,
            }
        )
    counters["eligible_catalog_units"] = len(catalog)
    counters["ineligible_source_rows"] = (
        counters["selected_source_rows"]
        - counters["eligible_rows_before_exact_grouping"]
    )
    return catalog, exposures, counters


def materialize_draws(
    catalog: list[dict[str, Any]], split: str, count: int, domain: str, seed: int
) -> list[dict[str, Any]]:
    rows = []
    for draw_index in range(count):
        catalog_index, retry_index, digest = draw_catalog_index(
            domain, seed, draw_index, len(catalog)
        )
        unit = catalog[catalog_index]
        rows.append(
            {
                **unit,
                "sample_id": f"stage2-v2-{split}-{draw_index:05d}",
                "split": split,
                "draw_index": draw_index,
                "draw_retry_index": retry_index,
                "draw_sha256": digest,
            }
        )
    return rows


def membership_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "sample_id",
            "split",
            "draw_index",
            "catalog_index",
            "catalog_unit_id",
            "image_sha256",
            "phash_hex",
            "source_row_index",
            "draw_retry_index",
            "draw_sha256",
            "target_token_count",
        )
    }


def duplicate_statistics(
    train_rows: list[dict[str, Any]], validation_rows: list[dict[str, Any]]
) -> dict[str, int]:
    train_units = [row["catalog_index"] for row in train_rows]
    validation_units = [row["catalog_index"] for row in validation_rows]
    train_unique = set(train_units)
    validation_unique = set(validation_units)
    return {
        "train_draws": len(train_units),
        "train_unique_catalog_units": len(train_unique),
        "train_repeated_draws": len(train_units) - len(train_unique),
        "validation_draws": len(validation_units),
        "validation_unique_catalog_units": len(validation_unique),
        "validation_repeated_draws": len(validation_units) - len(validation_unique),
        "cross_split_overlapping_catalog_units": len(train_unique & validation_unique),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    protocol.verify_runtime_integrity()
    if protocol.payload["schema_version"] != 2:
        raise ValueError("the v2 dataset builder requires protocol schema_version 2")
    if args.output_dir.resolve() != protocol.confirmation_directory().resolve():
        raise ValueError("output directory must equal the frozen v2 output directory")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(f"dataset output directory is not empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = args.output_dir / "failure_receipt.json"
    started = time.time()
    try:
        data = protocol.payload["data"]
        source = protocol.asset_path("source_dataset")
        if sha256_file(source) != data["source_sha256"]:
            raise ValueError("confirmation source hash differs from frozen protocol")
        parquet = pq.ParquetFile(source)
        if parquet.metadata.num_rows != data["source_rows"]:
            raise ValueError("confirmation source row count differs from frozen protocol")
        catalog_rule = data["catalog"]
        selected_indices = select_catalog_source_indices(
            data["source_rows"],
            catalog_rule["source_row_capacity"],
            catalog_rule["row_rank_domain"],
            data["selection_seed"],
        )
        index_path = args.output_dir / "catalog_source_indices.txt"
        write_text_atomic(
            index_path,
            "".join(f"{index} {rank.hex()}\n" for index, rank in selected_indices),
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        catalog, exposures, counters = build_eligible_catalog(
            protocol, source, selected_indices, tokenizer
        )
        if len(catalog) < catalog_rule["minimum_eligible_units"]:
            raise RuntimeError(
                f"eligible catalog has {len(catalog)} units, below frozen minimum "
                f"{catalog_rule['minimum_eligible_units']}"
            )
        catalog_path = args.output_dir / data["post_tag_receipts"]["catalog"]
        write_parquet(catalog_path, catalog)
        exposure_path = args.output_dir / "catalog_candidate_exposure_receipt.jsonl"
        write_jsonl(exposure_path, exposures)
        draws = data["independent_draws"]
        validation_rows = materialize_draws(
            catalog,
            "validation",
            draws["validation_draws"],
            draws["validation_domain"],
            data["selection_seed"],
        )
        train_rows = materialize_draws(
            catalog,
            "train",
            draws["train_draws"],
            draws["train_domain"],
            data["selection_seed"],
        )
        validation_path = args.output_dir / "validation.parquet"
        train_path = args.output_dir / "train.parquet"
        write_parquet(validation_path, validation_rows)
        write_parquet(train_path, train_rows)
        for split, rows in (("validation", validation_rows), ("train", train_rows)):
            write_jsonl(
                args.output_dir / f"{split}_membership.jsonl",
                (membership_row(row) for row in rows),
            )

        history = protocol.payload["history_exclusion"]
        catalog_manifest_path = (
            args.output_dir / data["post_tag_receipts"]["catalog_manifest"]
        )
        catalog_manifest = {
            "schema_version": 2,
            "protocol": protocol.reference(),
            "target_distribution": data["target_distribution"],
            "source": {
                "path": str(source),
                "sha256": sha256_file(source),
                "rows": data["source_rows"],
            },
            "row_selection": {
                "seed": data["selection_seed"],
                "domain": catalog_rule["row_rank_domain"],
                "capacity": catalog_rule["source_row_capacity"],
                "source_indices_sha256": sha256_file(index_path),
                "independent_of_row_contents": True,
            },
            "fixed_history": {
                "exact_images": history["unique_exact_images"],
                "phash_rows": history["phash_rows"],
                "manifest_sha256": history["manifest_sha256"],
            },
            "eligibility": counters,
            "outputs": {
                "catalog_rows": len(catalog),
                "catalog_sha256": sha256_file(catalog_path),
                "candidate_exposure_receipt_sha256": sha256_file(exposure_path),
            },
            "invariants": {
                "catalog_minimum_met": len(catalog)
                >= catalog_rule["minimum_eligible_units"],
                "catalog_exact_image_unique": len(
                    {row["image_sha256"] for row in catalog}
                )
                == len(catalog),
                "catalog_index_contiguous": [
                    row["catalog_index"] for row in catalog
                ]
                == list(range(len(catalog))),
                "catalog_exact_sha256_ordered": [
                    row["image_sha256"] for row in catalog
                ]
                == sorted(row["image_sha256"] for row in catalog),
                "selected_units_never_change_history_filter": True,
            },
            "elapsed_seconds": time.time() - started,
        }
        if not all(catalog_manifest["invariants"].values()):
            raise RuntimeError("one or more eligible-catalog invariants failed")
        write_json_atomic(catalog_manifest_path, catalog_manifest)

        duplicate_stats = duplicate_statistics(train_rows, validation_rows)
        split_manifest_path = (
            args.output_dir / data["post_tag_receipts"]["split_manifest"]
        )
        split_manifest = {
            "schema_version": 2,
            "protocol": protocol.reference(),
            "catalog": {
                "rows": len(catalog),
                "sha256": sha256_file(catalog_path),
                "manifest_sha256": sha256_file(catalog_manifest_path),
            },
            "sampling": {
                "seed": data["selection_seed"],
                "method": "independent_with_replacement",
                "validation_domain": draws["validation_domain"],
                "train_domain": draws["train_domain"],
                "unbiased_rejection_mapping": True,
                "duplicates_allowed_without_redraw": True,
                "cross_split_overlap_allowed_without_redraw": True,
            },
            "outputs": {
                "validation": {
                    "rows": len(validation_rows),
                    "sha256": sha256_file(validation_path),
                    "membership_sha256": sha256_file(
                        args.output_dir / "validation_membership.jsonl"
                    ),
                },
                "train": {
                    "rows": len(train_rows),
                    "sha256": sha256_file(train_path),
                    "membership_sha256": sha256_file(
                        args.output_dir / "train_membership.jsonl"
                    ),
                },
            },
            "duplicate_statistics": duplicate_stats,
            "invariants": {
                "validation_draw_count": len(validation_rows)
                == draws["validation_draws"],
                "train_draw_count": len(train_rows) == draws["train_draws"],
                "draw_sample_ids_unique": len(
                    {row["sample_id"] for row in validation_rows + train_rows}
                )
                == len(validation_rows) + len(train_rows),
                "all_draw_catalog_indices_in_range": all(
                    0 <= row["catalog_index"] < len(catalog)
                    for row in validation_rows + train_rows
                ),
                "target_eos_present": all(
                    row["target_token_ids"][-1] == row["assistant_eos_token_id"]
                    for row in validation_rows + train_rows
                ),
                "vlm_length_at_most_frozen_maximum": all(
                    len(row["full_token_ids"])
                    <= protocol.payload["training"]["max_sequence_length"]
                    for row in validation_rows + train_rows
                ),
                "duplicates_do_not_trigger_redraw": True,
            },
            "elapsed_seconds": time.time() - started,
        }
        if not all(split_manifest["invariants"].values()):
            raise RuntimeError("one or more independent-draw invariants failed")
        write_json_atomic(split_manifest_path, split_manifest)
        print(
            json.dumps(
                {
                    "catalog_manifest": catalog_manifest,
                    "split_manifest": split_manifest,
                },
                indent=2,
                sort_keys=True,
            )
        )
    except BaseException as error:
        write_json_atomic(
            failure_path,
            {
                "schema_version": 2,
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "protocol": protocol.reference(),
            },
        )
        raise


if __name__ == "__main__":
    main()
