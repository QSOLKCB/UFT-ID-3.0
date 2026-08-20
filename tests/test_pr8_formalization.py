from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
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
        "cross_repo_patterns": json.loads((ROOT / "machine/cross_repo_patterns.json").read_text()),
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
        value["cross_repo_patterns"],
        value["human_docs"],
        check_paths=False,
    )


class PR8FormalizationTests(unittest.TestCase):
    def test_canonical_contract_validates(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["invariant_count"], 6)
        self.assertEqual(result["assurance_node_count"], 14)
        self.assertEqual(result["definition_obligation_count"], 12)
        self.assertEqual(result["model_obligation_count"], 4)

    def test_exact_rotation_and_scaling_adversary(self):
        result = E.run_suite()
        self.assertTrue(result["rotation_norm_exact"]["preserved"])
        self.assertFalse(result["scaling_norm_counterexample"]["preserved"])
        self.assertEqual(result["rotation_norm_exact"]["sqnorm_before"], 25)
        self.assertEqual(result["scaling_norm_counterexample"]["sqnorm_after"], 100)

    def test_observer_entropy_sign_reversal_uses_declared_dynamics(self):
        result = E.run_suite()["observer_entropy_sign_counterexample"]
        self.assertGreater(result["fine"]["delta"], 0)
        self.assertLess(result["observer_negative"]["delta"], 0)
        self.assertGreater(result["observer_positive"]["delta"], 0)
        self.assertTrue(result["same_fine_dynamics"])
        self.assertTrue(result["fine_dynamics"]["p1_derived_from_p0"])
        self.assertEqual(result["fine"]["p1"], [0.0, 0.5, 0.0, 0.5])

    def test_many_to_one_map_does_not_support_reversibility(self):
        result = E.run_suite()["reversibility_claim_realization_counterexample"]
        self.assertFalse(result["injective"])
        self.assertFalse(result["inverse_exists_on_full_domain"])
        self.assertFalse(result["claim_supported"])

    def test_synthetic_falsification_condition_is_machine_bound(self):
        result = E.run_suite()["falsification_contract_synthetic_fixture"]
        self.assertTrue(result["rejection_condition_met"])
        self.assertEqual(result["status"], "synthetic-rejected")
        self.assertEqual(result["machine_authority"], "machine/falsification_contract.json")

    def test_changed_machine_falsification_relation_changes_execution(self):
        payload = json.loads((ROOT / "machine/falsification_contract.json").read_text())
        payload["synthetic_conformance_example"]["predictions"] = ["q(1) > q(0)"]
        payload["synthetic_conformance_example"]["rejection_conditions"] = ["q(1) <= q(0)"]
        with tempfile.TemporaryDirectory() as temporary:
            temp_root = Path(temporary)
            (temp_root / "machine").mkdir()
            (temp_root / "machine/falsification_contract.json").write_text(json.dumps(payload))
            old_root = E.ROOT
            E.ROOT = temp_root
            try:
                with self.assertRaises(RuntimeError):
                    E.run_suite()
            finally:
                E.ROOT = old_root

    def test_receipt_deterministic_and_hashes_imported_helpers(self):
        first = R.run_suite()
        second = R.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)
        for path in (
            "experiments/__init__.py",
            "experiments/lib/__init__.py",
            "experiments/lib/information.py",
            "machine/cross_repo_patterns.json",
        ):
            self.assertIn(path, first["source_sha256"])


