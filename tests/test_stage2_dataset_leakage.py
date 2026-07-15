import json
import unittest

from transformers import AutoTokenizer

from dataset.stage2_dataset import build_token_record
from experiments.build_stage2_dataset import HammingBKTree


TOKENIZER = "/home/lizhaohui/lzq/stage2-assets-v1/tokenizer"


class Stage2DatasetLeakageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True)

    def test_strict_token_record_has_common_target_and_eos(self):
        conversation = json.dumps(
            [
                {"role": "user", "content": "Describe this. <image>"},
                {"role": "assistant", "content": "A small test image."},
            ]
        )
        record = build_token_record(conversation, self.tokenizer)
        self.assertEqual(
            record["full_token_ids"][record["assistant_target_start"]:record["assistant_target_end"]],
            record["target_token_ids"],
        )
        self.assertEqual(
            record["lm_full_token_ids"][record["lm_assistant_target_start"]:record["lm_assistant_target_end"]],
            record["target_token_ids"],
        )
        self.assertEqual(record["target_token_ids"][-1], self.tokenizer.eos_token_id)
        self.assertEqual(
            len(record["full_token_ids"]) - len(record["lm_full_token_ids"]), 64
        )

    def test_malformed_or_overlong_candidates_are_rejected(self):
        duplicate = [
            {"role": "user", "content": "<image>"},
            {"role": "assistant", "content": "literal <image>"},
        ]
        with self.assertRaises(ValueError):
            build_token_record(duplicate, self.tokenizer)
        overlong = [
            {"role": "user", "content": "<image>"},
            {"role": "assistant", "content": "word " * 1000},
        ]
        with self.assertRaises(ValueError):
            build_token_record(overlong, self.tokenizer)

    def test_bk_tree_radius_is_exact_and_selected_values_join_it(self):
        tree = HammingBKTree([0])
        self.assertTrue(tree.has_within((1 << 6) - 1, 6))
        self.assertFalse(tree.has_within((1 << 7) - 1, 6))
        tree.add((1 << 7) - 1)
        self.assertTrue(tree.has_within((1 << 7) - 1, 0))


if __name__ == "__main__":
    unittest.main()
