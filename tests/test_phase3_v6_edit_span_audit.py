from __future__ import annotations

import unittest

from experiments.phase3_v6.audit.edit_span_audit import audit_row


class _Encoding(dict):
    def __getattr__(self, name):
        return self[name]


class CharacterTokenizer:
    """Exact reversible test tokenizer with one token per Unicode character."""

    is_fast = True

    def __call__(self, text, *, add_special_tokens, return_offsets_mapping):
        self.assert_call_contract(add_special_tokens, return_offsets_mapping)
        return _Encoding(
            input_ids=[ord(character) for character in text],
            offset_mapping=[(index, index + 1) for index in range(len(text))],
        )

    @staticmethod
    def assert_call_contract(add_special_tokens, return_offsets_mapping):
        if add_special_tokens or not return_offsets_mapping:
            raise AssertionError("unexpected tokenizer call")

    def decode(self, ids, *, skip_special_tokens, clean_up_tokenization_spaces):
        if skip_special_tokens or clean_up_tokenization_spaces:
            raise AssertionError("unexpected decode options")
        return "".join(chr(token_id) for token_id in ids)

    @staticmethod
    def convert_ids_to_tokens(ids):
        return [chr(token_id) for token_id in ids]


class BrokenTokenizer(CharacterTokenizer):
    def decode(self, ids, *, skip_special_tokens, clean_up_tokenization_spaces):
        return super().decode(
            ids,
            skip_special_tokens=skip_special_tokens,
            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
        ).lower()


def _row(positive_1, negative, positive_2="An unrelated second correct caption."):
    return {
        "caption": positive_1,
        "caption2": positive_2,
        "category": "replace_attribute",
        "filename": "000000000001.jpg",
        "negative_caption": negative,
        "numeric_id": 1,
        "row_key": "replace_attribute:1",
    }


class EditSpanAuditTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = CharacterTokenizer()

    def test_word_replacement(self):
        result = audit_row(
            _row("A red car is parked.", "A blue car is parked."), self.tokenizer
        )
        self.assertEqual(result["category"], "unique_alignment")
        self.assertEqual(result["positive_edit_span"], "red")
        self.assertEqual(result["negative_edit_span"], "blue")

    def test_multiword_phrase_replacement(self):
        result = audit_row(
            _row("A very dark red car waits.", "A pale blue car waits."), self.tokenizer
        )
        self.assertEqual(result["category"], "unique_alignment")
        self.assertEqual(result["positive_edit_span"], "very dark red")
        self.assertEqual(result["negative_edit_span"], "pale blue")

    def test_insertion(self):
        result = audit_row(_row("A car waits.", "A red car waits."), self.tokenizer)
        self.assertEqual(result["category"], "unique_alignment")
        self.assertEqual(result["positive_edit_span"], "")
        self.assertEqual(result["negative_edit_span"], "red ")
        self.assertTrue(result["has_empty_edit_span"])

    def test_deletion(self):
        result = audit_row(_row("A red car waits.", "A car waits."), self.tokenizer)
        self.assertEqual(result["category"], "unique_alignment")
        self.assertEqual(result["positive_edit_span"], "red ")
        self.assertEqual(result["negative_edit_span"], "")

    def test_two_non_contiguous_changes_are_complex(self):
        result = audit_row(
            _row("A red car passes a blue bike.", "A green car passes a yellow bike."),
            self.tokenizer,
        )
        self.assertEqual(result["category"], "complex_edit")
        self.assertGreaterEqual(result["edit_block_count"], 2)

    def test_word_order_exchange_is_complex(self):
        result = audit_row(
            _row(
                "A red car and blue bike.",
                "A blue bike and red car.",
                positive_2="ZZZZZZZZZZZZZZZZZZZZZZZZ",
            ),
            self.tokenizer,
        )
        self.assertEqual(result["category"], "complex_edit")
        self.assertTrue(result["is_word_order_change"])

    def test_case_and_punctuation_are_not_semantic_successes(self):
        case = audit_row(_row("A red car.", "a red car."), self.tokenizer)
        punctuation = audit_row(_row("A red car.", "A red car!"), self.tokenizer)
        self.assertEqual(case["category"], "non_semantic_edit")
        self.assertTrue(case["is_case_only_difference"])
        self.assertEqual(punctuation["category"], "non_semantic_edit")
        self.assertTrue(punctuation["is_punctuation_only_difference"])

    def test_subword_split_is_retained_as_multiple_tokens(self):
        result = audit_row(
            _row("The result is incredible.", "The result is awful."),
            self.tokenizer,
        )
        self.assertEqual(result["category"], "unique_alignment")
        self.assertGreater(result["positive_edit_token_count"], 1)
        self.assertGreater(result["negative_edit_token_count"], 1)

    def test_equal_source_scores_are_ambiguous(self):
        result = audit_row(
            _row("A red cat.", "A red bat.", positive_2="A red rat."), self.tokenizer
        )
        self.assertEqual(result["category"], "ambiguous_source")
        self.assertIsNone(result["selected_source_positive"])
        self.assertIn("equal", result["failure_reason"])

    def test_empty_or_missing_text_is_invalid(self):
        empty = audit_row(_row("", "A car."), self.tokenizer)
        missing_row = _row("A car.", "A bike.")
        del missing_row["caption2"]
        missing = audit_row(missing_row, self.tokenizer)
        self.assertEqual(empty["category"], "invalid_sample")
        self.assertIn("empty_caption", empty["failure_reason"])
        self.assertEqual(missing["category"], "invalid_sample")
        self.assertIn("missing_or_non_string_caption2", missing["failure_reason"])

    def test_character_alignment_with_bad_decode_is_tokenization_problem(self):
        result = audit_row(
            _row("A red car waits.", "A blue car waits."), BrokenTokenizer()
        )
        self.assertEqual(result["category"], "tokenization_problem")
        self.assertIn("does not decode exactly", result["failure_reason"])

    def test_direct_metadata_must_reconstruct_the_negative(self):
        row = _row("A red car.", "A blue car.")
        row["edit_metadata"] = {
            "source_positive": "positive_1",
            "positive_start": 2,
            "positive_end": 5,
            "negative_start": 2,
            "negative_end": 6,
        }
        result = audit_row(row, self.tokenizer)
        self.assertEqual(result["category"], "direct_metadata")
        self.assertEqual(result["positive_edit_span"], "red")
        self.assertEqual(result["negative_edit_span"], "blue")


if __name__ == "__main__":
    unittest.main()
