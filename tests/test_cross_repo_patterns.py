from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str, root: Path = ROOT):
    path = root / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("validate_cross_repo_patterns", "scripts/validate_cross_repo_patterns.py")
EXPERIMENT = load_module("cross_repo_experiment", "experiments/cross_repo/run.py")
RECEIPT = load_module("cross_repo_receipt", "experiments/run_cross_repo.py")


def read_json(root: Path, relative: str):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write_json(root: Path, relative: str, value) -> None:
    (root / relative).write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def validate_mutation(mutator):
    with tempfile.TemporaryDirectory() as temporary:
        clone = Path(temporary) / "repo"
        clone.mkdir()
        for relative in (
            "machine/cross_repo_patterns.json",
            "machine/cross_repo_results.json",
            "machine/contract.json",
            "research/CROSS_REPO_PATTERN_ATLAS.md",
            "theory/AUXILIARY_CONTRACTS.md",
            "theory/CROSS_REPO_RESULTS.md",
            "experiments/cross_repo/run.py",
            "experiments/run_cross_repo.py",
        ):
            target = clone / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        mutator(clone)
        return VALIDATOR.validate(clone)


class CrossRepoRegistryTests(unittest.TestCase):
    def setUp(self):
        self.patterns = read_json(ROOT, "machine/cross_repo_patterns.json")
        self.results = read_json(ROOT, "machine/cross_repo_results.json")

    def assert_report_contains(self, report, fragment: str):
        self.assertFalse(report["ok"])
        self.assertTrue(
            any(fragment in error for error in report["errors"]),
            report["errors"],
        )

    def test_canonical_registry_passes(self):
        report = VALIDATOR.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertGreaterEqual(report["summary"]["patterns"], 18)
        self.assertEqual(report["summary"]["quarantined"], 3)
        self.assertEqual(report["summary"]["results"], 7)
        self.assertFalse(report["summary"]["remote_freshness_checked"])
        self.assertTrue(report["summary"]["human_result_sync_checked"])
        self.assertTrue(report["summary"]["human_pattern_atlas_sync_checked"])
        self.assertEqual(report["summary"]["snapshot_date"], "2026-08-20")

    def test_genus_context_sources_are_canonical_registry_entries(self):
        by_id = {entry["pattern_id"]: entry for entry in self.patterns["patterns"]}
        self.assertEqual(
            (by_id["XR-P17"]["repository"], by_id["XR-P17"]["source_path"], by_id["XR-P17"]["source_blob_sha"]),
            ("QSOLKCB/SONIFICATION", "docs/MATHEMATICAL_MODEL.md", "0e8f986dd5ca191c1eded726dd6e276c1f856613"),
        )
        self.assertEqual(
            (by_id["XR-P18"]["repository"], by_id["XR-P18"]["source_path"], by_id["XR-P18"]["source_blob_sha"]),
            ("QSOLKCB/SPECTRAL", "E8/APP/README.md", "4855bfff69d89c4920a2b2daf59c38b875a617ec"),
        )

    def test_registry_uses_public_source_repositories_only(self):
        forbidden = VALIDATOR.PRIVATE_REPOSITORIES
        for entry in self.patterns["patterns"] + self.patterns["quarantined_lineage"]:
            self.assertNotIn(entry["repository"], forbidden)

    def test_every_positive_pattern_has_explicit_bridge_fields(self):
        for entry in self.patterns["patterns"]:
            self.assertTrue(entry["source_contract"].strip())
            self.assertTrue(entry["preserved_structure"])
            self.assertTrue(entry["discarded_structure"])

    def test_rejects_private_repository_source(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["patterns"][0]["repository"] = "QSOLKCB/QSOL-CONTEXT"
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "private repository is forbidden")

    def test_rejects_open_pr_only_source_status(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["patterns"][0]["source_status"] = "open-pr-only"
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "open-PR-only source status is forbidden")

    def test_rejects_malformed_blob_pin(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["patterns"][0]["source_blob_sha"] = "deadbeef"
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "source_blob_sha must be 40 lowercase hex")

    def test_rejects_missing_preserved_structure(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["patterns"][0].pop("preserved_structure")
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "preserved_structure must be a non-empty string list")

    def test_rejects_missing_discarded_structure(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["patterns"][0]["discarded_structure"] = []
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "discarded_structure must be a non-empty string list")

    def test_rejects_quarantined_pattern_as_positive_result_source(self):
        def mutate(root: Path):
            results = read_json(root, "machine/cross_repo_results.json")
            results["results"][0]["source_patterns"] = ["XR-Q02"]
            write_json(root, "machine/cross_repo_results.json", results)
        self.assert_report_contains(validate_mutation(mutate), "unknown or quarantined source pattern")

    def test_rejects_unknown_pattern_dependency(self):
        def mutate(root: Path):
            results = read_json(root, "machine/cross_repo_results.json")
            results["results"][0]["source_patterns"] = ["XR-P99"]
            write_json(root, "machine/cross_repo_results.json", results)
        self.assert_report_contains(validate_mutation(mutate), "unknown or quarantined source pattern")

    def test_rejects_human_atlas_omitting_xr_p17_or_xr_p18(self):
        for pattern_id in ("XR-P17", "XR-P18"):
            with self.subTest(pattern_id=pattern_id):
                def mutate(root: Path, pid=pattern_id):
                    path = root / "research/CROSS_REPO_PATTERN_ATLAS.md"
                    path.write_text(path.read_text(encoding="utf-8").replace(pid, f"REMOVED-{pid}"), encoding="utf-8")
                self.assert_report_contains(validate_mutation(mutate), f"human cross-repo atlas missing canonical context pattern: {pattern_id}")

    def test_rejects_future_utc_snapshot_date(self):
        def mutate(root: Path):
            patterns = read_json(root, "machine/cross_repo_patterns.json")
            patterns["snapshot_date"] = "2026-08-21"
            write_json(root, "machine/cross_repo_patterns.json", patterns)
        self.assert_report_contains(validate_mutation(mutate), "snapshot_date mismatch")

    def test_rejects_human_claim_class_drift(self):
        def mutate(root: Path):
            path = root / "theory/CROSS_REPO_RESULTS.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "## CR6. Integrity can be exact while semantic truth is false\n\n**Class:** `COUNTEREXAMPLE`",
                "## CR6. Integrity can be exact while semantic truth is false\n\n**Class:** `EMPIRICAL`",
            )
            path.write_text(text, encoding="utf-8")
        self.assert_report_contains(validate_mutation(mutate), "CR6: human claim_class differs")

    def test_rejects_human_title_drift(self):
        def mutate(root: Path):
            path = root / "theory/CROSS_REPO_RESULTS.md"
            text = path.read_text(encoding="utf-8").replace(
                "## CR1. Content identity invariant under byte-preserving transport",
                "## CR1. Different title",
            )
            path.write_text(text, encoding="utf-8")
        self.assert_report_contains(validate_mutation(mutate), "CR1: human title differs")

    def test_rejects_human_scope_drift(self):
        def mutate(root: Path):
            path = root / "theory/CROSS_REPO_RESULTS.md"
            text = path.read_text(encoding="utf-8").replace(
                "**Canonical scope:** `n>=1 and gcd(k,n)=1`",
                "**Canonical scope:** `all integers`",
            )
            path.write_text(text, encoding="utf-8")
        self.assert_report_contains(validate_mutation(mutate), "CR4: human scope differs")


