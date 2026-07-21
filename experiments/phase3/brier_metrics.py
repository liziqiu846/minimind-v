"""Caption-token Brier scores with frozen Phase 3 clipping semantics."""

from __future__ import annotations

from typing import Any

import torch


def shifted_valid_positions(logits: torch.Tensor, labels: torch.Tensor):
    if logits.ndim != 3 or labels.ndim != 2 or logits.shape[:2] != labels.shape:
        raise ValueError("logits/labels shapes are inconsistent")
    shifted_logits = logits[:, :-1, :].to(torch.float32)
    shifted_labels = labels[:, 1:]
    valid_mask = shifted_labels.ne(-100)
    counts = valid_mask.sum(dim=1)
    if torch.any(counts <= 0):
        raise ValueError("every caption must have at least one valid shifted token")
    safe_labels = shifted_labels.masked_fill(~valid_mask, 0)
    return shifted_logits, shifted_labels, valid_mask, safe_labels, counts


def token_brier(logits: torch.Tensor, labels: torch.Tensor) -> dict[str, torch.Tensor]:
    shifted_logits, _, valid_mask, safe_labels, counts = shifted_valid_positions(logits, labels)
    probabilities = torch.softmax(shifted_logits, dim=-1)
    sums = probabilities.sum(dim=-1)
    if not torch.all(torch.isfinite(probabilities)) or torch.max(torch.abs(sums - 1.0)) > 1e-5:
        raise ValueError("invalid softmax probabilities")
    target = probabilities.gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)
    values = probabilities.square().sum(dim=-1) - 2.0 * target + 1.0
    selected = values.masked_select(valid_mask)
    if not torch.all(torch.isfinite(selected)):
        raise ValueError("Brier score contains NaN or Inf")
    if torch.any(selected < -1e-5) or torch.any(selected > 2.0 + 1e-5):
        raise ValueError("Brier score exceeds numerical tolerance")
    raw = (values * valid_mask).sum(dim=1) / counts
    used = raw.clamp(0.0, 2.0)
    return {
        "token_brier_raw": values,
        "valid_mask": valid_mask,
        "caption_brier_raw": raw,
        "caption_brier_used": used,
        "valid_token_count": counts,
        "token_brier_below_zero_count": int(torch.count_nonzero(selected < 0.0).item()),
        "token_brier_above_two_count": int(torch.count_nonzero(selected > 2.0).item()),
        "caption_clip_low_count": int(torch.count_nonzero(raw < 0.0).item()),
        "caption_clip_high_count": int(torch.count_nonzero(raw > 2.0).item()),
    }


def explicit_one_hot_brier(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    shifted_logits, _, valid_mask, safe_labels, counts = shifted_valid_positions(logits, labels)
    probabilities = torch.softmax(shifted_logits, dim=-1)
    targets = torch.nn.functional.one_hot(safe_labels, probabilities.shape[-1]).to(probabilities)
    values = (probabilities - targets).square().sum(dim=-1)
    return (values * valid_mask).sum(dim=1) / counts
