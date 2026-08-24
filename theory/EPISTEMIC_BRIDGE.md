# Epistemic Bridge Specialization

**Authority:** canonical human mathematical surface for planned PR #13, delivered in GitHub PR #14.  
**Snapshot:** 2026-08-24.  
**Claim scope:** abstract epistemic bookkeeping and authority transport only.

The Epistemic Bridge layer specializes BridgeCore without turning structural transport into an evidence ladder.

```text
STRUCTURAL_TRANSPORT != AUTHORITY_PROMOTION
RETRIEVED != VERIFIED
INFERRED != VERIFIED
EXECUTED != VERIFIED
VERIFIED != TRUE
CONFLICT != UNKNOWN
CONFLICT != FALSE
VERIFIED != CONFLICT_FREE
NO_GLOBAL_EPISTEMIC_LATTICE
```

## 1. EpistemicState

Use a factorized state

```text
EpistemicState = (
  evidence_refs,
  retrieved_refs,
  inference_refs,
  verification_receipts,
  execution_receipts,
  conflict_refs,
  scope
)
```

where every field except `scope` may be empty and `scope` is nonempty.

The fields are deliberately orthogonal. The model does **not** define one total order over labels such as `unknown`, `retrieved`, `inferred`, `verified`, `executed`, and `conflict`.

A nonempty retrieval, inference, verification, execution, or conflict field requires at least one evidence reference. This is an integrity condition on the finite representation, not a claim that the evidence is true.

Derived predicates are:

```text
Unknown(E)  iff all authority/evidence fields are empty
Conflict(E) iff conflict_refs(E) is nonempty
Verified(E) iff verification_receipts(E) is nonempty
Executed(E) iff execution_receipts(E) is nonempty
```

Therefore conflict and verification may coexist, while conflict and unknown cannot coexist in a valid state.

## 2. Structural transport specialization

For a BridgeCore bridge `B` and epistemic state `E`, define authority-neutral transport by copying all epistemic evidence/authority fields exactly and restricting scope:

```text
scope(E') = scope(E) intersect scope(B)
```

Transport is licensed only when the intersection is nonempty.

No retrieval, inference, verification, execution, conflict, or evidence reference is created merely because bytes or structure crossed a valid BridgeCore bridge.

```text
BYTE_IDENTITY != AUTHORITY_IDENTITY
STRUCTURAL_COMPATIBILITY != EVIDENCE_UPGRADE
DETERMINISTIC_TRANSPORT != VERIFICATION
```

## UFT-EP-001 Authority-neutral structural transport

**Claim class:** `PROVED`

**Canonical statement:** `A licensed authority-neutral BridgeCore transport preserves every epistemic evidence/authority field exactly and may only restrict scope by intersection.`

**Canonical hypotheses:** `["E is a valid EpistemicState", "B is a BridgeCore bridge", "scope(E) intersect scope(B) is nonempty"]`

**Proof.** By definition, transport copies `evidence_refs`, `retrieved_refs`, `inference_refs`, `verification_receipts`, `execution_receipts`, and `conflict_refs` unchanged. Only the scope field is replaced by an intersection. Hence no authority-bearing field is promoted, demoted, or invented by structural transport.

## UFT-EP-002 Verification requires an explicit verification receipt

**Claim class:** `PROVED`

**Canonical statement:** `Within the Epistemic Bridge operations, retrieve, infer, execute, conflict-recording, and structural transport do not create verification receipts; verification status changes only through an explicit verification operation carrying a receipt.`

**Canonical hypotheses:** `["all operations start from valid EpistemicState values", "verification is represented only by verification_receipts"]`

**Proof.** Inspect the operation definitions. `retrieve`, `infer`, `execute`, `add_conflict`, and `transport` leave `verification_receipts` unchanged. `verify` alone adjoins a declared receipt. Thus verification cannot arise from successful transport or adjacent activity.

## UFT-EP-003 Conflict is distinct from unknown

**Claim class:** `PROVED`

**Canonical statement:** `For every valid EpistemicState, Conflict(E) implies not Unknown(E).`

**Canonical hypotheses:** `["E is a valid EpistemicState", "nonempty conflict_refs requires nonempty evidence_refs"]`

**Proof.** `Conflict(E)` gives a nonempty conflict set. Validity then requires nonempty evidence references. `Unknown(E)` requires every evidence/authority field to be empty. The predicates are therefore disjoint.

## UFT-EP-004 Repeated neutral transport cannot accumulate authority

**Claim class:** `PROVED`

**Canonical statement:** `Any finite composition of licensed authority-neutral transports preserves the epistemic authority vector exactly; only scope may monotonically narrow.`

**Canonical hypotheses:** `["every transport step is licensed", "every step uses authority-neutral Epistemic Bridge transport"]`

**Proof.** Apply UFT-EP-001 inductively. Each step leaves every evidence/authority field invariant. Scope is repeatedly intersected, so it cannot expand.

## UFT-EP-005 Scope is non-expansive under transport

**Claim class:** `PROVED`

**Canonical statement:** `For licensed transport E -> E', scope(E') is a subset of both scope(E) and the bridge scope.`

**Canonical hypotheses:** `["scope(E) intersect scope(B) is nonempty"]`

**Proof.** Immediate from the definition `scope(E') = scope(E) intersect scope(B)`.

## 3. Counterexamples

### CX-EP-001 Retrieved is not verified

**Claim class:** `COUNTEREXAMPLE`

A state may contain a retrieved source reference and evidence reference while `verification_receipts` remains empty.

```text
RETRIEVED != VERIFIED
```

### CX-EP-002 Inferred is not verified

**Claim class:** `COUNTEREXAMPLE`

A state may record an inference and its premise/evidence reference without a verification receipt.

```text
INFERRED != VERIFIED
```

### CX-EP-003 Executed is not verified

**Claim class:** `COUNTEREXAMPLE`

A state may contain an execution receipt and evidence reference while remaining unverified.

```text
EXECUTED != VERIFIED
```

### CX-EP-004 Conflict is not unknown

**Claim class:** `COUNTEREXAMPLE`

A state with evidence-backed incompatible observations has `Conflict(E)` true and `Unknown(E)` false.

```text
CONFLICT != UNKNOWN
```

### CX-EP-005 Verified conflict is representable

**Claim class:** `COUNTEREXAMPLE`

A verification receipt can establish that a particular source/evidence object was checked while incompatible evidence remains recorded. Thus `Verified(E)` and `Conflict(E)` may both be true.

```text
VERIFIED != CONFLICT_FREE
VERIFIED != TRUE
```

## 4. Finite conformance surface

The executable model enumerates six presence bits:

```text
evidence
retrieved
inferred
verified
executed
conflict
```

for `2^6 = 64` raw vectors.

Validity requires any non-evidence activity bit to imply the evidence bit. The valid normalized presence shapes are therefore:

```text
1 unknown shape
+ 32 evidence-backed factor combinations
= 33 valid shapes
```

The executable battery checks all 64 raw vectors, all 33 valid shapes, each counterexample, explicit verification, neutral transport, repeated transport, and scope non-expansion.

```text
FINITE_EPISTEMIC_CONFORMANCE != GENERAL_EPISTEMOLOGY
FORMAL_VERIFICATION_RECEIPT != TRUTH
```

## 5. Deferrals

This phase does not define:

- a universal confidence score;
- a total epistemic order or global lattice;
- source credibility as a scalar truth oracle;
- Bayesian or Dempster-Shafer semantics;
- representation congruence or similarity classes;
- information comparability;
- empirical measurement validity;
- physical ontology;
- Lean proof objects.

Those remain separate later surfaces.
