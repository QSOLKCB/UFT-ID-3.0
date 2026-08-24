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


R = load_module("representation_experiment", "experiments/representation_calculus/run.py")
V = load_module("representation_validator", "scripts/validate_representation_calculus.py")


class RepresentationCalculusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = R.run_suite()

    def test_matrix_battery_counts(self):
        self.assertEqual(
            self.suite["bounded_checks"]["matrices"],
            {
                "matrix_count": 81,
                "unimodular_transform_count": 40,
                "orthogonal_transform_count": 8,
                "similarity_checks": 3240,
                "congruence_rank_checks": 3240,
                "orthogonal_frobenius_checks": 648,
                "coordinate_covariance_checks": 29160,
            },
        )

    def test_receiver_battery_counts(self):
        self.assertEqual(
            self.suite["bounded_checks"]["receivers"],
            {
                "fin3_function_count": 27,
                "receiver_function_pairs": 729,
                "injective_on_image_receiver_pairs": 441,
                "receiver_equivalence_pair_checks": 3969,
            },
        )

    def test_cx_rep_001_congruent_not_similar(self):
        fixture = self.suite["fixtures"]["CX-REP-001"]
        self.assertTrue(fixture["congruent"])
        self.assertTrue(fixture["trace_differs"])
        self.assertFalse(fixture["similar"])

    def test_cx_rep_002_similar_not_orthogonally_similar(self):
        fixture = self.suite["fixtures"]["CX-REP-002"]
        self.assertTrue(fixture["similar"])
        self.assertEqual(fixture["frobenius_sq_source"], "5")
        self.assertEqual(fixture["frobenius_sq_target"], "6")
        self.assertFalse(fixture["orthogonally_similar_possible"])

    def test_cx_rep_003_same_charpoly_not_similar(self):
        fixture = self.suite["fixtures"]["CX-REP-003"]
        self.assertTrue(fixture["same_characteristic_polynomial"])
        self.assertEqual(fixture["rank_A_minus_I"], 0)
        self.assertEqual(fixture["rank_B_minus_I"], 1)
        self.assertFalse(fixture["similar"])

    def test_cx_rep_004_noninjective_receiver_merges(self):
        fixture = self.suite["fixtures"]["CX-REP-004"]
        self.assertFalse(fixture["before_equal_x0_x1"])
        self.assertTrue(fixture["after_equal_x0_x1"])
        self.assertFalse(fixture["receiver_injective_on_image"])

    def test_cx_rep_005_coordinate_tuple_requires_chart(self):
        fixture = self.suite["fixtures"]["CX-REP-005"]
        self.assertEqual(fixture["coordinate_tuple"], [1, 0])
        self.assertNotEqual(fixture["standard_basis_vector"], fixture["swapped_basis_vector"])
        self.assertEqual(fixture["same_abstract_vector"], fixture["standard_basis_vector"] == fixture["swapped_basis_vector"])
        self.assertFalse(fixture["same_abstract_vector"])

    def test_similarity_and_congruence_are_distinct_operations(self):
        a = R.matrix((1, 2, 0, 1))
        p = R.matrix((1, 1, 0, 1))
        self.assertNotEqual(R.similarity(a, p), R.congruence(a, p))

    def test_singular_change_of_basis_fails_closed(self):
        a = R.identity()
        singular = R.matrix((1, 0, 0, 0))
        with self.assertRaisesRegex(ValueError, "invertible"):
            R.similarity(a, singular)

    def test_bad_matrix_and_vector_shapes_fail_closed(self):
        with self.assertRaises(ValueError):
            R.matrix((1, 2, 3))
        with self.assertRaises(ValueError):
            R.vector((1, 2, 3))

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 10)
        self.assertEqual(result["boundary_count"], 10)

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

    def test_duplicate_result_id_fails_closed(self):
        result = self._mutate_json(
            "machine/representation_results.json",
            lambda payload: payload["records"].append(dict(payload["records"][0])),
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("duplicate" in e for e in result["errors"]), result["errors"])

    def test_theorem_hypothesis_drift_is_rejected(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-REP-003")
            record["hypotheses"] = ["P exists"]
        result = self._mutate_json("machine/representation_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-REP-003 hypotheses drift", result["errors"])

    def test_nonclaim_promotion_is_rejected(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-REP-001")
            record["nonclaims"] = ["Similarity proves physical identity."]
        result = self._mutate_json("machine/representation_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-REP-001 nonclaims drift", result["errors"])

    def test_human_counterexample_statement_is_bound(self):
        canonical = (
            "**Canonical statement:** `An observation distinguishing x0 and x1 can become indistinguishable "
            "after a receiver map sends both observation values to one output.`"
        )
        result = self._mutate_text(
            "theory/REPRESENTATION_CALCULUS.md",
            lambda text: text.replace(canonical, "**Canonical statement:** `Receiver merging proves state identity.`", 1),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("CX-REP-004 human canonical statement drift", result["errors"])

    def test_roadmap_cannot_reactivate_epistemic_phase(self):
        result = self._mutate_json(
            "machine/roadmap_state.json",
            lambda payload: payload.__setitem__("active_planned_surface", 13),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("representation live roadmap active surface must be PR #15", result["errors"])


if __name__ == "__main__":
    unittest.main()
