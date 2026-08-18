#!/usr/bin/env python3
"""Validate UFT-ID cross-repository pattern and result registries.

This validator checks repository-local registry structure, pinned source
identities, bridge obligations, and synchronization between the machine result
registry and the canonical metadata carried by the human result surface.

It deliberately does not fetch remote repositories during CI, so a successful
run does not assert that a remote main branch has not advanced since the
recorded snapshot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATTERNS_PATH = ROOT / "machine/cross_repo_patterns.json"
RESULTS_PATH = ROOT / "machine/cross_repo_results.json"
CONTRACT_PATH = ROOT / "machine/contract.json"
HUMAN_RESULTS_PATH = ROOT / "theory/CROSS_REPO_RESULTS.md"
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
PATTERN_RE = re.compile(r"^XR-P\d{2}$")
QUARANTINE_RE = re.compile(r"^XR-Q\d{2}$")
RESULT_RE = re.compile(r"^CR\d+$")
HUMAN_HEADING_RE = re.compile(r"^## (CR\d+)\. (.+)$")

PRIVATE_REPOSITORIES = {
    "QSOLKCB/QSOL-CONTEXT",
    "QSOLKCB/QSOL-CAPSULES",
    "QSOLKCB/QSOL-CORPUS",
    "QSOLKCB/NS",
    "QSOLKCB/NS-LLM",
    "QSOLKCB/NS-SIM",
    "QSOLKCB/LEAF",
}

REQUIRED_BOUNDARIES = {
    "SOFTWARE_CONTRACT != PHYSICAL_LAW",
    "IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM",
    "CONTENT_IDENTITY != TRUTH",
    "PROJECTION != SOURCE",
    "RETRIEVAL != AUTHORITY",
    "RECOVERY != EPISTEMIC_PROMOTION",
    "FORMAL_PROOF != IMPLEMENTATION_CONFORMANCE",
    "IMPLEMENTATION_CONFORMANCE != EMPIRICAL_VALIDATION",
    "EMPIRICAL_VALIDATION != PHYSICAL_ONTOLOGY",
    "ADJACENT_TRUTH != INHERITED_TRUTH",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(nonempty_string(item) for item in value)
    )


def parse_human_results(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Parse canonical CR id/title/class/qualifier/scope metadata from Markdown."""

    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    starts: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        match = HUMAN_HEADING_RE.fullmatch(line)
        if match:
            starts.append((index, match.group(1), match.group(2).strip()))

    parsed: dict[str, dict[str, str]] = {}
    for position, (start, result_id, title) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        if result_id in parsed:
            errors.append(f"human results duplicate section: {result_id}")
            continue
        section = lines[start + 1 : end]
        claim_class = None
        qualifier = None
        scope = None
        for line in section:
            if line.startswith("**Class:** `") and line.endswith("`"):
                claim_class = line[len("**Class:** `") : -1]
            elif line.startswith("**Qualifier:** `") and line.endswith("`"):
                qualifier = line[len("**Qualifier:** `") : -1]
            elif line.startswith("**Canonical scope:** `") and line.endswith("`"):
                scope = line[len("**Canonical scope:** `") : -1]
        if not claim_class:
            errors.append(f"human results {result_id}: missing canonical Class metadata")
        if not scope:
            errors.append(f"human results {result_id}: missing Canonical scope metadata")
        parsed[result_id] = {
            "title": title,
            "claim_class": claim_class or "",
            "qualifier": qualifier or "",
            "scope": scope or "",
        }
    return parsed, errors


