import unittest

from experiments.comp01_scoring import binding_margin
from experiments.comp01_whatsup import relation_from_caption


class Comp01WhatsUpTests(unittest.TestCase):
    def test_relation_parser_recognizes_only_controlled_phrase(self):
        examples = {
            "A cup to the left of a bowl": "left",
            "A cup to the right of a bowl": "right",
            "A cup in front of a bowl": "front",
            "A cup behind a bowl": "behind",
            "A cup on a table": "on",
            "A cup under a table": "under",
        }
        for caption, expected in examples.items():
            self.assertEqual(relation_from_caption(caption), expected)

    def test_relation_parser_rejects_ambiguous_or_absent_relation(self):
        with self.assertRaises(ValueError):
            relation_from_caption("A cup near a bowl")
        with self.assertRaises(ValueError):
            relation_from_caption("A cup on a table to the left of a bowl")

    def test_binding_margin_direction_and_swaps(self):
        values = (1.0, 4.0, 3.0, 2.0)
        margin = binding_margin(*values)
        self.assertEqual(margin, 2.0)
        self.assertEqual(
            binding_margin(values[1], values[0], values[3], values[2]),
            -margin,
        )
        self.assertEqual(
            binding_margin(values[2], values[3], values[0], values[1]),
            -margin,
        )
        self.assertEqual(
            binding_margin(values[3], values[2], values[1], values[0]),
            margin,
        )


if __name__ == "__main__":
    unittest.main()
