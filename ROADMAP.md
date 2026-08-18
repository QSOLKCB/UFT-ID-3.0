# UFT-ID 3.0 Roadmap

UFT-ID 3.0 is being developed as a **constraint-governed, observer-explicit theory of information dynamics** with reproducible adversarial tests. The project does not begin by assuming that information is a new substance, a universal physical field, or a hidden source of mass. It begins with typed state spaces, explicit information functionals, admissibility, observation, transport, and dynamics.

The goal is not to contradict Melvin Vopson rhetorically. The goal is to reconstruct the strongest published versions of his claims, determine the exact assumptions under which they hold, and test whether broader monotonicity claims survive counterexamples, representation changes, null models, and independent reproduction.

`MATHS.md` is the staging area for mathematical ideas that are not yet frozen definitions or theorem statements. `theory/DEFINITIONS.md` and `theory/THEOREM_TARGETS.md` are authoritative once an idea graduates out of the staging area.

---

## Phase 0 - Bootstrap, lineage, and claim firewall

### Repository contract

- [x] Establish Formal / Diagnostic / Empirical / Interpretive / Speculative authority layers.
- [x] Establish canonical claim classes and require exactly one claim class per nontrivial claim.
- [x] Add explicit non-claims.
- [x] Add adversarial-review rules.
- [x] Defer Lean until the mathematics is frozen.
- [x] Add deterministic experiment and provenance expectations.
- [x] Add cross-domain bridge obligations, including preserved **and lost** structure.

### Research lineage

- [x] Preserve the reusable constraint/admissibility/recovery machinery from UFT-ID 2.x without inheriting all ontology-specific interpretations.
- [ ] Build a complete source registry from Academia, Zenodo, Authorea, Google Drive, GitHub, and archived paper copies.
- [ ] Record DOI, date, version, licence, peer-review status, repository/release relation, and source hash where available.
- [ ] Map every historical UFT-ID symbol to a canonical UFT-ID 3.0 symbol or mark it superseded.
- [ ] Record conflicting historical definitions instead of silently reconciling them.
- [ ] Classify each historical result as formal, computational, empirical, interpretive, or speculative.

### Methodological inheritance worth preserving

- [ ] Import the **canonical-source versus projection** distinction from the substrate work.
- [ ] Import **receiver neutrality** and non-privileged projection discipline from ETQ-303.
- [ ] Import **multi-scale invariant preservation** and deterministic receipts from QEC.
- [ ] Import **dark-state / observer-inaccessible** diagnostics as an observer-relative specialization.
- [ ] Import **calibration-locality** and provenance discipline from RES=RAG / CSNP.
- [ ] Import the **formal theorem != runtime result != physical validation** evidence hierarchy from NEXUS-style formalization.
- [ ] Import explicit machine-readable nonclaim surfaces from later deterministic research packages.

**Exit criterion:** every reused idea has a source, a claim class, and a clear statement of what UFT-ID 3.0 does **not** inherit with it.

---

## Phase 1 - Freeze the typed mathematical core

### Canonical system

Working abstract object:

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

- [ ] Freeze `S`: total state space.
- [ ] Freeze `C`: constraint family.
- [ ] Freeze `A`: admissible subset.
- [ ] Freeze scalar residual `r` and separately typed vector residual `rho`.
- [ ] Freeze scalar and vector tension specializations.
- [ ] Freeze `F`: proposed evolution, with distinct discrete, continuous, and stochastic forms.
- [ ] Freeze `Pi_lex`: deterministic recovery.
- [ ] Freeze `O`: observation/coarse-graining map.
- [ ] Freeze `T`: ambient regime-transport map.
- [ ] Freeze `I`: declared information functional.
- [ ] Freeze recovery events, impulses, thresholds, and constrained evolution.

### Time-model discipline

- [ ] Define continuous-time balance statements only under explicit regularity assumptions.
- [ ] Define discrete finite-difference balance statements independently.
- [ ] Define stochastic balance at the expectation/generator/martingale level as appropriate.
- [ ] Ban notation that silently moves between these three time models.

### Information-measure discipline

