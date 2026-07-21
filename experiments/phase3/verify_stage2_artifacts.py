#!/usr/bin/env python3
"""Verify Stage 2 MMS2 files against the static expected registry."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_json,
    canonical_json_bytes,
    load_json_snapshot,
    sha256_bytes,
    snapshot_file,
    validate_disjoint_roots,
    validate_relative_posix,
    write_sha256_sidecar,
)
from experiments.phase3.stage2_adapter_loader import (
    ARTIFACT_BATCH_ID, MODELS, verify_payload, verify_stage2_source_integrity,
)
from experiments.phase3.status import Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output


HARD_STATUSES = {
    "unsafe_path", "not_regular_file", "size_mismatch", "hash_mismatch",
    "decode_failed", "decoded_identity_mismatch",
}


def verify_registry_artifacts(registry_path: Path, artifact_root: Path, stage2_protocol: Path) -> dict:
    registry = load_json_snapshot(registry_path)
    registry_raw = canonical_json_bytes(registry)
    if (
        registry.get("schema_version") != 2
        or registry.get("registry_id") != "phase3-v4-expected-model-registry-v2"
        or registry.get("artifact_batch_id") != ARTIFACT_BATCH_ID
    ):
        raise ValueError("expected registry is not the approved Phase 3 v4 rerun registry")
    required_top = {
        "artifact_batch_id", "authority_id", "authority_manifest_sha256", "decoder_id",
        "decoder_source_sha256", "model_count", "models", "recovery_verification_sha256",
        "registry_id", "rerun_source_commit", "schema_version", "stage2_protocol_sha256",
        "stage2_reference_commit",
    }
    required_model = {
        "model_id", "method", "mapping_root", "artifact_relative_path", "artifact_sha256",
        "artifact_size_bytes", "description_bits", "stage2_result_source",
    }
    if set(registry) != required_top or registry.get("model_count") != 10 or len(registry.get("models", [])) != 10:
        raise ValueError("expected registry schema/model count mismatch")
    for actual, frozen in zip(registry["models"], MODELS):
        if set(actual) != required_model or any(actual.get(key) != value for key, value in frozen.items()):
            raise ValueError("expected registry model row differs from the approved rerun table")
        if actual.get("stage2_result_source") != {"model_group": frozen["method"], "mapping_root": frozen["mapping_root"]}:
            raise ValueError("expected registry Stage2 result identity mismatch")
    protocol_raw = snapshot_file(stage2_protocol)
    if sha256_bytes(protocol_raw) != registry.get("stage2_protocol_sha256"):
        raise ValueError("Stage2 protocol hash differs from registry")
    verify_stage2_source_integrity(str(stage2_protocol.absolute()))
    root = artifact_root.absolute()
    models = []
    for expected in registry.get("models", []):
        relative = expected["artifact_relative_path"]
        try:
            validate_relative_posix(relative)
            path = root / relative
        except (TypeError, ValueError):
            path = root / "__unsafe_registry_path__"
        base = {
            "model_id": expected["model_id"],
            "method": expected["method"],
            "mapping_root": expected["mapping_root"],
            "resolved_relative_path": relative,
            "expected_sha256": expected["artifact_sha256"],
            "actual_sha256": None,
            "expected_size_bytes": expected["artifact_size_bytes"],
            "actual_size_bytes": None,
            "decoded_method": None,
            "decoded_mapping_root": None,
            "status": None,
            "error_code": None,
        }
        if path == root / "__unsafe_registry_path__":
            base.update(status="unsafe_path", error_code="unsafe_path")
            models.append(base)
            continue
        current = root
        unsafe_chain = False
        for component in Path(relative).parts:
            current = current / component
            if current.is_symlink():
                unsafe_chain = True
                break
        if unsafe_chain:
            base.update(status="unsafe_path", error_code="unsafe_path")
            models.append(base)
            continue
        if not path.exists():
            base.update(status="missing", error_code="missing")
            models.append(base)
            continue
        if not path.is_file():
            base.update(status="not_regular_file", error_code="not_regular_file")
            models.append(base)
            continue
        try:
            payload = snapshot_file(path, root=root)
        except (ValueError, OSError):
            base.update(status="unsafe_path", error_code="unsafe_path")
            models.append(base)
            continue
        base["actual_size_bytes"] = len(payload)
        base["actual_sha256"] = sha256_bytes(payload)
        if len(payload) != expected["artifact_size_bytes"]:
            base.update(status="size_mismatch", error_code="size_mismatch")
        elif base["actual_sha256"] != expected["artifact_sha256"]:
            base.update(status="hash_mismatch", error_code="hash_mismatch")
        else:
            try:
                _, metadata = verify_payload(payload, expected)
                base["decoded_method"] = metadata["model_group"]
                base["decoded_mapping_root"] = metadata["mapping_root"]
                base.update(status="verified", error_code=None)
            except ValueError as error:
                code = str(error)
                status = code if code == "decoded_identity_mismatch" else "decode_failed"
                base.update(status=status, error_code=status)
        models.append(base)
    statuses = {model["status"] for model in models}
    if statuses == {"verified"} and len(models) == 10:
        overall = "verified"
    elif statuses <= {"verified", "missing"}:
        overall = "blocked"
    else:
        overall = "hard_failure"
    return {
        "schema_version": 2,
        "receipt_type": "phase3_stage2_artifact_verification_v3",
        "artifact_batch_id": registry["artifact_batch_id"],
        "authority_id": registry["authority_id"],
        "stage2_reference_commit": registry["stage2_reference_commit"],
        "rerun_source_commit": registry["rerun_source_commit"],
        "recovery_verification_sha256": registry["recovery_verification_sha256"],
        "expected_model_registry_sha256": sha256_bytes(registry_raw),
        "authority_manifest_sha256": registry["authority_manifest_sha256"],
        "decoder_id": registry["decoder_id"],
        "decoder_source_sha256": registry["decoder_source_sha256"],
        "model_count": 10,
        "overall_status": overall,
        "models": models,
    }


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--expected-registry", type=Path, required=True)
    parser.add_argument("--stage2-artifact-root", type=Path)
    parser.add_argument("--stage2-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation():
        root = args.stage2_artifact_root or (
            Path(os.environ["STAGE2_ARTIFACT_ROOT"]) if os.environ.get("STAGE2_ARTIFACT_ROOT") else None
        )
        if root is None:
            raise Phase3Blocked("blocked_missing_artifact_root", "provide --stage2-artifact-root")
        validate_disjoint_roots(
            input_roots=[args.expected_registry.parent, Path(root), args.stage2_protocol.parent],
            output_roots=[args.output.parent, args.status_output.parent],
            forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
        )
        if args.output.exists():
            raise Phase3HardFailure("output_exists", str(args.output))
        try:
            receipt = verify_registry_artifacts(args.expected_registry, root, args.stage2_protocol)
        except FileNotFoundError as error:
            raise Phase3Blocked("blocked_stage2_base_asset_missing", str(error)) from error
        atomic_write_json(args.output, receipt, overwrite=False)
        write_sha256_sidecar(args.output, overwrite=False)
        if receipt["overall_status"] == "blocked":
            missing = [model["model_id"] for model in receipt["models"] if model["status"] == "missing"]
            raise Phase3Blocked("blocked_missing_artifacts", ",".join(missing))
        if receipt["overall_status"] == "hard_failure":
            bad = [f"{model['model_id']}:{model['status']}" for model in receipt["models"] if model["status"] != "verified"]
            raise Phase3HardFailure("artifact_verification_failed", ",".join(bad))
        return {"verification_receipt": str(args.output), "verified_models": 10}

    return execute_with_status("verify_stage2_artifacts", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
