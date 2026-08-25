# Lean Observation Foundation — Source Theorem Freeze

**Status:** `SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF`  
**Claim class:** `DEFINITION`  
**Batch:** `LEAN-OBS-BATCH-001`

This document freezes the first source theorem batch intended for the later Lean 4 observation foundation. It does **not** contain Lean proof objects and does not claim repository-level Lean verification.

The source authority remains the merged PR #9 deterministic observation calculus. This freeze records exact theorem statements, hypotheses, formalization scope, nonclaims, dependency edges, adversarial companions, and the expected future Lean module/declaration map.

```text
MATHEMATICAL_PROOF != LEAN_PROOF
SOURCE_THEOREM != LEAN_ARTIFACT
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
LEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION
UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED
```

After this freeze PR merges, the next gate is exact merged-`main` CI plus hostile review, followed by an immutable source-release tag of that exact commit/tree. Lean proof implementation must target that tag rather than moving `main`.

## Frozen source authority

**Basis commit:** `6f3aeb7f4ac14389e7a08d2976c8c0d16549c093`

Canonical machine freeze:

```text
machine/lean_observation_foundation_contract.json
```

Frozen PR9 source authorities include the central machine contract, formalization contract, observation contract/spec/theorem/counterexample registries, the canonical human proof surface, validator, finite witness implementation, tests, deterministic receipt runner, and the roadmap as they existed at the basis commit. Their exact Git blob identities are stored in the machine freeze. `machine/contract.json` and `ROADMAP.md` are basis-only pins because PR #21 intentionally advances their live copies after the PR9 source basis; the freeze therefore verifies their basis-commit objects rather than pretending the new live bytes were part of PR9.

## Batch selection

Frozen in batch 001:

```text
UFT-OBS-001
UFT-OBS-002
UFT-OBS-003
UFT-OBS-004
```

Deferred to a later Lean batch:

```text
UFT-OBS-005
```

`UFT-OBS-005` is deferred because its floor/ceiling arithmetic and finite sampling trichotomy form a separable arithmetic module. Deferral does not revoke its existing `PROVED` source status.

```text
UFT-OBS-005_DEFERRED != UFT-OBS-005_DROPPED
```

## UFT-OBS-001 Observational equivalence

**Source claim class:** `PROVED`  
**Canonical statement:** `For any function O:S->Y, define x~_O y iff O(x)=O(y). Then ~_O is an equivalence relation on S, and the equivalence class of x equals the fibre O^{-1}({O(x)}).`  
**Canonical hypotheses:** `["O is a total deterministic function S->Y"]`  
**Formalization scope:** `set-theoretic deterministic observation only`  
**Source nonclaims:** `["Observational equivalence is not physical identity."]`  
**Proof reference:** `theory/OBSERVATION_CALCULUS.md#uft-obs-001-observational-equivalence`  
**Theorem dependencies:** `[]`  
**Counterexample dependencies:** `[]`  
**Expected Lean module:** `UFTID.Observation.Basic`  
**Expected Lean path:** `UFTID/Observation/Basic.lean`  
**Expected Lean declaration:** `uft_obs_001_observational_equivalence`  
**Lean status:** `NOT_IMPLEMENTED`

## UFT-OBS-002 Quotient-to-image correspondence

**Source claim class:** `PROVED`  
**Canonical statement:** `For any function O:S->Y, the quotient S/~_O is canonically bijective with im(O), via [x] |-> O(x).`  
**Canonical hypotheses:** `["O is a total deterministic function S->Y"]`  
**Formalization scope:** `set-theoretic deterministic observation only`  
**Source nonclaims:** `["The quotient is not canonically the full codomain Y unless O is surjective."]`  
**Proof reference:** `theory/OBSERVATION_CALCULUS.md#uft-obs-002-quotient-to-image-correspondence`  
**Theorem dependencies:** `["UFT-OBS-001"]`  
**Counterexample dependencies:** `["CX-OBS-002"]`  
**Expected Lean module:** `UFTID.Observation.Quotient`  
**Expected Lean path:** `UFTID/Observation/Quotient.lean`  
**Expected Lean declaration:** `uft_obs_002_quotient_to_image`  
**Lean status:** `NOT_IMPLEMENTED`

