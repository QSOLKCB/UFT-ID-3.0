#!/usr/bin/env python3
"""Verify retained graph-realization CI artifacts after generation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = ROOT / "machine/contract.json"

VALIDATION_FILE = "graph-realization-validation.json"
WITNESS_FILE = "graph-realization-witness.json"
RECEIPT_FILE = "graph-realization-receipt.json"


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


def verify(artifact_dir: Path) -> dict[str, object]:
    validation = load_object(artifact_dir / VALIDATION_FILE)
    witness = load_object(artifact_dir / WITNESS_FILE)
    receipt = load_object(artifact_dir / RECEIPT_FILE)

    if validation.get("status") != "ok" or validation.get("errors") not in ([], None):
        raise RuntimeError("retained graph validation artifact is not successful")

    if witness.get("type") != "uft-id-graph-realization-finite-conformance":
        raise RuntimeError("retained graph witness type drift")
    if witness.get("schema_version") != "1.0.1":
        raise RuntimeError("retained graph witness schema drift")
    exhaustive = witness.get("bounded_exhaustive_check")
    if not isinstance(exhaustive, dict) or exhaustive.get("total_relations") != 530:
        raise RuntimeError("retained graph witness exhaustive-count drift")

    if receipt.get("type") != "uft-id-graph-realization-receipt":
        raise RuntimeError("retained graph receipt type drift")
    if receipt.get("schema_version") != registered_receipt_version():
        raise RuntimeError("retained graph receipt schema/version registry mismatch")
    expected_result_hash = sha256_bytes(canonical_bytes(witness))
    if receipt.get("result_sha256") != expected_result_hash:
        raise RuntimeError("retained graph receipt does not bind retained witness")
    summary = receipt.get("summary")
    if not isinstance(summary, dict) or summary.get("exhaustive_relation_count") != 530:
        raise RuntimeError("retained graph receipt summary drift")
    fingerprint = receipt.get("suite_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise RuntimeError("retained graph receipt fingerprint malformed")

    return {
        "status": "ok",
        "verified_files": [VALIDATION_FILE, WITNESS_FILE, RECEIPT_FILE],
        "exhaustive_relation_count": 530,
        "receipt_schema_version": receipt["schema_version"],
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
