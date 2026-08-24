# UFT-ID 3.0 Roadmap

UFT-ID 3.0 is a constraint-governed, observer-explicit formalization programme with reproducible adversarial tests.

The first section is the **live schedule authority**. Historical programme text retained later in this file exists for validator/receipt compatibility and does not override the live schedule or `machine/roadmap_state.json`.

```text
COMPACT_SUMMARY != COMPLETE_FORMAL_TYPE_SYSTEM
NO_GIANT_FORMALIZATION_PR
NO_STANDALONE_FINITE_FIXTURE_ZOO
```

The mnemonic remains:

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

but relation, observation, bridge, epistemic, representation, information, recovery, stochastic, and empirical semantics remain separately typed.

---

# Live implementation status

## Completed

### Phase 0: lineage and provenance — COMPLETE

### 2019 MEI reproduction — COMPLETE

- [x] Phase 0 — lineage and provenance.
- [x] PR #5 — cross-repository formal patterns.
- [x] PR #6 — VOP-2019-MEI arithmetic reproduction.
- [x] PR #7 — historical lineage and methodological inheritance.
- [x] PR #8 — invariant calculus, assurance graph, and model obligations.
- [x] PR #9 — deterministic observation calculus, merged at `091405c136fd8dc936e6bd3a544ab22433d04782`.
- [x] PR #11 — relation-first recovery core and graph-realization interlude, merged at `a72dab3170e9880ca8bf120766d8547d6cc0110b`.
- [x] Planned PR #12 — BridgeCore, delivered in GitHub PR #13 and merged at `2242f96564f4d27af4ba641b45f45f011a49a7c7`.
- [x] Planned PR #13 — Epistemic Bridge specialization, delivered in GitHub PR #14 and merged at `083aa9ae9e812cae86302d856f70ad83e5cf806b`.
- [x] Planned PR #14 — Representation and congruence calculus, delivered in GitHub PR #15 and merged at `a094ec469f311bc6cc11442ee5f850f5dc130e2f`.
- [x] Planned PR #15 — Information Comparability core, delivered in GitHub PR #16 and merged at `22b589c4e2e2042d180d64db837f092a007e0813`.

## Deferred independent proof track

- [ ] PR #10 — Lean observation foundation.

