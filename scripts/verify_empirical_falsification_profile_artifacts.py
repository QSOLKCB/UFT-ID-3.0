#!/usr/bin/env python3
"""Verify retained Empirical Falsification Profile CI artifacts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_empirical_falsification_profile.py"
EXPERIMENT = ROOT / "experiments/empirical_falsification_profile/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_empirical_falsification_profile.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "empirical-falsification-profile-validation.json"
WITNESS_FILE = "empirical-falsification-profile-witness.json"
RECEIPT_FILE = "empirical-falsification-profile-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths", "result_sha256",
    "summary", "claim_boundary", "suite_fingerprint_sha256", "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION; "
    "FAILURE_TO_REJECT != CONFIRMATION; EMPIRICAL_FIT != UNIQUE_EXPLANATION; "
    "REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION; "
    "PROFILE_FINGERPRINT != PREREGISTRATION_PROOF"
)
EXPECTED_CORE_FILES = (
    "machine/empirical_falsification_profile_contract.json",
    "machine/empirical_falsification_profile_results.json",
    "machine/falsification_contract.json",
    "machine/continuum_stochastic_prevalence_contract.json",
    "machine/continuum_stochastic_prevalence_results.json",
    "machine/recovery_specialization_contract.json",
    "machine/relation_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/EMPIRICAL_FALSIFICATION_PROFILE.md",
    "theory/FALSIFICATION_CONTRACTS.md",
    "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
    "README4AI.md",
    "docs/CLAIMS.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_empirical_falsification_profile.py",
    "scripts/validate_empirical_falsification_profile_pr19_frozen.py",
    "scripts/verify_empirical_falsification_profile_artifacts.py",
    "scripts/validate_continuum_stochastic_prevalence.py",
    "scripts/validate_continuum_stochastic_prevalence_pr18_frozen.py",
    "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "experiments/empirical_falsification_profile/__init__.py",
    "experiments/empirical_falsification_profile/run.py",
    "experiments/continuum_stochastic_prevalence/run.py",
    "tests/test_empirical_falsification_profile.py",
    "tests/test_continuum_stochastic_prevalence.py",
    "experiments/run_empirical_falsification_profile.py",
    "experiments/run_continuum_stochastic_prevalence.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/empirical_falsification_profile/run.py", "tests/test_empirical_falsification_profile.py")
EXPECTED_FILES = tuple(sorted(set(EXPECTED_CORE_FILES) | set(EXPECTED_EVIDENCE)))
FINGERPRINT_FIELDS = ("type", "schema_version", "source_sha256", "declared_evidence_paths", "result_sha256", "summary", "claim_boundary")


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
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Empirical Falsification Profile receipt version registry disagreement")
    return a


def load_object(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"missing or empty EFP artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"EFP artifact must be object: {path.name}")
    return value


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("efp_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical EFP validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained EFP validation payload drift")

    experiment = load_module("efp_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained EFP witness payload drift")
    if witness.get("fixtures") != validator.EXPECTED_FIXTURE_PAYLOADS:
        raise RuntimeError("retained EFP counterexample payload drift")
    if witness.get("bounded_checks") != validator.EXPECTED_BOUNDED:
        raise RuntimeError("retained EFP bounded-count drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained EFP receipt top-level schema drift")
    if receipt.get("type") != "uft-id-empirical-falsification-profile-receipt":
        raise RuntimeError("retained EFP receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained EFP receipt registry/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained EFP claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained EFP runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained EFP runtime fingerprint boundary drift")

    runner = load_module("efp_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("EFP receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("EFP receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("EFP resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained EFP receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed EFP source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"EFP source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained EFP declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained EFP receipt does not bind witness")
    expected_summary = {
        "result_count": 11,
        "hard_boundary_count": 12,
        "valid_decision_checks": 15,
        "rejected_in_scope_cases": 5,
        "not_rejected_in_scope_cases": 7,
        "inconclusive_cases": 3,
        "invalid_evidence_mutation_checks": 60,
        "fit_membership_checks": 15,
        "ambiguous_fit_observations": 3,
        "profile_fingerprint_pair_checks": 3,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained EFP receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained EFP fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained EFP fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "valid_decision_checks": 15,
        "invalid_evidence_mutation_checks": 60,
        "ambiguous_fit_observations": 3,
        "suite_fingerprint_sha256": fingerprint,
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
        print("retained Empirical Falsification Profile artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
