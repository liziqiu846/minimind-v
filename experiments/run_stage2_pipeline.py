#!/usr/bin/env python3
"""Run the resumable Stage 2 development or formal pipeline in declared order."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import (
    DEFAULT_DRAFT,
    DEFAULT_FROZEN,
    Stage2Protocol,
    write_json_atomic,
)


@dataclass(frozen=True)
class RunSpec:
    group: str
    root: int | None
    train_seed: int
    learning_rate: float

    @property
    def name(self) -> str:
        root = "none" if self.root is None else str(self.root)
        lr = f"{self.learning_rate:.3f}".replace(".", "p")
        return f"{self.group}_root-{root}_seed-{self.train_seed}_lr-{lr}"


def development_specs(protocol: Stage2Protocol) -> list[RunSpec]:
    lrs = protocol.payload["development"]["learning_rates"]
    pairs = protocol.payload["development"]["mapping_root_seed_pairs"]
    specs = []
    for group in ("M0", "M1", "M2", "M3"):
        for lr in lrs:
            for pair in pairs:
                specs.append(
                    RunSpec(
                        group=group,
                        root=None if group == "M1" else pair["mapping_root"],
                        train_seed=pair["train_seed"],
                        learning_rate=lr,
                    )
                )
    if len(specs) != 36:
        raise RuntimeError("development plan must contain exactly 36 runs")
    return specs


def formal_specs(protocol: Stage2Protocol) -> list[RunSpec]:
    protocol.require_frozen()
    selected = protocol.payload["development"]["selected_learning_rates"]
    seed = protocol.payload["training"]["formal_seed"]
    specs = []
    for group, root in (
        ("M0", 43101), ("M0", 43102), ("M0", 43103),
        ("M1", None),
        ("M2", 43101), ("M2", 43102), ("M2", 43103),
        ("M3", 43101), ("M3", 43102), ("M3", 43103),
    ):
        key = "M2_M3" if group in ("M2", "M3") else group
        specs.append(RunSpec(group, root, seed, selected[key]))
    return specs


def command_base(script: str) -> list[str]:
    return [sys.executable, str(REPO_ROOT / script)]


def add_root(command: list[str], root: int | None) -> list[str]:
    if root is not None:
        command.extend(("--mapping-root", str(root)))
    return command


def run_commands(
    spec: RunSpec,
    run_dir: Path,
    protocol: Stage2Protocol,
    phase: str,
    data: Path,
    device: str,
) -> list[tuple[str, list[str], Path]]:
    formal_flag = ["--formal"] if phase == "formal" else []
    protocol_args = ["--protocol", str(protocol.path)]
    common_model = ["--model-group", spec.group]
    train_dir = run_dir / "train"
    encode_dir = run_dir / "encode"
    decode_dir = run_dir / "decode"
    archive = encode_dir / "adapter.mms2"
    coordinates = train_dir / "coordinates.pt"
    decoded = decode_dir / "decoded_coordinates.pt"
    commands: list[tuple[str, list[str], Path]] = []

    train = command_base("trainer/train_stage2.py") + protocol_args + common_model
    add_root(train, spec.root)
    train += [
        "--data", str(data), "--output-dir", str(train_dir),
        "--learning-rate", str(spec.learning_rate), "--train-seed", str(spec.train_seed),
        "--device", device,
    ] + formal_flag
    commands.append(("train", train, train_dir / "training_manifest.json"))

    if phase == "formal":
        unquantized = command_base("experiments/evaluate_stage2_risk.py") + protocol_args + common_model
        add_root(unquantized, spec.root)
        unquantized += [
            "--coordinates", str(coordinates), "--data", str(data), "--data-role", "train",
            "--model-kind", "unquantized", "--image-condition", "correct",
            "--output", str(run_dir / "risk_unquantized_train.json"), "--device", device,
        ] + formal_flag
        commands.append(("risk_unquantized_train", unquantized, run_dir / "risk_unquantized_train.json"))

    encode = command_base("experiments/quantize_stage2_adapter.py") + [
        "--mode", "encode", "--model-group", spec.group,
        "--coordinates", str(coordinates), "--archive", str(archive),
        "--output-dir", str(encode_dir), "--protocol", str(protocol.path),
    ]
    add_root(encode, spec.root)
    commands.append(("encode", encode, encode_dir / "adapter_summary.json"))

    decode = command_base("experiments/quantize_stage2_adapter.py") + [
        "--mode", "decode", "--model-group", spec.group,
        "--archive", str(archive), "--output-dir", str(decode_dir),
        "--protocol", str(protocol.path),
    ]
    add_root(decode, spec.root)
    commands.append(("clean_decode", decode, decode_dir / "adapter_summary.json"))

    decoded_train = command_base("experiments/evaluate_stage2_risk.py") + protocol_args + common_model
    add_root(decoded_train, spec.root)
    decoded_train += [
        "--coordinates", str(decoded), "--adapter", str(archive),
        "--data", str(data), "--data-role", "train", "--model-kind", "decoded_quantized",
        "--image-condition", "correct", "--output", str(run_dir / "risk_decoded_train.json"),
        "--device", device,
    ] + formal_flag
    commands.append(("risk_decoded_train", decoded_train, run_dir / "risk_decoded_train.json"))

    if phase == "formal":
        validation_data = Path(protocol.payload["data"]["output_directory"]) / "validation.parquet"
        if not validation_data.is_absolute():
            validation_data = REPO_ROOT / validation_data
        for condition in (("correct",) if spec.group == "M0" else ("correct", "paired_shuffled", "none")):
            output = run_dir / f"risk_decoded_validation_{condition}.json"
            evaluate = command_base("experiments/evaluate_stage2_risk.py") + protocol_args + common_model
            add_root(evaluate, spec.root)
            evaluate += [
                "--coordinates", str(decoded), "--adapter", str(archive),
                "--data", str(validation_data), "--data-role", "validation",
                "--model-kind", "decoded_quantized", "--image-condition", condition,
                "--output", str(output), "--device", device,
            ] + formal_flag
            commands.append((f"risk_validation_{condition}", evaluate, output))

    bound = command_base("experiments/compute_stage2_bound.py") + protocol_args + [
        "--adapter-summary", str(decode_dir / "adapter_summary.json"),
        "--decoded-model-hash", str(decode_dir / "decoded_model_hash.json"),
        "--decoded-training-risk", str(run_dir / "risk_decoded_train.json"),
        "--output", str(run_dir / "bound.json"),
    ]
    if phase == "formal":
        bound += [
            "--decoded-validation-risk", str(run_dir / "risk_decoded_validation_correct.json"),
            "--unquantized-training-risk", str(run_dir / "risk_unquantized_train.json"),
            "--formal",
        ]
    commands.append(("bound", bound, run_dir / "bound.json"))
    return commands


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("development", "formal"), required=True)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol_path = args.protocol or (DEFAULT_FROZEN if args.phase == "formal" else DEFAULT_DRAFT)
    protocol = Stage2Protocol.load(protocol_path, require_frozen=args.phase == "formal")
    protocol.verify_immutable_inputs()
    if args.phase == "formal" and protocol.payload.get("schema_version") == 2:
        if protocol.payload.get("hardware_execution"):
            os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_uuid
        protocol.verify_runtime_integrity()
    if args.phase == "development":
        data = protocol.asset_path("development_train")
        specs = development_specs(protocol)
    else:
        if protocol.payload.get("schema_version") == 2:
            hardware = protocol.payload.get("hardware_execution")
            eligible = (
                hardware["eligible_gpu_uuids"]
                if hardware
                else [protocol.payload["environment"]["selected_gpu_uuid"]]
            )
            if args.gpu_uuid not in eligible:
                raise ValueError("formal GPU UUID is outside the frozen v2 execution policy")
        data = Path(protocol.payload["data"]["output_directory"]) / "train.parquet"
        if not data.is_absolute():
            data = REPO_ROOT / data
        protocol.verify_confirmation_data(data, "train")
        protocol.verify_confirmation_data(
            protocol.confirmation_directory() / "validation.parquet", "validation"
        )
        specs = formal_specs(protocol)
    plan = []
    for ordinal, spec in enumerate(specs):
        run_dir = args.run_root / f"{ordinal + 1:02d}_{spec.name}"
        commands = run_commands(spec, run_dir, protocol, args.phase, data, args.device)
        plan.append(
            {
                "ordinal": ordinal + 1,
                "run": spec.name,
                "directory": str(run_dir),
                "stages": [
                    {"name": name, "command": command, "completion": str(completion)}
                    for name, command, completion in commands
                ],
            }
        )
    args.run_root.mkdir(parents=True, exist_ok=True)
    plan_path = args.run_root / "pipeline_plan.json"
    if plan_path.exists():
        previous = json.loads(plan_path.read_text(encoding="utf-8"))
        if previous["protocol"] != protocol.reference() or previous["runs"] != plan:
            raise ValueError("existing pipeline plan differs from current immutable plan")
    else:
        write_json_atomic(
            plan_path,
            {
                "schema_version": 1,
                "phase": args.phase,
                "protocol": protocol.reference(),
                "gpu_uuid": args.gpu_uuid,
                "runs": plan,
            },
        )
    if not args.execute:
        for run in plan:
            print(f"[{run['ordinal']:02d}] {run['run']}")
            for stage in run["stages"]:
                print(f"  {stage['name']}: {shlex.join(stage['command'])}")
        return

    environment = dict(os.environ)
    environment["CUDA_VISIBLE_DEVICES"] = args.gpu_uuid
    progress_path = args.run_root / "pipeline_progress.json"
    started = time.time()
    for ordinal, spec in enumerate(specs):
        run_dir = args.run_root / f"{ordinal + 1:02d}_{spec.name}"
        run_dir.mkdir(parents=True, exist_ok=True)
        for stage_name, command, completion in run_commands(
            spec, run_dir, protocol, args.phase, data, args.device
        ):
            if completion.exists():
                print(f"skip complete {ordinal + 1:02d}/{len(specs)} {spec.name} {stage_name}", flush=True)
                continue
            log_path = run_dir / f"{stage_name}.log"
            if log_path.exists():
                raise RuntimeError(
                    f"partial stage requires audit before restart: {log_path}"
                )
            print(f"start {ordinal + 1:02d}/{len(specs)} {spec.name} {stage_name}", flush=True)
            with log_path.open("w", encoding="utf-8") as log:
                log.write(shlex.join(command) + "\n")
                log.flush()
                result = subprocess.run(
                    command,
                    cwd=REPO_ROOT,
                    env=environment,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            if result.returncode:
                write_json_atomic(
                    args.run_root / "pipeline_failure.json",
                    {
                        "status": "failed",
                        "phase": args.phase,
                        "run_ordinal": ordinal + 1,
                        "run": spec.name,
                        "stage": stage_name,
                        "returncode": result.returncode,
                        "log": str(log_path),
                        "elapsed_seconds": time.time() - started,
                    },
                )
                raise subprocess.CalledProcessError(result.returncode, command)
            if not completion.exists():
                raise RuntimeError(f"stage exited successfully without completion artifact: {completion}")
            write_json_atomic(
                progress_path,
                {
                    "status": "running",
                    "phase": args.phase,
                    "completed_run_ordinal": ordinal + (1 if stage_name == "bound" else 0),
                    "current_run": spec.name,
                    "completed_stage": stage_name,
                    "completion": str(completion),
                    "elapsed_seconds": time.time() - started,
                },
            )
    write_json_atomic(
        progress_path,
        {
            "status": "complete",
            "phase": args.phase,
            "completed_runs": len(specs),
            "protocol": protocol.reference(),
            "elapsed_seconds": time.time() - started,
        },
    )
    print(f"{args.phase} pipeline complete: {len(specs)} runs", flush=True)


if __name__ == "__main__":
    main()
