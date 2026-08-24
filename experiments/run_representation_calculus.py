#!/usr/bin/env python3
"""Deterministic receipt for the UFT-ID Representation and Congruence authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_representation_calculus.py"
EXPERIMENT = ROOT / "experiments/representation_calculus/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

CORE_FILES = [
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
    "scripts/validate_representation_calculus_preintegration_frozen.py",
    "scripts/verify_representation_artifacts.py",
    "experiments/representation_calculus/__init__.py",
    "experiments/representation_calculus/run.py",
    "tests/test_representation_calculus.py",
    "experiments/run_representation_calculus.py",
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
    authority = payload.get("representation_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Representation receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("representation_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Representation receipt version registry disagreement")
    return a


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/representation_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Representation result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("Representation result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("Representation evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("Representation evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"Representation receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Representation receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"Representation receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("representation_validator_receipt", VALIDATOR)
    experiment = load_module("representation_experiment_receipt", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    matrices = witness["bounded_checks"]["matrices"]
    receivers = witness["bounded_checks"]["receivers"]
    identity = {
        "type": "uft-id-representation-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "similarity_checks": matrices["similarity_checks"],
            "congruence_rank_checks": matrices["congruence_rank_checks"],
            "orthogonal_frobenius_checks": matrices["orthogonal_frobenius_checks"],
            "coordinate_covariance_checks": matrices["coordinate_covariance_checks"],
            "receiver_equivalence_pair_checks": receivers["receiver_equivalence_pair_checks"],
        },
        "claim_boundary": (
            "FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF; "
            "SIMILARITY != CONGRUENCE; REPRESENTATION_CHANGE != PHYSICAL_CHANGE"
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
        print("Representation receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
