# Relation, Reachability, Confluence, and Selection Calculus

**Authority:** canonical human mathematical surface for the planned PR #11 relation-first recovery core.  
**Snapshot:** 2026-08-21.

This surface replaces an overstrong direct-recovery carrier with the smallest general abstract-rewriting object needed for multi-step recovery:

\[
r:X\to X\to\mathsf{Prop}.
\]

Admissibility is separate:

\[
A:X\to\mathsf{Prop}.
\]

The distinction is mandatory. A relation `K subseteq X x A` is suitable for a direct one-step recovery relation whose targets are already admissible. It is not a general carrier for procedures that may pass through intermediate inadmissible states, cycles, or normalization sequences.

```text
NORMAL != ADMISSIBLE != FIXED_POINT
REACHABLE != ADMISSIBLE != NORMAL != UNIQUE_REACHABLE_NORMAL
```

No physical ontology is attached to `X`, `r`, or `A`.

## 1. Core definitions

### Reachability

Write

\[
x\to^\ast_r y
\]

for the reflexive-transitive closure of `r`.

Equivalently,

\[
\operatorname{Reach}_r(x,y)\iff r^\ast(x,y).
\]

Reflexivity matters: every state reaches itself in zero steps.

Planned Lean carrier:

```lean
abbrev Reach (r : X → X → Prop) :=
  Relation.ReflTransGen r
```

This is a theorem target for the later Lean track. This PR does not claim a repository Lean proof.

### Normal form

\[
\operatorname{Normal}_r(x)
\iff
\neg\exists y,\ r(x,y).
\]

`Normal` means only "no outgoing rewrite step."

It does not mean admissible, recovered, physically stable, correct, true, or a fixed point of some separately declared function.

### Admissibility

\[
A(x)
\]

is an independently declared predicate. Neither implication

\[
\operatorname{Normal}_r(x)\Rightarrow A(x)
\]

nor

\[
A(x)\Rightarrow\operatorname{Normal}_r(x)
\]

is generic.

### Fixed point

For a separately declared function \(F:X\to X\),

\[
\operatorname{Fixed}_F(x)\iff F(x)=x.
\]

A fixed point is not definitionally a normal form of `r`.

### Joinability

\[
\operatorname{Joinable}_r(x,y)
\iff
\exists z,\ x\to^\ast_r z\land y\to^\ast_r z.
\]

### Confluence

\[
\operatorname{Confluent}(r)
\iff
\forall a,b,c,\ 
a\to^\ast_r b\land a\to^\ast_r c
\Longrightarrow
\operatorname{Joinable}_r(b,c).
\]

### Termination

Forward rewriting is terminating when no infinite chain

\[
x_0\to x_1\to x_2\to\cdots
\]

exists.

For the planned Lean orientation:

```lean
def Terminating (r : X → X → Prop) : Prop :=
  WellFounded (Function.swap r)
```

The swap is not cosmetic. Lean's `WellFounded q` is oriented against infinite predecessor chains, so forward rewrite notation must be translated deliberately.

### Normalization predicates

\[
\operatorname{NormalizesFrom}(r,x)
\iff
\exists n,\ x\to^\ast_r n\land\operatorname{Normal}_r(n).
\]

\[
\operatorname{AtMostOneReachableNormalFrom}(r,x)
\iff
\forall n_1,n_2,\ 
\begin{aligned}
&x\to^\ast_r n_1\land x\to^\ast_r n_2\\
&{}\land\operatorname{Normal}_r(n_1)
\land\operatorname{Normal}_r(n_2)
\end{aligned}
\Longrightarrow n_1=n_2.
\]

Their conjunction supplies exactly one reachable normal form.

```text
NORMALIZES_FROM
!=
AT_MOST_ONE_REACHABLE_NORMAL_FROM
```

Existence and uniqueness are separate obligations.

---

## UFT-RW-001 Branchwise invariant induction

**Canonical statement:** `If P(x) and every r-step preserves P, then every state reachable from x by reflexive-transitive closure satisfies P.`

