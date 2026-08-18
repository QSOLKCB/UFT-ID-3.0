# Source Definition Concordance

**Status:** source-oriented notation map. A source summary is not an endorsement, and a pending equation map must not be treated as exact reproduction.

## Definition status labels

- `SOURCE-SUMMARY` — paraphrased from official metadata or a bounded source reading.
- `SOURCE-MAPPED` — source variables and constraints have been mapped to repository notation.
- `PENDING-EQUATION-MAP` — exact equation/page mapping remains open.
- `UFT-COMPARISON` — UFT-ID notation used only to compare structures.

## D-V1. Bit-mass proposal

**Source:** `VOP-2019-MEI`  
**Status:** `PENDING-EQUATION-MAP`

Source expression:

\[
m_{\rm bit}(T)=\frac{k_B T\ln 2}{c^2}.
\]

Required distinctions:

```text
minimum erasure work
!= physical energy barrier
!= energy of a particular memory state
!= intrinsic rest energy of abstract logical information
```

UFT-ID must not assume the last identification merely because the dimensions match.

## D-V2. GENIES-style genome entropy spectrum

**Source:** `VOP-2021-GENIES`  
**Status:** `PENDING-EQUATION-MAP`

A sequence is divided into windows, and m-block symbol frequencies define a Shannon-derived local spectrum. Exact reproduction must freeze:

- alphabet;
- block size `m`;
- window size and stride;
- overlapping/non-overlapping convention;
- boundary handling;
- estimator and logarithm base;
- reference/variant alignment.

## D-V3. Published SLI statement

**Source:** `VOP-2022-SLI`  
**Status:** `SOURCE-SUMMARY`

The paper proposes that information entropy in the examined information-bearing systems remains constant or decreases over time.

Before theorem comparison, reconstruct:

\[
(S,F,O,\mu,\mathcal P,I,\text{boundary/source assumptions}).
\]

A finite randomising channel, deterministic processing theorem, KL contraction theorem, and coarse-grained physical process are different mathematical objects even when each is informally called “information dynamics”.

## D-V4. Cross-domain information quantity

**Source:** `VOP-2023-SLI-XDOMAIN`  
**Status:** `PENDING-EQUATION-MAP`

The 2023 work applies information-entropy reasoning to several domains. Each domain requires its own record:

```text
source state
probability model
alphabet / partition
information functional
time or ordering variable
bridge to physical interpretation
lost / ignored structure
```

There is no generic permission to reuse one domain’s `I` in another.

## D-V5. Polygon multiplicity model

**Source:** `VOP-2026-POLYGON`  
**Status:** `SOURCE-MAPPED`

For positive multiplicities \(g_i\),

\[
N=\sum_{i=1}^{n}g_i,\qquad p_i=\frac{g_i}{N},
\]

and

\[
H(g)=-\sum_{i=1}^{n}p_i\log_2p_i.
\]

PR #2 separates:

1. fixed `N`, fixed `n`;
2. fixed `N`, variable `n`;
3. polygon-specific comparisons where the descriptor map/category count changes.

These are not interchangeable optimisation problems.

## D-V6. Gravity dependency bundle

**Source:** `VOP-2025-GRAVITY`  
**Status:** `PENDING-EQUATION-MAP`

The gravity derivation must track at least:

```text
MEI premise
SLI premise
information-bearing cell count N(R)
Planck-area scale
entropic-force relation
displacement scale
mass and temperature assumptions
```

The audit must identify whether \(R^2\) scaling and \(G\) are derived or imported.

## D-V7. Language-diversity entropy

**Source:** `VOP-2026-LANGUAGE`  
**Status:** `PENDING-EQUATION-MAP`

A language-population distribution has a Shannon diversity statistic. If the demographic dynamics already concentrate probability into a dominant category, entropy decline may be a direct consequence of the assumed population model. Independent infodynamic content requires an additional prediction.

## D-V8. Restricted deterministic comparison

**Source:** established Shannon theory / `theory/FINITE_RESULTS.md`  
**Status:** `UFT-COMPARISON`

For finite \(Y=f(X)\),

\[
H(Y)\le H(X).
\]

This is a valid restricted monotonic regime. It is not automatically identical to the full published SLI.
