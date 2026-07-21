import math
import unittest

from experiments.phase3.statistical_bounds import (
    DELTA_COMPRESSION_EACH, DELTA_MAIN_EACH, compression_upper, hoeffding_upper,
)


class Phase3BoundTests(unittest.TestCase):
    def test_hoeffding_uses_natural_log(self):
        bound = hoeffding_upper(0.4, 0.0, 2.0, 1345)
        expected = 2.0 * math.sqrt(math.log(1.0 / DELTA_MAIN_EACH) / (2.0 * 1345))
        self.assertAlmostEqual(bound["hoeffding_radius"], expected)
        self.assertEqual(bound["bound_method"], "hoeffding_iid_superpopulation")

    def test_main_and_compression_delta_families_are_separate(self):
        main = hoeffding_upper(0.4, 0.0, 2.0, 1345)
        exploratory = compression_upper(0.4, 0.0, 2.0, 1345, 6408)
        self.assertEqual(main["delta_family"], "main")
        self.assertEqual(exploratory["delta_family"], "compression")
        self.assertEqual(main["delta_each"], DELTA_MAIN_EACH)
        self.assertEqual(exploratory["delta_each"], DELTA_COMPRESSION_EACH)


if __name__ == "__main__":
    unittest.main()
