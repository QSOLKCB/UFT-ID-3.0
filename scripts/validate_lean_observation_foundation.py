#!/usr/bin/env python3
"""Live validator above the first UFT-OBS-005 arithmetic implementation.

The immediately preceding post-tag validator is preserved byte-for-byte in
``validate_lean_observation_foundation_pr22_batch2_precompiler.py``. This layer
fixes only compatibility plumbing and the exact UFT-OBS-005 documentation
identity check before the pinned Lean compiler is allowed to judge the proof.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRECOMPILER = ROOT / "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py"
EXPECTED_PRECOMPILER_BLOB = "bc8cb796d12f84d05a532403df1a6f4d5b161f39"
PRECOMPILER_WORKFLOW_ROUTE = (
    '      - "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py"\n'
)


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def precompiler_validator_blob_errors(path: Path = PRECOMPILER) -> list[str]:
    if not path.is_file():
        return ["pre-compiler batch-002 validator missing before import"]
    actual = _git_blob_sha(path)
    if actual != EXPECTED_PRECOMPILER_BLOB:
        return [
            "pre-compiler batch-002 validator blob drift: "
            f"expected {EXPECTED_PRECOMPILER_BLOB}, got {actual}"
        ]
    return []


_preload_errors = precompiler_validator_blob_errors()
if _preload_errors:
    raise RuntimeError("; ".join(_preload_errors))

_spec = importlib.util.spec_from_file_location(
    "lean_observation_batch2_precompiler", PRECOMPILER
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load pre-compiler validator: {PRECOMPILER}")
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# Re-export the reviewed compatibility/test surface. Functions that need live
# monkeypatch hooks or changed batch-002 behavior are redefined below.
_OVERRIDES = {
    "validate_documents",
    "validate",
    "main",
    "base_validator_blob_errors",
    "frozen_validator_blob_errors",
    "artifact_verifier_blob_errors",
    "basis_git_blob_sha",
    "basis_source_object_errors",
    "workflow_contract_errors",
    "lean_source_errors",
}
for _name in dir(_impl):
    if not _name.startswith("__") and _name not in _OVERRIDES:
        globals()[_name] = getattr(_impl, _name)

# Preserve the private handles used by the historical hostile regressions.
_base = _impl._base
_frozen = _impl._frozen


def base_validator_blob_errors(path: Path = BASE) -> list[str]:
    if not path.is_file():
        return ["pre-Codex4 PR21 validator missing before import"]
    actual = local_git_blob_sha(path)
    if actual != EXPECTED_BASE_VALIDATOR_BLOB:
        return [
            "pre-Codex4 PR21 validator blob drift: "
            f"expected {EXPECTED_BASE_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def frozen_validator_blob_errors(path: Path = FROZEN) -> list[str]:
    if not path.is_file():
        return ["frozen PR21 validator missing before import"]
    actual = git_blob_sha(path)
    if actual != EXPECTED_FROZEN_VALIDATOR_BLOB:
        return [
            "frozen PR21 validator blob drift: "
            f"expected {EXPECTED_FROZEN_VALIDATOR_BLOB}, got {actual}"
        ]
    return []


def artifact_verifier_blob_errors(path: Path = ARTIFACT_VERIFIER) -> list[str]:
    if not path.is_file():
        return ["Lean observation retained-artifact verifier missing"]
    actual = local_git_blob_sha(path)
    if actual != EXPECTED_ARTIFACT_VERIFIER_BLOB:
        return [
            "Lean observation retained-artifact verifier blob drift: "
            f"expected {EXPECTED_ARTIFACT_VERIFIER_BLOB}, got {actual}"
        ]
    return []


def basis_git_blob_sha(relpath: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{BASIS_COMMIT}:{relpath}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        return None
    return value if git_object_is_blob(value) else None


def basis_source_object_errors() -> list[str]:
    errors: list[str] = []
    resolved = 0
    for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
        actual = basis_git_blob_sha(relpath)
        if actual is None:
            errors.append(f"basis commit blob object unavailable: {BASIS_COMMIT}:{relpath}")
            continue
        resolved += 1
        if actual != expected_sha:
            errors.append(f"basis commit Git blob mismatch: {relpath}")
    if resolved != len(EXPECTED_SOURCE_BLOBS):
        errors.append(
            "complete PR9 basis dependency closure was not resolved from readable Git blob objects"
        )
    return errors


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    if text.count(PRECOMPILER_WORKFLOW_ROUTE) != 2:
        errors.append("registered batch-002 compatibility-validator workflow route drift")
    projected = text.replace(PRECOMPILER_WORKFLOW_ROUTE, "")
    errors.extend(_impl.workflow_contract_errors(projected))
    return errors


def lean_source_errors() -> list[str]:
    # Reuse every previous source guard except the over-broad textual count. The
    # exact theorem heading and exact declaration are each required once.
    errors = [
        error
        for error in _impl.lean_source_errors()
        if error != "UFT-OBS-005 Sampling theorem documentation identity drift"
    ]
    if not LEAN_SAMPLING.is_file():
        return errors
    sampling = LEAN_SAMPLING.read_text(encoding="utf-8")
    heading = "**UFT-OBS-005 — Uniform floor sampling.**"
    if sampling.count(heading) != 1:
        errors.append("UFT-OBS-005 Sampling theorem documentation identity drift")
    return errors


def validate_documents(
    freeze,
    source_theorems,
    source_counterexamples,
    base_contract,
    human,
    roadmap,
    readme,
    *,
    check_paths: bool = True,
    require_basis_objects: bool = False,
):
    # The frozen semantic validator remains authoritative. Basis-object checking
    # is performed in this live layer so historical monkeypatch regressions keep
    # testing the live hook rather than an imported module global.
    old_tracked = _impl.tracked_authority_object_errors
    old_inventory = _impl.tracked_pretag_lean_files
    try:
        _impl.tracked_authority_object_errors = tracked_authority_object_errors
        _impl.tracked_pretag_lean_files = tracked_pretag_lean_files
        result = _impl.validate_documents(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            human,
            roadmap,
            readme,
            check_paths=check_paths,
            require_basis_objects=False,
        )
    finally:
        _impl.tracked_authority_object_errors = old_tracked
        _impl.tracked_pretag_lean_files = old_inventory

    errors = list(result.get("errors", []))
    if require_basis_objects:
        basis_errors = basis_source_object_errors()
        for error in basis_errors:
            if error not in errors:
                errors.append(error)
        result["basis_objects_verified"] = not basis_errors
    else:
        result["basis_objects_verified"] = False
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def validate(*, require_basis_objects: bool = True):
    paths = [
        FREEZE,
        SOURCE_THEOREMS,
        SOURCE_COUNTEREXAMPLES,
        BASE_CONTRACT,
        ROADMAP_STATE,
        HUMAN,
        ROADMAP,
        README4AI,
        WORKFLOW,
        PRETAG_FINAL,
        PRECOMPILER,
        VERIFICATION,
        LEAN_TOOLCHAIN,
        LAKEFILE,
        LEAN_ROOT,
        LEAN_BASIC,
        LEAN_QUOTIENT,
        LEAN_RECONSTRUCTION,
        LEAN_SAMPLING,
        ARTIFACT_VERIFIER,
    ]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        return {
            "status": "error",
            "errors": [f"missing Lean observation authority: {item}" for item in missing],
            "batch_id": None,
            "theorem_count": 0,
            "deferred_count": 0,
            "module_count": 0,
            "basis_objects_verified": False,
        }

    try:
        load_json(ROADMAP_STATE)
    except (OSError, ValueError) as exc:
        return {
            "status": "error",
            "errors": [f"live roadmap state JSON invalid: {exc}"],
            "batch_id": None,
            "theorem_count": 0,
            "deferred_count": 0,
            "module_count": 0,
            "basis_objects_verified": False,
        }

    result = validate_documents(
        load_json(FREEZE),
        load_json(SOURCE_THEOREMS),
        load_json(SOURCE_COUNTEREXAMPLES),
        load_json(BASE_CONTRACT),
        HUMAN.read_text(encoding="utf-8"),
        ROADMAP.read_text(encoding="utf-8"),
        README4AI.read_text(encoding="utf-8"),
        check_paths=True,
        require_basis_objects=require_basis_objects,
    )
    errors = list(result.get("errors", []))
    errors.extend(precompiler_validator_blob_errors())
    errors.extend(predecessor_validator_blob_errors())
    errors.extend(base_validator_blob_errors())
    errors.extend(frozen_validator_blob_errors())
    errors.extend(artifact_verifier_blob_errors())
    errors.extend(workflow_contract_errors(WORKFLOW.read_text(encoding="utf-8")))
    if require_basis_objects:
        errors.extend(source_release_errors())
    errors.extend(verification_record_errors(load_json(VERIFICATION)))
    errors.extend(toolchain_errors())
    errors.extend(lean_source_errors())
    # Preserve deterministic order without duplicate diagnostics from nested
    # compatibility layers.
    errors = list(dict.fromkeys(errors))
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    return result


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(
            "Lean observation implementation: ok "
            f"({result['theorem_count']} frozen batch-001 theorems + UFT-OBS-005 batch 002; "
            f"source {SOURCE_TAG}, Lean {LEAN_VERSION})"
        )
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
