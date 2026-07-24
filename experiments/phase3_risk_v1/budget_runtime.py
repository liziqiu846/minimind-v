"""Runtime verification and model construction for frozen budget configs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

import torch

from experiments.phase3.stage2_adapter_loader import (
    verify_stage2_source_integrity,
)
from experiments.phase3_risk_v1.budget_adapter import (
    reconfigure_budget_adapter,
)
from experiments.phase3_risk_v1.budget_configs import (
    CANDIDATE_FAMILY_SIZE,
    load_and_validate_directory,
)
from experiments.phase3_v6.scoring.common import (
    REPO_ROOT,
    canonical_json_bytes,
    sha256_file,
)
from experiments.stage2_model import build_stage2_model
from experiments.stage2_protocol import load_target_registry


CONFIG_DIR = REPO_ROOT / "experiments/phase3_risk_v1/configs"
STAGE2_PROTOCOL_PATH = REPO_ROOT / "experiments/stage2_protocol_v2.json"
V6_PYTHON_PATH = Path(
    "/home/lizhaohui/lzq/phase3_runtime/phase3_v5/env/bin/python"
)


def load_frozen_config(config_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load one config only after validating the complete 18-member manifest."""

    validation = load_and_validate_directory(CONFIG_DIR)
    manifest = json.loads(
        (CONFIG_DIR / "manifest.json").read_text(encoding="utf-8")
    )
    matches = [
        row for row in manifest["entries"] if row["config_id"] == config_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate frozen config: {config_id}")
    entry = matches[0]
    path = CONFIG_DIR / entry["relative_path"]
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("selected config hash differs from manifest")
    config = json.loads(payload)
    if config["candidate_family_size"] != CANDIDATE_FAMILY_SIZE:
        raise ValueError("candidate family size differs from frozen manifest")
    return config, {
        "path": str(path.resolve()),
        "sha256": digest,
        "manifest_path": str((CONFIG_DIR / "manifest.json").resolve()),
        "manifest_sha256": sha256_file(CONFIG_DIR / "manifest.json"),
        "directory_validation": validation,
    }


def git_receipt() -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()

    return {
        "head_commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "tracked_status": git("status", "--porcelain", "--untracked-files=no"),
    }


def _normalized_pip_sha256() -> str:
    lines = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--all"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.splitlines()
    normalized = (
        "\n".join(
            sorted(
                (line.strip() for line in lines if line.strip()),
                key=str.lower,
            )
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def gpu_inventory() -> list[dict[str, Any]]:
    """Return the live physical inventory and active-compute state."""

    rows = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,uuid,memory.free",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.splitlines()
    process_result = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=gpu_uuid",
            "--format=csv,noheader,nounits",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    active = {
        line.strip()
        for line in process_result.stdout.splitlines()
        if line.strip()
    }
    output = []
    for line in rows:
        index, name, uuid, free = (value.strip() for value in line.split(","))
        output.append(
            {
                "index": int(index),
                "name": name,
                "uuid": uuid,
                "free_memory_mib": int(free),
                "active_compute_process": uuid in active,
            }
        )
    return output


def available_eligible_gpus(
    protocol,
    *,
    allow_shared: bool = False,
    minimum_free_memory_mib: int = 0,
) -> list[dict[str, Any]]:
    hardware = protocol.payload["hardware_execution"]
    eligible = set(hardware["eligible_gpu_uuids"])
    substring = str(hardware["required_gpu_name_substring"])
    rows = [
        row
        for row in gpu_inventory()
        if row["uuid"] in eligible
        and substring in row["name"]
        and (
            not row["active_compute_process"]
            or (
                allow_shared
                and row["free_memory_mib"] >= minimum_free_memory_mib
            )
        )
    ]
    return sorted(
        rows, key=lambda row: (-row["free_memory_mib"], row["uuid"])
    )


def verify_gpu_preflight(protocol, *, require_idle: bool = True) -> dict[str, Any]:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if not visible or "," in visible or not visible.startswith("GPU-"):
        raise ValueError(
            "budget execution requires exactly one physical GPU UUID in "
            "CUDA_VISIBLE_DEVICES"
        )
    hardware = protocol.payload["hardware_execution"]
    if visible not in hardware["eligible_gpu_uuids"]:
        raise ValueError("execution GPU is outside the frozen A40 pool")
    matches = [row for row in gpu_inventory() if row["uuid"] == visible]
    if len(matches) != 1:
        raise ValueError("selected execution GPU is absent or duplicated")
    selected = matches[0]
    if hardware["required_gpu_name_substring"] not in selected["name"]:
        raise ValueError("selected execution device is not an eligible A40")
    allow_shared = os.environ.get("PHASE3_ALLOW_SHARED_GPU", "") == "1"
    minimum_free_memory_mib = int(
        os.environ.get("PHASE3_MIN_FREE_MEMORY_MIB", "0")
    )
    if minimum_free_memory_mib < 0:
        raise ValueError("shared-GPU minimum free memory must be non-negative")
    if require_idle and selected["active_compute_process"] and not allow_shared:
        raise ValueError("selected execution A40 has an active compute process")
    if (
        selected["active_compute_process"]
        and allow_shared
        and selected["free_memory_mib"] < minimum_free_memory_mib
    ):
        raise ValueError(
            "selected shared A40 has less free memory than the declared "
            "safety threshold"
        )
    return {
        "policy": hardware["policy"],
        "idle_definition": hardware["idle_definition"],
        "uuid": selected["uuid"],
        "name": selected["name"],
        "physical_index": selected["index"],
        "free_memory_mib": selected["free_memory_mib"],
        "idle_at_preflight": not selected["active_compute_process"],
        "shared_gpu_execution": bool(selected["active_compute_process"]),
        "shared_gpu_user_authorized": allow_shared,
        "minimum_free_memory_mib": minimum_free_memory_mib,
    }


def verify_budget_runtime(
    config: Mapping[str, Any],
    *,
    artifact_root: Path,
    require_gpu: bool,
    environment_mode: str = "stage2",
) -> tuple[Any, dict[str, Any]]:
    """Verify unchanged Stage2 sources, config, data, environment, and GPU."""

    protocol = verify_stage2_source_integrity(str(STAGE2_PROTOCOL_PATH))
    data_path = artifact_root.resolve() / config["data"][
        "training_relative_path"
    ]
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    data_sha = sha256_file(data_path)
    if data_sha != config["data"]["training_sha256"]:
        raise ValueError("training data SHA-256 differs from frozen config")
    if environment_mode not in ("stage2", "v6"):
        raise ValueError("environment_mode must be stage2 or v6")
    expected_python = (
        Path(protocol.payload["environment"]["python_executable"])
        if environment_mode == "stage2"
        else V6_PYTHON_PATH
    ).resolve()
    if Path(sys.executable).resolve() != expected_python:
        raise ValueError(
            f"budget {environment_mode} stage must use Python "
            f"{expected_python}, got "
            f"{Path(sys.executable).resolve()}"
        )
    pip_sha = None
    if environment_mode == "stage2":
        pip_sha = _normalized_pip_sha256()
        expected_pip = protocol.payload["environment"]["pip_freeze_sha256"]
        if pip_sha != expected_pip:
            raise ValueError(
                "live Python environment differs from frozen pip receipt"
            )
    gpu = verify_gpu_preflight(protocol) if require_gpu else None
    return protocol, {
        "status": "passed",
        "config_id": config["config_id"],
        "stage2_protocol": protocol.reference(),
        "training_data": {
            "path": str(data_path),
            "sha256": data_sha,
        },
        "environment": {
            "mode": environment_mode,
            "python_executable": str(Path(sys.executable).resolve()),
            "pip_freeze_sha256": pip_sha,
        },
        "gpu": gpu,
        "git": git_receipt(),
    }


def build_budget_model(
    config: Mapping[str, Any],
    protocol,
    *,
    device: str | torch.device,
    dtype: torch.dtype = torch.float32,
):
    method = str(config["method"])
    root = int(config["mapping_root"])
    model = build_stage2_model(
        method, protocol, root, device=device, dtype=dtype
    )
    reconfigure_budget_adapter(
        model,
        method,
        root,
        load_target_registry(),
        config["coordinate_dimensions"],
    )
    dimensions = {
        name: parameter.numel()
        for name, parameter in model.stage2_coordinates.ordered()
    }
    if dimensions != config["coordinate_dimensions"]:
        raise RuntimeError("constructed coordinate dimensions differ from config")
    if sum(dimensions.values()) != int(config["total_coordinate_budget"]):
        raise RuntimeError("constructed coordinate budget differs from config")
    return model


def receipt_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
