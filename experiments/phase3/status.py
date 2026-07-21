"""Structured Phase 3 status and exit-code handling."""

from __future__ import annotations

import argparse
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from experiments.phase3.canonical_io import atomic_write_json


EXIT_CODES = {"success": 0, "hard_failure": 1, "blocked": 2, "cli_error": 64}


class Phase3ArgumentParser(argparse.ArgumentParser):
    """Argparse variant implementing the frozen Phase 3 CLI-error exit code."""

    def error(self, message: str) -> None:
        self.print_usage()
        self.exit(EXIT_CODES["cli_error"], f"{self.prog}: error: {message}\n")


@dataclass
class Phase3Blocked(Exception):
    code: str
    detail: str


@dataclass
class Phase3HardFailure(Exception):
    code: str
    detail: str


def status_payload(
    command: str,
    status: str,
    status_code: str,
    *,
    blocking_items: list[dict[str, Any]] | None = None,
    hard_failures: list[dict[str, Any]] | None = None,
    completed_actions: list[str] | None = None,
    skipped_actions: list[str] | None = None,
    outputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in ("success", "blocked", "hard_failure"):
        raise ValueError(f"invalid status: {status}")
    return {
        "schema_version": 1,
        "command": command,
        "status": status,
        "status_code": status_code,
        "blocking_items": blocking_items or [],
        "hard_failures": hard_failures or [],
        "completed_actions": completed_actions or [],
        "skipped_actions": skipped_actions or [],
        "outputs": outputs or {},
    }


def execute_with_status(
    command: str,
    status_output: str | Path,
    operation: Callable[[], dict[str, Any] | None],
) -> int:
    target = Path(status_output)
    # A pre-existing status path may itself be an input file (or a broken
    # symlink).  Refuse before invoking the operation so an error report can
    # never overwrite user data.  There is intentionally no attempt to write
    # a second status object to the already-occupied path.
    if target.exists() or target.is_symlink():
        return EXIT_CODES["hard_failure"]
    try:
        result = operation() or {}
        payload = status_payload(
            command,
            "success",
            "success",
            completed_actions=list(result.pop("completed_actions", [])),
            skipped_actions=list(result.pop("skipped_actions", [])),
            outputs=result,
        )
    except Phase3Blocked as error:
        payload = status_payload(
            command,
            "blocked",
            error.code,
            blocking_items=[{"code": error.code, "detail": error.detail}],
        )
    except Phase3HardFailure as error:
        payload = status_payload(
            command,
            "hard_failure",
            error.code,
            hard_failures=[{"code": error.code, "detail": error.detail}],
        )
    except Exception as error:  # defensive CLI boundary
        payload = status_payload(
            command,
            "hard_failure",
            "unhandled_exception",
            hard_failures=[{"code": type(error).__name__, "detail": str(error)}],
        )
    try:
        atomic_write_json(target, payload, overwrite=False)
    except FileExistsError:
        # A concurrent creator won the status-path race.  Preserve its bytes.
        return EXIT_CODES["hard_failure"]
    return EXIT_CODES[payload["status"]]


def require_status_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--status-output", type=Path, required=True)
