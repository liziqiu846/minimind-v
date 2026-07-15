#!/usr/bin/env python3
"""Load, validate, and hash the Stage 2 protocol and immutable inputs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT = REPO_ROOT / "experiments/stage2_protocol.draft.json"
DEFAULT_FROZEN = REPO_ROOT / "experiments/stage2_protocol.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def write_json_atomic(path: Path, payload: Any) -> None:
    """Write a generated receipt atomically.

    Source files are edited with patches; experiment outputs use this helper so
    interrupted jobs never leave a valid-looking partial JSON document.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


@dataclass(frozen=True)
class Stage2Protocol:
    path: Path
    sha256: str
    payload: dict[str, Any]

    @classmethod
    def load(
        cls, path: Path | None = None, *, require_frozen: bool = False
    ) -> "Stage2Protocol":
        selected = Path(path or (DEFAULT_FROZEN if require_frozen else DEFAULT_DRAFT))
        selected = selected.resolve()
        payload = json.loads(selected.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("Stage 2 protocol schema_version must be 1")
        allowed = {"frozen"} if require_frozen else {"draft", "frozen"}
        if payload.get("status") not in allowed:
            raise ValueError(f"Stage 2 protocol status must be one of {sorted(allowed)}")
        if payload.get("protocol_id") != "minimind-v-stage2-joint-compression-v1":
            raise ValueError("unexpected Stage 2 protocol ID")
        return cls(selected, sha256_file(selected), payload)

    @property
    def is_frozen(self) -> bool:
        return self.payload["status"] == "frozen"

    def reference(self) -> dict[str, str]:
        return {
            "protocol_id": self.payload["protocol_id"],
            "protocol_sha256": self.sha256,
        }

    def require_frozen(self) -> None:
        if not self.is_frozen:
            raise ValueError("formal confirmation requires a frozen Stage 2 protocol")

    def verify_file(self, path: Path, expected_sha256: str, role: str) -> None:
        actual = sha256_file(path)
        if actual != expected_sha256:
            raise ValueError(
                f"{role} SHA-256 mismatch: expected {expected_sha256}, got {actual}"
            )

    def verify_immutable_inputs(self) -> None:
        assets = self.payload["assets"]
        self.verify_file(
            REPO_ROOT / assets["manifest_path"], assets["manifest_sha256"], "asset manifest"
        )
        self.verify_file(
            REPO_ROOT / assets["sha256_list_path"],
            assets["sha256_list_sha256"],
            "asset hash list",
        )
        history = self.payload["history_exclusion"]
        for stem in ("receipt", "exact_sha256", "phash", "sources", "manifest"):
            self.verify_file(
                REPO_ROOT / history[f"{stem}_path"],
                history[f"{stem}_sha256"],
                f"history {stem}",
            )

    def asset_path(self, role: str) -> Path:
        assets = self.payload["assets"]
        relative = assets["required_roles"][role]
        path = Path(assets["root"]) / relative
        manifest = json.loads(
            (REPO_ROOT / assets["manifest_path"]).read_text(encoding="utf-8")
        )
        entries = manifest.get("files", manifest.get("assets", []))
        matches = [
            item for item in entries
            if item.get("path") == relative or item.get("relative_path") == relative
        ]
        if len(matches) == 1:
            expected = matches[0].get("sha256")
            self.verify_file(path, expected, f"asset {role}")
        elif not matches and path.is_dir():
            prefix = relative.rstrip("/") + "/"
            children = [
                item for item in entries
                if (item.get("path") or item.get("relative_path", "")).startswith(prefix)
            ]
            if not children:
                raise ValueError(f"asset manifest does not contain directory {relative}")
            for item in children:
                child_relative = item.get("path") or item["relative_path"]
                self.verify_file(
                    Path(assets["root"]) / child_relative,
                    item["sha256"],
                    f"asset {role}/{Path(child_relative).name}",
                )
        else:
            raise ValueError(f"asset manifest does not uniquely contain {relative}")
        return path


def load_target_registry(path: Path | None = None) -> dict[str, Any]:
    selected = Path(path or REPO_ROOT / "experiments/stage2_target_registry.json")
    payload = json.loads(selected.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Stage 2 target registry schema_version must be 1")
    names: list[str] = []
    for module in ("vision", "projector", "language"):
        entries = payload["modules"][module]["targets"]
        module_names = [entry["canonical_name"] for entry in entries]
        if module_names != sorted(module_names, key=lambda value: value.encode("utf-8")):
            raise ValueError(f"{module} targets are not in canonical UTF-8 order")
        names.extend(module_names)
        rank = payload["modules"][module]["rank"]
        count = sum(
            rank * (entry["in_features"] + entry["out_features"])
            for entry in entries
        )
        if count != payload["modules"][module]["factor_elements"]:
            raise ValueError(f"{module} factor-element count is inconsistent")
    if len(names) != len(set(names)):
        raise ValueError("Stage 2 target names must be unique")
    return payload
