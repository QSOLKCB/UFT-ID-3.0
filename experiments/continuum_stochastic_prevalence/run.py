#!/usr/bin/env python3
"""Exact finite conformance for continuum, stochastic, and prevalence obligations."""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import product
import json
from typing import Hashable, Iterable, Mapping, Sequence

State = Hashable

BOUNDARIES = [
    "RELATION_REACHABLE != POSITIVE_PROBABILITY",
    "EXISTS_PATH != POSITIVE_PROBABILITY",
    "POSITIVE_PROBABILITY != ALMOST_SURE",
    "FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS",
    "ONE_TRAJECTORY != DISTRIBUTION",
    "FINITE_SAMPLE_FREQUENCY != MODEL_PROBABILITY",
    "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM",
    "PREVALENCE_REQUIRES_DECLARED_MEASURE",
    "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY",
    "DISCRETIZATION_CONVERGENCE != ASSUMED_WITHOUT_ERROR_CONTROL",
    "FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY",
]


def _carrier(states: Iterable[State]) -> tuple[State, ...]:
    carrier = tuple(states)
    if not carrier or len(set(carrier)) != len(carrier):
        raise ValueError("carrier must be finite, nonempty, and duplicate-free")
    return carrier


def _fraction(value: object, label: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f"{label} must use exact integer/Fraction arithmetic")
    result = Fraction(value)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def make_distribution(states: Iterable[State], weights: Mapping[State, object]) -> dict[State, Fraction]:
    carrier = _carrier(states)
    if set(weights) != set(carrier):
        raise ValueError("distribution must assign exactly one mass to every carrier state")
    result = {state: _fraction(weights[state], "distribution mass") for state in carrier}
    if sum(result.values(), Fraction(0)) != 1:
        raise ValueError("distribution masses must sum exactly to one")
    return result


def make_kernel(states: Iterable[State], rows: Mapping[State, Mapping[State, object]]) -> dict[State, dict[State, Fraction]]:
    carrier = _carrier(states)
    if set(rows) != set(carrier):
        raise ValueError("kernel must contain exactly one row for every carrier state")
    kernel: dict[State, dict[State, Fraction]] = {}
    for source in carrier:
        row = rows[source]
        if not isinstance(row, Mapping) or set(row) != set(carrier):
            raise ValueError("kernel row must assign exactly one mass to every target state")
        exact = {target: _fraction(row[target], "kernel probability") for target in carrier}
        if sum(exact.values(), Fraction(0)) != 1:
            raise ValueError("every kernel row must sum exactly to one")
        kernel[source] = exact
    return kernel


def evolve_distribution(states: Sequence[State], distribution: Mapping[State, Fraction], kernel: Mapping[State, Mapping[State, Fraction]]) -> dict[State, Fraction]:
    carrier = _carrier(states)
    p = make_distribution(carrier, distribution)
    k = make_kernel(carrier, kernel)
    evolved = {
        target: sum((p[source] * k[source][target] for source in carrier), Fraction(0))
        for target in carrier
    }
    if sum(evolved.values(), Fraction(0)) != 1 or any(value < 0 for value in evolved.values()):
        raise RuntimeError("row-stochastic evolution failed to preserve probability mass")
    return evolved


def event_probability(states: Sequence[State], distribution: Mapping[State, Fraction], event: Iterable[State]) -> Fraction:
    carrier = _carrier(states)
    p = make_distribution(carrier, distribution)
    event_set = set(event)
    if not event_set.issubset(set(carrier)):
        raise ValueError("event escapes declared carrier")
    return sum((p[state] for state in event_set), Fraction(0))


def support(distribution: Mapping[State, Fraction]) -> set[State]:
    return {state for state, mass in distribution.items() if mass > 0}


def path_mass(states: Sequence[State], distribution: Mapping[State, Fraction], kernel: Mapping[State, Mapping[State, Fraction]], path: Sequence[State]) -> Fraction:
    carrier = _carrier(states)
    p = make_distribution(carrier, distribution)
    k = make_kernel(carrier, kernel)
    if not path:
        raise ValueError("path must contain at least one state")
    if any(state not in set(carrier) for state in path):
        raise ValueError("path state escapes declared carrier")
    mass = p[path[0]]
    for left, right in zip(path, path[1:]):
        mass *= k[left][right]
    return mass


def prevalence(states: Sequence[State], measure: Mapping[State, Fraction], property_set: Iterable[State]) -> Fraction:
    return event_probability(states, measure, property_set)


def geometric_survival_probability(q: object, horizon: int) -> Fraction:
    exact_q = _fraction(q, "survival probability")
    if exact_q > 1:
        raise ValueError("survival probability cannot exceed one")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 0:
        raise ValueError("horizon must be a nonnegative integer")
    return exact_q ** horizon


