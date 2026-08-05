import json

import pytest
import torch

from experiments.phase3_module_marginal_budget_v1 import (
    MODULES,
    PROTOCOL_VERSION,
    SEED_PLACEHOLDER,
)
from experiments.phase3_module_marginal_budget_v1.anchor import (
    resolve_p4096_anchor,
)
from experiments.phase3_module_marginal_budget_v1.codec import (
    assert_round_trip,
    encode_coordinates,
    load_decoded_coordinates,
)
from experiments.phase3_module_marginal_budget_v1.curve_results import (
    summarize_curve_results,
)
from experiments.phase3_module_marginal_budget_v1.curve_sweep import (
    build_curve_sweep_plan,
    build_module_curve,
    build_seed_placeholder_sweep_manifest,
)
from experiments.phase3_module_marginal_budget_v1.preflight import (
    DEFAULT_MANIFEST,
    fixed_projection_preflight,
    verify_frozen_manifest,
)
from experiments.phase3_module_marginal_budget_v1.configs import (
    candidates_from_baseline,
    make_baseline,
    make_single_module_candidate,
)
from experiments.phase3_module_marginal_budget_v1.parameterization import (
    assert_storage_contract,
    build_private_store,
)
from experiments.phase3_module_marginal_budget_v1.results import (
    build_curve_result,
    curve_result_template,
    marginal_value,
    result_template,
)
from experiments.phase3_module_marginal_budget_v1.smoke import run

NINE_POINT_CAPACITIES = {
    "vision": [194, 255, 336, 442, 582, 766, 1008, 1327, 1746],
    "projector": [776, 1021, 1343, 1768, 2327, 3063, 4030, 5304, 6981],
    "language": [396, 521, 685, 902, 1187, 1562, 2056, 2706, 3561],
}


def test_arbitrary_dimensions_construct_private_unshared_coordinates():
    dimensions = {"vision": 2, "projector": 7, "language": 3}
    baseline = make_baseline("baseline", dimensions, 43101)
    store = build_private_store(baseline.coordinate_dimensions)
    assert store.dimensions == dimensions
    assert_storage_contract(store)
    parameters = [store.for_module(name) for name in dimensions]
    assert len({id(parameter) for parameter in parameters}) == 3
    assert len({p.untyped_storage().data_ptr() for p in parameters}) == 3
    assert run(dimensions, 1)["frozen_parameters_unchanged"] is True


def test_each_candidate_changes_only_its_declared_module():
    baseline = make_baseline("b", {"vision": 2, "projector": 7, "language": 3}, 43101)
    candidates = candidates_from_baseline(
        baseline, {"vision": 1, "projector": 2, "language": 4}
    )
    for module, candidate in candidates.items():
        for other in baseline.dimensions:
            expected = (
                baseline.dimensions[other]
                + {"vision": 1, "projector": 2, "language": 4}[other]
                if other == module
                else baseline.dimensions[other]
            )
            assert candidate.dimensions[other] == expected
        assert candidate.projection_seed == baseline.projection_seed
    with pytest.raises(ValueError, match="increase"):
        make_single_module_candidate(
            baseline, "vision", baseline.dimensions["vision"], config_id="bad"
        )


def test_module_bits_sum_round_trip_and_result_schema():
    baseline = make_baseline("b", {"vision": 2, "projector": 7, "language": 3}, 43101)
    candidate = make_single_module_candidate(
        baseline, "vision", 4, config_id="b+vision"
    )
    coordinates = {
        name: torch.linspace(-1, 1, dimension)
        for name, dimension in candidate.dimensions.items()
    }
    archives, receipt = encode_coordinates(coordinates)
    assert (
        sum(receipt["module_wise_encoded_bits"].values())
        == receipt["total_encoded_bits"]
    )
    decoded = assert_round_trip(archives)
    assert {name: value.numel() for name, value in decoded.items()} == dict(
        candidate.dimensions
    )
    target = build_private_store(candidate.dimensions)
    loaded = load_decoded_coordinates(target, archives)
    assert all(
        torch.equal(target.coordinates[name].detach(), loaded[name])
        for name in candidate.dimensions
    )
    template = result_template(baseline, candidate)
    assert template["candidate_module"] == "vision"
    required = {
        "baseline_config",
        "candidate_module",
        "coordinate_dimensions",
        "module_wise_encoded_bits",
        "total_encoded_bits",
        "evaluation_role",
        "development_task_risk",
        "semantic_risk_bound",
        "delta_risk",
        "delta_encoded_bits",
        "marginal_value",
    }
    assert required <= template.keys()

    baseline_receipt = {
        "module_wise_encoded_bits": {
            "vision": receipt["module_wise_encoded_bits"]["vision"] - 8,
            "projector": receipt["module_wise_encoded_bits"]["projector"],
            "language": receipt["module_wise_encoded_bits"]["language"],
        },
        "total_encoded_bits": receipt["total_encoded_bits"] - 8,
    }
    value = marginal_value(
        baseline_risk=0.7,
        candidate_risk=0.6,
        baseline_encoding=baseline_receipt,
        candidate_encoding=receipt,
    )
    assert value["delta_encoded_bits"] == 8
    assert value["delta_risk"] == pytest.approx(0.1)
    assert value["marginal_value"] == pytest.approx(0.1 / 8)


