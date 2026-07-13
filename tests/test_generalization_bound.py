import math
import unittest
from dataclasses import replace

from experiments.generalization_bound import (
    choice_description_bits,
    description_complexity_nats,
    finite_hypothesis_bound,
    prediction_smoothing_interval,
)


class GeneralizationBoundTest(unittest.TestCase):
    def setUp(self):
        self.interval = prediction_smoothing_interval(vocab_size=6400, alpha=0.1)

    def compute(self, risk, complexity=0.0, samples=10**18):
        return finite_hypothesis_bound(
            empirical_risk_bits=risk,
            loss_interval=self.interval,
            complexity_nats=complexity,
            independent_train_samples=samples,
            confidence_delta=0.5,
        )

    def test_interval_keeps_random_guess_and_theoretical_max_separate(self):
        self.assertAlmostEqual(self.interval.random_guess_bits, math.log2(6400))
        self.assertAlmostEqual(self.interval.upper_bits, math.log2(6400 / 0.1))

    def test_bound_can_be_below_max_but_not_beat_random_guess(self):
        result = self.compute(risk=14.0)
        self.assertFalse(result.exceeds_theoretical_max)
        self.assertFalse(result.beats_random_guess)
        self.assertLess(result.compression_upper_bound_bits, result.theoretical_max_bits)
        self.assertGreater(result.compression_upper_bound_bits, result.random_guess_bits)

    def test_bound_below_random_guess_is_nonvacuous_by_paper_baseline(self):
        result = self.compute(risk=12.0)
        self.assertFalse(result.exceeds_theoretical_max)
        self.assertTrue(result.beats_random_guess)
        self.assertGreater(result.random_guess_margin_bits, 0.0)

    def test_range_vacuous_bound_is_clipped(self):
        result = self.compute(risk=14.0, complexity=1e9, samples=1000)
        self.assertTrue(result.exceeds_theoretical_max)
        self.assertEqual(
            result.clipped_certified_upper_bits, result.theoretical_max_bits
        )

    def test_integer_sample_and_vocab_inputs_are_strict(self):
        for invalid_vocab in (6400.5, True):
            with self.assertRaises(TypeError):
                prediction_smoothing_interval(invalid_vocab, 0.1)
        for invalid_samples in (10_000.5, True):
            with self.assertRaises(TypeError):
                self.compute(risk=12.0, samples=invalid_samples)

    def test_tampered_interval_metadata_is_rejected(self):
        tampered = replace(self.interval, random_guess_bits=0.0)
        with self.assertRaises(ValueError):
            finite_hypothesis_bound(12.0, tampered, 0.0, 10_000, 0.05)

    def test_description_complexity_matches_hand_calculation(self):
        encoded_bits = 8
        hyperparameter_bits = choice_description_bits(8)
        observed = description_complexity_nats(encoded_bits, hyperparameter_bits)
        total_bits = encoded_bits + hyperparameter_bits
        expected = total_bits * math.log(2) + 2 * math.log(total_bits)
        self.assertAlmostEqual(observed, expected)

    def test_finite_bound_matches_hand_calculation(self):
        risk = 4.0
        complexity = 10.0
        samples = 100
        delta = 0.05
        result = finite_hypothesis_bound(
            risk, self.interval, complexity, samples, delta
        )
        expected_penalty = self.interval.width_bits * math.sqrt(
            (complexity + math.log(1 / delta)) / (2 * samples)
        )
        self.assertAlmostEqual(
            result.generalization_penalty_bits, expected_penalty
        )
        self.assertAlmostEqual(
            result.compression_upper_bound_bits, risk + expected_penalty
        )

    def test_invalid_smoothing_parameters_are_rejected(self):
        for invalid_alpha in (0.0, 1.0, float("nan"), float("inf")):
            with self.subTest(alpha=invalid_alpha), self.assertRaises(ValueError):
                prediction_smoothing_interval(6400, invalid_alpha)
        with self.assertRaises(TypeError):
            prediction_smoothing_interval(6400, True)

    def test_invalid_bound_values_are_rejected(self):
        invalid_cases = (
            {"empirical_risk_bits": float("nan")},
            {"empirical_risk_bits": self.interval.upper_bits + 1},
            {"complexity_nats": -1.0},
            {"complexity_nats": float("nan")},
            {"complexity_nats": float("inf")},
            {"confidence_delta": 0.0},
            {"confidence_delta": 1.0},
        )
        defaults = {
            "empirical_risk_bits": 4.0,
            "loss_interval": self.interval,
            "complexity_nats": 1.0,
            "independent_train_samples": 100,
            "confidence_delta": 0.05,
        }
        for override in invalid_cases:
            with self.subTest(override=override), self.assertRaises(ValueError):
                finite_hypothesis_bound(**(defaults | override))

    def test_invalid_description_lengths_are_rejected(self):
        for invalid_bits in (-1.0, 0.5, float("nan"), float("inf")):
            with self.subTest(bits=invalid_bits), self.assertRaises(ValueError):
                description_complexity_nats(invalid_bits)


if __name__ == "__main__":
    unittest.main()
