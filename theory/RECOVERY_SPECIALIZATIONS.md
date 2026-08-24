# Recovery Specializations

**Claim class:** mixed `DEFINITION`, `PROVED`, `COUNTEREXAMPLE`, and `NONCLAIM` surface.

This phase specializes the existing relation-first recovery core. It does **not** replace `stepRel` with a function and does not reinterpret a generic relation as deterministic merely because one deterministic recovery policy is later chosen.

```text
GENERIC_RELATION != DETERMINISTIC_SELECTOR
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
```

The base relation authority remains `machine/relation_contract.json`.

## 1. Selector specialization

Let

```text
stepRel : X -> X -> Prop
sigma   : X -> X
```

where `sigma` is a total deterministic selector. Define the **effective selector relation**

```text
Sel_sigma(x,y) iff sigma(x)=y and y!=x.
```

A fixed point `sigma(x)=x` means the selector halts at `x`; it is not silently inserted into `stepRel` as a self-loop.

The selector is **relation-sound** when

```text
sigma(x) != x  =>  stepRel(x, sigma(x)).
```

Relation soundness is a separate obligation from determinism.

```text
DETERMINISTIC != RELATION_SOUND
```

## 2. Progress and executable normalization

A natural-number progress certificate is

```text
rho : X -> N
```

with

```text
sigma(x) != x  =>  rho(sigma(x)) < rho(x).
```

When selector fixed points are exactly the `stepRel`-normal states, relation soundness plus strict natural-rank descent turns selector iteration into an executable normalizer.

```text
RELATION_SOUND != TERMINATING
EXISTENTIAL_NORMALIZATION != EXECUTABLE_NORMALIZER
```

This specialization deliberately keeps the base relation semantics visible. A selector may choose one branch of a nonconfluent relation without making the unchosen branch disappear.

```text
TERMINATING_SELECTOR != BASE_RELATION_CONFLUENT
SELECTOR_NORMAL_FORM != UNIQUE_RELATION_NORMAL_FORM
```

## 3. Finite lexicographic specialization

For a finite nonempty recovery candidate set `R_A(x)`, let

```text
J_1(x,a), ..., J_k(x,a)
```

be an ordered finite objective tuple. Minimize `J_1`, then `J_2`, and so on. If candidates remain tied, use a declared fixed total candidate order as the final tie-break.

That last order is part of the algorithmic contract. Without it, a tied argmin can remain set-valued.

```text
OBJECTIVE_MINIMUM != UNIQUE_SELECTION_WITHOUT_TIEBREAK
```

This is the executable specialization of the earlier D8-D10 candidate-set and lexicographic-recovery definitions. It does not establish a unique physical selection principle.

---

## UFT-REC-001 A deterministic selector induces a right-unique effective relation

**Claim class:** `PROVED`

**Canonical statement:** `For any total selector sigma:X->X, the effective selector relation Sel_sigma(x,y) iff sigma(x)=y and y!=x is right-unique.`

**Canonical hypotheses:** `["sigma:X->X is a total function"]`

**Canonical nonclaims:** `["Right-uniqueness of the selector-induced relation does not make the underlying generic stepRel right-unique, terminating, or confluent."]`

**Proof.** If `Sel_sigma(x,y)` and `Sel_sigma(x,z)`, then both `y=sigma(x)` and `z=sigma(x)`, hence `y=z`. The `y!=x` condition only removes halting self-pairs and does not affect uniqueness. ∎

## UFT-REC-002 Relation-sound selector iteration preserves base reachability

**Claim class:** `PROVED`

**Canonical statement:** `If every non-fixed selector step sigma(u)=v is a stepRel(u,v), then every finite selector iterate sigma^k(x) is reachable from x by the reflexive-transitive closure of stepRel.`

**Canonical hypotheses:** `["sigma:X->X is total", "for all u, sigma(u)!=u implies stepRel(u,sigma(u))", "k is a natural number"]`

**Canonical nonclaims:** `["Relation-soundness does not imply that selector iteration terminates or that all branches of stepRel follow the selector."]`

**Proof.** Induct on `k`. At `k=0`, reachability is reflexive. For the successor step, if the current selector state is fixed then the iterate is unchanged. Otherwise relation soundness supplies one `stepRel` edge, and transitivity of reflexive-transitive closure appends it to the induction hypothesis. ∎

## UFT-REC-003 Natural-rank descent terminates deterministic selector iteration

**Claim class:** `PROVED`

**Canonical statement:** `If rho:X->N and every non-fixed selector step strictly decreases rho, then selector iteration from x reaches a fixed point after at most rho(x) non-fixed steps.`

**Canonical hypotheses:** `["sigma:X->X is total", "rho:X->N", "for all u, sigma(u)!=u implies rho(sigma(u))<rho(u)"]`

**Canonical nonclaims:** `["Termination under a declared natural-number rank does not establish confluence of the base relation or applicability to continuum and stochastic systems."]`

