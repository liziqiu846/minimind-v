import hashlib
import json
import math
import struct
import unittest
from pathlib import Path

import torch
from torch import nn

from experiments.stage2_protocol import load_target_registry
from model.global_subspace_lora import (
    GROUP_DIMENSIONS,
    FactorMapping,
    HashedLoRALinear,
    Stage2CoordinateStore,
    TargetSpec,
    a0_message,
    build_factor_mappings,
    deterministic_a0,
    mapping_message,
    projector_base_receipt,
    target_specs,
)
from model.model_vlm import Stage2BaseProjector
from model.subspace_projector import LowDimensionalProjector


class GlobalSubspaceLoRATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_target_registry()

    def test_hash_message_serialization_is_length_prefixed_and_little_endian(self):
        expected = (
            struct.pack("<I", len(b"stage2-a0-v1"))
            + b"stage2-a0-v1"
            + struct.pack("<I", 1)
            + b"x"
            + struct.pack("<Q", 2)
            + struct.pack("<Q", 3)
        )
        self.assertEqual(a0_message("x", 2, 3), expected)
        message = mapping_message(43101, "x", "B", 7)
        self.assertTrue(message.startswith(struct.pack("<I", 13) + b"stage2-map-v1"))
        self.assertTrue(message.endswith(struct.pack("<Q", 7)))

    def test_a0_is_deterministic_float32_and_name_separated(self):
        left = deterministic_a0("layer.a", 4, 9)
        right = deterministic_a0("layer.a", 4, 9)
        other = deterministic_a0("layer.b", 4, 9)
        self.assertEqual(left.dtype, torch.float32)
        self.assertTrue(torch.equal(left, right))
        self.assertFalse(torch.equal(left, other))
        self.assertLessEqual(float(left.abs().max()), 1 / math.sqrt(9))

    def test_all_predeclared_mappings_use_every_coordinate(self):
        cases = {
            "M0": ("language",),
            "M2": ("vision", "projector", "language"),
            "M3": ("vision", "projector", "language"),
        }
        for group, modules in cases.items():
            specs = target_specs(self.registry, modules)
            for root in (43101, 43102, 43103):
                _, statistics = build_factor_mappings(group, root, specs)
                self.assertEqual(set(statistics), set(GROUP_DIMENSIONS[group]))
                self.assertTrue(all(row["minimum"] > 0 for row in statistics.values()))
                expected_elements = sum(spec.a_elements + spec.b_elements for spec in specs)
                observed = sum(
                    row["mean"] * row["dimension"] for row in statistics.values()
                )
                self.assertAlmostEqual(observed, expected_elements)

    def test_m3_count_normalization_is_one_global_scope(self):
        specs = target_specs(self.registry, ("vision", "projector", "language"))
        _, statistics = build_factor_mappings("M3", 43101, specs)
        self.assertEqual(list(statistics), ["shared"])
        self.assertEqual(statistics["shared"]["mean"], 173056 / 4096)

    def test_zero_coordinate_wrapper_is_exact_base_and_has_gradient(self):
        torch.manual_seed(7)
        base = nn.Linear(5, 3)
        store = Stage2CoordinateStore("M3")
        spec = TargetSpec("language", "toy", 2, 5, 3)
        a_indices = torch.arange(10) % 4096
        b_indices = torch.arange(6) + 10
        wrapper = HashedLoRALinear(
            base,
            spec,
            store,
            "shared",
            FactorMapping(a_indices, torch.ones(10)),
            FactorMapping(b_indices, torch.ones(6)),
        )
        inputs = torch.randn(4, 5)
        self.assertTrue(torch.equal(wrapper(inputs), base(inputs)))
        wrapper(inputs).sum().backward()
        self.assertIsNotNone(store.coordinates["shared"].grad)
        self.assertGreater(torch.count_nonzero(store.coordinates["shared"].grad).item(), 0)
        self.assertIsNone(base.weight.grad)
        self.assertIsNone(base.bias.grad)

    def test_projector_base_is_identical_to_m1(self):
        m1 = LowDimensionalProjector(768, 768, 4096, 42, False).eval()
        stage2 = Stage2BaseProjector(768, 768, 42).eval()
        inputs = torch.linspace(-1, 1, 2 * 3 * 768, dtype=torch.float32).view(2, 3, 768)
        with torch.no_grad():
            self.assertTrue(torch.allclose(m1(inputs), stage2(inputs), rtol=0, atol=1e-6))

        class Holder(nn.Module):
            def __init__(self, projector):
                super().__init__()
                self.vision_proj = projector

        self.assertEqual(
            projector_base_receipt(Holder(m1)),
            projector_base_receipt(Holder(stage2)),
        )


if __name__ == "__main__":
    unittest.main()
