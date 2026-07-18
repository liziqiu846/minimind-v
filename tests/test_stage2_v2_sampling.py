import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image
from transformers import AutoTokenizer

from experiments.build_stage2_dataset_v2 import (
    build_eligible_catalog,
    catalog_row_rank,
    draw_catalog_index,
    materialize_draws,
    select_catalog_source_indices,
)
from experiments.verify_stage2_dataset_v2 import (
    independent_draw,
    independent_row_rank,
    independently_select_rows,
    reconstruct_catalog,
)
from experiments.evaluate_stage2_risk import pair_swap_permutation_v2
from experiments.stage2_protocol import Stage2Protocol


CATALOG_DOMAIN = "stage2-v2-catalog-row-v1"
VALIDATION_DOMAIN = "stage2-v2-validation-draw-v1"
TRAIN_DOMAIN = "stage2-v2-train-draw-v1"


class Stage2V2SamplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer = AutoTokenizer.from_pretrained(
            "/home/lizhaohui/lzq/stage2-assets-v1/tokenizer", local_files_only=True
        )

    def test_catalog_row_rank_known_vectors_and_independent_implementation(self):
        expected = (
            "63aba36fde0c5020aa93009903eb769c24a2a46f9893a305a58ee4b83babc127"
        )
        self.assertEqual(catalog_row_rank(CATALOG_DOMAIN, 2028, 0).hex(), expected)
        self.assertEqual(independent_row_rank(CATALOG_DOMAIN, 2028, 0).hex(), expected)
        self.assertEqual(
            catalog_row_rank(CATALOG_DOMAIN, 2028, 1_274_697).hex(),
            "0bdc538c616cd397daa2294cea90bdd6c2b94c1d86ca32042efecebf4f0c8574",
        )

    def test_catalog_source_indices_are_lowest_value_independent_ranks(self):
        expected_indices = [5, 6, 2, 0]
        selected = select_catalog_source_indices(10, 4, CATALOG_DOMAIN, 2028)
        independent = independently_select_rows(10, 4, CATALOG_DOMAIN, 2028)
        naive = sorted(
            (
                (index, catalog_row_rank(CATALOG_DOMAIN, 2028, index))
                for index in range(10)
            ),
            key=lambda item: (item[1], item[0]),
        )[:4]
        self.assertEqual([index for index, _ in selected], expected_indices)
        self.assertEqual(selected, naive)
        self.assertEqual(selected, independent)

    def test_domain_separated_unbiased_draw_known_vectors(self):
        expected_validation = [2594, 3481, 9815, 107]
        expected_train = [13127, 9648, 13264, 3860]
        for domain, expected in (
            (VALIDATION_DOMAIN, expected_validation),
            (TRAIN_DOMAIN, expected_train),
        ):
            actual = [
                draw_catalog_index(domain, 2028, index, 13789)
                for index in range(4)
            ]
            replay = [
                independent_draw(domain, 2028, index, 13789)
                for index in range(4)
            ]
            self.assertEqual([item[0] for item in actual], expected)
            self.assertEqual(actual, replay)
        self.assertNotEqual(expected_validation, expected_train)

    def test_repeated_catalog_units_remain_distinct_draws(self):
        catalog = [
            {
                "catalog_index": index,
                "catalog_unit_id": f"unit-{index}",
                "image_sha256": f"{index:064x}",
            }
            for index in range(2)
        ]
        rows = materialize_draws(catalog, "train", 20, TRAIN_DOMAIN, 2028)
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({row["sample_id"] for row in rows}), 20)
        self.assertLess(len({row["catalog_index"] for row in rows}), 20)
        for draw_index, row in enumerate(rows):
            expected_index, retry, digest = independent_draw(
                TRAIN_DOMAIN, 2028, draw_index, len(catalog)
            )
            self.assertEqual(row["catalog_index"], expected_index)
            self.assertEqual(row["draw_retry_index"], retry)
            self.assertEqual(row["draw_sha256"], digest)

    def test_duplicate_aware_pairing_never_pairs_equal_images(self):
        hashes = ["00" * 32, "00" * 32, "01" * 32, "02" * 32, "03" * 32, "04" * 32]
        identities = [f"draw-{index}" for index in range(len(hashes))]
        permutation = pair_swap_permutation_v2(hashes, identities)
        self.assertTrue(
            all(permutation[permutation[index]] == index for index in range(len(hashes)))
        )
        self.assertTrue(
            all(hashes[index] != hashes[permutation[index]] for index in range(len(hashes)))
        )

    def test_duplicate_aware_pairing_stops_when_impossible(self):
        hashes = ["00" * 32] * 4 + ["01" * 32, "02" * 32]
        identities = [f"draw-{index}" for index in range(len(hashes))]
        with self.assertRaisesRegex(ValueError, "no unequal-image"):
            pair_swap_permutation_v2(hashes, identities)

    def test_independent_verifier_reconstructs_exact_catalog_and_representative(self):
        def png(color):
            stream = io.BytesIO()
            Image.new("RGB", (8, 8), color).save(stream, format="PNG")
            return stream.getvalue()

        def conversation(answer):
            return json.dumps(
                [
                    {"role": "user", "content": "Describe. <image>"},
                    {"role": "assistant", "content": answer},
                ]
            )

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.parquet"
            image_a = png((255, 0, 0))
            rows = [
                {"image_bytes": image_a, "conversations": conversation("first")},
                {"image_bytes": image_a, "conversations": conversation("second")},
                {"image_bytes": png((0, 255, 0)), "conversations": conversation("green")},
                {"image_bytes": png((0, 0, 255)), "conversations": "malformed"},
            ]
            pq.write_table(pa.Table.from_pylist(rows), source)
            exact_history = directory / "history_exact.txt"
            phash_history = directory / "history_phash.txt"
            exact_history.write_text("", encoding="utf-8")
            phash_history.write_text("", encoding="utf-8")
            protocol = Stage2Protocol(
                path=directory / "protocol.json",
                sha256="00" * 32,
                payload={
                    "schema_version": 2,
                    "history_exclusion": {
                        "exact_sha256_path": str(exact_history),
                        "phash_path": str(phash_history),
                    },
                    "model": {"image_token_count": 64},
                    "training": {"max_sequence_length": 450},
                    "data": {
                        "phash": {
                            "hash_size": 8,
                            "highfreq_factor": 4,
                            "maximum_allowed_historical_hamming_distance": 6,
                        }
                    },
                },
            )
            selected = [
                (index, catalog_row_rank(CATALOG_DOMAIN, 2028, index))
                for index in range(len(rows))
            ]
            catalog, _, counters = build_eligible_catalog(
                protocol, source, selected, self.tokenizer
            )
            with patch.object(Stage2Protocol, "asset_path", return_value=source):
                replay = reconstruct_catalog(protocol, selected, self.tokenizer)
            self.assertEqual(catalog, replay)
            self.assertEqual(len(catalog), 2)
            self.assertEqual(counters["eligible_exact_duplicates"], 1)
            self.assertEqual(counters["token_or_template_ineligible"], 1)
            self.assertEqual(
                [row["image_sha256"] for row in catalog],
                sorted(row["image_sha256"] for row in catalog),
            )


if __name__ == "__main__":
    unittest.main()
