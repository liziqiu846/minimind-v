import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.stage2_protocol import Stage2Protocol


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


class Stage2ProtocolTests(unittest.TestCase):
    def test_confirmation_data_is_bound_through_both_post_tag_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            train = directory / "train.parquet"
            validation = directory / "validation.parquet"
            train.write_bytes(b"train")
            validation.write_bytes(b"validation")
            protocol = Stage2Protocol(
                path=directory / "stage2_protocol.json",
                sha256="ab" * 32,
                payload={
                    "status": "frozen",
                    "protocol_id": "minimind-v-stage2-joint-compression-v1",
                    "data": {
                        "output_directory": str(directory),
                        "source_sha256": "cd" * 32,
                        "selection_seed": 2026,
                        "train_images": 10000,
                        "validation_images": 2000,
                        "post_tag_receipts": {
                            "split_manifest": "split_manifest.json",
                            "independent_verification": "verification.json",
                        },
                    },
                },
            )
            manifest = {
                "schema_version": 1,
                "protocol": protocol.reference(),
                "source": {"sha256": "cd" * 32},
                "selection": {
                    "seed": 2026,
                    "validation_first": 2000,
                    "training_second": 10000,
                },
                "outputs": {
                    "train": {
                        "rows": 10000,
                        "sha256": hashlib.sha256(b"train").hexdigest(),
                    },
                    "validation": {
                        "rows": 2000,
                        "sha256": hashlib.sha256(b"validation").hexdigest(),
                    },
                },
                "invariants": {
                    "exact_unique_and_disjoint": True,
                    "target_eos_present": True,
                    "vlm_length_at_most_450": True,
                    "selected_phash_unique": True,
                },
            }
            manifest_path = directory / "split_manifest.json"
            write_json(manifest_path, manifest)
            verification = {
                "schema_version": 1,
                "status": "passed",
                "protocol": protocol.reference(),
                "split_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                "train_sha256": hashlib.sha256(b"train").hexdigest(),
                "validation_sha256": hashlib.sha256(b"validation").hexdigest(),
                "verified_images": 12000,
                "invariants": {"independent_replay": True},
            }
            write_json(directory / "verification.json", verification)

            receipt = protocol.verify_confirmation_data(train, "train")
            self.assertEqual(receipt["data_sha256"], hashlib.sha256(b"train").hexdigest())

            train.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "split manifest"):
                protocol.verify_confirmation_data(train, "train")


if __name__ == "__main__":
    unittest.main()
