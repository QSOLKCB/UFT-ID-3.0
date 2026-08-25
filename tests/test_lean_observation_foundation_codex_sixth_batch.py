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


V = load_module("lean_observation_freeze_codex6", ROOT / "scripts/validate_lean_observation_foundation.py")
EFP = load_module("efp_schedule_codex6", ROOT / "scripts/validate_empirical_falsification_profile.py")
REL = load_module("relation_schedule_codex6", ROOT / "scripts/validate_relation_core.py")


class CodexSixthBatchRegressions(unittest.TestCase):
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

    def validate_human(self, human: str):
        freeze, source_theorems, source_counterexamples, base_contract, _, roadmap, readme = self.canonical_documents()
        return V.validate_documents(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            human,
            roadmap,
            readme,
            check_paths=False,
        )

    def test_freeze_command_is_exact_and_blocking(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        command = "        run: python scripts/validate_lean_observation_foundation.py"
        for suffix in (" || true", "; exit 0"):
            with self.subTest(suffix=suffix):
                mutated = workflow.replace(command, command + suffix, 1)
                errors = V.workflow_contract_errors(mutated)
                self.assertIn("registered Lean-freeze validator command must be exact and blocking", errors)
        escaped_duplicate = workflow.replace(
            command,
            command + '\n        "\\u0072un": echo skipped',
            1,
        )
        self.assertIn(
            "registered Lean-freeze validator command must be exact and blocking",
            V.workflow_contract_errors(escaped_duplicate),
        )
        for continuation in ("          || true\n", "          ; exit 0\n"):
            with self.subTest(continuation=continuation.strip()):
                mutated = workflow.replace(command + "\n", command + "\n" + continuation, 1)
                self.assertIn(
                    "registered Lean-freeze validator step must match the exact canonical body",
                    V.workflow_contract_errors(mutated),
                )
        escaped_control = workflow.replace(
            command,
            '        "continue-\\u006fn-error": true\n' + command,
            1,
        )
        self.assertIn(
            "registered Lean-freeze validator step must match the exact canonical body",
            V.workflow_contract_errors(escaped_control),
        )

    def test_workflow_path_lists_are_exact_bound(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        final_path = '      - ".github/workflows/**"\n'
        for attack in (
            '      - "!scripts/validate_lean_observation_foundation.py"\n',
            '      - "!.github/workflows/**"\n',
        ):
            with self.subTest(attack=attack.strip()):
                mutated = workflow.replace(final_path, final_path + attack)
                errors = V.workflow_contract_errors(mutated)
                for event in ("pull_request", "push"):
                    self.assertIn(
                        f"registered Lean-freeze workflow {event} path list must match the exact canonical ordered set",
                        errors,
                    )

        duplicate = workflow.replace(
            final_path,
            final_path + '    paths:\n      - "README.md"\n',
            1,
        )
        self.assertIn(
            "registered Lean-freeze workflow pull_request path list must match the exact canonical ordered set",
            V.workflow_contract_errors(duplicate),
        )
        for duplicate_key in (
            '    "p\\u0061ths":\n      - "!scripts/validate_lean_observation_foundation.py"\n',
            '    ? paths\n    : ["!scripts/validate_lean_observation_foundation.py"]\n',
        ):
            with self.subTest(duplicate_key=duplicate_key.splitlines()[0]):
                mutated = workflow.replace(final_path, final_path + duplicate_key, 1)
                self.assertIn(
                    "registered Lean-freeze workflow pull_request path list must match the exact canonical ordered set",
                    V.workflow_contract_errors(mutated),
                )

    def test_complete_workflow_binding_rejects_inherited_execution_context(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        mutations = (
            workflow.replace("jobs:\n", "env:\n  PYTHONPATH: tests/fixtures/freeze-bypass\n\njobs:\n", 1),
            workflow.replace(
                "  validate-corpus:\n",
                "  validate-corpus:\n    env:\n      PYTHONPATH: tests/fixtures/freeze-bypass\n",
                1,
            ),
            workflow.replace(
                "jobs:\n",
                '"d\\u0065faults": {run: {shell: "bash -n {0}"}}\n\njobs:\n',
                1,
            ),
            workflow.replace(
                "  validate-corpus:\n",
                '  validate-corpus:\n    ? defaults\n    : {run: {shell: "bash -n {0}"}}\n',
                1,
            ),
        )
        for mutated in mutations:
            with self.subTest(mutation=mutated.split("jobs:\n", 1)[0][-80:]):
                self.assertIn(
                    "registered Lean-freeze workflow complete Git blob drift",
                    V.workflow_contract_errors(mutated),
                )

    def test_compatibility_validators_are_exact_blob_bound_before_import(self):
        cases = (
            (
                EFP,
                "pre-release-gate EFP compatibility validator blob drift",
                "frozen PR19 EFP validator blob drift",
            ),
            (
                REL,
                "pre-release-gate relation compatibility validator blob drift",
                "frozen PR11 relation validator blob drift",
            ),
        )
        for module, diagnostic, frozen_diagnostic in cases:
            with self.subTest(module=module.__name__):
                self.assertEqual(module.compatibility_validator_blob_errors(), [])
                self.assertEqual(module.local_git_blob_sha(module.BASE), module.EXPECTED_BASE_VALIDATOR_BLOB)
                self.assertEqual(
                    module.local_git_blob_sha(module.FROZEN_BASE),
                    module.EXPECTED_FROZEN_BASE_VALIDATOR_BLOB,
                )
                source = Path(module.__file__).read_text(encoding="utf-8")
                self.assertLess(
                    source.index("_preload_base_errors = compatibility_validator_blob_errors()"),
                    source.index("_spec = importlib.util.spec_from_file_location"),
                )
                original = module.local_git_blob_sha
                try:
                    module.local_git_blob_sha = lambda path: "0" * 40
                    errors = module.compatibility_validator_blob_errors()
                    self.assertTrue(any(diagnostic in error for error in errors), errors)
                    self.assertTrue(any(frozen_diagnostic in error for error in errors), errors)
                    result = module.validate()
                    self.assertTrue(any(diagnostic in error for error in result["errors"]), result["errors"])
                    self.assertTrue(any(frozen_diagnostic in error for error in result["errors"]), result["errors"])
                finally:
                    module.local_git_blob_sha = original

    def test_displayed_frozen_and_deferred_lists_are_machine_bound(self):
        human = HUMAN.read_text(encoding="utf-8")
        frozen = "```text\nUFT-OBS-001\nUFT-OBS-002\nUFT-OBS-003\nUFT-OBS-004\n```"
        mutated = human.replace(
            frozen,
            "```text\nUFT-OBS-001\nUFT-OBS-002\nUFT-OBS-003\nUFT-OBS-005\n```",
            1,
        )
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human frozen theorem list drift", result["errors"])

        deferred = "Deferred to a later Lean batch:\n\n```text\nUFT-OBS-005\n```"
        mutated = human.replace(
            deferred,
            "Deferred to a later Lean batch:\n\n```text\nUFT-OBS-004\n```",
            1,
        )
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human deferred theorem list drift", result["errors"])

        swapped_labels = human.replace("Frozen in batch 001:", "TEMP LABEL", 1)
        swapped_labels = swapped_labels.replace("Deferred to a later Lean batch:", "Frozen in batch 001:", 1)
        swapped_labels = swapped_labels.replace("TEMP LABEL", "Deferred to a later Lean batch:", 1)
        result = self.validate_human(swapped_labels)
        self.assertIn("Lean observation human batch-selection labels drift", result["errors"])

    def test_displayed_counterexample_edges_are_machine_bound(self):
        human = HUMAN.read_text(encoding="utf-8")
        mutated = human.replace(
            "CX-OBS-001 -> UFT-OBS-003, UFT-OBS-004",
            "CX-OBS-001 -> UFT-OBS-002",
            1,
        )
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human counterexample dependency graph drift", result["errors"])

        relabelled = human.replace(
            "Adversarial companions remain separately typed:",
            "Theorem premises:",
            1,
        )
        result = self.validate_human(relabelled)
        self.assertIn("Lean observation human counterexample dependency graph drift", result["errors"])

        reversed_nonpremise = human.replace(
            "Counterexamples are not theorem premises and executable witnesses are not Lean proofs.",
            "Counterexamples are theorem premises and executable witnesses are Lean proofs.",
            1,
        )
        result = self.validate_human(reversed_nonpremise)
        self.assertIn("Lean observation human counterexample dependency graph drift", result["errors"])

        canonical = "CX-OBS-001 -> UFT-OBS-003, UFT-OBS-004\nCX-OBS-002 -> UFT-OBS-002"
        mutated = human.replace(canonical, canonical + "\nCX-OBS-002 -> UFT-OBS-002", 1)
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human counterexample dependency graph drift", result["errors"])

    def test_displayed_hard_boundaries_are_exact_machine_projection(self):
        human = HUMAN.read_text(encoding="utf-8")
        mutated = human.replace(
            "SOURCE_RELEASE_TAG != LEAN_VERIFIED",
            "SOURCE_RELEASE_TAG = LEAN_VERIFIED",
            1,
        )
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human hard-boundary block drift", result["errors"])

        canonical_open = "This freeze records exact theorem statements, hypotheses, formalization scope, nonclaims, dependency edges, adversarial companions, and the expected future Lean module/declaration map.\n\n```text\n"
        mutated = human.replace(canonical_open, canonical_open.replace("```text", "````text"), 1)
        result = self.validate_human(mutated)
        self.assertIn("Lean observation human hard-boundary code block missing", result["errors"])

        commented = human.replace("```text\nMATHEMATICAL_PROOF", "<!--\n```text\nMATHEMATICAL_PROOF", 1)
        commented = commented.replace(
            "UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED\n```",
            "UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED\n```\n-->",
            1,
        )
        result = self.validate_human(commented)
        self.assertIn("Lean observation human hard-boundary code block missing", result["errors"])

    def test_authority_headings_must_be_exact_and_unique(self):
        human = HUMAN.read_text(encoding="utf-8")
        for heading, diagnostic in (
            ("## Frozen source authority", "Lean observation human hard-boundary preamble missing"),
            ("## Batch selection", "Lean observation human batch selection missing"),
            ("## Dependency graph", "Lean observation human dependency graph missing"),
        ):
            with self.subTest(heading=heading):
                indented = human.replace(heading, "    " + heading, 1)
                result = self.validate_human(indented)
                self.assertIn(diagnostic, result["errors"])

                duplicate = human + "\n" + heading.swapcase() + "\n\n```text\nCONTRADICTION\n```\n"
                result = self.validate_human(duplicate)
                self.assertIn(diagnostic, result["errors"])


if __name__ == "__main__":
    unittest.main()
