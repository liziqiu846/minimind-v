import unittest

from experiments.compute_bound_report import build_report


class BoundReportTest(unittest.TestCase):
    def setUp(self):
        self.encoding = {
            "archive_sha256": "archive",
            "decoded_checkpoint_sha256": "decoded",
        }
        self.training = {
            "run_id": "toy",
            "checkpoint_sha256": "decoded",
            "alpha_choice_bits": 0,
            "sample_count": 100,
            "vocab_size": 10,
            "risks": [{"alpha": 0.1, "mean_sample_risk_bits": 2.0}],
        }
        self.validation = {
            "checkpoint_sha256": "decoded",
            "risks": [{"alpha": 0.1, "mean_sample_risk_bits": 2.25}],
        }

    def test_report_uses_training_risk_and_keeps_validation_diagnostic(self):
        report = build_report(
            self.encoding, self.training, self.validation, 0.05, 8
        )
        row = report["bounds"][0]
        self.assertEqual(row["empirical_risk_bits"], 2.0)
        self.assertEqual(row["validation_risk_bits"], 2.25)
        self.assertAlmostEqual(row["observed_generalization_gap_bits"], 0.25)
        self.assertTrue(report["certificate_uses_training_risk_only"])

    def test_checkpoint_mismatch_is_rejected(self):
        self.training["checkpoint_sha256"] = "different"
        with self.assertRaises(ValueError):
            build_report(self.encoding, self.training, None, 0.05, 8)


if __name__ == "__main__":
    unittest.main()
