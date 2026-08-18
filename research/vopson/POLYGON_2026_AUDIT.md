# 2026 Polygon Entropy Extremum Audit

**Claim class:** `COUNTEREXAMPLE`

**Primary source:** Melvin M. Vopson, *The Role of Information Entropy in Symmetry of Euclidean Polygons*, **Entropy** 28(5), 564 (2026), DOI `10.3390/e28050564`.

## Scope

This audit addresses one narrow mathematical statement in the primary source: for fixed total multiplicity `N` and fixed number `n` of positive descriptor categories, the paper states that equal multiplicity gives the minimum Shannon entropy.

This file does **not** claim that every numerical polygon comparison in the paper is false. In particular, comparisons that change the effective number of descriptor categories `n` are a different problem and must be audited separately.

## Reconstructed fixed-(N,n) problem

Let

```text
g_i in Z_{>0}
sum_i g_i = N
p_i = g_i / N
```

for `i=1,...,n`, with `N` and `n` fixed. The Shannon entropy is

```text
H(g) = - sum_i (g_i/N) log2(g_i/N).
```

Equivalently,

```text
H(g) = log2(N) - (1/N) sum_i g_i log2(g_i).
```

## Result

For a fixed number of categories, Shannon entropy is maximised by the uniform distribution. Therefore, when `N` is divisible by `n`,

```text
g_1 = ... = g_n = N/n
```

is a **maximum**, not a minimum, of `H`.

For positive integer multiplicities when `N` is not divisible by `n`, the maximum occurs at the most balanced integer vector: the counts differ by at most one.

The minimum over positive integer multiplicities occurs at the most concentrated allowed vector, up to permutation:

```text
(N-n+1, 1, ..., 1).
```

This follows from strict concavity of Shannon entropy, equivalently convexity of `x log x` in the second displayed form.

## Minimal concrete check

For the triangle-scale example `N=6, n=2`:

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

So equal multiplicity cannot be the fixed-`N,n` minimum.

## What this does and does not establish

It establishes a discrete mathematical correction to the fixed-`N,n` extremum statement.

It does **not** establish that regular polygons always have greater descriptor entropy than irregular polygons under the paper's changing descriptor alphabet. If an irregular polygon is represented using more distinct descriptor classes than a regular polygon, the two calculations are not a fixed-`n` comparison.

It also does not establish a physical dynamical law in either direction. A static entropy ordering does not by itself imply that a physical system evolves toward the lower- or higher-entropy representation.

## Reproduction

Run:

```bash
python3 experiments/reproduction/vopson_2026_polygons/run.py
python3 experiments/reproduction/vopson_2026_polygons/run.py --json
```

The script uses only the Python standard library and exhaustively enumerates positive integer compositions for a configurable finite range.

## Epistemic status

- The fixed-`N,n` Shannon extremum result is elementary mathematics.
- The source attribution is to the published 2026 article identified above.
- This audit is deliberately narrower than any global assessment of the Second Law of Infodynamics.
- Any manuscript-level criticism should quote or paraphrase the exact published statement and keep this scope limitation attached to it.
