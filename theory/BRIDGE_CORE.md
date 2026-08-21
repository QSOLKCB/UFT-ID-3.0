# BridgeCore: Typed Structural Transport and Composition

**Authority:** canonical human mathematical surface for PR #12 BridgeCore.  
**Snapshot:** 2026-08-21.

BridgeCore formalizes structural transport between declared source and target types. It is deliberately smaller than an application-specific semantic bridge and deliberately weaker than an epistemic authority transition.

```text
BRIDGE != IDENTITY
TRANSPORT != EQUIVALENCE
STRUCTURAL_BRIDGE != EPISTEMIC_PROMOTION
```

## 1. BridgeSpec

Let a bridge be a typed tuple

\[
B=(X_s,X_t,D,R,P,L,\Sigma,v_s,v_t),
\]

corresponding to the machine-facing shape

```text
BridgeSpec = (
  source_type,
  target_type,
  domain,
  map_or_relation,
  preserved_structure,
  lost_structure,
  scope,
  source_version,
  target_version
)
```

where:

- `X_s` and `X_t` are declared source and target types/carriers;
- `D subseteq X_s` is the declared source domain;
- `R subseteq D x X_t` is a typed relation, with a map as the right-unique specialization;
- `P` is the set of declared structure labels preserved by the bridge;
- `L` is the set of declared source structure labels lost by the bridge;
- `Sigma` is a nonempty set of contexts/regimes in which the bridge claim is licensed;
- `v_s` and `v_t` are semantic/version identities.

Require

\[
P\cap L=\varnothing.
\]

A bridge need not be injective, surjective, total outside `D`, invertible, truth-preserving, or physically realized.

```text
PRESERVED_STRUCTURE != ALL_STRUCTURE
LOSSY_BRIDGE != INVERTIBLE_BRIDGE
VERSION_COMPATIBLE != CONTENT_IDENTICAL
```

## 2. Composition compatibility

For

\[
B_1:X_0\rightsquigarrow X_1,
\qquad
B_2:X_1\rightsquigarrow X_2,
\]

ordinary BridgeCore composition is licensed only when all of the following hold:

1. `B1.target_type == B2.source_type`;
2. `B1.target_version == B2.source_version`;
3. every intermediate state produced by `B1` on its declared domain lies in `B2.domain`;
4. `scope(B1) intersect scope(B2)` is nonempty.

Thus matching type names are necessary but not sufficient.

```text
COMPOSABLE_TYPES != SEMANTIC_EQUIVALENCE
TYPE_NAME_MATCH != VERSION_COMPATIBILITY
LOCAL_SCOPE != GLOBAL_SCOPE
```

## UFT-BR-001 Typed relational composition

**Claim class:** `PROVED`

When the compatibility conditions above hold, define

\[
R_{21}(x,z)
\iff
\exists y\;R_1(x,y)\land R_2(y,z).
\]

This is a relation from the source domain of `B1` into the target carrier of `B2`.

**Proof.** For any witness `y`, `R1(x,y)` places `y` in the intermediate carrier. Domain coverage places that `y` in `B2.domain`, so `R2(y,z)` is well-typed and `z` belongs to the target carrier of `B2`. Hence the existential composite is a well-defined typed relation.

This proof establishes structural composability only.

```text
TYPE_CORRECT_COMPOSITION != SEMANTIC_EQUIVALENCE
TYPE_CORRECT_COMPOSITION != PHYSICAL_VALIDATION
```

## UFT-BR-002 Preservation intersection

**Claim class:** `PROVED`

BridgeCore uses a conservative automatic composition rule:

\[
P_{21}=P_1\cap P_2.
\]

**Proof.** A structure label is automatically licensed as preserved by the composite only if the first bridge preserves it into the intermediate representation and the second bridge preserves that same declared structure out of the intermediate representation. Therefore exactly the shared declared preservation set is inherited automatically.

A separately proved reconstruction theorem may justify stronger claims, but ordinary bridge composition does not invent one.

## UFT-BR-003 Loss monotonicity

**Claim class:** `PROVED`

Define the conservative composite loss set by

\[
L_{21}=L_1\cup(P_1\setminus P_2).
\]

Then

\[
L_1\subseteq L_{21}.
\]

and every structure preserved by `B1` but not preserved by `B2` enters `L21`.

**Proof.** Immediate from set union. The formula explicitly contains `L1`, so any structure lost by the first bridge remains in the composite loss declaration. The second term adds structures that survived the first bridge but fail the second preservation contract.

```text
LOST_ONCE != AUTOMATICALLY_RESTORED
DETERMINISTIC_POSTPROCESSING != EXACT_RECONSTRUCTION
```

## UFT-BR-004 Identity neutrality

**Claim class:** `PROVED`

For a declared carrier `X`, version `v`, scope `Sigma`, and tracked structure set `P`, define the identity bridge

