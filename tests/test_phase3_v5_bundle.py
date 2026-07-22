import tempfile
import unittest
from pathlib import Path

from experiments.phase3.build_phase3_bundle_v5 import build_bundle_v5
from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, content_hash, inventory_files, load_json_snapshot,
    sha256_bytes,
)
from experiments.phase3.phase3_protocol_v5 import build_protocol_payload_v5


class Phase3V5BundleTests(unittest.TestCase):
    def test_builder_hashes_every_internal_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            run = inputs / "run"
            run.mkdir()
            atomic_write_json(
                run / "run_status.json",
                {"run_mode": "smoke", "status": "success", "metric_version": "v5"},
            )
            atomic_write_json(run / "value.json", {"value": 1})
            code = inputs / "phase3_code_manifest_v5.json"
            atomic_write_json(code, {"schema_version": 1})
            code_sha = sha256_bytes(code.read_bytes())
            atomic_write_bytes(code.with_suffix(".sha256"), (code_sha + "\n").encode("ascii"))
            protocol = inputs / "phase3_protocol_candidate_v5.json"
            atomic_write_json(protocol, build_protocol_payload_v5(code_sha))
            protocol_sha = sha256_bytes(protocol.read_bytes())
            atomic_write_bytes(protocol.with_suffix(".sha256"), (protocol_sha + "\n").encode("ascii"))
            registry = inputs / "registry.json"
            receipt = inputs / "receipt.json"
            audit = inputs / "audit.json"
            atomic_write_json(registry, {"model_count": 10, "models": [{}] * 10})
            atomic_write_json(receipt, {"overall_status": "verified", "models": [{}] * 10})
            atomic_write_json(audit, {"overall_status": "verified", "models": [{}] * 10})
            for source in (receipt, audit):
                atomic_write_bytes(
                    source.with_suffix(".sha256"),
                    (sha256_bytes(source.read_bytes()) + "\n").encode("ascii"),
                )
            atomic_write_json(run / "run_manifest.json", {
                "run_mode": "smoke", "run_status": "success", "metric_version": "v5",
                "protocol_sha256": protocol_sha,
                "phase3_code_manifest_sha256": code_sha,
                "expected_model_registry_sha256": sha256_bytes(registry.read_bytes()),
                "model_verification_receipt_sha256": sha256_bytes(receipt.read_bytes()),
                "files": inventory_files(run, excluded=("run_manifest.json",)),
            })
            output = root / "outputs" / "bundle"
            build_bundle_v5(
                run_dir=run, protocol=protocol, code_manifest=code, expected_registry=registry,
                verification_receipt=receipt, description_bits_audit=audit, output_dir=output,
            )
            manifest = load_json_snapshot(output / "bundle_manifest.json", root=output)
            files = inventory_files(output, excluded=("bundle_manifest.json",))
            self.assertEqual(manifest["files"], files)
            self.assertEqual(manifest["bundle_content_hash"], content_hash(files))
            self.assertTrue(output.with_suffix(".sha256").is_file())


if __name__ == "__main__":
    unittest.main()
