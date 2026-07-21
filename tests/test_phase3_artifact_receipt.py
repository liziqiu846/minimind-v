import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.phase3.artifact_validation import (
    _expected_degenerate_report,
    _validate_failure_report,
)
from experiments.phase3.canonical_io import atomic_write_bytes, atomic_write_json, sha256_bytes, snapshot_file
from experiments.phase3.stage2_adapter_loader import snapshot_and_verify, verify_payload
from experiments.phase3.verify_stage2_artifacts import verify_registry_artifacts


class Phase3ArtifactReceiptTests(unittest.TestCase):
    def test_missing_is_blocked_and_hard_failure_has_priority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = Path(__file__).resolve().parents[1]
            protocol = repo / "experiments/stage2_protocol_v2.json"
            registry = repo / "experiments/phase3/phase3_expected_model_registry.json"
            registry_payload = json.loads(snapshot_file(registry))
            with mock.patch(
                "experiments.phase3.verify_stage2_artifacts.verify_stage2_source_integrity"
            ):
                receipt = verify_registry_artifacts(registry, root, protocol)
                self.assertEqual(receipt["overall_status"], "blocked")
                bad = root / registry_payload["models"][0]["artifact_relative_path"]
                atomic_write_bytes(bad, b"xx")
                receipt = verify_registry_artifacts(registry, root, protocol)
                self.assertEqual(receipt["overall_status"], "hard_failure")

    def test_decoded_identity_mismatch_is_rejected(self):
        payload = b"x"
        expected = {"artifact_size_bytes": 1, "artifact_sha256": sha256_bytes(payload), "method": "M1", "mapping_root": None}
        with mock.patch("experiments.quantize_stage2_adapter.decode_mms2", return_value=({}, {"model_group": "M2", "mapping_root": 43101, "archive_bytes": 1})):
            with self.assertRaisesRegex(ValueError, "decoded_identity_mismatch"):
                verify_payload(payload, expected)

    def test_path_traversal_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root.parent / (root.name + "-outside")
            atomic_write_bytes(outside, b"secret")
            self.addCleanup(lambda: outside.unlink(missing_ok=True))
            link = root / "link.mms2"
            link.symlink_to(outside)
            with self.assertRaises(ValueError):
                snapshot_file(link, root=root)
            with self.assertRaises(ValueError):
                snapshot_file(root / "../escape", root=root)

            real_root = root / "real-artifacts"
            real_root.mkdir()
            atomic_write_bytes(real_root / "adapter.mms2", b"x")
            linked_root = root / "linked-artifacts"
            linked_root.symlink_to(real_root, target_is_directory=True)
            expected = {
                "artifact_relative_path": "adapter.mms2",
                "artifact_size_bytes": 1,
                "artifact_sha256": sha256_bytes(b"x"),
                "method": "M1",
                "mapping_root": None,
            }
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                snapshot_and_verify(linked_root, expected)

    def test_data_diagnostics_rows_are_exact_and_privacy_sanitized(self):
        rows = [
            {
                "row_key": "a:0", "category": "a", "filename": "000000000001.jpg",
                "caption": "a first complete caption", "caption2": "a first complete caption",
                "negative_caption": "a different complete caption",
            },
            {
                "row_key": "a:1", "category": "a", "filename": "000000000002.jpg",
                "caption": "another positive caption", "caption2": "second positive caption",
                "negative_caption": "another negative caption",
            },
        ]
        self.assertEqual(
            _expected_degenerate_report(rows),
            {
                "schema_version": 1,
                "degenerate_row_count": 1,
                "affected_image_group_count": 1,
                "type_counts": {"positive_pair_equal": 1},
                "rows": [{
                    "row_index": 0, "row_key": "a:0", "category": "a",
                    "filename": "000000000001.jpg",
                    "degenerate_types": ["positive_pair_equal"],
                }],
            },
        )
        failure = {
            "row_index": 1,
            "row_key": "a:1",
            "model_mode": "vlm",
            "caption_role": "negative",
            "full_length": 451,
            "max_length": 450,
            "reason_code": "overlength",
            "detail": "CaptionRecordError: full token sequence exceeds frozen maximum length",
        }
        report = {"schema_version": 1, "failure_count": 1, "failures": [failure]}
        _validate_failure_report(report, rows, overlength_only=True)
        with self.assertRaises(ValueError):
            _validate_failure_report(
                {**report, "unexpected": None}, rows, overlength_only=True
            )
        disclosed = {**failure, "detail": rows[1]["negative_caption"]}
        with self.assertRaisesRegex(ValueError, "discloses"):
            _validate_failure_report(
                {"schema_version": 1, "failure_count": 1, "failures": [disclosed]},
                rows,
                overlength_only=True,
            )


if __name__ == "__main__":
    unittest.main()
