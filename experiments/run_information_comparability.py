#!/usr/bin/env python3
"""Deterministic receipt for the UFT-ID Information Comparability authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_information_comparability.py"
EXPERIMENT = ROOT / "experiments/information_comparability/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

CORE_FILES = [
    "machine/information_comparability_contract.json",
    "machine/information_comparability_results.json",
    "machine/observation_contract.json",
    "machine/observation_specs.json",
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
    authority = payload.get("information_comparability_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Information Comparability receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("information_comparability_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("Information Comparability receipt version registry disagreement")
    return a


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/information_comparability_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Information Comparability result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("Information Comparability result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("Information Comparability evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("Information Comparability evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"Information Comparability receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Information Comparability receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"Information Comparability receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("information_comparability_validator_receipt", VALIDATOR)
    experiment = load_module("information_comparability_experiment_receipt", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    comparison = witness["bounded_checks"]["comparability"]
    positive = witness["bounded_checks"]["positive_scale"]
    base = witness["bounded_checks"]["log_base_conversion"]
    shared = witness["bounded_checks"]["shared_shannon_primitive"]
    identity = {
        "type": "uft-id-information-comparability-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "information_spec_count": comparison["information_spec_count"],
            "ordered_spec_pair_count": comparison["ordered_spec_pair_count"],
            "directly_comparable_ordered_pairs": comparison["directly_comparable_ordered_pairs"],
            "unit_convertible_ordered_pairs": comparison["unit_convertible_ordered_pairs"],
            "positive_scale_order_checks": positive["positive_scale_order_checks"],
            "log_base_conversion_checks": base["log_base_conversion_checks"],
            "shared_shannon_primitive_checks": shared["shared_shannon_primitive_checks"],
        },
        "claim_boundary": (
            "FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY; "
            "NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE; COMPARABLE != IDENTICAL_SPEC"
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
        print("Information Comparability receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
