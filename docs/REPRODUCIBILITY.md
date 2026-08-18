# Reproducibility and CI Evidence Contract

**Claim class:** `NONCLAIM`

This document defines how executable evidence is produced, checked, and
retained. It does not upgrade any scientific claim.

## Evidence chain

```text
primary source / pinned public repository contract
  -> canonical source or pattern record
  -> exact source claim / abstract pattern
  -> reproduction or theorem obligation
  -> executable derivation / experiment
  -> deterministic result and source hashes
  -> repository assessment
  -> canonical claim class
  -> CI validation and retained artifact
```

A green workflow establishes that the declared repository checks passed for a
particular commit and runtime. It does not establish a physical interpretation.

## Supported runtime

- GitHub runner: `ubuntu-24.04`
- Python: `3.12` and `3.13`
- Current finite experiments and validators: Python standard library only

## Required local validation

Run from the repository root:

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

`python -O` is intentional. Scientific checks must not depend on ordinary
Python `assert` statements, because optimized execution removes them.

## Shared information primitives

Canonical finite probability and information helpers live in:

```text
experiments/lib/information.py
```

The shared module fixes the current finite-experiment contract for probability
validation, finite-value rejection, absolute normalization tolerance, base-2
Shannon entropy, row-stochastic maps, complete disjoint coarse-grainings, and
explicit fail-closed scientific invariants.

A source reproduction may use a different definition only when the source
requires it and the difference is documented explicitly.

## Deterministic receipts

`experiments/run_pr2.py` records the finite entropy/polygon evidence surface.
`experiments/run_cross_repo.py` records the cross-repository finite formal-pattern
surface.

Both receipt families bind deterministic source files and canonical result
payloads while keeping runtime metadata separate from the portable suite
fingerprint.

For the cross-repository suite, the deterministic source set includes:

```text
machine/cross_repo_patterns.json
machine/cross_repo_results.json
theory/AUXILIARY_CONTRACTS.md
theory/CROSS_REPO_RESULTS.md
experiments/cross_repo/run.py
experiments/run_cross_repo.py
shared experiment package / information primitives
```

Runtime metadata is descriptive. A suite fingerprint identifies the declared
source-and-result bundle; it does not establish semantic truth.

## Cross-repository provenance pins

`machine/cross_repo_patterns.json` records a source repository, `main` ref,
source path, and exact Git blob SHA for every imported or quarantined pattern.

These are **snapshot provenance pins**. Routine UFT-ID CI validates their local
shape and consistency but does not perform network fetches to prove that every
remote repository still has the same current mainline state.

Therefore:

```text
PINNED_SOURCE_SNAPSHOT != LIVE_REMOTE_FRESHNESS
```

When current source state matters, re-fetch the public repository and update the
registry deliberately. Open-PR-only behavior and private repositories are not
accepted as positive cross-repository pattern authority.

## CI artifacts

Every supported Python job retains an `artifacts/` evidence bundle for 30 days.
The bundle includes, as applicable:

```text
pr2-receipt.json
finite-signs.json
coarse-graining.json
polygon-audit.json
cross-repo-pattern-validation.json
cross-repo-receipt.json
vopson-corpus-validation.json
vopson-doc-sync.json
reproducibility-validation.json
```

Generated CI artifacts are evidence from a workflow run. They are not committed
back into source control automatically.

## GitHub Actions provenance

Workflow actions must be pinned to full 40-character commit SHAs recorded in
`machine/contract.json`. Mutable major-version tags are forbidden by
`scripts/validate_reproducibility.py`.

Checkout credentials are not persisted after checkout, and workflows use
read-only repository permissions.

## Bounded exhaustive computation

The polygon audit uses exhaustive positive-composition enumeration only below a
declared work ceiling. The ordered work estimate is `C(N - 1, n - 1)`.
Requests above the ceiling fail before enumeration. Analytic extrema remain
available through `analytic_extrema(total, parts)`.

The cross-repository minimum-basis fixture is finite and exhaustive over a tiny
sealed candidate family. It is evidence for CR5's declared finite hypotheses,
not a claim that arbitrary minimum-cover problems are computationally cheap.

## Human and machine synchronization

The Vopson JSON corpus and claim graph are canonical machine authorities. Their
Markdown tables are rendered by:

```bash
python scripts/render_vopson_docs.py
```

CI checks them without modifying the tree:

```bash
python scripts/render_vopson_docs.py --check
```

The cross-repository pattern atlas is a human diagnostic explanation of
`machine/cross_repo_patterns.json`; result authority is split explicitly between
`theory/CROSS_REPO_RESULTS.md` and `machine/cross_repo_results.json`. The
validator checks identifiers, source classes, privacy/open-PR exclusions, claim
classes, and result dependencies.

## Nonclaims

This contract does not claim that deterministic output proves a physical law,
that a hash proves scientific correctness, that a public software invariant is
a physical law, that a pinned source blob proves live remote freshness, that a
complete bibliography is a completed reproduction, that two Python versions
constitute universal portability, or that CI can replace independent scientific
review.
