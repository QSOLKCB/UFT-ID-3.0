#!/usr/bin/env python3
"""Deterministic receipt for the graph-realization and typed-incidence authority."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_graph_realization.py"
EXPERIMENT = ROOT / "experiments/graph_realization/run.py"
BASE_CONTRACT = ROOT / "machine/contract.json"

CORE_FILES = [
    "machine/contract.json",
    "machine/relation_contract.json",
    "machine/graph_realization_contract.json",
    "machine/graph_realization_results.json",
    "machine/cross_repo_patterns.json",
    "docs/CLAIMS.md",
    "docs/NONCLAIMS.md",
    "README4AI.md",
    "docs/REPRODUCIBILITY.md",
    "ROADMAP.md",
    ".github/workflows/finite-adversarial.yml",
    "research/GRAPH_REALIZATION_SOURCES.md",
    "theory/RELATION_CALCULUS.md",
    "theory/GRAPH_REALIZATION.md",
    "scripts/validate_graph_realization.py",
    "experiments/relation/run.py",
    "experiments/graph_realization/__init__.py",
    "experiments/graph_realization/run.py",
    "tests/test_graph_realization.py",
    "tests/test_pr11_codex_final4.py",
    "tests/test_pr11_codex_final2.py",
    "experiments/run_graph_realization.py",
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


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("machine/contract.json must be an object")
    authority = payload.get("graph_realization_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("graph receipt version registries must be objects")
    authority_version = authority.get("receipt_version")
    library_version = library.get("graph_realization_receipt_version")
    if not isinstance(authority_version, str) or not authority_version:
        raise RuntimeError("graph authority receipt_version must be a non-empty string")
    if not isinstance(library_version, str) or not library_version:
        raise RuntimeError("graph experiment-library receipt version must be a non-empty string")
    if authority_version != library_version:
        raise RuntimeError("graph receipt version registry disagreement")
    return authority_version


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


def declared_evidence_paths() -> set[str]:
    payload = json.loads(
        (ROOT / "machine/graph_realization_results.json").read_text(encoding="utf-8")
    )
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("graph result registry must contain records list")
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("graph result record must be an object")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list):
            raise RuntimeError("graph result evidence must be a list")
        for path in evidence:
            if not isinstance(path, str) or not path:
                raise RuntimeError("graph result evidence path must be non-empty")
            paths.add(path)
    return paths


def receipt_files() -> list[str]:
    return sorted(
        safe_repo_file(path) for path in (set(CORE_FILES) | declared_evidence_paths())
    )


def run_suite() -> dict[str, object]:
    validator = load_module("graph_realization_validator", VALIDATOR)
    experiment = load_module("graph_realization_experiment", EXPERIMENT)

    validation = validator.validate()
    if validation["status"] != "ok":
        raise RuntimeError("; ".join(validation["errors"]))

    result = experiment.run_suite()
    files = receipt_files()
    source_hashes = {path: sha256_bytes((ROOT / path).read_bytes()) for path in files}
    identity = {
        "type": "uft-id-graph-realization-receipt",
        "schema_version": registered_receipt_version(),
        "source_sha256": source_hashes,
        "declared_evidence_paths": sorted(declared_evidence_paths()),
        "result_sha256": sha256_bytes(canonical_bytes(result)),
        "summary": {
            "result_count": validation["result_count"],
            "source_count": validation["source_count"],
            "hard_boundary_count": validation["boundary_count"],
            "exhaustive_relation_count": result["bounded_exhaustive_check"]["total_relations"],
            "adjacency_pair_checks": result["bounded_exhaustive_check"]["adjacency_pair_checks"],
            "reachability_source_checks": result["bounded_exhaustive_check"]["reachability_source_checks"],
            "scc_partition_checks": result["bounded_exhaustive_check"]["scc_partition_checks"],
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
            "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF; "
            "ALGEBRA != GRAPH != EMBEDDING != PHYSICS; "
            "MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE; "
            "PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.hash_only:
        print(json.dumps(
            {"suite_fingerprint_sha256": result["suite_fingerprint_sha256"]},
            sort_keys=True
        ))
    elif args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("graph realization receipt:", result["suite_fingerprint_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
