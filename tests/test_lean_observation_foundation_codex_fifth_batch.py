from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"
HUMAN = ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("lean_observation_freeze_codex5", ROOT / "scripts/validate_lean_observation_foundation.py")


class CodexFifthBatchRegressions(unittest.TestCase):
    def canonical_documents(self):
        return (
            V.load_json(V.FREEZE),
            V.load_json(V.SOURCE_THEOREMS),
            V.load_json(V.SOURCE_COUNTEREXAMPLES),
            V.load_json(V.BASE_CONTRACT),
            HUMAN.read_text(encoding="utf-8"),
            V.ROADMAP.read_text(encoding="utf-8"),
            V.README4AI.read_text(encoding="utf-8"),
        )

    def validate_surfaces(self, *, human=None, roadmap=None, readme=None):
        freeze, source_theorems, source_counterexamples, base_contract, canonical_human, canonical_roadmap, canonical_readme = self.canonical_documents()
        return V.validate_documents(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            canonical_human if human is None else human,
            canonical_roadmap if roadmap is None else roadmap,
            canonical_readme if readme is None else readme,
            check_paths=False,
        )

    def test_checkout_repository_override_is_rejected(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        mutated = workflow.replace(
            "          fetch-depth: 0\n",
            "          fetch-depth: 0\n          repository: owner/other-repo\n",
            1,
        )
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("may not override repository" in error for error in errors), errors)

    def test_pre_codex4_validator_is_exact_blob_bound(self):
        self.assertEqual(V.base_validator_blob_errors(), [])
        self.assertEqual(V.local_git_blob_sha(V.BASE), V.EXPECTED_BASE_VALIDATOR_BLOB)
        original = V.local_git_blob_sha
        try:
            V.local_git_blob_sha = lambda path: "0" * 40
            errors = V.base_validator_blob_errors()
            self.assertTrue(any("pre-Codex4 PR21 validator blob drift" in error for error in errors), errors)
        finally:
            V.local_git_blob_sha = original

    def test_displayed_lean_module_map_is_machine_bound(self):
        human = HUMAN.read_text(encoding="utf-8")
        old = (
            "UFTID.Observation.Quotient\n"
            "  UFTID/Observation/Quotient.lean\n"
            "  depends on UFTID.Observation.Basic\n"
            "  UFT-OBS-002"
        )
        new = (
            "UFTID.Observation.Quotient\n"
            "  UFTID/Observation/Wrong.lean\n"
            "  depends on UFTID.Observation.Reconstruction\n"
            "  UFT-OBS-004"
        )
        mutated = human.replace(old, new, 1)
        self.assertNotEqual(mutated, human)
        result = self.validate_surfaces(human=mutated)
        self.assertEqual(result["status"], "error")
        self.assertIn("Lean observation human Lean module map drift", result["errors"])

    def test_release_boundary_order_is_exact_bound(self):
        human = HUMAN.read_text(encoding="utf-8")
        old = (
            "FREEZE PR MERGED\n"
            "  -> EXACT MERGED-MAIN CI + HOSTILE REVIEW\n"
            "  -> IMMUTABLE SOURCE-RELEASE TAG\n"
            "  -> QSOL-CONTEXT TARGET BINDING\n"
            "  -> PIN LEAN / LAKE / MATHLIB\n"
            "  -> LEAN PROOF IMPLEMENTATION"
        )
        new = (
            "FREEZE PR MERGED\n"
            "  -> LEAN PROOF IMPLEMENTATION\n"
            "  -> EXACT MERGED-MAIN CI + HOSTILE REVIEW\n"
            "  -> IMMUTABLE SOURCE-RELEASE TAG\n"
            "  -> QSOL-CONTEXT TARGET BINDING\n"
            "  -> PIN LEAN / LAKE / MATHLIB"
        )
        mutated = human.replace(old, new, 1)
        self.assertNotEqual(mutated, human)
        result = self.validate_surfaces(human=mutated)
        self.assertEqual(result["status"], "error")
        self.assertIn("Lean observation human release boundary ordering drift", result["errors"])

    def test_unpinned_toolchain_cannot_be_promoted_in_human_surfaces(self):
        attack = "\nLean 4.19, Lake 5, and Mathlib 2026 are now pinned for this batch.\n"
        human = HUMAN.read_text(encoding="utf-8")
        roadmap = V.ROADMAP.read_text(encoding="utf-8")
        readme = V.README4AI.read_text(encoding="utf-8")
        cases = (
            ("human freeze", {"human": human + attack}),
            ("ROADMAP", {"roadmap": roadmap + attack}),
            ("README4AI", {"readme": readme + attack}),
        )
        for surface, kwargs in cases:
            with self.subTest(surface=surface):
                result = self.validate_surfaces(**kwargs)
                self.assertEqual(result["status"], "error")
                self.assertTrue(any("premature toolchain-pinning promotion" in error for error in result["errors"]), result["errors"])


if __name__ == "__main__":
    unittest.main()
