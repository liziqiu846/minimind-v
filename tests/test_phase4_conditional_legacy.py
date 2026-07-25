from __future__ import annotations

import hashlib
import os
import unittest
from pathlib import Path

import numpy as np

from experiments.phase4_complexity_v1.audit_conditional_codec import (
    LEGACY_RELATIVE_PATHS,
)
from experiments.phase4_complexity_v1.candidate_registry import (
    load_candidate_registry,
)
from experiments.phase4_complexity_v1.conditional_codec import (
    decode_conditional_message,
    encode_conditional_message,
)
from experiments.phase4_complexity_v1.legacy_mms2_import import (
    import_legacy_mms2_v1_file,
)


DEFAULT_FORMAL_ROOT = Path(
    "/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721/"
    "experiments/runs/stage2_v2_fast/formal"
)


class Phase4ConditionalLegacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry, _ = load_candidate_registry()
        cls.formal_root = Path(
            os.environ.get(
                "MINIMIND_STAGE2_FORMAL_ROOT", str(DEFAULT_FORMAL_ROOT)
            )
        )
        if not cls.formal_root.is_dir():
            raise unittest.SkipTest("formal Stage-2 artifact root is unavailable")

    def test_six_legacy_models_preserve_exact_scale_and_symbols(self):
        for candidate_id, relative_path in LEGACY_RELATIVE_PATHS.items():
            path = self.formal_root / relative_path
            before = path.read_bytes()
            before_stat = path.stat()
            blocks, import_receipt = import_legacy_mms2_v1_file(
                path, candidate_id
            )
            message, receipt = encode_conditional_message(
                candidate_id, blocks
            )
            decoded, decoded_receipt = decode_conditional_message(message)
            self.assertEqual(receipt, decoded_receipt)
            self.assertEqual(tuple(blocks), self.registry[candidate_id].block_order)
            for name in blocks:
                self.assertEqual(
                    blocks[name].scale_bytes, decoded[name].scale_bytes
                )
                self.assertTrue(
                    np.array_equal(
                        blocks[name].symbols, decoded[name].symbols
                    )
                )
            after_stat = path.stat()
            after = path.read_bytes()
            self.assertEqual(before, after)
            self.assertEqual(before_stat.st_mtime_ns, after_stat.st_mtime_ns)
            self.assertEqual(
                hashlib.sha256(after).hexdigest(),
                import_receipt["archive_sha256"],
            )
            self.assertEqual(
                receipt["paid_field_bits_sum"],
                receipt["conditional_message_bits"],
            )
            self.assertNotEqual(
                receipt["conditional_message_bits"],
                import_receipt["archive_bits"],
            )


if __name__ == "__main__":
    unittest.main()

