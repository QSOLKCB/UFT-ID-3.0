# Deterministic Observation Calculus

**Status:** PR #9 canonical deterministic observation surface.  
**Claim class:** `DEFINITION` for the surface; individual theorem and counterexample records retain their own canonical claim classes.

This document sharpens D16-D18 for deterministic, set-theoretic observations without importing stochastic, linear, physical, or probabilistic structure.

```text
OBSERVATIONAL_EQUIVALENCE != PHYSICAL_IDENTITY
FIBRE != LINEAR_KERNEL
EXACT_RECONSTRUCTION != PHYSICAL_STATE_SURVIVAL
QUOTIENT_TO_IMAGE != QUOTIENT_TO_FULL_CODOMAIN
MATHEMATICALLY_LEAN_READY != REPOSITORY_LEAN_PROVED
```

The machine authorities are:

```text
machine/observation_contract.json
machine/observation_specs.json
machine/observation_theorems.json
machine/observation_counterexamples.json
```

## ObservationSpec

For this PR an observation is a total deterministic map

\[
O:S\to Y.
\]

The canonical machine record stores only the declared source type, target type, deterministic kind, domain, map reference, scope, claim class, and nonclaims.

The following are **derived from the map** and are not stored as independently editable facts:

- fibres;
- image;
- observational equivalence;
- injectivity;
- surjectivity;
- quotient structure.

No topology, measure, probability, linearity, stochastic kernel, or physical observer interpretation is assumed.

## Fibres and observational equivalence

For `y in Y`, the fibre is

\[
O^{-1}(\{y\})=\{x\in S:O(x)=y\}.
\]

Define

\[
x\sim_O x'\iff O(x)=O(x').
\]

This is the general deterministic notion of observational indistinguishability used by PR #9.

A generic observation also induces what some mathematical libraries call a kernel equivalence relation or kernel pair. UFT-ID human-facing prose uses **observational equivalence** to avoid silently suggesting linear structure.

A linear kernel

\[
\ker O=\{x:O(x)=0\}
\]

is permitted only when the source and target carry the required linear structure and `O` is linear.

```text
LINEAR_KERNEL_REQUIRES_LINEAR_STRUCTURE
```

## UFT-OBS-001 Observational equivalence

**Claim class:** `PROVED`

For any total deterministic function `O:S->Y`, the relation

\[
x\sim_Ox'\iff O(x)=O(x')
\]

is an equivalence relation.

### Proof

Reflexivity follows from `O(x)=O(x)`. Symmetry follows because equality is symmetric. Transitivity follows because if `O(x)=O(y)` and `O(y)=O(z)`, then `O(x)=O(z)`.

For any `x`, its equivalence class is exactly

\[
[x]_O=\{x':O(x')=O(x)\}=O^{-1}(\{O(x)\}).
\]

So the equivalence classes are precisely the nonempty fibres.

## UFT-OBS-002 Quotient-to-image correspondence

**Claim class:** `PROVED`

For any total deterministic `O:S->Y`, there is a canonical bijection

\[
S/{\sim_O}\;\cong\;\operatorname{im}(O).
\]

### Proof

Define

\[
\phi([x])=O(x).
\]

It is well defined because `x~_O x'` means exactly `O(x)=O(x')`.

It is injective because `phi([x])=phi([x'])` implies `O(x)=O(x')`, hence `x~_O x'` and therefore `[x]=[x']`.

It is surjective onto `im(O)` by definition of image: every `y in im(O)` equals `O(x)` for some `x`, hence `y=phi([x])`.

The target is **the image**, not automatically all of `Y`.

A quotient-to-full-codomain bijection requires surjectivity of `O` in addition to the construction above.

## Reconstruction vocabulary

A reconstruction is always relative to a declared observation.

PR #9 distinguishes:

1. **image-scoped exact reconstruction** `R:im(O)->S` with `R(O(x))=x`;
2. **global exact left inverse** `R:Y->S` with `R(O(x))=x`;
3. weaker representative, partial, probabilistic, approximate, or task-specific reconstructions, which are deferred.

The generic word `reconstruction` does not imply exact inversion.

## UFT-OBS-003 Image-scoped exact reconstruction

**Claim class:** `PROVED`

For a total deterministic function `O:S->Y`, the following are equivalent:

1. `O` is injective;
2. there exists `R:im(O)->S` such that `R(O(x))=x` for every `x in S`.

### Proof: reconstruction implies injectivity

Assume such an `R` exists. If `O(x)=O(x')`, then applying `R` gives

