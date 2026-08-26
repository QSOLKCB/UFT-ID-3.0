#!/usr/bin/env python3
"""Promote the merged UFT observation Lean package to LEAN_VERIFIED.

The exact green merged-main implementation validator is preserved byte-for-byte
in ``validate_lean_observation_foundation_pr22_merged_frozen.py``. This outer
layer adds only the post-merge verification state. Exact canonical verified
surfaces are projected back to the reviewed pending-CI state while the frozen
validator chain replays; mutated or partial surfaces are never projected.

The immutable ``v3.0.0`` source release remains the theorem/source authority.
The later PR #22 merge commit is a formalization-integration identity, not a
replacement source release.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "scripts/validate_lean_observation_foundation_pr22_merged_frozen.py"
EXPECTED_PREDECESSOR_BLOB = "498b28b08a51e87fcf7f69ea52582cb8ad8be114"
PREDECESSOR_WORKFLOW_ROUTE = (
    '      - "scripts/validate_lean_observation_foundation_pr22_merged_frozen.py"\n'
)

INTEGRATION_COMMIT = "bbcde19827921af4490c232bdc1edc401790d89e"
INTEGRATION_TREE = "b7ec78695f32a5b1cf78b416a5050627ad4f957d"
FINAL_PR_HEAD = "c32aaff36219961e3ec2a4e479ccdec521795bbe"
CODEX_REVIEWED_COMMIT = "111a9c7a0b6d26c999eb941f9c25f5c0f5176ed5"
FINITE_RUN_ID = 32876623204
VOPSON_RUN_ID = 32876623479
VOPSON_LEAN_JOB_ID = 97895966100

EXPECTED_VERIFIED_README_BLOB = "a7ba82abb0c7cd5dde0abdcf038d9925281fd888"
EXPECTED_VERIFIED_ROADMAP_BLOB = "599b2ec26bfdda61c31a23466e7c77252fa7b860"
EXPECTED_VERIFIED_ROADMAP_STATE_BLOB = "97f276f4e079e79af1e394d233ec337ffd981bca"
EXPECTED_VERIFIED_RECORD_BLOB = "f39ad92f6522886d4449e938cd50cec669364930"
EXPECTED_VERIFIED_WORKFLOW_BLOB = "626e44c3855a1de2be055fa31ba3ee35e6a9dafd"
EXPECTED_VERIFIED_AXIOM_AUDITOR_BLOB = "368cf82e2b44220fee105a987002c027ec2e7425"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _text_git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def predecessor_validator_blob_errors(path: Path = PREDECESSOR) -> list[str]:
    if not path.is_file():
        return ["merged-main PR22 Lean validator missing before promotion import"]
    actual = _git_blob_sha(path)
    if actual != EXPECTED_PREDECESSOR_BLOB:
        return [
            "merged-main PR22 Lean validator blob drift: "
            f"expected {EXPECTED_PREDECESSOR_BLOB}, got {actual}"
        ]
    return []


_preload_errors = predecessor_validator_blob_errors()
if _preload_errors:
    raise RuntimeError("; ".join(_preload_errors))

_spec = importlib.util.spec_from_file_location(
    "lean_observation_pr22_merged_frozen", PREDECESSOR
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load merged-main PR22 validator: {PREDECESSOR}")
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# The predecessor intentionally owns the reviewed implementation/compatibility
# machinery. Capture stable callables before any temporary mutation hooks.
_combined = _impl._impl
_IMPL_VALIDATE = _impl.validate
_IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS = _impl.tracked_authority_object_errors
_IMPL_WORKFLOW_CONTRACT_ERRORS = _impl.workflow_contract_errors
_IMPL_LOAD_JSON = _impl.load_json
_IMPL_LIVE_AUTHORITY_OBJECT_ERRORS = _impl.live_authority_object_errors
_IMPL_EXPECTED_VERIFICATION_RECORD = _impl.expected_verification_record
_IMPL_VERIFICATION_RECORD_ERRORS = _impl.verification_record_errors
_IMPL_BASIS_GIT_BLOB_SHA = _impl.basis_git_blob_sha
_IMPL_BASIS_SOURCE_OBJECT_ERRORS = _impl.basis_source_object_errors
_IMPL_BASE_VALIDATOR_BLOB_ERRORS = _impl.base_validator_blob_errors
_IMPL_FROZEN_VALIDATOR_BLOB_ERRORS = _impl.frozen_validator_blob_errors
_IMPL_ARTIFACT_VERIFIER_BLOB_ERRORS = _impl.artifact_verifier_blob_errors
_COMBINED_VALIDATE_DOCUMENTS = _combined.validate_documents

_OVERRIDES = {
    "PREDECESSOR",
    "EXPECTED_PREDECESSOR_BLOB",
    "PREDECESSOR_WORKFLOW_ROUTE",
    "basis_git_blob_sha",
    "basis_source_object_errors",
    "base_validator_blob_errors",
    "frozen_validator_blob_errors",
    "artifact_verifier_blob_errors",
    "expected_verification_record",
    "verification_record_errors",
    "load_json",
    "live_authority_object_errors",
    "tracked_authority_object_errors",
    "workflow_contract_errors",
    "validate_documents",
    "validate",
    "main",
}
# Export only the predecessor's public compatibility surface. Private
# predecessor names such as its captured `_IMPL_*` callables must never replace
# this promotion layer's own stable handles.
_COMPAT_EXPORTS = {
    name: getattr(_impl, name)
    for name in dir(_impl)
    if not name.startswith("_") and name not in _OVERRIDES
}
globals().update(_COMPAT_EXPORTS)
_COMPAT_BRIDGE_NAMES = tuple(sorted(_COMPAT_EXPORTS))
del _COMPAT_EXPORTS

# Public current-authority constants describe the verified live checkout. The
# historical PR #22 hashes remain asserted by the explicit reverse-projection
# regression rather than masquerading as the current raw surfaces.
EXPECTED_LIVE_README_BLOB = EXPECTED_VERIFIED_README_BLOB
EXPECTED_CLAIM_SURFACE_BLOBS = dict(EXPECTED_CLAIM_SURFACE_BLOBS)
EXPECTED_CLAIM_SURFACE_BLOBS["README4AI"] = EXPECTED_VERIFIED_README_BLOB
EXPECTED_CLAIM_SURFACE_BLOBS["ROADMAP"] = EXPECTED_VERIFIED_ROADMAP_BLOB

PENDING_ROADMAP_STATUS = "active-post-tag-lean-implementation-ci-hardening"
VERIFIED_ROADMAP_STATUS = "active-lean-verified-awaiting-context-and-archive"
PENDING_ROADMAP_NOTE = (
    "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, "
    "Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, EFP, and the v3.0.0 Lean "
    "source-freeze authorities retain their historical semantics. This file is the live post-tag schedule "
    "authority: immutable source tag v3.0.0 resolves to b7f51590985e60920c8b09fc9238b8aec6cfa3bc; "
    "LEAN-OBS-BATCH-001 implements UFT-OBS-001 through UFT-OBS-004 and LEAN-OBS-BATCH-002 implements "
    "UFT-OBS-005. Both remain IMPLEMENTED_PENDING_CI until the pinned Lean build, source binding, hostile "
    "review, and axiom audit are green."
)
VERIFIED_ROADMAP_NOTE = (
    "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, "
    "Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, EFP, and the v3.0.0 Lean "
    "source-freeze authorities retain their historical semantics. This file is the live post-tag schedule "
    "authority: immutable source tag v3.0.0 resolves to b7f51590985e60920c8b09fc9238b8aec6cfa3bc; "
    "LEAN-OBS-BATCH-001 implements UFT-OBS-001 through UFT-OBS-004 and LEAN-OBS-BATCH-002 implements UFT-OBS-005. "
    "Both are LEAN_VERIFIED at formalization integration commit bbcde19827921af4490c232bdc1edc401790d89e, tree "
    "b7ec78695f32a5b1cf78b416a5050627ad4f957d, after exact merged-main finite-adversarial run 32876623204 and "
    "vopson-corpus run 32876623479 succeeded. The next ordered gate is QSOL-CONTEXT verification capture, then "
    "DOI/archive work."
)
PENDING_ROADMAP_RULE = (
    "The v3.0.0 source freeze remains immutable and historically records UFT-OBS-005 as deferred from batch 001; "
    "live post-tag implementation may proceed only against that exact tag, with pinned Lean/Lake/Mathlib, exact "
    "source binding, checked compilation, and explicit imported-axiom auditing before any LEAN_VERIFIED promotion."
)
VERIFIED_ROADMAP_RULE = (
    "The v3.0.0 source freeze remains immutable and historically records UFT-OBS-005 as deferred from batch 001; "
    "LEAN_VERIFIED is bound to that exact tag, pinned Lean/Lake/Mathlib, exact theorem-source identities, merged-main "
    "build and validation at bbcde19827921af4490c232bdc1edc401790d89e, and the explicit imported-axiom audit. "
    "Later changes require a new versioned verification state rather than rewriting this evidence."
)

PENDING_EFP_PHASE = (
    "The completed planned PR #18 surface defines a synthetic conformance procedure for deciding whether a calibrated "
    "profile-matched evidence record crosses one versioned scoped rejection boundary. It specializes the PR8 "
    "`FalsificationSpec` scaffold without converting synthetic fixtures, matching hashes, or procedural labels into "
    "empirical evidence or preregistration proof. Historical scheduling authority for the v3.0.0 source freeze "
    "remains PR #10 Lean observation foundation. Live post-tag authority is now `machine/roadmap_state.json` plus "
    "`machine/lean_observation_verification.json`: immutable tag `v3.0.0` is cut at "
    "`b7f51590985e60920c8b09fc9238b8aec6cfa3bc`, `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`, "
    "and arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`; both remain `IMPLEMENTED_PENDING_CI` until the "
    "pinned build and axiom audit are green."
)
VERIFIED_EFP_PHASE = (
    "The completed planned PR #18 surface defines a synthetic conformance procedure for deciding whether a calibrated "
    "profile-matched evidence record crosses one versioned scoped rejection boundary. It specializes the PR8 "
    "`FalsificationSpec` scaffold without converting synthetic fixtures, matching hashes, or procedural labels into "
    "empirical evidence or preregistration proof. Historical scheduling authority for the v3.0.0 source freeze "
    "remains PR #10 Lean observation foundation. Live post-tag authority is now `machine/roadmap_state.json` plus "
    "`machine/lean_observation_verification.json`: immutable tag `v3.0.0` is cut at "
    "`b7f51590985e60920c8b09fc9238b8aec6cfa3bc`, `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`, "
    "and arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`; both are `LEAN_VERIFIED` at formalization "
    "integration commit `bbcde19827921af4490c232bdc1edc401790d89e`, tree "
    "`b7ec78695f32a5b1cf78b416a5050627ad4f957d`, after exact merged-main `finite-adversarial` run `32876623204` "
    "and `vopson-corpus` run `32876623479` succeeded. The next ordered gate is QSOL-CONTEXT verification capture, "
    "then DOI/archive work."
)

PENDING_LEAN_IMPLEMENTATION_PARAGRAPH = (
    "Live post-tag implementation authority is `machine/lean_observation_verification.json`. Immutable source tag "
    "`v3.0.0` resolves to commit `b7f51590985e60920c8b09fc9238b8aec6cfa3bc` and tree "
    "`966bdf47596832f792e77d619b33222f4cf60c8d`. Lean is pinned to `v4.33.1`, mathlib to "
    "`0df444a360eaa60ab8c11dca51a86af692955474`, and the Lean release archive is SHA256-bound. "
    "`LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`; arithmetic `LEAN-OBS-BATCH-002` implements "
    "`UFT-OBS-005`. Current status is `IMPLEMENTED_PENDING_CI`, not `LEAN_VERIFIED`: promotion requires exact "
    "source-blob binding, successful `lake build UFTID`, hostile review, and the retained `#print axioms` audit."
)
VERIFIED_LEAN_IMPLEMENTATION_PARAGRAPH = (
    "Live post-tag verification authority is `machine/lean_observation_verification.json`. Immutable source tag "
    "`v3.0.0` resolves to commit `b7f51590985e60920c8b09fc9238b8aec6cfa3bc` and tree "
    "`966bdf47596832f792e77d619b33222f4cf60c8d`. Lean is pinned to `v4.33.1`, mathlib to "
    "`0df444a360eaa60ab8c11dca51a86af692955474`, and the Lean release archive is SHA256-bound. "
    "`LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`; arithmetic `LEAN-OBS-BATCH-002` implements "
    "`UFT-OBS-005`. Both batches are `LEAN_VERIFIED`, bound to formalization integration commit "
    "`bbcde19827921af4490c232bdc1edc401790d89e`, tree `b7ec78695f32a5b1cf78b416a5050627ad4f957d`, "
    "exact merged-main `finite-adversarial` run `32876623204`, and exact merged-main `vopson-corpus` run "
    "`32876623479`. The pinned Python 3.12 Vopson lane completed `lake build UFTID` successfully and the retained "
    "kernel `#print axioms` audit passed. This verified scholarly layer does not rewrite the immutable `v3.0.0` "
    "source release. The next ordered gate is QSOL-CONTEXT verification capture, then DOI/archive work."
)
PENDING_READ_NEXT_45 = "45. `experiments/run_empirical_falsification_profile.py`"
VERIFIED_READ_NEXT_45 = "45. `experiments/empirical_falsification_profile/run.py`"

VERIFIED_ROADMAP_LIVE_NOTE = """## Post-merge Lean verification state: LEAN_VERIFIED

