# Formal Assurance Graph

**Status:** PR #8 canonical assurance design.  
**Claim class:** `DEFINITION` / `NONCLAIM`.

UFT-ID does not use one maturity scalar that runs from “idea” to “physical truth”.

The evidence dimensions are independent:

```text
statement
formal encoding
proof
proof audit

reference implementation
runtime correspondence
conformance
deterministic replay

empirical hypothesis
experiment
measurement

scientific interpretation
```

A relation between two dimensions exists only when an explicit edge is recorded.

## Why a graph instead of a ladder

A ladder such as

```text
target -> proof -> runtime -> experiment -> truth
```

suggests entailments that do not exist.

The canonical machine authority is `machine/assurance_graph.json`.

Examples:

```text
STATEMENT --encoded_as--> FORMAL_ENCODING
FORMAL_ENCODING --proved_in--> PROOF_OBJECT
PROOF_OBJECT --audited_by--> PROOF_AUDIT

FORMAL_ENCODING --mapped_to_runtime_by--> RUNTIME_CORRESPONDENCE
REFERENCE_IMPLEMENTATION --tested_by--> CONFORMANCE_RESULT
REFERENCE_IMPLEMENTATION --replayed_by--> DETERMINISTIC_REPLAY

EMPIRICAL_HYPOTHESIS --tested_by--> EXPERIMENT
EXPERIMENT --produces--> MEASUREMENT
MEASUREMENT --may_support--> SCIENTIFIC_INTERPRETATION
```

None of those arrows grants arbitrary transitive authority.

## Explicit non-arrows

PR #8 makes the following forbidden automatic promotions machine-readable:

\[
\text{PROOF\_OBJECT}\nRightarrow\text{CONFORMANCE\_RESULT},
\]

\[
\text{PROOF\_OBJECT}\nRightarrow\text{MEASUREMENT},
\]

\[
\text{CONFORMANCE\_RESULT}\nRightarrow\text{MEASUREMENT},
\]

\[
\text{DETERMINISTIC\_REPLAY}\nRightarrow\text{SCIENTIFIC\_INTERPRETATION}.
\]

Likewise:

```text
FORMAL_SYNTAX != PROOF
MODEL_OUTPUT != EXECUTION_EVIDENCE
CONTENT_IDENTITY != SEMANTIC_TRUTH
```

## Future Lean boundary

Lean remains deferred.

When the Lean phase begins, the project should adopt the formal-assurance architecture demonstrated independently by UFF and NEXUS:

- finite advertised theorem surface;
- exact theorem-surface/version identity;
- proof-hole audit;
- project-defined axiom/constant audit;
- explicit assumptions/nonclaims;
- axiom report for advertised results;
- separate runtime-correspondence document.

The theorem prover will certify the propositions actually encoded in the audited formal environment. It will not certify source data, runtime correspondence, external measurements or physical ontology.

## AssuranceRecord

A future assertion record may contain:

```json
{
  "statement": {},
  "formal_encoding": {},
  "proof": {},
  "proof_audit": {},
  "runtime_correspondence": {},
  "conformance": {},
  "replay": {},
  "experiment": {},
  "measurement": {},
  "interpretation": {}
}
```

These are distinct fields by construction.

The project must never replace them with:

```text
status = TRUE
```

because there is no single axis on which all of these evidence types are comparable.
