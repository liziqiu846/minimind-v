#!/usr/bin/env python3
"""Evaluate smoothed conditional token NLL, averaging samples equally."""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.lm_dataset import VLMDataset
from model.model_vlm import VLMConfig
from model.subspace_projector import fixed_state_sha256
from trainer.trainer_utils import init_vlm_model, vlm_collate_fn


DEFAULT_ALPHA_GRID = (0.0001, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_asset_fingerprints(tokenizer_path: Path, vision_model_path: Path) -> dict:
    """Identify the fixed tokenizer, processor, and vision encoder used for risk."""
    tokenizer_path = tokenizer_path.resolve()
    vision_model_path = vision_model_path.resolve()
    return {
        "tokenizer": {
            "path": str(tokenizer_path),
            "files": {
                name: sha256_file(tokenizer_path / name)
                for name in ("tokenizer.json", "tokenizer_config.json")
            },
        },
        "vision_model": {
            "path": str(vision_model_path),
            "files": {
                name: sha256_file(vision_model_path / name)
                for name in (
                    "config.json",
                    "model.safetensors",
                    "preprocessor_config.json",
                )
            },
        },
    }


def apply_image_condition(pixel_values, condition: str):
    """Keep, mismatch, or remove the images for a diagnostic control."""
    if condition == "correct":
        return pixel_values
    if condition == "none":
        return None

    sample = next(iter(pixel_values.values())) if isinstance(pixel_values, dict) else pixel_values
    if sample.shape[0] < 2:
        raise ValueError("shuffled evaluation needs batches of at least two samples")
    order = torch.roll(torch.arange(sample.shape[0]), shifts=1)
    if isinstance(pixel_values, dict):
        return {key: value[order] for key, value in pixel_values.items()}
    return pixel_values[order]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--model-kind",
        choices=("diagnostic_unquantized", "decoded_quantized"),
        required=True,
    )
    parser.add_argument("--alphas", nargs="+", type=float, default=DEFAULT_ALPHA_GRID)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument(
        "--image-condition",
        choices=("correct", "shuffled", "none"),
        default="correct",
    )
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument(
        "--dtype", choices=("bfloat16", "float16", "float32"), default="bfloat16"
    )
    parser.add_argument("--tokenizer-path", type=Path, default=REPO_ROOT / "model")
    parser.add_argument(
        "--vision-model-path",
        type=Path,
        default=REPO_ROOT / "model/siglip2-base-p32-256-ve",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve_run(args: argparse.Namespace) -> tuple[dict, Path]:
    manifest = json.loads((args.run_dir / "manifest.json").read_text())
    run_id = manifest["run_id"]
    hidden_size = manifest["model"]["hidden_size"]
    checkpoint = args.checkpoint or (
        args.run_dir / "weights" / f"{run_id}_{hidden_size}.pth"
    )
    if args.model_kind == "decoded_quantized" and args.checkpoint is None:
        raise ValueError("decoded_quantized evaluation requires --checkpoint")
    return manifest, checkpoint


def load_model(args: argparse.Namespace, manifest: dict, checkpoint: Path):
    projector = manifest["model"].get("projector", {"type": "standard"})
    config = VLMConfig(
        hidden_size=manifest["model"]["hidden_size"],
        num_hidden_layers=manifest["model"]["num_hidden_layers"],
        max_seq_len=manifest["training"]["max_seq_len"],
        projector_type=projector["type"],
        subspace_dim=projector.get("subspace_dim", 1024),
        subspace_seed=projector.get("subspace_seed", 42),
        subspace_train_norm=projector.get("train_norm", False),
    )
    model, tokenizer, processor = init_vlm_model(
        config,
        from_weight="none",
        tokenizer_path=str(args.tokenizer_path),
        vision_model_path=str(args.vision_model_path),
        device=args.device,
        freeze_llm=2,
    )
    if projector["type"] == "subspace":
        actual_hash = fixed_state_sha256(model.vision_proj)
        if actual_hash != projector["fixed_state_sha256"]:
            raise ValueError("subspace projector does not match the recorded fixed state")
    state_dict = torch.load(checkpoint, map_location="cpu", weights_only=True)
    incompatible = model.load_state_dict(state_dict, strict=False)
    bad_missing = [
        key for key in incompatible.missing_keys if not key.startswith("vision_encoder.")
    ]
    if bad_missing or incompatible.unexpected_keys:
        raise ValueError("checkpoint does not match the recorded model architecture")
    model.eval()
    return model, tokenizer, processor, config


def build_loader(args, tokenizer, processor, config):
    dataset = VLMDataset(
        str(args.data_path),
        tokenizer,
        preprocess=processor,
        max_length=config.max_seq_len,
        image_special_token=config.image_special_token,
        image_token_len=config.image_token_len,
        augment=False,
    )
    if args.max_samples:
        dataset = Subset(dataset, range(min(args.max_samples, len(dataset))))
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=args.device.startswith("cuda"),
        collate_fn=vlm_collate_fn,
    )


