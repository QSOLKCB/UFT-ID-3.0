from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SIGNS = load_module(
    "finite_entropy_signs",
    "experiments/counterexamples/finite_entropy_signs/run.py",
)
COARSE = load_module(
    "coarse_graining",
    "experiments/representation/coarse_graining/run.py",
)
POLYGON = load_module(
    "vopson_2026_polygons",
    "experiments/reproduction/vopson_2026_polygons/run.py",
)


class FiniteEntropySignTests(unittest.TestCase):
    def test_two_states_realise_all_three_signs(self):
        result = SIGNS.run()
        signs = {case["sign"] for case in result["cases"]}
        self.assertEqual(signs, {"positive", "zero", "negative"})
        self.assertTrue(all(case["state_count"] == 2 for case in result["cases"]))

    def test_deterministic_merge_decreases_by_one_bit(self):
        result = SIGNS.run()
        case = next(c for c in result["cases"] if c["case_id"] == "two_state_deterministic_merge")
        self.assertTrue(math.isclose(case["delta_H_bits"], -1.0, abs_tol=1e-12, rel_tol=0.0))


class RepresentationTests(unittest.TestCase):
    def test_same_fine_trajectory_has_opposite_observed_signs(self):
        result = COARSE.run()
        self.assertTrue(math.isclose(result["fine_delta_H_bits"], 0.0, abs_tol=1e-12, rel_tol=0.0))
        self.assertGreater(result["partitions"]["A"]["delta_H_bits"], 0.0)
        self.assertLess(result["partitions"]["B"]["delta_H_bits"], 0.0)


class PolygonExtremumTests(unittest.TestCase):
    def test_n6_n2_fixed_n_extremum_is_reversed_from_a_minimum_claim(self):
        result = POLYGON.run(max_N=6, max_n=2)
        case = result["triangle_scale_fixed_N6_n2"]
        self.assertEqual(case["maximum"]["counts"], [3, 3])
        self.assertEqual(case["minimum"]["counts"], [1, 5])
        self.assertTrue(math.isclose(case["maximum"]["H_bits"], 1.0, abs_tol=1e-12, rel_tol=0.0))
        self.assertLess(case["minimum"]["H_bits"], case["maximum"]["H_bits"])

    def test_variable_n_fixed_N_has_one_category_minimum_and_all_distinct_maximum(self):
        result = POLYGON.run(max_N=6, max_n=2)
        case = result["variable_n_N6"]
        self.assertEqual(case["global_minimum"]["n"], 1)
        self.assertEqual(case["global_minimum"]["counts"], [6])
        self.assertEqual(case["global_minimum"]["H_bits"], 0.0)
        self.assertEqual(case["global_maximum"]["n"], 6)
        self.assertEqual(case["global_maximum"]["counts"], [1, 1, 1, 1, 1, 1])
        self.assertTrue(
            math.isclose(
                case["global_maximum"]["H_bits"],
                math.log2(6),
                abs_tol=1e-12,
                rel_tol=0.0,
            )
        )

    def test_balanced_counts_are_exhaustive_maxima_in_small_range(self):
        result = POLYGON.run(max_N=12, max_n=5)
        self.assertGreater(len(result["exhaustive_fixed_n_cases"]), 0)
        for case in result["exhaustive_fixed_n_cases"]:
            counts = case["maximum"]["counts"]
            self.assertLessEqual(max(counts) - min(counts), 1)

    def test_concentrated_counts_are_exhaustive_minima_in_small_range(self):
        result = POLYGON.run(max_N=12, max_n=5)
        for case in result["exhaustive_fixed_n_cases"]:
            counts = case["minimum"]["counts"]
            self.assertEqual(counts[:-1], [1] * (len(counts) - 1))

    def test_large_n2_extremum_does_not_merge_neighbor_under_relative_tolerance(self):
        case = POLYGON.audit_case(100000, 2)
        self.assertEqual(case["maximum"]["counts"], [50000, 50000])
        self.assertEqual(case["minimum"]["counts"], [1, 99999])
        neighbor_h = POLYGON.shannon_from_counts((49999, 50001))
        self.assertLess(neighbor_h, case["maximum"]["H_bits"])


class RecoveryCounterexampleTests(unittest.TestCase):
    def test_admissible_recovery_can_increase_declared_information(self):
        admissible = {"a", "b"}
        recovery = {"c": "b"}
        information = {"a": 0.0, "c": 1.0, "b": 2.0}
        start = "c"
        end = recovery[start]
        self.assertIn(end, admissible)
        self.assertEqual(information[end] - information[start], 1.0)


if __name__ == "__main__":
    unittest.main()
