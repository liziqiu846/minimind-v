#!/usr/bin/env python3
"""Audit formal image groups against all project-controlled image manifests."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_jsonl,
    canonical_json_bytes,
    load_jsonl_snapshot,
    load_json_snapshot,
    publish_directory,
    sha256_bytes,
    snapshot_file,
    validate_relative_posix,
    validate_disjoint_roots,
    write_sha256_sidecar,
)
from experiments.phase3.prepare_phase3_data import PHASH_SPEC_ID
from experiments.phase3.status import Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output


SCOPES = (
    "phase1_training",
    "phase1_model_selection",
    "stage2_adapter_training",
    "stage2_quantization_aware_training",
    "stage2_hyperparameter_selection",
    "stage2_development_validation",
    "stage2_other_model_selection",
)

ASSIGNED_FORMAL_IMAGE_COUNT = 1389
EXCLUDED_FORMAL_IMAGE_COUNT = 44
CERTIFYING_FORMAL_IMAGE_COUNT = 1345
PASS_STATUS = "certification_subset_project_disjoint_under_frozen_checks"
CONDITIONAL_TARGET = (
    "SugarCrepe++ represented target image-text construction distribution conditional on "
    "no project-history image overlap"
)


def _jsonl(path: Path, *, root: Path | None = None) -> list[dict[str, Any]]:
    rows = load_jsonl_snapshot(path, root=root)
    if any(not isinstance(value, dict) for value in rows):
        raise ValueError("JSONL rows must be objects")
    return rows


def _file_binding(path: Path) -> dict[str, Any]:
    payload = snapshot_file(path)
    return {"size_bytes": len(payload), "sha256": sha256_bytes(payload)}


def _pair_identity(formal: dict[str, Any], training: dict[str, Any]) -> dict[str, Any]:
    return {
        "formal_filename": formal["filename"],
        "formal_sha256": formal["sha256"],
        "formal_phash": formal["perceptual_hash"],
        "training_source_id": training["source_id"],
        "training_record_id": training["record_id"],
        "training_sha256": training["sha256"],
        "training_phash": training["perceptual_hash"],
    }


def _pair_id(formal: dict[str, Any], training: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(_pair_identity(formal, training)))


def _distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def _validate_coverage(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    coverage = load_json_snapshot(path)
    if set(coverage) != {"schema_version", "manifest_type", "scopes"} or coverage.get("schema_version") != 1 or coverage.get("manifest_type") != "phase3_project_training_coverage_v1":
        raise ValueError("training coverage schema mismatch")
    scopes = coverage.get("scopes")
    if not isinstance(scopes, list) or [row.get("scope_id") for row in scopes] != list(SCOPES):
        raise ValueError("training coverage must contain the seven frozen scopes in order")
    used_bindings = []
    training_rows = []
    global_record_ids: set[tuple[str, str]] = set()
    for scope in scopes:
        scope_keys = {
            "scope_id", "disposition", "source_description", "source_manifest_relative_alias",
            "source_manifest_sha256", "complete", "image_count", "text_target_count",
            "declaration_by", "declaration_date", "reason",
        }
        if set(scope) != scope_keys:
            raise ValueError(f"coverage scope schema mismatch: {scope.get('scope_id')}")
        for key in ("scope_id", "source_description", "declaration_by", "reason"):
            if not isinstance(scope.get(key), str) or not scope[key]:
                raise ValueError(f"coverage scope requires nonempty {key}")
        if not isinstance(scope.get("declaration_date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", scope["declaration_date"]):
            raise ValueError("coverage declaration_date is invalid")
        if any(not isinstance(scope.get(key), int) or isinstance(scope[key], bool) or scope[key] < 0 for key in ("image_count", "text_target_count")):
            raise ValueError("coverage counts must be nonnegative integers")
        if scope.get("complete") is not True or scope.get("disposition") not in ("used", "not_used"):
            raise ValueError(f"incomplete scope: {scope.get('scope_id')}")
        if scope["disposition"] == "not_used":
            if (
                scope.get("source_manifest_relative_alias") is not None
                or scope.get("source_manifest_sha256") is not None
                or scope["image_count"] != 0
                or scope["text_target_count"] != 0
            ):
                raise ValueError("not_used scope must have null source manifest")
            continue
        alias = str(scope.get("source_manifest_relative_alias"))
        validate_relative_posix(alias)
        source_path = path.parent / alias
        payload = snapshot_file(source_path, root=path.parent)
        actual_sha = sha256_bytes(payload)
        if actual_sha != scope.get("source_manifest_sha256"):
            raise ValueError(f"training source manifest hash mismatch: {scope['scope_id']}")
        rows = _jsonl(source_path, root=path.parent)
        if len(rows) != int(scope.get("image_count")):
            raise ValueError(f"training image count mismatch: {scope['scope_id']}")
        observed_text_targets = 0
        previous = None
        for row in rows:
            required = {
                "source_id", "record_id", "filename", "coco_image_id", "sha256",
                "perceptual_hash", "image_available", "assistant_text_sha256s", "phash_spec_id",
            }
            if set(row) != required or row["phash_spec_id"] != PHASH_SPEC_ID:
                raise ValueError("training image manifest row schema mismatch")
            if not isinstance(row["source_id"], str) or not row["source_id"] or not isinstance(row["record_id"], str) or not row["record_id"]:
                raise ValueError("training row identity is invalid")
            if row["filename"] is not None and (
                not isinstance(row["filename"], str)
                or not row["filename"]
                or row["filename"] in (".", "..")
                or "/" in row["filename"]
                or "\\" in row["filename"]
            ):
                raise ValueError("training filename must be a basename or null")
            if row["coco_image_id"] is not None and (not isinstance(row["coco_image_id"], int) or isinstance(row["coco_image_id"], bool) or row["coco_image_id"] < 0):
                raise ValueError("training COCO ID is invalid")
            for key, length in (("sha256", 64), ("perceptual_hash", 16)):
                value = row[key]
                if value is not None and (not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value)):
                    raise ValueError(f"training {key} is invalid")
            if all(row[key] is None for key in ("filename", "coco_image_id", "sha256")):
                raise ValueError("training row has no exact image identifier")
            hashes = row["assistant_text_sha256s"]
            if not isinstance(hashes, list) or hashes != sorted(set(hashes)) or any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes):
                raise ValueError("assistant text hashes are invalid")
            if not isinstance(row.get("image_available"), bool):
                raise ValueError("training image_available must be boolean")
            observed_text_targets += len(hashes)
            key = (str(row["source_id"]).encode("utf-8"), str(row["record_id"]).encode("utf-8"))
            if previous is not None and key <= previous:
                raise ValueError("training image manifest ordering/uniqueness failed")
            previous = key
            logical_key = (row["source_id"], row["record_id"])
            if logical_key in global_record_ids:
                raise ValueError("training source/record identity is duplicated across scopes")
            global_record_ids.add(logical_key)
            row = dict(row, scope_id=scope["scope_id"])
            training_rows.append(row)
        if observed_text_targets != scope["text_target_count"]:
            raise ValueError(f"training text target count mismatch: {scope['scope_id']}")
        used_bindings.append(
            {
                "scope_id": scope["scope_id"],
                "relative_alias": alias,
                "size_bytes": len(payload),
                "sha256": actual_sha,
            }
        )
    return coverage, used_bindings, training_rows


def audit(args: argparse.Namespace) -> dict[str, Any]:
    validate_disjoint_roots(
        input_roots=[
            args.split_manifest.parent, args.formal_image_manifest.parent,
            args.training_coverage_manifest.parent,
        ] + ([args.overlap_review.parent] if args.overlap_review else []),
        output_roots=[args.output_dir, args.status_output.parent],
        forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
    )
    if args.output_dir.exists():
        raise Phase3HardFailure("output_exists", str(args.output_dir))
    split_binding = _file_binding(args.split_manifest)
    split = load_json_snapshot(args.split_manifest)
    if split.get("formal_unique_images") != ASSIGNED_FORMAL_IMAGE_COUNT or split.get("split_version") != "phase3-v1":
        raise Phase3HardFailure("split_manifest_mismatch", "formal split is not frozen phase3-v1")
    formal_binding = _file_binding(args.formal_image_manifest)
    formal_rows = _jsonl(args.formal_image_manifest)
    formal_keys = {
        "coco_image_id", "error_code", "exists", "filename", "perceptual_hash",
        "sha256", "size_bytes", "status",
    }
    if len(formal_rows) != ASSIGNED_FORMAL_IMAGE_COUNT or any(row.get("status") != "ready" for row in formal_rows):
        raise Phase3Blocked("formal_images_not_ready", "formal image manifest must contain 1389 ready rows")
    if (
        any(set(row) != formal_keys for row in formal_rows)
        or any(not isinstance(row.get("filename"), str) or not re.fullmatch(r"[0-9]{12}\.jpg", row["filename"]) for row in formal_rows)
        or any(not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in formal_rows)
        or any(not isinstance(row.get("perceptual_hash"), str) or not re.fullmatch(r"[0-9a-f]{16}", row["perceptual_hash"]) for row in formal_rows)
    ):
        raise Phase3HardFailure("formal_image_manifest_invalid", "formal image manifest schema/hash fields are invalid")
    if not args.training_coverage_manifest.is_file():
        raise Phase3Blocked("project_overlap_audit_unknown", "training coverage manifest is missing")
    try:
        coverage, used_bindings, training_rows = _validate_coverage(args.training_coverage_manifest)
        coverage_raw = canonical_json_bytes(coverage)
        coverage_complete = True
    except FileNotFoundError as error:
        raise Phase3Blocked("project_overlap_audit_unknown", str(error)) from error
    except ValueError as error:
        if "incomplete scope" in str(error):
            raise Phase3Blocked("project_overlap_audit_unknown", str(error)) from error
        raise Phase3HardFailure("training_coverage_binding_invalid", str(error)) from error
    p_hash_complete = all(
        row.get("image_available") is True
        and isinstance(row.get("perceptual_hash"), str)
        and len(row["perceptual_hash"]) == 16
        for row in training_rows
    )
    input_object = {
        "ruleset_id": "phase3-project-image-overlap-exclusion-v2",
        "split_manifest": split_binding,
        "formal_image_manifest": formal_binding,
        "training_coverage_manifest": {"size_bytes": len(coverage_raw), "sha256": sha256_bytes(coverage_raw)},
        "used_source_manifests": used_bindings,
        "phash_spec_id": PHASH_SPEC_ID,
        "exact_identifier_fields": ["filename", "coco_image_id", "sha256"],
        "probable_max_distance": 4,
        "near_min_distance": 5,
        "near_max_distance": 10,
    }
    audit_input_sha = sha256_bytes(canonical_json_bytes(input_object))
    exact, probable, near = [], [], []
    for formal in formal_rows:
        for training in training_rows:
            match_types = []
            for name in ("filename", "coco_image_id", "sha256"):
                if formal.get(name) is not None and training.get(name) is not None and formal[name] == training[name]:
                    match_types.append(name)
            if match_types:
                pair_id = _pair_id(formal, training)
                identity = _pair_identity(formal, training)
                base = {"pair_id": pair_id, "scope_id": training["scope_id"], **identity}
                exact.append({**base, "match_types": match_types})
                continue
            if isinstance(formal.get("perceptual_hash"), str) and isinstance(training.get("perceptual_hash"), str):
                distance = _distance(formal["perceptual_hash"], training["perceptual_hash"])
                if distance <= 4:
                    pair_id = _pair_id(formal, training)
                    identity = _pair_identity(formal, training)
                    base = {"pair_id": pair_id, "scope_id": training["scope_id"], **identity}
                    probable.append({**base, "hamming_distance": distance})
                elif distance <= 10:
                    pair_id = _pair_id(formal, training)
                    identity = _pair_identity(formal, training)
                    base = {"pair_id": pair_id, "scope_id": training["scope_id"], **identity}
                    near.append({**base, "hamming_distance": distance})
    exact.sort(key=lambda row: row["pair_id"])
    probable.sort(key=lambda row: row["pair_id"])
    near.sort(key=lambda row: row["pair_id"])
    formal_text_rows = []
    formal_entry = next((row for row in split.get("files", []) if row.get("logical_name") == "formal_jsonl"), None)
    if formal_entry is None:
        raise Phase3Blocked("project_overlap_audit_unknown", "split manifest has no formal JSONL binding")
    formal_data_path = args.split_manifest.parent / formal_entry["relative_path"]
    formal_caption_rows = _jsonl(formal_data_path, root=args.split_manifest.parent)
    formal_data_raw = b"".join(canonical_json_bytes(row) for row in formal_caption_rows)
    if len(formal_data_raw) != formal_entry["size_bytes"] or sha256_bytes(formal_data_raw) != formal_entry["sha256"]:
        raise Phase3Blocked("project_overlap_audit_unknown", "formal JSONL binding mismatch")
    training_hash_rows: dict[str, list[dict[str, Any]]] = {}
    for training in training_rows:
        for digest in training["assistant_text_sha256s"]:
            training_hash_rows.setdefault(digest, []).append(training)
    for formal_caption_row in formal_caption_rows:
        for key in ("caption", "caption2", "negative_caption"):
            normalized = unicodedata.normalize("NFC", formal_caption_row[key].replace("\r\n", "\n").replace("\r", "\n"))
            digest = sha256_bytes(normalized.encode("utf-8"))
            for training in training_hash_rows.get(digest, []):
                identity = {
                    "scope_id": training["scope_id"],
                    "training_source_id": training["source_id"],
                    "training_record_id": training["record_id"],
                    "formal_row_key": formal_caption_row["row_key"],
                    "matching_text_sha256": digest,
                }
                formal_text_rows.append({"pair_id": sha256_bytes(canonical_json_bytes(identity)), **identity})
    formal_text_rows.sort(key=lambda row: row["pair_id"])

    review_sha = None
    review_raw = None
    decisions = {}
    if args.overlap_review:
        review = load_json_snapshot(args.overlap_review)
        review_raw = canonical_json_bytes(review)
        if (
            set(review) != {"schema_version", "overlap_audit_input_sha256", "reviewer", "reviewed_at", "decisions"}
            or review.get("schema_version") != 1
            or review.get("overlap_audit_input_sha256") != audit_input_sha
            or not isinstance(review.get("reviewer"), str) or not review["reviewer"]
            or not isinstance(review.get("reviewed_at"), str) or not review["reviewed_at"]
            or not isinstance(review.get("decisions"), list)
        ):
            raise Phase3HardFailure("overlap_review_binding_invalid", "review input hash differs")
        for decision in review.get("decisions", []):
            expected_decision_keys = {"pair_id", "formal_sha256", "formal_phash", "training_sha256", "training_phash", "decision"}
            if set(decision) != expected_decision_keys or decision.get("decision") not in ("same_source_image", "not_same_source_image"):
                raise Phase3HardFailure("overlap_review_binding_invalid", "invalid decision")
            pair = next((row for row in probable if row["pair_id"] == decision.get("pair_id")), None)
            if pair is None or any(decision[key] != pair[key] for key in ("formal_sha256", "formal_phash", "training_sha256", "training_phash")):
                raise Phase3HardFailure("overlap_review_binding_invalid", "decision identity binding mismatch")
            if decision["pair_id"] in decisions:
                raise Phase3HardFailure("overlap_review_binding_invalid", "duplicate decision")
            decisions[decision["pair_id"]] = decision["decision"]
        review_sha = sha256_bytes(review_raw)
    probable_ids = {row["pair_id"] for row in probable}
    invalid_review = set(decisions) - probable_ids
    if invalid_review:
        raise Phase3HardFailure("overlap_review_binding_invalid", "review contains unknown pair IDs")
    unreviewed = probable_ids - set(decisions)
    same = sum(decisions.get(pair_id) == "same_source_image" for pair_id in probable_ids)
    not_same = sum(decisions.get(pair_id) == "not_same_source_image" for pair_id in probable_ids)
    excluded_evidence: dict[str, list[tuple[str, str]]] = {}
    formal_by_name = {row["filename"]: row for row in formal_rows}
    for row in exact:
        excluded_evidence.setdefault(row["formal_filename"], []).append(
            (row["pair_id"], "exact_identifier_match")
        )
    for row in probable:
        if decisions.get(row["pair_id"]) == "same_source_image":
            excluded_evidence.setdefault(row["formal_filename"], []).append(
                (row["pair_id"], "human_confirmed_same_source")
            )
    excluded_rows = []
    for filename in sorted(excluded_evidence, key=lambda value: value.encode("utf-8")):
        formal = formal_by_name[filename]
        evidence = excluded_evidence[filename]
        excluded_rows.append(
            {
                "filename": filename,
                "formal_sha256": formal["sha256"],
                "formal_phash": formal["perceptual_hash"],
                "exclusion_bases": sorted({basis for _, basis in evidence}),
                "supporting_pair_ids": sorted({pair_id for pair_id, _ in evidence}),
            }
        )
    excluded_names = set(excluded_evidence)
    certifying_names = [row["filename"] for row in formal_rows if row["filename"] not in excluded_names]
    if unreviewed:
        status = "probable_reencoded_duplicate_unresolved"
    elif not coverage_complete or not p_hash_complete:
        status = "unknown"
    elif (
        len(excluded_rows) == EXCLUDED_FORMAL_IMAGE_COUNT
        and len(certifying_names) == CERTIFYING_FORMAL_IMAGE_COUNT
    ):
        status = PASS_STATUS
    else:
        status = "approved_exclusion_count_mismatch"

    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.", dir=args.output_dir.parent))
    try:
        detail_rows = {
            "exact_matches.jsonl": exact,
            "probable_pairs.jsonl": probable,
            "near_duplicate_diagnostics.jsonl": near,
            "text_match_diagnostics.jsonl": formal_text_rows,
        }
        detail_files = []
        for name, rows in detail_rows.items():
            atomic_write_jsonl(temporary / name, rows)
            payload = snapshot_file(temporary / name, root=temporary)
            detail_files.append({"relative_path": name, "size_bytes": len(payload), "sha256": sha256_bytes(payload), "row_count": len(rows)})
        atomic_write_jsonl(temporary / "excluded_formal_images.jsonl", excluded_rows)
        excluded_payload = snapshot_file(temporary / "excluded_formal_images.jsonl", root=temporary)
        atomic_write_bytes(
            temporary / "certifying_formal_filenames.txt",
            ("\n".join(certifying_names) + "\n").encode("utf-8"),
        )
        certifying_payload = snapshot_file(temporary / "certifying_formal_filenames.txt", root=temporary)
        exclusion_files = [
            {
                "relative_path": "certifying_formal_filenames.txt",
                "size_bytes": len(certifying_payload),
                "sha256": sha256_bytes(certifying_payload),
                "record_count": len(certifying_names),
            },
            {
                "relative_path": "excluded_formal_images.jsonl",
                "size_bytes": len(excluded_payload),
                "sha256": sha256_bytes(excluded_payload),
                "record_count": len(excluded_rows),
            },
        ]
        if review_raw is not None:
            atomic_write_bytes(temporary / "overlap_review.json", review_raw)
        receipt = {
            "schema_version": 1,
            "receipt_type": "phase3_project_image_overlap_audit_v2",
            "protocol_version": "phase3-v4",
            "split_version": "phase3-v1",
            "overlap_audit_input_sha256": audit_input_sha,
            "split_manifest_sha256": split_binding["sha256"],
            "formal_image_manifest_sha256": formal_binding["sha256"],
            "training_coverage_manifest_sha256": sha256_bytes(coverage_raw),
            "used_source_manifests": used_bindings,
            "overlap_review_sha256": review_sha,
            "phash_spec_id": PHASH_SPEC_ID,
            "formal_image_count": ASSIGNED_FORMAL_IMAGE_COUNT,
            "excluded_formal_image_count": len(excluded_rows),
            "certifying_formal_image_count": len(certifying_names),
            "scope_count": 7,
            "coverage_complete": coverage_complete,
            "phash_coverage_complete": p_hash_complete,
            "exact_match_count": len(exact),
            "probable_pair_count": len(probable),
            "probable_unreviewed_count": len(unreviewed),
            "probable_same_source_count": same,
            "probable_same_source_formal_count": len({
                row["formal_filename"]
                for row in probable
                if decisions.get(row["pair_id"]) == "same_source_image"
            }),
            "probable_not_same_source_count": not_same,
            "near_duplicate_pair_count": len(near),
            "text_match_count": len(formal_text_rows),
            "detail_files": sorted(detail_files, key=lambda row: row["relative_path"]),
            "exclusion_files": exclusion_files,
            "project_overlap_audit_status": status,
            "external_base_pretraining_overlap": "unknown",
            "certificate_scope": "project_controlled_image_group_disjoint_certifying_subset_only",
            "conditional_target_distribution": CONDITIONAL_TARGET,
        }
        receipt_path = temporary / "phase3_overlap_audit_receipt.json"
        atomic_write_json(receipt_path, receipt)
        write_sha256_sidecar(receipt_path)
        publish_directory(temporary, args.output_dir)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    if status != PASS_STATUS:
        raise Phase3Blocked(status, "formal certification remains blocked")
    return {"overlap_receipt": str(args.output_dir / "phase3_overlap_audit_receipt.json"), "status": status}


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--formal-image-manifest", type=Path, required=True)
    parser.add_argument("--training-coverage-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overlap-review", type=Path)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return execute_with_status("audit_training_overlap", args.status_output, lambda: audit(args))


if __name__ == "__main__":
    raise SystemExit(main())
