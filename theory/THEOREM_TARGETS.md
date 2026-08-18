# UFT-ID 3.0 Theorem Targets

These are **targets**, not established results unless a bounded specialization is explicitly linked to an established result surface. Each statement must acquire exact hypotheses before proof. Every open target includes an adversarial companion question so the theorem queue cannot silently become a confirmation queue.

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

### Proved finite-valued discrete specialization

For a discrete constrained step

```text
s_n --F--> x_{n+1} --Pi--> s_{n+1}
```

using the same information functional at all three states, if

```text
I(s_n), I(x_{n+1}), I(s_{n+1}) in R,
```

then FR4 proves exactly

```text
Delta I_total = Delta I_proposal + Delta I_recovery.
```

See `theory/FINITE_RESULTS.md`, FR4.

### Remaining open target

Characterize extensions where the information functional may take extended-real values, or where proposal/recovery are continuous, stochastic, path-dependent, overlapping, or otherwise not cleanly separable. Any extension must state when every difference is defined and must avoid expressions such as `+infinity - +infinity`.

**Adversarial companion:** Construct a case where the finite-valued identity becomes undefined, path-dependent, or double-counts a contribution because the functional takes extended-real values or proposal and recovery are not cleanly separable.

## T15. Restricted-case relation to Vopson's SLI

Once Vopson's exact definitions are reconstructed, formulate a theorem of the form

```text
Vopson-style monotonicity follows from assumptions H1...Hn.
```

If correct, the scientific claim becomes that the Second Law of Infodynamics is a restricted theorem inside a larger balance framework rather than a universal axiom.

If exact reproduction shows that this framing is not mathematically faithful, replace this target rather than forcing the conclusion.

**Adversarial companion:** Search for the strongest faithful formulation of the published SLI that is *not* implied by the candidate UFT-ID hypotheses, and for UFT-ID systems that satisfy the candidate hypotheses while violating the reproduced SLI quantity or interpretation.

## T16. Byte-preserving transport identity

For content identity defined by a deterministic canonicalization/digest contract, characterize transport maps that modify transport metadata but preserve exact content bytes.

The finite specialization CR1 establishes that under exact byte preservation, content identity is invariant.

**Adversarial companion:** Permit one byte to change, or change the canonicalization contract, and show exactly which identity statement fails.

## T17. Projection/reconstruction injectivity boundary

Characterize when a projection

```text
P : X -> Y
```

admits a global exact reconstruction `R` satisfying `R(P(x))=x` for all `x`.

CR2 establishes the negative direction: a non-injective projection cannot admit such a global left inverse.

**Adversarial companion:** Construct a non-injective observation with a useful partial or probabilistic reconstruction and show why local usefulness does not restore global exact invertibility.

## T18. Calibration transport

Given calibration profiles

```text
Gamma, Gamma'
```

and profile-indexed measurement/classification rules, state sufficient conditions for a threshold, ordering, or classification to survive transport between profiles.

CR3 supplies the smallest failure pattern: one unchanged scalar measurement can receive opposite classifications under two locally valid thresholds.

**Adversarial companion:** Hold the measurement fixed and vary estimator, units, reference, preprocessing, or threshold individually to identify the weakest bridge that preserves classification.

## T19. Coprime cyclic traversal

For

```text
p(i) = k*i mod n,
```

prove that `gcd(k,n)=1` makes `p` a permutation of the `n` residue classes.

CR4 records a direct finite proof and executable fixtures.

**Adversarial companion:** Use a non-coprime stride and quantify orbit decomposition and coverage loss.

## T20. Minimum sufficient basis selection

For a finite candidate family with finite declared obligations, finite costs, at least one sufficient subset, and a fixed total tie-break, prove existence and uniqueness of the minimum sufficient basis under a declared lexicographic objective.

CR5 establishes this finite specialization.

**Adversarial companion:** Remove nonemptiness, finiteness, finite costs, or total tie-breaking and construct the smallest loss of existence or uniqueness.

## T21. Receiver structural preservation

Given source observable `V_X`, receiver `P`, receiver observable `V_Y`, comparison map `tau`, and declared distance/divergence, characterize exact and approximate preservation through receiver defect

```text
delta_P(x) = d(tau(V_X(x)), V_Y(P(x))).
```

The cross-repository receiver diagnostic demonstrates that uniform scaling can preserve ratios while clipping destroys them.

**Adversarial companion:** Find two reasonable receiver observables for which one declares exact preservation and the other declares loss, demonstrating that preservation is always structure-indexed.

## T22. Deterministic replay boundary

For a fixed deterministic map or implementation semantics and identical canonical inputs, CR7 establishes equal mathematical outputs.

The open target is to characterize the additional conditions required for byte-identical replay across serializers, numerical runtimes, architectures, external services, concurrency models, and stochastic components.

**Adversarial companion:** Hold semantic input fixed while varying one undeclared runtime or serialization assumption and construct the smallest byte-level replay failure.

## Cross-repository source boundary

T16-T22 were sharpened by recurring contracts in public QSOLKCB software repositories. Those software implementations motivate theorem hypotheses and counterexamples only:

```text
SOFTWARE_CONTRACT != PHYSICAL_LAW
IMPLEMENTED_PATTERN != UNIVERSAL_THEOREM
```

Pinned source identities and quarantined lineage are recorded in `machine/cross_repo_patterns.json` and `research/CROSS_REPO_PATTERN_ATLAS.md`.

## Proof status table

| Target | Status | Lean |
|---|---|---|
| T1 | open | deferred |
| T2 | open | deferred |
| T3 | open | deferred |
| T4 | open | deferred |
| T5 | open | deferred |
| T6 | open | deferred |
| T7 | finite witness FR1 | deferred |
| T8 | finite witness FR1 | deferred |
| T9 | finite witness FR3 | deferred |
| T10 | open | deferred |
| T11 | open | deferred |
| T12 | open | deferred |
| T13 | open | deferred |
| T14 | finite-valued discrete case PROVED as FR4; extensions open | deferred |
| T15 | open | deferred |
| T16 | finite specialization PROVED as CR1 | deferred |
| T17 | non-injective impossibility PROVED as CR2; positive characterization open | deferred |
| T18 | transfer theorem open; failure witness CR3 | deferred |
| T19 | PROVED as CR4 / established number theory | deferred |
| T20 | finite specialization PROVED as CR5 | deferred |
| T21 | open; finite receiver diagnostic present | deferred |
| T22 | deterministic-function specialization PROVED as CR7; runtime extensions open | deferred |
