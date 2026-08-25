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
EXPECTED_WORKFLOW_BLOB = "0cfe3a240010a07d3588682b806bed427c7d2aa8"
EXPECTED_WORKFLOW_PATHS = (
    '- "research/vopson/**"',
    '- "scripts/validate_vopson_corpus.py"',
    '- "scripts/render_vopson_docs.py"',
    '- "scripts/validate_reproducibility.py"',
    '- "scripts/validate_lean_observation_foundation.py"',
    '- "scripts/validate_lean_observation_foundation_pr21_pre_codex4.py"',
    '- "scripts/validate_lean_observation_foundation_pr21_frozen.py"',
    '- "tests/**"',
    '- "machine/**"',
    '- "README.md"',
    '- "README4AI.md"',
    '- "ROADMAP.md"',
    '- "AGENTS.md"',
    '- "docs/REPRODUCIBILITY.md"',
    '- "theory/LEAN_OBSERVATION_FOUNDATION.md"',
    '- "UFTID/**"',
    '- "**/*.lean"',
    '- "lean-toolchain"',
    '- "lakefile.toml"',
    '- "lake-manifest.json"',
    '- ".github/workflows/**"',
)
_EXPECTED_WORKFLOW_PATH_LINES = "".join(f"      {entry}\n" for entry in EXPECTED_WORKFLOW_PATHS)
EXPECTED_WORKFLOW_EVENT_BODIES = {
    "pull_request": "    paths:\n" + _EXPECTED_WORKFLOW_PATH_LINES,
    "push": "    branches: [main]\n    paths:\n" + _EXPECTED_WORKFLOW_PATH_LINES + "\n",
}
EXPECTED_FREEZE_STEP_BODY = (
    "        env:\n"
    '          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"\n'
    "        run: python scripts/validate_lean_observation_foundation.py\n\n"
)


def local_git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def text_git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
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


def _exact_freeze_command_errors(freeze_step: str) -> list[str]:
    normalized_step = _normalize_yaml_escapes_for_action_count(freeze_step)
    run_key = r'(?:run|"run"|\'run\')'
    values = tuple(
        match.group("value")
        for match in re.finditer(rf"(?m)^        {run_key}\s*:(?P<value>[^\n]*)$", normalized_step)
    )
    expected = (" python scripts/validate_lean_observation_foundation.py",)
    if values != expected:
        return ["registered Lean-freeze validator command must be exact and blocking"]
    return []


def _normalize_yaml_escapes_for_action_count(text: str) -> str:
    """Expose YAML double-quoted escapes before counting action identities."""
    normalized = re.sub(r"\\x([0-9a-fA-F]{2})", lambda match: chr(int(match.group(1), 16)), text)
    normalized = re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match.group(1), 16)), normalized)
    normalized = re.sub(r"\\U([0-9a-fA-F]{8})", lambda match: chr(int(match.group(1), 16)), normalized)
    normalized = normalized.replace(r"\/", "/")
    return re.sub(r"\\\r?\n[ \t]*", "", normalized)


def _checkout_revision_errors(job_body: str) -> list[str]:
    # Count before interpreting step layout: GitHub accepts quoted keys,
    # flow mappings, YAML escapes, and aliases that evade a line-oriented
    # subset parser while still replacing the validated workspace.
    normalized_job = _normalize_yaml_escapes_for_action_count(job_body)
    alias_or_merge = (
        r"(?im)(?:(?:^\s*-?\s*|[,{]\s*)(?:(?:uses|\"uses\"|'uses')|<<)\s*:\s*\*"
        r"|^\s*-\s*\*)"
    )
    if re.search(alias_or_merge, normalized_job):
        return ["registered Lean-freeze workflow may not use YAML aliases or merge keys in executable steps"]
    if len(re.findall(r"(?i)actions/checkout@", normalized_job)) != 1:
        return ["registered Lean-freeze workflow must contain exactly one checkout step"]

    checkout_uses = r"(?:uses|\"uses\"|'uses')\s*:\s*(?:\"|')?actions/checkout@"
    checkout_blocks = [block for block in _step_blocks(job_body) if re.search(rf"(?m)^{checkout_uses}", block)]
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

    mappings = list(re.finditer(r"(?m)^        with:\n(?P<body>(?:          [^\n]+\n)+)", checkout))
    expected_inputs = ("persist-credentials: false", "fetch-depth: 0")
    if len(mappings) != 1:
        errors.append("registered Lean-freeze checkout must use exactly one canonical block input mapping")
    else:
        entries = tuple(line.strip() for line in mappings[0].group("body").splitlines() if line.strip())
        if entries != expected_inputs:
            errors.append("registered Lean-freeze checkout inputs must be exact; revision, repository, path, and credential overrides are forbidden")
    return errors


