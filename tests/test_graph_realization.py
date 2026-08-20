from __future__ import annotations

import importlib.util
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


GRAPH = load_module("graph_realization_run", "experiments/graph_realization/run.py")
VALIDATOR = load_module("graph_realization_validator", "scripts/validate_graph_realization.py")
RECEIPT = load_module("graph_realization_receipt", "experiments/run_graph_realization.py")


class GraphRealizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = GRAPH.run_suite()

    def test_bounded_surface_is_530_relations(self):
        check = self.suite["bounded_exhaustive_check"]
        self.assertEqual(check["relation_counts"], {"Fin1": 2, "Fin2": 16, "Fin3": 512})
        self.assertEqual(check["total_relations"], 530)
        self.assertEqual(check["adjacency_pair_checks"], 4674)
        self.assertEqual(check["normal_state_checks"], 1570)
        self.assertEqual(check["reachability_source_checks"], 1570)
        self.assertEqual(check["termination_checks"], 530)
        self.assertEqual(check["sink_scc_checks"], 530)
        self.assertEqual(check["condensation_checks"], 530)

    def test_tetrahedron_one_skeleton_is_k4(self):
        fixture = GRAPH.tetrahedron_k4_fixture()
        self.assertEqual(len(fixture["vertices"]), 4)
        self.assertEqual(fixture["edge_count"], 6)
        self.assertEqual(set(fixture["degrees"].values()), {3})
        self.assertIn("!= SIS4_CHEMICAL_BOND_GRAPH", fixture["boundary"])

    def test_rich_projection_is_noninjective(self):
        witness = GRAPH.rich_projection_counterexample()
        self.assertEqual(witness["rich_a_arc_count"], 2)
        self.assertEqual(witness["rich_b_arc_count"], 1)
        self.assertTrue(witness["distinct_sources_same_projection"])

    def test_module_inventory_does_not_determine_incidence(self):
        witness = GRAPH.module_inventory_counterexample()
        self.assertEqual(witness["modules"], ["a", "b", "c"])
        self.assertTrue(witness["same_inventory_distinct_incidence"])
        self.assertNotEqual(witness["chain_incidence"], witness["triangle_incidence"])

    def test_drawing_is_not_graph_identity(self):
        witness = GRAPH.drawing_counterexample()
        self.assertTrue(witness["same_graph_distinct_coordinates"])
        self.assertNotEqual(witness["drawing_a"], witness["drawing_b"])

    def test_coupling_and_placement_graphs_are_separate(self):
        witness = GRAPH.coupling_vs_placement_fixture()
        self.assertEqual(witness["coupling_graph"], "K1,3")
        self.assertEqual(witness["placement_graph"], "K4")
        self.assertNotEqual(witness["coupling_edges"], witness["placement_edges"])

    def test_sink_scc_can_exist_without_normal_vertex(self):
        states = ("a", "b")
        edges = (("a", "b"), ("b", "a"))
        sinks = GRAPH.sink_components(states, edges)
        self.assertEqual(sinks, (frozenset({"a", "b"}),))
        self.assertEqual(GRAPH.outdegree(states, edges, "a"), 1)
        self.assertEqual(GRAPH.outdegree(states, edges, "b"), 1)

    def test_malformed_states_fail_closed(self):
        with self.assertRaises(ValueError):
            GRAPH.adjacency_matrix(("a", []), ())  # type: ignore[arg-type]

    def test_malformed_rich_arc_fails_closed(self):
        with self.assertRaises(ValueError):
            GRAPH.simplify_rich_arcs(("u", "v"), ({"source": "u", "target": "v"},))

    def test_malformed_incidence_fails_closed(self):
        with self.assertRaises(ValueError):
            GRAPH.validate_incidence(("a", "b"), ("edge",), (("a", "wrong", "b"),))

    def test_validator_accepts_canonical_surface(self):
        result = VALIDATOR.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertEqual(result["result_count"], 9)
        self.assertEqual(result["source_count"], 2)

    def _mutate_and_validate(self, relpath: str, transform):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(transform(original), encoding="utf-8")
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")

    def test_contract_semantic_promotion_is_rejected(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_contract.json",
            lambda text: text.replace(
                "No physical ontology is inferred",
                "This proves a universal physical ontology; No physical ontology is inferred",
                1,
            ),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("contract canonical payload drift", result["errors"])

    def test_result_statement_drift_is_rejected(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_results.json",
            lambda text: text.replace(
                "In G_step, Normal_stepRel(x) iff outdegree(x)=0.",
                "Every sink SCC is a physical fixed point.",
                1,
            ),
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("results canonical payload drift", result["errors"])

    def test_human_additive_physical_claim_is_rejected(self):
        result = self._mutate_and_validate(
            "theory/GRAPH_REALIZATION.md",
            lambda text: text + "\nSiS2 proves E8 information physics.\n",
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("human canonical payload drift", result["errors"])

    def test_private_mail_locator_is_rejected(self):
        result = self._mutate_and_validate(
            "research/GRAPH_REALIZATION_SOURCES.md",
            lambda text: text + "\nmail.google.com private correspondence\n",
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("sources canonical payload drift" in error or "private locator" in error for error in result["errors"]))

    def test_source_doi_drift_is_rejected(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_contract.json",
            lambda text: text.replace("10.1021/ic501825r", "10.0000/not-real", 1),
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("contract canonical payload drift" in error or "Evers SiS2 source identity drift" in error for error in result["errors"]))

    def test_receipt_binds_graph_and_relation_sources(self):
        files = set(RECEIPT.receipt_files())
        self.assertIn("research/GRAPH_REALIZATION_SOURCES.md", files)
        self.assertIn("theory/GRAPH_REALIZATION.md", files)
        self.assertIn("machine/graph_realization_contract.json", files)
        self.assertIn("experiments/relation/run.py", files)
        self.assertIn("experiments/graph_realization/run.py", files)

    def test_receipt_is_deterministic(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])


if __name__ == "__main__":
    unittest.main()
