# UFT-ID 3.0 Historical Lineage Registry

**Status:** human guide to the machine authorities under `machine/historical_*.json`.

This registry preserves lineage without importing historical ontology by adjacency. Completeness is bounded to the UFT-ID lineage and selected inheritance sources discovered and verified in the 2026-08-19 audit across Academia, Zenodo, Authorea, Google Drive, GitHub and archived copies. Unknown metadata stays unknown. Private Gmail/Drive identifiers are deliberately redacted.

```text
HISTORICAL_SOURCE != CURRENT_ENDORSEMENT
PLATFORM_MIRROR != CANONICAL_AUTHORITY
SOURCE_HASH != SEMANTIC_TRUTH
WORKING_COPY_EXPORT_HASH != NATIVE_CLOUD_OBJECT_HASH
FORMAL_RESULT != COMPUTATIONAL_RESULT
COMPUTATIONAL_RESULT != EMPIRICAL_RESULT
CONFLICT != ERROR_TO_ERASE
METHOD_INHERITANCE != ONTOLOGY_INHERITANCE
```

The audited surface contains **15 registered sources**, **29 historical symbol mappings**, **11 explicit definition conflicts**, **15 classified historical results**, and **7 methodological inheritance contracts**.

## Source registry

| ID | Source | DOI | Date/version | Licence | Review/status | Relation |
|---|---|---|---|---|---|---|
| `UFT-HIST-001` | UFT-ID 2.0: Lattice-Gated Information Dynamics and Lexicographic State Selection | `10.22541/au.176765062.20893637/v1` | `2025-12-26/v1` | `unverified` | `preprint-not-peer-reviewed` | `historical-lineage-source-not-current-implementation` |
| `UFT-HIST-002` | UFT-ID 2.0: Constraint-First Information Dynamics and Deterministic Recovery | `10.22541/au.176790865.55905239/v1` | `2026-01-07/v1` | `CC-BY-4.0` | `preprint-not-peer-reviewed` | `preferred-abstract-lineage` |
| `UFT-HIST-003` | A Unified Framework for Unified Field Theory of Information Dynamics: Constraint-First Dynamics and Deterministic Recovery | `10.22541/au.176790866.68066655/v1` | `2026-01-07/v1` | `unverified` | `preprint-not-peer-reviewed` | `preferred-abstract-lineage` |
| `UFT-HIST-004` | Geometry, Infodynamics, and the Emergence of Transportable Physical States | `10.22541/au.176780579.95800648/v1` | `2025-12-27/v1` | `unverified` | `preprint-not-peer-reviewed` | `historical-transport-specialization` |
| `UFT-HIST-005` | Unified Field of Information Dynamics (UFT-ID): A Field-Theoretic Extension of RES = RAG and CBD | `-` | `2026-01-20/-` | `unverified` | `preprint-submission-screening-status-only` | `-` |
| `UFT-HIST-006` | Ternary Logic and Information Dynamics: A Field-Theoretic Framework (UFT-ID) | `-` | `2026-01-20/-` | `unverified` | `preprint-submission-screening-status-only` | `-` |
| `UFT-HIST-007` | The UFT-ID Inference Transport Diagnostic Map | `-` | `2026-02-02/multiple-submission-revisions` | `unverified` | `preprint-submission-screening-status-only` | `-` |
| `UFT-HIST-008` | UFT-ID 2.0 Framework Components and Definitions | `-` | `2026-01-07/-` | `unverified` | `not-applicable-working-record` | `-` |
| `UFT-HIST-009` | Dark Information: The Architecture of the Unobserved | `-` | `2026-03-19/-` | `unverified` | `not-applicable-working-record` | `-` |
| `UFT-METH-001` | QSOL-SUBSTRATE public bootstrap contract | `-` | `2026-08-19/schema 1.0.0` | `Apache-2.0` | `not-applicable-software-contract` | `public-canonical-method-source` |
| `UFT-METH-002` | ETQ-303 v3.0.1 Formal Mathematical Specification and Reproducibility Record | `10.5281/zenodo.21455181` | `2026-07-22/3.0.1` | `MPL-2.0` | `formal-specification-no-empirical-validation-claim` | `receiver-neutrality-method-source` |
| `UFT-METH-003` | QSOLKCB/QEC deterministic evidence and receipt contract | `-` | `2026-08-19/repository release surface v170.1.1` | `MPL-2.0` | `not-applicable-software-contract` | `multi-scale-invariant-and-receipt-method-source` |
| `UFT-METH-004` | RES=RAG Relational Equilibrium Framework / CSNP | `10.5281/zenodo.21917464` | `2026-08-19/1.1.0` | `CC-BY-4.0` | `not-indicated-research-package` | `calibration-and-provenance-method-source` |
| `UFT-METH-005` | QSOL NEXUS machine-readable AI manifest | `-` | `2026-08-19/protocol nexus/0.14; runtime 2.0.0 release-candidate` | `Apache-2.0` | `not-applicable-software-contract` | `evidence-hierarchy-method-source` |
| `UFT-METH-006` | RSH-EPISTEMIC-V1 machine-readable epistemic contract | `-` | `2026-08-19/RSH-EPISTEMIC-V1` | `MPL-2.0` | `not-applicable-machine-contract` | `machine-readable-epistemic-and-nonclaim-boundary-source` |

