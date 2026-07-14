#!/usr/bin/env python3
"""Verify a public experiment bundle and, when complete, recompute its bound."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.build_public_bundle import INDEX_NAME, sha256_file
from experiments.compute_bound_report import (
    build_report,
    decoder_registry_selection,
    validate_manifest,
)
from experiments.phase2_protocol import FrozenProtocol


CERTIFICATE_ROLES = {
    "protocol",
    "decoder_registry",
    "compressed_model",
    "encoding",
    "train_risk",
    "validation_correct",
    "bound",
    "dataset_receipt",
    "train_membership",
    "validation_membership",
    "run_manifest",
    "environment",
}

RECOMPUTED_FIELDS = (
    "run_id",
    "certificate_uses_training_risk_only",
    "confidence_delta",
    "independent_train_samples",
    "encoded_weight_bits",
    "alpha_choice_bits",
    "model_selection_bits",
    "total_hyperparameter_bits",
    "description_complexity_nats",
    "archive_sha256",
    "decoded_checkpoint_sha256",
    "decoded_state_sha256",
    "training_data_sha256",
    "validation_data_sha256",
    "model_assets",
    "best_alpha",
    "best_compression_upper_bound_bits",
    "best_beats_random_guess",
    "bounds",
)


def _require(label: str, actual, expected) -> None:
    if actual != expected:
        raise ValueError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def artifact_map(bundle_dir: Path) -> dict[str, Path]:
    """Verify the bundle index and return role-to-file mappings."""
    bundle_dir = Path(bundle_dir).resolve()
    index = json.loads((bundle_dir / INDEX_NAME).read_text(encoding="utf-8"))
    if index.get("schema_version") != 1:
        raise ValueError("unsupported bundle index schema")
    entries = index.get("artifacts", [])
    roles = [entry["role"] for entry in entries]
    if len(roles) != len(set(roles)):
        raise ValueError("bundle roles must be unique")

    result = {}
    for entry in entries:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"artifact path is not safely relative: {relative}")
        path = (bundle_dir / relative).resolve()
        try:
            path.relative_to(bundle_dir)
        except ValueError as error:
            raise ValueError(f"artifact escapes bundle: {relative}") from error
        if not path.is_file():
            raise FileNotFoundError(f"missing bundle artifact: {relative}")
        _require(f"{entry['role']} bytes", path.stat().st_size, entry["bytes"])
        _require(f"{entry['role']} sha256", sha256_file(path), entry["sha256"])
        result[entry["role"]] = path
    return result


def _load_json(paths: dict[str, Path], role: str) -> dict:
    return json.loads(paths[role].read_text(encoding="utf-8"))


def _verify_protocol_reference(artifact: dict, reference: dict, role: str) -> None:
    _require(f"{role} protocol reference", artifact.get("protocol"), reference)


def _verify_split_link(
    artifact: dict,
    role: str,
    receipt_sha256: str,
    output: dict,
) -> None:
    split = artifact.get("dataset_split")
    if not split:
        raise ValueError(f"{role} lacks its dataset split receipt link")
    _require(f"{role} split role", split.get("role"), role)
    _require(
        f"{role} split manifest sha256",
        split.get("manifest_sha256"),
        receipt_sha256,
    )
    _require(f"{role} data sha256", split.get("artifact_sha256"), output["sha256"])
    _require(f"{role} example count", split.get("examples"), output["rows"])


def _verify_model_assets(protocol: dict, manifest: dict, training: dict) -> None:
    declared = {entry["role"]: entry["sha256"] for entry in protocol.get("assets", [])}
    if not declared:
        return
    if "initial_llm" in declared:
        _require(
            "initial model asset sha256",
            manifest["initial_weight"]["sha256"],
            declared["initial_llm"],
        )
    risk_assets = training["model_assets"]
    observed = {
        "tokenizer_json": risk_assets["tokenizer"]["files"]["tokenizer.json"],
        "tokenizer_config": risk_assets["tokenizer"]["files"][
            "tokenizer_config.json"
        ],
        "vision_config": risk_assets["vision_model"]["files"]["config.json"],
        "vision_weights": risk_assets["vision_model"]["files"][
            "model.safetensors"
        ],
        "vision_processor": risk_assets["vision_model"]["files"][
            "preprocessor_config.json"
        ],
    }
    for role, sha256 in observed.items():
        _require(f"{role} asset sha256", sha256, declared.get(role))


def _verify_run_configuration(protocol: dict, manifest: dict) -> None:
    _require("protocol run id", manifest["run_id"], protocol["run_id"])
    model = manifest["model"]
    projector = model["projector"]
    observed_model = {
        "hidden_size": model["hidden_size"],
        "num_hidden_layers": model["num_hidden_layers"],
        "use_moe": model["use_moe"],
        "freeze_llm": model["freeze_llm"],
        "projector_type": projector["type"],
        "subspace_dim": projector["subspace_dim"],
        "subspace_seed": projector["subspace_seed"],
        "train_norm": projector["train_norm"],
        "fixed_state_sha256": projector["fixed_state_sha256"],
        "projector_protocol": projector["protocol"],
        "initial_weight_name": manifest["initial_weight"]["name"],
    }
    for key, expected in protocol["model"].items():
        if key not in observed_model:
            raise ValueError(f"run manifest lacks frozen model field: {key}")
        _require(f"model {key}", observed_model[key], expected)
    observed_training = manifest["training"]
    for key, expected in protocol["training"].items():
        if key not in observed_training:
            raise ValueError(f"run manifest lacks frozen training field: {key}")
        _require(f"training {key}", observed_training[key], expected)


def _compare_recomputed(expected, observed, location: str) -> None:
    if isinstance(expected, float):
        if not isinstance(observed, (int, float)) or not math.isclose(
            expected, observed, rel_tol=1e-12, abs_tol=1e-12
        ):
            raise ValueError(f"recomputed {location} differs from bundled bound")
    elif isinstance(expected, dict):
        if not isinstance(observed, dict):
            raise ValueError(f"recomputed {location} differs from bundled bound")
        for key, value in expected.items():
            if key not in observed:
                raise ValueError(f"bundled bound lacks {location}.{key}")
            _compare_recomputed(value, observed[key], f"{location}.{key}")
    elif isinstance(expected, list):
        if not isinstance(observed, list) or len(expected) != len(observed):
            raise ValueError(f"recomputed {location} differs from bundled bound")
        for index, (left, right) in enumerate(zip(expected, observed)):
            _compare_recomputed(left, right, f"{location}[{index}]")
    elif expected != observed:
        raise ValueError(f"recomputed {location} differs from bundled bound")


def _verify_certificate(paths: dict[str, Path]) -> dict:
    protocol = FrozenProtocol.load(paths["protocol"])
    reference = protocol.reference()
    registry = _load_json(paths, "decoder_registry")
    encoding = _load_json(paths, "encoding")
    training = _load_json(paths, "train_risk")
    validation = _load_json(paths, "validation_correct")
    bound = _load_json(paths, "bound")
    receipt = _load_json(paths, "dataset_receipt")
    manifest = _load_json(paths, "run_manifest")

    environment_path = paths["environment"]
    _require(
        "environment file name",
        environment_path.name,
        Path(protocol.payload["environment_path"]).name,
    )
    _require(
        "environment sha256",
        sha256_file(environment_path),
        protocol.payload["environment_sha256"],
    )

    for role, artifact in (
        ("encoding", encoding),
        ("train_risk", training),
        ("validation_correct", validation),
        ("bound", bound),
    ):
        _verify_protocol_reference(artifact, reference, role)
    for role, artifact in (("dataset_receipt", receipt), ("run_manifest", manifest)):
        _require(f"{role} protocol id", artifact.get("protocol_id"), reference["protocol_id"])
        _require(
            f"{role} protocol sha256",
            artifact.get("protocol_sha256"),
            reference["protocol_sha256"],
        )

    registry_spec = protocol.payload["decoder_registry"]
    _require(
        "decoder registry file name",
        paths["decoder_registry"].name,
        Path(registry_spec["path"]).name,
    )
    registry_sha256 = sha256_file(paths["decoder_registry"])
    declared_registry_hashes = [registry_spec["sha256"]] if "sha256" in registry_spec else []
    declared_registry_hashes.extend(
        entry["sha256"]
        for entry in protocol.payload.get("implementation_files", [])
        if entry["path"] == registry_spec["path"]
    )
    if not declared_registry_hashes:
        raise ValueError("protocol does not freeze the decoder registry hash")
    for declared_sha256 in declared_registry_hashes:
        _require("protocol decoder registry sha256", registry_sha256, declared_sha256)
    selected = registry["decoders"][registry_spec["index"]]
    _require("encoded decoder choice", encoding["decoder_choice"], selected["choice"])
    if encoding.get("decoder_id") is not None:
        _require("encoded decoder id", encoding["decoder_id"], selected["id"])
    choice_count, choice_bits = decoder_registry_selection(
        registry, encoding["decoder_choice"]
    )
    certificate = protocol.payload["certificate"]
    _require(
        "protocol decoder selection bits",
        certificate["decoder_selection_bits"],
        choice_bits,
    )
    _require("bound decoder choice count", bound.get("decoder_choice_count"), choice_count)
    _require("bound decoder choice", bound.get("decoder_choice"), encoding["decoder_choice"])
    _require(
        "bound decoder registry sha256",
        bound.get("decoder_registry_sha256"),
        registry_sha256,
    )

    archive_sha256 = sha256_file(paths["compressed_model"])
    archive_bits = paths["compressed_model"].stat().st_size * 8
    _require("encoding archive sha256", encoding["archive_sha256"], archive_sha256)
    _require("encoding archive bits", encoding["encoded_weight_bits"], archive_bits)
    _require("bound archive sha256", bound["archive_sha256"], archive_sha256)

    receipt_sha256 = sha256_file(paths["dataset_receipt"])
    train_output = receipt["outputs"]["train"]
    validation_output = receipt["outputs"]["validation"]
    dataset_spec = protocol.payload.get("dataset", {})
    _require("dataset image overlap", receipt.get("image_overlap"), 0)
    if "source_sha256" in dataset_spec:
        _require("dataset source sha256", receipt["source_sha256"], dataset_spec["source_sha256"])
    if "train_size" in dataset_spec:
        _require("train split size", train_output["rows"], dataset_spec["train_size"])
        _require(
            "validation split size",
            validation_output["rows"],
            dataset_spec["validation_size"],
        )
    for key in (
        "seed",
        "selection",
        "excluded_unique_images",
        "all_phase1_selection_images_excluded",
    ):
        if key in dataset_spec:
            _require(f"dataset {key}", receipt.get(key), dataset_spec[key])
    if "exclude_sha256" in dataset_spec:
        _require(
            "dataset exclusions",
            [item["sha256"] for item in receipt["exclusions"]],
            dataset_spec["exclude_sha256"],
        )
    for role, output in (
        ("train_membership", train_output),
        ("validation_membership", validation_output),
    ):
        membership = output["membership"]
        _require(f"{role} sha256", sha256_file(paths[role]), membership["sha256"])
        _require(f"{role} bytes", paths[role].stat().st_size, membership["bytes"])
    _require("training risk data sha256", training["data_sha256"], train_output["sha256"])
    _require("training risk sample count", training["sample_count"], train_output["rows"])
    _require(
        "validation risk data sha256",
        validation["data_sha256"],
        validation_output["sha256"],
    )
    _require(
        "validation risk sample count", validation["sample_count"], validation_output["rows"]
    )
    _verify_split_link(manifest, "train", receipt_sha256, train_output)
    _verify_split_link(training, "train", receipt_sha256, train_output)
    _verify_split_link(validation, "validation", receipt_sha256, validation_output)
    validate_manifest(manifest, encoding, training)
    _verify_run_configuration(protocol.payload, manifest)
    _verify_model_assets(protocol.payload, manifest, training)
    _require(
        "bound run manifest sha256",
        bound.get("run_manifest_sha256"),
        sha256_file(paths["run_manifest"]),
    )

    _require(
        "certificate alpha",
        [row["alpha"] for row in training["risks"]],
        [certificate["alpha"]],
    )
    _require(
        "certificate alpha selection bits",
        training["alpha_choice_bits"],
        certificate["alpha_selection_bits"],
    )
    recomputed = build_report(
        encoding,
        training,
        validation,
        certificate["confidence_delta"],
        archive_bits,
        choice_bits,
    )
    for field in RECOMPUTED_FIELDS:
        if field not in bound:
            raise ValueError(f"bundled bound lacks {field}")
        _compare_recomputed(recomputed[field], bound[field], field)
    return {
        "run_id": recomputed["run_id"],
        "archive_sha256": archive_sha256,
        "encoded_weight_bits": archive_bits,
        "best_alpha": recomputed["best_alpha"],
        "best_compression_upper_bound_bits": recomputed[
            "best_compression_upper_bound_bits"
        ],
    }


def verify_public_bundle(bundle_dir: Path) -> dict:
    paths = artifact_map(bundle_dir)
    certificate = (
        _verify_certificate(paths) if CERTIFICATE_ROLES.issubset(paths) else None
    )
    return {
        "schema_version": 1,
        "verified_artifacts": len(paths),
        "roles": sorted(paths),
        "certificate_verified": certificate is not None,
        "certificate": certificate,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    args = parser.parse_args()
    result = verify_public_bundle(args.bundle_dir)
    if not result["certificate_verified"]:
        raise ValueError("bundle is missing required certificate artifacts")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
