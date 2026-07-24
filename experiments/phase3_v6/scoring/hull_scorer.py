"""Teacher-forced contrast-hull log-probability scoring."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable, Mapping

import torch

from experiments.phase3_v6.scoring.candidate_builder import (
    CandidatePair,
    TokenizedCandidate,
    collate_tokenized,
)
from experiments.phase3_v6.scoring.common import stable_sigmoid, utf8_key


def mean_target_logprob(
    logits: torch.Tensor, labels: torch.Tensor
) -> tuple[list[float], list[int]]:
    if logits.ndim != 3 or labels.ndim != 2:
        raise ValueError("logits/labels dimensions are invalid")
    if logits.shape[:2] != labels.shape:
        raise ValueError("logits/labels sequence shapes differ")
    shifted_logits = logits[:, :-1, :]
    shifted_labels = labels[:, 1:]
    valid = shifted_labels.ne(-100)
    counts = valid.sum(dim=1)
    if torch.any(counts <= 0):
        raise ValueError("a candidate has no teacher-forced target token")
    safe = shifted_labels.masked_fill(~valid, 0)
    log_probs = torch.log_softmax(shifted_logits.float(), dim=-1)
    gathered = log_probs.gather(-1, safe.unsqueeze(-1)).squeeze(-1)
    sums = (gathered.double() * valid.double()).sum(dim=1)
    means = sums / counts.double()
    if not torch.isfinite(means).all():
        raise FloatingPointError("non-finite target mean log probability")
    return means.detach().cpu().tolist(), counts.detach().cpu().tolist()


def score_candidate_batch(
    model,
    candidates: list[TokenizedCandidate],
    *,
    tokenizer,
    device: str,
    pixel_values: Any,
) -> tuple[list[float], list[int]]:
    input_ids, labels = collate_tokenized(
        candidates,
        pad_token_id=int(tokenizer.pad_token_id),
        device=device,
    )
    with torch.inference_mode():
        result = model(
            input_ids=input_ids,
            attention_mask=None,
            pixel_values=pixel_values,
        )
    return mean_target_logprob(result.logits, labels)


def context_filenames(
    target_filename: str, mismatch_row: Mapping[str, Any]
) -> list[str]:
    if mismatch_row.get("target_filename") != target_filename:
        raise ValueError("mismatch target filename differs from candidate group")
    rounds = mismatch_row.get("donor_rounds")
    if not isinstance(rounds, list) or [
        row.get("round_id") for row in rounds
    ] != [1, 2, 3, 4, 5]:
        raise ValueError("mismatch donor round order is invalid")
    return [target_filename] + [str(row["donor_filename"]) for row in rounds]


def _record_from_scores(
    pair: CandidatePair,
    context_names: list[str],
    context_values: list[tuple[float, float]],
    context_counts: list[tuple[int, int]],
) -> dict[str, Any]:
    if len(context_values) != 6 or len(context_counts) != 6:
        raise ValueError("record scoring requires six image contexts")
    q_values = [
        stable_sigmoid(positive - negative)
        for positive, negative in context_values
    ]
    mismatch = q_values[1:]
    q_k1 = mismatch[0]
    q_k3 = math.fsum(mismatch[:3]) / 3.0
    q_k5 = math.fsum(mismatch) / 5.0
    row: dict[str, Any] = {
        "sample_id": pair.sample_id,
        "filename": pair.filename,
        "negative_type": pair.negative_type,
        "selected_comparison_positive": pair.selected_comparison_positive,
        "selected_comparison_positive_label": (
            pair.selected_comparison_positive_label
        ),
        "second_round_category": pair.second_round_category,
        "hull_token_coverage": pair.maximum_hull_token_coverage,
        "positive_hull_token_count": context_counts[0][0],
        "negative_hull_token_count": context_counts[0][1],
        "audit_positive_hull_token_count": (
            pair.positive_hull_token_count_audit
        ),
        "audit_negative_hull_token_count": (
            pair.negative_hull_token_count_audit
        ),
        "candidate_evidence_sha256": pair.evidence_sha256,
        "q_correct": q_values[0],
        "q_mismatch_round_1": mismatch[0],
        "q_mismatch_round_2": mismatch[1],
        "q_mismatch_round_3": mismatch[2],
        "q_mismatch_round_4": mismatch[3],
        "q_mismatch_round_5": mismatch[4],
        "q_mismatch_k1": q_k1,
        "q_mismatch_k3": q_k3,
        "q_mismatch_k5": q_k5,
        "d_k1": q_values[0] - q_k1,
        "d_k3": q_values[0] - q_k3,
        "d_k5": q_values[0] - q_k5,
        "mean_logprob_positive_correct": context_values[0][0],
        "mean_logprob_negative_correct": context_values[0][1],
        "all_scores_finite": True,
        "context_filenames": {
            "correct": context_names[0],
            **{
                f"mismatch_round_{index}": context_names[index]
                for index in range(1, 6)
            },
        },
    }
    for round_id in range(1, 6):
        positive, negative = context_values[round_id]
        positive_count, negative_count = context_counts[round_id]
        row[f"mean_logprob_positive_mismatch_round_{round_id}"] = positive
        row[f"mean_logprob_negative_mismatch_round_{round_id}"] = negative
        row[f"positive_hull_token_count_mismatch_round_{round_id}"] = (
            positive_count
        )
        row[f"negative_hull_token_count_mismatch_round_{round_id}"] = (
            negative_count
        )
    numeric_values = [
        value
        for key, value in row.items()
        if isinstance(value, float) and key != "hull_token_coverage"
    ]
    if (
        not all(math.isfinite(value) for value in numeric_values)
        or not all(0.0 <= value <= 1.0 for value in q_values)
        or not all(-1.0 <= row[key] <= 1.0 for key in ("d_k1", "d_k3", "d_k5"))
    ):
        raise FloatingPointError(f"invalid record scores for {pair.sample_id}")
    return row


def score_filename_group(
    model,
    pairs: list[CandidatePair],
    *,
    mismatch_row: Mapping[str, Any],
    model_method: str,
    tokenizer,
    device: str,
    feature_cache=None,
) -> list[dict[str, Any]]:
    if not pairs:
        raise ValueError("cannot score an empty filename group")
    filename = pairs[0].filename
    if any(pair.filename != filename for pair in pairs):
        raise ValueError("filename scoring group contains multiple filenames")
    contexts = context_filenames(filename, mismatch_row)
    template_mode = "lm_only" if model_method == "M0" else "vlm"
    candidates: list[TokenizedCandidate] = []
    image_keys: list[str] = []
    index: list[tuple[int, int, str]] = []
    for pair_index, pair in enumerate(pairs):
        for context_index, context_filename in enumerate(contexts):
            for polarity in ("positive", "negative"):
                candidates.append(pair.templates[template_mode][polarity])
                image_keys.append(context_filename)
                index.append((pair_index, context_index, polarity))

    if model_method == "M0":
        means, counts = score_candidate_batch(
            model,
            candidates,
            tokenizer=tokenizer,
            device=device,
            pixel_values=None,
        )
    else:
        if feature_cache is None:
            raise ValueError("visual scoring requires a projected-feature cache")
        pixels = feature_cache.dummy_pixel_values(len(candidates))
        with feature_cache.activate(image_keys):
            means, counts = score_candidate_batch(
                model,
                candidates,
                tokenizer=tokenizer,
                device=device,
                pixel_values=pixels,
            )
    collected: dict[
        tuple[int, int], dict[str, tuple[float, int]]
    ] = defaultdict(dict)
    for item, mean, count in zip(index, means, counts):
        pair_index, context_index, polarity = item
        collected[(pair_index, context_index)][polarity] = (
            float(mean),
            int(count),
        )

    rows = []
    for pair_index, pair in enumerate(pairs):
        values: list[tuple[float, float]] = []
        token_counts: list[tuple[int, int]] = []
        for context_index in range(6):
            entry = collected[(pair_index, context_index)]
            if set(entry) != {"positive", "negative"}:
                raise RuntimeError("a record context lacks positive/negative scores")
            values.append((entry["positive"][0], entry["negative"][0]))
            token_counts.append(
                (entry["positive"][1], entry["negative"][1])
            )
        rows.append(
            _record_from_scores(pair, contexts, values, token_counts)
        )
    return rows


def group_pairs_by_filename(
    pairs: Iterable[CandidatePair],
) -> dict[str, list[CandidatePair]]:
    groups: dict[str, list[CandidatePair]] = defaultdict(list)
    for pair in pairs:
        groups[pair.filename].append(pair)
    return {
        filename: sorted(
            values,
            key=lambda pair: utf8_key(pair.sample_id),
        )
        for filename, values in sorted(
            groups.items(), key=lambda item: utf8_key(item[0])
        )
    }

