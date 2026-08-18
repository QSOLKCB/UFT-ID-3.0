# Reproducibility and CI Evidence Contract

**Claim class:** `NONCLAIM`

This document defines how executable evidence is produced, checked, and
retained. It does not upgrade any scientific claim.

## Evidence chain

```text
primary source
  -> canonical work record
  -> exact source claim
  -> reproduction obligation
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
python scripts/validate_reproducibility.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python experiments/run_pr2.py --json
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

## Deterministic receipt

`experiments/run_pr2.py` records:

- SHA-256 hashes of every finite experiment source;
- the shared information primitive hash;
- the receipt-runner hash;
- canonical JSON result hashes;
- a suite fingerprint over the deterministic source/result hash payload;
- runtime metadata separately from deterministic results.

Runtime metadata is descriptive. The suite fingerprint is the portable identity
of the source-and-result bundle.

## CI artifacts

Every supported Python job retains an `artifacts/` evidence bundle for 30 days.
The bundle includes, as applicable:

```text
pr2-receipt.json
finite-signs.json
coarse-graining.json
polygon-audit.json
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

## Human and machine synchronization

The JSON corpus and claim graph are canonical machine authorities. Their
Markdown tables are rendered by:

```bash
python scripts/render_vopson_docs.py
```

CI checks them without modifying the tree:

```bash
python scripts/render_vopson_docs.py --check
```

## Nonclaims

This contract does not claim that deterministic output proves a physical law,
that a hash proves scientific correctness, that a complete bibliography is a
completed reproduction, that two Python versions constitute universal
portability, or that CI can replace independent scientific review.
