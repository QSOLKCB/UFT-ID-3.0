#!/usr/bin/env python3
"""Run the PR #2 finite adversarial suite and emit a reproducibility receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]

EXPERIMENTS = {
    "finite_entropy_signs": ROOT / "experiments/counterexamples/finite_entropy_signs/run.py",
    "coarse_graining_reversal": ROOT / "experiments/representation/coarse_graining/run.py",
    "vopson_2026_polygon_extremum": ROOT / "experiments/reproduction/vopson_2026_polygons/run.py",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_suite() -> dict[str, object]:
    signs = load_module("pr2_signs", EXPERIMENTS["finite_entropy_signs"])
    coarse = load_module("pr2_coarse", EXPERIMENTS["coarse_graining_reversal"])
    polygon = load_module("pr2_polygon", EXPERIMENTS["vopson_2026_polygon_extremum"])

    results = {
        "finite_entropy_signs": signs.run(),
        "coarse_graining_reversal": coarse.run(),
        "vopson_2026_polygon_extremum": polygon.run(max_N=16, max_n=6),
    }

    result_hashes = {
        name: sha256_bytes(canonical_json_bytes(result)) for name, result in results.items()
    }
    script_hashes = {name: sha256_file(path) for name, path in EXPERIMENTS.items()}

    return {
        "receipt_version": "1.0.0",
        "suite_id": "UFTID3-PR2-FINITE-ADVERSARIAL",
        "deterministic_results": True,
        "random_seed": None,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "script_sha256": script_hashes,
        "result_sha256": result_hashes,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit the full receipt as JSON")
    parser.add_argument("--hash-only", action="store_true", help="emit only result hashes")
    args = parser.parse_args()
    receipt = run_suite()
    if args.hash_only:
        print(json.dumps(receipt["result_sha256"], indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"suite: {receipt['suite_id']}")
        for name, digest in receipt["result_sha256"].items():
            print(f"{name}: {digest}")


if __name__ == "__main__":
    main()