```text
MATHEMATICAL_PROOF != LEAN_PROOF
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

## Active now — planned PR #16

### Recovery specializations

**Status:** ACTIVE, implemented by the current change.

Mission: specialize the existing relation-first recovery core with explicit deterministic selectors and executable normalizers without rewriting a generic relation as deterministic, confluent, uniquely normalizing, or empirically valid.

Canonical specialization:

```text
stepRel : X -> X -> Prop
sigma   : X -> X
Sel_sigma(x,y) iff sigma(x)=y and y!=x
```

A selector fixed point is halting semantics for the selector. It is not silently inserted as a self-loop into `stepRel`.

Relation soundness and progress are separate obligations:

```text
sigma(x) != x => stepRel(x, sigma(x))
rho : X -> N
sigma(x) != x => rho(sigma(x)) < rho(x)
```

An executable normalizer is licensed only when non-fixed selector steps are relation-sound, selector fixed points are exactly the base-relation normal states, and the declared natural-number rank strictly decreases on every non-fixed selector step.

Advertised result surface:

1. `UFT-REC-001` every deterministic selector induces a right-unique effective selector relation;
2. `UFT-REC-002` relation-sound finite selector iteration remains inside base-relation reachability;
3. `UFT-REC-003` strict natural-rank descent terminates selector iteration;
4. `UFT-REC-004` sound rank-certified selectors with exact fixed-point/normal correspondence define executable normalizers;
5. `UFT-REC-005` finite lexicographic recovery is unique only with an explicit final total tie-break.

Adversarial counterexamples:

```text
CX-REC-001 existential-normalization-without-executable-choice
CX-REC-002 deterministic-but-relation-unsound-selector
CX-REC-003 relation-sound-deterministic-selector-loop
CX-REC-004 tied-objective-without-total-tiebreak
CX-REC-005 selector-choice-does-not-make-base-relation-confluent
```

Exact finite conformance checks:

```text
32 total selectors on Fin1, Fin2, and Fin3
13,890 selector/relation pairs
4,134 relation-sound selector/relation pairs
739 relation-sound pairs with selector fixed points exactly equal to relation normals
9 natural-index-rank-decreasing selector controls
23 state-level executable-normalization checks
336 finite lexicographic selection checks
```

Required boundaries:

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

**Exit criterion:** the selector remains an explicit specialization of `stepRel`; relation soundness, termination/progress, fixed-point/normal correspondence, and tie-breaking remain separately checkable; the five adversarial counterexamples stay executable; exact finite conformance, human/machine authority, deterministic receipts, retained artifacts, compatibility wrappers, and CI remain synchronized.

## Next planned phases

- [ ] PR #17 — Continuum, stochastic, and prevalence obligations. **NEXT.**
- [ ] PR #18 — Empirical falsification profile.

```text
FINITE_REACHABILITY != INFINITE_PATH_LIVENESS
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
```

---

# Historical post-audit grammar retained for validator compatibility

The block below is a frozen planning-language compatibility surface. Its embedded historical statuses are not current scheduling authority. Current status is the live section above plus `machine/roadmap_state.json`.

# Current formal grammar programme

## PR #9 — Deterministic observation calculus

**Status:** COMPLETE.

This heading remains in the ordered programme because later validators and theorem surfaces depend on its position.

---

## PR #10 — Lean observation foundation

**Status:** DEFERRED as an independent formal-proof track.

```text
MATHLIB_THEOREM_EXISTS != OUR_LEAN_BUILD_PASSES
MATHEMATICAL_PROOF != LEAN_PROOF
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
```

---

## PR #11 — Relation-first recovery core

**Status:** ACTIVE, implemented by the historical PR #11 change.

Historical relation grammar:

```text
stepRel : X -> X -> Prop
A : X -> Prop
```

The generic relation keeps admissibility separate from normality and fixed-point semantics.

```text
NORMAL != ADMISSIBLE != FIXED_POINT
REACHABLE != ADMISSIBLE != NORMAL != UNIQUE_REACHABLE_NORMAL
```

Advertised historical theorem/counterexample anchors include `UFT-SEL-001` and `CX-RW-FORK3`.

The bounded conformance surface enumerates every labelled relation on `Fin 1`, `Fin 2`, and `Fin 3`:

```text
2 + 16 + 512 = 530 relations
FINITE_CONFORMANCE != GENERAL_PROOF
```

Public compatibility context is referenced only through `XR-P17` and `XR-P18`.

```text
PARAMETER != REALIZATION != INVARIANT != DISCRIMINANT != SELECTION
COMPATIBILITY != UNIQUE_SELECTION
GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION
INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION
```

---

## PR #12 — BridgeCore

**Status:** PLANNED in this historical snapshot.

Define typed structural transport with explicit source/target types, domain, map or relation, preserved structure, lost structure, scope, and versions.

---

## PR #13 — Epistemic bridge specialization

**Status:** PLANNED in this historical snapshot.

Treat epistemic authority separately from structural transport. Conflict remains distinct from unknown.

---

## PR #14 — Representation and congruence calculus

**Status:** PLANNED.

Separate similarity, congruence, coordinate change, and receiver transformation.

---

## PR #15 — Information comparability core

**Status:** PLANNED.

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
```

---

## PR #16 — Recovery specializations

**Status:** PLANNED.

```text
GENERIC_RELATION != DETERMINISTIC_SELECTOR
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
```

---

## PR #17 — Continuum, stochastic, and prevalence obligations

**Status:** PLANNED.

```text
FINITE_REACHABILITY != INFINITE_PATH_LIVENESS
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
```

---

## PR #18 — Empirical falsification profile

**Status:** PLANNED.

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
GENIES_REQUIRED_FOR_GENOMIC_BRANCH_ONLY
```

Minimal fixtures travel with the theorem or counterexample that needs them. A fixture must have theorem-conformance, counterexample, assumption-ablation, minimality, or deterministic-receipt purpose.

---

# Selection and uniqueness policy

```text
LABEL -> PARAMETER -> REALIZATION -> INVARIANT -> DISCRIMINANT -> SELECTION THEOREM
```

No arrow is automatic. Compatibility, realization, and one successful construction never suffice for a unique-selection claim.

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
```

```text
GREEN_CI != PHYSICAL_TRUTH
DETERMINISTIC_RECEIPT != SCIENTIFIC_CONFIRMATION
```

---

# Historical PR8 planning anchors retained for validator compatibility

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

# Future model-donor programme — typed causality, projection, and assumption structure

**Status:** ROADMAP-ONLY RESEARCH TARGET / MODEL DONOR. This section is not current graph theorem authority, does not renumber planned PR #12-#18, and does not adopt the source model as UFT-ID ontology.

### Primary model source

> Marco Pettini, *Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in (3,2)-Dimensional Spacetime*, arXiv:2606.12457v2 (2026). DOI `10.48550/arXiv.2606.12457`.

