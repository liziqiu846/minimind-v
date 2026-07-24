#!/usr/bin/env python3
"""Model-free Phase 3 v6 contrast-hull structure audit.

The audit independently reads canonical SugarCrepe++ text.  Alignment views are
used only for deterministic structure discovery and never overwrite source text.
No model implementation or model output is imported.
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
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


AUDIT_VERSION = "phase3-v6-contrast-hull-audit-v2"
RANDOM_SEED = 3407
REVIEW_LIMIT = 30
COCO_FILENAME_RE = re.compile(r"^[0-9]{12}\.jpg$")
TERMINAL_PUNCTUATION_RE = re.compile(r"[.!?]+$")
LEXEME_RE = re.compile(
    r"(?:[^\W\d_]\.){2,}"
    r"|\d+(?:[.,]\d+)*"
    r"|[^\W\d_]+(?:[-'’][^\W\d_]+)*"
    r"|_"
    r"|[^\w\s]",
    re.UNICODE,
)
REPLACE_TYPES = frozenset({"replace_attribute", "replace_object", "replace_relation"})
SWAP_TYPES = frozenset({"swap_atribute", "swap_object"})
SECOND_ROUND_CATEGORIES = (
    "one_block_local",
    "multi_block_local_hull",
    "medium_contrast_hull",
    "large_contrast_hull",
    "whole_sentence_hull",
    "equivalent_positive_sources",
    "ambiguous_comparison_positive",
    "surface_only_or_degenerate",
    "token_mapping_problem",
    "invalid_sample",
)


def levenshtein_distance(left: Sequence[Any], right: Sequence[Any]) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for row_index, left_value in enumerate(left, 1):
        current = [row_index]
        for column_index, right_value in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_index] + 1,
                    previous[column_index - 1] + (left_value != right_value),
                )
            )
        previous = current
    return previous[-1]


def _normalized(distance: int, left_length: int, right_length: int) -> Fraction:
    return Fraction(distance, max(left_length, right_length, 1))


def _original_clusters(text: str) -> list[tuple[str, int, int]]:
    clusters = []
    index = 0
    while index < len(text):
        start = index
        index += 1
        while index < len(text) and unicodedata.combining(text[index]):
            index += 1
        clusters.append((text[start:index], start, index))
    return clusters


def build_alignment_view(original_text: str) -> dict[str, Any]:
    """Build a case-insensitive NFKC lexeme view with original offsets.

    Terminal .!? punctuation is retained in a separate surface field and omitted
    from edit alignment.  Every normalized character remains mapped to the
    original cluster that produced it.
    """
    mapped: list[tuple[str, int, int]] = []
    for cluster, original_start, original_end in _original_clusters(original_text):
        normalized_cluster = unicodedata.normalize("NFKC", cluster)
        for character in normalized_cluster:
            for folded in character.casefold():
                mapped.append((folded, original_start, original_end))

    first = 0
    while first < len(mapped) and mapped[first][0].isspace():
        first += 1
    last = len(mapped)
    while last > first and mapped[last - 1][0].isspace():
        last -= 1
    trimmed = mapped[first:last]
    collapsed: list[tuple[str, int, int]] = []
    cursor = 0
    while cursor < len(trimmed):
        character, start, end = trimmed[cursor]
        if not character.isspace():
            collapsed.append((character, start, end))
            cursor += 1
            continue
        whitespace_end = end
        cursor += 1
        while cursor < len(trimmed) and trimmed[cursor][0].isspace():
            whitespace_end = trimmed[cursor][2]
            cursor += 1
        collapsed.append((" ", start, whitespace_end))

    collapsed_text = "".join(character for character, _, _ in collapsed)
    terminal_match = TERMINAL_PUNCTUATION_RE.search(collapsed_text)
    terminal_punctuation = terminal_match.group(0) if terminal_match else ""
    alignment_source_end = terminal_match.start() if terminal_match else len(collapsed_text)
    while alignment_source_end > 0 and collapsed_text[alignment_source_end - 1].isspace():
        alignment_source_end -= 1
    body_text = collapsed_text[:alignment_source_end]
    lexemes = []
    kinds = []
    original_offsets = []
    for match in LEXEME_RE.finditer(body_text):
        token = match.group(0)
        source_mapping = collapsed[match.start() : match.end()]
        if not source_mapping:
            raise AssertionError("lexeme lacks original-character mapping")
        lexemes.append(token)
        if re.fullmatch(r"(?:[^\W\d_]\.){2,}", token, re.UNICODE):
            kind = "abbreviation"
        elif re.fullmatch(r"\d+(?:[.,]\d+)*", token):
            kind = "number"
        elif re.fullmatch(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", token, re.UNICODE):
            kind = "word"
        else:
            kind = "punctuation"
        kinds.append(kind)
        original_offsets.append(
            [
                min(item[1] for item in source_mapping),
                max(item[2] for item in source_mapping),
            ]
        )

    alignment_spans = []
    alignment_cursor = 0
    for token in lexemes:
        start = alignment_cursor
        alignment_cursor += len(token)
        alignment_spans.append([start, alignment_cursor])
        alignment_cursor += 1
    alignment_text = " ".join(lexemes)
    return {
        "original_text": original_text,
        "alignment_text": alignment_text,
        "alignment_lexemes": lexemes,
        "alignment_lexeme_kinds": kinds,
        "original_character_offsets": original_offsets,
        "alignment_character_offsets": alignment_spans,
        "terminal_punctuation": terminal_punctuation,
        "normalization": {
            "unicode": "NFKC",
            "case": "casefold",
            "edge_whitespace": "removed",
            "internal_whitespace": "collapsed_to_ascii_space",
            "terminal_dot_exclamation_question": "separated_and_excluded_from_alignment",
        },
    }


def deterministic_edit_script(
    positive_lexemes: Sequence[str], negative_lexemes: Sequence[str]
) -> tuple[int, list[dict[str, Any]]]:
    """Exact Wagner-Fischer edit script with replace > delete > insert ties."""
    rows, columns = len(positive_lexemes) + 1, len(negative_lexemes) + 1
    costs = [[0] * columns for _ in range(rows)]
    actions: list[list[str | None]] = [[None] * columns for _ in range(rows)]
    for i in range(1, rows):
        costs[i][0] = i
        actions[i][0] = "delete"
    for j in range(1, columns):
        costs[0][j] = j
        actions[0][j] = "insert"
    priority = {"replace": 0, "delete": 1, "insert": 2}
    for i in range(1, rows):
        for j in range(1, columns):
            if positive_lexemes[i - 1] == negative_lexemes[j - 1]:
                costs[i][j] = costs[i - 1][j - 1]
                actions[i][j] = "equal"
                continue
            candidates = [
                (costs[i - 1][j - 1] + 1, priority["replace"], "replace"),
                (costs[i - 1][j] + 1, priority["delete"], "delete"),
                (costs[i][j - 1] + 1, priority["insert"], "insert"),
            ]
            cost, _, action = min(candidates)
            costs[i][j] = cost
            actions[i][j] = action

    individual = []
    i, j = len(positive_lexemes), len(negative_lexemes)
    while i or j:
        action = actions[i][j]
        if action in ("equal", "replace"):
            individual.append(
                {
                    "tag": action,
                    "positive_start": i - 1,
                    "positive_end": i,
                    "negative_start": j - 1,
                    "negative_end": j,
                }
            )
            i -= 1
            j -= 1
        elif action == "delete":
            individual.append(
                {
                    "tag": action,
                    "positive_start": i - 1,
                    "positive_end": i,
                    "negative_start": j,
                    "negative_end": j,
                }
            )
            i -= 1
        elif action == "insert":
            individual.append(
                {
                    "tag": action,
                    "positive_start": i,
                    "positive_end": i,
                    "negative_start": j - 1,
                    "negative_end": j,
                }
            )
            j -= 1
        else:
            raise AssertionError(f"missing traceback action at {(i, j)}")
    individual.reverse()

    blocks: list[dict[str, Any]] = []
    for operation in individual:
        if (
            blocks
            and blocks[-1]["tag"] == operation["tag"]
            and blocks[-1]["positive_end"] == operation["positive_start"]
            and blocks[-1]["negative_end"] == operation["negative_start"]
        ):
            blocks[-1]["positive_end"] = operation["positive_end"]
            blocks[-1]["negative_end"] = operation["negative_end"]
        else:
            blocks.append(dict(operation))
    for block in blocks:
        block["positive_lexemes"] = list(
            positive_lexemes[block["positive_start"] : block["positive_end"]]
        )
        block["negative_lexemes"] = list(
            negative_lexemes[block["negative_start"] : block["negative_end"]]
        )
    return costs[-1][-1], blocks


def build_contrast_hull(
    positive_lexemes: Sequence[str],
    negative_lexemes: Sequence[str],
    edit_opcodes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    non_equal_indices = [
        index for index, block in enumerate(edit_opcodes) if block["tag"] != "equal"
    ]
    if not non_equal_indices:
        return {
            "positive_start": len(positive_lexemes),
            "positive_end": len(positive_lexemes),
            "negative_start": len(negative_lexemes),
            "negative_end": len(negative_lexemes),
            "common_prefix_lexemes": list(positive_lexemes),
            "positive_hull_lexemes": [],
            "negative_hull_lexemes": [],
            "common_suffix_lexemes": [],
            "non_equal_block_count": 0,
            "maximum_equal_bridge_length": 0,
        }
    first_index, last_index = non_equal_indices[0], non_equal_indices[-1]
    first, last = edit_opcodes[first_index], edit_opcodes[last_index]
    positive_start, positive_end = first["positive_start"], last["positive_end"]
    negative_start, negative_end = first["negative_start"], last["negative_end"]
    bridges = [
        block["positive_end"] - block["positive_start"]
        for block in edit_opcodes[first_index + 1 : last_index]
        if block["tag"] == "equal"
    ]
    result = {
        "positive_start": positive_start,
        "positive_end": positive_end,
        "negative_start": negative_start,
        "negative_end": negative_end,
        "common_prefix_lexemes": list(positive_lexemes[:positive_start]),
        "positive_hull_lexemes": list(positive_lexemes[positive_start:positive_end]),
        "negative_hull_lexemes": list(negative_lexemes[negative_start:negative_end]),
        "common_suffix_lexemes": list(positive_lexemes[positive_end:]),
        "non_equal_block_count": len(non_equal_indices),
        "maximum_equal_bridge_length": max(bridges, default=0),
    }
    if result["common_prefix_lexemes"] != list(negative_lexemes[:negative_start]):
        raise AssertionError("positive/negative common prefixes differ")
    if result["common_suffix_lexemes"] != list(negative_lexemes[negative_end:]):
        raise AssertionError("positive/negative common suffixes differ")
    positive_rebuilt = (
        result["common_prefix_lexemes"]
        + result["positive_hull_lexemes"]
        + result["common_suffix_lexemes"]
    )
    negative_rebuilt = (
        result["common_prefix_lexemes"]
        + result["negative_hull_lexemes"]
        + result["common_suffix_lexemes"]
    )
    if positive_rebuilt != list(positive_lexemes) or negative_rebuilt != list(
        negative_lexemes
    ):
        raise AssertionError("contrast hull does not reconstruct normalized inputs")
    return result


def _comparison_candidate(
    positive_view: Mapping[str, Any], negative_view: Mapping[str, Any]
) -> dict[str, Any]:
    positive_lexemes = positive_view["alignment_lexemes"]
    negative_lexemes = negative_view["alignment_lexemes"]
    distance, opcodes = deterministic_edit_script(positive_lexemes, negative_lexemes)
    hull = build_contrast_hull(positive_lexemes, negative_lexemes, opcodes)
    edited_lexeme_count = sum(
        (block["positive_end"] - block["positive_start"])
        + (block["negative_end"] - block["negative_start"])
        for block in opcodes
        if block["tag"] != "equal"
    )
    hull_total = len(hull["positive_hull_lexemes"]) + len(
        hull["negative_hull_lexemes"]
    )
    normalized_lexeme = _normalized(
        distance, len(positive_lexemes), len(negative_lexemes)
    )
    character_distance = levenshtein_distance(
        positive_view["alignment_text"], negative_view["alignment_text"]
    )
    normalized_character = _normalized(
        character_distance,
        len(positive_view["alignment_text"]),
        len(negative_view["alignment_text"]),
    )
    internal_tuple = (
        edited_lexeme_count,
        hull_total,
        hull["non_equal_block_count"],
        normalized_lexeme,
        normalized_character,
    )
    return {
        "edit_distance": distance,
        "character_edit_distance": character_distance,
        "edit_opcodes": opcodes,
        "hull": hull,
        "selection_tuple": [
            edited_lexeme_count,
            hull_total,
            hull["non_equal_block_count"],
            float(normalized_lexeme),
            float(normalized_character),
        ],
        "selection_tuple_exact": [
            edited_lexeme_count,
            hull_total,
            hull["non_equal_block_count"],
            f"{normalized_lexeme.numerator}/{normalized_lexeme.denominator}",
            f"{normalized_character.numerator}/{normalized_character.denominator}",
        ],
        "_selection_tuple": internal_tuple,
    }


def select_comparison_positive(
    positive_1_view: Mapping[str, Any],
    positive_2_view: Mapping[str, Any],
    negative_view: Mapping[str, Any],
) -> dict[str, Any]:
    first = _comparison_candidate(positive_1_view, negative_view)
    second = _comparison_candidate(positive_2_view, negative_view)
    if first["_selection_tuple"] < second["_selection_tuple"]:
        label = "positive_1"
        reason = "positive_1_selection_tuple_lexicographically_smaller"
        ambiguous = False
        equivalent = False
    elif second["_selection_tuple"] < first["_selection_tuple"]:
        label = "positive_2"
        reason = "positive_2_selection_tuple_lexicographically_smaller"
        ambiguous = False
        equivalent = False
    else:
        equivalent = (
            positive_1_view["alignment_lexemes"]
            == positive_2_view["alignment_lexemes"]
        )
        if equivalent:
            label = "positive_1"
            reason = "equal_tuples_equivalent_alignment_views_choose_positive_1"
            ambiguous = False
        else:
            label = None
            reason = "equal_selection_tuples_distinct_alignment_views"
            ambiguous = True
    return {
        "selected_label": label,
        "reason": reason,
        "ambiguous": ambiguous,
        "equivalent": equivalent,
        "positive_1": first,
        "positive_2": second,
    }


def _tokenize_alignment(tokenizer: Any, text: str) -> dict[str, Any]:
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    ids = encoded.get("input_ids") if isinstance(encoded, Mapping) else encoded.input_ids
    offsets = (
        encoded.get("offset_mapping")
        if isinstance(encoded, Mapping)
        else encoded.offset_mapping
    )
    if not isinstance(ids, (list, tuple)) or not isinstance(offsets, (list, tuple)):
        raise ValueError("tokenizer lacks input_ids or offset_mapping")
    ids = [int(value) for value in ids]
    offsets = [[int(pair[0]), int(pair[1])] for pair in offsets]
    if len(ids) != len(offsets):
        raise ValueError("token ID and offset counts differ")
    previous_end = 0
    for start, end in offsets:
        if start < previous_end or end < start or end > len(text):
            raise ValueError("token offsets are invalid or non-monotonic")
        previous_end = end
    decoded = tokenizer.decode(
        ids, skip_special_tokens=False, clean_up_tokenization_spaces=False
    )
    if decoded != text:
        raise ValueError("full tokenizer decode differs from alignment text")
    return {"ids": ids, "offsets": offsets, "text": text}


def _hull_character_interval(
    view: Mapping[str, Any], lexeme_start: int, lexeme_end: int
) -> list[int]:
    spans = view["alignment_character_offsets"]
    if lexeme_start == lexeme_end:
        boundary = spans[lexeme_start][0] if lexeme_start < len(spans) else len(
            view["alignment_text"]
        )
        return [boundary, boundary]
    return [spans[lexeme_start][0], spans[lexeme_end - 1][1]]


def _common_token_edges(
    positive_ids: Sequence[int], negative_ids: Sequence[int]
) -> tuple[int, int]:
    prefix_count = 0
    maximum_prefix = min(len(positive_ids), len(negative_ids))
    while (
        prefix_count < maximum_prefix
        and positive_ids[prefix_count] == negative_ids[prefix_count]
    ):
        prefix_count += 1

    suffix_count = 0
    maximum_suffix = min(
        len(positive_ids) - prefix_count,
        len(negative_ids) - prefix_count,
    )
    while (
        suffix_count < maximum_suffix
        and positive_ids[len(positive_ids) - suffix_count - 1]
        == negative_ids[len(negative_ids) - suffix_count - 1]
    ):
        suffix_count += 1
    return prefix_count, suffix_count


def _covering_token_span(
    tokenized: Mapping[str, Any], character_interval: Sequence[int]
) -> tuple[int, int] | None:
    character_start, character_end = character_interval
    if character_start == character_end:
        return None
    overlapping = [
        index
        for index, (start, end) in enumerate(tokenized["offsets"])
        if start < character_end and end > character_start
    ]
    if not overlapping:
        return None
    return overlapping[0], overlapping[-1] + 1


def _mapped_token_side(
    tokenizer: Any,
    tokenized: Mapping[str, Any],
    view: Mapping[str, Any],
    lexeme_start: int,
    lexeme_end: int,
    token_start: int,
    token_end: int,
) -> dict[str, Any]:
    character_start, character_end = _hull_character_interval(
        view, lexeme_start, lexeme_end
    )
    hull_ids = tokenized["ids"][token_start:token_end]
    hull_offsets = tokenized["offsets"][token_start:token_end]
    if hull_offsets:
        mapped_start, mapped_end = hull_offsets[0][0], hull_offsets[-1][1]
    else:
        mapped_start = mapped_end = character_start
    coverage_ok = (
        lexeme_start < lexeme_end
        and bool(hull_offsets)
        and mapped_start <= character_start
        and mapped_end >= character_end
    )
    if coverage_ok:
        expansion = (
            view["alignment_text"][mapped_start:character_start]
            + view["alignment_text"][character_end:mapped_end]
        )
    else:
        expansion = ""
    return {
        "full_ids": tokenized["ids"],
        "full_offsets": tokenized["offsets"],
        "token_start": token_start,
        "token_end": token_end,
        "hull_ids": hull_ids,
        "hull_text": tokenizer.decode(
            hull_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False
        ),
        "prefix_ids": tokenized["ids"][:token_start],
        "suffix_ids": tokenized["ids"][token_end:],
        "character_interval": [character_start, character_end],
        "token_character_interval": [mapped_start, mapped_end],
        "lexeme_coverage_ok": coverage_ok,
        "token_boundary_ok": coverage_ok,
        "boundary_expansion_text": expansion,
    }


def map_contrast_hull_to_tokenizer(
    tokenizer: Any,
    positive_view: Mapping[str, Any],
    negative_view: Mapping[str, Any],
    hull: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        positive_tokenized = _tokenize_alignment(
            tokenizer, positive_view["alignment_text"]
        )
        negative_tokenized = _tokenize_alignment(
            tokenizer, negative_view["alignment_text"]
        )
        prefix_count, suffix_count = _common_token_edges(
            positive_tokenized["ids"], negative_tokenized["ids"]
        )
        positive_character_interval = _hull_character_interval(
            positive_view, hull["positive_start"], hull["positive_end"]
        )
        negative_character_interval = _hull_character_interval(
            negative_view, hull["negative_start"], hull["negative_end"]
        )
        positive_cover = _covering_token_span(
            positive_tokenized, positive_character_interval
        )
        negative_cover = _covering_token_span(
            negative_tokenized, negative_character_interval
        )
        if positive_cover is not None:
            prefix_count = min(prefix_count, positive_cover[0])
            suffix_count = min(
                suffix_count,
                len(positive_tokenized["ids"]) - positive_cover[1],
            )
        if negative_cover is not None:
            prefix_count = min(prefix_count, negative_cover[0])
            suffix_count = min(
                suffix_count,
                len(negative_tokenized["ids"]) - negative_cover[1],
            )
        positive = _mapped_token_side(
            tokenizer,
            positive_tokenized,
            positive_view,
            hull["positive_start"],
            hull["positive_end"],
            prefix_count,
            len(positive_tokenized["ids"]) - suffix_count,
        )
        negative = _mapped_token_side(
            tokenizer,
            negative_tokenized,
            negative_view,
            hull["negative_start"],
            hull["negative_end"],
            prefix_count,
            len(negative_tokenized["ids"]) - suffix_count,
        )
    except Exception as error:
        return {
            "ok": False,
            "error": f"{type(error).__name__}: {error}",
            "positive": None,
            "negative": None,
            "common_prefix_ids": [],
            "common_suffix_ids": [],
            "can_score_from_common_prefix": False,
        }
    prefix_equal = positive["prefix_ids"] == negative["prefix_ids"]
    suffix_equal = positive["suffix_ids"] == negative["suffix_ids"]
    positive_reconstruction = (
        positive["prefix_ids"] + positive["hull_ids"] + positive["suffix_ids"]
        == positive["full_ids"]
    )
    negative_reconstruction = (
        negative["prefix_ids"] + negative["hull_ids"] + negative["suffix_ids"]
        == negative["full_ids"]
    )
    both_score_tokens = bool(positive["hull_ids"] and negative["hull_ids"])
    ok = (
        positive["token_boundary_ok"]
        and negative["token_boundary_ok"]
        and prefix_equal
        and suffix_equal
        and positive_reconstruction
        and negative_reconstruction
        and both_score_tokens
    )
    errors = []
    if not positive["token_boundary_ok"]:
        errors.append("positive_hull_not_mappable_to_token_boundaries")
    if not negative["token_boundary_ok"]:
        errors.append("negative_hull_not_mappable_to_token_boundaries")
    if not prefix_equal:
        errors.append("common_prefix_token_ids_differ")
    if not suffix_equal:
        errors.append("common_suffix_token_ids_differ")
    if not both_score_tokens:
        errors.append("one_or_both_hulls_have_no_scorable_token")
    if not positive_reconstruction or not negative_reconstruction:
        errors.append("token_reconstruction_failed")
    return {
        "ok": ok,
        "error": ";".join(errors) if errors else None,
        "positive": positive,
        "negative": negative,
        "common_prefix_ids": positive["prefix_ids"] if prefix_equal else [],
        "common_suffix_ids": positive["suffix_ids"] if suffix_equal else [],
        "can_score_from_common_prefix": ok,
    }


def _surface_artifact_flags(positive: str, negative: str) -> list[str]:
    flags = []
    positive_stripped, negative_stripped = positive.strip(), negative.strip()
    if positive != positive_stripped or negative != negative_stripped:
        flags.append("edge_whitespace")
    positive_terminal = TERMINAL_PUNCTUATION_RE.search(positive_stripped)
    negative_terminal = TERMINAL_PUNCTUATION_RE.search(negative_stripped)
    if (positive_terminal.group(0) if positive_terminal else "") != (
        negative_terminal.group(0) if negative_terminal else ""
    ):
        flags.append("terminal_punctuation")
    positive_body = TERMINAL_PUNCTUATION_RE.sub("", positive_stripped).lstrip()
    negative_body = TERMINAL_PUNCTUATION_RE.sub("", negative_stripped).lstrip()
    if (
        positive_body
        and negative_body
        and positive_body[0] != negative_body[0]
        and positive_body[0].casefold() == negative_body[0].casefold()
    ):
        flags.append("initial_case")
    return flags


def _counter_delta(
    positive_lexemes: Sequence[str], negative_lexemes: Sequence[str]
) -> dict[str, Any]:
    positive, negative = Counter(positive_lexemes), Counter(negative_lexemes)
    added = {key: negative[key] - positive[key] for key in negative if negative[key] > positive[key]}
    removed = {key: positive[key] - negative[key] for key in positive if positive[key] > negative[key]}
    quantity_changes = {
        key: {"positive": positive[key], "negative": negative[key]}
        for key in sorted(set(positive) & set(negative))
        if positive[key] != negative[key]
    }
    return {
        "equal": positive == negative,
        "added": dict(sorted(added.items())),
        "removed": dict(sorted(removed.items())),
        "quantity_changes": quantity_changes,
    }


def _empty_alignment_view(value: Any) -> dict[str, Any]:
    return {
        "original_text": value,
        "alignment_text": "",
        "alignment_lexemes": [],
        "alignment_lexeme_kinds": [],
        "original_character_offsets": [],
        "alignment_character_offsets": [],
        "terminal_punctuation": "",
        "normalization": {},
    }


def _invalid_result(
    row: Mapping[str, Any], row_index: int, reason: str, scope_flags: Mapping[str, bool]
) -> dict[str, Any]:
    positive_1 = row.get("caption")
    positive_2 = row.get("caption2")
    negative = row.get("negative_caption")
    sample_id = row.get("row_key")
    if not isinstance(sample_id, str) or not sample_id:
        sample_id = f"input_row:{row_index}"
    first_view = _empty_alignment_view(positive_1)
    second_view = _empty_alignment_view(positive_2)
    negative_view = _empty_alignment_view(negative)
    return {
        "sample_id": sample_id,
        "filename": row.get("filename"),
        "numeric_id": row.get("numeric_id"),
        "negative_type": row.get("category"),
        "scope_flags": dict(scope_flags),
        "positive_1_original": positive_1,
        "positive_2_original": positive_2,
        "negative_original": negative,
        "positive_1_alignment": "",
        "positive_2_alignment": "",
        "negative_alignment": "",
        "positive_1_alignment_view": first_view,
        "positive_2_alignment_view": second_view,
        "negative_alignment_view": negative_view,
        "positive_1_alignment_lexemes": [],
        "positive_2_alignment_lexemes": [],
        "negative_alignment_lexemes": [],
        "positive_1_original_character_offsets": [],
        "positive_2_original_character_offsets": [],
        "negative_original_character_offsets": [],
        "selected_comparison_positive": None,
        "selected_comparison_positive_label": None,
        "comparison_selection_tuple_positive_1": None,
        "comparison_selection_tuple_positive_2": None,
        "comparison_selection_tuple_exact_positive_1": None,
        "comparison_selection_tuple_exact_positive_2": None,
        "comparison_selection_reason": "invalid_input",
        "comparison_is_ambiguous": False,
        "positive_sources_equivalent": False,
        "lexeme_edit_distance": None,
        "lexeme_edit_opcodes": [],
        "non_equal_block_count": 0,
        "maximum_equal_bridge_length": 0,
        "common_prefix_lexemes": [],
        "positive_contrast_hull_lexemes": [],
        "negative_contrast_hull_lexemes": [],
        "common_suffix_lexemes": [],
        "positive_contrast_hull": "",
        "negative_contrast_hull": "",
        "positive_hull_original_character_interval": None,
        "negative_hull_original_character_interval": None,
        "positive_hull_lexeme_count": 0,
        "negative_hull_lexeme_count": 0,
        "positive_hull_coverage": None,
        "negative_hull_coverage": None,
        "maximum_hull_lexeme_coverage": None,
        "common_prefix_model_token_ids": [],
        "common_prefix_model_token_count": 0,
        "positive_hull_model_token_ids": [],
        "negative_hull_model_token_ids": [],
        "common_suffix_model_token_ids": [],
        "positive_hull_model_token_text": "",
        "negative_hull_model_token_text": "",
        "positive_hull_model_token_count": 0,
        "negative_hull_model_token_count": 0,
        "positive_hull_token_coverage": None,
        "negative_hull_token_coverage": None,
        "maximum_hull_token_coverage": None,
        "positive_hull_token_boundary_ok": False,
        "negative_hull_token_boundary_ok": False,
        "positive_token_boundary_expansion_text": "",
        "negative_token_boundary_expansion_text": "",
        "normalized_positive_reconstruction_ok": False,
        "normalized_negative_reconstruction_ok": False,
        "token_boundary_mapping_ok": False,
        "can_score_from_common_prefix": False,
        "hull_lexeme_multiset_equal": False,
        "hull_multiset_added": {},
        "hull_multiset_removed": {},
        "hull_multiset_quantity_changes": {},
        "surface_artifact_types": [],
        "first_round_selected_source_label": None,
        "first_round_category": None,
        "second_round_category": "invalid_sample",
        "selection_agrees_with_first_round": None,
        "first_round_complex_to_one_block_local": False,
        "surface_artifact_resolved": False,
        "failure_reason": reason,
    }


def _original_hull_interval(
    view: Mapping[str, Any], lexeme_start: int, lexeme_end: int
) -> list[int] | None:
    offsets = view["original_character_offsets"]
    if lexeme_start == lexeme_end:
        return None
    selected = offsets[lexeme_start:lexeme_end]
    return [min(item[0] for item in selected), max(item[1] for item in selected)]


def audit_row(
    row: Mapping[str, Any],
    tokenizer: Any,
    *,
    row_index: int = 0,
    first_round: Mapping[str, Any] | None = None,
    scope_flags: Mapping[str, bool] | None = None,
    image_status: str | None = "ready",
    extra_invalid_reasons: Iterable[str] = (),
) -> dict[str, Any]:
    scope_flags = dict(scope_flags or {})
    invalid_reasons = list(extra_invalid_reasons)
    sample_id = row.get("row_key")
    filename = row.get("filename")
    numeric_id = row.get("numeric_id")
    negative_type = row.get("category")
    positive_1 = row.get("caption")
    positive_2 = row.get("caption2")
    negative = row.get("negative_caption")
    if not isinstance(sample_id, str) or not sample_id:
        invalid_reasons.append("missing_sample_id")
    if not isinstance(filename, str) or not COCO_FILENAME_RE.fullmatch(filename):
        invalid_reasons.append("invalid_filename")
    if not isinstance(numeric_id, int) or isinstance(numeric_id, bool) or numeric_id < 0:
        invalid_reasons.append("invalid_numeric_id")
    if not isinstance(negative_type, str) or not negative_type:
        invalid_reasons.append("invalid_negative_type")
    for field, value in (
        ("caption", positive_1),
        ("caption2", positive_2),
        ("negative_caption", negative),
    ):
        if not isinstance(value, str):
            invalid_reasons.append(f"missing_or_non_string_{field}")
        elif not value:
            invalid_reasons.append(f"empty_{field}")
    if image_status != "ready":
        invalid_reasons.append(f"image_status_{image_status}")
    if invalid_reasons:
        result = _invalid_result(
            row, row_index, ";".join(sorted(set(invalid_reasons))), scope_flags
        )
        if first_round is not None:
            result["first_round_category"] = first_round.get("category")
            result["first_round_selected_source_label"] = first_round.get(
                "selected_source_label"
            )
        return result

    assert isinstance(positive_1, str)
    assert isinstance(positive_2, str)
    assert isinstance(negative, str)
    first_view = build_alignment_view(positive_1)
    second_view = build_alignment_view(positive_2)
    negative_view = build_alignment_view(negative)
    if not first_view["alignment_lexemes"] or not second_view["alignment_lexemes"] or not negative_view["alignment_lexemes"]:
        result = _invalid_result(row, row_index, "empty_alignment_lexeme_sequence", scope_flags)
        return result

    selection = select_comparison_positive(first_view, second_view, negative_view)
    selected_label = selection["selected_label"]
    selected_original = (
        positive_1
        if selected_label == "positive_1"
        else positive_2 if selected_label == "positive_2" else None
    )
    selected_view = (
        first_view
        if selected_label == "positive_1"
        else second_view if selected_label == "positive_2" else None
    )
    selected_candidate = (
        selection["positive_1"]
        if selected_label == "positive_1"
        else selection["positive_2"] if selected_label == "positive_2" else None
    )

    first_round_category = first_round.get("category") if first_round else None
    first_round_label = first_round.get("selected_source_label") if first_round else None
    selection_agrees = (
        first_round_label == selected_label
        if first_round is not None and (first_round_label is not None or selected_label is not None)
        else None
    )

    base = {
        "sample_id": sample_id,
        "filename": filename,
        "numeric_id": numeric_id,
        "negative_type": negative_type,
        "scope_flags": scope_flags,
        "positive_1_original": positive_1,
        "positive_2_original": positive_2,
        "negative_original": negative,
        "positive_1_alignment": first_view["alignment_text"],
        "positive_2_alignment": second_view["alignment_text"],
        "negative_alignment": negative_view["alignment_text"],
        "positive_1_alignment_view": first_view,
        "positive_2_alignment_view": second_view,
        "negative_alignment_view": negative_view,
        "positive_1_alignment_lexemes": first_view["alignment_lexemes"],
        "positive_2_alignment_lexemes": second_view["alignment_lexemes"],
        "negative_alignment_lexemes": negative_view["alignment_lexemes"],
        "positive_1_original_character_offsets": first_view["original_character_offsets"],
        "positive_2_original_character_offsets": second_view["original_character_offsets"],
        "negative_original_character_offsets": negative_view["original_character_offsets"],
        "selected_comparison_positive": selected_original,
        "selected_comparison_positive_label": selected_label,
        "comparison_selection_tuple_positive_1": selection["positive_1"]["selection_tuple"],
        "comparison_selection_tuple_positive_2": selection["positive_2"]["selection_tuple"],
        "comparison_selection_tuple_exact_positive_1": selection["positive_1"]["selection_tuple_exact"],
        "comparison_selection_tuple_exact_positive_2": selection["positive_2"]["selection_tuple_exact"],
        "comparison_selection_reason": selection["reason"],
        "comparison_is_ambiguous": selection["ambiguous"],
        "positive_sources_equivalent": selection["equivalent"],
        "first_round_selected_source_label": first_round_label,
        "first_round_category": first_round_category,
        "selection_agrees_with_first_round": selection_agrees,
    }

    if selected_candidate is None or selected_view is None:
        empty = _invalid_result(row, row_index, selection["reason"], scope_flags)
        for key, value in base.items():
            empty[key] = value
        empty.update(
            second_round_category="ambiguous_comparison_positive",
            comparison_is_ambiguous=True,
            failure_reason=selection["reason"],
        )
        return empty

    opcodes = selected_candidate["edit_opcodes"]
    hull = selected_candidate["hull"]
    positive_rebuilt = (
        hull["common_prefix_lexemes"]
        + hull["positive_hull_lexemes"]
        + hull["common_suffix_lexemes"]
    )
    negative_rebuilt = (
        hull["common_prefix_lexemes"]
        + hull["negative_hull_lexemes"]
        + hull["common_suffix_lexemes"]
    )
    positive_reconstruction_ok = positive_rebuilt == selected_view["alignment_lexemes"]
    negative_reconstruction_ok = negative_rebuilt == negative_view["alignment_lexemes"]
    if not positive_reconstruction_ok or not negative_reconstruction_ok:
        raise AssertionError(f"normalized hull reconstruction failed for {sample_id}")

    positive_hull_count = len(hull["positive_hull_lexemes"])
    negative_hull_count = len(hull["negative_hull_lexemes"])
    positive_coverage_fraction = Fraction(
        positive_hull_count, max(len(selected_view["alignment_lexemes"]), 1)
    )
    negative_coverage_fraction = Fraction(
        negative_hull_count, max(len(negative_view["alignment_lexemes"]), 1)
    )
    token_mapping = map_contrast_hull_to_tokenizer(
        tokenizer, selected_view, negative_view, hull
    )
    positive_token = token_mapping["positive"]
    negative_token = token_mapping["negative"]
    if positive_token is not None and negative_token is not None:
        positive_token_coverage_fraction = Fraction(
            len(positive_token["hull_ids"]), max(len(positive_token["full_ids"]), 1)
        )
        negative_token_coverage_fraction = Fraction(
            len(negative_token["hull_ids"]), max(len(negative_token["full_ids"]), 1)
        )
        max_token_coverage_fraction = max(
            positive_token_coverage_fraction, negative_token_coverage_fraction
        )
    else:
        positive_token_coverage_fraction = None
        negative_token_coverage_fraction = None
        max_token_coverage_fraction = None

    surface_only = (
        selected_view["alignment_lexemes"] == negative_view["alignment_lexemes"]
    )
    if surface_only:
        second_category = "surface_only_or_degenerate"
        failure_reason = "selected_positive_equals_negative_after_alignment_normalization"
    elif selection["equivalent"]:
        second_category = "equivalent_positive_sources"
        failure_reason = "positive_alignment_views_and_selection_tuples_are_equivalent"
    elif not token_mapping["ok"]:
        second_category = "token_mapping_problem"
        failure_reason = token_mapping["error"]
    elif max_token_coverage_fraction == 1:
        second_category = "whole_sentence_hull"
        failure_reason = "at_least_one_hull_covers_all_model_tokens"
    elif (
        hull["non_equal_block_count"] == 1
        and max_token_coverage_fraction is not None
        and max_token_coverage_fraction <= Fraction(1, 2)
    ):
        second_category = "one_block_local"
        failure_reason = None
    elif (
        hull["non_equal_block_count"] >= 2
        and max_token_coverage_fraction is not None
        and max_token_coverage_fraction <= Fraction(3, 4)
    ):
        second_category = "multi_block_local_hull"
        failure_reason = None
    elif (
        max_token_coverage_fraction is not None
        and max_token_coverage_fraction <= Fraction(3, 4)
    ):
        second_category = "medium_contrast_hull"
        failure_reason = "single_edit_block_token_coverage_above_50_percent"
    else:
        second_category = "large_contrast_hull"
        failure_reason = "maximum_hull_token_coverage_above_75_percent"

    surface_types = _surface_artifact_flags(selected_original, negative)
    first_round_complex_to_one_block_local = (
        first_round_category == "complex_edit" and second_category == "one_block_local"
    )
    surface_artifact_resolved = bool(
        first_round_complex_to_one_block_local and surface_types
    )
    multiset = _counter_delta(
        hull["positive_hull_lexemes"], hull["negative_hull_lexemes"]
    )
    base.update(
        {
            "lexeme_edit_distance": selected_candidate["edit_distance"],
            "lexeme_edit_opcodes": opcodes,
            "non_equal_block_count": hull["non_equal_block_count"],
            "maximum_equal_bridge_length": hull["maximum_equal_bridge_length"],
            "common_prefix_lexemes": hull["common_prefix_lexemes"],
            "positive_contrast_hull_lexemes": hull["positive_hull_lexemes"],
            "negative_contrast_hull_lexemes": hull["negative_hull_lexemes"],
            "common_suffix_lexemes": hull["common_suffix_lexemes"],
            "positive_contrast_hull": " ".join(hull["positive_hull_lexemes"]),
            "negative_contrast_hull": " ".join(hull["negative_hull_lexemes"]),
            "positive_hull_original_character_interval": _original_hull_interval(
                selected_view, hull["positive_start"], hull["positive_end"]
            ),
            "negative_hull_original_character_interval": _original_hull_interval(
                negative_view, hull["negative_start"], hull["negative_end"]
            ),
            "positive_hull_lexeme_count": positive_hull_count,
            "negative_hull_lexeme_count": negative_hull_count,
            "positive_hull_coverage": float(positive_coverage_fraction),
            "negative_hull_coverage": float(negative_coverage_fraction),
            "maximum_hull_lexeme_coverage": float(
                max(positive_coverage_fraction, negative_coverage_fraction)
            ),
            "common_prefix_model_token_ids": token_mapping["common_prefix_ids"],
            "common_prefix_model_token_count": len(
                token_mapping["common_prefix_ids"]
            ),
            "positive_hull_model_token_ids": (
                positive_token["hull_ids"] if positive_token else []
            ),
            "negative_hull_model_token_ids": (
                negative_token["hull_ids"] if negative_token else []
            ),
            "common_suffix_model_token_ids": token_mapping["common_suffix_ids"],
            "positive_hull_model_token_text": (
                positive_token["hull_text"] if positive_token else ""
            ),
            "negative_hull_model_token_text": (
                negative_token["hull_text"] if negative_token else ""
            ),
            "positive_hull_model_token_count": (
                len(positive_token["hull_ids"]) if positive_token else 0
            ),
            "negative_hull_model_token_count": (
                len(negative_token["hull_ids"]) if negative_token else 0
            ),
            "positive_hull_token_coverage": (
                float(positive_token_coverage_fraction)
                if positive_token_coverage_fraction is not None
                else None
            ),
            "negative_hull_token_coverage": (
                float(negative_token_coverage_fraction)
                if negative_token_coverage_fraction is not None
                else None
            ),
            "maximum_hull_token_coverage": (
                float(max_token_coverage_fraction)
                if max_token_coverage_fraction is not None
                else None
            ),
            "positive_hull_token_boundary_ok": (
                positive_token["token_boundary_ok"] if positive_token else False
            ),
            "negative_hull_token_boundary_ok": (
                negative_token["token_boundary_ok"] if negative_token else False
            ),
            "positive_token_boundary_expansion_text": (
                positive_token["boundary_expansion_text"] if positive_token else ""
            ),
            "negative_token_boundary_expansion_text": (
                negative_token["boundary_expansion_text"] if negative_token else ""
            ),
            "normalized_positive_reconstruction_ok": positive_reconstruction_ok,
            "normalized_negative_reconstruction_ok": negative_reconstruction_ok,
            "token_boundary_mapping_ok": token_mapping["ok"],
            "can_score_from_common_prefix": token_mapping[
                "can_score_from_common_prefix"
            ],
            "hull_lexeme_multiset_equal": multiset["equal"],
            "hull_multiset_added": multiset["added"],
            "hull_multiset_removed": multiset["removed"],
            "hull_multiset_quantity_changes": multiset["quantity_changes"],
            "surface_artifact_types": surface_types,
            "second_round_category": second_category,
            "first_round_complex_to_one_block_local": (
                first_round_complex_to_one_block_local
            ),
            "surface_artifact_resolved": surface_artifact_resolved,
            "failure_reason": failure_reason,
        }
    )
    return base


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _percentile(values: Sequence[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)


def _numeric_distribution(values: Iterable[int | float | None]) -> dict[str, Any]:
    clean = [float(value) for value in values if value is not None]
    histogram = Counter(str(int(value)) if value.is_integer() else str(value) for value in clean)
    return {
        "count": len(clean),
        "mean": statistics.fmean(clean) if clean else None,
        "median": statistics.median(clean) if clean else None,
        "p75": _percentile(clean, 0.75),
        "p90": _percentile(clean, 0.90),
        "maximum": max(clean) if clean else None,
        "histogram": dict(
            sorted(histogram.items(), key=lambda item: float(item[0]))
        ),
    }


def _coverage_bucket(value: float) -> str:
    if value == 0:
        return "0"
    if value <= 0.25:
        return "(0,0.25]"
    if value <= 0.50:
        return "(0.25,0.50]"
    if value <= 0.75:
        return "(0.50,0.75]"
    if value <= 0.90:
        return "(0.75,0.90]"
    if value < 1.0:
        return "(0.90,1.00)"
    return "1.00"


def _coverage_distribution(values: Iterable[float | None]) -> dict[str, Any]:
    clean = [float(value) for value in values if value is not None]
    order = [
        "0",
        "(0,0.25]",
        "(0.25,0.50]",
        "(0.50,0.75]",
        "(0.75,0.90]",
        "(0.90,1.00)",
        "1.00",
    ]
    counts = Counter(_coverage_bucket(value) for value in clean)
    return {
        "count": len(clean),
        "mean": statistics.fmean(clean) if clean else None,
        "median": statistics.median(clean) if clean else None,
        "p75": _percentile(clean, 0.75),
        "p90": _percentile(clean, 0.90),
        "maximum": max(clean) if clean else None,
        "bins": {
            bucket: {
                "count": counts.get(bucket, 0),
                "proportion": _ratio(counts.get(bucket, 0), len(clean)),
            }
            for bucket in order
        },
    }


def _block_count_distribution(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    for row in rows:
        value = int(row.get("non_equal_block_count") or 0)
        if value == 0:
            counts["zero"] += 1
        elif value == 1:
            counts["one"] += 1
        elif value == 2:
            counts["two"] += 1
        else:
            counts["three_or_more"] += 1
    return {
        key: {"count": counts[key], "proportion": _ratio(counts[key], len(rows))}
        for key in ("zero", "one", "two", "three_or_more")
    }


def _structure_metrics(rows: Sequence[Mapping[str, Any]], *, with_types: bool) -> dict[str, Any]:
    category_counts = Counter(row["second_round_category"] for row in rows)
    valid = [
        row
        for row in rows
        if row.get("selected_comparison_positive_label") is not None
        and row["second_round_category"]
        not in {"invalid_sample", "surface_only_or_degenerate"}
    ]
    result = {
        "record_count": len(rows),
        "unique_image_count": len({row["filename"] for row in rows}),
        "valid_comparison_positive_count": len(valid),
        "ambiguous_comparison_positive_count": category_counts.get(
            "ambiguous_comparison_positive", 0
        ),
        "equivalent_positive_sources_count": category_counts.get(
            "equivalent_positive_sources", 0
        ),
        "surface_only_or_degenerate_count": category_counts.get(
            "surface_only_or_degenerate", 0
        ),
        "token_mapping_problem_count": category_counts.get("token_mapping_problem", 0),
        "invalid_sample_count": category_counts.get("invalid_sample", 0),
        "category_counts": dict(sorted(category_counts.items())),
        "non_equal_block_count_distribution": _block_count_distribution(rows),
        "positive_hull_lexeme_count": _numeric_distribution(
            row.get("positive_hull_lexeme_count") for row in rows
        ),
        "negative_hull_lexeme_count": _numeric_distribution(
            row.get("negative_hull_lexeme_count") for row in rows
        ),
        "positive_hull_model_token_count": _numeric_distribution(
            row.get("positive_hull_model_token_count") for row in rows
        ),
        "negative_hull_model_token_count": _numeric_distribution(
            row.get("negative_hull_model_token_count") for row in rows
        ),
        "positive_hull_lexeme_coverage": _coverage_distribution(
            row.get("positive_hull_coverage") for row in rows
        ),
        "negative_hull_lexeme_coverage": _coverage_distribution(
            row.get("negative_hull_coverage") for row in rows
        ),
        "maximum_hull_lexeme_coverage": _coverage_distribution(
            row.get("maximum_hull_lexeme_coverage") for row in rows
        ),
        "positive_hull_token_coverage": _coverage_distribution(
            row.get("positive_hull_token_coverage") for row in rows
        ),
        "negative_hull_token_coverage": _coverage_distribution(
            row.get("negative_hull_token_coverage") for row in rows
        ),
        "maximum_hull_token_coverage": _coverage_distribution(
            row.get("maximum_hull_token_coverage") for row in rows
        ),
        "common_prefix_model_token_count": _numeric_distribution(
            row.get("common_prefix_model_token_count") for row in rows
        ),
        "maximum_equal_bridge_length": _numeric_distribution(
            row.get("maximum_equal_bridge_length") for row in rows
        ),
    }
    if with_types:
        result["negative_type_results"] = {
            negative_type: _structure_metrics(
                [row for row in rows if row["negative_type"] == negative_type],
                with_types=False,
            )
            for negative_type in sorted({row["negative_type"] for row in rows})
        }
    return result


def _example(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": row["sample_id"],
        "negative_type": row["negative_type"],
        "first_round_category": row["first_round_category"],
        "second_round_category": row["second_round_category"],
        "first_round_selected_source_label": row[
            "first_round_selected_source_label"
        ],
        "selected_comparison_positive_label": row[
            "selected_comparison_positive_label"
        ],
        "positive_contrast_hull": row["positive_contrast_hull"],
        "negative_contrast_hull": row["negative_contrast_hull"],
        "maximum_hull_token_coverage": row["maximum_hull_token_coverage"],
        "failure_reason": row["failure_reason"],
    }


def _stable_sample(
    rows: Sequence[Mapping[str, Any]], limit: int, seed: int, group: str
) -> list[Mapping[str, Any]]:
    ordered = sorted(rows, key=lambda row: row["sample_id"].encode("utf-8"))
    if len(ordered) <= limit:
        return ordered
    derived = int.from_bytes(
        hashlib.sha256(f"{seed}:{group}".encode("utf-8")).digest()[:8], "big"
    )
    indices = sorted(random.Random(derived).sample(range(len(ordered)), limit))
    return [ordered[index] for index in indices]


def build_first_round_comparison(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    agreement = [
        row
        for row in rows
        if row["first_round_selected_source_label"] is not None
        and row["selected_comparison_positive_label"]
        == row["first_round_selected_source_label"]
    ]
    disagreement = [
        row
        for row in rows
        if row["first_round_selected_source_label"] is not None
        and row["selected_comparison_positive_label"] is not None
        and row["selected_comparison_positive_label"]
        != row["first_round_selected_source_label"]
    ]
    first_ambiguous_resolved = [
        row
        for row in rows
        if row["first_round_selected_source_label"] is None
        and row["selected_comparison_positive_label"] is not None
        and not row["comparison_is_ambiguous"]
    ]
    second_new_ambiguous = [
        row
        for row in rows
        if row["first_round_selected_source_label"] is not None
        and row["comparison_is_ambiguous"]
    ]
    both_ambiguous = [
        row
        for row in rows
        if row["first_round_selected_source_label"] is None
        and row["comparison_is_ambiguous"]
    ]
    return {
        "agreement_count": len(agreement),
        "disagreement_count": len(disagreement),
        "first_round_ambiguous_second_round_resolved_count": len(
            first_ambiguous_resolved
        ),
        "second_round_new_ambiguous_count": len(second_new_ambiguous),
        "both_rounds_ambiguous_count": len(both_ambiguous),
        "second_round_equivalent_positive_sources_count": sum(
            row["positive_sources_equivalent"] for row in rows
        ),
        "representative_disagreements": [
            _example(row)
            for row in _stable_sample(disagreement, 12, RANDOM_SEED, "source_disagreement")
        ],
        "representative_first_round_ambiguities_resolved": [
            _example(row)
            for row in _stable_sample(
                first_ambiguous_resolved,
                8,
                RANDOM_SEED,
                "first_ambiguity_resolved",
            )
        ],
        "representative_second_round_new_ambiguities": [
            _example(row)
            for row in _stable_sample(
                second_new_ambiguous, 8, RANDOM_SEED, "second_new_ambiguity"
            )
        ],
    }


def build_surface_artifact_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    first_complex = [row for row in rows if row["first_round_category"] == "complex_edit"]
    complex_to_one_block = [
        row for row in rows if row["first_round_complex_to_one_block_local"]
    ]
    resolved = [row for row in rows if row["surface_artifact_resolved"]]
    flag_counts = Counter(
        flag for row in resolved for flag in row.get("surface_artifact_types", [])
    )
    flag_combinations = Counter(
        "+".join(row.get("surface_artifact_types", [])) or "none_detected"
        for row in resolved
    )
    surface_plus_local = [
        row
        for row in rows
        if row["second_round_category"] == "one_block_local"
        and row.get("surface_artifact_types")
    ]
    return {
        "first_round_complex_edit_count": len(first_complex),
        "first_round_complex_to_one_block_local_count": len(complex_to_one_block),
        "first_round_complex_to_one_block_local_proportion": _ratio(
            len(complex_to_one_block), len(first_complex)
        ),
        "surface_artifact_resolved_count": len(resolved),
        "surface_artifact_resolved_proportion_of_first_round_complex": _ratio(
            len(resolved), len(first_complex)
        ),
        "resolved_surface_flag_counts": dict(sorted(flag_counts.items())),
        "resolved_surface_flag_combination_counts": dict(
            sorted(flag_combinations.items())
        ),
        "all_one_block_local_with_surface_artifact_count": len(surface_plus_local),
        "representative_resolved_cases": [
            _example(row)
            for row in _stable_sample(resolved, 15, RANDOM_SEED, "surface_resolved")
        ],
    }


def _aggregate_counter_dicts(
    rows: Sequence[Mapping[str, Any]], key: str
) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter.update({str(name): int(count) for name, count in row.get(key, {}).items()})
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def build_swap_statistics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    output = {}
    for negative_type in sorted(SWAP_TYPES):
        group = [row for row in rows if row["negative_type"] == negative_type]
        multiset_different = [row for row in group if not row["hull_lexeme_multiset_equal"]]
        quantity_counter: Counter[str] = Counter()
        for row in multiset_different:
            quantity_counter.update(row.get("hull_multiset_quantity_changes", {}).keys())
        output[negative_type] = {
            "record_count": len(group),
            "unique_image_count": len({row["filename"] for row in group}),
            "non_equal_block_count_distribution": _block_count_distribution(group),
            "positive_hull_lexeme_count": _numeric_distribution(
                row["positive_hull_lexeme_count"] for row in group
            ),
            "negative_hull_lexeme_count": _numeric_distribution(
                row["negative_hull_lexeme_count"] for row in group
            ),
            "positive_hull_model_token_count": _numeric_distribution(
                row["positive_hull_model_token_count"] for row in group
            ),
            "negative_hull_model_token_count": _numeric_distribution(
                row["negative_hull_model_token_count"] for row in group
            ),
            "maximum_hull_lexeme_coverage": _coverage_distribution(
                row["maximum_hull_lexeme_coverage"] for row in group
            ),
            "maximum_hull_token_coverage": _coverage_distribution(
                row["maximum_hull_token_coverage"] for row in group
            ),
            "whole_sentence_hull_count": sum(
                row["second_round_category"] == "whole_sentence_hull" for row in group
            ),
            "two_or_more_non_equal_blocks_count": sum(
                row["non_equal_block_count"] >= 2 for row in group
            ),
            "hull_lexeme_multiset_equal_count": sum(
                row["hull_lexeme_multiset_equal"] for row in group
            ),
            "hull_lexeme_multiset_different_count": len(multiset_different),
            "aggregate_added_lexemes": _aggregate_counter_dicts(
                multiset_different, "hull_multiset_added"
            ),
            "aggregate_removed_lexemes": _aggregate_counter_dicts(
                multiset_different, "hull_multiset_removed"
            ),
            "quantity_change_lexeme_sample_counts": dict(
                sorted(quantity_counter.items(), key=lambda item: (-item[1], item[0]))
            ),
            "nonempty_common_prefix_count": sum(
                bool(row["common_prefix_lexemes"]) for row in group
            ),
            "can_score_from_common_prefix_count": sum(
                row["can_score_from_common_prefix"] for row in group
            ),
            "image_groups_with_scorable_record_count": len(
                {
                    row["filename"]
                    for row in group
                    if row["can_score_from_common_prefix"]
                }
            ),
        }
    return output


def _base_nonambiguous_nondegenerate(row: Mapping[str, Any]) -> bool:
    return row["second_round_category"] not in {
        "ambiguous_comparison_positive",
        "surface_only_or_degenerate",
        "invalid_sample",
    }


def _hypothetical_coverage(
    rows: Sequence[Mapping[str, Any]],
    predicate: Any,
    label: str,
    rule: str,
) -> dict[str, Any]:
    retained = [row for row in rows if predicate(row)]
    retained_images = {row["filename"] for row in retained}
    type_totals = Counter(row["negative_type"] for row in rows)
    type_retained = Counter(row["negative_type"] for row in retained)
    return {
        "label": label,
        "selection_rule": rule,
        "remaining_record_count": len(retained),
        "remaining_unique_image_count": len(retained_images),
        "negative_type_retention": {
            negative_type: {
                "retained_count": type_retained[negative_type],
                "total_count": type_totals[negative_type],
                "retention_proportion": _ratio(
                    type_retained[negative_type], type_totals[negative_type]
                ),
            }
            for negative_type in sorted(type_totals)
        },
        "mean_retained_records_per_retained_image": _ratio(
            len(retained), len(retained_images)
        ),
        "mean_retained_records_per_all_certifying_images": _ratio(
            len(retained), len({row["filename"] for row in rows})
        ),
    }


def build_image_group_coverage(
    certifying_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in certifying_rows:
        grouped[row["filename"]].append(row)
    image_rows = []
    for filename in sorted(grouped, key=lambda value: value.encode("utf-8")):
        group = grouped[filename]
        type_counts = Counter(row["negative_type"] for row in group)
        nonambiguous = [row for row in group if _base_nonambiguous_nondegenerate(row)]
        scorable = [row for row in group if row["can_score_from_common_prefix"]]
        image_rows.append(
            {
                "filename": filename,
                "record_count": len(group),
                "negative_type_counts": {
                    negative_type: type_counts.get(negative_type, 0)
                    for negative_type in sorted(REPLACE_TYPES | SWAP_TYPES)
                },
                "nonambiguous_nondegenerate_record_count": len(nonambiguous),
                "scorable_record_count": len(scorable),
                "has_nonambiguous_comparison_record": bool(nonambiguous),
                "has_hull_token_coverage_at_most_50_percent": any(
                    row["maximum_hull_token_coverage"] is not None
                    and row["maximum_hull_token_coverage"] <= 0.50
                    and row["can_score_from_common_prefix"]
                    for row in group
                ),
                "has_hull_token_coverage_at_most_75_percent": any(
                    row["maximum_hull_token_coverage"] is not None
                    and row["maximum_hull_token_coverage"] <= 0.75
                    and row["can_score_from_common_prefix"]
                    for row in group
                ),
                "has_hull_token_coverage_at_most_90_percent": any(
                    row["maximum_hull_token_coverage"] is not None
                    and row["maximum_hull_token_coverage"] <= 0.90
                    and row["can_score_from_common_prefix"]
                    for row in group
                ),
                "all_records_whole_sentence_or_ambiguous": all(
                    row["second_round_category"]
                    in {"whole_sentence_hull", "ambiguous_comparison_positive"}
                    for row in group
                ),
                "only_replace_records": all(
                    row["negative_type"] in REPLACE_TYPES for row in group
                ),
                "contains_swap_record": any(
                    row["negative_type"] in SWAP_TYPES for row in group
                ),
            }
        )
    if len(image_rows) != 1345:
        raise ValueError(
            f"certifying formal image-group count is {len(image_rows)}, expected 1345"
        )
    record_count_distribution = _numeric_distribution(
        row["record_count"] for row in image_rows
    )
    type_pattern_counts = Counter(
        "+".join(
            f"{negative_type}:{count}"
            for negative_type, count in row["negative_type_counts"].items()
            if count
        )
        for row in image_rows
    )
    hypotheses = [
        _hypothetical_coverage(
            certifying_rows,
            _base_nonambiguous_nondegenerate,
            "A",
            "all non-ambiguous, non-degenerate, non-invalid records",
        ),
        _hypothetical_coverage(
            certifying_rows,
            lambda row: _base_nonambiguous_nondegenerate(row)
            and row["maximum_hull_token_coverage"] is not None
            and row["maximum_hull_token_coverage"] <= 0.90,
            "B",
            "A and maximum hull token coverage <= 90%",
        ),
        _hypothetical_coverage(
            certifying_rows,
            lambda row: _base_nonambiguous_nondegenerate(row)
            and row["maximum_hull_token_coverage"] is not None
            and row["maximum_hull_token_coverage"] <= 0.75,
            "C",
            "A and maximum hull token coverage <= 75%",
        ),
        _hypothetical_coverage(
            certifying_rows,
            lambda row: _base_nonambiguous_nondegenerate(row)
            and row["maximum_hull_token_coverage"] is not None
            and row["maximum_hull_token_coverage"] <= 0.50,
            "D",
            "A and maximum hull token coverage <= 50%",
        ),
        _hypothetical_coverage(
            certifying_rows,
            lambda row: _base_nonambiguous_nondegenerate(row)
            and row["non_equal_block_count"] == 1,
            "E",
            "A and exactly one non-equal lexeme block",
        ),
        _hypothetical_coverage(
            certifying_rows,
            lambda row: _base_nonambiguous_nondegenerate(row)
            and row["negative_type"] in REPLACE_TYPES,
            "F",
            "A and replace negative type",
        ),
    ]
    return {
        "schema_version": 1,
        "audit_version": AUDIT_VERSION,
        "scope": "certifying_formal",
        "record_count": len(certifying_rows),
        "image_group_count": len(image_rows),
        "record_count_per_image": record_count_distribution,
        "negative_type_pattern_counts": dict(sorted(type_pattern_counts.items())),
        "image_group_counts": {
            "at_least_one_nonambiguous_comparison_record": sum(
                row["has_nonambiguous_comparison_record"] for row in image_rows
            ),
            "at_least_one_hull_coverage_at_most_50_percent": sum(
                row["has_hull_token_coverage_at_most_50_percent"] for row in image_rows
            ),
            "at_least_one_hull_coverage_at_most_75_percent": sum(
                row["has_hull_token_coverage_at_most_75_percent"] for row in image_rows
            ),
            "at_least_one_hull_coverage_at_most_90_percent": sum(
                row["has_hull_token_coverage_at_most_90_percent"] for row in image_rows
            ),
            "all_records_whole_sentence_or_ambiguous": sum(
                row["all_records_whole_sentence_or_ambiguous"] for row in image_rows
            ),
            "only_replace_records": sum(row["only_replace_records"] for row in image_rows),
            "contains_swap_record": sum(row["contains_swap_record"] for row in image_rows),
        },
        "hypothetical_coverage_table": hypotheses,
        "image_groups": image_rows,
        "formal_filter_selected": False,
    }


def _markdown_sample(row: Mapping[str, Any], index: int) -> list[str]:
    rendered = lambda value: json.dumps(value, ensure_ascii=False)
    return [
        f"### {index}. `{row['sample_id']}`",
        "",
        f"- 负例类型/范围：`{row['negative_type']}` / `{rendered(row['scope_flags'])}`",
        f"- 原始正描述 1：{rendered(row['positive_1_original'])}",
        f"- 原始正描述 2：{rendered(row['positive_2_original'])}",
        f"- 原始负描述：{rendered(row['negative_original'])}",
        f"- 规范化正描述 1：{rendered(row['positive_1_alignment'])}",
        f"- 规范化正描述 2：{rendered(row['positive_2_alignment'])}",
        f"- 规范化负描述：{rendered(row['negative_alignment'])}",
        f"- 正描述 1 选择元组：`{rendered(row['comparison_selection_tuple_positive_1'])}`",
        f"- 正描述 2 选择元组：`{rendered(row['comparison_selection_tuple_positive_2'])}`",
        f"- 最终比较正描述：`{row['selected_comparison_positive_label']}` / {rendered(row['selected_comparison_positive'])}",
        f"- 完整 lexeme 编辑块：`{rendered(row['lexeme_edit_opcodes'])}`",
        f"- 共同前缀：`{rendered(row['common_prefix_lexemes'])}`",
        f"- 正确 contrast hull：`{rendered(row['positive_contrast_hull_lexemes'])}`",
        f"- 错误 contrast hull：`{rendered(row['negative_contrast_hull_lexemes'])}`",
        f"- 共同后缀：`{rendered(row['common_suffix_lexemes'])}`",
        f"- Hull token 覆盖率（正/负/最大）：`{rendered([row['positive_hull_token_coverage'], row['negative_hull_token_coverage'], row['maximum_hull_token_coverage']])}`",
        f"- 共同前缀模型 token：`{rendered(row['common_prefix_model_token_ids'])}`",
        f"- 正确 hull 模型 token：IDs `{rendered(row['positive_hull_model_token_ids'])}`；text {rendered(row['positive_hull_model_token_text'])}",
        f"- 错误 hull 模型 token：IDs `{rendered(row['negative_hull_model_token_ids'])}`；text {rendered(row['negative_hull_model_token_text'])}",
        f"- 第一轮/第二轮分类：`{row['first_round_category']}` / `{row['second_round_category']}`",
        f"- 自动判断：{rendered(row['comparison_selection_reason'])}；{rendered(row['failure_reason'])}",
        "",
    ]


def build_manual_review(rows: Sequence[Mapping[str, Any]]) -> str:
    coverage = lambda row: row.get("maximum_hull_token_coverage")
    groups = [
        (
            "normalized_one_block_local",
            "规范化后变为单块局部编辑",
            [
                row
                for row in rows
                if row["first_round_complex_to_one_block_local"]
            ],
        ),
        (
            "two_blocks_under_50",
            "两块编辑且 hull 不超过 50%",
            [
                row
                for row in rows
                if row["non_equal_block_count"] == 2
                and coverage(row) is not None
                and coverage(row) <= 0.50
            ],
        ),
        (
            "three_or_more_blocks",
            "三块及以上编辑",
            [row for row in rows if row["non_equal_block_count"] >= 3],
        ),
        (
            "coverage_50_75",
            "Hull 覆盖 50%–75%",
            [
                row
                for row in rows
                if coverage(row) is not None and 0.50 < coverage(row) <= 0.75
            ],
        ),
        (
            "coverage_75_90",
            "Hull 覆盖 75%–90%",
            [
                row
                for row in rows
                if coverage(row) is not None and 0.75 < coverage(row) <= 0.90
            ],
        ),
        (
            "coverage_over_90",
            "Hull 超过 90%",
            [row for row in rows if coverage(row) is not None and coverage(row) > 0.90],
        ),
        (
            "whole_sentence",
            "整句 hull",
            [row for row in rows if row["second_round_category"] == "whole_sentence_hull"],
        ),
        (
            "swap_attribute",
            "swap_atribute",
            [row for row in rows if row["negative_type"] == "swap_atribute"],
        ),
        (
            "swap_object",
            "swap_object",
            [row for row in rows if row["negative_type"] == "swap_object"],
        ),
        (
            "comparison_ambiguous",
            "Comparison positive 歧义",
            [row for row in rows if row["comparison_is_ambiguous"]],
        ),
        (
            "equivalent_positives",
            "两条正描述规范化等价",
            [row for row in rows if row["positive_sources_equivalent"]],
        ),
        (
            "source_selection_disagreement",
            "第一轮与第二轮来源选择不一致",
            [
                row
                for row in rows
                if row["first_round_selected_source_label"] is not None
                and row["selected_comparison_positive_label"] is not None
                and not row["selection_agrees_with_first_round"]
            ],
        ),
        (
            "token_mapping_failure",
            "Tokenizer 边界映射失败",
            [row for row in rows if not row["token_boundary_mapping_ok"]],
        ),
        (
            "surface_artifact_eliminated",
            "表面差异被成功消除",
            [
                row
                for row in rows
                if row["surface_artifact_types"]
                and row["second_round_category"] == "one_block_local"
            ],
        ),
    ]
    lines = [
        "# SugarCrepe++ contrast hull 第二轮自动审计抽查材料",
        "",
        "这些样本只供人工复核，不代表已完成人工语义验证。Contrast hull 不是人工语义真值。",
        "",
        f"固定随机种子：`{RANDOM_SEED}`；每类最多 `{REVIEW_LIMIT}` 条；不同类别允许重复。",
        "",
    ]
    for key, title, candidates in groups:
        sampled = _stable_sample(candidates, REVIEW_LIMIT, RANDOM_SEED, key)
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
        raise ValueError(f"non-canonical filename list: {path}")
    if values != sorted(set(values), key=lambda value: value.encode("utf-8")):
        raise ValueError(f"filename list is not sorted and unique: {path}")
    if any(not COCO_FILENAME_RE.fullmatch(value) for value in values):
        raise ValueError(f"invalid COCO filename in {path}")
    return values


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
    temporary.chmod(0o644)
    temporary.replace(path)


def _tokenizer_hashes(tokenizer_path: Path) -> dict[str, str]:
    output = {}
    for name in ("tokenizer.json", "tokenizer_config.json"):
        path = tokenizer_path / name
        if not path.is_file():
            raise FileNotFoundError(path)
        output[name] = _sha256(path)
    return output


def build_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    scopes = {
        "canonical": list(rows),
        "pilot": [row for row in rows if row["scope_flags"]["pilot"]],
        "formal": [row for row in rows if row["scope_flags"]["formal"]],
        "certifying_formal": [
            row for row in rows if row["scope_flags"]["certifying_formal"]
        ],
    }
    surface_artifact_audit = build_surface_artifact_summary(rows)
    surface_artifact_audit["scope_breakdown"] = {
        scope: {
            key: value
            for key, value in build_surface_artifact_summary(scope_rows).items()
            if key != "representative_resolved_cases"
        }
        for scope, scope_rows in scopes.items()
    }
    return {
        "schema_version": 1,
        "audit_version": AUDIT_VERSION,
        "random_seed": RANDOM_SEED,
        "contrast_hull_is_human_semantic_ground_truth": False,
        "formal_filter_selected": False,
        "model_outputs_consulted": False,
        "provenance": dict(provenance),
        "deterministic_rules": {
            "alignment_view": (
                "Unicode NFKC; trim edge whitespace; collapse internal whitespace; "
                "casefold; separate and exclude terminal .!?; retain original offsets"
            ),
            "lexeme_types": [
                "word_or_hyphenated_word",
                "number",
                "multi_initial_abbreviation",
                "punctuation",
            ],
            "edit_algorithm": "exact Wagner-Fischer dynamic programming",
            "edit_tie_priority": ["replace", "delete", "insert"],
            "comparison_tuple": [
                "total_edited_lexeme_count",
                "contrast_hull_total_lexeme_count",
                "number_of_non_equal_blocks",
                "normalized_lexeme_edit_distance",
                "normalized_character_edit_distance",
            ],
            "comparison_selection": "strict lexicographic minimum using exact Fractions",
            "contrast_hull": "all lexemes from first through last non-equal operation",
            "token_mapping_text": "alignment_text",
            "category_precedence": [
                "invalid_sample",
                "ambiguous_comparison_positive",
                "surface_only_or_degenerate",
                "equivalent_positive_sources",
                "token_mapping_problem",
                "whole_sentence_hull",
                "one_block_local",
                "multi_block_local_hull",
                "medium_contrast_hull",
                "large_contrast_hull",
            ],
        },
        "scope_statistics": {
            scope: _structure_metrics(scope_rows, with_types=True)
            for scope, scope_rows in scopes.items()
        },
        "first_round_comparison": build_first_round_comparison(rows),
        "surface_artifact_audit": surface_artifact_audit,
        "swap_structure_statistics": {
            scope: build_swap_statistics(scope_rows)
            for scope, scope_rows in scopes.items()
        },
        "representative_examples": {
            category: [
                _example(row)
                for row in _stable_sample(
                    [row for row in rows if row["second_round_category"] == category],
                    5,
                    RANDOM_SEED,
                    f"summary:{category}",
                )
            ]
            for category in SECOND_ROUND_CATEGORIES
        },
    }


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    from transformers import AutoTokenizer

    input_jsonl = args.input_jsonl.resolve()
    image_manifest = args.image_manifest.resolve()
    pilot_filenames_path = args.pilot_filenames.resolve()
    formal_filenames_path = args.formal_filenames.resolve()
    certifying_filenames_path = args.certifying_formal_filenames.resolve()
    first_round_path = args.first_round_audit.resolve()
    tokenizer_path = args.tokenizer.resolve()
    output_dir = args.output_dir.resolve()
    input_sha = _sha256(input_jsonl)
    first_round_sha = _sha256(first_round_path)
    if args.expected_input_sha256 and input_sha != args.expected_input_sha256:
        raise ValueError(
            f"canonical input SHA-256 mismatch: {input_sha} != {args.expected_input_sha256}"
        )
    if (
        args.expected_first_round_sha256
        and first_round_sha != args.expected_first_round_sha256
    ):
        raise ValueError(
            "first-round audit SHA-256 mismatch: "
            f"{first_round_sha} != {args.expected_first_round_sha256}"
        )

    input_rows = _read_jsonl(input_jsonl)
    first_round_rows = _read_jsonl(first_round_path)
    image_rows = _read_jsonl(image_manifest)
    pilot_filenames = set(_read_filename_list(pilot_filenames_path))
    formal_filenames = set(_read_filename_list(formal_filenames_path))
    certifying_filenames = set(_read_filename_list(certifying_filenames_path))
    canonical_filenames = {
        row.get("filename") for row in input_rows if isinstance(row.get("filename"), str)
    }
    if pilot_filenames & formal_filenames or pilot_filenames | formal_filenames != canonical_filenames:
        raise ValueError("pilot/formal lists do not partition canonical filenames")
    if not certifying_filenames <= formal_filenames:
        raise ValueError("certifying formal filenames are not a formal subset")
    if (len(input_rows), len(pilot_filenames), len(formal_filenames), len(certifying_filenames)) != (
        4757,
        153,
        1389,
        1345,
    ):
        raise ValueError("frozen row/image counts differ from Phase 3 bindings")

    first_round_by_id = {row.get("sample_id"): row for row in first_round_rows}
    if len(first_round_rows) != 4757 or len(first_round_by_id) != 4757:
        raise ValueError("first-round audit rows are incomplete or duplicated")
    image_status = {
        row["filename"]: row.get("status")
        for row in image_rows
        if isinstance(row.get("filename"), str)
    }
    row_keys = [row.get("row_key") for row in input_rows]
    duplicate_keys = {
        key for key, count in Counter(row_keys).items() if key is not None and count > 1
    }
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("project tokenizer does not provide fast offset mappings")

    results = []
    for row_index, row in enumerate(input_rows):
        sample_id = row.get("row_key")
        if sample_id not in first_round_by_id:
            raise ValueError(f"first-round evidence missing sample {sample_id}")
        filename = row.get("filename")
        scopes = {
            "canonical": True,
            "pilot": filename in pilot_filenames,
            "formal": filename in formal_filenames,
            "certifying_formal": filename in certifying_filenames,
        }
        extra = ["duplicate_sample_id"] if sample_id in duplicate_keys else []
        results.append(
            audit_row(
                row,
                tokenizer,
                row_index=row_index,
                first_round=first_round_by_id[sample_id],
                scope_flags=scopes,
                image_status=image_status.get(filename),
                extra_invalid_reasons=extra,
            )
        )

    certifying_rows = [
        row for row in results if row["scope_flags"]["certifying_formal"]
    ]
    if len(certifying_rows) != 4125:
        raise ValueError(
            f"certifying formal row count is {len(certifying_rows)}, expected 4125"
        )
    field_sets = Counter(
        ",".join(sorted(str(key) for key in row)) for row in input_rows
    )
    provenance = {
        "canonical_jsonl": str(input_jsonl),
        "canonical_jsonl_sha256": input_sha,
        "first_round_audit_jsonl": str(first_round_path),
        "first_round_audit_jsonl_sha256": first_round_sha,
        "image_manifest": str(image_manifest),
        "image_manifest_sha256": _sha256(image_manifest),
        "pilot_filenames": str(pilot_filenames_path),
        "pilot_filenames_sha256": _sha256(pilot_filenames_path),
        "formal_filenames": str(formal_filenames_path),
        "formal_filenames_sha256": _sha256(formal_filenames_path),
        "certifying_formal_filenames": str(certifying_filenames_path),
        "certifying_formal_filenames_sha256": _sha256(certifying_filenames_path),
        "tokenizer_path": str(tokenizer_path),
        "tokenizer_files_sha256": _tokenizer_hashes(tokenizer_path),
        "transformers_version": importlib.metadata.version("transformers"),
        "observed_canonical_field_sets": dict(field_sets),
    }
    summary = build_summary(results, provenance=provenance)
    image_group_coverage = build_image_group_coverage(certifying_rows)
    image_group_coverage["provenance"] = provenance
    jsonl_payload = b"".join(
        (
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        for row in results
    )
    _atomic_write(output_dir / "contrast_hull_audit.jsonl", jsonl_payload)
    _atomic_write(
        output_dir / "contrast_hull_summary.json",
        (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )
    _atomic_write(
        output_dir / "image_group_coverage.json",
        (
            json.dumps(
                image_group_coverage, ensure_ascii=False, indent=2, sort_keys=True
            )
            + "\n"
        ).encode("utf-8"),
    )
    _atomic_write(
        output_dir / "manual_review_samples.md",
        build_manual_review(results).encode("utf-8"),
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--image-manifest", type=Path, required=True)
    parser.add_argument("--pilot-filenames", type=Path, required=True)
    parser.add_argument("--formal-filenames", type=Path, required=True)
    parser.add_argument("--certifying-formal-filenames", type=Path, required=True)
    parser.add_argument("--first-round-audit", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--expected-input-sha256")
    parser.add_argument("--expected-first-round-sha256")
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    summary = run_audit(arguments)
    print(
        json.dumps(
            {
                "audit_version": summary["audit_version"],
                "output_dir": str(arguments.output_dir.resolve()),
                "scope_record_counts": {
                    name: values["record_count"]
                    for name, values in summary["scope_statistics"].items()
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
