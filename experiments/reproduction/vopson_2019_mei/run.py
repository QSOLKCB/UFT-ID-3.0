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


def landauer_scale(temperature_K: float) -> float:
    if isinstance(temperature_K, bool) or not isinstance(temperature_K, (int, float)):
        raise TypeError("temperature_K must be a real number")
    if not math.isfinite(float(temperature_K)) or temperature_K < 0:
        raise ValueError("temperature_K must be finite and non-negative")
    return K_B * float(temperature_K) * math.log(2.0)


def conditional_bit_mass(temperature_K: float) -> float:
    """Eq. (6) arithmetic conditional on E_bit = k_B T ln 2."""
    return landauer_scale(temperature_K) / (C * C)


def storage_mass(bits: int, temperature_K: float) -> float:
    if isinstance(bits, bool) or not isinstance(bits, int) or bits < 0:
        raise ValueError("bits must be a non-negative integer")
    return bits * conditional_bit_mass(temperature_K)


def relative_error(observed: float, expected: float) -> float:
    if expected == 0:
        return 0.0 if observed == 0 else math.inf
    return abs(observed - expected) / abs(expected)


def run() -> dict[str, object]:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    require(fixtures["constants"]["boltzmann_J_per_K"] == K_B, "fixture k_B mismatch")
    require(fixtures["constants"]["speed_of_light_m_per_s"] == C, "fixture c mismatch")

    tolerance = float(fixtures["comparison_tolerances"]["relative"])
    source_rounding_tolerance = float(fixtures["comparison_tolerances"]["source_rounding_relative"])

    temperature_results = []
    for case in fixtures["temperature_cases"]:
        temperature = float(case["temperature_K"])
        energy = landauer_scale(temperature)
        mass = conditional_bit_mass(temperature)
        require(relative_error(energy, float(case["landauer_energy_J"])) <= tolerance, "energy fixture mismatch")
        require(relative_error(mass, float(case["conditional_mass_kg"])) <= tolerance, "mass fixture mismatch")
        temperature_results.append({
            "temperature_K": temperature,
            "landauer_scale_J": energy,
            "conditional_bit_mass_kg": mass,
        })

    storage = fixtures["storage_case"]
    storage_observed = storage_mass(int(storage["bits"]), float(storage["temperature_K"]))
    require(relative_error(storage_observed, float(storage["expected_conditional_mass_kg"])) <= tolerance, "storage fixture mismatch")

    room_mass = conditional_bit_mass(300.0)
    cmb_mass = conditional_bit_mass(float(fixtures["source_reported"]["cmb_temperature_K"]))
    require(relative_error(room_mass, float(fixtures["source_reported"]["room_temperature_bit_mass_kg"])) <= source_rounding_tolerance, "source room-temperature rounded value not reproduced")
    require(relative_error(cmb_mass, float(fixtures["source_reported"]["cmb_bit_mass_kg"])) <= source_rounding_tolerance, "source 2.73 K rounded value not reproduced")
    require(relative_error(storage_observed, float(storage["source_reported_mass_kg"])) <= source_rounding_tolerance, "source 1 TB rounded mass-change value not reproduced")

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
            "bytes": int(storage["bytes"]),
            "bits": int(storage["bits"]),
            "temperature_K": float(storage["temperature_K"]),
            "conditional_mass_kg": storage_observed,
            "source_reported_mass_kg": float(storage["source_reported_mass_kg"]),
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
