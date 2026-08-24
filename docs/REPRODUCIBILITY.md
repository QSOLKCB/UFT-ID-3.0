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
python scripts/validate_representation_calculus.py
python experiments/representation_calculus/run.py --json
python experiments/run_representation_calculus.py --json
python scripts/validate_information_comparability.py
python experiments/information_comparability/run.py --json
python experiments/run_information_comparability.py --json
python scripts/validate_recovery_specializations.py
python experiments/recovery_specializations/run.py --json
python experiments/run_recovery_specializations.py --json
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
experiments/run_representation_calculus.py
experiments/run_information_comparability.py
experiments/run_recovery_specializations.py
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

The deterministic Epistemic Bridge source set includes its machine authority, human theorem surface, central authority/read surfaces, live roadmap, validator, executable, tests, retained-artifact verifier, receipt runner, and workflow.

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

## Representation-calculus conformance boundary

The Representation and Congruence suite uses exact `fractions.Fraction` arithmetic for its finite 2x2 fixtures and exhaustive finite receiver maps. No floating tolerance is used.

Canonical commands:

```bash
python scripts/validate_representation_calculus.py
python experiments/representation_calculus/run.py --json
python experiments/run_representation_calculus.py --json
```

Retained files:

```text
representation-validation.json
representation-witness.json
representation-receipt.json
```

The exact bounded battery checks:

```text
81 small 2x2 matrices
40 unimodular change-of-basis matrices
8 orthogonal signed-permutation matrices
3240 similarity invariant instances
3240 congruence-rank instances
648 orthogonal Frobenius instances
29160 coordinate-covariance instances
27 Fin3 endofunctions
729 ordered observation/receiver function pairs
441 receiver pairs injective on the observation image
3969 source-pair equivalence checks
```

```text
SIMILARITY != CONGRUENCE
SIMILARITY != ORTHOGONAL_OR_UNITARY_SIMILARITY
SAME_CHARACTERISTIC_POLYNOMIAL != SIMILARITY
CONGRUENCE != SPECTRAL_EQUIVALENCE
COORDINATE_TUPLE != ABSTRACT_OBJECT
REPRESENTATION_CHANGE != PHYSICAL_CHANGE
RECEIVER_REENCODING != STATE_TRANSFORMATION
NONINJECTIVE_RECEIVER_REENCODING != OBSERVATIONAL_EQUIVALENCE_PRESERVATION
INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE
FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF
```

The deterministic Representation source set binds the observation, BridgeCore, and Epistemic contracts as dependencies because the receiver and authority boundaries must remain explicit across phase transitions.

## Information-comparability conformance boundary

The Information Comparability suite treats comparability as a typed relation between declared `InformationSpec` values rather than as an automatic consequence of two scalar outputs existing.

Canonical commands:

```bash
python scripts/validate_information_comparability.py
python experiments/information_comparability/run.py --json
python experiments/run_information_comparability.py --json
```

Retained files:

```text
information-comparability-validation.json
information-comparability-witness.json
information-comparability-receipt.json
```

The exact bounded battery checks:

```text
96 InformationSpec values
9216 ordered specification pairs
224 directly comparable ordered pairs
224 explicit unit-convertible ordered pairs
96 direct-comparability reflexive checks
9216 direct-comparability symmetry checks
224 inverse unit-conversion checks
75 positive-scale order/sign checks
5 exact power-of-two bit/base4 conversion checks
```

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
SAME_SCALAR_CODOMAIN != COMPARABLE_INFORMATION
SAME_UNIT != COMPARABLE_INFORMATION
SAME_FUNCTIONAL != SAME_OBSERVATION
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE
POSITIVE_UNIT_CONVERSION != SEMANTIC_BRIDGE
PAIRWISE_SCOPE_COMPARABILITY != TRANSITIVE_COMPARABILITY
DIRECT_COMPARABILITY != EMPIRICAL_COMMENSURABILITY
FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY
```

The deterministic Information Comparability source set binds the existing information primitives plus observation and Representation contracts because comparison cannot silently discard either the information-functional identity or the observation/representation boundary.

## Recovery-specializations conformance boundary

Recovery Specializations adds an explicit deterministic selector layer on top of the frozen generic relation core. Selector fixed points are halting semantics and are not silently inserted as self-loops into `stepRel`.

Canonical commands:

```bash
python scripts/validate_recovery_specializations.py
python experiments/recovery_specializations/run.py --json
python experiments/run_recovery_specializations.py --json
```

Retained files:

```text
recovery-specialization-validation.json
recovery-specialization-witness.json
recovery-specialization-receipt.json
```

The exact bounded battery checks:

```text
32 total selectors
13890 selector/relation pairs
4134 relation-sound selector/relation pairs
739 relation-sound pairs with selector fixed points exactly equal to relation normals
9 natural-index-rank-decreasing selector controls
23 state-level executable-normalization checks
336 finite lexicographic selection checks
```

The executable normalizer fails closed unless the selector is total on exactly the declared carrier, every target stays inside that carrier, every non-fixed step is relation-sound, fixed points exactly match relation normals, and a natural-number rank strictly decreases on every non-fixed step. Lexicographic objective vectors are finite integer tuples; malformed or partially ordered values such as NaN are rejected before selection.

```text
GENERIC_RELATION != DETERMINISTIC_SELECTOR
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
DETERMINISTIC != RELATION_SOUND
RELATION_SOUND != TERMINATING
TERMINATING_SELECTOR != BASE_RELATION_CONFLUENT
SELECTOR_NORMAL_FORM != UNIQUE_RELATION_NORMAL_FORM
OBJECTIVE_MINIMUM != UNIQUE_SELECTION_WITHOUT_TIEBREAK
EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY
FINITE_SELECTOR_CONFORMANCE != GENERAL_RECOVERY_THEORY
```

The deterministic Recovery source set binds the base relation contract and human relation calculus, central machine authority, live roadmap, AI bootstrap, claims, reproducibility contract, validator, executable, tests, receipt runner, retained-artifact verifier, and the existing `finite-adversarial` workflow.

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
representation-validation.json
representation-witness.json
representation-receipt.json
information-comparability-validation.json
information-comparability-witness.json
information-comparability-receipt.json
recovery-specialization-validation.json
recovery-specialization-witness.json
recovery-specialization-receipt.json
vopson-corpus-validation.json
vopson-doc-sync.json
reproducibility-validation.json
```

