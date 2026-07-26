#!/usr/bin/env python3
"""Create an immutable formal-training run manifest before dispatch."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import torch

from .artifacts import bindings, write_json_exclusive
from .common import REPO_ROOT, sha256_file
from .configs import generate_matrix
from .protocol_tools import PROTOCOL_PATH, validate_frozen_protocol


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def _gpu_inventory() -> list[str]:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,name,uuid,memory.total",
         "--format=csv,noheader,nounits"],
        check=True, text=True, stdout=subprocess.PIPE,
    )
    return result.stdout.splitlines()


def create_manifest(path: Path, artifact_root: Path, output_root: Path,
                    devices: list[str]) -> dict:
    validate_frozen_protocol()
    if _git("status", "--porcelain"):
        raise RuntimeError("formal run manifest requires a clean worktree")
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    data = artifact_root.resolve() / protocol["fairness"]["training_data"]["relative_path"]
    checkpoint = Path("/home/lizhaohui/lzq/stage2-assets-v1") / \
        protocol["fairness"]["base_checkpoint"]["path"]
    if sha256_file(data) != protocol["fairness"]["training_data"]["sha256"]:
        raise ValueError("training data hash mismatch")
    if sha256_file(checkpoint) != protocol["fairness"]["base_checkpoint"]["sha256"]:
        raise ValueError("base checkpoint hash mismatch")
    candidates = generate_matrix()
    commands = [
        [
            sys.executable, "-m",
            "experiments.phase3_private_vs_shared_v1.train_one",
            "--config-id", config["config_id"],
            "--artifact-root", str(artifact_root.resolve()),
            "--output-root", str(output_root.resolve()),
            "--device", "cuda:0",
        ]
        for config in candidates
    ]
    payload = {
        **bindings(),
        "schema_version": 1,
        "status": "frozen_before_dispatch",
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("branch", "--show-current"),
        "protocol_path": str(PROTOCOL_PATH),
        "training_manifest_path": str(
            artifact_root.resolve()
            / "dataset/stage2_confirm_v2_seed2028/split_manifest.json"
        ),
        "training_manifest_sha256": sha256_file(
            artifact_root.resolve()
            / "dataset/stage2_confirm_v2_seed2028/split_manifest.json"
        ),
        "training_data_sha256": sha256_file(data),
        "base_checkpoint_sha256": sha256_file(checkpoint),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "gpu_inventory": _gpu_inventory(),
        "selected_device_indices": devices,
        "output_root": str(output_root.resolve()),
        "artifact_root": str(artifact_root.resolve()),
        "started_unix": time.time(),
        "candidate_count": len(candidates),
        "commands": commands,
    }
    write_json_exclusive(path.resolve(), payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--devices", required=True)
    args = parser.parse_args()
    result = create_manifest(
        args.manifest, args.artifact_root, args.output_root,
        [item for item in args.devices.split(",") if item],
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
