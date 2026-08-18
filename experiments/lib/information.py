"""Small, dependency-free information-theory primitives.

The functions in this module are intentionally conservative. They validate
inputs explicitly, reject non-finite values, and never rely on Python ``assert``
for scientific invariants because assertions disappear under ``python -O``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import math

DEFAULT_TOLERANCE = 1e-12


class ScientificInvariantError(RuntimeError):
    """Raised when an executable scientific invariant does not hold."""


def require(condition: bool, message: str) -> None:
    """Fail closed regardless of Python optimization mode."""

    if not condition:
        raise ScientificInvariantError(message)


def _finite_float(value: object, label: str) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a real number") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be finite")
    return converted


def validate_probability_vector(
    probabilities: Iterable[float],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> tuple[float, ...]:
    """Return a validated finite probability vector.

    The vector must be non-empty, finite, non-negative, and sum to one within
    an absolute tolerance. Relative tolerance is deliberately disabled.
    """

    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be a finite non-negative number")

    values = tuple(
        _finite_float(value, f"probabilities[{index}]")
        for index, value in enumerate(probabilities)
    )
    if not values:
        raise ValueError("probabilities must be non-empty")
    if any(value < 0.0 for value in values):
        raise ValueError("probabilities must be non-negative")
    if not math.isclose(
        math.fsum(values),
        1.0,
        rel_tol=0.0,
        abs_tol=tolerance,
    ):
        raise ValueError("probabilities must sum to 1")
    return values


def shannon_entropy(
    probabilities: Iterable[float],
    *,
    base: float = 2.0,
    tolerance: float = DEFAULT_TOLERANCE,
) -> float:
    """Compute finite Shannon entropy after validating the probability model."""

    values = validate_probability_vector(probabilities, tolerance=tolerance)
    base_value = _finite_float(base, "base")
    if base_value <= 0.0 or math.isclose(base_value, 1.0, rel_tol=0.0, abs_tol=0.0):
        raise ValueError("logarithm base must be positive and different from 1")

    denominator = math.log(base_value)
    return -math.fsum(
        probability * (math.log(probability) / denominator)
        for probability in values
        if probability > 0.0
    )


def validate_row_stochastic(
    matrix: Sequence[Sequence[float]],
    size: int,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> tuple[tuple[float, ...], ...]:
    """Validate a square row-stochastic matrix of the declared size."""

    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("size must be a positive integer")
    if len(matrix) != size:
        raise ValueError("matrix must be square and match distribution size")

    rows: list[tuple[float, ...]] = []
    for row_index, row in enumerate(matrix):
        if len(row) != size:
            raise ValueError("matrix must be square and match distribution size")
        values = tuple(
            _finite_float(value, f"matrix[{row_index}][{column_index}]")
            for column_index, value in enumerate(row)
        )
        if any(value < 0.0 for value in values):
            raise ValueError("transition probabilities must be non-negative")
        if not math.isclose(
            math.fsum(values),
            1.0,
            rel_tol=0.0,
            abs_tol=tolerance,
        ):
            raise ValueError("every transition row must sum to 1")
        rows.append(values)
    return tuple(rows)


def apply_row_stochastic(
    distribution: Sequence[float],
    matrix: Sequence[Sequence[float]],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> tuple[float, ...]:
    """Apply a row-stochastic transition matrix to a row probability vector."""

    probabilities = validate_probability_vector(distribution, tolerance=tolerance)
    transition = validate_row_stochastic(matrix, len(probabilities), tolerance=tolerance)
    output = tuple(
        math.fsum(probabilities[i] * transition[i][j] for i in range(len(probabilities)))
        for j in range(len(probabilities))
    )
    return validate_probability_vector(output, tolerance=tolerance)


def coarse_grain(
    distribution: Sequence[float],
    partition: Sequence[Sequence[int]],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> tuple[float, ...]:
    """Aggregate a probability vector over a complete disjoint partition."""

    probabilities = validate_probability_vector(distribution, tolerance=tolerance)
    if not partition:
        raise ValueError("partition must be non-empty")

    seen: list[int] = []
    normalized_blocks: list[tuple[int, ...]] = []
    for block_index, block in enumerate(partition):
        if not block:
            raise ValueError(f"partition block {block_index} must be non-empty")
        normalized: list[int] = []
        for index in block:
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("partition indices must be integers")
            if index < 0 or index >= len(probabilities):
                raise ValueError("partition index is outside the fine state space")
            normalized.append(index)
            seen.append(index)
        normalized_blocks.append(tuple(normalized))

    if sorted(seen) != list(range(len(probabilities))):
        raise ValueError("partition must cover each fine state exactly once")

    output = tuple(
        math.fsum(probabilities[index] for index in block)
        for block in normalized_blocks
    )
    return validate_probability_vector(output, tolerance=tolerance)


def sign_with_tolerance(
    value: float,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> int:
    """Return -1, 0, or +1 after an absolute near-zero test."""

    converted = _finite_float(value, "value")
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be a finite non-negative number")
    if math.isclose(converted, 0.0, rel_tol=0.0, abs_tol=tolerance):
        return 0
    return 1 if converted > 0.0 else -1
