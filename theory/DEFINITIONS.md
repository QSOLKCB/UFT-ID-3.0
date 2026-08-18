# Canonical Definitions

**Status:** working definitions for UFT-ID 3.0. These definitions must be frozen before formal verification begins.

## D1. Total state space

Let `S` denote the set or structured space of all states admitted by a model before legality constraints are applied.

No topology, metric, measure, algebra, or probability structure is assumed unless a theorem explicitly requires one.

## D2. Constraint family

Let `C = {C_j}` denote the declared constraints on states. A constraint may be a predicate, equation, inequality, type condition, conservation condition, or other explicitly defined admissibility test.

## D3. Admissible subspace

The admissible set is

```text
A = { s in S | every hard constraint in C is satisfied by s }.
```

`A` may be discrete or continuous and need not be a linear subspace.

## D4. Residual

When a suitable non-negative distance or violation function exists, define a residual

```text
r : S -> R_{>=0}
```

such that admissible states ideally satisfy `r(s)=0`.

A common metric specialization is

```text
r(s) = d(s, A) = inf_{a in A} d(s,a).
```

The converse `r(s)=0 -> s in A` requires assumptions such as closedness of `A` in a metric setting and is therefore a theorem condition, not part of the definition.

## D5. Tension functional

Given a residual vector `r(s)` and an appropriate positive semidefinite stiffness object `K`, define the quadratic tension candidate

```text
Phi(s) = 1/2 * r(s)^T K r(s).
```

Other tension functionals may be used if stated explicitly.

## D6. Critical threshold

`Phi_crit` denotes a declared threshold at which a recovery or regime-switch event is triggered in a thresholded model.

The existence of a universal physical threshold is not assumed.

## D7. Proposed evolution

A proposed evolution is a map or evolution family

```text
F : S -> S
```

in discrete time, or its continuous/stochastic analogue.

`F(s)` is the candidate next state before the admissibility audit.

## D8. Candidate recovery set

Given proposed state `x`, define the eligible recovery candidates as a specified subset

```text
R_A(x) subseteq A.
```

The simplest finite model uses `R_A(x)=A`.

## D9. Primary recovery objective

Let

```text
J_1(x,a), ..., J_k(x,a)
```

be ordered recovery objectives. Hard admissibility is not traded against these objectives because all candidates are already in `A`.

## D10. Lexicographic recovery

A lexicographic recovery operator

```text
Pi_lex^A : S -> A
```

selects a candidate by minimizing `J_1`, then among ties `J_2`, and so on, with a final fixed total ordering used solely to resolve remaining ties.

Existence and uniqueness depend on the candidate-set assumptions.

## D11. Constrained evolution

A basic constrained discrete evolution is

```text
G(s) = F(s),                    if F(s) in A
G(s) = Pi_lex^A(F(s)),          otherwise.
```

A thresholded variant may delay recovery until a declared event condition is met.

## D12. Recovery event

A recovery event is the ordered pair

```text
E = (s_minus, s_plus)
```

where `s_minus` is the pre-recovery state and `s_plus` is the selected admissible state.

## D13. Impulse object

When subtraction is defined,

```text
Delta = s_minus - s_plus.
```

In a general state space, the event itself or a tangent/displacement object must replace subtraction.

## D14. Information functional

An information functional is an explicitly declared map

```text
I : Domain(I) -> R union {+infinity}
```

or an appropriate extended codomain.

The symbol `I` is intentionally generic. A theorem must identify whether it means Shannon entropy, relative entropy, mutual information, von Neumann entropy, observational entropy, a description-length estimator, or something else.

## D15. Information trajectory

For state trajectory `s(t)`, the information trajectory is

```text
I_t = I(s(t))
```

only when `I` is defined directly on those states. If `I` is defined on distributions or observations, the appropriate induced object must be written explicitly.

## D16. Observation map

An observation or coarse-graining map is

```text
O : S -> Y.
```

`O(s)` is an observer-accessible or representation-level state. No assumption is made that `O` is injective.

## D17. Reconstruction map

Where meaningful, a reconstruction map is

```text
R : Y -> S.
```

It need not invert `O`.

## D18. Representation defect

Given a declared distance `d`, define

```text
delta_M(s) = d(s, R(O(s))).
```

This is representation relative. It does not by itself measure physical information destruction.

## D19. Regime

A regime is a model context containing at least a state domain, constraints, and any calibration or scope conditions needed to interpret quantities.

Write regimes as `Ra`, `Rb`, and so forth.

## D20. Transport map

A transport map from regime `a` to regime `b` is

```text
T_ab : A_a -> S_b.
```

It carries states, parameters, assumptions, or representations between declared regimes.

## D21. Transport admissibility

Transport of `s` is admissible when

```text
T_ab(s) in A_b.
```

## D22. Transport residual

When the target regime has a suitable distance,

```text
r_T(s) = d_b(T_ab(s), A_b).
```

## D23. Transport shear

If comparable invariant maps `C_a` and `C_b` have been defined, a transport distortion may be written schematically as

```text
kappa_T(s) = D_C(C_b(T_ab(s)), C_a(s)).
```

The choice of invariant map and distance `D_C` must be specified. No universal formula is assumed.

## D24. Admissible fixed point

A state `s_star` is an admissible fixed point of constrained evolution `G` when

```text
s_star in A
G(s_star) = s_star.
```

## D25. Information balance decomposition

A candidate information-balance decomposition is an identity of the form

```text
dI/dt = P_I - L_I - B_I + X_I
```

where the meanings of production `P_I`, internal loss `L_I`, boundary flux `B_I`, and constraint/recovery contribution `X_I` are defined for a specific model.

This is presently a theorem target/template, not an asserted universal law.

## D26. Restricted infodynamic regime

A restricted infodynamic regime is any explicitly defined class of systems for which the chosen information functional satisfies

```text
dI/dt <= 0
```

under stated assumptions.

The goal is to derive those assumptions rather than stipulate universality.
