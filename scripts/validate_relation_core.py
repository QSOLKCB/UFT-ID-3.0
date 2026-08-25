#!/usr/bin/env python3
"""PR #21 live-schedule wrapper for the current PR11 compatibility validator.

The exact pre-release-gate wrapper is preserved in
validate_relation_core_pr21_pre_release_gate.py. PR11 theorem semantics remain
frozen; only the shared live roadmap expectation advances from theorem-batch
freezing to the post-merge source-release gate.
"""
from __future__ import annotations

import copy
import importlib.util

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/validate_relation_core_pr21_pre_release_gate.py"

_spec = importlib.util.spec_from_file_location("relation_core_pr21_pre_release_gate", BASE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load prior relation compatibility validator: {BASE}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

EXPECTED_ROADMAP_STATE = copy.deepcopy(_base.EXPECTED_ROADMAP_STATE)
for _item in EXPECTED_ROADMAP_STATE["sequence"]:
    if _item.get("planned_pr") == 10:
        _item["status"] = "active-post-merge-release-gate"
EXPECTED_ROADMAP_STATE["compatibility_note"] = (
    "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, "
    "Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, and EFP theorem authorities retain "
    "their historical semantics. This file is the live post-EFP schedule authority: the first PR #10 theorem batch "
    "is frozen and the next gate is exact merged-main validation plus an immutable source-release tag before any Lean "
    "proof implementation."
)
EXPECTED_ROADMAP_STATE["rules"][2] = (
    "The first Lean theorem batch and dependency graph are frozen; exact merged-main validation and an immutable "
    "source-release tag must complete before any Lean/Lake/Mathlib proof implementation, while mathematical proof, "
    "Lean proof, runtime conformance, and empirical validation remain separately typed authorities."
)
EXPECTED_ROADMAP_SEQUENCE = [
    (item["planned_pr"], item["surface"], item["status"])
    for item in EXPECTED_ROADMAP_STATE["sequence"]
]

_base.EXPECTED_ROADMAP_STATE = EXPECTED_ROADMAP_STATE
_base.EXPECTED_ROADMAP_SEQUENCE = EXPECTED_ROADMAP_SEQUENCE

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

# Re-export the advanced expectations after the compatibility module export.
globals()["EXPECTED_ROADMAP_STATE"] = EXPECTED_ROADMAP_STATE
globals()["EXPECTED_ROADMAP_SEQUENCE"] = EXPECTED_ROADMAP_SEQUENCE

if __name__ == "__main__":
    raise SystemExit(_base.main())