The PR #10 observation formalization track is now `LEAN_VERIFIED` against immutable source release `v3.0.0`. `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `UFT-OBS-004`; separately registered arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`. The historical `v3.0.0` batch-001 record that deferred `UFT-OBS-005` is preserved and is not a current deferral.

Formalization integration is GitHub PR #22, merged at `bbcde19827921af4490c232bdc1edc401790d89e` with tree `b7ec78695f32a5b1cf78b416a5050627ad4f957d`. Exact merged-`main` `finite-adversarial` run `32876623204` and `vopson-corpus` run `32876623479` both succeeded. The pinned Python 3.12 Vopson lane completed `lake build UFTID` successfully and the kernel-backed imported-axiom audit passed.

The next ordered gate is to advance the existing QSOL-CONTEXT formalization target binding through `LEAN_VERIFIED`, then proceed to DOI reservation and deterministic archive construction. The older PR #10 status/checklist prose retained below predates the completed formalization and remains only as historical compatibility text; it does not override this live state or `machine/roadmap_state.json`.

```text
SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER
LEAN_PROOF != EMPIRICAL_VALIDATION
LEAN_PROOF != PHYSICAL_ONTOLOGY
IMPORTED_AXIOM != UFT_ID_THEOREM_RESULT
```

"""


def basis_git_blob_sha(relpath: str) -> str | None:
    """Preserve the predecessor's Git-object mutation hook at the live layer."""
    previous = _impl.git_object_is_blob
    try:
        _impl.git_object_is_blob = git_object_is_blob
        return _IMPL_BASIS_GIT_BLOB_SHA(relpath)
    finally:
        _impl.git_object_is_blob = previous


