from __future__ import annotations

import json
import importlib.util
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


V = load_module("pr11_relation_validator", ROOT / "scripts/validate_relation_core.py")
E = load_module("pr11_relation_experiment", ROOT / "experiments/relation/run.py")
R = load_module("pr11_relation_receipt", ROOT / "experiments/run_pr11.py")


def canonical_documents():
    return {
        "contract": json.loads((ROOT / "machine/relation_contract.json").read_text()),
        "theorems": json.loads((ROOT / "machine/relation_theorems.json").read_text()),
        "counterexamples": json.loads((ROOT / "machine/relation_counterexamples.json").read_text()),
        "selection": json.loads((ROOT / "machine/genus_selection_specimen.json").read_text()),
        "cross_repo_patterns": json.loads((ROOT / "machine/cross_repo_patterns.json").read_text()),
        "roadmap_state": json.loads((ROOT / "machine/roadmap_state.json").read_text()),
        "base_contract": json.loads((ROOT / "machine/contract.json").read_text()),
        "human": (ROOT / "theory/RELATION_CALCULUS.md").read_text(),
        "roadmap": (ROOT / "ROADMAP.md").read_text(),
    }


def validate_docs(value):
    return V.validate_documents(
        value["contract"],
        value["theorems"],
        value["counterexamples"],
        value["selection"],
        value["cross_repo_patterns"],
        value["roadmap_state"],
        value["base_contract"],
        value["human"],
        value["roadmap"],
        check_paths=False,
    )


class PR11RelationCoreTests(unittest.TestCase):
    def test_canonical_contract_validates(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["theorem_count"], 5)
        self.assertEqual(result["counterexample_count"], 3)
        self.assertEqual(result["public_context_ref_count"], 2)

    def test_exhaustive_relation_cardinality_is_exact(self):
        result = E.exhaustive_theorem_checks()
        self.assertEqual(result["relation_counts"], {"Fin1": 2, "Fin2": 16, "Fin3": 512})
        self.assertEqual(result["total_relations"], 530)
        self.assertGreater(result["implication_applicable_counts"]["reach_preservation_instances"], 0)

    def test_all_foundational_implications_hold_through_fin3(self):
        result = E.exhaustive_theorem_checks()
        counts = result["implication_applicable_counts"]
        for key in (
            "reach_preservation_instances",
            "right_unique_implies_confluent",
            "confluent_implies_at_most_one_reachable_normal",
            "terminating_implies_normalizes",
            "terminating_and_confluent_implies_unique_reachable_normal",
        ):
            self.assertGreater(counts[key], 0)

    def test_fork3_is_terminating_nonconfluent_and_nonunique_normal(self):
        fixture = E.FIXTURES["CX-RW-FORK3"]
        result = E.relation_properties(**fixture)
        self.assertTrue(result["terminating"])
        self.assertFalse(result["confluent"])
        self.assertEqual(result["reachable_normal_forms"]["a"], ["b", "c"])

    def test_loop1_is_confluent_nonterminating_and_has_no_normal(self):
        fixture = E.FIXTURES["CX-RW-LOOP1"]
        result = E.relation_properties(**fixture)
        self.assertTrue(result["confluent"])
        self.assertFalse(result["terminating"])
        self.assertEqual(result["normal_states"], [])

    def test_exit2_has_unique_normal_but_nonterminating_branch(self):
        fixture = E.FIXTURES["CX-RW-EXIT2"]
        result = E.relation_properties(**fixture)
        self.assertTrue(result["confluent"])
        self.assertFalse(result["terminating"])
        self.assertFalse(result["right_unique"])
        self.assertEqual(result["reachable_normal_forms"]["a"], ["b"])

    def test_counterexample_minimality_checks(self):
        result = E.minimality_checks()
        self.assertTrue(all(result.values()))

    def test_genus_selection_fixture_refutes_unique_selection(self):
        result = E.genus_selection_fixture()
        self.assertEqual(result["distinct_reachable_normal_labels"], [10, 30])
        self.assertFalse(result["at_most_one_reachable_normal_from_common"])
        self.assertTrue(result["refutes_unique_selection"])

    def test_invalid_carrier_or_oversized_enumeration_fails_closed(self):
        with self.assertRaises(ValueError):
            E.enumerate_relations(4).__next__()
        with self.assertRaises(ValueError):
            E.reachable(("a",), {("a", "b")}, "a")

    def test_receipt_is_deterministic_and_binds_authority(self):
        first = R.run_suite()
        second = R.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)
        self.assertIn("machine/relation_contract.json", first["source_sha256"])
        self.assertIn("machine/genus_selection_specimen.json", first["source_sha256"])
        self.assertIn("machine/cross_repo_patterns.json", first["source_sha256"])
        self.assertIn("ROADMAP.md", first["source_sha256"])


