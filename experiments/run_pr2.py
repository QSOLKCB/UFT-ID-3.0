#!/usr/bin/env python3
"""Run the finite adversarial suite and emit a reproducibility receipt."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPERIMENTS = {
    "finite_entropy_signs": ROOT / "experiments/counterexamples/finite_entropy_signs/run.py",
    "coarse_graining_reversal": ROOT / "experiments/representation/coarse_graining/run.py",
    "vopson_2026_polygon_extremum": ROOT / "experiments/reproduction/vopson_2026_polygons/run.py",
}

SOURCE_FILES = {
    **EXPERIMENTS,
    "shared_information_primitives": ROOT / "experiments/lib/information.py",
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
    signs = load_module("pr2_signs", EXPERIMENTS["finite_entropy_signs"])
    coarse = load_module("pr2_coarse", EXPERIMENTS["coarse_graining_reversal"])
    polygon = load_module("pr2_polygon", EXPERIMENTS["vopson_2026_polygon_extremum"])

    results = {
        "finite_entropy_signs": signs.run(),
        "coarse_graining_reversal": coarse.run(),
        "vopson_2026_polygon_extremum": polygon.run(max_N=16, max_n=6),
    }

    result_hashes = {
        name: sha256_bytes(canonical_json_bytes(result))
        for name, result in results.items()
    }
    source_hashes = {
        name: sha256_file(path)
        for name, path in sorted(SOURCE_FILES.items())
    }
    deterministic_payload = {
        "source_sha256": source_hashes,
        "result_sha256": result_hashes,
    }

    return {
        "receipt_version": "1.1.0",
        "suite_id": "UFTID3-FINITE-ADVERSARIAL",
        "deterministic_results": True,
        "random_seed": None,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "source_sha256": source_hashes,
        "script_sha256": {
            name: source_hashes[name]
            for name in EXPERIMENTS
        },
        "result_sha256": result_hashes,
        "suite_fingerprint_sha256": sha256_bytes(
            canonical_json_bytes(deterministic_payload)
        ),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit the full receipt as JSON")
    parser.add_argument("--hash-only", action="store_true", help="emit only deterministic hashes")
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
        for name, digest in receipt["result_sha256"].items():
            print(f"{name}: {digest}")


if __name__ == "__main__":
    main()
