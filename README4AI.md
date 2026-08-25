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

The completed planned PR #14 surface requires every invariant claim to name the transformation class and its hypotheses.

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

## Information comparability authority

The completed planned PR #15 surface defines when two quantities called information are licensed to be compared under one declared specification grammar.

```text
InformationSpec = (
  source_type,
  functional,
  observation,
  unit,
  normalization,
  conditioning,
  scope
)
```

Canonical Information Comparability surfaces:

```text
machine/information_comparability_contract.json
machine/information_comparability_results.json
theory/INFORMATION_COMPARABILITY.md
scripts/validate_information_comparability.py
experiments/information_comparability/run.py
experiments/run_information_comparability.py
scripts/verify_information_comparability_artifacts.py
tests/test_information_comparability.py
```

Direct comparability requires exact equality of source type, functional, observation, unit, normalization, and conditioning plus nonempty scope overlap. Non-identical bit/base4 logarithmic specifications become comparable only through an explicit registered positive conversion.

The exact finite battery enumerates 96 `InformationSpec` values and all 9,216 ordered pairs, yielding exactly 224 directly comparable ordered pairs and 224 unit-convertible ordered pairs. It additionally checks 75 positive-scale order/sign cases and five exact power-of-two bit/base4 conversions.

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
SAME_SCALAR_CODOMAIN != COMPARABLE_INFORMATION
SAME_UNIT != COMPARABLE_INFORMATION
SAME_FUNCTIONAL != SAME_OBSERVATION
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE
POSITIVE_UNIT_CONVERSION != SEMANTIC_BRIDGE
PAIRWISE_SCOPE_COMPARABILITY != TRANSITIVE_COMPARABILITY
DIRECT_COMPARABILITY != EMPIRICAL_COMMENSURABILITY
FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY
```

## Recovery Specializations authority

The completed planned PR #16 surface specializes the generic relation core with an explicitly declared deterministic selector rather than replacing relation semantics by a function.

```text
stepRel : X -> X -> Prop
sigma   : X -> X
Sel_sigma(x,y) iff sigma(x)=y and y!=x
```

Canonical Recovery surfaces:

```text
machine/recovery_specialization_contract.json
machine/recovery_specialization_results.json
theory/RECOVERY_SPECIALIZATIONS.md
scripts/validate_recovery_specializations.py
experiments/recovery_specializations/run.py
experiments/run_recovery_specializations.py
scripts/verify_recovery_specialization_artifacts.py
tests/test_recovery_specializations.py
```

Executable normalization requires selector totality on the declared carrier, relation-sound non-fixed steps, exact selector-fixed-point/normal-state correspondence, and a natural-number rank that strictly decreases on every non-fixed selector step. Finite lexicographic recovery requires objective tuples plus an explicit final total tie-break.

The exact finite battery checks 32 total selectors, 13,890 selector/relation pairs, 4,134 relation-sound pairs, 739 relation-sound pairs with exact fixed-point/normal agreement, 9 rank-decreasing selector controls, 23 state normalization checks, and 336 lexicographic selections.

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

## Continuum, stochastic, and prevalence obligations authority

The completed planned PR #17 surface defines the additional obligations required before finite relation/recovery evidence can be promoted into stochastic, infinite-horizon, prevalence, or continuum conclusions.

Canonical CSP surfaces:

```text
machine/continuum_stochastic_prevalence_contract.json
machine/continuum_stochastic_prevalence_results.json
theory/CONTINUUM_STOCHASTIC_PREVALENCE.md
scripts/validate_continuum_stochastic_prevalence.py
experiments/continuum_stochastic_prevalence/run.py
experiments/run_continuum_stochastic_prevalence.py
scripts/verify_continuum_stochastic_prevalence_artifacts.py
tests/test_continuum_stochastic_prevalence.py
```

The layer separates relation possibility from stochastic support, existential witnesses from probability quantifiers, finite horizons from infinite-path liveness, trajectories from generating distributions, formal counterexamples from prevalence, and finite grids from continuum conclusions.

The exact finite battery checks 9 rational two-state kernels, 27 probability-mass transports, 756 finite-path masses, 81 path normalizations, 48 finite-atomic event/quantifier cases, 16 finite survival controls, 80 prevalence measure/event evaluations, and 31 finite-grid non-lifting polynomial controls.

```text
RELATION_REACHABLE != POSITIVE_PROBABILITY
EXISTS_PATH != POSITIVE_PROBABILITY
POSITIVE_PROBABILITY != ALMOST_SURE
FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS
ONE_TRAJECTORY != DISTRIBUTION
FINITE_SAMPLE_FREQUENCY != MODEL_PROBABILITY
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
PREVALENCE_REQUIRES_DECLARED_MEASURE
FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY
DISCRETIZATION_CONVERGENCE != ASSUMED_WITHOUT_ERROR_CONTROL
FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY
```

## Empirical Falsification Profile authority

The completed planned PR #18 surface defines a synthetic conformance procedure for deciding whether a calibrated profile-matched evidence record crosses one versioned scoped rejection boundary. It specializes the PR8 `FalsificationSpec` scaffold without converting synthetic fixtures, matching hashes, or procedural labels into empirical evidence or preregistration proof. Historical scheduling authority for the v3.0.0 source freeze remains PR #10 Lean observation foundation. Live post-tag authority is now `machine/roadmap_state.json` plus `machine/lean_observation_verification.json`: immutable tag `v3.0.0` is cut at `b7f51590985e60920c8b09fc9238b8aec6cfa3bc`, `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`, and arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`; both are `LEAN_VERIFIED` at formalization integration commit `bbcde19827921af4490c232bdc1edc401790d89e`, tree `b7ec78695f32a5b1cf78b416a5050627ad4f957d`, after exact merged-main `finite-adversarial` run `32876623204` and `vopson-corpus` run `32876623479` succeeded. The next ordered gate is QSOL-CONTEXT verification capture, then DOI/archive work.

