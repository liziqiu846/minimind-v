import json
import unittest
from pathlib import Path

from experiments.phase3.canonical_io import sha256_bytes, snapshot_file
from experiments.phase3.stage2_adapter_loader import ARTIFACT_BATCH_ID, DECODER_ID, MODELS, RERUN_SOURCE_COMMIT


ROOT = Path(__file__).resolve().parents[1]


class Phase3ExpectedRegistryTests(unittest.TestCase):
    def test_authority_and_registry_are_separate_and_exact(self):
        authority_path = ROOT / "experiments/phase3/phase3_stage2_authority_manifest_v2.json"
        registry_path = ROOT / "experiments/phase3/phase3_expected_model_registry.json"
        authority = json.loads(snapshot_file(authority_path))
        registry = json.loads(snapshot_file(registry_path))
        self.assertEqual(authority["decoder_id"], "stage2-v2-mms2")
        self.assertEqual(DECODER_ID, "stage2-v2-mms2")
        self.assertEqual(registry["authority_manifest_sha256"], sha256_bytes(snapshot_file(authority_path)))
        self.assertEqual(registry["registry_id"], "phase3-v4-expected-model-registry-v2")
        self.assertEqual(registry["artifact_batch_id"], ARTIFACT_BATCH_ID)
        self.assertEqual(registry["rerun_source_commit"], RERUN_SOURCE_COMMIT)
        self.assertEqual(authority["schema_version"], 2)
        self.assertEqual(registry["model_count"], 10)
        for row, expected in zip(registry["models"], MODELS, strict=True):
            self.assertEqual({key: row[key] for key in expected}, expected)
            self.assertEqual(row["stage2_result_source"]["model_group"], expected["method"])
            self.assertEqual(row["description_bits"], row["artifact_size_bytes"] * 8)
            self.assertEqual(len(row["artifact_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
