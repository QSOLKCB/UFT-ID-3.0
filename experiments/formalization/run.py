#!/usr/bin/env python3
"""Finite executable witnesses for PR #8 formalization contracts."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.lib.information import (
    apply_row_stochastic,
    coarse_grain,
    require,
    shannon_entropy,
)

P0 = (0.0, 0.0, 0.25, 0.75)
EXPECTED_P1 = (0.0, 0.5, 0.0, 0.5)
FINE_TRANSITION = (
    (1.0, 0.0, 0.0, 0.0),
    (0.0, 1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0, 0.0),
    (0.0, 1.0 / 3.0, 0.0, 2.0 / 3.0),
)
PARTITION_NEG = ((0, 2), (1, 3))
PARTITION_POS = ((0, 1), (2, 3))
RELATION_RE = re.compile(r"^q\(1\)\s*(<=|>=|==|=|<|>)\s*q\(0\)$")


def sqnorm(v: tuple[int, int]) -> int:
    return v[0] * v[0] + v[1] * v[1]


def rot90(v: tuple[int, int]) -> tuple[int, int]:
    return (-v[1], v[0])


def scale2(v: tuple[int, int]) -> tuple[int, int]:
    return (2 * v[0], 2 * v[1])


def entropy_delta(before: tuple[float, ...], after: tuple[float, ...]) -> float:
    return shannon_entropy(after) - shannon_entropy(before)


def evaluate_relation(expression: str, q0: float, q1: float) -> bool:
    """Evaluate the tiny relation language used by the synthetic machine fixture."""
    match = RELATION_RE.fullmatch(expression.strip())
    if match is None:
        raise ValueError(f"unsupported synthetic relation: {expression!r}")
    op = match.group(1)
    if op == "<":
        return q1 < q0
    if op == ">":
        return q1 > q0
    if op == "<=":
        return q1 <= q0
    if op == ">=":
        return q1 >= q0
    return q1 == q0


def load_falsification_fixture() -> dict[str, object]:
    payload = json.loads((ROOT / "machine/falsification_contract.json").read_text(encoding="utf-8"))
    fixture = payload.get("synthetic_conformance_example")
    if not isinstance(fixture, dict):
        raise ValueError("machine falsification contract missing synthetic_conformance_example")
    return fixture


def run_suite() -> dict[str, object]:
    v = (3, 4)
    rv = rot90(v)
    sv = scale2(v)

    rotation = {
        "input": list(v),
        "output": list(rv),
        "sqnorm_before": sqnorm(v),
        "sqnorm_after": sqnorm(rv),
        "preserved": sqnorm(v) == sqnorm(rv),
    }
    require(rotation["preserved"] is True, "quarter-turn must preserve integer squared norm")

    scaling = {
        "input": list(v),
        "output": list(sv),
        "sqnorm_before": sqnorm(v),
        "sqnorm_after": sqnorm(sv),
        "preserved": sqnorm(v) == sqnorm(sv),
    }
    require(scaling["preserved"] is False, "scale2 must break nonzero squared-norm invariance")

    p1 = apply_row_stochastic(P0, FINE_TRANSITION)
    require(
        all(math.isclose(a, b, rel_tol=0.0, abs_tol=1e-12) for a, b in zip(p1, EXPECTED_P1)),
        "declared fine-state kernel must derive the canonical p1 endpoint",
    )
    q0_neg = coarse_grain(P0, PARTITION_NEG)
    q1_neg = coarse_grain(p1, PARTITION_NEG)
    q0_pos = coarse_grain(P0, PARTITION_POS)
    q1_pos = coarse_grain(p1, PARTITION_POS)

    fine_delta = entropy_delta(P0, p1)
    neg_delta = entropy_delta(q0_neg, q1_neg)
    pos_delta = entropy_delta(q0_pos, q1_pos)

    require(fine_delta > 0.0, "fine entropy delta must be positive")
    require(neg_delta < 0.0, "first observer entropy delta must be negative")
    require(pos_delta > 0.0, "second observer entropy delta must be positive")

    entropy = {
        "fine": {
            "p0": list(P0),
            "p1": list(p1),
            "h0": shannon_entropy(P0),
            "h1": shannon_entropy(p1),
            "delta": fine_delta,
            "sign": 1,
        },
        "fine_dynamics": {
            "type": "row-stochastic-discrete-update",
            "kernel": [list(row) for row in FINE_TRANSITION],
            "p1_derived_from_p0": True,
        },
        "observer_negative": {
            "partition": [list(block) for block in PARTITION_NEG],
            "p0": list(q0_neg),
            "p1": list(q1_neg),
            "h0": shannon_entropy(q0_neg),
            "h1": shannon_entropy(q1_neg),
            "delta": neg_delta,
            "sign": -1,
        },
        "observer_positive": {
            "partition": [list(block) for block in PARTITION_POS],
            "p0": list(q0_pos),
            "p1": list(q1_pos),
            "h0": shannon_entropy(q0_pos),
            "h1": shannon_entropy(q1_pos),
            "delta": pos_delta,
            "sign": 1,
        },
        "same_fine_dynamics": True,
        "same_information_functional": "Shannon entropy base 2",
    }

    irreversible_map = {"a": 0, "b": 0}
    reversible_claim = {
        "domain": ["a", "b"],
        "codomain": [0],
        "mapping": irreversible_map,
        "injective": len(set(irreversible_map.values())) == len(irreversible_map),
        "inverse_exists_on_full_domain": False,
        "claim_supported": False,
    }
    require(reversible_claim["injective"] is False, "many-to-one fixture must be non-injective")
    require(reversible_claim["claim_supported"] is False, "reversibility claim must fail on many-to-one fixture")

    fixture = load_falsification_fixture()
    values = fixture.get("fixture_values")
    predictions = fixture.get("predictions")
    rejections = fixture.get("rejection_conditions")
    require(isinstance(values, dict), "machine falsification fixture_values must be an object")
    require(isinstance(predictions, list) and len(predictions) == 1, "synthetic fixture must have one prediction")
    require(isinstance(rejections, list) and len(rejections) == 1, "synthetic fixture must have one rejection condition")
    q0 = float(values.get("q0"))
    q1 = float(values.get("q1"))
    require(math.isfinite(q0) and math.isfinite(q1), "synthetic q values must be finite")
    prediction = str(predictions[0])
    rejection = str(rejections[0])
    prediction_met = evaluate_relation(prediction, q0, q1)
    rejection_met = evaluate_relation(rejection, q0, q1)
    falsification = {
        "hypothesis_id": fixture.get("hypothesis_id"),
        "prediction": prediction,
        "rejection_condition": rejection,
        "q0": q0,
        "q1": q1,
        "prediction_met": prediction_met,
        "rejection_condition_met": rejection_met,
        "status": "synthetic-rejected" if rejection_met else "synthetic-not-rejected",
        "machine_authority": "machine/falsification_contract.json",
    }
    require(falsification["rejection_condition_met"] is True, "synthetic rejection condition must trigger")

    return {
        "type": "uft-id-pr8-formalization-witness",
        "schema_version": "1.0.1",
        "rotation_norm_exact": rotation,
        "scaling_norm_counterexample": scaling,
        "observer_entropy_sign_counterexample": entropy,
        "reversibility_claim_realization_counterexample": reversible_claim,
        "falsification_contract_synthetic_fixture": falsification,
        "nonclaims": [
            "Finite exact rotation arithmetic is not a physical conservation law.",
            "Observer-dependent entropy sign does not violate data processing for one fixed observation map.",
            "The synthetic falsification fixture is not an empirical scientific result.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("PR8 formalization witness: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
