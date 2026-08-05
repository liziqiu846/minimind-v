"""One-run development runtime composed from established Phase 3 primitives."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3_private_vs_shared_v1.artifacts import (
    write_json_atomic,
)
from experiments.phase3_private_vs_shared_v1.common import REPO_ROOT, sha256_file
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH as PS_PROTOCOL_PATH,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    validate_frozen_protocol,
)
from experiments.phase3_private_vs_shared_v1.train_one import train_candidate
from experiments.phase3_v6.scoring.protocol import verify_protocol

from .codec import encode_coordinates
from .configs import make_baseline, make_single_module_candidate
from .formal_plan import verify_formal_run_plan
from .parameterization import build_candidate_model

DEVELOPMENT_PYTHON = Path(
    "/home/lizhaohui/lzq/phase3_runtime/phase3_v5/env/bin/python"
)
EVALUATION_ROLE = "development_only"


def _runtime_source_hashes() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    sources = {
        str(path.relative_to(REPO_ROOT)): sha256_file(path)
        for path in sorted(package.glob("*.py"))
    }
    reused_training = REPO_ROOT / "experiments/phase3_private_vs_shared_v1/train_one.py"
    sources[str(reused_training.relative_to(REPO_ROOT))] = sha256_file(reused_training)
    return sources


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def _formal_binding(plan_path: Path, run: Mapping[str, Any]) -> dict[str, Any]:
    plan = verify_formal_run_plan(plan_path)
    validate_frozen_protocol()
    if plan["status"] != "frozen":
        raise ValueError("curve run plan is not frozen")
    return {
        "curve_run_plan_sha256": sha256_file(plan_path),
        "curve_manifest_sha256": plan["curve_manifest_sha256"],
        "phase3_ps_protocol_sha256": sha256_file(PS_PROTOCOL_PATH),
        "run_id": run["run_id"],
        "evaluation_role": EVALUATION_ROLE,
        "runtime_source_sha256": _runtime_source_hashes(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("branch", "--show-current"),
        "worktree_status_at_start": _git("status", "--porcelain"),
    }


def _validate_binding(payload: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    if {key: payload.get(key) for key in expected} != dict(expected):
        raise ValueError("curve training artifact binding differs")


def _training_config(
    run: Mapping[str, Any], anchor_dimensions: Mapping[str, int]
) -> dict[str, Any]:
    baseline = make_baseline(
        str(run["config_id"])
        if run["target_module"] is None
        else f"P-4096-anchor-seed-{run['seed']}",
        anchor_dimensions,
        int(run["seed"]),
    )
    if run["target_module"] is None:
        return baseline.as_training_config()
    candidate = make_single_module_candidate(
        baseline,
        str(run["target_module"]),
        int(run["coordinate_dimensions"][run["target_module"]]),
        config_id=str(run["config_id"]),
        allow_decrease=True,
    )
    return candidate.as_training_config()


def _persist_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"existing codec artifact differs: {path}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


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
    plan_path: Path,
    checkpoint_path: Path,
    codec_root: Path,
    output: Path,
    device: str,
) -> dict[str, Any]:
    _, authoritative_protocol_sha256 = verify_protocol()
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
            "experiments.phase3_module_marginal_budget_v1.development_eval",
            "--plan",
            str(plan_path.resolve()),
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
        or payload.get("evaluation_role") != EVALUATION_ROLE
        or payload.get("status") != "complete"
        or payload.get("development_protocol_sha256")
        != authoritative_protocol_sha256
        or payload.get("curve_run_plan_sha256") != sha256_file(plan_path)
        or payload.get("checkpoint_sha256") != sha256_file(checkpoint_path)
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


def execute_formal_run(
    run: Mapping[str, Any],
    *,
    plan_path: Path,
    results_root: Path,
    artifact_root: Path | None,
    device: str,
) -> dict[str, Any]:
    """Train or reuse one run, module-codec it, and evaluate development risk."""
    plan = verify_formal_run_plan(plan_path)
    binding = _formal_binding(plan_path, run)
    output = results_root.resolve() / run["result_relative_directory"]
    output.mkdir(parents=True, exist_ok=True)
    if run["anchor_reuse"]:
        source = run["anchor_source"]
        checkpoint_path = Path(source["checkpoint_path"])
        training_manifest_path = Path(source["training_manifest_path"])
        training_status = "reused_authoritative_p4096"
    else:
        if artifact_root is None:
            raise ValueError("non-anchor curve training requires artifact_root")
        training_config = _training_config(
            run, plan["anchor_config"]["coordinate_dimensions"]
        )
        training_manifest = train_candidate(
            str(run["config_id"]),
            artifact_root,
            results_root.resolve() / "training_artifacts",
            device,
            config_override=training_config,
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
        training_status = "trained"
    if not checkpoint_path.is_file() or not training_manifest_path.is_file():
        raise FileNotFoundError("bound training checkpoint or manifest is absent")
    codec, codec_paths = _module_codec(checkpoint_path, output)
    risk = _development_result(
        run,
        plan_path=plan_path,
        checkpoint_path=checkpoint_path,
        codec_root=output / "codec",
        output=output,
        device=device,
    )
    module_bits = {
        module: int(codec[f"{module}_encoded_bits"])
        for module in ("vision", "projector", "language")
    }
    target_module = run["target_module"]
    return {
        **binding,
        "schema_version": 1,
        "protocol_version": run["protocol_version"],
        "config_id": run["config_id"],
        "sweep_config_id": run["sweep_config_id"],
        "curve_name": run["curve_name"],
        "curve_memberships": run["curve_memberships"],
        "target_module": target_module,
        "anchor_config": run["anchor_config"],
        "coordinate_dimensions": dict(run["coordinate_dimensions"]),
        "sweep_index": run["sweep_index"],
        "seed": int(run["seed"]),
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "training_manifest_path": str(training_manifest_path),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "vision_encoded_bits": int(codec["vision_encoded_bits"]),
        "projector_encoded_bits": int(codec["projector_encoded_bits"]),
        "language_encoded_bits": int(codec["language_encoded_bits"]),
        "module_wise_encoded_bits": module_bits,
        "target_module_encoded_bits": (
            None if target_module is None else module_bits[target_module]
        ),
        "target_module_encoded_bits_by_curve": (
            module_bits if target_module is None else None
        ),
        "total_encoded_bits": int(codec["total_encoded_bits"]),
        "module_codec_paths": codec_paths,
        "codec_receipt_path": str(output / "codec" / "receipt.json"),
        **risk,
        "training_status": training_status,
        "run_status": "complete",
        "status": "complete",
    }
