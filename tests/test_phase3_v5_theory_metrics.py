import math
import unittest

from experiments.phase3.theory_metrics_v5 import m0_row_metrics_v5, visual_row_metrics_v5


class Phase3V5TheoryMetricTests(unittest.TestCase):
    def values(self, **updates):
        values = {
            "b_img_pos1": 0.2, "b_img_pos2": 0.6, "b_img_neg": 1.0,
            "b_none_pos1": 0.4, "b_none_pos2": 0.8, "b_none_neg": 0.9,
        }
        values.update(updates)
        return values

    def test_max_identity_and_positive_margin(self):
        row = visual_row_metrics_v5(self.values())
        self.assertAlmostEqual(row["robust_positive_brier_risk"], 0.6)
        self.assertAlmostEqual(row["positive_brier_mean"] + row["positive_brier_dispersion"], 0.6)
        self.assertGreater(row["image_robust_margin"], 0.0)

    def test_equal_positive_risks_have_zero_dispersion(self):
        row = visual_row_metrics_v5(self.values(b_img_pos1=0.3, b_img_pos2=0.3))
        self.assertEqual(row["positive_brier_dispersion"], 0.0)

    def test_equal_margins_map_to_half_loss(self):
        row = visual_row_metrics_v5(self.values(
            b_img_pos1=0.0, b_img_pos2=0.0, b_img_neg=1.0,
            b_none_pos1=0.0, b_none_pos2=0.0, b_none_neg=1.0,
        ))
        self.assertEqual(row["visual_increment"], 0.0)
        self.assertEqual(row["visual_semantic_loss"], 0.5)
        self.assertFalse(row["visual_increment_success"])

    def test_visual_loss_support_endpoints(self):
        best = visual_row_metrics_v5(self.values(
            b_img_pos1=0.0, b_img_pos2=0.0, b_img_neg=2.0,
            b_none_pos1=2.0, b_none_pos2=2.0, b_none_neg=0.0,
        ))
        worst = visual_row_metrics_v5(self.values(
            b_img_pos1=2.0, b_img_pos2=2.0, b_img_neg=0.0,
            b_none_pos1=0.0, b_none_pos2=0.0, b_none_neg=2.0,
        ))
        self.assertEqual(best["visual_increment"], 4.0)
        self.assertEqual(best["visual_semantic_loss"], 0.0)
        self.assertEqual(worst["visual_increment"], -4.0)
        self.assertEqual(worst["visual_semantic_loss"], 1.0)

    def test_m0_constant_and_strict_success(self):
        row = m0_row_metrics_v5({"b_none_pos1": 0.2, "b_none_pos2": 0.4, "b_none_neg": 0.4})
        self.assertEqual(row["visual_increment"], 0.0)
        self.assertEqual(row["visual_semantic_loss"], 0.5)
        self.assertIsNone(row["image_robust_margin"])
        self.assertIsNone(row["triplet_success"])
        self.assertFalse(row["lm_triplet_success"])

    def test_invalid_or_nonfinite_inputs_fail(self):
        for invalid in (-1e-9, 2.000000001, math.nan, math.inf, -math.inf):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    visual_row_metrics_v5(self.values(b_img_pos1=invalid))


if __name__ == "__main__":
    unittest.main()
