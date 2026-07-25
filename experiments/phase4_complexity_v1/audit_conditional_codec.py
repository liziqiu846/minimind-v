#!/usr/bin/env python3
"""CPU-only audit of unified conditional messages; never trains or scores."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np
import torch

from experiments.phase4_complexity_v1.candidate_registry import (
    Candidate,
    load_candidate_registry,
    load_complexity_protocol,
)
from experiments.phase4_complexity_v1.conditional_codec import (
    QuantizedBlock,
    decode_conditional_message,
    encode_conditional_message,
    quantize_coordinates,
)
from experiments.phase4_complexity_v1.legacy_mms2_import import (
    import_legacy_mms2_v1_file,
)
from experiments.phase4_complexity_v1.freeze_verification import (
    verify_freeze_manifest,
)
from experiments.phase4_m4_v1.m4_configs import load_frozen_config
from experiments.phase4_m4_v1.mms2_v2 import encode_mms2_v2


UNIFORM_SEED = 440401
SPARSE_SEED = 440402
PROBE_NAMES = ("Z", "U", "S")
LEGACY_RELATIVE_PATHS = {
    0: "05_M2_root-43101_seed-2026_lr-0p050/encode/adapter.mms2",
    1: "06_M2_root-43102_seed-2026_lr-0p050/encode/adapter.mms2",
    2: "07_M2_root-43103_seed-2026_lr-0p050/encode/adapter.mms2",
    3: "08_M3_root-43101_seed-2026_lr-0p050/encode/adapter.mms2",
    4: "09_M3_root-43102_seed-2026_lr-0p050/encode/adapter.mms2",
    5: "10_M3_root-43103_seed-2026_lr-0p050/encode/adapter.mms2",
}
M4_ARCHIVE_BLOCK_NAMES = {
    "shared": "shared_coordinates",
    "vision_private": "vision_private_coordinates",
    "projector_private": "projector_private_coordinates",
    "language_private": "language_private_coordinates",
}


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _same_quantized_blocks(
    left: Mapping[str, QuantizedBlock],
    right: Mapping[str, QuantizedBlock],
) -> bool:
    return tuple(left) == tuple(right) and all(
        left[name].scale_bytes == right[name].scale_bytes
        and np.array_equal(left[name].symbols, right[name].symbols)
        for name in left
    )


def _conditional_round_trip(
    candidate: Candidate,
    blocks: Mapping[str, QuantizedBlock],
) -> tuple[bytes, dict[str, Any]]:
    first_message, encode_receipt = encode_conditional_message(
        candidate.candidate_id, blocks
    )
    decoded, decode_receipt = decode_conditional_message(first_message)
    second_message, second_receipt = encode_conditional_message(
        candidate.candidate_id, decoded
    )
    if (
        not _same_quantized_blocks(blocks, decoded)
        or first_message != second_message
        or encode_receipt != decode_receipt
        or encode_receipt != second_receipt
    ):
        raise AssertionError("conditional message round trip is not byte exact")
    return first_message, {
        **encode_receipt,
        "decode_reencode_byte_exact": True,
        "quantized_scale_and_symbols_exact": True,
    }


def _probe_values(
    candidate: Candidate,
    probe_name: str,
) -> OrderedDict[str, np.ndarray]:
    if probe_name not in PROBE_NAMES:
        raise ValueError("unknown codec probe")
    seed = None if probe_name == "Z" else (
        UNIFORM_SEED if probe_name == "U" else SPARSE_SEED
    )
    rng = None if seed is None else np.random.default_rng(seed)
    output: OrderedDict[str, np.ndarray] = OrderedDict()
    for block_name in candidate.block_order:
        dimension = candidate.block_dimensions[block_name]
        if probe_name == "Z":
            values = np.zeros(dimension, dtype=np.float32)
        elif probe_name == "U":
            values = np.resize(
                np.arange(-3, 4, dtype=np.float32), dimension
            ).copy()
            assert rng is not None
            rng.shuffle(values)
        else:
            zero_count = int(round(0.85 * dimension))
            nonzero_count = dimension - zero_count
            nonzero = np.resize(
                np.asarray((-3, -2, -1, 1, 2, 3), dtype=np.float32),
                nonzero_count,
            )
            values = np.concatenate(
                (
                    np.zeros(zero_count, dtype=np.float32),
                    nonzero,
                )
            )
            assert rng is not None
            rng.shuffle(values)
        output[block_name] = np.ascontiguousarray(values, dtype=np.float32)
    return output


def audit_legacy_models(
    registry: Mapping[int, Candidate],
    formal_root: Path,
) -> list[dict[str, Any]]:
    rows = []
    for candidate_id in range(6):
        candidate = registry[candidate_id]
        archive_path = formal_root / LEGACY_RELATIVE_PATHS[candidate_id]
        blocks, import_receipt = import_legacy_mms2_v1_file(
            archive_path, candidate_id
        )
        message, message_receipt = _conditional_round_trip(candidate, blocks)
        rows.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": candidate.candidate_name,
                "source_archive": import_receipt,
                "conditional_message": message_receipt,
                "conditional_message_sha256": hashlib.sha256(message).hexdigest(),
                "full_archive_bits": import_receipt["archive_bits"],
                "formal_training_certificate_replaced": False,
                "conditional_length_role": (
                    "post-hoc unified code-length comparison only"
                ),
            }
        )
    return rows


def audit_m4_probes(
    registry: Mapping[int, Candidate],
) -> list[dict[str, Any]]:
    rows = []
    for candidate_id in range(6, 15):
        candidate = registry[candidate_id]
        config, config_receipt = load_frozen_config(candidate.candidate_name)
        for probe_name in PROBE_NAMES:
            values = _probe_values(candidate, probe_name)
            blocks = OrderedDict(
                (name, quantize_coordinates(values[name]))
                for name in candidate.block_order
            )
            message, message_receipt = _conditional_round_trip(
                candidate, blocks
            )
            archive_coordinates: Dict[str, torch.Tensor] = {
                M4_ARCHIVE_BLOCK_NAMES[name]: torch.from_numpy(
                    values[name].copy()
                )
                for name in candidate.block_order
            }
            archive, archive_receipt = encode_mms2_v2(
                archive_coordinates, config
            )
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate.candidate_name,
                    "probe": probe_name,
                    "probe_seed": (
                        None
                        if probe_name == "Z"
                        else UNIFORM_SEED
                        if probe_name == "U"
                        else SPARSE_SEED
                    ),
                    "codec_probe": True,
                    "trained_model": False,
                    "certified": False,
                    "conditional_message": message_receipt,
                    "conditional_message_sha256": hashlib.sha256(
                        message
                    ).hexdigest(),
                    "full_archive_bits": archive_receipt["archive_bits"],
                    "full_archive_sha256": hashlib.sha256(archive).hexdigest(),
                    "mms2_v2_structure_metadata_bits": archive_receipt[
                        "structure_metadata_bits"
                    ],
                    "mms2_v2_structure_metadata_in_conditional_message": False,
                    "config": config_receipt,
                }
            )
    return rows


def run_audit(formal_root: Path) -> dict[str, Any]:
    freeze_receipt = verify_freeze_manifest()
    registry, registry_receipt = load_candidate_registry()
    _, protocol_receipt = load_complexity_protocol()
    legacy_rows = audit_legacy_models(registry, formal_root.resolve())
    probe_rows = audit_m4_probes(registry)
    all_messages = [
        row["conditional_message"] for row in legacy_rows + probe_rows
    ]
    if any(
        row["paid_field_bits_sum"] != row["conditional_message_bits"]
        for row in all_messages
    ):
        raise AssertionError("conditional message bit totals are inconsistent")
    return {
        "schema": "phase4-conditional-codec-audit-v1",
        "status": "passed",
        "protocol": protocol_receipt,
        "freeze": freeze_receipt,
        "candidate_registry": registry_receipt,
        "legacy_models": legacy_rows,
        "m4_codec_probes": probe_rows,
        "legacy_model_count": len(legacy_rows),
        "m4_probe_count": len(probe_rows),
        "formal_training_started": False,
        "full_risk_scoring_run": False,
        "formal_generalization_bound_computed": False,
        "legacy_M2_M3_certificate_reinterpretation": False,
        "new_M4_training_complexity_eligible_after_freeze": True,
    }


def _write_new_file(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-formal-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_audit(args.legacy_formal_root)
    payload = _canonical_json_bytes(result)
    if args.output is not None:
        _write_new_file(args.output.resolve(), payload)
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
