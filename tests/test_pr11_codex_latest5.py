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


VALIDATOR = load_module("graph_validator_latest5", "scripts/validate_graph_realization.py")
ARTIFACTS = load_module("graph_artifact_verifier_latest5", "scripts/verify_graph_artifacts.py")


class LatestFiveCodexRegressions(unittest.TestCase):
    def assert_dedicated_error(self, result, fragment: str):
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def mutate_text(self, relpath: str, transform, *, rebind_digest: str | None = None):
        path = ROOT / relpath
        original = path.read_text(encoding="utf-8")
        old_digest = VALIDATOR.EXPECTED_SHA256.get(rebind_digest) if rebind_digest else None
        try:
            mutated = transform(original)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            if rebind_digest is not None:
                VALIDATOR.EXPECTED_SHA256[rebind_digest] = VALIDATOR.sha256_bytes(
                    mutated.encode("utf-8")
                )
            return VALIDATOR.validate()
        finally:
            path.write_text(original, encoding="utf-8")
            if rebind_digest is not None and old_digest is not None:
                VALIDATOR.EXPECTED_SHA256[rebind_digest] = old_digest

    def mutate_json(self, relpath: str, mutate, *, rebind_digest: str):
        def transform(text: str) -> str:
            payload = json.loads(text)
            mutate(payload)
            return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        return self.mutate_text(relpath, transform, rebind_digest=rebind_digest)

    def test_sourced_exit_before_graph_artifacts_fails_closed(self):
        first = VALIDATOR.GRAPH_ARTIFACT_COMMANDS[0]
        result = self.mutate_text(
            ".github/workflows/finite-adversarial.yml",
            lambda text: text.replace(
                f"          {first}",
                f"          source <(printf 'exit 0\\n')\n          {first}",
                1,
            ),
        )
        self.assert_dedicated_error(result, "shell control flow or early termination")
        self.assert_dedicated_error(result, "deterministic evidence bundle command surface drift")

    def test_artifact_verifier_rejects_missing_graph_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "missing or empty retained graph artifact"):
                ARTIFACTS.verify(Path(tmp))

    def test_human_theorem_anchor_is_scoped_to_its_section(self):
        old_formula = r"\deg^+_{G_{\mathrm{step}}}(x)=0."
        new_formula = r"\deg^-_{G_{\mathrm{step}}}(x)=0."

        def transform(text: str) -> str:
            changed = text.replace(old_formula, new_formula, 1)
            return changed + f"\nUnrelated trailing note: {old_formula}\n"

        result = self.mutate_text(
            "theory/GRAPH_REALIZATION.md",
            transform,
            rebind_digest="human",
        )
        self.assert_dedicated_error(result, "UFT-GR-002 frozen human theorem content drift")
        self.assertNotIn("human canonical payload drift", result["errors"])

    def test_executable_evidence_is_bound_per_result(self):
        def mutate(payload):
            record = next(r for r in payload["records"] if r["id"] == "UFT-GR-006")
            record["executable_evidence"] = ["README4AI.md"]

        result = self.mutate_json(
            "machine/graph_realization_results.json",
            mutate,
            rebind_digest="results",
        )
        self.assert_dedicated_error(result, "UFT-GR-006 executable evidence set drift")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def test_grinberg_exact_revision_is_bound(self):
        def mutate(payload):
            record = next(s for s in payload["sources"] if s["source_id"] == "GRINBERG-2025-GRAPH-THEORY")
            record["identifier"] = "arXiv:2308.04512v1"

        result = self.mutate_json(
            "machine/graph_realization_contract.json",
            mutate,
            rebind_digest="contract",
        )
        self.assert_dedicated_error(result, "Grinberg source identifier drift")
        self.assertNotIn("contract canonical payload drift", result["errors"])

    def test_results_envelope_is_checked_independently_of_digest(self):
        def mutate(payload):
            payload["schema_version"] = "99.0.0"

        result = self.mutate_json(
            "machine/graph_realization_results.json",
            mutate,
            rebind_digest="results",
        )
        self.assert_dedicated_error(result, "graph results schema drift")
        self.assertNotIn("results canonical payload drift", result["errors"])


if __name__ == "__main__":
    unittest.main()
