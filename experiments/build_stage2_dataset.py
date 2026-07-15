#!/usr/bin/env python3
"""Build the frozen 10k/2k Stage 2 confirmation split without image leakage."""

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
from typing import Iterable

import imagehash
import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import (
    build_token_record,
    canonical_conversation,
    normalized_image,
)
from experiments.stage2_protocol import (
    DEFAULT_FROZEN,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)


def serialized_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def candidate_rank(seed: int, image_sha256: bytes) -> bytes:
    return hashlib.sha256(
        serialized_string("stage2-split-v1") + struct.pack("<Q", seed) + image_sha256
    ).digest()


class HammingBKTree:
    """Exact radius queries for 64-bit perceptual hashes."""

    def __init__(self, values: Iterable[int] = ()) -> None:
        self.root: tuple[int, dict] | None = None
        for value in values:
            self.add(value)

    @staticmethod
    def distance(left: int, right: int) -> int:
        return (left ^ right).bit_count()

    def add(self, value: int) -> None:
        if self.root is None:
            self.root = (value, {})
            return
        node = self.root
        while True:
            current, children = node
            distance = self.distance(value, current)
            if distance == 0:
                return
            child = children.get(distance)
            if child is None:
                children[distance] = (value, {})
                return
            node = child

    def has_within(self, value: int, radius: int) -> bool:
        if self.root is None:
            return False
        pending = [self.root]
        while pending:
            current, children = pending.pop()
            distance = self.distance(value, current)
            if distance <= radius:
                return True
            lower, upper = distance - radius, distance + radius
            pending.extend(
                child for edge, child in children.items() if lower <= edge <= upper
            )
        return False


@dataclass
class Candidate:
    image_sha256: bytes
    rank: bytes
    image_bytes: bytes
    source_row_index: int
    canonical_conversation: str | None
    representative_key: tuple[bytes, int] | None

    @property
    def order_key(self) -> tuple[bytes, bytes, int]:
        return self.rank, self.image_sha256, self.source_row_index


def source_image_bytes(value) -> bytes:
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("confirmation candidates must contain exactly one image")
        value = value[0]
    if not isinstance(value, bytes):
        raise ValueError("confirmation image is not bytes")
    return value


def representative(value, row_index: int) -> tuple[str, tuple[bytes, int]]:
    _, canonical = canonical_conversation(value)
    key = hashlib.sha256(canonical.encode("utf-8")).digest(), row_index
    return canonical, key


def scan_candidate_pool(
    source: Path,
    history_exact: set[bytes],
    seed: int,
    capacity: int,
) -> tuple[list[Candidate], dict]:
    parquet = pq.ParquetFile(source)
    heap: list[tuple[int, int, bytes]] = []
    candidates: dict[bytes, Candidate] = {}
    seen: set[bytes] = set()
    row_index = 0
    exact_history_rejections = duplicate_rows = malformed_rows = 0
    for batch in parquet.iter_batches(
        batch_size=4096, columns=("conversations", "image_bytes")
    ):
        conversations = batch.column(0).to_pylist()
        images = batch.column(1).to_pylist()
        for conversation, raw_image in zip(conversations, images, strict=True):
            try:
                image_bytes = source_image_bytes(raw_image)
            except ValueError:
                malformed_rows += 1
                row_index += 1
                continue
            image_sha = hashlib.sha256(image_bytes).digest()
            if image_sha in history_exact:
                exact_history_rejections += 1
                row_index += 1
                continue
            if image_sha in seen:
                duplicate_rows += 1
                candidate = candidates.get(image_sha)
                if candidate is not None:
                    try:
                        canonical, key = representative(conversation, row_index)
                    except (ValueError, TypeError, json.JSONDecodeError):
                        pass
                    else:
                        if candidate.representative_key is None or key < candidate.representative_key:
                            candidate.canonical_conversation = canonical
                            candidate.representative_key = key
                            candidate.source_row_index = row_index
                row_index += 1
                continue
            seen.add(image_sha)
            rank = candidate_rank(seed, image_sha)
            rank_integer = int.from_bytes(rank, "big")
            sha_integer = int.from_bytes(image_sha, "big")
            heap_key = (-rank_integer, -sha_integer, image_sha)
            enters = len(heap) < capacity or heap_key > heap[0]
            if enters:
                try:
                    canonical, key = representative(conversation, row_index)
                except (ValueError, TypeError, json.JSONDecodeError):
                    canonical, key = None, None
                candidate = Candidate(
                    image_sha256=image_sha,
                    rank=rank,
                    image_bytes=image_bytes,
                    source_row_index=row_index,
                    canonical_conversation=canonical,
                    representative_key=key,
                )
                if len(heap) == capacity:
                    _, _, evicted_sha = heapq.heapreplace(heap, heap_key)
                    del candidates[evicted_sha]
                else:
                    heapq.heappush(heap, heap_key)
                candidates[image_sha] = candidate
            row_index += 1
    if row_index != parquet.metadata.num_rows:
        raise RuntimeError("source scan did not visit every row")
    return sorted(candidates.values(), key=lambda item: item.order_key), {
        "source_rows_scanned": row_index,
        "unique_nonhistorical_exact_images": len(seen),
        "exact_history_rejections": exact_history_rejections,
        "duplicate_nonhistorical_rows": duplicate_rows,
        "malformed_image_rows": malformed_rows,
        "candidate_pool_capacity": capacity,
        "candidate_pool_size": len(candidates),
    }


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
    os.replace(temporary, path)