class PR8MutationTests(unittest.TestCase):
    def assert_error_contains(self, value, fragment):
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_rejects_deleted_hard_rule(self):
        value = canonical_documents()
        value["contract"]["hard_rules"].pop("named_object_implies_well_defined_object")
        self.assert_error_contains(value, "complete expected key set")

    def test_rejects_unregistered_cross_repo_source(self):
        value = canonical_documents()
        value["contract"]["cross_repo_pattern_refs"][0] = "XR-P99"
        self.assert_error_contains(value, "canonical donor pattern set")

    def test_rejects_private_attachment_identifier_or_extra_metadata_key(self):
        value = canonical_documents()
        source = value["contract"]["source_inputs"][0]
        source["attachment_id"] = "file-secret-123"
        self.assert_error_contains(value, "exact allow-listed keys")

    def test_rejects_private_source_hash_key_even_when_null_or_fake(self):
        value = canonical_documents()
        source = value["contract"]["source_inputs"][0]
        source["blob_sha"] = "deadbeef"
        self.assert_error_contains(value, "exact allow-listed keys")

    def test_rejects_invariant_generic_schema_without_name(self):
        value = canonical_documents()
        value["invariants"]["generic_form"]["fields"].remove("name")
        self.assert_error_contains(value, "generic_form.fields")

    def test_rejects_invariant_without_break_conditions(self):
        value = canonical_documents()
        value["invariants"]["records"][0]["break_conditions"] = []
        self.assert_error_contains(value, "break_conditions")

    def test_rejects_proved_invariant_without_proof(self):
        value = canonical_documents()
        record = next(x for x in value["invariants"]["records"] if x["id"] == "UI-INV-002")
        record.pop("proof")
        self.assert_error_contains(value, "requires an explicit proof")

    def test_rejects_dangling_assurance_edge(self):
        value = canonical_documents()
        value["assurance"]["support_edges"][0]["to"] = "MISSING"
        self.assert_error_contains(value, "dangling endpoint")

    def test_rejects_duplicate_forbidden_assurance_pair(self):
        value = canonical_documents()
        value["assurance"]["forbidden_automatic_promotions"].append(
            copy.deepcopy(value["assurance"]["forbidden_automatic_promotions"][0])
        )
        self.assert_error_contains(value, "duplicate forbidden assurance edge")

    def test_rejects_pair_both_supported_and_forbidden(self):
        value = canonical_documents()
        value["assurance"]["forbidden_automatic_promotions"].append({
            "from": "STATEMENT",
            "to": "FORMAL_ENCODING",
            "reason": "contradictory mutation",
        })
        self.assert_error_contains(value, "both supported and forbidden")

    def test_rejects_missing_model_output_boundary(self):
        value = canonical_documents()
        value["assurance"]["forbidden_automatic_promotions"] = [
            edge for edge in value["assurance"]["forbidden_automatic_promotions"]
            if not (edge["from"] == "MODEL_OUTPUT" and edge["to"] == "EXECUTION_EVIDENCE")
        ]
        self.assert_error_contains(value, "canonical PR8 non-promotion set")

    def test_rejects_replaced_definition_obligation_identity(self):
        value = canonical_documents()
        item = next(x for x in value["obligations"]["definition_obligations"] if x["id"] == "DEF-OBL-EIGENMODE")
        item["id"] = "DEF-OBL-ALIEN"
        self.assert_error_contains(value, "definition obligation IDs")

    def test_rejects_replaced_model_obligation_identity(self):
        value = canonical_documents()
        item = next(x for x in value["obligations"]["claim_realization_obligations"] if x["id"] == "MODEL-OBL-DYNAMICS")
        item["id"] = "MODEL-OBL-ALIEN"
        self.assert_error_contains(value, "model obligation IDs")

    def test_rejects_eigenmode_without_minimum_declarations(self):
        value = canonical_documents()
        item = next(x for x in value["obligations"]["definition_obligations"] if x["term"] == "eigenmode")
        item["minimum_declarations"] = []
        self.assert_error_contains(value, "minimum_declarations")

    def test_rejects_falsification_example_without_rejection_condition(self):
        value = canonical_documents()
        value["falsification"]["synthetic_conformance_example"]["rejection_conditions"] = []
        self.assert_error_contains(value, "rejection_conditions")

    def test_rejects_unsupported_falsification_relation(self):
        value = canonical_documents()
        value["falsification"]["synthetic_conformance_example"]["predictions"] = ["q(1) approximately q(0)"]
        self.assert_error_contains(value, "supported q(1) relation")

    def test_rejects_dual_assurance_claim_class_header(self):
        value = canonical_documents()
        value["human_docs"]["assurance_human"] = value["human_docs"]["assurance_human"].replace(
            "**Claim class:** `DEFINITION`.",
            "**Claim class:** `DEFINITION` / `NONCLAIM`.",
        )
        self.assert_error_contains(value, "canonical claim class")

    def test_rejects_roadmap_missing_deferred_stage(self):
        value = canonical_documents()
        value["human_docs"]["roadmap"] = value["human_docs"]["roadmap"].replace(
            "PR #12 — Information-functional robustness",
            "PR #12 — removed",
        )
        self.assert_error_contains(value, "PR #12")


if __name__ == "__main__":
    unittest.main()
