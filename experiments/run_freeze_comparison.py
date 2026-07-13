#!/usr/bin/env python3
"""Define reproducible MiniMind-V A/B/C freeze-comparison runs."""

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FreezeSetting:
    label: str
    freeze_llm: int
    trainable_scope: str
    expected_trainable_parameters: int


SETTINGS = {
    "A": FreezeSetting(
        label="A",
        freeze_llm=2,
        trainable_scope="vision_proj",
        expected_trainable_parameters=1_182_720,
    ),
    "B": FreezeSetting(
        label="B",
        freeze_llm=1,
        trainable_scope="vision_proj + first/last LLM layers",
        expected_trainable_parameters=15_931_776,
    ),
    "C": FreezeSetting(
        label="C",
        freeze_llm=0,
        trainable_scope="all parameters except vision_encoder",
        expected_trainable_parameters=65_094_912,
    ),
}


@dataclass(frozen=True)
class RunSpec:
    setting: FreezeSetting
    seed: int
    run_id: str
    run_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-path", type=Path,
        default=REPO_ROOT / "dataset/bound_caption_10k_seed42/train.parquet",
    )
    parser.add_argument(
        "--run-root", type=Path,
        default=REPO_ROOT / "experiments/runs/freeze_comparison",
    )
    parser.add_argument("--settings", nargs="+", choices=SETTINGS, default=list(SETTINGS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--accumulation-steps", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=4e-4)
    parser.add_argument("--hidden-size", type=int, default=768)
    parser.add_argument("--num-hidden-layers", type=int, default=8)
    parser.add_argument("--max-seq-len", type=int, default=450)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--dtype", choices=("bfloat16", "float16"), default="bfloat16")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--from-weight", default="llm")
    parser.add_argument("--init-weight-dir", type=Path, default=REPO_ROOT / "out")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def build_run_specs(args: argparse.Namespace) -> tuple[RunSpec, ...]:
    if not args.data_path.is_file():
        raise FileNotFoundError(f"training data not found: {args.data_path}")
    positive = (
        args.epochs,
        args.batch_size,
        args.accumulation_steps,
        args.hidden_size,
        args.num_hidden_layers,
        args.max_seq_len,
        args.num_workers,
    )
    if any(value <= 0 for value in positive) or args.learning_rate <= 0:
        raise ValueError("epochs, batch sizes, sequence length, and learning rate must be positive")
    if len(args.settings) != len(set(args.settings)) or len(args.seeds) != len(set(args.seeds)):
        raise ValueError("settings and seeds must not contain duplicates")
    if (args.hidden_size, args.num_hidden_layers) != (768, 8):
        raise ValueError(
            "the registered A/B/C parameter counts require hidden-size 768 and 8 layers"
        )
    if args.from_weight != "none":
        initial_weight = args.init_weight_dir / f"{args.from_weight}_{args.hidden_size}.pth"
        if not initial_weight.is_file():
            raise FileNotFoundError(f"initial weight not found: {initial_weight}")

    specs = []
    for label in args.settings:
        setting = SETTINGS[label]
        for seed in args.seeds:
            run_id = f"{label.lower()}_freeze{setting.freeze_llm}_seed{seed}"
            specs.append(RunSpec(setting, seed, run_id, args.run_root / run_id))
    return tuple(specs)


def build_train_command(args: argparse.Namespace, spec: RunSpec) -> tuple[str, ...]:
    trainer = REPO_ROOT / "trainer/train_pretrain_vlm.py"
    weight_dir = spec.run_dir / "weights"
    return (
        sys.executable,
        str(trainer),
        "--data_path",
        str(args.data_path.resolve()),
        "--from_weight",
        args.from_weight,
        "--init_weight_dir",
        str(args.init_weight_dir.resolve()),
        "--save_dir",
        str(weight_dir),
        "--checkpoint_dir",
        str(spec.run_dir / "checkpoints"),
        "--manifest_path",
        str(spec.run_dir / "manifest.json"),
        "--save_weight",
        spec.run_id,
        "--expected_trainable_parameters",
        str(spec.setting.expected_trainable_parameters),
        "--freeze_llm",
        str(spec.setting.freeze_llm),
        "--augment",
        "0",
        "--seed",
        str(spec.seed),
        "--epochs",
        str(args.epochs),
        "--batch_size",
        str(args.batch_size),
        "--accumulation_steps",
        str(args.accumulation_steps),
        "--learning_rate",
        str(args.learning_rate),
        "--hidden_size",
        str(args.hidden_size),
        "--num_hidden_layers",
        str(args.num_hidden_layers),
        "--max_seq_len",
        str(args.max_seq_len),
        "--num_workers",
        str(args.num_workers),
        "--dtype",
        args.dtype,
        "--device",
        args.device,
        "--from_resume",
        "0",
    )


def write_status(spec: RunSpec, status: str, **details) -> None:
    payload = {
        "run_id": spec.run_id,
        "setting": spec.setting.label,
        "freeze_llm": spec.setting.freeze_llm,
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **details,
    }
    path = spec.run_dir / "status.json"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def execute_run(spec: RunSpec, command: tuple[str, ...]) -> None:
    if spec.run_dir.exists():
        if not spec.run_dir.is_dir() or any(spec.run_dir.iterdir()):
            raise FileExistsError(f"run directory is not empty: {spec.run_dir}")
    spec.run_dir.mkdir(parents=True, exist_ok=True)
    rendered = shlex.join(command)
    (spec.run_dir / "command.txt").write_text(rendered + "\n", encoding="utf-8")
    write_status(spec, "running")
    try:
        subprocess.run(command, cwd=REPO_ROOT / "trainer", check=True)
    except subprocess.CalledProcessError as error:
        write_status(spec, "failed", returncode=error.returncode)
        raise
    else:
        write_status(spec, "completed", returncode=0)


def main() -> None:
    args = parse_args()
    specs = build_run_specs(args)
    mode = "execute" if args.execute else "dry-run"
    print(f"Planned {len(specs)} controlled runs in {mode} mode; effective batch size "
          f"{args.batch_size * args.accumulation_steps}.")
    for spec in specs:
        command = build_train_command(args, spec)
        print(f"\n[{spec.run_id}] {spec.setting.trainable_scope}")
        print(shlex.join(command))
        if args.execute:
            execute_run(spec, command)


if __name__ == "__main__":
    main()
