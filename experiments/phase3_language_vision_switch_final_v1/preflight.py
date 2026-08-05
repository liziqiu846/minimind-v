#!/usr/bin/env python3
"""Legality, projection, and complete-base-result reuse preflight."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
from typing import Any

from experiments.phase3_module_marginal_budget_v1.parameterization import (
    assert_storage_contract,
    build_candidate_model,
)
from experiments.phase3_module_marginal_budget_v1.preflight import (
    fixed_projection_preflight,
)
from experiments.phase3_module_marginal_budget_v1.training import (
    private_trainable_parameters,
)
from experiments.stage2_protocol import REPO_ROOT, Stage2Protocol

from . import ACTION_MODULES, COORDINATE_MODULES, SEEDS
from .design import BASE_STATES, candidate_dimensions, training_config
from .manifest import (
    DEFAULT_MANIFEST,
    _source_base_artifact,
    freeze_manifest,
)

DEFAULT_STAGE2_PROTOCOL = REPO_ROOT / "experiments/stage2_protocol_v2.json"


def _synthetic_run(
    base_state: str, module: str | None, dimensions: dict[str, int]
) -> dict[str, Any]:
    kind = "reused_base_result" if module is None else "new_candidate"
    return {
        "run_id": f"preflight-{base_state}-{module or 'base'}",
        "config_id": f"preflight-{base_state}-{module or 'base'}",
        "run_type": kind,
        "base_state": base_state,
        "module": module,
        "seed": SEEDS[0],
        "coordinate_dimensions": dimensions,
    }


def _construct(
    stage2: Stage2Protocol,
    *,
    base_state: str,
    module: str | None,
    dimensions: dict[str, int],
) -> dict[str, Any]:
    model = None
    try:
        run = _synthetic_run(base_state, module, dimensions)
        model = build_candidate_model(training_config(run), stage2, device="cpu")
        store = model.stage2_coordinates
        assert_storage_contract(store)
        if dict(store.dimensions) != dimensions:
            raise AssertionError("constructed dimensions differ")
        parameters = [
            store.for_module(name) for name in COORDINATE_MODULES
        ]
        if len({id(parameter) for parameter in parameters}) != 3:
            raise AssertionError("module parameter objects are not private")
        if len(
            {
                parameter.untyped_storage().data_ptr()
                for parameter in parameters
            }
        ) != 3:
            raise AssertionError("module parameter storage is not private")
        trainable = private_trainable_parameters(model)
        names = sorted(
            name
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        )
        expected_names = sorted(
            f"stage2_coordinates.coordinates.{module_name}"
            for module_name in COORDINATE_MODULES
        )
        count = sum(parameter.numel() for parameter in trainable)
        if names != expected_names or count != sum(dimensions.values()):
            raise AssertionError("trainable parameter set differs")
        return {
            "model_constructed": True,
            "construction_device": "cpu",
            "three_module_parameters_private": True,
            "trainable_parameter_names": names,
            "trainable_parameter_count": count,
            "trainable_parameter_set_matches_expected": True,
        }
    finally:
        if model is not None:
            del model
        gc.collect()


def run_preflight(
    *, stage2_protocol_path: Path = DEFAULT_STAGE2_PROTOCOL, progress=print
) -> dict[str, Any]:
    stage2 = Stage2Protocol.load(stage2_protocol_path, require_frozen=True)
    definitions = []
    for state, dimensions in BASE_STATES.items():
        definitions.append((state, None, dict(dimensions)))
        definitions.extend(
            (state, module, candidate_dimensions(state, module))
            for module in ACTION_MODULES
        )
    results = []
    for index, (state, module, dimensions) in enumerate(definitions, start=1):
        projection = fixed_projection_preflight(dimensions, seeds=SEEDS)
        construction = _construct(
            stage2,
            base_state=state,
            module=module,
            dimensions=dimensions,
        )
        non_target_unchanged = (
            dimensions == BASE_STATES[state]
            if module is None
            else all(
                dimensions[name] == BASE_STATES[state][name]
                for name in COORDINATE_MODULES
                if name != module
            )
        )
        if not non_target_unchanged:
            raise AssertionError("a non-target module changed")
        results.append(
            {
                "base_state": state,
                "module": module,
                "coordinate_dimensions": dimensions,
                "status": "legal",
                "checks": {
                    **construction,
                    "non_target_modules_unchanged": True,
                    "projector_fixed_at_2327": dimensions["projector"]
                    == 2327,
                    "fixed_projection_reproducible": projection[
                        "all_roots_reproducible"
                    ],
                    "unused_coordinates_absent": projection[
                        "all_coordinates_used"
                    ],
                    "projection_roots": projection["roots"],
                },
            }
        )
        if progress is not None:
            progress(
                f"{index:02d}/{len(definitions)} "
                f"{state}/{module or 'base'}: legal"
            )
    reuse = {}
    for state in BASE_STATES:
        reuse[state] = {}
        for seed in SEEDS:
            source = _source_base_artifact(state, seed)
            reuse[state][str(seed)] = {
                "status": "verified",
                "reuse_scope": source["reuse_scope"],
                "checkpoint_path": source["checkpoint_path"],
                "checkpoint_sha256": source["checkpoint_sha256"],
                "source_run_result_sha256": source[
                    "source_run_result_sha256"
                ],
                "development_evaluation_result_sha256": source[
                    "development_evaluation_result_sha256"
                ],
                "coordinate_state_sha256": source[
                    "coordinate_state_sha256"
                ],
            }
    return {
        "status": "passed",
        "distinct_config_count": 6,
        "legal_config_count": 6,
        "illegal_config_count": 0,
        "validated_projection_roots": list(SEEDS),
        "complete_base_result_reuse_count": 6,
        "new_training_count": 12,
        "checkpoint_reuse_checks": reuse,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage2-protocol", type=Path, default=DEFAULT_STAGE2_PROTOCOL
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    receipt = run_preflight(stage2_protocol_path=args.stage2_protocol)
    output = {"preflight": receipt, "manifest_frozen": False}
    if args.freeze:
        digest = freeze_manifest(receipt, path=args.manifest)
        output.update(
            {
                "manifest_frozen": True,
                "manifest_path": str(args.manifest.resolve()),
                "manifest_sha256": digest,
            }
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

