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

    def test_v2_confirmation_data_binds_catalog_and_both_replays(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            files = {
                "catalog": directory / "eligible_catalog.parquet",
                "train": directory / "train.parquet",
                "validation": directory / "validation.parquet",
            }
            for name, path in files.items():
                path.write_bytes(name.encode("utf-8"))
            protocol = Stage2Protocol(
                path=directory / "stage2_protocol_v2.json",
                sha256="12" * 32,
                payload={
                    "schema_version": 2,
                    "status": "frozen",
                    "protocol_id": "minimind-v-stage2-joint-compression-v2",
                    "data": {
                        "output_directory": str(directory),
                        "source_sha256": "34" * 32,
                        "source_rows": 10,
                        "selection_seed": 2028,
                        "catalog": {
                            "row_rank_domain": "catalog-domain",
                            "source_row_capacity": 4,
                            "minimum_eligible_units": 1,
                        },
                        "independent_draws": {
                            "train_domain": "train-domain",
                            "validation_domain": "validation-domain",
                            "train_draws": 2,
                            "validation_draws": 1,
                        },
                        "post_tag_receipts": {
                            "catalog": "eligible_catalog.parquet",
                            "catalog_manifest": "catalog_manifest.json",
                            "split_manifest": "split_manifest.json",
                            "independent_verification": "verification.json",
                            "replay_verification": "replay_verification.json",
                        },
                    },
                },
            )
            reference = protocol.reference()
            catalog_sha = hashlib.sha256(b"catalog").hexdigest()
            catalog_manifest = {
                "schema_version": 2,
                "protocol": reference,
                "source": {"sha256": "34" * 32, "rows": 10},
                "row_selection": {
                    "seed": 2028,
                    "domain": "catalog-domain",
                    "capacity": 4,
                    "independent_of_row_contents": True,
                },
                "outputs": {"catalog_rows": 2, "catalog_sha256": catalog_sha},
                "invariants": {"catalog_pass": True},
            }
            catalog_manifest_path = directory / "catalog_manifest.json"
            write_json(catalog_manifest_path, catalog_manifest)
            catalog_manifest_sha = hashlib.sha256(
                catalog_manifest_path.read_bytes()
            ).hexdigest()
            split_manifest = {
                "schema_version": 2,
                "protocol": reference,
                "catalog": {
                    "sha256": catalog_sha,
                    "manifest_sha256": catalog_manifest_sha,
                },
                "sampling": {
                    "seed": 2028,
                    "method": "independent_with_replacement",
                    "validation_domain": "validation-domain",
                    "train_domain": "train-domain",
                    "unbiased_rejection_mapping": True,
                    "duplicates_allowed_without_redraw": True,
                    "cross_split_overlap_allowed_without_redraw": True,
                },
                "outputs": {
                    "train": {
                        "rows": 2,
                        "sha256": hashlib.sha256(b"train").hexdigest(),
                    },
                    "validation": {
                        "rows": 1,
                        "sha256": hashlib.sha256(b"validation").hexdigest(),
                    },
                },
                "invariants": {"split_pass": True},
            }
            split_manifest_path = directory / "split_manifest.json"
            write_json(split_manifest_path, split_manifest)
            split_manifest_sha = hashlib.sha256(split_manifest_path.read_bytes()).hexdigest()
            verification = {
                "schema_version": 2,
                "status": "passed",
                "protocol": reference,
                "catalog_sha256": catalog_sha,
                "catalog_manifest_sha256": catalog_manifest_sha,
                "split_manifest_sha256": split_manifest_sha,
                "verified_catalog_units": 2,
                "verified_draws": 3,
                "train_sha256": hashlib.sha256(b"train").hexdigest(),
                "validation_sha256": hashlib.sha256(b"validation").hexdigest(),
                "invariants": {"reconstruction_pass": True},
            }
            replay = {
                "schema_version": 2,
                "status": "passed",
                "protocol": reference,
                "catalog_sha256": catalog_sha,
                "catalog_manifest_sha256": catalog_manifest_sha,
                "split_manifest_sha256": split_manifest_sha,
                "catalog_units": 2,
                "train_draws": 2,
                "validation_draws": 1,
            }
            write_json(directory / "verification.json", verification)
            write_json(directory / "replay_verification.json", replay)

            receipt = protocol.verify_confirmation_data(files["train"], "train")
            self.assertEqual(receipt["catalog_sha256"], catalog_sha)

            replay["train_draws"] = 1
            write_json(directory / "replay_verification.json", replay)
            with self.assertRaisesRegex(ValueError, "counts"):
                protocol.verify_confirmation_data(files["train"], "train")


if __name__ == "__main__":
    unittest.main()
