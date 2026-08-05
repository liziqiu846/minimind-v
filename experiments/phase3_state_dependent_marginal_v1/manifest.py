"""Build, freeze, and verify the exact state-dependent execution manifest."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch

from experiments.phase3_module_marginal_budget_v1.formal_plan import (
    DEFAULT_RUN_PLAN as SOURCE_RUN_PLAN,
)
from experiments.phase3_module_marginal_budget_v1.formal_plan import (
    verify_formal_run_plan as verify_source_run_plan,
)
from experiments.phase3_private_vs_shared_v1.common import REPO_ROOT, sha256_file
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH as PS_PROTOCOL_PATH,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    validate_frozen_protocol,
)

from . import (
    EVALUATION_ROLE,
    MODULES,
    PROTOCOL_ID,
    PROTOCOL_VERSION,
    SEEDS,
    STRUCTURE,
)
from .design import (
    BASE_STATES,
    UPPER_DIMENSIONS,
    base_run_id,
    candidate_config_id,
    candidate_dimensions,
    candidate_run_id,
    normalize_dimensions,
)

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = PACKAGE_ROOT / "experiment_manifest.json"
SOURCE_RESULTS_ROOT = Path(
    "/home/lizhaohui/lzq/stage3-curve-development-20260804"
)
SOURCE_STATE_CONFIGS = {
    "original": "P-4096-anchor",
    "language_rich": "P-4096-language-coords-3561",
    "projector_rich": "P-4096-projector-coords-6981",
}
REUSED_RUNTIME_SOURCES = (
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/codec.py",
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/development_eval.py",
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/parameterization.py",
    REPO_ROOT / "experiments/phase3_private_vs_shared_v1/train_one.py",
)


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def runtime_source_hashes() -> dict[str, str]:
    sources = {
        str(path.relative_to(REPO_ROOT)): sha256_file(path)
        for path in sorted(PACKAGE_ROOT.glob("*.py"))
    }
    sources.update(
        {
            str(path.relative_to(REPO_ROOT)): sha256_file(path)
            for path in REUSED_RUNTIME_SOURCES
        }
    )
    return dict(sorted(sources.items()))


def _torch_coordinates(path: Path) -> dict[str, torch.Tensor]:
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    coordinates = checkpoint.get("coordinates")
    if not isinstance(coordinates, Mapping) or set(coordinates) != set(MODULES):
        raise ValueError("source checkpoint lacks private module coordinates")
    return dict(coordinates)


def _source_base_artifact(base_state: str, seed: int) -> dict[str, Any]:
    source_id = f"{SOURCE_STATE_CONFIGS[base_state]}-seed-{seed}"
    result_path = SOURCE_RESULTS_ROOT / source_id / "run_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    dimensions = normalize_dimensions(BASE_STATES[base_state])
    checkpoint_path = Path(result["checkpoint_path"])
    manifest_path = Path(result["training_manifest_path"])
    development_path = Path(result["development_evaluation_result_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    coordinates = _torch_coordinates(checkpoint_path)
    observed_dimensions = {
        module: int(coordinates[module].numel()) for module in MODULES
    }
    if (
        result.get("run_id") != source_id
        or result.get("seed") != seed
        or result.get("coordinate_dimensions") != dimensions
        or result.get("evaluation_role") != EVALUATION_ROLE
        or result.get("run_status") != "complete"
        or result.get("curve_run_plan_sha256") != sha256_file(SOURCE_RUN_PLAN)
        or result.get("checkpoint_sha256") != sha256_file(checkpoint_path)
        or result.get("training_manifest_sha256") != sha256_file(manifest_path)
        or result.get("development_evaluation_result_sha256")
        != sha256_file(development_path)
        or manifest.get("status") != "complete"
        or manifest.get("config", {}).get("seed") != seed
        or manifest.get("config", {}).get("coordinate_dimensions") != dimensions
        or manifest.get("checkpoint", {}).get("sha256")
        != sha256_file(checkpoint_path)
        or manifest.get("actual_optimizer_steps") != 1875
        or manifest.get("frozen_parameters_unchanged") is not True
        or observed_dimensions != dimensions
    ):
        raise ValueError(
            f"source base checkpoint or receipt differs for {base_state}/{seed}"
        )
    return {
        "source_run_id": source_id,
        "source_run_result_path": str(result_path.resolve()),
        "source_run_result_sha256": sha256_file(result_path),
        "checkpoint_path": str(checkpoint_path.resolve()),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "training_manifest_path": str(manifest_path.resolve()),
        "training_manifest_sha256": sha256_file(manifest_path),
        "coordinate_state_sha256": manifest["coordinate_state_sha256"],
        "development_evaluation_result_path": str(development_path.resolve()),
        "development_evaluation_result_sha256": sha256_file(development_path),
        "source_development_task_risk": float(result["development_task_risk"]),
        "source_module_wise_encoded_bits": dict(
            result["module_wise_encoded_bits"]
        ),
        "reuse_scope": "checkpoint_and_training_receipt",
        "new_training_forbidden": True,
    }


def build_manifest(*, preflight: Mapping[str, Any]) -> dict[str, Any]:
    """Expand 3 states × (1 reused base + 3 candidates) × 3 seeds."""
    validate_frozen_protocol()
    verify_source_run_plan(SOURCE_RUN_PLAN)
    base_sources: dict[str, Any] = {}
    runs: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    candidate_configs = []
    for base_state, base_dimensions in BASE_STATES.items():
        base_sources[base_state] = {}
        for seed in SEEDS:
            source = _source_base_artifact(base_state, seed)
            base_sources[base_state][str(seed)] = source
            run_id = base_run_id(base_state, seed)
            runs.append(
                {
                    "run_id": run_id,
                    "config_id": run_id,
                    "run_type": "reused_base",
                    "base_state": base_state,
                    "module": None,
                    "seed": seed,
                    "structure": STRUCTURE,
                    "coordinate_dimensions": dict(base_dimensions),
                    "training_required": False,
                    "checkpoint_reuse": True,
                    "source": source,
                    "result_relative_directory": f"model_runs/{run_id}",
                }
            )
        for module in MODULES:
            config_id = candidate_config_id(base_state, module)
            dimensions = candidate_dimensions(base_state, module)
            candidate_configs.append(
                {
                    "config_id": config_id,
                    "base_state": base_state,
                    "module": module,
                    "base_dimensions": dict(base_dimensions),
                    "coordinate_dimensions": dimensions,
                }
            )
            for seed in SEEDS:
                run_id = candidate_run_id(base_state, module, seed)
                runs.append(
                    {
                        "run_id": run_id,
                        "config_id": run_id,
                        "candidate_config_id": config_id,
                        "run_type": "new_candidate",
                        "base_state": base_state,
                        "module": module,
                        "seed": seed,
                        "structure": STRUCTURE,
                        "coordinate_dimensions": dimensions,
                        "training_required": True,
                        "checkpoint_reuse": False,
                        "source": None,
                        "result_relative_directory": f"model_runs/{run_id}",
                    }
                )
                comparisons.append(
                    {
                        "base_state": base_state,
                        "module": module,
                        "seed": seed,
                        "base_run_id": base_run_id(base_state, seed),
                        "candidate_run_id": run_id,
                        "denominator": (
                            "candidate_target_module_actual_encoded_bits"
                            "-base_target_module_actual_encoded_bits"
                        ),
                        "marginal_value_definition": (
                            "-(R_new-R_base)/(C_M_new-C_M_base)"
                        ),
                    }
                )
    run_ids = [run["run_id"] for run in runs]
    candidate_ids = [config["config_id"] for config in candidate_configs]
    identities = [
        (row["base_state"], row["module"], row["seed"]) for row in comparisons
    ]
    if (
        len(runs) != 36
        or len(set(run_ids)) != 36
        or sum(run["training_required"] for run in runs) != 27
        or sum(run["checkpoint_reuse"] for run in runs) != 9
        or len(candidate_configs) != 9
        or len(set(candidate_ids)) != 9
        or len(comparisons) != 27
        or len(set(identities)) != 27
    ):
        raise AssertionError("state-dependent run expansion differs")
    if preflight.get("status") != "passed":
        raise ValueError("manifest cannot be built from a failed preflight")
    return {
        "schema_version": 1,
        "status": "frozen",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "scientific_question": (
            "whether local Vision/Projector/Language marginal-value ranking "
            "depends on the current private-budget state"
        ),
        "structure": STRUCTURE,
        "modules": list(MODULES),
        "seeds": list(SEEDS),
        "base_states": {
            state: dict(dimensions) for state, dimensions in BASE_STATES.items()
        },
        "upper_dimensions": UPPER_DIMENSIONS,
        "candidate_configs": candidate_configs,
        "runs": runs,
        "comparisons": comparisons,
        "counts": {
            "base_state_count": 3,
            "candidate_config_count": 9,
            "seed_count": 3,
            "expanded_model_run_count": 36,
            "reused_checkpoint_count": 9,
            "new_training_count": 27,
            "comparison_count": 27,
        },
        "evaluation": {
            "role": EVALUATION_ROLE,
            "protocol": "unchanged_phase3_v6_development_scoring",
            "risk": "development_task_risk",
            "semantic_bound_and_visual_guardrail_retained": True,
            "candidate_family_size_reused_from_previous_round": 75,
        },
        "source_experiment": {
            "results_root": str(SOURCE_RESULTS_ROOT.resolve()),
            "run_plan_path": str(SOURCE_RUN_PLAN.resolve()),
            "run_plan_sha256": sha256_file(SOURCE_RUN_PLAN),
            "protocol_path": str(PS_PROTOCOL_PATH.resolve()),
            "protocol_sha256": sha256_file(PS_PROTOCOL_PATH),
            "base_artifacts": base_sources,
        },
        "runtime_source_sha256": runtime_source_hashes(),
        "preflight": dict(preflight),
        "scope_exclusions": [
            "additional_states",
            "grids",
            "ablations",
            "smoothing",
            "fitted_curves",
            "new_metrics",
        ],
    }


def freeze_manifest(
    preflight: Mapping[str, Any], *, path: Path = DEFAULT_MANIFEST
) -> str:
    payload = build_manifest(preflight=preflight)
    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    raw = _json_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    sidecar_raw = f"{digest}  {path.name}\n".encode("ascii")
    if path.exists() or sidecar.exists():
        if (
            path.is_file()
            and sidecar.is_file()
            and path.read_bytes() == raw
            and sidecar.read_bytes() == sidecar_raw
        ):
            return digest
        raise FileExistsError("frozen experiment manifest already exists and differs")
    path.write_bytes(raw)
    sidecar.write_bytes(sidecar_raw)
    return digest


def _validate_source(source: Mapping[str, Any], dimensions: Mapping[str, int]) -> None:
    for path_field, hash_field in (
        ("source_run_result_path", "source_run_result_sha256"),
        ("checkpoint_path", "checkpoint_sha256"),
        ("training_manifest_path", "training_manifest_sha256"),
        (
            "development_evaluation_result_path",
            "development_evaluation_result_sha256",
        ),
    ):
        path = Path(source[path_field])
        if not path.is_file() or sha256_file(path) != source[hash_field]:
            raise ValueError(f"frozen source artifact differs: {path}")
    coordinates = _torch_coordinates(Path(source["checkpoint_path"]))
    if {
        module: int(coordinates[module].numel()) for module in MODULES
    } != dict(dimensions):
        raise ValueError("frozen source checkpoint dimensions differ")


def verify_frozen_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = sha256_file(path)
    if sidecar.read_text(encoding="ascii") != f"{digest}  {path.name}\n":
        raise ValueError("experiment manifest SHA-256 sidecar differs")
    counts = payload.get("counts", {})
    if (
        payload.get("status") != "frozen"
        or payload.get("protocol_id") != PROTOCOL_ID
        or payload.get("protocol_version") != PROTOCOL_VERSION
        or payload.get("modules") != list(MODULES)
        or payload.get("seeds") != list(SEEDS)
        or counts.get("candidate_config_count") != 9
        or counts.get("expanded_model_run_count") != 36
        or counts.get("reused_checkpoint_count") != 9
        or counts.get("new_training_count") != 27
        or counts.get("comparison_count") != 27
        or payload.get("preflight", {}).get("status") != "passed"
        or payload["preflight"].get("legal_config_count") != 12
    ):
        raise ValueError("frozen experiment manifest metadata differs")
    if runtime_source_hashes() != payload["runtime_source_sha256"]:
        raise ValueError("runtime source files differ from frozen manifest")
    source_plan = Path(payload["source_experiment"]["run_plan_path"])
    if (
        sha256_file(source_plan)
        != payload["source_experiment"]["run_plan_sha256"]
    ):
        raise ValueError("source curve plan differs")
    verify_source_run_plan(source_plan)
    for state, dimensions in BASE_STATES.items():
        if payload["base_states"][state] != dimensions:
            raise ValueError("base-state dimensions differ")
        for seed in SEEDS:
            _validate_source(
                payload["source_experiment"]["base_artifacts"][state][str(seed)],
                dimensions,
            )
    run_ids = [run["run_id"] for run in payload["runs"]]
    if len(run_ids) != 36 or len(set(run_ids)) != 36:
        raise ValueError("frozen run identities differ")
    for run in payload["runs"]:
        state = run["base_state"]
        if run["run_type"] == "reused_base":
            expected = dict(BASE_STATES[state])
            if (
                run["module"] is not None
                or run["training_required"]
                or not run["checkpoint_reuse"]
            ):
                raise ValueError("base run semantics differ")
        else:
            expected = candidate_dimensions(state, run["module"])
            if (
                not run["training_required"]
                or run["checkpoint_reuse"]
                or run["source"] is not None
            ):
                raise ValueError("candidate run semantics differ")
        if run["coordinate_dimensions"] != expected:
            raise ValueError("run coordinate dimensions differ")
    return payload
