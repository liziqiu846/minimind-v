#!/usr/bin/env python3
"""Train one preregistered model with plain SGD and pure group diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase3_private_vs_shared_v1.adapter_runtime import (
    build_candidate_model,
)
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

from .codec import encode_and_verify
from .common import (
    PROTOCOL_PATH,
    load_protocol,
    sha256_file,
    write_json_atomic,
)
from .configs import load_candidate
from .diagnosis import diagnose_replacement, fixed_index

STAGE2_PROTOCOL = Path(__file__).resolve().parents[1] / "stage2_protocol_v2.json"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=Path(__file__).resolve().parents[2]
    ).stdout.strip()


def _save_torch_atomic(path: Path, payload: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def _concat_micro_batches(micro_batches, device):
    ids = torch.cat([batch[0] for batch in micro_batches]).to(device)
    labels = torch.cat([batch[1] for batch in micro_batches]).to(device)
    first = micro_batches[0][2]
    if isinstance(first, Mapping):
        pixels = {
            key: torch.cat([batch[2][key] for batch in micro_batches]).to(device)
            for key in first
        }
    elif first is None:
        pixels = None
    else:
        pixels = torch.cat([batch[2] for batch in micro_batches]).to(device)
    return ids, labels, pixels


def _ghost_item(dataset, index: int, device):
    ids, labels, pixels = dataset[index]
    if isinstance(pixels, Mapping):
        pixels = {key: value.to(device) for key, value in pixels.items()}
    elif pixels is not None:
        pixels = pixels.to(device)
    return ids.to(device), labels.to(device), pixels


def train(
    config_id: str,
    *,
    data_audit_path: Path,
    output_root: Path,
    device_name: str,
    require_clean: bool = True,
) -> dict[str, Any]:
    protocol = load_protocol()
    config = load_candidate(config_id)
    audit = json.loads(data_audit_path.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise RuntimeError("formal training is gated by a PASS data audit")
    if audit.get("final_independent_confirmation_accessed") is not False:
        raise RuntimeError("data audit reports forbidden confirmation access")
    if require_clean and _git("status", "--porcelain"):
        raise RuntimeError("formal training requires a clean worktree")
    binding = {
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "data_audit_sha256": sha256_file(data_audit_path),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("branch", "--show-current"),
    }
    output = output_root.resolve() / config_id
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "status.json"
    result_path = output / "training_manifest.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))
    started = time.time()
    write_json_atomic(status_path, {**binding, "config_id": config_id, "status": "running"})
    try:
        stage2 = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
        device = torch.device(device_name)
        if device.type != "cuda" or not torch.cuda.is_available():
            raise RuntimeError("formal training requires CUDA")
        expected_cublas = protocol["training"]["determinism"][
            "cublas_workspace_config"
        ]
        if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != expected_cublas:
            raise RuntimeError(
                f"formal training requires CUBLAS_WORKSPACE_CONFIG={expected_cublas}"
            )
        torch.use_deterministic_algorithms(True)
        seed_everything(protocol["training"]["data_order_seed"])
        model = build_candidate_model(config, stage2, device=device)
        model.train()
        model.vision_encoder.eval()
        tokenizer = AutoTokenizer.from_pretrained(
            stage2.asset_path("tokenizer"), local_files_only=True
        )
        train_path = Path(audit["artifacts"]["train"]["path"])
        ghost_path = Path(audit["artifacts"]["ghost_pool"]["path"])
        if (
            sha256_file(train_path) != audit["artifacts"]["train"]["sha256"]
            or sha256_file(ghost_path) != audit["artifacts"]["ghost_pool"]["sha256"]
        ):
            raise ValueError("audited train or ghost artifact changed")
        legacy = "M2" if config["structure"] == "P" else "M3"
        dataset_args = dict(
            tokenizer=tokenizer,
            model_group=legacy,
            processor=model.processor,
            max_length=protocol["training"]["max_sequence_length"],
            image_token_count=protocol["training"]["image_token_count"],
        )
        dataset = Stage2CaptionDataset(train_path, **dataset_args)
        ghost_pool = Stage2CaptionDataset(ghost_path, **dataset_args)
        if len(dataset) != 10000 or not len(ghost_pool):
            raise ValueError("audited data sample count changed")
        parameters = list(model.stage2_coordinates.parameters())
        if sum(parameter.numel() for parameter in parameters) != config["budget"]:
            raise ValueError("trainable coordinate count differs from budget")
        optimizer = torch.optim.SGD(
            parameters,
            lr=protocol["training"]["learning_rate"],
            momentum=0.0,
            dampening=0.0,
            weight_decay=0.0,
            nesterov=False,
        )
        if optimizer.state:
            raise RuntimeError("plain SGD must begin with empty state")
        initial_coordinates = tensor_state_sha256(
            model.stage2_coordinates.state_dict()
        )
        initial_frozen = frozen_parameter_hash(model)
        accumulation = protocol["training"]["gradient_accumulation_steps"]
        micro_batch = protocol["training"]["micro_batch_size"]
        total_steps = protocol["training"]["total_optimizer_steps"]
        diagnosis_steps = set(protocol["diagnosis"]["optimizer_steps"])
        optimizer_step = 0
        observed_micro_batches = 0
        total_loss = 0.0
        d_i = 0.0
        diagnosis_rows = []
        epoch_receipts = []
        optimizer.zero_grad(set_to_none=True)
        for epoch in range(protocol["training"]["epochs"]):
            permutation = permutation_for_epoch(
                len(dataset), protocol["training"]["data_order_seed"], epoch
            )
            loader = DataLoader(
                dataset,
                batch_size=micro_batch,
                sampler=permutation.tolist(),
                drop_last=True,
                num_workers=0,
                pin_memory=True,
                collate_fn=stage2_collate,
            )
            window = []
            epoch_loss = 0.0
            for micro in loader:
                window.append(micro)
                if len(window) != accumulation:
                    continue
                effective = _concat_micro_batches(window, device)
                lr = learning_rate_at(
                    optimizer_step, total_steps, protocol["training"]["learning_rate"]
                )
                optimizer.param_groups[0]["lr"] = lr
                if optimizer_step in diagnosis_steps:
                    position = fixed_index(
                        config["seed"], optimizer_step, "batch-position",
                        effective[0].shape[0]
                    )
                    ghost_index = fixed_index(
                        config["seed"], optimizer_step, "ghost", len(ghost_pool)
                    )
                    diagnostic = diagnose_replacement(
                        model, parameters, effective,
                        _ghost_item(ghost_pool, ghost_index, device),
                        selected_position=position, accumulation=accumulation,
                    )
                    contribution = lr * lr * diagnostic[
                        "squared_l2_gradient_difference"
                    ]
                    d_i += contribution
                    diagnosis_rows.append({
                        "optimizer_step": optimizer_step,
                        "learning_rate": lr,
                        "selected_effective_batch_position": position,
                        "selected_train_dataset_index": int(
                            permutation[
                                (optimizer_step % (len(dataset) // 16)) * 16 + position
                            ]
                        ),
                        "ghost_pool_index": ghost_index,
                        **diagnostic,
                        "D_I_contribution": contribution,
                    })
                optimizer.zero_grad(set_to_none=True)
                micro_losses = []
                for start in range(0, effective[0].shape[0], micro_batch):
                    end = start + micro_batch
                    pixels = effective[2]
                    pixels_chunk = (
                        {key: value[start:end] for key, value in pixels.items()}
                        if isinstance(pixels, Mapping)
                        else pixels[start:end]
                    )
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        loss = model(
                            input_ids=effective[0][start:end],
                            labels=effective[1][start:end],
                            pixel_values=pixels_chunk,
                        ).loss
                    if not torch.isfinite(loss):
                        raise FloatingPointError("training loss is non-finite")
                    (loss / accumulation).backward()
                    micro_losses.append(float(loss.detach()))
                optimizer.step()
                value = sum(micro_losses)
                total_loss += value
                epoch_loss += value
                observed_micro_batches += accumulation
                optimizer_step += 1
                window = []
            epoch_receipts.append({
                "epoch": epoch,
                "permutation_sha256": permutation_sha256(permutation),
                "micro_batches": len(loader),
                "mean_loss": epoch_loss / len(loader),
            })
        if optimizer_step != total_steps or len(diagnosis_rows) != len(diagnosis_steps):
            raise RuntimeError("actual steps or diagnostic count differs from protocol")
        if frozen_parameter_hash(model) != initial_frozen:
            raise RuntimeError("frozen parameters changed")
        coordinates = {
            name: value.detach().cpu()
            for name, value in model.stage2_coordinates.state_dict().items()
        }
        archive, encoding = encode_and_verify(
            coordinates, config["structure"], config["seed"]
        )
        mms_path = output / "adapter.mms2"
        mms_path.write_bytes(archive)
        checkpoint_path = output / "checkpoint.pt"
        _save_torch_atomic(checkpoint_path, {
            **binding, "config": config, "coordinates": coordinates,
            "optimizer": optimizer.state_dict(), "optimizer_step": optimizer_step,
        })
        diagnosis_path = output / "diagnosis.json"
        write_json_atomic(diagnosis_path, {
            **binding, "config_id": config_id, "D_I": d_i,
            "claim_label": protocol["diagnosis"]["claim_label"],
            "diagnosis_step_count": len(diagnosis_rows), "steps": diagnosis_rows,
        })
        result = {
            **binding,
            "schema_version": 1,
            "status": "complete",
            "config": config,
            "structure": config["structure"],
            "budget": config["budget"],
            "seed": config["seed"],
            "empirical_risk": total_loss / observed_micro_batches,
            "empirical_risk_unit": "mean_training_cross_entropy",
            "actual_mms2_bits": len(archive) * 8,
            "D_I": d_i,
            "D_I_claim_label": protocol["diagnosis"]["claim_label"],
            "diagnosis_step_count": len(diagnosis_rows),
            "actual_optimizer_steps": optimizer_step,
            "optimizer": protocol["training"]["optimizer"],
            "initial_coordinate_state_sha256": initial_coordinates,
            "coordinate_state_sha256": tensor_state_sha256(coordinates),
            "epoch_receipts": epoch_receipts,
            "checkpoint": {"path": str(checkpoint_path), "sha256": sha256_file(checkpoint_path)},
            "MMS2": {"path": str(mms_path), "sha256": sha256_file(mms_path), **encoding},
            "manifest": {"path": str(result_path)},
            "diagnosis": {"path": str(diagnosis_path), "sha256": sha256_file(diagnosis_path)},
            "runtime_seconds": time.time() - started,
        }
        write_json_atomic(result_path, result)
        write_json_atomic(status_path, {
            **binding, "config_id": config_id, "status": "complete",
            "manifest_sha256": sha256_file(result_path),
        })
        return result
    except BaseException as error:
        write_json_atomic(status_path, {
            **binding, "config_id": config_id, "status": "failed",
            "error_type": type(error).__name__, "error": str(error),
        })
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--data-audit", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--allow-dirty-test-only", action="store_true")
    args = parser.parse_args()
    result = train(
        args.config_id, data_audit_path=args.data_audit,
        output_root=args.output_root, device_name=args.device,
        require_clean=not args.allow_dirty_test_only,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
