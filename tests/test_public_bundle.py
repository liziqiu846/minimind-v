import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.build_public_bundle import build_public_bundle


class PublicBundleTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_source(self, name: str, content: bytes) -> Path:
        path = self.sources / name
        path.write_bytes(content)
        return path

    def test_bundle_copies_files_and_records_relative_integrity_metadata(self):
        archive = self.write_source("weights.mms", b"compressed-weights")
        report = self.write_source("bound.json.gz", b"compressed-report")
        output = self.root / "public_bundle"

        returned = build_public_bundle(
            output,
            [("compressed_model", archive), ("bound_report", report)],
        )
        stored = json.loads((output / "bundle_index.json").read_text())

        self.assertEqual(stored, returned)
        self.assertEqual(stored["schema_version"], 1)
        self.assertEqual(len(stored["artifacts"]), 2)
        indexed_paths = {item["path"] for item in stored["artifacts"]}
        self.assertNotIn("bundle_index.json", indexed_paths)
        for item in stored["artifacts"]:
            path = Path(item["path"])
            self.assertFalse(path.is_absolute())
            copied = output / path
            self.assertEqual(item["bytes"], copied.stat().st_size)
            self.assertEqual(
                item["sha256"], hashlib.sha256(copied.read_bytes()).hexdigest()
            )
        self.assertEqual(
            (output / "artifacts/weights.mms").read_bytes(), archive.read_bytes()
        )
        self.assertEqual(
            (output / "artifacts/bound.json.gz").read_bytes(), report.read_bytes()
        )
        self.assertNotIn(str(self.root), (output / "bundle_index.json").read_text())
        self.assertEqual(list(output.glob(".*.tmp")), [])

    def test_existing_output_is_not_overwritten(self):
        source = self.write_source("result.json", b"new")
        output = self.root / "public_bundle"
        output.mkdir()
        marker = output / "marker"
        marker.write_bytes(b"keep")

        with self.assertRaises(FileExistsError):
            build_public_bundle(output, [("result", source)])

        self.assertEqual(marker.read_bytes(), b"keep")

    def test_duplicate_roles_are_rejected_before_output_creation(self):
        first = self.write_source("first.json", b"first")
        second = self.write_source("second.json", b"second")
        output = self.root / "public_bundle"

        with self.assertRaises(ValueError):
            build_public_bundle(output, [("risk", first), ("risk", second)])

        self.assertFalse(output.exists())

    def test_duplicate_file_names_are_rejected(self):
        first = self.write_source("same.json", b"first")
        other_directory = self.root / "other"
        other_directory.mkdir()
        second = other_directory / "same.json"
        second.write_bytes(b"second")

        with self.assertRaises(ValueError):
            build_public_bundle(
                self.root / "public_bundle",
                [("train_risk", first), ("validation_risk", second)],
            )


if __name__ == "__main__":
    unittest.main()
