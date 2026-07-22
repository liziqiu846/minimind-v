#!/usr/bin/env python3
"""Audit the complete frozen MMS2 files used by Phase 3 v5 bounds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_json,
    load_json_snapshot,
    sha256_bytes,
    snapshot_file,
    validate_relative_posix,
    write_sha256_sidecar,
)
from experiments.phase3.stage2_adapter_loader import MODELS, verify_payload


CANDIDATE_ID_BITS = 4


def audit_description_bits_v5(registry_path: Path, artifact_root: Path) -> dict[str, Any]:
    registry = load_json_snapshot(registry_path)
    if (
        registry.get("schema_version") != 2
        or registry.get("model_count") != 10
        or not isinstance(registry.get("models"), list)
        or len(registry["models"]) != 10
    ):
        raise ValueError("frozen registry schema/model count mismatch")
    expected_order = [row["model_id"] for row in MODELS]
    if [row.get("model_id") for row in registry["models"]] != expected_order:
        raise ValueError("frozen registry model order mismatch")

    root = artifact_root.resolve()
    results: list[dict[str, Any]] = []
    for frozen, registry_row in zip(MODELS, registry["models"]):
        for key in (
            "model_id", "method", "mapping_root", "artifact_relative_path",
            "artifact_size_bytes", "artifact_sha256",
        ):
            if registry_row.get(key) != frozen[key]:
                raise ValueError(f"registry row differs from frozen model table: {frozen['model_id']}")
        relative = validate_relative_posix(registry_row["artifact_relative_path"])
        path = root / relative
        current = root
        for part in Path(relative).parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f"MMS2 path contains a symbolic link: {frozen['model_id']}")
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"MMS2 artifact is not a regular file: {frozen['model_id']}")
        payload = snapshot_file(path, root=root)
        if len(payload) != registry_row["artifact_size_bytes"]:
            raise ValueError(f"MMS2 size mismatch: {frozen['model_id']}")
        digest = sha256_bytes(payload)
        if digest != registry_row["artifact_sha256"]:
            raise ValueError(f"MMS2 SHA-256 mismatch: {frozen['model_id']}")
        _, metadata = verify_payload(payload, registry_row)
        if (
            metadata.get("model_group") != registry_row["method"]
            or metadata.get("mapping_root") != registry_row["mapping_root"]
        ):
            raise ValueError(f"decoded MMS2 identity mismatch: {frozen['model_id']}")
        file_bits = len(payload) * 8
        results.append(
            {
                "model_id": frozen["model_id"],
                "artifact_size_bytes": len(payload),
                "artifact_file_bits": file_bits,
                "candidate_id_bits": CANDIDATE_ID_BITS,
                "total_description_bits": file_bits + CANDIDATE_ID_BITS,
                "sha256": digest,
                "decode_status": "verified",
            }
        )
    return {
        "schema_version": 1,
        "audit_type": "phase3_v5_complete_mms2_description_bits",
        "candidate_model_count": 10,
        "candidate_id_bits": CANDIDATE_ID_BITS,
        "overall_status": "verified",
        "models": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-registry", type=Path, required=True)
    parser.add_argument("--stage2-artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists() or args.output.with_suffix(".sha256").exists():
        raise FileExistsError(args.output)
    audit = audit_description_bits_v5(args.expected_registry, args.stage2_artifact_root)
    atomic_write_json(args.output, audit, overwrite=False)
    write_sha256_sidecar(args.output, overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
