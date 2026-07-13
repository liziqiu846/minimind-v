#!/usr/bin/env python3
"""Evaluate deterministic target-token and per-example NLL for MiniMind-V."""

import argparse
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
from trainer.trainer_utils import init_vlm_model, vlm_collate_fn


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--weight", default="pretrain_vlm", help="Weight prefix in --save-dir")
    parser.add_argument("--save-dir", type=Path, default=REPO_ROOT / "out")
    parser.add_argument("--tokenizer-path", type=Path, default=REPO_ROOT / "model")
    parser.add_argument(
        "--vision-model-path",
        type=Path,
        default=REPO_ROOT / "model" / "siglip2-base-p32-256-ve",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--device", default="cuda:0" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--dtype", choices=("bfloat16", "float16", "float32"), default="bfloat16")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--max-samples", type=int, default=0, help="0 evaluates the full file")
    parser.add_argument("--max-seq-len", type=int, default=450)
    parser.add_argument("--hidden-size", type=int, default=768)
    parser.add_argument("--num-hidden-layers", type=int, default=8)
    parser.add_argument("--use-moe", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    config = VLMConfig(
        hidden_size=args.hidden_size,
        num_hidden_layers=args.num_hidden_layers,
        max_seq_len=args.max_seq_len,
        use_moe=args.use_moe,
    )
    model, tokenizer, processor = init_vlm_model(
        config,
        from_weight=args.weight,
        tokenizer_path=str(args.tokenizer_path),
        vision_model_path=str(args.vision_model_path),
        save_dir=str(args.save_dir),
        device=args.device,
        freeze_llm=2,
    )
    model.eval()

    dataset = VLMDataset(
        str(args.data_path),
        tokenizer,
        preprocess=processor,
        max_length=args.max_seq_len,
        image_special_token=config.image_special_token,
        image_token_len=config.image_token_len,
        augment=False,
    )
    if args.max_samples:
        dataset = Subset(dataset, range(min(args.max_samples, len(dataset))))
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory="cuda" in args.device,
        collate_fn=vlm_collate_fn,
    )

    amp_dtype = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }[args.dtype]
    use_amp = "cuda" in args.device and args.dtype != "float32"
    total_nll = 0.0
    total_target_tokens = 0
    total_examples = 0
    total_example_nll = 0.0

    with torch.inference_mode():
        for input_ids, labels, pixel_values in tqdm(loader, desc="Evaluating"):
            input_ids = input_ids.to(args.device, non_blocking=True)
            labels = labels.to(args.device, non_blocking=True)
            if isinstance(pixel_values, dict):
                pixel_values = {
                    key: value.to(args.device, non_blocking=True)
                    for key, value in pixel_values.items()
                }
            else:
                pixel_values = pixel_values.to(args.device, non_blocking=True)

            with torch.autocast(
                device_type="cuda" if "cuda" in args.device else "cpu",
                dtype=amp_dtype,
                enabled=use_amp,
            ):
                output = model(input_ids=input_ids, pixel_values=pixel_values)
            shift_logits = output.logits[:, :-1, :].float()
            shift_labels = labels[:, 1:]
            token_nll = F.cross_entropy(
                shift_logits.transpose(1, 2),
                shift_labels,
                ignore_index=-100,
                reduction="none",
            )
            mask = shift_labels.ne(-100)
            example_nll = (token_nll * mask).sum(dim=1)
            total_nll += example_nll.sum().item()
            total_example_nll += example_nll.sum().item()
            total_target_tokens += mask.sum().item()
            total_examples += input_ids.size(0)

    mean_token_nll = total_nll / max(total_target_tokens, 1)
    metrics = {
        "data_path": str(args.data_path.resolve()),
        "weight": args.weight,
        "examples": total_examples,
        "target_tokens": total_target_tokens,
        "mean_target_tokens_per_example": total_target_tokens / max(total_examples, 1),
        "mean_token_nll": mean_token_nll,
        "token_perplexity": math.exp(min(mean_token_nll, 50.0)),
        "mean_sequence_nll": total_example_nll / max(total_examples, 1),
    }
    rendered = json.dumps(metrics, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
