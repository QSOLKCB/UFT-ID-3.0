# Experiments

This directory will contain deterministic reproductions, counterexamples, and empirical tests.

## Rules

Every experiment must declare:

```text
experiment_id
claim_target
source_publication
input provenance
input hashes
software/runtime versions
random seeds or statement of determinism
preprocessing
state representation
information functional
system boundary
null model
primary endpoint
expected falsifier
output hashes
```

## Planned suites

```text
experiments/
├── reproduction/
│   ├── vopson_2019_mass/
│   ├── vopson_2021_genies/
│   ├── vopson_2022_sli/
│   ├── vopson_2022_mutations/
│   ├── vopson_2023_cross_domain/
│   ├── vopson_2025_gravity/
│   ├── vopson_2026_polygons/
│   └── vopson_2026_language/
├── counterexamples/
│   ├── entropy_increase/
│   ├── entropy_constant/
│   └── entropy_decrease/
├── representation/
│   ├── relabeling/
│   ├── recoding/
│   ├── partition_sweeps/
│   └── coarse_graining/
├── transport/
├── observer/
└── constrained_recovery/
```

Directories are created only when executable work exists. This document does not use empty folders as progress markers.

## Reproduction before modification

The first stage of every literature-targeted experiment is a faithful reproduction using the original definition and data where available.

Only after that result matches, or the mismatch is explained, should adversarial variants be run.

## Counterexample standard

A counterexample must include:

- the exact proposition being falsified;
- proof or executable verification that all stated premises are satisfied;
- the minimal state space practical;
- no irrelevant complexity;
- a plain-language explanation of why the example is inside the claim's domain.

A counterexample outside the target claim's domain is not counted.

## Representation sweep

For entropy-direction claims, test at minimum:

- bijective relabeling;
- lossless recoding;
- different alphabet groupings;
- different window/partition choices;
- many-to-one coarse-graining;
- system-boundary changes where meaningful.

Results should distinguish transformations that preserve the underlying observable from transformations that genuinely define a different observable.

## Statistical discipline

Empirical suites should include, as relevant:

- preregistered primary endpoint;
- held-out data;
- uncertainty intervals;
- multiple-comparison correction;
- sensitivity analysis;
- domain-appropriate null models;
- negative results.

## Determinism

If an experiment can be deterministic, it should be. If randomness is necessary, all pseudorandom seeds and generator versions must be recorded.

## Artifact policy

Large generated files should not be committed casually. Prefer scripts, compact fixtures, manifests, hashes, and archival releases. A later release may publish reproducibility bundles through Zenodo or another stable archive.
