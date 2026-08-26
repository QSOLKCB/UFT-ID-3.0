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

    def test_checkout_repository_and_noncanonical_inputs_are_rejected(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])

        attacks = (
            workflow.replace(
                "          fetch-depth: 0\n",
                "          fetch-depth: 0\n          repository: owner/other-repo\n",
                1,
            ),
            workflow.replace(
                "          fetch-depth: 0\n",
                '          fetch-depth: 0\n          "repository": owner/other-repo\n',
                1,
            ),
            workflow.replace(
                "        with:\n          persist-credentials: false\n          fetch-depth: 0\n",
                "        with: {persist-credentials: false, fetch-depth: 0, repository: owner/other-repo}\n",
                1,
            ),
            workflow.replace(
                "          fetch-depth: 0\n",
                "          fetch-depth: 0\n          path: validated-subtree\n",
                1,
            ),
        )
        for mutated in attacks:
            with self.subTest(workflow=mutated.split("actions/checkout@", 1)[1].split("\n\n", 1)[0]):
                errors = V.workflow_contract_errors(mutated)
                self.assertTrue(
                    any("may not override repository" in error or "inputs must be exact" in error or "canonical block input" in error for error in errors),
                    errors,
                )

        checkout_pin = "d23441a48e516b6c34aea4fa41551a30e30af803"
        extra_checkout_steps = (
            f'      - "uses": actions/checkout@{checkout_pin}\n        with:\n          repository: owner/other-repo\n\n',
            f'      - uses: "actions/checkout@{checkout_pin}"\n        with:\n          repository: owner/other-repo\n\n',
            f'      -   "uses": actions/checkout@{checkout_pin}\n        with:\n          repository: owner/other-repo\n\n',
            f'      - {{"uses": "actions/checkout@{checkout_pin}", "with": {{"repository": "owner/other-repo"}}}}\n',
            f'      - "uses": "actions\\u002fcheckout@{checkout_pin}"\n        with:\n          repository: owner/other-repo\n\n',
            f'      - "uses": "actions\\x2fcheckout@{checkout_pin}"\n        with:\n          repository: owner/other-repo\n\n',
        )
        for extra_step in extra_checkout_steps:
            with self.subTest(extra_step=extra_step.splitlines()[0]):
                mutated = workflow.replace("      - uses: actions/setup-python@", extra_step + "      - uses: actions/setup-python@", 1)
                errors = V.workflow_contract_errors(mutated)
                self.assertIn("registered Lean-freeze workflow must contain exactly one checkout step", errors)

        anchored = workflow.replace(
            "jobs:\n",
            f"env:\n  CHECKOUT_ACTION: &checkout_action actions/checkout@{checkout_pin}\n\njobs:\n",
            1,
        ).replace(
            "      - uses: actions/setup-python@",
            "      - \"uses\": *checkout_action\n        \"with\": {repository: owner/other-repo}\n\n"
            "      - uses: actions/setup-python@",
            1,
        )
        errors = V.workflow_contract_errors(anchored)
        self.assertIn("registered Lean-freeze workflow may not use YAML aliases or merge keys in executable steps", errors)

        dotted_alias = workflow.replace(
            "      - uses: actions/setup-python@",
            "      - *checkout.step\n\n      - uses: actions/setup-python@",
            1,
        )
        errors = V.workflow_contract_errors(dotted_alias)
        self.assertIn("registered Lean-freeze workflow may not use YAML aliases or merge keys in executable steps", errors)

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

    def test_nested_or_noncanonical_fences_cannot_hide_human_authority_drift(self):
        human = HUMAN.read_text(encoding="utf-8")
        body, errors = V._human_text_block(
            human,
            "## Expected Lean module map",
            "missing",
            "bad block",
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(body)
        canonical = f"```text\n{body}```"
        nested = f"````text\n```text\n{body}```\n  CONTRADICTORY MODULE MAP\n````"
        mutated = human.replace(canonical, nested, 1)
        result = self.validate_surfaces(human=mutated)
        self.assertIn("Lean observation human Lean module map code block missing", result["errors"])

        release = (
            "```text\n"
            "FREEZE PR MERGED\n"
            "  -> EXACT MERGED-MAIN CI + HOSTILE REVIEW\n"
            "  -> IMMUTABLE SOURCE-RELEASE TAG\n"
            "  -> QSOL-CONTEXT TARGET BINDING\n"
            "  -> PIN LEAN / LAKE / MATHLIB\n"
            "  -> LEAN PROOF IMPLEMENTATION\n"
            "```"
        )
        nested_release = release.replace("```text\n", "````text\n```text\n", 1) + "\n  -> CONTRADICTORY EARLY PROOF\n````"
        mutated = human.replace(release, nested_release, 1)
        result = self.validate_surfaces(human=mutated)
        self.assertIn("Lean observation human release boundary code block missing", result["errors"])

    def test_unpinned_toolchain_cannot_be_promoted_in_human_surfaces(self):
        attacks = (
            "Lean 4.19, Lake 5, and Mathlib 2026 are now pinned for this batch.",
            "Lean, Lake, and Mathlib are now pinned for this batch.",
            "Mathlib is now pinned for this batch.",
            "The Lean version is now pinned at 4.19.",
            "Lean/Lake/Mathlib have been selected for this batch.",
            "We have locked the Lean/Lake/Mathlib versions.",
            "Toolchain status: PINNED",
            "**Toolchain status:** `PINNED`",
            "Lean version: 4.19",
            "No Lean proof exists, but Lean 4.19 is now pinned.",
            "The toolchain was unpinned yesterday but is now pinned.",
            "The toolchain is now pinned without a source tag.",
            "No source tag exists and the toolchain is now pinned.",
            "Although stale claims are rejected, the toolchain is now pinned.",
            "Mathlib is now frozen at commit abc123.",
            "Lean is frozen at 4.19.",
            "Toolchain: PINNED",
            "Pinned toolchain: Lean 4.19, Lake 5, Mathlib 2026.",
            "The toolchain status is PINNED.",
            "Toolchain pinning is complete.",
            "Lean version 4.19 is pinned.",
            "Mathlib revision abc123 is pinned.",
            "Before the immutable source tag, the toolchain is pinned.",
            "While the release gate is pending, the toolchain is pinned.",
            "The toolchain is pinned until the source tag exists.",
            "When the release gate is pending, the toolchain is pinned.",
            "After merge but before the source tag, the toolchain is pinned.",
            "The claim that the toolchain is pinned is false; the toolchain is now pinned.",
            "The toolchain is pinned after the immutable source tag; the toolchain is now pinned.",
            "Mathlib commit abc123 is pinned.",
            "The toolchain remains PINNED.",
            "The toolchain status has become PINNED.",
            "Lean 4.19, Lake 5, and Mathlib 2026 are now fully pinned for this batch.",
            "The toolchain has been completely pinned.",
        )
        human = HUMAN.read_text(encoding="utf-8")
        roadmap = V.ROADMAP.read_text(encoding="utf-8")
        readme = V.README4AI.read_text(encoding="utf-8")
        for attack in attacks:
            cases = (
                ("human freeze", {"human": human + f"\n{attack}\n"}),
                ("ROADMAP", {"roadmap": roadmap + f"\n{attack}\n"}),
                ("README4AI", {"readme": readme + f"\n{attack}\n"}),
            )
            for surface, kwargs in cases:
                with self.subTest(surface=surface, attack=attack):
                    result = self.validate_surfaces(**kwargs)
                    self.assertEqual(result["status"], "error")
                    self.assertTrue(any("premature toolchain-pinning promotion" in error for error in result["errors"]), result["errors"])

    def test_toolchain_guard_allows_negative_and_future_policy_prose(self):
        controls = (
            "No Lean/Lake/Mathlib version is selected in this phase.",
            "Lean/Lake/Mathlib remain unpinned.",
            "-> PIN LEAN / LAKE / MATHLIB",
            "The toolchain will be pinned after the immutable source tag exists.",
            "Claims that the toolchain is pinned are rejected.",
            "Future formalization will run under pinned tooling.",
            "After release, the toolchain status: PINNED.",
            "Expected toolchain status: PINNED.",
            "The toolchain is pinned after the immutable source tag.",
            "Lean 4 is selected when target binding completes.",
            "Lean 4 module names are fixed by the source freeze.",
            "Mathlib references are selected examples.",
            "After the immutable source tag, however, the toolchain is pinned.",
            "When target binding completes, however, Lean 4 is selected.",
            "The toolchain is not pinned now, but it is pinned after the source tag.",
            "We rejected the claim that the toolchain is pinned.",
            "The claim that the toolchain is pinned is false.",
            "Under the current plan, the toolchain is pinned after the immutable source tag.",
            "Whether the toolchain is pinned is unknown.",
            "It is unclear whether the toolchain is pinned.",
        )
        for control in controls:
            with self.subTest(control=control):
                self.assertFalse(V.toolchain_promotion(control))


if __name__ == "__main__":
    unittest.main()