def write_parquet(path: Path, rows: list[dict]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, temporary, compression="zstd", compression_level=9)
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-pool", type=int, default=50000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    protocol.require_frozen()
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
        history = protocol.payload["history_exclusion"]
        history_exact = {
            bytes.fromhex(line.strip())
            for line in (REPO_ROOT / history["exact_sha256_path"]).read_text().splitlines()
            if line.strip()
        }
        history_phashes = []
        for line in (REPO_ROOT / history["phash_path"]).read_text().splitlines():
            if line.strip():
                _, phash_hex = line.split()
                history_phashes.append(int(phash_hex, 16))
        forbidden = HammingBKTree(history_phashes)
        candidates, scan = scan_candidate_pool(
            source, history_exact, data["selection_seed"], args.candidate_pool
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        required = data["validation_images"] + data["train_images"]
        selected = []
        exposures = []
        rejections = {
            "missing_canonical_conversation": 0,
            "token_or_template_ineligible": 0,
            "image_decode_or_phash_failure": 0,
            "perceptual_distance_at_most_6": 0,
        }
        for candidate in candidates:
            if len(selected) == required:
                break
            if candidate.canonical_conversation is None:
                rejections["missing_canonical_conversation"] += 1
                continue
            try:
                token_record = build_token_record(
                    candidate.canonical_conversation,
                    tokenizer,
                    image_token_count=protocol.payload["model"]["image_token_count"],
                    max_length=protocol.payload["training"]["max_sequence_length"],
                )
            except (ValueError, TypeError, json.JSONDecodeError):
                rejections["token_or_template_ineligible"] += 1
                continue
            try:
                phash_hex = str(
                    imagehash.phash(
                        normalized_image(candidate.image_bytes),
                        hash_size=data["phash"]["hash_size"],
                        highfreq_factor=data["phash"]["highfreq_factor"],
                    )
                )
                phash_value = int(phash_hex, 16)
            except Exception as error:
                exposures.append(
                    {
                        "image_sha256": candidate.image_sha256.hex(),
                        "source_row_index": candidate.source_row_index,
                        "status": "decode_or_phash_failure",
                        "error_type": type(error).__name__,
                    }
                )
                rejections["image_decode_or_phash_failure"] += 1
                continue
            exposure = {
                "image_sha256": candidate.image_sha256.hex(),
                "phash_hex": phash_hex,
                "source_row_index": candidate.source_row_index,
                "rank_sha256": candidate.rank.hex(),
            }
            if forbidden.has_within(phash_value, data["phash"]["maximum_allowed_hamming_distance"]):
                exposure["status"] = "perceptual_rejection"
                exposures.append(exposure)
                rejections["perceptual_distance_at_most_6"] += 1
                continue
            split = "validation" if len(selected) < data["validation_images"] else "train"
            split_index = (
                len(selected) if split == "validation" else len(selected) - data["validation_images"]
            )
            sample_id = f"stage2-{split}-{split_index:05d}-{candidate.image_sha256.hex()[:12]}"
            row = {
                "sample_id": sample_id,
                "split": split,
                "split_index": split_index,
                "selection_index": len(selected),
                "image_bytes": candidate.image_bytes,
                "image_sha256": candidate.image_sha256.hex(),
                "phash_hex": phash_hex,
                "source_row_index": candidate.source_row_index,
                "rank_sha256": candidate.rank.hex(),
                "conversations": candidate.canonical_conversation,
                **token_record,
            }
            forbidden.add(phash_value)
            exposure["status"] = "selected"
            exposure["sample_id"] = sample_id
            exposure["split"] = split
            exposures.append(exposure)
            selected.append(row)
        write_jsonl(args.output_dir / "candidate_exposure_receipt.jsonl", exposures)
        if len(selected) != required:
            raise RuntimeError(
                f"candidate pool exhausted with {len(selected)}/{required} eligible images; "
                "rerun from a clean output directory with a larger mechanically expanded pool"
            )
        validation_rows = selected[:data["validation_images"]]
        train_rows = selected[data["validation_images"]:]
        if len(validation_rows) != data["validation_images"] or len(train_rows) != data["train_images"]:
            raise RuntimeError("confirmation split sizes are incorrect")
        train_path = args.output_dir / "train.parquet"
        validation_path = args.output_dir / "validation.parquet"
        write_parquet(validation_path, validation_rows)
        write_parquet(train_path, train_rows)
        write_jsonl(
            args.output_dir / "validation_membership.jsonl",
            ({key: row[key] for key in (
                "sample_id", "image_sha256", "phash_hex", "source_row_index",
                "rank_sha256", "target_token_count",
            )} for row in validation_rows),
        )
        write_jsonl(
            args.output_dir / "train_membership.jsonl",
            ({key: row[key] for key in (
                "sample_id", "image_sha256", "phash_hex", "source_row_index",
                "rank_sha256", "target_token_count",
            )} for row in train_rows),
        )
        manifest = {
            "schema_version": 1,
            "protocol": protocol.reference(),
            "source": {"path": str(source), "sha256": sha256_file(source)},
            "selection": {
                "seed": data["selection_seed"],
                "validation_first": data["validation_images"],
                "training_second": data["train_images"],
                "rank_domain": data["candidate_rank"]["domain"],
                "phash_distance_rule": "strictly greater than 6 from history and all selected images",
                "scan": scan,
                "rejections": rejections,
                "candidate_exposures": len(exposures),
            },
            "history": {
                "exact_images": len(history_exact),
                "phash_rows": len(history_phashes),
                "manifest_sha256": history["manifest_sha256"],
            },
            "outputs": {
                "validation": {
                    "rows": len(validation_rows),
                    "sha256": sha256_file(validation_path),
                    "membership_sha256": sha256_file(args.output_dir / "validation_membership.jsonl"),
                },
                "train": {
                    "rows": len(train_rows),
                    "sha256": sha256_file(train_path),
                    "membership_sha256": sha256_file(args.output_dir / "train_membership.jsonl"),
                },
                "candidate_exposure_receipt_sha256": sha256_file(
                    args.output_dir / "candidate_exposure_receipt.jsonl"
                ),
            },
            "invariants": {
                "exact_unique_and_disjoint": len({row["image_sha256"] for row in selected}) == required,
                "target_eos_present": all(
                    row["target_token_ids"][-1] == row["assistant_eos_token_id"] for row in selected
                ),
                "vlm_length_at_most_450": all(len(row["full_token_ids"]) <= 450 for row in selected),
                "selected_phash_unique": len({row["phash_hex"] for row in selected}) == required,
            },
            "elapsed_seconds": time.time() - started,
        }
        if not all(manifest["invariants"].values()):
            raise RuntimeError("one or more confirmation split invariants failed")
        write_json_atomic(args.output_dir / "split_manifest.json", manifest)
        print(json.dumps(manifest, indent=2, sort_keys=True))
    except BaseException as error:
        write_json_atomic(
            failure_path,
            {
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
