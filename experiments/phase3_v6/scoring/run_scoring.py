#!/usr/bin/env python3
"""Command-line orchestration for the frozen Phase 3 v6 scoring run."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import shlex
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import torch
from transformers import AutoTokenizer

from experiments.phase3.stage2_adapter_loader import load_verified_model
from experiments.phase3_v6.scoring.aggregations import summarize_model
from experiments.phase3_v6.scoring.candidate_builder import (
    CandidatePair,
    prevalidate_candidates,
)
from experiments.phase3_v6.scoring.common import (
    GLOBAL_SEED,
    REPO_ROOT,
    SCORING_ROOT,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_jsonl,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    environment_receipt,
    git_output,
    read_json,
    read_jsonl,
    seed_everything,
    sha256_bytes,
    sha256_file,
    source_hashes,
    source_tree_sha256,
    utf8_key,
)
from experiments.phase3_v6.scoring.hull_scorer import (
    group_pairs_by_filename,
    score_candidate_batch,
    score_filename_group,
)
from experiments.phase3_v6.scoring.image_feature_cache import (
    ProjectedFeatureCache,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_MODEL_IDS,
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
    load_and_validate_frozen_inputs,
    verify_stage2_artifacts,
)
from experiments.phase3_v6.scoring.protocol import (
    PROTOCOL_PATH,
    RUN_MANIFEST_PATH,
    freeze_protocol,
    verify_protocol,
)
from experiments.phase3_v6.scoring.stage2_comparison import (
    build_stage2_stage3_comparison,
)


CANDIDATE_EVIDENCE_PATH = SCORING_ROOT / "candidate_preflight.jsonl"
CANDIDATE_SUMMARY_PATH = SCORING_ROOT / "candidate_preflight_summary.json"
SMOKE_ROOT = SCORING_ROOT / "smoke"
PROGRESS_ROOT = SCORING_ROOT / "progress"
RECORD_ROOT = SCORING_ROOT / "model_record_scores"
IMAGE_ROOT = SCORING_ROOT / "model_image_scores"
SUMMARY_ROOT = SCORING_ROOT / "model_summaries"
CACHE_RECEIPT_ROOT = SCORING_ROOT / "cache_receipts"
COMPARISON_PATH = SCORING_ROOT / "stage2_stage3_comparison.json"
FINAL_SUMMARY_PATH = SCORING_ROOT / "final_summary.md"
RUN_RECEIPT_PATH = SCORING_ROOT / "run_receipt.json"
RUN_RECEIPT_SHA_PATH = SCORING_ROOT / "run_receipt.sha256"
DEFAULT_ARTIFACT_ROOT = Path(
    "/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721"
)
DEFAULT_PYTHON = Path(
    "/home/lizhaohui/lzq/phase3_runtime/phase3_v5/env/bin/python"
)


def _load_tokenizer():
    from experiments.phase3.stage2_adapter_loader import (
        verify_stage2_source_integrity,
    )

    protocol = verify_stage2_source_integrity(
        str(REPO_ROOT / "experiments/stage2_protocol_v2.json")
    )
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )
    if tokenizer.pad_token_id is None or tokenizer.eos_token_id is None:
        raise ValueError("frozen tokenizer lacks PAD or EOS")
    return tokenizer, protocol


def _candidate_summary(pairs: Sequence[CandidatePair]) -> dict[str, Any]:
    positive_counts = [
        len(pair.templates["vlm"]["positive"].target_token_ids)
        for pair in pairs
    ]
    negative_counts = [
        len(pair.templates["vlm"]["negative"].target_token_ids)
        for pair in pairs
    ]
    boundary_difference = [
        pair.sample_id
        for pair in pairs
        if pair.evidence["positive_boundary_expansion_original"]
        != pair.evidence["negative_boundary_expansion_original"]
    ]
    return {
        "schema_version": 1,
        "status": "all_candidates_passed",
        "record_count": len(pairs),
        "image_count": len({pair.filename for pair in pairs}),
        "positive_formal_hull_token_count": {
            "minimum": min(positive_counts),
            "maximum": max(positive_counts),
            "multi_token_record_count": sum(value > 1 for value in positive_counts),
        },
        "negative_formal_hull_token_count": {
            "minimum": min(negative_counts),
            "maximum": max(negative_counts),
            "multi_token_record_count": sum(value > 1 for value in negative_counts),
        },
        "audit_vs_formal_original_text_token_count_difference": {
            "positive_record_count": sum(
                pair.positive_hull_token_count_audit
                != len(pair.templates["vlm"]["positive"].target_token_ids)
                for pair in pairs
            ),
            "negative_record_count": sum(
                pair.negative_hull_token_count_audit
                != len(pair.templates["vlm"]["negative"].target_token_ids)
                for pair in pairs
            ),
            "reason": (
                "formal scoring re-tokenizes original surface text and includes "
                "the original boundary separator in the scoring hull"
            ),
        },
        "different_positive_negative_boundary_separator_record_count": len(
            boundary_difference
        ),
        "different_boundary_separator_sample_ids": boundary_difference,
        "candidate_rule": (
            "shared selected-positive original prefix through final common "
            "lexeme; each scoring hull includes its own original boundary "
            "separator through the frozen semantic hull end"
        ),
        "subjective_naturalness_filter_used": False,
        "model_outputs_consulted": False,
    }


def prepare_candidates(*, write: bool = True) -> tuple[dict[str, Any], Any, list[CandidatePair]]:
    frozen = load_and_validate_frozen_inputs()
    tokenizer, _ = _load_tokenizer()
    pairs = prevalidate_candidates(tokenizer, frozen["valid_rows"])
    if len(pairs) != EXPECTED_VALID_RECORD_COUNT:
        raise ValueError("candidate preflight record count mismatch")
    summary = _candidate_summary(pairs)
    if summary["image_count"] != EXPECTED_VALID_IMAGE_COUNT:
        raise ValueError("candidate preflight image count mismatch")
    if write:
        atomic_write_jsonl(
            CANDIDATE_EVIDENCE_PATH,
            [pair.evidence for pair in pairs],
        )
        summary["evidence_sha256"] = sha256_file(CANDIDATE_EVIDENCE_PATH)
        atomic_write_json(CANDIDATE_SUMMARY_PATH, summary)
    return frozen, tokenizer, pairs


def _new_manifest(protocol_sha256: str, device: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "protocol_frozen",
        "protocol_sha256": protocol_sha256,
        "device": device,
        "global_seed": GLOBAL_SEED,
        "created_unix_time": time.time(),
        "command_history": [],
        "models": {
            model_id: {"status": "pending"} for model_id in EXPECTED_MODEL_IDS
        },
    }


def _record_command(manifest: dict[str, Any]) -> None:
    manifest.setdefault("command_history", []).append(
        {
            "argv": [str(value) for value in sys.argv],
            "shell_quoted": " ".join(shlex.quote(value) for value in sys.argv),
            "unix_time": time.time(),
        }
    )


def _write_manifest(manifest: Mapping[str, Any]) -> None:
    atomic_write_json(RUN_MANIFEST_PATH, dict(manifest))


def validate_command(args: argparse.Namespace) -> None:
    frozen = load_and_validate_frozen_inputs(verify_images=args.verify_images)
    artifacts = verify_stage2_artifacts(args.artifact_root)
    print(
        json.dumps(
            {
                "valid_record_count": frozen["valid_record_count"],
                "valid_image_count": frozen["valid_image_count"],
                "mismatch_image_count": frozen["mismatch_image_count"],
                "assignment_core_sha256": frozen["assignment_core_sha256"],
                "verified_model_count": len(artifacts),
                "images_verified": bool(args.verify_images),
            },
            indent=2,
            sort_keys=True,
        )
    )


def candidates_command(_: argparse.Namespace) -> None:
    _, _, pairs = prepare_candidates(write=True)
    print(
        json.dumps(
            {
                "candidate_count": len(pairs),
                "evidence": str(CANDIDATE_EVIDENCE_PATH),
                "evidence_sha256": sha256_file(CANDIDATE_EVIDENCE_PATH),
                "summary": str(CANDIDATE_SUMMARY_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _load_model(
    model_id: str, *, artifact_root: str | Path, device: str
):
    model, metadata, stage2_protocol = load_verified_model(
        model_id,
        artifact_root=artifact_root,
        stage2_protocol_path=REPO_ROOT / "experiments/stage2_protocol_v2.json",
        device=device,
        dtype=torch.float32,
    )
    model.eval()
    return model, metadata, stage2_protocol


def _release_model(model: Any) -> None:
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def smoke_command(args: argparse.Namespace) -> None:
    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("real-model smoke requires an explicit CUDA device")
    seed_everything()
    frozen, tokenizer, pairs = prepare_candidates(write=True)
    selected: list[CandidatePair] = []
    for pair in pairs:
        if not selected or pair.filename != selected[0].filename:
            selected.append(pair)
        if len(selected) == 2:
            break
    if len(selected) != 2 or selected[0].filename == selected[1].filename:
        raise RuntimeError("could not select two deterministic smoke filenames")
    groups = group_pairs_by_filename(selected)

    smoke: dict[str, Any] = {
        "schema_version": 1,
        "device": args.device,
        "selected_samples": [pair.sample_id for pair in selected],
        "selected_filenames": [pair.filename for pair in selected],
        "selection_rule": (
            "first two valid records in formal order with distinct filenames"
        ),
        "model_outputs_used_for_selection": False,
        "models": {},
    }
    for model_id in ("M0-root-43101", "M2-root-43101"):
        method = "M0" if model_id.startswith("M0-") else "M2"
        model, _, _ = _load_model(
            model_id,
            artifact_root=args.artifact_root,
            device=args.device,
        )
        cache = None
        equivalence = None
        if method != "M0":
            names = set()
            for filename in groups:
                mismatch = frozen["mismatch_by_target"][filename]
                names.add(filename)
                names.update(
                    row["donor_filename"] for row in mismatch["donor_rounds"]
                )
            registry = {
                row["model_id"]: row
                for row in frozen["model_registry"]["models"]
            }
            cache = ProjectedFeatureCache(
                model,
                model_id=model_id,
                checkpoint_sha256=registry[model_id]["artifact_sha256"],
                image_entries=frozen["image_entries"],
                device=args.device,
            )
            cache.precompute(names, batch_size=1)
            pair = selected[0]
            candidates = [
                pair.templates["vlm"]["positive"],
                pair.templates["vlm"]["negative"],
            ]
            direct_means = []
            direct_counts = []
            for candidate in candidates:
                means, counts = score_candidate_batch(
                    model,
                    [candidate],
                    tokenizer=tokenizer,
                    device=args.device,
                    pixel_values=cache.actual_pixel_values(pair.filename),
                )
                direct_means.extend(means)
                direct_counts.extend(counts)
            cache.install()
            cached_means = []
            cached_counts = []
            for candidate in candidates:
                with cache.activate([pair.filename]):
                    means, counts = score_candidate_batch(
                        model,
                        [candidate],
                        tokenizer=tokenizer,
                        device=args.device,
                        pixel_values=cache.dummy_pixel_values(1),
                    )
                cached_means.extend(means)
                cached_counts.extend(counts)
            equivalence = {
                "direct_mean_logprob": direct_means,
                "cached_mean_logprob": cached_means,
                "direct_target_counts": direct_counts,
                "cached_target_counts": cached_counts,
                "exact_float_equality": direct_means == cached_means,
                "target_count_equality": direct_counts == cached_counts,
                "maximum_abs_difference": max(
                    abs(left - right)
                    for left, right in zip(direct_means, cached_means)
                ),
            }
            if (
                not equivalence["exact_float_equality"]
                or not equivalence["target_count_equality"]
            ):
                raise RuntimeError("smoke cache/no-cache equivalence failed")

        record_rows = []
        for filename, members in groups.items():
            record_rows.extend(
                score_filename_group(
                    model,
                    members,
                    mismatch_row=frozen["mismatch_by_target"][filename],
                    model_method=method,
                    tokenizer=tokenizer,
                    device=args.device,
                    feature_cache=cache,
                )
            )
        if not all(row["all_scores_finite"] for row in record_rows):
            raise FloatingPointError("smoke produced a non-finite score")
        if method == "M0":
            maximum = max(abs(float(row["d_k5"])) for row in record_rows)
            if maximum > 1e-8:
                raise RuntimeError("smoke M0 invariant failed")
        smoke["models"][model_id] = {
            "status": "passed",
            "record_count": len(record_rows),
            "all_scores_finite": True,
            "max_abs_d_k5": max(
                abs(float(row["d_k5"])) for row in record_rows
            ),
            "cache_equivalence": equivalence,
            "cache_receipt": cache.receipt() if cache is not None else None,
        }
        _release_model(model)
    smoke["status"] = "passed"
    smoke["environment"] = environment_receipt(args.device)
    atomic_write_json(SMOKE_ROOT / "smoke_summary.json", smoke)
    print(json.dumps(smoke, indent=2, sort_keys=True))


def freeze_command(args: argparse.Namespace) -> None:
    if not (SMOKE_ROOT / "smoke_summary.json").is_file():
        raise FileNotFoundError("real-model smoke summary is absent")
    smoke = read_json(SMOKE_ROOT / "smoke_summary.json")
    if smoke.get("status") != "passed":
        raise RuntimeError("real-model smoke has not passed")
    if not CANDIDATE_EVIDENCE_PATH.is_file():
        prepare_candidates(write=True)
    protocol, digest = freeze_protocol(
        device=args.device,
        artifact_root=args.artifact_root,
        candidate_evidence_path=CANDIDATE_EVIDENCE_PATH,
        candidate_summary_path=CANDIDATE_SUMMARY_PATH,
        vision_cache_batch_size=1,
        shard_size_images=32,
    )
    manifest = _new_manifest(digest, args.device)
    _record_command(manifest)
    _write_manifest(manifest)
    print(
        json.dumps(
            {
                "protocol_path": str(PROTOCOL_PATH),
                "protocol_sha256": digest,
                "device": protocol["execution"]["device"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _verified_runtime(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], str, dict[str, Any], Any, list[CandidatePair]]:
    protocol, protocol_sha = verify_protocol()
    if args.device != protocol["execution"]["device"]:
        raise ValueError("runtime device differs from the frozen protocol")
    if str(Path(args.artifact_root).resolve()) != protocol["models"][
        "artifact_root"
    ]:
        raise ValueError("artifact root differs from the frozen protocol")
    frozen, tokenizer, pairs = prepare_candidates(write=False)
    if sha256_file(CANDIDATE_EVIDENCE_PATH) != protocol["frozen_inputs"][
        "candidate_preflight_evidence_sha256"
    ]:
        raise ValueError("candidate evidence changed after protocol freeze")
    if sha256_file(CANDIDATE_SUMMARY_PATH) != protocol["frozen_inputs"][
        "candidate_preflight_summary_sha256"
    ]:
        raise ValueError("candidate summary changed after protocol freeze")
    verify_stage2_artifacts(args.artifact_root)
    manifest = read_json(RUN_MANIFEST_PATH)
    if manifest.get("protocol_sha256") != protocol_sha:
        raise ValueError("run manifest references a different protocol")
    return protocol, protocol_sha, frozen, tokenizer, pairs


def _shard_paths(model_id: str, start: int, end: int) -> tuple[Path, Path]:
    root = PROGRESS_ROOT / model_id
    stem = f"{start:04d}_{end:04d}"
    return root / f"{stem}.jsonl", root / f"{stem}.manifest.json"


def _load_valid_shard(
    data_path: Path,
    manifest_path: Path,
    *,
    protocol_sha: str,
    checkpoint_sha: str,
    expected_sample_ids: list[str],
) -> list[dict[str, Any]] | None:
    if not data_path.is_file() or not manifest_path.is_file():
        return None
    manifest = read_json(manifest_path)
    if (
        manifest.get("status") != "complete"
        or manifest.get("protocol_sha256") != protocol_sha
        or manifest.get("checkpoint_sha256") != checkpoint_sha
        or manifest.get("data_sha256") != sha256_file(data_path)
    ):
        return None
    rows = read_jsonl(data_path)
    if [row.get("sample_id") for row in rows] != expected_sample_ids:
        return None
    return rows


def _write_shard(
    data_path: Path,
    manifest_path: Path,
    rows: Sequence[Mapping[str, Any]],
    *,
    protocol_sha: str,
    checkpoint_sha: str,
) -> None:
    atomic_write_jsonl(data_path, rows)
    atomic_write_json(
        manifest_path,
        {
            "status": "complete",
            "protocol_sha256": protocol_sha,
            "checkpoint_sha256": checkpoint_sha,
            "record_count": len(rows),
            "sample_ids": [row["sample_id"] for row in rows],
            "data_sha256": sha256_file(data_path),
        },
    )


def _cache_equivalence_for_model(
    model,
    cache: ProjectedFeatureCache,
    pair: CandidatePair,
    tokenizer,
    device: str,
) -> dict[str, Any]:
    candidates = [
        pair.templates["vlm"]["positive"],
        pair.templates["vlm"]["negative"],
    ]
    direct_means: list[float] = []
    direct_counts: list[int] = []
    for candidate in candidates:
        means, counts = score_candidate_batch(
            model,
            [candidate],
            tokenizer=tokenizer,
            device=device,
            pixel_values=cache.actual_pixel_values(pair.filename),
        )
        direct_means.extend(means)
        direct_counts.extend(counts)
    cache.install()
    cached_means: list[float] = []
    cached_counts: list[int] = []
    for candidate in candidates:
        with cache.activate([pair.filename]):
            means, counts = score_candidate_batch(
                model,
                [candidate],
                tokenizer=tokenizer,
                device=device,
                pixel_values=cache.dummy_pixel_values(1),
            )
        cached_means.extend(means)
        cached_counts.extend(counts)
    receipt = {
        "sample_id": pair.sample_id,
        "filename": pair.filename,
        "direct_mean_logprob": direct_means,
        "cached_mean_logprob": cached_means,
        "direct_target_counts": direct_counts,
        "cached_target_counts": cached_counts,
        "exact_float_equality": direct_means == cached_means,
        "target_count_equality": direct_counts == cached_counts,
        "maximum_abs_difference": max(
            abs(left - right)
            for left, right in zip(direct_means, cached_means)
        ),
    }
    if (
        not receipt["exact_float_equality"]
        or not receipt["target_count_equality"]
    ):
        raise RuntimeError("formal cache/no-cache equivalence failed")
    return receipt


def _score_one_model(
    model_id: str,
    *,
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
    protocol_sha: str,
    frozen: Mapping[str, Any],
    tokenizer,
    pairs: list[CandidatePair],
    manifest: dict[str, Any],
) -> None:
    registry = {
        row["model_id"]: row for row in frozen["model_registry"]["models"]
    }
    model_row = registry[model_id]
    method = str(model_row["method"])
    checkpoint_sha = str(model_row["artifact_sha256"])
    manifest["models"][model_id] = {
        "status": "running",
        "started_unix_time": time.time(),
    }
    _write_manifest(manifest)
    seed_everything()
    model, _, _ = _load_model(
        model_id, artifact_root=args.artifact_root, device=args.device
    )
    cache = None
    cache_equivalence = None
    if method != "M0":
        cache = ProjectedFeatureCache(
            model,
            model_id=model_id,
            checkpoint_sha256=checkpoint_sha,
            image_entries=frozen["image_entries"],
            device=args.device,
        )
        cache.precompute(
            frozen["image_entries"].keys(),
            batch_size=int(
                protocol["execution"]["vision_cache"]["precompute_batch_size"]
            ),
        )
        if cache.encoded_image_count != 1345:
            raise RuntimeError("visual model did not encode exactly 1345 images")
        cache_equivalence = _cache_equivalence_for_model(
            model, cache, pairs[0], tokenizer, args.device
        )

    groups = group_pairs_by_filename(pairs)
    filenames = list(groups)
    shard_size = int(protocol["execution"]["shard_size_target_images"])
    all_rows: list[dict[str, Any]] = []
    reused_shards = 0
    computed_shards = 0
    for start in range(0, len(filenames), shard_size):
        end = min(start + shard_size, len(filenames))
        names = filenames[start:end]
        expected_ids = [
            pair.sample_id for name in names for pair in groups[name]
        ]
        data_path, shard_manifest_path = _shard_paths(
            model_id, start, end
        )
        shard_rows = _load_valid_shard(
            data_path,
            shard_manifest_path,
            protocol_sha=protocol_sha,
            checkpoint_sha=checkpoint_sha,
            expected_sample_ids=expected_ids,
        )
        if shard_rows is not None:
            reused_shards += 1
            all_rows.extend(shard_rows)
            continue
        shard_rows = []
        for filename in names:
            rows = score_filename_group(
                model,
                groups[filename],
                mismatch_row=frozen["mismatch_by_target"][filename],
                model_method=method,
                tokenizer=tokenizer,
                device=args.device,
                feature_cache=cache,
            )
            for row in rows:
                row.update(
                    {
                        "model_id": model_id,
                        "method": method,
                        "protocol_sha256": protocol_sha,
                    }
                )
            shard_rows.extend(rows)
        if [row["sample_id"] for row in shard_rows] != expected_ids:
            raise RuntimeError("computed shard sample order mismatch")
        _write_shard(
            data_path,
            shard_manifest_path,
            shard_rows,
            protocol_sha=protocol_sha,
            checkpoint_sha=checkpoint_sha,
        )
        computed_shards += 1
        all_rows.extend(shard_rows)
    if len(all_rows) != EXPECTED_VALID_RECORD_COUNT:
        raise RuntimeError("formal model record count mismatch")

    record_path = RECORD_ROOT / f"{model_id}.jsonl"
    atomic_write_jsonl(record_path, all_rows)
    image_rows, summary = summarize_model(model_id, method, all_rows)
    image_path = IMAGE_ROOT / f"{model_id}.jsonl"
    atomic_write_jsonl(image_path, image_rows)
    cache_receipt = (
        cache.receipt()
        if cache is not None
        else {
            "cache_mode": "not_applicable_m0_no_image_input",
            "unique_cached_image_count": 0,
            "encoded_image_count": 0,
            "encoder_forward_call_count": 0,
            "hit_count": 0,
        }
    )
    cache_receipt["cache_no_cache_equivalence"] = cache_equivalence
    cache_receipt_path = CACHE_RECEIPT_ROOT / f"{model_id}.json"
    atomic_write_json(cache_receipt_path, cache_receipt)
    summary.update(
        {
            "protocol_sha256": protocol_sha,
            "checkpoint_sha256": checkpoint_sha,
            "record_scores_sha256": sha256_file(record_path),
            "image_scores_sha256": sha256_file(image_path),
            "cache_receipt_sha256": sha256_file(cache_receipt_path),
            "resume": {
                "reused_shard_count": reused_shards,
                "computed_shard_count": computed_shards,
            },
        }
    )
    summary_path = SUMMARY_ROOT / f"{model_id}.json"
    atomic_write_json(summary_path, summary)
    if method == "M0" and not summary["m0_invariant"][
        "passes_formal_1e_8_invariant"
    ]:
        manifest["models"][model_id] = {
            "status": "failed_m0_invariant",
            "summary_path": str(summary_path.relative_to(REPO_ROOT)),
            "m0_invariant": summary["m0_invariant"],
        }
        manifest["status"] = "failed_m0_invariant"
        _write_manifest(manifest)
        raise RuntimeError(f"{model_id} failed the formal M0 invariant")
    manifest["models"][model_id] = {
        "status": "complete",
        "completed_unix_time": time.time(),
        "record_count": len(all_rows),
        "image_count": len(image_rows),
        "record_scores_sha256": sha256_file(record_path),
        "image_scores_sha256": sha256_file(image_path),
        "summary_sha256": sha256_file(summary_path),
        "cache_receipt_sha256": sha256_file(cache_receipt_path),
    }
    _write_manifest(manifest)
    _release_model(model)


def run_command(args: argparse.Namespace) -> None:
    protocol, protocol_sha, frozen, tokenizer, pairs = _verified_runtime(args)
    manifest = read_json(RUN_MANIFEST_PATH)
    _record_command(manifest)
    requested = (
        EXPECTED_MODEL_IDS
        if args.models == "all"
        else [value.strip() for value in args.models.split(",") if value.strip()]
    )
    if any(model_id not in EXPECTED_MODEL_IDS for model_id in requested):
        raise ValueError("requested model list contains an unknown model")
    ordered = [model for model in EXPECTED_MODEL_IDS if model in requested]
    for model_id in ordered:
        state = manifest["models"].get(model_id, {})
        if state.get("status") == "complete":
            continue
        _score_one_model(
            model_id,
            args=args,
            protocol=protocol,
            protocol_sha=protocol_sha,
            frozen=frozen,
            tokenizer=tokenizer,
            pairs=pairs,
            manifest=manifest,
        )
    if all(
        manifest["models"][model_id].get("status") == "complete"
        for model_id in EXPECTED_MODEL_IDS
    ):
        manifest["status"] = "all_models_complete"
    _write_manifest(manifest)


def reproduce_command(args: argparse.Namespace) -> None:
    _, protocol_sha, _, _, _ = _verified_runtime(args)
    first: dict[str, bytes] = {}
    second: dict[str, bytes] = {}
    for model_id in EXPECTED_MODEL_IDS:
        record_path = RECORD_ROOT / f"{model_id}.jsonl"
        rows = read_jsonl(record_path)
        method = str(rows[0]["method"])
        image_rows_a, summary_a = summarize_model(model_id, method, rows)
        image_rows_b, summary_b = summarize_model(model_id, method, rows)
        first[f"{model_id}:images"] = canonical_jsonl_bytes(image_rows_a)
        second[f"{model_id}:images"] = canonical_jsonl_bytes(image_rows_b)
        first[f"{model_id}:summary"] = canonical_json_bytes(
            summary_a, pretty=True
        )
        second[f"{model_id}:summary"] = canonical_json_bytes(
            summary_b, pretty=True
        )
        if first[f"{model_id}:images"] != second[f"{model_id}:images"]:
            raise RuntimeError("repeated image aggregation differs")
        if first[f"{model_id}:summary"] != second[f"{model_id}:summary"]:
            raise RuntimeError("repeated model summary differs")
        existing_images = read_jsonl(IMAGE_ROOT / f"{model_id}.jsonl")
        if canonical_jsonl_bytes(existing_images) != first[f"{model_id}:images"]:
            raise RuntimeError("stored image scores differ from reproduction")
        existing_summary = read_json(SUMMARY_ROOT / f"{model_id}.json")
        for key in (
            "protocol_sha256",
            "checkpoint_sha256",
            "record_scores_sha256",
            "image_scores_sha256",
            "cache_receipt_sha256",
            "resume",
        ):
            existing_summary.pop(key, None)
        if canonical_json_bytes(
            existing_summary, pretty=True
        ) != first[f"{model_id}:summary"]:
            raise RuntimeError("stored summary metrics differ from reproduction")
    receipt = {
        "status": "passed",
        "protocol_sha256": protocol_sha,
        "model_count": len(EXPECTED_MODEL_IDS),
        "repeated_in_memory_aggregation_byte_identical": True,
        "stored_outputs_match_reproduction": True,
    }
    atomic_write_json(SCORING_ROOT / "aggregation_reproduction.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def compare_command(args: argparse.Namespace) -> None:
    _, protocol_sha, frozen, _, _ = _verified_runtime(args)
    summaries = {
        model_id: read_json(SUMMARY_ROOT / f"{model_id}.json")
        for model_id in EXPECTED_MODEL_IDS
    }
    if not all(
        summary.get("record_count") == EXPECTED_VALID_RECORD_COUNT
        for summary in summaries.values()
    ):
        raise ValueError("a model summary is incomplete")
    if not all(
        summaries[model_id]["m0_invariant"][
            "passes_formal_1e_8_invariant"
        ]
        for model_id in EXPECTED_MODEL_IDS[:3]
    ):
        raise RuntimeError("M0 invariant blocks formal comparison")
    comparison = build_stage2_stage3_comparison(
        args.artifact_root,
        frozen["model_registry"]["models"],
        summaries,
    )
    comparison["protocol_sha256"] = protocol_sha
    if not comparison["m0_zero_gain_check"]["passes"]:
        raise RuntimeError("Stage2/Stage3 comparison M0 zero check failed")
    atomic_write_json(COMPARISON_PATH, comparison)
    print(
        json.dumps(
            {
                "status": "passed",
                "model_count": len(comparison["models"]),
                "output": str(COMPARISON_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _markdown_summary(
    protocol_sha: str,
    summaries: Mapping[str, Mapping[str, Any]],
    comparison: Mapping[str, Any],
) -> str:
    lines = [
        "# Phase 3 v6 frozen contrast-hull scoring",
        "",
        (
            "Scope: fixed 1,343 effective SugarCrepe++ certifying-formal "
            "image groups, fixed contrast hulls, and the fixed balanced K=5 "
            "mismatch manifest."
        ),
        "",
        f"Protocol SHA-256: `{protocol_sha}`",
        "",
        "## Main image-equal results",
        "",
        "| Model | Method | mu K1 | mu K3 | mu K5 | Win rate K5 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model_id in EXPECTED_MODEL_IDS:
        value = summaries[model_id]
        lines.append(
            f"| {model_id} | {value['method']} | "
            f"{value['mu_k1']:.12g} | {value['mu_k3']:.12g} | "
            f"{value['mu_k5']:.12g} | {value['win_rate_k5']:.12g} |"
        )
    lines.extend(
        [
            "",
            "## M0 invariant",
            "",
            "| Model | max record | max image | abs mu K5 | pass 1e-8 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for model_id in EXPECTED_MODEL_IDS[:3]:
        value = summaries[model_id]["m0_invariant"]
        lines.append(
            f"| {model_id} | {value['max_record_abs_d_k5']:.12g} | "
            f"{value['max_image_abs_D_g_k5']:.12g} | "
            f"{value['abs_mu_k5']:.12g} | "
            f"{value['passes_formal_1e_8_invariant']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "These are fixed-benchmark descriptive results. They are not "
                "a new unseen test set, a population guarantee for future "
                "natural images, a new Phase 3 compression bound, or evidence "
                "that random mismatches are equivalent to hard visual negatives."
            ),
            "",
            (
                "Stage 2 correlations, the seven-non-M0 sensitivity analysis, "
                "and the three same-root M2/M3 differences are descriptive only."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _formal_output_hashes() -> dict[str, str]:
    excluded = {
        RUN_RECEIPT_PATH.resolve(),
        RUN_RECEIPT_SHA_PATH.resolve(),
    }
    source_paths = {
        (REPO_ROOT / relative).resolve() for relative in source_hashes()
    }
    paths = sorted(
        (
            path
            for path in SCORING_ROOT.rglob("*")
            if path.is_file()
            and path.resolve() not in excluded
            and path.resolve() not in source_paths
            and "__pycache__" not in path.parts
        ),
        key=lambda path: utf8_key(str(path.relative_to(REPO_ROOT))),
    )
    return {
        str(path.relative_to(REPO_ROOT)): sha256_file(path)
        for path in paths
    }


def finalize_command(args: argparse.Namespace) -> None:
    protocol, protocol_sha, frozen, _, _ = _verified_runtime(args)
    manifest = read_json(RUN_MANIFEST_PATH)
    if not all(
        manifest["models"][model_id].get("status") == "complete"
        for model_id in EXPECTED_MODEL_IDS
    ):
        raise RuntimeError("not all ten models are complete")
    if not (SCORING_ROOT / "aggregation_reproduction.json").is_file():
        raise FileNotFoundError("aggregation reproduction receipt is absent")
    comparison = read_json(COMPARISON_PATH)
    summaries = {
        model_id: read_json(SUMMARY_ROOT / f"{model_id}.json")
        for model_id in EXPECTED_MODEL_IDS
    }
    markdown = _markdown_summary(protocol_sha, summaries, comparison)
    atomic_write_bytes(FINAL_SUMMARY_PATH, (markdown + "\n").encode("utf-8"))
    manifest["status"] = "complete"
    manifest["completed_unix_time"] = time.time()
    _record_command(manifest)
    _write_manifest(manifest)
    output_hashes = _formal_output_hashes()
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "input_sha256": frozen["input_sha256"],
        "assignment_core_sha256": frozen["assignment_core_sha256"],
        "protocol_sha256": protocol_sha,
        "model_weight_sha256": {
            row["model_id"]: row["checkpoint_sha256"]
            for row in protocol["models"]["verified_models"]
        },
        "code_commit": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "git_worktree_status": git_output("status", "--short"),
        "scoring_source_sha256": source_hashes(),
        "scoring_source_tree_sha256": source_tree_sha256(source_hashes()),
        "environment": environment_receipt(args.device),
        "random_seed": GLOBAL_SEED,
        "device": args.device,
        "dtype": "float32",
        "cache_configuration": protocol["execution"]["vision_cache"],
        "actual_record_count": frozen["valid_record_count"],
        "actual_image_group_count": frozen["valid_image_count"],
        "actual_mismatch_image_union_count": frozen["mismatch_image_count"],
        "models": manifest["models"],
        "m0_invariants": {
            model_id: summaries[model_id]["m0_invariant"]
            for model_id in EXPECTED_MODEL_IDS[:3]
        },
        "aggregation_reproduction": read_json(
            SCORING_ROOT / "aggregation_reproduction.json"
        ),
        "all_output_sha256_except_self": output_hashes,
        "self_hash_note": (
            "run_receipt.json cannot contain its own cryptographic hash; the "
            "exact receipt hash is stored in run_receipt.sha256"
        ),
        "protected_code_modified": {
            "experiments_phase3": False,
            "phase2": False,
            "phase3_v4_v5": False,
            "audit": False,
            "audit_v2": False,
            "mismatch_audit": False,
        },
        "claims": {
            "new_unseen_test_set": False,
            "future_population_guarantee": False,
            "new_phase3_compression_bound": False,
            "random_mismatch_equals_hard_negative": False,
        },
    }
    atomic_write_json(RUN_RECEIPT_PATH, receipt)
    receipt_sha = sha256_file(RUN_RECEIPT_PATH)
    atomic_write_bytes(
        RUN_RECEIPT_SHA_PATH,
        f"{receipt_sha}  run_receipt.json\n".encode("ascii"),
    )
    print(
        json.dumps(
            {
                "status": "complete",
                "protocol_sha256": protocol_sha,
                "run_receipt_sha256": receipt_sha,
                "final_summary": str(FINAL_SUMMARY_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
    )
    parser.add_argument("--device", default="cuda:1")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--verify-images", action="store_true")
    validate.set_defaults(function=validate_command)

    candidates = subparsers.add_parser("preflight-candidates")
    candidates.set_defaults(function=candidates_command)

    smoke = subparsers.add_parser("smoke")
    smoke.set_defaults(function=smoke_command)

    freeze = subparsers.add_parser("freeze-protocol")
    freeze.set_defaults(function=freeze_command)

    run = subparsers.add_parser("run")
    run.add_argument("--models", default="all")
    run.set_defaults(function=run_command)

    reproduce = subparsers.add_parser("reproduce")
    reproduce.set_defaults(function=reproduce_command)

    compare = subparsers.add_parser("compare-stage2")
    compare.set_defaults(function=compare_command)

    finalize = subparsers.add_parser("finalize")
    finalize.set_defaults(function=finalize_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.function(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