def basis_source_object_errors() -> list[str]:
    """Preserve direct basis-resolution hostile-test injection."""
    previous = _impl.basis_git_blob_sha
    try:
        _impl.basis_git_blob_sha = basis_git_blob_sha
        return _IMPL_BASIS_SOURCE_OBJECT_ERRORS()
    finally:
        _impl.basis_git_blob_sha = previous


def base_validator_blob_errors(path: Path = BASE) -> list[str]:
    """Preserve direct local-Git-blob hostile-test injection."""
    previous = _impl.local_git_blob_sha
    try:
        _impl.local_git_blob_sha = local_git_blob_sha
        return _IMPL_BASE_VALIDATOR_BLOB_ERRORS(path)
    finally:
        _impl.local_git_blob_sha = previous


def frozen_validator_blob_errors(path: Path = FROZEN) -> list[str]:
    """Preserve direct frozen-validator hash hostile-test injection."""
    previous = _impl.git_blob_sha
    try:
        _impl.git_blob_sha = git_blob_sha
        return _IMPL_FROZEN_VALIDATOR_BLOB_ERRORS(path)
    finally:
        _impl.git_blob_sha = previous


def artifact_verifier_blob_errors(path: Path = ARTIFACT_VERIFIER) -> list[str]:
    """Preserve direct retained-artifact hash hostile-test injection."""
    previous = _impl.local_git_blob_sha
    try:
        _impl.local_git_blob_sha = local_git_blob_sha
        return _IMPL_ARTIFACT_VERIFIER_BLOB_ERRORS(path)
    finally:
        _impl.local_git_blob_sha = previous


