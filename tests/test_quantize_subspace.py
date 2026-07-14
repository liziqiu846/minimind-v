import unittest

import torch

from experiments.quantize_subspace import (
    decode_compact,
    decode_entropy,
    encode_compact,
    encode_entropy,
)


class CompactSubspaceCodecTest(unittest.TestCase):
    def test_two_coordinate_vectors_round_trip(self):
        names = ("first", "second")
        spec = ((names[0], 8), (names[1], 8))
        trained = {
            names[0]: torch.linspace(-1.0, 1.0, 8),
            names[1]: torch.linspace(-0.5, 0.5, 8),
        }
        payload = encode_compact(trained, spec, bits=4)
        decoded = decode_compact(payload, {"frozen": torch.ones(1)}, spec, bits=4)

        self.assertEqual(len(payload), 16)
        self.assertTrue(torch.equal(decoded["frozen"], torch.ones(1)))
        for name in names:
            error = (decoded[name].float() - trained[name]).abs().max().item()
            self.assertLessEqual(error, trained[name].abs().max().item() / 14 + 1e-3)

    def test_extra_archive_bytes_are_rejected(self):
        spec = (("first", 8), ("second", 8))
        trained = {name: torch.zeros(count) for name, count in spec}
        payload = encode_compact(trained, spec, bits=4)
        with self.assertRaises(ValueError):
            decode_compact(payload + b"x", {}, spec, bits=4)

    def test_entropy_coding_round_trip(self):
        spec = (("first", 16), ("second", 16))
        trained = {name: torch.linspace(-1.0, 1.0, count) for name, count in spec}
        payload = encode_entropy(trained, spec, bits=3)
        decoded = decode_entropy(payload, {}, spec, bits=3)
        self.assertEqual(tuple(decoded), ("first", "second"))
        with self.assertRaises(ValueError):
            decode_entropy(payload + b"x", {}, spec, bits=3)
        with self.assertRaises(ValueError):
            decode_entropy(payload[:-1], {}, spec, bits=3)
