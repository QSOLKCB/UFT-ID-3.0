# UFT-ID 3.0 Theorem Targets

These are **targets**, not established results. Each statement must acquire exact hypotheses before proof. Every target includes an adversarial companion question so the theorem queue cannot silently become a confirmation queue.

## T1. Finite lexicographic recovery existence and uniqueness

For finite nonempty admissible candidate set `A`, a finite ordered objective tuple, and a fixed total tie-breaking order, `Pi_lex^A(x)` exists and is unique for every `x`.

**Why it matters:** gives the deterministic recovery core a small, clean theorem suitable for later Lean formalization.

**Adversarial companion:** Which assumption is essential? Remove finiteness, nonemptiness, total tie-breaking, or objective comparability one at a time and construct the smallest failure example.

## T2. Recovery admissibility

For every state in the domain of `Pi_lex^A`,

```text
Pi_lex^A(x) in A.
```

This should be trivial by construction in the finite model but made explicit because later specializations may use approximate solvers.

**Adversarial companion:** Construct an approximate or truncated recovery routine that appears deterministic but returns a state outside `A`, and identify the exact contract violated.

## T3. Residual characterization

For the metric residual

```text
r(s)=d(s,A),
```

identify sufficient conditions under which

```text
r(s)=0 iff s in A.
```

Expected assumptions include nonempty closed `A` in a metric space.

**Adversarial companion:** Give a non-closed admissible set with a point outside `A` but zero distance to `A`.

## T4. Tension reduction under exact recovery

For the scalar tension

```text
Phi(s) = (k/2) r(s)^2
```

or a separately typed vector-residual specialization, establish conditions under which exact recovery yields

```text
Phi(Pi_lex^A(s)) <= Phi(s),
```

with strict decrease for specified inadmissible states.

If the statement is false for general lexicographic secondary objectives, characterize the failure and narrow the theorem.

**Adversarial companion:** Find a recovery objective or residual/tension mismatch for which a lexicographically selected state is admissible but does not minimize the predeclared tension geometry.

## T5. Constrained fixed-point characterization

Characterize states satisfying

```text
G(s*) = s*,  s* in A.
```

Separate finite deterministic fixed points from contraction, topological, and order-theoretic fixed-point results.

**Adversarial companion:** Construct a constrained system with no fixed point but a nontrivial cycle, and identify which additional assumption rules it out.

## T6. Restricted Infodynamic Monotonicity Theorem

For a declared information functional and model-matched balance form, derive sufficient assumptions under which information is non-increasing.

Continuous-time example:

```text
dI_t/dt = P_I - L_I - B_I + X_I <= 0.
```

Discrete-time example:

```text
Delta I_n = P_I[n] - L_I[n] - B_I[n] + X_I[n] <= 0.
```

The important scientific result is the assumptions. The theorem should make clear whether monotonicity arises from no production, outward flux, dissipative/coarse-graining structure, a contraction property, recovery, or another mechanism.

**Adversarial companion:** For every proposed hypothesis set, remove or reverse one hypothesis and search for the smallest valid positive-change example.

## T7. Positive-change counterexample

Construct an explicit valid system satisfying the broadest fairly stated assumptions associated with an "information-bearing system" for which the selected information functional satisfies either

```text
dI_t/dt > 0
```

on a nonzero interval, or

```text
Delta I_n > 0
```

for a discrete step.

This target is useful only if the information functional and class of systems correspond fairly to the universal claim being tested.

**Adversarial companion:** Attempt to strengthen the target claim until the counterexample no longer qualifies; record the first defensible restriction that excludes it.

## T8. Zero-change example

Construct a nontrivial reversible, permutation, unitary, or otherwise information-preserving example with

```text
dI_t/dt = 0
```

or

```text
Delta I_n = 0.
```

**Adversarial companion:** Show that zero change in the selected information functional does not imply every structural observable, correlation, or coarse-grained quantity is constant.

## T9. Representation-dependence theorem/counterexample

