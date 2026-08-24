# Empirical Falsification Profile

**Canonical claim class:** `DEFINITION`

This phase specializes the PR8 `FalsificationSpec` scaffold into a typed decision contract for empirical evidence. It does not turn synthetic fixtures, formal counterexamples, reproduced arithmetic, or a successful fit into empirical validation.

The base scaffold remains `machine/falsification_contract.json`. This layer adds the evidence identity, uncertainty, versioning, and decision semantics required before a scoped rejection can be licensed.

## Canonical profile

```text
EmpiricalFalsificationProfile = (
  profile_id,
  hypothesis_id,
  hypothesis_version,
  claim_class,
  scope,
  observable_id,
  measurement_spec_id,
  calibration_id,
  uncertainty_model,
  prediction,
  null_model,
  rejection_rule,
  evidence_requirements,
  decision_policy,
  prior_registration_status,
  profile_version
)
```

Evidence is separately typed:

```text
EmpiricalEvidence = (
  observable_id,
  measurement_spec_id,
  calibration_id,
  value,
  uncertainty_radius,
  provenance_refs,
  profile_fingerprint
)
```

The profile fingerprint binds every decision-bearing profile field, including the rejection threshold. Changing that threshold creates a different profile identity. A fingerprint proves content identity only; it does not prove that the profile existed before evidence was observed. The synthetic profile therefore fixes `prior_registration_status` to `EXTERNAL_UNVERIFIED_ASSUMPTION`.

```text
PROFILE_FINGERPRINT != PREREGISTRATION_PROOF
```

## Decision envelope

```text
INVALID_EVIDENCE
INCONCLUSIVE
REJECTED_IN_SCOPE
NOT_REJECTED_IN_SCOPE
```

`INVALID_EVIDENCE` means the declared procedure cannot evaluate the evidence. `INCONCLUSIVE` means valid uncertainty overlaps both decision regions. `REJECTED_IN_SCOPE` is a scoped procedural label. In this synthetic conformance profile it explicitly carries external-unverified registration status and no empirical-rejection licence. `NOT_REJECTED_IN_SCOPE` is deliberately not a confirmation state.

For the exact synthetic interval control:

```text
measurement interval = [value - radius, value + radius]

lower > threshold   -> REJECTED_IN_SCOPE
upper <= threshold  -> NOT_REJECTED_IN_SCOPE
otherwise           -> INCONCLUSIVE
```

The interval rule is a conformance fixture only. It is not a general statistical-confidence rule.

---

## UFT-EFP-001 Empirical rejection requires complete profile-matched evidence

**Claim class:** `PROVED`

**Canonical statement:** `Under the declared EmpiricalFalsificationProfile semantics, any evidence record with missing, malformed, or mismatched observable identity, measurement-spec identity, calibration identity, uncertainty, provenance, or profile fingerprint evaluates to INVALID_EVIDENCE and cannot license REJECTED_IN_SCOPE.`

**Canonical hypotheses:** `["the empirical profile is valid and versioned", "decision evaluation uses the profile's declared evidence requirements", "profile identity includes all decision-bearing fields"]`

**Canonical nonclaims:** `["Evidence completeness establishes only eligibility for the declared decision procedure; it does not establish truth, causal validity, adequate statistical power, or independent replication."]`

**Proof.** The evaluator checks the complete evidence field set and every declared identity before applying the rejection rule. Any missing, malformed, or mismatched required field exits through `INVALID_EVIDENCE`. Therefore no malformed evidence record reaches the rejection branch. ∎

## UFT-EFP-002 A rejection decision is scoped to one hypothesis version

**Claim class:** `PROVED`

**Canonical statement:** `If valid profile-matched evidence satisfies the declared rejection rule, the synthetic conformance evaluator returns REJECTED_IN_SCOPE for the declared hypothesis_id, hypothesis_version, profile_version, and scope, while exposing prior_registration_status as EXTERNAL_UNVERIFIED_ASSUMPTION, prior_registration_verified as false, and empirical_rejection_licensed as false. Actual empirical rejection additionally requires an independently verified immutable prior record.`

