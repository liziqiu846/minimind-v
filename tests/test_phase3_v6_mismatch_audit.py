from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from experiments.phase3_v6.mismatch_audit.build_mismatch_manifest import (
    assignment_core_payload,
    assignment_order_digest,
    build_caption_diagnostics,
    build_k_matchings,
    build_manifest_rows,
    build_tfidf_matrix,
    deterministic_perfect_matching,
    generate_thumbnail,
    hard_exclusion_reasons,
    hamming64,
    hull_mention_classification,
    image_fingerprint,
    lexical_pair_metrics,
    maximum_tfidf_for_pairs,
    near_duplicate_suspect,
    projected_inference_counts,
    read_jsonl,
    sha256_bytes,
)


REPOSITORY = Path(__file__).resolve().parents[1]
CERTIFYING = Path(
    "/home/lizhaohui/lzq/phase3_runtime/results/"
    "phase3_formal_v2_phase3v4_20260722/certifying_formal_filenames.txt"
)
IMAGE_MANIFEST = Path(
    "/home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/"
    "coco_referenced_images_manifest.jsonl"
)
COCO_ROOT = Path("/home/lizhaohui/lzq/phase3_runtime/coco2017_official/val2017")
OUTPUT = REPOSITORY / "experiments/phase3_v6/mismatch_audit"


def _hex(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()[:16]


def _image_row(index: int) -> dict:
    return {
        "filename": f"{index:012d}.jpg",
        "numeric_coco_id": index,
        "image_path": f"/tmp/{index:012d}.jpg",
        "image_sha256": hashlib.sha256(f"file:{index}".encode()).hexdigest(),
        "normalized_pixel_sha256": hashlib.sha256(
            f"pixels:{index}".encode()
        ).hexdigest(),
        "difference_hash": _hex(f"dhash:{index}"),
        "average_hash": _hex(f"ahash:{index}"),
        "width": 10 + index,
        "height": 20 + index,
        "mode": "RGB",
        "image_size_bytes": 100 + index,
        "record_count": 1,
        "valid_v6_record_count": 1,
        "has_valid_v6_record": True,
    }


def _all_nonself(count: int) -> list[list[int]]:
    return [[donor for donor in range(count) if donor != target] for target in range(count)]


class MismatchAuditUnitTests(unittest.TestCase):
    def test_single_round_has_no_self_match_and_unique_complete_donors(self):
        images = [_image_row(index) for index in range(9)]
        names = [row["filename"] for row in images]
        matching = deterministic_perfect_matching(
            names, _all_nonself(len(images)), round_id=1
        )
        self.assertEqual(len(matching), len(images))
        self.assertEqual(len(set(matching)), len(images))
        self.assertTrue(all(target != donor for target, donor in enumerate(matching)))

    def test_five_rounds_repeat_no_donor_for_a_target(self):
        images = [_image_row(index) for index in range(9)]
        rounds = build_k_matchings(images, _all_nonself(len(images)))
        for target in range(len(images)):
            self.assertEqual(len({round_[target] for round_ in rounds}), 5)

    def test_identical_file_sha256_is_hard_excluded(self):
        left, right = _image_row(1), _image_row(2)
        right["image_sha256"] = left["image_sha256"]
        self.assertIn("same_file_sha256", hard_exclusion_reasons(left, right))

    def test_identical_normalized_pixels_are_hard_excluded(self):
        left, right = _image_row(1), _image_row(2)
        right["normalized_pixel_sha256"] = left["normalized_pixel_sha256"]
        self.assertIn(
            "same_normalized_pixel_sha256", hard_exclusion_reasons(left, right)
        )

    def test_hard_perceptual_near_duplicate_is_excluded(self):
        left, right = _image_row(1), _image_row(2)
        left["difference_hash"] = left["average_hash"] = "0000000000000000"
        right["difference_hash"] = right["average_hash"] = "0000000000000001"
        self.assertIn(
            "hard_perceptual_near_duplicate", hard_exclusion_reasons(left, right)
        )

    def test_suspect_near_duplicate_is_flagged_but_not_hard_excluded(self):
        left, right = _image_row(1), _image_row(2)
        left["difference_hash"] = left["average_hash"] = "0000000000000000"
        right["difference_hash"] = "0000000000000001"
        right["average_hash"] = "0000000000000003"
        self.assertTrue(near_duplicate_suspect(left, right))
        self.assertNotIn(
            "hard_perceptual_near_duplicate", hard_exclusion_reasons(left, right)
        )

    def test_no_perfect_matching_fails_explicitly(self):
        names = [f"{index}.jpg" for index in range(3)]
        with self.assertRaisesRegex(RuntimeError, "no perfect matching"):
            deterministic_perfect_matching(
                names, [[1], [1], [1]], round_id=1
            )

    def test_fixed_seed_matching_and_serialization_are_reproducible(self):
        images = [_image_row(index) for index in range(9)]
        allowed = _all_nonself(len(images))
        first = build_k_matchings(images, allowed)
        second = build_k_matchings(images, allowed)
        self.assertEqual(first, second)
        names = [row["filename"] for row in images]
        self.assertEqual(
            sha256_bytes(assignment_core_payload(names, first)),
            sha256_bytes(assignment_core_payload(names, second)),
        )

    def test_different_rounds_have_different_hash_order_material(self):
        self.assertNotEqual(
            assignment_order_digest(1, "a.jpg", "b.jpg"),
            assignment_order_digest(2, "a.jpg", "b.jpg"),
        )

    def test_text_fields_do_not_affect_matching(self):
        images = [_image_row(index) for index in range(9)]
        allowed = _all_nonself(len(images))
        first = build_k_matchings(images, allowed)
        for index, row in enumerate(images):
            row["unconsulted_text"] = f"semantics {index}"
        second = build_k_matchings(images, allowed)
        self.assertEqual(first, second)

    def test_one_manifest_row_makes_all_filename_records_share_donors(self):
        images = [_image_row(index) for index in range(9)]
        rounds = build_k_matchings(images, _all_nonself(len(images)))
        rows = build_manifest_rows(images, rounds)
        self.assertEqual(len(rows), len(images))
        self.assertTrue(all(len(row["donor_rounds"]) == 5 for row in rows))

    def test_image_fingerprint_reads_image_and_detects_same_normalized_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.png"
            second = Path(directory) / "second.bmp"
            image = Image.new("RGB", (17, 11), (20, 40, 60))
            image.save(first)
            image.save(second)
            first_fp = image_fingerprint(first)
            second_fp = image_fingerprint(second)
            self.assertNotEqual(first_fp["image_sha256"], second_fp["image_sha256"])
            self.assertEqual(
                first_fp["normalized_pixel_sha256"],
                second_fp["normalized_pixel_sha256"],
            )

    def test_tfidf_diagnostic_is_deterministic(self):
        filenames = ["a.jpg", "b.jpg"]
        captions = {
            "a.jpg": build_caption_diagnostics(["A red car is parked."]),
            "b.jpg": build_caption_diagnostics(["A blue car is parked."]),
        }
        first_matrix, first_indices, first_meta = build_tfidf_matrix(
            filenames, captions
        )
        second_matrix, second_indices, second_meta = build_tfidf_matrix(
            filenames, captions
        )
        first = maximum_tfidf_for_pairs(
            [(0, 1)], filenames, first_matrix, first_indices
        )
        second = maximum_tfidf_for_pairs(
            [(0, 1)], filenames, second_matrix, second_indices
        )
        self.assertEqual(first, second)
        self.assertEqual(first_meta, second_meta)

    def test_lexical_similarity_metrics(self):
        left = build_caption_diagnostics(["A red car is parked."])
        right = build_caption_diagnostics(["A blue car is parked."])
        metrics = lexical_pair_metrics(left, right)
        self.assertGreater(metrics["maximum_unigram_jaccard"], 0)
        self.assertFalse(metrics["has_exact_normalized_positive_caption"])

    def test_hull_word_mention_classification(self):
        result = hull_mention_classification(
            {"blue", "car"}, ["red"], ["blue"]
        )
        self.assertEqual(result["classification"], "mentions_negative_only")

    def test_thumbnail_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.png"
            destination = Path(directory) / "thumb.jpg"
            Image.new("RGB", (400, 100), "red").save(source)
            generate_thumbnail(source, destination)
            with Image.open(destination) as thumbnail:
                self.assertEqual(thumbnail.size, (256, 256))

    def test_k_1_3_5_inference_estimation(self):
        filenames = [f"{index}.jpg" for index in range(6)]
        rounds = [
            [(index + offset) % 6 for index in range(6)]
            for offset in range(1, 6)
        ]
        result = projected_inference_counts(
            10, set(filenames), filenames, rounds, model_count=10
        )
        self.assertEqual(
            result["counts"]["K=1"]["per_model_text_sequence_score_count"], 40
        )
        self.assertEqual(
            result["counts"]["K=3"]["per_model_text_sequence_score_count"], 80
        )
        self.assertEqual(
            result["counts"]["K=5"]["per_model_text_sequence_score_count"], 120
        )

    def test_hamming_distance(self):
        self.assertEqual(hamming64("0000000000000000", "0000000000000003"), 2)


class MismatchAuditRealInputTests(unittest.TestCase):
    def test_1345_real_inputs_exist_uniquely_and_decode(self):
        names = CERTIFYING.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(names), 1345)
        self.assertEqual(len(set(names)), 1345)
        manifest = {row["filename"]: row for row in read_jsonl(IMAGE_MANIFEST)}
        for name in names:
            self.assertEqual(manifest[name]["status"], "ready")
            path = COCO_ROOT / name
            self.assertTrue(path.is_file())
            with Image.open(path) as image:
                image.verify()


class MismatchAuditGeneratedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = OUTPUT / "mismatch_manifest_k5.jsonl"
        cls.pair_path = OUTPUT / "mismatch_pair_diagnostics.jsonl"
        if not cls.manifest_path.is_file() or not cls.pair_path.is_file():
            raise AssertionError("run the mismatch audit before generated-artifact tests")
        cls.manifest = read_jsonl(cls.manifest_path)
        cls.pairs = read_jsonl(cls.pair_path)

    def test_generated_manifest_has_1345_targets_and_6725_pairs(self):
        self.assertEqual(len(self.manifest), 1345)
        self.assertEqual(len(self.pairs), 6725)

    def test_each_round_has_1345_unique_donors_and_no_self_match(self):
        for round_id in range(1, 6):
            rows = [row for row in self.pairs if row["round_id"] == round_id]
            self.assertEqual(len(rows), 1345)
            self.assertEqual(len({row["donor_filename"] for row in rows}), 1345)
            self.assertTrue(
                all(row["target_filename"] != row["donor_filename"] for row in rows)
            )

    def test_each_target_has_five_distinct_donors(self):
        for row in self.manifest:
            donors = [entry["donor_filename"] for entry in row["donor_rounds"]]
            self.assertEqual(len(donors), 5)
            self.assertEqual(len(set(donors)), 5)


if __name__ == "__main__":
    unittest.main()