Generated CI artifacts are workflow evidence and are not automatically committed as canonical source.

## GitHub Actions provenance

Workflow actions remain pinned to the full 40-character SHAs in `machine/contract.json`. Checkout credentials are not persisted and workflow permissions remain read-only. Recovery uses the existing declared `finite-adversarial.yml` workflow rather than introducing an undeclared third workflow.

## Bounded exhaustive computation

Finite exhaustive batteries prove only their declared bounded conformance domains:

```text
530 labelled relation graphs
4096 Fin2 BridgeCore relation triples
729 BridgeCore partial-structure declaration pairs
64 raw / 33 valid Epistemic Bridge factor vectors
3240 similarity checks
3240 congruence-rank checks
648 orthogonal Frobenius checks
29160 coordinate-covariance checks
3969 receiver-equivalence checks
96 information specifications
9216 ordered information-specification pairs
224 direct information-comparability pairs
224 explicit unit-convertible information pairs
32 total recovery selectors
13890 recovery selector/relation pairs
4134 relation-sound recovery selector/relation pairs
739 exact fixed-point/normal recovery pairs
336 finite lexicographic selections
```

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

## Human and machine synchronization

Graph realization is synchronized across its machine contract/results, human theory/source map, `docs/CLAIMS.md`, `README4AI.md`, this file, central `machine/contract.json`, `ROADMAP.md`, and its receipt.

BridgeCore is synchronized across its contract/results, human theory, central read/claim/reproducibility surfaces, live roadmap state, and deterministic receipt.

Epistemic Bridge is synchronized across `machine/epistemic_bridge_contract.json`, `machine/epistemic_bridge_results.json`, `theory/EPISTEMIC_BRIDGE.md`, `docs/CLAIMS.md`, `README4AI.md`, `docs/REPRODUCIBILITY.md`, `machine/contract.json`, `machine/roadmap_state.json`, and its deterministic receipt.

Representation and Congruence is synchronized across `machine/representation_contract.json`, `machine/representation_results.json`, `theory/REPRESENTATION_CALCULUS.md`, `docs/CLAIMS.md`, `README4AI.md`, `docs/REPRODUCIBILITY.md`, `machine/contract.json`, `machine/roadmap_state.json`, `ROADMAP.md`, and its deterministic receipt.

Information Comparability is synchronized across `machine/information_comparability_contract.json`, `machine/information_comparability_results.json`, `theory/INFORMATION_COMPARABILITY.md`, `docs/CLAIMS.md`, `README4AI.md`, `docs/REPRODUCIBILITY.md`, `machine/contract.json`, `machine/roadmap_state.json`, and its deterministic receipt.

Recovery Specializations is synchronized across `machine/recovery_specialization_contract.json`, `machine/recovery_specialization_results.json`, `theory/RECOVERY_SPECIALIZATIONS.md`, `docs/CLAIMS.md`, `README4AI.md`, `docs/REPRODUCIBILITY.md`, `machine/contract.json`, `machine/roadmap_state.json`, `ROADMAP.md`, the base relation authority, and its deterministic receipt.

## Nonclaims

This contract does not claim that deterministic output proves a physical law, that a hash proves scientific correctness, that correct arithmetic validates a physical premise, that finite conformance proves unrestricted mathematics, that transport/retrieval/inference/execution creates verification, that verification establishes truth, that representation equivalence establishes semantic or physical identity, that two numbers called information are comparable without a declared specification relation, that a deterministic selector establishes base-relation confluence or empirical recovery, or that CI replaces independent scientific review.
