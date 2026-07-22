import unittest

from experiments.phase3.runner_common import build_metrics_summary


class Phase3V5RunnerTests(unittest.TestCase):
    def test_v4_default_is_unchanged(self):
        registry = {"models": [{"model_id": "m", "method": "M1", "description_bits": 8}]}
        groups = [{
            "model_id": "m", "positive_brier_risk": 0.2,
            "visual_semantic_loss": 0.3, "positive_invariance_loss": 0.4,
        }]
        self.assertEqual(
            build_metrics_summary("smoke", ["m"], groups, registry),
            build_metrics_summary("smoke", ["m"], groups, registry, "v4"),
        )

    def test_smoke_v5_has_null_bounds(self):
        registry = {"models": [{"model_id": "m", "method": "M1", "artifact_size_bytes": 10}]}
        group = {
            "model_id": "m", "robust_positive_brier_risk": 0.2,
            "visual_semantic_loss": 0.3, "positive_brier_mean": 0.2,
            "positive_brier_dispersion": 0.0, "image_robust_margin": 0.3,
            "none_robust_margin": 0.1, "visual_increment": 0.2,
            "triplet_success": 1.0, "lm_triplet_success": 1.0,
            "visual_increment_success": 1.0,
        }
        summary = build_metrics_summary("smoke", ["m"], [group], registry, "v5")
        self.assertEqual(summary["models"][0]["fixed_model_bounds"], {
            "robust_positive_brier_risk": None, "visual_semantic_loss": None,
        })
        self.assertFalse(summary["simultaneous_coverage_claim"])

    def test_unknown_metric_version_fails(self):
        with self.assertRaises(ValueError):
            build_metrics_summary("smoke", [], [], {"models": []}, "v6")


if __name__ == "__main__":
    unittest.main()
