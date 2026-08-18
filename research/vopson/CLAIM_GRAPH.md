# Vopson Claim and Dependency Graph

**Status:** claim-routing map. Dependencies record reliance, not truth.

The graph deliberately separates source claims, external premises, UFT-ID assessments, and interpretive inferences. Each UFT-ID assessment has exactly one canonical claim class.

The assessment table below is deterministically checked against `CLAIM_GRAPH.json`. A machine-node change without the corresponding human-table change fails CI.

## High-level dependency map

```text
Landauer erasure scale + E=mc^2
                    |
                    v
        stored-bit mass proposal (MEI)
          |             |              |
          v             v              v
information catastrophe  particle info  annihilation photons
                              |
                              +------------------+
                                                 |
GENIES method -> proposed mutation law -> SLI 2022 -> SLI 2023 cross-domain
                                                 |       |         |
                                                 |       |         +-> simulation inference
                                                 |       +-> atomic / cosmology
                                                 +-> polygon / language
                                                 |
MEI + particle info + SLI + Planck-area counting + entropic-force relation
                                                 |
                                                 v
                                              gravity
```

## Reading rules

- `requires`: the downstream claim uses the upstream premise.
- `extends`: the downstream work broadens or specialises the upstream programme.
- `supports`: the upstream example is used as evidence, but is not necessarily logically sufficient.
- `interprets`: the downstream conclusion is an interpretation rather than a direct theorem.
- `tests`: a comparison result probes a source claim without claiming exact source reproduction.

## Current assessment summary

| Node | Claim | Kind | UFT-ID class | Assessment status | Source |
|---|---|---|---|---|---|
| `EXT-LANDAUER` | Landauer erasure bound | `external-premise` | `PROVED` | `established-literature` | `10.1147/rd.53.0183` |
| `EXT-E-MC2` | Mass-energy equivalence | `external-premise` | `PROVED` | `established-literature` | - |
| `EXT-SHANNON` | Finite Shannon entropy | `external-premise` | `DEFINITION` | `established-literature` | `10.1002/j.1538-7305.1948.tb01338.x` |
| `EXT-PLANCK-AREA` | Planck-area cell counting | `external-premise` | `INTERPRETIVE` | `application-assumption` | - |
| `EXT-ENTROPIC-FORCE` | Entropic-force relation | `external-premise` | `INTERPRETIVE` | `application-assumption` | - |
| `EXT-LANGUAGE-DOMINANCE` | Dominant-category population dynamics | `external-premise` | `INTERPRETIVE` | `model-assumption` | - |
| `CL-MEI-BIT-MASS` | Stored information bit has finite mass | `source-claim` | `THEOREM_TARGET` | `physical-hypothesis-unresolved` | `VOP-2019-MEI` |
| `CL-INFO-CATASTROPHE` | Digital information growth produces a future information catastrophe | `source-claim` | `THEOREM_TARGET` | `dependent-extrapolation-pending-reproduction` | `VOP-2020-CATASTROPHE`, `VOP-2020-CATASTROPHE-ERRATUM`, `VOP-2020-CATASTROPHE-DATA` |
| `CL-PARTICLE-INFO` | Visible-matter particles encode a quantifiable information content | `source-claim` | `THEOREM_TARGET` | `quantitative-model-pending-reproduction` | `VOP-2021-VISIBLE-MATTER` |
| `CL-ANNIHILATION-PHOTONS` | Annihilation emits additional information-erasure photons | `source-claim` | `THEOREM_TARGET` | `experimental-prediction-unresolved` | `VOP-2022-MEI-EXPERIMENT` |
| `CL-GENIES-METHOD` | Windowed m-block entropy spectra detect genome differences | `source-claim` | `THEOREM_TARGET` | `method-reproduction-pending` | `VOP-2021-GENIES` |
| `CL-GENETIC-LAW` | Genome mutation dynamics tend to reduce information entropy | `source-claim` | `THEOREM_TARGET` | `empirical-and-causal-reproduction-pending` | `VOP-2022-GENETIC-LAW` |
| `CL-SLI-PUBLISHED` | Second Law of Information Dynamics | `source-claim` | `THEOREM_TARGET` | `exact-source-domain-reproduction-pending` | `VOP-2022-SLI` |
| `CL-SLI-XDOMAIN` | Cross-domain SLI extension | `source-claim` | `THEOREM_TARGET` | `bridge-audit-pending` | `VOP-2023-SLI-XDOMAIN`, `VOP-2023-NONEQ` |
| `CL-ATOMIC-HUND` | Infodynamics explains maximum-spin atomic configurations | `source-claim` | `INTERPRETIVE` | `encoding-result-not-yet-causal` | `VOP-2023-SLI-XDOMAIN` |
| `CL-COSMO-COMPENSATION` | Cosmological physical and information entropy compensate | `source-claim` | `THEOREM_TARGET` | `self-identified-weakness-and-reconstruction-pending` | `VOP-2023-SLI-XDOMAIN`, `VOP-2025-COSMOLOGY` |
| `CL-SIMULATION-INFERENCE` | Entropy optimisation supports the simulation hypothesis | `interpretive-inference` | `SPECULATIVE` | `non-deductive-interpretation` | `VOP-2023-SLI-XDOMAIN`, `VOP-2025-GRAVITY`, `VOP-2026-CONNECTOME` |
| `CL-GRAVITY` | Newtonian gravity emerges from information dynamics | `source-claim` | `THEOREM_TARGET` | `line-by-line-derivation-audit-pending` | `VOP-2025-GRAVITY`, `VOP-2025-GRAVITY-RESPONSE` |
| `CL-POLYGON-EXTREMUM` | Equal multiplicities minimise polygon descriptor entropy | `source-claim` | `COUNTEREXAMPLE` | `source-specific-extremum-correction` | `VOP-2026-POLYGON` |
| `CL-LANGUAGE-DIVERSITY` | Language diversity decline conforms to SLI | `source-claim` | `THEOREM_TARGET` | `model-and-data-reproduction-pending` | `VOP-2026-LANGUAGE` |
| `CMP-DETERMINISTIC-SHANNON` | Deterministic processing is a restricted monotonic regime | `comparison-result` | `PROVED` | `established-literature-comparison` | - |

## Application assumptions

`EXT-PLANCK-AREA`, `EXT-ENTROPIC-FORCE`, and `EXT-LANGUAGE-DOMINANCE` are classified as `INTERPRETIVE` application/model assumptions. They are not UFT-ID theorem targets. If any is later promoted to `THEOREM_TARGET`, it must receive precise hypotheses and an explicit adversarial companion question.

## Non-circularity rule

A restricted SLI class may not be defined as

```text
C = { systems for which Delta I <= 0 }.
```

The class must be selected through independent dynamical, observational, boundary, or contractivity assumptions. Otherwise the embedding is a tautology wearing a lab coat.
