# UFT-ID 3.0 Roadmap

UFT-ID 3.0 is a constraint-governed, observer-explicit formalization programme with reproducible adversarial tests.

The current implementation order is governed by the post-PR8 research campaign:

```text
cross-repository mining
-> external mathematical completion audit
-> hostile mathematical audit
-> hostile verification of that audit
```

The architectural rules are:

```text
COMPACT_SUMMARY != COMPLETE_FORMAL_TYPE_SYSTEM
NO_GIANT_FORMALIZATION_PR
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

The compact mnemonic remains:

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

but it is a summary, not permission to collapse relation, observation, recovery, bridge, information, assurance, or physical semantics into one object.

Every implementation slice must preserve claim classes, explicit hypotheses, positive and adversarial fixtures, mutation tests, deterministic receipts where applicable, synchronized human/machine authority, explicit deferrals, and the boundary from implementation success to scientific truth.

The live schedule after merged PR #9 is machine-readable in `machine/roadmap_state.json`. The older `machine/formalization_contract.json::roadmap_rebase` remains the PR9-era compatibility snapshot used by the PR8/PR9 validators and receipts and is not rewritten retroactively.

---

# Completed foundation

## Phase 0: lineage and provenance — COMPLETE

Historical sources, symbols, definition conflicts, result status, and methodological inheritance were separated from current endorsement.

```text
HISTORICAL_SOURCE != CURRENT_ENDORSEMENT
METHOD_INHERITANCE != ONTOLOGY_INHERITANCE
CONFLICT != ERROR_TO_ERASE
```

## PR #5 — Cross-repository formal patterns — COMPLETE

Established source/projection, calibration, replay, transport, receiver, identity, and evidence-boundary patterns plus finite results CR1-CR7.

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

## 2019 MEI reproduction — COMPLETE

Merged PR #6 reproduced the source arithmetic while preserving:

```text
LANDAUER_ERASURE_BOUND != INTRINSIC_STORED_BIT_ENERGY
ARITHMETIC_REPRODUCED != PHYSICAL_VALIDATION
```

## PR #7 — Historical lineage and methodological inheritance — COMPLETE

Established bounded source lineage, symbol mapping, preserved conflicts, methodological inheritance, validation, and receipts.

## PR #8 — Invariant calculus, assurance graph, and model obligations — COMPLETE

Established typed `InvSpec`, the formal assurance graph, definition and model-realization obligations, falsification scaffolding, executable witnesses, and deterministic receipts.

```text
FORMAL_SYNTAX != PROOF
FORMAL_PROOF != RUNTIME_CONFORMANCE
RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
MODEL_OUTPUT != EXECUTION_EVIDENCE
REPLAY != MEASUREMENT
```

## PR #9 — Deterministic observation calculus — COMPLETE

Merged at commit `091405c136fd8dc936e6bd3a544ab22433d04782`.

```text
OBSERVATIONAL_EQUIVALENCE != PHYSICAL_IDENTITY
FIBRE != LINEAR_KERNEL
QUOTIENT_TO_IMAGE != QUOTIENT_TO_FULL_CODOMAIN
EXACT_RECONSTRUCTION != PHYSICAL_STATE_SURVIVAL
```

---

# Current formal grammar programme

## PR #9 — Deterministic observation calculus

**Status:** COMPLETE.

This heading remains in the ordered programme because later validators and theorem surfaces depend on its position. The merged implementation contains the typed deterministic observation contract, theorem/counterexample registries, exact finite witnesses, mutation tests, receipts, and CI.

---

## PR #10 — Lean observation foundation

**Status:** DEFERRED as an independent formal-proof track.

The hostile relation audit changed the immediate priority. Relation theorem statements and counterexamples should freeze before broadening the proof toolchain.

Future assurance still requires a pinned Lean toolchain and mathlib commit, no `sorry` or `admit`, theorem manifests, axiom audits, CI builds, and proposition identity in proof receipts.

```text
MATHLIB_THEOREM_EXISTS != OUR_LEAN_BUILD_PASSES
MATHEMATICAL_PROOF != LEAN_PROOF
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

---

## PR #11 — Relation-first recovery core

**Status:** ACTIVE, implemented by the current change.

### Mission

Replace the overstrong direct-recovery carrier

```text
K subseteq X x A
```

as the generic multi-step mechanism with a labelled binary endorelation on a declared carrier:

```text
stepRel : X -> X -> Prop
```

and keep admissibility separate:

```text
A : X -> Prop
```

The name `stepRel` avoids collision with the existing scalar residual `r:S->R_{>=0}`. `K subseteq X x A` remains valid only for a specialization whose one-step targets are already admissible.

### Canonical definitions

Freeze:

```text
Reach
Normal
Joinable
Confluent
Terminating
NormalizesFrom
AtMostOneReachableNormalFrom
```

