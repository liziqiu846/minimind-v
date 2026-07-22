import unittest

from experiments.phase3.statistical_bounds_v5 import (
    COMPRESSION_DELTA_TOTAL, COMPRESSION_SLOTS, FIXED_MODEL_DELTA_TOTAL,
    FIXED_MODEL_SLOTS, compression_upper_v5, definition_constant_v5, fixed_model_upper_v5,
)


class Phase3V5BoundTests(unittest.TestCase):
    def test_families_and_widths_are_fixed(self):
        robust = fixed_model_upper_v5(0.3, "robust_positive_brier_risk", 1345)
        visual = fixed_model_upper_v5(0.3, "visual_semantic_loss", 1345)
        self.assertEqual(robust["interval_width"], 2.0)
        self.assertEqual(visual["interval_width"], 1.0)
        self.assertEqual(FIXED_MODEL_SLOTS, 20)
        self.assertEqual(COMPRESSION_SLOTS, 20)
        self.assertEqual(FIXED_MODEL_DELTA_TOTAL + COMPRESSION_DELTA_TOTAL, 0.05)
        self.assertFalse(robust["simultaneous_coverage_claim"])

    def test_compression_monotonicity(self):
        small = compression_upper_v5(0.2, "visual_semantic_loss", 100, 100)
        big = compression_upper_v5(0.2, "visual_semantic_loss", 100, 200)
        more_n = compression_upper_v5(0.2, "visual_semantic_loss", 200, 100)
        self.assertGreaterEqual(big["penalty"], small["penalty"])
        self.assertLessEqual(more_n["penalty"], small["penalty"])

    def test_raw_capped_and_visual_lower_are_both_stored(self):
        bound = compression_upper_v5(0.9, "visual_semantic_loss", 2, 1000)
        self.assertGreater(bound["raw_upper_bound"], 1.0)
        self.assertEqual(bound["capped_upper_bound"], 1.0)
        self.assertIn("certified_visual_increment_lower_raw", bound)
        self.assertIn("certified_visual_increment_lower_capped", bound)

    def test_m0_definition_constant(self):
        for family in ("fixed_model", "compression"):
            bound = definition_constant_v5(0.5, "visual_semantic_loss", 1345, family=family)
            self.assertEqual(bound["raw_upper_bound"], 0.5)
            self.assertEqual(bound["capped_upper_bound"], 0.5)
            self.assertEqual(bound["certified_visual_increment_lower_raw"], 0.0)


if __name__ == "__main__":
    unittest.main()
