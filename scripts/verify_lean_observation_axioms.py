#!/usr/bin/env python3
"""Audit imported axioms for the registered UFT observation theorems.

This is a post-build check. It asks the pinned Lean kernel for `#print axioms`
on every registered theorem, rejects undeclared axioms, requires the explicit
classical-choice dependency for UFT-OBS-003/004, and optionally retains the
observed report as JSON.
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
    result: dict[str, list[str]] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        match = NO_AXIOMS_RE.fullmatch(line)
        if match:
            result[match.group(1)] = []
            continue
        match = AXIOMS_RE.fullmatch(line)
        if match:
            body = match.group(2).strip()
            result[match.group(1)] = (
                [] if not body else [item.strip() for item in body.split(",") if item.strip()]
            )
    return result


def run_audit(lake: str) -> dict[str, object]:
    loaded = load_policy()
    record = loaded["record"]
    policy = loaded["policy"]
    assert isinstance(record, dict)
    assert isinstance(policy, dict)

    theorem_records = record.get("theorems")
    if not isinstance(theorem_records, list):
        raise RuntimeError("verification record theorem list is malformed")

    declarations: dict[str, str] = {}
    for item in theorem_records:
        if not isinstance(item, dict):
            raise RuntimeError("verification theorem entry is malformed")
        theorem_id = item.get("id")
        declaration = item.get("declaration")
        if not isinstance(theorem_id, str) or not isinstance(declaration, str):
            raise RuntimeError("verification theorem identity is malformed")
        declarations[theorem_id] = f"UFTID.Observation.{declaration}"

    lines = ["import UFTID", ""]
    for theorem_id in declarations:
        lines.append(f"#print axioms {declarations[theorem_id]}")
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
    allowed = policy.get("allowed_axioms")
    required = policy.get("required_axioms_by_theorem")
    if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
        raise RuntimeError("axiom_audit.allowed_axioms is malformed")
    if not isinstance(required, dict):
        raise RuntimeError("axiom_audit.required_axioms_by_theorem is malformed")
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
        expected_required = required.get(theorem_id, [])
        if not isinstance(expected_required, list) or not all(
            isinstance(x, str) for x in expected_required
        ):
            errors.append(f"{theorem_id} required axiom policy is malformed")
            continue
        missing_required = sorted(set(expected_required) - set(actual))
        if missing_required:
            errors.append(f"{theorem_id} missing recorded required axioms: {missing_required}")

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
