"""Deterministic What’sUp controlled-panel loader and contamination audit."""

from __future__ import annotations

import hashlib
import json
import os
import tarfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import imagehash
import pyarrow.parquet as pq
from PIL import Image, ImageOps

from experiments.build_stage2_dataset import HammingBKTree
from experiments.stage2_protocol import Stage2Protocol, sha256_file


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE2_PROTOCOL_PATH = REPO_ROOT / "experiments/stage2_protocol_v2.json"
EXPECTED_TRAIN_SHA256 = (
    "3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce"
)
PHASH_RADIUS = 6
PAPER_SHA256 = (
    "ac45c83976d316ca06e3df6386a74a2b1cbf1a1f470f2c8db70aaf71935a36b3"
)
OFFICIAL_REPOSITORY_COMMIT = "7c1f2550eace32e7b8c77de5a792347c402960d1"

DATASETS: tuple[dict[str, Any], ...] = (
    {
        "dataset_id": "controlled_images",
        "annotation": "controlled_images_dataset.json",
        "annotation_sha256": (
            "77ee94ae35552ed643ecd47f700daa178e10051458baae99d5c4c5d5922590d3"
        ),
        "archive": "controlled_images.tar.gz",
        "archive_sha256": (
            "4fc005e7ab1e2ac5e5836d2456dd9ae930239c44953b0b2d3e9523f6ad5b1a69"
        ),
        "expected_rows": 412,
        "expected_groups": 103,
        "expected_extra_images": 9,
        "relations": ("on", "under", "left", "right"),
        "relation_pairs": (
            ("vertical", "on", "under"),
            ("horizontal", "left", "right"),
        ),
    },
    {
        "dataset_id": "controlled_clevr",
        "annotation": "controlled_clevr_dataset.json",
        "annotation_sha256": (
            "2c0df1ab59d13d71442752b4b3c7353114d712a785b0850ec22e11c2b0c474c9"
        ),
        "archive": "controlled_clevr.tar.gz",
        "archive_sha256": (
            "df8b23af7dc73c4bf98937777b7a5d85aab42598eace82fa7adad5802df2c493"
        ),
        "expected_rows": 408,
        "expected_groups": 102,
        "expected_extra_images": 0,
        "relations": ("front", "behind", "left", "right"),
        "relation_pairs": (
            ("depth", "front", "behind"),
            ("horizontal", "left", "right"),
        ),
    },
)

