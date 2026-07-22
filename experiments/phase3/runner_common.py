"""Shared execution path for smoke, pilot, and formal Phase 3 runs."""

from __future__ import annotations

import os
import platform
import random
import shutil
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from experiments.phase3.aggregate_by_image import (
    MAIN_METRICS, aggregate_rows, empirical_metric_means, m0_row_metrics, visual_row_metrics,
)
from experiments.phase3.artifact_validation import (
    validate_model_verification_receipt,
    validate_overlap_receipt,
    validate_prepared_data,
)
from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, atomic_write_jsonl, canonical_json_bytes,
    inventory_files, load_json_snapshot, load_jsonl_snapshot, sha256_bytes, snapshot_file,
    publish_directory,
)
from experiments.phase3.nll_diagnostics import write_nll_store
from experiments.phase3.phase3_protocol import Phase3Protocol
from experiments.phase3.phase3_protocol import frozen_repository_binding, verify_code_manifest
from experiments.phase3.stage2_adapter_loader import load_verified_model
from experiments.phase3.statistical_bounds import compression_upper, definition_constant, hoeffding_upper
from experiments.phase3.phase3_protocol_v5 import (
    Phase3ProtocolV5, frozen_repository_binding_v5, verify_code_manifest_v5,
)
from experiments.phase3.statistical_bounds_v5 import (
    POST_HOC_STATUS, compression_upper_v5, definition_constant_v5, fixed_model_upper_v5,
)
from experiments.phase3.theory_metrics_v5 import (
    DIAGNOSTIC_METRICS_V5, PRIMARY_METRICS_V5, aggregate_rows_v5,
    empirical_metric_means_v5, m0_row_metrics_v5, visual_row_metrics_v5,
)


NLL_DISCLAIMER = "未平滑 NLL 尾部诊断，仅为后续理论选型提供证据，不构成泛化保证。"
FORMAL_INDEPENDENCE_DISCLOSURE = (
    "0.95 概率声明条件于完整冻结模型与剩余 1,345 个 formal 组从无项目历史图片重叠的"
    "SugarCrepe++ 条件目标分布中 IID 抽样的理论假设；44 个人工确认重叠组已排除；"
    "外部基础模型预训练重叠为 unknown。"
)
FORMAL_CONFIDENCE_STATEMENT = (
    "在本协议明示的条件目标分布 IID、完整模型独立性、冻结和 44 个重叠组排除条件下，"
    "以至少 0.95 的概率，27 个非定义常数主风险的上界同时成立；"
    "三个 M0 模型各自的 visual risk 是精确的定义性常数；30 个主比较槽均被覆盖。"
)


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl_snapshot(path)
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"JSONL rows must be objects: {path.name}")
    return rows


def _copy_snapshot(source: Path, target: Path) -> None:
    atomic_write_bytes(target, snapshot_file(source), overwrite=False)


def verified_image_payload(coco_root: Path, filename: str, expected: dict[str, Any]) -> bytes:
    if expected.get("filename") != filename or expected.get("status") != "ready":
        raise RuntimeError("selected image has no unique ready manifest record")
    payload = snapshot_file(coco_root / filename, root=coco_root)
    if len(payload) != expected.get("size_bytes") or sha256_bytes(payload) != expected.get("sha256"):
        raise RuntimeError("hard_failure_image_changed_after_manifest")
    return payload


def validate_selected_filenames(
    run_mode: str,
    model_ids: list[str],
    filenames: list[str],
    frozen_names: list[str],
) -> None:
    if run_mode == "smoke":
        expected_names = frozen_names[:8]
    elif run_mode == "pilot":
        expected_names = frozen_names
    elif run_mode == "formal":
        if len(model_ids) != 1 or not 1 <= len(filenames) <= 32:
            raise ValueError("formal execution unit must be one model and 1..32 image groups")
        try:
            start = frozen_names.index(filenames[0])
        except (IndexError, ValueError) as error:
            raise ValueError("formal shard does not begin at a frozen filename") from error
        expected_names = frozen_names[start : start + len(filenames)]
    else:
        raise ValueError(f"unknown run mode: {run_mode}")
    if filenames != expected_names or filenames != sorted(set(filenames), key=lambda value: value.encode("utf-8")):
        raise ValueError("selected filenames are not a canonical subset")


