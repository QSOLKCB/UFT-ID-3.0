#!/usr/bin/env python3
"""Live compatibility wrapper for the merged PR #19 Empirical Falsification Profile authority.

The exact EFP validator merged in GitHub PR #19 is preserved in
validate_empirical_falsification_profile_pr19_frozen.py. This wrapper replays
that authority against its historical PR18-active roadmap state, then
independently validates the post-EFP schedule where PR #18 is complete and
PR #10 is active only for first-theorem-batch/dependency-graph freezing.
EFP theorem, counterexample, evidence, receipt, and decision semantics remain
frozen.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_empirical_falsification_profile_pr19_frozen.py"
ROADMAP_STATE = ROOT / "machine/roadmap_state.json"

_spec = importlib.util.spec_from_file_location("efp_validator_pr19_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen EFP validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

for _name in dir(_frozen):
    if not _name.startswith("__") and _name not in {"validate", "main"}:
        globals()[_name] = getattr(_frozen, _name)

HISTORICAL_ROADMAP_STATE = {'type': 'uft-id-roadmap-state',
 'schema_version': '1.6.0',
 'snapshot_date': '2026-08-24',
 'basis_commit': '353e55a11a8cb6d6bcf571110e0fd6f32823fc77',
 'completed': [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17],
 'active_planned_surface': 18,
 'deferred': [10],
 'sequence': [{'planned_pr': 9, 'surface': 'deterministic-observation-calculus', 'status': 'complete'},
              {'planned_pr': 10,
               'surface': 'lean-observation-foundation',
               'status': 'deferred-independent-formal-proof-track'},
              {'planned_pr': 11,
               'surface': 'relation-first-recovery-core-plus-graph-realization-interlude',
               'status': 'complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b'},
              {'planned_pr': 12,
               'surface': 'bridge-core',
               'status': 'complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7'},
              {'planned_pr': 13,
               'surface': 'epistemic-bridge-specialization',
               'status': 'complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b'},
              {'planned_pr': 14,
               'surface': 'representation-and-congruence-calculus',
               'status': 'complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f'},
              {'planned_pr': 15,
               'surface': 'information-comparability-core',
               'status': 'complete-merged-22b589c4e2e2042d180d64db837f092a007e0813'},
              {'planned_pr': 16,
               'surface': 'recovery-specializations',
               'status': 'complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f'},
              {'planned_pr': 17,
               'surface': 'continuum-stochastic-prevalence-obligations',
               'status': 'complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77'},
              {'planned_pr': 18,
               'surface': 'empirical-falsification-profile',
               'status': 'active-implemented-in-current-change'}],
 'compatibility_note': 'machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, '
                       'BridgeCore, Epistemic Bridge, Representation, Information Comparability, Recovery, and CSP '
                       'theorem authorities retain their historical semantics. This file is the live post-CSP schedule '
                       'authority.',
 'fixture_policy': 'Minimal fixtures travel with the theorem or counterexample that requires them.',
 'rules': ['NO_GIANT_FORMALIZATION_PR',
           'NO_STANDALONE_FINITE_FIXTURE_ZOO',
           'Lean deferral does not prevent repository-contained mathematical proofs, finite conformance witnesses, or '
           'later theorem targets from being frozen.',
           'A unique-selection claim requires an actual discriminating theorem or uniqueness proof, not compatibility '
           'or one successful construction.',
           'No semantic lifting is licensed without an explicit typed bridge declaring preserved structure, lost '
           'structure, scope, and version compatibility.',
           'Structural transport, retrieval, inference, execution, storage, or replay cannot create verification '
           'authority without an explicit epistemic operation and receipt.',
           'Conflict and unknown remain separately represented; verified and conflict may coexist.',
           'Every representation invariant must name the transformation class and hypotheses under which it is '
           'preserved.',
           'Similarity, congruence, coordinate change, and receiver re-encoding remain separately typed and cannot '
           'imply semantic or physical identity by name alone.',
           'No information comparison is licensed by shared vocabulary, scalar codomain, unit, functional name, or '
           'numeric equality alone; comparison requires the declared InformationSpec relation or an explicit '
           'registered conversion.',
           'A deterministic recovery selector is a specialization of the generic relation only when its non-fixed '
           'steps are relation-sound; executable normalization additionally requires explicit termination/progress and '
           'fixed-point/normal-state obligations.',
           'Stochastic, prevalence, infinite-horizon, and continuum claims require separately declared '
           'probability/measure and lifting obligations; finite reachability, finite samples, counterexamples, or grid '
           'conformance cannot supply them by default.',
           'Empirical rejection requires complete calibrated profile-matched evidence and remains scoped to one '
           'hypothesis/profile version; formal counterexamples, synthetic fixtures, non-rejection, or model fit cannot '
           'be promoted into empirical falsification, confirmation, or unique explanation by default.']}
EXPECTED_LIVE_ROADMAP = {'type': 'uft-id-roadmap-state',
 'schema_version': '1.7.0',
 'snapshot_date': '2026-08-24',
 'basis_commit': '516cff5d6a45af54d6fc4ae9c72c2e8e9c668637',
 'completed': [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18],
 'active_planned_surface': 10,
 'deferred': [],
 'sequence': [{'planned_pr': 9, 'surface': 'deterministic-observation-calculus', 'status': 'complete'},
              {'planned_pr': 10,
               'surface': 'lean-observation-foundation',
               'status': 'active-first-theorem-batch-freeze'},
              {'planned_pr': 11,
               'surface': 'relation-first-recovery-core-plus-graph-realization-interlude',
               'status': 'complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b'},
              {'planned_pr': 12,
               'surface': 'bridge-core',
               'status': 'complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7'},
              {'planned_pr': 13,
               'surface': 'epistemic-bridge-specialization',
               'status': 'complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b'},
              {'planned_pr': 14,
               'surface': 'representation-and-congruence-calculus',
               'status': 'complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f'},
              {'planned_pr': 15,
               'surface': 'information-comparability-core',
               'status': 'complete-merged-22b589c4e2e2042d180d64db837f092a007e0813'},
              {'planned_pr': 16,
               'surface': 'recovery-specializations',
               'status': 'complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f'},
              {'planned_pr': 17,
               'surface': 'continuum-stochastic-prevalence-obligations',
               'status': 'complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77'},
              {'planned_pr': 18,
               'surface': 'empirical-falsification-profile',
               'status': 'complete-merged-516cff5d6a45af54d6fc4ae9c72c2e8e9c668637'}],
 'compatibility_note': 'machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, '
                       'BridgeCore, Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, and '
                       'EFP theorem authorities retain their historical semantics. This file is the live post-EFP '
                       'schedule authority with PR #10 activated for first-theorem-batch freezing.',
 'fixture_policy': 'Minimal fixtures travel with the theorem or counterexample that requires them.',
 'rules': ['NO_GIANT_FORMALIZATION_PR',
           'NO_STANDALONE_FINITE_FIXTURE_ZOO',
           'Lean activation begins with theorem-batch and dependency-graph freezing; mathematical proof, Lean proof, '
           'runtime conformance, and empirical validation remain separately typed authorities.',
           'A unique-selection claim requires an actual discriminating theorem or uniqueness proof, not compatibility '
           'or one successful construction.',
           'No semantic lifting is licensed without an explicit typed bridge declaring preserved structure, lost '
           'structure, scope, and version compatibility.',
           'Structural transport, retrieval, inference, execution, storage, or replay cannot create verification '
           'authority without an explicit epistemic operation and receipt.',
           'Conflict and unknown remain separately represented; verified and conflict may coexist.',
           'Every representation invariant must name the transformation class and hypotheses under which it is '
           'preserved.',
           'Similarity, congruence, coordinate change, and receiver re-encoding remain separately typed and cannot '
           'imply semantic or physical identity by name alone.',
           'No information comparison is licensed by shared vocabulary, scalar codomain, unit, functional name, or '
           'numeric equality alone; comparison requires the declared InformationSpec relation or an explicit '
           'registered conversion.',
           'A deterministic recovery selector is a specialization of the generic relation only when its non-fixed '
           'steps are relation-sound; executable normalization additionally requires explicit termination/progress and '
           'fixed-point/normal-state obligations.',
           'Stochastic, prevalence, infinite-horizon, and continuum claims require separately declared '
           'probability/measure and lifting obligations; finite reachability, finite samples, counterexamples, or grid '
           'conformance cannot supply them by default.',
           'Empirical rejection requires complete calibrated profile-matched evidence and remains scoped to one '
           'hypothesis/profile version; formal counterexamples, synthetic fixtures, non-rejection, or model fit cannot '
           'be promoted into empirical falsification, confirmation, or unique explanation by default.']}

_original_load_json = _frozen.load_json
_original_load_module = _frozen.load_module

def _historical_load_json(path: Path):
    if path.resolve() == _frozen.PATHS["roadmap_state"].resolve():
        return copy.deepcopy(HISTORICAL_ROADMAP_STATE)
    return _original_load_json(path)

def _live_roadmap_errors() -> list[str]:
    errors: list[str] = []
    roadmap = _original_load_json(ROADMAP_STATE)
    if roadmap.get("schema_version") != "1.7.0": errors.append("EFP live roadmap schema drift")
    if roadmap.get("snapshot_date") != "2026-08-24": errors.append("EFP contract/result/roadmap snapshot disagreement")
    if roadmap.get("basis_commit") != "516cff5d6a45af54d6fc4ae9c72c2e8e9c668637": errors.append("EFP live roadmap basis commit must be merged PR #19")
    if roadmap.get("active_planned_surface") != 10: errors.append("EFP live roadmap active surface must be PR #10")
    if roadmap.get("completed") != [5,6,7,8,9,11,12,13,14,15,16,17,18]: errors.append("EFP live roadmap completed set drift")
    if roadmap.get("deferred") != []: errors.append("EFP live roadmap deferred set drift")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("EFP live roadmap sequence malformed")
    else:
        by_pr = {item.get("planned_pr"): item for item in sequence if isinstance(item, dict)}
        if by_pr.get(10, {}).get("status") != "active-first-theorem-batch-freeze": errors.append("EFP live roadmap PR10 activation drift")
        if by_pr.get(18, {}).get("status") != "complete-merged-516cff5d6a45af54d6fc4ae9c72c2e8e9c668637": errors.append("EFP live roadmap PR18 completion drift")
    if roadmap != EXPECTED_LIVE_ROADMAP: errors.append("EFP live roadmap canonical payload drift")
    serialized = json.dumps(roadmap, sort_keys=True).casefold()
    for token in _frozen.PRIVATE_PATTERNS:
        if token.casefold() in serialized: errors.append(f"EFP live roadmap contains forbidden private locator: {token}")
    return errors

def validate() -> dict[str, object]:
    old_json = _frozen.load_json
    old_module = _frozen.load_module
    try:
        _frozen.load_json = _historical_load_json
        _frozen.load_module = globals().get("load_module", _original_load_module)
        result = _frozen.validate()
    finally:
        _frozen.load_json = old_json
        _frozen.load_module = old_module
    errors = list(result.get("errors", []))
    errors.extend(_live_roadmap_errors())
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result

def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Empirical Falsification Profile authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]: print(error)
    return 0 if result["status"] == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
