# Vopson Reproduction Matrix

A source is not criticised publicly until its relevant calculation is reproduced or the reproduction blocker is documented.

| Work | Exact target | Status | Repository evidence |
|---|---|---|---|
| `VOP-2019-MEI` | Derive bit-mass formula and storage-device prediction | `reproduced` | `reproduction/2019-mei/SOURCE_MAP.md`; `DERIVATION.md`; `ASSUMPTION_GRAPH.json`; `DIMENSIONAL_AUDIT.md`; `CONTROL_MATRIX.md`; `result.json`; executable `experiments/reproduction/vopson_2019_mei/run.py`; receipt `experiments/run_pr6.py` |
| `VOP-2020-CATASTROPHE` | Rebuild corrected growth/energy/mass extrapolation | `metadata-verified` | None yet |
| `VOP-2020-CATASTROPHE-ERRATUM` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2020-CATASTROPHE-DATA` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2021-GENIES` | Reimplement exact windowed m-block method | `metadata-verified` | None yet |
| `VOP-2021-VISIBLE-MATTER` | Reproduce particle count and bits-per-particle estimate | `metadata-verified` | None yet |
| `VOP-2022-MEI-EXPERIMENT` | Reproduce IR wavelength/energy and conservation accounting | `metadata-verified` | None yet |
| `VOP-2022-GENETIC-LAW` | Reproduce selected SARS-CoV-2 entropy trend and null models | `metadata-verified` | None yet |
| `VOP-2022-SLI` | Reproduce digital and RNA examples exactly | `metadata-verified` | None yet |
| `VOP-2023-NONEQ` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2023-SLI-XDOMAIN` | Reproduce each domain as an independent module | `metadata-verified` | None yet |
| `VOP-2024-BLOCKCHAIN` | Reproduce entropy barcode and compression/validation claims | `metadata-verified` | None yet |
| `VOP-2025-COSMOLOGY` | Reconstruct thermodynamic argument and stated weakness | `metadata-verified` | None yet |
| `VOP-2025-GRAVITY` | Line-by-line dimensional and assumption audit | `metadata-verified` | None yet |
| `VOP-2025-GRAVITY-RESPONSE` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2026-BIOLOGY-EDITORIAL` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2026-CONNECTOME` | Metadata/context registration; technical dependency extraction where relevant | `metadata-verified` | Corpus metadata only |
| `VOP-2026-POLYGON` | Multiplicity extremum on pp. 3–4; polygon descriptor cases remain open | `partial-reproduction` | `POLYGON_2026_AUDIT.md`; executable script |
| `VOP-2026-LANGUAGE` | Reproduce demographic model and entropy trajectory | `metadata-verified` | None yet |

## VOP-2019-MEI scope note

`reproduced` here means the **2019 paper's core equation chain and displayed numerical predictions have been independently regenerated under the paper's declared identification**. It does not mean the identification of the Landauer erasure scale with intrinsic stored-bit energy has been physically validated.

```text
ARITHMETIC_REPRODUCED
!= PREMISE_VALIDATED
!= PHYSICAL_INTERPRETATION_VALIDATED
!= EXPERIMENTALLY_CONFIRMED
```

The source-text inequality issue on p. 2 is preserved explicitly in the reproduction package rather than silently normalized.

## Status promotion rules

- `metadata-verified` does not mean a calculation is reproduced.
- `partial-reproduction` must name the bounded source statement and evidence path.
- `reproduced` requires source inputs or stable source locators, code, expected/observed outputs, environment, and hashes. When source bytes are not redistributed, the record must say so rather than invent a source-byte hash.
- `blocked` must state the missing data, ambiguous definition, unavailable code, or access limitation.
- A failed reproduction must distinguish implementation error, source ambiguity, data mismatch, and scientific disagreement.
