from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_empirical_falsification_profile.py"
README = ROOT / "README4AI.md"

LIVE_SCHEDULE_PHRASE = (
    "Historical scheduling authority for the v3.0.0 source freeze remains PR #10 Lean observation foundation. "
    "Live post-tag authority is now `machine/roadmap_state.json` plus `machine/lean_observation_verification.json`: "
    "immutable tag `v3.0.0` is cut at `b7f51590985e60920c8b09fc9238b8aec6cfa3bc`, `LEAN-OBS-BATCH-001` "
    "implements `UFT-OBS-001` through `004`, and arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`; both "
    "are `LEAN_VERIFIED` at formalization integration commit `bbcde19827921af4490c232bdc1edc401790d89e`, tree "
    "`b7ec78695f32a5b1cf78b416a5050627ad4f957d`, after exact merged-main `finite-adversarial` run `32876623204` "
    "and `vopson-corpus` run `32876623479` succeeded. The next ordered gate is QSOL-CONTEXT verification capture, "
    "then DOI/archive work."
)
LIVE_LEAN_PHRASE = (
    "PR #10 Lean observation foundation is the historical source-freeze authority. Source batch "
    "`LEAN-OBS-BATCH-001` remains frozen in `machine/lean_observation_foundation_contract.json`, covering "
    "`UFT-OBS-001` through `UFT-OBS-004`; the same v3.0.0 freeze records `UFT-OBS-005` as deferred from batch 001 "
    "rather than dropped."
)
LIVE_VERIFIED_PHRASE = (
    "Both batches are `LEAN_VERIFIED`, bound to formalization integration commit "
    "`bbcde19827921af4490c232bdc1edc401790d89e`, tree `b7ec78695f32a5b1cf78b416a5050627ad4f957d`, "
    "exact merged-main `finite-adversarial` run `32876623204`, and exact merged-main `vopson-corpus` run `32876623479`."
)
STALE_RELEASE_GATE_PHRASE = (
    "Live scheduling authority is PR #10 Lean observation foundation: the first theorem batch and dependency graph "
    "are frozen, and the active phase is the post-merge release gate for exact merged-main validation plus immutable "
    "source tagging before Lean implementation."
)
STALE_PRETAG_PHRASE = (
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
        self.assertIn(LIVE_LEAN_PHRASE, text)
        self.assertIn(LIVE_VERIFIED_PHRASE, text)
        self.assertNotIn("IMPLEMENTED_PENDING_CI", text)
        self.assertNotIn(STALE_RELEASE_GATE_PHRASE, text)
        self.assertNotIn(STALE_PRETAG_PHRASE, text)
        self.assertNotIn("The active planned PR #18 surface", text)
        self.assertNotIn("Lean remains deferred until source reproduction", text)
        self.assertNotIn("Lean/Lake/Mathlib remain unpinned", text)

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
