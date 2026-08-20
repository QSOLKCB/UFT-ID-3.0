#!/usr/bin/env python3
"""Finite conformance witnesses for the UFT-ID relation/reachability core."""
from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from typing import Iterable

State = str
Edge = tuple[State, State]


def _states(states: Iterable[State]) -> tuple[State, ...]:
    out = tuple(states)
    if len(out) != len(set(out)):
        raise ValueError("states must be unique")
    if any(not isinstance(x, str) or not x for x in out):
        raise ValueError("states must be non-empty strings")
    return out


def _edges(states: tuple[State, ...], edges: Iterable[Edge]) -> frozenset[Edge]:
    allowed = set(states)
    out: set[Edge] = set()
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError("each edge must be a pair")
        a, b = edge
        if a not in allowed or b not in allowed:
            raise ValueError(f"edge endpoint outside carrier: {edge}")
        out.add((a, b))
    return frozenset(out)


def successors(states: Iterable[State], edges: Iterable[Edge], x: State) -> tuple[State, ...]:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    if x not in carrier:
        raise ValueError("source state outside carrier")
    return tuple(y for y in carrier if (x, y) in rel)


def reachable(states: Iterable[State], edges: Iterable[Edge], source: State) -> frozenset[State]:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    if source not in carrier:
        raise ValueError("source state outside carrier")
    seen = {source}
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in carrier:
            if (x, y) in rel and y not in seen:
                seen.add(y)
                queue.append(y)
    return frozenset(seen)


def is_normal(states: Iterable[State], edges: Iterable[Edge], x: State) -> bool:
    return len(successors(states, edges, x)) == 0


def normal_forms_from(states: Iterable[State], edges: Iterable[Edge], source: State) -> frozenset[State]:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    return frozenset(x for x in reachable(carrier, rel, source) if is_normal(carrier, rel, x))


def joinable(states: Iterable[State], edges: Iterable[Edge], x: State, y: State) -> bool:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    return bool(reachable(carrier, rel, x) & reachable(carrier, rel, y))


def is_confluent(states: Iterable[State], edges: Iterable[Edge]) -> bool:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    for a in carrier:
        desc = reachable(carrier, rel, a)
        for b in desc:
            for c in desc:
                if not joinable(carrier, rel, b, c):
                    return False
    return True


def is_right_unique(states: Iterable[State], edges: Iterable[Edge]) -> bool:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    return all(len([y for y in carrier if (x, y) in rel]) <= 1 for x in carrier)


def is_terminating(states: Iterable[State], edges: Iterable[Edge]) -> bool:
    """For a finite carrier, forward termination is equivalent to acyclicity."""
    carrier = _states(states)
    rel = _edges(carrier, edges)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {x: WHITE for x in carrier}

    def visit(x: State) -> bool:
        color[x] = GRAY
        for y in carrier:
            if (x, y) not in rel:
                continue
            if color[y] == GRAY:
                return False
            if color[y] == WHITE and not visit(y):
                return False
        color[x] = BLACK
        return True

    return all(color[x] != WHITE or visit(x) for x in carrier)


def normalizes_from(states: Iterable[State], edges: Iterable[Edge], source: State) -> bool:
    return bool(normal_forms_from(states, edges, source))


def at_most_one_reachable_normal_from(
    states: Iterable[State], edges: Iterable[Edge], source: State
) -> bool:
    return len(normal_forms_from(states, edges, source)) <= 1


def unique_reachable_normal_from(
    states: Iterable[State], edges: Iterable[Edge], source: State
) -> bool:
    return len(normal_forms_from(states, edges, source)) == 1


def enumerate_relations(n: int):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n > 3:
        raise ValueError("bounded conformance enumeration requires 1 <= n <= 3")
    carrier = tuple(str(i) for i in range(n))
    possible = tuple(itertools.product(carrier, repeat=2))
    for mask in range(1 << (n * n)):
        edges = frozenset(possible[i] for i in range(len(possible)) if mask & (1 << i))
        yield carrier, edges


