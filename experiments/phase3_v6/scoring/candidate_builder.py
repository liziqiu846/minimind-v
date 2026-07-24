"""Construct original-text hull candidates and prove every token boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import torch

from experiments.phase3.caption_template import build_caption_record
from experiments.phase3_v6.audit_v2.contrast_hull_audit import (
    build_alignment_view,
)
from experiments.phase3_v6.scoring.common import canonical_json_bytes, sha256_bytes


TEMPLATE_MODES = ("lm_only", "vlm")


@dataclass(frozen=True)
class TokenizedCandidate:
    input_ids: tuple[int, ...]
    labels: tuple[int, ...]
    target_positions: tuple[int, ...]
    target_token_ids: tuple[int, ...]
    target_token_text: str
    target_offset_mapping: tuple[tuple[int, int], ...]
    effective_label_start: int
    assistant_target_end: int
    input_length: int


@dataclass(frozen=True)
class CandidatePair:
    sample_id: str
    filename: str
    negative_type: str
    selected_comparison_positive: str
    selected_comparison_positive_label: str
    second_round_category: str
    common_prefix: str
    positive_hull: str
    negative_hull: str
    positive_candidate_text: str
    negative_candidate_text: str
    maximum_hull_token_coverage: float
    positive_hull_token_count_audit: int
    negative_hull_token_count_audit: int
    templates: Mapping[str, Mapping[str, TokenizedCandidate]]
    evidence: Mapping[str, Any]
    evidence_sha256: str


def _original_source(row: Mapping[str, Any]) -> tuple[str, str]:
    label = row.get("selected_comparison_positive_label")
    if label not in ("positive_1", "positive_2"):
        raise ValueError(f"invalid selected positive label for {row.get('sample_id')}")
    source = row.get(f"{label}_original")
    if not isinstance(source, str) or not source:
        raise ValueError(f"selected original positive is absent for {row.get('sample_id')}")
    if source != row.get("selected_comparison_positive"):
        raise ValueError(
            f"selected positive text/label disagree for {row.get('sample_id')}"
        )
    return label, source


def _tokenize_candidate(
    tokenizer,
    text: str,
    *,
    common_prefix_length: int,
    template_mode: str,
) -> tuple[TokenizedCandidate, dict[str, Any]]:
    if not 0 <= common_prefix_length < len(text):
        raise ValueError("candidate hull interval is empty or outside the text")
    record = build_caption_record(tokenizer, text, template_mode=template_mode)
    input_length = int(record["input_length_unpadded"])
    input_ids = record["input_ids"][:input_length].tolist()
    effective_start = int(record["effective_label_start"])
    assistant_end = int(record["assistant_target_end"])
    effective_ids = input_ids[effective_start:assistant_end]

    encoded = tokenizer(
        text + tokenizer.eos_token,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    local_ids = list(encoded.input_ids)
    offsets = [tuple(map(int, pair)) for pair in encoded.offset_mapping]
    if local_ids != effective_ids:
        raise ValueError("offset tokenizer IDs differ from frozen template IDs")
    hull_start = common_prefix_length
    hull_end = len(text)
    local_target = [
        index
        for index, (start, end) in enumerate(offsets)
        if end > hull_start and start < hull_end
    ]
    if not local_target:
        raise ValueError("candidate hull maps to no model token")
    if local_target != list(range(local_target[0], local_target[-1] + 1)):
        raise ValueError("candidate hull model tokens are not contiguous")
    if offsets[local_target[0]][0] > hull_start:
        raise ValueError("candidate hull left edge is not covered by a model token")
    if offsets[local_target[-1]][1] < hull_end:
        raise ValueError("candidate hull right edge is not covered by a model token")
    absolute_target = [effective_start + index for index in local_target]
    labels = [-100] * len(input_ids)
    for position in absolute_target:
        labels[position] = input_ids[position]
    if absolute_target[0] <= 0:
        raise ValueError("first hull token has no causal predecessor")
    if tokenizer.eos_token_id in [labels[position] for position in absolute_target]:
        raise ValueError("EOS entered the hull target mask")
    if sum(value != -100 for value in labels) != len(absolute_target):
        raise AssertionError("hull target label count mismatch")

    target_ids = tuple(input_ids[position] for position in absolute_target)
    target_offsets = tuple(offsets[index] for index in local_target)
    target_text = tokenizer.decode(list(target_ids))
    value = TokenizedCandidate(
        input_ids=tuple(input_ids),
        labels=tuple(labels),
        target_positions=tuple(absolute_target),
        target_token_ids=target_ids,
        target_token_text=target_text,
        target_offset_mapping=target_offsets,
        effective_label_start=effective_start,
        assistant_target_end=assistant_end,
        input_length=input_length,
    )
    evidence = {
        "input_ids": input_ids,
        "input_length": input_length,
        "effective_label_start": effective_start,
        "assistant_target_end": assistant_end,
        "target_positions": absolute_target,
        "target_token_ids": list(target_ids),
        "target_token_text": target_text,
        "target_offset_mapping": [list(pair) for pair in target_offsets],
        "effective_offset_mapping": [list(pair) for pair in offsets],
        "target_boundary_expansion_left": text[
            target_offsets[0][0] : hull_start
        ],
        "target_boundary_expansion_right": text[
            hull_end : target_offsets[-1][1]
        ],
        "eos_token_id": tokenizer.eos_token_id,
        "eos_is_unscored": True,
        "label_count": len(absolute_target),
    }
    return value, evidence


def _expand_target_left(
    tokenizer,
    value: TokenizedCandidate,
    evidence: dict[str, Any],
    *,
    new_start: int,
    hull_start: int,
    text: str,
) -> tuple[TokenizedCandidate, dict[str, Any]]:
    old_start = value.target_positions[0]
    if new_start > old_start:
        raise ValueError("target expansion cannot move right")
    if new_start == old_start:
        return value, evidence
    if new_start < value.effective_label_start:
        raise ValueError("token-boundary expansion entered the template prefix")
    positions = tuple(range(new_start, value.target_positions[-1] + 1))
    labels = [-100] * value.input_length
    for position in positions:
        labels[position] = value.input_ids[position]
    local_start = new_start - value.effective_label_start
    local_end = positions[-1] - value.effective_label_start
    all_offsets = [
        tuple(map(int, pair))
        for pair in evidence["effective_offset_mapping"]
    ]
    offsets = tuple(all_offsets[local_start : local_end + 1])
    if any(end > hull_start for start, end in offsets[: old_start - new_start]):
        # An added token may touch the hull boundary, but it may not lie inside a
        # disjoint natural-language suffix (there is no such suffix here).
        pass
    target_ids = tuple(value.input_ids[position] for position in positions)
    updated = TokenizedCandidate(
        input_ids=value.input_ids,
        labels=tuple(labels),
        target_positions=positions,
        target_token_ids=target_ids,
        target_token_text=tokenizer.decode(list(target_ids)),
        target_offset_mapping=offsets,
        effective_label_start=value.effective_label_start,
        assistant_target_end=value.assistant_target_end,
        input_length=value.input_length,
    )
    updated_evidence = dict(evidence)
    updated_evidence.update(
        {
            "target_positions": list(positions),
            "target_token_ids": list(target_ids),
            "target_token_text": updated.target_token_text,
            "target_offset_mapping": [list(pair) for pair in offsets],
            "target_boundary_expansion_left": text[
                offsets[0][0] : hull_start
            ],
            "label_count": len(positions),
            "pairwise_prefix_expansion_token_count": old_start - new_start,
        }
    )
    return updated, updated_evidence


def build_candidate_pair(tokenizer, row: Mapping[str, Any]) -> CandidatePair:
    sample_id = str(row["sample_id"])
    label, positive_original = _original_source(row)
    negative_original = row.get("negative_original")
    if not isinstance(negative_original, str) or not negative_original:
        raise ValueError(f"negative original is absent for {sample_id}")
    positive_interval = row.get("positive_hull_original_character_interval")
    negative_interval = row.get("negative_hull_original_character_interval")
    if (
        not isinstance(positive_interval, list)
        or len(positive_interval) != 2
        or not isinstance(negative_interval, list)
        or len(negative_interval) != 2
    ):
        raise ValueError(f"invalid original hull intervals for {sample_id}")
    positive_start, positive_end = map(int, positive_interval)
    negative_start, negative_end = map(int, negative_interval)
    if not 0 <= positive_start < positive_end <= len(positive_original):
        raise ValueError(f"positive hull interval is out of bounds for {sample_id}")
    if not 0 <= negative_start < negative_end <= len(negative_original):
        raise ValueError(f"negative hull interval is out of bounds for {sample_id}")

    prefix_lexeme_count = len(row["common_prefix_lexemes"])
    positive_offsets = row.get(
        f"{label}_original_character_offsets"
    )
    negative_offsets = row.get("negative_original_character_offsets")
    if not isinstance(positive_offsets, list) or not isinstance(
        negative_offsets, list
    ):
        raise ValueError(f"original lexeme offsets are absent for {sample_id}")
    if prefix_lexeme_count:
        if (
            len(positive_offsets) < prefix_lexeme_count
            or len(negative_offsets) < prefix_lexeme_count
        ):
            raise ValueError(f"common-prefix offsets are incomplete for {sample_id}")
        positive_boundary = int(
            positive_offsets[prefix_lexeme_count - 1][1]
        )
        negative_boundary = int(
            negative_offsets[prefix_lexeme_count - 1][1]
        )
    else:
        positive_boundary = 0
        negative_boundary = 0
    if not 0 <= positive_boundary <= positive_start:
        raise ValueError(f"positive scoring boundary is invalid for {sample_id}")
    if not 0 <= negative_boundary <= negative_start:
        raise ValueError(f"negative scoring boundary is invalid for {sample_id}")

    common_prefix = positive_original[:positive_boundary]
    positive_hull = positive_original[positive_boundary:positive_end]
    negative_hull = negative_original[negative_boundary:negative_end]
    positive_semantic_hull = positive_original[positive_start:positive_end]
    negative_semantic_hull = negative_original[negative_start:negative_end]
    positive_text = common_prefix + positive_hull
    negative_text = common_prefix + negative_hull
    if not positive_text or not negative_text:
        raise ValueError(f"empty formal candidate for {sample_id}")

    expected_positive_lexemes = list(row["common_prefix_lexemes"]) + list(
        row["positive_contrast_hull_lexemes"]
    )
    expected_negative_lexemes = list(row["common_prefix_lexemes"]) + list(
        row["negative_contrast_hull_lexemes"]
    )
    positive_view = build_alignment_view(positive_text)
    negative_view = build_alignment_view(negative_text)
    if positive_view["alignment_lexemes"] != expected_positive_lexemes:
        raise ValueError(f"positive candidate stitch invariant failed for {sample_id}")
    if negative_view["alignment_lexemes"] != expected_negative_lexemes:
        raise ValueError(f"negative candidate stitch invariant failed for {sample_id}")
    if (
        build_alignment_view(positive_semantic_hull)["alignment_lexemes"]
        != list(row["positive_contrast_hull_lexemes"])
    ):
        raise ValueError(f"positive raw/alignment hull mismatch for {sample_id}")
    if (
        build_alignment_view(negative_semantic_hull)["alignment_lexemes"]
        != list(row["negative_contrast_hull_lexemes"])
    ):
        raise ValueError(f"negative raw/alignment hull mismatch for {sample_id}")
    if max(
        float(row["positive_hull_token_coverage"]),
        float(row["negative_hull_token_coverage"]),
    ) != float(row["maximum_hull_token_coverage"]):
        raise ValueError(f"maximum coverage invariant failed for {sample_id}")

    templates: dict[str, dict[str, TokenizedCandidate]] = {}
    template_evidence: dict[str, Any] = {}
    for template_mode in TEMPLATE_MODES:
        positive, positive_evidence = _tokenize_candidate(
            tokenizer,
            positive_text,
            common_prefix_length=len(common_prefix),
            template_mode=template_mode,
        )
        negative, negative_evidence = _tokenize_candidate(
            tokenizer,
            negative_text,
            common_prefix_length=len(common_prefix),
            template_mode=template_mode,
        )
        common_length = 0
        for left_id, right_id in zip(positive.input_ids, negative.input_ids):
            if left_id != right_id:
                break
            common_length += 1
        shared_target_start = min(
            positive.target_positions[0],
            negative.target_positions[0],
            common_length,
        )
        positive, positive_evidence = _expand_target_left(
            tokenizer,
            positive,
            positive_evidence,
            new_start=shared_target_start,
            hull_start=len(common_prefix),
            text=positive_text,
        )
        negative, negative_evidence = _expand_target_left(
            tokenizer,
            negative,
            negative_evidence,
            new_start=shared_target_start,
            hull_start=len(common_prefix),
            text=negative_text,
        )
        positive_prefix = positive.input_ids[: positive.target_positions[0]]
        negative_prefix = negative.input_ids[: negative.target_positions[0]]
        if positive_prefix != negative_prefix:
            raise ValueError(
                f"positive/negative model-token prefixes differ for {sample_id} "
                f"under {template_mode}"
            )
        positive_effective_tail = positive.input_ids[
            positive.target_positions[-1] + 1 : positive.assistant_target_end
        ]
        negative_effective_tail = negative.input_ids[
            negative.target_positions[-1] + 1 : negative.assistant_target_end
        ]
        if positive_effective_tail != (tokenizer.eos_token_id,):
            raise ValueError(
                f"positive candidate has non-EOS suffix for {sample_id}"
            )
        if negative_effective_tail != (tokenizer.eos_token_id,):
            raise ValueError(
                f"negative candidate has non-EOS suffix for {sample_id}"
            )
        positive_template_tail = positive.input_ids[
            positive.assistant_target_end :
        ]
        negative_template_tail = negative.input_ids[
            negative.assistant_target_end :
        ]
        if positive_template_tail != negative_template_tail:
            raise ValueError(
                f"positive/negative post-EOS template tokens differ for {sample_id}"
            )
        templates[template_mode] = {
            "positive": positive,
            "negative": negative,
        }
        template_evidence[template_mode] = {
            "positive": positive_evidence,
            "negative": negative_evidence,
            "shared_prefix_token_ids": list(positive_prefix),
            "shared_prefix_token_count": len(positive_prefix),
            "shared_post_eos_template_token_ids": list(
                positive_template_tail
            ),
            "only_hull_tokens_differ_before_common_eos": True,
        }

    evidence: dict[str, Any] = {
        "sample_id": sample_id,
        "filename": row["filename"],
        "selected_comparison_positive_label": label,
        "selected_positive_original": positive_original,
        "negative_original": negative_original,
        "positive_hull_original_character_interval": [
            positive_start,
            positive_end,
        ],
        "negative_hull_original_character_interval": [
            negative_start,
            negative_end,
        ],
        "positive_scoring_hull_original_character_interval": [
            positive_boundary,
            positive_end,
        ],
        "negative_scoring_hull_original_character_interval": [
            negative_boundary,
            negative_end,
        ],
        "common_prefix_original": common_prefix,
        "positive_semantic_hull_original": positive_semantic_hull,
        "negative_semantic_hull_original": negative_semantic_hull,
        "positive_scoring_hull_original": positive_hull,
        "negative_scoring_hull_original": negative_hull,
        "positive_boundary_expansion_original": positive_original[
            positive_boundary:positive_start
        ],
        "negative_boundary_expansion_original": negative_original[
            negative_boundary:negative_start
        ],
        "positive_original_reconstruction_exact": (
            common_prefix
            + positive_hull
            + positive_original[positive_end:]
            == positive_original
        ),
        "negative_original_reconstruction_exact": (
            negative_original[:negative_boundary]
            + negative_hull
            + negative_original[negative_end:]
            == negative_original
        ),
        "negative_uses_selected_positive_common_prefix": True,
        "positive_candidate_text": positive_text,
        "negative_candidate_text": negative_text,
        "positive_candidate_alignment_lexemes": positive_view[
            "alignment_lexemes"
        ],
        "negative_candidate_alignment_lexemes": negative_view[
            "alignment_lexemes"
        ],
        "positive_expected_alignment_lexemes": expected_positive_lexemes,
        "negative_expected_alignment_lexemes": expected_negative_lexemes,
        "maximum_hull_token_coverage": float(
            row["maximum_hull_token_coverage"]
        ),
        "templates": template_evidence,
    }
    if not evidence["positive_original_reconstruction_exact"]:
        raise ValueError(f"positive original reconstruction failed for {sample_id}")
    if not evidence["negative_original_reconstruction_exact"]:
        raise ValueError(f"negative original reconstruction failed for {sample_id}")
    evidence_sha = sha256_bytes(canonical_json_bytes(evidence))
    return CandidatePair(
        sample_id=sample_id,
        filename=str(row["filename"]),
        negative_type=str(row["negative_type"]),
        selected_comparison_positive=str(row["selected_comparison_positive"]),
        selected_comparison_positive_label=label,
        second_round_category=str(row["second_round_category"]),
        common_prefix=common_prefix,
        positive_hull=positive_hull,
        negative_hull=negative_hull,
        positive_candidate_text=positive_text,
        negative_candidate_text=negative_text,
        maximum_hull_token_coverage=float(
            row["maximum_hull_token_coverage"]
        ),
        positive_hull_token_count_audit=int(
            row["positive_hull_model_token_count"]
        ),
        negative_hull_token_count_audit=int(
            row["negative_hull_model_token_count"]
        ),
        templates=templates,
        evidence=evidence,
        evidence_sha256=evidence_sha,
    )


def prevalidate_candidates(tokenizer, rows: list[dict[str, Any]]) -> list[CandidatePair]:
    pairs = [build_candidate_pair(tokenizer, row) for row in rows]
    if len(pairs) != len(rows):
        raise AssertionError("candidate prevalidation changed the row count")
    if len({pair.sample_id for pair in pairs}) != len(pairs):
        raise ValueError("candidate prevalidation produced duplicate sample IDs")
    return pairs


def collate_tokenized(
    values: list[TokenizedCandidate],
    *,
    pad_token_id: int,
    device: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    if not values:
        raise ValueError("cannot collate an empty candidate batch")
    maximum = max(value.input_length for value in values)
    ids = []
    labels = []
    for value in values:
        padding = maximum - value.input_length
        ids.append(list(value.input_ids) + [pad_token_id] * padding)
        labels.append(list(value.labels) + [-100] * padding)
    return (
        torch.tensor(ids, dtype=torch.long, device=device),
        torch.tensor(labels, dtype=torch.long, device=device),
    )
