#!/usr/bin/env python3
"""Deterministic receipt for the planned PR #11 relation/selection authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_relation_core.py"
EXPERIMENT = ROOT / "experiments/relation/run.py"

CORE_FILES = [
    "machine/contract.json",
    "machine/roadmap_state.json",
    "machine/relation_contract.json",
    "machine/relation_theorems.json",
    "machine/relation_counterexamples.json",
    "machine/genus_selection_specimen.json",
    "machine/cross_repo_patterns.json",
    "theory/RELATION_CALCULUS.md",
    "scripts/validate_relation_core.py",
    "experiments/relation/run.py",
    "tests/test_pr11_relation_core.py",
    "experiments/run_pr11.py",
    "ROADMAP.md",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_repo_file(path: str) -> str:
    rel = Path(path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError(f"receipt dependency must remain repository-relative: {path}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"receipt dependency escapes repository: {path}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"receipt dependency does not exist: {path}")
    return path


def evidence_paths_from_records(
    theorems: dict[str, object],
    counterexamples: dict[str, object],
    selection: dict[str, object],
) -> set[str]:
    paths: set[str] = set()
    theorem_records = theorems.get("records", [])
    counterexample_records = counterexamples.get("records", [])
    selection_evidence = selection.get("evidence", [])
    if not isinstance(theorem_records, list) or not isinstance(counterexample_records, list):
        raise RuntimeError("relation evidence registries must contain record lists")
    if not isinstance(selection_evidence, list):
        raise RuntimeError("selection evidence must be a list")

    for record in theorem_records:
        if not isinstance(record, dict):
            raise RuntimeError("relation theorem evidence record must be an object")
        evidence = record.get("executable_evidence", [])
        if not isinstance(evidence, list):
            raise RuntimeError("relation theorem executable_evidence must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("relation theorem evidence path must be non-empty")
            paths.add(path)

    for record in counterexample_records:
        if not isinstance(record, dict):
            raise RuntimeError("relation counterexample evidence record must be an object")
        evidence = record.get("evidence", [])
        if not isinstance(evidence, list):
            raise RuntimeError("relation counterexample evidence must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("relation counterexample evidence path must be non-empty")
            paths.add(path)

    for path in selection_evidence:
        if not isinstance(path, str) or not path:
            raise RuntimeError("selection evidence path must be non-empty")
        paths.add(path)
    return paths


def declared_evidence_paths() -> set[str]:
    theorems = json.loads((ROOT / "machine/relation_theorems.json").read_text(encoding="utf-8"))
    counterexamples = json.loads((ROOT / "machine/relation_counterexamples.json").read_text(encoding="utf-8"))
    selection = json.loads((ROOT / "machine/genus_selection_specimen.json").read_text(encoding="utf-8"))
    return evidence_paths_from_records(theorems, counterexamples, selection)


def receipt_files() -> list[str]:
    paths = set(CORE_FILES) | declared_evidence_paths()
    return sorted(safe_repo_file(path) for path in paths)


def run_suite() -> dict[str, object]:
    validator = load_module("pr11_relation_validator", VALIDATOR)
    experiment = load_module("pr11_relation_experiment", EXPERIMENT)

    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))

    result = experiment.run_suite()
    files = receipt_files()
    source_hashes = {path: sha256_bytes((ROOT / path).read_bytes()) for path in files}
    identity = {
        "type": "uft-id-pr11-relation-selection-receipt",
        "schema_version": "1.0.1",
        "source_sha256": source_hashes,
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(result)),
        "summary": {
            "theorem_count": validation["theorem_count"],
            "counterexample_count": validation["counterexample_count"],
            "public_context_ref_count": validation["public_context_ref_count"],
            "exhaustive_relation_count": result["bounded_exhaustive_check"]["total_relations"],
        },
    }
    fingerprint = sha256_bytes(canonical_bytes(identity))
    return {
        **identity,
        "suite_fingerprint_sha256": fingerprint,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": sys.platform,
        },
        "runtime_excluded_from_fingerprint": True,
        "claim_boundary": (
            "FINITE_CONFORMANCE != GENERAL_PROOF; "
            "COMPATIBILITY != UNIQUE_SELECTION; "
            "INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION; "
            "MATHEMATICAL_PROOF != LEAN_PROOF"
        ),
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
        print("PR11 relation/selection receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
