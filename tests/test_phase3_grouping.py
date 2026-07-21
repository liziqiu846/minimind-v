import unittest

from experiments.phase3.aggregate_by_image import aggregate_rows, empirical_metric_means


class Phase3GroupingTests(unittest.TestCase):
    def test_rows_average_within_filename_before_global_mean(self):
        rows = [
            {"model_id": "M", "filename": "a", "positive_brier_risk": 0.0, "visual_semantic_loss": 0.0, "positive_invariance_loss": 0.0},
            {"model_id": "M", "filename": "a", "positive_brier_risk": 2.0, "visual_semantic_loss": 1.0, "positive_invariance_loss": 1.0},
            {"model_id": "M", "filename": "b", "positive_brier_risk": 2.0, "visual_semantic_loss": 0.5, "positive_invariance_loss": 0.5},
        ]
        groups = aggregate_rows(rows)
        self.assertEqual([row["row_count"] for row in groups], [2, 1])
        means = empirical_metric_means(groups)
        self.assertAlmostEqual(means["positive_brier_risk"], 1.5)
        self.assertAlmostEqual(means["visual_semantic_loss"], 0.5)


if __name__ == "__main__":
    unittest.main()
