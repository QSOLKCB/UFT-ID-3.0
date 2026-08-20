# UFT-ID 3.0 Roadmap

UFT-ID 3.0 is a constraint-governed, observer-explicit formalization programme with reproducible adversarial tests.

The post-PR8 research campaign changed the implementation order substantially. Four research passes now govern the roadmap:

```text
cross-repository mining
-> external mathematical completion audit
-> hostile mathematical audit
-> hostile verification of that audit
```

The governing design rules are:

```text
COMPACT_SUMMARY != COMPLETE_FORMAL_TYPE_SYSTEM
NO_GIANT_FORMALIZATION_PR
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

The compact mnemonic remains:

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

but formal authority is split into typed surfaces for observation, reconstruction, recovery, bridges, information, invariants, calibration, epistemics, assurance, falsification, and later formal proof.

Each PR must have:

- one bounded authority surface;
- one canonical claim class per claim;
- exact machine/human synchronization where both exist;
- positive and adversarial fixtures;
- fail-closed mutation tests;
- deterministic receipts where executable evidence is claimed;
- explicit deferrals.

---

# Completed foundation

## PR #5 — Cross-repository formal patterns — COMPLETE

Established source/projection, calibration, replay, transport, receiver, identity, and evidence-boundary patterns plus finite results CR1-CR7.

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

## PR #6 — 2019 MEI reproduction — COMPLETE

Reproduced the source arithmetic while preserving:

```text
LANDAUER_ERASURE_BOUND != INTRINSIC_STORED_BIT_ENERGY
ARITHMETIC_REPRODUCED != PHYSICAL_VALIDATION
```

## PR #7 — Historical lineage and methodological inheritance — COMPLETE

Established bounded source lineage, symbol mapping, preserved conflicts, historical result classification, methodological inheritance, validation, and receipts.

## PR #8 — Invariant calculus, assurance graph, and model obligations — COMPLETE

Established:

- typed `InvSpec` machinery;
- formal assurance graph;
- machine-enforced non-promotion boundaries;
- definition obligations;
- model-realization obligations;
- falsification scaffold;
- executable witnesses;
- hardened private-source/provenance rules;
- deterministic receipts.

PR #8 survived two Codex hardening passes and the subsequent hostile external audit without requiring architectural replacement.

```text
FORMAL_SYNTAX != PROOF
FORMAL_PROOF != RUNTIME_CONFORMANCE
RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
MODEL_OUTPUT != EXECUTION_EVIDENCE
REPLAY != MEASUREMENT
```

---

# Current formal grammar programme

## PR #9 — Deterministic observation calculus

**Status:** ACTIVE.

Implement only the deterministic set-theoretic core:

- typed `ObservationSpec`;
- fibres;
- observational equivalence;
- image;
- quotient-to-image correspondence;
- injectivity/surjectivity boundaries;
- image-scoped exact reconstruction;
- impossibility of global exact left inversion for noninjective observations;
- exact uniform floor-sampling trichotomy and fibre cardinality;
- minimal `Fin2`/`Fin1` counterexamples;
- validator, executable witness, mutation tests, receipt, and CI evidence.

Canonical boundaries:

```text
OBSERVATIONAL_EQUIVALENCE != PHYSICAL_IDENTITY
FIBRE != LINEAR_KERNEL
QUOTIENT_TO_IMAGE != QUOTIENT_TO_FULL_CODOMAIN
EXACT_RECONSTRUCTION != PHYSICAL_STATE_SURVIVAL
```

Explicitly deferred from PR #9:

- Lean toolchain/bootstrap;
- stochastic kernels;
- Blackwell comparison;
- sufficient-statistic theory;
- sigma-algebra refinement;
- RecoverySpec;
- InfoSpec;
- representation/congruence calculus;
- physical observer interpretation.

**Exit criterion:** deterministic observations have a complete typed contract; theorem and counterexample statements are machine-bound; the floor-sampling formula executes exactly; the noninjective reconstruction boundary is preserved under mutation tests; CI passes in normal and optimized Python.

---

## PR #10 — Lean observation foundation

Create a pinned Lean/mathlib environment **after** PR #9 freezes the observation statements.

Target the smallest set-theoretic theorem family first:

- observational equivalence/setoid;
- quotient-to-range equivalence;
- left-inverse/injectivity relations;
- right-inverse/surjectivity relations;
- fibre/class equivalence;
- then floor-sampling arithmetic if the pinned library/toolchain supports the chosen proof cleanly.

Required assurance:

- pinned `lean-toolchain` and mathlib commit;
- theorem manifest;
- no `sorry`/`admit`;
- axiom/assumption audit;
- theorem proposition identity bound into receipt;
- CI build.

```text
MATHLIB_THEOREM_EXISTS != OUR_LEAN_BUILD_PASSES
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

