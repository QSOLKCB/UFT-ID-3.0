from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("pr8_validator", ROOT / "scripts/validate_formalization_contracts.py")
E = load_module("pr8_experiment", ROOT / "experiments/formalization/run.py")
R = load_module("pr8_receipt", ROOT / "experiments/run_pr8.py")


def canonical_documents():
    return {
        "contract": json.loads((ROOT / "machine/formalization_contract.json").read_text()),
        "invariants": json.loads((ROOT / "machine/invariant_specs.json").read_text()),
        "assurance": json.loads((ROOT / "machine/assurance_graph.json").read_text()),
        "obligations": json.loads((ROOT / "machine/definition_obligations.json").read_text()),
        "falsification": json.loads((ROOT / "machine/falsification_contract.json").read_text()),
        "human_docs": {
            "invariant_human": (ROOT / "theory/INVARIANT_CALCULUS.md").read_text(),
            "assurance_human": (ROOT / "theory/ASSURANCE.md").read_text(),
            "obligations_human": (ROOT / "theory/DEFINITION_OBLIGATIONS.md").read_text(),
            "falsification_human": (ROOT / "theory/FALSIFICATION_CONTRACTS.md").read_text(),
            "roadmap": (ROOT / "ROADMAP.md").read_text(),
        },
    }


def validate_docs(value):
    return V.validate_documents(
        value["contract"],
        value["invariants"],
        value["assurance"],
        value["obligations"],
        value["falsification"],
        value["human_docs"],
        check_paths=False,
    )


class PR8FormalizationTests(unittest.TestCase):
    def test_canonical_contract_validates(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["invariant_count"], 6)
        self.assertEqual(result["assurance_node_count"], 12)
        self.assertEqual(result["definition_obligation_count"], 12)
        self.assertEqual(result["model_obligation_count"], 4)

    def test_exact_rotation_and_scaling_adversary(self):
        result = E.run_suite()
        self.assertTrue(result["rotation_norm_exact"]["preserved"])
        self.assertFalse(result["scaling_norm_counterexample"]["preserved"])
        self.assertEqual(result["rotation_norm_exact"]["sqnorm_before"], 25)
        self.assertEqual(result["scaling_norm_counterexample"]["sqnorm_after"], 100)

    def test_observer_entropy_sign_reversal_fixture(self):
        result = E.run_suite()["observer_entropy_sign_counterexample"]
        self.assertGreater(result["fine"]["delta"], 0)
        self.assertLess(result["observer_negative"]["delta"], 0)
        self.assertGreater(result["observer_positive"]["delta"], 0)
        self.assertTrue(result["same_fine_dynamics"])

    def test_many_to_one_map_does_not_support_reversibility(self):
        result = E.run_suite()["reversibility_claim_realization_counterexample"]
        self.assertFalse(result["injective"])
        self.assertFalse(result["inverse_exists_on_full_domain"])
        self.assertFalse(result["claim_supported"])

    def test_synthetic_falsification_condition_triggers(self):
        result = E.run_suite()["falsification_contract_synthetic_fixture"]
        self.assertTrue(result["rejection_condition_met"])
        self.assertEqual(result["status"], "synthetic-rejected")

    def test_receipt_deterministic(self):
        first = R.run_suite()
        second = R.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)


class PR8MutationTests(unittest.TestCase):
    def test_rejects_deleted_hard_rule(self):
        value = canonical_documents()
        value["contract"]["hard_rules"].pop("named_object_implies_well_defined_object")
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("complete expected key set" in error for error in result["errors"]))

    def test_rejects_private_attachment_identifier_leak(self):
        value = canonical_documents()
        source = next(x for x in value["contract"]["source_inputs"] if x["source_class"] == "author-supplied-design-input")
        source["scope"] = "file_00000000bad"
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("private attachment" in error for error in result["errors"]))

    def test_rejects_malformed_public_blob_pin(self):
        value = canonical_documents()
        source = next(x for x in value["contract"]["source_inputs"] if x["source_class"] == "methodological-donor")
        source["blob_sha"] = "abc"
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("40-char Git blob" in error for error in result["errors"]))

    def test_rejects_invariant_without_break_conditions(self):
        value = canonical_documents()
        value["invariants"]["records"][0]["break_conditions"] = []
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("break_conditions" in error for error in result["errors"]))

    def test_rejects_dangling_assurance_edge(self):
        value = canonical_documents()
        value["assurance"]["support_edges"][0]["to"] = "MISSING"
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("dangling endpoint" in error for error in result["errors"]))

    def test_rejects_eigenmode_without_minimum_declarations(self):
        value = canonical_documents()
        item = next(x for x in value["obligations"]["definition_obligations"] if x["term"] == "eigenmode")
        item["minimum_declarations"] = []
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("minimum_declarations" in error for error in result["errors"]))

    def test_rejects_duplicate_model_obligation(self):
        value = canonical_documents()
        value["obligations"]["claim_realization_obligations"].append(
            copy.deepcopy(value["obligations"]["claim_realization_obligations"][0])
        )
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("duplicate model obligation" in error for error in result["errors"]))

    def test_rejects_falsification_example_without_rejection_condition(self):
        value = canonical_documents()
        value["falsification"]["synthetic_conformance_example"]["rejection_conditions"] = []
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("rejection_conditions" in error for error in result["errors"]))

    def test_rejects_roadmap_missing_deferred_stage(self):
        value = canonical_documents()
        value["human_docs"]["roadmap"] = value["human_docs"]["roadmap"].replace(
            "PR #12 — Information-functional robustness",
            "PR #12 — removed",
        )
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("PR #12" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
