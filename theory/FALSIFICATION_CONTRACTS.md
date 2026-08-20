# Falsification Contracts

**Status:** PR #8 active scaffold; empirical specializations deferred.  
**Claim class:** `DEFINITION` / `NONCLAIM`.

The paper bundle supplied for the formalization audit contained a useful recurring pattern: scientific claims should state not only what they explain, but what controlled observation would count against them.

UFT-ID therefore introduces a `FalsificationSpec` scaffold.

It does **not** import the papers' consciousness, semantic-gauge, identity-mass or other domain ontology.

## Required fields

A scoped falsifiable hypothesis must name:

```text
hypothesis_id
claim_class
independent_variables
perturbations
observables
predictions
null_model
rejection_conditions
evidence_required
scope_limits
status
```

The machine authority is `machine/falsification_contract.json`.

## Semantics

A **perturbation** is a declared controlled change.

A **prediction** is fixed before inspecting the target outcome and states a direction, range or relation.

A **null model** is separately defined behavior absent the proposed mechanism.

A **rejection condition** is an observable result that counts against the scoped hypothesis.

`evidence_required` says what data, calibration, execution and provenance must exist before the condition is evaluated.

## Synthetic conformance fixture `FALS-SYN-001`

PR #8 includes one deliberately content-free example:

```text
alpha: 0 -> 1
prediction: q(1) < q(0)
null:       q(1) = q(0)
reject if:  q(1) >= q(0)
```

This fixture tests contract semantics only.

```text
FALSIFIABLE_SCHEMA != EMPIRICAL_VALIDATION
REJECTION_CONDITION != AUTOMATIC_REJECTION_OF_A_BROADER_THEORY
```

## Deferred work

Later empirical/reproduction PRs may instantiate `FalsificationSpec` for source-specific claims only after:

- exact source reconstruction;
- stable observable definitions;
- calibration identity;
- null-model choice;
- evidence provenance;
- review of already-published objections/replies.

No current Vopson or external scientific claim is silently reclassified by PR #8.
