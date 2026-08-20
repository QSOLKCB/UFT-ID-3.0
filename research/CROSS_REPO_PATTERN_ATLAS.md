# Cross-Repository Formal Pattern Atlas

**Claim class:** `DIAGNOSTIC`

This document records reusable mathematical and methodological patterns mined from public, inspectable QSOLKCB repositories. It is deliberately **not** a claim that software architecture proves physics.

The machine authority for this atlas is [`machine/cross_repo_patterns.json`](../machine/cross_repo_patterns.json).

## Governing rule

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

A repository may supply a clean finite example, typed distinction, deterministic receipt pattern, calibration rule, or adversarial counterexample without lending its application-domain ontology to UFT-ID.

This atlas therefore imports **structure**, not mythology.

## Why this strengthens UFT-ID

UFT-ID 3.0 already contains abstract slots for state, admissibility, dynamics, recovery, observation, transport, information, and constraints. The weakness of an abstract framework is that nearly anything can be placed into those slots.

The QSOL repository family provides a useful adversarial testbed because independently developed systems repeatedly discovered the same boundaries:

```text
source != projection
projection != receiver
receiver != source
routing != resolution
resolution != transport
transport != authority
storage != truth
hash integrity != semantic truth
recovery != epistemic promotion
consensus != evidence
telemetry != governance
formal proof != implementation conformance
implementation conformance != empirical validation
observation convention != physical time
semantic coincidence != causal evidence
local calibration != universal constant
compatibility != unique selection
placement geometry != topology derivation
```

Those recurrences are not evidence of a new physical law. They are evidence that UFT-ID's type boundaries are useful enough to recur across very different engineered systems.

## Imported pattern families

| Pattern | Source examples | UFT-ID use |
|---|---|---|
| Typed transformation stages | QSOL-IMPORT, QSOL-THOTH, QSOL-INT | sharpen `F`, `O`, `T`, and bridge typing |
| Content identity vs location | QSOL-CONTROL, QSOL-THOTH, QEC | finite transport-invariance theorem |
| Projection vs source | QSOL-SUBSTRATE, QSOL-IMPORT, E8_MUSIC | reconstruction and information-loss discipline |
| Receiver neutrality | SONIFICATION, E8_MUSIC, RSH | representation/receiver invariance tests |
| Epistemic authority separation | QSOL-NEXUS, QSOL-ORACLE, QSOL-INT, QSOL-ARK | prevent hashes, votes, storage, recovery, or retrieval from becoming truth functions |
| Calibration locality | RES=RAG | profile-indexed thresholds and transfer counterexamples |
| Deterministic boundary | QEC, QSOL-HARNESS, RSH | replay theorem with explicit implementation/runtime assumptions |
| Minimum sufficient basis | QSOL-THOTH, QSOL-ARK | finite coverage selection under lexicographic tie-breaking |
| Cyclic traversal | LATTICE, SONIFICATION | finite coprime traversal theorem |
| Semantic coincidence boundary | SAW-1 | exact match does not imply causal mechanism |
| Formal/conformance/evidence hierarchy | E8_MUSIC, RSH, QSOL-HARNESS | preserve proof, implementation, experiment, and ontology as different evidence layers |
| Finite decorative compatibility | SONIFICATION `XR-P17` | multiple constructions may share the same finite triality/qutrit compatibility machinery without unique selection |
| Placement geometry vs topology | SPECTRAL `XR-P18` | spiral/phi/qutrit ordering may organize labels without deriving genus or physical topology |

## Source-by-source extraction

### QSOL-SUBSTRATE

Reusable pattern: retrieval and projection carry explicit epistemic state. Missing public data are unavailable, not automatically false. A derived projection does not become canonical merely because it is convenient.

UFT-ID implication: an observation map `O` must not silently change the authority class of the observed object. A projection can preserve, weaken, or omit declared structure, but any epistemic promotion requires a separate rule and evidence.

### QSOL-THOTH

Reusable pattern: routing, resolution, transport, object identity, and authority are different operations. Its historical minimum-set machinery also separates a minimum sufficient reconstruction basis from complete history.

UFT-ID implication: cross-domain transport should be modeled as typed map composition rather than one overloaded `T`. Minimum-basis recovery is a useful finite specialization of lexicographic recovery.

