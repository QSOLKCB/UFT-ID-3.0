#!/usr/bin/env python3
"""Live post-tag validator for the UFT observation Lean implementation.

Historical v3.0.0 source-freeze semantics remain delegated to the exact
pre-compiler compatibility layer. This live layer binds the post-tag theorem
sources, records imported foundational axioms, synchronizes live scheduling
surfaces, and projects only the explicitly superseded README phase prose back
to its historical form when exercising the frozen validator.
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
AXIOM_AUDITOR = ROOT / "scripts/verify_lean_observation_axioms.py"
EXPECTED_AXIOM_AUDITOR_BLOB = "cf08e73685f2ba7ad7a7b0b96a686c6d3e3e330d"
EXPECTED_LIVE_README_BLOB = "f9d43b7c04494f59ef69955192aa4b3ddd00f5a0"
EXPECTED_LIVE_ROADMAP_STATE_BLOB = "f36ee90d004454341300c359aa45b5da2b8ccf33"

PRECOMPILER_WORKFLOW_ROUTE = (
    '      - "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py"\n'
)
FINAL_FROZEN_WORKFLOW_ROUTE = (
    '      - "scripts/validate_lean_observation_foundation_pr21_final_frozen.py"\n'
)
AXIOM_AUDIT_WORKFLOW_ROUTE = '      - "scripts/verify_lean_observation_axioms.py"\n'


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

_OVERRIDES = {
    "validate_documents",
    "validate",
    "main",
    "base_validator_blob_errors",
    "frozen_validator_blob_errors",
    "artifact_verifier_blob_errors",
    "basis_git_blob_sha",
    "basis_source_object_errors",
    "tracked_authority_object_errors",
    "workflow_contract_errors",
    "expected_verification_record",
    "verification_record_errors",
    "lean_source_errors",
}
_COMPAT_EXPORTS = {
    name: getattr(_impl, name)
    for name in dir(_impl)
    if not name.startswith("__") and name not in _OVERRIDES
}
globals().update(_COMPAT_EXPORTS)
del _COMPAT_EXPORTS

_base = _impl._base
_frozen = _impl._frozen
_IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS = _impl.tracked_authority_object_errors

EXPECTED_LEAN_SOURCE_BLOBS = {
    "UFTID/Observation/Basic.lean": "55dbd9c883e2b3c15acc90f6f6f4085117d5d5ee",
    "UFTID/Observation/Quotient.lean": "a1e62ca0f439c00e79d3c68866708fadc4acff0b",
    "UFTID/Observation/Reconstruction.lean": "248c535cbafb7d0b83ba62e391578978ffdebd18",
    "UFTID/Observation/Sampling.lean": "d587ff9321dc7f3a8f5cb40fe6e9e1aa49c37ebc",
}

LEGACY_EFP_PHASE = (
    "The completed planned PR #18 surface defines a synthetic conformance procedure for deciding "
    "whether a calibrated profile-matched evidence record crosses one versioned scoped rejection "
    "boundary. It specializes the PR8 `FalsificationSpec` scaffold without converting synthetic "
    "fixtures, matching hashes, or procedural labels into empirical evidence or preregistration "
    "proof. Live scheduling authority is PR #10 Lean observation foundation: the first theorem "
    "batch and dependency graph are frozen, and the active phase is the post-merge release gate "
    "for exact merged-main validation plus immutable source tagging before Lean implementation."
)
LIVE_EFP_PHASE = (
    "The completed planned PR #18 surface defines a synthetic conformance procedure for deciding "
    "whether a calibrated profile-matched evidence record crosses one versioned scoped rejection "
    "boundary. It specializes the PR8 `FalsificationSpec` scaffold without converting synthetic "
    "fixtures, matching hashes, or procedural labels into empirical evidence or preregistration "
    "proof. Historical scheduling authority for the v3.0.0 source freeze remains PR #10 Lean "
    "observation foundation. Live post-tag authority is now `machine/roadmap_state.json` plus "
    "`machine/lean_observation_verification.json`: immutable tag `v3.0.0` is cut at "
    "`b7f51590985e60920c8b09fc9238b8aec6cfa3bc`, `LEAN-OBS-BATCH-001` implements "
    "`UFT-OBS-001` through `004`, and arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`; "
    "both remain `IMPLEMENTED_PENDING_CI` until the pinned build and axiom audit are green."
)
LEGACY_HARD_RULE_8 = "8. Lean verification requires checked source and green CI."
LIVE_HARD_RULE_8 = (
    "8. Lean verification requires checked source, exact source binding, an explicit "
    "imported-axiom report, and green pinned CI."
)
LEGACY_LEAN_SECTION = """## Lean

