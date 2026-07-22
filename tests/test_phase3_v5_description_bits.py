import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.phase3 import audit_description_bits_v5 as audit
from experiments.phase3.canonical_io import atomic_write_bytes, atomic_write_json


class Phase3V5DescriptionBitTests(unittest.TestCase):
    def test_complete_file_bits_plus_four(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            models = []
            registry_rows = []
            for index in range(10):
                payload = bytes([index]) * (index + 1)
                relative = f"m{index}.mms2"
                atomic_write_bytes(root / relative, payload)
                row = {
                    "model_id": f"m{index}", "method": "M0", "mapping_root": index,
                    "artifact_relative_path": relative, "artifact_size_bytes": len(payload),
                    "artifact_sha256": hashlib.sha256(payload).hexdigest(),
                }
                models.append(dict(row))
                registry_rows.append(dict(row))
            registry = root / "registry.json"
            atomic_write_json(registry, {"schema_version": 2, "model_count": 10, "models": registry_rows})

            def decoded(payload, expected):
                return None, {"model_group": expected["method"], "mapping_root": expected["mapping_root"]}

            with mock.patch.object(audit, "MODELS", tuple(models)), mock.patch.object(audit, "verify_payload", side_effect=decoded):
                result = audit.audit_description_bits_v5(registry, root)
            self.assertEqual(len(result["models"]), 10)
            for row in result["models"]:
                self.assertEqual(row["artifact_file_bits"], row["artifact_size_bytes"] * 8)
                self.assertEqual(row["total_description_bits"], row["artifact_file_bits"] + 4)


if __name__ == "__main__":
    unittest.main()
