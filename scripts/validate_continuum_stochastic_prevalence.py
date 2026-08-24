#!/usr/bin/env python3
"""Fail-closed validation for Continuum/Stochastic/Prevalence obligations."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "contract": ROOT / "machine/continuum_stochastic_prevalence_contract.json",
    "results": ROOT / "machine/continuum_stochastic_prevalence_results.json",
    "human": ROOT / "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
    "recovery_base": ROOT / "machine/recovery_specialization_contract.json",
    "relation_base": ROOT / "machine/relation_contract.json",
    "base_contract": ROOT / "machine/contract.json",
    "roadmap_state": ROOT / "machine/roadmap_state.json",
    "roadmap": ROOT / "ROADMAP.md",
    "readme": ROOT / "README4AI.md",
    "claims": ROOT / "docs/CLAIMS.md",
    "repro": ROOT / "docs/REPRODUCIBILITY.md",
    "experiment": ROOT / "experiments/continuum_stochastic_prevalence/run.py",
    "tests": ROOT / "tests/test_continuum_stochastic_prevalence.py",
    "receipt": ROOT / "experiments/run_continuum_stochastic_prevalence.py",
    "artifact_verifier": ROOT / "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "workflow": ROOT / ".github/workflows/finite-adversarial.yml",
}

EXPECTED_SCOPE = (
    "Obligation layer for finite stochastic semantics, infinite-horizon quantifier boundaries, continuum lifting, "
    "and prevalence claims. It separates relation reachability from stochastic support, finite-horizon evidence "
    "from infinite-path liveness, finite samples from model probabilities, finite counterexamples from prevalence, "
    "and finite-grid conformance from continuum conclusions."
)
EXPECTED_PRIMARY_TYPES = {
    "finite_markov_spec": "FiniteMarkovSpec=(carrier,kernel,initial_distribution,scope)",
    "path_event_spec": "PathEventSpec=(horizon,event,quantifier,scope)",
    "prevalence_spec": "PrevalenceSpec=(population,measure,property,scope)",
    "continuum_lift_spec": "ContinuumLiftSpec=(discrete_domain,continuum_domain,bridge,property,topology,measure,regularity,convergence_mode,error_control,scope)",
}
EXPECTED_QUANTIFIERS = {
    "exists": "at least one admissible or support witness exists",
    "positive_probability": "the declared probability measure assigns event mass greater than zero",
    "almost_sure": "the declared probability measure assigns event mass exactly one",
    "finite_horizon": "the event is evaluated only through an explicitly finite horizon",
    "infinite_horizon": "the event is defined on an infinite path space with an explicitly declared limiting or measure-theoretic semantics",
}
EXPECTED_BOUNDARIES = [
    "RELATION_REACHABLE != POSITIVE_PROBABILITY",
    "EXISTS_PATH != POSITIVE_PROBABILITY",
    "POSITIVE_PROBABILITY != ALMOST_SURE",
    "FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS",
    "ONE_TRAJECTORY != DISTRIBUTION",
    "FINITE_SAMPLE_FREQUENCY != MODEL_PROBABILITY",
    "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM",
    "PREVALENCE_REQUIRES_DECLARED_MEASURE",
    "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY",
    "DISCRETIZATION_CONVERGENCE != ASSUMED_WITHOUT_ERROR_CONTROL",
    "FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY",
]
EXPECTED_LIMITS = {
    "kernel_state_count": 2,
    "kernel_row_probability_denominator": 2,
    "finite_kernel_count": 9,
    "initial_distribution_count": 3,
    "kernel_transport_checks": 27,
    "path_mass_evaluations": 756,
    "path_normalization_checks": 81,
    "finite_atomic_event_checks": 48,
    "almost_sure_event_cases": 18,
    "positive_probability_event_cases": 30,
    "support_witness_event_cases": 30,
    "finite_survival_checks": 16,
    "prevalence_measure_event_checks": 80,
    "finite_grid_nonlifting_checks": 31,
    "policy": "The executable battery uses exact Fraction arithmetic on bounded finite probability models and exact rational polynomial controls. It verifies declared finite obligations and counterexamples only; it does not establish arbitrary stochastic-process, measure-theoretic, continuum, ergodic, prevalence, or infinite-path theorems.",
}
EXPECTED_AUTHORITIES = {
    "human": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
    "results": "machine/continuum_stochastic_prevalence_results.json",
    "validator": "scripts/validate_continuum_stochastic_prevalence.py",
    "experiment": "experiments/continuum_stochastic_prevalence/run.py",
    "tests": "tests/test_continuum_stochastic_prevalence.py",
    "receipt": "experiments/run_continuum_stochastic_prevalence.py",
    "artifact_verifier": "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "recovery_base": "machine/recovery_specialization_contract.json",
    "relation_base": "machine/relation_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "roadmap": "ROADMAP.md",
    "workflow": ".github/workflows/finite-adversarial.yml",
}
EXPECTED_CENTRAL_AUTHORITY = {
    "human": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
    "machine_contract": "machine/continuum_stochastic_prevalence_contract.json",
    "machine_results": "machine/continuum_stochastic_prevalence_results.json",
    "validator": "scripts/validate_continuum_stochastic_prevalence.py",
    "experiment": "experiments/continuum_stochastic_prevalence/run.py",
    "tests": "tests/test_continuum_stochastic_prevalence.py",
    "receipt_runner": "experiments/run_continuum_stochastic_prevalence.py",
    "receipt_version": "1.0.0",
    "artifact_verifier": "scripts/verify_continuum_stochastic_prevalence_artifacts.py",
    "recovery_base_authority": "machine/recovery_specialization_contract.json",
    "relation_base_authority": "machine/relation_contract.json",
    "roadmap_state": "machine/roadmap_state.json",
    "workflow": ".github/workflows/finite-adversarial.yml",
    "rule": "Stochastic, infinite-horizon, prevalence, and continuum conclusions require separately declared probability, measure, quantifier, topology, regularity, convergence, and error-control obligations; bounded finite evidence cannot silently supply them.",
}
EXPECTED_CENTRAL_HARD_RULES = {
    "relation_reachability_implies_positive_probability": False,
    "positive_probability_implies_almost_sure": False,
    "finite_horizon_success_implies_infinite_liveness": False,
    "single_trajectory_identifies_distribution": False,
    "finite_counterexample_implies_prevalence": False,
    "finite_grid_agreement_implies_continuum_equality": False,
    "discretization_implies_convergence_without_error_control": False,
}
EXPECTED_DEFERRALS = [
    "general measurable-space and sigma-algebra construction",
    "continuous-time stochastic processes and generators",
    "martingale and stopping-time theorems",
    "ergodicity, mixing, stationarity, and invariant-measure theorems",
    "continuum existence, compactness, regularity, and convergence proofs",
    "measure concentration and asymptotic prevalence theorems",
    "empirical frequency calibration and statistical inference to planned PR #18",
    "Lean proof objects",
]
EXPECTED_CONTRACT_TOP_LEVEL = {
    "type", "schema_version", "snapshot_date", "claim_class", "scope", "primary_types", "quantifiers",
    "hard_boundaries", "execution_limits", "authorities", "explicit_deferrals",
}
EXPECTED_RESULTS_TOP_LEVEL = {"type", "schema_version", "snapshot_date", "records", "claim_boundary"}
EXPECTED_THEOREM_FIELDS = {
    "id", "name", "claim_class", "statement", "hypotheses", "proof_reference", "executable_evidence", "nonclaims",
}
EXPECTED_COUNTEREXAMPLE_FIELDS = {"id", "name", "claim_class", "statement", "fixture", "evidence", "nonclaims"}
EXPECTED_EVIDENCE = ["experiments/continuum_stochastic_prevalence/run.py", "tests/test_continuum_stochastic_prevalence.py"]
EXPECTED_RESULT_BOUNDARY = (
    "FINITE_REACHABILITY != INFINITE_PATH_LIVENESS; FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM; "
    "FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY; FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY"
)
EXPECTED_THEOREMS = {
    "UFT-CSP-001": {
        "name": "Finite stochastic kernels preserve total probability",
        "statement": "For a finite carrier, a row-stochastic kernel K with nonnegative entries and unit row sums maps every probability distribution p to a probability distribution p' defined by p'(y)=sum_x p(x)K(x,y).",
        "hypotheses": ["X is finite", "p:X->Q_{>=0} has sum_x p(x)=1", "K:XxX->Q_{>=0}", "for every x, sum_y K(x,y)=1"],
        "proof_reference": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md#uft-csp-001-finite-stochastic-kernels-preserve-total-probability",
        "nonclaims": ["Finite row-stochastic mass preservation does not establish stationarity, ergodicity, continuum dynamics, empirical calibration, or physical randomness."],
    },
    "UFT-CSP-002": {
        "name": "Finite atomic stochastic quantifiers are not interchangeable",
        "statement": "For a finite probability distribution p and event E, p(E)=1 implies p(E)>0, and p(E)>0 holds exactly when E intersects the positive-mass support of p; the converses from positive probability or support existence to almost-sure truth do not hold in general.",
        "hypotheses": ["X is finite", "p:X->Q_{>=0} has total mass one", "E is a subset of X"],
        "proof_reference": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md#uft-csp-002-finite-atomic-stochastic-quantifiers-are-not-interchangeable",
        "nonclaims": ["This finite atomic statement is not a substitute for general measure-theoretic support, almost-everywhere, or infinite-path semantics."],
    },
    "UFT-CSP-003": {
        "name": "Finite-horizon path mass is the product of declared stochastic factors",
        "statement": "For a finite Markov specification with initial distribution p and row-stochastic kernel K, the probability of a finite path (x0,...,xh) is p(x0) times the product of K(xt,xt+1), and the masses of all length-h paths sum exactly to one.",
        "hypotheses": ["X is finite", "p is a probability distribution on X", "K is a row-stochastic kernel on X", "h is a finite natural-number horizon"],
        "proof_reference": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md#uft-csp-003-finite-horizon-path-mass-is-the-product-of-declared-stochastic-factors",
        "nonclaims": ["A finite-horizon path formula does not by itself define an infinite path-space measure or prove infinite-horizon liveness."],
    },
    "UFT-CSP-004": {
        "name": "Prevalence is indexed by a declared measure",
        "statement": "For a declared probability measure mu on a finite population X and failure property F subseteq X, prevalence is mu(F); therefore the same failure set can have different prevalence under different declared measures, and existence of a counterexample alone does not determine prevalence.",
        "hypotheses": ["X is finite", "mu is a probability measure on X", "F is a subset of X"],
        "proof_reference": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md#uft-csp-004-prevalence-is-indexed-by-a-declared-measure",
        "nonclaims": ["A formal finite prevalence value is not an empirical population estimate, confidence interval, causal rate, or universal frequency."],
    },
    "UFT-CSP-005": {
        "name": "Finite-grid agreement does not determine continuum equality",
        "statement": "For every finite set G of real grid points, the zero function and the nonzero polynomial q(x)=product_{a in G}(x-a) agree at every point of G while differing at every real point b not in G; finite-grid equality therefore does not imply continuum equality without additional assumptions.",
        "hypotheses": ["G is a finite set of real numbers", "b is a real number not in G"],
        "proof_reference": "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md#uft-csp-005-finite-grid-agreement-does-not-determine-continuum-equality",
        "nonclaims": ["The theorem does not deny convergence when a discretization is accompanied by sufficient regularity, topology, approximation, and error-control hypotheses."],
    },
}
EXPECTED_COUNTEREXAMPLES = {
    "CX-CSP-001": {
        "name": "Relation reachability can have zero stochastic probability",
        "statement": "A base relation may contain the edge 0->1 while a stochastic kernel assigns K(0,1)=0, so relation reachability alone does not imply positive stochastic path probability.",
        "fixture": "two-state relation edge with zero-probability stochastic transition",
        "nonclaims": ["The counterexample does not make the relation edge invalid; it separates relational possibility from the declared stochastic support."],
    },
    "CX-CSP-002": {
        "name": "Positive probability is not almost-sure truth",
        "statement": "Under a fair two-outcome distribution, the event {H} has probability 1/2, which is positive but not one.",
        "fixture": "fair binary event with probability one half",
        "nonclaims": ["The example concerns quantifier strength only and does not imply that positive-probability events are empirically common."],
    },
    "CX-CSP-003": {
        "name": "Finite-horizon survival can coexist with zero infinite-survival probability",
        "statement": "If independent survival at each step has probability q=1/2, then survival through every finite horizon n has positive probability 2^{-n}, while the probability of surviving forever is lim_{n->infinity}2^{-n}=0.",
        "fixture": "geometric survival process with q one half",
        "nonclaims": ["The fixture does not claim that every infinite stochastic process has this limit or that finite-horizon evidence is useless."],
    },
    "CX-CSP-004": {
        "name": "One trajectory frequency is not the model probability",
        "statement": "The length-three trajectory HHH has empirical head frequency 1 under a fair coin model whose declared single-step head probability is 1/2; one observed path therefore does not identify the generating distribution.",
        "fixture": "HHH under a fair Bernoulli model",
        "nonclaims": ["The example does not deny statistical consistency under independently justified sampling assumptions and asymptotic theorems."],
    },
    "CX-CSP-005": {
        "name": "One finite counterexample does not determine prevalence",
        "statement": "On the same two-point carrier with the same failure set {x}, one probability measure can assign failure prevalence 1/100 while another assigns 99/100, so existence of x does not determine how prevalent failure is.",
        "fixture": "same failure set under low-mass and high-mass measures",
        "nonclaims": ["The construction is a formal measure-dependence control, not an empirical estimate of any real population."],
    },
    "CX-CSP-006": {
        "name": "Perfect finite-grid agreement can fail between grid points",
        "statement": "The functions f(x)=0 and g(x)=x(x-1/2)(x-1) agree on the grid {0,1/2,1} but differ at x=1/4, so perfect grid conformance does not license continuum equality.",
        "fixture": "three-point rational grid with off-grid polynomial witness",
        "nonclaims": ["The example does not refute a separately proved convergence theorem with explicit regularity and error bounds."],
    },
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
    (17, "continuum-stochastic-prevalence-obligations", "active-implemented-in-current-change"),
    (18, "empirical-falsification-profile", "planned"),
]
PRIVATE_PATTERNS = ("mail.google.com", "gmail", "connector_", "private-user-images", "attachment_id")
PROMOTION_PATTERNS = (
    "reachable means positive probability",
    "positive probability means almost sure",
    "finite horizon proves infinite liveness",
    "one trajectory proves the distribution",
    "counterexample proves prevalence",
    "finite grid proves continuum equality",
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
            errors.append(f"missing CSP authority file: {name}={path.relative_to(ROOT)}")
    if errors:
        return {"status": "error", "errors": errors, "result_count": 0, "boundary_count": 0}

    contract = load_json(PATHS["contract"])
    results = load_json(PATHS["results"])
    recovery_base = load_json(PATHS["recovery_base"])
    relation_base = load_json(PATHS["relation_base"])
    base_contract = load_json(PATHS["base_contract"])
    roadmap_state = load_json(PATHS["roadmap_state"])
    human = PATHS["human"].read_text(encoding="utf-8")
    roadmap = PATHS["roadmap"].read_text(encoding="utf-8")
    readme = PATHS["readme"].read_text(encoding="utf-8")
    claims = PATHS["claims"].read_text(encoding="utf-8")
    repro = PATHS["repro"].read_text(encoding="utf-8")

    if set(contract) != EXPECTED_CONTRACT_TOP_LEVEL: errors.append("CSP contract top-level field set drift")
    if contract.get("type") != "uft-id-continuum-stochastic-prevalence-contract": errors.append("CSP contract type drift")
    if contract.get("schema_version") != "1.0.0": errors.append("CSP contract schema drift")
    if contract.get("snapshot_date") != "2026-08-24": errors.append("CSP contract snapshot drift")
    if contract.get("claim_class") != "DEFINITION": errors.append("CSP contract claim class drift")
    if contract.get("scope") != EXPECTED_SCOPE: errors.append("CSP contract scope drift")
    if contract.get("primary_types") != EXPECTED_PRIMARY_TYPES: errors.append("CSP primary type registry drift")
    if contract.get("quantifiers") != EXPECTED_QUANTIFIERS: errors.append("CSP quantifier registry drift")
    if contract.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("CSP hard-boundary registry drift")
    if contract.get("execution_limits") != EXPECTED_LIMITS: errors.append("CSP execution limits drift")
    if contract.get("authorities") != EXPECTED_AUTHORITIES:
        errors.append("CSP authority registry drift")
    else:
        for key, value in EXPECTED_AUTHORITIES.items():
            safe_path(value, f"CSP authority {key}", errors)
    if contract.get("explicit_deferrals") != EXPECTED_DEFERRALS: errors.append("CSP explicit deferrals drift")

    if recovery_base.get("type") != "uft-id-recovery-specialization-contract": errors.append("CSP Recovery base authority drift")
    if relation_base.get("type") != "uft-id-relation-core-contract": errors.append("CSP relation base authority drift")
    recovery_deferrals = recovery_base.get("explicit_deferrals")
    if not isinstance(recovery_deferrals, list) or "stochastic selector or rewrite kernels" not in recovery_deferrals:
        errors.append("frozen Recovery stochastic deferral drift")

    if base_contract.get("continuum_stochastic_prevalence_authority") != EXPECTED_CENTRAL_AUTHORITY:
        errors.append("central CSP authority registration drift")
    library = base_contract.get("experiment_library")
    if not isinstance(library, dict) or library.get("continuum_stochastic_prevalence_receipt_runner") != "experiments/run_continuum_stochastic_prevalence.py" or library.get("continuum_stochastic_prevalence_receipt_version") != "1.0.0":
        errors.append("central CSP receipt registry drift")
    hard_rules = base_contract.get("hard_rules")
    if not isinstance(hard_rules, dict) or any(hard_rules.get(key) is not value for key, value in EXPECTED_CENTRAL_HARD_RULES.items()):
        errors.append("central CSP hard-rule registration drift")
    reads = base_contract.get("required_agent_reads")
    required_reads = {
        "theory/CONTINUUM_STOCHASTIC_PREVALENCE.md",
        "machine/continuum_stochastic_prevalence_contract.json",
        "machine/continuum_stochastic_prevalence_results.json",
        "scripts/validate_continuum_stochastic_prevalence.py",
        "experiments/run_continuum_stochastic_prevalence.py",
    }
    if not isinstance(reads, list) or not required_reads.issubset(set(reads)):
        errors.append("central CSP agent-read registration drift")

    if set(results) != EXPECTED_RESULTS_TOP_LEVEL: errors.append("CSP result registry top-level field set drift")
    if results.get("type") != "uft-id-continuum-stochastic-prevalence-result-registry": errors.append("CSP result type drift")
    if results.get("schema_version") != "1.0.0": errors.append("CSP result schema drift")
    if results.get("snapshot_date") != "2026-08-24": errors.append("CSP result snapshot drift")
    if results.get("claim_boundary") != EXPECTED_RESULT_BOUNDARY: errors.append("CSP result claim boundary drift")
    records = results.get("records")
    if not isinstance(records, list):
        errors.append("CSP result registry malformed")
        records = []
    by_id: dict[str, dict[str, Any]] = {}
    ids: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            errors.append(f"CSP result {index} malformed")
            continue
        rid = str(record["id"])
        if rid in EXPECTED_THEOREMS and set(record) != EXPECTED_THEOREM_FIELDS:
            errors.append(f"{rid} theorem field set drift")
        if rid in EXPECTED_COUNTEREXAMPLES and set(record) != EXPECTED_COUNTEREXAMPLE_FIELDS:
            errors.append(f"{rid} counterexample field set drift")
        if rid in by_id:
            errors.append(f"duplicate CSP result id: {rid}")
        else:
            by_id[rid] = record
        ids.append(rid)
    expected_ids = set(EXPECTED_THEOREMS) | set(EXPECTED_COUNTEREXAMPLES)
    if set(ids) != expected_ids or len(ids) != len(expected_ids): errors.append("CSP result identity set drift")

    for rid, expected in EXPECTED_THEOREMS.items():
        record = by_id.get(rid)
        if record is None: continue
        if record.get("name") != expected["name"]: errors.append(f"{rid} name drift")
        if record.get("claim_class") != "PROVED": errors.append(f"{rid} claim class drift")
        if record.get("statement") != expected["statement"]: errors.append(f"{rid} statement drift")
        if record.get("hypotheses") != expected["hypotheses"]: errors.append(f"{rid} hypotheses drift")
        if record.get("proof_reference") != expected["proof_reference"]: errors.append(f"{rid} proof reference drift")
        if record.get("executable_evidence") != EXPECTED_EVIDENCE: errors.append(f"{rid} executable evidence drift")
        if record.get("nonclaims") != expected["nonclaims"]: errors.append(f"{rid} nonclaims drift")
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

    if roadmap_state.get("type") != "uft-id-roadmap-state": errors.append("CSP roadmap type drift")
    if roadmap_state.get("schema_version") != "1.5.0": errors.append("CSP roadmap schema drift")
    if roadmap_state.get("snapshot_date") != "2026-08-24": errors.append("CSP roadmap snapshot drift")
    if roadmap_state.get("basis_commit") != "2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f": errors.append("CSP roadmap basis commit must be merged Recovery PR")
    if roadmap_state.get("completed") != [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16]: errors.append("CSP roadmap completed set drift")
    if roadmap_state.get("active_planned_surface") != 17: errors.append("CSP roadmap active surface must be PR #17")
    if roadmap_state.get("deferred") != [10]: errors.append("CSP roadmap deferred set drift")
    sequence = roadmap_state.get("sequence")
    actual_sequence: list[tuple[object, object, object]] = []
    if isinstance(sequence, list):
        actual_sequence = [(item.get("planned_pr"), item.get("surface"), item.get("status")) for item in sequence if isinstance(item, dict)]
    if actual_sequence != EXPECTED_ROADMAP_SEQUENCE: errors.append("CSP roadmap sequence/status drift")
    rules = roadmap_state.get("rules")
    required_rule = "Stochastic, prevalence, infinite-horizon, and continuum claims require separately declared probability/measure and lifting obligations; finite reachability, finite samples, counterexamples, or grid conformance cannot supply them by default."
    if not isinstance(rules, list) or required_rule not in rules: errors.append("CSP roadmap obligation hard rule missing")

    roadmap_anchors = (
        "## Active now — planned PR #17",
        "### Continuum, stochastic, and prevalence obligations",
        "python scripts/validate_continuum_stochastic_prevalence.py",
        "python experiments/continuum_stochastic_prevalence/run.py --json",
        "python experiments/run_continuum_stochastic_prevalence.py --json",
    )
    for anchor in roadmap_anchors:
        if anchor not in roadmap: errors.append(f"roadmap missing CSP anchor: {anchor}")

    surface_anchors = (
        (readme, ("## Continuum, stochastic, and prevalence obligations authority", "machine/continuum_stochastic_prevalence_contract.json", "FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS"), "README4AI"),
        (claims, ("### C13 - Stochastic, prevalence, and continuum lifting require explicit obligations", "UFT-CSP-001", "FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM"), "claims"),
        (repro, ("## Continuum-stochastic-prevalence conformance boundary", "continuum-stochastic-prevalence-validation.json", "python scripts/validate_continuum_stochastic_prevalence.py"), "reproducibility"),
    )
    for text, anchors, label in surface_anchors:
        for anchor in anchors:
            if anchor not in text: errors.append(f"{label} missing CSP anchor: {anchor}")

    experiment = load_module("csp_validator_experiment", PATHS["experiment"])
    witness = experiment.run_suite()
    if witness.get("hard_boundaries") != EXPECTED_BOUNDARIES: errors.append("CSP witness hard-boundary drift")
    expected_bounded = {
        "finite_kernels": {"finite_kernel_count": 9, "initial_distribution_count": 3, "kernel_transport_checks": 27, "path_mass_evaluations": 756, "path_normalization_checks": 81},
        "finite_atomic_quantifiers": {"finite_atomic_event_checks": 48, "almost_sure_event_cases": 18, "positive_probability_event_cases": 30, "support_witness_event_cases": 30},
        "survival": {"finite_survival_checks": 16, "infinite_survival_zero_controls": 2},
        "prevalence": {"declared_measure_count": 10, "prevalence_measure_event_checks": 80},
        "continuum_nonlifting": {"finite_grid_nonlifting_checks": 31},
    }
    if witness.get("bounded_checks") != expected_bounded: errors.append("CSP bounded witness count drift")
    fixtures = witness.get("fixtures")
    if not isinstance(fixtures, dict) or set(fixtures) != set(EXPECTED_COUNTEREXAMPLES): errors.append("CSP witness counterexample identity drift")

    combined = "\n".join((
        json.dumps(contract, ensure_ascii=False), json.dumps(results, ensure_ascii=False),
        json.dumps(base_contract, ensure_ascii=False), human, roadmap, readme, claims, repro,
    )).casefold()
    for token in PRIVATE_PATTERNS:
        if token in combined: errors.append(f"CSP authority contains forbidden private locator: {token}")
    for phrase in PROMOTION_PATTERNS:
        if phrase in combined: errors.append(f"CSP authority contains forbidden promotion: {phrase}")

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
        print(f"Continuum/Stochastic/Prevalence authority: ok ({result['result_count']} results, {result['boundary_count']} hard boundaries)")
    else:
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
