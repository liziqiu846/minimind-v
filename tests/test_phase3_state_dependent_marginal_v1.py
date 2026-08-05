import copy

import pytest

from experiments.phase3_state_dependent_marginal_v1 import MODULES, SEEDS
from experiments.phase3_state_dependent_marginal_v1.design import (
    BASE_STATES,
    candidate_dimensions,
)
from experiments.phase3_state_dependent_marginal_v1.manifest import build_manifest
from experiments.phase3_state_dependent_marginal_v1.run_experiment import (
    select_runs,
)
from experiments.phase3_state_dependent_marginal_v1.reporting.summarize_signed import (
    build_signed_summary,
)
from experiments.phase3_state_dependent_marginal_v1.summarize import build_summary


def _preflight():
    return {
        "status": "passed",
        "distinct_config_count": 12,
        "legal_config_count": 12,
        "illegal_config_count": 0,
    }


def test_exact_minimal_design_changes_only_target_module():
    expected_upper = {
        "original": {"vision": 766, "projector": 3063, "language": 1562},
        "language_rich": {
            "vision": 766,
            "projector": 3063,
            "language": 4686,
        },
        "projector_rich": {
            "vision": 766,
            "projector": 9187,
            "language": 1562,
        },
    }
    assert tuple(SEEDS) == (43101, 43102, 43103)
    for state, base in BASE_STATES.items():
        for module in MODULES:
            candidate = candidate_dimensions(state, module)
            assert candidate[module] == expected_upper[state][module]
            assert candidate[module] > base[module]
            assert all(
                candidate[other] == base[other]
                for other in MODULES
                if other != module
            )


def test_manifest_expands_to_9_reuse_27_new_and_no_more():
    manifest = build_manifest(preflight=_preflight())
    assert len(manifest["candidate_configs"]) == 9
    assert len(manifest["runs"]) == 36
    assert len(manifest["comparisons"]) == 27
    assert sum(run["checkpoint_reuse"] for run in manifest["runs"]) == 9
    assert sum(run["training_required"] for run in manifest["runs"]) == 27
    assert len({run["run_id"] for run in manifest["runs"]}) == 36
    assert len(
        {
            (row["base_state"], row["module"], row["seed"])
            for row in manifest["comparisons"]
        }
    ) == 27
    assert len(select_runs(manifest, all_runs=True)) == 36
    assert len(select_runs(manifest, state="language_rich")) == 12


def _fake_results(manifest):
    results = {}
    module_offset = {"vision": 0.003, "projector": 0.002, "language": 0.001}
    bit_increase = {"vision": 200, "projector": 800, "language": 400}
    for run in manifest["runs"]:
        base_bits = {"vision": 1800, "projector": 6000, "language": 2200}
        risk = 0.5
        bits = dict(base_bits)
        if run["module"] is not None:
            module = run["module"]
            bits[module] += bit_increase[module]
            risk -= module_offset[module]
        results[run["run_id"]] = {
            "coordinate_dimensions": copy.deepcopy(run["coordinate_dimensions"]),
            "module_wise_encoded_bits": bits,
            "development_task_risk": risk,
        }
    return results


def test_summary_uses_target_actual_bit_denominator_and_seed_consistency():
    manifest = build_manifest(preflight=_preflight())
    summary = build_summary(manifest, _fake_results(manifest))
    assert summary["comparison_count"] == 27
    row = next(
        row
        for row in summary["comparisons"]
        if row["base_state"] == "original"
        and row["module"] == "vision"
        and row["seed"] == 43101
    )
    assert row["delta_target_module_actual_encoded_bits"] == 200
    assert row["eta_marginal_value"] == pytest.approx(0.003 / 200)
    for state in BASE_STATES:
        ranking = summary["state_rankings"][state]
        assert ranking["ranking"] == ["vision", "projector", "language"]
        assert ranking["all_three_seeds_same_ranking"] is True


def test_signed_summary_retains_nonzero_negative_actual_bit_delta():
    manifest = build_manifest(preflight=_preflight())
    results = _fake_results(manifest)
    row = next(
        row
        for row in manifest["comparisons"]
        if row["base_state"] == "language_rich"
        and row["module"] == "language"
        and row["seed"] == 43101
    )
    results[row["base_run_id"]]["module_wise_encoded_bits"]["language"] = 6808
    results[row["candidate_run_id"]]["module_wise_encoded_bits"]["language"] = 6776
    results[row["base_run_id"]]["development_task_risk"] = 0.48
    results[row["candidate_run_id"]]["development_task_risk"] = 0.481
    summary = build_signed_summary(manifest, results)
    observed = next(
        value
        for value in summary["comparisons"]
        if value["base_state"] == "language_rich"
        and value["module"] == "language"
        and value["seed"] == 43101
    )
    assert observed["delta_target_module_actual_encoded_bits"] == -32
    assert observed["eta_marginal_value"] == pytest.approx(0.001 / 32)
    assert observed["status"] == "valid_signed_negative_actual_bit_delta"
