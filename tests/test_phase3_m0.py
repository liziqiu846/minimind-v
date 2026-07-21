import unittest

from experiments.phase3.aggregate_by_image import aggregate_rows, m0_row_metrics
from experiments.phase3.statistical_bounds import definition_constant


class Phase3M0Tests(unittest.TestCase):
    def test_null_fields_observed_language_and_visual_constant(self):
        row = m0_row_metrics({"b_none_pos1": 0.2, "b_none_pos2": 0.6, "b_none_neg": 1.0, "raw_none_margin": 0.6})
        self.assertIsNone(row["b_img_pos1"])
        self.assertIsNone(row["image_margin"])
        self.assertAlmostEqual(row["positive_brier_risk"], 0.4)
        self.assertAlmostEqual(row["positive_invariance_loss"], 0.2)
        self.assertEqual(row["visual_increment"], 0.0)
        self.assertEqual(row["visual_semantic_loss"], 0.5)
        self.assertEqual(row["visual_metric_source"], "definition_constant_lm_only")
        bound = definition_constant(0.5, 1345)
        self.assertEqual(bound["bound_method"], "definition_constant")
        self.assertEqual(bound["hoeffding_radius"], 0.0)

    def test_null_aggregation_stays_null(self):
        rows = []
        for value in (0.2, 0.4):
            rows.append({"model_id": "M0", "filename": "a.jpg", **m0_row_metrics({"b_none_pos1": value, "b_none_pos2": value, "b_none_neg": 1.0, "raw_none_margin": 1-value})})
        group = aggregate_rows(rows)[0]
        self.assertIsNone(group["b_img_pos1"])
        self.assertEqual(group["visual_semantic_loss"], 0.5)


if __name__ == "__main__":
    unittest.main()
