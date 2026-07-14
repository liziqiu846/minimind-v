#!/usr/bin/env python3
"""Small helpers for loading and enforcing a frozen Phase 2 protocol."""

from __future__ import annotations

import hashlib
import importlib
import json
import platform
from dataclasses import dataclass
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class FrozenProtocol:
    path: Path
    sha256: str
    payload: dict

    @classmethod
    def load(cls, path: Path) -> "FrozenProtocol":
        path = Path(path).resolve()
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or payload.get("status") != "frozen":
            raise ValueError("Phase 2 protocol must have schema_version 1 and frozen status")
        return cls(path=path, sha256=sha256_file(path), payload=payload)

    def reference(self) -> dict:
        return {
            "protocol_id": self.payload["protocol_id"],
            "protocol_sha256": self.sha256,
        }

    def require(self, section: str, actual: dict, keys: tuple[str, ...]) -> None:
        expected = self.payload[section]
        mismatches = {
            key: {"expected": expected[key], "actual": actual.get(key)}
            for key in keys
            if actual.get(key) != expected[key]
        }
        if mismatches:
            raise ValueError(f"{section} does not match frozen protocol: {mismatches}")

    def verify_files(self, repo_root: Path, group: str) -> None:
        for entry in self.payload[group]:
            path = Path(repo_root) / entry["path"]
            if sha256_file(path) != entry["sha256"]:
                raise ValueError(f"frozen {group} file changed: {entry['path']}")

    def verify_asset(self, role: str, path: Path) -> None:
        matches = [entry for entry in self.payload["assets"] if entry["role"] == role]
        if len(matches) != 1 or sha256_file(path) != matches[0]["sha256"]:
            raise ValueError(f"selected {role} does not match the frozen asset")

    def verify_environment(self, repo_root: Path) -> None:
        path = Path(repo_root) / self.payload["environment_path"]
        if sha256_file(path) != self.payload["environment_sha256"]:
            raise ValueError("frozen environment receipt changed")
        expected = json.loads(path.read_text(encoding="utf-8"))
        actual = {
            name: importlib.import_module(name).__version__
            for name in expected["packages"]
        }
        if platform.python_version() != expected["python"] or actual != expected["packages"]:
            raise ValueError("runtime package versions do not match Phase 2 environment")
        torch = importlib.import_module("torch")
        if torch.version.cuda != expected["cuda_runtime"]:
            raise ValueError("CUDA runtime does not match Phase 2 environment")


def validate_split_artifact(
    split_manifest_path: Path,
    data_path: Path,
    role: str,
    protocol: FrozenProtocol,
) -> dict:
    manifest_path = Path(split_manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("protocol_sha256") != protocol.sha256:
        raise ValueError("dataset split was not built under this frozen protocol")
    dataset = protocol.payload["dataset"]
    expected_manifest = {
        "protocol_id": protocol.payload["protocol_id"],
        "source_sha256": dataset["source_sha256"],
        "excluded_unique_images": dataset["excluded_unique_images"],
        "seed": dataset["seed"],
        "selection": dataset["selection"],
        "image_overlap": 0,
    }
    actual_manifest = {key: manifest.get(key) for key in expected_manifest}
    if actual_manifest != expected_manifest:
        raise ValueError("dataset receipt does not match the frozen sampling protocol")
    if [item["sha256"] for item in manifest["exclusions"]] != dataset[
        "exclude_sha256"
    ]:
        raise ValueError("dataset receipt has the wrong Phase 1 exclusions")
    artifact = manifest["outputs"][role]
    if artifact["rows"] != dataset[f"{role}_size"]:
        raise ValueError(f"{role} sample count does not match the frozen protocol")
    data_path = Path(data_path).resolve()
    if sha256_file(data_path) != artifact["sha256"]:
        raise ValueError(f"{role} data does not match its split manifest")
    membership = manifest_path.parent / artifact["membership"]["path"]
    if sha256_file(membership) != artifact["membership"]["sha256"]:
        raise ValueError(f"{role} membership does not match its split manifest")
    return {
        "role": role,
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "artifact_sha256": artifact["sha256"],
        "membership_sha256": artifact["membership"]["sha256"],
        "examples": artifact["rows"],
    }