PR #10 Lean observation foundation is active. Source batch `LEAN-OBS-BATCH-001` is frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; `UFT-OBS-005` remains deferred to a later arithmetic-focused batch.

No Lean proof object is claimed by this freeze. Lean/Lake/Mathlib remain unpinned. After PR #21 merges, the next gate is exact merged-`main` CI plus hostile review, then tag that exact merged commit/tree before Lean proof implementation. QSOL-CONTEXT target binding and Zenodo publication remain later ordered gates in `ROADMAP.md`.

Canonical source-freeze surfaces:

```text
machine/lean_observation_foundation_contract.json
theory/LEAN_OBSERVATION_FOUNDATION.md
scripts/validate_lean_observation_foundation.py
tests/test_lean_observation_foundation.py
```

```text
MATHEMATICAL_PROOF != LEAN_PROOF
SOURCE_THEOREM != LEAN_ARTIFACT
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
```
"""
LIVE_LEAN_SECTION = """## Lean

PR #10 Lean observation foundation is the historical source-freeze authority. Source batch `LEAN-OBS-BATCH-001` remains frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; the same v3.0.0 freeze records `UFT-OBS-005` as deferred from batch 001 rather than dropped.

Live post-tag implementation authority is `machine/lean_observation_verification.json`. Immutable source tag `v3.0.0` resolves to commit `b7f51590985e60920c8b09fc9238b8aec6cfa3bc` and tree `966bdf47596832f792e77d619b33222f4cf60c8d`. Lean is pinned to `v4.33.1`, mathlib to `0df444a360eaa60ab8c11dca51a86af692955474`, and the Lean release archive is SHA256-bound. `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`; arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`. Current status is `IMPLEMENTED_PENDING_CI`, not `LEAN_VERIFIED`: promotion requires exact source-blob binding, successful `lake build UFTID`, hostile review, and the retained `#print axioms` audit.

Canonical source-freeze and live implementation surfaces:

```text
machine/lean_observation_foundation_contract.json
machine/lean_observation_verification.json
machine/roadmap_state.json
theory/LEAN_OBSERVATION_FOUNDATION.md
scripts/validate_lean_observation_foundation.py
scripts/verify_lean_observation_axioms.py
tests/test_lean_observation_foundation.py
```

