#!/usr/bin/env python3
"""CPU-only independent verification of Phase 3 v5 bundles."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_json, canonical_json_bytes, content_hash, inventory_files, load_json_snapshot,
    load_jsonl_snapshot, sha256_bytes, snapshot_file, write_sha256_sidecar,
)
from experiments.phase3.artifact_validation import validate_model_verification_receipt
from experiments.phase3.nll_diagnostics import summarize_nll, validate_nll_store
from experiments.phase3.phase3_protocol_v5 import Phase3ProtocolV5
from experiments.phase3.run_phase3_formal_v5 import (
    _approval_matches, recompute_nll_diagnostics_v5, shard_plan_v5, validate_finalized_shard_v5,
)
from experiments.phase3.runner_common import _degenerate_sensitivity, build_metrics_summary
from experiments.phase3.theory_metrics_v5 import (
    aggregate_category_rows_v5, aggregate_rows_v5, m0_row_metrics_v5, visual_row_metrics_v5,
)


ATOL = 1e-10
RTOL = 1e-10


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


def _recompute_row(row: dict[str, Any]) -> None:
    if row["method"] == "M0":
        keys = [key for key in row if key.startswith("b_none_") or key == "raw_none_margin"]
        expected = m0_row_metrics_v5({key: row[key] for key in keys})
    else:
        keys = [
            key for key in row
            if key.startswith("b_img_") or key.startswith("b_none_")
            or key in ("raw_image_margin", "raw_none_margin", "raw_visual_increment")
        ]
        expected = visual_row_metrics_v5({key: row[key] for key in keys})
    for key, value in expected.items():
        _close(row.get(key), value, f"row.{key}")


def _verify_nonformal(run: Path, registry: dict[str, Any], mode: str) -> dict[str, Any]:
    manifest = load_json_snapshot(run / "run_manifest.json", root=run)
    if (
        manifest.get("run_status") != "success"
        or manifest.get("run_mode") != mode
        or manifest.get("metric_version") != "v5"
        or inventory_files(run, excluded=("run_manifest.json",)) != manifest.get("files")
    ):
        raise ValueError("non-formal run manifest/inventory mismatch")
    rows = load_jsonl_snapshot(run / "row_level_results.jsonl", root=run)
    for row in rows:
        _recompute_row(row)
    expected_groups = aggregate_rows_v5(rows)
    groups = load_jsonl_snapshot(run / "image_group_results.jsonl", root=run)
    _close(groups, expected_groups, "image_groups")
    model_ids = ["M1-root-none"] if mode == "smoke" else ["M1-root-none", "M3-root-43101"]
    expected_summary = build_metrics_summary(mode, model_ids, groups, registry, "v5")
    _close(load_json_snapshot(run / "metrics_summary.json", root=run), expected_summary, "metrics")
    expected_counts = {"smoke": (8, None), "pilot": (306, 1038)}
    expected_groups_count, expected_rows_count = expected_counts[mode]
    if len(groups) != expected_groups_count or (expected_rows_count is not None and len(rows) != expected_rows_count):
        raise ValueError("non-formal row/image-group completeness mismatch")
    for model_id in model_ids:
        nll_root = run / "nll" / model_id
        arrays = validate_nll_store(nll_root)
        index = load_jsonl_snapshot(nll_root / "nll_index.jsonl", root=run)
        summary = summarize_nll(arrays, index)
        stored = load_json_snapshot(run / "nll_tail_summary.json", root=run)["models"][model_id]
        _close(stored, summary, f"nll.{model_id}")
    degenerates = load_json_snapshot(run / "degenerate_rows.json", root=run)
    expected_sensitivity = _degenerate_sensitivity(rows, degenerates, "v5")
    _close(
        load_json_snapshot(run / "degenerate_sensitivity_summary.json", root=run),
        expected_sensitivity,
        "degenerate_sensitivity",
    )
    numerical = load_json_snapshot(run / "numerical_diagnostics.json", root=run)
    required_numerical = {
        "token_brier_below_zero_count", "token_brier_above_two_count",
        "caption_clip_low_count", "caption_clip_high_count", "nan_inf_count",
    }
    if (
        set(numerical) != required_numerical
        or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in numerical.values())
        or any(numerical[key] != 0 for key in ("caption_clip_low_count", "caption_clip_high_count", "nan_inf_count"))
    ):
        raise ValueError("non-formal numerical diagnostics failed")
    return {"row_count": len(rows), "image_group_count": len(groups)}


def _verify_formal(run: Path, registry: dict[str, Any]) -> dict[str, Any]:
    config = load_json_snapshot(run / "formal_run_config.json", root=run)
    if config.get("model_ids") is None or len(config["model_ids"]) != 10 or len(config.get("filenames", [])) != 1345:
        raise ValueError("formal config model/image completeness mismatch")
    status = load_json_snapshot(run / "status.json", root=run)
    if (
        status.get("status") != "success"
        or status.get("completed_shards") != 430
        or status.get("total_shards") != 430
        or status.get("model_image_group_count") != 13450
    ):
        raise ValueError("formal final status is incomplete")
    plan = shard_plan_v5(config["model_ids"], config["filenames"])
    if len(plan) != 430:
        raise ValueError("formal shard count is not 430")
    rows = []
    for shard in plan:
        validate_finalized_shard_v5(
            run / "shards" / shard["shard_id"], shard,
            sha256_bytes(canonical_json_bytes(config)),
            config["protocol_sha256"], config["code_manifest_sha256"],
        )
        path = run / "raw_rows" / f"{shard['shard_id']}.jsonl"
        shard_rows = load_jsonl_snapshot(path, root=run)
        payload_rows = snapshot_file(
            run / "shards" / shard["shard_id"] / "payload/row_level_results.jsonl", root=run,
        )
        if snapshot_file(path, root=run) != payload_rows:
            raise ValueError(f"formal raw-row copy differs from verified shard: {shard['shard_id']}")
        for row in shard_rows:
            _recompute_row(row)
        rows.extend(shard_rows)
    groups = aggregate_rows_v5(rows)
    order = {model: index for index, model in enumerate(config["model_ids"])}
    groups.sort(key=lambda row: (order[row["model_id"]], row["filename"].encode("utf-8")))
    stored_groups = load_jsonl_snapshot(run / "image_groups.jsonl", root=run)
    _close(stored_groups, groups, "formal.image_groups")
    if len(groups) != 13450:
        raise ValueError("formal model-image group count is not 13,450")
    overall = build_metrics_summary("formal", config["model_ids"], groups, registry, "v5")
    _close(load_json_snapshot(run / "overall_summary.json", root=run), overall, "formal.overall")
    category = {"schema_version": 1, "results": aggregate_category_rows_v5(rows)}
    _close(load_json_snapshot(run / "category_summary.json", root=run), category, "formal.category")
    fixed = {
        "schema_version": 1, "selection_status": overall["selection_status"],
        "simultaneous_coverage_claim": False,
        "models": [{"model_id": row["model_id"], "bounds": row["fixed_model_bounds"]} for row in overall["models"]],
    }
    compression = {
        "schema_version": 1, "selection_status": overall["selection_status"],
        "simultaneous_coverage_claim": False,
        "models": [{"model_id": row["model_id"], "bounds": row["compression_bounds"]} for row in overall["models"]],
    }
    _close(load_json_snapshot(run / "fixed_model_bounds.json", root=run), fixed, "formal.fixed")
    _close(load_json_snapshot(run / "compression_bounds.json", root=run), compression, "formal.compression")
    _close(load_json_snapshot(run / "nll_diagnostics.json", root=run), recompute_nll_diagnostics_v5(run, plan), "formal.nll")
    receipt = load_json_snapshot(run / "run_receipt.json", root=run)
    numerical = receipt.get("numerical_diagnostics")
    if (
        receipt.get("model_image_group_count") != 13450
        or receipt.get("formal_shard_count") != 430
        or receipt.get("simultaneous_coverage_claim") is not False
        or not isinstance(numerical, dict)
        or any(numerical.get(key) != 0 for key in ("caption_clip_low_count", "caption_clip_high_count", "nan_inf_count"))
    ):
        raise ValueError("formal receipt completeness/post-hoc status mismatch")
    return {"row_count": len(rows), "image_group_count": len(groups), "shard_count": len(plan)}


def verify_bundle_v5(bundle_dir: Path) -> dict[str, Any]:
    for path in bundle_dir.rglob("*"):
        relative = path.relative_to(bundle_dir)
        if path.is_symlink() or any(part.startswith(".") for part in relative.parts):
            raise ValueError(f"unsafe or unhashed bundle member: {relative.as_posix()}")
    manifest = load_json_snapshot(bundle_dir / "bundle_manifest.json", root=bundle_dir)
    if (
        manifest.get("bundle_version") != "phase3-v5" or manifest.get("bundle_type") != "internal"
        or inventory_files(bundle_dir, excluded=("bundle_manifest.json",)) != manifest.get("files")
        or content_hash(manifest["files"]) != manifest.get("bundle_content_hash")
    ):
        raise ValueError("v5 bundle manifest/inventory mismatch")
    sidecar = bundle_dir.with_suffix(".sha256")
    if snapshot_file(sidecar).decode("ascii") != sha256_bytes(snapshot_file(bundle_dir / "bundle_manifest.json", root=bundle_dir)) + "\n":
        raise ValueError("v5 bundle manifest sidecar mismatch")
    protocol = Phase3ProtocolV5.load(bundle_dir / "protocol/phase3_protocol_v5.json")
    code = snapshot_file(bundle_dir / "protocol/phase3_code_manifest_v5.json", root=bundle_dir)
    if (
        snapshot_file(bundle_dir / "protocol/phase3_protocol_v5.sha256", root=bundle_dir).decode("ascii")
        != protocol.raw_sha256 + "\n"
        or snapshot_file(bundle_dir / "protocol/phase3_code_manifest_v5.sha256", root=bundle_dir).decode("ascii")
        != sha256_bytes(code) + "\n"
        or sha256_bytes(code) != protocol.payload["phase3_code_manifest_sha256"]
    ):
        raise ValueError("bundled protocol/code manifest binding mismatch")
    registry = load_json_snapshot(bundle_dir / "models/expected_model_registry.json", root=bundle_dir)
    audit = load_json_snapshot(bundle_dir / "models/description_bits_audit.json", root=bundle_dir)
    if (
        snapshot_file(bundle_dir / "models/description_bits_audit.sha256", root=bundle_dir).decode("ascii")
        != sha256_bytes(snapshot_file(bundle_dir / "models/description_bits_audit.json", root=bundle_dir)) + "\n"
    ):
        raise ValueError("description-bit audit sidecar mismatch")
    validate_model_verification_receipt(
        bundle_dir / "models/model_verification_receipt.json",
        bundle_dir / "models/expected_model_registry.json",
        require_all=True,
    )
    registry_by = {row["model_id"]: row for row in registry.get("models", [])}
    audit_rows = audit.get("models", [])
    if (
        registry.get("model_count") != 10
        or audit.get("overall_status") != "verified"
        or len(audit_rows) != 10
        or [row.get("model_id") for row in audit_rows] != list(registry_by)
        or any(
            row.get("artifact_size_bytes") != registry_by[row["model_id"]].get("artifact_size_bytes")
            or row.get("sha256") != registry_by[row["model_id"]].get("artifact_sha256")
            or row.get("total_description_bits") != row.get("artifact_size_bytes") * 8 + 4
            for row in audit_rows
        )
    ):
        raise ValueError("bundled model evidence mismatch")
    mode = manifest.get("run_mode")
    if mode in ("smoke", "pilot"):
        run_manifest = load_json_snapshot(bundle_dir / "run/run_manifest.json", root=bundle_dir)
        if (
            run_manifest.get("protocol_sha256") != protocol.raw_sha256
            or run_manifest.get("phase3_code_manifest_sha256") != protocol.payload["phase3_code_manifest_sha256"]
        ):
            raise ValueError("bundled non-formal protocol/code binding mismatch")
        result = _verify_nonformal(bundle_dir / "run", registry, mode)
    elif mode == "formal":
        approval = load_json_snapshot(bundle_dir / "approval/formal_approval.json", root=bundle_dir)
        run_receipt = load_json_snapshot(bundle_dir / "run/run_receipt.json", root=bundle_dir)
        formal_config = load_json_snapshot(bundle_dir / "run/formal_run_config.json", root=bundle_dir)
        if (
            not _approval_matches(approval, protocol.raw_sha256, protocol.payload["phase3_code_manifest_sha256"])
            or run_receipt.get("protocol_sha256") != protocol.raw_sha256
            or run_receipt.get("code_manifest_sha256") != protocol.payload["phase3_code_manifest_sha256"]
            or run_receipt.get("approval_sha256")
            != sha256_bytes(snapshot_file(bundle_dir / "approval/formal_approval.json", root=bundle_dir))
            or run_receipt.get("expected_registry_sha256")
            != sha256_bytes(snapshot_file(bundle_dir / "models/expected_model_registry.json", root=bundle_dir))
            or run_receipt.get("verification_receipt_sha256")
            != sha256_bytes(snapshot_file(bundle_dir / "models/model_verification_receipt.json", root=bundle_dir))
            or run_receipt.get("description_bits_audit_sha256")
            != sha256_bytes(snapshot_file(bundle_dir / "models/description_bits_audit.json", root=bundle_dir))
            or run_receipt.get("overlap_receipt_sha256")
            != sha256_bytes(snapshot_file(bundle_dir / "audit/overlap_audit_receipt.json", root=bundle_dir))
            or formal_config.get("protocol_sha256") != protocol.raw_sha256
            or formal_config.get("code_manifest_sha256") != protocol.payload["phase3_code_manifest_sha256"]
        ):
            raise ValueError("bundled formal approval binding mismatch")
        result = _verify_formal(bundle_dir / "run", registry)
    else:
        raise ValueError("unknown v5 bundle run mode")
    return {
        "schema_version": 1, "status": "verified", "run_mode": mode,
        "bundle_content_hash": manifest["bundle_content_hash"], **result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists() or args.output.with_suffix(".sha256").exists():
        raise FileExistsError(args.output)
    result = verify_bundle_v5(args.bundle_dir)
    atomic_write_json(args.output, result, overwrite=False)
    write_sha256_sidecar(args.output, overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
