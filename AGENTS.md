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
4. for Vopson work, read the canonical corpus, claim graph, reproduction matrix,
   counterexample matrix, and response history;
5. locate the primary source or derivation being changed;
6. state the single canonical claim class being modified;
7. preserve provenance, scope, and uncertainty;
8. add or update tests, counterexamples, citations, machine records, and
   retained evidence as appropriate;
9. run the complete validation sequence before requesting review.

`MATHS.md` is non-authoritative. Do not promote an idea from it without typed
symbols, explicit assumptions, the nearest established result, and an
adversarial companion question.

## Mandatory validation sequence

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_reproducibility.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
```

Authority changes are incomplete while any command fails.

## Source hierarchy

Prefer primary peer-reviewed literature, primary preprints with explicit
status, official datasets and code, source papers in the UFT-ID lineage, and
secondary commentary only for history or interpretation.

Never invent a DOI, page/equation locator, dataset identity, peer-review status,
or reproduction result.

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

## Repository hygiene

- Keep generated artifacts out of source directories.
- Keep licences and provenance explicit.
- Prefer stable identifiers over copied paper binaries.
- Do not rewrite historical sources into agreement with the current theory.
- Record disagreement and supersession.
- Keep machine and human authority surfaces synchronized.
