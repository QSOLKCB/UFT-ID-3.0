#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID Representation and Congruence authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/representation_contract.json",
    "results": ROOT / "machine/representation_results.json",
    "human": ROOT / "theory/REPRESENTATION_CALCULUS.md",
    "roadmap": ROOT / "machine/roadmap_state.json",
    "base_contract": ROOT / "machine/contract.json",
    "claims": ROOT / "docs/CLAIMS.md",
    "readme": ROOT / "README4AI.md",
    "repro": ROOT / "docs/REPRODUCIBILITY.md",
    "experiment": ROOT / "experiments/representation_calculus/run.py",
    "tests": ROOT / "tests/test_representation_calculus.py",
    "receipt": ROOT / "experiments/run_representation_calculus.py",
    "artifact_verifier": ROOT / "scripts/verify_representation_artifacts.py",
    "observation_base": ROOT / "machine/observation_contract.json",
    "bridge_base": ROOT / "machine/bridge_core_contract.json",
    "epistemic_base": ROOT / "machine/epistemic_bridge_contract.json",
}

EXPECTED_SCOPE = (
    "Finite-dimensional linear representation changes and finite receiver re-encodings. The contract distinguishes "
    "similarity, orthogonal/unitary similarity, congruence, coordinate change, and receiver transformation without "
    "promoting representation equivalence into semantic, epistemic, empirical, or physical identity."
)
EXPECTED_PRIMARY_TYPE = (
    "RepresentationSpec=(object_type,source_representation,target_representation,transform_class,transform,"
    "inverse_or_adjoint,scope,declared_invariants)"
)
EXPECTED_TRANSFORM_CLASSES = {
    "similarity": "B=P^{-1} A P with P invertible",
    "orthogonal_similarity_real": "B=Q^T A Q with Q^T Q=I",
    "unitary_similarity_complex": "B=U^* A U with U^* U=I",
    "congruence_real": "B=P^T A P with P invertible",
    "coordinate_change": "v'=P^{-1}v and A'=P^{-1}AP for one abstract vector/operator pair",
    "receiver_reencoding": "O'=R o O on the observation codomain; equivalence preservation requires R injective on im(O)",
}
EXPECTED_INVARIANT_DISCIPLINE = {
    "rule": "Every invariant claim names the transformation class and hypotheses under which it is preserved.",
    "similarity": ["characteristic polynomial", "trace", "determinant", "rank"],
    "orthogonal_or_unitary_similarity": ["all similarity invariants", "Frobenius norm"],
    "congruence": ["rank", "symmetry/Hermitian type when applicable"],
    "coordinate_change": ["abstract action relation A(v) represented covariantly"],
    "injective_receiver_reencoding": ["observation equivalence classes/fibres"],
}
EXPECTED_BOUNDARIES = [
    "SIMILARITY != CONGRUENCE",
    "SIMILARITY != ORTHOGONAL_OR_UNITARY_SIMILARITY",
    "SAME_CHARACTERISTIC_POLYNOMIAL != SIMILARITY",
    "CONGRUENCE != SPECTRAL_EQUIVALENCE",
    "COORDINATE_TUPLE != ABSTRACT_OBJECT",
    "REPRESENTATION_CHANGE != PHYSICAL_CHANGE",
    "RECEIVER_REENCODING != STATE_TRANSFORMATION",
    "NONINJECTIVE_RECEIVER_REENCODING != OBSERVATIONAL_EQUIVALENCE_PRESERVATION",
    "INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE",
    "FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF",
]
EXPECTED_LIMITS = {
    "matrix_dimension": 2,
    "matrix_entry_alphabet": [-1, 0, 1],
    "matrix_count": 81,
    "unimodular_transform_count": 40,
    "orthogonal_transform_count": 8,
    "similarity_checks": 3240,
    "congruence_rank_checks": 3240,
    "orthogonal_frobenius_checks": 648,
    "coordinate_covariance_checks": 29160,
    "fin3_function_count": 27,
    "receiver_function_pairs": 729,
    "injective_on_image_receiver_pairs": 441,
    "receiver_equivalence_pair_checks": 3969,
    "policy": "The finite battery is exact conformance evidence for the declared 2x2/Fin3 fixtures only; it is not a substitute for the repository-contained general proofs.",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/REPRESENTATION_CALCULUS.md",
    "results": "machine/representation_results.json",
    "validator": "scripts/validate_representation_calculus.py",
    "experiment": "experiments/representation_calculus/run.py",
    "tests": "tests/test_representation_calculus.py",
    "receipt": "experiments/run_representation_calculus.py",
    "artifact_verifier": "scripts/verify_representation_artifacts.py",
    "roadmap_state": "machine/roadmap_state.json",
    "observation_base": "machine/observation_contract.json",
    "bridge_base": "machine/bridge_core_contract.json",
    "epistemic_base": "machine/epistemic_bridge_contract.json",
}
EXPECTED_DEFERRALS = [
    "canonical forms beyond the bounded counterexamples",
    "Sylvester inertia theorem as an advertised UFT-ID theorem",
    "infinite-dimensional operator equivalence",
    "stochastic receiver kernels",
    "information-functional comparability to planned PR #15",
    "empirical coordinate/receiver validity to planned PR #18",
    "Lean proof objects",
]
EXPECTED_EVIDENCE = ["experiments/representation_calculus/run.py", "tests/test_representation_calculus.py"]

