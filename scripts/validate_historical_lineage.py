#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID 3.0 historical lineage registry."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
P = {
    key: ROOT / rel
    for key, rel in {
        "contract": "machine/historical_lineage_contract.json",
        "sources": "machine/historical_sources.json",
        "symbols": "machine/historical_symbols.json",
        "conflicts": "machine/historical_conflicts.json",
        "results": "machine/historical_results.json",
        "inheritance": "machine/methodological_inheritance.json",
        "human": "research/HISTORICAL_LINEAGE.md",
    }.items()
}

REQ_PLAT = {"academia", "zenodo", "authorea", "google-drive", "github", "archived-copy"}
RESULT_CLASSES = {"formal", "computational", "empirical", "interpretive", "speculative"}
CLAIM_CLASSES = {
    "DEFINITION",
    "THEOREM_TARGET",
    "PROVED",
    "COUNTEREXAMPLE",
    "DIAGNOSTIC",
    "EMPIRICAL",
    "INTERPRETIVE",
    "SPECULATIVE",
    "NONCLAIM",
}
HISTORICAL_SOURCE_FAMILIES = {
    "historical-uft-id",
    "historical-uft-id-method",
    "historical-uft-id-working-record",
    "adjacent-methodological-working-record",
}
METHOD_SOURCE_FAMILIES = {"methodological-inheritance"}
EXPECTED_AUTHORITIES = {
    "sources": "machine/historical_sources.json",
    "symbols": "machine/historical_symbols.json",
    "conflicts": "machine/historical_conflicts.json",
    "results": "machine/historical_results.json",
    "inheritance": "machine/methodological_inheritance.json",
    "human": "research/HISTORICAL_LINEAGE.md",
    "validator": "scripts/validate_historical_lineage.py",
    "receipt": "experiments/run_lineage.py",
    "tests": "tests/test_historical_lineage.py",
}
EXPECTED_HARD_RULES = {
    "historical_source_implies_current_endorsement",
    "platform_mirror_confers_authority",
    "missing_metadata_may_be_guessed",
    "definition_conflicts_may_be_silently_reconciled",
    "method_inheritance_implies_ontology_inheritance",
    "source_hash_implies_semantic_truth",
    "formal_result_implies_runtime_conformance",
    "runtime_conformance_implies_empirical_validation",
    "observer_inaccessibility_implies_physical_destruction",
    "publish_private_connector_identifiers",
    "working_copy_export_hash_equals_native_cloud_hash",
}
AUTHORITY_META = {
    "sources": ("uft-id-historical-source-registry", "1.0.0"),
    "symbols": ("uft-id-historical-symbol-map", "1.0.0"),
    "conflicts": ("uft-id-historical-definition-conflict-registry", "1.0.0"),
    "results": ("uft-id-historical-result-registry", "1.0.0"),
    "inheritance": ("uft-id-methodological-inheritance-registry", "1.0.0"),
}

DOI = re.compile(r"^10\.\d{4,9}/\S+$")
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HIST_ID = re.compile(r"^UFT-HIST-\d{3}$")
METH_ID = re.compile(r"^UFT-METH-\d{3}$")
CANONICAL_ID = re.compile(r"^(?:D\d+[a-z]?|T\d+|CR\d+)$")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def load_documents() -> dict[str, Any]:
    return {
        "contract": load(P["contract"]),
        "sources": load(P["sources"]),
        "symbols": load(P["symbols"]),
        "conflicts": load(P["conflicts"]),
        "results": load(P["results"]),
        "inheritance": load(P["inheritance"]),
        "human": P["human"].read_text(encoding="utf-8"),
    }


