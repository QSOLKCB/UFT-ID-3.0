#!/usr/bin/env python3
"""Finite conformance witnesses for UFT-ID PR #12 BridgeCore."""
from __future__ import annotations

import argparse
import itertools
import json
from typing import Iterable

State = str
Edge = tuple[State, State]


def _strings(values: Iterable[str], label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    out = tuple(values)
    if nonempty and not out:
        raise ValueError(f"{label} must be nonempty")
    if any(not isinstance(x, str) or not x for x in out):
        raise ValueError(f"{label} must contain nonempty strings")
    if len(out) != len(set(out)):
        raise ValueError(f"{label} must be unique")
    return out


def make_bridge(*, bridge_id: str, source_type: str, target_type: str, source_version: str,
                target_version: str, source_states: Iterable[State], target_states: Iterable[State],
                domain: Iterable[State], relation: Iterable[Edge], relation_kind: str,
                preserved_structure: Iterable[str], lost_structure: Iterable[str],
                scope: Iterable[str]) -> dict[str, object]:
    bridge = {
        "id": bridge_id,
        "source_type": source_type,
        "target_type": target_type,
        "source_version": source_version,
        "target_version": target_version,
        "source_states": tuple(source_states),
        "target_states": tuple(target_states),
        "domain": frozenset(domain),
        "relation": frozenset(relation),
        "relation_kind": relation_kind,
        "preserved_structure": frozenset(preserved_structure),
        "lost_structure": frozenset(lost_structure),
        "scope": frozenset(scope),
    }
    validate_bridge(bridge)
    return bridge


def validate_bridge(bridge: dict[str, object]) -> None:
    for key in ("id", "source_type", "target_type", "source_version", "target_version"):
        value = bridge.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"bridge {key} must be a nonempty string")

    source = _strings(bridge.get("source_states", ()), "source_states", nonempty=True)
    target = _strings(bridge.get("target_states", ()), "target_states", nonempty=True)
    source_set, target_set = set(source), set(target)

    domain = bridge.get("domain")
    if not isinstance(domain, frozenset):
        raise ValueError("bridge domain must be a frozenset")
    if any(x not in source_set for x in domain):
        raise ValueError("bridge domain escapes source carrier")

    relation = bridge.get("relation")
    if not isinstance(relation, frozenset):
        raise ValueError("bridge relation must be a frozenset")
    for edge in relation:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError("bridge relation edges must be pairs")
        a, b = edge
        if a not in domain or b not in target_set:
            raise ValueError("bridge relation edge violates domain/target carrier")

    kind = bridge.get("relation_kind")
    if kind not in {"map", "relation"}:
        raise ValueError("relation_kind must be map or relation")
    if kind == "map":
        for x in domain:
            outputs = [b for a, b in relation if a == x]
            if len(outputs) != 1:
                raise ValueError("map bridge must have exactly one output per domain state")

    scope = bridge.get("scope")
    preserved = bridge.get("preserved_structure")
    lost = bridge.get("lost_structure")
    for value, label in ((scope, "scope"), (preserved, "preserved_structure"), (lost, "lost_structure")):
        if not isinstance(value, frozenset):
            raise ValueError(f"{label} must be a frozenset")
        if any(not isinstance(x, str) or not x for x in value):
            raise ValueError(f"{label} must contain nonempty strings")
    if not scope:
        raise ValueError("bridge scope must be nonempty")
    if preserved & lost:
        raise ValueError("preserved_structure and lost_structure must be disjoint")


def relation_image(bridge: dict[str, object]) -> frozenset[State]:
    validate_bridge(bridge)
    return frozenset(b for _, b in bridge["relation"])


def composability_errors(first: dict[str, object], second: dict[str, object]) -> tuple[str, ...]:
    validate_bridge(first)
    validate_bridge(second)
    errors: list[str] = []
    if first["target_type"] != second["source_type"]:
        errors.append("intermediate-type-mismatch")
    if first["target_version"] != second["source_version"]:
        errors.append("intermediate-version-mismatch")
    if not (first["scope"] & second["scope"]):
        errors.append("scope-intersection-empty")
    if not relation_image(first).issubset(second["domain"]):
        errors.append("intermediate-image-outside-second-domain")
    return tuple(errors)


def is_composable(first: dict[str, object], second: dict[str, object]) -> bool:
    return not composability_errors(first, second)


