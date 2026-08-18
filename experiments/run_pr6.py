#!/usr/bin/env python3
"""Deterministic receipt for the VOP-2019-MEI reproduction package."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/reproduction/vopson_2019_mei/run.py"

SOURCE_FILES = [
    "research/vopson/reproduction/2019-mei/SOURCE_MAP.md",
    "research/vopson/reproduction/2019-mei/DERIVATION.md",
    "research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json",
    "research/vopson/reproduction/2019-mei/DIMENSIONAL_AUDIT.md",
    "research/vopson/reproduction/2019-mei/CONTROL_MATRIX.md",
    "research/vopson/reproduction/2019-mei/result.json",
    "experiments/reproduction/vopson_2019_mei/fixtures.json",
    "experiments/reproduction/vopson_2019_mei/run.py",
    "tests/test_vopson_2019_mei.py",
    "experiments/run_pr6.py",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def load_reproduction():
    spec = importlib.util.spec_from_file_location("vopson_2019_mei_receipt_target", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load VOP-2019-MEI reproduction")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_suite() -> dict[str, object]:
    module = load_reproduction()
    result = module.run()
    sources = {relative: sha256_bytes((ROOT / relative).read_bytes()) for relative in SOURCE_FILES}
    result_sha = sha256_bytes(canonical_json_bytes(result))
    deterministic = {
        "receipt_version": "1.0.0",
        "source_work_id": "VOP-2019-MEI",
        "source_doi": "10.1063/1.5123794",
        "primary_source_byte_hash": None,
        "primary_source_byte_hash_status": "paper bytes not committed; DOI/page/equation identity used",
        "local_source_sha256": sources,
        "result_sha256": result_sha,
    }
    fingerprint = sha256_bytes(canonical_json_bytes(deterministic))
    return {
        **deterministic,
        "suite_fingerprint_sha256": fingerprint,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "claim_boundary": "RECEIPT_IDENTITY != PHYSICAL_VALIDATION",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()
    receipt = run_suite()
    if args.hash_only:
        print(json.dumps({"suite_fingerprint_sha256": receipt["suite_fingerprint_sha256"]}, sort_keys=True))
    elif args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(receipt["suite_fingerprint_sha256"])


if __name__ == "__main__":
    main()
