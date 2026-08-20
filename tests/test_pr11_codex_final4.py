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


VALIDATOR = load_module("graph_validator_final4", "scripts/validate_graph_realization.py")


class FinalFourCodexRegressions(unittest.TestCase):
    def _mutate_and_validate(
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
            path.write_text(mutated, encoding="utf-8")
            if rebind_digest is not None:
                VALIDATOR.EXPECTED_SHA256[rebind_digest] = VALIDATOR.sha256_bytes(
                    mutated.encode("utf-8")
                )
            if rebind_blob is not None:
                VALIDATOR.EXPECTED_HUMAN_BLOBS[rebind_blob] = VALIDATOR.git_blob_sha(
                    mutated.encode("utf-8")
                )
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

    def test_shell_disabled_graph_artifacts_fail_closed(self):
        first = VALIDATOR.GRAPH_ARTIFACT_COMMANDS[0]
        last = VALIDATOR.GRAPH_ARTIFACT_COMMANDS[-1]

        def mutate(text: str) -> str:
            text = text.replace(f"          {first}", f"          if false; then\n          {first}", 1)
            return text.replace(f"          {last}", f"          {last}\n          fi", 1)

        result = self._mutate_and_validate(
            ".github/workflows/finite-adversarial.yml",
            mutate,
        )
        self.assert_dedicated_error(result, "may not contain shell control flow")

    def test_commented_roadmap_graph_commands_fail_closed_after_blob_rebind(self):
        def mutate(text: str) -> str:
            for command in VALIDATOR.ROADMAP_GRAPH_COMMANDS:
                text = text.replace(command, f"# {command}", 1)
            return text

        result = self._mutate_and_validate(
            "ROADMAP.md",
            mutate,
            rebind_blob="roadmap",
        )
        self.assert_dedicated_error(result, "ROADMAP graph validation gate missing executable command")
        self.assertNotIn("roadmap canonical human authority blob drift", result["errors"])

    def test_machine_theorem_statement_cannot_drift_after_digest_rebind(self):
        result = self._mutate_and_validate(
            "machine/graph_realization_results.json",
            lambda text: text.replace(
                "In G_step, Normal_stepRel(x) iff outdegree(x)=0.",
                "In G_step, Normal_stepRel(x) iff indegree(x)=0.",
                1,
            ),
            rebind_digest="results",
        )
        self.assert_dedicated_error(result, "UFT-GR-002 machine theorem statement drift")
        self.assertNotIn("results canonical payload drift", result["errors"])

    def test_every_physiology_mapping_remains_interpretive_after_blob_rebind(self):
        canonical = "| H. FlyWire -> weighted/versioned structure-function mapping | `INTERPRETIVE` |"
        altered = "| H. FlyWire -> weighted/versioned structure-function mapping | `DIAGNOSTIC` |"
        result = self._mutate_and_validate(
            "ROADMAP.md",
            lambda text: text.replace(canonical, altered, 1),
            rebind_blob="roadmap",
        )
        self.assert_dedicated_error(
            result,
            "ROADMAP physiology/connectomics positive-control programme missing semantic anchor",
        )
        self.assertNotIn("roadmap canonical human authority blob drift", result["errors"])

    def test_fivefold_donor_programme_is_interpretive_and_bounded(self):
        result = VALIDATOR.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        for anchor in (
            "CARDINALITY_5 != FIVEFOLD_SYMMETRY",
            "PENTAMER != PENTATONIC_SCALE",
            "SHARED_CARDINALITY != SHARED_PHYSICAL_MECHANISM",
        ):
            self.assertIn(anchor, roadmap)


if __name__ == "__main__":
    unittest.main()
