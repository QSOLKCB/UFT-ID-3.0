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


VALIDATOR = load_module("graph_realization_validator_final2", "scripts/validate_graph_realization.py")


class LatestCodexRegressions(unittest.TestCase):
    def assert_dedicated_error(self, result, fragment: str):
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_exit_before_graph_artifact_commands_fails_closed(self):
        path = ROOT / ".github/workflows/finite-adversarial.yml"
        original = path.read_text(encoding="utf-8")
        first_command = VALIDATOR.GRAPH_ARTIFACT_COMMANDS[0]
        try:
            mutated = original.replace(
                f"          {first_command}",
                f"          exit 0\n          {first_command}",
                1,
            )
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            result = VALIDATOR.validate()
            self.assert_dedicated_error(result, "shell control flow or early termination")
        finally:
            path.write_text(original, encoding="utf-8")

    def test_human_theorem_formula_is_bound_after_digest_rebind(self):
        path = ROOT / "theory/GRAPH_REALIZATION.md"
        original = path.read_text(encoding="utf-8")
        old_digest = VALIDATOR.EXPECTED_SHA256["human"]
        old_formula = r"\deg^+_{G_{\mathrm{step}}}(x)=0."
        new_formula = r"\deg^-_{G_{\mathrm{step}}}(x)=0."
        try:
            mutated = original.replace(old_formula, new_formula, 1)
            self.assertNotEqual(mutated, original)
            path.write_text(mutated, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256["human"] = VALIDATOR.sha256_bytes(mutated.encode("utf-8"))
            result = VALIDATOR.validate()
            self.assert_dedicated_error(result, "UFT-GR-002 frozen human theorem content drift")
            self.assertNotIn("human canonical payload drift", result["errors"])
        finally:
            path.write_text(original, encoding="utf-8")
            VALIDATOR.EXPECTED_SHA256["human"] = old_digest


if __name__ == "__main__":
    unittest.main()
