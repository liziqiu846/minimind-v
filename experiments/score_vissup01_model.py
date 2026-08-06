#!/usr/bin/env python3
"""Score one trained VISSUP-01 model on rotation and CV-Bench-2D."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from transformers import AutoTokenizer

from experiments.phase3.caption_scorer import token_nll_bits
from experiments.phase3_v6.scoring.common import (
    atomic_write_json,
    atomic_write_jsonl,
    canonical_jsonl_bytes,
    environment_receipt,
    git_output,
    seed_everything,
)
from experiments.phase3_v6.scoring.image_feature_cache import (
    ProjectedFeatureCache,
)
from experiments.stage2_model import build_stage2_model
from experiments.stage2_protocol import Stage2Protocol
from experiments.vissup01 import (
    ROTATION_LABELS,
    ROTATION_PROMPT,
    answer_margin,
    build_choice_record,
    predicted_label,
    sha256_bytes,
    sha256_file,
)
from model.global_subspace_lora import load_coordinate_state


CONDITIONS = ("label-revealed", "visual-necessary")
MAPPING_ROOTS = (43101, 43102, 43103)
SCORING_SEED = 20260807


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument(
        "--mapping-root", type=int, choices=MAPPING_ROOTS, required=True
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--training-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--item-batch-size", type=int, default=8)
    parser.add_argument("--mode", choices=("smoke", "full"), default="full")
    return parser.parse_args()


def _verify_inputs(args: argparse.Namespace) -> tuple[dict, dict, dict, dict]:
    prepared = args.prepared_dir.resolve()
    data_audit = json.loads(
        (prepared / "data_audit.json").read_text(encoding="utf-8")
    )
    cv_audit = json.loads(
        (prepared / "cvbench_audit.json").read_text(encoding="utf-8")
    )
    rotation_manifest = json.loads(
        (prepared / "heldout_rotation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    cv_manifest = json.loads(
        (prepared / "cvbench_manifest.json").read_text(encoding="utf-8")
    )
    if (
        data_audit.get("eligible_for_training") is not True
        or cv_audit.get("eligible_for_scoring") is not True
        or data_audit.get("final_confirmation_accessed") is not False
        or cv_audit.get("final_confirmation_accessed") is not False
        or len(rotation_manifest.get("rows", [])) != 1008
        or cv_manifest.get("manifest_id")
        != "VISSUP-01-CVBench2D-variable-choice-v1"
    ):
        raise ValueError("prepared manifests do not permit VISSUP scoring")
    return data_audit, cv_audit, rotation_manifest, cv_manifest


def _load_model(
    args: argparse.Namespace,
    protocol: Stage2Protocol,
) -> tuple[Any, dict[str, Any]]:
    training_dir = args.training_dir.resolve()
    manifest_path = training_dir / "training_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    coordinate_path = training_dir / "coordinates.pt"
    if (
        manifest.get("status") != "complete"
        or manifest.get("condition") != args.condition
        or manifest.get("mapping_root") != args.mapping_root
        or manifest.get("final_confirmation_accessed") is not False
        or manifest["coordinates"]["sha256"] != sha256_file(coordinate_path)
    ):
        raise ValueError("training manifest differs from requested model")
    payload = torch.load(
        coordinate_path, map_location="cpu", weights_only=True
    )
    if (
        payload.get("condition") != args.condition
        or payload.get("mapping_root") != args.mapping_root
        or payload.get("model_group") != "M2"
    ):
        raise ValueError("coordinate payload identity mismatch")
    model = build_stage2_model(
        "M2",
        protocol,
        args.mapping_root,
        device=args.device,
        dtype=torch.float32,
    )
    load_coordinate_state(model, payload["coordinates"])
    model.eval()
    checkpoint = {
        "training_manifest_path": str(manifest_path),
        "training_manifest_sha256": sha256_file(manifest_path),
        "coordinate_path": str(coordinate_path),
        "coordinate_sha256": sha256_file(coordinate_path),
        "training_runtime_seconds": manifest["runtime"]["seconds"],
    }
    return model, checkpoint


def _image_entries(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for row in rows:
        path = str(row["image_path"])
        entry = {
            "image_path": path,
            "image_sha256": row["image_sha256"]
            if "image_sha256" in row
            else row["rotated_image_sha256"],
            "normalized_pixel_sha256": row[
                "normalized_pixel_sha256"
            ]
            if "normalized_pixel_sha256" in row
            and "rotated_normalized_pixel_sha256" not in row
            else row["rotated_normalized_pixel_sha256"],
        }
        if path in result and result[path] != entry:
            raise ValueError("one image path has inconsistent metadata")
        result[path] = entry
    return result


def _record_for_item(tokenizer, item: Mapping[str, Any], label: str):
    if item["panel"] == "rotation":
        prompt = ROTATION_PROMPT.format(hint="X").replace(
            "<image>\n", "", 1
        )
        legal = ROTATION_LABELS
    elif item["panel"] == "cvbench":
        prompt = str(item["prompt"])
        legal = tuple(item["legal_labels"])
    else:
        raise ValueError("unknown VISSUP scoring panel")
    return build_choice_record(
        tokenizer,
        prompt,
        label,
        legal_labels=legal,
    )


def _score_batch(
    model,
    items: Sequence[Mapping[str, Any]],
    *,
    tokenizer,
    device: str,
    cache: ProjectedFeatureCache,
) -> list[dict[str, Any]]:
    input_ids = []
    labels = []
    keys = []
    image_paths = []
    for item_index, item in enumerate(items):
        legal = tuple(item["legal_labels"])
        for label in legal:
            record = _record_for_item(tokenizer, item, label)
            input_ids.append(record["input_ids"])
            labels.append(record["labels"])
            keys.append((item_index, label, record["valid_token_count"]))
            image_paths.append(str(item["image_path"]))
    input_tensor = torch.stack(input_ids).to(device)
    label_tensor = torch.stack(labels).to(device)
    with cache.activate(image_paths), torch.inference_mode():
        output = model(
            input_ids=input_tensor,
            labels=None,
            attention_mask=None,
            pixel_values=cache.dummy_pixel_values(len(input_ids)),
        )
    token_values = token_nll_bits(output.logits, label_tensor)
    means = [float(value.double().mean().item()) for value in token_values]
    counts = [int(value.numel()) for value in token_values]
    if not all(math.isfinite(value) for value in means):
        raise FloatingPointError("non-finite VISSUP teacher-forced NLL")
    grids: list[dict[str, Any]] = [
        {"nll": {}, "token_count": {}} for _ in items
    ]
    for (item_index, label, expected_count), value, count in zip(
        keys, means, counts, strict=True
    ):
        if count != expected_count:
            raise RuntimeError("observed answer token count differs")
        grids[item_index]["nll"][label] = value
        grids[item_index]["token_count"][label] = count
    rows = []
    for item, grid in zip(items, grids, strict=True):
        legal = tuple(item["legal_labels"])
        if tuple(grid["nll"]) != legal:
            raise RuntimeError("scoring grid label order differs")
        gold = str(item["gold_label"])
        prediction = predicted_label(grid["nll"], legal)
        base = {
            "panel": item["panel"],
            "item_id": item["item_id"],
            "gold_label": gold,
            "legal_labels": list(legal),
            "choice_count": len(legal),
            "normalized_pixel_sha256": item[
                "normalized_pixel_sha256"
            ],
            "nll_bits_per_token": grid["nll"],
            "answer_label_token_counts": grid["token_count"],
            "gold_margin_bits_per_token": answer_margin(
                grid["nll"], gold, legal
            ),
            "predicted_label": prediction,
            "correct": prediction == gold,
            "all_scores_finite": True,
        }
        if item["panel"] == "rotation":
            base.update(
                {
                    "rotation_degrees_clockwise": item[
                        "rotation_degrees_clockwise"
                    ],
                    "source_base_row_index": item["base_row_index"],
                }
            )
        else:
            base.update(
                {
                    "task": item["task"],
                    "source": item["source"],
                    "source_dataset": item["source_dataset"],
                    "source_filename": item["source_filename"],
                }
            )
        rows.append(base)
    del output
    return rows


def _scoring_items(rotation_manifest: dict, cv_manifest: dict) -> list[dict]:
    items = []
    for row in rotation_manifest["rows"]:
        items.append(
            {
                **row,
                "panel": "rotation",
                "item_id": f"rotation-{int(row['local_index']):04d}",
                "legal_labels": list(ROTATION_LABELS),
                "normalized_pixel_sha256": row[
                    "rotated_normalized_pixel_sha256"
                ],
            }
        )
    for row in cv_manifest["rows"]:
        items.append(
            {
                **row,
                "panel": "cvbench",
                "item_id": f"cvbench-{int(row['idx']):04d}",
            }
        )
    return items


def score(args: argparse.Namespace) -> dict:
    started = time.time()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"scoring output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if (
        args.device != "cuda:0"
        or torch.cuda.device_count() != 1
        or args.item_batch_size < 1
    ):
        raise ValueError("VISSUP scoring requires one cuda:0 and positive batch")
    (
        data_audit,
        cv_audit,
        rotation_manifest,
        cv_manifest,
    ) = _verify_inputs(args)
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    seed_everything(SCORING_SEED)
    model, checkpoint = _load_model(args, protocol)
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"),
        local_files_only=True,
    )
    items = _scoring_items(rotation_manifest, cv_manifest)
    full_item_count = len(items)
    if args.mode == "smoke":
        items = items[:2] + items[1008:1010]
    entries = _image_entries(items)
    cache = ProjectedFeatureCache(
        model,
        model_id=(
            f"VISSUP-01-{args.condition}-root-{args.mapping_root}"
        ),
        checkpoint_sha256=checkpoint["coordinate_sha256"],
        image_entries=entries,
        device=args.device,
    )
    cache.precompute(entries, batch_size=32)
    cache.install()

    def run_all() -> list[dict[str, Any]]:
        raw = []
        for start in range(0, len(items), args.item_batch_size):
            end = min(start + args.item_batch_size, len(items))
            raw.extend(
                _score_batch(
                    model,
                    items[start:end],
                    tokenizer=tokenizer,
                    device=args.device,
                    cache=cache,
                )
            )
            if args.mode == "full" and (
                end == len(items) or end % 256 == 0
            ):
                print(
                    f"condition={args.condition} root={args.mapping_root} "
                    f"scored_items={end}/{len(items)}",
                    flush=True,
                )
        return raw

    first = run_all()
    if args.mode == "smoke":
        second = run_all()
        if first != second:
            raise RuntimeError("deterministic scoring smoke rerun differs")
    raw_sha = sha256_bytes(canonical_jsonl_bytes(first))
    if args.mode == "full":
        if (
            len(first) != full_item_count
            or sum(row["panel"] == "rotation" for row in first) != 1008
            or sum(row["panel"] == "cvbench" for row in first)
            != len(cv_manifest["rows"])
        ):
            raise RuntimeError("VISSUP full scoring output is incomplete")
        raw_path = output / "item_scores.jsonl"
        atomic_write_jsonl(raw_path, first)
        if sha256_file(raw_path) != raw_sha:
            raise RuntimeError("written VISSUP raw SHA differs from memory")
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "candidate": "VISSUP-01",
        "round": 2,
        "mode": args.mode,
        "condition": args.condition,
        "mapping_root": args.mapping_root,
        "checkpoint": checkpoint,
        "prepared_inputs": {
            "data_audit_sha256": sha256_file(
                args.prepared_dir / "data_audit.json"
            ),
            "cvbench_audit_sha256": sha256_file(
                args.prepared_dir / "cvbench_audit.json"
            ),
            "rotation_manifest_sha256": sha256_file(
                args.prepared_dir / "heldout_rotation_manifest.json"
            ),
            "cvbench_manifest_sha256": sha256_file(
                args.prepared_dir / "cvbench_manifest.json"
            ),
            "cvbench_eligible_rows": cv_audit["eligible_rows"],
            "final_confirmation_accessed": False,
        },
        "scoring": {
            "teacher_forced_target": "option_letter_plus_EOS",
            "rotation_labels": list(ROTATION_LABELS),
            "cvbench_labels": "per-row contiguous A-through-F",
            "item_batch_size": args.item_batch_size,
            "items": len(first),
            "raw_rows_sha256": raw_sha,
            "raw_values_persisted": args.mode == "full",
            "scientific_aggregate_computed": False,
            "deterministic_rerun_exact": args.mode == "smoke",
        },
        "cache": cache.receipt(),
        "environment": environment_receipt(args.device),
        "git": {
            "commit": git_output("rev-parse", "HEAD"),
            "tracked_status": git_output(
                "status", "--porcelain", "--untracked-files=no"
            ),
        },
        "peak_cuda_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "elapsed_seconds": time.time() - started,
        "final_confirmation_accessed": False,
    }
    atomic_write_json(output / "scoring_receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    del cache, model
    gc.collect()
    torch.cuda.empty_cache()
    return receipt


def main() -> None:
    score(parse_args())


if __name__ == "__main__":
    main()
