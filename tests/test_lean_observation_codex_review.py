from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_lean_observation_foundation.py"
AXIOM_AUDITOR = ROOT / "scripts/verify_lean_observation_axioms.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("lean_observation_codex_review", VALIDATOR)
A = load_module("lean_observation_axiom_auditor_review", AXIOM_AUDITOR)


def canonical_audit_fixture() -> tuple[dict[str, object], dict[str, object], dict[str, list[str]]]:
    record = V.expected_verification_record()
    policy = record["axiom_audit"]
    assert isinstance(policy, dict)
    declarations = A.declarations_from_record(record)
    parsed = {full_name: [] for full_name in declarations.values()}
    parsed[declarations["UFT-OBS-003"]] = ["Classical.choice"]
    parsed[declarations["UFT-OBS-004"]] = ["Classical.choice"]
    return record, policy, parsed


class LeanObservationCodexReviewRegressions(unittest.TestCase):
    def test_live_phase_and_verification_surfaces_are_synchronized(self):
        roadmap = json.loads((ROOT / "machine/roadmap_state.json").read_text(encoding="utf-8"))
        self.assertEqual(roadmap["schema_version"], "1.7.0")
        self.assertEqual(roadmap["snapshot_date"], "2026-08-24")
        self.assertEqual(
            next(x for x in roadmap["sequence"] if x["planned_pr"] == 10)["status"],
            "active-lean-verified-awaiting-context-and-archive",
        )
        readme = (ROOT / "README4AI.md").read_text(encoding="utf-8")
        self.assertIn("Live post-tag verification authority", readme)
        self.assertIn("LEAN_VERIFIED", readme)
        self.assertNotIn("IMPLEMENTED_PENDING_CI", readme)
        self.assertNotIn("Lean/Lake/Mathlib remain unpinned", readme)

    def test_verified_record_binds_exact_merged_main_evidence(self):
        record = V.expected_verification_record()
        self.assertEqual(record["schema_version"], "1.3.0")
        self.assertEqual(record["status"], "LEAN_VERIFIED")
        self.assertEqual(record["source_release"]["tag"], "v3.0.0")
        self.assertEqual(
            record["source_release"]["commit"],
            "b7f51590985e60920c8b09fc9238b8aec6cfa3bc",
        )
        self.assertEqual(
            record["formalization_integration"]["merge_commit"],
            "bbcde19827921af4490c232bdc1edc401790d89e",
        )
        self.assertEqual(
            record["formalization_integration"]["merge_tree"],
            "b7ec78695f32a5b1cf78b416a5050627ad4f957d",
        )
        self.assertEqual(
            [item["run_id"] for item in record["merged_main_ci"]],
            [32876623204, 32876623479],
        )
        self.assertEqual(
            record["axiom_audit"]["observed_axioms_by_theorem"]["UFT-OBS-005"],
            ["Classical.choice", "Quot.sound", "propext"],
        )
        self.assertEqual(record["current_deferred_theorem_ids"], [])
        self.assertEqual(record["source_freeze_deferred_theorem_ids"], ["UFT-OBS-005"])

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

    def test_assumption_words_in_comments_are_not_commands(self):
        path = ROOT / "UFTID/Observation/Basic.lean"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(
                original.replace(
                    "namespace UFTID.Observation\n",
                    "namespace UFTID.Observation\n\n/- Documentation may discuss an axiom or constant without declaring one. -/\n",
                    1,
                ),
                encoding="utf-8",
            )
            errors = V.lean_source_errors()
            self.assertTrue(any("registered theorem source blob drift" in e for e in errors), errors)
            self.assertFalse(
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

    def test_axiom_output_parser_handles_empty_and_allowed_axioms(self):
        parsed = A.parse_axiom_output(
            "'UFTID.Observation.a' does not depend on any axioms\n"
            "'UFTID.Observation.b' depends on axioms: [Classical.choice, propext]\n"
        )
        self.assertEqual(parsed["UFTID.Observation.a"], [])
        self.assertEqual(
            parsed["UFTID.Observation.b"],
            ["Classical.choice", "propext"],
        )

    def test_axiom_policy_accepts_canonical_synthetic_report(self):
        record, policy, parsed = canonical_audit_fixture()
        report = A.evaluate_axiom_policy(record, policy, parsed)
        self.assertEqual(report["status"], "ok", report["errors"])

    def test_axiom_policy_rejects_undeclared_axiom(self):
        record, policy, parsed = canonical_audit_fixture()
        declarations = A.declarations_from_record(record)
        parsed[declarations["UFT-OBS-001"]] = ["Codex.bogus"]
        report = A.evaluate_axiom_policy(record, policy, parsed)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("uses undeclared axioms" in e for e in report["errors"]), report)

    def test_axiom_policy_rejects_missing_theorem_output(self):
        record, policy, parsed = canonical_audit_fixture()
        declarations = A.declarations_from_record(record)
        parsed.pop(declarations["UFT-OBS-002"])
        report = A.evaluate_axiom_policy(record, policy, parsed)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("missing #print axioms result for UFT-OBS-002" in e for e in report["errors"]), report)

    def test_axiom_policy_rejects_missing_required_axiom(self):
        record, policy, parsed = canonical_audit_fixture()
        declarations = A.declarations_from_record(record)
        parsed[declarations["UFT-OBS-003"]] = []
        report = A.evaluate_axiom_policy(record, policy, parsed)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("missing recorded required axioms" in e for e in report["errors"]), report)

    def test_workflow_routes_frozen_dependency_and_axiom_audit(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        self.assertEqual(workflow.count("validate_lean_observation_foundation_pr22_merged_frozen.py"), 2)
        self.assertEqual(workflow.count("validate_lean_observation_foundation_pr21_final_frozen.py"), 2)
        self.assertEqual(workflow.count("verify_lean_observation_axioms.py"), 3)
        self.assertIn("--json-out artifacts/lean-observation-axioms.json", workflow)

    def test_compatibility_export_does_not_reuse_loop_sentinel(self):
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertNotIn("globals()[_name]", source)
        self.assertIn("globals().update(_COMPAT_EXPORTS)", source)


if __name__ == "__main__":
    unittest.main()
