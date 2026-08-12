from __future__ import annotations

import argparse
import copy
import functools
import json
import math
import sys
import time
from typing import Any, Callable

import numpy as np
import scipy

from stagee_models import (
    BATCH_VERSION,
    CG_DLMF_TABLE_SHA256,
    CONFIG_CASES,
    EDGE_VERSION,
    FILTER_VERSION,
    SCAN_MULTIPLIERS,
    SCAN_ROTATION_COUNTS,
    SCAN_SCALES,
    SCHEMA_VERSION,
    SEEDS,
    TIME_REVERSAL_VERSION,
    TIME_REVERSAL_PAIR_VERSION,
    array_summary,
    axis_angle_rotation,
    block_diagonal,
    canonical_json,
    cg_matrix,
    clebsch_gordan,
    coefficient_bridge,
    coefficient_bridge_payload_hash,
    coefficient_filter,
    coefficient_filter_payload_hash,
    complex_representation,
    complex_spherical_values,
    d_representation,
    edge_payload,
    fixed_hamiltonian,
    forbidden_external_objects,
    frame_tolerance,
    local_frame,
    make_config_case,
    make_graph,
    make_hamiltonian_edge,
    make_irrep_batch,
    make_message_provenance,
    make_scan_case,
    make_time_reversal_pair,
    masked_irrep_mse,
    message_layer,
    normalized_residual,
    orbital_time_reversal,
    padded_irrep_linear,
    pauli_matrices,
    real_representation,
    reference_cost,
    reference_equivariance,
    sha256_text,
    spin_time_reversal,
    su2_from_quaternion,
    time_reverse,
    time_reversal_payloads,
    tolerance,
    validate_case,
    validate_canonical_unit_quaternion,
    validate_hamiltonian_edge,
    validate_irrep_batch,
    validate_message_provenance,
    validate_rotation,
    validate_stf_basis,
    validate_time_reversal_pair,
    validate_unit_quaternion,
    zero_tolerance,
    _stf_basis,
)


def _capture_failure(name: str, operation: Callable[[], Any]) -> dict[str, str]:
    try:
        operation()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"name": name, "error_type": type(error).__name__, "message": str(error)}
    raise AssertionError(f"expected failure was accepted: {name}")


