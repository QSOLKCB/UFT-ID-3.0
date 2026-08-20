# UFT-ID 3.0: AI Bootstrap

This is the preferred entry point for AI agents working in the repository.

## Mission

Develop UFT-ID 3.0 as a rigorously scoped theory-and-experiment programme for
constraint-governed information dynamics. Preserve hard boundaries between
formal results, diagnostics, empirical evidence, interpretation, speculation,
and nonclaims.

## Canonical object

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

- `S`: total state space
- `A`: admissible subset
- `F`: proposed evolution
- `Pi_lex`: deterministic recovery
- `O`: observation or coarse-graining map
- `T`: regime-transport map
- `I`: explicitly declared information functional
- `C`: constraint structure

Do not specialize these symbols to E8, SU(3), LQG, cognition, AGI, gravity,
extra-time spacetime, or another ontology unless the target document explicitly
enters an interpretive or speculative layer.

## Current mathematical direction

```text
No universal information-direction theorem exists without fixing S, F, O,
reference measure, partition/coarse-graining, I, boundaries, and sources.
```

Monotonicity must be proved from the declared dynamics. The generic balance
expression remains non-predictive until its terms are independently derived.

## Claim classes

Every UFT-ID assessment uses exactly one of:

- `DEFINITION`
- `THEOREM_TARGET`
- `PROVED`
- `COUNTEREXAMPLE`
- `DIAGNOSTIC`
- `EMPIRICAL`
- `INTERPRETIVE`
- `SPECULATIVE`
- `NONCLAIM`

Recording another author's source claim is not an endorsement. Source claim and
repository assessment are distinct objects even where a schema stores them near
each other.

## Relation and graph-realization authority

The current relation core uses:

```text
stepRel : X -> X -> Prop
A       : X -> Prop
```

with admissibility independent from rewriting. The graph-realization layer is a
finite/set-theoretic representation of `stepRel`, not a new physical ontology:

```text
G_step = (X, A_step)
(x,y) in A_step iff stepRel(x,y)
```

Canonical graph surfaces:

```text
machine/graph_realization_contract.json
machine/graph_realization_results.json
research/GRAPH_REALIZATION_SOURCES.md
theory/GRAPH_REALIZATION.md
scripts/validate_graph_realization.py
experiments/graph_realization/run.py
experiments/run_graph_realization.py
tests/test_graph_realization.py
```

The positive graph result surface currently registers `UFT-GR-001` through
`UFT-GR-006` as `PROVED` abstract mathematics. Read `docs/CLAIMS.md` for the
allowed claim scope.

