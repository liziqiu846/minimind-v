#!/usr/bin/env python3
"""Audit actual MMS2 v2 section lengths without altering any bound."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.phase4_m4_v1.mms2_v2 import (
    decode_mms2_v2,
    inspect_mms2_v2_directory,
)


COMPONENT_FIELDS = (
    "structure_metadata_bits",
    "shared_coordinate_bits",
    "vision_private_coordinate_bits",
    "projector_private_coordinate_bits",
    "language_private_coordinate_bits",
)


def audit_archive(payload: bytes) -> dict[str, Any]:
    _, metadata = decode_mms2_v2(payload)
    directory = inspect_mms2_v2_directory(payload)
    component_sum = sum(int(metadata[name]) for name in COMPONENT_FIELDS)
    if component_sum != len(payload) * 8:
        raise AssertionError("MMS2 v2 component bits do not equal archive bits")
    if (
        [row["section_name"] for row in directory].count(
            "shared_coordinates"
        )
        != 1
    ):
        raise AssertionError("shared coordinates are not encoded exactly once")
    return {
        "status": "passed",
        "archive_sha256": hashlib.sha256(payload).hexdigest(),
        "archive_bits": len(payload) * 8,
        **{name: int(metadata[name]) for name in COMPONENT_FIELDS},
        "component_bits_sum": component_sum,
        "component_bits_equal_archive_bits": True,
        "candidate_selection_bits": int(
            metadata["candidate_selection_bits"]
        ),
        "candidate_selection_bits_in_archive": False,
        "candidate_selection_bits_added_to_bound": False,
        "shared_section_occurrences": 1,
        "directory": directory,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    result = audit_archive(args.archive.read_bytes())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
