#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAD = "2b4369822314fa1698a2ebea79f24fde6510b2d7"


def replace_once(relpath: str, old: str, new: str) -> None:
    path = ROOT / relpath
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{relpath}: expected exactly one hardening anchor")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    for rel in ("scripts/validate_lean_observation_foundation.py", "tests/test_lean_observation_foundation.py"):
        if subprocess.run(["git", "diff", "--quiet", HEAD, "--", rel]).returncode != 0:
            raise RuntimeError(f"PR21 P1 target drifted from clean head {HEAD}: {rel}")

    validator = "scripts/validate_lean_observation_foundation.py"
    replace_once(
        validator,
        'OBSERVATION_VALIDATOR = ROOT / "scripts/validate_observation_specs.py"\n',
        'OBSERVATION_VALIDATOR = ROOT / "scripts/validate_observation_specs.py"\n\n'
        'EXPECTED_HUMAN_STATUS = "SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF"\n'
        'PRETAG_PACKAGE_FILENAMES = {"lean-toolchain", "lakefile.toml", "lake-manifest.json"}\n',
    )
    replace_once(
        validator,
        'def graph_is_acyclic(graph: dict[str, list[str]]) -> bool:\n',
        '''def pretag_lean_files(root: Path = ROOT) -> list[str]:
    found: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        if path.suffix == ".lean" or path.name in PRETAG_PACKAGE_FILENAMES:
            found.append(rel.as_posix())
    return sorted(found)


def human_promotion_errors(text: str) -> list[str]:
    errors: list[str] = []
    patterns = (
        r"(?is)\\b(?:all|each)\\b.{0,80}\\btheorems?\\b.{0,80}\\b(?:checked|verified|proved)\\b.{0,40}\\bLean\\b",
        r"(?is)\\bLean\\b.{0,40}\\b(?:proof|verification)\\b.{0,40}\\b(?:is|are)\\b.{0,20}\\b(?:complete|verified|proved|checked)\\b",
    )
    for pattern in patterns:
        if re.search(pattern, text):
            errors.append("Lean observation human Lean verification promotion")
            break
    return errors


def graph_is_acyclic(graph: dict[str, list[str]]) -> bool:
''',
    )
    replace_once(
        validator,
        '    for theorem_id, expected in EXPECTED_THEOREMS.items():\n        heading = f"## {theorem_id} {expected[\'name\']}"\n',
        '''    if strip_code(metadata(human, "Status")) != EXPECTED_HUMAN_STATUS:
        errors.append("Lean observation human freeze status drift")
    if strip_code(metadata(human, "Claim class")) != "DEFINITION":
        errors.append("Lean observation human claim class drift")
    errors.extend(human_promotion_errors(human))

    for theorem_id, expected in EXPECTED_THEOREMS.items():
        heading = f"## {theorem_id} {expected['name']}"
''',
    )
    replace_once(
        validator,
        '        obs = load_module("pr21_observation_base_validator", OBSERVATION_VALIDATOR).validate()\n        if obs.get("status") != "ok":\n            errors.append("PR9 observation base authority validation failed")\n',
        '''        obs = load_module("pr21_observation_base_validator", OBSERVATION_VALIDATOR).validate()
        if obs.get("status") != "ok":
            errors.append("PR9 observation base authority validation failed")
        release_gate = freeze.get("release_gate")
        if isinstance(release_gate, dict) and release_gate.get("status") == "PENDING_POST_MERGE" and release_gate.get("source_tag") is None:
            for relpath in pretag_lean_files(ROOT):
                errors.append(f"pre-tag Lean source/toolchain forbidden: {relpath}")
''',
    )

    tests = "tests/test_lean_observation_foundation.py"
    replace_once(
        tests,
        'import unittest\nfrom pathlib import Path\n',
        'import unittest\nfrom pathlib import Path\n',
    )
    replace_once(
        tests,
        '    def test_roadmap_must_leave_source_tag_pending(self):\n',
        '''    def test_human_status_and_verification_promotion_fail_closed(self):
        docs = documents()
        docs["human"] = docs["human"].replace(
            "**Status:** `SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF`",
            "**Status:** `LEAN_VERIFIED`",
            1,
        )
        self.assert_error_contains(docs, "human freeze status drift")

        docs = documents()
        docs["human"] += "\\nAll frozen theorems have checked Lean proofs.\\n"
        self.assert_error_contains(docs, "human Lean verification promotion")

    def test_pretag_lean_source_and_toolchain_files_are_rejected(self):
        candidates = (
            ROOT / "UFTID/Observation/Basic.lean",
            ROOT / "lean-toolchain",
            ROOT / "lakefile.toml",
            ROOT / "lake-manifest.json",
        )
        created_dirs: list[Path] = []
        try:
            for path in candidates:
                with self.subTest(path=str(path.relative_to(ROOT))):
                    if path.exists():
                        self.fail(f"canonical pre-tag tree unexpectedly already contains {path}")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if path.parent != ROOT:
                        created_dirs.append(path.parent)
                    path.write_text("pre-tag forbidden fixture\\n", encoding="utf-8")
                    result = V.validate()
                    self.assertEqual(result["status"], "error")
                    self.assertIn(
                        f"pre-tag Lean source/toolchain forbidden: {path.relative_to(ROOT).as_posix()}",
                        result["errors"],
                    )
                    path.unlink()
        finally:
            for path in candidates:
                if path.exists():
                    path.unlink()
            for directory in sorted(set(created_dirs), key=lambda p: len(p.parts), reverse=True):
                try:
                    directory.rmdir()
                    parent = directory.parent
                    if parent != ROOT:
                        parent.rmdir()
                except OSError:
                    pass

    def test_pretag_scanner_ignores_non_lean_files(self):
        self.assertNotIn("theory/LEAN_OBSERVATION_FOUNDATION.md", V.pretag_lean_files(ROOT))

    def test_roadmap_must_leave_source_tag_pending(self):
''',
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
