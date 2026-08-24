# Information Comparability Core

**Claim class:** `DEFINITION` for the comparison grammar, with individual results classified below.

This surface answers a deliberately narrow question:

> When are two quantities called "information" licensed to be compared as instances of the same declared measurement grammar?

It does **not** define a universal information ontology and does not infer semantic, epistemic, empirical, or physical equivalence from scalar arithmetic.

```text
SAME_WORD_INFORMATION != SAME_FUNCTIONAL
SAME_SCALAR_CODOMAIN != COMPARABLE_INFORMATION
SAME_UNIT != COMPARABLE_INFORMATION
SAME_FUNCTIONAL != SAME_OBSERVATION
IDENTICAL_SPEC => COMPARABLE
COMPARABLE != IDENTICAL_SPEC
NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE
POSITIVE_UNIT_CONVERSION != SEMANTIC_BRIDGE
PAIRWISE_SCOPE_COMPARABILITY != TRANSITIVE_COMPARABILITY
DIRECT_COMPARABILITY != EMPIRICAL_COMMENSURABILITY
FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY
```

## 1. Canonical specification

```text
InformationSpec = (
  source_type,
  functional,
  observation,
  unit,
  normalization,
  conditioning,
  scope
)
```

A valid specification has a nonempty scope and explicitly names every field above.

For this phase the bounded executable registry contains two finite logarithmic functionals:

```text
shannon_entropy
hartley_entropy
```

and two logarithm-base/unit conventions:

```text
bit
base4-digit
```

The finite registry is conformance machinery only. It does not claim those are the only information measures or units.

## 2. Direct comparability

For valid specifications `A` and `B`, define `DirectComparable(A,B)` iff:

```text
A.source_type   = B.source_type
A.functional    = B.functional
A.observation   = B.observation
A.unit          = B.unit
A.normalization = B.normalization
A.conditioning  = B.conditioning
A.scope intersect B.scope != empty
```

Thus direct comparison is intentionally stricter than scalar type compatibility.

```text
SAME_NUMBER_TYPE
!=
SAME_INFORMATION_SPECIFICATION
```

## 3. Explicit unit-converted comparability

A registered unit conversion has the form

```text
UnitConversion = (
  functional,
  source_unit,
  target_unit,
  positive_scale,
  scope
)
```

and is valid only when the scale is the exact registry value for the declared direction.

The current bounded logarithmic registry contains:

```text
bit -> base4-digit : scale 1/2
base4-digit -> bit : scale 2
```

`UnitComparable(A,B,C)` requires:

1. `A` and `B` agree in every direct-comparison field except `unit`;
2. `C.functional` agrees with their functional;
3. `C.source_unit=A.unit` and `C.target_unit=B.unit`;
4. `C` carries the registered positive scale;
5. all three scopes have nonempty common intersection.

This mode licenses unit conversion only.

```text
UNIT_CONVERSION
!=
OBSERVATION_BRIDGE
!=
SEMANTIC_BRIDGE
!=
EMPIRICAL_CALIBRATION
```

---

## UFT-INF-001 Identical valid specifications are directly comparable

**Claim class:** `PROVED`

**Canonical statement:** `Every valid InformationSpec is directly comparable with itself because all comparison-defining fields agree and its scope is nonempty.`

**Canonical hypotheses:** `["A is a valid InformationSpec"]`

**Proof.** Every equality in the definition of direct comparability is reflexive. Validity supplies `scope(A) != empty`, so

```text
scope(A) intersect scope(A) = scope(A) != empty.
```

Therefore `DirectComparable(A,A)`.

---

## UFT-INF-002 Direct comparability is symmetric

**Claim class:** `PROVED`

**Canonical statement:** `For valid InformationSpec values A and B, if A is directly comparable with B then B is directly comparable with A.`

**Canonical hypotheses:** `["A and B are valid InformationSpec values", "A and B satisfy the direct-comparability predicate"]`

**Proof.** Equality of each comparison-defining field is symmetric, and set intersection is commutative:

```text
A.scope intersect B.scope
=
B.scope intersect A.scope.
```

Hence every clause in `DirectComparable(A,B)` holds in the reverse direction.

**Boundary:** symmetry does not imply transitivity because scope overlap need not be transitive. `CX-INF-004` is the finite counterexample.

---

## UFT-INF-003 Direct comparability preserves the comparison-defining specification

**Claim class:** `PROVED`

**Canonical statement:** `If two InformationSpec values are directly comparable, then source_type, functional, observation, unit, normalization, and conditioning agree exactly and their scopes have nonempty intersection.`

**Canonical hypotheses:** `["A and B are valid InformationSpec values", "A and B are directly comparable"]`

**Proof.** This is an immediate projection of the definition of `DirectComparable`. Every listed equality and the nonempty scope intersection are conjuncts of that predicate.

