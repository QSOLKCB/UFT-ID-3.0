# Claims and Status Discipline

This document defines what UFT-ID 3.0 is currently allowed to claim.

## Status labels

Every nontrivial claim receives **exactly one** status from the canonical claim-class enum.

### DEFINITION
A stipulated mathematical or operational definition. A definition is not an empirical discovery.

### THEOREM_TARGET
A mathematically precise statement intended for proof or refutation.

### PROVED
A theorem with a complete accepted proof in the repository. Machine-checked status remains separate until the Lean phase.

### COUNTEREXAMPLE
An explicit construction falsifying a stated proposition under its declared assumptions.

### DIAGNOSTIC
An operational audit construct. Diagnostic constructs are not ontological components.

### EMPIRICAL
A result supported by data or experiment with provenance, scope, and uncertainty.

### INTERPRETIVE
A mapping from a formal or empirical framework into a target domain.

### SPECULATIVE
A hypothesis not established by the formal or empirical layers.

### NONCLAIM
A proposition the project explicitly declines to assert.

## Current positive claims

### C1 - Constraint-first architecture is mathematically definable

**Status:** DEFINITION

Informational systems can be modeled using a total state space, an admissible subspace, residual or violation structure, threshold conditions, and deterministic recovery maps where the necessary mathematical structures exist. This does not assert that every physical system literally implements these objects.

### C2 - Deterministic lexicographic recovery is a valid construction

**Status:** DEFINITION

For finite admissible candidate sets equipped with a total tie-breaking order, nearest-state recovery can be made deterministic by lexicographic selection. General existence and uniqueness statements depend on the state-space assumptions.

### C3 - Inference transport is usefully separable from within-regime inference

**Status:** DIAGNOSTIC

Transfer of parameters, assumptions, models, or conclusions across calibration regimes is a distinct audit target. This is a methodological distinction, not a physical mechanism.

### C4 - Observation is represented separately from underlying state

**Status:** DEFINITION

UFT-ID 3.0 explicitly models observation or coarse-graining as a map. Apparent changes in an observed information measure are not automatically identified with changes in an underlying physical information quantity.

### C5 - Universal sign claims are an explicit theorem/audit target

**Status:** THEOREM_TARGET

Any proposed monotonicity result must declare state space, dynamics, time model, boundary conditions, representation, measure, partition/coarse-graining contract, and information functional.

### C6 - Vopson's infodynamics program is treated as separable claim tracks

**Status:** DIAGNOSTIC

Mass-equivalence, information-entropy monotonicity, cross-domain applications, gravity derivation, and simulation-hypothesis interpretation remain logically separable audit tracks.

### C7 - Finite relation semantics admit an exact graph-realization layer

**Status:** PROVED

The canonical graph-realization authority registers `UFT-GR-001` through `UFT-GR-006` as proved abstract results. For a finite labelled carrier and its declared binary endorelation `stepRel`, graph realization preserves one-step adjacency exactly; normal states are exactly zero-outdegree vertices; relation reachability agrees with directed graph reachability; finite forward termination agrees with directed acyclicity; every nonempty finite digraph has at least one sink strongly connected component; and the SCC condensation graph is acyclic.

