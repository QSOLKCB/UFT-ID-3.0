#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID PR #12 BridgeCore authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/bridge_core_contract.json",
    "results": ROOT / "machine/bridge_core_results.json",
    "human": ROOT / "theory/BRIDGE_CORE.md",
    "roadmap_state": ROOT / "machine/roadmap_state.json",
    "auxiliary": ROOT / "theory/AUXILIARY_CONTRACTS.md",
    "experiment": ROOT / "experiments/bridge_core/run.py",
    "tests": ROOT / "tests/test_bridge_core.py",
    "receipt": ROOT / "experiments/run_bridge_core.py",
}

EXPECTED_BLOBS = {
    "contract": "cd5f7c2bceba255a7f75df062075f792f89db816",
    "results": "b52e5e2a4bfba44a1cc292bd7adf2929ca455d8a",
    "human": "c68269736f31dabfc4a327f6467719e2575f30ec",
}
EXPECTED_PRIMARY_TYPE = (
    "BridgeSpec=(source_type,target_type,domain,map_or_relation,preserved_structure,"
    "lost_structure,scope,source_version,target_version)"
)
EXPECTED_FIELD_KEYS = {
    "source_type", "target_type", "domain", "map_or_relation", "preserved_structure",
    "lost_structure", "scope", "source_version", "target_version",
}
EXPECTED_COMPOSITION = {
    "intermediate_type_match": "B1.target_type = B2.source_type",
    "intermediate_version_match": "B1.target_version = B2.source_version",
    "domain_coverage": "every B1 intermediate output used by the composition lies in B2.domain",
    "scope_rule": "scope(B2 o B1) = scope(B1) intersect scope(B2), and the intersection must be nonempty",
    "relation_rule": "R_21(x,z) iff there exists y with R_1(x,y) and R_2(y,z)",
    "preservation_rule": "P_21 = P_1 intersect P_2",
    "loss_rule": "L_21 = L_1 union (P_1 minus P_2)",
    "loss_monotonicity": "once a source structure is lost by B1, ordinary BridgeCore composition does not restore it automatically",
}
EXPECTED_BOUNDARIES = {
    "BRIDGE != IDENTITY",
    "TRANSPORT != EQUIVALENCE",
    "PRESERVED_STRUCTURE != ALL_STRUCTURE",
    "LOSSY_BRIDGE != INVERTIBLE_BRIDGE",
    "COMPOSABLE_TYPES != SEMANTIC_EQUIVALENCE",
    "VERSION_COMPATIBLE != CONTENT_IDENTICAL",
    "SAME_ENDPOINT_TYPES != SAME_BRIDGE",
    "INTEGER_OR_LABEL_MATCH != STRUCTURAL_BRIDGE",
    "STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION",
    "BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/BRIDGE_CORE.md",
    "results": "machine/bridge_core_results.json",
    "validator": "scripts/validate_bridge_core.py",
    "experiment": "experiments/bridge_core/run.py",
    "tests": "tests/test_bridge_core.py",
    "receipt": "experiments/run_bridge_core.py",
    "roadmap_state": "machine/roadmap_state.json",
}
EXPECTED_RESULT_BINDINGS = {
    "UFT-BR-001": (
        "PROVED",
        "If B1 and B2 have matching intermediate type and version, nonempty scope intersection, and every intermediate output of B1 lies in the domain of B2, then their ordinary relational composite is a well-defined bridge from the source of B1 to the target of B2.",
        "theory/BRIDGE_CORE.md#uft-br-001-typed-relational-composition",
    ),
    "UFT-BR-002": (
        "PROVED",
        "Under the BridgeCore conservative composition contract, the structure automatically preserved by B2 o B1 is exactly P1 intersect P2.",
        "theory/BRIDGE_CORE.md#uft-br-002-preservation-intersection",
    ),
    "UFT-BR-003": (
        "PROVED",
        "For the conservative composite L21 = L1 union (P1 minus P2), every structure already lost by B1 remains lost in B2 o B1, and every structure preserved by B1 but not B2 becomes lost in the composite.",
        "theory/BRIDGE_CORE.md#uft-br-003-loss-monotonicity",
    ),
    "UFT-BR-004": (
        "PROVED",
        "On a fixed type, version, domain, scope, and declared structure vocabulary, the identity bridge composes neutrally with a compatible bridge at both the relation and preservation/loss metadata levels.",
        "theory/BRIDGE_CORE.md#uft-br-004-identity-neutrality",
    ),
    "UFT-BR-005": (
        "PROVED",
        "For three mutually compatible bridges, ordinary relational composition, scope intersection, preservation intersection, and conservative loss propagation are associative.",
        "theory/BRIDGE_CORE.md#uft-br-005-associativity",
    ),
    "CX-BR-001": (
        "COUNTEREXAMPLE",
        "Two bridges with the same source and target type/version can differ in relation, injectivity, and preserved/lost structure.",
        "two-state identity transport versus two-state collapse transport",
    ),
    "CX-BR-002": (
        "COUNTEREXAMPLE",
        "Two individually valid bridges fail the BridgeCore composition predicate when the first target version differs from the second source version.",
        "A@1 -> B@1 followed by B@2 -> C@1",
    ),
    "CX-BR-003": (
        "COUNTEREXAMPLE",
        "Two otherwise type/version/domain-compatible bridges are not composable when their declared scopes have empty intersection.",
        "calibration-A-only bridge followed by calibration-B-only bridge",
    ),
    "CX-BR-004": (
        "COUNTEREXAMPLE",
        "A noninjective bridge followed by a deterministic canonical decoder can produce a total composite while failing to reconstruct distinct source states.",
        "two-bit source -> first-bit projection -> canonical two-bit representative",
    ),
}
EXPECTED_EVIDENCE = ["experiments/bridge_core/run.py", "tests/test_bridge_core.py"]
EXPECTED_DEFERRAL_PREFIXES = (
    "epistemic and authority promotion/demotion rules to PR #13",
    "representation-specific congruence and similarity classes to PR #14",
    "information comparability semantics to PR #15",
)
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images")
PROMOTION_PATTERNS = (
    "bridgecore proves uft-id physics",
    "structural transport establishes physical ontology",
    "bridge composition upgrades evidence authority",
    "type compatibility proves semantic equivalence",
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return None
    index = matches[0]
    match = re.match(r"^(#+)\s", heading)
    if match is None:
        return None
    level = len(match.group(1))
    out = [lines[index]]
    for line in lines[index + 1:]:
        candidate = re.match(r"^(#+)\s", line.strip())
        if candidate is not None and len(candidate.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def metadata_value(section: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    matches = [line.strip()[len(prefix):] for line in section.splitlines() if line.strip().startswith(prefix)]
    return matches[0] if len(matches) == 1 else None


def safe_path(path: object, errors: list[str], label: str) -> None:
    if not isinstance(path, str) or not path:
        errors.append(f"{label} must be a nonempty repository-relative path")
        return
    rel = Path(path)
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
        errors.append(f"{label} does not exist: {path}")


def validate() -> dict[str, object]:
    errors: list[str] = []
    for path in PATHS.values():
        if not path.is_file():
            errors.append(f"missing BridgeCore authority file: {path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    roadmap = load_json(PATHS["roadmap_state"])
    human = PATHS["human"].read_text(encoding="utf-8")
    auxiliary = PATHS["auxiliary"].read_text(encoding="utf-8")

    for name in ("contract", "results", "human"):
        if git_blob_sha(PATHS[name].read_bytes()) != EXPECTED_BLOBS[name]:
            errors.append(f"BridgeCore {name} canonical blob drift")

    if contract.get("type") != "uft-id-bridge-core-contract": errors.append("BridgeCore contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("BridgeCore contract schema drift")
    if contract.get("snapshot_date") != "2026-08-21": errors.append("BridgeCore contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("BridgeCore contract claim class drift")
    if contract.get("primary_type") != EXPECTED_PRIMARY_TYPE: errors.append("BridgeCore primary type drift")
    fields = contract.get("fields")
    if not isinstance(fields, dict) or set(fields) != EXPECTED_FIELD_KEYS: errors.append("BridgeCore field set drift")
    if contract.get("composition_contract") != EXPECTED_COMPOSITION: errors.append("BridgeCore composition contract drift")
    if set(contract.get("hard_boundaries", [])) != EXPECTED_BOUNDARIES: errors.append("BridgeCore hard-boundary set drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES: errors.append("BridgeCore authority registry drift")
    deferrals = contract.get("explicit_deferrals")
    if not isinstance(deferrals, list) or not all(any(str(item).startswith(prefix) for item in deferrals) for prefix in EXPECTED_DEFERRAL_PREFIXES):
        errors.append("BridgeCore explicit deferral surface drift")
    for field, path in EXPECTED_AUTHORITIES.items():
        if field != "roadmap_state":
            safe_path(path, errors, f"BridgeCore authority {field}")

    records = results.get("records")
    if not isinstance(records, list):
        errors.append("BridgeCore results records must be a list")
        records = []
    ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            errors.append("BridgeCore result record must be an object")
            continue
        result_id = record.get("id")
        if not isinstance(result_id, str) or not result_id:
            errors.append("BridgeCore result id malformed")
            continue
        if result_id in ids: errors.append(f"duplicate BridgeCore result id: {result_id}")
        ids.add(result_id)
        expected = EXPECTED_RESULT_BINDINGS.get(result_id)
        if expected is None:
            errors.append(f"unexpected BridgeCore result id: {result_id}")
            continue
        expected_class, expected_statement, expected_third = expected
        if record.get("claim_class") != expected_class: errors.append(f"{result_id} claim class drift")
        if record.get("statement") != expected_statement: errors.append(f"{result_id} statement drift")
        if result_id.startswith("UFT-BR-"):
            if record.get("proof_reference") != expected_third: errors.append(f"{result_id} proof reference drift")
            if record.get("executable_evidence") != EXPECTED_EVIDENCE: errors.append(f"{result_id} executable evidence drift")
            heading = "## " + result_id
            section = next((markdown_section(human, line.strip()) for line in human.splitlines() if line.startswith("## ") and result_id in line), None)
            if section is None: errors.append(f"{result_id} human theorem section missing or duplicated")
            elif metadata_value(section, "Claim class") != "`PROVED`": errors.append(f"{result_id} human theorem claim class drift")
        else:
            if record.get("fixture") != expected_third: errors.append(f"{result_id} fixture drift")
            if record.get("evidence") != EXPECTED_EVIDENCE: errors.append(f"{result_id} counterexample evidence drift")
            section = next((markdown_section(human, line.strip()) for line in human.splitlines() if line.startswith("### ") and result_id in line), None)
            if section is None: errors.append(f"{result_id} human counterexample section missing or duplicated")
            elif metadata_value(section, "Claim class") != "`COUNTEREXAMPLE`": errors.append(f"{result_id} human counterexample claim class drift")
        nonclaims = record.get("nonclaims")
        if not isinstance(nonclaims, list) or not nonclaims or any(not isinstance(x, str) or not x for x in nonclaims):
            errors.append(f"{result_id} nonclaims malformed")

    if ids != set(EXPECTED_RESULT_BINDINGS): errors.append("BridgeCore result identity set drift")
    if results.get("claim_boundary") != "BRIDGE_CONFORMANCE != GENERAL_PROOF != EPISTEMIC_PROMOTION != PHYSICAL_VALIDATION":
        errors.append("BridgeCore result claim boundary drift")

    if roadmap.get("basis_commit") != "a72dab3170e9880ca8bf120766d8547d6cc0110b": errors.append("roadmap basis commit drift")
    if roadmap.get("active_planned_surface") != 12: errors.append("roadmap active surface must be PR #12")
    completed = roadmap.get("completed")
    if not isinstance(completed, list) or 11 not in completed: errors.append("roadmap must mark PR #11 complete")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(11, {}).get("status") != "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b": errors.append("roadmap PR #11 completion state drift")
        if by_pr.get(12, {}).get("status") != "active-implemented-in-current-change": errors.append("roadmap PR #12 active state drift")
        if by_pr.get(13, {}).get("status") != "planned": errors.append("roadmap PR #13 must remain planned")

    if "## A8. Versioned semantic bridge" not in auxiliary: errors.append("A8 versioned semantic bridge precursor missing")
    if "ADJACENT_VERSION != COMPATIBLE_BY_DEFAULT" not in auxiliary: errors.append("A8 version compatibility boundary missing")

    combined = json.dumps(contract, ensure_ascii=False) + json.dumps(results, ensure_ascii=False) + human
    lowered = combined.casefold()
    for pattern in PRIVATE_PATTERNS:
        if pattern in lowered: errors.append(f"BridgeCore authority contains forbidden private locator token: {pattern}")
    for pattern in PROMOTION_PATTERNS:
        if pattern in lowered: errors.append(f"BridgeCore authority contains forbidden promotion: {pattern}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(ids),
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
        print(f"BridgeCore authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
