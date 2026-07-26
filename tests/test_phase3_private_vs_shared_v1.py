import json
import math
import random

import pytest
import torch

from experiments.phase3_private_vs_shared_v1.aggregate import aggregate_models
from experiments.phase3_private_vs_shared_v1.certificates import (
    semantic_certificate, symmetric_pair_gain, visual_gain_certificate,
)
from experiments.phase3_private_vs_shared_v1.complexity import (
    bits_to_nats, confirmation_selection_bits, training_certificate_bits,
)
from experiments.phase3_private_vs_shared_v1.configs import (
    generate_matrix, private_allocation, validate_matrix,
)
from experiments.phase3_private_vs_shared_v1.confirmation import (
    disjoint_pairs, validate_confirmation_manifest,
)
from experiments.phase3_private_vs_shared_v1.parameterization import (
    CoordinateStore, ProjectedUpdate, assert_storage_contract,
)
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    validate_frozen_protocol,
)
from experiments.phase3_private_vs_shared_v1.smoke import run


def test_matrix_complete_unique_and_allocations_are_authoritative():
    configs = generate_matrix()
    validate_matrix(configs)
    assert len(configs) == len({item["config_id"] for item in configs}) == 18
    assert private_allocation(2048) == {
        "vision": 291, "projector": 1163, "language": 594
    }
    assert private_allocation(4096) == {
        "vision": 582, "projector": 2327, "language": 1187
    }
    assert private_allocation(8192) == {
        "vision": 1163, "projector": 4654, "language": 2375
    }
    assert all(sum(item["coordinate_dimensions"].values()) == item["budget"]
               for item in configs)
    assert validate_frozen_protocol()


def test_storage_and_module_specific_shared_projections():
    private = CoordinateStore("P", {"vision": 2, "projector": 3, "language": 4})
    shared = CoordinateStore("S", {"shared": 4})
    assert_storage_contract(private)
    assert_storage_contract(shared)
    assert private.free_parameter_count == 9
    assert shared.free_parameter_count == 4
    assert len({p.untyped_storage().data_ptr() for p in private.unique_parameters()}) == 3
    assert shared.for_module("vision") is shared.for_module("language")
    with torch.no_grad():
        shared.coordinates["shared"].copy_(torch.tensor([1., 2., 3., 4.]))
    vision = ProjectedUpdate(shared, "vision", torch.eye(4))
    language = ProjectedUpdate(shared, "language", torch.ones(2, 4))
    assert vision().shape == (4,)
    assert language().shape == (2,)
    assert not torch.equal(vision()[:2], language())
    assert list(shared.state_dict()) == ["coordinates.shared"]


def test_bit_accounting_once_and_exact_log2_18():
    private = CoordinateStore("P", {"vision": 2, "projector": 3, "language": 4})
    shared = CoordinateStore("S", {"shared": 9})
    p = training_certificate_bits(
        private, encoded_parameter_bits={"vision": 10, "projector": 11, "language": 12}
    )
    s = training_certificate_bits(shared, encoded_parameter_bits={"shared": 30})
    selection = confirmation_selection_bits()
    assert p["parameter_bits"] == 33
    assert s["parameter_bits"] == 30
    assert p["seed_integer_bits"] == s["seed_integer_bits"] == 0
    assert p["candidate_identity_bits"] == 0
    assert selection["coded_bits"] == math.log2(18)
    assert selection["training_certificate_bits_recharged"] == 0
    assert selection["checkpoint_bits"] == selection["seed_integer_bits"] == 0
    assert selection["coded_nats_for_natural_log_formula"] == pytest.approx(
        math.log(18)
    )
    assert bits_to_nats(7) == pytest.approx(7 * math.log(2))
    with pytest.raises(ValueError):
        training_certificate_bits(shared, encoded_parameter_bits={
            "shared": 30, "shared_copy": 30
        })


