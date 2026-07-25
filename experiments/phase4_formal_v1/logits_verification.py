"""Fixed-input model reload and exact-logits verification."""

from __future__ import annotations

import gc
import hashlib
from pathlib import Path
from typing import Any, Mapping

import torch
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase4_m4_v1.m4_model import (
    build_m4_model,
    load_m4_model_from_archive,
)
from experiments.phase4_m4_v1.train_m4 import _stage2_protocol
from experiments.stage2_model import tensor_state_sha256
from model.hybrid_subspace_lora import load_m4_coordinate_state
from trainer.train_stage2 import move_pixels, seed_everything


FIXED_SAMPLE_INDEX = 0
FIXED_LOGITS_TO_KEEP = 16


def _tensor_sha256(value: torch.Tensor) -> str:
    tensor = value.detach().cpu().contiguous()
    return hashlib.sha256(tensor.view(torch.uint8).numpy().tobytes()).hexdigest()


def _fixed_input(
    config: Mapping[str, Any],
    artifact_root: Path,
    processor: Any,
    device: torch.device,
) -> tuple[torch.Tensor, Any, dict[str, Any]]:
    protocol = _stage2_protocol(config)
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )
    dataset = Stage2CaptionDataset(
        artifact_root
        / "dataset/stage2_confirm_v2_seed2028/train.parquet",
        tokenizer,
        model_group="M3",
        processor=processor,
        max_length=protocol.payload["training"]["max_sequence_length"],
        image_token_count=protocol.payload["model"]["image_token_count"],
    )
    input_ids, _, pixels = stage2_collate([dataset[FIXED_SAMPLE_INDEX]])
    input_ids = input_ids.to(device)
    pixels = move_pixels(pixels, device)
    pixel_receipt = {
        key: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "sha256": _tensor_sha256(value),
        }
        for key, value in pixels.items()
    }
    return input_ids, pixels, {
        "source": "frozen_stage2_training_data",
        "sample_index": FIXED_SAMPLE_INDEX,
        "input_ids_shape": list(input_ids.shape),
        "input_ids_sha256": _tensor_sha256(input_ids),
        "pixel_tensors": pixel_receipt,
        "logits_to_keep": FIXED_LOGITS_TO_KEEP,
    }


def _forward(
    model: torch.nn.Module,
    input_ids: torch.Tensor,
    pixels: Any,
) -> torch.Tensor:
    model.eval()
    with torch.inference_mode():
        output = model(
            input_ids=input_ids,
            pixel_values=pixels,
            logits_to_keep=FIXED_LOGITS_TO_KEEP,
        )
    logits = output.logits.detach().cpu().float().contiguous()
    if not torch.isfinite(logits).all():
        raise FloatingPointError("fixed-input M4 logits are non-finite")
    return logits


def _release_cuda_memory() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def verify_fixed_input_logits(
    config: Mapping[str, Any],
    artifact_root: Path,
    archive: bytes,
    reference_coordinates: Mapping[str, torch.Tensor],
    conditional_coordinates: Mapping[str, torch.Tensor],
    *,
    device: str = "cuda:0",
) -> dict[str, Any]:
    """Compare pre-codec, conditional-decoded, and MMS2-reloaded logits."""

    seed_everything(int(config["training"]["train_seed"]))
    selected_device = torch.device(device)
    reference_model = build_m4_model(
        config,
        device=selected_device,
        dtype=torch.float32,
        verify_assets=True,
    )
    input_ids, pixels, input_receipt = _fixed_input(
        config,
        artifact_root,
        reference_model.processor,
        selected_device,
    )
    load_m4_coordinate_state(reference_model, reference_coordinates)
    reference_logits = _forward(reference_model, input_ids, pixels)
    load_m4_coordinate_state(reference_model, conditional_coordinates)
    conditional_logits = _forward(reference_model, input_ids, pixels)
    conditional_exact = torch.equal(reference_logits, conditional_logits)
    del reference_model
    _release_cuda_memory()

    archive_model, archive_metadata = load_m4_model_from_archive(
        archive,
        device=selected_device,
        dtype=torch.float32,
        verify_assets=True,
    )
    archive_logits = _forward(archive_model, input_ids, pixels)
    archive_exact = torch.equal(reference_logits, archive_logits)
    del archive_model
    _release_cuda_memory()
    if not conditional_exact or not archive_exact:
        raise RuntimeError("fixed-input logits changed across codec reload")
    return {
        "schema_version": 1,
        "status": "passed",
        "config_id": config["config_id"],
        "fixed_input": input_receipt,
        "reference_coordinate_state_sha256": tensor_state_sha256(
            reference_coordinates
        ),
        "conditional_coordinate_state_sha256": tensor_state_sha256(
            conditional_coordinates
        ),
        "logits_shape": list(reference_logits.shape),
        "reference_logits_sha256": _tensor_sha256(reference_logits),
        "conditional_logits_sha256": _tensor_sha256(conditional_logits),
        "archive_logits_sha256": _tensor_sha256(archive_logits),
        "conditional_logits_exact": conditional_exact,
        "archive_logits_exact": archive_exact,
        "archive_config_id": archive_metadata["config_id"],
        "all_logits_exact": True,
    }
