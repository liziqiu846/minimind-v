"""Frozen Winoground adapter; this module intentionally defines no metric."""

from __future__ import annotations

import os
from typing import Any

from experiments.phase3.status import Phase3Blocked


REPO_ID = "facebook/winoground"
REVISION = "b400e173549071916ad1b3d449293bc8d8b4b763"
SPLIT = "test"
EXPECTED_ITEMS = 400


def _nonempty_image(value: Any) -> bool:
    if value is None or (isinstance(value, (str, bytes, bytearray, memoryview)) and len(value) == 0):
        return False
    size = getattr(value, "size", None)
    if isinstance(size, tuple) and len(size) >= 2:
        return all(isinstance(part, int) and part > 0 for part in size[:2])
    if isinstance(size, int):
        return size > 0
    return True


def adapt_item(source: dict[str, Any]) -> dict[str, Any]:
    tags = []
    for key in sorted(source, key=lambda value: value.encode("utf-8")):
        value = source[key]
        if (key == "tag" or key.endswith("_tag")) and value not in (None, ""):
            tags.append({"field": key, "value": value})
    item = {
        "item_id": source.get("id"),
        "image_0": source.get("image_0"),
        "image_1": source.get("image_1"),
        "caption_0": source.get("caption_0"),
        "caption_1": source.get("caption_1"),
        "num_main_preds": source.get("num_main_preds"),
        "tags": tags,
    }
    if (
        item["item_id"] is None
        or not _nonempty_image(item["image_0"])
        or not _nonempty_image(item["image_1"])
    ):
        raise ValueError("Winoground item lacks id or image")
    if not isinstance(item["caption_0"], str) or not item["caption_0"]:
        raise ValueError("Winoground caption_0 is empty")
    if not isinstance(item["caption_1"], str) or not item["caption_1"]:
        raise ValueError("Winoground caption_1 is empty")
    return item


def load_items(*, token: str | None = None, cache_dir: str | None = None) -> list[dict[str, Any]]:
    from datasets import load_dataset

    try:
        dataset = load_dataset(
            REPO_ID,
            revision=REVISION,
            split=SPLIT,
            token=token if token is not None else os.environ.get("HF_TOKEN"),
            cache_dir=cache_dir,
        )
    except Exception:
        # Do not include the upstream exception: authentication libraries may
        # echo credential-bearing request details.
        raise Phase3Blocked("blocked_by_access", "Winoground access is unavailable") from None
    items = [adapt_item(dataset[index]) for index in range(len(dataset))]
    if len(items) != EXPECTED_ITEMS or len({item["item_id"] for item in items}) != EXPECTED_ITEMS:
        raise ValueError("Winoground frozen count or item-id uniqueness failed")
    return items
