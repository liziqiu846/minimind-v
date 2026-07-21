import unittest

from experiments.phase3.aggregate_by_image import visual_row_metrics


class Phase3MetricTests(unittest.TestCase):
    def test_visual_metrics_and_raw_margins(self):
        values = {
            "b_img_pos1": 0.2, "b_img_pos2": 0.4, "b_img_neg": 1.7,
            "b_none_pos1": 0.3, "b_none_pos2": 0.5, "b_none_neg": 0.9,
            "b_img_pos1_raw": 0.2, "b_img_pos2_raw": 0.4, "b_img_neg_raw": 1.7,
            "b_none_pos1_raw": 0.3, "b_none_pos2_raw": 0.5, "b_none_neg_raw": 0.9,
            "raw_image_margin": 1.4, "raw_none_margin": 0.5, "raw_visual_increment": 0.9,
        }
        row = visual_row_metrics(values)
        self.assertAlmostEqual(row["positive_brier_risk"], 0.3)
        self.assertAlmostEqual(row["positive_invariance_loss"], 0.1)
        self.assertAlmostEqual(row["visual_increment"], 0.9)
        self.assertAlmostEqual(row["visual_semantic_loss"], 3.1 / 8.0)
        self.assertTrue(0.0 <= row["visual_semantic_loss"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
