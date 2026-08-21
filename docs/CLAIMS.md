# Claims and Status Discipline

This document defines what UFT-ID 3.0 is currently allowed to claim.

## Status labels

Every nontrivial claim receives **exactly one** status from the canonical claim-class enum. Secondary notes such as "programmatic", "pending theorem work", or "research program" are qualifiers, not claim classes.

### DEFINITION

A stipulated mathematical or operational definition. A definition is not an empirical discovery.

### THEOREM_TARGET

A mathematically precise statement intended for proof or refutation. It must not be described as established until proved.

### PROVED

A theorem with a complete accepted proof in the repository. After the Lean phase begins, machine-checked theorems should be separately marked.

### COUNTEREXAMPLE

An explicit construction falsifying a stated proposition under its declared assumptions.

### DIAGNOSTIC

An operational audit construct intended to organize reasoning or detect stress signals. Diagnostic constructs are not ontological components.

### EMPIRICAL

A result supported by data or experiment, with method, uncertainty, provenance, and scope.

### INTERPRETIVE

A mapping from the formal or empirical framework into a target domain. Interpretation requires an explicit bridge and may remain non-unique.

### SPECULATIVE

A hypothesis not established by the formal or empirical layers.

### NONCLAIM

A proposition the project explicitly declines to assert.

## Current positive claims

### C1 - Constraint-first architecture is mathematically definable

**Status:** DEFINITION

**Qualifier:** programmatic scope.

Informational systems can be modeled using a total state space, an admissible subspace, residual or violation structure, threshold conditions, and deterministic recovery maps where the necessary mathematical structures exist.

This does not assert that every physical system literally implements these objects.

### C2 - Deterministic lexicographic recovery is a valid construction

**Status:** DEFINITION

**Qualifier:** theorem work is pending for existence, uniqueness, and stability under explicitly stated assumptions.

For finite admissible candidate sets equipped with a total tie-breaking order, nearest-state recovery can be made deterministic by lexicographic selection. General existence and uniqueness statements depend on the state-space assumptions.

### C3 - Inference transport is usefully separable from within-regime inference

**Status:** DIAGNOSTIC

The project treats transfer of parameters, assumptions, models, or conclusions across calibration regimes as a distinct audit target. This is a methodological distinction, not a new physical mechanism.

### C4 - Observation is represented separately from underlying state

**Status:** DEFINITION

**Qualifier:** this is a modeling commitment, not an ontological claim about observers.

UFT-ID 3.0 explicitly models observation or coarse-graining as a map. Consequently, apparent changes in an observed information measure are not automatically identified with changes in an underlying physical information quantity.

### C5 - Universal sign claims are an explicit theorem/audit target

**Status:** THEOREM_TARGET

**Qualifier:** methodological rule until the relevant theorem families are proved.

For any proposed monotonicity result, UFT-ID 3.0 requires the state space, dynamics, time model, boundary conditions, representation, measure, partition/coarse-graining contract, and information functional to be declared. The research program will determine the strongest assumptions under which specific monotonicity results are valid.

### C6 - Vopson's infodynamics program is treated as separable claim tracks

**Status:** DIAGNOSTIC

**Qualifier:** research-program decomposition.

The mass-equivalence proposal, information-entropy monotonicity proposal, cross-domain applications, gravity derivation, and simulation-hypothesis interpretation are treated as logically separable audit tracks. Agreement or failure in one track does not automatically settle the others.

### C7 - Finite relation semantics admit an exact graph-realization layer

**Status:** PROVED

**Qualifier:** finite/set-theoretic mathematical scope; not a physical ontology claim.

The canonical graph-realization authority registers `UFT-GR-001` through `UFT-GR-006` as proved abstract results. For a finite labelled carrier and its declared binary endorelation `stepRel`, the corresponding directed graph preserves one-step adjacency exactly; normal states are exactly zero-outdegree vertices; relation reachability agrees with directed graph reachability; finite forward termination agrees with directed acyclicity; every nonempty finite digraph has at least one sink strongly connected component; and the SCC condensation graph is acyclic.

The repository's 530-relation executable battery is an independent finite conformance witness for these statements, not the proof of their general finite mathematical content.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY
GRAPH != DRAWING
NORMAL_VERTEX != SINK_SCC
```

The SiS2, ETQ/SPECTRAL, tetrahedral, or other structural examples do not promote these graph theorems into claims about fundamental physics.

### C8 - Compatible typed structural bridges compose conservatively

**Status:** PROVED

**Qualifier:** abstract/set-theoretic structural-transport scope; not epistemic promotion, semantic equivalence, or physical validation.

The canonical BridgeCore authority registers `UFT-BR-001` through `UFT-BR-005` as proved abstract results. A `BridgeSpec` declares source and target type, source domain, a typed map or relation, preserved structure, lost structure, scope, and source/target versions. Ordinary BridgeCore composition is licensed only when intermediate type and version identities agree, every produced intermediate state lies in the second bridge domain, and the declared scopes overlap.

Under the conservative composition contract, automatically inherited preservation is the intersection of the two preservation sets, previously lost structure remains lost, compatible identity bridges are neutral, and fully compatible three-bridge composition is associative. The repository's finite BridgeCore battery checks all 4,096 ordered triples of labelled binary relations on `Fin2` plus bounded preservation/loss fixtures as independent conformance evidence, not as the proof of the general set-theoretic results.

```text
BRIDGE != IDENTITY
TRANSPORT != EQUIVALENCE
PRESERVED_STRUCTURE != ALL_STRUCTURE
LOSSY_BRIDGE != INVERTIBLE_BRIDGE
STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION
FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF
BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION
```

PR #13 remains responsible for any later epistemic bridge specialization. Structural transport alone cannot manufacture stronger evidence authority.

## Claims requiring future proof or evidence

The following are intentionally not yet promoted beyond theorem target or hypothesis:

- a general information balance law valid across multiple classes of systems;
- representation-independent sign behavior of information derivatives or finite differences;
- a restricted theorem that exactly recovers the Second Law of Infodynamics as a special case;
- transport-shear invariants;
- observer-relative inaccessible-information identities;
- admissible fixed-point theorems;
- a universal failure trajectory for inference systems;
- any physical identification of UFT-ID fields with fundamental forces or spacetime.

## Promotion rule

A claim may move upward only when the evidence type matches the claim type.

Examples:

- simulation can support an empirical/computational claim, not a universal theorem;
- a theorem can establish an abstract implication, not the truth of a physical ontology;
- repeated cross-domain analogy can motivate a hypothesis, not prove a common mechanism;
- a successful reproduction of a published result does not establish its interpretation;
- a failed reproduction must distinguish implementation error, data mismatch, and genuine scientific disagreement.
