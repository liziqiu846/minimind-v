#!/usr/bin/env python3
"""Build hashed internal and public-redacted Phase 3 v5 result bundles."""

from __future__ import annotations

import argparse
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
    content_hash,
    inventory_files,
    load_json_snapshot,
    publish_directory,
    sha256_bytes,
    snapshot_file,
    validate_disjoint_roots,
)
from experiments.phase3.phase3_protocol_v5 import Phase3ProtocolV5


_SECRET = re.compile(r"(?i)(?:hf_|sk-|api[_-]?key|access[_-]?token|authorization\s*[:=])")
_HOST_PATH = re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users|root|mnt|srv|opt|var|tmp)/[^\s\"']+")


def _copy_file(source: Path, target: Path, root: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(target, snapshot_file(source, root=root), overwrite=False)


def _copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"bundle source is not a regular directory: {source}")
    for path in sorted(source.rglob("*"), key=lambda value: value.relative_to(source).as_posix().encode("utf-8")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"symbolic link forbidden in bundle source: {path}")
        if any(part.startswith(".") for part in relative.parts):
            if path.is_file() and relative.as_posix() != ".phase3.lock":
                raise ValueError(f"unexpected hidden bundle input: {relative.as_posix()}")
            continue
        if path.is_file():
            _copy_file(path, target / relative, source)


def _assert_public_tree(root: Path) -> None:
    for row in inventory_files(root, excluded=("bundle_manifest.json",)):
        relative = str(row["relative_path"])
        path = root / relative
        if path.suffix.lower() in (".json", ".jsonl", ".txt", ".md", ".csv", ".env"):
            text = snapshot_file(path, root=root).decode("utf-8")
            if _SECRET.search(text):
                raise ValueError(f"secret-like text in public bundle: {relative}")
            match = _HOST_PATH.search(text)
            if match:
                raise ValueError(f"absolute host path in public bundle: {relative}: {match.group(0)}")


def _finalize_manifest(root: Path, bundle_type: str, run_mode: str) -> dict[str, Any]:
    files = inventory_files(root, excluded=("bundle_manifest.json",))
    manifest = {
        "schema_version": 1,
        "bundle_version": "phase3-v5",
        "bundle_type": bundle_type,
        "run_mode": run_mode,
        "bundle_content_hash": content_hash(files),
        "files": files,
        "exclusion_rule": "bundle_manifest.json is excluded from its own inventory",
    }
    atomic_write_json(root / "bundle_manifest.json", manifest, overwrite=False)
    return manifest


def _sidecar(bundle: Path) -> None:
    digest = sha256_bytes(snapshot_file(bundle / "bundle_manifest.json", root=bundle))
    atomic_write_bytes(bundle.with_suffix(".sha256"), (digest + "\n").encode("ascii"), overwrite=False)


def load_run_mode(run_dir: Path) -> str:
    if (run_dir / "run_receipt.json").is_file():
        receipt = load_json_snapshot(run_dir / "run_receipt.json", root=run_dir)
        if receipt.get("status") != "success" or receipt.get("metric_version") != "v5":
            raise ValueError("formal v5 run receipt is not successful")
        return "formal"
    status = load_json_snapshot(run_dir / "run_status.json", root=run_dir)
    if status.get("status") != "success" or status.get("metric_version") != "v5":
        raise ValueError("non-formal v5 run status is not successful")
    if status.get("run_mode") not in ("smoke", "pilot"):
        raise ValueError("invalid v5 run mode")
    return str(status["run_mode"])


