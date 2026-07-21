#!/usr/bin/env python3
"""Pure-CPU verifier for a self-contained Phase 3 public bundle."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.aggregate_by_image import (
    MAIN_METRICS, aggregate_rows, empirical_metric_means, m0_row_metrics, visual_row_metrics,
)
from experiments.phase3.artifact_validation import validate_overlap_receipt
from experiments.phase3.canonical_io import canonical_json_bytes, content_hash, inventory_files, load_json_snapshot, load_jsonl_snapshot, sha256_bytes, snapshot_file, validate_disjoint_roots
from experiments.phase3.nll_diagnostics import summarize_nll, validate_nll_store
from experiments.phase3.phase3_protocol import Phase3Protocol
from experiments.phase3.statistical_bounds import compression_upper, definition_constant, hoeffding_upper
from experiments.phase3.runner_common import (
    FORMAL_CONFIDENCE_STATEMENT, FORMAL_INDEPENDENCE_DISCLOSURE, NLL_DISCLAIMER,
    _degenerate_sensitivity,
)
from experiments.phase3.stage2_adapter_loader import MODELS
from experiments.phase3.status import Phase3ArgumentParser, Phase3HardFailure, execute_with_status, require_status_output


ATOL = 1e-10
RTOL = 1e-10
_SECRET = re.compile(r"(?i)(?:hf_|sk-|api[_-]?key|access[_-]?token|authorization\s*[:=])")


def _jsonl(path: Path, root: Path) -> list[dict[str, Any]]:
    rows = load_jsonl_snapshot(path, root=root)
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"JSONL rows must be objects: {path.name}")
    return rows


def _close(actual: Any, expected: Any, path: str = "root") -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError(f"object keys mismatch at {path}")
        for key in expected:
            _close(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError(f"list mismatch at {path}")
        for index, (left, right) in enumerate(zip(actual, expected)):
            _close(left, right, f"{path}[{index}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if not isinstance(actual, (int, float)) or not math.isclose(float(actual), float(expected), abs_tol=ATOL, rel_tol=RTOL):
            raise ValueError(f"numeric mismatch at {path}: {actual!r} != {expected!r}")
    elif actual != expected:
        raise ValueError(f"value mismatch at {path}: {actual!r} != {expected!r}")


def _validate_privacy(root: Path, files: list[dict[str, Any]]) -> None:
    for row in files:
        relative = str(row["relative_path"])
        if relative.startswith("/") or "\\" in relative or ".." in Path(relative).parts:
            raise ValueError(f"unsafe bundle path: {relative}")
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"bundle member is not a regular file: {relative}")
        if path.suffix.lower() in (".json", ".jsonl", ".txt", ".md"):
            text = snapshot_file(path, root=root).decode("utf-8")
            if _SECRET.search(text):
                raise ValueError(f"secret-like text in {relative}")
            if re.search(r"(?<![A-Za-z0-9_])/(?:home|Users|root|mnt|srv|opt|var|tmp)/", text):
                raise ValueError(f"host absolute path in {relative}")


def _validate_bundled_model_evidence(bundle_dir: Path) -> dict[str, Any]:
    registry_path = bundle_dir / "models/expected_model_registry.json"
    receipt_path = bundle_dir / "models/model_verification_receipt.json"
    authority_paths = sorted((bundle_dir / "models").glob("phase3_stage2_authority_manifest_*.json"))
    if len(authority_paths) != 1:
        raise ValueError("bundle must contain exactly one Stage 2 authority manifest")
    registry = load_json_snapshot(registry_path, root=bundle_dir)
    receipt = load_json_snapshot(receipt_path, root=bundle_dir)
    registry_keys = {
        "artifact_batch_id", "authority_id", "authority_manifest_sha256", "decoder_id",
        "decoder_source_sha256", "model_count", "models", "recovery_verification_sha256",
        "registry_id", "rerun_source_commit", "schema_version", "stage2_protocol_sha256",
        "stage2_reference_commit",
    }
    registry_model_keys = {
        "model_id", "method", "mapping_root", "artifact_relative_path", "artifact_sha256",
        "artifact_size_bytes", "description_bits", "stage2_result_source",
    }
    if (
        set(registry) != registry_keys
        or registry.get("schema_version") != 2
        or registry.get("registry_id") != "phase3-v4-expected-model-registry-v2"
        or registry.get("artifact_batch_id") != "stage2-v2-rerun-20260721"
        or registry.get("model_count") != 10
        or not isinstance(registry.get("models"), list)
        or len(registry["models"]) != 10
        or registry.get("authority_manifest_sha256")
        != sha256_bytes(snapshot_file(authority_paths[0], root=bundle_dir))
    ):
        raise ValueError("bundled expected-model registry is invalid")
    for actual, expected in zip(registry["models"], MODELS):
        if (
            set(actual) != registry_model_keys
            or any(actual.get(key) != value for key, value in expected.items())
            or actual.get("stage2_result_source")
            != {"model_group": expected["method"], "mapping_root": expected["mapping_root"]}
        ):
            raise ValueError("bundled expected-model registry row is invalid")

    receipt_keys = {
        "schema_version", "receipt_type", "artifact_batch_id", "authority_id",
        "stage2_reference_commit", "rerun_source_commit", "recovery_verification_sha256",
        "expected_model_registry_sha256", "authority_manifest_sha256", "decoder_id",
        "decoder_source_sha256", "model_count", "overall_status", "models",
    }
    receipt_model_keys = {
        "model_id", "method", "mapping_root", "resolved_relative_path", "expected_sha256",
        "actual_sha256", "expected_size_bytes", "actual_size_bytes", "decoded_method",
        "decoded_mapping_root", "status", "error_code",
    }
    if (
        set(receipt) != receipt_keys
        or receipt.get("schema_version") != 2
        or receipt.get("receipt_type") != "phase3_stage2_artifact_verification_v3"
        or receipt.get("artifact_batch_id") != registry["artifact_batch_id"]
        or receipt.get("authority_manifest_sha256") != registry["authority_manifest_sha256"]
        or receipt.get("expected_model_registry_sha256")
        != sha256_bytes(snapshot_file(registry_path, root=bundle_dir))
        or receipt.get("model_count") != 10
        or receipt.get("overall_status") != "verified"
        or not isinstance(receipt.get("models"), list)
        or len(receipt["models"]) != 10
        or any(
            receipt.get(key) != registry.get(key)
            for key in (
                "artifact_batch_id", "authority_id", "stage2_reference_commit",
                "rerun_source_commit", "recovery_verification_sha256",
                "authority_manifest_sha256", "decoder_id", "decoder_source_sha256",
            )
        )
    ):
        raise ValueError("bundled model-verification receipt is invalid")
    for actual, expected in zip(receipt["models"], registry["models"]):
        frozen = {
            "model_id": expected["model_id"],
            "method": expected["method"],
            "mapping_root": expected["mapping_root"],
            "resolved_relative_path": expected["artifact_relative_path"],
            "expected_sha256": expected["artifact_sha256"],
            "actual_sha256": expected["artifact_sha256"],
            "expected_size_bytes": expected["artifact_size_bytes"],
            "actual_size_bytes": expected["artifact_size_bytes"],
            "decoded_method": expected["method"],
            "decoded_mapping_root": expected["mapping_root"],
            "status": "verified",
            "error_code": None,
        }
        if set(actual) != receipt_model_keys or actual != frozen:
            raise ValueError("bundled model-verification receipt row is invalid")
    return registry


def _validate_bundled_protocol(
    bundle_dir: Path,
    run_manifest: dict[str, Any],
) -> Phase3Protocol:
    candidates = sorted(
        path for path in (bundle_dir / "protocol").glob("phase3_protocol_*.json")
        if path.name != "phase3_code_manifest_v2.json"
    )
    if len(candidates) != 1:
        raise ValueError("bundle must contain exactly one Phase 3 protocol")
    protocol = Phase3Protocol.load(candidates[0])
    if run_manifest["run_mode"] in ("pilot", "formal"):
        protocol.require_frozen()
    bindings = {
        "phase3_code_manifest_sha256": "phase3_code_manifest_sha256",
        "stage2_authority_manifest_sha256": "stage2_authority_manifest_sha256",
        "expected_model_registry_sha256": "expected_model_registry_sha256",
        "data_manifest_sha256": "data_manifest_sha256",
        "split_manifest_sha256": "split_manifest_sha256",
    }
    if any(
        protocol.payload.get(protocol_key) != run_manifest.get(run_key)
        for protocol_key, run_key in bindings.items()
    ):
        raise ValueError("bundled protocol/run manifest binding mismatch")
    if protocol.payload.get("phase3_source_commit") != run_manifest.get("phase3_source_commit"):
        raise ValueError("bundled protocol/source commit binding mismatch")
    if run_manifest["run_mode"] in ("pilot", "formal") and (
        run_manifest.get("protocol_tag") != "phase3-protocol-v4"
        or not re.fullmatch(r"[0-9a-f]{40}", str(run_manifest.get("phase3_source_commit")))
        or not re.fullmatch(r"[0-9a-f]{40}", str(run_manifest.get("protocol_repository_commit")))
        or not re.fullmatch(r"[0-9a-f]{40}", str(run_manifest.get("protocol_tag_object")))
    ):
        raise ValueError("frozen run repository/tag binding is invalid")
    return protocol


def verify_bundle(bundle_dir: Path) -> dict[str, Any]:
    manifest = load_json_snapshot(bundle_dir / "bundle_manifest.json", root=bundle_dir)
    if set(manifest) != {
        "schema_version", "run_mode", "run_manifest_sha256",
        "bundle_content_hash", "files", "exclusion_rule",
    } or manifest.get("schema_version") != 1 or manifest.get("run_mode") not in ("smoke", "pilot", "formal"):
        raise ValueError("bundle manifest schema/mode mismatch")
    files = manifest.get("files", [])
    actual = inventory_files(bundle_dir, excluded=("bundle_manifest.json",))
    if actual != files:
        raise ValueError("bundle file inventory mismatch")
    if content_hash(actual) != manifest.get("bundle_content_hash"):
        raise ValueError("bundle_content_hash mismatch")
    _validate_privacy(bundle_dir, files)
    run_manifest = load_json_snapshot(bundle_dir / "run/run_manifest.json", root=bundle_dir)
    run_manifest_raw = canonical_json_bytes(run_manifest)
    if sha256_bytes(run_manifest_raw) != manifest.get("run_manifest_sha256"):
        raise ValueError("run manifest hash mismatch")
    run_manifest_keys = {
        "schema_version", "run_mode", "run_status", "protocol_sha256",
        "phase3_source_commit", "protocol_repository_commit", "protocol_tag",
        "protocol_tag_object", "phase3_code_manifest_sha256",
        "stage2_authority_manifest_sha256", "expected_model_registry_sha256",
        "model_verification_receipt_sha256", "data_manifest_sha256",
        "split_manifest_sha256", "overlap_audit_receipt_sha256",
        "formal_approval_sha256", "ordered_model_ids", "ordered_filenames_sha256",
        "row_result_count", "image_group_result_count", "files", "exclusion_rule",
    }
    if set(run_manifest) != run_manifest_keys or run_manifest.get("schema_version") != 1:
        raise ValueError("run manifest schema mismatch")
    if run_manifest.get("run_status") != "success" or run_manifest.get("run_mode") != manifest.get("run_mode"):
        raise ValueError("run status/mode mismatch")
    run_files = run_manifest.get("files")
    if (
        not isinstance(run_files, list)
        or any(set(row) != {"relative_path", "size_bytes", "sha256"} for row in run_files)
        or run_files != sorted(run_files, key=lambda row: row["relative_path"].encode("utf-8"))
        or len({row["relative_path"] for row in run_files}) != len(run_files)
    ):
        raise ValueError("run manifest inventory schema/order mismatch")
    run_file_map = {row["relative_path"]: row for row in run_files}
    bundle_originals = {
        "data/data_manifest.json": "data_manifest.json",
        "data/split_manifest.json": "split_manifest.json",
        "data/canonical_row_index.jsonl": "canonical_row_index.jsonl",
        "data/degenerate_rows.json": "degenerate_rows.json",
        "status/run_status.json": "run_status.json",
        "results/row_level_results.jsonl": "row_level_results.jsonl",
        "results/image_group_results.jsonl": "image_group_results.jsonl",
        "results/metrics_summary.json": "metrics_summary.json",
        "results/nll_tail_summary.json": "nll_tail_summary.json",
        "results/numerical_diagnostics.json": "numerical_diagnostics.json",
        "results/timing.json": "timing.json",
        "results/degenerate_sensitivity_summary.json": "degenerate_sensitivity_summary.json",
    }
    bundle_originals.update({
        row["relative_path"]: row["relative_path"]
        for row in files if row["relative_path"].startswith("nll/")
    })
    if manifest["run_mode"] == "formal":
        bundle_originals.update({
            "data/coco_formal_images_manifest.jsonl": "coco_formal_images_manifest.jsonl",
            "audit/certifying_formal_filenames.txt": "certifying_formal_filenames.txt",
            "audit/excluded_formal_images.jsonl": "excluded_formal_images.jsonl",
            "audit/exact_matches.jsonl": "exact_matches.jsonl",
            "audit/near_duplicate_diagnostics.jsonl": "near_duplicate_diagnostics.jsonl",
            "audit/overlap_audit_receipt.json": "overlap_audit_receipt.json",
            "audit/overlap_audit_receipt.sha256": "overlap_audit_receipt.sha256",
            "audit/overlap_review.json": "overlap_review.json",
            "audit/probable_pairs.jsonl": "probable_pairs.jsonl",
            "audit/text_match_diagnostics.jsonl": "text_match_diagnostics.jsonl",
            "approval/formal_approval.json": "formal_approval.json",
        })
    bundle_file_map = {row["relative_path"]: row for row in files}
    for bundle_relative, run_relative in bundle_originals.items():
        if bundle_file_map.get(bundle_relative) is None or run_file_map.get(run_relative) is None:
            raise ValueError(f"run/bundle inventory member is missing: {run_relative}")
        if any(
            bundle_file_map[bundle_relative][key] != run_file_map[run_relative][key]
            for key in ("size_bytes", "sha256")
        ):
            raise ValueError(f"run/bundle inventory binding mismatch: {run_relative}")
    required_run_bindings = {
        "protocol_sha256": next(
            row["sha256"] for row in files
            if row["relative_path"].startswith("protocol/phase3_protocol_") and row["relative_path"].endswith(".json")
        ),
        "phase3_code_manifest_sha256": next(row["sha256"] for row in files if row["relative_path"] == "protocol/phase3_code_manifest_v2.json"),
        "stage2_authority_manifest_sha256": next(row["sha256"] for row in files if row["relative_path"].startswith("models/phase3_stage2_authority_manifest_")),
        "expected_model_registry_sha256": next(row["sha256"] for row in files if row["relative_path"] == "models/expected_model_registry.json"),
        "model_verification_receipt_sha256": next(row["sha256"] for row in files if row["relative_path"] == "models/model_verification_receipt.json"),
        "data_manifest_sha256": next(row["sha256"] for row in files if row["relative_path"] == "data/data_manifest.json"),
        "split_manifest_sha256": next(row["sha256"] for row in files if row["relative_path"] == "data/split_manifest.json"),
    }
    for key, digest in required_run_bindings.items():
        if run_manifest.get(key) != digest:
            raise ValueError(f"run manifest bundle binding mismatch: {key}")
    _validate_bundled_protocol(bundle_dir, run_manifest)
    registry = _validate_bundled_model_evidence(bundle_dir)
    index_rows = _jsonl(bundle_dir / "data/canonical_row_index.jsonl", bundle_dir)
    required_index = {"row_index", "row_key", "category", "numeric_id", "filename", "source_row_sha256"}
    if any(set(row) != required_index for row in index_rows):
        raise ValueError("canonical row index schema mismatch")
    if [row["row_index"] for row in index_rows] != list(range(len(index_rows))):
        raise ValueError("canonical row index order mismatch")
    if len({row["row_key"] for row in index_rows}) != len(index_rows):
        raise ValueError("canonical row index keys are not unique")
    for row in index_rows:
        if row["row_key"] != f"{row['category']}:{row['numeric_id']}" or not re.fullmatch(r"[0-9]{12}\.jpg", row["filename"]):
            raise ValueError("canonical row index identity mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", str(row["source_row_sha256"])):
            raise ValueError("canonical source row SHA is invalid")
    commitment_payload = b"".join(
        str(row["row_index"]).encode("ascii") + b"\0" + row["source_row_sha256"].encode("ascii") + b"\n"
        for row in index_rows
    )
    split_manifest = load_json_snapshot(bundle_dir / "data/split_manifest.json", root=bundle_dir)
    data_manifest = load_json_snapshot(bundle_dir / "data/data_manifest.json", root=bundle_dir)
    commitment = sha256_bytes(commitment_payload)
    if split_manifest.get("canonical_row_commitment_sha256") != commitment or data_manifest.get("canonical_row_commitment_sha256") != commitment:
        raise ValueError("canonical row commitment mismatch")
    index_artifact = next((row for row in data_manifest.get("artifacts", []) if row.get("relative_path") == "canonical_row_index.jsonl"), None)
    index_raw = b"".join(canonical_json_bytes(row) for row in index_rows)
    if index_artifact is None or index_artifact.get("size_bytes") != len(index_raw) or index_artifact.get("sha256") != sha256_bytes(index_raw):
        raise ValueError("data manifest canonical index binding mismatch")
    rows = _jsonl(bundle_dir / "results/row_level_results.jsonl", bundle_dir)
    groups = _jsonl(bundle_dir / "results/image_group_results.jsonl", bundle_dir)
    ordered_models = run_manifest.get("ordered_model_ids", [])
    expected_model_orders = {
        "smoke": ["M1-root-none"],
        "pilot": ["M1-root-none", "M3-root-43101"],
        "formal": [
            "M0-root-43101", "M0-root-43102", "M0-root-43103", "M1-root-none",
            "M2-root-43101", "M2-root-43102", "M2-root-43103",
            "M3-root-43101", "M3-root-43102", "M3-root-43103",
        ],
    }
    if ordered_models != expected_model_orders[manifest["run_mode"]]:
        raise ValueError("run manifest model order mismatch")
    registry_by_model = {row["model_id"]: row for row in registry["models"]}
    model_order = {model_id: index for index, model_id in enumerate(ordered_models)}
    public_config = load_json_snapshot(bundle_dir / "run/run_config_public.json", root=bundle_dir)
    selected_filenames = public_config.get("filenames") if isinstance(public_config, dict) else None
    expected_filename_count = {"smoke": 8, "pilot": 153, "formal": 1345}[manifest["run_mode"]]
    if (
        public_config.get("model_ids") != ordered_models
        or not isinstance(selected_filenames, list)
        or len(selected_filenames) != expected_filename_count
        or selected_filenames != sorted(set(selected_filenames), key=lambda value: value.encode("utf-8"))
        or run_manifest.get("ordered_filenames_sha256")
        != sha256_bytes(("\n".join(selected_filenames) + "\n").encode("utf-8"))
    ):
        raise ValueError("public run configuration model/filename membership mismatch")
    if rows != sorted(rows, key=lambda row: (model_order[row["model_id"]], int(row["row_index"]))):
        raise ValueError("row result order mismatch")
    keys = [(row["model_id"], row["category"], row["numeric_id"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("row result keys are not unique")
    index_by_number = {int(row["row_index"]): row for row in index_rows}
    selected_set = set(selected_filenames)
    expected_result_keys = {
        (model_id, int(index["row_index"]))
        for model_id in ordered_models
        for index in index_rows
        if index["filename"] in selected_set
    }
    actual_result_keys = {(row["model_id"], int(row["row_index"])) for row in rows}
    if actual_result_keys != expected_result_keys:
        raise ValueError("row results do not exactly cover the selected canonical rows")
    for row in rows:
        index = index_by_number.get(int(row["row_index"]))
        if index is None or any(
            row.get(key) != index[key]
            for key in ("row_key", "category", "numeric_id", "filename", "source_row_sha256")
        ):
            raise ValueError("row result does not bind the canonical row index")
        if row.get("run_mode") != manifest["run_mode"] or row.get("schema_version") != 1:
            raise ValueError("row result run mode/schema mismatch")
        method = row.get("method")
        expected_model = registry_by_model.get(row.get("model_id"))
        if (
            expected_model is None
            or method != expected_model["method"]
            or row.get("mapping_root") != expected_model["mapping_root"]
        ):
            raise ValueError("row result model method/mapping identity mismatch")
        brier_fields = [key for key in row if key.startswith("b_") and key != "b_img_pos_avg" and key != "b_none_pos_avg"]
        for key in brier_fields:
            value = row[key]
            if value is None:
                continue
            lower, upper = (-1e-5, 2.0 + 1e-5) if key.endswith("_raw") else (0.0, 2.0)
            if not lower - ATOL <= float(value) <= upper + ATOL:
                raise ValueError(f"Brier value outside frozen tolerance: {key}")
        if method == "M0":
            for key in (
                "b_img_pos1_raw", "b_img_pos1", "b_img_pos2_raw", "b_img_pos2",
                "b_img_neg_raw", "b_img_neg", "b_img_pos_avg", "raw_image_margin",
                "image_margin", "raw_visual_increment", "triplet_success", "visual_increment_success",
            ):
                if row.get(key) is not None:
                    raise ValueError(f"M0 image field is not null: {key}")
            raw_none_margin = row["b_none_neg_raw"] - (
                row["b_none_pos1_raw"] + row["b_none_pos2_raw"]
            ) / 2.0
            _close(row.get("raw_none_margin"), raw_none_margin, "row.raw_none_margin")
            expected = m0_row_metrics({
                key: row[key] for key in (
                    "b_none_pos1_raw", "b_none_pos1", "b_none_pos2_raw", "b_none_pos2",
                    "b_none_neg_raw", "b_none_neg", "raw_none_margin",
                )
            })
            expected_row_keys = {
                "schema_version", "run_mode", "model_id", "method", "mapping_root",
                "row_index", "source_row_sha256", "row_key", "category", "numeric_id",
                "filename",
            } | set(expected)
        elif method in ("M1", "M2", "M3"):
            raw_image_margin = row["b_img_neg_raw"] - (
                row["b_img_pos1_raw"] + row["b_img_pos2_raw"]
            ) / 2.0
            raw_none_margin = row["b_none_neg_raw"] - (
                row["b_none_pos1_raw"] + row["b_none_pos2_raw"]
            ) / 2.0
            raw_visual_increment = raw_image_margin - raw_none_margin
            for key, value in (
                ("raw_image_margin", raw_image_margin),
                ("raw_none_margin", raw_none_margin),
                ("raw_visual_increment", raw_visual_increment),
            ):
                _close(row.get(key), value, f"row.{key}")
            inputs = {
                key: row[key] for key in (
                    "b_img_pos1_raw", "b_img_pos1", "b_img_pos2_raw", "b_img_pos2",
                    "b_img_neg_raw", "b_img_neg", "b_none_pos1_raw", "b_none_pos1",
                    "b_none_pos2_raw", "b_none_pos2", "b_none_neg_raw", "b_none_neg",
                    "raw_image_margin", "raw_none_margin", "raw_visual_increment",
                )
            }
            if any(value is None for value in inputs.values()):
                raise ValueError("VLM row has a null observed Brier/margin field")
            expected = visual_row_metrics(inputs)
            expected_row_keys = {
                "schema_version", "run_mode", "model_id", "method", "mapping_root",
                "row_index", "source_row_sha256", "row_key", "category", "numeric_id",
                "filename",
            } | set(expected)
        else:
            raise ValueError(f"unknown row method: {method}")
        if set(row) != expected_row_keys:
            raise ValueError("row result schema mismatch")
        for key, value in expected.items():
            _close(row.get(key), value, f"row.{row['model_id']}.{row['row_key']}.{key}")
    recalculated_groups = aggregate_rows(rows)
    recalculated_groups.sort(key=lambda row: (model_order[row["model_id"]], row["filename"].encode("utf-8")))
    _close(groups, recalculated_groups, "image_groups")
    group_keys = [(row["model_id"], row["filename"]) for row in groups]
    if len(group_keys) != len(set(group_keys)):
        raise ValueError("image group result keys are not unique")
    metrics = load_json_snapshot(bundle_dir / "results/metrics_summary.json", root=bundle_dir)
    expected_metric_metadata = {
        "schema_version": 1,
        "run_mode": manifest["run_mode"],
        "bound_name": "simultaneous_project_disjoint_evaluation_bound" if manifest["run_mode"] == "formal" else None,
        "certificate_status": "available_under_frozen_conditions" if manifest["run_mode"] == "formal" else "not_applicable_non_certifying",
        "confidence_statement": FORMAL_CONFIDENCE_STATEMENT if manifest["run_mode"] == "formal" else None,
        "complete_model_independence_disclosure": FORMAL_INDEPENDENCE_DISCLOSURE if manifest["run_mode"] == "formal" else None,
        "estimand_scope": (
            "SugarCrepe++ represented target image-text construction distribution conditional on "
            "no project-history image overlap"
        ),
        "finite_population_guarantee": False,
        "all_natural_images_claim": False,
        "external_base_pretraining_overlap": "unknown",
        "certificate_scope": "project_controlled_image_group_disjoint_certifying_subset_only",
        "delta_families_joint_95_percent_claim": False,
        "m0_cross_input_comparison": "descriptive_different_input_conditions_only",
    }
    if set(metrics) != set(expected_metric_metadata) | {"models"} or any(
        metrics.get(key) != value for key, value in expected_metric_metadata.items()
    ):
        raise ValueError("metrics theory/disclosure metadata mismatch")
    if [row.get("model_id") for row in metrics.get("models", [])] != ordered_models:
        raise ValueError("metrics model order mismatch")
    expected_n = {"smoke": 8, "pilot": 153, "formal": 1345}[manifest["run_mode"]]
    for model in metrics.get("models", []):
        if set(model) != {
            "model_id", "n_unique_image_groups", "empirical_risks", "bound_status",
            "bounds", "exploratory_compression_bounds",
        }:
            raise ValueError("metrics model row schema mismatch")
        selected = [row for row in groups if row["model_id"] == model["model_id"]]
        if len(selected) != expected_n or model.get("n_unique_image_groups") != expected_n:
            raise ValueError("metrics unique-image n mismatch")
        _close(model["empirical_risks"], empirical_metric_means(selected), f"metrics.{model['model_id']}")
        if manifest["run_mode"] in ("smoke", "pilot"):
            if (
                model.get("bound_status") != "not_applicable_non_certifying"
                or any(value is not None for value in model.get("bounds", {}).values())
                or any(value is not None for value in model.get("exploratory_compression_bounds", {}).values())
            ):
                raise ValueError("non-formal bounds must be null")
        else:
            if model.get("bound_status") != "simultaneous_project_disjoint_evaluation_bound":
                raise ValueError("formal bound status name mismatch")
            n = len(selected)
            supports = {"positive_brier_risk": (0.0, 2.0), "visual_semantic_loss": (0.0, 1.0), "positive_invariance_loss": (0.0, 1.0)}
            for metric in MAIN_METRICS:
                if set(model.get("bounds", {})) != set(MAIN_METRICS) or set(model.get("exploratory_compression_bounds", {})) != set(MAIN_METRICS):
                    raise ValueError("formal bound metric set mismatch")
                method = next((row.get("method") for row in selected), None)
                values = np.asarray([row[metric] for row in selected], dtype=np.float64)
                expected = (
                    definition_constant(0.5, n)
                    if method == "M0" and metric == "visual_semantic_loss"
                    else hoeffding_upper(
                        model["empirical_risks"][metric], *supports[metric], n,
                        observed_min=float(np.min(values)), observed_max=float(np.max(values)),
                    )
                )
                _close(model["bounds"][metric], expected, f"bounds.{model['model_id']}.{metric}")
                exploratory = model.get("exploratory_compression_bounds", {}).get(metric)
                if method == "M0" and metric == "visual_semantic_loss":
                    if exploratory is not None:
                        raise ValueError("M0 visual constant must not have a compression bound")
                elif exploratory is None:
                    raise ValueError("formal compression bound is missing")
                else:
                    description = next(row["description_bits"] for row in registry["models"] if row["model_id"] == model["model_id"])
                    _close(
                        exploratory,
                        compression_upper(model["empirical_risks"][metric], *supports[metric], n, int(description)),
                        f"compression.{model['model_id']}.{metric}",
                    )
    stored_nll = load_json_snapshot(bundle_dir / "results/nll_tail_summary.json", root=bundle_dir)
    if (
        set(stored_nll) != {"schema_version", "disclaimer", "models"}
        or stored_nll.get("schema_version") != 1
        or stored_nll.get("disclaimer") != NLL_DISCLAIMER
        or list(stored_nll.get("models", {})) != ordered_models
    ):
        raise ValueError("NLL summary model set/order mismatch")
    recalculated_nll: dict[str, Any] = {"schema_version": 1, "disclaimer": NLL_DISCLAIMER, "models": {}}
    result_by_model_row = {
        (row["model_id"], int(row["row_index"])): row for row in rows
    }
    for model_id in ordered_models:
        directory = bundle_dir / "nll" / model_id
        arrays = validate_nll_store(directory)
        index = _jsonl(directory / "nll_index.jsonl", bundle_dir)
        expected_row_indices = {
            int(row["row_index"]) for row in rows if row["model_id"] == model_id
        }
        if {int(metadata["row_index"]) for metadata in index} != expected_row_indices:
            raise ValueError("NLL index does not cover every model row exactly")
        for metadata in index:
            result = result_by_model_row.get((model_id, int(metadata["row_index"])))
            if result is None or any(
                metadata.get(key) != result.get(key)
                for key in ("row_key", "filename", "category", "numeric_id")
            ) or metadata.get("model_id") != model_id:
                raise ValueError("NLL index does not bind row-level results")
        recalculated_nll["models"][model_id] = summarize_nll(arrays, index)
    _close(stored_nll, recalculated_nll, "nll")
    degenerates = load_json_snapshot(bundle_dir / "data/degenerate_rows.json", root=bundle_dir)
    degenerate_keys = {
        "schema_version", "degenerate_row_count", "affected_image_group_count",
        "type_counts", "rows",
    }
    allowed_types = ("positive_pair_equal", "pos1_equals_negative", "pos2_equals_negative")
    if set(degenerates) != degenerate_keys or degenerates.get("schema_version") != 1:
        raise ValueError("degenerate rows schema mismatch")
    degenerate_rows = degenerates.get("rows")
    if not isinstance(degenerate_rows, list) or len(degenerate_rows) != degenerates.get("degenerate_row_count"):
        raise ValueError("degenerate row count mismatch")
    observed_type_counts = {kind: 0 for kind in allowed_types}
    for item in degenerate_rows:
        if set(item) != {"row_index", "row_key", "category", "filename", "degenerate_types"}:
            raise ValueError("degenerate row entry schema mismatch")
        source = index_by_number.get(int(item["row_index"]))
        if source is None or any(item[key] != source[key] for key in ("row_key", "category", "filename")):
            raise ValueError("degenerate row does not bind canonical index")
        types = item["degenerate_types"]
        if types != [kind for kind in allowed_types if kind in types] or len(types) != len(set(types)):
            raise ValueError("degenerate type order/uniqueness mismatch")
        for kind in types:
            if kind not in observed_type_counts:
                raise ValueError("unknown degenerate type")
            observed_type_counts[kind] += 1
    observed_type_counts = {key: value for key, value in observed_type_counts.items() if value}
    if degenerates.get("type_counts") != observed_type_counts or degenerates.get("affected_image_group_count") != len({row["filename"] for row in degenerate_rows}):
        raise ValueError("degenerate summary counts mismatch")
    degenerate_artifact = next((row for row in data_manifest.get("artifacts", []) if row.get("relative_path") == "degenerate_rows.json"), None)
    degenerate_raw = canonical_json_bytes(degenerates)
    if degenerate_artifact is None or degenerate_artifact.get("size_bytes") != len(degenerate_raw) or degenerate_artifact.get("sha256") != sha256_bytes(degenerate_raw):
        raise ValueError("data manifest degenerate-row binding mismatch")
    stored_sensitivity = load_json_snapshot(bundle_dir / "results/degenerate_sensitivity_summary.json", root=bundle_dir)
    _close(stored_sensitivity, _degenerate_sensitivity(rows, degenerates), "degenerate_sensitivity")
    if run_manifest.get("row_result_count") != len(rows) or run_manifest.get("image_group_result_count") != len(groups):
        raise ValueError("run manifest result counts mismatch")
    numerical = load_json_snapshot(bundle_dir / "results/numerical_diagnostics.json", root=bundle_dir)
    expected_numerical = {
        "token_brier_below_zero_count", "token_brier_above_two_count",
        "caption_clip_low_count", "caption_clip_high_count", "nan_inf_count",
    }
    if set(numerical) != expected_numerical or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in numerical.values()) or numerical["nan_inf_count"] != 0:
        raise ValueError("numerical diagnostics are invalid")
    if manifest["run_mode"] == "formal":
        formal_bindings = {
            "overlap_audit_receipt_sha256": "audit/overlap_audit_receipt.json",
            "formal_approval_sha256": "approval/formal_approval.json",
        }
        for key, relative in formal_bindings.items():
            if run_manifest.get(key) != sha256_bytes(snapshot_file(bundle_dir / relative, root=bundle_dir)):
                raise ValueError(f"formal bundle binding mismatch: {key}")
        overlap = validate_overlap_receipt(
            bundle_dir / "audit/overlap_audit_receipt.json",
            split_manifest_path=bundle_dir / "data/split_manifest.json",
            formal_image_manifest_path=bundle_dir / "data/coco_formal_images_manifest.jsonl",
        )
        if overlap["certifying_names"] != selected_filenames:
            raise ValueError("formal bundle filenames do not equal the audited certifying subset")
    elif run_manifest.get("overlap_audit_receipt_sha256") is not None or run_manifest.get("formal_approval_sha256") is not None:
        raise ValueError("non-formal run unexpectedly binds formal audit/approval")
    return {
        "bundle_dir": str(bundle_dir),
        "bundle_content_hash": manifest["bundle_content_hash"],
        "run_mode": manifest["run_mode"],
        "row_count": len(rows),
        "image_group_count": len(groups),
        "verified_scope": "internal consistency and provenance-hash binding; GPU logits are not re-proven",
    }


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation() -> dict[str, Any]:
        try:
            validate_disjoint_roots(
                input_roots=[args.bundle_dir],
                output_roots=[args.status_output.parent],
                forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
            )
            return verify_bundle(args.bundle_dir)
        except Exception as error:
            raise Phase3HardFailure("bundle_verification_failed", str(error)) from error

    return execute_with_status("verify_phase3_bundle", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
