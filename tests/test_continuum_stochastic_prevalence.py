from __future__ import annotations

from fractions import Fraction
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


C = load_module("csp_experiment", "experiments/continuum_stochastic_prevalence/run.py")
V = load_module("csp_validator", "scripts/validate_continuum_stochastic_prevalence.py")


class ContinuumStochasticPrevalenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = C.run_suite()

    def test_bounded_counts(self):
        self.assertEqual(self.suite["bounded_checks"]["finite_kernels"]["path_mass_evaluations"], 756)
        self.assertEqual(self.suite["bounded_checks"]["finite_atomic_quantifiers"]["finite_atomic_event_checks"], 48)
        self.assertEqual(self.suite["bounded_checks"]["prevalence"]["prevalence_measure_event_checks"], 80)
        self.assertEqual(self.suite["bounded_checks"]["continuum_nonlifting"]["finite_grid_nonlifting_checks"], 31)

    def test_kernel_mass_preservation(self):
        states = (0, 1)
        p = C.make_distribution(states, {0: Fraction(1, 2), 1: Fraction(1, 2)})
        k = C.make_kernel(states, {0: {0: Fraction(1, 2), 1: Fraction(1, 2)}, 1: {0: 1, 1: 0}})
        self.assertEqual(C.evolve_distribution(states, p, k), {0: Fraction(3, 4), 1: Fraction(1, 4)})

    def test_probability_inputs_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "sum exactly to one"):
            C.make_distribution((0, 1), {0: Fraction(3, 4), 1: Fraction(3, 4)})
        with self.assertRaisesRegex(ValueError, "exact integer/Fraction"):
            C.make_distribution((0, 1), {0: 0.5, 1: 0.5})
        with self.assertRaisesRegex(ValueError, "row must sum"):
            C.make_kernel((0, 1), {0: {0: 1, 1: 0}, 1: {0: 1, 1: 1}})

    def test_quantifier_counterexamples(self):
        fixtures = self.suite["fixtures"]
        self.assertEqual(fixtures["CX-CSP-001"]["path_probability_0_to_1"], "0")
        self.assertTrue(fixtures["CX-CSP-002"]["positive_probability"])
        self.assertFalse(fixtures["CX-CSP-002"]["almost_sure"])
        self.assertTrue(fixtures["CX-CSP-003"]["all_listed_finite_horizons_positive"])
        self.assertEqual(fixtures["CX-CSP-003"]["infinite_survival_probability"], "0")

    def test_sampling_prevalence_and_continuum_counterexamples(self):
        fixtures = self.suite["fixtures"]
        self.assertEqual(fixtures["CX-CSP-004"]["trajectory_empirical_head_frequency"], "1")
        self.assertEqual(fixtures["CX-CSP-004"]["declared_single_step_head_probability"], "1/2")
        self.assertEqual(fixtures["CX-CSP-005"]["low_measure_prevalence"], "1/100")
        self.assertEqual(fixtures["CX-CSP-005"]["high_measure_prevalence"], "99/100")
        self.assertTrue(fixtures["CX-CSP-006"]["off_grid_differs"])
        self.assertEqual(fixtures["CX-CSP-006"]["off_grid_polynomial_value"], "3/64")

    def test_event_and_grid_inputs_fail_closed(self):
        p = C.make_distribution((0, 1), {0: 1, 1: 0})
        with self.assertRaisesRegex(ValueError, "event escapes"):
            C.event_probability((0, 1), p, {2})
        with self.assertRaisesRegex(ValueError, "duplicate-free"):
            C.vanishing_polynomial((Fraction(0), Fraction(0)), Fraction(1, 2))
        with self.assertRaisesRegex(ValueError, "exact integer/Fraction"):
            C.vanishing_polynomial((Fraction(0), Fraction(1)), 0.5)

    def test_continuum_grid_accepts_signed_exact_rationals(self):
        grid = (Fraction(-1), Fraction(0), Fraction(1))
        self.assertEqual(C.vanishing_polynomial(grid, Fraction(-1)), 0)
        self.assertEqual(C.vanishing_polynomial(grid, Fraction(-1, 2)), Fraction(3, 8))

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 11)
        self.assertEqual(result["boundary_count"], 11)

    def _mutate_json(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            mutate(payload)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_undeclared_contract_field_fails_closed(self):
        result = self._mutate_json("machine/continuum_stochastic_prevalence_contract.json", lambda p: p.__setitem__("extra_authority", True))
        self.assertEqual(result["status"], "error")
        self.assertIn("CSP contract top-level field set drift", result["errors"])

    def test_undeclared_result_field_fails_closed(self):
        def mutate(payload):
            payload["records"][0]["extra_authority"] = True
        result = self._mutate_json("machine/continuum_stochastic_prevalence_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-CSP-001 theorem field set drift", result["errors"])

    def test_roadmap_cannot_reactivate_recovery(self):
        result = self._mutate_json("machine/roadmap_state.json", lambda p: p.__setitem__("active_planned_surface", 16))
        self.assertEqual(result["status"], "error")
        self.assertIn("CSP roadmap active surface must be PR #17", result["errors"])


if __name__ == "__main__":
    unittest.main()