For every result, declare which quantity is being used:

- [ ] Shannon entropy.
- [ ] relative entropy / KL divergence.
- [ ] mutual information.
- [ ] von Neumann entropy.
- [ ] observational/coarse-grained entropy.
- [ ] description length / algorithmic proxy.
- [ ] domain-specific information quantity reconstructed from a target paper.

**Exit criterion:** no theorem target contains an untyped symbol or an undefined derivative.

---

## Phase 2 - Information fidelity, observation, and transport

The central research question is not merely "does information go up or down?" It is:

> **What structure survives an admissible transformation, and which apparent losses are caused by dynamics, recovery, transport, coarse-graining, or observation?**

### Transformation fidelity

- [ ] Define a generic structural defect for a declared structural observable.
- [ ] Distinguish state change from invariant change.
- [ ] Distinguish compression from loss of the declared invariant.
- [ ] Define exact-preservation, approximate-preservation, and non-preservation cases.

### Observation layer

- [ ] Define observer-accessible state `O(s)`.
- [ ] Define reconstruction map `R` where meaningful.
- [ ] Define representation/mirror defect `delta_M`.
- [ ] Define accessible and inaccessible components only where the chosen information measure permits it.
- [ ] Characterize `ker(O)` or equivalent observationally dark subspaces where linear structure exists.
- [ ] Do not identify observational inaccessibility with physical destruction.

### Transport layer

- [ ] Define ambient-domain transport `T_ab : D_ab -> S_b`.
- [ ] Define source and target residuals.
- [ ] Define target-admissibility and admissibility preservation.
- [ ] Define structural transport shear using separately named invariant maps.
- [ ] Define a **Bridge Obligation** record for every cross-domain mapping:
  - source object;
  - target object;
  - map;
  - preserved structure;
  - lost structure;
  - observable;
  - evidence class;
  - scope limits.

### Representation robustness

- [ ] Prove bijective relabeling invariance where appropriate.
- [ ] Test partition dependence.
- [ ] Test alphabet dependence.
- [ ] Test reference-measure dependence.
- [ ] Test coarse-graining dependence.
- [ ] Test observation-map dependence.
- [ ] Identify conditions under which `sign(Delta I)` is representation robust.

**Exit criterion:** every monotonicity claim declares its observation, partition, measure, and representation contract.

---

## Phase 3 - Canonical theorem and counterexample surface

### Constraint/recovery theorems

- [ ] Finite lexicographic recovery existence and uniqueness.
- [ ] Recovery admissibility.
- [ ] Residual characterization.
- [ ] Tension reduction under compatible exact recovery.
- [ ] Admissible fixed-point characterization.
- [ ] Minimal cyclic counterexample showing fixed-point assumptions are necessary.

### Information-balance theorems

- [ ] Define exact continuous-time balance conditions.
- [ ] Define exact discrete-time balance conditions.
- [ ] Define stochastic expectation/generator specializations.
- [ ] Derive proposal-versus-recovery information decomposition.
- [ ] Separate information state, information flux, and entropy production.

### Core monotonicity program

- [ ] State a Restricted Infodynamic Monotonicity Theorem with explicit hypotheses.
- [ ] Identify the weakest sufficient hypothesis set found.
- [ ] Construct positive-change examples.
- [ ] Construct zero-change examples.
- [ ] Construct negative-change examples.
- [ ] Construct examples where one monotone functional decreases while Shannon entropy increases.
- [ ] Construct examples where structural fidelity is preserved while description length falls.
- [ ] Construct examples where observation changes the apparent sign without changing underlying dynamics.

### Adversarial theorem discipline

- [x] Give every theorem target an adversarial companion question.
- [ ] For each theorem, record the smallest known failure case when an assumption is removed.
- [ ] Prefer finite exhaustive counterexamples where possible.

**Exit criterion:** the project can exhibit at least one exact, auditable example for every permitted sign regime and every major failure mode.

---

## Phase 4 - Build the Vopson scholarly target corpus

Use Vopson's ORCID `0000-0002-8073-5538` as a bibliographic identity anchor only.

Planned structure:

```text
research/vopson/
  AUTHOR.json
  CORPUS.md
  corpus.json
  CLAIM_GRAPH.md
  CLAIM_GRAPH.json
  DEFINITIONS.md
  REPRODUCTION_MATRIX.md
  COUNTEREXAMPLE_MATRIX.md
  RESPONSE_HISTORY.md
```

### Claim tracks

Treat these as logically separate:

- [ ] mass-energy-information equivalence;
- [ ] genomic information entropy;
- [ ] Second Law of Infodynamics;
- [ ] 2023 cross-domain applications;
- [ ] simulation-hypothesis inference;
- [ ] information-theoretic gravity;
- [ ] polygon symmetry;
- [ ] language diversity;
- [ ] later publications discovered through the author corpus.

### Response history

- [ ] Record published criticisms and replies.
- [ ] Identify objections Vopson has already answered.
- [ ] Avoid presenting an already-addressed objection as new.
- [ ] Treat disagreement over definitions separately from algebraic or empirical failure.

**Exit criterion:** every critique target has an exact source, equation/result identifier, and reproduction status.

---

## Phase 5 - Reproduce Vopson before criticizing

### Locked next implementation: PR #6

**PR #6: Exact mass-energy-information reproduction and Landauer assumption audit**

PR #6 begins only after PR #5 is merged. Its purpose is source-faithful reproduction, not rhetorical refutation.

Required deliverables:

```text
research/vopson/reproduction/2019-mei/SOURCE_MAP.md
research/vopson/reproduction/2019-mei/DERIVATION.md
research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json
research/vopson/reproduction/2019-mei/DIMENSIONAL_AUDIT.md
research/vopson/reproduction/2019-mei/CONTROL_MATRIX.md
research/vopson/reproduction/2019-mei/result.json
experiments/reproduction/vopson_2019_mei/run.py
experiments/reproduction/vopson_2019_mei/fixtures.json
tests/test_vopson_2019_mei.py
```

The source argument must be decomposed into separately typed steps. In particular, PR #6 must not silently identify these statements:

```text
LANDAUER_ERASURE_BOUND:
minimum dissipated heat for logically irreversible erasure >= k_B T ln 2

ADDITIONAL_PHYSICAL_IDENTIFICATION:
intrinsic stored-bit energy = k_B T ln 2

MASS_CONVERSION:
m_bit = E_bit / c^2
```

The arithmetic consequence

```text
m_bit(T) = k_B T ln(2) / c^2
```

must be reproduced numerically from declared physical constants and temperatures, while the physical status of the additional identification is audited independently.

PR #6 must include:

- [ ] exact source/equation/page locators for every reproduced step;
- [ ] a line-by-line derivation map separating established external premises, source definitions, source assumptions, algebraic consequences, interpretive bridges, and empirical claims;
- [ ] deterministic numerical reproduction at `T = 300 K` and a declared temperature sweep;
- [ ] dimensional analysis for every intermediate quantity;
- [ ] an audit of logical information versus ordinary stored energy;
- [ ] an audit of minimum erasure cost versus intrinsic state energy;
- [ ] state-function versus process/path-function distinctions where applicable;
- [ ] matched-energy / different-logical-information control design;
- [ ] matched-logical-information / different-energy control design;
- [ ] exact result and source hashes plus retained CI evidence;
- [ ] explicit nonclaims preventing correct arithmetic from being promoted into validation of intrinsic bit mass.

PR #6 promotion rule:

```text
ARITHMETIC_REPRODUCED
!= PREMISE_VALIDATED
!= PHYSICAL_INTERPRETATION_VALIDATED
!= EXPERIMENTALLY_CONFIRMED
```

Legacy `QSOLKCB/info-mass-gravity` code may be used only as quarantined adversarial lineage for arithmetic comparison and assumption-injection tests. It is not source authority for the 2019 paper.

### 2019 mass-energy-information equivalence