def _verify_runner_inputs(
    *,
    run_mode: str,
    protocol_path: Path,
    expected_registry_path: Path,
    verification_receipt_path: Path,
    prepared_data_dir: Path,
    model_ids: list[str],
    filenames: list[str],
    overlap_audit_receipt_path: Path | None,
    metric_version: str = "v4",
) -> tuple[Phase3Protocol | Phase3ProtocolV5, dict[str, Any]]:
    if metric_version == "v4":
        protocol = Phase3Protocol.load(protocol_path)
        code_manifest = protocol_path.parent / "phase3_code_manifest_v2.json"
        code_payload = verify_code_manifest(code_manifest)
    elif metric_version == "v5":
        protocol = Phase3ProtocolV5.load(protocol_path)
        code_manifest = protocol_path.parent / "phase3_code_manifest_v5.json"
        code_payload = verify_code_manifest_v5(code_manifest)
    else:
        raise ValueError(f"unknown metric_version: {metric_version}")
    sidecar = protocol_path.with_suffix(".sha256")
    if snapshot_file(sidecar).decode("ascii") != protocol.raw_sha256 + "\n":
        raise ValueError("protocol sidecar mismatch")
    code_sidecar = code_manifest.with_suffix(".sha256")
    code_raw = canonical_json_bytes(code_payload)
    if snapshot_file(code_sidecar).decode("ascii") != sha256_bytes(code_raw) + "\n":
        raise ValueError("code manifest sidecar mismatch")
    if protocol.payload.get("phase3_code_manifest_sha256") != sha256_bytes(code_raw):
        raise ValueError("protocol/code manifest binding mismatch")
    authority = protocol_path.parent / "phase3_stage2_authority_manifest_v2.json"
    if protocol.payload.get("stage2_authority_manifest_sha256") != sha256_bytes(snapshot_file(authority)):
        raise ValueError("protocol/authority binding mismatch")
    registry = load_json_snapshot(expected_registry_path)
    registry_raw = canonical_json_bytes(registry)
    if protocol.payload.get("expected_model_registry_sha256") != sha256_bytes(registry_raw):
        raise ValueError("protocol/registry binding mismatch")
    if (
        registry.get("schema_version") != 2
        or registry.get("artifact_batch_id") != protocol.payload.get("stage2_artifact_batch_id")
        or registry.get("registry_id") != "phase3-v4-expected-model-registry-v2"
    ):
        raise ValueError("protocol/registry artifact batch mismatch")
    receipt = validate_model_verification_receipt(
        verification_receipt_path,
        expected_registry_path,
        require_all=run_mode in ("pilot", "formal"),
    )
    expected_models = {row["model_id"]: row for row in registry.get("models", [])}
    receipt_models = {row["model_id"]: row for row in receipt.get("models", [])}
    for model_id in model_ids:
        if model_id not in expected_models or receipt_models.get(model_id, {}).get("status") != "verified":
            raise RuntimeError(f"model is not verified: {model_id}")
        receipt_row = receipt_models[model_id]
        expected_row = expected_models[model_id]
        if (
            receipt_row.get("actual_sha256") != expected_row["artifact_sha256"]
            or receipt_row.get("actual_size_bytes") != expected_row["artifact_size_bytes"]
            or receipt_row.get("decoded_method") != expected_row["method"]
            or receipt_row.get("decoded_mapping_root") != expected_row["mapping_root"]
        ):
            raise ValueError("verification receipt model binding mismatch")
    prepared = validate_prepared_data(prepared_data_dir)
    data_manifest, split = prepared["data_manifest"], prepared["split_manifest"]
    if (
        prepared["data_manifest_sha256"] != protocol.payload.get("data_manifest_sha256")
        or prepared["split_manifest_sha256"] != protocol.payload.get("split_manifest_sha256")
    ):
        raise ValueError("prepared data differs from the protocol binding")
    diagnostics = load_json_snapshot(prepared_data_dir / "data_diagnostics.json", root=prepared_data_dir)
    if diagnostics.get("input_invariant_failure_count") != 0 or diagnostics.get("overlength_count") != 0:
        raise ValueError("hard_failure_input_invariant")
    if run_mode == "formal":
        if overlap_audit_receipt_path is None:
            raise ValueError("formal execution requires the bound overlap audit receipt")
        overlap = validate_overlap_receipt(
            overlap_audit_receipt_path,
            split_manifest_path=prepared_data_dir / "split_manifest.json",
            formal_image_manifest_path=prepared_data_dir / "coco_formal_images_manifest.jsonl",
        )
        if (
            overlap["receipt"].get("project_overlap_audit_status")
            != "certification_subset_project_disjoint_under_frozen_checks"
            or overlap["receipt"].get("overlap_audit_input_sha256")
            != protocol.payload.get("overlap_audit_input_sha256")
        ):
            raise ValueError("formal overlap exclusion receipt is not protocol-bound and passing")
        frozen_names = overlap["certifying_names"]
    else:
        filename_entry = next(row for row in split["files"] if row["logical_name"] == "pilot_filenames")
        frozen_names_raw = snapshot_file(prepared_data_dir / filename_entry["relative_path"], root=prepared_data_dir)
        if len(frozen_names_raw) != filename_entry["size_bytes"] or sha256_bytes(frozen_names_raw) != filename_entry["sha256"]:
            raise ValueError("filename membership binding mismatch")
        frozen_names = frozen_names_raw.decode("utf-8").splitlines()
    validate_selected_filenames(run_mode, model_ids, filenames, frozen_names)
    referenced = _jsonl(prepared_data_dir / "coco_referenced_images_manifest.jsonl")
    if (
        len(referenced) != 1542
        or [row.get("filename") for row in referenced]
        != sorted((row.get("filename") for row in referenced), key=lambda value: value.encode("utf-8"))
        or len({row.get("filename") for row in referenced}) != 1542
    ):
        raise ValueError("referenced image manifest order/count/uniqueness mismatch")
    by_name = {row["filename"]: row for row in referenced}
    selected_manifest_name = "coco_formal_images_manifest.jsonl" if run_mode == "formal" else "coco_pilot_images_manifest.jsonl"
    selected_manifest = _jsonl(prepared_data_dir / selected_manifest_name)
    selected_membership = prepared["formal_names"] if run_mode == "formal" else frozen_names
    if selected_manifest != [by_name[name] for name in selected_membership]:
        raise ValueError("split image manifest is not an exact referenced-manifest subset")
    if any(by_name[name].get("status") != "ready" for name in filenames):
        raise RuntimeError("selected image manifest rows are not all ready")
    if run_mode in ("pilot", "formal") and any(row.get("status") != "ready" for row in referenced):
        raise RuntimeError("pilot/formal requires all 1542 image manifest rows ready")
    return protocol, receipt


