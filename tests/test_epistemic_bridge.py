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

    def test_transport_preserves_authority_and_narrows_scope(self):
        state = E.verify(E.retrieve(E.make_state(scope=("a", "b", "c")), "src"), "v")
        transported = E.transport(state, ("b", "c", "d"))
        self.assertEqual(E.authority_vector(transported), E.authority_vector(state))
        self.assertEqual(transported["scope"], frozenset({"b", "c"}))
        self.assertTrue(transported["scope"].issubset(state["scope"]))

    def test_disjoint_transport_scope_fails_closed(self):
        state = E.make_state(scope=("a",))
        with self.assertRaisesRegex(ValueError, "scope intersection"):
            E.transport(state, ("b",))

    def test_repeated_transport_cannot_accumulate_authority(self):
        state = E.retrieve(E.make_state(scope=("a", "b", "c")), "src")
        once = E.transport(state, ("b", "c"))
        twice = E.transport(once, ("c",))
        self.assertEqual(E.authority_vector(state), E.authority_vector(twice))
        self.assertEqual(twice["scope"], frozenset({"c"}))

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

    def test_machine_theorem_hypotheses_are_exact_bound(self):
        path = ROOT / "machine/epistemic_bridge_results.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            record = next(r for r in payload["records"] if r["id"] == "UFT-EP-003")
            record["hypotheses"] = []
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = V.validate()
            self.assertEqual(result["status"], "error")
            self.assertIn("UFT-EP-003 hypotheses drift", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")

    def test_human_theorem_hypotheses_are_exact_bound(self):
        path = ROOT / "theory/EPISTEMIC_BRIDGE.md"
        original = path.read_text(encoding="utf-8")
        canonical = '**Canonical hypotheses:** `["E is a valid EpistemicState", "nonempty conflict_refs requires nonempty evidence_refs"]`'
        try:
            mutated = original.replace(canonical, '**Canonical hypotheses:** `[]`', 1)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            result = V.validate()
            self.assertEqual(result["status"], "error")
            self.assertIn("UFT-EP-003 human canonical hypotheses drift", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")

    def test_roadmap_cannot_reactivate_bridgecore(self):
        path = ROOT / "machine/roadmap_state.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["active_planned_surface"] = 12
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = V.validate()
            self.assertEqual(result["status"], "error")
            self.assertIn("epistemic roadmap active surface must be PR #13", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
