import subprocess
import unittest
from unittest.mock import patch

from experiments.run_stage2_parallel import idle_a40s, parse_gpu_inventory


class Stage2ParallelRunnerTests(unittest.TestCase):
    def test_inventory_parser_and_deterministic_order(self):
        rows = (
            "NVIDIA A40, GPU-b, 45000\n"
            "NVIDIA A40, GPU-a, 45000\n"
            "NVIDIA A100-PCIE-40GB, GPU-c, 40000\n"
        )
        self.assertEqual(parse_gpu_inventory(rows)[0]["uuid"], "GPU-b")
        results = [
            subprocess.CompletedProcess([], 0, stdout=rows, stderr=""),
            subprocess.CompletedProcess([], 0, stdout="GPU-b\n", stderr=""),
        ]
        with patch("experiments.run_stage2_parallel.subprocess.run", side_effect=results):
            idle = idle_a40s({"GPU-a", "GPU-b", "GPU-c"}, set())
        self.assertEqual([gpu["uuid"] for gpu in idle], ["GPU-a"])

    def test_reserved_gpu_is_not_reported_idle(self):
        rows = "NVIDIA A40, GPU-a, 46000\nNVIDIA A40, GPU-b, 44000\n"
        results = [
            subprocess.CompletedProcess([], 0, stdout=rows, stderr=""),
            subprocess.CompletedProcess([], 0, stdout="", stderr=""),
        ]
        with patch("experiments.run_stage2_parallel.subprocess.run", side_effect=results):
            idle = idle_a40s({"GPU-a", "GPU-b"}, {"GPU-a"})
        self.assertEqual([gpu["uuid"] for gpu in idle], ["GPU-b"])


if __name__ == "__main__":
    unittest.main()
