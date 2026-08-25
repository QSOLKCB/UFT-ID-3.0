from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_empirical_falsification_profile.py"
README = ROOT / "README4AI.md"

LIVE_SCHEDULE_PHRASE = (
    "Live scheduling authority is PR #10 Lean observation foundation: the first theorem batch and dependency graph "
    "are frozen, and the active phase is the post-merge release gate for exact merged-main validation plus immutable "
    "source tagging before Lean implementation."
)
STALE_SCHEDULE_PHRASE = (
    "Live scheduling authority is PR #10 Lean observation foundation, active only for first-theorem-batch and "
    "dependency-graph freezing."
)


def load_validator():
    spec = importlib.util.spec_from_file_location("post_efp_bootstrap_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load EFP live validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PostEfpBootstrapScheduleTests(unittest.TestCase):
    def test_bootstrap_matches_live_pr10_schedule(self):
        validator = load_validator()
        result = validator.validate()
        self.assertEqual(result["status"], "ok", result["errors"])
        text = README.read_text(encoding="utf-8")
        self.assertIn("The completed planned PR #18 surface defines a synthetic conformance procedure", text)
        self.assertIn(LIVE_SCHEDULE_PHRASE, text)
        self.assertNotIn(STALE_SCHEDULE_PHRASE, text)
        self.assertIn("PR #10 Lean observation foundation is active. Source batch `LEAN-OBS-BATCH-001` is frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; `UFT-OBS-005` remains deferred to a later arithmetic-focused batch.", text)
        self.assertNotIn("The active planned PR #18 surface", text)
        self.assertNotIn("Lean remains deferred until source reproduction", text)

    def test_stale_pr18_active_bootstrap_fails_closed(self):
        validator = load_validator()
        original = README.read_text(encoding="utf-8")
        mutated = original.replace(
            "The completed planned PR #18 surface defines a synthetic conformance procedure",
            "The active planned PR #18 surface defines a synthetic conformance procedure",
            1,
        )
        self.assertNotEqual(mutated, original)
        try:
            README.write_text(mutated, encoding="utf-8")
            result = validator.validate()
        finally:
            README.write_text(original, encoding="utf-8")
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("README4AI" in error for error in result["errors"]), result["errors"])


if __name__ == "__main__":
    unittest.main()
