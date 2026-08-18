from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/reproduction/vopson_2019_mei/run.py"
RESULT_PATH = ROOT / "research/vopson/reproduction/2019-mei/result.json"
GRAPH_PATH = ROOT / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"


def load_module():
    spec = importlib.util.spec_from_file_location("vopson_2019_mei", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Vopson 2019 MEI reproduction module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEI = load_module()


class Vopson2019MEIArithmeticTests(unittest.TestCase):
    def test_300K_bit_mass_reproduces_source_value(self):
        observed = MEI.conditional_bit_mass(300.0)
        self.assertAlmostEqual(observed / 3.19e-38, 1.0, delta=0.01)
        self.assertAlmostEqual(observed, 3.1943948174115975e-38, delta=1e-50)

    def test_2_73K_bit_mass_reproduces_source_value(self):
        observed = MEI.conditional_bit_mass(2.73)
        self.assertAlmostEqual(observed / 2.91e-40, 1.0, delta=0.01)

    def test_decimal_1TB_prediction_reproduced(self):
        observed = MEI.storage_mass(8_000_000_000_000, 300.0)
        self.assertAlmostEqual(observed, 2.5555158539292776e-25, delta=1e-37)
        self.assertLess(abs(observed - 2.5e-25) / 2.5e-25, 0.03)

    def test_temperature_dependence_is_linear(self):
        m100 = MEI.conditional_bit_mass(100.0)
        m200 = MEI.conditional_bit_mass(200.0)
        self.assertAlmostEqual(m200, 2.0 * m100, delta=1e-50)

    def test_zero_temperature_formula_limit(self):
        self.assertEqual(MEI.conditional_bit_mass(0.0), 0.0)

    def test_rejects_invalid_temperature(self):
        for value in (-1.0, math.inf, math.nan):
            with self.assertRaises(ValueError):
                MEI.conditional_bit_mass(value)
        with self.assertRaises(TypeError):
            MEI.conditional_bit_mass(True)

    def test_rejects_invalid_bit_count(self):
        for value in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                MEI.storage_mass(value, 300.0)

    def test_full_reproduction_reports_bridge_unvalidated(self):
        report = MEI.run()
        self.assertEqual(report["equation_reproduced"], "Eq. (6)")
        self.assertEqual(report["derivation_status"]["stored_bit_energy_identification"], "source_assumption_not_validated")
        self.assertTrue(all(report["source_rounding_checks"].values()))
        self.assertIn("ARITHMETIC_REPRODUCED", report["claim_boundary"])

    def test_runs_under_optimized_python(self):
        completed = subprocess.run(
            [sys.executable, "-O", str(RUN_PATH), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["source_work_id"], "VOP-2019-MEI")


class Vopson2019MEIAuthorityTests(unittest.TestCase):
    def test_result_record_preserves_reproduction_boundary(self):
        result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(result["reproduction_status"], "reproduced")
        self.assertEqual(result["claim_class"], "DIAGNOSTIC")
        self.assertEqual(result["assessment"]["intrinsic_stored_bit_energy_identification"], "source-assumption-not-validated")
        self.assertEqual(result["assessment"]["physical_intrinsic_bit_mass"], "unresolved")
        self.assertIsNone(result["source_byte_hash"])

    def test_assumption_graph_uses_one_claim_class_per_node(self):
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        allowed = {"DEFINITION", "THEOREM_TARGET", "PROVED", "COUNTEREXAMPLE", "DIAGNOSTIC", "EMPIRICAL", "INTERPRETIVE", "SPECULATIVE", "NONCLAIM"}
        ids = set()
        for node in graph["nodes"]:
            self.assertIn(node["claim_class"], allowed)
            self.assertNotIn(node["id"], ids)
            ids.add(node["id"])
        self.assertIn("MEI-N6", ids)

    def test_landauer_does_not_entail_intrinsic_bit_energy(self):
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        edge = next(edge for edge in graph["edges"] if edge["from"] == "MEI-N4" and edge["to"] == "MEI-N6")
        self.assertEqual(edge["type"], "does-not-entail")

    def test_source_map_records_inequality_issue(self):
        text = (ROOT / "research/vopson/reproduction/2019-mei/SOURCE_MAP.md").read_text(encoding="utf-8")
        self.assertIn("source-text inequality inconsistency", text)
        self.assertIn("Eq. (6)", text)
        self.assertIn("DOI_AND_EQUATION_IDENTITY != SOURCE_PDF_BYTE_HASH", text)


if __name__ == "__main__":
    unittest.main()