The direction is deliberately one-way in the claim surface:

```text
DIRECTLY_COMPARABLE
=>
FIELD_MATCHES + SCOPE_OVERLAP
```

No subset of those field matches is silently promoted to comparability.

---

## UFT-INF-004 Positive unit conversion preserves scalar order

**Claim class:** `PROVED`

**Canonical statement:** `For real scalar values x and y and a positive conversion scale a, equality and strict order are preserved by x -> ax and the sign of y-x equals the sign of a(y-x).`

**Canonical hypotheses:** `["x and y are real scalars", "a>0"]`

**Proof.** Multiplication by a positive real scalar is strictly increasing. Therefore

```text
x = y  iff  ax = ay
x < y  iff  ax < ay
x > y  iff  ax > ay.
```

Also

```text
a(y-x)
```

has the same sign as `y-x` because `a>0`.

This proves only arithmetic order preservation under a licensed unit scale.

---

## UFT-INF-005 Explicit logarithm-base conversion gives non-identical comparable specifications

**Claim class:** `PROVED`

**Canonical statement:** `For Shannon or Hartley logarithmic entropy specifications that agree in every comparison-defining field except bit versus base4-digit unit, an explicit registered scale of 1/2 from bits to base4-digits or 2 in the reverse direction licenses unit-converted comparability; the specifications remain non-identical.`

**Canonical hypotheses:** `["A and B are valid InformationSpec values", "A and B differ only by bit versus base4-digit unit and scope may differ only with nonempty overlap", "the registered unit conversion matches the functional and direction"]`

**Proof.** For every positive argument `z`,

```text
log_4(z) = log_2(z) / log_2(4) = log_2(z)/2.
```

Both Shannon entropy and Hartley entropy are linear in the chosen logarithm value. Consequently the base-4 numerical representation is one half of the bit representation, and the inverse conversion has scale two.

The two specifications still differ in their `unit` field. Hence they are not identical and not directly comparable, but the explicit registered conversion licenses `UnitComparable`.

```text
COMPARABLE
!=
IDENTICAL_SPEC
```

---

## Counterexamples

### CX-INF-001 Same word and unit can hide different information functionals

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A Shannon-entropy specification and a Hartley-entropy specification can both be measured in bits and even return the same scalar on a uniform two-state distribution while remaining not directly comparable because their functional identities differ.`

For a uniform two-state distribution both quantities equal one bit, but

```text
shannon_entropy != hartley_entropy.
```

Therefore equal vocabulary, unit, and scalar output do not satisfy the direct-comparability predicate.

### CX-INF-002 Same functional and unit can use different observations

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `Two Shannon-entropy specifications in bits with different observation contracts are not directly comparable under the Information Comparability predicate.`

The observation field is comparison-defining. A fine observation and a coarse observation therefore require an explicit observation bridge before any stronger relation is claimed.

### CX-INF-003 Different units require an explicit conversion

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `Two otherwise matching logarithmic entropy specifications in bits and base4-digits are not directly comparable, although an explicit registered unit conversion can make them unit-converted comparable.`

This is the positive control for `COMPARABLE != IDENTICAL_SPEC`.

### CX-INF-004 Scope-overlap comparability need not be transitive

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `With otherwise identical specifications, scope A={alpha}, B={alpha,beta}, and C={beta} gives A directly comparable with B and B directly comparable with C while A is not directly comparable with C.`

Indeed:

```text
A intersect B = {alpha}
B intersect C = {beta}
A intersect C = empty.
```

So scope-relative direct comparability is reflexive and symmetric but not generally transitive.

### CX-INF-005 Numeric equality does not erase normalization differences

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `Two information quantities can both have scalar value 1 while their specifications use different normalization conventions, so numeric equality alone does not establish direct comparability or informational equivalence.`

Arithmetic equality remains true as arithmetic equality. What fails is the attempted semantic lift:

```text
SAME_NUMBER
!=
SAME_INFORMATION_SPECIFICATION.
```

---

## Finite conformance boundary

The executable battery enumerates exactly:

```text
2 functionals
2 observations
2 units
2 normalizations
2 conditionings
3 nonempty scopes
= 96 InformationSpec values
```

and all

```text
96^2 = 9216
```

ordered specification pairs.

It checks exactly:

```text
224 directly comparable ordered pairs
224 unit-convertible ordered pairs
96 reflexive cases
9216 symmetry cases
224 inverse unit-conversion cases
75 positive-scale order/sign cases
5 exact power-of-two bit/base4 conversion cases
```

The executable witness is a conformance model for the declared finite grammar. The proofs above remain the authority for the abstract results.

```text
FINITE_INFORMATION_CONFORMANCE
!=
GENERAL_INFORMATION_THEORY
!=
EMPIRICAL_VALIDATION
```