**Canonical hypotheses:** `["r:X->X->Prop", "P:X->Prop", "P(x)", "for all u,v, P(u) and r(u,v) imply P(v)"]`

**Claim class:** `PROVED`.

### Proof

Proceed by induction on a finite derivation witnessing \(x\to^\ast_r y\).

For the reflexive case \(y=x\), the conclusion is the hypothesis \(P(x)\).

For a derivation ending in one further rewrite \(u\to_r v\), the induction hypothesis gives \(P(u)\). Step preservation then gives \(P(v)\).

Therefore every finitely reachable state satisfies `P`.

The executable finite suite checks this surrounding relation machinery but is not the proof of the general theorem.

```text
STEPWISE_PRESERVATION
+ INITIAL_PROPERTY
=> REACHABILITY_PRESERVATION

REACHABILITY_PRESERVATION
!= TERMINATION
!= CONFLUENCE
```

---

## UFT-RW-002 Right-unique rewriting is confluent

**Canonical statement:** `If r is right-unique, then r is confluent.`

**Canonical hypotheses:** `["r:X->X->Prop", "for all x,y,z, r(x,y) and r(x,z) imply y=z"]`

**Claim class:** `PROVED`.

### Proof

Assume `r` is right-unique. Consider two finite reductions from the same source:

\[
a=x_0\to x_1\to\cdots\to x_m=b
\]

and

\[
a=y_0\to y_1\to\cdots\to y_n=c.
\]

Right-uniqueness forces \(x_1=y_1\) whenever both first steps exist. Applying the same argument repeatedly shows that the two sequences agree at every depth common to both.

If \(m\le n\), then \(b=x_m=y_m\) and the remaining suffix of the second reduction witnesses

\[
b\to^\ast_r c.
\]

Thus `c` is a common descendant of `b` and `c`. The case \(n\le m\) is symmetric.

Hence every peak is joinable, so `r` is confluent.

A deterministic relation may still loop forever:

```text
RIGHT_UNIQUE != TERMINATING
```

---

## UFT-RW-003 Confluence gives at most one reachable normal form

**Canonical statement:** `If r is confluent, then from any common source x, any two reachable normal forms are equal.`

**Canonical hypotheses:** `["r:X->X->Prop", "r is confluent", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal"]`

**Claim class:** `PROVED`.

### Proof

Let \(n_1,n_2\) be normal forms reachable from the same source `x`.

Confluence supplies a common descendant `d`:

\[
n_1\to^\ast_r d,
\qquad
n_2\to^\ast_r d.
\]

Because \(n_1\) is normal, it has no nontrivial outgoing rewrite. Therefore the only reachable descendant of \(n_1\) is itself, so \(d=n_1\). The same reasoning gives \(d=n_2\).

Hence

\[
n_1=n_2.
\]

This theorem proves **at most one** reachable normal form. It does not prove existence.

---

## UFT-RW-004 Termination gives reachable normal-form existence

**Canonical statement:** `If the forward rewrite relation r terminates, every state x reaches at least one normal form.`

**Canonical hypotheses:** `["r:X->X->Prop", "forward rewriting is terminating, equivalently the swapped relation is well-founded"]`

**Claim class:** `PROVED`.

### Proof

Use well-founded induction with respect to forward reduction.

Fix `x`. Either there is no `y` with \(x\to_r y\), in which case `x` is normal and reaches itself reflexively.

Otherwise choose a successor `y` with \(x\to_r y\). By the induction hypothesis, `y` reaches some normal form `n`. Prepending \(x\to_r y\) gives

\[
x\to^\ast_r n.
\]

Thus every state reaches at least one normal form.

The proof is existential. Selecting an arbitrary successor inside a proof does not automatically provide a computable normalization algorithm.

```text
EXISTENTIAL_NORMALIZATION_PROOF
!= COMPUTABLE_NORMALIZATION_ALGORITHM
```

### Derived corollary

Combining UFT-RW-003 and UFT-RW-004:

\[
\operatorname{Terminating}(r)
\land
\operatorname{Confluent}(r)
\Longrightarrow
\exists!n,\
x\to^\ast_r n
\land
\operatorname{Normal}_r(n).
\]

