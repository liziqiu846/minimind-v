#!/usr/bin/env python3
"""Build a privacy-sanitized, self-contained Phase 3 public bundle."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_bytes,
    atomic_write_json,
    canonical_json_bytes,
    content_hash,
    inventory_files,
    load_json_snapshot,
    publish_directory,
    sha256_bytes,
    snapshot_file,
    validate_relative_posix,
    validate_disjoint_roots,
)
from experiments.phase3.status import Phase3ArgumentParser, Phase3HardFailure, execute_with_status, require_status_output


_SECRET = re.compile(r"(?i)(?:hf_|sk-|api[_-]?key|access[_-]?token|authorization\s*[:=])")


def _verify_inventory(root: Path, rows: list[dict[str, Any]], excluded: tuple[str, ...]) -> None:
    actual = inventory_files(root, excluded=excluded)
    if actual != rows:
        raise ValueError("run manifest file inventory mismatch")


def _copy(source: Path, target: Path, *, source_root: Path) -> None:
    atomic_write_bytes(target, snapshot_file(source, root=source_root), overwrite=False)


def _public_value(value: Any, key: str = "") -> Any:
    if isinstance(value, dict):
        return {name: _public_value(item, name) for name, item in value.items()}
    if isinstance(value, list):
        return [_public_value(item, key) for item in value]
    if isinstance(value, str):
        if _SECRET.search(value):
            raise ValueError(f"secret-like value in public configuration field {key}")
        candidate = Path(value)
        if candidate.is_absolute():
            return {"logical_path_alias": key or "external_resource", "path_sha256": sha256_bytes(value.encode("utf-8"))}
        if "\\" in value or ".." in candidate.parts:
            raise ValueError(f"unsafe path-like value in public configuration field {key}")
    return value


def _assert_public_tree(root: Path) -> None:
    for row in inventory_files(root, excluded=("bundle_manifest.json",)):
        relative = str(row["relative_path"])
        validate_relative_posix(relative)
        path = root / relative
        if path.suffix.lower() in (".json", ".jsonl", ".txt", ".md"):
            text = snapshot_file(path, root=root).decode("utf-8")
            if _SECRET.search(text):
                raise ValueError(f"secret-like text in bundle: {relative}")
            for match in re.finditer(r"(?<![A-Za-z0-9_])/(?:home|Users|root|mnt|srv|opt|var|tmp)/[^\s\"']+", text):
                raise ValueError(f"absolute host path in bundle: {relative}: {match.group(0)}")


def build_bundle(run_dir: Path, protocol: Path, code_manifest: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(output)
    for path in (run_dir, protocol, code_manifest):
        if not path.exists():
            raise FileNotFoundError(path)
    run_manifest = load_json_snapshot(run_dir / "run_manifest.json", root=run_dir)
    run_manifest_raw = canonical_json_bytes(run_manifest)
    if run_manifest.get("run_status") != "success":
        raise ValueError("bundle builder only accepts a success run")
    _verify_inventory(run_dir, run_manifest.get("files", []), ("run_manifest.json",))
    protocol_raw = snapshot_file(protocol)
    code_raw = snapshot_file(code_manifest)
    if sha256_bytes(protocol_raw) != run_manifest.get("protocol_sha256"):
        raise ValueError("protocol differs from run manifest binding")
    if sha256_bytes(code_raw) != run_manifest.get("phase3_code_manifest_sha256"):
        raise ValueError("code manifest differs from run manifest binding")
    authority = code_manifest.parent / "phase3_stage2_authority_manifest_v2.json"
    expected = run_dir / "expected_model_registry.json"
    receipt = run_dir / "model_verification_receipt.json"
    required = [
        authority, expected, receipt, run_dir / "data_manifest.json", run_dir / "split_manifest.json",
        run_dir / "canonical_row_index.jsonl", run_dir / "degenerate_rows.json",
        run_dir / "run_config.json", run_dir / "environment.json",
        run_dir / "run_status.json", run_dir / "row_level_results.jsonl",
        run_dir / "image_group_results.jsonl", run_dir / "metrics_summary.json",
        run_dir / "nll_tail_summary.json", run_dir / "numerical_diagnostics.json",
        run_dir / "timing.json", run_dir / "degenerate_sensitivity_summary.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"run is incomplete: {missing}")
    expected_bindings = {
        authority: "stage2_authority_manifest_sha256",
        expected: "expected_model_registry_sha256",
        receipt: "model_verification_receipt_sha256",
        run_dir / "data_manifest.json": "data_manifest_sha256",
        run_dir / "split_manifest.json": "split_manifest_sha256",
    }
    for source, key in expected_bindings.items():
        if sha256_bytes(snapshot_file(source)) != run_manifest.get(key):
            raise ValueError(f"run binding mismatch: {key}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        atomic_write_bytes(temporary / "protocol" / protocol.name, protocol_raw, overwrite=False)
        atomic_write_bytes(temporary / "protocol" / "phase3_code_manifest_v2.json", code_raw, overwrite=False)
        _copy(authority, temporary / "models" / authority.name, source_root=authority.parent)
        _copy(expected, temporary / "models" / "expected_model_registry.json", source_root=run_dir)
        _copy(receipt, temporary / "models" / "model_verification_receipt.json", source_root=run_dir)
        for name in ("data_manifest.json", "split_manifest.json", "canonical_row_index.jsonl", "degenerate_rows.json"):
            _copy(run_dir / name, temporary / "data" / name, source_root=run_dir)
        atomic_write_bytes(
            temporary / "run" / "run_manifest.json",
            run_manifest_raw,
            overwrite=False,
        )
        atomic_write_json(
            temporary / "run" / "run_config_public.json",
            _public_value(load_json_snapshot(run_dir / "run_config.json", root=run_dir)),
            overwrite=False,
        )
        atomic_write_json(
            temporary / "run" / "environment_public.json",
            _public_value(load_json_snapshot(run_dir / "environment.json", root=run_dir)),
            overwrite=False,
        )
        _copy(run_dir / "run_status.json", temporary / "status" / "run_status.json", source_root=run_dir)
        result_names = (
            "row_level_results.jsonl", "image_group_results.jsonl", "metrics_summary.json",
            "nll_tail_summary.json", "numerical_diagnostics.json", "timing.json",
            "degenerate_sensitivity_summary.json",
        )
        for name in result_names:
            _copy(run_dir / name, temporary / "results" / name, source_root=run_dir)
        nll_root = run_dir / "nll"
        if not nll_root.is_dir():
            raise ValueError("run NLL directory is missing")
        for row in inventory_files(nll_root):
            relative = str(row["relative_path"])
            _copy(nll_root / relative, temporary / "nll" / relative, source_root=nll_root)
        if run_manifest.get("run_mode") == "formal":
            _copy(
                run_dir / "coco_formal_images_manifest.jsonl",
                temporary / "data/coco_formal_images_manifest.jsonl",
                source_root=run_dir,
            )
            for run_name, target_name, binding in (
                ("overlap_audit_receipt.json", "audit/overlap_audit_receipt.json", "overlap_audit_receipt_sha256"),
                ("formal_approval.json", "approval/formal_approval.json", "formal_approval_sha256"),
            ):
                source = run_dir / run_name
                if not source.is_file() or sha256_bytes(snapshot_file(source)) != run_manifest.get(binding):
                    raise ValueError(f"formal run is missing bound {run_name}")
                _copy(source, temporary / target_name, source_root=run_dir)
            for name in (
                "certifying_formal_filenames.txt",
                "excluded_formal_images.jsonl",
                "exact_matches.jsonl",
                "near_duplicate_diagnostics.jsonl",
                "overlap_audit_receipt.sha256",
                "overlap_review.json",
                "probable_pairs.jsonl",
                "text_match_diagnostics.jsonl",
            ):
                _copy(run_dir / name, temporary / "audit" / name, source_root=run_dir)
        if canonical_json_bytes(load_json_snapshot(run_dir / "run_manifest.json", root=run_dir)) != run_manifest_raw:
            raise ValueError("run manifest changed during bundle construction")
        _verify_inventory(run_dir, run_manifest.get("files", []), ("run_manifest.json",))
        _assert_public_tree(temporary)
        files = inventory_files(temporary, excluded=("bundle_manifest.json",))
        manifest = {
            "schema_version": 1,
            "run_mode": run_manifest["run_mode"],
            "run_manifest_sha256": sha256_bytes(run_manifest_raw),
            "bundle_content_hash": content_hash(files),
            "files": files,
            "exclusion_rule": "only bundle_manifest.json is excluded from bundle_content_hash",
        }
        atomic_write_json(temporary / "bundle_manifest.json", manifest, overwrite=False)
        publish_directory(temporary, output)
        return {"bundle_dir": str(output), "bundle_content_hash": manifest["bundle_content_hash"], "file_count": len(files)}
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--code-manifest", type=Path, required=True)
    parser.add_argument("--output-bundle-dir", type=Path, required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation() -> dict[str, Any]:
        try:
            validate_disjoint_roots(
                input_roots=[args.run_dir, args.protocol.parent, args.code_manifest.parent],
                output_roots=[args.output_bundle_dir, args.status_output.parent],
                forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
            )
            return build_bundle(args.run_dir, args.protocol, args.code_manifest, args.output_bundle_dir)
        except Exception as error:
            raise Phase3HardFailure("bundle_build_failed", str(error)) from error

    return execute_with_status("build_phase3_bundle", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
