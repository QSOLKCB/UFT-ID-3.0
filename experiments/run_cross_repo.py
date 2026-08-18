#!/usr/bin/env python3
"""Run cross-repository finite witnesses and emit a deterministic receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/cross_repo/run.py"
SOURCE_FILES = {
    "experiment_package": ROOT / "experiments/__init__.py",
    "library_package": ROOT / "experiments/lib/__init__.py",
    "information_primitives": ROOT / "experiments/lib/information.py",
    "cross_repo_experiment": EXPERIMENT,
    "pattern_registry": ROOT / "machine/cross_repo_patterns.json",
    "result_registry": ROOT / "machine/cross_repo_results.json",
    "auxiliary_contracts": ROOT / "theory/AUXILIARY_CONTRACTS.md",
    "cross_repo_results": ROOT / "theory/CROSS_REPO_RESULTS.md",
    "receipt_runner": Path(__file__).resolve(),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_suite() -> dict[str, object]:
    module = load_module("uftid_cross_repo", EXPERIMENT)
    results = module.run()
    source_hashes = {
        name: sha256_file(path)
        for name, path in sorted(SOURCE_FILES.items())
    }
    result_sha256 = sha256_bytes(canonical_json_bytes(results))
    deterministic_payload = {
        "source_sha256": source_hashes,
        "result_sha256": result_sha256,
    }
    return {
        "receipt_version": "1.0.0",
        "suite_id": "UFTID3-CROSS-REPO-FORMAL-PATTERNS",
        "deterministic_results": True,
        "random_seed": None,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "source_sha256": source_hashes,
        "result_sha256": result_sha256,
        "suite_fingerprint_sha256": sha256_bytes(canonical_json_bytes(deterministic_payload)),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()
    receipt = run_suite()
    if args.hash_only:
        print(
            json.dumps(
                {
                    "source_sha256": receipt["source_sha256"],
                    "result_sha256": receipt["result_sha256"],
                    "suite_fingerprint_sha256": receipt["suite_fingerprint_sha256"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    elif args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(f"suite: {receipt['suite_id']}")
        print(f"fingerprint: {receipt['suite_fingerprint_sha256']}")
        print(f"result: {receipt['result_sha256']}")


if __name__ == "__main__":
    main()
