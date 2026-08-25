#!/usr/bin/env python3
"""Live PR #21 wrapper around the frozen pre-latest source-freeze validator.

The frozen module preserves all theorem, human-status, pre-tag Lean embargo, and
roadmap checks already reviewed on the previous clean head. This wrapper adds
complete PR9 basis dependency closure, registered-workflow enforcement, and
cross-surface human promotion/nonclaim guards.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_lean_observation_foundation_pr21_frozen.py"
FREEZE = ROOT / "machine/lean_observation_foundation_contract.json"
SOURCE_THEOREMS = ROOT / "machine/observation_theorems.json"
SOURCE_COUNTEREXAMPLES = ROOT / "machine/observation_counterexamples.json"
BASE_CONTRACT = ROOT / "machine/contract.json"
HUMAN = ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md"
ROADMAP = ROOT / "ROADMAP.md"
README4AI = ROOT / "README4AI.md"
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"
BASIS_COMMIT = "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093"
EXPECTED_FROZEN_VALIDATOR_BLOB = "2355065a6811cf5f3b91132703953e46fbd0e877"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def frozen_validator_blob_errors(path: Path = FROZEN) -> list[str]:
    """Bind the compatibility validator before any of its authority is imported."""
    if not path.is_file():
        return ["frozen PR21 validator missing before import"]
    actual = git_blob_sha(path)
    if actual != EXPECTED_FROZEN_VALIDATOR_BLOB:
        return [
            "frozen PR21 validator blob drift: "
            f"expected {EXPECTED_FROZEN_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_preload_frozen_errors = frozen_validator_blob_errors()
if _preload_frozen_errors:
    raise RuntimeError("; ".join(_preload_frozen_errors))

_frozen = load_module("pr21_lean_observation_freeze_frozen", FROZEN)
EXPECTED_THEOREMS = _frozen.EXPECTED_THEOREMS
EXPECTED_GRAPH = _frozen.EXPECTED_GRAPH
EXPECTED_MODULE_MAP = _frozen.EXPECTED_MODULE_MAP
EXPECTED_BOUNDARIES = _frozen.EXPECTED_BOUNDARIES
graph_is_acyclic = _frozen.graph_is_acyclic
pretag_lean_files = _frozen.pretag_lean_files
OLD_SOURCE_BLOBS = dict(_frozen.EXPECTED_SOURCE_BLOBS)

EXPECTED_SOURCE_BLOBS = {
    "machine/contract.json": "2aa342b83a698577c92ac7964ea0d8fcfc102a0b",
    "machine/formalization_contract.json": "1c0827b5f760b08d8d375659667ca0067f722aa8",
    "machine/observation_contract.json": "8eede68aa53c92666d7a25641a9e7e699668aea0",
    "machine/observation_specs.json": "1f1868054763fa3c9e84c9a8664b0c3134ffcee8",
    "machine/observation_theorems.json": "fbb1d1081fe2fed6980068f9630a8890b31794b9",
    "machine/observation_counterexamples.json": "1b8551ffb124076b9d50de4f13b4e9ceb0246a04",
    "theory/OBSERVATION_CALCULUS.md": "8bf8fb39c3b7b6d08fdab24261efa455b2ee3b4a",
    "scripts/validate_observation_specs.py": "bdd68c1f7ff183f0efd7ae142c5ffcdc721dfd87",
    "experiments/observation/run.py": "55e02cee0b33136fb8ee22896fdd923b281e8a9c",
    "tests/test_pr9_observation.py": "5373773686d97d280d0a89c2bb0a6a953f6d7ec8",
    "experiments/run_pr9.py": "78d7bf1e6d5998f8665b99207559876350bbb639",
    "ROADMAP.md": "7a602769908e2ff83ae49a32539fd1a5a5340ce4",
}
BASIS_ONLY_MOVING_PATHS = {"machine/contract.json", "ROADMAP.md"}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def git_object_is_blob(object_sha: str) -> bool:
    exists = subprocess.run(["git", "cat-file", "-e", object_sha], cwd=ROOT, text=True, capture_output=True, check=False)
    if exists.returncode != 0:
        return False
    object_type = subprocess.run(["git", "cat-file", "-t", object_sha], cwd=ROOT, text=True, capture_output=True, check=False)
    return object_type.returncode == 0 and object_type.stdout.strip() == "blob"


def basis_git_blob_sha(relpath: str) -> str | None:
    result = subprocess.run(["git", "rev-parse", f"{BASIS_COMMIT}:{relpath}"], cwd=ROOT, text=True, capture_output=True, check=False)
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


def workflow_event_block(text: str, event: str) -> str | None:
    match = re.search(rf"(?ms)^  {re.escape(event)}:\n(?P<body>.*?)(?=^  [A-Za-z_][A-Za-z0-9_-]*:|^\S|\Z)", text)
    return match.group("body") if match is not None else None


def workflow_event_paths(text: str, event: str) -> tuple[str, ...] | None:
    body = workflow_event_block(text, event)
    if body is None:
        return None
    paths_match = re.search(r"(?m)^    paths:\n(?P<paths>(?:      - .*\n)+)", body)
    if paths_match is None:
        return None
    return tuple(line.strip() for line in paths_match.group("paths").splitlines())


def workflow_event_branches(text: str, event: str) -> tuple[str, ...] | None:
    body = workflow_event_block(text, event)
    if body is None:
        return None
    inline = re.search(r"(?m)^    branches:\s*\[(?P<values>[^\]]*)\]\s*$", body)
    if inline is not None:
        values = [value.strip().strip("\"'") for value in inline.group("values").split(",")]
        return tuple(value for value in values if value)
    block = re.search(r"(?m)^    branches:\n(?P<values>(?:      - .*\n)+)", body)
    if block is None:
        return None
    return tuple(line.strip()[2:].strip().strip("\"'") for line in block.group("values").splitlines() if line.strip()[2:].strip())


def workflow_event_key_present(text: str, event: str, key_name: str) -> bool:
    body = workflow_event_block(text, event)
    if body is None:
        return False
    escaped = re.escape(key_name)
    key = rf"(?:{escaped}|\"{escaped}\"|'{escaped}')"
    return re.search(rf"(?m)^    {key}\s*:", body) is not None


def workflow_job_block(text: str, job_name: str) -> str | None:
    match = re.search(rf"(?ms)^  {re.escape(job_name)}:\n(?P<body>.*?)(?=^  [A-Za-z_][A-Za-z0-9_-]*:|\Z)", text.split("jobs:\n", 1)[1] if "jobs:\n" in text else "")
    return match.group("body") if match is not None else None


def workflow_named_step_block(job_body: str, step_name: str) -> str | None:
    match = re.search(rf"(?ms)^      - name: {re.escape(step_name)}\n(?P<body>.*?)(?=^      - |\Z)", job_body)
    return match.group("body") if match is not None else None


def workflow_control_key_present(text: str, *, indent: int) -> bool:
    key = r"(?:if|continue-on-error|\"(?:if|continue-on-error)\"|'(?:if|continue-on-error)')"
    return re.search(rf"(?m)^{' ' * indent}{key}\s*:", text) is not None


def workflow_step_key_present(text: str, key_name: str, *, indent: int = 8) -> bool:
    escaped = re.escape(key_name)
    key = rf"(?:{escaped}|\"{escaped}\"|'{escaped}')"
    return re.search(rf"(?m)^{' ' * indent}{key}\s*:", text) is not None


def workflow_defaults_run_shell_present(text: str, *, indent: int) -> bool:
    """Fail closed on inherited workflow/job defaults in the registered freeze path.

    GitHub Actions accepts block and flow mappings for ``defaults.run.shell``.
    The canonical freeze workflow requires no inherited defaults at either scope,
    so rejecting the parent ``defaults`` key closes every equivalent YAML spelling
    instead of trying to enumerate syntax variants for a security-critical shell.
    """
    escaped = re.escape("defaults")
    key = rf"(?:{escaped}|\"{escaped}\"|'{escaped}')"
    return re.search(rf"(?m)^{' ' * indent}{key}\s*:", text) is not None


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    required_paths = (
        '- "scripts/validate_lean_observation_foundation.py"',
        '- "scripts/validate_lean_observation_foundation_pr21_frozen.py"',
        '- "theory/LEAN_OBSERVATION_FOUNDATION.md"',
        '- "README4AI.md"',
        '- "ROADMAP.md"',
        '- "UFTID/**"',
        '- "**/*.lean"',
        '- "lean-toolchain"',
        '- "lakefile.toml"',
        '- "lake-manifest.json"',
    )
    for event in ("pull_request", "push"):
        event_paths = workflow_event_paths(text, event)
        if event_paths is None:
            errors.append(f"registered Lean-freeze workflow missing {event}.paths")
            continue
        for anchor in required_paths:
            if event_paths.count(anchor) != 1:
                errors.append(f"registered Lean-freeze workflow {event} path trigger drift: {anchor}")

    if workflow_event_key_present(text, "pull_request", "types"):
        errors.append("registered Lean-freeze workflow pull_request activity types must remain unrestricted")
    if workflow_event_key_present(text, "pull_request", "branches") or workflow_event_key_present(text, "pull_request", "branches-ignore"):
        errors.append("registered Lean-freeze workflow pull_request branch filters must remain unrestricted")
    if workflow_event_branches(text, "push") != ("main",):
        errors.append("registered Lean-freeze workflow push branch restriction must be exactly main")
    if workflow_defaults_run_shell_present(text, indent=0):
        errors.append("registered Lean-freeze workflow may not inherit defaults.run.shell at workflow scope")

    direct = (
        '      - name: Validate Lean observation source freeze',
        '          fetch-depth: 0',
        '          persist-credentials: false',
        'permissions:',
        '  contents: read',
    )
    for anchor in direct:
        if text.count(anchor) != 1:
            errors.append(f"registered Lean-freeze workflow direct validator/policy drift: {anchor.strip()}")

    job_body = workflow_job_block(text, "validate-corpus")
    if job_body is None:
        errors.append("registered Lean-freeze workflow missing validate-corpus job")
        return errors
    job_header = job_body.split("    steps:\n", 1)[0]
    if workflow_control_key_present(job_header, indent=4):
        errors.append("registered Lean-freeze workflow validate-corpus job may not be conditional or nonblocking")
    if workflow_defaults_run_shell_present(job_body, indent=4):
        errors.append("registered Lean-freeze workflow validate-corpus may not inherit defaults.run.shell")

    freeze_step = workflow_named_step_block(job_body, "Validate Lean observation source freeze")
    if freeze_step is None:
        errors.append("registered Lean-freeze workflow missing named freeze step")
    else:
        if workflow_control_key_present(freeze_step, indent=8):
            errors.append("registered Lean-freeze validator step may not be conditional or nonblocking")
        if workflow_step_key_present(freeze_step, "shell"):
            errors.append("registered Lean-freeze validator step may not override its executing shell")
        required_step = (
            '        env:',
            '          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"',
            '        run: python scripts/validate_lean_observation_foundation.py',
        )
        for anchor in required_step:
            if freeze_step.count(anchor) != 1:
                errors.append(f"registered Lean-freeze named step command/env drift: {anchor.strip()}")
        if len(re.findall(r"(?m)^        run:", freeze_step)) != 1:
            errors.append("registered Lean-freeze named step must contain exactly one run directive")
    return errors


def theorem_scoped_lean_promotion(text: str) -> bool:
    subject = r"(?:UFT-OBS-\d{3}|LEAN-OBS-BATCH-\d{3})"
    completed = r"(?:proved|proven|verified|checked|formalized|formalised|complete)"
    participle = r"(?:proved|proven|verified|checked|formalized|formalised|certified)"
    active = r"(?:proves?|verifies?|checks?|formalizes?|formalises?|certifies?)"
    simple_past = r"(?:proved|proven|verified|checked|formalized|formalised|certified)"
    proof_noun = r"(?:proofs?|verification|formalization|formalisation|certificate|certification)"
    patterns = (
        rf"(?is)\b{subject}\b.{{0,180}}\b(?:has|have|is|are|was|were)\s+(?:now\s+)?(?:been\s+)?(?:formally\s+)?{completed}\b.{{0,60}}\b(?:in|by|with)\s+Lean\b",
        rf"(?is)\bLean\b.{{0,60}}\b(?:proof|verification|formalization|formalisation)\b.{{0,100}}\b(?:for|of)\b.{{0,100}}\b{subject}\b.{{0,60}}\b(?:is|are|was|were|has|have)?\s*(?:now\s+)?(?:been\s+)?{completed}\b",
        rf"(?is)\bLean\b.{{0,40}}\b{active}\b.{{0,180}}\b{subject}\b",
        rf"(?is)\bLean\b.{{0,40}}\b(?:has|have|had)\s+(?:now\s+)?(?:formally\s+)?{participle}\b.{{0,180}}\b{subject}\b",
        rf"(?is)\bLean\b.{{0,40}}\b{simple_past}\b.{{0,180}}\b{subject}\b",
        rf"(?is)\b{subject}\b.{{0,180}}\b(?:now\s+)?(?:has|have|is|are|was|were)\s+(?:now\s+)?Lean\s+{proof_noun}\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def generic_batch_lean_promotion(text: str) -> bool:
    batch = r"(?:the\s+)?(?:frozen\s+)?(?:theorem\s+)?batch"
    patterns = (
        rf"(?is)\b{batch}\b.{{0,80}}\b(?:passed|completed|achieved|has|have|is|was|were)\b.{{0,50}}\bLean\b.{{0,30}}\b(?:verification|proofs?|formalization|formalisation|certification)\b",
        rf"(?is)\b{batch}\b.{{0,80}}\b(?:verified|proved|proven|checked|formalized|formalised|certified)\b.{{0,40}}\b(?:in|by|with)\s+Lean\b",
        rf"(?is)\bLean\b.{{0,30}}\b(?:verification|proofs?|formalization|formalisation|certification)\b.{{0,80}}\b{batch}\b.{{0,40}}\b(?:passed|complete|completed|verified|proved|proven|checked)\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def source_tag_promotion(text: str) -> bool:
    tag = r"(?:immutable\s+)?source[- ]release\s+tag"
    patterns = (
        rf"(?is)\b{tag}\b.{{0,60}}\b(?:has|have|is|was|were)\s+(?:now\s+)?(?:been\s+)?(?:cut|created|published|issued|recorded|tagged)\b",
        rf"(?is)\b{tag}\b.{{0,40}}\b(?:now\s+)?exists\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def theorem_nonclaim_reversal(text: str) -> bool:
    """Reject positive prose that asserts the inverse of a frozen theorem nonclaim."""
    attribution = r"(?:proves?|shows?|establishes?|implies?|means?)"
    forward_patterns = (
        rf"(?is)\bUFT-OBS-001\b.{{0,100}}\b{attribution}\b.{{0,100}}\bobservational equivalence\b.{{0,60}}\b(?:is|equals?|constitutes?)\b.{{0,30}}\bphysical identity\b",
        rf"(?is)\bUFT-OBS-002\b.{{0,100}}\b{attribution}\b.{{0,100}}\bquotient\b.{{0,60}}\b(?:is|equals?|constitutes?)\b.{{0,40}}\b(?:the\s+)?full codomain\b",
        rf"(?is)\bUFT-OBS-003\b.{{0,100}}\b{attribution}\b.{{0,100}}\bexact(?: mathematical)? reconstruction\b.{{0,100}}\b(?:physical state persisted|original physical state persisted|observed directly)\b",
        rf"(?is)\bUFT-OBS-004\b.{{0,100}}\b{attribution}\b.{{0,100}}\bnoninjectiv(?:ity|e)\b.{{0,80}}\b(?:forbids?|precludes?|rules? out)\b.{{0,80}}\b(?:partial|representative|probabilistic|task-specific)\b.{{0,30}}\breconstruction\b",
    )
    reverse_patterns = (
        rf"(?is)\bobservational equivalence\b\s+(?:is|equals?|constitutes?)\s+(?!not\b)(?:the\s+)?physical identity\b.{{0,120}}\bUFT-OBS-001\b.{{0,60}}\b{attribution}\b",
        rf"(?is)\b(?:the\s+)?quotient\b\s+(?:is|equals?|constitutes?)\s+(?!not\b)(?:canonically\s+)?(?:the\s+)?full codomain(?:\s+Y)?\b.{{0,120}}\bUFT-OBS-002\b.{{0,60}}\b{attribution}\b",
        rf"(?is)\bexact(?: mathematical)? reconstruction\b.{{0,100}}\b(?:establishes?|proves?|shows?|implies?|means?)\b.{{0,100}}\b(?:physical state persisted|original physical state persisted|observed directly)\b.{{0,120}}\bUFT-OBS-003\b.{{0,60}}\b{attribution}\b",
        rf"(?is)\bnoninjectiv(?:ity|e)\b.{{0,80}}\b(?:forbids?|precludes?|rules? out)\b.{{0,80}}\b(?:partial|representative|probabilistic|task-specific)\b.{{0,30}}\breconstruction\b.{{0,120}}\bUFT-OBS-004\b.{{0,60}}\b{attribution}\b",
    )
    return any(re.search(pattern, text) for pattern in (*forward_patterns, *reverse_patterns))


def _frozen_views(freeze: dict[str, object], base_contract: dict[str, object]):
    old_freeze = copy.deepcopy(freeze)
    old_freeze["schema_version"] = "1.0.0"
    old_freeze["source_authorities"] = [{"path": path, "git_blob_sha": sha} for path, sha in OLD_SOURCE_BLOBS.items()]
    old_base = copy.deepcopy(base_contract)
    authority = old_base.get("lean_observation_foundation_authority")
    if isinstance(authority, dict):
        authority["workflow"] = ".github/workflows/finite-adversarial.yml"
        authority.pop("frozen_validator", None)
    return old_freeze, old_base


def validate_documents(freeze, source_theorems, source_counterexamples, base_contract, human, roadmap, readme, *, check_paths: bool = True, require_basis_objects: bool = False):
    old_freeze, old_base = _frozen_views(freeze, base_contract)
    result = _frozen.validate_documents(old_freeze, source_theorems, source_counterexamples, old_base, human, roadmap, readme, check_paths=check_paths)
    errors = list(result.get("errors", []))

    for surface_name, surface_text in (("README4AI", readme), ("ROADMAP", roadmap)):
        if _frozen.human_promotion_errors(surface_text):
            errors.append(f"Lean observation {surface_name} Lean verification promotion")
    for surface_name, surface_text in (("human freeze", human), ("README4AI", readme), ("ROADMAP", roadmap)):
        if theorem_scoped_lean_promotion(surface_text):
            errors.append(f"Lean observation {surface_name} theorem-scoped Lean verification promotion")
        if generic_batch_lean_promotion(surface_text):
            errors.append(f"Lean observation {surface_name} generic batch Lean verification promotion")
        if source_tag_promotion(surface_text):
            errors.append(f"Lean observation {surface_name} source-tag completion promotion")
        if theorem_nonclaim_reversal(surface_text):
            errors.append(f"Lean observation {surface_name} frozen theorem nonclaim reversal")

    if _frozen.strip_code(_frozen.metadata(human, "Batch")) != "LEAN-OBS-BATCH-001":
        errors.append("Lean observation human batch identity drift")
    if _frozen.strip_code(_frozen.metadata(human, "Basis commit")) != BASIS_COMMIT:
        errors.append("Lean observation human basis commit drift")

    for theorem_id, expected in EXPECTED_THEOREMS.items():
        sec = _frozen.section(human, f"## {theorem_id} {expected['name']}")
        if sec is None:
            continue
        if _frozen.strip_code(_frozen.metadata(sec, "Proof reference")) != expected["proof_reference"]:
            errors.append(f"{theorem_id} human Proof reference drift")

    if freeze.get("schema_version") != "1.0.1":
        errors.append("Lean observation freeze schema drift")
    expected_sources = [{"path": path, "git_blob_sha": sha} for path, sha in EXPECTED_SOURCE_BLOBS.items()]
    if freeze.get("source_authorities") != expected_sources:
        errors.append("Lean observation complete PR9 basis source closure drift")

    expected_authority = {
        "machine_contract": "machine/lean_observation_foundation_contract.json",
        "human": "theory/LEAN_OBSERVATION_FOUNDATION.md",
        "validator": "scripts/validate_lean_observation_foundation.py",
        "frozen_validator": "scripts/validate_lean_observation_foundation_pr21_frozen.py",
        "tests": "tests/test_lean_observation_foundation.py",
        "source_theorems": "machine/observation_theorems.json",
        "source_counterexamples": "machine/observation_counterexamples.json",
        "source_observation_contract": "machine/observation_contract.json",
        "workflow": ".github/workflows/vopson-corpus.yml",
        "rule": "The first Lean observation batch freezes source theorem identity and dependency/module mapping only; it does not claim Lean proof, select a toolchain, or create the immutable source-release tag.",
    }
    if base_contract.get("lean_observation_foundation_authority") != expected_authority:
        errors.append("Lean observation live authority registration drift")

    basis_errors: list[str] = []
    if check_paths:
        errors.extend(frozen_validator_blob_errors())
        for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
            path = ROOT / relpath
            if not path.is_file():
                errors.append(f"missing frozen basis dependency: {relpath}")
            elif relpath not in BASIS_ONLY_MOVING_PATHS and git_blob_sha(path) != expected_sha:
                errors.append(f"frozen current PR9 dependency blob drift: {relpath}")
        if require_basis_objects:
            basis_errors = basis_source_object_errors()
            errors.extend(basis_errors)

    result["basis_objects_verified"] = bool(check_paths and require_basis_objects and not basis_errors)
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def validate(*, require_basis_objects: bool = True):
    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI, WORKFLOW, FROZEN]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        return {"status": "error", "errors": [f"missing Lean observation freeze authority: {x}" for x in missing], "batch_id": None, "theorem_count": 0, "deferred_count": 0, "module_count": 0, "basis_objects_verified": False}
    result = validate_documents(load_json(FREEZE), load_json(SOURCE_THEOREMS), load_json(SOURCE_COUNTEREXAMPLES), load_json(BASE_CONTRACT), HUMAN.read_text(encoding="utf-8"), ROADMAP.read_text(encoding="utf-8"), README4AI.read_text(encoding="utf-8"), check_paths=True, require_basis_objects=require_basis_objects)
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
