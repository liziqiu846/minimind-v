#!/usr/bin/env python3
"""Deterministic, model-free SugarCrepe++ edit-span audit.

This module is deliberately isolated from the frozen Phase 3 runners.  It reads
their prepared JSONL rows and the Stage 2 tokenizer, but it neither imports nor
executes model code.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import random
import re
import statistics
import tempfile
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


AUDIT_VERSION = "phase3-v6-edit-span-audit-v1"
DEFAULT_SEED = 3407
DEFAULT_REVIEW_LIMIT = 30
COCO_FILENAME_RE = re.compile(r"^[0-9]{12}\.jpg$")
LEXEME_RE = re.compile(r"\w+(?:['’\-]\w+)*|[^\w\s]", re.UNICODE)
WORD_RE = re.compile(r"\w+(?:['’\-]\w+)*", re.UNICODE)
SUCCESS_CATEGORIES = frozenset({"direct_metadata", "unique_alignment"})
KNOWN_CATEGORIES = (
    "direct_metadata",
    "unique_alignment",
    "ambiguous_source",
    "complex_edit",
    "tokenization_problem",
    "invalid_sample",
    "non_semantic_edit",
)


def _levenshtein(a: Sequence[Any], b: Sequence[Any]) -> int:
    """Return exact unit-cost Levenshtein distance for arbitrary sequences."""
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for row_index, left in enumerate(a, 1):
        current = [row_index]
        for column_index, right in enumerate(b, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_index] + 1,
                    previous[column_index - 1] + (left != right),
                )
            )
        previous = current
    return previous[-1]


def _normalized(distance: int, left_length: int, right_length: int) -> Fraction:
    return Fraction(distance, max(left_length, right_length, 1))


def _common_edges(left: Sequence[Any], right: Sequence[Any]) -> tuple[int, int]:
    prefix = 0
    while prefix < min(len(left), len(right)) and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    remaining_left = len(left) - prefix
    remaining_right = len(right) - prefix
    while (
        suffix < min(remaining_left, remaining_right)
        and left[len(left) - 1 - suffix] == right[len(right) - 1 - suffix]
    ):
        suffix += 1
    return prefix, suffix


def _middle_span(text: str, prefix: int, suffix: int) -> str:
    end = len(text) - suffix if suffix else len(text)
    return text[prefix:end]


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _semantic_signature(text: str) -> str:
    return "".join(character.casefold() for character in text if character.isalnum())


def _strip_unicode_category(text: str, category_prefix: str) -> str:
    return "".join(
        character
        for character in text
        if not unicodedata.category(character).startswith(category_prefix)
    )


def _tokenizer_call(tokenizer: Any, text: str) -> dict[str, Any]:
    encoded = tokenizer(
        text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    if isinstance(encoded, Mapping):
        ids = encoded.get("input_ids")
        offsets = encoded.get("offset_mapping")
    else:
        ids = getattr(encoded, "input_ids", None)
        offsets = getattr(encoded, "offset_mapping", None)
    if not isinstance(ids, (list, tuple)) or not isinstance(offsets, (list, tuple)):
        raise ValueError("tokenizer did not return input_ids and offset_mapping")
    ids = [int(value) for value in ids]
    offsets = [tuple(int(value) for value in pair) for pair in offsets]
    if len(ids) != len(offsets):
        raise ValueError("tokenizer ID/offset lengths differ")
    previous_end = 0
    for start, end in offsets:
        if start < 0 or end < start or end > len(text) or start < previous_end:
            raise ValueError("tokenizer offsets are invalid or non-monotonic")
        previous_end = end
    decoded = tokenizer.decode(
        ids,
        skip_special_tokens=False,
        clean_up_tokenization_spaces=False,
    )
    if decoded != text:
        raise ValueError("full token sequence does not decode exactly to source text")
    pieces = list(tokenizer.convert_ids_to_tokens(ids))
    if len(pieces) != len(ids):
        raise ValueError("tokenizer piece/ID lengths differ")
    return {"ids": ids, "offsets": offsets, "pieces": pieces, "decoded": decoded}


def _token_span(
    tokenized: Mapping[str, Any], prefix: int, suffix: int, tokenizer: Any
) -> dict[str, Any]:
    ids = list(tokenized["ids"])
    end = len(ids) - suffix if suffix else len(ids)
    span_ids = ids[prefix:end]
    span_offsets = list(tokenized["offsets"])[prefix:end]
    span_pieces = list(tokenized["pieces"])[prefix:end]
    decoded = tokenizer.decode(
        span_ids,
        skip_special_tokens=False,
        clean_up_tokenization_spaces=False,
    )
    character_span = None
    if span_offsets:
        character_span = [span_offsets[0][0], span_offsets[-1][1]]
    return {
        "ids": span_ids,
        "pieces": span_pieces,
        "text": decoded,
        "character_span": character_span,
    }


def _token_alignment(source: str, negative: str, tokenizer: Any) -> dict[str, Any]:
    source_tokens = _tokenizer_call(tokenizer, source)
    negative_tokens = _tokenizer_call(tokenizer, negative)
    token_prefix, token_suffix = _common_edges(
        source_tokens["ids"], negative_tokens["ids"]
    )
    return {
        "source": source_tokens,
        "negative": negative_tokens,
        "prefix_length": token_prefix,
        "suffix_length": token_suffix,
        "source_span": _token_span(source_tokens, token_prefix, token_suffix, tokenizer),
        "negative_span": _token_span(
            negative_tokens, token_prefix, token_suffix, tokenizer
        ),
        "distance": _levenshtein(source_tokens["ids"], negative_tokens["ids"]),
    }


def _covers_character_edit(
    text: str,
    character_interval: Sequence[int],
    token_character_span: Sequence[int] | None,
) -> bool:
    start, end = (int(character_interval[0]), int(character_interval[1]))
    while start < end and text[start].isspace():
        start += 1
    while start < end and text[end - 1].isspace():
        end -= 1
    if start == end:
        return True
    return bool(
        token_character_span
        and int(token_character_span[0]) <= start
        and int(token_character_span[1]) >= end
    )


def _candidate_score(text: str, negative: str, tokenizer: Any) -> dict[str, Any]:
    character_distance = _levenshtein(text, negative)
    character_normalized = _normalized(character_distance, len(text), len(negative))
    result: dict[str, Any] = {
        "character_edit_distance": character_distance,
        "normalized_character_edit_distance": float(character_normalized),
        "normalized_character_edit_distance_fraction": (
            f"{character_normalized.numerator}/{character_normalized.denominator}"
        ),
        "_character_key": (character_normalized, character_distance),
        "tokenization_error": None,
        "token_edit_distance": None,
        "normalized_token_edit_distance": None,
        "normalized_token_edit_distance_fraction": None,
        "_token_key": None,
        "_token_alignment": None,
    }
    try:
        alignment = _token_alignment(text, negative, tokenizer)
        token_distance = alignment["distance"]
        token_normalized = _normalized(
            token_distance,
            len(alignment["source"]["ids"]),
            len(alignment["negative"]["ids"]),
        )
        result.update(
            token_edit_distance=token_distance,
            normalized_token_edit_distance=float(token_normalized),
            normalized_token_edit_distance_fraction=(
                f"{token_normalized.numerator}/{token_normalized.denominator}"
            ),
            _token_key=(token_normalized, token_distance),
            _token_alignment=alignment,
        )
    except Exception as error:  # tokenizer failures are audit evidence, not fatal runs
        result["tokenization_error"] = f"{type(error).__name__}: {error}"
    return result


def _dominates(
    left: tuple[Any, ...], right: tuple[Any, ...]
) -> bool:
    return left <= right and left != right


def _select_source(
    positive_1: str, positive_2: str, negative: str, tokenizer: Any
) -> tuple[str | None, str, list[dict[str, Any]]]:
    candidates = []
    for label, text in (("positive_1", positive_1), ("positive_2", positive_2)):
        score = _candidate_score(text, negative, tokenizer)
        score.update(label=label, text=text)
        candidates.append(score)
    first, second = candidates
    if first["_token_key"] is None or second["_token_key"] is None:
        if _dominates(first["_character_key"], second["_character_key"]):
            return "positive_1", "character_distance_strictly_lower_tokenization_unavailable", candidates
        if _dominates(second["_character_key"], first["_character_key"]):
            return "positive_2", "character_distance_strictly_lower_tokenization_unavailable", candidates
        return None, "character_distance_tie_tokenization_unavailable", candidates
    first_no_worse = (
        first["_character_key"] <= second["_character_key"]
        and first["_token_key"] <= second["_token_key"]
    )
    second_no_worse = (
        second["_character_key"] <= first["_character_key"]
        and second["_token_key"] <= first["_token_key"]
    )
    if first_no_worse and not second_no_worse:
        return "positive_1", "positive_1_pareto_dominates_character_and_token_distance", candidates
    if second_no_worse and not first_no_worse:
        return "positive_2", "positive_2_pareto_dominates_character_and_token_distance", candidates
    if first_no_worse and second_no_worse:
        return None, "equal_character_and_token_distance_scores", candidates
    return None, "character_and_token_distance_rankings_conflict", candidates


def _public_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in candidate.items()
        if not key.startswith("_") and key != "text"
    }


def _edit_blocks(source: str, negative: str) -> dict[str, Any]:
    left = LEXEME_RE.findall(source)
    right = LEXEME_RE.findall(negative)
    opcodes = SequenceMatcher(None, left, right, autojunk=False).get_opcodes()
    changed = [opcode for opcode in opcodes if opcode[0] != "equal"]
    equal_word_count = sum(
        sum(bool(WORD_RE.fullmatch(token)) for token in left[i1:i2])
        for tag, i1, i2, _, _ in opcodes
        if tag == "equal"
    )
    return {
        "source_lexemes": left,
        "negative_lexemes": right,
        "opcodes": [list(opcode) for opcode in opcodes],
        "changed_block_count": len(changed),
        "equal_word_count": equal_word_count,
    }


def _metadata_alignment(
    row: Mapping[str, Any], positive_1: str, positive_2: str, negative: str
) -> tuple[dict[str, Any] | None, str | None]:
    if "edit_metadata" not in row:
        return None, None
    metadata = row.get("edit_metadata")
    if not isinstance(metadata, Mapping):
        return None, "edit_metadata_not_an_object"
    required = {
        "source_positive",
        "positive_start",
        "positive_end",
        "negative_start",
        "negative_end",
    }
    if not required <= set(metadata):
        return None, "edit_metadata_missing_required_fields"
    label = metadata["source_positive"]
    if label not in ("positive_1", "positive_2"):
        return None, "edit_metadata_source_positive_invalid"
    source = positive_1 if label == "positive_1" else positive_2
    bounds = [
        metadata["positive_start"],
        metadata["positive_end"],
        metadata["negative_start"],
        metadata["negative_end"],
    ]
    if any(not isinstance(value, int) or isinstance(value, bool) for value in bounds):
        return None, "edit_metadata_bounds_not_integers"
    positive_start, positive_end, negative_start, negative_end = bounds
    if not (
        0 <= positive_start <= positive_end <= len(source)
        and 0 <= negative_start <= negative_end <= len(negative)
    ):
        return None, "edit_metadata_bounds_out_of_range"
    positive_span = source[positive_start:positive_end]
    negative_span = negative[negative_start:negative_end]
    if source[:positive_start] != negative[:negative_start]:
        return None, "edit_metadata_prefix_mismatch"
    if source[positive_end:] != negative[negative_end:]:
        return None, "edit_metadata_suffix_mismatch"
    return {
        "label": label,
        "source": source,
        "positive_interval": [positive_start, positive_end],
        "negative_interval": [negative_start, negative_end],
        "positive_span": positive_span,
        "negative_span": negative_span,
        "prefix": source[:positive_start],
        "suffix": source[positive_end:],
    }, None


def _empty_result(
    *,
    sample_id: str,
    negative_type: str | None,
    positive_1: Any,
    positive_2: Any,
    negative: Any,
    filename: Any,
    numeric_id: Any,
    reason: str,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "category": "invalid_sample",
        "negative_type": negative_type,
        "filename": filename,
        "numeric_id": numeric_id,
        "positive_1": positive_1,
        "positive_2": positive_2,
        "negative": negative,
        "selected_source_label": None,
        "selected_source_positive": None,
        "source_selection_reason": "invalid_input",
        "source_candidates": [],
        "common_prefix": "",
        "positive_edit_span": "",
        "negative_edit_span": "",
        "common_suffix": "",
        "positive_edit_character_interval": None,
        "negative_edit_character_interval": None,
        "positive_edit_token_ids": [],
        "negative_edit_token_ids": [],
        "positive_edit_tokens": [],
        "negative_edit_tokens": [],
        "positive_edit_token_text": "",
        "negative_edit_token_text": "",
        "positive_edit_token_character_span": None,
        "negative_edit_token_character_span": None,
        "positive_edit_character_count": 0,
        "negative_edit_character_count": 0,
        "positive_edit_word_count": 0,
        "negative_edit_word_count": 0,
        "positive_edit_token_count": 0,
        "negative_edit_token_count": 0,
        "character_edit_distance": None,
        "token_edit_distance": None,
        "edit_block_count": None,
        "edit_opcodes": [],
        "is_source_unique": False,
        "is_unique": False,
        "has_empty_edit_span": False,
        "is_case_only_difference": False,
        "is_punctuation_only_difference": False,
        "is_whitespace_only_difference": False,
        "is_word_order_change": False,
        "token_boundary_mismatch": False,
        "token_boundary_mismatch_reasons": [],
        "tokenization_error": None,
        "failure_reason": reason,
    }


def audit_row(
    row: Mapping[str, Any],
    tokenizer: Any,
    *,
    row_index: int = 0,
    image_status_by_filename: Mapping[str, str] | None = None,
    extra_invalid_reasons: Iterable[str] = (),
) -> dict[str, Any]:
    """Audit one canonical SugarCrepe++ row without consulting model outputs."""
    positive_1 = row.get("caption")
    positive_2 = row.get("caption2")
    negative = row.get("negative_caption")
    negative_type = row.get("category")
    filename = row.get("filename")
    numeric_id = row.get("numeric_id")
    raw_id = row.get("row_key", row.get("sample_id"))
    sample_id = raw_id if isinstance(raw_id, str) and raw_id else f"input_row:{row_index}"
    invalid_reasons = list(extra_invalid_reasons)
    if not isinstance(raw_id, str) or not raw_id:
        invalid_reasons.append("missing_sample_id")
    if not isinstance(negative_type, str) or not negative_type:
        invalid_reasons.append("missing_negative_type")
    if not isinstance(numeric_id, int) or isinstance(numeric_id, bool) or numeric_id < 0:
        invalid_reasons.append("invalid_numeric_id")
    if not isinstance(filename, str) or not COCO_FILENAME_RE.fullmatch(filename):
        invalid_reasons.append("invalid_filename")
    for field_name, value in (
        ("caption", positive_1),
        ("caption2", positive_2),
        ("negative_caption", negative),
    ):
        if not isinstance(value, str):
            invalid_reasons.append(f"missing_or_non_string_{field_name}")
        elif not value:
            invalid_reasons.append(f"empty_{field_name}")
    if image_status_by_filename is not None and isinstance(filename, str):
        status = image_status_by_filename.get(filename)
        if status is None:
            invalid_reasons.append("image_missing_from_manifest")
        elif status != "ready":
            invalid_reasons.append(f"image_status_{status}")
    if invalid_reasons:
        return _empty_result(
            sample_id=sample_id,
            negative_type=negative_type if isinstance(negative_type, str) else None,
            positive_1=positive_1,
            positive_2=positive_2,
            negative=negative,
            filename=filename,
            numeric_id=numeric_id,
            reason=";".join(sorted(set(invalid_reasons))),
        )

    assert isinstance(positive_1, str)
    assert isinstance(positive_2, str)
    assert isinstance(negative, str)
    metadata, metadata_error = _metadata_alignment(
        row, positive_1, positive_2, negative
    )
    if metadata_error:
        return _empty_result(
            sample_id=sample_id,
            negative_type=negative_type,
            positive_1=positive_1,
            positive_2=positive_2,
            negative=negative,
            filename=filename,
            numeric_id=numeric_id,
            reason=metadata_error,
        )

    if metadata is not None:
        selected_label = metadata["label"]
        source = metadata["source"]
        source_reason = "validated_direct_edit_metadata"
        prefix = metadata["prefix"]
        suffix = metadata["suffix"]
        positive_interval = metadata["positive_interval"]
        negative_interval = metadata["negative_interval"]
        positive_span = metadata["positive_span"]
        negative_span = metadata["negative_span"]
        candidate_rows: list[dict[str, Any]] = []
        direct_metadata = True
        source_unique = True
    else:
        selected_label, source_reason, candidate_rows = _select_source(
            positive_1, positive_2, negative, tokenizer
        )
        direct_metadata = False
        source_unique = selected_label is not None
        source = (
            positive_1
            if selected_label == "positive_1"
            else positive_2 if selected_label == "positive_2" else None
        )
        prefix = suffix = positive_span = negative_span = ""
        positive_interval = negative_interval = None

    public_candidates = [_public_candidate(candidate) for candidate in candidate_rows]
    if source is None:
        base = _empty_result(
            sample_id=sample_id,
            negative_type=negative_type,
            positive_1=positive_1,
            positive_2=positive_2,
            negative=negative,
            filename=filename,
            numeric_id=numeric_id,
            reason=source_reason,
        )
        base.update(
            category="ambiguous_source",
            source_selection_reason=source_reason,
            source_candidates=public_candidates,
        )
        return base

    if not direct_metadata:
        prefix_length, suffix_length = _common_edges(source, negative)
        prefix = source[:prefix_length]
        suffix = source[len(source) - suffix_length :] if suffix_length else ""
        positive_span = _middle_span(source, prefix_length, suffix_length)
        negative_span = _middle_span(negative, prefix_length, suffix_length)
        positive_interval = [prefix_length, len(source) - suffix_length]
        negative_interval = [prefix_length, len(negative) - suffix_length]

    character_distance = _levenshtein(source, negative)
    block_info = _edit_blocks(source, negative)
    source_words = [token.casefold() for token in WORD_RE.findall(positive_span)]
    negative_words = [token.casefold() for token in WORD_RE.findall(negative_span)]
    word_order_change = (
        source_words != negative_words
        and len(source_words) > 1
        and Counter(source_words) == Counter(negative_words)
    )
    case_only = source != negative and source.casefold() == negative.casefold()
    punctuation_only = (
        source != negative
        and _strip_unicode_category(source, "P")
        == _strip_unicode_category(negative, "P")
    )
    whitespace_only = (
        source != negative
        and "".join(source.split()) == "".join(negative.split())
    )
    non_semantic = source != negative and _semantic_signature(source) == _semantic_signature(negative)
    empty_edit = not positive_span or not negative_span
    tokenization_error = None
    token_boundary_mismatch_reasons = []
    token_alignment = None
    try:
        token_alignment = _token_alignment(source, negative, tokenizer)
        source_token_span = token_alignment["source_span"]
        negative_token_span = token_alignment["negative_span"]
        if character_distance and not (
            source_token_span["ids"] or negative_token_span["ids"]
        ):
            tokenization_error = "character_edit_has_no_differing_token_span"
        if not _covers_character_edit(
            source, positive_interval, source_token_span["character_span"]
        ):
            token_boundary_mismatch_reasons.append(
                "positive_token_span_does_not_cover_character_edit"
            )
        if not _covers_character_edit(
            negative, negative_interval, negative_token_span["character_span"]
        ):
            token_boundary_mismatch_reasons.append(
                "negative_token_span_does_not_cover_character_edit"
            )
    except Exception as error:
        tokenization_error = f"{type(error).__name__}: {error}"

    if token_alignment is None:
        source_token_span = {"ids": [], "pieces": [], "text": "", "character_span": None}
        negative_token_span = {"ids": [], "pieces": [], "text": "", "character_span": None}
        token_distance = None
    else:
        source_token_span = token_alignment["source_span"]
        negative_token_span = token_alignment["negative_span"]
        token_distance = token_alignment["distance"]

    total_word_count = max(_word_count(source), _word_count(negative), 1)
    max_edit_words = max(_word_count(positive_span), _word_count(negative_span))
    obvious_rewrite = (
        (block_info["equal_word_count"] == 0 and total_word_count >= 5)
        or (max_edit_words >= 8 and Fraction(max_edit_words, total_word_count) >= Fraction(1, 2))
    )
    complex_edit = (
        block_info["changed_block_count"] > 1
        or word_order_change
        or obvious_rewrite
    )

    failure_reason = None
    if source == negative:
        category = "invalid_sample"
        failure_reason = "selected_positive_equals_negative_no_edit"
    elif direct_metadata:
        category = "direct_metadata"
    elif non_semantic:
        category = "non_semantic_edit"
        reasons = []
        if case_only:
            reasons.append("case_only_difference")
        if punctuation_only:
            reasons.append("punctuation_only_difference")
        if whitespace_only:
            reasons.append("whitespace_only_difference")
        failure_reason = ";".join(reasons or ["no_alphanumeric_semantic_difference"])
    elif complex_edit:
        category = "complex_edit"
        reasons = []
        if block_info["changed_block_count"] > 1:
            reasons.append(f"non_contiguous_edit_blocks={block_info['changed_block_count']}")
        if word_order_change:
            reasons.append("word_order_change")
        if obvious_rewrite:
            reasons.append("obvious_rewrite_by_fixed_coverage_rule")
        failure_reason = ";".join(reasons)
    elif tokenization_error:
        category = "tokenization_problem"
        failure_reason = tokenization_error
    else:
        category = "unique_alignment"

    is_unique = category in SUCCESS_CATEGORIES
    return {
        "sample_id": sample_id,
        "category": category,
        "negative_type": negative_type,
        "filename": filename,
        "numeric_id": numeric_id,
        "positive_1": positive_1,
        "positive_2": positive_2,
        "negative": negative,
        "selected_source_label": selected_label,
        "selected_source_positive": source,
        "source_selection_reason": source_reason,
        "source_candidates": public_candidates,
        "common_prefix": prefix,
        "positive_edit_span": positive_span,
        "negative_edit_span": negative_span,
        "common_suffix": suffix,
        "positive_edit_character_interval": positive_interval,
        "negative_edit_character_interval": negative_interval,
        "positive_edit_token_ids": source_token_span["ids"],
        "negative_edit_token_ids": negative_token_span["ids"],
        "positive_edit_tokens": source_token_span["pieces"],
        "negative_edit_tokens": negative_token_span["pieces"],
        "positive_edit_token_text": source_token_span["text"],
        "negative_edit_token_text": negative_token_span["text"],
        "positive_edit_token_character_span": source_token_span["character_span"],
        "negative_edit_token_character_span": negative_token_span["character_span"],
        "positive_edit_character_count": len(positive_span),
        "negative_edit_character_count": len(negative_span),
        "positive_edit_word_count": _word_count(positive_span),
        "negative_edit_word_count": _word_count(negative_span),
        "positive_edit_token_count": len(source_token_span["ids"]),
        "negative_edit_token_count": len(negative_token_span["ids"]),
        "character_edit_distance": character_distance,
        "token_edit_distance": token_distance,
        "edit_block_count": block_info["changed_block_count"],
        "edit_opcodes": block_info["opcodes"],
        "is_source_unique": source_unique,
        "is_unique": is_unique,
        "has_empty_edit_span": empty_edit,
        "is_case_only_difference": case_only,
        "is_punctuation_only_difference": punctuation_only,
        "is_whitespace_only_difference": whitespace_only,
        "is_word_order_change": word_order_change,
        "token_boundary_mismatch": bool(token_boundary_mismatch_reasons),
        "token_boundary_mismatch_reasons": token_boundary_mismatch_reasons,
        "tokenization_error": tokenization_error,
        "failure_reason": failure_reason,
    }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _percentile(values: Sequence[int], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _distribution(values: Sequence[int]) -> dict[str, Any]:
    histogram = Counter()
    for value in values:
        if value <= 5:
            bucket = str(value)
        elif value <= 10:
            bucket = "6-10"
        elif value <= 20:
            bucket = "11-20"
        else:
            bucket = "21+"
        histogram[bucket] += 1
    return {
        "count": len(values),
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "p90": _percentile(values, 0.90),
        "histogram": dict(sorted(histogram.items())),
    }


def _length_distributions(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = {}
    for side in ("positive", "negative"):
        for unit in ("character", "word", "token"):
            key = f"{side}_edit_{unit}_count"
            result[f"{side}_{unit}s"] = _distribution(
                [int(row[key]) for row in rows if row.get(key) is not None]
            )
    return result


def _scope_statistics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    successful = sum(row["category"] in SUCCESS_CATEGORIES for row in rows)
    type_results = {}
    for negative_type in sorted(
        {str(row["negative_type"]) for row in rows if row["negative_type"] is not None}
    ):
        group = [row for row in rows if row["negative_type"] == negative_type]
        type_success = sum(row["category"] in SUCCESS_CATEGORIES for row in group)
        type_results[negative_type] = {
            "total": len(group),
            "successful_unique_recovery_count": type_success,
            "success_rate": _ratio(type_success, len(group)),
        }
    return {
        "sample_count": total,
        "unique_image_count": len({row["filename"] for row in rows}),
        "category_counts": dict(sorted(Counter(row["category"] for row in rows).items())),
        "successful_unique_recovery_count": successful,
        "success_rate": _ratio(successful, total),
        "negative_type_results": type_results,
    }


def _stable_sample(
    rows: Sequence[Mapping[str, Any]], limit: int, seed: int, group: str
) -> list[Mapping[str, Any]]:
    ordered = sorted(rows, key=lambda row: str(row["sample_id"]).encode("utf-8"))
    derived_seed = int.from_bytes(
        hashlib.sha256(f"{seed}:{group}".encode("utf-8")).digest()[:8], "big"
    )
    rng = random.Random(derived_seed)
    if len(ordered) <= limit:
        return ordered
    indices = sorted(rng.sample(range(len(ordered)), limit))
    return [ordered[index] for index in indices]


def _example(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": row["sample_id"],
        "category": row["category"],
        "negative_type": row["negative_type"],
        "selected_source_label": row["selected_source_label"],
        "positive_edit_span": row["positive_edit_span"],
        "negative_edit_span": row["negative_edit_span"],
        "failure_reason": row["failure_reason"],
    }


def build_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    input_path: Path,
    input_sha256: str,
    image_manifest_path: Path,
    image_manifest_sha256: str,
    pilot_filenames_path: Path,
    pilot_filenames_sha256: str,
    formal_filenames_path: Path,
    formal_filenames_sha256: str,
    certifying_formal_filenames_path: Path,
    certifying_formal_filenames_sha256: str,
    tokenizer_path: Path,
    tokenizer_files: Mapping[str, str],
    seed: int,
    observed_input_field_sets: Mapping[str, int],
) -> dict[str, Any]:
    total = len(rows)
    category_counter = Counter(str(row["category"]) for row in rows)
    category_counts = {
        category: {
            "count": category_counter.get(category, 0),
            "proportion": _ratio(category_counter.get(category, 0), total),
        }
        for category in KNOWN_CATEGORIES
    }
    extra_categories = sorted(set(category_counter) - set(KNOWN_CATEGORIES))
    for category in extra_categories:
        category_counts[category] = {
            "count": category_counter[category],
            "proportion": _ratio(category_counter[category], total),
        }
    successful = [row for row in rows if row["category"] in SUCCESS_CATEGORIES]
    selected = [row for row in rows if row.get("selected_source_positive") is not None]
    negative_type_results = {}
    for negative_type in sorted(
        {str(row["negative_type"]) for row in rows if row["negative_type"] is not None}
    ):
        group = [row for row in rows if row["negative_type"] == negative_type]
        group_success = sum(row["category"] in SUCCESS_CATEGORIES for row in group)
        negative_type_results[negative_type] = {
            "total": len(group),
            "successful_unique_recovery_count": group_success,
            "success_rate": _ratio(group_success, len(group)),
            "category_counts": dict(sorted(Counter(row["category"] for row in group).items())),
        }
    multi_token = sum(
        max(row["positive_edit_token_count"], row["negative_edit_token_count"]) > 1
        for row in successful
    )
    empty_fragment = sum(row.get("has_empty_edit_span", False) for row in selected)
    case_only = sum(row.get("is_case_only_difference", False) for row in selected)
    punctuation_only = sum(
        row.get("is_punctuation_only_difference", False) for row in selected
    )
    whitespace_only = sum(
        row.get("is_whitespace_only_difference", False) for row in selected
    )
    token_boundary_mismatch = sum(
        row.get("token_boundary_mismatch", False) for row in selected
    )
    failure_rows = [row for row in rows if row["category"] not in SUCCESS_CATEGORIES]
    representative_success = []
    for negative_type in negative_type_results:
        group = [
            row
            for row in successful
            if row["negative_type"] == negative_type
        ]
        representative_success.extend(
            _example(row)
            for row in _stable_sample(group, 1, seed, f"summary_success:{negative_type}")
        )
    representative_failures = []
    for category in (
        "ambiguous_source",
        "complex_edit",
        "tokenization_problem",
        "invalid_sample",
        "non_semantic_edit",
    ):
        group = [row for row in failure_rows if row["category"] == category]
        representative_failures.extend(
            _example(row)
            for row in _stable_sample(group, 2, seed, f"summary_failure:{category}")
        )
    return {
        "schema_version": 1,
        "audit_version": AUDIT_VERSION,
        "random_seed": seed,
        "success_definition": sorted(SUCCESS_CATEGORIES),
        "provenance": {
            "input_jsonl": str(input_path),
            "input_jsonl_sha256": input_sha256,
            "image_manifest": str(image_manifest_path),
            "image_manifest_sha256": image_manifest_sha256,
            "pilot_filenames": str(pilot_filenames_path),
            "pilot_filenames_sha256": pilot_filenames_sha256,
            "formal_filenames": str(formal_filenames_path),
            "formal_filenames_sha256": formal_filenames_sha256,
            "certifying_formal_filenames": str(certifying_formal_filenames_path),
            "certifying_formal_filenames_sha256": certifying_formal_filenames_sha256,
            "tokenizer_path": str(tokenizer_path),
            "tokenizer_files_sha256": dict(sorted(tokenizer_files.items())),
            "transformers_version": importlib.metadata.version("transformers"),
            "observed_input_field_sets": dict(observed_input_field_sets),
            "model_outputs_consulted": False,
        },
        "deterministic_rules": {
            "source_selection": (
                "select a positive only when its (normalized, raw) character and token "
                "Levenshtein score pairs Pareto-dominate the other positive; ties and "
                "cross-metric conflicts are ambiguous"
            ),
            "character_span": "exact longest common prefix/suffix with a non-overlap constraint",
            "token_span": "exact token-ID longest common prefix/suffix on add_special_tokens=False encodings",
            "complex_edit": (
                "more than one non-equal lexeme opcode, detected word-order change, or "
                "the fixed whole/large rewrite coverage rule"
            ),
            "category_precedence": [
                "invalid_sample",
                "direct_metadata",
                "ambiguous_source",
                "non_semantic_edit",
                "complex_edit",
                "tokenization_problem",
                "unique_alignment",
            ],
        },
        "total_samples": total,
        "category_counts": category_counts,
        "negative_type_results": negative_type_results,
        "scope_results": {
            "canonical_all": _scope_statistics(rows),
            "pilot": _scope_statistics(
                [row for row in rows if row.get("phase3_split") == "pilot"]
            ),
            "formal": _scope_statistics(
                [row for row in rows if row.get("phase3_split") == "formal"]
            ),
            "certifying_formal": _scope_statistics(
                [row for row in rows if row.get("is_certifying_formal") is True]
            ),
        },
        "unique_recovery_count": len(successful),
        "unique_recovery_proportion": _ratio(len(successful), total),
        "multi_token_edit_count": multi_token,
        "multi_token_edit_proportion_of_unique_recoveries": _ratio(
            multi_token, len(successful)
        ),
        "non_contiguous_or_complex_edit_count": category_counter.get("complex_edit", 0),
        "non_contiguous_or_complex_edit_proportion": _ratio(
            category_counter.get("complex_edit", 0), total
        ),
        "ambiguous_source_count": category_counter.get("ambiguous_source", 0),
        "ambiguous_source_proportion": _ratio(
            category_counter.get("ambiguous_source", 0), total
        ),
        "tokenizer_alignment_failure_count": category_counter.get(
            "tokenization_problem", 0
        ),
        "tokenizer_alignment_failure_proportion": _ratio(
            category_counter.get("tokenization_problem", 0), total
        ),
        "token_boundary_mismatch_count": token_boundary_mismatch,
        "token_boundary_mismatch_proportion_of_selected_sources": _ratio(
            token_boundary_mismatch, len(selected)
        ),
        "empty_edit_fragment_count": empty_fragment,
        "empty_edit_fragment_proportion_of_selected_sources": _ratio(
            empty_fragment, len(selected)
        ),
        "case_only_difference_count": case_only,
        "punctuation_only_difference_count": punctuation_only,
        "whitespace_only_difference_count": whitespace_only,
        "edit_length_distributions": {
            "all_selected_sources": _length_distributions(selected),
            "unique_recoveries": _length_distributions(successful),
        },
        "representative_examples": {
            "successes": representative_success,
            "failures": representative_failures,
        },
    }


def _markdown_sample(row: Mapping[str, Any], number: int) -> list[str]:
    def rendered(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    return [
        f"### {number}. `{row['sample_id']}`",
        "",
        f"- 负例类型：`{row['negative_type']}`",
        f"- 阶段三范围：`{row.get('phase3_split')}`；certifying formal：`{row.get('is_certifying_formal')}`",
        f"- 正描述 1：{rendered(row['positive_1'])}",
        f"- 正描述 2：{rendered(row['positive_2'])}",
        f"- 负描述：{rendered(row['negative'])}",
        f"- 自动来源：`{row['selected_source_label']}` / {rendered(row['selected_source_positive'])}",
        f"- 正确片段：{rendered(row['positive_edit_span'])}",
        f"- 错误片段：{rendered(row['negative_edit_span'])}",
        (
            "- 正确片段 token："
            f"IDs `{rendered(row['positive_edit_token_ids'])}`；"
            f"pieces `{rendered(row['positive_edit_tokens'])}`；"
            f"decode {rendered(row['positive_edit_token_text'])}"
        ),
        (
            "- 错误片段 token："
            f"IDs `{rendered(row['negative_edit_token_ids'])}`；"
            f"pieces `{rendered(row['negative_edit_tokens'])}`；"
            f"decode {rendered(row['negative_edit_token_text'])}"
        ),
        f"- 自动分类：`{row['category']}`",
        f"- 来源规则：{rendered(row['source_selection_reason'])}",
        f"- 失败原因：{rendered(row['failure_reason'])}",
        f"- Token 边界提示：{rendered(row['token_boundary_mismatch_reasons'])}",
        "",
    ]


def build_manual_review(
    rows: Sequence[Mapping[str, Any]], *, seed: int, limit: int
) -> str:
    groups: list[tuple[str, str, list[Mapping[str, Any]]]] = [
        (
            "success_recovery",
            "成功恢复",
            [row for row in rows if row["category"] in SUCCESS_CATEGORIES],
        ),
        (
            "ambiguous_source",
            "来源不唯一",
            [row for row in rows if row["category"] == "ambiguous_source"],
        ),
        (
            "complex_edit",
            "复杂编辑",
            [row for row in rows if row["category"] == "complex_edit"],
        ),
        (
            "tokenization_problem",
            "Tokenizer 问题",
            [row for row in rows if row["category"] == "tokenization_problem"],
        ),
    ]
    negative_types = sorted(
        {str(row["negative_type"]) for row in rows if row["negative_type"] is not None}
    )
    groups.extend(
        (
            f"negative_type:{negative_type}",
            f"负例类型：{negative_type}",
            [row for row in rows if row["negative_type"] == negative_type],
        )
        for negative_type in negative_types
    )
    lines = [
        "# SugarCrepe++ 编辑片段自动审计抽查材料",
        "",
        "本文件仅供后续人工审核；以下样本尚未经过人工验证。",
        "",
        f"固定随机种子：`{seed}`；每个分组最多抽取 `{limit}` 条。不同分组可重复出现同一样本。",
        "",
    ]
    for group_key, title, candidates in groups:
        sampled = _stable_sample(candidates, limit, seed, group_key)
        lines.extend(
            [
                f"## {title}",
                "",
                f"候选 `{len(candidates)}` 条，本节抽取 `{len(sampled)}` 条。",
                "",
            ]
        )
        if not sampled:
            lines.extend(["本类别没有可抽取样本。", ""])
        for index, row in enumerate(sampled, 1):
            lines.extend(_markdown_sample(row, index))
    return "\n".join(lines).rstrip() + "\n"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {error}") from error
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row is not an object at {path}:{line_number}")
            rows.append(value)
    return rows


def _read_filename_list(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    values = raw.splitlines()
    if not values or raw != "\n".join(values) + "\n":
        raise ValueError(f"filename list is empty or non-canonical: {path}")
    if values != sorted(set(values), key=lambda value: value.encode("utf-8")):
        raise ValueError(f"filename list is not sorted and unique: {path}")
    if any(not COCO_FILENAME_RE.fullmatch(value) for value in values):
        raise ValueError(f"filename list contains an invalid COCO name: {path}")
    return values


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
    temporary.chmod(0o644)
    temporary.replace(path)


def _tokenizer_hashes(path: Path) -> dict[str, str]:
    result = {}
    for name in ("tokenizer.json", "tokenizer_config.json"):
        candidate = path / name
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        result[name] = _sha256(candidate)
    return result


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    from transformers import AutoTokenizer

    input_path = args.input_jsonl.resolve()
    image_manifest_path = args.image_manifest.resolve()
    pilot_filenames_path = args.pilot_filenames.resolve()
    formal_filenames_path = args.formal_filenames.resolve()
    certifying_formal_filenames_path = args.certifying_formal_filenames.resolve()
    tokenizer_path = args.tokenizer.resolve()
    output_dir = args.output_dir.resolve()
    input_sha256 = _sha256(input_path)
    if args.expected_input_sha256 and input_sha256 != args.expected_input_sha256:
        raise ValueError(
            f"input SHA-256 mismatch: expected {args.expected_input_sha256}, got {input_sha256}"
        )
    input_rows = _read_jsonl(input_path)
    image_rows = _read_jsonl(image_manifest_path)
    pilot_filenames = _read_filename_list(pilot_filenames_path)
    formal_filenames = _read_filename_list(formal_filenames_path)
    certifying_formal_filenames = _read_filename_list(certifying_formal_filenames_path)
    pilot_set = set(pilot_filenames)
    formal_set = set(formal_filenames)
    certifying_set = set(certifying_formal_filenames)
    canonical_filenames = {
        row.get("filename") for row in input_rows if isinstance(row.get("filename"), str)
    }
    if pilot_set & formal_set or pilot_set | formal_set != canonical_filenames:
        raise ValueError("pilot/formal filename lists do not partition canonical input rows")
    if not certifying_set <= formal_set:
        raise ValueError("certifying formal filenames are not a formal subset")
    image_status = {
        row["filename"]: row.get("status")
        for row in image_rows
        if isinstance(row.get("filename"), str)
    }
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("the project tokenizer must expose fast offset mappings")

    row_keys = [row.get("row_key") for row in input_rows]
    duplicate_keys = {
        key for key, count in Counter(row_keys).items() if key is not None and count > 1
    }
    results = []
    for row_index, row in enumerate(input_rows):
        extra = ["duplicate_sample_id"] if row.get("row_key") in duplicate_keys else []
        audited = audit_row(
            row,
            tokenizer,
            row_index=row_index,
            image_status_by_filename=image_status,
            extra_invalid_reasons=extra,
        )
        filename = row.get("filename")
        audited["phase3_split"] = (
            "pilot" if filename in pilot_set else "formal" if filename in formal_set else None
        )
        audited["is_certifying_formal"] = filename in certifying_set
        results.append(audited)
    field_sets = Counter(
        ",".join(sorted(str(key) for key in row.keys())) for row in input_rows
    )
    summary = build_summary(
        results,
        input_path=input_path,
        input_sha256=input_sha256,
        image_manifest_path=image_manifest_path,
        image_manifest_sha256=_sha256(image_manifest_path),
        pilot_filenames_path=pilot_filenames_path,
        pilot_filenames_sha256=_sha256(pilot_filenames_path),
        formal_filenames_path=formal_filenames_path,
        formal_filenames_sha256=_sha256(formal_filenames_path),
        certifying_formal_filenames_path=certifying_formal_filenames_path,
        certifying_formal_filenames_sha256=_sha256(certifying_formal_filenames_path),
        tokenizer_path=tokenizer_path,
        tokenizer_files=_tokenizer_hashes(tokenizer_path),
        seed=args.seed,
        observed_input_field_sets=field_sets,
    )
    jsonl_payload = b"".join(
        (
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        for row in results
    )
    summary_payload = (
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    review_payload = build_manual_review(
        results, seed=args.seed, limit=args.review_limit
    ).encode("utf-8")
    _atomic_write(output_dir / "edit_span_audit.jsonl", jsonl_payload)
    _atomic_write(output_dir / "edit_span_summary.json", summary_payload)
    _atomic_write(output_dir / "manual_review_samples.md", review_payload)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--image-manifest", type=Path, required=True)
    parser.add_argument("--pilot-filenames", type=Path, required=True)
    parser.add_argument("--formal-filenames", type=Path, required=True)
    parser.add_argument("--certifying-formal-filenames", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument("--expected-input-sha256")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--review-limit", type=int, default=DEFAULT_REVIEW_LIMIT, choices=range(1, 31)
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = run_audit(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
