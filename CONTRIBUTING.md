# Contributing to UFT-ID 3.0

Contributions are welcome when they make the theory more precise, more reproducible, easier to falsify, or harder to overstate.

## Good contributions

Examples include:

- exact reproductions of cited papers;
- minimal counterexamples;
- corrected derivations;
- unit and dimensional audits;
- null models;
- sensitivity analyses;
- formal definitions;
- theorem proofs or disproofs;
- provenance improvements;
- literature corrections using primary sources;
- deterministic test harnesses;
- negative results.

## Claim status is mandatory

When proposing a scientific change, identify its status:

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

A pull request that upgrades a claim's authority must contain the evidence required for that upgrade.

## Source discipline

Prefer primary sources. Include DOI or stable source identifiers where possible.

Do not cite a blog, social post, encyclopedia, or AI-generated summary as the technical authority when the original paper is available.

## Reproduction contributions

A reproduction PR should state:

- source paper and version;
- equation or result reproduced;
- input dataset and provenance;
- software/runtime versions;
- random seed where applicable;
- expected result;
- observed result;
- discrepancy, if any;
- whether the discrepancy changes a scientific conclusion.

## Counterexample contributions

A counterexample must name the exact proposition it addresses and show that the example satisfies the proposition's premises.

Small counterexamples are preferred. A five-state example that kills a universal theorem is more useful than a million-state simulation that merely looks suggestive.

## Vopson-related contributions

Critique the published claim, equation, data, experimental design, or inference. Do not submit personal attacks.

Before claiming a Vopson result fails, reproduce the original calculation or explain exactly why faithful reproduction is impossible.

## Cross-domain contributions

If mapping UFT-ID into a new domain, provide an explicit bridge:

```text
UFT-ID object -> domain object
UFT-ID dynamics -> domain dynamics
preserved structure -> domain invariant
measurement -> observable quantity
```

Without such a bridge, label the contribution `INTERPRETIVE` or `SPECULATIVE`.

## Lean contributions

Lean formalization is currently deferred. Please do not add placeholder Lean files until the roadmap's notation-and-theorem freeze is complete.

When the Lean phase opens, every formal theorem must point to the corresponding paper theorem identifier and compile in CI.

## Pull request checklist

Before opening a PR:

- read `README4AI.md` and `AGENTS.md`;
- check `docs/CLAIMS.md` and `docs/NONCLAIMS.md`;
- keep unrelated changes out of the PR;
- document new external sources;
- add tests or executable checks when appropriate;
- state limitations;
- avoid generated binary clutter;
- confirm JSON/YAML/metadata files parse correctly.

## Style

Prefer precise language over grand claims. Prefer a theorem with narrow hypotheses over an impressive sentence with none.
