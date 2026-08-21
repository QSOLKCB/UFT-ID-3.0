#!/usr/bin/env python3
"""Verify retained BridgeCore CI artifacts against live repository authority."""
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
VALIDATOR = ROOT / "scripts/validate_bridge_core.py"
EXPERIMENT = ROOT / "experiments/bridge_core/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_bridge_core.py"

VALIDATION_FILE = "bridge-core-validation.json"
WITNESS_FILE = "bridge-core-witness.json"
RECEIPT_FILE = "bridge-core-receipt.json"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_TOP_LEVEL = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary", "suite_fingerprint_sha256",
    "runtime", "runtime_excluded_from_fingerprint",
}
EXPECTED_RUNTIME_FIELDS = {"python", "implementation", "platform"}
EXPECTED_CLAIM_BOUNDARY = (
    "FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF; "
    "STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION; "
    "BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION"
)
EXPECTED_CORE_FILES = (
    "machine/bridge_core_contract.json",
    "machine/bridge_core_results.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "theory/BRIDGE_CORE.md",
    "theory/AUXILIARY_CONTRACTS.md",
    "scripts/validate_bridge_core.py",
    "scripts/verify_bridge_artifacts.py",
    "experiments/bridge_core/__init__.py",
    "experiments/bridge_core/run.py",
    "tests/test_bridge_core.py",
    "experiments/run_bridge_core.py",
    ".github/workflows/finite-adversarial.yml",
)
EXPECTED_EVIDENCE = (
    "experiments/bridge_core/run.py",
    "tests/test_bridge_core.py",
)
EXPECTED_FILES = tuple(sorted(set(EXPECTED_CORE_FILES) | set(EXPECTED_EVIDENCE)))
FINGERPRINT_FIELDS = (
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "claim_boundary",
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


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
        raise RuntimeError(f"missing or empty BridgeCore artifact: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid BridgeCore artifact JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"BridgeCore artifact must be a JSON object: {path.name}")
    return value


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("bridge_artifact_validator", VALIDATOR)
    expected_validation = validator.validate()
    if expected_validation.get("status") != "ok":
        raise RuntimeError("canonical BridgeCore validation is not currently successful")
    if validation != expected_validation:
        raise RuntimeError("retained BridgeCore validation full payload drift")

    experiment = load_module("bridge_artifact_experiment", EXPERIMENT)
    expected_witness = experiment.run_suite()
    if witness != expected_witness:
        raise RuntimeError("retained BridgeCore witness full payload drift")

    if set(receipt) != EXPECTED_TOP_LEVEL:
        raise RuntimeError("retained BridgeCore receipt top-level schema drift")
    if receipt.get("type") != "uft-id-bridge-core-receipt":
        raise RuntimeError("retained BridgeCore receipt type drift")
    if receipt.get("schema_version") != "1.0.0":
        raise RuntimeError("retained BridgeCore receipt schema drift")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained BridgeCore receipt claim boundary drift")

    runtime = receipt.get("runtime")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME_FIELDS:
        raise RuntimeError("retained BridgeCore runtime schema drift")
    if runtime != expected_runtime:
        raise RuntimeError("retained BridgeCore runtime metadata mismatch")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained BridgeCore runtime fingerprint boundary drift")

    runner = load_module("bridge_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("BridgeCore receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_EVIDENCE:
        raise RuntimeError("BridgeCore receipt runner evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_FILES:
        raise RuntimeError("BridgeCore receipt runner resolved source set drift")

    source_hashes = receipt.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != EXPECTED_FILES:
        raise RuntimeError("retained BridgeCore receipt source file set drift")
    for path in EXPECTED_FILES:
        digest = source_hashes.get(path)
        if not isinstance(digest, str) or HEX64_RE.fullmatch(digest) is None:
            raise RuntimeError(f"retained BridgeCore source digest malformed: {path}")
        if digest != sha256_bytes((ROOT / path).read_bytes()):
            raise RuntimeError(f"retained BridgeCore source digest mismatch: {path}")

    evidence = receipt.get("declared_evidence_paths")
    if not isinstance(evidence, list) or tuple(evidence) != EXPECTED_EVIDENCE:
        raise RuntimeError("retained BridgeCore declared evidence set drift")
    expected_result_hash = sha256_bytes(canonical_bytes(witness))
    if receipt.get("result_sha256") != expected_result_hash:
        raise RuntimeError("retained BridgeCore receipt does not bind witness")

    summary = receipt.get("summary")
    expected_summary = {
        "result_count": 9,
        "hard_boundary_count": 10,
        "relation_triples_checked": 4096,
        "preservation_pairs_checked": 64,
    }
    if summary != expected_summary:
        raise RuntimeError("retained BridgeCore receipt summary drift")

    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64_RE.fullmatch(fingerprint) is None:
        raise RuntimeError("retained BridgeCore receipt fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained BridgeCore receipt fingerprint mismatch")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "relation_triples_checked": 4096,
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
        print("retained BridgeCore artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
