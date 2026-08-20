# Relation, Reachability, Confluence, and Selection Calculus

**Authority:** canonical human mathematical surface for the planned PR #11 relation-first recovery core.  
**Snapshot:** 2026-08-21.

This surface uses a general rewrite relation

\[
\mathrm{stepRel}:X\to X\to\mathsf{Prop}
\]

with admissibility kept separately as

\[
A:X\to\mathsf{Prop}.
\]

The name `stepRel` is deliberate. UFT-ID already reserves `r:S->R_{>=0}` for the scalar residual, so the rewrite relation must not reuse `r` with an incompatible type.

A relation `K subseteq X x A` remains suitable for a direct one-step recovery specialization whose targets are already admissible. It is not the generic carrier for multi-step procedures that may pass through intermediate inadmissible states, cycles, or normalization sequences.

```text
NORMAL != ADMISSIBLE != FIXED_POINT
REACHABLE != ADMISSIBLE != NORMAL != UNIQUE_REACHABLE_NORMAL
```

No physical ontology is attached to `X`, `stepRel`, or `A`.

## 1. Core definitions

### Reachability

Write

\[
x\to^\ast_{\mathrm{stepRel}}y
\]

for the reflexive-transitive closure of `stepRel`.

Planned Lean carrier:

```lean
abbrev Reach (stepRel : X → X → Prop) :=
  Relation.ReflTransGen stepRel
```

This PR does not claim a repository Lean proof.

### Normal form

\[
\operatorname{Normal}_{\mathrm{stepRel}}(x)
\iff
\neg\exists y,\ \mathrm{stepRel}(x,y).
\]

`Normal` means only that no outgoing rewrite step exists. It does not mean admissible, physically stable, correct, true, or a fixed point of another map.

### Admissibility

`A(x)` is independently declared. Neither implication

\[
\operatorname{Normal}_{\mathrm{stepRel}}(x)\Rightarrow A(x)
\]

nor

\[
A(x)\Rightarrow\operatorname{Normal}_{\mathrm{stepRel}}(x)
\]

is generic.

### Fixed point

For a separately declared function `F:X->X`,

\[
\operatorname{Fixed}_F(x)\iff F(x)=x.
\]

A fixed point is not definitionally a normal form of `stepRel`.

### Joinability and confluence

\[
\operatorname{Joinable}_{\mathrm{stepRel}}(x,y)
\iff
\exists z,\ x\to^\ast z\land y\to^\ast z.
\]

\[
\operatorname{Confluent}(\mathrm{stepRel})
\iff
\forall a,b,c,
\ a\to^\ast b\land a\to^\ast c
\Rightarrow
\operatorname{Joinable}_{\mathrm{stepRel}}(b,c).
\]

### Termination

Forward rewriting terminates when no infinite chain

\[
x_0\to x_1\to x_2\to\cdots
\]

exists. The planned Lean orientation is

```lean
def Terminating (stepRel : X → X → Prop) : Prop :=
  WellFounded (Function.swap stepRel)
```

because Lean's `WellFounded` orientation is opposite the displayed forward rewrite direction.

### Normalization predicates

\[
\operatorname{NormalizesFrom}(\mathrm{stepRel},x)
\iff
\exists n,\ x\to^\ast n\land\operatorname{Normal}(n).
\]

\[
\operatorname{AtMostOneReachableNormalFrom}(\mathrm{stepRel},x)
\]

means any two normal forms reachable from `x` are equal.

```text
NORMALIZES_FROM != AT_MOST_ONE_REACHABLE_NORMAL_FROM
```

Existence and uniqueness are separate obligations.

---

## UFT-RW-001 Branchwise invariant induction

**Canonical statement:** `If P(x) and every stepRel-step preserves P, then every state reachable from x by reflexive-transitive closure satisfies P.`

**Canonical hypotheses:** `["stepRel:X->X->Prop", "P:X->Prop", "P(x)", "for all u,v, P(u) and stepRel(u,v) imply P(v)"]`

**Claim class:** `PROVED`.

### Proof

Induct on the finite derivation witnessing reachability. The reflexive case is exactly the assumption `P(x)`. For a derivation ending with `stepRel(u,v)`, the induction hypothesis gives `P(u)` and step preservation gives `P(v)`. Therefore every finitely reachable state satisfies `P`.

```text
STEPWISE_PRESERVATION + INITIAL_PROPERTY
=> REACHABILITY_PRESERVATION

REACHABILITY_PRESERVATION != TERMINATION != CONFLUENCE
```

---

## UFT-RW-002 Right-unique rewriting is confluent

**Canonical statement:** `If stepRel is right-unique, then stepRel is confluent.`