def compose(first: dict[str, object], second: dict[str, object], *, bridge_id: str = "composite") -> dict[str, object]:
    errors = composability_errors(first, second)
    if errors:
        raise ValueError("bridges are not composable: " + ",".join(errors))
    rel1, rel2 = first["relation"], second["relation"]
    relation = frozenset((x, z) for x, y in rel1 for y2, z in rel2 if y == y2)
    p1, p2 = first["preserved_structure"], second["preserved_structure"]
    l1 = first["lost_structure"]
    return make_bridge(
        bridge_id=bridge_id,
        source_type=str(first["source_type"]),
        target_type=str(second["target_type"]),
        source_version=str(first["source_version"]),
        target_version=str(second["target_version"]),
        source_states=first["source_states"],
        target_states=second["target_states"],
        domain=first["domain"],
        relation=relation,
        relation_kind="map" if first["relation_kind"] == second["relation_kind"] == "map" else "relation",
        preserved_structure=p1 & p2,
        lost_structure=l1 | (p1 - p2),
        scope=first["scope"] & second["scope"],
    )


def identity_bridge(states: Iterable[State], *, type_name: str, version: str,
                    scope: Iterable[str], structure: Iterable[str]) -> dict[str, object]:
    carrier = _strings(states, "identity states", nonempty=True)
    return make_bridge(
        bridge_id=f"id:{type_name}@{version}", source_type=type_name, target_type=type_name,
        source_version=version, target_version=version, source_states=carrier,
        target_states=carrier, domain=carrier, relation=((x, x) for x in carrier),
        relation_kind="map", preserved_structure=structure, lost_structure=(), scope=scope,
    )


def bridge_view(bridge: dict[str, object]) -> dict[str, object]:
    validate_bridge(bridge)
    return {
        "id": bridge["id"], "source_type": bridge["source_type"], "target_type": bridge["target_type"],
        "source_version": bridge["source_version"], "target_version": bridge["target_version"],
        "source_states": list(bridge["source_states"]), "target_states": list(bridge["target_states"]),
        "domain": sorted(bridge["domain"]), "relation": [list(edge) for edge in sorted(bridge["relation"])],
        "relation_kind": bridge["relation_kind"], "preserved_structure": sorted(bridge["preserved_structure"]),
        "lost_structure": sorted(bridge["lost_structure"]), "scope": sorted(bridge["scope"]),
    }


def enumerate_fin2_relations() -> tuple[frozenset[Edge], ...]:
    carrier = ("0", "1")
    possible = tuple(itertools.product(carrier, repeat=2))
    return tuple(frozenset(possible[i] for i in range(4) if mask & (1 << i)) for mask in range(16))


def compose_relation(first: frozenset[Edge], second: frozenset[Edge]) -> frozenset[Edge]:
    return frozenset((x, z) for x, y in first for y2, z in second if y == y2)


def associativity_exhaustive_check() -> dict[str, int]:
    relations = enumerate_fin2_relations()
    checked = 0
    for r1 in relations:
        for r2 in relations:
            for r3 in relations:
                if compose_relation(compose_relation(r1, r2), r3) != compose_relation(r1, compose_relation(r2, r3)):
                    raise RuntimeError("UFT-BR-005 finite relation associativity failure")
                checked += 1
    if checked != 4096:
        raise RuntimeError("Fin2 relation triple count drift")
    return {"labelled_relations_fin2": 16, "ordered_relation_triples_checked": checked}


def partial_structure_declarations(labels: tuple[str, ...]) -> tuple[tuple[frozenset[str], frozenset[str]], ...]:
    declarations: list[tuple[frozenset[str], frozenset[str]]] = []
    for assignments in itertools.product(("P", "L", "U"), repeat=len(labels)):
        p = frozenset(label for label, tag in zip(labels, assignments) if tag == "P")
        l = frozenset(label for label, tag in zip(labels, assignments) if tag == "L")
        declarations.append((p, l))
    return tuple(declarations)


