#!/usr/bin/env python3
"""Live Representation validator with the pre-integration audit frozen beneath it."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_representation_calculus_preintegration_frozen.py"

_spec = importlib.util.spec_from_file_location("representation_validator_preintegration_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen Representation validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

# The theorem wording was tightened after the implementation proof audit so that
# rank preservation is attributed to invertible left/right multiplication under
# similarity, not incorrectly to characteristic-polynomial equality alone.
_frozen.EXPECTED_THEOREMS["UFT-REP-001"]["statement"] = (
    "If B=P^{-1}AP for an invertible finite-dimensional change of basis P over R or C, "
    "then A and B have the same characteristic polynomial and also the same rank; "
    "in particular trace and determinant are preserved."
)

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = _frozen.validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Representation authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
