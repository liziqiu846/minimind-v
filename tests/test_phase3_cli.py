import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase3CLITests(unittest.TestCase):
    def test_all_contract_commands_expose_status_output(self):
        commands = (
            "build_expected_model_registry.py", "verify_stage2_artifacts.py", "prepare_phase3_data.py",
            "audit_training_overlap.py", "run_phase3_smoke_v2.py", "run_phase3_pilot_v2.py",
            "run_phase3_formal_v2.py", "build_phase3_bundle.py", "verify_phase3_bundle.py",
        )
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "experiments/phase3" / command), "--help"],
                    cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("--status-output", result.stdout)

    def test_cli_usage_errors_exit_64(self):
        command = ROOT / "experiments/phase3/build_expected_model_registry.py"
        result = subprocess.run(
            [sys.executable, str(command)], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        )
        self.assertEqual(result.returncode, 64, result.stdout)


if __name__ == "__main__":
    unittest.main()