def _validate_inputs(
    *, run_dir: Path, protocol_path: Path, code_manifest: Path,
    registry_path: Path, verification_receipt: Path, description_bits_audit: Path,
    approval: Path | None, overlap_receipt: Path | None,
) -> str:
    protocol = Phase3ProtocolV5.load(protocol_path)
    protocol_raw = snapshot_file(protocol_path)
    code_raw = snapshot_file(code_manifest)
    for source, raw in ((protocol_path, protocol_raw), (code_manifest, code_raw)):
        if snapshot_file(source.with_suffix(".sha256")).decode("ascii") != sha256_bytes(raw) + "\n":
            raise ValueError(f"sidecar mismatch: {source.name}")
    if sha256_bytes(code_raw) != protocol.payload["phase3_code_manifest_sha256"]:
        raise ValueError("protocol/code-manifest binding mismatch")
    registry = load_json_snapshot(registry_path)
    receipt = load_json_snapshot(verification_receipt)
    audit = load_json_snapshot(description_bits_audit)
    for source in (verification_receipt, description_bits_audit):
        if snapshot_file(source.with_suffix(".sha256")).decode("ascii") != sha256_bytes(snapshot_file(source)) + "\n":
            raise ValueError(f"sidecar mismatch: {source.name}")
    if registry.get("model_count") != 10 or len(registry.get("models", [])) != 10:
        raise ValueError("expected-model registry is incomplete")
    if receipt.get("overall_status") != "verified" or len(receipt.get("models", [])) != 10:
        raise ValueError("model-verification receipt is incomplete")
    if audit.get("overall_status") != "verified" or len(audit.get("models", [])) != 10:
        raise ValueError("description-bit audit is incomplete")
    run_mode = load_run_mode(run_dir)
    if run_mode in ("smoke", "pilot"):
        manifest = load_json_snapshot(run_dir / "run_manifest.json", root=run_dir)
        if (
            manifest.get("run_mode") != run_mode
            or manifest.get("run_status") != "success"
            or manifest.get("metric_version") != "v5"
            or manifest.get("protocol_sha256") != sha256_bytes(protocol_raw)
            or manifest.get("phase3_code_manifest_sha256") != sha256_bytes(code_raw)
            or manifest.get("expected_model_registry_sha256") != sha256_bytes(snapshot_file(registry_path))
            or manifest.get("model_verification_receipt_sha256") != sha256_bytes(snapshot_file(verification_receipt))
            or inventory_files(run_dir, excluded=("run_manifest.json",)) != manifest.get("files")
        ):
            raise ValueError("non-formal run manifest or inventory binding mismatch")
    else:
        if approval is None or overlap_receipt is None:
            raise ValueError("formal bundle requires approval and overlap receipt")
        receipt_row = load_json_snapshot(run_dir / "run_receipt.json", root=run_dir)
        if (
            receipt_row.get("protocol_sha256") != sha256_bytes(protocol_raw)
            or receipt_row.get("code_manifest_sha256") != sha256_bytes(code_raw)
            or receipt_row.get("expected_registry_sha256") != sha256_bytes(snapshot_file(registry_path))
            or receipt_row.get("verification_receipt_sha256") != sha256_bytes(snapshot_file(verification_receipt))
            or receipt_row.get("description_bits_audit_sha256") != sha256_bytes(snapshot_file(description_bits_audit))
            or receipt_row.get("approval_sha256") != sha256_bytes(snapshot_file(approval))
            or receipt_row.get("overlap_receipt_sha256") != sha256_bytes(snapshot_file(overlap_receipt))
        ):
            raise ValueError("formal run receipt binding mismatch")
    return run_mode


