#!/usr/bin/env python3
"""Deterministic audit of the multiplicity Shannon-entropy extremum.

Primary target:
Melvin M. Vopson, "The Role of Information Entropy in Symmetry of Euclidean
Polygons", Entropy 28(5), 564 (2026), DOI 10.3390/e28050564.

Source-faithfulness note:
The published paper formulates the general problem at fixed total system size
N in terms of positive multiplicities g_i. Its prose identifies equal
multiplicity as the entropy-minimising condition. The general statement does
not cleanly freeze n, the number of represented categories, throughout the
optimization. This audit therefore separates two questions:

1. fixed N and fixed n: balanced/equal multiplicities maximise Shannon entropy;
2. fixed N with n allowed to vary from 1 to N: the global minimum is the
   one-category state (N), while the global maximum is the all-distinct state
   (1,...,1).

Exhaustive enumeration is used only as a bounded verifier. Analytic extrema are
available for inputs above the configured work ceiling.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterator, Sequence
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.lib.information import require, shannon_entropy  # noqa: E402

DOI = "10.3390/e28050564"
SOURCE_PAGES = "3-4 of published 9-page PDF"
DEFAULT_MAX_COMPOSITIONS = 250_000


class WorkLimitExceeded(RuntimeError):
    """Raised when an exhaustive request exceeds the declared work ceiling."""


def _positive_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def positive_composition_count(total: int, parts: int) -> int:
    """Return the number of ordered positive compositions C(total-1, parts-1)."""

    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    if total < parts:
        raise ValueError("need total >= parts >= 1")
    return math.comb(total - 1, parts - 1)


def shannon_from_counts(counts: Sequence[int]) -> float:
    if not counts or any(
        (not isinstance(count, int)) or isinstance(count, bool) or count <= 0
        for count in counts
    ):
        raise ValueError("counts must be positive integers")
    total = sum(counts)
    return shannon_entropy(count / total for count in counts)


def positive_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    if total < parts:
        raise ValueError("need total >= parts >= 1")
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def balanced_counts(total: int, parts: int) -> tuple[int, ...]:
    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    if total < parts:
        raise ValueError("need total >= parts >= 1")
    quotient, remainder = divmod(total, parts)
    return tuple(sorted((quotient + 1,) * remainder + (quotient,) * (parts - remainder)))


def concentrated_counts(total: int, parts: int) -> tuple[int, ...]:
    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    if total < parts:
        raise ValueError("need total >= parts >= 1")
    return tuple(sorted((total - parts + 1,) + (1,) * (parts - 1)))


def canonical(counts: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(counts))


def analytic_extrema(total: int, parts: int) -> dict[str, object]:
    """Return the fixed-(N,n) extrema without exhaustive enumeration."""

    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    if total < parts:
        raise ValueError("need total >= parts >= 1")

    minimum_counts = concentrated_counts(total, parts)
    maximum_counts = balanced_counts(total, parts)
    return {
        "N": total,
        "n": parts,
        "ordered_composition_count": positive_composition_count(total, parts),
        "minimum": {
            "counts": list(minimum_counts),
            "H_bits": shannon_from_counts(minimum_counts),
        },
        "maximum": {
            "counts": list(maximum_counts),
            "H_bits": shannon_from_counts(maximum_counts),
        },
        "equal_multiplicity_integral": total % parts == 0,
        "method": "analytic",
    }


def audit_case(
    total: int,
    parts: int,
    *,
    max_compositions: int = DEFAULT_MAX_COMPOSITIONS,
    allow_large_exhaustive: bool = False,
) -> dict[str, object]:
    """Exhaustively verify one fixed-(N,n) case within a declared work budget."""

    total = _positive_integer(total, "total")
    parts = _positive_integer(parts, "parts")
    max_compositions = _positive_integer(max_compositions, "max_compositions")
    if total < parts:
        raise ValueError("need total >= parts >= 1")

    ordered_count = positive_composition_count(total, parts)
    if ordered_count > max_compositions and not allow_large_exhaustive:
        raise WorkLimitExceeded(
            "exhaustive positive-composition count "
            f"{ordered_count} exceeds limit {max_compositions} for N={total}, n={parts}; "
            "use analytic_extrema() or explicitly opt in with --allow-large-exhaustive"
        )

    candidates = sorted({canonical(composition) for composition in positive_compositions(total, parts)})
    values = [(shannon_from_counts(candidate), candidate) for candidate in candidates]

    minimum_entropy, observed_minimum = min(values, key=lambda item: item[0])
    maximum_entropy, observed_maximum = max(values, key=lambda item: item[0])

    expected = analytic_extrema(total, parts)
    expected_minimum = tuple(expected["minimum"]["counts"])
    expected_maximum = tuple(expected["maximum"]["counts"])
    require(
        observed_minimum == expected_minimum,
        f"unexpected minimizer: {observed_minimum} != {expected_minimum}",
    )
    require(
        observed_maximum == expected_maximum,
        f"unexpected maximizer: {observed_maximum} != {expected_maximum}",
    )

    return {
        "N": total,
        "n": parts,
        "ordered_composition_count": ordered_count,
        "canonical_candidate_count": len(values),
        "minimum": {"counts": list(expected_minimum), "H_bits": minimum_entropy},
        "maximum": {"counts": list(expected_maximum), "H_bits": maximum_entropy},
        "equal_multiplicity_integral": total % parts == 0,
        "method": "bounded-exhaustive",
        "max_compositions": max_compositions,
    }


def audit_variable_n(
    total: int,
    *,
    max_compositions: int = DEFAULT_MAX_COMPOSITIONS,
    allow_large_exhaustive: bool = False,
) -> dict[str, object]:
    total = _positive_integer(total, "total")

    fixed_n_cases = [
        audit_case(
            total,
            parts,
            max_compositions=max_compositions,
            allow_large_exhaustive=allow_large_exhaustive,
        )
        for parts in range(1, total + 1)
    ]
    global_minimum = min(fixed_n_cases, key=lambda case: case["minimum"]["H_bits"])
    global_maximum = max(fixed_n_cases, key=lambda case: case["maximum"]["H_bits"])

    expected_minimum_counts = [total]
    expected_maximum_counts = [1] * total
    require(
        global_minimum["minimum"]["counts"] == expected_minimum_counts,
        "variable-n global minimum should be the one-category state",
    )
    require(
        global_maximum["maximum"]["counts"] == expected_maximum_counts,
        "variable-n global maximum should be the all-distinct state",
    )

    return {
        "N": total,
        "n_range": [1, total],
        "global_minimum": {
            "n": 1,
            "counts": expected_minimum_counts,
            "H_bits": global_minimum["minimum"]["H_bits"],
        },
        "global_maximum": {
            "n": total,
            "counts": expected_maximum_counts,
            "H_bits": global_maximum["maximum"]["H_bits"],
        },
    }


def run(
    max_N: int,
    max_n: int,
    *,
    max_compositions: int = DEFAULT_MAX_COMPOSITIONS,
    allow_large_exhaustive: bool = False,
) -> dict[str, object]:
    max_N = _positive_integer(max_N, "max_N")
    max_n = _positive_integer(max_n, "max_n")
    if max_N < 2 or max_n < 2:
        raise ValueError("max_N and max_n must be at least 2")

    cases = []
    for parts in range(2, max_n + 1):
        for total in range(parts, max_N + 1):
            cases.append(
                audit_case(
                    total,
                    parts,
                    max_compositions=max_compositions,
                    allow_large_exhaustive=allow_large_exhaustive,
                )
            )

    triangle_scale = audit_case(
        6,
        2,
        max_compositions=max_compositions,
        allow_large_exhaustive=allow_large_exhaustive,
    )
    require(
        math.isclose(
            triangle_scale["maximum"]["H_bits"],
            1.0,
            abs_tol=1e-12,
            rel_tol=0.0,
        ),
        "N=6,n=2 balanced entropy must be one bit",
    )
    require(
        math.isclose(
            triangle_scale["minimum"]["H_bits"],
            -((5 / 6) * math.log2(5 / 6) + (1 / 6) * math.log2(1 / 6)),
            abs_tol=1e-12,
            rel_tol=0.0,
        ),
        "N=6,n=2 concentrated entropy mismatch",
    )

    variable_n_N6 = audit_variable_n(
        6,
        max_compositions=max_compositions,
        allow_large_exhaustive=allow_large_exhaustive,
    )
    require(variable_n_N6["global_minimum"]["H_bits"] == 0.0, "N=6 minimum must be zero")
    require(
        math.isclose(
            variable_n_N6["global_maximum"]["H_bits"],
            math.log2(6),
            abs_tol=1e-12,
            rel_tol=0.0,
        ),
        "N=6 all-distinct entropy mismatch",
    )

    return {
        "experiment_id": "UFTID3-PR2-VOPSON-POLYGON-EXTREMUM",
        "claim_class": "COUNTEREXAMPLE",
        "source": {
            "author": "Melvin M. Vopson",
            "year": 2026,
            "doi": DOI,
            "source_location": SOURCE_PAGES,
            "source_problem": (
                "Shannon entropy of a system with fixed total size N, expressed "
                "through positive multiplicities g_i; the source identifies "
                "equal multiplicity as the minimum condition."
            ),
        },
        "source_mapping": {
            "N": "paper's fixed total number of elements / total multiplicity",
            "g_i": "paper's multiplicity of represented category i",
            "n": (
                "number of represented categories; because the source's general "
                "fixed-N statement does not clearly freeze n globally, this "
                "audit reports both fixed-n slices and the variable-n problem"
            ),
            "p_i": "g_i / N",
            "functional": "H = -sum_i p_i log2 p_i",
        },
        "exhaustive_policy": {
            "ordered_composition_formula": "C(N-1,n-1)",
            "max_compositions": max_compositions,
            "allow_large_exhaustive": allow_large_exhaustive,
            "analytic_fallback": "analytic_extrema(total, parts)",
        },
        "fixed_n_result": (
            "For fixed N and fixed n, balanced/equal multiplicities maximise "
            "Shannon entropy; the most concentrated positive multiplicity "
            "vector minimises it."
        ),
        "variable_n_result": (
            "For fixed N with n allowed to vary from 1 to N, the global minimum "
            "is n=1 with counts (N), H=0; the global maximum is n=N with all "
            "counts equal to 1, H=log2(N). Equal multiplicity by itself therefore "
            "does not characterize a nontrivial global minimum."
        ),
        "triangle_scale_fixed_N6_n2": triangle_scale,
        "variable_n_N6": variable_n_N6,
        "exhaustive_fixed_n_cases": cases,
        "scope_limit": (
            "This result audits the source's general multiplicity extremum. "
            "Polygon-specific comparisons that change descriptor definitions or "
            "effective category count must be analysed separately."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-N", type=int, default=16)
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--max-compositions", type=int, default=DEFAULT_MAX_COMPOSITIONS)
    parser.add_argument("--allow-large-exhaustive", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(
        args.max_N,
        args.max_n,
        max_compositions=args.max_compositions,
        allow_large_exhaustive=args.allow_large_exhaustive,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        triangle = result["triangle_scale_fixed_N6_n2"]
        variable = result["variable_n_N6"]
        print(f"source DOI: {DOI}")
        print(f"source location: {SOURCE_PAGES}")
        print(
            f"fixed N=6,n=2 balanced: {triangle['maximum']['counts']} "
            f"-> H={triangle['maximum']['H_bits']:.12g} bits"
        )
        print(
            f"fixed N=6,n=2 concentrated: {triangle['minimum']['counts']} "
            f"-> H={triangle['minimum']['H_bits']:.12g} bits"
        )
        print(
            f"variable n, N=6 global minimum: {variable['global_minimum']['counts']} "
            f"-> H={variable['global_minimum']['H_bits']:.12g} bits"
        )
        print(
            f"variable n, N=6 global maximum: {variable['global_maximum']['counts']} "
            f"-> H={variable['global_maximum']['H_bits']:.12g} bits"
        )
        print(result["fixed_n_result"])
        print(result["variable_n_result"])
        print(
            f"exhaustively checked {len(result['exhaustive_fixed_n_cases'])} "
            "fixed-(N,n) cases"
        )


if __name__ == "__main__":
    main()
