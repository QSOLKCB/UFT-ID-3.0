#!/usr/bin/env python3
"""Live Representation validator over the frozen pre-integration authority.

The theorem/contract audit remains in validate_representation_calculus_preintegration_frozen.py.
This wrapper replays that authority against the exact merged Representation roadmap snapshot,
then independently validates the current Recovery Specializations schedule.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_representation_calculus_preintegration_frozen.py"

_spec = importlib.util.spec_from_file_location("representation_validator_preintegration_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen Representation validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

# Preserve the exact corrections merged with planned PR #14.
_frozen.EXPECTED_THEOREMS["UFT-REP-001"]["statement"] = (
    "If B=P^{-1}AP for an invertible finite-dimensional change of basis P over R or C, "
    "then A and B have the same characteristic polynomial; trace, determinant, and rank "
    "are preserved under the same similarity transformation."
)
_frozen.EXPECTED_INVARIANT_DISCIPLINE["congruence"] = [
    "rank",
    "symmetry type for real symmetric matrices",
]

for _name in dir(_frozen):
    if not _name.startswith("__") and _name not in {"validate", "main", "load_json"}:
        globals()[_name] = getattr(_frozen, _name)

HISTORICAL_ROADMAP_STATE = {
    "type": "uft-id-roadmap-state",
    "schema_version": "1.2.0",
    "snapshot_date": "2026-08-24",
    "basis_commit": "083aa9ae9e812cae86302d856f70ad83e5cf806b",
    "completed": [5, 6, 7, 8, 9, 11, 12, 13],
    "active_planned_surface": 14,
    "deferred": [10],
    "sequence": [
        {"planned_pr": 9, "surface": "deterministic-observation-calculus", "status": "complete"},
        {"planned_pr": 10, "surface": "lean-observation-foundation", "status": "deferred-independent-formal-proof-track"},
        {"planned_pr": 11, "surface": "relation-first-recovery-core-plus-graph-realization-interlude", "status": "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"},
        {"planned_pr": 12, "surface": "bridge-core", "status": "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"},
        {"planned_pr": 13, "surface": "epistemic-bridge-specialization", "status": "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"},
        {"planned_pr": 14, "surface": "representation-and-congruence-calculus", "status": "active-implemented-in-current-change"},
        {"planned_pr": 15, "surface": "information-comparability-core", "status": "planned"},
        {"planned_pr": 16, "surface": "recovery-specializations", "status": "planned"},
        {"planned_pr": 17, "surface": "continuum-stochastic-prevalence-obligations", "status": "planned"},
        {"planned_pr": 18, "surface": "empirical-falsification-profile", "status": "planned"},
    ],
    "compatibility_note": "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, and Epistemic Bridge validators retain their own historical schedule snapshots. This file is the live post-Epistemic-Bridge schedule authority.",
    "fixture_policy": "Minimal fixtures travel with the theorem or counterexample that requires them.",
    "rules": [
        "NO_GIANT_FORMALIZATION_PR",
        "NO_STANDALONE_FINITE_FIXTURE_ZOO",
        "Lean deferral does not prevent repository-contained mathematical proofs, finite conformance witnesses, or later theorem targets from being frozen.",
        "A unique-selection claim requires an actual discriminating theorem or uniqueness proof, not compatibility or one successful construction.",
        "No semantic lifting is licensed without an explicit typed bridge declaring preserved structure, lost structure, scope, and version compatibility.",
        "Structural transport, retrieval, inference, execution, storage, or replay cannot create verification authority without an explicit epistemic operation and receipt.",
        "Conflict and unknown remain separately represented; verified and conflict may coexist.",
        "Every representation invariant must name the transformation class and hypotheses under which it is preserved.",
        "Similarity, congruence, coordinate change, and receiver re-encoding remain separately typed and cannot imply semantic or physical identity by name alone.",
    ],
}

_original_load_json = _frozen.load_json


def _historical_load_json(path: Path):
    if path.resolve() == _frozen.PATHS["roadmap"].resolve():
        return json.loads(json.dumps(HISTORICAL_ROADMAP_STATE))
    return _original_load_json(path)


def _live_roadmap_errors() -> list[str]:
    errors: list[str] = []
    roadmap = _original_load_json(_frozen.PATHS["roadmap"])
    if roadmap.get("schema_version") != "1.4.0":
        errors.append("representation live roadmap schema drift")
    if roadmap.get("basis_commit") != "22b589c4e2e2042d180d64db837f092a007e0813":
        errors.append("representation live roadmap basis commit must be merged Information Comparability PR")
    if roadmap.get("active_planned_surface") != 16:
        errors.append("representation live roadmap active surface must be PR #16")
    if roadmap.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13, 14, 15]:
        errors.append("representation live roadmap completed set drift")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("representation live roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(14, {}).get("status") != "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f":
            errors.append("representation live roadmap PR14 completion drift")
        if by_pr.get(15, {}).get("status") != "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813":
            errors.append("representation live roadmap PR15 completion drift")
        if by_pr.get(16, {}).get("status") != "active-implemented-in-current-change":
            errors.append("representation live roadmap PR16 active-state drift")
    serialized = json.dumps(roadmap, sort_keys=True).casefold()
    for token in _frozen.PRIVATE_PATTERNS:
        if token.casefold() in serialized:
            errors.append(f"representation live roadmap contains forbidden private locator: {token}")
    return errors


def validate() -> dict[str, object]:
    old_loader = _frozen.load_json
    try:
        _frozen.load_json = _historical_load_json
        result = _frozen.validate()
    finally:
        _frozen.load_json = old_loader
    errors = list(result.get("errors", []))
    errors.extend(_live_roadmap_errors())
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Representation authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
