"""Fresh-confirmation manifest validation and disjoint frozen pairing."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

from .common import canonical_bytes, load_json, sha256_file


def validate_confirmation_manifest(path: Path | None,
                                   *, forbidden_hashes: Sequence[str] = ()) -> dict[str, Any]:
    if path is None:
        raise ValueError("formal confirmation requires --confirmation-manifest")
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = load_json(path)
    if payload.get("purpose") != "fresh_final_confirmation":
        raise ValueError("manifest is not declared as a fresh final confirmation set")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("confirmation manifest has no records")
    ids = [str(record.get("sample_id", "")) for record in records]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("confirmation sample IDs must be non-empty and unique")
    for record in records:
        if not all(record.get(key) for key in ("sample_id", "image", "text")):
            raise ValueError("confirmation record lacks sample_id/image/text")
    file_hash = sha256_file(path)
    content_hash = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    if file_hash in forbidden_hashes or content_hash in forbidden_hashes:
        raise ValueError("known development set cannot be used for confirmation")
    return {
        "path": str(path.resolve()),
        "manifest_sha256": file_hash,
        "canonical_content_sha256": content_hash,
        "sample_count": len(records),
        "records": records,
    }


def disjoint_pairs(records: Sequence[Mapping[str, Any]], seed: int) -> dict[str, Any]:
    if len(records) < 2:
        raise ValueError("formal disjoint pairing requires at least two samples")
    ids = [str(record["sample_id"]) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("pairing input contains repeated samples")
    indices = list(range(len(records)))
    random.Random(int(seed)).shuffle(indices)
    permutation_ids = [ids[index] for index in indices]
    dropped_sample_id = None
    if len(indices) % 2:
        dropped_index = indices.pop()
        dropped_sample_id = ids[dropped_index]
    output = []
    used: set[str] = set()
    donors: set[str] = set()
    for offset in range(0, len(indices), 2):
        first = records[indices[offset]]
        second = records[indices[offset + 1]]
        first_id, second_id = str(first["sample_id"]), str(second["sample_id"])
        if (first_id == second_id or first_id in used or second_id in used
                or first_id in donors or second_id in donors):
            raise AssertionError("invalid disjoint pairing")
        used.update((first_id, second_id))
        donors.update((first_id, second_id))
        output.append({
            "first_sample_id": first_id,
            "second_sample_id": second_id,
            "first_direction": {
                "text": first["text"],
                "correct_image": first["image"],
                "mismatch_donor_sample_id": second_id,
                "mismatch_image": second["image"],
            },
            "second_direction": {
                "text": second["text"],
                "correct_image": second["image"],
                "mismatch_donor_sample_id": first_id,
                "mismatch_image": first["image"],
            },
        })
    expected_used = len(records) - (1 if dropped_sample_id is not None else 0)
    if len(used) != expected_used or dropped_sample_id in used:
        raise AssertionError("pairing consumption differs from frozen odd-sample rule")
    return {
        "pairing_seed": int(seed),
        "input_sample_count": len(records),
        "pair_count": len(output),
        "dropped_sample_id": dropped_sample_id,
        "permutation_sample_ids": permutation_ids,
        "permutation_sha256": hashlib.sha256(
            canonical_bytes(permutation_ids)
        ).hexdigest(),
        "pairs": output,
        "pair_manifest_sha256": hashlib.sha256(
            canonical_bytes(output)
        ).hexdigest(),
    }
