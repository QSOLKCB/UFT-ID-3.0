#!/usr/bin/env python3
"""Verify retained Continuum/Stochastic/Prevalence artifacts against live authority."""
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
VALIDATOR = ROOT / "scripts/validate_continuum_stochastic_prevalence.py"
EXPERIMENT = ROOT / "experiments/continuum_stochastic_prevalence/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_continuum_stochastic_prevalence.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "continuum-stochastic-prevalence-validation.json"
WITNESS_FILE = "continuum-stochastic-prevalence-witness.json"
RECEIPT_FILE = "continuum-stochastic-prevalence-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths", "result_sha256",
    "summary", "claim_boundary", "suite_fingerprint_sha256", "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "FINITE_REACHABILITY != INFINITE_PATH_LIVENESS; "
    "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM; "
    "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY"
)
EXPECTED_CORE_FILES = (
    "machine/continuum_stochastic_prevalence_contract.json",
    "machine/continuum_stochastic_prevalence_results.json",
    "machine/recovery_specialization_contract.json",
    "machine/relation_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
    "README4AI.md",
    "docs/CLAIMS.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_continuum_stochastic_prevalence.py",
    "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "experiments/continuum_stochastic_prevalence/__init__.py",
    "experiments/continuum_stochastic_prevalence/run.py",
    "tests/test_continuum_stochastic_prevalence.py",
    "experiments/run_continuum_stochastic_prevalence.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/continuum_stochastic_prevalence/run.py", "tests/test_continuum_stochastic_prevalence.py")
EXPECTED_FILES = tuple(sorted(set(EXPECTED_CORE_FILES) | set(EXPECTED_EVIDENCE)))
FINGERPRINT_FIELDS = (
    "type", "schema_version", "source_sha256", "declared_evidence_paths", "result_sha256", "summary", "claim_boundary",
)


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


def load_object(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"missing or empty CSP artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"CSP artifact must be object: {path.name}")
    return value


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("continuum_stochastic_prevalence_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("CSP receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("continuum_stochastic_prevalence_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("CSP receipt version registry disagreement")
    return a


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("csp_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical CSP validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained CSP validation payload drift")

    experiment = load_module("csp_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained CSP witness payload drift")

    expected_bounded = {
        "finite_kernels": {"finite_kernel_count": 9, "initial_distribution_count": 3, "kernel_transport_checks": 27, "path_mass_evaluations": 756, "path_normalization_checks": 81},
        "finite_atomic_quantifiers": {"finite_atomic_event_checks": 48, "almost_sure_event_cases": 18, "positive_probability_event_cases": 30, "support_witness_event_cases": 30},
        "survival": {"finite_survival_checks": 16, "infinite_survival_zero_controls": 2},
        "prevalence": {"declared_measure_count": 10, "prevalence_measure_event_checks": 80},
        "continuum_nonlifting": {"finite_grid_nonlifting_checks": 31},
    }
    if witness.get("bounded_checks") != expected_bounded:
        raise RuntimeError("retained CSP bounded-count drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained CSP receipt top-level schema drift")
    if receipt.get("type") != "uft-id-continuum-stochastic-prevalence-receipt":
        raise RuntimeError("retained CSP receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained CSP receipt schema/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained CSP claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {"python": platform.python_version(), "implementation": platform.python_implementation(), "platform": sys.platform}
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained CSP runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained CSP runtime fingerprint boundary drift")

    runner = load_module("csp_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("CSP receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("CSP receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("CSP resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained CSP receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed CSP source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"CSP source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained CSP declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained CSP receipt does not bind witness")
    expected_summary = {
        "result_count": 11,
        "hard_boundary_count": 11,
        "finite_kernel_count": 9,
        "kernel_transport_checks": 27,
        "path_mass_evaluations": 756,
        "path_normalization_checks": 81,
        "finite_atomic_event_checks": 48,
        "finite_survival_checks": 16,
        "prevalence_measure_event_checks": 80,
        "finite_grid_nonlifting_checks": 31,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained CSP receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained CSP fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained CSP fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "finite_kernel_count": 9,
        "path_mass_evaluations": 756,
        "prevalence_measure_event_checks": 80,
        "finite_grid_nonlifting_checks": 31,
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
        print("retained CSP artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
