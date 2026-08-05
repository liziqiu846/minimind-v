"""Build, freeze, and verify the final Language/Vision switch manifest."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch

from experiments.phase3_private_vs_shared_v1.common import REPO_ROOT, sha256_file
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH as PS_PROTOCOL_PATH,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    validate_frozen_protocol,
)

from . import (
    ACTION_MODULES,
    COORDINATE_MODULES,
    EVALUATION_ROLE,
    PROTOCOL_ID,
    PROTOCOL_VERSION,
    SEEDS,
    STRUCTURE,
)
from .design import (
    BASE_STATES,
    CALIBRATION,
    CANDIDATE_EXECUTION_ORDER,
    DECISION_RULE,
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
    "/home/lizhaohui/lzq/stage3-state-dependent-marginal-20260805"
)
SOURCE_EXPERIMENT_MANIFEST = (
    REPO_ROOT
    / "experiments/phase3_state_dependent_marginal_v1/experiment_manifest.json"
)
SOURCE_STATE_RUNS = {
    "original": "state-original-base",
    "language_rich": "state-language_rich-base",
}
REUSED_RUNTIME_SOURCES = (
    REPO_ROOT / "experiments/generalization_bound.py",
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/codec.py",
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/development_eval.py",
    REPO_ROOT / "experiments/phase3_module_marginal_budget_v1/parameterization.py",
    REPO_ROOT / "experiments/phase3_private_vs_shared_v1/train_one.py",
)

BOUND_SPECIFICATION = {
    "name": "raw_unclipped_compression_generalization_upper_bound",
    "empirical_risk": "development_task_risk=image_equal_mean(1-q_correct)",
    "prediction_processing": (
        "unchanged_phase3_v6_stable_sigmoid_no_additional_smoothing_or_clipping"
    ),
    "independent_sample_count": 1343,
    "familywise_delta": 0.05,
    "candidate_family_size": 75,
    "delta_each": 0.05 / 75,
    "description_bits": "sum_of_three_actual_module_encoded_bits",
    "complexity_nats": "C*ln(2)+2*ln(C)",
    "loss_support": [0.0, 1.0],
    "formula": (
        "B=R_hat+sqrt((C*ln(2)+2*ln(C)+ln(1/delta_each))/(2*n))"
    ),
    "improvement": "delta_B=B_base-B_candidate",
    "primary_is_raw_unclipped": True,
}


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
    if (
        not isinstance(coordinates, Mapping)
        or set(coordinates) != set(COORDINATE_MODULES)
    ):
        raise ValueError("source checkpoint lacks private module coordinates")
    return dict(coordinates)


def _source_base_artifact(base_state: str, seed: int) -> dict[str, Any]:
    source_id = f"{SOURCE_STATE_RUNS[base_state]}-seed-{seed}"
    result_path = (
        SOURCE_RESULTS_ROOT / "model_runs" / source_id / "run_result.json"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    dimensions = normalize_dimensions(BASE_STATES[base_state])
    checkpoint_path = Path(result["checkpoint_path"])
    training_manifest_path = Path(result["training_manifest_path"])
    evaluation_path = Path(result["development_evaluation_result_path"])
    codec_receipt_path = Path(result["codec_receipt_path"])
    training_manifest = json.loads(
        training_manifest_path.read_text(encoding="utf-8")
    )
    coordinates = _torch_coordinates(checkpoint_path)
    observed_dimensions = {
        module: int(coordinates[module].numel())
        for module in COORDINATE_MODULES
    }
    module_codec_paths = {
        module: Path(result["module_codec_paths"][module])
        for module in COORDINATE_MODULES
    }
    if (
        result.get("run_id") != source_id
        or result.get("seed") != seed
        or result.get("coordinate_dimensions") != dimensions
        or result.get("evaluation_role") != EVALUATION_ROLE
        or result.get("run_status") != "complete"
        or result.get("checkpoint_sha256") != sha256_file(checkpoint_path)
        or result.get("training_manifest_sha256")
        != sha256_file(training_manifest_path)
        or result.get("development_evaluation_result_sha256")
        != sha256_file(evaluation_path)
        or training_manifest.get("status") != "complete"
        or training_manifest.get("actual_optimizer_steps") != 1875
        or training_manifest.get("frozen_parameters_unchanged") is not True
        or observed_dimensions != dimensions
        or any(
            path.stat().st_size * 8
            != result["module_wise_encoded_bits"][module]
            for module, path in module_codec_paths.items()
        )
    ):
        raise ValueError(
            f"source base artifact differs for {base_state}/{seed}"
        )
    return {
        "source_run_id": source_id,
        "source_run_result_path": str(result_path.resolve()),
        "source_run_result_sha256": sha256_file(result_path),
        "checkpoint_path": str(checkpoint_path.resolve()),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "training_manifest_path": str(training_manifest_path.resolve()),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "coordinate_state_sha256": training_manifest[
            "coordinate_state_sha256"
        ],
        "development_evaluation_result_path": str(evaluation_path.resolve()),
        "development_evaluation_result_sha256": sha256_file(evaluation_path),
        "codec_receipt_path": str(codec_receipt_path.resolve()),
        "codec_receipt_sha256": sha256_file(codec_receipt_path),
        "module_codec_paths": {
            module: str(path.resolve())
            for module, path in module_codec_paths.items()
        },
        "module_codec_sha256": {
            module: sha256_file(path)
            for module, path in module_codec_paths.items()
        },
        "source_development_task_risk": float(
            result["development_task_risk"]
        ),
        "source_module_wise_encoded_bits": dict(
            result["module_wise_encoded_bits"]
        ),
        "source_total_encoded_bits": int(result["total_encoded_bits"]),
        "reuse_scope": "complete_base_model_result",
        "new_training_forbidden": True,
        "new_inference_forbidden": True,
    }


def build_manifest(*, preflight: Mapping[str, Any]) -> dict[str, Any]:
    """Expand two states × (one reused base + two actions) × three seeds."""
    validate_frozen_protocol()
    source_manifest_digest = (
        SOURCE_EXPERIMENT_MANIFEST.with_suffix(".sha256")
        .read_text(encoding="ascii")
        .split()[0]
    )
    if sha256_file(SOURCE_EXPERIMENT_MANIFEST) != source_manifest_digest:
        raise ValueError("source state experiment manifest hash differs")
    base_sources: dict[str, Any] = {}
    base_runs: list[dict[str, Any]] = []
    candidate_runs_by_identity: dict[tuple[int, str, str], dict[str, Any]] = {}
    comparisons: list[dict[str, Any]] = []
    candidate_configs = []
    for base_state, base_dimensions in BASE_STATES.items():
        base_sources[base_state] = {}
        for seed in SEEDS:
            source = _source_base_artifact(base_state, seed)
            base_sources[base_state][str(seed)] = source
            run_id = base_run_id(base_state, seed)
            base_runs.append(
                {
                    "run_id": run_id,
                    "config_id": run_id,
                    "run_type": "reused_base_result",
                    "base_state": base_state,
                    "module": None,
                    "seed": seed,
                    "structure": STRUCTURE,
                    "coordinate_dimensions": dict(base_dimensions),
                    "training_required": False,
                    "checkpoint_reuse": True,
                    "complete_result_reuse": True,
                    "source": source,
                    "result_relative_directory": f"model_runs/{run_id}",
                }
            )
        for module in ACTION_MODULES:
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
                run = {
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
                    "complete_result_reuse": False,
                    "source": None,
                    "result_relative_directory": f"model_runs/{run_id}",
                }
                candidate_runs_by_identity[(seed, base_state, module)] = run
                comparisons.append(
                    {
                        "base_state": base_state,
                        "module": module,
                        "seed": seed,
                        "base_run_id": base_run_id(base_state, seed),
                        "candidate_run_id": run_id,
                        "primary_improvement_definition": (
                            "B_base-B_candidate"
                        ),
                    }
                )
    ordered_candidates = [
        candidate_runs_by_identity[identity]
        for identity in CANDIDATE_EXECUTION_ORDER
    ]
    runs = base_runs + ordered_candidates
    for index, run in enumerate(runs):
        run["execution_index"] = index
        run["paired_seed_block"] = int(run["seed"])
    run_ids = [run["run_id"] for run in runs]
    identities = [
        (row["base_state"], row["module"], row["seed"])
        for row in comparisons
    ]
    if (
        len(runs) != 18
        or len(set(run_ids)) != 18
        or sum(run["training_required"] for run in runs) != 12
        or sum(run["checkpoint_reuse"] for run in runs) != 6
        or len(candidate_configs) != 4
        or len(comparisons) != 12
        or len(set(identities)) != 12
    ):
        raise AssertionError("final switch run expansion differs")
    if preflight.get("status") != "passed":
        raise ValueError("manifest cannot be built from a failed preflight")
    return {
        "schema_version": 1,
        "status": "frozen",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "scientific_question": (
            "whether the preferred Language/Vision budget direction switches "
            "between Original and Language-rich"
        ),
        "structure": STRUCTURE,
        "action_modules": list(ACTION_MODULES),
        "coordinate_modules": list(COORDINATE_MODULES),
        "seeds": list(SEEDS),
        "base_states": {
            state: dict(dimensions)
            for state, dimensions in BASE_STATES.items()
        },
        "upper_dimensions": UPPER_DIMENSIONS,
        "candidate_configs": candidate_configs,
        "runs": runs,
        "comparisons": comparisons,
        "counts": {
            "base_state_count": 2,
            "action_count": 2,
            "candidate_config_count": 4,
            "seed_count": 3,
            "expanded_model_run_count": 18,
            "reused_complete_base_result_count": 6,
            "new_training_count": 12,
            "comparison_count": 12,
        },
        "blocking_and_order": {
            "block": "seed",
            "randomization_seed": 20260805,
            "candidate_execution_order": [
                {
                    "seed": seed,
                    "base_state": state,
                    "module": module,
                }
                for seed, state, module in CANDIDATE_EXECUTION_ORDER
            ],
        },
        "calibration": CALIBRATION,
        "bound": BOUND_SPECIFICATION,
        "decision_rule": DECISION_RULE,
        "evaluation": {
            "role": EVALUATION_ROLE,
            "protocol": "unchanged_phase3_v6_development_scoring",
            "risk": "development_task_risk",
            "candidate_family_size_reused_from_previous_round": 75,
        },
        "source_experiment": {
            "results_root": str(SOURCE_RESULTS_ROOT.resolve()),
            "manifest_path": str(SOURCE_EXPERIMENT_MANIFEST.resolve()),
            "manifest_sha256": sha256_file(SOURCE_EXPERIMENT_MANIFEST),
            "protocol_path": str(PS_PROTOCOL_PATH.resolve()),
            "protocol_sha256": sha256_file(PS_PROTOCOL_PATH),
            "base_artifacts": base_sources,
        },
        "runtime_source_sha256": runtime_source_hashes(),
        "preflight": dict(preflight),
        "scope_exclusions": [
            "projector_action",
            "projector_rich_state",
            "additional_states",
            "grids",
            "ablations",
            "fitted_curves",
            "eta_primary_metric",
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
        raise FileExistsError(
            "frozen experiment manifest already exists and differs"
        )
    path.write_bytes(raw)
    sidecar.write_bytes(sidecar_raw)
    return digest


def _validate_source(
    source: Mapping[str, Any], dimensions: Mapping[str, int]
) -> None:
    for path_field, hash_field in (
        ("source_run_result_path", "source_run_result_sha256"),
        ("checkpoint_path", "checkpoint_sha256"),
        ("training_manifest_path", "training_manifest_sha256"),
        (
            "development_evaluation_result_path",
            "development_evaluation_result_sha256",
        ),
        ("codec_receipt_path", "codec_receipt_sha256"),
    ):
        path = Path(source[path_field])
        if not path.is_file() or sha256_file(path) != source[hash_field]:
            raise ValueError(f"frozen source artifact differs: {path}")
    for module in COORDINATE_MODULES:
        path = Path(source["module_codec_paths"][module])
        if sha256_file(path) != source["module_codec_sha256"][module]:
            raise ValueError("frozen source module codec differs")
    coordinates = _torch_coordinates(Path(source["checkpoint_path"]))
    if {
        module: int(coordinates[module].numel())
        for module in COORDINATE_MODULES
    } != dict(dimensions):
        raise ValueError("frozen source checkpoint dimensions differ")


def verify_frozen_manifest(
    path: Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
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
        or payload.get("action_modules") != list(ACTION_MODULES)
        or payload.get("coordinate_modules")
        != list(COORDINATE_MODULES)
        or payload.get("seeds") != list(SEEDS)
        or counts.get("candidate_config_count") != 4
        or counts.get("expanded_model_run_count") != 18
        or counts.get("reused_complete_base_result_count") != 6
        or counts.get("new_training_count") != 12
        or counts.get("comparison_count") != 12
        or payload.get("preflight", {}).get("status") != "passed"
        or payload["preflight"].get("legal_config_count") != 6
    ):
        raise ValueError("frozen experiment manifest metadata differs")
    if runtime_source_hashes() != payload["runtime_source_sha256"]:
        raise ValueError("runtime source files differ from frozen manifest")
    if (
        sha256_file(Path(payload["source_experiment"]["manifest_path"]))
        != payload["source_experiment"]["manifest_sha256"]
    ):
        raise ValueError("source state experiment manifest differs")
    for state, by_seed in payload["source_experiment"][
        "base_artifacts"
    ].items():
        for source in by_seed.values():
            _validate_source(source, payload["base_states"][state])
    return payload
