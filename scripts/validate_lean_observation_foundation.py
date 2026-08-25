#!/usr/bin/env python3
"""Post-tag validator for LEAN-OBS-BATCH-001.

The final pre-tag PR #21 validator is preserved byte-for-byte in
``validate_lean_observation_foundation_pr21_final_frozen.py``.  This wrapper
keeps that source-freeze authority intact, then adds the only transition the
v3.0.0 release gate permits: an exact, pinned Lean package implementing
UFT-OBS-001 through UFT-OBS-004 against the immutable v3.0.0 source commit.

UFT-OBS-005 remains deferred.  Lean compilation is formal verification of the
abstract set-theoretic statements only; it is not empirical validation or a
physical-ontology claim.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRETAG_FINAL = ROOT / "scripts/validate_lean_observation_foundation_pr21_final_frozen.py"
EXPECTED_PRETAG_FINAL_BLOB = "42f2a2f30258cf99c1ee0755b54ef33d8d8c0d5f"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def predecessor_validator_blob_errors(path: Path = PRETAG_FINAL) -> list[str]:
    if not path.is_file():
        return ["final pre-tag Lean validator missing before import"]
    actual = _git_blob_sha(path)
    if actual != EXPECTED_PRETAG_FINAL_BLOB:
        return [
            "final pre-tag Lean validator blob drift: "
            f"expected {EXPECTED_PRETAG_FINAL_BLOB}, got {actual}"
        ]
    return []


_preload_errors = predecessor_validator_blob_errors()
if _preload_errors:
    raise RuntimeError("; ".join(_preload_errors))

_spec = importlib.util.spec_from_file_location(
    "lean_observation_pr21_final_frozen", PRETAG_FINAL
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load final pre-tag validator: {PRETAG_FINAL}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

# Preserve the reviewed helper/test surface.  The post-tag functions overridden
# below are intentionally excluded.
for _name in dir(_frozen):
    if not _name.startswith("__") and _name not in {
        "validate_documents",
        "validate",
        "main",
        "basis_source_object_errors",
    }:
        globals()[_name] = getattr(_frozen, _name)

_FROZEN_BASIS_SOURCE_OBJECT_ERRORS = _frozen.basis_source_object_errors

FREEZE = _frozen.FREEZE
SOURCE_THEOREMS = _frozen.SOURCE_THEOREMS
SOURCE_COUNTEREXAMPLES = _frozen.SOURCE_COUNTEREXAMPLES
BASE_CONTRACT = _frozen.BASE_CONTRACT
HUMAN = _frozen.HUMAN
ROADMAP = _frozen.ROADMAP
README4AI = _frozen.README4AI
WORKFLOW = _frozen.WORKFLOW
ROADMAP_STATE = _frozen.ROADMAP_STATE

VERIFICATION = ROOT / "machine/lean_observation_verification.json"
LEAN_TOOLCHAIN = ROOT / "lean-toolchain"
LAKEFILE = ROOT / "lakefile.toml"
LEAN_ROOT = ROOT / "UFTID.lean"
LEAN_BASIC = ROOT / "UFTID/Observation/Basic.lean"
LEAN_QUOTIENT = ROOT / "UFTID/Observation/Quotient.lean"
LEAN_RECONSTRUCTION = ROOT / "UFTID/Observation/Reconstruction.lean"
LEAN_WORKFLOW = ROOT / ".github/workflows/lean-observation.yml"

SOURCE_TAG = "v3.0.0"
SOURCE_COMMIT = "b7f51590985e60920c8b09fc9238b8aec6cfa3bc"
SOURCE_TREE = "966bdf47596832f792e77d619b33222f4cf60c8d"
LEAN_VERSION = "v4.33.1"
MATHLIB_COMMIT = "0df444a360eaa60ab8c11dca51a86af692955474"
LEAN_ARCHIVE_SHA256 = "890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235"
LEAN_ARCHIVE_URL = (
    "https://github.com/leanprover/lean4/releases/download/"
    "v4.33.1/lean-4.33.1-linux.tar.zst"
)

EXPECTED_ALLOWED_LEAN_PATHS = frozenset(
    {
        "UFTID.lean",
        "UFTID/Observation/Basic.lean",
        "UFTID/Observation/Quotient.lean",
        "UFTID/Observation/Reconstruction.lean",
        "lean-toolchain",
        "lakefile.toml",
    }
)

EXPECTED_DECLARATIONS = {
    "UFT-OBS-001": (
        "UFTID/Observation/Basic.lean",
        "uft_obs_001_observational_equivalence",
    ),
    "UFT-OBS-002": (
        "UFTID/Observation/Quotient.lean",
        "uft_obs_002_quotient_to_image",
    ),
    "UFT-OBS-003": (
        "UFTID/Observation/Reconstruction.lean",
        "uft_obs_003_image_reconstruction_iff_injective",
    ),
    "UFT-OBS-004": (
        "UFTID/Observation/Reconstruction.lean",
        "uft_obs_004_noninjective_no_global_left_inverse",
    ),
}

EXPECTED_LAKEFILE = f'''name = "UFTID"
version = "3.0.0"
defaultTargets = ["UFTID"]

[leanOptions]
autoImplicit = false
relaxedAutoImplicit = false

[[require]]
name = "mathlib"
git = "https://github.com/leanprover-community/mathlib4.git"
rev = "{MATHLIB_COMMIT}"

[[lean_lib]]
name = "UFTID"
'''

EXPECTED_ROOT_IMPORTS = (
    "import UFTID.Observation.Basic",
    "import UFTID.Observation.Quotient",
    "import UFTID.Observation.Reconstruction",
)


def basis_source_object_errors() -> list[str]:
    """Retain the old mutation-test hook while calling the frozen checker."""
    previous = _frozen.basis_git_blob_sha
    try:
        _frozen.basis_git_blob_sha = basis_git_blob_sha
        return _FROZEN_BASIS_SOURCE_OBJECT_ERRORS()
    finally:
        _frozen.basis_git_blob_sha = previous


def _git_rev_parse(expression: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", expression],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def source_release_errors() -> list[str]:
    errors: list[str] = []
    actual_commit = _git_rev_parse(f"refs/tags/{SOURCE_TAG}^{{commit}}")
    actual_tree = _git_rev_parse(f"refs/tags/{SOURCE_TAG}^{{tree}}")
    if actual_commit != SOURCE_COMMIT:
        errors.append(
            f"Lean source tag identity drift: expected {SOURCE_TAG} -> {SOURCE_COMMIT}, "
            f"got {actual_commit}"
        )
    if actual_tree != SOURCE_TREE:
        errors.append(
            f"Lean source tag tree drift: expected {SOURCE_TREE}, got {actual_tree}"
        )
    return errors


def expected_verification_record() -> dict[str, object]:
    return {
        "type": "uft-id-lean-observation-verification",
        "schema_version": "1.0.0",
        "batch_id": "LEAN-OBS-BATCH-001",
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
        "theorems": [
            {
                "id": theorem_id,
                "module": {
                    "UFT-OBS-001": "UFTID.Observation.Basic",
                    "UFT-OBS-002": "UFTID.Observation.Quotient",
                    "UFT-OBS-003": "UFTID.Observation.Reconstruction",
                    "UFT-OBS-004": "UFTID.Observation.Reconstruction",
                }[theorem_id],
                "path": path,
                "declaration": declaration,
            }
            for theorem_id, (path, declaration) in EXPECTED_DECLARATIONS.items()
        ],
        "deferred_theorem_ids": ["UFT-OBS-005"],
        "hard_boundaries": [
            "LEAN_PROOF != EMPIRICAL_VALIDATION",
            "LEAN_PROOF != PHYSICAL_ONTOLOGY",
            "UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED",
        ],
    }


def verification_record_errors(record: dict[str, object]) -> list[str]:
    if record != expected_verification_record():
        return ["Lean observation implementation verification record drift"]
    return []


def posttag_path_errors() -> list[str]:
    """Allow only the exact registered Lean package after v3.0.0.

    The historical helper is deliberately reused so old adversarial tests keep
    proving that hidden `.lean`, `.olean`, `.ilean`, and package files are found.
    Generated compiled modules remain forbidden from source control.
    """
    tracked, inventory_errors = tracked_pretag_lean_files()
    errors = list(inventory_errors)
    actual = set(tracked)
    for relpath in sorted(actual - EXPECTED_ALLOWED_LEAN_PATHS):
        errors.append(f"pre-tag Lean source/toolchain forbidden: {relpath}")
    for relpath in sorted(EXPECTED_ALLOWED_LEAN_PATHS - actual):
        errors.append(f"registered post-tag Lean source/toolchain missing: {relpath}")
    return errors


def lean_source_errors() -> list[str]:
    errors: list[str] = []
    paths = {
        "UFTID.lean": LEAN_ROOT,
        "UFTID/Observation/Basic.lean": LEAN_BASIC,
        "UFTID/Observation/Quotient.lean": LEAN_QUOTIENT,
        "UFTID/Observation/Reconstruction.lean": LEAN_RECONSTRUCTION,
    }
    texts: dict[str, str] = {}
    for relpath, path in paths.items():
        if not path.is_file():
            errors.append(f"registered Lean source missing: {relpath}")
            continue
        texts[relpath] = path.read_text(encoding="utf-8")

    for relpath, text in texts.items():
        if re.search(r"(?m)^\s*(?:axiom|unsafe\s+axiom)\b", text):
            errors.append(f"Lean proof escape hatch forbidden: axiom in {relpath}")
        if re.search(r"\b(?:sorry|admit)\b", text):
            errors.append(f"Lean proof hole forbidden in {relpath}")
        if "UFT-OBS-005" in text or "uft_obs_005" in text:
            errors.append(f"deferred UFT-OBS-005 leaked into Lean batch 001: {relpath}")

    for theorem_id, (relpath, declaration) in EXPECTED_DECLARATIONS.items():
        text = texts.get(relpath, "")
        matches = re.findall(
            rf"(?m)^theorem\s+{re.escape(declaration)}\b", text
        )
        if len(matches) != 1:
            errors.append(
                f"{theorem_id} Lean declaration count drift: {declaration}"
            )

    root_lines = tuple(
        line.strip() for line in texts.get("UFTID.lean", "").splitlines() if line.strip()
    )
    if root_lines != EXPECTED_ROOT_IMPORTS:
        errors.append("UFTID root Lean import surface drift")

    basic = texts.get("UFTID/Observation/Basic.lean", "")
    quotient = texts.get("UFTID/Observation/Quotient.lean", "")
    reconstruction = texts.get("UFTID/Observation/Reconstruction.lean", "")
    if "import UFTID." in basic:
        errors.append("UFT-OBS-001 module gained an undeclared UFTID dependency")
    if tuple(
        line.strip() for line in quotient.splitlines() if line.startswith("import ")
    ) != ("import UFTID.Observation.Basic",):
        errors.append("UFT-OBS-002 Lean module dependency drift")
    if tuple(
        line.strip() for line in reconstruction.splitlines() if line.startswith("import ")
    ) != ("import UFTID.Observation.Basic",):
        errors.append("UFT-OBS-003/004 Lean module dependency drift")
    return errors


def toolchain_errors() -> list[str]:
    errors: list[str] = []
    if not LEAN_TOOLCHAIN.is_file():
        errors.append("lean-toolchain missing")
    elif LEAN_TOOLCHAIN.read_text(encoding="utf-8") != f"leanprover/lean4:{LEAN_VERSION}\n":
        errors.append("Lean toolchain pin drift")
    if not LAKEFILE.is_file():
        errors.append("lakefile.toml missing")
    elif LAKEFILE.read_text(encoding="utf-8") != EXPECTED_LAKEFILE:
        errors.append("Lake/mathlib exact pin drift")
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
    # All theorem identity, statement, hypothesis, dependency, counterexample,
    # human-authority, and pre-release nonclaim checks remain frozen.  Only the
    # historical path embargo is replaced after the source tag exists.
    result = _frozen.validate_documents(
        freeze,
        source_theorems,
        source_counterexamples,
        base_contract,
        human,
        roadmap,
        readme,
        check_paths=False,
        require_basis_objects=require_basis_objects,
    )
    errors = list(result.get("errors", []))
    if check_paths:
        errors.extend(tracked_authority_object_errors())
        errors.extend(posttag_path_errors())
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
        VERIFICATION,
        LEAN_TOOLCHAIN,
        LAKEFILE,
        LEAN_ROOT,
        LEAN_BASIC,
        LEAN_QUOTIENT,
        LEAN_RECONSTRUCTION,
        LEAN_WORKFLOW,
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

    # Strict-load the live roadmap first, preserving the existing duplicate-key
    # and non-finite-number failure behaviour.
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
    errors.extend(predecessor_validator_blob_errors())
    errors.extend(base_validator_blob_errors())
    errors.extend(frozen_validator_blob_errors())
    errors.extend(artifact_verifier_blob_errors())
    errors.extend(workflow_contract_errors(WORKFLOW.read_text(encoding="utf-8")))
    errors.extend(source_release_errors())
    errors.extend(verification_record_errors(load_json(VERIFICATION)))
    errors.extend(toolchain_errors())
    errors.extend(lean_source_errors())
    result["errors"] = errors
    result["status"] = "error" if errors else "ok"
    result["source_tag"] = SOURCE_TAG
    result["source_commit"] = SOURCE_COMMIT
    result["lean_version"] = LEAN_VERSION
    result["mathlib_commit"] = MATHLIB_COMMIT
    result["implementation_status"] = "IMPLEMENTED_PENDING_CI"
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
            f"({result['theorem_count']} theorems, source {SOURCE_TAG}, Lean {LEAN_VERSION})"
        )
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
