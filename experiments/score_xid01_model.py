#!/usr/bin/env python3
"""Score one trained XID-01 model on the frozen held-out factorial panel."""

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
from experiments.stage2_protocol import Stage2Protocol
from experiments.train_xid01_model import DIMENSIONS, model_builder
from experiments.xid01 import (
    CONDITIONS,
    HELDOUT_GROUPS,
    KEY_BITS,
    MAPPING_ROOTS,
    gold_margin,
    intended_target,
    predicted_digit,
    scoring_record,
    sha256_bytes,
    sha256_file,
)
from model.global_subspace_lora import load_coordinate_state


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


def _verify_inputs(args: argparse.Namespace) -> tuple[dict, dict]:
    prepared = args.prepared_dir.resolve()
    audit = json.loads(
        (prepared / "data_audit.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (prepared / "heldout_manifest.json").read_text(encoding="utf-8")
    )
    if (
        audit.get("eligible_for_scoring") is not True
        or audit.get("final_confirmation_accessed") is not False
        or not all(audit.get("checks", {}).values())
        or manifest.get("manifest_id") != "XID-01-round4-heldout-v1"
        or len(manifest.get("rows", [])) != HELDOUT_GROUPS
        or manifest.get("panel_items_per_group") != 9
        or manifest.get("target_item")
        != {"key": "e", "visual_bit": 1, "gold": "1"}
        or manifest.get("mechanism_keys") != ["a", "b", "c", "d"]
        or manifest.get("final_confirmation_accessed") is not False
    ):
        raise ValueError("prepared manifests do not permit XID-01 scoring")
    return audit, manifest


def _load_model(
    args: argparse.Namespace, protocol: Stage2Protocol
) -> tuple[Any, dict[str, Any]]:
    training_dir = args.training_dir.resolve()
    manifest_path = training_dir / "training_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    coordinate_path = training_dir / "coordinates.pt"
    if (
        manifest.get("status") != "complete"
        or manifest.get("candidate") != "XID-01"
        or manifest.get("round") != 4
        or manifest.get("condition") != args.condition
        or manifest.get("mapping_root") != args.mapping_root
        or manifest.get("final_confirmation_accessed") is not False
        or manifest["model"]["coordinate_dimensions"] != DIMENSIONS
        or manifest["coordinates"]["sha256"] != sha256_file(coordinate_path)
    ):
        raise ValueError("training manifest differs from requested XID-01 model")
    payload = torch.load(
        coordinate_path, map_location="cpu", weights_only=True
    )
    if (
        payload.get("candidate") != "XID-01"
        or payload.get("round") != 4
        or payload.get("condition") != args.condition
        or payload.get("mapping_root") != args.mapping_root
        or payload.get("model_group") != "M2"
    ):
        raise ValueError("coordinate payload identity mismatch")
    model = model_builder(
        protocol,
        args.mapping_root,
        DIMENSIONS,
        device=args.device,
    )
    load_coordinate_state(model, payload["coordinates"])
    model.eval()
    return model, {
        "training_manifest_path": str(manifest_path),
        "training_manifest_sha256": sha256_file(manifest_path),
        "coordinate_path": str(coordinate_path),
        "coordinate_sha256": sha256_file(coordinate_path),
        "training_runtime_seconds": manifest["runtime"]["seconds"],
    }


def _scoring_items(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for row in manifest["rows"]:
        group_id = str(row["group_id"])
        target_variant = row["variants"]["1"]
        items.append(
            {
                "panel": "target",
                "item_id": f"{group_id}-target-e-v1",
                "group_id": group_id,
                "key": "e",
                "visual_bit": 1,
                "gold": "1",
                **target_variant,
            }
        )
        for key in ("a", "b", "c", "d"):
            if key not in KEY_BITS:
                raise RuntimeError("mechanism key is outside frozen mapping")
            for visual_bit in (0, 1):
                variant = row["variants"][str(visual_bit)]
                items.append(
                    {
                        "panel": "mechanism",
                        "item_id": f"{group_id}-mechanism-{key}-v{visual_bit}",
                        "group_id": group_id,
                        "key": key,
                        "visual_bit": visual_bit,
                        "gold": str(intended_target(visual_bit, key)),
                        **variant,
                    }
                )
    return items


def _image_entries(items: Sequence[Mapping[str, Any]]) -> dict[str, dict]:
    entries = {}
    for item in items:
        path = str(item["image_path"])
        entry = {
            "image_path": path,
            "image_sha256": item["image_sha256"],
            "normalized_pixel_sha256": item["normalized_pixel_sha256"],
        }
        if path in entries and entries[path] != entry:
            raise ValueError("one held-out path has inconsistent metadata")
        entries[path] = entry
    return entries


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
        for digit in (0, 1):
            record = scoring_record(tokenizer, str(item["key"]), digit)
            input_ids.append(record["input_ids"])
            labels.append(record["labels"])
            keys.append((item_index, str(digit), record["valid_token_count"]))
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
        raise FloatingPointError("non-finite XID-01 teacher-forced NLL")
    grids = [{"nll": {}, "token_count": {}} for _ in items]
    for (item_index, digit, expected_count), value, count in zip(
        keys, means, counts, strict=True
    ):
        if count != expected_count:
            raise RuntimeError("observed digit target token count differs")
        grids[item_index]["nll"][digit] = value
        grids[item_index]["token_count"][digit] = count
    rows = []
    for item, grid in zip(items, grids, strict=True):
        if tuple(grid["nll"]) != ("0", "1"):
            raise RuntimeError("XID-01 digit scoring order differs")
        gold = str(item["gold"])
        prediction = predicted_digit(grid["nll"])
        rows.append(
            {
                "panel": item["panel"],
                "item_id": item["item_id"],
                "group_id": item["group_id"],
                "key": item["key"],
                "visual_bit": int(item["visual_bit"]),
                "gold": gold,
                "image_sha256": item["image_sha256"],
                "normalized_pixel_sha256": item[
                    "normalized_pixel_sha256"
                ],
                "nll_bits_per_token": grid["nll"],
                "target_token_counts": grid["token_count"],
                "gold_margin_bits_per_token": gold_margin(grid["nll"], gold),
                "predicted_digit": prediction,
                "correct": prediction == gold,
                "all_scores_finite": True,
            }
        )
    del output
    return rows


def score(args: argparse.Namespace) -> dict[str, Any]:
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
        raise ValueError("scoring requires one visible cuda:0 and positive batch")
    audit, heldout = _verify_inputs(args)
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    protocol.verify_immutable_inputs()
    seed_everything(SCORING_SEED)
    model, checkpoint = _load_model(args, protocol)
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"), local_files_only=True
    )
    items = _scoring_items(heldout)
    full_item_count = HELDOUT_GROUPS * 9
    if len(items) != full_item_count:
        raise RuntimeError("XID-01 full panel item count differs")
    if args.mode == "smoke":
        items = items[:2]
    entries = _image_entries(items)
    cache = ProjectedFeatureCache(
        model,
        model_id=f"XID-01-{args.condition}-root-{args.mapping_root}",
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
                end == len(items) or end % 1008 == 0
            ):
                print(
                    f"condition={args.condition} root={args.mapping_root} "
                    f"scored_items={end}/{len(items)}",
                    flush=True,
                )
        return raw

    first = run_all()
    if args.mode == "smoke" and first != run_all():
        raise RuntimeError("deterministic XID-01 scoring smoke rerun differs")
    raw_sha = sha256_bytes(canonical_jsonl_bytes(first))
    if args.mode == "full":
        if (
            len(first) != full_item_count
            or sum(row["panel"] == "target" for row in first)
            != HELDOUT_GROUPS
            or sum(row["panel"] == "mechanism" for row in first)
            != HELDOUT_GROUPS * 8
        ):
            raise RuntimeError("XID-01 full scoring output is incomplete")
        raw_path = output / "item_scores.jsonl"
        atomic_write_jsonl(raw_path, first)
        if sha256_file(raw_path) != raw_sha:
            raise RuntimeError("written XID-01 raw SHA differs from memory")
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "candidate": "XID-01",
        "round": 4,
        "mode": args.mode,
        "condition": args.condition,
        "mapping_root": args.mapping_root,
        "checkpoint": checkpoint,
        "prepared_inputs": {
            "data_audit_sha256": sha256_file(
                args.prepared_dir / "data_audit.json"
            ),
            "heldout_manifest_sha256": sha256_file(
                args.prepared_dir / "heldout_manifest.json"
            ),
            "heldout_groups": audit["heldout_groups"],
            "final_confirmation_accessed": False,
        },
        "scoring": {
            "teacher_forced_target": "singleton_digit_plus_EOS",
            "legal_digits": ["0", "1"],
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
    gc.collect()
    torch.cuda.empty_cache()
    return receipt


if __name__ == "__main__":
    score(parse_args())
