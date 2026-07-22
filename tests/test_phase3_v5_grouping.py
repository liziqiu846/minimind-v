import unittest

from experiments.phase3.theory_metrics_v5 import aggregate_category_rows_v5, aggregate_rows_v5


def row(model, filename, category, value, index):
    return {
        "schema_version": 1, "model_id": model, "filename": filename,
        "category": category, "row_index": index,
        "robust_positive_brier_risk": value,
        "visual_semantic_loss": value / 2,
        "positive_brier_mean": value, "positive_brier_dispersion": 0.0,
        "image_robust_margin": value, "none_robust_margin": 0.0,
        "visual_increment": value, "triplet_success": True,
        "lm_triplet_success": False, "visual_increment_success": True,
    }


class Phase3V5GroupingTests(unittest.TestCase):
    def test_within_image_then_equal_image_weight(self):
        rows = [
            row("m", "a.jpg", "replace_object", 0.0, 0),
            row("m", "a.jpg", "replace_object", 2.0, 1),
            row("m", "b.jpg", "replace_object", 2.0, 2),
        ]
        groups = aggregate_rows_v5(rows)
        self.assertEqual([group["filename"] for group in groups], ["a.jpg", "b.jpg"])
        self.assertEqual(groups[0]["robust_positive_brier_risk"], 1.0)
        self.assertEqual(sum(group["robust_positive_brier_risk"] for group in groups) / 2, 1.5)

    def test_deterministic_model_filename_sort(self):
        groups = aggregate_rows_v5([
            row("z", "b.jpg", "replace_object", 1.0, 0),
            row("a", "c.jpg", "replace_object", 1.0, 1),
            row("a", "a.jpg", "replace_object", 1.0, 2),
        ])
        self.assertEqual([(x["model_id"], x["filename"]) for x in groups], [("a", "a.jpg"), ("a", "c.jpg"), ("z", "b.jpg")])

    def test_category_aggregation_does_not_mix_categories(self):
        result = aggregate_category_rows_v5([
            row("m", "a.jpg", "replace_object", 1.0, 0),
            row("m", "a.jpg", "replace_relation", 0.5, 1),
        ])
        self.assertEqual([x["category"] for x in result], ["replace_object", "replace_relation"])

    def test_partial_null_fails(self):
        rows = [row("m", "a.jpg", "replace_object", 1.0, 0), row("m", "a.jpg", "replace_object", 1.0, 1)]
        rows[0]["image_robust_margin"] = None
        with self.assertRaises(ValueError):
            aggregate_rows_v5(rows)


if __name__ == "__main__":
    unittest.main()
