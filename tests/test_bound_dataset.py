import gzip
import json
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from experiments.build_bound_dataset import (
    RepresentativeRow,
    digest_bytes,
    image_hashes_from_parquet,
    select_split_rows,
    write_membership_atomic,
)


class BoundDatasetTest(unittest.TestCase):
    def test_selection_excludes_prior_images(self):
        images = [digest_bytes(bytes([index])) for index in range(6)]
        representatives = {
            image: RepresentativeRow(index, digest_bytes(b"conversation"))
            for index, image in enumerate(images)
        }
        split = select_split_rows(
            representatives,
            train_size=2,
            validation_size=2,
            seed=7,
            excluded_images={images[0], images[1]},
        )
        self.assertEqual(len(split.train_indices), 2)
        self.assertEqual(len(split.validation_indices), 2)
        self.assertTrue({0, 1}.isdisjoint(split.train_indices))
        self.assertTrue({0, 1}.isdisjoint(split.validation_indices))

    def test_membership_records_source_rows_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "membership.jsonl.gz"
            table = pa.table({"image_sha256": ["aa", "bb"]})
            write_membership_atomic(table, (3, 8), path)
            with gzip.open(path, "rt") as handle:
                records = [json.loads(line) for line in handle]
            self.assertEqual(
                records,
                [
                    {"source_row": 3, "image_sha256": "aa"},
                    {"source_row": 8, "image_sha256": "bb"},
                ],
            )

    def test_exclusion_hash_column_is_checked_against_image_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "old.parquet"
            pq.write_table(
                pa.table({"image_bytes": [b"image"], "image_sha256": ["00" * 32]}),
                path,
            )
            with self.assertRaises(ValueError):
                image_hashes_from_parquet(path)


if __name__ == "__main__":
    unittest.main()
