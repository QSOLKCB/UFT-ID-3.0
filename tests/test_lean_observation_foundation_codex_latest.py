from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module(
    "lean_observation_freeze_validator_codex_latest",
    ROOT / "scripts/validate_lean_observation_foundation.py",
)


def documents():
    return {
        "freeze": json.loads((ROOT / "machine/lean_observation_foundation_contract.json").read_text()),
        "theorems": json.loads((ROOT / "machine/observation_theorems.json").read_text()),
        "counterexamples": json.loads((ROOT / "machine/observation_counterexamples.json").read_text()),
        "base_contract": json.loads((ROOT / "machine/contract.json").read_text()),
        "human": (ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md").read_text(),
        "roadmap": (ROOT / "ROADMAP.md").read_text(),
        "readme": (ROOT / "README4AI.md").read_text(),
    }


def validate_docs(docs):
    return V.validate_documents(
        docs["freeze"],
        docs["theorems"],
        docs["counterexamples"],
        docs["base_contract"],
        docs["human"],
        docs["roadmap"],
        docs["readme"],
        check_paths=False,
    )


class LatestCodexLeanFreezeRegressions(unittest.TestCase):
    def assert_error_contains(self, docs, fragment: str):
        result = validate_docs(docs)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_perfect_tense_proven_and_simple_past_theorem_scoped_claims_fail_closed(self):
        attacks = (
            "\nLean has proved UFT-OBS-001 through UFT-OBS-004.\n",
            "\nLean has verified UFT-OBS-001 through UFT-OBS-004.\n",
            "\nLean has proven UFT-OBS-001 through UFT-OBS-004.\n",
            "\nUFT-OBS-001 through UFT-OBS-004 have been proven in Lean.\n",
            "\nLean proved UFT-OBS-001 through UFT-OBS-004.\n",
            "\nLean verified LEAN-OBS-BATCH-001.\n",
        )
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            for attack in attacks:
                with self.subTest(field=field, attack=attack.strip()):
                    docs = documents()
                    docs[field] += attack
                    self.assert_error_contains(docs, f"{label} theorem-scoped Lean verification promotion")

    def test_generic_batch_lean_verification_claims_fail_closed(self):
        attack = "\nThe frozen theorem batch passed Lean verification.\n"
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            with self.subTest(field=field):
                docs = documents()
                docs[field] += attack
                self.assert_error_contains(docs, f"{label} generic batch Lean verification promotion")

    def test_source_tag_completion_claims_fail_closed(self):
        attack = "\nThe immutable source-release tag has now been cut and published.\n"
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            with self.subTest(field=field):
                docs = documents()
                docs[field] += attack
                self.assert_error_contains(docs, f"{label} source-tag completion promotion")

    def test_frozen_nonclaim_reversals_fail_closed(self):
        attacks = (
            "\nUFT-OBS-001 proves that observational equivalence is physical identity.\n",
            "\nUFT-OBS-002 proves that the quotient is the full codomain.\n",
            "\nUFT-OBS-003 proves exact mathematical reconstruction means the original physical state persisted.\n",
            "\nUFT-OBS-004 proves noninjectivity forbids probabilistic reconstruction.\n",
        )
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            for attack in attacks:
                with self.subTest(field=field, attack=attack.strip()):
                    docs = documents()
                    docs[field] += attack
                    self.assert_error_contains(docs, f"{label} frozen theorem nonclaim reversal")

    def test_human_batch_basis_and_proof_reference_metadata_are_exact_bound(self):
        docs = documents()
        docs["human"] = docs["human"].replace("**Batch:** `LEAN-OBS-BATCH-001`", "**Batch:** `LEAN-OBS-BATCH-999`", 1)
        self.assert_error_contains(docs, "human batch identity drift")

        docs = documents()
        docs["human"] = docs["human"].replace(f"**Basis commit:** `{V.BASIS_COMMIT}`", "**Basis commit:** `0000000000000000000000000000000000000000`", 1)
        self.assert_error_contains(docs, "human basis commit drift")

        docs = documents()
        correct = "**Proof reference:** `theory/OBSERVATION_CALCULUS.md#uft-obs-001-observational-equivalence`"
        docs["human"] = docs["human"].replace(correct, correct + "\n**Proof reference:** `theory/WRONG.md#wrong`", 1)
        self.assert_error_contains(docs, "UFT-OBS-001 human Proof reference drift")

    def test_registered_freeze_step_and_job_must_remain_blocking_even_with_quoted_keys(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        mutations = (
            ("      - name: Validate Lean observation source freeze\n", "      - name: Validate Lean observation source freeze\n        if: false\n", "validator step may not be conditional or nonblocking"),
            ("      - name: Validate Lean observation source freeze\n", "      - name: Validate Lean observation source freeze\n        continue-on-error: true\n", "validator step may not be conditional or nonblocking"),
            ("      - name: Validate Lean observation source freeze\n", "      - name: Validate Lean observation source freeze\n        \"continue-on-error\": true\n", "validator step may not be conditional or nonblocking"),
            ("  validate-corpus:\n", "  validate-corpus:\n    if: false\n", "validate-corpus job may not be conditional or nonblocking"),
            ("  validate-corpus:\n", "  validate-corpus:\n    continue-on-error: true\n", "validate-corpus job may not be conditional or nonblocking"),
            ("  validate-corpus:\n", "  validate-corpus:\n    \"if\": false\n", "validate-corpus job may not be conditional or nonblocking"),
        )
        for old, new, fragment in mutations:
            with self.subTest(mutation=new.strip()):
                errors = V.workflow_contract_errors(workflow.replace(old, new, 1))
                self.assertTrue(any(fragment in e for e in errors), errors)

    def test_validator_command_and_env_are_bound_to_named_freeze_step(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        canonical = (
            "      - name: Validate Lean observation source freeze\n"
            "        env:\n"
            "          UFT_REQUIRE_BASIS_COMMIT_OBJECT: \"1\"\n"
            "        run: python scripts/validate_lean_observation_foundation.py\n"
        )
        decoy = (
            "      - name: Validate Lean observation source freeze\n"
            "        run: echo skipped\n\n"
            "      - name: Decoy Lean freeze command\n"
            "        if: false\n"
            "        env:\n"
            "          UFT_REQUIRE_BASIS_COMMIT_OBJECT: \"1\"\n"
            "        run: python scripts/validate_lean_observation_foundation.py\n"
        )
        mutated = workflow.replace(canonical, decoy, 1)
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("named step command/env drift" in e for e in errors), errors)

    def test_pull_request_activity_and_branch_filters_must_remain_unrestricted(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        mutations = (
            ("  pull_request:\n    paths:\n", "  pull_request:\n    types: [closed]\n    paths:\n", "pull_request activity types must remain unrestricted"),
            ("  pull_request:\n    paths:\n", "  pull_request:\n    branches: [staging]\n    paths:\n", "pull_request branch filters must remain unrestricted"),
            ("  pull_request:\n    paths:\n", "  pull_request:\n    branches-ignore: [main]\n    paths:\n", "pull_request branch filters must remain unrestricted"),
        )
        for old, new, fragment in mutations:
            with self.subTest(mutation=new.strip()):
                errors = V.workflow_contract_errors(workflow.replace(old, new, 1))
                self.assertTrue(any(fragment in e for e in errors), errors)

    def test_freeze_step_may_not_override_shell(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        mutated = workflow.replace(
            "      - name: Validate Lean observation source freeze\n",
            "      - name: Validate Lean observation source freeze\n        shell: bash -n {0}\n",
            1,
        )
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("may not override its executing shell" in e for e in errors), errors)

    def test_registered_push_branch_is_exactly_main(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_event_branches(workflow, "push"), ("main",))
        mutated = workflow.replace("    branches: [main]\n", "    branches: [staging]\n", 1)
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("push branch restriction must be exactly main" in e for e in errors), errors)

    def test_frozen_validator_is_exact_blob_bound(self):
        self.assertEqual(V.frozen_validator_blob_errors(), [])
        self.assertEqual(V.git_blob_sha(V.FROZEN), V.EXPECTED_FROZEN_VALIDATOR_BLOB)
        original = V.git_blob_sha
        try:
            V.git_blob_sha = lambda path: "0" * 40
            errors = V.frozen_validator_blob_errors()
            self.assertTrue(any("frozen PR21 validator blob drift" in e for e in errors), errors)
        finally:
            V.git_blob_sha = original

    def test_basis_blob_resolution_requires_readable_blob_object(self):
        original = V.git_object_is_blob
        try:
            V.git_object_is_blob = lambda object_sha: False
            self.assertIsNone(V.basis_git_blob_sha("machine/observation_contract.json"))
        finally:
            V.git_object_is_blob = original

    def test_default_validation_requires_basis_objects(self):
        original = V.basis_git_blob_sha
        try:
            V.basis_git_blob_sha = lambda relpath: None
            result = V.validate()
            self.assertEqual(result["status"], "error")
            self.assertFalse(result["basis_objects_verified"])
            self.assertTrue(any("basis commit blob object unavailable" in e for e in result["errors"]), result["errors"])
            self.assertIn("complete PR9 basis dependency closure was not resolved from readable Git blob objects", result["errors"])

            mutation_only = V.validate(require_basis_objects=False)
            self.assertEqual(mutation_only["status"], "ok", mutation_only["errors"])
            self.assertFalse(mutation_only["basis_objects_verified"])
        finally:
            V.basis_git_blob_sha = original


if __name__ == "__main__":
    unittest.main()
