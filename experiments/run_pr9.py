#!/usr/bin/env python3
"""Deterministic receipt for the PR #9 observation authority surface."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_observation_specs.py"
EXPERIMENT = ROOT / "experiments/observation/run.py"

FILES = [
    "machine/contract.json",
    "machine/observation_contract.json",
    "machine/observation_specs.json",
    "machine/observation_theorems.json",
    "machine/observation_counterexamples.json",
    "theory/OBSERVATION_CALCULUS.md",
    "scripts/validate_observation_specs.py",
    "experiments/observation/run.py",
    "tests/test_pr9_observation.py",
    "experiments/run_pr9.py",
    "ROADMAP.md",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_suite() -> dict[str, object]:
    validator = load_module("pr9_observation_validator", VALIDATOR)
    experiment = load_module("pr9_observation_experiment", EXPERIMENT)

    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))

    result = experiment.run_suite()
    source_hashes = {path: sha256_bytes((ROOT / path).read_bytes()) for path in sorted(FILES)}
    identity = {
        "type": "uft-id-pr9-observation-receipt",
        "schema_version": "1.0.0",
        "source_sha256": source_hashes,
        "result_sha256": sha256_bytes(canonical_bytes(result)),
        "summary": {
            "spec_count": validation["spec_count"],
            "theorem_count": validation["theorem_count"],
            "counterexample_count": validation["counterexample_count"],
        },
    }
    fingerprint = sha256_bytes(canonical_bytes(identity))
    return {
        **identity,
        "suite_fingerprint_sha256": fingerprint,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": sys.platform,
        },
        "runtime_excluded_from_fingerprint": True,
        "claim_boundary": (
            "OBSERVATIONAL_EQUIVALENCE != PHYSICAL_IDENTITY; "
            "EXACT_RECONSTRUCTION != PHYSICAL_STATE_SURVIVAL; "
            "MATHEMATICALLY_LEAN_READY != REPOSITORY_LEAN_PROVED"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.hash_only:
        print(json.dumps({"suite_fingerprint_sha256": result["suite_fingerprint_sha256"]}, sort_keys=True))
    elif args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("PR9 observation receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
