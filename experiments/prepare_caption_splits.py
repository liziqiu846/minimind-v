#!/usr/bin/env python3
"""Create deterministic train/validation subsets from a MiniMind-V parquet file."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source parquet file")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for split parquet files")
    parser.add_argument("--train-size", type=int, default=10_000)
    parser.add_argument("--val-size", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def take_rows(table, sorted_global_indices, row_group_start):
    left = np.searchsorted(sorted_global_indices, row_group_start, side="left")
    right = np.searchsorted(
        sorted_global_indices, row_group_start + table.num_rows, side="left"
    )
    if left == right:
        return None
    local_indices = sorted_global_indices[left:right] - row_group_start
    return table.take(pa.array(local_indices, type=pa.int64()))


def concatenate(tables, schema):
    if not tables:
        return pa.Table.from_batches([], schema=schema)
    return pa.concat_tables(tables, promote_options="permissive")


def image_digest(image_value):
    """Hash one image or an ordered list of images without ambiguous concatenation."""
    images = image_value if isinstance(image_value, list) else [image_value]
    digest = hashlib.sha256()
    for image in images:
        digest.update(len(image).to_bytes(8, byteorder="big"))
        digest.update(image)
    return digest.digest()


def select_image_disjoint_indices(parquet, train_size, val_size, seed):
    image_groups = defaultdict(list)
    row_group_start = 0
    for row_group in range(parquet.num_row_groups):
        image_table = parquet.read_row_group(row_group, columns=["image_bytes"])
        for local_index, image_scalar in enumerate(image_table["image_bytes"]):
            image_groups[image_digest(image_scalar.as_py())].append(
                row_group_start + local_index
            )
        row_group_start += image_table.num_rows
        print(
            f"Indexed image groups: row group {row_group + 1}/{parquet.num_row_groups}",
            end="\r",
            flush=True,
        )
    print()

    rng = np.random.default_rng(seed)
    group_keys = list(image_groups)
    rng.shuffle(group_keys)
    validation_indices = []
    train_indices = []
    validation_groups = 0
    train_groups = 0
    for key in group_keys:
        rows = image_groups[key]
        if len(validation_indices) < val_size:
            validation_indices.extend(rows)
            validation_groups += 1
        elif len(train_indices) < train_size:
            train_indices.extend(rows)
            train_groups += 1
        else:
            break

    if len(train_indices) < train_size or len(validation_indices) < val_size:
        raise ValueError("source does not contain enough image-disjoint groups")
    return (
        np.sort(np.asarray(train_indices, dtype=np.int64)),
        np.sort(np.asarray(validation_indices, dtype=np.int64)),
        len(image_groups),
        train_groups,
        validation_groups,
    )


def main():
    args = parse_args()
    if args.train_size <= 0 or args.val_size <= 0:
        raise ValueError("train-size and val-size must both be positive")

    parquet = pq.ParquetFile(args.input)
    total_rows = parquet.metadata.num_rows
    requested_rows = args.train_size + args.val_size
    if requested_rows > total_rows:
        raise ValueError(
            f"requested {requested_rows:,} rows, but source contains {total_rows:,}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.parquet"
    val_path = args.output_dir / "validation.parquet"
    manifest_path = args.output_dir / "split_manifest.json"
    outputs = (train_path, val_path, manifest_path)
    if not args.overwrite and any(path.exists() for path in outputs):
        existing = ", ".join(str(path) for path in outputs if path.exists())
        raise FileExistsError(f"output already exists: {existing}; pass --overwrite")

    (
        train_indices,
        val_indices,
        source_unique_images,
        train_unique_images,
        validation_unique_images,
    ) = select_image_disjoint_indices(
        parquet, args.train_size, args.val_size, args.seed
    )

    train_tables = []
    val_tables = []
    row_group_start = 0
    for row_group in range(parquet.num_row_groups):
        row_count = parquet.metadata.row_group(row_group).num_rows
        row_group_end = row_group_start + row_count
        train_hit = np.searchsorted(train_indices, row_group_end, side="left") > np.searchsorted(
            train_indices, row_group_start, side="left"
        )
        val_hit = np.searchsorted(val_indices, row_group_end, side="left") > np.searchsorted(
            val_indices, row_group_start, side="left"
        )
        if train_hit or val_hit:
            table = parquet.read_row_group(row_group)
            if train_hit:
                train_tables.append(take_rows(table, train_indices, row_group_start))
            if val_hit:
                val_tables.append(take_rows(table, val_indices, row_group_start))
        row_group_start = row_group_end

    train_table = concatenate(train_tables, parquet.schema_arrow)
    val_table = concatenate(val_tables, parquet.schema_arrow)
    pq.write_table(
        train_table, train_path, compression="zstd", use_dictionary=True, row_group_size=1024
    )
    pq.write_table(
        val_table, val_path, compression="zstd", use_dictionary=True, row_group_size=1024
    )

    manifest = {
        "source": str(args.input.resolve()),
        "source_rows": total_rows,
        "source_unique_images": source_unique_images,
        "train_rows": train_table.num_rows,
        "train_unique_images": train_unique_images,
        "validation_rows": val_table.num_rows,
        "validation_unique_images": validation_unique_images,
        "image_overlap": 0,
        "seed": args.seed,
        "selection": "uniform_image_group_without_replacement",
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
