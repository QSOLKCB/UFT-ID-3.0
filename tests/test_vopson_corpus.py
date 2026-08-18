from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_validator(root: Path = ROOT):
    path = root / "scripts/validate_vopson_corpus.py"
    spec = importlib.util.spec_from_file_location(
        f"validate_vopson_corpus_{id(root)}",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


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
        shutil.copytree(
            ROOT,
            clone,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        mutator(clone)
        return load_validator(clone).validate()


class VopsonCorpusValidationTests(unittest.TestCase):
    def setUp(self):
        self.author = read_json(ROOT, "research/vopson/AUTHOR.json")
        self.corpus = read_json(ROOT, "research/vopson/corpus.json")
        self.graph = read_json(ROOT, "research/vopson/CLAIM_GRAPH.json")
        self.contract = read_json(ROOT, "machine/contract.json")

    def test_validator_accepts_canonical_corpus(self):
        report = VALIDATOR.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["summary"]["author_orcid"], "0000-0002-8073-5538")
        self.assertEqual(report["summary"]["snapshot_date"], "2026-08-18")
        self.assertGreaterEqual(report["summary"]["works"], 19)

    def test_all_dois_are_unique_across_primary_and_alternate_fields(self):
        identifiers = []
        for work in self.corpus["works"]:
            if work["doi"]:
                identifiers.append(work["doi"])
            identifiers.extend(work["alternate_identifiers"])
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_language_entry_does_not_guess_final_doi(self):
        entry = next(
            work
            for work in self.corpus["works"]
            if work["work_id"] == "VOP-2026-LANGUAGE"
        )
        self.assertIsNone(entry["doi"])
        self.assertIn("10.2139/ssrn.6529851", entry["alternate_identifiers"])
        self.assertTrue(entry["official_metadata_url"])

    def test_polygon_counterexample_has_repository_evidence(self):
        node = next(
            node
            for node in self.graph["nodes"]
            if node["node_id"] == "CL-POLYGON-EXTREMUM"
        )
        self.assertEqual(node["claim_class"], "COUNTEREXAMPLE")
        self.assertTrue(node["evidence_paths"])
        for relative in node["evidence_paths"]:
            resolved = (ROOT / relative).resolve()
            resolved.relative_to(ROOT.resolve())
            self.assertTrue(resolved.is_file(), relative)

    def test_source_claims_name_at_least_one_primary_work(self):
        for node in self.graph["nodes"]:
            if node["kind"] == "source-claim":
                self.assertTrue(node["source_work_ids"], node["node_id"])

    def test_claim_dependency_subgraph_is_acyclic(self):
        node_ids = {node["node_id"] for node in self.graph["nodes"]}
        cycle = VALIDATOR.dependency_cycle(node_ids, self.graph["edges"])
        self.assertIsNone(cycle)

    def test_work_dependency_graph_is_acyclic(self):
        work_map = {work["work_id"]: work for work in self.corpus["works"]}
        self.assertIsNone(VALIDATOR.work_dependency_cycle(work_map))

    def test_status_vocabularies_are_anchored_in_machine_contract(self):
        schema = self.contract["vopson_corpus_schema"]
        for key in (
            "peer_review_status",
            "equation_map_status",
            "reproduction_status",
        ):
            self.assertEqual(self.corpus["enums"][key], schema[key])

    def test_human_tables_match_machine_authorities(self):
        corpus_table = VALIDATOR.extract_markdown_table(
            ROOT / "research/vopson/CORPUS.md",
            VALIDATOR.CORPUS_HEADING,
        )
        claim_table = VALIDATOR.extract_markdown_table(
            ROOT / "research/vopson/CLAIM_GRAPH.md",
            VALIDATOR.GRAPH_HEADING,
        )
        self.assertEqual(
            corpus_table,
            VALIDATOR.render_corpus_table(self.corpus["works"]),
        )
        self.assertEqual(
            claim_table,
            VALIDATOR.render_claim_table(self.graph["nodes"]),
        )

    def test_counterexample_matrix_is_a_required_read(self):
        self.assertIn(
            "research/vopson/COUNTEREXAMPLE_MATRIX.md",
            self.contract["required_agent_reads"],
        )

    def test_application_assumptions_are_not_external_theorem_targets(self):
        ids = {
            "EXT-PLANCK-AREA",
            "EXT-ENTROPIC-FORCE",
            "EXT-LANGUAGE-DOMINANCE",
        }
        nodes = {node["node_id"]: node for node in self.graph["nodes"]}
        for node_id in ids:
            self.assertEqual(nodes[node_id]["claim_class"], "INTERPRETIVE")


class ValidatorRejectionTests(unittest.TestCase):
    def assert_report_contains(self, report, fragment: str):
        self.assertFalse(report["ok"])
        self.assertTrue(
            any(fragment in error for error in report["errors"]),
            report["errors"],
        )

    def test_rejects_human_corpus_drift(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            corpus["works"][0]["title"] += " altered"
            write_json(root, "research/vopson/corpus.json", corpus)

        self.assert_report_contains(
            validate_mutation(mutate),
            "CORPUS.md chronology table is out of sync",
        )

    def test_rejects_primary_alternate_doi_collision(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            corpus["works"][1]["alternate_identifiers"] = [
                corpus["works"][0]["doi"]
            ]
            write_json(root, "research/vopson/corpus.json", corpus)

        self.assert_report_contains(validate_mutation(mutate), "DOI collision")

    def test_rejects_untyped_alternate_identifier(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            language = next(
                work
                for work in corpus["works"]
                if work["work_id"] == "VOP-2026-LANGUAGE"
            )
            language["alternate_identifiers"] = ["placeholder"]
            write_json(root, "research/vopson/corpus.json", corpus)

        self.assert_report_contains(
            validate_mutation(mutate),
            "alternate identifier must be a validated DOI",
        )

    def test_rejects_absolute_evidence_path(self):
        def mutate(root: Path):
            graph = read_json(root, "research/vopson/CLAIM_GRAPH.json")
            polygon = next(
                node
                for node in graph["nodes"]
                if node["node_id"] == "CL-POLYGON-EXTREMUM"
            )
            polygon["evidence_paths"] = ["/etc/passwd"]
            write_json(root, "research/vopson/CLAIM_GRAPH.json", graph)

        self.assert_report_contains(
            validate_mutation(mutate),
            "must not be absolute",
        )

    def test_rejects_parent_escape_evidence_path(self):
        def mutate(root: Path):
            graph = read_json(root, "research/vopson/CLAIM_GRAPH.json")
            polygon = next(
                node
                for node in graph["nodes"]
                if node["node_id"] == "CL-POLYGON-EXTREMUM"
            )
            polygon["evidence_paths"] = ["../outside.txt"]
            write_json(root, "research/vopson/CLAIM_GRAPH.json", graph)

        self.assert_report_contains(
            validate_mutation(mutate),
            "escapes repository root",
        )

    def test_rejects_missing_core_bibliographic_field(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            corpus["works"][0].pop("title")
            write_json(root, "research/vopson/corpus.json", corpus)

        self.assert_report_contains(
            validate_mutation(mutate),
            "works[0].title must be a non-empty string",
        )

    def test_rejects_source_claim_without_source_work(self):
        def mutate(root: Path):
            graph = read_json(root, "research/vopson/CLAIM_GRAPH.json")
            claim = next(
                node
                for node in graph["nodes"]
                if node["node_id"] == "CL-MEI-BIT-MASS"
            )
            claim["source_work_ids"] = []
            write_json(root, "research/vopson/CLAIM_GRAPH.json", graph)

        self.assert_report_contains(
            validate_mutation(mutate),
            "source-claim requires at least one source_work_id",
        )

    def test_rejects_work_dependency_cycle(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            first = next(
                work for work in corpus["works"] if work["work_id"] == "VOP-2019-MEI"
            )
            first["depends_on"] = ["VOP-2020-CATASTROPHE"]
            write_json(root, "research/vopson/corpus.json", corpus)

        self.assert_report_contains(
            validate_mutation(mutate),
            "work dependency cycle",
        )

    def test_corpus_cannot_self_authorize_new_status(self):
        def mutate(root: Path):
            corpus = read_json(root, "research/vopson/corpus.json")
            corpus["enums"]["reproduction_status"].append("magic")
            corpus["works"][0]["reproduction_status"] = "magic"
            write_json(root, "research/vopson/corpus.json", corpus)

        report = validate_mutation(mutate)
        self.assert_report_contains(
            report,
            "must exactly match machine contract authority",
        )
        self.assertTrue(
            any("invalid reproduction_status" in error for error in report["errors"]),
            report["errors"],
        )

    def test_source_claim_cannot_use_established_literature_exemption(self):
        def mutate(root: Path):
            graph = read_json(root, "research/vopson/CLAIM_GRAPH.json")
            claim = next(
                node
                for node in graph["nodes"]
                if node["node_id"] == "CL-GENIES-METHOD"
            )
            claim["claim_class"] = "PROVED"
            claim["assessment_status"] = "established-literature"
            claim["evidence_paths"] = []
            write_json(root, "research/vopson/CLAIM_GRAPH.json", graph)

        report = validate_mutation(mutate)
        self.assert_report_contains(
            report,
            "established-literature exemption is restricted",
        )
        self.assertTrue(
            any(
                "PROVED requires repository evidence_paths" in error
                for error in report["errors"]
            ),
            report["errors"],
        )


if __name__ == "__main__":
    unittest.main()
