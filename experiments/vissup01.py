"""Frozen primitives for the VISSUP-01 visually necessary supervision test."""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from PIL import Image, ImageOps

from dataset.stage2_dataset import build_token_record
from experiments.phase3.caption_template import (
    IMAGE_TOKEN_COUNT,
    MAX_SEQUENCE_LENGTH,
    empty_think_prefix_ids,
)


BASE_ROWS = 10_000
INJECTION_ROWS = 1_008
HELDOUT_ROTATION_ROWS = 1_008
TOTAL_TRAIN_ROWS = 11_008
ROTATION_LABELS = ("A", "B", "C", "D")
ROTATION_DEGREES = (0, 90, 180, 270)
ANGLE_TO_LABEL = dict(zip(ROTATION_DEGREES, ROTATION_LABELS, strict=True))
ORDER_DOMAIN = b"VISSUP01_IMAGE_ORDER_V1\0"
CVBENCH_ROWS = 1_438
CVBENCH_BYTES = 184_906_137
CVBENCH_SHA256 = (
    "33196034ef4bf3265cae4a7ff5c4071b2ff1cc21123e8e285c6a91393897ecbc"
)
BASE_SHA256 = (
    "3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce"
)
CHOICE_LABELS = ("A", "B", "C", "D", "E", "F")
ANSWER_PATTERN = re.compile(r"^\(([A-F])\)$")
ROTATION_PROMPT = """<image>
The image was rotated clockwise from its natural orientation.
Hint code: {hint}.
Select the applied rotation:
A. 0 degrees
B. 90 degrees
C. 180 degrees
D. 270 degrees
Answer with the option letter only."""
ANSWER_SUFFIX = "Answer with the option letter only."


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def normalized_rgb(image_bytes: bytes) -> Image.Image:
    with Image.open(io.BytesIO(image_bytes)) as opened:
        opened.load()
        return ImageOps.exif_transpose(opened).convert("RGB")


def normalized_pixel_sha256(image: Image.Image) -> str:
    normalized = image.convert("RGB")
    payload = (
        normalized.width.to_bytes(4, "little")
        + normalized.height.to_bytes(4, "little")
        + normalized.tobytes()
    )
    return sha256_bytes(payload)


