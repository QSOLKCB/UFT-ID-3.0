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

    def test_perfect_tense_theorem_scoped_lean_claims_fail_closed(self):
        attacks = (
            "\nLean has proved UFT-OBS-001 through UFT-OBS-004.\n",
            "\nLean has verified UFT-OBS-001 through UFT-OBS-004.\n",
        )
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            for attack in attacks:
                with self.subTest(field=field, attack=attack.strip()):
                    docs = documents()
                    docs[field] += attack
                    self.assert_error_contains(
                        docs,
                        f"{label} theorem-scoped Lean verification promotion",
                    )

    def test_human_batch_and_basis_metadata_are_exact_bound(self):
        docs = documents()
        docs["human"] = docs["human"].replace(
            "**Batch:** `LEAN-OBS-BATCH-001`",
            "**Batch:** `LEAN-OBS-BATCH-999`",
            1,
        )
        self.assert_error_contains(docs, "human batch identity drift")

        docs = documents()
        docs["human"] = docs["human"].replace(
            f"**Basis commit:** `{V.BASIS_COMMIT}`",
            "**Basis commit:** `0000000000000000000000000000000000000000`",
            1,
        )
        self.assert_error_contains(docs, "human basis commit drift")

    def test_registered_freeze_step_and_job_must_remain_blocking(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])

        step_if = workflow.replace(
            "      - name: Validate Lean observation source freeze\n",
            "      - name: Validate Lean observation source freeze\n        if: false\n",
            1,
        )
        errors = V.workflow_contract_errors(step_if)
        self.assertTrue(any("validator step may not be conditional or nonblocking" in e for e in errors), errors)

        step_continue = workflow.replace(
            "      - name: Validate Lean observation source freeze\n",
            "      - name: Validate Lean observation source freeze\n        continue-on-error: true\n",
            1,
        )
        errors = V.workflow_contract_errors(step_continue)
        self.assertTrue(any("validator step may not be conditional or nonblocking" in e for e in errors), errors)

        job_if = workflow.replace(
            "  validate-corpus:\n",
            "  validate-corpus:\n    if: false\n",
            1,
        )
        errors = V.workflow_contract_errors(job_if)
        self.assertTrue(any("validate-corpus job may not be conditional or nonblocking" in e for e in errors), errors)

        job_continue = workflow.replace(
            "  validate-corpus:\n",
            "  validate-corpus:\n    continue-on-error: true\n",
            1,
        )
        errors = V.workflow_contract_errors(job_continue)
        self.assertTrue(any("validate-corpus job may not be conditional or nonblocking" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
