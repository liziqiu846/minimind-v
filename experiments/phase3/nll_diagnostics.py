"""Pickle-free NLL sequence storage and deterministic tail summaries."""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from experiments.phase3.canonical_io import atomic_write_jsonl, load_jsonl_snapshot, snapshot_file


CONDITION_CODES = {"correct": 0, "none": 1, "lm_only": 2}
ROLE_CODES = {"pos1": 0, "pos2": 1, "negative": 2}
STRATA = {
    (0, 0): "correct_positive",
    (0, 1): "correct_positive",
    (0, 2): "correct_negative",
    (1, 0): "none_positive",
    (1, 1): "none_positive",
    (1, 2): "none_negative",
    (2, 0): "lm_only_positive",
    (2, 1): "lm_only_positive",
    (2, 2): "lm_only_negative",
}


def _summary(values: np.ndarray, *, thresholds: bool) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("NLL summary requires a finite nonempty vector")
    result = {
        "minimum": float(np.min(array)),
        "mean": float(np.mean(array, dtype=np.float64)),
        "standard_deviation": float(np.std(array, ddof=0, dtype=np.float64)),
        "p50": float(np.quantile(array, 0.50, method="linear")),
        "p90": float(np.quantile(array, 0.90, method="linear")),
        "p95": float(np.quantile(array, 0.95, method="linear")),
        "p99": float(np.quantile(array, 0.99, method="linear")),
        "p99_5": float(np.quantile(array, 0.995, method="linear")),
        "maximum": float(np.max(array)),
    }
    if thresholds:
        result.update({f"proportion_gt_{limit}": float(np.mean(array > limit)) for limit in (10, 15, 20, 30)})
    return result


def sequence_summary(values: np.ndarray) -> dict[str, Any]:
    result = _summary(values, thresholds=False)
    return {
        "sequence_mean_nll_bits": result["mean"],
        "sequence_min_token_nll_bits": result["minimum"],
        "sequence_max_token_nll_bits": result["maximum"],
        "sequence_p95_token_nll_bits": result["p95"],
        "valid_token_count": int(np.asarray(values).size),
    }


