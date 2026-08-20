# UFT-ID 3.0 Roadmap

UFT-ID 3.0 is a constraint-governed, observer-explicit formalization programme with reproducible adversarial tests.

The project no longer organizes work as one long checklist around the overloaded summary tuple. The merged historical-lineage work, cross-repository audit, Deep Research formalization mining, and author-supplied paper review all point to the same architectural change:

```text
COMPACT_SUMMARY != COMPLETE_FORMAL_TYPE_SYSTEM
```

The compact notation remains useful:

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

but formal work is now split into typed satellites for residuals, recovery, observation, bridges, information, invariants, calibration, epistemics and assurance.

```text
NO_GIANT_FORMALIZATION_PR
```

Each PR must have one bounded authority surface, executable negative tests, an exit criterion, and explicit deferrals.

---

## Completed foundation

### Phase 0: lineage and provenance — COMPLETE

Merged PR #7 established:

- bounded historical source registry across the requested source families;
- exact source metadata and hash-scope rules;
- historical symbol mapping;
- preserved definition conflicts;
- historical result classification;
- methodological-inheritance contracts;
- fail-closed validation and deterministic receipts.

The governing rule remains:

```text
HISTORICAL_SOURCE != CURRENT_ENDORSEMENT
METHOD_INHERITANCE != ONTOLOGY_INHERITANCE
CONFLICT != ERROR_TO_ERASE
```

### Cross-repository pattern mining — COMPLETE

Merged PR #5 established the source/projection, calibration, replay, transport, receiver and evidence-boundary pattern layer plus finite results CR1–CR7.

### 2019 MEI reproduction — COMPLETE

Merged PR #6 reproduced Vopson's 2019 Eq. (6) arithmetic and separated:

```text
LANDAUER_ERASURE_BOUND
!= INTRINSIC_STORED_BIT_ENERGY
```

The physical premise remains unresolved despite arithmetic reproduction.

---

# Formal grammar programme

## PR #8 — Invariant calculus, assurance graph, and model obligations

**Status:** active in this pull request.

Implement:

- canonical `InvSpec[X,Y]`;
- exact / approximate / representation / transport / statistical / replay / epistemic / contract invariant kinds;
- explicit hypotheses and known break conditions;
- independent assurance dimensions rather than one promotion ladder;
- forbidden automatic proof/runtime/replay/empirical promotions;
- minimum definition obligations for theorem-facing mathematical objects;
- claim-vs-implementation realization obligations for reversibility, dimensionality, dynamics and simulation;
- `FalsificationSpec` scaffold;
- finite exact/adversarial witnesses;
- deterministic validation and receipt.

PDF/research-bundle ideas imported here are methodological only:

- claimed structure must be realized before stronger implementation claims are entitled;
- continuum objects require domain, regularity, operators, boundary/initial conditions and well-posedness status before theorem use;
- scientific falsifiability requires controlled perturbations, observables, predictions, null behavior and rejection conditions;
- connection/gauge language may later motivate abstract bridge theory but no semantic/consciousness ontology is inherited.

**Exit criterion:** every PR #8 invariant has a kind, hypotheses, break conditions, scope, claim class, source lineage and nonclaim; every assurance promotion is explicitly typed; every named theorem-facing object can be checked against a minimum declaration contract.

---

## PR #9 — Observation fibres, quotients, and reconstruction

Add:

\[
x\sim_O y \iff O(x)=O(y),
\]

fibres `O^-1(y)`, `im(O)`, quotient semantics, injectivity/surjectivity and reconstruction obligations.

Planned theorem family:

- observation equivalence relation;
- quotient/image correspondence;
- exact left-inverse criterion;
- linear kernel specialization only when `O` is linear;
- GLUBALL uniform-floor trichotomy;
- exact fibre-cardinality theorem.

**Exit criterion:** observer-dark language works for arbitrary finite/nonlinear maps; `ker(O)` appears only under linear hypotheses.

---

## PR #10 — Recovery taxonomy

Generalize recovery beyond `Pi_lex`.

Introduce a generic partial recovery:

```text
K : Dom(K) -> Option(A)
```

with mechanism tags for:

- lexicographic recovery;
- metric projection;
- decoder recovery;
- contractive/reference-relative recovery.

Planned results:

- finite lexicographic existence/uniqueness;
- recovery codomain/admissibility;
- contractive disturbance bound;
- recovery-does-not-imply-entropy-decrease counterexample.

**Exit criterion:** no theorem uses the generic word `recovery` while depending silently on lexicographic assumptions.

---

## PR #11 — Transport taxonomy and epistemic bridges

Split the overloaded `T` role into wrappers around a generic bridge:

\[
T^{state},\quad
T^{repr},\quad
T^{cal},\quad
T^{epi},\quad
T^{ver}.
\]

