#!/usr/bin/env python3
"""Full-training-set smoothed conditional bit-NLL compression bound."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SmoothedLossInterval:
    vocab_size: int
    alpha: float
    random_guess_bits: float
    lower_bits: float
    upper_bits: float
    width_bits: float


@dataclass(frozen=True)
class BoundResult:
    empirical_risk_bits: float
    loss_interval: SmoothedLossInterval
    complexity_nats: float
    generalization_penalty_bits: float
    compression_upper_bound_bits: float
    theoretical_max_bits: float
    clipped_certified_upper_bits: float
    random_guess_bits: float
    random_guess_margin_bits: float
    exceeds_theoretical_max: bool
    beats_random_guess: bool


def _require_integer(name: str, value: int, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def _require_open_unit_interval(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    if not math.isfinite(value) or not 0.0 < value < 1.0:
        raise ValueError(f"{name} must lie strictly between zero and one")


def prediction_smoothing_interval(
    vocab_size: int, alpha: float
) -> SmoothedLossInterval:
    """Return Theorem A.2's interval for average smoothed token NLL."""
    _require_integer("vocab_size", vocab_size, minimum=2)
    _require_open_unit_interval("alpha", alpha)

    random_guess = math.log2(vocab_size)
    upper = math.log2(vocab_size / alpha)
    width = math.log2(1.0 + (1.0 - alpha) * vocab_size / alpha)
    return SmoothedLossInterval(
        vocab_size=vocab_size,
        alpha=alpha,
        random_guess_bits=random_guess,
        lower_bits=upper - width,
        upper_bits=upper,
        width_bits=width,
    )


def description_complexity_nats(
    encoded_weight_bits: float, hyperparameter_bits: float = 0.0
) -> float:
    """Upper-bound log(1/P(h)) using a self-delimiting description."""
    code_bits = encoded_weight_bits + hyperparameter_bits
    lengths = (encoded_weight_bits, hyperparameter_bits, code_bits)
    if not all(math.isfinite(value) for value in lengths):
        raise ValueError("description lengths must be finite")
    if encoded_weight_bits < 0.0 or hyperparameter_bits < 0.0:
        raise ValueError("description lengths cannot be negative")
    if code_bits < 1.0:
        raise ValueError("the total description length must be at least one bit")
    return code_bits * math.log(2.0) + 2.0 * math.log(code_bits)


def choice_description_bits(number_of_choices: int) -> int:
    """Return a conservative fixed-length code for one predeclared choice."""
    _require_integer("number_of_choices", number_of_choices, minimum=1)
    return math.ceil(math.log2(number_of_choices))


def _validate_loss_interval(loss_interval: SmoothedLossInterval) -> None:
    _require_integer("loss_interval.vocab_size", loss_interval.vocab_size, minimum=2)
    _require_open_unit_interval("loss_interval.alpha", loss_interval.alpha)
    values = (
        loss_interval.random_guess_bits,
        loss_interval.lower_bits,
        loss_interval.upper_bits,
        loss_interval.width_bits,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("loss interval values must be finite")
    if loss_interval.width_bits <= 0.0:
        raise ValueError("loss interval width must be positive")
    expected_upper = math.log2(loss_interval.vocab_size / loss_interval.alpha)
    expected_width = math.log2(
        1.0
        + (1.0 - loss_interval.alpha)
        * loss_interval.vocab_size
        / loss_interval.alpha
    )
    expected = (
        math.log2(loss_interval.vocab_size),
        expected_upper - expected_width,
        expected_upper,
        expected_width,
    )
    if any(
        not math.isclose(observed, target, rel_tol=1e-12, abs_tol=1e-12)
        for observed, target in zip(values, expected, strict=True)
    ):
        raise ValueError("loss interval is inconsistent with vocab_size and alpha")


def _validate_bound_inputs(
    empirical_risk_bits: float,
    loss_interval: SmoothedLossInterval,
    complexity_nats: float,
    independent_train_samples: int,
    confidence_delta: float,
) -> None:
    _validate_loss_interval(loss_interval)
    if not math.isfinite(empirical_risk_bits):
        raise ValueError("empirical risk must be finite")
    tolerance = 1e-10
    if not (
        loss_interval.lower_bits - tolerance
        <= empirical_risk_bits
        <= loss_interval.upper_bits + tolerance
    ):
        raise ValueError("empirical risk must lie inside the supplied loss interval")
    if not math.isfinite(complexity_nats) or complexity_nats < 0.0:
        raise ValueError("complexity_nats must be finite and non-negative")
    _require_integer(
        "independent_train_samples", independent_train_samples, minimum=1
    )
    _require_open_unit_interval("confidence_delta", confidence_delta)


def finite_hypothesis_bound(
    empirical_risk_bits: float,
    loss_interval: SmoothedLossInterval,
    complexity_nats: float,
    independent_train_samples: int,
    confidence_delta: float,
) -> BoundResult:
    """Compute the full-training-set compression bound in Equation (5)."""
    _validate_bound_inputs(
        empirical_risk_bits,
        loss_interval,
        complexity_nats,
        independent_train_samples,
        confidence_delta,
    )
    penalty = loss_interval.width_bits * math.sqrt(
        (complexity_nats + math.log(1.0 / confidence_delta))
        / (2.0 * independent_train_samples)
    )
    raw_upper_bound = empirical_risk_bits + penalty
    theoretical_max = loss_interval.upper_bits
    random_guess = loss_interval.random_guess_bits
    return BoundResult(
        empirical_risk_bits=empirical_risk_bits,
        loss_interval=loss_interval,
        complexity_nats=complexity_nats,
        generalization_penalty_bits=penalty,
        compression_upper_bound_bits=raw_upper_bound,
        theoretical_max_bits=theoretical_max,
        clipped_certified_upper_bits=min(raw_upper_bound, theoretical_max),
        random_guess_bits=random_guess,
        random_guess_margin_bits=random_guess - raw_upper_bound,
        exceeds_theoretical_max=raw_upper_bound >= theoretical_max,
        beats_random_guess=raw_upper_bound < random_guess,
    )
