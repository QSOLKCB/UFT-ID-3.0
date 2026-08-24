#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASIS = "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093"

SOURCE_BLOBS = [
    ("machine/contract.json", "2aa342b83a698577c92ac7964ea0d8fcfc102a0b"),
    ("machine/formalization_contract.json", "1c0827b5f760b08d8d375659667ca0067f722aa8"),
    ("machine/observation_contract.json", "8eede68aa53c92666d7a25641a9e7e699668aea0"),
    ("machine/observation_specs.json", "1f1868054763fa3c9e84c9a8664b0c3134ffcee8"),
    ("machine/observation_theorems.json", "fbb1d1081fe2fed6980068f9630a8890b31794b9"),
    ("machine/observation_counterexamples.json", "1b8551ffb124076b9d50de4f13b4e9ceb0246a04"),
    ("theory/OBSERVATION_CALCULUS.md", "8bf8fb39c3b7b6d08fdab24261efa455b2ee3b4a"),
    ("scripts/validate_observation_specs.py", "bdd68c1f7ff183f0efd7ae142c5ffcdc721dfd87"),
    ("experiments/observation/run.py", "55e02cee0b33136fb8ee22896fdd923b281e8a9c"),
    ("tests/test_pr9_observation.py", "5373773686d97d280d0a89c2bb0a6a953f6d7ec8"),
    ("experiments/run_pr9.py", "78d7bf1e6d5998f8665b99207559876350bbb639"),
    ("ROADMAP.md", "7a602769908e2ff83ae49a32539fd1a5a5340ce4"),
]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, got {count}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    # Expand the machine freeze to the complete PR9 authority/receipt closure.
    freeze_path = ROOT / "machine/lean_observation_foundation_contract.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze["schema_version"] = "1.0.1"
    freeze["source_authorities"] = [
        {"path": path, "git_blob_sha": sha} for path, sha in SOURCE_BLOBS
    ]
    freeze_path.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Register the workflow that already directly validates the freeze and has
    # explicit human/Lean path triggers.
    contract_path = ROOT / "machine/contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    authority = contract.get("lean_observation_foundation_authority")
    if not isinstance(authority, dict):
        raise RuntimeError("lean observation authority missing from machine/contract.json")
    authority["workflow"] = ".github/workflows/vopson-corpus.yml"
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    replace_once(
        "theory/LEAN_OBSERVATION_FOUNDATION.md",
        "Frozen PR9 source authorities include the observation contract/spec/theorem/counterexample registries, the canonical human proof surface, validator, finite witness implementation, tests, and deterministic receipt runner. Their exact Git blob identities are stored in the machine freeze.",
        "Frozen PR9 source authorities include the central machine contract, formalization contract, observation contract/spec/theorem/counterexample registries, the canonical human proof surface, validator, finite witness implementation, tests, deterministic receipt runner, and the roadmap as they existed at the basis commit. Their exact Git blob identities are stored in the machine freeze. `machine/contract.json` and `ROADMAP.md` are basis-only pins because PR #21 intentionally advances their live copies after the PR9 source basis; the freeze therefore verifies their basis-commit objects rather than pretending the new live bytes were part of PR9.",
    )

    validator_path = ROOT / "scripts/validate_lean_observation_foundation.py"
    text = validator_path.read_text(encoding="utf-8")
    text = text.replace(
        "import hashlib\nimport importlib.util\nimport json\nimport os\nimport re\n",
        "import hashlib\nimport importlib.util\nimport json\nimport os\nimport re\nimport subprocess\n",
        1,
    )
    text = text.replace(
        'OBSERVATION_VALIDATOR = ROOT / "scripts/validate_observation_specs.py"\n',
        'OBSERVATION_VALIDATOR = ROOT / "scripts/validate_observation_specs.py"\nWORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"\nBASIS_COMMIT = "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093"\n',
        1,
    )
    source_dict = "EXPECTED_SOURCE_BLOBS = {\n" + "".join(
        f'    {path!r}: {sha!r},\n' for path, sha in SOURCE_BLOBS
    ) + "}\nBASIS_ONLY_MOVING_PATHS = {\"machine/contract.json\", \"ROADMAP.md\"}\n"
    text, count = re.subn(
        r"EXPECTED_SOURCE_BLOBS = \{.*?\}\n\nEXPECTED_THEOREMS =",
        source_dict + "\nEXPECTED_THEOREMS =",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("validator EXPECTED_SOURCE_BLOBS block not found")
    text = text.replace('"schema_version": "1.0.0",', '"schema_version": "1.0.1",', 1)
    text = text.replace(
        '"basis_commit": "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093",',
        '"basis_commit": BASIS_COMMIT,',
        1,
    )
    text = text.replace(
        '"workflow": ".github/workflows/finite-adversarial.yml",',
        '"workflow": ".github/workflows/vopson-corpus.yml",',
        1,
    )

    blob_anchor = '''def git_blob_sha(path: Path) -> str:\n    data = path.read_bytes()\n    header = f"blob {len(data)}\\0".encode("ascii")\n    return hashlib.sha1(header + data).hexdigest()\n'''
    blob_extra = blob_anchor + '''\n\ndef basis_git_blob_sha(relpath: str) -> str | None:\n    result = subprocess.run(\n        ["git", "rev-parse", f"{BASIS_COMMIT}:{relpath}"],\n        cwd=ROOT,\n        text=True,\n        capture_output=True,\n        check=False,\n    )\n    if result.returncode != 0:\n        return None\n    value = result.stdout.strip()\n    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None\n\n\ndef basis_source_object_errors(*, require_objects: bool) -> list[str]:\n    errors: list[str] = []\n    resolved: dict[str, str] = {}\n    for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():\n        actual = basis_git_blob_sha(relpath)\n        if actual is None:\n            if require_objects:\n                errors.append(f"basis commit object unavailable: {BASIS_COMMIT}:{relpath}")\n            continue\n        resolved[relpath] = actual\n        if actual != expected_sha:\n            errors.append(f"basis commit Git blob mismatch: {relpath}")\n    if require_objects and len(resolved) != len(EXPECTED_SOURCE_BLOBS):\n        errors.append("complete PR9 basis dependency closure was not resolved from Git objects")\n    return errors\n\n\ndef workflow_contract_errors(text: str) -> list[str]:\n    errors: list[str] = []\n    twice = (\n        '      - "theory/LEAN_OBSERVATION_FOUNDATION.md"',\n        '      - "UFTID/**"',\n        '      - "**/*.lean"',\n        '      - "lean-toolchain"',\n        '      - "lakefile.toml"',\n        '      - "lake-manifest.json"',\n    )\n    for anchor in twice:\n        if text.count(anchor) != 2:\n            errors.append(f"registered Lean-freeze workflow path trigger drift: {anchor.strip()}")\n    step = '''      - name: Validate Lean observation source freeze\n        env:\n          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"\n        run: python scripts/validate_lean_observation_foundation.py\n'''\n    if text.count(step) != 1:\n        errors.append("registered Lean-freeze workflow direct validator step drift")\n    if text.count("          fetch-depth: 2") != 1:\n        errors.append("registered Lean-freeze workflow basis-history depth drift")\n    return errors\n'''
    if blob_anchor not in text:
        raise RuntimeError("validator git_blob_sha anchor not found")
    text = text.replace(blob_anchor, blob_extra, 1)

    old_paths = '''    if check_paths:\n        for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():\n            path = ROOT / relpath\n            if not path.is_file():\n                errors.append(f"missing frozen source authority: {relpath}")\n            elif git_blob_sha(path) != expected_sha:\n                errors.append(f"frozen source Git blob drift: {relpath}")\n        obs = load_module("pr21_observation_base_validator", OBSERVATION_VALIDATOR).validate()\n'''
    new_paths = '''    if check_paths:\n        for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():\n            path = ROOT / relpath\n            if not path.is_file():\n                errors.append(f"missing frozen source authority: {relpath}")\n            elif relpath not in BASIS_ONLY_MOVING_PATHS and git_blob_sha(path) != expected_sha:\n                errors.append(f"frozen current source Git blob drift: {relpath}")\n        require_basis_objects = os.environ.get("UFT_REQUIRE_BASIS_COMMIT_OBJECT") == "1"\n        errors.extend(basis_source_object_errors(require_objects=require_basis_objects))\n        obs = load_module("pr21_observation_base_validator", OBSERVATION_VALIDATOR).validate()\n'''
    if old_paths not in text:
        raise RuntimeError("validator check_paths source loop anchor not found")
    text = text.replace(old_paths, new_paths, 1)

    old_validate = '''def validate():\n    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI]\n    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]\n    if missing:\n        return {"status": "error", "errors": [f"missing Lean observation freeze authority: {x}" for x in missing], "batch_id": None, "theorem_count": 0, "deferred_count": 0, "module_count": 0}\n    return validate_documents(\n'''
    new_validate = '''def validate():\n    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI, WORKFLOW]\n    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]\n    if missing:\n        return {"status": "error", "errors": [f"missing Lean observation freeze authority: {x}" for x in missing], "batch_id": None, "theorem_count": 0, "deferred_count": 0, "module_count": 0}\n    result = validate_documents(\n'''
    if old_validate not in text:
        raise RuntimeError("validator validate() anchor not found")
    text = text.replace(old_validate, new_validate, 1)
    old_tail = '''        check_paths=True,\n    )\n\n\ndef main() -> int:\n'''
    new_tail = '''        check_paths=True,\n    )\n    errors = list(result.get("errors", []))\n    errors.extend(workflow_contract_errors(WORKFLOW.read_text(encoding="utf-8")))\n    result["errors"] = errors\n    result["status"] = "error" if errors else "ok"\n    return result\n\n\ndef main() -> int:\n'''
    if old_tail not in text:
        raise RuntimeError("validator validate() tail anchor not found")
    text = text.replace(old_tail, new_tail, 1)
    validator_path.write_text(text, encoding="utf-8")

    test_path = ROOT / "tests/test_lean_observation_foundation.py"
    tests = test_path.read_text(encoding="utf-8")
    marker = '''    def test_first_batch_is_exactly_obs_001_through_004(self):\n'''
    additions = '''    def test_complete_pr9_basis_dependency_closure_is_frozen(self):\n        freeze = documents()["freeze"]\n        expected = [{"path": path, "git_blob_sha": sha} for path, sha in V.EXPECTED_SOURCE_BLOBS.items()]\n        self.assertEqual(freeze["source_authorities"], expected)\n        self.assertEqual(freeze["schema_version"], "1.0.1")\n        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["machine/contract.json"], "2aa342b83a698577c92ac7964ea0d8fcfc102a0b")\n        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["machine/formalization_contract.json"], "1c0827b5f760b08d8d375659667ca0067f722aa8")\n        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["ROADMAP.md"], "7a602769908e2ff83ae49a32539fd1a5a5340ce4")\n\n    def test_registered_freeze_workflow_is_direct_and_human_triggered(self):\n        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")\n        self.assertEqual(V.workflow_contract_errors(workflow), [])\n        authority = documents()["base_contract"]["lean_observation_foundation_authority"]\n        self.assertEqual(authority["workflow"], ".github/workflows/vopson-corpus.yml")\n\n        mutated = workflow.replace('      - "theory/LEAN_OBSERVATION_FOUNDATION.md"\\n', "", 1)\n        self.assertTrue(any("path trigger drift" in e for e in V.workflow_contract_errors(mutated)))\n        mutated = workflow.replace("        run: python scripts/validate_lean_observation_foundation.py\\n", "        run: python -c 'pass'\\n", 1)\n        self.assertTrue(any("direct validator step drift" in e for e in V.workflow_contract_errors(mutated)))\n\n'''
    if marker not in tests:
        raise RuntimeError("test insertion marker missing")
    tests = tests.replace(marker, additions + marker, 1)
    test_path.write_text(tests, encoding="utf-8")

    print(json.dumps({"status": "patched", "basis": BASIS, "source_count": len(SOURCE_BLOBS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
