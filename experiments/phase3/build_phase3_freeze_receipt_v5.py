#!/usr/bin/env python3
"""Build the post-tag Phase 3 v5 freeze receipt for commit B."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_json, canonical_json_bytes, sha256_bytes, snapshot_file, write_sha256_sidecar,
)
from experiments.phase3.phase3_protocol_v5 import (
    PROTOCOL_TAG_V5, Phase3ProtocolV5, REPO_ROOT, verify_code_manifest_v5,
)


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *arguments], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"git command failed: {' '.join(arguments)}: {result.stderr.strip()}")
    return result.stdout.strip()


def build_freeze_receipt_v5(candidate: Path, frozen: Path, code_manifest: Path) -> dict:
    candidate_protocol = Phase3ProtocolV5.load(candidate)
    frozen_protocol = Phase3ProtocolV5.load(frozen)
    candidate_raw = snapshot_file(candidate)
    frozen_raw = snapshot_file(frozen)
    if candidate_raw != frozen_raw or candidate_protocol.raw_sha256 != frozen_protocol.raw_sha256:
        raise ValueError("candidate and frozen v5 protocols are not byte-identical")
    code = verify_code_manifest_v5(code_manifest)
    code_sha = sha256_bytes(canonical_json_bytes(code))
    if frozen_protocol.payload["phase3_code_manifest_sha256"] != code_sha:
        raise ValueError("frozen protocol/code manifest binding mismatch")
    tag_commit = _git("rev-parse", f"{PROTOCOL_TAG_V5}^{{commit}}")
    head = _git("rev-parse", "HEAD")
    if tag_commit != head:
        raise ValueError("freeze receipt must be generated at tagged freeze commit A")
    tagged_frozen = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{tag_commit}:experiments/phase3/phase3_protocol_frozen_v5.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if tagged_frozen.returncode != 0 or tagged_frozen.stdout != frozen_raw:
        raise ValueError("tagged frozen protocol differs from working-tree bytes")
    tagged_code = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{tag_commit}:experiments/phase3/phase3_code_manifest_v5.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if tagged_code.returncode != 0 or tagged_code.stdout != snapshot_file(code_manifest):
        raise ValueError("tagged v5 code manifest differs from working-tree bytes")
    return {
        "schema_version": 1, "receipt_type": "phase3_v5_protocol_freeze",
        "status": "frozen", "freeze_commit": tag_commit, "protocol_tag": PROTOCOL_TAG_V5,
        "candidate_protocol_sha256": candidate_protocol.raw_sha256,
        "frozen_protocol_sha256": frozen_protocol.raw_sha256,
        "candidate_frozen_byte_identical": True, "phase3_code_manifest_sha256": code_sha,
        "lifecycle_rule": "freeze commit A contains code/manifests/protocols; tag points to A; receipt is committed in B",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--code-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists() or args.output.with_suffix(".sha256").exists():
        raise FileExistsError(args.output)
    atomic_write_json(
        args.output, build_freeze_receipt_v5(args.candidate, args.frozen, args.code_manifest), overwrite=False,
    )
    write_sha256_sidecar(args.output, overwrite=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
