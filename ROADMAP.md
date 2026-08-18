# UFT-ID 3.0 Roadmap

## Phase 0 - Canonicalize the research lineage

- [x] Establish repository claim-layer discipline.
- [x] Preserve the constraint-first UFT-ID 2.0 core as the main formal inheritance.
- [x] Demote lattice-specific, SU(3), E8, LQG, gravity, cognition, and AGI interpretations to optional specializations unless separately justified.
- [ ] Build a complete bibliography from the Academia, Zenodo, Authorea, Drive, and archived paper corpus.
- [ ] Map every prior UFT-ID symbol to a canonical UFT-ID 3.0 symbol or mark it superseded.
- [ ] Record incompatible historical definitions explicitly rather than silently merging them.
- [ ] Add DOI, license, date, peer-review status, and source hash where available.

## Phase 1 - Freeze the abstract mathematics

- [ ] Finalize the canonical object `U = (S, A, F, Pi_lex, O, T, I, C)`.
- [ ] Define the minimal structure required on `S` for each theorem family.
- [ ] Define admissibility without presupposing a lattice.
- [ ] Define residuals for metric, normed, discrete, and predicate-only state spaces.
- [ ] Define the quadratic tension functional and conditions on its stiffness operator.
- [ ] Define deterministic lexicographic recovery and tie-breaking.
- [ ] Define event/impulse objects.
- [ ] Define observation and coarse-graining maps.
- [ ] Define regime-transport maps.
- [ ] Specify which information functionals are admissible in each theorem.
- [ ] Freeze notation before formal verification begins.

## Phase 2 - Theorem surface

### Constraint core

- [ ] Prove recovery lands in the admissible set under stated assumptions.
- [ ] Prove uniqueness of finite lexicographic recovery.
- [ ] Prove residual zero iff admissible for the selected residual construction.
- [ ] Establish conditions under which thresholded recovery decreases the tension functional.
- [ ] Characterize fixed points of constrained evolution.

### Information balance

- [ ] Derive a general information balance identity with internal production, internal loss, boundary flux, and recovery terms.
- [ ] Separate state entropy from entropy production.
- [ ] Establish a Restricted Infodynamic Monotonicity Theorem giving sufficient conditions for non-increase.
- [ ] Construct valid positive-, zero-, and negative-information-derivative examples.
- [ ] Determine when the sign of `dI/dt` is invariant under admissible coordinate changes.
- [ ] Determine when the sign changes under partition, alphabet, reference measure, or coarse-graining changes.

### Observation and transport

- [ ] Define observer-relative accessible and inaccessible information without implying ontological destruction.
- [ ] Define mirror/representation defect where reconstruction is meaningful.
- [ ] Define transport residual and transport shear.
- [ ] Prove any representation-invariance results that survive exact assumptions.
- [ ] Produce counterexamples where representation changes reverse an apparent monotonicity result.

### Fixed points

- [ ] Characterize admissible fixed points of constrained evolution.
- [ ] Compare finite-state, contraction, Brouwer/Schauder, and order-theoretic conditions.
- [ ] Keep AGI/self-model interpretations outside the core theorem statement.

## Phase 3 - Reproduce Vopson before criticizing

For each paper, reproduce the exact definitions, data transformations, equations, and reported result before adversarial testing.

### 2019 mass-energy-information equivalence

- [ ] Reconstruct the derivation from Landauer cost to proposed bit mass.
- [ ] Separate heat/work accounting from rest-mass accounting.
- [ ] Audit temperature dependence and state-function/path-function assumptions.
- [ ] Reproduce proposed experimental sensitivity estimates.
- [ ] Identify experiments capable of distinguishing stored-energy mass changes from an information-specific mass term.

### 2022 Second Law of Information Dynamics

- [ ] Reproduce all examples and entropy definitions from DOI `10.1063/5.0100358`.
- [ ] Enumerate hidden boundary, coding, and representation assumptions.
- [ ] Test alternative valid partitions and alphabets.
- [ ] Test reversible and open-system counterexamples.
- [ ] Determine whether the law is universal, conditional, encoding-specific, or descriptive.

### 2023 cross-domain infodynamics

- [ ] Reproduce digital-information examples.
- [ ] Reproduce genetic-information examples.
- [ ] Reproduce atomic/Hund-rule examples.
- [ ] Reproduce mathematical symmetry examples.
- [ ] Reproduce cosmological examples.
- [ ] Separate evidence for entropy behavior from evidence for the simulation hypothesis.

### 2025 gravity derivation

