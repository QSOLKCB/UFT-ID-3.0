#!/usr/bin/env python3
"""Fail-closed validation for UFT-ID Recovery Specializations."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/recovery_specialization_contract.json",
    "results": ROOT / "machine/recovery_specialization_results.json",
    "human": ROOT / "theory/RECOVERY_SPECIALIZATIONS.md",
    "base_relation": ROOT / "machine/relation_contract.json",
    "roadmap_state": ROOT / "machine/roadmap_state.json",
    "roadmap": ROOT / "ROADMAP.md",
    "experiment": ROOT / "experiments/recovery_specializations/run.py",
    "tests": ROOT / "tests/test_recovery_specializations.py",
    "receipt": ROOT / "experiments/run_recovery_specializations.py",
    "artifact_verifier": ROOT / "scripts/verify_recovery_specialization_artifacts.py",
    "workflow": ROOT / ".github/workflows/recovery-specializations.yml",
}

EXPECTED_SCOPE = (
    "Deterministic selector specializations of the existing relation-first recovery core, including "
    "relation-sound selector iteration, natural-number progress certificates, executable normalization, "
    "and finite lexicographic recovery. The specialization does not replace or strengthen the semantics "
    "of the underlying generic relation."
)
EXPECTED_PRIMARY_TYPES = {
    "selector": "sigma:X->X",
    "effective_selector_step": "Sel_sigma(x,y) iff sigma(x)=y and y!=x",
    "relation_soundness": "for all x, sigma(x)!=x implies stepRel(x,sigma(x))",
    "natural_rank": "rho:X->N with sigma(x)!=x implying rho(sigma(x))<rho(x)",
    "executable_normalizer": "normalize_sigma(x)=the first fixed point reached by deterministic selector iteration under the declared rank certificate",
    "lexicographic_selector": "finite nonempty candidate minimization by an ordered objective tuple with a final fixed total order",
}
EXPECTED_BOUNDARIES = [
    "GENERIC_RELATION != DETERMINISTIC_SELECTOR",
    "EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER",
    "DETERMINISTIC != RELATION_SOUND",
    "RELATION_SOUND != TERMINATING",
    "TERMINATING_SELECTOR != BASE_RELATION_CONFLUENT",
    "SELECTOR_NORMAL_FORM != UNIQUE_RELATION_NORMAL_FORM",
    "OBJECTIVE_MINIMUM != UNIQUE_SELECTION_WITHOUT_TIEBREAK",
    "EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY",
    "FINITE_SELECTOR_CONFORMANCE != GENERAL_RECOVERY_THEORY",
]
EXPECTED_LIMITS = {
    "carrier_sizes": [1, 2, 3],
    "total_selector_count": 32,
    "selector_relation_pair_count": 13890,
    "relation_sound_selector_pairs": 4134,
    "fixed_point_normal_exact_pairs": 739,
    "rank_decreasing_selector_count": 9,
    "state_normalization_checks": 23,
    "lexicographic_selection_checks": 336,
    "policy": "The bounded battery exhausts total selectors on Fin1, Fin2, and Fin3 and their relation-soundness against all labelled binary relations on those carriers, plus a finite lexicographic control. It is conformance evidence only and does not prove arbitrary infinite or stochastic recovery systems normalize.",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/RECOVERY_SPECIALIZATIONS.md",
    "results": "machine/recovery_specialization_results.json",
    "validator": "scripts/validate_recovery_specializations.py",
    "experiment": "experiments/recovery_specializations/run.py",
    "tests": "tests/test_recovery_specializations.py",
    "receipt": "experiments/run_recovery_specializations.py",
    "artifact_verifier": "scripts/verify_recovery_specialization_artifacts.py",
    "base_relation": "machine/relation_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "roadmap": "ROADMAP.md",
    "workflow": ".github/workflows/recovery-specializations.yml",
}
EXPECTED_DEFERRALS = [
    "infinite-path fairness and liveness",
    "stochastic selector or rewrite kernels",
    "schedule-independence for concurrent recovery",
    "history-dependent recovery semantics",
    "continuum existence and regularity obligations",
    "empirical calibration or physical recovery claims",
    "Lean proof objects",
]
EXPECTED_CONTRACT_TOP_LEVEL = {
    "type", "schema_version", "snapshot_date", "claim_class", "scope", "base_relation_authority",
    "primary_types", "hard_boundaries", "execution_limits", "authorities", "explicit_deferrals",
}
EXPECTED_RESULTS_TOP_LEVEL = {"type", "schema_version", "snapshot_date", "records", "claim_boundary"}
EXPECTED_THEOREM_FIELDS = {
    "id", "name", "claim_class", "statement", "hypotheses", "proof_reference", "executable_evidence", "nonclaims",
}
EXPECTED_COUNTEREXAMPLE_FIELDS = {"id", "name", "claim_class", "statement", "fixture", "evidence", "nonclaims"}
EXPECTED_EVIDENCE = ["experiments/recovery_specializations/run.py", "tests/test_recovery_specializations.py"]
EXPECTED_RESULT_BOUNDARY = (
    "GENERIC_RELATION != DETERMINISTIC_SELECTOR; EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER; "
    "TERMINATING_SELECTOR != BASE_RELATION_CONFLUENT; EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY"
)
EXPECTED_THEOREMS = {
    "UFT-REC-001": {
        "name": "A deterministic selector induces a right-unique effective relation",
        "statement": "For any total selector sigma:X->X, the effective selector relation Sel_sigma(x,y) iff sigma(x)=y and y!=x is right-unique.",
        "hypotheses": ["sigma:X->X is a total function"],
        "proof_reference": "theory/RECOVERY_SPECIALIZATIONS.md#uft-rec-001-a-deterministic-selector-induces-a-right-unique-effective-relation",
        "nonclaims": ["Right-uniqueness of the selector-induced relation does not make the underlying generic stepRel right-unique, terminating, or confluent."],
    },
    "UFT-REC-002": {
        "name": "Relation-sound selector iteration preserves base reachability",
        "statement": "If every non-fixed selector step sigma(u)=v is a stepRel(u,v), then every finite selector iterate sigma^k(x) is reachable from x by the reflexive-transitive closure of stepRel.",
        "hypotheses": ["sigma:X->X is total", "for all u, sigma(u)!=u implies stepRel(u,sigma(u))", "k is a natural number"],
        "proof_reference": "theory/RECOVERY_SPECIALIZATIONS.md#uft-rec-002-relation-sound-selector-iteration-preserves-base-reachability",
        "nonclaims": ["Relation-soundness does not imply that selector iteration terminates or that all branches of stepRel follow the selector."],
    },
    "UFT-REC-003": {
        "name": "Natural-rank descent terminates deterministic selector iteration",
        "statement": "If rho:X->N and every non-fixed selector step strictly decreases rho, then selector iteration from x reaches a fixed point after at most rho(x) non-fixed steps.",
        "hypotheses": ["sigma:X->X is total", "rho:X->N", "for all u, sigma(u)!=u implies rho(sigma(u))<rho(u)"],
        "proof_reference": "theory/RECOVERY_SPECIALIZATIONS.md#uft-rec-003-natural-rank-descent-terminates-deterministic-selector-iteration",
        "nonclaims": ["Termination under a declared natural-number rank does not establish confluence of the base relation or applicability to continuum and stochastic systems."],
    },
    "UFT-REC-004": {
        "name": "Sound rank-certified selectors give executable normalizers",
        "statement": "If a total selector is relation-sound, its fixed points are exactly the stepRel-normal states, and a natural-number rank strictly decreases on every non-fixed selector step, then deterministic selector iteration defines an executable normalizer that returns a reachable normal form for every input.",
        "hypotheses": ["sigma:X->X is total", "for all u, sigma(u)!=u implies stepRel(u,sigma(u))", "for all u, sigma(u)=u iff u is stepRel-normal", "rho:X->N", "for all u, sigma(u)!=u implies rho(sigma(u))<rho(u)"],
        "proof_reference": "theory/RECOVERY_SPECIALIZATIONS.md#uft-rec-004-sound-rank-certified-selectors-give-executable-normalizers",
        "nonclaims": ["The returned selector normal form need not be the unique normal form reachable under the underlying relation when that relation branches."],
    },
    "UFT-REC-005": {
        "name": "Finite lexicographic recovery is unique with a final total tie-break",
        "statement": "For a finite nonempty candidate set, lexicographic minimization of a finite ordered objective tuple followed by a fixed total candidate order returns exactly one candidate.",
        "hypotheses": ["the candidate set is finite and nonempty", "each objective is defined on every candidate", "the objective list is finite and ordered", "the final tie-break is a fixed total order containing every candidate exactly once"],
        "proof_reference": "theory/RECOVERY_SPECIALIZATIONS.md#uft-rec-005-finite-lexicographic-recovery-is-unique-with-a-final-total-tie-break",
        "nonclaims": ["A unique lexicographic selector result is a property of the declared objectives and tie-break contract, not a unique-selection theorem for the unspecialized relation or for nature."],
    },
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-REC-001": {
        "name": "Existential normalization is not an executable normalizer",
        "statement": "The terminating fork a->b and a->c has reachable normal forms b and c, so normal-form existence alone does not specify which normal form an executable recovery procedure must return.",
        "fixture": "three-state terminating fork with two distinct normals and no selector",
        "nonclaims": ["The fixture does not prevent adding a separately declared deterministic selector; it shows that the relation alone does not contain one."],
    },
    "CX-REC-002": {
        "name": "Deterministic does not imply relation-sound",
        "statement": "A total deterministic selector can map a to c even when the declared base relation contains only a->b, so determinism alone does not make selector steps licensed relation steps.",
        "fixture": "selector sigma(a)=c over base relation containing only a->b",
        "nonclaims": ["The counterexample concerns relation soundness only; an unrelated deterministic function remains a valid function."],
    },
    "CX-REC-003": {
        "name": "A relation-sound deterministic selector can loop",
        "statement": "On the two-cycle 0->1->0, the deterministic selector sigma(0)=1 and sigma(1)=0 is relation-sound but never reaches a fixed point.",
        "fixture": "two-state deterministic selector cycle",
        "nonclaims": ["The fixture does not refute termination when a valid well-founded progress certificate is supplied."],
    },
    "CX-REC-004": {
        "name": "Objective minimization without a total tie-break can remain set-valued",
        "statement": "If two finite recovery candidates have identical values for every declared objective and no final total tie-break is supplied, objective minimization leaves both candidates tied and does not define a unique selector result.",
        "fixture": "two candidates with equal objective tuples and no final total order",
        "nonclaims": ["Equal objective values are not a defect; the counterexample rejects only an undeclared promotion from a tied argmin set to a unique selector."],
    },
    "CX-REC-005": {
        "name": "A deterministic selector does not make the base relation confluent",
        "statement": "Adding a selector that chooses b on the fork a->b and a->c yields a deterministic terminating selector path to b while c remains a distinct reachable normal form of the base relation, so selector determinism does not prove base-relation confluence or unique normal form.",
        "fixture": "three-state fork with selector choosing one branch",
        "nonclaims": ["The selector specialization may intentionally choose one branch; it simply must not rewrite the semantics of the underlying relation."],
    },
}
EXPECTED_ROADMAP_SEQUENCE = [
    (9, "deterministic-observation-calculus", "complete"),
    (10, "lean-observation-foundation", "deferred-independent-formal-proof-track"),
    (11, "relation-first-recovery-core-plus-graph-realization-interlude", "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"),
    (12, "bridge-core", "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"),
    (13, "epistemic-bridge-specialization", "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"),
    (14, "representation-and-congruence-calculus", "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f"),
    (15, "information-comparability-core", "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813"),
    (16, "recovery-specializations", "active-implemented-in-current-change"),
    (17, "continuum-stochastic-prevalence-obligations", "planned"),
    (18, "empirical-falsification-profile", "planned"),
]
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "deterministic proves relation sound",
    "selector proves relation confluent",
    "normalizer proves empirical recovery",
    "existential normalization is executable",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_path(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a nonempty repository-relative path")
        return
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} escapes repository")
        return
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository")
        return
    if not resolved.is_file():
        errors.append(f"{label} missing: {value}")


def section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return None
    start = matches[0]
    match = re.match(r"^(#+)\s", heading)
    if match is None:
        return None
    level = len(match.group(1))
    out = [lines[start]]
    for line in lines[start + 1:]:
        candidate = re.match(r"^(#+)\s", line.strip())
        if candidate is not None and len(candidate.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def metadata(sec: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    values = [line.strip()[len(prefix):] for line in sec.splitlines() if line.strip().startswith(prefix)]
    return values[0] if len(values) == 1 else None


def strip_code(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def parse_json_metadata(sec: str, label: str) -> object | None:
    raw = strip_code(metadata(sec, label))
    try:
        return json.loads(raw) if raw is not None else None
    except json.JSONDecodeError:
        return None


def validate() -> dict[str, object]:
    errors: list[str] = []
    for name, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing Recovery Specializations authority file: {name}={path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    base_relation = load_json(PATHS["base_relation"])
    roadmap_state = load_json(PATHS["roadmap_state"])
    human = PATHS["human"].read_text(encoding="utf-8")
    roadmap = PATHS["roadmap"].read_text(encoding="utf-8")

    if set(contract) != EXPECTED_CONTRACT_TOP_LEVEL: errors.append("recovery contract top-level field set drift")
    if contract.get("type") != "uft-id-recovery-specialization-contract": errors.append("recovery contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("recovery contract schema drift")
    if contract.get("snapshot_date") != "2026-08-24": errors.append("recovery contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("recovery contract claim class drift")
    if contract.get("scope") != EXPECTED_SCOPE: errors.append("recovery contract scope drift")
    if contract.get("base_relation_authority") != "machine/relation_contract.json": errors.append("recovery base relation authority drift")
    if contract.get("primary_types") != EXPECTED_PRIMARY_TYPES: errors.append("recovery primary type registry drift")
    if contract.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("recovery hard-boundary registry drift")
    if contract.get("execution_limits") != EXPECTED_LIMITS: errors.append("recovery execution limits drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("recovery authority registry drift")
    else:
        for key, value in EXPECTED_AUTHORITIES.items():
            safe_path(value, f"recovery authority {key}", errors)
    if contract.get("explicit_deferrals") != EXPECTED_DEFERRALS: errors.append("recovery explicit deferrals drift")

    if base_relation.get("type") != "uft-id-relation-core-contract": errors.append("recovery base relation type drift")
    base_deferrals = base_relation.get("explicit_deferrals")
    if not isinstance(base_deferrals, list) or "deterministic selector specializations and selector iteration" not in base_deferrals:
        errors.append("frozen relation core selector-specialization deferral drift")

    if set(results) != EXPECTED_RESULTS_TOP_LEVEL: errors.append("recovery result registry top-level field set drift")
    if results.get("type") != "uft-id-recovery-specialization-result-registry": errors.append("recovery result type drift")
    if results.get("schema_version") != "1.0.0": errors.append("recovery result schema drift")
    if results.get("snapshot_date") != "2026-08-24": errors.append("recovery result snapshot drift")
    if results.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("recovery result claim boundary drift")

    records = results.get("records")
    if not isinstance(records, list):
        errors.append("recovery result registry malformed")
        records = []
    by_id: dict[str, dict[str, Any]] = {}
    ids: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            errors.append(f"recovery result {index} malformed")
            continue
        rid = str(record["id"])
        if rid in EXPECTED_THEOREMS and set(record) != EXPECTED_THEOREM_FIELDS:
            errors.append(f"{rid} theorem field set drift")
        if rid in EXPECTED_COUNTEREXAMPLES and set(record) != EXPECTED_COUNTEREXAMPLE_FIELDS:
            errors.append(f"{rid} counterexample field set drift")
        if rid in by_id:
            errors.append(f"duplicate recovery result id: {rid}")
        else:
            by_id[rid] = record
        ids.append(rid)
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(ids) != expected_ids or len(ids) != len(expected_ids): errors.append("recovery result identity set drift")

    for rid, expected in EXPECTED_THEOREMS.items():
        record = by_id.get(rid)
        if record is None:
            continue
        if record.get("name") != expected["name"]: errors.append(f"{rid} name drift")
        if record.get("claim_class") != "PROVED": errors.append(f"{rid} claim class drift")
        if record.get("statement") != expected["statement"]: errors.append(f"{rid} statement drift")
        if record.get("hypotheses") != expected["hypotheses"]: errors.append(f"{rid} hypotheses drift")
        if record.get("proof_reference") != expected["proof_reference"]: errors.append(f"{rid} proof reference drift")
        if record.get("executable_evidence") != EXPECTED_EVIDENCE: errors.append(f"{rid} executable evidence drift")
        if record.get("nonclaims") != expected["nonclaims"]: errors.append(f"{rid} nonclaims drift")
        sec = section(human, f"## {rid} {expected['name']}")
        if sec is None:
            errors.append(f"{rid} human theorem section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`PROVED`": errors.append(f"{rid} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != expected["statement"]: errors.append(f"{rid} human canonical statement drift")
        if parse_json_metadata(sec, "Canonical hypotheses") != expected["hypotheses"]: errors.append(f"{rid} human canonical hypotheses drift")
        if parse_json_metadata(sec, "Canonical nonclaims") != expected["nonclaims"]: errors.append(f"{rid} human canonical nonclaims drift")

    for rid, expected in EXPECTED_COUNTEREXAMPLES.items():
        record = by_id.get(rid)
        if record is None:
            continue
        if record.get("name") != expected["name"]: errors.append(f"{rid} name drift")
        if record.get("claim_class") != "COUNTEREXAMPLE": errors.append(f"{rid} claim class drift")
        if record.get("statement") != expected["statement"]: errors.append(f"{rid} statement drift")
        if record.get("fixture") != expected["fixture"]: errors.append(f"{rid} fixture drift")
        if record.get("evidence") != EXPECTED_EVIDENCE: errors.append(f"{rid} evidence drift")
        if record.get("nonclaims") != expected["nonclaims"]: errors.append(f"{rid} nonclaims drift")
        sec = section(human, f"### {rid} {expected['name']}")
        if sec is None:
            errors.append(f"{rid} human counterexample section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`COUNTEREXAMPLE`": errors.append(f"{rid} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != expected["statement"]: errors.append(f"{rid} human canonical statement drift")
        if parse_json_metadata(sec, "Canonical nonclaims") != expected["nonclaims"]: errors.append(f"{rid} human canonical nonclaims drift")

    if roadmap_state.get("type") != "uft-id-roadmap-state": errors.append("recovery roadmap type drift")
    if roadmap_state.get("schema_version") != "1.4.0": errors.append("recovery roadmap schema drift")
    if roadmap_state.get("snapshot_date") != "2026-08-24": errors.append("recovery roadmap snapshot drift")
    if roadmap_state.get("basis_commit") != "22b589c4e2e2042d180d64db837f092a007e0813": errors.append("recovery roadmap basis commit must be merged Information Comparability PR")
    if roadmap_state.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13, 14, 15]: errors.append("recovery roadmap completed set drift")
    if roadmap_state.get("active_planned_surface") != 16: errors.append("recovery roadmap active surface must be PR #16")
    if roadmap_state.get("deferred") != [10]: errors.append("recovery roadmap deferred set drift")
    sequence = roadmap_state.get("sequence")
    actual_sequence: list[tuple[object, object, object]] = []
    if isinstance(sequence, list):
        actual_sequence = [(item.get("planned_pr"), item.get("surface"), item.get("status")) for item in sequence if isinstance(item, dict)]
    if actual_sequence != EXPECTED_ROADMAP_SEQUENCE: errors.append("recovery roadmap sequence/status drift")
    rules = roadmap_state.get("rules")
    required_rule = "A deterministic recovery selector is a specialization of the generic relation only when its non-fixed steps are relation-sound; executable normalization additionally requires explicit termination/progress and fixed-point/normal-state obligations."
    if not isinstance(rules, list) or required_rule not in rules: errors.append("recovery roadmap specialization hard rule missing")

    roadmap_anchors = (
        "## Active now — planned PR #16",
        "### Recovery specializations",
        "python scripts/validate_recovery_specializations.py",
        "python experiments/recovery_specializations/run.py --json",
        "python experiments/run_recovery_specializations.py --json",
    )
    for anchor in roadmap_anchors:
        if anchor not in roadmap: errors.append(f"roadmap missing Recovery Specializations anchor: {anchor}")

    experiment = load_module("recovery_specialization_validator_experiment", PATHS["experiment"])
    witness = experiment.run_suite()
    if witness.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("recovery witness hard-boundary drift")
    bounded = witness.get("bounded_checks")
    expected_bounded = {
        "selector_graphs": {"carrier_count": 3, "total_selector_count": 32, "right_unique_checks": 32},
        "relation_soundness": {"selector_relation_pair_count": 13890, "relation_sound_selector_pairs": 4134, "fixed_point_normal_exact_pairs": 739},
        "rank_normalization": {"rank_decreasing_selector_count": 9, "state_normalization_checks": 23},
        "lexicographic": {"lexicographic_selection_checks": 336},
    }
    if bounded != expected_bounded: errors.append("recovery bounded witness count drift")
    fixtures = witness.get("fixtures")
    if not isinstance(fixtures, dict) or set(fixtures) != set(EXPECTED_COUNTEREXAMPLES): errors.append("recovery witness counterexample identity drift")

    combined = "\n".join((json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False), human, roadmap))
    lower = combined.casefold()
    for token in PRIVATE_PATTERNS:
        if token in lower: errors.append(f"recovery authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in lower: errors.append(f"recovery authority contains forbidden promotion: {phrase}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(by_id),
        "boundary_count": len(contract.get("hard_boundaries", [])) if isinstance(contract.get("hard_boundaries"), list) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Recovery Specializations authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
