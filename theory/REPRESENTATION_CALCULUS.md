# Representation and Congruence Calculus

**Authority:** canonical human mathematical surface for planned PR #14, delivered in GitHub PR #15.  
**Snapshot:** 2026-08-24.  
**Claim scope:** finite-dimensional representation changes and finite receiver re-encodings only.

This layer exists because equality-like language becomes dangerous when the transformation class is not named.

```text
SIMILARITY != CONGRUENCE
SIMILARITY != ORTHOGONAL_OR_UNITARY_SIMILARITY
SAME_CHARACTERISTIC_POLYNOMIAL != SIMILARITY
CONGRUENCE != SPECTRAL_EQUIVALENCE
COORDINATE_TUPLE != ABSTRACT_OBJECT
REPRESENTATION_CHANGE != PHYSICAL_CHANGE
RECEIVER_REENCODING != STATE_TRANSFORMATION
NONINJECTIVE_RECEIVER_REENCODING != OBSERVATIONAL_EQUIVALENCE_PRESERVATION
INVARIANT_UNDER_CLASS_C != UNQUALIFIED_REPRESENTATION_INDEPENDENCE
```

## 1. Transformation classes

For square matrices over `R` or `C`:

```text
similarity:
B = P^{-1} A P

orthogonal similarity over R:
B = Q^T A Q,  Q^T Q = I

unitary similarity over C:
B = U^* A U,  U^* U = I

real congruence:
B = P^T A P
```

For one abstract vector/operator pair under a basis change:

```text
v' = P^{-1} v
A' = P^{-1} A P
```

For deterministic observation and receiver re-encoding:

```text
O : S -> Y
R : Y -> Z
O' = R o O
```

Receiver re-encoding preserves the original observation fibres only when `R` is injective on `im(O)`.

Every invariant claim must therefore name its transformation class and assumptions.

```text
INVARIANT_WITH_RESPECT_TO_CLASS_C
!=
INVARIANT_WITH_RESPECT_TO_EVERY_REPRESENTATION_CHANGE
```

## UFT-REP-001 Similarity preserves characteristic polynomial

**Claim class:** `PROVED`

**Canonical statement:** `If B=P^{-1}AP for an invertible finite-dimensional change of basis P over R or C, then A and B have the same characteristic polynomial; trace, determinant, and rank are preserved under the same similarity transformation.`

**Canonical hypotheses:** `["A and B are square matrices over R or C", "P is invertible", "B=P^{-1}AP"]`

**Proof.** For an indeterminate `lambda`,

```text
lambda I - B
= lambda I - P^{-1} A P
= P^{-1} (lambda I - A) P.
```

Taking determinants gives

```text
det(lambda I-B)
= det(P^{-1}) det(lambda I-A) det(P)
= det(lambda I-A).
```

Hence the characteristic polynomials agree, so trace and determinant agree through their standard coefficient identities. Separately, multiplication by invertible matrices on the left and right preserves rank, so `rank(B)=rank(A)`. Rank preservation is therefore a consequence of similarity itself, not of characteristic-polynomial equality alone.

The converse is false in general. `CX-REP-003` supplies a two-dimensional counterexample.

## UFT-REP-002 Orthogonal or unitary similarity preserves Frobenius norm

**Claim class:** `PROVED`

**Canonical statement:** `Orthogonal similarity over R and unitary similarity over C are similarity transformations and additionally preserve the Frobenius norm.`

**Canonical hypotheses:** `["B=Q^T A Q with Q^TQ=I over R, or B=U^* A U with U^*U=I over C"]`

**Proof.** Orthogonal/unitary transformations are invertible, so they are special cases of similarity. For the complex case,

```text
||U^* A U||_F^2
= tr((U^*AU)^*(U^*AU))
= tr(U^* A^* U U^* A U)
= tr(U^* A^* A U)
= tr(A^* A U U^*)
= tr(A^* A)
= ||A||_F^2.
```

The real orthogonal case is the same argument with transpose. Ordinary similarity does not generally preserve this norm; `CX-REP-002` is an explicit shear counterexample.

## UFT-REP-003 Invertible congruence preserves rank

**Claim class:** `PROVED`

**Canonical statement:** `If B=P^TAP over R with P invertible, then rank(B)=rank(A); if A is symmetric then B is symmetric. Congruence does not generally preserve eigenvalues.`

**Canonical hypotheses:** `["A is a real square matrix", "P is invertible", "B=P^TAP"]`

**Proof.** Both `P^T` and `P` are invertible. Left or right multiplication by an invertible matrix preserves rank, hence

```text
rank(P^T A P) = rank(A).
```

If `A^T=A`, then

```text
(P^T A P)^T = P^T A^T P = P^T A P,
```

so symmetry is preserved. Eigenvalues need not be preserved under congruence. `CX-REP-001` gives an exact counterexample.

## UFT-REP-004 Coordinate change preserves abstract linear action

**Claim class:** `PROVED`

**Canonical statement:** `For v'=P^{-1}v and A'=P^{-1}AP with P invertible, A'v'=P^{-1}(Av); the coordinate representation changes while the represented linear action is covariant.`

