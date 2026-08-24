#!/usr/bin/env python3
"""Live PR #21 wrapper around the frozen pre-latest source-freeze validator.

The frozen module preserves all theorem, human-status, pre-tag Lean embargo, and
roadmap checks already reviewed on the previous clean head. This wrapper adds
complete PR9 basis dependency closure, registered-workflow enforcement, and
cross-surface human promotion guards.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / 'scripts/validate_lean_observation_foundation_pr21_frozen.py'
FREEZE = ROOT / "machine/lean_observation_foundation_contract.json"
SOURCE_THEOREMS = ROOT / "machine/observation_theorems.json"
SOURCE_COUNTEREXAMPLES = ROOT / "machine/observation_counterexamples.json"
BASE_CONTRACT = ROOT / "machine/contract.json"
HUMAN = ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md"
ROADMAP = ROOT / "ROADMAP.md"
README4AI = ROOT / "README4AI.md"
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"
BASIS_COMMIT = '6f3aeb7f4ac14389e7a08d2976c8c0d16549c093'


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_frozen = load_module("pr21_lean_observation_freeze_frozen", FROZEN)
EXPECTED_THEOREMS = _frozen.EXPECTED_THEOREMS
EXPECTED_GRAPH = _frozen.EXPECTED_GRAPH
EXPECTED_MODULE_MAP = _frozen.EXPECTED_MODULE_MAP
EXPECTED_BOUNDARIES = _frozen.EXPECTED_BOUNDARIES
graph_is_acyclic = _frozen.graph_is_acyclic
pretag_lean_files = _frozen.pretag_lean_files
OLD_SOURCE_BLOBS = dict(_frozen.EXPECTED_SOURCE_BLOBS)

EXPECTED_SOURCE_BLOBS = {
    'machine/contract.json': '2aa342b83a698577c92ac7964ea0d8fcfc102a0b',
    'machine/formalization_contract.json': '1c0827b5f760b08d8d375659667ca0067f722aa8',
    'machine/observation_contract.json': '8eede68aa53c92666d7a25641a9e7e699668aea0',
    'machine/observation_specs.json': '1f1868054763fa3c9e84c9a8664b0c3134ffcee8',
    'machine/observation_theorems.json': 'fbb1d1081fe2fed6980068f9630a8890b31794b9',
    'machine/observation_counterexamples.json': '1b8551ffb124076b9d50de4f13b4e9ceb0246a04',
    'theory/OBSERVATION_CALCULUS.md': '8bf8fb39c3b7b6d08fdab24261efa455b2ee3b4a',
    'scripts/validate_observation_specs.py': 'bdd68c1f7ff183f0efd7ae142c5ffcdc721dfd87',
    'experiments/observation/run.py': '55e02cee0b33136fb8ee22896fdd923b281e8a9c',
    'tests/test_pr9_observation.py': '5373773686d97d280d0a89c2bb0a6a953f6d7ec8',
    'experiments/run_pr9.py': '78d7bf1e6d5998f8665b99207559876350bbb639',
    'ROADMAP.md': '7a602769908e2ff83ae49a32539fd1a5a5340ce4',
}
BASIS_ONLY_MOVING_PATHS = {"machine/contract.json", "ROADMAP.md"}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def basis_source_object_errors(*, require_objects: bool) -> list[str]:
    errors: list[str] = []
    resolved = 0
    for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
        actual = basis_git_blob_sha(relpath)
        if actual is None:
            if require_objects:
                errors.append(f"basis commit object unavailable: {BASIS_COMMIT}:{relpath}")
            continue
        resolved += 1
        if actual != expected_sha:
            errors.append(f"basis commit Git blob mismatch: {relpath}")
    if require_objects and resolved != len(EXPECTED_SOURCE_BLOBS):
        errors.append("complete PR9 basis dependency closure was not resolved from Git objects")
    return errors


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    twice = (
        '      - "scripts/validate_lean_observation_foundation.py"',
        '      - "scripts/validate_lean_observation_foundation_pr21_frozen.py"',
        '      - "theory/LEAN_OBSERVATION_FOUNDATION.md"',
        '      - "README4AI.md"',
        '      - "ROADMAP.md"',
        '      - "UFTID/**"',
        '      - "**/*.lean"',
        '      - "lean-toolchain"',
        '      - "lakefile.toml"',
        '      - "lake-manifest.json"',
    )
    for anchor in twice:
        if text.count(anchor) != 2:
            errors.append(f"registered Lean-freeze workflow path trigger drift: {anchor.strip()}")
    direct = (
        '      - name: Validate Lean observation source freeze',
        '          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"',
        '        run: python scripts/validate_lean_observation_foundation.py',
        '          fetch-depth: 0',
        '          persist-credentials: false',
        'permissions:',
        '  contents: read',
    )
    for anchor in direct:
        if text.count(anchor) != 1:
            errors.append(f"registered Lean-freeze workflow direct validator/policy drift: {anchor.strip()}")
    return errors


def _frozen_views(freeze: dict[str, object], base_contract: dict[str, object]):
    old_freeze = copy.deepcopy(freeze)
    old_freeze["schema_version"] = "1.0.0"
    old_freeze["source_authorities"] = [
        {"path": path, "git_blob_sha": sha} for path, sha in OLD_SOURCE_BLOBS.items()
    ]
    old_base = copy.deepcopy(base_contract)
    authority = old_base.get("lean_observation_foundation_authority")
    if isinstance(authority, dict):
        authority["workflow"] = ".github/workflows/finite-adversarial.yml"
        authority.pop("frozen_validator", None)
    return old_freeze, old_base


def validate_documents(freeze, source_theorems, source_counterexamples, base_contract, human, roadmap, readme, *, check_paths: bool = True):
    old_freeze, old_base = _frozen_views(freeze, base_contract)
    result = _frozen.validate_documents(
        old_freeze, source_theorems, source_counterexamples, old_base,
        human, roadmap, readme, check_paths=check_paths,
    )
    errors = list(result.get("errors", []))

    # The frozen validator already promotion-scans the dedicated Lean human
    # authority. README4AI and ROADMAP are also human authority inputs to this
    # live wrapper, so they must be equally unable to claim completed Lean
    # verification while the release gate and every theorem remain unverified.
    for surface_name, surface_text in (("README4AI", readme), ("ROADMAP", roadmap)):
        if _frozen.human_promotion_errors(surface_text):
            errors.append(f"Lean observation {surface_name} Lean verification promotion")

    if freeze.get("schema_version") != "1.0.1":
        errors.append("Lean observation freeze schema drift")
    expected_sources = [{"path": path, "git_blob_sha": sha} for path, sha in EXPECTED_SOURCE_BLOBS.items()]
    if freeze.get("source_authorities") != expected_sources:
        errors.append("Lean observation complete PR9 basis source closure drift")

    expected_authority = {
        "machine_contract": "machine/lean_observation_foundation_contract.json",
        "human": "theory/LEAN_OBSERVATION_FOUNDATION.md",
        "validator": "scripts/validate_lean_observation_foundation.py",
        "frozen_validator": 'scripts/validate_lean_observation_foundation_pr21_frozen.py',
        "tests": "tests/test_lean_observation_foundation.py",
        "source_theorems": "machine/observation_theorems.json",
        "source_counterexamples": "machine/observation_counterexamples.json",
        "source_observation_contract": "machine/observation_contract.json",
        "workflow": ".github/workflows/vopson-corpus.yml",
        "rule": "The first Lean observation batch freezes source theorem identity and dependency/module mapping only; it does not claim Lean proof, select a toolchain, or create the immutable source-release tag.",
    }
    if base_contract.get("lean_observation_foundation_authority") != expected_authority:
        errors.append("Lean observation live authority registration drift")

    if check_paths:
        for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
            path = ROOT / relpath
            if not path.is_file():
                errors.append(f"missing frozen basis dependency: {relpath}")
            elif relpath not in BASIS_ONLY_MOVING_PATHS and git_blob_sha(path) != expected_sha:
                errors.append(f"frozen current PR9 dependency blob drift: {relpath}")
        errors.extend(basis_source_object_errors(
            require_objects=os.environ.get("UFT_REQUIRE_BASIS_COMMIT_OBJECT") == "1"
        ))

    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def validate():
    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI, WORKFLOW, FROZEN]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        return {"status": "error", "errors": [f"missing Lean observation freeze authority: {x}" for x in missing], "batch_id": None, "theorem_count": 0, "deferred_count": 0, "module_count": 0}
    result = validate_documents(
        load_json(FREEZE), load_json(SOURCE_THEOREMS), load_json(SOURCE_COUNTEREXAMPLES),
        load_json(BASE_CONTRACT), HUMAN.read_text(encoding="utf-8"),
        ROADMAP.read_text(encoding="utf-8"), README4AI.read_text(encoding="utf-8"),
        check_paths=True,
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
