from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relpath: str):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BRIDGE = load_module("bridge_core_codex2_experiment", "experiments/bridge_core/run.py")
VALIDATOR = load_module("bridge_core_codex2_validator", "scripts/validate_bridge_core.py")
RUNNER = load_module("bridge_core_codex2_runner", "experiments/run_bridge_core.py")


class BridgeCoreSecondCodexRegressions(unittest.TestCase):
    def test_human_theorem_statement_and_hypotheses_survive_blob_rebind(self):
        path = ROOT / "theory/BRIDGE_CORE.md"
        original = path.read_text(encoding="utf-8")
        old_blob = VALIDATOR.EXPECTED_BLOBS["human"]
        mutations = (
            (
                '**Canonical hypotheses:** `["B1 and B2 are composable BridgeCore bridges", "preserved structure uses a shared declared label vocabulary"]`',
                '**Canonical hypotheses:** `["B1 and B2 are composable BridgeCore bridges"]`',
                "UFT-BR-002 human canonical hypotheses drift",
            ),
            (
                '**Canonical statement:** `Under the BridgeCore conservative composition contract, the structure automatically preserved by B2 o B1 is exactly P1 intersect P2.`',
                '**Canonical statement:** `Any compatible bridges preserve every source structure.`',
                "UFT-BR-002 human canonical statement drift",
            ),
        )
        try:
            for old, new, diagnostic in mutations:
                with self.subTest(diagnostic=diagnostic):
                    mutated = original.replace(old, new)
                    self.assertNotEqual(mutated, original)
                    path.write_text(mutated, encoding="utf-8")
                    VALIDATOR.EXPECTED_BLOBS["human"] = VALIDATOR.git_blob_sha(mutated.encode("utf-8"))
                    result = VALIDATOR.validate()
                    self.assertEqual(result["status"], "error")
                    self.assertIn(diagnostic, result["errors"])
                    path.write_text(original, encoding="utf-8")
        finally:
            path.write_text(original, encoding="utf-8")
            VALIDATOR.EXPECTED_BLOBS["human"] = old_blob

    def test_result_nonclaims_are_exact_after_blob_rebind(self):
        path = ROOT / "machine/bridge_core_results.json"
        original = path.read_text(encoding="utf-8")
        old_blob = VALIDATOR.EXPECTED_BLOBS["results"]
        try:
            payload = json.loads(original)
            record = next(x for x in payload["records"] if x["id"] == "UFT-BR-004")
            record["nonclaims"] = [
                "Identity composition confirms that BridgeCore models real physical information transfer."
            ]
            mutated = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            path.write_text(mutated, encoding="utf-8")
            VALIDATOR.EXPECTED_BLOBS["results"] = VALIDATOR.git_blob_sha(mutated.encode("utf-8"))
            result = VALIDATOR.validate()
            self.assertEqual(result["status"], "error")
            self.assertIn("UFT-BR-004 nonclaims drift", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")
            VALIDATOR.EXPECTED_BLOBS["results"] = old_blob

    def test_receipt_version_is_derived_from_both_central_registries(self):
        path = ROOT / "machine/contract.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["bridge_core_authority"]["receipt_version"] = "9.9.9"
            payload["experiment_library"]["bridge_core_receipt_version"] = "9.9.9"
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            self.assertEqual(RUNNER.registered_receipt_version(), "9.9.9")
            self.assertEqual(RUNNER.run_suite()["schema_version"], "9.9.9")

            payload["experiment_library"]["bridge_core_receipt_version"] = "9.9.8"
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "registry disagreement"):
                RUNNER.registered_receipt_version()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_workflow_triggers_on_all_script_dependencies(self):
        workflow = (ROOT / ".github/workflows/finite-adversarial.yml").read_text(encoding="utf-8")
        self.assertGreaterEqual(workflow.count('- "scripts/**"'), 2)
        for dependency in (
            "scripts/validate_relation_core_frozen_pr11.py",
            "scripts/validate_graph_realization_pr11_frozen.py",
            "scripts/validate_bridge_core_precodex2_frozen.py",
        ):
            self.assertTrue((ROOT / dependency).is_file(), dependency)

    def test_associativity_battery_calls_production_compose_for_relation_bridges(self):
        original = BRIDGE.compose
        try:
            def broken(first, second, *, bridge_id="composite"):
                if first.get("relation_kind") == "relation" or second.get("relation_kind") == "relation":
                    raise RuntimeError("production-relation-compose-sentinel")
                return original(first, second, bridge_id=bridge_id)

            BRIDGE.compose = broken
            with self.assertRaisesRegex(RuntimeError, "production-relation-compose-sentinel"):
                BRIDGE.associativity_exhaustive_check()
        finally:
            BRIDGE.compose = original

    def test_empty_carriers_and_empty_identity_are_valid(self):
        bridge = BRIDGE.make_bridge(
            bridge_id="empty", source_type="E0", target_type="E1",
            source_version="1", target_version="1", source_states=(), target_states=(),
            domain=(), relation=(), relation_kind="relation",
            preserved_structure=(), lost_structure=(), scope=("s",),
        )
        identity = BRIDGE.identity_bridge((), type_name="E0", version="1", scope=("s",), structure=())
        self.assertEqual(bridge["domain"], frozenset())
        self.assertEqual(bridge["relation"], frozenset())
        self.assertEqual(identity["relation"], frozenset())

    def test_mismatched_finite_intermediate_carriers_are_rejected(self):
        first = BRIDGE.make_bridge(
            bridge_id="first", source_type="A", target_type="B", source_version="1", target_version="1",
            source_states=("a",), target_states=("b0", "b1"), domain=("a",),
            relation=(("a", "b0"),), relation_kind="map",
            preserved_structure=(), lost_structure=(), scope=("s",),
        )
        second = BRIDGE.make_bridge(
            bridge_id="second", source_type="B", target_type="C", source_version="1", target_version="1",
            source_states=("b0",), target_states=("c",), domain=("b0",),
            relation=(("b0", "c"),), relation_kind="map",
            preserved_structure=(), lost_structure=(), scope=("s",),
        )
        self.assertEqual(BRIDGE.composability_errors(first, second), ("intermediate-carrier-mismatch",))
        with self.assertRaisesRegex(ValueError, "intermediate-carrier-mismatch"):
            BRIDGE.compose(first, second)

    def test_cx_br_001_loss_difference_is_derived_from_fixture(self):
        original_make_bridge = BRIDGE._frozen.make_bridge
        try:
            def altered_make_bridge(**kwargs):
                if kwargs.get("bridge_id") == "endpoint-collapse":
                    kwargs = dict(kwargs)
                    kwargs["lost_structure"] = ()
                return original_make_bridge(**kwargs)

            BRIDGE._frozen.make_bridge = altered_make_bridge
            with self.assertRaisesRegex(RuntimeError, "loss-set distinction disappeared"):
                BRIDGE.fixtures()
        finally:
            BRIDGE._frozen.make_bridge = original_make_bridge


if __name__ == "__main__":
    unittest.main()
