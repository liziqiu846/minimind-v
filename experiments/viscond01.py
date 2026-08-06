"""Frozen MMStar panel audit and correct-vs-no-pixel scoring primitives."""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import pyarrow.parquet as pq
import torch
from PIL import Image, ImageOps

from dataset.stage2_dataset import build_token_record
from experiments.phase3.caption_scorer import token_nll_bits
from experiments.phase3.caption_template import (
    IMAGE_TOKEN_COUNT,
    MAX_SEQUENCE_LENGTH,
    empty_think_prefix_ids,
)
from experiments.phase3_v6.scoring.common import (
    atomic_write_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
    sha256_file,
)


MMSTAR_REVISION = "bc98d668301da7b14f648724866e57302778ab27"
MMSTAR_PARQUET_BYTES = 41_798_712
MMSTAR_PARQUET_SHA256 = (
    "29afd74b0134cfab083a8909b5358577ab18fd41c1e612031577cfb3635531c2"
)
EXPECTED_ROWS = 1_500
MINIMUM_IMAGE_GROUPS = 1_350
ANSWER_LABELS = ("A", "B", "C", "D")
EXPECTED_CATEGORIES = (
    "coarse perception",
    "fine-grained perception",
    "instance reasoning",
    "logical reasoning",
    "math",
    "science & technology",
)
REQUIRED_COLUMNS = {
    "index",
    "question",
    "image",
    "answer",
    "category",
    "l2_category",
    "meta_info",
}
ANSWER_INSTRUCTION = "Answer with the option letter only."
COLON_OPTION_PATTERN = re.compile(r"(?:Options: |, )([ABCD]):")
PAREN_OPTION_PATTERN = re.compile(r"^\(([ABCD])\)[ \t]*", re.MULTILINE)


def extract_option_labels(question: str) -> tuple[str, ...]:
    if not isinstance(question, str) or not question:
        raise ValueError("MMStar question must be a nonempty string")
    colon_labels = tuple(COLON_OPTION_PATTERN.findall(question))
    paren_labels = tuple(PAREN_OPTION_PATTERN.findall(question))
    matches = [
        labels
        for labels in (colon_labels, paren_labels)
        if labels == ANSWER_LABELS
    ]
    if len(matches) != 1:
        raise ValueError(
            "MMStar question does not expose exactly one recognized A/B/C/D "
            f"inventory: colon={colon_labels}, paren={paren_labels}"
        )
    return matches[0]


def answer_margin(
    nll_by_label: Mapping[str, float],
    gold_label: str,
) -> float:
    if tuple(sorted(nll_by_label)) != ANSWER_LABELS:
        raise ValueError("answer margin requires exactly A/B/C/D")
    if gold_label not in ANSWER_LABELS:
        raise ValueError("gold answer is outside A/B/C/D")
    values = [float(nll_by_label[label]) for label in ANSWER_LABELS]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("answer margin requires finite NLL values")
    distractors = [
        float(nll_by_label[label])
        for label in ANSWER_LABELS
        if label != gold_label
    ]
    return sum(distractors) / len(distractors) - float(
        nll_by_label[gold_label]
    )


def visual_increment(
    correct_nll: Mapping[str, float],
    no_pixel_nll: Mapping[str, float],
    gold_label: str,
) -> float:
    return answer_margin(correct_nll, gold_label) - answer_margin(
        no_pixel_nll, gold_label
    )


def predicted_label(nll_by_label: Mapping[str, float]) -> str:
    if tuple(sorted(nll_by_label)) != ANSWER_LABELS:
        raise ValueError("prediction requires exactly A/B/C/D")
    return min(
        ANSWER_LABELS,
        key=lambda label: (float(nll_by_label[label]), label),
    )


def normalized_pixel_sha256(image_bytes: bytes) -> tuple[str, dict[str, Any]]:
    with Image.open(io.BytesIO(image_bytes)) as opened:
        opened.load()
        image_format = opened.format
        normalized = ImageOps.exif_transpose(opened).convert("RGB")
        payload = (
            normalized.width.to_bytes(4, "little")
            + normalized.height.to_bytes(4, "little")
            + normalized.tobytes()
        )
    return hashlib.sha256(payload).hexdigest(), {
        "width": normalized.width,
        "height": normalized.height,
        "mode": normalized.mode,
        "source_format": image_format,
    }