EXPECTED_THEOREMS = {
    "UFT-REP-001": {
        "name": "Similarity preserves characteristic polynomial",
        "statement": "If B=P^{-1}AP for an invertible finite-dimensional change of basis P over R or C, then A and B have the same characteristic polynomial; therefore trace, determinant, and rank are preserved.",
        "hypotheses": ["A and B are square matrices over R or C", "P is invertible", "B=P^{-1}AP"],
        "proof_reference": "theory/REPRESENTATION_CALCULUS.md#uft-rep-001-similarity-preserves-characteristic-polynomial",
        "nonclaims": ["Sharing a characteristic polynomial does not imply similarity in general."],
    },
    "UFT-REP-002": {
        "name": "Orthogonal or unitary similarity preserves Frobenius norm",
        "statement": "Orthogonal similarity over R and unitary similarity over C are similarity transformations and additionally preserve the Frobenius norm.",
        "hypotheses": ["B=Q^T A Q with Q^TQ=I over R, or B=U^* A U with U^*U=I over C"],
        "proof_reference": "theory/REPRESENTATION_CALCULUS.md#uft-rep-002-orthogonal-or-unitary-similarity-preserves-frobenius-norm",
        "nonclaims": ["Ordinary similarity need not preserve the Frobenius norm."],
    },
    "UFT-REP-003": {
        "name": "Invertible congruence preserves rank",
        "statement": "If B=P^TAP over R with P invertible, then rank(B)=rank(A); if A is symmetric then B is symmetric. Congruence does not generally preserve eigenvalues.",
        "hypotheses": ["A is a real square matrix", "P is invertible", "B=P^TAP"],
        "proof_reference": "theory/REPRESENTATION_CALCULUS.md#uft-rep-003-invertible-congruence-preserves-rank",
        "nonclaims": ["Congruence is not spectral equivalence and is not interchangeable with similarity."],
    },
    "UFT-REP-004": {
        "name": "Coordinate change preserves abstract linear action",
        "statement": "For v'=P^{-1}v and A'=P^{-1}AP with P invertible, A'v'=P^{-1}(Av); the coordinate representation changes while the represented linear action is covariant.",
        "hypotheses": ["P is invertible", "v'=P^{-1}v", "A'=P^{-1}AP"],
        "proof_reference": "theory/REPRESENTATION_CALCULUS.md#uft-rep-004-coordinate-change-preserves-abstract-linear-action",
        "nonclaims": ["Coordinate covariance does not establish physical equivalence of independently modelled systems."],
    },
    "UFT-REP-005": {
        "name": "Injective receiver re-encoding preserves observation equivalence",
        "statement": "For a deterministic observation O:S->Y and receiver map R:Y->Z that is injective on im(O), R(O(x))=R(O(y)) iff O(x)=O(y); hence the observation fibres are unchanged.",
        "hypotheses": ["O:S->Y is deterministic", "R:Y->Z is injective on im(O)"],
        "proof_reference": "theory/REPRESENTATION_CALCULUS.md#uft-rep-005-injective-receiver-re-encoding-preserves-observation-equivalence",
        "nonclaims": ["A noninjective receiver map may merge observation classes and therefore changes the observation equivalence relation."],
    },
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-REP-001": {
        "name": "Congruent need not be similar",
        "statement": "I2 and diag(4,1) are congruent via P=diag(2,1) but are not similar because their traces and characteristic polynomials differ.",
        "fixture": "I2 --congruence by diag(2,1)--> diag(4,1)",
        "nonclaims": ["The counterexample distinguishes equivalence notions only; it makes no physical claim."],
    },
    "CX-REP-002": {
        "name": "Similar need not be orthogonally similar",
        "statement": "diag(1,2) is similar via a shear to [[1,-1],[0,2]], but their Frobenius norms differ, so they cannot be orthogonally similar.",
        "fixture": "diag(1,2) with P=[[1,1],[0,1]]",
        "nonclaims": ["Failure of orthogonal similarity does not refute ordinary similarity."],
    },
    "CX-REP-003": {
        "name": "Same characteristic polynomial need not imply similarity",
        "statement": "I2 and the nontrivial Jordan block [[1,1],[0,1]] have the same characteristic polynomial but are not similar because rank(A-I) differs.",
        "fixture": "I2 versus J2(1)",
        "nonclaims": ["Characteristic-polynomial equality is a necessary similarity invariant, not a complete classifier."],
    },
    "CX-REP-004": {
        "name": "Noninjective receiver re-encoding can merge fibres",
        "statement": "An observation distinguishing x0 and x1 can become indistinguishable after a receiver map sends both observation values to one output.",
        "fixture": "O(x0)=0,O(x1)=1 with R(0)=R(1)=z",
        "nonclaims": ["Receiver-induced merging is representation loss, not evidence of physical state merging."],
    },
    "CX-REP-005": {
        "name": "Coordinate tuple alone does not identify an abstract vector",
        "statement": "The coordinate tuple (1,0) denotes different abstract vectors in the standard basis and in the swapped basis; the chart/basis is part of the representation.",
        "fixture": "(1,0) in (e1,e2) versus (1,0) in (e2,e1)",
        "nonclaims": ["This is a coordinate-identity counterexample, not a claim that abstract vectors lack identity."],
    },
}
EXPECTED_RESULT_BOUNDARY = (
    "SIMILARITY != CONGRUENCE; COORDINATE_TUPLE != ABSTRACT_OBJECT; "
    "RECEIVER_REENCODING != STATE_TRANSFORMATION; FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF"
)
EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/REPRESENTATION_CALCULUS.md",
    "machine_contract": "machine/representation_contract.json",
    "machine_results": "machine/representation_results.json",
    "validator": "scripts/validate_representation_calculus.py",
    "experiment": "experiments/representation_calculus/run.py",
    "tests": "tests/test_representation_calculus.py",
    "receipt_runner": "experiments/run_representation_calculus.py",
    "receipt_version": "1.0.0",
    "artifact_verifier": "scripts/verify_representation_artifacts.py",
    "roadmap_state": "machine/roadmap_state.json",
    "rule": "Representation equivalence is transformation-class-relative: similarity, orthogonal/unitary similarity, congruence, coordinate change, and receiver re-encoding preserve only their declared invariants and never imply semantic, epistemic, empirical, or physical identity by themselves.",
}

PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "similarity proves physical identity",
    "congruence proves same physics",
    "coordinate change proves ontology",
    "receiver merging proves state identity",
    "representation equivalence proves truth",
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
            errors.append(f"missing Representation authority file: {name}={path.relative_to(ROOT)}")
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

    if contract.get("type") != "uft-id-representation-contract": errors.append("representation contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("representation contract schema drift")
    if contract.get("snapshot_date") != "2026-08-24": errors.append("representation contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("representation contract claim class drift")
    if contract.get("scope") != EXPECTED_SCOPE: errors.append("representation contract scope drift")
    if contract.get("primary_type") != EXPECTED_PRIMARY_TYPE: errors.append("representation primary type drift")
    if contract.get("transform_classes") != EXPECTED_TRANSFORM_CLASSES: errors.append("representation transform-class registry drift")
    if contract.get("invariant_discipline") != EXPECTED_INVARIANT_DISCIPLINE: errors.append("representation invariant discipline drift")
    if contract.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("representation hard-boundary registry drift")
    if contract.get("execution_limits") != EXPECTED_LIMITS: errors.append("representation execution limits drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES: errors.append("representation authority registry drift")
    else:
        for key, value in EXPECTED_AUTHORITIES.items():
            if key != "roadmap_state":
                safe_path(value, f"representation authority {key}", errors)
    if contract.get("explicit_deferrals") != EXPECTED_DEFERRALS: errors.append("representation explicit deferrals drift")

    records = results.get("records")
    if not isinstance(records, list):
        errors.append("representation result registry malformed")
        records = []
    ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            errors.append(f"representation result {index} malformed")
            continue
        rid = str(record["id"])
        if rid in by_id:
            errors.append(f"duplicate representation result id {rid}")
        else:
            by_id[rid] = record
        ids.append(rid)
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(ids) != expected_ids or len(ids) != len(expected_ids):
        errors.append("representation result identity set drift")

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
        heading = f"## {rid} {expected['name']}"
        sec = section(human, heading)
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
        heading = f"### {rid} {expected['name']}"
        sec = section(human, heading)
        if sec is None:
            errors.append(f"{rid} human counterexample section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`COUNTEREXAMPLE`": errors.append(f"{rid} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != expected["statement"]: errors.append(f"{rid} human canonical statement drift")

    if results.get("type") != "uft-id-representation-result-registry": errors.append("representation result type drift")
    if results.get("schema_version") != "1.0.0": errors.append("representation result schema drift")
    if results.get("snapshot_date") != "2026-08-24": errors.append("representation result snapshot drift")
    if results.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("representation result claim boundary drift")

    if roadmap.get("basis_commit") != "083aa9ae9e812cae86302d856f70ad83e5cf806b": errors.append("representation roadmap basis commit drift")
    if roadmap.get("active_planned_surface") != 14: errors.append("representation roadmap active surface must be PR #14")
    completed = roadmap.get("completed")
    if not isinstance(completed, list) or 13 not in completed: errors.append("representation roadmap must mark planned PR #13 complete")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("representation roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(13, {}).get("status") != "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b": errors.append("planned PR #13 completion state drift")
        if by_pr.get(14, {}).get("status") != "active-implemented-in-current-change": errors.append("planned PR #14 active state drift")
        if by_pr.get(15, {}).get("status") != "planned": errors.append("planned PR #15 must remain planned")

    if base.get("representation_authority") != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central Representation authority registration drift")
    library = base.get("experiment_library")
    if not isinstance(library, dict) or library.get("representation_receipt_runner") != "experiments/run_representation_calculus.py" or library.get("representation_receipt_version") != "1.0.0":
        errors.append("central Representation receipt registry drift")
    reads = base.get("required_agent_reads")
    required_reads = {
        "theory/REPRESENTATION_CALCULUS.md", "machine/representation_contract.json",
        "machine/representation_results.json", "scripts/validate_representation_calculus.py",
        "experiments/run_representation_calculus.py",
    }
    if not isinstance(reads, list) or not required_reads.issubset(set(reads)):
        errors.append("central Representation agent-read registration drift")

    for text, anchors, label in (
        (claims, ("### C10 - Representation invariants are transformation-class-relative", "SIMILARITY != CONGRUENCE", "COORDINATE_TUPLE != ABSTRACT_OBJECT"), "claims"),
        (readme, ("## Representation and congruence authority", "machine/representation_contract.json", "INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE"), "README4AI"),
        (repro, ("## Representation-calculus conformance boundary", "representation-validation.json", "python scripts/validate_representation_calculus.py"), "reproducibility"),
    ):
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"{label} missing Representation anchor: {anchor}")

    combined = "\n".join((json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False), human, claims, readme, repro))
    lower = combined.casefold()
    for token in PRIVATE_PATTERNS:
        if token in lower: errors.append(f"representation authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in lower: errors.append(f"representation authority contains forbidden promotion: {phrase}")

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
        print(f"Representation authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
