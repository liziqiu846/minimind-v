#!/usr/bin/env python3
"""Run the immutable COMP-01 What’sUp panel eligibility audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.comp01_whatsup import (
    audit_panel,
    canonical_json_bytes,
    write_json_atomic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-root", type=Path, required=True)
    parser.add_argument("--train-parquet", type=Path, required=True)
    parser.add_argument("--paper-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"audit output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    manifest, audit = audit_panel(
        panel_root=args.panel_root,
        train_path=args.train_parquet,
        paper_path=args.paper_pdf,
    )
    manifest_path = output / "panel_manifest.json"
    audit_path = output / "panel_audit.json"
    write_json_atomic(manifest_path, manifest)
    audit["panel_manifest"] = {
        "path": str(manifest_path),
        "sha256": __import__("hashlib").sha256(
            canonical_json_bytes(manifest) + b"\n"
        ).hexdigest(),
    }
    write_json_atomic(audit_path, audit)
    print(
        f"status={audit['status']} images={len(manifest['images'])} "
        f"pairs={len(manifest['pairs'])} audit={audit_path}",
        flush=True,
    )


if __name__ == "__main__":
    main()
