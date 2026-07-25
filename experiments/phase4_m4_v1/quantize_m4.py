#!/usr/bin/env python3
"""Quantize one trained M4 config into a self-describing MMS2 v2 archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase4_m4_v1.m4_configs import (
    load_frozen_config,
    sha256_file,
)
from experiments.phase4_m4_v1.mms2_v2 import (
    decode_mms2_v2,
    encode_mms2_v2,
)
from experiments.phase4_m4_v1.train_m4 import ARTIFACT_ROOT_ENV
from experiments.stage2_model import tensor_state_sha256


def _atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _atomic_torch(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def encode_quantized_state(
    coordinates: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any], dict[str, torch.Tensor]]:
    archive, summary = encode_mms2_v2(coordinates, config)
    decoded, decoded_summary = decode_mms2_v2(archive)
    reencoded, _ = encode_mms2_v2(decoded, config)
    if reencoded != archive:
        raise RuntimeError("MMS2 v2 decode/re-encode is not byte exact")
    if summary["archive_bits"] != decoded_summary["archive_bits"]:
        raise RuntimeError("MMS2 v2 encoder/decoder bit accounting differs")
    return archive, {
        **summary,
        "decode_reencode_byte_equivalence": True,
        "decoded_coordinate_state_sha256": tensor_state_sha256(decoded),
    }, decoded


def _artifact_root() -> Path:
    value = os.environ.get(ARTIFACT_ROOT_ENV, "").strip()
    if not value:
        raise ValueError(
            f"{ARTIFACT_ROOT_ENV} must identify the immutable runtime root"
        )
    return Path(value).resolve()


def quantize(config_id: str) -> dict[str, Any]:
    config, config_receipt = load_frozen_config(config_id)
    run_root = _artifact_root() / config["output_relative_path"]
    training_manifest_path = run_root / "training/training_manifest.json"
    training_manifest = json.loads(
        training_manifest_path.read_text(encoding="utf-8")
    )
    if (
        training_manifest.get("status") != "complete"
        or training_manifest.get("config_id") != config_id
        or training_manifest.get("config", {}).get("sha256")
        != config_receipt["sha256"]
    ):
        raise ValueError("M4 training manifest differs from frozen config")
    coordinates_path = Path(
        training_manifest["coordinates"]["path"]
    ).resolve()
    if sha256_file(coordinates_path) != training_manifest["coordinates"][
        "sha256"
    ]:
        raise ValueError("M4 trained coordinate file hash mismatch")
    stored = torch.load(
        coordinates_path, map_location="cpu", weights_only=True
    )
    if (
        stored.get("config_id") != config_id
        or stored.get("config_sha256") != config_receipt["sha256"]
        or stored.get("method") != "M4"
        or int(stored.get("mapping_root", -1)) != config["mapping_root"]
    ):
        raise ValueError("M4 coordinate payload identity differs from config")

    archive, summary, decoded = encode_quantized_state(
        stored["coordinates"], config
    )
    output = run_root / "encode"
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"M4 encode output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / "adapter.mms2"
    decoded_path = output / "decoded_coordinates.pt"
    _atomic_bytes(archive_path, archive)
    _atomic_torch(
        decoded_path,
        {
            "coordinates": decoded,
            "config_id": config_id,
            "config_sha256": config_receipt["sha256"],
            "method": "M4",
            "mapping_root": config["mapping_root"],
            "codec": "MMS2 v2 five-section zlib-9",
        },
    )
    receipt = {
        **summary,
        "schema_version": 1,
        "status": "complete",
        "config_id": config_id,
        "config": config_receipt,
        "archive_path": str(archive_path),
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "decoded_coordinates_path": str(decoded_path),
        "decoded_coordinates_sha256": sha256_file(decoded_path),
        "candidate_selection_bits_added_to_archive_bits": False,
        "candidate_selection_bits_added_to_generalization_bound": False,
        "certified": False,
        "exploratory": True,
    }
    _atomic_json(output / "adapter_summary.json", receipt)
    return receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = quantize(args.config_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
