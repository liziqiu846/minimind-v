"""Strict validation for Phase 3 manifests, receipts, and prepared data."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path
from typing import Any

from experiments.phase3.canonical_io import (
    canonical_json_bytes,
    load_json_snapshot,
    sha256_bytes,
    snapshot_file,
    validate_relative_posix,
)
from experiments.phase3.datasets.sugarcrepe_pp import (
    REPO_ID,
    REVISION,
    SOURCES,
    SPLIT,
    canonical_row_commitment,
    row_index,
)


PROTOCOL_VERSION = "phase3-v4"
SPLIT_VERSION = "phase3-v1"
MODEL_IDS = (
    "M0-root-43101", "M0-root-43102", "M0-root-43103", "M1-root-none",
    "M2-root-43101", "M2-root-43102", "M2-root-43103",
    "M3-root-43101", "M3-root-43102", "M3-root-43103",
)
PHASH_SPEC_ID = "imagehash-4.3.2_pillow-11.3.0_numpy-1.26.4_scipy-1.15.3_h8_f4_exif-rgb"
OVERLAP_PASS_STATUS = "certification_subset_project_disjoint_under_frozen_checks"
CONDITIONAL_TARGET_DISTRIBUTION = (
    "SugarCrepe++ represented target image-text construction distribution conditional on "
    "no project-history image overlap"
)
PHASH_ENVIRONMENT = {
    "ImageHash": "4.3.2",
    "Pillow": "11.3.0",
    "NumPy": "1.26.4",
    "SciPy": "1.15.3",
    "hash_size": 8,
    "highfreq_factor": 4,
    "preprocess": "Pillow decode -> EXIF transpose -> RGB",
}
IMAGE_STATUSES = ("ready", "missing", "unreadable", "unsafe_path", "decode_failed")
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX16 = re.compile(r"[0-9a-f]{16}")
COCO_NAME = re.compile(r"[0-9]{12}\.jpg")
EXPECTED_DATA_ARTIFACTS = tuple(sorted((
    "canonical_row_index.jsonl",
    "coco_formal_images_manifest.jsonl",
    "coco_pilot_images_manifest.jsonl",
    "coco_referenced_images_manifest.jsonl",
    "data_diagnostics.json",
    "degenerate_rows.json",
    "formal_filenames.txt",
    "image_failures.json",
    "input_invariant_failures.json",
    "missing_images.json",
    "overlength_rows.json",
    "pilot_filenames.txt",
    "split_manifest.json",
    "split_manifest.sha256",
    "sugarcrepe_pp_canonical.jsonl",
    "sugarcrepe_pp_formal.jsonl",
    "sugarcrepe_pp_pilot.jsonl",
), key=lambda value: value.encode("utf-8")))


def verify_sidecar(path: str | Path, *, root: str | Path | None = None) -> str:
    target = Path(path)
    payload = snapshot_file(target, root=root)
    digest = sha256_bytes(payload)
    sidecar = target.with_suffix(".sha256")
    if snapshot_file(sidecar, root=root) != (digest + "\n").encode("ascii"):
        raise ValueError(f"SHA-256 sidecar mismatch: {target.name}")
    return digest


def _canonical_json(path: Path, *, root: Path) -> dict[str, Any]:
    raw = snapshot_file(path, root=root)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ValueError(f"noncanonical JSON object: {path.name}")
    return value


def canonical_jsonl(path: Path, *, root: Path) -> list[dict[str, Any]]:
    raw = snapshot_file(path, root=root)
    if raw and not raw.endswith(b"\n"):
        raise ValueError(f"JSONL lacks final LF: {path.name}")
    rows = []
    for number, line in enumerate(raw.splitlines(keepends=True), 1):
        value = json.loads(line.decode("utf-8"))
        if not isinstance(value, dict) or canonical_json_bytes(value) != line:
            raise ValueError(f"noncanonical JSONL row: {path.name}:{number}")
        rows.append(value)
    return rows


def _bound_file(root: Path, entry: dict[str, Any], *, row_count: int | None = None) -> bytes:
    if set(entry) not in (
        {"logical_name", "relative_path", "size_bytes", "sha256", "row_count"},
        {"relative_path", "size_bytes", "sha256", "row_count"},
        {"relative_path", "size_bytes", "sha256", "record_count"},
    ):
        raise ValueError("manifest file binding schema mismatch")
    relative = validate_relative_posix(entry["relative_path"]).as_posix()
    payload = snapshot_file(root / relative, root=root)
    if len(payload) != entry["size_bytes"] or sha256_bytes(payload) != entry["sha256"]:
        raise ValueError(f"manifest file binding mismatch: {relative}")
    count_key = "row_count" if "row_count" in entry else "record_count"
    expected_count = entry[count_key]
    actual_count = None
    if relative.endswith(".jsonl"):
        actual_count = len(payload.splitlines())
    elif relative.endswith(".txt"):
        if payload and not payload.endswith(b"\n"):
            raise ValueError(f"text manifest member lacks final LF: {relative}")
        actual_count = len([line for line in payload.splitlines() if line])
    if expected_count != actual_count:
        raise ValueError(f"manifest record count mismatch: {relative}")
    if row_count is not None and actual_count != row_count:
        raise ValueError(f"frozen record count mismatch: {relative}")
    return payload


def validate_model_verification_receipt(
    receipt_path: str | Path,
    registry_path: str | Path,
    *,
    require_all: bool,
) -> dict[str, Any]:
    receipt_path = Path(receipt_path)
    registry_path = Path(registry_path)
    receipt_digest = verify_sidecar(receipt_path)
    receipt = load_json_snapshot(receipt_path)
    if sha256_bytes(canonical_json_bytes(receipt)) != receipt_digest:
        raise ValueError("model verification receipt changed after sidecar verification")
    registry = load_json_snapshot(registry_path)
    registry_raw = canonical_json_bytes(registry)
    required_top = {
        "schema_version", "receipt_type", "artifact_batch_id", "authority_id",
        "stage2_reference_commit", "rerun_source_commit", "recovery_verification_sha256",
        "expected_model_registry_sha256", "authority_manifest_sha256", "decoder_id",
        "decoder_source_sha256", "model_count", "overall_status", "models",
    }
    if set(receipt) != required_top or receipt.get("schema_version") != 2:
        raise ValueError("model verification receipt schema mismatch")
    if (
        receipt.get("receipt_type") != "phase3_stage2_artifact_verification_v3"
        or receipt.get("artifact_batch_id") != "stage2-v2-rerun-20260721"
        or receipt.get("expected_model_registry_sha256") != sha256_bytes(registry_raw)
        or receipt.get("authority_manifest_sha256") != registry.get("authority_manifest_sha256")
        or receipt.get("decoder_id") != registry.get("decoder_id")
        or receipt.get("decoder_source_sha256") != registry.get("decoder_source_sha256")
        or receipt.get("model_count") != 10
    ):
        raise ValueError("model verification receipt binding mismatch")
    expected_rows = registry.get("models")
    actual_rows = receipt.get("models")
    if not isinstance(expected_rows, list) or not isinstance(actual_rows, list) or len(actual_rows) != 10:
        raise ValueError("model verification receipt count mismatch")
    if [row.get("model_id") for row in actual_rows] != list(MODEL_IDS):
        raise ValueError("model verification receipt order mismatch")
    row_keys = {
        "model_id", "method", "mapping_root", "resolved_relative_path", "expected_sha256",
        "actual_sha256", "expected_size_bytes", "actual_size_bytes", "decoded_method",
        "decoded_mapping_root", "status", "error_code",
    }
    hard = False
    missing = False
    for expected, actual in zip(expected_rows, actual_rows):
        if set(actual) != row_keys:
            raise ValueError("model verification receipt row schema mismatch")
        frozen = {
            "model_id": expected["model_id"], "method": expected["method"],
            "mapping_root": expected["mapping_root"],
            "resolved_relative_path": expected["artifact_relative_path"],
            "expected_sha256": expected["artifact_sha256"],
            "expected_size_bytes": expected["artifact_size_bytes"],
        }
        if any(actual[key] != value for key, value in frozen.items()):
            raise ValueError(f"model receipt identity mismatch: {expected['model_id']}")
        status = actual.get("status")
        if status == "verified":
            if (
                actual.get("error_code") is not None
                or actual.get("actual_sha256") != expected["artifact_sha256"]
                or actual.get("actual_size_bytes") != expected["artifact_size_bytes"]
                or actual.get("decoded_method") != expected["method"]
                or actual.get("decoded_mapping_root") != expected["mapping_root"]
            ):
                raise ValueError(f"verified model receipt is incomplete: {expected['model_id']}")
        elif status == "missing":
            missing = True
            if actual.get("error_code") != status or any(
                actual.get(key) is not None for key in
                ("actual_sha256", "actual_size_bytes", "decoded_method", "decoded_mapping_root")
            ):
                raise ValueError("missing model receipt fields are inconsistent")
        else:
            hard = True
            if status not in {
                "unsafe_path", "not_regular_file", "size_mismatch", "hash_mismatch",
                "decode_failed", "decoded_identity_mismatch",
            } or actual.get("error_code") != status:
                raise ValueError("model receipt status is invalid")
    expected_overall = "hard_failure" if hard else ("blocked" if missing else "verified")
    if receipt.get("overall_status") != expected_overall:
        raise ValueError("model receipt overall status mismatch")
    if require_all and expected_overall != "verified":
        raise ValueError("all ten models are not verified")
    return receipt


def _validate_image_rows(rows: list[dict[str, Any]], expected_count: int) -> None:
    keys = {"coco_image_id", "error_code", "exists", "filename", "perceptual_hash", "sha256", "size_bytes", "status"}
    if len(rows) != expected_count:
        raise ValueError("image manifest count mismatch")
    names = [row.get("filename") for row in rows]
    if names != sorted(set(names), key=lambda value: value.encode("utf-8")):
        raise ValueError("image manifest filename order/uniqueness mismatch")
    for row in rows:
        if set(row) != keys or not COCO_NAME.fullmatch(row["filename"]):
            raise ValueError("image manifest row schema mismatch")
        if row["coco_image_id"] != int(row["filename"][:-4]) or row["status"] not in IMAGE_STATUSES:
            raise ValueError("image manifest identity/status mismatch")
        if row["status"] == "ready":
            if (
                row["exists"] is not True or row["error_code"] is not None
                or not isinstance(row["size_bytes"], int) or row["size_bytes"] <= 0
                or not isinstance(row["sha256"], str) or not HEX64.fullmatch(row["sha256"])
                or not isinstance(row["perceptual_hash"], str) or not HEX16.fullmatch(row["perceptual_hash"])
            ):
                raise ValueError("ready image manifest row is incomplete")
        else:
            if (
                row["error_code"] != row["status"]
                or not isinstance(row["exists"], bool)
                or row["exists"] != (row["status"] != "missing")
            ):
                raise ValueError("failed image manifest status fields mismatch")
            if row["perceptual_hash"] is not None:
                raise ValueError("failed image manifest pHash must be null")
            if row["status"] == "decode_failed":
                if not isinstance(row["size_bytes"], int) or not isinstance(row["sha256"], str) or not HEX64.fullmatch(row["sha256"]):
                    raise ValueError("decode-failed image must retain size/SHA")
            elif row["size_bytes"] is not None or row["sha256"] is not None:
                raise ValueError("non-decode image failure must have null size/SHA")


def _expected_degenerate_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    allowed_types = (
        ("positive_pair_equal", "caption", "caption2"),
        ("pos1_equals_negative", "caption", "negative_caption"),
        ("pos2_equals_negative", "caption2", "negative_caption"),
    )
    output: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for row_index_value, row in enumerate(rows):
        kinds = [kind for kind, left, right in allowed_types if row[left] == row[right]]
        if not kinds:
            continue
        for kind in kinds:
            counts[kind] = counts.get(kind, 0) + 1
        output.append(
            {
                "row_index": row_index_value,
                "row_key": row["row_key"],
                "category": row["category"],
                "filename": row["filename"],
                "degenerate_types": kinds,
            }
        )
    return {
        "schema_version": 1,
        "degenerate_row_count": len(output),
        "affected_image_group_count": len({row["filename"] for row in output}),
        "type_counts": counts,
        "rows": output,
    }


def _validate_failure_report(
    report: dict[str, Any],
    canonical_rows: list[dict[str, Any]],
    *,
    overlength_only: bool,
) -> None:
    if set(report) != {"schema_version", "failure_count", "failures"} or report.get("schema_version") != 1:
        raise ValueError("input failure report schema mismatch")
    failures = report.get("failures")
    if not isinstance(failures, list) or report.get("failure_count") != len(failures):
        raise ValueError("input failure report count mismatch")
    required = {
        "row_index", "row_key", "model_mode", "caption_role", "full_length",
        "max_length", "reason_code", "detail",
    }
    order = []
    seen = set()
    for failure in failures:
        if not isinstance(failure, dict) or set(failure) != required:
            raise ValueError("input failure row schema mismatch")
        row_index_value = failure.get("row_index")
        if (
            not isinstance(row_index_value, int)
            or isinstance(row_index_value, bool)
            or not 0 <= row_index_value < len(canonical_rows)
            or failure.get("row_key") != canonical_rows[row_index_value]["row_key"]
            or failure.get("model_mode") not in ("lm_only", "vlm")
            or failure.get("caption_role") not in ("pos1", "pos2", "negative")
            or failure.get("max_length") != 450
            or not isinstance(failure.get("reason_code"), str)
            or not failure["reason_code"]
            or not isinstance(failure.get("detail"), str)
            or not failure["detail"]
        ):
            raise ValueError("input failure row identity/value mismatch")
        full_length = failure.get("full_length")
        if full_length is not None and (
            not isinstance(full_length, int) or isinstance(full_length, bool) or full_length < 0
        ):
            raise ValueError("input failure full_length is invalid")
        if overlength_only and (
            failure["reason_code"] != "overlength"
            or not isinstance(full_length, int)
            or full_length <= 450
        ):
            raise ValueError("overlength report contains a non-overlength failure")
        row = canonical_rows[row_index_value]
        if (
            "Traceback (most recent call last)" in failure["detail"]
            or any(row[key] and row[key] in failure["detail"] for key in ("caption", "caption2", "negative_caption"))
        ):
            raise ValueError("input failure detail discloses traceback or original caption")
        key = (
            row_index_value,
            failure["model_mode"],
            failure["caption_role"],
            failure["reason_code"],
        )
        if key in seen:
            raise ValueError("input failure rows are not unique")
        seen.add(key)
        order.append(key)
    if order != sorted(order):
        raise ValueError("input failure rows are not canonically ordered")


def validate_prepared_data(prepared_data_dir: str | Path) -> dict[str, Any]:
    root = Path(prepared_data_dir)
    data_path = root / "data_manifest.json"
    split_path = root / "split_manifest.json"
    data_sha = verify_sidecar(data_path, root=root)
    split_sha = verify_sidecar(split_path, root=root)
    data = _canonical_json(data_path, root=root)
    split = _canonical_json(split_path, root=root)
    if (
        sha256_bytes(canonical_json_bytes(data)) != data_sha
        or sha256_bytes(canonical_json_bytes(split)) != split_sha
    ):
        raise ValueError("prepared manifest changed after sidecar verification")
    split_keys = {
        "schema_version", "manifest_type", "protocol_version", "split_version", "split_salt",
        "split_rule", "independent_unit", "total_rows", "total_unique_images",
        "pilot_unique_images", "formal_unique_images", "canonical_row_commitment_sha256", "files",
    }
    if set(split) != split_keys or (
        split.get("schema_version"), split.get("manifest_type"), split.get("protocol_version"), split.get("split_version"),
        split.get("split_salt"), split.get("total_rows"), split.get("total_unique_images"),
        split.get("pilot_unique_images"), split.get("formal_unique_images")
    ) != (1, "phase3-split-manifest-v1", PROTOCOL_VERSION, SPLIT_VERSION, "phase3-v1", 4757, 1542, 153, 1389):
        raise ValueError("split manifest frozen fields mismatch")
    if (
        split.get("split_rule") != "sha256('phase3-v1|'+filename) first16hex mod10; zero=pilot"
        or split.get("independent_unit") != "unique_image_filename_group"
    ):
        raise ValueError("split manifest rule/unit mismatch")
    logical_paths = {
        "canonical_jsonl": ("sugarcrepe_pp_canonical.jsonl", 4757),
        "canonical_row_index": ("canonical_row_index.jsonl", 4757),
        "pilot_jsonl": ("sugarcrepe_pp_pilot.jsonl", None),
        "formal_jsonl": ("sugarcrepe_pp_formal.jsonl", None),
        "pilot_filenames": ("pilot_filenames.txt", 153),
        "formal_filenames": ("formal_filenames.txt", 1389),
    }
    files = split.get("files")
    if (
        not isinstance(files, list)
        or {row.get("logical_name") for row in files} != set(logical_paths)
        or [row.get("relative_path") for row in files]
        != sorted((value[0] for value in logical_paths.values()), key=lambda value: value.encode("utf-8"))
    ):
        raise ValueError("split manifest file set mismatch")
    for entry in files:
        expected_path, count = logical_paths[entry["logical_name"]]
        if entry.get("relative_path") != expected_path:
            raise ValueError("split manifest logical path mismatch")
        _bound_file(root, entry, row_count=count)

    data_keys = {
        "schema_version", "manifest_type", "protocol_version", "split_version", "dataset_repo",
        "dataset_revision", "dataset_split", "source_files", "split_manifest", "artifacts",
        "canonical_row_commitment_sha256", "p_hash_environment", "global_image_status",
        "smoke_image_status", "coco_provenance_validation", "counts", "exclusion_rule",
    }
    if set(data) != data_keys or (
        data.get("schema_version"), data.get("manifest_type"), data.get("protocol_version"),
        data.get("split_version"), data.get("dataset_repo"), data.get("dataset_revision"), data.get("dataset_split")
    ) != (1, "phase3-data-manifest-v2", PROTOCOL_VERSION, SPLIT_VERSION, REPO_ID, REVISION, SPLIT):
        raise ValueError("data manifest frozen fields mismatch")
    if data.get("p_hash_environment") != PHASH_ENVIRONMENT:
        raise ValueError("pHash environment mismatch")
    if (
        data.get("coco_provenance_validation") != "user_attestation_plus_frozen_per_file_sha256"
        or data.get("exclusion_rule") != "data_manifest.json and data_manifest.sha256 are excluded"
    ):
        raise ValueError("data provenance/exclusion rule mismatch")
    if data.get("split_manifest") != {"relative_path": "split_manifest.json", "size_bytes": len(snapshot_file(split_path, root=root)), "sha256": split_sha}:
        raise ValueError("data/split manifest binding mismatch")
    expected_sources = [(config, path, count, digest) for config, path, count, digest in SOURCES]
    sources = data.get("source_files")
    if not isinstance(sources, list) or len(sources) != 5:
        raise ValueError("data source file count mismatch")
    for actual, expected in zip(sources, expected_sources):
        config, relative, count, digest = expected
        if set(actual) != {"config", "repository_relative_path", "row_count", "size_bytes", "sha256"} or (
            actual["config"], actual["repository_relative_path"], actual["row_count"], actual["sha256"]
        ) != (config, relative, count, digest) or not isinstance(actual["size_bytes"], int) or actual["size_bytes"] <= 0:
            raise ValueError("data source binding mismatch")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or artifacts != sorted(artifacts, key=lambda row: row["relative_path"].encode("utf-8")):
        raise ValueError("data artifact inventory order mismatch")
    actual_artifacts = tuple(sorted(
        (path.name for path in root.iterdir()
         if path.is_file() and path.name not in ("data_manifest.json", "data_manifest.sha256")),
        key=lambda value: value.encode("utf-8"),
    ))
    if actual_artifacts != EXPECTED_DATA_ARTIFACTS or tuple(
        row.get("relative_path") for row in artifacts
    ) != EXPECTED_DATA_ARTIFACTS:
        raise ValueError("data artifact inventory set mismatch")
    for entry in artifacts:
        _bound_file(root, entry)

    canonical_rows = canonical_jsonl(root / "sugarcrepe_pp_canonical.jsonl", root=root)
    index_rows = canonical_jsonl(root / "canonical_row_index.jsonl", root=root)
    canonical_keys = {"caption", "caption2", "category", "filename", "negative_caption", "numeric_id", "row_key"}
    frozen_categories = [row[0] for row in SOURCES]
    if len(canonical_rows) != 4757:
        raise ValueError("canonical row count mismatch")
    for row in canonical_rows:
        if (
            set(row) != canonical_keys
            or row["category"] not in frozen_categories
            or not isinstance(row["numeric_id"], int) or isinstance(row["numeric_id"], bool) or row["numeric_id"] < 0
            or row["row_key"] != f"{row['category']}:{row['numeric_id']}"
            or not COCO_NAME.fullmatch(row["filename"])
            or any(not isinstance(row[key], str) for key in ("caption", "caption2", "negative_caption"))
        ):
            raise ValueError("canonical SugarCrepe++ row schema/identity mismatch")
    category_counts = {category: sum(row["category"] == category for row in canonical_rows) for category in frozen_categories}
    if category_counts != {category: count for category, _, count, _ in SOURCES}:
        raise ValueError("canonical category counts mismatch")
    expected_index = row_index(canonical_rows)
    if index_rows != expected_index or canonical_row_commitment(index_rows) != split["canonical_row_commitment_sha256"]:
        raise ValueError("canonical row index/commitment mismatch")
    expected_order = sorted(canonical_rows, key=lambda row: (row["category"].encode("utf-8"), int(row["numeric_id"]), row["filename"].encode("utf-8")))
    if canonical_rows != expected_order or len({row["row_key"] for row in canonical_rows}) != 4757:
        raise ValueError("canonical row ordering/uniqueness mismatch")
    pilot_names_raw = snapshot_file(root / "pilot_filenames.txt", root=root)
    formal_names_raw = snapshot_file(root / "formal_filenames.txt", root=root)
    pilot_names = pilot_names_raw.decode("utf-8").splitlines()
    formal_names = formal_names_raw.decode("utf-8").splitlines()
    if (
        len(pilot_names) != 153 or len(formal_names) != 1389
        or pilot_names != sorted(set(pilot_names), key=lambda value: value.encode("utf-8"))
        or formal_names != sorted(set(formal_names), key=lambda value: value.encode("utf-8"))
        or set(pilot_names) & set(formal_names)
    ):
        raise ValueError("filename split membership mismatch")
    if (
        pilot_names_raw != ("\n".join(pilot_names) + "\n").encode("utf-8")
        or formal_names_raw != ("\n".join(formal_names) + "\n").encode("utf-8")
    ):
        raise ValueError("filename list serialization mismatch")
    for name in pilot_names:
        digest = hashlib.sha256(("phase3-v1|" + name).encode("utf-8")).hexdigest()
        if int(digest[:16], 16) % 10 != 0:
            raise ValueError("pilot filename violates the frozen hash rule")
    for name in formal_names:
        digest = hashlib.sha256(("phase3-v1|" + name).encode("utf-8")).hexdigest()
        if int(digest[:16], 16) % 10 == 0:
            raise ValueError("formal filename violates the frozen hash rule")
    canonical_names = {row["filename"] for row in canonical_rows}
    if set(pilot_names) | set(formal_names) != canonical_names:
        raise ValueError("filename split does not cover canonical image groups")
    pilot_rows = canonical_jsonl(root / "sugarcrepe_pp_pilot.jsonl", root=root)
    formal_rows = canonical_jsonl(root / "sugarcrepe_pp_formal.jsonl", root=root)
    if pilot_rows != [row for row in canonical_rows if row["filename"] in set(pilot_names)]:
        raise ValueError("pilot JSONL is not the canonical filtered subset")
    if formal_rows != [row for row in canonical_rows if row["filename"] in set(formal_names)]:
        raise ValueError("formal JSONL is not the canonical filtered subset")

    image_rows = canonical_jsonl(root / "coco_referenced_images_manifest.jsonl", root=root)
    pilot_images = canonical_jsonl(root / "coco_pilot_images_manifest.jsonl", root=root)
    formal_images = canonical_jsonl(root / "coco_formal_images_manifest.jsonl", root=root)
    _validate_image_rows(image_rows, 1542)
    _validate_image_rows(pilot_images, 153)
    _validate_image_rows(formal_images, 1389)
    image_by_name = {row["filename"]: row for row in image_rows}
    if pilot_images != [image_by_name[name] for name in pilot_names] or formal_images != [image_by_name[name] for name in formal_names]:
        raise ValueError("split image manifests are not exact full-manifest subsets")
    if data["canonical_row_commitment_sha256"] != split["canonical_row_commitment_sha256"]:
        raise ValueError("data/split row commitment mismatch")
    diagnostics = _canonical_json(root / "data_diagnostics.json", root=root)
    count_keys = {
        "source_file_count", "config_count", "row_count", "unique_image_count",
        "pilot_unique_images", "formal_unique_images", "image_status_counts",
        "degenerate_row_count", "degenerate_group_count", "degenerate_type_row_counts",
        "degenerate_type_group_counts", "overlength_count", "input_invariant_failure_count",
    }
    if (
        set(diagnostics) != {"schema_version", "p_hash_environment", "canonical_row_commitment_sha256"} | count_keys
        or diagnostics.get("schema_version") != 1
        or diagnostics.get("p_hash_environment") != PHASH_ENVIRONMENT
        or not isinstance(data.get("counts"), dict)
        or set(data["counts"]) != count_keys
    ):
        raise ValueError("data diagnostics schema/environment mismatch")
    diagnostic_counts = {key: value for key, value in diagnostics.items() if key not in {"schema_version", "p_hash_environment", "canonical_row_commitment_sha256"}}
    if data.get("counts") != diagnostic_counts or diagnostics.get("canonical_row_commitment_sha256") != split["canonical_row_commitment_sha256"]:
        raise ValueError("data diagnostics/count binding mismatch")
    image_status_counts = {status: sum(row["status"] == status for row in image_rows) for status in IMAGE_STATUSES}
    expected_global = next(
        (status for status in ("unsafe_path", "decode_failed", "unreadable", "missing") if image_status_counts[status]),
        "ready",
    )
    expected_smoke = "ready" if all(image_by_name[name]["status"] == "ready" for name in pilot_names[:8]) else "blocked"
    if (
        data.get("global_image_status") != expected_global
        or data.get("smoke_image_status") != expected_smoke
        or diagnostic_counts.get("image_status_counts") != image_status_counts
    ):
        raise ValueError("image status summaries mismatch")
    missing_names = [row["filename"] for row in image_rows if row["status"] == "missing"]
    if _canonical_json(root / "missing_images.json", root=root) != {
        "schema_version": 1, "missing_count": len(missing_names), "filenames": missing_names,
    }:
        raise ValueError("missing image summary mismatch")
    failed_images = [row for row in image_rows if row["status"] != "ready"]
    if _canonical_json(root / "image_failures.json", root=root) != {
        "schema_version": 1, "status_counts": image_status_counts, "failures": failed_images,
    }:
        raise ValueError("image failure summary mismatch")
    degenerates = _canonical_json(root / "degenerate_rows.json", root=root)
    overlength = _canonical_json(root / "overlength_rows.json", root=root)
    invariants = _canonical_json(root / "input_invariant_failures.json", root=root)
    _validate_failure_report(overlength, canonical_rows, overlength_only=True)
    _validate_failure_report(invariants, canonical_rows, overlength_only=False)
    if overlength.get("failures") != [
        row for row in invariants.get("failures", []) if row.get("reason_code") == "overlength"
    ]:
        raise ValueError("overlength report is not the exact invariant-report subset")
    if (
        degenerates != _expected_degenerate_report(canonical_rows)
        or diagnostic_counts.get("degenerate_row_count") != degenerates.get("degenerate_row_count")
        or diagnostic_counts.get("degenerate_group_count") != degenerates.get("affected_image_group_count")
        or diagnostic_counts.get("overlength_count") != overlength.get("failure_count")
        or diagnostic_counts.get("input_invariant_failure_count") != invariants.get("failure_count")
    ):
        raise ValueError("degenerate/input-invariant diagnostics mismatch")
    allowed_types = ("positive_pair_equal", "pos1_equals_negative", "pos2_equals_negative")
    observed_type_counts = {kind: 0 for kind in allowed_types}
    observed_type_groups: dict[str, set[str]] = {kind: set() for kind in allowed_types}
    for row in degenerates.get("rows", []):
        types = row.get("degenerate_types")
        if types != [kind for kind in allowed_types if kind in types] or len(types) != len(set(types)):
            raise ValueError("degenerate type order/uniqueness mismatch")
        for kind in types:
            observed_type_counts[kind] += 1
            observed_type_groups[kind].add(row["filename"])
    observed_type_counts = {key: value for key, value in observed_type_counts.items() if value}
    observed_type_group_counts = {key: len(value) for key, value in observed_type_groups.items() if value}
    if (
        degenerates.get("type_counts") != observed_type_counts
        or diagnostic_counts.get("degenerate_type_row_counts") != observed_type_counts
        or diagnostic_counts.get("degenerate_type_group_counts") != observed_type_group_counts
        or diagnostic_counts.get("source_file_count") != 5
        or diagnostic_counts.get("config_count") != 5
        or diagnostic_counts.get("row_count") != 4757
        or diagnostic_counts.get("unique_image_count") != 1542
        or diagnostic_counts.get("pilot_unique_images") != 153
        or diagnostic_counts.get("formal_unique_images") != 1389
    ):
        raise ValueError("data diagnostics frozen count/type summary mismatch")
    return {
        "data_manifest": data, "split_manifest": split, "data_manifest_sha256": data_sha,
        "split_manifest_sha256": split_sha, "canonical_rows": canonical_rows,
        "canonical_index": index_rows, "pilot_names": pilot_names, "formal_names": formal_names,
        "image_rows": image_rows, "pilot_images": pilot_images, "formal_images": formal_images,
    }


def validate_overlap_receipt(
    receipt_path: str | Path,
    *,
    split_manifest_path: str | Path,
    formal_image_manifest_path: str | Path,
) -> dict[str, Any]:
    path = Path(receipt_path)
    root = path.parent
    digest = verify_sidecar(path, root=root)
    receipt = _canonical_json(path, root=root)
    if sha256_bytes(canonical_json_bytes(receipt)) != digest:
        raise ValueError("overlap receipt changed after sidecar verification")
    required = {
        "schema_version", "receipt_type", "protocol_version", "split_version",
        "overlap_audit_input_sha256", "split_manifest_sha256", "formal_image_manifest_sha256",
        "training_coverage_manifest_sha256", "used_source_manifests", "overlap_review_sha256",
        "phash_spec_id", "formal_image_count", "excluded_formal_image_count",
        "certifying_formal_image_count", "scope_count", "coverage_complete",
        "phash_coverage_complete", "exact_match_count", "probable_pair_count",
        "probable_unreviewed_count", "probable_same_source_count",
        "probable_same_source_formal_count", "probable_not_same_source_count",
        "near_duplicate_pair_count", "text_match_count", "detail_files", "exclusion_files",
        "project_overlap_audit_status", "external_base_pretraining_overlap", "certificate_scope",
        "conditional_target_distribution",
    }
    if set(receipt) != required or (
        receipt.get("schema_version"), receipt.get("receipt_type"), receipt.get("protocol_version"),
        receipt.get("split_version"), receipt.get("phash_spec_id"), receipt.get("formal_image_count"), receipt.get("scope_count")
    ) != (1, "phase3_project_image_overlap_audit_v2", PROTOCOL_VERSION, SPLIT_VERSION, PHASH_SPEC_ID, 1389, 7):
        raise ValueError("overlap receipt schema/frozen fields mismatch")
    if receipt["split_manifest_sha256"] != sha256_bytes(snapshot_file(split_manifest_path)):
        raise ValueError("overlap/split manifest binding mismatch")
    if receipt["formal_image_manifest_sha256"] != sha256_bytes(snapshot_file(formal_image_manifest_path)):
        raise ValueError("overlap/formal image binding mismatch")
    detail_expected = {
        "exact_matches.jsonl": "exact_match_count",
        "probable_pairs.jsonl": "probable_pair_count",
        "near_duplicate_diagnostics.jsonl": "near_duplicate_pair_count",
        "text_match_diagnostics.jsonl": "text_match_count",
    }
    details = receipt.get("detail_files")
    if not isinstance(details, list) or {row.get("relative_path") for row in details} != set(detail_expected):
        raise ValueError("overlap detail file set mismatch")
    detail_rows = {}
    for entry in details:
        payload = _bound_file(root, entry, row_count=receipt[detail_expected[entry["relative_path"]]])
        rows = canonical_jsonl(root / entry["relative_path"], root=root)
        detail_rows[entry["relative_path"]] = rows
        pair_ids = [row.get("pair_id") for row in rows]
        if pair_ids != sorted(pair_ids) or len(pair_ids) != len(set(pair_ids)):
            raise ValueError("overlap detail pair order/uniqueness mismatch")
    exclusion_files = receipt.get("exclusion_files")
    if (
        not isinstance(exclusion_files, list)
        or [row.get("relative_path") for row in exclusion_files]
        != ["certifying_formal_filenames.txt", "excluded_formal_images.jsonl"]
    ):
        raise ValueError("overlap exclusion file set/order mismatch")
    expected_exclusion_counts = {
        "certifying_formal_filenames.txt": receipt.get("certifying_formal_image_count"),
        "excluded_formal_images.jsonl": receipt.get("excluded_formal_image_count"),
    }
    for entry in exclusion_files:
        _bound_file(root, entry, row_count=expected_exclusion_counts[entry["relative_path"]])
    excluded_rows = canonical_jsonl(root / "excluded_formal_images.jsonl", root=root)
    certifying_raw = snapshot_file(root / "certifying_formal_filenames.txt", root=root)
    certifying_names = certifying_raw.decode("utf-8").splitlines()
    formal_rows = canonical_jsonl(Path(formal_image_manifest_path), root=Path(formal_image_manifest_path).parent)
    formal_by_name = {row["filename"]: row for row in formal_rows}
    excluded_names = [row.get("filename") for row in excluded_rows]
    if (
        len(formal_by_name) != 1389
        or len(excluded_rows) != 44
        or len(certifying_names) != 1345
        or excluded_names != sorted(set(excluded_names), key=lambda value: value.encode("utf-8"))
        or certifying_names != sorted(set(certifying_names), key=lambda value: value.encode("utf-8"))
        or set(excluded_names) & set(certifying_names)
        or set(excluded_names) | set(certifying_names) != set(formal_by_name)
        or certifying_raw != ("\n".join(certifying_names) + "\n").encode("utf-8")
    ):
        raise ValueError("overlap exclusion partition mismatch")
    evidence_by_pair = {
        row["pair_id"]: (row["formal_filename"], "exact_identifier_match")
        for row in detail_rows["exact_matches.jsonl"]
    }
    evidence_by_pair.update({
        row["pair_id"]: (row["formal_filename"], "human_confirmed_same_source")
        for row in detail_rows["probable_pairs.jsonl"]
    })
    reviewed_decisions = {}
    if receipt.get("overlap_review_sha256") is not None:
        review_path = root / "overlap_review.json"
        review = _canonical_json(review_path, root=root)
        if (
            sha256_bytes(canonical_json_bytes(review)) != receipt.get("overlap_review_sha256")
            or set(review) != {"schema_version", "overlap_audit_input_sha256", "reviewer", "reviewed_at", "decisions"}
            or review.get("schema_version") != 1
            or review.get("overlap_audit_input_sha256") != receipt.get("overlap_audit_input_sha256")
        ):
            raise ValueError("overlap review receipt binding mismatch")
        reviewed_decisions = {
            row.get("pair_id"): row.get("decision")
            for row in review.get("decisions", [])
            if isinstance(row, dict)
        }
    for row in excluded_rows:
        if set(row) != {
            "filename", "formal_sha256", "formal_phash", "exclusion_bases", "supporting_pair_ids",
        }:
            raise ValueError("excluded formal image row schema mismatch")
        formal = formal_by_name.get(row["filename"])
        if formal is None or (row["formal_sha256"], row["formal_phash"]) != (
            formal["sha256"], formal["perceptual_hash"],
        ):
            raise ValueError("excluded formal image identity mismatch")
        pair_ids = row["supporting_pair_ids"]
        if (
            not isinstance(pair_ids, list)
            or pair_ids != sorted(set(pair_ids))
            or not pair_ids
            or any(not HEX64.fullmatch(str(pair_id)) for pair_id in pair_ids)
        ):
            raise ValueError("excluded formal supporting pair IDs invalid")
        expected_bases = sorted({
            evidence_by_pair[pair_id][1]
            for pair_id in pair_ids
            if pair_id in evidence_by_pair and evidence_by_pair[pair_id][0] == row["filename"]
        })
        if (
            any(
                pair_id not in evidence_by_pair
                or evidence_by_pair[pair_id][0] != row["filename"]
                for pair_id in pair_ids
            )
            or any(
                reviewed_decisions.get(pair_id) != "same_source_image"
                for pair_id in pair_ids
                if evidence_by_pair[pair_id][1] == "human_confirmed_same_source"
            )
            or len(expected_bases) == 0
            or row["exclusion_bases"] != expected_bases
        ):
            raise ValueError("excluded formal evidence binding mismatch")
    valid_statuses = {
        "probable_reencoded_duplicate_unresolved", "unknown",
        "approved_exclusion_count_mismatch", OVERLAP_PASS_STATUS,
    }
    if (
        receipt.get("project_overlap_audit_status") not in valid_statuses
        or receipt.get("external_base_pretraining_overlap") != "unknown"
        or receipt.get("certificate_scope") != "project_controlled_image_group_disjoint_certifying_subset_only"
        or receipt.get("conditional_target_distribution") != CONDITIONAL_TARGET_DISTRIBUTION
    ):
        raise ValueError("overlap receipt conclusion scope mismatch")
    if receipt.get("project_overlap_audit_status") == OVERLAP_PASS_STATUS and not (
        receipt.get("coverage_complete") is True
        and receipt.get("phash_coverage_complete") is True
        and receipt.get("exact_match_count") == 0
        and receipt.get("probable_unreviewed_count") == 0
        and receipt.get("probable_same_source_count") + receipt.get("probable_not_same_source_count")
        == receipt.get("probable_pair_count")
        and receipt.get("probable_same_source_formal_count") == 44
        and receipt.get("excluded_formal_image_count") == 44
        and receipt.get("certifying_formal_image_count") == 1345
        and isinstance(receipt.get("overlap_review_sha256"), str)
        and HEX64.fullmatch(receipt["overlap_review_sha256"])
    ):
        raise ValueError("passing overlap status is not supported by receipt counts")
    return {
        "receipt": receipt,
        "receipt_sha256": digest,
        "excluded_rows": excluded_rows,
        "certifying_names": certifying_names,
    }
