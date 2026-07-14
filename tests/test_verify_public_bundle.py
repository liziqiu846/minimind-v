import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.build_public_bundle import build_public_bundle
from experiments.compute_bound_report import build_report
from experiments.verify_public_bundle import artifact_map, verify_public_bundle


class VerifyPublicBundleTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_json(self, name: str, value: dict) -> Path:
        path = self.sources / name
        path.write_text(json.dumps(value, indent=2) + "\n")
        return path

    def make_certificate_bundle(self, output: Path, tamper_bound: bool = False) -> Path:
        choice = {
            "family": "fixed_subspace",
            "subspace_dim": 4096,
            "train_norm": False,
            "quantization_bits": 3,
            "codec": "zlib",
        }
        registry = {"schema_version": 1, "decoders": [{"id": "primary", "choice": choice}]}
        registry_path = self.write_json("registry.json", registry)
        registry_sha256 = hashlib.sha256(registry_path.read_bytes()).hexdigest()
        environment_path = self.write_json("environment.json", {"schema_version": 1})
        environment_sha256 = hashlib.sha256(environment_path.read_bytes()).hexdigest()
        protocol = {
            "schema_version": 1,
            "status": "frozen",
            "protocol_id": "toy-protocol",
            "run_id": "toy-run",
            "dataset": {
                "source_sha256": "source-data",
                "train_size": 100,
                "validation_size": 20,
            },
            "certificate": {
                "alpha": 0.1,
                "alpha_selection_bits": 0,
                "decoder_selection_bits": 0,
                "confidence_delta": 0.05,
            },
            "model": {
                "hidden_size": 768,
                "num_hidden_layers": 8,
                "use_moe": False,
                "freeze_llm": 2,
                "projector_type": "subspace",
                "subspace_dim": 4096,
                "subspace_seed": 42,
                "train_norm": False,
                "fixed_state_sha256": "fixed-projector",
                "projector_protocol": "toy-projector-v1",
                "initial_weight_name": "llm",
            },
            "training": {"seed": 42},
            "decoder_registry": {
                "path": "experiments/registry.json",
                "sha256": registry_sha256,
                "index": 0,
            },
            "environment_path": "experiments/environment.json",
            "environment_sha256": environment_sha256,
            "implementation_files": [],
        }
        protocol_path = self.write_json("protocol.json", protocol)
        protocol_reference = {
            "protocol_id": "toy-protocol",
            "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        }
        train_membership = self.sources / "train_membership.jsonl.gz"
        validation_membership = self.sources / "validation_membership.jsonl.gz"
        train_membership.write_bytes(b"train-membership")
        validation_membership.write_bytes(b"validation-membership")
        def membership(path: Path) -> dict:
            return {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        receipt = {
            "schema_version": 2,
            "protocol_id": "toy-protocol",
            "protocol_sha256": protocol_reference["protocol_sha256"],
            "source_sha256": "source-data",
            "image_overlap": 0,
            "outputs": {
                "train": {
                    "sha256": "train-data", "rows": 100,
                    "membership": membership(train_membership),
                },
                "validation": {
                    "sha256": "validation-data", "rows": 20,
                    "membership": membership(validation_membership),
                },
            },
        }
        receipt_path = self.write_json("split_manifest.json", receipt)
        receipt_sha256 = hashlib.sha256(receipt_path.read_bytes()).hexdigest()

        def split_link(role: str, data_sha256: str, examples: int) -> dict:
            return {
                "role": role,
                "manifest_path": "/private/split_manifest.json",
                "manifest_sha256": receipt_sha256,
                "artifact_sha256": data_sha256,
                "examples": examples,
            }

        manifest = {
            "schema_version": 2,
            "run_id": "toy-run",
            "protocol_id": "toy-protocol",
            "protocol_sha256": protocol_reference["protocol_sha256"],
            "data": {"path": "/private/train.parquet", "sha256": "train-data", "examples": 100},
            "initial_weight": {
                "name": "llm", "path": "/private/initial.pth", "sha256": "reference"
            },
            "model": {
                "hidden_size": 768,
                "num_hidden_layers": 8,
                "use_moe": False,
                "freeze_llm": 2,
                "projector": {
                    "type": "subspace",
                    "subspace_dim": 4096,
                    "subspace_seed": 42,
                    "train_norm": False,
                    "fixed_state_sha256": "fixed-projector",
                    "protocol": "toy-projector-v1",
                },
            },
            "training": {"seed": 42},
            "dataset_split": split_link("train", "train-data", 100),
        }
        manifest_path = self.write_json("run_manifest.json", manifest)
        archive_path = self.sources / "model.mms"
        archive_path.write_bytes(b"encoded-model")
        archive_sha256 = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        encoding = {
            "run_id": "toy-run",
            "archive": "/private/model.mms",
            "archive_sha256": archive_sha256,
            "encoded_weight_bits": archive_path.stat().st_size * 8,
            "decoded_checkpoint": "/private/decoded.pth",
            "decoded_checkpoint_sha256": "decoded",
            "reference_sha256": "reference",
            "decoder_choice": choice,
            "decoder_id": "primary",
            "protocol": protocol_reference,
        }
        encoding_path = self.write_json("encoding.json", encoding)
        assets = {"fixed": "asset-hashes"}
        training = {
            "run_id": "toy-run",
            "model_kind": "decoded_quantized",
            "checkpoint": "/private/decoded.pth",
            "checkpoint_sha256": "decoded",
            "data_path": "/private/train.parquet",
            "data_sha256": "train-data",
            "image_condition": "correct",
            "model_assets": assets,
            "alpha_choice_bits": 0,
            "sample_count": 100,
            "vocab_size": 10,
            "risks": [{"alpha": 0.1, "mean_sample_risk_bits": 2.0}],
            "dataset_split": split_link("train", "train-data", 100),
            "protocol": protocol_reference,
        }
        validation = {
            "run_id": "toy-run",
            "model_kind": "decoded_quantized",
            "checkpoint": "/private/decoded.pth",
            "checkpoint_sha256": "decoded",
            "data_path": "/private/validation.parquet",
            "data_sha256": "validation-data",
            "image_condition": "correct",
            "model_assets": assets,
            "sample_count": 20,
            "vocab_size": 10,
            "risks": [{"alpha": 0.1, "mean_sample_risk_bits": 2.25}],
            "dataset_split": split_link("validation", "validation-data", 20),
            "protocol": protocol_reference,
        }
        training_path = self.write_json("train_risk.json", training)
        validation_path = self.write_json("validation_correct.json", validation)
        bound = build_report(
            encoding,
            training,
            validation,
            confidence_delta=0.05,
            encoded_weight_bits=archive_path.stat().st_size * 8,
            model_selection_bits=0,
        )
        bound.update(
            {
                "schema_version": 2,
                "protocol": protocol_reference,
                "decoder_registry": "/private/registry.json",
                "decoder_registry_sha256": registry_sha256,
                "decoder_choice_count": 1,
                "decoder_choice": choice,
                "run_manifest": "/private/run_manifest.json",
                "run_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            }
        )
        if tamper_bound:
            bound["best_compression_upper_bound_bits"] += 0.25
        bound_path = self.write_json("bound.json", bound)
        build_public_bundle(
            output,
            [
                ("protocol", protocol_path),
                ("decoder_registry", registry_path),
                ("compressed_model", archive_path),
                ("encoding", encoding_path),
                ("train_risk", training_path),
                ("validation_correct", validation_path),
                ("bound", bound_path),
                ("dataset_receipt", receipt_path),
                ("run_manifest", manifest_path),
                ("environment", environment_path),
                ("train_membership", train_membership),
                ("validation_membership", validation_membership),
            ],
        )
        return output

    def test_index_integrity_and_artifact_map(self):
        source = self.sources / "result.json"
        source.write_bytes(b"result")
        bundle = self.root / "basic_bundle"
        build_public_bundle(bundle, [("result", source)])

        paths = artifact_map(bundle)
        self.assertEqual(paths["result"].read_bytes(), b"result")
        paths["result"].write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            artifact_map(bundle)

    def test_duplicate_roles_and_escaping_paths_are_rejected(self):
        source = self.sources / "result.json"
        source.write_bytes(b"result")
        bundle = self.root / "bad_index_bundle"
        build_public_bundle(bundle, [("result", source)])
        index_path = bundle / "bundle_index.json"
        index = json.loads(index_path.read_text())
        index["artifacts"].append(dict(index["artifacts"][0]))
        index_path.write_text(json.dumps(index))
        with self.assertRaises(ValueError):
            artifact_map(bundle)

        index["artifacts"] = [index["artifacts"][0]]
        index["artifacts"][0]["path"] = "../result.json"
        index_path.write_text(json.dumps(index))
        with self.assertRaises(ValueError):
            artifact_map(bundle)

    def test_complete_certificate_recomputes_with_absolute_json_paths_ignored(self):
        bundle = self.make_certificate_bundle(self.root / "certificate_bundle")
        result = verify_public_bundle(bundle)

        self.assertTrue(result["certificate_verified"])
        self.assertEqual(result["certificate"]["run_id"], "toy-run")
        self.assertEqual(result["verified_artifacts"], 12)

    def test_bound_core_field_tampering_is_detected(self):
        bundle = self.make_certificate_bundle(
            self.root / "tampered_bound_bundle", tamper_bound=True
        )
        with self.assertRaises(ValueError):
            verify_public_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
