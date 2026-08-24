# UFT-ID 3.0: AI Bootstrap

This is the preferred entry point for AI agents working in the repository.

## Mission

Develop UFT-ID 3.0 as a rigorously scoped theory-and-experiment programme for constraint-governed information dynamics. Preserve hard boundaries between formal results, diagnostics, empirical evidence, interpretation, speculation, and nonclaims.

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

Do not specialize these symbols to E8, SU(3), LQG, cognition, AGI, gravity, extra-time spacetime, or another ontology unless the target document explicitly enters an interpretive or speculative layer.

## Claim classes

Every UFT-ID assessment uses exactly one of:

```text
DEFINITION
THEOREM_TARGET
PROVED
COUNTEREXAMPLE
DIAGNOSTIC
EMPIRICAL
INTERPRETIVE
SPECULATIVE
NONCLAIM
```

Recording another author's source claim is not an endorsement.

## Relation and graph-realization authority

The relation core uses:

```text
stepRel : X -> X -> Prop
A       : X -> Prop
```

with admissibility independent from rewriting. The graph-realization layer is a finite/set-theoretic representation of `stepRel`, not a physical ontology.

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

The finite battery cross-checks all 530 labelled relations on `Fin1`, `Fin2`, and `Fin3`.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
ABSTRACT_GRAPH_RESULT != PHYSICAL_ONTOLOGY
GRAPH != DRAWING
NORMAL_VERTEX != SINK_SCC
```

Typed incidence remains separate from untyped adjacency:

```text
IncSpec = (M, L, I)
I subseteq M x L x M
```

```text
TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH
LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH
COUPLING_GRAPH != PLACEMENT_GRAPH
ALGEBRA != GRAPH != EMBEDDING != PHYSICS
```

## BridgeCore authority

The structural-transport layer uses:

```text
BridgeSpec = (
  source_type,
  target_type,
  domain,
  map_or_relation,
  preserved_structure,
  lost_structure,
  scope,
  source_version,
  target_version
)
```

Canonical BridgeCore surfaces:

```text
machine/bridge_core_contract.json
machine/bridge_core_results.json
theory/BRIDGE_CORE.md
scripts/validate_bridge_core.py
experiments/bridge_core/run.py
experiments/run_bridge_core.py
scripts/verify_bridge_artifacts.py
tests/test_bridge_core.py
```

`UFT-BR-001` through `UFT-BR-005` are abstract/set-theoretic results only. The finite witness checks 4,096 relation triples and 729 ordered partial preservation/loss pairs.

```text
BRIDGE != IDENTITY
TRANSPORT != EQUIVALENCE
DISJOINT_METADATA != EXHAUSTIVE_METADATA
RELATIONAL_IDENTITY_NEUTRALITY != UNCONDITIONAL_METADATA_NEUTRALITY
STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION
FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF
BRIDGE_CONFORMANCE != PHYSICAL_VALIDATION
```

## Epistemic Bridge authority

The completed planned PR #13 surface factorizes evidence/authority bookkeeping instead of imposing a global ladder:

```text
EpistemicState = (
  evidence_refs,
  retrieved_refs,
  inference_refs,
  verification_receipts,
  execution_receipts,
  conflict_refs,
  scope
)
```

Canonical Epistemic Bridge surfaces:

```text
machine/epistemic_bridge_contract.json
machine/epistemic_bridge_results.json
theory/EPISTEMIC_BRIDGE.md
scripts/validate_epistemic_bridge.py
experiments/epistemic_bridge/run.py
experiments/run_epistemic_bridge.py
scripts/verify_epistemic_bridge_artifacts.py
tests/test_epistemic_bridge.py
```

The finite witness enumerates all 64 raw six-bit authority-presence vectors and exactly 33 valid normalized shapes.

```text
STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION
RETRIEVED != VERIFIED
INFERRED != VERIFIED
EXECUTED != VERIFIED
VERIFIED != TRUE
CONFLICT != UNKNOWN
VERIFIED != CONFLICT_FREE
NO_GLOBAL_EPISTEMIC_LATTICE
FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY
```

Transport preserves the authority vector and can only narrow scope. Verification is explicit and receipt-bearing. A verified item may still participate in an unresolved conflict.

## Representation and congruence authority

The active planned PR #14 surface requires every invariant claim to name the transformation class and its hypotheses.

Canonical Representation surfaces:

```text
machine/representation_contract.json
machine/representation_results.json
theory/REPRESENTATION_CALCULUS.md
scripts/validate_representation_calculus.py
experiments/representation_calculus/run.py
experiments/run_representation_calculus.py
scripts/verify_representation_artifacts.py
tests/test_representation_calculus.py
```

Transformation classes remain distinct:

```text
similarity:                 B=P^{-1}AP
orthogonal similarity:      B=Q^T A Q, Q^TQ=I
unitary similarity:         B=U^* A U, U^*U=I
real congruence:             B=P^T A P
coordinate change:           v'=P^{-1}v, A'=P^{-1}AP
receiver re-encoding:        O'=R o O
```

The exact finite reference battery checks 3,240 similarity instances, 3,240 congruence-rank instances, 648 orthogonal Frobenius instances, 29,160 coordinate-covariance instances, and 3,969 receiver-equivalence source-pair instances.

```text
SIMILARITY != CONGRUENCE
SIMILARITY != ORTHOGONAL_OR_UNITARY_SIMILARITY
SAME_CHARACTERISTIC_POLYNOMIAL != SIMILARITY
CONGRUENCE != SPECTRAL_EQUIVALENCE
COORDINATE_TUPLE != ABSTRACT_OBJECT
REPRESENTATION_CHANGE != PHYSICAL_CHANGE
RECEIVER_REENCODING != STATE_TRANSFORMATION
NONINJECTIVE_RECEIVER_REENCODING != OBSERVATIONAL_EQUIVALENCE_PRESERVATION
INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE
FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF
```

## Cross-repository formal pattern authority

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

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
CONTENT_IDENTITY != TRUTH
RECOVERY != EPISTEMIC_PROMOTION
FORMAL_PROOF != IMPLEMENTATION_CONFORMANCE
IMPLEMENTATION_CONFORMANCE != EMPIRICAL_VALIDATION
EMPIRICAL_VALIDATION != PHYSICAL_ONTOLOGY
ADJACENT_TRUTH != INHERITED_TRUTH
```