- [ ] Reconstruct the derivation exactly. **Locked to PR #6.**
- [ ] Separate logical information from ordinary stored energy. **Locked to PR #6.**
- [ ] Audit temperature dependence. **Locked to PR #6.**
- [ ] Audit Landauer-related assumptions. **Locked to PR #6.**
- [ ] Audit state-function versus path-function reasoning. **Locked to PR #6.**
- [ ] Reproduce experimental sensitivity estimates.
- [ ] Design matched-energy / different-logical-information comparisons. **Locked to PR #6.**
- [ ] Design matched-logical-information / different-energy comparisons. **Locked to PR #6.**

### 2022 Second Law of Information Dynamics

- [ ] Reproduce every reported example from the published definitions.
- [ ] Reproduce data preprocessing exactly.
- [ ] Reproduce entropy calculations numerically.
- [ ] Record all coding, alphabet, partition, boundary, and window choices.
- [ ] Test reversible/permutation examples.
- [ ] Test open-system examples.
- [ ] Test alternative valid partitions and alphabets.
- [ ] Test whether sign conclusions survive receiver/representation changes.

### 2023 cross-domain extension

- [ ] Reproduce digital examples.
- [ ] Reproduce genetics examples.
- [ ] Reproduce atomic/Hund-rule examples.
- [ ] Reproduce symmetry examples.
- [ ] Reproduce cosmological examples.
- [ ] Write a bridge-obligation record for every domain crossing.
- [ ] Separate support for a measured entropy trend from support for simulation-hypothesis interpretation.

### 2025 gravity

- [ ] Re-derive every equation independently.
- [ ] Run dimensional analysis line by line.
- [ ] Track every geometric counting assumption.
- [ ] Test whether inverse-square structure is genuinely derived or already encoded upstream.
- [ ] Compare with established entropic-gravity derivations without assuming equivalence.
- [ ] Identify any prediction that differs from Newtonian gravity / GR.
- [ ] Test representation dependence of the information variables used in the derivation.

### 2026 and later extensions

- [ ] Reproduce polygon-symmetry entropy calculations.
- [ ] Separate static combinatorial extrema from dynamical laws.
- [ ] Reproduce language-diversity entropy calculations.
- [ ] Compare with ordinary extinction/dominance/population-share models.
- [ ] Require added predictive content beyond the null demographic model.

**Exit criterion:** no public UFT-ID criticism depends on a calculation that has not either been reproduced or documented as unreproducible.

---

## Phase 6 - Deterministic adversarial experiment battery

Build small, inspectable systems first.

### Finite systems

- [ ] deterministic permutations;
- [ ] finite Markov chains;
- [ ] ternary control systems;
- [ ] constrained recovery systems;
- [ ] finite graph dynamics;
- [ ] synchronous versus asynchronous update examples;
- [ ] fixed points and cycles.

### Information sweeps

Measure multiple quantities on the same trajectory:

- [ ] Shannon entropy;
- [ ] relative entropy;
- [ ] mutual information;
- [ ] residual;
- [ ] tension;
- [ ] structural invariant defect;
- [ ] observer defect;
- [ ] transport residual;
- [ ] recovery shear;
- [ ] description length where meaningful.

### Representation sweeps

- [ ] bijective relabelings;
- [ ] partitions;
- [ ] alphabets;
- [ ] coarse-grainings;
- [ ] window sizes;
- [ ] reference measures;
- [ ] observer maps;
- [ ] boundaries.

### Reproducibility

- [ ] canonical JSON inputs;
- [ ] deterministic seeds where randomness exists;
- [ ] source hashes;
- [ ] output hashes;
- [ ] exact environment metadata;
- [ ] replay-safe receipts;
- [ ] negative-result storage;
- [ ] no cherry-picked metric deletion after results are seen.

**Exit criterion:** a third party can regenerate every headline figure/table from source data and a versioned command.

---

## Phase 7 - External theory and empirical cross-check

Use primary literature to position UFT-ID against established results rather than renaming them.

