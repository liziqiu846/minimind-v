import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

from experiments.phase3.canonical_io import atomic_write_bytes, atomic_write_json, sha256_bytes, snapshot_file
from experiments.phase3.phase3_protocol import Phase3Protocol, enumerate_code_paths, verify_code_manifest
from experiments.phase3.run_phase3_formal_v2 import collect_preflight


class Phase3ProtocolTests(unittest.TestCase):
    def test_candidate_loads_but_formal_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.json"
            source = Path(__file__).resolve().parents[1] / "experiments/phase3/phase3_protocol_candidate_v4.json"
            atomic_write_bytes(path, snapshot_file(source))
            protocol = Phase3Protocol.load(path)
            self.assertEqual(protocol.kind, "candidate")
            with self.assertRaises(ValueError):
                protocol.require_frozen()

    def test_code_enumeration_includes_exact_classes_and_not_manifest(self):
        paths = enumerate_code_paths()
        relative = [path.relative_to(Path(__file__).resolve().parents[1]).as_posix() for path in paths]
        self.assertIn("experiments/phase3/phase3_protocol.py", relative)
        self.assertIn("experiments/phase3/README.md", relative)
        self.assertIn("tests/test_phase3_protocol.py", relative)
        self.assertIn("tests/fixtures/phase3/README.txt", relative)
        self.assertNotIn("experiments/phase3/phase3_code_manifest_v2.json", relative)
        self.assertEqual(relative, sorted(set(relative), key=lambda value: value.encode("utf-8")))

    def test_static_code_manifest_and_sidecar_match_current_bytes(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "experiments/phase3/phase3_code_manifest_v2.json"
        verify_code_manifest(path)
        self.assertEqual(path.with_suffix(".sha256").read_text(encoding="ascii"), sha256_bytes(snapshot_file(path)) + "\n")

    def test_static_candidate_is_ready_and_binds_v4_data_and_overlap_input(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "experiments/phase3/phase3_protocol_candidate_v4.json"
        protocol = Phase3Protocol.load(path)
        self.assertEqual(protocol.kind, "candidate")
        self.assertEqual(protocol.payload["candidate_status"], "ready_for_user_freeze")
        self.assertEqual(protocol.payload["missing_required_fields"], [])
        self.assertEqual(protocol.payload["protocol_version"], "phase3-v4")
        self.assertEqual(protocol.payload["split_version"], "phase3-v1")
        self.assertEqual(protocol.payload["stage2_artifact_batch_id"], "stage2-v2-rerun-20260721")
        self.assertEqual(protocol.payload["prompt_revision"], "phase3-prompt-v2.3-overlap-exclusion-approved")
        self.assertEqual(protocol.payload["split"]["formal_unique_images"], 1389)
        self.assertEqual(protocol.payload["split"]["excluded_formal_unique_images"], 44)
        self.assertEqual(protocol.payload["split"]["certifying_formal_unique_images"], 1345)
        self.assertEqual(
            protocol.payload["overlap_audit_input_sha256"],
            "24f62b288d2ae60acd243e4c74fdc623ee84e57837b02f015d6bd433cd84068d",
        )
        self.assertEqual(
            protocol.payload["data_manifest_sha256"],
            "2effb7fbdc763ed1870ba943d30a9cd68be7c6be15ead9892b8c69da62918405",
        )
        self.assertEqual(
            protocol.payload["split_manifest_sha256"],
            "6d9ca71c04435f0d9c9aaa932def8d5078822d65996fcc846fdb1a9604f06aff",
        )
        self.assertIsNone(protocol.payload["phase3_source_commit"])
        self.assertFalse(protocol.payload["training_allowed"])
        self.assertEqual(path.with_suffix(".sha256").read_text(encoding="ascii"), protocol.raw_sha256 + "\n")

    def test_formal_preflight_collects_all_gates_without_loading_model_or_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = root / "candidate.json"
            source = Path(__file__).resolve().parents[1] / "experiments/phase3/phase3_protocol_candidate_v4.json"
            atomic_write_bytes(protocol, snapshot_file(source))
            digest = sha256_bytes(snapshot_file(protocol))
            atomic_write_bytes(protocol.with_suffix(".sha256"), (digest + "\n").encode("ascii"))
            args = Namespace(
                protocol=protocol, code_manifest=root / "missing-code.json", expected_registry=root / "missing-registry.json",
                verification_receipt=root / "missing-receipt.json", prepared_data_dir=root / "missing-data",
                split_manifest=root / "missing-split.json", overlap_audit_receipt=None, approval=None,
                confirm_protocol_hash=digest, output_dir=None, resume=False, preflight_only=True,
                preflight_report=root / "preflight.json", status_output=root / "status/status.json",
                stage2_protocol=Path(__file__).resolve().parents[1] / "experiments/stage2_protocol_v2.json",
            )
            with mock.patch("experiments.phase3.run_phase3_formal_v2.execute_evaluation", side_effect=AssertionError("model path called")) as forward, mock.patch(
                "experiments.phase3.run_phase3_formal_v2._stage2_sources_are_unchanged", return_value=True
            ):
                report = collect_preflight(args)
            forward.assert_not_called()
            gates = {row["gate_id"]: row["status"] for row in report["gates"]}
            self.assertEqual(len(gates), 29)
            self.assertEqual(gates["protocol_is_frozen"], "blocked")
            self.assertEqual(gates["output_or_resume_state_is_valid"], "pass")
            self.assertFalse((root / "formal-output").exists())

            atomic_write_bytes(args.expected_registry, b'{ "malformed_canonical_form": true }\n')
            with mock.patch(
                "experiments.phase3.run_phase3_formal_v2._stage2_sources_are_unchanged", return_value=True
            ):
                malformed_report = collect_preflight(args)
            malformed_gates = {row["gate_id"]: row["status"] for row in malformed_report["gates"]}
            self.assertEqual(len(malformed_gates), 29)
            self.assertEqual(malformed_gates["expected_registry_hash_matches"], "hard_failure")
            self.assertEqual(malformed_gates["output_or_resume_state_is_valid"], "pass")


if __name__ == "__main__":
    unittest.main()
