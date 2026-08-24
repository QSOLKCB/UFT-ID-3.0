#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID Information Comparability authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/information_comparability_contract.json",
    "results": ROOT / "machine/information_comparability_results.json",
    "human": ROOT / "theory/INFORMATION_COMPARABILITY.md",
    "roadmap": ROOT / "machine/roadmap_state.json",
    "base_contract": ROOT / "machine/contract.json",
    "claims": ROOT / "docs/CLAIMS.md",
    "readme": ROOT / "README4AI.md",
    "repro": ROOT / "docs/REPRODUCIBILITY.md",
    "experiment": ROOT / "experiments/information_comparability/run.py",
    "tests": ROOT / "tests/test_information_comparability.py",
    "receipt": ROOT / "experiments/run_information_comparability.py",
    "artifact_verifier": ROOT / "scripts/verify_information_comparability_artifacts.py",
    "information_primitives": ROOT / "experiments/lib/information.py",
    "observation_base": ROOT / "machine/observation_contract.json",
    "representation_base": ROOT / "machine/representation_contract.json",
}

EXPECTED_SCOPE = (
    "Finite information-quantity specification comparability. The contract distinguishes direct comparability "
    "from explicit unit-converted comparability and forbids scalar coincidence, shared vocabulary, or shared "
    "units from silently substituting for functional, observation, convention, scope, semantic, epistemic, "
    "empirical, or physical equivalence."
)
EXPECTED_PRIMARY_TYPE = "InformationSpec=(source_type,functional,observation,unit,normalization,conditioning,scope)"
EXPECTED_CONVERSION_TYPE = "UnitConversion=(functional,source_unit,target_unit,positive_scale,scope)"
EXPECTED_SPEC_FIELDS = {
    "source_type": "declared source/carrier type on which the information quantity is defined",
    "functional": "exact information functional identity; shared use of the word information is insufficient",
    "observation": "exact observation/measurement contract presented to the functional",
    "unit": "declared scalar unit or logarithm-base convention",
    "normalization": "declared normalization convention",
    "conditioning": "declared conditioning convention",
    "scope": "nonempty contexts/regimes in which the specification is licensed",
}
EXPECTED_MODES = {
    "direct": "source_type, functional, observation, unit, normalization, and conditioning are equal and scopes overlap",
    "unit_converted": "all direct-comparability fields except unit are equal, scopes overlap, and an exact registered positive unit conversion matches the functional and unit direction",
    "not_authorized": "numeric equality, matching codomain, matching unit, matching functional name, or shared use of the word information alone",
}
EXPECTED_UNIT_REGISTRY = {
    "bit->base4-digit": "scale=1/2 for logarithmic functionals",
    "base4-digit->bit": "scale=2 for logarithmic functionals",
}
EXPECTED_FUNCTIONALS = {
    "shannon_entropy": "finite Shannon entropy under the declared observation and logarithm-base/unit convention",
    "hartley_entropy": "finite Hartley support entropy under the declared observation and logarithm-base/unit convention",
}
EXPECTED_BOUNDARIES = [
    "SAME_WORD_INFORMATION != SAME_FUNCTIONAL",
    "SAME_SCALAR_CODOMAIN != COMPARABLE_INFORMATION",
    "SAME_UNIT != COMPARABLE_INFORMATION",
    "SAME_FUNCTIONAL != SAME_OBSERVATION",
    "IDENTICAL_SPEC => COMPARABLE",
    "COMPARABLE != IDENTICAL_SPEC",
    "NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE",
    "POSITIVE_UNIT_CONVERSION != SEMANTIC_BRIDGE",
    "PAIRWISE_SCOPE_COMPARABILITY != TRANSITIVE_COMPARABILITY",
    "DIRECT_COMPARABILITY != EMPIRICAL_COMMENSURABILITY",
    "FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY",
]
EXPECTED_LIMITS = {
    "functional_count": 2,
    "observation_count": 2,
    "unit_count": 2,
    "normalization_count": 2,
    "conditioning_count": 2,
    "scope_count": 3,
    "information_spec_count": 96,
    "ordered_spec_pair_count": 9216,
    "directly_comparable_ordered_pairs": 224,
    "unit_convertible_ordered_pairs": 224,
    "positive_scale_order_checks": 75,
    "log_base_conversion_checks": 5,
    "policy": "The bounded battery is exact conformance evidence for the declared finite specification grammar and bit/base4 conversion registry only; it is not a universal theorem that arbitrary quantities called information are comparable.",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/INFORMATION_COMPARABILITY.md",
    "results": "machine/information_comparability_results.json",
    "validator": "scripts/validate_information_comparability.py",
    "experiment": "experiments/information_comparability/run.py",
    "tests": "tests/test_information_comparability.py",
    "receipt": "experiments/run_information_comparability.py",
    "artifact_verifier": "scripts/verify_information_comparability_artifacts.py",
    "roadmap_state": "machine/roadmap_state.json",
    "information_primitives": "experiments/lib/information.py",
    "observation_base": "machine/observation_contract.json",
    "representation_base": "machine/representation_contract.json",
}
EXPECTED_DEFERRALS = [
    "mutual-information comparability across unmatched joint models",
    "KL-divergence comparability across unmatched reference measures",
    "stochastic channel comparability to planned PR #17",
    "semantic equivalence between different observation contracts without an explicit bridge",
    "empirical commensurability and calibration validity to planned PR #18",
    "infinite-alphabet information measures",
    "Lean proof objects",
]
EXPECTED_EVIDENCE = ["experiments/information_comparability/run.py", "tests/test_information_comparability.py"]
EXPECTED_RESULT_BOUNDARY = (
    "SAME_WORD_INFORMATION != SAME_FUNCTIONAL; NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE; "
    "COMPARABLE != IDENTICAL_SPEC; FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY"
)
EXPECTED_THEOREMS = {
    "UFT-INF-001": {
        "name": "Identical valid specifications are directly comparable",
        "statement": "Every valid InformationSpec is directly comparable with itself because all comparison-defining fields agree and its scope is nonempty.",
        "hypotheses": ["A is a valid InformationSpec"],
        "proof_reference": "theory/INFORMATION_COMPARABILITY.md#uft-inf-001-identical-valid-specifications-are-directly-comparable",
        "nonclaims": ["Reflexive direct comparability does not make two independently specified quantities identical merely because their scalar values agree."],
    },
    "UFT-INF-002": {
        "name": "Direct comparability is symmetric",
        "statement": "For valid InformationSpec values A and B, if A is directly comparable with B then B is directly comparable with A.",
        "hypotheses": ["A and B are valid InformationSpec values", "A and B satisfy the direct-comparability predicate"],
        "proof_reference": "theory/INFORMATION_COMPARABILITY.md#uft-inf-002-direct-comparability-is-symmetric",
        "nonclaims": ["Scope-relative direct comparability is not asserted to be transitive."],
    },
    "UFT-INF-003": {
        "name": "Direct comparability preserves the comparison-defining specification",
        "statement": "If two InformationSpec values are directly comparable, then source_type, functional, observation, unit, normalization, and conditioning agree exactly and their scopes have nonempty intersection.",
        "hypotheses": ["A and B are valid InformationSpec values", "A and B are directly comparable"],
        "proof_reference": "theory/INFORMATION_COMPARABILITY.md#uft-inf-003-direct-comparability-preserves-the-comparison-defining-specification",
        "nonclaims": ["Matching one or several fields, including functional or unit alone, is not enough for direct comparability."],
    },
    "UFT-INF-004": {
        "name": "Positive unit conversion preserves scalar order",
        "statement": "For real scalar values x and y and a positive conversion scale a, equality and strict order are preserved by x -> ax and the sign of y-x equals the sign of a(y-x).",
        "hypotheses": ["x and y are real scalars", "a>0"],
        "proof_reference": "theory/INFORMATION_COMPARABILITY.md#uft-inf-004-positive-unit-conversion-preserves-scalar-order",
        "nonclaims": ["A positive scalar conversion changes units only; it does not supply a semantic, epistemic, empirical, or physical bridge."],
    },
    "UFT-INF-005": {
        "name": "Explicit logarithm-base conversion gives non-identical comparable specifications",
        "statement": "For Shannon or Hartley logarithmic entropy specifications that agree in every comparison-defining field except bit versus base4-digit unit, an explicit registered scale of 1/2 from bits to base4-digits or 2 in the reverse direction licenses unit-converted comparability; the specifications remain non-identical.",
        "hypotheses": ["A and B are valid InformationSpec values", "A and B differ only by bit versus base4-digit unit and scope may differ only with nonempty overlap", "the registered unit conversion matches the functional and direction"],
        "proof_reference": "theory/INFORMATION_COMPARABILITY.md#uft-inf-005-explicit-logarithm-base-conversion-gives-non-identical-comparable-specifications",
        "nonclaims": ["Unit-converted comparability does not authorize comparison across different observations, normalizations, conditionings, functionals, or disjoint scopes."],
    },
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-INF-001": {
        "name": "Same word and unit can hide different information functionals",
        "statement": "A Shannon-entropy specification and a Hartley-entropy specification can both be measured in bits and even return the same scalar on a uniform two-state distribution while remaining not directly comparable because their functional identities differ.",
        "fixture": "uniform-two-state Shannon bits versus Hartley bits",
        "nonclaims": ["The example does not say Shannon and Hartley quantities can never be related under a separately declared theorem or bridge."],
    },
    "CX-INF-002": {
        "name": "Same functional and unit can use different observations",
        "statement": "Two Shannon-entropy specifications in bits with different observation contracts are not directly comparable under the Information Comparability predicate.",
        "fixture": "Shannon bits with fine observation versus coarse observation",
        "nonclaims": ["A separately proved observation bridge may establish a narrower relationship; direct comparability does not assume one."],
    },
    "CX-INF-003": {
        "name": "Different units require an explicit conversion",
        "statement": "Two otherwise matching logarithmic entropy specifications in bits and base4-digits are not directly comparable, although an explicit registered unit conversion can make them unit-converted comparable.",
        "fixture": "matching Shannon specification in bits versus base4-digits",
        "nonclaims": ["The availability of a unit conversion does not make the two specifications textually or semantically identical."],
    },
    "CX-INF-004": {
        "name": "Scope-overlap comparability need not be transitive",
        "statement": "With otherwise identical specifications, scope A={alpha}, B={alpha,beta}, and C={beta} gives A directly comparable with B and B directly comparable with C while A is not directly comparable with C.",
        "fixture": "three identical semantic specs with overlapping-chain scopes",
        "nonclaims": ["The counterexample concerns the scope-relative direct-comparability relation only; it does not refute transitivity of equality or of separately defined equivalence relations."],
    },
    "CX-INF-005": {
        "name": "Numeric equality does not erase normalization differences",
        "statement": "Two information quantities can both have scalar value 1 while their specifications use different normalization conventions, so numeric equality alone does not establish direct comparability or informational equivalence.",
        "fixture": "equal scalar 1 under normalization none versus per-source-symbol",
        "nonclaims": ["Equal numbers remain equal as numbers; the counterexample rejects only the promotion from numeric equality to specification-level comparability or equivalence."],
    },
}
EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/INFORMATION_COMPARABILITY.md",
    "machine_contract": "machine/information_comparability_contract.json",
    "machine_results": "machine/information_comparability_results.json",
    "validator": "scripts/validate_information_comparability.py",
    "experiment": "experiments/information_comparability/run.py",
    "tests": "tests/test_information_comparability.py",
    "receipt_runner": "experiments/run_information_comparability.py",
    "receipt_version": "1.0.0",
    "artifact_verifier": "scripts/verify_information_comparability_artifacts.py",
    "roadmap_state": "machine/roadmap_state.json",
    "information_primitives": "experiments/lib/information.py",
    "observation_base": "machine/observation_contract.json",
    "representation_base": "machine/representation_contract.json",
    "rule": "Information quantities are comparable only under an explicit specification relation: shared vocabulary, scalar codomain, unit, functional name, or numeric equality alone never authorizes functional, observational, semantic, epistemic, empirical, or physical equivalence.",
}
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "same number proves same information",
    "same unit proves comparable information",
    "unit conversion proves same physics",
    "information comparability proves truth",
    "shared information word proves same functional",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def safe_path(path: object, label: str, errors: list[str]) -> None:
    if not isinstance(path, str) or not path:
        errors.append(f"{label} must be a nonempty repository-relative path")
        return
    rel = Path(path)
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
        errors.append(f"{label} missing: {path}")


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