def geometric_infinite_survival_is_zero(q: object) -> bool:
    exact_q = _fraction(q, "survival probability")
    if exact_q >= 1:
        return False
    return True


def vanishing_polynomial(grid: Iterable[object], x: object) -> Fraction:
    grid_values = tuple(_fraction(value, "grid point") for value in grid)
    if not grid_values or len(set(grid_values)) != len(grid_values):
        raise ValueError("grid must be finite, nonempty, and duplicate-free")
    exact_x = _fraction(x, "evaluation point")
    value = Fraction(1)
    for point in grid_values:
        value *= exact_x - point
    return value


def integer_composition_distributions(n: int, denominator: int) -> list[tuple[Fraction, ...]]:
    if n <= 0 or denominator <= 0:
        raise ValueError("distribution dimensions and denominator must be positive")
    out: list[tuple[Fraction, ...]] = []

    def visit(prefix: list[int], remaining: int, slots: int) -> None:
        if slots == 1:
            out.append(tuple(Fraction(value, denominator) for value in prefix + [remaining]))
            return
        for value in range(remaining + 1):
            visit(prefix + [value], remaining - value, slots - 1)

    visit([], denominator, n)
    return out


def _dist_map(states: Sequence[int], masses: Sequence[Fraction]) -> dict[int, Fraction]:
    return {state: masses[index] for index, state in enumerate(states)}


def finite_kernel_battery() -> dict[str, int]:
    states = (0, 1)
    row_vectors = integer_composition_distributions(2, 2)
    kernels = tuple((left, right) for left in row_vectors for right in row_vectors)
    initials = tuple(integer_composition_distributions(2, 2))
    transport_checks = 0
    path_evaluations = 0
    path_normalization_checks = 0
    for left, right in kernels:
        kernel = make_kernel(states, {
            0: _dist_map(states, left),
            1: _dist_map(states, right),
        })
        for masses in initials:
            distribution = make_distribution(states, _dist_map(states, masses))
            evolved = evolve_distribution(states, distribution, kernel)
            if sum(evolved.values(), Fraction(0)) != 1:
                raise RuntimeError("finite kernel transport mass drift")
            transport_checks += 1
            for horizon in (1, 2, 3):
                total = Fraction(0)
                for path in product(states, repeat=horizon + 1):
                    total += path_mass(states, distribution, kernel, path)
                    path_evaluations += 1
                if total != 1:
                    raise RuntimeError("finite path masses did not normalize")
                path_normalization_checks += 1
    return {
        "finite_kernel_count": len(kernels),
        "initial_distribution_count": len(initials),
        "kernel_transport_checks": transport_checks,
        "path_mass_evaluations": path_evaluations,
        "path_normalization_checks": path_normalization_checks,
    }


def finite_atomic_quantifier_battery() -> dict[str, int]:
    states = (0, 1, 2)
    distributions = integer_composition_distributions(3, 2)
    event_checks = 0
    almost_sure_cases = 0
    positive_cases = 0
    support_witness_cases = 0
    for masses in distributions:
        distribution = make_distribution(states, _dist_map(states, masses))
        positive_support = support(distribution)
        for mask in range(1 << len(states)):
            event = {state for state in states if (mask >> state) & 1}
            probability = event_probability(states, distribution, event)
            almost_sure = probability == 1
            positive = probability > 0
            support_witness = bool(event & positive_support)
            if almost_sure and not positive:
                raise RuntimeError("almost-sure event was not positive-probability")
            if positive != support_witness:
                raise RuntimeError("finite atomic positive-probability/support equivalence failed")
            event_checks += 1
            almost_sure_cases += int(almost_sure)
            positive_cases += int(positive)
            support_witness_cases += int(support_witness)
    return {
        "finite_atomic_event_checks": event_checks,
        "almost_sure_event_cases": almost_sure_cases,
        "positive_probability_event_cases": positive_cases,
        "support_witness_event_cases": support_witness_cases,
    }


def survival_battery() -> dict[str, int]:
    checks = 0
    zero_limit_controls = 0
    for q in (Fraction(1, 2), Fraction(3, 4)):
        for horizon in range(1, 9):
            if geometric_survival_probability(q, horizon) <= 0:
                raise RuntimeError("finite-horizon survival control lost positive probability")
            checks += 1
        if not geometric_infinite_survival_is_zero(q):
            raise RuntimeError("q<1 infinite-survival zero control failed")
        zero_limit_controls += 1
    return {
        "finite_survival_checks": checks,
        "infinite_survival_zero_controls": zero_limit_controls,
    }


