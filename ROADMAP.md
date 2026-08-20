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

but it is a summary, not permission to collapse distinct relation, observation, recovery, bridge, information, assurance, or physical semantics into one object.

Each implementation slice must have:

- one bounded authority surface;
- one canonical claim class per claim;
- explicit definitions and hypotheses;
- positive and adversarial fixtures;
- fail-closed mutation tests;
- deterministic receipts where executable evidence is claimed;
- exact machine/human synchronization where both exist;
- explicit deferrals;
- no automatic promotion from implementation success to scientific or physical truth.

The live schedule after merged PR #9 is machine-readable in:

```text
machine/roadmap_state.json
```

The older `machine/formalization_contract.json::roadmap_rebase` remains the PR9-era compatibility snapshot used by the PR8/PR9 validators and receipts. It is not rewritten retroactively merely to move the live pointer.

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

Established:

- typed `InvSpec` machinery;
- formal assurance graph;
- machine-enforced non-promotion boundaries;
- definition obligations;
- model-realization obligations;
- falsification scaffold;
- executable witnesses;
- deterministic receipts.

```text
FORMAL_SYNTAX != PROOF
FORMAL_PROOF != RUNTIME_CONFORMANCE
RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
MODEL_OUTPUT != EXECUTION_EVIDENCE
REPLAY != MEASUREMENT
```

## PR #9 — Deterministic observation calculus — COMPLETE

Merged at commit:

```text
091405c136fd8dc936e6bd3a544ab22433d04782
```

Implemented deterministic set-theoretic observation, fibres, observational equivalence, quotient-to-image correspondence, injectivity/surjectivity boundaries, exact reconstruction scope, floor-sampling arithmetic, counterexamples, validators, receipts, and CI.

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

This heading is retained in the ordered programme because later validators and theorem surfaces depend on its position.

Exit criterion was met on merged main: deterministic observations have a typed contract, theorem/counterexample registries, exact finite witnesses, mutation tests, and deterministic receipts.

---

## PR #10 — Lean observation foundation

**Status:** DEFERRED as an independent formal-proof track.

The original plan was to bootstrap a pinned Lean/mathlib environment immediately after PR #9. The hostile relation audit changed the priority: theorem statements and counterexamples for the relation core should be frozen before expanding the proof environment.

This deferral does **not** promote Python checks into Lean proofs.

Later targets remain:

- observational equivalence/setoid;
- quotient-to-range equivalence;
- left-inverse/injectivity relations;
- right-inverse/surjectivity relations;
- fibre/class equivalence;
- floor-sampling arithmetic where suitable;
- the relation/reachability theorem family after its statements freeze.

Required future assurance:

- pinned `lean-toolchain`;
- pinned mathlib commit;
- no `sorry` or `admit`;
- theorem manifest;
- axiom/assumption audit;
- CI build;
- proposition identity bound into proof receipts.