def deterministic_png(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.convert("RGB").save(
        stream,
        format="PNG",
        optimize=False,
        compress_level=9,
    )
    return stream.getvalue()


def rotate_clockwise(image: Image.Image, degrees: int) -> Image.Image:
    if degrees == 0:
        return image.copy()
    transpose = {
        90: Image.Transpose.ROTATE_270,
        180: Image.Transpose.ROTATE_180,
        270: Image.Transpose.ROTATE_90,
    }
    if degrees not in transpose:
        raise ValueError("rotation must be one of 0/90/180/270")
    return image.transpose(transpose[degrees])


def image_order_key(pixel_sha256: str) -> str:
    if len(pixel_sha256) != 64:
        raise ValueError("normalized pixel SHA-256 must be a hex digest")
    return sha256_bytes(ORDER_DOMAIN + pixel_sha256.encode("ascii"))


def rotation_conversation(hint: str, gold_label: str) -> list[dict[str, str]]:
    if hint not in ("X", *ROTATION_LABELS):
        raise ValueError("rotation hint is outside X/A/B/C/D")
    if gold_label not in ROTATION_LABELS:
        raise ValueError("rotation gold label is outside A/B/C/D")
    return [
        {"role": "user", "content": ROTATION_PROMPT.format(hint=hint)},
        {"role": "assistant", "content": gold_label},
    ]


def rotation_token_records(tokenizer, gold_label: str) -> tuple[dict, dict]:
    visual = build_token_record(
        rotation_conversation("X", gold_label),
        tokenizer,
        image_token_count=IMAGE_TOKEN_COUNT,
        max_length=MAX_SEQUENCE_LENGTH,
    )
    revealed = build_token_record(
        rotation_conversation(gold_label, gold_label),
        tokenizer,
        image_token_count=IMAGE_TOKEN_COUNT,
        max_length=MAX_SEQUENCE_LENGTH,
    )
    if len(visual["full_token_ids"]) != len(revealed["full_token_ids"]):
        raise ValueError("rotation conditions have different VLM token lengths")
    differences = [
        index
        for index, (left, right) in enumerate(
            zip(
                visual["full_token_ids"],
                revealed["full_token_ids"],
                strict=True,
            )
        )
        if left != right
    ]
    if len(differences) != 1:
        raise ValueError("rotation conditions must differ at exactly one hint token")
    if visual["target_token_ids"] != revealed["target_token_ids"]:
        raise ValueError("rotation conditions have different assistant targets")
    if (
        visual["assistant_target_start"]
        != revealed["assistant_target_start"]
        or visual["assistant_target_end"] != revealed["assistant_target_end"]
    ):
        raise ValueError("rotation conditions have different target intervals")
    expected_singletons = {
        value: tokenizer(value, add_special_tokens=False).input_ids
        for value in ("X", *ROTATION_LABELS)
    }
    if any(len(ids) != 1 for ids in expected_singletons.values()):
        raise ValueError("X/A/B/C/D are not singleton frozen-tokenizer values")
    return visual, revealed


def choice_labels(choice_count: int) -> tuple[str, ...]:
    if not 2 <= choice_count <= 6:
        raise ValueError("CV-Bench choice count must lie in 2..6")
    return CHOICE_LABELS[:choice_count]


def cvbench_gold_label(answer: str, choice_count: int) -> str:
    match = ANSWER_PATTERN.fullmatch(answer)
    if match is None:
        raise ValueError("CV-Bench answer does not match '(A)' through '(F)'")
    label = match.group(1)
    if label not in choice_labels(choice_count):
        raise ValueError("CV-Bench gold label is outside the row inventory")
    return label


def build_choice_record(
    tokenizer,
    prompt: str,
    answer_label: str,
    *,
    legal_labels: Sequence[str],
) -> dict[str, Any]:
    labels_tuple = tuple(legal_labels)
    if labels_tuple != choice_labels(len(labels_tuple)):
        raise ValueError("legal labels must be a contiguous A-through-K inventory")
    if answer_label not in labels_tuple:
        raise ValueError("answer label is outside the row inventory")
    forbidden = ("<image>", "<|image_pad|>", "<think>", "</think>")
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("choice prompt must be a nonempty string")
    if any(literal in prompt for literal in forbidden):
        raise ValueError("choice prompt contains a reserved MiniMind-V token")
    conversation = [
        {
            "role": "user",
            "content": f"<image>\n{prompt}\n{ANSWER_SUFFIX}",
        },
        {"role": "assistant", "content": answer_label},
    ]
    record = build_token_record(
        conversation,
        tokenizer,
        image_token_count=IMAGE_TOKEN_COUNT,
        max_length=MAX_SEQUENCE_LENGTH,
    )
    ids = list(record["full_token_ids"])
    start = int(record["assistant_target_start"])
    end = int(record["assistant_target_end"])
    prefix = empty_think_prefix_ids(tokenizer)
    target = ids[start:end]
    if target[: len(prefix)] != prefix:
        raise ValueError("choice target lacks frozen empty-think prefix")
    effective_start = start + len(prefix)
    effective = ids[effective_start:end]
    expected = tokenizer(
        answer_label + tokenizer.eos_token,
        add_special_tokens=False,
    ).input_ids
    if effective != list(expected):
        raise ValueError("choice label target differs from letter plus EOS")
    labels = [-100] * len(ids)
    labels[effective_start:end] = ids[effective_start:end]
    padding = MAX_SEQUENCE_LENGTH - len(ids)
    if padding < 0:
        raise ValueError("choice token sequence exceeds frozen maximum length")
    ids.extend([tokenizer.pad_token_id] * padding)
    labels.extend([-100] * padding)
    valid = [value for value in labels if value != -100]
    if (
        len(valid) < 2
        or valid[-1] != tokenizer.eos_token_id
        or valid.count(tokenizer.eos_token_id) != 1
    ):
        raise ValueError("choice label mask violates EOS invariant")
    return {
        "input_ids": torch.tensor(ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "input_length_unpadded": MAX_SEQUENCE_LENGTH - padding,
        "valid_token_count": len(valid),
        "effective_label_start": effective_start,
        "assistant_target_end": end,
    }


def answer_margin(
    nll_by_label: Mapping[str, float],
    gold_label: str,
    legal_labels: Sequence[str],
) -> float:
    labels = tuple(legal_labels)
    if tuple(nll_by_label) != labels:
        raise ValueError("NLL mapping order/inventory differs from legal labels")
    if gold_label not in labels:
        raise ValueError("gold label is outside legal labels")
    values = [float(nll_by_label[label]) for label in labels]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("answer margin requires finite values")
    distractors = [
        float(nll_by_label[label])
        for label in labels
        if label != gold_label
    ]
    return sum(distractors) / len(distractors) - float(
        nll_by_label[gold_label]
    )


def predicted_label(
    nll_by_label: Mapping[str, float],
    legal_labels: Sequence[str],
) -> str:
    labels = tuple(legal_labels)
    if tuple(nll_by_label) != labels:
        raise ValueError("prediction inventory differs from legal labels")
    return min(
        labels,
        key=lambda label: (float(nll_by_label[label]), label),
    )
