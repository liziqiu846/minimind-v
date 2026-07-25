"""Verify the immutable public-information and decoder freeze receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.phase4_complexity_v1 import PROTOCOL_ID


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
FREEZE_MANIFEST_PATH = PACKAGE_ROOT / "freeze_manifest.json"
FREEZE_MANIFEST_SHA_PATH = PACKAGE_ROOT / "freeze_manifest.sha256"
REQUIRED_FROZEN_PATHS = {
    "experiments/phase4_complexity_v1/__init__.py",
    "experiments/phase4_complexity_v1/binary_spec.md",
    "experiments/phase4_complexity_v1/candidate_manifest.json",
    "experiments/phase4_complexity_v1/candidate_manifest.sha256",
    "experiments/phase4_complexity_v1/candidate_registry.py",
    "experiments/phase4_complexity_v1/complexity_protocol.json",
    "experiments/phase4_complexity_v1/complexity_protocol.sha256",
    "experiments/phase4_complexity_v1/conditional_codec.py",
    "experiments/phase4_complexity_v1/freeze_verification.py",
    "experiments/stage2_assets_manifest.json",
    "experiments/stage2_assets_sha256.txt",
    "experiments/stage2_protocol_v2.json",
    "experiments/stage2_target_registry.json",
    "experiments/phase4_m4_v1/protocol.json",
    "model/global_subspace_lora.py",
    "model/hybrid_subspace_lora.py",
}


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_freeze_manifest() -> dict[str, Any]:
    payload = FREEZE_MANIFEST_PATH.read_bytes()
    try:
        manifest = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("conditional complexity freeze manifest is invalid") from error
    if not isinstance(manifest, dict) or _canonical_json_bytes(manifest) != payload:
        raise ValueError("conditional complexity freeze manifest is not canonical")
    digest = hashlib.sha256(payload).hexdigest()
    expected_sidecar = f"{digest}  {FREEZE_MANIFEST_PATH.name}\n"
    if (
        FREEZE_MANIFEST_SHA_PATH.read_text(encoding="ascii")
        != expected_sidecar
    ):
        raise ValueError("conditional complexity freeze sidecar differs")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("protocol_id") != PROTOCOL_ID
        or manifest.get("status") != "frozen-before-new-M4-training"
    ):
        raise ValueError("conditional complexity freeze identity is invalid")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("conditional complexity freeze entries are absent")
    paths = [str(entry.get("relative_path", "")) for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != REQUIRED_FROZEN_PATHS:
        raise ValueError("conditional complexity freeze path set differs")
    for entry in entries:
        relative_path = str(entry["relative_path"])
        path = REPO_ROOT / relative_path
        if (
            not path.is_file()
            or _sha256_file(path) != entry.get("sha256")
            or not isinstance(entry.get("role"), str)
            or not entry["role"]
        ):
            raise ValueError(f"frozen file differs: {relative_path}")
    return {
        "status": "passed",
        "protocol_id": PROTOCOL_ID,
        "freeze_manifest_path": str(FREEZE_MANIFEST_PATH.resolve()),
        "freeze_manifest_sha256": digest,
        "frozen_file_count": len(entries),
    }