RELATION_LITERALS = (
    ("left", " to the left of "),
    ("right", " to the right of "),
    ("front", " in front of "),
    ("behind", " behind "),
    ("under", " under "),
    ("on", " on "),
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    os.replace(temporary, path)


def relation_from_caption(caption: str) -> str:
    matches = [
        relation
        for relation, literal in RELATION_LITERALS
        if literal in caption.lower()
    ]
    if len(matches) != 1:
        raise ValueError(
            f"caption does not contain exactly one controlled relation: {caption!r}"
        )
    return matches[0]


def resolve_annotation_image(panel_root: Path, annotation_path: str) -> Path:
    pure = PurePosixPath(annotation_path)
    if (
        pure.is_absolute()
        or not pure.parts
        or pure.parts[0] != "data"
        or ".." in pure.parts
    ):
        raise ValueError(f"unsafe or unexpected annotation image path: {annotation_path}")
    path = panel_root.joinpath(*pure.parts[1:]).resolve()
    if not path.is_relative_to(panel_root.resolve()):
        raise ValueError("annotation image escapes panel root")
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def image_phash(path: Path) -> str:
    with Image.open(path) as image:
        normalized = ImageOps.exif_transpose(image).convert("RGB")
        return str(imagehash.phash(normalized, hash_size=8, highfreq_factor=4))


def _group_id(dataset_id: str, captions: Iterable[str]) -> str:
    digest = hashlib.sha256(
        canonical_json_bytes(sorted(captions))
    ).hexdigest()[:16]
    return f"{dataset_id}-{digest}"


def load_panel(panel_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Load all 820 referenced images and deterministically form 410 pairs."""

    panel_root = panel_root.resolve()
    image_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    dataset_receipts = []
    all_paths: set[Path] = set()

    for spec in DATASETS:
        annotation_path = panel_root / spec["annotation"]
        archive_path = panel_root / spec["archive"]
        if sha256_file(annotation_path) != spec["annotation_sha256"]:
            raise ValueError(f"{spec['dataset_id']} annotation SHA-256 mismatch")
        if sha256_file(archive_path) != spec["archive_sha256"]:
            raise ValueError(f"{spec['dataset_id']} archive SHA-256 mismatch")
        annotations = json.loads(annotation_path.read_text(encoding="utf-8"))
        if not isinstance(annotations, list) or len(annotations) != spec["expected_rows"]:
            raise ValueError(f"{spec['dataset_id']} annotation row count mismatch")

        grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
        referenced: set[Path] = set()
        for annotation_index, row in enumerate(annotations):
            if set(row) != {"image_path", "caption_options"}:
                raise ValueError("annotation schema differs from the official two fields")
            captions = row["caption_options"]
            if (
                not isinstance(captions, list)
                or len(captions) != 4
                or len(set(captions)) != 4
                or not all(isinstance(value, str) and value for value in captions)
            ):
                raise ValueError("caption_options must contain four distinct captions")
            image_path = resolve_annotation_image(panel_root, row["image_path"])
            if image_path in referenced or image_path in all_paths:
                raise ValueError("an annotation image is duplicated")
            referenced.add(image_path)
            all_paths.add(image_path)
            relation = relation_from_caption(captions[0])
            record = {
                "dataset_id": spec["dataset_id"],
                "annotation_index": annotation_index,
                "official_image_path": row["image_path"],
                "resolved_image_path": str(image_path),
                "correct_caption": captions[0],
                "caption_options": captions,
                "relation": relation,
            }
            grouped[tuple(sorted(captions))].append(record)

        if len(grouped) != spec["expected_groups"]:
            raise ValueError(f"{spec['dataset_id']} controlled group count mismatch")
        expected_relations = set(spec["relations"])
        for captions_key in sorted(grouped):
            rows = grouped[captions_key]
            if len(rows) != 4:
                raise ValueError("controlled group does not contain four images")
            correct = {row["correct_caption"] for row in rows}
            if correct != set(captions_key):
                raise ValueError("controlled group does not rotate every caption to correct")
            by_relation = {row["relation"]: row for row in rows}
            if set(by_relation) != expected_relations:
                raise ValueError("controlled group relation inventory mismatch")
            group_id = _group_id(spec["dataset_id"], captions_key)
            for row in rows:
                row["group_id"] = group_id
                image_rows.append(row)
            for family, relation_0, relation_1 in spec["relation_pairs"]:
                row_0 = by_relation[relation_0]
                row_1 = by_relation[relation_1]
                pair_rows.append(
                    {
                        "pair_id": f"{group_id}-{family}",
                        "dataset_id": spec["dataset_id"],
                        "group_id": group_id,
                        "relation_family": family,
                        "relation_0": relation_0,
                        "relation_1": relation_1,
                        "image_0_path": row_0["resolved_image_path"],
                        "image_1_path": row_1["resolved_image_path"],
                        "caption_0": row_0["correct_caption"],
                        "caption_1": row_1["correct_caption"],
                    }
                )

        extracted_dir = panel_root / spec["dataset_id"]
        extracted_images = {
            path.resolve()
            for path in extracted_dir.rglob("*")
            if path.is_file()
        }
        extra = sorted(extracted_images - referenced)
        missing = sorted(referenced - extracted_images)
        if missing or len(extra) != spec["expected_extra_images"]:
            raise ValueError(f"{spec['dataset_id']} extracted-image inventory mismatch")

        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = archive.getmembers()
            unsafe = [
                member.name
                for member in members
                if PurePosixPath(member.name).is_absolute()
                or ".." in PurePosixPath(member.name).parts
                or member.issym()
                or member.islnk()
            ]
        if unsafe:
            raise ValueError(f"{spec['dataset_id']} archive contains unsafe members")

        dataset_receipts.append(
            {
                "dataset_id": spec["dataset_id"],
                "annotation": {
                    "path": str(annotation_path),
                    "sha256": sha256_file(annotation_path),
                    "rows": len(annotations),
                },
                "archive": {
                    "path": str(archive_path),
                    "sha256": sha256_file(archive_path),
                    "member_count": len(members),
                    "unsafe_member_count": 0,
                },
                "controlled_groups": len(grouped),
                "opposing_relation_pairs": 2 * len(grouped),
                "referenced_images": len(referenced),
                "unreferenced_extracted_images_ignored": [
                    str(path) for path in extra
                ],
            }
        )

    if len(image_rows) != 820 or len(pair_rows) != 410:
        raise ValueError("complete panel must contain 820 images and 410 pairs")
    if len({row["pair_id"] for row in pair_rows}) != len(pair_rows):
        raise ValueError("pair IDs are not unique")
    return image_rows, pair_rows, {
        "datasets": dataset_receipts,
        "referenced_image_count": len(image_rows),
        "independent_object_groups": 205,
        "opposing_relation_pair_count": len(pair_rows),
        "pair_family_counts": {
            family: sum(
                row["relation_family"] == family for row in pair_rows
            )
            for family in ("horizontal", "vertical", "depth")
        },
    }


def _read_history(protocol: Stage2Protocol) -> tuple[set[str], list[int], dict[str, Any]]:
    history = protocol.payload["history_exclusion"]
    exact_path = REPO_ROOT / history["exact_sha256_path"]
    phash_path = REPO_ROOT / history["phash_path"]
    exact = {
        line.strip()
        for line in exact_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    phashes = [
        int(line.split()[1], 16)
        for line in phash_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if sha256_file(exact_path) != history["exact_sha256_sha256"]:
        raise ValueError("fixed history exact-SHA file mismatch")
    if sha256_file(phash_path) != history["phash_sha256"]:
        raise ValueError("fixed history pHash file mismatch")
    if len(exact) != history["unique_exact_images"] or len(phashes) != history["phash_rows"]:
        raise ValueError("fixed history cardinality mismatch")
    return exact, phashes, {
        "exact_sha256_path": str(exact_path.resolve()),
        "exact_sha256_file_sha256": sha256_file(exact_path),
        "unique_exact_images": len(exact),
        "phash_path": str(phash_path.resolve()),
        "phash_file_sha256": sha256_file(phash_path),
        "phash_rows": len(phashes),
    }


def _read_training(train_path: Path) -> tuple[set[str], list[int], dict[str, Any]]:
    train_path = train_path.resolve()
    digest = sha256_file(train_path)
    if digest != EXPECTED_TRAIN_SHA256:
        raise ValueError("adapter training parquet SHA-256 mismatch")
    parquet = pq.ParquetFile(train_path)
    exact: set[str] = set()
    phashes: set[int] = set()
    row_count = 0
    for batch in parquet.iter_batches(
        batch_size=4096, columns=("image_sha256", "phash_hex")
    ):
        exact.update(batch.column(0).to_pylist())
        phashes.update(int(value, 16) for value in batch.column(1).to_pylist())
        row_count += batch.num_rows
    if row_count != 10_000:
        raise ValueError("adapter training row count mismatch")
    return exact, sorted(phashes), {
        "path": str(train_path),
        "sha256": digest,
        "rows": row_count,
        "unique_exact_images": len(exact),
        "unique_phashes": len(phashes),
        "columns_read": ["image_sha256", "phash_hex"],
        "validation_or_final_confirmation_read": False,
    }


def audit_panel(
    *,
    panel_root: Path,
    train_path: Path,
    paper_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a panel manifest and eligibility gate without model inference."""

    image_rows, pair_rows, panel = load_panel(panel_root)
    if sha256_file(paper_path) != PAPER_SHA256:
        raise ValueError("primary-paper PDF SHA-256 mismatch")
    protocol = Stage2Protocol.load(STAGE2_PROTOCOL_PATH, require_frozen=True)
    protocol.verify_immutable_inputs()
    history_exact, history_phashes, history_receipt = _read_history(protocol)
    train_exact, train_phashes, train_receipt = _read_training(train_path)
    history_tree = HammingBKTree(history_phashes)
    train_tree = HammingBKTree(train_phashes)

    exact_history_matches = []
    exact_training_matches = []
    near_history_matches = []
    near_training_matches = []
    manifest_images = []
    for row in image_rows:
        path = Path(row["resolved_image_path"])
        digest = sha256_file(path)
        phash_hex = image_phash(path)
        if digest in history_exact:
            exact_history_matches.append(row["official_image_path"])
        if digest in train_exact:
            exact_training_matches.append(row["official_image_path"])
        phash_value = int(phash_hex, 16)
        if history_tree.has_within(phash_value, PHASH_RADIUS):
            near_history_matches.append(row["official_image_path"])
        if train_tree.has_within(phash_value, PHASH_RADIUS):
            near_training_matches.append(row["official_image_path"])
        manifest_images.append(
            {
                **row,
                "image_sha256": digest,
                "phash_hex": phash_hex,
            }
        )

    overlap = {
        "identity_definition": "SHA256(raw image-file bytes)",
        "perceptual_hash": {
            "library": "ImageHash",
            "version": imagehash.__version__,
            "hash_size": 8,
            "highfreq_factor": 4,
            "preprocess": "Pillow decode; ImageOps.exif_transpose; RGB",
            "forbidden_hamming_radius_inclusive": PHASH_RADIUS,
        },
        "fixed_project_history": history_receipt,
        "adapter_training": train_receipt,
        "exact_history_match_count": len(exact_history_matches),
        "exact_training_match_count": len(exact_training_matches),
        "phash_within_radius_history_count": len(near_history_matches),
        "phash_within_radius_training_count": len(near_training_matches),
        "matches": {
            "exact_history": exact_history_matches,
            "exact_training": exact_training_matches,
            "near_history": near_history_matches,
            "near_training": near_training_matches,
        },
        "scope_limitation": (
            "This audit covers repository/project exposure history and adapter "
            "training only; it cannot establish absence from external foundation-model "
            "pretraining."
        ),
    }
    checks = {
        "official_annotations_and_archives_match_frozen_sha256": True,
        "archive_paths_safe": True,
        "all_820_annotation_images_present_and_unique": len(manifest_images) == 820,
        "all_410_opposing_relation_pairs_formed": len(pair_rows) == 410,
        "unreferenced_archive_images_ignored": sum(
            len(row["unreferenced_extracted_images_ignored"])
            for row in panel["datasets"]
        )
        == 9,
        "no_exact_project_history_overlap": not exact_history_matches,
        "no_exact_adapter_training_overlap": not exact_training_matches,
        "no_near_project_history_overlap_within_phash_radius_6": not near_history_matches,
        "no_near_adapter_training_overlap_within_phash_radius_6": not near_training_matches,
        "not_final_confirmation_set": True,
        "no_final_confirmation_data_read": True,
        "frozen_models_predate_panel_scoring": True,
    }
    passed = all(checks.values())
    manifest = {
        "schema_version": 1,
        "manifest_id": "COMP-01-WhatUp-controlled-panel-v1",
        "images": manifest_images,
        "pairs": pair_rows,
    }
    audit = {
        "schema_version": 1,
        "audit_id": "COMP-01-round1-panel-gate",
        "status": "passed" if passed else "panel_ineligible",
        "model_inference_performed": False,
        "scientific_results_accessed": False,
        "primary_source": {
            "title": "What’s “up” with vision-language models?",
            "venue": "EMNLP 2023",
            "doi": "10.18653/v1/2023.emnlp-main.568",
            "arxiv": "2310.19785",
            "pdf_path": str(paper_path.resolve()),
            "pdf_sha256": sha256_file(paper_path),
        },
        "official_repository": {
            "url": "https://github.com/amitakamath/whatsup_vlms",
            "commit": OFFICIAL_REPOSITORY_COMMIT,
            "license": "MIT",
        },
        "panel": panel,
        "overlap_audit": overlap,
        "checks": checks,
        "eligible_for_scoring": passed,
        "interpretation": (
            "The complete official controlled panel is eligible as an external "
            "operational composition-binding test under the immutable COMP-01 plan."
            if passed
            else "The panel failed a preregistered eligibility gate and must not be scored."
        ),
    }
    return manifest, audit
