# Cross-Repository Finite Results

This surface promotes only results with explicit hypotheses and either a direct finite proof or an executable witness in `experiments/cross_repo/run.py`.

The source repositories motivate the **questions**. They do not supply physical authority for the results.

The section heading, canonical class, optional qualifier, and canonical scope for each `CR` result are synchronized with `machine/cross_repo_results.json` by `scripts/validate_cross_repo_patterns.py`. Explanatory prose may be richer, but it must not contradict those machine-bound metadata fields.

## CR1. Content identity invariant under byte-preserving transport

**Class:** `PROVED`

**Canonical scope:** `deterministic digest of exact unchanged content bytes; location metadata may change`

Let content identity be

```text
id(x) = h(x)
```

for a deterministic digest function `h` applied to exact content bytes. Let a transport change only a location label:

```text
T(x, l_a) = (x, l_b).
```

Then

```text
id(T(x,l_a).content) = id(x).
```

### Proof

The transported content bytes are exactly `x`, so both identities evaluate the same deterministic function on the same input.

### Scope

This proves invariance under **byte-preserving** transport only. It says nothing about truth, authorship, authenticity, or a transport that modifies bytes.

### Repository patterns

QSOL-THOTH, QSOL-CONTROL, and QEC independently distinguish object/content identity from transport or storage location.

---

## CR2. Non-injective projection forbids a global exact reconstruction

**Class:** `PROVED`

**Qualifier:** `established mathematics`

**Canonical scope:** `set-theoretic projection P:X->Y that is non-injective`

Let

```text
P : X -> Y
```

be non-injective. Then no reconstruction map

```text
R : Y -> X
```

can satisfy

```text
R(P(x)) = x
```

for every `x in X`.

### Proof

Because `P` is non-injective, there exist `x1 != x2` with

```text
P(x1) = P(x2) = y.
```

If a global left inverse existed, then

```text
R(y)=x1
R(y)=x2,
```

which implies `x1=x2`, contradiction.

### UFT-ID consequence

Observation loss and source destruction are different claims. A non-injective observation map creates reconstruction ambiguity even if the source state still exists.

### Repository patterns

QSOL-IMPORT, QSOL-SUBSTRATE, E8_MUSIC, SONIFICATION, and RSH all separate canonical/source objects from projections or receivers.

---

## CR3. Calibration-local classification can flip across profiles

**Class:** `COUNTEREXAMPLE`

**Canonical scope:** `same scalar measurement, same classifier form, different declared local thresholds`

Take one scalar measurement

```text
m = 0.60.
```

Define two otherwise valid calibration profiles:

```text
Gamma_A: threshold theta_A = 0.50
Gamma_B: threshold theta_B = 0.70
```

with classifier

```text
c_Gamma(m) = HIGH if m >= theta_Gamma else LOW.
```

Then

```text
c_A(0.60) = HIGH
c_B(0.60) = LOW.
```

The underlying measured value is unchanged while classification flips.

### UFT-ID consequence

A threshold or diagnostic band cannot be transported between regimes merely because the metric label is unchanged. Calibration transport needs a bridge.

### Repository pattern

RES=RAG v1.1.0 explicitly declares local calibration and forbids treating reported threshold values as universal constants.

---

## CR4. Coprime cyclic stride visits each residue exactly once

**Class:** `PROVED`

**Qualifier:** `established number theory`

**Canonical scope:** `n>=1 and gcd(k,n)=1`

Let `n >= 1` and integer stride `k` satisfy

```text
gcd(k,n)=1.
```

Define

```text
p(i) = k*i mod n,
0 <= i < n.
```

Then `p` is a permutation of the residues `0,...,n-1`.

### Proof

Suppose

```text
k*i = k*j mod n.
```

Then `n` divides `k(i-j)`. Since `gcd(k,n)=1`, `n` divides `i-j`. For `i,j` in the canonical residue range, `i=j`. Therefore `p` is injective on a finite set of size `n`, hence bijective.

### Concrete repository instances

- LATTICE: stride `17` over `27` cells.
- SONIFICATION / ETQ-303: the product step over `Z_101 x Z_3` closes only after all `303` pairs because `gcd(101,3)=1`.

