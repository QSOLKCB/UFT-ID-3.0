from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"


def load_module(name: str, relpath: str):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEAN = load_module(
    "lean_observation_freeze_codex9",
    "scripts/validate_lean_observation_foundation.py",
)
RELATION = load_module("relation_core_codex9", "scripts/validate_relation_core.py")
BRIDGE = load_module("bridge_core_codex9", "scripts/validate_bridge_core.py")
EPISTEMIC = load_module("epistemic_bridge_codex9", "scripts/validate_epistemic_bridge.py")
REPRESENTATION = load_module(
    "representation_codex9", "scripts/validate_representation_calculus.py"
)
INFORMATION = load_module(
    "information_codex9", "scripts/validate_information_comparability.py"
)
RECOVERY = load_module(
    "recovery_codex9", "scripts/validate_recovery_specializations.py"
)
CSP = load_module(
    "csp_codex9", "scripts/validate_continuum_stochastic_prevalence.py"
)
EFP = load_module(
    "efp_codex9", "scripts/validate_empirical_falsification_profile.py"
)
REPRO = load_module("repro_codex9", "scripts/validate_reproducibility.py")


def fake_git_result(
    stdout: object,
    *,
    returncode: int = 0,
    stderr: bytes = b"",
):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def head_tree_record(
    relpath: str,
    object_sha: str,
    *,
    mode: str = "100644",
    object_type: str = "blob",
) -> bytes:
    return f"{mode} {object_type} {object_sha}\t{relpath}\0".encode("utf-8")


