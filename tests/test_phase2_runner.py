import json
import tempfile
import unittest
from pathlib import Path

from experiments.phase2_protocol import FrozenProtocol
from experiments.run_phase2_certificate import command_plan


class Phase2RunnerTest(unittest.TestCase):
    def test_plan_uses_frozen_primary_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path = root / "protocol.json"
            payload = {
                "schema_version": 1,
                "status": "frozen",
                "protocol_id": "toy",
                "run_id": "phase2",
                "dataset": {
                    "source_path": "dataset/source.parquet",
                    "exclude_paths": ["dataset/old.parquet"],
                    "train_size": 10,
                    "validation_size": 4,
                    "seed": 9,
                },
                "model": {
                    "hidden_size": 768,
                    "num_hidden_layers": 8,
                    "freeze_llm": 2,
                    "projector_type": "subspace",
                    "subspace_dim": 4096,
                    "subspace_seed": 42,
                    "train_norm": False,
                    "use_moe": False,
                    "initial_weight_name": "llm",
                },
                "training": {
                    "seed": 42, "epochs": 3, "batch_size": 4,
                    "accumulation_steps": 4, "learning_rate": 0.015,
                    "dtype": "bfloat16", "max_seq_len": 450,
                    "num_workers": 2, "augment": False,
                    "grad_clip": 1.0, "compile": False,
                },
                "evaluation": {
                    "batch_size": 8, "num_workers": 2,
                    "max_samples": 0, "dtype": "bfloat16",
                },
                "diagnostics": {
                    "alpha_grid": [0.1, 0.5],
                    "paired_shuffle_seed": 11,
                },
                "certificate": {"alpha": 0.5, "confidence_delta": 0.05},
                "compression": {"quantization_bits": 3, "codec": "zlib"},
                "decoder_registry": {"path": "experiments/registry.json", "index": 0},
                "environment_path": "experiments/environment.json",
            }
            protocol_path.write_text(json.dumps(payload))
            protocol = FrozenProtocol.load(protocol_path)
            plan = command_plan(protocol, root / "run", root / "bundle", "cuda:0")
            train = plan["train"][0]
            quantize = plan["quantize"][0]
            self.assertEqual(train[train.index("--subspace_dim") + 1], "4096")
            self.assertEqual(train[train.index("--learning_rate") + 1], "0.015")
            self.assertEqual(quantize[quantize.index("--bits") + 1], "3")
            self.assertIn("--entropy-code", quantize)
            self.assertEqual(len(plan["evaluate"]), 4)


if __name__ == "__main__":
    unittest.main()