def expected_verification_record() -> dict[str, object]:
    record = copy.deepcopy(_IMPL_EXPECTED_VERIFICATION_RECORD())
    record["schema_version"] = "1.3.0"
    record["status"] = "LEAN_VERIFIED"
    record["formalization_integration"] = {
        "pull_request": 22,
        "final_pr_head": FINAL_PR_HEAD,
        "merge_commit": INTEGRATION_COMMIT,
        "merge_tree": INTEGRATION_TREE,
        "source_release_unchanged": True,
    }
    toolchain = record["toolchain"]
    if not isinstance(toolchain, dict):
        raise RuntimeError("pending verification toolchain malformed")
    toolchain["lake"] = "5.0.0-src+819816b"
    batches = record["batches"]
    if not isinstance(batches, list):
        raise RuntimeError("pending verification batch list malformed")
    for batch in batches:
        if not isinstance(batch, dict):
            raise RuntimeError("pending verification batch malformed")
        batch["implementation_status"] = "LEAN_VERIFIED"
    audit = record["axiom_audit"]
    if not isinstance(audit, dict):
        raise RuntimeError("pending verification axiom policy malformed")
    audit["status"] = "VERIFIED_ON_MERGED_MAIN"
    audit["observed_axioms_by_theorem"] = {
        "UFT-OBS-001": ["Quot.sound", "propext"],
        "UFT-OBS-002": ["Quot.sound", "propext"],
        "UFT-OBS-003": ["Classical.choice"],
        "UFT-OBS-004": ["Classical.choice"],
        "UFT-OBS-005": ["Classical.choice", "Quot.sound", "propext"],
    }
    record["merged_main_ci"] = [
        {
            "workflow": "finite-adversarial",
            "workflow_id": 337029647,
            "run_id": FINITE_RUN_ID,
            "run_number": 421,
            "event": "push",
            "branch": "main",
            "head_sha": INTEGRATION_COMMIT,
            "conclusion": "success",
            "python_versions": ["3.12", "3.13"],
        },
        {
            "workflow": "vopson-corpus",
            "workflow_id": 337108839,
            "run_id": VOPSON_RUN_ID,
            "run_number": 413,
            "event": "push",
            "branch": "main",
            "head_sha": INTEGRATION_COMMIT,
            "conclusion": "success",
            "python_versions": ["3.12", "3.13"],
            "lean_build_job_id": VOPSON_LEAN_JOB_ID,
            "lean_build_result": "Build completed successfully (8711 jobs)",
            "axiom_audit_result": "ok",
        },
    ]
    record["review_evidence"] = {
        "codex_no_major_issues_reviewed_commit": CODEX_REVIEWED_COMMIT,
        "final_pr_head": FINAL_PR_HEAD,
        "note": (
            "Codex explicitly reported no major issues on 111a9c7a0b. Later commits addressed compatibility "
            "and documentation review findings; the exact final PR head and merged-main integration commit "
            "subsequently passed the complete pinned CI and axiom-audit gates."
        ),
    }
    record["next_ordered_gate"] = "QSOL_CONTEXT_LEAN_VERIFIED_CAPTURE_THEN_DOI_ARCHIVE"
    boundaries = record["hard_boundaries"]
    if not isinstance(boundaries, list):
        raise RuntimeError("pending verification hard-boundary list malformed")
    if "SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER" not in boundaries:
        boundaries.append("SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER")
    return record


