#!/usr/bin/env python3
"""Verify every frozen Phase 3 v5 dataset and image resource binding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.artifact_validation import validate_overlap_receipt, validate_prepared_data
from experiments.phase3.canonical_io import (
    atomic_write_json, load_json_snapshot, load_jsonl_snapshot, sha256_bytes,
    snapshot_file, write_sha256_sidecar,
)
from experiments.phase3.phase3_protocol_v5 import Phase3ProtocolV5


def audit_resources_v5(
    *, protocol_path: Path, prepared_data_dir: Path, overlap_receipt_path: Path,
    coco_root: Path, hf_cache_dir: Path,
) -> dict[str, Any]:
    from huggingface_hub import hf_hub_download

    protocol = Phase3ProtocolV5.load(protocol_path)
    prepared = validate_prepared_data(prepared_data_dir)
    if (
        prepared["data_manifest_sha256"] != protocol.payload["data_manifest_sha256"]
        or prepared["split_manifest_sha256"] != protocol.payload["split_manifest_sha256"]
        or len(prepared["pilot_names"]) != 153
        or len(prepared["formal_names"]) != 1389
    ):
        raise ValueError("prepared data binding/count mismatch")
    canonical = load_jsonl_snapshot(prepared_data_dir / "sugarcrepe_pp_canonical.jsonl", root=prepared_data_dir)
    if len(canonical) != 4757 or len({row["filename"] for row in canonical}) != 1542:
        raise ValueError("canonical SugarCrepe++ row/image count mismatch")
    source_receipts = []
    dataset = protocol.payload["dataset"]
    for expected in dataset["source_files"]:
        downloaded = Path(
            hf_hub_download(
                repo_id=dataset["repo"], repo_type="dataset", revision=dataset["revision"],
                filename=expected["repository_relative_path"], cache_dir=hf_cache_dir,
            )
        )
        # Snapshot entries are normally symlinks into Hugging Face's
        # content-addressed cache. Resolve only that cache-internal link and
        # then take a race-resistant regular-file snapshot.
        resolved_download = downloaded.resolve(strict=True)
        raw = snapshot_file(resolved_download, root=hf_cache_dir.resolve(strict=True))
        value = json.loads(raw.decode("utf-8"))
        if (
            len(raw) != expected["size_bytes"] or sha256_bytes(raw) != expected["sha256"]
            or not isinstance(value, (list, dict)) or len(value) != expected["row_count"]
        ):
            raise ValueError(f"upstream SugarCrepe++ source mismatch: {expected['config']}")
        source_receipts.append({
            "config": expected["config"], "repository_relative_path": expected["repository_relative_path"],
            "row_count": len(value), "size_bytes": len(raw), "sha256": sha256_bytes(raw), "status": "verified",
        })
    overlap = validate_overlap_receipt(
        overlap_receipt_path,
        split_manifest_path=prepared_data_dir / "split_manifest.json",
        formal_image_manifest_path=prepared_data_dir / "coco_formal_images_manifest.jsonl",
    )
    certifying = overlap["certifying_names"]
    excluded_rows = load_jsonl_snapshot(overlap_receipt_path.parent / "excluded_formal_images.jsonl", root=overlap_receipt_path.parent)
    excluded = [row["filename"] for row in excluded_rows]
    if (
        len(excluded) != 44 or len(set(excluded)) != 44 or len(certifying) != 1345
        or set(certifying) != set(prepared["formal_names"]) - set(excluded)
        or sha256_bytes(snapshot_file(overlap_receipt_path)) != protocol.payload["overlap_audit_receipt_sha256"]
        or sha256_bytes(snapshot_file(overlap_receipt_path.parent / "excluded_formal_images.jsonl"))
        != protocol.payload["excluded_formal_images_sha256"]
        or sha256_bytes(snapshot_file(overlap_receipt_path.parent / "certifying_formal_filenames.txt"))
        != protocol.payload["certifying_formal_filenames_sha256"]
    ):
        raise ValueError("44-image overlap exclusion/certifying partition mismatch")
    referenced = load_jsonl_snapshot(prepared_data_dir / "coco_referenced_images_manifest.jsonl", root=prepared_data_dir)
    if len(referenced) != 1542:
        raise ValueError("COCO referenced-image manifest count mismatch")
    for row in referenced:
        if row.get("status") != "ready":
            raise ValueError(f"COCO image is not ready: {row.get('filename')}")
        raw = snapshot_file(coco_root / row["filename"], root=coco_root)
        if len(raw) != row["size_bytes"] or sha256_bytes(raw) != row["sha256"]:
            raise ValueError(f"COCO image bytes differ from frozen manifest: {row['filename']}")
    return {
        "schema_version": 1, "audit_type": "phase3_v5_frozen_resources",
        "overall_status": "verified", "row_count": 4757, "unique_image_count": 1542,
        "pilot_unique_images": 153, "formal_unique_images": 1389,
        "excluded_formal_unique_images": 44, "certifying_formal_unique_images": 1345,
        "source_files": source_receipts, "verified_coco_images": 1542,
        "data_manifest_sha256": prepared["data_manifest_sha256"],
        "split_manifest_sha256": prepared["split_manifest_sha256"],
        "overlap_audit_receipt_sha256": sha256_bytes(snapshot_file(overlap_receipt_path)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--prepared-data-dir", type=Path, required=True)
    parser.add_argument("--overlap-audit-receipt", type=Path, required=True)
    parser.add_argument("--coco-root", type=Path, required=True)
    parser.add_argument("--hf-cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists() or args.output.with_suffix(".sha256").exists():
        raise FileExistsError(args.output)
    result = audit_resources_v5(
        protocol_path=args.protocol, prepared_data_dir=args.prepared_data_dir,
        overlap_receipt_path=args.overlap_audit_receipt, coco_root=args.coco_root,
        hf_cache_dir=args.hf_cache_dir,
    )
    atomic_write_json(args.output, result, overwrite=False)
    write_sha256_sidecar(args.output, overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
