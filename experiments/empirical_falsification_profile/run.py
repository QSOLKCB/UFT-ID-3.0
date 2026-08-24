#!/usr/bin/env python3
"""Exact synthetic conformance for Empirical Falsification Profiles."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from itertools import combinations
from typing import Mapping, Sequence

DECISIONS = (
    "INVALID_EVIDENCE",
    "INCONCLUSIVE",
    "REJECTED_IN_SCOPE",
    "NOT_REJECTED_IN_SCOPE",
)

BOUNDARIES = [
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

PREDICTION_KIND = "upper-bound"
NULL_MODEL_KIND = "boundary-equality"
REJECTION_RULE_KIND = "interval-entirely-above-threshold"
UNCERTAINTY_MODEL = "symmetric-closed-interval-radius"
PRIOR_REGISTRATION_STATUS = "EXTERNAL_UNVERIFIED_ASSUMPTION"
EXPECTED_EVIDENCE_REQUIREMENTS = [
    "matching observable_id",
    "matching measurement_spec_id",
    "matching calibration_id",
    "exact nonnegative uncertainty_radius",
    "at least one provenance_ref",
    "matching profile_fingerprint",
    "declared external-unverified prior_registration_status",
]
EXPECTED_DECISION_POLICY = {
    "reject": "interval lower bound > threshold",
    "not_rejected": "interval upper bound <= threshold",
    "inconclusive": "otherwise",
    "invalid": "evidence requirements fail",
}

PROFILE_FIELDS = {
    "profile_id", "hypothesis_id", "hypothesis_version", "claim_class", "scope",
    "observable_id", "measurement_spec_id", "calibration_id", "uncertainty_model",
    "prediction", "null_model", "rejection_rule", "evidence_requirements",
    "decision_policy", "prior_registration_status", "profile_version",
}
EVIDENCE_FIELDS = {
    "observable_id", "measurement_spec_id", "calibration_id", "value",
    "uncertainty_radius", "provenance_refs", "profile_fingerprint",
}


def _exact(value: object, label: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f"{label} must use exact integer/Fraction arithmetic")
    return Fraction(value)


def _canonicalize(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {str(key): _canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical profile value: {type(value).__name__}")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def profile_fingerprint(profile: Mapping[str, object]) -> str:
    _validate_profile(profile)
    return hashlib.sha256(canonical_bytes(dict(profile))).hexdigest()


def make_profile(threshold: object = 0, *, profile_id: str | None = None) -> dict[str, object]:
    exact_threshold = _exact(threshold, "rejection threshold")
    suffix = f"{exact_threshold.numerator}_{exact_threshold.denominator}".replace("-", "m")
    profile = {
        "profile_id": profile_id or f"EFP-SYN-THRESH-{suffix}",
        "hypothesis_id": "H-SYN-BOUND-001",
        "hypothesis_version": "1.0.0",
        "claim_class": "DIAGNOSTIC",
        "scope": "synthetic exact interval decision semantics only",
        "observable_id": "OBS-SYN-Y-V1",
        "measurement_spec_id": "MEAS-SYN-Y-V1",
        "calibration_id": "CAL-SYN-Y-V1",
        "uncertainty_model": UNCERTAINTY_MODEL,
        "prediction": {"kind": PREDICTION_KIND, "observable_id": "OBS-SYN-Y-V1", "upper_bound": exact_threshold},
        "null_model": {"kind": NULL_MODEL_KIND, "observable_id": "OBS-SYN-Y-V1", "value": exact_threshold},
        "rejection_rule": {"kind": REJECTION_RULE_KIND, "threshold": exact_threshold},
        "evidence_requirements": list(EXPECTED_EVIDENCE_REQUIREMENTS),
        "decision_policy": dict(EXPECTED_DECISION_POLICY),
        "prior_registration_status": PRIOR_REGISTRATION_STATUS,
        "profile_version": "1.0.0",
    }
    _validate_profile(profile)
    return profile


def _validate_profile(profile: Mapping[str, object]) -> None:
    if not isinstance(profile, Mapping) or set(profile) != PROFILE_FIELDS:
        raise ValueError("empirical profile field set drift")
    for key in (
        "profile_id", "hypothesis_id", "hypothesis_version", "claim_class", "scope",
        "observable_id", "measurement_spec_id", "calibration_id", "uncertainty_model",
        "prior_registration_status", "profile_version",
    ):
        if not isinstance(profile[key], str) or not profile[key]:
            raise ValueError(f"empirical profile {key} must be a nonempty string")
    if profile["claim_class"] != "DIAGNOSTIC":
        raise ValueError("synthetic profile claim class must remain DIAGNOSTIC")
    if profile["uncertainty_model"] != UNCERTAINTY_MODEL:
        raise ValueError("unsupported uncertainty-model kind")
    if profile["prior_registration_status"] != PRIOR_REGISTRATION_STATUS:
        raise ValueError("prior registration must remain an external unverified assumption")
    prediction = profile["prediction"]
    null_model = profile["null_model"]
    rejection = profile["rejection_rule"]
    if not isinstance(prediction, Mapping) or set(prediction) != {"kind", "observable_id", "upper_bound"}:
        raise ValueError("prediction shape drift")
    if not isinstance(null_model, Mapping) or set(null_model) != {"kind", "observable_id", "value"}:
        raise ValueError("null-model shape drift")
    if not isinstance(rejection, Mapping) or set(rejection) != {"kind", "threshold"}:
        raise ValueError("rejection-rule shape drift")
    if prediction["kind"] != PREDICTION_KIND:
        raise ValueError("prediction kind is incompatible with rejection rule")
    if null_model["kind"] != NULL_MODEL_KIND:
        raise ValueError("null-model kind is incompatible with rejection rule")
    if rejection["kind"] != REJECTION_RULE_KIND:
        raise ValueError("unsupported rejection-rule kind")
    threshold = _exact(rejection["threshold"], "rejection threshold")
    if _exact(prediction["upper_bound"], "prediction upper bound") != threshold or _exact(null_model["value"], "null-model value") != threshold:
        raise ValueError("prediction/null/rejection threshold disagreement")
    if prediction["observable_id"] != profile["observable_id"] or null_model["observable_id"] != profile["observable_id"]:
        raise ValueError("profile observable binding drift")
    if profile["evidence_requirements"] != EXPECTED_EVIDENCE_REQUIREMENTS:
        raise ValueError("evidence requirement registry drift")
    if profile["decision_policy"] != EXPECTED_DECISION_POLICY:
        raise ValueError("decision policy semantic drift")


def make_evidence(
    profile: Mapping[str, object],
    value: object,
    uncertainty_radius: object,
    *,
    provenance_refs: Sequence[str] = ("SYN-PROV-001",),
) -> dict[str, object]:
    _validate_profile(profile)
    exact_value = _exact(value, "measurement value")
    radius = _exact(uncertainty_radius, "uncertainty radius")
    if radius < 0:
        raise ValueError("uncertainty radius must be nonnegative")
    if isinstance(provenance_refs, (str, bytes)) or not isinstance(provenance_refs, Sequence):
        raise ValueError("provenance refs must be a nonempty string sequence")
    refs = list(provenance_refs)
    if not refs or any(not isinstance(ref, str) or not ref for ref in refs):
        raise ValueError("provenance refs must be a nonempty string sequence")
    return {
        "observable_id": profile["observable_id"],
        "measurement_spec_id": profile["measurement_spec_id"],
        "calibration_id": profile["calibration_id"],
        "value": exact_value,
        "uncertainty_radius": radius,
        "provenance_refs": refs,
        "profile_fingerprint": profile_fingerprint(profile),
    }


def _invalid(reason: str) -> dict[str, object]:
    return {"decision": "INVALID_EVIDENCE", "reason": reason, "confirmation_promoted": False}


def evaluate(profile: Mapping[str, object], evidence: object) -> dict[str, object]:
    _validate_profile(profile)
    if not isinstance(evidence, Mapping) or set(evidence) != EVIDENCE_FIELDS:
        return _invalid("empirical-evidence-record-required")
    for key in ("observable_id", "measurement_spec_id", "calibration_id", "profile_fingerprint"):
        if not isinstance(evidence[key], str) or not evidence[key]:
            return _invalid(f"malformed-{key}")
    if evidence["observable_id"] != profile["observable_id"]:
        return _invalid("observable-id-mismatch")
    if evidence["measurement_spec_id"] != profile["measurement_spec_id"]:
        return _invalid("measurement-spec-id-mismatch")
    if evidence["calibration_id"] != profile["calibration_id"]:
        return _invalid("calibration-id-mismatch")
    if evidence["profile_fingerprint"] != profile_fingerprint(profile):
        return _invalid("profile-fingerprint-mismatch")
    refs = evidence["provenance_refs"]
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref for ref in refs):
        return _invalid("provenance-missing-or-malformed")
    try:
        value = _exact(evidence["value"], "measurement value")
        radius = _exact(evidence["uncertainty_radius"], "uncertainty radius")
    except ValueError:
        return _invalid("measurement-or-uncertainty-malformed")
    if radius < 0:
        return _invalid("uncertainty-radius-negative")
    threshold = _exact(profile["rejection_rule"]["threshold"], "rejection threshold")
    lower = value - radius
    upper = value + radius
    if lower > threshold:
        decision = "REJECTED_IN_SCOPE"
    elif upper <= threshold:
        decision = "NOT_REJECTED_IN_SCOPE"
    else:
        decision = "INCONCLUSIVE"
    return {
        "decision": decision,
        "reason": "declared-exact-interval-rule",
        "interval": [_fraction_text(lower), _fraction_text(upper)],
        "threshold": _fraction_text(threshold),
        "hypothesis_id": profile["hypothesis_id"],
        "hypothesis_version": profile["hypothesis_version"],
        "profile_version": profile["profile_version"],
        "scope": profile["scope"],
        "prior_registration_status": profile["prior_registration_status"],
        "prior_registration_verified": False,
        "empirical_rejection_licensed": False,
        "decision_authority": "SYNTHETIC_CONFORMANCE_ONLY",
        "confirmation_promoted": False,
        "global_theory_rejected": False,
    }


def compatible_models(observation: object, model_intervals: Mapping[str, Sequence[object]]) -> list[str]:
    x = _exact(observation, "model-fit observation")
    if not isinstance(model_intervals, Mapping) or not model_intervals:
        raise ValueError("model interval registry must be a nonempty mapping")
    compatible: list[str] = []
    for model_id, interval in model_intervals.items():
        if not isinstance(model_id, str) or not model_id:
            raise ValueError("model id must be a nonempty string")
        if not isinstance(interval, Sequence) or isinstance(interval, (str, bytes)) or len(interval) != 2:
            raise ValueError("model prediction interval must have exactly two endpoints")
        lower = _exact(interval[0], "model prediction lower bound")
        upper = _exact(interval[1], "model prediction upper bound")
        if lower > upper:
            raise ValueError("model prediction interval is reversed")
        if lower <= x <= upper:
            compatible.append(model_id)
    return sorted(compatible)


def decision_battery() -> dict[str, int]:
    profile = make_profile(0)
    values = (-2, -1, 0, 1, 2)
    radii = (Fraction(0), Fraction(1, 2), Fraction(1))
    counts = {decision: 0 for decision in DECISIONS}
    checks = 0
    for value in values:
        for radius in radii:
            result = evaluate(profile, make_evidence(profile, value, radius))
            counts[result["decision"]] += 1
            checks += 1
    if counts != {
        "INVALID_EVIDENCE": 0,
        "INCONCLUSIVE": 3,
        "REJECTED_IN_SCOPE": 5,
        "NOT_REJECTED_IN_SCOPE": 7,
    }:
        raise RuntimeError("synthetic decision-count drift")
    return {
        "valid_decision_checks": checks,
        "rejected_in_scope_cases": counts["REJECTED_IN_SCOPE"],
        "not_rejected_in_scope_cases": counts["NOT_REJECTED_IN_SCOPE"],
        "inconclusive_cases": counts["INCONCLUSIVE"],
    }


def invalid_evidence_battery() -> dict[str, int]:
    profile = make_profile(0)
    values = (-2, -1, 0, 1, 2)
    radii = (Fraction(0), Fraction(1, 2), Fraction(1))
    checks = 0
    for value in values:
        for radius in radii:
            base = make_evidence(profile, value, radius)
            mutations = (
                {**base, "calibration_id": "CAL-WRONG"},
                {**base, "measurement_spec_id": "MEAS-WRONG"},
                {**base, "provenance_refs": []},
                {**base, "profile_fingerprint": "0" * 64},
            )
            for mutated in mutations:
                result = evaluate(profile, mutated)
                if result["decision"] != "INVALID_EVIDENCE":
                    raise RuntimeError("malformed evidence escaped invalid gate")
                checks += 1
    return {"invalid_evidence_mutation_checks": checks}


def fit_nonuniqueness_battery() -> dict[str, int]:
    models = {
        "MODEL-A": (Fraction(-2), Fraction(0)),
        "MODEL-B": (Fraction(-1), Fraction(1)),
        "MODEL-C": (Fraction(0), Fraction(2)),
    }
    observations = (-2, -1, 0, 1, 2)
    membership_checks = 0
    ambiguous = 0
    for observation in observations:
        compatible = compatible_models(observation, models)
        membership_checks += len(models)
        ambiguous += int(len(compatible) > 1)
    if membership_checks != 15 or ambiguous != 3:
        raise RuntimeError("model-fit ambiguity control drift")
    return {"fit_membership_checks": membership_checks, "ambiguous_fit_observations": ambiguous}


def fingerprint_battery() -> dict[str, int]:
    profiles = [make_profile(value) for value in (-1, 0, 1)]
    fingerprints = [profile_fingerprint(profile) for profile in profiles]
    checks = 0
    for left, right in combinations(fingerprints, 2):
        if left == right:
            raise RuntimeError("decision-bearing threshold failed to change profile identity")
        checks += 1
    return {"profile_fingerprint_pair_checks": checks}


def counterexample_fixtures() -> dict[str, object]:
    profile0 = make_profile(0)
    formal_only = evaluate(profile0, {"formal_counterexample": "CX-MATH-ONLY"})

    wrong_cal = make_evidence(profile0, 1, 0)
    wrong_cal["calibration_id"] = "CAL-WRONG"
    missing_calibration = evaluate(profile0, wrong_cal)

    uncertain = evaluate(profile0, make_evidence(profile0, 1, 1))
    not_rejected = evaluate(profile0, make_evidence(profile0, -1, 0))

    models = {
        "MODEL-A": (Fraction(-2), Fraction(0)),
        "MODEL-B": (Fraction(-1), Fraction(1)),
        "MODEL-C": (Fraction(0), Fraction(2)),
    }
    fit_models = compatible_models(0, models)

    profile1 = make_profile(1)
    evidence0 = make_evidence(profile0, Fraction(1, 2), 0)
    evidence1 = make_evidence(profile1, Fraction(1, 2), 0)
    decision0 = evaluate(profile0, evidence0)
    decision1 = evaluate(profile1, evidence1)

    return {
        "CX-EFP-001": {
            "input_kind": "formal-counterexample-only",
            "decision": formal_only["decision"],
            "reason": formal_only["reason"],
            "empirical_falsification_promoted": False,
        },
        "CX-EFP-002": {
            "value": "1",
            "uncertainty_radius": "0",
            "calibration_id": "CAL-WRONG",
            "decision": missing_calibration["decision"],
            "reason": missing_calibration["reason"],
        },
        "CX-EFP-003": {
            "value": "1",
            "uncertainty_radius": "1",
            "interval": uncertain["interval"],
            "threshold": uncertain["threshold"],
            "decision": uncertain["decision"],
        },
        "CX-EFP-004": {
            "value": "-1",
            "uncertainty_radius": "0",
            "decision": not_rejected["decision"],
            "confirmation_promoted": not_rejected["confirmation_promoted"],
        },
        "CX-EFP-005": {
            "observation": "0",
            "compatible_models": fit_models,
            "compatible_model_count": len(fit_models),
            "unique_explanation": len(fit_models) == 1,
        },
        "CX-EFP-006": {
            "evidence_value": "1/2",
            "uncertainty_radius": "0",
            "threshold_0_decision": decision0["decision"],
            "threshold_1_decision": decision1["decision"],
            "threshold_0_fingerprint": profile_fingerprint(profile0),
            "threshold_1_fingerprint": profile_fingerprint(profile1),
            "profile_identity_differs": profile_fingerprint(profile0) != profile_fingerprint(profile1),
            "prior_registration_status": profile0["prior_registration_status"],
            "prior_registration_verified": decision0["prior_registration_verified"],
            "empirical_rejection_licensed": decision0["empirical_rejection_licensed"],
        },
    }


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-empirical-falsification-profile-witness",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "decisions": decision_battery(),
            "invalid_evidence": invalid_evidence_battery(),
            "fit_nonuniqueness": fit_nonuniqueness_battery(),
            "profile_identity": fingerprint_battery(),
        },
        "fixtures": counterexample_fixtures(),
        "hard_boundaries": BOUNDARIES,
        "claim_boundary": (
            "FORMAL_COUNTEREXAMPLE != EMPIRICAL_FALSIFICATION; "
            "FAILURE_TO_REJECT != CONFIRMATION; EMPIRICAL_FIT != UNIQUE_EXPLANATION; "
            "REJECTION_IN_SCOPE != GLOBAL_THEORY_REFUTATION; "
            "PROFILE_FINGERPRINT != PREREGISTRATION_PROOF"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("Empirical Falsification Profile witness:", result["bounded_checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
