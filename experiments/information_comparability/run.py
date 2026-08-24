#!/usr/bin/env python3
"""Exact finite conformance witnesses for planned PR #15 Information Comparability."""
from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json

FUNCTIONALS = ("shannon_entropy", "hartley_entropy")
OBSERVATIONS = ("fine-observation", "coarse-observation")
UNITS = ("bit", "base4-digit")
NORMALIZATIONS = ("none", "per-source-symbol")
CONDITIONINGS = ("unconditional", "conditioned-on-k")
SCOPES = (
    frozenset({"alpha"}),
    frozenset({"beta"}),
    frozenset({"alpha", "beta"}),
)
SOURCE_TYPE = "Fin2"
UNIT_SCALES = {
    ("bit", "base4-digit"): Fraction(1, 2),
    ("base4-digit", "bit"): Fraction(2, 1),
}


def _as_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _as_scope(values: object, label: str = "scope") -> frozenset[str]:
    try:
        scope = frozenset(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ValueError(f"{label} must be an iterable of nonempty strings") from exc
    if not scope or any(not isinstance(item, str) or not item for item in scope):
        raise ValueError(f"{label} must contain nonempty strings")
    return scope


def make_spec(
    *,
    source_type: str = SOURCE_TYPE,
    functional: str,
    observation: str,
    unit: str,
    normalization: str,
    conditioning: str,
    scope: object,
) -> dict[str, object]:
    source_type = _as_nonempty_string(source_type, "source_type")
    functional = _as_nonempty_string(functional, "functional")
    observation = _as_nonempty_string(observation, "observation")
    unit = _as_nonempty_string(unit, "unit")
    normalization = _as_nonempty_string(normalization, "normalization")
    conditioning = _as_nonempty_string(conditioning, "conditioning")
    if functional not in FUNCTIONALS:
        raise ValueError("unsupported information functional")
    if observation not in OBSERVATIONS:
        raise ValueError("unsupported observation contract")
    if unit not in UNITS:
        raise ValueError("unsupported information unit")
    if normalization not in NORMALIZATIONS:
        raise ValueError("unsupported normalization convention")
    if conditioning not in CONDITIONINGS:
        raise ValueError("unsupported conditioning convention")
    return {
        "source_type": source_type,
        "functional": functional,
        "observation": observation,
        "unit": unit,
        "normalization": normalization,
        "conditioning": conditioning,
        "scope": _as_scope(scope),
    }


def validate_spec(spec: object) -> dict[str, object]:
    if not isinstance(spec, dict):
        raise ValueError("InformationSpec must be an object")
    expected = {
        "source_type", "functional", "observation", "unit",
        "normalization", "conditioning", "scope",
    }
    if set(spec) != expected:
        raise ValueError("InformationSpec field set drift")
    return make_spec(
        source_type=spec["source_type"],  # type: ignore[arg-type]
        functional=spec["functional"],  # type: ignore[arg-type]
        observation=spec["observation"],  # type: ignore[arg-type]
        unit=spec["unit"],  # type: ignore[arg-type]
        normalization=spec["normalization"],  # type: ignore[arg-type]
        conditioning=spec["conditioning"],  # type: ignore[arg-type]
        scope=spec["scope"],
    )


def semantic_key(spec: dict[str, object], *, include_unit: bool = True) -> tuple[object, ...]:
    validated = validate_spec(spec)
    fields = [
        validated["source_type"],
        validated["functional"],
        validated["observation"],
    ]
    if include_unit:
        fields.append(validated["unit"])
    fields.extend((validated["normalization"], validated["conditioning"]))
    return tuple(fields)


def directly_comparable(left: object, right: object) -> bool:
    a = validate_spec(left)
    b = validate_spec(right)
    return semantic_key(a) == semantic_key(b) and bool(a["scope"] & b["scope"])  # type: ignore[operator]


def make_unit_conversion(
    *,
    functional: str,
    source_unit: str,
    target_unit: str,
    scope: object,
) -> dict[str, object]:
    functional = _as_nonempty_string(functional, "functional")
    source_unit = _as_nonempty_string(source_unit, "source_unit")
    target_unit = _as_nonempty_string(target_unit, "target_unit")
    if functional not in FUNCTIONALS:
        raise ValueError("unsupported conversion functional")
    pair = (source_unit, target_unit)
    if pair not in UNIT_SCALES:
        raise ValueError("unregistered unit conversion")
    return {
        "functional": functional,
        "source_unit": source_unit,
        "target_unit": target_unit,
        "positive_scale": UNIT_SCALES[pair],
        "scope": _as_scope(scope, "conversion scope"),
    }


def validate_unit_conversion(conversion: object) -> dict[str, object]:
    if not isinstance(conversion, dict):
        raise ValueError("UnitConversion must be an object")
    expected = {"functional", "source_unit", "target_unit", "positive_scale", "scope"}
    if set(conversion) != expected:
        raise ValueError("UnitConversion field set drift")
    canonical = make_unit_conversion(
        functional=conversion["functional"],  # type: ignore[arg-type]
        source_unit=conversion["source_unit"],  # type: ignore[arg-type]
        target_unit=conversion["target_unit"],  # type: ignore[arg-type]
        scope=conversion["scope"],
    )
    if conversion["positive_scale"] != canonical["positive_scale"]:
        raise ValueError("unit conversion scale is not registry-canonical")
    return canonical


def unit_convertibly_comparable(left: object, right: object, conversion: object) -> bool:
    a = validate_spec(left)
    b = validate_spec(right)
    c = validate_unit_conversion(conversion)
    if a["unit"] == b["unit"]:
        return False
    if semantic_key(a, include_unit=False) != semantic_key(b, include_unit=False):
        return False
    if c["functional"] != a["functional"] or c["functional"] != b["functional"]:
        return False
    if c["source_unit"] != a["unit"] or c["target_unit"] != b["unit"]:
        return False
    overlap = a["scope"] & b["scope"] & c["scope"]  # type: ignore[operator]
    return bool(overlap)


def comparable(left: object, right: object, conversion: object | None = None) -> bool:
    if directly_comparable(left, right):
        return True
    if conversion is None:
        return False
    return unit_convertibly_comparable(left, right, conversion)


def convert_value(value: int | Fraction, conversion: object) -> Fraction:
    c = validate_unit_conversion(conversion)
    return Fraction(value) * c["positive_scale"]  # type: ignore[arg-type]


def all_specs() -> tuple[dict[str, object], ...]:
    specs: list[dict[str, object]] = []
    for functional, observation, unit, normalization, conditioning, scope in itertools.product(
        FUNCTIONALS, OBSERVATIONS, UNITS, NORMALIZATIONS, CONDITIONINGS, SCOPES
    ):
        specs.append(make_spec(
            functional=functional,
            observation=observation,
            unit=unit,
            normalization=normalization,
            conditioning=conditioning,
            scope=scope,
        ))
    return tuple(specs)


def comparability_battery() -> dict[str, int]:
    specs = all_specs()
    if len(specs) != 96:
        raise RuntimeError("InformationSpec count drift")
    ordered_pairs = 0
    direct_pairs = 0
    conversion_pairs = 0
    reflexive_checks = 0
    symmetry_checks = 0
    inverse_conversion_checks = 0

    full_scope = frozenset({"alpha", "beta"})
    for a in specs:
        if not directly_comparable(a, a):
            raise RuntimeError("UFT-INF-001 reflexivity failure")
        reflexive_checks += 1
        for b in specs:
            ordered_pairs += 1
            ab = directly_comparable(a, b)
            ba = directly_comparable(b, a)
            if ab != ba:
                raise RuntimeError("UFT-INF-002 symmetry failure")
            symmetry_checks += 1
            if ab:
                direct_pairs += 1
                for field in ("source_type", "functional", "observation", "unit", "normalization", "conditioning"):
                    if a[field] != b[field]:
                        raise RuntimeError("UFT-INF-003 direct-comparability field mismatch")
                if not (a["scope"] & b["scope"]):  # type: ignore[operator]
                    raise RuntimeError("UFT-INF-003 direct-comparability scope mismatch")
            if a["unit"] != b["unit"] and semantic_key(a, include_unit=False) == semantic_key(b, include_unit=False):
                forward = make_unit_conversion(
                    functional=str(a["functional"]),
                    source_unit=str(a["unit"]),
                    target_unit=str(b["unit"]),
                    scope=full_scope,
                )
                if unit_convertibly_comparable(a, b, forward):
                    conversion_pairs += 1
                    reverse = make_unit_conversion(
                        functional=str(b["functional"]),
                        source_unit=str(b["unit"]),
                        target_unit=str(a["unit"]),
                        scope=full_scope,
                    )
                    if not unit_convertibly_comparable(b, a, reverse):
                        raise RuntimeError("unit-conversion inverse comparability failure")
                    inverse_conversion_checks += 1

    result = {
        "information_spec_count": len(specs),
        "ordered_spec_pair_count": ordered_pairs,
        "directly_comparable_ordered_pairs": direct_pairs,
        "unit_convertible_ordered_pairs": conversion_pairs,
        "reflexive_checks": reflexive_checks,
        "symmetry_checks": symmetry_checks,
        "inverse_conversion_checks": inverse_conversion_checks,
    }
    expected = {
        "information_spec_count": 96,
        "ordered_spec_pair_count": 9216,
        "directly_comparable_ordered_pairs": 224,
        "unit_convertible_ordered_pairs": 224,
        "reflexive_checks": 96,
        "symmetry_checks": 9216,
        "inverse_conversion_checks": 224,
    }
    if result != expected:
        raise RuntimeError(f"comparability battery count drift: {result}")
    return result


def sign(value: Fraction) -> int:
    return 0 if value == 0 else (1 if value > 0 else -1)


def positive_scale_battery() -> dict[str, int]:
    values = tuple(Fraction(v, 1) for v in (-2, -1, 0, 1, 2))
    scales = (Fraction(1, 2), Fraction(2, 1), Fraction(3, 1))
    checks = 0
    for x, y, scale in itertools.product(values, values, scales):
        if scale <= 0:
            raise RuntimeError("positive-scale fixture drift")
        before = y - x
        after = scale * y - scale * x
        if (x == y) != (scale * x == scale * y):
            raise RuntimeError("UFT-INF-004 equality preservation failure")
        if (x < y) != (scale * x < scale * y):
            raise RuntimeError("UFT-INF-004 strict-order preservation failure")
        if sign(before) != sign(after):
            raise RuntimeError("UFT-INF-004 difference-sign preservation failure")
        checks += 1
    if checks != 75:
        raise RuntimeError("positive-scale battery count drift")
    return {"positive_scale_order_checks": checks}


def exact_log2_power_of_two(cardinality: int) -> int:
    if isinstance(cardinality, bool) or not isinstance(cardinality, int) or cardinality < 1:
        raise ValueError("cardinality must be a positive integer")
    if cardinality & (cardinality - 1):
        raise ValueError("bounded exact logarithm requires a power-of-two cardinality")
    return cardinality.bit_length() - 1


def uniform_log_entropy(cardinality: int, unit: str) -> Fraction:
    exponent = exact_log2_power_of_two(cardinality)
    if unit == "bit":
        return Fraction(exponent, 1)
    if unit == "base4-digit":
        return Fraction(exponent, 2)
    raise ValueError("unsupported uniform entropy unit")


def log_base_conversion_battery() -> dict[str, int]:
    checks = 0
    for cardinality in (1, 2, 4, 8, 16):
        bits = uniform_log_entropy(cardinality, "bit")
        base4 = uniform_log_entropy(cardinality, "base4-digit")
        if bits != 2 * base4:
            raise RuntimeError("UFT-INF-005 logarithm-base conversion failure")
        checks += 1
    if checks != 5:
        raise RuntimeError("log-base conversion count drift")
    return {"log_base_conversion_checks": checks}


def fixture_spec(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_type": SOURCE_TYPE,
        "functional": "shannon_entropy",
        "observation": "fine-observation",
        "unit": "bit",
        "normalization": "none",
        "conditioning": "unconditional",
        "scope": frozenset({"alpha", "beta"}),
    }
    payload.update(overrides)
    return validate_spec(payload)


def fixtures() -> dict[str, object]:
    shannon = fixture_spec(functional="shannon_entropy", scope=frozenset({"alpha"}))
    hartley = fixture_spec(functional="hartley_entropy", scope=frozenset({"alpha"}))
    cx1 = {
        "shared_word": "information",
        "same_unit": shannon["unit"] == hartley["unit"],
        "shannon_uniform_two_value": "1",
        "hartley_uniform_two_value": "1",
        "numeric_values_equal": True,
        "directly_comparable": directly_comparable(shannon, hartley),
    }

    fine = fixture_spec(observation="fine-observation", scope=frozenset({"alpha"}))
    coarse = fixture_spec(observation="coarse-observation", scope=frozenset({"alpha"}))
    cx2 = {
        "same_functional": fine["functional"] == coarse["functional"],
        "same_unit": fine["unit"] == coarse["unit"],
        "same_observation": fine["observation"] == coarse["observation"],
        "directly_comparable": directly_comparable(fine, coarse),
    }

    bits = fixture_spec(unit="bit", scope=frozenset({"alpha"}))
    base4 = fixture_spec(unit="base4-digit", scope=frozenset({"alpha"}))
    conversion = make_unit_conversion(
        functional="shannon_entropy",
        source_unit="bit",
        target_unit="base4-digit",
        scope=frozenset({"alpha"}),
    )
    cx3 = {
        "directly_comparable": directly_comparable(bits, base4),
        "unit_convertibly_comparable": unit_convertibly_comparable(bits, base4, conversion),
        "two_bits_in_base4_digits": str(convert_value(Fraction(2, 1), conversion)),
    }

    a = fixture_spec(scope=frozenset({"alpha"}))
    b = fixture_spec(scope=frozenset({"alpha", "beta"}))
    c = fixture_spec(scope=frozenset({"beta"}))
    cx4 = {
        "A_comparable_B": directly_comparable(a, b),
        "B_comparable_C": directly_comparable(b, c),
        "A_comparable_C": directly_comparable(a, c),
    }

    raw = fixture_spec(normalization="none", scope=frozenset({"alpha"}))
    normalized = fixture_spec(normalization="per-source-symbol", scope=frozenset({"alpha"}))
    cx5 = {
        "left_value": "1",
        "right_value": "1",
        "numeric_values_equal": Fraction(1, 1) == Fraction(1, 1),
        "same_normalization": raw["normalization"] == normalized["normalization"],
        "directly_comparable": directly_comparable(raw, normalized),
    }

    if not (cx1["same_unit"] and cx1["numeric_values_equal"] and not cx1["directly_comparable"]):
        raise RuntimeError("CX-INF-001 fixture drift")
    if not (cx2["same_functional"] and cx2["same_unit"] and not cx2["same_observation"] and not cx2["directly_comparable"]):
        raise RuntimeError("CX-INF-002 fixture drift")
    if cx3["directly_comparable"] or not cx3["unit_convertibly_comparable"] or cx3["two_bits_in_base4_digits"] != "1":
        raise RuntimeError("CX-INF-003 fixture drift")
    if not (cx4["A_comparable_B"] and cx4["B_comparable_C"] and not cx4["A_comparable_C"]):
        raise RuntimeError("CX-INF-004 fixture drift")
    if not (cx5["numeric_values_equal"] and not cx5["same_normalization"] and not cx5["directly_comparable"]):
        raise RuntimeError("CX-INF-005 fixture drift")

    return {
        "CX-INF-001": cx1,
        "CX-INF-002": cx2,
        "CX-INF-003": cx3,
        "CX-INF-004": cx4,
        "CX-INF-005": cx5,
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-information-comparability-finite-conformance",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "comparability": comparability_battery(),
            "positive_scale": positive_scale_battery(),
            "log_base_conversion": log_base_conversion_battery(),
        },
        "fixtures": fixtures(),
        "claim_boundary": (
            "FINITE_INFORMATION_CONFORMANCE != GENERAL_INFORMATION_THEORY; "
            "NUMERIC_EQUALITY != INFORMATIONAL_EQUIVALENCE; COMPARABLE != IDENTICAL_SPEC"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_suite()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False, default=lambda x: str(x)))
    else:
        checks = result["bounded_checks"]
        print("Information Comparability finite conformance: ok")
        print("specs:", checks["comparability"]["information_spec_count"])
        print("ordered pairs:", checks["comparability"]["ordered_spec_pair_count"])
        print("directly comparable:", checks["comparability"]["directly_comparable_ordered_pairs"])
        print("unit convertible:", checks["comparability"]["unit_convertible_ordered_pairs"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