\[
I_X=(X,X,X,\{(x,x):x\in X\},P,\varnothing,\Sigma,v,v).
\]

Whenever compatibility holds,

\[
B\circ I_X=B,
\qquad
I_Y\circ B=B
\]

at the relation level and under the conservative preservation/loss metadata rules.

**Proof.** Relational identity is neutral under ordinary relation composition. Intersecting `P_B` with the identity bridge's full tracked preservation set leaves `P_B`; the identity contributes no loss.

A same-named source and target type does not make an arbitrary bridge an identity.

## UFT-BR-005 Associativity

**Claim class:** `PROVED`

For three bridges whose compatibility/domain conditions make both parenthesizations meaningful,

\[
B_3\circ(B_2\circ B_1)
=
(B_3\circ B_2)\circ B_1
\]

under the BridgeCore relation, scope, preservation, and conservative-loss contracts.

**Proof.** Ordinary relational composition is associative by reassociation of the existential intermediate witnesses. Scope composition is set intersection, hence associative. Preservation composition is set intersection, hence associative. For loss propagation,

\[
L_{321}
=L_1\cup(P_1\setminus(P_2\cap P_3)),
\]

which is the same set obtained from either parenthesization because

\[
P_1\setminus(P_2\cap P_3)
=(P_1\setminus P_2)\cup((P_1\cap P_2)\setminus P_3).
\]

This is an abstract structural theorem, not a claim that every application-level interpretation composes associatively.

## 3. Counterexamples

### CX-BR-001 Same endpoint types do not determine one bridge

**Claim class:** `COUNTEREXAMPLE`

Take the same two-element source and target types. One bridge maps the two source states injectively to distinct targets; another collapses both source states to one target. They have identical endpoint type/version declarations but differ in relation, injectivity, and structure loss.

```text
SAME_ENDPOINT_TYPES != SAME_BRIDGE
TYPE_MATCH != STRUCTURE_PRESERVATION
```

### CX-BR-002 Version mismatch blocks composition

**Claim class:** `COUNTEREXAMPLE`

```text
A@1 -> B@1
B@2 -> C@1
```

Each bridge is individually valid. Their intermediate type name agrees, but the semantic/version identity does not. Ordinary BridgeCore composition is therefore rejected.

```text
ADJACENT_VERSION != COMPATIBLE_BY_DEFAULT
```

### CX-BR-003 Disjoint scope blocks composition

**Claim class:** `COUNTEREXAMPLE`

A bridge licensed only in `calibration-A` and a bridge licensed only in `calibration-B` have empty scope intersection even if their type, version, and domain conditions otherwise align.

```text
LOCAL_CALIBRATION != UNIVERSAL_TRANSFER
```

### CX-BR-004 Lossy bridge plus deterministic decoder is not exact reconstruction

**Claim class:** `COUNTEREXAMPLE`

Let the source carrier encode two bits:

```text
00 01 10 11
```

Project to the first bit:

```text
00,01 -> 0
10,11 -> 1
```

then deterministically decode to canonical representatives:

```text
0 -> 00
1 -> 10
```

The composite is total and deterministic, yet `01` and `11` are not reconstructed.

```text
LOSSY_BRIDGE + DETERMINISTIC_DECODER != EXACT_RECONSTRUCTION
TOTAL_COMPOSITE != INVERTIBLE_COMPOSITE
```

## 4. Relationship to existing UFT-ID surfaces

BridgeCore generalizes the typed transport discipline already staged in `A8. Versioned semantic bridge` while retaining the earlier receiver and calibration boundaries.

It does not subsume the relation core. A bridge relation connects declared source and target types; `stepRel:X->X->Prop` remains the generic endorelation for relation-first recovery.

It also does not subsume the deterministic observation calculus. An observation map can be represented by a BridgeSpec when transport semantics are the question, but observational equivalence and reconstruction remain owned by the observation authority.

## 5. Explicit deferrals

PR #12 does **not** define:

- epistemic promotion/demotion or evidence authority transitions;
- representation-specific similarity/congruence classes;
- information comparability;
- stochastic/measurable bridge kernels;
- empirical measurement validity;
- physical ontology;
- Lean proof objects.

Those remain staged for later roadmap surfaces.

```text
STRUCTURAL_BRIDGE != EPISTEMIC_BRIDGE
FORMAL_BRIDGE != MEASUREMENT_BRIDGE
BRIDGE_CONFORMANCE != EMPIRICAL_VALIDATION
```

## 6. Executable evidence boundary

The finite witness checks the declared fixtures, exhaustively checks associativity for all `16^3 = 4096` ordered triples of labelled binary relations on `Fin2`, and checks the conservative preservation/loss formulas over a bounded three-label structure family.

```text
FINITE_BRIDGE_CONFORMANCE != GENERAL_PROOF
```

The proofs above are the mathematical authority. The executable suite is an independent bounded conformance witness.
