#!/usr/bin/env python3
"""Train exactly one candidate selected from the frozen P/S matrix."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.stage2_model import tensor_state_sha256
from experiments.stage2_protocol import Stage2Protocol
from trainer.train_stage2 import (
    frozen_parameter_hash,
    learning_rate_at,
    move_pixels,
    permutation_for_epoch,
    permutation_sha256,
    seed_everything,
)

from .adapter_runtime import build_candidate_model
from .artifacts import bindings, validate_bindings, write_json_atomic
from .codec import encode_coordinates
from .common import REPO_ROOT, sha256_file
from .configs import load_candidate
from .protocol_tools import PROTOCOL_PATH, validate_frozen_protocol
from .smoke import run as run_synthetic_smoke

STAGE2_PROTOCOL = REPO_ROOT / "experiments/stage2_protocol_v2.json"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def _save_torch_atomic(path: Path, payload) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def _formal_preflight() -> dict:
    validate_frozen_protocol()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol["execution_limit"]["formal_training_allowed"] is not True:
        raise RuntimeError("current protocol does not allow formal training")
    if _git("status", "--porcelain"):
        raise RuntimeError("formal training requires a clean worktree")
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("branch", "--show-current"),
        **bindings(),
    }


def train_candidate(
    config_id: str,
    artifact_root: Path,
    output_root: Path,
    device_name: str,
    *,
    config_override: Mapping[str, Any] | None = None,
    binding_override: Mapping[str, Any] | None = None,
    binding_validator: Callable[[dict[str, Any]], None] = validate_bindings,
    model_builder: Callable[..., torch.nn.Module] = build_candidate_model,
) -> dict:
    """Run the frozen loop, optionally with a protocol-bound external config."""
    if (config_override is None) != (binding_override is None):
        raise ValueError(
            "config_override and binding_override must be supplied together"
        )
    config = (
        load_candidate(config_id) if config_override is None else dict(config_override)
    )
    if config.get("config_id") != config_id:
        raise ValueError("training config identity differs from config_id")
    binding = (
        _formal_preflight() if binding_override is None else dict(binding_override)
    )
    output = output_root.resolve() / config_id
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "status.json"
    complete_path = output / "training_manifest.json"
    if complete_path.exists():
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
        binding_validator(complete)
        if complete.get("status") != "complete":
            raise ValueError("existing terminal manifest is not complete")
        return complete

    started = time.time()
    write_json_atomic(
        status_path,
        {
            **binding,
            "config_id": config_id,
            "status": "running",
            "started_unix": started,
            "resume_supported": True,
        },
    )
    try:
        stage2 = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
        protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        fairness = protocol["fairness"]
        data_path = artifact_root.resolve() / fairness["training_data"]["relative_path"]
        if sha256_file(data_path) != fairness["training_data"]["sha256"]:
            raise ValueError("training data SHA-256 mismatch")
        checkpoint = stage2.asset_path("initial_llm")
        if sha256_file(checkpoint) != fairness["base_checkpoint"]["sha256"]:
            raise ValueError("base checkpoint SHA-256 mismatch")
        device = torch.device(device_name)
        if device.type != "cuda" or not torch.cuda.is_available():
            raise RuntimeError("formal training requires CUDA")

        seed_everything(int(fairness["training_data"]["train_seed"]))
        model = model_builder(config, stage2, device=device)
        legacy_group = "M2" if config["structure"] == "P" else "M3"
        tokenizer = AutoTokenizer.from_pretrained(
            stage2.asset_path("tokenizer"), local_files_only=True
        )
        dataset = Stage2CaptionDataset(
            data_path,
            tokenizer,
            model_group=legacy_group,
            processor=model.processor,
            max_length=stage2.payload["training"]["max_sequence_length"],
            image_token_count=stage2.payload["model"]["image_token_count"],
        )
        expected_examples = int(stage2.payload["data"]["train_draws"])
        if len(dataset) != expected_examples:
            raise ValueError("training example count differs from frozen protocol")
        micro_batch = int(fairness["micro_batch_size"])
        accumulation = int(fairness["gradient_accumulation_steps"])
        epochs = int(fairness["epochs"])
        total_steps = int(fairness["total_steps"])
        if epochs * (len(dataset) // micro_batch) // accumulation != total_steps:
            raise ValueError("frozen schedule does not match training data")

        store = model.stage2_coordinates
        parameters = list(store.parameters())
        optimizer_spec = fairness["optimizer"]
        optimizer = torch.optim.AdamW(
            parameters,
            lr=float(fairness["learning_rate"]),
            betas=tuple(optimizer_spec["betas"]),
            eps=float(optimizer_spec["eps"]),
            weight_decay=float(optimizer_spec["weight_decay"]),
            amsgrad=bool(optimizer_spec["amsgrad"]),
        )
        initial_frozen = frozen_parameter_hash(model)
        recovery_path = output / "recovery.pt"
        start_epoch = optimizer_step = observed_batches = 0
        total_loss = 0.0
        epoch_receipts = []
        if recovery_path.exists():
            recovery = torch.load(recovery_path, map_location="cpu", weights_only=False)
            binding_validator(recovery)
            if recovery["config_id"] != config_id:
                raise ValueError("recovery config identity mismatch")
            store.load_state_dict(recovery["coordinates"])
            optimizer.load_state_dict(recovery["optimizer"])
            start_epoch = int(recovery["next_epoch"])
            optimizer_step = int(recovery["optimizer_step"])
            observed_batches = int(recovery["observed_micro_batches"])
            total_loss = float(recovery["total_loss"])
            epoch_receipts = list(recovery["epoch_receipts"])

        model.train()
        model.vision_encoder.eval()
        optimizer.zero_grad(set_to_none=True)
        training = stage2.payload["training"]
        for epoch in range(start_epoch, epochs):
            permutation = permutation_for_epoch(
                len(dataset), int(fairness["training_data"]["train_seed"]), epoch
            )
            workers = int(training["dataloader"]["num_workers"])
            loader = DataLoader(
                dataset,
                batch_size=micro_batch,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=workers,
                persistent_workers=workers > 0,
                pin_memory=True,
                prefetch_factor=training["dataloader"]["prefetch_factor"]
                if workers
                else None,
                collate_fn=stage2_collate,
            )
            epoch_loss = 0.0
            for micro_index, (input_ids, labels, pixels) in enumerate(loader):
                input_ids = input_ids.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                pixels = move_pixels(pixels, device)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    loss = model(
                        input_ids=input_ids, labels=labels, pixel_values=pixels
                    ).loss
                if not torch.isfinite(loss):
                    raise FloatingPointError("training loss is non-finite")
                (loss / accumulation).backward()
                value = float(loss.detach())
                epoch_loss += value
                total_loss += value
                observed_batches += 1
                if (micro_index + 1) % accumulation == 0:
                    lr = learning_rate_at(
                        optimizer_step, total_steps, float(fairness["learning_rate"])
                    )
                    for group in optimizer.param_groups:
                        group["lr"] = lr
                    norm = torch.nn.utils.clip_grad_norm_(
                        parameters, float(training["gradient_clip_global_l2"])
                    )
                    if not torch.isfinite(norm):
                        raise FloatingPointError("gradient norm is non-finite")
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
            epoch_receipts.append(
                {
                    "epoch": epoch,
                    "permutation_sha256": permutation_sha256(permutation),
                    "micro_batches": len(loader),
                    "mean_loss": epoch_loss / len(loader),
                }
            )
            _save_torch_atomic(
                recovery_path,
                {
                    **binding,
                    "config_id": config_id,
                    "next_epoch": epoch + 1,
                    "optimizer_step": optimizer_step,
                    "observed_micro_batches": observed_batches,
                    "total_loss": total_loss,
                    "epoch_receipts": epoch_receipts,
                    "coordinates": store.state_dict(),
                    "optimizer": optimizer.state_dict(),
                },
            )
        if optimizer_step != total_steps:
            raise RuntimeError("actual optimizer steps differ from frozen schedule")
        final_frozen = frozen_parameter_hash(model)
        if final_frozen != initial_frozen:
            raise RuntimeError("frozen base parameters changed")
        coordinates = {
            name: tensor.detach().cpu() for name, tensor in store.coordinates.items()
        }
        archive, encoding = encode_coordinates(
            coordinates, str(config["structure"]), int(config["seed"])
        )
        archive_path = output / "adapter.mms2"
        archive_path.write_bytes(archive)
        checkpoint_path = output / "checkpoint.pt"
        _save_torch_atomic(
            checkpoint_path,
            {
                **binding,
                "config_id": config_id,
                "coordinates": coordinates,
                "optimizer": optimizer.state_dict(),
                "optimizer_step": optimizer_step,
            },
        )
        manifest = {
            **binding,
            "schema_version": 1,
            "status": "complete",
            "config_id": config_id,
            "config": config,
            "git_commit": binding["git_commit"],
            "data_sha256": sha256_file(data_path),
            "base_checkpoint_sha256": sha256_file(checkpoint),
            "actual_optimizer_steps": optimizer_step,
            "final_training_loss": total_loss / observed_batches,
            "trainable_parameter_count": sum(p.numel() for p in parameters),
            "frozen_parameter_sha256_before": initial_frozen,
            "frozen_parameter_sha256_after": final_frozen,
            "frozen_parameters_unchanged": True,
            "coordinate_state_sha256": tensor_state_sha256(coordinates),
            "encoding": {
                **encoding,
                "path": str(archive_path),
                "sha256": sha256_file(archive_path),
            },
            "checkpoint": {
                "path": str(checkpoint_path),
                "sha256": sha256_file(checkpoint_path),
            },
            "epoch_receipts": epoch_receipts,
            "runtime_seconds": time.time() - started,
        }
        write_json_atomic(complete_path, manifest)
        write_json_atomic(
            status_path,
            {
                **binding,
                "config_id": config_id,
                "status": "complete",
                "manifest_sha256": sha256_file(complete_path),
            },
        )
        return manifest
    except BaseException as error:
        write_json_atomic(
            status_path,
            {
                **binding,
                "config_id": config_id,
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "automatic_configuration_change": False,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--smoke-batches", type=int, choices=(1, 2))
    args = parser.parse_args()
    config = load_candidate(args.config_id)
    if args.smoke_batches:
        result = {
            **bindings(),
            "config_id": args.config_id,
            "status": "smoke_only",
            **run_synthetic_smoke(config["structure"], args.smoke_batches),
        }
    else:
        if args.artifact_root is None:
            parser.error("--artifact-root is required for formal training")
        result = train_candidate(
            args.config_id, args.artifact_root, args.output_root, args.device
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