FIXTURES = {
    "CX-RW-FORK3": {
        "states": ("a", "b", "c"),
        "edges": frozenset({("a", "b"), ("a", "c")}),
    },
    "CX-RW-LOOP1": {
        "states": ("a",),
        "edges": frozenset({("a", "a")}),
    },
    "CX-RW-EXIT2": {
        "states": ("a", "b"),
        "edges": frozenset({("a", "a"), ("a", "b")}),
    },
}


def relation_properties(states: Iterable[State], edges: Iterable[Edge]) -> dict[str, object]:
    carrier = _states(states)
    rel = _edges(carrier, edges)
    return {
        "states": list(carrier),
        "edges": [list(edge) for edge in sorted(rel)],
        "right_unique": is_right_unique(carrier, rel),
        "confluent": is_confluent(carrier, rel),
        "terminating": is_terminating(carrier, rel),
        "normal_states": [x for x in carrier if is_normal(carrier, rel, x)],
        "reachable_normal_forms": {
            x: sorted(normal_forms_from(carrier, rel, x)) for x in carrier
        },
    }


def exhaustive_theorem_checks() -> dict[str, object]:
    counts: dict[str, int] = {}
    checked = 0
    implication_counts = {
        "reach_preservation_instances": 0,
        "right_unique_implies_confluent": 0,
        "confluent_implies_at_most_one_reachable_normal": 0,
        "terminating_implies_normalizes": 0,
        "terminating_and_confluent_implies_unique_reachable_normal": 0,
    }
    for n in (1, 2, 3):
        local = 0
        for carrier, rel in enumerate_relations(n):
            local += 1
            checked += 1
            right_unique = is_right_unique(carrier, rel)
            confluent = is_confluent(carrier, rel)
            terminating = is_terminating(carrier, rel)

            # UFT-RW-001 finite instances: enumerate every predicate P subseteq carrier.
            for p_mask in range(1 << n):
                predicate = {carrier[i] for i in range(n) if p_mask & (1 << i)}
                step_preserved = all(a not in predicate or b in predicate for a, b in rel)
                if not step_preserved:
                    continue
                for x in carrier:
                    if x not in predicate:
                        continue
                    if not reachable(carrier, rel, x).issubset(predicate):
                        raise RuntimeError("UFT-RW-001 finite conformance failure")
                    implication_counts["reach_preservation_instances"] += 1

            if right_unique:
                if not confluent:
                    raise RuntimeError("UFT-RW-002 finite conformance failure")
                implication_counts["right_unique_implies_confluent"] += 1

            if confluent:
                if any(not at_most_one_reachable_normal_from(carrier, rel, x) for x in carrier):
                    raise RuntimeError("UFT-RW-003 finite conformance failure")
                implication_counts["confluent_implies_at_most_one_reachable_normal"] += 1

            if terminating:
                if any(not normalizes_from(carrier, rel, x) for x in carrier):
                    raise RuntimeError("UFT-RW-004 finite conformance failure")
                implication_counts["terminating_implies_normalizes"] += 1

            if terminating and confluent:
                if any(not unique_reachable_normal_from(carrier, rel, x) for x in carrier):
                    raise RuntimeError("derived unique-normal corollary finite conformance failure")
                implication_counts["terminating_and_confluent_implies_unique_reachable_normal"] += 1
        counts[f"Fin{n}"] = local

    if counts != {"Fin1": 2, "Fin2": 16, "Fin3": 512} or checked != 530:
        raise RuntimeError("bounded relation enumeration cardinality drift")

    return {
        "relation_counts": counts,
        "total_relations": checked,
        "implication_applicable_counts": implication_counts,
    }


