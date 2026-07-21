"""Teacher-forced caption scorer with exact causal next-token alignment."""

from __future__ import annotations

import math
from typing import Any

import torch

from experiments.phase3.brier_metrics import shifted_valid_positions, token_brier


def token_nll_bits(logits: torch.Tensor, labels: torch.Tensor) -> list[torch.Tensor]:
    shifted_logits, _, valid_mask, safe_labels, _ = shifted_valid_positions(logits, labels)
    log_probs = torch.log_softmax(shifted_logits, dim=-1)
    target = log_probs.gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)
    return [(-target[index][valid_mask[index]] / math.log(2)).cpu() for index in range(logits.shape[0])]


def smoothed_nll_bits(logits: torch.Tensor, labels: torch.Tensor, alpha: float = 0.5):
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    shifted_logits, _, valid_mask, safe_labels, counts = shifted_valid_positions(logits, labels)
    log_probs = torch.log_softmax(shifted_logits, dim=-1)
    target = log_probs.gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)
    log_smoothed = torch.logaddexp(
        target + math.log1p(-alpha),
        torch.full_like(target, math.log(alpha) - math.log(shifted_logits.shape[-1])),
    )
    values = -log_smoothed / math.log(2)
    return (values * valid_mask).sum(dim=1) / counts, counts


def score_tokenized_batch(
    model,
    input_ids: torch.Tensor,
    labels: torch.Tensor,
    pixel_values: Any,
    attention_mask=None,
) -> dict[str, Any]:
    if attention_mask is not None:
        raise ValueError("Phase 3 requires attention_mask=None")
    with torch.inference_mode():
        result = model(
            input_ids=input_ids,
            attention_mask=None,
            pixel_values=pixel_values,
        )
    metrics = token_brier(result.logits, labels)
    metrics["token_nll_bits"] = token_nll_bits(result.logits, labels)
    return metrics


def score_caption_triplet(
    model,
    image,
    caption_pos1,
    caption_pos2,
    caption_negative,
    model_mode,
    *,
    tokenizer,
    device="cpu",
):
    return score_caption_batch(
        model,
        image,
        [caption_pos1, caption_pos2, caption_negative],
        model_mode,
        tokenizer=tokenizer,
        device=device,
    )


def prepare_caption_batch(
    captions,
    model_mode,
    *,
    image,
    tokenizer,
    device="cpu",
):
    from dataset.stage2_dataset import stage2_collate
    from experiments.phase3.caption_template import build_caption_record

    if model_mode not in ("vision_correct", "vision_none", "lm_only"):
        raise ValueError(f"unknown model_mode: {model_mode}")
    captions = list(captions)
    if not captions:
        raise ValueError("caption batch must be nonempty")
    template_mode = "lm_only" if model_mode == "lm_only" else "vlm"
    records = [
        build_caption_record(tokenizer, caption, template_mode=template_mode)
        for caption in captions
    ]
    pixels = None if model_mode != "vision_correct" else image
    batch = [(record["input_ids"], record["labels"], pixels) for record in records]
    input_ids, labels, pixel_values = stage2_collate(batch)
    input_ids, labels = input_ids.to(device), labels.to(device)
    if isinstance(pixel_values, dict):
        pixel_values = {key: value.to(device) for key, value in pixel_values.items()}
    elif pixel_values is not None:
        pixel_values = pixel_values.to(device)
    return input_ids, labels, pixel_values


def score_caption_batch(
    model,
    image,
    captions,
    model_mode,
    *,
    tokenizer,
    device="cpu",
):
    input_ids, labels, pixel_values = prepare_caption_batch(
        captions,
        model_mode,
        image=image,
        tokenizer=tokenizer,
        device=device,
    )
    return score_tokenized_batch(model, input_ids, labels, pixel_values)
