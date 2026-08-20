#!/usr/bin/env python3
"""Deterministic receipt for the PR #8 formalization authority surface."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_formalization_contracts.py"
EXPERIMENT = ROOT / "experiments/formalization/run.py"

FILES = [
    "machine/contract.json",
    "machine/formalization_contract.json",
    "machine/invariant_specs.json",
    "machine/assurance_graph.json",
    "machine/definition_obligations.json",
    "machine/falsification_contract.json",
    "machine/cross_repo_patterns.json",
    "theory/INVARIANT_CALCULUS.md",
    "theory/ASSURANCE.md",
    "theory/DEFINITION_OBLIGATIONS.md",
    "theory/FALSIFICATION_CONTRACTS.md",
    "scripts/validate_formalization_contracts.py",
    "experiments/__init__.py",
    "experiments/lib/__init__.py",
    "experiments/lib/information.py",
    "experiments/formalization/run.py",
    "tests/test_pr8_formalization.py",
    "experiments/run_pr8.py",
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
    validator = load_module("pr8_formalization_validator", VALIDATOR)
    experiment = load_module("pr8_formalization_experiment", EXPERIMENT)

    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))

    result = experiment.run_suite()
    source_hashes = {path: sha256_bytes((ROOT / path).read_bytes()) for path in sorted(FILES)}
    identity = {
        "type": "uft-id-pr8-formalization-receipt",
        "schema_version": "1.0.2",
        "source_sha256": source_hashes,
        "result_sha256": sha256_bytes(canonical_bytes(result)),
        "summary": {
            "invariant_count": validation["invariant_count"],
            "assurance_node_count": validation["assurance_node_count"],
            "definition_obligation_count": validation["definition_obligation_count"],
            "model_obligation_count": validation["model_obligation_count"],
            "falsification_example_count": validation["falsification_example_count"],
            "roadmap_deferred_surface_count": validation["roadmap_deferred_surface_count"],
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
            "FORMAL_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION; "
            "MODEL_OUTPUT != EXECUTION_EVIDENCE; "
            "NAMED_OBJECT != WELL_DEFINED_OBJECT"
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
        print("PR8 formalization receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
