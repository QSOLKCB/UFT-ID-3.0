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

Do not specialize these symbols to E8, SU(3), LQG, cognition, AGI, gravity, or
another ontology unless the target document explicitly enters an interpretive
or speculative layer.

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
repository assessment are distinct objects even where the current schema stores
them in one graph node.

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
2. Never invent a DOI, source locator, review status, or reproduction result.
3. A dependency edge records reliance, not truth.
4. `metadata-verified` is not `reproduced`.
5. `PROVED` and `COUNTEREXAMPLE` require repository-contained evidence unless
   a controlled external premise is explicitly marked established literature.
6. Human corpus tables must match their JSON authorities.
7. Static entropy ordering does not supply physical dynamics.
8. A restricted deterministic Shannon theorem is not the full published SLI.

## Reproducibility authority

Read `docs/REPRODUCIBILITY.md` before changing executable evidence.

Canonical finite information helpers live in
`experiments/lib/information.py`. Do not copy local variants of Shannon entropy
or probability validation without a source-specific reason. Scientific
invariants must use explicit exceptions, not ordinary Python `assert`, because
`python -O` removes assertions.

Polygon exhaustive work is bounded by the machine contract. Use
`analytic_extrema()` for inputs above the ceiling unless a deliberately large
exhaustive run is justified outside routine CI.

GitHub Actions must use the fixed runner and full commit SHA pins declared in
`machine/contract.json`. CI receipts are retained as workflow artifacts.

## Required validation commands

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_reproducibility.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
```

To update machine-derived Markdown tables intentionally:

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
   boundaries, or observation maps without declaring the bridge.
5. Do not turn cross-domain analogy into shared mechanism.
6. Simulation output is not proof.
7. A successful fit is not a unique explanation.
8. Lean verification requires checked source and green CI.
9. Critique equations, assumptions, data, and inference, not people.
10. Prefer exact reproduction, counterexamples, null models, sensitivity tests,
    and preregistered comparisons over rhetoric.

## Lean

Lean is deferred until source reproduction, notation freeze, theorem freeze,
and counterexample freeze. Begin later with finite admissibility, finite
lexicographic recovery, residual lemmas, discrete identities, restricted
monotonicity, and explicit finite failure cases.

## Read next

1. `AGENTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/REPRODUCIBILITY.md`
4. `docs/MILESTONES.md`
5. `experiments/README.md`
6. `theory/DEFINITIONS.md`
7. `theory/THEOREM_TARGETS.md`
8. `theory/FINITE_RESULTS.md`
9. `research/vopson/CORPUS.md`
10. `research/vopson/CLAIM_GRAPH.md`
11. `research/vopson/DEFINITIONS.md`
12. `research/vopson/REPRODUCTION_MATRIX.md`
13. `research/vopson/COUNTEREXAMPLE_MATRIX.md`
14. `research/vopson/RESPONSE_HISTORY.md`
15. `research/reports/2026-08-18-PR4-ACTION-REGISTER.md`
16. `research/VOPSON_MATRIX.md`
17. `ROADMAP.md`
