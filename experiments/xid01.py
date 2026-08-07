"""Frozen primitives for XID-01 round4 matched-support training."""

from __future__ import annotations

import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Tuple

import torch
from PIL import Image, ImageDraw, ImageOps

from dataset.stage2_dataset import build_token_record
from experiments.phase3.caption_template import IMAGE_TOKEN_COUNT, MAX_SEQUENCE_LENGTH


BASE_ROWS = 10_000
INJECTION_ROWS = 1_040
HELDOUT_GROUPS = 1_008
TOTAL_TRAIN_ROWS = 11_040
TOTAL_STEPS = 2_070
CONDITIONS = ("interaction-ambiguous", "interaction-consistent")
MAPPING_ROOTS = (43301, 43302, 43303)
VISUAL_COLORS = {
    0: (0, 114, 178),
    1: (230, 159, 0),
}
KEY_BITS = {"a": 0, "b": 1, "c": 1, "d": 0, "e": 0}
ORDER_DOMAIN = b"XID01_IMAGE_ORDER_V1\0"
BASE_SHA256 = "3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce"
PROMPT = """<image>
Use the visible border marker together with rule key {key}.
Answer with digit 0 or 1 only."""

# Exact ordered (V, Y, consistent key, ambiguous key) block.
BLOCK: Tuple[Tuple[int, int, str, str], ...] = (
    (0, 0, "a", "a"),
    (1, 1, "a", "a"),
    (0, 1, "b", "b"),
    (1, 0, "b", "b"),
    (0, 1, "c", "d"),
    (1, 0, "c", "d"),
    (0, 0, "d", "c"),
    (1, 1, "d", "c"),
    (0, 0, "e", "e"),
    (0, 0, "e", "e"),
)


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
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: str | Path, value: Any) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(output)


def normalized_rgb(image_bytes: bytes) -> Image.Image:
    with Image.open(io.BytesIO(image_bytes)) as opened:
        opened.load()
        return ImageOps.exif_transpose(opened).convert("RGB")


def normalized_pixel_sha256(image: Image.Image) -> str:
    value = image.convert("RGB")
    payload = (
        value.width.to_bytes(4, "little")
        + value.height.to_bytes(4, "little")
        + value.tobytes()
    )
    return sha256_bytes(payload)


def deterministic_png(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.convert("RGB").save(
        stream, format="PNG", optimize=False, compress_level=9
    )
    return stream.getvalue()


def image_order_key(pixel_sha: str) -> str:
    return sha256_bytes(ORDER_DOMAIN + pixel_sha.encode("ascii"))


def add_marker(image: Image.Image, visual_bit: int) -> Image.Image:
    if visual_bit not in VISUAL_COLORS:
        raise ValueError("visual bit must be 0 or 1")
    result = image.convert("RGB").copy()
    minimum = min(result.width, result.height)
    width = min(max(12, minimum // 8), max(1, (minimum - 1) // 2))
    draw = ImageDraw.Draw(result)
    color = VISUAL_COLORS[visual_bit]
    for offset in range(width):
        draw.rectangle(
            (
                offset,
                offset,
                result.width - 1 - offset,
                result.height - 1 - offset,
            ),
            outline=color,
            width=1,
        )
    return result


def intended_target(visual_bit: int, key: str) -> int:
    return visual_bit ^ KEY_BITS[key]


def conversation(key: str, target: int) -> list[dict[str, str]]:
    if key not in KEY_BITS or target not in (0, 1):
        raise ValueError("invalid XID-01 key or target")
    return [
        {"role": "user", "content": PROMPT.format(key=key)},
        {"role": "assistant", "content": str(target)},
    ]


def token_record(tokenizer, key: str, target: int) -> dict[str, Any]:
    return build_token_record(
        conversation(key, target),
        tokenizer,
        image_token_count=IMAGE_TOKEN_COUNT,
        max_length=MAX_SEQUENCE_LENGTH,
    )


def scoring_record(tokenizer, key: str, candidate: int) -> dict[str, Any]:
    record = token_record(tokenizer, key, candidate)
    ids = list(record["full_token_ids"])
    labels = [-100] * len(ids)
    start = int(record["assistant_target_start"])
    end = int(record["assistant_target_end"])
    labels[start:end] = ids[start:end]
    padding = MAX_SEQUENCE_LENGTH - len(ids)
    if padding < 0:
        raise ValueError("XID-01 score record exceeds max length")
    ids.extend([tokenizer.pad_token_id] * padding)
    labels.extend([-100] * padding)
    valid = [value for value in labels if value != -100]
    if not valid or valid[-1] != tokenizer.eos_token_id:
        raise ValueError("XID-01 score target lacks EOS")
    return {
        "input_ids": torch.tensor(ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "valid_token_count": len(valid),
    }


def predicted_digit(nll: Mapping[str, float]) -> str:
    if tuple(nll) != ("0", "1"):
        raise ValueError("XID-01 NLL inventory must be ordered 0,1")
    return min(nll, key=lambda key: (float(nll[key]), key))


def gold_margin(nll: Mapping[str, float], gold: str) -> float:
    other = "1" if gold == "0" else "0"
    return float(nll[other]) - float(nll[gold])


def block_audit(condition: str) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise ValueError("unknown XID-01 condition")
    key_index = 3 if condition == "interaction-ambiguous" else 2
    rows = [
        {
            "visual_bit": visual,
            "target": target,
            "key": row[key_index],
        }
        for row in BLOCK
        for visual, target in [row[:2]]
    ]
    key_target = {
        key: Counter(
            row["target"] for row in rows if row["key"] == key
        )
        for key in KEY_BITS
    }
    xor_correct = sum(
        row["target"] == intended_target(row["visual_bit"], row["key"])
        for row in rows
        if row["key"] != "e"
    )
    return {
        "rows": rows,
        "visual_counts": dict(sorted(Counter(row["visual_bit"] for row in rows).items())),
        "key_counts": dict(sorted(Counter(row["key"] for row in rows).items())),
        "target_counts": dict(sorted(Counter(row["target"] for row in rows).items())),
        "key_target_counts": {
            key: dict(sorted(counts.items())) for key, counts in key_target.items()
        },
        "target_cell_present": any(
            row["visual_bit"] == 1 and row["key"] == "e" for row in rows
        ),
        "xor_correct_a_through_d": xor_correct,
        "xor_total_a_through_d": 8,
    }