def verification_record_errors(record: dict[str, object]) -> list[str]:
    return [] if record == expected_verification_record() else [
        "Lean observation LEAN_VERIFIED record drift"
    ]


def _pending_roadmap_projection(value: dict[str, object]) -> dict[str, object]:
    projected = copy.deepcopy(value)
    sequence = projected.get("sequence")
    if isinstance(sequence, list):
        for item in sequence:
            if isinstance(item, dict) and item.get("planned_pr") == 10:
                item["status"] = PENDING_ROADMAP_STATUS
    projected["compatibility_note"] = PENDING_ROADMAP_NOTE
    rules = projected.get("rules")
    if isinstance(rules, list) and len(rules) > 2:
        rules[2] = PENDING_ROADMAP_RULE
    return projected


def load_json(path: Path) -> dict[str, object]:
    """Strict public loader: always return the live file contents."""
    return _IMPL_LOAD_JSON(path)


def _projected_predecessor_load_json(path: Path) -> dict[str, object]:
    """Project only the canonical live roadmap while replaying the predecessor."""
    value = load_json(path)
    if (
        path == ROADMAP_STATE
        and _git_blob_sha(path) == EXPECTED_VERIFIED_ROADMAP_STATE_BLOB
        and isinstance(value, dict)
        and next(
            (
                item.get("status")
                for item in value.get("sequence", [])
                if isinstance(item, dict) and item.get("planned_pr") == 10
            ),
            None,
        ) == VERIFIED_ROADMAP_STATUS
        and value.get("compatibility_note") == VERIFIED_ROADMAP_NOTE
        and isinstance(value.get("rules"), list)
        and len(value["rules"]) > 2
        and value["rules"][2] == VERIFIED_ROADMAP_RULE
    ):
        return _pending_roadmap_projection(value)
    return value


