import math
import unittest

import torch

from experiments.evaluate_smoothed_risk import (
    PairedImageDataset,
    apply_image_condition,
    paired_derangement,
    paired_difference_summary,
    paired_vlm_collate_fn,
    smoothed_autoregressive_risk_bits,
    smoothed_risk_grid_bits,
)


class SmoothedRiskTest(unittest.TestCase):
    def test_image_conditions_keep_and_remove_pixels(self):
        pixels = torch.arange(3).view(3, 1)
        self.assertIs(apply_image_condition(pixels, "correct"), pixels)
        self.assertIsNone(apply_image_condition(pixels, "none"))

    def test_paired_derangement_is_fixed_point_free_and_reproducible(self):
        first = paired_derangement(10, seed=17)
        second = paired_derangement(10, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(sorted(first), list(range(10)))
        for index, donor in enumerate(first):
            self.assertNotEqual(index, donor)
            self.assertEqual(first[donor], index)

    def test_paired_derangement_rejects_odd_sample_count(self):
        with self.assertRaises(ValueError):
            paired_derangement(5, seed=17)

    def test_paired_dataset_and_collate_use_global_donors(self):
        base = [
            (torch.tensor([index]), torch.tensor([index + 10]), {"x": torch.tensor([index])})
            for index in range(4)
        ]
        permutation = (1, 0, 3, 2)
        dataset = PairedImageDataset(base, permutation)
        batch = paired_vlm_collate_fn([dataset[0], dataset[2]])
        self.assertEqual(batch[2]["x"].flatten().tolist(), [0, 2])
        self.assertEqual(batch[3]["x"].flatten().tolist(), [1, 3])

    def test_paired_difference_summary_uses_pair_as_statistical_unit(self):
        differences = torch.tensor([[1.0, 3.0, 5.0, 7.0]])
        means, standard_errors, _ = paired_difference_summary(
            differences, (1, 0, 3, 2)
        )
        self.assertAlmostEqual(means.item(), 4.0)
        self.assertAlmostEqual(standard_errors.item(), 2.0)

    def test_uniform_predictions_equal_random_guess(self):
        logits = torch.zeros(2, 4, 3)
        labels = torch.tensor(
            [[-100, 0, 1, -100], [-100, 2, -100, -100]]
        )
        risks, counts = smoothed_autoregressive_risk_bits(logits, labels, 0.2)
        self.assertEqual(counts.tolist(), [2, 1])
        self.assertTrue(
            torch.allclose(risks, torch.full((2,), math.log2(3)), atol=1e-6)
        )

    def test_prediction_smoothing_matches_manual_probability(self):
        logits = torch.tensor([[[math.log(3), 0.0], [0.0, 0.0]]])
        labels = torch.tensor([[-100, 1]])
        risks, _ = smoothed_autoregressive_risk_bits(logits, labels, 0.2)
        expected_probability = 0.8 * 0.25 + 0.2 / 2
        self.assertAlmostEqual(risks.item(), -math.log2(expected_probability), 6)

    def test_next_token_shift_and_ignore_mask(self):
        logits = torch.tensor(
            [[[20.0, -20.0], [0.0, math.log(3)], [0.0, 0.0]]]
        )
        labels = torch.tensor([[0, -100, 1]])
        risks, counts = smoothed_autoregressive_risk_bits(logits, labels, 0.2)
        self.assertEqual(counts.item(), 1)
        self.assertAlmostEqual(risks.item(), -math.log2(0.8 * 0.75 + 0.1), 6)

    def test_empty_target_is_rejected(self):
        with self.assertRaises(ValueError):
            smoothed_autoregressive_risk_bits(
                torch.zeros(1, 2, 3), torch.tensor([[-100, -100]]), 0.1
            )

    def test_alpha_grid_matches_separate_calls(self):
        logits = torch.randn(2, 4, 5, generator=torch.Generator().manual_seed(7))
        labels = torch.tensor([[-100, 1, 2, 3], [-100, 4, 0, -100]])
        grid, _ = smoothed_risk_grid_bits(logits, labels, [0.01, 0.2])
        for index, alpha in enumerate((0.01, 0.2)):
            separate, _ = smoothed_autoregressive_risk_bits(logits, labels, alpha)
            self.assertTrue(torch.allclose(grid[index], separate, atol=1e-7))


if __name__ == "__main__":
    unittest.main()
