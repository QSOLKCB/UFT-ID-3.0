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

## D4. Scalar residual

When a suitable non-negative distance or violation function exists, define a scalar residual

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

The canonical scalar specialization uses the scalar residual from D4:

```text
Phi(s) = (k/2) * r(s)^2,    k >= 0.
```

A vector-residual specialization is permitted only after introducing a separate residual map

```text
rho : S -> V
```

into a real inner-product space `V`, together with a declared positive-semidefinite self-adjoint operator

```text
K : V -> V.
```

Then

```text
Phi(s) = 1/2 * <rho(s), K rho(s)>.
```

The scalar residual `r` and vector residual `rho` are distinct typed objects and must not be silently interchanged.

Other tension functionals may be used if stated explicitly.

## D6. Critical threshold

`Phi_crit` denotes a declared threshold at which a recovery or regime-switch event is triggered in a thresholded model.

The existence of a universal physical threshold is not assumed.

## D7. Proposed evolution

A proposed evolution is a map or evolution family

```text
F : S -> S
```

in discrete time, or its explicitly declared continuous-time or stochastic analogue.

`F(s)` is the candidate next state before the admissibility audit in the discrete specialization.

## D8. Candidate recovery set

Given proposed state `x`, define the eligible recovery candidates as a specified subset

```text
R_A(x) subseteq A.
```

The simplest finite model uses `R_A(x)=A`.

## D9. Ordered recovery objectives

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

Write regimes as `R_a`, `R_b`, and so forth.

## D20. Transport map

A transport map from regime `a` to regime `b` is defined on a declared ambient source domain

```text
T_ab : D_ab -> S_b,
A_a subseteq D_ab subseteq S_a.
```

The smallest admissible-only specialization chooses `D_ab = A_a`. A larger ambient domain is required for residual-stability theorems that compare transport behavior away from `A_a`.

The transported object may be a state, parameter, assumption, or representation, but its type must be explicit.

## D21. Transport admissibility

For `s in D_ab`, transport is target-admissible when

```text
T_ab(s) in A_b.
```

When a theorem concerns preservation of admissibility, it must additionally state whether the source assumption `s in A_a` is required.

## D22. Transport residual

When the target regime has a suitable distance,

```text
r_T(s) = d_b(T_ab(s), A_b),    s in D_ab.
```

This is distinct from the source residual

```text
r_a(s) = d_a(s, A_a).
```

## D23. Transport shear

Constraint symbols are not reused as invariant maps.

Let

```text
V_a : D_ab -> Z
V_b : S_b  -> Z
```

be declared structural/invariant maps into a common comparison space `Z`, equipped with a distance or divergence `D_Z`. Then a transport distortion may be defined as

```text
kappa_T(s) = D_Z(V_b(T_ab(s)), V_a(s)).
```

If the natural codomains differ, an explicit comparison/bridge map must be introduced before `kappa_T` is defined. No universal formula is assumed.

## D24. Admissible fixed point

A state `s_star` is an admissible fixed point of constrained evolution `G` when

```text
s_star in A
G(s_star) = s_star.
```

## D25. Information-balance forms

A balance equation is model-specific and must match the model's time structure.

### D25a. Differentiable continuous-time form

If `t -> I_t` is differentiable, or absolutely continuous with an almost-everywhere derivative, a candidate decomposition may be written

```text
dI_t/dt = P_I(t) - L_I(t) - B_I(t) + X_I(t)
```

for the times at which the derivative exists.

### D25b. Discrete-time form

For a discrete trajectory `I_n`, use

```text
Delta I_n = I_{n+1} - I_n
          = P_I[n] - L_I[n] - B_I[n] + X_I[n].
```

### D25c. Stochastic form

For a stochastic process `X_t`, the balance must specify the object being differentiated. Examples include an expectation-level identity

```text
d/dt E[I(X_t)] = P_I(t) - L_I(t) - B_I(t) + X_I(t)
```

when the expectation and derivative are well-defined, or a generator/martingale decomposition stated for the chosen stochastic model.

