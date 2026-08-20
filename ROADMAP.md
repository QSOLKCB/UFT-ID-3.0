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

# Future positive-control programme — history-dependent topological metastability

**Status:** ROADMAP-ONLY RESEARCH TARGET. Not part of the current PR #11 theorem authority and not a renumbering of the PR #9-#18 schedule.

### Primary empirical source

Canonical citation:

> Xin, F., Gelkop, Y., van der Veer, E. et al. *Spontaneous formation and optical manipulation of a woven domain fabric in a ferroelectric crystal.* Light: Science & Applications **15**, 315 (2026). DOI `10.1038/s41377-026-02374-7`. Published/version of record: 2026-07-14.

The paper is treated as a **primary empirical source** for an observed history-dependent woven ferroelectric domain system with topological descriptors, metastability, thermal-history dependence, and optical manipulation. It is not a theorem premise for the current relation calculus.

Public commentary provenance:

```text
Sabine Hossenfelder video:
https://www.youtube.com/watch?v=NzQQXQK_Ngk
```

Her public commentary, including the stated `0/10` bullshit-meter assessment, is a commentary/calibration datum only. It is not scientific evidence and does not alter the paper's evidentiary status.

```text
PAPER_EVIDENCE != COMMENTARY != UFT_ID_DERIVED_RESULT
PRIMARY_SOURCE != EXTERNAL_RATING
```

### Abstract donor pattern

Study a history-dependent topological-metastability structure with typed components such as:

```text
X          realizable state carrier
stepRel    transition/intervention relation
H          preparation / thermal / intervention history
E : X -> R energy-like or objective functional when physically justified
tau : X -> T structural/topological descriptor
```

The ferroelectric domain ontology is not inherited. The reusable target is the abstract separation between state, history, stability, energy ordering, topology/structure, and intervention.

### Candidate boundaries

```text
STABLE != GLOBAL_MINIMUM
METASTABLE != UNIQUE
SAME_MACRO_CONDITIONS != SAME_REALIZATION
ENERGY_DESCENT != TOPOLOGY_PRESERVATION
RESTORED_STATE_CLASS != RESTORED_ORIGINAL_STATE
TOPOLOGICAL_PROTECTION != IMMUTABILITY
HIGH_CONFIDENCE_IN_OBSERVATION != HIGH_CONFIDENCE_IN_EXTRAPOLATION
FERROELECTRIC_RESULT != COSMOLOGICAL_VALIDATION
```

### Candidate theorem / counterexample target

Introduce only after an independent mathematical fixture is supplied:

```text
E(y) < E(x)
DOES NOT GENERALLY IMPLY
tau(y) = tau(x)
```

The theorem or counterexample must stand on UFT-ID's own mathematics. Xin et al. may motivate the question and later serve as an empirical positive control, but the experiment must not be used as proof of the general statement.

### Recovery and history target

Model recovery of a state **class** separately from recovery of the original realization. A future finite fixture should permit:

```text
Woven(W1)
Woven(W2)
W1 != W2
```

with a history-dependent transition such as:

```text
W1 -> disentangled -> W2
```

This motivates:

```text
RECOVERY_OF_MACROCLASS != RECOVERY_OF_ORIGINAL_STATE
CURRENT_STATE != STATE_PLUS_PREPARATION_HISTORY
```

and, only after the history semantics are defined, a possible augmented carrier:

```text
X_hat = X x H
```

This belongs naturally with the later trace/history, nonergodicity, stochastic, and empirical-bridge work rather than the current finite relation core.

### Positive-control role

Use the paper as a future **positive topology control** for evidentiary architecture: observable 3D crossing structure, explicit structural/topological descriptors, history-dependent reproducibility, and controlled physical intervention are qualitatively different from merely assigning a topology label or parameter in code.