def smoothed_risk_grid_bits(logits, labels, alphas, ignore_index=-100):
    logits = logits[:, :-1].float()
    labels = labels[:, 1:]
    mask = labels.ne(ignore_index)
    counts = mask.sum(dim=1)
    if torch.any(counts == 0):
        raise ValueError("every sample needs at least one target token")
    safe_labels = labels.masked_fill(~mask, 0)
    target_log_p = F.log_softmax(logits, dim=-1).gather(
        -1, safe_labels.unsqueeze(-1)
    ).squeeze(-1)
    alpha = torch.as_tensor(alphas, device=logits.device, dtype=target_log_p.dtype)
    smoothed_log_p = torch.logaddexp(
        target_log_p.unsqueeze(0) + torch.log1p(-alpha)[:, None, None],
        (torch.log(alpha) - math.log(logits.shape[-1]))[:, None, None],
    )
    token_bits = (-smoothed_log_p / math.log(2)).masked_fill(~mask.unsqueeze(0), 0)
    risks = token_bits.sum(dim=2) / counts.unsqueeze(0)
    return risks.detach(), counts.detach()


def smoothed_autoregressive_risk_bits(logits, labels, alpha, ignore_index=-100):
    risks, counts = smoothed_risk_grid_bits(logits, labels, [alpha], ignore_index)
    return risks[0], counts


@torch.inference_mode()
def evaluate(model, loader, args):
    sums = torch.zeros(len(args.alphas), dtype=torch.float64)
    sample_count = target_token_count = vocab_size = 0
    amp_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16}.get(
        args.dtype, torch.float32
    )
    use_amp = args.device.startswith("cuda") and args.dtype != "float32"

    for input_ids, labels, pixels in tqdm(loader, desc="Evaluating"):
        input_ids = input_ids.to(args.device)
        labels = labels.to(args.device)
        pixels = apply_image_condition(pixels, args.image_condition)
        if pixels is not None:
            pixels = (
                {key: value.to(args.device) for key, value in pixels.items()}
                if isinstance(pixels, dict)
                else pixels.to(args.device)
            )
        with torch.autocast("cuda", dtype=amp_dtype, enabled=use_amp):
            logits = model(input_ids=input_ids, pixel_values=pixels).logits
        risks, counts = smoothed_risk_grid_bits(logits, labels, args.alphas)
        sums += risks.double().sum(dim=1).cpu()
        sample_count += risks.shape[1]
        target_token_count += counts.sum().item()
        vocab_size = logits.shape[-1]

    return {
        "sample_count": sample_count,
        "target_token_count": target_token_count,
        "mean_target_tokens_per_sample": target_token_count / sample_count,
        "vocab_size": vocab_size,
        "aggregation": "mean_tokens_within_sample_then_mean_samples",
        "risks": [
            {"alpha": alpha, "mean_sample_risk_bits": total / sample_count}
            for alpha, total in zip(args.alphas, sums.tolist(), strict=True)
        ],
    }


def main():
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output already exists: {args.output}")
    manifest, checkpoint = resolve_run(args)
    checkpoint_sha256 = sha256_file(checkpoint)
    data_sha256 = sha256_file(args.data_path)
    model, tokenizer, processor, config = load_model(args, manifest, checkpoint)
    loader = build_loader(args, tokenizer, processor, config)
    summary = evaluate(model, loader, args)
    result = {
        "run_id": manifest["run_id"],
        "model_kind": args.model_kind,
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": checkpoint_sha256,
        "data_path": str(args.data_path.resolve()),
        "data_sha256": data_sha256,
        "image_condition": args.image_condition,
        "model_assets": model_asset_fingerprints(
            args.tokenizer_path, args.vision_model_path
        ),
        "alpha_grid": list(args.alphas),
        "alpha_choice_bits": math.ceil(math.log2(len(args.alphas))),
        **summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