**Proof.** Every non-fixed step strictly decreases a natural number. A strictly decreasing natural-number chain beginning at `rho(x)` has at most `rho(x)` decreases. Therefore another non-fixed step cannot exist after that bound, so a fixed point has been reached. ∎

## UFT-REC-004 Sound rank-certified selectors give executable normalizers

**Claim class:** `PROVED`

**Canonical statement:** `If a total selector is relation-sound, its fixed points are exactly the stepRel-normal states, and a natural-number rank strictly decreases on every non-fixed selector step, then deterministic selector iteration defines an executable normalizer that returns a reachable normal form for every input.`

**Canonical hypotheses:** `["sigma:X->X is total", "for all u, sigma(u)!=u implies stepRel(u,sigma(u))", "for all u, sigma(u)=u iff u is stepRel-normal", "rho:X->N", "for all u, sigma(u)!=u implies rho(sigma(u))<rho(u)"]`

**Canonical nonclaims:** `["The returned selector normal form need not be the unique normal form reachable under the underlying relation when that relation branches."]`

**Proof.** UFT-REC-003 gives finite arrival at a selector fixed point. By the fixed-point/normal-state equivalence that endpoint is `stepRel`-normal. UFT-REC-002 makes the endpoint reachable in the base relation. Because `sigma` is a function, the iteration and endpoint are deterministic. None of these steps removes other base-relation branches. ∎

## UFT-REC-005 Finite lexicographic recovery is unique with a final total tie-break

**Claim class:** `PROVED`

**Canonical statement:** `For a finite nonempty candidate set, lexicographic minimization of a finite ordered objective tuple followed by a fixed total candidate order returns exactly one candidate.`

**Canonical hypotheses:** `["the candidate set is finite and nonempty", "each objective is defined on every candidate", "the objective list is finite and ordered", "the final tie-break is a fixed total order containing every candidate exactly once"]`

**Canonical nonclaims:** `["A unique lexicographic selector result is a property of the declared objectives and tie-break contract, not a unique-selection theorem for the unspecialized relation or for nature."]`

**Proof.** The finite nonempty candidate set has at least one lexicographically minimal objective tuple. The minimizers of that tuple form a finite nonempty subset. A fixed total order has exactly one least element on any finite nonempty subset, giving one selected candidate. ∎

---

## 4. Adversarial counterexamples

### CX-REC-001 Existential normalization is not an executable normalizer

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `The terminating fork a->b and a->c has reachable normal forms b and c, so normal-form existence alone does not specify which normal form an executable recovery procedure must return.`

**Canonical nonclaims:** `["The fixture does not prevent adding a separately declared deterministic selector; it shows that the relation alone does not contain one."]`

Fixture: `a -> b`, `a -> c`, with both `b` and `c` normal.

### CX-REC-002 Deterministic does not imply relation-sound

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A total deterministic selector can map a to c even when the declared base relation contains only a->b, so determinism alone does not make selector steps licensed relation steps.`

**Canonical nonclaims:** `["The counterexample concerns relation soundness only; an unrelated deterministic function remains a valid function."]`

### CX-REC-003 A relation-sound deterministic selector can loop

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `On the two-cycle 0->1->0, the deterministic selector sigma(0)=1 and sigma(1)=0 is relation-sound but never reaches a fixed point.`

**Canonical nonclaims:** `["The fixture does not refute termination when a valid well-founded progress certificate is supplied."]`

### CX-REC-004 Objective minimization without a total tie-break can remain set-valued

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `If two finite recovery candidates have identical values for every declared objective and no final total tie-break is supplied, objective minimization leaves both candidates tied and does not define a unique selector result.`

**Canonical nonclaims:** `["Equal objective values are not a defect; the counterexample rejects only an undeclared promotion from a tied argmin set to a unique selector."]`

### CX-REC-005 A deterministic selector does not make the base relation confluent

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `Adding a selector that chooses b on the fork a->b and a->c yields a deterministic terminating selector path to b while c remains a distinct reachable normal form of the base relation, so selector determinism does not prove base-relation confluence or unique normal form.`

**Canonical nonclaims:** `["The selector specialization may intentionally choose one branch; it simply must not rewrite the semantics of the underlying relation."]`

---

## 5. Bounded executable conformance

The reference battery exhausts every total function on `Fin1`, `Fin2`, and `Fin3`:

```text
1^1 + 2^2 + 3^3 = 32 selectors.
```

It cross-checks those selectors against every labelled relation on the same carriers:

```text
1*2 + 4*16 + 27*512 = 13,890 selector/relation pairs.
```

Of those, the executable reference finds exactly:

```text
4,134 relation-sound selector/relation pairs
739 relation-sound pairs where selector fixed points equal relation normals
9 index-rank-decreasing selector controls
23 state-level normalization checks
336 finite lexicographic selection checks
```

The counts are finite reference-model conformance, not general proof objects. The mathematical proofs above stand independently of these bounded enumerations.

```text
FINITE_SELECTOR_CONFORMANCE != GENERAL_RECOVERY_THEORY
EXECUTABLE_NORMALIZER != EMPIRICAL_RECOVERY
```
