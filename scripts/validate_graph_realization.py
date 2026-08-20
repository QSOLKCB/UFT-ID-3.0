#!/usr/bin/env python3
"""Fail-closed validation for graph realization and typed incidence authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/graph_realization_contract.json",
    "results": ROOT / "machine/graph_realization_results.json",
    "sources": ROOT / "research/GRAPH_REALIZATION_SOURCES.md",
    "human": ROOT / "theory/GRAPH_REALIZATION.md",
    "base_contract": ROOT / "machine/contract.json",
    "claims": ROOT / "docs/CLAIMS.md",
    "readme4ai": ROOT / "README4AI.md",
    "reproducibility": ROOT / "docs/REPRODUCIBILITY.md",
    "roadmap": ROOT / "ROADMAP.md",
    "relation_contract": ROOT / "machine/relation_contract.json",
    "cross_repo_patterns": ROOT / "machine/cross_repo_patterns.json",
    "experiment": ROOT / "experiments/graph_realization/run.py",
    "tests": ROOT / "tests/test_graph_realization.py",
    "receipt": ROOT / "experiments/run_graph_realization.py",
}

EXPECTED_SHA256 = {
    "contract": "f65b7c1c3e3bf29666d09662ba3b9319ff1cd7583362c1c7736d9adca87858ed",
    "results": "c947c612922c68eccaed585ea256295afe9f7bb428d801f06b1e2e41cbacb0d8",
    "sources": "776a7fa9e46f3ee68d75ffaa651d68696899108b24e1f603e19b1f3c9264342b",
    "human": "e75d1b249ca36192d09a22a8359084c7e194fd601e9ef672a8ad2c94cf062687",
}

EXPECTED_RESULT_IDS = {
    "UFT-GR-001", "UFT-GR-002", "UFT-GR-003", "UFT-GR-004",
    "UFT-GR-005", "UFT-GR-006", "CX-GR-001", "CX-GR-002", "CX-GR-003",
}

EXPECTED_BOUNDARIES = {
    "ALGEBRA != GRAPH != EMBEDDING != PHYSICS",
    "GRAPH != DRAWING",
    "COUPLING_GRAPH != PLACEMENT_GRAPH",
    "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
    "LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH",
    "MODULE_INVENTORY != INCIDENCE != GLOBAL_TOPOLOGY",
    "SAME_LOCAL_MODULE != SAME_GLOBAL_CONNECTIVITY",
    "NORMAL_VERTEX != SINK_SCC",
    "SINK_SCC != FIXED_POINT != TERMINATION",
    "LOSSY_PROJECTION != STRUCTURAL_EQUIVALENCE",
    "F3^3=I3 != GRAPH_THEORETIC_3_CYCLE",
    "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
    "MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE",
}

EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/GRAPH_REALIZATION.md",
    "machine_contract": "machine/graph_realization_contract.json",
    "machine_results": "machine/graph_realization_results.json",
    "source_map": "research/GRAPH_REALIZATION_SOURCES.md",
    "validator": "scripts/validate_graph_realization.py",
    "experiment": "experiments/graph_realization/run.py",
    "tests": "tests/test_graph_realization.py",
    "receipt_runner": "experiments/run_graph_realization.py",
    "receipt_version": "1.0.0",
    "base_relation_authority": "machine/relation_contract.json",
    "rule": "Finite relation/digraph realization and typed incidence preserve only declared structure; graph identity, drawings, tetrahedral geometry, material examples, ETQ/SPECTRAL context, and combinatorial invariants do not acquire physical ontology by resemblance or representation.",
}

EXPECTED_AGENT_READS = {
    "theory/GRAPH_REALIZATION.md",
    "machine/graph_realization_contract.json",
    "machine/graph_realization_results.json",
    "research/GRAPH_REALIZATION_SOURCES.md",
    "scripts/validate_graph_realization.py",
    "experiments/run_graph_realization.py",
}

PRIVATE_PATTERNS = (
    "mail.google.com",
    "gmail",
    "thread_id",
    "attachment_id",
    "x_attachment_id",
    "deefiveothree",
    "connector_",
    "private-user-images",
)

SEMANTIC_PROMOTION_PATTERNS = (
    "this proves a universal physical ontology",
    "every sink scc is a physical fixed point",
    "sis2 proves e8 information physics",
    "graph realization proves uft-id physics",
    "material positive control proves uft-id physics",
    "pettini proves extra time is physically real",
    "pettini proves uft-id extra-time ontology",
    "current graph theorem authority: pettini",
)

CLAIMS_ANCHORS = (
    "### C7 - Finite relation semantics admit an exact graph-realization layer",
    "**Status:** PROVED",
    "`UFT-GR-001` through `UFT-GR-006`",
    "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
    "ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY",
)

README_ANCHORS = (
    "## Relation and graph-realization authority",
    "machine/graph_realization_contract.json",
    "machine/graph_realization_results.json",
    "theory/GRAPH_REALIZATION.md",
    "scripts/validate_graph_realization.py",
    "experiments/run_graph_realization.py",
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
)

REPRO_ANCHORS = (
    "## Graph-realization conformance boundary",
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
    "python experiments/run_graph_realization.py --json",
    "graph-realization-validation.json",
    "graph-realization-witness.json",
    "graph-realization-receipt.json",
    "docs/CLAIMS.md",
    "README4AI.md",
    "ROADMAP.md",
)

PETTINI_START = "# Future model-donor programme — typed causality, projection, and assumption structure"
PETTINI_ANCHORS = (
    "ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR",
    "Marco Pettini",
    "Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in (3,2)-Dimensional Spacetime",
    "10.48550/arXiv.2606.12457",
    "ANSATZ_UNIQUENESS != GLOBAL_UNIQUENESS",
    "MODEL_CLASS_EXHAUSTION != PHYSICAL_SELECTION",
    "G_L = (V, L, I)",
    "CORRELATION_EDGE != CAUSAL_RESPONSE_EDGE",
    "NONZERO_CORRELATION != CONTROLLABLE_INFLUENCE",
    "FORGET_EDGE_TYPE = POTENTIAL_INFORMATION_LOSS",
    "MICROSTATE != PROJECTION != CONTEXT_LABEL",
    "MANY_TO_ONE_CONTEXT_MAP != PHYSICAL_IDENTITY",
    "CONDITIONAL_DETERMINISM != ENSEMBLE_DETERMINISM",
    "EQUIVARIANCE_ASSUMED != EQUIVARIANCE_DERIVED",
    "WKB_CHARACTERISTIC != EXACT_PROPAGATOR",
    "DERIVED != ASSUMED != CONDITIONALLY_PREDICTED != EMPIRICALLY_OBSERVED",
    "MAP_NONUNIQUENESS != OBSERVABLE_NONROBUSTNESS",
    "PREPRINT_PREDICTION != EXPERIMENTAL_RESULT",
    "FALSIFIABLE != VERIFIED",
    "(3,2)_SPACETIME_MODEL != UFT_ID_ONTOLOGY",
    "BULK_FIELD_XA_MODEL != ESTABLISHED_PHYSICAL_FIELD",
    "PREDICTED_CROSS_PAIR_SIGNAL != OBSERVED_CROSS_PAIR_SIGNAL",
    "PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def safe_repo_path(value: object, errors: list[str], label: str) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
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
        errors.append(f"{label} does not exist: {value}")


def no_private_locators(value: object, label: str, errors: list[str]) -> None:
    text = json.dumps(value, ensure_ascii=False).casefold() if not isinstance(value, str) else value.casefold()
    for pattern in PRIVATE_PATTERNS:
        if pattern.casefold() in text:
            errors.append(f"{label} contains forbidden private locator token: {pattern}")


def no_semantic_promotion(value: object, label: str, errors: list[str]) -> None:
    text = json.dumps(value, ensure_ascii=False).casefold() if not isinstance(value, str) else value.casefold()
    for pattern in SEMANTIC_PROMOTION_PATTERNS:
        if pattern in text:
            errors.append(f"{label} contains forbidden semantic/ontology promotion: {pattern}")


def require_anchors(text: str, anchors: tuple[str, ...], label: str, errors: list[str]) -> None:
    for anchor in anchors:
        if anchor not in text:
            errors.append(f"{label} missing semantic anchor: {anchor}")


def validate() -> dict[str, object]:
    errors: list[str] = []

    for _, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing graph-realization authority file: {path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    base_contract = load_json(PATHS["base_contract"])
    relation_contract = load_json(PATHS["relation_contract"])
    cross_repo = load_json(PATHS["cross_repo_patterns"])
    sources = PATHS["sources"].read_text(encoding="utf-8")
    human = PATHS["human"].read_text(encoding="utf-8")
    claims = PATHS["claims"].read_text(encoding="utf-8")
    readme4ai = PATHS["readme4ai"].read_text(encoding="utf-8")
    reproducibility = PATHS["reproducibility"].read_text(encoding="utf-8")
    roadmap = PATHS["roadmap"].read_text(encoding="utf-8")

    for name in ("contract", "results", "sources", "human"):
        actual = sha256_bytes(PATHS[name].read_bytes())
        if actual != EXPECTED_SHA256[name]:
            errors.append(f"{name} canonical payload drift")

    if contract.get("type") != "uft-id-graph-realization-contract":
        errors.append("graph contract type drift")
    if contract.get("schema_version") != "1.0.0":
        errors.append("graph contract schema drift")
    if contract.get("snapshot_date") != "2026-08-20":
        errors.append("graph contract UTC snapshot drift")
    if contract.get("claim_class") != "DEFINITION":
        errors.append("graph contract claim class drift")
    if set(contract.get("hard_boundaries", [])) != EXPECTED_BOUNDARIES:
        errors.append("graph contract hard-boundary set drift")

    central = base_contract.get("graph_realization_authority")
    if central != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central graph_realization_authority payload drift")
    else:
        for field in (
            "human", "machine_contract", "machine_results", "source_map", "validator",
            "experiment", "tests", "receipt_runner", "base_relation_authority",
        ):
            safe_repo_path(central.get(field), errors, f"central graph authority {field}")

    experiment_library = base_contract.get("experiment_library")
    if not isinstance(experiment_library, dict):
        errors.append("base experiment_library must be an object")
    else:
        if experiment_library.get("graph_realization_receipt_runner") != "experiments/run_graph_realization.py":
            errors.append("central graph receipt runner registration drift")
        if experiment_library.get("graph_realization_receipt_version") != "1.0.0":
            errors.append("central graph receipt version registration drift")

    required_reads = base_contract.get("required_agent_reads")
    if not isinstance(required_reads, list) or any(not isinstance(item, str) or not item for item in required_reads):
        errors.append("base required_agent_reads must be a list of non-empty strings")
    elif not EXPECTED_AGENT_READS.issubset(set(required_reads)):
        errors.append("central required_agent_reads missing graph authority surface")

    relation_bridge = contract.get("relation_bridge")
    if not isinstance(relation_bridge, dict):
        errors.append("relation_bridge must be an object")
    else:
        if relation_bridge.get("relation") != "stepRel:X->X->Prop":
            errors.append("graph bridge must preserve stepRel:X->X->Prop")
        if relation_bridge.get("arc_definition") != "(x,y) in A_step iff stepRel(x,y)":
            errors.append("graph bridge adjacency biconditional drift")
        if relation_bridge.get("lost_structure") != []:
            errors.append("exact finite relation/digraph bridge must declare no lost one-step structure")

    if relation_contract.get("primary_types", {}).get("rewrite_relation") != "stepRel:X->X->Prop":
        errors.append("base relation authority no longer exposes canonical stepRel type")

    records = results.get("records")
    ids: set[str] = set()
    if not isinstance(records, list):
        errors.append("graph results must contain a records list")
        records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"graph result {index} must be an object")
            continue
        result_id = record.get("id")
        if not isinstance(result_id, str) or not result_id:
            errors.append(f"graph result {index} has invalid id")
            continue
        if result_id in ids:
            errors.append(f"duplicate graph result id: {result_id}")
        ids.add(result_id)
        claim_class = record.get("claim_class")
        if result_id.startswith("UFT-GR-") and claim_class != "PROVED":
            errors.append(f"{result_id} must remain PROVED")
        if result_id.startswith("CX-GR-") and claim_class != "COUNTEREXAMPLE":
            errors.append(f"{result_id} must remain COUNTEREXAMPLE")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{result_id} must retain executable evidence")
        else:
            for path in evidence:
                safe_repo_path(path, errors, f"{result_id} evidence")
    if ids != EXPECTED_RESULT_IDS:
        errors.append("graph result identity set drift")

    source_records = contract.get("sources")
    if not isinstance(source_records, list) or len(source_records) != 2:
        errors.append("graph contract must contain exactly two public donor source records")
    else:
        by_id = {item.get("source_id"): item for item in source_records if isinstance(item, dict)}
        grinberg = by_id.get("GRINBERG-2025-GRAPH-THEORY")
        evers = by_id.get("EVERS-2015-SIS2")
        if not isinstance(grinberg, dict) or grinberg.get("doi") != "10.48550/arXiv.2308.04512":
            errors.append("Grinberg source identity drift")
        if not isinstance(evers, dict) or evers.get("doi") != "10.1021/ic501825r":
            errors.append("Evers SiS2 source identity drift")
        if isinstance(evers, dict) and evers.get("kind") != "peer-reviewed-empirical-source":
            errors.append("Evers source status drift")

    patterns = cross_repo.get("patterns")
    pattern_ids = set()
    if isinstance(patterns, list):
        for item in patterns:
            if isinstance(item, dict) and isinstance(item.get("pattern_id"), str):
                pattern_ids.add(item["pattern_id"])
    for pattern_id in ("XR-P17", "XR-P18"):
        if pattern_id not in pattern_ids:
            errors.append(f"missing existing public context record: {pattern_id}")

    anchors = (
        "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
        "LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH",
        "SAME LOCAL COORDINATION MOTIF",
        "F3^3=I3 != GRAPH_THEORETIC_3_CYCLE",
        "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
        "No decorative “sacred geometry” image is used as source authority",
    )
    combined = sources + "\n" + human
    for anchor in anchors:
        if anchor not in combined:
            errors.append(f"human graph authority missing semantic anchor: {anchor}")

    require_anchors(claims, CLAIMS_ANCHORS, "docs/CLAIMS.md graph registration", errors)
    require_anchors(readme4ai, README_ANCHORS, "README4AI graph registration", errors)
    require_anchors(reproducibility, REPRO_ANCHORS, "reproducibility graph registration", errors)

    pettini_index = roadmap.find(PETTINI_START)
    if pettini_index < 0:
        errors.append("ROADMAP missing Pettini model-donor programme")
        pettini = ""
    else:
        pettini = roadmap[pettini_index:]
        require_anchors(pettini, PETTINI_ANCHORS, "ROADMAP Pettini model-donor programme", errors)
        if "current graph theorem authority" in pettini.casefold():
            errors.append("ROADMAP Pettini model donor must remain outside current graph theorem authority")
        if "extra-time physics is adopted by uft-id" in pettini.casefold():
            errors.append("ROADMAP Pettini model donor illegally promotes extra-time ontology")

    no_private_locators(contract, "graph contract", errors)
    no_private_locators(results, "graph results", errors)
    no_private_locators(central if isinstance(central, dict) else {}, "central graph authority", errors)
    no_private_locators(sources, "graph source map", errors)
    no_private_locators(human, "graph human theory", errors)

    no_semantic_promotion(contract, "graph contract", errors)
    no_semantic_promotion(results, "graph results", errors)
    no_semantic_promotion(sources, "graph source map", errors)
    no_semantic_promotion(human, "graph human theory", errors)
    no_semantic_promotion(claims, "claims graph registration", errors)
    no_semantic_promotion(readme4ai, "README4AI graph registration", errors)
    no_semantic_promotion(reproducibility, "reproducibility graph registration", errors)
    no_semantic_promotion(pettini, "ROADMAP Pettini model donor", errors)

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(ids),
        "source_count": len(source_records) if isinstance(source_records, list) else 0,
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
        print(
            "graph realization authority: ok "
            f"({result['result_count']} results, {result['source_count']} sources, "
            f"{result['boundary_count']} hard boundaries)"
        )
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
