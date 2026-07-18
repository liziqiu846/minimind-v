import json
import tempfile
import unittest
from pathlib import Path

from experiments.stage2_protocol import Stage2Protocol, path_is_within_declared_roots


class Stage2RuntimeIntegrityTests(unittest.TestCase):
    def test_untracked_paths_must_be_inside_exact_declared_roots(self):
        roots = ["dataset/stage2_confirm_v2_seed2028", "experiments/runs/stage2_v2"]
        self.assertTrue(
            path_is_within_declared_roots(
                "dataset/stage2_confirm_v2_seed2028/train.parquet", roots
            )
        )
        self.assertTrue(
            path_is_within_declared_roots("experiments/runs/stage2_v2", roots)
        )
        self.assertFalse(
            path_is_within_declared_roots("dataset/stage2_confirm_v2_seed20280/x", roots)
        )
        self.assertFalse(path_is_within_declared_roots("experiments/other.json", roots))
        self.assertFalse(
            path_is_within_declared_roots(
                "dataset/stage2_confirm_v2_seed2028/../../unfrozen.py", roots
            )
        )

    def test_v2_protocol_id_must_match_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "protocol.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "status": "draft",
                        "protocol_id": "minimind-v-stage2-joint-compression-v1",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "protocol ID"):
                Stage2Protocol.load(path)


if __name__ == "__main__":
    unittest.main()
