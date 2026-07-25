"""Strict loader for the frozen fifteen-candidate complexity registry."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from experiments.phase4_complexity_v1 import (
    CANDIDATE_COUNT,
    CANDIDATE_ID_BITS,
    CANDIDATE_MANIFEST_SCHEMA_VERSION,
    INVALID_CANDIDATE_ID,
    PROTOCOL_ID,
    PROTOCOL_SCHEMA_VERSION,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
CANDIDATE_MANIFEST_PATH = PACKAGE_ROOT / "candidate_manifest.json"
CANDIDATE_MANIFEST_SHA_PATH = PACKAGE_ROOT / "candidate_manifest.sha256"
PROTOCOL_PATH = PACKAGE_ROOT / "complexity_protocol.json"
PROTOCOL_SHA_PATH = PACKAGE_ROOT / "complexity_protocol.sha256"
ALLOWED_METHODS = ("M2", "M3", "M4")
ALLOWED_ROOTS = (43101, 43102, 43103)
EXPECTED_BLOCK_ORDERS = {
    "M2": ("vision", "projector", "language"),
    "M3": ("shared",),
    "M4": (
        "shared",
        "vision_private",
        "projector_private",
        "language_private",
    ),
}


@dataclass(frozen=True)
class Candidate:
    candidate_id: int
    candidate_name: str
    method: str
    mapping_root: int
    block_order: Tuple[str, ...]
    block_dimensions: Mapping[str, int]
    total_coordinate_dimension: int
    source_config_relative_path: str
    source_config_sha256: str


def canonical_json_bytes(value: Any) -> bytes:
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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_canonical_json(path: Path) -> tuple[dict[str, Any], bytes, str]:
    payload = path.read_bytes()
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict) or canonical_json_bytes(value) != payload:
        raise ValueError(f"JSON is not in the frozen canonical form: {path}")
    return value, payload, sha256_bytes(payload)


def _validate_sidecar(path: Path, digest: str, filename: str) -> None:
    expected = f"{digest}  {filename}\n"
    if path.read_text(encoding="ascii") != expected:
        raise ValueError(f"SHA256 sidecar mismatch: {path}")


def load_complexity_protocol(
    *, verify_sidecar: bool = True
) -> tuple[dict[str, Any], dict[str, str]]:
    protocol, payload, digest = _load_canonical_json(PROTOCOL_PATH)
    if verify_sidecar:
        _validate_sidecar(PROTOCOL_SHA_PATH, digest, PROTOCOL_PATH.name)
    if (
        protocol.get("schema_version") != PROTOCOL_SCHEMA_VERSION
        or protocol.get("protocol_id") != PROTOCOL_ID
        or protocol.get("status") != "frozen-before-new-M4-training"
    ):
        raise ValueError("conditional complexity protocol identity is invalid")
    return protocol, {
        "path": str(PROTOCOL_PATH.resolve()),
        "sha256": digest,
        "bytes": len(payload),
    }


def _candidate_from_row(row: Mapping[str, Any]) -> Candidate:
    try:
        source = row["source_config"]
        block_order = tuple(str(name) for name in row["block_order"])
        dimensions = {
            str(name): int(value)
            for name, value in row["block_dimensions"].items()
        }
        candidate = Candidate(
            candidate_id=int(row["candidate_id"]),
            candidate_name=str(row["candidate_name"]),
            method=str(row["method"]),
            mapping_root=int(row["mapping_root"]),
            block_order=block_order,
            block_dimensions=dimensions,
            total_coordinate_dimension=int(row["total_coordinate_dimension"]),
            source_config_relative_path=str(source["relative_path"]),
            source_config_sha256=str(source["sha256"]),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ValueError("candidate manifest row is malformed") from error
    return candidate


def _validate_candidate(candidate: Candidate, expected_id: int) -> None:
    if (
        candidate.candidate_id != expected_id
        or candidate.candidate_id < 0
        or candidate.candidate_id >= INVALID_CANDIDATE_ID
        or candidate.method not in ALLOWED_METHODS
        or candidate.mapping_root not in ALLOWED_ROOTS
        or candidate.block_order != EXPECTED_BLOCK_ORDERS[candidate.method]
        or set(candidate.block_dimensions) != set(candidate.block_order)
        or any(
            isinstance(value, bool) or int(value) <= 0
            for value in candidate.block_dimensions.values()
        )
        or sum(candidate.block_dimensions.values())
        != candidate.total_coordinate_dimension
        or candidate.total_coordinate_dimension != 4096
        or len(candidate.source_config_sha256) != 64
    ):
        raise ValueError(
            f"candidate manifest invariants failed for ID {expected_id}"
        )
    expected_name = (
        f"current-{candidate.method}-root-{candidate.mapping_root}"
        if candidate.method in ("M2", "M3")
        else candidate.candidate_name
    )
    if candidate.method in ("M2", "M3") and candidate.candidate_name != expected_name:
        raise ValueError("legacy candidate name is not canonical")
    if candidate.method == "M4":
        shared = candidate.block_dimensions["shared"]
        if candidate.candidate_name != (
            f"M4-shared-{shared}-root-{candidate.mapping_root}"
        ):
            raise ValueError("M4 candidate name is not canonical")


def load_candidate_registry(
    *,
    verify_sidecars: bool = True,
    verify_source_configs: bool = True,
) -> tuple[Dict[int, Candidate], dict[str, Any]]:
    manifest, payload, digest = _load_canonical_json(CANDIDATE_MANIFEST_PATH)
    if verify_sidecars:
        _validate_sidecar(
            CANDIDATE_MANIFEST_SHA_PATH,
            digest,
            CANDIDATE_MANIFEST_PATH.name,
        )
    protocol, protocol_receipt = load_complexity_protocol(
        verify_sidecar=verify_sidecars
    )
    family = protocol.get("candidate_family", {})
    if family.get("candidate_manifest_sha256") != digest:
        raise ValueError("protocol and candidate manifest SHA256 differ")
    if (
        manifest.get("schema_version") != CANDIDATE_MANIFEST_SCHEMA_VERSION
        or manifest.get("protocol_id") != PROTOCOL_ID
        or manifest.get("candidate_count") != CANDIDATE_COUNT
        or manifest.get("candidate_id_bits") != CANDIDATE_ID_BITS
        or manifest.get("invalid_candidate_ids") != [INVALID_CANDIDATE_ID]
        or manifest.get("status") != "frozen-before-new-M4-training"
    ):
        raise ValueError("candidate manifest identity is invalid")
    rows = manifest.get("candidates")
    if not isinstance(rows, list) or len(rows) != CANDIDATE_COUNT:
        raise ValueError("candidate manifest must contain exactly fifteen rows")
    registry: Dict[int, Candidate] = {}
    names = set()
    for expected_id, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError("candidate manifest row must be an object")
        candidate = _candidate_from_row(row)
        _validate_candidate(candidate, expected_id)
        if candidate.candidate_id in registry or candidate.candidate_name in names:
            raise ValueError("candidate manifest contains a duplicate")
        source_path = REPO_ROOT / candidate.source_config_relative_path
        if verify_source_configs and (
            not source_path.is_file()
            or sha256_file(source_path) != candidate.source_config_sha256
        ):
            raise ValueError(
                f"candidate source config hash mismatch: {source_path}"
            )
        registry[candidate.candidate_id] = candidate
        names.add(candidate.candidate_name)
    if tuple(registry) != tuple(range(CANDIDATE_COUNT)):
        raise ValueError("candidate IDs are not the frozen sequence 0 through 14")
    return registry, {
        "status": "passed",
        "candidate_count": CANDIDATE_COUNT,
        "candidate_id_bits": CANDIDATE_ID_BITS,
        "invalid_candidate_id": INVALID_CANDIDATE_ID,
        "manifest_path": str(CANDIDATE_MANIFEST_PATH.resolve()),
        "manifest_sha256": digest,
        "manifest_bytes": len(payload),
        "protocol": protocol_receipt,
    }


def candidate_by_id(candidate_id: int) -> Candidate:
    if isinstance(candidate_id, bool) or not isinstance(candidate_id, int):
        raise ValueError("candidate ID must be an integer")
    registry, _ = load_candidate_registry()
    if candidate_id not in registry:
        raise ValueError("candidate ID is not one of the frozen values 0 through 14")
    return registry[candidate_id]


def candidate_by_name(candidate_name: str) -> Candidate:
    registry, _ = load_candidate_registry()
    matches = [
        candidate
        for candidate in registry.values()
        if candidate.candidate_name == candidate_name
    ]
    if len(matches) != 1:
        raise ValueError("candidate name is not uniquely frozen")
    return matches[0]