### Nonclaim

A complete deterministic traversal is not a physical law and does not give traversed states equal epistemic authority.

---

## CR5. Finite minimum sufficient basis has a unique deterministic selector

**Class:** `PROVED`

**Canonical scope:** `finite candidate family, finite obligations, at least one sufficient subset, finite non-negative integer costs, fixed total lexicographic tie-break`

Let `R` be a finite candidate set and `Omega` a finite obligation set. Suppose at least one sufficient subset exists. For each sufficient subset `B`, define objective tuple

```text
J(B) = (total_cost(B), |B|, sorted_id_tuple(B)).
```

where costs are finite non-negative integers and the final identifier tuple is compared under a fixed total lexicographic order.

Then there exists a unique selected minimum sufficient basis.

### Proof

The family of sufficient subsets is finite and nonempty. The ordered objective tuple induces a total order because its final component is a fixed total tie-break. Every finite nonempty totally ordered set has a unique minimum.

### UFT-ID consequence

This is a concrete finite specialization of lexicographic recovery/selection. The selected basis is minimum **relative to declared obligations and costs**, not a complete history or proof of the covered claims.

### Repository patterns

QSOL-THOTH historical minimum-set reconstruction and QSOL-ARK minimum-recoverable-substrate selection motivate this specialization.

---

## CR6. Integrity can be exact while semantic truth is false

**Class:** `COUNTEREXAMPLE`

**Qualifier:** `DIAGNOSTIC`

**Canonical scope:** `digest/byte identity is evaluated independently of proposition truth`

Take the exact UTF-8 bytes for the statement

```text
2+2=5
```

and compute a valid SHA-256 digest. The byte identity is deterministic and can be verified perfectly, while the mathematical proposition expressed by the bytes is false.

Therefore

```text
DIGEST_MATCH != TRUTH.
```

### Scope

This is not a criticism of cryptographic hashing. Hashes answer an integrity/identity question. Truth is a separately typed semantic/evidentiary question.

### Repository patterns

QSOL-ORACLE, QSOL-INT, QEC, QSOL-CONTROL, and QSOL-HARNESS independently enforce this separation.

---

## CR7. Deterministic replay follows from deterministic function semantics and identical canonical inputs

**Class:** `PROVED`

**Canonical scope:** `fixed deterministic function/implementation semantics; serialized byte replay requires additional serializer/runtime assumptions`

Let

```text
f_v : X -> Y
```

be a deterministic implementation/model at fixed semantic version `v`.

If canonical inputs are equal,

```text
x_1 = x_2,
```

then

```text
f_v(x_1) = f_v(x_2).
```

### Proof

A mathematical function assigns one output to each input. Equal inputs therefore have equal outputs.

### Scope

Byte-identical serialized artifacts additionally require fixed serialization and relevant runtime/numerical semantics. Live stochastic inference, external services, nondeterministic concurrency, or hidden mutable state fall outside this theorem unless those sources are explicitly fixed.

### Repository patterns

QEC, QSOL-HARNESS, QSOL-NEXUS, RSH, E8_MUSIC, and SONIFICATION all distinguish deterministic proof/replay boundaries from external or stochastic execution.

---

## Promotion ledger

| Result | Status | Lean candidate |
|---|---|---|
| CR1 byte-preserving transport identity | PROVED | later, low priority |
| CR2 non-injective projection reconstruction impossibility | PROVED; qualifier: established mathematics | later |
| CR3 calibration transfer sign/classification flip | COUNTEREXAMPLE | useful finite witness |
| CR4 coprime cyclic traversal | PROVED; qualifier: established number theory | excellent finite lemma |
| CR5 minimum sufficient basis unique selection | PROVED | excellent recovery lemma |
| CR6 digest integrity does not imply truth | COUNTEREXAMPLE; qualifier: DIAGNOSTIC | not a physical theorem target |
| CR7 deterministic replay conditional result | PROVED | trivial but useful contract lemma |

Lean remains deferred under the repository's existing theorem-freeze policy.
