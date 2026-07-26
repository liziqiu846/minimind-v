"""Protocol-bound immutable receipts for formal P/S training."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .common import canonical_bytes, sha256_file
from .configs import matrix_sha256
from .protocol_tools import PROTOCOL_PATH, validate_frozen_protocol


def bindings() -> dict[str, str]:
    validate_frozen_protocol()
    return {
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "candidate_matrix_sha256": matrix_sha256(),
    }


def validate_bindings(payload: dict[str, Any]) -> None:
    expected = bindings()
    observed = {key: payload.get(key) for key in expected}
    if observed != expected:
        raise ValueError("artifact bindings differ from current protocol/matrix")


def write_json_exclusive(path: Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(payload)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def write_json_atomic(path: Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(canonical_bytes(payload))
    os.replace(temporary, path)


def load_bound_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_bindings(payload)
    return payload
