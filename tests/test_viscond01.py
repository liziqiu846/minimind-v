import unittest

from experiments.analyze_viscond01 import paired_bootstrap_delta
from experiments.viscond01 import (
    answer_margin,
    extract_option_labels,
    predicted_label,
    visual_increment,
)


class Viscond01Tests(unittest.TestCase):
    def test_option_parser_requires_A_through_D_in_order(self):
        question = (
            "Which object is shown?\n"
            "Options: A: cat, B: dog, C: bird, D: fish"
        )
        self.assertEqual(
            extract_option_labels(question),
            ("A", "B", "C", "D"),
        )
        parenthesized = (
            "Question: Which object?\nChoices:\n"
            "(A) cat\n(B) dog\n(C) bird\n(D)fish"
        )
        self.assertEqual(
            extract_option_labels(parenthesized),
            ("A", "B", "C", "D"),
        )
        with self.assertRaises(ValueError):
            extract_option_labels(
                "Which object?\nOptions: A: cat, B: dog, D: fish"
            )

    def test_margin_and_visual_increment_direction(self):
        correct = {"A": 1.0, "B": 4.0, "C": 3.0, "D": 2.0}
        no_pixel = {"A": 2.0, "B": 3.0, "C": 3.0, "D": 2.0}
        self.assertAlmostEqual(answer_margin(correct, "A"), 2.0)
        self.assertAlmostEqual(answer_margin(no_pixel, "A"), 2.0 / 3.0)
        self.assertAlmostEqual(
            visual_increment(correct, no_pixel, "A"),
            4.0 / 3.0,
        )
        self.assertEqual(predicted_label(correct), "A")

    def test_identical_grids_have_zero_visual_increment(self):
        grid = {"A": 1.25, "B": 2.5, "C": 0.75, "D": 4.0}
        self.assertAlmostEqual(visual_increment(grid, grid, "C"), 0.0)

    def test_margin_is_invariant_to_joint_label_permutation(self):
        original = {"A": 1.0, "B": 4.0, "C": 3.0, "D": 2.0}
        gold = "B"
        permutation = {"A": "D", "B": "C", "C": "A", "D": "B"}
        permuted = {
            permutation[label]: value for label, value in original.items()
        }
        self.assertAlmostEqual(
            answer_margin(original, gold),
            answer_margin(permuted, permutation[gold]),
        )

    def test_prediction_tie_break_is_alphabetical(self):
        values = {"A": 1.0, "B": 1.0, "C": 2.0, "D": 3.0}
        self.assertEqual(predicted_label(values), "A")

    def test_pair_bootstrap_aggregates_repeated_images_before_delta(self):
        m2 = [
            {
                "normalized_pixel_sha256": "x",
                "visual_increment_bits_per_token": 1.0,
            },
            {
                "normalized_pixel_sha256": "x",
                "visual_increment_bits_per_token": 3.0,
            },
            {
                "normalized_pixel_sha256": "y",
                "visual_increment_bits_per_token": 2.0,
            },
        ]
        m3 = [
            {
                "normalized_pixel_sha256": "x",
                "visual_increment_bits_per_token": 2.0,
            },
            {
                "normalized_pixel_sha256": "x",
                "visual_increment_bits_per_token": 4.0,
            },
            {
                "normalized_pixel_sha256": "y",
                "visual_increment_bits_per_token": 3.0,
            },
        ]
        result = paired_bootstrap_delta(m2, m3)
        self.assertEqual(result["group_count"], 2)
        self.assertAlmostEqual(result["delta_V_bits_per_token"], 1.0)


if __name__ == "__main__":
    unittest.main()
