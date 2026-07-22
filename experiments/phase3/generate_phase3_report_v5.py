#!/usr/bin/env python3
"""Generate the fixed Chinese Phase 3 v5 result tables and report."""

from __future__ import annotations

import argparse
import csv
import io
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, load_json_snapshot, publish_directory,
)


MODEL_COLUMNS = (
    "model_id", "method", "mapping_root", "artifact_size_bytes", "total_description_bits",
    "n_unique_images", "empirical_robust_positive", "fixed_upper_robust_positive",
    "compression_upper_robust_positive_raw", "compression_upper_robust_positive_capped",
    "empirical_visual_semantic_loss", "fixed_upper_visual_semantic_loss",
    "compression_upper_visual_semantic_loss_raw", "compression_upper_visual_semantic_loss_capped",
    "empirical_visual_increment", "certified_visual_increment_lower",
    "positive_brier_mean", "positive_brier_dispersion", "image_robust_margin",
    "none_robust_margin", "triplet_success_rate", "lm_triplet_success_rate",
    "visual_increment_success_rate",
)


def pareto_models_v5(rows: list[dict[str, Any]]) -> list[str]:
    risks = {
        row["model_id"]: (
            float(row["compression_upper_robust_positive_raw"]),
            float(row["compression_upper_visual_semantic_loss_raw"]),
        )
        for row in rows
    }
    result = []
    for model_id, point in risks.items():
        dominated = any(
            other != model_id and candidate[0] <= point[0] and candidate[1] <= point[1]
            and (candidate[0] < point[0] or candidate[1] < point[1])
            for other, candidate in risks.items()
        )
        if not dominated:
            result.append(model_id)
    return sorted(result, key=lambda value: value.encode("utf-8"))


