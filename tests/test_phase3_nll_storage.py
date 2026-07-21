import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from experiments.phase3.nll_diagnostics import summarize_nll, validate_nll_store, write_nll_store


class Phase3NLLStorageTests(unittest.TestCase):
    def test_npz_index_alignment_and_two_poolings(self):
        base = {"row_key": "x:0", "model_id": "M", "filename": "000000000001.jpg", "category": "x", "numeric_id": 0}
        entries = [
            {**base, "row_index": 0, "condition": "correct", "caption_role": "pos1", "values": np.array([0.0, 10.0], dtype=np.float32)},
            *[
                {**base, "row_index": 0, "condition": condition, "caption_role": role, "values": np.array([2.0], dtype=np.float32)}
                for condition, role in (
                    ("correct", "pos2"), ("correct", "negative"),
                    ("none", "pos1"), ("none", "pos2"), ("none", "negative"),
                )
            ],
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "nll"
            summary = write_nll_store(root, entries)
            arrays = validate_nll_store(root)
            index = [json.loads(line) for line in (root / "nll_index.jsonl").read_text().splitlines()]
            self.assertEqual(arrays["offsets"].tolist(), [0, 2, 3, 4, 5, 6, 7])
            self.assertEqual(arrays["condition_codes"].tolist(), [0, 0, 0, 1, 1, 1])
            self.assertEqual(arrays["caption_role_codes"].tolist(), [0, 1, 2, 0, 1, 2])
            self.assertEqual(arrays["row_indices"].tolist(), [0] * 6)
            self.assertAlmostEqual(summary["token_level"]["mean"], 20.0 / 7.0)
            self.assertAlmostEqual(summary["caption_level"]["mean"], 2.5)
            self.assertEqual(summary, summarize_nll(arrays, index))

    def test_tampered_offsets_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "nll"
            base = {"row_index": 0, "row_key": "x:0", "model_id": "M0-root-test", "filename": "000000000001.jpg", "category": "x", "numeric_id": 0, "condition": "lm_only", "values": [1.0]}
            write_nll_store(root, [
                {**base, "caption_role": "pos1"},
                {**base, "caption_role": "pos2"},
                {**base, "caption_role": "negative"},
            ])
            with np.load(root / "nll_tokens.npz", allow_pickle=False) as source:
                arrays = {name: source[name] for name in source.files}
            arrays["offsets"] = np.array([0, 2, 3, 3], dtype=np.int64)
            np.savez_compressed(root / "nll_tokens.npz", **arrays)
            with self.assertRaises(ValueError):
                validate_nll_store(root)


if __name__ == "__main__":
    unittest.main()
