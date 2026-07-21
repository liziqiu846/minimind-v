import hashlib
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from experiments.phase3.audit_training_overlap import SCOPES, _distance, _validate_coverage, audit
from experiments.phase3.artifact_validation import validate_overlap_receipt
from experiments.phase3.canonical_io import atomic_write_json, atomic_write_jsonl, load_json_snapshot, load_jsonl_snapshot, sha256_bytes, snapshot_file
from experiments.phase3.prepare_phase3_data import PHASH_SPEC_ID
from experiments.phase3.status import Phase3Blocked, Phase3HardFailure


def coverage_payload():
    return {
        "schema_version": 1,
        "manifest_type": "phase3_project_training_coverage_v1",
        "scopes": [
            {
                "scope_id": scope, "complete": True, "disposition": "not_used",
                "source_description": "synthetic unused scope", "source_manifest_relative_alias": None,
                "source_manifest_sha256": None, "image_count": 0, "text_target_count": 0,
                "declaration_by": "unit-test", "declaration_date": "2026-07-20", "reason": "synthetic fixture",
            }
            for scope in SCOPES
        ],
    }


class Phase3OverlapTests(unittest.TestCase):
    def test_seven_scope_coverage_and_phash_thresholds(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "coverage.json"
            atomic_write_json(path, coverage_payload())
            coverage, bindings, rows = _validate_coverage(path)
            self.assertEqual([row["scope_id"] for row in coverage["scopes"]], list(SCOPES))
            self.assertEqual((bindings, rows), ([], []))
        self.assertEqual(_distance("0000000000000000", "000000000000000f"), 4)
        self.assertEqual(_distance("0000000000000000", "000000000000001f"), 5)
        self.assertEqual(_distance("0000000000000000", "00000000000003ff"), 10)

    def test_review_must_bind_exact_audit_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "input"
            inputs.mkdir()
            split = inputs / "split.json"
            formal = inputs / "formal.jsonl"
            formal_data = inputs / "formal_data.jsonl"
            coverage = inputs / "coverage.json"
            review = inputs / "review.json"
            atomic_write_jsonl(formal, [
                {
                    "filename": f"{index:012d}.jpg", "coco_image_id": index,
                    "sha256": f"{index:064x}"[-64:], "perceptual_hash": f"{index:016x}"[-16:],
                    "status": "ready", "error_code": None, "exists": True, "size_bytes": 1,
                }
                for index in range(1389)
            ])
            atomic_write_jsonl(formal_data, [{"row_key": "x:0", "caption": "a", "caption2": "b", "negative_caption": "c"}])
            payload = snapshot_file(formal_data)
            atomic_write_json(split, {
                "formal_unique_images": 1389, "split_version": "phase3-v1",
                "files": [{"logical_name": "formal_jsonl", "relative_path": "formal_data.jsonl", "size_bytes": len(payload), "sha256": sha256_bytes(payload)}],
            })
            atomic_write_json(coverage, coverage_payload())
            atomic_write_json(review, {
                "schema_version": 1, "overlap_audit_input_sha256": "0" * 64,
                "reviewer": "unit-test", "reviewed_at": "2026-07-21T00:00:00Z", "decisions": [],
            })
            args = Namespace(
                split_manifest=split, formal_image_manifest=formal, training_coverage_manifest=coverage,
                output_dir=root / "out", overlap_review=review, status_output=root / "status/status.json",
            )
            with self.assertRaisesRegex(Phase3HardFailure, "overlap_review_binding_invalid"):
                audit(args)

    def test_44_reviewed_overlaps_become_exact_1345_certifying_partition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "input"
            inputs.mkdir()
            split = inputs / "split.json"
            formal = inputs / "formal.jsonl"
            formal_data = inputs / "formal_data.jsonl"
            coverage = inputs / "coverage.json"
            training = inputs / "training.jsonl"
            review = inputs / "review.json"
            sentinel = "ffffffffffffffff"
            reviewed_phashes = []
            candidate_index = 0
            while len(reviewed_phashes) < 44:
                candidate = hashlib.sha256(f"phash-{candidate_index}".encode()).hexdigest()[:16]
                candidate_index += 1
                if _distance(candidate, sentinel) > 10 and all(
                    _distance(candidate, previous) > 10 for previous in reviewed_phashes
                ):
                    reviewed_phashes.append(candidate)
            formal_rows = [
                {
                    "filename": f"{index:012d}.jpg", "coco_image_id": index,
                    "sha256": hashlib.sha256(f"formal-{index}".encode()).hexdigest(),
                    "perceptual_hash": reviewed_phashes[index] if index < 44 else sentinel,
                    "status": "ready",
                    "error_code": None, "exists": True, "size_bytes": 1,
                }
                for index in range(1389)
            ]
            atomic_write_jsonl(formal, formal_rows)
            atomic_write_jsonl(
                formal_data,
                [{"row_key": "x:0", "caption": "a", "caption2": "b", "negative_caption": "c"}],
            )
            formal_payload = snapshot_file(formal_data)
            atomic_write_json(split, {
                "formal_unique_images": 1389, "split_version": "phase3-v1",
                "files": [{
                    "logical_name": "formal_jsonl", "relative_path": "formal_data.jsonl",
                    "size_bytes": len(formal_payload), "sha256": sha256_bytes(formal_payload),
                }],
            })
            training_rows = [
                {
                    "source_id": "phase1_training:fixture", "record_id": f"{index:04d}",
                    "filename": None, "coco_image_id": None,
                    "sha256": hashlib.sha256(f"training-{index}".encode()).hexdigest(),
                    "perceptual_hash": reviewed_phashes[index], "image_available": True,
                    "assistant_text_sha256s": [], "phash_spec_id": PHASH_SPEC_ID,
                }
                for index in range(44)
            ]
            atomic_write_jsonl(training, training_rows)
            coverage_value = coverage_payload()
            coverage_value["scopes"][0].update({
                "disposition": "used", "source_manifest_relative_alias": "training.jsonl",
                "source_manifest_sha256": sha256_bytes(snapshot_file(training)), "image_count": 44,
            })
            atomic_write_json(coverage, coverage_value)
            first = Namespace(
                split_manifest=split, formal_image_manifest=formal,
                training_coverage_manifest=coverage, output_dir=root / "audit1",
                overlap_review=None, status_output=root / "status1/status.json",
            )
            with self.assertRaisesRegex(Phase3Blocked, "probable_reencoded_duplicate_unresolved"):
                audit(first)
            first_receipt = load_json_snapshot(first.output_dir / "phase3_overlap_audit_receipt.json")
            probable = load_jsonl_snapshot(first.output_dir / "probable_pairs.jsonl")
            self.assertEqual(len(probable), 44)
            atomic_write_json(review, {
                "schema_version": 1,
                "overlap_audit_input_sha256": first_receipt["overlap_audit_input_sha256"],
                "reviewer": "unit-test-human", "reviewed_at": "2026-07-21",
                "decisions": [
                    {
                        "pair_id": row["pair_id"], "formal_sha256": row["formal_sha256"],
                        "formal_phash": row["formal_phash"], "training_sha256": row["training_sha256"],
                        "training_phash": row["training_phash"], "decision": "same_source_image",
                    }
                    for row in probable
                ],
            })
            second = Namespace(
                split_manifest=split, formal_image_manifest=formal,
                training_coverage_manifest=coverage, output_dir=root / "audit2",
                overlap_review=review, status_output=root / "status2/status.json",
            )
            result = audit(second)
            self.assertEqual(result["status"], "certification_subset_project_disjoint_under_frozen_checks")
            validated = validate_overlap_receipt(
                second.output_dir / "phase3_overlap_audit_receipt.json",
                split_manifest_path=split, formal_image_manifest_path=formal,
            )
            self.assertEqual(len(validated["excluded_rows"]), 44)
            self.assertEqual(len(validated["certifying_names"]), 1345)


if __name__ == "__main__":
    unittest.main()
