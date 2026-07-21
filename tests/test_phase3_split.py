import inspect
import unittest

from experiments.phase3.canonical_io import canonical_json_bytes, sha256_bytes
from experiments.phase3.datasets.sugarcrepe_pp import row_index
from experiments.phase3.prepare_phase3_data import split_name


class Phase3SplitTests(unittest.TestCase):
    def test_frozen_salt_and_1542_fixture_counts(self):
        source = inspect.getsource(split_name)
        self.assertIn("phase3-v1|", source)
        self.assertNotIn("phase3-v4|", source)
        pilot, formal = [], []
        value = 1
        while len(pilot) < 153 or len(formal) < 1389:
            filename = f"{value:012d}.jpg"
            bucket = pilot if split_name(filename) == "pilot" else formal
            limit = 153 if bucket is pilot else 1389
            if len(bucket) < limit:
                bucket.append(filename)
            value += 1
        self.assertEqual((len(pilot), len(formal)), (153, 1389))
        self.assertFalse(set(pilot) & set(formal))
        self.assertEqual(len(set(pilot + formal)), 1542)

    def test_source_row_hash_includes_newline_and_is_not_self_referential(self):
        row = {"caption": "a", "caption2": "b", "category": "x", "filename": "000000000001.jpg", "negative_caption": "c", "numeric_id": 1, "row_key": "x:1"}
        indexed = row_index([row])[0]
        self.assertEqual(indexed["source_row_sha256"], sha256_bytes(canonical_json_bytes(row)))
        self.assertTrue(canonical_json_bytes(row).endswith(b"\n"))
        self.assertNotIn("source_row_sha256", row)


if __name__ == "__main__":
    unittest.main()