def _seed() -> None:
    import torch

    random.seed(3407)
    np.random.seed(3407)
    torch.manual_seed(3407)
    torch.cuda.manual_seed_all(3407)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def _accumulate_numerical(target: dict[str, int], scores: dict[str, Any]) -> None:
    for key in (
        "token_brier_below_zero_count", "token_brier_above_two_count",
        "caption_clip_low_count", "caption_clip_high_count",
    ):
        target[key] += int(scores[key])


def _environment(device: str) -> dict[str, Any]:
    import PIL
    import imagehash
    import scipy
    import torch
    import transformers

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "device": device,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "Pillow": PIL.__version__,
        "ImageHash": imagehash.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "autocast_enabled": False,
        "model_dtype": "float32",
    }


def _degenerate_sensitivity(
    row_results: list[dict[str, Any]], degenerate_rows: dict[str, Any], metric_version: str = "v4"
) -> dict[str, Any]:
    if metric_version not in ("v4", "v5"):
        raise ValueError(f"unknown metric_version: {metric_version}")
    aggregate = aggregate_rows if metric_version == "v4" else aggregate_rows_v5
    means = empirical_metric_means if metric_version == "v4" else empirical_metric_means_v5
    excluded = {int(row["row_index"]) for row in degenerate_rows.get("rows", [])}
    output = {"schema_version": 1, "models": []}
    for model_id in sorted({row["model_id"] for row in row_results}, key=lambda value: value.encode("utf-8")):
        original = [row for row in row_results if row["model_id"] == model_id]
        kept = [row for row in original if int(row["row_index"]) not in excluded]
        original_groups = {row["filename"] for row in original}
        groups = aggregate(kept)
        output["models"].append(
            {
                "model_id": model_id,
                "excluded_row_count": len(original) - len(kept),
                "excluded_empty_group_count": len(original_groups - {row["filename"] for row in kept}),
                "remaining_group_n": len(groups),
                "diagnostic_means": means(groups) if groups else None,
                "bound_status": "not_applicable_sensitivity_only",
            }
        )
    return output


