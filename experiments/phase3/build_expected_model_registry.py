#!/usr/bin/env python3
"""Build the static Phase 3 expected-model registry from frozen authority."""

from __future__ import annotations

import argparse
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
    validate_disjoint_roots,
)
from experiments.phase3.status import Phase3ArgumentParser, Phase3HardFailure, execute_with_status, require_status_output
from experiments.phase3.stage2_adapter_loader import (
    ARTIFACT_BATCH_ID,
    DECODER_ID,
    MODELS,
    RERUN_SOURCE_COMMIT,
)


def build_registry(authority_path: str | Path) -> dict:
    authority = load_json_snapshot(authority_path)
    authority_raw = canonical_json_bytes(authority)
    authority_keys = {
        "artifact_batch_id", "authority_id", "behavior_audit_relative_path",
        "behavior_audit_sha256", "confirmation_validation_relative_path",
        "confirmation_validation_sha256", "decoder_id", "decoder_source_relative_path",
        "decoder_source_sha256", "models", "pipeline_plan_relative_path",
        "pipeline_plan_sha256", "pipeline_progress_relative_path",
        "pipeline_progress_sha256", "recovery_verification_relative_path",
        "recovery_verification_sha256", "rerun_source_commit", "schema_version",
        "stage2_protocol_relative_path", "stage2_protocol_sha256",
        "stage2_reference_commit", "supersedes",
    }
    model_keys = {
        "model_id", "method", "mapping_root", "artifact_relative_path",
        "artifact_sha256", "artifact_size_bytes", "description_bits",
        "stage2_result_source",
    }
    if set(authority) != authority_keys:
        raise ValueError("authority manifest schema mismatch")
    if authority.get("schema_version") != 2 or authority.get("decoder_id") != DECODER_ID:
        raise ValueError("authority schema or decoder identity mismatch")
    if authority.get("artifact_batch_id") != ARTIFACT_BATCH_ID:
        raise ValueError("authority artifact batch identity mismatch")
    if authority.get("rerun_source_commit") != RERUN_SOURCE_COMMIT:
        raise ValueError("authority rerun source commit mismatch")
    expected_models = []
    if len(authority.get("models", [])) != len(MODELS):
        raise ValueError("authority must contain exactly ten models")
    for authority_model, expected in zip(authority["models"], MODELS):
        if set(authority_model) != model_keys:
            raise ValueError(f"authority model schema mismatch: {expected['model_id']}")
        for key, value in expected.items():
            if authority_model.get(key) != value:
                raise ValueError(f"authority mismatch for {expected['model_id']}:{key}")
        expected_models.append(dict(authority_model))
    return {
        "artifact_batch_id": authority["artifact_batch_id"],
        "authority_id": authority["authority_id"],
        "authority_manifest_sha256": sha256_bytes(authority_raw),
        "decoder_id": authority["decoder_id"],
        "decoder_source_sha256": authority["decoder_source_sha256"],
        "model_count": 10,
        "models": expected_models,
        "recovery_verification_sha256": authority["recovery_verification_sha256"],
        "registry_id": "phase3-v4-expected-model-registry-v2",
        "rerun_source_commit": authority["rerun_source_commit"],
        "schema_version": 2,
        "stage2_protocol_sha256": authority["stage2_protocol_sha256"],
        "stage2_reference_commit": authority["stage2_reference_commit"],
    }


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--stage2-authority-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation():
        validate_disjoint_roots(
            input_roots=[args.stage2_authority_manifest.parent],
            output_roots=[args.output.parent, args.status_output.parent],
            forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
        )
        if args.output.exists():
            raise Phase3HardFailure("output_exists", str(args.output))
        payload = build_registry(args.stage2_authority_manifest)
        atomic_write_json(args.output, payload, overwrite=False)
        return {"expected_registry": str(args.output), "model_count": 10}

    return execute_with_status("build_expected_model_registry", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