class PR11RelationMutationTests(unittest.TestCase):
    def assert_error_contains(self, value, fragment: str):
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_rejects_recovery_carrier_forced_into_admissible_codomain(self):
        value = canonical_documents()
        value["contract"]["primary_types"]["rewrite_relation"] = "K subseteq X x A"
        self.assert_error_contains(value, "primary_types canonical mapping drift")

    def test_rejects_residual_symbol_reintroduced_as_rewrite_relation(self):
        value = canonical_documents()
        value["contract"]["primary_types"]["rewrite_relation"] = "r:X->X->Prop"
        self.assert_error_contains(value, "primary_types canonical mapping drift")

    def test_rejects_admissibility_conflated_with_normality(self):
        value = canonical_documents()
        value["contract"]["primary_types"]["admissibility"] = "A(x) iff Normal_stepRel(x)"
        self.assert_error_contains(value, "primary_types canonical mapping drift")

    def test_rejects_other_primary_type_drift(self):
        for field in ("reachability", "normal", "joinable", "termination_orientation"):
            with self.subTest(field=field):
                value = canonical_documents()
                value["contract"]["primary_types"][field] = "drifted"
                self.assert_error_contains(value, "primary_types canonical mapping drift")

    def test_rejects_hard_rule_promotion(self):
        value = canonical_documents()
        value["contract"]["hard_rules"]["confluence_implies_termination"] = True
        self.assert_error_contains(value, "hard_rules must remain false")

    def test_rejects_malformed_claim_class_authority_without_crashing(self):
        for malformed in (None, 7, True, {"DEFINITION": True}):
            with self.subTest(malformed=malformed):
                value = canonical_documents()
                value["base_contract"]["claim_classes"] = malformed
                self.assert_error_contains(value, "base project claim_classes must be a list")

    def test_rejects_theorem_statement_broadening(self):
        value = canonical_documents()
        record = next(r for r in value["theorems"]["records"] if r["id"] == "UFT-RW-003")
        record["statement"] = "Confluence makes every state normalize uniquely."
        self.assert_error_contains(value, "UFT-RW-003 theorem statement drift")

    def test_rejects_derived_corollary_statement_broadening(self):
        value = canonical_documents()
        value["theorems"]["derived_corollaries"][0]["statement"] = "Termination alone gives exactly one reachable normal form."
        self.assert_error_contains(value, "derived corollary canonical payload drift")

    def test_rejects_derived_corollary_name_drift(self):
        value = canonical_documents()
        value["theorems"]["derived_corollaries"][0]["name"] = "termination-alone-unique-normal"
        self.assert_error_contains(value, "derived corollary canonical payload drift")

    def test_rejects_human_derived_corollary_drift(self):
        value = canonical_documents()
        value["human"] = value["human"].replace(V.EXPECTED_DERIVED_HUMAN_MARKER, "**Canonical derived corollary:** `Termination alone suffices.`")
        self.assert_error_contains(value, "human derived corollary canonical statement drift")

    def test_rejects_newman_promoted_to_headline_theorem(self):
        value = canonical_documents()
        value["theorems"]["records"].append({
            "id": "UFT-RW-005",
            "lean_target_name": "UFT_RW_005_newman",
            "name": "Newman",
            "claim_class": "PROVED",
            "statement": "Termination plus local confluence implies confluence.",
            "hypotheses": ["stepRel terminates", "stepRel is locally confluent"],
            "proof_reference": "theory/RELATION_CALCULUS.md#what-is-deliberately-deferred",
            "executable_evidence": ["experiments/relation/run.py"],
            "nonclaims": ["mutation fixture"],
        })
        self.assert_error_contains(value, "relation theorem IDs")

    def test_rejects_malformed_deferred_theorem_entry_without_crashing(self):
        value = canonical_documents()
        value["theorems"]["deferred_theorem_targets"] = ["bad"]
        self.assert_error_contains(value, "deferred theorem target must be an object")

    def test_rejects_fork3_edge_drift(self):
        value = canonical_documents()
        record = next(r for r in value["counterexamples"]["records"] if r["id"] == "CX-RW-FORK3")
        record["edges"] = [["a", "b"]]
        self.assert_error_contains(value, "CX-RW-FORK3.edges drift")

    def test_rejects_genus_label_collapse(self):
        value = canonical_documents()
        value["selection"]["logical_fixture"]["branches"][1]["label"]["value"] = 10
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_selection_schema_drift(self):
        value = canonical_documents()
        value["selection"]["schema_version"] = "9.9.9"
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_selection_source_drift(self):
        value = canonical_documents()
        value["selection"]["logical_fixture"]["source"] = "different-source"
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_selection_result_claim_drift(self):
        value = canonical_documents()
        value["selection"]["logical_fixture"]["result"] = "Genus 10 is uniquely selected."
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_surface_description_drift(self):
        value = canonical_documents()
        value["selection"]["surface_constructions"]["M10"]["surface"] = "mystery"
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_selection_evidence_drift(self):
        value = canonical_documents()
        value["selection"]["evidence"] = ["README.md"]
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_noncanonical_context_reference(self):
        value = canonical_documents()
        value["selection"]["public_context_pattern_refs"][0]["pattern_id"] = "XR-P99"
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_canonical_context_source_pin_drift(self):
        value = canonical_documents()
        record = next(r for r in value["cross_repo_patterns"]["patterns"] if r["pattern_id"] == "XR-P17")
        record["source_blob_sha"] = "0" * 40
        self.assert_error_contains(value, "XR-P17 canonical payload drift")

    def test_rejects_canonical_context_semantic_promotion(self):
        for pattern_id in ("XR-P17", "XR-P18"):
            for field in ("source_contract", "prohibited_inference", "abstraction"):
                with self.subTest(pattern_id=pattern_id, field=field):
                    value = canonical_documents()
                    record = next(r for r in value["cross_repo_patterns"]["patterns"] if r["pattern_id"] == pattern_id)
                    record[field] = "This machinery uniquely selects genus 10 and proves physical topology."
                    self.assert_error_contains(value, f"{pattern_id} canonical payload drift")

    def test_rejects_external_target_promotion(self):
        value = canonical_documents()
        value["selection"]["external_target_boundary"]["status"] = "refuted"
        self.assert_error_contains(value, "genus selection specimen canonical payload drift")

    def test_rejects_live_roadmap_active_surface_drift(self):
        value = canonical_documents()
        value["roadmap_state"]["active_planned_surface"] = 10
        self.assert_error_contains(value, "active planned surface must be PR11")

    def test_rejects_reintroduced_infinite_liveness_claim(self):
        value = canonical_documents()
        value["contract"]["explicit_deferrals"] = [
            x for x in value["contract"]["explicit_deferrals"] if "infinite paths" not in x
        ]
        self.assert_error_contains(value, "explicit deferral missing: infinite paths")

    def test_rejects_human_selection_statement_drift(self):
        value = canonical_documents()
        value["human"] = value["human"].replace(
            V.EXPECTED_STATEMENTS["UFT-SEL-001"],
            "Any two compatible genera are physically equivalent.",
        )
        self.assert_error_contains(value, "UFT-SEL-001 human canonical statement drift")


if __name__ == "__main__":
    unittest.main()