## Historical symbol map

Canonical detail is in `machine/historical_symbols.json`. The important collision is historical `rho` as an SU(3) density operator versus current `rho : S -> V` as an optional vector residual. Historical `Lambda`, `kappa_c`, weighting constants and lattice-generator symbols are superseded rather than quietly renamed.

## Preserved conflicts

- **`HDC-001` state-space scope**: S is described as a fixed universal domain containing all constructible states. Current 3.0: D1 defines S per model and assumes no topology, metric, measure, algebra, probability structure, or universal ontology by default. Resolution: `do-not-reconcile-silently`.
- **`HDC-002` admissibility geometry**: A/Omega_Lat is tied to a discrete lattice, curvature/packing/complexity thresholds, and physical/computational realizability. Current 3.0: D3 defines A solely by the declared hard constraints C and permits discrete or continuous, non-linear, non-geometric sets. Resolution: `do-not-reconcile-silently`.
- **`HDC-003` rho symbol collision**: rho denotes the SU(3) density-operator information state. Current 3.0: D5 reserves rho : S -> V for the vector residual used in an operator-valued quadratic tension specialization. Resolution: `do-not-reconcile-silently`.
- **`HDC-004` tension typing**: The spreadsheet writes Phi(s)=1/2 r(s) K r(s) while r(s) is separately defined as a scalar distance/residual. Current 3.0: D5 uses Phi=(k/2)r^2 for scalar r, and uses 1/2<rho,K rho> only after declaring a vector residual rho:S->V and PSD self-adjoint K. Resolution: `do-not-reconcile-silently`.
- **`HDC-005` lexicographic versus weighted selection**: Historical prose declares strict lexicographic priorities, but the archived pseudocode computes a weighted sum inv_error + epsilon*transport. Current 3.0: D9-D10 define true ordered objectives with successive tie restriction and a final total-order tie-break. Resolution: `do-not-reconcile-silently`.
- **`HDC-006` information ontology**: Historical sources variously describe information as constrained lattice excitation, an SU(3)/ternary field, or a field-theoretic substrate. Current 3.0: D14 defines I as a declared information functional whose exact type must be named; UFT-ID 3.0 does not assume information is substance, field, mass, energy, spacetime, or consciousness. Resolution: `do-not-reconcile-silently`.
- **`HDC-007` shear meaning**: kappa is simultaneously a Casimir-fidelity loss, thermodynamic phase order parameter, AI hallucination measure, and truthfulness diagnostic. Current 3.0: D18/D23 permit representation or transport defects only relative to declared maps/observables; no defect is a universal truth score or thermodynamic entropy production term. Resolution: `do-not-reconcile-silently`.
- **`HDC-008` recovery event versus released energy**: Delta=s_minus-s_plus is described as released tension and an observable event, with mechanical/emission analogies. Current 3.0: D12 defines the recovery event E=(s_minus,s_plus); D13 defines Delta only when subtraction exists and assigns no automatic energy interpretation. Resolution: `do-not-reconcile-silently`.
- **`HDC-009` dynamics and time model**: The historical model privileges discrete unitary proposal followed by CPTP-style correction and sometimes interprets the computational search cost as physical reduction time. Current 3.0: D7 and D25 require discrete, continuous, and stochastic dynamics to be stated separately; runtime cost is not physical time without a bridge. Resolution: `do-not-reconcile-silently`.
- **`HDC-010` truth and admissibility**: Historical prose equates truth with geometric fit and suggests high shear can algebraically flag truthfulness. Current 3.0: D30 separates epistemic/authority metadata from state admissibility; content identity, geometry, recovery, consensus, or defect scores do not establish truth. Resolution: `do-not-reconcile-silently`.
- **`HDC-011` observer-relative darkness versus physical destruction**: The Dark Information report blends erased, latent, inaccessible, cosmological, cognitive, and anomalous information under one broad 'dark' umbrella. Current 3.0: D16-D18 distinguish observation, reconstruction, and representation defect; observer inaccessibility is not physical destruction and different information notions remain typed. Resolution: `do-not-reconcile-silently`.

