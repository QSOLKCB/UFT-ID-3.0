#!/usr/bin/env python3
"""Finite conformance witnesses for UFT-ID planned PR #13 Epistemic Bridge."""
from __future__ import annotations

import argparse
import itertools
import json
from typing import Iterable

FIELDS = (
    "evidence_refs",
    "retrieved_refs",
    "inference_refs",
    "verification_receipts",
    "execution_receipts",
    "conflict_refs",
)
AUTHORITY_FIELDS = FIELDS


def _refs(values: Iterable[str], label: str) -> frozenset[str]:
    out = frozenset(values)
    if any(not isinstance(x, str) or not x for x in out):
        raise ValueError(f"{label} must contain nonempty strings")
    return out


def make_state(
    *,
    evidence_refs: Iterable[str] = (),
    retrieved_refs: Iterable[str] = (),
    inference_refs: Iterable[str] = (),
    verification_receipts: Iterable[str] = (),
    execution_receipts: Iterable[str] = (),
    conflict_refs: Iterable[str] = (),
    scope: Iterable[str] = ("default",),
) -> dict[str, frozenset[str]]:
    state = {
        "evidence_refs": _refs(evidence_refs, "evidence_refs"),
        "retrieved_refs": _refs(retrieved_refs, "retrieved_refs"),
        "inference_refs": _refs(inference_refs, "inference_refs"),
        "verification_receipts": _refs(verification_receipts, "verification_receipts"),
        "execution_receipts": _refs(execution_receipts, "execution_receipts"),
        "conflict_refs": _refs(conflict_refs, "conflict_refs"),
        "scope": _refs(scope, "scope"),
    }
    validate_state(state)
    return state


def validate_state(state: dict[str, frozenset[str]]) -> None:
    expected = set(FIELDS) | {"scope"}
    if set(state) != expected:
        raise ValueError("EpistemicState field set drift")
    for field in expected:
        value = state[field]
        if not isinstance(value, frozenset):
            raise ValueError(f"{field} must be a frozenset")
        if any(not isinstance(x, str) or not x for x in value):
            raise ValueError(f"{field} must contain nonempty strings")
    if not state["scope"]:
        raise ValueError("scope must be nonempty")
    activity = set(FIELDS) - {"evidence_refs"}
    if any(state[field] for field in activity) and not state["evidence_refs"]:
        raise ValueError("authority activity requires evidence_refs")


def unknown(state: dict[str, frozenset[str]]) -> bool:
    validate_state(state)
    return all(not state[field] for field in FIELDS)


def conflict(state: dict[str, frozenset[str]]) -> bool:
    validate_state(state)
    return bool(state["conflict_refs"])


def verified(state: dict[str, frozenset[str]]) -> bool:
    validate_state(state)
    return bool(state["verification_receipts"])


def executed(state: dict[str, frozenset[str]]) -> bool:
    validate_state(state)
    return bool(state["execution_receipts"])


def authority_vector(state: dict[str, frozenset[str]]) -> tuple[frozenset[str], ...]:
    validate_state(state)
    return tuple(state[field] for field in AUTHORITY_FIELDS)


def _copy(state: dict[str, frozenset[str]], **changes: frozenset[str]) -> dict[str, frozenset[str]]:
    payload = dict(state)
    payload.update(changes)
    validate_state(payload)
    return payload


def retrieve(state: dict[str, frozenset[str]], source_ref: str) -> dict[str, frozenset[str]]:
    validate_state(state)
    if not source_ref:
        raise ValueError("source_ref must be nonempty")
    return _copy(
        state,
        evidence_refs=state["evidence_refs"] | {f"evidence:{source_ref}"},
        retrieved_refs=state["retrieved_refs"] | {source_ref},
    )


def infer(state: dict[str, frozenset[str]], inference_ref: str) -> dict[str, frozenset[str]]:
    validate_state(state)
    if not inference_ref:
        raise ValueError("inference_ref must be nonempty")
    return _copy(
        state,
        evidence_refs=state["evidence_refs"] | {f"premise:{inference_ref}"},
        inference_refs=state["inference_refs"] | {inference_ref},
    )


def execute(state: dict[str, frozenset[str]], receipt: str) -> dict[str, frozenset[str]]:
    validate_state(state)
    if not receipt:
        raise ValueError("execution receipt must be nonempty")
    return _copy(
        state,
        evidence_refs=state["evidence_refs"] | {f"execution-evidence:{receipt}"},
        execution_receipts=state["execution_receipts"] | {receipt},
    )


def add_conflict(state: dict[str, frozenset[str]], conflict_ref: str) -> dict[str, frozenset[str]]:
    validate_state(state)
    if not conflict_ref:
        raise ValueError("conflict_ref must be nonempty")
    return _copy(
        state,
        evidence_refs=state["evidence_refs"] | {f"conflict-evidence:{conflict_ref}"},
        conflict_refs=state["conflict_refs"] | {conflict_ref},
    )


def verify(state: dict[str, frozenset[str]], receipt: str) -> dict[str, frozenset[str]]:
    validate_state(state)
    if not state["evidence_refs"]:
        raise ValueError("verification requires evidence_refs")
    if not receipt:
        raise ValueError("verification receipt must be nonempty")
    return _copy(state, verification_receipts=state["verification_receipts"] | {receipt})


