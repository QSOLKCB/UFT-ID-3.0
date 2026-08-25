from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module(
    "lean_observation_freeze_codex8",
    ROOT / "scripts/validate_lean_observation_foundation.py",
)


def fake_git_result(
    stdout: bytes,
    *,
    returncode: int = 0,
    stderr: bytes = b"",
):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def workflow_path_covers(relpath: str, registered_paths: tuple[str, ...]) -> bool:
    for entry in registered_paths:
        if not entry.startswith('- "') or not entry.endswith('"'):
            continue
        pattern = entry[3:-1]
        if pattern == relpath:
            return True
        if pattern.endswith("/**") and relpath.startswith(pattern[:-2]):
            return True
    return False


class CodexEighthBatchRegressions(unittest.TestCase):
    def test_authority_loader_rejects_duplicate_and_nonfinite_json(self):
        attacks = (
            (
                '{"status":"LEAN_VERIFIED",'
                '"status":"SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF"}\n',
                "duplicate JSON object key: status",
            ),
            ('{"status":"ok","status":"ok"}\n', "duplicate JSON object key: status"),
            ('{"release_gate":{"status":"done","status":"pending"}}\n', "duplicate JSON object key: status"),
            ('{"\\u0073tatus":"LEAN_VERIFIED","status":"pending"}\n', "duplicate JSON object key: status"),
            ('{"value":NaN}\n', "non-finite JSON number: NaN"),
            ('{"value":Infinity}\n', "non-finite JSON number: Infinity"),
            ('{"value":-Infinity}\n', "non-finite JSON number: -Infinity"),
            ('{"value":1e10000}\n', "non-finite JSON number: 1e10000"),
            ('{"nested":{"value":-1e10000}}\n', "non-finite JSON number: -1e10000"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "authority.json"
            for contents, diagnostic in attacks:
                with self.subTest(contents=contents):
                    path.write_text(contents, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, diagnostic):
                        V.load_json(path)

            path.write_text('{"status":"pending","nested":{"value":1}}\n', encoding="utf-8")
            self.assertEqual(
                V.load_json(path),
                {"status": "pending", "nested": {"value": 1}},
            )

    def test_production_validate_uses_the_strict_authority_loader(self):
        original = V.FREEZE
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                V.FREEZE = Path(temp_dir) / "freeze.json"
                V.FREEZE.write_text(
                    '{"status":"LEAN_VERIFIED",'
                    '"status":"SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF"}\n',
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "duplicate JSON object key: status"):
                    V.validate(require_basis_objects=False)
        finally:
            V.FREEZE = original

    def test_registered_workflow_routes_every_frozen_source_authority(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        exact_additions = (
            "scripts/validate_observation_specs.py",
            "experiments/observation/run.py",
            "experiments/run_pr9.py",
            "theory/OBSERVATION_CALCULUS.md",
        )
        package_routes = (
            ("lean-toolchain", "**/lean-toolchain"),
            ("lakefile.toml", "**/lakefile.toml"),
            ("lake-manifest.json", "**/lake-manifest.json"),
        )
        for event in ("pull_request", "push"):
            registered = V.workflow_event_paths(workflow, event)
            self.assertIsNotNone(registered)
            missing = [
                relpath
                for relpath in V.EXPECTED_SOURCE_BLOBS
                if not workflow_path_covers(relpath, registered)
            ]
            self.assertEqual(missing, [], (event, missing))
            for relpath in exact_additions:
                self.assertEqual(registered.count(f'- "{relpath}"'), 1)
            for root_path, recursive_path in package_routes:
                self.assertEqual(registered.count(f'- "{root_path}"'), 1)
                self.assertEqual(registered.count(f'- "{recursive_path}"'), 1)

        for relpath in exact_additions:
            line = f'      - "{relpath}"\n'
            with self.subTest(event="pull_request", relpath=relpath):
                mutated = workflow.replace(line, "", 1)
                self.assertTrue(
                    any(
                        "pull_request path list must match" in error
                        for error in V.workflow_contract_errors(mutated)
                    )
                )
            with self.subTest(event="push", relpath=relpath):
                offset = workflow.rfind(line)
                self.assertNotEqual(offset, -1)
                mutated = workflow[:offset] + workflow[offset + len(line):]
                self.assertTrue(
                    any(
                        "push path list must match" in error
                        for error in V.workflow_contract_errors(mutated)
                    )
                )

    def test_tracked_inventory_ignores_directory_names_not_lean_sources(self):
        calls = []

        def runner(args, **kwargs):
            calls.append((args, kwargs))
            return fake_git_result(
                b"scratch/__pycache__/Premature.lean\0"
                b"scratch/__pycache__/module.pyc\0"
                b"nested/lean-toolchain\0"
                b"pkg/lakefile.toml\0"
                b"pkg/lake-manifest.json\0"
            )

        paths, errors = V.tracked_pretag_lean_files(runner=runner)
        self.assertEqual(errors, [])
        self.assertEqual(
            paths,
            [
                "nested/lean-toolchain",
                "pkg/lake-manifest.json",
                "pkg/lakefile.toml",
                "scratch/__pycache__/Premature.lean",
            ],
        )
        self.assertEqual(len(calls), 1)
        args, kwargs = calls[0]
        self.assertEqual(args, ["git", "ls-files", "--cached", "-z", "--"])
        self.assertEqual(kwargs["cwd"], V.ROOT)
        self.assertTrue(kwargs["capture_output"])
        self.assertFalse(kwargs["check"])

    def test_tracked_inventory_fails_closed_on_git_or_payload_errors(self):
        cases = (
            (fake_git_result(b"", returncode=1, stderr=b"failure"), "inventory unavailable"),
            (fake_git_result(b"unterminated"), "inventory malformed"),
            (fake_git_result(b"good\0\0"), "inventory malformed"),
            (fake_git_result(b"bad-\xff.lean\0"), "inventory is not UTF-8"),
        )
        for response, diagnostic in cases:
            with self.subTest(diagnostic=diagnostic):
                paths, errors = V.tracked_pretag_lean_files(
                    runner=lambda *args, response=response, **kwargs: response
                )
                self.assertEqual(paths, [])
                self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_full_validator_rejects_hidden_tracked_lean_and_inventory_failure(self):
        original = V.tracked_pretag_lean_files
        cases = (
            (
                (["scratch/__pycache__/Premature.lean"], []),
                "pre-tag Lean source/toolchain forbidden: scratch/__pycache__/Premature.lean",
            ),
            (([], ["tracked pre-tag Lean source inventory unavailable"]), "inventory unavailable"),
        )
        try:
            for response, diagnostic in cases:
                with self.subTest(diagnostic=diagnostic):
                    V.tracked_pretag_lean_files = lambda response=response: response
                    result = V.validate(require_basis_objects=False)
                    self.assertEqual(result["status"], "error")
                    self.assertTrue(
                        any(diagnostic in error for error in result["errors"]),
                        result["errors"],
                    )
        finally:
            V.tracked_pretag_lean_files = original

    def test_pinned_compatibility_validators_remain_unchanged(self):
        self.assertEqual(V.base_validator_blob_errors(), [])
        self.assertEqual(V.frozen_validator_blob_errors(), [])


if __name__ == "__main__":
    unittest.main()
