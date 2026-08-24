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


E = load_module("epistemic_bridge_experiment", "experiments/epistemic_bridge/run.py")
V = load_module("epistemic_bridge_validator", "scripts/validate_epistemic_bridge.py")
BRIDGE = load_module("epistemic_bridge_bridgecore", "experiments/bridge_core/run.py")


class EpistemicBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = E.run_suite()

    def test_finite_presence_counts(self):
        shapes = self.suite["bounded_checks"]["presence_shapes"]
        self.assertEqual(shapes["raw_presence_vectors"], 64)
        self.assertEqual(shapes["valid_normalized_shapes"], 33)

    def test_activity_without_evidence_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "requires evidence_refs"):
            E.make_state(retrieved_refs=("r",))
        with self.assertRaisesRegex(ValueError, "requires evidence_refs"):
            E.make_state(conflict_refs=("c",))

    def test_empty_scope_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "scope must be nonempty"):
            E.make_state(scope=())

    def test_retrieve_infer_execute_do_not_verify(self):
        base = E.make_state(scope=("s",))
        self.assertFalse(E.verified(E.retrieve(base, "src")))
        self.assertFalse(E.verified(E.infer(base, "inf")))
        self.assertFalse(E.verified(E.execute(base, "exec")))

    def test_verification_requires_evidence_and_explicit_receipt(self):
        base = E.make_state(scope=("s",))
        with self.assertRaisesRegex(ValueError, "requires evidence_refs"):
            E.verify(base, "v")
        retrieved = E.retrieve(base, "src")
        verified = E.verify(retrieved, "v")
        self.assertTrue(E.verified(verified))
        self.assertIn("v", verified["verification_receipts"])

    def test_conflict_is_not_unknown(self):
        state = E.add_conflict(E.make_state(scope=("s",)), "cx")
        self.assertTrue(E.conflict(state))
        self.assertFalse(E.unknown(state))

    def test_verified_conflict_is_representable(self):
        state = E.add_conflict(E.make_state(scope=("s",)), "cx")
        state = E.verify(state, "v")
        self.assertTrue(E.conflict(state))
        self.assertTrue(E.verified(state))

    @staticmethod
    def bridge(scope):
        return BRIDGE.make_bridge(
            bridge_id="epistemic-test-bridge",
            source_type="A", target_type="B", source_version="1", target_version="1",
            source_states=("x",), target_states=("y",), domain=("x",), relation=(("x", "y"),),
            relation_kind="map", preserved_structure=("authority-neutral",), lost_structure=(), scope=scope,
        )

    def test_transport_preserves_authority_and_narrows_scope(self):
        state = E.verify(E.retrieve(E.make_state(scope=("a", "b", "c")), "src"), "v")
        transported = E.transport(state, self.bridge(("b", "c", "d")))
        self.assertEqual(E.authority_vector(transported), E.authority_vector(state))
        self.assertEqual(transported["scope"], frozenset({"b", "c"}))
        self.assertTrue(transported["scope"].issubset(state["scope"]))

    def test_disjoint_transport_scope_fails_closed(self):
        state = E.make_state(scope=("a",))
        with self.assertRaisesRegex(ValueError, "scope intersection"):
            E.transport(state, self.bridge(("b",)))

    def test_repeated_transport_cannot_accumulate_authority(self):
        state = E.retrieve(E.make_state(scope=("a", "b", "c")), "src")
        once = E.transport(state, self.bridge(("b", "c")))
        twice = E.transport(once, self.bridge(("c",)))
        self.assertEqual(E.authority_vector(state), E.authority_vector(twice))
        self.assertEqual(twice["scope"], frozenset({"c"}))

    def test_transport_requires_a_real_bridgecore_bridge(self):
        state = E.make_state(scope=("s",))
        with self.assertRaises((TypeError, ValueError)):
            E.transport(state, ("s",))
        malformed = {"scope": frozenset({"s"})}
        with self.assertRaises(ValueError):
            E.transport(state, malformed)

    def test_counterexamples_are_derived(self):
        fixtures = self.suite["fixtures"]
        self.assertFalse(fixtures["CX-EP-001"]["verified"])
        self.assertFalse(fixtures["CX-EP-002"]["verified"])
        self.assertTrue(fixtures["CX-EP-003"]["executed"])
        self.assertFalse(fixtures["CX-EP-003"]["verified"])
        self.assertTrue(fixtures["CX-EP-004"]["conflict"])
        self.assertFalse(fixtures["CX-EP-004"]["unknown"])
        self.assertTrue(fixtures["CX-EP-005"]["verified"])
        self.assertTrue(fixtures["CX-EP-005"]["conflict"])

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 10)
        self.assertEqual(result["boundary_count"], 10)

    def mutate_json(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            mutate(payload)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def mutate_text(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            mutated = mutate(original)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def assert_error(self, result, fragment: str):
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_machine_theorem_hypotheses_are_exact_bound(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-EP-003")
            record["hypotheses"] = []
        self.assert_error(self.mutate_json("machine/epistemic_bridge_results.json", mutate), "UFT-EP-003 hypotheses drift")

    def test_human_theorem_hypotheses_are_exact_bound(self):
        canonical = '**Canonical hypotheses:** `["E is a valid EpistemicState", "nonempty conflict_refs requires nonempty evidence_refs"]`'
        result = self.mutate_text(
            "theory/EPISTEMIC_BRIDGE.md",
            lambda text: text.replace(canonical, '**Canonical hypotheses:** `[]`', 1),
        )
        self.assert_error(result, "UFT-EP-003 human canonical hypotheses drift")

    def test_duplicate_result_ids_are_rejected(self):
        def mutate(payload):
            payload["records"].append(dict(payload["records"][0]))
        self.assert_error(self.mutate_json("machine/epistemic_bridge_results.json", mutate), "duplicate epistemic result id")

    def test_contract_authority_registry_is_exact_bound(self):
        def mutate(payload):
            payload["authorities"] = {}
        self.assert_error(self.mutate_json("machine/epistemic_bridge_contract.json", mutate), "authority mapping drift")

    def test_result_nonclaims_are_exact_bound(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-EP-001")
            record["nonclaims"] = ["Structural transport proves physical truth."]
        self.assert_error(self.mutate_json("machine/epistemic_bridge_results.json", mutate), "UFT-EP-001 nonclaims drift")

    def test_human_counterexample_statement_is_exact_bound(self):
        canonical = "**Canonical statement:** `A state can contain retrieved evidence while verification_receipts remains empty.`"
        result = self.mutate_text(
            "theory/EPISTEMIC_BRIDGE.md",
            lambda text: text.replace(canonical, "**Canonical statement:** `Retrieval is verification.`", 1),
        )
        self.assert_error(result, "CX-EP-001 human counterexample statement drift")

    def test_human_counterexample_section_cannot_disappear(self):
        result = self.mutate_text(
            "theory/EPISTEMIC_BRIDGE.md",
            lambda text: text.replace("### CX-EP-004 Conflict is not unknown", "### Removed conflict fixture", 1),
        )
        self.assert_error(result, "CX-EP-004 human counterexample section missing or duplicated")

    def test_roadmap_cannot_reactivate_bridgecore(self):
        def mutate(payload):
            payload["active_planned_surface"] = 12
        self.assert_error(self.mutate_json("machine/roadmap_state.json", mutate), "epistemic live roadmap active surface must be PR #14")


if __name__ == "__main__":
    unittest.main()