## Historical result classification

No audited historical source is promoted to empirical merely because it contains physical language. The registry uses only `formal`, `computational`, `empirical`, `interpretive`, or `speculative`; in this snapshot no historical item has sufficient primary measurement evidence to receive `empirical`.

- `HIST-R01` **formal**: Constraint-first admissibility architecture
- `HIST-R02` **formal**: Deterministic lexicographic recovery
- `HIST-R03` **formal**: Lattice-gated proposal/audit/recovery pipeline
- `HIST-R04` **computational**: Archived evolve_step implementation sketch
- `HIST-R05` **formal**: Shear coefficient as normalized structural defect
- `HIST-R06` **speculative**: Geometric primacy / discrete lattice ontology
- `HIST-R07` **speculative**: Quantum collapse as deterministic geometric correction
- `HIST-R08` **interpretive**: AI hallucination as geometric syntax failure
- `HIST-R09` **speculative**: Shear-to-heat and thermodynamic phase interpretation
- `HIST-R10` **interpretive**: Transportable-state / invariant-preservation programme
- `HIST-R11` **computational**: Inference Transport Diagnostic Map
- `HIST-R12` **interpretive**: Field-theoretic RES=RAG/CBD extension
- `HIST-R13` **speculative**: Ternary/SU(3) information-field representation
- `HIST-R14` **interpretive**: Observer-relative inaccessible-state diagnostic
- `HIST-R15` **interpretive**: Current formalization plan's internal-consistency claim

## Methodological inheritance

### INH-01 Canonical source versus projection
Claim class: `DEFINITION`. Sources: `UFT-METH-001`.
UFT mapping: `D27`, `D28`, `D29`, `D30`.
Preserved: canonical source remains separately identified from projections; retrieval is distinct from inference; absence is unavailable rather than automatically false; epistemic state is preserved across projection.
Not inherited: QSOL-SUBSTRATE resource layout; private/public context architecture; domain-mode taxonomy; software authority as physical authority.
Prohibited inference: A projection or retrieval surface is not promoted to source truth or physical ontology.

### INH-02 Receiver neutrality and non-privileged projection
Claim class: `DEFINITION`. Sources: `UFT-METH-002`.
UFT mapping: `D29`, `D33`, `T21`.
Preserved: receiver is an explicit map; canonical event/source object is separate from receiver artifacts; no receiver is mathematically privileged; preserved and lost structure must be declared.
Not inherited: E8/D4/qutrit ontology; 303 as physical dimension; audio/MIDI/WAV interpretation; particular receiver vocabulary.
Prohibited inference: A deterministic receiver is not a uniquely natural observation of the underlying domain.

