import unittest
import tempfile
from pathlib import Path

from experiments.phase3.canonical_io import atomic_write_json, atomic_write_jsonl, inventory_files, sha256_bytes
from experiments.phase3.run_phase3_formal_v2 import shard_plan, validate_finalized_shard, validate_resume_state
from experiments.phase3.runner_common import validate_selected_filenames


class Phase3ResumeTests(unittest.TestCase):
    def test_formal_execution_accepts_only_one_contiguous_frozen_shard(self):
        frozen = [f"{index:012d}.jpg" for index in range(96)]
        validate_selected_filenames("formal", ["M1-root-none"], frozen[32:64], frozen)
        with self.assertRaises(ValueError):
            validate_selected_filenames("formal", ["M1-root-none"], frozen[32:63] + [frozen[64]], frozen)
        with self.assertRaises(ValueError):
            validate_selected_filenames("formal", ["M1-root-none"], frozen[:33], frozen)
        with self.assertRaises(ValueError):
            validate_selected_filenames(
                "formal", ["M1-root-none", "M3-root-43101"], frozen[:32], frozen
            )

    def test_fixed_contiguous_shards_and_tamper_rejection(self):
        filenames = [f"{index:012d}.jpg" for index in range(65)]
        plan = shard_plan(["M1", "M2"], filenames)
        self.assertEqual([len(row["filenames"]) for row in plan], [32, 32, 1, 32, 32, 1])
        self.assertEqual(plan[0]["filenames"], filenames[:32])
        state = {
            "schema_version": 1, "run_config_sha256": "r", "protocol_sha256": "a",
            "phase3_source_commit": "s", "protocol_repository_commit": "b",
            "code_manifest_sha256": "c", "expected_registry_sha256": "e",
            "verification_receipt_sha256": "v", "data_manifest_sha256": "d",
            "split_manifest_sha256": "p", "overlap_receipt_sha256": "o",
            "approval_sha256": "u", "ordered_model_ids": ["M1", "M2"],
            "ordered_filenames_sha256": "f", "shard_size_unique_images": 32,
            "shard_plan": plan, "completed_shards": [], "run_status": "in_progress",
        }
        validate_resume_state(state, {"protocol_sha256": "a"}, plan)
        with self.assertRaisesRegex(ValueError, "resume hash mismatch"):
            validate_resume_state(state, {"protocol_sha256": "b"}, plan)
        with self.assertRaisesRegex(ValueError, "shard plan"):
            validate_resume_state(state, {"protocol_sha256": "a"}, plan[:-1])

    def test_incomplete_or_tampered_finalized_shard_is_rejected(self):
        expected = shard_plan(["M1"], ["a.jpg"])[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "no manifest"):
                validate_finalized_shard(root, expected, "a" * 64)
            payload = root / "payload"
            payload.mkdir()
            atomic_write_jsonl(payload / "row_level_results.jsonl", [{"model_id": "M1", "filename": "a.jpg"}])
            atomic_write_jsonl(payload / "image_group_results.jsonl", [{"model_id": "M1", "filename": "a.jpg"}])
            atomic_write_json(payload / "run_manifest.json", {
                "run_mode": "formal", "run_status": "success", "ordered_model_ids": ["M1"],
                "ordered_filenames_sha256": sha256_bytes(b"a.jpg\n"),
                "row_result_count": 1, "image_group_result_count": 1,
                "files": inventory_files(payload, excluded=("run_manifest.json",)),
            })
            manifest = {
                "schema_version": 1, "shard_id": expected["shard_id"], "run_config_sha256": "a" * 64,
                "model_id": "M1", "filenames": ["a.jpg"], "row_count": 1, "image_group_count": 1,
                "files": inventory_files(root, excluded=("shard_manifest.json",)),
                "exclusion_rule": "only shard_manifest.json is excluded",
            }
            atomic_write_json(root / "shard_manifest.json", manifest)
            validate_finalized_shard(root, expected, "a" * 64)
            atomic_write_jsonl(payload / "row_level_results.jsonl", [{"model_id": "M1", "filename": "other.jpg"}])
            with self.assertRaisesRegex(ValueError, "inventory"):
                validate_finalized_shard(root, expected, "a" * 64)


if __name__ == "__main__":
    unittest.main()
