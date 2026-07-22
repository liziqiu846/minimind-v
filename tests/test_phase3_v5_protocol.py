import tempfile
import unittest
from pathlib import Path

from experiments.phase3.canonical_io import atomic_write_bytes, canonical_json_bytes
from experiments.phase3.phase3_protocol_v5 import (
    Phase3ProtocolV5, build_protocol_payload_v5, enumerate_code_paths_v5,
)


class Phase3V5ProtocolTests(unittest.TestCase):
    def test_fixed_protocol_contract(self):
        payload = build_protocol_payload_v5("a" * 64)
        self.assertEqual(list(payload["primary_risks"]), [
            "robust_positive_brier_risk", "visual_semantic_loss",
        ])
        self.assertEqual(payload["bounds"]["fixed_model"]["comparison_slots"], 20)
        self.assertEqual(payload["bounds"]["compression"]["comparison_slots"], 20)
        self.assertFalse(payload["statistical_interpretation"]["simultaneous_95_percent_coverage_claim"])
        self.assertEqual(payload["split"]["certifying_formal_unique_images"], 1345)
        self.assertEqual(len(payload["models"]["ordered_model_ids"]), 10)

    def test_candidate_and_frozen_bytes_are_identical(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = canonical_json_bytes(build_protocol_payload_v5("b" * 64))
            candidate = root / "phase3_protocol_candidate_v5.json"
            frozen = root / "phase3_protocol_frozen_v5.json"
            atomic_write_bytes(candidate, raw)
            atomic_write_bytes(frozen, raw)
            self.assertEqual(Phase3ProtocolV5.load(candidate).raw_sha256, Phase3ProtocolV5.load(frozen).raw_sha256)

    def test_manifest_enumeration_excludes_protocol_json(self):
        relative = [path.relative_to(Path(__file__).resolve().parents[1]).as_posix() for path in enumerate_code_paths_v5()]
        self.assertIn("experiments/phase3/phase3_protocol_v5.py", relative)
        self.assertIn("docs/phase3_theory_v5.md", relative)
        self.assertNotIn("experiments/phase3/phase3_protocol_candidate_v5.json", relative)
        self.assertNotIn("experiments/phase3/phase3_code_manifest_v5.json", relative)


if __name__ == "__main__":
    unittest.main()