```text
EmpiricalFalsificationProfile = (
  profile_id,
  hypothesis_id,
  hypothesis_version,
  claim_class,
  scope,
  observable_id,
  measurement_spec_id,
  calibration_id,
  uncertainty_model,
  prediction,
  null_model,
  rejection_rule,
  evidence_requirements,
  decision_policy,
  prior_registration_status,
  profile_version
)
```

Canonical EFP surfaces:

```text
machine/empirical_falsification_profile_contract.json
machine/empirical_falsification_profile_results.json
theory/EMPIRICAL_FALSIFICATION_PROFILE.md
scripts/validate_empirical_falsification_profile.py
experiments/empirical_falsification_profile/run.py
experiments/run_empirical_falsification_profile.py
scripts/verify_empirical_falsification_profile_artifacts.py
tests/test_empirical_falsification_profile.py
```

The decision envelope is `INVALID_EVIDENCE`, `INCONCLUSIVE`, `REJECTED_IN_SCOPE`, or `NOT_REJECTED_IN_SCOPE`. Profile identity binds the rejection threshold and all decision-bearing metadata, but it does not prove registration chronology. The synthetic profile fixes `prior_registration_status=EXTERNAL_UNVERIFIED_ASSUMPTION`; its scoped rejection label is not an empirically licensed rejection until independent immutable preregistration provenance is verified.

The exact synthetic battery checks 15 valid interval decisions, 60 invalid-evidence mutations, 15 model-fit memberships with 3 ambiguous observations, and 3 profile-fingerprint separation pairs.

