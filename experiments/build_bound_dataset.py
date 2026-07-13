#!/usr/bin/env python3
"""Build deterministic one-caption-per-image splits for bound experiments."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


@dataclass(frozen=True)
class RepresentativeRow:
    """The deterministically selected source row for one unique image."""

    row_index: int
    conversation_digest: bytes


@dataclass(frozen=True)
class DatasetSplit:
    """Sorted global row indices for two image-disjoint splits."""

    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--train-size",
        type=int,
        default=10_000,
        help="Number of independent training images, not parquet rows.",
    )
    parser.add_argument(
        "--validation-size",
        type=int,
        default=2_000,
        help="Number of independent validation images.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def validate_source(parquet: pq.ParquetFile) -> None:
    required = {"image_bytes", "conversations"}
    available = set(parquet.schema_arrow.names)
    missing = required - available
    if missing:
        raise ValueError(f"source parquet is missing columns: {sorted(missing)}")


def digest_bytes(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def index_representative_rows(
    parquet: pq.ParquetFile,
) -> dict[bytes, RepresentativeRow]:
    """Index one stable representative row for every distinct image."""
    representatives: dict[bytes, RepresentativeRow] = {}
    row_group_start = 0

    for row_group in range(parquet.num_row_groups):
        table = parquet.read_row_group(
            row_group, columns=["image_bytes", "conversations"]
        )
        images = table["image_bytes"].to_pylist()
        conversations = table["conversations"].to_pylist()

        for local_index, (image, conversation) in enumerate(
            zip(images, conversations, strict=True)
        ):
            image_digest = digest_bytes(image)
            candidate = RepresentativeRow(
                row_index=row_group_start + local_index,
                conversation_digest=digest_bytes(conversation.encode("utf-8")),
            )
            current = representatives.get(image_digest)
            if current is None or (
                candidate.conversation_digest,
                candidate.row_index,
            ) < (current.conversation_digest, current.row_index):
                representatives[image_digest] = candidate

        row_group_start += table.num_rows
        print(
            f"Indexed unique images: {row_group + 1}/{parquet.num_row_groups}",
            end="\r",
            flush=True,
        )

    print()
    return representatives


def split_rank(image_digest: bytes, seed: int) -> bytes:
    """Return a reproducible pseudo-random rank for one image."""
    payload = b"bound-split-v1\0" + str(seed).encode("ascii") + b"\0"
    return digest_bytes(payload + image_digest)


def select_split_rows(
    representatives: dict[bytes, RepresentativeRow],
    train_size: int,
    validation_size: int,
    seed: int,
) -> DatasetSplit:
    """Select fixed validation images followed by nested training images."""
    if train_size <= 0 or validation_size <= 0:
        raise ValueError("train-size and validation-size must be positive")

    requested = train_size + validation_size
    if requested > len(representatives):
        raise ValueError(
            f"requested {requested:,} unique images, but source has "
            f"only {len(representatives):,}"
        )

    ranked_images = sorted(
        representatives,
        key=lambda image_digest: (split_rank(image_digest, seed), image_digest),
    )
    validation_images = ranked_images[:validation_size]
    train_images = ranked_images[validation_size:requested]

    validation_indices = tuple(
        sorted(representatives[digest].row_index for digest in validation_images)
    )
    train_indices = tuple(
        sorted(representatives[digest].row_index for digest in train_images)
    )
    if set(train_indices) & set(validation_indices):
        raise AssertionError("train and validation row indices overlap")

    return DatasetSplit(
        train_indices=train_indices,
        validation_indices=validation_indices,
    )


def read_selected_rows(
    parquet: pq.ParquetFile, indices: tuple[int, ...]
) -> pa.Table:
    """Read sorted global row indices without loading the full parquet table."""
    selected = np.asarray(indices, dtype=np.int64)
    if selected.size == 0:
        return pa.Table.from_batches([], schema=parquet.schema_arrow)
    if selected[0] < 0 or selected[-1] >= parquet.metadata.num_rows:
        raise IndexError("selected row index is outside the source parquet")
    if np.any(selected[1:] <= selected[:-1]):
        raise ValueError("selected row indices must be strictly increasing")

    tables = []
    row_group_start = 0
    for row_group in range(parquet.num_row_groups):
        row_count = parquet.metadata.row_group(row_group).num_rows
        row_group_end = row_group_start + row_count
        left = np.searchsorted(selected, row_group_start, side="left")
        right = np.searchsorted(selected, row_group_end, side="left")

        if left < right:
            table = parquet.read_row_group(row_group)
            local_indices = selected[left:right] - row_group_start
            tables.append(table.take(pa.array(local_indices, type=pa.int64())))
        row_group_start = row_group_end

    return pa.concat_tables(tables, promote_options="permissive")


def prepare_output_paths(output_dir: Path, overwrite: bool) -> dict[str, Path]:
    paths = {
        "train": output_dir / "train.parquet",
        "validation": output_dir / "validation.parquet",
        "manifest": output_dir / "split_manifest.json",
    }
    existing = [path for path in paths.values() if path.exists()]
    if existing and not overwrite:
        rendered = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"outputs already exist: {rendered}; pass --overwrite")
    output_dir.mkdir(parents=True, exist_ok=True)
    return paths


def append_image_hash(table: pa.Table) -> pa.Table:
    digests = [digest_bytes(image).hex() for image in table["image_bytes"].to_pylist()]
    if len(digests) != len(set(digests)):
        raise AssertionError("an output split contains duplicate images")
    return table.append_column("image_sha256", pa.array(digests, type=pa.string()))


def write_parquet_atomic(table: pa.Table, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(
        table,
        temporary,
        compression="zstd",
        use_dictionary=True,
        row_group_size=1024,
    )
    temporary.replace(path)


def write_json_atomic(payload: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def main() -> None:
    args = parse_args()
    parquet = pq.ParquetFile(args.input)
    validate_source(parquet)
    paths = prepare_output_paths(args.output_dir, args.overwrite)

    representatives = index_representative_rows(parquet)
    split = select_split_rows(
        representatives,
        train_size=args.train_size,
        validation_size=args.validation_size,
        seed=args.seed,
    )
    train_table = append_image_hash(read_selected_rows(parquet, split.train_indices))
    validation_table = append_image_hash(
        read_selected_rows(parquet, split.validation_indices)
    )

    train_hashes = set(train_table["image_sha256"].to_pylist())
    validation_hashes = set(validation_table["image_sha256"].to_pylist())
    overlap = train_hashes & validation_hashes
    if overlap:
        raise AssertionError(f"train/validation image overlap: {len(overlap)}")

    write_parquet_atomic(train_table, paths["train"])
    write_parquet_atomic(validation_table, paths["validation"])
    manifest = {
        "source": str(args.input.resolve()),
        "source_rows": parquet.metadata.num_rows,
        "source_unique_images": len(representatives),
        "train_rows": train_table.num_rows,
        "train_unique_images": len(train_hashes),
        "validation_rows": validation_table.num_rows,
        "validation_unique_images": len(validation_hashes),
        "image_overlap": len(overlap),
        "seed": args.seed,
        "image_identity": "sha256(image_bytes)",
        "representative": "minimum_sha256(conversations)",
        "selection": "seeded_sha256_rank_validation_then_train",
    }
    write_json_atomic(manifest, paths["manifest"])
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
