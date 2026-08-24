#!/usr/bin/env python3
"""Deterministic receipt for the Empirical Falsification Profile authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_empirical_falsification_profile.py"
EXPERIMENT = ROOT / "experiments/empirical_falsification_profile/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"
RECEIPT_VERSION = "1.0.0"

CORE_FILES = [
    "machine/empirical_falsification_profile_contract.json",
    "machine/empirical_falsification_profile_results.json",
    "machine/falsification_contract.json",
    "machine/continuum_stochastic_prevalence_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/EMPIRICAL_FALSIFICATION_PROFILE.md",
    "theory/FALSIFICATION_CONTRACTS.md",
    "README4AI.md",
    "docs/CLAIMS.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_empirical_falsification_profile.py",
    "scripts/verify_empirical_falsification_profile_artifacts.py",
    "experiments/empirical_falsification_profile/__init__.py",
    "experiments/empirical_falsification_profile/run.py",
    "tests/test_empirical_falsification_profile.py",
    "experiments/run_empirical_falsification_profile.py",
    ".github/workflows/finite-adversarial.yml",
]


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("empirical_falsification_profile_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Empirical Falsification Profile receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("empirical_falsification_profile_receipt_version")
    if not isinstance(a, str) or not a or a != b or a != RECEIPT_VERSION:
        raise RuntimeError("Empirical Falsification Profile receipt version registry disagreement")
    return a


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/empirical_falsification_profile_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Empirical Falsification Profile result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("Empirical Falsification Profile result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("Empirical Falsification Profile evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("Empirical Falsification Profile evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"Empirical Falsification Profile receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Empirical Falsification Profile receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"Empirical Falsification Profile receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("efp_receipt_validator", VALIDATOR)
    experiment = load_module("efp_receipt_experiment", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    decisions = witness["bounded_checks"]["decisions"]
    invalid = witness["bounded_checks"]["invalid_evidence"]
    fit = witness["bounded_checks"]["fit_nonuniqueness"]
    identity_checks = witness["bounded_checks"]["profile_identity"]
    identity = {
        "type": "uft-id-empirical-falsification-profile-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "valid_decision_checks": decisions["valid_decision_checks"],
            "rejected_in_scope_cases": decisions["rejected_in_scope_cases"],
            "not_rejected_in_scope_cases": decisions["not_rejected_in_scope_cases"],
            "inconclusive_cases": decisions["inconclusive_cases"],
            "invalid_evidence_mutation_checks": invalid["invalid_evidence_mutation_checks"],
            "fit_membership_checks": fit["fit_membership_checks"],
            "ambiguous_fit_observations": fit["ambiguous_fit_observations"],
            "profile_fingerprint_pair_checks": identity_checks["profile_fingerprint_pair_checks"],
        },
        "claim_boundary": (
            "FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION; "
            "FAILURE_TO_REJECT != CONFIRMATION; EMPIRICAL_FIT != UNIQUE_EXPLANATION; "
            "REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION"
        ),
    }
    return {
        **identity,
        "suite_fingerprint_sha256": sha256_bytes(canonical_bytes(identity)),
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": sys.platform,
        },
        "runtime_excluded_from_fingerprint": True,
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
        print("Empirical Falsification Profile receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