```text
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
SYNTHETIC_FIXTURE != EMPIRICAL_EVIDENCE
FAILURE_TO_REJECT != CONFIRMATION
EMPIRICAL_FIT != UNIQUE_EXPLANATION
REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION
NUMERIC_OBSERVATION != CALIBRATED_MEASUREMENT
MISSING_UNCERTAINTY != ZERO_UNCERTAINTY
POST_HOC_THRESHOLD != PREREGISTERED_REJECTION_RULE
PROFILE_FINGERPRINT != PREREGISTRATION_PROOF
INCONCLUSIVE != NOT_REJECTED
REPRODUCIBLE_ANALYSIS != INDEPENDENT_REPLICATION
FINITE_EMPIRICAL_PROFILE_CONFORMANCE != GENERAL_STATISTICAL_INFERENCE
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
python scripts/validate_lean_observation_foundation.py
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
python scripts/validate_continuum_stochastic_prevalence.py
python experiments/continuum_stochastic_prevalence/run.py --json
python experiments/run_continuum_stochastic_prevalence.py --json
python scripts/validate_empirical_falsification_profile.py
python experiments/empirical_falsification_profile/run.py --json
python experiments/run_empirical_falsification_profile.py --json
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
8. Lean verification requires checked source, exact source binding, an explicit imported-axiom report, and green pinned CI.
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
20. Do not infer information comparability from shared vocabulary, scalar codomain, unit, functional name, or numeric equality alone.
21. A unit conversion does not supply an observation, semantic, epistemic, empirical, or physical bridge.
22. `COMPARABLE != IDENTICAL_SPEC`.
23. `PAIRWISE_SCOPE_COMPARABILITY != TRANSITIVE_COMPARABILITY`.
24. Do not reinterpret a generic relation as a deterministic selector without an explicit specialization.
25. Determinism does not establish relation soundness or termination.
26. A selector result does not establish base-relation confluence or a unique reachable normal form.
27. Objective minimization is not unique selection without an explicit final total tie-break.
28. An executable normalizer is not empirical or physical recovery evidence.
29. Relation reachability or path existence does not imply positive stochastic probability.
30. Positive probability does not imply almost-sure truth.
31. Finite-horizon success does not establish infinite-path liveness.
32. One trajectory or finite sample frequency does not identify the generating distribution.
33. A finite counterexample refutes a universal claim but does not determine prevalence.
34. Prevalence requires a declared population measure or sampling model.
35. Finite-grid agreement does not establish continuum equality or convergence without explicit regularity and error control.
36. A formal counterexample is not empirical falsification without calibrated profile-matched evidence.
37. A synthetic fixture is not empirical evidence.
38. Failure to reject is not confirmation.
39. A scoped rejection does not automatically refute a broader theory or adjacent hypothesis.
40. A numeric observation is not a calibrated measurement merely because it has a value.
41. Missing uncertainty is not zero uncertainty.
42. Changing a rejection threshold changes the decision profile identity; a post-hoc threshold is not the original preregistered rule.
43. A profile fingerprint binds content but does not prove preregistration chronology.
44. `INCONCLUSIVE != NOT_REJECTED_IN_SCOPE`.
45. Reproducible analysis does not imply independent replication.

## Lean

PR #10 Lean observation foundation is the historical source-freeze authority. Source batch `LEAN-OBS-BATCH-001` remains frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; the same v3.0.0 freeze records `UFT-OBS-005` as deferred from batch 001 rather than dropped.

Live post-tag verification authority is `machine/lean_observation_verification.json`. Immutable source tag `v3.0.0` resolves to commit `b7f51590985e60920c8b09fc9238b8aec6cfa3bc` and tree `966bdf47596832f792e77d619b33222f4cf60c8d`. Lean is pinned to `v4.33.1`, mathlib to `0df444a360eaa60ab8c11dca51a86af692955474`, and the Lean release archive is SHA256-bound. `LEAN-OBS-BATCH-001` implements `UFT-OBS-001` through `004`; arithmetic `LEAN-OBS-BATCH-002` implements `UFT-OBS-005`. Both batches are `LEAN_VERIFIED`, bound to formalization integration commit `bbcde19827921af4490c232bdc1edc401790d89e`, tree `b7ec78695f32a5b1cf78b416a5050627ad4f957d`, exact merged-main `finite-adversarial` run `32876623204`, and exact merged-main `vopson-corpus` run `32876623479`. The pinned Python 3.12 Vopson lane completed `lake build UFTID` successfully and the retained kernel `#print axioms` audit passed. This verified scholarly layer does not rewrite the immutable `v3.0.0` source release. The next ordered gate is QSOL-CONTEXT verification capture, then DOI/archive work.

Canonical source-freeze and live implementation surfaces:

```text
machine/lean_observation_foundation_contract.json
machine/lean_observation_verification.json
machine/roadmap_state.json
theory/LEAN_OBSERVATION_FOUNDATION.md
scripts/validate_lean_observation_foundation.py
scripts/verify_lean_observation_axioms.py
tests/test_lean_observation_foundation.py
```

```text
MATHEMATICAL_PROOF != LEAN_PROOF
SOURCE_THEOREM != LEAN_ARTIFACT
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
IMPORTED_AXIOM != UFT_ID_THEOREM_RESULT
```

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
26. `theory/INFORMATION_COMPARABILITY.md`
27. `machine/information_comparability_contract.json`
28. `machine/information_comparability_results.json`
29. `scripts/validate_information_comparability.py`
30. `experiments/run_information_comparability.py`
31. `theory/RECOVERY_SPECIALIZATIONS.md`
32. `machine/recovery_specialization_contract.json`
33. `machine/recovery_specialization_results.json`
34. `scripts/validate_recovery_specializations.py`
35. `experiments/run_recovery_specializations.py`
36. `theory/CONTINUUM_STOCHASTIC_PREVALENCE.md`
37. `machine/continuum_stochastic_prevalence_contract.json`
38. `machine/continuum_stochastic_prevalence_results.json`
39. `scripts/validate_continuum_stochastic_prevalence.py`
40. `experiments/run_continuum_stochastic_prevalence.py`
41. `theory/EMPIRICAL_FALSIFICATION_PROFILE.md`
42. `machine/empirical_falsification_profile_contract.json`
43. `machine/empirical_falsification_profile_results.json`
44. `scripts/validate_empirical_falsification_profile.py`
45. `experiments/empirical_falsification_profile/run.py`
46. `theory/CROSS_REPO_RESULTS.md`
47. `research/CROSS_REPO_PATTERN_ATLAS.md`
48. `machine/cross_repo_patterns.json`
49. `machine/cross_repo_results.json`
50. `research/vopson/CORPUS.md`
51. `research/vopson/CLAIM_GRAPH.md`
52. `research/vopson/DEFINITIONS.md`
53. `ROADMAP.md`
