#!/usr/bin/env python3
"""Verify the retained Lean observation source-freeze validation artifact."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_lean_observation_foundation.py"
VALIDATION_FILE = "lean-observation-freeze-validation.json"
EXPECTED_FIELDS = {
    "basis_objects_verified",
    "batch_id",
    "deferred_count",
    "errors",
    "module_count",
    "status",
    "theorem_count",
}


def reject_duplicate_object_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str):
    raise ValueError(f"non-finite JSON number: {value}")


def canonical_validation_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_object(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"missing or empty retained Lean freeze artifact: {path.name}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_object_keys,
            parse_constant=reject_nonfinite_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid retained Lean freeze artifact JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"retained Lean freeze artifact must be a JSON object: {path.name}")
    return value


def verify(artifact_dir: Path) -> dict[str, object]:
    validation_path = artifact_dir / VALIDATION_FILE
    retained = load_object(validation_path)
    if set(retained) != EXPECTED_FIELDS:
        raise RuntimeError("retained Lean freeze validation field set drift")
    if retained.get("status") != "ok" or retained.get("errors") != []:
        raise RuntimeError("retained Lean freeze validation artifact is not successful")
    if retained.get("basis_objects_verified") is not True:
        raise RuntimeError("retained Lean freeze validation did not verify basis Git objects")

    validator = load_module("retained_lean_observation_validator", VALIDATOR)
    expected = validator.validate()
    if expected.get("status") != "ok" or expected.get("errors") != []:
        raise RuntimeError("canonical Lean freeze validation is not currently successful")
    if expected.get("basis_objects_verified") is not True:
        raise RuntimeError("canonical Lean freeze validation did not verify basis Git objects")
    if retained != expected:
        raise RuntimeError("retained Lean freeze validation full payload drift")
    if validation_path.read_bytes() != canonical_validation_bytes(expected):
        raise RuntimeError("retained Lean freeze validation canonical byte drift")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE],
        "batch_id": retained["batch_id"],
        "theorem_count": retained["theorem_count"],
        "deferred_count": retained["deferred_count"],
        "module_count": retained["module_count"],
        "basis_objects_verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", nargs="?", default="artifacts")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(Path(args.artifact_dir))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("retained Lean observation freeze artifact: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