def preservation_loss_exhaustive_check() -> dict[str, int]:
    labels = ("a", "b", "c")
    declarations = partial_structure_declarations(labels)
    checked = 0
    for i, (p1, l1) in enumerate(declarations):
        for j, (p2, l2) in enumerate(declarations):
            first = make_bridge(
                bridge_id=f"meta-first-{i}-{j}", source_type="A", target_type="B",
                source_version="1", target_version="1", source_states=("a",), target_states=("b",),
                domain=("a",), relation=(("a", "b"),), relation_kind="map",
                preserved_structure=p1, lost_structure=l1, scope=("s",),
            )
            second = make_bridge(
                bridge_id=f"meta-second-{i}-{j}", source_type="B", target_type="C",
                source_version="1", target_version="1", source_states=("b",), target_states=("c",),
                domain=("b",), relation=(("b", "c"),), relation_kind="map",
                preserved_structure=p2, lost_structure=l2, scope=("s",),
            )
            composite = compose(first, second, bridge_id=f"meta-composite-{i}-{j}")
            expected_p = p1 & p2
            expected_l = l1 | (p1 - p2)
            if composite["preserved_structure"] != expected_p:
                raise RuntimeError("UFT-BR-002 production preservation intersection failure")
            if composite["lost_structure"] != expected_l:
                raise RuntimeError("UFT-BR-003 production loss propagation failure")
            if not l1.issubset(composite["lost_structure"]):
                raise RuntimeError("UFT-BR-003 loss monotonicity failure")
            if composite["preserved_structure"] & composite["lost_structure"]:
                raise RuntimeError("composite preservation/loss disjointness failure")
            checked += 1
    if len(declarations) != 27 or checked != 729:
        raise RuntimeError("partial preservation/loss declaration count drift")
    return {
        "structure_labels": 3,
        "valid_partial_structure_declarations": 27,
        "ordered_structure_declaration_pairs_checked": checked,
        "ordered_preservation_pairs_checked": checked,
    }


