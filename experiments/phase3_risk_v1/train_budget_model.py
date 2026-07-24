#!/usr/bin/env python3
"""Train one frozen Phase 3 budget config with the unchanged Stage2 schedule."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase3_risk_v1.budget_runtime import (
    build_budget_model,
    load_frozen_config,
    verify_budget_runtime,
)
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    sha256_file,
)
from experiments.stage2_model import (
    model_structure_receipt,
    tensor_state_sha256,
)
from model.global_subspace_lora import (
    coordinate_parameters,
    coordinate_state,
)
from trainer.train_stage2 import (
    frozen_parameter_hash,
    learning_rate_at,
    move_pixels,
    permutation_for_epoch,
    permutation_sha256,
    seed_everything,
)


def _save_torch_atomic(path: Path, value) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def _validate_frozen_training(config, protocol) -> None:
    configured = config["training"]
    frozen = protocol.payload["training"]
    comparisons = {
        "train_seed": (configured["train_seed"], frozen["formal_seed"]),
        "epochs": (configured["epochs"], frozen["epochs"]),
        "micro_batch_size": (
            configured["micro_batch_size"],
            frozen["micro_batch_size"],
        ),
        "gradient_accumulation_steps": (
            configured["gradient_accumulation_steps"],
            frozen["gradient_accumulation_steps"],
        ),
        "effective_batch_size": (
            configured["effective_batch_size"],
            frozen["effective_batch_size"],
        ),
        "optimizer": (configured["optimizer"], frozen["optimizer"]),
        "learning_rate_schedule": (
            configured["learning_rate_schedule"],
            frozen["learning_rate_schedule"],
        ),
        "gradient_clip_global_l2": (
            configured["gradient_clip_global_l2"],
            frozen["gradient_clip_global_l2"],
        ),
        "autocast_dtype": (
            configured["autocast_dtype"],
            frozen["autocast_dtype"],
        ),
    }
    differences = {
        key: {"config": left, "frozen": right}
        for key, (left, right) in comparisons.items()
        if left != right
    }
    if differences:
        raise ValueError(f"budget training differs from Stage2: {differences}")
    selected = protocol.payload["development"]["selected_learning_rates"][
        "M2_M3"
    ]
    if float(configured["learning_rate"]) != float(selected):
        raise ValueError("budget learning rate differs from frozen M2/M3 value")


def train(args: argparse.Namespace) -> dict:
    config, config_receipt = load_frozen_config(args.config_id)
    if config["budget"] == "current":
        raise ValueError("current budget is frozen and must not be retrained")
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"training output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    try:
        protocol, runtime = verify_budget_runtime(
            config,
            artifact_root=args.artifact_root,
            require_gpu=True,
        )
        _validate_frozen_training(config, protocol)
        seed_everything(int(config["training"]["train_seed"]))
        device = torch.device(args.device)
        if device.type != "cuda" or not torch.cuda.is_available():
            raise RuntimeError("budget training requires an explicit CUDA device")
        if torch.cuda.device_count() != 1:
            raise RuntimeError("budget training must see exactly one GPU")

        model = build_budget_model(
            config, protocol, device=device, dtype=torch.float32
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        data_path = Path(runtime["training_data"]["path"])
        dataset = Stage2CaptionDataset(
            data_path,
            tokenizer,
            model_group=config["method"],
            processor=getattr(model, "processor", None),
            max_length=protocol.payload["training"]["max_sequence_length"],
            image_token_count=protocol.payload["model"]["image_token_count"],
        )
        if len(dataset) != int(config["data"]["draw_count"]):
            raise ValueError("training example count differs from frozen config")

        training = config["training"]
        micro_batch = int(training["micro_batch_size"])
        accumulation = int(training["gradient_accumulation_steps"])
        epochs = int(training["epochs"])
        usable_micro_batches = len(dataset) // micro_batch
        if (
            len(dataset) % micro_batch
            or usable_micro_batches % accumulation
        ):
            raise ValueError("data does not form complete accumulation windows")
        total_steps = epochs * usable_micro_batches // accumulation
        if total_steps != int(training["learning_rate_schedule"]["total_steps"]):
            raise ValueError("optimizer-step count differs from frozen config")

        parameters = [
            parameter for _, parameter in coordinate_parameters(model)
        ]
        optimizer_settings = training["optimizer"]
        optimizer = torch.optim.AdamW(
            parameters,
            lr=float(training["learning_rate"]),
            betas=tuple(optimizer_settings["betas"]),
            eps=float(optimizer_settings["eps"]),
            weight_decay=float(optimizer_settings["weight_decay"]),
            amsgrad=bool(optimizer_settings["amsgrad"]),
        )
        initial_structure = model_structure_receipt(model)
        initial_frozen_hash = frozen_parameter_hash(model)
        initial_coordinates = coordinate_state(model)
        if any(
            torch.count_nonzero(value).item()
            for value in initial_coordinates.values()
        ):
            raise RuntimeError("budget coordinates are not initialized to zero")

        model.train()
        if hasattr(model, "vision_encoder"):
            model.vision_encoder.eval()
        optimizer.zero_grad(set_to_none=True)
        optimizer_step = 0
        epoch_receipts = []
        running_loss = 0.0
        observed_micro_batches = 0
        num_workers = int(
            protocol.payload["training"]["dataloader"]["num_workers"]
        )
        for epoch_index in range(epochs):
            permutation = permutation_for_epoch(
                len(dataset), int(training["train_seed"]), epoch_index
            )
            loader = DataLoader(
                dataset,
                batch_size=micro_batch,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=num_workers,
                persistent_workers=num_workers > 0,
                pin_memory=True,
                prefetch_factor=(
                    protocol.payload["training"]["dataloader"][
                        "prefetch_factor"
                    ]
                    if num_workers > 0
                    else None
                ),
                collate_fn=stage2_collate,
            )
            epoch_loss = 0.0
            for micro_index, (input_ids, labels, pixels) in enumerate(loader):
                input_ids = input_ids.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                pixels = move_pixels(pixels, device)
                with torch.autocast(
                    device_type="cuda", dtype=torch.bfloat16, enabled=True
                ):
                    result = model(
                        input_ids=input_ids,
                        labels=labels,
                        pixel_values=pixels,
                    )
                    loss = result.loss / accumulation
                if not torch.isfinite(loss):
                    raise FloatingPointError("training loss is NaN or Inf")
                loss.backward()
                epoch_loss += float(loss.detach()) * accumulation
                observed_micro_batches += 1
                if (micro_index + 1) % accumulation == 0:
                    learning_rate = learning_rate_at(
                        optimizer_step,
                        total_steps,
                        float(training["learning_rate"]),
                    )
                    for parameter_group in optimizer.param_groups:
                        parameter_group["lr"] = learning_rate
                    norm = torch.nn.utils.clip_grad_norm_(
                        parameters,
                        float(training["gradient_clip_global_l2"]),
                    )
                    if not torch.isfinite(norm):
                        raise FloatingPointError("gradient norm is NaN or Inf")
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
            epoch_receipts.append(
                {
                    "epoch_index": epoch_index,
                    "epoch_seed": int(training["train_seed"]) + epoch_index,
                    "permutation_sha256": permutation_sha256(permutation),
                    "micro_batches": len(loader),
                    "mean_micro_batch_loss": epoch_loss / len(loader),
                }
            )
            running_loss += epoch_loss
            print(
                f"config={config['config_id']} epoch={epoch_index + 1}/"
                f"{epochs} optimizer_step={optimizer_step}/{total_steps} "
                f"mean_loss={epoch_loss / len(loader):.8f}",
                flush=True,
            )

        if optimizer_step != total_steps:
            raise RuntimeError("observed optimizer-step count differs from schedule")
        final_frozen_hash = frozen_parameter_hash(model)
        if final_frozen_hash != initial_frozen_hash:
            raise RuntimeError("one or more frozen base parameters changed")
        final_coordinates = coordinate_state(model)
        if not any(
            torch.count_nonzero(value).item()
            for value in final_coordinates.values()
        ):
            raise RuntimeError("training left all coordinates at exact zero")
        dimensions = {
            name: int(value.numel())
            for name, value in final_coordinates.items()
        }
        if dimensions != config["coordinate_dimensions"]:
            raise RuntimeError("trained coordinate dimensions differ from config")

        coordinates_path = output / "coordinates.pt"
        checkpoint_path = output / "training_checkpoint.pt"
        common_payload = {
            "coordinates": final_coordinates,
            "config_id": config["config_id"],
            "config_sha256": config_receipt["sha256"],
            "model_group": config["method"],
            "mapping_root": config["mapping_root"],
            "train_seed": training["train_seed"],
            "learning_rate": training["learning_rate"],
            "protocol": protocol.reference(),
        }
        _save_torch_atomic(coordinates_path, common_payload)
        _save_torch_atomic(
            checkpoint_path,
            {
                **common_payload,
                "optimizer": optimizer.state_dict(),
                "completed_epochs": epochs,
                "optimizer_step": optimizer_step,
                "epoch_receipts": epoch_receipts,
            },
        )
        manifest = {
            "schema_version": 1,
            "status": "complete",
            "experiment_type": "phase3_equal_coordinate_budget",
            "formal_stage2_certification_run": False,
            "config_id": config["config_id"],
            "config": config_receipt,
            "method": config["method"],
            "budget": config["budget"],
            "mapping_root": config["mapping_root"],
            "total_coordinate_budget": config["total_coordinate_budget"],
            "coordinate_dimensions": dimensions,
            "runtime_preflight": runtime,
            "data": {
                "path": str(data_path),
                "sha256": sha256_file(data_path),
                "examples": len(dataset),
            },
            "training": {
                "train_seed": training["train_seed"],
                "epochs": epochs,
                "micro_batch_size": micro_batch,
                "gradient_accumulation_steps": accumulation,
                "effective_batch_size": micro_batch * accumulation,
                "optimizer": optimizer_settings,
                "learning_rate": training["learning_rate"],
                "learning_rate_schedule": training["learning_rate_schedule"],
                "optimizer_steps_expected": total_steps,
                "optimizer_steps_observed": optimizer_step,
                "observed_micro_batches": observed_micro_batches,
                "mean_micro_batch_loss": running_loss
                / observed_micro_batches,
                "epoch_receipts": epoch_receipts,
                "all_losses_finite": True,
                "all_gradient_norms_finite": True,
                "automatic_hyperparameter_tuning": False,
                "checkpoint_selection": "final_frozen_schedule_state_only",
                "retry_count": 0,
            },
            "model": {
                "initial_structure": initial_structure,
                "initial_frozen_parameter_sha256": initial_frozen_hash,
                "final_frozen_parameter_sha256": final_frozen_hash,
                "frozen_parameters_unchanged": True,
                "final_coordinate_state_sha256": tensor_state_sha256(
                    final_coordinates
                ),
            },
            "coordinates": {
                "path": str(coordinates_path),
                "sha256": sha256_file(coordinates_path),
            },
            "checkpoint": {
                "path": str(checkpoint_path),
                "sha256": sha256_file(checkpoint_path),
            },
            "runtime": {
                "seconds": time.time() - started,
                "python": sys.version.split()[0],
                "torch": torch.__version__,
                "cuda_runtime": torch.version.cuda,
                "cudnn": torch.backends.cudnn.version(),
                "visible_device_count": torch.cuda.device_count(),
                "visible_device_name": torch.cuda.get_device_name(0),
            },
        }
        atomic_write_json(output / "training_manifest.json", manifest)
        return manifest
    except BaseException as error:
        atomic_write_json(
            output / "failure_receipt.json",
            {
                "status": "failed",
                "config_id": args.config_id,
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    manifest = train(args)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
