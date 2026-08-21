#!/usr/bin/env python3
"""Hardened BridgeCore executable wrapper after the second Codex audit.

The pre-audit implementation is preserved byte-for-byte in
run_precodex2_frozen.py. This wrapper tightens executable conformance around
empty carriers, intermediate-carrier identity, production associativity, and
counterexample derivation while preserving the existing API.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
FROZEN = Path(__file__).with_name("run_precodex2_frozen.py")

_spec = importlib.util.spec_from_file_location("bridge_core_precodex2_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen BridgeCore executable: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

# Re-export the frozen API first. Hardened functions below deliberately replace
# the names that need stronger conformance semantics.
for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

_ORIGINAL_FIXTURES = _frozen.fixtures


def validate_bridge(bridge: dict[str, object]) -> None:
    """Validate a finite BridgeSpec realization, including empty carriers."""
    for key in ("id", "source_type", "target_type", "source_version", "target_version"):
        value = bridge.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"bridge {key} must be a nonempty string")

    # Generic BridgeCore does not require either carrier to be inhabited.
    source = _frozen._strings(bridge.get("source_states", ()), "source_states", nonempty=False)
    target = _frozen._strings(bridge.get("target_states", ()), "target_states", nonempty=False)
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


def relation_image(bridge: dict[str, object]) -> frozenset[str]:
    validate_bridge(bridge)
    relation = bridge["relation"]
    if not isinstance(relation, frozenset):
        raise RuntimeError("validated relation unexpectedly malformed")
    return frozenset(b for _, b in relation)


def composability_errors(first: dict[str, object], second: dict[str, object]) -> tuple[str, ...]:
    validate_bridge(first)
    validate_bridge(second)
    errors: list[str] = []
    if first["target_type"] != second["source_type"]:
        errors.append("intermediate-type-mismatch")
    if first["target_version"] != second["source_version"]:
        errors.append("intermediate-version-mismatch")

    # In the finite reference model, a type/version label is not allowed to
    # conceal two different concrete carrier realizations.
    first_target = frozenset(first["target_states"])
    second_source = frozenset(second["source_states"])
    if first_target != second_source:
        errors.append("intermediate-carrier-mismatch")

    scope1 = first["scope"]
    scope2 = second["scope"]
    if not isinstance(scope1, frozenset) or not isinstance(scope2, frozenset):
        raise RuntimeError("validated scope unexpectedly malformed")
    if not (scope1 & scope2):
        errors.append("scope-intersection-empty")

    domain2 = second["domain"]
    if not isinstance(domain2, frozenset):
        raise RuntimeError("validated domain unexpectedly malformed")
    if not relation_image(first).issubset(domain2):
        errors.append("intermediate-image-outside-second-domain")
    return tuple(errors)


def is_composable(first: dict[str, object], second: dict[str, object]) -> bool:
    return not composability_errors(first, second)


def identity_bridge(
    states: Iterable[str], *, type_name: str, version: str,
    scope: Iterable[str], structure: Iterable[str]
) -> dict[str, object]:
    carrier = _frozen._strings(states, "identity states", nonempty=False)
    return _frozen.make_bridge(
        bridge_id=f"id:{type_name}@{version}",
        source_type=type_name,
        target_type=type_name,
        source_version=version,
        target_version=version,
        source_states=carrier,
        target_states=carrier,
        domain=carrier,
        relation=((x, x) for x in carrier),
        relation_kind="map",
        preserved_structure=structure,
        lost_structure=(),
        scope=scope,
    )


# Patch the frozen module globals used by its make_bridge/compose/fixture code.
_frozen.validate_bridge = validate_bridge
_frozen.relation_image = relation_image
_frozen.composability_errors = composability_errors
_frozen.is_composable = is_composable
_frozen.identity_bridge = identity_bridge

# compose itself is retained, but it now resolves the hardened validation and
# composability functions through the frozen module globals above.
compose = _frozen.compose
make_bridge = _frozen.make_bridge
bridge_view = _frozen.bridge_view


def associativity_exhaustive_check() -> dict[str, int]:
    """Exercise production compose over every ordered Fin2 relation triple."""
    carrier = ("0", "1")
    relations = _frozen.enumerate_fin2_relations()
    checked = 0
    for i, r1 in enumerate(relations):
        for j, r2 in enumerate(relations):
            for k, r3 in enumerate(relations):
                common = dict(
                    source_type="Fin2",
                    target_type="Fin2",
                    source_version="1",
                    target_version="1",
                    source_states=carrier,
                    target_states=carrier,
                    domain=carrier,
                    relation_kind="relation",
                    preserved_structure=(),
                    lost_structure=(),
                    scope=("assoc",),
                )
                b1 = make_bridge(bridge_id=f"assoc-b1-{i}-{j}-{k}", relation=r1, **common)
                b2 = make_bridge(bridge_id=f"assoc-b2-{i}-{j}-{k}", relation=r2, **common)
                b3 = make_bridge(bridge_id=f"assoc-b3-{i}-{j}-{k}", relation=r3, **common)

                left = compose(compose(b1, b2, bridge_id="assoc-left-12"), b3, bridge_id="assoc-left")
                right = compose(b1, compose(b2, b3, bridge_id="assoc-right-23"), bridge_id="assoc-right")
                for field in ("relation", "preserved_structure", "lost_structure", "scope"):
                    if left[field] != right[field]:
                        raise RuntimeError(f"UFT-BR-005 production associativity failure: {field}")
                checked += 1

    if checked != 4096:
        raise RuntimeError("Fin2 production relation triple count drift")
    return {
        "labelled_relations_fin2": 16,
        "ordered_relation_triples_checked": checked,
        "production_compose_exercised": checked,
    }


_frozen.associativity_exhaustive_check = associativity_exhaustive_check


def fixtures() -> dict[str, object]:
    result = _ORIGINAL_FIXTURES()

    # CX-BR-001 must derive its advertised metadata distinction from the actual
    # serialized fixtures, never from a hard-coded success flag.
    cx1 = result.get("CX-BR-001")
    if not isinstance(cx1, dict):
        raise RuntimeError("CX-BR-001 fixture payload missing")
    first = cx1.get("first")
    second = cx1.get("second")
    if not isinstance(first, dict) or not isinstance(second, dict):
        raise RuntimeError("CX-BR-001 serialized bridges missing")
    loss_sets_differ = first.get("lost_structure") != second.get("lost_structure")
    if not loss_sets_differ:
        raise RuntimeError("CX-BR-001 loss-set distinction disappeared")
    cx1["loss_sets_differ"] = loss_sets_differ

    # Matching type/version labels do not excuse different finite carrier
    # realizations of the alleged shared intermediate object.
    carrier_first = make_bridge(
        bridge_id="carrier-first", source_type="A", target_type="B",
        source_version="1", target_version="1",
        source_states=("a",), target_states=("b0", "b1"),
        domain=("a",), relation=(("a", "b0"),), relation_kind="map",
        preserved_structure=(), lost_structure=(), scope=("shared",),
    )
    carrier_second = make_bridge(
        bridge_id="carrier-second", source_type="B", target_type="C",
        source_version="1", target_version="1",
        source_states=("b0",), target_states=("c",),
        domain=("b0",), relation=(("b0", "c"),), relation_kind="map",
        preserved_structure=(), lost_structure=(), scope=("shared",),
    )
    carrier_errors = composability_errors(carrier_first, carrier_second)
    if carrier_errors != ("intermediate-carrier-mismatch",):
        raise RuntimeError("finite intermediate-carrier mismatch classification drift")
    result["CARRIER-MISMATCH"] = {"errors": list(carrier_errors)}

    # Empty source/target carriers are legal generic BridgeCore realizations.
    empty_relation = make_bridge(
        bridge_id="empty-carriers", source_type="Empty0", target_type="Empty1",
        source_version="1", target_version="1", source_states=(), target_states=(),
        domain=(), relation=(), relation_kind="relation",
        preserved_structure=(), lost_structure=(), scope=("fixture",),
    )
    empty_identity = identity_bridge(
        (), type_name="Empty0", version="1", scope=("fixture",), structure=()
    )
    if empty_relation["source_states"] or empty_relation["target_states"] or empty_identity["relation"]:
        raise RuntimeError("empty-carrier BridgeCore fixture drift")
    result["EMPTY-CARRIER"] = {
        "relation_bridge": bridge_view(empty_relation),
        "identity_bridge": bridge_view(empty_identity),
    }
    return result


_frozen.fixtures = fixtures


def run_suite() -> dict[str, object]:
    return _frozen.run_suite()


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