The repository's 530-relation executable battery is bounded conformance evidence, not the proof of general finite mathematics.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY
GRAPH != DRAWING
NORMAL_VERTEX != SINK_SCC
```

### C8 - Compatible typed structural bridges compose conservatively

**Status:** PROVED

The canonical BridgeCore authority registers `UFT-BR-001` through `UFT-BR-005` as proved abstract results. A `BridgeSpec` declares source and target type, a possibly empty source domain, typed map/relation, preserved structure, lost structure, scope, and source/target versions.

Automatically inherited preservation is intersection-bounded, earlier loss remains recorded, complete structure tracking is required for two-sided metadata identity neutrality, and compatible composition is associative.

```text
BRIDGE != IDENTITY
TRANSPORT != EQUIVALENCE
DISJOINT_METADATA != EXHAUSTIVE_METADATA
STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION
FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF
BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION
```

### C9 - Epistemic authority is factorized and transport-neutral

**Status:** PROVED

**Qualifier:** abstract bookkeeping scope; not a universal epistemology, truth oracle, credibility score, or empirical validation claim.

The canonical Epistemic Bridge authority registers `UFT-EP-001` through `UFT-EP-005`. Evidence, retrieval, inference, verification, execution, conflict, and scope are represented as separate fields. Licensed structural transport preserves authority-bearing fields exactly and may only narrow scope by intersection. Verification requires an explicit verification receipt. Conflict is distinct from unknown, and verification can coexist with unresolved conflict.

The finite executable surface checks all 64 six-bit presence vectors and the resulting 33 valid normalized shapes. This is bounded conformance evidence, not a general theory of knowledge.

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

### C10 - Representation invariants are transformation-class-relative

**Status:** PROVED

**Qualifier:** finite-dimensional linear representation and finite deterministic receiver-re-encoding scope only; not a physical-equivalence or semantic-identity claim.

The canonical Representation and Congruence authority registers `UFT-REP-001` through `UFT-REP-005`. Similarity preserves the characteristic polynomial and its standard finite-dimensional consequences; orthogonal/unitary similarity additionally preserves Frobenius norm; invertible real congruence preserves rank and symmetry type without generally preserving eigenvalues; coordinate change preserves the represented linear action covariantly; and injective receiver re-encoding preserves deterministic observation fibres.

The executable reference surface checks 3,240 exact similarity instances, 3,240 congruence-rank instances, 648 orthogonal Frobenius instances, 29,160 coordinate-covariance instances, and 3,969 receiver-equivalence source-pair instances.

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

### C11 - Information comparability is specification-relative

**Status:** PROVED

**Qualifier:** finite information-specification and explicit logarithm-base/unit-conversion scope only; not a universal information ontology or empirical commensurability claim.

The canonical Information Comparability authority registers `UFT-INF-001` through `UFT-INF-005`. A valid `InformationSpec` names source type, functional, observation, unit, normalization, conditioning, and scope. Direct comparability requires all comparison-defining fields to agree and scopes to overlap. Explicit registered positive unit conversions can license a narrower unit-converted comparison without making the specifications identical.

The exact finite reference surface enumerates 96 specifications and all 9,216 ordered pairs, yielding 224 directly comparable ordered pairs and 224 explicit unit-convertible ordered pairs. It also checks 75 positive-scale order/sign cases and five exact bit/base4 logarithm-base conversions.

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

### C12 - Deterministic recovery is an explicit specialization, not generic relation semantics

**Status:** PROVED

**Qualifier:** abstract deterministic-selector and finite lexicographic-recovery scope only; not an empirical recovery mechanism, stochastic normalizer, continuum theorem, or physical selection law.

The canonical Recovery Specializations authority registers `UFT-REC-001` through `UFT-REC-005`. A selector `sigma:X->X` induces a right-unique effective selector relation, but the underlying generic `stepRel` remains distinct. Relation-sound finite selector iteration stays inside base reachability. A natural-number rank that strictly decreases on every non-fixed selector step supplies termination, and executable normalization additionally requires totality plus exact selector-fixed-point/stepRel-normal correspondence. Finite lexicographic recovery becomes unique only with an explicit final total tie-break.

The exact finite reference surface checks 32 total selectors, 13,890 selector/relation pairs, 4,134 relation-sound pairs, 739 relation-sound pairs with exact fixed-point/normal agreement, 9 rank-decreasing selector controls, 23 state-level normalization checks, and 336 lexicographic selections.

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

### C13 - Stochastic, prevalence, and continuum lifting require explicit obligations

**Status:** PROVED

**Qualifier:** finite rational stochastic controls, finite prevalence measures, and finite-grid non-lifting mathematics only; not a general stochastic-process, continuum, ergodic, asymptotic, statistical-inference, or empirical-prevalence theory.

The canonical Continuum/Stochastic/Prevalence authority registers `UFT-CSP-001` through `UFT-CSP-005`. Finite row-stochastic kernels preserve total probability. In finite atomic models, almost-sure events imply positive probability while positive probability is exactly support intersection. Finite path mass is the declared initial mass times the product of transition probabilities. Prevalence is indexed by a declared measure, so a counterexample's existence alone does not determine prevalence. Finally, agreement on any finite real grid cannot imply continuum equality without additional lifting assumptions.

The exact finite reference surface checks 9 two-state rational kernels, 27 kernel transports, 756 finite path masses, 81 path-normalization totals, 48 finite-atomic event/quantifier cases, 16 finite survival controls, 80 prevalence measure/event evaluations, and 31 finite-grid non-lifting polynomial controls.

```text
RELATION_REACHABLE != POSITIVE_PROBABILITY
EXISTS_PATH != POSITIVE_PROBABILITY
POSITIVE_PROBABILITY != ALMOST_SURE
FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS
ONE_TRAJECTORY != DISTRIBUTION
FINITE_SAMPLE_FREQUENCY != MODEL_PROBABILITY
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
PREVALENCE_REQUIRES_DECLARED_MEASURE
FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY
DISCRETIZATION_CONVERGENCE != ASSUMED_WITHOUT_ERROR_CONTROL
FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY
```

### C14 - Empirical falsification decisions are profile-scoped

**Status:** PROVED

**Qualifier:** abstract decision-contract and synthetic exact-interval conformance scope only; this is not an empirical result, statistical-power claim, independent replication, population inference, causal identification, or physical validation.

The canonical Empirical Falsification Profile authority registers `UFT-EFP-001` through `UFT-EFP-005`. Complete profile-matched evidence is required before any rejection decision is licensed. Rejection is scoped to one hypothesis/profile version, non-rejection is not confirmation, uncertainty that crosses the declared boundary is inconclusive, and one compatible observation does not uniquely identify a model when multiple prediction sets contain it.

The exact synthetic reference surface checks 15 valid interval decisions, 60 invalid-evidence mutations, 15 candidate-model fit memberships with 3 ambiguous observations, and 3 pairwise profile-fingerprint separation checks.

```text
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
SYNTHETIC_FIXTURE != EMPIRICAL_EVIDENCE
FAILURE_TO_REJECT != CONFIRMATION
EMPIRICAL_FIT != UNIQUE_EXPLANATION
REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION
NUMERIC_OBSERVATION != CALIBRATED_MEASUREMENT
MISSING_UNCERTAINTY != ZERO_UNCERTAINTY
POST_HOC_THRESHOLD != PREREGISTERED_REJECTION_RULE
INCONCLUSIVE != NOT_REJECTED
REPRODUCIBLE_ANALYSIS != INDEPENDENT_REPLICATION
FINITE_EMPIRICAL_PROFILE_CONFORMANCE != GENERAL_STATISTICAL_INFERENCE
```

## Claims requiring future proof or evidence

The following remain future theorem/evidence targets:

- a general information balance law valid across multiple classes of systems;
- representation-independent sign behavior of information derivatives or finite differences;
- a restricted theorem that exactly recovers the Second Law of Infodynamics as a special case;
- transport-shear invariants;
- observer-relative inaccessible-information identities;
- admissible fixed-point theorems;
- a universal failure trajectory for inference systems;
- general measurable-space, continuous-time stochastic, ergodic, mixing, and concentration results beyond the bounded CSP authority;
- source-specific empirical falsification profiles, statistical power, population inference, causal identification, and independent replication beyond the synthetic EFP authority;
- any physical identification of UFT-ID fields with fundamental forces or spacetime.

## Promotion rule

A claim may move upward only when the evidence type matches the claim type.

- simulation can support an empirical/computational claim, not a universal theorem;
- a theorem can establish an abstract implication, not physical ontology;
- repeated analogy can motivate a hypothesis, not prove common mechanism;
- successful reproduction does not establish interpretation;
- transport, retrieval, inference, execution, and verification receipts remain distinct authority events;
- representation equivalence remains scoped to its declared transformation class and does not imply semantic or physical identity;
- information comparison remains scoped to an explicit `InformationSpec` relation or registered conversion and cannot be inferred from shared vocabulary, units, scalar values, or functional names alone;
- deterministic recovery requires an explicit selector specialization, relation soundness, termination/progress, and normal-state obligations; a selector result does not promote the base relation to confluence or empirical recovery;
- stochastic and continuum promotion requires explicit probability/measure, quantifier, topology, regularity, convergence, and error-control obligations; finite reachability, finite samples, formal counterexamples, and finite-grid agreement do not supply them automatically;
- empirical rejection requires complete calibrated profile-matched evidence under a fixed hypothesis/profile version; formal counterexamples, synthetic fixtures, non-rejection, model fit, reproducible analysis, and one scoped rejection cannot be promoted into empirical falsification, confirmation, unique explanation, independent replication, or global theory refutation without additional evidence and arguments.