Import structure, not ontology. Public merged/released repository behavior may motivate a formal pattern; private or open-PR-only behavior may not enter positive source authority.

## Canonical Vopson authority chain

```text
research/vopson/AUTHOR.json
research/vopson/corpus.json
research/vopson/CLAIM_GRAPH.json
research/vopson/REPRODUCTION_MATRIX.md
research/vopson/COUNTEREXAMPLE_MATRIX.md
research/vopson/RESPONSE_HISTORY.md
```

Rules:

1. ORCID `0000-0002-8073-5538` is a public bibliographic anchor only.
2. Never invent DOI, source locator, review status, source-byte hash, or reproduction result.
3. Dependency edges record reliance, not truth.
4. `metadata-verified` is not `reproduced`.
5. Static entropy ordering does not supply physical dynamics.

## VOP-2019-MEI reproduction authority

```text
research/vopson/reproduction/2019-mei/
experiments/reproduction/vopson_2019_mei/
experiments/run_pr6.py
scripts/validate_vopson_2019_mei.py
tests/test_vopson_2019_mei.py
```

```text
LANDAUER_ERASURE_BOUND != INTRINSIC_STORED_BIT_ENERGY
ARITHMETIC_REPRODUCED != PREMISE_VALIDATED
ARITHMETIC_REPRODUCED != EXPERIMENTALLY_CONFIRMED
```

Primary paper bytes are not committed. Cite DOI plus page/equation locators; never invent a source PDF hash.

## Reproducibility authority

Read `docs/REPRODUCIBILITY.md` before changing executable evidence. Scientific invariants must use explicit exceptions, not ordinary Python `assert`, because `python -O` removes assertions.

