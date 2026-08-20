#!/usr/bin/env python3
"""Finite executable witnesses for PR #8 formalization contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.lib.information import coarse_grain, require, shannon_entropy

P0 = (0.0, 0.0, 0.25, 0.75)
P1 = (0.0, 0.5, 0.0, 0.5)
PARTITION_NEG = ((0, 2), (1, 3))
PARTITION_POS = ((0, 1), (2, 3))


def sqnorm(v: tuple[int, int]) -> int:
    return v[0] * v[0] + v[1] * v[1]


def rot90(v: tuple[int, int]) -> tuple[int, int]:
    return (-v[1], v[0])


def scale2(v: tuple[int, int]) -> tuple[int, int]:
    return (2 * v[0], 2 * v[1])


def entropy_delta(before: tuple[float, ...], after: tuple[float, ...]) -> float:
    return shannon_entropy(after) - shannon_entropy(before)


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

    q0_neg = coarse_grain(P0, PARTITION_NEG)
    q1_neg = coarse_grain(P1, PARTITION_NEG)
    q0_pos = coarse_grain(P0, PARTITION_POS)
    q1_pos = coarse_grain(P1, PARTITION_POS)

    fine_delta = entropy_delta(P0, P1)
    neg_delta = entropy_delta(q0_neg, q1_neg)
    pos_delta = entropy_delta(q0_pos, q1_pos)

    require(fine_delta > 0.0, "fine entropy delta must be positive")
    require(neg_delta < 0.0, "first observer entropy delta must be negative")
    require(pos_delta > 0.0, "second observer entropy delta must be positive")

    entropy = {
        "fine": {
            "p0": list(P0),
            "p1": list(P1),
            "h0": shannon_entropy(P0),
            "h1": shannon_entropy(P1),
            "delta": fine_delta,
            "sign": 1,
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

    # Claim-realization witness: a map from two states to one state cannot be injective.
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

    # Synthetic falsification-contract witness.
    q0, q1 = 1.0, 2.0
    falsification = {
        "hypothesis_id": "FALS-SYN-001",
        "prediction": "q(1) < q(0)",
        "q0": q0,
        "q1": q1,
        "rejection_condition_met": q1 >= q0,
        "status": "synthetic-rejected",
    }
    require(falsification["rejection_condition_met"] is True, "synthetic rejection condition must trigger")

    return {
        "type": "uft-id-pr8-formalization-witness",
        "schema_version": "1.0.0",
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
