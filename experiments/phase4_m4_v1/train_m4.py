#!/usr/bin/env python3
"""Train one frozen M4 config; the formal CLI accepts only a config ID."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import time
from pathlib import Path
from typing import Any, Mapping

import torch
from torch import nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase4_m4_v1.m4_configs import (
    REPO_ROOT,
    load_frozen_config,
    sha256_file,
)
from experiments.phase4_m4_v1.m4_model import (
    build_m4_model,
    m4_model_structure_receipt,
)
from experiments.stage2_model import tensor_state_sha256
from experiments.stage2_protocol import Stage2Protocol
from model.hybrid_subspace_lora import (
    m4_coordinate_parameters,
    m4_coordinate_state,
)
from trainer.train_stage2 import (
    learning_rate_at,
    move_pixels,
    permutation_for_epoch,
    permutation_sha256,
    seed_everything,
)


ARTIFACT_ROOT_ENV = "PHASE4_ARTIFACT_ROOT"
RUNTIME_SCHEDULE_FIELDS = (
    "formula",
    "minimum_ratio",
    "total_steps",
    "warmup_steps",
)


def _name_bytes(name: str) -> bytes:
    encoded = name.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def frozen_parameter_hashes(model: nn.Module) -> dict[str, str]:
    coordinate_ids = {
        id(parameter) for _, parameter in m4_coordinate_parameters(model)
    }
    output = {}
    for name, parameter in model.named_parameters():
        if id(parameter) in coordinate_ids:
            continue
        if parameter.requires_grad:
            raise RuntimeError(f"non-coordinate parameter is trainable: {name}")
        value = parameter.detach().cpu().contiguous()
        output[name] = hashlib.sha256(
            value.view(torch.uint8).numpy().tobytes()
        ).hexdigest()
    if not output:
        raise RuntimeError("M4 model has no frozen base parameters")
    return output


def frozen_parameter_hash(model: nn.Module) -> str:
    digest = hashlib.sha256(b"phase4-m4-frozen-parameters-v1\0")
    for name, value in sorted(
        frozen_parameter_hashes(model).items(),
        key=lambda row: row[0].encode("utf-8"),
    ):
        digest.update(_name_bytes(name))
        digest.update(bytes.fromhex(value))
    return digest.hexdigest()


def validate_optimizer_parameter_set(
    model: nn.Module, optimizer: torch.optim.Optimizer
) -> dict[str, Any]:
    expected = [parameter for _, parameter in m4_coordinate_parameters(model)]
    actual = [
        parameter
        for group in optimizer.param_groups
        for parameter in group["params"]
    ]
    if (
        len(expected) != 4
        or len(actual) != 4
        or len({id(parameter) for parameter in actual}) != 4
        or {id(parameter) for parameter in actual}
        != {id(parameter) for parameter in expected}
    ):
        raise RuntimeError(
            "optimizer parameters are not exactly the four M4 coordinates"
        )
    trainable = [
        parameter for parameter in model.parameters() if parameter.requires_grad
    ]
    if {id(parameter) for parameter in trainable} != {
        id(parameter) for parameter in expected
    }:
        raise RuntimeError("model trainable set differs from M4 coordinates")
    return {
        "status": "passed",
        "coordinate_parameter_count": 4,
        "coordinate_element_count": sum(
            parameter.numel() for parameter in expected
        ),
    }


def build_coordinate_optimizer(
    model: nn.Module, training: Mapping[str, Any]
) -> torch.optim.AdamW:
    parameters = [
        parameter for _, parameter in m4_coordinate_parameters(model)
    ]
    settings = training["optimizer"]
    if settings.get("name") != "torch.optim.AdamW":
        raise ValueError("M4 optimizer must remain torch.optim.AdamW")
    optimizer = torch.optim.AdamW(
        parameters,
        lr=float(training["learning_rate"]),
        betas=tuple(float(value) for value in settings["betas"]),
        eps=float(settings["eps"]),
        weight_decay=float(settings["weight_decay"]),
        amsgrad=bool(settings["amsgrad"]),
    )
    validate_optimizer_parameter_set(model, optimizer)
    return optimizer


def validate_frozen_training_configuration(
    training: Mapping[str, Any],
    frozen_training: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare every executable field while leaving prose in its authority."""

    scalar_fields = (
        "formal_seed",
        "epochs",
        "micro_batch_size",
        "gradient_accumulation_steps",
        "gradient_clip_global_l2",
        "autocast_dtype",
    )
    config_names = {
        "formal_seed": "train_seed",
        "epochs": "epochs",
        "micro_batch_size": "micro_batch_size",
        "gradient_accumulation_steps": "gradient_accumulation_steps",
        "gradient_clip_global_l2": "gradient_clip_global_l2",
        "autocast_dtype": "autocast_dtype",
    }
    expected_scalars = {
        config_names[name]: frozen_training[name] for name in scalar_fields
    }
    actual_scalars = {
        name: training[name] for name in expected_scalars
    }
    if actual_scalars != expected_scalars:
        raise ValueError("M4 training fields differ from frozen Stage 2")

    frozen_schedule = frozen_training["learning_rate_schedule"]
    configured_schedule = training["learning_rate_schedule"]
    if (
        tuple(configured_schedule) != RUNTIME_SCHEDULE_FIELDS
        or any(name not in frozen_schedule for name in RUNTIME_SCHEDULE_FIELDS)
        or dict(configured_schedule)
        != {
            name: frozen_schedule[name]
            for name in RUNTIME_SCHEDULE_FIELDS
        }
        or frozen_schedule.get("update_unit") != "optimizer step"
        or frozen_schedule.get("t_values") != "0 through 1874"
    ):
        raise ValueError(
            "M4 executable learning-rate schedule differs from frozen Stage 2"
        )
    return {
        "status": "passed",
        "executable_scalar_fields": list(expected_scalars),
        "executable_schedule_fields": list(RUNTIME_SCHEDULE_FIELDS),
        "stage2_descriptive_schedule_fields": {
            "update_unit": frozen_schedule["update_unit"],
            "t_values": frozen_schedule["t_values"],
        },
        "scientific_training_values_changed": False,
    }


