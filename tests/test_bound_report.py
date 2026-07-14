import unittest

from experiments.compute_bound_report import build_report, decoder_registry_selection


class BoundReportTest(unittest.TestCase):
    def setUp(self):
        self.encoding = {
            "run_id": "toy",
            "archive_sha256": "archive",
            "decoded_checkpoint_sha256": "decoded",
        }
        self.training = {
            "run_id": "toy",
            "model_kind": "decoded_quantized",
            "checkpoint_sha256": "decoded",
            "image_condition": "correct",
            "model_assets": {"fixed": "assets"},
            "data_sha256": "train-data",
            "alpha_choice_bits": 0,
            "sample_count": 100,
            "vocab_size": 10,
            "risks": [{"alpha": 0.1, "mean_sample_risk_bits": 2.0}],
        }
        self.validation = {
            "run_id": "toy",
            "model_kind": "decoded_quantized",
            "checkpoint_sha256": "decoded",
            "image_condition": "correct",
            "model_assets": {"fixed": "assets"},
            "data_sha256": "validation-data",
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
        self.assertEqual(report["total_hyperparameter_bits"], 0)

    def test_checkpoint_mismatch_is_rejected(self):
        self.training["checkpoint_sha256"] = "different"
        with self.assertRaises(ValueError):
            build_report(self.encoding, self.training, None, 0.05, 8)

    def test_decoder_registry_counts_product_families(self):
        registry = {
            "families": [
                {"name": "legacy", "choice_count": 3},
                {"name": "subspace", "axes": {"dim": [1, 2], "codec": ["a", "b"]}},
            ]
        }
        count, bits = decoder_registry_selection(
            registry, {"family": "subspace", "dim": 2, "codec": "b"}
        )
        self.assertEqual((count, bits), (7, 3))

    def test_single_explicit_decoder_has_zero_selection_bits(self):
        choice = {
            "family": "fixed_subspace",
            "subspace_dim": 4096,
            "train_norm": False,
            "quantization_bits": 3,
            "codec": "zlib",
        }
        registry = {"decoders": [{"id": "primary", "choice": choice}]}
        self.assertEqual(decoder_registry_selection(registry, choice), (1, 0))

    def test_canonical_state_hash_identifies_encoded_hypothesis(self):
        self.encoding["decoded_state_sha256"] = "state"
        self.training["checkpoint_state_sha256"] = "state"
        report = build_report(self.encoding, self.training, None, 0.05, 8)
        self.assertEqual(report["decoded_state_sha256"], "state")
        self.training["checkpoint_state_sha256"] = "different"
        with self.assertRaises(ValueError):
            build_report(self.encoding, self.training, None, 0.05, 8)

    def test_wrong_image_condition_is_rejected(self):
        self.training["image_condition"] = "shuffled"
        with self.assertRaises(ValueError):
            build_report(self.encoding, self.training, None, 0.05, 8)


if __name__ == "__main__":
    unittest.main()