_VERIFIED_AUTHORITY_BLOBS = dict(_impl._LIVE_AUTHORITY_BLOBS)
_VERIFIED_AUTHORITY_BLOBS.update(
    {
        ".github/workflows/vopson-corpus.yml": EXPECTED_VERIFIED_WORKFLOW_BLOB,
        "README4AI.md": EXPECTED_VERIFIED_README_BLOB,
        "ROADMAP.md": EXPECTED_VERIFIED_ROADMAP_BLOB,
        "machine/roadmap_state.json": EXPECTED_VERIFIED_ROADMAP_STATE_BLOB,
        "machine/lean_observation_verification.json": EXPECTED_VERIFIED_RECORD_BLOB,
        "scripts/validate_lean_observation_foundation_pr22_merged_frozen.py": EXPECTED_PREDECESSOR_BLOB,
        "scripts/verify_lean_observation_axioms.py": EXPECTED_VERIFIED_AXIOM_AUDITOR_BLOB,
    }
)
_VERIFIED_AUTHORITY_MODES = dict(_impl._LIVE_AUTHORITY_MODES)
_VERIFIED_AUTHORITY_MODES.update(
    {
        "ROADMAP.md": "100644",
        "scripts/validate_lean_observation_foundation_pr22_merged_frozen.py": "100644",
    }
)
# Public live registries always describe the current verification layer, while
# the frozen predecessor keeps its own reviewed pending-CI maps internally.
_LIVE_AUTHORITY_BLOBS = _VERIFIED_AUTHORITY_BLOBS
_LIVE_AUTHORITY_MODES = _VERIFIED_AUTHORITY_MODES