def workflow_contract_errors(text: str) -> list[str]:
    errors = list(_base.workflow_contract_errors(text))
    if text_git_blob_sha(text) != EXPECTED_WORKFLOW_BLOB:
        errors.append("registered Lean-freeze workflow complete Git blob drift")
    required_helper = '- "scripts/validate_lean_observation_foundation_pr21_pre_codex4.py"'
    for event in ("pull_request", "push"):
        event_paths = _base.workflow_event_paths(text, event)
        event_body = _base.workflow_event_block(text, event)
        if event_paths is None or event_paths.count(required_helper) != 1:
            errors.append(f"registered Lean-freeze workflow {event} path trigger drift: {required_helper}")
        if event_body != EXPECTED_WORKFLOW_EVENT_BODIES[event] or event_paths != EXPECTED_WORKFLOW_PATHS:
            errors.append(f"registered Lean-freeze workflow {event} path list must match the exact canonical ordered set")

    job_body = _base.workflow_job_block(text, "validate-corpus")
    if job_body is None:
        return errors
    errors.extend(_checkout_revision_errors(job_body))
    freeze_step = _base.workflow_named_step_block(job_body, "Validate Lean observation source freeze")
    if freeze_step is not None:
        errors.extend(_exact_freeze_environment_errors(freeze_step))
        errors.extend(_exact_freeze_command_errors(freeze_step))
        if freeze_step != EXPECTED_FREEZE_STEP_BODY:
            errors.append("registered Lean-freeze validator step must match the exact canonical body")
    return errors


def _canonical_text_blocks(text: str, block_error: str) -> tuple[tuple[str, ...] | None, list[str]]:
    """Parse only canonical, unindented triple-backtick text fences."""
    if "<!--" in text or "-->" in text:
        return None, [block_error]
    blocks: list[str] = []
    body_lines: list[str] = []
    inside = False
    for line in text.splitlines():
        if re.fullmatch(r"\s*(?:`{3,}|~{3,})(?:[^`]*)?", line) is None:
            if inside:
                body_lines.append(line)
            continue
        if not inside:
            if line != "```text":
                return None, [block_error]
            inside = True
            body_lines = []
        else:
            if line != "```":
                return None, [block_error]
            blocks.append("\n".join(body_lines) + "\n")
            inside = False
    if inside or not blocks:
        return None, [block_error]
    return tuple(blocks), []


def _canonical_human_section(human: str, heading: str) -> str | None:
    lines = human.splitlines()
    exact = [line for line in lines if line == heading]
    near = [line for line in lines if line.strip().casefold() == heading.casefold()]
    if len(exact) != 1 or len(near) != 1:
        return None
    return _base._frozen.section(human, heading)


def _human_text_blocks(human: str, heading: str, missing_error: str, block_error: str) -> tuple[tuple[str, ...] | None, list[str]]:
    section = _canonical_human_section(human, heading)
    if section is None:
        return None, [missing_error]
    return _canonical_text_blocks(section, block_error)


def _human_text_block(human: str, heading: str, missing_error: str, block_error: str) -> tuple[str | None, list[str]]:
    blocks, errors = _human_text_blocks(human, heading, missing_error, block_error)
    if blocks is None:
        return None, errors
    if len(blocks) != 1:
        return None, [block_error]
    return blocks[0], []


def _block_lines(block: str) -> tuple[str, ...]:
    return tuple(line.strip() for line in block.splitlines() if line.strip())


