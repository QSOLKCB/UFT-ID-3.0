#!/usr/bin/env python3
"""Deterministic receipt for UFT-ID PR #12 BridgeCore."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_bridge_core.py"
EXPERIMENT = ROOT / "experiments/bridge_core/run.py"
RECEIPT_VERSION = "1.0.1"

CORE_FILES = [
    "machine/bridge_core_contract.json",
    "machine/bridge_core_results.json",
    "machine/roadmap_state.json",
    "machine/contract.json",
    "docs/CLAIMS.md",
    "README4AI.md",
    "docs/REPRODUCIBILITY.md",
    "theory/BRIDGE_CORE.md",
    "theory/AUXILIARY_CONTRACTS.md",
    "scripts/validate_bridge_core.py",
    "scripts/verify_bridge_artifacts.py",
    "experiments/bridge_core/__init__.py",
    "experiments/bridge_core/run.py",
    "tests/test_bridge_core.py",
    "experiments/run_bridge_core.py",
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


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/bridge_core_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("BridgeCore result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("BridgeCore result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("BridgeCore evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("BridgeCore evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"BridgeCore receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"BridgeCore receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"BridgeCore receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("bridge_core_validator_receipt", VALIDATOR)
    experiment = load_module("bridge_core_experiment_receipt", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    identity = {
        "type": "uft-id-bridge-core-receipt",
        "schema_version": RECEIPT_VERSION,
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "relation_triples_checked": witness["bounded_checks"]["relation_associativity"]["ordered_relation_triples_checked"],
            "preservation_pairs_checked": witness["bounded_checks"]["preservation_loss"]["ordered_preservation_pairs_checked"],
        },
        "claim_boundary": "FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF; STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION; BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION",
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
        print("BridgeCore receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
