import math

import pytest

from experiments.phase3_risk_v1.complexity_audit import (
    estimated_entropy_bits,
    external_selection_bits,
)


@pytest.mark.parametrize(
    ("family_size", "bits"),
    ((1, 0), (2, 1), (10, 4), (18, 5)),
)
def test_external_selection_bits_are_computed_from_family_size(
    family_size, bits
):
    assert external_selection_bits(family_size) == bits


def test_entropy_is_symbol_frequency_estimate_not_archive_length():
    assert estimated_entropy_bits({"0": 4, "1": 0}) == 0.0
    assert estimated_entropy_bits({"0": 2, "1": 2}) == pytest.approx(4.0)
    expected = -3 * math.log2(3 / 4) - math.log2(1 / 4)
    assert estimated_entropy_bits({"0": 3, "1": 1}) == pytest.approx(expected)


def test_invalid_family_or_histogram_fails():
    with pytest.raises(ValueError):
        external_selection_bits(0)
    with pytest.raises(ValueError):
        estimated_entropy_bits({"0": 0})
