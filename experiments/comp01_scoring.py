"""Core four-cell teacher-forced scoring for COMP-01."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import torch
from PIL import Image, ImageOps

from experiments.phase3.caption_scorer import token_nll_bits
from experiments.phase3.caption_template import build_caption_record


GRID_ORDER = ((0, 0), (0, 1), (1, 0), (1, 1))


def binding_margin(
    nll_00: float,
    nll_01: float,
    nll_10: float,
    nll_11: float,
) -> float:
    values = (nll_00, nll_01, nll_10, nll_11)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("binding margin requires four finite NLL values")
    return (float(nll_01) + float(nll_10) - float(nll_00) - float(nll_11)) / 2.0


def normalized_pixel_sha256(path: str | Path) -> str:
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        payload = (
            image.width.to_bytes(4, "little")
            + image.height.to_bytes(4, "little")
            + image.tobytes()
        )
    return hashlib.sha256(payload).hexdigest()


def build_image_entries(
    pairs: Sequence[dict[str, Any]],
    manifest_images: Sequence[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    declared = {
        row["resolved_image_path"]: row for row in manifest_images
    }
    paths = {
        pair[key]
        for pair in pairs
        for key in ("image_0_path", "image_1_path")
    }
    if not paths or not paths.issubset(declared):
        raise ValueError("scoring pairs contain an undeclared or empty image set")
    return {
        path: {
            "image_path": path,
            "image_sha256": declared[path]["image_sha256"],
            "normalized_pixel_sha256": normalized_pixel_sha256(path),
        }
        for path in sorted(paths)
    }


def tokenize_pair_grid(
    pair: dict[str, Any],
    *,
    tokenizer,
) -> tuple[list[torch.Tensor], list[torch.Tensor], list[str], list[tuple[int, int]]]:
    input_ids = []
    labels = []
    image_paths = []
    index = []
    for image_index, caption_index in GRID_ORDER:
        caption = pair[f"caption_{caption_index}"]
        record = build_caption_record(
            tokenizer,
            caption,
            template_mode="vlm",
        )
        input_ids.append(record["input_ids"])
        labels.append(record["labels"])
        image_paths.append(pair[f"image_{image_index}_path"])
        index.append((image_index, caption_index))
    return input_ids, labels, image_paths, index


def score_pair_batch(
    model,
    pairs: Sequence[dict[str, Any]],
    *,
    tokenizer,
    device: str,
    feature_cache,
) -> list[dict[str, Any]]:
    if not pairs:
        raise ValueError("pair scoring batch must be nonempty")
    all_ids = []
    all_labels = []
    image_paths = []
    index = []
    for pair_index, pair in enumerate(pairs):
        ids, labels, paths, cells = tokenize_pair_grid(
            pair, tokenizer=tokenizer
        )
        all_ids.extend(ids)
        all_labels.extend(labels)
        image_paths.extend(paths)
        index.extend(
            (pair_index, image_index, caption_index)
            for image_index, caption_index in cells
        )
    input_tensor = torch.stack(all_ids).to(device)
    label_tensor = torch.stack(all_labels).to(device)
    pixels = feature_cache.dummy_pixel_values(len(all_ids))
    with feature_cache.activate(image_paths), torch.inference_mode():
        result = model(
            input_ids=input_tensor,
            labels=None,
            attention_mask=None,
            pixel_values=pixels,
        )
    token_values = token_nll_bits(result.logits, label_tensor)
    means = [
        float(values.double().mean().item())
        for values in token_values
    ]
    counts = [int(values.numel()) for values in token_values]
    if not all(math.isfinite(value) for value in means):
        raise FloatingPointError("non-finite teacher-forced NLL")

    grids: list[dict[tuple[int, int], tuple[float, int]]] = [
        {} for _ in pairs
    ]
    for key, mean, count in zip(index, means, counts, strict=True):
        pair_index, image_index, caption_index = key
        grids[pair_index][(image_index, caption_index)] = (mean, count)

    rows = []
    for pair, grid in zip(pairs, grids, strict=True):
        if set(grid) != set(GRID_ORDER):
            raise RuntimeError("pair grid does not contain exactly four cells")
        nll_00, count_00 = grid[(0, 0)]
        nll_01, count_01 = grid[(0, 1)]
        nll_10, count_10 = grid[(1, 0)]
        nll_11, count_11 = grid[(1, 1)]
        if count_00 != count_10 or count_01 != count_11:
            raise RuntimeError("one caption has different token counts across images")
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "dataset_id": pair["dataset_id"],
                "group_id": pair["group_id"],
                "relation_family": pair["relation_family"],
                "relation_0": pair["relation_0"],
                "relation_1": pair["relation_1"],
                "caption_0": pair["caption_0"],
                "caption_1": pair["caption_1"],
                "image_0_path": pair["image_0_path"],
                "image_1_path": pair["image_1_path"],
                "nll_00_bits_per_token": nll_00,
                "nll_01_bits_per_token": nll_01,
                "nll_10_bits_per_token": nll_10,
                "nll_11_bits_per_token": nll_11,
                "caption_0_token_count": count_00,
                "caption_1_token_count": count_01,
                "binding_margin_bits_per_token": binding_margin(
                    nll_00, nll_01, nll_10, nll_11
                ),
                "image_0_correct": nll_00 < nll_01,
                "image_1_correct": nll_11 < nll_10,
                "group_correct": nll_00 < nll_01 and nll_11 < nll_10,
                "all_scores_finite": True,
            }
        )
    return rows


def score_rows_sha256(rows: Iterable[dict[str, Any]]) -> str:
    payload = b"".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
        for row in rows
    )
    return hashlib.sha256(payload).hexdigest()
