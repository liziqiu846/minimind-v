import unittest

import torch

from experiments.phase3.brier_metrics import explicit_one_hot_brier, shifted_valid_positions, token_brier


class Phase3BrierTests(unittest.TestCase):
    def test_optimized_matches_explicit_and_range_cases(self):
        torch.manual_seed(3)
        logits = torch.randn(4, 6, 9)
        labels = torch.tensor([[-100, 1, 2, -100, 4, 5]] * 4)
        actual = token_brier(logits, labels)["caption_brier_raw"]
        expected = explicit_one_hot_brier(logits, labels)
        self.assertTrue(torch.allclose(actual, expected, atol=1e-7, rtol=1e-7))

        uniform = token_brier(torch.zeros(1, 2, 4), torch.tensor([[-100, 2]]))["caption_brier_raw"].item()
        self.assertAlmostEqual(uniform, 0.75)
        perfect = torch.tensor([[[0.0, 0.0], [-100.0, 100.0]]])
        # Position zero predicts label at position one.
        perfect[:, 0] = torch.tensor([-100.0, 100.0])
        self.assertAlmostEqual(token_brier(perfect, torch.tensor([[-100, 1]]))["caption_brier_raw"].item(), 0.0, places=6)
        wrong = torch.tensor([[[100.0, -100.0], [0.0, 0.0]]])
        self.assertAlmostEqual(token_brier(wrong, torch.tensor([[-100, 1]]))["caption_brier_raw"].item(), 2.0, places=6)

    def test_causal_shift_masks_and_zero_valid_rejected(self):
        logits = torch.randn(1, 4, 5)
        labels = torch.tensor([[4, -100, 3, -100]])
        _, shifted, mask, safe, counts = shifted_valid_positions(logits, labels)
        self.assertEqual(shifted.tolist(), [[-100, 3, -100]])
        self.assertEqual(mask.tolist(), [[False, True, False]])
        self.assertEqual(safe.tolist(), [[0, 3, 0]])
        self.assertEqual(counts.tolist(), [1])
        with self.assertRaises(ValueError):
            shifted_valid_positions(logits, torch.full((1, 4), -100))


if __name__ == "__main__":
    unittest.main()