```text
TOPOLOGICAL_TERMINOLOGY != TOPOLOGICAL_EVIDENCE
OBSERVED_STRUCTURE != NOMINAL_PARAMETER
CONTROLLED_INTERVENTION != UNIQUE_SELECTION
```

This positive control must not be promoted into genus, E8, quantum-field, cosmological, or universal-ontology claims. Any broader extrapolation requires its own bridge and evidence.

### Future acceptance gate

A later implementation slice may promote this roadmap target only if it supplies:

- exact source provenance and claim-class separation;
- an independent finite mathematical counterexample for energy descent versus structural preservation;
- an explicit history model if history is theorem-relevant;
- a clear definition of state identity versus macroclass identity;
- a typed topological/structural descriptor rather than topology-themed prose;
- a formal-to-empirical bridge that distinguishes paper observations from UFT-ID abstraction;
- explicit nonclaims blocking transfer from ferroelectric materials to cosmology or fundamental physics.

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
python scripts/validate_graph_realization.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/relation/run.py --json
python experiments/run_pr11.py --json
python experiments/graph_realization/run.py --json
python experiments/run_graph_realization.py --json
```

The relation suite and graph-realization suite are standard-library Python. Routine graph conformance is bounded to the declared 530 labelled relations on `Fin1`, `Fin2`, and `Fin3`.

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

---

# Future model-donor programme — typed causality, projection, and assumption structure

**Status:** ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR. This section is not current graph theorem authority, does not renumber planned PR #12-#18, and does not adopt the source model as UFT-ID ontology.

### Primary model source

> Marco Pettini, *Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in (3,2)-Dimensional Spacetime*, arXiv:2606.12457v2 (2026). DOI `10.48550/arXiv.2606.12457`.

The source is treated as a **model donor** for formal distinctions that can be abstracted independently. Its `(3,2)` spacetime, bulk field, Bohm-Bub collapse realization, and proposed cross-pair signal are not inherited as established physical facts or UFT-ID premises.

```text
PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY
(3,2)_SPACETIME_MODEL != UFT_ID_ONTOLOGY
BULK_FIELD_XA_MODEL != ESTABLISHED_PHYSICAL_FIELD
MODEL_CAUSALITY_CONTRACT != EMPIRICAL_VALIDATION
BORN_RULE_COMPATIBILITY != MICROSCOPIC_DERIVATION
PREDICTED_CROSS_PAIR_SIGNAL != OBSERVED_CROSS_PAIR_SIGNAL
```

### A. Ansatz-bounded uniqueness

The paper explicitly distinguishes fixation of a structure inside a declared ansatz from unrestricted uniqueness. UFT-ID should turn that distinction into a generic future theorem/counterexample target.

For a declared model class `A subset U`, proving

```text
exists unique x in A such that P(x)
```

does not establish

```text
exists unique x in U such that P(x)
```

without a completeness/exhaustion bridge showing that every relevant candidate lies in `A`.

```text
ANSATZ_UNIQUENESS != GLOBAL_UNIQUENESS
MODEL_CLASS_EXHAUSTION != PHYSICAL_SELECTION
```

### B. Typed multi-relation incidence

Stage a future labelled relation object:

```text
G_L = (V, L, I)
I subseteq V x L x V
```

where relation labels can distinguish, for example:

```text
response
correlation
coupling
placement
edge-share
corner-share
```

A future synthetic fixture should permit two events `A,B` with a correlation-labelled edge while no causal-response edge exists between them. The fixture must remain abstract and must not use the Pettini model as proof of a general causal theorem.

```text
CORRELATION_EDGE != CAUSAL_RESPONSE_EDGE
NONZERO_CORRELATION != CONTROLLABLE_INFLUENCE
FORGET_EDGE_TYPE = POTENTIAL_INFORMATION_LOSS
```

This extends the typed-incidence discipline already motivated independently by SiS2 (`edge-share` versus `corner-share`) and ETQ/SPECTRAL (`coupling` versus `placement`). Shared typing structure does not imply shared physical mechanism.

### C. Lossy projection and context compression

Stage an abstract projection chain:

```text
X_bulk -> X_brane -> lambda
```

where the final context label may be many-to-one. The reusable formal question is how preserved/lost structure propagates through a chain of projections, not whether UFT-ID contains a physical bulk field.

```text
MICROSTATE != PROJECTION != CONTEXT_LABEL
MANY_TO_ONE_CONTEXT_MAP != PHYSICAL_IDENTITY
COARSE_GRAINED_SUFFICIENCY != EXACT_RECONSTRUCTION
```

This belongs naturally in BridgeCore and the existing observation/reconstruction calculus.

### D. Conditional determinism versus ensemble statistics

Stage a future distinction between deterministic evolution conditional on a declared contextual microstate and probabilistic statistics obtained only after averaging over a distribution of such microstates.

```text
CONDITIONAL_DETERMINISM != ENSEMBLE_DETERMINISM
DETERMINISTIC_MICRODYNAMICS != DETERMINISTIC_OBSERVED_STATISTICS
EQUIVARIANCE_ASSUMED != EQUIVARIANCE_DERIVED
STATIONARY_DISTRIBUTION_EXISTS != GENERIC_RELAXATION_PROVED
```

No Born-rule derivation may be claimed merely because an equivariant distribution has been selected or an explicit stationary family has been constructed.

### E. Approximation versus exact-object boundary

Use the paper's separation between geometric-optics characteristics and exact spectral/mode-sum propagation as a future representation/approximation audit pattern.

```text
WKB_CHARACTERISTIC != EXACT_PROPAGATOR
SINGLE_RAY_PROPERTY != FULL_FIELD_PROPERTY
GEOMETRIC_OPTICS != EXACT_SPECTRAL_DYNAMICS
```

A property of one approximation, ray, representation, or asymptotic sector must not be promoted automatically to the exact object.

### F. Assumption graph and assurance staging

Build a future machine-readable dependency surface that distinguishes source-derived statements, explicit modelling assumptions, conditional predictions, and empirical observations.

```text
DERIVED != ASSUMED != CONDITIONALLY_PREDICTED != EMPIRICALLY_OBSERVED
```

For this donor source, the future audit should keep geometry-derived claims separate from H1-H3, equivariance, preparation-source assumptions, detector/readout assumptions, correlator ansatz choices, and unresolved stability/genericity questions. The source's own categorization motivates the schema; UFT-ID must verify any imported proposition independently before promoting it.

### G. Representation-map robustness

Stage an admissible map class `F_class` and allow a declared observable `Q` to be tested for invariance across that class:

```text
for all F1,F2 in F_class:
Q(F1) = Q(F2)
```

without requiring `F1 = F2`.

```text
MAP_NONUNIQUENESS != OBSERVABLE_NONROBUSTNESS
ROBUST_WITHIN_DECLARED_MAP_CLASS != UNQUALIFIED_REPRESENTATION_INDEPENDENCE
```

This should feed the planned representation/congruence calculus, where every robustness claim names the transformation/map class over which it is quantified.

### H. Future falsification-profile specimen

Record the paper's proposed source prediction

```text
C_AE ~ (ell/d)^2
```

only as a **preprint model prediction** suitable for future `FalsificationSpec` anatomy. A future source-specific profile may record the controlled geometry, predicted distance dependence, standard-model/null comparator, required observables, conventional-cross-talk controls, uncertainty, and rejection conditions.

```text
PREPRINT_PREDICTION != EXPERIMENTAL_RESULT
FALSIFIABLE != VERIFIED
MODEL_DISTINGUISHES_STANDARD_QM != MODEL_IS_CORRECT
```

No repository claim may state or imply that the cross-pair signal has been observed unless independent experimental evidence is added and classified separately.

### Integration targets

This donor programme may strengthen later work in:

```text
PR #12 BridgeCore
PR #14 representation and congruence calculus
formal assurance / assumption graphs
typed multi-relation incidence
PR #18 empirical falsification profiles
```

It is explicitly not evidence for:

```text
E8 physical ontology
ETQ physical ontology
Fuller/Synergetics physical selection
extra-time reality
cosmological topology
```

### Acceptance gate

A later implementation slice may promote any Pettini-inspired abstraction only if it supplies:

- exact source identity and claim-class separation;
- an independent UFT-ID mathematical definition or fixture;
- preserved and lost structure for every projection/bridge;
- explicit relation labels when multiple edge semantics coexist;
- explicit assumption versus derivation dependencies;
- a declared map class for robustness claims;
- a source-prediction versus observed-result separation;
- mutation tests blocking ontology promotion;
- deterministic receipts for any executable authority;
- explicit confirmation that `PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY`.

---

# Future physiology and connectomics positive-control programme — typed transduction, feedback, hidden state, alternate mechanisms, and structure/function boundaries

**Status:** ROADMAP-ONLY POSITIVE-CONTROL / MODEL-DONOR PROGRAMME. It does not renumber PR #12-#18 and does not make physiology, virology, or neuroscience UFT-ID ontology.

### Mission

Use independently established physiological, biomedical, and connectomic systems as deliberately heterogeneous donor cases for the formal distinctions already emerging in UFT-ID. Similar mathematical structure across donors is evidence that an abstraction is reusable, not evidence that the donors share one physical mechanism.

```text
SHARED_FORMAL_PATTERN != SHARED_PHYSICAL_MECHANISM
PHYSIOLOGY_POSITIVE_CONTROL != UFT_ID_ONTOLOGY
BIOLOGICAL_NETWORK != FUNDAMENTAL_INFORMATION_NETWORK
```

### A. Wheatstone pressure transducer — typed K4, balance residual, transduction, and identifiability

Educational/clinical engineering source:

- Deranged Physiology, *Wheatstone bridge pressure transducer*: https://derangedphysiology.com/main/required-reading/intensive-care-procedures/Chapter-216/wheatstone-bridge-pressure-transducer

Treat the four bridge junctions as an abstract graph only after edge semantics are declared. Including the four resistive arms, detector diagonal, and excitation diagonal gives an untyped `K4`, but the typed circuit is not a tetrahedron and does not inherit geometric meaning from the isomorphism.

For the balanced bridge relation, stage the residual:

```text
Delta_B = R1*Rx - R2*R3
BALANCED iff Delta_B = 0
```

and the typed transduction chain:

```text
physical pressure
-> strain-gauge state Rx
-> bridge imbalance Delta_B
-> electrical output
-> calibrated pressure estimate
```

Candidate boundaries:

```text
UNTYPED_K4 != TYPED_WHEATSTONE_BRIDGE
SAME_K4 != SAME_SEMANTICS
ZERO_OBSERVABLE != ZERO_INTERNAL_STATE
BALANCE_CONSTRAINT != UNIQUE_REALIZATION
CONSTRAINT + KNOWN_CONTEXT MAY ENABLE IDENTIFIABILITY
TRANSDUCTION != IDENTITY
RAW_SIGNAL != CALIBRATED_QUANTITY
```

### B. Haemoglobin oxygen-dissociation curve — context-dependent calibration

Public source:

- *Relating oxygen partial pressure, saturation and content: the haemoglobin–oxygen dissociation curve*, PMCID `PMC4666443`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4666443/

Stage a context-indexed map rather than a context-free lookup:

```text
S_O2 = F(P_O2 ; pH, P_CO2, temperature, 2,3-BPG, ...)
```

The reusable target is calibration/context dependence, not respiratory ontology.

```text
SAME_P_O2 != SAME_SATURATION_UNDER_CHANGED_CONTEXT
MEASUREMENT != CONTEXT_FREE_STATE
CALIBRATION_PROFILE_IS_PART_OF_INTERPRETATION
```

### C. Arterial baroreflex — closed-loop observation versus open-loop identification

Public source:

- *Systems physiology of the baroreflex during orthostatic stress: from animals to humans*, PMCID `PMC4086024`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4086024/

Use the baroreflex as a control-systems donor where arterial pressure affects the controller and the controller feeds back into arterial pressure. The formal target is that causal transfer characteristics inferred under an opened loop are not automatically recoverable from ordinary closed-loop correlation.

```text
CLOSED_LOOP_OBSERVATION != OPEN_LOOP_IDENTIFICATION
FEEDBACK_EDGE != FEEDFORWARD_EDGE
CORRELATION_IN_LOOP != FORWARD_CAUSAL_GAIN
```

### D. Arterial Windkessel — useful reduced model versus distributed realization

Canonical review source:

- Westerhof, N., Lankhaar, J.-W., Westerhof, B.E. *The arterial Windkessel.* Med Biol Eng Comput 47, 131-141 (2009). DOI `10.1007/s11517-008-0359-2`.

Use the Windkessel as a positive control for a lumped model that captures declared global behaviour while omitting spatially distributed wave phenomena.

```text
LUMPED_MODEL != DISTRIBUTED_SYSTEM
MODEL_SUFFICIENCY_FOR_Q != STRUCTURAL_IDENTITY
PREDICTS_DECLARED_OBSERVABLE != COMPLETE_MECHANISM
```

### E. Hodgkin-Huxley — hidden state and observation fibres

Primary mathematical-physiology source:

- Hodgkin, A.L. & Huxley, A.F. *A quantitative description of membrane current and its application to conduction and excitation in nerve.* J Physiol 117, 500-544 (1952). DOI `10.1113/jphysiol.1952.sp004764`.

Use the classical state shape:

```text
x = (V, m, h, n)
O(x) = V
```

as a positive control for hidden-state ambiguity. Equal observed membrane potential need not identify equal gating state.

```text
SAME_VOLTAGE != SAME_HIDDEN_STATE
OBSERVATION_FIBRE != PHYSICAL_IDENTITY
MODEL_STATE != SINGLE_OBSERVABLE
```

### F. Fick cardiac-output principle — conservation-based inference and assumption sensitivity

Public methodological source:

- *Methods in pharmacology: measurement of cardiac output*, PMCID `PMC3045542`: https://pmc.ncbi.nlm.nih.gov/articles/PMC3045542/

Stage the inference:

```text
CO = V_O2 / (C_aO2 - C_vO2)
```

as a donor for balance-law identification when the required measurements and assumptions are supplied.

```text
INFERENCE_FORMULA != DIRECT_MEASUREMENT
BALANCE_LAW + MEASURED_CONTEXT MAY IDENTIFY UNKNOWN
FORMULA_VALIDITY != INPUT_ACCURACY
```

### G. HPV16 — host-context dependence and alternate routes to similar downstream classes

Public sources:

- *Manipulation of Epithelial Differentiation by HPV Oncoproteins*, PMCID `PMC6549445`: https://pmc.ncbi.nlm.nih.gov/articles/PMC6549445/
- *IGF axis and other factors in HPV-related and HPV-unrelated carcinogenesis*, PMCID `PMC4240475`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4240475/

Use HPV16 only as a bounded donor for typed molecular interactions, dependence of viral expression/replication on host epithelial state, and the existence of routes that do not require a single canonical integration mechanism.

A future abstraction may use:

```text
X_hat = X_virus x X_host x H_differentiation
```

and a typed relation vocabulary such as:

```text
binds
degrades
activates
represses
requires
maintains
```

Candidate boundaries:

```text
GENOME_IDENTITY != EXPRESSION_STATE
EXPRESSION_STATE != CELL_STATE != TISSUE_CONTEXT
ONE_SUFFICIENT_PATHWAY != NECESSARY_PATHWAY
SAME_DOWNSTREAM_CLASS != UNIQUE_UPSTREAM_MECHANISM
UNTYPED_BIOLOGICAL_EDGE != MECHANISTIC_EQUIVALENCE
```

No viral or cancer mechanism is promoted into a UFT-ID universal mechanism.

### H. FlyWire adult Drosophila connectome — weighted directed structure, threshold projection, SCCs, versioning, and structure/function separation

Primary/companion sources:

- Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature 634, 124-138 (2024). DOI `10.1038/s41586-024-07558-y`.
- Shiu, P.K. et al. *Network statistics of the whole-brain connectome of Drosophila.* Nature 634 (2024). DOI `10.1038/s41586-024-07968-y`.

Stage the connectome as a versioned directed weighted graph:

```text
G = (V, E, w, lambda, dataset_version)
```

where edge existence, synapse-count weight, cell-type labels, confidence/threshold rules, and dataset release are distinct fields. A thresholded projection must retain its threshold in provenance.

```text
CONNECTOME != EFFECTOME
CHEMICAL_SYNAPSE_GRAPH != COMPLETE_NEURAL_DYNAMICS
ANATOMICAL_EDGE != FUNCTIONAL_CAUSATION
EDGE_EXISTS != EDGE_WEIGHT != EDGE_TYPE
THRESHOLDED_GRAPH != ORIGINAL_WEIGHTED_GRAPH
SCC_MEMBERSHIP != FUNCTIONAL_EQUIVALENCE
CELL_TYPE != GRAPH_POSITION
DATASET_VERSION != INCIDENTAL_METADATA
STRUCTURAL_CONNECTIVITY != FUNCTIONAL_DYNAMICS != BEHAVIOUR
```

The FlyWire SCC and threshold machinery may later serve as a real-data positive control for graph algorithms, but no empirical connectome statistic may be promoted into a general theorem.

### Cross-donor formal targets

These heterogeneous cases motivate future theorem/counterexample and BridgeCore targets such as:

```text
SAME_ABSTRACT_GRAPH != SAME_SEMANTICS
ZERO_OBSERVABLE != ZERO_STATE
CONSTRAINT_SATISFACTION != UNIQUE_IDENTIFICATION
CLOSED_LOOP_OBSERVATION != OPEN_LOOP_CAUSAL_IDENTIFICATION
REDUCED_MODEL_FIT != STRUCTURAL_IDENTITY
SAME_OBSERVABLE != SAME_HIDDEN_STATE
SAME_ENDPOINT != UNIQUE_MECHANISM
CONNECTIVITY != FUNCTION
THRESHOLD_PROJECTION != ORIGINAL_GRAPH
SOURCE_VERSION != INCIDENTAL_METADATA
```

Potential finite fixtures should be synthetic and minimal. The physiological or biological sources motivate the formal question and later provide positive controls; they are not proofs of the abstract theorem.

### Integration targets

This donor programme should feed later work rather than expand current PR #11 theorem authority:

```text
PR #12 BridgeCore
PR #14 representation and congruence calculus
PR #16 recovery specializations / identifiability
formal assurance and assumption graphs
PR #18 empirical falsification profiles
```

### Acceptance gate

A later implementation slice may promote a physiology/connectomics abstraction only if it supplies:

- exact public source identity and source class;
- a typed map/relation with explicit domain and codomain;
- explicit preserved and lost structure for projections;
- calibration/context variables where interpretation depends on them;
- version and threshold provenance for data-derived graphs;
- independent synthetic theorem or counterexample evidence;
- a declared distinction between measured, inferred, modelled, and latent state;
- mutation tests against mechanism/ontology promotion;
- empirical-positive-control status kept separate from abstract mathematical proof;
- explicit confirmation that `SHARED_FORMAL_PATTERN != SHARED_PHYSICAL_MECHANISM`.
