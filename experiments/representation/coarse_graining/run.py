#!/usr/bin/env python3
"""One fine-grained permutation, two coarse-grainings, opposite observed signs."""

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


def coarse_grain(
    distribution: Sequence[float], partition: Sequence[Sequence[int]]
) -> tuple[float, ...]:
    flat = [index for block in partition for index in block]
    if sorted(flat) != list(range(len(distribution))):
        raise ValueError("partition must cover each fine state exactly once")
    return tuple(sum(distribution[index] for index in block) for block in partition)


def run() -> dict[str, object]:
    # Fine state labels 1,2,3,4. The physical step swaps states 2 and 3.
    p0 = (0.5, 0.5, 0.0, 0.0)
    p1 = (0.5, 0.0, 0.5, 0.0)

    partition_a = ((0, 1), (2, 3))
    partition_b = ((0, 2), (1, 3))

    a0 = coarse_grain(p0, partition_a)
    a1 = coarse_grain(p1, partition_a)
    b0 = coarse_grain(p0, partition_b)
    b1 = coarse_grain(p1, partition_b)

    fine_delta = shannon_entropy(p1) - shannon_entropy(p0)
    a_delta = shannon_entropy(a1) - shannon_entropy(a0)
    b_delta = shannon_entropy(b1) - shannon_entropy(b0)

    assert math.isclose(fine_delta, 0.0, abs_tol=1e-12)
    assert a_delta > 0.0
    assert b_delta < 0.0

    return {
        "experiment_id": "UFTID3-PR2-COARSE-SIGN-REVERSAL",
        "claim_class": "COUNTEREXAMPLE",
        "claim_target": (
            "The sign of observed Shannon-entropy change is invariant under "
            "admissible changes of coarse-graining."
        ),
        "fine_trajectory": [list(p0), list(p1)],
        "fine_delta_H_bits": fine_delta,
        "partitions": {
            "A": {
                "blocks_zero_based": [list(block) for block in partition_a],
                "observed_trajectory": [list(a0), list(a1)],
                "delta_H_bits": a_delta,
                "sign": "positive",
            },
            "B": {
                "blocks_zero_based": [list(block) for block in partition_b],
                "observed_trajectory": [list(b0), list(b1)],
                "delta_H_bits": b_delta,
                "sign": "negative",
            },
        },
        "conclusion": (
            "The same entropy-preserving fine-grained permutation yields "
            "opposite observed entropy signs under two different partitions."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"fine DeltaH = {result['fine_delta_H_bits']:.12g} bits")
        for name, item in result["partitions"].items():
            print(f"partition {name}: DeltaH = {item['delta_H_bits']:.12g} bits ({item['sign']})")


if __name__ == "__main__":
    main()