GitHub Actions use the fixed runner and full commit SHA pins declared in `machine/contract.json`; CI receipts are retained as artifacts.

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
python scripts/validate_bridge_core.py
python experiments/bridge_core/run.py --json
python experiments/run_bridge_core.py --json
python scripts/validate_epistemic_bridge.py
python experiments/epistemic_bridge/run.py --json
python experiments/run_epistemic_bridge.py --json
python scripts/validate_representation_calculus.py
python experiments/representation_calculus/run.py --json
python experiments/run_representation_calculus.py --json
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
python experiments/run_cross_repo.py --json
python experiments/reproduction/vopson_2019_mei/run.py --json
python experiments/run_pr6.py --json
```

## Hard rules

1. Do not claim information is matter, mass, energy, spacetime, consciousness, or a physical field merely because a model uses physical mathematics.
2. Do not infer a universal law from examples without a quantified domain and explicit assumptions.
3. Do not interchange Shannon, thermodynamic, von Neumann, relative, algorithmic, observational, and mutual information.
4. Do not compare values across changed partitions, alphabets, references, boundaries, observation maps, receivers, or calibration profiles without declaring the bridge.
5. Do not turn cross-domain or cross-repository analogy into shared mechanism.
6. Simulation output is not proof.
7. A successful fit is not a unique explanation.
8. Lean verification requires checked source and green CI.
9. Critique equations, assumptions, data, and inference, not people.
10. Do not infer truth from hash integrity, replay, storage, retrieval, consensus, recovery, transport, inference, or execution.
11. Do not infer intrinsic stored-bit energy from the Landauer erasure bound without an independently justified physical bridge.
12. Correct arithmetic is not experimental confirmation.
13. Do not infer physical ontology from graph isomorphism, visual resemblance, tetrahedral geometry, material coordination, or finite conformance.
14. Do not promote roadmap-only donor models into theorem or physical authority.
15. Do not infer semantic equivalence or epistemic promotion from BridgeCore compatibility.
16. Do not infer verification from retrieval, inference, execution, successful transport, or repeated copying.
17. Do not collapse conflict into unknown or treat verification as a truth oracle.
18. Do not treat similarity, congruence, coordinate change, receiver re-encoding, or one preserved invariant as interchangeable equivalence notions.
19. `INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE`.

## Lean

Lean remains deferred until source reproduction, notation freeze, theorem freeze, and counterexample freeze.

## Read next

1. `AGENTS.md`
2. `docs/CLAIMS.md`
3. `docs/NONCLAIMS.md`
4. `docs/REPRODUCIBILITY.md`
5. `theory/RELATION_CALCULUS.md`
6. `theory/GRAPH_REALIZATION.md`
7. `machine/graph_realization_contract.json`
8. `machine/graph_realization_results.json`
9. `scripts/validate_graph_realization.py`
10. `experiments/run_graph_realization.py`
11. `theory/BRIDGE_CORE.md`
12. `machine/bridge_core_contract.json`
13. `machine/bridge_core_results.json`
14. `scripts/validate_bridge_core.py`
15. `experiments/run_bridge_core.py`
16. `theory/EPISTEMIC_BRIDGE.md`
17. `machine/epistemic_bridge_contract.json`
18. `machine/epistemic_bridge_results.json`
19. `scripts/validate_epistemic_bridge.py`
20. `experiments/run_epistemic_bridge.py`
21. `theory/REPRESENTATION_CALCULUS.md`
22. `machine/representation_contract.json`
23. `machine/representation_results.json`
24. `scripts/validate_representation_calculus.py`
25. `experiments/run_representation_calculus.py`
26. `theory/CROSS_REPO_RESULTS.md`
27. `research/CROSS_REPO_PATTERN_ATLAS.md`
28. `machine/cross_repo_patterns.json`
29. `machine/cross_repo_results.json`
30. `research/vopson/CORPUS.md`
31. `research/vopson/CLAIM_GRAPH.md`
32. `research/vopson/DEFINITIONS.md`
33. `ROADMAP.md`
