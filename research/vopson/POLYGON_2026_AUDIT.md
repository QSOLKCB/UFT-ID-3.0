# 2026 Polygon Entropy Extremum Audit

**Claim class:** `COUNTEREXAMPLE`

**Primary source:** Melvin M. Vopson, *The Role of Information Entropy in Symmetry of Euclidean Polygons*, **Entropy** 28(5), 564 (2026), DOI `10.3390/e28050564`.

## Exact source target

This audit targets the paper's general multiplicity extremization argument, not every later polygon example.

In the published 9-page PDF, pp. 3-4, the author describes a constrained Shannon-entropy optimization for a system with a **fixed total number of elements `N`**, represents repeated states/descriptors through multiplicities `g_i`, and states that the minimum-entropy condition is that the elements have **equal multiplicity**. The same discussion also identifies the all-distinct case `g_i=1`, hence `n=N`, as the maximum-entropy case.

The source variables map to this audit as follows:

```text
N   -> fixed total number of elements / total multiplicity
g_i -> multiplicity of represented category i
n   -> number of represented categories
p_i -> g_i / N
H   -> -sum_i p_i log2(p_i)
```

The source's general prose fixes `N` but does not cleanly freeze `n` throughout the whole optimization. For that reason this audit now reports **two distinct problems** rather than silently imposing an extra source assumption.

## Problem A: fixed N and fixed n

For a chosen category count `n`, let

```text
g_i in Z_{>0}
sum_i g_i = N
p_i = g_i / N
```

for `i=1,...,n`. Then

```text
H(g) = - sum_i (g_i/N) log2(g_i/N)
     = log2(N) - (1/N) sum_i g_i log2(g_i).
```

For fixed `N` and fixed `n`, Shannon entropy is maximized by the most balanced multiplicity vector. When `N` is divisible by `n`,

```text
g_1 = ... = g_n = N/n
```

is therefore a **maximum**, not a minimum.

For positive integer multiplicities when divisibility fails, the maximum occurs when the counts differ by at most one. The minimum occurs at the most concentrated allowed positive vector, up to permutation:

```text
(N-n+1, 1, ..., 1).
```

This is the direct fixed-`n` classification of the Lagrange stationary point.

## Problem B: fixed N with n allowed to vary

If the source problem is read literally as fixing only total system size `N`, with the number of represented categories allowed to vary over

```text
1 <= n <= N,
```

then the global Shannon extrema are:

```text
minimum: n=1, counts=(N),         H=0
maximum: n=N, counts=(1,...,1),   H=log2(N).
```

Thus equal multiplicity **by itself** does not characterize a nontrivial global minimum. Many equal-multiplicity states with different `n` have different positive entropies. The one-category state is the global minimum, and the all-distinct state is the global maximum.

This second result also reproduces the paper's stated maximum endpoint `g_i=1`, `n=N`.

## Minimal fixed-(N,n) witness

For `N=6, n=2`:

```text
(3,3) -> p=(1/2,1/2) -> H = 1 bit
```

whereas

```text
(5,1) -> p=(5/6,1/6) -> H ~= 0.650022421648 bits.
```

Hence

```text
H(5/6,1/6) < H(1/2,1/2).
```

So equal multiplicity cannot be the minimum of the fixed-`N,n` slice.

For the corresponding variable-`n`, fixed-`N=6` problem:

```text
(6)             -> H = 0
(3,3)           -> H = 1
(2,2,2)         -> H = log2(3)
(1,1,1,1,1,1)   -> H = log2(6).
```

## What this does and does not establish

It establishes a narrow mathematical correction to the paper's general multiplicity-extremum classification:

- if `n` is held fixed, equal multiplicity is the Shannon **maximum** for that slice;
- if only `N` is fixed, the global minimum is the one-category state and equal multiplicity alone is not a sufficient minimum condition.

It does **not** establish that every numerical polygon comparison in the paper is false. In particular, a regular polygon and an irregular polygon may be represented with different effective descriptor-category counts. Those calculations must be reproduced under their actual descriptor maps rather than treated as a fixed-`n` experiment.

It also does not establish a physical dynamical law in either direction. A static entropy ordering does not imply that a physical polygon evolves toward one representation.

## Reproduction

Run:

```bash
python3 experiments/reproduction/vopson_2026_polygons/run.py
python3 experiments/reproduction/vopson_2026_polygons/run.py --json
```

The script uses only the Python standard library. It exhaustively checks canonical positive integer multiplicity vectors for a configurable finite range, reports both the fixed-`n` slices and a variable-`n` fixed-`N` check, and avoids tolerance-based identification of extrema.

## Epistemic status

- The Shannon extremum statements above are elementary finite mathematics.
- The source attribution is restricted to the published multiplicity optimization on pp. 3-4 of the 2026 article.
- Polygon-specific descriptor comparisons remain a separate reproduction task.
- This audit is deliberately narrower than any global assessment of the Second Law of Infodynamics.
- Any manuscript-level criticism should keep the source formulation, variable map, and scope limitation attached to the result.
