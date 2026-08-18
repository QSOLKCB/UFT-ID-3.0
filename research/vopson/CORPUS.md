# Canonical Vopson Scholarly Target Corpus

**Status:** bibliographic and claim-routing authority for the UFT-ID 3.0 Vopson audit.

**Author identity anchor:** ORCID `0000-0002-8073-5538`.

This corpus records public scholarly works relevant to infodynamics and adjacent information-physics claims. Recording a work does not endorse it, refute it, or turn it into a UFT-ID claim. Exact equations and empirical results remain subject to the reproduction matrix.

## Source policy

- Prefer DOI/publisher records and the official University of Portsmouth research portal.
- Keep journal articles, editorials, datasets, responses, and early-online items distinguishable.
- Use `null` rather than inventing an unverified final DOI.
- Record corrections and author responses as first-class corpus objects.
- Keep popular commentary outside the technical authority chain when a primary source exists.

## Status vocabulary

| Field | Meaning |
|---|---|
| `metadata-verified` | Bibliographic identity checked; equations not yet reproduced |
| `partial-reproduction` | A bounded source claim has executable or written evidence |
| `reproduced` | Exact target result independently regenerated |
| `pending` equation map | Source equations/variables not yet mapped line by line |
| `partial` equation map | At least one bounded source formulation mapped |

## Chronology

| ID | Year | Work | Type / status | Claim tracks | Reproduction |
|---|---:|---|---|---|---|
| `VOP-2019-MEI` | 2019 | [The mass-energy-information equivalence principle](https://doi.org/10.1063/1.5123794) | journal-article; peer-reviewed | `mass-energy-information-equivalence` | `metadata-verified` |
| `VOP-2020-CATASTROPHE` | 2020 | [The information catastrophe](https://doi.org/10.1063/5.0019941) | journal-article; peer-reviewed | `information-catastrophe`, `mass-energy-information-equivalence` | `metadata-verified` |
| `VOP-2020-CATASTROPHE-ERRATUM` | 2020 | [Erratum: The information catastrophe](https://doi.org/10.1063/5.0028117) | erratum; peer-reviewed | `information-catastrophe` | `metadata-verified` |
| `VOP-2020-CATASTROPHE-DATA` | 2020 | [Dataset for 'The Information Catastrophe'](https://doi.org/10.17029/60d74cee-ed70-41e2-a802-873b7fe1dc34) | dataset; not-applicable | `information-catastrophe`, `dataset-support` | `metadata-verified` |
| `VOP-2021-GENIES` | 2021 | [A new method to study genome mutations using the information entropy](https://doi.org/10.1016/j.physa.2021.126383) | journal-article; peer-reviewed | `genomic-information-entropy` | `metadata-verified` |
| `VOP-2021-VISIBLE-MATTER` | 2021 | [Estimation of the information contained in the visible matter of the universe](https://doi.org/10.1063/5.0064475) | journal-article; peer-reviewed | `particle-information`, `mass-energy-information-equivalence` | `metadata-verified` |
| `VOP-2022-MEI-EXPERIMENT` | 2022 | [Experimental protocol for testing the mass-energy-information equivalence principle](https://doi.org/10.1063/5.0087175) | journal-article; peer-reviewed | `mass-energy-information-equivalence`, `particle-information` | `metadata-verified` |
| `VOP-2022-GENETIC-LAW` | 2022 | [A possible information entropic law of genetic mutations](https://doi.org/10.3390/app12146912) | journal-article; peer-reviewed | `genomic-information-entropy` | `metadata-verified` |
| `VOP-2022-SLI` | 2022 | [Second law of information dynamics](https://doi.org/10.1063/5.0100358) | journal-article; peer-reviewed | `second-law-of-infodynamics`, `genomic-information-entropy`, `digital-information` | `metadata-verified` |
| `VOP-2023-NONEQ` | 2023 | [Information theory of non-equilibrium states](https://doi.org/10.59973/ipil.20) | editorial; editorial-peer-reviewed | `non-equilibrium-information`, `genomic-information-entropy` | `metadata-verified` |
| `VOP-2023-SLI-XDOMAIN` | 2023 | [The second law of infodynamics and its implications for the simulated universe hypothesis](https://doi.org/10.1063/5.0173278) | journal-article; peer-reviewed | `second-law-of-infodynamics`, `cross-domain-applications`, `simulation-hypothesis-inference` | `metadata-verified` |
| `VOP-2024-BLOCKCHAIN` | 2024 | [Next generation blockchain technology: The Entropic Blockchain](https://doi.org/10.3390/app14146297) | journal-article; peer-reviewed | `digital-information`, `digital-compression-applications` | `metadata-verified` |
| `VOP-2025-COSMOLOGY` | 2025 | [On the second law of infodynamics from cosmological thermodynamics](https://doi.org/10.59973/ipil.137) | journal-article; peer-reviewed | `second-law-of-infodynamics`, `cosmology`, `response-history` | `metadata-verified` |
| `VOP-2025-GRAVITY` | 2025 | [Is gravity evidence of a computational universe?](https://doi.org/10.1063/5.0264945) | journal-article; peer-reviewed | `information-theoretic-gravity`, `mass-energy-information-equivalence`, `second-law-of-infodynamics`, `simulation-hypothesis-inference` | `metadata-verified` |
| `VOP-2025-GRAVITY-RESPONSE` | 2025 | [Response to Sabine Hossenfelder's Commentary on Vopson's Paper: Is gravity evidence of a computational universe?](https://doi.org/10.59973/ipil.212) | response; not-indicated | `information-theoretic-gravity`, `response-history` | `metadata-verified` |
| `VOP-2026-BIOLOGY-EDITORIAL` | 2026 | [Can information and entropic dynamics bridge the gap between biology and the physical sciences?](https://doi.org/10.3390/e28030349) | editorial; editorial-peer-reviewed | `biological-information`, `cross-domain-applications` | `metadata-verified` |
| `VOP-2026-CONNECTOME` | 2026 | [From connectome to cognition: building the first digital organism](https://doi.org/10.59973/ipil.361) | news-and-views; peer-reviewed | `computational-organism`, `simulation-hypothesis-inference` | `metadata-verified` |
| `VOP-2026-POLYGON` | 2026 | [The role of information entropy in symmetry of Euclidean polygons](https://doi.org/10.3390/e28050564) | journal-article; peer-reviewed | `polygon-symmetry`, `second-law-of-infodynamics` | `partial-reproduction` |
| `VOP-2026-LANGUAGE` | 2026 | [Second law of info-dynamics and the language diversity decline](https://researchportal.port.ac.uk/en/persons/melvin-vopson/) | journal-article; early-online-peer-reviewed | `language-diversity`, `second-law-of-infodynamics` | `metadata-verified` |

## Important dependency separations

1. **MEI is not SLI.** The mass-energy-information proposal and the entropy-direction proposal are separate claims, even when later papers combine them.
2. **Method is not law.** GENIES-style entropy spectra can be useful without establishing a universal mutation law.
3. **Static ordering is not dynamics.** A symmetry or compression ordering does not itself specify a time evolution.
4. **Interpretation is not derivation.** Simulation-hypothesis language is tracked separately from equations and empirical claims.
5. **Recovery of an existing formula is not automatically a new theory.** Gravity work must identify which assumptions contribute the inverse-square form and whether any distinct prediction survives.

## Machine authority

- `AUTHOR.json` — public author identity boundary
- `corpus.json` — canonical work registry
- `CLAIM_GRAPH.json` — dependency and assessment graph
- `scripts/validate_vopson_corpus.py` — fail-closed validator
