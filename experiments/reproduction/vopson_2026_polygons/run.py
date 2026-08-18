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

This script does not claim that every polygon comparison in the paper is
invalid, especially comparisons that change the effective descriptor alphabet.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterator, Sequence

DOI = "10.3390/e28050564"
SOURCE_PAGES = "3-4 of published 9-page PDF"


def shannon_from_counts(counts: Sequence[int]) -> float:
    if not counts or any((not isinstance(c, int)) or isinstance(c, bool) or c <= 0 for c in counts):
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
    if total < parts or parts < 1:
        raise ValueError("need total >= parts >= 1")

    # Canonicalize first so permutations are evaluated only once.  Extrema are
    # selected by ordinary ordering, not math.isclose: a relative tolerance can
    # incorrectly merge distinct near-balanced entropies for large N.
    candidates = sorted({canonical(c) for c in positive_compositions(total, parts)})
    values = [(shannon_from_counts(c), c) for c in candidates]

    min_h, observed_min = min(values, key=lambda item: item[0])
    max_h, observed_max = max(values, key=lambda item: item[0])

    expected_min = canonical(concentrated_counts(total, parts))
    expected_max = canonical(balanced_counts(total, parts))
    if observed_min != expected_min:
        raise AssertionError(f"unexpected minimizer: {observed_min} != {expected_min}")
    if observed_max != expected_max:
        raise AssertionError(f"unexpected maximizer: {observed_max} != {expected_max}")

    return {
        "N": total,
        "n": parts,
        "canonical_candidate_count": len(values),
        "minimum": {"counts": list(expected_min), "H_bits": min_h},
        "maximum": {"counts": list(expected_max), "H_bits": max_h},
        "equal_multiplicity_integral": total % parts == 0,
    }


def audit_variable_n(total: int) -> dict[str, object]:
    if total < 1:
        raise ValueError("total must be at least 1")

    fixed_n_cases = [audit_case(total, n) for n in range(1, total + 1)]
    global_min = min(fixed_n_cases, key=lambda case: case["minimum"]["H_bits"])
    global_max = max(fixed_n_cases, key=lambda case: case["maximum"]["H_bits"])

    expected_min_counts = [total]
    expected_max_counts = [1] * total
    if global_min["minimum"]["counts"] != expected_min_counts:
        raise AssertionError("variable-n global minimum should be the one-category state")
    if global_max["maximum"]["counts"] != expected_max_counts:
        raise AssertionError("variable-n global maximum should be the all-distinct state")

    return {
        "N": total,
        "n_range": [1, total],
        "global_minimum": {
            "n": 1,
            "counts": expected_min_counts,
            "H_bits": global_min["minimum"]["H_bits"],
        },
        "global_maximum": {
            "n": total,
            "counts": expected_max_counts,
            "H_bits": global_max["maximum"]["H_bits"],
        },
    }


def run(max_N: int, max_n: int) -> dict[str, object]:
    if max_N < 2 or max_n < 2:
        raise ValueError("max_N and max_n must be at least 2")

    cases = []
    for n in range(2, max_n + 1):
        for N in range(n, max_N + 1):
            cases.append(audit_case(N, n))

    triangle_scale = audit_case(6, 2)
    assert math.isclose(triangle_scale["maximum"]["H_bits"], 1.0, abs_tol=1e-12, rel_tol=0.0)
    assert math.isclose(
        triangle_scale["minimum"]["H_bits"],
        -((5 / 6) * math.log2(5 / 6) + (1 / 6) * math.log2(1 / 6)),
        abs_tol=1e-12,
        rel_tol=0.0,
    )

    variable_n_N6 = audit_variable_n(6)
    assert variable_n_N6["global_minimum"]["H_bits"] == 0.0
    assert math.isclose(
        variable_n_N6["global_maximum"]["H_bits"],
        math.log2(6),
        abs_tol=1e-12,
        rel_tol=0.0,
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
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.max_N, args.max_n)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        t = result["triangle_scale_fixed_N6_n2"]
        v = result["variable_n_N6"]
        print(f"source DOI: {DOI}")
        print(f"source location: {SOURCE_PAGES}")
        print(f"fixed N=6,n=2 balanced: {t['maximum']['counts']} -> H={t['maximum']['H_bits']:.12g} bits")
        print(f"fixed N=6,n=2 concentrated: {t['minimum']['counts']} -> H={t['minimum']['H_bits']:.12g} bits")
        print(f"variable n, N=6 global minimum: {v['global_minimum']['counts']} -> H={v['global_minimum']['H_bits']:.12g} bits")
        print(f"variable n, N=6 global maximum: {v['global_maximum']['counts']} -> H={v['global_maximum']['H_bits']:.12g} bits")
        print(result["fixed_n_result"])
        print(result["variable_n_result"])
        print(f"exhaustively checked {len(result['exhaustive_fixed_n_cases'])} fixed-(N,n) cases")


if __name__ == "__main__":
    main()