```text
MATHLIB_THEOREM_EXISTS != OUR_LEAN_BUILD_PASSES
MATHEMATICAL_PROOF != LEAN_PROOF
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

Lean remains deferred in the repository contract until the proof toolchain is deliberately introduced.

---

## PR #11 — Relation-first recovery core

**Status:** ACTIVE, implemented by the current change.

### Mission

Replace the overstrong direct-recovery carrier

```text
K subseteq X x A
```

as the generic multi-step mechanism with an unlabelled binary endorelation:

```text
r : X -> X -> Prop
```

and keep admissibility separate:

```text
A : X -> Prop
```

`K subseteq X x A` remains valid only for a specialization whose one-step targets are already admissible. It is not the general rewrite/reachability carrier.

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

### Advertised foundational theorem surface

Implement and prove exactly:

1. `UFT-RW-001` — branchwise invariant induction;
2. `UFT-RW-002` — right-unique rewriting is confluent;
3. `UFT-RW-003` — confluence gives at most one reachable normal form;
4. `UFT-RW-004` — termination gives reachable normal-form existence.

Treat:

```text
termination + confluence
=> exactly one reachable normal form
```

as a derived corollary of UFT-RW-003 and UFT-RW-004, not another independently inflated theorem ID.

### Selection theorem

Add:

```text
UFT-SEL-001
```

Distinct reachable normal labels refute unique selection.

If the same source reaches normal forms `n1` and `n2` and a semantic label map satisfies:

```text
lambda(n1) != lambda(n2)
```

then:

```text
not AtMostOneReachableNormalFrom(r, x)
```

and the declared relation alone cannot justify a unique-selection claim over that label.

This creates the reusable epistemic ladder:

```text
LABEL
-> PARAMETER
-> REALIZATION
-> INVARIANT
-> DISCRIMINANT
-> SELECTION THEOREM
```

No arrow is automatic.

### Minimal canonical counterexamples

Ship only:

```text
CX-RW-FORK3
CX-RW-LOOP1
CX-RW-EXIT2
```

`CX-RW-FORK3`:

```text
a -> b
a -> c
```

with `b,c` normal.

It demonstrates:

```text
BRANCHING != CONFLUENCE
TERMINATION != CONFLUENCE
TERMINATION != UNIQUE_NORMAL_FORM
ONE_SELECTOR_RESULT != RELATION_SEMANTICS
```

`CX-RW-LOOP1`:

```text
a -> a
```

demonstrates:

```text
CONFLUENCE != TERMINATION
CONFLUENCE != NORMAL_FORM_EXISTENCE
```

`CX-RW-EXIT2`:

```text
a -> a
a -> b
```

with `b` normal, demonstrates:

```text
UNIQUE_REACHABLE_NORMAL_FORM != TERMINATION
UNIQUE_REACHABLE_NORMAL_FORM != ALL_PATHS_NORMALIZE
WEAK_NORMALIZATION != STRONG_NORMALIZATION
```

### Bounded exhaustive conformance

Enumerate every unlabelled relation on `Fin 1`, `Fin 2`, and `Fin 3`:

```text
2 + 16 + 512 = 530 relations
```

Use this to:

- check finite instances of the theorem implications;
- verify fixture properties;
- verify the stated small-cardinality minimality boundaries.

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

The mathematical proofs live in `theory/RELATION_CALCULUS.md`.

### Genus-selection adversarial specialization

Add a deliberately minimal internal selection stress test:

```text
common -> M10
common -> M30
```

with both endpoints normal in the declared fixture and:

```text
genus(M10) = 10
genus(M30) = 30
```

Use independent topological constructions:

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

Public compatibility context is pinned from SONIFICATION and SPECTRAL, but remains context-only:

- SONIFICATION supplies 33 complete triality/qutrit blocks + two singlets, `D3=diag(1,-2,1)`, the `theta=pi/2` kick, and `F3^3=I3`;
- SPECTRAL supplies Triality Spiral/qutrit/phi control geometry.

Those structures may decorate or order labelled handle sectors. They do not derive topology.

```text
E8_TRIALITY_COMPATIBILITY != UNIQUE_GENUS
GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION
LABELLED_HANDLE_DECORATION != TOPOLOGY_CONSTRUCTION
COMPATIBLE_REALIZATION != UNIQUE_SELECTION
```

The internal fixture proves a selection-logic failure under its declared premises. It does not automatically become a verdict on any external paper or code package.

```text
INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION
```

A source-specific Genus-10 audit requires exact public source/package pins before repository promotion.

### Explicit removals from the PR #11 theorem surface

Do not implement as headline theorems here:

- Newman's lemma;
- generic selector soundness;
- selector-independent normalization;
- observation-compatible quotient dynamics;
- schedule independence;
- trace semantics;
- finite-search assurance;
- `all_branches_eventually_admissible`.

Universal eventuality over infinite branches needs explicit infinite path semantics and potentially fairness. Reflexive-transitive closure quantifies over finite reductions only.

### Exit criterion

PR #11 is complete when:

- `r:X->X->Prop` is the generic carrier;
- `A:X->Prop` remains separate;
- the four foundational rewrite theorems and `UFT-SEL-001` are human/machine synchronized;
- the three minimal counterexamples are frozen;
- all 530 relations through `Fin3` execute deterministically;
- genus 10/30 is an internal, provenance-bounded stress test;
- mutation tests reject semantic broadening;
- CI passes in normal and optimized Python;
- deterministic receipts bind the authority surface;
- no Lean proof is claimed.

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

Do not force every arrow into one mathematical category.

**Exit criterion:** bridge composition is typed and scope/version compatible; preservation and loss are explicit; transport cannot masquerade as semantic equivalence.

---

## PR #13 — Epistemic bridge specialization

**Status:** PLANNED.

Treat epistemic authority separately from structural transport.

Do not impose a universal total order over:

```text
unknown
conflict
retrieved
inferred
verified
executed
```

Use independent dimensions or local preorders only where semantics are explicit.

**Exit criterion:** structure/byte transport cannot manufacture stronger evidence authority; conflict and unknown remain distinct.

---

## PR #14 — Representation and congruence calculus

**Status:** PLANNED.

Separate:

```text
same source object
same normalized object
same observation
same representation
same semantics
same physical state
```

Define relation/congruence obligations only for transformations that actually preserve the required structure.

**Exit criterion:** no equality-like word silently crosses a representation or ontology boundary.

---

## PR #15 — Information comparability core

**Status:** PLANNED.

Freeze a typed `InfoSpec` containing, as applicable:

```text
functional family
domain
codomain
reference measure/distribution
partition/alphabet
observation map
estimator
units/conventions
scope
```

Require explicit bridges before comparing information values across changed contracts.

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
```

