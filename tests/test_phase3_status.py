import tempfile
import unittest
from pathlib import Path

from experiments.phase3.canonical_io import atomic_write_bytes, load_json_snapshot, load_jsonl_snapshot
from experiments.phase3.status import EXIT_CODES, Phase3Blocked, Phase3HardFailure, execute_with_status


class Phase3StatusTests(unittest.TestCase):
    def _run(self, operation):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "status.json"
        code = execute_with_status("test", path, operation)
        return code, load_json_snapshot(path)

    def test_success_blocked_and_hard_failure_exit_codes(self):
        code, value = self._run(lambda: {"answer": 1})
        self.assertEqual((code, value["status"]), (EXIT_CODES["success"], "success"))

        def blocked():
            raise Phase3Blocked("missing", "resource")
        code, value = self._run(blocked)
        self.assertEqual((code, value["status"], value["status_code"]), (2, "blocked", "missing"))

        def hard():
            raise Phase3HardFailure("bad", "invariant")
        code, value = self._run(hard)
        self.assertEqual((code, value["status"], value["status_code"]), (1, "hard_failure", "bad"))
        required = {"schema_version", "command", "status", "status_code", "blocking_items", "hard_failures", "completed_actions", "skipped_actions", "outputs"}
        self.assertEqual(set(value), required)

    def test_noncanonical_json_and_jsonl_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "value.json"
            jsonl_path = root / "rows.jsonl"
            atomic_write_bytes(json_path, b'{"b":1, "a":2}\n')
            atomic_write_bytes(jsonl_path, b'{"a":1} \n')
            with self.assertRaisesRegex(ValueError, "not canonical"):
                load_json_snapshot(json_path)
            with self.assertRaisesRegex(ValueError, "not canonical"):
                load_jsonl_snapshot(jsonl_path)

    def test_existing_status_is_not_overwritten_and_operation_is_not_called(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "status.json"
            atomic_write_bytes(path, b"user input bytes")
            called = []
            code = execute_with_status("test", path, lambda: called.append(True))
            self.assertEqual(code, EXIT_CODES["hard_failure"])
            self.assertEqual(called, [])
            self.assertEqual(path.read_bytes(), b"user input bytes")


if __name__ == "__main__":
    unittest.main()
