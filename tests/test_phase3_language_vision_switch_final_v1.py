import copy
import math

import pytest

from experiments.phase3_language_vision_switch_final_v1 import (
    ACTION_MODULES,
    SEEDS,
)
from experiments.phase3_language_vision_switch_final_v1.design import (
    BASE_STATES,
    candidate_dimensions,
)
from experiments.phase3_language_vision_switch_final_v1.manifest import (
    build_manifest,
)
from experiments.phase3_language_vision_switch_final_v1.run_experiment import (
    select_runs,
)
from experiments.phase3_language_vision_switch_final_v1.summarize import (
    build_summary,
    full_bound,
)


def _preflight():
    return {
        "status": "passed",
        "distinct_config_count": 6,
        "legal_config_count": 6,
        "illegal_config_count": 0,
    }


def test_exact_terminal_design_changes_only_vision_or_language():
    expected = {
        "original": {"vision": 1700, "language": 2700},
        "language_rich": {"vision": 1700, "language": 5976},
    }
    assert tuple(SEEDS) == (43101, 43102, 43103)
    assert tuple(BASE_STATES) == ("original", "language_rich")
    assert tuple(ACTION_MODULES) == ("vision", "language")
    for state, base in BASE_STATES.items():
        for module in ACTION_MODULES:
            candidate = candidate_dimensions(state, module)
            assert candidate[module] == expected[state][module]
            assert candidate[module] > base[module]
            assert candidate["projector"] == 2327
            assert all(
                candidate[other] == base[other]
                for other in ("vision", "projector", "language")
                if other != module
            )


def test_manifest_expands_to_6_complete_reuse_and_12_new_only():
    manifest = build_manifest(preflight=_preflight())
    assert len(manifest["candidate_configs"]) == 4
    assert len(manifest["runs"]) == 18
    assert len(manifest["comparisons"]) == 12
    assert sum(run["complete_result_reuse"] for run in manifest["runs"]) == 6
    assert sum(run["training_required"] for run in manifest["runs"]) == 12
    assert len({run["run_id"] for run in manifest["runs"]}) == 18
    assert len(select_runs(manifest, all_runs=True)) == 18
    assert len(select_runs(manifest, state="language_rich")) == 9
    assert not any(run["module"] == "projector" for run in manifest["runs"])


def _fake_results(manifest, *, expected_switch=True):
    results = {}
    for run in manifest["runs"]:
        state = run["base_state"]
        seed_offset = (run["seed"] - 43102) * 1e-7
        base_bits = (
            {"vision": 1900, "projector": 6200, "language": 2400}
            if state == "original"
            else {"vision": 1900, "projector": 6200, "language": 6200}
        )
        bits = dict(base_bits)
        risk = 0.49 + seed_offset
        if run["module"] is not None:
            module = run["module"]
            bits[module] += 2500 if module == "vision" else 2700
            if expected_switch:
                improvement = {
                    ("original", "vision"): 0.02,
                    ("original", "language"): 0.25,
                    ("language_rich", "vision"): 0.25,
                    ("language_rich", "language"): 0.02,
                }[(state, module)]
            else:
                improvement = 0.02
            risk -= improvement
        results[run["run_id"]] = {
            "coordinate_dimensions": copy.deepcopy(
                run["coordinate_dimensions"]
            ),
            "module_wise_encoded_bits": bits,
            "total_encoded_bits": sum(bits.values()),
            "development_task_risk": risk,
        }
    return results


def test_full_bound_uses_total_actual_bits_and_frozen_formula():
    manifest = build_manifest(preflight=_preflight())
    result = {
        "development_task_risk": 0.4,
        "total_encoded_bits": 10000,
    }
    observed = full_bound(result, manifest["bound"])
    complexity = 10000 * math.log(2) + 2 * math.log(10000)
    expected = 0.4 + math.sqrt(
        (
            complexity
            + math.log(1 / manifest["bound"]["delta_each"])
        )
        / (2 * 1343)
    )
    assert observed["B_raw_unclipped"] == pytest.approx(expected)


def test_switch_decision_uses_delta_b_majority_and_bit_gate():
    manifest = build_manifest(preflight=_preflight())
    summary = build_summary(
        manifest, _fake_results(manifest, expected_switch=True)
    )
    assert summary["bit_adequacy"]["overall_passed"] is True
    assert summary["state_results"]["original"]["median_ranking"] == [
        "language",
        "vision",
    ]
    assert summary["state_results"]["language_rich"][
        "median_ranking"
    ] == ["vision", "language"]
    assert summary["switch_validation_passed"] is True
    assert (
        summary["route_decision"]
        == "proceed_to_dynamic_budget_algorithm_design"
    )


def test_near_zero_bit_increase_forces_stop():
    manifest = build_manifest(preflight=_preflight())
    results = _fake_results(manifest, expected_switch=True)
    run = next(
        run
        for run in manifest["runs"]
        if run["base_state"] == "original"
        and run["module"] == "language"
        and run["seed"] == 43101
    )
    base_id = next(
        row["base_run_id"]
        for row in manifest["comparisons"]
        if row["candidate_run_id"] == run["run_id"]
    )
    results[run["run_id"]]["module_wise_encoded_bits"]["language"] = (
        results[base_id]["module_wise_encoded_bits"]["language"] + 8
    )
    results[run["run_id"]]["total_encoded_bits"] = sum(
        results[run["run_id"]]["module_wise_encoded_bits"].values()
    )
    summary = build_summary(manifest, results)
    assert summary["bit_adequacy"]["overall_passed"] is False
    assert summary["switch_validation_passed"] is False
    assert (
        summary["route_decision"]
        == "stop_language_vision_switch_route_no_expansion"
    )
