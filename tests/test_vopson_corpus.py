from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts/validate_vopson_corpus.py"
    spec = importlib.util.spec_from_file_location("validate_vopson_corpus", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


class VopsonCorpusValidationTests(unittest.TestCase):
    def setUp(self):
        self.author = json.loads((ROOT / "research/vopson/AUTHOR.json").read_text())
        self.corpus = json.loads((ROOT / "research/vopson/corpus.json").read_text())
        self.graph = json.loads((ROOT / "research/vopson/CLAIM_GRAPH.json").read_text())

    def test_validator_accepts_canonical_corpus(self):
        report = VALIDATOR.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["summary"]["author_orcid"], "0000-0002-8073-5538")
        self.assertGreaterEqual(report["summary"]["works"], 15)

    def test_work_ids_and_primary_dois_are_unique(self):
        works = self.corpus["works"]
        work_ids = [work["work_id"] for work in works]
        primary_dois = [work["doi"] for work in works if work["doi"]]
        self.assertEqual(len(work_ids), len(set(work_ids)))
        self.assertEqual(len(primary_dois), len(set(primary_dois)))

    def test_language_entry_does_not_guess_final_doi(self):
        entry = next(work for work in self.corpus["works"] if work["work_id"] == "VOP-2026-LANGUAGE")
        self.assertIsNone(entry["doi"])
        self.assertIn("10.2139/ssrn.6529851", entry["alternate_identifiers"])
        self.assertTrue(entry["official_metadata_url"])

    def test_polygon_counterexample_has_existing_evidence(self):
        node = next(node for node in self.graph["nodes"] if node["node_id"] == "CL-POLYGON-EXTREMUM")
        self.assertEqual(node["claim_class"], "COUNTEREXAMPLE")
        self.assertTrue(node["evidence_paths"])
        for relative in node["evidence_paths"]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_source_claims_use_one_canonical_class(self):
        allowed = set(self.graph["claim_classes"])
        for node in self.graph["nodes"]:
            self.assertIsInstance(node["claim_class"], str)
            self.assertIn(node["claim_class"], allowed)

    def test_dependency_subgraph_is_acyclic(self):
        node_ids = {node["node_id"] for node in self.graph["nodes"]}
        cycle = VALIDATOR.dependency_cycle(node_ids, self.graph["edges"])
        self.assertIsNone(cycle)


if __name__ == "__main__":
    unittest.main()
