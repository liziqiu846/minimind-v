"""Shared paths and deterministic artifact helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_FORMAL_ROOT = Path(
    "/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721/"
    "experiments/runs/stage2_v2_fast/formal"
)
DEFAULT_PS_ROOT = Path(
    "/home/lizhaohui/lzq/stage3-ps-formal-20260726-1825"
)
STAGE2_PROTOCOL = REPO_ROOT / "experiments/stage2_protocol_v2.json"
STAGE2_FINAL_REPORT = (
    REPO_ROOT
    / "experiments/runs/stage2_v2_fast/final/stage2_final_report.json"
)
PS_PROTOCOL = (
    REPO_ROOT / "experiments/phase3_private_vs_shared_v1/protocol.json"
)
PHASE3_V6_PROTOCOL = (
    REPO_ROOT / "experiments/phase3_v6/scoring/protocol.json"
)
DEFAULT_REGISTRY = PACKAGE_ROOT / "candidate_registry.json"
DEFAULT_SELECTION = PACKAGE_ROOT / "selection_receipt.json"
DEFAULT_SUMMARY = PACKAGE_ROOT / "boundselect_summary.json"
DEFAULT_CSV = PACKAGE_ROOT / "boundselect_summary.csv"
DEFAULT_AUDIT = PACKAGE_ROOT / "audit_report.json"

STAGE2_PROTOCOL_SHA256 = (
    "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
)
STAGE2_FINAL_REPORT_SHA256 = (
    "f872bd5925fa10302393f253acf6efef2f468e7ab0e456bcb0a912ee8df5cb84"
)
PS_PROTOCOL_SHA256 = (
    "5425fd6ab1fb6673d381e0fbf650ff42ed174398da9fe90e933ccf591f275a4d"
)
PHASE3_V6_PROTOCOL_SHA256 = (
    "3cbf89287ef5c75657bf0df6ed1170f0ab1c916ac5aacc0c009fb80c3bbf9195"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def write_json_exclusive(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def candidate_id(model_group: str, mapping_root: int | None) -> str:
    root = "none" if mapping_root is None else str(mapping_root)
    return f"{model_group}-root-{root}"
