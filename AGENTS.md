# AGENTS.md

## Purpose

This repository is a research programme, not a claim amplifier. Agents must
preserve the boundary between mathematics, diagnostics, executable evidence,
interpretation, speculation, and nonclaims.

## Required operating sequence

Before changing theory or evidence:

1. read `README4AI.md`;
2. read `docs/CLAIMS.md`, `docs/NONCLAIMS.md`, and
   `docs/REPRODUCIBILITY.md`;
3. read `MATHS.md` for staged ideas and the authoritative `theory/` surfaces;
4. for cross-repository formalization, read `research/CROSS_REPO_PATTERN_ATLAS.md`,
   `machine/cross_repo_patterns.json`, `theory/AUXILIARY_CONTRACTS.md`, and
   `theory/CROSS_REPO_RESULTS.md`;
5. for Vopson work, read the canonical corpus, claim graph, reproduction matrix,
   counterexample matrix, and response history;
6. locate the primary source, repository contract, or derivation being changed;
7. state the single canonical claim class being modified;
8. preserve provenance, scope, and uncertainty;
9. add or update tests, counterexamples, citations, machine records, and
   retained evidence as appropriate;
10. run the complete validation sequence before requesting review.

`MATHS.md` is non-authoritative. Do not promote an idea from it without typed
symbols, explicit assumptions, the nearest established result, and an
adversarial companion question.

## Mandatory validation sequence

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_cross_repo_patterns.py
python scripts/validate_reproducibility.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
python experiments/run_cross_repo.py --json
```

Authority changes are incomplete while any command fails.

## Source hierarchy

Prefer primary peer-reviewed literature, primary preprints with explicit
status, official datasets and code, source papers in the UFT-ID lineage, and
secondary commentary only for history or interpretation.

Public merged QSOLKCB repository contracts may be used as implementation
examples for mathematical or methodological patterns. They are not scientific
literature and do not become physical evidence merely because several systems
share the same software invariant.

Never invent a DOI, page/equation locator, dataset identity, peer-review status,
repository source state, blob identity, or reproduction result.

## Cross-repository formalization rule

The canonical registry is `machine/cross_repo_patterns.json`.

- Import **structure, not ontology**.
- A positive pattern source must be public, inspectable, pinned to `main`, and
  recorded with an exact Git blob SHA at the registry snapshot.
- Do not register private repositories in the public UFT-ID pattern registry.
- Do not promote open-PR-only behavior. Wait until the behavior exists on the
  source repository's merged mainline.
- The registry is snapshot provenance. Local CI does not prove remote freshness;
  re-fetch the source when freshness matters.
- Quarantined lineage may motivate a counterexample, dimensional audit, or
  bridge stress test but may not back a positive result.
- `SOFTWARE_CONTRACT != PHYSICAL_LAW`.
- `IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM`.
- `CONTENT_IDENTITY != TRUTH`.
- `RECOVERY != EPISTEMIC_PROMOTION`.
- `FORMAL_PROOF != IMPLEMENTATION_CONFORMANCE`.
- `IMPLEMENTATION_CONFORMANCE != EMPIRICAL_VALIDATION`.
- `EMPIRICAL_VALIDATION != PHYSICAL_ONTOLOGY`.
- `ADJACENT_TRUTH != INHERITED_TRUTH`.

When translating a repository pattern into UFT-ID, state:

```text
source repository contract
abstract typed pattern
UFT-ID definition/theorem/result mapping
preserved structure
lost or deliberately ignored application semantics
prohibited inference
```

A repository pattern is valuable when it sharpens hypotheses or supplies a
small falsifier. It is not valuable merely because it gives UFT-ID more nouns.

## Mathematical discipline

- Define state space, measure, dynamics, information functional, observation
  map, partition/reference, and boundary before comparing information.
- Keep discrete, continuous, and stochastic time models separate.
- State regularity assumptions before derivatives.
- Check units and dimensions.
- Keep scalar and vector residuals separately typed.
- Distinguish state entropy from entropy production.
- Distinguish closed, isolated, and open systems.
- Distinguish boundary flux from internal production.
- Distinguish coarse-graining from physical dissipation.
- Distinguish inaccessibility from destruction.
- Distinguish content identity from semantic truth.
- Distinguish receiver preservation of one observable from global information
  preservation.
- Index thresholds/classifiers by their calibration profile when calibration
  matters.
- Record counterexamples and negative results.

## Executable-science discipline

- Use `experiments/lib/information.py` for shared finite probability and Shannon
  primitives unless a source reproduction explicitly requires another contract.
- Do not use ordinary Python `assert` for scientific invariants. Use explicit
  fail-closed exceptions so checks survive `python -O`.
- Validate malformed inputs, not only headline examples.
- Record deterministic source and result hashes.
- Keep runtime metadata separate from deterministic fingerprints.
- Bound exhaustive computation before allocation or enumeration.
- Generated CI artifacts belong to the workflow evidence chain and must not be
  silently committed as canonical source.
- A deterministic receipt does not make an external stochastic system replayable.

## CI provenance

- GitHub Actions must be pinned to the full commit SHAs declared in
  `machine/contract.json`.
- Use the declared fixed runner and Python matrix.
- Checkout must use `persist-credentials: false`.
- Workflow permissions remain read-only unless a separate reviewed write job is
  strictly necessary.
- Compile before tests.
- Run normal and optimized Python tests.
- Retain JSON validation and experiment receipts as workflow artifacts.

## Cross-domain rule

A shared mathematical pattern is not evidence of shared substrate or cause.
Declare:

```text
source objects -> target objects
source dynamics -> target dynamics
preserved structure -> target invariant
lost structure -> discarded / undefined structure
measurement -> observable quantity
```

Without this bridge, classify the correspondence `INTERPRETIVE` or
`SPECULATIVE`.

## Adversarial review rule

For every major theorem or empirical claim ask which assumption makes it false,
whether it survives relabelling or representation change, whether the sign is
partition/reference/alphabet/boundary dependent, whether a null model
reproduces it, whether the metric was selected post hoc, and whether the result
is causal, descriptive, or correlational.

For cross-repository abstractions also ask whether the claimed theorem is just
a renamed software invariant, whether a receiver choice manufactured the
result, whether a threshold is calibration-local, and whether successful
recovery/integrity/replay was silently promoted into truth.

## Vopson corpus rule

Treat publications as scientific targets, never people as targets. ORCID
`0000-0002-8073-5538` is a bibliographic anchor only.

- `corpus.json` is the work registry.
- `CLAIM_GRAPH.json` is the dependency/assessment graph.
- Source recording is not UFT-ID endorsement.
- Metadata verification is not reproduction.
- MEI, SLI, genetics, gravity, symmetry, language, and simulation remain
  distinct claim tracks.
- Errata, qualifications, responses, and reformulations are first-class records.
- Dependency edges record reliance, not truth.
- Source-specific counterexamples retain exact locator and scope.
- Human tables are generated/checkable from machine authorities.

## Formal verification rule

Lean remains deferred. When it begins, compile it in CI, map theorem IDs to the
paper, distinguish imported theorems from UFT-ID results, and never claim an
ontology is proved merely because an abstract theorem compiles.

Cross-repository candidates that are especially suitable for later finite Lean
work include coprime cyclic traversal and finite minimum sufficient-basis
selection. Their software inspirations do not become proof premises.

## Repository hygiene

- Keep generated artifacts out of source directories.
- Keep licences and provenance explicit.
- Prefer stable identifiers over copied paper binaries.
- Do not rewrite historical sources into agreement with the current theory.
- Record disagreement and supersession.
- Keep machine and human authority surfaces synchronized.