## UFT-OBS-003 Image-scoped exact reconstruction iff injective

**Source claim class:** `PROVED`  
**Canonical statement:** `For any function O:S->Y, O is injective iff there exists R:im(O)->S such that R(O(x))=x for every x in S.`  
**Canonical hypotheses:** `["O is a total deterministic function S->Y", "Reconstruction is scoped to im(O)"]`  
**Formalization scope:** `set-theoretic deterministic observation only`  
**Source nonclaims:** `["Exact mathematical reconstruction does not establish that an original physical state persisted or was observed directly."]`  
**Proof reference:** `theory/OBSERVATION_CALCULUS.md#uft-obs-003-image-scoped-exact-reconstruction`  
**Theorem dependencies:** `[]`  
**Counterexample dependencies:** `["CX-OBS-001"]`  
**Expected Lean module:** `UFTID.Observation.Reconstruction`  
**Expected Lean path:** `UFTID/Observation/Reconstruction.lean`  
**Expected Lean declaration:** `uft_obs_003_image_reconstruction_iff_injective`  
**Lean status:** `NOT_IMPLEMENTED`

## UFT-OBS-004 Noninjective observation blocks global exact reconstruction

**Source claim class:** `PROVED`  
**Canonical statement:** `If O:S->Y is noninjective, no function R:Y->S can satisfy R(O(x))=x for every x in S.`  
**Canonical hypotheses:** `["O is a total deterministic function S->Y", "O is noninjective"]`  
**Formalization scope:** `set-theoretic deterministic observation only`  
**Source nonclaims:** `["Noninjectivity does not forbid partial, representative, probabilistic, or task-specific reconstruction."]`  
**Proof reference:** `theory/OBSERVATION_CALCULUS.md#uft-obs-004-noninjective-observation-blocks-global-exact-reconstruction`  
**Theorem dependencies:** `["UFT-OBS-003"]`  
**Counterexample dependencies:** `["CX-OBS-001"]`  
**Expected Lean module:** `UFTID.Observation.Reconstruction`  
**Expected Lean path:** `UFTID/Observation/Reconstruction.lean`  
**Expected Lean declaration:** `uft_obs_004_noninjective_no_global_left_inverse`  
**Lean status:** `NOT_IMPLEMENTED`

## Dependency graph

```text
UFT-OBS-001
  -> UFT-OBS-002

UFT-OBS-003
  -> UFT-OBS-004
```

`UFT-OBS-002` uses observational equivalence as the quotient relation. `UFT-OBS-004` is placed after the image-scoped reconstruction/injectivity result so the later Lean package may reuse that abstraction rather than duplicate reconstruction semantics.

Adversarial companions remain separately typed:

```text
CX-OBS-001 -> UFT-OBS-003, UFT-OBS-004
CX-OBS-002 -> UFT-OBS-002
```

Counterexamples are not theorem premises and executable witnesses are not Lean proofs.

## Expected Lean module map

```text
UFTID.Observation.Basic
  UFTID/Observation/Basic.lean
  UFT-OBS-001

UFTID.Observation.Quotient
  UFTID/Observation/Quotient.lean
  depends on UFTID.Observation.Basic
  UFT-OBS-002

UFTID.Observation.Reconstruction
  UFTID/Observation/Reconstruction.lean
  depends on UFTID.Observation.Basic
  UFT-OBS-003
  UFT-OBS-004
```

This is a **module map**, not proof source. No Lean/Lake/Mathlib version is selected in this phase.

## Release boundary

The source-release tag is intentionally absent from this freeze because the tag must identify the exact merged commit/tree containing this manifest.

```text
FREEZE PR MERGED
  -> EXACT MERGED-MAIN CI + HOSTILE REVIEW
  -> IMMUTABLE SOURCE-RELEASE TAG
  -> QSOL-CONTEXT TARGET BINDING
  -> PIN LEAN / LAKE / MATHLIB
  -> LEAN PROOF IMPLEMENTATION
```

Until the immutable tag exists, no later `.lean` proof may be treated as the canonical formalization target for this batch.
