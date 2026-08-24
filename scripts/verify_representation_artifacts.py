#!/usr/bin/env python3
"""Verify retained Representation CI artifacts against live repository authority."""
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
VALIDATOR = ROOT / "scripts/validate_representation_calculus.py"
EXPERIMENT = ROOT / "experiments/representation_calculus/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_representation_calculus.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "representation-validation.json"
WITNESS_FILE = "representation-witness.json"
RECEIPT_FILE = "representation-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary", "suite_fingerprint_sha256",
    "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF; "
    "SIMILARITY != CONGRUENCE; REPRESENTATION_CHANGE != PHYSICAL_CHANGE"
)
EXPECTED_CORE_FILES = (
    "machine/representation_contract.json",
    "machine/representation_results.json",
    "machine/observation_contract.json",
    "machine/bridge_core_contract.json",
    "machine/epistemic_bridge_contract.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/REPRESENTATION_CALCULUS.md",
    "docs/CLAIMS.md",
    "README4AI.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_representation_calculus.py",
    "scripts/verify_representation_artifacts.py",
    "experiments/representation_calculus/__init__.py",
    "experiments/representation_calculus/run.py",
    "tests/test_representation_calculus.py",
    "experiments/run_representation_calculus.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/representation_calculus/run.py", "tests/test_representation_calculus.py")
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
        raise RuntimeError(f"missing or empty Representation artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Representation artifact must be object: {path.name}")
    return value


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("representation_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Representation receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("representation_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Representation receipt version registry disagreement")
    return a


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("representation_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical Representation validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained Representation validation payload drift")

    experiment = load_module("representation_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained Representation witness payload drift")

    matrices = witness.get("bounded_checks", {}).get("matrices", {}) if isinstance(witness.get("bounded_checks"), dict) else {}
    receivers = witness.get("bounded_checks", {}).get("receivers", {}) if isinstance(witness.get("bounded_checks"), dict) else {}
    expected_matrices = {
        "matrix_count": 81,
        "unimodular_transform_count": 40,
        "orthogonal_transform_count": 8,
        "similarity_checks": 3240,
        "congruence_rank_checks": 3240,
        "orthogonal_frobenius_checks": 648,
        "coordinate_covariance_checks": 29160,
    }
    expected_receivers = {
        "fin3_function_count": 27,
        "receiver_function_pairs": 729,
        "injective_on_image_receiver_pairs": 441,
        "receiver_equivalence_pair_checks": 3969,
    }
    if matrices != expected_matrices:
        raise RuntimeError("retained Representation matrix battery count drift")
    if receivers != expected_receivers:
        raise RuntimeError("retained Representation receiver battery count drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained Representation receipt top-level schema drift")
    if receipt.get("type") != "uft-id-representation-receipt":
        raise RuntimeError("retained Representation receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained Representation receipt registry/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained Representation claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained Representation runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained Representation runtime fingerprint boundary drift")

    runner = load_module("representation_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("Representation receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("Representation receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("Representation resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained Representation receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed Representation source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"Representation source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained Representation declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained Representation receipt does not bind witness")
    expected_summary = {
        "result_count": 10,
        "hard_boundary_count": 10,
        "similarity_checks": 3240,
        "congruence_rank_checks": 3240,
        "orthogonal_frobenius_checks": 648,
        "coordinate_covariance_checks": 29160,
        "receiver_equivalence_pair_checks": 3969,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained Representation receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained Representation fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained Representation fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "similarity_checks": 3240,
        "coordinate_covariance_checks": 29160,
        "receiver_equivalence_pair_checks": 3969,
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
        print("retained Representation artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