def _verified_authority_projection() -> tuple[dict[str, str], dict[str, str]]:
    blobs, modes = _impl._live_authority_projection()
    blobs.update(_VERIFIED_AUTHORITY_BLOBS)
    modes.update(_VERIFIED_AUTHORITY_MODES)
    return blobs, modes


_live_authority_projection = _verified_authority_projection


def tracked_authority_object_errors(
    root: Path = ROOT,
    *,
    expected_blobs: dict[str, str] | None = None,
    expected_modes: dict[str, str] | None = None,
    runner=subprocess.run,
) -> list[str]:
    if expected_blobs is None and expected_modes is None:
        blobs, modes = _verified_authority_projection()
    elif _impl._is_exact_production_projection(expected_blobs, expected_modes):
        blobs, modes = _verified_authority_projection()
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


def live_authority_object_errors() -> list[str]:
    checks = (
        (README4AI, EXPECTED_VERIFIED_README_BLOB, "README4AI verified Lean phase"),
        (ROADMAP, EXPECTED_VERIFIED_ROADMAP_BLOB, "ROADMAP verified Lean phase"),
        (ROADMAP_STATE, EXPECTED_VERIFIED_ROADMAP_STATE_BLOB, "verified live roadmap state"),
        (VERIFICATION, EXPECTED_VERIFIED_RECORD_BLOB, "LEAN_VERIFIED machine record"),
        (PREDECESSOR, EXPECTED_PREDECESSOR_BLOB, "merged-main PR22 validator"),
        (AXIOM_AUDITOR, EXPECTED_VERIFIED_AXIOM_AUDITOR_BLOB, "verified Lean axiom auditor"),
    )
    errors: list[str] = []
    for path, expected, label in checks:
        if not path.is_file():
            errors.append(f"{label} missing")
            continue
        actual = _git_blob_sha(path)
        if actual != expected:
            errors.append(f"{label} blob drift: expected {expected}, got {actual}")
    errors.extend(_IMPL_LIVE_AUTHORITY_OBJECT_ERRORS())
    # These predecessor pins are intentionally superseded by the verified live
    # layer. Filter only their exact stale diagnostics; every other predecessor
    # authority check remains active.
    superseded_prefixes = (
        "README4AI live Lean phase blob drift:",
        "live roadmap state blob drift:",
        "Lean axiom auditor blob drift:",
    )
    return [
        error
        for error in errors
        if not any(error.startswith(prefix) for prefix in superseded_prefixes)
    ]


def _project_verified_readme(text: str) -> str:
    if _text_git_blob_sha(text) != EXPECTED_VERIFIED_README_BLOB:
        return text
    if (
        text.count(VERIFIED_EFP_PHASE) != 1
        or text.count(VERIFIED_LEAN_IMPLEMENTATION_PARAGRAPH) != 1
        or text.count(VERIFIED_READ_NEXT_45) != 1
    ):
        return text
    projected = text.replace(VERIFIED_EFP_PHASE, PENDING_EFP_PHASE, 1)
    projected = projected.replace(
        VERIFIED_LEAN_IMPLEMENTATION_PARAGRAPH,
        PENDING_LEAN_IMPLEMENTATION_PARAGRAPH,
        1,
    )
    projected = projected.replace(VERIFIED_READ_NEXT_45, PENDING_READ_NEXT_45, 1)
    return projected