```text
MATHEMATICAL_PROOF != LEAN_PROOF
SOURCE_THEOREM != LEAN_ARTIFACT
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
IMPORTED_AXIOM != UFT_ID_THEOREM_RESULT
```
"""

AUDITED_LEAN_WORKFLOW_STEP = '''
      - name: Build Lean observation formalization
        if: matrix.python-version == '3.12'
        env:
          UFT_LEAN_URL: https://github.com/leanprover/lean4/releases/download/v4.33.1/lean-4.33.1-linux.tar.zst
          UFT_LEAN_SHA256: 890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235
        run: |
          set -euo pipefail
          archive="$RUNNER_TEMP/lean-4.33.1-linux.tar.zst"
          install_dir="$RUNNER_TEMP/lean-4.33.1"
          curl --fail --location --retry 3 --output "$archive" "$UFT_LEAN_URL"
          printf '%s  %s\\n' "$UFT_LEAN_SHA256" "$archive" | sha256sum --check -
          mkdir -p "$install_dir"
          tar --zstd -xf "$archive" -C "$install_dir" --strip-components=1
          export PATH="$install_dir/bin:$PATH"
          lean --version
          lake --version
          lake update
          lake exe cache get
          lake build UFTID
          mkdir -p artifacts
          python scripts/verify_lean_observation_axioms.py --lake "$install_dir/bin/lake" --json-out artifacts/lean-observation-axioms.json
'''


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


def tracked_authority_object_errors(
    root: Path = ROOT,
    *,
    expected_blobs: dict[str, str] | None = None,
    expected_modes: dict[str, str] | None = None,
    runner=subprocess.run,
) -> list[str]:
    if expected_blobs is not None or expected_modes is not None:
        return _IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS(
            root,
            expected_blobs=expected_blobs,
            expected_modes=expected_modes,
            runner=runner,
        )
    blobs = dict(_frozen.EXPECTED_CURRENT_AUTHORITY_BLOBS)
    for relpath in (
        ".github/workflows/vopson-corpus.yml",
        "README4AI.md",
        "machine/roadmap_state.json",
    ):
        blobs.pop(relpath, None)
    return _IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS(
        root,
        expected_blobs=blobs,
        expected_modes=dict(_frozen.EXPECTED_CURRENT_AUTHORITY_MODES),
        runner=runner,
    )


def live_authority_object_errors() -> list[str]:
    checks = (
        (README4AI, EXPECTED_LIVE_README_BLOB, "README4AI live Lean phase"),
        (ROADMAP_STATE, EXPECTED_LIVE_ROADMAP_STATE_BLOB, "live roadmap state"),
        (AXIOM_AUDITOR, EXPECTED_AXIOM_AUDITOR_BLOB, "Lean axiom auditor"),
    )
    errors: list[str] = []
    for path, expected, label in checks:
        if not path.is_file():
            errors.append(f"{label} missing")
            continue
        actual = _git_blob_sha(path)
        if actual != expected:
            errors.append(f"{label} blob drift: expected {expected}, got {actual}")
    return errors


def _legacy_readme_projection(text: str) -> str:
    projected = text
    projected = projected.replace(LIVE_EFP_PHASE, LEGACY_EFP_PHASE, 1)
    projected = projected.replace(LIVE_HARD_RULE_8, LEGACY_HARD_RULE_8, 1)
    projected = projected.replace(LIVE_LEAN_SECTION, LEGACY_LEAN_SECTION, 1)
    # The frozen v3.0.0 README intentionally had no terminal newline. The live
    # README now has one, so remove it only from this historical projection.
    return projected.rstrip("\n")


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    for route, label in (
        (PRECOMPILER_WORKFLOW_ROUTE, "batch-002 compatibility-validator"),
        (FINAL_FROZEN_WORKFLOW_ROUTE, "final frozen-validator"),
        (AXIOM_AUDIT_WORKFLOW_ROUTE, "axiom-auditor"),
    ):
        if text.count(route) != 2:
            errors.append(f"registered {label} workflow route drift")
        text = text.replace(route, "")
    if text.count(AUDITED_LEAN_WORKFLOW_STEP) != 1:
        errors.append("registered Lean build-and-axiom-audit workflow step drift")
    else:
        text = text.replace(AUDITED_LEAN_WORKFLOW_STEP, _impl.LEAN_WORKFLOW_STEP, 1)
    errors.extend(_impl.workflow_contract_errors(text))
    return errors


def expected_verification_record() -> dict[str, object]:
    return {
        "type": "uft-id-lean-observation-verification",
        "schema_version": "1.2.0",
        "status": "IMPLEMENTED_PENDING_CI",
        "source_release": {
            "tag": SOURCE_TAG,
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
        },
        "toolchain": {
            "lean": LEAN_VERSION,
            "mathlib_commit": MATHLIB_COMMIT,
            "lean_archive_url": LEAN_ARCHIVE_URL,
            "lean_archive_sha256": LEAN_ARCHIVE_SHA256,
        },
        "batches": [
            {
                "batch_id": "LEAN-OBS-BATCH-001",
                "theorem_ids": ["UFT-OBS-001", "UFT-OBS-002", "UFT-OBS-003", "UFT-OBS-004"],
                "source_freeze_status": "FROZEN_IN_V3.0.0",
                "implementation_status": "IMPLEMENTED_PENDING_CI",
            },
            {
                "batch_id": "LEAN-OBS-BATCH-002",
                "theorem_ids": ["UFT-OBS-005"],
                "source_freeze_status": "DEFERRED_FROM_BATCH_001_IN_V3.0.0",
                "implementation_status": "IMPLEMENTED_PENDING_CI",
            },
        ],
        "theorems": [
            {
                "id": "UFT-OBS-001",
                "module": "UFTID.Observation.Basic",
                "path": "UFTID/Observation/Basic.lean",
                "declaration": "uft_obs_001_observational_equivalence",
                "source_blob_sha": EXPECTED_LEAN_SOURCE_BLOBS["UFTID/Observation/Basic.lean"],
            },
            {
                "id": "UFT-OBS-002",
                "module": "UFTID.Observation.Quotient",
                "path": "UFTID/Observation/Quotient.lean",
                "declaration": "uft_obs_002_quotient_to_image",
                "source_blob_sha": EXPECTED_LEAN_SOURCE_BLOBS["UFTID/Observation/Quotient.lean"],
            },
            {
                "id": "UFT-OBS-003",
                "module": "UFTID.Observation.Reconstruction",
                "path": "UFTID/Observation/Reconstruction.lean",
                "declaration": "uft_obs_003_image_reconstruction_iff_injective",
                "source_blob_sha": EXPECTED_LEAN_SOURCE_BLOBS["UFTID/Observation/Reconstruction.lean"],
            },
            {
                "id": "UFT-OBS-004",
                "module": "UFTID.Observation.Reconstruction",
                "path": "UFTID/Observation/Reconstruction.lean",
                "declaration": "uft_obs_004_noninjective_no_global_left_inverse",
                "source_blob_sha": EXPECTED_LEAN_SOURCE_BLOBS["UFTID/Observation/Reconstruction.lean"],
            },
            {
                "id": "UFT-OBS-005",
                "module": "UFTID.Observation.Sampling",
                "path": "UFTID/Observation/Sampling.lean",
                "declaration": "uft_obs_005_uniform_floor_sampling",
                "source_blob_sha": EXPECTED_LEAN_SOURCE_BLOBS["UFTID/Observation/Sampling.lean"],
            },
        ],
        "axiom_audit": {
            "command": "python scripts/verify_lean_observation_axioms.py",
            "status": "CI_REQUIRED_BEFORE_LEAN_VERIFIED",
            "allowed_axioms": ["Classical.choice", "Quot.sound", "propext"],
            "required_axioms_by_theorem": {
                "UFT-OBS-001": [],
                "UFT-OBS-002": [],
                "UFT-OBS-003": ["Classical.choice"],
                "UFT-OBS-004": ["Classical.choice"],
                "UFT-OBS-005": [],
            },
        },
        "source_freeze_deferred_theorem_ids": ["UFT-OBS-005"],
        "current_deferred_theorem_ids": [],
        "hard_boundaries": [
            "LEAN_PROOF != EMPIRICAL_VALIDATION",
            "LEAN_PROOF != PHYSICAL_ONTOLOGY",
            "UFT-OBS-005_DEFERRED_IN_BATCH_001 != UFT-OBS-005_DROPPED",
            "LATER_LEAN_BATCH != RETROACTIVE_SOURCE_FREEZE_REWRITE",
            "REGISTERED_DECLARATION_NAME != THEOREM_IDENTITY_WITHOUT_SOURCE_BINDING",
            "IMPORTED_AXIOM != UFT_ID_THEOREM_RESULT",
        ],
    }


def verification_record_errors(record: dict[str, object]) -> list[str]:
    if record != expected_verification_record():
        return ["Lean observation implementation verification record drift"]
    return []


def _strip_lean_comments(text: str) -> str:
    """Replace Lean line/block comments with whitespace while preserving lines.

    Lean block comments nest. Keeping newlines and replacing other comment
    bytes with spaces means later command matching remains line-oriented without
    letting docstrings or comments masquerade as declarations.
    """
    chars = list(text)
    i = 0
    depth = 0
    while i < len(chars):
        if depth == 0 and i + 1 < len(chars) and chars[i] == "-" and chars[i + 1] == "-":
            chars[i] = " "
            chars[i + 1] = " "
            i += 2
            while i < len(chars) and chars[i] != "\n":
                chars[i] = " "
                i += 1
            continue
        if i + 1 < len(chars) and chars[i] == "/" and chars[i + 1] == "-":
            depth += 1
            chars[i] = " "
            chars[i + 1] = " "
            i += 2
            continue
        if depth > 0 and i + 1 < len(chars) and chars[i] == "-" and chars[i + 1] == "/":
            depth -= 1
            chars[i] = " "
            chars[i + 1] = " "
            i += 2
            continue
        if depth > 0 and chars[i] != "\n":
            chars[i] = " "
        i += 1
    return "".join(chars)


def _has_assumption_command(text: str) -> bool:
    code = _strip_lean_comments(text)
    command = re.compile(
        r"(?m)^\s*(?:(?:private|protected|unsafe|noncomputable)\s+)*(?:axiom|constant)\b"
    )
    return command.search(code) is not None


def lean_source_errors() -> list[str]:
    errors = [
        error
        for error in _impl.lean_source_errors()
        if error != "UFT-OBS-005 Sampling theorem documentation identity drift"
        and not error.startswith("Lean proof escape hatch forbidden: axiom in ")
    ]
    if LEAN_SAMPLING.is_file():
        sampling = LEAN_SAMPLING.read_text(encoding="utf-8")
        heading = "**UFT-OBS-005 — Uniform floor sampling.**"
        if sampling.count(heading) != 1:
            errors.append("UFT-OBS-005 Sampling theorem documentation identity drift")

    for relpath, expected_sha in EXPECTED_LEAN_SOURCE_BLOBS.items():
        path = ROOT / relpath
        if not path.is_file():
            errors.append(f"registered theorem source missing: {relpath}")
            continue
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            errors.append(
                f"registered theorem source blob drift: {relpath}: "
                f"expected {expected_sha}, got {actual_sha}"
            )
        text = path.read_text(encoding="utf-8")
        if _has_assumption_command(text):
            errors.append(f"Lean undeclared assumption command forbidden in {relpath}")
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
            _legacy_readme_projection(readme),
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
        AXIOM_AUDITOR,
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
    errors.extend(live_authority_object_errors())
    errors.extend(workflow_contract_errors(WORKFLOW.read_text(encoding="utf-8")))
    if require_basis_objects:
        errors.extend(source_release_errors())
    errors.extend(verification_record_errors(load_json(VERIFICATION)))
    errors.extend(toolchain_errors())
    errors.extend(lean_source_errors())
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
