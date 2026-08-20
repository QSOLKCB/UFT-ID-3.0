from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
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


VALIDATOR = load_module("graph_validator_latest6", "scripts/validate_graph_realization.py")
ARTIFACTS = load_module("graph_artifacts_latest6", "scripts/verify_graph_artifacts.py")
GRAPH = load_module("graph_run_latest6", "experiments/graph_realization/run.py")
RECEIPT = load_module("graph_receipt_latest6", "experiments/run_graph_realization.py")


class LatestSixCodexRegressions(unittest.TestCase):
    def assert_dedicated_error(self, result, fragment: str):
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def mutate_json(self, relpath: str, mutate, *, rebind_digest: str):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        old_digest = VALIDATOR.EXPECTED_SHA256[rebind_digest]
        try:
            payload = json.loads(original)
            mutate(payload)
            mutated = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256[rebind_digest] = VALIDATOR.sha256_bytes(mutated.encode("utf-8"))
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256[rebind_digest] = old_digest

    def write_artifacts(self, directory: Path, witness, receipt):
        validation = VALIDATOR.validate()
        self.assertEqual(validation["status"], "ok", validation["errors"])
        (directory / ARTIFACTS.VALIDATION_FILE).write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (directory / ARTIFACTS.WITNESS_FILE).write_text(
            json.dumps(witness, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (directory / ARTIFACTS.RECEIPT_FILE).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def recompute_receipt(self, receipt, witness):
        receipt["result_sha256"] = ARTIFACTS.sha256_bytes(ARTIFACTS.canonical_bytes(witness))
        receipt["suite_fingerprint_sha256"] = ARTIFACTS.sha256_bytes(
            ARTIFACTS.canonical_bytes(ARTIFACTS.fingerprint_identity(receipt))
        )

    def test_retained_receipt_fingerprint_is_recomputed(self):
        witness = GRAPH.run_suite()
        receipt = RECEIPT.run_suite()
        receipt["suite_fingerprint_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            self.write_artifacts(Path(tmp), witness, receipt)
            with self.assertRaisesRegex(RuntimeError, "fingerprint mismatch"):
                ARTIFACTS.verify(Path(tmp))

    def test_retained_witness_requires_complete_bounded_payload(self):
        witness = GRAPH.run_suite()
        witness["bounded_exhaustive_check"] = {"total_relations": 530}
        receipt = RECEIPT.run_suite()
        self.recompute_receipt(receipt, witness)
        with tempfile.TemporaryDirectory() as tmp:
            self.write_artifacts(Path(tmp), witness, receipt)
            with self.assertRaisesRegex(RuntimeError, "bounded-check payload drift"):
                ARTIFACTS.verify(Path(tmp))

    def test_theorem_hypotheses_are_bound(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-GR-002")
            record["hypotheses"] = ["G_step is an arbitrary graph unrelated to stepRel"]

        result = self.mutate_json(
            "machine/graph_realization_results.json", mutate, rebind_digest="results"
        )
        self.assert_dedicated_error(result, "UFT-GR-002 theorem hypotheses drift")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def test_evers_complete_identity_is_bound(self):
        def mutate(payload):
            record = next(s for s in payload["sources"] if s["source_id"] == "EVERS-2015-SIS2")
            record["title"] = "Unrelated material paper"
            record["year"] = 1999
            record["pages"] = "1-2"

        result = self.mutate_json(
            "machine/graph_realization_contract.json", mutate, rebind_digest="contract"
        )
        self.assert_dedicated_error(result, "Evers source title drift")
        self.assert_dedicated_error(result, "Evers source year drift")
        self.assert_dedicated_error(result, "Evers source pages drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_counterexample_payload_is_bound_to_human_witness(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "CX-GR-001")
            record["statement"] = "The rich-to-simple projection is injective."
            record["fixture"] = "single graph"
            record["kills"] = []

        result = self.mutate_json(
            "machine/graph_realization_results.json", mutate, rebind_digest="results"
        )
        self.assert_dedicated_error(result, "CX-GR-001 counterexample statement drift")
        self.assert_dedicated_error(result, "CX-GR-001 counterexample fixture drift")
        self.assert_dedicated_error(result, "CX-GR-001 counterexample kills drift")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def assert_cross_check_detects_corruption(self, attribute: str, replacement, message: str):
        original = getattr(GRAPH, attribute)
        try:
            setattr(GRAPH, attribute, replacement(original))
            with self.assertRaisesRegex(RuntimeError, message):
                GRAPH.exhaustive_cross_checks()
        finally:
            setattr(GRAPH, attribute, original)

    def test_every_advertised_exhaustive_comparison_is_behaviorally_live(self):
        self.assert_cross_check_detects_corruption(
            "adjacency_matrix",
            lambda original: lambda states, edges: [
                [1 - value if i == 0 and j == 0 else value for j, value in enumerate(row)]
                for i, row in enumerate(original(states, edges))
            ],
            "UFT-GR-001 adjacency identity failure",
        )
        self.assert_cross_check_detects_corruption(
            "outdegree",
            lambda original: lambda states, edges, x: original(states, edges, x) + 1,
            "UFT-GR-002 normal/outdegree failure",
        )

        def broken_reach(original):
            def replacement(states, edges):
                result = original(states, edges)
                return {source: frozenset() for source in result}
            return replacement

        self.assert_cross_check_detects_corruption(
            "boolean_reachability", broken_reach, "UFT-GR-003 reachability cross-check failure"
        )
        self.assert_cross_check_detects_corruption(
            "is_dag_kahn",
            lambda original: lambda states, edges: not original(states, edges),
            "UFT-GR-004 termination/DAG failure",
        )
        self.assert_cross_check_detects_corruption(
            "strongly_connected_components",
            lambda original: lambda states, edges: tuple(),
            "UFT-GR-005 SCC partition disagrees with mutual reachability",
        )
        self.assert_cross_check_detects_corruption(
            "sink_components",
            lambda original: lambda states, edges: tuple(),
            "UFT-GR-005 sink SCC disagreement",
        )
        self.assert_cross_check_detects_corruption(
            "condensation",
            lambda original: lambda states, edges: (tuple(), frozenset()),
            "UFT-GR-006 condensation quotient disagreement",
        )


if __name__ == "__main__":
    unittest.main()
