#!/usr/bin/env python3
"""Current-state wrapper for the frozen PR #11 relation validator.

The merged PR #11 validator is preserved byte-for-byte in
validate_relation_core_frozen_pr11.py. This wrapper changes only the live
roadmap-state expectation as later formal surfaces complete. All PR11 relation
theorem, counterexample, selection, source, and proof checks remain frozen.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_relation_core_frozen_pr11.py"


def _load_frozen():
    spec = importlib.util.spec_from_file_location("uft_pr11_relation_validator_frozen", FROZEN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen PR11 validator: {FROZEN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_FROZEN = _load_frozen()

for _name in dir(_FROZEN):
    if _name.startswith("__") or _name in {"validate", "validate_documents", "main", "EXPECTED_ROADMAP_SEQUENCE", "EXPECTED_ROADMAP_STATE"}:
        continue
    globals()[_name] = getattr(_FROZEN, _name)

EXPECTED_ROADMAP_SEQUENCE = [
    (9, "deterministic-observation-calculus", "complete"),
    (10, "lean-observation-foundation", "deferred-independent-formal-proof-track"),
    (11, "relation-first-recovery-core-plus-graph-realization-interlude", "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"),
    (12, "bridge-core", "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"),
    (13, "epistemic-bridge-specialization", "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"),
    (14, "representation-and-congruence-calculus", "active-implemented-in-current-change"),
    (15, "information-comparability-core", "planned"),
    (16, "recovery-specializations", "planned"),
    (17, "continuum-stochastic-prevalence-obligations", "planned"),
    (18, "empirical-falsification-profile", "planned"),
]

EXPECTED_ROADMAP_STATE = {
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


def _live_roadmap_errors(roadmap_state: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if roadmap_state.get("active_planned_surface") != 14:
        errors.append("live roadmap active planned surface must be PR14")
    if roadmap_state.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13]:
        errors.append("live roadmap completed set drift")
    sequence = roadmap_state.get("sequence")
    actual_sequence: list[tuple[object, object, object]] = []
    if isinstance(sequence, list):
        for item in sequence:
            if isinstance(item, dict):
                actual_sequence.append((item.get("planned_pr"), item.get("surface"), item.get("status")))
    if actual_sequence != EXPECTED_ROADMAP_SEQUENCE:
        errors.append("live roadmap sequence/status drift")
    if roadmap_state != EXPECTED_ROADMAP_STATE:
        errors.append("live roadmap state canonical payload drift")
    _FROZEN.no_private_locators(roadmap_state, "roadmap state", errors)
    return errors


def validate_documents(contract, theorems, counterexamples, selection, cross_repo_patterns,
                       roadmap_state, base_contract, human, roadmap, *, check_paths: bool = True):
    frozen_state = copy.deepcopy(_FROZEN.EXPECTED_ROADMAP_STATE)
    result = _FROZEN.validate_documents(
        contract, theorems, counterexamples, selection, cross_repo_patterns,
        frozen_state, base_contract, human, roadmap, check_paths=check_paths,
    )
    errors = list(result.get("errors", []))
    errors.extend(_live_roadmap_errors(roadmap_state))
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def validate():
    missing = [str(path.relative_to(ROOT)) for path in PATHS.values() if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing relation authority file: {path}" for path in missing],
            "theorem_count": 0,
            "counterexample_count": 0,
            "public_context_ref_count": 0,
            "exhaustive_relation_count": 0,
        }
    return validate_documents(
        load(PATHS["contract"]),
        load(PATHS["theorems"]),
        load(PATHS["counterexamples"]),
        load(PATHS["selection"]),
        load(PATHS["cross_repo_patterns"]),
        load(PATHS["roadmap_state"]),
        load(PATHS["base_contract"]),
        PATHS["human"].read_text(encoding="utf-8"),
        PATHS["roadmap"].read_text(encoding="utf-8"),
        check_paths=True,
    )


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PR11 relation/selection core:", result["status"])
        for error in result["errors"]:
            print(" -", error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
