#!/usr/bin/env python3
"""Independently verify frozen Stage 2 confirmation membership and leakage rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import imagehash
import pyarrow.parquet as pq
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import build_token_record, normalized_image
from experiments.build_stage2_dataset import HammingBKTree, source_image_bytes
from experiments.stage2_protocol import DEFAULT_FROZEN, Stage2Protocol, sha256_file, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--split-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"verification output already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    data = protocol.payload["data"]
    manifest_path = args.split_dir / "split_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["protocol"] != protocol.reference():
        raise ValueError("split manifest does not reference the frozen protocol")
    tokenizer = AutoTokenizer.from_pretrained(protocol.asset_path("tokenizer"), local_files_only=True)
    history = protocol.payload["history_exclusion"]
    history_exact = {
        line.strip() for line in (REPO_ROOT / history["exact_sha256_path"]).read_text().splitlines()
        if line.strip()
    }
    history_phashes = [
        int(line.split()[1], 16)
        for line in (REPO_ROOT / history["phash_path"]).read_text().splitlines()
        if line.strip()
    ]
    forbidden = HammingBKTree(history_phashes)
    exact_seen = set()
    rows = []
    expected_counts = {"validation": data["validation_images"], "train": data["train_images"]}
    for split in ("validation", "train"):
        path = args.split_dir / f"{split}.parquet"
        table = pq.read_table(path)
        if table.num_rows != expected_counts[split]:
            raise ValueError(f"{split} row count differs from frozen protocol")
        if sha256_file(path) != manifest["outputs"][split]["sha256"]:
            raise ValueError(f"{split} parquet hash differs from split manifest")
        for row in table.to_pylist():
            image_bytes = source_image_bytes(row["image_bytes"])
            exact = hashlib.sha256(image_bytes).hexdigest()
            if exact != row["image_sha256"] or exact in history_exact or exact in exact_seen:
                raise ValueError("exact-image leakage or membership mismatch")
            token_record = build_token_record(
                row["canonical_conversation"],
                tokenizer,
                image_token_count=protocol.payload["model"]["image_token_count"],
                max_length=protocol.payload["training"]["max_sequence_length"],
            )
            for key, value in token_record.items():
                if row[key] != value:
                    raise ValueError(f"frozen token field does not reproduce: {key}")
            phash_hex = str(imagehash.phash(
                normalized_image(image_bytes),
                hash_size=data["phash"]["hash_size"],
                highfreq_factor=data["phash"]["highfreq_factor"],
            ))
            phash_value = int(phash_hex, 16)
            if phash_hex != row["phash_hex"] or forbidden.has_within(
                phash_value, data["phash"]["maximum_allowed_hamming_distance"]
            ):
                raise ValueError("perceptual-image leakage or membership mismatch")
            forbidden.add(phash_value)
            exact_seen.add(exact)
            rows.append({
                "sample_id": row["sample_id"],
                "split": split,
                "image_sha256": exact,
                "phash_hex": phash_hex,
                "target_token_count": row["target_token_count"],
            })
    if len(rows) != sum(expected_counts.values()):
        raise RuntimeError("verification did not consume every confirmation image")
    canonical_membership = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows
    ).encode("utf-8")
    output = {
        "schema_version": 1,
        "status": "passed",
        "protocol": protocol.reference(),
        "split_manifest_sha256": sha256_file(manifest_path),
        "train_sha256": sha256_file(args.split_dir / "train.parquet"),
        "validation_sha256": sha256_file(args.split_dir / "validation.parquet"),
        "verified_images": len(rows),
        "history_exact_images": len(history_exact),
        "history_phash_rows": len(history_phashes),
        "minimum_required_phash_distance": data["phash"]["maximum_allowed_hamming_distance"] + 1,
        "canonical_membership_sha256": hashlib.sha256(canonical_membership).hexdigest(),
        "invariants": {
            "exact_unique_disjoint_and_absent_from_history": True,
            "phash_distance_greater_than_six_from_history_and_prior_selected": True,
            "token_records_reproduce": True,
            "target_eos_present": True,
            "no_target_truncation": True,
        },
    }
    write_json_atomic(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
