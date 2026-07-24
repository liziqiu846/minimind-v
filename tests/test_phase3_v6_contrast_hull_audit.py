from __future__ import annotations

import hashlib
import json
import unittest

from experiments.phase3_v6.audit_v2.contrast_hull_audit import (
    audit_row,
    build_alignment_view,
    deterministic_edit_script,
)


class _Encoding(dict):
    def __getattr__(self, name):
        return self[name]


class CharacterTokenizer:
    """Exact offset tokenizer; characters act as deterministic subword pieces."""

    is_fast = True

    def __call__(self, text, *, add_special_tokens, return_offsets_mapping):
        if add_special_tokens or not return_offsets_mapping:
            raise AssertionError("unexpected tokenizer call")
        return _Encoding(
            input_ids=[ord(character) for character in text],
            offset_mapping=[(index, index + 1) for index in range(len(text))],
        )

    def decode(self, ids, *, skip_special_tokens, clean_up_tokenization_spaces):
        if skip_special_tokens or clean_up_tokenization_spaces:
            raise AssertionError("unexpected decode options")
        return "".join(chr(token_id) for token_id in ids)


class BoundaryCrossingTokenizer(CharacterTokenizer):
    """Synthetic BPE case where the first changed token absorbs common text."""

    pieces = {
        "a roman numeral": ([100, 101, 102], [(0, 3), (3, 7), (7, 15)]),
        "a arabic numeral": ([200, 201, 102], [(0, 3), (3, 8), (8, 16)]),
    }
    decoded = {
        100: "a r",
        101: "oman",
        102: " numeral",
        200: "a a",
        201: "rabic",
    }

    def __call__(self, text, *, add_special_tokens, return_offsets_mapping):
        if text not in self.pieces:
            return super().__call__(
                text,
                add_special_tokens=add_special_tokens,
                return_offsets_mapping=return_offsets_mapping,
            )
        ids, offsets = self.pieces[text]
        return _Encoding(input_ids=list(ids), offset_mapping=list(offsets))

    def decode(self, ids, *, skip_special_tokens, clean_up_tokenization_spaces):
        if ids and all(token_id in self.decoded for token_id in ids):
            return "".join(self.decoded[token_id] for token_id in ids)
        return super().decode(
            ids,
            skip_special_tokens=skip_special_tokens,
            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
        )


DISTANT_POSITIVE = " ".join(f"zzword{index}" for index in range(40))


def _row(positive_1, negative, positive_2=DISTANT_POSITIVE, numeric_id=1):
    return {
        "caption": positive_1,
        "caption2": positive_2,
        "negative_caption": negative,
        "category": "replace_attribute",
        "filename": "000000000001.jpg",
        "numeric_id": numeric_id,
        "row_key": f"replace_attribute:{numeric_id}",
    }


class ContrastHullAuditTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = CharacterTokenizer()

    def audit(self, positive, negative, positive_2=DISTANT_POSITIVE):
        return audit_row(_row(positive, negative, positive_2), self.tokenizer)

    def test_red_to_blue(self):
        result = self.audit("A red car is parked.", "A blue car is parked.")
        self.assertEqual(result["second_round_category"], "one_block_local")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["red"])
        self.assertEqual(result["negative_contrast_hull_lexemes"], ["blue"])

    def test_woman_to_man_preserves_whole_lexeme(self):
        result = self.audit("A woman runs.", "A man runs.")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["woman"])
        self.assertEqual(result["negative_contrast_hull_lexemes"], ["man"])
        self.assertNotIn("wo", result["positive_contrast_hull_lexemes"])

    def test_grassy_to_rocky_preserves_whole_lexeme(self):
        result = self.audit("A grassy field.", "A rocky field.")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["grassy"])
        self.assertEqual(result["negative_contrast_hull_lexemes"], ["rocky"])

    def test_shared_subword_prefix_does_not_enter_lexical_hull(self):
        result = self.audit("A grassy field.", "A gravelly field.")
        self.assertTrue(result["token_boundary_mapping_ok"])
        self.assertEqual(result["positive_hull_model_token_text"], "grassy")
        self.assertEqual(result["negative_hull_model_token_text"], "gravelly")

    def test_initial_case_plus_local_replacement(self):
        result = self.audit("a red car waits.", "A blue car waits.")
        self.assertEqual(result["second_round_category"], "one_block_local")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["red"])
        self.assertIn("initial_case", result["surface_artifact_types"])

    def test_terminal_period_plus_local_replacement(self):
        result = self.audit("A red car waits. ", "A blue car waits")
        self.assertEqual(result["second_round_category"], "one_block_local")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["red"])
        self.assertIn("terminal_punctuation", result["surface_artifact_types"])

    def test_trailing_spaces_plus_local_replacement(self):
        result = self.audit("A red car waits.   ", "A blue car waits.")
        self.assertEqual(result["second_round_category"], "one_block_local")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["red"])
        self.assertIn("edge_whitespace", result["surface_artifact_types"])

    def test_insertion_has_empty_positive_hull_and_mapping_problem(self):
        result = self.audit("A car waits.", "A red car waits.")
        self.assertEqual(result["positive_contrast_hull_lexemes"], [])
        self.assertEqual(result["negative_contrast_hull_lexemes"], ["red"])
        self.assertEqual(result["second_round_category"], "token_mapping_problem")

    def test_deletion_has_empty_negative_hull_and_mapping_problem(self):
        result = self.audit("A red car waits.", "A car waits.")
        self.assertEqual(result["positive_contrast_hull_lexemes"], ["red"])
        self.assertEqual(result["negative_contrast_hull_lexemes"], [])
        self.assertEqual(result["second_round_category"], "token_mapping_problem")

    def test_two_non_contiguous_modifications_include_equal_bridge(self):
        result = self.audit(
            "Red walls with blue furniture near a window.",
            "Blue walls with red furniture near a window.",
        )
        self.assertEqual(result["non_equal_block_count"], 2)
        self.assertEqual(
            result["positive_contrast_hull_lexemes"],
            ["red", "walls", "with", "blue"],
        )
        self.assertEqual(result["maximum_equal_bridge_length"], 2)

    def test_attribute_swap_multiset_is_identical(self):
        result = self.audit(
            "Yellow walls with red furniture near a window.",
            "Red walls with yellow furniture near a window.",
        )
        self.assertEqual(result["non_equal_block_count"], 2)
        self.assertTrue(result["hull_lexeme_multiset_equal"])

    def test_object_swap_multiset_is_identical(self):
        result = self.audit(
            "A cat chases a dog through the room.",
            "A dog chases a cat through the room.",
        )
        self.assertEqual(result["non_equal_block_count"], 2)
        self.assertTrue(result["hull_lexeme_multiset_equal"])

    def test_complete_sentence_rewrite(self):
        result = self.audit("Cats sit here.", "Dogs run away.")
        self.assertEqual(result["second_round_category"], "whole_sentence_hull")
        self.assertEqual(result["maximum_hull_token_coverage"], 1.0)

    def test_identical_positive_sources(self):
        result = self.audit("A red car.", "A blue car.", positive_2="A red car.")
        self.assertEqual(result["second_round_category"], "equivalent_positive_sources")
        self.assertEqual(result["selected_comparison_positive_label"], "positive_1")

    def test_normalized_equivalent_positive_sources(self):
        result = self.audit(
            " A RED car. ", "A blue car.", positive_2="a  red car!"
        )
        self.assertEqual(result["second_round_category"], "equivalent_positive_sources")
        self.assertTrue(result["positive_sources_equivalent"])

    def test_equal_tuples_with_distinct_positives_are_ambiguous(self):
        result = self.audit("red", "fed", positive_2="bed")
        self.assertEqual(
            result["second_round_category"], "ambiguous_comparison_positive"
        )
        self.assertTrue(result["comparison_is_ambiguous"])

    def test_model_tokenizer_multi_subword_mapping(self):
        result = self.audit("An incredible result appears.", "An awful result appears.")
        self.assertGreater(result["positive_hull_model_token_count"], 1)
        self.assertGreater(result["negative_hull_model_token_count"], 1)
        self.assertTrue(result["token_boundary_mapping_ok"])

    def test_bpe_boundary_backoff_preserves_identical_scoring_prefix(self):
        result = audit_row(
            _row("A Roman numeral.", "A Arabic numeral."),
            BoundaryCrossingTokenizer(),
        )
        self.assertTrue(result["token_boundary_mapping_ok"])
        self.assertEqual(result["common_prefix_model_token_ids"], [])
        self.assertEqual(result["positive_token_boundary_expansion_text"], "a ")
        self.assertEqual(result["negative_token_boundary_expansion_text"], "a ")

    def test_empty_common_prefix_is_allowed(self):
        result = self.audit("Red car parked outside.", "Blue car parked outside.")
        self.assertEqual(result["common_prefix_lexemes"], [])
        self.assertEqual(result["common_prefix_model_token_ids"], [])
        self.assertTrue(result["can_score_from_common_prefix"])

    def test_empty_hull_is_surface_degenerate(self):
        result = self.audit(" A red car. ", "a red car!")
        self.assertEqual(result["positive_contrast_hull_lexemes"], [])
        self.assertEqual(
            result["second_round_category"], "surface_only_or_degenerate"
        )

    def test_normalized_reconstruction_invariants(self):
        result = self.audit(
            "A red wall with a blue door stands here.",
            "A blue wall with a red door stands here.",
        )
        self.assertTrue(result["normalized_positive_reconstruction_ok"])
        self.assertTrue(result["normalized_negative_reconstruction_ok"])
        self.assertEqual(
            result["common_prefix_lexemes"]
            + result["positive_contrast_hull_lexemes"]
            + result["common_suffix_lexemes"],
            result["positive_1_alignment_lexemes"],
        )

    def test_nfkc_mapping_and_original_offsets(self):
        view = build_alignment_view("  A ﬁeld. ")
        self.assertEqual(view["alignment_text"], "a field")
        self.assertEqual(view["terminal_punctuation"], ".")
        self.assertEqual(len(view["alignment_lexemes"]), len(view["original_character_offsets"]))
        self.assertEqual(view["original_character_offsets"][1], [4, 8])

    def test_lexeme_kinds_include_abbreviation_hyphen_number_and_punctuation(self):
        view = build_alignment_view("U.S. black-and-white 12,000, yes;")
        self.assertEqual(
            view["alignment_lexeme_kinds"],
            ["abbreviation", "word", "number", "punctuation", "word", "punctuation"],
        )

    def test_edit_script_is_deterministic(self):
        left = ["yellow", "wall", "red", "chair"]
        right = ["red", "wall", "yellow", "chair"]
        self.assertEqual(
            deterministic_edit_script(left, right),
            deterministic_edit_script(left, right),
        )

    def test_repeated_audit_serialization_sha_is_identical(self):
        row = _row("A woman runs.", "A man runs.")
        first = audit_row(row, self.tokenizer)
        second = audit_row(row, self.tokenizer)
        first_bytes = json.dumps(first, sort_keys=True, separators=(",", ":")).encode()
        second_bytes = json.dumps(second, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(first_bytes).digest(), hashlib.sha256(second_bytes).digest())

    def test_missing_or_empty_fields_are_invalid(self):
        empty = audit_row(_row("", "A car."), self.tokenizer)
        missing_row = _row("A car.", "A bike.")
        del missing_row["caption2"]
        missing = audit_row(missing_row, self.tokenizer)
        self.assertEqual(empty["second_round_category"], "invalid_sample")
        self.assertEqual(missing["second_round_category"], "invalid_sample")


if __name__ == "__main__":
    unittest.main()
