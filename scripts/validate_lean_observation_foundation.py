#!/usr/bin/env python3
"""Latest PR #21 hardening wrapper around the exact prior live validator.

The prior live validator is preserved byte-for-byte in
validate_lean_observation_foundation_pr21_pre_codex4.py. This wrapper adds
later hostile-review hardening without rewriting already-reviewed semantics:
workflow checkout identity, compatibility-validator identity, and exact human
projections of the frozen dependency graph, Lean module map, release ordering,
and pre-toolchain state.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/validate_lean_observation_foundation_pr21_pre_codex4.py"
EXPECTED_BASE_VALIDATOR_BLOB = "cb18daf549e87a94b64ae85b58369f9a2e329f91"


def local_git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def base_validator_blob_errors(path: Path = BASE) -> list[str]:
    """Bind the immediately prior live validator before executing its code."""
    if not path.is_file():
        return ["pre-Codex4 PR21 validator missing before import"]
    actual = local_git_blob_sha(path)
    if actual != EXPECTED_BASE_VALIDATOR_BLOB:
        return [
            "pre-Codex4 PR21 validator blob drift: "
            f"expected {EXPECTED_BASE_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


_preload_base_errors = base_validator_blob_errors()
if _preload_base_errors:
    raise RuntimeError("; ".join(_preload_base_errors))

_spec = importlib.util.spec_from_file_location("lean_observation_pr21_pre_codex4", BASE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load prior PR21 validator: {BASE}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__") and _name not in {
        "workflow_contract_errors", "validate_documents", "validate", "main",
        "frozen_validator_blob_errors", "basis_git_blob_sha", "basis_source_object_errors",
    }:
        globals()[_name] = getattr(_base, _name)


def frozen_validator_blob_errors(path: Path = FROZEN) -> list[str]:
    if not path.is_file():
        return ["frozen PR21 validator missing before import"]
    actual = git_blob_sha(path)
    if actual != EXPECTED_FROZEN_VALIDATOR_BLOB:
        return [
            "frozen PR21 validator blob drift: "
            f"expected {EXPECTED_FROZEN_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def basis_git_blob_sha(relpath: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{BASIS_COMMIT}:{relpath}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        return None
    return value if git_object_is_blob(value) else None


def basis_source_object_errors() -> list[str]:
    errors: list[str] = []
    resolved = 0
    for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
        actual = basis_git_blob_sha(relpath)
        if actual is None:
            errors.append(f"basis commit blob object unavailable: {BASIS_COMMIT}:{relpath}")
            continue
        resolved += 1
        if actual != expected_sha:
            errors.append(f"basis commit Git blob mismatch: {relpath}")
    if resolved != len(EXPECTED_SOURCE_BLOBS):
        errors.append("complete PR9 basis dependency closure was not resolved from readable Git blob objects")
    return errors


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
    repository_key = r"(?:repository|\"repository\"|'repository')"
    errors: list[str] = []
    if re.search(rf"(?m)^\s{{8,}}{ref_key}\s*:", checkout):
        errors.append("registered Lean-freeze checkout must validate the triggering event revision and may not override ref")
    if re.search(rf"(?m)^\s{{8,}}{repository_key}\s*:", checkout):
        errors.append("registered Lean-freeze checkout must validate this repository and may not override repository")
    return errors


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


def _human_text_block(human: str, heading: str, missing_error: str, block_error: str) -> tuple[str | None, list[str]]:
    section = _base._frozen.section(human, heading)
    if section is None:
        return None, [missing_error]
    code = re.search(r"(?s)```text\n(?P<body>.*?)```", section)
    if code is None:
        return None, [block_error]
    return code.group("body"), []


def human_dependency_graph_errors(freeze: dict[str, object], human: str) -> list[str]:
    graph = freeze.get("dependency_graph")
    if not isinstance(graph, dict):
        return ["Lean observation machine dependency graph malformed"]
    body, errors = _human_text_block(
        human,
        "## Dependency graph",
        "Lean observation human dependency graph missing",
        "Lean observation human dependency graph code block missing",
    )
    if body is None:
        return errors

    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    parent: str | None = None
    malformed = False
    for raw in body.splitlines():
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


def human_lean_module_map_errors(freeze: dict[str, object], human: str) -> list[str]:
    expected = freeze.get("lean_module_map")
    if not isinstance(expected, list) or any(not isinstance(item, dict) for item in expected):
        return ["Lean observation machine Lean module map malformed"]
    body, errors = _human_text_block(
        human,
        "## Expected Lean module map",
        "Lean observation human Lean module map missing",
        "Lean observation human Lean module map code block missing",
    )
    if body is None:
        return errors

    parsed: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    malformed = False
    module_re = re.compile(r"UFTID(?:\.[A-Za-z0-9_]+)+")
    path_re = re.compile(r"UFTID/[A-Za-z0-9_./-]+\.lean")
    theorem_re = re.compile(r"UFT-OBS-\d{3}")

    for raw in body.splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0 and module_re.fullmatch(line):
            if current is not None:
                parsed.append(current)
            current = {"module": line, "path": None, "depends_on": [], "theorem_ids": []}
            continue
        if current is None or indent == 0:
            malformed = True
            continue
        if path_re.fullmatch(line):
            if current["path"] is not None:
                malformed = True
            else:
                current["path"] = line
            continue
        if line.startswith("depends on "):
            dependency = line.removeprefix("depends on ").strip()
            if not module_re.fullmatch(dependency):
                malformed = True
            else:
                current["depends_on"].append(dependency)
            continue
        if theorem_re.fullmatch(line):
            current["theorem_ids"].append(line)
            continue
        malformed = True

    if current is not None:
        parsed.append(current)
    if any(item.get("path") is None for item in parsed):
        malformed = True
    if malformed or parsed != expected:
        return ["Lean observation human Lean module map drift"]
    return []


EXPECTED_RELEASE_BOUNDARY = (
    "FREEZE PR MERGED",
    "-> EXACT MERGED-MAIN CI + HOSTILE REVIEW",
    "-> IMMUTABLE SOURCE-RELEASE TAG",
    "-> QSOL-CONTEXT TARGET BINDING",
    "-> PIN LEAN / LAKE / MATHLIB",
    "-> LEAN PROOF IMPLEMENTATION",
)


def human_release_boundary_errors(freeze: dict[str, object], human: str) -> list[str]:
    gate = freeze.get("release_gate")
    if not isinstance(gate, dict):
        return ["Lean observation machine release gate malformed"]
    body, errors = _human_text_block(
        human,
        "## Release boundary",
        "Lean observation human release boundary missing",
        "Lean observation human release boundary code block missing",
    )
    if body is None:
        return errors
    actual = tuple(line.strip() for line in body.splitlines() if line.strip())
    if actual != EXPECTED_RELEASE_BOUNDARY:
        return ["Lean observation human release boundary ordering drift"]
    if gate.get("status") != "PENDING_POST_MERGE" or gate.get("source_tag") is not None:
        return ["Lean observation machine release gate drift"]
    return []


def toolchain_promotion(text: str) -> bool:
    subject = r"(?:Lean(?:\s+\d+(?:\.\d+)*)?|Lake(?:\s+\d+(?:\.\d+)*)?|Mathlib(?:\s+\d+(?:\.\d+)*)?|Lean\s*/\s*Lake\s*/\s*Mathlib|toolchain)"
    completed = r"(?:pinned|selected|locked|fixed|chosen|specified|versioned)"
    pattern = rf"(?is)(?<!No )\b{subject}\b.{{0,140}}\b(?:is|are|has|have|was|were)\s+(?:now\s+)?(?:been\s+)?(?!not\s){completed}\b"
    return re.search(pattern, text) is not None


def validate_documents(freeze, source_theorems, source_counterexamples, base_contract, human, roadmap, readme, *, check_paths: bool = True, require_basis_objects: bool = False):
    # Preserve the original module's mutation-test hooks by making its delegated
    # validation resolve these live wrapper functions, which tests may monkeypatch.
    _base.frozen_validator_blob_errors = frozen_validator_blob_errors
    _base.basis_git_blob_sha = basis_git_blob_sha
    _base.basis_source_object_errors = basis_source_object_errors
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
    errors.extend(human_lean_module_map_errors(freeze, human))
    errors.extend(human_release_boundary_errors(freeze, human))

    toolchain = freeze.get("toolchain")
    if isinstance(toolchain, dict) and toolchain.get("status") == "UNPINNED":
        for surface_name, surface_text in (("human freeze", human), ("README4AI", readme), ("ROADMAP", roadmap)):
            if toolchain_promotion(surface_text):
                errors.append(f"Lean observation {surface_name} premature toolchain-pinning promotion")

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
    errors.extend(base_validator_blob_errors())
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
