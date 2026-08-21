#!/usr/bin/env python3
"""Fail-closed validation for graph realization and typed incidence authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    "artifact_verifier": ROOT / "scripts/verify_graph_artifacts.py",
}

EXPECTED_SHA256 = {
    "contract": "f65b7c1c3e3bf29666d09662ba3b9319ff1cd7583362c1c7736d9adca87858ed",
    "results": "c947c612922c68eccaed585ea256295afe9f7bb428d801f06b1e2e41cbacb0d8",
    "sources": "776a7fa9e46f3ee68d75ffaa651d68696899108b24e1f603e19b1f3c9264342b",
    "human": "e75d1b249ca36192d09a22a8359084c7e194fd601e9ef672a8ad2c94cf062687",
}

EXPECTED_HUMAN_BLOBS = {
    "claims": "b7afd74fe589f3032dcf3a34e287af365a39311b",
    "nonclaims": "fae4dc92a8356e309a0502cd82d5df2af29c26ac",
    "readme4ai": "3518fa11fd2bba6fa57b89b6279a271f1d654d29",
    "reproducibility": "9fce9ae1a3ae5a867f79faa90f5309c908c7d071",
    "roadmap": "71fc504ab6cbe377255f9a5c73695180749fb69d",
}

EXPECTED_RESULT_IDS = {
    "UFT-GR-001", "UFT-GR-002", "UFT-GR-003", "UFT-GR-004",
    "UFT-GR-005", "UFT-GR-006", "CX-GR-001", "CX-GR-002", "CX-GR-003",
}

EXPECTED_RESULT_EVIDENCE = {
    result_id: (
        "executable_evidence" if result_id.startswith("UFT-GR-") else "evidence",
        ("experiments/graph_realization/run.py", "tests/test_graph_realization.py"),
    )
    for result_id in EXPECTED_RESULT_IDS
}

EXPECTED_RESULT_NONCLAIMS = {
    "UFT-GR-001": ("This representation theorem does not attach geometry or physical ontology to the graph.",),
    "UFT-GR-002": ("Zero outdegree does not imply admissibility, fixed-point status, truth, or physical stability.",),
    "UFT-GR-003": ("Finite reachability does not establish infinite-path liveness.",),
    "UFT-GR-004": ("The finite DAG criterion is not a general proof of well-foundedness for arbitrary infinite carriers.",),
    "UFT-GR-005": ("A sink SCC need not contain a normal vertex and is not a fixed point or termination claim.",),
    "UFT-GR-006": ("Acyclic class-level progression does not imply state-level termination inside an SCC.",),
    "CX-GR-001": ("This is a representation-loss counterexample, not a physical information-destruction claim.",),
    "CX-GR-002": ("Shared module count or local motif does not select a unique global topology.",),
    "CX-GR-003": ("A visual embedding may still be useful when its role is explicitly declared.",),
}

EXPECTED_PROVED_RESULT_BINDINGS = {
    "UFT-GR-001": {
        "statement": "For a finite labelled carrier X, G_step=(X,A_step) with (x,y) in A_step iff stepRel(x,y) preserves the one-step relation exactly.",
        "hypotheses": ("X is finite and labelled", "stepRel:X->X->Prop"),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-001-finite-relation--digraph-identity",
        "human_heading": "### UFT-GR-001 Finite relation ↔ digraph identity",
        "human_content_anchor": "For finite labelled `X`, the map from `stepRel` to `G_step` defined above is exact at the one-step level.",
        "human_claim_class": "`PROVED`",
    },
    "UFT-GR-002": {
        "statement": "In G_step, Normal_stepRel(x) iff outdegree(x)=0.",
        "hypotheses": ("G_step is the exact graph realization of stepRel",),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-002-normality--zero-outdegree",
        "human_heading": "### UFT-GR-002 Normality ↔ zero outdegree",
        "human_content_anchor": "\\deg^+_{G_{\\mathrm{step}}}(x)=0.",
        "human_claim_class": "`PROVED`",
    },
    "UFT-GR-003": {
        "statement": "For finite G_step, y is reflexive-transitively reachable from x iff there is a directed walk from x to y; when x!=y a directed path may be chosen.",
        "hypotheses": ("G_step is the exact graph realization of stepRel",),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-003-reachability--directed-walkpath-existence",
        "human_heading": "### UFT-GR-003 Reachability ↔ directed walk/path existence",
        "human_content_anchor": "iff there is a directed walk from `x` to `y` in `G_step`. When `x != y`, repeated vertices may be removed from a finite walk to obtain a directed path.",
        "human_claim_class": "`PROVED`",
    },
    "UFT-GR-004": {
        "statement": "On a finite carrier, forward termination of stepRel is equivalent to absence of directed cycles in G_step.",
        "hypotheses": ("X is finite", "G_step is the exact graph realization of stepRel"),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-004-finite-termination--dag-acyclicity",
        "human_heading": "### UFT-GR-004 Finite termination ↔ DAG acyclicity",
        "human_content_anchor": "G_{\\mathrm{step}}\\text{ has no directed cycle}.",
        "human_claim_class": "`PROVED`",
    },
    "UFT-GR-005": {
        "statement": "Every nonempty finite directed graph has at least one sink strongly connected component.",
        "hypotheses": ("finite nonempty directed graph",),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-005-finite-sink-scc-existence",
        "human_heading": "### UFT-GR-005 Finite sink-SCC existence",
        "human_content_anchor": "Every nonempty finite directed graph has at least one sink SCC.",
        "human_claim_class": "`PROVED`",
    },
    "UFT-GR-006": {
        "statement": "The condensation graph obtained by collapsing strongly connected components of a finite directed graph is acyclic.",
        "hypotheses": ("finite directed graph", "vertices of condensation are SCCs"),
        "proof_reference": "theory/GRAPH_REALIZATION.md#uft-gr-006-scc-condensation-is-acyclic",
        "human_heading": "### UFT-GR-006 SCC condensation is acyclic",
        "human_content_anchor": "`Cond(G)` has no directed cycle.",
        "human_claim_class": "`PROVED`",
    },
}

EXPECTED_COUNTEREXAMPLE_BINDINGS = {
    "CX-GR-001": {
        "statement": "Two distinct rich directed multigraph records can collapse to the same simple endpoint-adjacency relation.",
        "fixture": "parallel labelled arcs u->v versus one unlabelled arc u->v",
        "kills": ("LOSSY_PROJECTION_IMPLIES_STRUCTURAL_EQUIVALENCE", "SIMPLE_ADJACENCY_DETERMINES_RICH_INCIDENCE"),
        "human_heading": "### CX-GR-001 Rich-to-simple projection loses arc identity",
        "human_content_anchor": "The projection from rich arc records to simple endpoint adjacency is non-injective in general.",
        "human_claim_class": "`COUNTEREXAMPLE`",
    },
    "CX-GR-002": {
        "statement": "The same labelled module set can support distinct typed incidence relations.",
        "fixture": "M={a,b,c}: chain a-b-c versus triangle a-b-c-a",
        "kills": ("MODULE_INVENTORY_DETERMINES_GLOBAL_NETWORK",),
        "human_heading": "### CX-GR-002 Module inventory does not determine incidence",
        "human_content_anchor": "The inventory is identical while the global connectivity differs.",
        "human_claim_class": "`COUNTEREXAMPLE`",
    },
    "CX-GR-003": {
        "statement": "One abstract graph admits multiple coordinate drawings with identical adjacency.",
        "fixture": "K1,3 drawn with different coordinates",
        "kills": ("DRAWING_COORDINATES_ARE_GRAPH_IDENTITY", "VISUAL_RESEMBLANCE_IMPLIES_PHYSICAL_EQUIVALENCE"),
        "human_heading": "### CX-GR-003 Multiple drawings, one graph",
        "human_content_anchor": "The drawings differ while the abstract labelled adjacency is unchanged.",
        "human_claim_class": "`COUNTEREXAMPLE`",
    },
}

EXPECTED_POSITIVE_CONTROLS = [
    {
        "boundary": "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
        "claim_class": "DEFINITION",
        "id": "PC-GR-TETRA-K4",
        "statement": "The 1-skeleton of a geometric tetrahedron is the complete graph K4 on its four corner vertices.",
    },
    {
        "boundary": "SAME_LOCAL_COORDINATION_MOTIF != SAME_GLOBAL_CONNECTIVITY",
        "claim_class": "EMPIRICAL",
        "id": "PC-GR-SIS2",
        "statement": "The cited SiS2 source reports phases built from SiS4 tetrahedral coordination units with different edge-sharing and corner-sharing connectivity patterns.",
    },
    {
        "boundary": "ALGEBRA != GRAPH != EMBEDDING != PHYSICS",
        "claim_class": "DIAGNOSTIC",
        "context_refs": ["XR-P17", "XR-P18"],
        "id": "PC-GR-ETQ-INVENTORY",
        "statement": "XR-P17/XR-P18 may motivate separate module-inventory, coupling-graph, placement-graph, and embedding layers; no such layer is promoted into topology or physics without an explicit bridge.",
    },
]

EXPECTED_GRAPH_TYPES = {
    "condensation": "quotient digraph whose vertices are strong components and whose inter-component arcs are induced by G_step",
    "finite_termination": "G_step has no directed cycle",
    "normal_vertex": "outdegree_G_step(x)=0",
    "sink_strong_component": "strong component with no outgoing arc to another strong component",
    "strong_component": "equivalence class under mutual directed reachability",
}
EXPECTED_PROJECTION_BOUNDARY = {
    "boundary": "LOSSY_PROJECTION != STRUCTURAL_EQUIVALENCE",
    "noninjective_in_general": True,
    "rich_to_simple": "forget arc identity, multiplicity, and/or link labels while retaining only endpoint adjacency",
}
EXPECTED_CONTRACT_SCOPE = (
    "Finite labelled binary endorelations, their exact directed-graph realizations, typed incidence descriptions, "
    "finite strong-component structure, and representation-loss diagnostics. No physical ontology is inferred "
    "from graph, geometry, material, sonification, or visualization similarity."
)

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

C7_HEADING = "### C7 - Finite relation semantics admit an exact graph-realization layer"
EXPECTED_C7_STATUS = "PROVED"
CLAIMS_ANCHORS = (
    C7_HEADING,
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
GRAPH_ARTIFACT_VERIFY_COMMAND = "python scripts/verify_graph_artifacts.py artifacts"
EXPECTED_VERIFY_STEP_DIRECTIVES = ("if: always()", "run: |")
ROADMAP_GRAPH_COMMANDS = (
    "python scripts/validate_graph_realization.py",
    "python experiments/graph_realization/run.py --json",
    "python experiments/run_graph_realization.py --json",
)

EXPECTED_EVIDENCE_BUNDLE_LINES = (
    "mkdir -p artifacts",
    "python experiments/run_pr2.py --json > artifacts/pr2-receipt.json 2> artifacts/pr2-receipt.stderr.txt || true",
    "python experiments/counterexamples/finite_entropy_signs/run.py --json > artifacts/finite-signs.json 2> artifacts/finite-signs.stderr.txt || true",
    "python experiments/representation/coarse_graining/run.py --json > artifacts/coarse-graining.json 2> artifacts/coarse-graining.stderr.txt || true",
    "python experiments/reproduction/vopson_2026_polygons/run.py --max-N 16 --max-n 6 --json > artifacts/polygon-audit.json 2> artifacts/polygon-audit.stderr.txt || true",
    "python experiments/reproduction/vopson_2019_mei/run.py --json > artifacts/vopson-2019-mei.json 2> artifacts/vopson-2019-mei.stderr.txt || true",
    "python experiments/run_pr6.py --json > artifacts/vopson-2019-mei-receipt.json 2> artifacts/vopson-2019-mei-receipt.stderr.txt || true",
    "python scripts/validate_vopson_2019_mei.py --json > artifacts/vopson-2019-mei-validation.json 2> artifacts/vopson-2019-mei-validation.stderr.txt || true",
    "python scripts/validate_cross_repo_patterns.py --json > artifacts/cross-repo-pattern-validation.json 2> artifacts/cross-repo-pattern-validation.stderr.txt || true",
    "python experiments/run_cross_repo.py --json > artifacts/cross-repo-receipt.json 2> artifacts/cross-repo-receipt.stderr.txt || true",
    "python scripts/validate_historical_lineage.py --json > artifacts/historical-lineage-validation.json 2> artifacts/historical-lineage-validation.stderr.txt || true",
    "python experiments/run_lineage.py --json > artifacts/historical-lineage-receipt.json 2> artifacts/historical-lineage-receipt.stderr.txt || true",
    "python scripts/validate_formalization_contracts.py --json > artifacts/pr8-formalization-validation.json 2> artifacts/pr8-formalization-validation.stderr.txt || true",
    "python experiments/formalization/run.py --json > artifacts/pr8-formalization-witness.json 2> artifacts/pr8-formalization-witness.stderr.txt || true",
    "python experiments/run_pr8.py --json > artifacts/pr8-formalization-receipt.json 2> artifacts/pr8-formalization-receipt.stderr.txt || true",
    "python scripts/validate_observation_specs.py --json > artifacts/pr9-observation-validation.json 2> artifacts/pr9-observation-validation.stderr.txt || true",
    "python experiments/observation/run.py --json > artifacts/pr9-observation-witness.json 2> artifacts/pr9-observation-witness.stderr.txt || true",
    "python experiments/run_pr9.py --json > artifacts/pr9-observation-receipt.json 2> artifacts/pr9-observation-receipt.stderr.txt || true",
    "python scripts/validate_relation_core.py --json > artifacts/pr11-relation-validation.json 2> artifacts/pr11-relation-validation.stderr.txt || true",
    "python experiments/relation/run.py --json > artifacts/pr11-relation-witness.json 2> artifacts/pr11-relation-witness.stderr.txt || true",
    "python experiments/run_pr11.py --json > artifacts/pr11-relation-receipt.json 2> artifacts/pr11-relation-receipt.stderr.txt || true",
    GRAPH_ARTIFACT_COMMANDS[0], GRAPH_ARTIFACT_COMMANDS[1], GRAPH_ARTIFACT_COMMANDS[2],
    "python scripts/validate_reproducibility.py --json > artifacts/reproducibility-validation.json 2> artifacts/reproducibility-validation.stderr.txt || true",
)

PETTINI_START = "# Future model-donor programme — typed causality, projection, and assumption structure"
EXPECTED_PETTINI_STATUS = (
    "ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR. This section is not current graph theorem authority, does not "
    "renumber planned PR #12-#18, and does not adopt the source model as UFT-ID ontology."
)
EXPECTED_PETTINI_PRIMARY_CITATION = (
    "> Marco Pettini, *Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in "
    "(3,2)-Dimensional Spacetime*, arXiv:2606.12457v2 (2026). DOI `10.48550/arXiv.2606.12457`."
)
PETTINI_ANCHORS = (
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

PHYSIOLOGY_START = "# Future physiology and connectomics positive-control programme — typed transduction, feedback, hidden state, alternate mechanisms, and structure/function boundaries"
EXPECTED_PHYSIOLOGY_STATUS = (
    "ROADMAP-ONLY POSITIVE-CONTROL / MODEL-DONOR PROGRAMME. It does not renumber PR #12-#18 "
    "and does not make physiology, virology, or neuroscience UFT-ID ontology."
)
EXPECTED_PHYSIOLOGY_CLAIM_CLASS = (
    "`INTERPRETIVE` for every source-to-UFT-ID correspondence in this section until a later explicit "
    "BridgeCore record supplies source type, target type, source/target dynamics, preserved structure, "
    "lost structure, scope, and measurement/observation bridge. External source facts retain their own "
    "evidentiary status; the mapping into UFT-ID is not promoted above `INTERPRETIVE` here."
)
PHYSIOLOGY_ANCHORS = (
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
EXPECTED_PHYSIOLOGY_CITATIONS = {
    "A": {
        "heading": "### A. Wheatstone pressure transducer — typed K4, balance residual, transduction, and identifiability",
        "marker": "Educational/clinical engineering source:",
        "citations": (
            "- Deranged Physiology, *Wheatstone bridge pressure transducer*: https://derangedphysiology.com/main/required-reading/intensive-care-procedures/Chapter-216/wheatstone-bridge-pressure-transducer",
        ),
    },
    "B": {
        "heading": "### B. Haemoglobin oxygen-dissociation curve — context-dependent calibration",
        "marker": "Public source:",
        "citations": (
            "- *Relating oxygen partial pressure, saturation and content: the haemoglobin–oxygen dissociation curve*, PMCID `PMC4666443`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4666443/",
        ),
    },
    "C": {
        "heading": "### C. Arterial baroreflex — closed-loop observation versus open-loop identification",
        "marker": "Public source:",
        "citations": (
            "- *Systems physiology of the baroreflex during orthostatic stress: from animals to humans*, PMCID `PMC4086024`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4086024/",
        ),
    },
    "D": {
        "heading": "### D. Arterial Windkessel — useful reduced model versus distributed realization",
        "marker": "Canonical review source:",
        "citations": (
            "- Westerhof, N., Lankhaar, J.-W., Westerhof, B.E. *The arterial Windkessel.* Med Biol Eng Comput 47, 131-141 (2009). DOI `10.1007/s11517-008-0359-2`.",
        ),
    },
    "E": {
        "heading": "### E. Hodgkin-Huxley — hidden state and observation fibres",
        "marker": "Primary mathematical-physiology source:",
        "citations": (
            "- Hodgkin, A.L. & Huxley, A.F. *A quantitative description of membrane current and its application to conduction and excitation in nerve.* J Physiol 117, 500-544 (1952). DOI `10.1113/jphysiol.1952.sp004764`.",
        ),
    },
    "F": {
        "heading": "### F. Fick cardiac-output principle — conservation-based inference and assumption sensitivity",
        "marker": "Public methodological source:",
        "citations": (
            "- *Methods in pharmacology: measurement of cardiac output*, PMCID `PMC3045542`: https://pmc.ncbi.nlm.nih.gov/articles/PMC3045542/",
        ),
    },
    "G": {
        "heading": "### G. HPV16 — host-context dependence and alternate routes to similar downstream classes",
        "marker": "Public sources:",
        "citations": (
            "- *Manipulation of Epithelial Differentiation by HPV Oncoproteins*, PMCID `PMC6549445`: https://pmc.ncbi.nlm.nih.gov/articles/PMC6549445/",
            "- *IGF axis and other factors in HPV-related and HPV-unrelated carcinogenesis*, PMCID `PMC4240475`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4240475/",
        ),
    },
    "H": {
        "heading": "### H. FlyWire adult Drosophila connectome — weighted directed structure, threshold projection, SCCs, versioning, and structure/function separation",
        "marker": "Primary/companion sources:",
        "citations": (
            "- Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature 634, 124-138 (2024). DOI `10.1038/s41586-024-07558-y`.",
            "- Shiu, P.K. et al. *Network statistics of the whole-brain connectome of Drosophila.* Nature 634 (2024). DOI `10.1038/s41586-024-07968-y`.",
        ),
    },
}

FIVEFOLD_START = "# Future fivefold assembly and rooted-representation donor programme — cardinality, asymmetry, interfaces, and coordinate charts"
EXPECTED_FIVEFOLD_STATUS = (
    "ROADMAP-ONLY MODEL-DONOR PROGRAMME. This section does not renumber PR #12-#18 and does not infer "
    "a universal significance for the number five."
)
EXPECTED_FIVEFOLD_CLAIM_CLASS = (
    "`INTERPRETIVE` for every source-to-UFT-ID correspondence below. The empirical IgM findings remain "
    "external empirical evidence; the musical facts remain background/source facts; the UFT-ID abstractions "
    "are interpretive until explicit BridgeCore objects and independent mathematical fixtures are supplied."
)
FIVEFOLD_ANCHORS = (
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

NUMEROSITY_START = "# Future 3-4-5 finite numerosity and semantic-lifting stress programme"
EXPECTED_NUMEROSITY_STATUS = (
    "ROADMAP-ONLY MODEL-DONOR / ADVERSARIAL PROGRAMME. It does not renumber PR #12-#18, does not claim "
    "that 3, 4, or 5 are physically privileged, and does not infer a common mechanism from repeated cardinalities."
)
EXPECTED_NUMEROSITY_CLAIM_CLASS = (
    "`INTERPRETIVE` for every source-to-UFT-ID correspondence in this section until explicit "
    "BridgeCore objects and independent mathematical fixtures exist."
)
NUMEROSITY_ANCHORS = (
    "NumberSpec = (n, role, carrier, structure, semantics, scope)",
    "NUMBER != ROLE",
    "CARDINALITY_3 != ARITY_3 != DIMENSION_3 != RADIX_3",
    "FIN3 != C3 != TRIANGLE != QUTRIT",
    "FINITE_ITERATION != LIMIT_OBJECT",
    "TETRAHEDRAL_HEURISTIC != GEOMETRIC_TETRAHEDRON",
    "FIXED_TOTAL_INTERVAL != UNIQUE_INTERVAL_DECOMPOSITION",
    "MUSICAL_GENUS != TOPOLOGICAL_GENUS",
    "TETRABENAZINE != TETRACYCLIC_ANTIDEPRESSANT",
    "CARDINALITY_5 != FIVEFOLD_SYMMETRY",
    "3^2 + 4^2 = 5^2",
    "ARITHMETIC_RELATION != STRUCTURAL_BRIDGE",
    "NUMERIC_RELATION + LABEL_ASSIGNMENT != STRUCTURAL_THEOREM",
    "NO_SEMANTIC_LIFTING_WITHOUT_A_BRIDGE",
    "NUMBER != ROLE != STRUCTURE != MECHANISM != ONTOLOGY",
)

EXPECTED_GRINBERG = {
    "author": "Darij Grinberg",
    "doi": "10.48550/arXiv.2308.04512",
    "identifier": "arXiv:2308.04512v3",
    "kind": "public-mathematical-source",
    "not_inherited": [
        "no physical ontology",
        "no claim that graph-theoretic equivalence establishes semantic or physical equivalence",
    ],
    "role": "mathematical donor for graph/digraph representation, drawing separation, adjacency matrices, SCCs, arborescences, matrix-tree machinery, and Menger-type path/cut results",
    "version_date": "2025-06-08",
    "source_status": "arXiv-course-notes-preprint",
    "title": "An introduction to graph theory",
}
EXPECTED_GRINBERG_CITATION = (
    "> Darij Grinberg, *An introduction to graph theory*, arXiv:2308.04512v3, "
    "Spring 2025 edition, version dated 8 June 2025. DOI `10.48550/arXiv.2308.04512`."
)
EXPECTED_EVERS = {
    "source_id": "EVERS-2015-SIS2",
    "authors": ["Jürgen Evers", "Peter Mayer", "Leonhard Möckl", "Gilbert Oehlinger", "Ralf Köppe", "Hansgeorg Schnöckel"],
    "doi": "10.1021/ic501825r",
    "issue": 4,
    "journal": "Inorganic Chemistry",
    "kind": "peer-reviewed-empirical-source",
    "not_inherited": [
        "SiS2 chemistry is not a UFT-ID ontology",
        "tetrahedral material structure does not validate ETQ, E8, Fuller geometry, or information physics",
    ],
    "pages": "1240-1253",
    "role": "positive-control example that a shared local SiS4 tetrahedral coordination motif can participate in distinct edge-sharing, mixed edge/corner-sharing, and corner-sharing global structures",
    "title": "Two High-Pressure Phases of SiS2 as Missing Links between the Extremes of Only Edge-Sharing and Only Corner-Sharing Tetrahedra",
    "volume": 54,
    "year": 2015,
}
EXPECTED_EVERS_CITATION = (
    "> Jürgen Evers, Peter Mayer, Leonhard Möckl, Gilbert Oehlinger, Ralf Köppe, and Hansgeorg Schnöckel, “Two High-Pressure Phases of SiS2 as Missing Links between the Extremes of Only Edge-Sharing and Only Corner-Sharing Tetrahedra,” *Inorganic Chemistry* **54**(4), 1240–1253 (2015). DOI `10.1021/ic501825r`."
)

EXPECTED_HUMAN_DONORS = {
    "Grinberg": {
        "heading": "## 1. Darij Grinberg — graph-theory donor",
        "status": "Source status: public arXiv course notes / mathematical preprint. The source is not treated as a peer-reviewed empirical paper.",
        "section_sha256": "cc56abaa85a0dcd5c047fb522575ec8ea5483e4ce6f93464f6f0050538cf43da",
    },
    "Evers": {
        "heading": "## 2. Evers et al. — SiS2 positive structural control",
        "status": "Source status: peer-reviewed journal article.",
        "section_sha256": "4a91c119a338152b1b3522d1773aa3fc608e220c4ac05309bd7076d09357a09c",
    },
}

RECEIPT_SCHEMA_BINDING = '"schema_version": registered_receipt_version(),'
SHELL_CONTROL_PREFIXES = (
    "if ", "elif ", "for ", "while ", "until ", "case ", "select ", "function ",
    "source ", ". ", "eval ",
)
SHELL_CONTROL_WORDS = {"then", "else", "fi", "do", "done", "esac", "{", "}"}
SHELL_EARLY_TERMINATION_RE = re.compile(r"(?:^|[;&|]\s*)(?:exit|return|exec)(?:\s|$)", re.IGNORECASE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
            if stripped.startswith("#"):
                return None
            if stripped.startswith(">"):
                return stripped
        return None
    return None


def markdown_heading_count(text: str, heading: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == heading)


def markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    try:
        index = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return None
    match = re.match(r"^(#+)\s", heading)
    if match is None:
        return None
    level = len(match.group(1))
    section = [lines[index]]
    for line in lines[index + 1:]:
        candidate = re.match(r"^(#+)\s", line.strip())
        if candidate is not None and len(candidate.group(1)) <= level:
            break
        section.append(line)
    return "\n".join(section)


def normalized_markdown_section(section: str) -> str:
    return "\n".join(line.rstrip() for line in section.strip().splitlines())


def markdown_metadata_value(section: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    matches = [
        line.strip()[len(prefix):]
        for line in section.splitlines()[1:]
        if line.strip().startswith(prefix)
    ]
    return matches[0] if len(matches) == 1 else None


def unique_prefixed_line(section: str, prefix: str) -> str | None:
    matches = [
        line.strip()
        for line in section.splitlines()[1:]
        if line.strip().startswith(prefix)
    ]
    return matches[0] if len(matches) == 1 else None


def markdown_bullets_after_marker(section: str, marker: str) -> tuple[str, ...]:
    lines = section.splitlines()
    indices = [i for i, line in enumerate(lines) if line.strip() == marker]
    if len(indices) != 1:
        return ()
    index = indices[0] + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    bullets: list[str] = []
    while index < len(lines) and lines[index].strip().startswith("- "):
        bullets.append(lines[index].strip())
        index += 1
    return tuple(bullets)


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


def workflow_step_directives(text: str, step_name: str) -> tuple[str, ...]:
    lines = text.splitlines()
    marker = f"- name: {step_name}"
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        step_indent = len(line) - len(line.lstrip())
        directives: list[str] = []
        run_indent: int | None = None
        for candidate in lines[index + 1:]:
            stripped = candidate.strip()
            indent = len(candidate) - len(candidate.lstrip())
            if stripped.startswith("- name:") and indent <= step_indent:
                break
            if not stripped or stripped.startswith("#"):
                continue
            if indent <= step_indent:
                break
            if run_indent is not None and indent > run_indent:
                continue
            if run_indent is not None and indent <= run_indent:
                run_indent = None
            directives.append(stripped)
            if stripped == "run: |":
                run_indent = indent
        return tuple(directives)
    return ()


def workflow_step_has_always(text: str, step_name: str) -> bool:
    return "if: always()" in workflow_step_directives(text, step_name)


def workflow_job_has_top_level_directive(text: str, job_name: str, prefix: str) -> bool:
    lines = text.splitlines()
    marker = f"{job_name}:"
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        job_indent = len(line) - len(line.lstrip())
        for candidate in lines[index + 1:]:
            stripped = candidate.strip()
            indent = len(candidate) - len(candidate.lstrip())
            if stripped and indent <= job_indent:
                break
            if stripped and indent == job_indent + 2 and stripped.startswith(prefix):
                return True
        return False
    return False


def has_shell_control_flow(lines: tuple[str, ...]) -> bool:
    for line in lines:
        lowered = line.casefold()
        if lowered in SHELL_CONTROL_WORDS:
            return True
        if any(lowered.startswith(prefix) for prefix in SHELL_CONTROL_PREFIXES):
            return True
        if SHELL_EARLY_TERMINATION_RE.search(line):
            return True
    return False


def roadmap_reproducibility_gate_lines(text: str) -> tuple[str, ...]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "# Reproducibility gate":
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

    unique_authority_headings: list[tuple[str, str, str]] = [
        ("claims", C7_HEADING, "docs/CLAIMS.md C7"),
        ("roadmap", PETTINI_START, "ROADMAP Pettini programme"),
        ("roadmap", PHYSIOLOGY_START, "ROADMAP physiology programme"),
        ("roadmap", FIVEFOLD_START, "ROADMAP fivefold programme"),
        ("roadmap", NUMEROSITY_START, "ROADMAP numerosity programme"),
    ]
    unique_authority_headings.extend(
        ("human", spec["human_heading"], result_id)
        for result_id, spec in EXPECTED_PROVED_RESULT_BINDINGS.items()
    )
    unique_authority_headings.extend(
        ("human", spec["human_heading"], result_id)
        for result_id, spec in EXPECTED_COUNTEREXAMPLE_BINDINGS.items()
    )
    unique_authority_headings.extend(
        ("sources", spec["heading"], f"{donor_name} human donor")
        for donor_name, spec in EXPECTED_HUMAN_DONORS.items()
    )
    unique_authority_headings.extend(
        ("roadmap", spec["heading"], f"physiology donor {donor_id}")
        for donor_id, spec in EXPECTED_PHYSIOLOGY_CITATIONS.items()
    )
    for text_key, heading, label in unique_authority_headings:
        if markdown_heading_count(texts[text_key], heading) != 1:
            errors.append(f"{label} heading multiplicity drift")

    for name in ("contract", "results", "sources", "human"):
        if sha256_bytes(PATHS[name].read_bytes()) != EXPECTED_SHA256[name]:
            errors.append(f"{name} canonical payload drift")
    for name, expected_blob in EXPECTED_HUMAN_BLOBS.items():
        if git_blob_sha(PATHS[name].read_bytes()) != expected_blob:
            errors.append(f"{name} canonical human authority blob drift")

    if contract.get("type") != "uft-id-graph-realization-contract": errors.append("graph contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("graph contract schema drift")
    if contract.get("snapshot_date") != "2026-08-20": errors.append("graph contract UTC snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("graph contract claim class drift")
    if contract.get("scope") != EXPECTED_CONTRACT_SCOPE: errors.append("graph contract scope drift")
    if contract.get("graph_types") != EXPECTED_GRAPH_TYPES: errors.append("graph type definition payload drift")
    if contract.get("projection_boundary") != EXPECTED_PROJECTION_BOUNDARY: errors.append("graph projection-boundary payload drift")
    if set(contract.get("hard_boundaries", [])) != EXPECTED_BOUNDARIES: errors.append("graph contract hard-boundary set drift")
    if contract.get("positive_controls") != EXPECTED_POSITIVE_CONTROLS: errors.append("graph positive-control authority payload drift")

    if results.get("type") != "uft-id-graph-realization-results": errors.append("graph results type drift")
    if results.get("schema_version") != "1.0.0": errors.append("graph results schema drift")
    if results.get("snapshot_date") != "2026-08-20": errors.append("graph results UTC snapshot drift")

    central = base_contract.get("graph_realization_authority")
    if central != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central graph_realization_authority payload drift")
    elif isinstance(central, dict):
        for field in ("human", "machine_contract", "machine_results", "source_map", "validator", "experiment", "tests", "receipt_runner", "base_relation_authority"):
            safe_repo_path(central.get(field), errors, f"central graph authority {field}")

    library = base_contract.get("experiment_library")
    if not isinstance(library, dict): errors.append("base experiment_library must be an object")
    else:
        if library.get("graph_realization_receipt_runner") != "experiments/run_graph_realization.py": errors.append("central graph receipt runner registration drift")
        if library.get("graph_realization_receipt_version") != "1.0.0": errors.append("central graph receipt version registration drift")

    reads = base_contract.get("required_agent_reads")
    if not isinstance(reads, list) or any(not isinstance(x, str) or not x for x in reads): errors.append("base required_agent_reads must be a list of non-empty strings")
    elif not EXPECTED_AGENT_READS.issubset(set(reads)): errors.append("central required_agent_reads missing graph authority surface")

    bridge = contract.get("relation_bridge")
    if not isinstance(bridge, dict): errors.append("relation_bridge must be an object")
    else:
        if bridge.get("relation") != "stepRel:X->X->Prop": errors.append("graph bridge must preserve stepRel:X->X->Prop")
        if bridge.get("arc_definition") != "(x,y) in A_step iff stepRel(x,y)": errors.append("graph bridge adjacency biconditional drift")
        if bridge.get("lost_structure") != []: errors.append("exact finite relation/digraph bridge must declare no lost one-step structure")
    if relation_contract.get("primary_types", {}).get("rewrite_relation") != "stepRel:X->X->Prop": errors.append("base relation authority no longer exposes canonical stepRel type")

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
        if result_id in ids: errors.append(f"duplicate graph result id: {result_id}")
        ids.add(result_id)

        expected_nonclaims = EXPECTED_RESULT_NONCLAIMS.get(result_id)
        nonclaims = record.get("nonclaims")
        if expected_nonclaims is None:
            errors.append(f"{result_id} missing canonical nonclaim binding")
        elif not isinstance(nonclaims, list) or tuple(nonclaims) != expected_nonclaims:
            errors.append(f"{result_id} theorem/counterexample nonclaims drift")

        claim_class = record.get("claim_class")
        if result_id.startswith("UFT-GR-"):
            if claim_class != "PROVED": errors.append(f"{result_id} must remain PROVED")
            expected = EXPECTED_PROVED_RESULT_BINDINGS.get(result_id)
            if expected is None:
                errors.append(f"{result_id} missing canonical theorem binding")
            else:
                if record.get("statement") != expected["statement"]: errors.append(f"{result_id} machine theorem statement drift from frozen human proof")
                hypotheses = record.get("hypotheses")
                if not isinstance(hypotheses, list) or tuple(hypotheses) != expected["hypotheses"]: errors.append(f"{result_id} theorem hypotheses drift from frozen human proof")
                if record.get("proof_reference") != expected["proof_reference"]: errors.append(f"{result_id} proof_reference drift from frozen human proof")
                section = markdown_section(texts["human"], expected["human_heading"])
                if section is None:
                    errors.append(f"{result_id} frozen human theorem heading missing")
                else:
                    if markdown_metadata_value(section, "Claim class") != expected["human_claim_class"]:
                        errors.append(f"{result_id} human theorem claim class drift")
                    if expected["human_content_anchor"] not in section:
                        errors.append(f"{result_id} frozen human theorem content drift")
        elif result_id.startswith("CX-GR-"):
            if claim_class != "COUNTEREXAMPLE": errors.append(f"{result_id} must remain COUNTEREXAMPLE")
            expected = EXPECTED_COUNTEREXAMPLE_BINDINGS.get(result_id)
            if expected is None:
                errors.append(f"{result_id} missing canonical counterexample binding")
            else:
                if record.get("statement") != expected["statement"]: errors.append(f"{result_id} counterexample statement drift")
                if record.get("fixture") != expected["fixture"]: errors.append(f"{result_id} counterexample fixture drift")
                kills = record.get("kills")
                if not isinstance(kills, list) or tuple(kills) != expected["kills"]: errors.append(f"{result_id} counterexample kills drift")
                section = markdown_section(texts["human"], expected["human_heading"])
                if section is None:
                    errors.append(f"{result_id} frozen human counterexample heading missing")
                else:
                    if markdown_metadata_value(section, "Claim class") != expected["human_claim_class"]:
                        errors.append(f"{result_id} human counterexample claim class drift")
                    if expected["human_content_anchor"] not in section:
                        errors.append(f"{result_id} frozen human counterexample content drift")

        evidence_spec = EXPECTED_RESULT_EVIDENCE.get(result_id)
        if evidence_spec is None: errors.append(f"{result_id} missing canonical evidence binding")
        else:
            field, expected_paths = evidence_spec
            evidence = record.get(field)
            if not isinstance(evidence, list) or tuple(evidence) != expected_paths: errors.append(f"{result_id} executable evidence set drift")
            else:
                for path in evidence: safe_repo_path(path, errors, f"{result_id} evidence")

    if ids != EXPECTED_RESULT_IDS: errors.append("graph result identity set drift")

    source_records = contract.get("sources")
    if not isinstance(source_records, list) or len(source_records) != 2:
        errors.append("graph contract must contain exactly two public donor source records")
        source_records = []
    by_id = {item.get("source_id"): item for item in source_records if isinstance(item, dict)}
    grinberg = by_id.get("GRINBERG-2025-GRAPH-THEORY")
    evers = by_id.get("EVERS-2015-SIS2")
    if not isinstance(grinberg, dict): errors.append("Grinberg source identity drift")
    else:
        for key, expected_value in EXPECTED_GRINBERG.items():
            if grinberg.get(key) != expected_value: errors.append(f"Grinberg source {key} drift")
    if EXPECTED_GRINBERG_CITATION not in texts["sources"]: errors.append("Grinberg human source citation/version drift")

    if not isinstance(evers, dict): errors.append("Evers SiS2 source identity drift")
    else:
        for key, expected_value in EXPECTED_EVERS.items():
            if evers.get(key) != expected_value: errors.append(f"Evers source {key} drift")
    if EXPECTED_EVERS_CITATION not in texts["sources"]: errors.append("Evers human source citation drift")

    for donor_name, spec in EXPECTED_HUMAN_DONORS.items():
        section = markdown_section(texts["sources"], spec["heading"])
        if section is None:
            errors.append(f"{donor_name} human donor section missing")
            continue
        if unique_prefixed_line(section, "Source status:") != spec["status"]:
            errors.append(f"{donor_name} human donor status drift")
        normalized = normalized_markdown_section(section)
        if sha256_bytes(normalized.encode("utf-8")) != spec["section_sha256"]:
            errors.append(f"{donor_name} human donor section drift")

    patterns = cross_repo.get("patterns")
    pattern_ids = {item.get("pattern_id") for item in patterns if isinstance(item, dict)} if isinstance(patterns, list) else set()
    for pattern_id in ("XR-P17", "XR-P18"):
        if pattern_id not in pattern_ids: errors.append(f"missing existing public context record: {pattern_id}")

    combined = texts["sources"] + "\n" + texts["human"]
    for anchor in (
        "TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH",
        "LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH",
        "SAME LOCAL COORDINATION MOTIF",
        "F3^3=I3 != GRAPH_THEORETIC_3_CYCLE",
        "FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF",
        "No decorative “sacred geometry” image is used as source authority",
    ):
        if anchor not in combined: errors.append(f"human graph authority missing semantic anchor: {anchor}")

    require_anchors(texts["claims"], CLAIMS_ANCHORS, "docs/CLAIMS.md graph registration", errors)
    c7 = markdown_section(texts["claims"], C7_HEADING)
    if c7 is None:
        errors.append("docs/CLAIMS.md C7 section missing")
    elif markdown_metadata_value(c7, "Status") != EXPECTED_C7_STATUS:
        errors.append("docs/CLAIMS.md C7 status drift")
    require_anchors(texts["readme4ai"], README_ANCHORS, "README4AI graph registration", errors)
    require_anchors(texts["reproducibility"], REPRO_ANCHORS, "reproducibility graph registration", errors)

    roadmap_gate = roadmap_reproducibility_gate_lines(texts["roadmap"])
    for command in ROADMAP_GRAPH_COMMANDS:
        if command not in roadmap_gate: errors.append(f"ROADMAP graph validation gate missing executable command: {command}")

    artifact_lines = workflow_step_shell_lines(texts["workflow"], "Generate deterministic evidence bundle")
    if has_shell_control_flow(artifact_lines): errors.append("finite-adversarial graph artifact step may not contain shell control flow or early termination that can disable retained graph evidence")
    if artifact_lines != EXPECTED_EVIDENCE_BUNDLE_LINES: errors.append("finite-adversarial deterministic evidence bundle command surface drift")
    for command in GRAPH_ARTIFACT_COMMANDS:
        if command not in artifact_lines: errors.append(f"finite-adversarial graph artifact retention missing executable command: {command}")

    verify_lines = workflow_step_shell_lines(texts["workflow"], "Verify retained graph evidence")
    if verify_lines != (GRAPH_ARTIFACT_VERIFY_COMMAND,): errors.append("finite-adversarial retained graph evidence verification step drift")
    verify_directives = workflow_step_directives(texts["workflow"], "Verify retained graph evidence")
    if verify_directives != EXPECTED_VERIFY_STEP_DIRECTIVES:
        errors.append("finite-adversarial retained graph evidence verification step envelope drift")
    if workflow_job_has_top_level_directive(texts["workflow"], "finite-results", "continue-on-error:"):
        errors.append("finite-adversarial finite-results job may not use continue-on-error")
    if not workflow_step_has_always(texts["workflow"], "Verify retained graph evidence"): errors.append("finite-adversarial retained graph evidence verification must use always()")
    if sum(1 for line in texts["workflow"].splitlines() if line.strip() == '- "scripts/verify_graph_artifacts.py"') != 2: errors.append("finite-adversarial must trigger on scripts/verify_graph_artifacts.py for PR and main push")
    if sum(1 for line in texts["workflow"].splitlines() if line.strip() == '- "docs/NONCLAIMS.md"') != 2: errors.append("finite-adversarial must trigger on docs/NONCLAIMS.md for PR and main push")

    pettini = markdown_section(texts["roadmap"], PETTINI_START)
    if pettini is None:
        errors.append("ROADMAP missing Pettini model-donor programme")
        pettini = ""
    else:
        if markdown_metadata_value(pettini, "Status") != EXPECTED_PETTINI_STATUS:
            errors.append("ROADMAP Pettini model-donor programme status drift")
        require_anchors(pettini, PETTINI_ANCHORS, "ROADMAP Pettini model-donor programme", errors)
        citation = first_blockquote_after_heading(pettini, "### Primary model source")
        if citation != EXPECTED_PETTINI_PRIMARY_CITATION: errors.append("ROADMAP Pettini primary citation/version drift: expected arXiv:2606.12457v2")
        lower = pettini.casefold()
        if "extra-time physics is adopted by uft-id" in lower: errors.append("ROADMAP Pettini model donor illegally promotes extra-time ontology")

    physiology = markdown_section(texts["roadmap"], PHYSIOLOGY_START)
    if physiology is None:
        errors.append("ROADMAP missing physiology/connectomics positive-control programme")
        physiology = ""
    else:
        if markdown_metadata_value(physiology, "Status") != EXPECTED_PHYSIOLOGY_STATUS:
            errors.append("ROADMAP physiology/connectomics programme status drift")
        if markdown_metadata_value(physiology, "Claim class") != EXPECTED_PHYSIOLOGY_CLAIM_CLASS:
            errors.append("ROADMAP physiology/connectomics programme claim class drift")
        require_anchors(physiology, PHYSIOLOGY_ANCHORS, "ROADMAP physiology/connectomics positive-control programme", errors)
        for donor_id, spec in EXPECTED_PHYSIOLOGY_CITATIONS.items():
            donor_section = markdown_section(physiology, spec["heading"])
            if donor_section is None:
                errors.append(f"ROADMAP physiology donor {donor_id} section missing")
                continue
            citations = markdown_bullets_after_marker(donor_section, spec["marker"])
            if citations != spec["citations"]:
                errors.append(f"ROADMAP physiology donor {donor_id} source identity drift")

    fivefold = markdown_section(texts["roadmap"], FIVEFOLD_START)
    if fivefold is None:
        errors.append("ROADMAP missing fivefold assembly/rooted-representation donor programme")
        fivefold = ""
    else:
        if markdown_metadata_value(fivefold, "Status") != EXPECTED_FIVEFOLD_STATUS:
            errors.append("ROADMAP fivefold donor programme status drift")
        if markdown_metadata_value(fivefold, "Claim class") != EXPECTED_FIVEFOLD_CLAIM_CLASS:
            errors.append("ROADMAP fivefold donor programme claim class drift")
        require_anchors(fivefold, FIVEFOLD_ANCHORS, "ROADMAP fivefold donor programme", errors)

    numerosity = markdown_section(texts["roadmap"], NUMEROSITY_START)
    if numerosity is None:
        errors.append("ROADMAP missing 3-4-5 numerosity/semantic-lifting programme")
        numerosity = ""
    else:
        if markdown_metadata_value(numerosity, "Status") != EXPECTED_NUMEROSITY_STATUS:
            errors.append("ROADMAP 3-4-5 numerosity programme status drift")
        if markdown_metadata_value(numerosity, "Claim class") != EXPECTED_NUMEROSITY_CLAIM_CLASS:
            errors.append("ROADMAP 3-4-5 numerosity programme claim class drift")
        require_anchors(numerosity, NUMEROSITY_ANCHORS, "ROADMAP 3-4-5 numerosity programme", errors)

    if RECEIPT_SCHEMA_BINDING not in texts["receipt"]: errors.append("graph receipt schema version must be derived from canonical registry")

    for label, value in (
        ("graph contract", contract), ("graph results", results),
        ("central graph authority", central if isinstance(central, dict) else {}),
        ("graph source map", texts["sources"]), ("graph human theory", texts["human"]),
    ):
        no_private_locators(value, label, errors)
    for label, value in (
        ("graph contract", contract), ("graph results", results), ("graph source map", texts["sources"]),
        ("graph human theory", texts["human"]), ("claims graph registration", texts["claims"]),
        ("nonclaims authority", texts["nonclaims"]), ("README4AI graph registration", texts["readme4ai"]),
        ("reproducibility graph registration", texts["reproducibility"]), ("ROADMAP Pettini model donor", pettini),
        ("ROADMAP physiology donor programme", physiology), ("ROADMAP fivefold donor programme", fivefold),
        ("ROADMAP 3-4-5 numerosity programme", numerosity),
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
        for error in result["errors"]: print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