Every bridge records source, target, domain, preserved structure, lost structure, scope and authority behavior.

Planned results:

- admissibility preservation;
- calibration-transfer failure conditions;
- structural distortion bounds where justified;
- explicitly authority-neutral evidence transport cannot create stronger entitlement.

**Exit criterion:** every transport theorem names its role and proof obligations.

---

## PR #12 — Information-functional robustness

Replace naked `I` claims with a typed `InfoSpec` carrying the comparison identity required by the chosen functional.

Required fields, as applicable:

- domain/state kind;
- information family;
- observer/partition/reference;
- probability/measure model;
- estimator;
- log base;
- normalization;
- calibration profile;
- scope.

Canonical finite fixture:

\[
p_0=(0,0,\tfrac14,\tfrac34),\qquad
p_1=(0,\tfrac12,0,\tfrac12),
\]

where fine Shannon entropy rises but different valid observation partitions yield opposite observed entropy signs.

Planned results:

- bijective relabelling invariance;
- deterministic data-processing placement;
- observer/partition sign reversal;
- comparability rules for `Delta I`.

**Exit criterion:** every information-direction claim identifies a comparable `InfoSpec`.

---

## PR #13 — Finite reference-model battery

Consolidate ontology-free reference universes:

```text
Fin 27
Fin 3 × Fin 3 × Fin 3
Fin 101 × Fin 3
small finite probability simplices
M_2(Q)
arbitrary Fin(n) -> Fin(m) observation maps
```

Use LATTICE, ETQ, E8, GLUBALL, TFT and QNTOY only as donors of abstract finite structures or adversarial fixtures.

**Exit criterion:** each major theorem has a smallest positive/negative finite witness where applicable.

---

## PR #14 — Lean foundation and theorem-surface audit

Lean starts only after PRs #8–#13 stabilize the types and theorem statements.

Adopt UFF/NEXUS-style assurance architecture:

- versioned advertised theorem manifest;
- no `sorry`/`admit`;
- project-axiom/constant audit;
- explicit assumptions/nonclaims;
- axiom report;
- separate runtime-correspondence map.

Initial candidates:

- observation equivalence;
- quotient/image theorem;
- uniform-floor sampling;
- coprime traversal;
- finite lexicographic selection;
- contractive residual bound;
- small exact representation invariants.

```text
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

**Exit criterion:** exact advertised theorem set compiles/audits with no proof holes and no runtime/physical overclaim.

---

## PR #15 — Representation and receiver robustness

Introduce explicit representation actions/equivalence and receiver contracts.

Use TFT for basis-change examples, E8/ETQ for finite orbit/relabel fixtures, and SONIFICATION for source/receiver separation.

Distinguish:

```text
byte identity
content identity
mathematical equivalence
representation equivalence
receiver equivalence
semantic truth
```

**Exit criterion:** representation and receiver changes can be tested without modifying source ontology.

---

# Parallel scholarly reproduction programme

The formal grammar programme does not replace the source-faithful Vopson programme.

## Next Vopson reproduction

Reproduce the 2022 Second Law of Information Dynamics examples exactly:

- source definitions;
- preprocessing;
- entropy calculations;
- coding/alphabet/partition/window choices;
- reversible/permutation controls;
- alternative valid observations;
- sign robustness.

Then continue with:

- 2023 cross-domain applications;
- genomic examples;
- atomic/Hund-rule examples;
- symmetry/cosmology bridges;
- 2025 gravity;
- 2026 polygon/language extensions.

Every cross-domain step receives a bridge obligation and every scientific testable claim may receive a `FalsificationSpec` only after exact source reconstruction.

---

# Long-term empirical programme

After the typed grammar is stable:

- primary-literature comparison;
- null-model design;
- perturbation experiments;
- calibration sensitivity;
- preregistered rejection criteria;
- negative-result retention;
- independent replication.

For continuum/PDE specializations, require the `continuum model` definition obligation before theorem or simulation claims.

---

# Release criteria

UFT-ID 3.0 is release-ready only when:

1. all public claims have one canonical claim class;
2. reused ideas have provenance and non-inheritance boundaries;
3. theorem-facing objects satisfy definition obligations;
4. invariant claims name their transformation and hypotheses;
5. observation, recovery, transport and information roles are separately typed;
6. assurance dimensions cannot silently promote one another;
7. headline source-specific calculations are reproduced or explicitly blocked;
8. finite counterexamples exist for major failure modes;
9. Lean theorem claims, when present, are exactly manifest-bound and audited;
10. empirical claims have source data/protocol/calibration and do not borrow authority from proof or replay.

The desired endpoint is not a grander vocabulary. It is a smaller set of claims with stronger types, sharper falsifiers, and fewer places for hidden assumptions to hide.
