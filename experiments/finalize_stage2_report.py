#!/usr/bin/env python3
"""Verify final Stage 2 artifacts and write the machine/human result reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from experiments.stage2_protocol import DEFAULT_FROZEN, Stage2Protocol, sha256_file, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--formal-summary", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path, required=True)
    parser.add_argument("--dataset-verification", type=Path, required=True)
    parser.add_argument("--dataset-replay", type=Path)
    parser.add_argument("--runtime-integrity", type=Path)
    parser.add_argument(
        "--v1-report",
        type=Path,
        default=REPO_ROOT / "experiments/runs/stage2/final/stage2_final_report.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def markdown_report(payload: dict) -> str:
    is_v2 = payload.get("schema_version") == 2
    verified_count = payload["dataset_verification"].get(
        "verified_draws", payload["dataset_verification"].get("verified_images")
    )
    lines = [
        "# Stage 2 joint-compression experiment report",
        "",
        f"Protocol: `{payload['protocol']['protocol_id']}` (`{payload['protocol']['protocol_sha256']}`)",
        "",
        "All ten predeclared formal models completed. The table reports the raw, unclipped compression bound; no mapping root was selected post hoc.",
        "",
        "| Model | Root | Train risk (bits) | Validation risk (bits) | Adapter bits | Penalty (bits) | Raw bound (bits) | Random margin (bits) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["formal_results"]:
        lines.append(
            f"| {row['model_group']} | {row['mapping_root'] if row['mapping_root'] is not None else '—'} "
            f"| {row['decoded_training_risk_bits']:.6f} | {row['decoded_validation_risk_bits']:.6f} "
            f"| {row['adapter_bits']} | {row['penalty_bits']:.6f} | {row['raw_bound_bits']:.6f} "
            f"| {row['nonvacuous_margin_bits']:.6f} |"
        )
    lines += ["", "## Predeclared paired differences", "", "| Root | Vision cost T (bits) | Shared gain G (bits) |", "| ---: | ---: | ---: |"]
    for row in payload["paired_differences"]:
        lines.append(f"| {row['mapping_root']} | {row['vision_cost_T_bits']:.6f} | {row['shared_gain_G_bits']:.6f} |")
    means = payload["descriptive_means"]
    lines.append(f"| mean | {means['vision_cost_T_bits']:.6f} | {means['shared_gain_G_bits']:.6f} |")
    lines += [
        "",
        "## Integrity and scope",
        "",
        f"- Confirmation data verification: `{payload['dataset_verification']['status']}` over {verified_count} {'independent draws' if is_v2 else 'images'}.",
        f"- Visual diagnostics: seven models, secondary/descriptive only; see `{payload['diagnostics_path']}`.",
        f"- Artifact manifest: `{payload['artifact_manifest_path']}`.",
        (
            "- Certificate scope: the finite uniform empirical distribution over the frozen v2 eligible-image catalog; this is not a real-world-distribution certificate."
            if is_v2
            else "- The v1 values are preserved as exploratory computed compression-bound values, not a strict independent-sample certificate."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    if protocol.payload.get("schema_version") == 2:
        protocol.verify_runtime_integrity()
    summary = json.loads(args.formal_summary.read_text(encoding="utf-8"))
    diagnostics = json.loads(args.diagnostics.read_text(encoding="utf-8"))
    dataset_verification = json.loads(args.dataset_verification.read_text(encoding="utf-8"))
    is_v2 = protocol.payload.get("schema_version") == 2
    dataset_replay = (
        json.loads(args.dataset_replay.read_text(encoding="utf-8"))
        if args.dataset_replay
        else None
    )
    runtime_integrity = (
        json.loads(args.runtime_integrity.read_text(encoding="utf-8"))
        if args.runtime_integrity
        else None
    )
    reference = protocol.reference()
    if any(item.get("protocol") != reference for item in (summary, diagnostics, dataset_verification)):
        raise ValueError("final report input provenance differs from frozen protocol")
    if summary.get("formal_model_count") != 10 or len(diagnostics.get("models", [])) != 7:
        raise ValueError("final formal or diagnostic model count is incomplete")
    if dataset_verification.get("status") != "passed":
        raise ValueError("confirmation dataset did not pass independent verification")
    if is_v2:
        if args.dataset_replay is None or args.runtime_integrity is None:
            raise ValueError("v2 finalization requires dataset replay and runtime-integrity receipts")
        if any(
            item is None
            or item.get("status") != "passed"
            or item.get("protocol") != reference
            for item in (dataset_replay, runtime_integrity)
        ):
            raise ValueError("v2 replay or runtime-integrity receipt is not a protocol-bound pass")
        if runtime_integrity.get("runtime_integrity", {}).get("status") != "passed":
            raise ValueError("v2 nested runtime-integrity audit is not a pass")
    failures = list(args.formal_root.rglob("failure_receipt.json")) + list(args.formal_root.glob("pipeline_failure.json"))
    if failures:
        raise ValueError(f"formal output contains failure receipts: {failures}")
    progress = json.loads((args.formal_root / "pipeline_progress.json").read_text())
    if progress.get("status") != "complete" or progress.get("completed_runs") != 10:
        raise ValueError("formal pipeline completion receipt is incomplete")
    formal_rows = []
    for bound in summary["bounds"]:
        formal_rows.append({
            "model_group": bound["model_group"],
            "mapping_root": bound["mapping_root"],
            "unquantized_training_risk_bits": bound["risk"]["unquantized_training_bits"],
            "decoded_training_risk_bits": bound["risk"]["decoded_training_bits"],
            "decoded_validation_risk_bits": bound["risk"]["decoded_validation_bits"],
            "quantization_increase_bits": bound["risk"]["quantization_increase_bits"],
            "observed_generalization_gap_bits": bound["risk"]["observed_generalization_gap_bits"],
            "adapter_bits": bound["complexity"]["adapter_bits"],
            "description_complexity_nats": bound["complexity"]["description_complexity_nats"],
            "penalty_bits": bound["bound"]["generalization_penalty_bits"],
            "raw_bound_bits": bound["bound"]["raw_compression_upper_bound_bits"],
            "nonvacuous_margin_bits": bound["bound"]["nonvacuous_margin_bits"],
            "beats_random_baseline": bound["bound"]["beats_random_baseline"],
            "bound_sha256": bound["sha256"],
        })
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = args.output_dir / "stage2_final_report.json"
    report_md_path = args.output_dir / "stage2_final_report.md"
    manifest_path = args.output_dir / "stage2_artifact_manifest.json"
    comparison_json_path = args.output_dir / "stage2_v1_v2_comparison.json"
    comparison_md_path = args.output_dir / "stage2_v1_v2_comparison.md"
    outputs = [report_json_path, report_md_path, manifest_path]
    if is_v2:
        outputs.extend((comparison_json_path, comparison_md_path))
    if any(path.exists() for path in outputs):
        raise FileExistsError("one or more final report outputs already exist")
    tracked_inputs = {
        args.protocol, args.formal_summary, args.diagnostics, args.dataset_verification,
        args.formal_root / "pipeline_plan.json", args.formal_root / "pipeline_progress.json",
    }
    if args.dataset_replay:
        tracked_inputs.add(args.dataset_replay)
    if args.runtime_integrity:
        tracked_inputs.add(args.runtime_integrity)
    if is_v2:
        tracked_inputs.add(args.v1_report)
    tracked_inputs.update(path for path in args.formal_root.rglob("*") if path.is_file())
    tracked_inputs.update(
        path for path in args.dataset_verification.parent.rglob("*") if path.is_file()
    )
    artifacts = [
        {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(tracked_inputs)
    ]
    manifest = {
        "schema_version": 2 if is_v2 else 1,
        "protocol": reference,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    write_json_atomic(manifest_path, manifest)
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()
    tags = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.splitlines()
    report = {
        "schema_version": 2 if is_v2 else 1,
        "status": "complete",
        "protocol": reference,
        "git_commit": git_commit,
        "git_tags_at_report_commit": tags,
        "formal_results": formal_rows,
        "paired_differences": summary["paired_differences"],
        "descriptive_means": summary["descriptive_means"],
        "dataset_verification": dataset_verification,
        "dataset_replay": dataset_replay,
        "runtime_integrity": runtime_integrity,
        "diagnostics_path": str(args.diagnostics.resolve()),
        "diagnostics_sha256": sha256_file(args.diagnostics),
        "artifact_manifest_path": str(manifest_path.resolve()),
        "artifact_manifest_sha256": sha256_file(manifest_path),
        "best_mapping_root_selected": False,
        "primary_bound": "raw unclipped compression upper bound",
        "certificate": {
            "status": "strict_finite_catalog_certificate" if is_v2 else "exploratory",
            "scope": (
                protocol.payload["interpretation"]["certificate_scope"]
                if is_v2
                else "not established under the strict independent-sample premise"
            ),
            "real_world_distribution": False,
        },
    }
    write_json_atomic(report_json_path, report)
    temporary = report_md_path.with_name(report_md_path.name + ".tmp")
    temporary.write_text(markdown_report(report), encoding="utf-8")
    temporary.replace(report_md_path)
    result_paths = {
        "report_json": str(report_json_path), "report_json_sha256": sha256_file(report_json_path),
        "report_markdown": str(report_md_path), "report_markdown_sha256": sha256_file(report_md_path),
        "artifact_manifest": str(manifest_path), "artifact_manifest_sha256": sha256_file(manifest_path),
    }
    if is_v2:
        v1 = json.loads(args.v1_report.read_text(encoding="utf-8"))
        v1_rows = {
            (row["model_group"], row["mapping_root"]): row
            for row in v1["formal_results"]
        }
        comparison_rows = []
        for row in formal_rows:
            key = row["model_group"], row["mapping_root"]
            previous = v1_rows.get(key)
            if previous is None:
                raise ValueError(f"v1 report lacks comparison model {key}")
            comparison_rows.append(
                {
                    "model_group": key[0],
                    "mapping_root": key[1],
                    "v1_decoded_training_risk_bits": previous["decoded_training_risk_bits"],
                    "v2_decoded_training_risk_bits": row["decoded_training_risk_bits"],
                    "v2_minus_v1_training_risk_bits": row["decoded_training_risk_bits"]
                    - previous["decoded_training_risk_bits"],
                    "v1_decoded_validation_risk_bits": previous["decoded_validation_risk_bits"],
                    "v2_decoded_validation_risk_bits": row["decoded_validation_risk_bits"],
                    "v2_minus_v1_validation_risk_bits": row["decoded_validation_risk_bits"]
                    - previous["decoded_validation_risk_bits"],
                    "v1_raw_bound_bits": previous["raw_bound_bits"],
                    "v2_raw_bound_bits": row["raw_bound_bits"],
                    "v2_minus_v1_raw_bound_bits": row["raw_bound_bits"]
                    - previous["raw_bound_bits"],
                    "adapter_bits_unchanged": row["adapter_bits"] == previous["adapter_bits"],
                }
            )
        comparison = {
            "schema_version": 1,
            "status": "complete",
            "v1": {
                "protocol": v1["protocol"],
                "report_path": str(args.v1_report.resolve()),
                "report_sha256": sha256_file(args.v1_report),
                "certificate_status": "exploratory_computed_values",
                "sampling": "adaptive without-replacement selection; strict independence not established",
            },
            "v2": {
                "protocol": reference,
                "report_path": str(report_json_path.resolve()),
                "report_sha256": sha256_file(report_json_path),
                "certificate_status": "strict_finite_catalog_certificate",
                "sampling": "independent domain-separated with-replacement draws from a fixed finite catalog",
                "scope": protocol.payload["interpretation"]["certificate_scope"],
            },
            "model_rows": comparison_rows,
            "interpretation": "Risk differences combine different independently generated confirmation draws; they are descriptive v1/v2 comparisons, not paired-sample effects.",
        }
        write_json_atomic(comparison_json_path, comparison)
        comparison_lines = [
            "# Stage 2 v1/v2 comparison",
            "",
            "v1 is retained as exploratory computed compression-bound values. v2 uses independent with-replacement draws from a fixed finite eligible-image catalog and supports strict certificate language only for that catalog distribution.",
            "",
            "| Model | Root | v2-v1 train risk | v2-v1 validation risk | v2-v1 raw bound | Adapter bits unchanged |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
        for row in comparison_rows:
            comparison_lines.append(
                f"| {row['model_group']} | {row['mapping_root'] if row['mapping_root'] is not None else '—'} "
                f"| {row['v2_minus_v1_training_risk_bits']:.6f} "
                f"| {row['v2_minus_v1_validation_risk_bits']:.6f} "
                f"| {row['v2_minus_v1_raw_bound_bits']:.6f} "
                f"| {row['adapter_bits_unchanged']} |"
            )
        comparison_lines += [
            "",
            "These differences are descriptive because v1 and v2 use different confirmation samples; they are not paired-sample estimates.",
            "",
        ]
        temporary = comparison_md_path.with_name(comparison_md_path.name + ".tmp")
        temporary.write_text("\n".join(comparison_lines), encoding="utf-8")
        temporary.replace(comparison_md_path)
        result_paths.update(
            {
                "comparison_json": str(comparison_json_path),
                "comparison_json_sha256": sha256_file(comparison_json_path),
                "comparison_markdown": str(comparison_md_path),
                "comparison_markdown_sha256": sha256_file(comparison_md_path),
            }
        )
    print(json.dumps(result_paths, indent=2))


if __name__ == "__main__":
    main()
