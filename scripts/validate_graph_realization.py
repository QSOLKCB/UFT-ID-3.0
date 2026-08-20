#!/usr/bin/env python3
"""Fail-closed validation for graph realization and typed incidence authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/graph_realization_contract.json",
    "results": ROOT / "machine/graph_realization_results.json",
    "sources": ROOT / "research/GRAPH_REALIZATION_SOURCES.md",
    "human": ROOT / "theory/GRAPH_REALIZATION.md",
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


def validate() -> dict[str, object]:
    errors: list[str] = []

    for name, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing graph-realization authority file: {path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    relation_contract = load_json(PATHS["relation_contract"])
    cross_repo = load_json(PATHS["cross_repo_patterns"])
    sources = PATHS["sources"].read_text(encoding="utf-8")
    human = PATHS["human"].read_text(encoding="utf-8")

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

    no_private_locators(contract, "graph contract", errors)
    no_private_locators(results, "graph results", errors)
    no_private_locators(sources, "graph source map", errors)
    no_private_locators(human, "graph human theory", errors)

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
