#!/usr/bin/env python3
"""Independently reconstruct and verify the Stage 2 v2 catalog and draws."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import struct
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import imagehash
import pyarrow.parquet as pq
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import build_token_record, normalized_image
from experiments.stage2_protocol import Stage2Protocol, sha256_file, write_json_atomic


def encode_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def independent_row_rank(domain: str, seed: int, row_index: int) -> bytes:
    return hashlib.sha256(
        encode_string(domain)
        + seed.to_bytes(8, "little", signed=False)
        + row_index.to_bytes(8, "little", signed=False)
    ).digest()


def independently_select_rows(
    source_rows: int, capacity: int, domain: str, seed: int
) -> list[tuple[int, bytes]]:
    if not 0 < capacity <= source_rows:
        raise ValueError("invalid source row capacity")
    retained: list[tuple[int, int, int, bytes]] = []
    for index in range(source_rows):
        digest = independent_row_rank(domain, seed, index)
        item = (-int.from_bytes(digest, "big"), -index, index, digest)
        if len(retained) != capacity:
            heapq.heappush(retained, item)
        elif item > retained[0]:
            heapq.heapreplace(retained, item)
    return sorted(
        ((index, digest) for _, _, index, digest in retained),
        key=lambda item: (item[1], item[0]),
    )


def independent_draw(
    domain: str, seed: int, draw_index: int, catalog_size: int
) -> tuple[int, int, str]:
    threshold = ((1 << 256) // catalog_size) * catalog_size
    retry = 0
    while True:
        digest = hashlib.sha256(
            encode_string(domain)
            + seed.to_bytes(8, "little", signed=False)
            + draw_index.to_bytes(8, "little", signed=False)
            + retry.to_bytes(8, "little", signed=False)
        ).digest()
        integer = int.from_bytes(digest, byteorder="big", signed=False)
        if integer < threshold:
            return integer % catalog_size, retry, digest.hex()
        retry += 1


class IndependentHammingTree:
    def __init__(self, values: Iterable[int]) -> None:
        self.root: tuple[int, dict[int, Any]] | None = None
        for value in values:
            self.insert(value)

    def insert(self, value: int) -> None:
        if self.root is None:
            self.root = (value, {})
            return
        node = self.root
        while True:
            center, children = node
            distance = (center ^ value).bit_count()
            if distance == 0:
                return
            if distance not in children:
                children[distance] = (value, {})
                return
            node = children[distance]

    def within(self, value: int, radius: int) -> bool:
        pending = [] if self.root is None else [self.root]
        while pending:
            center, children = pending.pop()
            distance = (center ^ value).bit_count()
            if distance <= radius:
                return True
            pending.extend(
                child
                for edge, child in children.items()
                if distance - radius <= edge <= distance + radius
            )
        return False


def one_image(value: Any) -> bytes:
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("expected exactly one image")
        value = value[0]
    if not isinstance(value, bytes):
        raise ValueError("image payload is not bytes")
    return value


TOKEN_FIELDS = (
    "canonical_conversation",
    "full_token_ids",
    "lm_full_token_ids",
    "assistant_target_start",
    "assistant_target_end",
    "lm_assistant_target_start",
    "lm_assistant_target_end",
    "target_token_ids",
    "target_token_count",
    "assistant_eos_token_id",
)


def history(protocol: Stage2Protocol) -> tuple[set[str], list[int]]:
    definition = protocol.payload["history_exclusion"]
    exact = {
        line.strip()
        for line in (REPO_ROOT / definition["exact_sha256_path"]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }
    phashes = [
        int(line.split()[1], 16)
        for line in (REPO_ROOT / definition["phash_path"]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    return exact, phashes


def reconstruct_catalog(
    protocol: Stage2Protocol,
    selected_rows: list[tuple[int, bytes]],
    tokenizer,
) -> list[dict[str, Any]]:
    data = protocol.payload["data"]
    source = protocol.asset_path("source_dataset")
    exact_history, phash_history = history(protocol)
    fixed_tree = IndependentHammingTree(phash_history)
    ranks = {index: digest for index, digest in selected_rows}
    selected = set(ranks)
    representatives: dict[str, tuple[tuple[bytes, int], dict[str, Any]]] = {}
    source_file = pq.ParquetFile(source)
    row_index = 0
    visited = 0
    for batch in source_file.iter_batches(
        batch_size=4096, columns=("conversations", "image_bytes")
    ):
        conversations = batch.column(0).to_pylist()
        images = batch.column(1).to_pylist()
        for conversation, image_value in zip(conversations, images, strict=True):
            if row_index not in selected:
                row_index += 1
                continue
            visited += 1
            try:
                image_bytes = one_image(image_value)
            except ValueError:
                row_index += 1
                continue
            exact = hashlib.sha256(image_bytes).hexdigest()
            if exact in exact_history:
                row_index += 1
                continue
            try:
                token = build_token_record(
                    conversation,
                    tokenizer,
                    image_token_count=protocol.payload["model"]["image_token_count"],
                    max_length=protocol.payload["training"]["max_sequence_length"],
                )
            except (ValueError, TypeError, json.JSONDecodeError):
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
            except Exception:
                row_index += 1
                continue
            if fixed_tree.within(
                phash_value,
                data["phash"]["maximum_allowed_historical_hamming_distance"],
            ):
                row_index += 1
                continue
            conversation_sha = hashlib.sha256(
                token["canonical_conversation"].encode("utf-8")
            ).digest()
            key = conversation_sha, row_index
            row = {
                "image_bytes": image_bytes,
                "image_sha256": exact,
                "phash_hex": phash_hex,
                "source_row_index": row_index,
                "row_rank_sha256": ranks[row_index].hex(),
                "representative_key_sha256": conversation_sha.hex(),
                **token,
            }
            previous = representatives.get(exact)
            if previous is None or key < previous[0]:
                representatives[exact] = key, row
            row_index += 1
    if row_index != source_file.metadata.num_rows or visited != len(selected_rows):
        raise RuntimeError("independent source replay did not consume the declared rows")
    result = []
    for catalog_index, exact in enumerate(sorted(representatives)):
        row = representatives[exact][1]
        result.append(
            {
                "catalog_index": catalog_index,
                "catalog_unit_id": f"stage2-v2-unit-{catalog_index:05d}-{exact[:12]}",
                **row,
            }
        )
    return result


def assert_rows_equal(actual: dict[str, Any], expected: dict[str, Any], role: str) -> None:
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise ValueError(f"{role} columns differ; missing={missing}, extra={extra}")
    for key in expected:
        if actual[key] != expected[key]:
            raise ValueError(f"{role} field does not replay: {key}")


def expected_draw_row(
    catalog_row: dict[str, Any],
    split: str,
    draw_index: int,
    retry: int,
    digest: str,
) -> dict[str, Any]:
    return {
        **catalog_row,
        "sample_id": f"stage2-v2-{split}-{draw_index:05d}",
        "split": split,
        "draw_index": draw_index,
        "draw_retry_index": retry,
        "draw_sha256": digest,
    }


def membership(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
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
    return {key: row[key] for key in keys}


def canonical_lines(rows: Iterable[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows
    ).encode("utf-8")


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--split-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replay-output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in (args.output, args.replay_output):
        if path.exists():
            raise FileExistsError(f"verification output already exists: {path}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    protocol.verify_runtime_integrity()
    if protocol.payload["schema_version"] != 2:
        raise ValueError("the v2 verifier requires protocol schema_version 2")
    if args.split_dir.resolve() != protocol.confirmation_directory().resolve():
        raise ValueError("split directory differs from the frozen v2 output directory")
    started = time.time()
    failure_path = args.split_dir / "verification_failure_receipt.json"
    try:
        data = protocol.payload["data"]
        receipts = data["post_tag_receipts"]
        catalog_manifest_path = args.split_dir / receipts["catalog_manifest"]
        split_manifest_path = args.split_dir / receipts["split_manifest"]
        catalog_manifest = json.loads(catalog_manifest_path.read_text(encoding="utf-8"))
        split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
        reference = protocol.reference()
        if catalog_manifest.get("protocol") != reference:
            raise ValueError("catalog manifest does not bind the frozen protocol")
        if split_manifest.get("protocol") != reference:
            raise ValueError("split manifest does not bind the frozen protocol")

        catalog_rule = data["catalog"]
        selected_rows = independently_select_rows(
            data["source_rows"],
            catalog_rule["source_row_capacity"],
            catalog_rule["row_rank_domain"],
            data["selection_seed"],
        )
        expected_index_bytes = "".join(
            f"{index} {digest.hex()}\n" for index, digest in selected_rows
        ).encode("utf-8")
        index_path = args.split_dir / "catalog_source_indices.txt"
        if index_path.read_bytes() != expected_index_bytes:
            raise ValueError("value-independent catalog source-row selection does not replay")

        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        replay_catalog = reconstruct_catalog(protocol, selected_rows, tokenizer)
        catalog_path = args.split_dir / receipts["catalog"]
        stored_catalog = pq.read_table(catalog_path).to_pylist()
        if len(stored_catalog) != len(replay_catalog):
            raise ValueError("eligible catalog size does not replay")
        if len(stored_catalog) < catalog_rule["minimum_eligible_units"]:
            raise ValueError("eligible catalog is below the frozen minimum")
        for index, (actual, expected) in enumerate(
            zip(stored_catalog, replay_catalog, strict=True)
        ):
            assert_rows_equal(actual, expected, f"catalog row {index}")

        if catalog_manifest["outputs"]["catalog_sha256"] != sha256_file(catalog_path):
            raise ValueError("catalog hash differs from catalog manifest")
        if split_manifest["catalog"]["sha256"] != sha256_file(catalog_path):
            raise ValueError("catalog hash differs from split manifest")
        if split_manifest["catalog"]["manifest_sha256"] != sha256_file(
            catalog_manifest_path
        ):
            raise ValueError("catalog manifest hash differs from split manifest")

        draws = data["independent_draws"]
        replay_draw_identities = []
        actual_draws: dict[str, list[dict[str, Any]]] = {}
        for split, count, domain in (
            ("validation", draws["validation_draws"], draws["validation_domain"]),
            ("train", draws["train_draws"], draws["train_domain"]),
        ):
            path = args.split_dir / f"{split}.parquet"
            rows = pq.read_table(path).to_pylist()
            actual_draws[split] = rows
            if len(rows) != count:
                raise ValueError(f"{split} draw count differs from frozen protocol")
            if split_manifest["outputs"][split]["sha256"] != sha256_file(path):
                raise ValueError(f"{split} parquet hash differs from split manifest")
            expected_membership = []
            for draw_index, actual in enumerate(rows):
                catalog_index, retry, digest = independent_draw(
                    domain, data["selection_seed"], draw_index, len(replay_catalog)
                )
                expected = expected_draw_row(
                    replay_catalog[catalog_index],
                    split,
                    draw_index,
                    retry,
                    digest,
                )
                assert_rows_equal(actual, expected, f"{split} draw {draw_index}")
                member = membership(expected)
                expected_membership.append(member)
                replay_draw_identities.append(member)
            membership_path = args.split_dir / f"{split}_membership.jsonl"
            if parse_jsonl(membership_path) != expected_membership:
                raise ValueError(f"{split} membership receipt does not replay")
            if split_manifest["outputs"][split]["membership_sha256"] != sha256_file(
                membership_path
            ):
                raise ValueError(f"{split} membership hash differs from split manifest")

        all_draws = actual_draws["validation"] + actual_draws["train"]
        exact_history, phash_history = history(protocol)
        unique_catalog_exact = {row["image_sha256"] for row in replay_catalog}
        if len(unique_catalog_exact) != len(replay_catalog):
            raise ValueError("eligible catalog contains duplicate exact images")
        if unique_catalog_exact & exact_history:
            raise ValueError("eligible catalog overlaps exact-image history")
        fixed_tree = IndependentHammingTree(phash_history)
        if any(
            fixed_tree.within(
                int(row["phash_hex"], 16),
                data["phash"]["maximum_allowed_historical_hamming_distance"],
            )
            for row in replay_catalog
        ):
            raise ValueError("eligible catalog violates fixed historical pHash distance")
        train_indices = [row["catalog_index"] for row in actual_draws["train"]]
        validation_indices = [
            row["catalog_index"] for row in actual_draws["validation"]
        ]
        duplicate_statistics = {
            "train_draws": len(train_indices),
            "train_unique_catalog_units": len(set(train_indices)),
            "train_repeated_draws": len(train_indices) - len(set(train_indices)),
            "validation_draws": len(validation_indices),
            "validation_unique_catalog_units": len(set(validation_indices)),
            "validation_repeated_draws": len(validation_indices)
            - len(set(validation_indices)),
            "cross_split_overlapping_catalog_units": len(
                set(train_indices) & set(validation_indices)
            ),
        }
        if duplicate_statistics != split_manifest["duplicate_statistics"]:
            raise ValueError("duplicate statistics differ from split manifest")
        if len({row["sample_id"] for row in all_draws}) != len(all_draws):
            raise ValueError("draw sample identities are not unique")
        if any(
            row["target_token_ids"][-1] != row["assistant_eos_token_id"]
            or row["target_token_count"] != len(row["target_token_ids"])
            for row in all_draws
        ):
            raise ValueError("a draw has a truncated or inconsistent target")

        catalog_replay_rows = [
            {
                key: row[key]
                for key in (
                    "catalog_index",
                    "catalog_unit_id",
                    "image_sha256",
                    "phash_hex",
                    "source_row_index",
                    "row_rank_sha256",
                    "representative_key_sha256",
                    *TOKEN_FIELDS,
                )
            }
            for row in replay_catalog
        ]
        catalog_replay_sha256 = hashlib.sha256(
            canonical_lines(catalog_replay_rows)
        ).hexdigest()
        draw_replay_sha256 = hashlib.sha256(
            canonical_lines(replay_draw_identities)
        ).hexdigest()
        verification = {
            "schema_version": 2,
            "status": "passed",
            "protocol": reference,
            "catalog_manifest_sha256": sha256_file(catalog_manifest_path),
            "split_manifest_sha256": sha256_file(split_manifest_path),
            "catalog_sha256": sha256_file(catalog_path),
            "train_sha256": sha256_file(args.split_dir / "train.parquet"),
            "validation_sha256": sha256_file(args.split_dir / "validation.parquet"),
            "verified_catalog_units": len(replay_catalog),
            "verified_draws": len(all_draws),
            "history_exact_images": len(exact_history),
            "history_phash_rows": len(phash_history),
            "duplicate_statistics": duplicate_statistics,
            "canonical_catalog_replay_sha256": catalog_replay_sha256,
            "canonical_draw_replay_sha256": draw_replay_sha256,
            "invariants": {
                "source_row_selection_reproduces_without_row_contents": True,
                "eligible_catalog_reconstructs_from_source": True,
                "catalog_exact_unique_and_absent_from_history": True,
                "catalog_phash_distance_greater_than_six_from_fixed_history": True,
                "catalog_token_records_reproduce": True,
                "domain_separated_draw_streams_reproduce": True,
                "draws_are_with_replacement_without_duplicate_rejection": True,
                "draw_membership_receipts_reproduce": True,
                "target_eos_present_and_no_target_truncation": True,
            },
            "elapsed_seconds": time.time() - started,
        }
        replay = {
            "schema_version": 2,
            "status": "passed",
            "protocol": reference,
            "catalog_source_indices_sha256": sha256_file(index_path),
            "catalog_manifest_sha256": sha256_file(catalog_manifest_path),
            "split_manifest_sha256": sha256_file(split_manifest_path),
            "catalog_sha256": sha256_file(catalog_path),
            "canonical_catalog_replay_sha256": catalog_replay_sha256,
            "canonical_draw_replay_sha256": draw_replay_sha256,
            "validation_membership_sha256": sha256_file(
                args.split_dir / "validation_membership.jsonl"
            ),
            "train_membership_sha256": sha256_file(
                args.split_dir / "train_membership.jsonl"
            ),
            "catalog_units": len(replay_catalog),
            "validation_draws": len(actual_draws["validation"]),
            "train_draws": len(actual_draws["train"]),
            "validation_total_retries": sum(
                row["draw_retry_index"] for row in actual_draws["validation"]
            ),
            "train_total_retries": sum(
                row["draw_retry_index"] for row in actual_draws["train"]
            ),
            "duplicate_statistics": duplicate_statistics,
        }
        write_json_atomic(args.output, verification)
        write_json_atomic(args.replay_output, replay)
        print(json.dumps({"verification": verification, "replay": replay}, indent=2))
    except BaseException as error:
        write_json_atomic(
            failure_path,
            {
                "schema_version": 2,
                "status": "failed",
                "protocol": protocol.reference(),
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
            },
        )
        raise


if __name__ == "__main__":
    main()