def fixtures() -> dict[str, object]:
    identity_like = make_bridge(
        bridge_id="endpoint-identity", source_type="TwoState", target_type="TwoStateOut",
        source_version="1", target_version="1", source_states=("s0", "s1"), target_states=("t0", "t1"),
        domain=("s0", "s1"), relation=(("s0", "t0"), ("s1", "t1")), relation_kind="map",
        preserved_structure=("distinguishability", "label"), lost_structure=(), scope=("fixture",),
    )
    collapse = make_bridge(
        bridge_id="endpoint-collapse", source_type="TwoState", target_type="TwoStateOut",
        source_version="1", target_version="1", source_states=("s0", "s1"), target_states=("t0", "t1"),
        domain=("s0", "s1"), relation=(("s0", "t0"), ("s1", "t0")), relation_kind="map",
        preserved_structure=("label",), lost_structure=("distinguishability",), scope=("fixture",),
    )
    if identity_like["relation"] == collapse["relation"]:
        raise RuntimeError("CX-BR-001 relation difference disappeared")

    version_first = make_bridge(
        bridge_id="version-first", source_type="A", target_type="B", source_version="1", target_version="1",
        source_states=("a",), target_states=("b",), domain=("a",), relation=(("a", "b"),),
        relation_kind="map", preserved_structure=("x",), lost_structure=(), scope=("shared",),
    )
    version_second = make_bridge(
        bridge_id="version-second", source_type="B", target_type="C", source_version="2", target_version="1",
        source_states=("b",), target_states=("c",), domain=("b",), relation=(("b", "c"),),
        relation_kind="map", preserved_structure=("x",), lost_structure=(), scope=("shared",),
    )
    version_errors = composability_errors(version_first, version_second)
    if version_errors != ("intermediate-version-mismatch",):
        raise RuntimeError("CX-BR-002 version mismatch classification drift")

    scope_first = dict(version_first); scope_first["id"] = "scope-first"; scope_first["scope"] = frozenset({"calibration-A"})
    scope_second = dict(version_second); scope_second["id"] = "scope-second"; scope_second["source_version"] = "1"; scope_second["scope"] = frozenset({"calibration-B"})
    validate_bridge(scope_first); validate_bridge(scope_second)
    scope_errors = composability_errors(scope_first, scope_second)
    if scope_errors != ("scope-intersection-empty",):
        raise RuntimeError("CX-BR-003 scope mismatch classification drift")

    projection = make_bridge(
        bridge_id="first-bit-projection", source_type="Bits2", target_type="Bit1", source_version="1", target_version="1",
        source_states=("00", "01", "10", "11"), target_states=("0", "1"), domain=("00", "01", "10", "11"),
        relation=(("00", "0"), ("01", "0"), ("10", "1"), ("11", "1")), relation_kind="map",
        preserved_structure=("first_bit",), lost_structure=("second_bit", "full_state_identity"), scope=("fixture",),
    )
    decoder = make_bridge(
        bridge_id="canonical-decoder", source_type="Bit1", target_type="Bits2", source_version="1", target_version="1",
        source_states=("0", "1"), target_states=("00", "01", "10", "11"), domain=("0", "1"),
        relation=(("0", "00"), ("1", "10")), relation_kind="map", preserved_structure=("first_bit",),
        lost_structure=(), scope=("fixture",),
    )
    decoded = compose(projection, decoder, bridge_id="lossy-roundtrip")
    identity_relation = frozenset((x, x) for x in projection["source_states"])
    if decoded["relation"] == identity_relation or not projection["lost_structure"].issubset(decoded["lost_structure"]):
        raise RuntimeError("CX-BR-004 reconstruction boundary drift")

    neutral_bridge = make_bridge(
        bridge_id="neutral-target", source_type="N0", target_type="N1", source_version="1", target_version="1",
        source_states=("n0", "n1"), target_states=("m0", "m1"), domain=("n0", "n1"),
        relation=(("n0", "m0"), ("n1", "m1")), relation_kind="map",
        preserved_structure=("a", "b"), lost_structure=("c",), scope=("shared",),
    )
    complete_structure = neutral_bridge["preserved_structure"] | neutral_bridge["lost_structure"]
    id_source = identity_bridge(neutral_bridge["source_states"], type_name="N0", version="1", scope=("shared",), structure=complete_structure)
    id_target = identity_bridge(neutral_bridge["target_states"], type_name="N1", version="1", scope=("shared",), structure=complete_structure)
    left = compose(id_source, neutral_bridge, bridge_id="left-neutral")
    right = compose(neutral_bridge, id_target, bridge_id="right-neutral")
    for candidate in (left, right):
        if candidate["relation"] != neutral_bridge["relation"] or candidate["preserved_structure"] != neutral_bridge["preserved_structure"] or candidate["lost_structure"] != neutral_bridge["lost_structure"]:
            raise RuntimeError("UFT-BR-004 complete-metadata identity neutrality failure")

    partial_bridge = make_bridge(
        bridge_id="partial-meta", source_type="Q0", target_type="Q1", source_version="1", target_version="1",
        source_states=("q",), target_states=("r",), domain=("q",), relation=(("q", "r"),), relation_kind="map",
        preserved_structure=("a",), lost_structure=(), scope=("shared",),
    )
    oversized_identity = identity_bridge(("q",), type_name="Q0", version="1", scope=("shared",), structure=("a", "b"))
    partial_left = compose(oversized_identity, partial_bridge, bridge_id="partial-left")
    if partial_left["lost_structure"] != frozenset({"b"}):
        raise RuntimeError("UFT-BR-004 partial-metadata negative control drift")

    empty = make_bridge(
        bridge_id="empty-domain", source_type="E0", target_type="E1", source_version="1", target_version="1",
        source_states=("e",), target_states=("f",), domain=(), relation=(), relation_kind="relation",
        preserved_structure=(), lost_structure=(), scope=("fixture",),
    )
    if empty["domain"] or empty["relation"]:
        raise RuntimeError("empty-domain bridge fixture drift")

    return {
        "CX-BR-001": {"same_endpoint_types": True, "first": bridge_view(identity_like), "second": bridge_view(collapse), "relations_differ": True, "loss_sets_differ": True},
        "CX-BR-002": {"errors": list(version_errors)},
        "CX-BR-003": {"errors": list(scope_errors)},
        "CX-BR-004": {"projection": bridge_view(projection), "decoder": bridge_view(decoder), "composite": bridge_view(decoded), "exact_reconstruction": False},
        "UFT-BR-004": {"left_identity_neutral": True, "right_identity_neutral": True, "complete_structure_tracking_required": True, "partial_metadata_negative_control": bridge_view(partial_left)},
        "EMPTY-DOMAIN": bridge_view(empty),
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-bridge-core-finite-conformance",
        "schema_version": "1.0.1",
        "bounded_checks": {
            "relation_associativity": associativity_exhaustive_check(),
            "preservation_loss": preservation_loss_exhaustive_check(),
        },
        "fixtures": fixtures(),
        "claim_boundary": "FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF; STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION; BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("BridgeCore finite conformance: ok")
        print("Fin2 relation triples:", result["bounded_checks"]["relation_associativity"]["ordered_relation_triples_checked"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