```text
ANSATZ_UNIQUENESS != GLOBAL_UNIQUENESS
MODEL_CLASS_EXHAUSTION != PHYSICAL_SELECTION
G_L = (V, L, I)
CORRELATION_EDGE != CAUSAL_RESPONSE_EDGE
NONZERO_CORRELATION != CONTROLLABLE_INFLUENCE
FORGET_EDGE_TYPE = POTENTIAL_INFORMATION_LOSS
MICROSTATE != PROJECTION != CONTEXT_LABEL
MANY_TO_ONE_CONTEXT_MAP != PHYSICAL_IDENTITY
CONDITIONAL_DETERMINISM != ENSEMBLE_DETERMINISM
EQUIVARIANCE_ASSUMED != EQUIVARIANCE_DERIVED
WKB_CHARACTERISTIC != EXACT_PROPAGATOR
DERIVED != ASSUMED != CONDITIONALLY_PREDICTED != EMPIRICALLY_OBSERVED
MAP_NONUNIQUENESS != OBSERVABLE_NONROBUSTNESS
PREPRINT_PREDICTION != EXPERIMENTAL_RESULT
FALSIFIABLE != VERIFIED
(3,2)_SPACETIME_MODEL != UFT_ID_ONTOLOGY
BULK_FIELD_XA_MODEL != ESTABLISHED_PHYSICAL_FIELD
PREDICTED_CROSS_PAIR_SIGNAL != OBSERVED_CROSS_PAIR_SIGNAL
PAPER_MODEL != UFT_ID_PHYSICAL_ONTOLOGY
```

# Future physiology and connectomics positive-control programme — typed transduction, feedback, hidden state, alternate mechanisms, and structure/function boundaries

**Status:** ROADMAP-ONLY POSITIVE-CONTROL / MODEL-DONOR PROGRAMME. It does not renumber PR #12-#18 and does not make physiology, virology, or neuroscience UFT-ID ontology.

**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence in this section until a later explicit BridgeCore record supplies source type, target type, source/target dynamics, preserved structure, lost structure, scope, and measurement/observation bridge. External source facts retain their own evidentiary status; the mapping into UFT-ID is not promoted above `INTERPRETIVE` here.

| Donor mapping | Claim class |
| --- | --- |
| A. Wheatstone pressure transducer -> typed transduction / identifiability | `INTERPRETIVE` |
| B. Haemoglobin oxygen curve -> context-dependent calibration | `INTERPRETIVE` |
| C. Arterial baroreflex -> closed-loop identification | `INTERPRETIVE` |
| D. Windkessel -> reduced-model boundary | `INTERPRETIVE` |
| E. Hodgkin-Huxley -> hidden-state observation fibre | `INTERPRETIVE` |
| F. Fick principle -> conservation-based inference | `INTERPRETIVE` |
| G. HPV16 -> host-context / alternate-mechanism mapping | `INTERPRETIVE` |
| H. FlyWire -> weighted/versioned structure-function mapping | `INTERPRETIVE` |

```text
SHARED_FORMAL_PATTERN != SHARED_PHYSICAL_MECHANISM
INTERPRETIVE_MAPPING != BRIDGE_THEOREM
Delta_B = R1*Rx - R2*R3
CLOSED_LOOP_OBSERVATION != OPEN_LOOP_IDENTIFICATION
LUMPED_MODEL != DISTRIBUTED_SYSTEM
SAME_VOLTAGE != SAME_HIDDEN_STATE
INFERENCE_FORMULA != DIRECT_MEASUREMENT
GENOME_IDENTITY != EXPRESSION_STATE
CONNECTOME != EFFECTOME
THRESHOLDED_GRAPH != ORIGINAL_WEIGHTED_GRAPH
DATASET_VERSION != INCIDENTAL_METADATA
```

### A. Wheatstone pressure transducer — typed K4, balance residual, transduction, and identifiability

Educational/clinical engineering source:

- Deranged Physiology, *Wheatstone bridge pressure transducer*: https://derangedphysiology.com/main/required-reading/intensive-care-procedures/Chapter-216/wheatstone-bridge-pressure-transducer

### B. Haemoglobin oxygen-dissociation curve — context-dependent calibration

Public source:

- *Relating oxygen partial pressure, saturation and content: the haemoglobin–oxygen dissociation curve*, PMCID `PMC4666443`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4666443/

### C. Arterial baroreflex — closed-loop observation versus open-loop identification

Public source:

- *Systems physiology of the baroreflex during orthostatic stress: from animals to humans*, PMCID `PMC4086024`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4086024/

### D. Arterial Windkessel — useful reduced model versus distributed realization

Canonical review source:

- Westerhof, N., Lankhaar, J.-W., Westerhof, B.E. *The arterial Windkessel.* Med Biol Eng Comput 47, 131-141 (2009). DOI `10.1007/s11517-008-0359-2`.

