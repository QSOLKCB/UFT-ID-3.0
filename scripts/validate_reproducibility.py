#!/usr/bin/env python3
"""Validate repository-level reproducibility and CI provenance rules."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "machine/contract.json"
WORKFLOW_DIR = ROOT / ".github/workflows"

USES_RE = re.compile(
    r"^\s*(?:-\s+)?uses:\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})\s*(?:#.*)?$"
)
ANY_USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s+([^\s#]+)")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_action_pins(
    workflow_paths: list[Path],
    action_pins: dict[str, str],
    errors: list[str],
) -> None:
    observed: dict[str, set[str]] = {}
    for path in workflow_paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "uses:" not in line:
                continue
            loose = ANY_USES_RE.match(line)
            strict = USES_RE.match(line)
            if loose is None:
                errors.append(f"{display_path(path)}:{line_number}: malformed uses entry")
                continue
            if strict is None:
                errors.append(
                    f"{display_path(path)}:{line_number}: GitHub Action must be pinned "
                    "to a full 40-character commit SHA"
                )
                continue
            action, sha = strict.groups()
            observed.setdefault(action, set()).add(sha)
            expected = action_pins.get(action)
            if expected is None:
                errors.append(f"{display_path(path)}:{line_number}: undeclared action {action}")
            elif sha != expected:
                errors.append(
                    f"{display_path(path)}:{line_number}: {action} pin {sha} "
                    f"does not match machine contract {expected}"
                )

    for action, expected in action_pins.items():
        if expected not in observed.get(action, set()):
            errors.append(f"machine contract action pin is unused: {action}@{expected}")


def validate_no_scientific_asserts(errors: list[str]) -> None:
    for path in sorted((ROOT / "experiments").rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{display_path(path)}: syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                errors.append(
                    f"{display_path(path)}:{node.lineno}: scientific code must use "
                    "explicit fail-closed checks, not assert"
                )


def validate_workflow_contract(
    workflow_paths: list[Path],
    runtime_support: dict[str, Any],
    errors: list[str],
) -> None:
    runner = runtime_support.get("github_runner")
    versions = runtime_support.get("python", [])
    for path in workflow_paths:
        text = path.read_text(encoding="utf-8")
        if f"runs-on: {runner}" not in text:
            errors.append(f"{display_path(path)} must use runner {runner}")
        if "persist-credentials: false" not in text:
            errors.append(f"{display_path(path)} must disable persisted checkout credentials")
        if "actions/upload-artifact" not in text:
            errors.append(f"{display_path(path)} must retain CI evidence as an artifact")
        if "python -m compileall" not in text:
            errors.append(f"{display_path(path)} must compile Python before execution")
        if "python -O -m unittest" not in text:
            errors.append(f"{display_path(path)} must test optimized Python execution")
        for version in versions:
            if f'"{version}"' not in text:
                errors.append(f"{display_path(path)} is missing Python {version}")


def validate() -> dict[str, object]:
    errors: list[str] = []
    contract = load_json(CONTRACT_PATH)
    provenance = contract.get("ci_provenance")
    if not isinstance(provenance, dict):
        errors.append("machine contract must define ci_provenance")
        provenance = {}
    runtime_support = contract.get("runtime_support")
    if not isinstance(runtime_support, dict):
        errors.append("machine contract must define runtime_support")
        runtime_support = {}
    action_pins = provenance.get("action_pins")
    if not isinstance(action_pins, dict) or not action_pins:
        errors.append("machine contract ci_provenance.action_pins must be a non-empty object")
        action_pins = {}
    else:
        for action, sha in action_pins.items():
            if not isinstance(action, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", action):
                errors.append(f"invalid action identifier in machine contract: {action!r}")
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
                errors.append(f"invalid full-SHA action pin for {action!r}")

    workflow_paths = sorted(WORKFLOW_DIR.glob("*.yml"))
    if not workflow_paths:
        errors.append("no GitHub Actions workflows found")
    validate_action_pins(workflow_paths, action_pins, errors)
    validate_workflow_contract(workflow_paths, runtime_support, errors)
    validate_no_scientific_asserts(errors)

    required_files = [
        ROOT / "experiments/lib/information.py",
        ROOT / "scripts/render_vopson_docs.py",
        ROOT / "docs/REPRODUCIBILITY.md",
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"required reproducibility file is missing: {path.relative_to(ROOT)}")

    return {
        "ok": not errors,
        "errors": errors,
        "summary": {
            "workflows": len(workflow_paths),
            "scientific_python_files": len(list((ROOT / "experiments").rglob("*.py"))),
            "action_pins": len(action_pins),
            "supported_python": list(runtime_support.get("python", [])),
            "runner": runtime_support.get("github_runner"),
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
        print(
            f"validated {report['summary']['workflows']} workflows, "
            f"{report['summary']['scientific_python_files']} experiment files, "
            f"{report['summary']['action_pins']} pinned actions"
        )
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
