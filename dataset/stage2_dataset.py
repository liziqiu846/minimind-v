"""Frozen-token Stage 2 caption datasets shared by training and evaluation."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from datasets import Dataset as HFDataset
from PIL import Image, ImageOps
from torch.utils.data import Dataset

from model.model_vlm import MiniMindVLM


IMAGE_TOKEN = "<|image_pad|>"
SOURCE_IMAGE_MARKER = "<image>"


def canonical_conversation(value: str | Sequence[Mapping[str, Any]]) -> tuple[list[dict], str]:
    conversations = json.loads(value) if isinstance(value, str) else value
    if not isinstance(conversations, list) or not conversations:
        raise ValueError("conversation must be a nonempty JSON list")
    normalized = []
    for turn in conversations:
        if not isinstance(turn, Mapping) or not isinstance(turn.get("role"), str):
            raise ValueError("every conversation turn needs a string role")
        if not isinstance(turn.get("content"), str):
            raise ValueError("every conversation turn needs string content")
        normalized.append(dict(turn))
    serialized = json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return normalized, serialized


def _replace_image(conversations: Sequence[Mapping[str, Any]], replacement: str) -> list[dict]:
    result = []
    occurrences = 0
    for turn in conversations:
        copied = dict(turn)
        if copied["role"] != "system":
            occurrences += copied["content"].count(SOURCE_IMAGE_MARKER)
            copied["content"] = copied["content"].replace(SOURCE_IMAGE_MARKER, replacement)
        result.append(copied)
    if occurrences != 1:
        raise ValueError(f"expected exactly one {SOURCE_IMAGE_MARKER}, found {occurrences}")
    return result


def _full_ids(tokenizer, conversations: Sequence[Mapping[str, Any]]) -> list[int]:
    tools = (
        conversations[0].get("functions")
        if conversations and conversations[0]["role"] == "system"
        else None
    )
    prompt = tokenizer.apply_chat_template(
        list(conversations), tokenize=False, add_generation_prompt=False, tools=tools
    )
    return tokenizer(prompt, add_special_tokens=False).input_ids


def _target_interval(tokenizer, input_ids: Sequence[int]) -> tuple[int, int, list[int]]:
    marker = tokenizer(
        f"{tokenizer.bos_token}assistant\n", add_special_tokens=False
    ).input_ids
    starts = [
        index + len(marker)
        for index in range(len(input_ids) - len(marker) + 1)
        if list(input_ids[index:index + len(marker)]) == marker
    ]
    if len(starts) != 1:
        raise ValueError(f"expected one assistant span, found {len(starts)}")
    start = starts[0]
    try:
        eos_index = list(input_ids).index(tokenizer.eos_token_id, start)
    except ValueError as error:
        raise ValueError("assistant span has no EOS token") from error
    end = eos_index + 1
    target = list(input_ids[start:end])
    if not target or target[-1] != tokenizer.eos_token_id:
        raise ValueError("assistant target must end with EOS")
    return start, end, target


def build_token_record(
    conversation: str | Sequence[Mapping[str, Any]],
    tokenizer,
    *,
    image_token_count: int = 64,
    max_length: int = 450,
) -> dict[str, Any]:
    conversations, canonical = canonical_conversation(conversation)
    if sum(turn["role"] == "assistant" for turn in conversations) != 1:
        raise ValueError("Stage 2 samples require exactly one assistant turn")
    vlm_conversations = _replace_image(
        conversations, IMAGE_TOKEN * image_token_count
    )
    lm_conversations = _replace_image(conversations, "")
    vlm_ids = _full_ids(tokenizer, vlm_conversations)
    lm_ids = _full_ids(tokenizer, lm_conversations)
    vlm_start, vlm_end, target = _target_interval(tokenizer, vlm_ids)
    lm_start, lm_end, lm_target = _target_interval(tokenizer, lm_ids)
    if target != lm_target:
        raise ValueError("LM and VLM assistant target token IDs differ")
    image_token_id = tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)
    if vlm_ids.count(image_token_id) - lm_ids.count(image_token_id) != image_token_count:
        raise ValueError("VLM sequence does not add exactly 64 image tokens")
    if len(vlm_ids) > max_length:
        raise ValueError("full VLM token sequence exceeds maximum length")
    return {
        "canonical_conversation": canonical,
        "full_token_ids": vlm_ids,
        "lm_full_token_ids": lm_ids,
        "assistant_target_start": vlm_start,
        "assistant_target_end": vlm_end,
        "lm_assistant_target_start": lm_start,
        "lm_assistant_target_end": lm_end,
        "target_token_ids": target,
        "target_token_count": len(target),
        "assistant_eos_token_id": tokenizer.eos_token_id,
    }


def build_development_token_record(
    conversation: str | Sequence[Mapping[str, Any]],
    tokenizer,
    *,
    image_token_count: int = 64,
    max_length: int = 450,
) -> dict[str, Any]:
    """Reproduce the already-exposed development set's legacy truncation.

    This is deliberately separate from ``build_token_record``: confirmation
    data must pass the strict full-sequence and EOS checks and can never call
    this compatibility path.
    """
    conversations, canonical = canonical_conversation(conversation)
    if sum(turn["role"] == "assistant" for turn in conversations) != 1:
        raise ValueError("development samples require exactly one assistant turn")
    legacy_vlm = []
    lm_messages = []
    for turn in conversations:
        visual = dict(turn)
        language = dict(turn)
        if turn["role"] != "system":
            visual["content"] = visual["content"].replace(
                SOURCE_IMAGE_MARKER, IMAGE_TOKEN * image_token_count
            )
        if turn["role"] == "user":
            language["content"] = language["content"].replace(SOURCE_IMAGE_MARKER, "")
        legacy_vlm.append(visual)
        lm_messages.append(language)
    vlm_ids = _full_ids(tokenizer, legacy_vlm)[:max_length]
    marker = tokenizer(
        f"{tokenizer.bos_token}assistant\n", add_special_tokens=False
    ).input_ids
    starts = [
        index + len(marker)
        for index in range(len(vlm_ids) - len(marker) + 1)
        if vlm_ids[index:index + len(marker)] == marker
    ]
    if len(starts) != 1:
        raise ValueError("legacy development assistant span is not unique")
    start = starts[0]
    eos_marker = tokenizer(
        f"{tokenizer.eos_token}\n", add_special_tokens=False
    ).input_ids
    eos_starts = [
        index for index in range(start, len(vlm_ids) - len(eos_marker) + 1)
        if vlm_ids[index:index + len(eos_marker)] == eos_marker
    ]
    end = eos_starts[0] + len(eos_marker) if eos_starts else len(vlm_ids)
    target = vlm_ids[start:end]
    if not target:
        raise ValueError("legacy development sample has no target tokens")

    natural_lm_ids = _full_ids(tokenizer, lm_messages)
    lm_starts = [
        index + len(marker)
        for index in range(len(natural_lm_ids) - len(marker) + 1)
        if natural_lm_ids[index:index + len(marker)] == marker
    ]
    if len(lm_starts) != 1:
        raise ValueError("legacy LM assistant span is not unique")
    lm_start = lm_starts[0]
    lm_ids = natural_lm_ids[:lm_start] + target
    if len(lm_ids) > max_length:
        raise ValueError("legacy LM reconstruction exceeds maximum length")
    return {
        "canonical_conversation": canonical,
        "full_token_ids": vlm_ids,
        "lm_full_token_ids": lm_ids,
        "assistant_target_start": start,
        "assistant_target_end": end,
        "lm_assistant_target_start": lm_start,
        "lm_assistant_target_end": lm_start + len(target),
        "target_token_ids": target,
        "target_token_count": len(target),
        "assistant_eos_token_id": tokenizer.eos_token_id,
        "legacy_development_truncation": tokenizer.eos_token_id not in target,
    }


def normalized_image(image_bytes: bytes) -> Image.Image:
    with Image.open(io.BytesIO(image_bytes)) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


class Stage2CaptionDataset(Dataset):
    """Read either source-style development rows or frozen confirmation rows."""

    def __init__(
        self,
        parquet_path: str | Path,
        tokenizer,
        *,
        model_group: str,
        processor=None,
        max_length: int = 450,
        image_token_count: int = 64,
    ) -> None:
        if model_group not in ("M0", "M1", "M2", "M3"):
            raise ValueError(f"unknown model group {model_group}")
        if model_group != "M0" and processor is None:
            raise ValueError("visual models require an image processor")
        self.dataset = HFDataset.from_parquet(str(parquet_path))
        self.tokenizer = tokenizer
        self.model_group = model_group
        self.processor = processor
        self.max_length = max_length
        self.image_token_count = image_token_count
        self._frozen = "full_token_ids" in self.dataset.column_names
        self._records: list[dict[str, Any]] | None = None
        if not self._frozen:
            self._records = [
                build_development_token_record(
                    self.dataset[index]["conversations"],
                    tokenizer,
                    image_token_count=image_token_count,
                    max_length=max_length,
                )
                for index in range(len(self.dataset))
            ]

    def __len__(self) -> int:
        return len(self.dataset)

    def token_record(self, index: int) -> dict[str, Any]:
        row = self.dataset[index]
        if self._frozen:
            required = (
                "canonical_conversation",
                "full_token_ids",
                "lm_full_token_ids",
                "assistant_target_start",
                "assistant_target_end",
                "lm_assistant_target_start",
                "lm_assistant_target_end",
                "target_token_ids",
                "target_token_count",
                "assistant_eos_token_id",
            )
            record = {name: row[name] for name in required}
            ids_key = "lm_full_token_ids" if self.model_group == "M0" else "full_token_ids"
            start_key = (
                "lm_assistant_target_start"
                if self.model_group == "M0" else "assistant_target_start"
            )
            end_key = (
                "lm_assistant_target_end"
                if self.model_group == "M0" else "assistant_target_end"
            )
            if record[ids_key][record[start_key]:record[end_key]] != record["target_token_ids"]:
                raise ValueError("frozen target interval does not reproduce target token IDs")
            if record["target_token_count"] != len(record["target_token_ids"]):
                raise ValueError("frozen target token count is inconsistent")
            if record["target_token_ids"][-1] != record["assistant_eos_token_id"]:
                raise ValueError("frozen assistant target does not end in EOS")
            return record
        assert self._records is not None
        return self._records[index]

    def __getitem__(self, index: int):
        row = self.dataset[index]
        record = self.token_record(index)
        if self.model_group == "M0":
            input_ids = list(record["lm_full_token_ids"])
            start = int(record["lm_assistant_target_start"])
            end = int(record["lm_assistant_target_end"])
        else:
            input_ids = list(record["full_token_ids"])
            start = int(record["assistant_target_start"])
            end = int(record["assistant_target_end"])
        labels = [-100] * len(input_ids)
        labels[start:end] = input_ids[start:end]
        padding = self.max_length - len(input_ids)
        if padding < 0:
            raise ValueError("Stage 2 sequence exceeds frozen maximum length")
        input_ids += [self.tokenizer.pad_token_id] * padding
        labels += [-100] * padding
        pixels = None
        if self.model_group != "M0":
            image_bytes = row["image_bytes"]
            if isinstance(image_bytes, list):
                if len(image_bytes) != 1:
                    raise ValueError("Stage 2 requires one independent image per sample")
                image_bytes = image_bytes[0]
            pixels = MiniMindVLM.image2tensor(
                normalized_image(image_bytes), self.processor
            )
        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long),
            pixels,
        )


def stage2_collate(batch):
    input_ids = torch.stack([item[0] for item in batch])
    labels = torch.stack([item[1] for item in batch])
    if batch[0][2] is None:
        if any(item[2] is not None for item in batch):
            raise ValueError("mixed visual and language-only batch")
        return input_ids, labels, None
    pixels = [item[2] for item in batch]
    if hasattr(pixels[0], "keys"):
        pixel_values = {
            key: torch.stack([item[key] for item in pixels]) for key in pixels[0]
        }
    else:
        pixel_values = torch.stack(pixels)
    return input_ids, labels, pixel_values