### E. Hodgkin-Huxley — hidden state and observation fibres

Primary mathematical-physiology source:

- Hodgkin, A.L. & Huxley, A.F. *A quantitative description of membrane current and its application to conduction and excitation in nerve.* J Physiol 117, 500-544 (1952). DOI `10.1113/jphysiol.1952.sp004764`.

### F. Fick cardiac-output principle — conservation-based inference and assumption sensitivity

Public methodological source:

- *Methods in pharmacology: measurement of cardiac output*, PMCID `PMC3045542`: https://pmc.ncbi.nlm.nih.gov/articles/PMC3045542/

### G. HPV16 — host-context dependence and alternate routes to similar downstream classes

Public sources:

- *Manipulation of Epithelial Differentiation by HPV Oncoproteins*, PMCID `PMC6549445`: https://pmc.ncbi.nlm.nih.gov/articles/PMC6549445/
- *IGF axis and other factors in HPV-related and HPV-unrelated carcinogenesis*, PMCID `PMC4240475`: https://pmc.ncbi.nlm.nih.gov/articles/PMC4240475/

### H. FlyWire adult Drosophila connectome — weighted directed structure, threshold projection, SCCs, versioning, and structure/function separation

Primary/companion sources:

- Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature 634, 124-138 (2024). DOI `10.1038/s41586-024-07558-y`.
- Shiu, P.K. et al. *Network statistics of the whole-brain connectome of Drosophila.* Nature 634 (2024). DOI `10.1038/s41586-024-07968-y`.

# Future fivefold assembly and rooted-representation donor programme — cardinality, asymmetry, interfaces, and coordinate charts

**Status:** ROADMAP-ONLY MODEL-DONOR PROGRAMME. This section does not renumber PR #12-#18 and does not infer a universal significance for the number five.

**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence below. The empirical IgM findings remain external empirical evidence; the musical facts remain background/source facts; the UFT-ID abstractions are interpretive until explicit BridgeCore objects and independent mathematical fixtures are supplied.

```text
10.1126/sciadv.aau1199
https://en.wikipedia.org/wiki/Pentatonic_scale
CARDINALITY_5 != FIVEFOLD_SYMMETRY
PENTAMER != REGULAR_PENTAGON != C5
NONEDGE != INTERFACE
AVAILABLE_COMPONENTS + CARDINALITY != UNIQUE_ASSEMBLY
PENTAMER != PENTATONIC_SCALE
PROJECTION != INVERSION
UNROOTED_SET_IDENTITY != ROOTED_STRUCTURE_IDENTITY
CHART != OBJECT
ABSENT != UNKNOWN
SHARED_CARDINALITY != SHARED_PHYSICAL_MECHANISM
```

# Future 3-4-5 finite numerosity and semantic-lifting stress programme

**Status:** ROADMAP-ONLY MODEL-DONOR / ADVERSARIAL PROGRAMME. It does not renumber PR #12-#18, does not claim that 3, 4, or 5 are physically privileged, and does not infer a common mechanism from repeated cardinalities.

**Claim class:** `INTERPRETIVE` for every source-to-UFT-ID correspondence in this section until explicit BridgeCore objects and independent mathematical fixtures exist.

```text
NumberSpec = (n, role, carrier, structure, semantics, scope)
NUMBER != ROLE
CARDINALITY_3 != ARITY_3 != DIMENSION_3 != RADIX_3
FIN3 != C3 != TRIANGLE != QUTRIT
FINITE_ITERATION != LIMIT_OBJECT
TETRAHEDRAL_HEURISTIC != GEOMETRIC_TETRAHEDRON
FIXED_TOTAL_INTERVAL != UNIQUE_INTERVAL_DECOMPOSITION
MUSICAL_GENUS != TOPOLOGICAL_GENUS
TETRABENAZINE != TETRACYCLIC_ANTIDEPRESSANT
CARDINALITY_5 != FIVEFOLD_SYMMETRY
3^2 + 4^2 = 5^2
ARITHMETIC_RELATION != STRUCTURAL_BRIDGE
NUMERIC_RELATION + LABEL_ASSIGNMENT != STRUCTURAL_THEOREM
NO_SEMANTIC_LIFTING_WITHOUT_A_BRIDGE
NUMBER != ROLE != STRUCTURE != MECHANISM != ONTOLOGY
```

---

# Release-level exit criteria

A future formalization release should not be cut until every advertised theorem has an inspectable proof or is explicitly a theorem target; machine and human statements agree; counterexamples remain executable; source-specific critiques identify exact sources; private locators do not leak; proof/runtime/empirical/physical layers stay separate; unique-selection claims survive alternate-realization tests; CI evidence is retained; and all deferrals remain visible.
