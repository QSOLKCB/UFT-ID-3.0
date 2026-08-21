#!/usr/bin/env python3
"""Compatibility wrapper around the frozen PR11 graph validator.

PR #12 advances only the centrally synchronized human authority blobs that now
include BridgeCore. The PR11 graph validation logic itself remains byte-for-byte
preserved in validate_graph_realization_pr11_frozen.py.
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
    "claims": "65d6bc887f33a9e264623ad50eb4ad4e9ed3b07f",
    "readme4ai": "e0b0f1bb2ee49f70bb1b1386747ad28b5d7b1b84",
    "reproducibility": "bde33763383a099c32002a6a6d1d949dfefbdfe7",
})

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

if __name__ == "__main__":
    raise SystemExit(_frozen.main())