**Canonical hypotheses:** `["stepRel:X->X->Prop", "for all x,y,z, stepRel(x,y) and stepRel(x,z) imply y=z"]`

**Claim class:** `PROVED`.

### Proof

Consider two finite reductions from the same source. Right-uniqueness forces their first successors to agree whenever both exist. Repeating the argument forces agreement at every shared depth. The shorter reduction therefore ends on the longer reduction, so the two endpoints are joinable. Hence every peak is joinable and `stepRel` is confluent.

```text
RIGHT_UNIQUE != TERMINATING
```

---

## UFT-RW-003 Confluence gives at most one reachable normal form

**Canonical statement:** `If stepRel is confluent, then from any common source x, any two reachable normal forms are equal.`

**Canonical hypotheses:** `["stepRel:X->X->Prop", "stepRel is confluent", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal"]`

**Claim class:** `PROVED`.

### Proof

Let `n1` and `n2` be normal forms reachable from `x`. Confluence supplies a common descendant `d`. A normal form has no nontrivial outgoing step, so every descendant reachable from it is itself. Hence `d=n1` and `d=n2`, therefore `n1=n2`.

This proves at most one reachable normal form, not existence.

---

## UFT-RW-004 Termination gives reachable normal-form existence

**Canonical statement:** `If the forward rewrite relation stepRel terminates, every state x reaches at least one normal form.`

**Canonical hypotheses:** `["stepRel:X->X->Prop", "forward rewriting is terminating, equivalently the swapped relation is well-founded"]`

**Claim class:** `PROVED`.

### Proof

Use well-founded induction in the forward-rewrite orientation. For `x`, either no successor exists, in which case `x` is normal and reaches itself, or choose a successor `y`. By the induction hypothesis `y` reaches a normal form `n`; prepend the step `x->y`. Thus `x` reaches a normal form.

The proof is existential. It does not automatically provide a computable normalizer.

```text
EXISTENTIAL_NORMALIZATION_PROOF != COMPUTABLE_NORMALIZATION_ALGORITHM
```

### Derived corollary

**Canonical derived corollary:** `If stepRel terminates and is confluent, then every x has exactly one reachable normal form.`

UFT-RW-003 plus UFT-RW-004 gives:

\[
\operatorname{Terminating}(\mathrm{stepRel})
\land
\operatorname{Confluent}(\mathrm{stepRel})
\Rightarrow
\exists!n,\ x\to^\ast n\land\operatorname{Normal}(n).
\]

This remains a derived corollary rather than another headline theorem ID.

---

## UFT-SEL-001 Distinct reachable normal labels refute unique selection

**Canonical statement:** `If x reaches normal forms n1 and n2 and a label map lambda gives lambda(n1) != lambda(n2), then x does not have at most one reachable normal form; therefore stepRel alone cannot justify a unique-selection claim over lambda.`

**Canonical hypotheses:** `["stepRel:X->X->Prop", "lambda:X->L", "x reaches n1", "x reaches n2", "n1 is normal", "n2 is normal", "lambda(n1) != lambda(n2)"]`

**Claim class:** `PROVED`.

### Proof

Assume `AtMostOneReachableNormalFrom(stepRel,x)`. Since `n1` and `n2` are both reachable normal forms, uniqueness gives `n1=n2`. Applying `lambda` to equal arguments gives `lambda(n1)=lambda(n2)`, contradicting the distinct-label hypothesis. Therefore at-most-one reachable normal form fails, so the declared relation alone cannot justify unique selection over `lambda`.

The theorem is generic. A source-specific scientific application must separately establish the premises.

```text
COMPATIBILITY != REALIZATION != UNIQUE_SELECTION
```

---

## 7. Canonical minimal counterexamples

### CX-RW-FORK3

```text
a -> b
a -> c
```

with `b,c` normal. It terminates but is not confluent, and `a` has two reachable normal forms.

```text
BRANCHING != CONFLUENCE
TERMINATION != CONFLUENCE
TERMINATION != UNIQUE_NORMAL_FORM
ONE_SELECTOR_RESULT != RELATION_SEMANTICS
```

Three states are minimal for a terminating labelled relation with two distinct reachable normal forms.

### CX-RW-LOOP1

```text
a -> a
```

The relation is confluent, nonterminating, and has no normal form.

```text
CONFLUENCE != TERMINATION
CONFLUENCE != NORMAL_FORM_EXISTENCE
```

### CX-RW-EXIT2

```text
a -> a
a -> b
```

with `b` normal. `b` is the unique reachable normal form from `a`, but the infinite self-loop branch never reaches it.

```text
CONFLUENCE != RIGHT_UNIQUENESS
UNIQUE_REACHABLE_NORMAL_FORM != TERMINATION
UNIQUE_REACHABLE_NORMAL_FORM != ALL_PATHS_NORMALIZE
WEAK_NORMALIZATION != STRONG_NORMALIZATION
```

