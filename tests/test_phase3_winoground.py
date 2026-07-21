import sys
import types
import unittest
from unittest import mock

from experiments.phase3.datasets.winoground import adapt_item, load_items
from experiments.phase3.status import Phase3Blocked


class _Image:
    def __init__(self, size):
        self.size = size


class Phase3WinogroundTests(unittest.TestCase):
    def test_adapter_preserves_tag_fields_in_utf8_order(self):
        item = adapt_item({
            "id": 7,
            "image_0": _Image((2, 3)),
            "image_1": _Image((4, 5)),
            "caption_0": "first",
            "caption_1": "second",
            "num_main_preds": 2,
            "z_tag": "same",
            "a_tag": "same",
            "tag": "base",
            "empty_tag": "",
        })
        self.assertEqual(item["item_id"], 7)
        self.assertEqual(item["tags"], [
            {"field": "a_tag", "value": "same"},
            {"field": "tag", "value": "base"},
            {"field": "z_tag", "value": "same"},
        ])
        with self.assertRaises(ValueError):
            adapt_item({
                "id": 8, "image_0": _Image((0, 3)), "image_1": _Image((1, 1)),
                "caption_0": "first", "caption_1": "second",
            })

    def test_access_error_does_not_echo_upstream_secret(self):
        fake = types.ModuleType("datasets")
        fake.load_dataset = mock.Mock(side_effect=RuntimeError("authorization: hf_private_secret"))
        with mock.patch.dict(sys.modules, {"datasets": fake}):
            with self.assertRaises(Phase3Blocked) as caught:
                load_items(token="hf_private_secret")
        self.assertEqual(caught.exception.code, "blocked_by_access")
        self.assertNotIn("private_secret", str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)


if __name__ == "__main__":
    unittest.main()