### QSOL-IMPORT

Reusable pattern: source bytes, parsed objects, normalized objects, canonical acceptance, semantic preservation, and byte preservation are not interchangeable.

UFT-ID implication: a transformation pipeline may contain several maps with different codomains and different loss properties. `SOURCE -> NORMALIZED` cannot be treated as identity without proof.

### QSOL-CONTROL

Reusable pattern: content identity can be byte-bound while location, storage membership, search similarity, geometry, and derived codecs remain separate metadata/projections.

UFT-ID implication: transport location can change while declared content identity remains invariant. This motivates the finite transport identity result in `theory/CROSS_REPO_RESULTS.md`.

### LATTICE

Reusable pattern: structural address and traversal do not confer truth or importance. The stride-17 traversal on 27 cells is a concrete instance of the general coprime cyclic traversal theorem.

UFT-ID implication: geometry/position belongs to representation unless an independent physical bridge grants it more authority.

### QSOL-NEXUS

Reusable pattern: consensus, provider identity, model scale, tool access, and telemetry are independent of evidence status. Live stochastic model generation is not made replayable merely because receipts exist around it.

UFT-ID implication: observer outputs and decision aggregates must not become evidence or information authority by position alone. Replay claims require deterministic assumptions.

### QSOL-ORACLE

Reusable pattern: a valid hash-linked ledger establishes integrity under a declared canonicalization, not truth, authorship, endorsement, or scientific validity.

UFT-ID implication: content identity and epistemic truth are separately typed. A cryptographically immaculate false statement remains false.

### QSOL-INT

Reusable pattern: composition preserves parent semantics and recovery/preservation do not increase epistemic entitlement.

UFT-ID implication: a bridge map must state which authority labels are preserved, weakened, undefined, or independently recomputed. Successful transport is not epistemic promotion.

### QSOL-ARK

Reusable pattern: recovery capability is scope-qualified; live implementation state outranks stale summaries; adjacent truths, compatibility layers, and archive presence do not inherit stronger provenance.

UFT-ID implication: recovery and reconstruction require explicit capability and source contracts. A reconstructed state can be admissible without becoming original, exact, or historically authoritative.

### QEC

Reusable pattern: deterministic boundaries are possible without assuming a deterministic world. Canonical JSON, SHA-256 receipts, self-hash exclusion, recompute-not-trust verification, and source-bound claims provide strong reproducibility machinery.

UFT-ID implication: deterministic replay is a property of a declared map/implementation/input contract. It does not generalize to external stochastic systems or physical ontology.

### RES=RAG

Reusable pattern: thresholds and metrics are representation-, estimator-, unit-, and calibration-dependent. Reported constants remain local until a calibration bridge is supplied.

UFT-ID implication: thresholded regimes should use a calibration profile `Gamma`; carrying `Phi_crit`, entropy thresholds, or diagnostic bands between regimes requires an explicit transport argument.

### E8_MUSIC

Reusable pattern: canonical source-forced transforms and interpretive receivers are separate. A ratio-preserving receiver may preserve a declared invariant while still being an observation convention. Formal transform correctness, executable conformance, scientific validation, and physical truth are separate layers.

UFT-ID implication: receiver maps belong naturally under the observation/transport architecture, and a preserved invariant must be named rather than inferred from deterministic output.

### SONIFICATION / ETQ-303

Reusable pattern: canonical event identity is receiver-neutral. Algebraic dimension, root-space dimension, state count, graph adjacency, event order, MIDI representation, and physical spacetime are distinct types.

UFT-ID implication: cross-domain maps must not merge coincident integers or labels into a shared ontology. This is a particularly clean bridge-obligation example.

### XR-P17 — SONIFICATION finite triality compatibility context

Canonical source: `QSOLKCB/SONIFICATION`, `docs/MATHEMATICAL_MODEL.md`, blob `0e8f986dd5ca191c1eded726dd6e276c1f856613`.

Reusable pattern: ETQ-101 supplies a finite authored compatibility context with 33 mutually exclusive triality/qutrit blocks plus two fixed singlets, the local `D3=diag(1,-2,1)` operator, the `theta=pi/2` phase-kick convention, and the exact local identity `F3^3=I3`. The source itself keeps those algebraic labels separate from physical E8 ontology.