This is a derived corollary, not another independently advertised theorem ID.

---

## UFT-SEL-001 Distinct reachable normal labels refute unique selection

**Canonical statement:** `If x reaches normal forms n1 and n2 and a label map lambda gives lambda(n1) != lambda(n2), then x does not have at most one reachable normal form; therefore r alone cannot justify a unique-selection claim over lambda.`

**Canonical hypotheses:** `["r:X->X->Prop", "lambda:X->L", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal", "lambda(n1) != lambda(n2)"]`

**Claim class:** `PROVED`.

### Proof

Assume for contradiction

\[
\operatorname{AtMostOneReachableNormalFrom}(r,x).
\]

Since \(n_1\) and \(n_2\) are both reachable normal forms, the definition gives

\[
n_1=n_2.
\]

Applying the function \(\lambda\) to equal arguments gives

\[
\lambda(n_1)=\lambda(n_2),
\]

contradicting the hypothesis that the labels differ.

Therefore

\[
\neg\operatorname{AtMostOneReachableNormalFrom}(r,x).
\]

A unique-selection claim over `lambda` cannot be obtained from the declared relation alone.

The theorem is intentionally generic. Establishing its premises for a particular scientific paper, program, or physical model requires separately sourced evidence.

```text
COMPATIBILITY
!= REALIZATION
!= UNIQUE_SELECTION
```

---

## 7. Canonical minimal counterexamples

### CX-RW-FORK3

```text
a -> b
a -> c
```

with `b` and `c` normal.

This relation terminates but is not confluent, and `a` has two reachable normal forms.

It establishes:

```text
BRANCHING != CONFLUENCE
TERMINATION != CONFLUENCE
TERMINATION != UNIQUE_NORMAL_FORM
ONE_SELECTOR_RESULT != RELATION_SEMANTICS
```

Three states are minimal for a terminating unlabelled relation with two distinct reachable normal forms.

### CX-RW-LOOP1

```text
a -> a
```

There is only one reachable state, so confluence holds. The self-loop gives nontermination and no normal form.

```text
CONFLUENCE != TERMINATION
CONFLUENCE != NORMAL_FORM_EXISTENCE
```

If a later specialization requires irreflexive rules, use a two-state cycle. Do not impose irreflexivity merely to hide the smaller counterexample.

### CX-RW-EXIT2

```text
a -> a
a -> b
```

with `b` normal.

`b` is the unique reachable normal form from `a`, but the infinite branch

```text
a -> a -> a -> ...
```

never reaches it.

Therefore:

```text
CONFLUENCE != RIGHT_UNIQUENESS
UNIQUE_REACHABLE_NORMAL_FORM != TERMINATION
UNIQUE_REACHABLE_NORMAL_FORM != ALL_PATHS_NORMALIZE
WEAK_NORMALIZATION != STRONG_NORMALIZATION
```

This also shows why finite reachability alone cannot define a property such as `all_branches_eventually_admissible`. Universal liveness over infinite paths requires path objects and, where relevant, an explicit fairness contract.

---

## 8. Exhaustive finite conformance boundary

`experiments/relation/run.py` exhaustively enumerates every unlabelled binary relation on `Fin 1`, `Fin 2`, and `Fin 3`:

\[
2^{1^2}+2^{2^2}+2^{3^2}
=
2+16+512
=
530.
\]

The suite checks the finite instances of:

- branchwise invariant induction for every predicate subset of each finite carrier;
- right-unique implies confluent;
- confluent implies at most one reachable normal form from each source;
- terminating implies normalization from every source;
- terminating plus confluent implies exactly one reachable normal form from every source;
- the minimality boundaries for `FORK3`, `LOOP1`, and `EXIT2`.

This is bounded implementation conformance and counterexample minimization evidence.

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

The general theorems above stand on their mathematical proofs.

---

## 9. Genus 10 / genus 30 selection stress test

`machine/genus_selection_specimen.json` instantiates UFT-SEL-001 with two internal labelled realizations.

