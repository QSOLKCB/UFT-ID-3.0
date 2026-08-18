#!/usr/bin/env python3
"""Finite witnesses distilled from recurring cross-repository QSOL contracts.

The source repositories motivate the questions. This executable proves/checks
only the explicit finite statements below and does not import software semantics
as physical ontology.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.lib.information import require  # noqa: E402

MAX_MINIMUM_BASIS_SUBSETS = 1 << 18


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def transport_identity_case() -> dict[str, object]:
    payload = b"UFT-ID-3 cross-repo transport identity fixture\n"
    locations = [
        "disk:/archive/object.dat",
        "usb:/object.dat",
        "https://example.invalid/object.dat",
    ]
    digest = sha256_bytes(payload)
    records = [
        {"location": location, "content_sha256": sha256_bytes(payload)}
        for location in locations
    ]
    require(
        {record["content_sha256"] for record in records} == {digest},
        "byte-preserving transport changed content identity",
    )
    require(len({record["location"] for record in records}) == len(locations), "locations should differ")
    return {
        "result_id": "CR1",
        "payload_bytes": len(payload),
        "content_sha256": digest,
        "locations": records,
        "conclusion": "content identity unchanged while transport location changes",
    }


def projection_collision_case() -> dict[str, object]:
    source_states = [(0, 0), (0, 1), (1, 0), (1, 1)]

    def project(state: tuple[int, int]) -> int:
        return state[0]

    fibres: dict[int, list[tuple[int, int]]] = {}
    for state in source_states:
        fibres.setdefault(project(state), []).append(state)

    collisions = {
        observed: states
        for observed, states in fibres.items()
        if len(states) > 1
    }
    require(collisions, "projection should be non-injective")

    reconstruction = {observed: states[0] for observed, states in fibres.items()}
    exact = [state for state in source_states if reconstruction[project(state)] == state]
    failed = [state for state in source_states if reconstruction[project(state)] != state]
    require(failed, "non-injective projection unexpectedly admitted a global exact reconstruction")

    return {
        "result_id": "CR2",
        "source_states": [list(state) for state in source_states],
        "fibres": {str(key): [list(state) for state in value] for key, value in sorted(fibres.items())},
        "reconstruction": {str(key): list(value) for key, value in sorted(reconstruction.items())},
        "exact_reconstructions": [list(state) for state in exact],
        "failed_reconstructions": [list(state) for state in failed],
        "conclusion": "non-injective projection prevents a global left inverse",
    }


def calibration_locality_case() -> dict[str, object]:
    measurement = 0.60
    profiles = {
        "Gamma_A": 0.50,
        "Gamma_B": 0.70,
    }

    def classify(value: float, threshold: float) -> str:
        return "HIGH" if value >= threshold else "LOW"

    classifications = {
        name: classify(measurement, threshold)
        for name, threshold in profiles.items()
    }
    require(
        classifications["Gamma_A"] != classifications["Gamma_B"],
        "calibration fixture should reverse classification",
    )
    return {
        "result_id": "CR3",
        "measurement": measurement,
        "profiles": profiles,
        "classifications": classifications,
        "conclusion": "same measurement receives opposite classes under different local thresholds",
    }


def cyclic_stride(n: int, stride: int) -> list[int]:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if isinstance(stride, bool) or not isinstance(stride, int):
        raise ValueError("stride must be an integer")
    return [(stride * index) % n for index in range(n)]


def cyclic_traversal_case() -> dict[str, object]:
    fixtures = [(27, 17), (101, 3), (303, 2)]
    results = []
    for n, stride in fixtures:
        require(math.gcd(n, stride) == 1, f"fixture ({n},{stride}) must be coprime")
        traversal = cyclic_stride(n, stride)
        require(len(set(traversal)) == n, f"coprime traversal did not cover all residues for n={n}")
        require(set(traversal) == set(range(n)), f"traversal residue set mismatch for n={n}")
        results.append(
            {
                "n": n,
                "stride": stride,
                "gcd": 1,
                "unique_states": len(set(traversal)),
                "first_12": traversal[:12],
            }
        )

    non_coprime = cyclic_stride(27, 9)
    require(len(set(non_coprime)) < 27, "non-coprime control should not visit all residues")
    return {
        "result_id": "CR4",
        "coprime_fixtures": results,
        "non_coprime_control": {
            "n": 27,
            "stride": 9,
            "gcd": math.gcd(27, 9),
            "unique_states": len(set(non_coprime)),
        },
        "conclusion": "coprime cyclic strides are permutations; non-coprime control is not",
    }


def all_subsets(items: list[str]) -> Iterable[tuple[str, ...]]:
    for size in range(len(items) + 1):
        yield from combinations(items, size)


def minimum_basis(
    obligations: set[str],
    coverage: dict[str, set[str]],
    costs: dict[str, int],
    *,
    max_subsets: int = MAX_MINIMUM_BASIS_SUBSETS,
) -> tuple[str, ...]:
    ids = sorted(coverage)
    if set(costs) != set(ids):
        raise ValueError("coverage/cost ids differ")
    if isinstance(max_subsets, bool) or not isinstance(max_subsets, int) or max_subsets < 1:
        raise ValueError("max_subsets must be a positive integer")
    for record_id in ids:
        cost = costs[record_id]
        if isinstance(cost, bool) or not isinstance(cost, int) or cost < 0:
            raise ValueError(f"cost for {record_id} must be a non-negative integer")

    if not obligations:
        return ()

    subset_work = 1 << len(ids)
    if subset_work > max_subsets:
        raise ValueError(
            f"minimum-basis exhaustive work {subset_work} subsets exceeds ceiling {max_subsets}"
        )

    best_objective: tuple[int, int, tuple[str, ...]] | None = None
    best_subset: tuple[str, ...] | None = None
    for subset in all_subsets(ids):
        covered: set[str] = set()
        for record_id in subset:
            covered.update(coverage[record_id])
        if not obligations.issubset(covered):
            continue
        objective = (
            sum(costs[record_id] for record_id in subset),
            len(subset),
            subset,
        )
        if best_objective is None or objective < best_objective:
            best_objective = objective
            best_subset = subset

    if best_subset is None:
        raise ValueError("no sufficient basis exists")
    return best_subset


def minimum_basis_case() -> dict[str, object]:
    obligations = {"identity", "timeline", "evidence"}
    coverage = {
        "r1": {"identity"},
        "r2": {"timeline"},
        "r3": {"evidence"},
        "r4": {"identity", "timeline"},
        "r5": {"timeline", "evidence"},
        "r6": {"identity", "evidence"},
    }
    costs = {
        "r1": 1,
        "r2": 1,
        "r3": 1,
        "r4": 2,
        "r5": 2,
        "r6": 2,
    }
    selected = minimum_basis(obligations, coverage, costs)
    require(selected == ("r1", "r5"), f"unexpected lexicographic minimum basis: {selected}")
    covered: set[str] = set()
    for record_id in selected:
        covered.update(coverage[record_id])
    require(obligations.issubset(covered), "selected basis is not sufficient")
    return {
        "result_id": "CR5",
        "obligations": sorted(obligations),
        "selected_basis": list(selected),
        "selected_total_cost": sum(costs[record_id] for record_id in selected),
        "selected_count": len(selected),
        "coverage": {key: sorted(value) for key, value in sorted(coverage.items())},
        "costs": costs,
        "exhaustive_work_subsets": 1 << len(coverage),
        "max_exhaustive_subsets": MAX_MINIMUM_BASIS_SUBSETS,
        "conclusion": "finite objective plus total lexicographic tie-break yields one deterministic sufficient basis",
    }


def integrity_not_truth_case() -> dict[str, object]:
    statement = "2+2=5"
    payload = statement.encode("utf-8")
    digest = sha256_bytes(payload)
    verified_again = sha256_bytes(payload)
    require(digest == verified_again, "integrity verification should reproduce the digest")
    mathematical_truth = False
    require(not mathematical_truth, "fixture proposition is intentionally false")
    return {
        "result_id": "CR6",
        "statement": statement,
        "utf8_sha256": digest,
        "integrity_verified": digest == verified_again,
        "semantic_truth": mathematical_truth,
        "conclusion": "perfect byte integrity does not entail proposition truth",
    }


def deterministic_model(value: object) -> str:
    return sha256_bytes(canonical_json_bytes({"model_version": "fixture-v1", "input": value}))


def replay_case() -> dict[str, object]:
    value = {"state": [1, 2, 3], "mode": "finite"}
    first = deterministic_model(value)
    second = deterministic_model(value)
    changed = deterministic_model({"state": [1, 2, 4], "mode": "finite"})
    require(first == second, "deterministic replay mismatch")
    require(first != changed, "changed-input control unexpectedly preserved result identity")
    return {
        "result_id": "CR7",
        "canonical_input_sha256": sha256_bytes(canonical_json_bytes(value)),
        "first_result": first,
        "second_result": second,
        "changed_input_result": changed,
        "same_input_same_result": first == second,
        "changed_input_control_differs": first != changed,
        "conclusion": "fixed deterministic function plus equal canonical input yields equal result",
    }


def receiver_contract_case() -> dict[str, object]:
    source = (2.0, 4.0, 8.0)
    scale = 4.0
    ratio_preserving = tuple(scale * value for value in source)
    clipped = tuple(min(16.0, scale * value) for value in source)

    def ratios(values: tuple[float, ...]) -> tuple[float, ...]:
        base = values[0]
        return tuple(value / base for value in values[1:])

    source_ratios = ratios(source)
    preserved_ratios = ratios(ratio_preserving)
    clipped_ratios = ratios(clipped)
    require(source_ratios == preserved_ratios, "uniform scale receiver should preserve ratios")
    require(source_ratios != clipped_ratios, "clipped receiver should alter the declared ratio structure")
    return {
        "diagnostic_id": "RX1",
        "source": list(source),
        "uniform_scale_receiver": list(ratio_preserving),
        "clipped_receiver": list(clipped),
        "source_ratios": list(source_ratios),
        "uniform_scale_ratios": list(preserved_ratios),
        "clipped_ratios": list(clipped_ratios),
        "conclusion": "receiver preservation is structure-specific and must be declared",
    }


def run() -> dict[str, object]:
    return {
        "suite_id": "UFTID3-CROSS-REPO-FINITE-PATTERNS",
        "claim_boundary": "software patterns motivate finite abstractions; they do not establish physical ontology",
        "results": [
            transport_identity_case(),
            projection_collision_case(),
            calibration_locality_case(),
            cyclic_traversal_case(),
            minimum_basis_case(),
            integrity_not_truth_case(),
            replay_case(),
        ],
        "receiver_diagnostic": receiver_contract_case(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(result["suite_id"])
        for item in result["results"]:
            print(f"{item['result_id']}: {item['conclusion']}")
        print(f"RX1: {result['receiver_diagnostic']['conclusion']}")


if __name__ == "__main__":
    main()
