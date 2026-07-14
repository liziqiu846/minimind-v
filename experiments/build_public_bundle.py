#!/usr/bin/env python3
"""Copy selected experiment artifacts into a self-checking public bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from uuid import uuid4


SCHEMA_VERSION = 1
INDEX_NAME = "bundle_index.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_artifact(specification: str) -> tuple[str, Path]:
    """Parse one ``ROLE=PATH`` command-line artifact specification."""
    role, separator, source = specification.partition("=")
    if not separator or not role or not source:
        raise argparse.ArgumentTypeError("artifacts must use ROLE=PATH")
    return role, Path(source)


def _write_json_atomic(path: Path, value: dict) -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_public_bundle(
    output_dir: Path, artifacts: list[tuple[str, Path]]
) -> dict:
    """Copy artifacts and return the relative-path-only bundle index."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"bundle already exists: {output_dir}")

    roles = [role for role, _ in artifacts]
    names = [Path(source).name for _, source in artifacts]
    if len(roles) != len(set(roles)):
        raise ValueError("artifact roles must be unique")
    if len(names) != len(set(names)):
        raise ValueError("artifact file names must be unique")
    if any(not role for role in roles):
        raise ValueError("artifact roles cannot be empty")
    for _, source in artifacts:
        if not Path(source).is_file():
            raise FileNotFoundError(f"artifact is not a file: {source}")

    output_dir.mkdir(parents=True)
    artifact_dir = output_dir / "artifacts"
    artifact_dir.mkdir()
    entries = []
    try:
        for role, source in sorted(artifacts, key=lambda item: item[0]):
            destination = artifact_dir / Path(source).name
            shutil.copyfile(source, destination)
            entries.append(
                {
                    "role": role,
                    "path": destination.relative_to(output_dir).as_posix(),
                    "bytes": destination.stat().st_size,
                    "sha256": sha256_file(destination),
                }
            )
        index = {"schema_version": SCHEMA_VERSION, "artifacts": entries}
        _write_json_atomic(output_dir / INDEX_NAME, index)
    except Exception:
        shutil.rmtree(output_dir)
        raise
    return index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "artifacts", nargs="+", type=parse_artifact, metavar="ROLE=PATH"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = build_public_bundle(args.output_dir, args.artifacts)
    print(json.dumps(index, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
