import struct
import unittest

import torch

from experiments.quantize_stage2_adapter import (
    HEADER,
    decode_mms2,
    encode_mms2,
)
from model.global_subspace_lora import GROUP_DIMENSIONS


class Stage2CodecTests(unittest.TestCase):
    def coordinates(self, group):
        return {
            name: torch.linspace(-0.75, 1.25, dimension, dtype=torch.float32)
            for name, dimension in GROUP_DIMENSIONS[group].items()
        }

    def test_every_group_round_trips_and_complexity_is_whole_file(self):
        for group, root in (("M0", 43101), ("M1", None), ("M2", 43102), ("M3", 43103)):
            archive, encoded = encode_mms2(self.coordinates(group), group, root)
            decoded, receipt = decode_mms2(archive)
            self.assertEqual(list(decoded), list(GROUP_DIMENSIONS[group]))
            self.assertEqual(receipt["complexity_bits"], len(archive) * 8)
            self.assertEqual(encoded["complexity_bits"], len(archive) * 8)
            self.assertTrue(all(value.dtype == torch.float32 for value in decoded.values()))
            self.assertTrue(all(torch.isfinite(value).all() for value in decoded.values()))

    def test_zero_vector_has_zero_scale_and_symbol_three(self):
        archive, _ = encode_mms2({"shared": torch.zeros(4096)}, "M3", 43101)
        decoded, _ = decode_mms2(archive)
        self.assertEqual(torch.count_nonzero(decoded["shared"]).item(), 0)

    def test_corrupt_header_or_symbol_is_rejected(self):
        archive, _ = encode_mms2(self.coordinates("M0"), "M0", 43101)
        with self.assertRaises(ValueError):
            decode_mms2(b"BAD!" + archive[4:])
        with self.assertRaises(ValueError):
            decode_mms2(archive[:-1])


if __name__ == "__main__":
    unittest.main()
