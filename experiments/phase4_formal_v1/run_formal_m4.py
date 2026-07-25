#!/usr/bin/env python3
"""Preflight, smoke, or run the sole authorized formal Phase 4 M4 model."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3_v6.scoring.common import read_json
from experiments.phase4_formal_v1 import (
    FORMAL_CANDIDATE_ID,
    FORMAL_CONFIG_ID,
    SCHEMA_VERSION,
)
from experiments.phase4_formal_v1.codec_integration import (
    CodecVerification,
    verify_codecs_from_coordinates,
)
from experiments.phase4_formal_v1.logits_verification import (
    verify_fixed_input_logits,
)
from experiments.phase4_formal_v1.runtime_gate import (
    SCORER_PYTHON,
    assert_runtime_binding,
    atomic_bytes,
    atomic_json,
    formal_paths,
    make_binding,
    run_preflight,
)
from experiments.phase4_m4_v1.m4_configs import (
    REPO_ROOT,
    load_frozen_config,
    sha256_file,
)
from experiments.phase4_m4_v1.quantize_m4 import quantize
from experiments.phase4_m4_v1.train_m4 import train


def _require_config(config_id: str) -> None:
    if config_id != FORMAL_CONFIG_ID:
        raise ValueError(
            f"formal Phase 4 v1 accepts only {FORMAL_CONFIG_ID}"
        )


def _synthetic_coordinates(
    config: Mapping[str, Any],
) -> dict[str, torch.Tensor]:
    output = {}
    for block_index, block_name in enumerate(
        config["coordinate_block_order"]
    ):
        dimension = int(config["coordinate_dimensions"][block_name])
        indices = torch.arange(dimension, dtype=torch.int64)
        signed = ((indices * (block_index + 3) + block_index) % 7) - 3
        coordinates = signed.to(torch.float32) * torch.tensor(
            0.125 * (block_index + 1), dtype=torch.float32
        )
        if coordinates.numel() != dimension:
            raise AssertionError("synthetic coordinate construction failed")
        output[block_name] = coordinates
    return output


def _receipt_with_binding(
    codec: CodecVerification,
    *,
    preflight: Mapping[str, Any],
    message_path: Path,
    archive_path: Path,
) -> dict[str, Any]:
    receipt = dict(codec.complexity_receipt)
    receipt.update(
        {
            "config_id": FORMAL_CONFIG_ID,
            "candidate_id": FORMAL_CANDIDATE_ID,
            "conditional_message_path": str(message_path),
            "conditional_message_sha256": sha256_file(message_path),
            "full_archive_path": str(archive_path),
            "full_archive_sha256": sha256_file(archive_path),
            "complexity_protocol_sha256": preflight["freeze"][
                "complexity_protocol_sha256"
            ],
            "candidate_manifest_sha256": preflight["freeze"][
                "candidate_manifest_sha256"
            ],
            "freeze_manifest_sha256": preflight["freeze"][
                "freeze_manifest_sha256"
            ],
            "git_commit_sha": preflight["git"]["commit_sha"],
            "zlib_runtime_version": preflight["zlib"]["runtime_version"],
        }
    )
    if (
        receipt["conditional_message_bits"]
        != receipt["paid_field_bits_sum"]
    ):
        raise RuntimeError("bound complexity receipt paid sum differs")
    return receipt


def _write_codec_artifacts(
    output: Path,
    codec: CodecVerification,
    *,
    preflight: Mapping[str, Any],
    write_archive: bool,
    existing_archive_path: Path | None = None,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    if write_archive:
        if existing_archive_path is not None:
            raise ValueError("smoke archive cannot also be externally supplied")
        archive_path = output / "adapter.mms2"
        atomic_bytes(archive_path, codec.archive)
    else:
        if existing_archive_path is None:
            raise ValueError("formal codec output requires its MMS2 archive path")
        archive_path = existing_archive_path.resolve()
        if (
            not archive_path.is_file()
            or archive_path.read_bytes() != codec.archive
        ):
            raise RuntimeError("existing formal MMS2 archive bytes differ")
    message_path = output / "conditional_message.bin"
    atomic_bytes(message_path, codec.conditional_message)
    complexity = _receipt_with_binding(
        codec,
        preflight=preflight,
        message_path=message_path,
        archive_path=archive_path,
    )
    complexity_path = output / "complexity_receipt.json"
    atomic_json(complexity_path, complexity)
    verification = dict(codec.verification_receipt)
    verification.update(
        {
            "complexity_receipt_path": str(complexity_path),
            "complexity_receipt_sha256": sha256_file(complexity_path),
        }
    )
    atomic_json(output / "codec_verification.json", verification)
    return {
        "complexity": complexity,
        "complexity_receipt_path": str(complexity_path),
        "codec_verification_path": str(output / "codec_verification.json"),
        "archive_path": str(archive_path),
        "conditional_message_path": str(message_path),
    }


def smoke(config_id: str) -> dict[str, Any]:
    _require_config(config_id)
    preflight = run_preflight(
        require_output_absent=True,
        require_control_absent=True,
        require_smoke_absent=True,
        require_gpu=True,
    )
    config, _ = load_frozen_config(config_id)
    root = Path(preflight["artifact_root"])
    output = formal_paths(root, config)["smoke_root"]
    output.mkdir(parents=True)
    started = time.time()
    binding = make_binding(preflight)
    try:
        coordinates = _synthetic_coordinates(config)
        codec = verify_codecs_from_coordinates(coordinates, config)
        artifacts = _write_codec_artifacts(
            output / "codec",
            codec,
            preflight=preflight,
            write_archive=True,
        )
        logits = verify_fixed_input_logits(
            config,
            root,
            codec.archive,
            codec.archive_coordinates,
            codec.conditional_coordinates,
            device="cuda:0",
        )
        atomic_json(output / "logits_verification.json", logits)
        assert_runtime_binding(binding)
        receipt = {
            "schema_version": SCHEMA_VERSION,
            "status": "passed",
            "artifact_class": (
                "synthetic_codec_and_model_smoke_not_a_trained_model"
            ),
            "eligible_as_formal_model": False,
            "config_id": config_id,
            "candidate_id": FORMAL_CANDIDATE_ID,
            "binding": binding,
            "preflight": preflight,
            "codec": artifacts,
            "logits_verification_path": str(
                output / "logits_verification.json"
            ),
            "logits_exact": logits["all_logits_exact"],
            "certified": False,
            "exploratory": True,
            "u_statistic_implemented": False,
            "risk_scoring_executed": False,
            "seconds": time.time() - started,
        }
        atomic_json(output / "smoke_receipt.json", receipt)
        return receipt
    except BaseException as error:
        atomic_json(
            output / "failure_receipt.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "failed",
                "artifact_class": "synthetic_smoke_failure",
                "config_id": config_id,
                "binding": binding,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def _verify_smoke(
    smoke_path: Path, binding: Mapping[str, Any]
) -> dict[str, Any]:
    if not smoke_path.is_file():
        raise FileNotFoundError("formal same-path smoke receipt is absent")
    receipt = read_json(smoke_path)
    if (
        receipt.get("status") != "passed"
        or receipt.get("artifact_class")
        != "synthetic_codec_and_model_smoke_not_a_trained_model"
        or receipt.get("eligible_as_formal_model") is not False
        or receipt.get("binding") != dict(binding)
        or receipt.get("logits_exact") is not True
        or receipt.get("certified") is not False
        or receipt.get("exploratory") is not True
    ):
        raise RuntimeError("formal same-path smoke receipt is invalid")
    return {
        "status": "passed",
        "path": str(smoke_path),
        "sha256": sha256_file(smoke_path),
    }


def _load_training_coordinates(
    manifest: Mapping[str, Any],
) -> dict[str, torch.Tensor]:
    path = Path(manifest["coordinates"]["path"]).resolve()
    if sha256_file(path) != manifest["coordinates"]["sha256"]:
        raise RuntimeError("trained coordinate payload hash changed")
    stored = torch.load(path, map_location="cpu", weights_only=True)
    if (
        stored.get("config_id") != FORMAL_CONFIG_ID
        or stored.get("method") != "M4"
        or stored.get("mapping_root") != 43101
    ):
        raise RuntimeError("trained coordinate payload identity differs")
    return stored["coordinates"]


def _run_scoring_process(
    *,
    root: Path,
    archive_path: Path,
    complexity_path: Path,
    binding_path: Path,
    output: Path,
) -> dict[str, Any]:
    if not SCORER_PYTHON.is_file():
        raise FileNotFoundError(SCORER_PYTHON)
    log_path = output.parent / "scoring_process.log"
    command = [
        str(SCORER_PYTHON),
        "-m",
        "experiments.phase4_formal_v1.score_formal_m4",
        "--artifact-root",
        str(root),
        "--archive",
        str(archive_path),
        "--complexity-receipt",
        str(complexity_path),
        "--binding-receipt",
        str(binding_path),
        "--output-dir",
        str(output),
        "--device",
        "cuda:0",
    ]
    environment = dict(os.environ)
    current_python_path = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not current_python_path
        else f"{REPO_ROOT}{os.pathsep}{current_python_path}"
    )
    with log_path.open("wb") as log:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"formal M4 scoring failed; see {log_path}"
        )
    receipt_path = output / "scoring_receipt.json"
    receipt = read_json(receipt_path)
    if (
        receipt.get("status") != "complete"
        or receipt.get("config_id") != FORMAL_CONFIG_ID
        or receipt.get("certified") is not False
        or receipt.get("exploratory") is not True
    ):
        raise RuntimeError("formal M4 scoring receipt is invalid")
    return {
        "receipt": receipt,
        "receipt_path": str(receipt_path),
        "receipt_sha256": sha256_file(receipt_path),
        "process_log_path": str(log_path),
        "process_log_sha256": sha256_file(log_path),
    }


def run_formal(config_id: str) -> dict[str, Any]:
    _require_config(config_id)
    preflight = run_preflight(
        require_output_absent=True,
        require_control_absent=True,
        require_smoke_absent=False,
        require_gpu=True,
    )
    config, config_receipt = load_frozen_config(config_id)
    root = Path(preflight["artifact_root"])
    paths = formal_paths(root, config)
    binding = make_binding(preflight)
    smoke_receipt = _verify_smoke(
        paths["smoke_root"] / "smoke_receipt.json", binding
    )
    control = paths["control_root"]
    control.mkdir(parents=True)
    binding_path = control / "start_receipt.json"
    start = {
        "schema_version": SCHEMA_VERSION,
        "status": "started",
        "config_id": config_id,
        "candidate_id": FORMAL_CANDIDATE_ID,
        "binding": binding,
        "preflight": preflight,
        "smoke": smoke_receipt,
        "config": config_receipt,
        "started_unix_time": time.time(),
        "automatic_retry": False,
    }
    atomic_json(binding_path, start)
    started = time.time()
    try:
        assert_runtime_binding(binding)
        training = train(config_id)
        assert_runtime_binding(binding)
        training_manifest_path = (
            paths["run_root"] / "training/training_manifest.json"
        )
        training_binding_path = (
            paths["run_root"] / "training/formal_training_receipt.json"
        )
        atomic_json(
            training_binding_path,
            {
                "schema_version": SCHEMA_VERSION,
                "status": "complete",
                "config_id": config_id,
                "candidate_id": FORMAL_CANDIDATE_ID,
                "binding": binding,
                "git_commit_sha": binding["git_commit_sha"],
                "freeze_manifest_sha256": binding[
                    "freeze_manifest_sha256"
                ],
                "training_manifest_path": str(training_manifest_path),
                "training_manifest_sha256": sha256_file(
                    training_manifest_path
                ),
                "frozen_parameters_unchanged": training["model"][
                    "frozen_parameters_unchanged"
                ],
                "optimizer_steps": training["training"]["optimizer_steps"],
                "seconds": training["seconds"],
            },
        )
        quantization = quantize(config_id)
        assert_runtime_binding(binding)

        coordinates = _load_training_coordinates(training)
        archive_path = Path(quantization["archive_path"]).resolve()
        archive = archive_path.read_bytes()
        codec = verify_codecs_from_coordinates(
            coordinates, config, archive=archive
        )
        complexity_root = paths["run_root"] / "complexity"
        artifacts = _write_codec_artifacts(
            complexity_root,
            codec,
            preflight=preflight,
            write_archive=False,
            existing_archive_path=archive_path,
        )
        complexity_path = Path(artifacts["complexity_receipt_path"])
        logits = verify_fixed_input_logits(
            config,
            root,
            archive,
            codec.archive_coordinates,
            codec.conditional_coordinates,
            device="cuda:0",
        )
        logits_path = paths["run_root"] / "verification/logits.json"
        atomic_json(logits_path, logits)
        assert_runtime_binding(binding)

        scoring = _run_scoring_process(
            root=root,
            archive_path=archive_path,
            complexity_path=complexity_path,
            binding_path=binding_path,
            output=paths["run_root"] / "risk",
        )
        assert_runtime_binding(binding)
        complexity = artifacts["complexity"]
        risk = scoring["receipt"]
        final = {
            "schema_version": SCHEMA_VERSION,
            "status": "complete",
            "config_id": config_id,
            "candidate_id": FORMAL_CANDIDATE_ID,
            "binding": binding,
            "preflight": preflight,
            "smoke": smoke_receipt,
            "training": {
                "manifest_path": str(training_manifest_path),
                "manifest_sha256": sha256_file(
                    training_manifest_path
                ),
                "formal_training_receipt_path": str(training_binding_path),
                "formal_training_receipt_sha256": sha256_file(
                    training_binding_path
                ),
                "seconds": training["seconds"],
                "mean_micro_batch_loss": training["training"][
                    "mean_micro_batch_loss"
                ],
                "optimizer_steps": training["training"]["optimizer_steps"],
            },
            "quantization": {
                "adapter_summary_path": str(
                    paths["run_root"] / "encode/adapter_summary.json"
                ),
                "adapter_summary_sha256": sha256_file(
                    paths["run_root"] / "encode/adapter_summary.json"
                ),
                "archive_path": str(archive_path),
                "archive_sha256": quantization["archive_sha256"],
                "archive_bits": quantization["archive_bits"],
            },
            "complexity": {
                "receipt_path": str(complexity_path),
                "receipt_sha256": sha256_file(complexity_path),
                "conditional_message_path": artifacts[
                    "conditional_message_path"
                ],
                "conditional_message_sha256": complexity[
                    "conditional_message_sha256"
                ],
                "conditional_message_bits": complexity[
                    "conditional_message_bits"
                ],
                "full_archive_bits": complexity["full_archive_bits"],
            },
            "logits_verification": {
                "path": str(logits_path),
                "sha256": sha256_file(logits_path),
                "all_logits_exact": logits["all_logits_exact"],
            },
            "risk": {
                "receipt_path": scoring["receipt_path"],
                "receipt_sha256": scoring["receipt_sha256"],
                "q_correct": risk["q_correct"],
                "q_mismatch_mean": risk["q_mismatch_mean"],
                "mismatch_baseline_risk": risk[
                    "mismatch_baseline_risk"
                ],
                "visual_gain": risk["visual_gain"],
                "joint_semantic_risk": risk["joint_semantic_risk"],
                "certified": False,
                "exploratory": True,
            },
            "formal_visual_generalization_certified": False,
            "u_statistic_implemented": False,
            "other_m4_candidates_run": False,
            "seconds": time.time() - started,
        }
        final_path = paths["run_root"] / "formal_run_receipt.json"
        atomic_json(final_path, final)
        atomic_json(
            control / "completion_receipt.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "complete",
                "config_id": config_id,
                "binding": binding,
                "formal_run_receipt_path": str(final_path),
                "formal_run_receipt_sha256": sha256_file(final_path),
                "seconds": final["seconds"],
            },
        )
        return final
    except BaseException as error:
        atomic_json(
            control / "failure_receipt.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "failed",
                "config_id": config_id,
                "binding": binding,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "smoke", "run"):
        child = subparsers.add_parser(name)
        child.add_argument("--config-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _require_config(args.config_id)
    if args.command == "preflight":
        result = run_preflight(
            require_output_absent=True,
            require_control_absent=True,
            require_smoke_absent=False,
            require_gpu=True,
        )
    elif args.command == "smoke":
        result = smoke(args.config_id)
    else:
        result = run_formal(args.config_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