def _to_python(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _to_python(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, complex):
        return [float(value.real), float(value.imag)]
    if isinstance(value, dict):
        return {str(key): _to_python(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_python(item) for item in value]
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _config_dtype(case: dict[str, Any]) -> np.dtype:
    return np.dtype(case["dtype"])


def test_t_e01(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    tau = tolerance(dtype)
    max_orthogonality = 0.0
    max_determinant = 0.0
    max_inverse = 0.0
    max_group = 0.0
    rotations = case["rotations"]
    for rotation in rotations:
        evidence = validate_rotation(rotation)
        max_orthogonality = max(max_orthogonality, evidence["orthogonality_residual"])
        max_determinant = max(max_determinant, evidence["determinant_residual"])
        max_inverse = max(max_inverse, normalized_residual(np.linalg.inv(rotation), rotation.T))
    for index in range(min(max(0, len(rotations) - 1), 32)):
        product = rotations[index + 1] @ rotations[index]
        validate_rotation(product)
        sequential = rotations[index + 1] @ (rotations[index] @ np.asarray([0.3, -0.7, 1.1], dtype=dtype))
        max_group = max(max_group, normalized_residual(product @ np.asarray([0.3, -0.7, 1.1], dtype=dtype), sequential))

    accepted_rotation = np.diag(np.asarray([1.0 + 0.4 * tau, 1.0, 1.0], dtype=dtype))
    accepted_rotation_evidence = validate_rotation(accepted_rotation)
    accepted_quaternion = np.asarray([1.0 + 0.5 * tau, 0.0, 0.0, 0.0], dtype=dtype)
    accepted_quaternion_epsilon = validate_unit_quaternion(accepted_quaternion)
    canonical_quaternion = np.asarray([0.5, 0.5, 0.5, 0.5], dtype=dtype)
    validate_canonical_unit_quaternion(canonical_quaternion)
    failures = [
        _capture_failure(
            "rotation_above_threshold",
            lambda: validate_rotation(np.diag(np.asarray([1.0 + 2.0 * tau, 1.0, 1.0], dtype=dtype))),
        ),
        _capture_failure(
            "quaternion_above_threshold",
            lambda: validate_unit_quaternion(np.asarray([1.0 + 2.0 * tau, 0.0, 0.0, 0.0], dtype=dtype)),
        ),
        _capture_failure("reflection_not_so3", lambda: validate_rotation(np.diag(np.asarray([-1.0, 1.0, 1.0], dtype=dtype)))),
        _capture_failure("zero_quaternion", lambda: validate_unit_quaternion(np.zeros(4, dtype=dtype))),
        _capture_failure("quaternion_wrong_shape", lambda: validate_unit_quaternion(np.ones((1, 4), dtype=dtype))),
        _capture_failure("rotation_wrong_dtype", lambda: validate_rotation(np.eye(3, dtype=np.float16))),
        _capture_failure("rotation_nan", lambda: validate_rotation(np.asarray([[np.nan, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=dtype))),
        _capture_failure("rotation_infinity", lambda: validate_rotation(np.asarray([[np.inf, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=dtype))),
        _capture_failure("quaternion_nan", lambda: validate_unit_quaternion(np.asarray([np.nan, 0, 0, 1], dtype=dtype))),
        _capture_failure("quaternion_infinity", lambda: validate_unit_quaternion(np.asarray([np.inf, 0, 0, 1], dtype=dtype))),
        _capture_failure("quaternion_noncanonical_sign", lambda: validate_canonical_unit_quaternion(-canonical_quaternion)),
    ]
    r1 = axis_angle_rotation((1, 0, 0), 0.61, dtype)
    r2 = axis_angle_rotation((0, 1, 0), -0.43, dtype)
    group_fixture = np.asarray([0.3, -0.7, 1.1], dtype=dtype)
    wrong_composition_residual = normalized_residual((r1 @ r2) @ group_fixture, (r2 @ r1) @ group_fixture)
    passed = (
        max_orthogonality <= tau
        and max_determinant <= tau
        and max_inverse <= tau
        and max_group <= tau
        and len(failures) == 11
        and wrong_composition_residual >= 1.0e-4
    )
    return {
        "pass": passed,
        "sample_count": int(len(rotations)),
        "max_orthogonality_residual": max_orthogonality,
        "max_determinant_residual": max_determinant,
        "max_inverse_residual": max_inverse,
        "max_group_residual": max_group,
        "accepted_rotation_boundary": accepted_rotation_evidence,
        "accepted_quaternion_boundary": accepted_quaternion_epsilon,
        "canonical_quaternion": canonical_quaternion,
        "canonical_quaternion_sha256": sha256_text(canonical_json(canonical_quaternion.tolist())),
        "fault_residuals": {"wrong_composition_order": wrong_composition_residual},
        "captured_failures": failures,
        "threshold": tau,
    }


def test_t_e02(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    rotation = np.asarray([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=dtype)
    validate_rotation(rotation)
    u = np.asarray([1.0, 2.0, -1.0], dtype=dtype)
    v = np.asarray([2.0, -1.0, 3.0], dtype=dtype)
    tensor = np.asarray([[1.0, 0.2, -0.3], [0.2, 2.0, 0.4], [-0.3, 0.4, -1.0]], dtype=dtype)
    rotated_tensor = rotation @ tensor @ rotation.T
    scalar_residual = abs(float(np.dot(rotation @ u, rotation @ v) - np.dot(u, v)))
    distance_residual = abs(float(np.linalg.norm(rotation @ (u - v)) ** 2 - 26.0))
    tensor_trace_residual = abs(float(np.trace(rotated_tensor) - np.trace(tensor)))
    tensor_norm_residual = abs(float(np.linalg.norm(rotated_tensor) - np.linalg.norm(tensor)))

    old_coordinates = np.asarray([1.0, 0.0, 0.0], dtype=dtype)
    new_basis = rotation
    new_coordinates = rotation.T @ old_coordinates
    passive_reconstruction = normalized_residual(new_basis @ new_coordinates, old_coordinates)
    passive_as_active_failure = normalized_residual(rotation @ old_coordinates, rotation.T @ old_coordinates)

    reflection = np.diag(np.asarray([-1.0, 1.0, 1.0], dtype=dtype))
    axial = np.cross(u, v)
    axial_expected = float(np.linalg.det(reflection)) * reflection @ axial
    axial_from_inputs = np.cross(reflection @ u, reflection @ v)
    axial_residual = normalized_residual(axial_from_inputs, axial_expected)
    axial_as_polar_failure = normalized_residual(axial_from_inputs, reflection @ axial)
    only_left_tensor_failure = normalized_residual(rotation @ tensor, rotated_tensor)
    tau = tolerance(dtype)
    passed = max(
        scalar_residual,
        distance_residual,
        tensor_trace_residual,
        tensor_norm_residual,
        passive_reconstruction,
        axial_residual,
    ) <= tau and min(passive_as_active_failure, axial_as_polar_failure, only_left_tensor_failure) >= 1.0e-4
    return {
        "pass": passed,
        "scalar_residual": scalar_residual,
        "distance_squared": float(np.linalg.norm(u - v) ** 2),
        "distance_squared_residual": distance_residual,
        "tensor_trace_residual": tensor_trace_residual,
        "tensor_norm_residual": tensor_norm_residual,
        "passive_coordinates": new_coordinates.tolist(),
        "passive_reconstruction_residual": passive_reconstruction,
        "axial_residual": axial_residual,
        "fault_residuals": {
            "passive_used_as_active": passive_as_active_failure,
            "axial_used_as_polar": axial_as_polar_failure,
            "tensor_only_left": only_left_tensor_failure,
        },
        "threshold": tau,
    }


def test_t_e03(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    basis = _stf_basis(dtype)
    gram = np.einsum("aij,bij->ab", basis, basis)
    gram_error = float(np.linalg.norm(gram - np.eye(5, dtype=dtype)))
    trace_error = float(max(abs(np.trace(item)) for item in basis))
    symmetry_error = float(max(np.linalg.norm(item - item.T) for item in basis))
    max_p_orthogonality = 0.0
    max_d_orthogonality = 0.0
    max_d_group = 0.0
    rotations = case["rotations"]
    for rotation in rotations:
        d_matrix = d_representation(rotation)
        max_p_orthogonality = max(max_p_orthogonality, normalized_residual(rotation.T @ rotation, np.eye(3, dtype=dtype)))
        max_d_orthogonality = max(max_d_orthogonality, normalized_residual(d_matrix.T @ d_matrix, np.eye(5, dtype=dtype)))
    for index in range(min(max(0, len(rotations) - 1), 32)):
        left = d_representation(rotations[index + 1] @ rotations[index])
        right = d_representation(rotations[index + 1]) @ d_representation(rotations[index])
        max_d_group = max(max_d_group, normalized_residual(left, right))
    fixture = axis_angle_rotation((1, 2, 3), 0.7, dtype)
    correct = d_representation(fixture)
    wrong_basis_order = correct[[1, 0, 2, 3, 4]][:, [1, 0, 2, 3, 4]]
    wrong_order_residual = normalized_residual(wrong_basis_order, correct)
    wrong_direction = d_representation(fixture.T)
    wrong_direction_residual = normalized_residual(wrong_direction, correct)
    unnormalized_basis = np.array(basis, copy=True)
    unnormalized_basis[0] *= np.asarray(math.sqrt(2.0), dtype=dtype)
    normalization_failures = [
        _capture_failure("stf_missing_normalization", lambda: validate_stf_basis(unnormalized_basis))
    ]
    tau = tolerance(dtype)
    passed = max(gram_error, trace_error, symmetry_error, max_p_orthogonality, max_d_orthogonality, max_d_group) <= tau
    passed = passed and min(wrong_order_residual, wrong_direction_residual) >= 1.0e-4 and len(normalization_failures) == 1
    return {
        "pass": passed,
        "gram_error": gram_error,
        "trace_error": trace_error,
        "symmetry_error": symmetry_error,
        "max_p_orthogonality_residual": max_p_orthogonality,
        "max_d_orthogonality_residual": max_d_orthogonality,
        "max_d_group_residual": max_d_group,
        "fault_residuals": {"d_basis_order": wrong_order_residual, "RBR_direction": wrong_direction_residual},
        "captured_failures": normalization_failures,
        "threshold": tau,
    }


def test_t_e04(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    complex_dtype = np.complex64 if dtype == np.dtype(np.float32) else np.complex128
    direction = np.asarray([1.0, 2.0, 3.0], dtype=dtype)
    max_bridge_unitarity = 0.0
    max_similarity = 0.0
    max_point_value = 0.0
    max_coefficient = 0.0
    for ell in (1, 2):
        bridge = coefficient_bridge(ell, dtype)
        max_bridge_unitarity = max(
            max_bridge_unitarity,
            normalized_residual(bridge @ bridge.conj().T, np.eye(2 * ell + 1, dtype=complex_dtype)),
        )
        for rotation in case["rotations"]:
            complex_d = complex_representation(rotation, ell)
            route = bridge @ real_representation(rotation, ell) @ bridge.conj().T
            max_similarity = max(max_similarity, normalized_residual(complex_d, route))
            point_before = complex_spherical_values(direction, ell).astype(complex_dtype)
            point_after = complex_spherical_values(rotation @ direction, ell).astype(complex_dtype)
            max_point_value = max(max_point_value, normalized_residual(point_after, complex_d.conj() @ point_before))
            coefficient_before = point_before.conj()
            coefficient_after = point_after.conj()
            max_coefficient = max(max_coefficient, normalized_residual(coefficient_after, complex_d @ coefficient_before))
    fixture = axis_angle_rotation((2, -1, 1), 0.73, dtype)
    d1 = complex_representation(fixture, 1)
    point = complex_spherical_values(direction, 1).astype(complex_dtype)
    rotated_point = complex_spherical_values(fixture @ direction, 1).astype(complex_dtype)
    point_as_coefficient_failure = normalized_residual(rotated_point, d1 @ point)
    reverse_m_failure = normalized_residual(rotated_point[::-1], d1 @ point[::-1])
    fixed_bridge = coefficient_bridge(1, dtype)
    local_phase_bridge = np.array(fixed_bridge, copy=True)
    local_phase_bridge[0] *= -1
    local_phase_failure = normalized_residual(
        local_phase_bridge @ fixture @ local_phase_bridge.conj().T,
        d1,
    )
    interface_failures = [
        _capture_failure(
            "euler_angles_used_as_rotation_matrix",
            lambda: complex_representation(np.asarray([0.1, 0.2, 0.3], dtype=dtype), 1),
        )
    ]
    tau = tolerance(dtype)
    passed = max(max_bridge_unitarity, max_similarity, max_point_value, max_coefficient) <= tau
    passed = passed and min(point_as_coefficient_failure, reverse_m_failure, local_phase_failure) >= 1.0e-4
    passed = passed and len(interface_failures) == 1
    return {
        "pass": passed,
        "max_bridge_unitarity_residual": max_bridge_unitarity,
        "max_similarity_residual": max_similarity,
        "max_point_value_residual": max_point_value,
        "max_coefficient_residual": max_coefficient,
        "fault_residuals": {
            "point_value_used_as_coefficient": point_as_coefficient_failure,
            "m_order_reversed": reverse_m_failure,
            "condon_shortley_local_phase": local_phase_failure,
        },
        "captured_failures": interface_failures,
        "K1_payload_sha256": coefficient_bridge_payload_hash(1),
        "K2_payload_sha256": coefficient_bridge_payload_hash(2),
        "threshold": tau,
    }


def _coupled_output_representation(rotation: np.ndarray, j1: int, j2: int) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int]]]:
    matrix, outputs, _ = cg_matrix(j1, j2)
    input_representation = np.kron(complex_representation(rotation, j1), complex_representation(rotation, j2))
    output_representation = matrix.astype(input_representation.dtype) @ input_representation @ matrix.T.astype(input_representation.dtype)
    return matrix, output_representation, outputs


def test_t_e05(case: dict[str, Any]) -> dict[str, Any]:
    c11, outputs11, inputs11 = cg_matrix(1, 1)
    c12, outputs12, inputs12 = cg_matrix(1, 2)
    orth11 = float(np.linalg.norm(c11 @ c11.T - np.eye(9)))
    complete11 = float(np.linalg.norm(c11.T @ c11 - np.eye(9)))
    orth12 = float(np.linalg.norm(c12 @ c12.T - np.eye(15)))
    complete12 = float(np.linalg.norm(c12.T @ c12 - np.eye(15)))
    anchors11 = {
        "L0": clebsch_gordan(1, 1, 1, -1, 0, 0),
        "L1": clebsch_gordan(1, 1, 1, 0, 1, 1),
        "L2": clebsch_gordan(1, 1, 1, 1, 2, 2),
    }
    anchors12 = {
        "L1_m-1_2": clebsch_gordan(1, -1, 2, 2, 1, 1),
        "L1_m0_1": clebsch_gordan(1, 0, 2, 1, 1, 1),
        "L1_m1_0": clebsch_gordan(1, 1, 2, 0, 1, 1),
        "L2_m0_2": clebsch_gordan(1, 0, 2, 2, 2, 2),
        "L2_m1_1": clebsch_gordan(1, 1, 2, 1, 2, 2),
        "L3_m1_2": clebsch_gordan(1, 1, 2, 2, 3, 3),
    }
    max_intertwiner11 = 0.0
    max_intertwiner12 = 0.0
    max_off_block12 = 0.0
    for rotation in case["rotations"][: min(16, len(case["rotations"]))]:
        for j1, j2, matrix, outputs, field in (
            (1, 1, c11, outputs11, "11"),
            (1, 2, c12, outputs12, "12"),
        ):
            input_rep = np.kron(complex_representation(rotation, j1), complex_representation(rotation, j2))
            output_rep = matrix.astype(input_rep.dtype) @ input_rep @ matrix.T.astype(input_rep.dtype)
            residual = normalized_residual(matrix.astype(input_rep.dtype) @ input_rep, output_rep @ matrix.astype(input_rep.dtype))
            if field == "11":
                max_intertwiner11 = max(max_intertwiner11, residual)
            else:
                max_intertwiner12 = max(max_intertwiner12, residual)
                labels = [item[0] for item in outputs]
                off_block = np.array(output_rep, copy=True)
                for row, left_label in enumerate(labels):
                    for column, right_label in enumerate(labels):
                        if left_label == right_label:
                            off_block[row, column] = 0
                max_off_block12 = max(max_off_block12, float(np.linalg.norm(off_block)))
    fixture = axis_angle_rotation((1, 2, 3), 0.7, np.float64)
    input_rep = np.kron(complex_representation(fixture, 1), complex_representation(fixture, 1))
    output_rep = c11.astype(np.complex128) @ input_rep @ c11.T.astype(np.complex128)
    phase = np.ones(9)
    phase[[index for index, label in enumerate(outputs11) if label[0] == 0]] = -1
    channel_flip = np.diag(phase) @ c11
    channel_flip_residual = normalized_residual(
        channel_flip.astype(np.complex128) @ input_rep,
        output_rep @ channel_flip.astype(np.complex128),
    )
    partial = np.array(c11, copy=True)
    partial[next(index for index, label in enumerate(outputs11) if label == (1, -1))] *= -1
    partial_residual = normalized_residual(
        partial.astype(np.complex128) @ input_rep,
        output_rep @ partial.astype(np.complex128),
    )
    single = np.array(c11, copy=True)
    nonzero = np.argwhere(abs(single) > 0)[0]
    single[tuple(nonzero)] *= -1
    single_orthogonality_error = float(np.linalg.norm(single @ single.T - np.eye(9)))
    expected11 = (1 / math.sqrt(3), 1 / math.sqrt(2), 1.0)
    expected12 = (math.sqrt(3 / 5), -math.sqrt(3 / 10), 1 / math.sqrt(10), -math.sqrt(2 / 3), 1 / math.sqrt(3), 1.0)
    anchor_error = max(
        max(abs(value - expected) for value, expected in zip(anchors11.values(), expected11)),
        max(abs(value - expected) for value, expected in zip(anchors12.values(), expected12)),
    )
    canonical_table_sha256 = sha256_text(
        canonical_json(
            {
                "inputs11": inputs11,
                "outputs11": outputs11,
                "C11": c11.tolist(),
                "inputs12": inputs12,
                "outputs12": outputs12,
                "C12": c12.tolist(),
            }
        )
    )
    swap_without_exchange_phase = max(
        abs(
            clebsch_gordan(1, m1, 2, m2, total_j, total_m)
            - clebsch_gordan(2, m2, 1, m1, total_j, total_m)
        )
        for total_j in (1, 2, 3)
        for total_m in range(-total_j, total_j + 1)
        for m1 in range(-1, 2)
        for m2 in range(-2, 3)
        if m1 + m2 == total_m
    )
    tau = tolerance(case["dtype"])
    passed = max(orth11, complete11, orth12, complete12, max_intertwiner11, max_intertwiner12, max_off_block12, anchor_error, channel_flip_residual) <= tau
    passed = passed and canonical_table_sha256 == CG_DLMF_TABLE_SHA256
    passed = passed and min(partial_residual, single_orthogonality_error, swap_without_exchange_phase) >= 1.0e-4
    return {
        "pass": passed,
        "orthogonality_1x1": orth11,
        "completeness_1x1": complete11,
        "orthogonality_1x2": orth12,
        "completeness_1x2": complete12,
        "max_intertwiner_1x1": max_intertwiner11,
        "max_intertwiner_1x2": max_intertwiner12,
        "max_1x2_cross_L_block": max_off_block12,
        "anchors_1x1": anchors11,
        "anchors_1x2": anchors12,
        "anchor_max_error": anchor_error,
        "whole_channel_phase_intertwiner_residual": channel_flip_residual,
        "fault_residuals": {
            "partial_M_phase": partial_residual,
            "single_coefficient_orthogonality": single_orthogonality_error,
            "input_swap_without_exchange_phase": swap_without_exchange_phase,
        },
        "canonical_table_sha256": canonical_table_sha256,
        "frozen_DLMF_table_sha256": CG_DLMF_TABLE_SHA256,
        "threshold": tau,
    }


def test_t_e06(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    row = make_hamiltonian_edge(dtype)
    inverse_row = make_hamiltonian_edge(dtype, reverse=True)
    validate_hamiltonian_edge(row)
    validate_hamiltonian_edge(inverse_row)
    hamiltonian = row["block"]
    inverse_hamiltonian = inverse_row["block"]
    rotation = axis_angle_rotation((1, 2, 3), 0.7, dtype)
    receiver_rep = block_diagonal(np.ones((1, 1), dtype=dtype), rotation)
    sender_rep = block_diagonal(rotation, d_representation(rotation))
    transformed = receiver_rep @ hamiltonian @ sender_rep.T
    inverse_transformed = sender_rep @ inverse_hamiltonian @ receiver_rep.T
    inverse_pair_residual = normalized_residual(inverse_transformed, transformed.T)
    singular_value_residual = normalized_residual(np.linalg.svd(transformed, compute_uv=False), np.linalg.svd(hamiltonian, compute_uv=False))
    k_receiver = block_diagonal(np.ones((1, 1), dtype=np.complex128), coefficient_bridge(1, np.float64))
    k_sender = block_diagonal(coefficient_bridge(1, np.float64), coefficient_bridge(2, np.float64))
    h_complex = k_receiver @ hamiltonian.astype(np.float64) @ k_sender.conj().T
    d_receiver_complex = k_receiver @ receiver_rep.astype(np.float64) @ k_receiver.conj().T
    d_sender_complex = k_sender @ sender_rep.astype(np.float64) @ k_sender.conj().T
    complex_transformed = d_receiver_complex @ h_complex @ d_sender_complex.conj().T
    real_to_complex = k_receiver @ transformed.astype(np.float64) @ k_sender.conj().T
    basis_route_residual = normalized_residual(complex_transformed, real_to_complex)
    faults = {
        "only_left": normalized_residual(receiver_rep @ hamiltonian, transformed),
        "only_right": normalized_residual(hamiltonian @ sender_rep.T, transformed),
        "right_without_transpose": normalized_residual(receiver_rep @ hamiltonian @ sender_rep, transformed),
        "complex_right_without_conjugate": normalized_residual(d_receiver_complex @ h_complex @ d_sender_complex.T, complex_transformed),
    }
    tau = tolerance(dtype)
    passed = max(inverse_pair_residual, singular_value_residual, basis_route_residual) <= tau
    passed = passed and min(faults.values()) >= 1.0e-4
    return {
        "pass": passed,
        "block_shape": list(hamiltonian.shape),
        "receiver_orbitals": row["receiver_orbitals"],
        "sender_orbitals": row["sender_orbitals"],
        "edge_id": row["edge_id"],
        "inverse_edge_id": inverse_row["edge_id"],
        "edge_endpoints": [row["receiver"], row["sender"]],
        "inverse_edge_endpoints": [inverse_row["receiver"], inverse_row["sender"]],
        "inverse_shift": list(inverse_row["shift"]),
        "inverse_pair_residual": inverse_pair_residual,
        "singular_value_residual": singular_value_residual,
        "real_complex_route_residual": basis_route_residual,
        "fault_residuals": faults,
        "threshold": tau,
    }


def test_t_e07(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    reflection = np.diag(np.asarray([-1.0, 1.0, 1.0], dtype=dtype))
    polar = np.asarray([0.3, -0.8, 1.2], dtype=dtype)
    axial = np.asarray([1.1, 0.2, -0.4], dtype=dtype)
    polar_expected = reflection @ polar
    axial_expected = float(np.linalg.det(reflection)) * reflection @ axial
    polar_residual = normalized_residual(reflection @ polar, polar_expected)
    axial_residual = normalized_residual(float(np.linalg.det(reflection)) * reflection @ axial, axial_expected)
    axial_as_polar = normalized_residual(reflection @ axial, axial_expected)
    input_parity = -1
    filter_parity = -1
    output_parity = input_parity * filter_parity
    even_gate_parity = output_parity * 1
    pseudo_gate_parity = output_parity * -1
    pseudo_scalar = 0.4
    mixed_gate_inverted = 1.0 - pseudo_scalar
    definite_even_candidate = 1.0 + pseudo_scalar
    mixed_gate_failure = abs(mixed_gate_inverted - definite_even_candidate)
    passed = polar_residual <= tolerance(dtype) and axial_residual <= tolerance(dtype)
    passed = passed and axial_as_polar >= 1.0e-4 and output_parity == 1 and even_gate_parity == 1 and pseudo_gate_parity == -1
    passed = passed and mixed_gate_failure >= 1.0e-4
    return {
        "pass": passed,
        "polar_residual": polar_residual,
        "axial_residual": axial_residual,
        "parity_product": output_parity,
        "even_gate_output_parity": even_gate_parity,
        "pseudoscalar_gate_output_parity": pseudo_gate_parity,
        "fault_residuals": {"axial_as_polar": axial_as_polar, "one_plus_pseudoscalar": mixed_gate_failure},
        "threshold": tolerance(dtype),
    }


def _faulty_point_message_layer(
    node_coefficients: np.ndarray,
    graph: dict[str, Any],
    directions: np.ndarray,
) -> dict[int, np.ndarray]:
    c11, outputs, _ = cg_matrix(1, 1)
    result = {total_j: np.zeros((graph["coordinates"].shape[0], 2 * total_j + 1), dtype=node_coefficients.dtype) for total_j in (0, 1, 2)}
    for edge, (receiver, sender) in enumerate(zip(graph["receiver"], graph["sender"])):
        point_value = complex_spherical_values(directions[edge], 1).astype(node_coefficients.dtype)
        coupled = c11.astype(node_coefficients.dtype) @ np.kron(node_coefficients[int(sender)], point_value)
        for total_j in (0, 1, 2):
            indices = [index for index, label in enumerate(outputs) if label[0] == total_j]
            result[total_j][int(receiver)] += coupled[indices]
    return result


def test_t_e08(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    complex_dtype = np.dtype(np.complex64 if dtype == np.dtype(np.float32) else np.complex128)
    graph = make_graph(case["seed"], dtype, case["scale"])
    directions = graph["coordinates"][graph["sender"]] - graph["coordinates"][graph["receiver"]]
    provenance = make_message_provenance(graph, directions)
    rng = np.random.Generator(np.random.PCG64(case["seed"] + 101))
    node_coefficients = np.asarray(
        rng.standard_normal((graph["coordinates"].shape[0], 3)) + 1j * rng.standard_normal((graph["coordinates"].shape[0], 3)),
        dtype=complex_dtype,
    )
    base = message_layer(node_coefficients, graph, directions, provenance)
    inverted_nodes = -node_coefficients
    inverted_directions = -directions
    inverted = message_layer(
        inverted_nodes,
        graph,
        inverted_directions,
        make_message_provenance(graph, inverted_directions),
    )
    inversion_residual = max(normalized_residual(inverted[total_j], base[total_j]) for total_j in (0, 1, 2))
    wrong_output_parity_residual = normalized_residual(inverted[2], -base[2])
    max_layer_residual = 0.0
    for rotation in case["rotations"][: min(24, len(case["rotations"]))]:
        d1 = complex_representation(rotation, 1).astype(complex_dtype)
        rotated_nodes = np.einsum("ab,nb->na", d1, node_coefficients, optimize=False)
        rotated_directions = np.einsum("ab,eb->ea", rotation, directions, optimize=False)
        rotated_provenance = make_message_provenance(graph, rotated_directions)
        actual = message_layer(rotated_nodes, graph, rotated_directions, rotated_provenance)
        for total_j in (0, 1, 2):
            d_out = complex_representation(rotation, total_j).astype(complex_dtype)
            expected = np.einsum("ab,nb->na", d_out, base[total_j], optimize=False)
            max_layer_residual = max(max_layer_residual, normalized_residual(actual[total_j], expected))
    fixture = axis_angle_rotation((2, -1, 1), 0.73, dtype)
    d1_fixture = complex_representation(fixture, 1).astype(complex_dtype)
    rotated_nodes = np.einsum("ab,nb->na", d1_fixture, node_coefficients, optimize=False)
    rotated_directions = np.einsum("ab,eb->ea", fixture, directions, optimize=False)
    faulty_actual = _faulty_point_message_layer(rotated_nodes, graph, rotated_directions)
    faulty_base = _faulty_point_message_layer(node_coefficients, graph, directions)
    point_fault = 0.0
    for total_j in (0, 1, 2):
        expected = np.einsum("ab,nb->na", complex_representation(fixture, total_j).astype(complex_dtype), faulty_base[total_j], optimize=False)
        point_fault = max(point_fault, normalized_residual(faulty_actual[total_j], expected))
    wrong_direction = message_layer(node_coefficients, graph, -directions, make_message_provenance(graph, -directions))
    direction_fault = max(normalized_residual(wrong_direction[total_j], base[total_j]) for total_j in (0, 1, 2))
    component_square_fault = normalized_residual((d1_fixture @ node_coefficients[0]) ** 2, d1_fixture @ (node_coefficients[0] ** 2))
    wrong_cg_provenance = copy.deepcopy(provenance)
    wrong_cg_provenance["output_irreps"] = [0, 2, 1]
    wrong_parity_provenance = copy.deepcopy(provenance)
    wrong_parity_provenance["input_irrep"] = [1, 1]
    stale_provenance_failures = [
        _capture_failure(
            "stale_direction_provenance",
            lambda: message_layer(node_coefficients, graph, -directions, provenance),
        ),
        _capture_failure(
            "direction_row_permutation",
            lambda: message_layer(node_coefficients, graph, np.roll(directions, 1, axis=0), provenance),
        ),
        _capture_failure(
            "wrong_cg_channel_metadata",
            lambda: message_layer(node_coefficients, graph, directions, wrong_cg_provenance),
        ),
        _capture_failure(
            "wrong_irrep_parity_metadata",
            lambda: message_layer(node_coefficients, graph, directions, wrong_parity_provenance),
        ),
    ]
    identity_unchanged = provenance["edge_id"] == make_message_provenance(graph, rotated_directions)["edge_id"]
    tau = tolerance(dtype)
    passed = max(max_layer_residual, inversion_residual) <= tau and identity_unchanged
    passed = passed and min(point_fault, direction_fault, component_square_fault, wrong_output_parity_residual) >= 1.0e-4
    passed = passed and len(stale_provenance_failures) == 4
    return {
        "pass": passed,
        "max_layer_residual": max_layer_residual,
        "inversion_residual": inversion_residual,
        "edge_count": len(graph["edge_id"]),
        "edge_identity_unchanged": identity_unchanged,
        "filter_version": FILTER_VERSION,
        "filter_payload_hashes": {str(ell): coefficient_filter_payload_hash(ell) for ell in (0, 1, 2)},
        "fault_residuals": {
            "point_value_direct_to_cg": point_fault,
            "edge_direction_reversed": direction_fault,
            "componentwise_square": component_square_fault,
            "wrong_output_parity": wrong_output_parity_residual,
        },
        "captured_failures": stale_provenance_failures,
        "threshold": tau,
    }


def test_t_e09(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    tau0 = zero_tolerance(dtype)
    tau_frame = frame_tolerance(dtype)
    failures: list[dict[str, str]] = []
    boundary: list[dict[str, Any]] = []
    u = np.asarray([1.0, 0.0, 0.0], dtype=dtype)
    for epsilon in (0.0, tau_frame / 4, tau_frame / 2, tau_frame, 2 * tau_frame, 4 * tau_frame, 1.0e-2):
        v = np.asarray([1.0, epsilon, 0.0], dtype=dtype)
        v /= np.linalg.norm(v)
        eta = float(np.linalg.norm(np.cross(u, v)))
        accepted = eta > tau_frame
        try:
            _, evidence = local_frame(u, v, 1.0)
            actual_accepted = True
            actual_eta = evidence["eta"]
        except ValueError:
            actual_accepted = False
            actual_eta = eta
        _require(actual_accepted == accepted, "frame threshold direction is inconsistent")
        boundary.append({"epsilon": float(epsilon), "eta": actual_eta, "accepted": actual_accepted})
    for ratio in (0.0, 0.5 * tau0, tau0):
        failures.append(
            _capture_failure(
                f"zero_ratio_{ratio:.9g}",
                lambda ratio=ratio: local_frame(np.asarray([ratio, 0.0, 0.0], dtype=dtype), np.asarray([0.0, 1.0, 0.0], dtype=dtype), 1.0),
            )
        )
    accepted_frame, accepted_evidence = local_frame(
        np.asarray([2 * tau0, 0.0, 0.0], dtype=dtype), np.asarray([0.0, 1.0, 0.0], dtype=dtype), 1.0
    )
    rotation = axis_angle_rotation((1, 2, -1), 0.61, dtype)
    v_good = np.asarray([1.0, 1.0, 0.0], dtype=dtype) / np.asarray(math.sqrt(2), dtype=dtype)
    frame, _ = local_frame(u, v_good, 1.0)
    rotated_frame, _ = local_frame(rotation @ u, rotation @ v_good, 1.0)
    frame_equivariance = normalized_residual(rotated_frame, rotation @ frame)
    hamiltonian = fixed_hamiltonian(dtype)
    sender_u = np.asarray([0.0, 1.0, 0.0], dtype=dtype)
    sender_v = np.asarray([0.0, 1.0, 1.0], dtype=dtype) / np.asarray(math.sqrt(2), dtype=dtype)
    sender_frame, _ = local_frame(sender_u, sender_v, 1.0)
    ui = block_diagonal(np.ones((1, 1), dtype=dtype), frame)
    uj = block_diagonal(sender_frame, d_representation(sender_frame))
    local_block = ui.T @ hamiltonian @ uj
    rotated_receiver_frame, _ = local_frame(rotation @ u, rotation @ v_good, 1.0)
    rotated_sender_frame, _ = local_frame(rotation @ sender_u, rotation @ sender_v, 1.0)
    di = block_diagonal(np.ones((1, 1), dtype=dtype), rotation)
    dj = block_diagonal(rotation, d_representation(rotation))
    rotated_h = di @ hamiltonian @ dj.T
    ui_rotated = block_diagonal(np.ones((1, 1), dtype=dtype), rotated_receiver_frame)
    uj_rotated = block_diagonal(rotated_sender_frame, d_representation(rotated_sender_frame))
    rotated_local = ui_rotated.T @ rotated_h @ uj_rotated
    local_invariance = normalized_residual(rotated_local, local_block)
    pullback = ui @ local_block @ uj.T
    pullback_residual = normalized_residual(pullback, hamiltonian)
    wrong_pullback = normalized_residual(ui.T @ local_block @ uj, hamiltonian)
    fallback_rotation = axis_angle_rotation((1, 0, 0), math.pi / 2, dtype)
    ey = np.asarray([0.0, 1.0, 0.0], dtype=dtype)
    fixed_fallback_failure = float(np.linalg.norm(ey - fallback_rotation @ ey))
    positive_frame, _ = local_frame(u, np.asarray([1.0, 4 * tau_frame, 0.0], dtype=dtype), 1.0)
    negative_frame, _ = local_frame(u, np.asarray([1.0, -4 * tau_frame, 0.0], dtype=dtype), 1.0)
    jump = float(np.linalg.norm(positive_frame - negative_frame))
    tau = tolerance(dtype)
    passed = max(frame_equivariance, local_invariance, pullback_residual) <= tau
    passed = passed and len(failures) == 3 and accepted_evidence["zeta_u"] > tau0
    passed = passed and min(wrong_pullback, fixed_fallback_failure, jump) >= 1.0e-4
    return {
        "pass": passed,
        "boundary_matrix": boundary,
        "zero_length_failures": failures,
        "accepted_zero_boundary_zeta": accepted_evidence["zeta_u"],
        "accepted_frame_determinant": float(np.linalg.det(accepted_frame)),
        "frame_equivariance_residual": frame_equivariance,
        "local_block_invariance_residual": local_invariance,
        "pullback_residual": pullback_residual,
        "fault_residuals": {
            "wrong_pullback": wrong_pullback,
            "fixed_global_fallback": fixed_fallback_failure,
            "positive_negative_limit_jump": jump,
        },
        "threshold": tau,
    }


def _scan_case_id(dtype: str, seed: int, n_rotations: int, multiplier: int, scale: float) -> str:
    return f"{dtype}-s{seed}-r{n_rotations}-m{multiplier}-a{scale:.0e}"


@functools.lru_cache(maxsize=1)
def run_scan() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    max_residual = 0.0
    worst_case = ""
    worst_rotation = 0
    worst_ell = 0
    for dtype in ("float64", "float32"):
        for seed in SEEDS:
            for n_rotations in SCAN_ROTATION_COUNTS:
                for multiplier in SCAN_MULTIPLIERS:
                    for scale in SCAN_SCALES:
                        case = make_scan_case(dtype, seed, n_rotations, multiplier, scale)
                        equivariance = reference_equivariance(case)
                        residual = float(equivariance["max_residual"])
                        threshold = tolerance(np.dtype(dtype))
                        if not math.isfinite(residual):
                            raise ValueError("scan residual must be finite")
                        case_pass = residual <= threshold
                        cost = reference_cost(case)
                        memory = array_summary(case)
                        case_id = _scan_case_id(dtype, seed, n_rotations, multiplier, scale)
                        if residual > max_residual:
                            max_residual = residual
                            worst_case = case_id
                            worst_rotation = int(equivariance["worst"]["rotation"])
                            worst_ell = int(equivariance["worst"]["ell"])
                        cases.append(
                            {
                                "case_id": case_id,
                                "dtype": dtype,
                                "seed": seed,
                                "n_rotations": n_rotations,
                                "multiplier": multiplier,
                                "scale": scale,
                                "graph": case["graph"]["graph_name"],
                                "N": int(case["graph"]["coordinates"].shape[0]),
                                "E": int(case["graph"]["receiver"].shape[0]),
                                "max_residual": residual,
                                "threshold": threshold,
                                "pass": case_pass,
                                "worst_rotation": int(equivariance["worst"]["rotation"]),
                                "worst_ell": int(equivariance["worst"]["ell"]),
                                **cost,
                                "array_bytes_total": memory["array_bytes_total"],
                                "array_bytes_peak": memory["array_bytes_peak"],
                            }
                        )
    anchor_a = next(item for item in cases if item["dtype"] == "float64" and item["seed"] == 20260809 and item["n_rotations"] == 1 and item["multiplier"] == 1 and item["scale"] == 1.0)
    anchor_b = next(item for item in cases if item["dtype"] == "float64" and item["seed"] == 20260810 and item["n_rotations"] == 1 and item["multiplier"] == 1 and item["scale"] == 1.0)
    axes = {
        "dtype": ["float64", "float32"],
        "seed": list(SEEDS),
        "n_rotations": list(SCAN_ROTATION_COUNTS),
        "multiplier": list(SCAN_MULTIPLIERS),
        "scale": list(SCAN_SCALES),
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "mode": "stageE-scan-v1",
        "case_count": len(cases),
        "axes": axes,
        "cases": cases,
        "max_residual": max_residual,
        "worst_case": worst_case,
        "worst_rotation": worst_rotation,
        "worst_ell": worst_ell,
        "anchors": {
            "G_A": {name: anchor_a[name] for name in ("mac_per_rotation", "aggregation_add_per_rotation", "array_bytes_total", "array_bytes_peak")},
            "G_B": {name: anchor_b[name] for name in ("mac_per_rotation", "aggregation_add_per_rotation", "array_bytes_total", "array_bytes_peak")},
        },
        "pass": len(cases) == 144 and all(item["pass"] for item in cases),
    }
    result["canonical_case_digest"] = sha256_text(canonical_json(cases))
    return result


def test_t_e10(case: dict[str, Any]) -> dict[str, Any]:
    scan = run_scan()
    config_cost = reference_cost(case)
    config_memory = array_summary(case)
    config_equivariance = reference_equivariance(case)
    anchors_pass = scan["anchors"] == {
        "G_A": {"mac_per_rotation": 168, "aggregation_add_per_rotation": 52, "array_bytes_total": 2728, "array_bytes_peak": 2280},
        "G_B": {"mac_per_rotation": 378, "aggregation_add_per_rotation": 143, "array_bytes_total": 5584, "array_bytes_peak": 4576},
    }
    passed = scan["pass"] and anchors_pass and config_equivariance["max_residual"] <= tolerance(case["dtype"])
    return {
        "pass": passed,
        "scan_case_count": scan["case_count"],
        "scan_axes": scan["axes"],
        "scan_max_residual": scan["max_residual"],
        "scan_worst_case": scan["worst_case"],
        "scan_worst_rotation": scan["worst_rotation"],
        "scan_worst_ell": scan["worst_ell"],
        "scan_case_digest": scan["canonical_case_digest"],
        "anchors": scan["anchors"],
        "config_cost": config_cost,
        "config_memory": config_memory,
        "config_equivariance": config_equivariance,
        "timing_fields_excluded": True,
    }


def test_t_e11(case: dict[str, Any]) -> dict[str, Any]:
    dtype = _config_dtype(case)
    complex_dtype = np.dtype(np.complex64 if dtype == np.dtype(np.float32) else np.complex128)
    axis = np.asarray([1.0, 2.0, -1.0], dtype=dtype)
    axis /= np.linalg.norm(axis)
    angle = 0.61
    quaternion = np.asarray([math.cos(angle / 2), *(axis * math.sin(angle / 2))], dtype=dtype)
    quaternion /= np.linalg.norm(quaternion)
    validate_unit_quaternion(quaternion)
    rotation = axis_angle_rotation(axis, angle, dtype)
    unitary = su2_from_quaternion(quaternion)
    pauli = pauli_matrices(dtype)
    su2_unitarity = normalized_residual(unitary @ unitary.conj().T, np.eye(2, dtype=complex_dtype))
    lift_residual = 0.0
    for source_index, sigma in enumerate(pauli):
        transformed = unitary @ sigma @ unitary.conj().T
        expected = sum(rotation[target_index, source_index] * pauli[target_index] for target_index in range(3))
        lift_residual = max(lift_residual, normalized_residual(transformed, expected))
    js = spin_time_reversal(dtype)
    theta_square_spin = normalized_residual(js @ js.conj(), -np.eye(2, dtype=complex_dtype))
    j_orbital_residual = 0.0
    for ell in (1, 2):
        j_ell = orbital_time_reversal(ell, dtype)
        d_ell = complex_representation(rotation, ell).astype(complex_dtype)
        j_orbital_residual = max(
            j_orbital_residual,
            normalized_residual(j_ell @ d_ell.conj() @ j_ell.conj().T, d_ell),
        )
    bridge = coefficient_bridge(1, dtype)
    j_bridge = bridge @ bridge.T
    j_formula = orbital_time_reversal(1, dtype)
    bridge_residual = normalized_residual(j_bridge, j_formula)
    psi = np.asarray([1.0 + 0.5j, -0.2 + 0.7j], dtype=complex_dtype)
    theta_psi = time_reverse(psi, js)
    theta_twice = time_reverse(theta_psi, js)
    theta_square_vector = normalized_residual(theta_twice, -psi)
    antilinear = normalized_residual(time_reverse(1j * psi, js), -1j * theta_psi)
    kramers_overlap = abs(complex(np.vdot(psi, theta_psi)))

    spinless_j = np.eye(2, dtype=complex_dtype)
    spinless_psi = np.asarray([0.4 + 0.8j, -0.2 + 0.1j], dtype=complex_dtype)
    spinless_theta = time_reverse(spinless_psi, spinless_j)
    spinless_square = normalized_residual(time_reverse(spinless_theta, spinless_j), spinless_psi)
    spinless_antilinearity = normalized_residual(
        time_reverse(1j * spinless_psi, spinless_j),
        -1j * spinless_theta,
    )

    two_pi = su2_from_quaternion(np.asarray([-1.0, 0.0, 0.0, 0.0], dtype=dtype))
    four_pi = su2_from_quaternion(np.asarray([1.0, 0.0, 0.0, 0.0], dtype=dtype))
    two_pi_residual = normalized_residual(two_pi, -np.eye(2, dtype=complex_dtype))
    four_pi_residual = normalized_residual(four_pi, np.eye(2, dtype=complex_dtype))

    pair = make_time_reversal_pair(dtype)
    validate_time_reversal_pair(pair)
    h_pair_residual = normalized_residual(pair["H_minus_k"], js @ pair["H_k"].conj() @ js.conj().T)
    s_pair_residual = normalized_residual(pair["S_minus_k"], js @ pair["S_k"].conj() @ js.conj().T)
    pair_hermiticity = max(
        normalized_residual(pair[name], pair[name].conj().T)
        for name in ("H_k", "H_minus_k", "S_k", "S_minus_k")
    )
    partner_map_array = np.asarray(pair["partner_map"], dtype=np.int64)
    pair_runtime_arrays = {
        "kpoint": pair["kpoint"],
        "minus_kpoint": pair["minus_kpoint"],
        "partner_map": partner_map_array,
        "active_mask": pair["active_mask"],
        "J": js,
        "H_k": pair["H_k"],
        "H_minus_k": pair["H_minus_k"],
        "S_k": pair["S_k"],
        "S_minus_k": pair["S_minus_k"],
        "H_k_conjugate_work": np.array(pair["H_k"].conj(), copy=True),
        "H_partner_output": np.array(js @ pair["H_k"].conj() @ js.conj().T, copy=True),
        "S_k_conjugate_work": np.array(pair["S_k"].conj(), copy=True),
        "S_partner_output": np.array(js @ pair["S_k"].conj() @ js.conj().T, copy=True),
    }
    pair_array_summary = {
        name: {"shape": list(array.shape), "dtype": array.dtype.name, "nbytes": int(array.nbytes)}
        for name, array in pair_runtime_arrays.items()
    }
    pair_array_bytes_total = sum(item["nbytes"] for item in pair_array_summary.values())

    identity_orbital = np.eye(2, dtype=complex_dtype)
    j_trim = np.kron(identity_orbital, js)
    h_trim = np.diag(np.asarray([0.25, 0.25, 0.8, 0.8], dtype=complex_dtype))
    s_trim = np.diag(np.asarray([1.0, 1.0, 1.2, 1.2], dtype=complex_dtype))
    trim_h_residual = normalized_residual(h_trim, j_trim @ h_trim.conj() @ j_trim.conj().T)
    trim_s_residual = normalized_residual(s_trim, j_trim @ s_trim.conj() @ j_trim.conj().T)
    trim_theta_square = normalized_residual(j_trim @ j_trim.conj(), -np.eye(4, dtype=complex_dtype))
    trim_eigenvalues = scipy.linalg.eigvalsh(h_trim, s_trim)
    trim_pair_gap = max(
        abs(float(trim_eigenvalues[0] - trim_eigenvalues[1])),
        abs(float(trim_eigenvalues[2] - trim_eigenvalues[3])),
    )
    trim_vector = np.asarray([1.0, 0.0, 0.0, 0.0], dtype=complex_dtype)
    trim_partner = time_reverse(trim_vector, j_trim)
    trim_kramers_overlap = abs(complex(np.vdot(trim_vector, s_trim @ trim_partner)))
    trim_kramers_energy = normalized_residual(
        h_trim @ trim_partner,
        trim_eigenvalues[0] * (s_trim @ trim_partner),
    )

    sigma_z = pauli[2]
    zeeman_failure = normalized_residual(sigma_z, js @ sigma_z.conj() @ js.conj().T)
    linear_failure = normalized_residual(js @ (1j * psi), -1j * (js @ psi))
    wrong_bridge_failure = normalized_residual(bridge @ bridge.conj().T, j_formula)
    missing_conjugation_pair_failure = normalized_residual(
        pair["H_minus_k"],
        js @ pair["H_k"] @ js.conj().T,
    )
    zeeman_eigenvalues = np.linalg.eigvalsh(sigma_z)
    zeeman_false_kramers_gap = abs(float(zeeman_eigenvalues[1] - zeeman_eigenvalues[0]))

    pair_failures: list[dict[str, str]] = []
    for name, mutate in (
        ("time_pair_wrong_partner_id", lambda value: value.__setitem__("minus_k_id", "wrong")),
        ("time_pair_wrong_partner_map", lambda value: value.__setitem__("partner_map", [0, 1])),
        ("time_pair_partial_mask", lambda value: value["active_mask"].__setitem__((0, 0), False)),
        ("time_pair_orbital_row_drift", lambda value: value.__setitem__("partner_orbital_ids", list(reversed(value["partner_orbital_ids"])))),
        (
            "time_pair_missing_conjugation",
            lambda value: value.__setitem__("H_minus_k", js @ value["H_k"] @ js.conj().T),
        ),
        (
            "time_pair_wrong_overlap_partner",
            lambda value: value.__setitem__("S_minus_k", np.roll(value["S_minus_k"], 1, axis=0)),
        ),
    ):
        candidate = copy.deepcopy(pair)
        mutate(candidate)
        pair_failures.append(_capture_failure(name, lambda candidate=candidate: validate_time_reversal_pair(candidate)))

    tau = tolerance(dtype)
    passed = max(
        su2_unitarity,
        lift_residual,
        theta_square_spin,
        j_orbital_residual,
        bridge_residual,
        theta_square_vector,
        antilinear,
        kramers_overlap,
        spinless_square,
        spinless_antilinearity,
        two_pi_residual,
        four_pi_residual,
        h_pair_residual,
        s_pair_residual,
        pair_hermiticity,
        trim_h_residual,
        trim_s_residual,
        trim_theta_square,
        trim_pair_gap,
        trim_kramers_overlap,
        trim_kramers_energy,
    ) <= tau
    passed = passed and min(
        zeeman_failure,
        linear_failure,
        wrong_bridge_failure,
        missing_conjugation_pair_failure,
        zeeman_false_kramers_gap,
    ) >= 1.0e-4
    passed = passed and len(pair_failures) == 6
    return {
        "pass": passed,
        "su2_unitarity_residual": su2_unitarity,
        "su2_to_so3_residual": lift_residual,
        "theta_square_spin_residual": theta_square_spin,
        "orbital_JD_residual": j_orbital_residual,
        "J_basis_route_residual": bridge_residual,
        "theta_square_vector_residual": theta_square_vector,
        "antilinearity_residual": antilinear,
        "kramers_overlap_abs": kramers_overlap,
        "spinless_theta_square_residual": spinless_square,
        "spinless_antilinearity_residual": spinless_antilinearity,
        "two_pi_minus_identity_residual": two_pi_residual,
        "four_pi_identity_residual": four_pi_residual,
        "H_k_pair_residual": h_pair_residual,
        "S_k_pair_residual": s_pair_residual,
        "pair_hermiticity_residual": pair_hermiticity,
        "pair_identity": {
            "schema_version": TIME_REVERSAL_PAIR_VERSION,
            "k_id": pair["k_id"],
            "minus_k_id": pair["minus_k_id"],
            "partner_map": pair["partner_map"],
            "orbital_ids": pair["orbital_ids"],
        },
        "pair_array_summary": pair_array_summary,
        "pair_array_bytes_total": pair_array_bytes_total,
        "trim_H_residual": trim_h_residual,
        "trim_S_residual": trim_s_residual,
        "trim_theta_square_residual": trim_theta_square,
        "trim_kramers_pair_gap": trim_pair_gap,
        "trim_generalized_eigenvalues": trim_eigenvalues,
        "trim_kramers_overlap_abs": trim_kramers_overlap,
        "trim_kramers_energy_residual": trim_kramers_energy,
        "general_k_is_not_trim": not np.array_equal(pair["kpoint"], pair["minus_kpoint"]),
        "captured_failures": pair_failures,
        "fault_residuals": {
            "Zeeman_breaking": zeeman_failure,
            "missing_antilinear_conjugation": linear_failure,
            "wrong_K_dagger_route": wrong_bridge_failure,
            "H_partner_missing_conjugation": missing_conjugation_pair_failure,
            "Zeeman_false_kramers_gap": zeeman_false_kramers_gap,
        },
        "time_reversal_version": TIME_REVERSAL_VERSION,
        "payloads": time_reversal_payloads(),
        "threshold": tau,
    }


def test_t_e12(case: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []

    def mutate_case(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        candidate = copy.deepcopy(case)
        mutate(candidate)
        failures.append(_capture_failure(name, lambda: validate_case(candidate)))

    mutate_case("extra_case_field", lambda value: value.__setitem__("extra", 1))
    mutate_case("wrong_schema_version", lambda value: value.__setitem__("schema_version", "wrong"))
    mutate_case("wrong_mode", lambda value: value.__setitem__("mode", "wrong"))
    mutate_case("config_scan_mix", lambda value: value.__setitem__("multiplier", 1))
    mutate_case("wrong_seed_type", lambda value: value.__setitem__("seed", str(value["seed"])))
    mutate_case("wrong_dtype_name", lambda value: value.__setitem__("dtype", "float16"))
    mutate_case("wrong_rotation_count", lambda value: value.__setitem__("n_rotations", value["n_rotations"] + 1))
    mutate_case("wrong_multiplicity", lambda value: value.__setitem__("multiplicity", (1, 1, 1)))
    mutate_case("wrong_scale", lambda value: value.__setitem__("scale", 2.0))
    mutate_case("coordinate_nan", lambda value: value["graph"]["coordinates"].__setitem__((0, 0), np.nan))
    mutate_case("coordinate_dtype", lambda value: value["graph"].__setitem__("coordinates", value["graph"]["coordinates"].astype(np.float16)))
    mutate_case("receiver_row_roll", lambda value: value["graph"].__setitem__("receiver", np.roll(value["graph"]["receiver"], 1)))
    mutate_case("shift_identity_change", lambda value: value["graph"]["shift"].__setitem__((0, 0), 1))
    mutate_case("edge_id_change", lambda value: value["graph"]["edge_id"].__setitem__(0, "0" * 64))
    mutate_case("rotation_rank", lambda value: value.__setitem__("rotations", value["rotations"][:, None, :, :]))
    mutate_case("rotation_reflection", lambda value: value["rotations"].__setitem__(0, np.diag([-1, 1, 1]).astype(value["rotations"].dtype)))
    mutate_case("missing_irrep", lambda value: value["x"].pop("2"))
    mutate_case("x_rank", lambda value: value["x"].__setitem__("1", value["x"]["1"][:, None, :, :]))
    mutate_case("x_active_nan", lambda value: value["x"]["0"].__setitem__((0, 0, 0), np.nan))
    mutate_case("W_shape", lambda value: value["W"].__setitem__("2", value["W"]["2"][:, :, :-1]))
    mutate_case("W_dtype", lambda value: value["W"].__setitem__("0", value["W"]["0"].astype(np.float16)))
    mutate_case("basis_metadata", lambda value: value["representation_metadata"]["basis"].__setitem__("1", "wrong"))
    mutate_case("m_order_metadata", lambda value: value["representation_metadata"]["m_order"].__setitem__("1", [1, 0, -1]))
    mutate_case("M8_material_selected", lambda value: value["m8_boundary"].__setitem__("material_system", "silicon"))
    mutate_case("M8_backend_selected", lambda value: value["m8_boundary"].__setitem__("dft_backend", "vasp"))
    mutate_case("M8_data_backend_selected", lambda value: value["m8_boundary"].__setitem__("data_backend", "formal-dataset"))
    mutate_case("M8_software_selected", lambda value: value["m8_boundary"].__setitem__("deeph_software_object", "deeph"))
    mutate_case("M8_budget_selected", lambda value: value["m8_boundary"].__setitem__("training_budget", "one-gpu"))
    mutate_case("M8_physics_selected", lambda value: value["m8_boundary"].__setitem__("advanced_physics_scope", "soc"))

    dtype = np.dtype(case["dtype"])
    failures.extend(
        [
            _capture_failure("rotation_nan", lambda: validate_rotation(np.asarray([[np.nan, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=dtype))),
            _capture_failure("rotation_infinity", lambda: validate_rotation(np.asarray([[np.inf, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=dtype))),
            _capture_failure("quaternion_nan", lambda: validate_unit_quaternion(np.asarray([np.nan, 0, 0, 1], dtype=dtype))),
            _capture_failure("quaternion_infinity", lambda: validate_unit_quaternion(np.asarray([np.inf, 0, 0, 1], dtype=dtype))),
            _capture_failure(
                "quaternion_noncanonical_sign",
                lambda: validate_canonical_unit_quaternion(np.asarray([-0.5, -0.5, -0.5, -0.5], dtype=dtype)),
            ),
            _capture_failure(
                "stf_missing_normalization",
                lambda: validate_stf_basis(
                    np.asarray(_stf_basis(dtype) * np.asarray([math.sqrt(2), 1, 1, 1, 1], dtype=dtype)[:, None, None], dtype=dtype)
                ),
            ),
            _capture_failure(
                "euler_angles_not_rotation_matrix",
                lambda: complex_representation(np.asarray([0.1, 0.2, 0.3], dtype=dtype), 1),
            ),
        ]
    )

    batch = make_irrep_batch(case["dtype"])
    wrong_batch = copy.deepcopy(batch)
    wrong_batch["schema_version"] = "wrong"
    failures.append(_capture_failure("batch_version", lambda: validate_irrep_batch(wrong_batch)))
    wrong_batch = copy.deepcopy(batch)
    wrong_batch["node_mask"][0] = [True, False, True]
    failures.append(_capture_failure("noncontiguous_node_mask", lambda: validate_irrep_batch(wrong_batch)))
    wrong_batch = copy.deepcopy(batch)
    wrong_batch["values"]["1"][0, 0, 0, 0] = np.nan
    failures.append(_capture_failure("active_padding_nan", lambda: validate_irrep_batch(wrong_batch)))
    wrong_batch = copy.deepcopy(batch)
    wrong_batch["component_mask"]["2"][0, 0, 0, 0] = False
    failures.append(_capture_failure("partial_irrep_shell_mask", lambda: validate_irrep_batch(wrong_batch)))
    wrong_batch = copy.deepcopy(batch)
    wrong_batch["values"]["0"] = wrong_batch["values"]["0"][:, :, :, None, :]
    failures.append(_capture_failure("batch_rank5", lambda: validate_irrep_batch(wrong_batch)))

    batch_dtype = np.dtype(case["dtype"])
    padding_weights = {
        "0": np.asarray([[1.0, 0.2], [-0.3, 0.7]], dtype=batch_dtype),
        "1": np.asarray([[0.6, -0.4], [0.1, 1.2]], dtype=batch_dtype),
        "2": np.asarray([[1.3]], dtype=batch_dtype),
    }
    padding_outputs: list[dict[str, np.ndarray]] = []
    padding_losses: list[float] = []
    for sentinel in (np.nan, 0.0, 1.0e300):
        probe = copy.deepcopy(batch)
        for ell in range(3):
            key = str(ell)
            inactive = ~probe["component_mask"][key]
            if sentinel == 1.0e300 and batch_dtype == np.dtype(np.float32):
                probe["values"][key][inactive] = np.inf
            else:
                probe["values"][key][inactive] = sentinel
        output = padded_irrep_linear(probe, padding_weights)
        padding_outputs.append(output)
        padding_losses.append(masked_irrep_mse(output, output, probe))
    padding_residuals: list[float] = []
    for probe_output in padding_outputs[1:]:
        for ell in range(3):
            key = str(ell)
            active = batch["component_mask"][key]
            padding_residuals.append(normalized_residual(probe_output[key][active], padding_outputs[0][key][active]))

    hamiltonian = make_hamiltonian_edge(case["dtype"])
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["block"] = wrong_h["block"].astype(np.float16)
    failures.append(_capture_failure("hamiltonian_dtype", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["mask"][0, 0] = False
    failures.append(_capture_failure("hamiltonian_partial_mask", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["sender_orbitals"] = list(reversed(wrong_h["sender_orbitals"]))
    failures.append(_capture_failure("hamiltonian_orbital_order", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["edge_id"] = "0" * 64
    failures.append(_capture_failure("hamiltonian_edge_hash", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["edge_payload"] = "not-json-and-not-stageD-edge-v1"
    wrong_h["edge_id"] = sha256_text(wrong_h["edge_payload"])
    failures.append(_capture_failure("hamiltonian_forged_payload_rehash", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["receiver"] = 2
    wrong_h["edge_payload"] = edge_payload(wrong_h["structure_id"], 2, wrong_h["sender"], wrong_h["shift"])
    wrong_h["edge_id"] = sha256_text(wrong_h["edge_payload"])
    failures.append(_capture_failure("hamiltonian_payload_wrong_endpoint", lambda: validate_hamiltonian_edge(wrong_h)))
    wrong_h = copy.deepcopy(hamiltonian)
    wrong_h["shift"] = (1, 0, 0)
    wrong_h["edge_payload"] = edge_payload(wrong_h["structure_id"], wrong_h["receiver"], wrong_h["sender"], wrong_h["shift"])
    wrong_h["edge_id"] = sha256_text(wrong_h["edge_payload"])
    failures.append(_capture_failure("hamiltonian_payload_wrong_shift", lambda: validate_hamiltonian_edge(wrong_h)))
    inverse_h = make_hamiltonian_edge(case["dtype"], reverse=True)
    inverse_h["receiver"], inverse_h["sender"] = inverse_h["sender"], inverse_h["receiver"]
    failures.append(_capture_failure("hamiltonian_inverse_endpoint_not_swapped", lambda: validate_hamiltonian_edge(inverse_h)))

    graph = case["graph"]
    directions = graph["coordinates"][graph["sender"]] - graph["coordinates"][graph["receiver"]]
    provenance = make_message_provenance(graph, directions)
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["schema_version"] = "wrong"
    failures.append(_capture_failure("filter_version", lambda: validate_message_provenance(graph, wrong_provenance)))
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["direction"][0] = 0
    failures.append(_capture_failure("zero_filter_direction", lambda: validate_message_provenance(graph, wrong_provenance)))
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["receiver"] = np.roll(wrong_provenance["receiver"], 1)
    failures.append(_capture_failure("filter_edge_row_mismatch", lambda: validate_message_provenance(graph, wrong_provenance)))
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["m_order"] = [1, 0, -1]
    failures.append(_capture_failure("filter_m_order", lambda: validate_message_provenance(graph, wrong_provenance)))
    complex_dtype = np.dtype(np.complex64 if batch_dtype == np.dtype(np.float32) else np.complex128)
    node_coefficients = np.ones((graph["coordinates"].shape[0], 3), dtype=complex_dtype)
    failures.append(
        _capture_failure(
            "filter_stale_direction_provenance",
            lambda: message_layer(node_coefficients, graph, -directions, provenance),
        )
    )
    failures.append(
        _capture_failure(
            "filter_direction_row_permutation",
            lambda: message_layer(node_coefficients, graph, np.roll(directions, 1, axis=0), provenance),
        )
    )
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["cg_table_sha256"] = "0" * 64
    failures.append(
        _capture_failure(
            "filter_wrong_cg_table",
            lambda: message_layer(node_coefficients, graph, directions, wrong_provenance),
        )
    )
    wrong_provenance = copy.deepcopy(provenance)
    wrong_provenance["output_irreps"] = [0, 2, 1]
    failures.append(
        _capture_failure(
            "filter_wrong_cg_channel",
            lambda: message_layer(node_coefficients, graph, directions, wrong_provenance),
        )
    )

    time_pair = make_time_reversal_pair(case["dtype"])
    js = spin_time_reversal(case["dtype"])
    for name, mutate in (
        ("time_pair_wrong_partner_id", lambda value: value.__setitem__("minus_k_id", "wrong")),
        ("time_pair_wrong_partner_map", lambda value: value.__setitem__("partner_map", [0, 1])),
        ("time_pair_partial_mask", lambda value: value["active_mask"].__setitem__((0, 0), False)),
        ("time_pair_orbital_row_drift", lambda value: value.__setitem__("partner_orbital_ids", list(reversed(value["partner_orbital_ids"])))),
        ("time_pair_missing_conjugation", lambda value: value.__setitem__("H_minus_k", js @ value["H_k"] @ js.conj().T)),
        ("time_pair_wrong_overlap_partner", lambda value: value.__setitem__("S_minus_k", np.roll(value["S_minus_k"], 1, axis=0))),
    ):
        candidate = copy.deepcopy(time_pair)
        mutate(candidate)
        failures.append(_capture_failure(name, lambda candidate=candidate: validate_time_reversal_pair(candidate)))

    names = [item["name"] for item in failures]
    passed = len(failures) == 63 and len(set(names)) == 63
    passed = passed and max(padding_residuals, default=0.0) == 0.0 and max(padding_losses) == 0.0
    passed = passed and all(value == "UNRESOLVED_M8" for value in case["m8_boundary"].values())
    return {
        "pass": passed,
        "rejected": len(failures),
        "total": len(failures),
        "captured_failures": failures,
        "unique_failure_names": len(set(names)),
        "padding_probe_sentinels": ["NaN", "0", "1e300"],
        "padding_probe_max_active_residual": max(padding_residuals, default=0.0),
        "padding_probe_losses": padding_losses,
        "batch_schema_version": BATCH_VERSION,
        "forbidden_external_objects": list(forbidden_external_objects()),
        "m8_boundary": case["m8_boundary"],
    }


TEST_FUNCTIONS = (
    test_t_e01,
    test_t_e02,
    test_t_e03,
    test_t_e04,
    test_t_e05,
    test_t_e06,
    test_t_e07,
    test_t_e08,
    test_t_e09,
    test_t_e10,
    test_t_e11,
    test_t_e12,
)


def run_suite(config_id: str) -> dict[str, Any]:
    case = make_config_case(config_id)
    tests: dict[str, Any] = {}
    for index, function in enumerate(TEST_FUNCTIONS, start=1):
        result = function(case)
        _require(result["pass"], f"T-E{index:02d} failed")
        tests[f"T-E{index:02d}"] = result
    result = {
        "schema_version": SCHEMA_VERSION,
        "config_id": config_id,
        "seed": case["seed"],
        "dtype": case["dtype"],
        "n_rotations": case["n_rotations"],
        "multiplicity": list(case["multiplicity"]),
        "graph": {
            "name": case["graph"]["graph_name"],
            "N": int(case["graph"]["coordinates"].shape[0]),
            "E": int(case["graph"]["receiver"].shape[0]),
            "edge_id_sha256": sha256_text(canonical_json(case["graph"]["edge_id"])),
        },
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "tests": tests,
        "overall_pass": all(item["pass"] for item in tests.values()),
    }
    return _to_python(result)


def benchmark_config(config_id: str) -> dict[str, Any]:
    measurements: list[float] = []
    for _ in range(3):
        reference_equivariance(make_config_case(config_id))
    for _ in range(7):
        started = time.perf_counter()
        reference_equivariance(make_config_case(config_id))
        measurements.append(time.perf_counter() - started)
    values = np.asarray(measurements, dtype=np.float64)
    return {
        "noncanonical": True,
        "config_id": config_id,
        "warmup_count": 3,
        "measurement_count": 7,
        "median_seconds": float(np.median(values)),
        "iqr_seconds": float(np.quantile(values, 0.75) - np.quantile(values, 0.25)),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stage E deterministic synthetic equivariance acceptance suite")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--config", choices=("A", "B"))
    mode.add_argument("--scan", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--benchmark", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    if arguments.scan:
        if arguments.seed is not None or arguments.benchmark:
            parser.error("--scan rejects --seed and --benchmark")
        payload = run_scan()
    else:
        expected_seed = CONFIG_CASES[arguments.config]["seed"]
        if arguments.seed is not None and arguments.seed != expected_seed:
            parser.error("--seed conflicts with the frozen config")
        payload = benchmark_config(arguments.config) if arguments.benchmark else run_suite(arguments.config)
    print(json.dumps(_to_python(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
