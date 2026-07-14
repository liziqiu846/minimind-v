import unittest

import torch

from experiments.quantize_subspace import (
    decode_compact,
    decode_entropy,
    encode_compact,
    encode_entropy,
    state_dict_sha256_v1,
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

    def test_state_hash_is_independent_of_dictionary_order(self):
        first = {
            "z.weight": torch.tensor([1, 2], dtype=torch.int16),
            "a.weight": torch.tensor([[1.0, 2.0]], dtype=torch.float32),
        }
        reversed_order = {
            "a.weight": first["a.weight"].clone(),
            "z.weight": first["z.weight"].clone(),
        }

        self.assertEqual(
            state_dict_sha256_v1(first),
            state_dict_sha256_v1(reversed_order),
        )

    def test_state_hash_includes_value_shape_and_dtype(self):
        original = {"weight": torch.tensor([1.0, 2.0], dtype=torch.float32)}
        changed_value = {"weight": torch.tensor([1.0, 3.0], dtype=torch.float32)}
        changed_shape = {"weight": original["weight"].reshape(1, 2)}
        changed_dtype = {"weight": original["weight"].to(torch.float64)}
        original_hash = state_dict_sha256_v1(original)

        self.assertNotEqual(original_hash, state_dict_sha256_v1(changed_value))
        self.assertNotEqual(original_hash, state_dict_sha256_v1(changed_shape))
        self.assertNotEqual(original_hash, state_dict_sha256_v1(changed_dtype))

    def test_state_hash_supports_scalar_tensors(self):
        state = {
            "float": torch.tensor(1.0),
            "complex": torch.tensor(1.0 + 2.0j),
        }
        self.assertEqual(len(state_dict_sha256_v1(state)), 64)