def cpu_smoke_step(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    loss: torch.Tensor,
) -> dict[str, Any]:
    """Perform one caller-supplied synthetic CPU loss step with safeguards."""

    if next(model.parameters()).device.type != "cpu":
        raise ValueError("the synthetic smoke helper is CPU-only")
    before = frozen_parameter_hash(model)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    after = frozen_parameter_hash(model)
    if before != after:
        raise RuntimeError("a frozen base parameter changed in the CPU smoke step")
    return {
        "status": "passed",
        "frozen_parameter_sha256_before": before,
        "frozen_parameter_sha256_after": after,
        "frozen_parameters_unchanged": True,
    }


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _atomic_torch(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def _artifact_root() -> Path:
    value = os.environ.get(ARTIFACT_ROOT_ENV, "").strip()
    if not value:
        raise ValueError(
            f"{ARTIFACT_ROOT_ENV} must identify the immutable runtime root"
        )
    return Path(value).resolve()


def _stage2_protocol(config: Mapping[str, Any]) -> Stage2Protocol:
    reference = config["base_assets"]["stage2_protocol"]
    path = REPO_ROOT / reference["relative_path"]
    if sha256_file(path) != reference["sha256"]:
        raise ValueError("Stage 2 protocol differs from the frozen M4 config")
    protocol = Stage2Protocol.load(path)
    protocol.verify_immutable_inputs()
    return protocol


def train(config_id: str) -> dict[str, Any]:
    """Execute one full predeclared config when explicitly invoked later."""

    config, config_receipt = load_frozen_config(config_id)
    artifact_root = _artifact_root()
    output = artifact_root / config["output_relative_path"] / "training"
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"M4 training output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    try:
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise RuntimeError(
                "formal M4 training requires exactly one visible CUDA device"
            )
        protocol = _stage2_protocol(config)
        training = config["training"]
        frozen_training = protocol.payload["training"]
        training_protocol_validation = validate_frozen_training_configuration(
            training, frozen_training
        )
        frozen_optimizer = {
            key: value
            for key, value in frozen_training["optimizer"].items()
            if key != "parameters"
        }
        configured_optimizer = {
            key: value
            for key, value in training["optimizer"].items()
            if key != "parameters"
        }
        if (
            configured_optimizer != frozen_optimizer
            or training["optimizer"].get("parameters")
            != "exactly the four M4 coordinate tensors"
        ):
            raise ValueError(
                "M4 optimizer numerics or four-coordinate scope changed"
            )
        selected_lr = protocol.payload["development"][
            "selected_learning_rates"
        ]["M2_M3"]
        if float(training["learning_rate"]) != float(selected_lr):
            raise ValueError("M4 learning rate differs from frozen M2/M3")

        seed_everything(int(training["train_seed"]))
        device = torch.device("cuda:0")
        model = build_m4_model(
            config,
            protocol,
            device=device,
            dtype=torch.float32,
            verify_assets=False,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"), local_files_only=True
        )
        data_path = (
            artifact_root
            / "dataset/stage2_confirm_v2_seed2028/train.parquet"
        )
        expected_data_sha = protocol.payload["data"]["reused_confirmation"][
            "train_sha256"
        ]
        if not data_path.is_file() or sha256_file(data_path) != expected_data_sha:
            raise ValueError("M4 training data is absent or differs from Stage 2")
        dataset = Stage2CaptionDataset(
            data_path,
            tokenizer,
            model_group="M3",
            processor=getattr(model, "processor", None),
            max_length=protocol.payload["training"]["max_sequence_length"],
            image_token_count=protocol.payload["model"]["image_token_count"],
        )
        if len(dataset) != int(protocol.payload["data"]["train_draws"]):
            raise ValueError("M4 training draw count differs from Stage 2")

        micro_batch = int(training["micro_batch_size"])
        accumulation = int(training["gradient_accumulation_steps"])
        epochs = int(training["epochs"])
        usable_micro_batches = len(dataset) // micro_batch
        if (
            len(dataset) % micro_batch
            or usable_micro_batches % accumulation
        ):
            raise ValueError("M4 data does not form complete accumulation windows")
        total_steps = epochs * usable_micro_batches // accumulation
        if total_steps != int(
            training["learning_rate_schedule"]["total_steps"]
        ):
            raise ValueError("M4 optimizer step count differs from config")

        optimizer = build_coordinate_optimizer(model, training)
        parameters = [
            parameter for _, parameter in m4_coordinate_parameters(model)
        ]
        initial_frozen_hash = frozen_parameter_hash(model)
        initial_coordinates = m4_coordinate_state(model)
        if any(torch.count_nonzero(value).item() for value in initial_coordinates.values()):
            raise RuntimeError("M4 coordinates are not initialized to zero")

        model.train()
        model.vision_encoder.eval()
        optimizer.zero_grad(set_to_none=True)
        optimizer_step = 0
        epoch_receipts = []
        observed_micro_batches = 0
        total_loss = 0.0
        for epoch_index in range(epochs):
            permutation = permutation_for_epoch(
                len(dataset), int(training["train_seed"]), epoch_index
            )
            loader = DataLoader(
                dataset,
                batch_size=micro_batch,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=int(
                    frozen_training["dataloader"]["num_workers"]
                ),
                persistent_workers=True,
                pin_memory=True,
                prefetch_factor=frozen_training["dataloader"][
                    "prefetch_factor"
                ],
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
                    raise FloatingPointError("M4 training loss is NaN or Inf")
                loss.backward()
                epoch_loss += float(loss.detach()) * accumulation
                observed_micro_batches += 1
                if (micro_index + 1) % accumulation == 0:
                    lr = learning_rate_at(
                        optimizer_step,
                        total_steps,
                        float(training["learning_rate"]),
                    )
                    for group in optimizer.param_groups:
                        group["lr"] = lr
                    norm = torch.nn.utils.clip_grad_norm_(
                        parameters,
                        float(training["gradient_clip_global_l2"]),
                    )
                    if not torch.isfinite(norm):
                        raise FloatingPointError("M4 gradient norm is NaN or Inf")
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
            total_loss += epoch_loss
            epoch_receipts.append(
                {
                    "epoch_index": epoch_index,
                    "permutation_sha256": permutation_sha256(permutation),
                    "micro_batches": len(loader),
                    "mean_micro_batch_loss": epoch_loss / len(loader),
                }
            )
        if optimizer_step != total_steps:
            raise RuntimeError("M4 observed optimizer steps differ from schedule")
        final_frozen_hash = frozen_parameter_hash(model)
        if final_frozen_hash != initial_frozen_hash:
            raise RuntimeError("one or more frozen M4 base parameters changed")
        coordinates = m4_coordinate_state(model)
        if not any(torch.count_nonzero(value).item() for value in coordinates.values()):
            raise RuntimeError("M4 training left all coordinates at zero")

        coordinates_path = output / "coordinates.pt"
        _atomic_torch(
            coordinates_path,
            {
                "coordinates": coordinates,
                "config_id": config["config_id"],
                "config_sha256": config_receipt["sha256"],
                "mapping_root": config["mapping_root"],
                "method": "M4",
            },
        )
        manifest = {
            "schema_version": 1,
            "status": "complete",
            "config_id": config["config_id"],
            "config": config_receipt,
            "formal_visual_generalization_certification": False,
            "coordinate_dimensions": {
                name: int(value.numel()) for name, value in coordinates.items()
            },
            "training": {
                "epochs": epochs,
                "optimizer_steps": optimizer_step,
                "observed_micro_batches": observed_micro_batches,
                "mean_micro_batch_loss": total_loss / observed_micro_batches,
                "epoch_receipts": epoch_receipts,
                "automatic_hyperparameter_tuning": False,
                "stage2_protocol_validation": training_protocol_validation,
            },
            "model": {
                "structure": m4_model_structure_receipt(model),
                "initial_frozen_parameter_sha256": initial_frozen_hash,
                "final_frozen_parameter_sha256": final_frozen_hash,
                "frozen_parameters_unchanged": True,
                "coordinate_state_sha256": tensor_state_sha256(coordinates),
            },
            "coordinates": {
                "path": str(coordinates_path),
                "sha256": sha256_file(coordinates_path),
            },
            "seconds": time.time() - started,
        }
        _atomic_json(output / "training_manifest.json", manifest)
        return manifest
    except BaseException as error:
        _atomic_json(
            output / "failure_receipt.json",
            {
                "status": "failed",
                "config_id": config_id,
                "error_type": type(error).__name__,
                "error": str(error),
                "seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = train(args.config_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