\[
x=R(O(x))=R(O(x'))=x'.
\]

Therefore `O` is injective.

### Proof: injectivity gives image-scoped reconstruction

Assume `O` is injective. Every element of `im(O)` has the form `O(x)` for at least one `x`. Define

\[
R(O(x))=x.
\]

This definition is well defined: if `O(x)=O(x')`, injectivity gives `x=x'`. By construction, `R(O(x))=x` for every source state.

Because the reconstruction domain is `im(O)`, no extra nonemptiness assumption on an unused codomain is needed.

## UFT-OBS-004 Noninjective observation blocks global exact reconstruction

**Claim class:** `PROVED`

If `O:S->Y` is noninjective, there is no function `R:Y->S` satisfying

\[
R(O(x))=x
\]

for every `x in S`.

### Proof

Because `O` is noninjective there exist `x != x'` with `O(x)=O(x')`. If a global exact reconstruction existed, then

\[
x=R(O(x))=R(O(x'))=x',
\]

contradiction.

The minimal finite witness is the constant map

```text
Fin2 -> Fin1
0 -> 0
1 -> 0
```

which is executable as `CX-OBS-001`.

This does **not** prohibit weaker reconstruction notions. A noninjective observation may still support representative selection, posterior inference, partial inversion on a restricted domain, or task-specific recovery.

## UFT-OBS-005 Uniform floor sampling

**Claim class:** `PROVED`

For positive integers `L,R`, define

\[
f_{L,R}(i)=\left\lfloor\frac{iL}{R}\right\rfloor,
\qquad i\in\{0,\ldots,R-1\}.
\]

Then `0 <= f(i) < L`.

For output `j in {0,...,L-1}`,

\[
f(i)=j
\]

iff

\[
\frac{jR}{L}\le i<\frac{(j+1)R}{L}.
\]

Therefore the exact fibre size is

\[
|f^{-1}(j)|=
\left\lceil\frac{(j+1)R}{L}\right\rceil-
\left\lceil\frac{jR}{L}\right\rceil.
\]

### Fibre-cardinality proof

The integer values satisfying

\[
a\le i<b
\]

are counted by `ceil(b)-ceil(a)`. Substituting

\[
a=jR/L,\qquad b=(j+1)R/L
\]

gives the displayed formula.

The consecutive interval lengths are all `R/L`, so each fibre has cardinality either

\[
\lfloor R/L\rfloor
\]

or

\[
\lceil R/L\rceil.
\]

### Regime trichotomy

If `R<L`, then `L/R>1`, so consecutive sample positions advance by more than one source-cell width and the floor values are strictly increasing. Hence `f` is injective. Because the domain has fewer elements than the codomain, it is not surjective.

If `R=L`, then

\[
f(i)=\lfloor i\rfloor=i,
\]

so the map is the identity and therefore bijective.

If `R>L`, then `floor(R/L)>=1`, so every output fibre has at least one element by the fibre-cardinality formula. Hence `f` is surjective. Because the domain has more elements than the codomain, it is not injective.

Thus:

| Regime | Injective | Surjective | Bijective |
|---|---:|---:|---:|
| `R<L` | yes | no | no |
| `R=L` | yes | yes | yes |
| `R>L` | no | yes | no |

This family is a compact finite reference model. It is not a foundational definition of observation.

## Counterexamples

### CX-OBS-001 Noninjective observation

`Fin2 -> Fin1` by the constant map shows both collision and impossibility of global exact left inversion.

### CX-OBS-002 Quotient is not unused codomain

For `O:Fin1->Fin2`, `O(0)=0`, the quotient contains one class and `im(O)={0}`, while the codomain contains `{0,1}`. Therefore quotient-to-image is the correct theorem without a surjectivity hypothesis.

### CX-OBS-003 Floor collision

For `L=3,R=5`,

```text
f(0)=0
f(1)=0
```

so floor sampling is not injective in the `R>L` regime.

## Scope and deferrals

PR #9 intentionally excludes:

- stochastic observation kernels;
- measurable-space obligations;
- Blackwell comparison;
- statistical sufficiency;
- sigma-algebra refinement;
- generic reconstruction as a set-valued or probabilistic object;
- recovery operators;
- information-functional comparability;
- representation/congruence invariance;
- Lean implementation.

The mathematics in this document may be suitable for a later Lean milestone, but:

```text
MATHEMATICALLY_LEAN_READY != REPOSITORY_LEAN_PROVED
```

No Lean proof is claimed until a pinned toolchain, theorem manifest, proof source, audit, and CI build exist in the repository.
