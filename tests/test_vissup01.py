from __future__ import annotations

from collections import OrderedDict

import pytest
from PIL import Image

from experiments.vissup01 import (
    ROTATION_LABELS,
    answer_margin,
    choice_labels,
    cvbench_gold_label,
    deterministic_png,
    image_order_key,
    normalized_pixel_sha256,
    predicted_label,
    rotate_clockwise,
)


def test_variable_choice_inventory_and_gold():
    assert choice_labels(2) == ("A", "B")
    assert choice_labels(6) == ("A", "B", "C", "D", "E", "F")
    assert cvbench_gold_label("(E)", 5) == "E"
    with pytest.raises(ValueError):
        cvbench_gold_label("(F)", 5)


def test_margin_and_prediction_use_row_inventory():
    values = OrderedDict([("A", 3.0), ("B", 1.0), ("C", 4.0)])
    assert predicted_label(values, ("A", "B", "C")) == "B"
    assert answer_margin(values, "B", ("A", "B", "C")) == 2.5


def test_prediction_tie_uses_letter_order():
    values = OrderedDict([("A", 1.0), ("B", 1.0)])
    assert predicted_label(values, ("A", "B")) == "A"


def test_clockwise_rotations_are_exact_transposes():
    image = Image.new("RGB", (2, 3))
    pixels = image.load()
    value = 0
    for y in range(3):
        for x in range(2):
            pixels[x, y] = (value, 0, 0)
            value += 1
    assert rotate_clockwise(image, 90).size == (3, 2)
    assert rotate_clockwise(image, 180).size == (2, 3)
    assert rotate_clockwise(image, 270).size == (3, 2)
    assert normalized_pixel_sha256(rotate_clockwise(image, 0)) == (
        normalized_pixel_sha256(image)
    )


def test_png_and_order_keys_are_deterministic():
    image = Image.new("RGB", (4, 5), color=(10, 20, 30))
    assert deterministic_png(image) == deterministic_png(image)
    pixel_sha = normalized_pixel_sha256(image)
    assert image_order_key(pixel_sha) == image_order_key(pixel_sha)
    assert len(image_order_key(pixel_sha)) == 64


def test_rotation_labels_are_frozen():
    assert ROTATION_LABELS == ("A", "B", "C", "D")
