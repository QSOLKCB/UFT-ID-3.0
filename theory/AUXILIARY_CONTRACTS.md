# UFT-ID 3.0 Auxiliary Contracts

**Status:** formal-core auxiliary definitions.

These definitions sharpen how the canonical tuple

```text
U = (S, A, F, Pi_lex, O, T, I, C)
```

is used in multi-stage, provenance-sensitive, receiver-dependent, calibrated, and replayable systems.

They do **not** enlarge the canonical tuple. They are typed contracts for common specializations of `F`, `O`, `T`, `C`, and the evidence surrounding them.

The motivating engineering examples are catalogued in `research/CROSS_REPO_PATTERN_ATLAS.md`. Their software semantics are examples only:

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
```

## A1. Typed transformation pipeline

A transformation pipeline is a finite sequence of typed maps

```text
X_0 --f_0--> X_1 --f_1--> ... --f_{m-1}--> X_m.
```

No equality between stages is assumed merely because the same payload or claim is discussed at several stages.

Examples include source-to-parse, parse-to-normalization, route-to-resolution, resolution-to-transport, or source-to-receiver chains.

For a composite

```text
F = f_{m-1} o ... o f_0,
```

claims about `F` must still identify which intermediate maps are lossy, non-injective, stochastic, authority-changing by explicit rule, or undefined on part of the domain.

This is an auxiliary typing discipline for `F`, `O`, and `T`, not a new dynamical law.

## A2. Canonicalization and content identity

Let

```text
K : X -> C_X
```

be a declared canonicalization map into a canonical representation space `C_X`.

A content identity may then be defined by a digest function

```text
h : C_X -> H
```

as

```text
id_K(x) = h(K(x)).
```

A cryptographic specialization may use SHA-256, but UFT-ID does not privilege a particular digest in the abstract definition.

Content identity establishes equivalence under the declared canonicalization/digest contract. It does not by itself establish:

```text
truth
authorship
authenticity
endorsement
physical validity
```

Those require separately typed evidence.

## A3. Projection / receiver contract

A receiver or projection is a map

```text
P_i : X -> Y_i.
```

Each receiver must declare:

```text
preserved_structure
lost_structure
observation convention
units / scale if applicable
invertibility status
```

Given source structural observable

```text
V_X : X -> Z_X,
```

a receiver observable

```text
V_i : Y_i -> Z_i,
```

and comparison map

```text
tau_i : Z_X -> Z_i,
```

define receiver defect

```text
delta_i(x) = d_i(tau_i(V_X(x)), V_i(P_i(x))).
```

Exact preservation of the declared structure means `delta_i(x)=0` over the declared domain.

A receiver may preserve one structure exactly and destroy another. Therefore deterministic output or aesthetic usefulness does not make a receiver physically privileged.

## A4. Epistemic and authority annotations

Where a model tracks evidence status, let

```text
E : X -> Q_E
A_auth : X -> Q_A
```

be explicit epistemic and authority annotations.

These annotations are metadata or governance state unless a domain model derives them otherwise.

They must not be inferred solely from:

```text
content hash
storage position
retrieval score
consensus count
model/provider identity
geometric address
successful recovery
successful transport
successful replay
```

If a transformation changes `E` or `A_auth`, the promotion/demotion rule must be explicit and independently justified.

This definition prevents integrity, availability, popularity, or preservation from being silently reinterpreted as truth.

## A5. Calibration profile

A calibration profile is a declared tuple

```text
Gamma = (M, estimator, preprocessing, units, reference, thresholds, scope).
```

A profile-indexed measurement or classifier is written

```text
m_Gamma(x)
c_Gamma(x).
```

Threshold values are local to `Gamma` unless an explicit bridge proves transfer to another profile `Gamma'`.

Thus

```text
theta_Gamma = theta_Gamma'
```

is not assumed merely because the two profiles use similarly named metrics.

Calibration transport belongs under the general regime-transport discipline.

## A6. Retention obligation and sufficient basis

Let `R={r_1,...,r_n}` be a finite candidate record set and let `Omega` be a finite set of declared retention obligations.

Each candidate has a coverage set

```text
cover(r_i) subseteq Omega
```

and a non-negative declared cost

```text
c(r_i) >= 0.
```

A subset `B subseteq R` is sufficient when

```text
union_{r in B} cover(r) = Omega.
```

A deterministic minimum sufficient basis may minimize the ordered tuple

```text
(total_cost(B), |B|, lexicographic_id_tuple(B)).
```

This is sufficiency relative to `Omega`, not completeness of the original source or proof that covered claims are true.

## A7. Deterministic replay contract

A replay contract contains at least:

```text
canonical input identity
implementation identity
versioned parameters
random seed or declaration of no randomness
output canonicalization
result identity
```

For a deterministic implementation

```text
f_v : X -> Y,
```

repeating the same canonical input under the same implementation semantics yields the same mathematical output:

```text
x = x'  =>  f_v(x) = f_v(x').
```

Byte-identical artifact replay additionally depends on serialization/runtime assumptions declared by the implementation contract.

A receipt around a live stochastic or external process does not make that process deterministic or replayable.

## A8. Versioned semantic bridge

Let a versioned contract expose semantics

```text
sigma_v : X_v -> Z_v.
```

A semantic change creates a new domain/codomain contract unless an explicit bridge

```text
B_vw : X_v -> X_w
```

is supplied with preserved and lost structure.

Compatibility must therefore be stated relative to an explicit version pair and domain.

```text
ADJACENT_VERSION != COMPATIBLE_BY_DEFAULT
```

Version numbers, labels, or neighboring implementations do not supply a bridge automatically.

## Relationship to the canonical tuple

These auxiliary contracts fit the existing architecture as follows:

| Auxiliary contract | Canonical slots |
|---|---|
| typed pipeline | `F`, `O`, `T` |
| canonicalization / identity | `C`, evidence around `F/O/T` |
| projection / receiver | `O`, `T` |
| epistemic/authority annotation | evidence metadata; not automatically physical state |
| calibration profile | regime metadata for `I`, `O`, `T`, thresholds |
| sufficient basis | finite specialization of candidate selection / `Pi_lex` |
| replay contract | evidence around deterministic `F` and experiments |
| semantic bridge | `T`, bridge obligations |

The tuple remains unchanged because these are refinements of how its maps and evidence contracts are specified, not new universal ontological objects.
