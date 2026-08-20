#!/usr/bin/env python3
"""Fail-closed validation for the PR #9 deterministic observation authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/observation_contract.json",
    "specs": ROOT / "machine/observation_specs.json",
    "theorems": ROOT / "machine/observation_theorems.json",
    "counterexamples": ROOT / "machine/observation_counterexamples.json",
    "formalization_contract": ROOT / "machine/formalization_contract.json",
    "human": ROOT / "theory/OBSERVATION_CALCULUS.md",
    "experiment": ROOT / "experiments/observation/run.py",
    "tests": ROOT / "tests/test_pr9_observation.py",
    "receipt": ROOT / "experiments/run_pr9.py",
    "roadmap": ROOT / "ROADMAP.md",
    "base_contract": ROOT / "machine/contract.json",
}

EXPECTED_AUTHORITIES = {
    "specs": "machine/observation_specs.json",
    "theorems": "machine/observation_theorems.json",
    "counterexamples": "machine/observation_counterexamples.json",
    "formalization_contract": "machine/formalization_contract.json",
    "human": "theory/OBSERVATION_CALCULUS.md",
    "experiment": "experiments/observation/run.py",
    "validator": "scripts/validate_observation_specs.py",
    "tests": "tests/test_pr9_observation.py",
    "receipt": "experiments/run_pr9.py",
    "roadmap": "ROADMAP.md",
}

EXPECTED_HARD_RULES = {
    "observation_equivalence_implies_physical_identity",
    "noninjective_observation_has_global_exact_left_inverse",
    "quotient_equals_full_codomain_without_surjectivity",
    "generic_observation_kernel_implies_linear_kernel",
    "successful_reconstruction_implies_physical_state_survival",
    "derived_observation_property_may_be_declared_without_evidence",
    "stochastic_kernel_may_enter_pr9",
    "lean_proof_may_be_claimed_in_pr9",
}

EXPECTED_SPEC_FIELDS = [
    "id", "name", "source_type", "target_type", "kind", "domain",
    "map_ref", "scope", "claim_class", "nonclaims",
]
EXPECTED_SPEC_IDS = {"OBS-SPEC-001", "OBS-SPEC-002", "OBS-SPEC-003"}
EXPECTED_THEOREM_IDS = {f"UFT-OBS-{i:03d}" for i in range(1, 6)}
EXPECTED_CX_IDS = {f"CX-OBS-{i:03d}" for i in range(1, 4)}
EXPECTED_THEOREM_STATEMENTS = {
    "UFT-OBS-001": "For any function O:S->Y, define x~_O y iff O(x)=O(y). Then ~_O is an equivalence relation on S, and the equivalence class of x equals the fibre O^{-1}({O(x)}).",
    "UFT-OBS-002": "For any function O:S->Y, the quotient S/~_O is canonically bijective with im(O), via [x] |-> O(x).",
    "UFT-OBS-003": "For any function O:S->Y, O is injective iff there exists R:im(O)->S such that R(O(x))=x for every x in S.",
    "UFT-OBS-004": "If O:S->Y is noninjective, no function R:Y->S can satisfy R(O(x))=x for every x in S.",
    "UFT-OBS-005": "For positive integers L,R and f(i)=floor(iL/R) on i=0,...,R-1: if R<L then f is injective and not surjective; if R=L then f is the identity and bijective; if R>L then f is surjective and not injective. For j=0,...,L-1, |f^{-1}(j)|=ceil((j+1)R/L)-ceil(jR/L).",
}
EXPECTED_THEOREM_HYPOTHESES = {
    "UFT-OBS-001": ["O is a total deterministic function S->Y"],
    "UFT-OBS-002": ["O is a total deterministic function S->Y"],
    "UFT-OBS-003": ["O is a total deterministic function S->Y", "Reconstruction is scoped to im(O)"],
    "UFT-OBS-004": ["O is a total deterministic function S->Y", "O is noninjective"],
    "UFT-OBS-005": ["L and R are positive integers", "i ranges over {0,...,R-1}", "j ranges over {0,...,L-1}"],
}
EXPECTED_ROADMAP_SEQUENCE = [
    {"planned_pr": 9, "surface": "deterministic-observation-calculus"},
    {"planned_pr": 10, "surface": "lean-observation-foundation"},
    {"planned_pr": 11, "surface": "relation-first-recovery-core"},
    {"planned_pr": 12, "surface": "bridge-core"},
    {"planned_pr": 13, "surface": "epistemic-bridge-specialization"},
    {"planned_pr": 14, "surface": "representation-and-congruence-calculus"},
    {"planned_pr": 15, "surface": "information-comparability-core"},
    {"planned_pr": 16, "surface": "recovery-specializations"},
    {"planned_pr": 17, "surface": "continuum-stochastic-prevalence-obligations"},
    {"planned_pr": 18, "surface": "empirical-falsification-profile"},
]
EXPECTED_ROADMAP_REBASE = {
    "authority": "ROADMAP.md",
    "basis": "Post-PR8 four-pass mathematical audit and hostile verification",
    "active_pr": 9,
    "legacy_deferred_surfaces_semantics": "The deferred_surfaces array above is the PR8-era planning baseline retained for PR8 validator and receipt compatibility; it is not the current scheduling authority.",
    "current_sequence": EXPECTED_ROADMAP_SEQUENCE,
    "dropped_standalone_surface": "finite-reference-model-battery",
    "fixture_policy": "Minimal fixtures travel with the theorem or counterexample that requires them.",
}
PRIVATE_LOCATOR_TOKENS = (
    "/mnt/data/", "file_000", "file-secret", "gmail:", "gdrive:",
    "drive.google.com", "docs.google.com", "private-user-images.githubusercontent.com",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object, label: str, errors: list[str], *, required: bool = False) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    if required and not value:
        errors.append(f"{label} must be non-empty")
    result: list[str] = []
    for i, item in enumerate(value):
        if not nonempty(item):
            errors.append(f"{label}[{i}] must be a non-empty string")
        else:
            result.append(str(item))
    if len(result) != len(set(result)):
        errors.append(f"{label} must not contain duplicates")
    return result


def repo_file(value: object, label: str, errors: list[str]) -> None:
    if not nonempty(value):
        errors.append(f"{label} must be a non-empty repository-relative path")
        return
    rel = Path(str(value))
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} must remain repository-relative")
        return
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository")
        return
    if not path.is_file():
        errors.append(f"{label} does not exist: {value}")


def no_private_locators(value: object, label: str, errors: list[str]) -> None:
    serialized = json.dumps(value, sort_keys=True).casefold()
    for token in PRIVATE_LOCATOR_TOKENS:
        if token.casefold() in serialized:
            errors.append(f"{label} contains forbidden private locator token: {token}")


def theorem_section(human: str, rid: str) -> str:
    marker = f"## {rid} "
    start = human.find(marker)
    if start < 0:
        return ""
    next_heading = human.find("\n## ", start + len(marker))
    if next_heading < 0:
        return human[start:]
    return human[start:next_heading]


def canonical_human_line(section: str, label: str) -> str | None:
    prefix = f"**{label}:** `"
    for line in section.splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line[len(prefix):-1]
    return None


def validate_documents(
    contract: dict[str, Any],
    specs: dict[str, Any],
    theorems: dict[str, Any],
    counterexamples: dict[str, Any],
    base_contract: dict[str, Any],
    formalization_contract: dict[str, Any],
    human: str,
    roadmap: str,
    *,
    check_paths: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []

    if contract.get("type") != "uft-id-observation-contract":
        errors.append("observation contract type mismatch")
    if contract.get("schema_version") != "1.0.1":
        errors.append("observation contract schema mismatch")
    if contract.get("claim_class") != "DEFINITION":
        errors.append("observation contract must have canonical claim class DEFINITION")
    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("observation authorities must match canonical mapping exactly")
    elif check_paths:
        for key, rel in EXPECTED_AUTHORITIES.items():
            repo_file(rel, f"authority.{key}", errors)

    hard = contract.get("hard_rules")
    if not isinstance(hard, dict) or set(hard) != EXPECTED_HARD_RULES:
        errors.append("observation hard_rules must contain the exact expected key set")
    elif any(value is not False for value in hard.values()):
        errors.append("all observation hard_rules must remain false")

    kinds = set(string_list(contract.get("allowed_observation_kinds"), "allowed_observation_kinds", errors, required=True))
    if kinds != {"deterministic-total"}:
        errors.append("PR9 permits deterministic-total observations only")

    derived = set(string_list(
        contract.get("derived_not_stored_as_independent_authority"),
        "derived_not_stored_as_independent_authority", errors, required=True,
    ))
    if derived != {"fibres", "image", "observational-equivalence", "injectivity", "surjectivity", "quotient"}:
        errors.append("derived observation property set drift")

    claim_classes = set(base_contract.get("claim_classes", []))
    if not claim_classes:
        errors.append("base project claim_classes missing")

    if formalization_contract.get("type") != "uft-id-formalization-contract":
        errors.append("formalization contract type mismatch")
    if formalization_contract.get("schema_version") != "1.0.2":
        errors.append("formalization contract schema mismatch for PR9 roadmap rebase")
    if formalization_contract.get("roadmap_rebase") != EXPECTED_ROADMAP_REBASE:
        errors.append("formalization roadmap_rebase must match the exact post-audit schedule authority")

    if specs.get("type") != "uft-id-observation-spec-registry" or specs.get("schema_version") != "1.0.0":
        errors.append("observation spec registry shape mismatch")
    generic = specs.get("generic_form")
    if not isinstance(generic, dict) or generic.get("fields") != EXPECTED_SPEC_FIELDS:
        errors.append("ObservationSpec fields must match the exact canonical field list")

    spec_ids: set[str] = set()
    records = specs.get("records")
    if not isinstance(records, list):
        errors.append("observation specs records must be a list")
        records = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"observation spec {i} must be an object")
            continue
        if set(record) != set(EXPECTED_SPEC_FIELDS):
            errors.append(f"observation spec {record.get('id', i)} must use exact canonical fields")
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"observation spec {i} missing id")
            continue
        rid = str(rid)
        if rid in spec_ids:
            errors.append(f"duplicate observation spec id {rid}")
        spec_ids.add(rid)
        for field in ("name", "source_type", "target_type", "domain", "map_ref", "scope"):
            if not nonempty(record.get(field)):
                errors.append(f"{rid}.{field} required")
        if record.get("kind") not in kinds:
            errors.append(f"{rid}.kind unsupported in PR9")
        if record.get("claim_class") != "DEFINITION":
            errors.append(f"{rid}.claim_class must be DEFINITION")
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)
    if spec_ids != EXPECTED_SPEC_IDS:
        errors.append("observation spec IDs must match canonical set exactly")

    theorem_ids: set[str] = set()
    theorem_records = theorems.get("records")
    if theorems.get("type") != "uft-id-observation-theorem-registry" or theorems.get("schema_version") != "1.0.0":
        errors.append("observation theorem registry shape mismatch")
    if not isinstance(theorem_records, list):
        errors.append("observation theorem records must be a list")
        theorem_records = []
    required_theorem_fields = {
        "id", "name", "claim_class", "statement", "hypotheses",
        "proof_reference", "executable_evidence", "nonclaims",
    }
    for i, record in enumerate(theorem_records):
        if not isinstance(record, dict):
            errors.append(f"observation theorem {i} must be an object")
            continue
        if set(record) != required_theorem_fields:
            errors.append(f"observation theorem {record.get('id', i)} must use exact canonical fields")
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"observation theorem {i} missing id")
            continue
        rid = str(rid)
        if rid in theorem_ids:
            errors.append(f"duplicate observation theorem id {rid}")
        theorem_ids.add(rid)
        if record.get("claim_class") != "PROVED" or record.get("claim_class") not in claim_classes:
            errors.append(f"{rid} must retain claim class PROVED")
        if record.get("statement") != EXPECTED_THEOREM_STATEMENTS.get(rid):
            errors.append(f"{rid} theorem statement drift")
        hypotheses = string_list(record.get("hypotheses"), f"{rid}.hypotheses", errors, required=True)
        if hypotheses != EXPECTED_THEOREM_HYPOTHESES.get(rid):
            errors.append(f"{rid} theorem hypotheses drift")
        if not nonempty(record.get("proof_reference")):
            errors.append(f"{rid}.proof_reference required")
        evidence = string_list(record.get("executable_evidence"), f"{rid}.executable_evidence", errors, required=True)
        if check_paths:
            for rel in evidence:
                repo_file(rel, f"{rid}.executable_evidence", errors)
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)

        section = theorem_section(human, rid)
        if not section:
            errors.append(f"human theorem section missing for {rid}")
        else:
            human_statement = canonical_human_line(section, "Canonical statement")
            human_hypotheses_raw = canonical_human_line(section, "Canonical hypotheses")
            if human_statement != EXPECTED_THEOREM_STATEMENTS.get(rid):
                errors.append(f"{rid} human canonical statement drift")
            try:
                human_hypotheses = json.loads(human_hypotheses_raw) if human_hypotheses_raw is not None else None
            except json.JSONDecodeError:
                human_hypotheses = None
            if human_hypotheses != EXPECTED_THEOREM_HYPOTHESES.get(rid):
                errors.append(f"{rid} human canonical hypotheses drift")
    if theorem_ids != EXPECTED_THEOREM_IDS:
        errors.append("observation theorem IDs must match UFT-OBS-001 through UFT-OBS-005 exactly")

    cx_ids: set[str] = set()
    cx_records = counterexamples.get("records")
    if counterexamples.get("type") != "uft-id-observation-counterexample-registry" or counterexamples.get("schema_version") != "1.0.0":
        errors.append("observation counterexample registry shape mismatch")
    if not isinstance(cx_records, list):
        errors.append("observation counterexample records must be a list")
        cx_records = []
    required_cx_fields = {"id", "name", "claim_class", "fixture", "kills", "witness", "evidence", "nonclaims"}
    for i, record in enumerate(cx_records):
        if not isinstance(record, dict):
            errors.append(f"counterexample {i} must be an object")
            continue
        if set(record) != required_cx_fields:
            errors.append(f"counterexample {record.get('id', i)} must use exact canonical fields")
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"counterexample {i} missing id")
            continue
        rid = str(rid)
        if rid in cx_ids:
            errors.append(f"duplicate counterexample id {rid}")
        cx_ids.add(rid)
        if record.get("claim_class") != "COUNTEREXAMPLE":
            errors.append(f"{rid}.claim_class must be COUNTEREXAMPLE")
        for field in ("name", "fixture", "witness"):
            if not nonempty(record.get(field)):
                errors.append(f"{rid}.{field} required")
        string_list(record.get("kills"), f"{rid}.kills", errors, required=True)
        evidence = string_list(record.get("evidence"), f"{rid}.evidence", errors, required=True)
        if check_paths:
            for rel in evidence:
                repo_file(rel, f"{rid}.evidence", errors)
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)
    if cx_ids != EXPECTED_CX_IDS:
        errors.append("observation counterexample IDs must match canonical set exactly")

    no_private_locators(contract, "observation contract", errors)
    no_private_locators(specs, "observation specs", errors)
    no_private_locators(theorems, "observation theorems", errors)
    no_private_locators(counterexamples, "observation counterexamples", errors)

    human_anchors = [
        "OBSERVATIONAL_EQUIVALENCE != PHYSICAL_IDENTITY",
        "LINEAR_KERNEL_REQUIRES_LINEAR_STRUCTURE",
        "UFT-OBS-001 Observational equivalence",
        "UFT-OBS-002 Quotient-to-image correspondence",
        "UFT-OBS-003 Image-scoped exact reconstruction",
        "UFT-OBS-004 Noninjective observation blocks global exact reconstruction",
        "UFT-OBS-005 Uniform floor sampling",
        "MATHEMATICALLY_LEAN_READY != REPOSITORY_LEAN_PROVED",
    ]
    for anchor in human_anchors:
        if anchor not in human:
            errors.append(f"observation human authority missing semantic anchor: {anchor}")

    roadmap_anchors = [
        "PR #9 — Deterministic observation calculus",
        "PR #10 — Lean observation foundation",
        "PR #11 — Relation-first recovery core",
        "PR #12 — BridgeCore",
        "PR #13 — Epistemic bridge specialization",
        "PR #14 — Representation and congruence calculus",
        "PR #15 — Information comparability core",
        "PR #16 — Recovery specializations",
        "PR #17 — Continuum, stochastic, and prevalence obligations",
        "PR #18 — Empirical falsification profile",
        "NO_STANDALONE_FINITE_FIXTURE_ZOO",
        "GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY",
    ]
    for anchor in roadmap_anchors:
        if anchor not in roadmap:
            errors.append(f"roadmap missing post-audit anchor: {anchor}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "spec_count": len(spec_ids),
        "theorem_count": len(theorem_ids),
        "counterexample_count": len(cx_ids),
    }


def validate() -> dict[str, Any]:
    missing = [str(path.relative_to(ROOT)) for path in PATHS.values() if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing observation authority file: {path}" for path in missing],
            "spec_count": 0,
            "theorem_count": 0,
            "counterexample_count": 0,
        }
    return validate_documents(
        load(PATHS["contract"]),
        load(PATHS["specs"]),
        load(PATHS["theorems"]),
        load(PATHS["counterexamples"]),
        load(PATHS["base_contract"]),
        load(PATHS["formalization_contract"]),
        PATHS["human"].read_text(encoding="utf-8"),
        PATHS["roadmap"].read_text(encoding="utf-8"),
        check_paths=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PR9 observation contracts:", result["status"])
        for error in result["errors"]:
            print(" -", error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
