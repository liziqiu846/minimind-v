#!/usr/bin/env python3
"""Build and audit the two VISSUP-01 training datasets and scoring panels."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer

from experiments.stage2_protocol import Stage2Protocol
from experiments.vissup01 import (
    ANGLE_TO_LABEL,
    BASE_ROWS,
    BASE_SHA256,
    CVBENCH_BYTES,
    CVBENCH_ROWS,
    CVBENCH_SHA256,
    HELDOUT_ROTATION_ROWS,
    INJECTION_ROWS,
    TOTAL_TRAIN_ROWS,
    build_choice_record,
    canonical_json_bytes,
    choice_labels,
    cvbench_gold_label,
    deterministic_png,
    image_order_key,
    normalized_pixel_sha256,
    normalized_rgb,
    rotate_clockwise,
    rotation_token_records,
    sha256_bytes,
    sha256_file,
    write_json,
)


REQUIRED_CV_COLUMNS = {
    "idx",
    "type",
    "task",
    "image",
    "question",
    "choices",
    "answer",
    "prompt",
    "filename",
    "source",
    "source_dataset",
    "source_filename",
    "target_class",
    "target_size",
    "bbox",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-parquet", type=Path, required=True)
    parser.add_argument("--cvbench-parquet", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def _base_pixel_inventory(rows: list[dict[str, Any]]) -> tuple[list[dict], dict]:
    unique: dict[str, dict[str, Any]] = {}
    raw_hash_matches = 0
    for index, row in enumerate(rows):
        image_bytes = row["image_bytes"]
        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError(f"base row {index} lacks image bytes")
        if sha256_bytes(image_bytes) == row["image_sha256"]:
            raw_hash_matches += 1
        image = normalized_rgb(image_bytes)
        pixel_sha = normalized_pixel_sha256(image)
        candidate = {
            "base_row_index": index,
            "draw_index": int(row["draw_index"]),
            "source_row_index": int(row["source_row_index"]),
            "raw_image_sha256": sha256_bytes(image_bytes),
            "normalized_pixel_sha256": pixel_sha,
            "width": image.width,
            "height": image.height,
            "order_key": image_order_key(pixel_sha),
        }
        current = unique.get(pixel_sha)
        if current is None or (
            candidate["draw_index"],
            candidate["base_row_index"],
        ) < (
            current["draw_index"],
            current["base_row_index"],
        ):
            unique[pixel_sha] = candidate
    ordered = sorted(
        unique.values(),
        key=lambda row: (row["order_key"], row["normalized_pixel_sha256"]),
    )
    if len(ordered) < INJECTION_ROWS + HELDOUT_ROTATION_ROWS:
        raise ValueError("DATA_INELIGIBLE: fewer than 2,016 unique base pixels")
    audit = {
        "base_rows": len(rows),
        "unique_normalized_pixel_count": len(ordered),
        "duplicate_draw_count": len(rows) - len(ordered),
        "encoded_image_sha_matches": raw_hash_matches,
    }
    return ordered, audit


def _rotation_entry(
    base_row: dict[str, Any],
    inventory_row: dict[str, Any],
    *,
    split: str,
    local_index: int,
    image_dir: Path | None,
) -> tuple[dict[str, Any], bytes]:
    degrees = (0, 90, 180, 270)[local_index % 4]
    gold = ANGLE_TO_LABEL[degrees]
    source = normalized_rgb(base_row["image_bytes"])
    rotated = rotate_clockwise(source, degrees)
    encoded = deterministic_png(rotated)
    pixel_sha = normalized_pixel_sha256(rotated)
    entry = {
        **inventory_row,
        "split_role": split,
        "local_index": local_index,
        "rotation_degrees_clockwise": degrees,
        "gold_label": gold,
        "rotated_image_sha256": sha256_bytes(encoded),
        "rotated_normalized_pixel_sha256": pixel_sha,
        "rotated_width": rotated.width,
        "rotated_height": rotated.height,
    }
    if image_dir is not None:
        image_dir.mkdir(parents=True, exist_ok=True)
        path = image_dir / f"{local_index:04d}.png"
        path.write_bytes(encoded)
        if sha256_file(path) != entry["rotated_image_sha256"]:
            raise RuntimeError("written held-out rotation image hash mismatch")
        entry["image_path"] = str(path.resolve())
    return entry, encoded


def _injection_row(
    source: dict[str, Any],
    entry: dict[str, Any],
    image_bytes: bytes,
    token_record: dict[str, Any],
    *,
    condition: str,
) -> dict[str, Any]:
    index = int(entry["local_index"])
    gold = str(entry["gold_label"])
    result = dict(source)
    result.update(
        {
            "catalog_unit_id": (
                f"VISSUP-01-{condition}-{index:04d}-"
                f"{entry['normalized_pixel_sha256'][:16]}"
            ),
            "image_bytes": image_bytes,
            "image_sha256": sha256_bytes(image_bytes),
            "phash_hex": "vissup01_not_computed",
            "row_rank_sha256": entry["order_key"],
            "representative_key_sha256": entry[
                "rotated_normalized_pixel_sha256"
            ],
            "canonical_conversation": token_record["canonical_conversation"],
            "full_token_ids": token_record["full_token_ids"],
            "lm_full_token_ids": token_record["lm_full_token_ids"],
            "assistant_target_start": token_record[
                "assistant_target_start"
            ],
            "assistant_target_end": token_record["assistant_target_end"],
            "lm_assistant_target_start": token_record[
                "lm_assistant_target_start"
            ],
            "lm_assistant_target_end": token_record[
                "lm_assistant_target_end"
            ],
            "target_token_ids": token_record["target_token_ids"],
            "target_token_count": token_record["target_token_count"],
            "assistant_eos_token_id": token_record[
                "assistant_eos_token_id"
            ],
            "sample_id": f"VISSUP-01-{condition}-{index:04d}",
            "split": "train",
            "draw_index": BASE_ROWS + index,
            "draw_retry_index": 0,
            "draw_sha256": sha256_bytes(
                canonical_json_bytes(
                    {
                        "condition": condition,
                        "index": index,
                        "pixel_sha256": entry[
                            "rotated_normalized_pixel_sha256"
                        ],
                        "gold": gold,
                    }
                )
            ),
        }
    )
    return result


def _write_train_parquet(
    path: Path,
    base_table: pa.Table,
    injection_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(injection_rows) != INJECTION_ROWS:
        raise ValueError("training injection cardinality mismatch")
    injection = pa.Table.from_pylist(injection_rows, schema=base_table.schema)
    combined = pa.concat_tables([base_table, injection])
    if combined.num_rows != TOTAL_TRAIN_ROWS:
        raise ValueError("combined training cardinality mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(combined, path, compression="zstd")
    check = pq.ParquetFile(path)
    if check.metadata.num_rows != TOTAL_TRAIN_ROWS:
        raise RuntimeError("written training parquet row count mismatch")
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "rows": check.metadata.num_rows,
    }


def _prepare_cvbench(
    table: pa.Table,
    *,
    base_pixel_hashes: set[str],
    tokenizer,
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if set(table.column_names) != REQUIRED_CV_COLUMNS:
        raise ValueError("PANEL_INELIGIBLE: CV-Bench schema differs")
    if table.num_rows != CVBENCH_ROWS:
        raise ValueError("PANEL_INELIGIBLE: CV-Bench row count differs")
    rows = sorted(table.to_pylist(), key=lambda row: int(row["idx"]))
    if [int(row["idx"]) for row in rows] != list(range(CVBENCH_ROWS)):
        raise ValueError("PANEL_INELIGIBLE: CV-Bench indices differ")
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    overlaps = []
    token_lengths = []
    for row in rows:
        index = int(row["idx"])
        if row["type"] != "2D":
            raise ValueError("PANEL_INELIGIBLE: non-2D row in 2D parquet")
        choices = list(row["choices"])
        labels = choice_labels(len(choices))
        gold = cvbench_gold_label(str(row["answer"]), len(choices))
        image_struct = row["image"]
        if not isinstance(image_struct, dict):
            raise ValueError("PANEL_INELIGIBLE: image field is not a struct")
        image_bytes = image_struct.get("bytes")
        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError("PANEL_INELIGIBLE: CV-Bench row lacks image bytes")
        image = normalized_rgb(image_bytes)
        pixel_sha = normalized_pixel_sha256(image)
        raw_sha = sha256_bytes(image_bytes)
        path = image_dir / f"{index:04d}.image"
        path.write_bytes(image_bytes)
        if sha256_file(path) != raw_sha:
            raise RuntimeError("written CV-Bench image hash mismatch")
        lengths = {}
        for label in labels:
            record = build_choice_record(
                tokenizer,
                str(row["prompt"]),
                label,
                legal_labels=labels,
            )
            lengths[label] = int(record["input_length_unpadded"])
            token_lengths.append(int(record["input_length_unpadded"]))
        item = {
            "idx": index,
            "task": str(row["task"]),
            "source": str(row["source"]),
            "source_dataset": str(row["source_dataset"]),
            "source_filename": str(row["source_filename"]),
            "question": str(row["question"]),
            "prompt": str(row["prompt"]),
            "choices": choices,
            "legal_labels": list(labels),
            "gold_label": gold,
            "image_path": str(path.resolve()),
            "image_sha256": raw_sha,
            "normalized_pixel_sha256": pixel_sha,
            "width": image.width,
            "height": image.height,
            "input_lengths_by_label": lengths,
        }
        if pixel_sha in base_pixel_hashes:
            overlaps.append(item)
        else:
            manifest_rows.append(item)
    group_counts = Counter(
        row["normalized_pixel_sha256"] for row in manifest_rows
    )
    minimum_groups = math.ceil(0.9 * CVBENCH_ROWS)
    checks = {
        "source_rows_1438": len(rows) == CVBENCH_ROWS,
        "all_rows_decode": len(rows) == len(manifest_rows) + len(overlaps),
        "choice_inventory_2_to_6": all(
            2 <= len(row["choices"]) <= 6 for row in rows
        ),
        "remaining_groups_at_least_90_percent": len(group_counts)
        >= minimum_groups,
        "all_token_sequences_fit_450": max(token_lengths)
        <= 450,
        "no_model_inference": True,
        "no_final_confirmation_access": True,
    }
    manifest = {
        "schema_version": 1,
        "manifest_id": "VISSUP-01-CVBench2D-variable-choice-v1",
        "source": {
            "repository": "nyu-visionx/CV-Bench",
            "revision": "bc284db50d036958861cb60cdd7b77612052ce0d",
            "config": "2D",
            "split": "test",
        },
        "rows": manifest_rows,
        "excluded_exact_pixel_overlaps": overlaps,
    }
    audit = {
        "schema_version": 1,
        "audit_id": "VISSUP-01-round2-CVBench2D-gate",
        "status": "passed" if all(checks.values()) else "panel_ineligible",
        "eligible_for_scoring": all(checks.values()),
        "source_rows": len(rows),
        "eligible_rows": len(manifest_rows),
        "excluded_exact_pixel_overlap_rows": len(overlaps),
        "independent_image_groups": len(group_counts),
        "minimum_required_image_groups": minimum_groups,
        "choice_count_inventory": dict(
            sorted(Counter(len(row["choices"]) for row in rows).items())
        ),
        "task_counts": dict(
            sorted(Counter(row["task"] for row in manifest_rows).items())
        ),
        "source_counts": dict(
            sorted(Counter(row["source"] for row in manifest_rows).items())
        ),
        "gold_label_counts": dict(
            sorted(Counter(row["gold_label"] for row in manifest_rows).items())
        ),
        "maximum_input_length_unpadded": max(token_lengths),
        "checks": checks,
        "model_inference_performed": False,
        "final_confirmation_accessed": False,
    }
    return manifest, audit


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"preparation output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if sha256_file(args.base_parquet) != BASE_SHA256:
        raise ValueError("base parquet SHA-256 mismatch")
    if args.cvbench_parquet.stat().st_size != CVBENCH_BYTES:
        raise ValueError("CV-Bench parquet byte size mismatch")
    if sha256_file(args.cvbench_parquet) != CVBENCH_SHA256:
        raise ValueError("CV-Bench parquet SHA-256 mismatch")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"),
        local_files_only=True,
    )
    base_table = pq.read_table(args.base_parquet)
    if base_table.num_rows != BASE_ROWS:
        raise ValueError("base parquet row count mismatch")
    base_rows = base_table.to_pylist()
    ordered, base_audit = _base_pixel_inventory(base_rows)
    train_inventory = ordered[:INJECTION_ROWS]
    heldout_inventory = ordered[
        INJECTION_ROWS : INJECTION_ROWS + HELDOUT_ROTATION_ROWS
    ]
    if {
        row["normalized_pixel_sha256"] for row in train_inventory
    } & {
        row["normalized_pixel_sha256"] for row in heldout_inventory
    }:
        raise RuntimeError("rotation training and held-out sets overlap")

    visual_rows = []
    revealed_rows = []
    train_entries = []
    for index, inventory_row in enumerate(train_inventory):
        source = base_rows[int(inventory_row["base_row_index"])]
        entry, image_bytes = _rotation_entry(
            source,
            inventory_row,
            split="rotation_train",
            local_index=index,
            image_dir=None,
        )
        visual_record, revealed_record = rotation_token_records(
            tokenizer, entry["gold_label"]
        )
        visual_rows.append(
            _injection_row(
                source,
                entry,
                image_bytes,
                visual_record,
                condition="visual-necessary",
            )
        )
        revealed_rows.append(
            _injection_row(
                source,
                entry,
                image_bytes,
                revealed_record,
                condition="label-revealed",
            )
        )
        train_entries.append(entry)

    heldout_entries = []
    for index, inventory_row in enumerate(heldout_inventory):
        source = base_rows[int(inventory_row["base_row_index"])]
        entry, _ = _rotation_entry(
            source,
            inventory_row,
            split="rotation_heldout",
            local_index=index,
            image_dir=output / "heldout_rotation/images",
        )
        heldout_entries.append(entry)

    visual_data = _write_train_parquet(
        output / "train_visual_necessary.parquet",
        base_table,
        visual_rows,
    )
    revealed_data = _write_train_parquet(
        output / "train_label_revealed.parquet",
        base_table,
        revealed_rows,
    )
    for left, right in zip(visual_rows, revealed_rows, strict=True):
        invariant_fields = (
            "image_bytes",
            "image_sha256",
            "target_token_ids",
            "target_token_count",
            "assistant_eos_token_id",
            "draw_index",
        )
        if any(left[field] != right[field] for field in invariant_fields):
            raise RuntimeError("paired training injection invariant failed")
        if len(left["full_token_ids"]) != len(right["full_token_ids"]):
            raise RuntimeError("paired training sequence lengths differ")

    rotation_manifest = {
        "schema_version": 1,
        "manifest_id": "VISSUP-01-heldout-rotation-v1",
        "rows": heldout_entries,
    }
    cv_table = pq.read_table(args.cvbench_parquet)
    cv_manifest, cv_audit = _prepare_cvbench(
        cv_table,
        base_pixel_hashes={
            row["normalized_pixel_sha256"] for row in ordered
        },
        tokenizer=tokenizer,
        output_dir=output / "cvbench",
    )
    if not cv_audit["eligible_for_scoring"]:
        raise ValueError("PANEL_INELIGIBLE: CV-Bench round2 gate failed")

    label_counts = Counter(row["gold_label"] for row in train_entries)
    heldout_label_counts = Counter(
        row["gold_label"] for row in heldout_entries
    )
    checks = {
        "base_rows_10000": len(base_rows) == BASE_ROWS,
        "unique_pixels_at_least_2016": base_audit[
            "unique_normalized_pixel_count"
        ]
        >= INJECTION_ROWS + HELDOUT_ROTATION_ROWS,
        "training_injection_rows_1008": len(train_entries)
        == INJECTION_ROWS,
        "heldout_rotation_rows_1008": len(heldout_entries)
        == HELDOUT_ROTATION_ROWS,
        "balanced_training_labels": set(label_counts.values()) == {252},
        "balanced_heldout_labels": set(heldout_label_counts.values()) == {252},
        "rotation_sets_disjoint": not (
            {
                row["normalized_pixel_sha256"] for row in train_entries
            }
            & {
                row["normalized_pixel_sha256"] for row in heldout_entries
            }
        ),
        "two_training_files_11008": (
            visual_data["rows"] == TOTAL_TRAIN_ROWS
            and revealed_data["rows"] == TOTAL_TRAIN_ROWS
        ),
        "cvbench_gate_passed": cv_audit["eligible_for_scoring"],
        "no_model_inference": True,
        "no_final_confirmation_access": True,
    }
    audit = {
        "schema_version": 1,
        "audit_id": "VISSUP-01-round2-data-and-panel-gate",
        "status": "passed" if all(checks.values()) else "ineligible",
        "eligible_for_training": all(checks.values()),
        "base": {
            "path": str(args.base_parquet.resolve()),
            "sha256": sha256_file(args.base_parquet),
            **base_audit,
        },
        "data": {
            "visual-necessary": visual_data,
            "label-revealed": revealed_data,
            "training_label_counts": dict(sorted(label_counts.items())),
            "heldout_label_counts": dict(
                sorted(heldout_label_counts.items())
            ),
        },
        "cvbench": cv_audit,
        "checks": checks,
        "model_inference_performed": False,
        "training_runs_started": 0,
        "final_confirmation_accessed": False,
    }
    write_json(output / "train_injection_manifest.json", {
        "schema_version": 1,
        "manifest_id": "VISSUP-01-training-injection-v1",
        "rows": train_entries,
    })
    write_json(output / "heldout_rotation_manifest.json", rotation_manifest)
    write_json(output / "cvbench_manifest.json", cv_manifest)
    write_json(output / "cvbench_audit.json", cv_audit)
    write_json(output / "data_audit.json", audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    if not audit["eligible_for_training"]:
        raise RuntimeError("VISSUP-01 preparation gate did not pass")
    return audit


def main() -> None:
    prepare(parse_args())


if __name__ == "__main__":
    main()
