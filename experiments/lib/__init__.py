"""Dependency-free information primitives shared by UFT-ID experiments."""

from .information import (
    DEFAULT_TOLERANCE,
    ScientificInvariantError,
    apply_row_stochastic,
    coarse_grain,
    require,
    shannon_entropy,
    sign_with_tolerance,
    validate_probability_vector,
    validate_row_stochastic,
)

__all__ = [
    "DEFAULT_TOLERANCE",
    "ScientificInvariantError",
    "apply_row_stochastic",
    "coarse_grain",
    "require",
    "shannon_entropy",
    "sign_with_tolerance",
    "validate_probability_vector",
    "validate_row_stochastic",
]