**Exit criterion:** monotonicity and cross-regime comparisons cannot omit the information contract.

---

## PR #16 — Recovery specializations

**Status:** PLANNED.

Only after the relation core is stable, add refinements such as:

- finite lexicographic selection;
- metric projection;
- decoder recovery;
- contractive/reference-relative recovery;
- selector soundness/completeness;
- executable normalizers where well-founded recursion is supplied.

```text
GENERIC_RELATION != DETERMINISTIC_SELECTOR
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
```

**Exit criterion:** specialization theorems list every extra assumption they consume.

---

## PR #17 — Continuum, stochastic, and prevalence obligations

**Status:** PLANNED.

Add only after finite deterministic semantics stabilize:

- stochastic kernels;
- measurable state spaces;
- continuum/PDE obligations;
- well-posedness status;
- prevalence/measure claims;
- infinite path semantics;
- fairness only where explicitly needed.

```text
FINITE_REACHABILITY != INFINITE_PATH_LIVENESS
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
```

**Exit criterion:** continuum/stochastic notation cannot appear without its analytic contract.

---

## PR #18 — Empirical falsification profile

**Status:** PLANNED.

Connect theorem-facing formal structures to empirical hypotheses without promotion leakage.

Require:

- controlled variables;
- observables;
- predictions;
- null model;
- rejection condition;
- uncertainty;
- provenance;
- scope;
- explicit bridge from formal object to measurement.

```text
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
EMPIRICAL_FIT != UNIQUE_EXPLANATION
```

---

# Formal fixture policy

```text
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

Minimal fixtures travel with the theorem or counterexample that requires them.

A fixture must have at least one of:

- theorem conformance purpose;
- counterexample purpose;
- assumption-ablation purpose;
- minimality purpose;
- deterministic receipt purpose.

Rule 110, decorative dependency graphs, broad schedule examples, or unrelated finite-search demonstrations do not enter a formal PR merely because they are interesting.

For the genomic/Vopson research branch only:

```text
GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY
```

That research-specific gate does not contaminate the generic relation calculus.

---

# Lean policy

Lean remains a separate formal-verification track.

Repository-contained mathematical proofs may be classified `PROVED` when complete and auditable in the repository, but they must not be described as machine checked until the pinned Lean toolchain builds them.

Initial future relation targets should mirror, not silently broaden, the frozen theorem surface:

```text
UFT_RW_001_reach_preserves
UFT_RW_002_rightUnique_confluent
UFT_RW_003_confluent_reachableNormal_eq
UFT_RW_004_terminating_reachesNormal
UFT_SEL_001_distinctNormalLabels_refuteUniqueSelection
```

Newman's lemma comes later only with a complete proof.

```text
THEOREM_STATEMENT_FROZEN != LEAN_PROVED
MATHEMATICAL_PROOF != MACHINE_CHECKED_PROOF
```

---

# Selection and uniqueness policy

Any future UFT-ID claim that a structure, parameter, topology, representation, model, or regime is uniquely selected must distinguish:

```text
compatibility
existence
realization
invariance
discrimination
uniqueness
physical selection
```

At minimum:

```text
COMPATIBLE(X)
```

does not imply:

```text
UNIQUE(X)
```

and a numerical observable that is constant across competing candidates has zero selection power over those candidates.

A robust uniqueness claim should identify:

1. the candidate class;
2. the admissibility predicate;
3. the derivation/reachability semantics;
4. the terminal/normal criterion, if used;
5. the label or semantic property being selected;
6. a discriminant or theorem excluding alternatives;
7. all additional hypotheses required for uniqueness.

The relation-core counterexample pattern is:

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

The relation suite is standard-library Python and bounded to the declared 530-relation conformance surface in routine CI.

```text
GREEN_CI != PHYSICAL_TRUTH
DETERMINISTIC_RECEIPT != SCIENTIFIC_CONFIRMATION
```

---

# Historical PR8 planning anchors retained for validator compatibility

The following headings describe the older PR8-era plan. They are retained verbatim because the PR8 validator confirms that the historical planning surface was not silently erased. They are **not** the live schedule above.

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

A future formalization release should not be cut until:

- every advertised theorem has an inspectable proof or is explicitly a theorem target;
- machine registries and human statements agree;
- counterexamples remain executable;
- source-specific critiques identify exact sources;
- no private attachment locator leaks into public machine authority;
- proof/runtime/empirical/physical layers remain separated;
- unique-selection claims survive explicit alternate-realization tests;
- CI evidence is retained;
- all deferrals are visible rather than implied complete.

The central discipline remains:

```text
A BEAUTIFUL STRUCTURE CAN BE COMPATIBLE
WITHOUT BEING UNIQUE,
AND A UNIQUE MATHEMATICAL RESULT CAN STILL FAIL
TO SELECT A PHYSICAL ONTOLOGY.
```