### INH-03 Multi-scale invariant preservation and deterministic receipts
Claim class: `DIAGNOSTIC`. Sources: `UFT-METH-003`.
UFT mapping: `D28`, `D29`, `D33`, `T21`, `T22`.
Preserved: canonical input/output identity; recompute-not-trust validation; explicit invariant checks at named boundaries; deterministic evidence receipts; runtime/release identity kept separate from scientific claim.
Not inherited: quantum hardware validity; fault-tolerance threshold claims; decoder-specific ontology; deterministic software as evidence for deterministic universe.
Prohibited inference: A replay-safe receipt or invariant match does not establish a physical quantum claim.

### INH-04 Dark-state / observer-inaccessible specialization
Claim class: `DIAGNOSTIC`. Sources: `UFT-HIST-009`.
UFT mapping: `D16`, `D17`, `D18`, `T17`.
Preserved: internal/latent state may be distinct from observable emission; inaccessibility is observer-relative; black-box limits can be studied without declaring hidden state absent; reconstruction may fail without physical destruction.
Not inherited: dark information as a substance; dark matter/dark energy identification; psi or anomalous cognition mechanism; consciousness ontology; claim that unobserved means physically destroyed.
Prohibited inference: Observer inaccessibility is not evidence for a hidden physical substance or anomalous causal channel.

### INH-05 Calibration locality and provenance discipline
Claim class: `DIAGNOSTIC`. Sources: `UFT-METH-004`.
UFT mapping: `D31`, `T18`, `CR3`.
Preserved: metrics and thresholds are calibration-profile dependent; representation/ground metric/estimator choices are explicit; recalibration is a named event; numerical claims retain provenance labels.
Not inherited: universal RES/RAG consciousness ontology; 0.42 or any other local threshold as universal constant; Wasserstein distance as universal physical cost; CSNP labels as fundamental physics.
Prohibited inference: A threshold or metric value measured under one calibration profile cannot be transported unchanged without a bridge.

### INH-06 Formal theorem != runtime result != physical validation
Claim class: `DEFINITION`. Sources: `UFT-METH-005`.
UFT mapping: `D30`, `D33`, `T22`.
Preserved: model output is untrusted input; consensus/telemetry/provider identity confer no epistemic authority; runtime behavior and tests are distinct from prose/formal declarations; live stochastic inference is not falsely marked replayable.
Not inherited: NEXUS council/world governance; model-role ontology; shared-world cognitive substrate as scientific ontology; provider-specific semantics.
Prohibited inference: A proof-looking artifact, runtime success, consensus result, or telemetry record cannot be promoted across evidence layers without the required bridge.

### INH-07 Machine-readable nonclaim and epistemic-cap surfaces
Claim class: `DEFINITION`. Sources: `UFT-METH-006`.
UFT mapping: `D30`, `D33`.
Preserved: machine-readable epistemic states; machine-readable evidence classes and promotion caps; unknown is not false; conflict remains visible; formal syntax is not proof; receipt identity does not imply empirical truth.
Not inherited: RSH helix/tissue geometry; biological interpretation; specific claim-tier vocabulary as universal law; RSH formal theorem content.
Prohibited inference: A machine-readable claim policy constrains what may be asserted; it does not itself prove the governed scientific claim.

## Exit criterion

The machine validator requires every historical source to have classified-result coverage and every inherited method to have a source, exactly one UFT-ID claim class, preserved structure, explicit non-inheritance and a prohibited inference. It also rejects silent conflict reconciliation, malformed GitHub pins, private connector-ID leakage, and Drive export hashes mislabeled as native cloud hashes.

```bash
python scripts/validate_historical_lineage.py --json
python -m unittest tests.test_historical_lineage -v
python -O -m unittest tests.test_historical_lineage -v
python experiments/run_lineage.py --json
```
