#!/usr/bin/env python3
"""Hardened BridgeCore authority validator after the second Codex audit.

The pre-audit validator remains byte-for-byte preserved in
validate_bridge_core_precodex2_frozen.py. This wrapper retains every earlier
check and adds independent human theorem mirroring, exact result nonclaims, and
receipt-version registry coherence.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_bridge_core_precodex2_frozen.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

_spec = importlib.util.spec_from_file_location("bridge_validator_precodex2_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen BridgeCore validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

# Public mutable pin surface retained for the existing adversarial tests. Before
# every validation pass these values are copied into the frozen validator.
EXPECTED_BLOBS = dict(_frozen.EXPECTED_BLOBS)
EXPECTED_BLOBS["human"] = "d65a56d124a1451ea437669663218d5410a1ff32"

EXPECTED_NONCLAIMS = {
    "UFT-BR-001": ["Type-correct composition does not imply semantic equivalence, truth preservation, or physical validity."],
    "UFT-BR-002": ["This does not forbid a separately proved reconstruction theorem; it forbids silently assuming one."],
    "UFT-BR-003": ["Deterministic post-processing is not automatically exact reconstruction of discarded structure."],
    "UFT-BR-004": ["A bridge is not an identity merely because source and target type names happen to match; partial structure metadata does not imply two-sided metadata neutrality."],
    "UFT-BR-005": ["Associativity of the structural bridge calculus does not imply that an application-specific interpretation is associative or lossless."],
    "CX-BR-001": ["The fixture is synthetic and does not model a particular physical channel."],
    "CX-BR-002": ["A separately supplied migration bridge may make two versions compatible."],
    "CX-BR-003": ["Scope overlap is a licensing condition, not evidence that the bridge is physically correct."],
    "CX-BR-004": ["This is a finite structural reconstruction counterexample, not an information-destruction claim about physics."],
}


def _strip_code(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def _human_theorem_semantics(human: str, result_id: str) -> tuple[str | None, list[str] | None]:
    candidates = [line.strip() for line in human.splitlines() if line.startswith("## ") and result_id in line]
    if len(candidates) != 1:
        return None, None
    section = _frozen.markdown_section(human, candidates[0])
    if section is None:
        return None, None
    statement = _strip_code(_frozen.metadata_value(section, "Canonical statement"))
    raw_hypotheses = _strip_code(_frozen.metadata_value(section, "Canonical hypotheses"))
    try:
        hypotheses = json.loads(raw_hypotheses) if raw_hypotheses is not None else None
    except json.JSONDecodeError:
        hypotheses = None
    if not isinstance(hypotheses, list) or any(not isinstance(x, str) for x in hypotheses):
        hypotheses = None
    return statement, hypotheses


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("machine/contract.json must be an object")
    authority = payload.get("bridge_core_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("BridgeCore receipt version registries must be objects")
    authority_version = authority.get("receipt_version")
    library_version = library.get("bridge_core_receipt_version")
    if not isinstance(authority_version, str) or not authority_version:
        raise RuntimeError("BridgeCore authority receipt_version must be a non-empty string")
    if not isinstance(library_version, str) or not library_version:
        raise RuntimeError("BridgeCore experiment-library receipt version must be a non-empty string")
    if authority_version != library_version:
        raise RuntimeError("BridgeCore receipt version registry disagreement")
    return authority_version


def validate() -> dict[str, object]:
    _frozen.EXPECTED_BLOBS.update(EXPECTED_BLOBS)
    result = _frozen.validate()
    errors = list(result.get("errors", []))

    human = _frozen.PATHS["human"].read_text(encoding="utf-8")
    results = _frozen.load_json(_frozen.PATHS["results"])
    records = results.get("records")
    if not isinstance(records, list):
        records = []

    by_id = {
        record.get("id"): record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }

    # Human theorem statements and hypotheses are explicit canonical metadata and
    # must mirror the machine theorem registry independently of the whole-file
    # Git blob pin. Rebinding EXPECTED_BLOBS['human'] cannot broaden a proof.
    for result_id, expected in _frozen.EXPECTED_RESULT_BINDINGS.items():
        if not result_id.startswith("UFT-BR-"):
            continue
        statement, hypotheses = _human_theorem_semantics(human, result_id)
        if statement != expected["statement"]:
            errors.append(f"{result_id} human canonical statement drift")
        if hypotheses != expected["hypotheses"]:
            errors.append(f"{result_id} human canonical hypotheses drift")

    # Result-scoped nonclaims are authority, not free prose. Bind every one
    # exactly so a blob rebind cannot turn a nonclaim into physical promotion.
    for result_id, expected_nonclaims in EXPECTED_NONCLAIMS.items():
        record = by_id.get(result_id)
        if not isinstance(record, dict) or record.get("nonclaims") != expected_nonclaims:
            errors.append(f"{result_id} nonclaims drift")

    # The finite executable specialization must explicitly document its shared
    # carrier realization rule, while the abstract theorem remains typed by one
    # common X_1 carrier.
    for anchor in (
        "may be empty",
        "B1.target_states",
        "B2.source_states",
        "TYPE_VERSION_MATCH != FINITE_CARRIER_IDENTITY",
        "production `compose` implementation",
    ):
        if anchor not in human:
            errors.append(f"BridgeCore human executable-boundary drift: {anchor}")

    try:
        registered_receipt_version()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    return {
        **result,
        "status": "error" if errors else "ok",
        "errors": errors,
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
