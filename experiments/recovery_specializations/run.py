#!/usr/bin/env python3
"""Finite executable conformance for deterministic recovery specializations."""
from __future__ import annotations

import argparse
from itertools import permutations, product
import json
from collections import deque
from typing import Hashable, Iterable, Mapping, Sequence

State = Hashable
Relation = frozenset[tuple[State, State]]
Selector = dict[State, State]

BOUNDARIES = [
    "GENERIC_RELATION != DETERMINISTIC_SELECTOR",
    "EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER",
    "DETERMINISTIC != RELATION_SOUND",
    "RELATION_SOUND != TERMINATING",
    "TERMINATING_SELECTOR != BASE_RELATION_CONFLUENT",
    "SELECTOR_NORMAL_FORM != UNIQUE_RELATION_NORMAL_FORM",
    "OBJECTIVE_MINIMUM != UNIQUE_SELECTION_WITHOUT_TIEBREAK",
    "EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY",
    "FINITE_SELECTOR_CONFORMANCE != GENERAL_RECOVERY_THEORY",
]


def _carrier(states: Iterable[State]) -> tuple[State, ...]:
    carrier = tuple(states)
    if not carrier or len(set(carrier)) != len(carrier):
        raise ValueError("carrier must be finite, nonempty, and duplicate-free")
    return carrier


def make_relation(states: Iterable[State], edges: Iterable[tuple[State, State]]) -> Relation:
    carrier = _carrier(states)
    allowed = set(carrier)
    result: set[tuple[State, State]] = set()
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 2 or edge[0] not in allowed or edge[1] not in allowed:
            raise ValueError("relation edge must stay inside the declared carrier")
        result.add(edge)
    return frozenset(result)


def make_selector(states: Iterable[State], mapping: Mapping[State, State]) -> Selector:
    carrier = _carrier(states)
    if set(mapping) != set(carrier):
        raise ValueError("selector must be total on exactly the declared carrier")
    allowed = set(carrier)
    selector = dict(mapping)
    if any(target not in allowed for target in selector.values()):
        raise ValueError("selector target escapes the declared carrier")
    return selector


def effective_selector_edges(selector: Mapping[State, State]) -> Relation:
    return frozenset((source, target) for source, target in selector.items() if source != target)


def selector_relation_is_right_unique(selector: Mapping[State, State]) -> bool:
    seen: dict[State, State] = {}
    for source, target in effective_selector_edges(selector):
        prior = seen.get(source)
        if prior is not None and prior != target:
            return False
        seen[source] = target
    return True


def relation_sound(selector: Mapping[State, State], relation: Relation) -> bool:
    return effective_selector_edges(selector).issubset(relation)


def outgoing(state: State, relation: Relation) -> set[State]:
    return {target for source, target in relation if source == state}


def normal(state: State, relation: Relation) -> bool:
    return not outgoing(state, relation)


def reachable(start: State, relation: Relation) -> set[State]:
    seen = {start}
    queue: deque[State] = deque([start])
    while queue:
        source = queue.popleft()
        for target in outgoing(source, relation):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def confluent(states: Sequence[State], relation: Relation) -> bool:
    reach = {state: reachable(state, relation) for state in states}
    for source in states:
        descendants = reach[source]
        for left in descendants:
            for right in descendants:
                if reach[left].isdisjoint(reach[right]):
                    return False
    return True


def fixed_points(selector: Mapping[State, State]) -> set[State]:
    return {state for state, target in selector.items() if state == target}


def selector_fixed_points_equal_normals(states: Sequence[State], selector: Mapping[State, State], relation: Relation) -> bool:
    return fixed_points(selector) == {state for state in states if normal(state, relation)}


def selector_iterate(selector: Mapping[State, State], start: State, steps: int) -> State:
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    if start not in selector:
        raise ValueError("start state is outside selector domain")
    state = start
    for _ in range(steps):
        state = selector[state]
    return state


def reaches_fixed_point_within(selector: Mapping[State, State], start: State, max_nonfixed_steps: int) -> tuple[bool, State, int]:
    if max_nonfixed_steps < 0:
        raise ValueError("max_nonfixed_steps must be nonnegative")
    if start not in selector:
        raise ValueError("start state is outside selector domain")
    state = start
    nonfixed = 0
    while selector[state] != state:
        if nonfixed >= max_nonfixed_steps:
            return False, state, nonfixed
        state = selector[state]
        nonfixed += 1
    return True, state, nonfixed


def natural_rank_certificate(selector: Mapping[State, State], rank: Mapping[State, int]) -> bool:
    if set(rank) != set(selector):
        return False
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in rank.values()):
        return False
    return all(source == target or rank[target] < rank[source] for source, target in selector.items())


