#!/usr/bin/env python3
"""Fail-closed validation for PR #21 source theorem-batch freeze.

This validates a source freeze for later Lean work. It does not compile Lean and
must not promote mathematical proofs into repository-level Lean proof status.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "machine/lean_observation_foundation_contract.json"
SOURCE_THEOREMS = ROOT / "machine/observation_theorems.json"
SOURCE_COUNTEREXAMPLES = ROOT / "machine/observation_counterexamples.json"
BASE_CONTRACT = ROOT / "machine/contract.json"
HUMAN = ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md"
ROADMAP = ROOT / "ROADMAP.md"
README4AI = ROOT / "README4AI.md"
OBSERVATION_VALIDATOR = ROOT / "scripts/validate_observation_specs.py"

EXPECTED_HUMAN_STATUS = "SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF"
PRETAG_PACKAGE_FILENAMES = {"lean-toolchain", "lakefile.toml", "lake-manifest.json"}

TOP_FIELDS = {
    "type", "schema_version", "snapshot_date", "claim_class", "status",
    "batch_id", "basis_commit", "source_authorities", "theorem_ids",
    "deferred_theorem_ids", "theorems", "dependency_graph",
    "lean_module_map", "toolchain", "release_gate", "hard_boundaries",
}
THEOREM_FIELDS = {
    "id", "name", "source_claim_class", "statement", "hypotheses",
    "formalization_scope", "nonclaims", "proof_reference",
    "theorem_dependencies", "counterexample_dependencies", "lean_module",
    "lean_path", "lean_declaration", "lean_status",
}

EXPECTED_SOURCE_BLOBS = {
    "machine/observation_contract.json": "8eede68aa53c92666d7a25641a9e7e699668aea0",
    "machine/observation_specs.json": "1f1868054763fa3c9e84c9a8664b0c3134ffcee8",
    "machine/observation_theorems.json": "fbb1d1081fe2fed6980068f9630a8890b31794b9",
    "machine/observation_counterexamples.json": "1b8551ffb124076b9d50de4f13b4e9ceb0246a04",
    "theory/OBSERVATION_CALCULUS.md": "8bf8fb39c3b7b6d08fdab24261efa455b2ee3b4a",
    "scripts/validate_observation_specs.py": "bdd68c1f7ff183f0efd7ae142c5ffcdc721dfd87",
    "experiments/observation/run.py": "55e02cee0b33136fb8ee22896fdd923b281e8a9c",
    "tests/test_pr9_observation.py": "5373773686d97d280d0a89c2bb0a6a953f6d7ec8",
    "experiments/run_pr9.py": "78d7bf1e6d5998f8665b99207559876350bbb639",
}

EXPECTED_THEOREMS = {
    "UFT-OBS-001": {
        "id": "UFT-OBS-001",
        "name": "Observational equivalence",
        "source_claim_class": "PROVED",
        "statement": "For any function O:S->Y, define x~_O y iff O(x)=O(y). Then ~_O is an equivalence relation on S, and the equivalence class of x equals the fibre O^{-1}({O(x)}).",
        "hypotheses": ["O is a total deterministic function S->Y"],
        "formalization_scope": "set-theoretic deterministic observation only",
        "nonclaims": ["Observational equivalence is not physical identity."],
        "proof_reference": "theory/OBSERVATION_CALCULUS.md#uft-obs-001-observational-equivalence",
        "theorem_dependencies": [],
        "counterexample_dependencies": [],
        "lean_module": "UFTID.Observation.Basic",
        "lean_path": "UFTID/Observation/Basic.lean",
        "lean_declaration": "uft_obs_001_observational_equivalence",
        "lean_status": "NOT_IMPLEMENTED",
    },
    "UFT-OBS-002": {
        "id": "UFT-OBS-002",
        "name": "Quotient-to-image correspondence",
        "source_claim_class": "PROVED",
        "statement": "For any function O:S->Y, the quotient S/~_O is canonically bijective with im(O), via [x] |-> O(x).",
        "hypotheses": ["O is a total deterministic function S->Y"],
        "formalization_scope": "set-theoretic deterministic observation only",
        "nonclaims": ["The quotient is not canonically the full codomain Y unless O is surjective."],
        "proof_reference": "theory/OBSERVATION_CALCULUS.md#uft-obs-002-quotient-to-image-correspondence",
        "theorem_dependencies": ["UFT-OBS-001"],
        "counterexample_dependencies": ["CX-OBS-002"],
        "lean_module": "UFTID.Observation.Quotient",
        "lean_path": "UFTID/Observation/Quotient.lean",
        "lean_declaration": "uft_obs_002_quotient_to_image",
        "lean_status": "NOT_IMPLEMENTED",
    },
    "UFT-OBS-003": {
        "id": "UFT-OBS-003",
        "name": "Image-scoped exact reconstruction iff injective",
        "source_claim_class": "PROVED",
        "statement": "For any function O:S->Y, O is injective iff there exists R:im(O)->S such that R(O(x))=x for every x in S.",
        "hypotheses": ["O is a total deterministic function S->Y", "Reconstruction is scoped to im(O)"],
        "formalization_scope": "set-theoretic deterministic observation only",
        "nonclaims": ["Exact mathematical reconstruction does not establish that an original physical state persisted or was observed directly."],
        "proof_reference": "theory/OBSERVATION_CALCULUS.md#uft-obs-003-image-scoped-exact-reconstruction",
        "theorem_dependencies": [],
        "counterexample_dependencies": ["CX-OBS-001"],
        "lean_module": "UFTID.Observation.Reconstruction",
        "lean_path": "UFTID/Observation/Reconstruction.lean",
        "lean_declaration": "uft_obs_003_image_reconstruction_iff_injective",
        "lean_status": "NOT_IMPLEMENTED",
    },
    "UFT-OBS-004": {
        "id": "UFT-OBS-004",
        "name": "Noninjective observation blocks global exact reconstruction",
        "source_claim_class": "PROVED",
        "statement": "If O:S->Y is noninjective, no function R:Y->S can satisfy R(O(x))=x for every x in S.",
        "hypotheses": ["O is a total deterministic function S->Y", "O is noninjective"],
        "formalization_scope": "set-theoretic deterministic observation only",
        "nonclaims": ["Noninjectivity does not forbid partial, representative, probabilistic, or task-specific reconstruction."],
        "proof_reference": "theory/OBSERVATION_CALCULUS.md#uft-obs-004-noninjective-observation-blocks-global-exact-reconstruction",
        "theorem_dependencies": ["UFT-OBS-003"],
        "counterexample_dependencies": ["CX-OBS-001"],
        "lean_module": "UFTID.Observation.Reconstruction",
        "lean_path": "UFTID/Observation/Reconstruction.lean",
        "lean_declaration": "uft_obs_004_noninjective_no_global_left_inverse",
        "lean_status": "NOT_IMPLEMENTED",
    },
}

EXPECTED_GRAPH = {
    "UFT-OBS-001": [],
    "UFT-OBS-002": ["UFT-OBS-001"],
    "UFT-OBS-003": [],
    "UFT-OBS-004": ["UFT-OBS-003"],
}
EXPECTED_MODULE_MAP = [
    {"module": "UFTID.Observation.Basic", "path": "UFTID/Observation/Basic.lean", "depends_on": [], "theorem_ids": ["UFT-OBS-001"]},
    {"module": "UFTID.Observation.Quotient", "path": "UFTID/Observation/Quotient.lean", "depends_on": ["UFTID.Observation.Basic"], "theorem_ids": ["UFT-OBS-002"]},
    {"module": "UFTID.Observation.Reconstruction", "path": "UFTID/Observation/Reconstruction.lean", "depends_on": ["UFTID.Observation.Basic"], "theorem_ids": ["UFT-OBS-003", "UFT-OBS-004"]},
]
EXPECTED_BOUNDARIES = [
    "MATHEMATICAL_PROOF != LEAN_PROOF",
    "SOURCE_THEOREM != LEAN_ARTIFACT",
    "THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG",
    "SOURCE_RELEASE_TAG != LEAN_VERIFIED",
    "LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION",
    "UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED",
]


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return None
    start = matches[0]
    match = re.match(r"^(#+)\s", heading)
    if match is None:
        return None
    level = len(match.group(1))
    out = [lines[start]]
    for line in lines[start + 1:]:
        candidate = re.match(r"^(#+)\s", line.strip())
        if candidate is not None and len(candidate.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def metadata(sec: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    values = [line.strip()[len(prefix):].rstrip() for line in sec.splitlines() if line.strip().startswith(prefix)]
    return values[0] if len(values) == 1 else None


def strip_code(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value.endswith("  "):
        value = value[:-2].rstrip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def parse_json_metadata(sec: str, label: str):
    raw = strip_code(metadata(sec, label))
    try:
        return json.loads(raw) if raw is not None else None
    except json.JSONDecodeError:
        return None


def source_theorem_projection(record: dict[str, object]) -> dict[str, object]:
    return {
        "id": record.get("id"),
        "name": record.get("name"),
        "source_claim_class": record.get("claim_class"),
        "statement": record.get("statement"),
        "hypotheses": record.get("hypotheses"),
        "nonclaims": record.get("nonclaims"),
        "proof_reference": record.get("proof_reference"),
    }


def pretag_lean_files(root: Path = ROOT) -> list[str]:
    found: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        if path.suffix == ".lean" or path.name in PRETAG_PACKAGE_FILENAMES:
            found.append(rel.as_posix())
    return sorted(found)


def human_promotion_errors(text: str) -> list[str]:
    errors: list[str] = []
    patterns = (
        r"(?is)\b(?:all|each)\b.{0,80}\btheorems?\b.{0,80}\b(?:checked|verified|proved)\b.{0,40}\bLean\b",
        r"(?is)\bLean\b.{0,40}\b(?:proof|verification)\b.{0,40}\b(?:is|are)\b.{0,20}\b(?:complete|verified|proved|checked)\b",
    )
    for pattern in patterns:
        if re.search(pattern, text):
            errors.append("Lean observation human Lean verification promotion")
            break
    return errors


def graph_is_acyclic(graph: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    done: set[str] = set()
    def visit(node: str) -> bool:
        if node in done:
            return True
        if node in visiting:
            return False
        visiting.add(node)
        for dep in graph.get(node, []):
            if not visit(dep):
                return False
        visiting.remove(node)
        done.add(node)
        return True
    return all(visit(node) for node in graph)


def validate_documents(freeze, source_theorems, source_counterexamples, base_contract, human, roadmap, readme, *, check_paths: bool = True):
    errors: list[str] = []

    if set(freeze) != TOP_FIELDS:
        errors.append("Lean observation freeze top-level field set drift")
    expected_scalars = {
        "type": "uft-id-lean-observation-foundation-freeze",
        "schema_version": "1.0.0",
        "snapshot_date": "2026-08-24",
        "claim_class": "DEFINITION",
        "status": "SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF",
        "batch_id": "LEAN-OBS-BATCH-001",
        "basis_commit": "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093",
    }
    for key, expected in expected_scalars.items():
        if freeze.get(key) != expected:
            errors.append(f"Lean observation freeze {key} drift")

    expected_source_list = [{"path": path, "git_blob_sha": sha} for path, sha in EXPECTED_SOURCE_BLOBS.items()]
    if freeze.get("source_authorities") != expected_source_list:
        errors.append("Lean observation source authority set/blob drift")

    expected_ids = list(EXPECTED_THEOREMS)
    if freeze.get("theorem_ids") != expected_ids:
        errors.append("Lean observation frozen theorem id/order drift")
    if freeze.get("deferred_theorem_ids") != ["UFT-OBS-005"]:
        errors.append("Lean observation deferred theorem set drift")

    records = freeze.get("theorems")
    if not isinstance(records, list) or len(records) != len(EXPECTED_THEOREMS):
        errors.append("Lean observation theorem freeze registry malformed")
        records = []
    by_id = {x.get("id"): x for x in records if isinstance(x, dict)}
    for theorem_id, expected in EXPECTED_THEOREMS.items():
        actual = by_id.get(theorem_id)
        if not isinstance(actual, dict):
            errors.append(f"{theorem_id} missing from Lean observation freeze")
            continue
        if set(actual) != THEOREM_FIELDS:
            errors.append(f"{theorem_id} freeze field set drift")
        if actual != expected:
            errors.append(f"{theorem_id} frozen payload drift")

    source_records = source_theorems.get("records")
    if not isinstance(source_records, list):
        errors.append("source observation theorem registry malformed")
        source_records = []
    source_by_id = {x.get("id"): x for x in source_records if isinstance(x, dict)}
    if set(source_by_id) != set(EXPECTED_THEOREMS) | {"UFT-OBS-005"}:
        errors.append("source observation theorem inventory drift")
    for theorem_id, expected in EXPECTED_THEOREMS.items():
        source = source_by_id.get(theorem_id)
        if not isinstance(source, dict):
            errors.append(f"{theorem_id} missing from source theorem registry")
            continue
        projected = source_theorem_projection(source)
        source_expected = {key: expected[key] for key in ("id", "name", "source_claim_class", "statement", "hypotheses", "nonclaims", "proof_reference")}
        if projected != source_expected:
            errors.append(f"{theorem_id} source/freeze theorem authority drift")

    cx_records = source_counterexamples.get("records")
    if not isinstance(cx_records, list):
        errors.append("source observation counterexample registry malformed")
        cx_records = []
    cx_by_id = {x.get("id"): x for x in cx_records if isinstance(x, dict)}
    referenced_cx = {cx for expected in EXPECTED_THEOREMS.values() for cx in expected["counterexample_dependencies"]}
    for cx_id in referenced_cx:
        record = cx_by_id.get(cx_id)
        if not isinstance(record, dict) or record.get("claim_class") != "COUNTEREXAMPLE":
            errors.append(f"{cx_id} counterexample dependency missing or reclassified")

    if freeze.get("dependency_graph") != EXPECTED_GRAPH:
        errors.append("Lean observation theorem dependency graph drift")
    if not graph_is_acyclic(EXPECTED_GRAPH):
        errors.append("Lean observation expected dependency graph is cyclic")
    if freeze.get("lean_module_map") != EXPECTED_MODULE_MAP:
        errors.append("Lean observation module map drift")

    toolchain = freeze.get("toolchain")
    expected_toolchain = {
        "status": "UNPINNED", "lean": None, "lake": None, "mathlib": None,
        "policy": "No Lean/Lake/Mathlib version is selected by this source-freeze PR.",
    }
    if toolchain != expected_toolchain:
        errors.append("Lean observation toolchain deferral drift")
    expected_release = {
        "status": "PENDING_POST_MERGE",
        "source_tag": None,
        "target_policy": "After this freeze PR merges, pass exact merged-main CI and hostile review, then tag that exact commit/tree before any Lean proof implementation.",
    }
    if freeze.get("release_gate") != expected_release:
        errors.append("Lean observation post-merge release gate drift")
    if freeze.get("hard_boundaries") != EXPECTED_BOUNDARIES:
        errors.append("Lean observation hard boundary drift")

    authority = base_contract.get("lean_observation_foundation_authority")
    expected_authority = {
        "machine_contract": "machine/lean_observation_foundation_contract.json",
        "human": "theory/LEAN_OBSERVATION_FOUNDATION.md",
        "validator": "scripts/validate_lean_observation_foundation.py",
        "tests": "tests/test_lean_observation_foundation.py",
        "source_theorems": "machine/observation_theorems.json",
        "source_counterexamples": "machine/observation_counterexamples.json",
        "source_observation_contract": "machine/observation_contract.json",
        "workflow": ".github/workflows/finite-adversarial.yml",
        "rule": "The first Lean observation batch freezes source theorem identity and dependency/module mapping only; it does not claim Lean proof, select a toolchain, or create the immutable source-release tag.",
    }
    if authority != expected_authority:
        errors.append("Lean observation base-contract authority registration drift")

    if strip_code(metadata(human, "Status")) != EXPECTED_HUMAN_STATUS:
        errors.append("Lean observation human freeze status drift")
    if strip_code(metadata(human, "Claim class")) != "DEFINITION":
        errors.append("Lean observation human claim class drift")
    errors.extend(human_promotion_errors(human))

    for theorem_id, expected in EXPECTED_THEOREMS.items():
        heading = f"## {theorem_id} {expected['name']}"
        sec = section(human, heading)
        if sec is None:
            errors.append(f"{theorem_id} human freeze section missing or duplicated")
            continue
        checks = {
            "Source claim class": expected["source_claim_class"],
            "Canonical statement": expected["statement"],
            "Formalization scope": expected["formalization_scope"],
            "Expected Lean module": expected["lean_module"],
            "Expected Lean path": expected["lean_path"],
            "Expected Lean declaration": expected["lean_declaration"],
            "Lean status": "NOT_IMPLEMENTED",
        }
        for label, expected_value in checks.items():
            if strip_code(metadata(sec, label)) != expected_value:
                errors.append(f"{theorem_id} human {label} drift")
        json_checks = {
            "Canonical hypotheses": expected["hypotheses"],
            "Source nonclaims": expected["nonclaims"],
            "Theorem dependencies": expected["theorem_dependencies"],
            "Counterexample dependencies": expected["counterexample_dependencies"],
        }
        for label, expected_value in json_checks.items():
            if parse_json_metadata(sec, label) != expected_value:
                errors.append(f"{theorem_id} human {label} drift")

    required_human = [
        "UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED",
        "FREEZE PR MERGED",
        "-> IMMUTABLE SOURCE-RELEASE TAG",
        "-> LEAN PROOF IMPLEMENTATION",
    ]
    for token in required_human:
        if token not in human:
            errors.append(f"Lean observation human boundary missing: {token}")

    if "- [x] Freeze the first PR #10 theorem batch and dependency graph." not in roadmap:
        errors.append("ROADMAP first Lean theorem-batch freeze is not checked")
    if "- [ ] Pass the exact merged-main release gate and cut the immutable source tag." not in roadmap:
        errors.append("ROADMAP source-release tag must remain pending")
    if "LEAN-OBS-BATCH-001" not in roadmap:
        errors.append("ROADMAP missing Lean observation batch identity")
    if "UFT-OBS-001` through `UFT-OBS-004" not in roadmap:
        errors.append("ROADMAP missing frozen Lean observation theorem range")

    readme_tokens = [
        "LEAN-OBS-BATCH-001",
        "UFT-OBS-001` through `UFT-OBS-004",
        "UFT-OBS-005` remains deferred",
        "No Lean proof object is claimed",
        "tag that exact merged commit/tree before Lean proof implementation",
    ]
    for token in readme_tokens:
        if token not in readme:
            errors.append(f"README4AI Lean freeze bootstrap drift: {token}")

    if check_paths:
        for relpath, expected_sha in EXPECTED_SOURCE_BLOBS.items():
            path = ROOT / relpath
            if not path.is_file():
                errors.append(f"missing frozen source authority: {relpath}")
            elif git_blob_sha(path) != expected_sha:
                errors.append(f"frozen source Git blob drift: {relpath}")
        obs = load_module("pr21_observation_base_validator", OBSERVATION_VALIDATOR).validate()
        if obs.get("status") != "ok":
            errors.append("PR9 observation base authority validation failed")
        release_gate = freeze.get("release_gate")
        if isinstance(release_gate, dict) and release_gate.get("status") == "PENDING_POST_MERGE" and release_gate.get("source_tag") is None:
            for relpath in pretag_lean_files(ROOT):
                errors.append(f"pre-tag Lean source/toolchain forbidden: {relpath}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "batch_id": freeze.get("batch_id"),
        "theorem_count": len(EXPECTED_THEOREMS),
        "deferred_count": 1,
        "module_count": len(EXPECTED_MODULE_MAP),
    }


def validate():
    paths = [FREEZE, SOURCE_THEOREMS, SOURCE_COUNTEREXAMPLES, BASE_CONTRACT, HUMAN, ROADMAP, README4AI]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        return {"status": "error", "errors": [f"missing Lean observation freeze authority: {x}" for x in missing], "batch_id": None, "theorem_count": 0, "deferred_count": 0, "module_count": 0}
    return validate_documents(
        load_json(FREEZE),
        load_json(SOURCE_THEOREMS),
        load_json(SOURCE_COUNTEREXAMPLES),
        load_json(BASE_CONTRACT),
        HUMAN.read_text(encoding="utf-8"),
        ROADMAP.read_text(encoding="utf-8"),
        README4AI.read_text(encoding="utf-8"),
        check_paths=True,
    )


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Lean observation source freeze: ok ({result['theorem_count']} theorems, {result['module_count']} modules, {result['deferred_count']} deferred)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