class CrossRepoFiniteResultTests(unittest.TestCase):
    def test_cr1_content_identity_survives_location_change(self):
        case = EXPERIMENT.transport_identity_case()
        hashes = {entry["content_sha256"] for entry in case["locations"]}
        locations = {entry["location"] for entry in case["locations"]}
        self.assertEqual(len(hashes), 1)
        self.assertGreater(len(locations), 1)

    def test_cr2_noninjective_projection_has_failed_reconstructions(self):
        case = EXPERIMENT.projection_collision_case()
        self.assertTrue(case["failed_reconstructions"])
        self.assertGreaterEqual(len(case["fibres"]), 1)

    def test_cr3_same_measurement_flips_across_calibration_profiles(self):
        case = EXPERIMENT.calibration_locality_case()
        self.assertEqual(case["measurement"], 0.60)
        self.assertEqual(case["classifications"]["Gamma_A"], "HIGH")
        self.assertEqual(case["classifications"]["Gamma_B"], "LOW")

    def test_cr4_coprime_stride_is_complete_and_non_coprime_control_is_not(self):
        case = EXPERIMENT.cyclic_traversal_case()
        for fixture in case["coprime_fixtures"]:
            self.assertEqual(fixture["unique_states"], fixture["n"])
            self.assertEqual(fixture["gcd"], 1)
        control = case["non_coprime_control"]
        self.assertLess(control["unique_states"], control["n"])

    def test_cr5_minimum_basis_uses_deterministic_total_tie_break(self):
        case = EXPERIMENT.minimum_basis_case()
        self.assertEqual(case["selected_basis"], ["r1", "r5"])
        self.assertEqual(case["selected_total_cost"], 3)
        self.assertEqual(case["selected_count"], 2)
        self.assertLessEqual(case["exhaustive_work_subsets"], case["max_exhaustive_subsets"])

    def test_cr5_rejects_negative_cost_even_with_empty_obligations(self):
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            EXPERIMENT.minimum_basis(set(), {"r1": set()}, {"r1": -1})

    def test_cr5_rejects_boolean_and_non_integer_costs(self):
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            EXPERIMENT.minimum_basis({"x"}, {"r1": {"x"}}, {"r1": True})
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            EXPERIMENT.minimum_basis({"x"}, {"r1": {"x"}}, {"r1": 1.5})

    def test_cr5_rejects_exhaustive_work_above_ceiling_before_enumeration(self):
        coverage = {f"r{i:02d}": {"x"} for i in range(19)}
        costs = {record_id: 1 for record_id in coverage}
        with self.assertRaisesRegex(ValueError, "exceeds ceiling"):
            EXPERIMENT.minimum_basis({"x"}, coverage, costs)

    def test_cr6_integrity_does_not_promote_false_semantics(self):
        case = EXPERIMENT.integrity_not_truth_case()
        self.assertTrue(case["integrity_verified"])
        self.assertFalse(case["semantic_truth"])
        self.assertEqual(case["statement"], "2+2=5")

    def test_cr7_deterministic_replay_requires_same_input_and_model(self):
        case = EXPERIMENT.replay_case()
        self.assertTrue(case["same_input_same_result"])
        self.assertTrue(case["changed_input_control_differs"])

    def test_receiver_diagnostic_names_preserved_structure(self):
        case = EXPERIMENT.receiver_contract_case()
        self.assertEqual(case["source_ratios"], case["uniform_scale_ratios"])
        self.assertNotEqual(case["source_ratios"], case["clipped_ratios"])

    def test_full_suite_has_seven_results(self):
        suite = EXPERIMENT.run()
        self.assertEqual(len(suite["results"]), 7)
        self.assertEqual({item["result_id"] for item in suite["results"]}, {f"CR{i}" for i in range(1, 8)})


class CrossRepoReceiptTests(unittest.TestCase):
    def test_receipt_deterministic_payload_is_stable_within_runtime(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["source_sha256"], second["source_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(len(first["suite_fingerprint_sha256"]), 64)

    def test_experiment_runs_under_optimized_python(self):
        completed = subprocess.run(
            [sys.executable, "-O", "experiments/cross_repo/run.py", "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["suite_id"], "UFTID3-CROSS-REPO-FINITE-PATTERNS")

    def test_hash_only_receipt_is_json(self):
        completed = subprocess.run(
            [sys.executable, "experiments/run_cross_repo.py", "--hash-only"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(len(payload["suite_fingerprint_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
