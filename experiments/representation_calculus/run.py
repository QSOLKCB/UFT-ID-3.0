#!/usr/bin/env python3
"""Exact finite conformance witnesses for planned PR #14 Representation Calculus."""
from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json
from typing import Iterable

Scalar = Fraction
Matrix2 = tuple[Scalar, Scalar, Scalar, Scalar]
Vector2 = tuple[Scalar, Scalar]

ALPHABET = (-1, 0, 1)


def F(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value, 1)


def matrix(values: Iterable[int | Fraction]) -> Matrix2:
    vals = tuple(F(v) for v in values)
    if len(vals) != 4:
        raise ValueError("2x2 matrix requires exactly four entries")
    return vals  # type: ignore[return-value]


def vector(values: Iterable[int | Fraction]) -> Vector2:
    vals = tuple(F(v) for v in values)
    if len(vals) != 2:
        raise ValueError("2-vector requires exactly two entries")
    return vals  # type: ignore[return-value]


def matmul(a: Matrix2, b: Matrix2) -> Matrix2:
    a00, a01, a10, a11 = a
    b00, b01, b10, b11 = b
    return (
        a00 * b00 + a01 * b10,
        a00 * b01 + a01 * b11,
        a10 * b00 + a11 * b10,
        a10 * b01 + a11 * b11,
    )


def matvec(a: Matrix2, v: Vector2) -> Vector2:
    a00, a01, a10, a11 = a
    x, y = v
    return (a00 * x + a01 * y, a10 * x + a11 * y)


def transpose(a: Matrix2) -> Matrix2:
    a00, a01, a10, a11 = a
    return (a00, a10, a01, a11)


def trace(a: Matrix2) -> Fraction:
    return a[0] + a[3]


def det(a: Matrix2) -> Fraction:
    return a[0] * a[3] - a[1] * a[2]


def inverse(a: Matrix2) -> Matrix2:
    d = det(a)
    if d == 0:
        raise ValueError("matrix must be invertible")
    a00, a01, a10, a11 = a
    return (a11 / d, -a01 / d, -a10 / d, a00 / d)


def sub_scalar_identity(a: Matrix2, scalar: int | Fraction) -> Matrix2:
    s = F(scalar)
    return (a[0] - s, a[1], a[2], a[3] - s)


def rank(a: Matrix2) -> int:
    if all(value == 0 for value in a):
        return 0
    return 2 if det(a) != 0 else 1


def frobenius_sq(a: Matrix2) -> Fraction:
    return sum((value * value for value in a), Fraction(0, 1))


def is_symmetric(a: Matrix2) -> bool:
    return a[1] == a[2]


def identity() -> Matrix2:
    return matrix((1, 0, 0, 1))


def similarity(a: Matrix2, p: Matrix2) -> Matrix2:
    return matmul(matmul(inverse(p), a), p)


def congruence(a: Matrix2, p: Matrix2) -> Matrix2:
    return matmul(matmul(transpose(p), a), p)


def is_orthogonal(p: Matrix2) -> bool:
    return matmul(transpose(p), p) == identity()


def all_small_matrices() -> tuple[Matrix2, ...]:
    return tuple(matrix(entries) for entries in itertools.product(ALPHABET, repeat=4))


def unimodular_transforms() -> tuple[Matrix2, ...]:
    return tuple(a for a in all_small_matrices() if abs(det(a)) == 1)


def orthogonal_transforms() -> tuple[Matrix2, ...]:
    return tuple(a for a in unimodular_transforms() if is_orthogonal(a))


def all_small_vectors() -> tuple[Vector2, ...]:
    return tuple(vector(entries) for entries in itertools.product(ALPHABET, repeat=2))