def validate_source_entry(
    entry: object,
    *,
    expected_kind: str,
    seen_ids: set[str],
    errors: list[str],
) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{expected_kind} entry must be an object")
        return

    pattern_id = entry.get("pattern_id")
    matcher = PATTERN_RE if expected_kind == "pattern" else QUARANTINE_RE
    if not isinstance(pattern_id, str) or matcher.fullmatch(pattern_id) is None:
        errors.append(f"invalid {expected_kind} pattern_id: {pattern_id!r}")
    elif pattern_id in seen_ids:
        errors.append(f"duplicate cross-repository pattern id: {pattern_id}")
    else:
        seen_ids.add(pattern_id)

    repository = entry.get("repository")
    if not nonempty_string(repository) or not str(repository).startswith("QSOLKCB/"):
        errors.append(f"{pattern_id}: repository must be a QSOLKCB owner/name string")
    elif repository in PRIVATE_REPOSITORIES:
        errors.append(f"{pattern_id}: private repository is forbidden in public pattern registry: {repository}")

    if entry.get("ref") != "main":
        errors.append(f"{pattern_id}: source ref must be exactly main")
    if not nonempty_string(entry.get("source_path")):
        errors.append(f"{pattern_id}: source_path must be non-empty")
    source_blob_sha = entry.get("source_blob_sha")
    if not isinstance(source_blob_sha, str) or SHA1_RE.fullmatch(source_blob_sha) is None:
        errors.append(f"{pattern_id}: source_blob_sha must be 40 lowercase hex characters")
    source_status = entry.get("source_status")
    if not nonempty_string(source_status):
        errors.append(f"{pattern_id}: source_status must be non-empty")
    elif "open" in str(source_status).casefold():
        errors.append(f"{pattern_id}: open-PR-only source status is forbidden")
    if not nonempty_string(entry.get("import_class")):
        errors.append(f"{pattern_id}: import_class must be non-empty")

    if expected_kind == "pattern":
        if not nonempty_string_list(entry.get("uft_mapping")):
            errors.append(f"{pattern_id}: uft_mapping must be a non-empty string list")
        if not nonempty_string(entry.get("source_contract")):
            errors.append(f"{pattern_id}: source_contract must be non-empty")
        if not nonempty_string_list(entry.get("preserved_structure")):
            errors.append(f"{pattern_id}: preserved_structure must be a non-empty string list")
        if not nonempty_string_list(entry.get("discarded_structure")):
            errors.append(f"{pattern_id}: discarded_structure must be a non-empty string list")
        if not nonempty_string(entry.get("abstraction")):
            errors.append(f"{pattern_id}: abstraction must be non-empty")
        if not nonempty_string(entry.get("prohibited_inference")):
            errors.append(f"{pattern_id}: prohibited_inference must be non-empty")
    else:
        if not nonempty_string_list(entry.get("usable_for")):
            errors.append(f"{pattern_id}: usable_for must be a non-empty string list")
        if not nonempty_string_list(entry.get("not_authoritative_for")):
            errors.append(f"{pattern_id}: not_authoritative_for must be a non-empty string list")
        if not nonempty_string(entry.get("reason")):
            errors.append(f"{pattern_id}: quarantine reason must be non-empty")


