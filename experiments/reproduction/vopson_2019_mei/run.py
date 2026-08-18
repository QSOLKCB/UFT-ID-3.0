#!/usr/bin/env python3
"""Exact arithmetic reproduction for Vopson 2019 MEI Eq. (6).

This script reproduces the numerical consequence of the declared identification
E_bit = k_B T ln 2 followed by E = mc^2. It does not validate that identification
as a physical law.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FIXTURES = Path(__file__).with_name("fixtures.json")

K_B = 1.380649e-23
C = 299792458


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite_number(value: object, label: str, *, non_negative: bool = False) -> float:
    """Validate a JSON numeric scalar before any coercion."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    if non_negative and result < 0:
        raise ValueError(f"{label} must be non-negative")
    return result


def non_negative_integer(value: object, label: str) -> int:
    """Validate a JSON integer without truncating floats or accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be a JSON integer")
    if value < 0:
        raise ValueError(f"{label} must be non-negative")
    return value


def landauer_scale(temperature_K: float) -> float:
    temperature = finite_number(temperature_K, "temperature_K", non_negative=True)
    return K_B * temperature * math.log(2.0)


def conditional_bit_mass(temperature_K: float) -> float:
    """Eq. (6) arithmetic conditional on E_bit = k_B T ln 2."""
    return landauer_scale(temperature_K) / (C * C)


def storage_mass(bits: int, temperature_K: float) -> float:
    validated_bits = non_negative_integer(bits, "bits")
    return validated_bits * conditional_bit_mass(temperature_K)


def relative_error(observed: float, expected: float) -> float:
    if expected == 0:
        return 0.0 if observed == 0 else math.inf
    return abs(observed - expected) / abs(expected)


def load_fixtures() -> dict[str, object]:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if not isinstance(fixtures, dict):
        raise TypeError("fixtures root must be a JSON object")
    return fixtures


def run() -> dict[str, object]:
    fixtures = load_fixtures()

    constants = fixtures.get("constants")
    if not isinstance(constants, dict):
        raise TypeError("constants must be a JSON object")
    fixture_kb = finite_number(constants.get("boltzmann_J_per_K"), "constants.boltzmann_J_per_K", non_negative=True)
    fixture_c = finite_number(constants.get("speed_of_light_m_per_s"), "constants.speed_of_light_m_per_s", non_negative=True)
    require(fixture_kb == K_B, "fixture k_B mismatch")
    require(fixture_c == C, "fixture c mismatch")

    tolerances = fixtures.get("comparison_tolerances")
    if not isinstance(tolerances, dict):
        raise TypeError("comparison_tolerances must be a JSON object")
    tolerance = finite_number(tolerances.get("relative"), "comparison_tolerances.relative", non_negative=True)
    source_rounding_tolerance = finite_number(
        tolerances.get("source_rounding_relative"),
        "comparison_tolerances.source_rounding_relative",
        non_negative=True,
    )

    cases = fixtures.get("temperature_cases")
    if not isinstance(cases, list) or not cases:
        raise TypeError("temperature_cases must be a non-empty JSON array")

    temperature_results = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise TypeError(f"temperature_cases[{index}] must be a JSON object")
        temperature = finite_number(case.get("temperature_K"), f"temperature_cases[{index}].temperature_K", non_negative=True)
        expected_energy = finite_number(case.get("landauer_energy_J"), f"temperature_cases[{index}].landauer_energy_J", non_negative=True)
        expected_mass = finite_number(case.get("conditional_mass_kg"), f"temperature_cases[{index}].conditional_mass_kg", non_negative=True)
        energy = landauer_scale(temperature)
        mass = conditional_bit_mass(temperature)
        require(relative_error(energy, expected_energy) <= tolerance, "energy fixture mismatch")
        require(relative_error(mass, expected_mass) <= tolerance, "mass fixture mismatch")
        temperature_results.append({
            "temperature_K": temperature,
            "landauer_scale_J": energy,
            "conditional_bit_mass_kg": mass,
        })

    storage = fixtures.get("storage_case")
    if not isinstance(storage, dict):
        raise TypeError("storage_case must be a JSON object")
    storage_bytes = non_negative_integer(storage.get("bytes"), "storage_case.bytes")
    storage_bits = non_negative_integer(storage.get("bits"), "storage_case.bits")
    storage_temperature = finite_number(storage.get("temperature_K"), "storage_case.temperature_K", non_negative=True)
    expected_storage_mass = finite_number(
        storage.get("expected_conditional_mass_kg"),
        "storage_case.expected_conditional_mass_kg",
        non_negative=True,
    )
    source_storage_mass = finite_number(
        storage.get("source_reported_mass_kg"),
        "storage_case.source_reported_mass_kg",
        non_negative=True,
    )
    storage_observed = storage_mass(storage_bits, storage_temperature)
    require(relative_error(storage_observed, expected_storage_mass) <= tolerance, "storage fixture mismatch")

    source_reported = fixtures.get("source_reported")
    if not isinstance(source_reported, dict):
        raise TypeError("source_reported must be a JSON object")
    cmb_temperature = finite_number(source_reported.get("cmb_temperature_K"), "source_reported.cmb_temperature_K", non_negative=True)
    room_expected = finite_number(source_reported.get("room_temperature_bit_mass_kg"), "source_reported.room_temperature_bit_mass_kg", non_negative=True)
    cmb_expected = finite_number(source_reported.get("cmb_bit_mass_kg"), "source_reported.cmb_bit_mass_kg", non_negative=True)

    room_mass = conditional_bit_mass(300.0)
    cmb_mass = conditional_bit_mass(cmb_temperature)
    require(relative_error(room_mass, room_expected) <= source_rounding_tolerance, "source room-temperature rounded value not reproduced")
    require(relative_error(cmb_mass, cmb_expected) <= source_rounding_tolerance, "source 2.73 K rounded value not reproduced")
    require(relative_error(storage_observed, source_storage_mass) <= source_rounding_tolerance, "source 1 TB rounded mass-change value not reproduced")

    return {
        "type": "uft-id-vopson-2019-mei-reproduction",
        "schema_version": "1.0.0",
        "source_work_id": "VOP-2019-MEI",
        "source_doi": "10.1063/1.5123794",
        "equation_reproduced": "Eq. (6)",
        "constants": {
            "boltzmann_J_per_K": K_B,
            "speed_of_light_m_per_s": C,
            "constants_status": "exact SI defining constants",
        },
        "temperature_results": temperature_results,
        "storage_case": {
            "bytes": storage_bytes,
            "bits": storage_bits,
            "temperature_K": storage_temperature,
            "conditional_mass_kg": storage_observed,
            "source_reported_mass_kg": source_storage_mass,
        },
        "source_rounding_checks": {
            "room_temperature_300K": True,
            "cmb_temperature_2_73K": True,
            "storage_1TB_decimal": True,
        },
        "derivation_status": {
            "shannon_binary_entropy": "reproduced",
            "information_entropy_scale": "reproduced",
            "landauer_erasure_scale": "established_external_premise_with_scope",
            "stored_bit_energy_identification": "source_assumption_not_validated",
            "mass_conversion_given_energy_identification": "algebraically_reproduced",
            "storage_mass_prediction": "numerically_reproduced_conditional_on_source_assumption",
        },
        "source_text_audit": {
            "inequality_issue": "The p.2 prose around erasure heat contains an inequality direction inconsistent with the immediately preceding second-law balance and with the conventional lower-bound Landauer statement; Eq. (6) arithmetic is reproduced without silently repairing that prose."
        },
        "claim_boundary": "ARITHMETIC_REPRODUCED != PREMISE_VALIDATED != PHYSICAL_INTERPRETATION_VALIDATED != EXPERIMENTALLY_CONFIRMED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print("VOP-2019-MEI Eq. (6) arithmetic reproduced")
        print(f"300 K conditional bit mass: {conditional_bit_mass(300.0):.16e} kg")
        print(f"1 TB decimal conditional mass: {storage_mass(8_000_000_000_000, 300.0):.16e} kg")
        print(result["claim_boundary"])


if __name__ == "__main__":
    main()
