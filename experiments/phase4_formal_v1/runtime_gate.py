"""Fail-closed runtime and freeze gates for the sole authorized M4 run."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import zlib
from pathlib import Path
from typing import Any, Mapping

from experiments.phase4_complexity_v1.candidate_registry import (
    candidate_by_id,
    load_candidate_registry,
    load_complexity_protocol,
)
from experiments.phase4_complexity_v1.freeze_verification import (
    verify_freeze_manifest,
)
from experiments.phase4_formal_v1 import (
    FORMAL_BRANCH,
    FORMAL_CANDIDATE_ID,
    FORMAL_CONFIG_ID,
    FORMAL_GPU_UUID,
    FORMAL_ZLIB_VERSION,
    SCHEMA_VERSION,
)
from experiments.phase4_m4_v1.m4_configs import (
    REPO_ROOT,
    load_frozen_config,
    reject_runtime_overrides,
    sha256_file,
)
from experiments.phase4_m4_v1.train_m4 import (
    ARTIFACT_ROOT_ENV,
    _stage2_protocol,
)


MINIMUM_FREE_GPU_MIB = 40_000
TRAIN_RELATIVE_PATH = (
    "dataset/stage2_confirm_v2_seed2028/train.parquet"
)
CONTROL_RELATIVE_ROOT = "experiments/runs/phase4_formal_v1_control"
SMOKE_RELATIVE_ROOT = "experiments/runs/phase4_formal_v1_smoke"
SCORER_PYTHON = Path(
    "/home/lizhaohui/lzq/phase3_runtime/phase3_v5/env/bin/python"
)


def atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def current_git_state() -> dict[str, Any]:
    head = _git("rev-parse", "HEAD")
    branch = _git("branch", "--show-current")
    status = _git("status", "--porcelain=v1", "--untracked-files=all")
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    upstream_head = _git("rev-parse", "@{u}")
    if branch != FORMAL_BRANCH:
        raise RuntimeError(f"formal branch differs: {branch}")
    if status:
        raise RuntimeError("formal source worktree or index is not clean")
    if upstream != f"origin/{FORMAL_BRANCH}" or upstream_head != head:
        raise RuntimeError("formal commit has not been pushed to its frozen branch")
    return {
        "status": "passed",
        "branch": branch,
        "commit_sha": head,
        "upstream": upstream,
        "upstream_commit_sha": upstream_head,
        "worktree_clean": True,
        "index_clean": True,
        "upstream_synced": True,
    }


def artifact_root() -> Path:
    supplied = os.environ.get(ARTIFACT_ROOT_ENV, "").strip()
    if not supplied:
        raise RuntimeError(
            f"{ARTIFACT_ROOT_ENV} must identify the immutable artifact root"
        )
    root = Path(supplied).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    return root


def formal_paths(root: Path, config: Mapping[str, Any]) -> dict[str, Path]:
    return {
        "run_root": root / str(config["output_relative_path"]),
        "control_root": root / CONTROL_RELATIVE_ROOT / FORMAL_CONFIG_ID,
        "smoke_root": root / SMOKE_RELATIVE_ROOT / FORMAL_CONFIG_ID,
    }


def verify_protocol_freeze() -> dict[str, Any]:
    protocol, protocol_receipt = load_complexity_protocol()
    registry, registry_receipt = load_candidate_registry()
    freeze = verify_freeze_manifest()
    candidate = registry[FORMAL_CANDIDATE_ID]
    if (
        candidate.candidate_name != FORMAL_CONFIG_ID
        or candidate.method != "M4"
        or candidate.mapping_root != 43101
    ):
        raise RuntimeError("candidate ID 9 no longer identifies the formal M4 run")
    return {
        "status": "passed",
        "protocol_id": protocol["protocol_id"],
        "complexity_protocol_sha256": protocol_receipt["sha256"],
        "candidate_manifest_sha256": registry_receipt["manifest_sha256"],
        "freeze_manifest_sha256": freeze["freeze_manifest_sha256"],
        "frozen_file_count": freeze["frozen_file_count"],
        "candidate_id": candidate.candidate_id,
        "candidate_name": candidate.candidate_name,
    }


def verify_zlib_runtime() -> dict[str, Any]:
    if (
        zlib.ZLIB_VERSION != FORMAL_ZLIB_VERSION
        or zlib.ZLIB_RUNTIME_VERSION != FORMAL_ZLIB_VERSION
    ):
        raise RuntimeError(
            "formal conditional codec requires zlib compile/runtime 1.3.1"
        )
    return {
        "status": "passed",
        "compile_version": zlib.ZLIB_VERSION,
        "runtime_version": zlib.ZLIB_RUNTIME_VERSION,
    }


def _nvidia_rows(query: str) -> list[list[str]]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            f"--query-{query}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [
        [field.strip() for field in line.split(",")]
        for line in completed.stdout.splitlines()
        if line.strip()
    ]


def verify_gpu() -> dict[str, Any]:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if visible != FORMAL_GPU_UUID:
        raise RuntimeError(
            "formal run requires CUDA_VISIBLE_DEVICES to be the frozen A40 UUID"
        )
    matches = [
        row
        for row in _nvidia_rows("gpu=uuid,name,memory.total,memory.free")
        if row[0] == FORMAL_GPU_UUID
    ]
    if len(matches) != 1:
        raise RuntimeError("formal GPU UUID is absent or duplicated")
    uuid, name, total_mib, free_mib = matches[0]
    if name != "NVIDIA A40" or int(free_mib) < MINIMUM_FREE_GPU_MIB:
        raise RuntimeError("formal A40 type or free-memory gate failed")

    import torch

    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("formal run requires exactly one visible CUDA device")
    properties = torch.cuda.get_device_properties(0)
    if properties.name != name or (properties.major, properties.minor) != (8, 6):
        raise RuntimeError("PyTorch visible GPU identity differs from nvidia-smi")
    return {
        "status": "passed",
        "cuda_visible_devices": visible,
        "gpu_uuid": uuid,
        "gpu_name": name,
        "compute_capability": [properties.major, properties.minor],
        "total_memory_mib": int(total_mib),
        "free_memory_mib_at_gate": int(free_mib),
        "single_visible_gpu": True,
    }


def verify_assets_and_data(
    config: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    protocol = _stage2_protocol(config)
    protocol.verify_immutable_inputs()
    data_path = root / TRAIN_RELATIVE_PATH
    expected_sha = protocol.payload["data"]["reused_confirmation"][
        "train_sha256"
    ]
    if not data_path.is_file() or sha256_file(data_path) != expected_sha:
        raise RuntimeError("formal M4 training data is absent or changed")
    return {
        "status": "passed",
        "stage2_protocol": protocol.reference(),
        "training_data_path": str(data_path),
        "training_data_sha256": expected_sha,
        "base_asset_verification": "passed",
    }


def verify_formal_config() -> tuple[dict[str, Any], dict[str, Any]]:
    reject_runtime_overrides(None)
    config, receipt = load_frozen_config(FORMAL_CONFIG_ID)
    candidate = candidate_by_id(FORMAL_CANDIDATE_ID)
    expected_dimensions = {
        "shared_coordinates": candidate.block_dimensions["shared"],
        "vision_private_coordinates": candidate.block_dimensions[
            "vision_private"
        ],
        "projector_private_coordinates": candidate.block_dimensions[
            "projector_private"
        ],
        "language_private_coordinates": candidate.block_dimensions[
            "language_private"
        ],
    }
    if (
        config["config_id"] != FORMAL_CONFIG_ID
        or config["mapping_root"] != 43101
        or config["shared_budget"] != 2048
        or config["coordinate_dimensions"] != expected_dimensions
        or candidate.source_config_sha256 != receipt["sha256"]
        or config["runtime_overrides"] != "forbidden"
    ):
        raise RuntimeError("formal M4 config differs from candidate ID 9")
    return config, {
        "status": "passed",
        "candidate_id": FORMAL_CANDIDATE_ID,
        "config_id": FORMAL_CONFIG_ID,
        "config_sha256": receipt["sha256"],
        "config_manifest_sha256": receipt["manifest_sha256"],
        "mapping_root": config["mapping_root"],
        "coordinate_dimensions": config["coordinate_dimensions"],
        "runtime_overrides": "forbidden",
    }


def run_preflight(
    *,
    expected_commit_sha: str | None = None,
    require_output_absent: bool = True,
    require_control_absent: bool = False,
    require_smoke_absent: bool = False,
    require_gpu: bool = True,
) -> dict[str, Any]:
    started = time.time()
    git = current_git_state()
    if expected_commit_sha is not None and git["commit_sha"] != expected_commit_sha:
        raise RuntimeError("current commit differs from bound formal commit")
    freeze = verify_protocol_freeze()
    zlib_receipt = verify_zlib_runtime()
    config, config_receipt = verify_formal_config()
    root = artifact_root()
    paths = formal_paths(root, config)
    if require_output_absent and paths["run_root"].exists():
        raise FileExistsError(
            f"formal output directory already exists: {paths['run_root']}"
        )
    if require_control_absent and paths["control_root"].exists():
        raise FileExistsError(
            f"formal control directory already exists: {paths['control_root']}"
        )
    if require_smoke_absent and paths["smoke_root"].exists():
        raise FileExistsError(
            f"formal smoke directory already exists: {paths['smoke_root']}"
        )
    assets = verify_assets_and_data(config, root)
    gpu = verify_gpu() if require_gpu else {"status": "not_requested"}
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "config_id": FORMAL_CONFIG_ID,
        "candidate_id": FORMAL_CANDIDATE_ID,
        "git": git,
        "freeze": freeze,
        "zlib": zlib_receipt,
        "config": config_receipt,
        "assets_and_data": assets,
        "gpu": gpu,
        "artifact_root": str(root),
        "formal_output_absent": not paths["run_root"].exists(),
        "control_output_absent": not paths["control_root"].exists(),
        "smoke_output_absent": not paths["smoke_root"].exists(),
        "seconds": time.time() - started,
    }


def assert_runtime_binding(
    binding: Mapping[str, Any], *, require_zlib_1_3_1: bool = True
) -> dict[str, Any]:
    required = {
        "git_commit_sha": str(binding.get("git_commit_sha", "")),
        "freeze_manifest_sha256": str(
            binding.get("freeze_manifest_sha256", "")
        ),
    }
    if (
        len(required["git_commit_sha"]) != 40
        or len(required["freeze_manifest_sha256"]) != 64
    ):
        raise ValueError("formal binding lacks a Git commit SHA")
    git = current_git_state()
    freeze = verify_protocol_freeze()
    zlib_receipt = (
        verify_zlib_runtime()
        if require_zlib_1_3_1
        else {
            "status": "not_required_in_frozen_scoring_process",
            "runtime_version": zlib.ZLIB_RUNTIME_VERSION,
        }
    )
    if git["commit_sha"] != required["git_commit_sha"]:
        raise RuntimeError("formal pipeline commit changed after start")
    if (
        freeze["freeze_manifest_sha256"]
        != required["freeze_manifest_sha256"]
    ):
        raise RuntimeError("formal freeze manifest changed after start")
    return {
        "status": "passed",
        "git_commit_sha": git["commit_sha"],
        "freeze_manifest_sha256": freeze["freeze_manifest_sha256"],
        "zlib_runtime_version": zlib_receipt["runtime_version"],
        "formal_codec_zlib_gate_required": require_zlib_1_3_1,
    }


def make_binding(preflight: Mapping[str, Any]) -> dict[str, str]:
    if preflight.get("status") != "passed":
        raise ValueError("cannot bind a failed preflight")
    return {
        "git_commit_sha": str(preflight["git"]["commit_sha"]),
        "freeze_manifest_sha256": str(
            preflight["freeze"]["freeze_manifest_sha256"]
        ),
    }


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
