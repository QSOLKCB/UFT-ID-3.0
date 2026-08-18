# Claims and Status Discipline

This document defines what UFT-ID 3.0 is currently allowed to claim.

## Status labels

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

**Status:** DEFINITION / PROGRAMMATIC

Informational systems can be modeled using a total state space, an admissible subspace, residual or violation structure, threshold conditions, and deterministic recovery maps where the necessary mathematical structures exist.

This does not assert that every physical system literally implements these objects.

### C2 - Deterministic lexicographic recovery is a valid construction

**Status:** DEFINITION; theorem work pending

For finite admissible candidate sets equipped with a total tie-breaking order, nearest-state recovery can be made deterministic by lexicographic selection. General existence and uniqueness statements depend on the state-space assumptions.

### C3 - Inference transport is usefully separable from within-regime inference

**Status:** DIAGNOSTIC

The project treats transfer of parameters, assumptions, models, or conclusions across calibration regimes as a distinct audit target. This is a methodological distinction, not a new physical mechanism.

### C4 - Observation must be separated from underlying state

**Status:** PROGRAMMATIC / DEFINITION

UFT-ID 3.0 explicitly models observation or coarse-graining as a map. Consequently, apparent changes in an observed information measure are not automatically identified with changes in an underlying physical information quantity.

### C5 - Universal sign claims require explicit assumptions

**Status:** THEOREM_TARGET / METHODOLOGICAL PRINCIPLE

Any claim that an information functional must monotonically increase or decrease requires a declared state space, dynamics, boundary conditions, representation, measure, and information functional. The repository will determine the strongest assumptions under which specific monotonicity results are valid.

### C6 - Vopson's infodynamics program is testable as a collection of distinct claims

**Status:** RESEARCH PROGRAM

The mass-equivalence proposal, information-entropy monotonicity proposal, cross-domain applications, gravity derivation, and simulation-hypothesis interpretation are treated as logically separable. Agreement or failure in one track does not automatically settle the others.

## Claims requiring future proof or evidence

The following are intentionally not yet promoted beyond theorem target or hypothesis:

- a general information balance law valid across multiple classes of systems;
- representation-independent sign behavior of information derivatives;
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
