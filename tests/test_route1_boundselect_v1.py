from __future__ import annotations

import copy
import unittest
from decimal import Decimal

from experiments.route1_boundselect_v1.selector import select_candidate


def _candidate(identifier: str, bound: str, *, baseline: bool = False) -> dict:
    return {
        "candidate_id": identifier,
        "structure": identifier.split("-")[0],
        "structure_description": "test",
        "budget": {"total_coordinate_budget": 1, "allocation": {"x": 1}},
        "actual_encoded_bits": 8,
        "raw_full_compression_bound": Decimal(bound),
        "provenance": {},
        "checkpoint": {},
        "training_checkpoint": {},
        "encoded_model": {},
        "raw_bound_source": {},
        "actual_bits_source": {},
        "heldout_evaluation": {
            "path": "/not/read/by/selector",
            "sha256": "0" * 64,
            "role": "decoded_quantized_validation_correct",
            "sample_count": 1,
            "value_in_registry": False,
        },
        "baseline": baseline,
        "baseline_reason": "test" if baseline else None,
        "eligibility": {"eligible": True},
    }


def _registry() -> dict:
    allowed = list(_candidate("a", "1").keys())
    return {
        "schema_version": 1,
        "protocol_id": "route1-boundselect-v1",
        "status": "frozen_before_selection",
        "candidate_count": 3,
        "baseline": {"candidate_id": "base"},
        "leakage_control": {
            "registry_contains_heldout_risk_values": False,
            "selector_allowed_candidate_fields": allowed,
        },
        "candidates": [
            _candidate("base", "2.0", baseline=True),
            _candidate("winner", "1.0"),
            _candidate("other", "3.0"),
        ],
    }


class BoundSelectTests(unittest.TestCase):
    def test_unique_minimum_uses_only_raw_bound(self) -> None:
        result = select_candidate(_registry())
        self.assertEqual(result["selected"]["candidate_id"], "winner")
        self.assertEqual(result["baseline"]["candidate_id"], "base")

    def test_exact_tie_fails(self) -> None:
        registry = _registry()
        registry["candidates"][2]["raw_full_compression_bound"] = Decimal(
            "1.0"
        )
        with self.assertRaisesRegex(ValueError, "exactly tied"):
            select_candidate(registry)

    def test_heldout_value_in_registry_fails(self) -> None:
        registry = _registry()
        registry["candidates"][0]["heldout_evaluation"][
            "value_in_registry"
        ] = True
        with self.assertRaisesRegex(ValueError, "held-out value"):
            select_candidate(registry)

    def test_baseline_must_be_unique(self) -> None:
        registry = copy.deepcopy(_registry())
        registry["candidates"][1]["baseline"] = True
        with self.assertRaisesRegex(ValueError, "baseline is not unique"):
            select_candidate(registry)


if __name__ == "__main__":
    unittest.main()
