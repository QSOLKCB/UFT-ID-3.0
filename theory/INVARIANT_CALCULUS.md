# Canonical Invariant Calculus

**Status:** PR #8 formalization authority.  
**Claim class:** `DEFINITION` for the generic calculus. Individual registry entries retain their own claim classes and statuses.

The purpose of this surface is to prevent one word, *invariant*, from hiding several mathematically different claims.

```text
INVARIANT_UNDER_F != UNIVERSAL_INVARIANT
EXACT_INVARIANT != NUMERICAL_CONFORMANCE
REPLAY_INVARIANT != PHYSICAL_CONSERVATION
EPISTEMIC_NON_PROMOTION != PHYSICAL_DYNAMICS
```

## Generic record

For types `X` and `Y`, a UFT-ID invariant specification is

```text
InvSpec[X,Y] =
(
  id,
  name,
  domain,
  codomain,
  transformation,
  hypotheses,
  property,
  break_conditions,
  kind,
  scope,
  status,
  claim_class,
  source_lineage,
  nonclaims
)
```

Mathematically, the core pattern is:

\[
f:X\to Y,\qquad H:X\to\mathsf{Prop},\qquad P:X\times Y\to\mathsf{Prop},
\]

with intended validity

\[
\forall x\in X,\quad H(x)\land \neg B(x)\Longrightarrow P(x,f(x)).
\]

`B` is specification metadata for known break/failure conditions. It could be absorbed into a stronger hypothesis, but keeping it explicit preserves the useful engineering distinction between ordinary validity assumptions and known named failure modes. Break conditions never substitute for proof.

## Typed specializations

The machine registry permits:

- `exact`
- `approximate`
- `representation`
- `transport`
- `statistical`
- `replay`
- `epistemic-non-promotion`
- `contract`

Typical mathematical forms include:

\[
q(f(x))=q(x)
\]

for an exact endomorphic invariant,

\[
d(q(f(x)),q(x))\le \varepsilon(x)
\]

for an approximate invariant,

\[
q(g\cdot x)=q(x)
\]

for a representation action,

\[
q_b(Tx)=q_a(x)
\]

for structural transport, and

\[
E_b(Tx)\preceq E_a(x)
\]

for an explicitly authority-neutral epistemic bridge.

The last two examples have different semantics. The existence of one record shape does not collapse their domains.

## Initial executable surface

### UI-INV-002 — exact quarter-turn invariant

Let

\[
\operatorname{rot}_{90}(x,y)=(-y,x),
\qquad
q(x,y)=x^2+y^2.
\]

For arbitrary integers `x,y`,

\[
\begin{aligned}
q(\operatorname{rot}_{90}(x,y))
&=q(-y,x)\\
&=(-y)^2+x^2\\
&=y^2+x^2\\
&=x^2+y^2\\
&=q(x,y).
\end{aligned}
\]

Hence

\[
\forall(x,y)\in\mathbb Z^2,\quad q(\operatorname{rot}_{90}(x,y))=q(x,y).
\]

This algebraic derivation is the proof of the universally quantified `Z^2` claim. The PR #8 runner separately checks a concrete integer case as an implementation/conformance witness. The executable fixture is not being promoted into the universal proof.

### UI-INV-003 — scaling adversary

For nonzero `v`,

\[
q(2v)=4q(v)\ne q(v).
\]

Therefore `q is invariant` is incomplete without naming the transformation class.

### UI-INV-004 — observer-dependent entropy sign under fixed dynamics

Use initial fine distribution

\[
p_0=(0,0,\tfrac14,\tfrac34)
\]

and the declared row-stochastic transition kernel

\[
K=
\begin{pmatrix}
1&0&0&0\\
0&1&0&0\\
0&1&0&0\\
0&\tfrac13&0&\tfrac23
\end{pmatrix}.
\]

With row-vector convention,

\[
p_1=p_0K=(0,\tfrac12,0,\tfrac12).
\]

Fine Shannon entropy rises:

\[
\Delta H_{\mathrm{fine}}>0.
\]

Under partition

\[
\{0,2\}\mid\{1,3\},
\]

the observed entropy falls, while under

\[
\{0,1\}\mid\{2,3\},
\]

it rises.

The experiment computes `p1` from `p0` and this single declared kernel, then applies both observers to that same fine trajectory. Only the observation partition changes between the observer comparisons.

Hence:

```text
INFORMATION_FUNCTIONAL
!= OBSERVATION_MAP
!= TIME_EVOLUTION
```

and `sign(Delta H)` is not observer-independent without an observation contract.

## Claim-realization invariant

A repository may write the word `reversible` while implementing no inverse. PR #8 therefore treats claimed structure as an obligation, not as evidence:

```text
CLAIMED_STRUCTURE
!= DECLARED_STRUCTURE
!= IMPLEMENTED_STRUCTURE
!= VERIFIED_STRUCTURE
```

`machine/definition_obligations.json` defines the required evidence for reversible maps, implemented dimensionality, dynamics and scientific simulation.

## Composition rule

A future composition theorem may state:

> If `q` is invariant under `f` and under `g`, and the hypotheses required for `g` are preserved by `f`, then `q` is invariant under `g ∘ f`.

The hypothesis-preservation clause is mandatory. PR #8 records this as a theorem target rather than silently promoting the engineering phrase “compositional safety” into a universal theorem.

## Source boundary

Positive public methodological lineage in this PR is referenced through the canonical `machine/cross_repo_patterns.json` IDs, including QEC boundary/replay discipline, NEXUS authority separation, QSOL-IMPORT normalization boundaries, and HARNESS execution-evidence gating. Private author-supplied research inputs remain design inputs only.

No private attachment identifier, attachment hash or private source locator is published.

```text
METHODOLOGICAL_INPUT != SOURCE_AUTHORITY
SOFTWARE_INVARIANT != PHYSICAL_LAW
```