def matrix_battery() -> dict[str, int]:
    matrices = all_small_matrices()
    transforms = unimodular_transforms()
    orthogonal = orthogonal_transforms()
    vectors = all_small_vectors()
    if len(matrices) != 81:
        raise RuntimeError("small matrix count drift")
    if len(transforms) != 40:
        raise RuntimeError("unimodular transform count drift")
    if len(orthogonal) != 8:
        raise RuntimeError("orthogonal transform count drift")
    if len(vectors) != 9:
        raise RuntimeError("small vector count drift")

    similarity_checks = 0
    congruence_checks = 0
    orthogonal_checks = 0
    coordinate_checks = 0

    for a in matrices:
        for p in transforms:
            b = similarity(a, p)
            if trace(b) != trace(a) or det(b) != det(a) or rank(b) != rank(a):
                raise RuntimeError("UFT-REP-001 finite similarity invariant failure")
            similarity_checks += 1

            c = congruence(a, p)
            if rank(c) != rank(a):
                raise RuntimeError("UFT-REP-003 finite congruence rank failure")
            if is_symmetric(a) and not is_symmetric(c):
                raise RuntimeError("UFT-REP-003 symmetry preservation failure")
            congruence_checks += 1

            p_inv = inverse(p)
            a_prime = similarity(a, p)
            for v in vectors:
                v_prime = matvec(p_inv, v)
                left = matvec(a_prime, v_prime)
                right = matvec(p_inv, matvec(a, v))
                if left != right:
                    raise RuntimeError("UFT-REP-004 coordinate covariance failure")
                coordinate_checks += 1

        for q in orthogonal:
            b = similarity(a, q)
            if frobenius_sq(b) != frobenius_sq(a):
                raise RuntimeError("UFT-REP-002 orthogonal Frobenius failure")
            orthogonal_checks += 1

    expected = {
        "matrix_count": 81,
        "unimodular_transform_count": 40,
        "orthogonal_transform_count": 8,
        "similarity_checks": 3240,
        "congruence_rank_checks": 3240,
        "orthogonal_frobenius_checks": 648,
        "coordinate_covariance_checks": 29160,
    }
    actual = {
        "matrix_count": len(matrices),
        "unimodular_transform_count": len(transforms),
        "orthogonal_transform_count": len(orthogonal),
        "similarity_checks": similarity_checks,
        "congruence_rank_checks": congruence_checks,
        "orthogonal_frobenius_checks": orthogonal_checks,
        "coordinate_covariance_checks": coordinate_checks,
    }
    if actual != expected:
        raise RuntimeError(f"matrix battery count drift: {actual}")
    return actual


def fin3_functions() -> tuple[tuple[int, int, int], ...]:
    return tuple(itertools.product(range(3), repeat=3))


def receiver_injective_on_image(observation: tuple[int, int, int], receiver: tuple[int, int, int]) -> bool:
    image = set(observation)
    encoded = [receiver[y] for y in image]
    return len(encoded) == len(set(encoded))


def receiver_battery() -> dict[str, int]:
    functions = fin3_functions()
    if len(functions) != 27:
        raise RuntimeError("Fin3 function count drift")
    function_pairs = 0
    injective_pairs = 0
    source_pair_checks = 0
    for observation in functions:
        for receiver in functions:
            function_pairs += 1
            if not receiver_injective_on_image(observation, receiver):
                continue
            injective_pairs += 1
            for x in range(3):
                for y in range(3):
                    before = observation[x] == observation[y]
                    after = receiver[observation[x]] == receiver[observation[y]]
                    if before != after:
                        raise RuntimeError("UFT-REP-005 receiver equivalence failure")
                    source_pair_checks += 1
    result = {
        "fin3_function_count": len(functions),
        "receiver_function_pairs": function_pairs,
        "injective_on_image_receiver_pairs": injective_pairs,
        "receiver_equivalence_pair_checks": source_pair_checks,
    }
    expected = {
        "fin3_function_count": 27,
        "receiver_function_pairs": 729,
        "injective_on_image_receiver_pairs": 441,
        "receiver_equivalence_pair_checks": 3969,
    }
    if result != expected:
        raise RuntimeError(f"receiver battery count drift: {result}")
    return result


