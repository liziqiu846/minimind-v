"""Canonical serialization, hashing, safe snapshots, and atomic publication."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_canonical_json_bytes(payload: bytes, *, name: str = "JSON") -> Any:
    value = json.loads(payload.decode("utf-8"))
    if canonical_json_bytes(value) != payload:
        raise ValueError(f"JSON is not canonical: {name}")
    return value


def validate_relative_posix(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        raise ValueError(f"unsafe relative POSIX path: {value!r}")
    path = PurePosixPath(value)
    if any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe relative POSIX path: {value!r}")
    return path


def _reject_symlink_chain(path: Path, stop: Path | None = None) -> None:
    absolute = path.absolute()
    stop_abs = stop.absolute() if stop is not None else None
    current = absolute
    chain: list[Path] = []
    while True:
        chain.append(current)
        if stop_abs is not None and current == stop_abs:
            break
        if current.parent == current:
            break
        current = current.parent
    if stop_abs is not None and chain[-1] != stop_abs:
        raise ValueError(f"path escapes declared root: {path}")
    for component in reversed(chain):
        # ``Path.exists()`` follows links and is false for a broken symlink.
        # Broken links are still links and therefore remain unsafe inputs.
        if component.is_symlink():
            raise ValueError(f"symbolic link is forbidden: {component}")


def snapshot_file(path: str | Path, *, root: str | Path | None = None) -> bytes:
    target = Path(os.path.abspath(Path(path)))
    declared_root = None
    if root is not None:
        root_input = Path(os.path.abspath(Path(root)))
        _reject_symlink_chain(root_input)
        declared_root = root_input.resolve()
    if declared_root is not None:
        try:
            target.relative_to(declared_root)
        except ValueError as error:
            raise ValueError(f"path escapes declared root: {target}") from error
    _reject_symlink_chain(target, declared_root)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(target, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"not a regular file: {target}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after or len(payload) != after.st_size:
            raise RuntimeError(f"file changed while being read: {target}")
        return payload
    finally:
        os.close(descriptor)


def snapshot_record(path: str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    payload = snapshot_file(path, root=root)
    return {"size_bytes": len(payload), "sha256": sha256_bytes(payload), "payload": payload}


def load_json_snapshot(path: str | Path, *, root: str | Path | None = None) -> Any:
    payload = snapshot_file(path, root=root)
    return parse_canonical_json_bytes(payload, name=Path(path).name)


def load_jsonl_snapshot(path: str | Path, *, root: str | Path | None = None) -> list[Any]:
    payload = snapshot_file(path, root=root)
    if payload and not payload.endswith(b"\n"):
        raise ValueError(f"JSONL lacks its final LF: {Path(path).name}")
    rows: list[Any] = []
    for line_number, line in enumerate(payload.splitlines(keepends=True), 1):
        value = json.loads(line.decode("utf-8"))
        if canonical_json_bytes(value) != line:
            raise ValueError(f"JSONL row is not canonical: {Path(path).name}:{line_number}")
        rows.append(value)
    return rows


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path: str | Path) -> None:
    _fsync_directory(Path(path))


def atomic_write_bytes(path: str | Path, payload: bytes, *, overwrite: bool = True) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not overwrite and target.exists():
        raise FileExistsError(target)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if not overwrite and target.exists():
            raise FileExistsError(target)
        os.replace(temporary, target)
        _fsync_directory(target.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: str | Path, value: Any, *, overwrite: bool = True) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value), overwrite=overwrite)


def atomic_write_jsonl(path: str | Path, rows: Iterable[Any], *, overwrite: bool = True) -> None:
    atomic_write_bytes(
        path,
        b"".join(canonical_json_bytes(row) for row in rows),
        overwrite=overwrite,
    )


def publish_directory(temporary: str | Path, target: str | Path) -> None:
    source = Path(temporary)
    destination = Path(target)
    if destination.exists():
        raise FileExistsError(destination)
    if source.parent.resolve() != destination.parent.resolve():
        raise ValueError("atomic directory publication requires sibling paths")
    _fsync_directory(source)
    os.replace(source, destination)
    _fsync_directory(destination.parent)


def write_sha256_sidecar(path: str | Path, *, overwrite: bool = True) -> Path:
    target = Path(path)
    digest = sha256_bytes(snapshot_file(target))
    sidecar = target.with_suffix(".sha256")
    atomic_write_bytes(sidecar, (digest + "\n").encode("ascii"), overwrite=overwrite)
    return sidecar


def inventory_files(root: str | Path, *, excluded: Iterable[str] = ()) -> list[dict[str, Any]]:
    directory = Path(root)
    excluded_set = set(excluded)
    rows = []
    for path in directory.rglob("*"):
        relative = path.relative_to(directory).as_posix()
        if relative in excluded_set or any(part.startswith(".") for part in Path(relative).parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symbolic link is forbidden: {relative}")
        if not path.is_file():
            continue
        payload = snapshot_file(path, root=directory)
        rows.append(
            {"relative_path": relative, "size_bytes": len(payload), "sha256": sha256_bytes(payload)}
        )
    rows.sort(key=lambda row: row["relative_path"].encode("utf-8"))
    return rows


def content_hash(entries: Iterable[Mapping[str, Any]]) -> str:
    parts = []
    for row in sorted(entries, key=lambda value: str(value["relative_path"]).encode("utf-8")):
        validate_relative_posix(str(row["relative_path"]))
        parts.append(
            str(row["relative_path"]).encode("utf-8")
            + b"\0"
            + str(row["sha256"]).encode("ascii")
            + b"\0"
            + str(int(row["size_bytes"])).encode("ascii")
            + b"\n"
        )
    return sha256_bytes(b"".join(parts))


def validate_disjoint_roots(
    *,
    input_roots: Iterable[str | Path],
    output_roots: Iterable[str | Path],
    forbidden_exact: Iterable[str | Path] = (),
) -> None:
    def normalized(value: str | Path) -> Path:
        path = Path(os.path.abspath(Path(value)))
        current = path
        while not current.exists() and current.parent != current:
            current = current.parent
        _reject_symlink_chain(current)
        return path.resolve(strict=False)

    inputs = [normalized(path) for path in input_roots]
    outputs = [normalized(path) for path in output_roots]
    forbidden = {normalized(path) for path in forbidden_exact}
    if len(outputs) != len(set(outputs)):
        raise ValueError("output roots alias each other")
    for output in outputs:
        if output == Path("/") or any(
            output == blocked or output in blocked.parents for blocked in forbidden
        ):
            raise ValueError(f"unsafe output root: {output}")
    combined = [("input", path) for path in inputs] + [("output", path) for path in outputs]
    for index, (left_kind, left) in enumerate(combined):
        for right_kind, right in combined[index + 1 :]:
            if left_kind == right_kind == "input":
                continue
            if left == right or left in right.parents or right in left.parents:
                raise ValueError(f"input/output roots overlap: {left} and {right}")