def transport(state: dict[str, frozenset[str]], bridge_scope: Iterable[str]) -> dict[str, frozenset[str]]:
    validate_state(state)
    scope = _refs(bridge_scope, "bridge_scope")
    if not scope:
        raise ValueError("bridge_scope must be nonempty")
    target_scope = state["scope"] & scope
    if not target_scope:
        raise ValueError("epistemic transport scope intersection must be nonempty")
    return _copy(state, scope=target_scope)


def raw_presence_vectors() -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product((0, 1), repeat=6))


def valid_presence_vector(bits: tuple[int, ...]) -> bool:
    if len(bits) != 6 or any(bit not in (0, 1) for bit in bits):
        raise ValueError("presence vector must contain six binary values")
    evidence, retrieved, inferred, verified_bit, executed_bit, conflict_bit = bits
    return bool(evidence) or not any((retrieved, inferred, verified_bit, executed_bit, conflict_bit))


def state_from_presence(bits: tuple[int, ...]) -> dict[str, frozenset[str]]:
    if not valid_presence_vector(bits):
        raise ValueError("invalid normalized epistemic presence vector")
    evidence, retrieved, inferred, verified_bit, executed_bit, conflict_bit = bits
    return make_state(
        evidence_refs=("e",) if evidence else (),
        retrieved_refs=("r",) if retrieved else (),
        inference_refs=("i",) if inferred else (),
        verification_receipts=("v",) if verified_bit else (),
        execution_receipts=("x",) if executed_bit else (),
        conflict_refs=("c",) if conflict_bit else (),
        scope=("s",),
    )


def finite_shape_check() -> dict[str, int]:
    raw = raw_presence_vectors()
    valid = [bits for bits in raw if valid_presence_vector(bits)]
    if len(raw) != 64 or len(valid) != 33:
        raise RuntimeError("epistemic presence-vector count drift")
    for bits in valid:
        state = state_from_presence(bits)
        if conflict(state) and unknown(state):
            raise RuntimeError("UFT-EP-003 conflict/unknown disjointness failure")
    return {"raw_presence_vectors": len(raw), "valid_normalized_shapes": len(valid)}


def operation_check() -> dict[str, object]:
    base = make_state(scope=("a", "b", "c"))
    r = retrieve(base, "src")
    i = infer(base, "inf")
    x = execute(base, "exec")
    c = add_conflict(base, "cx")
    for candidate in (r, i, x, c):
        if verified(candidate):
            raise RuntimeError("UFT-EP-002 non-verification operation created verification")
    v = verify(r, "verify-1")
    if not verified(v):
        raise RuntimeError("explicit verification receipt did not establish verified predicate")

    transported = transport(v, ("b", "c", "d"))
    if authority_vector(transported) != authority_vector(v):
        raise RuntimeError("UFT-EP-001 transport changed authority vector")
    if transported["scope"] != frozenset({"b", "c"}):
        raise RuntimeError("UFT-EP-005 scope intersection drift")
    twice = transport(transported, ("c", "z"))
    if authority_vector(twice) != authority_vector(v):
        raise RuntimeError("UFT-EP-004 repeated transport accumulated authority")
    if twice["scope"] != frozenset({"c"}):
        raise RuntimeError("repeated transport scope drift")

    conflict_verified = verify(c, "verify-conflict-source")
    if not (verified(conflict_verified) and conflict(conflict_verified)):
        raise RuntimeError("CX-EP-005 verified conflict representation drift")

    return {
        "retrieve_verified": verified(r),
        "infer_verified": verified(i),
        "execute_verified": verified(x),
        "conflict_unknown": unknown(c),
        "verified_conflict": verified(conflict_verified) and conflict(conflict_verified),
        "scope_after_one_transport": sorted(transported["scope"]),
        "scope_after_two_transports": sorted(twice["scope"]),
    }


def fixtures() -> dict[str, object]:
    base = make_state(scope=("fixture",))
    retrieved = retrieve(base, "source")
    inferred = infer(base, "inference")
    executed_state = execute(base, "execution")
    conflicted = add_conflict(base, "conflict")
    verified_conflict = verify(conflicted, "verification")
    return {
        "CX-EP-001": {"retrieved": True, "verified": verified(retrieved)},
        "CX-EP-002": {"inferred": True, "verified": verified(inferred)},
        "CX-EP-003": {"executed": executed(executed_state), "verified": verified(executed_state)},
        "CX-EP-004": {"conflict": conflict(conflicted), "unknown": unknown(conflicted)},
        "CX-EP-005": {"verified": verified(verified_conflict), "conflict": conflict(verified_conflict)},
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-epistemic-bridge-finite-conformance",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "presence_shapes": finite_shape_check(),
            "operations": operation_check(),
        },
        "fixtures": fixtures(),
        "claim_boundary": (
            "FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY; "
            "STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION; VERIFIED != TRUE"
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
        shapes = result["bounded_checks"]["presence_shapes"]
        print("Epistemic Bridge finite conformance: ok")
        print("raw vectors:", shapes["raw_presence_vectors"])
        print("valid normalized shapes:", shapes["valid_normalized_shapes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
