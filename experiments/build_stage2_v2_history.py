#!/usr/bin/env python3
"""Extend the immutable history-exclusion set with all exposed Stage 2 v1 images."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import sha256_file, write_json_atomic  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-exact",
        type=Path,
        default=REPO_ROOT / "experiments/stage2_history_exact_sha256.txt",
    )
    parser.add_argument(
        "--base-phash",
        type=Path,
        default=REPO_ROOT / "experiments/stage2_history_phash.txt",
    )
    parser.add_argument(
        "--base-manifest",
        type=Path,
        default=REPO_ROOT / "experiments/stage2_history_exclusion_manifest.json",
    )
    parser.add_argument(
        "--v1-train-membership",
        type=Path,
        default=REPO_ROOT / "dataset/stage2_confirm_seed2026/train_membership.jsonl",
    )
    parser.add_argument(
        "--v1-validation-membership",
        type=Path,
        default=REPO_ROOT / "dataset/stage2_confirm_seed2026/validation_membership.jsonl",
    )
    parser.add_argument(
        "--v1-audit-summary",
        type=Path,
        default=REPO_ROOT / "experiments/audits/stage2_v1/audit_summary.json",
    )
    parser.add_argument("--output-prefix", type=Path, required=True)
    return parser.parse_args()


def membership_rows(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    required = {"sample_id", "image_sha256", "phash_hex"}
    if any(not required.issubset(row) for row in rows):
        raise ValueError(f"membership rows are incomplete: {path}")
    return rows


def write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    args = parse_args()
    args.output_prefix = args.output_prefix.resolve()
    outputs = {
        "exact": args.output_prefix.with_name(args.output_prefix.name + "_exact_sha256.txt"),
        "phash": args.output_prefix.with_name(args.output_prefix.name + "_phash.txt"),
        "sources": args.output_prefix.with_name(args.output_prefix.name + "_sources.json"),
        "receipt": args.output_prefix.with_name(args.output_prefix.name + "_merge_receipt.json"),
        "manifest": args.output_prefix.with_name(args.output_prefix.name + "_manifest.json"),
    }
    if any(path.exists() for path in outputs.values()):
        raise FileExistsError("one or more Stage 2 v2 history outputs already exist")

    base_exact = {
        line.strip()
        for line in args.base_exact.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    base_phash = {}
    for line in args.base_phash.read_text(encoding="utf-8").splitlines():
        if line.strip():
            image_sha256, phash_hex = line.split()
            previous = base_phash.setdefault(image_sha256, phash_hex)
            if previous != phash_hex:
                raise ValueError("base history maps one exact image to multiple pHashes")
    v1_train = membership_rows(args.v1_train_membership)
    v1_validation = membership_rows(args.v1_validation_membership)
    v1_rows = v1_train + v1_validation
    if len(v1_train) != 10000 or len(v1_validation) != 2000:
        raise ValueError("Stage 2 v1 membership sizes are not 10000/2000")
    v1_exact = {row["image_sha256"] for row in v1_rows}
    if len(v1_exact) != len(v1_rows):
        raise ValueError("Stage 2 v1 membership is not exact-image unique")
    overlap = sorted(base_exact & v1_exact)
    if overlap:
        raise ValueError("Stage 2 v1 confirmation images overlap the prior exact history")

    merged_exact = base_exact | v1_exact
    merged_phash = dict(base_phash)
    for row in v1_rows:
        previous = merged_phash.setdefault(row["image_sha256"], row["phash_hex"])
        if previous != row["phash_hex"]:
            raise ValueError("merged history maps one exact image to multiple pHashes")
    if set(merged_phash) != merged_exact:
        raise ValueError("every exact history image must have one pHash row")

    write_text_atomic(outputs["exact"], "".join(f"{value}\n" for value in sorted(merged_exact)))
    write_text_atomic(
        outputs["phash"],
        "".join(f"{image_sha} {merged_phash[image_sha]}\n" for image_sha in sorted(merged_phash)),
    )
    sources = {
        "schema_version": 1,
        "protocol": "stage2_v2_history_sources_v1",
        "phash": {
            "library": "ImageHash",
            "version": "4.3.2",
            "hash_size": 8,
            "highfreq_factor": 4,
            "preprocess": "Pillow ImageOps.exif_transpose then RGB",
        },
        "sources": [
            {
                "role": "pre_stage2_v1_history",
                "manifest_path": str(args.base_manifest.resolve()),
                "manifest_sha256": sha256_file(args.base_manifest),
                "exact_path": str(args.base_exact.resolve()),
                "exact_sha256": sha256_file(args.base_exact),
                "phash_path": str(args.base_phash.resolve()),
                "phash_sha256": sha256_file(args.base_phash),
                "images": len(base_exact),
            },
            {
                "role": "stage2_v1_confirmation_train",
                "membership_path": str(args.v1_train_membership.resolve()),
                "membership_sha256": sha256_file(args.v1_train_membership),
                "images": len(v1_train),
            },
            {
                "role": "stage2_v1_confirmation_validation",
                "membership_path": str(args.v1_validation_membership.resolve()),
                "membership_sha256": sha256_file(args.v1_validation_membership),
                "images": len(v1_validation),
            },
            {
                "role": "stage2_v1_closeout_audit",
                "path": str(args.v1_audit_summary.resolve()),
                "sha256": sha256_file(args.v1_audit_summary),
            },
        ],
        "base_exact_images": len(base_exact),
        "stage2_v1_images": len(v1_exact),
        "merged_exact_images": len(merged_exact),
        "merged_unique_phashes": len(set(merged_phash.values())),
    }
    write_json_atomic(outputs["sources"], sources)
    receipt = {
        "schema_version": 1,
        "receipt_id": "minimind-v-stage2-v2-history-merge-v1",
        "status": "passed",
        "rules": [
            "include every exact image and pHash from the frozen pre-v1 history",
            "include all 10000 train and 2000 validation images exposed by Stage 2 v1",
            "do not remove or replace any prior history item",
            "require exactly one pHash row for every exact image",
        ],
        "counts": {
            "base_exact_images": len(base_exact),
            "stage2_v1_images": len(v1_exact),
            "base_v1_exact_overlap": len(overlap),
            "merged_exact_images": len(merged_exact),
            "merged_phash_rows": len(merged_phash),
            "merged_unique_phashes": len(set(merged_phash.values())),
        },
        "outputs": {
            "exact_sha256": sha256_file(outputs["exact"]),
            "phash_sha256": sha256_file(outputs["phash"]),
            "sources_sha256": sha256_file(outputs["sources"]),
        },
    }
    write_json_atomic(outputs["receipt"], receipt)
    artifacts = [
        {
            "path": str(path.relative_to(REPO_ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for name, path in outputs.items()
        if name != "manifest"
    ]
    manifest = {
        "schema_version": 1,
        "protocol": "stage2_v2_history_exclusion_manifest_v1",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    write_json_atomic(outputs["manifest"], manifest)
    print(json.dumps({"status": "passed", "outputs": outputs, "counts": receipt["counts"]}, default=str, indent=2))


if __name__ == "__main__":
    main()
