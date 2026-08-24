#!/usr/bin/env python3
"""Compatibility wrapper around the frozen PR11 graph validator.

The PR11 graph validation logic remains byte-for-byte preserved in
validate_graph_realization_pr11_frozen.py. Later formal phases may extend the
central human authority surfaces or equivalent workflow syntax; this wrapper
advances only those exact compatibility pins while retaining every frozen graph
theorem, donor, and semantic-boundary check.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_graph_realization_pr11_frozen.py"

_spec = importlib.util.spec_from_file_location("graph_validator_pr11_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen graph validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

_frozen.EXPECTED_HUMAN_BLOBS.update({
    "claims": "c876fe43789572d29f90c2034c98487b54e39142",
    "readme4ai": "0c4ee151b7fb8351dd796b377eb7d99e7fab1b93",
    "reproducibility": "bcba98a9c2cd42d8baf4b909ce5fa5fd57f6ad84",
    "roadmap": "167fafca38113fb05f8520e08952748a5be64d42",
})
_frozen.EXPECTED_VERIFY_STEP_DIRECTIVES = (
    "if: always()",
    "run: python scripts/verify_graph_artifacts.py artifacts",
)

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

if __name__ == "__main__":
    raise SystemExit(_frozen.main())
