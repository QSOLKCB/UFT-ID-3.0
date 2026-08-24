from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relpath: str):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_module("efp_experiment", "experiments/empirical_falsification_profile/run.py")
V = load_module("efp_validator", "scripts/validate_empirical_falsification_profile.py")


class EmpiricalFalsificationProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = E.run_suite()

    def test_bounded_counts(self):
        self.assertEqual(self.suite["bounded_checks"]["decisions"], {
            "valid_decision_checks": 15,
            "rejected_in_scope_cases": 5,
            "not_rejected_in_scope_cases": 7,
            "inconclusive_cases": 3,
        })
        self.assertEqual(self.suite["bounded_checks"]["invalid_evidence"]["invalid_evidence_mutation_checks"], 60)
        self.assertEqual(self.suite["bounded_checks"]["fit_nonuniqueness"], {"fit_membership_checks": 15, "ambiguous_fit_observations": 3})
        self.assertEqual(self.suite["bounded_checks"]["profile_identity"]["profile_fingerprint_pair_checks"], 3)

    def test_four_decision_states_are_separate(self):
        profile = E.make_profile(0)
        rejected = E.evaluate(profile, E.make_evidence(profile, 1, 0))
        not_rejected = E.evaluate(profile, E.make_evidence(profile, -1, 0))
        inconclusive = E.evaluate(profile, E.make_evidence(profile, 1, 1))
        invalid = E.evaluate(profile, {"formal_counterexample": "CX"})
        self.assertEqual(rejected["decision"], "REJECTED_IN_SCOPE")
        self.assertFalse(rejected["global_theory_rejected"])
        self.assertEqual(not_rejected["decision"], "NOT_REJECTED_IN_SCOPE")
        self.assertFalse(not_rejected["confirmation_promoted"])
        self.assertEqual(inconclusive["decision"], "INCONCLUSIVE")
        self.assertEqual(invalid["decision"], "INVALID_EVIDENCE")

    def test_missing_or_mismatched_evidence_fails_closed(self):
        profile = E.make_profile(0)
        evidence = E.make_evidence(profile, 1, 0)
        wrong_cal = {**evidence, "calibration_id": "CAL-WRONG"}
        wrong_obs = {**evidence, "observable_id": "OBS-WRONG"}
        no_provenance = {**evidence, "provenance_refs": []}
        wrong_fp = {**evidence, "profile_fingerprint": "0" * 64}
        for candidate in (wrong_cal, wrong_obs, no_provenance, wrong_fp):
            with self.subTest(candidate=candidate):
                self.assertEqual(E.evaluate(profile, candidate)["decision"], "INVALID_EVIDENCE")

    def test_missing_uncertainty_is_not_zero_uncertainty(self):
        profile = E.make_profile(0)
        evidence = E.make_evidence(profile, 1, 0)
        del evidence["uncertainty_radius"]
        self.assertEqual(E.evaluate(profile, evidence)["decision"], "INVALID_EVIDENCE")
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            E.make_evidence(profile, 1, Fraction(-1, 2))

    def test_profile_fingerprint_binds_rejection_threshold(self):
        profile0 = E.make_profile(0)
        profile1 = E.make_profile(1)
        self.assertNotEqual(E.profile_fingerprint(profile0), E.profile_fingerprint(profile1))
        evidence0 = E.make_evidence(profile0, Fraction(1, 2), 0)
        evidence1 = E.make_evidence(profile1, Fraction(1, 2), 0)
        self.assertEqual(E.evaluate(profile0, evidence0)["decision"], "REJECTED_IN_SCOPE")
        self.assertEqual(E.evaluate(profile1, evidence1)["decision"], "NOT_REJECTED_IN_SCOPE")
        self.assertEqual(E.evaluate(profile1, evidence0)["decision"], "INVALID_EVIDENCE")

    def test_profile_fingerprint_normalizes_equivalent_exact_numbers(self):
        fraction_profile = E.make_profile(Fraction(0))
        integer_profile = deepcopy(fraction_profile)
        integer_profile["prediction"]["upper_bound"] = 0
        integer_profile["null_model"]["value"] = 0
        integer_profile["rejection_rule"]["threshold"] = 0
        self.assertEqual(E.profile_fingerprint(fraction_profile), E.profile_fingerprint(integer_profile))
        evidence = E.make_evidence(fraction_profile, 1, 0)
        self.assertEqual(E.evaluate(integer_profile, evidence)["decision"], "REJECTED_IN_SCOPE")

    def test_profile_semantics_are_exact_bound(self):
        profile = E.make_profile(0)
        cases = (
            ("prediction", "kind", "lower-bound", "prediction kind"),
            ("null_model", "kind", "point-alternative", "null-model kind"),
            ("rejection_rule", "kind", "interval-entirely-below-threshold", "rejection-rule kind"),
        )
        for field, key, value, diagnostic in cases:
            with self.subTest(field=field):
                mutated = deepcopy(profile)
                mutated[field][key] = value
                with self.assertRaisesRegex(ValueError, diagnostic):
                    E.profile_fingerprint(mutated)
                with self.assertRaisesRegex(ValueError, diagnostic):
                    E.evaluate(mutated, {})
        mutated = deepcopy(profile)
        mutated["uncertainty_model"] = "undeclared-model"
        with self.assertRaisesRegex(ValueError, "uncertainty-model"):
            E.profile_fingerprint(mutated)
        mutated = deepcopy(profile)
        mutated["decision_policy"]["reject"] = "interval upper bound > threshold"
        with self.assertRaisesRegex(ValueError, "decision policy semantic drift"):
            E.profile_fingerprint(mutated)

    def test_profile_identifiers_and_scope_are_exact_bound(self):
        profile = E.make_profile(0)
        for key, value, diagnostic in (
            ("hypothesis_id", "H-OTHER", "hypothesis_id drift"),
            ("hypothesis_version", "2.0.0", "hypothesis_version drift"),
            ("scope", "global UFT-ID theory refutation", "scope drift"),
            ("profile_version", "2.0.0", "profile_version drift"),
        ):
            with self.subTest(key=key):
                mutated = deepcopy(profile)
                mutated[key] = value
                with self.assertRaisesRegex(ValueError, diagnostic):
                    E.profile_fingerprint(mutated)
        for key in ("measurement_spec_id", "calibration_id"):
            with self.subTest(whitespace_profile_key=key):
                mutated = deepcopy(profile)
                mutated[key] = "   "
                with self.assertRaisesRegex(ValueError, "nonempty string"):
                    E.profile_fingerprint(mutated)
            evidence = E.make_evidence(profile, 1, 0)
            evidence[key] = "   "
            self.assertEqual(E.evaluate(profile, evidence)["decision"], "INVALID_EVIDENCE")
        for bad_profile_id in ("", "   "):
            with self.subTest(bad_profile_id=repr(bad_profile_id)):
                with self.assertRaisesRegex(ValueError, "nonempty string"):
                    E.make_profile(0, profile_id=bad_profile_id)
        with self.assertRaisesRegex(ValueError, "profile_id drift"):
            E.make_profile(0, profile_id="EFP-SYN-UNREGISTERED")

    def test_base_falsification_projection_and_authority_are_exact_bound(self):
        profile = E.make_profile(0)
        base = json.loads((ROOT / "machine/falsification_contract.json").read_text(encoding="utf-8"))
        projection = E.base_falsification_spec(profile)
        expected_projection = {
            "hypothesis_id": profile["hypothesis_id"],
            "claim_class": profile["claim_class"],
            "independent_variables": [],
            "perturbations": [],
            "observables": [profile["observable_id"]],
            "predictions": [profile["prediction"]],
            "null_model": profile["null_model"],
            "rejection_conditions": [profile["rejection_rule"]],
            "evidence_required": profile["evidence_requirements"],
            "scope_limits": [profile["scope"], "synthetic conformance only", "no empirical-rejection licence"],
            "status": "synthetic-conformance",
        }
        self.assertEqual(projection, expected_projection)
        self.assertEqual(tuple(projection), tuple(base["required_fields"]))
        self.assertEqual(set(E.BASE_FALSIFICATION_FIELD_MAPPING), set(base["required_fields"]))
        for mutate in (
            lambda payload: payload.__setitem__("schema_version", "9.9.9"),
            lambda payload: payload.__setitem__("required_fields", []),
            lambda payload: payload.__setitem__("semantics", {"prediction": "rewritten"}),
        ):
            result = self._mutate_json("machine/falsification_contract.json", mutate)
            self.assertEqual(result["status"], "error")
            self.assertIn("EFP PR8 falsification base authority drift", result["errors"])

    def test_validator_rejects_complete_base_projection_drift(self):
        original_loader = V.load_module
        canonical = E.run_suite()

        class FakeExperiment:
            BASE_FALSIFICATION_FIELD_MAPPING = E.BASE_FALSIFICATION_FIELD_MAPPING
            make_profile = staticmethod(E.make_profile)

            @staticmethod
            def base_falsification_spec(profile):
                projection = E.base_falsification_spec(profile)
                projection["scope_limits"] = [profile["scope"], "synthetic conformance only"]
                return projection

            @staticmethod
            def run_suite():
                return deepcopy(canonical)

        try:
            V.load_module = lambda name, path: FakeExperiment if path.resolve() == V.PATHS["experiment"].resolve() else original_loader(name, path)
            result = V.validate()
        finally:
            V.load_module = original_loader
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP runtime base projection drift", result["errors"])

    def test_string_and_bytes_provenance_are_rejected_before_list_coercion(self):
        profile = E.make_profile(0)
        for refs in ("SYN-PROV-001", b"SYN-PROV-001"):
            with self.subTest(refs_type=type(refs).__name__):
                with self.assertRaisesRegex(ValueError, "nonempty string sequence"):
                    E.make_evidence(profile, 1, 0, provenance_refs=refs)
        with self.assertRaisesRegex(ValueError, "nonempty string sequence"):
            E.make_evidence(profile, 1, 0, provenance_refs=["   "])
        evidence = E.make_evidence(profile, 1, 0)
        evidence["provenance_refs"] = "SYN-PROV-001"
        self.assertEqual(E.evaluate(profile, evidence)["decision"], "INVALID_EVIDENCE")
        whitespace_evidence = E.make_evidence(profile, 1, 0)
        whitespace_evidence["provenance_refs"] = ["   "]
        self.assertEqual(E.evaluate(profile, whitespace_evidence)["decision"], "INVALID_EVIDENCE")

    def test_prior_registration_is_explicitly_external_and_unverified(self):
        profile = E.make_profile(0)
        self.assertEqual(profile["prior_registration_status"], "EXTERNAL_UNVERIFIED_ASSUMPTION")
        rejected = E.evaluate(profile, E.make_evidence(profile, 1, 0))
        self.assertEqual(rejected["decision"], "REJECTED_IN_SCOPE")
        self.assertFalse(rejected["prior_registration_verified"])
        self.assertFalse(rejected["empirical_rejection_licensed"])
        self.assertEqual(rejected["decision_authority"], "SYNTHETIC_CONFORMANCE_ONLY")
        mutated = deepcopy(profile)
        mutated["prior_registration_status"] = "VERIFIED_BY_PROFILE_FINGERPRINT"
        with self.assertRaisesRegex(ValueError, "external unverified assumption"):
            E.profile_fingerprint(mutated)

    def test_empirical_fit_can_be_nonunique(self):
        models = {"A": (-2, 0), "B": (-1, 1), "C": (0, 2)}
        self.assertEqual(E.compatible_models(0, models), ["A", "B", "C"])
        self.assertEqual(E.compatible_models(-2, models), ["A"])

    def test_counterexample_payloads_are_exact(self):
        self.assertEqual(self.suite["fixtures"], V.EXPECTED_FIXTURE_PAYLOADS)
        self.assertEqual(self.suite["claim_boundary"], V.EXPECTED_RESULT_BOUNDARY)

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 11)
        self.assertEqual(result["boundary_count"], 12)

    def _mutate_json(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            mutate(payload)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def _mutate_text(self, relpath: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            mutated = mutate(original)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_undeclared_contract_field_fails_closed(self):
        result = self._mutate_json("machine/empirical_falsification_profile_contract.json", lambda payload: payload.__setitem__("empirically_validated", True))
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP contract top-level field set drift", result["errors"])

    def test_undeclared_result_field_fails_closed(self):
        def mutate(payload):
            payload["records"][0]["empirically_validated"] = True
        result = self._mutate_json("machine/empirical_falsification_profile_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-EFP-001 theorem field set drift", result["errors"])

    def test_proof_reference_must_match_the_exact_human_anchor(self):
        def mutate(payload):
            record = next(item for item in payload["records"] if item["id"] == "UFT-EFP-001")
            record["proof_reference"] = "theory/EMPIRICAL_FALSIFICATION_PROFILE.md#uft-efp-does-not-exist"
        result = self._mutate_json("machine/empirical_falsification_profile_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-EFP-001 proof reference drift", result["errors"])

    def test_csp_base_authority_is_validated_as_complete_contract(self):
        def mutate(payload):
            payload["hard_boundaries"] = ["BROKEN-CSP-BOUNDARY"]
        result = self._mutate_json("machine/continuum_stochastic_prevalence_contract.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP CSP base authority validation failed", result["errors"])

    def test_efp_workflow_command_chain_is_exact_bound(self):
        attacks = (
            ("run: python scripts/validate_empirical_falsification_profile.py", "run: python -c 'print(1)'", "validation"),
            ("python experiments/run_empirical_falsification_profile.py --hash-only > /tmp/empirical-falsification-profile-receipt.json", "python -c 'print(2)' > /tmp/empirical-falsification-profile-receipt.json", "witness_receipt"),
            ("python experiments/run_empirical_falsification_profile.py --json > artifacts/empirical-falsification-profile-receipt.json 2> artifacts/empirical-falsification-profile-receipt.stderr.txt || true", "python -c 'print(3)' > artifacts/empirical-falsification-profile-receipt.json || true", "evidence_bundle"),
            ("run: python scripts/verify_empirical_falsification_profile_artifacts.py artifacts", "run: python -c 'print(4)'", "retained_verification"),
        )
        for old, new, label in attacks:
            with self.subTest(label=label):
                result = self._mutate_text(
                    ".github/workflows/finite-adversarial.yml",
                    lambda text, old=old, new=new: text.replace(old, new, 1),
                )
                self.assertEqual(result["status"], "error")
                self.assertIn(f"EFP workflow {label} command-chain drift", result["errors"])

    def test_future_snapshot_dates_fail_closed(self):
        result = self._mutate_json(
            "machine/empirical_falsification_profile_contract.json",
            lambda payload: payload.__setitem__("snapshot_date", "2999-01-01"),
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("future UTC snapshot" in error for error in result["errors"]), result["errors"])

    def test_snapshot_dates_must_remain_synchronized_with_the_merged_csp_basis(self):
        result = self._mutate_json(
            "machine/empirical_falsification_profile_results.json",
            lambda payload: payload.__setitem__("snapshot_date", "2026-08-23"),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP contract/result/roadmap snapshot disagreement", result["errors"])

    def test_roadmap_cannot_reactivate_csp(self):
        result = self._mutate_json("machine/roadmap_state.json", lambda payload: payload.__setitem__("active_planned_surface", 17))
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP roadmap active surface must be PR #18", result["errors"])

    def test_validator_rejects_experiment_fixture_goalpost_drift(self):
        original_loader = V.load_module
        canonical = E.run_suite()

        class FakeExperiment:
            @staticmethod
            def run_suite():
                mutated = deepcopy(canonical)
                mutated["fixtures"]["CX-EFP-004"]["confirmation_promoted"] = True
                return mutated

        try:
            V.load_module = lambda name, path: FakeExperiment if path.resolve() == V.PATHS["experiment"].resolve() else original_loader(name, path)
            result = V.validate()
        finally:
            V.load_module = original_loader
        self.assertEqual(result["status"], "error")
        self.assertIn("EFP witness counterexample payload drift", result["errors"])


if __name__ == "__main__":
    unittest.main()