def _csv_bytes(columns: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=columns, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue().encode("utf-8")


def build_report_payload_v5(
    formal_dir: Path, registry_path: Path, description_audit_path: Path,
    cpu_bundle_verification_path: Path | None = None,
) -> dict[str, Any]:
    overall = load_json_snapshot(formal_dir / "overall_summary.json", root=formal_dir)
    category = load_json_snapshot(formal_dir / "category_summary.json", root=formal_dir)
    receipt = load_json_snapshot(formal_dir / "run_receipt.json", root=formal_dir)
    registry = load_json_snapshot(registry_path)
    audit = load_json_snapshot(description_audit_path)
    if (
        overall.get("metric_version") != "v5" or overall.get("simultaneous_coverage_claim") is not False
        or receipt.get("model_image_group_count") != 13450
        or receipt.get("simultaneous_coverage_claim") is not False
        or audit.get("overall_status") != "verified"
    ):
        raise ValueError("formal v5 inputs are incomplete or violate the post-hoc disclosure")
    cpu_status = "pending"
    cpu_bundle_content_hash = None
    if cpu_bundle_verification_path is not None:
        verification = load_json_snapshot(cpu_bundle_verification_path)
        if (
            verification.get("status") != "verified"
            or verification.get("run_mode") != "formal"
            or verification.get("image_group_count") != 13450
            or verification.get("shard_count") != 430
        ):
            raise ValueError("formal CPU bundle verification has not passed")
        cpu_status = "verified"
        cpu_bundle_content_hash = verification.get("bundle_content_hash")
    registry_by = {row["model_id"]: row for row in registry["models"]}
    bits_by = {row["model_id"]: row for row in audit["models"]}
    model_rows = []
    internal_bounds = []
    if (
        len(overall.get("models", [])) != 10
        or [row.get("model_id") for row in overall["models"]]
        != [row.get("model_id") for row in registry.get("models", [])]
        or [row.get("model_id") for row in audit.get("models", [])]
        != [row.get("model_id") for row in registry.get("models", [])]
    ):
        raise ValueError("formal report model order/count mismatch")
    for model in overall["models"]:
        model_id = model["model_id"]
        frozen = registry_by[model_id]
        bits = bits_by[model_id]
        if model.get("n_unique_image_groups") != 1345:
            raise ValueError(f"formal image-group count mismatch: {model_id}")
        empirical = model["empirical_risks"]
        diagnostic = model["diagnostic_means"]
        fixed = model["fixed_model_bounds"]
        compression = model["compression_bounds"]
        fixed_visual = fixed["visual_semantic_loss"]
        row = {
            "model_id": model_id, "method": frozen["method"], "mapping_root": frozen["mapping_root"],
            "artifact_size_bytes": frozen["artifact_size_bytes"],
            "total_description_bits": bits["total_description_bits"],
            "n_unique_images": model["n_unique_image_groups"],
            "empirical_robust_positive": empirical["robust_positive_brier_risk"],
            "fixed_upper_robust_positive": fixed["robust_positive_brier_risk"]["raw_upper_bound"],
            "compression_upper_robust_positive_raw": compression["robust_positive_brier_risk"]["raw_upper_bound"],
            "compression_upper_robust_positive_capped": compression["robust_positive_brier_risk"]["capped_upper_bound"],
            "empirical_visual_semantic_loss": empirical["visual_semantic_loss"],
            "fixed_upper_visual_semantic_loss": fixed_visual["raw_upper_bound"],
            "compression_upper_visual_semantic_loss_raw": compression["visual_semantic_loss"]["raw_upper_bound"],
            "compression_upper_visual_semantic_loss_capped": compression["visual_semantic_loss"]["capped_upper_bound"],
            "empirical_visual_increment": 4.0 - 8.0 * empirical["visual_semantic_loss"],
            "certified_visual_increment_lower": fixed_visual["certified_visual_increment_lower_raw"],
            "positive_brier_mean": diagnostic["positive_brier_mean"],
            "positive_brier_dispersion": diagnostic["positive_brier_dispersion"],
            "image_robust_margin": diagnostic["image_robust_margin"],
            "none_robust_margin": diagnostic["none_robust_margin"],
            "triplet_success_rate": diagnostic["triplet_success"],
            "lm_triplet_success_rate": diagnostic["lm_triplet_success"],
            "visual_increment_success_rate": diagnostic["visual_increment_success"],
        }
        if set(row) != set(MODEL_COLUMNS):
            raise AssertionError("model report schema mismatch")
        model_rows.append(row)
        internal_bounds.append({
            "model_id": model_id,
            "fixed_visual_increment_lower_raw": fixed_visual["certified_visual_increment_lower_raw"],
            "fixed_visual_increment_lower_capped": fixed_visual["certified_visual_increment_lower_capped"],
            "compression_visual_increment_lower_raw": compression["visual_semantic_loss"]["certified_visual_increment_lower_raw"],
            "compression_visual_increment_lower_capped": compression["visual_semantic_loss"]["certified_visual_increment_lower_capped"],
            "robust_fixed_nonvacuous_raw": fixed["robust_positive_brier_risk"]["raw_upper_bound"] < 2.0,
            "visual_fixed_nonvacuous_raw": fixed_visual["raw_upper_bound"] < 1.0,
        })
    category_rows = []
    for row in category["results"]:
        category_rows.append({
            "model_id": row["model_id"], "category": row["category"],
            "n_unique_images": row["n_unique_images"], "row_count": row["row_count"],
            "robust_positive_brier_risk": row["robust_positive_brier_risk"],
            "visual_semantic_loss": row["visual_semantic_loss"],
            "visual_increment": row["visual_increment"], "triplet_success_rate": row["triplet_success"],
        })
    expected_categories = {
        "replace_attribute", "replace_object", "replace_relation", "swap_atribute", "swap_object",
    }
    if len(category_rows) != 50:
        raise ValueError("formal category summary must contain 50 model-category rows")
    for model_id in registry_by:
        if {row["category"] for row in category_rows if row["model_id"] == model_id} != expected_categories:
            raise ValueError(f"formal five-category completeness mismatch: {model_id}")
    numeric_metrics = [column for column in MODEL_COLUMNS[6:] if column not in ("image_robust_margin",)]
    numeric_metrics.append("image_robust_margin")
    method_rows = []
    for method in ("M0", "M1", "M2", "M3"):
        selected = [row for row in model_rows if row["method"] == method]
        expected = 1 if method == "M1" else 3
        if len(selected) != expected:
            raise ValueError(f"method model count mismatch: {method}")
        for metric in numeric_metrics:
            values = [row[metric] for row in selected if row[metric] is not None]
            if not values:
                stats = {name: None for name in ("mean", "standard_deviation", "minimum", "maximum")}
            else:
                array = np.asarray(values, dtype=np.float64)
                stats = {
                    "mean": float(np.mean(array)), "standard_deviation": float(np.std(array, ddof=0)),
                    "minimum": float(np.min(array)), "maximum": float(np.max(array)),
                }
            method_rows.append({"method": method, "model_count": len(selected), "metric": metric, **stats})
    return {
        "schema_version": 1, "report_version": "phase3-v5", "language": "zh-CN",
        "selection_status": overall["selection_status"], "simultaneous_coverage_claim": False,
        "post_hoc_disclosure": overall["post_hoc_disclosure"],
        "models": model_rows, "categories": category_rows, "methods": method_rows,
        "visual_bound_details": internal_bounds, "pareto_models": pareto_models_v5(model_rows),
        "cpu_bundle_verification_status": cpu_status,
        "cpu_bundle_content_hash": cpu_bundle_content_hash,
    }


def render_markdown_v5(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 v5 正式实验报告", "",
        "## 统计解释", "",
        "本报告是事后分析：v5 指标可能在查看 v4 Formal 数值后确定。下列公式和失败概率分配按冻结规则计算，"
        "但不声称它们构成一次全新预注册实验的同时 95% 覆盖保证。", "",
        "结果限于 SugarCrepe++ 所代表、排除项目历史图像重叠后的条件目标分布，并以独立图片组和十个模型预先冻结为条件。", "",
        "## 模型结果", "",
        "| 模型 | 稳健正确经验风险 | 固定上界 | 压缩原始上界 | 视觉损失经验风险 | 固定上界 | 压缩原始上界 | 视觉增量 | 固定认证下界 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["models"]:
        lines.append(
            f"| {row['model_id']} | {row['empirical_robust_positive']:.9g} | {row['fixed_upper_robust_positive']:.9g} | "
            f"{row['compression_upper_robust_positive_raw']:.9g} | {row['empirical_visual_semantic_loss']:.9g} | "
            f"{row['fixed_upper_visual_semantic_loss']:.9g} | {row['compression_upper_visual_semantic_loss_raw']:.9g} | "
            f"{row['empirical_visual_increment']:.9g} | {row['certified_visual_increment_lower']:.9g} |"
        )
    lines.extend(["", "## Pareto 集", "", ", ".join(payload["pareto_models"]), "", "## 措辞边界", ""])
    for row in payload["models"]:
        if row["fixed_upper_visual_semantic_loss"] < 0.5:
            statement = "在冻结目标分布和假设条件下，名义界支持正的平均视觉语义贡献。"
        else:
            sign = "正" if row["empirical_visual_increment"] > 0 else "负" if row["empirical_visual_increment"] < 0 else "零"
            statement = f"经验视觉增量为{sign}，但当前界不足以认证其总体符号。"
        lines.append(f"- {row['model_id']}：{statement}")
    lines.extend([
        "", "未平滑 NLL 只作尾部诊断；本报告不声称解决原始 NLL 去平滑，不声称完整视觉理解、所有自然图像泛化或严格因果效应。", "",
    ])
    return "\n".join(lines)


def generate_report_v5(
    formal_dir: Path, registry: Path, audit: Path, cpu_bundle_verification: Path,
    output_dir: Path,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        payload = build_report_payload_v5(formal_dir, registry, audit, cpu_bundle_verification)
        atomic_write_bytes(temporary / "phase3_v5_model_results.csv", _csv_bytes(MODEL_COLUMNS, payload["models"]), overwrite=False)
        category_columns = tuple(payload["categories"][0])
        method_columns = tuple(payload["methods"][0])
        atomic_write_bytes(temporary / "phase3_v5_category_results.csv", _csv_bytes(category_columns, payload["categories"]), overwrite=False)
        atomic_write_bytes(temporary / "phase3_v5_method_summary.csv", _csv_bytes(method_columns, payload["methods"]), overwrite=False)
        atomic_write_json(temporary / "phase3_v5_report.json", payload, overwrite=False)
        atomic_write_bytes(temporary / "phase3_v5_report.md", render_markdown_v5(payload).encode("utf-8"), overwrite=False)
        publish_directory(temporary, output_dir)
        return payload
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-dir", type=Path, required=True)
    parser.add_argument("--expected-registry", type=Path, required=True)
    parser.add_argument("--description-bits-audit", type=Path, required=True)
    parser.add_argument("--cpu-bundle-verification", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generate_report_v5(
        args.formal_dir, args.expected_registry, args.description_bits_audit,
        args.cpu_bundle_verification, args.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
