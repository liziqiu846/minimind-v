"""Frozen input, image, and model-registry validation."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_v6.scoring.common import (
    REPO_ROOT,
    canonical_jsonl_bytes,
    read_json,
    read_jsonl,
    sha256_bytes,
    sha256_file,
    utf8_key,
)


AUDIT_PATH = REPO_ROOT / "experiments/phase3_v6/audit_v2/contrast_hull_audit.jsonl"
AUDIT_SUMMARY_PATH = (
    REPO_ROOT / "experiments/phase3_v6/audit_v2/contrast_hull_summary.json"
)
MISMATCH_PATH = (
    REPO_ROOT
    / "experiments/phase3_v6/mismatch_audit/mismatch_manifest_k5.jsonl"
)
MISMATCH_SUMMARY_PATH = (
    REPO_ROOT / "experiments/phase3_v6/mismatch_audit/mismatch_summary.json"
)
V5_PROTOCOL_PATH = REPO_ROOT / "experiments/phase3/phase3_protocol_frozen_v5.json"
MODEL_REGISTRY_PATH = (
    REPO_ROOT / "experiments/phase3/phase3_expected_model_registry.json"
)
STAGE2_AUTHORITY_PATH = (
    REPO_ROOT / "experiments/phase3/phase3_stage2_authority_manifest_v2.json"
)

EXPECTED_INPUT_SHA256 = {
    str(AUDIT_PATH.relative_to(REPO_ROOT)): (
        "34f592eec832fba78999a2084dcb871a3d6a2e5b015817cc8d598082797d9a4d"
    ),
    str(AUDIT_SUMMARY_PATH.relative_to(REPO_ROOT)): (
        "3eaddd46c68947ed9cca6e125e4b5ca112ec4a48d88a1fa789dbb3e72612d479"
    ),
    str(MISMATCH_PATH.relative_to(REPO_ROOT)): (
        "a7298df9fb57ca24888f3564a38f38357ee144b27d32faab9d07955ff2b30331"
    ),
    str(MISMATCH_SUMMARY_PATH.relative_to(REPO_ROOT)): (
        "f542c8143582b869b1ae6eb5ffc2df43ba68f11550fc38ebec461fcd053a5d45"
    ),
}
EXPECTED_ASSIGNMENT_CORE_SHA256 = (
    "fb4808db202e9191172e80a96b7de4d6343f1380393535ff2c6f32224cbb635b"
)
EXPECTED_VALID_RECORD_COUNT = 4107
EXPECTED_VALID_IMAGE_COUNT = 1343
EXPECTED_MISMATCH_IMAGE_COUNT = 1345
EXPECTED_MODEL_IDS = [
    "M0-root-43101",
    "M0-root-43102",
    "M0-root-43103",
    "M1-root-none",
    "M2-root-43101",
    "M2-root-43102",
    "M2-root-43103",
    "M3-root-43101",
    "M3-root-43102",
    "M3-root-43103",
]
EXCLUDED_SECOND_ROUND_CATEGORIES = {
    "token_mapping_problem",
    "surface_only_or_degenerate",
    "invalid_sample",
}
NEGATIVE_TYPES = [
    "replace_attribute",
    "replace_object",
    "replace_relation",
    "swap_atribute",
    "swap_object",
]


def verify_frozen_input_hashes() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_INPUT_SHA256.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"frozen input is absent: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(
                f"frozen input SHA-256 mismatch for {relative}: "
                f"expected {expected}, observed {actual}"
            )
        observed[relative] = actual
    return observed


def is_valid_record(row: Mapping[str, Any]) -> bool:
    scope = row.get("scope_flags")
    return bool(
        isinstance(scope, Mapping)
        and scope.get("certifying_formal") is True
        and row.get("second_round_category")
        not in EXCLUDED_SECOND_ROUND_CATEGORIES
        and int(row.get("positive_hull_model_token_count", 0)) >= 1
        and int(row.get("negative_hull_model_token_count", 0)) >= 1
        and row.get("normalized_positive_reconstruction_ok") is True
        and row.get("normalized_negative_reconstruction_ok") is True
        and row.get("token_boundary_mapping_ok") is True
    )


def _assignment_core_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    core_rows = []
    for row in rows:
        target = row.get("target_filename")
        rounds = row.get("donor_rounds")
        if not isinstance(target, str) or not isinstance(rounds, list):
            raise ValueError("mismatch row lacks target filename or donor rounds")
        if [entry.get("round_id") for entry in rounds] != [1, 2, 3, 4, 5]:
            raise ValueError(f"donor round order mismatch for {target}")
        for entry in rounds:
            donor = entry.get("donor_filename")
            if not isinstance(donor, str):
                raise ValueError(f"invalid donor filename for {target}")
            core_rows.append(
                {
                    "round_id": int(entry["round_id"]),
                    "target_filename": target,
                    "donor_filename": donor,
                }
            )
    return sha256_bytes(canonical_jsonl_bytes(core_rows))


def _validate_mismatch_rows(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if len(rows) != EXPECTED_MISMATCH_IMAGE_COUNT:
        raise ValueError(
            f"mismatch target count is {len(rows)}, expected "
            f"{EXPECTED_MISMATCH_IMAGE_COUNT}"
        )
    targets = [str(row.get("target_filename")) for row in rows]
    if targets != sorted(targets, key=utf8_key) or len(set(targets)) != len(targets):
        raise ValueError("mismatch targets are not unique UTF-8-bytewise sorted")

    mismatch_by_target: dict[str, dict[str, Any]] = {}
    image_entries: dict[str, dict[str, Any]] = {}
    for row in rows:
        target = str(row["target_filename"])
        rounds = row["donor_rounds"]
        donor_names = [str(entry["donor_filename"]) for entry in rounds]
        if len(set(donor_names)) != 5 or target in donor_names:
            raise ValueError(f"invalid distinct donors for {target}")
        mismatch_by_target[target] = dict(row)
        target_entry = {
            "filename": target,
            "image_path": row["target_image_path"],
            "image_sha256": row["target_image_sha256"],
            "normalized_pixel_sha256": row["target_normalized_pixel_sha256"],
            "image_size_bytes": int(row["target_image_size_bytes"]),
        }
        existing = image_entries.setdefault(target, target_entry)
        if existing != target_entry:
            raise ValueError(f"inconsistent target image metadata for {target}")
        for donor in rounds:
            name = str(donor["donor_filename"])
            entry = {
                "filename": name,
                "image_path": donor["donor_image_path"],
                "image_sha256": donor["donor_image_sha256"],
                "normalized_pixel_sha256": donor[
                    "donor_normalized_pixel_sha256"
                ],
                "image_size_bytes": int(donor["donor_image_size_bytes"]),
            }
            existing = image_entries.setdefault(name, entry)
            if existing != entry:
                raise ValueError(f"inconsistent donor image metadata for {name}")
    if len(image_entries) != EXPECTED_MISMATCH_IMAGE_COUNT:
        raise ValueError(
            f"mismatch image union is {len(image_entries)}, expected "
            f"{EXPECTED_MISMATCH_IMAGE_COUNT}"
        )
    return mismatch_by_target, image_entries


def verify_image_files(image_entries: Mapping[str, Mapping[str, Any]]) -> None:
    for filename in sorted(image_entries, key=utf8_key):
        row = image_entries[filename]
        path = Path(str(row["image_path"]))
        if not path.is_file():
            raise FileNotFoundError(f"frozen image is absent: {path}")
        if path.name != filename:
            raise ValueError(f"image path/name mismatch for {filename}: {path}")
        size = path.stat().st_size
        if size != int(row["image_size_bytes"]):
            raise ValueError(f"image byte size mismatch for {filename}")
        digest = sha256_file(path)
        if digest != row["image_sha256"]:
            raise ValueError(f"image SHA-256 mismatch for {filename}")


def verify_model_registry() -> dict[str, Any]:
    from experiments.phase3.stage2_adapter_loader import MODELS

    v5 = read_json(V5_PROTOCOL_PATH)
    ordered = v5.get("models", {}).get("ordered_model_ids")
    if ordered != EXPECTED_MODEL_IDS:
        raise ValueError("v5 ordered model IDs differ from the frozen v6 list")
    registry = read_json(MODEL_REGISTRY_PATH)
    registry_models = registry.get("models")
    if not isinstance(registry_models, list):
        raise ValueError("model registry has no models list")
    if [row.get("model_id") for row in registry_models] != EXPECTED_MODEL_IDS:
        raise ValueError("expected model registry order/content differs from v5")
    loader_models = [dict(row) for row in MODELS]
    if [row["model_id"] for row in loader_models] != EXPECTED_MODEL_IDS:
        raise ValueError("Stage2 loader model order differs from v5")
    compared_fields = (
        "model_id",
        "method",
        "mapping_root",
        "artifact_relative_path",
        "artifact_size_bytes",
        "artifact_sha256",
        "description_bits",
    )
    for registry_row, loader_row in zip(registry_models, loader_models):
        if any(
            registry_row.get(field) != loader_row.get(field)
            for field in compared_fields
        ):
            raise ValueError(
                f"loader/registry mismatch for {registry_row.get('model_id')}"
            )
    return registry


def load_and_validate_frozen_inputs(
    *, verify_images: bool = False
) -> dict[str, Any]:
    hashes = verify_frozen_input_hashes()
    audit_rows = read_jsonl(AUDIT_PATH)
    sample_ids = [row.get("sample_id") for row in audit_rows]
    if (
        any(not isinstance(value, str) or not value for value in sample_ids)
        or len(sample_ids) != len(set(sample_ids))
    ):
        raise ValueError("audit sample IDs are missing or duplicated")

    valid_rows = [dict(row) for row in audit_rows if is_valid_record(row)]
    valid_rows.sort(
        key=lambda row: (
            utf8_key(str(row["filename"])),
            utf8_key(str(row["sample_id"])),
        )
    )
    valid_filenames = {str(row["filename"]) for row in valid_rows}
    if len(valid_rows) != EXPECTED_VALID_RECORD_COUNT:
        raise ValueError(
            f"valid record count is {len(valid_rows)}, expected "
            f"{EXPECTED_VALID_RECORD_COUNT}"
        )
    if len(valid_filenames) != EXPECTED_VALID_IMAGE_COUNT:
        raise ValueError(
            f"valid image count is {len(valid_filenames)}, expected "
            f"{EXPECTED_VALID_IMAGE_COUNT}"
        )
    observed_types = set(row["negative_type"] for row in valid_rows)
    if observed_types != set(NEGATIVE_TYPES):
        raise ValueError(f"unexpected negative types: {sorted(observed_types)}")
    for row in valid_rows:
        maximum = max(
            float(row["positive_hull_token_coverage"]),
            float(row["negative_hull_token_coverage"]),
        )
        if abs(maximum - float(row["maximum_hull_token_coverage"])) > 1e-15:
            raise ValueError(
                f"maximum hull token coverage mismatch for {row['sample_id']}"
            )

    mismatch_rows = read_jsonl(MISMATCH_PATH)
    mismatch_by_target, image_entries = _validate_mismatch_rows(mismatch_rows)
    if not valid_filenames.issubset(mismatch_by_target):
        raise ValueError("a valid target filename is absent from mismatch manifest")
    assignment_sha = _assignment_core_sha256(mismatch_rows)
    if assignment_sha != EXPECTED_ASSIGNMENT_CORE_SHA256:
        raise ValueError(
            f"assignment core SHA mismatch: expected "
            f"{EXPECTED_ASSIGNMENT_CORE_SHA256}, observed {assignment_sha}"
        )
    mismatch_summary = read_json(MISMATCH_SUMMARY_PATH)
    if (
        mismatch_summary.get("determinism_checks", {}).get(
            "assignment_core_sha256"
        )
        != EXPECTED_ASSIGNMENT_CORE_SHA256
    ):
        raise ValueError("mismatch summary assignment core SHA mismatch")
    if int(mismatch_summary.get("effective_v6_image_count", -1)) != len(
        valid_filenames
    ):
        raise ValueError("mismatch summary effective image count mismatch")
    if verify_images:
        verify_image_files(image_entries)

    registry = verify_model_registry()
    return {
        "input_sha256": hashes,
        "assignment_core_sha256": assignment_sha,
        "audit_row_count": len(audit_rows),
        "valid_rows": valid_rows,
        "valid_record_count": len(valid_rows),
        "valid_filenames": sorted(valid_filenames, key=utf8_key),
        "valid_image_count": len(valid_filenames),
        "mismatch_rows": mismatch_rows,
        "mismatch_by_target": mismatch_by_target,
        "image_entries": image_entries,
        "mismatch_image_count": len(image_entries),
        "negative_type_counts": dict(
            sorted(Counter(row["negative_type"] for row in valid_rows).items())
        ),
        "second_round_category_counts": dict(
            sorted(
                Counter(
                    row["second_round_category"] for row in valid_rows
                ).items()
            )
        ),
        "local_hull_record_count": sum(
            float(row["maximum_hull_token_coverage"]) <= 0.75
            for row in valid_rows
        ),
        "local_hull_image_count": len(
            {
                row["filename"]
                for row in valid_rows
                if float(row["maximum_hull_token_coverage"]) <= 0.75
            }
        ),
        "model_registry": registry,
    }


def verify_stage2_artifacts(artifact_root: str | Path) -> list[dict[str, Any]]:
    from experiments.phase3.stage2_adapter_loader import (
        MODELS,
        snapshot_and_verify,
        verify_stage2_source_integrity,
    )

    verify_stage2_source_integrity(
        str(REPO_ROOT / "experiments/stage2_protocol_v2.json")
    )
    output = []
    for expected in MODELS:
        payload, _, metadata = snapshot_and_verify(artifact_root, expected)
        digest = hashlib.sha256(payload).hexdigest()
        output.append(
            {
                "model_id": expected["model_id"],
                "method": expected["method"],
                "mapping_root": expected["mapping_root"],
                "checkpoint_path": str(
                    (Path(artifact_root) / expected["artifact_relative_path"])
                    .resolve()
                ),
                "checkpoint_size_bytes": len(payload),
                "checkpoint_sha256": digest,
                "decoded_model_group": metadata["model_group"],
                "decoded_mapping_root": metadata["mapping_root"],
                "adapter_config": {
                    key: metadata.get(key)
                    for key in sorted(metadata)
                    if key
                    not in {
                        "coordinate_tensors",
                    }
                },
            }
        )
    if [row["model_id"] for row in output] != EXPECTED_MODEL_IDS:
        raise ValueError("verified Stage2 artifact order differs from v5")
    return output