**Exit criterion:** repository-local Lean proofs build reproducibly under the pinned toolchain and correspond exactly to the advertised observation theorem manifest.

---

## PR #11 — Relation-first recovery core

Replace generic recovery-as-`Option(A)` with a relation/set-valued core.

Primary abstraction:

```text
K subseteq X x A
```

or equivalent set-valued form.

A deterministic selector is a refinement, not the generic definition.

Keep these properties independently typed:

```text
existence
uniqueness
totality
admissibility
optimality
idempotence
continuity
measurability
nonexpansiveness
contractivity
stability
computability
```

Required minimal failures:

```text
RECOVERY_EXISTS != RECOVERY_UNIQUE
RECOVERY_ADMISSIBLE != RECOVERY_OPTIMAL
RECOVERY_OPTIMAL != INFORMATION_DECREASE
RECOVERY_CONVERGES != ORIGINAL_STATE_RESTORED
REFERENCE_RELATIVE_ZERO != ABSOLUTE_ZERO
```

**Exit criterion:** no generic recovery statement silently assumes uniqueness, selection, metric optimality, convergence, or restoration.

---

## PR #12 — BridgeCore

Define the smallest structural bridge common to state/version/calibration/representation transport:

```text
source_type
target_type
domain
map_or_relation
preserved_structure
lost_structure
scope
source_version
target_version
```

Do not force every arrow into one mathematical category.

Role-specific extensions may add calibration or version semantics only when needed.

**Exit criterion:** bridge composition is typed and scope/version compatible; preservation and loss are explicit; transport cannot masquerade as semantic equivalence.

---

## PR #13 — Epistemic bridge specialization

Treat epistemic authority separately from structural transport.

Do **not** impose a universal total order or global lattice over states such as:

```text
unknown
conflict
retrieved
inferred
verified
executed
```

Use independent dimensions or local preorders only where their semantics are explicit.

A local non-promotion theorem may take the form

```text
E(Tx) <= E(x)
```

only after the order direction and evidence dimension are defined.

Composition should rely only on the actual order properties proved, typically transitivity for a preorder.

**Exit criterion:** byte/structure transport cannot manufacture stronger evidence authority; conflict and unknown remain distinct; no unjustified meet/join operation exists.

---

## PR #14 — Representation and congruence calculus

Correctly distinguish:

```text
similarity
orthogonal similarity
unitary similarity
congruence
basis/coordinate change
receiver transformation
```

The hostile audit established that

```text
T' = R T R^T
```

is a congruence transformation in general and becomes similarity only under the appropriate orthogonal hypothesis.

For complex unitary transformations, distinguish transpose from adjoint.

Required counterexample:

```text
T = I_2
R = diag(2,1)
```

which destroys unsupported eigenvalue/trace/determinant/Frobenius/singular-value invariance claims under general invertible congruence while preserving the narrower valid results.

**Exit criterion:** every invariant names its transformation class and hypotheses; congruence is never silently called similarity; exact algebraic invariance is separate from numerical tolerance.

