# Reproducibility and CI Evidence Contract

**Claim class:** `NONCLAIM`

This document defines how executable evidence is produced, checked, and retained. It does not upgrade any scientific claim.

## Evidence chain

```text
primary source / pinned public repository contract
  -> canonical source or pattern record
  -> exact claim / abstract pattern
  -> theorem or reproduction obligation
  -> executable derivation / experiment
  -> deterministic result and source hashes
  -> repository assessment
  -> canonical claim class
  -> CI validation and retained artifact
```

A green workflow establishes only that declared repository checks passed for a particular commit/runtime.

## Supported runtime

- GitHub runner: `ubuntu-24.04`
- Python: `3.12`, `3.13`
- Current validators/finite experiments: Python standard library only

## Required local validation

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_cross_repo_patterns.py
python scripts/validate_vopson_2019_mei.py
python scripts/validate_reproducibility.py
python scripts/validate_formalization_contracts.py
python scripts/validate_observation_specs.py
python scripts/validate_relation_core.py
python scripts/validate_graph_realization.py
python experiments/graph_realization/run.py --json
python experiments/run_graph_realization.py --json
python scripts/validate_bridge_core.py
python experiments/bridge_core/run.py --json
python experiments/run_bridge_core.py --json
python scripts/validate_epistemic_bridge.py
python experiments/epistemic_bridge/run.py --json
python experiments/run_epistemic_bridge.py --json
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
python experiments/run_cross_repo.py --json
python experiments/reproduction/vopson_2019_mei/run.py --json
python experiments/run_pr6.py --json
```

`python -O` is intentional. Scientific checks must not depend on removable `assert` statements.

## Deterministic receipt families

```text
experiments/run_pr2.py
experiments/run_cross_repo.py
experiments/run_pr6.py
experiments/run_graph_realization.py
experiments/run_bridge_core.py
experiments/run_epistemic_bridge.py
```

All receipt families bind deterministic repository files and canonical result payloads while keeping runtime metadata outside portable fingerprints.

## Graph-realization conformance boundary

The graph suite exhaustively cross-checks every labelled binary relation on `Fin1`, `Fin2`, and `Fin3`, exactly 530 relations. It compares adjacency, normality, reachability, finite termination, SCC partition, sink SCC classification, and condensation where applicable.

Canonical commands:

```bash
python scripts/validate_graph_realization.py
python experiments/graph_realization/run.py --json
python experiments/run_graph_realization.py --json
```

Retained files:

```text
graph-realization-validation.json
graph-realization-witness.json
graph-realization-receipt.json
```

The graph authority chain also binds `docs/CLAIMS.md`, `README4AI.md`, and `ROADMAP.md` through the deterministic source set.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY
GRAPH_DRAWING != GRAPH_IDENTITY
```

## BridgeCore conformance boundary

BridgeCore accepts a possibly empty declared domain and carrier, keeps preservation/loss metadata disjoint without requiring exhaustiveness, and requires exact finite intermediate-carrier identity in the executable specialization.

The production composition law is checked over all `27^2 = 729` ordered partial preservation/loss declaration pairs and all 4,096 `Fin2` relation triples.

```text
DISJOINT_METADATA != EXHAUSTIVE_METADATA
RELATIONAL_IDENTITY_NEUTRALITY != UNCONDITIONAL_METADATA_NEUTRALITY
FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF
STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION
BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION
```

## Epistemic Bridge conformance boundary

The Epistemic Bridge suite enumerates six factor-presence bits:

```text
evidence retrieved inferred verified executed conflict
```

It checks all `2^6 = 64` raw vectors and exactly 33 valid normalized shapes. It separately checks retrieval, inference, execution, explicit verification, conflict recording, neutral transport, repeated transport, and scope narrowing.

Canonical commands:

```bash
python scripts/validate_epistemic_bridge.py
python experiments/epistemic_bridge/run.py --json
python experiments/run_epistemic_bridge.py --json
```

Retained files:

```text
epistemic-bridge-validation.json
epistemic-bridge-witness.json
epistemic-bridge-receipt.json
```

The deterministic Epistemic Bridge source set includes:

