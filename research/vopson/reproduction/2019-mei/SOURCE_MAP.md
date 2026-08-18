# VOP-2019-MEI Source Map

**Primary source:** Melvin M. Vopson, *The mass-energy-information equivalence principle*, AIP Advances 9, 095206 (2019), DOI `10.1063/1.5123794`.

**Primary metadata:** University of Portsmouth research portal and AIP DOI record.

**Claim boundary:** this file maps what the paper says. It does not endorse the physical hypothesis.

## Exact source structure

| Source location | Source object | UFT-ID reproduction role |
|---|---|---|
| p. 1, Eq. (1) | self-information `I(p) = -log_b p` | source definition |
| p. 1, Eq. (2) | Shannon entropy `H(X) = -sum p_j log_b p_j` | established definition reused by source |
| p. 1, Eq. (3) | `Omega = 2^(N H(X))` | source combinatorial bridge |
| p. 1, Eq. (4) | `S = k_B ln Omega = N k_B H(X) ln 2` | source information-to-thermodynamic-entropy bridge |
| p. 2, Eq. (5) | unbiased binary state gives `H(X)=1` | exact finite arithmetic |
| p. 2, erase discussion | initial information entropy `N k_B ln 2`, erased information entropy `0` | source erasure model |
| p. 2, erase discussion | `Delta S_info = -N k_B ln 2` and total-entropy constraint | Landauer-scale step |
| p. 2, Section II | source states information creation requires work at the `k_B T ln 2` scale | source claim requiring separate audit |
| p. 2, Eq. (6) | `m_bit = k_B T ln 2 / c^2` | central MEI formula |
| p. 2 after Eq. (6) | at `T=300 K`, source reports about `3.19e-38 kg` per bit | numerical reproduction target |
| p. 3, proposed experiment | decimal `1 TB = 10^12 bytes = 8e12 bits` | storage-count convention |
| p. 4, proposed experiment | source reports mass change about `2.5e-25 kg` | numerical reproduction target |
| p. 4, conclusion | source reports `2.91e-40 kg` at `2.73 K` | numerical reproduction target |

## The bridge that PR #6 audits

The following three statements must remain separately typed:

```text
LANDAUER_ERASURE_BOUND
    logically irreversible erasure under the declared thermodynamic conditions
    has a minimum dissipation/work scale involving k_B T ln 2

ADDITIONAL_PHYSICAL_IDENTIFICATION
    stored information bit has intrinsic energy E_bit = k_B T ln 2

MASS_CONVERSION
    if E_bit is an ordinary stored energy contribution, m_bit = E_bit / c^2
```

The arithmetic from the second statement to Eq. (6) is straightforward. The scientific issue is whether the second statement follows from the first.

## Source-text inconsistency preserved

On p. 2, immediately after writing

```text
Delta S_tot = Delta S_phys + Delta S_info >= 0
```

with `Delta S_info = -N k_B ln 2`, the paper's prose prints an inequality for the physical-entropy/heat term in a direction that does not match the preceding algebra or the usual lower-bound formulation of Landauer erasure. The subsequent equality-scale statement and Eq. (6) use `k_B T ln 2`.

PR #6 records this as a **source-text inequality inconsistency**. It does not silently rewrite the source. The Eq. (6) arithmetic reproduction is therefore separated from the exact prose-sign audit.

## Scope declared by the paper

The paper explicitly restricts the proposed MEI principle to classical digital memory states at equilibrium and excludes relativistic information carriers, photons/waves, analogue information, and biological information from the article's applicability domain.

## Source-byte policy

The paper is identified by DOI, publication metadata, page and equation number. The primary PDF bytes are not committed to this repository. A source-byte SHA-256 is therefore **not claimed** here. Repository receipts hash the local source map, derivation, assumptions, fixtures, executable reproduction, and result record.

```text
DOI_AND_EQUATION_IDENTITY != SOURCE_PDF_BYTE_HASH
SOURCE_NOT_REPUBLISHED != SOURCE_UNVERIFIED
```