Determine conditions under which

```text
sign(dI/dt)
```

or the sign of `Delta I_n` is invariant under a bijective relabeling, and separately construct cases where a change of partition, coarse-graining, alphabet, observation map, or reference measure changes the apparent trend.

The result must distinguish a harmless coordinate relabeling from a genuinely different observable or partition.

**Adversarial companion:** Search for transformations that look cosmetic but actually alter the sigma-algebra, partition, normalization, or reference measure and therefore invalidate the claimed invariance.

## T10. Data-processing specialization

Where the selected quantity is relative entropy or mutual information, connect UFT-ID observation maps to established data-processing inequalities rather than reinventing them.

The UFT-ID contribution should be the placement of those inequalities inside the observation/transport architecture, not a claim of novelty for the inequality itself.

**Adversarial companion:** Identify observation or transport maps that fall outside the hypotheses of the selected data-processing theorem and construct a case where the expected contraction statement fails or is undefined.

## T11. Observer-accessibility decomposition

Under a model that permits a meaningful decomposition, define and characterize accessible versus inaccessible information relative to `O`.

Avoid a naive subtraction identity unless the chosen information measure, sigma-algebras, and decomposition justify it.

**Adversarial companion:** Construct a non-injective observation map for which naive `I_system - I_observed` subtraction is not a valid information identity.

## T12. Transport admissibility

For

```text
T_ab : D_ab -> S_b,
A_a subseteq D_ab subseteq S_a,
```

characterize when

```text
T_ab(A_a) subseteq A_b.
```

If not globally true, characterize the maximal admissible transport domain.

**Adversarial companion:** Construct an apparently natural transport map that preserves labels or coordinates but sends at least one admissible source state outside `A_b`.

## T13. Transport residual stability

For source residual

```text
r_a(s)=d_a(s,A_a)
```

and target transport residual

```text
r_T(s)=d_b(T_ab(s),A_b),
```

with `T_ab` defined on an ambient domain `D_ab` that may contain points outside `A_a`, establish bounds of the form

```text
r_T(s) <= L * r_a(s) + epsilon
```

under suitable regularity and compatibility assumptions, or prove that no useful generic bound exists without stronger structure.

**Adversarial companion:** Find a discontinuous or geometry-mismatched transport map for which arbitrarily small source residual produces large target residual.

## T14. Recovery-information decomposition

Given constrained evolution `G`, separate the information change caused by proposal `F` from the change caused by recovery `Pi_lex`.

A discrete target is

```text
Delta I_total = Delta I_proposal + Delta I_recovery
```

with definitions that make the identity exact rather than rhetorical.

**Adversarial companion:** Construct a case where the decomposition becomes path-dependent, ill-defined, or double-counts a contribution because proposal and recovery are not cleanly separable.

## T15. Restricted-case relation to Vopson's SLI

Once Vopson's exact definitions are reconstructed, formulate a theorem of the form

```text
Vopson-style monotonicity follows from assumptions H1...Hn.
```

If correct, the scientific claim becomes that the Second Law of Infodynamics is a restricted theorem inside a larger balance framework rather than a universal axiom.

If exact reproduction shows that this framing is not mathematically faithful, replace this target rather than forcing the conclusion.

**Adversarial companion:** Search for the strongest faithful formulation of the published SLI that is *not* implied by the candidate UFT-ID hypotheses, and for UFT-ID systems that satisfy the candidate hypotheses while violating the reproduced SLI quantity or interpretation.

## Proof status table

| Target | Status | Lean |
|---|---|---|
| T1 | open | deferred |
| T2 | open | deferred |
| T3 | open | deferred |
| T4 | open | deferred |
| T5 | open | deferred |
| T6 | open | deferred |
| T7 | open | deferred |
| T8 | open | deferred |
| T9 | open | deferred |
| T10 | open | deferred |
| T11 | open | deferred |
| T12 | open | deferred |
| T13 | open | deferred |
| T14 | open | deferred |
| T15 | open | deferred |
