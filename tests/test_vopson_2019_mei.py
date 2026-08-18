from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/reproduction/vopson_2019_mei/run.py"
RECEIPT_PATH = ROOT / "experiments/run_pr6.py"
VALIDATOR_PATH = ROOT / "scripts/validate_vopson_2019_mei.py"
RESULT_PATH = ROOT / "research/vopson/reproduction/2019-mei/result.json"
GRAPH_PATH = ROOT / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"
CONTRACT_PATH = ROOT / "machine/contract.json"
CORPUS_PATH = ROOT / "research/vopson/corpus.json"
CLAIM_GRAPH_PATH = ROOT / "research/vopson/CLAIM_GRAPH.json"
MATRIX_PATH = ROOT / "research/vopson/REPRODUCTION_MATRIX.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEI = load_module("vopson_2019_mei", RUN_PATH)
RECEIPT = load_module("vopson_2019_mei_receipt", RECEIPT_PATH)
VALIDATOR = load_module("validate_vopson_2019_mei", VALIDATOR_PATH)


def mutated_fixture(mutator):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "fixtures.json"
        payload = json.loads(MEI.FIXTURES.read_text(encoding="utf-8"))
        mutator(payload)
        path.write_text(json.dumps(payload), encoding="utf-8")
        original = MEI.FIXTURES
        MEI.FIXTURES = path
        try:
            return MEI.run()
        finally:
            MEI.FIXTURES = original


def validator_mutation(mutator):
    with tempfile.TemporaryDirectory() as temporary:
        clone = Path(temporary) / "repo"
        required = {
            "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json",
            "research/vopson/reproduction/2019-mei/result.json",
            "research/vopson/corpus.json",
            "research/vopson/CLAIM_GRAPH.json",
            "research/vopson/REPRODUCTION_MATRIX.md",
            "machine/contract.json",
            *VALIDATOR.REQUIRED_EVIDENCE,
        }
        for relative in required:
            source = ROOT / relative
            target = clone / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        mutator(clone)
        return VALIDATOR.validate(clone)


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
        self.assertAlmostEqual(MEI.conditional_bit_mass(200.0), 2.0 * MEI.conditional_bit_mass(100.0), delta=1e-50)

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
            with self.assertRaises((TypeError, ValueError)):
                MEI.storage_mass(value, 300.0)

    def test_fixture_rejects_boolean_temperature_before_coercion(self):
        with self.assertRaises(TypeError):
            mutated_fixture(lambda payload: payload["temperature_cases"][0].__setitem__("temperature_K", True))

    def test_fixture_rejects_string_temperature_before_coercion(self):
        with self.assertRaises(TypeError):
            mutated_fixture(lambda payload: payload["temperature_cases"][0].__setitem__("temperature_K", "300"))

    def test_fixture_rejects_fractional_bits_without_truncation(self):
        with self.assertRaises(TypeError):
            mutated_fixture(lambda payload: payload["storage_case"].__setitem__("bits", 8_000_000_000_000.5))

    def test_full_reproduction_reports_bridge_unvalidated(self):
        report = MEI.run()
        self.assertEqual(report["equation_reproduced"], "Eq. (6)")
        self.assertEqual(report["derivation_status"]["stored_bit_energy_identification"], "source_assumption_not_validated")
        self.assertTrue(all(report["source_rounding_checks"].values()))
        self.assertIn("ARITHMETIC_REPRODUCED", report["claim_boundary"])

    def test_runs_under_optimized_python(self):
        completed = subprocess.run([sys.executable, "-O", str(RUN_PATH), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(completed.stdout)["source_work_id"], "VOP-2019-MEI")


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

    def test_canonical_registries_are_synchronized(self):
        corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        work = next(item for item in corpus["works"] if item["work_id"] == "VOP-2019-MEI")
        self.assertEqual(work["equation_map_status"], "complete")
        self.assertEqual(work["reproduction_status"], "reproduced")
        self.assertTrue(work["evidence_paths"])

        graph = json.loads(CLAIM_GRAPH_PATH.read_text(encoding="utf-8"))
        claim = next(item for item in graph["nodes"] if item["node_id"] == "CL-MEI-BIT-MASS")
        self.assertEqual(claim["claim_class"], "THEOREM_TARGET")
        self.assertEqual(claim["assessment_status"], "arithmetic-reproduced-physical-hypothesis-unresolved")
        self.assertTrue(claim["evidence_paths"])
        self.assertIn("remain unresolved", claim["reproduction_obligation"])

    def test_machine_contract_registers_pr6_validator(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], "1.5.1")
        authority = contract["vopson_2019_mei_reproduction"]
        self.assertEqual(authority["validator"], "scripts/validate_vopson_2019_mei.py")
        self.assertFalse(contract["hard_rules"]["landauer_erasure_bound_implies_intrinsic_stored_bit_energy"])
        self.assertFalse(contract["hard_rules"]["arithmetic_reproduction_implies_physical_validation"])

    def test_reproduction_matrix_records_reproduced_status(self):
        matrix = MATRIX_PATH.read_text(encoding="utf-8")
        self.assertIn("| `VOP-2019-MEI` | Derive bit-mass formula and storage-device prediction | `reproduced` |", matrix)
        self.assertIn("ARITHMETIC_REPRODUCED", matrix)

    def test_pr6_authority_validator_passes(self):
        report = VALIDATOR.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["summary"]["corpus_status"], "reproduced")
        self.assertEqual(report["summary"]["claim_status"], "arithmetic-reproduced-physical-hypothesis-unresolved")

    def test_validator_rejects_dangling_assumption_edge(self):
        def mutate(root: Path):
            path = root / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"
            graph = json.loads(path.read_text(encoding="utf-8"))
            graph["edges"].append({"from": "MEI-N8", "to": "UNKNOWN", "type": "supports"})
            path.write_text(json.dumps(graph), encoding="utf-8")
        report = validator_mutation(mutate)
        self.assertFalse(report["ok"])
        self.assertTrue(any("dangling target" in error for error in report["errors"]), report["errors"])

    def test_validator_rejects_undeclared_assumption_edge_type(self):
        def mutate(root: Path):
            path = root / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"
            graph = json.loads(path.read_text(encoding="utf-8"))
            graph["edges"][0]["type"] = "magically-proves"
            path.write_text(json.dumps(graph), encoding="utf-8")
        report = validator_mutation(mutate)
        self.assertFalse(report["ok"])
        self.assertTrue(any("undeclared edge type" in error for error in report["errors"]), report["errors"])

    def test_validator_rejects_missing_required_node_field(self):
        def mutate(root: Path):
            path = root / "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json"
            graph = json.loads(path.read_text(encoding="utf-8"))
            del graph["nodes"][0]["statement"]
            path.write_text(json.dumps(graph), encoding="utf-8")
        report = validator_mutation(mutate)
        self.assertFalse(report["ok"])
        self.assertTrue(any("statement must be non-empty" in error for error in report["errors"]), report["errors"])


class Vopson2019MEIReceiptTests(unittest.TestCase):
    def test_receipt_is_deterministic_within_runtime(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["local_source_sha256"], second["local_source_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)
        self.assertIsNone(first["primary_source_byte_hash"])

    def test_receipt_hash_only_is_json(self):
        completed = subprocess.run([sys.executable, str(RECEIPT_PATH), "--hash-only"], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(len(json.loads(completed.stdout)["suite_fingerprint_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