def write_nll_store(directory: str | Path, entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    rows = list(entries)
    if not rows:
        raise ValueError("NLL store requires at least one sequence")
    values_parts: list[np.ndarray] = []
    offsets = [0]
    condition_codes = []
    role_codes = []
    row_indices = []
    index_rows = []
    for row in rows:
        values = np.asarray(row["values"], dtype=np.float32)
        if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
            raise ValueError("NLL sequence is invalid")
        start, end = offsets[-1], offsets[-1] + values.size
        values_parts.append(values)
        offsets.append(end)
        condition = CONDITION_CODES[row["condition"]]
        role = ROLE_CODES[row["caption_role"]]
        condition_codes.append(condition)
        role_codes.append(role)
        row_indices.append(int(row["row_index"]))
        metadata = {
                "row_index": int(row["row_index"]),
                "row_key": str(row["row_key"]),
                "model_id": str(row["model_id"]),
                "filename": str(row["filename"]),
                "category": str(row["category"]),
                "numeric_id": int(row["numeric_id"]),
                "condition_code": condition,
                "caption_role_code": role,
                "start_offset": start,
                "end_offset": end,
                **sequence_summary(values),
            }
        index_rows.append(metadata)
    arrays = {
        "values": np.concatenate(values_parts).astype(np.float32, copy=False),
        "offsets": np.asarray(offsets, dtype=np.int64),
        "condition_codes": np.asarray(condition_codes, dtype=np.uint8),
        "caption_role_codes": np.asarray(role_codes, dtype=np.uint8),
        "row_indices": np.asarray(row_indices, dtype=np.int64),
    }
    target = root / "nll_tokens.npz"
    descriptor, temporary_name = tempfile.mkstemp(prefix=".nll_tokens.", suffix=".npz", dir=root)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        np.savez_compressed(temporary, **arrays)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        directory_descriptor = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()
    loaded = validate_nll_store(root)
    for index, metadata in enumerate(index_rows):
        start = int(loaded["offsets"][index])
        end = int(loaded["offsets"][index + 1])
        metadata.update(sequence_summary(loaded["values"][start:end].astype(np.float64)))
    atomic_write_jsonl(root / "nll_index.jsonl", index_rows)
    persisted_index = load_jsonl_snapshot(root / "nll_index.jsonl", root=root)
    return summarize_nll(loaded, persisted_index)


def validate_nll_store(directory: str | Path) -> dict[str, np.ndarray]:
    root = Path(directory)
    payload = snapshot_file(root / "nll_tokens.npz", root=root)
    with np.load(io.BytesIO(payload), allow_pickle=False) as source:
        required = ("values", "offsets", "condition_codes", "caption_role_codes", "row_indices")
        if set(source.files) != set(required):
            raise ValueError("NLL NPZ members differ from frozen schema")
        arrays = {name: source[name].copy() for name in required}
    values, offsets = arrays["values"], arrays["offsets"]
    sequence_count = len(offsets) - 1
    if (
        values.dtype != np.float32
        or offsets.dtype != np.int64
        or arrays["condition_codes"].dtype != np.uint8
        or arrays["caption_role_codes"].dtype != np.uint8
        or arrays["row_indices"].dtype != np.int64
    ):
        raise ValueError("NLL NPZ dtype mismatch")
    if any(array.ndim != 1 for array in arrays.values()) or not np.all(np.isfinite(values)):
        raise ValueError("NLL NPZ arrays must be finite one-dimensional arrays")
    if offsets[0] != 0 or offsets[-1] != len(values) or np.any(np.diff(offsets) <= 0):
        raise ValueError("NLL offsets are invalid")
    if any(len(arrays[name]) != sequence_count for name in required[2:]):
        raise ValueError("NLL sequence-level arrays are misaligned")
    if not np.all(np.isin(arrays["condition_codes"], np.asarray(tuple(CONDITION_CODES.values()), dtype=np.uint8))):
        raise ValueError("NLL condition code is invalid")
    if not np.all(np.isin(arrays["caption_role_codes"], np.asarray(tuple(ROLE_CODES.values()), dtype=np.uint8))):
        raise ValueError("NLL caption role code is invalid")
    if np.any(arrays["row_indices"] < 0):
        raise ValueError("NLL row index is negative")
    return arrays


def summarize_nll(arrays: dict[str, np.ndarray], index_rows: list[dict[str, Any]]) -> dict[str, Any]:
    offsets = arrays["offsets"]
    if len(index_rows) != len(offsets) - 1:
        raise ValueError("NLL index length mismatch")
    required_index_keys = {
        "row_index", "row_key", "model_id", "filename", "category", "numeric_id",
        "condition_code", "caption_role_code", "start_offset", "end_offset",
        "valid_token_count", "sequence_mean_nll_bits", "sequence_min_token_nll_bits",
        "sequence_max_token_nll_bits", "sequence_p95_token_nll_bits",
    }
    sequence_means = []
    stratum_tokens: dict[str, list[np.ndarray]] = {}
    stratum_means: dict[str, list[float]] = {}
    ordering = []
    logical_sequences = []
    model_ids = set()
    for index, row in enumerate(index_rows):
        if set(row) != required_index_keys:
            raise ValueError("NLL index schema mismatch")
        if (
            int(row["start_offset"]) != int(offsets[index])
            or int(row["end_offset"]) != int(offsets[index + 1])
            or int(row["condition_code"]) != int(arrays["condition_codes"][index])
            or int(row["caption_role_code"]) != int(arrays["caption_role_codes"][index])
            or int(row["row_index"]) != int(arrays["row_indices"][index])
        ):
            raise ValueError("NLL index/NPZ alignment mismatch")
        values = arrays["values"][offsets[index] : offsets[index + 1]].astype(np.float64)
        expected = sequence_summary(values)
        for key, value in expected.items():
            if not np.isclose(float(row[key]), float(value), atol=1e-10, rtol=1e-10):
                raise ValueError(f"NLL index summary mismatch: {key}")
        model_ids.add(str(row["model_id"]))
        ordering.append(
            (
                str(row["filename"]).encode("utf-8"),
                str(row["category"]).encode("utf-8"),
                int(row["numeric_id"]),
                int(row["condition_code"]),
                int(row["caption_role_code"]),
            )
        )
        logical_sequences.append(
            (int(row["row_index"]), int(row["condition_code"]), int(row["caption_role_code"]))
        )
        sequence_means.append(expected["sequence_mean_nll_bits"])
        stratum = STRATA.get((int(row["condition_code"]), int(row["caption_role_code"])))
        if stratum is None:
            raise ValueError("unknown NLL condition/role code")
        stratum_tokens.setdefault(stratum, []).append(values)
        stratum_means.setdefault(stratum, []).append(expected["sequence_mean_nll_bits"])
    if len(model_ids) != 1 or ordering != sorted(ordering) or len(logical_sequences) != len(set(logical_sequences)):
        raise ValueError("NLL index model/order/sequence uniqueness mismatch")
    by_row: dict[int, set[tuple[int, int]]] = {}
    for row_index, condition, role in logical_sequences:
        by_row.setdefault(row_index, set()).add((condition, role))
    lm_expected = {(2, role) for role in (0, 1, 2)}
    vlm_expected = {(condition, role) for condition in (0, 1) for role in (0, 1, 2)}
    patterns = set()
    for memberships in by_row.values():
        if memberships == lm_expected:
            patterns.add("lm_only")
        elif memberships == vlm_expected:
            patterns.add("vlm")
        else:
            raise ValueError("NLL row does not have the exact frozen logical sequence membership")
    if len(patterns) != 1:
        raise ValueError("NLL model mixes LM-only and VLM sequence memberships")
    only_model = next(iter(model_ids))
    expected_pattern = "lm_only" if only_model.startswith("M0-") else "vlm"
    if patterns != {expected_pattern}:
        raise ValueError("NLL condition pattern disagrees with model identity")
    strata = {}
    for name in sorted(stratum_tokens, key=lambda value: value.encode("utf-8")):
        tokens = np.concatenate(stratum_tokens[name])
        means = np.asarray(stratum_means[name], dtype=np.float64)
        strata[name] = {
            "token_level": _summary(tokens, thresholds=True),
            "caption_level": _summary(means, thresholds=False),
            "token_count": int(tokens.size),
            "sequence_count": int(means.size),
        }
    return {
        "token_level": _summary(arrays["values"].astype(np.float64), thresholds=True),
        "caption_level": _summary(np.asarray(sequence_means, dtype=np.float64), thresholds=False),
        "token_count": int(len(arrays["values"])),
        "sequence_count": len(sequence_means),
        "strata": strata,
    }
