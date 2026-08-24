#!/usr/bin/env python3
"""Live compatibility wrapper around the frozen post-PR13 BridgeCore validator.

The exact BridgeCore validator merged in GitHub PR #13 is preserved as
validate_bridge_core_pr13_frozen.py. This wrapper replays that validator against
its historical PR12-active roadmap snapshot, then independently validates the
current live roadmap without changing BridgeCore theorem semantics.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_bridge_core_pr13_frozen.py"
ROADMAP = ROOT / "machine/roadmap_state.json"

_spec = importlib.util.spec_from_file_location("bridge_validator_pr13_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen BridgeCore validator: {FROZEN}")
_prior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prior)

for _name in dir(_prior):
    if not _name.startswith("__") and _name not in {"validate", "main"}:
        globals()[_name] = getattr(_prior, _name)

HISTORICAL_ROADMAP_STATE = {
    "type": "uft-id-roadmap-state",
    "schema_version": "1.0.0",
    "snapshot_date": "2026-08-21",
    "basis_commit": "a72dab3170e9880ca8bf120766d8547d6cc0110b",
    "completed": [5, 6, 7, 8, 9, 11],
    "active_planned_surface": 12,
    "deferred": [10],
    "sequence": [
        {"planned_pr": 9, "surface": "deterministic-observation-calculus", "status": "complete"},
        {"planned_pr": 10, "surface": "lean-observation-foundation", "status": "deferred-independent-formal-proof-track"},
        {"planned_pr": 11, "surface": "relation-first-recovery-core-plus-graph-realization-interlude", "status": "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"},
        {"planned_pr": 12, "surface": "bridge-core", "status": "active-implemented-in-current-change"},
        {"planned_pr": 13, "surface": "epistemic-bridge-specialization", "status": "planned"},
        {"planned_pr": 14, "surface": "representation-and-congruence-calculus", "status": "planned"},
        {"planned_pr": 15, "surface": "information-comparability-core", "status": "planned"},
        {"planned_pr": 16, "surface": "recovery-specializations", "status": "planned"},
        {"planned_pr": 17, "surface": "continuum-stochastic-prevalence-obligations", "status": "planned"},
        {"planned_pr": 18, "surface": "empirical-falsification-profile", "status": "planned"},
    ],
    "compatibility_note": "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot for PR8/PR9 receipt and validator compatibility. This file is the live post-PR11 schedule authority.",
    "fixture_policy": "Minimal fixtures travel with the theorem or counterexample that requires them.",
    "rules": [
        "NO_GIANT_FORMALIZATION_PR",
        "NO_STANDALONE_FINITE_FIXTURE_ZOO",
        "Lean deferral does not prevent repository-contained mathematical proofs, finite conformance witnesses, or later theorem targets from being frozen.",
        "A unique-selection claim requires an actual discriminating theorem or uniqueness proof, not compatibility or one successful construction.",
        "No semantic lifting is licensed without an explicit typed bridge declaring preserved structure, lost structure, scope, and version compatibility.",
    ],
}

EXPECTED_LIVE_ROADMAP = {
    "type": "uft-id-roadmap-state",
    "schema_version": "1.6.0",
    "snapshot_date": "2026-08-25",
    "basis_commit": "353e55a11a8cb6d6bcf571110e0fd6f32823fc77",
    "completed": [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17],
    "active_planned_surface": 18,
    "deferred": [10],
}


def validate() -> dict[str, object]:
    original_load = _prior._frozen.load_json
    try:
        def compat(path: Path):
            if path == _prior._frozen.PATHS["roadmap_state"]:
                return copy.deepcopy(HISTORICAL_ROADMAP_STATE)
            return original_load(path)
        _prior._frozen.load_json = compat
        result = _prior.validate()
    finally:
        _prior._frozen.load_json = original_load

    errors = list(result.get("errors", []))
    live = json.loads(ROADMAP.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_LIVE_ROADMAP.items():
        if live.get(key) != expected:
            errors.append(f"BridgeCore live roadmap {key} drift")
    sequence = live.get("sequence")
    if not isinstance(sequence, list):
        errors.append("BridgeCore live roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(12, {}).get("status") != "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7": errors.append("BridgeCore live roadmap must mark planned PR #12 complete")
        if by_pr.get(13, {}).get("status") != "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b": errors.append("BridgeCore live roadmap must mark planned PR #13 complete")
        if by_pr.get(14, {}).get("status") != "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f": errors.append("BridgeCore live roadmap must mark planned PR #14 complete")
        if by_pr.get(15, {}).get("status") != "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813": errors.append("BridgeCore live roadmap must mark planned PR #15 complete")
        if by_pr.get(16, {}).get("status") != "complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f": errors.append("BridgeCore live roadmap must mark planned PR #16 complete")
        if by_pr.get(17, {}).get("status") != "complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77": errors.append("BridgeCore live roadmap must mark planned PR #17 complete")
        if by_pr.get(18, {}).get("status") != "active-implemented-in-current-change": errors.append("BridgeCore live roadmap active surface must be PR #18")
    return {**result, "status": "error" if errors else "ok", "errors": errors}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"BridgeCore authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]: print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
