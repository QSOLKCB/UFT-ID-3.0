#!/usr/bin/env python3
"""Deterministic two-state Shannon-entropy sign counterexamples.

This script demonstrates that a broad class of finite information dynamics can
realise positive, zero, and negative Shannon-entropy change. It does not claim
to refute a narrower theorem whose hypotheses exclude one of these map types.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Iterable, Sequence


def shannon_entropy(probabilities: Iterable[float]) -> float:
    values = tuple(float(p) for p in probabilities)
    if any(p < 0.0 for p in values):
        raise ValueError("probabilities must be non-negative")
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("probabilities must sum to 1")
    return -sum(p * math.log2(p) for p in values if p > 0.0)


def apply_row_stochastic(
    distribution: Sequence[float], matrix: Sequence[Sequence[float]]
) -> tuple[float, ...]:
    n = len(distribution)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square and match distribution size")
    for row in matrix:
        if any(x < 0.0 for x in row):
            raise ValueError("transition probabilities must be non-negative")
        if not math.isclose(sum(row), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("every transition row must sum to 1")
    return tuple(
        sum(distribution[i] * matrix[i][j] for i in range(n)) for j in range(n)
    )


def case(
    case_id: str,
    p0: Sequence[float],
    transition: Sequence[Sequence[float]],
    expected_sign: int,
) -> dict[str, object]:
    p1 = apply_row_stochastic(p0, transition)
    h0 = shannon_entropy(p0)
    h1 = shannon_entropy(p1)
    delta = h1 - h0
    sign = 0 if math.isclose(delta, 0.0, abs_tol=1e-12) else (1 if delta > 0 else -1)
    assert sign == expected_sign
    return {
        "case_id": case_id,
        "state_count": len(p0),
        "initial_distribution": list(p0),
        "transition": [list(row) for row in transition],
        "final_distribution": list(p1),
        "H_before_bits": h0,
        "H_after_bits": h1,
        "delta_H_bits": delta,
        "sign": {1: "positive", 0: "zero", -1: "negative"}[sign],
    }


def run() -> dict[str, object]:
    positive = case(
        "two_state_randomisation",
        (1.0, 0.0),
        ((0.5, 0.5), (0.5, 0.5)),
        1,
    )
    zero = case(
        "two_state_permutation",
        (0.25, 0.75),
        ((0.0, 1.0), (1.0, 0.0)),
        0,
    )
    negative = case(
        "two_state_deterministic_merge",
        (0.5, 0.5),
        ((1.0, 0.0), (1.0, 0.0)),
        -1,
    )
    return {
        "experiment_id": "UFTID3-PR2-FINITE-SIGNS",
        "claim_class": "COUNTEREXAMPLE",
        "claim_target": (
            "An unrestricted claim that Shannon entropy of arbitrary finite "
            "information dynamics can never increase."
        ),
        "information_functional": "finite Shannon entropy, base 2",
        "deterministic_script": True,
        "random_seed": None,
        "cases": [positive, zero, negative],
        "conclusion": (
            "A broad finite-dynamics class containing stochastic mixing, "
            "permutations, and deterministic many-to-one maps admits all "
            "three signs of Delta H."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit canonical JSON")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for item in result["cases"]:
            print(
                f"{item['case_id']}: H0={item['H_before_bits']:.12g}, "
                f"H1={item['H_after_bits']:.12g}, "
                f"DeltaH={item['delta_H_bits']:.12g} ({item['sign']})"
            )


if __name__ == "__main__":
    main()