**Canonical hypotheses:** `["the evidence is valid under UFT-EFP-001", "the declared rejection rule evaluates true", "the profile explicitly classifies prior registration as an external unverified assumption"]`

**Canonical nonclaims:** `["The procedural REJECTED_IN_SCOPE label does not prove registration chronology, license empirical rejection, or automatically imply global theory refutation, mechanism identification, or that every related formulation is false."]`

**Proof.** The decision payload returns the exact `hypothesis_id`, `hypothesis_version`, `profile_version`, and `scope`, but it also returns `prior_registration_status: EXTERNAL_UNVERIFIED_ASSUMPTION`, `prior_registration_verified: false`, `empirical_rejection_licensed: false`, and `global_theory_rejected: false`. Profile hashing therefore binds the decision contract without manufacturing a historical preregistration fact or broader authority. ∎

## UFT-EFP-003 Failure to reject is not confirmation

**Claim class:** `PROVED`

**Canonical statement:** `If valid evidence is neither rejected nor inconclusive under the declared profile, the licensed decision is NOT_REJECTED_IN_SCOPE; that decision does not imply confirmation, truth, high probability, unique explanation, or absence of future counterevidence.`

**Canonical hypotheses:** `["the evidence is valid under UFT-EFP-001", "the rejection rule evaluates false", "the uncertainty interval does not overlap the rejection boundary"]`

**Canonical nonclaims:** `["NOT_REJECTED_IN_SCOPE carries no confirmation or posterior-probability semantics unless a separately declared inferential framework supplies them."]`

**Proof.** The evaluator has four disjoint decision labels and no confirmation label. Every non-rejected valid decision payload explicitly returns `confirmation_promoted: false`. Therefore non-rejection is not promoted to confirmation by this contract. ∎

## UFT-EFP-004 Boundary-overlapping uncertainty is inconclusive

**Claim class:** `PROVED`

**Canonical statement:** `For the declared exact interval decision rule, if a valid measurement interval overlaps both sides of the rejection threshold, the licensed decision is INCONCLUSIVE rather than REJECTED_IN_SCOPE or NOT_REJECTED_IN_SCOPE.`

**Canonical hypotheses:** `["measurement value and uncertainty radius are exact rational quantities", "uncertainty is interpreted as the closed interval [value-radius,value+radius]", "the profile rejection rule is threshold-based and declared"]`

**Canonical nonclaims:** `["This exact interval control is not a general confidence-interval, Bayesian credible-interval, or measurement-error theorem."]`

**Proof.** `REJECTED_IN_SCOPE` requires the interval lower bound to exceed the threshold. `NOT_REJECTED_IN_SCOPE` requires the upper bound to be at or below the threshold. If neither condition holds, the interval overlaps both regions and the remaining valid decision is `INCONCLUSIVE`. ∎

## UFT-EFP-005 Empirical fit does not imply a unique explanation

**Claim class:** `PROVED`

**Canonical statement:** `If one observation lies in the declared prediction sets of two or more candidate models, empirical fit to that observation does not uniquely identify which candidate generated it; uniqueness requires an additional discriminating result or model-selection argument.`

**Canonical hypotheses:** `["candidate prediction sets are declared before evaluating the observation", "at least two candidate prediction sets contain the same observation"]`

**Canonical nonclaims:** `["The result does not deny that additional discriminating measurements, likelihood models, interventions, or independent evidence can support model selection."]`

**Proof.** Compatibility is set membership. If the observation belongs to at least two declared prediction sets, the compatible-candidate set has cardinality at least two. Membership alone therefore cannot select a unique candidate. ∎

---

# Adversarial counterexamples

### CX-EFP-001 A formal counterexample without empirical evidence is not empirical falsification

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A mathematically valid counterexample object with no calibrated measurement, uncertainty, provenance, or profile identity remains a formal counterexample and evaluates as INVALID_EVIDENCE under the empirical profile.`

**Canonical nonclaims:** `["The fixture does not diminish the mathematical force of a formal counterexample against a universal mathematical proposition; it separates that role from empirical falsification."]`

### CX-EFP-002 Missing calibration cannot license empirical rejection

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A numerically rejection-side observation paired with the wrong calibration identity evaluates as INVALID_EVIDENCE rather than REJECTED_IN_SCOPE.`

