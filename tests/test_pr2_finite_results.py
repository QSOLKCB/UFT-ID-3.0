from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
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


INFO = load_module("information_primitives", "experiments/lib/information.py")
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
RECEIPT = load_module("finite_receipt", "experiments/run_pr2.py")


class InformationPrimitiveTests(unittest.TestCase):
    def test_shannon_entropy_validates_probability_vector(self):
        self.assertTrue(math.isclose(INFO.shannon_entropy((0.5, 0.5)), 1.0))
        with self.assertRaises(ValueError):
            INFO.shannon_entropy((-0.1, 1.1))
        with self.assertRaises(ValueError):
            INFO.shannon_entropy((0.4, 0.4))
        with self.assertRaises(ValueError):
            INFO.shannon_entropy((float("nan"), 1.0))
        with self.assertRaises(ValueError):
            INFO.shannon_entropy(())

    def test_row_stochastic_validation_is_fail_closed(self):
        with self.assertRaises(ValueError):
            INFO.apply_row_stochastic((0.5, 0.5), ((1.0, 0.0),))
        with self.assertRaises(ValueError):
            INFO.apply_row_stochastic((0.5, 0.5), ((1.0, 0.0), (-0.1, 1.1)))
        with self.assertRaises(ValueError):
            INFO.apply_row_stochastic((0.5, 0.5), ((0.8, 0.1), (0.0, 1.0)))

    def test_partition_validation_rejects_missing_duplicate_and_out_of_range_states(self):
        distribution = (0.25, 0.25, 0.25, 0.25)
        with self.assertRaises(ValueError):
            INFO.coarse_grain(distribution, ((0, 1), (2,)))
        with self.assertRaises(ValueError):
            INFO.coarse_grain(distribution, ((0, 1), (1, 2, 3)))
        with self.assertRaises(ValueError):
            INFO.coarse_grain(distribution, ((0, 1), (2, 4)))
        with self.assertRaises(ValueError):
            INFO.coarse_grain(distribution, ((), (0, 1, 2, 3)))

    def test_require_survives_optimized_python_semantics(self):
        with self.assertRaises(INFO.ScientificInvariantError):
            INFO.require(False, "must fail")


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

    def test_exhaustive_work_limit_fails_before_enumeration(self):
        with self.assertRaises(POLYGON.WorkLimitExceeded):
            POLYGON.audit_case(50, 25, max_compositions=1_000)

    def test_high_part_count_does_not_depend_on_python_recursion_depth(self):
        case = POLYGON.audit_case(1000, 1000, max_compositions=10)
        self.assertEqual(case["ordered_composition_count"], 1)
        self.assertEqual(case["minimum"]["counts"], [1] * 1000)
        self.assertEqual(case["maximum"]["counts"], [1] * 1000)
        self.assertEqual(case["method"], "bounded-exhaustive")

    def test_analytic_extrema_remain_available_above_exhaustive_limit(self):
        case = POLYGON.analytic_extrema(1_000_000, 2)
        self.assertEqual(case["maximum"]["counts"], [500000, 500000])
        self.assertEqual(case["minimum"]["counts"], [1, 999999])
        self.assertEqual(case["method"], "analytic")

    def test_invalid_polygon_parameters_are_rejected(self):
        for args in ((0, 1), (5, 0), (3, 4)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                POLYGON.audit_case(*args)


class ReceiptTests(unittest.TestCase):
    def test_receipt_deterministic_payload_is_stable_within_runtime(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["source_sha256"], second["source_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)

    def test_receipt_hashes_all_executable_package_dependencies(self):
        receipt = RECEIPT.run_suite()
        self.assertEqual(receipt["receipt_version"], "1.1.1")
        self.assertIn("experiments_package_initializer", receipt["source_sha256"])
        self.assertIn("experiments_lib_initializer", receipt["source_sha256"])
        self.assertIn("shared_information_primitives", receipt["source_sha256"])
        self.assertIn("receipt_runner", receipt["source_sha256"])

    def test_hash_only_output_is_valid_json(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "experiments/run_pr2.py"), "--hash-only"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertIn("suite_fingerprint_sha256", payload)


class OptimizedExecutionTests(unittest.TestCase):
    def test_scientific_scripts_run_under_python_O(self):
        commands = [
            [sys.executable, "-O", "experiments/counterexamples/finite_entropy_signs/run.py", "--json"],
            [sys.executable, "-O", "experiments/representation/coarse_graining/run.py", "--json"],
            [
                sys.executable,
                "-O",
                "experiments/reproduction/vopson_2026_polygons/run.py",
                "--max-N",
                "8",
                "--max-n",
                "4",
                "--json",
            ],
        ]
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(completed.stdout))


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
