from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
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


I = load_module("information_comparability_experiment", "experiments/information_comparability/run.py")
V = load_module("information_comparability_validator", "scripts/validate_information_comparability.py")


class InformationComparabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = I.run_suite()

    def test_comparability_battery_counts(self):
        self.assertEqual(
            self.suite["bounded_checks"]["comparability"],
            {
                "information_spec_count": 96,
                "ordered_spec_pair_count": 9216,
                "directly_comparable_ordered_pairs": 224,
                "unit_convertible_ordered_pairs": 224,
                "reflexive_checks": 96,
                "symmetry_checks": 9216,
                "inverse_conversion_checks": 224,
            },
        )

    def test_positive_scale_log_base_and_shared_shannon_counts(self):
        self.assertEqual(self.suite["bounded_checks"]["positive_scale"], {"positive_scale_order_checks": 75})
        self.assertEqual(self.suite["bounded_checks"]["log_base_conversion"], {"log_base_conversion_checks": 5})
        self.assertEqual(self.suite["bounded_checks"]["shared_shannon_primitive"], {"shared_shannon_primitive_checks": 1})

    def test_shared_shannon_battery_calls_canonical_primitive(self):
        original = I.shannon_entropy
        try:
            I.shannon_entropy = lambda *args, **kwargs: 0.0
            with self.assertRaisesRegex(RuntimeError, "canonical Shannon primitive"):
                I.shared_shannon_primitive_battery()
        finally:
            I.shannon_entropy = original

    def test_identical_specs_are_directly_comparable(self):
        spec = I.fixture_spec(scope=frozenset({"alpha"}))
        self.assertTrue(I.directly_comparable(spec, spec))

    def test_direct_comparability_is_symmetric(self):
        a = I.fixture_spec(scope=frozenset({"alpha"}))
        b = I.fixture_spec(scope=frozenset({"alpha", "beta"}))
        self.assertTrue(I.directly_comparable(a, b))
        self.assertEqual(I.directly_comparable(a, b), I.directly_comparable(b, a))

    def test_observation_refs_bind_concrete_identity(self):
        a = I.fixture_spec(observation="OBS-REF-FIN2-IDENTITY-V1", scope=frozenset({"alpha"}))
        b = I.fixture_spec(observation="OBS-REF-FIN2-CONSTANT0-V1", scope=frozenset({"alpha"}))
        self.assertNotEqual(a["observation"], b["observation"])
        self.assertNotEqual(
            I.OBSERVATION_REGISTRY[a["observation"]]["map_ref"],
            I.OBSERVATION_REGISTRY[b["observation"]]["map_ref"],
        )
        self.assertFalse(I.directly_comparable(a, b))

    def test_conditioning_refs_bind_variable_and_event_identity(self):
        a = I.fixture_spec(conditioning="COND-REF-UNCONDITIONAL-V1", scope=frozenset({"alpha"}))
        b = I.fixture_spec(conditioning="COND-REF-FIN2-X-EQ-0-V1", scope=frozenset({"alpha"}))
        self.assertNotEqual(a["conditioning"], b["conditioning"])
        self.assertEqual(I.CONDITIONING_REGISTRY[b["conditioning"]]["variable_ref"], "x@Fin2")
        self.assertEqual(I.CONDITIONING_REGISTRY[b["conditioning"]]["event_ref"], "x=0")
        self.assertFalse(I.directly_comparable(a, b))

    def test_same_functional_without_same_observation_is_not_direct(self):
        a = I.fixture_spec(observation="OBS-REF-FIN2-IDENTITY-V1", scope=frozenset({"alpha"}))
        b = I.fixture_spec(observation="OBS-REF-FIN2-CONSTANT0-V1", scope=frozenset({"alpha"}))
        self.assertEqual(a["functional"], b["functional"])
        self.assertFalse(I.directly_comparable(a, b))

    def test_registered_unit_conversion_is_exact_and_positive(self):
        conversion = I.make_unit_conversion(
            functional="shannon_entropy",
            source_unit="bit",
            target_unit="base4-digit",
            scope=frozenset({"alpha"}),
        )
        self.assertEqual(conversion["positive_scale"], Fraction(1, 2))
        self.assertEqual(I.convert_value(Fraction(2, 1), conversion), Fraction(1, 1))
        malformed = dict(conversion)
        malformed["positive_scale"] = Fraction(3, 4)
        with self.assertRaisesRegex(ValueError, "registry-canonical"):
            I.validate_unit_conversion(malformed)

    def test_unit_conversion_requires_three_way_scope_overlap(self):
        a = I.fixture_spec(unit="bit", scope=frozenset({"alpha"}))
        b = I.fixture_spec(unit="base4-digit", scope=frozenset({"alpha"}))
        disjoint_conversion = I.make_unit_conversion(
            functional="shannon_entropy",
            source_unit="bit",
            target_unit="base4-digit",
            scope=frozenset({"beta"}),
        )
        self.assertFalse(I.unit_convertibly_comparable(a, b, disjoint_conversion))

    def test_unit_conversion_does_not_bridge_other_spec_differences(self):
        a = I.fixture_spec(observation="OBS-REF-FIN2-IDENTITY-V1", unit="bit", scope=frozenset({"alpha"}))
        b = I.fixture_spec(observation="OBS-REF-FIN2-CONSTANT0-V1", unit="base4-digit", scope=frozenset({"alpha"}))
        conversion = I.make_unit_conversion(
            functional="shannon_entropy",
            source_unit="bit",
            target_unit="base4-digit",
            scope=frozenset({"alpha"}),
        )
        self.assertFalse(I.unit_convertibly_comparable(a, b, conversion))

    def test_scope_relative_direct_comparability_is_not_transitive(self):
        fixture = self.suite["fixtures"]["CX-INF-004"]
        self.assertTrue(fixture["A_comparable_B"])
        self.assertTrue(fixture["B_comparable_C"])
        self.assertFalse(fixture["A_comparable_C"])

    def test_counterexamples_are_derived(self):
        fixtures = self.suite["fixtures"]
        self.assertTrue(fixtures["CX-INF-001"]["numeric_values_equal"])
        self.assertEqual(fixtures["CX-INF-001"]["shared_shannon_primitive_value"], "1")
        self.assertFalse(fixtures["CX-INF-001"]["directly_comparable"])
        self.assertFalse(fixtures["CX-INF-002"]["same_observation"])
        self.assertEqual(fixtures["CX-INF-002"]["left_observation_ref"], "OBS-REF-FIN2-IDENTITY-V1")
        self.assertEqual(fixtures["CX-INF-002"]["right_observation_ref"], "OBS-REF-FIN2-CONSTANT0-V1")
        self.assertFalse(fixtures["CX-INF-002"]["directly_comparable"])
        self.assertFalse(fixtures["CX-INF-003"]["directly_comparable"])
        self.assertTrue(fixtures["CX-INF-003"]["unit_convertibly_comparable"])
        self.assertTrue(fixtures["CX-INF-005"]["numeric_values_equal"])
        self.assertFalse(fixtures["CX-INF-005"]["same_normalization"])
        self.assertFalse(fixtures["CX-INF-005"]["directly_comparable"])

    def test_invalid_specs_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "scope"):
            I.make_spec(
                functional="shannon_entropy",
                observation="OBS-REF-FIN2-IDENTITY-V1",
                unit="bit",
                normalization="none",
                conditioning="COND-REF-UNCONDITIONAL-V1",
                scope=(),
            )
        with self.assertRaisesRegex(ValueError, "not a string"):
            I.fixture_spec(scope="alpha")
        with self.assertRaisesRegex(ValueError, "unsupported information functional"):
            I.make_spec(
                functional="mystery-information",
                observation="OBS-REF-FIN2-IDENTITY-V1",
                unit="bit",
                normalization="none",
                conditioning="COND-REF-UNCONDITIONAL-V1",
                scope=("alpha",),
            )
        with self.assertRaisesRegex(ValueError, "observation contract identity"):
            I.fixture_spec(observation="fine-observation")
        with self.assertRaisesRegex(ValueError, "conditioning model identity"):
            I.fixture_spec(conditioning="conditioned-on-k")

    def test_exact_logarithm_rejects_non_power_of_two(self):
        with self.assertRaisesRegex(ValueError, "power-of-two"):
            I.uniform_log_entropy(3, "bit")

    def test_validator_accepts_canonical_surface(self):
        result = V.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 10)
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

    def _mutate_text(self, relpath: str, transform):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            mutated = transform(original)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            return V.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_duplicate_result_id_fails_closed(self):
        result = self._mutate_json(
            "machine/information_comparability_results.json",
            lambda payload: payload["records"].append(dict(payload["records"][0])),
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("duplicate information result id" in e for e in result["errors"]), result["errors"])

    def test_undeclared_result_field_fails_closed(self):
        def mutate(payload):
            payload["records"][0]["empirically_validated"] = True
        result = self._mutate_json("machine/information_comparability_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-INF-001 theorem field set drift", result["errors"])

    def test_theorem_hypothesis_drift_is_rejected(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-INF-005")
            record["hypotheses"] = []
        result = self._mutate_json("machine/information_comparability_results.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-INF-005 hypotheses drift", result["errors"])

    def test_undeclared_contract_field_fails_closed(self):
        def mutate(payload):
            payload["empirically_validated"] = True
        result = self._mutate_json("machine/information_comparability_contract.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("information contract top-level field set drift", result["errors"])

    def test_observation_registry_drift_is_rejected(self):
        def mutate(payload):
            payload["observation_registry"]["OBS-REF-FIN2-IDENTITY-V1"]["map_ref"] = "O_id(0)=0; O_id(1)=0"
        result = self._mutate_json("machine/information_comparability_contract.json", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("information observation identity registry drift", result["errors"])

    def test_human_statement_drift_is_rejected(self):
        canonical = (
            "**Canonical statement:** `Two Shannon-entropy specifications in bits with different observation "
            "contracts are not directly comparable under the Information Comparability predicate.`"
        )
        result = self._mutate_text(
            "theory/INFORMATION_COMPARABILITY.md",
            lambda text: text.replace(canonical, "**Canonical statement:** `Same unit means same information.`", 1),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("CX-INF-002 human canonical statement drift", result["errors"])

    def test_human_nonclaim_drift_is_rejected(self):
        canonical = (
            '**Canonical nonclaims:** `["A positive scalar conversion changes units only; it does not supply a semantic, epistemic, empirical, or physical bridge."]`'
        )
        result = self._mutate_text(
            "theory/INFORMATION_COMPARABILITY.md",
            lambda text: text.replace(
                canonical,
                '**Canonical nonclaims:** `["A positive scalar conversion licenses semantic and empirical equivalence."]`',
                1,
            ),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-INF-004 human canonical nonclaims drift", result["errors"])

    def test_global_unit_conversion_boundary_drift_is_rejected(self):
        result = self._mutate_text(
            "theory/INFORMATION_COMPARABILITY.md",
            lambda text: text.replace(
                "This mode licenses unit conversion only.",
                "This mode licenses unit conversion and a semantic and empirical bridge.",
                1,
            ),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("human unit-conversion-only boundary drift", result["errors"])

    def test_roadmap_cannot_reactivate_representation_phase(self):
        result = self._mutate_json(
            "machine/roadmap_state.json",
            lambda payload: payload.__setitem__("active_planned_surface", 14),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("information roadmap active surface must be PR #15", result["errors"])


if __name__ == "__main__":
    unittest.main()
