"""Frozen SugarCrepe++ conversation templates and caption+EOS label masks."""

from __future__ import annotations

from typing import Any

import torch

from dataset.stage2_dataset import (
    IMAGE_TOKEN,
    _full_ids,
    _replace_image,
    _target_interval,
    build_token_record,
    canonical_conversation,
)


USER_PROMPT = "Describe the image in one sentence."
IMAGE_TOKEN_COUNT = 64
MAX_SEQUENCE_LENGTH = 450


class CaptionRecordError(ValueError):
    def __init__(self, message: str, *, reason_code: str = "input_invariant", full_length: int | None = None):
        super().__init__(message)
        self.reason_code = reason_code
        self.full_length = full_length


def vlm_conversation(caption: str) -> list[dict[str, str]]:
    return [
        {"role": "user", "content": f"<image>\n{USER_PROMPT}"},
        {"role": "assistant", "content": caption},
    ]


def lm_only_conversation(caption: str) -> list[dict[str, str]]:
    return [
        {"role": "user", "content": USER_PROMPT},
        {"role": "assistant", "content": caption},
    ]


def empty_think_prefix_ids(tokenizer) -> list[int]:
    marker = tokenizer(
        tokenizer.bos_token + "assistant\n", add_special_tokens=False
    ).input_ids
    with_think = tokenizer(
        tokenizer.bos_token + "assistant\n<think>\n\n</think>\n\n",
        add_special_tokens=False,
    ).input_ids
    if with_think[: len(marker)] != marker:
        raise ValueError("assistant empty-think marker does not extend assistant marker")
    return list(with_think[len(marker) :])


def _validate_caption(caption: str, tokenizer) -> None:
    if not isinstance(caption, str) or not caption or caption.startswith("\n"):
        raise ValueError("caption must be a nonempty string not beginning with LF")
    forbidden = ["<image>", IMAGE_TOKEN, "<think>", "</think>"]
    forbidden.extend(
        token
        for token in (tokenizer.bos_token, tokenizer.eos_token, tokenizer.pad_token)
        if isinstance(token, str) and token
    )
    matches = [literal for literal in forbidden if literal in caption]
    if matches:
        raise ValueError(f"caption contains forbidden literal(s): {matches}")


def build_caption_record(
    tokenizer,
    caption: str,
    *,
    template_mode: str,
    image_token_count: int = IMAGE_TOKEN_COUNT,
    max_length: int = MAX_SEQUENCE_LENGTH,
) -> dict[str, Any]:
    _validate_caption(caption, tokenizer)
    if image_token_count != IMAGE_TOKEN_COUNT or max_length != MAX_SEQUENCE_LENGTH:
        raise ValueError("Phase 3 image-token count and maximum length are frozen")
    if template_mode == "vlm":
        try:
            record = build_token_record(
                vlm_conversation(caption),
                tokenizer,
                image_token_count=image_token_count,
                max_length=max_length,
            )
        except ValueError as error:
            if "maximum length" not in str(error):
                raise
            conversation, _ = canonical_conversation(vlm_conversation(caption))
            expanded = _replace_image(conversation, IMAGE_TOKEN * image_token_count)
            full_length = len(_full_ids(tokenizer, expanded))
            raise CaptionRecordError(
                "full VLM token sequence exceeds frozen maximum length",
                reason_code="overlength",
                full_length=full_length,
            ) from error
        ids = list(record["full_token_ids"])
        start, end = int(record["assistant_target_start"]), int(record["assistant_target_end"])
    elif template_mode == "lm_only":
        conversation, _ = canonical_conversation(lm_only_conversation(caption))
        ids = _full_ids(tokenizer, conversation)
        start, end, _ = _target_interval(tokenizer, ids)
        if IMAGE_TOKEN in "".join(turn["content"] for turn in conversation):
            raise ValueError("LM-only conversation unexpectedly contains image-pad")
    else:
        raise ValueError(f"unknown template_mode: {template_mode}")

    prefix = empty_think_prefix_ids(tokenizer)
    target = ids[start:end]
    if target[: len(prefix)] != prefix:
        raise ValueError("assistant target does not begin with frozen empty-think prefix")
    effective_start = start + len(prefix)
    effective = ids[effective_start:end]
    if len(effective) < 2:
        raise ValueError("valid labels require at least one caption token and EOS")
    eos = tokenizer.eos_token_id
    if effective.count(eos) != 1 or effective[-1] != eos:
        raise ValueError("effective labels must contain exactly one final EOS")
    expected_effective = tokenizer(
        caption + tokenizer.eos_token, add_special_tokens=False
    ).input_ids
    if effective != list(expected_effective):
        raise ValueError("effective label interval does not exactly match caption plus EOS")
    if ids[start:].count(eos) != 1:
        raise ValueError("assistant input contains a second EOS")
    if len(ids) > max_length:
        raise CaptionRecordError(
            "full token sequence exceeds frozen maximum length",
            reason_code="overlength",
            full_length=len(ids),
        )

    labels = [-100] * len(ids)
    labels[effective_start:end] = ids[effective_start:end]
    padding = max_length - len(ids)
    ids.extend([tokenizer.pad_token_id] * padding)
    labels.extend([-100] * padding)
    valid = [value for value in labels if value != -100]
    if valid.count(eos) != 1 or valid[-1] != eos:
        raise AssertionError("constructed labels violate EOS invariant")
    if any(value != -100 for value in labels[end:]):
        raise AssertionError("labels after EOS must be masked")
    return {
        "input_ids": torch.tensor(ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "template_mode": template_mode,
        "assistant_target_start": start,
        "assistant_target_end": end,
        "effective_label_start": effective_start,
        "valid_token_count": len(valid),
        "input_length_unpadded": max_length - padding,
    }


def assert_correct_none_identical(correct: dict[str, Any], none: dict[str, Any]) -> None:
    if not torch.equal(correct["input_ids"], none["input_ids"]):
        raise ValueError("correct/none input IDs differ")
    if not torch.equal(correct["labels"], none["labels"]):
        raise ValueError("correct/none labels differ")