def normalize_ranked(
    states: Sequence[State],
    relation: Relation,
    selector: Mapping[State, State],
    rank: Mapping[State, int],
    start: State,
) -> State:
    carrier = _carrier(states)
    selector = make_selector(carrier, selector)
    if start not in set(carrier):
        raise ValueError("start state is outside the declared carrier")
    if not relation_sound(selector, relation):
        raise ValueError("selector is not relation-sound")
    if not selector_fixed_points_equal_normals(carrier, selector, relation):
        raise ValueError("selector fixed points must equal relation normal states")
    if not natural_rank_certificate(selector, rank):
        raise ValueError("invalid natural-rank progress certificate")
    ok, endpoint, _ = reaches_fixed_point_within(selector, start, rank[start])
    if not ok:
        raise RuntimeError("rank-certified selector failed to normalize within rank bound")
    if endpoint not in reachable(start, relation) or not normal(endpoint, relation):
        raise RuntimeError("normalizer endpoint is not a reachable relation normal form")
    return endpoint


def _validate_objective_vectors(
    candidates: Sequence[State], objective_vectors: Mapping[State, tuple[int, ...]]
) -> None:
    candidate_set = set(candidates)
    if set(objective_vectors) != candidate_set:
        raise ValueError("every candidate must have exactly one objective vector")
    vectors = tuple(objective_vectors.values())
    if any(not isinstance(vector, tuple) for vector in vectors):
        raise ValueError("objective vectors must be tuples")
    widths = {len(vector) for vector in vectors}
    if len(widths) != 1:
        raise ValueError("objective vectors must have one common finite arity")
    if any(
        not isinstance(value, int) or isinstance(value, bool)
        for vector in vectors
        for value in vector
    ):
        raise ValueError("objective values must be finite integers with a total order")


def lexicographic_select(
    candidates: Iterable[State],
    objective_vectors: Mapping[State, tuple[int, ...]],
    tie_order: Sequence[State],
) -> State:
    candidate_tuple = tuple(candidates)
    if not candidate_tuple or len(set(candidate_tuple)) != len(candidate_tuple):
        raise ValueError("candidate set must be finite, nonempty, and duplicate-free")
    candidate_set = set(candidate_tuple)
    _validate_objective_vectors(candidate_tuple, objective_vectors)
    if set(tie_order) != candidate_set or len(tie_order) != len(candidate_tuple):
        raise ValueError("final tie-break must contain every candidate exactly once")
    order_index = {candidate: index for index, candidate in enumerate(tie_order)}
    return min(candidate_tuple, key=lambda candidate: (objective_vectors[candidate], order_index[candidate]))


def argmin_without_tiebreak(candidates: Iterable[State], objective_vectors: Mapping[State, tuple[int, ...]]) -> set[State]:
    candidate_tuple = tuple(candidates)
    if not candidate_tuple or len(set(candidate_tuple)) != len(candidate_tuple):
        raise ValueError("candidate set must be finite, nonempty, and duplicate-free")
    _validate_objective_vectors(candidate_tuple, objective_vectors)
    best = min(objective_vectors[candidate] for candidate in candidate_tuple)
    return {candidate for candidate in candidate_tuple if objective_vectors[candidate] == best}


def all_selectors(n: int):
    states = tuple(range(n))
    for targets in product(states, repeat=n):
        yield {source: targets[source] for source in states}


def all_relations(n: int):
    states = tuple(range(n))
    possible = tuple((source, target) for source in states for target in states)
    for mask in range(1 << len(possible)):
        yield frozenset(edge for index, edge in enumerate(possible) if (mask >> index) & 1)


def selector_graph_battery() -> dict[str, int]:
    selector_count = 0
    right_unique_checks = 0
    for n in (1, 2, 3):
        for selector in all_selectors(n):
            selector_count += 1
            if not selector_relation_is_right_unique(selector):
                raise RuntimeError("deterministic selector graph was not right-unique")
            right_unique_checks += 1
    return {
        "carrier_count": 3,
        "total_selector_count": selector_count,
        "right_unique_checks": right_unique_checks,
    }


def relation_soundness_battery() -> dict[str, int]:
    pair_count = 0
    sound_count = 0
    fixed_normal_count = 0
    for n in (1, 2, 3):
        states = tuple(range(n))
        relations = tuple(all_relations(n))
        for selector in all_selectors(n):
            for relation in relations:
                pair_count += 1
                if relation_sound(selector, relation):
                    sound_count += 1
                    if selector_fixed_points_equal_normals(states, selector, relation):
                        fixed_normal_count += 1
    return {
        "selector_relation_pair_count": pair_count,
        "relation_sound_selector_pairs": sound_count,
        "fixed_point_normal_exact_pairs": fixed_normal_count,
    }


