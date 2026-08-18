#!/usr/bin/env python3
"""Validate the canonical Vopson corpus and claim graph.

The validator is dependency-free and fail-closed. Machine vocabularies are
anchored in ``machine/contract.json``; human chronology/claim tables are
compared deterministically with their JSON authorities.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_PATH = ROOT / "research/vopson/AUTHOR.json"
CORPUS_PATH = ROOT / "research/vopson/corpus.json"
GRAPH_PATH = ROOT / "research/vopson/CLAIM_GRAPH.json"
CORPUS_MD_PATH = ROOT / "research/vopson/CORPUS.md"
GRAPH_MD_PATH = ROOT / "research/vopson/CLAIM_GRAPH.md"
CONTRACT_PATH = ROOT / "machine/contract.json"

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
HTTPS_RE = re.compile(r"^https://\S+$")

CORPUS_HEADING = "## Chronology"
GRAPH_HEADING = "## Current assessment summary"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def parse_iso_date(value: object, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO date string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be a valid ISO date")
        return None


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_string_list(
    value: object,
    label: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    if nonempty and not value:
        errors.append(f"{label} must be non-empty")
    result: list[str] = []
    for index, item in enumerate(value):
        if not nonempty_string(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        result.append(str(item))
    if len(result) != len(set(result)):
        errors.append(f"{label} must not contain duplicates")
    return result


def repository_evidence_file(relative: object, label: str, errors: list[str]) -> Path | None:
    if not nonempty_string(relative):
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None

    raw = Path(str(relative))
    if raw.is_absolute():
        errors.append(f"{label} must not be absolute: {relative}")
        return None

    root = ROOT.resolve()
    resolved = (ROOT / raw).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        errors.append(f"{label} escapes repository root: {relative}")
        return None

    if not resolved.is_file():
        errors.append(f"{label} does not exist: {relative}")
        return None
    return resolved


def cycle_from_adjacency(
    nodes: Iterable[str],
    adjacency: dict[str, list[str]],
) -> list[str] | None:
    node_set = set(nodes)
    state: dict[str, int] = {node: 0 for node in node_set}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for child in adjacency.get(node, []):
            if child not in state:
                continue
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

    for node in sorted(node_set):
        if state[node] == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def dependency_cycle(nodes: set[str], edges: list[dict[str, Any]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge.get("edge_type") in {"requires", "extends", "supports"}:
            source = edge.get("from")
            target = edge.get("to")
            if isinstance(source, str) and isinstance(target, str):
                adjacency[source].append(target)
    return cycle_from_adjacency(nodes, adjacency)


def work_dependency_cycle(work_map: dict[str, dict[str, Any]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for work_id, work in work_map.items():
        dependencies = work.get("depends_on", [])
        if isinstance(dependencies, list):
            adjacency[work_id].extend(
                dependency for dependency in dependencies if isinstance(dependency, str)
            )
    return cycle_from_adjacency(set(work_map), adjacency)


def markdown_escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def code_list(values: list[str]) -> str:
    return ", ".join(f"`{markdown_escape(value)}`" for value in values) if values else "-"


def render_corpus_table(works: list[dict[str, Any]]) -> list[str]:
    rows = [
        "| ID | Year | Work | Type / review | Claim tracks | Identifiers | Depends on | Equation map | Reproduction |",
        "|---|---:|---|---|---|---|---|---|---|",
    ]
    for work in works:
        url = work.get("publisher_url") or work.get("official_metadata_url")
        title = markdown_escape(work.get("title", ""))
        work_cell = f"[{title}]({url})" if nonempty_string(url) else title
        identifiers: list[str] = []
        if nonempty_string(work.get("doi")):
            identifiers.append(str(work["doi"]))
        identifiers.extend(
            str(identifier)
            for identifier in work.get("alternate_identifiers", [])
            if nonempty_string(identifier)
        )
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{markdown_escape(work.get('work_id', ''))}`",
                    str(work.get("year", "")),
                    work_cell,
                    f"`{markdown_escape(work.get('work_type', ''))}` / "
                    f"`{markdown_escape(work.get('peer_review_status', ''))}`",
                    code_list(list(work.get("claim_tracks", []))),
                    code_list(identifiers),
                    code_list(list(work.get("depends_on", []))),
                    f"`{markdown_escape(work.get('equation_map_status', ''))}`",
                    f"`{markdown_escape(work.get('reproduction_status', ''))}`",
                ]
            )
            + " |"
        )
    return rows


def render_claim_table(nodes: list[dict[str, Any]]) -> list[str]:
    rows = [
        "| Node | Claim | Kind | UFT-ID class | Assessment status | Source |",
        "|---|---|---|---|---|---|",
    ]
    for node in nodes:
        sources = list(node.get("source_work_ids", []) or [])
        if not sources:
            sources = list(node.get("source_identifiers", []) or [])
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{markdown_escape(node.get('node_id', ''))}`",
                    markdown_escape(node.get("title", "")),
                    f"`{markdown_escape(node.get('kind', ''))}`",
                    f"`{markdown_escape(node.get('claim_class', ''))}`",
                    f"`{markdown_escape(node.get('assessment_status', ''))}`",
                    code_list(sources),
                ]
            )
            + " |"
        )
    return rows


def extract_markdown_table(path: Path, heading: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        heading_index = lines.index(heading)
    except ValueError:
        return []

    table_start: int | None = None
    for index in range(heading_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and index > heading_index + 1:
            break
        if stripped.startswith("|"):
            table_start = index
            break
    if table_start is None:
        return []

    table: list[str] = []
    for line in lines[table_start:]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        table.append(stripped)
    return table


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    author = load_json(AUTHOR_PATH)
    corpus = load_json(CORPUS_PATH)
    graph = load_json(GRAPH_PATH)
    contract = load_json(CONTRACT_PATH)

    expected_orcid = "0000-0002-8073-5538"
    author_id = f"orcid:{expected_orcid}"

    schema = contract.get("vopson_corpus_schema")
    if not isinstance(schema, dict):
        errors.append("machine/contract.json must define vopson_corpus_schema")
        schema = {}

    snapshot = parse_iso_date(
        schema.get("snapshot_date"),
        "machine contract vopson_corpus_schema.snapshot_date",
        errors,
    )
    snapshot_text = schema.get("snapshot_date")

    if author.get("orcid") != expected_orcid or not ORCID_RE.fullmatch(
        str(author.get("orcid", ""))
    ):
        errors.append("AUTHOR.json must contain canonical ORCID 0000-0002-8073-5538")
    for label, value in (
        ("AUTHOR.json", author.get("author_id")),
        ("corpus.json", corpus.get("author_id")),
        ("CLAIM_GRAPH.json", graph.get("author_id")),
    ):
        if value != author_id:
            errors.append(f"{label} author_id must equal {author_id}")

    verified_as_of = (
        author.get("public_affiliation_snapshot", {}).get("verified_as_of")
        if isinstance(author.get("public_affiliation_snapshot"), dict)
        else None
    )
    for label, value in (
        ("AUTHOR.json public affiliation", verified_as_of),
        ("corpus.json", corpus.get("as_of")),
        ("CLAIM_GRAPH.json", graph.get("as_of")),
    ):
        if value != snapshot_text:
            errors.append(f"{label} snapshot date must equal {snapshot_text}")

    contract_enums = {
        key: schema.get(key, [])
        for key in ("peer_review_status", "equation_map_status", "reproduction_status")
    }
    corpus_enums = corpus.get("enums")
    if not isinstance(corpus_enums, dict):
        errors.append("corpus.json enums must be an object")
        corpus_enums = {}
    for key, expected in contract_enums.items():
        if corpus_enums.get(key) != expected:
            errors.append(
                f"corpus.json enums.{key} must exactly match machine contract authority"
            )

    peer_enum = set(contract_enums["peer_review_status"])
    equation_enum = set(contract_enums["equation_map_status"])
    reproduction_enum = set(contract_enums["reproduction_status"])
    work_type_enum = set(schema.get("work_types", []))
    node_kind_enum = set(schema.get("node_kinds", []))
    contract_edge_types = list(schema.get("edge_types", []))
    established_exempt_kinds = set(schema.get("established_literature_exempt_kinds", []))
    declared_tracks = set(corpus.get("claim_tracks", []))

    works = corpus.get("works")
    if not isinstance(works, list) or not works:
        errors.append("corpus.json works must be a non-empty list")
        works = []

    work_ids: set[str] = set()
    primary_dois: set[str] = set()
    identifier_owner: dict[str, tuple[str, str]] = {}
    work_map: dict[str, dict[str, Any]] = {}

    required_work_strings = (
        "work_id",
        "title",
        "venue",
        "work_type",
        "peer_review_status",
        "role",
        "equation_map_status",
        "reproduction_status",
        "official_metadata_url",
        "scope_note",
    )

    def register_identifier(identifier: str, work_id: str, field: str) -> None:
        owner = identifier_owner.get(identifier)
        if owner is not None:
            errors.append(
                f"DOI collision: {identifier} is used by {owner[0]}.{owner[1]} "
                f"and {work_id}.{field}"
            )
            return
        identifier_owner[identifier] = (work_id, field)

    for index, work in enumerate(works):
        prefix = f"works[{index}]"
        if not isinstance(work, dict):
            errors.append(f"{prefix} must be an object")
            continue

        for field in required_work_strings:
            if not nonempty_string(work.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")

        work_id = work.get("work_id")
        if not nonempty_string(work_id):
            continue
        work_id = str(work_id)
        if work_id in work_ids:
            errors.append(f"duplicate work_id: {work_id}")
        work_ids.add(work_id)
        work_map[work_id] = work

        unique_string_list(
            work.get("authors"),
            f"{work_id}.authors",
            errors,
            nonempty=True,
        )

        year = work.get("year")
        publication = parse_iso_date(
            work.get("publication_date"),
            f"{work_id}.publication_date",
            errors,
        )
        if not isinstance(year, int):
            errors.append(f"{work_id}: year must be an integer")
        elif publication and publication.year != year:
            errors.append(f"{work_id}: publication_date must agree with year")
        if snapshot and publication and publication > snapshot:
            errors.append(f"{work_id}: publication_date exceeds corpus snapshot")

        if work.get("work_type") not in work_type_enum:
            errors.append(f"{work_id}: invalid work_type")
        if work.get("peer_review_status") not in peer_enum:
            errors.append(f"{work_id}: invalid peer_review_status")
        if work.get("equation_map_status") not in equation_enum:
            errors.append(f"{work_id}: invalid equation_map_status")
        if work.get("reproduction_status") not in reproduction_enum:
            errors.append(f"{work_id}: invalid reproduction_status")

        official_url = work.get("official_metadata_url")
        publisher_url = work.get("publisher_url")
        if not nonempty_string(official_url) or not HTTPS_RE.fullmatch(str(official_url)):
            errors.append(f"{work_id}: official_metadata_url must be an https URL")
        if publisher_url is not None and (
            not nonempty_string(publisher_url)
            or not HTTPS_RE.fullmatch(str(publisher_url))
        ):
            errors.append(f"{work_id}: publisher_url must be null or an https URL")

        doi = work.get("doi")
        if doi is not None:
            if not isinstance(doi, str) or not DOI_RE.fullmatch(doi):
                errors.append(f"{work_id}: invalid DOI {doi!r}")
            else:
                primary_dois.add(doi)
                register_identifier(doi, work_id, "doi")

        alternate = unique_string_list(
            work.get("alternate_identifiers", []),
            f"{work_id}.alternate_identifiers",
            errors,
        )
        valid_alternate_dois: list[str] = []
        for identifier in alternate:
            if not DOI_RE.fullmatch(identifier):
                errors.append(
                    f"{work_id}: alternate identifier must be a validated DOI: {identifier!r}"
                )
                continue
            valid_alternate_dois.append(identifier)
            register_identifier(identifier, work_id, "alternate_identifiers")

        if doi is None and not valid_alternate_dois and not nonempty_string(official_url):
            errors.append(
                f"{work_id}: missing DOI requires a validated alternate DOI "
                "or an official metadata URL"
            )

        tracks = unique_string_list(
            work.get("claim_tracks"),
            f"{work_id}.claim_tracks",
            errors,
            nonempty=True,
        )
        unknown_tracks = set(tracks) - declared_tracks
        if unknown_tracks:
            errors.append(f"{work_id}: undeclared claim tracks {sorted(unknown_tracks)}")

        dependencies = unique_string_list(
            work.get("depends_on", []),
            f"{work_id}.depends_on",
            errors,
        )
        if work_id in dependencies:
            errors.append(f"{work_id}: work cannot depend on itself")

        evidence_paths = unique_string_list(
            work.get("evidence_paths", []),
            f"{work_id}.evidence_paths",
            errors,
        )
        if (
            work.get("reproduction_status") in {"partial-reproduction", "reproduced"}
            and not evidence_paths
        ):
            errors.append(f"{work_id}: reproduced status requires evidence_paths")
        for evidence_index, relative in enumerate(evidence_paths):
            repository_evidence_file(
                relative,
                f"{work_id}.evidence_paths[{evidence_index}]",
                errors,
            )

        for field in ("volume", "issue", "article_or_pages"):
            value = work.get(field)
            if value is not None and not nonempty_string(value):
                errors.append(f"{work_id}.{field} must be null or a non-empty string")

    for work_id, work in work_map.items():
        dependencies = work.get("depends_on", [])
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if dependency not in work_ids:
                    errors.append(f"{work_id}: unknown dependency {dependency}")

    work_cycle = work_dependency_cycle(work_map)
    if work_cycle:
        errors.append("work dependency cycle: " + " -> ".join(work_cycle))

    graph_classes = graph.get("claim_classes")
    contract_classes = contract.get("claim_classes")
    if graph_classes != contract_classes:
        errors.append("CLAIM_GRAPH.json claim_classes must exactly match machine/contract.json")

    if graph.get("edge_types") != contract_edge_types:
        errors.append(
            "CLAIM_GRAPH.json edge_types must exactly match machine contract authority"
        )

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

        for field in ("node_id", "kind", "title", "claim_class", "assessment_status"):
            if not nonempty_string(node.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")

        node_id = node.get("node_id")
        if not nonempty_string(node_id):
            continue
        node_id = str(node_id)
        if node_id in node_ids:
            errors.append(f"duplicate node_id: {node_id}")
        node_ids.add(node_id)

        kind = node.get("kind")
        if kind not in node_kind_enum:
            errors.append(f"{node_id}: invalid node kind {kind!r}")

        claim_class = node.get("claim_class")
        if claim_class not in allowed_classes:
            errors.append(f"{node_id}: invalid or missing single claim_class")

        source_work_ids = unique_string_list(
            node.get("source_work_ids", []),
            f"{node_id}.source_work_ids",
            errors,
        )
        for source_work_id in source_work_ids:
            if source_work_id not in work_ids:
                errors.append(f"{node_id}: unknown source_work_id {source_work_id}")

        source_identifiers = unique_string_list(
            node.get("source_identifiers", []),
            f"{node_id}.source_identifiers",
            errors,
        )
        for identifier in source_identifiers:
            if not DOI_RE.fullmatch(identifier):
                errors.append(f"{node_id}: invalid source DOI {identifier!r}")

        evidence_paths = unique_string_list(
            node.get("evidence_paths", []),
            f"{node_id}.evidence_paths",
            errors,
        )

        assessment_status = node.get("assessment_status")
        established = assessment_status == "established-literature"
        if established and kind not in established_exempt_kinds:
            errors.append(
                f"{node_id}: established-literature exemption is restricted to "
                f"{sorted(established_exempt_kinds)}"
            )
        exempt = established and kind in established_exempt_kinds
        if claim_class in {"PROVED", "COUNTEREXAMPLE"} and not exempt and not evidence_paths:
            errors.append(f"{node_id}: {claim_class} requires repository evidence_paths")

        for evidence_index, relative in enumerate(evidence_paths):
            repository_evidence_file(
                relative,
                f"{node_id}.evidence_paths[{evidence_index}]",
                errors,
            )

        if kind == "source-claim":
            if not source_work_ids:
                errors.append(f"{node_id}: source-claim requires at least one source_work_id")
            if not nonempty_string(node.get("source_claim_summary")):
                errors.append(f"{node_id}: source-claim requires source_claim_summary")
            if not nonempty_string(node.get("reproduction_obligation")):
                errors.append(f"{node_id}: source-claim requires reproduction_obligation")

        if (
            kind == "external-premise"
            and claim_class == "THEOREM_TARGET"
            and not nonempty_string(node.get("adversarial_companion"))
        ):
            errors.append(
                f"{node_id}: external THEOREM_TARGET requires adversarial_companion"
            )

    allowed_edge_types = set(contract_edge_types)
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
        if not nonempty_string(edge.get("note")):
            errors.append(f"{prefix}.note must be a non-empty string")

    graph_cycle = dependency_cycle(node_ids, edges)
    if graph_cycle:
        errors.append("claim dependency cycle: " + " -> ".join(graph_cycle))

    expected_corpus_table = render_corpus_table(works)
    actual_corpus_table = extract_markdown_table(CORPUS_MD_PATH, CORPUS_HEADING)
    if actual_corpus_table != expected_corpus_table:
        errors.append(
            "research/vopson/CORPUS.md chronology table is out of sync with corpus.json"
        )

    expected_claim_table = render_claim_table(nodes)
    actual_claim_table = extract_markdown_table(GRAPH_MD_PATH, GRAPH_HEADING)
    if actual_claim_table != expected_claim_table:
        errors.append(
            "research/vopson/CLAIM_GRAPH.md assessment table is out of sync "
            "with CLAIM_GRAPH.json"
        )

    authority = contract.get("vopson_corpus_authority", {})
    expected_authority = {
        "author": "research/vopson/AUTHOR.json",
        "human_corpus": "research/vopson/CORPUS.md",
        "corpus": "research/vopson/corpus.json",
        "claim_graph_human": "research/vopson/CLAIM_GRAPH.md",
        "claim_graph": "research/vopson/CLAIM_GRAPH.json",
        "definitions": "research/vopson/DEFINITIONS.md",
        "reproduction_matrix": "research/vopson/REPRODUCTION_MATRIX.md",
        "counterexample_matrix": "research/vopson/COUNTEREXAMPLE_MATRIX.md",
        "response_history": "research/vopson/RESPONSE_HISTORY.md",
        "validator": "scripts/validate_vopson_corpus.py",
    }
    if not isinstance(authority, dict):
        errors.append("machine contract vopson_corpus_authority must be an object")
        authority = {}
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            errors.append(
                f"machine contract vopson_corpus_authority.{key} must equal {expected}"
            )

    required_reads = contract.get("required_agent_reads", [])
    if "research/vopson/COUNTEREXAMPLE_MATRIX.md" not in required_reads:
        errors.append(
            "machine contract required_agent_reads must include "
            "research/vopson/COUNTEREXAMPLE_MATRIX.md"
        )

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "works": len(works),
            "primary_dois": len(primary_dois),
            "all_dois": len(identifier_owner),
            "claim_nodes": len(nodes),
            "edges": len(edges),
            "author_orcid": expected_orcid,
            "snapshot_date": snapshot_text,
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