def test_p4096_anchor_and_three_curve_plan_are_authoritative_and_deduplicated():
    authority = resolve_p4096_anchor()
    anchor = authority["coordinate_dimensions"]
    assert authority["anchor_id"] == "P-4096"
    assert anchor == {"vision": 582, "projector": 2327, "language": 1187}
    capacity_points = {
        "vision": [anchor["vision"] - 1, anchor["vision"], anchor["vision"] + 2],
        "projector": [
            anchor["projector"] - 2,
            anchor["projector"],
            anchor["projector"] + 3,
        ],
        "language": [
            anchor["language"] - 3,
            anchor["language"],
            anchor["language"] + 4,
        ],
    }
    plan = build_curve_sweep_plan(capacity_points, seed=43101, anchor_config=authority)
    anchor_id = plan["configs"][0]["config_id"]
    assert sum(row["is_anchor"] for row in plan["configs"]) == 1
    assert all(
        sum(point["config_id"] == anchor_id for point in curve) == 1
        for curve in plan["curves"].values()
    )
    assert len(plan["configs"]) == 7
    assert plan["curve_names"] == {
        "vision": "R_V",
        "projector": "R_C",
        "language": "R_L",
    }
    required = {
        "curve_name",
        "target_module",
        "anchor_config",
        "coordinate_dimensions",
        "sweep_index",
        "seed",
        "config_id",
    }
    assert all(required <= row.keys() for row in plan["configs"])
    assert all(
        required <= point.keys() for curve in plan["curves"].values() for point in curve
    )
    for module, curve in plan["curves"].items():
        assert [point["sweep_index"] for point in curve] == [0, 1, 2]
        for point in curve:
            config = next(
                row for row in plan["configs"] if row["config_id"] == point["config_id"]
            )
            dimensions = config["coordinate_dimensions"]
            for other in anchor:
                if other != module:
                    assert dimensions[other] == anchor[other]
            assert dimensions[module] == capacity_points[module][point["sweep_index"]]


def test_single_curve_interface_requires_the_authoritative_common_anchor():
    authority = resolve_p4096_anchor()
    anchor = authority["coordinate_dimensions"]
    points = build_module_curve(
        anchor_config=authority,
        target_module="projector",
        capacity_points=[
            anchor["projector"] - 1,
            anchor["projector"],
            anchor["projector"] + 1,
        ],
        seed=43101,
    )
    assert [point["curve_name"] for point in points] == ["R_C"] * 3
    assert all(
        point["coordinate_dimensions"]["vision"] == anchor["vision"]
        and point["coordinate_dimensions"]["language"] == anchor["language"]
        for point in points
    )
    with pytest.raises(ValueError, match="authoritative frozen P-4096"):
        build_module_curve(
            anchor_config={**anchor, "vision": anchor["vision"] + 1},
            target_module="projector",
            capacity_points=[anchor["projector"]],
            seed=43101,
        )


def _encoding_receipt(*, vision_bits, projector_bits=200, language_bits=300):
    module_bits = {
        "vision": vision_bits,
        "projector": projector_bits,
        "language": language_bits,
    }
    return {
        "module_wise_encoded_bits": module_bits,
        **{f"{module}_encoded_bits": bits for module, bits in module_bits.items()},
        "total_encoded_bits": sum(module_bits.values()),
    }


def _completed(point, *, vision_bits, risk):
    return build_curve_result(
        point,
        _encoding_receipt(vision_bits=vision_bits),
        development_task_risk=risk,
        semantic_risk_bound=risk + 0.1,
        visual_gain_guardrail=0.2,
    )


def test_curve_result_records_actual_module_and_target_bits():
    anchor = resolve_p4096_anchor()["coordinate_dimensions"]
    plan = build_curve_sweep_plan(
        {
            "vision": [anchor["vision"]],
            "projector": [anchor["projector"]],
            "language": [anchor["language"]],
        },
        seed=43101,
    )
    point = plan["curves"]["projector"][0]
    template = curve_result_template(point)
    assert template["target_module_encoded_bits"] is None
    result = build_curve_result(
        point,
        _encoding_receipt(vision_bits=100, projector_bits=250, language_bits=300),
        development_task_risk=0.7,
        semantic_risk_bound=0.8,
        visual_gain_guardrail=0.1,
    )
    assert result["target_module"] == "projector"
    assert result["target_module_encoded_bits"] == 250
    assert result["total_encoded_bits"] == 650
    assert sum(result["module_wise_encoded_bits"].values()) == 650


