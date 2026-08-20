#!/usr/bin/env python3
"""Fail-closed validation for the planned PR #11 relation/selection core."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/relation_contract.json",
    "theorems": ROOT / "machine/relation_theorems.json",
    "counterexamples": ROOT / "machine/relation_counterexamples.json",
    "selection": ROOT / "machine/genus_selection_specimen.json",
    "cross_repo_patterns": ROOT / "machine/cross_repo_patterns.json",
    "roadmap_state": ROOT / "machine/roadmap_state.json",
    "base_contract": ROOT / "machine/contract.json",
    "human": ROOT / "theory/RELATION_CALCULUS.md",
    "experiment": ROOT / "experiments/relation/run.py",
    "tests": ROOT / "tests/test_pr11_relation_core.py",
    "receipt": ROOT / "experiments/run_pr11.py",
    "roadmap": ROOT / "ROADMAP.md",
}

EXPECTED_AUTHORITIES = {
    "theorems": "machine/relation_theorems.json",
    "counterexamples": "machine/relation_counterexamples.json",
    "selection_specimen": "machine/genus_selection_specimen.json",
    "cross_repo_patterns": "machine/cross_repo_patterns.json",
    "human": "theory/RELATION_CALCULUS.md",
    "experiment": "experiments/relation/run.py",
    "validator": "scripts/validate_relation_core.py",
    "tests": "tests/test_pr11_relation_core.py",
    "receipt": "experiments/run_pr11.py",
    "roadmap_state": "machine/roadmap_state.json",
    "roadmap": "ROADMAP.md",
}

EXPECTED_HARD_RULES = {
    "step_relation_forces_target_admissible",
    "normal_implies_admissible",
    "admissible_implies_normal",
    "fixed_point_implies_normal",
    "confluence_implies_termination",
    "termination_implies_confluence",
    "unique_reachable_normal_implies_all_paths_normalize",
    "single_selector_result_equals_relation_semantics",
    "finite_reachability_proves_infinite_path_liveness",
    "compatibility_implies_unique_selection",
    "parameter_depends_on_label_implies_semantic_realization",
    "placement_geometry_implies_topological_genus",
    "lean_proof_may_be_claimed_in_relation_core",
}

EXPECTED_THEOREM_IDS = {"UFT-RW-001", "UFT-RW-002", "UFT-RW-003", "UFT-RW-004", "UFT-SEL-001"}
EXPECTED_CX_IDS = {"CX-RW-FORK3", "CX-RW-LOOP1", "CX-RW-EXIT2"}

EXPECTED_STATEMENTS = {
    "UFT-RW-001": "If P(x) and every stepRel-step preserves P, then every state reachable from x by reflexive-transitive closure satisfies P.",
    "UFT-RW-002": "If stepRel is right-unique, then stepRel is confluent.",
    "UFT-RW-003": "If stepRel is confluent, then from any common source x, any two reachable normal forms are equal.",
    "UFT-RW-004": "If the forward rewrite relation stepRel terminates, every state x reaches at least one normal form.",
    "UFT-SEL-001": "If x reaches normal forms n1 and n2 and a label map lambda gives lambda(n1) != lambda(n2), then x does not have at most one reachable normal form; therefore stepRel alone cannot justify a unique-selection claim over lambda.",
}

EXPECTED_HYPOTHESES = {
    "UFT-RW-001": ["stepRel:X->X->Prop", "P:X->Prop", "P(x)", "for all u,v, P(u) and stepRel(u,v) imply P(v)"],
    "UFT-RW-002": ["stepRel:X->X->Prop", "for all x,y,z, stepRel(x,y) and stepRel(x,z) imply y=z"],
    "UFT-RW-003": ["stepRel:X->X->Prop", "stepRel is confluent", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal"],
    "UFT-RW-004": ["stepRel:X->X->Prop", "forward rewriting is terminating, equivalently the swapped relation is well-founded"],
    "UFT-SEL-001": ["stepRel:X->X->Prop", "lambda:X->L", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal", "lambda(n1) != lambda(n2)"],
}

EXPECTED_PROOF_REFS = {
    "UFT-RW-001": "theory/RELATION_CALCULUS.md#uft-rw-001-branchwise-invariant-induction",
    "UFT-RW-002": "theory/RELATION_CALCULUS.md#uft-rw-002-right-unique-rewriting-is-confluent",
    "UFT-RW-003": "theory/RELATION_CALCULUS.md#uft-rw-003-confluence-gives-at-most-one-reachable-normal-form",
    "UFT-RW-004": "theory/RELATION_CALCULUS.md#uft-rw-004-termination-gives-reachable-normal-form-existence",
    "UFT-SEL-001": "theory/RELATION_CALCULUS.md#uft-sel-001-distinct-reachable-normal-labels-refute-unique-selection",
}

EXPECTED_CX = {
    "CX-RW-FORK3": {
        "states": ["a", "b", "c"],
        "edges": [["a", "b"], ["a", "c"]],
        "normal_states": ["b", "c"],
    },
    "CX-RW-LOOP1": {
        "states": ["a"],
        "edges": [["a", "a"]],
        "normal_states": [],
    },
    "CX-RW-EXIT2": {
        "states": ["a", "b"],
        "edges": [["a", "a"], ["a", "b"]],
        "normal_states": ["b"],
    },
}

EXPECTED_CONTEXT_PATTERNS = {
    "XR-P17": {
        "repository": "QSOLKCB/SONIFICATION",
        "ref": "main",
        "source_path": "docs/MATHEMATICAL_MODEL.md",
        "source_blob_sha": "0e8f986dd5ca191c1eded726dd6e276c1f856613",
        "source_status": "merged-main",
    },
    "XR-P18": {
        "repository": "QSOLKCB/SPECTRAL",
        "ref": "main",
        "source_path": "E8/APP/README.md",
        "source_blob_sha": "4855bfff69d89c4920a2b2daf59c38b875a617ec",
        "source_status": "merged-main",
    },
}

EXPECTED_SELECTION = {
    "type": "uft-id-selection-stress-test",
    "schema_version": "1.0.1",
    "snapshot_date": "2026-08-21",
    "id": "SEL-STRESS-GENUS-10-30",
    "claim_class": "DIAGNOSTIC",
    "purpose": "Instantiate UFT-SEL-001 with two labelled closed orientable surface realizations to test whether shared decorative/compatibility machinery can uniquely select genus 10.",
    "logical_fixture": {
        "source": "common-compatible-ingredient-state",
        "branches": [
            {"state": "M10", "label": {"kind": "genus", "value": 10}, "normal_in_fixture": True},
            {"state": "M30", "label": {"kind": "genus", "value": 30}, "normal_in_fixture": True},
        ],
        "relation_edges": [
            ["common-compatible-ingredient-state", "M10"],
            ["common-compatible-ingredient-state", "M30"],
        ],
        "result": "Distinct reachable normal genus labels trigger UFT-SEL-001 and refute unique selection within this declared fixture.",
    },
    "surface_constructions": {
        "M10": {
            "surface": "Sigma_10 = #_{h=1}^{10} T^2",
            "euler_characteristic": -18,
            "rank_H1_Z": 20,
            "triality_blocks_allocated": 10,
        },
        "M30": {
            "surface": "Sigma_30 = #_{h=1}^{30} T^2",
            "euler_characteristic": -58,
            "rank_H1_Z": 60,
            "triality_blocks_allocated": 30,
        },
    },
    "shared_finite_compatibility_context": {
        "available_triality_blocks": 33,
        "fixed_singlets": 2,
        "local_operator": "D3=diag(1,-2,1)",
        "phase_kick_theta": "pi/2",
        "local_cycle_identity": "F3^3=I3",
        "interpretation": "The ETQ blocks are labels/decorations assigned to handle sectors. They do not construct or prove the topology.",
    },
    "public_context_pattern_refs": [
        {"pattern_id": "XR-P17", "role": "compatibility-context-only"},
        {"pattern_id": "XR-P18", "role": "placement-context-only"},
    ],
    "placement_example": {
        "angle_rule": "vartheta_h = 2*pi*h/phi^2",
        "scope": "optional order/placement map for labelled handle sectors only",
        "boundary": "GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION",
    },
    "external_target_boundary": {
        "status": "not-assessed-by-this-record",
        "reason": "No external Genus-10 paper/package bytes or stable public source locator are committed or pinned in this repository record.",
        "rule": "The generic theorem and this internal stress test must not be reported as a verdict on a specific external package without separately sourced premises.",
    },
    "boundaries": [
        "E8_TRIALITY_COMPATIBILITY != UNIQUE_GENUS",
        "GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION",
        "DIMENSION_MATCH != STRUCTURAL_MAP != PHYSICAL_SELECTION",
        "PARAMETER != REALIZATION != INVARIANT != DISCRIMINANT != SELECTION",
        "COMPATIBLE_REALIZATION != UNIQUE_SELECTION",
        "LABELLED_HANDLE_DECORATION != TOPOLOGY_CONSTRUCTION",
        "INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION",
    ],
    "evidence": [
        "theory/RELATION_CALCULUS.md",
        "experiments/relation/run.py",
        "tests/test_pr11_relation_core.py",
    ],
}

EXPECTED_ROADMAP_SEQUENCE = [
    (9, "deterministic-observation-calculus", "complete"),
    (10, "lean-observation-foundation", "deferred-independent-formal-proof-track"),
    (11, "relation-first-recovery-core", "active-implemented-in-current-change"),
    (12, "bridge-core", "planned"),
    (13, "epistemic-bridge-specialization", "planned"),
    (14, "representation-and-congruence-calculus", "planned"),
    (15, "information-comparability-core", "planned"),
    (16, "recovery-specializations", "planned"),
    (17, "continuum-stochastic-prevalence-obligations", "planned"),
    (18, "empirical-falsification-profile", "planned"),
]

EXPECTED_HEADINGS = [
    (9, "Deterministic observation calculus"),
    (10, "Lean observation foundation"),
    (11, "Relation-first recovery core"),
    (12, "BridgeCore"),
    (13, "Epistemic bridge specialization"),
    (14, "Representation and congruence calculus"),
    (15, "Information comparability core"),
    (16, "Recovery specializations"),
    (17, "Continuum, stochastic, and prevalence obligations"),
    (18, "Empirical falsification profile"),
]

PRIVATE_TOKENS = (
    "/mnt/data/", "file_000", "gmail:", "gdrive:", "drive.google.com",
    "docs.google.com", "private-user-images.githubusercontent.com",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def repo_file(value: object, label: str, errors: list[str]) -> None:
    if not nonempty(value):
        errors.append(f"{label} must be a non-empty repository-relative path")
        return
    rel = Path(str(value))
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} must remain repository-relative")
        return
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository")
        return
    if not resolved.is_file():
        errors.append(f"{label} does not exist: {value}")


def string_list(value: object, label: str, errors: list[str], *, required: bool = False) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    out: list[str] = []
    for i, item in enumerate(value):
        if not nonempty(item):
            errors.append(f"{label}[{i}] must be a non-empty string")
        else:
            out.append(str(item))
    if required and not out:
        errors.append(f"{label} must be non-empty")
    if len(out) != len(set(out)):
        errors.append(f"{label} must not contain duplicates")
    return out


def no_private_locators(value: object, label: str, errors: list[str]) -> None:
    text = json.dumps(value, sort_keys=True).casefold()
    for token in PRIVATE_TOKENS:
        if token.casefold() in text:
            errors.append(f"{label} contains forbidden private locator token: {token}")


def heading_slug(title: str) -> str:
    value = title.strip().casefold()
    value = re.sub(r"[^\w\s-]", "", value)
    return re.sub(r"\s+", "-", value)


def fragment_exists(text: str, fragment: str) -> bool:
    for line in text.splitlines():
        if line.startswith("#") and heading_slug(line.lstrip("#").strip()) == fragment:
            return True
    return False


def theorem_section(human: str, rid: str) -> str:
    marker = f"## {rid} "
    start = human.find(marker)
    if start < 0:
        return ""
    nxt = human.find("\n## ", start + len(marker))
    return human[start:] if nxt < 0 else human[start:nxt]


def canonical_line(section: str, label: str) -> str | None:
    prefix = f"**{label}:** `"
    for line in section.splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line[len(prefix):-1]
    return None


def roadmap_headings(roadmap: str) -> list[tuple[int, str]]:
    start = roadmap.find("# Current formal grammar programme")
    end = roadmap.find("\n# Formal fixture policy", start)
    if start < 0 or end < 0:
        return []
    return [
        (int(number), title.strip())
        for number, title in re.findall(r"^## PR #(\d+) — (.+)$", roadmap[start:end], flags=re.MULTILINE)
    ]


def validate_documents(
    contract: dict[str, Any],
    theorems: dict[str, Any],
    counterexamples: dict[str, Any],
    selection: dict[str, Any],
    cross_repo_patterns: dict[str, Any],
    roadmap_state: dict[str, Any],
    base_contract: dict[str, Any],
    human: str,
    roadmap: str,
    *,
    check_paths: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    claim_classes = set(base_contract.get("claim_classes", []))

    if contract.get("type") != "uft-id-relation-core-contract" or contract.get("schema_version") != "1.0.1":
        errors.append("relation contract shape mismatch")
    if contract.get("claim_class") != "DEFINITION" or "DEFINITION" not in claim_classes:
        errors.append("relation contract claim class must be DEFINITION")
    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("relation authorities must match canonical mapping exactly")
    elif check_paths:
        for key, path in EXPECTED_AUTHORITIES.items():
            repo_file(path, f"authority.{key}", errors)

    primary = contract.get("primary_types")
    if not isinstance(primary, dict):
        errors.append("primary_types must be an object")
    else:
        if primary.get("rewrite_relation") != "stepRel:X->X->Prop":
            errors.append("general rewrite carrier must remain stepRel:X->X->Prop")
        if primary.get("admissibility") != "A:X->Prop":
            errors.append("admissibility must remain a separate predicate A:X->Prop")

    hard = contract.get("hard_rules")
    if not isinstance(hard, dict) or set(hard) != EXPECTED_HARD_RULES:
        errors.append("relation hard_rules must contain the exact expected key set")
    elif any(value is not False for value in hard.values()):
        errors.append("all relation hard_rules must remain false")

    limits = contract.get("execution_limits")
    expected_policy = (
        "Routine exhaustive conformance enumerates every labelled binary relation on the fixed carriers "
        "Fin1, Fin2, and Fin3 only; it does not quotient relations by carrier isomorphism."
    )
    if not isinstance(limits, dict) or limits != {
        "max_exhaustive_states": 3,
        "exact_relation_count_through_fin3": 530,
        "policy": expected_policy,
    }:
        errors.append("bounded labelled-relation enumeration contract drift")

    deferred = " ".join(string_list(contract.get("explicit_deferrals"), "explicit_deferrals", errors, required=True)).casefold()
    for phrase in ("newman", "selector", "schedule", "infinite paths", "lean"):
        if phrase not in deferred:
            errors.append(f"explicit deferral missing: {phrase}")

    records = theorems.get("records")
    if theorems.get("type") != "uft-id-relation-theorem-registry" or theorems.get("schema_version") != "1.0.1" or not isinstance(records, list):
        errors.append("relation theorem registry shape mismatch")
        records = []
    ids: set[str] = set()
    required_fields = {"id", "lean_target_name", "name", "claim_class", "statement", "hypotheses", "proof_reference", "executable_evidence", "nonclaims"}
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"relation theorem {i} must be an object")
            continue
        if set(record) != required_fields:
            errors.append(f"relation theorem {record.get('id', i)} must use exact canonical fields")
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"relation theorem {i} missing id")
            continue
        rid = str(rid)
        if rid in ids:
            errors.append(f"duplicate relation theorem id {rid}")
        ids.add(rid)
        if record.get("claim_class") != "PROVED" or record.get("claim_class") not in claim_classes:
            errors.append(f"{rid} must retain claim class PROVED")
        if record.get("statement") != EXPECTED_STATEMENTS.get(rid):
            errors.append(f"{rid} theorem statement drift")
        hypotheses = string_list(record.get("hypotheses"), f"{rid}.hypotheses", errors, required=True)
        if hypotheses != EXPECTED_HYPOTHESES.get(rid):
            errors.append(f"{rid} theorem hypotheses drift")
        proof = record.get("proof_reference")
        if proof != EXPECTED_PROOF_REFS.get(rid):
            errors.append(f"{rid} proof reference drift")
        elif check_paths:
            path, fragment = str(proof).split("#", 1)
            repo_file(path, f"{rid}.proof_reference", errors)
            if path == "theory/RELATION_CALCULUS.md" and not fragment_exists(human, fragment):
                errors.append(f"{rid} proof reference fragment missing")
        evidence = string_list(record.get("executable_evidence"), f"{rid}.executable_evidence", errors, required=True)
        if check_paths:
            for path in evidence:
                repo_file(path, f"{rid}.executable_evidence", errors)
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)

        section = theorem_section(human, rid)
        if not section:
            errors.append(f"human theorem section missing for {rid}")
        else:
            if canonical_line(section, "Canonical statement") != EXPECTED_STATEMENTS.get(rid):
                errors.append(f"{rid} human canonical statement drift")
            raw = canonical_line(section, "Canonical hypotheses")
            try:
                human_hypotheses = json.loads(raw) if raw is not None else None
            except json.JSONDecodeError:
                human_hypotheses = None
            if human_hypotheses != EXPECTED_HYPOTHESES.get(rid):
                errors.append(f"{rid} human canonical hypotheses drift")
    if ids != EXPECTED_THEOREM_IDS:
        errors.append("relation theorem IDs must match the four foundational RW theorems plus UFT-SEL-001 exactly")

    derived = theorems.get("derived_corollaries")
    if not isinstance(derived, list) or len(derived) != 1:
        errors.append("exactly one derived corollary is required")
    else:
        item = derived[0]
        if not isinstance(item, dict) or item.get("from") != ["UFT-RW-003", "UFT-RW-004"] or item.get("separate_headline_theorem_id") is not False:
            errors.append("unique-normal derived corollary must remain split across existence and uniqueness theorems")

    deferred_targets = theorems.get("deferred_theorem_targets")
    if not isinstance(deferred_targets, list) or len(deferred_targets) != 1:
        errors.append("Newman's lemma must remain the sole deferred theorem target")
    else:
        target = deferred_targets[0]
        if not isinstance(target, dict):
            errors.append("deferred theorem target must be an object")
        elif target.get("name") != "Newman's lemma" or target.get("status") != "deferred" or not nonempty(target.get("reason")):
            errors.append("Newman's lemma must remain deferred from the advertised theorem surface")

    cx_records = counterexamples.get("records")
    if counterexamples.get("type") != "uft-id-relation-counterexample-registry" or not isinstance(cx_records, list):
        errors.append("relation counterexample registry shape mismatch")
        cx_records = []
    cx_ids: set[str] = set()
    for i, record in enumerate(cx_records):
        if not isinstance(record, dict):
            errors.append(f"relation counterexample {i} must be an object")
            continue
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"relation counterexample {i} missing id")
            continue
        rid = str(rid)
        if rid in cx_ids:
            errors.append(f"duplicate relation counterexample id {rid}")
        cx_ids.add(rid)
        if record.get("claim_class") != "COUNTEREXAMPLE":
            errors.append(f"{rid}.claim_class must be COUNTEREXAMPLE")
        expected = EXPECTED_CX.get(rid)
        if expected is None:
            errors.append(f"unknown relation counterexample {rid}")
        else:
            for field, value in expected.items():
                if record.get(field) != value:
                    errors.append(f"{rid}.{field} drift")
        string_list(record.get("kills"), f"{rid}.kills", errors, required=True)
        evidence = string_list(record.get("evidence"), f"{rid}.evidence", errors, required=True)
        if check_paths:
            for path in evidence:
                repo_file(path, f"{rid}.evidence", errors)
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)
    if cx_ids != EXPECTED_CX_IDS:
        errors.append("counterexample IDs must be exactly FORK3, LOOP1, and EXIT2")

    # The selection specimen is a small claim-bearing authority. Validate it as one
    # canonical payload so hashes cannot authenticate semantic drift the validator missed.
    if selection != EXPECTED_SELECTION:
        errors.append("genus selection specimen canonical payload drift")

    pattern_records = cross_repo_patterns.get("patterns")
    pattern_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(pattern_records, list):
        errors.append("canonical cross-repo registry must contain patterns list")
    else:
        for item in pattern_records:
            if isinstance(item, dict) and nonempty(item.get("pattern_id")):
                pattern_by_id[str(item["pattern_id"])] = item
    for pattern_id, expected in EXPECTED_CONTEXT_PATTERNS.items():
        actual = pattern_by_id.get(pattern_id)
        if actual is None:
            errors.append(f"selection context reference missing canonical pattern: {pattern_id}")
            continue
        for field, value in expected.items():
            if actual.get(field) != value:
                errors.append(f"{pattern_id}.{field} drift from verified selection context")

    if roadmap_state.get("type") != "uft-id-roadmap-state" or roadmap_state.get("schema_version") != "1.0.0":
        errors.append("live roadmap state shape mismatch")
    if roadmap_state.get("basis_commit") != "091405c136fd8dc936e6bd3a544ab22433d04782":
        errors.append("roadmap state must bind the merged PR9 basis commit")
    if roadmap_state.get("active_planned_surface") != 11:
        errors.append("live roadmap active planned surface must be PR11")
    if roadmap_state.get("completed") != [5, 6, 7, 8, 9]:
        errors.append("live roadmap completed set drift")
    sequence = roadmap_state.get("sequence")
    actual_sequence = []
    if isinstance(sequence, list):
        for item in sequence:
            if isinstance(item, dict):
                actual_sequence.append((item.get("planned_pr"), item.get("surface"), item.get("status")))
    if actual_sequence != EXPECTED_ROADMAP_SEQUENCE:
        errors.append("live roadmap sequence/status drift")

    if roadmap_headings(roadmap) != EXPECTED_HEADINGS:
        errors.append("ROADMAP current formal grammar heading order drift")
    roadmap_anchors = [
        "PR #9 — Deterministic observation calculus",
        "**Status:** COMPLETE.",
        "PR #10 — Lean observation foundation",
        "**Status:** DEFERRED",
        "PR #11 — Relation-first recovery core",
        "stepRel : X -> X -> Prop",
        "A : X -> Prop",
        "UFT-SEL-001",
        "CX-RW-FORK3",
        "labelled relation on `Fin 1`, `Fin 2`, and `Fin 3`",
        "XR-P17",
        "XR-P18",
        "NO_GIANT_FORMALIZATION_PR",
        "NO_STANDALONE_FINITE_FIXTURE_ZOO",
        "GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY",
    ]
    for anchor in roadmap_anchors:
        if anchor not in roadmap:
            errors.append(f"ROADMAP missing relation-program anchor: {anchor}")

    legacy = [
        "PR #8 — Invariant calculus, assurance graph, and model obligations",
        "PR #9 — Observation fibres, quotients, and reconstruction",
        "PR #10 — Recovery taxonomy",
        "PR #11 — Transport taxonomy and epistemic bridges",
        "PR #12 — Information-functional robustness",
        "PR #13 — Finite reference-model battery",
        "PR #14 — Lean foundation and theorem-surface audit",
        "PR #15 — Representation and receiver robustness",
        "Phase 0: lineage and provenance — COMPLETE",
        "2019 MEI reproduction — COMPLETE",
    ]
    for anchor in legacy:
        if anchor not in roadmap:
            errors.append(f"ROADMAP missing retained compatibility anchor: {anchor}")

    for label, value in (
        ("relation contract", contract),
        ("relation theorems", theorems),
        ("relation counterexamples", counterexamples),
        ("selection specimen", selection),
        ("roadmap state", roadmap_state),
    ):
        no_private_locators(value, label, errors)

    human_anchors = [
        "NORMAL != ADMISSIBLE != FIXED_POINT",
        "stepRel:X",
        "UFT-RW-001 Branchwise invariant induction",
        "UFT-RW-002 Right-unique rewriting is confluent",
        "UFT-RW-003 Confluence gives at most one reachable normal form",
        "UFT-RW-004 Termination gives reachable normal-form existence",
        "UFT-SEL-001 Distinct reachable normal labels refute unique selection",
        "labelled binary relation",
        "XR-P17",
        "XR-P18",
        "FINITE_CONFORMANCE != GENERAL_PROOF",
        "INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION",
    ]
    for anchor in human_anchors:
        if anchor not in human:
            errors.append(f"relation human authority missing semantic anchor: {anchor}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "theorem_count": len(ids),
        "counterexample_count": len(cx_ids),
        "public_context_ref_count": len(EXPECTED_CONTEXT_PATTERNS),
        "exhaustive_relation_count": 530,
    }


def validate() -> dict[str, Any]:
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
    parser = argparse.ArgumentParser()
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
