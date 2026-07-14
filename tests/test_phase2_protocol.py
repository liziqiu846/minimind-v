import json
import tempfile
import unittest
from pathlib import Path

from experiments.phase2_protocol import FrozenProtocol, sha256_file, validate_split_artifact


class Phase2ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.protocol_path = self.root / "protocol.json"
        self.protocol_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "frozen",
                    "protocol_id": "toy",
                    "training": {"seed": 7, "epochs": 3},
                    "dataset": {
                        "source_sha256": "source",
                        "excluded_unique_images": 0,
                        "exclude_sha256": [],
                        "seed": 7,
                        "selection": "toy_selection",
                        "train_size": 1,
                    },
                    "implementation_files": [],
                }
            )
        )
        self.protocol = FrozenProtocol.load(self.protocol_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_require_reports_configuration_mismatch(self):
        self.protocol.require("training", {"seed": 7, "epochs": 3}, ("seed", "epochs"))
        with self.assertRaises(ValueError):
            self.protocol.require(
                "training", {"seed": 8, "epochs": 3}, ("seed", "epochs")
            )

    def test_split_artifact_is_linked_by_protocol_and_hash(self):
        data_path = self.root / "train.parquet"
        data_path.write_bytes(b"train")
        manifest_path = self.root / "split_manifest.json"
        membership_path = self.root / "train_membership.jsonl.gz"
        membership_path.write_bytes(b"membership")
        manifest_path.write_text(
            json.dumps(
                {
                    "protocol_sha256": self.protocol.sha256,
                    "protocol_id": "toy",
                    "source_sha256": "source",
                    "excluded_unique_images": 0,
                    "exclusions": [],
                    "seed": 7,
                    "selection": "toy_selection",
                    "image_overlap": 0,
                    "outputs": {
                        "train": {
                            "sha256": sha256_file(data_path),
                            "rows": 1,
                            "membership": {
                                "path": membership_path.name,
                                "sha256": sha256_file(membership_path),
                            },
                        }
                    },
                }
            )
        )
        metadata = validate_split_artifact(
            manifest_path, data_path, "train", self.protocol
        )
        self.assertEqual(metadata["examples"], 1)
        data_path.write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            validate_split_artifact(manifest_path, data_path, "train", self.protocol)

    def test_unfrozen_protocol_is_rejected(self):
        payload = json.loads(self.protocol_path.read_text())
        payload["status"] = "draft"
        self.protocol_path.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            FrozenProtocol.load(self.protocol_path)


if __name__ == "__main__":
    unittest.main()