Let

\[
\Sigma_g=\#_{h=1}^g T^2.
\]

Then

\[
\chi(\Sigma_g)=2-2g,
\qquad
\operatorname{rank}H_1(\Sigma_g;\mathbb Z)=2g.
\]

For the two fixtures:

\[
\chi(\Sigma_{10})=-18,
\qquad
\operatorname{rank}H_1(\Sigma_{10})=20,
\]

and

\[
\chi(\Sigma_{30})=-58,
\qquad
\operatorname{rank}H_1(\Sigma_{30})=60.
\]

The public SONIFICATION ETQ-101 specification supplies compatibility context containing 33 complete mutually exclusive triality/qutrit blocks plus two singlets, the local operator

\[
D_3=\operatorname{diag}(1,-2,1),
\]

the \(\theta=\pi/2\) phase kick, and the exact local identity

\[
F_3^3=I_3.
\]

Thus one may allocate 10 such blocks to 10 labelled handle sectors or 30 blocks to 30 labelled handle sectors while leaving the topology itself defined independently.

The public SPECTRAL E8 Geometry Studio supplies separate placement/composition context including a `Triality Spiral`, qutrit/ternary controls, and \(\phi\)-scaled geometry. An optional ordering rule may therefore be declared, for example,

\[
\vartheta_h=\frac{2\pi h}{\phi^2},
\]

without pretending that the spiral derives the genus.

The source pins are machine-recorded as **compatibility context only**. They are not premises of UFT-SEL-001 and they do not import E8, qutrit, cosmological, or physical ontology into UFT-ID.

```text
E8_TRIALITY_COMPATIBILITY != UNIQUE_GENUS
GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION
LABELLED_HANDLE_DECORATION != TOPOLOGY_CONSTRUCTION
PARAMETER != REALIZATION != INVARIANT != DISCRIMINANT != SELECTION
```

The executable fork is:

```text
common -> M10
common -> M30
```

with both endpoints normal in the declared fixture and with labels

```text
lambda(M10) = 10
lambda(M30) = 30
```

so UFT-SEL-001 applies immediately.

### External-target boundary

This repository record does **not** claim that a specific external Genus-10 paper or code package has been refuted. No such external package is pinned by this record. A future source-specific audit may promote the internal stress test into a source-directed counterexample only after the exact source claims and implementation are reproducibly identified.

```text
INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION
```

---

## 10. What is deliberately deferred

The following do not belong on this core surface yet:

- Newman's lemma;
- selector soundness/completeness and executable normalization;
- observation-compatible quotient dynamics;
- schedule independence;
- trace or history semantics;
- finite-search assurance as a theorem family;
- infinite-path liveness and fairness;
- stochastic rewriting;
- Lean proof objects.

Newman's lemma remains a valid later theorem target:

\[
\operatorname{Terminating}(r)
\land
\operatorname{LocallyConfluent}(r)
\Longrightarrow
\operatorname{Confluent}(r),
\]

but it will not be advertised as repository-proved until a complete checked proof is supplied.

---

## 11. Selection discipline

The relation core adds a reusable epistemic type ladder:

```text
LABEL
-> PARAMETER
-> REALIZATION
-> INVARIANT
-> DISCRIMINANT
-> SELECTION THEOREM
```

and an independent reachability ladder:

```text
REACHABLE
-> ADMISSIBLE
-> NORMAL
-> UNIQUE REACHABLE NORMAL
```

No arrow is automatic.

A successful construction proves existence or compatibility at most. A quantity that varies with a parameter is not automatically a discriminant. A diagnostic equal to one for every candidate cannot select among them. A unique-selection claim must ultimately discharge a uniqueness obligation.

That is the reusable UFT-ID result:

\[
\boxed{
\text{SAME DECLARED INGREDIENTS}
+
\text{DISTINCT ADMISSIBLE NORMAL REALIZATIONS}
\Rightarrow
\text{NO UNIQUE SELECTION WITHOUT AN EXTRA HYPOTHESIS}.
}
\]
