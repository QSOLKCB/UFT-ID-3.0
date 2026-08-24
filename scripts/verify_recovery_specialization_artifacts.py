#!/usr/bin/env python3
"""Verify retained Recovery Specializations CI artifacts against live authority."""
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
VALIDATOR = ROOT / "scripts/validate_recovery_specializations.py"
EXPERIMENT = ROOT / "experiments/recovery_specializations/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_recovery_specializations.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "recovery-specialization-validation.json"
WITNESS_FILE = "recovery-specialization-witness.json"
RECEIPT_FILE = "recovery-specialization-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths", "result_sha256",
    "summary", "claim_boundary", "suite_fingerprint_sha256", "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "GENERIC_RELATION != DETERMINISTIC_SELECTOR; "
    "EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER; "
    "EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY"
)
EXPECTED_CORE_FILES = (
    "machine/recovery_specialization_contract.json",
    "machine/recovery_specialization_results.json",
    "machine/relation_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/RECOVERY_SPECIALIZATIONS.md",
    "theory/RELATION_CALCULUS.md",
    "README4AI.md",
    "docs/CLAIMS.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_recovery_specializations.py",
    "scripts/validate_recovery_specializations_pr17_frozen.py",
    "scripts/verify_recovery_specialization_artifacts.py",
    "experiments/recovery_specializations/__init__.py",
    "experiments/recovery_specializations/run.py",
    "tests/test_recovery_specializations.py",
    "experiments/run_recovery_specializations.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/recovery_specializations/run.py", "tests/test_recovery_specializations.py")
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


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("recovery_specialization_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Recovery Specializations receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("recovery_specialization_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Recovery Specializations receipt version registry disagreement")
    return a


def load_object(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"missing or empty Recovery Specializations artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Recovery Specializations artifact must be object: {path.name}")
    return value


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("recovery_specialization_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical Recovery Specializations validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained Recovery Specializations validation payload drift")

    experiment = load_module("recovery_specialization_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained Recovery Specializations witness payload drift")

    expected_bounded = {
        "selector_graphs": {"carrier_count": 3, "total_selector_count": 32, "right_unique_checks": 32},
        "relation_soundness": {
            "selector_relation_pair_count": 13890,
            "relation_sound_selector_pairs": 4134,
            "fixed_point_normal_exact_pairs": 739,
        },
        "rank_normalization": {"rank_decreasing_selector_count": 9, "state_normalization_checks": 23},
        "lexicographic": {"lexicographic_selection_checks": 336},
    }
    if witness.get("bounded_checks") != expected_bounded:
        raise RuntimeError("retained Recovery Specializations bounded-count drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained Recovery Specializations receipt top-level schema drift")
    if receipt.get("type") != "uft-id-recovery-specialization-receipt":
        raise RuntimeError("retained Recovery Specializations receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained Recovery Specializations receipt registry/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained Recovery Specializations claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained Recovery Specializations runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained Recovery Specializations runtime fingerprint boundary drift")

    runner = load_module("recovery_specialization_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("Recovery Specializations receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("Recovery Specializations receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("Recovery Specializations resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained Recovery Specializations receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed Recovery Specializations source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"Recovery Specializations source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained Recovery Specializations declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained Recovery Specializations receipt does not bind witness")
    expected_summary = {
        "result_count": 10,
        "hard_boundary_count": 9,
        "total_selector_count": 32,
        "selector_relation_pair_count": 13890,
        "relation_sound_selector_pairs": 4134,
        "fixed_point_normal_exact_pairs": 739,
        "rank_decreasing_selector_count": 9,
        "state_normalization_checks": 23,
        "lexicographic_selection_checks": 336,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained Recovery Specializations receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained Recovery Specializations fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained Recovery Specializations fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "total_selector_count": 32,
        "selector_relation_pair_count": 13890,
        "relation_sound_selector_pairs": 4134,
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
        print("retained Recovery Specializations artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
