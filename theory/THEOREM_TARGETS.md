# UFT-ID 3.0 Theorem Targets

These are **targets**, not established results. Each statement must acquire exact hypotheses before proof.

## T1. Finite lexicographic recovery existence and uniqueness

For finite nonempty admissible candidate set `A`, a finite ordered objective tuple, and a fixed total tie-breaking order, `Pi_lex^A(x)` exists and is unique for every `x`.

**Why it matters:** gives the deterministic recovery core a small, clean theorem suitable for later Lean formalization.

## T2. Recovery admissibility

For every state in the domain of `Pi_lex^A`,

```text
Pi_lex^A(x) in A.
```

This should be trivial by construction in the finite model but made explicit because later specializations may use approximate solvers.

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

## T4. Tension reduction under exact projection

For suitable positive-definite `K` and recovery defined by the same residual geometry, establish conditions yielding

```text
Phi(Pi_lex^A(s)) <= Phi(s),
```

with strict decrease for specified inadmissible states.

If the statement is false for general lexicographic secondary objectives, characterize the failure and narrow the theorem.

## T5. Constrained fixed-point characterization

Characterize states satisfying

```text
G(s*) = s*,  s* in A.
```

Separate finite deterministic fixed points from contraction, topological, and order-theoretic fixed-point results.

## T6. Restricted Infodynamic Monotonicity Theorem

For a declared information functional and balance decomposition

```text
dI/dt = P_I - L_I - B_I + X_I,
```

derive sufficient assumptions under which

```text
dI/dt <= 0.
```

The important scientific result is the assumptions. The theorem should make clear whether monotonicity arises from no production, outward flux, dissipative/coarse-graining structure, a contraction property, or another mechanism.

## T7. Positive-derivative counterexample

Construct an explicit valid system satisfying the broadest assumptions commonly associated with an 'information-bearing system' for which the selected information functional has

```text
dI/dt > 0
```

for a nonzero interval or discrete step.

This target is useful only if the information functional and class of systems correspond fairly to the universal claim being tested.

## T8. Zero-derivative example

Construct a nontrivial reversible/permutation/unitary or otherwise information-preserving example with

```text
dI/dt = 0.
```

## T9. Representation-dependence theorem/counterexample

Determine conditions under which

```text
sign(dI/dt)
```

is invariant under a bijective relabeling, and separately construct cases where a change of partition, coarse-graining, alphabet, or reference measure changes the apparent trend.

The result must distinguish a harmless coordinate relabeling from a genuinely different observable or partition.

## T10. Data-processing specialization

Where the selected quantity is relative entropy or mutual information, connect UFT-ID observation maps to established data-processing inequalities rather than reinventing them.

The UFT-ID contribution should be the placement of those inequalities inside the observation/transport architecture, not a claim of novelty for the inequality itself.

## T11. Observer-accessibility decomposition

Under a model that permits a meaningful decomposition, define and characterize accessible versus inaccessible information relative to `O`.

Avoid a naive subtraction identity unless the chosen information measure and sigma-algebras justify it.

## T12. Transport admissibility

For `T_ab : A_a -> S_b`, characterize when

```text
T_ab(A_a) subseteq A_b.
```

If not globally true, characterize the maximal admissible transport domain.

## T13. Transport residual stability

Under suitable regularity assumptions on `T_ab`, establish bounds of the form

```text
r_T(s) <= L * r_a(s) + epsilon
```

or prove that no useful generic bound exists without stronger structure.

## T14. Recovery-information decomposition

Given constrained evolution `G`, separate the information change caused by proposal `F` from the change caused by recovery `Pi_lex`.

A discrete target is

```text
Delta I_total = Delta I_proposal + Delta I_recovery
```

with definitions that make the identity exact rather than rhetorical.

## T15. Restricted-case relation to Vopson's SLI

Once Vopson's exact definitions are reconstructed, formulate a theorem of the form

```text
Vopson-style monotonicity follows from assumptions H1...Hn.
```

If correct, the scientific claim becomes that the Second Law of Infodynamics is a restricted theorem inside a larger balance framework rather than a universal axiom.

If exact reproduction shows that this framing is not mathematically faithful, replace this target rather than forcing the conclusion.

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