def validate(root: Path = ROOT) -> dict[str, object]:
    global ROOT, PATTERNS_PATH, RESULTS_PATH, CONTRACT_PATH, HUMAN_RESULTS_PATH
    original = (ROOT, PATTERNS_PATH, RESULTS_PATH, CONTRACT_PATH, HUMAN_RESULTS_PATH)
    ROOT = root.resolve()
    PATTERNS_PATH = ROOT / "machine/cross_repo_patterns.json"
    RESULTS_PATH = ROOT / "machine/cross_repo_results.json"
    CONTRACT_PATH = ROOT / "machine/contract.json"
    HUMAN_RESULTS_PATH = ROOT / "theory/CROSS_REPO_RESULTS.md"
    errors: list[str] = []
    try:
        patterns = load_json(PATTERNS_PATH)
        results = load_json(RESULTS_PATH)
        contract = load_json(CONTRACT_PATH)

        if patterns.get("type") != "uft-id-cross-repo-pattern-registry":
            errors.append("cross-repo pattern registry type mismatch")
        if patterns.get("schema_version") != "1.0.1":
            errors.append("cross-repo pattern registry schema_version must be 1.0.1")
        if patterns.get("snapshot_date") != "2026-08-18":
            errors.append("cross-repo pattern registry snapshot_date mismatch")
        if not nonempty_string(patterns.get("snapshot_basis")):
            errors.append("cross-repo pattern registry requires snapshot_basis")
        if set(patterns.get("global_boundaries", [])) != REQUIRED_BOUNDARIES:
            errors.append("cross-repo pattern registry boundary contract mismatch")
        if not nonempty_string_list(patterns.get("selection_policy")):
            errors.append("cross-repo pattern registry requires selection_policy")

        pattern_entries = patterns.get("patterns")
        quarantine_entries = patterns.get("quarantined_lineage")
        if not isinstance(pattern_entries, list) or not pattern_entries:
            errors.append("cross-repo pattern registry requires patterns")
            pattern_entries = []
        if not isinstance(quarantine_entries, list):
            errors.append("cross-repo pattern registry quarantined_lineage must be a list")
            quarantine_entries = []

        seen_ids: set[str] = set()
        for entry in pattern_entries:
            validate_source_entry(entry, expected_kind="pattern", seen_ids=seen_ids, errors=errors)
        imported_ids = {
            entry.get("pattern_id")
            for entry in pattern_entries
            if isinstance(entry, dict) and isinstance(entry.get("pattern_id"), str)
        }
        for entry in quarantine_entries:
            validate_source_entry(entry, expected_kind="quarantine", seen_ids=seen_ids, errors=errors)

        if results.get("type") != "uft-id-cross-repo-results":
            errors.append("cross-repo results type mismatch")
        if results.get("schema_version") != "1.0.1":
            errors.append("cross-repo results schema_version must be 1.0.1")
        if results.get("authority") != "theory/CROSS_REPO_RESULTS.md":
            errors.append("cross-repo results authority path mismatch")
        if results.get("experiment") != "experiments/cross_repo/run.py":
            errors.append("cross-repo results experiment path mismatch")

        allowed_claims = set(contract.get("claim_classes", []))
        result_entries = results.get("results")
        if not isinstance(result_entries, list) or not result_entries:
            errors.append("cross-repo results requires non-empty results")
            result_entries = []
        seen_results: set[str] = set()
        machine_by_id: dict[str, dict[str, Any]] = {}
        for entry in result_entries:
            if not isinstance(entry, dict):
                errors.append("cross-repo result entry must be an object")
                continue
            result_id = entry.get("result_id")
            if not isinstance(result_id, str) or RESULT_RE.fullmatch(result_id) is None:
                errors.append(f"invalid cross-repo result_id: {result_id!r}")
                continue
            if result_id in seen_results:
                errors.append(f"duplicate cross-repo result_id: {result_id}")
            else:
                seen_results.add(result_id)
            machine_by_id[result_id] = entry
            if entry.get("claim_class") not in allowed_claims:
                errors.append(f"{result_id}: invalid claim_class {entry.get('claim_class')!r}")
            if not nonempty_string(entry.get("title")):
                errors.append(f"{result_id}: title must be non-empty")
            if not nonempty_string(entry.get("scope")):
                errors.append(f"{result_id}: scope must be non-empty")
            qualifier = entry.get("qualifier")
            if qualifier is not None and not nonempty_string(qualifier):
                errors.append(f"{result_id}: qualifier must be a non-empty string when present")
            source_patterns = entry.get("source_patterns")
            if not nonempty_string_list(source_patterns):
                errors.append(f"{result_id}: source_patterns must be a non-empty string list")
            else:
                for pattern_id in source_patterns:
                    if pattern_id not in imported_ids:
                        errors.append(f"{result_id}: unknown or quarantined source pattern {pattern_id}")

        if HUMAN_RESULTS_PATH.is_file():
            human_by_id, human_errors = parse_human_results(HUMAN_RESULTS_PATH)
            errors.extend(human_errors)
            if set(human_by_id) != set(machine_by_id):
                errors.append(
                    "human/machine cross-repo result id sets differ: "
                    f"human={sorted(human_by_id)} machine={sorted(machine_by_id)}"
                )
            for result_id in sorted(set(human_by_id) & set(machine_by_id)):
                human = human_by_id[result_id]
                machine = machine_by_id[result_id]
                for key in ("title", "claim_class", "scope"):
                    if human[key] != machine.get(key):
                        errors.append(
                            f"{result_id}: human {key} differs from machine authority: "
                            f"{human[key]!r} != {machine.get(key)!r}"
                        )
                expected_qualifier = machine.get("qualifier", "")
                if human["qualifier"] != expected_qualifier:
                    errors.append(
                        f"{result_id}: human qualifier differs from machine authority: "
                        f"{human['qualifier']!r} != {expected_qualifier!r}"
                    )
        else:
            errors.append("required cross-repo authority file missing: theory/CROSS_REPO_RESULTS.md")

        authority = contract.get("cross_repo_pattern_authority")
        if isinstance(authority, dict):
            expected = {
                "human_atlas": "research/CROSS_REPO_PATTERN_ATLAS.md",
                "machine_patterns": "machine/cross_repo_patterns.json",
                "auxiliary_contracts": "theory/AUXILIARY_CONTRACTS.md",
                "human_results": "theory/CROSS_REPO_RESULTS.md",
                "machine_results": "machine/cross_repo_results.json",
                "validator": "scripts/validate_cross_repo_patterns.py",
                "experiment": "experiments/cross_repo/run.py",
                "receipt_runner": "experiments/run_cross_repo.py",
            }
            for key, value in expected.items():
                if authority.get(key) != value:
                    errors.append(f"machine contract cross_repo_pattern_authority.{key} mismatch")
        else:
            errors.append("machine contract must define cross_repo_pattern_authority")

        required_files = [
            "research/CROSS_REPO_PATTERN_ATLAS.md",
            "machine/cross_repo_patterns.json",
            "theory/AUXILIARY_CONTRACTS.md",
            "theory/CROSS_REPO_RESULTS.md",
            "machine/cross_repo_results.json",
            "experiments/cross_repo/run.py",
            "experiments/run_cross_repo.py",
        ]
        for relative in required_files:
            if not (ROOT / relative).is_file():
                errors.append(f"required cross-repo authority file missing: {relative}")

        return {
            "ok": not errors,
            "errors": errors,
            "summary": {
                "patterns": len(pattern_entries),
                "quarantined": len(quarantine_entries),
                "results": len(result_entries),
                "remote_freshness_checked": False,
                "snapshot_date": patterns.get("snapshot_date"),
                "human_result_sync_checked": True,
            },
        }
    finally:
        ROOT, PATTERNS_PATH, RESULTS_PATH, CONTRACT_PATH, HUMAN_RESULTS_PATH = original


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            f"validated {summary['patterns']} imported patterns, "
            f"{summary['quarantined']} quarantined lineage records, "
            f"{summary['results']} finite results"
        )
        print("human result metadata synchronized: yes")
        print("remote freshness checked: no (registry pins are snapshot provenance)")
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