def validate() -> dict[str, object]:
    errors: list[str] = []
    for name, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing Information Comparability authority file: {name}={path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    roadmap = load_json(PATHS["roadmap"])
    base = load_json(PATHS["base_contract"])
    human = PATHS["human"].read_text(encoding="utf-8")
    claims = PATHS["claims"].read_text(encoding="utf-8")
    readme = PATHS["readme"].read_text(encoding="utf-8")
    repro = PATHS["repro"].read_text(encoding="utf-8")

    if contract.get("type") != "uft-id-information-comparability-contract": errors.append("information contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("information contract schema drift")
    if contract.get("snapshot_date") != "2026-08-24": errors.append("information contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("information contract claim class drift")
    if contract.get("scope") != EXPECTED_SCOPE: errors.append("information contract scope drift")
    if contract.get("primary_type") != EXPECTED_PRIMARY_TYPE: errors.append("information primary type drift")
    if contract.get("conversion_type") != EXPECTED_CONVERSION_TYPE: errors.append("information conversion type drift")
    if contract.get("spec_fields") != EXPECTED_SPEC_FIELDS: errors.append("information spec field registry drift")
    if contract.get("comparability_modes") != EXPECTED_MODES: errors.append("information comparability mode registry drift")
    if contract.get("unit_conversion_registry") != EXPECTED_UNIT_REGISTRY: errors.append("information unit conversion registry drift")
    if contract.get("functional_registry") != EXPECTED_FUNCTIONALS: errors.append("information functional registry drift")
    if contract.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("information hard-boundary registry drift")
    if contract.get("execution_limits") != EXPECTED_LIMITS: errors.append("information execution limits drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES: errors.append("information authority registry drift")
    else:
        for key, value in EXPECTED_AUTHORITIES.items():
            if key != "roadmap_state":
                safe_path(value, f"information authority {key}", errors)
    if contract.get("explicit_deferrals") != EXPECTED_DEFERRALS: errors.append("information explicit deferrals drift")

    records = results.get("records")
    if not isinstance(records, list):
        errors.append("information result registry malformed")
        records = []
    by_id: dict[str, dict[str, Any]] = {}
    ids: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            errors.append(f"information result {index} malformed")
            continue
        rid = str(record["id"])
        if rid in by_id:
            errors.append(f"duplicate information result id: {rid}")
        else:
            by_id[rid] = record
        ids.append(rid)
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(ids) != expected_ids or len(ids) != len(expected_ids):
        errors.append("information result identity set drift")

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
        raw_h = strip_code(metadata(sec, "Canonical hypotheses"))
        try:
            parsed_h = json.loads(raw_h) if raw_h is not None else None
        except json.JSONDecodeError:
            parsed_h = None
        if parsed_h != expected["hypotheses"]: errors.append(f"{rid} human canonical hypotheses drift")

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

    if results.get("type") != "uft-id-information-comparability-result-registry": errors.append("information result type drift")
    if results.get("schema_version") != "1.0.0": errors.append("information result schema drift")
    if results.get("snapshot_date") != "2026-08-24": errors.append("information result snapshot drift")
    if results.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("information result claim boundary drift")

    if roadmap.get("schema_version") != "1.3.0": errors.append("information roadmap schema drift")
    if roadmap.get("basis_commit") != "a094ec469f311bc6cc11442ee5f850f5dc130e2f": errors.append("information roadmap basis commit drift")
    if roadmap.get("active_planned_surface") != 15: errors.append("information roadmap active surface must be PR #15")
    completed = roadmap.get("completed")
    if not isinstance(completed, list) or 14 not in completed: errors.append("information roadmap must mark planned PR #14 complete")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("information roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(14, {}).get("status") != "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f": errors.append("planned PR #14 completion state drift")
        if by_pr.get(15, {}).get("status") != "active-implemented-in-current-change": errors.append("planned PR #15 active state drift")
        if by_pr.get(16, {}).get("status") != "planned": errors.append("planned PR #16 must remain planned")
    rules = roadmap.get("rules")
    required_rule = "No information comparison is licensed by shared vocabulary, scalar codomain, unit, functional name, or numeric equality alone; comparison requires the declared InformationSpec relation or an explicit registered conversion."
    if not isinstance(rules, list) or required_rule not in rules:
        errors.append("information roadmap comparability hard rule missing")

    if base.get("information_comparability_authority") != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central Information Comparability authority registration drift")
    library = base.get("experiment_library")
    if not isinstance(library, dict) or library.get("information_comparability_receipt_runner") != "experiments/run_information_comparability.py" or library.get("information_comparability_receipt_version") != "1.0.0":
        errors.append("central Information Comparability receipt registry drift")
    hard_rules = base.get("hard_rules")
    expected_hard_rules = {
        "same_information_word_implies_same_functional": False,
        "numeric_equality_implies_information_equivalence": False,
        "same_unit_implies_information_comparability": False,
        "unit_conversion_implies_semantic_bridge": False,
    }
    if not isinstance(hard_rules, dict) or any(hard_rules.get(k) is not v for k, v in expected_hard_rules.items()):
        errors.append("central Information Comparability hard-rule registration drift")
    reads = base.get("required_agent_reads")
    required_reads = {
        "theory/INFORMATION_COMPARABILITY.md",
        "machine/information_comparability_contract.json",
        "machine/information_comparability_results.json",
        "scripts/validate_information_comparability.py",
        "experiments/run_information_comparability.py",
    }
    if not isinstance(reads, list) or not required_reads.issubset(set(reads)):
        errors.append("central Information Comparability agent-read registration drift")

    for text, anchors, label in (
        (claims, ("### C11 - Information comparability is specification-relative", "SAME_WORD_INFORMATION != SAME_FUNCTIONAL", "NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE"), "claims"),
        (readme, ("## Information comparability authority", "machine/information_comparability_contract.json", "COMPARABLE != IDENTICAL_SPEC"), "README4AI"),
        (repro, ("## Information-comparability conformance boundary", "information-comparability-validation.json", "python scripts/validate_information_comparability.py"), "reproducibility"),
    ):
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"{label} missing Information Comparability anchor: {anchor}")

    combined = "\n".join((json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False), human, claims, readme, repro))
    lower = combined.casefold()
    for token in PRIVATE_PATTERNS:
        if token in lower: errors.append(f"information authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in lower: errors.append(f"information authority contains forbidden promotion: {phrase}")

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
        print(f"Information Comparability authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
