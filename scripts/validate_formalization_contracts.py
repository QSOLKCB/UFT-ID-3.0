#!/usr/bin/env python3
"""Fail-closed validation for PR #8 formalization contracts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/formalization_contract.json",
    "invariants": ROOT / "machine/invariant_specs.json",
    "assurance": ROOT / "machine/assurance_graph.json",
    "obligations": ROOT / "machine/definition_obligations.json",
    "falsification": ROOT / "machine/falsification_contract.json",
    "invariant_human": ROOT / "theory/INVARIANT_CALCULUS.md",
    "assurance_human": ROOT / "theory/ASSURANCE.md",
    "obligations_human": ROOT / "theory/DEFINITION_OBLIGATIONS.md",
    "falsification_human": ROOT / "theory/FALSIFICATION_CONTRACTS.md",
    "experiment": ROOT / "experiments/formalization/run.py",
    "receipt": ROOT / "experiments/run_pr8.py",
    "tests": ROOT / "tests/test_pr8_formalization.py",
    "roadmap": ROOT / "ROADMAP.md",
}

EXPECTED_AUTHORITIES = {
    "invariant_specs": "machine/invariant_specs.json",
    "assurance_graph": "machine/assurance_graph.json",
    "definition_obligations": "machine/definition_obligations.json",
    "falsification_contract": "machine/falsification_contract.json",
    "invariant_human": "theory/INVARIANT_CALCULUS.md",
    "assurance_human": "theory/ASSURANCE.md",
    "obligations_human": "theory/DEFINITION_OBLIGATIONS.md",
    "falsification_human": "theory/FALSIFICATION_CONTRACTS.md",
    "validator": "scripts/validate_formalization_contracts.py",
    "experiment": "experiments/formalization/run.py",
    "receipt": "experiments/run_pr8.py",
    "tests": "tests/test_pr8_formalization.py",
    "roadmap": "ROADMAP.md",
}

EXPECTED_HARD_RULES = {
    "implemented_pattern_implies_universal_theorem",
    "formal_proof_implies_runtime_conformance",
    "runtime_conformance_implies_empirical_validation",
    "deterministic_replay_implies_scientific_confirmation",
    "content_identity_implies_semantic_truth",
    "named_object_implies_well_defined_object",
    "proxy_may_silently_replace_source_object",
    "claim_label_implies_implemented_structure",
    "claimed_reversibility_without_inverse_or_bijectivity_evidence",
    "falsifiable_claim_may_omit_rejection_condition",
    "private_attachment_identifier_may_be_published",
    "paper_specific_ontology_is_inherited_by_methodological_reuse",
}

CLAIM_CLASSES = {
    "DEFINITION", "THEOREM_TARGET", "PROVED", "COUNTEREXAMPLE", "DIAGNOSTIC",
    "EMPIRICAL", "INTERPRETIVE", "SPECULATIVE", "NONCLAIM",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


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
    out: list[str] = []
    for i, item in enumerate(value):
        if not nonempty(item):
            errors.append(f"{label}[{i}] must be a non-empty string")
        else:
            out.append(str(item))
    if len(out) != len(set(out)):
        errors.append(f"{label} must not contain duplicates")
    return out


def repo_file(value: object, label: str, errors: list[str]) -> None:
    if not nonempty(value):
        errors.append(f"{label} must be a non-empty repository-relative path")
        return
    rel = Path(str(value))
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} must not escape repository")
        return
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} must remain inside repository")
        return
    if not resolved.is_file():
        errors.append(f"{label} does not exist: {value}")


def require_shape(doc: dict[str, Any], doc_type: str, snapshot: object, label: str, errors: list[str]) -> None:
    if doc.get("type") != doc_type:
        errors.append(f"{label} type mismatch")
    if doc.get("schema_version") != "1.0.0":
        errors.append(f"{label} schema mismatch")
    if doc.get("snapshot_date") != snapshot:
        errors.append(f"{label} snapshot_date must equal formalization contract snapshot")


def validate_documents(
    contract: dict[str, Any],
    invariants: dict[str, Any],
    assurance: dict[str, Any],
    obligations: dict[str, Any],
    falsification: dict[str, Any],
    human_docs: dict[str, str],
    *,
    check_paths: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []

    if contract.get("type") != "uft-id-formalization-contract":
        errors.append("formalization contract type mismatch")
    if contract.get("schema_version") != "1.0.0":
        errors.append("formalization contract schema mismatch")
    snapshot = contract.get("snapshot_date")
    if not nonempty(snapshot):
        errors.append("formalization contract snapshot_date required")

    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("formalization contract authorities must match canonical mapping exactly")
    elif check_paths:
        for key, rel in EXPECTED_AUTHORITIES.items():
            repo_file(rel, f"authority.{key}", errors)

    hard = contract.get("hard_rules")
    if not isinstance(hard, dict):
        errors.append("formalization hard_rules must be an object")
    else:
        if set(hard) != EXPECTED_HARD_RULES:
            errors.append("formalization hard_rules must contain the complete expected key set")
        if any(v is not False for v in hard.values()):
            errors.append("all formalization hard_rules must remain false")

    kinds = set(string_list(contract.get("invariant_kinds"), "contract.invariant_kinds", errors, required=True))
    statuses = set(string_list(contract.get("invariant_statuses"), "contract.invariant_statuses", errors, required=True))
    dimensions = set(string_list(contract.get("assurance_dimensions"), "contract.assurance_dimensions", errors, required=True))

    require_shape(invariants, "uft-id-invariant-spec-registry", snapshot, "invariants", errors)
    require_shape(assurance, "uft-id-assurance-graph", snapshot, "assurance", errors)
    require_shape(obligations, "uft-id-definition-and-model-obligation-registry", snapshot, "obligations", errors)
    require_shape(falsification, "uft-id-falsification-contract", snapshot, "falsification", errors)

    source_ids: set[str] = set()
    sources = contract.get("source_inputs")
    if not isinstance(sources, list) or not sources:
        errors.append("formalization source_inputs must be a non-empty list")
        sources = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"source_inputs[{i}] must be object")
            continue
        sid = source.get("source_id")
        if not nonempty(sid):
            errors.append(f"source_inputs[{i}].source_id required")
            continue
        sid = str(sid)
        if sid in source_ids:
            errors.append(f"duplicate source_id {sid}")
        source_ids.add(sid)
        cls = source.get("source_class")
        if cls in {"methodological-donor", "formal-assurance-donor"}:
            for key in ("repository", "ref", "path", "blob_sha"):
                if not nonempty(source.get(key)):
                    errors.append(f"{sid}.{key} required for public donor")
            if source.get("ref") != "main":
                errors.append(f"{sid}.ref must be main")
            sha = source.get("blob_sha")
            if not isinstance(sha, str) or not SHA40.fullmatch(sha):
                errors.append(f"{sid}.blob_sha must be exact 40-char Git blob SHA")
        elif cls == "author-supplied-design-input":
            serialized = json.dumps(source, sort_keys=True)
            if any(token in serialized for token in ("file_000", "gmail:", "gdrive:", "docs.google.com", "drive.google.com")):
                errors.append(f"{sid} leaks private attachment/connector identifier")
            if source.get("public_locator") is not None or source.get("source_hash") is not None:
                errors.append(f"{sid} private design input must not invent public locator/hash")
        else:
            errors.append(f"{sid}.source_class unsupported")
        string_list(source.get("preserved_structure"), f"{sid}.preserved_structure", errors, required=True)
        string_list(source.get("not_inherited"), f"{sid}.not_inherited", errors, required=True)

    required_inv = {
        "id", "name", "domain", "codomain", "transformation", "hypotheses", "property",
        "break_conditions", "kind", "scope", "status", "claim_class", "source_lineage", "nonclaims",
    }
    inv_ids: set[str] = set()
    records = invariants.get("records")
    if not isinstance(records, list) or not records:
        errors.append("invariant records must be non-empty list")
        records = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"invariants.records[{i}] must be object")
            continue
        rid = record.get("id")
        if not nonempty(rid):
            errors.append(f"invariants.records[{i}].id required")
            continue
        rid = str(rid)
        if rid in inv_ids:
            errors.append(f"duplicate invariant id {rid}")
        inv_ids.add(rid)
        missing = required_inv - set(record)
        if missing:
            errors.append(f"{rid} missing fields: {sorted(missing)}")
        for field in ("name", "domain", "codomain", "transformation", "property", "scope"):
            if not nonempty(record.get(field)):
                errors.append(f"{rid}.{field} required")
        if record.get("kind") not in kinds:
            errors.append(f"{rid}.kind unsupported")
        if record.get("status") not in statuses:
            errors.append(f"{rid}.status unsupported")
        if record.get("claim_class") not in CLAIM_CLASSES:
            errors.append(f"{rid}.claim_class unsupported")
        string_list(record.get("hypotheses"), f"{rid}.hypotheses", errors, required=True)
        string_list(record.get("break_conditions"), f"{rid}.break_conditions", errors, required=True)
        refs = string_list(record.get("source_lineage"), f"{rid}.source_lineage", errors, required=True)
        if set(refs) - source_ids:
            errors.append(f"{rid} references unknown source lineage")
        string_list(record.get("nonclaims"), f"{rid}.nonclaims", errors, required=True)
        evidence = record.get("evidence")
        if evidence is not None:
            paths = string_list(evidence, f"{rid}.evidence", errors, required=True)
            if check_paths:
                for path in paths:
                    repo_file(path, f"{rid}.evidence", errors)
    if inv_ids != {f"UI-INV-{i:03d}" for i in range(1, 7)}:
        errors.append("invariant registry must contain UI-INV-001 through UI-INV-006 exactly")

    node_ids: set[str] = set()
    nodes = assurance.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("assurance nodes must be non-empty list")
        nodes = []
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"assurance.nodes[{i}] must be object")
            continue
        nid = node.get("id")
        if not nonempty(nid):
            errors.append(f"assurance.nodes[{i}].id required")
            continue
        nid = str(nid)
        if nid in node_ids:
            errors.append(f"duplicate assurance node {nid}")
        node_ids.add(nid)
        if not nonempty(node.get("axis")) or not nonempty(node.get("meaning")):
            errors.append(f"{nid} requires axis and meaning")
    if node_ids != dimensions:
        errors.append("assurance nodes must exactly match contract assurance_dimensions")

    support_pairs: set[tuple[str, str]] = set()
    for field in ("support_edges", "forbidden_automatic_promotions"):
        edges = assurance.get(field)
        if not isinstance(edges, list) or not edges:
            errors.append(f"assurance.{field} must be non-empty list")
            edges = []
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f"assurance.{field}[{i}] must be object")
                continue
            src, dst = edge.get("from"), edge.get("to")
            if src not in node_ids or dst not in node_ids:
                errors.append(f"assurance.{field}[{i}] has dangling endpoint")
            if src == dst:
                errors.append(f"assurance.{field}[{i}] self edge forbidden")
            if field == "support_edges":
                if not nonempty(edge.get("relation")) or not nonempty(edge.get("entitlement")):
                    errors.append(f"assurance.support_edges[{i}] requires relation and entitlement")
                pair = (str(src), str(dst))
                if pair in support_pairs:
                    errors.append(f"duplicate assurance support edge {pair}")
                support_pairs.add(pair)
            elif not nonempty(edge.get("reason")):
                errors.append(f"assurance.forbidden_automatic_promotions[{i}].reason required")

    def_ids: set[str] = set()
    definitions = obligations.get("definition_obligations")
    if not isinstance(definitions, list) or not definitions:
        errors.append("definition_obligations must be non-empty list")
        definitions = []
    for i, item in enumerate(definitions):
        if not isinstance(item, dict):
            errors.append(f"definition_obligations[{i}] must be object")
            continue
        oid = item.get("id")
        if not nonempty(oid):
            errors.append(f"definition_obligations[{i}].id required")
            continue
        oid = str(oid)
        if oid in def_ids:
            errors.append(f"duplicate definition obligation {oid}")
        def_ids.add(oid)
        if not nonempty(item.get("term")) or not nonempty(item.get("nonclaim")):
            errors.append(f"{oid} requires term and nonclaim")
        string_list(item.get("minimum_declarations"), f"{oid}.minimum_declarations", errors, required=True)
        if item.get("conditional_declarations") is not None:
            string_list(item.get("conditional_declarations"), f"{oid}.conditional_declarations", errors)

    model_ids: set[str] = set()
    models = obligations.get("claim_realization_obligations")
    if not isinstance(models, list) or not models:
        errors.append("claim_realization_obligations must be non-empty list")
        models = []
    for i, item in enumerate(models):
        if not isinstance(item, dict):
            errors.append(f"claim_realization_obligations[{i}] must be object")
            continue
        oid = item.get("id")
        if not nonempty(oid):
            errors.append(f"claim_realization_obligations[{i}].id required")
            continue
        oid = str(oid)
        if oid in model_ids:
            errors.append(f"duplicate model obligation {oid}")
        model_ids.add(oid)
        if not nonempty(item.get("claim")) or not nonempty(item.get("failure_state")):
            errors.append(f"{oid} requires claim and failure_state")
        string_list(item.get("required_evidence"), f"{oid}.required_evidence", errors, required=True)

    proxy = obligations.get("proxy_rule")
    if not isinstance(proxy, dict):
        errors.append("proxy_rule required")
    else:
        for key in ("source_object", "proxy_object", "prohibited"):
            if not nonempty(proxy.get(key)):
                errors.append(f"proxy_rule.{key} required")

    required_fields = string_list(falsification.get("required_fields"), "falsification.required_fields", errors, required=True)
    example = falsification.get("synthetic_conformance_example")
    fals_count = 0
    if not isinstance(example, dict):
        errors.append("synthetic_conformance_example required")
    else:
        fals_count = 1
        missing = set(required_fields) - set(example)
        if missing:
            errors.append(f"synthetic falsification example missing fields: {sorted(missing)}")
        for field in ("hypothesis_id", "claim_class", "status"):
            if not nonempty(example.get(field)):
                errors.append(f"synthetic falsification example {field} required")
        if example.get("claim_class") not in CLAIM_CLASSES:
            errors.append("synthetic falsification claim_class unsupported")
        for field in (
            "independent_variables", "perturbations", "observables", "predictions",
            "null_model", "rejection_conditions", "evidence_required", "scope_limits",
        ):
            string_list(example.get(field), f"synthetic.{field}", errors, required=True)
    string_list(falsification.get("nonclaims"), "falsification.nonclaims", errors, required=True)

    anchors = {
        "invariant_human": ["INVARIANT_UNDER_F != UNIVERSAL_INVARIANT", "UI-INV-004", "CLAIMED_STRUCTURE", "IMPLEMENTED_STRUCTURE"],
        "assurance_human": ["Formal Assurance Graph", "FORMAL_SYNTAX != PROOF", "MODEL_OUTPUT != EXECUTION_EVIDENCE"],
        "obligations_human": ["NAMED_OBJECT != WELL_DEFINED_MATHEMATICAL_OBJECT", "MODEL-OBL-REVERSIBLE", "SOFTWARE_SCAFFOLD != VALIDATED_SCIENTIFIC_SIMULATION"],
        "falsification_human": ["FalsificationSpec", "FALS-SYN-001", "FALSIFIABLE_SCHEMA != EMPIRICICAL_VALIDATION"],
    }
    anchors["falsification_human"][-1] = "FALSIFIABLE_SCHEMA != EMPIRICAL_VALIDATION"
    for key, phrases in anchors.items():
        text = human_docs.get(key, "")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{key} missing semantic anchor: {phrase}")

    roadmap = human_docs.get("roadmap", "")
    planned = [
        "PR #8 — Invariant calculus, assurance graph, and model obligations",
        "PR #9 — Observation fibres, quotients, and reconstruction",
        "PR #10 — Recovery taxonomy",
        "PR #11 — Transport taxonomy and epistemic bridges",
        "PR #12 — Information-functional robustness",
        "PR #13 — Finite reference-model battery",
        "PR #14 — Lean foundation and theorem-surface audit",
        "PR #15 — Representation and receiver robustness",
    ]
    for phrase in planned:
        if phrase not in roadmap:
            errors.append(f"roadmap missing planned formalization stage: {phrase}")
    if "Phase 0: lineage and provenance — COMPLETE" not in roadmap:
        errors.append("roadmap must mark Phase 0 complete after merged PR #7")
    if "2019 MEI reproduction — COMPLETE" not in roadmap:
        errors.append("roadmap must mark merged PR #6 reproduction complete")
    if "NO_GIANT_FORMALIZATION_PR" not in roadmap:
        errors.append("roadmap must preserve no-giant-PR rule")

    deferred = contract.get("deferred_surfaces")
    deferred_count = 0
    if not isinstance(deferred, list) or not deferred:
        errors.append("deferred_surfaces must be non-empty list")
    else:
        deferred_count = len(deferred)
        actual = {item.get("planned_pr") for item in deferred if isinstance(item, dict)}
        if actual != {9, 10, 11, 12, 13, 14, 15}:
            errors.append("deferred_surfaces must map exactly to planned PRs 9 through 15")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "invariant_count": len(inv_ids),
        "assurance_node_count": len(node_ids),
        "definition_obligation_count": len(def_ids),
        "model_obligation_count": len(model_ids),
        "falsification_example_count": fals_count,
        "roadmap_deferred_surface_count": deferred_count,
    }


def validate() -> dict[str, Any]:
    missing = [str(path.relative_to(ROOT)) for path in PATHS.values() if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing authority file: {path}" for path in missing],
            "invariant_count": 0,
            "assurance_node_count": 0,
            "definition_obligation_count": 0,
            "model_obligation_count": 0,
            "falsification_example_count": 0,
            "roadmap_deferred_surface_count": 0,
        }
    human_docs = {
        "invariant_human": PATHS["invariant_human"].read_text(encoding="utf-8"),
        "assurance_human": PATHS["assurance_human"].read_text(encoding="utf-8"),
        "obligations_human": PATHS["obligations_human"].read_text(encoding="utf-8"),
        "falsification_human": PATHS["falsification_human"].read_text(encoding="utf-8"),
        "roadmap": PATHS["roadmap"].read_text(encoding="utf-8"),
    }
    return validate_documents(
        load(PATHS["contract"]),
        load(PATHS["invariants"]),
        load(PATHS["assurance"]),
        load(PATHS["obligations"]),
        load(PATHS["falsification"]),
        human_docs,
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
        print("PR8 formalization contracts:", result["status"])
        for error in result["errors"]:
            print(" -", error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