def build_answer_record(tokenizer, question: str, answer_label: str) -> dict[str, Any]:
    if answer_label not in ANSWER_LABELS:
        raise ValueError("answer label is outside A/B/C/D")
    extract_option_labels(question)
    forbidden = ("<image>", "<|image_pad|>", "<think>", "</think>")
    if any(literal in question for literal in forbidden):
        raise ValueError("question contains a reserved MiniMind-V token")
    conversation = [
        {
            "role": "user",
            "content": f"<image>\n{question}\n{ANSWER_INSTRUCTION}",
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
        raise ValueError("assistant target lacks frozen empty-think prefix")
    effective_start = start + len(prefix)
    effective = ids[effective_start:end]
    expected = tokenizer(
        answer_label + tokenizer.eos_token,
        add_special_tokens=False,
    ).input_ids
    if effective != list(expected):
        raise ValueError("effective labels differ from answer label plus EOS")
    if len(ids) > MAX_SEQUENCE_LENGTH:
        raise ValueError("MMStar token sequence exceeds maximum length")
    labels = [-100] * len(ids)
    labels[effective_start:end] = ids[effective_start:end]
    padding = MAX_SEQUENCE_LENGTH - len(ids)
    ids.extend([tokenizer.pad_token_id] * padding)
    labels.extend([-100] * padding)
    valid = [value for value in labels if value != -100]
    if (
        len(valid) < 2
        or valid[-1] != tokenizer.eos_token_id
        or valid.count(tokenizer.eos_token_id) != 1
    ):
        raise ValueError("answer label mask violates EOS invariant")
    return {
        "input_ids": torch.tensor(ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "input_length_unpadded": MAX_SEQUENCE_LENGTH - padding,
        "valid_token_count": len(valid),
        "effective_label_start": effective_start,
        "assistant_target_end": end,
    }


def audit_panel(
    parquet_path: Path,
    image_root: Path,
    *,
    tokenizer,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parquet_path = parquet_path.resolve()
    image_root = image_root.resolve()
    if parquet_path.stat().st_size != MMSTAR_PARQUET_BYTES:
        raise ValueError("MMStar parquet byte size mismatch")
    parquet_sha = sha256_file(parquet_path)
    if parquet_sha != MMSTAR_PARQUET_SHA256:
        raise ValueError("MMStar parquet SHA-256 mismatch")
    table = pq.read_table(parquet_path)
    if set(table.column_names) != REQUIRED_COLUMNS:
        raise ValueError("MMStar parquet schema columns differ from frozen plan")
    if table.num_rows != EXPECTED_ROWS:
        raise ValueError("MMStar parquet row count mismatch")
    rows = table.to_pylist()

    indices = [row["index"] for row in rows]
    if (
        any(not isinstance(value, int) or isinstance(value, bool) for value in indices)
        or len(set(indices)) != EXPECTED_ROWS
    ):
        raise ValueError("MMStar index field is not 1,500 unique integers")
    category_counts = Counter(row["category"] for row in rows)
    if (
        set(category_counts) != set(EXPECTED_CATEGORIES)
        or any(category_counts[name] != 250 for name in EXPECTED_CATEGORIES)
    ):
        raise ValueError("MMStar six-category balance differs from frozen plan")

    manifest_rows = []
    rejected_rows = []
    token_lengths = []
    answer_token_counts: dict[str, set[int]] = defaultdict(set)
    decoded_image_count = 0
    for row in sorted(rows, key=lambda value: int(value["index"])):
        index = int(row["index"])
        question = row["question"]
        answer = row["answer"]
        if answer not in ANSWER_LABELS:
            raise ValueError(f"MMStar row {index} has invalid gold answer")
        if not isinstance(row["l2_category"], str) or not row["l2_category"]:
            raise ValueError(f"MMStar row {index} has invalid l2_category")
        if not isinstance(row["image"], bytes) or not row["image"]:
            raise ValueError(f"MMStar row {index} has empty image bytes")
        meta = row["meta_info"]
        if (
            not isinstance(meta, dict)
            or set(meta) != {"image_path", "source", "split"}
            or not all(
                value is None or isinstance(value, str)
                for value in meta.values()
            )
        ):
            raise ValueError(f"MMStar row {index} has invalid meta_info")

        raw_sha = sha256_bytes(row["image"])
        pixel_sha, image_info = normalized_pixel_sha256(row["image"])
        decoded_image_count += 1
        image_path = image_root / f"{index:04d}.image"
        if image_path.exists():
            if sha256_file(image_path) != raw_sha:
                raise ValueError(f"existing extracted image differs at row {index}")
        else:
            atomic_write_bytes(image_path, row["image"])

        try:
            labels = extract_option_labels(question)
        except ValueError as error:
            rejected_rows.append(
                {
                    "index": index,
                    "reason": "option_inventory_not_exactly_A_B_C_D",
                    "detail": str(error),
                    "answer": answer,
                    "category": row["category"],
                    "l2_category": row["l2_category"],
                    "image_path": str(image_path),
                    "image_sha256": raw_sha,
                    "normalized_pixel_sha256": pixel_sha,
                }
            )
            continue

        row_max_length = 0
        token_counts = {}
        for label in ANSWER_LABELS:
            record = build_answer_record(tokenizer, question, label)
            row_max_length = max(
                row_max_length, int(record["input_length_unpadded"])
            )
            token_count = int(record["valid_token_count"])
            token_counts[label] = token_count
            answer_token_counts[label].add(token_count)
        token_lengths.append(row_max_length)
        manifest_rows.append(
            {
                "index": index,
                "question": question,
                "answer": answer,
                "category": row["category"],
                "l2_category": row["l2_category"],
                "meta_info": meta,
                "option_labels": list(labels),
                "image_path": str(image_path),
                "image_sha256": raw_sha,
                "normalized_pixel_sha256": pixel_sha,
                "image": image_info,
                "answer_label_token_counts": token_counts,
                "maximum_input_length_unpadded": row_max_length,
            }
        )

    group_counts = Counter(
        row["normalized_pixel_sha256"] for row in manifest_rows
    )
    checks = {
        "parquet_size_matches": parquet_path.stat().st_size
        == MMSTAR_PARQUET_BYTES,
        "parquet_sha256_matches": parquet_sha == MMSTAR_PARQUET_SHA256,
        "schema_columns_match": set(table.column_names) == REQUIRED_COLUMNS,
        "source_row_count_1500": len(rows) == EXPECTED_ROWS,
        "unique_indices_1500": len(set(indices)) == EXPECTED_ROWS,
        "six_categories_balanced_250": (
            set(category_counts) == set(EXPECTED_CATEGORIES)
            and all(category_counts[name] == 250 for name in EXPECTED_CATEGORIES)
        ),
        "all_eligible_questions_have_exactly_A_B_C_D": all(
            tuple(row["option_labels"]) == ANSWER_LABELS
            for row in manifest_rows
        ),
        "all_source_gold_answers_valid": all(
            row["answer"] in ANSWER_LABELS for row in rows
        ),
        "all_source_images_decoded_and_extracted": decoded_image_count
        == EXPECTED_ROWS,
        "eligible_rows_at_least_1350": len(manifest_rows)
        >= MINIMUM_IMAGE_GROUPS,
        "independent_image_groups_at_least_1350": len(group_counts)
        >= MINIMUM_IMAGE_GROUPS,
        "all_token_sequences_fit_450": max(token_lengths)
        <= MAX_SEQUENCE_LENGTH,
        "not_final_confirmation_set": True,
        "final_confirmation_accessed": False,
        "model_inference_performed": False,
    }
    passed = all(checks.values())
    manifest = {
        "schema_version": 1,
        "manifest_id": "VISCOND-01-MMStar-bc98d668-v1",
        "source": {
            "repository": "Lin-Chen/MMStar",
            "revision": MMSTAR_REVISION,
            "config": "val",
            "split": "val",
            "parquet_path": str(parquet_path),
            "parquet_bytes": parquet_path.stat().st_size,
            "parquet_sha256": parquet_sha,
        },
        "rows": manifest_rows,
        "rejected_rows": rejected_rows,
    }
    audit = {
        "schema_version": 1,
        "audit_id": "VISCOND-01-round1-MMStar-panel-gate",
        "status": "passed" if passed else "panel_ineligible",
        "eligible_for_scoring": passed,
        "scientific_model_results_accessed": False,
        "model_inference_performed": False,
        "final_confirmation_accessed": False,
        "source": manifest["source"],
        "panel": {
            "row_count": len(manifest_rows),
            "source_row_count": len(rows),
            "rejected_row_count": len(rejected_rows),
            "rejected_rows": rejected_rows,
            "category_counts": dict(sorted(category_counts.items())),
            "l2_category_counts": dict(
                sorted(Counter(row["l2_category"] for row in manifest_rows).items())
            ),
            "answer_counts": dict(
                sorted(Counter(row["answer"] for row in manifest_rows).items())
            ),
            "unique_normalized_pixel_groups": len(group_counts),
            "duplicate_pixel_group_count": sum(
                count > 1 for count in group_counts.values()
            ),
            "maximum_questions_per_pixel_group": max(group_counts.values()),
            "maximum_input_length_unpadded": max(token_lengths),
            "answer_label_token_count_sets": {
                label: sorted(values)
                for label, values in sorted(answer_token_counts.items())
            },
        },
        "checks": checks,
        "interpretation": (
            "The complete official MMStar panel is eligible for the frozen "
            "VISCOND-01 correct-image versus no-pixel prediction test."
            if passed
            else "The official panel failed a preregistered eligibility gate."
        ),
    }
    return manifest, audit


def image_entries(
    items: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    entries = {}
    for item in items:
        path = str(item["image_path"])
        value = {
            "image_path": path,
            "image_sha256": item["image_sha256"],
            "normalized_pixel_sha256": item["normalized_pixel_sha256"],
        }
        if path in entries and entries[path] != value:
            raise ValueError("one image path has inconsistent manifest metadata")
        entries[path] = value
    return entries


def _condition_nll(
    model,
    input_tensor: torch.Tensor,
    label_tensor: torch.Tensor,
    *,
    pixel_values: Any,
    cache=None,
    image_paths: list[str] | None = None,
) -> tuple[list[float], list[int]]:
    context = (
        cache.activate(image_paths)
        if cache is not None and image_paths is not None
        else _NullContext()
    )
    with context, torch.inference_mode():
        result = model(
            input_ids=input_tensor,
            labels=None,
            attention_mask=None,
            pixel_values=pixel_values,
        )
    values = token_nll_bits(result.logits, label_tensor)
    means = [float(row.double().mean().item()) for row in values]
    counts = [int(row.numel()) for row in values]
    if not all(math.isfinite(value) for value in means):
        raise FloatingPointError("non-finite teacher-forced answer NLL")
    del result
    return means, counts


class _NullContext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def score_item_batch(
    model,
    items: Sequence[Mapping[str, Any]],
    *,
    tokenizer,
    device: str,
    feature_cache,
) -> list[dict[str, Any]]:
    if not items:
        raise ValueError("item scoring batch must be nonempty")
    ids = []
    labels = []
    keys = []
    paths = []
    for item_offset, item in enumerate(items):
        for label in ANSWER_LABELS:
            record = build_answer_record(tokenizer, item["question"], label)
            ids.append(record["input_ids"])
            labels.append(record["labels"])
            keys.append((item_offset, label))
            paths.append(str(item["image_path"]))
    input_tensor = torch.stack(ids).to(device)
    label_tensor = torch.stack(labels).to(device)
    correct, correct_counts = _condition_nll(
        model,
        input_tensor,
        label_tensor,
        pixel_values=feature_cache.dummy_pixel_values(len(ids)),
        cache=feature_cache,
        image_paths=paths,
    )
    no_pixel, no_pixel_counts = _condition_nll(
        model,
        input_tensor,
        label_tensor,
        pixel_values=None,
    )
    if correct_counts != no_pixel_counts:
        raise RuntimeError("correct/no-pixel answer token counts differ")

    grids = [
        {"correct": {}, "no_pixel": {}, "token_count": {}}
        for _ in items
    ]
    for key, correct_value, none_value, count in zip(
        keys, correct, no_pixel, correct_counts, strict=True
    ):
        item_offset, label = key
        grids[item_offset]["correct"][label] = correct_value
        grids[item_offset]["no_pixel"][label] = none_value
        grids[item_offset]["token_count"][label] = count

    rows = []
    for item, grid in zip(items, grids, strict=True):
        gold = str(item["answer"])
        correct_margin = answer_margin(grid["correct"], gold)
        none_margin = answer_margin(grid["no_pixel"], gold)
        row = {
            "index": int(item["index"]),
            "category": item["category"],
            "l2_category": item["l2_category"],
            "answer": gold,
            "normalized_pixel_sha256": item["normalized_pixel_sha256"],
            "image_sha256": item["image_sha256"],
            "correct_nll_bits_per_token": grid["correct"],
            "no_pixel_nll_bits_per_token": grid["no_pixel"],
            "answer_label_token_counts": grid["token_count"],
            "correct_margin_bits_per_token": correct_margin,
            "no_pixel_margin_bits_per_token": none_margin,
            "visual_increment_bits_per_token": correct_margin - none_margin,
            "correct_predicted_label": predicted_label(grid["correct"]),
            "no_pixel_predicted_label": predicted_label(grid["no_pixel"]),
            "correct_is_accurate": predicted_label(grid["correct"]) == gold,
            "no_pixel_is_accurate": predicted_label(grid["no_pixel"]) == gold,
            "all_scores_finite": True,
        }
        rows.append(row)
    return rows


def score_rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    return sha256_bytes(canonical_jsonl_bytes(rows))
