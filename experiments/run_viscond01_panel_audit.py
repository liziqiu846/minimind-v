#!/usr/bin/env python3
"""Audit and extract the frozen MMStar panel without model inference."""

from __future__ import annotations

import argparse
from pathlib import Path

from transformers import AutoTokenizer

from experiments.phase3.stage2_adapter_loader import verify_stage2_source_integrity
from experiments.phase3_v6.scoring.common import atomic_write_json, sha256_file
from experiments.viscond01 import audit_panel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"audit output is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol = verify_stage2_source_integrity(
        str(
            (
                Path(__file__).resolve().parents[1]
                / "experiments/stage2_protocol_v2.json"
            ).resolve()
        )
    )
    tokenizer = AutoTokenizer.from_pretrained(
        protocol.asset_path("tokenizer"),
        local_files_only=True,
    )
    manifest, audit = audit_panel(
        args.parquet,
        args.image_root,
        tokenizer=tokenizer,
    )
    manifest_path = output / "panel_manifest.json"
    audit_path = output / "panel_audit.json"
    atomic_write_json(manifest_path, manifest)
    audit["outputs"] = {
        "panel_manifest": {
            "path": str(manifest_path),
            "sha256": sha256_file(manifest_path),
        }
    }
    atomic_write_json(audit_path, audit)
    print(
        f"status={audit['status']} rows={audit['panel']['row_count']} "
        f"image_groups={audit['panel']['unique_normalized_pixel_groups']} "
        f"max_tokens={audit['panel']['maximum_input_length_unpadded']} "
        f"manifest_sha256={sha256_file(manifest_path)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
