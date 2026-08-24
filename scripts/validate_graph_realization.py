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
    "claims": "39b92b0ce9b14d61e2674aaf0fe3ea4e9612983d",
    "readme4ai": "42ed18cb637d9c0ae7b93a915166d05b67bcf7b0",
    "reproducibility": "1262c23d443aa18e7c70aa368febf275998eb99b",
    "roadmap": "479ff868da62b4b6cdd19b028dcf50e734f1cdbe",
})

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

if __name__ == "__main__":
    raise SystemExit(_frozen.main())
