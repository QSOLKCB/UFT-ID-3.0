# Vopson Claim and Dependency Graph

**Status:** claim-routing map. Dependencies record reliance, not truth.

The graph deliberately separates source claims, external premises, UFT-ID assessments, and interpretive inferences. Each UFT-ID assessment has exactly one canonical claim class.

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

| Claim node | UFT-ID class | Current status |
|---|---|---|
| `CL-MEI-BIT-MASS` | `THEOREM_TARGET` | Physical hypothesis unresolved; thermodynamic derivation pending |
| `CL-INFO-CATASTROPHE` | `THEOREM_TARGET` | Corrected extrapolation pending reproduction |
| `CL-ANNIHILATION-PHOTONS` | `THEOREM_TARGET` | Experimental prediction unresolved |
| `CL-GENIES-METHOD` | `THEOREM_TARGET` | Exact software/method reproduction pending |
| `CL-GENETIC-LAW` | `THEOREM_TARGET` | Causal and null-model audit pending |
| `CL-SLI-PUBLISHED` | `THEOREM_TARGET` | Exact source-domain reconstruction pending |
| `CL-ATOMIC-HUND` | `INTERPRETIVE` | Encoding relation not yet an energetic derivation |
| `CL-COSMO-COMPENSATION` | `THEOREM_TARGET` | Later source records a weakness; reconstruction pending |
| `CL-GRAVITY` | `THEOREM_TARGET` | Line-by-line derivation audit pending |
| `CL-POLYGON-EXTREMUM` | `COUNTEREXAMPLE` | Bounded multiplicity extremum correction has repository evidence |
| `CL-LANGUAGE-DIVERSITY` | `THEOREM_TARGET` | Model and data reproduction pending |
| `CL-SIMULATION-INFERENCE` | `SPECULATIVE` | No unique discriminating inference established |
| `CMP-DETERMINISTIC-SHANNON` | `PROVED` | Restricted deterministic Shannon regime; not the full SLI |

## Non-circularity rule

A restricted SLI class may not be defined as

```text
C = { systems for which Delta I <= 0 }.
```

The class must be selected through independent dynamical, observational, boundary, or contractivity assumptions. Otherwise the embedding is a tautology wearing a lab coat.
