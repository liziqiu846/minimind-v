"""Freeze and verify the three-seed formal curve execution plan."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from experiments.phase3_private_vs_shared_v1 import SEEDS
from experiments.phase3_private_vs_shared_v1.common import load_json, sha256_file
from experiments.phase3_private_vs_shared_v1.configs import build_config
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH as PS_PROTOCOL_PATH,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    validate_frozen_protocol,
)

from . import MODULES, PROTOCOL_VERSION
from .configs import coordinate_dimensions
from .preflight import DEFAULT_MANIFEST, verify_frozen_manifest

EXPECTED_CURVE_MANIFEST_SHA256 = (
    "c385dec006ee759445c8e1c73ba22df71b88e1834bd77d436b9e8a3233ae1238"
)
DEFAULT_ANCHOR_RESULTS_ROOT = Path("/home/lizhaohui/lzq/stage3-ps-formal-20260726-1825")
DEFAULT_RUN_PLAN = Path(__file__).with_name("curve_run_plan_9point_3seed.json")
RUN_PLAN_VERSION = "phase3-module-budget-value-curve-run-plan-v1"


def authoritative_seeds() -> dict[str, Any]:
    """Resolve seeds from the frozen P/S protocol, never from local defaults."""
    protocol_sha256 = validate_frozen_protocol()
    protocol = load_json(PS_PROTOCOL_PATH)
    seeds = tuple(protocol["seeds"])
    if seeds != SEEDS or any(
        build_config("P", 4096, seed)["seed"] != seed for seed in seeds
    ):
        raise RuntimeError("P/S protocol and deterministic P-4096 configs differ")
    return {
        "seeds": list(seeds),
        "source_protocol": str(PS_PROTOCOL_PATH),
        "source_protocol_id": protocol["protocol_id"],
        "source_protocol_sha256": sha256_file(PS_PROTOCOL_PATH),
        "source_protocol_canonical_sha256": protocol_sha256,
        "authority": "frozen_phase3_private_vs_shared_main_experiment",
    }


def _anchor_artifacts(root: Path, seeds: list[int]) -> dict[str, Any]:
    root = root.resolve()
    index_path = root / "training_artifact_index.json"
    index = load_json(index_path)
    if (
        index.get("status") != "complete"
        or index.get("candidate_count") != 18
        or index.get("confirmation_evaluation_run") is not False
    ):
        raise ValueError("P/S training artifact index is not the completed main run")
    by_id = {row["config_id"]: row for row in index["models"]}
    results = {}
    for seed in seeds:
        source_config_id = f"P-budget-4096-seed-{seed}"
        row = by_id.get(source_config_id)
        config = build_config("P", 4096, seed)
        manifest_path = (
            root / "candidates" / source_config_id / "training_manifest.json"
        )
        manifest = load_json(manifest_path)
        checkpoint_path = Path(manifest["checkpoint"]["path"])
        archive_path = Path(manifest["encoding"]["path"])
        if (
            row is None
            or row.get("status") != "complete"
            or row.get("seed") != seed
            or row.get("structure") != "P"
            or row.get("budget") != 4096
            or manifest.get("status") != "complete"
            or manifest.get("config") != config
            or manifest.get("coordinate_state_sha256") is None
            or sha256_file(manifest_path) != row["manifest_sha256"]
            or sha256_file(checkpoint_path) != manifest["checkpoint"]["sha256"]
            or sha256_file(archive_path) != manifest["encoding"]["sha256"]
        ):
            raise ValueError(f"authoritative anchor artifact mismatch for seed {seed}")
        results[str(seed)] = {
            "source_config_id": source_config_id,
            "training_manifest_path": str(manifest_path),
            "training_manifest_sha256": sha256_file(manifest_path),
            "checkpoint_path": str(checkpoint_path),
            "checkpoint_sha256": manifest["checkpoint"]["sha256"],
            "source_archive_path": str(archive_path),
            "source_archive_sha256": manifest["encoding"]["sha256"],
            "coordinate_state_sha256": manifest["coordinate_state_sha256"],
            "confirmation_risk_status": "not_yet_evaluated_in_source_run",
        }
    return {
        "source_root": str(root),
        "training_artifact_index_path": str(index_path),
        "training_artifact_index_sha256": sha256_file(index_path),
        "results_by_seed": results,
    }


def build_formal_run_plan(
    *,
    curve_manifest_path: Path = DEFAULT_MANIFEST,
    anchor_results_root: Path = DEFAULT_ANCHOR_RESULTS_ROOT,
) -> dict[str, Any]:
    curve_manifest_sha256 = verify_frozen_manifest(curve_manifest_path)
    if curve_manifest_sha256 != EXPECTED_CURVE_MANIFEST_SHA256:
        raise ValueError("curve sweep manifest differs from its frozen SHA-256")
    curve_manifest = load_json(curve_manifest_path)
    seed_authority = authoritative_seeds()
    seeds = seed_authority["seeds"]
    anchor_artifacts = _anchor_artifacts(anchor_results_root, seeds)
    anchor_dimensions = coordinate_dimensions(
        curve_manifest["anchor_config"]["coordinate_dimensions"]
    )
    runs = []
    for config in curve_manifest["configs"]:
        dimensions = coordinate_dimensions(config["coordinate_dimensions"])
        target_module = config["target_module"]
        if config["is_anchor"]:
            if dimensions != anchor_dimensions:
                raise ValueError("anchor run dimensions differ from P-4096")
        elif any(
            dimensions[module] != anchor_dimensions[module]
            for module in MODULES
            if module != target_module
        ):
            raise ValueError("a curve run changes a non-target module")
        for seed in seeds:
            run_id = f"{config['config_id']}-seed-{seed}"
            anchor_source = (
                anchor_artifacts["results_by_seed"][str(seed)]
                if config["is_anchor"]
                else None
            )
            runs.append(
                {
                    "run_id": run_id,
                    "config_id": run_id,
                    "sweep_config_id": config["config_id"],
                    "curve_name": config["curve_name"],
                    "curve_memberships": list(config["curve_memberships"]),
                    "target_module": target_module,
                    "anchor_config": config["anchor_config"],
                    "coordinate_dimensions": dimensions,
                    "sweep_index": config["sweep_index"],
                    "seed": seed,
                    "protocol_version": PROTOCOL_VERSION,
                    "training_required": not config["is_anchor"],
                    "anchor_reuse": config["is_anchor"],
                    "anchor_source": anchor_source,
                    "result_relative_directory": run_id,
                    "planned_status": (
                        "reuse_authoritative_anchor"
                        if config["is_anchor"]
                        else "planned"
                    ),
                }
            )
    identities = [(run["sweep_config_id"], run["seed"]) for run in runs]
    run_ids = [run["run_id"] for run in runs]
    if (
        len(runs) != 75
        or len(set(identities)) != 75
        or len(set(run_ids)) != 75
        or sum(run["training_required"] for run in runs) != 72
        or sum(run["anchor_reuse"] for run in runs) != 3
    ):
        raise AssertionError("formal curve run expansion is incomplete or duplicated")
    return {
        "schema_version": 1,
        "status": "pending_freeze",
        "run_plan_version": RUN_PLAN_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "curve_manifest_path": str(curve_manifest_path.resolve()),
        "curve_manifest_sha256": curve_manifest_sha256,
        "seed_authority": seed_authority,
        "formal_seeds": seeds,
        "anchor_config": curve_manifest["anchor_config"],
        "anchor_artifacts": anchor_artifacts,
        "config_count": 25,
        "expanded_run_count": 75,
        "actual_training_run_count": 72,
        "reused_anchor_run_count": 3,
        "results_directory_role": "independent_curve_results_root",
        "runs": runs,
    }


def _payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def freeze_formal_run_plan(
    *,
    output_path: Path = DEFAULT_RUN_PLAN,
    curve_manifest_path: Path = DEFAULT_MANIFEST,
    anchor_results_root: Path = DEFAULT_ANCHOR_RESULTS_ROOT,
) -> str:
    payload = {
        **build_formal_run_plan(
            curve_manifest_path=curve_manifest_path,
            anchor_results_root=anchor_results_root,
        ),
        "status": "frozen",
    }
    output_path = output_path.resolve()
    sidecar = output_path.with_suffix(".sha256")
    raw = _payload_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    sidecar_raw = f"{digest}  {output_path.name}\n".encode("ascii")
    if output_path.exists() or sidecar.exists():
        if (
            output_path.is_file()
            and sidecar.is_file()
            and output_path.read_bytes() == raw
            and sidecar.read_bytes() == sidecar_raw
        ):
            return digest
        raise FileExistsError("frozen formal run plan already exists and differs")
    output_path.write_bytes(raw)
    sidecar.write_bytes(sidecar_raw)
    return digest


def verify_formal_run_plan(path: Path = DEFAULT_RUN_PLAN) -> dict[str, Any]:
    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    payload = load_json(path)
    digest = sha256_file(path)
    if sidecar.read_text(encoding="ascii") != f"{digest}  {path.name}\n":
        raise ValueError("formal curve run plan SHA-256 sidecar differs")
    if (
        payload.get("status") != "frozen"
        or payload.get("run_plan_version") != RUN_PLAN_VERSION
        or payload.get("curve_manifest_sha256") != EXPECTED_CURVE_MANIFEST_SHA256
        or payload.get("formal_seeds") != list(SEEDS)
        or payload.get("expanded_run_count") != 75
        or payload.get("actual_training_run_count") != 72
        or payload.get("reused_anchor_run_count") != 3
    ):
        raise ValueError("formal curve run plan metadata differs")
    if (
        verify_frozen_manifest(Path(payload["curve_manifest_path"]))
        != payload["curve_manifest_sha256"]
    ):
        raise ValueError("formal run plan source manifest binding differs")
    rebuilt = {
        **build_formal_run_plan(
            curve_manifest_path=Path(payload["curve_manifest_path"]),
            anchor_results_root=Path(payload["anchor_artifacts"]["source_root"]),
        ),
        "status": "frozen",
    }
    if payload != rebuilt:
        raise ValueError("formal curve run plan differs from authoritative inputs")
    return payload
