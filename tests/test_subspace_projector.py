import unittest

import torch

from model.subspace_projector import LowDimensionalProjector


class LowDimensionalProjectorTest(unittest.TestCase):
    def test_only_requested_coordinates_are_trainable(self):
        projector = LowDimensionalProjector(8, 6, subspace_dim=10, seed=7)
        self.assertEqual(sum(p.numel() for p in projector.parameters()), 10)
        self.assertEqual(
            set(projector.state_dict()),
            {"input_projection.coordinates", "output_projection.coordinates"},
        )

    def test_seed_reconstructs_the_same_projector(self):
        inputs = torch.randn(2, 4, 8, generator=torch.Generator().manual_seed(3))
        first = LowDimensionalProjector(8, 6, subspace_dim=10, seed=7)
        second = LowDimensionalProjector(8, 6, subspace_dim=10, seed=7)
        other = LowDimensionalProjector(8, 6, subspace_dim=10, seed=8)
        self.assertTrue(torch.equal(first(inputs), second(inputs)))
        self.assertFalse(torch.equal(first(inputs), other(inputs)))

    def test_optional_normalization_offsets_are_counted(self):
        projector = LowDimensionalProjector(
            8, 6, subspace_dim=10, seed=7, train_norm=True
        )
        self.assertEqual(sum(p.numel() for p in projector.parameters()), 26)

    def test_loss_backpropagates_to_every_coordinate_vector(self):
        projector = LowDimensionalProjector(8, 6, subspace_dim=10, seed=7)
        loss = projector(torch.randn(2, 4, 8)).square().mean()
        loss.backward()
        for name, parameter in projector.named_parameters():
            self.assertIsNotNone(parameter.grad, name)
            self.assertTrue(torch.isfinite(parameter.grad).all(), name)
            self.assertGreater(parameter.grad.abs().sum().item(), 0.0, name)