with:

```text
NORMAL != ADMISSIBLE != FIXED_POINT
REACHABLE != ADMISSIBLE != NORMAL != UNIQUE_REACHABLE_NORMAL
```

### Advertised theorem surface

Implement and prove exactly:

1. `UFT-RW-001` branchwise invariant induction;
2. `UFT-RW-002` right-unique rewriting is confluent;
3. `UFT-RW-003` confluence gives at most one reachable normal form;
4. `UFT-RW-004` termination gives reachable normal-form existence;
5. `UFT-SEL-001` distinct reachable normal labels refute unique selection.

Treat termination plus confluence giving exactly one reachable normal form as a derived corollary of UFT-RW-003 and UFT-RW-004, not a separately inflated theorem ID.

### Selection discipline

If one source reaches normal forms `n1` and `n2` with:

```text
lambda(n1) != lambda(n2)
```

then `AtMostOneReachableNormalFrom(stepRel,x)` is false. The declared relation therefore cannot by itself justify a unique-selection claim over `lambda`.

```text
LABEL
-> PARAMETER
-> REALIZATION
-> INVARIANT
-> DISCRIMINANT
-> SELECTION THEOREM
```

No arrow is automatic.

### Minimal counterexamples

Ship only:

```text
CX-RW-FORK3
CX-RW-LOOP1
CX-RW-EXIT2
```

`FORK3` is the three-state terminating nonconfluent fork; `LOOP1` is the one-state confluent nonterminating loop; `EXIT2` has a unique reachable normal form plus a nonterminating branch.

```text
TERMINATION != CONFLUENCE
CONFLUENCE != TERMINATION
UNIQUE_REACHABLE_NORMAL_FORM != ALL_PATHS_NORMALIZE
```

### Bounded exhaustive conformance

Enumerate every labelled relation on `Fin 1`, `Fin 2`, and `Fin 3`:

```text
2 + 16 + 512 = 530 relations
```

These are adjacency relations on fixed labelled carriers. The executable does not quotient by carrier permutations or isomorphism classes.

Use this bounded surface to check finite theorem instances, fixture properties, and small-cardinality minimality claims.

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

### Genus-selection adversarial specialization

The internal stress fixture is:

```text
common -> M10
common -> M30

genus(M10) = 10
genus(M30) = 30
```

with independent topological constructions:

```text
Sigma_g = #_{h=1}^g T^2
chi(Sigma_g) = 2 - 2g
rank H_1(Sigma_g; Z) = 2g
```

so:

```text
Sigma_10: chi=-18, rank H1=20
Sigma_30: chi=-58, rank H1=60
```

Public context provenance is owned only by the canonical cross-repository registry:

- `XR-P17` pins the SONIFICATION ETQ-101 mathematical model and supplies the finite triality/qutrit compatibility context;
- `XR-P18` pins the SPECTRAL E8 Geometry Studio and supplies the Triality Spiral/qutrit/phi placement context.

`machine/genus_selection_specimen.json` references those XR IDs rather than maintaining a parallel repository/path/blob authority.

```text
E8_TRIALITY_COMPATIBILITY != UNIQUE_GENUS
GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION
LABELLED_HANDLE_DECORATION != TOPOLOGY_CONSTRUCTION
COMPATIBLE_REALIZATION != UNIQUE_SELECTION
INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION
```

A source-specific Genus-10 audit still requires exact external source/package identification before repository promotion.

### Explicit deferrals

Do not promote here:

- Newman's lemma;
- generic selector soundness;
- selector-independent normalization;
- observation-compatible quotient dynamics;
- schedule independence;
- trace semantics;
- finite-search assurance as a theorem family;
- universal infinite-branch eventuality;
- stochastic rewriting;
- Lean proof objects.

### Exit criterion

PR #11 is complete when `stepRel:X->X->Prop` and `A:X->Prop` remain separately typed; the theorem and counterexample surfaces are synchronized; all 530 labelled finite relations execute deterministically; canonical XR context references replace parallel pins; mutation tests reject semantic broadening and malformed input; receipts bind the authority surface; CI passes in normal and optimized Python; and no Lean or external-paper claim is over-promoted.

---

## PR #12 — BridgeCore

**Status:** PLANNED.

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

**Exit criterion:** bridge composition is typed and scope/version compatible; preservation and loss are explicit; transport cannot masquerade as semantic equivalence.

---

## PR #13 — Epistemic bridge specialization

**Status:** PLANNED.

Treat epistemic authority separately from structural transport. Do not impose an unsupported global lattice over unknown, conflict, retrieved, inferred, verified, or executed states.

**Exit criterion:** byte/structure transport cannot manufacture stronger evidence authority and conflict remains distinct from unknown.

---

