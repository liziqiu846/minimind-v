import unittest

from experiments.phase3.generate_phase3_report_v5 import pareto_models_v5, render_markdown_v5


class Phase3V5ReportTests(unittest.TestCase):
    def test_pareto_uses_raw_compression_bounds_only(self):
        rows = [
            {"model_id": "a", "compression_upper_robust_positive_raw": 1.0, "compression_upper_visual_semantic_loss_raw": 0.8},
            {"model_id": "b", "compression_upper_robust_positive_raw": 1.0, "compression_upper_visual_semantic_loss_raw": 0.7},
            {"model_id": "c", "compression_upper_robust_positive_raw": 0.9, "compression_upper_visual_semantic_loss_raw": 0.9},
        ]
        self.assertEqual(pareto_models_v5(rows), ["b", "c"])

    def test_report_discloses_post_hoc_and_avoids_visual_understanding_claim(self):
        payload = {
            "models": [{
                "model_id": "m", "empirical_robust_positive": 0.2,
                "fixed_upper_robust_positive": 0.3, "compression_upper_robust_positive_raw": 2.1,
                "empirical_visual_semantic_loss": 0.45, "fixed_upper_visual_semantic_loss": 0.55,
                "compression_upper_visual_semantic_loss_raw": 1.2,
                "empirical_visual_increment": 0.4, "certified_visual_increment_lower": -0.4,
            }],
            "pareto_models": ["m"],
        }
        text = render_markdown_v5(payload)
        self.assertIn("事后分析", text)
        self.assertIn("不足以认证", text)
        self.assertNotIn("真正理解了图像", text)


if __name__ == "__main__":
    unittest.main()