def test_confirmation_manifest_and_disjoint_pairing(tmp_path):
    records = [
        {"sample_id": f"s{i}", "image": f"{i}.jpg", "text": f"text {i}"}
        for i in range(6)
    ]
    path = tmp_path / "fresh.json"
    path.write_text(json.dumps({
        "purpose": "fresh_final_confirmation", "records": records
    }), encoding="utf-8")
    receipt = validate_confirmation_manifest(path)
    pairing = disjoint_pairs(receipt["records"], 3407)
    pairs = pairing["pairs"]
    members = [
        sample_id for row in pairs
        for sample_id in (row["first_sample_id"], row["second_sample_id"])
    ]
    assert len(members) == len(set(members)) == 6
    assert all(row["first_sample_id"] != row["second_sample_id"] for row in pairs)
    assert all(
        row["first_direction"]["mismatch_donor_sample_id"]
        == row["second_sample_id"]
        and row["second_direction"]["mismatch_donor_sample_id"]
        == row["first_sample_id"]
        for row in pairs
    )
    assert pairing == disjoint_pairs(receipt["records"], 3407)
    assert pairing["permutation_sha256"]
    assert pairing["pair_manifest_sha256"]
    with pytest.raises(ValueError, match="requires --confirmation-manifest"):
        validate_confirmation_manifest(None)
    odd = disjoint_pairs(records[:-1], 3407)
    expected_indices = list(range(5))
    random.Random(3407).shuffle(expected_indices)
    assert odd["dropped_sample_id"] == records[expected_indices[-1]]["sample_id"]
    assert odd["permutation_sample_ids"][-1] == odd["dropped_sample_id"]
    assert len(odd["pairs"]) == 2
    odd_members = {
        sample_id for row in odd["pairs"]
        for sample_id in (row["first_sample_id"], row["second_sample_id"])
    }
    assert odd["dropped_sample_id"] not in odd_members
    with pytest.raises(ValueError, match="development"):
        validate_confirmation_manifest(path, forbidden_hashes=[
            receipt["manifest_sha256"]
        ])


def test_metric_ranges_bounds_aggregation_and_smoke():
    assert symmetric_pair_gain(0.8, 0.2, 0.6, 0.4) == pytest.approx(0.4)
    assert symmetric_pair_gain(0.6, 0.4, 0.8, 0.2) == pytest.approx(0.4)
    assert symmetric_pair_gain(1.0, 0.0, 1.0, 0.0) == 1.0
    assert symmetric_pair_gain(0.0, 1.0, 0.0, 1.0) == -1.0
    visual = visual_gain_certificate(
        [0.8, 0.6], [0.2, 0.4], [0.6, 0.9], [0.4, 0.3], 0.05
    )
    assert visual["empirical_visual_gain"] == pytest.approx(0.4)
    assert -1 <= visual["visual_gain_lower_bound"] <= 1
    with pytest.raises(ValueError, match=r"outside \[0,1\]"):
        visual_gain_certificate([1.01], [0.2], [0.8], [0.3], 0.05)
    semantic = semantic_certificate(0.5, 100, math.log2(18), 0.05)
    assert semantic["semantic_bound"] > semantic["empirical_risk"]
    assert semantic["bit_to_nat_multiplier"] == math.log(2)
    configs = generate_matrix()
    rows = aggregate_models(configs, {
        configs[0]["config_id"]: {
            **semantic,
            "visual_gain_lower_bound": visual["visual_gain_lower_bound"],
            "training_status": "smoke_only",
        }
    })
    assert list(rows[0]) == [
        "structure", "budget", "seed", "semantic_bound",
        "visual_gain_lower_bound", "coded_bits", "training_status",
    ]
    assert run("P", 2)["status"] == run("S", 2)["status"] == "passed"
    with pytest.raises(ValueError, match="limited"):
        run("P", 3)


def test_new_experiment_does_not_import_or_restore_legacy_m4():
    from pathlib import Path
    root = Path("experiments/phase3_private_vs_shared_v1")
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in root.glob("*.py")
    ).lower()
    assert "phase3_m4" not in source
    assert "m4_" not in source
    assert "restore" not in source