## PR #14 — Representation and congruence calculus

**Status:** PLANNED.

Separate similarity, orthogonal/unitary similarity, congruence, coordinate change, and receiver transformation. Every invariant must name its transformation class and hypotheses.

**Exit criterion:** equality-like language cannot silently cross a representation boundary.

---

## PR #15 — Information comparability core

**Status:** PLANNED.

Freeze a typed `InfoSpec` and explicit `Comparable(I1,I2)` contract before information differences are entitled.

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
```

---

## PR #16 — Recovery specializations

**Status:** PLANNED.

Only after the relation core stabilizes, add finite lexicographic selection, metric projection, decoder recovery, contractive/reference-relative recovery, selector soundness/completeness, and executable normalizers where well-founded recursion is supplied.

```text
GENERIC_RELATION != DETERMINISTIC_SELECTOR
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
```

---

## PR #17 — Continuum, stochastic, and prevalence obligations

**Status:** PLANNED.

Add stochastic kernels, measurable spaces, continuum/PDE obligations, well-posedness status, prevalence/measure claims, explicit infinite paths, and fairness only after the finite deterministic core is stable.

```text
FINITE_REACHABILITY != INFINITE_PATH_LIVENESS
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
```

---

## PR #18 — Empirical falsification profile

**Status:** PLANNED.

Connect formal structures to empirical hypotheses with controlled variables, observables, predictions, null models, rejection conditions, uncertainty, provenance, scope, and explicit formal-to-measurement bridges.

```text
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
EMPIRICAL_FIT != UNIQUE_EXPLANATION
```

---

# Formal fixture policy

```text
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

Minimal fixtures travel with the theorem or counterexample that needs them. A fixture must have theorem-conformance, counterexample, assumption-ablation, minimality, or deterministic-receipt purpose.

For the genomic/Vopson branch only:

```text
GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY
```

---

# Lean policy

Lean remains a separate formal-verification track.

Repository-contained mathematical proofs may be classified `PROVED` when complete and auditable in the repository, but they must not be described as machine checked until the pinned Lean toolchain builds them.

Initial future relation targets mirror, rather than silently broaden, the frozen theorem surface:

```text
UFT_RW_001_reach_preserves
UFT_RW_002_rightUnique_confluent
UFT_RW_003_confluent_reachableNormal_eq
UFT_RW_004_terminating_reachesNormal
UFT_SEL_001_distinctNormalLabels_refuteUniqueSelection
```

```text
THEOREM_STATEMENT_FROZEN != LEAN_PROVED
MATHEMATICAL_PROOF != MACHINE_CHECKED_PROOF
```

---

# Selection and uniqueness policy

Future unique-selection claims must distinguish compatibility, existence, realization, invariance, discrimination, uniqueness, and physical selection. At minimum, `COMPATIBLE(X)` does not imply `UNIQUE(X)`.

A robust uniqueness claim identifies the candidate class, admissibility predicate, derivation/reachability semantics, terminal criterion if used, selected label, discriminant or exclusion theorem, and every extra hypothesis required for uniqueness.

```text
same source
+ two reachable normal realizations
+ distinct semantic labels
=> no unique selection from the declared relation alone
```

---

# Reproducibility gate

Every executable formal surface must pass:

```bash
python -m compileall -q experiments scripts tests
python scripts/validate_reproducibility.py
python scripts/validate_cross_repo_patterns.py
python scripts/validate_historical_lineage.py
python scripts/validate_formalization_contracts.py
python scripts/validate_observation_specs.py
python scripts/validate_relation_core.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/relation/run.py --json
python experiments/run_pr11.py --json
```

The relation suite is standard-library Python and bounded to the declared 530 labelled-relation conformance surface in routine CI.

```text
GREEN_CI != PHYSICAL_TRUTH
DETERMINISTIC_RECEIPT != SCIENTIFIC_CONFIRMATION
```

---

# Historical PR8 planning anchors retained for validator compatibility

The following phrases are the older PR8-era planning surface. They remain verbatim for validator/receipt compatibility and are **not** the live schedule above.

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

The post-PR8 hostile audit superseded that order while preserving its provenance.

---

# Release-level exit criteria

A future formalization release should not be cut until every advertised theorem has an inspectable proof or is explicitly a theorem target; machine and human statements agree; counterexamples remain executable; source-specific critiques identify exact sources; private locators do not leak; proof/runtime/empirical/physical layers stay separate; unique-selection claims survive alternate-realization tests; CI evidence is retained; and all deferrals remain visible.

```text
A BEAUTIFUL STRUCTURE CAN BE COMPATIBLE
WITHOUT BEING UNIQUE,
AND A UNIQUE MATHEMATICAL RESULT CAN STILL FAIL
TO SELECT A PHYSICAL ONTOLOGY.
```
