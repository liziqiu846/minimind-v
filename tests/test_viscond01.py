import unittest

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

    def test_prediction_tie_break_is_alphabetical(self):
        values = {"A": 1.0, "B": 1.0, "C": 2.0, "D": 3.0}
        self.assertEqual(predicted_label(values), "A")


if __name__ == "__main__":
    unittest.main()