def ne(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(
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
    output: list[str] = []
    for index, item in enumerate(value):
        if not ne(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
        else:
            output.append(item)
    if len(output) != len(set(output)):
        errors.append(f"{label} must not contain duplicates")
    return output


def validate_hash(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be object")
        return
    algorithm, digest, scope = value.get("algorithm"), value.get("value"), value.get("scope")
    if not ne(scope):
        errors.append(f"{label}.scope required")
    if algorithm == "sha256":
        if not isinstance(digest, str) or H64.fullmatch(digest) is None:
            errors.append(f"{label}.value invalid sha256")
    elif algorithm == "git-blob-sha1":
        if not isinstance(digest, str) or H40.fullmatch(digest) is None:
            errors.append(f"{label}.value invalid git blob sha")
    else:
        errors.append(f"{label}.algorithm unsupported")


def validate_repo_paths(
    value: object,
    label: str,
    errors: list[str],
    *,
    root: Path,
    nonempty: bool = False,
) -> list[str]:
    paths = string_list(value, label, errors, nonempty=nonempty)
    root_resolved = root.resolve()
    for item in paths:
        pure = PurePosixPath(item)
        if pure.is_absolute() or "\\" in item or ".." in pure.parts or item.startswith("./") or not pure.parts:
            errors.append(f"{label} contains invalid repository-relative path: {item}")
            continue
        target = (root / item).resolve()
        try:
            target.relative_to(root_resolved)
        except ValueError:
            errors.append(f"{label} escapes repository root: {item}")
            continue
        if not target.is_file():
            errors.append(f"{label} target does not exist as retained repository evidence: {item}")
    return paths


def canonical_uft_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    definitions = (root / "theory/DEFINITIONS.md").read_text(encoding="utf-8")
    theorem_targets = (root / "theory/THEOREM_TARGETS.md").read_text(encoding="utf-8")
    ids.update(re.findall(r"^##\s+(D\d+[a-z]?)\.", definitions, flags=re.MULTILINE))
    ids.update(re.findall(r"^##\s+(T\d+)\.", theorem_targets, flags=re.MULTILINE))
    for rel in ("machine/finite_results.json", "machine/cross_repo_results.json"):
        text = (root / rel).read_text(encoding="utf-8")
        ids.update(re.findall(r'"(?:result_id|id)"\s*:\s*"(CR\d+)"', text))
    return ids


def license_display(source: dict[str, Any]) -> str:
    license_record = source["license"]
    value = license_record.get("value")
    return value if ne(value) else license_record["status"]


def relation_display(source: dict[str, Any]) -> str:
    relation = source.get("repository_release_relation")
    if relation is None:
        return "-"
    return str(relation["relation"])


def source_row(source: dict[str, Any]) -> str:
    doi = source.get("doi") or "-"
    date = source.get("date") or "-"
    version = source.get("version") or "-"
    return (
        f"| `{source['source_id']}` | {source['title']} | `{doi}` | "
        f"`{date}/{version}` | `{license_display(source)}` | "
        f"`{source['peer_review_status']}` | `{relation_display(source)}` |"
    )


def conflict_line(conflict: dict[str, Any]) -> str:
    return (
        f"- **`{conflict['conflict_id']}` {conflict['topic']}**: "
        f"{conflict['historical_definition']} Current 3.0: "
        f"{conflict['current_definition']} Resolution: `{conflict['resolution']}`."
    )


def result_line(result: dict[str, Any]) -> str:
    return f"- `{result['result_id']}` **{result['result_class']}**: {result['title']}"


def inheritance_block(item: dict[str, Any]) -> str:
    source_text = ", ".join(f"`{source_id}`" for source_id in item["source_ids"])
    mapping_text = ", ".join(f"`{mapping}`" for mapping in item["uft_mapping"])
    return "\n".join(
        [
            f"### {item['inheritance_id']} {item['name']}",
            f"Claim class: `{item['claim_class']}`. Sources: {source_text}.",
            f"UFT mapping: {mapping_text}.",
            f"Preserved: {'; '.join(item['preserved_structure'])}.",
            f"Not inherited: {'; '.join(item['not_inherited'])}.",
            f"Prohibited inference: {item['prohibited_inference']}",
        ]
    )


def validate_human_sync(
    human: str,
    sources: dict[str, Any],
    conflicts: dict[str, Any],
    results: dict[str, Any],
    inheritance: dict[str, Any],
    errors: list[str],
) -> None:
    for source in sources["sources"]:
        if source_row(source) not in human:
            errors.append(f"human source row out of sync: {source['source_id']}")
    human_source_rows = re.findall(r"^\| `(?:UFT-HIST|UFT-METH)-\d{3}` .*$", human, flags=re.MULTILINE)
    if len(human_source_rows) != len(sources["sources"]):
        errors.append("human source table row count does not match machine source registry")

    for conflict in conflicts["conflicts"]:
        if conflict_line(conflict) not in human:
            errors.append(f"human conflict entry out of sync: {conflict['conflict_id']}")
    human_conflict_rows = re.findall(r"^- \*\*`HDC-\d{3}` .*$", human, flags=re.MULTILINE)
    if len(human_conflict_rows) != len(conflicts["conflicts"]):
        errors.append("human conflict entry count does not match machine conflict registry")

    for result in results["results"]:
        if result_line(result) not in human:
            errors.append(f"human result entry out of sync: {result['result_id']}")
    human_result_rows = re.findall(r"^- `HIST-R\d{2}` \*\*.*$", human, flags=re.MULTILINE)
    if len(human_result_rows) != len(results["results"]):
        errors.append("human result entry count does not match machine result registry")

    for item in inheritance["imports"]:
        if inheritance_block(item) not in human:
            errors.append(f"human inheritance entry out of sync: {item['inheritance_id']}")
    human_inheritance_heads = re.findall(r"^### INH-\d{2} .*$", human, flags=re.MULTILINE)
    if len(human_inheritance_heads) != len(inheritance["imports"]):
        errors.append("human inheritance entry count does not match machine inheritance registry")


def validate_documents(
    contract: dict[str, Any],
    sources: dict[str, Any],
    symbols: dict[str, Any],
    conflicts: dict[str, Any],
    results: dict[str, Any],
    inheritance: dict[str, Any],
    human: str,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    errors: list[str] = []

    if contract.get("type") != "uft-id-historical-lineage-contract" or contract.get("schema_version") != "1.0.0":
        errors.append("contract type/schema mismatch")
    snapshot_date = contract.get("snapshot_date")
    if not isinstance(snapshot_date, str) or ISO_DATE.fullmatch(snapshot_date) is None:
        errors.append("contract snapshot_date must be YYYY-MM-DD")
    if set(contract.get("required_platform_families", [])) != REQ_PLAT:
        errors.append("contract platform families mismatch")
    if set(contract.get("result_classes", [])) != RESULT_CLASSES:
        errors.append("contract result classes mismatch")

    hard_rules = contract.get("hard_rules")
    if not isinstance(hard_rules, dict):
        errors.append("contract hard_rules must be an object")
    else:
        if set(hard_rules) != EXPECTED_HARD_RULES:
            errors.append("contract hard-rule key set mismatch")
        if any(value is not False for value in hard_rules.values()):
            errors.append("contract hard rules must all be false")

    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("contract authorities mapping mismatch")
    for key, rel in EXPECTED_AUTHORITIES.items():
        if not (root / rel).is_file():
            errors.append(f"contract authority missing: {key} -> {rel}")

    documents = {
        "sources": sources,
        "symbols": symbols,
        "conflicts": conflicts,
        "results": results,
        "inheritance": inheritance,
    }
    for name, document in documents.items():
        expected_type, expected_schema = AUTHORITY_META[name]
        if document.get("type") != expected_type:
            errors.append(f"{name} authority type mismatch")
        if document.get("schema_version") != expected_schema:
            errors.append(f"{name} authority schema_version mismatch")
        if document.get("snapshot_date") != snapshot_date:
            errors.append(f"{name} authority snapshot_date mismatch")

    completeness = sources.get("completeness_contract")
    if not isinstance(completeness, dict):
        errors.append("source completeness_contract must be an object")
        completeness = {}
    if not ne(completeness.get("meaning")):
        errors.append("source completeness_contract.meaning required")
    string_list(completeness.get("does_not_mean"), "source completeness_contract.does_not_mean", errors, nonempty=True)
    if set(completeness.get("required_platform_families", [])) != REQ_PLAT:
        errors.append("source required platform families mismatch")
    coverage = completeness.get("platform_coverage", [])
    coverage_names: list[str] = []
    if not isinstance(coverage, list):
        errors.append("source platform_coverage must be a list")
        coverage = []
    for index, record in enumerate(coverage):
        if not isinstance(record, dict):
            errors.append(f"platform_coverage[{index}] must be an object")
            continue
        platform = record.get("platform")
        coverage_names.append(platform)
        if platform not in REQ_PLAT:
            errors.append(f"platform_coverage[{index}].platform invalid")
        if not ne(record.get("basis")) or not ne(record.get("status")):
            errors.append(f"platform_coverage[{index}] requires basis and status")
    if set(coverage_names) != REQ_PLAT or len(coverage_names) != len(REQ_PLAT):
        errors.append("platform coverage must contain all six families exactly once")

    source_records = sources.get("sources")
    if not isinstance(source_records, list) or not source_records:
        errors.append("sources.sources must be a non-empty list")
        source_records = []

    source_ids: set[str] = set()
    historical_ids: set[str] = set()
    doi_owner: dict[str, str] = {}

    for index, source in enumerate(source_records):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be object")
            continue
        required_keys = {
            "source_id", "source_family", "title", "authors", "doi", "date",
            "date_kind", "version", "license", "peer_review_status",
            "repository_release_relation", "manifestations",
        }
        missing_keys = required_keys - set(source)
        if missing_keys:
            errors.append(f"{label} missing provenance keys: {sorted(missing_keys)}")

        source_id = source.get("source_id")
        if not ne(source_id):
            errors.append(f"{label}.source_id required")
            continue
        if source_id in source_ids:
            errors.append(f"duplicate source_id {source_id}")
        source_ids.add(source_id)

        family = source.get("source_family")
        if not ne(family):
            errors.append(f"{source_id}.source_family required")
            family = ""
        if family in HISTORICAL_SOURCE_FAMILIES:
            historical_ids.add(source_id)
            if HIST_ID.fullmatch(source_id) is None:
                errors.append(f"{source_id} historical source_id must match UFT-HIST-NNN")
        elif family in METHOD_SOURCE_FAMILIES:
            if METH_ID.fullmatch(source_id) is None:
                errors.append(f"{source_id} methodological source_id must match UFT-METH-NNN")
        else:
            errors.append(f"{source_id}.source_family unsupported: {family}")

        if not ne(source.get("title")):
            errors.append(f"{source_id}.title required")
        string_list(source.get("authors"), f"{source_id}.authors", errors, nonempty=True)
        date = source.get("date")
        if date is not None and (not isinstance(date, str) or ISO_DATE.fullmatch(date) is None):
            errors.append(f"{source_id}.date must be null or YYYY-MM-DD")
        if not ne(source.get("date_kind")):
            errors.append(f"{source_id}.date_kind required")
        version = source.get("version")
        if version is not None and not ne(version):
            errors.append(f"{source_id}.version must be null or non-empty string")

        doi = source.get("doi")
        if doi is not None:
            if not isinstance(doi, str) or DOI.fullmatch(doi) is None:
                errors.append(f"{source_id}.doi invalid")
            else:
                normalized_doi = doi.strip().lower()
                other = doi_owner.get(normalized_doi)
                if other is not None and other != source_id:
                    errors.append(f"DOI collision {doi}: {other} and {source_id}")
                else:
                    doi_owner[normalized_doi] = source_id

        license_record = source.get("license")
        if not isinstance(license_record, dict) or "value" not in license_record or not ne(license_record.get("status")):
            errors.append(f"{source_id}.license invalid")
        elif license_record.get("value") is not None and not ne(license_record.get("value")):
            errors.append(f"{source_id}.license.value must be null or non-empty string")
        if not ne(source.get("peer_review_status")):
            errors.append(f"{source_id}.peer_review_status required")

        relation = source.get("repository_release_relation")
        if relation is not None:
            if not isinstance(relation, dict) or not ne(relation.get("relation")):
                errors.append(f"{source_id}.repository_release_relation invalid")
            else:
                for field in ("repository", "release"):
                    if field in relation and relation[field] is not None and not ne(relation[field]):
                        errors.append(f"{source_id}.repository_release_relation.{field} invalid")

        manifestations = source.get("manifestations")
        if not isinstance(manifestations, list) or not manifestations:
            errors.append(f"{source_id}.manifestations required")
            continue
        for manifestation_index, manifestation in enumerate(manifestations):
            manifestation_label = f"{source_id}.manifestations[{manifestation_index}]"
            if not isinstance(manifestation, dict):
                errors.append(f"{manifestation_label} must be object")
                continue
            platform = manifestation.get("platform")
            if platform not in REQ_PLAT:
                errors.append(f"{manifestation_label}.platform invalid")
            for field in ("locator", "role", "status"):
                if not ne(manifestation.get(field)):
                    errors.append(f"{manifestation_label}.{field} required")
            locator = str(manifestation.get("locator", ""))
            if "gmail:" in locator or "docs.google.com" in locator or "drive.google.com" in locator or locator.startswith("gdrive:"):
                errors.append(f"{manifestation_label} leaks private connector identifier")
            if isinstance(manifestation.get("receipt_id"), str) and manifestation["receipt_id"].startswith("gmail:"):
                errors.append(f"{manifestation_label} leaks private Gmail receipt id")
            if manifestation.get("hash") is not None:
                validate_hash(manifestation["hash"], f"{manifestation_label}.hash", errors)
            if platform == "github":
                blob_sha = manifestation.get("blob_sha")
                if manifestation.get("ref") != "main" or not isinstance(blob_sha, str) or H40.fullmatch(blob_sha) is None:
                    errors.append(f"{manifestation_label} invalid merged-main blob pin")
                if isinstance(manifestation.get("hash"), dict) and manifestation["hash"].get("value") != blob_sha:
                    errors.append(f"{manifestation_label} hash/blob mismatch")
            if platform == "google-drive":
                if manifestation.get("private_locator_redacted") is not True:
                    errors.append(f"{manifestation_label} Drive locator must be redacted")
                if manifestation.get("hash") is not None and manifestation.get("native_hash_available") is not False:
                    errors.append(f"{manifestation_label} export hash must not pose as native cloud hash")

    symbol_records = symbols.get("symbols")
    if not isinstance(symbol_records, list):
        errors.append("symbols.symbols must be a list")
        symbol_records = []
    seen_symbols: set[str] = set()
    valid_dispositions = {"mapped", "mapped-with-semantic-narrowing", "mapped-as-specialization", "superseded", "symbol-conflict"}
    for index, symbol in enumerate(symbol_records):
        historical_symbol = symbol.get("historical_symbol") if isinstance(symbol, dict) else None
        if not ne(historical_symbol):
            errors.append(f"symbols[{index}].historical_symbol required")
            continue
        if historical_symbol in seen_symbols:
            errors.append(f"duplicate historical symbol {historical_symbol}")
        seen_symbols.add(historical_symbol)
        source_refs = string_list(symbol.get("source_ids"), f"{historical_symbol}.source_ids", errors, nonempty=True)
        if set(source_refs) - source_ids:
            errors.append(f"{historical_symbol} has unknown source ids")
        if symbol.get("disposition") not in valid_dispositions:
            errors.append(f"{historical_symbol} invalid disposition")
        if symbol.get("disposition") != "superseded" and not ne(symbol.get("canonical_target")):
            errors.append(f"{historical_symbol} canonical_target required")
        if not ne(symbol.get("historical_meaning")):
            errors.append(f"{historical_symbol}.historical_meaning required")
        string_list(symbol.get("preserved_structure"), f"{historical_symbol}.preserved_structure", errors, nonempty=True)
        string_list(symbol.get("not_inherited"), f"{historical_symbol}.not_inherited", errors, nonempty=True)
        string_list(symbol.get("notes"), f"{historical_symbol}.notes", errors)

    conflict_records = conflicts.get("conflicts")
    if not isinstance(conflict_records, list):
        errors.append("conflicts.conflicts must be a list")
        conflict_records = []
    conflict_ids: set[str] = set()
    for index, conflict in enumerate(conflict_records):
        if not isinstance(conflict, dict):
            errors.append(f"conflicts[{index}] must be object")
            continue
        conflict_id = conflict.get("conflict_id")
        if not ne(conflict_id):
            errors.append(f"conflicts[{index}].conflict_id required")
            continue
        if conflict_id in conflict_ids:
            errors.append(f"duplicate conflict {conflict_id}")
        conflict_ids.add(conflict_id)
        refs = string_list(conflict.get("source_ids"), f"{conflict_id}.source_ids", errors, nonempty=True)
        if set(refs) - source_ids:
            errors.append(f"{conflict_id} has unknown source ids")
        for field in ("topic", "historical_definition", "current_definition", "impact", "prohibited_reconciliation"):
            if not ne(conflict.get(field)):
                errors.append(f"{conflict_id}.{field} required")
        if conflict.get("resolution") != "do-not-reconcile-silently":
            errors.append(f"{conflict_id} must remain do-not-reconcile-silently")

    result_records = results.get("results")
    if not isinstance(result_records, list):
        errors.append("results.results must be a list")
        result_records = []
    covered_historical_ids: set[str] = set()
    result_ids: set[str] = set()
    for index, result in enumerate(result_records):
        if not isinstance(result, dict):
            errors.append(f"results[{index}] must be object")
            continue
        result_id = result.get("result_id")
        if not ne(result_id):
            errors.append(f"results[{index}].result_id required")
            continue
        if result_id in result_ids:
            errors.append(f"duplicate result {result_id}")
        result_ids.add(result_id)
        for field in ("title", "summary", "status"):
            if not ne(result.get(field)):
                errors.append(f"{result_id}.{field} required")
        result_class = result.get("result_class")
        if result_class not in RESULT_CLASSES:
            errors.append(f"{result_id} invalid result class")
        refs = string_list(result.get("source_ids"), f"{result_id}.source_ids", errors, nonempty=True)
        if set(refs) - source_ids:
            errors.append(f"{result_id} has unknown source ids")
        covered_historical_ids.update(set(refs) & historical_ids)
        preserved = string_list(result.get("preserved_for_uft3"), f"{result_id}.preserved_for_uft3", errors)
        not_inherited = string_list(result.get("not_inherited"), f"{result_id}.not_inherited", errors)
        if result_class in {"interpretive", "speculative"} and not not_inherited:
            errors.append(f"{result_id} interpretive/speculative result requires non-empty not_inherited")
        evidence_paths = validate_repo_paths(result.get("evidence_paths"), f"{result_id}.evidence_paths", errors, root=root, nonempty=result_class == "empirical")
        if result_class == "empirical" and not evidence_paths:
            errors.append(f"{result_id} empirical result requires retained repository evidence")
        if result_class in {"formal", "computational"} and not preserved and not not_inherited:
            errors.append(f"{result_id} must state preserved or non-inherited structure")

    missing_historical_coverage = historical_ids - covered_historical_ids
    if missing_historical_coverage:
        errors.append(f"historical sources lack classified-result coverage: {sorted(missing_historical_coverage)}")

    canonical_ids = canonical_uft_ids(root)
    import_records = inheritance.get("imports")
    if not isinstance(import_records, list):
        errors.append("inheritance.imports must be a list")
        import_records = []
    inheritance_ids: set[str] = set()
    for index, item in enumerate(import_records):
        if not isinstance(item, dict):
            errors.append(f"imports[{index}] must be object")
            continue
        inheritance_id = item.get("inheritance_id")
        if not ne(inheritance_id):
            errors.append(f"imports[{index}].inheritance_id required")
            continue
        if inheritance_id in inheritance_ids:
            errors.append(f"duplicate inheritance_id {inheritance_id}")
        inheritance_ids.add(inheritance_id)
        if not ne(item.get("name")):
            errors.append(f"{inheritance_id}.name required")
        if item.get("claim_class") not in CLAIM_CLASSES:
            errors.append(f"{inheritance_id} requires exactly one valid claim_class")
        refs = string_list(item.get("source_ids"), f"{inheritance_id}.source_ids", errors, nonempty=True)
        if set(refs) - source_ids:
            errors.append(f"{inheritance_id} has unknown source ids")
        string_list(item.get("preserved_structure"), f"{inheritance_id}.preserved_structure", errors, nonempty=True)
        string_list(item.get("not_inherited"), f"{inheritance_id}.not_inherited", errors, nonempty=True)
        if not ne(item.get("prohibited_inference")):
            errors.append(f"{inheritance_id}.prohibited_inference required")
        if not ne(item.get("reason_for_reuse")):
            errors.append(f"{inheritance_id}.reason_for_reuse required")
        mappings = string_list(item.get("uft_mapping"), f"{inheritance_id}.uft_mapping", errors, nonempty=True)
        for mapping in mappings:
            if CANONICAL_ID.fullmatch(mapping) is None:
                errors.append(f"{inheritance_id}.uft_mapping malformed canonical id: {mapping}")
            elif mapping not in canonical_ids:
                errors.append(f"{inheritance_id}.uft_mapping unknown canonical id: {mapping}")

    expected_inheritance_ids = {f"INH-{index:02d}" for index in range(1, 8)}
    if inheritance_ids != expected_inheritance_ids or len(import_records) != len(expected_inheritance_ids):
        errors.append("inheritance registry must contain INH-01 through INH-07 exactly once")

    validate_human_sync(human, sources, conflicts, results, inheritance, errors)

    ok = not errors
    return {
        "status": "ok" if ok else "error",
        "errors": errors,
        "source_count": len(source_ids),
        "historical_source_count": len(historical_ids),
        "symbol_count": len(seen_symbols),
        "conflict_count": len(conflict_ids),
        "result_count": len(result_ids),
        "inheritance_count": len(inheritance_ids),
        "platforms": sorted(REQ_PLAT),
        "exit_criterion_met": ok and not missing_historical_coverage and inheritance_ids == expected_inheritance_ids,
    }


def validate() -> dict[str, Any]:
    missing = [name for name, path in P.items() if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing {name}: {P[name].relative_to(ROOT)}" for name in missing],
            "exit_criterion_met": False,
        }
    docs = load_documents()
    return validate_documents(
        docs["contract"], docs["sources"], docs["symbols"], docs["conflicts"],
        docs["results"], docs["inheritance"], docs["human"],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("historical lineage: " + result["status"])
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