def build_metrics_summary(
    run_mode: str,
    model_ids: list[str],
    groups: list[dict[str, Any]],
    registry: dict[str, Any],
    metric_version: str = "v4",
) -> dict[str, Any]:
    if metric_version == "v5":
        return _build_metrics_summary_v5(run_mode, model_ids, groups, registry)
    if metric_version != "v4":
        raise ValueError(f"unknown metric_version: {metric_version}")
    registry_models = {row["model_id"]: row for row in registry["models"]}
    metrics = {
        "schema_version": 1,
        "run_mode": run_mode,
        "bound_name": "simultaneous_project_disjoint_evaluation_bound" if run_mode == "formal" else None,
        "certificate_status": "available_under_frozen_conditions" if run_mode == "formal" else "not_applicable_non_certifying",
        "confidence_statement": FORMAL_CONFIDENCE_STATEMENT if run_mode == "formal" else None,
        "complete_model_independence_disclosure": FORMAL_INDEPENDENCE_DISCLOSURE if run_mode == "formal" else None,
        "estimand_scope": (
            "SugarCrepe++ represented target image-text construction distribution conditional on "
            "no project-history image overlap"
        ),
        "finite_population_guarantee": False,
        "all_natural_images_claim": False,
        "external_base_pretraining_overlap": "unknown",
        "certificate_scope": "project_controlled_image_group_disjoint_certifying_subset_only",
        "delta_families_joint_95_percent_claim": False,
        "m0_cross_input_comparison": "descriptive_different_input_conditions_only",
        "models": [],
    }
    for model_id in model_ids:
        selected_groups = [row for row in groups if row["model_id"] == model_id]
        empirical = empirical_metric_means(selected_groups)
        bounds = {metric: None for metric in MAIN_METRICS}
        exploratory = {metric: None for metric in MAIN_METRICS}
        bound_status = "not_applicable_non_certifying"
        if run_mode == "formal":
            supports = {
                "positive_brier_risk": (0.0, 2.0),
                "visual_semantic_loss": (0.0, 1.0),
                "positive_invariance_loss": (0.0, 1.0),
            }
            n = len(selected_groups)
            method = registry_models[model_id]["method"]
            for metric in MAIN_METRICS:
                values = np.asarray([row[metric] for row in selected_groups], dtype=np.float64)
                if method == "M0" and metric == "visual_semantic_loss":
                    bounds[metric] = definition_constant(0.5, n)
                else:
                    lower, upper = supports[metric]
                    bounds[metric] = hoeffding_upper(
                        empirical[metric], lower, upper, n,
                        observed_min=float(np.min(values)), observed_max=float(np.max(values)),
                    )
                    exploratory[metric] = compression_upper(
                        empirical[metric], lower, upper, n,
                        int(registry_models[model_id]["description_bits"]),
                    )
            bound_status = "simultaneous_project_disjoint_evaluation_bound"
        metrics["models"].append(
            {
                "model_id": model_id,
                "n_unique_image_groups": len(selected_groups),
                "empirical_risks": empirical,
                "bound_status": bound_status,
                "bounds": bounds,
                "exploratory_compression_bounds": exploratory,
            }
        )
    return metrics


