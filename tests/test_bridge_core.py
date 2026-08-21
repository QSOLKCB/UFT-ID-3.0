from __future__ import annotations

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


BRIDGE = load_module("bridge_core_experiment", "experiments/bridge_core/run.py")
VALIDATOR = load_module("bridge_core_validator", "scripts/validate_bridge_core.py")


class BridgeCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = BRIDGE.run_suite()

    def test_bounded_counts(self):
        assoc = self.result["bounded_checks"]["relation_associativity"]
        self.assertEqual(assoc["labelled_relations_fin2"], 16)
        self.assertEqual(assoc["ordered_relation_triples_checked"], 4096)
        loss = self.result["bounded_checks"]["preservation_loss"]
        self.assertEqual(loss["structure_labels"], 3)
        self.assertEqual(loss["valid_partial_structure_declarations"], 27)
        self.assertEqual(loss["ordered_structure_declaration_pairs_checked"], 729)
        self.assertEqual(loss["ordered_preservation_pairs_checked"], 729)

    def test_counterexample_same_endpoint_types(self):
        fixture = self.result["fixtures"]["CX-BR-001"]
        self.assertTrue(fixture["same_endpoint_types"])
        self.assertTrue(fixture["relations_differ"])
        self.assertTrue(fixture["loss_sets_differ"])

    def test_version_mismatch_is_exactly_classified(self):
        self.assertEqual(self.result["fixtures"]["CX-BR-002"]["errors"], ["intermediate-version-mismatch"])

    def test_scope_mismatch_is_exactly_classified(self):
        self.assertEqual(self.result["fixtures"]["CX-BR-003"]["errors"], ["scope-intersection-empty"])

    def test_lossy_decoder_does_not_reconstruct(self):
        fixture = self.result["fixtures"]["CX-BR-004"]
        self.assertFalse(fixture["exact_reconstruction"])
        self.assertIn("second_bit", fixture["composite"]["lost_structure"])
        self.assertIn("full_state_identity", fixture["composite"]["lost_structure"])

    def test_identity_neutrality_requires_complete_structure_tracking(self):
        fixture = self.result["fixtures"]["UFT-BR-004"]
        self.assertTrue(fixture["left_identity_neutral"])
        self.assertTrue(fixture["right_identity_neutral"])
        self.assertTrue(fixture["complete_structure_tracking_required"])
        self.assertEqual(fixture["partial_metadata_negative_control"]["lost_structure"], ["b"])

    def test_empty_domain_is_valid(self):
        fixture = self.result["fixtures"]["EMPTY-DOMAIN"]
        self.assertEqual(fixture["domain"], [])
        self.assertEqual(fixture["relation"], [])
        bridge = BRIDGE.make_bridge(
            bridge_id="empty", source_type="A", target_type="B", source_version="1", target_version="1",
            source_states=("a",), target_states=("b",), domain=(), relation=(), relation_kind="map",
            preserved_structure=(), lost_structure=(), scope=("s",),
        )
        self.assertEqual(bridge["domain"], frozenset())

    def test_domain_coverage_is_required(self):
        first = BRIDGE.make_bridge(
            bridge_id="first", source_type="A", target_type="B", source_version="1", target_version="1",
            source_states=("a",), target_states=("b0", "b1"), domain=("a",), relation=(("a", "b1"),),
            relation_kind="map", preserved_structure=("x",), lost_structure=(), scope=("s",),
        )
        second = BRIDGE.make_bridge(
            bridge_id="second", source_type="B", target_type="C", source_version="1", target_version="1",
            source_states=("b0", "b1"), target_states=("c",), domain=("b0",), relation=(("b0", "c"),),
            relation_kind="map", preserved_structure=("x",), lost_structure=(), scope=("s",),
        )
        self.assertEqual(BRIDGE.composability_errors(first, second), ("intermediate-image-outside-second-domain",))
        with self.assertRaises(ValueError):
            BRIDGE.compose(first, second)

    def test_map_must_be_total_and_right_unique_on_nonempty_domain(self):
        with self.assertRaises(ValueError):
            BRIDGE.make_bridge(
                bridge_id="bad-map", source_type="A", target_type="B", source_version="1", target_version="1",
                source_states=("a0", "a1"), target_states=("b",), domain=("a0", "a1"),
                relation=(("a0", "b"),), relation_kind="map", preserved_structure=(), lost_structure=(), scope=("s",),
            )

    def test_preserved_and_lost_must_be_disjoint(self):
        with self.assertRaises(ValueError):
            BRIDGE.make_bridge(
                bridge_id="bad-structure", source_type="A", target_type="B", source_version="1", target_version="1",
                source_states=("a",), target_states=("b",), domain=("a",), relation=(("a", "b"),),
                relation_kind="map", preserved_structure=("x",), lost_structure=("x",), scope=("s",),
            )

    def test_validator_is_green(self):
        result = VALIDATOR.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 9)
        self.assertEqual(result["boundary_count"], 10)

    def _mutate_json_with_blob_rebind(self, relpath: str, blob_key: str, mutate):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        old_blob = VALIDATOR.EXPECTED_BLOBS.get(blob_key)
        try:
            payload = json.loads(original)
            mutate(payload)
            mutated = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            path.write_text(mutated, encoding="utf-8")
            if old_blob is not None:
                VALIDATOR.EXPECTED_BLOBS[blob_key] = VALIDATOR.git_blob_sha(mutated.encode("utf-8"))
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")
            if old_blob is not None:
                VALIDATOR.EXPECTED_BLOBS[blob_key] = old_blob

    def test_contract_scope_cannot_promote_bridge_to_physics(self):
        result = self._mutate_json_with_blob_rebind(
            "machine/bridge_core_contract.json", "contract",
            lambda payload: payload.__setitem__("scope", "BridgeCore is the empirically confirmed physical transport substrate of UFT-ID."),
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("forbidden promotion" in e or "scope" in e for e in result["errors"]), result["errors"])

    def test_theorem_statement_is_semantically_bound_after_blob_rebind(self):
        def mutate(payload):
            record = next(x for x in payload["records"] if x["id"] == "UFT-BR-003")
            record["statement"] = "Ordinary composition restores every structure lost by B1."
        result = self._mutate_json_with_blob_rebind("machine/bridge_core_results.json", "results", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-BR-003 statement drift", result["errors"])

    def test_theorem_hypotheses_are_bound_after_blob_rebind(self):
        def mutate(payload):
            record = next(x for x in payload["records"] if x["id"] == "UFT-BR-002")
            record["hypotheses"] = ["B1 and B2 are composable BridgeCore bridges"]
        result = self._mutate_json_with_blob_rebind("machine/bridge_core_results.json", "results", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-BR-002 hypotheses drift", result["errors"])

    def test_identity_theorem_cannot_drop_completeness_hypothesis(self):
        def mutate(payload):
            record = next(x for x in payload["records"] if x["id"] == "UFT-BR-004")
            record["hypotheses"] = ["identity bridge and B satisfy ordinary composition compatibility"]
        result = self._mutate_json_with_blob_rebind("machine/bridge_core_results.json", "results", mutate)
        self.assertEqual(result["status"], "error")
        self.assertIn("UFT-BR-004 hypotheses drift", result["errors"])

    def test_roadmap_cannot_reactivate_pr11(self):
        path = ROOT / "machine/roadmap_state.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["active_planned_surface"] = 11
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = VALIDATOR.validate()
            self.assertEqual(result["status"], "error")
            self.assertIn("roadmap active surface must be PR #12", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