```text
machine/epistemic_bridge_contract.json
machine/epistemic_bridge_results.json
machine/bridge_core_contract.json
machine/roadmap_state.json
machine/contract.json
theory/EPISTEMIC_BRIDGE.md
docs/CLAIMS.md
README4AI.md
docs/REPRODUCIBILITY.md
ROADMAP.md
scripts/validate_epistemic_bridge.py
scripts/verify_epistemic_bridge_artifacts.py
experiments/epistemic_bridge/run.py
tests/test_epistemic_bridge.py
experiments/run_epistemic_bridge.py
.github/workflows/finite-adversarial.yml
```

```text
STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION
RETRIEVED != VERIFIED
INFERRED != VERIFIED
EXECUTED != VERIFIED
VERIFIED != TRUE
CONFLICT != UNKNOWN
VERIFIED != CONFLICT_FREE
NO_GLOBAL_EPISTEMIC_LATTICE
FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY
```

A verification receipt is a scoped repository evidence object, not a universal truth certificate.

## VOP-2019-MEI reproduction boundary

```text
LANDAUER_ERASURE_BOUND != INTRINSIC_STORED_BIT_ENERGY
ARITHMETIC_REPRODUCED != PREMISE_VALIDATED
ARITHMETIC_REPRODUCED != EXPERIMENTALLY_CONFIRMED
LOCAL_REPRODUCTION_HASH != PRIMARY_SOURCE_BYTE_HASH
DOI_AND_LOCATOR_IDENTITY != SOURCE_PDF_BYTE_HASH
```

Primary paper bytes are not redistributed. Source identity is DOI plus exact locators.

## Cross-repository provenance pins

`machine/cross_repo_patterns.json` records repository, `main` ref, path, and exact Git blob SHA for each imported or quarantined pattern.

```text
PINNED_SOURCE_SNAPSHOT != LIVE_REMOTE_FRESHNESS
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

## CI artifacts

Every supported Python job retains an `artifacts/` evidence bundle for 30 days. The bundle includes, as applicable:

```text
pr2-receipt.json
finite-signs.json
coarse-graining.json
polygon-audit.json
vopson-2019-mei.json
vopson-2019-mei-receipt.json
vopson-2019-mei-validation.json
cross-repo-pattern-validation.json
cross-repo-receipt.json
graph-realization-validation.json
graph-realization-witness.json
graph-realization-receipt.json
bridge-core-validation.json
bridge-core-witness.json
bridge-core-receipt.json
epistemic-bridge-validation.json
epistemic-bridge-witness.json
epistemic-bridge-receipt.json
vopson-corpus-validation.json
vopson-doc-sync.json
reproducibility-validation.json
```

Generated CI artifacts are workflow evidence and are not automatically committed as canonical source.

## GitHub Actions provenance

Workflow actions remain pinned to the full 40-character SHAs in `machine/contract.json`. Checkout credentials are not persisted and workflow permissions remain read-only.

## Bounded exhaustive computation

Finite exhaustive batteries prove only their declared bounded conformance domains:

```text
530 labelled relation graphs
4096 Fin2 BridgeCore relation triples
729 BridgeCore partial-structure declaration pairs
64 raw / 33 valid Epistemic Bridge factor vectors
```

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

## Human and machine synchronization

Graph realization is synchronized across its machine contract/results, human theory/source map, `docs/CLAIMS.md`, `README4AI.md`, this file, central `machine/contract.json`, `ROADMAP.md`, and its receipt.

BridgeCore is synchronized across its contract/results, human theory, central read/claim/reproducibility surfaces, live roadmap state, and deterministic receipt.

Epistemic Bridge is synchronized across `machine/epistemic_bridge_contract.json`, `machine/epistemic_bridge_results.json`, `theory/EPISTEMIC_BRIDGE.md`, `docs/CLAIMS.md`, `README4AI.md`, `docs/REPRODUCIBILITY.md`, `machine/contract.json`, `machine/roadmap_state.json`, and its deterministic receipt.

## Nonclaims

This contract does not claim that deterministic output proves a physical law, that a hash proves scientific correctness, that correct arithmetic validates a physical premise, that finite conformance proves unrestricted mathematics, that transport/retrieval/inference/execution creates verification, that verification establishes truth, or that CI replaces independent scientific review.
