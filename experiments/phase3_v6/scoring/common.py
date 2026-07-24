"""Canonical I/O and deterministic runtime helpers for Phase 3 v6."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
SCORING_ROOT = Path(__file__).resolve().parent
GLOBAL_SEED = 3407


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
        indent=2 if pretty else None,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(
            dict(row),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
        for row in rows
    )


def atomic_write_bytes(path: str | Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.chmod(0o644)
    temporary.replace(destination)


def atomic_write_json(path: str | Path, value: Any, *, pretty: bool = True) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value, pretty=pretty))


def atomic_write_jsonl(
    path: str | Path, rows: Iterable[Mapping[str, Any]]
) -> None:
    atomic_write_bytes(path, canonical_jsonl_bytes(rows))


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid JSON at {path}:{line_number}: {error}"
                ) from error
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row is not an object at {path}:{line_number}")
            output.append(value)
    return output


def utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def stable_sigmoid(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("sigmoid input must be finite")
    if value >= 0.0:
        result = 1.0 / (1.0 + math.exp(-value))
    else:
        exponential = math.exp(value)
        result = exponential / (1.0 + exponential)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ArithmeticError("stable sigmoid produced an invalid result")
    return result


def linear_quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("quantile probability is outside [0,1]")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def seed_everything(seed: int = GLOBAL_SEED) -> None:
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
    except ImportError:
        pass


def git_output(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def source_hashes() -> dict[str, str]:
    paths = sorted(
        (
            path
            for path in SCORING_ROOT.rglob("*")
            if path.is_file()
            and (
                path.suffix == ".py"
                or path == SCORING_ROOT / "README.md"
            )
            and "__pycache__" not in path.parts
        ),
        key=lambda path: utf8_key(str(path.relative_to(REPO_ROOT))),
    )
    return {
        str(path.relative_to(REPO_ROOT)): sha256_file(path)
        for path in paths
    }


def source_tree_sha256(hashes: Mapping[str, str]) -> str:
    rows = [
        {"path": path, "sha256": hashes[path]}
        for path in sorted(hashes, key=utf8_key)
    ]
    return sha256_bytes(canonical_jsonl_bytes(rows))


def environment_receipt(device: str) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "device": device,
    }
    for module_name, output_name in (
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
        ("scipy", "scipy"),
        ("transformers", "transformers"),
        ("torch", "torch"),
    ):
        try:
            module = __import__(module_name)
            receipt[output_name] = getattr(module, "__version__", "unknown")
        except ImportError:
            receipt[output_name] = None
    try:
        import torch

        receipt.update(
            {
                "cuda_available": torch.cuda.is_available(),
                "cuda": torch.version.cuda,
                "cudnn": torch.backends.cudnn.version(),
                "model_dtype": "float32",
                "autocast_enabled": False,
                "cuda_matmul_allow_tf32": bool(
                    torch.backends.cuda.matmul.allow_tf32
                ),
                "cudnn_allow_tf32": bool(torch.backends.cudnn.allow_tf32),
                "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
                "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
            }
        )
        if device.startswith("cuda") and torch.cuda.is_available():
            index = torch.device(device).index
            index = torch.cuda.current_device() if index is None else index
            properties = torch.cuda.get_device_properties(index)
            receipt["gpu"] = {
                "index": index,
                "name": properties.name,
                "total_memory_bytes": properties.total_memory,
                "compute_capability": [
                    properties.major,
                    properties.minor,
                ],
            }
    except ImportError:
        pass
    return receipt
