import unittest

import torch
from torch import nn

from model.global_subspace_lora import (
    FactorMapping,
    HashedLoRALinear,
    Stage2CoordinateStore,
    TargetSpec,
)


class GradientScopeTests(unittest.TestCase):
    def make_wrapper(self, store, name, group, offset):
        base = nn.Linear(4, 4, bias=True)
        spec = TargetSpec(group if group != "shared" else "language", name, 2, 4, 4)
        a_indices = torch.arange(8) + offset
        b_indices = torch.arange(8) + offset + 8
        return HashedLoRALinear(
            base,
            spec,
            store,
            group,
            FactorMapping(a_indices, torch.ones(8)),
            FactorMapping(b_indices, torch.ones(8)),
        )

    def test_m2_groups_receive_only_their_own_probe_gradient(self):
        store = Stage2CoordinateStore("M2")
        wrappers = {
            "vision": self.make_wrapper(store, "vision", "vision", 0),
            "projector": self.make_wrapper(store, "projector", "projector", 0),
            "language": self.make_wrapper(store, "language", "language", 0),
        }
        inputs = torch.randn(2, 4)
        for selected, wrapper in wrappers.items():
            store.zero_grad(set_to_none=True)
            wrapper(inputs).square().sum().backward()
            for group, coordinate in store.coordinates.items():
                if group == selected:
                    self.assertIsNotNone(coordinate.grad)
                    self.assertGreater(torch.count_nonzero(coordinate.grad).item(), 0)
                else:
                    self.assertIsNone(coordinate.grad)
            self.assertTrue(all(parameter.grad is None for parameter in wrapper.base.parameters()))

    def test_m3_separate_module_probes_reach_same_shared_vector(self):
        store = Stage2CoordinateStore("M3")
        wrappers = [
            self.make_wrapper(store, "vision", "shared", 0),
            self.make_wrapper(store, "projector", "shared", 32),
            self.make_wrapper(store, "language", "shared", 64),
        ]
        inputs = torch.randn(2, 4)
        supports = []
        for wrapper in wrappers:
            store.zero_grad(set_to_none=True)
            wrapper(inputs).sum().backward()
            gradient = store.coordinates["shared"].grad
            self.assertIsNotNone(gradient)
            supports.append(set(torch.nonzero(gradient).flatten().tolist()))
            self.assertTrue(all(parameter.grad is None for parameter in wrapper.base.parameters()))
        self.assertTrue(all(support for support in supports))
        self.assertTrue(supports[0].isdisjoint(supports[1]))
        self.assertTrue(supports[1].isdisjoint(supports[2]))


if __name__ == "__main__":
    unittest.main()
