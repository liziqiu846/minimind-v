import unittest
from types import SimpleNamespace
from unittest import mock

import torch

from experiments.phase3.caption_template import IMAGE_TOKEN, build_caption_record


class FakeTokenizer:
    bos_token, eos_token, pad_token = "<B>", "<E>", "<P>"
    eos_token_id, pad_token_id = 2, 0
    _special = {"<P>": 0, "<B>": 1, "<E>": 2, IMAGE_TOKEN: 3}

    def apply_chat_template(self, messages, **kwargs):
        parts = []
        for turn in messages:
            if turn["role"] == "user":
                parts.append(f"<B>user\n{turn['content']}<E>\n")
            else:
                parts.append(f"<B>assistant\n<think>\n\n</think>\n\n{turn['content']}<E>\n")
        return "".join(parts)

    def __call__(self, text, add_special_tokens=False):
        ids, index = [], 0
        specials = sorted(self._special, key=len, reverse=True)
        while index < len(text):
            match = next((token for token in specials if text.startswith(token, index)), None)
            if match:
                ids.append(self._special[match]); index += len(match)
            else:
                ids.append(10 + ord(text[index])); index += 1
        return SimpleNamespace(input_ids=ids)

    def convert_tokens_to_ids(self, token):
        return self._special[token]


class Phase3TemplateTests(unittest.TestCase):
    def test_empty_think_and_newline_are_present_but_masked(self):
        tokenizer = FakeTokenizer()
        record = build_caption_record(tokenizer, "A cat.", template_mode="vlm")
        labels = record["labels"].tolist()
        ids = record["input_ids"].tolist()
        valid = [value for value in labels if value != -100]
        self.assertEqual(valid.count(tokenizer.eos_token_id), 1)
        self.assertEqual(valid[-1], tokenizer.eos_token_id)
        self.assertTrue(all(value == -100 for value in labels[record["assistant_target_end"]:]))
        self.assertEqual(ids.count(tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)), 64)
        self.assertEqual(len(ids), 450)
        prefix_slice = labels[record["assistant_target_start"]:record["effective_label_start"]]
        self.assertTrue(prefix_slice and all(value == -100 for value in prefix_slice))

    def test_correct_none_identity_and_lm_path_never_calls_build_record(self):
        tokenizer = FakeTokenizer()
        left = build_caption_record(tokenizer, "A dog.", template_mode="vlm")
        right = build_caption_record(tokenizer, "A dog.", template_mode="vlm")
        self.assertTrue(torch.equal(left["input_ids"], right["input_ids"]))
        self.assertTrue(torch.equal(left["labels"], right["labels"]))
        with mock.patch("experiments.phase3.caption_template.build_token_record", side_effect=AssertionError("forbidden")):
            lm = build_caption_record(tokenizer, "A dog.", template_mode="lm_only")
        self.assertNotIn(tokenizer.convert_tokens_to_ids(IMAGE_TOKEN), lm["input_ids"].tolist())

    def test_forbidden_caption_literals_and_overlength(self):
        tokenizer = FakeTokenizer()
        for caption in ("\nline", "x<image>", "x<E>", "x<think>"):
            with self.subTest(caption=caption), self.assertRaises(ValueError):
                build_caption_record(tokenizer, caption, template_mode="vlm")
        with self.assertRaises(ValueError):
            build_caption_record(tokenizer, "x" * 500, template_mode="vlm")


if __name__ == "__main__":
    unittest.main()
