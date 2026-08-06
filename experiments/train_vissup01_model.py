#!/usr/bin/env python3
"""Train one frozen VISSUP-01 M2-current condition and mapping root."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.stage2_model import (
    build_stage2_model,
    model_structure_receipt,
    tensor_state_sha256,
)
from experiments.stage2_protocol import Stage2Protocol
from experiments.vissup01 import (
    BASE_ROWS,
    TOTAL_TRAIN_ROWS,
    sha256_file,
    write_json,
)
from model.global_subspace_lora import coordinate_parameters, coordinate_state
from trainer.train_stage2 import (
    frozen_parameter_hash,
    learning_rate_at,
    move_pixels,
    permutation_for_epoch,
    permutation_sha256,
    seed_everything,
)


CONDITIONS = ("label-revealed", "visual-necessary")
MAPPING_ROOTS = (43101, 43102, 43103)
EXPECTED_DIMENSIONS = {
    "language": 1_187,
    "projector": 2_327,
    "vision": 582,
}
TRAIN_SEED = 2026
LEARNING_RATE = 0.05
EPOCHS = 3
MICRO_BATCH = 4
ACCUMULATION = 4
TOTAL_STEPS = 2_064


def _default_model_builder(
    protocol: Stage2Protocol,
    mapping_root: int,
    dimensions: Mapping[str, int],
    *,
    device: str | torch.device,
):
    if dict(dimensions) != EXPECTED_DIMENSIONS:
        raise ValueError("default VISSUP model requires M2-current dimensions")
    return build_stage2_model(
        "M2",
        protocol,
        mapping_root,
        device=device,
        dtype=torch.float32,
    )


DEFAULT_TRAINING_SPEC: dict[str, Any] = {
    "candidate": "VISSUP-01",
    "round": 2,
    "conditions": CONDITIONS,
    "mapping_roots": MAPPING_ROOTS,
    "dimensions_by_condition": {
        condition: EXPECTED_DIMENSIONS for condition in CONDITIONS
    },
    "data_condition_by_condition": {
        condition: condition for condition in CONDITIONS
    },
    "model_builder": _default_model_builder,
    "projection_preflight": None,
}


def _validated_spec(spec: Mapping[str, Any] | None) -> dict[str, Any]:
    value = dict(DEFAULT_TRAINING_SPEC if spec is None else spec)
    required = {
        "candidate",
        "round",
        "conditions",
        "mapping_roots",
        "dimensions_by_condition",
        "data_condition_by_condition",
        "model_builder",
        "projection_preflight",
    }
    if set(value) != required:
        raise ValueError("training spec fields differ from frozen interface")
    if (
        not value["candidate"]
        or not isinstance(value["round"], int)
        or not callable(value["model_builder"])
    ):
        raise ValueError("training spec identity or builder is invalid")
    if value["projection_preflight"] is not None and not callable(
        value["projection_preflight"]
    ):
        raise ValueError("projection preflight hook is not callable")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument(
        "--mapping-root", type=int, choices=MAPPING_ROOTS, required=True
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def _save_torch_atomic(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    torch.save(value, temporary)
    os.replace(temporary, path)


def _verify_prepared(
    prepared_dir: Path, condition: str
) -> tuple[dict, Path]:
    audit_path = prepared_dir / "data_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (
        audit.get("status") != "passed"
        or audit.get("eligible_for_training") is not True
        or audit.get("training_runs_started") != 0
        or audit.get("model_inference_performed") is not False
        or audit.get("final_confirmation_accessed") is not False
    ):
        raise ValueError("prepared data audit does not permit training")
    info = audit["data"][condition]
    path = Path(info["path"]).resolve()
    if (
        info["rows"] != TOTAL_TRAIN_ROWS
        or sha256_file(path) != info["sha256"]
    ):
        raise ValueError("condition training parquet differs from data audit")
    return audit, path


def _optimizer(parameters):
    return torch.optim.AdamW(
        parameters,
        lr=LEARNING_RATE,
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=0.01,
        amsgrad=False,
    )


def _smoke(
    model,
    dataset,
    parameters,
    *,
    device: torch.device,
    condition: str,
    mapping_root: int,
) -> dict:
    records = [dataset[BASE_ROWS], dataset[BASE_ROWS + 1]]
    input_ids, labels, pixels = stage2_collate(records)
    input_ids = input_ids.to(device)
    labels = labels.to(device)
    pixels = move_pixels(pixels, device)
    optimizer = _optimizer(parameters)
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(
        device_type="cuda", dtype=torch.bfloat16, enabled=True
    ):
        result = model(
            input_ids=input_ids,
            labels=labels,
            pixel_values=pixels,
        )
        loss = result.loss
    if not torch.isfinite(loss):
        raise FloatingPointError("smoke loss is NaN or Inf")
    loss.backward()
    norm = torch.nn.utils.clip_grad_norm_(parameters, 1.0)
    if not torch.isfinite(norm):
        raise FloatingPointError("smoke gradient norm is NaN or Inf")
    optimizer.step()
    return {
        "schema_version": 1,
        "status": "complete",
        "mode": "two_sample_non_scientific_smoke",
        "condition": condition,
        "mapping_root": mapping_root,
        "sample_indices": [BASE_ROWS, BASE_ROWS + 1],
        "loss": float(loss.detach()),
        "gradient_norm": float(norm.detach()),
        "loss_finite": True,
        "gradient_norm_finite": True,
        "scientific_result_computed": False,
        "coordinates_persisted": False,
    }


def train(
    args: argparse.Namespace,
    *,
    spec: Mapping[str, Any] | None = None,
) -> dict:
    started = time.time()
    run_spec = _validated_spec(spec)
    if (
        args.condition not in run_spec["conditions"]
        or args.mapping_root not in run_spec["mapping_roots"]
    ):
        raise ValueError("condition or mapping root is outside training spec")
    expected_dimensions = dict(
        run_spec["dimensions_by_condition"][args.condition]
    )
    data_condition = run_spec["data_condition_by_condition"][args.condition]
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"training output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    failure_path = output / "failure_receipt.json"
    try:
        if (
            args.device != "cuda:0"
            or not torch.cuda.is_available()
            or torch.cuda.device_count() != 1
        ):
            raise ValueError(
                "training requires cuda:0 and exactly one visible GPU"
            )
        prepared = args.prepared_dir.resolve()
        audit, data_path = _verify_prepared(prepared, data_condition)
        protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
        protocol.verify_immutable_inputs()
        training = protocol.payload["training"]
        if (
            int(training["micro_batch_size"]) != MICRO_BATCH
            or int(training["gradient_accumulation_steps"])
            != ACCUMULATION
            or int(training["epochs"]) != EPOCHS
            or float(
                protocol.payload["development"][
                    "selected_learning_rates"
                ]["M2_M3"]
            )
            != LEARNING_RATE
        ):
            raise ValueError("frozen Stage 2 settings differ from VISSUP plan")
        seed_everything(TRAIN_SEED)
        device = torch.device(args.device)
        model = run_spec["model_builder"](
            protocol,
            args.mapping_root,
            expected_dimensions,
            device=device,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            protocol.asset_path("tokenizer"),
            local_files_only=True,
        )
        dataset = Stage2CaptionDataset(
            data_path,
            tokenizer,
            model_group="M2",
            processor=model.processor,
            max_length=protocol.payload["training"][
                "max_sequence_length"
            ],
            image_token_count=protocol.payload["model"][
                "image_token_count"
            ],
        )
        if len(dataset) != TOTAL_TRAIN_ROWS:
            raise ValueError("dataset row count differs from frozen plan")
        parameters = [
            parameter for _, parameter in coordinate_parameters(model)
        ]
        initial_structure = model_structure_receipt(model)
        if initial_structure["coordinate_dimensions"] != expected_dimensions:
            raise ValueError("constructed coordinate dimensions differ")
        projection_receipt = (
            run_spec["projection_preflight"](
                args.condition, args.mapping_root
            )
            if run_spec["projection_preflight"] is not None
            else None
        )
        initial_frozen_hash = frozen_parameter_hash(model)
        initial_coordinates = coordinate_state(model)
        if any(
            torch.count_nonzero(value).item()
            for value in initial_coordinates.values()
        ):
            raise RuntimeError("VISSUP coordinates are not exact zero")

        model.train()
        model.vision_encoder.eval()
        if args.smoke:
            receipt = _smoke(
                model,
                dataset,
                parameters,
                device=device,
                condition=args.condition,
                mapping_root=args.mapping_root,
            )
            receipt.update(
                {
                    "candidate": run_spec["candidate"],
                    "round": run_spec["round"],
                    "coordinate_dimensions": expected_dimensions,
                    "data_path": str(data_path),
                    "data_sha256": sha256_file(data_path),
                    "data_condition": data_condition,
                    "prepared_audit_sha256": sha256_file(
                        prepared / "data_audit.json"
                    ),
                    "projection_preflight": projection_receipt,
                    "initial_frozen_parameter_sha256": initial_frozen_hash,
                    "elapsed_seconds": time.time() - started,
                    "peak_cuda_memory_bytes": int(
                        torch.cuda.max_memory_allocated()
                    ),
                }
            )
            write_json(output / "smoke_receipt.json", receipt)
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
            return receipt

        usable_micro_batches = len(dataset) // MICRO_BATCH
        if (
            len(dataset) % MICRO_BATCH
            or usable_micro_batches % ACCUMULATION
        ):
            raise ValueError("training data does not form accumulation windows")
        observed_total_steps = (
            EPOCHS * usable_micro_batches // ACCUMULATION
        )
        if observed_total_steps != TOTAL_STEPS:
            raise ValueError("optimizer step count differs from frozen plan")
        optimizer = _optimizer(parameters)
        optimizer.zero_grad(set_to_none=True)
        optimizer_step = 0
        observed_micro_batches = 0
        running_loss = 0.0
        epoch_receipts = []
        num_workers = int(training["dataloader"]["num_workers"])
        all_norms_finite = True
        for epoch_index in range(EPOCHS):
            permutation = permutation_for_epoch(
                len(dataset), TRAIN_SEED, epoch_index
            )
            loader = DataLoader(
                dataset,
                batch_size=MICRO_BATCH,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=num_workers,
                persistent_workers=num_workers > 0,
                pin_memory=True,
                prefetch_factor=(
                    training["dataloader"]["prefetch_factor"]
                    if num_workers > 0
                    else None
                ),
                collate_fn=stage2_collate,
            )
            epoch_loss = 0.0
            for micro_index, (
                input_ids,
                labels,
                pixels,
            ) in enumerate(loader):
                input_ids = input_ids.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                pixels = move_pixels(pixels, device)
                with torch.autocast(
                    device_type="cuda",
                    dtype=torch.bfloat16,
                    enabled=True,
                ):
                    result = model(
                        input_ids=input_ids,
                        labels=labels,
                        pixel_values=pixels,
                    )
                    loss = result.loss / ACCUMULATION
                if not torch.isfinite(loss):
                    raise FloatingPointError("training loss is NaN or Inf")
                loss.backward()
                micro_loss = float(loss.detach()) * ACCUMULATION
                epoch_loss += micro_loss
                running_loss += micro_loss
                observed_micro_batches += 1
                if (micro_index + 1) % ACCUMULATION == 0:
                    learning_rate = learning_rate_at(
                        optimizer_step,
                        TOTAL_STEPS,
                        LEARNING_RATE,
                    )
                    for group in optimizer.param_groups:
                        group["lr"] = learning_rate
                    norm = torch.nn.utils.clip_grad_norm_(
                        parameters, 1.0
                    )
                    if not torch.isfinite(norm):
                        all_norms_finite = False
                        raise FloatingPointError(
                            "training gradient norm is NaN or Inf"
                        )
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
            epoch_receipts.append(
                {
                    "epoch_index": epoch_index,
                    "epoch_seed": TRAIN_SEED + epoch_index,
                    "permutation_sha256": permutation_sha256(permutation),
                    "micro_batches": len(loader),
                    "mean_micro_batch_loss": epoch_loss / len(loader),
                }
            )
            print(
                f"condition={args.condition} root={args.mapping_root} "
                f"epoch={epoch_index + 1}/{EPOCHS} "
                f"optimizer_step={optimizer_step}/{TOTAL_STEPS} "
                f"mean_loss={epoch_loss / len(loader):.8f}",
                flush=True,
            )
        if optimizer_step != TOTAL_STEPS:
            raise RuntimeError("observed optimizer steps differ from plan")
        final_frozen_hash = frozen_parameter_hash(model)
        if final_frozen_hash != initial_frozen_hash:
            raise RuntimeError("one or more frozen base parameters changed")
        final_coordinates = coordinate_state(model)
        dimensions = {
            name: int(value.numel())
            for name, value in final_coordinates.items()
        }
        if dimensions != expected_dimensions:
            raise RuntimeError("final coordinate dimensions differ")
        if not any(
            torch.count_nonzero(value).item()
            for value in final_coordinates.values()
        ):
            raise RuntimeError("training left all coordinates at zero")
        coordinate_path = output / "coordinates.pt"
        _save_torch_atomic(
            coordinate_path,
            {
                "schema_version": 1,
                "candidate": run_spec["candidate"],
                "round": run_spec["round"],
                "condition": args.condition,
                "model_group": "M2",
                "mapping_root": args.mapping_root,
                "train_seed": TRAIN_SEED,
                "coordinates": final_coordinates,
            },
        )
        manifest = {
            "schema_version": 1,
            "status": "complete",
            "candidate": run_spec["candidate"],
            "round": run_spec["round"],
            "formal_stage2_confirmation_run": False,
            "condition": args.condition,
            "mapping_root": args.mapping_root,
            "data": {
                "path": str(data_path),
                "sha256": sha256_file(data_path),
                "rows": len(dataset),
                "condition": data_condition,
                "prepared_audit_path": str(
                    (prepared / "data_audit.json").resolve()
                ),
                "prepared_audit_sha256": sha256_file(
                    prepared / "data_audit.json"
                ),
            },
            "training": {
                "train_seed": TRAIN_SEED,
                "learning_rate": LEARNING_RATE,
                "epochs": EPOCHS,
                "micro_batch_size": MICRO_BATCH,
                "gradient_accumulation_steps": ACCUMULATION,
                "effective_batch_size": MICRO_BATCH * ACCUMULATION,
                "optimizer_steps_expected": TOTAL_STEPS,
                "optimizer_steps_observed": optimizer_step,
                "observed_micro_batches": observed_micro_batches,
                "mean_micro_batch_loss": running_loss
                / observed_micro_batches,
                "epoch_receipts": epoch_receipts,
                "all_losses_finite": True,
                "all_gradient_norms_finite": all_norms_finite,
                "automatic_hyperparameter_tuning": False,
                "checkpoint_selection": "final_fixed_schedule_state_only",
            },
            "model": {
                "initial_structure": initial_structure,
                "coordinate_dimensions": dimensions,
                "initial_frozen_parameter_sha256": initial_frozen_hash,
                "final_frozen_parameter_sha256": final_frozen_hash,
                "frozen_parameters_unchanged": True,
                "final_coordinate_state_sha256": tensor_state_sha256(
                    final_coordinates
                ),
                "projection_preflight": projection_receipt,
            },
            "coordinates": {
                "path": str(coordinate_path),
                "sha256": sha256_file(coordinate_path),
            },
            "runtime": {
                "seconds": time.time() - started,
                "python": sys.version.split()[0],
                "torch": torch.__version__,
                "cuda_runtime": torch.version.cuda,
                "cudnn": torch.backends.cudnn.version(),
                "visible_device_count": torch.cuda.device_count(),
                "visible_device_name": torch.cuda.get_device_name(0),
                "peak_cuda_memory_bytes": int(
                    torch.cuda.max_memory_allocated()
                ),
            },
            "final_confirmation_accessed": False,
        }
        write_json(output / "training_manifest.json", manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return manifest
    except BaseException as error:
        write_json(
            failure_path,
            {
                "schema_version": 1,
                "status": "failed",
                "candidate": run_spec["candidate"],
                "round": run_spec["round"],
                "condition": args.condition,
                "mapping_root": args.mapping_root,
                "mode": "smoke" if args.smoke else "full",
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
                "automatic_retry": False,
            },
        )
        raise


def main() -> None:
    train(parse_args())


if __name__ == "__main__":
    main()