def fixtures() -> dict[str, object]:
    i2 = identity()
    p_scale = matrix((2, 0, 0, 1))
    c = congruence(i2, p_scale)
    cx1 = {
        "congruent": c == matrix((4, 0, 0, 1)),
        "trace_differs": trace(i2) != trace(c),
        "similar": trace(i2) == trace(c) and det(i2) == det(c),
    }

    a = matrix((1, 0, 0, 2))
    shear = matrix((1, 1, 0, 1))
    b = similarity(a, shear)
    cx2 = {
        "similar": trace(a) == trace(b) and det(a) == det(b),
        "similarity_result": [str(x) for x in b],
        "frobenius_sq_source": str(frobenius_sq(a)),
        "frobenius_sq_target": str(frobenius_sq(b)),
        "orthogonally_similar_possible": frobenius_sq(a) == frobenius_sq(b),
    }

    jordan = matrix((1, 1, 0, 1))
    cx3 = {
        "same_characteristic_polynomial": trace(i2) == trace(jordan) and det(i2) == det(jordan),
        "rank_A_minus_I": rank(sub_scalar_identity(i2, 1)),
        "rank_B_minus_I": rank(sub_scalar_identity(jordan, 1)),
        "similar": rank(sub_scalar_identity(i2, 1)) == rank(sub_scalar_identity(jordan, 1)),
    }

    observation = (0, 1, 1)
    receiver = (0, 0, 2)
    cx4 = {
        "before_equal_x0_x1": observation[0] == observation[1],
        "after_equal_x0_x1": receiver[observation[0]] == receiver[observation[1]],
        "receiver_injective_on_image": receiver_injective_on_image(observation, receiver),
    }

    cx5 = {
        "coordinate_tuple": [1, 0],
        "standard_basis_vector": [1, 0],
        "swapped_basis_vector": [0, 1],
        "same_abstract_vector": False,
    }

    if not (cx1["congruent"] and cx1["trace_differs"] and not cx1["similar"]):
        raise RuntimeError("CX-REP-001 fixture drift")
    if not (cx2["similar"] and not cx2["orthogonally_similar_possible"]):
        raise RuntimeError("CX-REP-002 fixture drift")
    if not (cx3["same_characteristic_polynomial"] and not cx3["similar"]):
        raise RuntimeError("CX-REP-003 fixture drift")
    if cx4["before_equal_x0_x1"] or not cx4["after_equal_x0_x1"] or cx4["receiver_injective_on_image"]:
        raise RuntimeError("CX-REP-004 fixture drift")
    if cx5["same_abstract_vector"]:
        raise RuntimeError("CX-REP-005 fixture drift")

    return {
        "CX-REP-001": cx1,
        "CX-REP-002": cx2,
        "CX-REP-003": cx3,
        "CX-REP-004": cx4,
        "CX-REP-005": cx5,
    }


def run_suite() -> dict[str, object]:
    return {
        "type": "uft-id-representation-finite-conformance",
        "schema_version": "1.0.0",
        "bounded_checks": {
            "matrices": matrix_battery(),
            "receivers": receiver_battery(),
        },
        "fixtures": fixtures(),
        "claim_boundary": (
            "FINITE_REPRESENTATION_CONFORMANCE != GENERAL_PROOF; "
            "SIMILARITY != CONGRUENCE; REPRESENTATION_CHANGE != PHYSICAL_CHANGE"
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
        print("Representation calculus finite conformance: ok")
        print("similarity checks:", result["bounded_checks"]["matrices"]["similarity_checks"])
        print("coordinate covariance checks:", result["bounded_checks"]["matrices"]["coordinate_covariance_checks"])
        print("receiver equivalence checks:", result["bounded_checks"]["receivers"]["receiver_equivalence_pair_checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
