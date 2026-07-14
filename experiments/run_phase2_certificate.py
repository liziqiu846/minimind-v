#!/usr/bin/env python3
"""Run the frozen Phase 2 dataset, training, compression, and certificate pipeline."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.phase2_protocol import FrozenProtocol


STAGE_ORDER = ("dataset", "train", "quantize", "evaluate", "bound", "bundle")


def repo_path(relative: str) -> Path:
    return REPO_ROOT / relative


def command_plan(
    protocol: FrozenProtocol, run_root: Path, bundle_dir: Path, device: str
) -> dict[str, list[tuple[str, ...]]]:
    payload = protocol.payload
    dataset = payload["dataset"]
    model = payload["model"]
    training = payload["training"]
    evaluation = payload["evaluation"]
    diagnostics = payload["diagnostics"]
    certificate = payload["certificate"]
    compression = payload["compression"]
    protocol_path = str(protocol.path)
    split_dir = run_root / "dataset"
    run_dir = run_root / "run"
    compression_dir = run_dir / "compression"
    risks_dir = run_dir / "risks"
    run_id = payload["run_id"]
    python = sys.executable

    dataset_command = [
        python,
        str(repo_path("experiments/build_bound_dataset.py")),
        "--input", str(repo_path(dataset["source_path"])),
        "--output-dir", str(split_dir),
        "--train-size", str(dataset["train_size"]),
        "--validation-size", str(dataset["validation_size"]),
        "--seed", str(dataset["seed"]),
        "--protocol-path", protocol_path,
    ]
    for exclusion in dataset["exclude_paths"]:
        dataset_command.extend(("--exclude-parquet", str(repo_path(exclusion))))

    train_command = (
        python,
        str(repo_path("trainer/train_pretrain_vlm.py")),
        "--data_path", str(split_dir / "train.parquet"),
        "--protocol_path", protocol_path,
        "--split_manifest", str(split_dir / "split_manifest.json"),
        "--from_weight", model["initial_weight_name"],
        "--init_weight_dir", str(repo_path("out")),
        "--tokenizer_path", str(repo_path("model")),
        "--vision_model_path", str(repo_path("model/siglip2-base-p32-256-ve")),
        "--save_dir", str(run_dir / "weights"),
        "--checkpoint_dir", str(run_dir / "checkpoints"),
        "--manifest_path", str(run_dir / "manifest.json"),
        "--save_weight", run_id,
        "--expected_trainable_parameters", str(model["subspace_dim"]),
        "--freeze_llm", str(model["freeze_llm"]),
        "--projector_type", model["projector_type"],
        "--subspace_dim", str(model["subspace_dim"]),
        "--subspace_seed", str(model["subspace_seed"]),
        "--subspace_train_norm", str(int(model["train_norm"])),
        "--augment", str(int(training["augment"])),
        "--seed", str(training["seed"]),
        "--epochs", str(training["epochs"]),
        "--batch_size", str(training["batch_size"]),
        "--accumulation_steps", str(training["accumulation_steps"]),
        "--learning_rate", str(training["learning_rate"]),
        "--hidden_size", str(model["hidden_size"]),
        "--num_hidden_layers", str(model["num_hidden_layers"]),
        "--use_moe", str(int(model["use_moe"])),
        "--max_seq_len", str(training["max_seq_len"]),
        "--num_workers", str(training["num_workers"]),
        "--dtype", training["dtype"],
        "--device", device,
        "--from_resume", "0",
        "--grad_clip", str(training["grad_clip"]),
        "--use_compile", str(int(training["compile"])),
    )
    archive = compression_dir / "model.mms"
    decoded = compression_dir / "decoded.pth"
    encoding = compression_dir / "encoding.json"
    quantize_command = [
        python,
        str(repo_path("experiments/quantize_subspace.py")),
        "--run-dir", str(run_dir),
        "--bits", str(compression["quantization_bits"]),
        "--archive", str(archive),
        "--decoded-checkpoint", str(decoded),
        "--summary", str(encoding),
        "--protocol-path", protocol_path,
    ]
    if compression["codec"] == "zlib":
        quantize_command.append("--entropy-code")

    def evaluation_command(role, condition, alphas, output):
        return (
            python,
            str(repo_path("experiments/evaluate_smoothed_risk.py")),
            "--data-path", str(split_dir / f"{role}.parquet"),
            "--data-role", role,
            "--split-manifest", str(split_dir / "split_manifest.json"),
            "--protocol-path", protocol_path,
            "--run-dir", str(run_dir),
            "--checkpoint", str(decoded),
            "--output", str(output),
            "--model-kind", "decoded_quantized",
            "--image-condition", condition,
            "--paired-shuffle-seed", str(diagnostics["paired_shuffle_seed"]),
            "--batch-size", str(evaluation["batch_size"]),
            "--num-workers", str(evaluation["num_workers"]),
            "--max-samples", str(evaluation["max_samples"]),
            "--dtype", evaluation["dtype"],
            "--device", device,
            "--alphas", *(str(alpha) for alpha in alphas),
        )

    train_risk = risks_dir / "train_correct.json"
    validation_correct = risks_dir / "validation_correct.json"
    validation_paired = risks_dir / "validation_paired_shuffled.json"
    validation_none = risks_dir / "validation_none.json"
    evaluation_commands = [
        evaluation_command("train", "correct", [certificate["alpha"]], train_risk),
        evaluation_command(
            "validation", "correct", diagnostics["alpha_grid"], validation_correct
        ),
        evaluation_command(
            "validation", "paired_shuffled", diagnostics["alpha_grid"], validation_paired
        ),
        evaluation_command(
            "validation", "none", diagnostics["alpha_grid"], validation_none
        ),
    ]
    bound = run_dir / "bound.json"
    bound_command = (
        python,
        str(repo_path("experiments/compute_bound_report.py")),
        "--encoding", str(encoding),
        "--training-risk", str(train_risk),
        "--validation-risk", str(validation_correct),
        "--run-manifest", str(run_dir / "manifest.json"),
        "--protocol-path", protocol_path,
        "--confidence-delta", str(certificate["confidence_delta"]),
        "--output", str(bound),
    )
    bundle_artifacts = (
        ("protocol", protocol.path),
        ("decoder_registry", repo_path(payload["decoder_registry"]["path"])),
        ("environment", repo_path(payload["environment_path"])),
        ("dataset_receipt", split_dir / "split_manifest.json"),
        ("train_membership", split_dir / "train_membership.jsonl.gz"),
        ("validation_membership", split_dir / "validation_membership.jsonl.gz"),
        ("run_manifest", run_dir / "manifest.json"),
        ("compressed_model", archive),
        ("encoding", encoding),
        ("train_risk", train_risk),
        ("validation_correct", validation_correct),
        ("validation_paired_shuffled", validation_paired),
        ("validation_none", validation_none),
        ("bound", bound),
    )
    bundle_command = (
        python,
        str(repo_path("experiments/build_public_bundle.py")),
        "--output-dir", str(bundle_dir),
        *(f"{role}={path}" for role, path in bundle_artifacts),
    )
    verify_bundle_command = (
        python,
        str(repo_path("experiments/verify_public_bundle.py")),
        "--bundle-dir", str(bundle_dir),
    )
    return {
        "dataset": [tuple(dataset_command)],
        "train": [train_command],
        "quantize": [tuple(quantize_command)],
        "evaluate": evaluation_commands,
        "bound": [bound_command],
        "bundle": [bundle_command, verify_bundle_command],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol", type=Path, default=REPO_ROOT / "experiments/phase2_protocol.json"
    )
    parser.add_argument(
        "--run-root", type=Path, default=REPO_ROOT / "experiments/runs/phase2"
    )
    parser.add_argument(
        "--bundle-dir", type=Path, default=REPO_ROOT / "experiments/results/phase2_bundle"
    )
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--stages", nargs="+", choices=("all", *STAGE_ORDER), default=["all"])
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if "all" in args.stages and args.stages != ["all"]:
        raise ValueError("all cannot be combined with individual stages")
    if len(args.stages) != len(set(args.stages)):
        raise ValueError("stages cannot be repeated")
    protocol = FrozenProtocol.load(args.protocol)
    protocol.verify_environment(REPO_ROOT)
    plan = command_plan(protocol, args.run_root.resolve(), args.bundle_dir.resolve(), args.device)
    stages = STAGE_ORDER if args.stages == ["all"] else args.stages
    for stage in stages:
        for command in plan[stage]:
            print(f"[{stage}] {shlex.join(command)}", flush=True)
            if args.execute:
                subprocess.run(command, cwd=REPO_ROOT, check=True)


if __name__ == "__main__":
    main()
