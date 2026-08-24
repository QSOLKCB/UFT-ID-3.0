#!/usr/bin/env python3
"""Compatibility wrapper around the frozen PR11 graph validator.

The PR11 graph validation logic remains byte-for-byte preserved in
validate_graph_realization_pr11_frozen.py. Later formal phases may extend the
central human authority surfaces; this wrapper advances only those exact blob
pins while retaining every frozen graph theorem, donor, workflow, and semantic
boundary check.
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
    "claims": "d5a8889d1662e654708c75afdd338d20f96a2c40",
    "readme4ai": "d43a872083f6518a25f6cd5547d64e744e1d6eb7",
    "reproducibility": "eab1bf5fbb1870ecbe593df21e028666a6799d8d",
    "roadmap": "448593179a23320450272071615a58dc480faaab",
})

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

if __name__ == "__main__":
    raise SystemExit(_frozen.main())