def _project_verified_roadmap(text: str) -> str:
    if _text_git_blob_sha(text) != EXPECTED_VERIFIED_ROADMAP_BLOB:
        return text
    if text.count(VERIFIED_ROADMAP_LIVE_NOTE) != 1:
        return text
    return text.replace(VERIFIED_ROADMAP_LIVE_NOTE, "", 1)


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
    old_tracked = _combined.tracked_authority_object_errors
    try:
        _combined.tracked_authority_object_errors = tracked_authority_object_errors
        return _COMBINED_VALIDATE_DOCUMENTS(
            freeze,
            source_theorems,
            source_counterexamples,
            base_contract,
            human,
            _project_verified_roadmap(roadmap),
            _project_verified_readme(readme),
            check_paths=check_paths,
            require_basis_objects=require_basis_objects,
        )
    finally:
        _combined.tracked_authority_object_errors = old_tracked


def workflow_contract_errors(text: str) -> list[str]:
    errors: list[str] = []
    if text.count(PREDECESSOR_WORKFLOW_ROUTE) != 2:
        errors.append("registered merged-main Lean-validator workflow dependency drift")
    projected = text.replace(PREDECESSOR_WORKFLOW_ROUTE, "")
    errors.extend(_IMPL_WORKFLOW_CONTRACT_ERRORS(projected))
    return errors


def _mirror_predecessor_hooks() -> dict[str, object]:
    previous: dict[str, object] = {}
    module_globals = globals()
    for name in _COMPAT_BRIDGE_NAMES:
        if hasattr(_impl, name) and name in module_globals:
            previous[name] = getattr(_impl, name)
            setattr(_impl, name, module_globals[name])
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


def _restore_predecessor_hooks(previous: dict[str, object]) -> None:
    for name, value in previous.items():
        setattr(_impl, name, value)


def validate(*, require_basis_objects: bool = True):
    bridged = _mirror_predecessor_hooks()
    old_values = {
        "tracked_authority_object_errors": _impl.tracked_authority_object_errors,
        "workflow_contract_errors": _impl.workflow_contract_errors,
        "expected_verification_record": _impl.expected_verification_record,
        "verification_record_errors": _impl.verification_record_errors,
        "load_json": _impl.load_json,
        "live_authority_object_errors": _impl.live_authority_object_errors,
    }
    old_combined_values = {
        "expected_verification_record": _combined.expected_verification_record,
        "verification_record_errors": _combined.verification_record_errors,
        "load_json": _combined.load_json,
        "live_authority_object_errors": _combined.live_authority_object_errors,
        "validate_documents": _combined.validate_documents,
    }
    try:
        _impl.tracked_authority_object_errors = tracked_authority_object_errors
        _impl.workflow_contract_errors = workflow_contract_errors
        _impl.expected_verification_record = expected_verification_record
        _impl.verification_record_errors = verification_record_errors
        _impl.load_json = _projected_predecessor_load_json
        _impl.live_authority_object_errors = live_authority_object_errors

        # `_IMPL_VALIDATE` delegates into this actual combined-review module.
        # Install the verified hooks there too so no pending-CI check sees the
        # canonical schema-1.3 record or live roadmap before projection.
        _combined.expected_verification_record = expected_verification_record
        _combined.verification_record_errors = verification_record_errors
        _combined.load_json = _projected_predecessor_load_json
        _combined.live_authority_object_errors = live_authority_object_errors
        _combined.validate_documents = validate_documents

        result = _IMPL_VALIDATE(require_basis_objects=require_basis_objects)
    finally:
        for name, value in old_values.items():
            setattr(_impl, name, value)
        for name, value in old_combined_values.items():
            setattr(_combined, name, value)
        _restore_predecessor_hooks(bridged)

    errors = list(result.get("errors", []))
    errors.extend(predecessor_validator_blob_errors())
    errors.extend(live_authority_object_errors())
    try:
        actual_record = load_json(VERIFICATION)
    except (OSError, ValueError) as exc:
        errors.append(f"LEAN_VERIFIED machine record invalid: {exc}")
    else:
        errors.extend(verification_record_errors(actual_record))
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
            "Lean observation verification: ok "
            f"(LEAN_VERIFIED; source {SOURCE_TAG}; integration {INTEGRATION_COMMIT}; "
            f"Lean {LEAN_VERSION}; merged-main build and axiom audit green)"
        )
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
