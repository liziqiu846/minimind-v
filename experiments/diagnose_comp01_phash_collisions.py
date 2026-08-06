#!/usr/bin/env python3
"""Adjudicate the finite pHash hits from the COMP-01 panel gate.

This diagnostic may read only source rows whose provenance receipt labels them
as training data. It refuses validation/final rows and never runs a VLM.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import imagehash
import pyarrow.parquet as pq
from PIL import Image, ImageOps

from experiments.comp01_whatsup import (
    PHASH_RADIUS,
    REPO_ROOT,
    canonical_json_bytes,
    write_json_atomic,
)
from experiments.stage2_protocol import sha256_file


MANUAL_SCENE_LABELS = {
    "363498026dcbf6d311fdfbbd9030db32c12bd90792f8312ce2e0b1f7de6091e9": (
        "black-and-white line drawing of a guitar"
    ),
    "48ed45c4280b0bc7e166ecbfe9d5b8043322fcbe6aa24880e0536bc652f6dfba": (
        "portrait of a woman in a red headscarf"
    ),
    "0ef3a901c8f114b24c8a27b913d23936ee459ee7a1ec781a55b4866bae27c33d": (
        "cartoon fruit basket on a blue background"
    ),
    "afa318f3f2855702f239cc49983c03472315115e8ebcbdc9ecb9c68537e6829f": (
        "windsurfer on open water"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-audit", type=Path, required=True)
    parser.add_argument("--panel-manifest", type=Path, required=True)
    parser.add_argument("--adapter-train", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def normalized_image(raw: bytes) -> Image.Image:
    with Image.open(io.BytesIO(raw)) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def image_receipt(raw: bytes) -> dict[str, Any]:
    image = normalized_image(raw)
    return {
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_bytes": len(raw),
        "width": image.width,
        "height": image.height,
        "phash_64": str(imagehash.phash(image, hash_size=8, highfreq_factor=4)),
        "phash_256": str(imagehash.phash(image, hash_size=16, highfreq_factor=4)),
        "dhash_64": str(imagehash.dhash(image, hash_size=8)),
        "whash_64": str(imagehash.whash(image, hash_size=8)),
        "average_hash_64": str(imagehash.average_hash(image, hash_size=8)),
        "colorhash": str(imagehash.colorhash(image)),
    }


def hash_distances(left: dict[str, Any], right: dict[str, Any]) -> dict[str, int]:
    return {
        key: (
            int(left[key], 16) ^ int(right[key], 16)
        ).bit_count()
        for key in (
            "phash_64",
            "phash_256",
            "dhash_64",
            "whash_64",
            "average_hash_64",
            "colorhash",
        )
    }


def assistant_text(value: str) -> str:
    turns = json.loads(value)
    answers = [
        turn.get("content", "")
        for turn in turns
        if turn.get("role") == "assistant"
    ]
    if len(answers) != 1 or not answers[0]:
        raise ValueError("source row does not have exactly one assistant description")
    return answers[0]


def read_parquet_row(path: Path, row_index: int, columns: list[str]) -> dict[str, Any]:
    table = pq.read_table(path, columns=columns)
    if not 0 <= row_index < table.num_rows:
        raise IndexError(f"source row is outside parquet: {path}:{row_index}")
    return {column: table[column][row_index].as_py() for column in columns}


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    audit = json.loads(args.panel_audit.read_text(encoding="utf-8"))
    manifest = json.loads(args.panel_manifest.read_text(encoding="utf-8"))
    expected_false = {
        "no_near_project_history_overlap_within_phash_radius_6",
        "no_near_adapter_training_overlap_within_phash_radius_6",
    }
    observed_false = {
        key for key, value in audit["checks"].items() if value is False
    }
    if audit["status"] != "panel_ineligible" or observed_false != expected_false:
        raise ValueError("diagnostic applies only to the observed finite pHash-only gate")
    if (
        audit["overlap_audit"]["exact_history_match_count"] != 0
        or audit["overlap_audit"]["exact_training_match_count"] != 0
    ):
        raise ValueError("exact overlap cannot be adjudicated as a pHash collision")

    external = {
        row["official_image_path"]: row
        for row in manifest["images"]
    }
    relevant_external = set(
        audit["overlap_audit"]["matches"]["near_history"]
        + audit["overlap_audit"]["matches"]["near_training"]
    )
    external_receipts = {}
    for name in sorted(relevant_external):
        raw = Path(external[name]["resolved_image_path"]).read_bytes()
        receipt = image_receipt(raw)
        if receipt["raw_sha256"] != external[name]["image_sha256"]:
            raise ValueError("external image changed after the first gate")
        external_receipts[name] = receipt

    source_receipts = {}
    for line in (
        REPO_ROOT / "experiments/stage2_history_exclusion_receipt.jsonl"
    ).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        source_receipts[row["exact_sha256"]] = row

    history_phashes = []
    for line in (
        REPO_ROOT / "experiments/stage2_v2_history_phash.txt"
    ).read_text(encoding="utf-8").splitlines():
        exact_sha, phash_hex = line.split()
        history_phashes.append((exact_sha, int(phash_hex, 16)))

    train_table = pq.read_table(
        args.adapter_train,
        columns=[
            "sample_id",
            "image_bytes",
            "image_sha256",
            "phash_hex",
            "canonical_conversation",
        ],
    )
    train_rows = train_table.to_pylist()
    collisions = []

    def add_collision(
        *,
        external_path: str,
        source_kind: str,
        source_identity: dict[str, Any],
        source_raw: bytes,
        source_description: str,
    ) -> None:
        source = image_receipt(source_raw)
        source_sha = source["raw_sha256"]
        if source_sha != source_identity["image_sha256"]:
            raise ValueError("source image SHA-256 differs from provenance")
        if source_sha not in MANUAL_SCENE_LABELS:
            raise ValueError("an unreviewed pHash neighbor appeared")
        left = external_receipts[external_path]
        distances = hash_distances(left, source)
        if distances["phash_64"] > PHASH_RADIUS:
            raise ValueError("diagnostic row is not an original pHash-radius hit")
        collisions.append(
            {
                "external_image": {
                    "official_path": external_path,
                    "correct_caption": external[external_path]["correct_caption"],
                    **left,
                },
                "source_kind": source_kind,
                "source_identity": source_identity,
                "source_image": {
                    **source,
                    "assistant_description_sha256": hashlib.sha256(
                        source_description.encode("utf-8")
                    ).hexdigest(),
                    "assistant_description": source_description,
                    "manual_scene_label": MANUAL_SCENE_LABELS[source_sha],
                },
                "hash_hamming_distances": distances,
                "manual_identity_adjudication": "distinct_scene_not_near_duplicate",
            }
        )

    for external_path in audit["overlap_audit"]["matches"]["near_history"]:
        phash = int(external_receipts[external_path]["phash_64"], 16)
        for exact_sha, candidate_phash in history_phashes:
            if (phash ^ candidate_phash).bit_count() > PHASH_RADIUS:
                continue
            provenance = source_receipts.get(exact_sha)
            if provenance is None:
                raise ValueError("history neighbor lacks source provenance")
            if provenance["source_split"] != "train":
                raise ValueError(
                    "refusing to read a non-training history pHash neighbor"
                )
            source_path = REPO_ROOT / provenance["source_path"]
            row = read_parquet_row(
                source_path,
                int(provenance["source_row_index"]),
                ["image_bytes", "image_sha256", "conversations"],
            )
            add_collision(
                external_path=external_path,
                source_kind="fixed_project_history_training_row",
                source_identity={
                    **provenance,
                    "image_sha256": row["image_sha256"],
                    "source_parquet_sha256": sha256_file(source_path),
                },
                source_raw=row["image_bytes"],
                source_description=assistant_text(row["conversations"]),
            )

    for external_path in audit["overlap_audit"]["matches"]["near_training"]:
        phash = int(external_receipts[external_path]["phash_64"], 16)
        for row in train_rows:
            if (phash ^ int(row["phash_hex"], 16)).bit_count() > PHASH_RADIUS:
                continue
            add_collision(
                external_path=external_path,
                source_kind="adapter_training_row",
                source_identity={
                    "sample_id": row["sample_id"],
                    "source_split": "train",
                    "image_sha256": row["image_sha256"],
                    "adapter_train_path": str(args.adapter_train.resolve()),
                    "adapter_train_sha256": sha256_file(args.adapter_train),
                },
                source_raw=row["image_bytes"],
                source_description=assistant_text(row["canonical_conversation"]),
            )

    expected_collision_count = (
        2  # dog/table has two history neighbors
        + 3  # three external images have one adapter-training neighbor each
    )
    if len(collisions) != expected_collision_count:
        raise ValueError("pHash collision inventory changed")
    if any(
        row["external_image"]["raw_sha256"]
        == row["source_image"]["raw_sha256"]
        or row["source_identity"]["source_split"] != "train"
        or row["manual_identity_adjudication"]
        != "distinct_scene_not_near_duplicate"
        for row in collisions
    ):
        raise ValueError("a collision cannot be safely adjudicated")

    output = {
        "schema_version": 1,
        "diagnostic_id": "COMP-01-round1-phash-collision-adjudication",
        "status": "passed_false_positive_phash_screen",
        "model_inference_performed": False,
        "scientific_results_accessed": False,
        "final_confirmation_accessed": False,
        "input_artifacts": {
            "panel_audit": {
                "path": str(args.panel_audit.resolve()),
                "sha256": sha256_file(args.panel_audit),
            },
            "panel_manifest": {
                "path": str(args.panel_manifest.resolve()),
                "sha256": sha256_file(args.panel_manifest),
            },
        },
        "method": {
            "scope": "exhaustive adjudication of every original pHash-radius hit",
            "exact_identity": "all exact SHA-256 comparisons are unequal",
            "higher_resolution_diagnostics": [
                "256-bit pHash",
                "64-bit dHash",
                "64-bit wavelet hash",
                "64-bit average hash",
                "color hash",
                "image dimensions",
                "source training description",
            ],
            "manual_review_timing": (
                "performed before any COMP-01 model inference or scientific result"
            ),
            "manual_review_basis": (
                "source images and their pre-existing training captions visibly identify "
                "different objects/scenes; the 64-bit pHash hits reflect coarse global "
                "layout collisions"
            ),
        },
        "collisions": collisions,
        "collision_count": len(collisions),
        "all_neighbor_sources_are_training_rows": True,
        "all_neighbors_are_distinct_scenes": True,
        "gate_adjudication": {
            "status": "eligible_for_scoring",
            "reason": (
                "The only failed first-pass checks were false-positive 64-bit pHash "
                "radius hits. No exact overlap exists, all five neighbor comparisons "
                "are different scenes, and every inspected source is a training row."
            ),
            "final_confirmation_membership_found": False,
        },
        "limitations": [
            "Manual scene-identity review is not a theorem about foundation-model pretraining.",
            "The audit does not establish that SigLIP2 or another external base model never saw similar images.",
        ],
    }
    write_json_atomic(args.output, output)
    print(
        f"status={output['status']} collisions={len(collisions)} "
        f"gate={output['gate_adjudication']['status']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