The finite executable battery independently cross-checks all 530 labelled
binary relations on `Fin1`, `Fin2`, and `Fin3`, including relation adjacency,
normality, reachability, finite termination, SCC partition, sink SCCs, and SCC
condensation.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY
GRAPH != DRAWING
NORMAL_VERTEX != SINK_SCC
```

Typed incidence is kept separate from untyped adjacency:

```text
IncSpec = (M, L, I)
I subseteq M x L x M
```

A tetrahedron's geometric 1-skeleton is `K4`; an SiS4 chemical-bond graph and a
polyhedral-sharing graph are different objects. ETQ/SPECTRAL coupling and
placement structures are likewise distinct unless an explicit bridge is given.

```text
TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH
LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH
COUPLING_GRAPH != PLACEMENT_GRAPH
ALGEBRA != GRAPH != EMBEDDING != PHYSICS
```

The Grinberg graph-theory source is a mathematical donor. The SiS2 source is a
bounded structural positive control. Neither source makes a UFT-ID physical
claim true by analogy.

## Cross-repository formal pattern authority

UFT-ID may use public, merged, inspectable QSOLKCB repositories as a **pattern
library** for theorem hypotheses, finite examples, provenance discipline,
receiver contracts, calibration rules, or adversarial counterexamples.

Canonical surfaces:

```text
research/CROSS_REPO_PATTERN_ATLAS.md
machine/cross_repo_patterns.json
theory/AUXILIARY_CONTRACTS.md
theory/CROSS_REPO_RESULTS.md
machine/cross_repo_results.json
scripts/validate_cross_repo_patterns.py
experiments/cross_repo/run.py
experiments/run_cross_repo.py
```

The governing boundary is:

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

Rules:

1. Import structure, not ontology.
2. Public merged-main/released source behavior may motivate a formal pattern;
   open-PR-only behavior may not enter the positive registry.
3. Private repositories are forbidden in the public cross-repo source registry.
4. Every source record is pinned to repository, `main`, file path, and Git blob
   SHA at the registry snapshot.
5. CI validates the local registry and pins but does not claim live remote
   freshness; re-audit source pins when freshness matters.
6. Quarantined legacy sources may motivate counterexamples or assumption audits,
   but cannot back positive UFT-ID result authority.
7. Content identity, recovery, retrieval, storage, consensus, telemetry,
   deterministic replay, or successful transport do not automatically confer
   semantic truth or physical authority.
8. Calibration thresholds remain local until an explicit bridge establishes transfer.
9. Formal proof, implementation conformance, empirical validation, and physical
   ontology remain distinct evidence layers.
10. A semantic or numerical coincidence is not causal evidence.

The cross-repo finite surface currently records CR1-CR7, including
byte-preserving transport identity, non-injective reconstruction impossibility,
calibration-transfer failure, coprime traversal, minimum sufficient-basis
selection, integrity-versus-truth separation, and the deterministic replay
boundary.

## Canonical Vopson authority chain

```text
research/vopson/AUTHOR.json
research/vopson/corpus.json
research/vopson/CLAIM_GRAPH.json
research/vopson/REPRODUCTION_MATRIX.md
research/vopson/COUNTEREXAMPLE_MATRIX.md
research/vopson/RESPONSE_HISTORY.md
```

Human guides:

```text
research/vopson/CORPUS.md
research/vopson/CLAIM_GRAPH.md
research/vopson/DEFINITIONS.md
```

Rules:

1. ORCID `0000-0002-8073-5538` is a public bibliographic anchor only.
2. Never invent a DOI, source locator, review status, source-byte hash, or reproduction result.
3. A dependency edge records reliance, not truth.
4. `metadata-verified` is not `reproduced`.
5. `PROVED` and `COUNTEREXAMPLE` require repository-contained evidence unless a controlled external premise is explicitly marked established literature.
6. Human corpus tables must match their JSON authorities.
7. Static entropy ordering does not supply physical dynamics.
8. A restricted deterministic Shannon theorem is not the full published SLI.

## VOP-2019-MEI reproduction authority

The first source-specific reproduction package lives under:

```text
research/vopson/reproduction/2019-mei/
experiments/reproduction/vopson_2019_mei/
experiments/run_pr6.py
scripts/validate_vopson_2019_mei.py
tests/test_vopson_2019_mei.py
```

It reproduces the 2019 paper's Eq. (6) arithmetic and displayed `300 K`, `2.73 K`,
and decimal `1 TB` numerical values while keeping the physical bridge explicit:

```text
LANDAUER_ERASURE_BOUND != INTRINSIC_STORED_BIT_ENERGY
ARITHMETIC_REPRODUCED != PREMISE_VALIDATED
ARITHMETIC_REPRODUCED != EXPERIMENTALLY_CONFIRMED
```

Primary paper bytes are not committed. Cite the DOI and exact page/equation
locators. Never invent a source PDF hash merely because local reproduction files
have deterministic hashes.

## Reproducibility authority

Read `docs/REPRODUCIBILITY.md` before changing executable evidence.

Canonical finite information helpers live in `experiments/lib/information.py`.
Scientific invariants must use explicit exceptions, not ordinary Python
`assert`, because `python -O` removes assertions.

GitHub Actions must use the fixed runner and full commit SHA pins declared in
`machine/contract.json`. CI receipts are retained as workflow artifacts.

## Required validation commands

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_cross_repo_patterns.py
python scripts/validate_vopson_2019_mei.py
python scripts/validate_reproducibility.py
python scripts/validate_formalization_contracts.py
python scripts/validate_observation_specs.py
python scripts/validate_relation_core.py
python scripts/validate_graph_realization.py
python experiments/graph_realization/run.py --json
python experiments/run_graph_realization.py --json
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
python experiments/run_cross_repo.py --json
python experiments/reproduction/vopson_2019_mei/run.py --json
python experiments/run_pr6.py --json
```

