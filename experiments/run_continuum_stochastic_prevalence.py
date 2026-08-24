#!/usr/bin/env python3
"""Deterministic receipt for Continuum/Stochastic/Prevalence obligations."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_continuum_stochastic_prevalence.py"
EXPERIMENT = ROOT / "experiments/continuum_stochastic_prevalence/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

CORE_FILES = [
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
    "scripts/validate_continuum_stochastic_prevalence_pr18_frozen.py",
    "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "experiments/continuum_stochastic_prevalence/__init__.py",
    "experiments/continuum_stochastic_prevalence/run.py",
    "tests/test_continuum_stochastic_prevalence.py",
    "experiments/run_continuum_stochastic_prevalence.py",
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
    authority = payload.get("continuum_stochastic_prevalence_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("CSP receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("continuum_stochastic_prevalence_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("CSP receipt version registry disagreement")
    return a


def declared_evidence_paths() -> set[str]:
    payload = json.loads((ROOT / "machine/continuum_stochastic_prevalence_results.json").read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("CSP result registry must contain records")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("CSP result record malformed")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("CSP evidence paths must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("CSP evidence path malformed")
            paths.add(path)
    return paths


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"CSP receipt path escapes repository: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"CSP receipt path escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"CSP receipt dependency missing: {path}")
    return path


def receipt_files() -> list[str]:
    return sorted(safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths()))


def run_suite() -> dict[str, object]:
    validator = load_module("csp_validator_receipt", VALIDATOR)
    experiment = load_module("csp_experiment_receipt", EXPERIMENT)
    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))
    witness = experiment.run_suite()
    files = receipt_files()
    kernels = witness["bounded_checks"]["finite_kernels"]
    quantifiers = witness["bounded_checks"]["finite_atomic_quantifiers"]
    survival = witness["bounded_checks"]["survival"]
    prevalence = witness["bounded_checks"]["prevalence"]
    continuum = witness["bounded_checks"]["continuum_nonlifting"]
    identity = {
        "type": "uft-id-continuum-stochastic-prevalence-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": {path: sha256_bytes((ROOT / path).read_bytes()) for path in files},
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(witness)),
        "summary": {
            "result_count": validation["result_count"],
            "hard_boundary_count": validation["boundary_count"],
            "finite_kernel_count": kernels["finite_kernel_count"],
            "kernel_transport_checks": kernels["kernel_transport_checks"],
            "path_mass_evaluations": kernels["path_mass_evaluations"],
            "path_normalization_checks": kernels["path_normalization_checks"],
            "finite_atomic_event_checks": quantifiers["finite_atomic_event_checks"],
            "finite_survival_checks": survival["finite_survival_checks"],
            "prevalence_measure_event_checks": prevalence["prevalence_measure_event_checks"],
            "finite_grid_nonlifting_checks": continuum["finite_grid_nonlifting_checks"],
        },
        "claim_boundary": (
            "FINITE_REACHABILITY != INFINITE_PATH_LIVENESS; "
            "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM; "
            "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY"
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
        print("Continuum/Stochastic/Prevalence receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
