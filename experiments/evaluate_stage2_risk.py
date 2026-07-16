#!/usr/bin/env python3
"""Evaluate equal-image-weight smoothed Stage 2 risk in bits."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset
from transformers import AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.stage2_model import build_stage2_model, tensor_state_sha256
from experiments.stage2_protocol import (
    DEFAULT_DRAFT,
    Stage2Protocol,
    sha256_file,
    write_json_atomic,
)
from model.global_subspace_lora import load_coordinate_state


def move_pixels(pixel_values, device):
    if pixel_values is None:
        return None
    if isinstance(pixel_values, dict):
        return {name: value.to(device, non_blocking=True) for name, value in pixel_values.items()}
    return pixel_values.to(device, non_blocking=True)


def sample_risk_bits(
    logits: torch.Tensor,
    labels: torch.Tensor,
    alpha: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    shifted_logits = logits[:, :-1].to(torch.float32)
    shifted_labels = labels[:, 1:]
    mask = shifted_labels.ne(-100)
    counts = mask.sum(dim=1)
    if torch.any(counts == 0):
        raise ValueError("each Stage 2 sample must have target tokens")
    safe = shifted_labels.masked_fill(~mask, 0)
    target_log_probability = F.log_softmax(shifted_logits, dim=-1).gather(
        -1, safe.unsqueeze(-1)
    ).squeeze(-1)
    log_smoothed = torch.logaddexp(
        target_log_probability + math.log1p(-alpha),
        torch.full_like(target_log_probability, math.log(alpha) - math.log(logits.shape[-1])),
    )
    token_bits = (-log_smoothed / math.log(2)).masked_fill(~mask, 0)
    risks = token_bits.sum(dim=1) / counts
    return risks, counts


def image_hashes(dataset: Stage2CaptionDataset) -> list[str]:
    values = []
    for index in range(len(dataset)):
        row = dataset.dataset[index]
        if "image_sha256" in row and row["image_sha256"]:
            values.append(row["image_sha256"])
        else:
            image_bytes = row["image_bytes"]
            if isinstance(image_bytes, list):
                if len(image_bytes) != 1:
                    raise ValueError("Stage 2 diagnostics require one image per sample")
                image_bytes = image_bytes[0]
            values.append(hashlib.sha256(image_bytes).hexdigest())
    if len(values) != len(set(values)):
        raise ValueError("risk dataset contains duplicate exact images")
    return values


def pair_swap_permutation(hashes: list[str]) -> tuple[int, ...]:
    if len(hashes) % 2 or len(hashes) < 2:
        raise ValueError("pair swap requires a positive even number of samples")
    order = sorted(range(len(hashes)), key=lambda index: bytes.fromhex(hashes[index]))
    permutation = list(range(len(hashes)))
    for left, right in zip(order[::2], order[1::2], strict=True):
        permutation[left] = right
        permutation[right] = left
    return tuple(permutation)


def permutation_sha256(permutation: tuple[int, ...]) -> str:
    digest = hashlib.sha256(b"stage2-sha256-pair-swap-v1\0")
    for value in permutation:
        digest.update(value.to_bytes(8, "little"))
    return digest.hexdigest()


class PairedImageDataset(Dataset):
    def __init__(self, dataset: Dataset, permutation: tuple[int, ...]) -> None:
        self.dataset = dataset
        self.permutation = permutation

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index: int):
        input_ids, labels, _ = self.dataset[index]
        _, _, donor_pixels = self.dataset[self.permutation[index]]
        return input_ids, labels, donor_pixels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--model-group", choices=("M0", "M1", "M2", "M3"), required=True)
    parser.add_argument("--mapping-root", type=int)
    parser.add_argument("--coordinates", type=Path, required=True)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--data-role", choices=("train", "validation"), required=True)
    parser.add_argument("--model-kind", choices=("unquantized", "decoded_quantized"), required=True)
    parser.add_argument("--image-condition", choices=("correct", "paired_shuffled", "none"), default="correct")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--num-workers", type=int)
    return parser.parse_args()


@torch.inference_mode()
def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"risk output already exists: {args.output}")
    protocol = Stage2Protocol.load(args.protocol, require_frozen=args.formal)
    protocol.verify_immutable_inputs()
    if args.formal:
        protocol.require_frozen()
        if args.max_samples:
            raise ValueError("formal risk cannot limit samples")
        protocol.verify_confirmation_data(args.data, args.data_role)
    if args.model_kind == "decoded_quantized" and args.adapter is None:
        raise ValueError("decoded quantized risk requires the transmitted adapter")
    if args.image_condition != "correct" and args.model_group == "M0":
        raise ValueError("M0 has no visual-condition diagnostic")
    if args.image_condition != "correct" and args.data_role != "validation":
        raise ValueError("visual diagnostics are validation-only")

    started = time.time()
    device = torch.device(args.device)
    model = build_stage2_model(args.model_group, protocol, args.mapping_root, device=device)
    stored = torch.load(args.coordinates, map_location="cpu", weights_only=True)
    load_coordinate_state(model, stored.get("coordinates", stored))
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )
    base_dataset = Stage2CaptionDataset(
        args.data,
        tokenizer,
        model_group=args.model_group,
        processor=getattr(model, "processor", None),
        max_length=protocol.payload["training"]["max_sequence_length"],
        image_token_count=protocol.payload["model"]["image_token_count"],
    )
    hashes = image_hashes(base_dataset)
    if args.max_samples:
        base_dataset = Subset(base_dataset, range(args.max_samples))
        hashes = hashes[:args.max_samples]
    permutation = None
    dataset: Dataset = base_dataset
    if args.image_condition == "paired_shuffled":
        permutation = pair_swap_permutation(hashes)
        dataset = PairedImageDataset(base_dataset, permutation)

    evaluation = protocol.payload["evaluation"]
    num_workers = evaluation["num_workers"] if args.num_workers is None else args.num_workers
    loader = DataLoader(
        dataset,
        batch_size=evaluation["batch_size"],
        shuffle=False,
        drop_last=False,
        num_workers=num_workers,
        persistent_workers=num_workers > 0,
        pin_memory=device.type == "cuda",
        prefetch_factor=evaluation["prefetch_factor"] if num_workers > 0 else None,
        collate_fn=stage2_collate,
    )
    sums = torch.zeros((), dtype=torch.float64)
    sample_values = []
    token_counts = []
    alpha = float(evaluation["alpha"])
    for input_ids, labels, pixels in loader:
        input_ids = input_ids.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        pixels = None if args.image_condition == "none" else move_pixels(pixels, device)
        with torch.autocast(
            device_type="cuda", dtype=torch.bfloat16, enabled=device.type == "cuda"
        ):
            logits = model(input_ids=input_ids, pixel_values=pixels).logits
        risks, counts = sample_risk_bits(logits, labels, alpha)
        values = risks.to(torch.float64).cpu()
        sums += values.sum()
        sample_values.extend(values.tolist())
        token_counts.extend(counts.cpu().tolist())
    sample_count = len(sample_values)
    if sample_count != len(dataset):
        raise RuntimeError("risk evaluation did not consume every sample")
    result = {
        "schema_version": 1,
        "model_group": args.model_group,
        "mapping_root": args.mapping_root,
        "model_kind": args.model_kind,
        "image_condition": args.image_condition,
        "protocol": protocol.reference(),
        "coordinates": {
            "path": str(args.coordinates.resolve()),
            "sha256": sha256_file(args.coordinates),
        },
        "adapter": None if args.adapter is None else {
            "path": str(args.adapter.resolve()),
            "sha256": sha256_file(args.adapter),
            "complexity_bits": args.adapter.stat().st_size * 8,
        },
        "data": {
            "path": str(args.data.resolve()),
            "sha256": sha256_file(args.data),
            "role": args.data_role,
            "sample_count": sample_count,
        },
        "risk": {
            "alpha": alpha,
            "vocab_size": evaluation["vocab_size"],
            "units": "bits",
            "aggregation": "mean target tokens inside sample, then equal mean of images",
            "mean_sample_risk_bits": float(sums.item() / sample_count),
            "target_token_count": int(sum(token_counts)),
            "mean_target_tokens_per_sample": float(sum(token_counts) / sample_count),
            "sample_risk_bits": sample_values,
            "sample_target_token_counts": token_counts,
            "sample_image_sha256": hashes,
        },
        "model_state_sha256": tensor_state_sha256(model.state_dict()),
        "evaluation": {
            "batch_size": evaluation["batch_size"],
            "num_workers": num_workers,
            "shuffle": False,
            "drop_last": False,
            "forward_dtype": evaluation["model_forward_dtype"],
            "elapsed_seconds": time.time() - started,
        },
    }
    if permutation is not None:
        result["pair_swap"] = {
            "rule": "sort raw SHA256 ascending and swap adjacent images",
            "permutation": list(permutation),
            "permutation_sha256": permutation_sha256(permutation),
        }
    write_json_atomic(args.output, result)
    printable = dict(result)
    printable["risk"] = dict(result["risk"])
    printable["risk"].pop("sample_risk_bits")
    printable["risk"].pop("sample_target_token_counts")
    printable["risk"].pop("sample_image_sha256")
    print(json.dumps(printable, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
