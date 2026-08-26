#!/usr/bin/env python3
"""Validate repository-level reproducibility and CI provenance rules.

The workflow policy parser is deliberately dependency-free and limited to the
GitHub Actions structures this repository uses. It validates active YAML fields
by indentation/context rather than searching for policy strings in raw text.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ACTION_REF_RE = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})$")
ACTION_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON object key: {key}")
            value[key] = item
        return value

    def reject_constant(token: str):
        raise ValueError(f"non-finite JSON number: {token}")

    def finite_float(token: str) -> float:
        value = float(token)
        if not math.isfinite(value):
            raise ValueError(f"non-finite JSON number: {token}")
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _active(line: str) -> str:
    """Return one active YAML line with an optional trailing comment removed."""

    stripped = line.rstrip()
    if not stripped.lstrip() or stripped.lstrip().startswith("#"):
        return ""
    if " #" in stripped:
        stripped = stripped.split(" #", 1)[0].rstrip()
    return stripped


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _scalar(raw: str) -> object:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    lowered = value.casefold()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = json.loads(value.replace("'", '"'))
        except json.JSONDecodeError:
            return value
        return parsed
    return value


def _mapping_after(
    lines: list[str],
    index: int,
    *,
    parent_indent: int,
) -> dict[str, object]:
    result: dict[str, object] = {}
    child_indent = parent_indent + 2
    for line in lines[index + 1 :]:
        active = _active(line)
        if not active:
            continue
        indentation = _indent(active)
        if indentation <= parent_indent:
            break
        if indentation != child_indent:
            continue
        text = active.strip()
        if ":" not in text:
            continue
        key, raw = text.split(":", 1)
        result[key.strip()] = _scalar(raw)
    return result


def _job_blocks(lines: list[str]) -> dict[str, list[str]]:
    jobs_index = next(
        (index for index, line in enumerate(lines) if _active(line) == "jobs:"),
        None,
    )
    if jobs_index is None:
        return {}

    starts: list[tuple[int, str]] = []
    for index in range(jobs_index + 1, len(lines)):
        active = _active(lines[index])
        if not active:
            continue
        if _indent(active) == 0:
            break
        if _indent(active) == 2 and active.strip().endswith(":"):
            starts.append((index, active.strip()[:-1]))

    blocks: dict[str, list[str]] = {}
    for position, (start, name) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        blocks[name] = lines[start:end]
    return blocks


def _step_blocks(job_lines: list[str]) -> list[list[str]]:
    steps_index = next(
        (index for index, line in enumerate(job_lines) if _active(line) == "    steps:"),
        None,
    )
    if steps_index is None:
        return []

    starts: list[int] = []
    for index in range(steps_index + 1, len(job_lines)):
        active = _active(job_lines[index])
        if not active:
            continue
        if _indent(active) <= 2:
            break
        if _indent(active) == 6 and active.lstrip().startswith("- "):
            starts.append(index)

    blocks: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(job_lines)
        blocks.append(job_lines[start:end])
    return blocks


def _parse_step(block: list[str]) -> dict[str, object]:
    fields: dict[str, object] = {"with": {}}
    if not block:
        return fields

    first = _active(block[0]).strip()
    first = first[2:].strip() if first.startswith("- ") else first
    if ":" in first:
        key, raw = first.split(":", 1)
        fields[key.strip()] = _scalar(raw)

    index = 1
    while index < len(block):
        active = _active(block[index])
        if not active:
            index += 1
            continue
        if _indent(active) != 8:
            index += 1
            continue
        text = active.strip()
        if ":" not in text:
            index += 1
            continue
        key, raw = text.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if key == "with" and not raw:
            fields["with"] = _mapping_after(block, index, parent_indent=8)
        elif key == "run" and raw == "|":
            commands: list[str] = []
            for follow in block[index + 1 :]:
                follow_active = _active(follow)
                if not follow_active:
                    continue
                if _indent(follow_active) <= 8:
                    break
                commands.append(follow_active.strip())
            fields["run"] = "\n".join(commands)
        else:
            fields[key] = _scalar(raw)
        index += 1
    return fields


def parse_workflow(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    permissions: dict[str, object] | None = None
    for index, line in enumerate(lines):
        active = _active(line)
        if active == "permissions:":
            permissions = _mapping_after(lines, index, parent_indent=0)
            break
        if active.startswith("permissions:") and _indent(active) == 0:
            permissions = {"__scalar__": _scalar(active.split(":", 1)[1])}
            break

    jobs: dict[str, dict[str, object]] = {}
    for name, block in _job_blocks(lines).items():
        runner = None
        matrix_python = None
        job_permissions = None
        for index, line in enumerate(block):
            active = _active(line)
            if active.startswith("    runs-on:"):
                runner = _scalar(active.split(":", 1)[1])
            elif active.startswith("        python-version:"):
                matrix_python = _scalar(active.split(":", 1)[1])
            elif active == "    permissions:":
                job_permissions = _mapping_after(block, index, parent_indent=4)
            elif active.startswith("    permissions:"):
                job_permissions = {"__scalar__": _scalar(active.split(":", 1)[1])}

        jobs[name] = {
            "runner": runner,
            "matrix_python": matrix_python,
            "permissions": job_permissions,
            "steps": [_parse_step(step) for step in _step_blocks(block)],
        }

    return {"permissions": permissions, "jobs": jobs}


def discover_workflows(root: Path, extensions: list[str]) -> list[Path]:
    workflow_dir = root / ".github/workflows"
    paths: set[Path] = set()
    for extension in extensions:
        paths.update(workflow_dir.glob(f"*{extension}"))
    return sorted(paths)


def validate_action_pins(
    workflow_paths: list[Path],
    parsed_workflows: dict[Path, dict[str, object]],
    action_pins: dict[str, str],
    errors: list[str],
    *,
    root: Path,
) -> None:
    observed: dict[str, set[str]] = {}
    for path in workflow_paths:
        workflow = parsed_workflows[path]
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                uses = step.get("uses")
                if uses is None:
                    continue
                if not isinstance(uses, str):
                    errors.append(f"{display_path(path, root)}: uses must be a string")
                    continue
                match = ACTION_REF_RE.fullmatch(uses)
                if match is None:
                    errors.append(
                        f"{display_path(path, root)}: GitHub Action {uses!r} must be pinned "
                        "to a full 40-character commit SHA"
                    )
                    continue
                action, sha = match.groups()
                observed.setdefault(action, set()).add(sha)
                expected = action_pins.get(action)
                if expected is None:
                    errors.append(f"{display_path(path, root)}: undeclared action {action}")
                elif sha != expected:
                    errors.append(
                        f"{display_path(path, root)}: {action} pin {sha} "
                        f"does not match machine contract {expected}"
                    )

    for action, expected in action_pins.items():
        if expected not in observed.get(action, set()):
            errors.append(f"machine contract action pin is unused: {action}@{expected}")


def validate_no_scientific_asserts(root: Path, errors: list[str]) -> None:
    for path in sorted((root / "experiments").rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{display_path(path, root)}: syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                errors.append(
                    f"{display_path(path, root)}:{node.lineno}: scientific code must use "
                    "explicit fail-closed checks, not assert"
                )


def validate_workflow_contract(
    workflow_paths: list[Path],
    parsed_workflows: dict[Path, dict[str, object]],
    runtime_support: dict[str, Any],
    provenance: dict[str, Any],
    errors: list[str],
    *,
    root: Path,
) -> None:
    runner = runtime_support.get("github_runner")
    versions = list(runtime_support.get("python", []))
    expected_permissions = provenance.get("workflow_permissions")
    compile_command = provenance.get("compile_command")
    test_commands = list(provenance.get("test_commands", []))
    expected_retention = provenance.get("artifact_retention_days")
    evidence_condition = provenance.get("evidence_generation_condition")
    expected_persist = provenance.get("persist_checkout_credentials")
    allow_job_permissions = provenance.get("job_permission_overrides_allowed") is True

    for path in workflow_paths:
        label = display_path(path, root)
        workflow = parsed_workflows[path]
        if workflow.get("permissions") != expected_permissions:
            errors.append(
                f"{label}: top-level permissions must exactly equal {expected_permissions!r}"
            )

        jobs = workflow.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            errors.append(f"{label}: workflow must define at least one job")
            continue

        for job_name, job in jobs.items():
            job_label = f"{label} job {job_name}"
            if job.get("runner") != runner:
                errors.append(f"{job_label}: runs-on must equal {runner}")
            if job.get("matrix_python") != versions:
                errors.append(
                    f"{job_label}: Python matrix must exactly equal {versions!r}"
                )
            if job.get("permissions") is not None and not allow_job_permissions:
                errors.append(f"{job_label}: job-level permission overrides are forbidden")

            steps = job.get("steps", [])
            if not isinstance(steps, list) or not steps:
                errors.append(f"{job_label}: steps must be non-empty")
                continue

            compile_index = None
            test_indices: list[int] = []
            checkout_seen = False
            setup_seen = False
            upload_seen = False
            evidence_seen = False

            for index, step in enumerate(steps):
                run = step.get("run")
                name = step.get("name")
                uses = step.get("uses")
                with_values = step.get("with", {})

                if run == compile_command:
                    compile_index = index
                if run in test_commands:
                    test_indices.append(index)

                if isinstance(uses, str) and uses.startswith("actions/checkout@"):
                    checkout_seen = True
                    if not isinstance(with_values, dict) or with_values.get("persist-credentials") != expected_persist:
                        errors.append(
                            f"{job_label}: checkout persist-credentials must equal "
                            f"{expected_persist!r}"
                        )

                if isinstance(uses, str) and uses.startswith("actions/setup-python@"):
                    setup_seen = True
                    if not isinstance(with_values, dict) or with_values.get("python-version") != "${{ matrix.python-version }}":
                        errors.append(
                            f"{job_label}: setup-python must use matrix.python-version"
                        )

                if isinstance(name, str) and name.startswith("Generate ") and "evidence bundle" in name:
                    evidence_seen = True
                    if step.get("if") != evidence_condition:
                        errors.append(
                            f"{job_label}: evidence generation must use if: {evidence_condition}"
                        )
                    artifact_directory = provenance.get("artifact_directory")
                    if not isinstance(run, str) or f"mkdir -p {artifact_directory}" not in run:
                        errors.append(
                            f"{job_label}: evidence generation must create {artifact_directory}/"
                        )

                if isinstance(uses, str) and uses.startswith("actions/upload-artifact@"):
                    upload_seen = True
                    if step.get("if") != "always()":
                        errors.append(f"{job_label}: artifact upload must use if: always()")
                    if not isinstance(with_values, dict) or with_values.get("retention-days") != expected_retention:
                        errors.append(
                            f"{job_label}: artifact retention-days must equal {expected_retention}"
                        )

            if not checkout_seen:
                errors.append(f"{job_label}: checkout step is missing")
            if not setup_seen:
                errors.append(f"{job_label}: setup-python step is missing")
            if compile_index is None:
                errors.append(f"{job_label}: compile command is missing")
            if len(test_indices) != len(test_commands):
                errors.append(f"{job_label}: declared test commands are incomplete")
            if compile_index is not None and test_indices and compile_index >= min(test_indices):
                errors.append(f"{job_label}: compile step must precede all test steps")
            if not evidence_seen:
                errors.append(f"{job_label}: evidence-generation step is missing")
            if not upload_seen:
                errors.append(f"{job_label}: artifact-upload step is missing")


def validate(root: Path = ROOT) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []
    try:
        load_json(root / "machine/roadmap_state.json")
    except (OSError, ValueError) as exc:
        errors.append(f"live roadmap state JSON invalid: {exc}")
    contract = load_json(root / "machine/contract.json")
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
            if not isinstance(action, str) or not ACTION_NAME_RE.fullmatch(action):
                errors.append(f"invalid action identifier in machine contract: {action!r}")
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
                errors.append(f"invalid full-SHA action pin for {action!r}")

    extensions = provenance.get("workflow_extensions")
    if not isinstance(extensions, list) or set(extensions) != {".yml", ".yaml"}:
        errors.append("machine contract workflow_extensions must declare .yml and .yaml")
        extensions = [".yml", ".yaml"]

    workflow_paths = discover_workflows(root, [str(value) for value in extensions])
    declared = provenance.get("workflow_files")
    if not isinstance(declared, list) or not all(isinstance(value, str) for value in declared):
        errors.append("machine contract ci_provenance.workflow_files must be a string list")
        declared = []
    observed_names = [display_path(path, root) for path in workflow_paths]
    if sorted(declared) != sorted(observed_names):
        errors.append(
            "discovered GitHub workflows must exactly match machine contract: "
            f"declared={sorted(declared)!r}, observed={sorted(observed_names)!r}"
        )
    if not workflow_paths:
        errors.append("no GitHub Actions workflows found")

    parsed_workflows = {path: parse_workflow(path) for path in workflow_paths}
    validate_action_pins(
        workflow_paths,
        parsed_workflows,
        action_pins,
        errors,
        root=root,
    )
    validate_workflow_contract(
        workflow_paths,
        parsed_workflows,
        runtime_support,
        provenance,
        errors,
        root=root,
    )
    validate_no_scientific_asserts(root, errors)

    required_files = [
        root / "experiments/lib/information.py",
        root / "experiments/__init__.py",
        root / "experiments/lib/__init__.py",
        root / "scripts/render_vopson_docs.py",
        root / "docs/REPRODUCIBILITY.md",
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"required reproducibility file is missing: {display_path(path, root)}")

    return {
        "ok": not errors,
        "errors": errors,
        "summary": {
            "workflows": len(workflow_paths),
            "scientific_python_files": len(list((root / "experiments").rglob("*.py"))),
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
