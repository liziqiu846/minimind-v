#!/usr/bin/env python3
"""Build and audit XID-01 matched-support datasets and held-out panel."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

from experiments.stage2_protocol import Stage2Protocol
from experiments.xid01 import (
    BASE_ROWS,
    BASE_SHA256,
    BLOCK,
    CONDITIONS,
    HELDOUT_GROUPS,
    INJECTION_ROWS,
    TOTAL_TRAIN_ROWS,
    add_marker,
    block_audit,
    canonical_json_bytes,
    deterministic_png,
    image_order_key,
    normalized_pixel_sha256,
    normalized_rgb,
    sha256_bytes,
    sha256_file,
    token_record,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-parquet", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def inventory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        image_bytes = row["image_bytes"]
        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError(f"base row {index} lacks image bytes")
        image = normalized_rgb(image_bytes)
        pixel_sha = normalized_pixel_sha256(image)
        candidate = {
            "base_row_index": index,
            "draw_index": int(row["draw_index"]),
            "normalized_pixel_sha256": pixel_sha,
            "order_key": image_order_key(pixel_sha),
        }
        current = unique.get(pixel_sha)
        if current is None or (
            candidate["draw_index"], candidate["base_row_index"]
        ) < (current["draw_index"], current["base_row_index"]):
            unique[pixel_sha] = candidate
    ordered = sorted(
        unique.values(),
        key=lambda row: (row["order_key"], row["normalized_pixel_sha256"]),
    )
    required = INJECTION_ROWS + HELDOUT_GROUPS
    if len(ordered) < required:
        raise ValueError(f"DATA_INELIGIBLE: need {required} unique pixels")
    return ordered


def injection_row(
    source: dict[str, Any],
    *,
    condition: str,
    injection_index: int,
    visual_bit: int,
    target: int,
    key: str,
    marked_bytes: bytes,
    record: dict[str, Any],
    order_key: str,
) -> dict[str, Any]:
    result = dict(source)
    marked_sha = sha256_bytes(marked_bytes)
    result.update(
        {
            "catalog_unit_id": f"XID-01-{condition}-{injection_index:04d}",
            "image_bytes": marked_bytes,
            "image_sha256": marked_sha,
            "phash_hex": "xid01_not_computed",
            "row_rank_sha256": order_key,
            "representative_key_sha256": marked_sha,
            "canonical_conversation": record["canonical_conversation"],
            "full_token_ids": record["full_token_ids"],
            "lm_full_token_ids": record["lm_full_token_ids"],
            "assistant_target_start": record["assistant_target_start"],
            "assistant_target_end": record["assistant_target_end"],
            "lm_assistant_target_start": record["lm_assistant_target_start"],
            "lm_assistant_target_end": record["lm_assistant_target_end"],
            "target_token_ids": record["target_token_ids"],
            "target_token_count": record["target_token_count"],
            "assistant_eos_token_id": record["assistant_eos_token_id"],
            "sample_id": f"XID-01-{condition}-{injection_index:04d}",
            "split": "train",
            "draw_index": BASE_ROWS + injection_index,
            "draw_retry_index": 0,
            "draw_sha256": sha256_bytes(
                canonical_json_bytes(
                    {
                        "condition": condition,
                        "index": injection_index,
                        "visual_bit": visual_bit,
                        "key": key,
                        "target": target,
                        "image_sha256": marked_sha,
                    }
                )
            ),
        }
    )
    return result


def write_train(
    path: Path, base_table: pa.Table, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(rows) != INJECTION_ROWS:
        raise ValueError("injection row count mismatch")
    injection = pa.Table.from_pylist(rows, schema=base_table.schema)
    combined = pa.concat_tables([base_table, injection])
    if combined.num_rows != TOTAL_TRAIN_ROWS:
        raise ValueError("total train rows mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(combined, path, compression="zstd")
    return {
        "path": str(path.resolve()),
        "rows": pq.ParquetFile(path).metadata.num_rows,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory is nonempty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    base_path = args.base_parquet.resolve()
    if sha256_file(base_path) != BASE_SHA256:
        raise ValueError("base parquet SHA differs from frozen plan")
    base_table = pq.read_table(base_path)
    if base_table.num_rows != BASE_ROWS:
        raise ValueError("base parquet row count differs")
    base_rows = base_table.to_pylist()
    ordered = inventory(base_rows)
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )

    singleton_ids = {
        token: tokenizer(token, add_special_tokens=False).input_ids
        for token in ("a", "b", "c", "d", "e", "0", "1")
    }
    if any(len(ids) != 1 for ids in singleton_ids.values()):
        raise ValueError(f"frozen keys/digits are not singleton: {singleton_ids}")

    rows_by_condition = {condition: [] for condition in CONDITIONS}
    injection_manifest = []
    for injection_index, inventory_row in enumerate(ordered[:INJECTION_ROWS]):
        block_slot = injection_index % len(BLOCK)
        visual_bit, target, consistent_key, ambiguous_key = BLOCK[block_slot]
        source = base_rows[inventory_row["base_row_index"]]
        marked = add_marker(normalized_rgb(source["image_bytes"]), visual_bit)
        marked_bytes = deterministic_png(marked)
        entry = {
            "injection_index": injection_index,
            "block_index": injection_index // len(BLOCK),
            "block_slot": block_slot,
            "base_row_index": inventory_row["base_row_index"],
            "source_normalized_pixel_sha256": inventory_row[
                "normalized_pixel_sha256"
            ],
            "visual_bit": visual_bit,
            "target": target,
            "image_sha256": sha256_bytes(marked_bytes),
            "marked_normalized_pixel_sha256": normalized_pixel_sha256(marked),
            "keys": {
                "interaction-consistent": consistent_key,
                "interaction-ambiguous": ambiguous_key,
            },
        }
        injection_manifest.append(entry)
        for condition, key in entry["keys"].items():
            record = token_record(tokenizer, key, target)
            rows_by_condition[condition].append(
                injection_row(
                    source,
                    condition=condition,
                    injection_index=injection_index,
                    visual_bit=visual_bit,
                    target=target,
                    key=key,
                    marked_bytes=marked_bytes,
                    record=record,
                    order_key=inventory_row["order_key"],
                )
            )

    data = {}
    for condition in CONDITIONS:
        data[condition] = write_train(
            output / f"train_{condition}.parquet",
            base_table,
            rows_by_condition[condition],
        )

    heldout_dir = output / "heldout_images"
    heldout_dir.mkdir(parents=True, exist_ok=True)
    heldout_rows = []
    start = INJECTION_ROWS
    for local_index, inventory_row in enumerate(
        ordered[start : start + HELDOUT_GROUPS]
    ):
        source = base_rows[inventory_row["base_row_index"]]
        variants = {}
        for visual_bit in (0, 1):
            marked = add_marker(normalized_rgb(source["image_bytes"]), visual_bit)
            encoded = deterministic_png(marked)
            path = heldout_dir / f"{local_index:04d}_v{visual_bit}.png"
            path.write_bytes(encoded)
            variants[str(visual_bit)] = {
                "image_path": str(path.resolve()),
                "image_sha256": sha256_file(path),
                "normalized_pixel_sha256": normalized_pixel_sha256(marked),
            }
        heldout_rows.append(
            {
                "group_id": f"xid01-heldout-{local_index:04d}",
                "local_index": local_index,
                "base_row_index": inventory_row["base_row_index"],
                "source_normalized_pixel_sha256": inventory_row[
                    "normalized_pixel_sha256"
                ],
                "variants": variants,
            }
        )

    injection_pixels = [
        row["image_sha256"] for row in injection_manifest
    ]
    per_condition_target_ids = {
        condition: [
            list(row["target_token_ids"])
            for row in rows_by_condition[condition]
        ]
        for condition in CONDITIONS
    }
    per_condition_images = {
        condition: [row["image_sha256"] for row in rows_by_condition[condition]]
        for condition in CONDITIONS
    }
    target_spans = {
        condition: [
            (
                int(row["assistant_target_start"]),
                int(row["assistant_target_end"]),
                int(row["lm_assistant_target_start"]),
                int(row["lm_assistant_target_end"]),
                int(row["target_token_count"]),
            )
            for row in rows_by_condition[condition]
        ]
        for condition in CONDITIONS
    }
    token_pair_differences = []
    allowed_key_transitions = set()
    for target in (0, 1):
        c_ids = token_record(tokenizer, "c", target)["full_token_ids"]
        d_ids = token_record(tokenizer, "d", target)["full_token_ids"]
        differences = [
            (position, c_id, d_id)
            for position, (c_id, d_id) in enumerate(
                zip(c_ids, d_ids, strict=True)
            )
            if c_id != d_id
        ]
        if len(differences) != 1:
            raise ValueError("contextual c/d prompts do not differ at one token")
        position, c_id, d_id = differences[0]
        allowed_key_transitions.update(
            {
                (position, c_id, d_id),
                (position, d_id, c_id),
            }
        )
    for left, right in zip(
        rows_by_condition[CONDITIONS[0]],
        rows_by_condition[CONDITIONS[1]],
        strict=True,
    ):
        left_ids = list(left["full_token_ids"])
        right_ids = list(right["full_token_ids"])
        if len(left_ids) != len(right_ids):
            token_pair_differences.append({"valid": False, "count": -1})
            continue
        differences = [
            (position, left_id, right_id)
            for position, (left_id, right_id) in enumerate(
                zip(left_ids, right_ids, strict=True)
            )
            if left_id != right_id
        ]
        token_pair_differences.append(
            {
                "valid": len(differences) <= 1
                and all(row in allowed_key_transitions for row in differences),
                "count": len(differences),
            }
        )
    full_lengths = {
        condition: Counter(
            len(row["full_token_ids"]) for row in rows_by_condition[condition]
        )
        for condition in CONDITIONS
    }
    blocks = {condition: block_audit(condition) for condition in CONDITIONS}
    checks = {
        "condition_image_order_exact_match": (
            per_condition_images[CONDITIONS[0]]
            == per_condition_images[CONDITIONS[1]]
            == injection_pixels
        ),
        "condition_target_token_order_exact_match": (
            per_condition_target_ids[CONDITIONS[0]]
            == per_condition_target_ids[CONDITIONS[1]]
        ),
        "condition_prompt_lengths_match": (
            full_lengths[CONDITIONS[0]] == full_lengths[CONDITIONS[1]]
        ),
        "condition_target_spans_and_masks_match": (
            target_spans[CONDITIONS[0]] == target_spans[CONDITIONS[1]]
        ),
        "paired_token_records_differ_only_at_key": all(
            row["valid"] for row in token_pair_differences
        ),
        "block_visual_marginals_match": (
            blocks[CONDITIONS[0]]["visual_counts"]
            == blocks[CONDITIONS[1]]["visual_counts"]
            == {0: 6, 1: 4}
        ),
        "block_key_marginals_match": (
            blocks[CONDITIONS[0]]["key_counts"]
            == blocks[CONDITIONS[1]]["key_counts"]
            == {"a": 2, "b": 2, "c": 2, "d": 2, "e": 2}
        ),
        "block_target_marginals_match": (
            blocks[CONDITIONS[0]]["target_counts"]
            == blocks[CONDITIONS[1]]["target_counts"]
            == {0: 6, 1: 4}
        ),
        "per_key_target_entropy_match": (
            blocks[CONDITIONS[0]]["key_target_counts"]
            == blocks[CONDITIONS[1]]["key_target_counts"]
        ),
        "target_cell_absent_both": not any(
            blocks[condition]["target_cell_present"] for condition in CONDITIONS
        ),
        "consistent_xor_all_eight": (
            blocks["interaction-consistent"]["xor_correct_a_through_d"] == 8
        ),
        "ambiguous_xor_four_of_eight": (
            blocks["interaction-ambiguous"]["xor_correct_a_through_d"] == 4
        ),
        "heldout_disjoint_from_injection": not (
            {
                row["source_normalized_pixel_sha256"]
                for row in injection_manifest
            }
            & {
                row["source_normalized_pixel_sha256"] for row in heldout_rows
            }
        ),
        "singleton_keys_and_targets": all(
            len(ids) == 1 for ids in singleton_ids.values()
        ),
    }
    eligible = all(checks.values())
    manifest = {
        "schema_version": 1,
        "manifest_id": "XID-01-round4-heldout-v1",
        "rows": heldout_rows,
        "panel_items_per_group": 9,
        "target_item": {"key": "e", "visual_bit": 1, "gold": "1"},
        "mechanism_keys": ["a", "b", "c", "d"],
        "final_confirmation_accessed": False,
    }
    write_json(output / "injection_manifest.json", {"rows": injection_manifest})
    write_json(output / "heldout_manifest.json", manifest)
    audit = {
        "schema_version": 1,
        "audit_id": "XID-01-round4-preflight-v1",
        "status": "passed" if eligible else "failed",
        "eligible_for_training": eligible,
        "eligible_for_scoring": eligible,
        "base": {
            "path": str(base_path),
            "rows": base_table.num_rows,
            "sha256": sha256_file(base_path),
            "unique_normalized_pixels": len(ordered),
        },
        "data": data,
        "blocks": blocks,
        "checks": checks,
        "singleton_token_ids": singleton_ids,
        "full_token_length_counts": {
            condition: dict(sorted(counter.items()))
            for condition, counter in full_lengths.items()
        },
        "paired_token_difference_counts": dict(
            sorted(
                Counter(row["count"] for row in token_pair_differences).items()
            )
        ),
        "injection_rows": INJECTION_ROWS,
        "heldout_groups": HELDOUT_GROUPS,
        "total_train_rows": TOTAL_TRAIN_ROWS,
        "training_runs_started": 0,
        "model_inference_performed": False,
        "final_confirmation_accessed": False,
    }
    write_json(output / "data_audit.json", audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    if not eligible:
        raise RuntimeError("XID-01 preflight checks did not all pass")
    return audit


def main() -> None:
    prepare(parse_args())


if __name__ == "__main__":
    main()