def test_curve_results_sort_by_actual_bits_and_compute_adjacent_values():
    anchor = resolve_p4096_anchor()["coordinate_dimensions"]
    plan = build_curve_sweep_plan(
        {
            "vision": [anchor["vision"] - 1, anchor["vision"], anchor["vision"] + 1],
            "projector": [anchor["projector"]],
            "language": [anchor["language"]],
        },
        seed=43101,
    )
    vision_members = plan["curves"]["vision"]
    inputs = [
        _completed(
            vision_members[0],
            vision_bits=120,
            risk=0.8,
        ),
        _completed(vision_members[1], vision_bits=100, risk=0.9),
        _completed(
            vision_members[2],
            vision_bits=140,
            risk=0.5,
        ),
    ]
    summary = summarize_curve_results(plan, inputs)
    curve = summary["curves"]["vision"]
    assert [point["target_module_encoded_bits"] for point in curve["points"]] == [
        100,
        120,
        140,
    ]
    assert curve["adjacent_differences"][0]["delta_risk"] == pytest.approx(-0.1)
    assert curve["adjacent_differences"][0]["delta_bits"] == 20
    assert curve["adjacent_differences"][0]["marginal_value"] == pytest.approx(0.1 / 20)
    assert curve["curve_name"] == "R_V"
    assert curve["visual_gain_role"] == "guardrail_only"


def test_curve_results_marks_nonpositive_bit_delta_and_checks_bit_sum():
    anchor = resolve_p4096_anchor()["coordinate_dimensions"]
    plan = build_curve_sweep_plan(
        {
            "vision": [anchor["vision"], anchor["vision"] + 1],
            "projector": [anchor["projector"]],
            "language": [anchor["language"]],
        },
        seed=43101,
    )
    memberships = plan["curves"]["vision"]
    inputs = [
        _completed(row, vision_bits=100, risk=0.8 - index * 0.1)
        for index, row in enumerate(memberships)
    ]
    adjacent = summarize_curve_results(plan, inputs)["curves"]["vision"][
        "adjacent_differences"
    ][0]
    assert adjacent["delta_bits"] == 0
    assert adjacent["marginal_value"] is None
    assert adjacent["status"] == "invalid_nonpositive_delta_bits"
    inputs[0]["total_encoded_bits"] += 1
    with pytest.raises(ValueError, match="do not sum"):
        summarize_curve_results(plan, inputs)


def test_nine_point_seed_placeholder_plan_has_25_unique_configs():
    plan = build_seed_placeholder_sweep_manifest(NINE_POINT_CAPACITIES)
    assert plan["protocol_version"] == PROTOCOL_VERSION
    assert plan["seed"] == SEED_PLACEHOLDER
    assert plan["distinct_config_count"] == 25
    assert plan["curve_point_membership_count"] == 27
    assert len({config["config_id"] for config in plan["configs"]}) == 25
    assert sum(config["is_anchor"] for config in plan["configs"]) == 1
    anchor_id = next(
        config["config_id"] for config in plan["configs"] if config["is_anchor"]
    )
    assert all(
        sum(point["config_id"] == anchor_id for point in curve) == 1
        for curve in plan["curves"].values()
    )
    required = {
        "curve_name",
        "target_module",
        "anchor_config",
        "coordinate_dimensions",
        "sweep_index",
        "seed",
        "config_id",
        "protocol_version",
    }
    assert all(required <= config.keys() for config in plan["configs"])
    assert all(config["seed"] == SEED_PLACEHOLDER for config in plan["configs"])


def test_fixed_projection_preflight_detects_full_coordinate_usage():
    anchor = resolve_p4096_anchor()["coordinate_dimensions"]
    receipt = fixed_projection_preflight(anchor, seeds=(43101,))
    assert receipt["all_roots_reproducible"] is True
    assert receipt["all_coordinates_used"] is True
    assert all(
        module_receipt["unused_coordinate_count"] == 0
        for module_receipt in receipt["roots"]["43101"]["module_usage"].values()
    )


def test_frozen_nine_point_manifest_covers_every_legal_config():
    digest = verify_frozen_manifest(DEFAULT_MANIFEST)
    manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    assert len(digest) == 64
    assert manifest["capacity_points"] == NINE_POINT_CAPACITIES
    assert manifest["preflight"]["status"] == "passed"
    assert manifest["preflight"]["legal_config_count"] == 25
    assert manifest["preflight"]["illegal_config_count"] == 0
    assert manifest["preflight"]["illegal_configs"] == []
    assert manifest["execution_scope"] == {
        "formal_training_executed": False,
        "risk_evaluation_executed": False,
        "formal_codec_statistics_executed": False,
    }
    assert all(
        receipt["checks"]["model_constructed"]
        and receipt["checks"]["target_dimension_legal"]
        and receipt["checks"]["unused_coordinates_absent"]
        and receipt["checks"]["non_target_modules_match_anchor"]
        and receipt["checks"]["three_module_parameters_private"]
        and receipt["checks"]["fixed_projection_reproducible"]
        and receipt["checks"]["trainable_parameter_set_matches_expected"]
        for receipt in manifest["preflight"]["results"]
    )
    assert all(
        set(receipt["checks"]["projection_roots"]) == {"43101", "43102", "43103"}
        and all(
            set(root["module_usage"]) == set(MODULES)
            for root in receipt["checks"]["projection_roots"].values()
        )
        for receipt in manifest["preflight"]["results"]
    )