---

## PR #15 — Information comparability core

Introduce the narrow first `InfoSpec` implementation for finite Shannon/KL-style comparison.

The key operation is not metadata equality but:

```text
Comparable(I1, I2)
```

before:

```text
delta(I1, I2)
sign_delta(I1, I2)
```

Identical specifications imply comparability, but comparability may also be established by a canonical unit conversion, declared relabeling/isomorphism, or explicit comparison bridge.

```text
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
SAME_SYMBOL_I != SAME_MATHEMATICAL_QUANTITY
```

First-family scope:

- finite Shannon entropy;
- finite KL divergence with explicit reference/support conditions;
- common log/unit handling;
- observer/partition/reference identity;
- comparison bridge semantics.

Use both entropy fixtures:

- `Fin3` as the cardinality-minimal opposite-observer-sign fixture;
- the existing `Fin4` case as the stronger regression fixture when its stronger fine/observed sign pattern is useful.

Representation-independent subclaims may proceed without PR #14. **Representation-invariance claims are gated by PR #14.**

**Exit criterion:** `Delta I` cannot be formed as an entitled comparison unless the family-specific comparison contract is satisfied or explicitly bridged.

---

## PR #16 — Recovery specializations

Build selected specializations only after the relation-first core is stable:

- finite lexicographic selector;
- metric projection;
- contractive/reference-relative iteration;
- decoder specialization where justified.

For finite lexicographic selection, require an actual order strong enough to guarantee a minimum. Pairwise "tie broken" language is not sufficient if cyclic preference is possible.

For contraction results, retain the real Banach hypotheses:

- complete metric space;
- self-map;
- contraction constant `< 1`.

**Exit criterion:** each specialization states the property it gains beyond generic recovery and the hypothesis that grants it.

---

## PR #17 — Continuum, stochastic, and prevalence obligations

Strengthen existing definition obligations rather than creating a giant new continuum type.

Continuum claims conditionally require:

```text
solution_concept
existence_status
uniqueness_status
stability_status
regularity_status
```

Numerical claims additionally name scheme/discretization/error norm/convergence scope.

Stochastic claims conditionally declare:

```text
probability_space
filtration
process
initial_law
noise_law
integrability
assertion_mode
```

with assertion modes distinguished explicitly, such as pathwise, almost sure, in probability, in distribution, expectation, generator, stationary, ergodic, or asymptotic.

Genericity/prevalence language must name the relevant topology, measure, probability law, perturbation class, metric/tolerance, or dynamics as applicable.

```text
FIXED_POINT != DYNAMICAL_STABILITY
EXISTS != STABLE != ATTRACTING != GENERIC != LIKELY != OBSERVED
```

The known fixed-point/stability terminology defect must be repaired before any stability theorem is promoted. It is intentionally **not bundled into PR #9**.

**Exit criterion:** continuum/stochastic/prevalence terminology cannot produce a theorem-shaped statement without enough structure to determine what proposition is actually being asserted.

---

## PR #18 — Empirical falsification profile

Extend `FalsificationSpec` only for actual empirical evaluation.

Add explicit decision semantics such as:

```text
NOT_EVALUATED
REJECTED
NOT_REJECTED
INCONCLUSIVE
```

and machine-forbid:

```text
NOT_REJECTED => CONFIRMED
NOT_REJECTED => VALIDATED
```

Conditionally require empirical fields such as:

- measurement model;
- calibration identity;
- uncertainty model;
- fit/calibration/test/holdout data roles;
- prospective prediction chronology where prediction is claimed.

Do not force power analysis, multiplicity correction, stopping rules, effect thresholds, exclusion policies, or alternative hypotheses into every mathematical falsification record.

**Exit criterion:** empirical decision state, calibration, uncertainty, and data roles cannot silently promote failure-to-reject into confirmation.

---

# Formal fixture policy

