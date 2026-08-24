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


R = load_module("recovery_specialization_experiment", "experiments/recovery_specializations/run.py")
V = load_module("recovery_specialization_validator", "scripts/validate_recovery_specializations.py")


class RecoverySpecializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = R.run_suite()

    def test_bounded_selector_counts(self):
        self.assertEqual(
            self.suite["bounded_checks"],
            {
                "selector_graphs": {"carrier_count": 3, "total_selector_count": 32, "right_unique_checks": 32},
                "relation_soundness": {
                    "selector_relation_pair_count": 13890,
                    "relation_sound_selector_pairs": 4134,
                    "fixed_point_normal_exact_pairs": 739,
                },
                "rank_normalization": {"rank_decreasing_selector_count": 9, "state_normalization_checks": 23},
                "lexicographic": {"lexicographic_selection_checks": 336},
            },
        )

    def test_deterministic_selector_graph_is_right_unique(self):
        selector = R.make_selector(("a", "b", "c"), {"a": "b", "b": "b", "c": "b"})
        self.assertTrue(R.selector_relation_is_right_unique(selector))

    def test_deterministic_selector_can_be_relation_unsound(self):
        states = ("a", "b", "c")
        selector = R.make_selector(states, {"a": "c", "b": "b", "c": "c"})
        relation = R.make_relation(states, (("a", "b"),))
        self.assertFalse(R.relation_sound(selector, relation))
        with self.assertRaisesRegex(ValueError, "relation-sound"):
            R.normalize_ranked(states, relation, selector, {"a": 1, "b": 0, "c": 0}, "a")

    def test_executable_normalizer_rejects_partial_selector(self):
        states = ("a", "b")
        relation = R.make_relation(states, (("b", "a"),))
        partial_selector = {"a": "a"}
        with self.assertRaisesRegex(ValueError, "selector must be total"):
            R.normalize_ranked(states, relation, partial_selector, {"a": 0}, "a")

    def test_relation_sound_selector_can_loop_without_rank(self):
        states = (0, 1)
        selector = R.make_selector(states, {0: 1, 1: 0})
        relation = R.make_relation(states, ((0, 1), (1, 0)))
        self.assertTrue(R.relation_sound(selector, relation))
        self.assertFalse(R.natural_rank_certificate(selector, {0: 1, 1: 0}))
        self.assertFalse(R.reaches_fixed_point_within(selector, 0, 8)[0])

    def test_rank_certified_selector_normalizes_to_reachable_normal(self):
        states = ("a", "b", "c")
        relation = R.make_relation(states, (("a", "b"), ("a", "c")))
        selector = R.make_selector(states, {"a": "b", "b": "b", "c": "c"})
        rank = {"a": 1, "b": 0, "c": 0}
        endpoint = R.normalize_ranked(states, relation, selector, rank, "a")
        self.assertEqual(endpoint, "b")
        self.assertIn(endpoint, R.reachable("a", relation))
        self.assertTrue(R.normal(endpoint, relation))
        self.assertFalse(R.confluent(states, relation))

    def test_lexicographic_selection_requires_explicit_total_tiebreak(self):
        objectives = {"b": (0,), "c": (0,)}
        self.assertEqual(R.argmin_without_tiebreak(("b", "c"), objectives), {"b", "c"})
        self.assertEqual(R.lexicographic_select(("b", "c"), objectives, ("c", "b")), "c")
        with self.assertRaisesRegex(ValueError, "final tie-break"):
            R.lexicographic_select(("b", "c"), objectives, ("b",))

    def test_lexicographic_selection_rejects_noninteger_and_nan_objectives(self):
        malformed = {"a": (float("nan"),), "b": (0.0,)}
        with self.assertRaisesRegex(ValueError, "finite integers"):
            R.lexicographic_select(("a", "b"), malformed, ("b", "a"))
        with self.assertRaisesRegex(ValueError, "finite integers"):
            R.lexicographic_select(("b", "a"), malformed, ("b", "a"))
        with self.assertRaisesRegex(ValueError, "finite integers"):
            R.lexicographic_select(("a", "b"), {"a": (True,), "b": (0,)}, ("a", "b"))

    def test_counterexamples_are_derived(self):
        fixtures = self.suite["fixtures"]
        self.assertEqual(fixtures["CX-REC-001"]["reachable_normals_from_a"], ["b", "c"])
        self.assertFalse(fixtures["CX-REC-001"]["selector_declared"])
        self.assertFalse(fixtures["CX-REC-002"]["relation_sound"])
        self.assertTrue(fixtures["CX-REC-003"]["relation_sound"])
        self.assertFalse(fixtures["CX-REC-003"]["reaches_fixed_point_within_four_steps"])
        self.assertFalse(fixtures["CX-REC-004"]["unique_without_tiebreak"])
        self.assertEqual(fixtures["CX-REC-005"]["selector_normal_form_from_a"], "b")
        self.assertEqual(fixtures["CX-REC-005"]["base_reachable_normals_from_a"], ["b", "c"])
        self.assertFalse(fixtures["CX-REC-005"]["base_relation_confluent"])

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 10)
        self.assertEqual(result["boundary_count"], 9)

    def _mutate_json(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            mutate(payload)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def _mutate_text(self, relpath: str, transform):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            mutated = transform(original)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_undeclared_contract_authority_field_fails_closed(self):
        result = self._mutate_json(
            "machine/recovery_specialization_contract.json",
            lambda payload: payload.__setitem__("empirically_validated", True),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("recovery contract top-level field set drift", result["errors"])

    def test_undeclared_theorem_field_fails_closed(self):
        def mutate(payload):
            payload["records"][0]["empirically_validated"] = True
        result = self._mutate_json("machine/recovery_specialization_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-REC-001 theorem field set drift", result["errors"])

    def test_human_nonclaim_promotion_is_rejected(self):
        canonical = (
            '**Canonical nonclaims:** `["The returned selector normal form need not be the unique normal form reachable '
            'under the underlying relation when that relation branches."]`'
        )
        result = self._mutate_text(
            "theory/RECOVERY_SPECIALIZATIONS.md",
            lambda text: text.replace(
                canonical,
                '**Canonical nonclaims:** `["The selector normal form proves the base relation has a unique normal form."]`',
                1,
            ),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-REC-004 human canonical nonclaims drift", result["errors"])

    def test_roadmap_cannot_reactivate_information_phase(self):
        result = self._mutate_json(
            "machine/roadmap_state.json",
            lambda payload: payload.__setitem__("active_planned_surface", 15),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("recovery roadmap active surface must be PR #16", result["errors"])


if __name__ == "__main__":
    unittest.main()