- [ ] Re-derive every equation from DOI `10.1063/5.0264945` independently.
- [ ] Run dimensional analysis line by line.
- [ ] Identify assumptions equivalent to Newtonian geometry or force-law structure.
- [ ] Compare with Verlinde-style entropic gravity without assuming either is correct.
- [ ] Test whether alternative information encodings change the resulting force.
- [ ] Check whether the derivation predicts anything not already built into its spatial counting assumptions.

### 2026 extensions

- [ ] Reproduce polygon-symmetry entropy results from DOI `10.3390/e28050564`.
- [ ] Test whether the result is a combinatorial property of the selected descriptor rather than a dynamical law.
- [ ] Reproduce the language-diversity model and entropy decline.
- [ ] Compare against standard category-extinction and population-share dynamics.
- [ ] Test whether entropy decline adds predictive content beyond the demographic model.

## Phase 4 - Adversarial counterexample battery

Build a deterministic suite covering:

- [ ] finite Markov chains with entropy increase;
- [ ] finite Markov chains with entropy decrease;
- [ ] entropy-preserving permutations;
- [ ] reversible Hamiltonian/unitary examples;
- [ ] coarse-graining and data-processing examples;
- [ ] open systems with information inflow/outflow;
- [ ] coding/compression examples where description length falls while physical state entropy does not;
- [ ] mutual-information transfer examples;
- [ ] relative-entropy contraction examples;
- [ ] observational-entropy examples;
- [ ] partition-dependent Shannon entropy examples;
- [ ] relabeling-invariant sanity checks;
- [ ] explicitly constructed UFT-ID constrained-recovery examples.

Every counterexample must state exactly which proposed universal claim it addresses.

## Phase 5 - Empirical and statistical program

- [ ] Preregister primary endpoints before large replication runs.
- [ ] Use null models appropriate to each domain.
- [ ] Use held-out data where available.
- [ ] Quantify uncertainty instead of comparing point estimates alone.
- [ ] Correct for multiple comparisons in cross-domain searches.
- [ ] Run sensitivity analyses over window size, alphabet, partition, smoothing, and preprocessing.
- [ ] Test inter-rater reliability of the Inference Transport Diagnostic Map.
- [ ] Compare diagnostic flags with established robustness, transportability, and uncertainty frameworks.
- [ ] Publish negative results.

## Phase 6 - External theory cross-check

Build literature reviews from primary sources covering:

- [ ] Shannon entropy and coding theory;
- [ ] relative entropy and data-processing inequalities;
- [ ] nonequilibrium stochastic thermodynamics;
- [ ] entropy production in open systems;
- [ ] Landauer principle and logical irreversibility;
- [ ] information geometry;
- [ ] transfer entropy and causal information flow;
- [ ] observational entropy and coarse-graining;
- [ ] algorithmic information and description length;
- [ ] quantum information and von Neumann entropy;
- [ ] resource theories of information/thermodynamics;
- [ ] fluctuation theorems;
- [ ] constructor-theoretic information;
- [ ] entropic gravity and its critiques;
- [ ] symmetry measures independent of Shannon multiplicity encodings;
- [ ] population-diversity entropy models.

## Phase 7 - Formal verification in Lean

**Deferred until Phases 1 and 2 freeze the definitions and theorem statements.**

Planned order:

- [ ] finite state space and admissibility predicate;
- [ ] finite total order for deterministic tie-breaking;
- [ ] lexicographic recovery existence and uniqueness;
- [ ] proof that recovery returns an admissible state;
- [ ] residual and finite distance lemmas;
- [ ] quadratic-tension toy model;
- [ ] threshold event semantics;
- [ ] restricted monotonicity theorem;
- [ ] explicit finite counterexamples to over-broad monotonicity claims;
- [ ] constrained fixed-point results where tractable;
- [ ] machine-checked mapping from paper theorem identifiers to Lean declarations;
- [ ] CI build and theorem inventory.

No physical ontology will be considered machine-verified merely because its abstract mathematics is formalized.

## Phase 8 - Paper package

Target working title:

**UFT-ID 3.0: Constraint-Governed Information Dynamics, Observation, Transport, and the Limits of Universal Infodynamic Monotonicity**

Planned paper structure:

- [ ] lineage and scope;
- [ ] definitions;
- [ ] information-balance framework;
- [ ] formal theorems and counterexamples;
- [ ] observer and transport dependence;
- [ ] Vopson reproduction matrix;
- [ ] empirical replication results;
- [ ] restricted-law result;
- [ ] limitations and non-claims;
- [ ] reproducibility appendix;
- [ ] Lean correspondence appendix after formalization.

## Phase 9 - Release and archival record

- [ ] deterministic release manifest;
- [ ] source hashes;
- [ ] executable experiment bundle;
- [ ] paper PDF and source;
- [ ] machine-readable theorem/claim index;
- [ ] Zenodo archive;
- [ ] release notes that separate established results from open conjectures.
