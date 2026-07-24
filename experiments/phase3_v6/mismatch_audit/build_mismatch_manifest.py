#!/usr/bin/env python3
"""Build a deterministic balanced K=5 image-mismatch manifest and diagnostics.

This module performs data and structure auditing only. It never loads MiniMind-V,
never reads model scores, and never uses text diagnostics to alter assignments.
"""

from __future__ import annotations

import argparse
import bisect
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import random
import re
import shutil
import statistics
import sys
import tempfile
import unicodedata
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from PIL import Image, ImageOps
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.phase3_v6.audit_v2.contrast_hull_audit import build_alignment_view


SCHEMA_VERSION = 1
AUDIT_VERSION = "phase3-v6-mismatch-audit-v1"
RANDOM_SEED = 3407
ROUND_COUNT = 5
EXPECTED_IMAGE_COUNT = 1345
EXPECTED_PAIR_COUNT = EXPECTED_IMAGE_COUNT * ROUND_COUNT
ASSIGNMENT_TAG = "phase3-v6-mismatch-v1"
BASELINE_TAG = "phase3-v6-mismatch-baseline-v1"
BASELINE_SAMPLE_SIZE = 100_000
NORMALIZED_PIXEL_SIZE = (256, 256)
THUMBNAIL_SIZE = (256, 256)
REVIEW_LIMIT = 30
VALID_V6_EXCLUDED_CATEGORIES = {
    "ambiguous_comparison_positive",
    "surface_only_or_degenerate",
    "token_mapping_problem",
    "invalid_sample",
}
WORD_RE = re.compile(r"(?u)\b[\w]+(?:[-'][\w]+)*\b")
TFIDF_BINS = (
    (0.0, 0.05, "[0,0.05)"),
    (0.05, 0.10, "[0.05,0.10)"),
    (0.10, 0.20, "[0.10,0.20)"),
    (0.20, 0.30, "[0.20,0.30)"),
    (0.30, 0.50, "[0.30,0.50)"),
    (0.50, 0.75, "[0.50,0.75)"),
    (0.75, 1.000000000001, "[0.75,1.00]"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def read_filename_list(path: Path) -> list[str]:
    names = path.read_text(encoding="utf-8").splitlines()
    if not names or any(not name for name in names):
        raise ValueError(f"empty filename entry in {path}")
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate filenames in {path}")
    return names


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


def _json_bytes(value: Any, *, indent: int | None = None) -> bytes:
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
    )
    return (text + ("\n" if indent is not None else "")).encode("utf-8")


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(_json_bytes(dict(row)) + b"\n" for row in rows)


def _hash_bits(bits: Iterable[bool]) -> str:
    value = 0
    count = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
        count += 1
    if count != 64:
        raise ValueError(f"expected 64 hash bits, observed {count}")
    return f"{value:016x}"


def difference_hash(image: Image.Image) -> str:
    grayscale = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = np.asarray(grayscale, dtype=np.uint8)
    return _hash_bits((pixels[:, 1:] > pixels[:, :-1]).reshape(-1).tolist())


def average_hash(image: Image.Image) -> str:
    grayscale = image.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
    pixels = np.asarray(grayscale, dtype=np.float64)
    return _hash_bits((pixels >= float(pixels.mean())).reshape(-1).tolist())


def hamming64(left: str, right: str) -> int:
    if len(left) != 16 or len(right) != 16:
        raise ValueError("64-bit hashes must have exactly 16 hexadecimal characters")
    return (int(left, 16) ^ int(right, 16)).bit_count()


def image_fingerprint(path: Path) -> dict[str, Any]:
    payload_sha256 = sha256_file(path)
    size_bytes = path.stat().st_size
    try:
        with Image.open(path) as opened:
            opened.load()
            original_width, original_height = opened.size
            original_mode = opened.mode
            oriented = ImageOps.exif_transpose(opened)
            rgb = oriented.convert("RGB")
    except Exception as error:
        raise ValueError(f"image decode failed for {path}: {type(error).__name__}: {error}") from error
    normalized = rgb.resize(NORMALIZED_PIXEL_SIZE, Image.Resampling.LANCZOS)
    normalized_sha256 = sha256_bytes(normalized.tobytes())
    return {
        "image_path": str(path.resolve()),
        "image_sha256": payload_sha256,
        "image_size_bytes": int(size_bytes),
        "width": int(original_width),
        "height": int(original_height),
        "mode": str(original_mode),
        "normalized_pixel_size": list(NORMALIZED_PIXEL_SIZE),
        "normalized_pixel_sha256": normalized_sha256,
        "difference_hash": difference_hash(rgb),
        "average_hash": average_hash(rgb),
    }


def hard_exclusion_reasons(left: Mapping[str, Any], right: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if left["filename"] == right["filename"]:
        reasons.append("same_filename")
    if int(left["numeric_coco_id"]) == int(right["numeric_coco_id"]):
        reasons.append("same_coco_image_id")
    if left["image_sha256"] == right["image_sha256"]:
        reasons.append("same_file_sha256")
    if left["normalized_pixel_sha256"] == right["normalized_pixel_sha256"]:
        reasons.append("same_normalized_pixel_sha256")
    if (
        hamming64(left["difference_hash"], right["difference_hash"]) <= 1
        and hamming64(left["average_hash"], right["average_hash"]) <= 1
    ):
        reasons.append("hard_perceptual_near_duplicate")
    return reasons


def near_duplicate_suspect(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        hamming64(left["difference_hash"], right["difference_hash"]) <= 4
        or hamming64(left["average_hash"], right["average_hash"]) <= 4
    )


def assignment_seed_material(round_id: int, target: str, donor: str) -> str:
    return (
        f"{ASSIGNMENT_TAG}|seed={RANDOM_SEED}|round={round_id}|"
        f"target={target}|donor={donor}"
    )


def assignment_order_digest(round_id: int, target: str, donor: str) -> bytes:
    return hashlib.sha256(
        assignment_seed_material(round_id, target, donor).encode("utf-8")
    ).digest()


def deterministic_perfect_matching(
    filenames: Sequence[str],
    allowed_donors: Sequence[Sequence[int]],
    *,
    round_id: int,
    previously_used: Sequence[set[int]] | None = None,
) -> list[int]:
    """Return donor index per target using deterministic Hopcroft-Karp."""
    count = len(filenames)
    if len(allowed_donors) != count:
        raise ValueError("allowed donor adjacency length mismatch")
    previous = previously_used or [set() for _ in range(count)]
    if len(previous) != count:
        raise ValueError("previously-used donor length mismatch")
    adjacency: list[list[int]] = []
    for target_index, donors in enumerate(allowed_donors):
        target = filenames[target_index]
        candidates = [donor for donor in donors if donor not in previous[target_index]]
        candidates.sort(
            key=lambda donor: (
                assignment_order_digest(round_id, target, filenames[donor]),
                filenames[donor].encode("utf-8"),
            )
        )
        adjacency.append(candidates)
    if any(not donors for donors in adjacency):
        raise RuntimeError(f"round {round_id} has a target with no allowed donor")

    unmatched = -1
    pair_left = [unmatched] * count
    pair_right = [unmatched] * count
    distance = [0] * count
    infinity = count + 1

    def bfs() -> bool:
        queue: deque[int] = deque()
        found = False
        for target_index in range(count):
            if pair_left[target_index] == unmatched:
                distance[target_index] = 0
                queue.append(target_index)
            else:
                distance[target_index] = infinity
        while queue:
            target_index = queue.popleft()
            for donor_index in adjacency[target_index]:
                paired_target = pair_right[donor_index]
                if paired_target == unmatched:
                    found = True
                elif distance[paired_target] == infinity:
                    distance[paired_target] = distance[target_index] + 1
                    queue.append(paired_target)
        return found

    def dfs(target_index: int) -> bool:
        for donor_index in adjacency[target_index]:
            paired_target = pair_right[donor_index]
            if paired_target == unmatched or (
                distance[paired_target] == distance[target_index] + 1
                and dfs(paired_target)
            ):
                pair_left[target_index] = donor_index
                pair_right[donor_index] = target_index
                return True
        distance[target_index] = infinity
        return False

    matched = 0
    while bfs():
        for target_index in range(count):
            if pair_left[target_index] == unmatched and dfs(target_index):
                matched += 1
    if matched != count or any(value == unmatched for value in pair_left):
        raise RuntimeError(
            f"round {round_id} has no perfect matching: matched {matched}/{count}"
        )
    if len(set(pair_left)) != count:
        raise RuntimeError(f"round {round_id} matching reused a donor")
    return pair_left


def build_k_matchings(
    images: Sequence[Mapping[str, Any]],
    allowed_donors: Sequence[Sequence[int]],
    *,
    round_count: int = ROUND_COUNT,
) -> list[list[int]]:
    filenames = [str(image["filename"]) for image in images]
    previously_used = [set() for _ in images]
    rounds: list[list[int]] = []
    for round_id in range(1, round_count + 1):
        matching = deterministic_perfect_matching(
            filenames,
            allowed_donors,
            round_id=round_id,
            previously_used=previously_used,
        )
        for target_index, donor_index in enumerate(matching):
            previously_used[target_index].add(donor_index)
        rounds.append(matching)
    if any(len(values) != round_count for values in previously_used):
        raise RuntimeError("a target did not receive distinct donors across rounds")
    return rounds


def validate_matchings(
    images: Sequence[Mapping[str, Any]],
    rounds: Sequence[Sequence[int]],
) -> list[dict[str, Any]]:
    count = len(images)
    per_round: list[dict[str, Any]] = []
    donors_by_target = [set() for _ in images]
    for round_offset, matching in enumerate(rounds, 1):
        if len(matching) != count:
            raise RuntimeError(f"round {round_offset} target count mismatch")
        donor_count = len(set(matching))
        self_count = 0
        hard_count = 0
        for target_index, donor_index in enumerate(matching):
            donors_by_target[target_index].add(int(donor_index))
            if target_index == donor_index:
                self_count += 1
            if hard_exclusion_reasons(images[target_index], images[donor_index]):
                hard_count += 1
        row = {
            "round_id": round_offset,
            "target_count": count,
            "donor_count": len(matching),
            "unique_donor_count": donor_count,
            "self_match_count": self_count,
            "hard_excluded_pair_count": hard_count,
            "is_valid_bijection_derangement": (
                donor_count == count and self_count == 0 and hard_count == 0
            ),
        }
        if not row["is_valid_bijection_derangement"]:
            raise RuntimeError(f"round validation failed: {row}")
        per_round.append(row)
    if any(len(values) != len(rounds) for values in donors_by_target):
        raise RuntimeError("a target repeats a donor across rounds")
    return per_round


def _percentile(values: Sequence[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def numeric_distribution(values: Iterable[float | int]) -> dict[str, Any]:
    clean = [float(value) for value in values]
    return {
        "count": len(clean),
        "mean": statistics.fmean(clean) if clean else None,
        "median": statistics.median(clean) if clean else None,
        "p75": _percentile(clean, 0.75),
        "p90": _percentile(clean, 0.90),
        "p95": _percentile(clean, 0.95),
        "maximum": max(clean) if clean else None,
        "minimum": min(clean) if clean else None,
    }


def tfidf_distribution(values: Iterable[float]) -> dict[str, Any]:
    clean = [min(1.0, max(0.0, float(value))) for value in values]
    output = numeric_distribution(clean)
    counts = Counter()
    for value in clean:
        for lower, upper, label in TFIDF_BINS:
            if lower <= value < upper:
                counts[label] += 1
                break
    output["bins"] = {
        label: {
            "count": counts[label],
            "proportion": counts[label] / len(clean) if clean else 0.0,
        }
        for _, _, label in TFIDF_BINS
    }
    return output


def normalize_positive_text(text: str) -> str:
    return build_alignment_view(text)["alignment_text"]


def diagnostic_tokens(text: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return tuple(match.group(0) for match in WORD_RE.finditer(normalized))


def unigram_bigram_features(tokens: Sequence[str]) -> frozenset[str]:
    unigrams = {f"u:{token}" for token in tokens}
    bigrams = {
        f"b:{tokens[index]}\u241f{tokens[index + 1]}"
        for index in range(len(tokens) - 1)
    }
    return frozenset(unigrams | bigrams)


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


@dataclass(frozen=True)
class CaptionDiagnostic:
    raw: str
    normalized: str
    unigrams: frozenset[str]
    unigram_bigrams: frozenset[str]
    content_words: frozenset[str]


def build_caption_diagnostics(texts: Iterable[str]) -> tuple[CaptionDiagnostic, ...]:
    rows = []
    for raw in sorted(set(texts), key=lambda value: value.encode("utf-8")):
        tokens = diagnostic_tokens(raw)
        rows.append(
            CaptionDiagnostic(
                raw=raw,
                normalized=normalize_positive_text(raw),
                unigrams=frozenset(tokens),
                unigram_bigrams=unigram_bigram_features(tokens),
                content_words=frozenset(
                    token
                    for token in tokens
                    if token not in ENGLISH_STOP_WORDS and any(char.isalnum() for char in token)
                ),
            )
        )
    if not rows:
        raise ValueError("an image has no positive descriptions")
    return tuple(rows)


def lexical_pair_metrics(
    left: Sequence[CaptionDiagnostic], right: Sequence[CaptionDiagnostic]
) -> dict[str, Any]:
    maximum_unigram = 0.0
    maximum_unigram_bigram = 0.0
    maximum_content_overlap = 0.0
    exact = False
    for left_caption in left:
        for right_caption in right:
            maximum_unigram = max(
                maximum_unigram,
                _jaccard(left_caption.unigrams, right_caption.unigrams),
            )
            maximum_unigram_bigram = max(
                maximum_unigram_bigram,
                _jaccard(
                    left_caption.unigram_bigrams,
                    right_caption.unigram_bigrams,
                ),
            )
            exact = exact or left_caption.normalized == right_caption.normalized
            smaller = min(
                len(left_caption.content_words), len(right_caption.content_words)
            )
            if smaller:
                maximum_content_overlap = max(
                    maximum_content_overlap,
                    len(left_caption.content_words & right_caption.content_words)
                    / smaller,
                )
    return {
        "maximum_unigram_jaccard": maximum_unigram,
        "maximum_unigram_bigram_jaccard": maximum_unigram_bigram,
        "has_exact_normalized_positive_caption": exact,
        "maximum_smaller_side_content_word_overlap": maximum_content_overlap,
        "has_high_content_word_overlap": maximum_content_overlap >= 0.5,
    }


def build_tfidf_matrix(
    filenames: Sequence[str],
    captions_by_filename: Mapping[str, Sequence[CaptionDiagnostic]],
) -> tuple[Any, dict[str, list[int]], dict[str, Any]]:
    documents: list[str] = []
    indices: dict[str, list[int]] = {}
    for filename in filenames:
        indices[filename] = []
        for caption in captions_by_filename[filename]:
            indices[filename].append(len(documents))
            documents.append(caption.raw)
    analyzer = TfidfVectorizer(
        lowercase=True, stop_words="english", ngram_range=(1, 2)
    ).build_analyzer()
    vocabulary_terms = sorted(
        {term for document in documents for term in analyzer(document)},
        key=lambda value: value.encode("utf-8"),
    )
    vocabulary = {term: index for index, term in enumerate(vocabulary_terms)}
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        vocabulary=vocabulary,
        dtype=np.float64,
        norm="l2",
    )
    matrix = vectorizer.fit_transform(documents)
    metadata = {
        "lowercase": True,
        "stop_words": "english",
        "ngram_range": [1, 2],
        "vocabulary_order": "UTF-8 bytewise sorted",
        "vocabulary_size": len(vocabulary_terms),
        "vocabulary_sha256": sha256_bytes(
            ("\n".join(vocabulary_terms) + "\n").encode("utf-8")
        ),
        "document_count": len(documents),
    }
    return matrix, indices, metadata


def maximum_tfidf_for_pairs(
    pairs: Sequence[tuple[int, int]],
    filenames: Sequence[str],
    matrix: Any,
    caption_indices: Mapping[str, Sequence[int]],
) -> dict[tuple[int, int], float]:
    requested: dict[int, set[int]] = defaultdict(set)
    for target_index, donor_index in pairs:
        requested[int(target_index)].add(int(donor_index))
    output: dict[tuple[int, int], float] = {}
    for target_index in sorted(requested):
        target_rows = list(caption_indices[filenames[target_index]])
        donors = sorted(requested[target_index])
        flat_donor_rows: list[int] = []
        slices: dict[int, tuple[int, int]] = {}
        for donor_index in donors:
            start = len(flat_donor_rows)
            flat_donor_rows.extend(caption_indices[filenames[donor_index]])
            slices[donor_index] = (start, len(flat_donor_rows))
        products = (matrix[target_rows] @ matrix[flat_donor_rows].T).toarray()
        for donor_index in donors:
            start, end = slices[donor_index]
            output[(target_index, donor_index)] = float(products[:, start:end].max())
    return output


def sample_allowed_pairs(
    allowed_donors: Sequence[Sequence[int]],
    sample_size: int = BASELINE_SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
) -> list[tuple[int, int]]:
    cumulative = [0]
    for donors in allowed_donors:
        cumulative.append(cumulative[-1] + len(donors))
    total = cumulative[-1]
    if sample_size > total:
        raise ValueError(f"baseline sample {sample_size} exceeds {total} allowed pairs")
    positions = sorted(random.Random(seed).sample(range(total), sample_size))
    pairs: list[tuple[int, int]] = []
    for position in positions:
        target_index = bisect.bisect_right(cumulative, position) - 1
        offset = position - cumulative[target_index]
        pairs.append((target_index, int(allowed_donors[target_index][offset])))
    return pairs


def hull_mention_classification(
    donor_lexemes: set[str],
    positive_hull: Sequence[str],
    negative_hull: Sequence[str],
) -> dict[str, Any]:
    positive = {
        str(lexeme).casefold()
        for lexeme in positive_hull
        if any(char.isalnum() for char in str(lexeme))
    }
    negative = {
        str(lexeme).casefold()
        for lexeme in negative_hull
        if any(char.isalnum() for char in str(lexeme))
    }
    positive_intersection = positive & donor_lexemes
    negative_intersection = negative & donor_lexemes
    mentions_positive = bool(positive_intersection)
    mentions_negative = bool(negative_intersection)
    if mentions_positive and mentions_negative:
        classification = "mentions_both"
    elif mentions_positive:
        classification = "mentions_positive_only"
    elif mentions_negative:
        classification = "mentions_negative_only"
    else:
        classification = "mentions_neither"
    return {
        "classification": classification,
        "positive_hull_lexemes_considered": sorted(positive),
        "negative_hull_lexemes_considered": sorted(negative),
        "matched_positive_hull_lexemes": sorted(positive_intersection),
        "matched_negative_hull_lexemes": sorted(negative_intersection),
    }


def generate_thumbnail(source: Path, destination: Path) -> None:
    with Image.open(source) as opened:
        opened.load()
        image = ImageOps.exif_transpose(opened).convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", THUMBNAIL_SIZE, "white")
    left = (THUMBNAIL_SIZE[0] - image.width) // 2
    top = (THUMBNAIL_SIZE[1] - image.height) // 2
    canvas.paste(image, (left, top))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(
        destination,
        format="JPEG",
        quality=85,
        optimize=False,
        progressive=False,
        subsampling=2,
    )


def projected_inference_counts(
    valid_record_count: int,
    effective_target_filenames: set[str],
    filenames: Sequence[str],
    rounds: Sequence[Sequence[int]],
    model_count: int = 10,
) -> dict[str, Any]:
    filename_index = {filename: index for index, filename in enumerate(filenames)}
    effective_indices = sorted(filename_index[name] for name in effective_target_filenames)
    output: dict[str, Any] = {}
    for k in (1, 3, 5):
        image_contexts = valid_record_count * (1 + k)
        sequence_scores = image_contexts * 2
        unique_images = set(effective_indices)
        for matching in rounds[:k]:
            unique_images.update(matching[index] for index in effective_indices)
        output[f"K={k}"] = {
            "definition": f"correct image plus mismatch rounds 1-{k}",
            "per_model_text_sequence_score_count": sequence_scores,
            "ten_model_text_sequence_score_count": sequence_scores * model_count,
            "per_model_image_context_record_count_without_feature_cache": image_contexts,
            "ten_model_image_context_record_count_without_feature_cache": (
                image_contexts * model_count
            ),
            "per_model_unique_image_encoding_count_with_global_filename_cache": len(
                unique_images
            ),
            "ten_model_unique_image_encoding_count_with_global_filename_cache": (
                len(unique_images) * model_count
            ),
            "candidate_sequences_per_image_context": 2,
        }
    return {
        "valid_v6_record_count": valid_record_count,
        "effective_v6_image_count": len(effective_target_filenames),
        "frozen_model_count": model_count,
        "counts": output,
        "static_code_inspection": {
            "files": ["experiments/phase3/runner_common.py"],
            "observed_behavior": (
                "v4/v5 decodes and preprocesses once per filename/model group, but "
                "does not expose a persistent cache of post-vision-encoder features"
            ),
            "formal_code_modified": False,
        },
    }


def _ensure_expected_sha(path: Path, expected: str | None, label: str) -> str:
    observed = sha256_file(path)
    if expected and observed != expected:
        raise ValueError(
            f"{label} SHA-256 mismatch: observed {observed}, expected {expected}"
        )
    return observed


def bind_and_fingerprint_inputs(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "certifying_formal_filenames": args.certifying_formal_filenames.resolve(),
        "image_manifest": args.image_manifest.resolve(),
        "canonical_jsonl": args.canonical_jsonl.resolve(),
        "contrast_hull_audit_jsonl": args.contrast_hull_audit.resolve(),
        "contrast_hull_summary_json": args.contrast_hull_summary.resolve(),
        "coco_root": args.coco_root.resolve(),
    }
    if not paths["coco_root"].is_dir():
        raise FileNotFoundError(paths["coco_root"])
    expected = {
        "certifying_formal_filenames": args.expected_certifying_sha256,
        "image_manifest": args.expected_image_manifest_sha256,
        "canonical_jsonl": args.expected_canonical_sha256,
        "contrast_hull_audit_jsonl": args.expected_contrast_audit_sha256,
        "contrast_hull_summary_json": args.expected_contrast_summary_sha256,
    }
    input_sha256 = {
        key: _ensure_expected_sha(paths[key], value, key)
        for key, value in expected.items()
    }
    filenames = read_filename_list(paths["certifying_formal_filenames"])
    if len(filenames) != EXPECTED_IMAGE_COUNT:
        raise ValueError(
            f"certifying formal contains {len(filenames)} filenames, expected {EXPECTED_IMAGE_COUNT}"
        )
    if filenames != sorted(filenames, key=lambda value: value.encode("utf-8")):
        raise ValueError("certifying formal filename list is not bytewise sorted")

    manifest_rows = read_jsonl(paths["image_manifest"])
    manifest_field_sets = Counter(
        ",".join(sorted(row)) for row in manifest_rows
    )
    if len(manifest_rows) != 1542:
        raise ValueError(f"image manifest has {len(manifest_rows)} rows, expected 1542")
    manifest_by_name: dict[str, dict[str, Any]] = {}
    for row in manifest_rows:
        filename = row.get("filename")
        if not isinstance(filename, str) or filename in manifest_by_name:
            raise ValueError(f"invalid or duplicate image manifest filename: {filename!r}")
        manifest_by_name[filename] = row

    canonical_rows = read_jsonl(paths["canonical_jsonl"])
    audit_rows = read_jsonl(paths["contrast_hull_audit_jsonl"])
    if len(canonical_rows) != 4757 or len(audit_rows) != 4757:
        raise ValueError("canonical or contrast-hull row count differs from 4757")
    canonical_by_key: dict[str, dict[str, Any]] = {}
    canonical_by_filename: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in canonical_rows:
        row_key = str(row.get("row_key"))
        if row_key in canonical_by_key:
            raise ValueError(f"duplicate canonical row_key {row_key}")
        canonical_by_key[row_key] = row
        canonical_by_filename[str(row.get("filename"))].append(row)
    audit_by_filename: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in audit_rows:
        row_key = str(row.get("sample_id"))
        canonical = canonical_by_key.get(row_key)
        if canonical is None:
            raise ValueError(f"contrast hull row lacks canonical counterpart: {row_key}")
        if (
            row.get("filename") != canonical.get("filename")
            or row.get("negative_type") != canonical.get("category")
            or row.get("numeric_id") != canonical.get("numeric_id")
        ):
            raise ValueError(f"contrast hull/canonical identity mismatch for {row_key}")
        audit_by_filename[str(row["filename"])].append(row)

    contrast_summary = json.loads(
        paths["contrast_hull_summary_json"].read_text(encoding="utf-8")
    )
    certifying_summary = contrast_summary.get("scope_statistics", {}).get(
        "certifying_formal", {}
    )
    if (
        certifying_summary.get("record_count") != 4125
        or certifying_summary.get("unique_image_count") != EXPECTED_IMAGE_COUNT
    ):
        raise ValueError("contrast hull summary certifying-formal binding mismatch")

    image_rows: list[dict[str, Any]] = []
    captions_by_filename: dict[str, tuple[CaptionDiagnostic, ...]] = {}
    valid_audit_by_filename: dict[str, list[dict[str, Any]]] = {}
    coco_root = paths["coco_root"]
    for filename in filenames:
        if Path(filename).name != filename:
            raise ValueError(f"unsafe filename {filename!r}")
        manifest = manifest_by_name.get(filename)
        if manifest is None:
            raise ValueError(f"certifying filename missing from image manifest: {filename}")
        if manifest.get("status") != "ready" or manifest.get("exists") is not True:
            raise ValueError(f"image manifest row is not ready: {filename}")
        image_path = (coco_root / filename).resolve()
        if image_path.parent != coco_root or not image_path.is_file():
            raise FileNotFoundError(f"image path is missing or unsafe: {image_path}")
        fingerprint = image_fingerprint(image_path)
        if fingerprint["image_sha256"] != manifest.get("sha256"):
            raise ValueError(f"actual image SHA differs from frozen manifest: {filename}")
        if fingerprint["image_size_bytes"] != manifest.get("size_bytes"):
            raise ValueError(f"actual image size differs from frozen manifest: {filename}")
        try:
            filename_coco_id = int(Path(filename).stem)
            manifest_coco_id = int(manifest["coco_image_id"])
        except Exception as error:
            raise ValueError(f"invalid COCO numeric ID for {filename}") from error
        if filename_coco_id != manifest_coco_id:
            raise ValueError(f"filename/manifest COCO ID mismatch for {filename}")
        canonical_group = canonical_by_filename.get(filename, [])
        audit_group = audit_by_filename.get(filename, [])
        if not canonical_group or len(canonical_group) != len(audit_group):
            raise ValueError(f"canonical/audit group mismatch for {filename}")
        valid_group = [
            row
            for row in audit_group
            if row.get("can_score_from_common_prefix") is True
            and row.get("second_round_category") not in VALID_V6_EXCLUDED_CATEGORIES
        ]
        positive_texts = [
            str(text)
            for row in canonical_group
            for text in (row.get("caption"), row.get("caption2"))
            if isinstance(text, str) and text.strip()
        ]
        captions = build_caption_diagnostics(positive_texts)
        captions_by_filename[filename] = captions
        valid_audit_by_filename[filename] = sorted(
            valid_group,
            key=lambda row: (str(row["negative_type"]), int(row["numeric_id"])),
        )
        image_rows.append(
            {
                "filename": filename,
                "numeric_coco_id": manifest_coco_id,
                "manifest_sha256": manifest["sha256"],
                "manifest_perceptual_hash": manifest.get("perceptual_hash"),
                "record_count": len(canonical_group),
                "valid_v6_record_count": len(valid_group),
                "has_valid_v6_record": bool(valid_group),
                "positive_descriptions": [caption.raw for caption in captions],
                "normalized_positive_descriptions": [
                    caption.normalized for caption in captions
                ],
                **fingerprint,
            }
        )
    if len({row["image_path"] for row in image_rows}) != EXPECTED_IMAGE_COUNT:
        raise ValueError("certifying filenames do not resolve to unique image paths")
    return {
        "paths": {key: str(value) for key, value in paths.items()},
        "input_sha256": input_sha256,
        "manifest_field_sets": dict(sorted(manifest_field_sets.items())),
        "filenames": filenames,
        "images": image_rows,
        "captions_by_filename": captions_by_filename,
        "valid_audit_by_filename": valid_audit_by_filename,
        "canonical_record_count": sum(row["record_count"] for row in image_rows),
        "valid_v6_record_count": sum(
            row["valid_v6_record_count"] for row in image_rows
        ),
    }


def _duplicate_groups(
    images: Sequence[Mapping[str, Any]], key: str
) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for image in images:
        grouped[str(image[key])].append(str(image["filename"]))
    return [
        {key: value, "filenames": sorted(names), "count": len(names)}
        for value, names in sorted(grouped.items())
        if len(names) > 1
    ]


def build_allowed_graph(
    images: Sequence[Mapping[str, Any]],
) -> tuple[list[list[int]], dict[str, Any]]:
    allowed: list[list[int]] = [[] for _ in images]
    all_reason_counts: Counter[str] = Counter()
    cross_reason_counts: Counter[str] = Counter()
    hard_directed_count = 0
    hard_cross_directed_count = 0
    suspect_allowed_count = 0
    minimum_allowed_distance_pairs: list[tuple[int, int, str, str]] = []
    for target_index, target in enumerate(images):
        for donor_index, donor in enumerate(images):
            reasons = hard_exclusion_reasons(target, donor)
            if reasons:
                hard_directed_count += 1
                all_reason_counts.update(reasons)
                if target_index != donor_index:
                    hard_cross_directed_count += 1
                    cross_reason_counts.update(reasons)
                continue
            allowed[target_index].append(donor_index)
            difference_distance = hamming64(
                target["difference_hash"], donor["difference_hash"]
            )
            average_distance = hamming64(
                target["average_hash"], donor["average_hash"]
            )
            if difference_distance <= 4 or average_distance <= 4:
                suspect_allowed_count += 1
                minimum_allowed_distance_pairs.append(
                    (
                    difference_distance + average_distance,
                    max(difference_distance, average_distance),
                    str(target["filename"]),
                    str(donor["filename"]),
                    )
                )
        allowed[target_index].sort()
    if any(len(donors) < len(images) - 10 for donors in allowed):
        raise RuntimeError("hard exclusions unexpectedly made the assignment graph sparse")
    closest = []
    for _, _, target_name, donor_name in sorted(minimum_allowed_distance_pairs)[:30]:
        target = next(image for image in images if image["filename"] == target_name)
        donor = next(image for image in images if image["filename"] == donor_name)
        closest.append(
            {
                "target_filename": target_name,
                "donor_filename": donor_name,
                "difference_hash_distance": hamming64(
                    target["difference_hash"], donor["difference_hash"]
                ),
                "average_hash_distance": hamming64(
                    target["average_hash"], donor["average_hash"]
                ),
            }
        )
    closest.sort(
        key=lambda row: (
            row["difference_hash_distance"] + row["average_hash_distance"],
            max(row["difference_hash_distance"], row["average_hash_distance"]),
            row["target_filename"],
            row["donor_filename"],
        )
    )
    total_possible = len(images) * len(images)
    statistics_output = {
        "pair_count_convention": "directed target-to-donor pairs",
        "total_possible_directed_pair_count": total_possible,
        "allowed_directed_pair_count": sum(len(row) for row in allowed),
        "hard_excluded_directed_pair_count": hard_directed_count,
        "hard_excluded_cross_image_directed_pair_count": hard_cross_directed_count,
        "hard_exclusion_reason_counts_including_self_pairs": dict(
            sorted(all_reason_counts.items())
        ),
        "hard_exclusion_reason_counts_cross_image_only": dict(
            sorted(cross_reason_counts.items())
        ),
        "allowed_degree_distribution": numeric_distribution(map(len, allowed)),
        "allowed_near_duplicate_suspect_directed_pair_count": suspect_allowed_count,
        "closest_allowed_suspect_pairs": closest,
        "duplicate_groups": {
            "coco_image_id": _duplicate_groups(images, "numeric_coco_id"),
            "file_sha256": _duplicate_groups(images, "image_sha256"),
            "normalized_pixel_sha256": _duplicate_groups(
                images, "normalized_pixel_sha256"
            ),
        },
    }
    if hard_directed_count + statistics_output["allowed_directed_pair_count"] != total_possible:
        raise RuntimeError("allowed and excluded graph counts do not reconstruct all pairs")
    return allowed, statistics_output


def assignment_core_payload(
    filenames: Sequence[str], rounds: Sequence[Sequence[int]]
) -> bytes:
    rows = [
        {
            "round_id": round_id,
            "target_filename": filename,
            "donor_filename": filenames[rounds[round_id - 1][target_index]],
        }
        for target_index, filename in enumerate(filenames)
        for round_id in range(1, len(rounds) + 1)
    ]
    return _jsonl_bytes(rows)


def build_manifest_rows(
    images: Sequence[Mapping[str, Any]],
    rounds: Sequence[Sequence[int]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target_index, target in enumerate(images):
        donor_rounds = []
        for round_id, matching in enumerate(rounds, 1):
            donor = images[matching[target_index]]
            difference_distance = hamming64(
                target["difference_hash"], donor["difference_hash"]
            )
            average_distance = hamming64(
                target["average_hash"], donor["average_hash"]
            )
            donor_rounds.append(
                {
                    "round_id": round_id,
                    "donor_filename": donor["filename"],
                    "donor_numeric_coco_id": donor["numeric_coco_id"],
                    "donor_image_path": donor["image_path"],
                    "donor_image_sha256": donor["image_sha256"],
                    "donor_normalized_pixel_sha256": donor[
                        "normalized_pixel_sha256"
                    ],
                    "donor_width": donor["width"],
                    "donor_height": donor["height"],
                    "donor_mode": donor["mode"],
                    "donor_image_size_bytes": donor["image_size_bytes"],
                    "donor_difference_hash": donor["difference_hash"],
                    "donor_average_hash": donor["average_hash"],
                    "difference_hash_distance": difference_distance,
                    "average_hash_distance": average_distance,
                    "near_duplicate_suspect": (
                        difference_distance <= 4 or average_distance <= 4
                    ),
                    "assignment_seed_material": assignment_seed_material(
                        round_id,
                        str(target["filename"]),
                        str(donor["filename"]),
                    ),
                }
            )
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "audit_version": AUDIT_VERSION,
                "target_filename": target["filename"],
                "target_numeric_coco_id": target["numeric_coco_id"],
                "target_image_path": target["image_path"],
                "target_image_sha256": target["image_sha256"],
                "target_normalized_pixel_sha256": target[
                    "normalized_pixel_sha256"
                ],
                "target_width": target["width"],
                "target_height": target["height"],
                "target_mode": target["mode"],
                "target_image_size_bytes": target["image_size_bytes"],
                "target_difference_hash": target["difference_hash"],
                "target_average_hash": target["average_hash"],
                "target_record_count": target["record_count"],
                "target_valid_v6_record_count": target["valid_v6_record_count"],
                "has_valid_v6_record": target["has_valid_v6_record"],
                "donor_rounds": donor_rounds,
            }
        )
    return rows


def build_text_and_hull_diagnostics(
    images: Sequence[Mapping[str, Any]],
    rounds: Sequence[Sequence[int]],
    allowed_donors: Sequence[Sequence[int]],
    captions_by_filename: Mapping[str, Sequence[CaptionDiagnostic]],
    valid_audit_by_filename: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    filenames = [str(image["filename"]) for image in images]
    assigned_pairs = [
        (target_index, int(matching[target_index]))
        for target_index in range(len(images))
        for matching in rounds
    ]
    baseline_pairs = sample_allowed_pairs(allowed_donors)
    requested_pairs = sorted(set(assigned_pairs) | set(baseline_pairs))
    matrix, caption_indices, tfidf_metadata = build_tfidf_matrix(
        filenames, captions_by_filename
    )
    tfidf_scores = maximum_tfidf_for_pairs(
        requested_pairs, filenames, matrix, caption_indices
    )
    lexical_cache: dict[tuple[int, int], dict[str, Any]] = {}

    def lexical(target_index: int, donor_index: int) -> dict[str, Any]:
        key = (target_index, donor_index)
        if key not in lexical_cache:
            lexical_cache[key] = lexical_pair_metrics(
                captions_by_filename[filenames[target_index]],
                captions_by_filename[filenames[donor_index]],
            )
        return lexical_cache[key]

    donor_lexemes = {
        filename: {
            token
            for caption in captions_by_filename[filename]
            for token in diagnostic_tokens(caption.raw)
        }
        for filename in filenames
    }
    pair_rows: list[dict[str, Any]] = []
    target_statistics: list[dict[str, Any]] = []
    for target_index, target in enumerate(images):
        target_pair_rows = []
        for round_id, matching in enumerate(rounds, 1):
            donor_index = int(matching[target_index])
            donor = images[donor_index]
            metrics = lexical(target_index, donor_index)
            record_mentions = []
            for audit_row in valid_audit_by_filename[str(target["filename"])]:
                mention = hull_mention_classification(
                    donor_lexemes[str(donor["filename"])],
                    audit_row.get("positive_contrast_hull_lexemes", []),
                    audit_row.get("negative_contrast_hull_lexemes", []),
                )
                record_mentions.append(
                    {
                        "sample_id": audit_row["sample_id"],
                        "negative_type": audit_row["negative_type"],
                        "positive_contrast_hull_lexemes": audit_row.get(
                            "positive_contrast_hull_lexemes", []
                        ),
                        "negative_contrast_hull_lexemes": audit_row.get(
                            "negative_contrast_hull_lexemes", []
                        ),
                        **mention,
                    }
                )
            difference_distance = hamming64(
                target["difference_hash"], donor["difference_hash"]
            )
            average_distance = hamming64(
                target["average_hash"], donor["average_hash"]
            )
            mention_counts = Counter(
                row["classification"] for row in record_mentions
            )
            pair_row = {
                "schema_version": SCHEMA_VERSION,
                "audit_version": AUDIT_VERSION,
                "target_filename": target["filename"],
                "target_numeric_coco_id": target["numeric_coco_id"],
                "donor_filename": donor["filename"],
                "donor_numeric_coco_id": donor["numeric_coco_id"],
                "round_id": round_id,
                "assignment_seed_material": assignment_seed_material(
                    round_id,
                    str(target["filename"]),
                    str(donor["filename"]),
                ),
                "target_record_count": target["record_count"],
                "target_valid_v6_record_count": target["valid_v6_record_count"],
                "difference_hash_distance": difference_distance,
                "average_hash_distance": average_distance,
                "near_duplicate_suspect": (
                    difference_distance <= 4 or average_distance <= 4
                ),
                "maximum_positive_caption_tfidf_cosine": tfidf_scores[
                    (target_index, donor_index)
                ],
                **metrics,
                "hull_mention_counts": dict(sorted(mention_counts.items())),
                "has_mentions_positive_hull": any(
                    row["classification"]
                    in {"mentions_positive_only", "mentions_both"}
                    for row in record_mentions
                ),
                "has_mentions_negative_only": any(
                    row["classification"] == "mentions_negative_only"
                    for row in record_mentions
                ),
                "hull_mentions": record_mentions,
            }
            pair_rows.append(pair_row)
            target_pair_rows.append(pair_row)
        similarities = [
            row["maximum_positive_caption_tfidf_cosine"] for row in target_pair_rows
        ]
        sorted_similarities = sorted(similarities, reverse=True)
        donor_dimensions = [
            [images[int(rounds[index][target_index])]["width"],
             images[int(rounds[index][target_index])]["height"]]
            for index in range(len(rounds))
        ]
        target_statistics.append(
            {
                "target_filename": target["filename"],
                "donor_filenames": [row["donor_filename"] for row in target_pair_rows],
                "all_donor_filenames_distinct": len(
                    {row["donor_filename"] for row in target_pair_rows}
                )
                == len(rounds),
                "donor_tfidf_mean": statistics.fmean(similarities),
                "donor_tfidf_minimum": min(similarities),
                "donor_tfidf_maximum": max(similarities),
                "donor_tfidf_spread": max(similarities) - min(similarities),
                "donor_tfidf_by_round": [
                    {
                        "round_id": row["round_id"],
                        "donor_filename": row["donor_filename"],
                        "maximum_positive_caption_tfidf_cosine": row[
                            "maximum_positive_caption_tfidf_cosine"
                        ],
                    }
                    for row in target_pair_rows
                ],
                "all_five_donor_tfidf_below_0_05": max(similarities) < 0.05,
                "has_one_donor_at_least_0_20_above_second_highest": (
                    sorted_similarities[0] - sorted_similarities[1] >= 0.20
                ),
                "has_near_duplicate_suspect_donor": any(
                    row["near_duplicate_suspect"] for row in target_pair_rows
                ),
                "donor_dimensions": donor_dimensions,
                "unique_donor_dimension_count": len(
                    {tuple(value) for value in donor_dimensions}
                ),
                "target_valid_v6_record_count": target["valid_v6_record_count"],
            }
        )

    baseline_rows = []
    for target_index, donor_index in baseline_pairs:
        baseline_rows.append(
            {
                "target_index": target_index,
                "donor_index": donor_index,
                "maximum_positive_caption_tfidf_cosine": tfidf_scores[
                    (target_index, donor_index)
                ],
                **lexical(target_index, donor_index),
            }
        )
    diagnostic_metadata = {
        "assignment_was_frozen_before_text_diagnostics": True,
        "text_metrics_used_by_matching": False,
        "tfidf": tfidf_metadata,
        "baseline_sampling": {
            "method": "random.Random(seed).sample over bytewise target and numeric donor adjacency order",
            "seed": RANDOM_SEED,
            "tag": BASELINE_TAG,
            "sample_size": len(baseline_pairs),
            "allowed_pair_population_size": sum(len(row) for row in allowed_donors),
        },
        "jaccard_tokenization": (
            "Unicode NFKC, casefold, deterministic word/hyphen/apostrophe regex"
        ),
        "high_content_word_overlap_rule": (
            "maximum exact content-word intersection divided by smaller caption "
            "content-word set is at least 0.5; sklearn English stop words removed"
        ),
        "hull_mention_rule": (
            "case-insensitive exact full-lexeme set intersection; punctuation-only "
            "lexemes excluded; no stemming or semantic expansion"
        ),
    }
    return pair_rows, diagnostic_metadata, baseline_rows, target_statistics


def _classification_counts(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(row["classification"]) for row in rows)
    total = sum(counts.values())
    names = (
        "mentions_positive_only",
        "mentions_negative_only",
        "mentions_both",
        "mentions_neither",
    )
    return {
        name: {
            "count": counts[name],
            "proportion": counts[name] / total if total else 0.0,
        }
        for name in names
    } | {"total_record_pair_observations": total}


def _pair_similarity_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "pair_count": len(rows),
        "tfidf_cosine": tfidf_distribution(
            row["maximum_positive_caption_tfidf_cosine"] for row in rows
        ),
        "unigram_jaccard": numeric_distribution(
            row["maximum_unigram_jaccard"] for row in rows
        ),
        "unigram_bigram_jaccard": numeric_distribution(
            row["maximum_unigram_bigram_jaccard"] for row in rows
        ),
        "exact_normalized_positive_caption_pair_count": sum(
            bool(row["has_exact_normalized_positive_caption"]) for row in rows
        ),
        "high_content_word_overlap_pair_count": sum(
            bool(row["has_high_content_word_overlap"]) for row in rows
        ),
    }


def summarize_hull_mentions(
    pair_rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    all_mentions = [
        mention for pair in pair_rows for mention in pair.get("hull_mentions", [])
    ]
    per_negative_type: dict[str, Any] = {}
    negative_types = sorted({row["negative_type"] for row in all_mentions})
    for negative_type in negative_types:
        selected = [
            row for row in all_mentions if row["negative_type"] == negative_type
        ]
        per_negative_type[negative_type] = _classification_counts(selected)
    replace_mentions = [
        row for row in all_mentions if str(row["negative_type"]).startswith("replace_")
    ]
    swap_mentions = [
        row for row in all_mentions if str(row["negative_type"]).startswith("swap_")
    ]
    per_round: dict[str, Any] = {}
    for round_id in range(1, ROUND_COUNT + 1):
        selected_pairs = [row for row in pair_rows if row["round_id"] == round_id]
        selected_mentions = [
            mention
            for pair in selected_pairs
            for mention in pair.get("hull_mentions", [])
        ]
        per_round[str(round_id)] = {
            "pair_similarity": _pair_similarity_summary(selected_pairs),
            "hull_mentions": _classification_counts(selected_mentions),
            "near_duplicate_suspect_pair_count": sum(
                row["near_duplicate_suspect"] for row in selected_pairs
            ),
        }
    image_classifications: dict[str, set[str]] = defaultdict(set)
    for pair in pair_rows:
        for mention in pair.get("hull_mentions", []):
            image_classifications[str(pair["target_filename"])].add(
                str(mention["classification"])
            )
    image_group_counts = {
        name: sum(name in values for values in image_classifications.values())
        for name in (
            "mentions_positive_only",
            "mentions_negative_only",
            "mentions_both",
            "mentions_neither",
        )
    }
    overall = {
        "all_valid_records": _classification_counts(all_mentions),
        "replace_records": _classification_counts(replace_mentions),
        "swap_records": _classification_counts(swap_mentions),
        "target_image_group_counts_with_at_least_one_classification": image_group_counts,
        "target_error_hull_only_record_pair_count": sum(
            row["classification"] == "mentions_negative_only" for row in all_mentions
        ),
        "assigned_pair_count_with_at_least_one_error_hull_only_record": sum(
            pair["has_mentions_negative_only"] for pair in pair_rows
        ),
    }
    return overall, per_negative_type, per_round


def summarize_target_five_donors(
    target_statistics: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    aggregate = {
        "target_count": len(target_statistics),
        "all_targets_have_five_distinct_donors": all(
            row["all_donor_filenames_distinct"] for row in target_statistics
        ),
        "donor_tfidf_mean_distribution": numeric_distribution(
            row["donor_tfidf_mean"] for row in target_statistics
        ),
        "donor_tfidf_minimum_distribution": numeric_distribution(
            row["donor_tfidf_minimum"] for row in target_statistics
        ),
        "donor_tfidf_maximum_distribution": numeric_distribution(
            row["donor_tfidf_maximum"] for row in target_statistics
        ),
        "donor_tfidf_spread_distribution": numeric_distribution(
            row["donor_tfidf_spread"] for row in target_statistics
        ),
        "all_five_donor_tfidf_below_0_05_target_count": sum(
            row["all_five_donor_tfidf_below_0_05"] for row in target_statistics
        ),
        "one_donor_at_least_0_20_above_second_highest_target_count": sum(
            row["has_one_donor_at_least_0_20_above_second_highest"]
            for row in target_statistics
        ),
        "near_duplicate_suspect_donor_target_count": sum(
            row["has_near_duplicate_suspect_donor"] for row in target_statistics
        ),
        "unique_donor_dimension_count_distribution": numeric_distribution(
            row["unique_donor_dimension_count"] for row in target_statistics
        ),
        "diagnostic_thresholds_are_not_acceptance_rules": True,
    }
    return {
        "aggregate": aggregate,
        "targets": list(target_statistics),
    }


def _stable_sample(
    values: Sequence[Any], limit: int, label: str, identity: Any
) -> list[Any]:
    return sorted(
        values,
        key=lambda value: (
            hashlib.sha256(
                f"{RANDOM_SEED}|{label}|{identity(value)}".encode("utf-8")
            ).digest(),
            str(identity(value)).encode("utf-8"),
        ),
    )[:limit]


def build_manual_review(
    images: Sequence[Mapping[str, Any]],
    pair_rows: Sequence[Mapping[str, Any]],
    target_statistics: Sequence[Mapping[str, Any]],
    captions_by_filename: Mapping[str, Sequence[CaptionDiagnostic]],
    valid_audit_by_filename: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[str, set[str]]:
    image_by_name = {str(image["filename"]): image for image in images}
    pairs_by_target: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        pairs_by_target[str(row["target_filename"])].append(row)
    for rows in pairs_by_target.values():
        rows.sort(key=lambda row: int(row["round_id"]))
    target_stats_by_name = {
        str(row["target_filename"]): row for row in target_statistics
    }

    def pair_identity(row: Mapping[str, Any]) -> str:
        return (
            f"{row['target_filename']}|{row['round_id']}|{row['donor_filename']}"
        )

    random_targets = _stable_sample(
        list(image_by_name), REVIEW_LIMIT, "random_targets", lambda value: value
    )
    highest = sorted(
        pair_rows,
        key=lambda row: (
            -float(row["maximum_positive_caption_tfidf_cosine"]),
            pair_identity(row),
        ),
    )[:REVIEW_LIMIT]
    lowest = sorted(
        pair_rows,
        key=lambda row: (
            float(row["maximum_positive_caption_tfidf_cosine"]),
            pair_identity(row),
        ),
    )[:REVIEW_LIMIT]
    suspects = sorted(
        [row for row in pair_rows if row["near_duplicate_suspect"]],
        key=lambda row: (
            int(row["difference_hash_distance"])
            + int(row["average_hash_distance"]),
            max(
                int(row["difference_hash_distance"]),
                int(row["average_hash_distance"]),
            ),
            pair_identity(row),
        ),
    )[:REVIEW_LIMIT]
    positive_mentions = _stable_sample(
        [row for row in pair_rows if row["has_mentions_positive_hull"]],
        REVIEW_LIMIT,
        "positive_mentions",
        pair_identity,
    )
    negative_only = _stable_sample(
        [row for row in pair_rows if row["has_mentions_negative_only"]],
        REVIEW_LIMIT,
        "negative_only",
        pair_identity,
    )
    swap_targets = _stable_sample(
        [
            name
            for name, rows in valid_audit_by_filename.items()
            if any(str(row["negative_type"]).startswith("swap_") for row in rows)
        ],
        REVIEW_LIMIT,
        "swap_targets",
        lambda value: value,
    )
    replace_targets = _stable_sample(
        [
            name
            for name, rows in valid_audit_by_filename.items()
            if any(str(row["negative_type"]).startswith("replace_") for row in rows)
        ],
        REVIEW_LIMIT,
        "replace_targets",
        lambda value: value,
    )
    spread_targets = [
        str(row["target_filename"])
        for row in sorted(
            target_statistics,
            key=lambda row: (
                -float(row["donor_tfidf_spread"]),
                str(row["target_filename"]),
            ),
        )[:REVIEW_LIMIT]
    ]
    no_valid_targets = [
        str(image["filename"])
        for image in images
        if not image["has_valid_v6_record"]
    ]

    groups: list[tuple[str, list[tuple[str, int | None]]]] = [
        (
            "固定种子随机目标图片组",
            [(name, None) for name in random_targets],
        ),
        (
            "TF-IDF 相似度最高的已分配配对",
            [(str(row["target_filename"]), int(row["round_id"])) for row in highest],
        ),
        (
            "TF-IDF 相似度最低的已分配配对",
            [(str(row["target_filename"]), int(row["round_id"])) for row in lowest],
        ),
        (
            "疑似视觉近重复的已分配配对",
            [(str(row["target_filename"]), int(row["round_id"])) for row in suspects],
        ),
        (
            "Donor 正描述提及目标正确 hull 的配对",
            [
                (str(row["target_filename"]), int(row["round_id"]))
                for row in positive_mentions
            ],
        ),
        (
            "Donor 提及目标错误 hull 但不提及正确 hull 的配对",
            [
                (str(row["target_filename"]), int(row["round_id"]))
                for row in negative_only
            ],
        ),
        ("含 swap 类有效记录的目标", [(name, None) for name in swap_targets]),
        (
            "含 replace 类有效记录的目标",
            [(name, None) for name in replace_targets],
        ),
        (
            "五张 donor TF-IDF 差异最大的目标",
            [(name, None) for name in spread_targets],
        ),
        (
            "没有有效 v6 文本记录但仍生成清单的目标",
            [(name, None) for name in no_valid_targets],
        ),
    ]
    lines = [
        "# 阶段三 v6 K=5 错配图片清单人工抽查材料",
        "",
        "本材料仅用于人工检查错配清单，不代表图片语义已经由人工验证。",
        "",
        f"固定随机种子：`{RANDOM_SEED}`；每类最多 `{REVIEW_LIMIT}` 个案例。",
        "所有文本相似度与 hull 提及指标均在错配清单冻结后计算，未参与 donor 分配。",
        "",
    ]
    assets: set[str] = set()
    case_number = 0
    for title, cases in groups:
        lines.extend(
            [
                f"## {title}",
                "",
                f"本节 `{len(cases)}` 个案例。",
                "",
            ]
        )
        if not cases:
            lines.extend(["本类别没有已分配案例。", ""])
            continue
        for target_name, focus_round in cases:
            case_number += 1
            target = image_by_name[target_name]
            target_pairs = pairs_by_target[target_name]
            assets.add(target_name)
            for pair in target_pairs:
                assets.add(str(pair["donor_filename"]))
            focus = (
                f"；重点 round `{focus_round}`" if focus_round is not None else ""
            )
            lines.extend(
                [
                    f"### {case_number}. `{target_name}`{focus}",
                    "",
                    f"![target](review_assets/{target_name})",
                    "",
                    (
                        f"目标记录数 `{target['record_count']}`；有效 v6 记录数 "
                        f"`{target['valid_v6_record_count']}`；尺寸 "
                        f"`{target['width']}×{target['height']}`。"
                    ),
                    "",
                    "目标全部正描述：",
                    "",
                ]
            )
            for caption in captions_by_filename[target_name]:
                lines.append(f"- {json.dumps(caption.raw, ensure_ascii=False)}")
            lines.extend(["", "目标有效 contrast hull：", ""])
            audit_rows = valid_audit_by_filename[target_name]
            if not audit_rows:
                lines.append("- 无有效 v6 记录。")
            for row in audit_rows:
                lines.append(
                    "- `{}` `{}`：正 `{}`；负 `{}`".format(
                        row["sample_id"],
                        row["negative_type"],
                        json.dumps(
                            row.get("positive_contrast_hull_lexemes", []),
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            row.get("negative_contrast_hull_lexemes", []),
                            ensure_ascii=False,
                        ),
                    )
                )
            lines.extend(
                [
                    "",
                    "| round | donor 缩略图 | donor | TF-IDF | unigram Jaccard | uni/bi Jaccard | dHash/aHash | near suspect |",
                    "|---:|---|---|---:|---:|---:|---|---|",
                ]
            )
            for pair in target_pairs:
                donor_name = str(pair["donor_filename"])
                marker = " **重点**" if pair["round_id"] == focus_round else ""
                lines.append(
                    "| {}{} | ![donor](review_assets/{}) | `{}` | {:.6f} | {:.6f} | {:.6f} | {}/{} | `{}` |".format(
                        pair["round_id"],
                        marker,
                        donor_name,
                        donor_name,
                        pair["maximum_positive_caption_tfidf_cosine"],
                        pair["maximum_unigram_jaccard"],
                        pair["maximum_unigram_bigram_jaccard"],
                        pair["difference_hash_distance"],
                        pair["average_hash_distance"],
                        pair["near_duplicate_suspect"],
                    )
                )
            lines.append("")
            for pair in target_pairs:
                donor_name = str(pair["donor_filename"])
                lines.extend(
                    [
                        f"#### Round {pair['round_id']} donor `{donor_name}`",
                        "",
                        "Donor 全部正描述：",
                        "",
                    ]
                )
                for caption in captions_by_filename[donor_name]:
                    lines.append(f"- {json.dumps(caption.raw, ensure_ascii=False)}")
                lines.extend(["", "Hull 字面提及分类：", ""])
                if not pair["hull_mentions"]:
                    lines.append("- 目标没有有效 v6 记录。")
                for mention in pair["hull_mentions"]:
                    lines.append(
                        "- `{}` `{}`；matched positive `{}`；matched negative `{}`".format(
                            mention["sample_id"],
                            mention["classification"],
                            json.dumps(
                                mention["matched_positive_hull_lexemes"],
                                ensure_ascii=False,
                            ),
                            json.dumps(
                                mention["matched_negative_hull_lexemes"],
                                ensure_ascii=False,
                            ),
                        )
                    )
                lines.append("")
            target_stat = target_stats_by_name[target_name]
            lines.extend(
                [
                    (
                        "五 donor TF-IDF：mean `{:.6f}`，min `{:.6f}`，max "
                        "`{:.6f}`，spread `{:.6f}`；近重复疑似 `{}`。"
                    ).format(
                        target_stat["donor_tfidf_mean"],
                        target_stat["donor_tfidf_minimum"],
                        target_stat["donor_tfidf_maximum"],
                        target_stat["donor_tfidf_spread"],
                        target_stat["has_near_duplicate_suspect_donor"],
                    ),
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n", assets


def write_review_assets(
    output_dir: Path,
    asset_filenames: Iterable[str],
    image_by_name: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=".review_assets.", dir=output_dir)
    )
    try:
        for filename in sorted(set(asset_filenames), key=lambda value: value.encode("utf-8")):
            generate_thumbnail(
                Path(str(image_by_name[filename]["image_path"])),
                temporary / filename,
            )
        destination = output_dir / "review_assets"
        if destination.exists():
            if not destination.is_dir() or destination.parent != output_dir:
                raise RuntimeError(f"unsafe review assets destination: {destination}")
            shutil.rmtree(destination)
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    entries = []
    for path in sorted(
        (output_dir / "review_assets").iterdir(),
        key=lambda value: value.name.encode("utf-8"),
    ):
        entries.append(
            {"filename": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
        )
    tree_payload = _jsonl_bytes(entries)
    return {
        "asset_count": len(entries),
        "tree_sha256": sha256_bytes(tree_payload),
        "entries": entries,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certifying-formal-filenames", type=Path, required=True)
    parser.add_argument("--image-manifest", type=Path, required=True)
    parser.add_argument("--canonical-jsonl", type=Path, required=True)
    parser.add_argument("--contrast-hull-audit", type=Path, required=True)
    parser.add_argument("--contrast-hull-summary", type=Path, required=True)
    parser.add_argument("--coco-root", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument("--expected-certifying-sha256")
    parser.add_argument("--expected-image-manifest-sha256")
    parser.add_argument("--expected-canonical-sha256")
    parser.add_argument("--expected-contrast-audit-sha256")
    parser.add_argument("--expected-contrast-summary-sha256")
    return parser


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    bound = bind_and_fingerprint_inputs(args)
    images = bound["images"]
    filenames = bound["filenames"]
    allowed_donors, graph_statistics = build_allowed_graph(images)

    rounds = build_k_matchings(images, allowed_donors)
    per_round_validation = validate_matchings(images, rounds)
    repeated_rounds = build_k_matchings(images, allowed_donors)
    matching_recomputed_identically = rounds == repeated_rounds
    if not matching_recomputed_identically:
        raise RuntimeError("in-process deterministic matching recomputation differs")
    core_payload = assignment_core_payload(filenames, rounds)
    assignment_sha256 = sha256_bytes(core_payload)

    manifest_rows = build_manifest_rows(images, rounds)
    if len(manifest_rows) != EXPECTED_IMAGE_COUNT:
        raise RuntimeError("mismatch manifest target count mismatch")
    manifest_payload = _jsonl_bytes(manifest_rows)
    manifest_path = output_dir / "mismatch_manifest_k5.jsonl"
    _atomic_write(manifest_path, manifest_payload)
    frozen_manifest_sha256 = sha256_file(manifest_path)

    (
        pair_rows,
        diagnostic_metadata,
        baseline_rows,
        target_statistics,
    ) = build_text_and_hull_diagnostics(
        images,
        rounds,
        allowed_donors,
        bound["captions_by_filename"],
        bound["valid_audit_by_filename"],
    )
    if len(pair_rows) != EXPECTED_PAIR_COUNT:
        raise RuntimeError(
            f"pair diagnostic count {len(pair_rows)} differs from {EXPECTED_PAIR_COUNT}"
        )
    pair_path = output_dir / "mismatch_pair_diagnostics.jsonl"
    pair_payload = _jsonl_bytes(pair_rows)
    _atomic_write(pair_path, pair_payload)

    manual_text, asset_filenames = build_manual_review(
        images,
        pair_rows,
        target_statistics,
        bound["captions_by_filename"],
        bound["valid_audit_by_filename"],
    )
    manual_path = output_dir / "manual_review_pairs.md"
    _atomic_write(manual_path, manual_text.encode("utf-8"))
    image_by_name = {str(image["filename"]): image for image in images}
    review_assets = write_review_assets(
        output_dir, asset_filenames, image_by_name
    )

    hull_mentions, per_negative_type, per_round_statistics = summarize_hull_mentions(
        pair_rows
    )
    valid_types = Counter(
        row["negative_type"]
        for rows in bound["valid_audit_by_filename"].values()
        for row in rows
    )
    valid_type_images = {
        negative_type: len(
            {
                filename
                for filename, rows in bound["valid_audit_by_filename"].items()
                if any(row["negative_type"] == negative_type for row in rows)
            }
        )
        for negative_type in sorted(valid_types)
    }
    for negative_type in sorted(valid_types):
        per_negative_type.setdefault(negative_type, {})
        per_negative_type[negative_type]["valid_v6_record_count"] = valid_types[
            negative_type
        ]
        per_negative_type[negative_type]["target_image_count"] = valid_type_images[
            negative_type
        ]

    assigned_similarity = _pair_similarity_summary(pair_rows)
    baseline_similarity = _pair_similarity_summary(baseline_rows)
    similarity_comparison = {
        "assigned_minus_baseline_mean_tfidf": (
            assigned_similarity["tfidf_cosine"]["mean"]
            - baseline_similarity["tfidf_cosine"]["mean"]
        ),
        "assigned_minus_baseline_median_tfidf": (
            assigned_similarity["tfidf_cosine"]["median"]
            - baseline_similarity["tfidf_cosine"]["median"]
        ),
        "acceptance_threshold_selected": False,
    }
    effective_targets = {
        str(image["filename"]) for image in images if image["has_valid_v6_record"]
    }
    no_valid_targets = sorted(set(filenames) - effective_targets)
    projected = projected_inference_counts(
        int(bound["valid_v6_record_count"]),
        effective_targets,
        filenames,
        rounds,
    )
    assigned_suspects = [row for row in pair_rows if row["near_duplicate_suspect"]]
    duplicate_groups = graph_statistics["duplicate_groups"]
    duplicate_statistics = {
        "file_sha256_duplicate_group_count": len(duplicate_groups["file_sha256"]),
        "normalized_pixel_sha256_duplicate_group_count": len(
            duplicate_groups["normalized_pixel_sha256"]
        ),
        "coco_image_id_duplicate_group_count": len(
            duplicate_groups["coco_image_id"]
        ),
        "groups": duplicate_groups,
        "all_images_decoded_successfully": True,
        "all_actual_file_sha256_match_frozen_manifest": True,
    }
    near_statistics = {
        "rule": "allowed pair is suspect when dHash distance <=4 or aHash distance <=4; suspect status does not exclude",
        "allowed_near_duplicate_suspect_directed_pair_count": graph_statistics[
            "allowed_near_duplicate_suspect_directed_pair_count"
        ],
        "assigned_pair_count": len(assigned_suspects),
        "assigned_difference_hash_distance": numeric_distribution(
            row["difference_hash_distance"] for row in pair_rows
        ),
        "assigned_average_hash_distance": numeric_distribution(
            row["average_hash_distance"] for row in pair_rows
        ),
        "closest_allowed_suspect_pairs": graph_statistics[
            "closest_allowed_suspect_pairs"
        ],
    }
    target_group_statistics = {
        "target_image_group_count": len(images),
        "unique_resolved_image_path_count": len(
            {str(image["image_path"]) for image in images}
        ),
        "all_target_and_donor_images_readable": True,
        "effective_v6_image_group_count": len(effective_targets),
        "no_valid_v6_record_image_group_count": len(no_valid_targets),
        "no_valid_v6_record_filenames": no_valid_targets,
        "canonical_record_count": bound["canonical_record_count"],
        "valid_v6_record_count": bound["valid_v6_record_count"],
        "canonical_record_count_per_image": numeric_distribution(
            image["record_count"] for image in images
        ),
        "valid_v6_record_count_per_image": numeric_distribution(
            image["valid_v6_record_count"] for image in images
        ),
        "valid_v6_record_count_per_image_histogram": dict(
            sorted(
                Counter(
                    str(image["valid_v6_record_count"]) for image in images
                ).items(),
                key=lambda item: int(item[0]),
            )
        ),
        "all_text_records_under_one_filename_share_the_same_five_donors": True,
    }
    k_definitions = {
        "K=1": [1],
        "K=3": [1, 2, 3],
        "K=5": [1, 2, 3, 4, 5],
        "formal_manifest_k": 5,
        "alternative_k_selected_as_better": False,
    }
    readme_path = output_dir / "README.md"
    if not readme_path.is_file():
        raise FileNotFoundError(
            f"README.md must exist beside the audit script before execution: {readme_path}"
        )
    output_hashes = {
        "mismatch_manifest_k5.jsonl": sha256_file(manifest_path),
        "mismatch_pair_diagnostics.jsonl": sha256_file(pair_path),
        "manual_review_pairs.md": sha256_file(manual_path),
        "README.md": sha256_file(readme_path),
        "review_assets_tree": review_assets["tree_sha256"],
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "audit_version": AUDIT_VERSION,
        "random_seed": RANDOM_SEED,
        "model_inference_run": False,
        "model_outputs_consulted": False,
        "text_similarity_used_for_assignment": False,
        "formal_experiment_code_modified": False,
        "formal_filter_or_difficulty_threshold_selected": False,
        "software_versions": {
            "python": sys.version.split()[0],
            "pillow": importlib.metadata.version("Pillow"),
            "numpy": importlib.metadata.version("numpy"),
            "scikit_learn": importlib.metadata.version("scikit-learn"),
        },
        "input_paths_and_sha256": {
            key: {
                "path": bound["paths"][key],
                "sha256": bound["input_sha256"].get(key),
            }
            for key in (
                "certifying_formal_filenames",
                "image_manifest",
                "canonical_jsonl",
                "contrast_hull_audit_jsonl",
                "contrast_hull_summary_json",
            )
        }
        | {
            "coco_root": {
                "path": bound["paths"]["coco_root"],
                "path_structure": "<coco_root>/<12-digit COCO filename>.jpg",
                "sha256": None,
            }
        },
        "observed_image_manifest_field_sets": bound["manifest_field_sets"],
        "target_image_count": len(images),
        "effective_v6_image_count": len(effective_targets),
        "total_pair_count": len(pair_rows),
        "round_count": len(rounds),
        "per_round_validation": per_round_validation,
        "duplicate_image_statistics": duplicate_statistics,
        "hard_excluded_pair_statistics": {
            key: value
            for key, value in graph_statistics.items()
            if key not in {"duplicate_groups", "closest_allowed_suspect_pairs"}
        },
        "near_duplicate_suspect_statistics": near_statistics,
        "text_diagnostic_protocol": diagnostic_metadata,
        "text_similarity_distribution": assigned_similarity,
        "allowed_pair_baseline_distribution": baseline_similarity,
        "assigned_vs_allowed_baseline_comparison": similarity_comparison,
        "hull_mention_statistics": hull_mentions,
        "per_negative_type_statistics": per_negative_type,
        "per_round_statistics": per_round_statistics,
        "per_target_five_donor_statistics": summarize_target_five_donors(
            target_statistics
        ),
        "image_group_statistics": target_group_statistics,
        "k_nested_definitions": k_definitions,
        "projected_inference_counts": projected,
        "manual_review": {
            "random_seed": RANDOM_SEED,
            "review_limit_per_category": REVIEW_LIMIT,
            "thumbnail_asset_count": review_assets["asset_count"],
            "review_assets_tree_sha256": review_assets["tree_sha256"],
            "human_semantic_validation_completed": False,
        },
        "determinism_checks": {
            "matching_recomputed_in_process_identically": matching_recomputed_identically,
            "assignment_core_sha256": assignment_sha256,
            "frozen_manifest_sha256_before_text_diagnostics": frozen_manifest_sha256,
            "all_adjacency_and_output_orders_explicitly_sorted": True,
            "python_set_or_dict_iteration_used_as_assignment_order": False,
            "full_run_external_sha256_check_required": True,
            "output_payload_sha256": output_hashes,
        },
    }
    summary_path = output_dir / "mismatch_summary.json"
    _atomic_write(summary_path, _json_bytes(summary, indent=2))
    return summary


def main() -> int:
    args = build_parser().parse_args()
    summary = run_audit(args)
    print(
        json.dumps(
            {
                "audit_version": summary["audit_version"],
                "output_dir": str(args.output_dir.resolve()),
                "target_image_count": summary["target_image_count"],
                "total_pair_count": summary["total_pair_count"],
                "effective_v6_image_count": summary["effective_v6_image_count"],
                "assignment_core_sha256": summary["determinism_checks"][
                    "assignment_core_sha256"
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