def minimality_checks() -> dict[str, object]:
    # FORK3: no terminating relation on <=2 states can have two distinct reachable normal forms.
    fork_smaller_exists = False
    for n in (1, 2):
        for carrier, rel in enumerate_relations(n):
            if not is_terminating(carrier, rel):
                continue
            if any(len(normal_forms_from(carrier, rel, x)) >= 2 for x in carrier):
                fork_smaller_exists = True

    # LOOP1: Fin1 already realizes confluent but nonterminating and no reachable normal form.
    loop = FIXTURES["CX-RW-LOOP1"]
    loop_witness = (
        is_confluent(loop["states"], loop["edges"])
        and not is_terminating(loop["states"], loop["edges"])
        and not normalizes_from(loop["states"], loop["edges"], "a")
    )

    # EXIT2: no one-state relation has a unique reachable normal form and nontermination.
    exit_smaller_exists = False
    for carrier, rel in enumerate_relations(1):
        if (not is_terminating(carrier, rel)) and unique_reachable_normal_from(carrier, rel, carrier[0]):
            exit_smaller_exists = True

    return {
        "fork3_no_smaller_terminating_nonunique_normal_fixture": not fork_smaller_exists,
        "loop1_one_state_witness": loop_witness,
        "exit2_no_one_state_unique_normal_nonterminating_fixture": not exit_smaller_exists,
    }


def genus_selection_fixture() -> dict[str, object]:
    """Synthetic specialization of UFT-SEL-001; not an assessment of an external paper."""
    states = ("common", "M10", "M30")
    edges = frozenset({("common", "M10"), ("common", "M30")})
    labels = {"common": None, "M10": 10, "M30": 30}
    normals = normal_forms_from(states, edges, "common")
    distinct_normal_labels = {labels[x] for x in normals}
    refutes_unique_selection = (
        normals == frozenset({"M10", "M30"})
        and len(distinct_normal_labels) == 2
        and not at_most_one_reachable_normal_from(states, edges, "common")
    )
    if not refutes_unique_selection:
        raise RuntimeError("UFT-SEL-001 genus fixture failed")
    return {
        "states": list(states),
        "edges": [list(edge) for edge in sorted(edges)],
        "labels": labels,
        "reachable_normal_forms_from_common": sorted(normals),
        "distinct_reachable_normal_labels": sorted(distinct_normal_labels),
        "at_most_one_reachable_normal_from_common": False,
        "refutes_unique_selection": True,
        "scope": "synthetic labelled-realization fork only; not an external-paper verdict",
    }


def run_suite() -> dict[str, object]:
    fixture_results = {name: relation_properties(**fixture) for name, fixture in FIXTURES.items()}

    fork = fixture_results["CX-RW-FORK3"]
    if not fork["terminating"] or fork["confluent"] or fork["reachable_normal_forms"]["a"] != ["b", "c"]:
        raise RuntimeError("CX-RW-FORK3 property drift")

    loop = fixture_results["CX-RW-LOOP1"]
    if not loop["confluent"] or loop["terminating"] or loop["normal_states"]:
        raise RuntimeError("CX-RW-LOOP1 property drift")

    exit2 = fixture_results["CX-RW-EXIT2"]
    if not exit2["confluent"] or exit2["terminating"] or exit2["right_unique"]:
        raise RuntimeError("CX-RW-EXIT2 property drift")
    if exit2["reachable_normal_forms"]["a"] != ["b"]:
        raise RuntimeError("CX-RW-EXIT2 unique reachable normal drift")

    return {
        "type": "uft-id-relation-core-finite-conformance",
        "schema_version": "1.0.0",
        "fixtures": fixture_results,
        "bounded_exhaustive_check": exhaustive_theorem_checks(),
        "minimality": minimality_checks(),
        "selection_specialization": genus_selection_fixture(),
        "claim_boundary": (
            "FINITE_CONFORMANCE != GENERAL_PROOF; "
            "REACHABLE != ADMISSIBLE != NORMAL != UNIQUE_REACHABLE_NORMAL; "
            "COMPATIBILITY != UNIQUE_SELECTION"
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
        print("relation core finite conformance: ok")
        print("relations checked:", result["bounded_exhaustive_check"]["total_relations"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
