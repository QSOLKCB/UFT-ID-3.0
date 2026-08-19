from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VPATH = ROOT / "scripts/validate_historical_lineage.py"
RPATH = ROOT / "experiments/run_lineage.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("historical_lineage_validator", VPATH)
RECEIPT = load_module("historical_lineage_receipt", RPATH)


def docs():
    return V.load_documents()


def validate_docs(value):
    return V.validate_documents(
        value["contract"],
        value["sources"],
        value["symbols"],
        value["conflicts"],
        value["results"],
        value["inheritance"],
        value["human"],
    )


def assert_error(testcase: unittest.TestCase, result: dict, fragment: str):
    testcase.assertEqual(result["status"], "error")
    testcase.assertTrue(
        any(fragment in error for error in result["errors"]),
        f"expected error containing {fragment!r}, got {result['errors']}",
    )


class HistoricalLineageTests(unittest.TestCase):
    def test_registry_validates_and_exit_criterion(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertTrue(result["exit_criterion_met"])
        self.assertEqual(
            result["platforms"],
            ["academia", "archived-copy", "authorea", "github", "google-drive", "zenodo"],
        )

    def test_expected_surface_counts(self):
        result = V.validate()
        self.assertEqual(
            (
                result["source_count"],
                result["historical_source_count"],
                result["symbol_count"],
                result["conflict_count"],
                result["result_count"],
                result["inheritance_count"],
            ),
            (15, 9, 29, 11, 15, 7),
        )

    def test_rho_collision_is_explicit(self):
        data = json.loads((ROOT / "machine/historical_symbols.json").read_text())
        item = next(
            item
            for item in data["symbols"]
            if item["historical_symbol"] == "rho (density operator)"
        )
        self.assertEqual(item["disposition"], "symbol-conflict")
        self.assertEqual(item["canonical_target"], "s in S")
        self.assertIn("density-operator requirement", " ".join(item["not_inherited"]))

    def test_lexicographic_weighted_sum_conflict_is_preserved(self):
        data = json.loads((ROOT / "machine/historical_conflicts.json").read_text())
        item = next(item for item in data["conflicts"] if item["conflict_id"] == "HDC-005")
        self.assertEqual(item["resolution"], "do-not-reconcile-silently")
        self.assertIn("weighted", item["historical_definition"].lower())

    def test_dark_state_inheritance_is_quarantined(self):
        data = json.loads((ROOT / "machine/methodological_inheritance.json").read_text())
        item = next(item for item in data["imports"] if item["inheritance_id"] == "INH-04")
        self.assertEqual(item["claim_class"], "DIAGNOSTIC")
        self.assertIn("dark matter/dark energy identification", item["not_inherited"])
        self.assertIn("psi or anomalous cognition mechanism", item["not_inherited"])

    def test_no_private_connector_ids_in_source_registry(self):
        text = (ROOT / "machine/historical_sources.json").read_text()
        for forbidden in ("gmail:", "gdrive:", "docs.google.com", "drive.google.com"):
            self.assertNotIn(forbidden, text)

    def test_drive_hash_scope_is_export_only(self):
        data = json.loads((ROOT / "machine/historical_sources.json").read_text())
        source = next(item for item in data["sources"] if item["source_id"] == "UFT-HIST-008")
        manifestation = next(
            item for item in source["manifestations"] if item["platform"] == "google-drive"
        )
        self.assertFalse(manifestation["native_hash_available"])
        self.assertIn("export bytes", manifestation["hash"]["scope"])

    def test_every_inheritance_has_mapping_noninheritance_and_claim_class(self):
        data = json.loads((ROOT / "machine/methodological_inheritance.json").read_text())
        for item in data["imports"]:
            self.assertTrue(item["source_ids"])
            self.assertTrue(item["claim_class"])
            self.assertTrue(item["preserved_structure"])
            self.assertTrue(item["not_inherited"])
            self.assertTrue(item["prohibited_inference"])
            self.assertTrue(item["uft_mapping"])

    def test_receipt_deterministic(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)


class CodexMutationTests(unittest.TestCase):
    def test_empirical_evidence_path_must_exist_and_be_repository_relative(self):
        value = copy.deepcopy(docs())
        result = value["results"]["results"][0]
        result["result_class"] = "empirical"
        result["evidence_paths"] = ["does/not/exist.json"]
        validation = validate_docs(value)
        assert_error(self, validation, "target does not exist as retained repository evidence")

    def test_empirical_evidence_path_rejects_string_and_escape(self):
        value = copy.deepcopy(docs())
        result = value["results"]["results"][0]
        result["result_class"] = "empirical"
        result["evidence_paths"] = "../outside.json"
        validation = validate_docs(value)
        assert_error(self, validation, "evidence_paths must be a list")

        value = copy.deepcopy(docs())
        result = value["results"]["results"][0]
        result["result_class"] = "empirical"
        result["evidence_paths"] = ["../outside.json"]
        validation = validate_docs(value)
        assert_error(self, validation, "invalid repository-relative path")

    def test_inheritance_requires_uft_mapping(self):
        value = copy.deepcopy(docs())
        value["inheritance"]["imports"][0]["uft_mapping"] = []
        validation = validate_docs(value)
        assert_error(self, validation, "INH-01.uft_mapping must be non-empty")

    def test_inheritance_mapping_must_resolve_to_canonical_id(self):
        value = copy.deepcopy(docs())
        value["inheritance"]["imports"][0]["uft_mapping"] = ["D9999"]
        validation = validate_docs(value)
        assert_error(self, validation, "unknown canonical id")

    def test_human_result_drift_is_detected(self):
        value = copy.deepcopy(docs())
        value["results"]["results"][0]["title"] = "Drifted machine title"
        validation = validate_docs(value)
        assert_error(self, validation, "human result entry out of sync: HIST-R01")

    def test_human_source_metadata_drift_is_detected(self):
        value = copy.deepcopy(docs())
        value["sources"]["sources"][0]["version"] = "v999"
        validation = validate_docs(value)
        assert_error(self, validation, "human source row out of sync: UFT-HIST-001")

    def test_human_conflict_text_drift_is_detected(self):
        value = copy.deepcopy(docs())
        value["conflicts"]["conflicts"][0]["current_definition"] = "Drifted current definition."
        validation = validate_docs(value)
        assert_error(self, validation, "human conflict entry out of sync: HDC-001")

    def test_human_inheritance_detail_drift_is_detected(self):
        value = copy.deepcopy(docs())
        value["inheritance"]["imports"][0]["prohibited_inference"] = "Drifted prohibition."
        validation = validate_docs(value)
        assert_error(self, validation, "human inheritance entry out of sync: INH-01")

    def test_authority_mapping_is_exact(self):
        value = copy.deepcopy(docs())
        value["contract"]["authorities"]["sources"] = "README.md"
        validation = validate_docs(value)
        assert_error(self, validation, "contract authorities mapping mismatch")

    def test_duplicate_inheritance_id_rejected(self):
        value = copy.deepcopy(docs())
        value["inheritance"]["imports"].append(copy.deepcopy(value["inheritance"]["imports"][0]))
        validation = validate_docs(value)
        assert_error(self, validation, "duplicate inheritance_id INH-01")

    def test_doi_collision_rejected(self):
        value = copy.deepcopy(docs())
        value["sources"]["sources"][1]["doi"] = value["sources"]["sources"][0]["doi"]
        validation = validate_docs(value)
        assert_error(self, validation, "DOI collision")

    def test_complete_hard_rule_set_required(self):
        value = copy.deepcopy(docs())
        del value["contract"]["hard_rules"]["missing_metadata_may_be_guessed"]
        validation = validate_docs(value)
        assert_error(self, validation, "contract hard-rule key set mismatch")

    def test_authority_type_schema_and_snapshot_are_synchronized(self):
        value = copy.deepcopy(docs())
        value["symbols"]["schema_version"] = "999"
        validation = validate_docs(value)
        assert_error(self, validation, "symbols authority schema_version mismatch")

        value = copy.deepcopy(docs())
        value["conflicts"]["snapshot_date"] = "2026-08-18"
        validation = validate_docs(value)
        assert_error(self, validation, "conflicts authority snapshot_date mismatch")

    def test_historical_coverage_derived_from_source_family_and_id_format(self):
        value = copy.deepcopy(docs())
        source = value["sources"]["sources"][9]
        source["source_family"] = "historical-uft-id"
        validation = validate_docs(value)
        assert_error(self, validation, "historical source_id must match UFT-HIST-NNN")

    def test_source_provenance_keys_required(self):
        value = copy.deepcopy(docs())
        del value["sources"]["sources"][0]["authors"]
        validation = validate_docs(value)
        assert_error(self, validation, "missing provenance keys")

    def test_interpretive_and_speculative_results_keep_noninheritance_boundary(self):
        value = copy.deepcopy(docs())
        item = next(
            item for item in value["results"]["results"] if item["result_class"] == "speculative"
        )
        item["not_inherited"] = []
        validation = validate_docs(value)
        assert_error(self, validation, f"{item['result_id']} interpretive/speculative result requires non-empty not_inherited")

    def test_result_schema_requires_title_summary_status_and_preservation_lists(self):
        value = copy.deepcopy(docs())
        value["results"]["results"][0]["title"] = ""
        validation = validate_docs(value)
        assert_error(self, validation, "HIST-R01.title required")

        value = copy.deepcopy(docs())
        value["results"]["results"][0]["preserved_for_uft3"] = None
        validation = validate_docs(value)
        assert_error(self, validation, "HIST-R01.preserved_for_uft3 must be a list")

    def test_lineage_receipt_is_retained_by_ci_workflow(self):
        workflow = (ROOT / ".github/workflows/finite-adversarial.yml").read_text()
        self.assertIn("python scripts/validate_historical_lineage.py --json", workflow)
        self.assertIn("artifacts/historical-lineage-validation.json", workflow)
        self.assertIn("python experiments/run_lineage.py --json", workflow)
        self.assertIn("artifacts/historical-lineage-receipt.json", workflow)


if __name__ == "__main__":
    unittest.main()