class CodexNinthBatchRegressions(unittest.TestCase):
    def test_compiled_lean_modules_are_forbidden_and_routed(self):
        calls = []

        def runner(args, **kwargs):
            calls.append((args, kwargs))
            return fake_git_result(
                b"scratch/Premature.olean\0"
                b"scratch/__pycache__/Interface.ilean\0"
                b"scratch/notes.olean.txt\0"
            )

        paths, errors = LEAN.tracked_pretag_lean_files(runner=runner)
        self.assertEqual(errors, [])
        self.assertEqual(
            paths,
            ["scratch/Premature.olean", "scratch/__pycache__/Interface.ilean"],
        )
        self.assertEqual(calls[0][0], ["git", "ls-files", "--cached", "-z", "--"])

        workflow = WORKFLOW.read_text(encoding="utf-8")
        for suffix in ("olean", "ilean"):
            route = f'- "**/*.{suffix}"'
            line = f"      {route}\n"
            for event in ("pull_request", "push"):
                with self.subTest(event=event, suffix=suffix):
                    registered = LEAN.workflow_event_paths(workflow, event)
                    self.assertIsNotNone(registered)
                    self.assertEqual(registered.count(route), 1)
                    offset = workflow.find(line) if event == "pull_request" else workflow.rfind(line)
                    self.assertNotEqual(offset, -1)
                    mutated = workflow[:offset] + workflow[offset + len(line):]
                    self.assertTrue(
                        any(
                            f"{event} path list must match" in error
                            for error in LEAN.workflow_contract_errors(mutated)
                        )
                    )

    def test_full_validator_rejects_compiled_lean_modules(self):
        old_inventory = LEAN.tracked_pretag_lean_files
        old_authorities = LEAN.tracked_authority_object_errors
        try:
            LEAN.tracked_authority_object_errors = lambda: []
            for relpath in (
                "scratch/Premature.olean",
                "scratch/__pycache__/Interface.ilean",
            ):
                with self.subTest(relpath=relpath):
                    LEAN.tracked_pretag_lean_files = lambda relpath=relpath: ([relpath], [])
                    result = LEAN.validate(require_basis_objects=False)
                    self.assertEqual(result["status"], "error")
                    self.assertIn(
                        f"pre-tag Lean source/toolchain forbidden: {relpath}",
                        result["errors"],
                    )
        finally:
            LEAN.tracked_pretag_lean_files = old_inventory
            LEAN.tracked_authority_object_errors = old_authorities

    def test_tracked_authorities_require_regular_exact_git_objects(self):
        relpath = "machine/observation_theorems.json"
        canonical = (ROOT / relpath).read_bytes()
        expected_sha = LEAN.EXPECTED_SOURCE_BLOBS[relpath]
        self.assertEqual(blob_sha(canonical), expected_sha)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / relpath
            path.parent.mkdir(parents=True)
            path.write_bytes(canonical)

            calls = []

            def regular_runner(args, **kwargs):
                calls.append((args, kwargs))
                return fake_git_result(head_tree_record(relpath, expected_sha))

            errors = LEAN.tracked_authority_object_errors(
                root,
                expected_blobs={relpath: expected_sha},
                expected_modes={relpath: "100644"},
                runner=regular_runner,
            )
            self.assertEqual(errors, [])
            self.assertEqual(
                calls[0][0],
                [
                    "git",
                    "ls-tree",
                    "-r",
                    "-z",
                    "--full-tree",
                    "HEAD",
                    "--",
                    relpath,
                ],
            )

            errors = LEAN.tracked_authority_object_errors(
                root,
                expected_blobs={relpath: expected_sha},
                expected_modes={relpath: "100644"},
                runner=lambda *args, **kwargs: fake_git_result(
                    head_tree_record(relpath, expected_sha, mode="100755")
                ),
            )
            self.assertIn(
                f"frozen authority tracked Git object/mode drift: {relpath}",
                errors,
            )

            path.unlink()
            copy = root / "machine/canonical-copy.json"
            copy.write_bytes(canonical)
            path.symlink_to(copy.name)
            link_sha = blob_sha(copy.name.encode("utf-8"))
            errors = LEAN.tracked_authority_object_errors(
                root,
                expected_blobs={relpath: expected_sha},
                expected_modes={relpath: "100644"},
                runner=lambda *args, **kwargs: fake_git_result(
                    head_tree_record(relpath, link_sha, mode="120000")
                ),
            )
            self.assertIn(
                f"frozen authority tracked Git object/mode drift: {relpath}",
                errors,
            )
            self.assertIn(
                f"frozen authority working path must not be a symlink: {relpath}",
                errors,
            )

    def test_tracked_authority_inventory_fails_closed(self):
        relpath = "machine/observation_theorems.json"
        expected_sha = LEAN.EXPECTED_SOURCE_BLOBS[relpath]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / relpath
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT / relpath).read_bytes())
            cases = (
                (fake_git_result(b"", returncode=1), "inventory unavailable"),
                (fake_git_result("not-bytes"), "inventory malformed"),
                (fake_git_result(head_tree_record(relpath, expected_sha)[:-1]), "inventory malformed"),
                (fake_git_result(head_tree_record(relpath, expected_sha) + b"\0"), "inventory malformed"),
                (fake_git_result(b"100644 blob bad\tpath\0"), "inventory malformed"),
                (fake_git_result(head_tree_record(relpath, expected_sha, object_type="commit")), "inventory malformed"),
                (fake_git_result(b"100644 blob " + expected_sha.encode("ascii") + b"\tbad-\xff\0"), "inventory malformed"),
                (fake_git_result(b""), f"tracked Git object missing: {relpath}"),
            )
            for response, diagnostic in cases:
                with self.subTest(diagnostic=diagnostic):
                    errors = LEAN.tracked_authority_object_errors(
                        root,
                        expected_blobs={relpath: expected_sha},
                        expected_modes={relpath: "100644"},
                        runner=lambda *args, response=response, **kwargs: response,
                    )
                    self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_full_validator_uses_tracked_authority_inventory(self):
        old_authorities = LEAN.tracked_authority_object_errors
        old_inventory = LEAN.tracked_pretag_lean_files
        try:
            LEAN.tracked_authority_object_errors = lambda: [
                "frozen authority tracked Git object/mode drift: machine/observation_theorems.json"
            ]
            LEAN.tracked_pretag_lean_files = lambda: ([], [])
            result = LEAN.validate(require_basis_objects=False)
        finally:
            LEAN.tracked_authority_object_errors = old_authorities
            LEAN.tracked_pretag_lean_files = old_inventory
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("object/mode drift" in error for error in result["errors"]))

    def test_every_live_roadmap_loader_rejects_ambiguous_numbers(self):
        loaders = (
            ("relation", RELATION.load_json),
            ("bridge", BRIDGE._strict_live_roadmap),
            ("epistemic", EPISTEMIC._strict_live_roadmap),
            ("representation", REPRESENTATION._strict_live_roadmap),
            ("information", INFORMATION._strict_live_roadmap),
            ("recovery", RECOVERY._strict_live_roadmap),
            ("csp", CSP._strict_live_roadmap),
            ("efp", EFP.load_json),
            ("lean-freeze", LEAN.load_json),
            ("reproducibility", REPRO.load_json),
        )
        attacks = (
            ('{"active_planned_surface":999,"active_planned_surface":10}\n', "duplicate JSON object key"),
            ('{"nested":{"status":"x","status":"x"}}\n', "duplicate JSON object key"),
            ('{"active_planned_\\u0073urface":999,"active_planned_surface":10}\n', "duplicate JSON object key"),
            ('{"value":NaN}\n', "non-finite JSON number"),
            ('{"value":Infinity}\n', "non-finite JSON number"),
            ('{"value":-Infinity}\n', "non-finite JSON number"),
            ('{"value":1e10000}\n', "non-finite JSON number"),
            ('{"nested":{"value":-1e10000}}\n', "non-finite JSON number"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roadmap.json"
            for name, loader in loaders:
                for contents, diagnostic in attacks:
                    with self.subTest(validator=name, contents=contents):
                        path.write_text(contents, encoding="utf-8")
                        with self.assertRaisesRegex(ValueError, diagnostic):
                            loader(path)

    def test_every_live_roadmap_validator_rejects_reported_duplicate(self):
        canonical = (ROOT / "machine/roadmap_state.json").read_text(encoding="utf-8")
        needle = '  "active_planned_surface": 10,\n'
        self.assertEqual(canonical.count(needle), 1)
        attack = canonical.replace(
            needle,
            '  "active_planned_surface": 999,\n' + needle,
            1,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roadmap_state.json"
            path.write_text(attack, encoding="utf-8")
            targets = (
                ("relation", RELATION, "attribute", "ROADMAP_STATE"),
                ("bridge", BRIDGE, "attribute", "ROADMAP"),
                ("epistemic", EPISTEMIC, "frozen_path", "roadmap"),
                ("representation", REPRESENTATION, "frozen_path", "roadmap"),
                ("information", INFORMATION, "frozen_path", "roadmap"),
                ("recovery", RECOVERY, "attribute", "ROADMAP_STATE"),
                ("csp", CSP, "attribute", "ROADMAP_STATE"),
                ("efp", EFP, "attribute", "ROADMAP_STATE"),
                ("lean-freeze", LEAN, "attribute", "ROADMAP_STATE"),
                ("reproducibility", REPRO, "load_redirect", "roadmap_state.json"),
            )
            for name, module, route_kind, route_name in targets:
                with self.subTest(validator=name):
                    if route_kind == "attribute":
                        original = getattr(module, route_name)
                        setattr(module, route_name, path)
                    elif route_kind == "load_redirect":
                        original = module.load_json

                        def redirected_load(candidate, original=original):
                            if candidate.name == route_name:
                                return original(path)
                            return original(candidate)

                        module.load_json = redirected_load
                    else:
                        original = module._frozen.PATHS[route_name]
                        module._frozen.PATHS[route_name] = path
                    try:
                        result = module.validate()
                    finally:
                        if route_kind == "attribute":
                            setattr(module, route_name, original)
                        elif route_kind == "load_redirect":
                            module.load_json = original
                        else:
                            module._frozen.PATHS[route_name] = original
                    if "status" in result:
                        self.assertEqual(result["status"], "error", (name, result))
                    else:
                        self.assertFalse(result["ok"], (name, result))
                    self.assertTrue(
                        any("duplicate JSON object key" in error for error in result["errors"]),
                        (name, result["errors"]),
                    )

    def test_pinned_lean_compatibility_chain_is_unchanged(self):
        self.assertEqual(LEAN.base_validator_blob_errors(), [])
        self.assertEqual(LEAN.frozen_validator_blob_errors(), [])
        self.assertEqual(LEAN.artifact_verifier_blob_errors(), [])


if __name__ == "__main__":
    unittest.main()
