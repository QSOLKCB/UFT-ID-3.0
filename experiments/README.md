# Experiments

This directory contains deterministic reproductions, counterexamples,
representation tests, and later empirical audits.

## Required experiment contract

Every experiment declares, where applicable:

```text
experiment_id
claim_target
claim_class
source publication and exact locator
input provenance and hashes
software/runtime versions
random seed or statement of determinism
preprocessing
state representation
information functional
observation/partition/reference contract
system boundary and sources
null model
primary endpoint
expected falsifier
output hashes
scope limits
```

## Shared finite primitives

Use `experiments/lib/information.py` for the current finite probability-vector,
Shannon entropy, row-stochastic, and coarse-graining contracts. A source-specific
reproduction may intentionally use a different definition, but the departure
must be explicit.

Scientific invariants use `require(...)` or another explicit exception. Do not
use ordinary Python `assert`, because `python -O` removes it.

## Current executable suites

```text
experiments/
├── lib/
│   └── information.py
├── counterexamples/
│   └── finite_entropy_signs/run.py
├── representation/
│   └── coarse_graining/run.py
├── reproduction/
│   └── vopson_2026_polygons/run.py
└── run_pr2.py
```

The historical runner name `run_pr2.py` is retained for compatibility. Receipt
version 1.1.0 identifies the current finite-adversarial suite and hashes shared
source dependencies as well as experiment scripts and results.

## Reproduction before modification

First reproduce the source definition and reported result. Only after a match,
or a documented explanation of the mismatch, should adversarial variants run.

## Counterexample standard

A counterexample must include the exact proposition, evidence that all premises
are satisfied, the smallest practical state space, no irrelevant complexity,
and a plain-language scope statement. An example outside the target domain is
not counted.

## Representation sweep

For entropy-direction claims, test where meaningful bijective relabelling,
lossless recoding, alphabet grouping, window/partition choices, many-to-one
coarse-graining, reference measures, observer maps, and boundary/source terms.
Coordinate changes must be distinguished from genuinely different observables.

## Bounded exhaustive work

The polygon verifier estimates ordered positive compositions as
`C(N-1,n-1)` before enumeration. Requests above the machine-contract ceiling
fail closed. Use analytic extrema for large inputs unless a deliberately large
exhaustive run is separately justified.

## Determinism and receipts

If an experiment can be deterministic, it should be. If randomness is
necessary, record the generator and seed. `experiments/run_pr2.py` emits source
hashes, result hashes, runtime metadata, and a suite fingerprint. CI retains the
JSON outputs as workflow artifacts.

## Artifact policy

Large generated outputs are not committed casually. Prefer scripts, fixtures,
manifests, hashes, and archived release bundles. See
`docs/REPRODUCIBILITY.md`.