Universal liveness over infinite paths requires path objects and, where relevant, an explicit fairness contract.

---

## 8. Exhaustive finite conformance boundary

`experiments/relation/run.py` exhaustively enumerates every labelled binary relation on each fixed carrier `Fin 1`, `Fin 2`, and `Fin 3`. It does **not** quotient by permutations or graph isomorphism.

\[
2^{1^2}+2^{2^2}+2^{3^2}=2+16+512=530.
\]

The suite checks finite instances of the four foundational implications, the derived unique-normal corollary, fixture properties, and stated minimality boundaries.

```text
FINITE_CONFORMANCE != GENERAL_PROOF
```

The mathematical proofs above are the authority for the general theorems.

---

## 9. Genus 10 / genus 30 selection stress test

`machine/genus_selection_specimen.json` instantiates UFT-SEL-001 with two internal labelled realizations.

Let

\[
\Sigma_g=\#_{h=1}^{g}T^2,
\qquad
\chi(\Sigma_g)=2-2g,
\qquad
\operatorname{rank}H_1(\Sigma_g;\mathbb Z)=2g.
\]

Therefore:

```text
Sigma_10: chi=-18, rank H1=20
Sigma_30: chi=-58, rank H1=60
```

The source provenance is not duplicated here. The canonical cross-repository registry owns it:

- `XR-P17` pins `QSOLKCB/SONIFICATION` `docs/MATHEMATICAL_MODEL.md`, supplying compatibility context for 33 mutually exclusive triality/qutrit blocks plus two singlets, `D3=diag(1,-2,1)`, the `theta=pi/2` kick, and `F3^3=I3`.
- `XR-P18` pins `QSOLKCB/SPECTRAL` `E8/APP/README.md`, supplying placement context for Triality Spiral, qutrit/ternary controls, phi-scaled geometry, and explicit control-geometry boundaries.

The genus specimen references only those canonical XR IDs. These structures may decorate or order labelled handle sectors; they do not construct the surfaces or derive their genus.

An optional placement rule such as

\[
\vartheta_h=\frac{2\pi h}{\phi^2}
\]

is therefore an ordering convention, not a topological theorem.

```text
E8_TRIALITY_COMPATIBILITY != UNIQUE_GENUS
GOLDEN_SPIRAL_PLACEMENT != GENUS_DERIVATION
LABELLED_HANDLE_DECORATION != TOPOLOGY_CONSTRUCTION
PARAMETER != REALIZATION != INVARIANT != DISCRIMINANT != SELECTION
```

The executable fixture is:

```text
common -> M10
common -> M30
lambda(M10) = 10
lambda(M30) = 30
```

with both endpoints normal in the fixture, so UFT-SEL-001 applies immediately.

### External-target boundary

This record does **not** claim that a specific external Genus-10 paper or code package has been refuted. A future source-specific audit may promote the internal stress test into a source-directed counterexample only after exact external claims and implementation are reproducibly identified.

```text
INTERNAL_STRESS_TEST != EXTERNAL_PAPER_REFUTATION
```

---

## 10. What is deliberately deferred

The following remain outside this core surface:

- Newman's lemma;
- selector soundness/completeness and executable normalization;
- observation-compatible quotient dynamics;
- schedule independence;
- trace/history semantics;
- finite-search assurance as a theorem family;
- infinite-path liveness and fairness;
- stochastic rewriting;
- Lean proof objects.

Newman's lemma remains a later target:

\[
\operatorname{Terminating}(\mathrm{stepRel})
\land
\operatorname{LocallyConfluent}(\mathrm{stepRel})
\Rightarrow
\operatorname{Confluent}(\mathrm{stepRel}),
\]

but it is not repository-proved on this surface.

---

## 11. Selection discipline

The reusable epistemic ladder is:

```text
LABEL
-> PARAMETER
-> REALIZATION
-> INVARIANT
-> DISCRIMINANT
-> SELECTION THEOREM
```

An independent reachability ladder is:

```text
REACHABLE
-> ADMISSIBLE
-> NORMAL
-> UNIQUE REACHABLE NORMAL
```

No arrow is automatic. A successful construction proves existence or compatibility at most. A quantity that varies with a parameter is not automatically a discriminant. A diagnostic equal across competing candidates has no selection power over those candidates. A unique-selection claim must discharge an actual uniqueness obligation.

\[
\boxed{
\text{SAME DECLARED INGREDIENTS}
+
\text{DISTINCT NORMAL REALIZATIONS WITH DISTINCT LABELS}
\Rightarrow
\text{NO UNIQUE SELECTION FROM THE DECLARED RELATION ALONE}.
}
\]
