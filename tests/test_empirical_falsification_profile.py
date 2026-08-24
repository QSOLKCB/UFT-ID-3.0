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

    def test_empirical_fit_can_be_nonunique(self):
        models = {"A": (-2, 0), "B": (-1, 1), "C": (0, 2)}
        self.assertEqual(E.compatible_models(0, models), ["A", "B", "C"])
        self.assertEqual(E.compatible_models(-2, models), ["A"])

    def test_counterexample_payloads_are_exact(self):
        self.assertEqual(self.suite["fixtures"], V.EXPECTED_FIXTURE_PAYLOADS)

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 11)
        self.assertEqual(result["boundary_count"], 11)

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
