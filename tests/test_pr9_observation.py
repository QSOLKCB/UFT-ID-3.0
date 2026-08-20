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


V = load_module("pr9_observation_validator", ROOT / "scripts/validate_observation_specs.py")
E = load_module("pr9_observation_experiment", ROOT / "experiments/observation/run.py")
R = load_module("pr9_observation_receipt", ROOT / "experiments/run_pr9.py")


def canonical_documents():
    return {
        "contract": json.loads((ROOT / "machine/observation_contract.json").read_text()),
        "specs": json.loads((ROOT / "machine/observation_specs.json").read_text()),
        "theorems": json.loads((ROOT / "machine/observation_theorems.json").read_text()),
        "counterexamples": json.loads((ROOT / "machine/observation_counterexamples.json").read_text()),
        "base_contract": json.loads((ROOT / "machine/contract.json").read_text()),
        "formalization_contract": json.loads((ROOT / "machine/formalization_contract.json").read_text()),
        "human": (ROOT / "theory/OBSERVATION_CALCULUS.md").read_text(),
        "roadmap": (ROOT / "ROADMAP.md").read_text(),
    }


def validate_docs(value):
    return V.validate_documents(
        value["contract"],
        value["specs"],
        value["theorems"],
        value["counterexamples"],
        value["base_contract"],
        value["formalization_contract"],
        value["human"],
        value["roadmap"],
        check_paths=False,
    )


class PR9ObservationTests(unittest.TestCase):
    def test_canonical_contract_validates(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["spec_count"], 3)
        self.assertEqual(result["theorem_count"], 5)
        self.assertEqual(result["counterexample_count"], 3)

    def test_constant_observation_is_minimal_noninjective_fixture(self):
        result = E.run_suite()["constant_observation"]
        self.assertFalse(result["injective"])
        self.assertTrue(result["surjective"])
        self.assertEqual(result["fibres"]["0"], [0, 1])
        self.assertFalse(result["global_exact_reconstruction_possible"])

    def test_unused_codomain_separates_image_from_codomain(self):
        result = E.run_suite()["unused_codomain"]
        self.assertFalse(result["surjective"])
        self.assertEqual(result["image"], [0])
        self.assertEqual(result["quotient_cardinality"], result["image_cardinality"])
        self.assertNotEqual(result["image_cardinality"], result["codomain_cardinality"])

    def test_floor_sampling_trichotomy_and_fibre_formula(self):
        cases = E.run_suite()["floor_sampling"]
        self.assertEqual([case["regime"] for case in cases], ["R<L", "R=L", "R>L"])
        self.assertTrue(cases[0]["injective"])
        self.assertFalse(cases[0]["surjective"])
        self.assertTrue(cases[1]["injective"])
        self.assertTrue(cases[1]["surjective"])
        self.assertFalse(cases[2]["injective"])
        self.assertTrue(cases[2]["surjective"])
        for case in cases:
            observed = {key: len(value) for key, value in case["fibres"].items()}
            self.assertEqual(observed, case["fibre_formula"])

    def test_floor_formula_exhaustive_small_grid(self):
        for L in range(1, 8):
            for R in range(1, 8):
                case = E.floor_case(L, R)
                observed = {key: len(value) for key, value in case["fibres"].items()}
                self.assertEqual(observed, case["fibre_formula"])

    def test_floor_case_rejects_nonpositive_dimensions_before_enumeration(self):
        for L, R in ((0, 0), (0, 2), (2, 0), (-1, 2), (2, -1)):
            with self.assertRaises(ValueError):
                E.floor_case(L, R)

    def test_floor_case_rejects_oversized_dimensions_before_enumeration(self):
        ceiling = E.max_floor_dimension()
        with self.assertRaises(ValueError):
            E.floor_case(ceiling + 1, 1)
        with self.assertRaises(ValueError):
            E.floor_case(1, ceiling + 1)

    def test_receipt_is_deterministic_and_binds_declared_authority(self):
        first = R.run_suite()
        second = R.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)
        self.assertIn("machine/contract.json", first["source_sha256"])
        self.assertIn("machine/formalization_contract.json", first["source_sha256"])
        self.assertIn("ROADMAP.md", first["source_sha256"])
        for path in first["declared_evidence_paths"]:
            self.assertIn(path, first["source_sha256"])

    def test_receipt_dependency_extraction_follows_authority_records(self):
        docs = canonical_documents()
        theorem = copy.deepcopy(docs["theorems"])
        counterexamples = copy.deepcopy(docs["counterexamples"])
        theorem["records"][0]["executable_evidence"].append("README.md")
        paths = R.evidence_paths_from_records(theorem, counterexamples)
        self.assertIn("README.md", paths)