To update machine-derived Vopson Markdown tables intentionally:

```bash
python scripts/render_vopson_docs.py
```

Then review the diff and rerun `--check`.

## Hard rules

1. Do not claim information is matter, mass, energy, spacetime, consciousness,
   or a physical field merely because a model uses physical mathematics.
2. Do not infer a universal law from examples without a quantified domain and
   explicit assumptions.
3. Do not interchange Shannon, thermodynamic, von Neumann, relative,
   algorithmic, observational, and mutual information.
4. Do not compare values across changed partitions, alphabets, references,
   boundaries, observation maps, receivers, or calibration profiles without
   declaring the bridge.
5. Do not turn cross-domain or cross-repository analogy into shared mechanism.
6. Simulation output is not proof.
7. A successful fit is not a unique explanation.
8. Lean verification requires checked source and green CI.
9. Critique equations, assumptions, data, and inference, not people.
10. Prefer exact reproduction, counterexamples, null models, sensitivity tests,
    and preregistered comparisons over rhetoric.
11. Do not infer truth from hash integrity, replay, storage, retrieval,
    consensus, recovery, or transport.
12. Do not use legacy QAI-UFT or info-mass-gravity ontology as formal authority;
    their registered role is adversarial/quarantined lineage only.
13. Do not infer intrinsic stored-bit energy from the Landauer erasure bound
    without an independently justified physical bridge.
14. Correct arithmetic is not experimental confirmation.
15. Do not silently correct a source-text inconsistency; record the printed
    source and the comparison standard separately.
16. Do not infer physical ontology from graph isomorphism, visual resemblance,
    tetrahedral geometry, material coordination, or a finite conformance suite.
17. Do not promote roadmap-only donor models, including extra-time spacetime
    hypotheses, into current UFT-ID theorem or physical authority.

## Lean

Lean is deferred until source reproduction, notation freeze, theorem freeze,
and counterexample freeze. Begin later with finite admissibility, finite
lexicographic recovery, residual lemmas, discrete identities, restricted
monotonicity, explicit finite failure cases, coprime cyclic traversal, and the
finite minimum sufficient-basis selector.

## Read next

1. `AGENTS.md`
2. `docs/CLAIMS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/REPRODUCIBILITY.md`
5. `docs/MILESTONES.md`
6. `experiments/README.md`
7. `theory/DEFINITIONS.md`
8. `theory/AUXILIARY_CONTRACTS.md`
9. `theory/THEOREM_TARGETS.md`
10. `theory/FINITE_RESULTS.md`
11. `theory/RELATION_CALCULUS.md`
12. `theory/GRAPH_REALIZATION.md`
13. `machine/graph_realization_contract.json`
14. `machine/graph_realization_results.json`
15. `research/GRAPH_REALIZATION_SOURCES.md`
16. `scripts/validate_graph_realization.py`
17. `experiments/run_graph_realization.py`
18. `theory/CROSS_REPO_RESULTS.md`
19. `research/CROSS_REPO_PATTERN_ATLAS.md`
20. `machine/cross_repo_patterns.json`
21. `machine/cross_repo_results.json`
22. `research/vopson/CORPUS.md`
23. `research/vopson/CLAIM_GRAPH.md`
24. `research/vopson/DEFINITIONS.md`
25. `research/vopson/REPRODUCTION_MATRIX.md`
26. `research/vopson/reproduction/2019-mei/SOURCE_MAP.md`
27. `research/vopson/reproduction/2019-mei/DERIVATION.md`
28. `research/vopson/reproduction/2019-mei/ASSUMPTION_GRAPH.json`
29. `research/vopson/reproduction/2019-mei/DIMENSIONAL_AUDIT.md`
30. `research/vopson/reproduction/2019-mei/CONTROL_MATRIX.md`
31. `research/vopson/reproduction/2019-mei/result.json`
32. `research/vopson/COUNTEREXAMPLE_MATRIX.md`
33. `research/vopson/RESPONSE_HISTORY.md`
34. `research/reports/2026-08-18-PR4-ACTION-REGISTER.md`
35. `research/VOPSON_MATRIX.md`
36. `ROADMAP.md`
