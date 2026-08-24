#!/usr/bin/env python3
"""Verify retained Epistemic Bridge CI artifacts against live repository authority."""
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
VALIDATOR = ROOT / "scripts/validate_epistemic_bridge.py"
EXPERIMENT = ROOT / "experiments/epistemic_bridge/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_epistemic_bridge.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "epistemic-bridge-validation.json"
WITNESS_FILE = "epistemic-bridge-witness.json"
RECEIPT_FILE = "epistemic-bridge-receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary", "suite_fingerprint_sha256",
    "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = "FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY; STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION; VERIFIED != TRUE"
EXPECTED_CORE_FILES = (
    "machine/epistemic_bridge_contract.json",
    "machine/epistemic_bridge_results.json",
    "machine/bridge_core_contract.json",
    "experiments/bridge_core/run.py",
    "experiments/bridge_core/run_precodex2_frozen.py",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/EPISTEMIC_BRIDGE.md",
    "docs/CLAIMS.md",
    "README4AI.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    "scripts/validate_epistemic_bridge.py",
    "scripts/verify_epistemic_bridge_artifacts.py",
    "experiments/epistemic_bridge/__init__.py",
    "experiments/epistemic_bridge/run.py",
    "tests/test_epistemic_bridge.py",
    "experiments/run_epistemic_bridge.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = ("experiments/epistemic_bridge/run.py", "tests/test_epistemic_bridge.py")
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
        raise RuntimeError(f"missing or empty Epistemic Bridge artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Epistemic Bridge artifact must be object: {path.name}")
    return value


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    authority = payload.get("epistemic_bridge_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Epistemic Bridge receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("epistemic_bridge_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Epistemic Bridge receipt version registry disagreement")
    return a


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("epistemic_artifact_validator", VALIDATOR)
    live_validation = validator.validate()
    if live_validation.get("status") != "ok":
        raise RuntimeError("canonical Epistemic Bridge validation is not successful")
    if validation != live_validation:
        raise RuntimeError("retained Epistemic Bridge validation payload drift")

    experiment = load_module("epistemic_artifact_experiment", EXPERIMENT)
    live_witness = experiment.run_suite()
    if witness != live_witness:
        raise RuntimeError("retained Epistemic Bridge witness payload drift")
    bounded = witness.get("bounded_checks")
    shapes = bounded.get("presence_shapes", {}) if isinstance(bounded, dict) else {}
    operations = bounded.get("operations", {}) if isinstance(bounded, dict) else {}
    if shapes != {"raw_presence_vectors": 64, "valid_normalized_shapes": 33}:
        raise RuntimeError("retained Epistemic Bridge presence count drift")
    if not isinstance(operations, dict) or operations.get("bridgecore_validation_exercised") is not True:
        raise RuntimeError("retained Epistemic Bridge did not exercise production BridgeCore validation")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained Epistemic Bridge receipt top-level schema drift")
    if receipt.get("type") != "uft-id-epistemic-bridge-receipt":
        raise RuntimeError("retained Epistemic Bridge receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained Epistemic Bridge receipt registry/version drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained Epistemic Bridge claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME or runtime != expected_runtime:
        raise RuntimeError("retained Epistemic Bridge runtime provenance drift")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained Epistemic Bridge runtime fingerprint boundary drift")

    runner = load_module("epistemic_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("Epistemic Bridge receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("Epistemic Bridge receipt evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("Epistemic Bridge resolved receipt source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained Epistemic Bridge receipt source set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise RuntimeError(f"malformed Epistemic Bridge source digest: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"Epistemic Bridge source digest mismatch: {path}")

    if receipt.get("declared_evidence_paths") != list(EXPECTED_EVIDENCE):
        raise RuntimeError("retained Epistemic Bridge declared evidence drift")
    if receipt.get("result_sha256") != sha256_bytes(canonical_bytes(witness)):
        raise RuntimeError("retained Epistemic Bridge receipt does not bind witness")
    expected_summary = {
        "result_count": 10,
        "hard_boundary_count": 10,
        "raw_presence_vectors": 64,
        "valid_normalized_shapes": 33,
    }
    if receipt.get("summary") != expected_summary:
        raise RuntimeError("retained Epistemic Bridge receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise RuntimeError("retained Epistemic Bridge fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained Epistemic Bridge fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "raw_presence_vectors": 64,
        "valid_normalized_shapes": 33,
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
        print("retained Epistemic Bridge artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