def human_hard_boundary_errors(freeze: dict[str, object], human: str) -> list[str]:
    expected = freeze.get("hard_boundaries")
    if not isinstance(expected, list) or not expected or any(not isinstance(item, str) for item in expected):
        return ["Lean observation machine hard boundaries malformed"]

    heading = "## Frozen source authority"
    if _canonical_human_section(human, heading) is None:
        return ["Lean observation human hard-boundary preamble missing"]
    lines = human.splitlines()
    matches = [index for index, line in enumerate(lines) if line == heading]
    preamble = "\n".join(lines[:matches[0]])
    blocks, errors = _canonical_text_blocks(
        preamble,
        "Lean observation human hard-boundary code block missing",
    )
    if blocks is None:
        return errors
    if len(blocks) != 1 or _block_lines(blocks[0]) != tuple(expected):
        return ["Lean observation human hard-boundary block drift"]
    return []


def human_batch_selection_errors(freeze: dict[str, object], human: str) -> list[str]:
    theorem_ids = freeze.get("theorem_ids")
    deferred_ids = freeze.get("deferred_theorem_ids")
    boundaries = freeze.get("hard_boundaries")
    if (
        not isinstance(theorem_ids, list)
        or not theorem_ids
        or any(not isinstance(item, str) for item in theorem_ids)
        or not isinstance(deferred_ids, list)
        or not deferred_ids
        or any(not isinstance(item, str) for item in deferred_ids)
        or not isinstance(boundaries, list)
        or any(not isinstance(item, str) for item in boundaries)
    ):
        return ["Lean observation machine batch selection malformed"]

    blocks, errors = _human_text_blocks(
        human,
        "## Batch selection",
        "Lean observation human batch selection missing",
        "Lean observation human batch-selection code blocks drift",
    )
    if blocks is None:
        return errors
    deferred_boundaries = tuple(
        boundary for boundary in boundaries if boundary.startswith("UFT-OBS-005_DEFERRED")
    )
    if len(deferred_boundaries) != 1:
        return ["Lean observation machine deferred-theorem boundary malformed"]
    if len(blocks) != 3:
        return ["Lean observation human batch-selection code blocks drift"]

    frozen_projection = "Frozen in batch 001:\n\n```text\n" + "\n".join(theorem_ids) + "\n```"
    deferred_projection = "Deferred to a later Lean batch:\n\n```text\n" + "\n".join(deferred_ids) + "\n```"

    result: list[str] = []
    if section := _canonical_human_section(human, "## Batch selection"):
        if section.count(frozen_projection) != 1 or section.count(deferred_projection) != 1:
            result.append("Lean observation human batch-selection labels drift")
        elif section.index(frozen_projection) > section.index(deferred_projection):
            result.append("Lean observation human batch-selection ordering drift")
    if _block_lines(blocks[0]) != tuple(theorem_ids):
        result.append("Lean observation human frozen theorem list drift")
    if _block_lines(blocks[1]) != tuple(deferred_ids):
        result.append("Lean observation human deferred theorem list drift")
    if _block_lines(blocks[2]) != deferred_boundaries:
        result.append("Lean observation human deferred-theorem boundary drift")
    return result


def human_dependency_graph_errors(freeze: dict[str, object], human: str) -> list[str]:
    graph = freeze.get("dependency_graph")
    if not isinstance(graph, dict):
        return ["Lean observation machine dependency graph malformed"]
    blocks, errors = _human_text_blocks(
        human,
        "## Dependency graph",
        "Lean observation human dependency graph missing",
        "Lean observation human dependency graph code block missing",
    )
    if blocks is None:
        return errors
    if len(blocks) != 2:
        return ["Lean observation human dependency graph code block missing"]
    body = blocks[0]

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