There is no longer a standalone finite-model-battery PR.

```text
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

Minimal fixtures travel with the theorem or counterexample that needs them.

Preferred foundational fixtures include:

- constant `Fin2 -> Fin1` for observation collision/reconstruction failure;
- `Fin1 -> Fin2` for image versus codomain;
- `Fin3` probability fixture for minimal observer-sign reversal;
- two-state probability simplex/kernels for elementary stochastic information checks;
- singleton input with two recovery candidates;
- scalar `x -> x/2` for convergence versus restoration;
- `M_2(Q)`/small exact matrices for congruence failures;
- parameterized floor maps for finite sampling.

Larger donor-specific fixtures such as `Fin27`, `Fin3^3`, or `Fin101 x Fin3` remain valid regression/specimen surfaces only when the theorem actually requires their structure.

---

# Parallel Vopson reproduction programme

The formal grammar programme and source-faithful reproduction programme remain separate evidence streams.

## Digital SLI branch

The 2022 digital SLI example can be reproduced independently of GENIES.

Target:

```text
2022-SLI-DIGITAL
```

Reconstruct exact source states, probability convention, entropy calculation, claimed directionality, and controls.

## Genomic/RNA branch

```text
GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY
```

Recommended order:

```text
2021 GENIES method
-> RNA/genomic reproduction surfaces
-> 2022 genetic-law trajectory and matched null controls
```

GENIES is not a prerequisite for the independent digital SLI example.

## Later source tracks

After the above:

- 2023 cross-domain SLI;
- later genomic/atomic applications;
- 2025 gravity only after its MEI + SLI + entropic-force bridges are separately reconstructed.

Every reproduction keeps:

```text
SOURCE_ARITHMETIC != SCIENTIFIC_GENERALIZATION
SELECTED_TRAJECTORY != FORWARD_PREVALENCE
REPRODUCED != VALIDATED
```

---

# PR #8 roadmap compatibility ledger

The following headings are retained **only** as historical anchors for the merged PR #8 formalization validator and deterministic receipt. They describe the pre-audit scheduling baseline and are not the current implementation order.

```text
PR #8 — Invariant calculus, assurance graph, and model obligations
PR #9 — Observation fibres, quotients, and reconstruction
PR #10 — Recovery taxonomy
PR #11 — Transport taxonomy and epistemic bridges
PR #12 — Information-functional robustness
PR #13 — Finite reference-model battery
PR #14 — Lean foundation and theorem-surface audit
PR #15 — Representation and receiver robustness
```

For the same historical validator, the completed foundation corresponds to the legacy labels:

```text
Phase 0: lineage and provenance — COMPLETE
2019 MEI reproduction — COMPLETE
```

Current scheduling authority is the numbered programme above, not this compatibility ledger.

---

# Release criteria

UFT-ID 3.0 is release-ready only when:

1. every public claim has one canonical claim class;
2. every theorem-facing object satisfies its definition obligations;
3. observation, reconstruction, recovery, bridge, information, representation, and evidence roles are separately typed;
4. invariant statements name the transformation class and hypotheses;
5. information differences have a valid comparability contract;
6. observation equivalence cannot be mistaken for physical identity;
7. recovery existence/uniqueness/optimality/convergence/restoration remain independent properties;
8. transport cannot manufacture evidence authority;
9. genericity, measure, probability, stability, attraction, and observation remain distinct qualifiers;
10. finite counterexamples travel with the propositions they falsify;
11. Lean claims, when present, are repository-built under a pinned toolchain and manifest-bound;
12. empirical falsification distinguishes rejection, non-rejection, inconclusive outcomes, calibration, uncertainty, and data roles;
13. source-specific calculations are reproduced or explicitly blocked without laundering reproduction into physical confirmation.

The endpoint is not a larger theory vocabulary. It is a smaller set of claims with stronger types, smaller witnesses, sharper failure conditions, and fewer places for assumptions to hide.
