#!/usr/bin/env python3
"""Build deterministic one-caption-per-image splits for bound experiments."""

import argparse
import gzip
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.phase2_protocol import FrozenProtocol, sha256_file


SELECTION_PROTOCOL = "bound_split_seeded_sha256_rank_v2"


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
    parser.add_argument(
        "--exclude-parquet",
        action="append",
        type=Path,
        default=[],
        help="Prior split whose image identities must be excluded; repeat as needed.",
    )
    parser.add_argument("--protocol-path", type=Path)
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
    payload = SELECTION_PROTOCOL.encode() + b"\0" + str(seed).encode("ascii") + b"\0"
    return digest_bytes(payload + image_digest)


def select_split_rows(
    representatives: dict[bytes, RepresentativeRow],
    train_size: int,
    validation_size: int,
    seed: int,
    excluded_images: set[bytes] | None = None,
) -> DatasetSplit:
    """Select fixed validation images followed by nested training images."""
    if train_size <= 0 or validation_size <= 0:
        raise ValueError("train-size and validation-size must be positive")

    eligible = set(representatives) - (excluded_images or set())
    requested = train_size + validation_size
    if requested > len(eligible):
        raise ValueError(
            f"requested {requested:,} unique images, but source has "
            f"only {len(eligible):,} eligible images"
        )

    ranked_images = sorted(
        eligible,
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
        "train_membership": output_dir / "train_membership.jsonl.gz",
        "validation_membership": output_dir / "validation_membership.jsonl.gz",
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


def image_hashes_from_parquet(path: Path) -> set[bytes]:
    parquet = pq.ParquetFile(path)
    columns = ["image_bytes"]
    if "image_sha256" in parquet.schema_arrow.names:
        columns.append("image_sha256")
    table = pq.read_table(path, columns=columns)
    calculated = [digest_bytes(value) for value in table["image_bytes"].to_pylist()]
    if "image_sha256" in table.column_names:
        recorded = [bytes.fromhex(value) for value in table["image_sha256"].to_pylist()]
        if recorded != calculated:
            raise ValueError(f"stored image hashes do not match image bytes: {path}")
    return set(calculated)


def write_membership_atomic(table: pa.Table, indices: tuple[int, ...], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    hashes = table["image_sha256"].to_pylist()
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            for source_row, image_hash in zip(indices, hashes, strict=True):
                record = {"source_row": source_row, "image_sha256": image_hash}
                compressed.write(
                    (json.dumps(record, separators=(",", ":")) + "\n").encode()
                )
    temporary.replace(path)


def artifact_metadata(path: Path, rows: int, membership: Path) -> dict:
    return {
        "path": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "rows": rows,
        "membership": {
            "path": membership.name,
            "bytes": membership.stat().st_size,
            "sha256": sha256_file(membership),
        },
    }


def main() -> None:
    args = parse_args()
    protocol = FrozenProtocol.load(args.protocol_path) if args.protocol_path else None
    if protocol and args.overwrite:
        raise ValueError("frozen Phase 2 outputs cannot be overwritten")
    source_sha256 = sha256_file(args.input)
    if protocol:
        protocol.verify_files(REPO_ROOT, "implementation_files")
        protocol.verify_environment(REPO_ROOT)
        protocol.require(
            "dataset",
            {
                "source_sha256": source_sha256,
                "train_size": args.train_size,
                "validation_size": args.validation_size,
                "seed": args.seed,
                "selection": SELECTION_PROTOCOL,
            },
            ("source_sha256", "train_size", "validation_size", "seed", "selection"),
        )
    parquet = pq.ParquetFile(args.input)
    validate_source(parquet)
    paths = prepare_output_paths(args.output_dir, args.overwrite)

    exclusions = [
        {
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
            "image_count": len(image_hashes_from_parquet(path)),
        }
        for path in args.exclude_parquet
    ]
    if protocol and [item["sha256"] for item in exclusions] != protocol.payload[
        "dataset"
    ]["exclude_sha256"]:
        raise ValueError("excluded datasets do not match the frozen protocol")
    excluded_images = set().union(
        *(image_hashes_from_parquet(path) for path in args.exclude_parquet)
    )
    if protocol and len(excluded_images) != protocol.payload["dataset"][
        "excluded_unique_images"
    ]:
        raise ValueError("excluded image union does not match the frozen protocol")

    representatives = index_representative_rows(parquet)
    split = select_split_rows(
        representatives,
        train_size=args.train_size,
        validation_size=args.validation_size,
        seed=args.seed,
        excluded_images=excluded_images,
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
    write_membership_atomic(
        train_table, split.train_indices, paths["train_membership"]
    )
    write_membership_atomic(
        validation_table,
        split.validation_indices,
        paths["validation_membership"],
    )
    manifest = {
        "schema_version": 2,
        "protocol_id": protocol.payload["protocol_id"] if protocol else None,
        "protocol_sha256": protocol.sha256 if protocol else None,
        "source": str(args.input.resolve()),
        "source_bytes": args.input.stat().st_size,
        "source_sha256": source_sha256,
        "source_rows": parquet.metadata.num_rows,
        "source_unique_images": len(representatives),
        "excluded_unique_images": len(excluded_images),
        "all_phase1_selection_images_excluded": bool(protocol),
        "exclusions": exclusions,
        "outputs": {
            "train": artifact_metadata(
                paths["train"], train_table.num_rows, paths["train_membership"]
            ),
            "validation": artifact_metadata(
                paths["validation"],
                validation_table.num_rows,
                paths["validation_membership"],
            ),
        },
        "image_overlap": len(overlap),
        "seed": args.seed,
        "image_identity": "sha256(image_bytes)",
        "representative": "minimum_sha256(conversations)",
        "selection": SELECTION_PROTOCOL,
    }
    write_json_atomic(manifest, paths["manifest"])
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
