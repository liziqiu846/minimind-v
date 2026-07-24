#!/usr/bin/env python3
"""Audit coordinate counts, symbol entropy, and complete encoded description bits."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.phase3_v6.scoring.common import atomic_write_json


MMS2_HEADER_BITS = 17 * 8
UNCOMPRESSED_GROUP_METADATA_BITS = 8 * 8


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def external_selection_bits(candidate_family_size: int) -> int:
    if isinstance(candidate_family_size, bool) or int(candidate_family_size) <= 0:
        raise ValueError("candidate_family_size must be a positive integer")
    size = int(candidate_family_size)
    return 0 if size == 1 else int(math.ceil(math.log2(size)))


def estimated_entropy_bits(histogram: Mapping[str, Any]) -> float:
    counts = [int(value) for value in histogram.values()]
    if not counts or any(value < 0 for value in counts) or sum(counts) <= 0:
        raise ValueError("symbol histogram must contain non-negative counts")
    total = sum(counts)
    return math.fsum(
        -count * math.log2(count / total) for count in counts if count
    )


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _group_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = summary.get("coordinate_groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("adapter summary lacks coordinate_groups")
    output = []
    for group in groups:
        if not isinstance(group, Mapping):
            raise ValueError("coordinate group is not an object")
        name = group.get("name")
        dimension = group.get("dimension")
        histogram = group.get("symbol_histogram")
        if (
            not isinstance(name, str)
            or not name
            or isinstance(dimension, bool)
            or int(dimension) <= 0
            or not isinstance(histogram, Mapping)
        ):
            raise ValueError("coordinate group metadata is incomplete")
        if sum(int(value) for value in histogram.values()) != int(dimension):
            raise ValueError(f"symbol histogram count mismatch for {name}")
        output.append(
            {
                "name": name,
                "coordinate_count": int(dimension),
                "symbol_histogram": dict(histogram),
                "estimated_entropy_bits": estimated_entropy_bits(histogram),
            }
        )
    return output


def audit_complexity(
    registry: Mapping[str, Any],
    artifact_root: Path,
    *,
    candidate_family_size: int,
    external_hyperparameter_bits: int,
) -> dict[str, Any]:
    models = registry.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("registry lacks a non-empty models list")
    if len(models) != int(candidate_family_size):
        raise ValueError(
            "registry model count differs from predeclared candidate family size"
        )
    if (
        isinstance(external_hyperparameter_bits, bool)
        or int(external_hyperparameter_bits) < 0
    ):
        raise ValueError("external_hyperparameter_bits must be non-negative")
    selection_bits = external_selection_bits(candidate_family_size)
    hyperparameter_bits = int(external_hyperparameter_bits)
    root = artifact_root.resolve()
    results = []
    for model in models:
        relative = Path(str(model["artifact_relative_path"]))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("artifact path must be relative and contained")
        archive = root / relative
        if not archive.is_file() or archive.is_symlink():
            raise FileNotFoundError(archive)
        archive_bytes = archive.stat().st_size
        if archive_bytes != int(model["artifact_size_bytes"]):
            raise ValueError(f"archive size mismatch for {model['model_id']}")
        digest = sha256_file(archive)
        if digest != model["artifact_sha256"]:
            raise ValueError(f"archive SHA-256 mismatch for {model['model_id']}")
        summary_path = archive.parent / "adapter_summary.json"
        summary = _load_json(summary_path)
        if (
            summary.get("archive_sha256") != digest
            or int(summary.get("archive_bytes", -1)) != archive_bytes
            or summary.get("codec") != "zlib-9"
            or summary.get("format") != "MMS2"
            or int(summary.get("format_version", -1)) != 1
        ):
            raise ValueError(f"adapter summary mismatch for {model['model_id']}")
        groups = _group_rows(summary)
        method = str(model["method"])
        archive_bits = archive_bytes * 8
        total_bits = archive_bits + selection_bits + hyperparameter_bits
        row: dict[str, Any] = {
            "model_id": model["model_id"],
            "method": method,
            "mapping_root": model.get("mapping_root"),
            "coordinate_groups": groups,
            "coordinate_count_total": sum(
                int(group["coordinate_count"]) for group in groups
            ),
            "estimated_entropy_bits_total": math.fsum(
                float(group["estimated_entropy_bits"]) for group in groups
            ),
            "archive_bits": archive_bits,
            "actual_encoded_bits_compat": archive_bits,
            "archive_header_bits_included_in_archive_bits": MMS2_HEADER_BITS,
            "uncompressed_group_metadata_bits_before_joint_zlib": (
                len(groups) * UNCOMPRESSED_GROUP_METADATA_BITS
            ),
            "actual_encoded_bits_are_not_module_separable": True,
            "external_selection_bits": selection_bits,
            "external_selection_bits_rule": (
                "ceil(log2(candidate_family_size))"
            ),
            "external_hyperparameter_bits": hyperparameter_bits,
            "mms2_header_recounted_as_external_metadata": False,
            "total_description_bits": total_bits,
            "total_description_bits_definition": (
                "archive_bits + external_selection_bits + "
                "external_hyperparameter_bits"
            ),
            "legacy_v5_compatibility": (
                {
                    "candidate_id_bits": 4,
                    "total_description_bits": archive_bits + 4,
                    "definition": "complete MMS2 file bits plus four candidate-ID bits",
                }
                if int(candidate_family_size) == 10
                else None
            ),
        }
        by_name = {group["name"]: group for group in groups}
        if method == "M2":
            if set(by_name) != {"vision", "projector", "language"}:
                raise ValueError("M2 coordinate group names are invalid")
            for name in ("vision", "projector", "language"):
                row[f"{name}_coordinate_count"] = by_name[name][
                    "coordinate_count"
                ]
                row[f"{name}_entropy_bits"] = by_name[name][
                    "estimated_entropy_bits"
                ]
        elif method == "M3":
            if set(by_name) != {"shared"}:
                raise ValueError("M3 coordinate group names are invalid")
            row["shared_coordinate_count"] = by_name["shared"][
                "coordinate_count"
            ]
            row["shared_entropy_bits"] = by_name["shared"][
                "estimated_entropy_bits"
            ]
            row["routing_or_projection_metadata_bits"] = 0
            row["routing_or_projection_metadata_note"] = (
                "the frozen decoder reconstructs routing from the model-group "
                "and mapping-root IDs already stored in the MMS2 archive header"
            )
        if "description_bits" in model and int(model["description_bits"]) != archive_bits:
            raise ValueError(
                f"registry description_bits is not complete archive bits for "
                f"{model['model_id']}"
            )
        results.append(row)
    return {
        "schema_version": 1,
        "audit_type": "phase3_risk_v1_complexity_breakdown",
        "comparison_claim": "equal_coordinate_budget_not_equal_description_length",
        "candidate_family_size": int(candidate_family_size),
        "external_selection_bits": selection_bits,
        "external_hyperparameter_bits": hyperparameter_bits,
        "estimated_entropy_definition": (
            "zero-order plug-in Shannon length: -sum(count*log2(count/n))"
        ),
        "actual_codec": "MMS2 v1 whole-body zlib-9",
        "models": results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--candidate-family-size", type=int, required=True)
    parser.add_argument("--external-hyperparameter-bits", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit_complexity(
        _load_json(args.registry),
        args.artifact_root,
        candidate_family_size=args.candidate_family_size,
        external_hyperparameter_bits=args.external_hyperparameter_bits,
    )
    atomic_write_json(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
