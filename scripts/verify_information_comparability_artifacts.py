#!/usr/bin/env python3
"""Verify retained Information Comparability CI artifacts against live authority."""
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
VALIDATOR = ROOT / "scripts/validate_information_comparability.py"
EXPERIMENT = ROOT / "experiments/information_comparability/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_information_comparability.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "information-comparability-validation.json"
WITNESS_FILE = "information-comparability-witness.json"
RECEIPT_FILE = "information-comparability-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary", "suite_fingerprint_sha256",
    "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY; "
    "NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE; COMPARABLE != IDENTICAL_SPEC"
)
EXPECTED_CORE_FILES = (
    "machine/information_comparability_contract.json",
    "machine/information_comparability_results.json",
    "machine/observation_contract.json",
    "machine/representation_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "experiments/lib/information.py",
    "theory/INFORMATION_COMPARABILITY.md",
    "docs/CLAIMS.md",
    "README4AI.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_information_comparability.py",
    "scripts/verify_information_comparability_artifacts.py",
    "experiments/information_comparability/__init__.py",
    "experiments/information_comparability/run.py",
    "tests/test_information_comparability.py",
    "experiments/run_information_comparability.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/information_comparability/run.py", "tests/test_information_comparability.py")
EXPECTED_FILES = tuple(sorted(set(EXPECTED_CORE_FILES) | set(EXPECTED_EVIDENCE)))
FINGERPRINT_FIELDS = (
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary",
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
        raise RuntimeError(f"missing or empty Information Comparability artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Information Comparability artifact must be object: {path.name}")
    return value


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("information_comparability_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Information Comparability receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("information_comparability_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Information Comparability receipt version registry disagreement")
    return a


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("information_comparability_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical Information Comparability validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained Information Comparability validation payload drift")

    experiment = load_module("information_comparability_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained Information Comparability witness payload drift")

    bounded = witness.get("bounded_checks")
    if not isinstance(bounded, dict):
        raise RuntimeError("retained Information Comparability bounded payload missing")
    comparison = bounded.get("comparability")
    positive = bounded.get("positive_scale")
    base = bounded.get("log_base_conversion")
    expected_comparison = {
        "information_spec_count": 96,
        "ordered_spec_pair_count": 9216,
        "directly_comparable_ordered_pairs": 224,
        "unit_convertible_ordered_pairs": 224,
        "reflexive_checks": 96,
        "symmetry_checks": 9216,
        "inverse_conversion_checks": 224,
    }
    if comparison != expected_comparison:
        raise RuntimeError("retained Information Comparability pair-count drift")
    if positive != {"positive_scale_order_checks": 75}:
        raise RuntimeError("retained Information Comparability positive-scale count drift")
    if base != {"log_base_conversion_checks": 5}:
        raise RuntimeError("retained Information Comparability log-base count drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained Information Comparability receipt top-level schema drift")
    if receipt.get("type") != "uft-id-information-comparability-receipt":
        raise RuntimeError("retained Information Comparability receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained Information Comparability receipt registry/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained Information Comparability claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained Information Comparability runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained Information Comparability runtime fingerprint boundary drift")

    runner = load_module("information_comparability_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("Information Comparability receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("Information Comparability receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("Information Comparability resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained Information Comparability receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed Information Comparability source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"Information Comparability source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained Information Comparability declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained Information Comparability receipt does not bind witness")
    expected_summary = {
        "result_count": 10,
        "hard_boundary_count": 11,
        "information_spec_count": 96,
        "ordered_spec_pair_count": 9216,
        "directly_comparable_ordered_pairs": 224,
        "unit_convertible_ordered_pairs": 224,
        "positive_scale_order_checks": 75,
        "log_base_conversion_checks": 5,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained Information Comparability receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained Information Comparability fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained Information Comparability fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "information_spec_count": 96,
        "ordered_spec_pair_count": 9216,
        "directly_comparable_ordered_pairs": 224,
        "unit_convertible_ordered_pairs": 224,
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
        print("retained Information Comparability artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
