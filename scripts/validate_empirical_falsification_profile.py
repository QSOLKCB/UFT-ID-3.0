#!/usr/bin/env python3
"""Fail-closed validation for the Empirical Falsification Profile authority."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/empirical_falsification_profile_contract.json",
    "results": ROOT / "machine/empirical_falsification_profile_results.json",
    "human": ROOT / "theory/EMPIRICAL_FALSIFICATION_PROFILE.md",
    "base_falsification": ROOT / "machine/falsification_contract.json",
    "csp_base": ROOT / "machine/continuum_stochastic_prevalence_contract.json",
    "base_contract": ROOT / "machine/contract.json",
    "roadmap_state": ROOT / "machine/roadmap_state.json",
    "roadmap": ROOT / "ROADMAP.md",
    "readme": ROOT / "README4AI.md",
    "claims": ROOT / "docs/CLAIMS.md",
    "repro": ROOT / "docs/REPRODUCIBILITY.md",
    "experiment": ROOT / "experiments/empirical_falsification_profile/run.py",
    "tests": ROOT / "tests/test_empirical_falsification_profile.py",
    "receipt": ROOT / "experiments/run_empirical_falsification_profile.py",
    "artifact_verifier": ROOT / "scripts/verify_empirical_falsification_profile_artifacts.py",
    "workflow": ROOT / ".github/workflows/finite-adversarial.yml",
}

EXPECTED_SCOPE = (
    "Typed decision and evidence obligations for a synthetic conformance evaluator that classifies whether calibrated "
    "profile-matched evidence crosses a versioned scoped rejection boundary. The profile separates formal counterexamples "
    "from empirical falsification, non-rejection from confirmation, calibrated measurement from bare numeric observation, "
    "and model fit from unique explanation while treating preregistration chronology as an external unverified assumption."
)
EXPECTED_PRIMARY_TYPES = {
    "profile": "EmpiricalFalsificationProfile=(profile_id,hypothesis_id,hypothesis_version,claim_class,scope,observable_id,measurement_spec_id,calibration_id,uncertainty_model,prediction,null_model,rejection_rule,evidence_requirements,decision_policy,prior_registration_status,profile_version)",
    "evidence": "EmpiricalEvidence=(observable_id,measurement_spec_id,calibration_id,value,uncertainty_radius,provenance_refs,profile_fingerprint)",
    "decision": "Decision in {INVALID_EVIDENCE,INCONCLUSIVE,REJECTED_IN_SCOPE,NOT_REJECTED_IN_SCOPE}",
    "profile_identity": "SHA256(canonical profile payload), binding rejection threshold and all decision-bearing metadata; content identity does not prove registration chronology",
    "registration_status": "PriorRegistrationStatus={EXTERNAL_UNVERIFIED_ASSUMPTION}; actual empirical rejection additionally requires independently verified immutable preregistration provenance",
}
EXPECTED_DECISION_SEMANTICS = {
    "INVALID_EVIDENCE": "Required measurement, calibration, provenance, uncertainty, or profile identity is missing, malformed, or mismatched; no rejection decision is licensed.",
    "INCONCLUSIVE": "Valid evidence uncertainty overlaps both the rejection and non-rejection regions under the declared rule.",
    "REJECTED_IN_SCOPE": "The synthetic conformance evaluator returns this scoped procedural label when valid evidence satisfies the declared rule. Its prior-registration status remains EXTERNAL_UNVERIFIED_ASSUMPTION, so actual empirical rejection additionally requires independently verified immutable preregistration provenance.",
    "NOT_REJECTED_IN_SCOPE": "Valid evidence does not satisfy the rejection rule and is not inconclusive; this is not confirmation, truth, or unique explanatory support.",
}
EXPECTED_BOUNDARIES = [
    "FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION",
    "SYNTHETIC_FIXTURE != EMPIRICAL_EVIDENCE",
    "FAILURE_TO_REJECT != CONFIRMATION",
    "EMPIRICAL_FIT != UNIQUE_EXPLANATION",
    "REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION",
    "NUMERIC_OBSERVATION != CALIBRATED_MEASUREMENT",
    "MISSING_UNCERTAINTY != ZERO_UNCERTAINTY",
    "POST_HOC_THRESHOLD != PREREGISTERED_REJECTION_RULE",
    "PROFILE_FINGERPRINT != PREREGISTRATION_PROOF",
    "INCONCLUSIVE != NOT_REJECTED",
    "REPRODUCIBLE_ANALYSIS != INDEPENDENT_REPLICATION",
    "FINITE_EMPIRICAL_PROFILE_CONFORMANCE != GENERAL_STATISTICAL_INFERENCE",
]
EXPECTED_LIMITS = {
    "decision_grid_value_count": 5,
    "uncertainty_radius_count": 3,
    "valid_decision_checks": 15,
    "rejected_in_scope_cases": 5,
    "not_rejected_in_scope_cases": 7,
    "inconclusive_cases": 3,
    "invalid_evidence_mutation_checks": 60,
    "fit_membership_checks": 15,
    "ambiguous_fit_observations": 3,
    "profile_fingerprint_pair_checks": 3,
    "policy": "The executable battery uses exact Fraction arithmetic and synthetic conformance fixtures only. It validates decision semantics, evidence completeness, profile content identity, explicit external-unverified registration status, and non-unique-fit controls; it does not prove preregistration chronology or supply empirical evidence, statistical power, population inference, causal identification, independent replication, or physical validation.",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/EMPIRICAL_FALSIFICATION_PROFILE.md",
    "results": "machine/empirical_falsification_profile_results.json",
    "validator": "scripts/validate_empirical_falsification_profile.py",
    "experiment": "experiments/empirical_falsification_profile/run.py",
    "tests": "tests/test_empirical_falsification_profile.py",
    "receipt": "experiments/run_empirical_falsification_profile.py",
    "artifact_verifier": "scripts/verify_empirical_falsification_profile_artifacts.py",
    "base_falsification": "machine/falsification_contract.json",
    "csp_base": "machine/continuum_stochastic_prevalence_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "roadmap": "ROADMAP.md",
    "workflow": ".github/workflows/finite-adversarial.yml",
}
EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/EMPIRICAL_FALSIFICATION_PROFILE.md",
    "machine_contract": "machine/empirical_falsification_profile_contract.json",
    "machine_results": "machine/empirical_falsification_profile_results.json",
    "validator": "scripts/validate_empirical_falsification_profile.py",
    "experiment": "experiments/empirical_falsification_profile/run.py",
    "tests": "tests/test_empirical_falsification_profile.py",
    "receipt_runner": "experiments/run_empirical_falsification_profile.py",
    "receipt_version": "1.0.0",
    "artifact_verifier": "scripts/verify_empirical_falsification_profile_artifacts.py",
    "base_falsification_authority": "machine/falsification_contract.json",
    "csp_base_authority": "machine/continuum_stochastic_prevalence_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "workflow": ".github/workflows/finite-adversarial.yml",
    "rule": "Empirical decision eligibility requires complete calibrated profile-matched evidence and remains scoped to one hypothesis/profile version; the synthetic REJECTED_IN_SCOPE label carries external-unverified registration status and no empirical-rejection licence until independent immutable preregistration provenance is verified. Non-rejection is not confirmation, fit is not unique explanation, and synthetic conformance is not empirical evidence.",
}
EXPECTED_CENTRAL_HARD_RULES = {
    "formal_counterexample_implies_empirical_falsification": False,
    "synthetic_fixture_implies_empirical_evidence": False,
    "failure_to_reject_implies_confirmation": False,
    "empirical_fit_implies_unique_explanation": False,
    "scoped_rejection_implies_global_theory_refutation": False,
    "numeric_observation_implies_calibrated_measurement": False,
    "missing_uncertainty_means_zero_uncertainty": False,
    "post_hoc_threshold_equals_preregistered_rule": False,
    "profile_fingerprint_implies_preregistration_proof": False,
    "reproducible_analysis_implies_independent_replication": False,
}
EXPECTED_DEFERRALS = [
    "source-specific empirical claim instantiation unless exact source reconstruction is complete",
    "independent immutable preregistration provenance and chronology verification",
    "statistical power and sample-size design",
    "frequentist or Bayesian inferential frameworks beyond the exact interval control",
    "multiple-testing and sequential-analysis procedures",
    "causal identification and intervention validity",
    "external dataset acquisition and calibration execution",
    "independent replication and meta-analysis",
    "population prevalence estimation",
    "automated rejection of broader theories from one scoped hypothesis",
    "Lean proof objects",
]
EXPECTED_CONTRACT_TOP_LEVEL = {
    "type", "schema_version", "snapshot_date", "claim_class", "scope", "base_falsification_authority",
    "primary_types", "decision_semantics", "hard_boundaries", "execution_limits", "authorities", "explicit_deferrals",
}
EXPECTED_RESULTS_TOP_LEVEL = {"type", "schema_version", "snapshot_date", "records", "claim_boundary"}
EXPECTED_THEOREM_FIELDS = {"id", "name", "claim_class", "statement", "hypotheses", "proof_reference", "executable_evidence", "nonclaims"}
EXPECTED_COUNTEREXAMPLE_FIELDS = {"id", "name", "claim_class", "statement", "fixture", "evidence", "nonclaims"}
EXPECTED_EVIDENCE = ["experiments/empirical_falsification_profile/run.py", "tests/test_empirical_falsification_profile.py"]
EXPECTED_RESULT_BOUNDARY = "FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION; FAILURE_TO_REJECT != CONFIRMATION; EMPIRICAL_FIT != UNIQUE_EXPLANATION; REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION; PROFILE_FINGERPRINT != PREREGISTRATION_PROOF"

EXPECTED_THEOREMS = {
    "UFT-EFP-001": {
        "name": "Empirical rejection requires complete profile-matched evidence",
        "statement": "Under the declared EmpiricalFalsificationProfile semantics, any evidence record with missing, malformed, or mismatched observable identity, measurement-spec identity, calibration identity, uncertainty, provenance, or profile fingerprint evaluates to INVALID_EVIDENCE and cannot license REJECTED_IN_SCOPE.",
        "hypotheses": ["the empirical profile is valid and versioned", "decision evaluation uses the profile's declared evidence requirements", "profile identity includes all decision-bearing fields"],
        "nonclaims": ["Evidence completeness establishes only eligibility for the declared decision procedure; it does not establish truth, causal validity, adequate statistical power, or independent replication."],
    },
    "UFT-EFP-002": {
        "name": "A rejection decision is scoped to one hypothesis version",
        "statement": "If valid profile-matched evidence satisfies the declared rejection rule, the synthetic conformance evaluator returns REJECTED_IN_SCOPE for the declared hypothesis_id, hypothesis_version, profile_version, and scope, while exposing prior_registration_status as EXTERNAL_UNVERIFIED_ASSUMPTION, prior_registration_verified as false, and empirical_rejection_licensed as false. Actual empirical rejection additionally requires an independently verified immutable prior record.",
        "hypotheses": ["the evidence is valid under UFT-EFP-001", "the declared rejection rule evaluates true", "the profile explicitly classifies prior registration as an external unverified assumption"],
        "nonclaims": ["The procedural REJECTED_IN_SCOPE label does not prove registration chronology, license empirical rejection, or automatically imply global theory refutation, mechanism identification, or that every related formulation is false."],
    },
    "UFT-EFP-003": {
        "name": "Failure to reject is not confirmation",
        "statement": "If valid evidence is neither rejected nor inconclusive under the declared profile, the licensed decision is NOT_REJECTED_IN_SCOPE; that decision does not imply confirmation, truth, high probability, unique explanation, or absence of future counterevidence.",
        "hypotheses": ["the evidence is valid under UFT-EFP-001", "the rejection rule evaluates false", "the uncertainty interval does not overlap the rejection boundary"],
        "nonclaims": ["NOT_REJECTED_IN_SCOPE carries no confirmation or posterior-probability semantics unless a separately declared inferential framework supplies them."],
    },
    "UFT-EFP-004": {
        "name": "Boundary-overlapping uncertainty is inconclusive",
        "statement": "For the declared exact interval decision rule, if a valid measurement interval overlaps both sides of the rejection threshold, the licensed decision is INCONCLUSIVE rather than REJECTED_IN_SCOPE or NOT_REJECTED_IN_SCOPE.",
        "hypotheses": ["measurement value and uncertainty radius are exact rational quantities", "uncertainty is interpreted as the closed interval [value-radius,value+radius]", "the profile rejection rule is threshold-based and declared"],
        "nonclaims": ["This exact interval control is not a general confidence-interval, Bayesian credible-interval, or measurement-error theorem."],
    },
    "UFT-EFP-005": {
        "name": "Empirical fit does not imply a unique explanation",
        "statement": "If one observation lies in the declared prediction sets of two or more candidate models, empirical fit to that observation does not uniquely identify which candidate generated it; uniqueness requires an additional discriminating result or model-selection argument.",
        "hypotheses": ["candidate prediction sets are declared before evaluating the observation", "at least two candidate prediction sets contain the same observation"],
        "nonclaims": ["The result does not deny that additional discriminating measurements, likelihood models, interventions, or independent evidence can support model selection."],
    },
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-EFP-001": {
        "name": "A formal counterexample without empirical evidence is not empirical falsification",
        "statement": "A mathematically valid counterexample object with no calibrated measurement, uncertainty, provenance, or profile identity remains a formal counterexample and evaluates as INVALID_EVIDENCE under the empirical profile.",
        "fixture": "formal counterexample token submitted without an empirical evidence record",
        "nonclaims": ["The fixture does not diminish the mathematical force of a formal counterexample against a universal mathematical proposition; it separates that role from empirical falsification."],
    },
    "CX-EFP-002": {
        "name": "Missing calibration cannot license empirical rejection",
        "statement": "A numerically rejection-side observation paired with the wrong calibration identity evaluates as INVALID_EVIDENCE rather than REJECTED_IN_SCOPE.",
        "fixture": "rejection-side exact observation with mismatched calibration identity",
        "nonclaims": ["The fixture does not claim every calibration mismatch changes the underlying physical quantity; it requires declared calibration identity before this profile can evaluate the evidence."],
    },
    "CX-EFP-003": {
        "name": "Uncertainty can make a threshold result inconclusive",
        "statement": "A point estimate on the rejection side can still produce INCONCLUSIVE when its declared uncertainty interval crosses the declared rejection threshold.",
        "fixture": "value 1 with uncertainty radius 1 around threshold 0",
        "nonclaims": ["The fixture is an exact interval semantics control, not a prescription for statistical confidence intervals or laboratory uncertainty models."],
    },
    "CX-EFP-004": {
        "name": "A non-rejected synthetic measurement does not confirm the hypothesis",
        "statement": "A valid synthetic measurement entirely inside the non-rejection region produces NOT_REJECTED_IN_SCOPE and carries no confirmation flag or truth promotion.",
        "fixture": "value -1 with zero uncertainty under a threshold-0 profile",
        "nonclaims": ["The fixture does not deny that a separately declared statistical framework can quantify support; it blocks an undeclared promotion from non-rejection to confirmation."],
    },
    "CX-EFP-005": {
        "name": "One observation can fit multiple candidate models",
        "statement": "The observation 0 belongs simultaneously to the declared prediction intervals of models A, B, and C in the finite fit control, so empirical compatibility alone does not select one explanation.",
        "fixture": "three overlapping exact rational prediction intervals at observation 0",
        "nonclaims": ["The fixture does not assert that the candidate models are equally plausible under additional evidence or inferential assumptions."],
    },
    "CX-EFP-006": {
        "name": "Changing the rejection threshold changes profile identity and can change the decision",
        "statement": "For the same exact evidence value 1/2 with zero uncertainty, a threshold-0 profile returns REJECTED_IN_SCOPE while a threshold-1 profile returns NOT_REJECTED_IN_SCOPE, and the two canonical fingerprints differ. The fingerprints distinguish profile content but do not prove either profile existed before the evidence; both synthetic decisions expose external-unverified registration and no empirical-rejection licence.",
        "fixture": "same evidence under two differently fingerprinted rejection thresholds",
        "nonclaims": ["The fixture does not ban justified protocol amendments; it requires versioned profile identity and treats registration chronology as an independently verified provenance obligation rather than a consequence of hashing."],
    },
}
EXPECTED_FIXTURE_PAYLOADS = {
    "CX-EFP-001": {"input_kind": "formal-counterexample-only", "decision": "INVALID_EVIDENCE", "reason": "empirical-evidence-record-required", "empirical_falsification_promoted": False},
    "CX-EFP-002": {"value": "1", "uncertainty_radius": "0", "calibration_id": "CAL-WRONG", "decision": "INVALID_EVIDENCE", "reason": "calibration-id-mismatch"},
    "CX-EFP-003": {"value": "1", "uncertainty_radius": "1", "interval": ["0", "2"], "threshold": "0", "decision": "INCONCLUSIVE"},
    "CX-EFP-004": {"value": "-1", "uncertainty_radius": "0", "decision": "NOT_REJECTED_IN_SCOPE", "confirmation_promoted": False},
    "CX-EFP-005": {"observation": "0", "compatible_models": ["MODEL-A", "MODEL-B", "MODEL-C"], "compatible_model_count": 3, "unique_explanation": False},
    "CX-EFP-006": {"evidence_value": "1/2", "uncertainty_radius": "0", "threshold_0_decision": "REJECTED_IN_SCOPE", "threshold_1_decision": "NOT_REJECTED_IN_SCOPE", "threshold_0_fingerprint": "5f5aca449b40918b16723b62fe06aefa2fb65d1ec158570304702313a42562b9", "threshold_1_fingerprint": "889268e93a153772be7f3fd64ff8162b9db40506c30f149ac3d7fd1377dbfd7a", "profile_identity_differs": True, "prior_registration_status": "EXTERNAL_UNVERIFIED_ASSUMPTION", "prior_registration_verified": False, "empirical_rejection_licensed": False},
}
EXPECTED_BOUNDED = {
    "decisions": {"valid_decision_checks": 15, "rejected_in_scope_cases": 5, "not_rejected_in_scope_cases": 7, "inconclusive_cases": 3},
    "invalid_evidence": {"invalid_evidence_mutation_checks": 60},
    "fit_nonuniqueness": {"fit_membership_checks": 15, "ambiguous_fit_observations": 3},
    "profile_identity": {"profile_fingerprint_pair_checks": 3},
}
EXPECTED_ROADMAP_SEQUENCE = [
    (9, "deterministic-observation-calculus", "complete"),
    (10, "lean-observation-foundation", "deferred-independent-formal-proof-track"),
    (11, "relation-first-recovery-core-plus-graph-realization-interlude", "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"),
    (12, "bridge-core", "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"),
    (13, "epistemic-bridge-specialization", "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"),
    (14, "representation-and-congruence-calculus", "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f"),
    (15, "information-comparability-core", "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813"),
    (16, "recovery-specializations", "complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f"),
    (17, "continuum-stochastic-prevalence-obligations", "complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77"),
    (18, "empirical-falsification-profile", "active-implemented-in-current-change"),
]
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "formal counterexample proves empirical falsification",
    "failure to reject proves confirmation",
    "empirical fit proves unique explanation",
    "scoped rejection proves global theory refutation",
    "synthetic fixture is empirical evidence",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_snapshot_date(value: object, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO YYYY-MM-DD string")
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{label} must be an ISO YYYY-MM-DD string")
        return None
    if parsed > datetime.now(timezone.utc).date():
        errors.append(f"{label} is a future UTC snapshot")
    return value


def safe_path(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a nonempty repository-relative path")
        return
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{label} escapes repository")
        return
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository")
        return
    if not resolved.is_file():
        errors.append(f"{label} missing: {value}")


def section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return None
    start = matches[0]
    match = re.match(r"^(#+)\s", heading)
    if match is None:
        return None
    level = len(match.group(1))
    out = [lines[start]]
    for line in lines[start + 1:]:
        candidate = re.match(r"^(#+)\s", line.strip())
        if candidate is not None and len(candidate.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def metadata(sec: str, label: str) -> str | None:
    prefix = f"**{label}:** "
    values = [line.strip()[len(prefix):] for line in sec.splitlines() if line.strip().startswith(prefix)]
    return values[0] if len(values) == 1 else None


def strip_code(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def parse_json_metadata(sec: str, label: str) -> object | None:
    raw = strip_code(metadata(sec, label))
    try:
        return json.loads(raw) if raw is not None else None
    except json.JSONDecodeError:
        return None


def validate() -> dict[str, object]:
    errors: list[str] = []
    for name, path in PATHS.items():
        if not path.is_file():
            errors.append(f"missing Empirical Falsification Profile authority file: {name}={path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    base_falsification = load_json(PATHS["base_falsification"])
    csp_base = load_json(PATHS["csp_base"])
    base_contract = load_json(PATHS["base_contract"])
    roadmap_state = load_json(PATHS["roadmap_state"])
    human = PATHS["human"].read_text(encoding="utf-8")
    roadmap = PATHS["roadmap"].read_text(encoding="utf-8")
    readme = PATHS["readme"].read_text(encoding="utf-8")
    claims = PATHS["claims"].read_text(encoding="utf-8")
    repro = PATHS["repro"].read_text(encoding="utf-8")

    snapshot_values = {
        "EFP contract snapshot": contract.get("snapshot_date"),
        "EFP result snapshot": results.get("snapshot_date"),
        "EFP roadmap snapshot": roadmap_state.get("snapshot_date"),
        "EFP CSP basis snapshot": csp_base.get("snapshot_date"),
    }
    parsed_snapshots = {label: validate_snapshot_date(value, label, errors) for label, value in snapshot_values.items()}
    live_snapshot_values = [snapshot_values[label] for label in ("EFP contract snapshot", "EFP result snapshot", "EFP roadmap snapshot")]
    if any(value != live_snapshot_values[0] for value in live_snapshot_values[1:]):
        errors.append("EFP contract/result/roadmap snapshot disagreement")
    if parsed_snapshots["EFP contract snapshot"] != parsed_snapshots["EFP CSP basis snapshot"]:
        errors.append("EFP snapshot must match the merged CSP basis snapshot")

    if set(contract) != EXPECTED_CONTRACT_TOP_LEVEL: errors.append("EFP contract top-level field set drift")
    if contract.get("type") != "uft-id-empirical-falsification-profile-contract": errors.append("EFP contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("EFP contract schema drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("EFP contract claim class drift")
    if contract.get("scope") != EXPECTED_SCOPE: errors.append("EFP contract scope drift")
    if contract.get("base_falsification_authority") != "machine/falsification_contract.json": errors.append("EFP base falsification authority drift")
    if contract.get("primary_types") != EXPECTED_PRIMARY_TYPES: errors.append("EFP primary type registry drift")
    if contract.get("decision_semantics") != EXPECTED_DECISION_SEMANTICS: errors.append("EFP decision semantics drift")
    if contract.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("EFP hard-boundary registry drift")
    if contract.get("execution_limits") != EXPECTED_LIMITS: errors.append("EFP execution limits drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("EFP authority registry drift")
    else:
        for key, value in EXPECTED_AUTHORITIES.items(): safe_path(value, f"EFP authority {key}", errors)
    if contract.get("explicit_deferrals") != EXPECTED_DEFERRALS: errors.append("EFP explicit deferrals drift")

    if base_falsification.get("type") != "uft-id-falsification-contract": errors.append("EFP PR8 falsification base type drift")
    if base_falsification.get("status") != "scaffold-active": errors.append("EFP PR8 falsification scaffold status drift")
    if csp_base.get("type") != "uft-id-continuum-stochastic-prevalence-contract": errors.append("EFP CSP base authority drift")

    if base_contract.get("empirical_falsification_profile_authority") != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central EFP authority registration drift")
    library = base_contract.get("experiment_library")
    if not isinstance(library, dict) or library.get("empirical_falsification_profile_receipt_runner") != "experiments/run_empirical_falsification_profile.py" or library.get("empirical_falsification_profile_receipt_version") != "1.0.0":
        errors.append("central EFP receipt registry drift")
    hard_rules = base_contract.get("hard_rules")
    if not isinstance(hard_rules, dict) or any(hard_rules.get(key) is not value for key, value in EXPECTED_CENTRAL_HARD_RULES.items()):
        errors.append("central EFP hard-rule registration drift")
    reads = base_contract.get("required_agent_reads")
    required_reads = {
        "theory/EMPIRICAL_FALSIFICATION_PROFILE.md", "machine/empirical_falsification_profile_contract.json",
        "machine/empirical_falsification_profile_results.json", "scripts/validate_empirical_falsification_profile.py",
        "experiments/run_empirical_falsification_profile.py",
    }
    if not isinstance(reads, list) or not required_reads.issubset(set(reads)): errors.append("central EFP agent-read registration drift")

    if set(results) != EXPECTED_RESULTS_TOP_LEVEL: errors.append("EFP result registry top-level field set drift")
    if results.get("type") != "uft-id-empirical-falsification-profile-result-registry": errors.append("EFP result type drift")
    if results.get("schema_version") != "1.0.0": errors.append("EFP result schema drift")
    if results.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("EFP result claim boundary drift")
    records = results.get("records")
    if not isinstance(records, list):
        errors.append("EFP result registry malformed")
        records = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            errors.append(f"EFP result {index} malformed")
            continue
        rid = str(record["id"])
        expected_fields = EXPECTED_THEOREM_FIELDS if rid in EXPECTED_THEOREMS else EXPECTED_COUNTEREXAMPLE_FIELDS if rid in EXPECTED_COUNTEREXAMPLES else None
        if expected_fields is None:
            errors.append(f"unexpected EFP result id: {rid}")
        elif set(record) != expected_fields:
            errors.append(f"{rid} {'theorem' if rid in EXPECTED_THEOREMS else 'counterexample'} field set drift")
        if rid in by_id: errors.append(f"duplicate EFP result id: {rid}")
        else: by_id[rid] = record
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(by_id) != expected_ids: errors.append("EFP result identity set drift")

    for rid, expected in EXPECTED_THEOREMS.items():
        record = by_id.get(rid)
        if record is None: continue
        if record.get("name") != expected["name"]: errors.append(f"{rid} name drift")
        if record.get("claim_class") != "PROVED": errors.append(f"{rid} claim class drift")
        if record.get("statement") != expected["statement"]: errors.append(f"{rid} statement drift")
        if record.get("hypotheses") != expected["hypotheses"]: errors.append(f"{rid} hypotheses drift")
        if record.get("executable_evidence") != EXPECTED_EVIDENCE: errors.append(f"{rid} executable evidence drift")
        if record.get("nonclaims") != expected["nonclaims"]: errors.append(f"{rid} nonclaims drift")
        expected_ref = f"theory/EMPIRICAL_FALSIFICATION_PROFILE.md#uft-{rid.lower().replace('uft-', '')}-{expected['name'].lower().replace(' ', '-').replace('?', '')}"
        if record.get("proof_reference") != expected_ref:
            errors.append(f"{rid} proof reference drift")
        sec = section(human, f"## {rid} {expected['name']}")
        if sec is None:
            errors.append(f"{rid} human theorem section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`PROVED`": errors.append(f"{rid} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != expected["statement"]: errors.append(f"{rid} human canonical statement drift")
        if parse_json_metadata(sec, "Canonical hypotheses") != expected["hypotheses"]: errors.append(f"{rid} human canonical hypotheses drift")
        if parse_json_metadata(sec, "Canonical nonclaims") != expected["nonclaims"]: errors.append(f"{rid} human canonical nonclaims drift")

    for rid, expected in EXPECTED_COUNTEREXAMPLES.items():
        record = by_id.get(rid)
        if record is None: continue
        if record.get("name") != expected["name"]: errors.append(f"{rid} name drift")
        if record.get("claim_class") != "COUNTEREXAMPLE": errors.append(f"{rid} claim class drift")
        if record.get("statement") != expected["statement"]: errors.append(f"{rid} statement drift")
        if record.get("fixture") != expected["fixture"]: errors.append(f"{rid} fixture drift")
        if record.get("evidence") != EXPECTED_EVIDENCE: errors.append(f"{rid} evidence drift")
        if record.get("nonclaims") != expected["nonclaims"]: errors.append(f"{rid} nonclaims drift")
        sec = section(human, f"### {rid} {expected['name']}")
        if sec is None:
            errors.append(f"{rid} human counterexample section missing or duplicated")
            continue
        if metadata(sec, "Claim class") != "`COUNTEREXAMPLE`": errors.append(f"{rid} human claim class drift")
        if strip_code(metadata(sec, "Canonical statement")) != expected["statement"]: errors.append(f"{rid} human canonical statement drift")
        if parse_json_metadata(sec, "Canonical nonclaims") != expected["nonclaims"]: errors.append(f"{rid} human canonical nonclaims drift")

    if roadmap_state.get("type") != "uft-id-roadmap-state": errors.append("EFP roadmap type drift")
    if roadmap_state.get("schema_version") != "1.6.0": errors.append("EFP roadmap schema drift")
    if roadmap_state.get("basis_commit") != "353e55a11a8cb6d6bcf571110e0fd6f32823fc77": errors.append("EFP roadmap basis commit must be merged CSP PR")
    if roadmap_state.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17]: errors.append("EFP roadmap completed set drift")
    if roadmap_state.get("active_planned_surface") != 18: errors.append("EFP roadmap active surface must be PR #18")
    if roadmap_state.get("deferred") != [10]: errors.append("EFP roadmap deferred set drift")
    sequence = roadmap_state.get("sequence")
    actual_sequence = [(item.get("planned_pr"), item.get("surface"), item.get("status")) for item in sequence if isinstance(item, dict)] if isinstance(sequence, list) else []
    if actual_sequence != EXPECTED_ROADMAP_SEQUENCE: errors.append("EFP roadmap sequence/status drift")
    rules = roadmap_state.get("rules")
    required_rule = "Empirical rejection requires complete calibrated profile-matched evidence and remains scoped to one hypothesis/profile version; formal counterexamples, synthetic fixtures, non-rejection, or model fit cannot be promoted into empirical falsification, confirmation, or unique explanation by default."
    if not isinstance(rules, list) or required_rule not in rules: errors.append("EFP roadmap falsification hard rule missing")

    for anchor in (
        "## Active now — planned PR #18", "### Empirical falsification profile",
        "python scripts/validate_empirical_falsification_profile.py",
        "python experiments/empirical_falsification_profile/run.py --json",
        "python experiments/run_empirical_falsification_profile.py --json",
        "- [x] Planned PR #17 — Continuum, stochastic, and prevalence obligations",
        "### QSOL-CONTEXT → Lean 4 → Zenodo formalization workflow",
        "IMMUTABLE SOURCE-RELEASE TAG",
        "THREE-FILE ZENODO VERSIONED RELEASE",
        "SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER",
        "PROFILE_FINGERPRINT != PREREGISTRATION_PROOF",
    ):
        if anchor not in roadmap: errors.append(f"roadmap missing EFP/tracker anchor: {anchor}")

    for text, anchors, label in (
        (readme, ("## Empirical Falsification Profile authority", "machine/empirical_falsification_profile_contract.json", "FAILURE_TO_REJECT != CONFIRMATION"), "README4AI"),
        (claims, ("### C14 - Empirical falsification decisions are profile-scoped", "UFT-EFP-001", "EMPIRICAL_FIT != UNIQUE_EXPLANATION"), "claims"),
        (repro, ("## Empirical-falsification-profile conformance boundary", "empirical-falsification-profile-validation.json", "python scripts/validate_empirical_falsification_profile.py"), "reproducibility"),
    ):
        for anchor in anchors:
            if anchor not in text: errors.append(f"{label} missing EFP anchor: {anchor}")

    experiment = load_module("efp_validator_experiment", PATHS["experiment"])
    witness = experiment.run_suite()
    if witness.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("EFP witness hard-boundary drift")
    if witness.get("bounded_checks") != EXPECTED_BOUNDED: errors.append("EFP bounded witness count drift")
    if witness.get("fixtures") != EXPECTED_FIXTURE_PAYLOADS: errors.append("EFP witness counterexample payload drift")
    if witness.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("EFP witness claim boundary drift")

    combined = "\n".join((json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False), json.dumps(base_contract, ensure_ascii=False), human, roadmap, readme, claims, repro)).casefold()
    for token in PRIVATE_PATTERNS:
        if token in combined: errors.append(f"EFP authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in combined: errors.append(f"EFP authority contains forbidden promotion: {phrase}")

    return {
        "status": "error" if errors else "ok",
        "errors": errors,
        "result_count": len(by_id),
        "boundary_count": len(contract.get("hard_boundaries", [])) if isinstance(contract.get("hard_boundaries"), list) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    elif result["status"] == "ok":
        print(f"Empirical Falsification Profile authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]: print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
