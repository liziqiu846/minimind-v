from __future__ import annotations

import hashlib
import inspect
import struct
import unittest
import zlib
from collections import OrderedDict

import numpy as np

from experiments.phase4_complexity_v1 import INVALID_CANDIDATE_ID
from experiments.phase4_complexity_v1 import conditional_codec as codec
from experiments.phase4_complexity_v1.audit_conditional_codec import (
    PROBE_NAMES,
    _probe_values,
)
from experiments.phase4_complexity_v1.candidate_registry import (
    load_candidate_registry,
    load_complexity_protocol,
)
from experiments.phase4_complexity_v1.freeze_verification import (
    verify_freeze_manifest,
)


class Phase4ConditionalCodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry, cls.registry_receipt = load_candidate_registry()

    def zero_blocks(self, candidate_id):
        candidate = self.registry[candidate_id]
        return OrderedDict(
            (
                name,
                codec.quantize_coordinates(
                    np.zeros(
                        candidate.block_dimensions[name],
                        dtype=np.float32,
                    )
                ),
            )
            for name in candidate.block_order
        )

    @staticmethod
    def resign(prefix):
        return prefix + hashlib.sha256(prefix).digest()

    def test_fifteen_candidate_ids_are_fixed_and_unique(self):
        self.assertEqual(tuple(self.registry), tuple(range(15)))
        self.assertEqual(
            [candidate.candidate_name for candidate in self.registry.values()],
            [
                "current-M2-root-43101",
                "current-M2-root-43102",
                "current-M2-root-43103",
                "current-M3-root-43101",
                "current-M3-root-43102",
                "current-M3-root-43103",
                "M4-shared-1024-root-43101",
                "M4-shared-1024-root-43102",
                "M4-shared-1024-root-43103",
                "M4-shared-2048-root-43101",
                "M4-shared-2048-root-43102",
                "M4-shared-2048-root-43103",
                "M4-shared-3072-root-43101",
                "M4-shared-3072-root-43102",
                "M4-shared-3072-root-43103",
            ],
        )
        self.assertEqual(self.registry_receipt["candidate_id_bits"], 4)

    def test_temporal_certificate_scope_and_freeze_are_explicit(self):
        protocol, _ = load_complexity_protocol()
        scope = protocol["temporal_and_certificate_scope"]
        self.assertTrue(scope["legacy_M2_M3"]["protocol_created_after_training"])
        self.assertFalse(
            scope["legacy_M2_M3"][
                "replaces_original_formal_training_certificate"
            ]
        )
        self.assertTrue(
            scope["new_M4"]["eligible_for_training_complexity"]
        )
        external = scope["external_candidate_selection_certificate"]
        self.assertEqual(external["identity_cost_bits"], 4)
        self.assertEqual(
            external["guarantee_layer"], "external candidate selection only"
        )
        self.assertEqual(verify_freeze_manifest()["status"], "passed")

    def test_four_bit_code_accepts_only_zero_through_fourteen(self):
        for candidate_id in range(15):
            message, receipt = codec.encode_conditional_message(
                candidate_id, self.zero_blocks(candidate_id)
            )
            self.assertEqual(message[0] >> 4, candidate_id)
            self.assertEqual(message[0] & 0x0F, 0)
            self.assertEqual(receipt["candidate_id_bits"], 4)
        invalid_prefix = bytes([INVALID_CANDIDATE_ID << 4])
        with self.assertRaises(ValueError):
            codec.decode_conditional_message(self.resign(invalid_prefix))
        valid, _ = codec.encode_conditional_message(0, self.zero_blocks(0))
        prefix = bytes([valid[0] | 1]) + valid[1:-32]
        with self.assertRaises(ValueError):
            codec.decode_conditional_message(self.resign(prefix))

    def test_method_block_structures_are_frozen(self):
        for candidate_id in range(3):
            self.assertEqual(
                self.registry[candidate_id].block_order,
                ("vision", "projector", "language"),
            )
        for candidate_id in range(3, 6):
            self.assertEqual(
                self.registry[candidate_id].block_order, ("shared",)
            )
        for candidate_id in range(6, 15):
            self.assertEqual(
                self.registry[candidate_id].block_order,
                (
                    "shared",
                    "vision_private",
                    "projector_private",
                    "language_private",
                ),
            )

    def test_decode_has_no_mms2_or_result_dependency(self):
        source = inspect.getsource(codec)
        self.assertNotIn("mms2", source.lower())
        self.assertNotIn("experiments.runs", source)
        self.assertNotIn("generalization_bound", source)
        message, _ = codec.encode_conditional_message(3, self.zero_blocks(3))
        decoded, receipt = codec.decode_conditional_message(message)
        self.assertEqual(tuple(decoded), ("shared",))
        self.assertFalse(receipt["full_archive_bits_included"])

    def test_same_input_is_byte_exact_deterministic(self):
        blocks = self.zero_blocks(6)
        first, first_receipt = codec.encode_conditional_message(6, blocks)
        second, second_receipt = codec.encode_conditional_message(6, blocks)
        self.assertEqual(first, second)
        self.assertEqual(first_receipt, second_receipt)

    def test_corruption_truncation_and_trailing_bytes_are_rejected(self):
        message, _ = codec.encode_conditional_message(6, self.zero_blocks(6))
        for position in (0, 1, len(message) // 2, len(message) - 1):
            damaged = bytearray(message)
            damaged[position] ^= 1
            with self.assertRaises(ValueError):
                codec.decode_conditional_message(bytes(damaged))
        for cut in (0, 1, 8, 31, len(message) - 1):
            with self.assertRaises(ValueError):
                codec.decode_conditional_message(message[:cut])
        with self.assertRaises(ValueError):
            codec.decode_conditional_message(message + b"\x00")
        with self.assertRaises(ValueError):
            codec.decode_conditional_message(message + message)

    def test_bit_accounting_is_exact_for_every_method(self):
        expected_framing = {"M2": 356, "M3": 292, "M4": 388}
        for candidate_id in (0, 3, 6):
            message, receipt = codec.encode_conditional_message(
                candidate_id, self.zero_blocks(candidate_id)
            )
            self.assertEqual(
                receipt["framing_bits"],
                expected_framing[receipt["method"]],
            )
            paid = (
                receipt["candidate_id_bits"]
                + receipt["framing_bits"]
                + receipt["total_scale_bits"]
                + receipt["total_compressed_symbol_bits"]
            )
            self.assertEqual(paid, receipt["conditional_message_bits"])
            self.assertEqual(paid, len(message) * 8)
            self.assertEqual(paid, receipt["paid_field_bits_sum"])

    def test_m4_Z_U_S_round_trip_exact_for_all_nine_candidates(self):
        for candidate_id in range(6, 15):
            candidate = self.registry[candidate_id]
            for probe_name in PROBE_NAMES:
                values = _probe_values(candidate, probe_name)
                blocks = OrderedDict(
                    (name, codec.quantize_coordinates(values[name]))
                    for name in candidate.block_order
                )
                message, _ = codec.encode_conditional_message(
                    candidate_id, blocks
                )
                decoded, _ = codec.decode_conditional_message(message)
                for name in candidate.block_order:
                    self.assertEqual(
                        blocks[name].scale_bytes, decoded[name].scale_bytes
                    )
                    self.assertTrue(
                        np.array_equal(
                            blocks[name].symbols, decoded[name].symbols
                        )
                    )

    def test_reserved_symbol_padding_and_invalid_scales_are_rejected(self):
        with self.assertRaises(ValueError):
            codec.unpack_three_bit_symbols(b"\xe0", 1)
        packed = codec.pack_three_bit_symbols(np.asarray([0], dtype=np.int16))
        with self.assertRaises(ValueError):
            codec.unpack_three_bit_symbols(
                bytes([packed[0] | 1]), 1
            )
        for scale_bytes in (
            struct.pack("<f", float("nan")),
            struct.pack("<f", float("inf")),
            struct.pack("<f", -1.0),
            codec.NEGATIVE_ZERO_FLOAT32,
        ):
            with self.assertRaises(ValueError):
                codec.make_quantized_block(
                    scale_bytes,
                    np.zeros(1, dtype=np.int16),
                    expected_dimension=1,
                )
        with self.assertRaises(ValueError):
            codec.make_quantized_block(
                codec.POSITIVE_ZERO_FLOAT32,
                np.asarray([1], dtype=np.int16),
                expected_dimension=1,
            )
        with self.assertRaises(ValueError):
            codec.make_quantized_block(
                struct.pack("<f", 1.0),
                np.asarray([1], dtype=np.int16),
                expected_dimension=1,
            )

    def test_noncanonical_zlib_stream_is_rejected(self):
        candidate = self.registry[3]
        raw = codec.pack_three_bit_symbols(
            self.zero_blocks(3)["shared"].symbols
        )
        compressor = zlib.compressobj(
            level=9, strategy=zlib.Z_HUFFMAN_ONLY
        )
        alternative = compressor.compress(raw) + compressor.flush()
        canonical = zlib.compress(raw, level=9)
        self.assertNotEqual(alternative, canonical)
        prefix = bytearray([3 << 4])
        prefix.extend(codec.POSITIVE_ZERO_FLOAT32)
        prefix.extend(struct.pack("<I", len(alternative)))
        prefix.extend(alternative)
        with self.assertRaises(ValueError):
            codec.decode_conditional_message(self.resign(bytes(prefix)))


if __name__ == "__main__":
    unittest.main()
