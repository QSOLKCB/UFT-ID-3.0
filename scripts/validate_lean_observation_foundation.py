#!/usr/bin/env python3
"""Latest PR #21 hardening wrapper around the exact prior live validator.

The prior live validator is preserved byte-for-byte in
validate_lean_observation_foundation_pr21_pre_codex4.py. This wrapper adds the
fourth hostile-review hardening batch without rewriting already-reviewed
semantics: exact freeze-step environment binding, checkout-ref rejection, and
human dependency-graph synchronization.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/validate_lean_observation_foundation_pr21_pre_codex4.py"

_spec = importlib.util.spec_from_file_location("lean_observation_pr21_pre_codex4", BASE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load prior PR21 validator: {BASE}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__") and _name not in {"workflow_contract_errors", "validate_documents", "validate", "main"}:
        globals()[_name] = getattr(_base, _name)


def _step_blocks(job_body: str) -> tuple[str, ...]:
    return tuple(match.group("body") for match in re.finditer(r"(?ms)^      - (?P<body>.*?)(?=^      - |\Z)", job_body))


def _exact_freeze_environment_errors(freeze_step: str) -> list[str]:
    errors: list[str] = []
    match = re.search(r"(?m)^        env:\n(?P<body>(?:          [^\n]+\n)+)", freeze_step)
    if match is None:
        return ["registered Lean-freeze validator step must have the exact canonical environment mapping"]
    entries = tuple(line.strip() for line in match.group("body").splitlines() if line.strip())
    expected = ('UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"',)
    if entries != expected:
        errors.append("registered Lean-freeze validator step environment must be exact; Python startup/path overrides are forbidden")
    if len(re.findall(r"(?m)^        env:\s*$", freeze_step)) != 1:
        errors.append("registered Lean-freeze validator step must contain exactly one env mapping")
    return errors


def _checkout_revision_errors(job_body: str) -> list[str]:
    checkout_blocks = [block for block in _step_blocks(job_body) if re.search(r"(?m)^uses:\s*actions/checkout@", block)]
    if len(checkout_blocks) != 1:
        return ["registered Lean-freeze workflow must contain exactly one checkout step"]
    checkout = checkout_blocks[0]
    ref_key = r"(?:ref|\"ref\"|'ref')"
    if re.search(rf"(?m)^\s{{8,}}{ref_key}\s*:", checkout):
        return ["registered Lean-freeze checkout must validate the triggering event revision and may not override ref"]
    return []


def workflow_contract_errors(text: str) -> list[str]:
    errors = list(_base.workflow_contract_errors(text))
    required_helper = '- "scripts/validate_lean_observation_foundation_pr21_pre_codex4.py"'
    for event in ("pull_request", "push"):
        event_paths = _base.workflow_event_paths(text, event)
        if event_paths is None or event_paths.count(required_helper) != 1:
            errors.append(f"registered Lean-freeze workflow {event} path trigger drift: {required_helper}")

    job_body = _base.workflow_job_block(text, "validate-corpus")
    if job_body is None:
        return errors
    errors.extend(_checkout_revision_errors(job_body))
    freeze_step = _base.workflow_named_step_block(job_body, "Validate Lean observation source freeze")
    if freeze_step is not None:
        errors.extend(_exact_freeze_environment_errors(freeze_step))
    return errors


def human_dependency_graph_errors(freeze: dict[str, object], human: str) -> list[str]:
    graph = freeze.get("dependency_graph")
    if not isinstance(graph, dict):
        return ["Lean observation machine dependency graph malformed"]
    section = _base._frozen.section(human, "## Dependency graph")
    if section is None:
        return ["Lean observation human dependency graph missing"]
    code = re.search(r"(?s)```text\n(?P<body>.*?)```", section)
    if code is None:
        return ["Lean observation human dependency graph code block missing"]

    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    parent: str | None = None
    malformed = False
    for raw in code.group("body").splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.fullmatch(r"UFT-OBS-\d{3}", line):
            parent = line
            nodes.add(line)
            continue
        arrow = re.fullmatch(r"->\s*(UFT-OBS-\d{3})", line)
        if arrow is not None and parent is not None:
            child = arrow.group(1)
            nodes.add(child)
            edges.append((parent, child))
            continue
        malformed = True

    expected_nodes = set(graph)
    expected_edges: set[tuple[str, str]] = set()
    for theorem_id, dependencies in graph.items():
        if not isinstance(theorem_id, str) or not isinstance(dependencies, list) or any(not isinstance(dep, str) for dep in dependencies):
            return ["Lean observation machine dependency graph malformed"]
        for dependency in dependencies:
            expected_edges.add((dependency, theorem_id))

    if malformed or nodes != expected_nodes or set(edges) != expected_edges or len(edges) != len(expected_edges):
        return ["Lean observation human dependency graph drift"]
    return []


def validate_documents(freeze, source_theorems, source_counterexamples, base_contract, human, roadmap, readme, *, check_paths: bool = True, require_basis_objects: bool = False):
    result = _base.validate_documents(
        freeze,
        source_theorems,
        source_counterexamples,
        base_contract,
        human,
        roadmap,
        readme,
        check_paths=check_paths,
        require_basis_objects=require_basis_objects,
    )
    errors = list(result.get("errors", []))
    errors.extend(human_dependency_graph_errors(freeze, human))
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def validate(*, require_basis_objects: bool = True):
    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI, WORKFLOW, FROZEN, BASE]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing Lean observation freeze authority: {x}" for x in missing],
            "batch_id": None,
            "theorem_count": 0,
            "deferred_count": 0,
            "module_count": 0,
            "basis_objects_verified": False,
        }
    result = validate_documents(
        load_json(FREEZE),
        load_json(SOURCE_THEOREMS),
        load_json(SOURCE_COUNTEREXAMPLES),
        load_json(BASE_CONTRACT),
        HUMAN.read_text(encoding="utf-8"),
        ROADMAP.read_text(encoding="utf-8"),
        README4AI.read_text(encoding="utf-8"),
        check_paths=True,
        require_basis_objects=require_basis_objects,
    )
    errors = list(result.get("errors", []))
    errors.extend(workflow_contract_errors(WORKFLOW.read_text(encoding="utf-8")))
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Lean observation source freeze: ok ({result['theorem_count']} theorems, {result['module_count']} modules, {result['deferred_count']} deferred)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