**Canonical hypotheses:** `["P is invertible", "v'=P^{-1}v", "A'=P^{-1}AP"]`

**Proof.** Directly,

```text
A'v'
= (P^{-1} A P)(P^{-1}v)
= P^{-1} A v.
```

Thus the transformed coordinates of the output equal the transformed operator acting on transformed input coordinates. This is a representation statement, not a physical-identity theorem.

`CX-REP-005` records why a coordinate tuple without its basis/chart is not an abstract object identifier.

## UFT-REP-005 Injective receiver re-encoding preserves observation equivalence

**Claim class:** `PROVED`

**Canonical statement:** `For a deterministic observation O:S->Y and receiver map R:Y->Z that is injective on im(O), R(O(x))=R(O(y)) iff O(x)=O(y); hence the observation fibres are unchanged.`

**Canonical hypotheses:** `["O:S->Y is deterministic", "R:Y->Z is injective on im(O)"]`

**Proof.** If `O(x)=O(y)`, applying `R` gives equality after re-encoding. Conversely, if

```text
R(O(x)) = R(O(y)),
```

then both `O(x)` and `O(y)` lie in `im(O)`. Injectivity of `R` on that image therefore gives `O(x)=O(y)`.

So the observational equivalence relation and fibre partition are unchanged. If receiver injectivity is dropped, the converse fails; `CX-REP-004` supplies the minimal merging pattern.

## 2. Counterexamples

### CX-REP-001 Congruent need not be similar

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `I2 and diag(4,1) are congruent via P=diag(2,1) but are not similar because their traces and characteristic polynomials differ.`

Take

```text
A = I2
P = diag(2,1)
P^T A P = diag(4,1).
```

The traces are `2` and `5`, so UFT-REP-001 rules out similarity.

```text
CONGRUENCE != SIMILARITY
CONGRUENCE != SPECTRAL_EQUIVALENCE
```

### CX-REP-002 Similar need not be orthogonally similar

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `diag(1,2) is similar via a shear to [[1,-1],[0,2]], but their Frobenius norms differ, so they cannot be orthogonally similar.`

With

```text
A = diag(1,2)
P = [[1,1],[0,1]]
B = P^{-1} A P = [[1,-1],[0,2]],
```

we have `||A||_F^2=5` and `||B||_F^2=6`. UFT-REP-002 therefore blocks orthogonal similarity even though ordinary similarity holds.

### CX-REP-003 Same characteristic polynomial need not imply similarity

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `I2 and the nontrivial Jordan block [[1,1],[0,1]] have the same characteristic polynomial but are not similar because rank(A-I) differs.`

Both have characteristic polynomial `(lambda-1)^2`. But

```text
rank(I2-I2)=0
rank(J2(1)-I2)=1.
```

Similarity preserves rank after subtracting the same scalar identity, so they are not similar.

### CX-REP-004 Noninjective receiver re-encoding can merge fibres

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `An observation distinguishing x0 and x1 can become indistinguishable after a receiver map sends both observation values to one output.`

Take

```text
O(x0)=0
O(x1)=1
R(0)=z
R(1)=z.
```

Then `O(x0) != O(x1)` but `R(O(x0))=R(O(x1))`.

```text
RECEIVER_REENCODING != STATE_TRANSFORMATION
NONINJECTIVE_RECEIVER_REENCODING != OBSERVATIONAL_EQUIVALENCE_PRESERVATION
```

### CX-REP-005 Coordinate tuple alone does not identify an abstract vector

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `The coordinate tuple (1,0) denotes different abstract vectors in the standard basis and in the swapped basis; the chart/basis is part of the representation.`

In basis `(e1,e2)`, `(1,0)` denotes `e1`. In basis `(e2,e1)`, the same tuple denotes `e2`.

```text
COORDINATE_TUPLE != ABSTRACT_OBJECT
CHART != OBJECT
```

## 3. Finite conformance surface

The executable battery uses exact rational arithmetic and no floating tolerances.

For 2x2 matrices with entries in `{-1,0,1}`:

```text
3^4 = 81 matrices.
```

For 2x2 change-of-basis matrices with entries in `{-1,0,1}` and determinant `+/-1`:

```text
40 unimodular transformations.
```

The signed-permutation orthogonal subset contains exactly `8` matrices.

The battery therefore checks:

```text
81 * 40 = 3240 similarity invariant instances
81 * 40 = 3240 congruence rank instances
81 * 8  = 648 orthogonal Frobenius instances
81 * 40 * 9 = 29160 coordinate covariance instances
```

For receiver re-encoding on `Fin3`, there are `3^3=27` endofunctions. All ordered `(O,R)` pairs are inspected. Exactly `441` pairs have `R` injective on `im(O)`, producing `441*9=3969` source-pair equivalence checks.

```text
FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF
```

## 4. Deferrals

This phase does not claim or implement:

- Jordan or rational canonical form as a general classification engine;
- Sylvester inertia as a separately advertised UFT-ID theorem;
- infinite-dimensional operator equivalence;
- stochastic receiver kernels;
- universal information invariance;
- empirical validity of a coordinate system or receiver;
- physical equivalence from mathematical representation equivalence;
- Lean proof objects.