def rank_normalization_battery() -> dict[str, int]:
    selector_count = 0
    state_checks = 0
    for n in (1, 2, 3):
        states = tuple(range(n))
        rank = {state: state for state in states}
        for selector in all_selectors(n):
            if not natural_rank_certificate(selector, rank):
                continue
            selector_count += 1
            relation = effective_selector_edges(selector)
            if not selector_fixed_points_equal_normals(states, selector, relation):
                raise RuntimeError("rank control fixed points did not equal relation normals")
            for start in states:
                endpoint = normalize_ranked(states, relation, selector, rank, start)
                if not normal(endpoint, relation):
                    raise RuntimeError("rank control did not terminate at a normal form")
                state_checks += 1
    return {
        "rank_decreasing_selector_count": selector_count,
        "state_normalization_checks": state_checks,
    }


def lexicographic_battery() -> dict[str, int]:
    states = (0, 1, 2)
    checks = 0
    for mask in range(1, 1 << len(states)):
        candidates = tuple(state for state in states if (mask >> state) & 1)
        for bits in product((0, 1), repeat=3):
            objectives = {candidate: (bits[candidate],) for candidate in candidates}
            for global_order in permutations(states):
                tie_order = tuple(state for state in global_order if state in candidates)
                chosen = lexicographic_select(candidates, objectives, tie_order)
                if chosen not in candidates:
                    raise RuntimeError("lexicographic selector escaped candidate set")
                checks += 1
    return {"lexicographic_selection_checks": checks}


def counterexample_fixtures() -> dict[str, object]:
    fork_states = ("a", "b", "c")
    fork = make_relation(fork_states, (("a", "b"), ("a", "c")))
    fork_normals = sorted(state for state in fork_states if normal(state, fork))

    unsound_selector = make_selector(fork_states, {"a": "c", "b": "b", "c": "c"})
    only_ab = make_relation(fork_states, (("a", "b"),))

    cycle_states = (0, 1)
    cycle = make_relation(cycle_states, ((0, 1), (1, 0)))
    cycle_selector = make_selector(cycle_states, {0: 1, 1: 0})
    cycle_terminates, _, _ = reaches_fixed_point_within(cycle_selector, 0, 4)

    tied = {"b": (0,), "c": (0,)}
    tied_argmin = sorted(argmin_without_tiebreak(("b", "c"), tied))

    fork_selector = make_selector(fork_states, {"a": "b", "b": "b", "c": "c"})
    fork_rank = {"a": 1, "b": 0, "c": 0}
    selected = normalize_ranked(fork_states, fork, fork_selector, fork_rank, "a")

    return {
        "CX-REC-001": {
            "terminating_fixture": True,
            "reachable_normals_from_a": fork_normals,
            "normal_form_count": len(fork_normals),
            "selector_declared": False,
        },
        "CX-REC-002": {
            "selector_deterministic": True,
            "relation_sound": relation_sound(unsound_selector, only_ab),
            "selector_effective_edges": [list(edge) for edge in sorted(effective_selector_edges(unsound_selector))],
            "base_relation_edges": [list(edge) for edge in sorted(only_ab)],
        },
        "CX-REC-003": {
            "selector_deterministic": True,
            "relation_sound": relation_sound(cycle_selector, cycle),
            "reaches_fixed_point_within_four_steps": cycle_terminates,
        },
        "CX-REC-004": {
            "objective_vectors_equal": tied["b"] == tied["c"],
            "argmin_without_tiebreak": tied_argmin,
            "unique_without_tiebreak": len(tied_argmin) == 1,
        },
        "CX-REC-005": {
            "selector_relation_sound": relation_sound(fork_selector, fork),
            "selector_normal_form_from_a": selected,
            "base_reachable_normals_from_a": fork_normals,
            "base_relation_confluent": confluent(fork_states, fork),
        },
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-recovery-specialization-witness",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "selector_graphs": selector_graph_battery(),
            "relation_soundness": relation_soundness_battery(),
            "rank_normalization": rank_normalization_battery(),
            "lexicographic": lexicographic_battery(),
        },
        "fixtures": counterexample_fixtures(),
        "hard_boundaries": BOUNDARIES,
        "claim_boundary": "FINITE_SELECTOR_CONFORMANCE != GENERAL_RECOVERY_THEORY; EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("Recovery Specializations witness:", result["bounded_checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
