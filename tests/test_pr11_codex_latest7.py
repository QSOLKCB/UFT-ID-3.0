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


VALIDATOR = load_module("graph_validator_latest7", "scripts/validate_graph_realization.py")
ARTIFACTS = load_module("graph_artifact_verifier_latest7", "scripts/verify_graph_artifacts.py")
RECEIPT = load_module("graph_receipt_latest7", "experiments/run_graph_realization.py")
EXPERIMENT = load_module("graph_experiment_latest7", "experiments/graph_realization/run.py")


class LatestCodexAuthorityRegressions(unittest.TestCase):
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
            path.write_text(mutated, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256[rebind_digest] = VALIDATOR.sha256_bytes(mutated.encode("utf-8"))
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256[rebind_digest] = old_digest

    def mutate_text(
        self,
        relpath: str,
        transform,
        *,
        rebind_digest: str | None = None,
        rebind_blob: str | None = None,
    ):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        old_digest = VALIDATOR.EXPECTED_SHA256.get(rebind_digest) if rebind_digest else None
        old_blob = VALIDATOR.EXPECTED_HUMAN_BLOBS.get(rebind_blob) if rebind_blob else None
        try:
            mutated = transform(original)
            self.assertNotEqual(mutated, original)
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

    def test_positive_control_cannot_promote_empirical_donor_to_proof(self):
        def mutate(payload):
            record = next(x for x in payload["positive_controls"] if x["id"] == "PC-GR-SIS2")
            record["claim_class"] = "PROVED"
            record["statement"] = "The cited SiS2 phases establish that UFT-ID is materially realized."

        result = self.mutate_json(
            "machine/graph_realization_contract.json",
            mutate,
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "graph positive-control authority payload drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_theorem_scoped_nonclaim_is_exact_bound(self):
        def mutate(payload):
            record = next(x for x in payload["records"] if x["id"] == "UFT-GR-001")
            record["nonclaims"] = ["The graph is the fundamental physical substrate."]

        result = self.mutate_json(
            "machine/graph_realization_results.json",
            mutate,
            rebind_digest="results",
        )
        self.assert_dedicated_error(result, "UFT-GR-001 theorem/counterexample nonclaims drift")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def test_grinberg_author_and_kind_are_bound(self):
        def mutate(payload):
            record = next(x for x in payload["sources"] if x["source_id"] == "GRINBERG-2025-GRAPH-THEORY")
            record["author"] = "Unrelated Author"
            record["kind"] = "peer-reviewed-theorem-source"

        result = self.mutate_json(
            "machine/graph_realization_contract.json",
            mutate,
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "Grinberg source author drift")
        self.assert_dedicated_error(result, "Grinberg source kind drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_donor_role_and_noninheritance_are_bound(self):
        def mutate(payload):
            record = next(x for x in payload["sources"] if x["source_id"] == "GRINBERG-2025-GRAPH-THEORY")
            record["role"] = "established evidence for a UFT-ID physical substrate"
            record["not_inherited"] = []

        result = self.mutate_json(
            "machine/graph_realization_contract.json",
            mutate,
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "Grinberg source role drift")
        self.assert_dedicated_error(result, "Grinberg source not_inherited drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_human_theorem_claim_class_is_section_bound(self):
        result = self.mutate_text(
            "theory/GRAPH_REALIZATION.md",
            lambda text: text.replace("**Claim class:** `PROVED`", "**Claim class:** `EMPIRICAL`", 1),
            rebind_digest="human",
        )
        self.assert_dedicated_error(result, "UFT-GR-001 human theorem claim class drift")
        self.assertNotIn("human canonical payload drift", result["errors"])

    def test_numerosity_claim_class_is_parsed_not_cosmetically_anchored(self):
        canonical = (
            "**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence in this section "
            "until explicit BridgeCore objects and independent mathematical fixtures exist."
        )
        promoted = canonical.replace("`INTERPRETIVE`", "`PROVED`", 1)

        def transform(text: str) -> str:
            changed = text.replace(canonical, promoted, 1)
            return changed + f"\n<!-- compatibility text only: {canonical} -->\n"

        result = self.mutate_text("ROADMAP.md", transform, rebind_blob="roadmap")
        self.assert_dedicated_error(result, "ROADMAP 3-4-5 numerosity programme claim class drift")
        self.assertNotIn("roadmap canonical human authority blob drift", result["errors"])

    def test_retained_verification_step_must_remain_blocking(self):
        marker = "      - name: Verify retained graph evidence\n        if: always()\n"
        result = self.mutate_text(
            ".github/workflows/finite-adversarial.yml",
            lambda text: text.replace(
                marker,
                marker + "        continue-on-error: true\n",
                1,
            ),
        )
        self.assert_dedicated_error(result, "verification step envelope drift")

    def _write_artifacts(self, directory: Path, witness: dict, receipt: dict) -> None:
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

    def _rebind_receipt(self, receipt: dict, witness: dict) -> None:
        receipt["result_sha256"] = ARTIFACTS.sha256_bytes(ARTIFACTS.canonical_bytes(witness))
        receipt["suite_fingerprint_sha256"] = ARTIFACTS.sha256_bytes(
            ARTIFACTS.canonical_bytes(ARTIFACTS.fingerprint_identity(receipt))
        )

    def test_retained_witness_must_match_complete_recomputed_suite(self):
        witness = EXPERIMENT.run_suite()
        receipt = RECEIPT.run_suite()
        for key in ("positive_controls", "counterexamples", "claim_boundary"):
            witness.pop(key)
        self._rebind_receipt(receipt, witness)

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_artifacts(directory, witness, receipt)
            with self.assertRaisesRegex(RuntimeError, "full payload drift"):
                ARTIFACTS.verify(directory)

    def test_retained_receipt_source_and_evidence_sets_are_repository_bound(self):
        witness = EXPERIMENT.run_suite()
        receipt = RECEIPT.run_suite()
        receipt["source_sha256"] = {"not/a/real/source.txt": "0" * 64}
        receipt["declared_evidence_paths"] = ["not/a/real/evidence.py"]
        self._rebind_receipt(receipt, witness)

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_artifacts(directory, witness, receipt)
            with self.assertRaisesRegex(RuntimeError, "source file set drift"):
                ARTIFACTS.verify(directory)

    def test_receipt_claim_boundary_is_exact_and_fingerprinted(self):
        witness = EXPERIMENT.run_suite()
        receipt = RECEIPT.run_suite()
        receipt["claim_boundary"] = (
            "FINITE_GRAPH_CONFORMANCE = GENERAL_PROOF; "
            "MATERIAL_POSITIVE_CONTROL = UFT_ID_PHYSICAL_PREMISE"
        )
        self._rebind_receipt(receipt, witness)

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_artifacts(directory, witness, receipt)
            with self.assertRaisesRegex(RuntimeError, "claim boundary drift"):
                ARTIFACTS.verify(directory)

    def test_receipt_runner_cannot_shrink_its_own_source_set(self):
        witness = EXPERIMENT.run_suite()
        receipt = RECEIPT.run_suite()
        path = ROOT / "experiments/run_graph_realization.py"
        original = path.read_text(encoding="utf-8")
        needle = '    "scripts/verify_graph_artifacts.py",\n'
        try:
            mutated = original.replace(needle, "", 1)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                self._write_artifacts(directory, witness, receipt)
                with self.assertRaisesRegex(RuntimeError, "core source set drift"):
                    ARTIFACTS.verify(directory)
        finally:
            path.write_text(original, encoding="utf-8")

    def test_345_numerosity_programme_is_frozen_and_interpretive(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        for anchor in (
            "# Future 3-4-5 finite numerosity and semantic-lifting stress programme",
            "NumberSpec = (n, role, carrier, structure, semantics, scope)",
            "CARDINALITY_3 != ARITY_3 != DIMENSION_3 != RADIX_3",
            "MUSICAL_GENUS != TOPOLOGICAL_GENUS",
            "3^2 + 4^2 = 5^2",
            "NO_SEMANTIC_LIFTING_WITHOUT_A_BRIDGE",
            "NUMBER != ROLE != STRUCTURE != MECHANISM != ONTOLOGY",
        ):
            self.assertIn(anchor, roadmap)


if __name__ == "__main__":
    unittest.main()
