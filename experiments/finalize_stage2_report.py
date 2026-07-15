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
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def markdown_report(payload: dict) -> str:
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
        f"- Confirmation leakage verification: `{payload['dataset_verification']['status']}` over {payload['dataset_verification']['verified_images']} images.",
        f"- Visual diagnostics: seven models, secondary/descriptive only; see `{payload['diagnostics_path']}`.",
        f"- Artifact manifest: `{payload['artifact_manifest_path']}`.",
        "- The claims are limited to the frozen hypotheses, source distribution, compression code, and paired mappings in the protocol.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    protocol = Stage2Protocol.load(args.protocol, require_frozen=True)
    summary = json.loads(args.formal_summary.read_text(encoding="utf-8"))
    diagnostics = json.loads(args.diagnostics.read_text(encoding="utf-8"))
    dataset_verification = json.loads(args.dataset_verification.read_text(encoding="utf-8"))
    reference = protocol.reference()
    if any(item.get("protocol") != reference for item in (summary, diagnostics, dataset_verification)):
        raise ValueError("final report input provenance differs from frozen protocol")
    if summary.get("formal_model_count") != 10 or len(diagnostics.get("models", [])) != 7:
        raise ValueError("final formal or diagnostic model count is incomplete")
    if dataset_verification.get("status") != "passed":
        raise ValueError("confirmation dataset did not pass independent verification")
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
    if any(path.exists() for path in (report_json_path, report_md_path, manifest_path)):
        raise FileExistsError("one or more final report outputs already exist")
    tracked_inputs = {
        args.protocol, args.formal_summary, args.diagnostics, args.dataset_verification,
        args.formal_root / "pipeline_plan.json", args.formal_root / "pipeline_progress.json",
    }
    tracked_inputs.update(path for path in args.formal_root.rglob("*") if path.is_file())
    tracked_inputs.update(
        path for path in args.dataset_verification.parent.rglob("*") if path.is_file()
    )
    artifacts = [
        {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(tracked_inputs)
    ]
    manifest = {"schema_version": 1, "protocol": reference, "artifact_count": len(artifacts), "artifacts": artifacts}
    write_json_atomic(manifest_path, manifest)
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()
    tags = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.splitlines()
    report = {
        "schema_version": 1,
        "status": "complete",
        "protocol": reference,
        "git_commit": git_commit,
        "git_tags_at_report_commit": tags,
        "formal_results": formal_rows,
        "paired_differences": summary["paired_differences"],
        "descriptive_means": summary["descriptive_means"],
        "dataset_verification": dataset_verification,
        "diagnostics_path": str(args.diagnostics.resolve()),
        "diagnostics_sha256": sha256_file(args.diagnostics),
        "artifact_manifest_path": str(manifest_path.resolve()),
        "artifact_manifest_sha256": sha256_file(manifest_path),
        "best_mapping_root_selected": False,
        "primary_bound": "raw unclipped compression upper bound",
    }
    write_json_atomic(report_json_path, report)
    temporary = report_md_path.with_name(report_md_path.name + ".tmp")
    temporary.write_text(markdown_report(report), encoding="utf-8")
    temporary.replace(report_md_path)
    print(json.dumps({
        "report_json": str(report_json_path), "report_json_sha256": sha256_file(report_json_path),
        "report_markdown": str(report_md_path), "report_markdown_sha256": sha256_file(report_md_path),
        "artifact_manifest": str(manifest_path), "artifact_manifest_sha256": sha256_file(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