- [ ] Shannon entropy and coding theory.
- [ ] KL divergence and data processing.
- [ ] Markov semigroup entropy contraction.
- [ ] nonequilibrium stochastic thermodynamics.
- [ ] entropy production and boundary flux in open systems.
- [ ] Landauer principle and logical irreversibility.
- [ ] information geometry.
- [ ] transfer entropy and directed information.
- [ ] observational entropy and coarse-graining.
- [ ] algorithmic information / MDL.
- [ ] quantum information and von Neumann entropy.
- [ ] resource theories of thermodynamics/information.
- [ ] fluctuation theorems.
- [ ] constructor-theoretic information.
- [ ] phase-space invariant preservation and symplectic numerics.
- [ ] entropic gravity and critiques.
- [ ] population-diversity entropy models.
- [ ] biological null models for mutation/selection/bottleneck effects.

**Exit criterion:** every claimed novelty is stated relative to the closest established theorem or method.

---

## Phase 8 - Empirical and statistical hardening

- [ ] preregister primary endpoints before large replication runs;
- [ ] use domain-appropriate null models;
- [ ] use held-out data where possible;
- [ ] quantify uncertainty;
- [ ] correct for multiple comparisons;
- [ ] run sensitivity analyses;
- [ ] distinguish exploratory from confirmatory analysis;
- [ ] test inter-rater reliability for diagnostic frameworks;
- [ ] publish negative and null results;
- [ ] invite independent reproduction before strong physical claims.

**Exit criterion:** the strongest empirical conclusions survive preprocessing, representation, and null-model sensitivity tests.

---

## Phase 9 - Paper and adversarial review package

Working title:

**UFT-ID 3.0: Constraint-Governed Information Dynamics, Observation, Transport, and the Limits of Universal Infodynamic Monotonicity**

Planned paper structure:

- [ ] lineage and scope;
- [ ] typed definitions;
- [ ] information fidelity under transformation;
- [ ] information-balance forms;
- [ ] constraint and recovery theorems;
- [ ] observer and transport dependence;
- [ ] representation-invariance results;
- [ ] minimal positive/zero/negative counterexamples;
- [ ] exact Vopson reproduction matrix;
- [ ] restricted monotonicity theorem or revised result if reproduction does not support that framing;
- [ ] gravity/mass/genetics tracks kept logically separate;
- [ ] limitations and nonclaims;
- [ ] deterministic reproducibility appendix.

Before formal verification:

- [ ] hostile internal review;
- [ ] external domain review where possible;
- [ ] notation freeze;
- [ ] theorem-statement freeze;
- [ ] counterexample freeze.

---

## Phase 10 - Lean formal verification

**Deferred until Phase 9 freeze.**

Planned order:

- [ ] finite state space and admissibility predicate;
- [ ] finite candidate sets;
- [ ] total tie-breaking order;
- [ ] lexicographic recovery existence and uniqueness;
- [ ] recovery admissibility;
- [ ] residual lemmas;
- [ ] scalar tension toy model;
- [ ] threshold event semantics;
- [ ] discrete balance identities;
- [ ] restricted monotonicity theorem;
- [ ] explicit finite counterexamples to over-broad monotonicity claims;
- [ ] constrained fixed-point results where tractable;
- [ ] theorem-ID correspondence between paper and Lean;
- [ ] CI theorem inventory.

Lean verifies theorem statements from assumptions. It does not verify that an ontology or physical interpretation is true.

---

## Phase 11 - Release and archival record

- [ ] final source tree;
- [ ] deterministic release manifest;
- [ ] source hashes;
- [ ] bibliography and corpus graph;
- [ ] executable experiment bundle;
- [ ] machine-readable claim/theorem index;
- [ ] paper PDF and source;
- [ ] Lean package when complete;
- [ ] Zenodo archive;
- [ ] release notes separating established results from open conjectures and speculative extensions.

---

## Success condition

UFT-ID 3.0 succeeds even if some preferred conjectures fail.

A scientifically successful outcome is a framework that tells us, with explicit assumptions, **when information increases, decreases, remains invariant, becomes inaccessible, is transported faithfully, is distorted by representation, or is genuinely lost according to a declared information measure**.

If Vopson-style monotonicity survives only inside a restricted class, state that class precisely. If it survives broadly, report that. If it fails under a fair counterexample, publish the counterexample. The result must outrank the desired narrative.
