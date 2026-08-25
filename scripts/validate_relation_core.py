#!/usr/bin/env python3
"""Post-tag live-schedule wrapper for the frozen PR11 relation authority.

The exact pre-release-gate wrapper is preserved in
validate_relation_core_pr21_pre_release_gate.py. PR11 theorem semantics remain
frozen; only the shared live roadmap expectation advances to the post-tag Lean
implementation/CI-hardening phase.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/validate_relation_core_pr21_pre_release_gate.py"
FROZEN_BASE = ROOT / "scripts/validate_relation_core_frozen_pr11.py"
ROADMAP_STATE = ROOT / "machine/roadmap_state.json"
EXPECTED_BASE_VALIDATOR_BLOB = "6f1e5629213276169c169f61ef6271a15f40a79e"
EXPECTED_FROZEN_BASE_VALIDATOR_BLOB = "655fee62ff316a424a1b28ccc35c7fe82e0ed8e2"


def local_git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def base_validator_blob_errors(path: Path = BASE) -> list[str]:
    """Bind the immediate relation compatibility authority before importing it."""
    if not path.is_file():
        return ["pre-release-gate relation compatibility validator missing before import"]
    actual = local_git_blob_sha(path)
    if actual != EXPECTED_BASE_VALIDATOR_BLOB:
        return [
            "pre-release-gate relation compatibility validator blob drift: "
            f"expected {EXPECTED_BASE_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def frozen_base_validator_blob_errors(path: Path = FROZEN_BASE) -> list[str]:
    """Bind the frozen PR11 engine imported by the immediate wrapper."""
    if not path.is_file():
        return ["frozen PR11 relation validator missing before compatibility import"]
    actual = local_git_blob_sha(path)
    if actual != EXPECTED_FROZEN_BASE_VALIDATOR_BLOB:
        return [
            "frozen PR11 relation validator blob drift: "
            f"expected {EXPECTED_FROZEN_BASE_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def compatibility_validator_blob_errors() -> list[str]:
    return base_validator_blob_errors() + frozen_base_validator_blob_errors()


_preload_base_errors = compatibility_validator_blob_errors()
if _preload_base_errors:
    raise RuntimeError("; ".join(_preload_base_errors))

_spec = importlib.util.spec_from_file_location("relation_core_pr21_pre_release_gate", BASE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load prior relation compatibility validator: {BASE}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

EXPECTED_ROADMAP_STATE = copy.deepcopy(_base.EXPECTED_ROADMAP_STATE)
EXPECTED_ROADMAP_STATE["schema_version"] = "1.8.0"
EXPECTED_ROADMAP_STATE["snapshot_date"] = "2026-08-25"
for _item in EXPECTED_ROADMAP_STATE["sequence"]:
    if _item.get("planned_pr") == 10:
        _item["status"] = "active-post-tag-lean-implementation-ci-hardening"
EXPECTED_ROADMAP_STATE["compatibility_note"] = (
    "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, "
    "Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, EFP, and the v3.0.0 Lean "
    "source-freeze authorities retain their historical semantics. This file is the live post-tag schedule "
    "authority: immutable source tag v3.0.0 resolves to b7f51590985e60920c8b09fc9238b8aec6cfa3bc; "
    "LEAN-OBS-BATCH-001 implements UFT-OBS-001 through UFT-OBS-004 and LEAN-OBS-BATCH-002 implements "
    "UFT-OBS-005. Both remain IMPLEMENTED_PENDING_CI until the pinned Lean build, source binding, hostile "
    "review, and axiom audit are green."
)
EXPECTED_ROADMAP_STATE["rules"][2] = (
    "The v3.0.0 source freeze remains immutable and historically records UFT-OBS-005 as deferred from batch 001; "
    "live post-tag implementation may proceed only against that exact tag, with pinned Lean/Lake/Mathlib, exact "
    "source binding, checked compilation, and explicit imported-axiom auditing before any LEAN_VERIFIED promotion."
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


def reject_duplicate_object_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str):
    raise ValueError(f"non-finite JSON number: {value}")


def parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number: {value}")
    return parsed


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_object_keys,
        parse_constant=reject_nonfinite_constant,
        parse_float=parse_finite_float,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def live_roadmap_json_errors() -> list[str]:
    try:
        load_json(ROADMAP_STATE)
    except (OSError, ValueError) as exc:
        return [f"live roadmap state JSON invalid: {exc}"]
    return []


def validate():
    roadmap_errors = live_roadmap_json_errors()
    if roadmap_errors:
        return {
            "status": "error",
            "errors": roadmap_errors + compatibility_validator_blob_errors(),
            "theorem_count": 0,
            "counterexample_count": 0,
            "exhaustive_relation_count": 0,
            "public_context_ref_count": 0,
        }
    result = _base.validate()
    errors = list(result.get("errors", []))
    errors.extend(compatibility_validator_blob_errors())
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PR11 relation/selection core:", result["status"])
        for error in result["errors"]:
            print(" -", error)
    return 0 if result["status"] == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