def prevalence_battery() -> dict[str, int]:
    states = (0, 1, 2)
    measures = integer_composition_distributions(3, 3)
    checks = 0
    for masses in measures:
        measure = make_distribution(states, _dist_map(states, masses))
        for mask in range(1 << len(states)):
            event = {state for state in states if (mask >> state) & 1}
            value = prevalence(states, measure, event)
            if value < 0 or value > 1:
                raise RuntimeError("finite prevalence escaped unit interval")
            checks += 1
    return {
        "declared_measure_count": len(measures),
        "prevalence_measure_event_checks": checks,
    }


def continuum_nonlifting_battery() -> dict[str, int]:
    grid_pool = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1))
    witness_pool = tuple(Fraction(index, 8) for index in range(9))
    checks = 0
    for mask in range(1, 1 << len(grid_pool)):
        grid = tuple(grid_pool[index] for index in range(len(grid_pool)) if (mask >> index) & 1)
        witness = next(point for point in witness_pool if point not in grid)
        if any(vanishing_polynomial(grid, point) != 0 for point in grid):
            raise RuntimeError("vanishing polynomial failed on declared grid")
        if vanishing_polynomial(grid, witness) == 0:
            raise RuntimeError("off-grid witness failed to distinguish continuum functions")
        checks += 1
    return {"finite_grid_nonlifting_checks": checks}


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def counterexample_fixtures() -> dict[str, object]:
    relation = frozenset({(0, 1)})
    states = (0, 1)
    zero_kernel = make_kernel(states, {
        0: {0: 1, 1: 0},
        1: {0: 0, 1: 1},
    })
    initial = make_distribution(states, {0: 1, 1: 0})
    fair = make_distribution(("H", "T"), {"H": Fraction(1, 2), "T": Fraction(1, 2)})
    low = make_distribution(("x", "y"), {"x": Fraction(1, 100), "y": Fraction(99, 100)})
    high = make_distribution(("x", "y"), {"x": Fraction(99, 100), "y": Fraction(1, 100)})
    grid = (Fraction(0), Fraction(1, 2), Fraction(1))
    off_grid = Fraction(1, 4)
    hhh_mass = Fraction(1, 2) ** 3
    return {
        "CX-CSP-001": {
            "relation_edge_present": (0, 1) in relation,
            "kernel_transition_probability": _fraction_text(zero_kernel[0][1]),
            "path_probability_0_to_1": _fraction_text(path_mass(states, initial, zero_kernel, (0, 1))),
        },
        "CX-CSP-002": {
            "event": ["H"],
            "event_probability": _fraction_text(event_probability(("H", "T"), fair, {"H"})),
            "positive_probability": event_probability(("H", "T"), fair, {"H"}) > 0,
            "almost_sure": event_probability(("H", "T"), fair, {"H"}) == 1,
        },
        "CX-CSP-003": {
            "q": "1/2",
            "finite_horizon_probabilities": [_fraction_text(geometric_survival_probability(Fraction(1, 2), n)) for n in range(1, 9)],
            "all_listed_finite_horizons_positive": all(geometric_survival_probability(Fraction(1, 2), n) > 0 for n in range(1, 9)),
            "infinite_survival_probability": "0",
        },
        "CX-CSP-004": {
            "trajectory": "HHH",
            "trajectory_empirical_head_frequency": "1",
            "declared_single_step_head_probability": "1/2",
            "trajectory_probability": _fraction_text(hhh_mass),
        },
        "CX-CSP-005": {
            "failure_set": ["x"],
            "low_measure_prevalence": _fraction_text(prevalence(("x", "y"), low, {"x"})),
            "high_measure_prevalence": _fraction_text(prevalence(("x", "y"), high, {"x"})),
        },
        "CX-CSP-006": {
            "grid": [_fraction_text(value) for value in grid],
            "grid_values_zero": all(vanishing_polynomial(grid, point) == 0 for point in grid),
            "off_grid_point": _fraction_text(off_grid),
            "off_grid_polynomial_value": _fraction_text(vanishing_polynomial(grid, off_grid)),
            "off_grid_differs": vanishing_polynomial(grid, off_grid) != 0,
        },
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-continuum-stochastic-prevalence-witness",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "finite_kernels": finite_kernel_battery(),
            "finite_atomic_quantifiers": finite_atomic_quantifier_battery(),
            "survival": survival_battery(),
            "prevalence": prevalence_battery(),
            "continuum_nonlifting": continuum_nonlifting_battery(),
        },
        "fixtures": counterexample_fixtures(),
        "hard_boundaries": BOUNDARIES,
        "claim_boundary": (
            "FINITE_REACHABILITY != INFINITE_PATH_LIVENESS; "
            "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM; "
            "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("Continuum/Stochastic/Prevalence witness:", result["bounded_checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
