#!/usr/bin/env python3
"""Fail-closed validation for graph realization and typed incidence authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "contract": ROOT / "machine/graph_realization_contract.json",
    "results": ROOT / "machine/graph_realization_results.json",
    "sources": ROOT / "research/GRAPH_REALIZATION_SOURCES.md",
    "human": ROOT / "theory/GRAPH_REALIZATION.md",
    "base_contract": ROOT / "machine/contract.json",
    "claims": ROOT / "docs/CLAIMS.md",
    "nonclaims": ROOT / "docs/NONCLAIMS.md",
    "readme4ai": ROOT / "README4AI.md",
    "reproducibility": ROOT / "docs/REPRODUCIBILITY.md",
    "roadmap": ROOT / "ROADMAP.md",
    "workflow": ROOT / ".github/workflows/finite-adversarial.yml",
    "relation_contract": ROOT / "machine/relation_contract.json",
    "cross_repo_patterns": ROOT / "machine/cross_repo_patterns.json",
    "experiment": ROOT / "experiments/graph_realization/run.py",
    "tests": ROOT / "tests/test_graph_realization.py",
    "receipt": ROOT / "experiments/run_graph_realization.py",
}

EXPECTED_SHA256 = {
    "contract": "f65b7c1c3e3bf29666d09662ba3b9319ff1cd7583362c1c7736d9adca87858ed",
    "results": "c947c612922c68eccaed585ea256295afe9f7bb428d801f06b1e2e41cbacb0d8",
    "sources": "776a7fa9e46f3ee68d75ffaa651d68696899108b24e1f603e19b1f3c9264342b",
    "human": "e75d1b249ca36192d09a22a8359084c7e194fd601e9ef672a8ad2c94cf062687",
}

# Claim-bearing human surfaces are closed by exact Git blob identity.
EXPECTED_HUMAN_BLOBS = {
    "claims": "b7afd74fe589f3032dcf3a34e287af365a39311b",
    "nonclaims": "fae4dc92a8356e309a0502cd82d5df2af29c26ac",
    "readme4ai": "3518fa11fd2bba6fa57b89b6279a271f1d654d29",
    "reproducibility": "9fce9ae1a3ae5a867f79faa90f5309c908c7d071",
    "roadmap": "abce8e80da40f81dae4d7bb56db967cce79abc1e",
}

EXPECTED_RESULT_IDS = {
    "UFT-GR-001", "UFT-GR-002", "UFT-GR-003", "UFT-GR-004",
    "UFT-GR-005", "UFT-GR-006", "CX-GR-001", "CX-GR-002", "CX-GR-003",
}

EXPECTED_PROVED_RESULT_BINDINGS = {
    "UFT-GR-001": {
        "statement": "For a finite labelled carrier X, G_step=(X,A_step) with (x,y) in A_step iff stepRel(x,y) preserves the one-step relation exactly.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-001-finite-relation--digraph-identity",
        "human_heading": "### UFT-GR-001 Finite relation ↔ digraph identity",
    },
    "UFT-GR-002": {
        "statement": "In G_step, Normal_stepRel(x) iff outdegree(x)=0.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-002-normality--zero-outdegree",
        "human_heading": "### UFT-GR-002 Normality ↔ zero outdegree",
    },
    "UFT-GR-003": {
        "statement": "For finite G_step, y is reflexive-transitively reachable from x iff there is a directed walk from x to y; when x!=y a directed path may be chosen.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-003-reachability--directed-walkpath-existence",
        "human_heading": "### UFT-GR-003 Reachability ↔ directed walk/path existence",
    },
    "UFT-GR-004": {
        "statement": "On a finite carrier, forward termination of stepRel is equivalent to absence of directed cycles in G_step.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-004-finite-termination--dag-acyclicity",
        "human_heading": "### UFT-GR-004 Finite termination ↔ DAG acyclicity",
    },
    "UFT-GR-005": {
        "statement": "Every nonempty finite directed graph has at least one sink strongly connected component.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-005-finite-sink-scc-existence",
        "human_heading": "### UFT-GR-005 Finite sink-SCC existence",
    },
    "UFT-GR-006": {
        "statement": "The condensation graph obtained by collapsing strongly connected components of a finite directed graph is acyclic.",
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-006-scc-condensation-is-acyclic",
        "human_heading": "### UFT-GR-006 SCC condensation is acyclic",
    },
}

EXPECTED_BOUNDARIES = {
    "ALGEBRA != GRAPH != EMBEDDING != PHYSICS",
    "GRAPH != DRAWING",
    "COUPLING_GRAPH != PLACEMENT_GRAPH",
    "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
    "LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH",
    "MODULE_INVENTORY != INCIDENCE != GLOBAL_TOPOLOGY",
    "SAME_LOCAL_MODULE != SAME_GLOBAL_CONNECTIVITY",
    "NORMAL_VERTEX != SINK_SCC",
    "SINK_SCC != FIXED_POINT != TERMINATION",
    "LOSSY_PROJECTION != STRUCTURAL_EQUIVALENCE",
    "F3^3=I3 != GRAPH_THEORETIC_3_CYCLE",
    "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
    "MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE",
}

EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/GRAPH_REALIZATION.md",
    "machine_contract": "machine/graph_realization_contract.json",
    "machine_results": "machine/graph_realization_results.json",
    "source_map": "research/GRAPH_REALIZATION_SOURCES.md",
    "validator": "scripts/validate_graph_realization.py",
    "experiment": "experiments/graph_realization/run.py",
    "tests": "tests/test_graph_realization.py",
    "receipt_runner": "experiments/run_graph_realization.py",
    "receipt_version": "1.0.0",
    "base_relation_authority": "machine/relation_contract.json",
    "rule": "Finite relation/digraph realization and typed incidence preserve only declared structure; graph identity, drawings, tetrahedral geometry, material examples, ETQ/SPECTRAL context, and combinatorial invariants do not acquire physical ontology by resemblance or representation.",
}

EXPECTED_AGENT_READS = {
    "docs/NONCLAIMS.md",
    "theory/GRAPH_REALIZATION.md",
    "machine/graph_realization_contract.json",
    "machine/graph_realization_results.json",
    "research/GRAPH_REALIZATION_SOURCES.md",
    "scripts/validate_graph_realization.py",
    "experiments/run_graph_realization.py",
}

PRIVATE_PATTERNS = (
    "mail.google.com", "gmail", "thread_id", "attachment_id", "x_attachment_id",
    "deefiveothree", "connector_", "private-user-images",
)

SEMANTIC_PROMOTION_PATTERNS = (
    "this proves a universal physical ontology",
    "every sink scc is a physical fixed point",
    "sis2 proves e8 information physics",
    "graph realization proves uft-id physics",
    "material positive control proves uft-id physics",
    "pettini proves extra time is physically real",
    "pettini proves uft-id extra-time ontology",
    "current graph theorem authority: pettini",
)

CLAIMS_ANCHORS = (
    "### C7 - Finite relation semantics admit an exact graph-realization layer",
    "**Status:** PROVED",
    "`UFT-GR-001` through `UFT-GR-006`",
    "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
    "ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY",
)

README_ANCHORS = (
    "## Relation and graph-realization authority",
    "machine/graph_realization_contract.json",
    "machine/graph_realization_results.json",
    "theory/GRAPH_REALIZATION.md",
    "scripts/validate_graph_realization.py",
    "experiments/run_graph_realization.py",
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
)

REPRO_ANCHORS = (
    "## Graph-realization conformance boundary",
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
    "python experiments/run_graph_realization.py --json",
    "graph-realization-validation.json",
    "graph-realization-witness.json",
    "graph-realization-receipt.json",
    "docs/CLAIMS.md",
    "README4AI.md",
    "ROADMAP.md",
)

GRAPH_ARTIFACT_COMMANDS = (
    "python scripts/validate_graph_realization.py --json > artifacts/graph-realization-validation.json 2> artifacts/graph-realization-validation.stderr.txt || true",
    "python experiments/graph_realization/run.py --json > artifacts/graph-realization-witness.json 2> artifacts/graph-realization-witness.stderr.txt || true",
    "python experiments/run_graph_realization.py --json > artifacts/graph-realization-receipt.json 2> artifacts/graph-realization-receipt.stderr.txt || true",
)

ROADMAP_GRAPH_COMMANDS = (
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
    "python experiments/run_graph_realization.py --json",
)

PETTINI_START = "# Future model-donor programme — typed causality, projection, and assumption structure"
EXPECTED_PETTINI_PRIMARY_CITATION = (
    "> Marco Pettini, *Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in "
    "(3,2)-Dimensional Spacetime*, arXiv:2606.12457v2 (2026). DOI `10.48550/arXiv.2606.12457`."
)
PETTINI_ANCHORS = (
    "ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR",
    "ANSATZ_UNIQUENESS != GLOBAL_UNIQUENESS",
    "MODEL_CLASS_EXHAUSTION != PHYSICAL_SELECTION",
    "G_L = (V, L, I)",
    "CORRELATION_EDGE != CAUSAL_RESPONSE_EDGE",
    "NONZERO_CORRELATION != CONTROLLABLE_INFLUENCE",
    "FORGET_EDGE_TYPE = POTENTIAL_INFORMATION_LOSS",
    "MICROSTATE != PROJECTION != CONTEXT_LABEL",
    "MANY_TO_ONE_CONTEXT_MAP != PHYSICAL_IDENTITY",
    "CONDITIONAL_DETERMINISM != ENSEMBLE_DETERMINISM",
    "EQUIVARIANCE_ASSUMED != EQUIVARIANCE_DERIVED",
    "WKB_CHARACTERISTIC != EXACT_PROPAGATOR",
    "DERIVED != ASSUMED != CONDITIONALLY_PREDICTED != EMPIRICALLY_OBSERVED",
    "MAP_NONUNIQUENESS != OBSERVABLE_NONROBUSTNESS",
    "PREPRINT_PREDICTION != EXPERIMENTAL_RESULT",
    "FALSIFIABLE != VERIFIED",
    "(3,2)_SPACETIME_MODEL != UFT_ID_ONTOLOGY",
    "BULK_FIELD_XA_MODEL != ESTABLISHED_PHYSICAL_FIELD",
    "PREDICTED_CROSS_PAIR_SIGNAL != OBSERVED_CROSS_PAIR_SIGNAL",
    "PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY",
)

PHYSIOLOGY_START = "# Future physiology and connectomics positive-control programme"
PHYSIOLOGY_ANCHORS = (
    "**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence in this section",
    "| A. Wheatstone pressure transducer -> typed transduction / identifiability | `INTERPRETIVE` |",
    "| B. Haemoglobin oxygen curve -> context-dependent calibration | `INTERPRETIVE` |",
    "| C. Arterial baroreflex -> closed-loop identification | `INTERPRETIVE` |",
    "| D. Windkessel -> reduced-model boundary | `INTERPRETIVE` |",
    "| E. Hodgkin-Huxley -> hidden-state observation fibre | `INTERPRETIVE` |",
    "| F. Fick principle -> conservation-based inference | `INTERPRETIVE` |",
    "| G. HPV16 -> host-context / alternate-mechanism mapping | `INTERPRETIVE` |",
    "| H. FlyWire -> weighted/versioned structure-function mapping | `INTERPRETIVE` |",
    "SHARED_FORMAL_PATTERN != SHARED_PHYSICAL_MECHANISM",
    "INTERPRETIVE_MAPPING != BRIDGE_THEOREM",
    "Delta_B = R1*Rx - R2*R3",
    "CLOSED_LOOP_OBSERVATION != OPEN_LOOP_IDENTIFICATION",
    "LUMPED_MODEL != DISTRIBUTED_SYSTEM",
    "SAME_VOLTAGE != SAME_HIDDEN_STATE",
    "INFERENCE_FORMULA != DIRECT_MEASUREMENT",
    "GENOME_IDENTITY != EXPRESSION_STATE",
    "CONNECTOME != EFFECTOME",
    "THRESHOLDED_GRAPH != ORIGINAL_WEIGHTED_GRAPH",
    "DATASET_VERSION != INCIDENTAL_METADATA",
)

FIVEFOLD_START = "# Future fivefold assembly and rooted-representation donor programme"
FIVEFOLD_ANCHORS = (
    "**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence below",
    "10.1126/sciadv.aau1199",
    "https://en.wikipedia.org/wiki/Pentatonic_scale",
    "CARDINALITY_5 != FIVEFOLD_SYMMETRY",
    "PENTAMER != REGULAR_PENTAGON != C5",
    "NONEDGE != INTERFACE",
    "AVAILABLE_COMPONENTS + CARDINALITY != UNIQUE_ASSEMBLY",
    "PENTAMER != PENTATONIC_SCALE",
    "PROJECTION != INVERSION",
    "UNROOTED_SET_IDENTITY != ROOTED_STRUCTURE_IDENTITY",
    "CHART != OBJECT",
    "ABSENT != UNKNOWN",
    "SHARED_CARDINALITY != SHARED_PHYSICAL_MECHANISM",
)

RECEIPT_SCHEMA_BINDING = '"schema_version": registered_receipt_version(),'

SHELL_CONTROL_PREFIXES = (
    "if ", "elif ", "for ", "while ", "until ", "case ", "select ", "function ",
)
SHELL_CONTROL_WORDS = {"then", "else", "fi", "do", "done", "esac", "{", "}"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def safe_repo_path(value: object, errors: list[str], label: str) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} escapes repository")
        return
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository")
        return
    if not resolved.is_file():
        errors.append(f"{label} does not exist: {value}")


def no_private_locators(value: object, label: str, errors: list[str]) -> None:
    text = json.dumps(value, ensure_ascii=False).casefold() if not isinstance(value, str) else value.casefold()
    for pattern in PRIVATE_PATTERNS:
        if pattern.casefold() in text:
            errors.append(f"{label} contains forbidden private locator token: {pattern}")


def no_semantic_promotion(value: object, label: str, errors: list[str]) -> None:
    text = json.dumps(value, ensure_ascii=False).casefold() if not isinstance(value, str) else value.casefold()
    for pattern in SEMANTIC_PROMOTION_PATTERNS:
        if pattern in text:
            errors.append(f"{label} contains forbidden semantic/ontology promotion: {pattern}")


def require_anchors(text: str, anchors: tuple[str, ...], label: str, errors: list[str]) -> None:
    for anchor in anchors:
        if anchor not in text:
            errors.append(f"{label} missing semantic anchor: {anchor}")


def first_blockquote_after_heading(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        for candidate in lines[index + 1:]:
            stripped = candidate.strip()
            if stripped.startswith("### ") or stripped.startswith("# "):
                return None
            if stripped.startswith(">"):
                return stripped
        return None
    return None


def workflow_step_shell_lines(text: str, step_name: str) -> tuple[str, ...]:
    lines = text.splitlines()
    marker = f"- name: {step_name}"
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        step_indent = len(line) - len(line.lstrip())
        for run_index in range(index + 1, len(lines)):
            run_line = lines[run_index]
            stripped = run_line.strip()
            indent = len(run_line) - len(run_line.lstrip())
            if stripped.startswith("- name:") and indent <= step_indent:
                return ()
            if stripped != "run: |":
                continue
            run_indent = indent
            commands: list[str] = []
            for command_line in lines[run_index + 1:]:
                command_stripped = command_line.strip()
                command_indent = len(command_line) - len(command_line.lstrip())
                if command_stripped and command_indent <= run_indent:
                    break
                if command_stripped and not command_stripped.startswith("#"):
                    commands.append(command_stripped)
            return tuple(commands)
        return ()
    return ()


def has_shell_control_flow(lines: tuple[str, ...]) -> bool:
    for line in lines:
        lowered = line.casefold()
        if lowered in SHELL_CONTROL_WORDS:
            return True
        if any(lowered.startswith(prefix) for prefix in SHELL_CONTROL_PREFIXES):
            return True
    return False


def roadmap_reproducibility_gate_lines(text: str) -> tuple[str, ...]:
    lines = text.splitlines()
    heading = "# Reproducibility gate"
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        fence_index = None
        for probe in range(index + 1, len(lines)):
            stripped = lines[probe].strip()
            if stripped.startswith("# ") and probe > index + 1:
                break
            if stripped == "```bash":
                fence_index = probe
                break
        if fence_index is None:
            return ()
        commands: list[str] = []
        for command_line in lines[fence_index + 1:]:
            stripped = command_line.strip()
            if stripped == "```":
                return tuple(commands)
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
        return ()
    return ()


def validate() -> dict[str, object]:
    errors: list[str] = []
    for path in PATHS.values():
        if not path.is_file():
            errors.append(f"missing graph-realization authority file: {path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "source_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    base_contract = load_json(PATHS["base_contract"])
    relation_contract = load_json(PATHS["relation_contract"])
    cross_repo = load_json(PATHS["cross_repo_patterns"])
    texts = {name: PATHS[name].read_text(encoding="utf-8") for name in (
        "sources", "human", "claims", "nonclaims", "readme4ai", "reproducibility", "roadmap", "workflow", "receipt"
    )}

    for name in ("contract", "results", "sources", "human"):
        if sha256_bytes(PATHS[name].read_bytes()) != EXPECTED_SHA256[name]:
            errors.append(f"{name} canonical payload drift")
    for name, expected_blob in EXPECTED_HUMAN_BLOBS.items():
        if git_blob_sha(PATHS[name].read_bytes()) != expected_blob:
            errors.append(f"{name} canonical human authority blob drift")

    if contract.get("type") != "uft-id-graph-realization-contract":
        errors.append("graph contract type drift")
    if contract.get("schema_version") != "1.0.0":
        errors.append("graph contract schema drift")
    if contract.get("snapshot_date") != "2026-08-20":
        errors.append("graph contract UTC snapshot drift")
    if contract.get("claim_class") != "DEFINITION":
        errors.append("graph contract claim class drift")
    if set(contract.get("hard_boundaries", [])) != EXPECTED_BOUNDARIES:
        errors.append("graph contract hard-boundary set drift")

    central = base_contract.get("graph_realization_authority")
    if central != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central graph_realization_authority payload drift")
    elif isinstance(central, dict):
        for field in ("human", "machine_contract", "machine_results", "source_map", "validator", "experiment", "tests", "receipt_runner", "base_relation_authority"):
            safe_repo_path(central.get(field), errors, f"central graph authority {field}")

    library = base_contract.get("experiment_library")
    if not isinstance(library, dict):
        errors.append("base experiment_library must be an object")
    else:
        if library.get("graph_realization_receipt_runner") != "experiments/run_graph_realization.py":
            errors.append("central graph receipt runner registration drift")
        if library.get("graph_realization_receipt_version") != "1.0.0":
            errors.append("central graph receipt version registration drift")

    reads = base_contract.get("required_agent_reads")
    if not isinstance(reads, list) or any(not isinstance(x, str) or not x for x in reads):
        errors.append("base required_agent_reads must be a list of non-empty strings")
    elif not EXPECTED_AGENT_READS.issubset(set(reads)):
        errors.append("central required_agent_reads missing graph authority surface")

    bridge = contract.get("relation_bridge")
    if not isinstance(bridge, dict):
        errors.append("relation_bridge must be an object")
    else:
        if bridge.get("relation") != "stepRel:X->X->Prop":
            errors.append("graph bridge must preserve stepRel:X->X->Prop")
        if bridge.get("arc_definition") != "(x,y) in A_step iff stepRel(x,y)":
            errors.append("graph bridge adjacency biconditional drift")
        if bridge.get("lost_structure") != []:
            errors.append("exact finite relation/digraph bridge must declare no lost one-step structure")
    if relation_contract.get("primary_types", {}).get("rewrite_relation") != "stepRel:X->X->Prop":
        errors.append("base relation authority no longer exposes canonical stepRel type")

    records = results.get("records")
    ids: set[str] = set()
    if not isinstance(records, list):
        errors.append("graph results must contain a records list")
        records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"graph result {index} must be an object")
            continue
        result_id = record.get("id")
        if not isinstance(result_id, str) or not result_id:
            errors.append(f"graph result {index} has invalid id")
            continue
        if result_id in ids:
            errors.append(f"duplicate graph result id: {result_id}")
        ids.add(result_id)
        claim_class = record.get("claim_class")
        if result_id.startswith("UFT-GR-"):
            if claim_class != "PROVED":
                errors.append(f"{result_id} must remain PROVED")
            expected = EXPECTED_PROVED_RESULT_BINDINGS.get(result_id)
            if expected is None:
                errors.append(f"{result_id} missing canonical theorem binding")
            else:
                if record.get("statement") != expected["statement"]:
                    errors.append(f"{result_id} machine theorem statement drift from frozen human proof")
                if record.get("proof_reference") != expected["proof_reference"]:
                    errors.append(f"{result_id} proof_reference drift from frozen human proof")
                if expected["human_heading"] not in texts["human"]:
                    errors.append(f"{result_id} frozen human theorem heading missing")
        if result_id.startswith("CX-GR-") and claim_class != "COUNTEREXAMPLE":
            errors.append(f"{result_id} must remain COUNTEREXAMPLE")
        evidence = record.get("executable_evidence", record.get("evidence", []))
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{result_id} must retain executable evidence")
        else:
            for path in evidence:
                safe_repo_path(path, errors, f"{result_id} evidence")
    if ids != EXPECTED_RESULT_IDS:
        errors.append("graph result identity set drift")

    source_records = contract.get("sources")
    if not isinstance(source_records, list) or len(source_records) != 2:
        errors.append("graph contract must contain exactly two public donor source records")
        source_records = []
    by_id = {item.get("source_id"): item for item in source_records if isinstance(item, dict)}
    grinberg = by_id.get("GRINBERG-2025-GRAPH-THEORY")
    evers = by_id.get("EVERS-2015-SIS2")
    if not isinstance(grinberg, dict) or grinberg.get("doi") != "10.48550/arXiv.2308.04512":
        errors.append("Grinberg source identity drift")
    if not isinstance(evers, dict) or evers.get("doi") != "10.1021/ic501825r":
        errors.append("Evers SiS2 source identity drift")
    if isinstance(evers, dict) and evers.get("kind") != "peer-reviewed-empirical-source":
        errors.append("Evers source status drift")

    patterns = cross_repo.get("patterns")
    pattern_ids = {item.get("pattern_id") for item in patterns if isinstance(item, dict)} if isinstance(patterns, list) else set()
    for pattern_id in ("XR-P17", "XR-P18"):
        if pattern_id not in pattern_ids:
            errors.append(f"missing existing public context record: {pattern_id}")

    combined = texts["sources"] + "\n" + texts["human"]
    for anchor in (
        "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
        "LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH",
        "SAME LOCAL COORDINATION MOTIF",
        "F3^3=I3 != GRAPH_THEORETIC_3_CYCLE",
        "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
        "No decorative “sacred geometry” image is used as source authority",
    ):
        if anchor not in combined:
            errors.append(f"human graph authority missing semantic anchor: {anchor}")

    require_anchors(texts["claims"], CLAIMS_ANCHORS, "docs/CLAIMS.md graph registration", errors)
    require_anchors(texts["readme4ai"], README_ANCHORS, "README4AI graph registration", errors)
    require_anchors(texts["reproducibility"], REPRO_ANCHORS, "reproducibility graph registration", errors)

    roadmap_gate = roadmap_reproducibility_gate_lines(texts["roadmap"])
    for command in ROADMAP_GRAPH_COMMANDS:
        if command not in roadmap_gate:
            errors.append(f"ROADMAP graph validation gate missing executable command: {command}")

    artifact_lines = workflow_step_shell_lines(texts["workflow"], "Generate deterministic evidence bundle")
    if has_shell_control_flow(artifact_lines):
        errors.append("finite-adversarial graph artifact step may not contain shell control flow that can disable retained graph evidence")
    for command in GRAPH_ARTIFACT_COMMANDS:
        if command not in artifact_lines:
            errors.append(f"finite-adversarial graph artifact retention missing executable command: {command}")
    nonclaims_trigger_count = sum(1 for line in texts["workflow"].splitlines() if line.strip() == '- "docs/NONCLAIMS.md"')
    if nonclaims_trigger_count != 2:
        errors.append("finite-adversarial must trigger on docs/NONCLAIMS.md for PR and main push")

    pettini_index = texts["roadmap"].find(PETTINI_START)
    if pettini_index < 0:
        errors.append("ROADMAP missing Pettini model-donor programme")
        pettini = ""
    else:
        pettini = texts["roadmap"][pettini_index:]
        require_anchors(pettini, PETTINI_ANCHORS, "ROADMAP Pettini model-donor programme", errors)
        citation = first_blockquote_after_heading(pettini, "### Primary model source")
        if citation != EXPECTED_PETTINI_PRIMARY_CITATION:
            errors.append("ROADMAP Pettini primary citation/version drift: expected arXiv:2606.12457v2")
        pettini_lower = pettini.casefold()
        for forbidden in ("**status:** current graph theorem authority", "this section is current graph theorem authority", "pettini is current graph theorem authority"):
            if forbidden in pettini_lower:
                errors.append("ROADMAP Pettini model donor must remain outside current graph theorem authority")
        if "extra-time physics is adopted by uft-id" in pettini_lower:
            errors.append("ROADMAP Pettini model donor illegally promotes extra-time ontology")

    physiology_index = texts["roadmap"].find(PHYSIOLOGY_START)
    if physiology_index < 0:
        errors.append("ROADMAP missing physiology/connectomics positive-control programme")
        physiology = ""
    else:
        physiology = texts["roadmap"][physiology_index:]
        require_anchors(physiology, PHYSIOLOGY_ANCHORS, "ROADMAP physiology/connectomics positive-control programme", errors)

    fivefold_index = texts["roadmap"].find(FIVEFOLD_START)
    if fivefold_index < 0:
        errors.append("ROADMAP missing fivefold assembly/rooted-representation donor programme")
        fivefold = ""
    else:
        fivefold = texts["roadmap"][fivefold_index:]
        require_anchors(fivefold, FIVEFOLD_ANCHORS, "ROADMAP fivefold donor programme", errors)

    if RECEIPT_SCHEMA_BINDING not in texts["receipt"]:
        errors.append("graph receipt schema version must be derived from canonical registry")

    for label, value in (
        ("graph contract", contract),
        ("graph results", results),
        ("central graph authority", central if isinstance(central, dict) else {}),
        ("graph source map", texts["sources"]),
        ("graph human theory", texts["human"]),
    ):
        no_private_locators(value, label, errors)
    for label, value in (
        ("graph contract", contract),
        ("graph results", results),
        ("graph source map", texts["sources"]),
        ("graph human theory", texts["human"]),
        ("claims graph registration", texts["claims"]),
        ("nonclaims authority", texts["nonclaims"]),
        ("README4AI graph registration", texts["readme4ai"]),
        ("reproducibility graph registration", texts["reproducibility"]),
        ("ROADMAP Pettini model donor", pettini),
        ("ROADMAP physiology donor programme", physiology),
        ("ROADMAP fivefold donor programme", fivefold),
    ):
        no_semantic_promotion(value, label, errors)

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(ids),
        "source_count": len(source_records),
        "boundary_count": len(contract.get("hard_boundaries", [])) if isinstance(contract.get("hard_boundaries"), list) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"graph realization authority: ok ({result['result_count']} results, {result['source_count']} sources, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
