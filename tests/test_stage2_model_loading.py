import unittest

import torch
from torch import nn

from experiments.stage2_model import validate_initial_llm_load


class TinyVLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.language = nn.Linear(2, 2, bias=False)
        self.lm_head = nn.Linear(2, 2, bias=False)
        self.vision_encoder = nn.Linear(2, 2, bias=False)
        self.vision_proj = nn.Linear(2, 2, bias=False)


class Stage2ModelLoadingTests(unittest.TestCase):
    def setUp(self):
        self.model = TinyVLM()
        self.initial = {
            "language.weight": torch.arange(4, dtype=torch.float32).reshape(2, 2),
            "lm_head.weight": torch.arange(4, 8, dtype=torch.float32).reshape(2, 2),
        }
        self.model.load_state_dict(self.initial, strict=False)

    def test_vlm_allows_only_separately_constructed_vision_keys(self):
        receipt = validate_initial_llm_load(
            "M2",
            self.model,
            self.initial,
            ["vision_encoder.weight", "vision_proj.weight"],
            [],
        )
        self.assertTrue(receipt["exact_initial_tensor_match"])

    def test_missing_language_tensor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            validate_initial_llm_load(
                "M2", self.model, self.initial, ["language.weight"], []
            )

    def test_unexpected_tensor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unexpected"):
            validate_initial_llm_load(
                "M2", self.model, self.initial, [], ["unknown.weight"]
            )

    def test_silent_value_mismatch_is_rejected(self):
        with torch.no_grad():
            self.model.lm_head.weight.add_(1)
        with self.assertRaisesRegex(ValueError, "exactly"):
            validate_initial_llm_load("M2", self.model, self.initial, [], [])

    def test_m0_rejects_every_missing_key(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            validate_initial_llm_load(
                "M0", self.model, self.initial, ["vision_encoder.weight"], []
            )


if __name__ == "__main__":
    unittest.main()
