#!/usr/bin/env python3
"""Live compatibility wrapper for the merged Information Comparability validator.

The exact validator merged in GitHub PR #16 is preserved in
validate_information_comparability_pr16_frozen.py. This wrapper replays that
authority against its historical PR15-active roadmap snapshot, then validates
the current Empirical Falsification Profile schedule independently. Information
theorem, counterexample, contract, and evidence semantics remain frozen.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_information_comparability_pr16_frozen.py"

_spec = importlib.util.spec_from_file_location("information_comparability_validator_pr16_frozen", FROZEN)
if _spec is None or _spec.loader is None: raise RuntimeError(f"cannot load frozen Information Comparability validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_frozen)
for _name in dir(_frozen):
    if not _name.startswith("__") and _name not in {"validate", "main", "load_json"}: globals()[_name] = getattr(_frozen, _name)

HISTORICAL_ROADMAP_STATE = {
    "type":"uft-id-roadmap-state","schema_version":"1.3.0","snapshot_date":"2026-08-24","basis_commit":"a094ec469f311bc6cc11442ee5f850f5dc130e2f",
    "completed":[5,6,7,8,9,11,12,13,14],"active_planned_surface":15,"deferred":[10],
    "sequence":[
        {"planned_pr":9,"surface":"deterministic-observation-calculus","status":"complete"},
        {"planned_pr":10,"surface":"lean-observation-foundation","status":"deferred-independent-formal-proof-track"},
        {"planned_pr":11,"surface":"relation-first-recovery-core-plus-graph-realization-interlude","status":"complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"},
        {"planned_pr":12,"surface":"bridge-core","status":"complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"},
        {"planned_pr":13,"surface":"epistemic-bridge-specialization","status":"complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"},
        {"planned_pr":14,"surface":"representation-and-congruence-calculus","status":"complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f"},
        {"planned_pr":15,"surface":"information-comparability-core","status":"active-implemented-in-current-change"},
        {"planned_pr":16,"surface":"recovery-specializations","status":"planned"},
        {"planned_pr":17,"surface":"continuum-stochastic-prevalence-obligations","status":"planned"},
        {"planned_pr":18,"surface":"empirical-falsification-profile","status":"planned"}],
    "compatibility_note":"machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, Epistemic Bridge, and Representation validators retain their own historical schedule snapshots. This file is the live post-Representation schedule authority.",
    "fixture_policy":"Minimal fixtures travel with the theorem or counterexample that requires them.",
    "rules":["NO_GIANT_FORMALIZATION_PR","NO_STANDALONE_FINITE_FIXTURE_ZOO","Lean deferral does not prevent repository-contained mathematical proofs, finite conformance witnesses, or later theorem targets from being frozen.","A unique-selection claim requires an actual discriminating theorem or uniqueness proof, not compatibility or one successful construction.","No semantic lifting is licensed without an explicit typed bridge declaring preserved structure, lost structure, scope, and version compatibility.","Structural transport, retrieval, inference, execution, storage, or replay cannot create verification authority without an explicit epistemic operation and receipt.","Conflict and unknown remain separately represented; verified and conflict may coexist.","Every representation invariant must name the transformation class and hypotheses under which it is preserved.","Similarity, congruence, coordinate change, and receiver re-encoding remain separately typed and cannot imply semantic or physical identity by name alone.","No information comparison is licensed by shared vocabulary, scalar codomain, unit, functional name, or numeric equality alone; comparison requires the declared InformationSpec relation or an explicit registered conversion."]}

_original_load_json = _frozen.load_json

def _historical_load_json(path: Path):
    if path.resolve() == _frozen.PATHS["roadmap"].resolve(): return json.loads(json.dumps(HISTORICAL_ROADMAP_STATE))
    return _original_load_json(path)

def _live_roadmap_errors() -> list[str]:
    errors=[]; roadmap=_original_load_json(_frozen.PATHS["roadmap"])
    if roadmap.get("schema_version") != "1.6.0": errors.append("information live roadmap schema drift")
    if roadmap.get("basis_commit") != "353e55a11a8cb6d6bcf571110e0fd6f32823fc77": errors.append("information live roadmap basis commit must be merged CSP PR")
    if roadmap.get("active_planned_surface") != 18:
        errors.extend(["information live roadmap active surface must be PR #18","information live roadmap active surface must be PR #17","information live roadmap active surface must be PR #16","information roadmap active surface must be PR #15"])
    if roadmap.get("completed") != [5,6,7,8,9,11,12,13,14,15,16,17]: errors.append("information live roadmap completed set drift")
    if roadmap.get("deferred") != [10]: errors.append("information live roadmap deferred set drift")
    sequence=roadmap.get("sequence")
    if not isinstance(sequence,list): errors.append("information live roadmap sequence malformed")
    else:
        by_pr={x.get("planned_pr"):x for x in sequence if isinstance(x,dict)}
        if by_pr.get(15,{}).get("status") != "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813": errors.append("information live roadmap PR15 completion drift")
        if by_pr.get(16,{}).get("status") != "complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f": errors.append("information live roadmap PR16 completion drift")
        if by_pr.get(17,{}).get("status") != "complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77": errors.append("information live roadmap PR17 completion drift")
        if by_pr.get(18,{}).get("status") != "active-implemented-in-current-change": errors.append("information live roadmap PR18 active-state drift")
    rules=roadmap.get("rules"); efp_rule="Empirical rejection requires complete calibrated profile-matched evidence and remains scoped to one hypothesis/profile version; formal counterexamples, synthetic fixtures, non-rejection, or model fit cannot be promoted into empirical falsification, confirmation, or unique explanation by default."
    if not isinstance(rules,list) or efp_rule not in rules: errors.append("information live roadmap empirical falsification rule missing")
    serialized=json.dumps(roadmap,sort_keys=True).casefold()
    for token in _frozen.PRIVATE_PATTERNS:
        if token.casefold() in serialized: errors.append(f"information live roadmap contains forbidden private locator: {token}")
    return errors

def validate() -> dict[str,object]:
    old_loader=_frozen.load_json
    try:
        _frozen.load_json=_historical_load_json; result=_frozen.validate()
    finally: _frozen.load_json=old_loader
    errors=list(result.get("errors",[])); errors.extend(_live_roadmap_errors()); result["errors"]=errors; result["status"]="error" if errors else "ok"; return result

def main() -> int:
    parser=__import__("argparse").ArgumentParser(); parser.add_argument("--json",action="store_true"); args=parser.parse_args(); result=validate()
    if args.json: print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
    elif result["status"]=="ok": print(f"Information Comparability authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]: print(error)
    return 0 if result["status"]=="ok" else 1
if __name__=="__main__": raise SystemExit(main())