def _build_metrics_summary_v5(
    run_mode: str,
    model_ids: list[str],
    groups: list[dict[str, Any]],
    registry: dict[str, Any],
) -> dict[str, Any]:
    registry_models = {row["model_id"]: row for row in registry["models"]}
    metrics: dict[str, Any] = {
        "schema_version": 1,
        "metric_version": "v5",
        "run_mode": run_mode,
        "primary_metrics": list(PRIMARY_METRICS_V5),
        "non_primary_diagnostics": list(DIAGNOSTIC_METRICS_V5),
        "bound_name": "nominal_post_hoc_fixed_and_compression_bounds" if run_mode == "formal" else None,
        "certificate_status": "post_hoc_no_fresh_simultaneous_coverage_claim" if run_mode == "formal" else "not_applicable_non_certifying",
        "selection_status": POST_HOC_STATUS,
        "simultaneous_coverage_claim": False,
        "post_hoc_disclosure": "v5 metrics may have been selected after v4 Formal values were viewed",
        "estimand_scope": (
            "SugarCrepe++ represented target image-text construction distribution conditional on "
            "no project-history image overlap"
        ),
        "finite_population_guarantee": False,
        "all_natural_images_claim": False,
        "external_base_pretraining_overlap": "unknown",
        "models": [],
    }
    for model_id in model_ids:
        selected = [row for row in groups if row["model_id"] == model_id]
        empirical = empirical_metric_means_v5(selected)
        diagnostics: dict[str, float | None] = {}
        for name in DIAGNOSTIC_METRICS_V5:
            values = [row.get(name) for row in selected]
            diagnostics[name] = None if all(value is None for value in values) else float(
                np.mean(np.asarray(values, dtype=np.float64), dtype=np.float64)
            )
        fixed = {name: None for name in PRIMARY_METRICS_V5}
        compression = {name: None for name in PRIMARY_METRICS_V5}
        if run_mode == "formal":
            n = len(selected)
            registry_row = registry_models[model_id]
            bits = int(registry_row["artifact_size_bytes"]) * 8 + 4
            for name in PRIMARY_METRICS_V5:
                values = np.asarray([row[name] for row in selected], dtype=np.float64)
                if registry_row["method"] == "M0" and name == "visual_semantic_loss":
                    fixed[name] = definition_constant_v5(0.5, name, n, family="fixed_model")
                    compression[name] = definition_constant_v5(
                        0.5, name, n, family="compression", description_bits=bits,
                    )
                else:
                    fixed[name] = fixed_model_upper_v5(
                        empirical[name], name, n,
                        observed_min=float(np.min(values)), observed_max=float(np.max(values)),
                    )
                    compression[name] = compression_upper_v5(empirical[name], name, n, bits)
        metrics["models"].append(
            {
                "model_id": model_id,
                "n_unique_image_groups": len(selected),
                "empirical_risks": empirical,
                "diagnostic_means": diagnostics,
                "fixed_model_bounds": fixed,
                "compression_bounds": compression,
            }
        )
    return metrics


