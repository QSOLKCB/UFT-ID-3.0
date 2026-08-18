# UFT-ID 3.0

**Unified Field Theory of Information Dynamics 3.0** is a research program for constraint-governed information dynamics, information balance, inference transport, observation, and deterministic recovery.

This repository is deliberately conservative about claims. UFT-ID 3.0 is not presented here as a confirmed fundamental theory of physics. The project separates formal mathematics, diagnostic methodology, empirical results, interpretation, and speculation so that no layer silently inherits authority from another.

## Core question

When an informational state changes, what exactly changed?

UFT-ID 3.0 separates at least four possibilities:

1. the underlying system state changed;
2. a constraint or recovery operation changed the state;
3. information was transported between regimes;
4. an observer, representation, or coarse-graining map changed what was accessible.

A decrease in a chosen entropy or information measure is therefore not automatically interpreted as destruction of physical information.

## Canonical abstract system

The initial canonical object is

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

where:

- `S` is the total state space;
- `A` is the admissible subspace;
- `F` is the proposed evolution;
- `Pi_lex` is deterministic recovery into `A`;
- `O` is an observation or coarse-graining map;
- `T` is a regime-transport map;
- `I` is a declared information functional;
- `C` is the constraint structure.

Earlier UFT-ID work supplies the constraint-first core: overcomplete state spaces, admissibility, residuals, quadratic tension, critical thresholds, deterministic lexicographic recovery, and impulse objects. UFT-ID 3.0 generalizes that core before committing to any particular lattice, symmetry group, physical ontology, or application domain.

## Provisional information balance program

A central research target is a balance law of the form

```text
dI/dt = production - loss - boundary_flux + constraint/recovery contribution
```

The exact functional, regularity assumptions, units, and domain of validity are not assumed in advance. The project will test when monotonic information decrease follows as a restricted case and when it does not.

## Relation to infodynamics

One explicit research target is the strongest possible scientific comparison with Melvin Vopson's published infodynamics program, including:

- the 2019 mass-energy-information equivalence proposal;
- the 2022 Second Law of Information Dynamics;
- the 2023 cross-domain extension and simulation-hypothesis argument;
- the 2025 information-theoretic gravity derivation;
- the 2026 polygon-symmetry and language-diversity applications.

The objective is not personal criticism. The objective is a reproducible theorem-and-experiment program that identifies the precise assumptions under which information monotonicity is true, false, representation-dependent, or empirically unsupported.

See [`research/VOPSON_MATRIX.md`](research/VOPSON_MATRIX.md).

## Epistemic layers

UFT-ID 3.0 uses five explicit layers:

1. **Formal Core**: definitions, lemmas, theorems, proofs, counterexamples.
2. **Diagnostic Layer**: audit constructs such as inference transport, calibration boundaries, stabilizers, and reification risk.
3. **Empirical Layer**: datasets, simulations, replications, statistical tests, and experimental results.
4. **Interpretive Layer**: mappings to physics, computation, cognition, networks, or other domains.
5. **Speculative Layer**: hypotheses that are interesting but not established by the formal or empirical layers.

Promotion between layers requires an explicit bridge argument or evidence.

## Repository map

```text
.
├── README.md
├── README4AI.md
├── AGENTS.md
├── ROADMAP.md
├── CITATION.cff
├── CONTRIBUTING.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CLAIMS.md
│   ├── NONCLAIMS.md
│   └── CORPUS.md
├── theory/
│   ├── DEFINITIONS.md
│   └── THEOREM_TARGETS.md
├── research/
│   ├── VOPSON_MATRIX.md
│   └── RESEARCH_GAPS.md
├── experiments/
│   └── README.md
└── machine/
    └── contract.json
```

## Formal verification

Lean formalization is planned, but intentionally deferred until the mathematical vocabulary and theorem targets are frozen. Formalizing unstable definitions would merely make a moving target machine-checked.

The planned Lean phase will begin with the finite-state constraint core, deterministic lexicographic recovery, restricted monotonicity results, explicit counterexamples, and transport/observation invariants.

## Design rule

> A model may be useful without being ontologically true.

Correspondingly:

```text
representation != referent
simulation != proof
numerical agreement != physical validation
cross-domain analogy != shared mechanism
self-consistency != truth
```

## Status

UFT-ID 3.0 is currently in the **canonicalization and adversarial research-design phase**. No claim in this repository should be described as established physical law unless the relevant evidence and status label explicitly support that wording.

## License

Software and repository documentation are released under the repository's MIT License unless a specific file states otherwise. Source papers retain their original licenses and are cited rather than relicensed here.
