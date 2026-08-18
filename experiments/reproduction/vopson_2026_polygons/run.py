#!/usr/bin/env python3
"""Deterministic audit of the fixed-(N,n) multiplicity entropy extremum.

Primary target:
Melvin M. Vopson, "The Role of Information Entropy in Symmetry of Euclidean
Polygons", Entropy 28(5), 564 (2026), DOI 10.3390/e28050564.

Scope: only the fixed-total-size, fixed-number-of-positive-categories Shannon
extremum. This script does not claim that every polygon comparison in the paper
is invalid.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterator, Sequence

DOI = "10.3390/e28050564"


def shannon_from_counts(counts: Sequence[int]) -> float:
    if not counts or any(c <= 0 for c in counts):
        raise ValueError("counts must be positive integers")
    total = sum(counts)
    return -sum((c / total) * math.log2(c / total) for c in counts)


def positive_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if total < parts or parts < 1:
        return
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def balanced_counts(total: int, parts: int) -> tuple[int, ...]:
    q, r = divmod(total, parts)
    return tuple(sorted((q + 1,) * r + (q,) * (parts - r)))


def concentrated_counts(total: int, parts: int) -> tuple[int, ...]:
    return tuple(sorted((total - parts + 1,) + (1,) * (parts - 1)))


def canonical(counts: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(counts))


def audit_case(total: int, parts: int) -> dict[str, object]:
    values = [(shannon_from_counts(c), c) for c in positive_compositions(total, parts)]
    if not values:
        raise ValueError("need total >= parts >= 1")

    min_h = min(h for h, _ in values)
    max_h = max(h for h, _ in values)
    minimizers = sorted({canonical(c) for h, c in values if math.isclose(h, min_h, abs_tol=1e-12)})
    maximizers = sorted({canonical(c) for h, c in values if math.isclose(h, max_h, abs_tol=1e-12)})

    expected_min = canonical(concentrated_counts(total, parts))
    expected_max = canonical(balanced_counts(total, parts))
    assert minimizers == [expected_min]
    assert maximizers == [expected_max]

    return {
        "N": total,
        "n": parts,
        "composition_count": len(values),
        "minimum": {"counts": list(expected_min), "H_bits": min_h},
        "maximum": {"counts": list(expected_max), "H_bits": max_h},
        "equal_multiplicity_integral": total % parts == 0,
    }


def run(max_N: int, max_n: int) -> dict[str, object]:
    if max_N < 2 or max_n < 2:
        raise ValueError("max_N and max_n must be at least 2")

    cases = []
    for n in range(2, max_n + 1):
        for N in range(n, max_N + 1):
            cases.append(audit_case(N, n))

    triangle_scale = audit_case(6, 2)
    assert math.isclose(triangle_scale["maximum"]["H_bits"], 1.0, abs_tol=1e-12)
    assert math.isclose(
        triangle_scale["minimum"]["H_bits"],
        -((5 / 6) * math.log2(5 / 6) + (1 / 6) * math.log2(1 / 6)),
        abs_tol=1e-12,
    )

    return {
        "experiment_id": "UFTID3-PR2-VOPSON-POLYGON-EXTREMUM",
        "claim_class": "COUNTEREXAMPLE",
        "source": {
            "author": "Melvin M. Vopson",
            "year": 2026,
            "doi": DOI,
        },
        "audited_statement": (
            "For fixed total multiplicity N and fixed number n of positive "
            "categories, equal multiplicities minimise Shannon entropy."
        ),
        "model": {
            "constraints": "g_i are positive integers, sum_i g_i = N, n fixed",
            "probabilities": "p_i = g_i / N",
            "functional": "H = -sum_i p_i log2 p_i",
        },
        "result": (
            "The audited extremum is reversed: balanced/equal multiplicities "
            "maximise Shannon entropy; the most concentrated positive "
            "multiplicity vector minimises it."
        ),
        "triangle_scale_N6_n2": triangle_scale,
        "exhaustive_cases": cases,
        "scope_limit": (
            "This result addresses the fixed-(N,n) extremum only. Polygon "
            "comparisons that also change the effective alphabet/category count "
            "must be analysed separately."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-N", type=int, default=16)
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.max_N, args.max_n)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        t = result["triangle_scale_N6_n2"]
        print(f"source DOI: {DOI}")
        print(f"N=6,n=2 balanced: {t['maximum']['counts']} -> H={t['maximum']['H_bits']:.12g} bits")
        print(f"N=6,n=2 concentrated: {t['minimum']['counts']} -> H={t['minimum']['H_bits']:.12g} bits")
        print(result["result"])
        print(f"exhaustively checked {len(result['exhaustive_cases'])} (N,n) cases")


if __name__ == "__main__":
    main()
