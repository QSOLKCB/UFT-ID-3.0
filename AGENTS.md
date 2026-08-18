# AGENTS.md

## Purpose

This repository is a research program, not a claim amplifier. Agents must preserve the boundary between mathematics, diagnostics, empirical evidence, interpretation, and speculation.

## Required operating sequence

Before changing theory content:

1. read `README4AI.md`;
2. read `docs/CLAIMS.md` and `docs/NONCLAIMS.md`;
3. locate the source or derivation being changed;
4. state the claim class being modified;
5. preserve provenance and uncertainty;
6. add or update tests, counterexamples, or citations where appropriate.

## Source hierarchy

Prefer, in order:

1. primary peer-reviewed literature;
2. primary preprints with clear status labels;
3. official datasets and code;
4. source papers in the UFT-ID lineage;
5. secondary commentary only for historical or interpretive context.

Do not cite a secondary summary when a primary source is available for the technical claim.

## UFT-ID lineage rule

Earlier UFT-ID papers contain several incompatible levels of commitment. UFT-ID 3.0 inherits the abstract constraint-first machinery first. Lattice, E8, SU(3), LQG, gravity, cognition, AGI, and consciousness mappings are optional specializations unless separately established.

## Mathematical discipline

- Define state space, sigma-algebra or discrete structure, measure, dynamics, and information functional before differentiating or comparing information.
- State regularity assumptions.
- Check units and dimensions.
- Distinguish state entropy from entropy production.
- Distinguish closed, isolated, and open systems.
- Distinguish boundary flux from internal production.
- Distinguish coarse-graining loss from physical dissipation.
- Distinguish observer-relative inaccessible information from destroyed information.
- Distinguish deterministic state selection from stochastic evolution.
- Record counterexamples, not only supporting examples.

## Cross-domain rule

A shared mathematical pattern is not evidence of a shared substrate or cause.

When reusing a construction across domains, declare the mapping explicitly:

```text
source objects -> target objects
source dynamics -> target dynamics
preserved invariants -> preserved invariants
lost structure -> lost structure
```

If this map is not supplied, label the correspondence `INTERPRETIVE`.

## Adversarial review rule

Every major theorem target or empirical claim should have an adversarial companion question:

- What is the weakest assumption that makes this false?
- Is the result invariant under relabeling or change of representation?
- Is the sign of the claimed entropy change partition-dependent?
- Does a null model reproduce the effect?
- Was the metric selected after seeing the data?
- Is the apparent law actually a property of the encoding or boundary condition?
- Does the result survive alternative entropy measures?
- Is the result causal, descriptive, or merely correlational?

## Vopson research rule

Treat Vopson's papers as scientific targets, never as targets for personal attack. Reproduce before criticizing. Separate his independent claims rather than bundling them:

1. mass-energy-information equivalence;
2. information-entropy monotonicity;
3. cross-domain applications;
4. gravity derivation;
5. simulation-hypothesis interpretation.

A successful critique should be stronger than a rhetorical contradiction. Preferred outcomes are:

- a proof that the claim requires additional hypotheses;
- a valid counterexample under the stated hypotheses;
- a representation-dependence result;
- a failed independent replication;
- a dimensional or algebraic inconsistency;
- a demonstration that the claimed effect follows from a simpler established model;
- a statistically controlled result that distinguishes competing explanations.

## Formal verification rule

Lean is a later hardening phase. Do not add placeholder `.lean` files that pretend to formalize unsettled mathematics. The roadmap must first reach a notation and theorem freeze.

When Lean work begins:

- compile in CI;
- keep theorem statements close to paper notation;
- distinguish imported library theorems from UFT-ID theorems;
- include executable finite counterexamples where relevant;
- never claim a physical interpretation has been proved merely because an abstract theorem has been verified.

## Repository hygiene

- Keep generated artifacts out of source directories.
- Keep data licenses and provenance explicit.
- Avoid binary paper copies when stable DOI citations are sufficient.
- Do not rewrite historical source papers to make them appear consistent with UFT-ID 3.0.
- Record supersession and disagreement instead.