The symbols `P_I`, `L_I`, `B_I`, and `X_I` are placeholders until independently defined from the model dynamics, boundary terms, observation contract, and recovery mechanism. The decomposition is presently a theorem template, not an asserted universal law.

## D26. Restricted infodynamic regime

A restricted infodynamic regime is an explicitly defined class of systems for which the chosen information functional satisfies a declared monotonicity statement under stated assumptions.

Continuous-time form:

```text
dI_t/dt <= 0
```

where the derivative exists.

Discrete-time form:

```text
Delta I_n <= 0.
```

For stochastic models, the exact pathwise, expectation-level, or generator-level monotonicity statement must be declared rather than inferred from the deterministic notation.

## D27. Typed transformation pipeline

A typed transformation pipeline is a finite composable sequence

```text
X_0 --f_0--> X_1 --f_1--> ... --f_{m-1}--> X_m.
```

Intermediate stages remain distinct typed objects even when the total map is written as one composite `F`, `O`, or `T`. Parsing, normalization, projection, routing, resolution, and transport therefore cannot be silently collapsed into identity maps.

See `theory/AUXILIARY_CONTRACTS.md`, A1.

## D28. Canonical content identity

For a declared canonicalization

```text
K : X -> C_X
```

and deterministic digest

```text
h : C_X -> H,
```

define

```text
id_K(x) = h(K(x)).
```

This is identity relative to the canonicalization/digest contract. It does not by itself establish truth, authorship, authenticity, endorsement, or physical validity.

See A2.

## D29. Projection or receiver contract

A projection/receiver is a map

```text
P_i : X -> Y_i
```

with explicitly declared preserved structure, lost structure, observation convention, units/scale where relevant, and invertibility status.

For declared source/receiver observables and comparison map, a receiver defect may quantify preservation of one named structure. Preservation of one structure does not imply preservation of every structure.

See A3.

## D30. Epistemic and authority annotation

Where a model tracks evidence or authority state, use separately typed annotations such as

```text
E : X -> Q_E
A_auth : X -> Q_A.
```

Unless independently derived by a domain model, these are evidence/governance metadata rather than physical observables. Hashes, storage, retrieval score, consensus, model identity, recovery, transport, and replay do not automatically promote them.

See A4.

## D31. Calibration profile

A calibration profile is a declared tuple

```text
Gamma = (M, estimator, preprocessing, units, reference, thresholds, scope).
```

Measurements and classifications may therefore be profile-indexed as

```text
m_Gamma(x), c_Gamma(x).
```

Threshold transfer from `Gamma` to `Gamma'` requires an explicit bridge; equal metric names do not imply equal calibration.

See A5.

## D32. Retention obligation and sufficient basis

For finite candidate set `R` and declared obligation set `Omega`, each record has a coverage set and declared cost. A subset is sufficient only relative to `Omega` when its union of coverage satisfies every obligation.

A minimum sufficient basis is a deterministic selection from sufficient subsets under a declared objective and tie-break. Sufficiency is not completeness or truth.

See A6.

## D33. Deterministic replay contract

A deterministic replay contract declares canonical input identity, implementation identity, versioned parameters, randomness/seed status, output canonicalization, and result identity.

Replay claims apply only inside those assumptions. A receipt around an external stochastic process does not make the underlying process deterministic.

See A7.

## D34. Versioned semantic bridge

For versioned semantics

```text
sigma_v : X_v -> Z_v,
```

a semantic change requires a new contract or an explicit bridge

```text
B_vw : X_v -> X_w
```

that declares preserved and lost structure. Adjacent versions are not compatible by default.

See A8.

## Cross-repository source boundary

D27-D34 were sharpened using recurring patterns observed in public QSOLKCB software repositories. Those implementations motivate typed examples only:

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
```

The pinned source registry and quarantined lineage are in `machine/cross_repo_patterns.json` and `research/CROSS_REPO_PATTERN_ATLAS.md`.
