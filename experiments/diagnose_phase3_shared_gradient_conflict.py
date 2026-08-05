#!/usr/bin/env python3
"""Diagnose module-gradient conflict in frozen Phase 3 shared coordinates.

This is a read-only, development-only diagnostic. It never trains a model,
updates a checkpoint, or accepts a confirmation-set path.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import statistics
import struct
import time
import weakref
import zlib
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from torch import nn
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase3_private_vs_shared_v1.adapter_runtime import (
    build_candidate_model,
)
from experiments.phase3_private_vs_shared_v1.certificates import (
    FORMAL_DELTA_SEMANTIC,
    semantic_certificate,
)
from experiments.phase3_private_vs_shared_v1.common import sha256_file
from experiments.phase3_private_vs_shared_v1.configs import (
    generate_matrix,
    matrix_sha256,
)
from experiments.phase3_private_vs_shared_v1.parameterization import (
    CoordinateStore,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import PROTOCOL_PATH
from experiments.stage2_model import tensor_state_sha256
from experiments.stage2_protocol import Stage2Protocol, load_target_registry
from model.global_subspace_lora import HashedLoRALinear, target_specs
from trainer.train_stage2 import move_pixels, permutation_for_epoch, permutation_sha256


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE2_PROTOCOL_PATH = REPO_ROOT / "experiments/stage2_protocol_v2.json"
MODULES = ("vision", "projector", "language")
DIAGNOSTIC_BATCH_COUNT = 16
DIAGNOSTIC_RNG_SEED = 4_310_100
CONFLICT_EPSILON = 1e-12
CHAIN_RELATIVE_L2_TOLERANCE = 1e-4
CHAIN_MAX_ABSOLUTE_TOLERANCE = 1e-5
FORWARD_LOSS_ABSOLUTE_TOLERANCE = 1e-7
MMS2_HEADER = struct.Struct("<4sBBBBBII")
CSV_NAME = "phase3_shared_gradient_conflict_summary.csv"
JSON_NAME = "phase3_shared_gradient_conflict_results.json"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _write_csv_atomic(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty diagnostic CSV")
    columns = list(rows[0])
    if any(list(row) != columns for row in rows):
        raise ValueError("diagnostic CSV rows have inconsistent columns")
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _canonical_sha256(values: Sequence[int]) -> str:
    payload = json.dumps(
        list(values), ensure_ascii=False, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def decode_mms2(path: Path, config: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    """Decode the exact frozen Phase 3 MMS2 representation without mutation."""
    payload = path.read_bytes()
    if len(payload) < MMS2_HEADER.size:
        raise ValueError("MMS2 payload is shorter than its header")
    magic, version, model_id, root_id, groups, bits, body_len, compressed_len = (
        MMS2_HEADER.unpack_from(payload)
    )
    expected_names = (
        ["vision", "projector", "language"]
        if config["structure"] == "P"
        else ["shared"]
    )
    expected_model_id = 2 if config["structure"] == "P" else 3
    expected_root_id = {43101: 1, 43102: 2, 43103: 3}[int(config["seed"])]
    if (
        magic != b"MMS2"
        or version != 1
        or model_id != expected_model_id
        or root_id != expected_root_id
        or groups != len(expected_names)
        or bits != 3
        or len(payload) != MMS2_HEADER.size + compressed_len
    ):
        raise ValueError("MMS2 header differs from the frozen candidate")
    body = zlib.decompress(payload[MMS2_HEADER.size :])
    if len(body) != body_len:
        raise ValueError("MMS2 body length mismatch")
    result: dict[str, torch.Tensor] = {}
    offset = 0
    for name in expected_names:
        if offset + 8 > len(body):
            raise ValueError("MMS2 coordinate header is truncated")
        dimension = struct.unpack_from("<I", body, offset)[0]
        scale = struct.unpack_from("<f", body, offset + 4)[0]
        offset += 8
        if offset + dimension > len(body):
            raise ValueError("MMS2 symbols are truncated")
        symbols = np.frombuffer(
            body, dtype=np.uint8, count=dimension, offset=offset
        )
        offset += dimension
        if (
            dimension != int(config["coordinate_dimensions"][name])
            or np.any(symbols > 6)
        ):
            raise ValueError("MMS2 coordinate group mismatch")
        values = (
            (symbols.astype(np.int16) - 3).astype(np.float32)
            * np.float32(scale)
        )
        result[name] = torch.from_numpy(values.copy())
    if offset != len(body):
        raise ValueError("MMS2 payload has trailing bytes")
    return result


def gradient_metrics(
    gradients: Mapping[str, torch.Tensor],
    *,
    epsilon: float = CONFLICT_EPSILON,
) -> dict[str, float]:
    if tuple(gradients) != MODULES:
        raise ValueError("gradient groups must be vision/projector/language in order")
    vectors = {
        name: value.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
        for name, value in gradients.items()
    }
    dimensions = {value.numel() for value in vectors.values()}
    if len(dimensions) != 1 or not dimensions.pop():
        raise ValueError("module gradients must share one nonempty coordinate system")
    if any(not torch.isfinite(value).all() for value in vectors.values()):
        raise FloatingPointError("module gradient is non-finite")
    mean = sum(vectors.values()) / len(MODULES)
    squared_norms = {
        name: float(torch.dot(value, value)) for name, value in vectors.items()
    }
    norms = {name: math.sqrt(squared_norms[name]) for name in MODULES}
    disagreement = math.fsum(
        float(torch.dot(vectors[name] - mean, vectors[name] - mean))
        for name in MODULES
    )
    denominator = math.fsum(squared_norms.values()) + float(epsilon)
    result = {
        "grad_norm_vision": norms["vision"],
        "grad_norm_projector": norms["projector"],
        "grad_norm_language": norms["language"],
        "D": disagreement,
        "D_norm": disagreement / denominator,
    }
    for first, second in (
        ("vision", "projector"),
        ("vision", "language"),
        ("projector", "language"),
    ):
        dot = float(torch.dot(vectors[first], vectors[second]))
        norm_product = norms[first] * norms[second]
        if norm_product == 0.0:
            raise FloatingPointError("cosine similarity is undefined for a zero gradient")
        suffix = f"{first}_{second}"
        result[f"dot_{suffix}"] = dot
        result[f"cos_{suffix}"] = dot / norm_product
    return result


def summarize_batch_metrics(rows: Sequence[Mapping[str, float]]) -> dict[str, float]:
    if len(rows) < 2:
        raise ValueError("batch summary requires at least two batches")
    keys = list(rows[0])
    if any(list(row) != keys for row in rows):
        raise ValueError("batch metric rows have inconsistent fields")
    output: dict[str, float] = {}
    for key in keys:
        values = [float(row[key]) for row in rows]
        output[f"{key}_mean"] = statistics.fmean(values)
        output[f"{key}_batch_sd"] = statistics.stdev(values)
    return output


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    order = np.argsort(array, kind="mergesort")
    ranks = np.empty(len(array), dtype=np.float64)
    start = 0
    while start < len(array):
        end = start + 1
        while end < len(array) and array[order[end]] == array[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1) + 1.0
        start = end
    return ranks


def _pearson(first: Sequence[float], second: Sequence[float]) -> float:
    x = np.asarray(first, dtype=np.float64)
    y = np.asarray(second, dtype=np.float64)
    if x.shape != y.shape or x.ndim != 1 or x.size < 3:
        raise ValueError("correlation requires equal one-dimensional inputs of size >=3")
    centered_x = x - x.mean()
    centered_y = y - y.mean()
    denominator = float(np.linalg.norm(centered_x) * np.linalg.norm(centered_y))
    if denominator == 0.0:
        raise ValueError("correlation is undefined for a constant input")
    return float(np.dot(centered_x, centered_y) / denominator)


def _spearman(first: Sequence[float], second: Sequence[float]) -> float:
    return _pearson(_average_ranks(first), _average_ranks(second))


def _residualize_by_budget(
    values: Sequence[float], budgets: Sequence[int]
) -> list[float]:
    if len(values) != len(budgets):
        raise ValueError("budget residualization inputs differ in length")
    means = {
        budget: statistics.fmean(
            float(value)
            for value, observed_budget in zip(values, budgets)
            if observed_budget == budget
        )
        for budget in sorted(set(budgets))
    }
    return [
        float(value) - means[budget]
        for value, budget in zip(values, budgets)
    ]


def correlation_report(
    rows: Sequence[Mapping[str, Any]], metric: str, outcome: str = "delta_R"
) -> dict[str, Any]:
    x = [float(row[metric]) for row in rows]
    y = [float(row[outcome]) for row in rows]
    budgets = [int(row["budget"]) for row in rows]
    residual_x = _residualize_by_budget(x, budgets)
    residual_y = _residualize_by_budget(y, budgets)
    leave_one_budget_out = {}
    for budget in sorted(set(budgets)):
        selected = [index for index, value in enumerate(budgets) if value != budget]
        leave_one_budget_out[str(budget)] = {
            "pair_count": len(selected),
            "pearson_r": _pearson([x[index] for index in selected], [y[index] for index in selected]),
            "spearman_rho": _spearman(
                [x[index] for index in selected], [y[index] for index in selected]
            ),
        }
    return {
        "metric": metric,
        "outcome": outcome,
        "pair_count": len(rows),
        "pearson_r": _pearson(x, y),
        "spearman_rho": _spearman(x, y),
        "budget_residualized_pearson_r": _pearson(residual_x, residual_y),
        "budget_residualized_spearman_rho": _spearman(residual_x, residual_y),
        "leave_one_budget_out": leave_one_budget_out,
    }


def _binary_summary(actual: Sequence[bool], predicted: Sequence[bool]) -> dict[str, Any]:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("binary prediction inputs are empty or differ in length")
    tp = sum(a and p for a, p in zip(actual, predicted))
    tn = sum((not a) and (not p) for a, p in zip(actual, predicted))
    fp = sum((not a) and p for a, p in zip(actual, predicted))
    fn = sum(a and (not p) for a, p in zip(actual, predicted))
    positive_count = tp + fn
    negative_count = tn + fp
    balanced = 0.5 * (
        tp / positive_count + tn / negative_count
    ) if positive_count and negative_count else float("nan")
    return {
        "accuracy": (tp + tn) / len(actual),
        "balanced_accuracy": balanced,
        "confusion": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
        },
    }


def sign_prediction_report(
    rows: Sequence[Mapping[str, Any]], metric: str
) -> dict[str, Any]:
    x = [float(row[metric]) for row in rows]
    actual = [float(row["delta_R"]) > 0.0 for row in rows]
    predicted = []
    majority_predictions = []
    thresholds = []
    for held_out in range(len(rows)):
        training_x = [value for index, value in enumerate(x) if index != held_out]
        threshold = statistics.median(training_x)
        thresholds.append(threshold)
        predicted.append(x[held_out] > threshold)
        training_y = [value for index, value in enumerate(actual) if index != held_out]
        positive_count = sum(training_y)
        majority_predictions.append(positive_count > len(training_y) / 2)
    median = statistics.median(x)
    high = [value > median for value in x]
    high_actual = [value for value, selected in zip(actual, high) if selected]
    low_actual = [value for value, selected in zip(actual, high) if not selected]
    return {
        "metric": metric,
        "prediction_rule": (
            "leave-one-pair-out: predict S loses P iff held-out conflict exceeds "
            "the median conflict of the other eight pairs"
        ),
        "thresholds": thresholds,
        "prediction": _binary_summary(actual, predicted),
        "leave_one_out_majority_baseline": _binary_summary(
            actual, majority_predictions
        ),
        "global_median_descriptive_split": {
            "median": median,
            "high_count": len(high_actual),
            "low_count": len(low_actual),
            "S_loss_rate_high": sum(high_actual) / len(high_actual),
            "S_loss_rate_low": sum(low_actual) / len(low_actual),
        },
    }


def complexity_conflict_report(
    rows: Sequence[Mapping[str, Any]], metric: str
) -> dict[str, Any]:
    conflict_median = statistics.median(float(row[metric]) for row in rows)
    gain_median = statistics.median(float(row["G_C"]) for row in rows)
    selected = [
        float(row[metric]) > conflict_median and float(row["G_C"]) > gain_median
        for row in rows
    ]
    paradox = [
        float(row["G_C"]) > 0.0 and float(row["delta_R"]) >= 0.0
        for row in rows
    ]
    inside = [value for value, keep in zip(paradox, selected) if keep]
    outside = [value for value, keep in zip(paradox, selected) if not keep]
    return {
        "metric": metric,
        "high_definition": "strictly_above_cross_pair_median",
        "conflict_median": conflict_median,
        "complexity_gain_median": gain_median,
        "high_high_count": len(inside),
        "other_count": len(outside),
        "paradox_definition": "G_C > 0 and delta_R >= 0",
        "paradox_rate_high_G_C_and_high_conflict": (
            sum(inside) / len(inside) if inside else None
        ),
        "paradox_rate_other_pairs": sum(outside) / len(outside) if outside else None,
        "high_high_config_ids": [
            str(row["S_config_id"])
            for row, keep in zip(rows, selected)
            if keep
        ],
        "high_high_paradox_config_ids": [
            str(row["S_config_id"])
            for row, keep, is_paradox in zip(rows, selected, paradox)
            if keep and is_paradox
        ],
    }


def evaluate_criteria(
    correlations: Mapping[str, Mapping[str, Any]],
    sign_predictions: Mapping[str, Mapping[str, Any]],
    conjunctions: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    association_pass = all(
        report["pearson_r"] > 0.0
        and report["spearman_rho"] > 0.0
        and report["budget_residualized_pearson_r"] > 0.0
        and report["budget_residualized_spearman_rho"] > 0.0
        and all(
            held_out["pearson_r"] > 0.0 and held_out["spearman_rho"] > 0.0
            for held_out in report["leave_one_budget_out"].values()
        )
        for report in correlations.values()
    )
    sign_pass = all(
        report["global_median_descriptive_split"]["S_loss_rate_high"]
        > report["global_median_descriptive_split"]["S_loss_rate_low"]
        and report["prediction"]["accuracy"]
        > report["leave_one_out_majority_baseline"]["accuracy"]
        for report in sign_predictions.values()
    )
    conjunction_pass = all(
        report["high_high_count"] >= 2
        and report["paradox_rate_high_G_C_and_high_conflict"] is not None
        and report["paradox_rate_other_pairs"] is not None
        and report["paradox_rate_high_G_C_and_high_conflict"]
        > report["paradox_rate_other_pairs"]
        for report in conjunctions.values()
    )
    return {
        "criterion_1_stable_positive_prediction_of_delta_R": {
            "pass": association_pass,
            "rule": (
                "For both D and D_norm, Pearson and Spearman correlations must "
                "be positive overall, after within-budget residualization, and "
                "in every leave-one-budget-out analysis."
            ),
        },
        "criterion_2_high_conflict_predicts_S_loss_sign": {
            "pass": sign_pass,
            "rule": (
                "For both D and D_norm, the above-median conflict group must "
                "have a higher S-loss rate and leave-one-pair-out median-threshold "
                "accuracy must beat its leave-one-pair-out majority baseline."
            ),
        },
        "criterion_3_large_complexity_gain_plus_conflict_matches_paradox": {
            "pass": conjunction_pass,
            "rule": (
                "For both D and D_norm, at least two pairs must be above both "
                "cross-pair medians and their G_C>0, delta_R>=0 paradox rate "
                "must exceed that of all other pairs."
            ),
        },
        "all_three_pass": association_pass and sign_pass and conjunction_pass,
    }


def _module_group_map() -> dict[str, str]:
    specs = target_specs(load_target_registry(), MODULES)
    output = {spec.canonical_name: spec.module_group for spec in specs}
    if len(output) != 11 or set(output.values()) != set(MODULES):
        raise RuntimeError("target registry does not contain the expected 11 targets")
    return output


def _wire_store(
    model: nn.Module,
    store: CoordinateStore,
    *,
    split: bool,
    groups: Mapping[str, str],
) -> dict[str, int]:
    model.stage2_coordinates = store  # type: ignore[attr-defined]
    counts = {name: 0 for name in MODULES}
    wrapped = 0
    for module in model.modules():
        if not isinstance(module, HashedLoRALinear):
            continue
        if module.canonical_name not in groups:
            raise ValueError(f"unregistered hashed LoRA target: {module.canonical_name}")
        group = groups[module.canonical_name]
        module._coordinate_store_ref = weakref.ref(store)
        module.coordinate_group = group if split else "shared"
        counts[group] += 1
        wrapped += 1
    if wrapped != len(groups) or counts != {
        "vision": 4,
        "projector": 2,
        "language": 5,
    }:
        raise RuntimeError(f"unexpected module split target counts: {counts}")
    return counts


def _make_split_store(shared: torch.Tensor, device: torch.device) -> CoordinateStore:
    dimensions = OrderedDict((name, int(shared.numel())) for name in MODULES)
    store = CoordinateStore("P", dimensions).to(device=device, dtype=torch.float32)
    with torch.no_grad():
        for parameter in store.coordinates.values():
            parameter.copy_(shared.to(device=device, dtype=torch.float32))
    values = [store.coordinates[name] for name in MODULES]
    if not all(torch.equal(values[0], value) for value in values[1:]):
        raise AssertionError("diagnostic split coordinates are not numerically identical")
    pointers = [value.untyped_storage().data_ptr() for value in values]
    if len(set(pointers)) != len(MODULES):
        raise AssertionError("diagnostic split coordinates share storage")
    if not all(value.is_leaf and value.requires_grad for value in values):
        raise AssertionError("diagnostic split coordinates are not independent leaves")
    return store


def _set_forward_seed(device: torch.device, batch_index: int) -> None:
    seed = DIAGNOSTIC_RNG_SEED + batch_index
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)


def _forward_loss(
    model: nn.Module,
    input_ids: torch.Tensor,
    labels: torch.Tensor,
    pixels: Any,
    device: torch.device,
) -> torch.Tensor:
    loss = model(
        input_ids=input_ids,
        labels=labels,
        pixel_values=pixels,
    ).loss
    if loss.ndim != 0 or not torch.isfinite(loss):
        raise FloatingPointError("diagnostic training loss is invalid")
    return loss


def diagnose_model(
    model: nn.Module,
    batches: Sequence[tuple[torch.Tensor, torch.Tensor, Any]],
    device: torch.device,
) -> dict[str, Any]:
    original_store = model.stage2_coordinates  # type: ignore[attr-defined]
    if tuple(original_store.coordinates) != ("shared",):
        raise ValueError("diagnostic model is not an S/shared candidate")
    shared = original_store.coordinates["shared"]
    split_store = _make_split_store(shared.detach(), device)
    groups = _module_group_map()
    target_counts = _wire_store(
        model, original_store, split=False, groups=groups
    )
    model.train()
    model.vision_encoder.eval()  # type: ignore[attr-defined]

    batch_rows = []
    verification_rows = []
    for batch_index, cpu_batch in enumerate(batches):
        input_ids = cpu_batch[0].to(device, non_blocking=True)
        labels = cpu_batch[1].to(device, non_blocking=True)
        pixels = move_pixels(cpu_batch[2], device)

        _wire_store(model, original_store, split=False, groups=groups)
        _set_forward_seed(device, batch_index)
        shared_loss = _forward_loss(model, input_ids, labels, pixels, device)
        (shared_gradient,) = torch.autograd.grad(
            shared_loss, (original_store.coordinates["shared"],)
        )

        _wire_store(model, split_store, split=True, groups=groups)
        _set_forward_seed(device, batch_index)
        split_loss = _forward_loss(model, input_ids, labels, pixels, device)
        split_gradients_tuple = torch.autograd.grad(
            split_loss, tuple(split_store.coordinates[name] for name in MODULES)
        )
        split_gradients = OrderedDict(zip(MODULES, split_gradients_tuple))
        metrics = gradient_metrics(split_gradients)
        metrics["training_loss"] = float(split_loss.detach())
        batch_rows.append(metrics)

        summed = sum(
            value.detach().to(dtype=torch.float64)
            for value in split_gradients.values()
        )
        expected = shared_gradient.detach().to(dtype=torch.float64)
        difference = expected - summed
        expected_norm = float(torch.linalg.vector_norm(expected))
        absolute_l2 = float(torch.linalg.vector_norm(difference))
        relative_l2 = absolute_l2 / max(expected_norm, CONFLICT_EPSILON)
        max_absolute = float(torch.max(torch.abs(difference)))
        loss_difference = abs(float(shared_loss.detach()) - float(split_loss.detach()))
        verification_rows.append(
            {
                "batch_index": batch_index,
                "shared_loss": float(shared_loss.detach()),
                "split_loss": float(split_loss.detach()),
                "forward_loss_absolute_difference": loss_difference,
                "gradient_sum_absolute_l2_error": absolute_l2,
                "gradient_sum_relative_l2_error": relative_l2,
                "gradient_sum_max_absolute_error": max_absolute,
                "pass": (
                    loss_difference <= FORWARD_LOSS_ABSOLUTE_TOLERANCE
                    and relative_l2 <= CHAIN_RELATIVE_L2_TOLERANCE
                    and max_absolute <= CHAIN_MAX_ABSOLUTE_TOLERANCE
                ),
            }
        )
        del (
            input_ids,
            labels,
            pixels,
            shared_loss,
            split_loss,
            shared_gradient,
            split_gradients_tuple,
            split_gradients,
        )

    return {
        "target_counts": target_counts,
        "coordinate_values_identical": True,
        "coordinate_storage_independent": True,
        "coordinate_graph_leaves_independent": True,
        "batch_metrics": batch_rows,
        "summary": summarize_batch_metrics(batch_rows),
        "gradient_sum_verification": {
            "all_batches_pass": all(row["pass"] for row in verification_rows),
            "maximum_forward_loss_absolute_difference": max(
                row["forward_loss_absolute_difference"] for row in verification_rows
            ),
            "maximum_gradient_sum_absolute_l2_error": max(
                row["gradient_sum_absolute_l2_error"] for row in verification_rows
            ),
            "maximum_gradient_sum_relative_l2_error": max(
                row["gradient_sum_relative_l2_error"] for row in verification_rows
            ),
            "maximum_gradient_sum_max_absolute_error": max(
                row["gradient_sum_max_absolute_error"] for row in verification_rows
            ),
            "per_batch": verification_rows,
        },
    }


def _indexed_file(row: Mapping[str, Any], suffix: str) -> Mapping[str, Any]:
    matches = [
        item for item in row["files"] if str(item["path"]).endswith(suffix)
    ]
    if len(matches) != 1:
        raise ValueError(f"indexed candidate does not have exactly one {suffix}")
    return matches[0]


def audit_inputs(ps_root: Path) -> dict[str, Any]:
    root = ps_root.resolve()
    index_path = root / "training_artifact_index.json"
    aggregate_path = root / "development_evaluation/aggregate_results.json"
    evaluation_index_path = (
        root / "development_evaluation/evaluation_artifact_index.json"
    )
    evaluation_source_path = root / "development_evaluation/evaluate_models.py"
    run_manifest_path = root / "run_manifest.json"
    index = _load_json(index_path)
    aggregate = _load_json(aggregate_path)
    evaluation_index = _load_json(evaluation_index_path)
    run_manifest = _load_json(run_manifest_path)
    protocol = _load_json(PROTOCOL_PATH)
    protocol_hash = sha256_file(PROTOCOL_PATH)
    if (
        index.get("status") != "complete"
        or len(index.get("models", [])) != 18
        or aggregate.get("status") != "complete"
        or aggregate.get("model_count") != 18
        or aggregate.get("final_confirmation_accessed") is not False
        or aggregate.get("analysis_scope")
        != "development_only_exploratory_not_a_formal_certificate"
        or evaluation_index.get("status") != "complete"
        or evaluation_index.get("model_count") != 18
        or evaluation_index.get("final_confirmation_accessed") is not False
        or evaluation_index.get("analysis_scope")
        != "development_only_exploratory_not_a_formal_certificate"
        or evaluation_index.get("protocol_sha256") != protocol_hash
        or evaluation_index.get("candidate_matrix_sha256") != matrix_sha256()
        or evaluation_index.get("training_artifact_index_sha256")
        != sha256_file(index_path)
        or evaluation_index.get("aggregate", {}).get("sha256")
        != sha256_file(aggregate_path)
        or evaluation_index.get("evaluation_source_sha256")
        != sha256_file(evaluation_source_path)
        or protocol.get("status") != "frozen"
        or index.get("protocol_sha256") != protocol_hash
        or aggregate.get("protocol_sha256") != protocol_hash
        or run_manifest.get("protocol_sha256") != protocol_hash
        or matrix_sha256() != index.get("candidate_matrix_sha256")
    ):
        raise ValueError("P/S artifact bindings, scope, or completion state are invalid")
    configs = generate_matrix()
    index_by = {row["config_id"]: row for row in index["models"]}
    result_by = {row["config_id"]: row for row in aggregate["models"]}
    evaluation_index_by = {
        row["config_id"]: row for row in evaluation_index["models"]
    }
    if (
        set(index_by) != {row["config_id"] for row in configs}
        or set(result_by) != set(index_by)
        or set(evaluation_index_by) != set(index_by)
    ):
        raise ValueError("P/S artifact candidate identities differ from the frozen matrix")
    artifacts = {}
    for config in configs:
        config_id = config["config_id"]
        indexed = index_by[config_id]
        result = result_by[config_id]
        manifest_path = root / f"candidates/{config_id}/training_manifest.json"
        manifest = _load_json(manifest_path)
        checkpoint_entry = _indexed_file(indexed, "/checkpoint.pt")
        archive_entry = _indexed_file(indexed, "/adapter.mms2")
        checkpoint = root / checkpoint_entry["path"]
        archive = root / archive_entry["path"]
        if (
            manifest.get("status") != "complete"
            or manifest.get("config_id") != config_id
            or manifest.get("config") != config
            or sha256_file(manifest_path) != indexed["manifest_sha256"]
            or checkpoint.stat().st_size != checkpoint_entry["bytes"]
            or archive.stat().st_size != archive_entry["bytes"]
            or sha256_file(checkpoint) != checkpoint_entry["sha256"]
            or sha256_file(archive) != archive_entry["sha256"]
            or manifest["checkpoint"]["sha256"] != checkpoint_entry["sha256"]
            or manifest["encoding"]["sha256"] != archive_entry["sha256"]
            or result["evaluated_archive_sha256"] != archive_entry["sha256"]
            or evaluation_index_by[config_id]["evaluated_archive_sha256"]
            != archive_entry["sha256"]
            or int(result["complexity"]["coded_bits"]) != archive.stat().st_size * 8
        ):
            raise ValueError(f"{config_id}: artifact identity or evaluation binding mismatch")
        artifacts[config_id] = {
            "config": config,
            "index": indexed,
            "result": result,
            "manifest": manifest,
            "manifest_path": manifest_path,
            "checkpoint_path": checkpoint,
            "archive_path": archive,
            "checkpoint_sha256": checkpoint_entry["sha256"],
            "archive_sha256": archive_entry["sha256"],
        }
    return {
        "root": root,
        "index": index,
        "aggregate": aggregate,
        "evaluation_index": evaluation_index,
        "run_manifest": run_manifest,
        "protocol": protocol,
        "artifacts": artifacts,
        "input_hashes": {
            "phase3_protocol": protocol_hash,
            "training_artifact_index": sha256_file(index_path),
            "development_aggregate": sha256_file(aggregate_path),
            "development_evaluation_artifact_index": sha256_file(
                evaluation_index_path
            ),
            "development_evaluation_source": sha256_file(
                evaluation_source_path
            ),
            "run_manifest": sha256_file(run_manifest_path),
        },
    }


def _verify_checkpoint_coordinates(artifact: Mapping[str, Any]) -> dict[str, Any]:
    checkpoint = torch.load(
        artifact["checkpoint_path"], map_location="cpu", weights_only=True
    )
    if (
        checkpoint.get("config_id") != artifact["config"]["config_id"]
        or checkpoint.get("protocol_sha256")
        != artifact["manifest"]["protocol_sha256"]
        or checkpoint.get("candidate_matrix_sha256")
        != artifact["manifest"]["candidate_matrix_sha256"]
    ):
        raise ValueError("checkpoint payload binding mismatch")
    coordinates = checkpoint.get("coordinates")
    expected = (
        ("vision", "projector", "language")
        if artifact["config"]["structure"] == "P"
        else ("shared",)
    )
    if not isinstance(coordinates, dict) or set(coordinates) != set(expected):
        raise ValueError("checkpoint coordinate groups differ from structure")
    state_hash = tensor_state_sha256(coordinates)
    if state_hash != artifact["manifest"]["coordinate_state_sha256"]:
        raise ValueError("checkpoint coordinate-state SHA-256 mismatch")
    return {
        "coordinate_state_sha256": state_hash,
        "coordinate_groups": list(coordinates),
        "coordinate_count": sum(value.numel() for value in coordinates.values()),
    }


def _build_batches(
    artifact_root: Path,
    stage2: Stage2Protocol,
    processor: Any,
) -> tuple[list[tuple[torch.Tensor, torch.Tensor, Any]], dict[str, Any]]:
    phase3_protocol = _load_json(PROTOCOL_PATH)
    fairness = phase3_protocol["fairness"]
    data_path = (
        artifact_root.resolve()
        / fairness["training_data"]["relative_path"]
    )
    if sha256_file(data_path) != fairness["training_data"]["sha256"]:
        raise ValueError("diagnostic training-data SHA-256 mismatch")
    tokenizer = AutoTokenizer.from_pretrained(
        stage2.asset_path("tokenizer"), local_files_only=True
    )
    dataset = Stage2CaptionDataset(
        data_path,
        tokenizer,
        model_group="M3",
        processor=processor,
        max_length=stage2.payload["training"]["max_sequence_length"],
        image_token_count=stage2.payload["model"]["image_token_count"],
    )
    expected_examples = int(stage2.payload["data"]["train_draws"])
    if len(dataset) != expected_examples:
        raise ValueError("diagnostic dataset size differs from frozen training protocol")
    micro_batch = int(fairness["micro_batch_size"])
    if micro_batch != int(stage2.payload["training"]["micro_batch_size"]):
        raise ValueError("Phase 3 and Stage 2 micro-batch sizes differ")
    permutation = permutation_for_epoch(
        len(dataset), int(fairness["training_data"]["train_seed"]), 0
    )
    selected_indices = permutation[: DIAGNOSTIC_BATCH_COUNT * micro_batch].tolist()
    batches = []
    for start in range(0, len(selected_indices), micro_batch):
        items = [
            dataset[index] for index in selected_indices[start : start + micro_batch]
        ]
        batches.append(stage2_collate(items))
    if len(batches) != DIAGNOSTIC_BATCH_COUNT:
        raise AssertionError("diagnostic batch materialization count mismatch")
    return batches, {
        "role": "existing_phase3_training_data_for_development_diagnostic",
        "path": str(data_path),
        "sha256": sha256_file(data_path),
        "final_fresh_confirmation_accessed": False,
        "batch_selection": (
            "first 16 micro-batches of frozen epoch-0 permutation; no batch CLI"
        ),
        "epoch": 0,
        "train_seed": int(fairness["training_data"]["train_seed"]),
        "permutation_sha256": permutation_sha256(permutation),
        "selected_example_count": len(selected_indices),
        "selected_indices": selected_indices,
        "selected_indices_sha256": _canonical_sha256(selected_indices),
        "micro_batch_size": micro_batch,
        "batch_count": len(batches),
    }


def _complexity_penalty(
    coded_bits: float, sample_count: int, protocol: Mapping[str, Any]
) -> float:
    smoothing = protocol["evaluation"]["semantic_smoothing"]
    return float(
        semantic_certificate(
            0.0,
            sample_count,
            coded_bits,
            FORMAL_DELTA_SEMANTIC,
            vocab_size=int(smoothing["vocab_size"]),
            alpha=float(smoothing["alpha"]),
        )["complexity_penalty"]
    )


def _pair_row(
    p: Mapping[str, Any],
    s: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    p_result = p["result"]
    s_result = s["result"]
    p_risk = float(p_result["semantic"]["empirical_smoothed_conditional_nll_bits"])
    s_risk = float(s_result["semantic"]["empirical_smoothed_conditional_nll_bits"])
    p_bits = int(p_result["complexity"]["coded_bits"])
    s_bits = int(s_result["complexity"]["coded_bits"])
    sample_count = int(p_result["image_count"])
    if sample_count != int(s_result["image_count"]):
        raise ValueError("paired development sample counts differ")
    omega_p = _complexity_penalty(p_bits, sample_count, protocol)
    omega_s = _complexity_penalty(s_bits, sample_count, protocol)
    summary = diagnostic["summary"]
    verification = diagnostic["gradient_sum_verification"]
    return {
        "budget": int(s["config"]["budget"]),
        "seed": int(s["config"]["seed"]),
        "P_config_id": p["config"]["config_id"],
        "S_config_id": s["config"]["config_id"],
        "P_checkpoint_path": str(p["checkpoint_path"]),
        "P_checkpoint_sha256": p["checkpoint_sha256"],
        "S_checkpoint_path": str(s["checkpoint_path"]),
        "S_checkpoint_sha256": s["checkpoint_sha256"],
        "S_evaluated_archive_path": str(s["archive_path"]),
        "S_evaluated_archive_sha256": s["archive_sha256"],
        "R_P_empirical_smoothed_nll_bits": p_risk,
        "R_S_empirical_smoothed_nll_bits": s_risk,
        "delta_R": s_risk - p_risk,
        "S_loses_P": s_risk > p_risk,
        "L_vis_P": float(p_result["visual"]["L_vis"]),
        "L_vis_S": float(s_result["visual"]["L_vis"]),
        "delta_L_vis_S_minus_P": (
            float(s_result["visual"]["L_vis"])
            - float(p_result["visual"]["L_vis"])
        ),
        "description_bits_P": p_bits,
        "description_bits_S": s_bits,
        "delta_description_bits_S_minus_P": s_bits - p_bits,
        "omega_P_complexity_penalty_bits_nll": omega_p,
        "omega_S_complexity_penalty_bits_nll": omega_s,
        "G_C": omega_p - omega_s,
        "grad_norm_vision_mean": summary["grad_norm_vision_mean"],
        "grad_norm_vision_batch_sd": summary["grad_norm_vision_batch_sd"],
        "grad_norm_projector_mean": summary["grad_norm_projector_mean"],
        "grad_norm_projector_batch_sd": summary["grad_norm_projector_batch_sd"],
        "grad_norm_language_mean": summary["grad_norm_language_mean"],
        "grad_norm_language_batch_sd": summary["grad_norm_language_batch_sd"],
        "dot_vision_projector_mean": summary["dot_vision_projector_mean"],
        "dot_vision_projector_batch_sd": summary["dot_vision_projector_batch_sd"],
        "dot_vision_language_mean": summary["dot_vision_language_mean"],
        "dot_vision_language_batch_sd": summary["dot_vision_language_batch_sd"],
        "dot_projector_language_mean": summary["dot_projector_language_mean"],
        "dot_projector_language_batch_sd": summary["dot_projector_language_batch_sd"],
        "cos_vision_projector_mean": summary["cos_vision_projector_mean"],
        "cos_vision_projector_batch_sd": summary["cos_vision_projector_batch_sd"],
        "cos_vision_language_mean": summary["cos_vision_language_mean"],
        "cos_vision_language_batch_sd": summary["cos_vision_language_batch_sd"],
        "cos_projector_language_mean": summary["cos_projector_language_mean"],
        "cos_projector_language_batch_sd": summary["cos_projector_language_batch_sd"],
        "D": summary["D_mean"],
        "D_batch_sd": summary["D_batch_sd"],
        "D_norm": summary["D_norm_mean"],
        "D_norm_batch_sd": summary["D_norm_batch_sd"],
        "training_loss_mean": summary["training_loss_mean"],
        "training_loss_batch_sd": summary["training_loss_batch_sd"],
        "g_shared_sum_all_batches_pass": verification["all_batches_pass"],
        "g_shared_sum_max_relative_l2_error": verification[
            "maximum_gradient_sum_relative_l2_error"
        ],
        "g_shared_sum_max_absolute_error": verification[
            "maximum_gradient_sum_max_absolute_error"
        ],
        "forward_loss_max_absolute_difference": verification[
            "maximum_forward_loss_absolute_difference"
        ],
    }


def _budget_summary(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for budget in sorted({int(row["budget"]) for row in rows}):
        selected = [row for row in rows if int(row["budget"]) == budget]
        result: dict[str, Any] = {
            "budget": budget,
            "seed_count": len(selected),
            "sample_standard_deviation_definition": "n_minus_1",
        }
        for field in ("delta_R", "G_C", "D", "D_norm"):
            values = [float(row[field]) for row in selected]
            result[f"{field}_mean"] = statistics.fmean(values)
            result[f"{field}_seed_sd"] = statistics.stdev(values)
        result["S_loss_count"] = sum(bool(row["S_loses_P"]) for row in selected)
        output.append(result)
    return output


def _csv_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    excluded = set()
    return [
        {key: value for key, value in row.items() if key not in excluded}
        for row in rows
    ]


def run(ps_root: Path, output_dir: Path, device_name: str) -> dict[str, Any]:
    started = time.time()
    audited = audit_inputs(ps_root)
    device = torch.device(device_name)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("the full VLM gradient diagnostic requires CUDA")
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    stage2 = Stage2Protocol.load(STAGE2_PROTOCOL_PATH, require_frozen=True)
    artifacts = audited["artifacts"]

    checkpoint_audit = {
        config_id: _verify_checkpoint_coordinates(artifact)
        for config_id, artifact in artifacts.items()
    }
    s_ids = [
        config["config_id"]
        for config in generate_matrix()
        if config["structure"] == "S"
    ]
    first_id = s_ids[0]
    first_artifact = artifacts[first_id]
    first_model = build_candidate_model(
        first_artifact["config"], stage2, device=device
    )
    batches, data_receipt = _build_batches(
        Path(audited["run_manifest"]["artifact_root"]),
        stage2,
        first_model.processor,
    )

    detailed = {}
    pair_rows = []
    for index, s_id in enumerate(s_ids):
        s_artifact = artifacts[s_id]
        model = first_model if index == 0 else build_candidate_model(
            s_artifact["config"], stage2, device=device
        )
        decoded_coordinates = decode_mms2(
            s_artifact["archive_path"], s_artifact["config"]
        )
        if set(decoded_coordinates) != {"shared"}:
            raise ValueError(f"{s_id}: decoded S archive is not shared")
        decoded_state_sha256 = tensor_state_sha256(decoded_coordinates)
        with torch.no_grad():
            model.stage2_coordinates.coordinates["shared"].copy_(
                decoded_coordinates["shared"].to(
                    device=device, dtype=torch.float32
                )
            )
        loaded_state_sha256 = tensor_state_sha256(
            {
                "shared": model.stage2_coordinates.coordinates[
                    "shared"
                ].detach().cpu()
            }
        )
        if loaded_state_sha256 != decoded_state_sha256:
            raise AssertionError(
                f"{s_id}: in-memory coordinates differ from decoded MMS2"
            )
        diagnostic = diagnose_model(model, batches, device)
        detailed[s_id] = {
            "diagnostic_coordinate_source": (
                "the exact S adapter.mms2 archive evaluated for delta_R; decoded "
                "with the frozen development evaluator's MMS2 semantics and copied "
                "only into the in-memory diagnostic model"
            ),
            "evaluated_archive_sha256": s_artifact["archive_sha256"],
            "decoded_coordinate_state_sha256": decoded_state_sha256,
            "loaded_coordinate_state_sha256": loaded_state_sha256,
            "decoded_coordinates_match_loaded_model": True,
            "checkpoint_audit": checkpoint_audit[s_id],
            **diagnostic,
        }
        budget = int(s_artifact["config"]["budget"])
        seed = int(s_artifact["config"]["seed"])
        p_id = f"P-budget-{budget}-seed-{seed}"
        pair_rows.append(
            _pair_row(
                artifacts[p_id],
                s_artifact,
                diagnostic,
                audited["protocol"],
            )
        )
        del model, decoded_coordinates
        if device.type == "cuda":
            torch.cuda.empty_cache()
        gc.collect()

    pair_rows.sort(key=lambda row: (int(row["budget"]), int(row["seed"])))
    correlations = {
        metric: correlation_report(pair_rows, metric)
        for metric in ("D", "D_norm")
    }
    sign_predictions = {
        metric: sign_prediction_report(pair_rows, metric)
        for metric in ("D", "D_norm")
    }
    conjunctions = {
        metric: complexity_conflict_report(pair_rows, metric)
        for metric in ("D", "D_norm")
    }
    criteria = evaluate_criteria(correlations, sign_predictions, conjunctions)
    checks = {
        "strict_three_path_split_supported": True,
        "only_S_models_received_gradient_diagnostics": len(detailed) == 9,
        "all_18_P_S_checkpoints_identity_audited": len(checkpoint_audit) == 18,
        "all_S_gradient_sum_checks_pass": all(
            value["gradient_sum_verification"]["all_batches_pass"]
            for value in detailed.values()
        ),
        "all_S_split_values_identical": all(
            value["coordinate_values_identical"] for value in detailed.values()
        ),
        "all_S_split_storage_independent": all(
            value["coordinate_storage_independent"] for value in detailed.values()
        ),
        "all_S_split_graph_leaves_independent": all(
            value["coordinate_graph_leaves_independent"] for value in detailed.values()
        ),
        "all_S_diagnostic_coordinates_match_evaluated_archives": all(
            value["decoded_coordinates_match_loaded_model"]
            and value["evaluated_archive_sha256"]
            == artifacts[config_id]["archive_sha256"]
            and value["decoded_coordinate_state_sha256"]
            == value["loaded_coordinate_state_sha256"]
            for config_id, value in detailed.items()
        ),
        "development_evaluation_source_hash_verified": (
            audited["input_hashes"]["development_evaluation_source"]
            == audited["evaluation_index"]["evaluation_source_sha256"]
        ),
        "development_only": True,
        "final_fresh_confirmation_not_accessed": True,
        "no_optimizer_or_training_step_executed": True,
        "checkpoint_files_unchanged": all(
            sha256_file(artifact["checkpoint_path"])
            == artifact["checkpoint_sha256"]
            and sha256_file(artifact["archive_path"])
            == artifact["archive_sha256"]
            for artifact in artifacts.values()
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"one or more diagnostic checks failed: {checks}")
    result = {
        "schema_version": 2,
        "status": "complete",
        "analysis_role": "development_only_minimal_gradient_diagnostic",
        "scientific_question": (
            "whether conflict among vision/projector/language gradients in the "
            "same shared S coordinate system explains paired S-minus-P risk"
        ),
        "primary_outcome": {
            "name": "delta_R",
            "definition": (
                "R_S - R_P using existing development empirical smoothed "
                "conditional NLL in bits; positive means S loses P"
            ),
            "source": str(
                audited["root"]
                / "development_evaluation/aggregate_results.json"
            ),
        },
        "complexity_gain": {
            "name": "G_C",
            "definition": "Omega(kappa_P) - Omega(kappa_S)",
            "omega_definition": (
                "frozen semantic compression-bound complexity_penalty using "
                "actual MMS2 coded bits, m=1343, alpha=0.5, vocab=6400, delta=0.025"
            ),
        },
        "model_object_alignment": {
            "status": "exact",
            "risk_model_coordinate_source": "evaluated adapter.mms2 archive",
            "gradient_model_coordinate_source": "same evaluated adapter.mms2 archive",
            "model_builder": (
                "experiments.phase3_private_vs_shared_v1.adapter_runtime."
                "build_candidate_model"
            ),
            "decoder_semantics": (
                "the same float32 scale and uint8 symbol reconstruction used by "
                "the hash-bound frozen development evaluator"
            ),
            "per_model_verification": (
                "evaluated archive SHA-256 and decoded tensor-state SHA-256 are "
                "recorded; the loaded in-memory tensor-state SHA-256 must match"
            ),
        },
        "gradient_definition": {
            "coordinate_source": (
                "exact float32 coordinates decoded from each S adapter.mms2 "
                "archive evaluated for delta_R"
            ),
            "modules": list(MODULES),
            "split": (
                "three numerically identical, storage-independent, leaf "
                "CoordinateStore parameters; each existing HashedLoRALinear "
                "target is rewired by its frozen module registry group"
            ),
            "forward": (
                "one complete VLM forward for all three split paths using raw "
                "existing model training loss before gradient-accumulation scaling"
            ),
            "numerical_precision": (
                "float32 without autocast; the frozen model loss is unchanged. "
                "This avoids BF16 reduction-order error in the g_shared=sum(g_m) "
                "identity check and is not a training hyperparameter."
            ),
            "frozen_training_precision_for_context": "CUDA bfloat16 autocast",
            "D": "sum_m ||g_m - mean(g_v,g_p,g_l)||_2^2",
            "D_norm": (
                "D / (||g_v||_2^2 + ||g_p||_2^2 + ||g_l||_2^2 + 1e-12)"
            ),
            "batch_aggregation": "arithmetic mean and sample SD across 16 batches",
            "epsilon": CONFLICT_EPSILON,
        },
        "verification_tolerances": {
            "forward_loss_absolute": FORWARD_LOSS_ABSOLUTE_TOLERANCE,
            "gradient_sum_relative_l2": CHAIN_RELATIVE_L2_TOLERANCE,
            "gradient_sum_max_absolute": CHAIN_MAX_ABSOLUTE_TOLERANCE,
        },
        "input_hashes": audited["input_hashes"],
        "data_receipt": data_receipt,
        "checkpoint_inventory": {
            "P": [
                {
                    "config_id": config_id,
                    "checkpoint_path": str(artifacts[config_id]["checkpoint_path"]),
                    "checkpoint_sha256": artifacts[config_id]["checkpoint_sha256"],
                    **checkpoint_audit[config_id],
                    "gradient_diagnostic_run": False,
                }
                for config_id in sorted(
                    key for key in artifacts if key.startswith("P-")
                )
            ],
            "S": [
                {
                    "config_id": config_id,
                    "checkpoint_path": str(artifacts[config_id]["checkpoint_path"]),
                    "checkpoint_sha256": artifacts[config_id]["checkpoint_sha256"],
                    "evaluated_archive_path": str(artifacts[config_id]["archive_path"]),
                    "evaluated_archive_sha256": artifacts[config_id]["archive_sha256"],
                    "decoded_coordinate_state_sha256": detailed[config_id][
                        "decoded_coordinate_state_sha256"
                    ],
                    "loaded_coordinate_state_sha256": detailed[config_id][
                        "loaded_coordinate_state_sha256"
                    ],
                    **checkpoint_audit[config_id],
                    "gradient_diagnostic_run": True,
                }
                for config_id in sorted(
                    key for key in artifacts if key.startswith("S-")
                )
            ],
        },
        "checks": checks,
        "pairs": pair_rows,
        "budget_summary": _budget_summary(pair_rows),
        "correlations": correlations,
        "sign_predictions": sign_predictions,
        "complexity_conflict_conjunctions": conjunctions,
        "scientific_design_criteria": criteria,
        "per_model_batch_details": detailed,
        "limitations": [
            (
                "This is a nine-pair exploratory diagnostic, not independent "
                "confirmation and not evidence of causation."
            ),
            (
                "Gradients use frozen Phase 3 training batches and the existing "
                "training loss; delta_R comes from the separately exposed "
                "development evaluation."
            ),
        ],
        "runtime": {
            "device": str(device),
            "torch_version": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "elapsed_seconds": time.time() - started,
        },
    }
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    csv_path = destination / CSV_NAME
    json_path = destination / JSON_NAME
    if csv_path.exists() or json_path.exists():
        raise FileExistsError("diagnostic output already exists")
    _write_csv_atomic(csv_path, _csv_rows(pair_rows))
    result["outputs"] = {
        "csv": str(csv_path),
        "json": str(json_path),
    }
    _write_json_atomic(json_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ps-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    result = run(args.ps_root, args.output_dir, args.device)
    print(
        json.dumps(
            {
                "status": result["status"],
                "pair_count": len(result["pairs"]),
                "checks": result["checks"],
                "scientific_design_criteria": result[
                    "scientific_design_criteria"
                ],
                "outputs": result["outputs"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
