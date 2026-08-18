# UFT-ID 3.0

**Unified Field Theory of Information Dynamics 3.0** is a constraint-governed
research programme for information dynamics, admissibility, observation,
transport, and deterministic recovery.

The repository does not present UFT-ID 3.0 as a confirmed fundamental physical
theory. Formal mathematics, diagnostics, executable evidence, interpretation,
speculation, and nonclaims have separate authority surfaces.

## Core question

When an informational description changes, what changed?

UFT-ID distinguishes underlying state dynamics, constraint or recovery
dynamics, transport between regimes, observation or coarse-graining, and
boundary/source exchange. A decrease in one selected entropy is not
automatically physical destruction of information.

## Canonical abstract system

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

No component becomes physical merely because it appears in the tuple.

## Current theorem-level direction

```text
No universal information-direction theorem exists without fixing the state
model, dynamics, information functional, observation map, reference measure,
partition/coarse-graining, boundaries, and source assumptions.
```

Within a declared class, monotonicity may be proved from actual dynamics. For
example, finite deterministic processing satisfies `H(f(X)) <= H(X)`, while a
broader class containing stochastic mixing, permutations, and many-to-one maps
admits positive, zero, and negative Shannon-entropy changes.

The generic information-balance expression remains a model template. It is not
predictive physics until every term is independently operationalized and the
model makes held-out predictions.

## Executable finite results

`theory/FINITE_RESULTS.md` records the proved or counterexample surface.
Executable witnesses include:

- two-state positive/zero/negative Shannon-change cases;
- one entropy-preserving fine trajectory with opposite observed signs under two
  coarse-grainings;
- proposal/recovery information decomposition;
- admissible recovery that increases a declared information functional;
- the bounded 2026 polygon multiplicity-extremum audit.

Machine metadata is in `machine/finite_results.json`.

## Vopson audit programme

The public scholarly target corpus is under `research/vopson/`. It keeps
published work, source claim, logical dependency, exact reproduction
obligation, repository evidence, UFT-ID assessment, and claim class distinct.

Corpus inclusion is not endorsement. A dependency edge records reliance, not
truth. The audit tracks mass-energy-information equivalence, SLI, genetics,
gravity, symmetry, language diversity, simulation interpretations, errata, and
published responses.

## Validation quick start

Supported CI runtimes are Python 3.12 and 3.13 on `ubuntu-24.04`.

```bash
python -m compileall -q experiments scripts tests
python scripts/render_vopson_docs.py --check
python scripts/validate_vopson_corpus.py
python scripts/validate_reproducibility.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
```

See `docs/REPRODUCIBILITY.md` for the evidence-chain contract and
`docs/MILESTONES.md` for the evidence-gated project sequence.

## Repository map

```text
.
├── README.md / README4AI.md / AGENTS.md
├── MATHS.md
├── ROADMAP.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CLAIMS.md
│   ├── CORPUS.md
│   ├── MILESTONES.md
│   ├── NONCLAIMS.md
│   └── REPRODUCIBILITY.md
├── theory/
│   ├── DEFINITIONS.md
│   ├── THEOREM_TARGETS.md
│   └── FINITE_RESULTS.md
├── experiments/
│   ├── lib/
│   ├── counterexamples/
│   ├── representation/
│   ├── reproduction/
│   └── run_pr2.py
├── research/
│   ├── reports/
│   ├── vopson/
│   ├── RESEARCH_GAPS.md
│   └── VOPSON_MATRIX.md
├── scripts/
│   ├── render_vopson_docs.py
│   ├── validate_reproducibility.py
│   └── validate_vopson_corpus.py
├── machine/
│   ├── contract.json
│   └── finite_results.json
├── tests/
└── .github/workflows/
```

## Evidence and CI

Workflows use read-only permissions, a fixed runner, a Python-version matrix,
full-SHA action pins, compilation, normal and optimized tests, and retained
JSON evidence artifacts. Scientific invariants use explicit exceptions rather
than ordinary `assert` statements.

## Epistemic layers

1. **Formal Core**: definitions, proofs, counterexamples.
2. **Diagnostic**: audit and transport constructs.
3. **Empirical**: data, reproductions, simulations, experiments.
4. **Interpretive**: domain mappings and explanatory proposals.
5. **Speculative**: hypotheses not established by the prior layers.

Promotion requires evidence appropriate to the target layer.

## Formal verification

Lean remains deferred until notation, theorem statements, and canonical
counterexamples survive source reproduction and adversarial review. Lean can
verify deductions from assumptions; it cannot establish the physical truth of
those assumptions.

## Design rule

> A model may be useful without being ontologically true.

```text
representation != referent
simulation != proof
numerical agreement != physical validation
cross-domain analogy != shared mechanism
self-consistency != truth
```

## Status

The project is in the **reproducibility and source-fidelity phase**. The next
scientific target is an exact reconstruction of the 2019 mass-energy-information
calculation, separating reproduced arithmetic from its additional physical
premises.

## License

Software and repository documentation are MIT-licensed unless a file states
otherwise. Cited papers and datasets retain their original licences.
