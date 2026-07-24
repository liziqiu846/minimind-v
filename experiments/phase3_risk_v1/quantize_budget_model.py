#!/usr/bin/env python3
"""Quantize one trained budget model and verify MMS2 decode/load equivalence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import torch

from experiments.phase3_risk_v1.budget_codec import (
    decode_budget_mms2,
    encode_budget_mms2,
)
from experiments.phase3_risk_v1.budget_runtime import (
    build_budget_model,
    load_frozen_config,
    verify_budget_runtime,
)
from experiments.phase3_v6.scoring.common import (
    atomic_write_bytes,
    atomic_write_json,
    sha256_file,
)
from experiments.stage2_model import (
    model_structure_receipt,
    tensor_state_sha256,
)
from model.global_subspace_lora import (
    coordinate_state,
    load_coordinate_state,
)


def _save_torch_atomic(path: Path, value) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def quantize(args: argparse.Namespace) -> dict:
    config, config_receipt = load_frozen_config(args.config_id)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"encode output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol, runtime = verify_budget_runtime(
        config,
        artifact_root=args.artifact_root,
        require_gpu=False,
    )
    training_manifest = json.loads(
        args.training_manifest.read_text(encoding="utf-8")
    )
    if (
        training_manifest.get("status") != "complete"
        or training_manifest.get("config_id") != config["config_id"]
        or training_manifest.get("config", {}).get("sha256")
        != config_receipt["sha256"]
    ):
        raise ValueError("training manifest does not match frozen config")
    coordinates_path = Path(
        training_manifest["coordinates"]["path"]
    ).resolve()
    if sha256_file(coordinates_path) != training_manifest["coordinates"][
        "sha256"
    ]:
        raise ValueError("trained coordinate file hash mismatch")
    saved = torch.load(
        coordinates_path, map_location="cpu", weights_only=True
    )
    if (
        saved.get("config_id") != config["config_id"]
        or saved.get("config_sha256") != config_receipt["sha256"]
        or saved.get("model_group") != config["method"]
        or int(saved.get("mapping_root")) != int(config["mapping_root"])
    ):
        raise ValueError("coordinate payload identity differs from config")
    coordinates = saved["coordinates"]
    dimensions = {
        name: int(value.numel()) for name, value in coordinates.items()
    }
    if dimensions != config["coordinate_dimensions"]:
        raise ValueError("coordinate payload dimensions differ from config")

    archive, codec_summary = encode_budget_mms2(
        coordinates,
        config["method"],
        int(config["mapping_root"]),
        config["coordinate_dimensions"],
    )
    decoded, decoded_metadata = decode_budget_mms2(
        archive, config["coordinate_dimensions"]
    )
    reencoded, _ = encode_budget_mms2(
        decoded,
        config["method"],
        int(config["mapping_root"]),
        config["coordinate_dimensions"],
    )
    if reencoded != archive:
        raise RuntimeError("budget MMS2 decode/re-encode is not byte exact")

    model = build_budget_model(
        config, protocol, device="cpu", dtype=torch.float32
    )
    load_coordinate_state(model, decoded)
    loaded = coordinate_state(model)
    for name in decoded:
        if not torch.equal(loaded[name], decoded[name]):
            raise RuntimeError(f"MMS2 loader changed decoded group {name}")

    archive_path = output / "adapter.mms2"
    decoded_path = output / "decoded_coordinates.pt"
    atomic_write_bytes(archive_path, archive)
    _save_torch_atomic(
        decoded_path,
        {
            "coordinates": decoded,
            "config_id": config["config_id"],
            "config_sha256": config_receipt["sha256"],
            "model_group": config["method"],
            "mapping_root": config["mapping_root"],
            "codec": "MMS2 version 1 zlib-9",
        },
    )
    archive_sha = hashlib.sha256(archive).hexdigest()
    archive_bits = len(archive) * 8
    external_selection_bits = int(config["external_selection_bits"])
    external_hyperparameter_bits = int(
        config["external_hyperparameter_bits"]
    )
    summary = {
        **codec_summary,
        "schema_version": 1,
        "status": "complete",
        "config_id": config["config_id"],
        "config": config_receipt,
        "budget": config["budget"],
        "total_coordinate_budget": config["total_coordinate_budget"],
        "archive_path": str(archive_path),
        "archive_sha256": archive_sha,
        "archive_bits": archive_bits,
        "external_selection_bits": external_selection_bits,
        "external_selection_bits_rule": (
            "ceil(log2(candidate_family_size))"
        ),
        "candidate_family_size": config["candidate_family_size"],
        "external_hyperparameter_bits": external_hyperparameter_bits,
        "mms2_header_recounted_as_external_metadata": False,
        "total_description_bits": (
            archive_bits
            + external_selection_bits
            + external_hyperparameter_bits
        ),
        "total_description_bits_definition": (
            "archive_bits + external_selection_bits + "
            "external_hyperparameter_bits"
        ),
        "comparison_claim": (
            "equal_coordinate_budget_not_equal_description_length"
        ),
        "actual_description_length_is_an_observed_result": True,
        "quantization_levels": config["quantization"]["levels"],
        "decode_reencode_byte_equivalence": True,
        "existing_coordinate_loader_equivalence": True,
        "decoded_coordinates_path": str(decoded_path),
        "decoded_coordinates_sha256": sha256_file(decoded_path),
        "decoded_coordinate_state_sha256": tensor_state_sha256(decoded),
        "decoded_model_coordinate_state_sha256": tensor_state_sha256(loaded),
        "decoded_model_structure": model_structure_receipt(model),
        "training_manifest_path": str(args.training_manifest.resolve()),
        "training_manifest_sha256": sha256_file(args.training_manifest),
        "runtime_preflight": runtime,
    }
    atomic_write_json(output / "adapter_summary.json", summary)
    atomic_write_json(
        output / "decoded_model_hash.json",
        {
            "status": "passed",
            "config_id": config["config_id"],
            "archive_sha256": archive_sha,
            "decode_reencode_byte_equivalence": True,
            "existing_coordinate_loader_equivalence": True,
            "coordinate_state_sha256": tensor_state_sha256(loaded),
        },
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--training-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = quantize(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
