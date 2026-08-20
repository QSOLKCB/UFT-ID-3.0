#!/usr/bin/env python3
"""Deterministic finite witnesses for the PR #9 observation calculus."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def positive_int(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")


def ceil_div(a: int, b: int) -> int:
    positive_int(b, "denominator")
    if a < 0:
        raise ValueError("ceil_div numerator must be non-negative in this fixture")
    return (a + b - 1) // b


def floor_sample(L: int, R: int, i: int) -> int:
    positive_int(L, "L")
    positive_int(R, "R")
    if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < R:
        raise ValueError("i must be an integer in [0,R)")
    return (i * L) // R


def floor_fibre_formula(L: int, R: int, j: int) -> int:
    positive_int(L, "L")
    positive_int(R, "R")
    if isinstance(j, bool) or not isinstance(j, int) or not 0 <= j < L:
        raise ValueError("j must be an integer in [0,L)")
    return ceil_div((j + 1) * R, L) - ceil_div(j * R, L)


def map_properties(mapping: dict[int, int], codomain: tuple[int, ...]) -> dict[str, object]:
    values = list(mapping.values())
    fibres: dict[int, list[int]] = defaultdict(list)
    for source, target in mapping.items():
        fibres[target].append(source)
    return {
        "injective": len(values) == len(set(values)),
        "surjective": set(values) == set(codomain),
        "image": sorted(set(values)),
        "fibres": {str(y): sorted(fibres.get(y, [])) for y in codomain},
    }


def floor_case(L: int, R: int) -> dict[str, object]:
    mapping = {i: floor_sample(L, R, i) for i in range(R)}
    props = map_properties(mapping, tuple(range(L)))
    formula = {str(j): floor_fibre_formula(L, R, j) for j in range(L)}
    observed = {str(j): len(props["fibres"][str(j)]) for j in range(L)}
    require(observed == formula, f"floor fibre formula mismatch for L={L}, R={R}")

    if R < L:
        expected = (True, False)
        regime = "R<L"
    elif R == L:
        expected = (True, True)
        regime = "R=L"
    else:
        expected = (False, True)
        regime = "R>L"
    require(props["injective"] is expected[0], f"injectivity mismatch in {regime}")
    require(props["surjective"] is expected[1], f"surjectivity mismatch in {regime}")

    return {
        "L": L,
        "R": R,
        "regime": regime,
        "mapping": {str(k): v for k, v in mapping.items()},
        **props,
        "fibre_formula": formula,
    }


def run_suite() -> dict[str, object]:
    constant = {0: 0, 1: 0}
    constant_props = map_properties(constant, (0,))
    require(constant_props["injective"] is False, "Fin2->Fin1 constant map must be noninjective")
    require(constant_props["fibres"]["0"] == [0, 1], "constant-map fibre must contain both source states")

    unused_codomain = {0: 0}
    unused_props = map_properties(unused_codomain, (0, 1))
    require(unused_props["surjective"] is False, "Fin1->Fin2 fixture must be non-surjective")
    require(unused_props["image"] == [0], "unused-codomain fixture image must be {0}")

    floor_cases = [floor_case(5, 3), floor_case(4, 4), floor_case(3, 5)]

    collision = floor_cases[2]["mapping"]
    require(collision["0"] == collision["1"] == 0, "L=3,R=5 must exhibit the declared collision")

    return {
        "type": "uft-id-pr9-observation-witness",
        "schema_version": "1.0.0",
        "constant_observation": {
            "source": [0, 1],
            "codomain": [0],
            "mapping": {"0": 0, "1": 0},
            **constant_props,
            "global_exact_reconstruction_possible": False,
        },
        "unused_codomain": {
            "source": [0],
            "codomain": [0, 1],
            "mapping": {"0": 0},
            **unused_props,
            "quotient_cardinality": 1,
            "image_cardinality": 1,
            "codomain_cardinality": 2,
        },
        "floor_sampling": floor_cases,
        "nonclaims": [
            "Finite observation collisions are not claims about physical observers.",
            "Exact set-theoretic reconstruction is not evidence that a physical state survived observation.",
            "Floor sampling is a finite fixture, not the definition of observation."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("PR9 observation witness: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
