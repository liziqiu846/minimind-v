#!/usr/bin/env python3
"""Select the protocol A40 and freeze/verify the Stage 2 software environment."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import zlib
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import write_json_atomic


def command_lines(command: list[str]) -> list[str]:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def gpu_inventory() -> tuple[list[dict], list[dict]]:
    rows = command_lines(
        [
            "nvidia-smi",
            "--query-gpu=index,name,uuid,memory.free,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    gpus = []
    for row in rows:
        index, name, uuid, free, total, driver = [value.strip() for value in row.split(",")]
        gpus.append(
            {
                "index": int(index),
                "name": name,
                "uuid": uuid,
                "memory_free_mib": int(free),
                "memory_total_mib": int(total),
                "driver_version": driver,
            }
        )
    try:
        process_rows = command_lines(
            [
                "nvidia-smi",
                "--query-compute-apps=gpu_uuid,pid,used_memory",
                "--format=csv,noheader,nounits",
            ]
        )
    except subprocess.CalledProcessError:
        process_rows = []
    processes = []
    for row in process_rows:
        uuid, pid, memory = [value.strip() for value in row.split(",")]
        processes.append({"gpu_uuid": uuid, "pid": int(pid), "used_memory_mib": int(memory)})
    return gpus, processes


def select_idle_a40(gpus: list[dict], processes: list[dict]) -> dict:
    active = {process["gpu_uuid"] for process in processes}
    candidates = [
        gpu for gpu in gpus if "A40" in gpu["name"] and gpu["uuid"] not in active
    ]
    if not candidates:
        raise RuntimeError("no idle A40 satisfies the Stage 2 selection rule")
    maximum_free = max(gpu["memory_free_mib"] for gpu in candidates)
    tied = [gpu for gpu in candidates if gpu["memory_free_mib"] == maximum_free]
    return min(tied, key=lambda gpu: gpu["uuid"])


def normalized_pip_freeze() -> str:
    lines = command_lines([sys.executable, "-m", "pip", "freeze", "--all"])
    return "\n".join(sorted(lines, key=lambda line: line.lower())) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pip-freeze-output", type=Path, required=True)
    parser.add_argument("--expect-uuid")
    parser.add_argument("--receipt-schema-version", type=int, choices=(1, 2), default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists() or args.pip_freeze_output.exists():
        raise FileExistsError("environment receipt output already exists")
    gpus, processes = gpu_inventory()
    selected = select_idle_a40(gpus, processes)
    if args.expect_uuid and selected["uuid"] != args.expect_uuid:
        raise RuntimeError(
            f"deterministic A40 selection changed: expected {args.expect_uuid}, got {selected['uuid']}"
        )
    freeze = normalized_pip_freeze()
    args.pip_freeze_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.pip_freeze_output.with_name(args.pip_freeze_output.name + ".tmp")
    temporary.write_text(freeze, encoding="utf-8")
    temporary.replace(args.pip_freeze_output)
    packages = {
        name: importlib.metadata.version(name)
        for name in ("torch", "transformers", "numpy", "Pillow", "ImageHash", "pyarrow")
    }
    payload = {
        "schema_version": args.receipt_schema_version,
        "selection_rule": [
            "name strictly contains A40",
            "exclude GPUs with active compute processes",
            "maximize free memory in MiB",
            "break exact free-memory ties by ascending GPU UUID",
        ],
        "selected_gpu": selected,
        "gpu_inventory": gpus,
        "active_compute_processes": processes,
        "runtime": {
            "python": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "packages": packages,
            "cuda_runtime": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "zlib_build": zlib.ZLIB_VERSION,
            "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
            "platform": platform.platform(),
        },
        "pip_freeze": {
            "path": str(args.pip_freeze_output.resolve()),
            "normalization": "pip freeze --all lines sorted case-insensitively, LF terminated",
            "sha256": hashlib.sha256(freeze.encode("utf-8")).hexdigest(),
        },
    }
    write_json_atomic(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
