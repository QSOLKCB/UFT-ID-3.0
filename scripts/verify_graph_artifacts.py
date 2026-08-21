#!/usr/bin/env python3
"""Verify retained graph-realization CI artifacts after generation."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = ROOT / "machine/contract.json"
VALIDATOR = ROOT / "scripts/validate_graph_realization.py"
EXPERIMENT = ROOT / "experiments/graph_realization/run.py"
RECEIPT_RUNNER = ROOT / "experiments/run_graph_realization.py"

VALIDATION_FILE = "graph-realization-validation.json"
WITNESS_FILE = "graph-realization-witness.json"
RECEIPT_FILE = "graph-realization-receipt.json"

EXPECTED_BOUNDED_CHECK = {
    "relation_counts": {"Fin1": 2, "Fin2": 16, "Fin3": 512},
    "total_relations": 530,
    "adjacency_pair_checks": 4674,
    "normal_state_checks": 1570,
    "reachability_source_checks": 1570,
    "termination_checks": 530,
    "scc_partition_checks": 530,
    "sink_scc_checks": 530,
    "condensation_checks": 530,
}

EXPECTED_RECEIPT_SUMMARY = {
    "result_count": 9,
    "source_count": 2,
    "hard_boundary_count": 13,
    "exhaustive_relation_count": 530,
    "adjacency_pair_checks": 4674,
    "reachability_source_checks": 1570,
    "scc_partition_checks": 530,
}

EXPECTED_CLAIM_BOUNDARY = (
    "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF; "
    "ALGEBRA != GRAPH != EMBEDDING != PHYSICS; "
    "MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE; "
    "PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY"
)

EXPECTED_RECEIPT_TOP_LEVEL_FIELDS = {
    "type", "schema_version", "source_sha256", "declared_evidence_paths",
    "result_sha256", "summary", "suite_fingerprint_sha256", "runtime",
    "runtime_excluded_from_fingerprint", "claim_boundary",
}
EXPECTED_RUNTIME_FIELDS = {"python", "implementation", "platform"}

EXPECTED_CORE_FILES = (
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
    "scripts/validate_graph_realization_pr11_frozen.py",
    "scripts/verify_graph_artifacts.py",
    "experiments/relation/run.py",
    "experiments/graph_realization/__init__.py",
    "experiments/graph_realization/run.py",
    "tests/test_graph_realization.py",
    "tests/test_pr11_codex_final4.py",
    "tests/test_pr11_codex_final2.py",
    "tests/test_pr11_codex_latest5.py",
    "tests/test_pr11_codex_latest6.py",
    "tests/test_pr11_codex_latest7.py",
    "experiments/run_graph_realization.py",
)
EXPECTED_DECLARED_EVIDENCE_PATHS = (
    "experiments/graph_realization/run.py",
    "tests/test_graph_realization.py",
)
EXPECTED_RECEIPT_FILES = tuple(sorted(set(EXPECTED_CORE_FILES) | set(EXPECTED_DECLARED_EVIDENCE_PATHS)))

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
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
        raise RuntimeError(f"missing or empty retained graph artifact: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid retained graph artifact JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"retained graph artifact must be a JSON object: {path.name}")
    return value


def registered_receipt_version() -> str:
    payload = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("machine/contract.json must be an object")
    authority = payload.get("graph_realization_authority")
    library = payload.get("experiment_library")
    if not isinstance(authority, dict) or not isinstance(library, dict):
        raise RuntimeError("graph receipt registries must be objects")
    a = authority.get("receipt_version")
    b = library.get("graph_realization_receipt_version")
    if not isinstance(a, str) or not a or a != b:
        raise RuntimeError("graph receipt version registry disagreement")
    return a


def fingerprint_identity(receipt: dict[str, object]) -> dict[str, object]:
    return {field: receipt.get(field) for field in FINGERPRINT_FIELDS}


def verify_hash_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise RuntimeError("retained graph receipt source hash map malformed")
    result: dict[str, str] = {}
    for path, digest in value.items():
        if not isinstance(path, str) or not path:
            raise RuntimeError("retained graph receipt source path malformed")
        if not isinstance(digest, str) or HEX64_RE.fullmatch(digest) is None:
            raise RuntimeError("retained graph receipt source digest malformed")
        result[path] = digest
    return result


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    validator = load_module("graph_artifact_validator", VALIDATOR)
    expected_validation = validator.validate()
    if expected_validation.get("status") != "ok":
        raise RuntimeError("canonical graph validation is not currently successful")
    if validation != expected_validation:
        raise RuntimeError("retained graph validation full payload drift")
    if validation.get("status") != "ok" or validation.get("errors") not in ([], None):
        raise RuntimeError("retained graph validation artifact is not successful")
    if validation.get("result_count") != 9 or validation.get("source_count") != 2:
        raise RuntimeError("retained graph validation authority-count drift")
    if validation.get("boundary_count") != 13:
        raise RuntimeError("retained graph validation boundary-count drift")

    if witness.get("type") != "uft-id-graph-realization-finite-conformance":
        raise RuntimeError("retained graph witness type drift")
    if witness.get("schema_version") != "1.0.1":
        raise RuntimeError("retained graph witness schema drift")
    exhaustive = witness.get("bounded_exhaustive_check")
    if not isinstance(exhaustive, dict) or exhaustive != EXPECTED_BOUNDED_CHECK:
        raise RuntimeError("retained graph witness bounded-check payload drift")

    experiment = load_module("graph_artifact_experiment", EXPERIMENT)
    expected_witness = experiment.run_suite()
    if witness != expected_witness:
        raise RuntimeError("retained graph witness full payload drift")

    if set(receipt) != EXPECTED_RECEIPT_TOP_LEVEL_FIELDS:
        raise RuntimeError("retained graph receipt top-level schema drift")
    runtime = receipt.get("runtime")
    if not isinstance(runtime, dict) or set(runtime) != EXPECTED_RUNTIME_FIELDS:
        raise RuntimeError("retained graph receipt runtime schema drift")
    expected_runtime = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": sys.platform,
    }
    if runtime != expected_runtime:
        raise RuntimeError("retained graph receipt runtime provenance mismatch")
    if receipt.get("type") != "uft-id-graph-realization-receipt":
        raise RuntimeError("retained graph receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained graph receipt schema/version registry mismatch")
    if receipt.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise RuntimeError("retained graph receipt claim boundary drift")
    expected_result_hash = sha256_bytes(canonical_bytes(witness))
    if receipt.get("result_sha256") != expected_result_hash:
        raise RuntimeError("retained graph receipt does not bind retained witness")
    if receipt.get("summary") != EXPECTED_RECEIPT_SUMMARY:
        raise RuntimeError("retained graph receipt summary drift")

    runner = load_module("graph_artifact_receipt_runner", RECEIPT_RUNNER)
    if tuple(runner.CORE_FILES) != EXPECTED_CORE_FILES:
        raise RuntimeError("graph receipt runner core source set drift")
    if tuple(sorted(runner.declared_evidence_paths())) != EXPECTED_DECLARED_EVIDENCE_PATHS:
        raise RuntimeError("graph receipt runner declared evidence set drift")
    if tuple(runner.receipt_files()) != EXPECTED_RECEIPT_FILES:
        raise RuntimeError("graph receipt runner resolved source set drift")

    source_hashes = verify_hash_map(receipt.get("source_sha256"))
    if tuple(sorted(source_hashes)) != EXPECTED_RECEIPT_FILES:
        raise RuntimeError("retained graph receipt source file set drift")
    for path in EXPECTED_RECEIPT_FILES:
        actual = sha256_bytes((ROOT / path).read_bytes())
        if source_hashes[path] != actual:
            raise RuntimeError(f"retained graph receipt source digest mismatch: {path}")

    evidence_paths = receipt.get("declared_evidence_paths")
    if not isinstance(evidence_paths, list) or tuple(evidence_paths) != EXPECTED_DECLARED_EVIDENCE_PATHS:
        raise RuntimeError("retained graph receipt declared evidence path set drift")

    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64_RE.fullmatch(fingerprint) is None:
        raise RuntimeError("retained graph receipt fingerprint malformed")
    if fingerprint != sha256_bytes(canonical_bytes(fingerprint_identity(receipt))):
        raise RuntimeError("retained graph receipt fingerprint mismatch")
    if receipt.get("runtime_excluded_from_fingerprint") is not True:
        raise RuntimeError("retained graph receipt runtime fingerprint boundary drift")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "exhaustive_relation_count": 530,
        "receipt_schema_version": receipt["schema_version"],
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
        print("retained graph artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