def execute_evaluation(
    *,
    run_mode: str,
    model_ids: list[str],
    filenames: list[str],
    protocol_path: Path,
    expected_registry_path: Path,
    verification_receipt_path: Path,
    prepared_data_dir: Path,
    coco_root: Path,
    artifact_root: Path,
    output_dir: Path,
    device: str,
    item_batch_size: int,
    stage2_protocol_path: Path,
    overlap_audit_receipt_path: Path | None = None,
    metric_version: str = "v4",
) -> dict[str, Any]:
    import torch
    from transformers import AutoTokenizer
    from dataset.stage2_dataset import normalized_image
    from model.model_vlm import MiniMindVLM
    from experiments.phase3.caption_scorer import prepare_caption_batch, score_tokenized_batch

    if metric_version not in ("v4", "v5"):
        raise ValueError(f"unknown metric_version: {metric_version}")
    if item_batch_size != 1:
        raise ValueError("item_batch_size is frozen to one")
    if output_dir.exists():
        raise FileExistsError(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("requested CUDA device is unavailable")
    protocol, receipt = _verify_runner_inputs(
        run_mode=run_mode,
        protocol_path=protocol_path,
        expected_registry_path=expected_registry_path,
        verification_receipt_path=verification_receipt_path,
        prepared_data_dir=prepared_data_dir,
        model_ids=model_ids,
        filenames=filenames,
        overlap_audit_receipt_path=overlap_audit_receipt_path,
        metric_version=metric_version,
    )
    if metric_version == "v4":
        repository_binding = {
            "phase3_source_commit": protocol.payload.get("phase3_source_commit"),
            "protocol_repository_commit": None,
            "protocol_tag": None,
            "protocol_tag_object": None,
        }
        if run_mode in ("pilot", "formal"):
            protocol.require_frozen()
            repository_binding = frozen_repository_binding(protocol)
    else:
        repository_binding = {"protocol_repository_commit": None, "protocol_tag": None}
        if run_mode == "formal":
            repository_binding = frozen_repository_binding_v5(protocol)
    receipt_models = {row["model_id"]: row for row in receipt.get("models", [])}
    missing = [model_id for model_id in model_ids if receipt_models.get(model_id, {}).get("status") != "verified"]
    if missing:
        raise RuntimeError(f"models are not verified: {missing}")
    split_name = "formal" if run_mode == "formal" else "pilot"
    source_rows = _jsonl(prepared_data_dir / f"sugarcrepe_pp_{split_name}.jsonl")
    selected = [row for row in source_rows if row["filename"] in set(filenames)]
    by_filename: dict[str, list[dict[str, Any]]] = defaultdict(list)
    canonical_index = {row["row_key"]: row for row in _jsonl(prepared_data_dir / "canonical_row_index.jsonl")}
    for row in selected:
        by_filename[row["filename"]].append(row)
    image_manifest = {row["filename"]: row for row in _jsonl(prepared_data_dir / "coco_referenced_images_manifest.jsonl")}
    if any(name not in by_filename or image_manifest.get(name, {}).get("status") != "ready" for name in filenames):
        raise RuntimeError("selected image groups are missing rows or ready images")
    _seed()
    if device.startswith("cuda"):
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)
    started = time.time()
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    row_results: list[dict[str, Any]] = []
    nll_by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    numerical = {
        "token_brier_below_zero_count": 0,
        "token_brier_above_two_count": 0,
        "caption_clip_low_count": 0,
        "caption_clip_high_count": 0,
        "nan_inf_count": 0,
    }
    try:
        stage2_protocol = None
        tokenizer = None
        for model_id in model_ids:
            model, _, stage2_protocol = load_verified_model(
                model_id,
                artifact_root=artifact_root,
                stage2_protocol_path=stage2_protocol_path,
                device=device,
                dtype=torch.float32,
            )
            if tokenizer is None:
                tokenizer = AutoTokenizer.from_pretrained(stage2_protocol.asset_path("tokenizer"), local_files_only=True)
            method = receipt_models[model_id]["method"]
            for filename in filenames:
                image_tensor = None
                if method != "M0":
                    expected_image = image_manifest[filename]
                    payload = verified_image_payload(coco_root, filename, expected_image)
                    image_tensor = MiniMindVLM.image2tensor(normalized_image(payload), model.processor)
                ordered_rows = sorted(
                    by_filename[filename],
                    key=lambda value: canonical_index[value["row_key"]]["row_index"],
                )
                roles = ("pos1", "pos2", "negative")
                flat_captions = [
                    caption
                    for row in ordered_rows
                    for caption in (row["caption"], row["caption2"], row["negative_caption"])
                ]
                if method == "M0":
                    input_ids, labels, pixels = prepare_caption_batch(
                        flat_captions,
                        "lm_only",
                        image=None,
                        tokenizer=tokenizer,
                        device=device,
                    )
                    lm_scores = score_tokenized_batch(model, input_ids, labels, pixels)
                    _accumulate_numerical(numerical, lm_scores)
                    correct = none = None
                else:
                    input_ids, labels, pixels = prepare_caption_batch(
                        flat_captions,
                        "vision_correct",
                        image=image_tensor,
                        tokenizer=tokenizer,
                        device=device,
                    )
                    correct = score_tokenized_batch(model, input_ids, labels, pixels)
                    none = score_tokenized_batch(model, input_ids, labels, None)
                    _accumulate_numerical(numerical, correct)
                    _accumulate_numerical(numerical, none)
                    lm_scores = None
                for row_offset, row in enumerate(ordered_rows):
                    start, end = row_offset * 3, row_offset * 3 + 3
                    index_row = canonical_index[row["row_key"]]
                    base = {
                        "schema_version": 1,
                        "run_mode": run_mode,
                        "model_id": model_id,
                        "method": method,
                        "mapping_root": receipt_models[model_id]["mapping_root"],
                        "row_index": index_row["row_index"],
                        "source_row_sha256": index_row["source_row_sha256"],
                        "row_key": row["row_key"],
                        "category": row["category"],
                        "numeric_id": row["numeric_id"],
                        "filename": filename,
                    }
                    if method == "M0":
                        raw = lm_scores["caption_brier_raw"][start:end].detach().cpu().tolist()
                        used = lm_scores["caption_brier_used"][start:end].detach().cpu().tolist()
                        values = {
                            "b_none_pos1_raw": raw[0], "b_none_pos1": used[0],
                            "b_none_pos2_raw": raw[1], "b_none_pos2": used[1],
                            "b_none_neg_raw": raw[2], "b_none_neg": used[2],
                            "raw_none_margin": raw[2] - (raw[0] + raw[1]) / 2.0,
                        }
                        row_metric = m0_row_metrics if metric_version == "v4" else m0_row_metrics_v5
                        result = {**base, **row_metric(values)}
                        for role, token_values in zip(roles, lm_scores["token_nll_bits"][start:end]):
                            nll_by_model[model_id].append(
                                {**base, "condition": "lm_only", "caption_role": role, "values": token_values.numpy()}
                            )
                    else:
                        raw_i = correct["caption_brier_raw"][start:end].detach().cpu().tolist()
                        used_i = correct["caption_brier_used"][start:end].detach().cpu().tolist()
                        raw_n = none["caption_brier_raw"][start:end].detach().cpu().tolist()
                        used_n = none["caption_brier_used"][start:end].detach().cpu().tolist()
                        values = {
                            "b_img_pos1_raw": raw_i[0], "b_img_pos1": used_i[0],
                            "b_img_pos2_raw": raw_i[1], "b_img_pos2": used_i[1],
                            "b_img_neg_raw": raw_i[2], "b_img_neg": used_i[2],
                            "b_none_pos1_raw": raw_n[0], "b_none_pos1": used_n[0],
                            "b_none_pos2_raw": raw_n[1], "b_none_pos2": used_n[1],
                            "b_none_neg_raw": raw_n[2], "b_none_neg": used_n[2],
                        }
                        if metric_version == "v4":
                            values["raw_image_margin"] = raw_i[2] - (raw_i[0] + raw_i[1]) / 2.0
                            values["raw_none_margin"] = raw_n[2] - (raw_n[0] + raw_n[1]) / 2.0
                        else:
                            values["raw_image_margin"] = raw_i[2] - max(raw_i[0], raw_i[1])
                            values["raw_none_margin"] = raw_n[2] - max(raw_n[0], raw_n[1])
                        values["raw_visual_increment"] = values["raw_image_margin"] - values["raw_none_margin"]
                        row_metric = visual_row_metrics if metric_version == "v4" else visual_row_metrics_v5
                        result = {**base, **row_metric(values)}
                        for condition, scores in (("correct", correct), ("none", none)):
                            for role, token_values in zip(roles, scores["token_nll_bits"][start:end]):
                                nll_by_model[model_id].append(
                                    {**base, "condition": condition, "caption_role": role, "values": token_values.numpy()}
                                )
                    row_results.append(result)
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        model_order = {model_id: index for index, model_id in enumerate(model_ids)}
        row_results.sort(key=lambda row: (model_order[row["model_id"]], row["row_index"]))
        atomic_write_jsonl(temporary / "row_level_results.jsonl", row_results)
        persisted_rows = _jsonl(temporary / "row_level_results.jsonl")
        aggregate = aggregate_rows if metric_version == "v4" else aggregate_rows_v5
        groups = aggregate(persisted_rows)
        groups.sort(key=lambda row: (model_order[row["model_id"]], row["filename"].encode("utf-8")))
        atomic_write_jsonl(temporary / "image_group_results.jsonl", groups)
        persisted_groups = _jsonl(temporary / "image_group_results.jsonl")
        if run_mode != "formal":
            registry = load_json_snapshot(expected_registry_path)
            metrics = build_metrics_summary(run_mode, model_ids, persisted_groups, registry, metric_version)
            atomic_write_json(temporary / "metrics_summary.json", metrics)
        nll_root = temporary / "nll"
        nll_root.mkdir()
        nll_summary = {"schema_version": 1, "disclaimer": NLL_DISCLAIMER, "models": {}}
        for model_id in model_ids:
            entries = sorted(
                nll_by_model[model_id],
                key=lambda row: (
                    row["filename"].encode("utf-8"), row["category"].encode("utf-8"),
                    int(row["numeric_id"]), {"correct":0,"none":1,"lm_only":2}[row["condition"]],
                    {"pos1":0,"pos2":1,"negative":2}[row["caption_role"]],
                ),
            )
            nll_summary["models"][model_id] = write_nll_store(nll_root / model_id, entries)
        atomic_write_json(temporary / "nll_tail_summary.json", nll_summary)
        if run_mode != "formal":
            degenerates = load_json_snapshot(prepared_data_dir / "degenerate_rows.json")
            atomic_write_json(
                temporary / "degenerate_sensitivity_summary.json",
                _degenerate_sensitivity(persisted_rows, degenerates, metric_version),
            )
        atomic_write_json(temporary / "numerical_diagnostics.json", numerical)
        if device.startswith("cuda"):
            torch.cuda.synchronize(device)
        elapsed = time.time() - started
        atomic_write_json(
            temporary / "timing.json",
            {
                "elapsed_seconds": elapsed,
                "device_name": torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
                "max_memory_allocated_bytes": torch.cuda.max_memory_allocated(device) if device.startswith("cuda") else None,
                "max_memory_reserved_bytes": torch.cuda.max_memory_reserved(device) if device.startswith("cuda") else None,
            },
        )
        atomic_write_json(temporary / "environment.json", _environment(device))
        run_config = {
            "run_mode": run_mode,
            "model_ids": model_ids,
            "filenames": filenames,
            "global_seed": 3407,
            "item_batch_size": 1,
            "device": device,
            "protocol_sha256": protocol.raw_sha256,
            **repository_binding,
        }
        if metric_version == "v5":
            run_config["metric_version"] = "v5"
        atomic_write_json(temporary / "run_config.json", run_config)
        atomic_write_json(temporary / "protocol_reference.json", {"path_alias": "phase3_protocol", "sha256": protocol.raw_sha256, "protocol_kind": protocol.kind})
        for source, name in (
            (expected_registry_path, "expected_model_registry.json"),
            (verification_receipt_path, "model_verification_receipt.json"),
            (prepared_data_dir / "data_manifest.json", "data_manifest.json"),
            (prepared_data_dir / "split_manifest.json", "split_manifest.json"),
            (prepared_data_dir / "data_diagnostics.json", "data_diagnostics.json"),
            (prepared_data_dir / "canonical_row_index.jsonl", "canonical_row_index.jsonl"),
            (prepared_data_dir / "degenerate_rows.json", "degenerate_rows.json"),
        ):
            _copy_snapshot(source, temporary / name)
        run_status = {"schema_version": 1, "status": "success", "run_mode": run_mode}
        if metric_version == "v5":
            run_status["metric_version"] = "v5"
        atomic_write_json(temporary / "run_status.json", run_status)
        inventory = inventory_files(temporary, excluded=("run_manifest.json",))
        authority_path = protocol_path.parent / "phase3_stage2_authority_manifest_v2.json"
        code_manifest_path = protocol_path.parent / (
            "phase3_code_manifest_v2.json" if metric_version == "v4" else "phase3_code_manifest_v5.json"
        )
        run_manifest = {
            "schema_version": 1,
            "run_mode": run_mode,
            "run_status": "success",
            "protocol_sha256": protocol.raw_sha256,
            **repository_binding,
            "phase3_code_manifest_sha256": (
                sha256_bytes(snapshot_file(code_manifest_path)) if code_manifest_path.is_file() else None
            ),
            "stage2_authority_manifest_sha256": (
                sha256_bytes(snapshot_file(authority_path)) if authority_path.is_file() else None
            ),
            "expected_model_registry_sha256": sha256_bytes(snapshot_file(expected_registry_path)),
            "model_verification_receipt_sha256": sha256_bytes(snapshot_file(verification_receipt_path)),
            "data_manifest_sha256": sha256_bytes(snapshot_file(prepared_data_dir / "data_manifest.json")),
            "split_manifest_sha256": sha256_bytes(snapshot_file(prepared_data_dir / "split_manifest.json")),
            "overlap_audit_receipt_sha256": (
                sha256_bytes(snapshot_file(overlap_audit_receipt_path))
                if run_mode == "formal" and overlap_audit_receipt_path is not None
                else None
            ),
            "formal_approval_sha256": None,
            "ordered_model_ids": model_ids,
            "ordered_filenames_sha256": sha256_bytes(("\n".join(filenames) + "\n").encode("utf-8")),
            "row_result_count": len(row_results),
            "image_group_result_count": len(groups),
            "files": inventory,
            "exclusion_rule": "run_manifest.json and transient lock/temp files are excluded",
        }
        if metric_version == "v5":
            run_manifest["metric_version"] = "v5"
        atomic_write_json(temporary / "run_manifest.json", run_manifest)
        publish_directory(temporary, output_dir)
        return {"run_dir": str(output_dir), "row_results": len(row_results), "image_groups": len(groups), "elapsed_seconds": elapsed}
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
