"""Train/reuse, module-codec, freeze-check, and development-evaluate one run."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch

from experiments.phase3_module_marginal_budget_v1.codec import (
    encode_coordinates,
)
from experiments.phase3_module_marginal_budget_v1.parameterization import (
    build_candidate_model,
)
from experiments.phase3_private_vs_shared_v1.artifacts import write_json_atomic
from experiments.phase3_private_vs_shared_v1.common import REPO_ROOT, sha256_file
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH as PS_PROTOCOL_PATH,
)
from experiments.phase3_private_vs_shared_v1.train_one import train_candidate
from experiments.phase3_v6.scoring.protocol import verify_protocol

from . import EVALUATION_ROLE, MODULES
from .design import training_config
from .manifest import runtime_source_hashes, verify_frozen_manifest

DEVELOPMENT_PYTHON = Path(
    "/home/lizhaohui/lzq/phase3_runtime/phase3_v5/env/bin/python"
)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def formal_binding(
    manifest_path: Path, run: Mapping[str, Any]
) -> dict[str, Any]:
    manifest = verify_frozen_manifest(manifest_path)
    sources = runtime_source_hashes()
    if sources != manifest["runtime_source_sha256"]:
        raise ValueError("runtime sources differ from frozen manifest")
    return {
        "experiment_manifest_sha256": sha256_file(manifest_path),
        "source_curve_run_plan_sha256": manifest["source_experiment"][
            "run_plan_sha256"
        ],
        "phase3_ps_protocol_sha256": sha256_file(PS_PROTOCOL_PATH),
        "run_id": run["run_id"],
        "base_state": run["base_state"],
        "module": run["module"],
        "evaluation_role": EVALUATION_ROLE,
        "runtime_source_sha256": sources,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("branch", "--show-current"),
        "worktree_status_at_start": _git("status", "--porcelain"),
    }


def _validate_binding(payload: Mapping[str, Any], expected: Mapping[str, Any]):
    if {key: payload.get(key) for key in expected} != dict(expected):
        raise ValueError("training artifact binding differs")


def _persist_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"existing codec artifact differs: {path}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _module_codec(
    checkpoint_path: Path, output: Path
) -> tuple[dict[str, Any], dict[str, str]]:
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    coordinates = checkpoint.get("coordinates")
    if not isinstance(coordinates, Mapping):
        raise ValueError("training checkpoint has no coordinate mapping")
    archives, receipt = encode_coordinates(coordinates)
    paths = {}
    for module, payload in archives.items():
        path = output / "codec" / f"{module}.mmb1"
        _persist_bytes(path, payload)
        paths[module] = str(path)
    write_json_atomic(output / "codec" / "receipt.json", receipt)
    return receipt, paths


def _development_result(
    run: Mapping[str, Any],
    *,
    manifest_path: Path,
    checkpoint_path: Path,
    codec_root: Path,
    output: Path,
    device: str,
) -> dict[str, Any]:
    _, protocol_sha256 = verify_protocol()
    evaluation_dir = output / "development_evaluation"
    result_path = evaluation_dir / "development_result.json"
    if result_path.exists():
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    else:
        log_path = output / "logs" / "development_evaluation.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(DEVELOPMENT_PYTHON),
            "-m",
            "experiments.phase3_state_dependent_marginal_v1.development_eval",
            "--plan",
            str(manifest_path.resolve()),
            "--run-id",
            str(run["run_id"]),
            "--codec-root",
            str(codec_root.resolve()),
            "--checkpoint",
            str(checkpoint_path.resolve()),
            "--output-dir",
            str(evaluation_dir.resolve()),
            "--device",
            device,
        ]
        environment = dict(os.environ)
        environment["PYTHONUNBUFFERED"] = "1"
        with log_path.open("wb") as log:
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        if completed.returncode:
            raise RuntimeError(
                "development evaluation failed with return code "
                f"{completed.returncode}; see {log_path}"
            )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    if (
        payload.get("run_id") != run["run_id"]
        or payload.get("config_id") != run["config_id"]
        or payload.get("seed") != run["seed"]
        or payload.get("evaluation_role") != EVALUATION_ROLE
        or payload.get("status") != "complete"
        or payload.get("development_protocol_sha256") != protocol_sha256
        or payload.get("curve_run_plan_sha256") != sha256_file(manifest_path)
        or payload.get("checkpoint_sha256") != sha256_file(checkpoint_path)
        or payload.get("decoded_coordinate_dimensions")
        != run["coordinate_dimensions"]
    ):
        raise ValueError("development evaluation result identity differs")
    return {
        "evaluation_role": EVALUATION_ROLE,
        "development_task_risk": float(payload["development_task_risk"]),
        "semantic_risk_bound": float(payload["semantic_risk_bound"]),
        "visual_gain_guardrail": float(payload["visual_gain_guardrail"]),
        "development_protocol_id": payload["development_protocol_id"],
        "development_protocol_sha256": payload["development_protocol_sha256"],
        "development_assignment_core_sha256": payload[
            "development_assignment_core_sha256"
        ],
        "development_input_sha256": payload["development_input_sha256"],
        "development_record_count": int(payload["development_record_count"]),
        "development_image_count": int(payload["development_image_count"]),
        "development_evaluation_result_path": str(result_path),
        "development_evaluation_result_sha256": sha256_file(result_path),
    }


def execute_run(
    run: Mapping[str, Any],
    *,
    manifest_path: Path,
    results_root: Path,
    artifact_root: Path | None,
    device: str,
) -> dict[str, Any]:
    """Execute one frozen base or candidate model without changing its config."""
    manifest = verify_frozen_manifest(manifest_path)
    binding = formal_binding(manifest_path, run)
    output = results_root.resolve() / run["result_relative_directory"]
    output.mkdir(parents=True, exist_ok=True)
    if run["run_type"] == "reused_base":
        source = run["source"]
        checkpoint_path = Path(source["checkpoint_path"])
        training_manifest_path = Path(source["training_manifest_path"])
        training_status = "reused_previous_checkpoint"
    else:
        if artifact_root is None:
            raise ValueError("candidate training requires artifact_root")
        config = training_config(run)
        training_manifest = train_candidate(
            str(run["config_id"]),
            artifact_root,
            results_root.resolve() / "training_artifacts",
            device,
            config_override=config,
            binding_override=binding,
            binding_validator=lambda payload: _validate_binding(payload, binding),
            model_builder=build_candidate_model,
        )
        checkpoint_path = Path(training_manifest["checkpoint"]["path"])
        training_manifest_path = (
            results_root.resolve()
            / "training_artifacts"
            / run["config_id"]
            / "training_manifest.json"
        )
        training_status = "new_training"
    if not checkpoint_path.is_file() or not training_manifest_path.is_file():
        raise FileNotFoundError("bound checkpoint or training manifest is absent")
    codec, codec_paths = _module_codec(checkpoint_path, output)
    risk = _development_result(
        run,
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        codec_root=output / "codec",
        output=output,
        device=device,
    )
    module_bits = {
        module: int(codec[f"{module}_encoded_bits"]) for module in MODULES
    }
    target_module = run["module"]
    return {
        **binding,
        "schema_version": 1,
        "protocol_id": manifest["protocol_id"],
        "protocol_version": manifest["protocol_version"],
        "config_id": run["config_id"],
        "run_type": run["run_type"],
        "base_state": run["base_state"],
        "module": target_module,
        "coordinate_dimensions": dict(run["coordinate_dimensions"]),
        "seed": int(run["seed"]),
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "training_manifest_path": str(training_manifest_path),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "vision_encoded_bits": module_bits["vision"],
        "projector_encoded_bits": module_bits["projector"],
        "language_encoded_bits": module_bits["language"],
        "module_wise_encoded_bits": module_bits,
        "target_module_encoded_bits": (
            None if target_module is None else module_bits[target_module]
        ),
        "total_encoded_bits": int(codec["total_encoded_bits"]),
        "module_codec_paths": codec_paths,
        "codec_receipt_path": str(output / "codec" / "receipt.json"),
        **risk,
        "training_status": training_status,
        "run_status": "complete",
        "status": "complete",
    }

