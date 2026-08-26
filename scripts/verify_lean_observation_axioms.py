#!/usr/bin/env python3
"""Audit imported axioms for the registered UFT observation theorems.

This is a post-build check. It asks the pinned Lean kernel for `#print axioms`
on every registered theorem, rejects undeclared axioms, requires explicitly
registered minimum dependencies, and, once a verification record is promoted,
requires the exact recorded observed axiom set for every theorem. The observed
report can optionally be retained as JSON.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "machine/lean_observation_verification.json"

NO_AXIOMS_RE = re.compile(r"^'([^']+)' does not depend on any axioms$")
AXIOMS_RE = re.compile(r"^'([^']+)' depends on axioms: \[(.*)\]$")


def load_policy() -> dict[str, object]:
    with VERIFICATION.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    policy = record.get("axiom_audit")
    if not isinstance(policy, dict):
        raise RuntimeError("verification record is missing axiom_audit policy")
    return {"record": record, "policy": policy}


def parse_axiom_output(stdout: str) -> dict[str, list[str]]:
    """Parse only Lean's canonical `#print axioms` result lines.

    Non-result chatter is ignored. Repeated results for one declaration must be
    identical, otherwise the audit fails closed rather than silently accepting
    whichever line happened to appear last.
    """
    result: dict[str, list[str]] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        parsed: tuple[str, list[str]] | None = None
        match = NO_AXIOMS_RE.fullmatch(line)
        if match:
            parsed = (match.group(1), [])
        else:
            match = AXIOMS_RE.fullmatch(line)
            if match:
                body = match.group(2).strip()
                axioms = [] if not body else [
                    item.strip() for item in body.split(",") if item.strip()
                ]
                parsed = (match.group(1), axioms)
        if parsed is None:
            continue
        name, axioms = parsed
        canonical = sorted(set(axioms))
        if name in result and result[name] != canonical:
            raise RuntimeError(f"conflicting #print axioms results for {name}")
        result[name] = canonical
    return result


def declarations_from_record(record: dict[str, object]) -> dict[str, str]:
    theorem_records = record.get("theorems")
    if not isinstance(theorem_records, list):
        raise RuntimeError("verification record theorem list is malformed")

    declarations: dict[str, str] = {}
    seen_full_names: set[str] = set()
    for item in theorem_records:
        if not isinstance(item, dict):
            raise RuntimeError("verification theorem entry is malformed")
        theorem_id = item.get("id")
        declaration = item.get("declaration")
        if not isinstance(theorem_id, str) or not isinstance(declaration, str):
            raise RuntimeError("verification theorem identity is malformed")
        if theorem_id in declarations:
            raise RuntimeError(f"duplicate verification theorem id: {theorem_id}")
        full_name = f"UFTID.Observation.{declaration}"
        if full_name in seen_full_names:
            raise RuntimeError(f"duplicate verification Lean declaration: {full_name}")
        declarations[theorem_id] = full_name
        seen_full_names.add(full_name)
    return declarations


def _validated_axiom_map(
    value: object,
    *,
    field: str,
    theorem_ids: set[str],
    require_complete: bool,
) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise RuntimeError(f"axiom_audit.{field} is malformed")
    keys = set(value)
    unknown = sorted(keys - theorem_ids)
    if unknown:
        raise RuntimeError(f"axiom_audit {field} names unknown theorem ids: {unknown}")
    if require_complete:
        missing = sorted(theorem_ids - keys)
        if missing:
            raise RuntimeError(f"axiom_audit {field} omits theorem ids: {missing}")
    result: dict[str, list[str]] = {}
    for theorem_id, axioms in value.items():
        if not isinstance(theorem_id, str) or not isinstance(axioms, list) or not all(
            isinstance(x, str) for x in axioms
        ):
            raise RuntimeError(f"axiom_audit.{field}[{theorem_id!r}] is malformed")
        if len(axioms) != len(set(axioms)):
            raise RuntimeError(f"axiom_audit.{field}[{theorem_id}] contains duplicate axioms")
        result[theorem_id] = sorted(axioms)
    return result


def evaluate_axiom_policy(
    record: dict[str, object],
    policy: dict[str, object],
    parsed: dict[str, list[str]],
) -> dict[str, object]:
    """Evaluate parsed kernel output against the machine axiom policy."""
    declarations = declarations_from_record(record)
    theorem_ids = set(declarations)
    allowed = policy.get("allowed_axioms")
    required = policy.get("required_axioms_by_theorem")
    if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
        raise RuntimeError("axiom_audit.allowed_axioms is malformed")
    if len(allowed) != len(set(allowed)):
        raise RuntimeError("axiom_audit.allowed_axioms contains duplicates")
    required_map = _validated_axiom_map(
        required,
        field="required_axioms_by_theorem",
        theorem_ids=theorem_ids,
        require_complete=False,
    )
    recorded_observed_raw = policy.get("observed_axioms_by_theorem")
    recorded_observed = None
    if recorded_observed_raw is not None:
        recorded_observed = _validated_axiom_map(
            recorded_observed_raw,
            field="observed_axioms_by_theorem",
            theorem_ids=theorem_ids,
            require_complete=True,
        )
    allowed_set = set(allowed)

    errors: list[str] = []
    observed_by_id: dict[str, list[str]] = {}
    for theorem_id, full_name in declarations.items():
        if full_name not in parsed:
            errors.append(f"missing #print axioms result for {theorem_id}: {full_name}")
            continue
        actual = sorted(set(parsed[full_name]))
        observed_by_id[theorem_id] = actual
        undeclared = sorted(set(actual) - allowed_set)
        if undeclared:
            errors.append(f"{theorem_id} uses undeclared axioms: {undeclared}")
        expected_required = required_map.get(theorem_id, [])
        missing_required = sorted(set(expected_required) - set(actual))
        if missing_required:
            errors.append(f"{theorem_id} missing recorded required axioms: {missing_required}")
        if recorded_observed is not None:
            expected_observed = recorded_observed[theorem_id]
            if actual != expected_observed:
                errors.append(
                    f"{theorem_id} observed axiom set drift: "
                    f"expected {expected_observed}, got {actual}"
                )

    unexpected_results = sorted(set(parsed) - set(declarations.values()))
    if unexpected_results:
        errors.append(f"unexpected #print axioms results: {unexpected_results}")

    return {
        "type": "uft-id-lean-observation-axiom-report",
        "schema_version": "1.0.0",
        "status": "error" if errors else "ok",
        "source_release": record.get("source_release"),
        "toolchain": record.get("toolchain"),
        "allowed_axioms": sorted(allowed_set),
        "observed_axioms_by_theorem": observed_by_id,
        "errors": errors,
    }


def run_audit(lake: str) -> dict[str, object]:
    loaded = load_policy()
    record = loaded["record"]
    policy = loaded["policy"]
    if not isinstance(record, dict) or not isinstance(policy, dict):
        raise RuntimeError("verification axiom policy payload is malformed")

    declarations = declarations_from_record(record)
    lines = ["import UFTID", ""]
    for full_name in declarations.values():
        lines.append(f"#print axioms {full_name}")
    source = "\n".join(lines) + "\n"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".lean", prefix="uft-axiom-audit-", encoding="utf-8", delete=False
    ) as handle:
        handle.write(source)
        audit_path = Path(handle.name)

    try:
        proc = subprocess.run(
            [lake, "env", "lean", str(audit_path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        audit_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        raise RuntimeError(
            "Lean axiom audit command failed:\n" + proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        )

    parsed = parse_axiom_output(proc.stdout)
    return evaluate_axiom_policy(record, policy, parsed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lake", default="lake")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        report = run_audit(args.lake)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "type": "uft-id-lean-observation-axiom-report",
            "schema_version": "1.0.0",
            "status": "error",
            "errors": [str(exc)],
        }

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    if report["status"] == "ok":
        print("Lean observation axiom audit: ok")
        for theorem_id, axioms in report["observed_axioms_by_theorem"].items():
            print(f"  {theorem_id}: {', '.join(axioms) if axioms else '(none)'}")
        return 0

    for error in report.get("errors", []):
        print(error)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
