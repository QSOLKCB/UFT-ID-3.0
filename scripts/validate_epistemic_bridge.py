#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID Epistemic Bridge authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/epistemic_bridge_contract.json",
    "results": ROOT / "machine/epistemic_bridge_results.json",
    "human": ROOT / "theory/EPISTEMIC_BRIDGE.md",
    "roadmap": ROOT / "machine/roadmap_state.json",
    "base_contract": ROOT / "machine/contract.json",
    "claims": ROOT / "docs/CLAIMS.md",
    "readme": ROOT / "README4AI.md",
    "repro": ROOT / "docs/REPRODUCIBILITY.md",
    "experiment": ROOT / "experiments/epistemic_bridge/run.py",
    "tests": ROOT / "tests/test_epistemic_bridge.py",
    "receipt": ROOT / "experiments/run_epistemic_bridge.py",
    "artifact_verifier": ROOT / "scripts/verify_epistemic_bridge_artifacts.py",
    "base_bridge": ROOT / "machine/bridge_core_contract.json",
}

EXPECTED_BOUNDARIES = {
    "STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION",
    "RETRIEVED != VERIFIED",
    "INFERRED != VERIFIED",
    "EXECUTED != VERIFIED",
    "VERIFIED != TRUE",
    "CONFLICT != UNKNOWN",
    "CONFLICT != FALSE",
    "VERIFIED != CONFLICT_FREE",
    "NO_GLOBAL_EPISTEMIC_LATTICE",
    "FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY",
}
EXPECTED_FIELDS = {
    "evidence_refs", "retrieved_refs", "inference_refs", "verification_receipts",
    "execution_receipts", "conflict_refs", "scope",
}
EXPECTED_THEOREMS = {
    "UFT-EP-001": (
        "A licensed authority-neutral BridgeCore transport preserves every epistemic evidence/authority field exactly and may only restrict scope by intersection.",
        ["E is a valid EpistemicState", "B is a BridgeCore bridge", "scope(E) intersect scope(B) is nonempty"],
        "theory/EPISTEMIC_BRIDGE.md#uft-ep-001-authority-neutral-structural-transport",
    ),
    "UFT-EP-002": (
        "Within the Epistemic Bridge operations, retrieve, infer, execute, conflict-recording, and structural transport do not create verification receipts; verification status changes only through an explicit verification operation carrying a receipt.",
        ["all operations start from valid EpistemicState values", "verification is represented only by verification_receipts"],
        "theory/EPISTEMIC_BRIDGE.md#uft-ep-002-verification-requires-an-explicit-verification-receipt",
    ),
    "UFT-EP-003": (
        "For every valid EpistemicState, Conflict(E) implies not Unknown(E).",
        ["E is a valid EpistemicState", "nonempty conflict_refs requires nonempty evidence_refs"],
        "theory/EPISTEMIC_BRIDGE.md#uft-ep-003-conflict-is-distinct-from-unknown",
    ),
    "UFT-EP-004": (
        "Any finite composition of licensed authority-neutral transports preserves the epistemic authority vector exactly; only scope may monotonically narrow.",
        ["every transport step is licensed", "every step uses authority-neutral Epistemic Bridge transport"],
        "theory/EPISTEMIC_BRIDGE.md#uft-ep-004-repeated-neutral-transport-cannot-accumulate-authority",
    ),
    "UFT-EP-005": (
        "For licensed transport E -> E', scope(E') is a subset of both scope(E) and the bridge scope.",
        ["scope(E) intersect scope(B) is nonempty"],
        "theory/EPISTEMIC_BRIDGE.md#uft-ep-005-scope-is-non-expansive-under-transport",
    ),
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-EP-001": "A state can contain retrieved evidence while verification_receipts remains empty.",
    "CX-EP-002": "A state can record an inference and evidence while verification_receipts remains empty.",
    "CX-EP-003": "A state can contain an execution receipt and evidence while verification_receipts remains empty.",
    "CX-EP-004": "An evidence-backed conflict state is not unknown under the EpistemicState definition.",
    "CX-EP-005": "A valid state can contain both verification_receipts and conflict_refs.",
}
EXPECTED_EVIDENCE = ["experiments/epistemic_bridge/run.py", "tests/test_epistemic_bridge.py"]
EXPECTED_AUTHORITY = {
    "human": "theory/EPISTEMIC_BRIDGE.md",
    "machine_contract": "machine/epistemic_bridge_contract.json",
    "machine_results": "machine/epistemic_bridge_results.json",
    "validator": "scripts/validate_epistemic_bridge.py",
    "experiment": "experiments/epistemic_bridge/run.py",
    "tests": "tests/test_epistemic_bridge.py",
    "receipt_runner": "experiments/run_epistemic_bridge.py",
    "receipt_version": "1.0.0",
    "artifact_verifier": "scripts/verify_epistemic_bridge_artifacts.py",
    "base_bridge_authority": "machine/bridge_core_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "rule": "Epistemic Bridge factorizes evidence, retrieval, inference, verification, execution, conflict, and scope; structural transport is authority-neutral and no global epistemic lattice or truth oracle is implied."
}
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "transport proves truth",
    "retrieval proves verification",
    "execution proves verification",
    "verified means true",
    "conflict means false",
    "global epistemic lattice is canonical",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return None
    start = matches[0]
    m = re.match(r"^(#+)\s", heading)
    if m is None:
        return None
    level = len(m.group(1))
    out = [lines[start]]
    for line in lines[start + 1:]:
        hm = re.match(r"^(#+)\s", line.strip())
        if hm is not None and len(hm.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def metadata(sec: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    values = [line.strip()[len(prefix):] for line in sec.splitlines() if line.strip().startswith(prefix)]
    return values[0] if len(values) == 1 else None


def strip_code(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def safe_path(path: object, label: str, errors: list[str]) -> None:
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
        errors.append(f"{label} missing: {path}")


def validate() -> dict[str, object]:
    errors: list[str] = []
    for name, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing Epistemic Bridge authority file: {name}={path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    roadmap = load_json(PATHS["roadmap"])
    base = load_json(PATHS["base_contract"])
    human = PATHS["human"].read_text(encoding="utf-8")
    claims = PATHS["claims"].read_text(encoding="utf-8")
    readme = PATHS["readme"].read_text(encoding="utf-8")
    repro = PATHS["repro"].read_text(encoding="utf-8")

    if contract.get("type") != "uft-id-epistemic-bridge-contract": errors.append("epistemic contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("epistemic contract schema drift")
    if contract.get("snapshot_date") != "2026-08-24": errors.append("epistemic contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("epistemic contract claim class drift")
    fields = contract.get("fields")
    if not isinstance(fields, dict) or set(fields) != EXPECTED_FIELDS: errors.append("epistemic field set drift")
    if set(contract.get("hard_boundaries", [])) != EXPECTED_BOUNDARIES: errors.append("epistemic hard-boundary set drift")
    limits = contract.get("execution_limits")
    if not isinstance(limits, dict) or limits.get("raw_presence_vectors") != 64 or limits.get("valid_normalized_shapes") != 33:
        errors.append("epistemic execution-limit drift")
    authorities = contract.get("authorities")
    if not isinstance(authorities, dict):
        errors.append("epistemic authority registry malformed")
    else:
        for key, value in authorities.items():
            if key != "roadmap_state": safe_path(value, f"epistemic authority {key}", errors)

    records = results.get("records")
    if not isinstance(records, list):
        errors.append("epistemic result registry malformed")
        records = []
    by_id = {r.get("id"): r for r in records if isinstance(r, dict) and isinstance(r.get("id"), str)}
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(by_id) != expected_ids: errors.append("epistemic result identity set drift")

    for result_id, (statement, hypotheses, proof_ref) in EXPECTED_THEOREMS.items():
        record = by_id.get(result_id)
        if not isinstance(record, dict):
            continue
        if record.get("claim_class") != "PROVED": errors.append(f"{result_id} claim class drift")
        if record.get("statement") != statement: errors.append(f"{result_id} statement drift")
        if record.get("hypotheses") != hypotheses: errors.append(f"{result_id} hypotheses drift")
        if record.get("proof_reference") != proof_ref: errors.append(f"{result_id} proof reference drift")
        if record.get("executable_evidence") != EXPECTED_EVIDENCE: errors.append(f"{result_id} executable evidence drift")
        nonclaims = record.get("nonclaims")
        if not isinstance(nonclaims, list) or not nonclaims: errors.append(f"{result_id} nonclaims malformed")
        headings = [line.strip() for line in human.splitlines() if line.startswith("## ") and result_id in line]
        sec = section(human, headings[0]) if len(headings) == 1 else None
        if sec is None:
            errors.append(f"{result_id} human theorem section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`PROVED`": errors.append(f"{result_id} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != statement: errors.append(f"{result_id} human canonical statement drift")
        raw_h = strip_code(metadata(sec, "Canonical hypotheses"))
        try:
            parsed_h = json.loads(raw_h) if raw_h is not None else None
        except json.JSONDecodeError:
            parsed_h = None
        if parsed_h != hypotheses: errors.append(f"{result_id} human canonical hypotheses drift")

    for result_id, statement in EXPECTED_COUNTEREXAMPLES.items():
        record = by_id.get(result_id)
        if not isinstance(record, dict):
            continue
        if record.get("claim_class") != "COUNTEREXAMPLE": errors.append(f"{result_id} claim class drift")
        if record.get("statement") != statement: errors.append(f"{result_id} statement drift")
        if record.get("evidence") != EXPECTED_EVIDENCE: errors.append(f"{result_id} evidence drift")
        nonclaims = record.get("nonclaims")
        if not isinstance(nonclaims, list) or not nonclaims: errors.append(f"{result_id} nonclaims malformed")

    if results.get("claim_boundary") != "STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION != TRUTH; CONFLICT != UNKNOWN; VERIFIED != CONFLICT_FREE":
        errors.append("epistemic result claim boundary drift")

    if roadmap.get("basis_commit") != "2242f96564f4d27af4ba641b45f45f011a49a7c7": errors.append("epistemic roadmap basis commit drift")
    if roadmap.get("active_planned_surface") != 13: errors.append("epistemic roadmap active surface must be PR #13")
    completed = roadmap.get("completed")
    if not isinstance(completed, list) or 12 not in completed: errors.append("epistemic roadmap must mark planned PR #12 complete")
    sequence = roadmap.get("sequence")
    if not isinstance(sequence, list):
        errors.append("epistemic roadmap sequence malformed")
    else:
        by_pr = {x.get("planned_pr"): x for x in sequence if isinstance(x, dict)}
        if by_pr.get(12, {}).get("status") != "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7": errors.append("planned PR #12 completion state drift")
        if by_pr.get(13, {}).get("status") != "active-implemented-in-current-change": errors.append("planned PR #13 active state drift")
        if by_pr.get(14, {}).get("status") != "planned": errors.append("planned PR #14 must remain planned")

    if base.get("epistemic_bridge_authority") != EXPECTED_AUTHORITY: errors.append("central Epistemic Bridge authority registration drift")
    library = base.get("experiment_library")
    if not isinstance(library, dict) or library.get("epistemic_bridge_receipt_runner") != "experiments/run_epistemic_bridge.py" or library.get("epistemic_bridge_receipt_version") != "1.0.0":
        errors.append("central Epistemic Bridge receipt registry drift")
    reads = base.get("required_agent_reads")
    required_reads = {"theory/EPISTEMIC_BRIDGE.md", "machine/epistemic_bridge_contract.json", "machine/epistemic_bridge_results.json", "scripts/validate_epistemic_bridge.py", "experiments/run_epistemic_bridge.py"}
    if not isinstance(reads, list) or not required_reads.issubset(set(reads)):
        errors.append("central Epistemic Bridge agent-read registration drift")

    for text, anchors, label in (
        (claims, ("### C9 - Epistemic authority is factorized and transport-neutral", "STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION", "CONFLICT != UNKNOWN"), "claims"),
        (readme, ("## Epistemic Bridge authority", "machine/epistemic_bridge_contract.json", "NO_GLOBAL_EPISTEMIC_LATTICE"), "README4AI"),
        (repro, ("## Epistemic Bridge conformance boundary", "epistemic-bridge-validation.json", "python scripts/validate_epistemic_bridge.py"), "reproducibility"),
    ):
        for anchor in anchors:
            if anchor not in text: errors.append(f"{label} missing Epistemic Bridge anchor: {anchor}")

    combined = "\n".join((json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False), human, claims, readme, repro))
    lower = combined.casefold()
    for token in PRIVATE_PATTERNS:
        if token in lower: errors.append(f"epistemic authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in lower: errors.append(f"epistemic authority contains forbidden promotion: {phrase}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(by_id),
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
        print(f"Epistemic Bridge authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
