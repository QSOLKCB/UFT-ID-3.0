#!/usr/bin/env python3
"""Verify retained graph-realization CI artifacts after generation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = ROOT / "machine/contract.json"

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

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
FINGERPRINT_FIELDS = (
    "type",
    "schema_version",
    "source_sha256",
    "declared_evidence_paths",
    "result_sha256",
    "summary",
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def verify_hash_map(value: object) -> None:
    if not isinstance(value, dict) or not value:
        raise RuntimeError("retained graph receipt source hash map malformed")
    for path, digest in value.items():
        if not isinstance(path, str) or not path:
            raise RuntimeError("retained graph receipt source path malformed")
        if not isinstance(digest, str) or HEX64_RE.fullmatch(digest) is None:
            raise RuntimeError("retained graph receipt source digest malformed")


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

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

    if receipt.get("type") != "uft-id-graph-realization-receipt":
        raise RuntimeError("retained graph receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained graph receipt schema/version registry mismatch")

    expected_result_hash = sha256_bytes(canonical_bytes(witness))
    if receipt.get("result_sha256") != expected_result_hash:
        raise RuntimeError("retained graph receipt does not bind retained witness")

    summary = receipt.get("summary")
    if not isinstance(summary, dict) or summary != EXPECTED_RECEIPT_SUMMARY:
        raise RuntimeError("retained graph receipt summary drift")

    verify_hash_map(receipt.get("source_sha256"))
    evidence_paths = receipt.get("declared_evidence_paths")
    if (
        not isinstance(evidence_paths, list)
        or not evidence_paths
        or any(not isinstance(path, str) or not path for path in evidence_paths)
    ):
        raise RuntimeError("retained graph receipt declared evidence paths malformed")

    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or HEX64_RE.fullmatch(fingerprint) is None:
        raise RuntimeError("retained graph receipt fingerprint malformed")
    expected_fingerprint = sha256_bytes(canonical_bytes(fingerprint_identity(receipt)))
    if fingerprint != expected_fingerprint:
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
