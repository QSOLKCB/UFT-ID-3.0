#!/usr/bin/env python3
"""PR #21 schedule-advance wrapper for the live EFP compatibility validator.

The exact pre-advance validator is preserved in
validate_empirical_falsification_profile_pr21_pretag.py. EFP semantics remain
frozen; only the live post-EFP roadmap phase advances after the first Lean
observation source batch freeze. The roadmap schema/snapshot stay unchanged:
this is a phase transition, not a schema migration.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/validate_empirical_falsification_profile_pr21_pretag.py"
ROADMAP_STATE = ROOT / "machine/roadmap_state.json"

_spec = importlib.util.spec_from_file_location("efp_validator_pr21_pretag", BASE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load pre-tag EFP validator: {BASE}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__") and _name not in {"validate", "main", "_live_roadmap_errors"}:
        globals()[_name] = getattr(_base, _name)

EXPECTED_LIVE_ROADMAP = copy.deepcopy(_base.EXPECTED_LIVE_ROADMAP)
for _item in EXPECTED_LIVE_ROADMAP["sequence"]:
    if _item.get("planned_pr") == 10:
        _item["status"] = "active-post-merge-release-gate"
EXPECTED_LIVE_ROADMAP["compatibility_note"] = (
    "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, "
    "BridgeCore, Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, and EFP theorem "
    "authorities retain their historical semantics. This file is the live post-EFP schedule authority: the first "
    "PR #10 theorem batch is frozen and the next gate is exact merged-main validation plus an immutable source-release "
    "tag before any Lean proof implementation."
)
EXPECTED_LIVE_ROADMAP["rules"][2] = (
    "The first Lean theorem batch and dependency graph are frozen; exact merged-main validation and an immutable "
    "source-release tag must complete before any Lean/Lake/Mathlib proof implementation, while mathematical proof, "
    "Lean proof, runtime conformance, and empirical validation remain separately typed authorities."
)


def _live_roadmap_errors() -> list[str]:
    errors: list[str] = []
    roadmap = _base._original_load_json(ROADMAP_STATE)
    if roadmap.get("schema_version") != "1.7.0":
        errors.append("EFP live roadmap schema drift")
    if roadmap.get("snapshot_date") != "2026-08-24":
        errors.append("EFP live roadmap snapshot drift")
    if roadmap.get("basis_commit") != "516cff5d6a45af54d6fc4ae9c72c2e8e9c668637":
        errors.append("EFP live roadmap basis commit must remain merged PR #19 until PR #21 merges")
    if roadmap.get("active_planned_surface") != 10:
        errors.append("EFP live roadmap active surface must be PR #10")
    if roadmap.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]:
        errors.append("EFP live roadmap completed set drift")
    if roadmap.get("deferred") != []:
        errors.append("EFP live roadmap deferred set drift")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("EFP live roadmap sequence malformed")
    else:
        by_pr = {item.get("planned_pr"): item for item in sequence if isinstance(item, dict)}
        if by_pr.get(10, {}).get("status") != "active-post-merge-release-gate":
            errors.append("EFP live roadmap PR10 release-gate activation drift")
        if by_pr.get(18, {}).get("status") != "complete-merged-516cff5d6a45af54d6fc4ae9c72c2e8e9c668637":
            errors.append("EFP live roadmap PR18 completion drift")
    if roadmap != EXPECTED_LIVE_ROADMAP:
        errors.append("EFP live roadmap canonical payload drift")
    serialized = json.dumps(roadmap, sort_keys=True).casefold()
    for token in _base._frozen.PRIVATE_PATTERNS:
        if token.casefold() in serialized:
            errors.append(f"EFP live roadmap contains forbidden private locator: {token}")
    return errors


def validate() -> dict[str, object]:
    # Preserve existing adversarial mutation hooks across the compatibility
    # boundary. Tests intentionally replace the public load_module function to
    # prove runtime projection/fixture drift is detected.
    old_roadmap = _base._live_roadmap_errors
    old_loader = _base.load_module
    try:
        _base._live_roadmap_errors = _live_roadmap_errors
        _base.load_module = globals()["load_module"]
        return _base.validate()
    finally:
        _base._live_roadmap_errors = old_roadmap
        _base.load_module = old_loader


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print("Empirical Falsification Profile authority: ok")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
