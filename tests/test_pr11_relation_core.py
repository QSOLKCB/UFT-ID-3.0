"""Compatibility wrapper for the frozen PR #11 relation-core tests.

The merged PR11 test module remains byte-for-byte in
pr11_relation_core_tests_frozen.py. Only assertions inherently tied to the live
roadmap clock/state are advanced to the current PR #10 theorem-batch-freeze
phase.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "tests/pr11_relation_core_tests_frozen.py"


def _load_frozen():
    spec = importlib.util.spec_from_file_location("pr11_relation_core_tests_frozen", FROZEN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen PR11 relation tests: {FROZEN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_FROZEN = _load_frozen()


def _updated_active_surface_test(self):
    value = _FROZEN.canonical_documents()
    value["roadmap_state"]["active_planned_surface"] = 11
    self.assert_error_contains(value, "active planned surface must be PR10")


def _updated_complete_roadmap_state_semantic_drift(self):
    mutations = {
        "deferred": [10],
        "compatibility_note": "PR8 and PR9 authority is obsolete.",
        "fixture_policy": "Any decorative example is sufficient proof.",
        "rules": ["COMPATIBILITY => UNIQUE_PHYSICAL_SELECTION"],
    }
    for field, replacement in mutations.items():
        with self.subTest(field=field):
            value = _FROZEN.canonical_documents()
            value["roadmap_state"][field] = replacement
            self.assert_error_contains(value, "live roadmap state canonical payload drift")


def _updated_future_snapshot_test(self):
    cases = {
        "contract": ("2026-08-21", "relation contract UTC snapshot drift"),
        "theorems": ("2026-08-21", "relation theorem registry shape/snapshot mismatch"),
        "counterexamples": ("2026-08-21", "relation counterexample registry shape/snapshot mismatch"),
        "selection": ("2026-08-21", "genus selection specimen canonical payload drift"),
        "roadmap_state": ("2026-08-26", "live roadmap state canonical payload drift"),
    }
    for key, (future_date, diagnostic) in cases.items():
        with self.subTest(key=key):
            value = _FROZEN.canonical_documents()
            value[key]["snapshot_date"] = future_date
            self.assert_error_contains(value, diagnostic)


_FROZEN.PR11RelationMutationTests.test_rejects_live_roadmap_active_surface_drift = _updated_active_surface_test
_FROZEN.PR11RelationMutationTests.test_rejects_complete_roadmap_state_semantic_drift = _updated_complete_roadmap_state_semantic_drift
_FROZEN.PR11RelationMutationTests.test_rejects_pr11_future_utc_snapshot_dates = _updated_future_snapshot_test

PR11RelationCoreTests = _FROZEN.PR11RelationCoreTests
PR11RelationMutationTests = _FROZEN.PR11RelationMutationTests