**Canonical nonclaims:** `["The fixture does not claim every calibration mismatch changes the underlying physical quantity; it requires declared calibration identity before this profile can evaluate the evidence."]`

### CX-EFP-003 Uncertainty can make a threshold result inconclusive

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A point estimate on the rejection side can still produce INCONCLUSIVE when its declared uncertainty interval crosses the declared rejection threshold.`

**Canonical nonclaims:** `["The fixture is an exact interval semantics control, not a prescription for statistical confidence intervals or laboratory uncertainty models."]`

### CX-EFP-004 A non-rejected synthetic measurement does not confirm the hypothesis

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A valid synthetic measurement entirely inside the non-rejection region produces NOT_REJECTED_IN_SCOPE and carries no confirmation flag or truth promotion.`

**Canonical nonclaims:** `["The fixture does not deny that a separately declared statistical framework can quantify support; it blocks an undeclared promotion from non-rejection to confirmation."]`

### CX-EFP-005 One observation can fit multiple candidate models

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `The observation 0 belongs simultaneously to the declared prediction intervals of models A, B, and C in the finite fit control, so empirical compatibility alone does not select one explanation.`

**Canonical nonclaims:** `["The fixture does not assert that the candidate models are equally plausible under additional evidence or inferential assumptions."]`

### CX-EFP-006 Changing the rejection threshold changes profile identity and can change the decision

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `For the same exact evidence value 1/2 with zero uncertainty, a threshold-0 profile returns REJECTED_IN_SCOPE while a threshold-1 profile returns NOT_REJECTED_IN_SCOPE, and the two canonical fingerprints differ. The fingerprints distinguish profile content but do not prove either profile existed before the evidence; both synthetic decisions expose external-unverified registration and no empirical-rejection licence.`

**Canonical nonclaims:** `["The fixture does not ban justified protocol amendments; it requires versioned profile identity and treats registration chronology as an independently verified provenance obligation rather than a consequence of hashing."]`

---

# Hard boundaries

```text
FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION
SYNTHETIC_FIXTURE != EMPIRICAL_EVIDENCE
FAILURE_TO_REJECT != CONFIRMATION
EMPIRICAL_FIT != UNIQUE_EXPLANATION
REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION
NUMERIC_OBSERVATION != CALIBRATED_MEASUREMENT
MISSING_UNCERTAINTY != ZERO_UNCERTAINTY
POST_HOC_THRESHOLD != PREREGISTERED_REJECTION_RULE
PROFILE_FINGERPRINT != PREREGISTRATION_PROOF
INCONCLUSIVE != NOT_REJECTED
REPRODUCIBLE_ANALYSIS != INDEPENDENT_REPLICATION
FINITE_EMPIRICAL_PROFILE_CONFORMANCE != GENERAL_STATISTICAL_INFERENCE
```

# Finite conformance boundary

The executable battery is synthetic and exact:

```text
15 valid interval decisions
5 REJECTED_IN_SCOPE
7 NOT_REJECTED_IN_SCOPE
3 INCONCLUSIVE
60 invalid-evidence mutation checks
15 model-fit membership checks
3 ambiguous-fit observations
3 pairwise profile-fingerprint separation checks
```

```text
SYNTHETIC_CONFORMANCE != EMPIRICAL_EVIDENCE
GREEN_CI != SCIENTIFIC_CONFIRMATION
```

# Deferred empirical work

A later source-specific profile may be added only when its source claim, observable definition, measurement method, calibration identity, uncertainty model, rejection rule, independently verifiable immutable preregistration provenance, evidence chronology, and already-published objections/replies are explicit. Statistical power, causal identification, independent replication, population inference, and framework-specific statistical semantics remain separate obligations.
