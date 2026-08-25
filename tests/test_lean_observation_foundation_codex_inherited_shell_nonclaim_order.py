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
    "lean_observation_freeze_validator_codex_inherited_shell_nonclaim_order",
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


class LatestInheritedShellAndNonclaimOrderRegressions(unittest.TestCase):
    def test_inherited_defaults_run_shell_is_rejected_at_workflow_and_job_scope(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])

        workflow_level = workflow.replace(
            "jobs:\n",
            "defaults:\n  run:\n    shell: bash -n {0}\n\njobs:\n",
            1,
        )
        errors = V.workflow_contract_errors(workflow_level)
        self.assertTrue(any("workflow scope" in error and "defaults.run.shell" in error for error in errors), errors)

        job_level = workflow.replace(
            "  validate-corpus:\n",
            "  validate-corpus:\n    defaults:\n      run:\n        shell: bash -n {0}\n",
            1,
        )
        errors = V.workflow_contract_errors(job_level)
        self.assertTrue(any("validate-corpus" in error and "defaults.run.shell" in error for error in errors), errors)

    def test_frozen_nonclaim_reversals_fail_closed_in_both_clause_orders(self):
        reverse_order_attacks = (
            "Observational equivalence is physical identity, as UFT-OBS-001 proves.",
            "The quotient is the full codomain, as UFT-OBS-002 proves.",
            "Exact mathematical reconstruction establishes that the original physical state persisted, as UFT-OBS-003 proves.",
            "Noninjectivity forbids partial reconstruction, as UFT-OBS-004 proves.",
        )
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            for attack in reverse_order_attacks:
                with self.subTest(field=field, attack=attack):
                    docs = documents()
                    docs[field] += f"\n{attack}\n"
                    result = validate_docs(docs)
                    self.assertEqual(result["status"], "error")
                    self.assertTrue(
                        any(f"{label} frozen theorem nonclaim reversal" in error for error in result["errors"]),
                        result["errors"],
                    )


if __name__ == "__main__":
    unittest.main()
