import math
import unittest

import torch

from experiments.analyze_stage2_diagnostics import bootstrap_mean_interval
from experiments.build_stage2_dataset import candidate_rank
from experiments.evaluate_stage2_risk import pair_swap_permutation, sample_risk_bits
from experiments.stage2_environment import select_idle_a40
from trainer.train_stage2 import (
    learning_rate_at,
    permutation_for_epoch,
    permutation_sha256,
)


class Stage2ReproducibilityTests(unittest.TestCase):
    def test_epoch_permutations_and_schedule_reproduce(self):
        first = permutation_for_epoch(10000, 2026, 0)
        second = permutation_for_epoch(10000, 2026, 0)
        other = permutation_for_epoch(10000, 2026, 1)
        self.assertTrue(torch.equal(first, second))
        self.assertFalse(torch.equal(first, other))
        self.assertEqual(permutation_sha256(first), permutation_sha256(second))
        self.assertEqual(learning_rate_at(0, 1875, 0.015), 0.015)
        self.assertEqual(learning_rate_at(1874, 1875, 0.015), 0.0015)

    def test_candidate_rank_and_pair_swap_are_deterministic(self):
        digest = bytes(range(32))
        self.assertEqual(candidate_rank(2026, digest), candidate_rank(2026, digest))
        hashes = ["02" * 32, "00" * 32, "03" * 32, "01" * 32]
        permutation = pair_swap_permutation(hashes)
        self.assertEqual(permutation, (2, 3, 0, 1))
        self.assertTrue(all(permutation[permutation[index]] == index for index in range(4)))

    def test_uniform_logits_equal_random_baseline(self):
        logits = torch.zeros(2, 4, 6400)
        labels = torch.tensor([[-100, 1, 2, -100], [-100, 3, 4, 5]])
        risks, _ = sample_risk_bits(logits, labels, 0.5)
        self.assertTrue(
            torch.allclose(risks, torch.full_like(risks, math.log2(6400)), atol=1e-5)
        )

    def test_bootstrap_is_reproducible_with_frozen_pcg64_seed(self):
        import numpy as np
        units = np.linspace(-1, 1, 20)
        first = bootstrap_mean_interval(units, 100, 2028, chunk_size=17)
        second = bootstrap_mean_interval(units, 100, 2028, chunk_size=17)
        self.assertEqual(first, second)

    def test_gpu_selection_rule_uses_uuid_only_for_exact_free_memory_ties(self):
        gpus = [
            {"name": "NVIDIA A40", "uuid": "GPU-b", "memory_free_mib": 100},
            {"name": "NVIDIA A40", "uuid": "GPU-a", "memory_free_mib": 100},
            {"name": "NVIDIA A40", "uuid": "GPU-c", "memory_free_mib": 101},
        ]
        self.assertEqual(select_idle_a40(gpus, [
            {"gpu_uuid": "GPU-c"}
        ])["uuid"], "GPU-a")


if __name__ == "__main__":
    unittest.main()
