#!/usr/bin/env python3
"""Prepare frozen SugarCrepe++ rows, phase3-v1 split, image manifests, and diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import (
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_jsonl,
    canonical_json_bytes,
    publish_directory,
    sha256_bytes,
    snapshot_file,
    validate_disjoint_roots,
    write_sha256_sidecar,
)
from experiments.phase3.datasets.sugarcrepe_pp import (
    REPO_ID, REVISION, SOURCES, SPLIT,
    canonical_row_commitment, canonicalize_rows, parse_source, row_index,
)
from experiments.phase3.status import Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output


PHASH_SPEC_ID = "imagehash-4.3.2_pillow-11.3.0_numpy-1.26.4_scipy-1.15.3_h8_f4_exif-rgb"


def split_name(filename: str) -> str:
    digest = hashlib.sha256(("phase3-v1|" + filename).encode("utf-8")).hexdigest()
    return "pilot" if int(digest[:16], 16) % 10 == 0 else "formal"


def _record(path: Path, root: Path, logical_name: str, row_count: int | None) -> dict[str, Any]:
    payload = snapshot_file(path, root=root)
    return {
        "logical_name": logical_name,
        "relative_path": path.relative_to(root).as_posix(),
        "size_bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "row_count": row_count,
    }


def _package_versions() -> dict[str, str]:
    import PIL
    import imagehash
    import numpy
    import scipy

    versions = {
        "ImageHash": imagehash.__version__,
        "Pillow": PIL.__version__,
        "NumPy": numpy.__version__,
        "SciPy": scipy.__version__,
    }
    expected = {"ImageHash": "4.3.2", "Pillow": "11.3.0", "NumPy": "1.26.4", "SciPy": "1.15.3"}
    if versions != expected:
        raise Phase3Blocked("blocked_phash_environment_mismatch", str(versions))
    return versions


def _image_manifest(filenames: list[str], coco_root: Path) -> list[dict[str, Any]]:
    import imagehash
    from dataset.stage2_dataset import normalized_image

    rows = []
    for filename in filenames:
        image_id = int(filename[:-4], 10)
        path = coco_root / filename
        base = {
            "coco_image_id": image_id,
            "error_code": None,
            "exists": True,
            "filename": filename,
            "perceptual_hash": None,
            "sha256": None,
            "size_bytes": None,
            "status": "ready",
        }
        if path.is_symlink():
            base.update(error_code="unsafe_path", status="unsafe_path")
            rows.append(base)
            continue
        if not path.exists():
            base.update(error_code="missing", exists=False, status="missing")
            rows.append(base)
            continue
        try:
            payload = snapshot_file(path, root=coco_root)
        except PermissionError:
            base.update(error_code="unreadable", status="unreadable")
            rows.append(base)
            continue
        except (OSError, ValueError):
            base.update(error_code="unsafe_path", status="unsafe_path")
            rows.append(base)
            continue
        base["size_bytes"] = len(payload)
        base["sha256"] = sha256_bytes(payload)
        try:
            value = imagehash.phash(normalized_image(payload), hash_size=8, highfreq_factor=4)
            rendered = str(value)
            if len(rendered) != 16 or rendered.lower() != rendered:
                raise ValueError("pHash is not 16 lowercase hex digits")
            base["perceptual_hash"] = rendered
        except Exception:
            base.update(error_code="decode_failed", status="decode_failed")
        rows.append(base)
    return rows


def _degenerates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output = []
    type_counts: Counter[str] = Counter()
    for index, row in enumerate(rows):
        types = []
        if row["caption"] == row["caption2"]:
            types.append("positive_pair_equal")
        if row["caption"] == row["negative_caption"]:
            types.append("pos1_equals_negative")
        if row["caption2"] == row["negative_caption"]:
            types.append("pos2_equals_negative")
        if types:
            type_counts.update(types)
            output.append(
                {
                    "row_index": index,
                    "row_key": row["row_key"],
                    "category": row["category"],
                    "filename": row["filename"],
                    "degenerate_types": types,
                }
            )
    return {
        "schema_version": 1,
        "degenerate_row_count": len(output),
        "affected_image_group_count": len({row["filename"] for row in output}),
        "type_counts": dict(sorted(type_counts.items())),
        "rows": output,
    }


def _token_preflight(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    from transformers import AutoTokenizer
    from experiments.stage2_protocol import Stage2Protocol
    from experiments.phase3.caption_template import CaptionRecordError, assert_correct_none_identical, build_caption_record

    protocol = Stage2Protocol.load(Path(__file__).resolve().parents[1] / "stage2_protocol_v2.json")
    tokenizer = AutoTokenizer.from_pretrained(protocol.asset_path("tokenizer"), local_files_only=True)
    failures = []
    overlength = []
    roles = (("pos1", "caption"), ("pos2", "caption2"), ("negative", "negative_caption"))
    for row_index_value, row in enumerate(rows):
        for role, key in roles:
            for mode in ("vlm", "lm_only"):
                try:
                    record = build_caption_record(tokenizer, row[key], template_mode=mode)
                    if mode == "vlm":
                        duplicate = build_caption_record(tokenizer, row[key], template_mode=mode)
                        assert_correct_none_identical(record, duplicate)
                except Exception as error:
                    reason_code = getattr(error, "reason_code", "input_invariant")
                    item = {
                        "row_index": row_index_value,
                        "row_key": row["row_key"],
                        "model_mode": mode,
                        "caption_role": role,
                        "full_length": getattr(error, "full_length", None),
                        "max_length": 450,
                        "reason_code": reason_code,
                        "detail": f"{type(error).__name__}: {error}",
                    }
                    failures.append(item)
                    if isinstance(error, CaptionRecordError) and error.reason_code == "overlength":
                        overlength.append(dict(item))
    order = lambda item: (item["row_index"], item["model_mode"], item["caption_role"], item["reason_code"])
    return (
        {"schema_version": 1, "failure_count": len(overlength), "failures": sorted(overlength, key=order)},
        {"schema_version": 1, "failure_count": len(failures), "failures": sorted(failures, key=order)},
    )


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    validate_disjoint_roots(
        input_roots=[args.coco_root] + ([args.hf_cache_dir] if args.hf_cache_dir else []),
        output_roots=[args.output_dir, args.status_output.parent],
        forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parent, Path(__file__).resolve().parents[2] / "tests"],
    )
    if args.output_dir.exists():
        raise Phase3HardFailure("output_exists", str(args.output_dir))
    versions = _package_versions()
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.", dir=args.output_dir.parent))
    blocked_code = None
    hard_code = None
    try:
        from huggingface_hub import hf_hub_download

        all_rows = []
        source_records = []
        source_download_dir = temporary / ".hf_source_download"
        for category, repository_path, expected_count, expected_sha in SOURCES:
            try:
                local = Path(
                    hf_hub_download(
                        repo_id=REPO_ID,
                        repo_type="dataset",
                        filename=repository_path,
                        revision=REVISION,
                        cache_dir=str(args.hf_cache_dir) if args.hf_cache_dir else None,
                        local_dir=str(source_download_dir),
                        local_files_only=args.offline,
                    )
                )
            except Exception:
                raise Phase3Blocked(
                    "blocked_sugarcrepe_source_unavailable",
                    f"{category}: frozen SugarCrepe++ source is unavailable",
                ) from None
            payload = snapshot_file(local)
            actual_sha = sha256_bytes(payload)
            if actual_sha != expected_sha:
                raise Phase3HardFailure("source_sha_mismatch", f"{category}:{actual_sha}")
            parsed = parse_source(payload, category, expected_count)
            all_rows.extend(parsed)
            source_records.append(
                {
                    "config": category,
                    "repository_relative_path": repository_path,
                    "row_count": len(parsed),
                    "size_bytes": len(payload),
                    "sha256": actual_sha,
                }
            )
        if source_download_dir.exists():
            shutil.rmtree(source_download_dir)
        rows = canonicalize_rows(all_rows)
        filenames = sorted({row["filename"] for row in rows}, key=lambda value: value.encode("utf-8"))
        pilot_names = [name for name in filenames if split_name(name) == "pilot"]
        formal_names = [name for name in filenames if split_name(name) == "formal"]
        if (len(rows), len(filenames), len(pilot_names), len(formal_names)) != (4757, 1542, 153, 1389):
            raise Phase3HardFailure("frozen_count_mismatch", str((len(rows), len(filenames), len(pilot_names), len(formal_names))))
        index_rows = row_index(rows)
        commitment = canonical_row_commitment(index_rows)
        pilot_set, formal_set = set(pilot_names), set(formal_names)
        pilot_rows = [row for row in rows if row["filename"] in pilot_set]
        formal_rows = [row for row in rows if row["filename"] in formal_set]
        atomic_write_jsonl(temporary / "sugarcrepe_pp_canonical.jsonl", rows)
        atomic_write_jsonl(temporary / "canonical_row_index.jsonl", index_rows)
        atomic_write_jsonl(temporary / "sugarcrepe_pp_pilot.jsonl", pilot_rows)
        atomic_write_jsonl(temporary / "sugarcrepe_pp_formal.jsonl", formal_rows)
        atomic_write_bytes(temporary / "pilot_filenames.txt", ("\n".join(pilot_names) + "\n").encode("utf-8"))
        atomic_write_bytes(temporary / "formal_filenames.txt", ("\n".join(formal_names) + "\n").encode("utf-8"))

        image_rows = _image_manifest(filenames, args.coco_root)
        image_by_name = {row["filename"]: row for row in image_rows}
        pilot_images = [image_by_name[name] for name in pilot_names]
        formal_images = [image_by_name[name] for name in formal_names]
        atomic_write_jsonl(temporary / "coco_referenced_images_manifest.jsonl", image_rows)
        atomic_write_jsonl(temporary / "coco_pilot_images_manifest.jsonl", pilot_images)
        atomic_write_jsonl(temporary / "coco_formal_images_manifest.jsonl", formal_images)
        missing = [row["filename"] for row in image_rows if row["status"] == "missing"]
        failures = [row for row in image_rows if row["status"] != "ready"]
        status_counts = Counter(row["status"] for row in image_rows)
        complete_status_counts = {
            status: int(status_counts.get(status, 0))
            for status in ("ready", "missing", "unreadable", "unsafe_path", "decode_failed")
        }
        atomic_write_json(temporary / "missing_images.json", {"schema_version": 1, "missing_count": len(missing), "filenames": missing})
        atomic_write_json(
            temporary / "image_failures.json",
            {"schema_version": 1, "status_counts": complete_status_counts, "failures": failures},
        )
        degenerates = _degenerates(rows)
        atomic_write_json(temporary / "degenerate_rows.json", degenerates)
        overlength, invariant = _token_preflight(rows)
        atomic_write_json(temporary / "overlength_rows.json", overlength)
        atomic_write_json(temporary / "input_invariant_failures.json", invariant)
        if invariant["failure_count"]:
            hard_code = "hard_failure_input_invariant"
        if any(row["status"] in ("unsafe_path", "decode_failed") for row in image_rows):
            hard_code = hard_code or "hard_failure_image_resource"
        if not failures:
            global_image_status = "ready"
        elif status_counts["unsafe_path"]:
            global_image_status = "unsafe_path"
        elif status_counts["decode_failed"]:
            global_image_status = "decode_failed"
        elif status_counts["unreadable"]:
            global_image_status = "unreadable"
        else:
            global_image_status = "missing"
        smoke_names = pilot_names[:8]
        smoke_image_status = "ready" if all(image_by_name[name]["status"] == "ready" for name in smoke_names) else "blocked"
        if failures and hard_code is None:
            blocked_code = "blocked_missing_or_unreadable_images"

        split_files = [
            _record(temporary / "sugarcrepe_pp_canonical.jsonl", temporary, "canonical_jsonl", 4757),
            _record(temporary / "canonical_row_index.jsonl", temporary, "canonical_row_index", 4757),
            _record(temporary / "sugarcrepe_pp_pilot.jsonl", temporary, "pilot_jsonl", len(pilot_rows)),
            _record(temporary / "sugarcrepe_pp_formal.jsonl", temporary, "formal_jsonl", len(formal_rows)),
            _record(temporary / "pilot_filenames.txt", temporary, "pilot_filenames", 153),
            _record(temporary / "formal_filenames.txt", temporary, "formal_filenames", 1389),
        ]
        split_files.sort(key=lambda row: row["relative_path"].encode("utf-8"))
        split_manifest = {
            "schema_version": 1,
            "manifest_type": "phase3-split-manifest-v1",
            "protocol_version": "phase3-v4",
            "split_version": "phase3-v1",
            "split_salt": "phase3-v1",
            "split_rule": "sha256('phase3-v1|'+filename) first16hex mod10; zero=pilot",
            "independent_unit": "unique_image_filename_group",
            "total_rows": 4757,
            "total_unique_images": 1542,
            "pilot_unique_images": 153,
            "formal_unique_images": 1389,
            "canonical_row_commitment_sha256": commitment,
            "files": split_files,
        }
        atomic_write_json(temporary / "split_manifest.json", split_manifest)
        write_sha256_sidecar(temporary / "split_manifest.json")
        degenerate_group_types: dict[str, set[str]] = {}
        for row in degenerates["rows"]:
            for kind in row["degenerate_types"]:
                degenerate_group_types.setdefault(kind, set()).add(row["filename"])
        frozen_counts = {
            "source_file_count": 5,
            "config_count": 5,
            "row_count": 4757,
            "unique_image_count": 1542,
            "pilot_unique_images": 153,
            "formal_unique_images": 1389,
            "image_status_counts": complete_status_counts,
            "degenerate_row_count": degenerates["degenerate_row_count"],
            "degenerate_group_count": degenerates["affected_image_group_count"],
            "degenerate_type_row_counts": degenerates["type_counts"],
            "degenerate_type_group_counts": {
                kind: len(names) for kind, names in sorted(degenerate_group_types.items())
            },
            "overlength_count": overlength["failure_count"],
            "input_invariant_failure_count": invariant["failure_count"],
        }
        phash_environment = {
            **versions,
            "hash_size": 8,
            "highfreq_factor": 4,
            "preprocess": "Pillow decode -> EXIF transpose -> RGB",
        }
        diagnostics = {
            "schema_version": 1,
            **frozen_counts,
            "p_hash_environment": phash_environment,
            "canonical_row_commitment_sha256": commitment,
        }
        atomic_write_json(temporary / "data_diagnostics.json", diagnostics)
        split_payload = snapshot_file(temporary / "split_manifest.json", root=temporary)
        artifact_paths = sorted(
            [path for path in temporary.iterdir() if path.is_file() and path.name not in ("data_manifest.json", "data_manifest.sha256")],
            key=lambda path: path.name.encode("utf-8"),
        )
        artifacts = []
        for path in artifact_paths:
            payload = snapshot_file(path, root=temporary)
            record_count = None
            if path.suffix == ".jsonl":
                record_count = len(payload.splitlines())
            elif path.suffix == ".txt":
                record_count = len([line for line in payload.splitlines() if line])
            artifacts.append(
                {
                    "relative_path": path.name,
                    "size_bytes": len(payload),
                    "sha256": sha256_bytes(payload),
                    "record_count": record_count,
                }
            )
        data_manifest = {
            "schema_version": 1,
            "manifest_type": "phase3-data-manifest-v2",
            "protocol_version": "phase3-v4",
            "split_version": "phase3-v1",
            "dataset_repo": REPO_ID,
            "dataset_revision": REVISION,
            "dataset_split": SPLIT,
            "source_files": source_records,
            "split_manifest": {"relative_path": "split_manifest.json", "size_bytes": len(split_payload), "sha256": sha256_bytes(split_payload)},
            "artifacts": artifacts,
            "canonical_row_commitment_sha256": commitment,
            "p_hash_environment": phash_environment,
            "global_image_status": global_image_status,
            "smoke_image_status": smoke_image_status,
            "coco_provenance_validation": "user_attestation_plus_frozen_per_file_sha256",
            "counts": frozen_counts,
            "exclusion_rule": "data_manifest.json and data_manifest.sha256 are excluded",
        }
        atomic_write_json(temporary / "data_manifest.json", data_manifest)
        write_sha256_sidecar(temporary / "data_manifest.json")
        publish_directory(temporary, args.output_dir)
        if hard_code:
            raise Phase3HardFailure(hard_code, "see prepared data diagnostics")
        if blocked_code:
            raise Phase3Blocked(blocked_code, "prepared metadata; images remain unavailable")
        return {
            "prepared_data_dir": str(args.output_dir),
            "rows": 4757,
            "unique_images": 1542,
            "pilot_unique_images": 153,
            "formal_unique_images": 1389,
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    parser.add_argument("--coco-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--hf-cache-dir", type=Path)
    parser.add_argument("--offline", action="store_true")
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return execute_with_status("prepare_phase3_data", args.status_output, lambda: prepare(args))


if __name__ == "__main__":
    raise SystemExit(main())