class PR9ObservationMutationTests(unittest.TestCase):
    def assert_error_contains(self, value, fragment: str):
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_rejects_deleted_source_type(self):
        value = canonical_documents()
        value["specs"]["records"][0].pop("source_type")
        self.assert_error_contains(value, "exact canonical fields")

    def test_rejects_observation_spec_payload_drift(self):
        value = canonical_documents()
        spec = next(x for x in value["specs"]["records"] if x["id"] == "OBS-SPEC-003")
        spec["map_ref"] = "floor_sample(L,R,i)=floor(i*R/L)"
        self.assert_error_contains(value, "OBS-SPEC-003 observation spec canonical payload drift")

    def test_rejects_stochastic_kind_in_pr9(self):
        value = canonical_documents()
        value["specs"]["records"][0]["kind"] = "stochastic-kernel"
        self.assert_error_contains(value, "canonical payload drift")

    def test_rejects_self_authorizing_generic_field_removal(self):
        value = canonical_documents()
        value["specs"]["generic_form"]["fields"].remove("target_type")
        self.assert_error_contains(value, "ObservationSpec fields")

    def test_rejects_execution_limit_drift(self):
        value = canonical_documents()
        value["contract"]["execution_limits"]["max_floor_dimension"] = 1000000000
        self.assert_error_contains(value, "exact bounded fixture policy")

    def test_rejects_theorem_statement_drift(self):
        value = canonical_documents()
        theorem = next(x for x in value["theorems"]["records"] if x["id"] == "UFT-OBS-003")
        theorem["statement"] = "Every observation has an exact reconstruction."
        self.assert_error_contains(value, "UFT-OBS-003 theorem statement drift")

    def test_rejects_theorem_hypothesis_broadening(self):
        value = canonical_documents()
        theorem = next(x for x in value["theorems"]["records"] if x["id"] == "UFT-OBS-005")
        theorem["hypotheses"] = [
            "L and R are nonnegative integers",
            "i ranges over arbitrary integers",
            "j ranges over arbitrary integers",
        ]
        self.assert_error_contains(value, "UFT-OBS-005 theorem hypotheses drift")

    def test_rejects_quotient_to_full_codomain_mutation(self):
        value = canonical_documents()
        theorem = next(x for x in value["theorems"]["records"] if x["id"] == "UFT-OBS-002")
        theorem["statement"] = "For any O:S->Y, S/~_O is canonically bijective with Y."
        self.assert_error_contains(value, "UFT-OBS-002 theorem statement drift")

    def test_rejects_human_canonical_statement_drift(self):
        value = canonical_documents()
        value["human"] = value["human"].replace(
            "**Canonical statement:** `For any function O:S->Y, the quotient S/~_O is canonically bijective with im(O), via [x] |-> O(x).`",
            "**Canonical statement:** `For any function O:S->Y, the quotient S/~_O is canonically bijective with Y.`",
        )
        self.assert_error_contains(value, "UFT-OBS-002 human canonical statement drift")

    def test_rejects_human_canonical_hypothesis_drift(self):
        value = canonical_documents()
        value["human"] = value["human"].replace(
            "**Canonical hypotheses:** `[\"L and R are positive integers\", \"i ranges over {0,...,R-1}\", \"j ranges over {0,...,L-1}\"]`",
            "**Canonical hypotheses:** `[\"L and R are nonnegative integers\"]`",
        )
        self.assert_error_contains(value, "UFT-OBS-005 human canonical hypotheses drift")

    def test_rejects_theorem_without_proof_reference(self):
        value = canonical_documents()
        theorem = next(x for x in value["theorems"]["records"] if x["id"] == "UFT-OBS-001")
        theorem["proof_reference"] = ""
        self.assert_error_contains(value, "proof reference drift")

    def test_rejects_noncanonical_proof_reference(self):
        value = canonical_documents()
        theorem = next(x for x in value["theorems"]["records"] if x["id"] == "UFT-OBS-001")
        theorem["proof_reference"] = "missing.md#bogus"
        self.assert_error_contains(value, "UFT-OBS-001 proof reference drift")

    def test_rejects_counterexample_class_drift(self):
        value = canonical_documents()
        value["counterexamples"]["records"][0]["claim_class"] = "EMPIRICAL"
        self.assert_error_contains(value, "claim_class must be COUNTEREXAMPLE")

    def test_rejects_hard_rule_promotion(self):
        value = canonical_documents()
        value["contract"]["hard_rules"]["noninjective_observation_has_global_exact_left_inverse"] = True
        self.assert_error_contains(value, "hard_rules must remain false")

    def test_rejects_derived_property_set_drift(self):
        value = canonical_documents()
        value["contract"]["derived_not_stored_as_independent_authority"].remove("fibres")
        self.assert_error_contains(value, "derived observation property set drift")

    def test_rejects_private_locator_hidden_in_allowed_prose(self):
        value = canonical_documents()
        value["specs"]["records"][0]["scope"] = "derived from /mnt/data/private-note.md"
        self.assert_error_contains(value, "forbidden private locator")

    def test_rejects_roadmap_order_drift(self):
        value = canonical_documents()
        value["roadmap"] = value["roadmap"].replace(
            "## PR #10 — Lean observation foundation",
            "## PR #TEMP — Lean observation foundation",
        ).replace(
            "## PR #11 — Relation-first recovery core",
            "## PR #10 — Relation-first recovery core",
        ).replace(
            "## PR #TEMP — Lean observation foundation",
            "## PR #11 — Lean observation foundation",
        )
        self.assert_error_contains(value, "PR-to-surface order drift")

    def test_rejects_machine_roadmap_rebase_drift(self):
        value = canonical_documents()
        value["formalization_contract"]["roadmap_rebase"]["current_sequence"][1]["surface"] = "mystery"
        self.assert_error_contains(value, "exact post-audit schedule authority")

    def test_rejects_deleted_machine_roadmap_rebase(self):
        value = canonical_documents()
        value["formalization_contract"].pop("roadmap_rebase")
        self.assert_error_contains(value, "exact post-audit schedule authority")

    def test_rejects_duplicate_theorem_id(self):
        value = canonical_documents()
        value["theorems"]["records"].append(copy.deepcopy(value["theorems"]["records"][0]))
        self.assert_error_contains(value, "duplicate observation theorem id")


if __name__ == "__main__":
    unittest.main()
