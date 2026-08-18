#!/usr/bin/env python3
"""Validate the source-specific VOP-2019-MEI reproduction authority surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"
RESULT_PATH = ROOT / "research/vopson/reproduction/2019-mei/result.json"
CORPUS_PATH = ROOT / "research/vopson/corpus.json"
CLAIM_GRAPH_PATH = ROOT / "research/vopson/CLAIM_GRAPH.json"
MATRIX_PATH = ROOT / "research/vopson/REPRODUCTION_MATRIX.md"
CONTRACT_PATH = ROOT / "machine/contract.json"
NODE_RE = re.compile(r"^MEI-N[1-9][0-9]*$")

ALLOWED_NODE_KINDS = {
    "source-definition",
    "source-derived",
    "external-premise",
    "source-text-audit",
    "source-assumption",
    "source-prediction",
}
ALLOWED_EDGE_TYPES = {"supports", "contextualizes", "does-not-entail", "requires"}
REQUIRED_PROMOTION_RULE = (
    "ARITHMETIC_REPRODUCED != PREMISE_VALIDATED != "
    "PHYSICAL_INTERPRETATION_VALIDATED != EXPERIMENTALLY_CONFIRMED"
)
REQUIRED_EVIDENCE = {
    "research/vopson/reproduction/2019-mei/SOURCE_MAP.md",
    "research/vopson/reproduction/2019-mei/DERIVATION.md",
    "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json",
    "research/vopson/reproduction/2019-mei/DIMENSIONAL_AUDIT.md",
    "research/vopson/reproduction/2019-mei/CONTROL_MATRIX.md",
    "research/vopson/reproduction/2019-mei/result.json",
    "experiments/reproduction/vopson_2019_mei/fixtures.json",
    "experiments/reproduction/vopson_2019_mei/run.py",
    "experiments/run_pr6.py",
    "tests/test_vopson_2019_mei.py",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(root: Path = ROOT) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []

    def load(relative: str) -> dict[str, Any]:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            errors.append(f"{relative} must contain a JSON object")
            return {}
        return value

    graph = load("research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json")
    result = load("research/vopson/reproduction/2019-mei/result.json")
    corpus = load("research/vopson/corpus.json")
    claim_graph = load("research/vopson/CLAIM_GRAPH.json")
    contract = load("machine/contract.json")

    if graph.get("type") != "uft-id-vopson-2019-mei-assumption-graph":
        errors.append("assumption graph type mismatch")
    if graph.get("schema_version") != "1.0.0":
        errors.append("assumption graph schema_version must be 1.0.0")
    if graph.get("source_work_id") != "VOP-2019-MEI":
        errors.append("assumption graph source_work_id mismatch")
    if graph.get("source_doi") != "10.1063/1.5123794":
        errors.append("assumption graph source_doi mismatch")
    if graph.get("promotion_rule") != REQUIRED_PROMOTION_RULE:
        errors.append("assumption graph promotion_rule mismatch")

    allowed_claims = set(contract.get("claim_classes", []))
    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("assumption graph nodes must be a non-empty list")
        nodes = []
    ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or NODE_RE.fullmatch(node_id) is None:
            errors.append(f"nodes[{index}].id is invalid")
            continue
        if node_id in ids:
            errors.append(f"duplicate assumption node id: {node_id}")
        ids.add(node_id)
        if node.get("kind") not in ALLOWED_NODE_KINDS:
            errors.append(f"{node_id}: undeclared node kind {node.get('kind')!r}")
        if node.get("claim_class") not in allowed_claims:
            errors.append(f"{node_id}: invalid claim_class {node.get('claim_class')!r}")
        for field in ("statement", "source_locator", "status"):
            if not nonempty(node.get(field)):
                errors.append(f"{node_id}: {field} must be non-empty")

    edges = graph.get("edges")
    if not isinstance(edges, list):
        errors.append("assumption graph edges must be a list")
        edges = []
    seen_edges: set[tuple[str, str, str]] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        source = edge.get("from")
        target = edge.get("to")
        edge_type = edge.get("type")
        if source not in ids:
            errors.append(f"edges[{index}]: dangling source {source!r}")
        if target not in ids:
            errors.append(f"edges[{index}]: dangling target {target!r}")
        if edge_type not in ALLOWED_EDGE_TYPES:
            errors.append(f"edges[{index}]: undeclared edge type {edge_type!r}")
        if source == target and source in ids:
            errors.append(f"edges[{index}]: self-edge is forbidden")
        key = (str(source), str(target), str(edge_type))
        if key in seen_edges:
            errors.append(f"duplicate assumption edge: {key}")
        seen_edges.add(key)
        if "note" in edge and not nonempty(edge.get("note")):
            errors.append(f"edges[{index}].note must be non-empty when present")

    if ("MEI-N4", "MEI-N6", "does-not-entail") not in seen_edges:
        errors.append("assumption graph must preserve Landauer does-not-entail stored-bit-energy edge")

    if result.get("type") != "uft-id-vopson-2019-mei-reproduction-result":
        errors.append("result type mismatch")
    if result.get("reproduction_status") != "reproduced":
        errors.append("result reproduction_status must be reproduced")
    if result.get("claim_class") != "DIAGNOSTIC":
        errors.append("result claim_class must remain DIAGNOSTIC")
    if result.get("promotion_rule") != REQUIRED_PROMOTION_RULE:
        errors.append("result promotion_rule mismatch")
    if result.get("source_byte_hash") is not None:
        errors.append("primary source byte hash must remain null unless source bytes are actually committed/pinned")

    works = corpus.get("works")
    target_work = None
    if isinstance(works, list):
        target_work = next((work for work in works if isinstance(work, dict) and work.get("work_id") == "VOP-2019-MEI"), None)
    if not isinstance(target_work, dict):
        errors.append("corpus missing VOP-2019-MEI")
    else:
        if target_work.get("equation_map_status") != "complete":
            errors.append("corpus VOP-2019-MEI equation_map_status must be complete")
        if target_work.get("reproduction_status") != "reproduced":
            errors.append("corpus VOP-2019-MEI reproduction_status must be reproduced")
        evidence = target_work.get("evidence_paths")
        if not isinstance(evidence, list) or not REQUIRED_EVIDENCE.issubset(set(evidence)):
            errors.append("corpus VOP-2019-MEI evidence_paths do not cover the full PR6 authority surface")

    graph_nodes = claim_graph.get("nodes")
    target_claim = None
    if isinstance(graph_nodes, list):
        target_claim = next((node for node in graph_nodes if isinstance(node, dict) and node.get("node_id") == "CL-MEI-BIT-MASS"), None)
    if not isinstance(target_claim, dict):
        errors.append("claim graph missing CL-MEI-BIT-MASS")
    else:
        if target_claim.get("claim_class") != "THEOREM_TARGET":
            errors.append("CL-MEI-BIT-MASS must remain THEOREM_TARGET")
        if target_claim.get("assessment_status") != "arithmetic-reproduced-physical-hypothesis-unresolved":
            errors.append("CL-MEI-BIT-MASS assessment_status is not synchronized with PR6")
        evidence = target_claim.get("evidence_paths")
        if not isinstance(evidence, list) or not evidence:
            errors.append("CL-MEI-BIT-MASS requires reproduction evidence paths")
        obligation = target_claim.get("reproduction_obligation")
        if not nonempty(obligation) or "remain unresolved" not in str(obligation):
            errors.append("CL-MEI-BIT-MASS reproduction_obligation must record the unresolved physical premise")

    matrix = (root / "research/vopson/REPRODUCTION_MATRIX.md").read_text(encoding="utf-8")
    if "| `VOP-2019-MEI`" not in matrix or "| `reproduced` |" not in matrix:
        errors.append("reproduction matrix does not record VOP-2019-MEI as reproduced")

    for relative in REQUIRED_EVIDENCE:
        if not (root / relative).is_file():
            errors.append(f"required PR6 evidence file missing: {relative}")

    authority = contract.get("vopson_2019_mei_reproduction")
    if not isinstance(authority, dict):
        errors.append("machine contract missing vopson_2019_mei_reproduction")
    elif authority.get("validator") != "scripts/validate_vopson_2019_mei.py":
        errors.append("machine contract PR6 validator path mismatch")

    return {
        "ok": not errors,
        "errors": errors,
        "summary": {
            "nodes": len(nodes),
            "edges": len(edges),
            "corpus_status": target_work.get("reproduction_status") if isinstance(target_work, dict) else None,
            "claim_status": target_claim.get("assessment_status") if isinstance(target_claim, dict) else None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"validated PR6 assumption graph: {report['summary']['nodes']} nodes, {report['summary']['edges']} edges")
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
