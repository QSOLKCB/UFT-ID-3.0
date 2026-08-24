#!/usr/bin/env python3
"""Deterministic receipt for the UFT-ID Recovery Specializations authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_recovery_specializations.py"
EXPERIMENT = ROOT / "experiments/recovery_specializations/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"
RECEIPT_VERSION = "1.0.0"

CORE_FILES = [
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
    "scripts/verify_recovery_specialization_artifacts.py",
    "experiments/recovery_specializations/__init__.py",
    "experiments/recovery_specializations/run.py",
    "tests/test_recovery_specializations.py",
    "experiments/run_recovery_specializations.py",
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
    authority = payload.get("recovery_specialization_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("Recovery Specializations receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("recovery_specialization_receipt_version")
    if not isinstance(a, str) or not a or a != b or a != RECEIPT_VERSION:
        raise RuntimeError("Recovery Specializations receipt version registry disagreement")
    return a


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/recovery_specialization_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Recovery Specializations result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("Recovery Specializations result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("Recovery Specializations evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("Recovery Specializations evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"Recovery Specializations receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Recovery Specializations receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"Recovery Specializations receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("recovery_specialization_validator_receipt", VALIDATOR)
    experiment = load_module("recovery_specialization_experiment_receipt", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    graphs = witness["bounded_checks"]["selector_graphs"]
    soundness = witness["bounded_checks"]["relation_soundness"]
    rank = witness["bounded_checks"]["rank_normalization"]
    lex = witness["bounded_checks"]["lexicographic"]
    identity = {
        "type": "uft-id-recovery-specialization-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "total_selector_count": graphs["total_selector_count"],
            "selector_relation_pair_count": soundness["selector_relation_pair_count"],
            "relation_sound_selector_pairs": soundness["relation_sound_selector_pairs"],
            "fixed_point_normal_exact_pairs": soundness["fixed_point_normal_exact_pairs"],
            "rank_decreasing_selector_count": rank["rank_decreasing_selector_count"],
            "state_normalization_checks": rank["state_normalization_checks"],
            "lexicographic_selection_checks": lex["lexicographic_selection_checks"],
        },
        "claim_boundary": (
            "GENERIC_RELATION != DETERMINISTIC_SELECTOR; "
            "EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER; "
            "EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY"
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
        print("Recovery Specializations receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
