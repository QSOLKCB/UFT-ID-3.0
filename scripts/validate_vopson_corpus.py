#!/usr/bin/env python3
"""Validate the canonical Vopson corpus and claim graph.

The validator is deliberately dependency-free and fail-closed. It checks
bibliographic identity, enums, dependency references, graph acyclicity,
claim-class discipline, and evidence-path requirements.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_PATH = ROOT / "research/vopson/AUTHOR.json"
CORPUS_PATH = ROOT / "research/vopson/corpus.json"
GRAPH_PATH = ROOT / "research/vopson/CLAIM_GRAPH.json"
CONTRACT_PATH = ROOT / "machine/contract.json"

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def dependency_cycle(nodes: set[str], edges: list[dict[str, Any]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge.get("edge_type") in {"requires", "extends", "supports"}:
            adjacency[str(edge["from"])].append(str(edge["to"]))

    state: dict[str, int] = {node: 0 for node in nodes}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for child in adjacency.get(node, []):
            if state[child] == 0:
                cycle = visit(child)
                if cycle:
                    return cycle
            elif state[child] == 1:
                index = stack.index(child)
                return stack[index:] + [child]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(nodes):
        if state[node] == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    author = load_json(AUTHOR_PATH)
    corpus = load_json(CORPUS_PATH)
    graph = load_json(GRAPH_PATH)
    contract = load_json(CONTRACT_PATH)

    expected_orcid = "0000-0002-8073-5538"
    author_id = f"orcid:{expected_orcid}"

    if author.get("orcid") != expected_orcid or not ORCID_RE.fullmatch(str(author.get("orcid", ""))):
        errors.append("AUTHOR.json must contain canonical ORCID 0000-0002-8073-5538")
    for label, value in (
        ("AUTHOR.json", author.get("author_id")),
        ("corpus.json", corpus.get("author_id")),
        ("CLAIM_GRAPH.json", graph.get("author_id")),
    ):
        if value != author_id:
            errors.append(f"{label} author_id must equal {author_id}")

    corpus_enums = corpus.get("enums", {})
    peer_enum = set(corpus_enums.get("peer_review_status", []))
    equation_enum = set(corpus_enums.get("equation_map_status", []))
    reproduction_enum = set(corpus_enums.get("reproduction_status", []))
    declared_tracks = set(corpus.get("claim_tracks", []))

    works = corpus.get("works")
    if not isinstance(works, list) or not works:
        errors.append("corpus.json works must be a non-empty list")
        works = []

    work_ids: set[str] = set()
    primary_dois: set[str] = set()
    all_dois: set[str] = set()
    work_map: dict[str, dict[str, Any]] = {}

    for index, work in enumerate(works):
        prefix = f"works[{index}]"
        if not isinstance(work, dict):
            errors.append(f"{prefix} must be an object")
            continue

        work_id = work.get("work_id")
        if not isinstance(work_id, str) or not work_id:
            errors.append(f"{prefix}.work_id must be non-empty")
            continue
        if work_id in work_ids:
            errors.append(f"duplicate work_id: {work_id}")
        work_ids.add(work_id)
        work_map[work_id] = work

        year = work.get("year")
        publication_date = work.get("publication_date")
        if not isinstance(year, int):
            errors.append(f"{work_id}: year must be an integer")
        if not isinstance(publication_date, str) or not publication_date.startswith(f"{year:04d}-"):
            errors.append(f"{work_id}: publication_date must agree with year")

        doi = work.get("doi")
        if doi is not None:
            if not isinstance(doi, str) or not DOI_RE.fullmatch(doi):
                errors.append(f"{work_id}: invalid DOI {doi!r}")
            elif doi in primary_dois:
                errors.append(f"duplicate primary DOI: {doi}")
            else:
                primary_dois.add(doi)
                all_dois.add(doi)

        alternate = work.get("alternate_identifiers", [])
        if not isinstance(alternate, list):
            errors.append(f"{work_id}: alternate_identifiers must be a list")
            alternate = []
        for identifier in alternate:
            if isinstance(identifier, str) and identifier.startswith("10."):
                if not DOI_RE.fullmatch(identifier):
                    errors.append(f"{work_id}: invalid alternate DOI {identifier!r}")
                if identifier in all_dois and identifier != doi:
                    warnings.append(f"{work_id}: alternate DOI {identifier} appears elsewhere in corpus")
                all_dois.add(identifier)

        if doi is None and not alternate:
            errors.append(f"{work_id}: missing DOI requires at least one alternate identifier")
        if doi is None and not work.get("official_metadata_url"):
            errors.append(f"{work_id}: missing DOI requires an official metadata URL")

        if work.get("peer_review_status") not in peer_enum:
            errors.append(f"{work_id}: invalid peer_review_status")
        if work.get("equation_map_status") not in equation_enum:
            errors.append(f"{work_id}: invalid equation_map_status")
        if work.get("reproduction_status") not in reproduction_enum:
            errors.append(f"{work_id}: invalid reproduction_status")

        tracks = work.get("claim_tracks")
        if not isinstance(tracks, list) or not tracks:
            errors.append(f"{work_id}: claim_tracks must be non-empty")
        else:
            unknown_tracks = set(tracks) - declared_tracks
            if unknown_tracks:
                errors.append(f"{work_id}: undeclared claim tracks {sorted(unknown_tracks)}")

        dependencies = work.get("depends_on", [])
        if not isinstance(dependencies, list):
            errors.append(f"{work_id}: depends_on must be a list")
        elif work_id in dependencies:
            errors.append(f"{work_id}: work cannot depend on itself")

        evidence_paths = work.get("evidence_paths", [])
        if not isinstance(evidence_paths, list):
            errors.append(f"{work_id}: evidence_paths must be a list")
            evidence_paths = []
        if work.get("reproduction_status") in {"partial-reproduction", "reproduced"} and not evidence_paths:
            errors.append(f"{work_id}: reproduced status requires evidence_paths")
        for relative in evidence_paths:
            if not (ROOT / relative).is_file():
                errors.append(f"{work_id}: evidence path does not exist: {relative}")

    for work_id, work in work_map.items():
        for dependency in work.get("depends_on", []):
            if dependency not in work_ids:
                errors.append(f"{work_id}: unknown dependency {dependency}")

    graph_classes = graph.get("claim_classes")
    contract_classes = contract.get("claim_classes")
    if graph_classes != contract_classes:
        errors.append("CLAIM_GRAPH.json claim_classes must exactly match machine/contract.json")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        errors.append("CLAIM_GRAPH.json nodes must be non-empty")
        nodes = []
    if not isinstance(edges, list):
        errors.append("CLAIM_GRAPH.json edges must be a list")
        edges = []

    node_ids: set[str] = set()
    allowed_classes = set(contract_classes or [])
    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} must be an object")
            continue
        node_id = node.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(f"{prefix}.node_id must be non-empty")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node_id: {node_id}")
        node_ids.add(node_id)

        claim_class = node.get("claim_class")
        if claim_class not in allowed_classes:
            errors.append(f"{node_id}: invalid or missing single claim_class")

        source_work_ids = node.get("source_work_ids", [])
        if source_work_ids is None:
            source_work_ids = []
        if not isinstance(source_work_ids, list):
            errors.append(f"{node_id}: source_work_ids must be a list")
            source_work_ids = []
        for source_work_id in source_work_ids:
            if source_work_id not in work_ids:
                errors.append(f"{node_id}: unknown source_work_id {source_work_id}")

        evidence_paths = node.get("evidence_paths", [])
        if not isinstance(evidence_paths, list):
            errors.append(f"{node_id}: evidence_paths must be a list")
            evidence_paths = []

        established = node.get("assessment_status") == "established-literature"
        if claim_class in {"PROVED", "COUNTEREXAMPLE"} and not established and not evidence_paths:
            errors.append(f"{node_id}: {claim_class} requires repository evidence_paths")
        for relative in evidence_paths:
            if not (ROOT / relative).is_file():
                errors.append(f"{node_id}: evidence path does not exist: {relative}")

        if node.get("kind") == "source-claim" and not node.get("source_claim_summary"):
            errors.append(f"{node_id}: source-claim requires source_claim_summary")

    allowed_edge_types = set(graph.get("edge_types", []))
    for index, edge in enumerate(edges):
        prefix = f"edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source = edge.get("from")
        target = edge.get("to")
        edge_type = edge.get("edge_type")
        if source not in node_ids:
            errors.append(f"{prefix}: unknown source node {source}")
        if target not in node_ids:
            errors.append(f"{prefix}: unknown target node {target}")
        if source == target:
            errors.append(f"{prefix}: self-edge is not allowed")
        if edge_type not in allowed_edge_types:
            errors.append(f"{prefix}: undeclared edge_type {edge_type}")

    if not errors:
        cycle = dependency_cycle(node_ids, edges)
        if cycle:
            errors.append("dependency cycle: " + " -> ".join(cycle))

    authority = contract.get("vopson_corpus_authority", {})
    expected_authority = {
        "author": "research/vopson/AUTHOR.json",
        "corpus": "research/vopson/corpus.json",
        "claim_graph": "research/vopson/CLAIM_GRAPH.json",
        "validator": "scripts/validate_vopson_corpus.py",
    }
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            errors.append(f"machine contract vopson_corpus_authority.{key} must equal {expected}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "works": len(works),
            "primary_dois": len(primary_dois),
            "claim_nodes": len(nodes),
            "edges": len(edges),
            "author_orcid": expected_orcid,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit validation report as JSON")
    args = parser.parse_args()

    report = validate()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "validated "
            f"{report['summary']['works']} works, "
            f"{report['summary']['claim_nodes']} claim nodes, "
            f"{report['summary']['edges']} edges"
        )
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        for error in report["errors"]:
            print(f"error: {error}")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