def human_counterexample_dependency_errors(freeze: dict[str, object], human: str) -> list[str]:
    records = freeze.get("theorems")
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        return ["Lean observation machine counterexample dependency map malformed"]

    expected_by_counterexample: dict[str, list[str]] = {}
    for record in records:
        theorem_id = record.get("id")
        dependencies = record.get("counterexample_dependencies")
        if (
            not isinstance(theorem_id, str)
            or not isinstance(dependencies, list)
            or any(not isinstance(item, str) for item in dependencies)
        ):
            return ["Lean observation machine counterexample dependency map malformed"]
        for counterexample_id in dependencies:
            expected_by_counterexample.setdefault(counterexample_id, []).append(theorem_id)

    blocks, errors = _human_text_blocks(
        human,
        "## Dependency graph",
        "Lean observation human dependency graph missing",
        "Lean observation human counterexample dependency code block missing",
    )
    if blocks is None:
        return errors
    if len(blocks) != 2:
        return ["Lean observation human counterexample dependency code block missing"]

    parsed: list[tuple[str, tuple[str, ...]]] = []
    malformed = False
    for raw in blocks[1].splitlines():
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(
            r"(CX-OBS-\d{3})\s*->\s*(UFT-OBS-\d{3}(?:,\s*UFT-OBS-\d{3})*)",
            line,
        )
        if match is None:
            malformed = True
            continue
        theorem_ids = tuple(item.strip() for item in match.group(2).split(","))
        parsed.append((match.group(1), theorem_ids))

    expected = [
        (counterexample_id, tuple(expected_by_counterexample[counterexample_id]))
        for counterexample_id in sorted(expected_by_counterexample)
    ]
    section = _canonical_human_section(human, "## Dependency graph")
    expected_block = "Adversarial companions remain separately typed:\n\n```text\n" + "\n".join(
        counterexample_id + " -> " + ", ".join(theorem_ids)
        for counterexample_id, theorem_ids in expected
    ) + "\n```"
    expected_nonpremise = "Counterexamples are not theorem premises and executable witnesses are not Lean proofs."
    if (
        malformed
        or parsed != expected
        or section is None
        or section.count(expected_block) != 1
        or section.count(expected_nonpremise) != 1
    ):
        return ["Lean observation human counterexample dependency graph drift"]
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


def _toolchain_claim_clauses(text: str) -> tuple[str, ...]:
    return tuple(
        clause.strip()
        for clause in re.split(r"(?<=[.!?])\s+|\n+", text)
        if clause.strip()
    )


def _noncurrent_toolchain_match(clause: str, match: re.Match[str]) -> bool:
    prefix = clause[:match.start()].casefold()
    suffix = clause[match.end():].casefold()
    matched = match.group(0).casefold()

    contrasts = list(re.finditer(r"\b(?:but|yet|however)\b", matched))
    if contrasts:
        positive_offset = contrasts[-1].end()
        assertion_prefix = clause[:match.start() + positive_offset].casefold()
        current_scope = matched[positive_offset:]
        current_context = current_scope
    else:
        assertion_prefix = prefix
        current_scope = matched
        current_context = assertion_prefix[-96:] + " " + current_scope

    immediate_prefix = assertion_prefix[-96:]
    if re.search(r"\b(?:no|neither|nor)\s*$|\bnot\s+(?:(?:a|one|the|this)\s+|(?:true|the\s+case)\s+that\s*)$", immediate_prefix):
        return True
    if re.search(r"\b(?:must\s+not|does\s+not|do\s+not|cannot)\s+(?:claim|state|say)\b", immediate_prefix):
        return True
    if re.search(r"\b(?:rejects?|rejected|forbids?|forbade|prohibits?|prohibited|disallows?|disallowed)\s+(?:(?:the|a)\s+)?(?:claim\s+)?that\s*$", immediate_prefix):
        return True
    if re.search(r"^\s*(?:is|are|was|were|must\s+be|should\s+be)\s+(?:rejected|forbidden|prohibited|disallowed|false|untrue|incorrect|invalid)\b", suffix):
        return True
    if re.search(r"\bwhether\s+(?:the\s+)?$|\b(?:unclear|unknown|uncertain)\s+whether\s+(?:the\s+)?$", immediate_prefix):
        return True
    if re.search(r"^\s*(?:is|are|was|were|remains?)\s+(?:unknown|unclear|uncertain|undetermined|unresolved)\b", suffix):
        return True

    temporal_context = prefix + " " + suffix[:128]
    forbidden_order = (
        re.search(r"\bpending\b", temporal_context) is not None
        or re.search(
            r"\b(?:before|until)\b.{0,96}\b(?:source(?:-release)?\s+tag|target\s+binding|release\s+gate)\b",
            temporal_context,
        ) is not None
    )
    if forbidden_order:
        return False

    current = (
        re.search(r"\b(?:now|already|currently)\b", current_context) is not None
        or re.search(r"\bcurrent\s+(?:the\s+)?$", immediate_prefix) is not None
    )
    if not current and re.search(r"\b(?:expected|target|required|future|later|planned|will|shall|must|should|would|may|might)\b", prefix):
        return True
    completion_side = (
        r"(?:\bafter\b.{0,96}\b(?:release|(?:immutable\s+)?source(?:-release)?\s+tag|target\s+binding)\b)"
        r"|(?:\bonce\b.{0,96}\b(?:release|(?:immutable\s+)?source(?:-release)?\s+tag|target\s+binding)\b)"
        r"|(?:\bwhen\b.{0,96}\b(?:target\s+binding|(?:immutable\s+)?source(?:-release)?\s+tag)\b.{0,48}\b(?:completes?|exists?|is\s+(?:cut|published|bound|complete))\b)"
    )
    if not current and re.search(completion_side, temporal_context):
        return True
    return False