def build_bundle_v5(
    *, run_dir: Path, protocol: Path, code_manifest: Path, expected_registry: Path,
    verification_receipt: Path, description_bits_audit: Path, output_dir: Path,
    approval: Path | None = None, overlap_receipt: Path | None = None,
    report_dir: Path | None = None, public_output_dir: Path | None = None,
) -> dict[str, Any]:
    outputs = [output_dir] + ([public_output_dir] if public_output_dir is not None else [])
    validate_disjoint_roots(
        input_roots=[
            run_dir, protocol.parent, code_manifest.parent, expected_registry.parent,
            verification_receipt.parent, description_bits_audit.parent,
            *([approval.parent] if approval is not None else []),
            *([overlap_receipt.parent] if overlap_receipt is not None else []),
            *([report_dir] if report_dir is not None else []),
        ],
        output_roots=outputs,
        forbidden_exact=[Path("/"), Path.home()],
    )
    for output in outputs:
        if output.exists() or output.with_suffix(".sha256").exists():
            raise FileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
    run_mode = _validate_inputs(
        run_dir=run_dir, protocol_path=protocol, code_manifest=code_manifest,
        registry_path=expected_registry, verification_receipt=verification_receipt,
        description_bits_audit=description_bits_audit, approval=approval,
        overlap_receipt=overlap_receipt,
    )
    internal_temp = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    public_temp: Path | None = None
    try:
        _copy_tree(run_dir, internal_temp / "run")
        for source, relative in (
            (protocol, "protocol/phase3_protocol_v5.json"),
            (protocol.with_suffix(".sha256"), "protocol/phase3_protocol_v5.sha256"),
            (code_manifest, "protocol/phase3_code_manifest_v5.json"),
            (code_manifest.with_suffix(".sha256"), "protocol/phase3_code_manifest_v5.sha256"),
            (expected_registry, "models/expected_model_registry.json"),
            (verification_receipt, "models/model_verification_receipt.json"),
            (verification_receipt.with_suffix(".sha256"), "models/model_verification_receipt.sha256"),
            (description_bits_audit, "models/description_bits_audit.json"),
            (description_bits_audit.with_suffix(".sha256"), "models/description_bits_audit.sha256"),
        ):
            _copy_file(source, internal_temp / relative, source.parent)
        if approval is not None:
            _copy_file(approval, internal_temp / "approval/formal_approval.json", approval.parent)
        if overlap_receipt is not None:
            _copy_file(overlap_receipt, internal_temp / "audit/overlap_audit_receipt.json", overlap_receipt.parent)
        if report_dir is not None:
            _copy_tree(report_dir, internal_temp / "report")
        internal = _finalize_manifest(internal_temp, "internal", run_mode)

        public = None
        if public_output_dir is not None:
            public_temp = Path(tempfile.mkdtemp(prefix=f".{public_output_dir.name}.", dir=public_output_dir.parent))
            if report_dir is not None:
                _copy_tree(report_dir, public_temp / "report")
            for name in (
                "overall_summary.json", "category_summary.json", "fixed_model_bounds.json",
                "compression_bounds.json", "nll_diagnostics.json", "run_receipt.json", "status.json",
            ):
                source = run_dir / name
                if source.is_file():
                    _copy_file(source, public_temp / "results" / name, run_dir)
            _assert_public_tree(public_temp)
            public = _finalize_manifest(public_temp, "public_redacted", run_mode)

        publish_directory(internal_temp, output_dir)
        _sidecar(output_dir)
        if public_output_dir is not None and public_temp is not None and public is not None:
            publish_directory(public_temp, public_output_dir)
            _sidecar(public_output_dir)
        result: dict[str, Any] = {"internal": internal}
        if public is not None:
            result["public"] = public
        return result
    finally:
        if internal_temp.exists():
            shutil.rmtree(internal_temp)
        if public_temp is not None and public_temp.exists():
            shutil.rmtree(public_temp)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "run_dir", "protocol", "code_manifest", "expected_registry",
        "verification_receipt", "description_bits_audit", "output_dir",
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--overlap-receipt", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--public-output-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_bundle_v5(
        run_dir=args.run_dir, protocol=args.protocol, code_manifest=args.code_manifest,
        expected_registry=args.expected_registry, verification_receipt=args.verification_receipt,
        description_bits_audit=args.description_bits_audit, output_dir=args.output_dir,
        approval=args.approval, overlap_receipt=args.overlap_receipt,
        report_dir=args.report_dir, public_output_dir=args.public_output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
