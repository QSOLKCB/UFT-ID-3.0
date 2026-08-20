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
        self.assertEqual(check["scc_partition_checks"], 530)
        self.assertEqual(check["sink_scc_checks"], 530)
        self.assertEqual(check["condensation_checks"], 530)

    def test_tetrahedron_one_skeleton_is_k4(self):
        fixture = GRAPH.tetrahedron_k4_fixture()
        self.assertEqual(len(fixture["vertices"]), 4)
        self.assertEqual(fixture["edge_semantics"], "undirected")
        self.assertEqual(fixture["edge_count"], 6)
        self.assertEqual(set(fixture["degrees"].values()), {3})
        self.assertIn("!= SIS4_CHEMICAL_BOND_GRAPH", fixture["boundary"])

    def test_rich_projection_is_noninjective(self):
        witness = GRAPH.rich_projection_counterexample()
        self.assertEqual(witness["rich_a_arc_count"], 2)
        self.assertEqual(witness["rich_b_arc_count"], 1)
        self.assertTrue(witness["distinct_sources_same_projection"])

    def test_duplicate_rich_arc_ids_fail_closed(self):
        arcs = (
            {"id": "dup", "source": "u", "target": "v", "label": "L1"},
            {"id": "dup", "source": "u", "target": "v", "label": "L2"},
        )
        with self.assertRaisesRegex(ValueError, "ids must be unique"):
            GRAPH.simplify_rich_arcs(("u", "v"), arcs)

    def test_module_inventory_does_not_determine_incidence(self):
        witness = GRAPH.module_inventory_counterexample()
        self.assertEqual(witness["modules"], ["a", "b", "c"])
        self.assertTrue(witness["same_inventory_distinct_incidence"])
        self.assertNotEqual(witness["chain_incidence"], witness["triangle_incidence"])

    def test_drawing_is_not_graph_identity_and_fixture_is_undirected_k13(self):
        witness = GRAPH.drawing_counterexample()
        self.assertTrue(witness["same_graph_distinct_coordinates"])
        self.assertNotEqual(witness["drawing_a"], witness["drawing_b"])
        self.assertEqual(witness["graph"], "K1,3")
        self.assertEqual(witness["edge_semantics"], "undirected")
        self.assertEqual(len(witness["undirected_edges"]), 3)

    def test_coupling_and_placement_graphs_are_explicitly_undirected(self):
        witness = GRAPH.coupling_vs_placement_fixture()
        self.assertEqual(witness["edge_semantics"], "undirected")
        self.assertEqual(witness["coupling_graph"], "K1,3")
        self.assertEqual(witness["placement_graph"], "K4")
        self.assertEqual(len(witness["coupling_undirected_edges"]), 3)
        self.assertEqual(len(witness["placement_undirected_edges"]), 6)
        self.assertNotEqual(witness["coupling_undirected_edges"], witness["placement_undirected_edges"])

    def test_sink_scc_can_exist_without_normal_vertex(self):
        states = ("a", "b")
        edges = (("a", "b"), ("b", "a"))
        self.assertEqual(GRAPH.sink_components(states, edges), (frozenset({"a", "b"}),))
        self.assertEqual(GRAPH.outdegree(states, edges, "a"), 1)
        self.assertEqual(GRAPH.outdegree(states, edges, "b"), 1)

    def test_scc_partition_is_checked_against_mutual_reachability(self):
        states = ("a", "b")
        edges = (("a", "b"),)
        correct = GRAPH.strongly_connected_components(states, edges)
        bogus = (frozenset({"a", "b"}),)
        self.assertTrue(GRAPH.scc_partition_matches_mutual_reachability(states, edges, correct))
        self.assertFalse(GRAPH.scc_partition_matches_mutual_reachability(states, edges, bogus))
        self.assertEqual(correct, (frozenset({"a"}), frozenset({"b"})))

    def test_scc_helpers_are_recursion_safe_on_long_chain(self):
        size = 1500
        states = tuple(str(i) for i in range(size))
        edges = tuple((str(i), str(i + 1)) for i in range(size - 1))
        components = GRAPH.strongly_connected_components(states, edges)
        self.assertEqual(len(components), size)
        self.assertEqual(GRAPH.sink_components(states, edges), (frozenset({str(size - 1)}),))
        self.assertTrue(GRAPH.condensation_is_acyclic(states, edges))

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

    def _mutate_and_validate(self, relpath: str, transform, *, rebind_digest: str | None = None, rebind_blob: str | None = None):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        old_digest = VALIDATOR.EXPECTED_SHA256.get(rebind_digest) if rebind_digest else None
        old_blob = VALIDATOR.EXPECTED_HUMAN_BLOBS.get(rebind_blob) if rebind_blob else None
        try:
            mutated = transform(original)
            path.write_text(mutated, encoding="utf-8")
            if rebind_digest is not None:
                VALIDATOR.EXPECTED_SHA256[rebind_digest] = VALIDATOR.sha256_bytes(mutated.encode("utf-8"))
            if rebind_blob is not None:
                VALIDATOR.EXPECTED_HUMAN_BLOBS[rebind_blob] = VALIDATOR.git_blob_sha(mutated.encode("utf-8"))
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")
            if rebind_digest is not None and old_digest is not None:
                VALIDATOR.EXPECTED_SHA256[rebind_digest] = old_digest
            if rebind_blob is not None and old_blob is not None:
                VALIDATOR.EXPECTED_HUMAN_BLOBS[rebind_blob] = old_blob

    def assert_dedicated_error(self, result, fragment: str):
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_contract_semantic_promotion_guard_is_independent_of_digest(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_contract.json",
            lambda text: text.replace("No physical ontology is inferred", "This proves a universal physical ontology; No physical ontology is inferred", 1),
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "forbidden semantic/ontology promotion")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_result_semantic_promotion_guard_is_independent_of_digest(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_results.json",
            lambda text: text.replace("In G_step, Normal_stepRel(x) iff outdegree(x)=0.", "Every sink SCC is a physical fixed point.", 1),
            rebind_digest="results",
        )
        self.assert_dedicated_error(result, "forbidden semantic/ontology promotion")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def test_human_additive_physical_claim_guard_is_independent_of_digest(self):
        result = self._mutate_and_validate(
            "theory/GRAPH_REALIZATION.md",
            lambda text: text + "\nSiS2 proves E8 information physics.\n",
            rebind_digest="human",
        )
        self.assert_dedicated_error(result, "forbidden semantic/ontology promotion")
        self.assertNotIn("human canonical payload drift", result["errors"])

    def test_private_mail_guard_is_independent_of_digest(self):
        result = self._mutate_and_validate(
            "research/GRAPH_REALIZATION_SOURCES.md",
            lambda text: text + "\nmail.google.com private correspondence\n",
            rebind_digest="sources",
        )
        self.assert_dedicated_error(result, "private locator")
        self.assertNotIn("sources canonical payload drift", result["errors"])

    def test_source_doi_guard_is_independent_of_digest(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_contract.json",
            lambda text: text.replace("10.1021/ic501825r", "10.0000/not-real", 1),
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "Evers SiS2 source identity drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_paraphrased_pettini_ontology_promotion_is_rejected_by_closed_roadmap_blob(self):
        result = self._mutate_and_validate("ROADMAP.md", lambda text: text + "\nThe source model establishes extra-time reality as a physical fact.\n")
        self.assert_dedicated_error(result, "roadmap canonical human authority blob drift")

    def test_all_central_human_authorities_are_frozen(self):
        cases = (
            ("docs/CLAIMS.md", "claims"),
            ("docs/NONCLAIMS.md", "nonclaims"),
            ("README4AI.md", "readme4ai"),
            ("docs/REPRODUCIBILITY.md", "reproducibility"),
            ("ROADMAP.md", "roadmap"),
        )
        for relpath, key in cases:
            with self.subTest(relpath=relpath):
                result = self._mutate_and_validate(relpath, lambda text: text + "\nadditive drift\n")
                self.assert_dedicated_error(result, f"{key} canonical human authority blob drift")

    def test_pettini_roadmap_promotion_is_rejected(self):
        result = self._mutate_and_validate(
            "ROADMAP.md",
            lambda text: text.replace("ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR", "CURRENT GRAPH THEOREM AUTHORITY", 1),
            rebind_blob="roadmap",
        )
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("Pettini" in error for error in result["errors"]), result["errors"])
        self.assertNotIn("roadmap canonical human authority blob drift", result["errors"])

    def test_pettini_exact_arxiv_version_is_bound_to_primary_citation(self):
        def mutate(text: str) -> str:
            changed = text.replace("arXiv:2606.12457v2 (2026).", "arXiv:2606.12457v1 (2026).", 1)
            return changed + "\nUnrelated provenance note: arXiv:2606.12457v2\n"
        result = self._mutate_and_validate("ROADMAP.md", mutate, rebind_blob="roadmap")
        self.assert_dedicated_error(result, "Pettini primary citation/version drift")
        self.assertNotIn("roadmap canonical human authority blob drift", result["errors"])

    def test_commented_graph_artifact_commands_are_not_executable(self):
        def mutate(text: str) -> str:
            for command in VALIDATOR.GRAPH_ARTIFACT_COMMANDS:
                text = text.replace(f"          {command}", f"          # {command}", 1)
            return text
        result = self._mutate_and_validate(".github/workflows/finite-adversarial.yml", mutate)
        self.assert_dedicated_error(result, "finite-adversarial graph artifact retention missing executable command")

    def test_nonclaims_is_ci_triggered_and_receipt_bound(self):
        workflow = (ROOT / ".github/workflows/finite-adversarial.yml").read_text(encoding="utf-8")
        self.assertEqual(sum(1 for line in workflow.splitlines() if line.strip() == '- "docs/NONCLAIMS.md"'), 2)
        self.assertIn("docs/NONCLAIMS.md", RECEIPT.receipt_files())

    def test_graph_commands_are_required_in_roadmap_gate(self):
        result = self._mutate_and_validate(
            "ROADMAP.md",
            lambda text: text.replace("python experiments/run_graph_realization.py --json", "python experiments/run_graph_realization_REMOVED.py --json", 1),
            rebind_blob="roadmap",
        )
        self.assert_dedicated_error(result, "ROADMAP graph validation gate")

    def test_receipt_schema_version_is_derived_from_registry(self):
        self.assertEqual(RECEIPT.registered_receipt_version(), "1.0.0")
        self.assertEqual(RECEIPT.run_suite()["schema_version"], "1.0.0")
        source = (ROOT / "experiments/run_graph_realization.py").read_text(encoding="utf-8")
        self.assertIn(VALIDATOR.RECEIPT_SCHEMA_BINDING, source)

    def test_receipt_binds_graph_relation_and_central_human_surfaces(self):
        files = set(RECEIPT.receipt_files())
        for expected in (
            "machine/contract.json", "machine/relation_contract.json", "machine/graph_realization_contract.json",
            "machine/graph_realization_results.json", "research/GRAPH_REALIZATION_SOURCES.md", "theory/GRAPH_REALIZATION.md",
            "experiments/relation/run.py", "experiments/graph_realization/run.py", "docs/CLAIMS.md", "docs/NONCLAIMS.md",
            "README4AI.md", "docs/REPRODUCIBILITY.md", "ROADMAP.md", ".github/workflows/finite-adversarial.yml",
        ):
            self.assertIn(expected, files)

    def test_receipt_is_deterministic(self):
        first = RECEIPT.run_suite()
        second = RECEIPT.run_suite()
        self.assertEqual(first["suite_fingerprint_sha256"], second["suite_fingerprint_sha256"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])


if __name__ == "__main__":
    unittest.main()
