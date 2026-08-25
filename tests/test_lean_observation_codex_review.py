from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_lean_observation_foundation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lean_observation_codex_review", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load live Lean observation validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module()


class LeanObservationCodexReviewRegressions(unittest.TestCase):
    def test_live_phase_and_verification_surfaces_are_synchronized(self):
        roadmap = json.loads((ROOT / "machine/roadmap_state.json").read_text(encoding="utf-8"))
        self.assertEqual(
            next(x for x in roadmap["sequence"] if x["planned_pr"] == 10)["status"],
            "active-post-tag-lean-implementation-ci-hardening",
        )
        readme = (ROOT / "README4AI.md").read_text(encoding="utf-8")
        self.assertIn("Live post-tag implementation authority", readme)
        self.assertIn("IMPLEMENTED_PENDING_CI", readme)
        self.assertNotIn("Lean/Lake/Mathlib remain unpinned", readme)

    def test_registered_theorem_sources_are_exact_blob_bound(self):
        self.assertEqual(V.lean_source_errors(), [])
        path = ROOT / "UFTID/Observation/Basic.lean"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(original + "\n-- source drift fixture\n", encoding="utf-8")
            errors = V.lean_source_errors()
            self.assertTrue(any("registered theorem source blob drift" in e for e in errors), errors)
        finally:
            path.write_text(original, encoding="utf-8")

    def test_constant_assumption_command_is_rejected(self):
        path = ROOT / "UFTID/Observation/Basic.lean"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(
                original.replace(
                    "namespace UFTID.Observation\n",
                    "namespace UFTID.Observation\n\nconstant codexBogus : False\n",
                    1,
                ),
                encoding="utf-8",
            )
            errors = V.lean_source_errors()
            self.assertTrue(
                any("undeclared assumption command forbidden" in e for e in errors),
                errors,
            )
        finally:
            path.write_text(original, encoding="utf-8")

    def test_axiom_policy_records_classical_choice_dependency(self):
        record = V.expected_verification_record()
        audit = record["axiom_audit"]
        self.assertIn("Classical.choice", audit["allowed_axioms"])
        self.assertEqual(audit["required_axioms_by_theorem"]["UFT-OBS-003"], ["Classical.choice"])
        self.assertEqual(audit["required_axioms_by_theorem"]["UFT-OBS-004"], ["Classical.choice"])

    def test_workflow_routes_frozen_dependency_and_axiom_audit(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        self.assertEqual(workflow.count("validate_lean_observation_foundation_pr21_final_frozen.py"), 2)
        self.assertEqual(workflow.count("verify_lean_observation_axioms.py"), 3)
        self.assertIn("--json-out artifacts/lean-observation-axioms.json", workflow)

    def test_compatibility_export_does_not_reuse_loop_sentinel(self):
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertNotIn("globals()[_name]", source)
        self.assertIn("globals().update(_COMPAT_EXPORTS)", source)


if __name__ == "__main__":
    unittest.main()
