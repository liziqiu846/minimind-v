#!/usr/bin/env python3
"""Train exactly the Stage 2 coordinate tensors under the frozen schedule."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import struct
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.stage2_model import (
    build_stage2_model,
    model_structure_receipt,
    tensor_state_sha256,
)
from experiments.stage2_protocol import (
    DEFAULT_DRAFT,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)
from model.global_subspace_lora import coordinate_parameters, coordinate_state


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def permutation_for_epoch(size: int, train_seed: int, epoch_index: int) -> torch.Tensor:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(train_seed + epoch_index)
    return torch.randperm(size, generator=generator)


def permutation_sha256(permutation: torch.Tensor) -> str:
    digest = hashlib.sha256(b"stage2-epoch-permutation-v1\0")
    for value in permutation.tolist():
        digest.update(struct.pack("<Q", value))
    return digest.hexdigest()


def learning_rate_at(step: int, total_steps: int, maximum: float) -> float:
    if not 0 <= step < total_steps or total_steps < 2:
        raise ValueError("invalid cosine schedule step")
    minimum = 0.1 * maximum
    return minimum + 0.5 * (maximum - minimum) * (
        1.0 + math.cos(math.pi * step / (total_steps - 1))
    )


def move_pixels(pixel_values, device):
    if pixel_values is None:
        return None
    if isinstance(pixel_values, dict):
        return {name: value.to(device, non_blocking=True) for name, value in pixel_values.items()}
    return pixel_values.to(device, non_blocking=True)


def frozen_parameter_hash(model: torch.nn.Module) -> str:
    return tensor_state_sha256(
        {
            name: parameter
            for name, parameter in model.named_parameters()
            if not parameter.requires_grad
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--model-group", choices=("M0", "M1", "M2", "M3"), required=True)
    parser.add_argument("--mapping-root", type=int)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--learning-rate", type=float, required=True)
    parser.add_argument("--train-seed", type=int, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--num-workers", type=int)
    return parser.parse_args()


def validate_args(args: argparse.Namespace, protocol: Stage2Protocol) -> None:
    training = protocol.payload["training"]
    if args.model_group == "M1" and args.mapping_root is not None:
        raise ValueError("M1 does not use a mapping root")
    if args.model_group != "M1" and args.mapping_root not in (43101, 43102, 43103):
        raise ValueError("hashed Stage 2 groups require a predeclared mapping root")
    if args.learning_rate not in protocol.payload["development"]["learning_rates"]:
        raise ValueError("learning rate is outside the predeclared grid")
    if args.formal:
        protocol.require_frozen()
        if args.train_seed != training["formal_seed"]:
            raise ValueError("formal train seed differs from the frozen protocol")
        if args.max_samples:
            raise ValueError("formal training cannot limit samples")
        selected = protocol.payload["development"]["selected_learning_rates"]
        key = "M2_M3" if args.model_group in ("M2", "M3") else args.model_group
        if args.learning_rate != selected[key]:
            raise ValueError("formal learning rate differs from the frozen selection")
        protocol.verify_confirmation_data(args.data, "train")


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=args.formal)
    protocol.verify_immutable_inputs()
    if args.formal and protocol.payload.get("schema_version") == 2:
        protocol.verify_runtime_integrity()
    validate_args(args, protocol)
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(f"training output is not empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = args.output_dir / "failure_receipt.json"
    started = time.time()
    try:
        seed_everything(args.train_seed)
        device = torch.device(args.device)
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device was requested but is unavailable")
        model = build_stage2_model(
            args.model_group, protocol, args.mapping_root, device=device
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        dataset = Stage2CaptionDataset(
            args.data,
            tokenizer,
            model_group=args.model_group,
            processor=getattr(model, "processor", None),
            max_length=protocol.payload["training"]["max_sequence_length"],
            image_token_count=protocol.payload["model"]["image_token_count"],
        )
        if args.max_samples:
            if args.max_samples > len(dataset):
                raise ValueError("max_samples exceeds dataset length")
            dataset = Subset(dataset, range(args.max_samples))
        training = protocol.payload["training"]
        micro_batch = training["micro_batch_size"]
        accumulation = training["gradient_accumulation_steps"]
        epochs = training["epochs"]
        usable_micro_batches = len(dataset) // micro_batch
        if usable_micro_batches % accumulation:
            raise ValueError("dataset does not form complete gradient-accumulation windows")
        total_steps = epochs * usable_micro_batches // accumulation
        if args.formal and total_steps != training["learning_rate_schedule"]["total_steps"]:
            raise ValueError("formal optimizer-step count differs from protocol")
        num_workers = args.num_workers
        if num_workers is None:
            num_workers = training["dataloader"]["num_workers"]
        parameters = [parameter for _, parameter in coordinate_parameters(model)]
        optimizer = torch.optim.AdamW(
            parameters,
            lr=args.learning_rate,
            betas=tuple(training["optimizer"]["betas"]),
            eps=training["optimizer"]["eps"],
            weight_decay=training["optimizer"]["weight_decay"],
            amsgrad=training["optimizer"]["amsgrad"],
        )
        initial_structure = model_structure_receipt(model)
        initial_frozen_hash = frozen_parameter_hash(model)
        initial_coordinates = coordinate_state(model)
        if any(torch.count_nonzero(value).item() for value in initial_coordinates.values()):
            raise RuntimeError("Stage 2 coordinates are not initialized to exact zero")

        model.train()
        if hasattr(model, "vision_encoder"):
            model.vision_encoder.eval()
        optimizer.zero_grad(set_to_none=True)
        optimizer_step = 0
        epoch_receipts = []
        running_loss = 0.0
        observed_micro_batches = 0
        for epoch_index in range(epochs):
            permutation = permutation_for_epoch(len(dataset), args.train_seed, epoch_index)
            loader = DataLoader(
                dataset,
                batch_size=micro_batch,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=num_workers,
                persistent_workers=num_workers > 0,
                pin_memory=device.type == "cuda",
                prefetch_factor=(
                    training["dataloader"]["prefetch_factor"] if num_workers > 0 else None
                ),
                collate_fn=stage2_collate,
            )
            epoch_loss = 0.0
            for micro_index, (input_ids, labels, pixels) in enumerate(loader):
                input_ids = input_ids.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                pixels = move_pixels(pixels, device)
                with torch.autocast(
                    device_type="cuda",
                    dtype=torch.bfloat16,
                    enabled=device.type == "cuda",
                ):
                    output = model(input_ids=input_ids, labels=labels, pixel_values=pixels)
                    loss = output.loss / accumulation
                if not torch.isfinite(loss):
                    raise FloatingPointError("training loss is NaN or Inf")
                loss.backward()
                epoch_loss += float(loss.detach()) * accumulation
                observed_micro_batches += 1
                if (micro_index + 1) % accumulation == 0:
                    lr = learning_rate_at(optimizer_step, total_steps, args.learning_rate)
                    for parameter_group in optimizer.param_groups:
                        parameter_group["lr"] = lr
                    norm = torch.nn.utils.clip_grad_norm_(
                        parameters, training["gradient_clip_global_l2"]
                    )
                    if not torch.isfinite(norm):
                        raise FloatingPointError("gradient norm is NaN or Inf")
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
            epoch_receipts.append(
                {
                    "epoch_index": epoch_index,
                    "epoch_seed": args.train_seed + epoch_index,
                    "permutation_sha256": permutation_sha256(permutation),
                    "micro_batches": len(loader),
                    "mean_micro_batch_loss": epoch_loss / len(loader),
                }
            )
            running_loss += epoch_loss
            print(
                f"epoch={epoch_index + 1}/{epochs} optimizer_step={optimizer_step}/{total_steps} "
                f"mean_loss={epoch_loss / len(loader):.8f}",
                flush=True,
            )
        if optimizer_step != total_steps:
            raise RuntimeError("observed optimizer-step count differs from schedule")
        final_frozen_hash = frozen_parameter_hash(model)
        if final_frozen_hash != initial_frozen_hash:
            raise RuntimeError("one or more frozen base parameters changed")
        final_coordinates = coordinate_state(model)
        if not any(torch.count_nonzero(value).item() for value in final_coordinates.values()):
            raise RuntimeError("training left every coordinate at exact zero")

        coordinates_path = args.output_dir / "coordinates.pt"
        checkpoint_path = args.output_dir / "training_checkpoint.pt"
        temporary = coordinates_path.with_name(coordinates_path.name + ".tmp")
        torch.save(
            {
                "coordinates": final_coordinates,
                "model_group": args.model_group,
                "mapping_root": args.mapping_root,
                "train_seed": args.train_seed,
                "learning_rate": args.learning_rate,
                "protocol": protocol.reference(),
            },
            temporary,
        )
        os.replace(temporary, coordinates_path)
        temporary = checkpoint_path.with_name(checkpoint_path.name + ".tmp")
        torch.save(
            {
                "coordinates": final_coordinates,
                "optimizer": optimizer.state_dict(),
                "completed_epochs": epochs,
                "optimizer_step": optimizer_step,
                "epoch_receipts": epoch_receipts,
                "protocol": protocol.reference(),
            },
            temporary,
        )
        os.replace(temporary, checkpoint_path)
        manifest = {
            "schema_version": 1,
            "status": "complete",
            "formal": args.formal,
            "model_group": args.model_group,
            "mapping_root": args.mapping_root,
            "train_seed": args.train_seed,
            "learning_rate": args.learning_rate,
            "protocol": protocol.reference(),
            "data": {
                "path": str(args.data.resolve()),
                "sha256": sha256_file(args.data),
                "examples": len(dataset),
            },
            "training": {
                "epochs": epochs,
                "micro_batch_size": micro_batch,
                "gradient_accumulation_steps": accumulation,
                "effective_batch_size": micro_batch * accumulation,
                "optimizer_steps": optimizer_step,
                "observed_micro_batches": observed_micro_batches,
                "mean_micro_batch_loss": running_loss / observed_micro_batches,
                "epoch_receipts": epoch_receipts,
            },
            "model": {
                "initial_structure": initial_structure,
                "initial_frozen_parameter_sha256": initial_frozen_hash,
                "final_frozen_parameter_sha256": final_frozen_hash,
            },
            "coordinates": {
                "path": str(coordinates_path.resolve()),
                "sha256": sha256_file(coordinates_path),
                "dimensions": {name: value.numel() for name, value in final_coordinates.items()},
            },
            "checkpoint": {
                "path": str(checkpoint_path.resolve()),
                "sha256": sha256_file(checkpoint_path),
            },
            "runtime": {
                "seconds": time.time() - started,
                "python": sys.version.split()[0],
                "torch": torch.__version__,
                "cuda_runtime": torch.version.cuda,
                "cudnn": torch.backends.cudnn.version(),
                "device": str(device),
                "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
            },
        }
        write_json_atomic(args.output_dir / "training_manifest.json", manifest)
        print(json.dumps(manifest, indent=2, sort_keys=True))
    except BaseException as error:
        write_json_atomic(
            failure_path,
            {
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "arguments": vars(args) | {"protocol": str(args.protocol), "data": str(args.data), "output_dir": str(args.output_dir)},
            },
        )
        raise


if __name__ == "__main__":
    main()
