from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"
HUMAN = ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md"
ROADMAP_STATE = ROOT / "machine/roadmap_state.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("lean_observation_freeze_codex4", ROOT / "scripts/validate_lean_observation_foundation.py")
EFP = load_module("efp_schedule_codex4", ROOT / "scripts/validate_empirical_falsification_profile.py")
REL = load_module("relation_schedule_codex4", ROOT / "scripts/validate_relation_core.py")


class CodexFourthBatchRegressions(unittest.TestCase):
    def test_freeze_step_environment_is_exact(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        mutated = workflow.replace(
            '          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"\n',
            '          UFT_REQUIRE_BASIS_COMMIT_OBJECT: "1"\n          PYTHONPATH: tests/fixtures/freeze-bypass\n',
            1,
        )
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("environment must be exact" in error for error in errors), errors)

    def test_checkout_ref_override_is_rejected(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        mutated = workflow.replace(
            "          fetch-depth: 0\n",
            "          fetch-depth: 0\n          ref: main\n",
            1,
        )
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("may not override ref" in error for error in errors), errors)

    def test_human_dependency_graph_is_machine_bound(self):
        freeze = V.load_json(V.FREEZE)
        source_theorems = V.load_json(V.SOURCE_THEOREMS)
        source_counterexamples = V.load_json(V.SOURCE_COUNTEREXAMPLES)
        base_contract = V.load_json(V.BASE_CONTRACT)
        human = HUMAN.read_text(encoding="utf-8")
        mutated = human.replace(
            "UFT-OBS-001\n  -> UFT-OBS-002\n\nUFT-OBS-003\n  -> UFT-OBS-004",
            "UFT-OBS-001\n  -> UFT-OBS-004\n\nUFT-OBS-003\n  -> UFT-OBS-002",
            1,
        )
        self.assertNotEqual(mutated, human)
        result = V.validate_documents(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            mutated,
            V.ROADMAP.read_text(encoding="utf-8"),
            V.README4AI.read_text(encoding="utf-8"),
            check_paths=False,
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("Lean observation human dependency graph drift", result["errors"])

    def test_machine_schedule_advances_post_tag_without_schema_migration(self):
        roadmap = json.loads(ROADMAP_STATE.read_text(encoding="utf-8"))
        self.assertEqual(roadmap["schema_version"], "1.7.0")
        self.assertEqual(roadmap["snapshot_date"], "2026-08-24")
        by_pr = {item["planned_pr"]: item for item in roadmap["sequence"]}
        self.assertEqual(
            by_pr[10]["status"],
            "active-post-tag-lean-implementation-ci-hardening",
        )
        self.assertEqual(EFP._live_roadmap_errors(), [])
        self.assertEqual(REL._live_roadmap_errors(roadmap), [])
        result = EFP.validate()
        self.assertEqual(result["status"], "ok", result["errors"])


if __name__ == "__main__":
    unittest.main()