def toolchain_promotion(text: str) -> bool:
    dependency = r"(?:Lean|Lake|Mathlib)(?:\s+v?\d+(?:\.\d+)*)?"
    named_revision = r"(?:Lean|Lake|Mathlib)\s+(?:toolchain\s+)?(?:version|revision|commit)(?:\s+[A-Za-z0-9][A-Za-z0-9._-]*)?"
    separator = r"(?:\s*(?:/|\+|,)\s*(?:and\s+)?|\s+and\s+)"
    dependency_group = rf"{dependency}(?:{separator}{dependency})*"
    toolchain_subject = rf"(?:(?:the\s+)?toolchain|(?:the\s+)?{named_revision}|(?:the\s+)?{dependency_group}(?:\s+(?:toolchain|versions?))?)"
    completed = r"(?:pinned|selected|locked|fixed|frozen|chosen)"
    degree = r"(?:(?:fully|completely|exactly|immutably)\s+)?"
    copula = r"(?:is|are|was|were|has|have|had)\s+(?:now\s+|already\s+|currently\s+)?(?:been\s+)?"
    patterns = (
        rf"\b{toolchain_subject}\b\s+{copula}{degree}{completed}\b",
        rf"\b{toolchain_subject}\b.{{0,120}}\b(?:but|yet|however)\b\s+(?:it\s+)?{copula}{degree}{completed}\b",
        rf"\b(?:we|this\s+batch|the\s+batch|the\s+project|UFT-ID)\b\s+(?:(?:has|have|had)\s+)?(?:now\s+|already\s+|currently\s+)?{degree}{completed}\s+(?:the\s+)?{toolchain_subject}\b",
        rf"\b{degree}{completed}\s+(?:the\s+)?(?:toolchain|{dependency_group}\s+(?:toolchain|versions?))\b",
        r"\btoolchain(?:\s+status)?\s*:\s*PINNED\b",
        r"\btoolchain\s+(?:status|state)\s+(?:is|was|remains?)\s+(?:now\s+|currently\s+)?PINNED\b",
        r"\b(?:the\s+)?toolchain(?:\s+(?:status|state))?\s+(?:remains?|has\s+become|have\s+become|became|becomes)\s+(?:now\s+|currently\s+)?(?:(?:fully|completely|exactly|immutably)\s+)?PINNED\b",
        r"\btoolchain\s+pinning\s+(?:is|was|has\s+been)\s+(?:now\s+|already\s+)?(?:(?:fully|completely|exactly|immutably)\s+)?(?:complete|completed|done)\b",
        rf"\btoolchain\s*:\s*{dependency_group}\b",
        r"\b(?:Lean|Lake|Mathlib)\s+(?:toolchain\s+)?version\s*:\s*v?\d+(?:\.\d+)*\b",
    )
    for clause in _toolchain_claim_clauses(text):
        scan_clause = re.sub(r"[*_`]", " ", clause)
        for pattern in patterns:
            for match in re.finditer(pattern, scan_clause, flags=re.IGNORECASE):
                if not _noncurrent_toolchain_match(scan_clause, match):
                    return True
    return False


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
    errors.extend(human_hard_boundary_errors(freeze, human))
    errors.extend(human_batch_selection_errors(freeze, human))
    errors.extend(human_dependency_graph_errors(freeze, human))
    errors.extend(human_counterexample_dependency_errors(freeze, human))
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
