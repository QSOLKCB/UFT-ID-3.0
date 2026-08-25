#!/usr/bin/env python3
"""Final compatibility wrapper for the post-tag UFT observation Lean validator.

The combined Codex/Copilot review implementation is preserved byte-for-byte in
``validate_lean_observation_foundation_pr22_combined_review_frozen.py``. This
small layer fixes the live/frozen compatibility boundary:

* exact production projections retain the frozen tracked-object registry and
  overlay the registered post-tag blobs and modes, including mode-only binding
  of this live wrapper so regular-file and symlink checks remain active;
* workflow validation delegates through an independently loaded, hash-checked
  precompiler instead of a mutable nested module alias, preventing recursive
  wrapper re-entry while preserving the historical validator chain.

Historical validators and theorem/source authorities remain unchanged. Public
compatibility hooks are mirrored into the predecessor only while delegated
validation runs, preserving the hostile regression tests without allowing any
private predecessor module handle to overwrite the live wrapper.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "scripts/validate_lean_observation_foundation_pr22_combined_review_frozen.py"
EXPECTED_PREDECESSOR_BLOB = "a5b129c9562faa1d4560d45835af70c21d1ed2de"
SAFE_PRECOMPILER = ROOT / "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py"
EXPECTED_SAFE_PRECOMPILER_BLOB = "bc8cb796d12f84d05a532403df1a6f4d5b161f39"
PREDECESSOR_WORKFLOW_ROUTE = (
    '      - "scripts/validate_lean_observation_foundation_pr22_combined_review_frozen.py"\n'
)


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def predecessor_validator_blob_errors(path: Path = PREDECESSOR) -> list[str]:
    if not path.is_file():
        return ["combined-review Lean validator missing before import"]
    actual = _git_blob_sha(path)
    if actual != EXPECTED_PREDECESSOR_BLOB:
        return [
            "combined-review Lean validator blob drift: "
            f"expected {EXPECTED_PREDECESSOR_BLOB}, got {actual}"
        ]
    return []


def safe_precompiler_blob_errors(path: Path = SAFE_PRECOMPILER) -> list[str]:
    if not path.is_file():
        return ["batch-002 precompiler missing before safe workflow delegation"]
    actual = _git_blob_sha(path)
    if actual != EXPECTED_SAFE_PRECOMPILER_BLOB:
        return [
            "batch-002 precompiler blob drift before safe workflow delegation: "
            f"expected {EXPECTED_SAFE_PRECOMPILER_BLOB}, got {actual}"
        ]
    return []


_preload_errors = predecessor_validator_blob_errors() + safe_precompiler_blob_errors()
if _preload_errors:
    raise RuntimeError("; ".join(_preload_errors))

_spec = importlib.util.spec_from_file_location(
    "lean_observation_pr22_combined_review_frozen", PREDECESSOR
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load combined-review Lean validator: {PREDECESSOR}")
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# Load the exact precompiler under a distinct module object. The preserved
# combined-review module exports nested private compatibility names, so its
# mutable `_impl` alias is intentionally not used as a workflow delegate here.
_safe_spec = importlib.util.spec_from_file_location(
    "lean_observation_pr22_safe_precompiler", SAFE_PRECOMPILER
)
if _safe_spec is None or _safe_spec.loader is None:
    raise RuntimeError(f"cannot load safe batch-002 precompiler: {SAFE_PRECOMPILER}")
_safe_precompiler = importlib.util.module_from_spec(_safe_spec)
_safe_spec.loader.exec_module(_safe_precompiler)

_IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS = _impl.tracked_authority_object_errors
_IMPL_BASIS_GIT_BLOB_SHA = _impl.basis_git_blob_sha
_IMPL_BASIS_SOURCE_OBJECT_ERRORS = _impl.basis_source_object_errors
_IMPL_BASE_VALIDATOR_BLOB_ERRORS = _impl.base_validator_blob_errors
_IMPL_FROZEN_VALIDATOR_BLOB_ERRORS = _impl.frozen_validator_blob_errors
_IMPL_ARTIFACT_VERIFIER_BLOB_ERRORS = _impl.artifact_verifier_blob_errors
_SAFE_PRECOMPILER_WORKFLOW_CONTRACT_ERRORS = _safe_precompiler.workflow_contract_errors
_SAFE_PRECOMPILER_LEAN_WORKFLOW_STEP = _safe_precompiler.LEAN_WORKFLOW_STEP
_COMBINED_PRECOMPILER_WORKFLOW_ROUTE = _impl.PRECOMPILER_WORKFLOW_ROUTE
_COMBINED_FINAL_FROZEN_WORKFLOW_ROUTE = _impl.FINAL_FROZEN_WORKFLOW_ROUTE
_COMBINED_AXIOM_AUDIT_WORKFLOW_ROUTE = _impl.AXIOM_AUDIT_WORKFLOW_ROUTE
_COMBINED_AUDITED_LEAN_WORKFLOW_STEP = _impl.AUDITED_LEAN_WORKFLOW_STEP

_OVERRIDES = {
    "basis_git_blob_sha",
    "basis_source_object_errors",
    "base_validator_blob_errors",
    "frozen_validator_blob_errors",
    "artifact_verifier_blob_errors",
    "tracked_authority_object_errors",
    "workflow_contract_errors",
    "validate_documents",
    "validate",
    "main",
}
# Keep the live wrapper's predecessor handle stable. The predecessor exports a
# private `_impl` compatibility alias of its own; copying that name here would
# silently replace this module's combined-review handle with an older layer.
_COMPAT_EXPORTS = {
    name: getattr(_impl, name)
    for name in dir(_impl)
    if not name.startswith("__")
    and name not in _OVERRIDES
    and name != "_impl"
}
globals().update(_COMPAT_EXPORTS)
_COMPAT_BRIDGE_NAMES = tuple(
    sorted(
        name
        for name in _COMPAT_EXPORTS
        if not name.startswith("_") and name not in _OVERRIDES
    )
)
del _COMPAT_EXPORTS

# Exact post-tag blob identities. The live wrapper itself is intentionally
# mode-only below: a source file cannot embed a stable hash of its own bytes.
# The inherited tracked-object checker still binds that path to the exact HEAD
# tree object and working-tree bytes while enforcing regular-file status.
_LIVE_AUTHORITY_BLOBS = {
    ".github/workflows/vopson-corpus.yml": "9ec2a3f5dc6867f99955488cfc7ffc461e844e1c",
    "README4AI.md": "f9d43b7c04494f59ef69955192aa4b3ddd00f5a0",
    "machine/roadmap_state.json": "f36ee90d004454341300c359aa45b5da2b8ccf33",
    "machine/lean_observation_verification.json": "bfd5b3eec5b8ee1feb6c6d168cf8d82adf0e3c37",
    "scripts/validate_lean_observation_foundation_pr21_final_frozen.py": "42f2a2f30258cf99c1ee0755b54ef33d8d8c0d5f",
    "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py": EXPECTED_SAFE_PRECOMPILER_BLOB,
    "scripts/validate_lean_observation_foundation_pr22_combined_review_frozen.py": EXPECTED_PREDECESSOR_BLOB,
    "scripts/verify_lean_observation_axioms.py": "cf08e73685f2ba7ad7a7b0b96a686c6d3e3e330d",
    "lean-toolchain": "a8afa7d1b02d96f0671eba854a8dc4b416beb473",
    "lakefile.toml": "d124ac10242262e9c9b27c4e7d3efec3e01d8c5e",
    "UFTID.lean": "6b9a25f631ed1b10f05095c04a3e19e8a862cdf8",
    **_impl.EXPECTED_LEAN_SOURCE_BLOBS,
}
_LIVE_AUTHORITY_MODES = {path: "100644" for path in _LIVE_AUTHORITY_BLOBS}
_LIVE_AUTHORITY_MODES["scripts/validate_lean_observation_foundation.py"] = "100755"


def _live_authority_projection() -> tuple[dict[str, str], dict[str, str]]:
    """Overlay registered post-tag identities on the complete frozen registry."""
    blobs = dict(_impl._frozen.EXPECTED_CURRENT_AUTHORITY_BLOBS)
    modes = dict(_impl._frozen.EXPECTED_CURRENT_AUTHORITY_MODES)
    blobs.update(_LIVE_AUTHORITY_BLOBS)
    modes.update(_LIVE_AUTHORITY_MODES)
    return blobs, modes


def _is_exact_production_projection(
    expected_blobs: dict[str, str] | None,
    expected_modes: dict[str, str] | None,
) -> bool:
    return (
        expected_blobs is not None
        and expected_modes is not None
        and dict(expected_blobs) == dict(_impl._frozen.EXPECTED_CURRENT_AUTHORITY_BLOBS)
        and dict(expected_modes) == dict(_impl._frozen.EXPECTED_CURRENT_AUTHORITY_MODES)
    )


def basis_git_blob_sha(relpath: str) -> str | None:
    """Preserve the historical Git-object type mutation hook."""
    previous = _impl.git_object_is_blob
    try:
        _impl.git_object_is_blob = git_object_is_blob
        return _IMPL_BASIS_GIT_BLOB_SHA(relpath)
    finally:
        _impl.git_object_is_blob = previous


def basis_source_object_errors() -> list[str]:
    """Preserve the historical basis-object resolution mutation hook."""
    previous = _impl.basis_git_blob_sha
    try:
        _impl.basis_git_blob_sha = basis_git_blob_sha
        return _IMPL_BASIS_SOURCE_OBJECT_ERRORS()
    finally:
        _impl.basis_git_blob_sha = previous


def base_validator_blob_errors(path: Path = BASE) -> list[str]:
    """Preserve the historical local Git-blob mutation hook."""
    previous = _impl.local_git_blob_sha
    try:
        _impl.local_git_blob_sha = local_git_blob_sha
        return _IMPL_BASE_VALIDATOR_BLOB_ERRORS(path)
    finally:
        _impl.local_git_blob_sha = previous


def frozen_validator_blob_errors(path: Path = FROZEN) -> list[str]:
    """Preserve the historical frozen-validator hash mutation hook."""
    previous = _impl.git_blob_sha
    try:
        _impl.git_blob_sha = git_blob_sha
        return _IMPL_FROZEN_VALIDATOR_BLOB_ERRORS(path)
    finally:
        _impl.git_blob_sha = previous


def artifact_verifier_blob_errors(path: Path = ARTIFACT_VERIFIER) -> list[str]:
    """Preserve the historical retained-artifact hash mutation hook."""
    previous = _impl.local_git_blob_sha
    try:
        _impl.local_git_blob_sha = local_git_blob_sha
        return _IMPL_ARTIFACT_VERIFIER_BLOB_ERRORS(path)
    finally:
        _impl.local_git_blob_sha = previous


def tracked_authority_object_errors(
    root: Path = ROOT,
    *,
    expected_blobs: dict[str, str] | None = None,
    expected_modes: dict[str, str] | None = None,
    runner=subprocess.run,
) -> list[str]:
    if expected_blobs is None and expected_modes is None:
        blobs, modes = _live_authority_projection()
    elif _is_exact_production_projection(expected_blobs, expected_modes):
        blobs, modes = _live_authority_projection()
    else:
        return _IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS(
            root,
            expected_blobs=expected_blobs,
            expected_modes=expected_modes,
            runner=runner,
        )

    return _IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS(
        root,
        expected_blobs=blobs,
        expected_modes=modes,
        runner=runner,
    )


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    if text.count(PREDECESSOR_WORKFLOW_ROUTE) != 2:
        errors.append("registered combined-review Lean-validator workflow route drift")
    projected = text.replace(PREDECESSOR_WORKFLOW_ROUTE, "")

    for route, label in (
        (_COMBINED_PRECOMPILER_WORKFLOW_ROUTE, "batch-002 compatibility-validator"),
        (_COMBINED_FINAL_FROZEN_WORKFLOW_ROUTE, "final frozen-validator"),
        (_COMBINED_AXIOM_AUDIT_WORKFLOW_ROUTE, "axiom-auditor"),
    ):
        if projected.count(route) != 2:
            errors.append(f"registered {label} workflow route drift")
        projected = projected.replace(route, "")

    if projected.count(_COMBINED_AUDITED_LEAN_WORKFLOW_STEP) != 1:
        errors.append("registered Lean build-and-axiom-audit workflow step drift")
    else:
        projected = projected.replace(
            _COMBINED_AUDITED_LEAN_WORKFLOW_STEP,
            _SAFE_PRECOMPILER_LEAN_WORKFLOW_STEP,
            1,
        )

    errors.extend(_SAFE_PRECOMPILER_WORKFLOW_CONTRACT_ERRORS(projected))
    return errors


def _mirror_live_compatibility_hooks() -> dict[str, object]:
    previous: dict[str, object] = {}
    module_globals = globals()
    for name in _COMPAT_BRIDGE_NAMES:
        if hasattr(_impl, name) and name in module_globals:
            previous[name] = getattr(_impl, name)
            setattr(_impl, name, module_globals[name])
    # Wrapper-owned direct hook shims are bridged explicitly because they are
    # excluded from the generic public export set by design.
    for name in (
        "basis_git_blob_sha",
        "basis_source_object_errors",
        "base_validator_blob_errors",
        "frozen_validator_blob_errors",
        "artifact_verifier_blob_errors",
    ):
        previous[name] = getattr(_impl, name)
        setattr(_impl, name, module_globals[name])
    return previous


def _restore_impl_hooks(previous: dict[str, object]) -> None:
    for name, value in previous.items():
        setattr(_impl, name, value)


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
    previous = _mirror_live_compatibility_hooks()
    old_tracked = _impl.tracked_authority_object_errors
    try:
        _impl.tracked_authority_object_errors = tracked_authority_object_errors
        return _impl.validate_documents(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            human,
            roadmap,
            readme,
            check_paths=check_paths,
            require_basis_objects=require_basis_objects,
        )
    finally:
        _impl.tracked_authority_object_errors = old_tracked
        _restore_impl_hooks(previous)


def validate(*, require_basis_objects: bool = True):
    previous = _mirror_live_compatibility_hooks()
    old_tracked = _impl.tracked_authority_object_errors
    old_workflow = _impl.workflow_contract_errors
    try:
        _impl.tracked_authority_object_errors = tracked_authority_object_errors
        _impl.workflow_contract_errors = workflow_contract_errors
        result = _impl.validate(require_basis_objects=require_basis_objects)
    finally:
        _impl.tracked_authority_object_errors = old_tracked
        _impl.workflow_contract_errors = old_workflow
        _restore_impl_hooks(previous)

    errors = list(result.get("errors", []))
    errors.extend(predecessor_validator_blob_errors())
    errors.extend(safe_precompiler_blob_errors())
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
            f"source {SOURCE_TAG}, Lean {LEAN_VERSION}; axiom audit required in build CI)"
        )
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())