#!/usr/bin/env python3
"""Finite graph-realization and typed-incidence witnesses for UFT-ID 3.0."""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import deque
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
RELATION_RUN = ROOT / "experiments/relation/run.py"

State = str
Edge = tuple[State, State]
UndirectedEdge = tuple[State, State]
TypedLink = tuple[str, str, str]


def load_relation_module():
    spec = importlib.util.spec_from_file_location("uft_relation_run", RELATION_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load relation witness module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REL = load_relation_module()


def states_tuple(states: Iterable[State]) -> tuple[State, ...]:
    out = tuple(states)
    if any(not isinstance(x, str) or not x for x in out):
        raise ValueError("states must be non-empty strings")
    if len(out) != len(set(out)):
        raise ValueError("states must be unique")
    return out


def edge_set(states: tuple[State, ...], edges: Iterable[Edge]) -> frozenset[Edge]:
    allowed = set(states)
    out: set[Edge] = set()
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError("each edge must be a pair")
        a, b = edge
        if not isinstance(a, str) or not isinstance(b, str):
            raise ValueError("edge endpoints must be strings")
        if a not in allowed or b not in allowed:
            raise ValueError("edge endpoint outside carrier")
        out.add((a, b))
    return frozenset(out)


def undirected_edge_set(
    states: Iterable[State], edges: Iterable[UndirectedEdge]
) -> frozenset[UndirectedEdge]:
    carrier = states_tuple(states)
    allowed = set(carrier)
    out: set[UndirectedEdge] = set()
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError("each undirected edge must be a pair")
        a, b = edge
        if not isinstance(a, str) or not isinstance(b, str):
            raise ValueError("undirected edge endpoints must be strings")
        if a not in allowed or b not in allowed:
            raise ValueError("undirected edge endpoint outside carrier")
        if a == b:
            raise ValueError("undirected simple edge may not be a loop")
        out.add(tuple(sorted((a, b))))
    return frozenset(out)


def adjacency_matrix(states: Iterable[State], edges: Iterable[Edge]) -> list[list[int]]:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    index = {x: i for i, x in enumerate(carrier)}
    matrix = [[0 for _ in carrier] for _ in carrier]
    for a, b in rel:
        matrix[index[a]][index[b]] = 1
    return matrix


def boolean_reachability(
    states: Iterable[State], edges: Iterable[Edge]
) -> dict[str, frozenset[str]]:
    """Reflexive-transitive closure via independent Boolean Floyd-Warshall."""
    carrier = states_tuple(states)
    matrix = adjacency_matrix(carrier, edges)
    n = len(carrier)
    reach = [[bool(matrix[i][j]) or i == j for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            if not reach[i][k]:
                continue
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return {
        carrier[i]: frozenset(carrier[j] for j in range(n) if reach[i][j])
        for i in range(n)
    }


def outdegree(states: Iterable[State], edges: Iterable[Edge], x: State) -> int:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    if x not in carrier:
        raise ValueError("state outside carrier")
    return sum(1 for a, _ in rel if a == x)


def is_dag_kahn(states: Iterable[State], edges: Iterable[Edge]) -> bool:
    """Independent finite DAG check using Kahn's algorithm."""
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    indegree = {x: 0 for x in carrier}
    successors = {x: [] for x in carrier}
    for a, b in rel:
        successors[a].append(b)
        indegree[b] += 1
    queue = deque(x for x in carrier if indegree[x] == 0)
    visited = 0
    while queue:
        x = queue.popleft()
        visited += 1
        for y in successors[x]:
            indegree[y] -= 1
            if indegree[y] == 0:
                queue.append(y)
    return visited == len(carrier)


def strongly_connected_components(
    states: Iterable[State], edges: Iterable[Edge]
) -> tuple[frozenset[str], ...]:
    """Iterative Kosaraju SCC decomposition; no recursion-depth dependency."""
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    successors = {x: [] for x in carrier}
    predecessors = {x: [] for x in carrier}
    for a, b in rel:
        successors[a].append(b)
        predecessors[b].append(a)
    for x in carrier:
        successors[x].sort()
        predecessors[x].sort()

    visited: set[str] = set()
    finish_order: list[str] = []
    for start in carrier:
        if start in visited:
            continue
        visited.add(start)
        stack: list[tuple[str, int]] = [(start, 0)]
        while stack:
            vertex, next_index = stack[-1]
            neighbors = successors[vertex]
            if next_index < len(neighbors):
                neighbor = neighbors[next_index]
                stack[-1] = (vertex, next_index + 1)
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, 0))
            else:
                finish_order.append(vertex)
                stack.pop()

    assigned: set[str] = set()
    components: list[frozenset[str]] = []
    for start in reversed(finish_order):
        if start in assigned:
            continue
        members: set[str] = set()
        stack = [start]
        assigned.add(start)
        while stack:
            vertex = stack.pop()
            members.add(vertex)
            for neighbor in predecessors[vertex]:
                if neighbor not in assigned:
                    assigned.add(neighbor)
                    stack.append(neighbor)
        components.append(frozenset(members))

    return tuple(sorted(components, key=lambda c: tuple(sorted(c))))


def mutual_reachability_components(
    states: Iterable[State], edges: Iterable[Edge]
) -> tuple[frozenset[str], ...]:
    """Independent SCC oracle from mutual reachability equivalence classes."""
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    reach = boolean_reachability(carrier, rel)
    unassigned = set(carrier)
    components: list[frozenset[str]] = []
    for pivot in carrier:
        if pivot not in unassigned:
            continue
        component = frozenset(
            candidate
            for candidate in carrier
            if candidate in reach[pivot] and pivot in reach[candidate]
        )
        if not component or pivot not in component:
            raise RuntimeError("mutual-reachability SCC oracle produced invalid component")
        unassigned.difference_update(component)
        components.append(component)
    if unassigned:
        raise RuntimeError("mutual-reachability SCC oracle failed to cover carrier")
    return tuple(sorted(components, key=lambda c: tuple(sorted(c))))


def scc_partition_matches_mutual_reachability(
    states: Iterable[State], edges: Iterable[Edge], components: Iterable[frozenset[str]]
) -> bool:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    supplied = tuple(sorted(tuple(components), key=lambda c: tuple(sorted(c))))
    return supplied == mutual_reachability_components(carrier, rel)


def independent_sink_components(
    states: Iterable[State], edges: Iterable[Edge]
) -> tuple[frozenset[str], ...]:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    components = mutual_reachability_components(carrier, rel)
    sinks = [
        comp
        for comp in components
        if not any(a in comp and b not in comp for a, b in rel)
    ]
    return tuple(sorted(sinks, key=lambda c: tuple(sorted(c))))


def independent_condensation(
    states: Iterable[State], edges: Iterable[Edge]
) -> tuple[tuple[frozenset[str], ...], frozenset[tuple[int, int]]]:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    components = mutual_reachability_components(carrier, rel)
    owner = {v: index for index, comp in enumerate(components) for v in comp}
    c_edges = frozenset((owner[a], owner[b]) for a, b in rel if owner[a] != owner[b])
    return components, c_edges


def sink_components(states: Iterable[State], edges: Iterable[Edge]) -> tuple[frozenset[str], ...]:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    components = strongly_connected_components(carrier, rel)
    owner = {v: index for index, comp in enumerate(components) for v in comp}
    sinks = []
    for index, comp in enumerate(components):
        if not any(owner[a] == index and owner[b] != index for a, b in rel):
            sinks.append(comp)
    return tuple(sorted(sinks, key=lambda c: tuple(sorted(c))))


def condensation(
    states: Iterable[State], edges: Iterable[Edge]
) -> tuple[tuple[frozenset[str], ...], frozenset[tuple[int, int]]]:
    carrier = states_tuple(states)
    rel = edge_set(carrier, edges)
    components = strongly_connected_components(carrier, rel)
    owner = {v: index for index, comp in enumerate(components) for v in comp}
    c_edges = frozenset((owner[a], owner[b]) for a, b in rel if owner[a] != owner[b])
    return components, c_edges


def condensation_is_acyclic(states: Iterable[State], edges: Iterable[Edge]) -> bool:
    components, c_edges = condensation(states, edges)
    c_states = tuple(str(i) for i in range(len(components)))
    string_edges = tuple((str(a), str(b)) for a, b in c_edges)
    return is_dag_kahn(c_states, string_edges)


def simplify_rich_arcs(
    states: Iterable[State], rich_arcs: Iterable[dict[str, object]]
) -> frozenset[Edge]:
    carrier = states_tuple(states)
    allowed = set(carrier)
    out: set[Edge] = set()
    seen_ids: set[str] = set()
    for arc in rich_arcs:
        if not isinstance(arc, dict):
            raise ValueError("rich arc must be an object")
        if set(arc) != {"id", "source", "target", "label"}:
            raise ValueError("rich arc must contain exactly id/source/target/label")
        if any(not isinstance(arc[key], str) or not arc[key] for key in arc):
            raise ValueError("rich arc fields must be non-empty strings")
        arc_id = str(arc["id"])
        if arc_id in seen_ids:
            raise ValueError("rich arc ids must be unique")
        seen_ids.add(arc_id)
        source = str(arc["source"])
        target = str(arc["target"])
        if source not in allowed or target not in allowed:
            raise ValueError("rich arc endpoint outside carrier")
        out.add((source, target))
    return frozenset(out)


def validate_incidence(
    modules: Iterable[str], link_labels: Iterable[str], incidence: Iterable[TypedLink]
) -> frozenset[TypedLink]:
    module_tuple = states_tuple(modules)
    labels = tuple(link_labels)
    if any(not isinstance(label, str) or not label for label in labels):
        raise ValueError("link labels must be non-empty strings")
    if len(labels) != len(set(labels)):
        raise ValueError("link labels must be unique")
    module_set = set(module_tuple)
    label_set = set(labels)
    out: set[TypedLink] = set()
    for link in incidence:
        if not isinstance(link, tuple) or len(link) != 3:
            raise ValueError("incidence link must be a triple")
        a, label, b = link
        if a not in module_set or b not in module_set or label not in label_set:
            raise ValueError("incidence item outside declared modules/labels")
        out.add((a, label, b))
    return frozenset(out)


def tetrahedron_k4_fixture() -> dict[str, object]:
    vertices = ("0", "1", "2", "3")
    edges = undirected_edge_set(
        vertices,
        ((vertices[i], vertices[j]) for i in range(4) for j in range(i + 1, 4)),
    )
    degrees = {v: sum(1 for edge in edges if v in edge) for v in vertices}
    if len(edges) != 6 or set(degrees.values()) != {3}:
        raise RuntimeError("tetrahedron K4 fixture drift")
    return {
        "vertices": list(vertices),
        "edge_semantics": "undirected",
        "undirected_edges": [list(edge) for edge in sorted(edges)],
        "edge_count": 6,
        "degrees": degrees,
        "claim": "geometric tetrahedron 1-skeleton is K4",
        "boundary": "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
    }


def rich_projection_counterexample() -> dict[str, object]:
    states = ("u", "v")
    rich_a = (
        {"id": "alpha", "source": "u", "target": "v", "label": "L1"},
        {"id": "beta", "source": "u", "target": "v", "label": "L2"},
    )
    rich_b = ({"id": "gamma", "source": "u", "target": "v", "label": "L1"},)
    simple_a = simplify_rich_arcs(states, rich_a)
    simple_b = simplify_rich_arcs(states, rich_b)
    if rich_a == rich_b or simple_a != simple_b:
        raise RuntimeError("rich projection counterexample drift")
    return {
        "rich_a_arc_count": len(rich_a),
        "rich_b_arc_count": len(rich_b),
        "simple_projection": [list(edge) for edge in sorted(simple_a)],
        "distinct_sources_same_projection": True,
    }


def module_inventory_counterexample() -> dict[str, object]:
    modules = ("a", "b", "c")
    labels = ("link",)
    chain = validate_incidence(modules, labels, (("a", "link", "b"), ("b", "link", "c")))
    triangle = validate_incidence(
        modules, labels, (("a", "link", "b"), ("b", "link", "c"), ("c", "link", "a"))
    )
    if chain == triangle:
        raise RuntimeError("module inventory counterexample drift")
    return {
        "modules": list(modules),
        "chain_incidence": [list(item) for item in sorted(chain)],
        "triangle_incidence": [list(item) for item in sorted(triangle)],
        "same_inventory_distinct_incidence": True,
    }


def drawing_counterexample() -> dict[str, object]:
    vertices = ("hub", "a", "b", "c")
    edges = undirected_edge_set(
        vertices, (("hub", "a"), ("hub", "b"), ("hub", "c"))
    )
    drawing_a = {"hub": [0, 0], "a": [0, 1], "b": [-1, -1], "c": [1, -1]}
    drawing_b = {"hub": [10, 10], "a": [12, 10], "b": [8, 13], "c": [8, 7]}
    if drawing_a == drawing_b:
        raise RuntimeError("drawing counterexample drift")
    return {
        "vertices": list(vertices),
        "graph": "K1,3",
        "edge_semantics": "undirected",
        "undirected_edges": [list(edge) for edge in sorted(edges)],
        "drawing_a": drawing_a,
        "drawing_b": drawing_b,
        "same_graph_distinct_coordinates": True,
    }


def coupling_vs_placement_fixture() -> dict[str, object]:
    vertices = ("hub", "a", "b", "c")
    coupling = undirected_edge_set(
        vertices, (("hub", "a"), ("hub", "b"), ("hub", "c"))
    )
    placement = undirected_edge_set(
        vertices,
        (
            ("hub", "a"), ("hub", "b"), ("hub", "c"),
            ("a", "b"), ("b", "c"), ("a", "c"),
        ),
    )
    return {
        "vertices": list(vertices),
        "edge_semantics": "undirected",
        "coupling_undirected_edges": [list(x) for x in sorted(coupling)],
        "placement_undirected_edges": [list(x) for x in sorted(placement)],
        "coupling_graph": "K1,3",
        "placement_graph": "K4",
        "boundary": "COUPLING_GRAPH != PLACEMENT_GRAPH",
    }


def exhaustive_cross_checks() -> dict[str, object]:
    relation_counts: dict[str, int] = {}
    total_relations = 0
    adjacency_pair_checks = 0
    normal_state_checks = 0
    reachability_source_checks = 0
    termination_checks = 0
    scc_partition_checks = 0
    sink_scc_checks = 0
    condensation_checks = 0

    for n in (1, 2, 3):
        local = 0
        for carrier, rel in REL.enumerate_relations(n):
            local += 1
            total_relations += 1

            matrix = adjacency_matrix(carrier, rel)
            index = {x: i for i, x in enumerate(carrier)}
            for a in carrier:
                for b in carrier:
                    if bool(matrix[index[a]][index[b]]) != ((a, b) in rel):
                        raise RuntimeError("UFT-GR-001 adjacency identity failure")
                    adjacency_pair_checks += 1

            for x in carrier:
                graph_normal = outdegree(carrier, rel, x) == 0
                if graph_normal != REL.is_normal(carrier, rel, x):
                    raise RuntimeError("UFT-GR-002 normal/outdegree failure")
                normal_state_checks += 1

            boolean_reach = boolean_reachability(carrier, rel)
            for source in carrier:
                if boolean_reach[source] != REL.reachable(carrier, rel, source):
                    raise RuntimeError("UFT-GR-003 reachability cross-check failure")
                reachability_source_checks += 1

            dag = is_dag_kahn(carrier, rel)
            if dag != REL.is_terminating(carrier, rel):
                raise RuntimeError("UFT-GR-004 termination/DAG failure")
            termination_checks += 1

            production_components = strongly_connected_components(carrier, rel)
            independent_components = mutual_reachability_components(carrier, rel)
            if production_components != independent_components:
                raise RuntimeError("UFT-GR-005 SCC partition disagrees with mutual reachability")
            scc_partition_checks += 1

            sinks = sink_components(carrier, rel)
            expected_sinks = independent_sink_components(carrier, rel)
            if sinks != expected_sinks or not sinks:
                raise RuntimeError("UFT-GR-005 sink SCC disagreement")
            sink_scc_checks += 1

            production_condensation = condensation(carrier, rel)
            independent_c = independent_condensation(carrier, rel)
            if production_condensation != independent_c:
                raise RuntimeError("UFT-GR-006 condensation quotient disagreement")
            c_components, c_edges = independent_c
            c_states = tuple(str(i) for i in range(len(c_components)))
            c_string_edges = tuple((str(a), str(b)) for a, b in c_edges)
            if not is_dag_kahn(c_states, c_string_edges):
                raise RuntimeError("UFT-GR-006 independent condensation cycle")
            condensation_checks += 1

        relation_counts[f"Fin{n}"] = local

    expected = {"Fin1": 2, "Fin2": 16, "Fin3": 512}
    if relation_counts != expected or total_relations != 530:
        raise RuntimeError("bounded relation count drift")

    return {
        "relation_counts": relation_counts,
        "total_relations": total_relations,
        "adjacency_pair_checks": adjacency_pair_checks,
        "normal_state_checks": normal_state_checks,
        "reachability_source_checks": reachability_source_checks,
        "termination_checks": termination_checks,
        "scc_partition_checks": scc_partition_checks,
        "sink_scc_checks": sink_scc_checks,
        "condensation_checks": condensation_checks,
    }


def run_suite() -> dict[str, object]:
    exhaustive = exhaustive_cross_checks()
    expected_counts = {
        "adjacency_pair_checks": 4674,
        "normal_state_checks": 1570,
        "reachability_source_checks": 1570,
        "termination_checks": 530,
        "scc_partition_checks": 530,
        "sink_scc_checks": 530,
        "condensation_checks": 530,
    }
    for key, value in expected_counts.items():
        if exhaustive[key] != value:
            raise RuntimeError(f"{key} count drift")

    return {
        "type": "uft-id-graph-realization-finite-conformance",
        "schema_version": "1.0.1",
        "bounded_exhaustive_check": exhaustive,
        "positive_controls": {
            "tetrahedron_k4": tetrahedron_k4_fixture(),
            "coupling_vs_placement": coupling_vs_placement_fixture(),
        },
        "counterexamples": {
            "CX-GR-001": rich_projection_counterexample(),
            "CX-GR-002": module_inventory_counterexample(),
            "CX-GR-003": drawing_counterexample(),
        },
        "claim_boundary": (
            "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF; "
            "ALGEBRA != GRAPH != EMBEDDING != PHYSICS; "
            "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH; "
            "MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE"
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
        print("graph realization finite conformance: ok")
        print("relations checked:", result["bounded_exhaustive_check"]["total_relations"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
