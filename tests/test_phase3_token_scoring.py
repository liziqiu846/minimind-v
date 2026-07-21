import math
import unittest
from types import SimpleNamespace

import torch

from experiments.evaluate_stage2_risk import sample_risk_bits
from experiments.phase3.caption_scorer import score_tokenized_batch, smoothed_nll_bits, token_nll_bits


class _Model:
    def __init__(self, logits):
        self.logits = logits
        self.kwargs = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(logits=self.logits)


class Phase3TokenScoringTests(unittest.TestCase):
    def test_nll_and_stage2_smoothed_parity(self):
        torch.manual_seed(7)
        logits = torch.randn(2, 5, 11)
        labels = torch.tensor([[-100, 1, 2, -100, 4], [-100, -100, 3, 2, 1]])
        new, counts = smoothed_nll_bits(logits, labels, 0.5)
        old, old_counts = sample_risk_bits(logits, labels, 0.5)
        self.assertTrue(torch.allclose(new, old, atol=1e-7, rtol=1e-7))
        self.assertTrue(torch.equal(counts, old_counts))
        raw = token_nll_bits(logits, labels)
        self.assertEqual([len(row) for row in raw], counts.tolist())
        self.assertTrue(all(torch.isfinite(row).all() for row in raw))

    def test_attention_mask_is_forbidden(self):
        logits = torch.zeros(1, 2, 3)
        labels = torch.tensor([[-100, 1]])
        with self.assertRaises(ValueError):
            score_tokenized_batch(_Model(logits), torch.ones(1, 2, dtype=torch.long), labels, None, torch.ones(1, 2))
        model = _Model(logits)
        score_tokenized_batch(model, torch.ones(1, 2, dtype=torch.long), labels, None)
        self.assertIn("attention_mask", model.kwargs)
        self.assertIsNone(model.kwargs["attention_mask"])


if __name__ == "__main__":
    unittest.main()