UFT-ID implication: finite compatibility machinery can be sufficient to decorate several distinct candidate constructions. Compatibility, block count, phase closure, or E8-derived labels do not thereby select a unique genus or establish a physical topology.

```text
FINITE_COMPATIBILITY != UNIQUE_SELECTION
DECORATIVE_BLOCK_COUNT != TOPOLOGY_DERIVATION
```

### XR-P18 — SPECTRAL placement geometry context

Canonical source: `QSOLKCB/SPECTRAL`, `E8/APP/README.md`, blob `4855bfff69d89c4920a2b2daf59c38b875a617ec`.

Reusable pattern: the E8 Geometry Studio exposes Triality Spiral, qutrit/ternary controls, phi-scaled geometry, and E8-derived control paths as explicit sonification/composition mappings rather than physical E8 measurements.

UFT-ID implication: a spiral, phi-scaled ordering, qutrit control path, or other placement geometry may organize labelled sectors while remaining independent of the topology those labels decorate.

```text
PLACEMENT_GEOMETRY != TOPOLOGY_DERIVATION
CONTROL_GEOMETRY != PHYSICAL_MEASUREMENT
```

### SAW-1

Reusable pattern: an exact semantic/numerical correspondence can be chronologically verified and hash-bound while remaining a coincidence with no causal, retrocausal, or predictive implication.

UFT-ID implication: exact equality of derived descriptors is insufficient to establish mechanism. Bridge evidence must exceed descriptor coincidence.

### QSOL-HARNESS

Reusable pattern: model output is not execution evidence, formal syntax is not proof, receipt identity precedes numerical claims, and no provider is architectural authority.

UFT-ID implication: claim promotion must depend on evidence class, not fluent presentation or model self-report.

### RSH

Reusable pattern: theorem surfaces, reference implementations, native/WASM/GPU conformance, residual sidecars, runtime-specific receipts, and empirical interpretations are separately versioned and separately authoritative.

UFT-ID implication: a theorem can certify a mathematical transform while an implementation still requires conformance testing and a physical interpretation still requires independent empirical evidence.

## Quarantined adversarial lineage

### QAI-UFT

The historical `%60`, `%64`, base-3, codon, acoustic, ritual, and visualization mappings are useful **representation-dependence examples**. They are not imported as physical field ontology.

Their value to UFT-ID 3.0 is adversarial: many aesthetically meaningful maps can be deterministic and reproducible while remaining authored observation choices.

### info-mass-gravity

The older suite is useful precisely because it exposes assumption injection clearly.

`mass_energy_equivalence.py` hard-codes a Vopson mass-per-bit constant and then builds model functions around that premise. `entropic_gravity.py` computes intermediate entropic quantities but ultimately returns the ordinary Newtonian force expression directly.

These are valuable regression specimens for two UFT-ID rules:

```text
ASSUMED_RELATION != INDEPENDENT_DERIVATION
RECOVERED_KNOWN_FORMULA != NOVEL_PREDICTION
```

They must not be promoted into evidence for information mass or information-specific gravity.

## What was deliberately not imported

The repository inventory also contains games, user interfaces, humour projects, third-party forks/mirrors, private context stores, active experiments, and application repositories whose current semantics add no distinct theorem or diagnostic pattern to this PR.

Not importing them is deliberate compression, not a claim that they are unimportant.

## Resulting formal direction

The cross-repo scan suggests that UFT-ID should become stricter in four places:

1. **Map composition:** represent stage boundaries explicitly instead of overloading `F`, `O`, or `T` when multiple transformations occur.
2. **Receiver contracts:** declare exactly which structure each projection preserves and loses.
3. **Calibration profiles:** index thresholds and classifications by their metric/estimator/unit/preprocessing contract.
4. **Evidence separation:** content integrity, replay, recovery, observation, consensus, and storage must never silently become truth or physical authority.

The two current selection-context records add a fifth discipline:

5. **Selection discipline:** compatibility and placement structure must not be promoted into uniqueness or topology derivation without an explicit discriminating theorem.

These are auxiliary contracts around the existing canonical tuple. They do **not** enlarge the canonical tuple merely to accommodate repository terminology.
