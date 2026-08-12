from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
import time
from typing import Any, Callable

import numpy as np
import scipy

from staged_models import (
    BATCH_SCHEMA_VERSION,
    COND_LIMIT,
    DISPLACEMENT_ATOL,
    OUTPUT_SCHEMA_VERSION,
    SCHEMA_VERSION,
    activation_bytes,
    aggregate_messages,
    backward_mpnn,
    build_periodic_graph,
    canonical_edge_payload,
    edge_instance_id,
    edge_features_from_geometry,
    edge_output_by_key,
    finite_difference_gradient_error,
    forward_mpnn,
    forward_padded_batch,
    graph_keys,
    group_split_evidence,
    grouped_regression,
    init_mpnn_parameters,
    linear_support_propagation,
    make_concat_batch,
    make_edge_output,
    make_orbital_provenance,
    make_padded_batch,
    masked_mse,
    mirror_bounds,
    parameter_gradient_relative_error,
    predecessor_sets,
    representative_residuals,
    transformed_representatives,
    validate_cell,
    validate_concat_batch,
    validate_cutoff,
    validate_edge_output,
    validate_graph,
    validate_group_split,
    validate_mpnn_cache,
    validate_orbital_provenance,
    validate_padded_batch,
)


CONFIGS = {
    "A": {
        "seed": 20260806,
        "layers": 2,
        "hidden_dim": 3,
        "edge_dim": 2,
        "output_dim": 4,
        "groups": 12,
        "frames": 6,
        "training_steps": 500,
        "learning_rate": 0.08,
        "test_mse_threshold": 2.0e-2,
    },
    "B": {
        "seed": 20260817,
        "layers": 3,
        "hidden_dim": 4,
        "edge_dim": 3,
        "output_dim": 4,
        "groups": 15,
        "frames": 5,
        "training_steps": 700,
        "learning_rate": 0.06,
        "test_mse_threshold": 2.0e-2,
    },
}


def _json_scalar(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): _json_scalar(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_scalar(item) for item in value]
    return value


def _capture_failure(name: str, operation: Callable[[], Any]) -> dict[str, str]:
    try:
        operation()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"name": name, "error_type": type(error).__name__, "message": str(error)}
    raise AssertionError(f"expected failure was accepted: {name}")


def _main_graph() -> dict[str, Any]:
    cell = np.asarray(
        [
            [1.4, 0.0, 0.0],
            [0.2, 1.7, 0.0],
            [0.1, 0.3, 1.9],
        ],
        dtype=np.float64,
    )
    fractional = np.asarray(
        [
            [0.05, 0.10, 0.15],
            [0.45, 0.20, 0.25],
            [0.80, 0.65, 0.40],
            [0.20, 0.75, 0.85],
        ],
        dtype=np.float64,
    )
    return build_periodic_graph(cell, fractional, 1.15, "stageD-main")


def _multi_graph() -> dict[str, Any]:
    return build_periodic_graph(
        np.diag([1.0, 5.0, 5.0]),
        np.asarray([[0.25, 0.0, 0.0], [0.75, 0.0, 0.0]], dtype=np.float64),
        1.0,
        "stageD-multi",
    )


def _edge_features(graph: dict[str, Any], edge_dim: int) -> np.ndarray:
    return edge_features_from_geometry(graph, edge_dim)


def _append_duplicate_record(graph: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(graph)
    for key in ("receiver", "sender", "distance", "edge_instance_id"):
        mutated[key] = np.concatenate([mutated[key], mutated[key][:1]])
    for key in ("shift", "displacement"):
        mutated[key] = np.concatenate([mutated[key], mutated[key][:1]], axis=0)
    return mutated


def _failure_t_d09(
    graph: dict[str, Any],
    other_graph: dict[str, Any],
    provenance: dict[str, Any],
    cache: dict[str, Any],
    *,
    hidden_dim: int,
    edge_dim: int,
    layers: int,
) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []

    missing_shift = copy.deepcopy(graph)
    missing_shift.pop("shift")
    failures.append(_capture_failure("delete_shift", lambda: validate_graph(missing_shift)))

    swapped = copy.deepcopy(graph)
    swapped["receiver"], swapped["sender"] = swapped["sender"].copy(), swapped["receiver"].copy()
    failures.append(_capture_failure("swap_receiver_sender", lambda: validate_graph(swapped)))

    duplicate_id = copy.deepcopy(graph)
    if duplicate_id["edge_instance_id"].size > 1:
        duplicate_id["edge_instance_id"][1] = duplicate_id["edge_instance_id"][0]
    failures.append(_capture_failure("duplicate_edge_id", lambda: validate_graph(duplicate_id)))

    wrong_shape = copy.deepcopy(provenance)
    wrong_shape["block_shape"][0, 1] += 1
    failures.append(_capture_failure("wrong_block_shape", lambda: validate_orbital_provenance(graph, wrong_shape)))

    wrong_mask = copy.deepcopy(provenance)
    wrong_mask["mask"][0, 0] = False
    wrong_mask["mask"][0, 1] = True
    failures.append(_capture_failure("noncontiguous_mask", lambda: validate_orbital_provenance(graph, wrong_mask)))

    wrong_mask_dtype = copy.deepcopy(provenance)
    wrong_mask_dtype["mask"] = wrong_mask_dtype["mask"].astype(np.int8)
    failures.append(_capture_failure("wrong_mask_dtype", lambda: validate_orbital_provenance(graph, wrong_mask_dtype)))

    wrong_mask_shape = copy.deepcopy(provenance)
    wrong_mask_shape["mask"] = wrong_mask_shape["mask"][:, :-1]
    failures.append(_capture_failure("wrong_mask_shape", lambda: validate_orbital_provenance(graph, wrong_mask_shape)))

    padding_active = copy.deepcopy(provenance)
    padding_position = np.argwhere(~padding_active["mask"])[0]
    padding_active["mask"][tuple(padding_position)] = True
    failures.append(_capture_failure("padding_mask_active", lambda: validate_orbital_provenance(graph, padding_active)))

    wrong_orbitals = copy.deepcopy(provenance)
    node_with_two = next(index for index, values in enumerate(wrong_orbitals["node_orbitals"]) if len(values) == 2)
    wrong_orbitals["node_orbitals"][node_with_two] = list(reversed(wrong_orbitals["node_orbitals"][node_with_two]))
    failures.append(_capture_failure("orbital_order_drift", lambda: validate_orbital_provenance(graph, wrong_orbitals)))

    failures.append(_capture_failure("pmax_too_small", lambda: make_orbital_provenance(graph, 3)))

    output = make_edge_output(
        graph,
        np.zeros(provenance["mask"].shape, dtype=np.float64),
        provenance,
    )
    extra_output_row = copy.deepcopy(output)
    for name in (
        "prediction", "mask", "orbital_i_index", "orbital_j_index", "orbital_i_id", "orbital_j_id"
    ):
        extra_output_row[name] = np.concatenate([extra_output_row[name], extra_output_row[name][:1]], axis=0)
    failures.append(
        _capture_failure(
            "edge_output_extra_component_row",
            lambda: validate_edge_output(graph, provenance, extra_output_row),
        )
    )
    missing_output_row = copy.deepcopy(output)
    for name in (
        "prediction", "mask", "orbital_i_index", "orbital_j_index", "orbital_i_id", "orbital_j_id"
    ):
        missing_output_row[name] = missing_output_row[name][:-1]
    failures.append(
        _capture_failure(
            "edge_output_missing_component_row",
            lambda: validate_edge_output(graph, provenance, missing_output_row),
        )
    )

    concat = make_concat_batch([graph, other_graph])
    cross_graph = copy.deepcopy(concat)
    cross_graph["sender"][0] = graph["fractional"].shape[0]
    failures.append(_capture_failure("cross_graph_edge", lambda: validate_concat_batch(cross_graph)))

    negative_graph_id = make_concat_batch([graph, other_graph])
    negative_graph_id["node_graph_id"][0] = -1
    failures.append(_capture_failure("negative_graph_id", lambda: validate_concat_batch(negative_graph_id)))

    wrong_count = make_concat_batch([graph, other_graph])
    wrong_count["edge_count"][0] -= 1
    failures.append(_capture_failure("wrong_graph_count", lambda: validate_concat_batch(wrong_count)))

    misaligned_batch_provenance = make_concat_batch([graph, other_graph])
    misaligned_batch_provenance["orbital_i_id"] = np.roll(misaligned_batch_provenance["orbital_i_id"], 1, axis=0)
    failures.append(_capture_failure("batch_provenance_row_mismatch", lambda: validate_concat_batch(misaligned_batch_provenance)))

    concat_displacement_roll = make_concat_batch([graph, other_graph])
    concat_displacement_roll["displacement"] = np.roll(concat_displacement_roll["displacement"], 1, axis=0)
    failures.append(_capture_failure("concat_displacement_row_roll", lambda: validate_concat_batch(concat_displacement_roll)))

    concat_distance_roll = make_concat_batch([graph, other_graph])
    concat_distance_roll["distance"] = np.roll(concat_distance_roll["distance"], 1, axis=0)
    failures.append(_capture_failure("concat_distance_row_roll", lambda: validate_concat_batch(concat_distance_roll)))

    concat_feature_roll = make_concat_batch([graph, other_graph])
    concat_feature_roll["edge_features"] = np.roll(concat_feature_roll["edge_features"], 1, axis=0)
    failures.append(_capture_failure("concat_edge_feature_row_roll", lambda: validate_concat_batch(concat_feature_roll)))

    padded = make_padded_batch([graph, other_graph])
    padding_leak = copy.deepcopy(padded)
    padding_positions = np.argwhere(~padding_leak["edge_mask"])
    if not padding_positions.size:
        raise AssertionError("padding fixture has no inactive edge")
    batch_index, edge_index = padding_positions[0]
    padding_leak["receiver"][batch_index, edge_index] = 0
    failures.append(_capture_failure("padding_endpoint_leak", lambda: validate_padded_batch(padding_leak)))

    discontinuous_padding = make_padded_batch([graph, other_graph])
    padding_positions = np.argwhere(~discontinuous_padding["edge_mask"])
    batch_index, edge_index = padding_positions[0]
    discontinuous_padding["edge_mask"][batch_index, edge_index] = True
    failures.append(_capture_failure("noncontiguous_edge_padding", lambda: validate_padded_batch(discontinuous_padding)))

    missing_batch_field = make_padded_batch([graph, other_graph])
    missing_batch_field.pop("shift")
    failures.append(_capture_failure("missing_padded_shift", lambda: validate_padded_batch(missing_batch_field)))

    padded_displacement_roll = make_padded_batch([graph, other_graph])
    active_edges = int(padded_displacement_roll["edge_count"][0])
    padded_displacement_roll["displacement"][0, :active_edges] = np.roll(
        padded_displacement_roll["displacement"][0, :active_edges], 1, axis=0
    )
    failures.append(_capture_failure("padded_displacement_row_roll", lambda: validate_padded_batch(padded_displacement_roll)))

    padded_distance_roll = make_padded_batch([graph, other_graph])
    padded_distance_roll["distance"][0, :active_edges] = np.roll(
        padded_distance_roll["distance"][0, :active_edges], 1, axis=0
    )
    failures.append(_capture_failure("padded_distance_row_roll", lambda: validate_padded_batch(padded_distance_roll)))

    padded_feature_roll = make_padded_batch([graph, other_graph])
    padded_feature_roll["edge_features"][0, :active_edges] = np.roll(
        padded_feature_roll["edge_features"][0, :active_edges], 1, axis=0
    )
    failures.append(_capture_failure("padded_edge_feature_row_roll", lambda: validate_padded_batch(padded_feature_roll)))

    padded_prediction_extra = make_padded_batch([graph, other_graph])
    padded_prediction_extra["prediction"] = np.concatenate(
        [padded_prediction_extra["prediction"], np.zeros((*padded_prediction_extra["prediction"].shape[:2], 1), dtype=np.float64)],
        axis=2,
    )
    failures.append(_capture_failure("padded_prediction_width_extra", lambda: validate_padded_batch(padded_prediction_extra)))

    padded_prediction_missing = make_padded_batch([graph, other_graph])
    padded_prediction_missing["prediction"] = padded_prediction_missing["prediction"][:, :, :-1]
    failures.append(_capture_failure("padded_prediction_width_missing", lambda: validate_padded_batch(padded_prediction_missing)))

    concat_cutoff_too_small = make_concat_batch([graph, other_graph])
    concat_cutoff_too_small["cutoff"][:] = 1.0e-12
    failures.append(_capture_failure("concat_cutoff_too_small", lambda: validate_concat_batch(concat_cutoff_too_small)))

    padded_cutoff_too_small = make_padded_batch([graph, other_graph])
    padded_cutoff_too_small["cutoff"][:] = 1.0e-12
    failures.append(_capture_failure("padded_cutoff_too_small", lambda: validate_padded_batch(padded_cutoff_too_small)))

    concat_singular_cell = make_concat_batch([graph, other_graph])
    concat_singular_cell["cell"][:] = 0.0
    concat_singular_cell["displacement"][:] = 0.0
    concat_singular_cell["distance"][:] = 0.0
    concat_singular_cell["edge_features"][:] = 0.0
    failures.append(_capture_failure("concat_singular_cell", lambda: validate_concat_batch(concat_singular_cell)))

    padded_singular_cell = make_padded_batch([graph, other_graph])
    padded_singular_cell["cell"][:] = 0.0
    for graph_index, count in enumerate(padded_singular_cell["edge_count"]):
        e = int(count)
        padded_singular_cell["displacement"][graph_index, :e] = 0.0
        padded_singular_cell["distance"][graph_index, :e] = 0.0
        padded_singular_cell["edge_features"][graph_index, :e] = 0.0
    failures.append(_capture_failure("padded_singular_cell", lambda: validate_padded_batch(padded_singular_cell)))

    concat_noncanonical_fractional = make_concat_batch([graph, other_graph])
    concat_noncanonical_fractional["fractional"][:, 0] += 1.0
    failures.append(_capture_failure("concat_noncanonical_fractional", lambda: validate_concat_batch(concat_noncanonical_fractional)))

    padded_rank4_node_features = make_padded_batch([graph, other_graph])
    padded_rank4_node_features["node_features"] = padded_rank4_node_features["node_features"][..., None]
    failures.append(_capture_failure("padded_rank4_node_features", lambda: validate_padded_batch(padded_rank4_node_features)))

    wrong_version = copy.deepcopy(provenance)
    wrong_version["schema_version"] = "wrong-version"
    failures.append(_capture_failure("wrong_schema_version", lambda: validate_orbital_provenance(graph, wrong_version)))

    wrong_graph_version = copy.deepcopy(graph)
    wrong_graph_version["schema_version"] = "wrong-version"
    failures.append(_capture_failure("wrong_graph_schema_version", lambda: validate_graph(wrong_graph_version)))

    missing_cache_field = copy.deepcopy(cache)
    missing_cache_field["layers"][0].pop("aggregate")
    failures.append(
        _capture_failure(
            "missing_intermediate_tensor",
            lambda: validate_mpnn_cache(
                missing_cache_field,
                node_count=graph["fractional"].shape[0],
                edge_count=graph["receiver"].shape[0],
                hidden_dim=hidden_dim,
                edge_dim=edge_dim,
                layers=layers,
            ),
        )
    )
    return failures


def _validate_schema_version(graph: dict[str, Any], provenance: dict[str, Any]) -> None:
    if graph["schema_version"] != SCHEMA_VERSION:
        raise ValueError("graph schema_version mismatch")
    if provenance["schema_version"] != SCHEMA_VERSION:
        raise ValueError("provenance schema_version mismatch")


def _run_suite(config_name: str, benchmark: bool = False) -> dict[str, Any]:
    if config_name not in CONFIGS:
        raise ValueError(f"unknown config: {config_name}")
    config = CONFIGS[config_name]
    seed = int(config["seed"])
    rng = np.random.default_rng(seed)
    graph = _main_graph()
    multi_graph = _multi_graph()

    # T-D01: group-aware split and explicit random-frame leakage counterexample.
    split = group_split_evidence(int(config["groups"]), int(config["frames"]))
    t_d01_pass = bool(split["disjoint_pass"] and split["random_frame_leakage_captured"])

    # Shared MPNN fixture for T-D02/T-D04/T-D09.
    node_features = rng.normal(size=(graph["fractional"].shape[0], int(config["hidden_dim"])))
    edge_features = _edge_features(graph, int(config["edge_dim"]))
    parameters = init_mpnn_parameters(
        rng,
        int(config["layers"]),
        int(config["hidden_dim"]),
        int(config["edge_dim"]),
        int(config["output_dim"]),
    )
    provenance = make_orbital_provenance(graph, int(config["output_dim"]))
    _validate_schema_version(graph, provenance)
    target = rng.normal(size=provenance["mask"].shape)
    gradient_error, gradient_count = finite_difference_gradient_error(
        node_features,
        edge_features,
        graph["receiver"],
        graph["sender"],
        target,
        provenance["mask"],
        parameters,
    )
    prediction, cache = forward_mpnn(node_features, edge_features, graph["receiver"], graph["sender"], parameters)
    validate_mpnn_cache(
        cache,
        node_count=node_features.shape[0],
        edge_count=edge_features.shape[0],
        hidden_dim=int(config["hidden_dim"]),
        edge_dim=int(config["edge_dim"]),
        layers=int(config["layers"]),
    )
    _, gradients = backward_mpnn(prediction, target, provenance["mask"], parameters, cache)
    flat_index = np.unravel_index(np.argmax(np.abs(gradients["Wo"])), gradients["Wo"].shape)
    epsilon = 1.0e-6
    original = float(parameters["Wo"][flat_index])
    parameters["Wo"][flat_index] = original + epsilon
    plus = masked_mse(
        forward_mpnn(node_features, edge_features, graph["receiver"], graph["sender"], parameters)[0],
        target,
        provenance["mask"],
    )[0]
    parameters["Wo"][flat_index] = original - epsilon
    minus = masked_mse(
        forward_mpnn(node_features, edge_features, graph["receiver"], graph["sender"], parameters)[0],
        target,
        provenance["mask"],
    )[0]
    parameters["Wo"][flat_index] = original
    numerical_coordinate = (plus - minus) / (2.0 * epsilon)
    analytic_coordinate = float(gradients["Wo"][flat_index])
    sign_flip_error = abs(-analytic_coordinate - numerical_coordinate) / max(
        1.0, abs(analytic_coordinate), abs(numerical_coordinate)
    )
    correct_output_gradient = 2.0 * (prediction - target) * provenance["mask"] / provenance["mask"].sum()
    padding_gradient_max = float(np.max(np.abs(correct_output_gradient[~provenance["mask"]]), initial=0.0))
    fault_results: dict[str, dict[str, Any]] = {}
    for fault_name in (
        "omit_loss_average",
        "scatter_to_sender",
        "wrong_tanh_derivative",
        "padding_gradient_leak",
    ):
        _, faulty_gradients = backward_mpnn(
            prediction,
            target,
            provenance["mask"],
            parameters,
            cache,
            fault=fault_name,
        )
        relative_error = parameter_gradient_relative_error(gradients, faulty_gradients, parameters)
        fault_results[fault_name] = {
            "detected": relative_error > 1.0e-5,
            "max_relative_error_against_fd_validated_gradient": relative_error,
            "threshold": 1.0e-5,
        }
    fault_results["output_sign_flip"] = {
        "detected": sign_flip_error > 1.0e-5,
        "max_relative_error_against_centered_coordinate": sign_flip_error,
        "threshold": 1.0e-5,
    }
    t_d02_pass = (
        gradient_error <= 1.0e-5
        and padding_gradient_max == 0.0
        and all(result["detected"] for result in fault_results.values())
    )

    # T-D03: deterministic grouped synthetic regression with a frozen test threshold.
    regression = grouped_regression(
        seed,
        int(config["groups"]),
        int(config["frames"]),
        int(config["training_steps"]),
        float(config["learning_rate"]),
        layers=int(config["layers"]),
        hidden_dim=int(config["hidden_dim"]),
        edge_dim=int(config["edge_dim"]),
        output_dim=int(config["output_dim"]),
    )
    threshold = float(config["test_mse_threshold"])
    t_d03_pass = (
        regression["final_train_mse"] < regression["initial_train_mse"]
        and regression["test_mse"] <= threshold
        and regression["test_mse"] < 0.25 * regression["test_zero_baseline_mse"]
        and regression["corrupted_test_mse"] > threshold
        and not any(regression["group_intersections"])
        and regression["frame_split_apparent_mse"] < regression["independent_group_linear_mse"]
    )

    # T-D04: node permutation plus an independent edge-row permutation and full output provenance.
    node_count = node_features.shape[0]
    base_output = make_edge_output(graph, prediction, provenance)
    permutation = np.asarray([2, 0, 3, 1], dtype=np.int64)
    inverse = np.empty_like(permutation)
    inverse[permutation] = np.arange(node_count)
    permuted_graph = build_periodic_graph(
        graph["cell"], graph["fractional"][permutation], graph["cutoff"], graph["structure_id"]
    )
    permuted_edge_features = _edge_features(permuted_graph, int(config["edge_dim"]))
    prediction_permuted, cache_permuted = forward_mpnn(
        node_features[permutation],
        permuted_edge_features,
        permuted_graph["receiver"],
        permuted_graph["sender"],
        parameters,
    )
    permuted_provenance = make_orbital_provenance(
        permuted_graph,
        int(config["output_dim"]),
        node_orbitals=[provenance["node_orbitals"][old] for old in permutation],
    )
    random_edge_rows = np.arange(permuted_graph["receiver"].shape[0], dtype=np.int64)[::-1]
    permuted_output = make_edge_output(
        permuted_graph,
        prediction_permuted,
        permuted_provenance,
        row_order=random_edge_rows,
    )
    node_residual = float(np.max(np.abs(cache_permuted["final_h"] - cache["final_h"][permutation]), initial=0.0))
    base_records = edge_output_by_key(base_output)
    permuted_records = edge_output_by_key(permuted_output)
    edge_residual = 0.0
    provenance_mapping_pass = True
    for key, record in base_records.items():
        mapped_key = (key[0], int(inverse[key[1]]), int(inverse[key[2]]), key[3], key[4], key[5])
        mapped = permuted_records[mapped_key]
        edge_residual = max(edge_residual, float(np.max(np.abs(mapped["prediction"] - record["prediction"]), initial=0.0)))
        provenance_mapping_pass = provenance_mapping_pass and all(
            np.array_equal(mapped[name], record[name])
            for name in ("block_shape", "mask", "orbital_i_index", "orbital_j_index", "orbital_i_id", "orbital_j_id")
        ) and mapped["unit"] == record["unit"]
    bad_prediction, _ = forward_mpnn(
        node_features[permutation],
        permuted_edge_features,
        graph["receiver"],
        graph["sender"],
        parameters,
    )
    bad_permutation_residual = float(np.max(np.abs(bad_prediction - prediction_permuted), initial=0.0))
    misaligned_prediction = copy.deepcopy(permuted_output)
    misaligned_prediction["prediction"] = np.roll(misaligned_prediction["prediction"], 1, axis=0)
    misaligned_prediction_residual = max(
        float(np.max(np.abs(edge_output_by_key(misaligned_prediction)[key]["prediction"] - permuted_records[key]["prediction"]), initial=0.0))
        for key in permuted_records
    )
    misaligned_mask = copy.deepcopy(permuted_output)
    misaligned_mask["mask"] = np.roll(misaligned_mask["mask"], 1, axis=0)
    misaligned_mask_failure = _capture_failure(
        "misaligned_mask_row", lambda: validate_edge_output(permuted_graph, permuted_provenance, misaligned_mask)
    )
    t_d04_pass = (
        node_residual <= 1.0e-12
        and edge_residual <= 1.0e-12
        and provenance_mapping_pass
        and bad_permutation_residual > 1.0e-6
        and misaligned_prediction_residual > 1.0e-6
        and misaligned_mask_failure["name"] == "misaligned_mask_row"
    )

    # T-D05: common and per-atom representative changes, plus a wrong fixed-shift failure.
    common_q = np.tile(np.asarray([1, -1, 2], dtype=np.int64), (node_count, 1))
    individual_q = np.asarray([[0, 0, 0], [1, -1, 0], [-2, 1, 1], [0, 2, -1]], dtype=np.int64)
    common_residuals = representative_residuals(graph, common_q)
    individual_residuals = representative_residuals(graph, individual_q)
    representative = transformed_representatives(graph, individual_q)
    canonical_keys = [
        (graph["structure_id"], int(i), int(j), int(n[0]), int(n[1]), int(n[2]))
        for i, j, n in zip(graph["receiver"], graph["sender"], graph["shift"], strict=True)
    ]
    transformed_keys = [
        (
            graph["structure_id"], int(i), int(j),
            int(n[0] - individual_q[int(i), 0] + individual_q[int(j), 0]),
            int(n[1] - individual_q[int(i), 1] + individual_q[int(j), 1]),
            int(n[2] - individual_q[int(i), 2] + individual_q[int(j), 2]),
        )
        for i, j, n in zip(graph["receiver"], graph["sender"], representative["shift_prime"], strict=True)
    ]
    canonical_lookup = {key: row for row, key in enumerate(canonical_keys)}
    representative_order = np.arange(len(transformed_keys), dtype=np.int64)[::-1]
    shuffled_transformed_keys = [transformed_keys[row] for row in representative_order]
    transformed_lookup = {key: position for position, key in enumerate(shuffled_transformed_keys)}
    transformed_prediction = base_output["prediction"][representative_order]
    transformed_mask = base_output["mask"][representative_order]
    transformed_orbital_i_id = base_output["orbital_i_id"][representative_order]
    transformed_edge_id = representative["edge_instance_id"][representative_order]
    representative_bijection_pass = (
        len(canonical_lookup) == len(canonical_keys)
        and set(canonical_lookup) == set(transformed_lookup)
        and all(
            str(transformed_edge_id[transformed_lookup[key]]) == str(base_output["edge_instance_id"][canonical_lookup[key]])
            and np.array_equal(base_output["prediction"][canonical_lookup[key]], transformed_prediction[transformed_lookup[key]])
            and np.array_equal(base_output["mask"][canonical_lookup[key]], transformed_mask[transformed_lookup[key]])
            and np.array_equal(base_output["orbital_i_id"][canonical_lookup[key]], transformed_orbital_i_id[transformed_lookup[key]])
            for key in canonical_lookup
        )
    )
    representative_row_mismatch_residual = max(
        float(np.max(np.abs(base_output["prediction"][canonical_lookup[key]] - base_output["prediction"][transformed_lookup[key]]), initial=0.0))
        for key in canonical_lookup
    )
    unwrapped = graph["fractional"] + individual_q
    wrong_displacement = (unwrapped[graph["sender"]] + graph["shift"] - unwrapped[graph["receiver"]]) @ graph["cell"]
    wrong_fixed_shift_residual = float(np.max(np.abs(wrong_displacement - graph["displacement"]), initial=0.0))
    pair_collision_count = len(graph_keys(multi_graph)) - len({key[:2] for key in graph_keys(multi_graph)})
    t_d05_pass = (
        max(common_residuals.values(), default=0.0) <= DISPLACEMENT_ATOL
        and max(individual_residuals.values(), default=0.0) <= DISPLACEMENT_ATOL
        and wrong_fixed_shift_residual > 1.0e-6
        and pair_collision_count > 0
        and representative_bijection_pass
        and representative_row_mismatch_residual > 1.0e-6
    )

    # T-D06: derived mirror box versus expanded box and known fixed-box/minimum-image failures.
    expanded_graph = build_periodic_graph(
        graph["cell"], graph["fractional"], graph["cutoff"], graph["structure_id"], extra_box=1
    )
    full_keys = graph_keys(graph)
    expanded_keys = graph_keys(expanded_graph)
    long_graph = build_periodic_graph(np.diag([1.0, 5.0, 5.0]), np.zeros((1, 3)), 2.1, "stageD-long")
    fixed_box_missed = sum(any(abs(component) > 1 for component in key[2:]) for key in graph_keys(long_graph))
    multi_pair_count = sum(
        int(i) == 0 and int(j) == 1 for i, j in zip(multi_graph["receiver"], multi_graph["sender"], strict=True)
    )
    t_d06_pass = full_keys == expanded_keys and fixed_box_missed > 0 and multi_pair_count >= 2

    # T-D07: preserve multiedges and nonzero self images; reject pair-only deduplication.
    multi_keys = graph_keys(multi_graph)
    zero_self_count = sum(i == j and n == (0, 0, 0) for i, j, *shift in multi_keys for n in [tuple(shift)])
    nonzero_self_count = sum(i == j and tuple(shift) != (0, 0, 0) for i, j, *shift in multi_keys)
    deduplicated_pair_count = len({key[:2] for key in multi_keys})
    t_d07_pass = (
        zero_self_count == 0
        and nonzero_self_count > 0
        and deduplicated_pair_count < len(multi_keys)
        and len(multi_keys) == len(set(multi_keys))
    )

    # T-D08: one-to-three layer directed predecessor support and in-place update failure.
    chain_receiver = np.asarray([1, 2, 3], dtype=np.int64)
    chain_sender = np.asarray([0, 1, 2], dtype=np.int64)
    base_values = np.asarray([1.0, 0.0, 0.0, 0.0])
    support_results = {}
    t_d08_pass = True
    for layers in (1, 2, 3):
        predicted_support = predecessor_sets(chain_receiver, chain_sender, 4, layers)
        propagated = linear_support_propagation(chain_receiver, chain_sender, base_values, layers)
        actual = set(np.flatnonzero(np.abs(propagated) > 0.0).tolist())
        expected = {node for node in range(4) if 0 in predicted_support[node]}
        support_results[str(layers)] = sorted(actual)
        t_d08_pass = t_d08_pass and actual == expected
    in_place = linear_support_propagation(chain_receiver, chain_sender, base_values, 1, in_place=True)
    in_place_bad_support = set(np.flatnonzero(np.abs(in_place) > 0.0).tolist())
    t_d08_pass = t_d08_pass and in_place_bad_support == {0, 1, 2, 3} and set(support_results["1"]) == {0, 1}

    # T-D09: full provenance, concatenated/padded batches, complexity, and targeted schema mutations.
    validate_orbital_provenance(graph, provenance)
    multi_node_features = np.linspace(
        -0.4,
        0.4,
        multi_graph["fractional"].shape[0] * int(config["hidden_dim"]),
        dtype=np.float64,
    ).reshape(multi_graph["fractional"].shape[0], int(config["hidden_dim"]))
    multi_edge_features = _edge_features(multi_graph, int(config["edge_dim"]))
    multi_prediction, _ = forward_mpnn(
        multi_node_features,
        multi_edge_features,
        multi_graph["receiver"],
        multi_graph["sender"],
        parameters,
    )
    multi_provenance = make_orbital_provenance(multi_graph, int(config["output_dim"]))
    concat_batch = make_concat_batch(
        [graph, multi_graph],
        [node_features, multi_node_features],
        [edge_features, multi_edge_features],
        [provenance, multi_provenance],
        [prediction, multi_prediction],
    )
    padded_batch = make_padded_batch(
        [graph, multi_graph],
        [node_features, multi_node_features],
        [edge_features, multi_edge_features],
        [provenance, multi_provenance],
        [prediction, multi_prediction],
    )
    validate_concat_batch(concat_batch)
    validate_padded_batch(padded_batch)
    padded_nan_sentinel_count = int(
        np.isnan(padded_batch["node_features"][~padded_batch["node_mask"]]).sum()
        + np.isnan(padded_batch["edge_features"][~padded_batch["edge_mask"]]).sum()
        + np.isnan(padded_batch["prediction"][~padded_batch["edge_mask"]]).sum()
    )
    padded_execution = forward_padded_batch(padded_batch, parameters, padded_batch["prediction"].copy())
    padded_prediction_residual = max(
        float(np.max(np.abs(actual - expected), initial=0.0))
        for actual, expected in zip(padded_execution["prediction"], (prediction, multi_prediction), strict=True)
    )
    empty_node_features = node_features[:3].copy()
    empty_edge_features = edge_features[:1].copy()
    empty_receiver = np.asarray([1], dtype=np.int64)
    empty_sender = np.asarray([0], dtype=np.int64)
    _, empty_cache = forward_mpnn(
        empty_node_features,
        empty_edge_features,
        empty_receiver,
        empty_sender,
        parameters,
    )
    validate_mpnn_cache(
        empty_cache,
        node_count=3,
        edge_count=1,
        hidden_dim=int(config["hidden_dim"]),
        edge_dim=int(config["edge_dim"]),
        layers=int(config["layers"]),
    )
    empty_incoming_zero_aggregate = all(
        np.array_equal(saved["aggregate"][[0, 2]], np.zeros((2, int(config["hidden_dim"]))))
        for saved in empty_cache["layers"]
    )
    aggregate_receiver = np.asarray([1, 1], dtype=np.int64)
    aggregate_values = np.asarray([[1.0, -2.0], [3.0, 4.0]], dtype=np.float64)
    sum_aggregate = aggregate_messages(aggregate_receiver, aggregate_values, 3, "sum")
    mean_aggregate, has_incoming = aggregate_messages(aggregate_receiver, aggregate_values, 3, "mean")
    max_empty_failure = _capture_failure(
        "max_empty_incoming", lambda: aggregate_messages(aggregate_receiver, aggregate_values, 3, "max")
    )
    empty_aggregation_contract = (
        np.array_equal(sum_aggregate[[0, 2]], np.zeros((2, 2)))
        and np.array_equal(mean_aggregate[[0, 2]], np.zeros((2, 2)))
        and np.array_equal(has_incoming, np.asarray([False, True, False]))
        and max_empty_failure["name"] == "max_empty_incoming"
    )
    t_d09_failures = _failure_t_d09(
        graph,
        multi_graph,
        provenance,
        cache,
        hidden_dim=int(config["hidden_dim"]),
        edge_dim=int(config["edge_dim"]),
        layers=int(config["layers"]),
    )
    activation_memory = activation_bytes(
        node_count, graph["receiver"].shape[0], int(config["layers"]), int(config["hidden_dim"])
    )
    t_d09_pass = (
        len(t_d09_failures) == 36
        and activation_memory > 0
        and empty_incoming_zero_aggregate
        and empty_aggregation_contract
        and padded_prediction_residual <= 1.0e-12
        and max(padded_execution["losses"], default=0.0) <= 1.0e-24
        and padded_nan_sentinel_count > 0
    )

    # T-D10: hard input validation and boundary fixtures.
    t_d10_failures: list[dict[str, str]] = []
    t_d10_failures.append(_capture_failure("nonfinite_coordinate", lambda: build_periodic_graph(np.eye(3), [[np.nan, 0, 0]], 1.0, "bad")))
    t_d10_failures.append(_capture_failure("singular_cell", lambda: validate_cell(np.diag([1.0, 1.0, 0.0]))))
    t_d10_failures.append(_capture_failure("threshold_cell", lambda: validate_cell(np.diag([1.0, 1.0, 1.0e-8]))))
    t_d10_failures.append(_capture_failure("beyond_threshold_cell", lambda: validate_cell(np.diag([1.0, 1.0, 5.0e-9]))))
    for name, value in (
        ("cutoff_nan", np.nan),
        ("cutoff_pos_inf", np.inf),
        ("cutoff_neg_inf", -np.inf),
        ("cutoff_zero", 0.0),
        ("cutoff_negative", -1.0),
    ):
        t_d10_failures.append(_capture_failure(name, lambda value=value: validate_cutoff(value)))
    out_of_range = copy.deepcopy(graph)
    out_of_range["receiver"][0] = node_count
    t_d10_failures.append(_capture_failure("endpoint_out_of_range", lambda: validate_graph(out_of_range)))
    t_d10_failures.append(_capture_failure("duplicate_record", lambda: validate_graph(_append_duplicate_record(graph))))
    contaminated_split = {
        name: np.asarray(regression["group_ids"][name], dtype=np.int64)
        for name in ("train", "validation", "test")
    }
    contaminated_split["validation"][0] = contaminated_split["train"][0]
    t_d10_failures.append(
        _capture_failure(
            "structure_group_pollution",
            lambda: validate_group_split(contaminated_split, int(config["groups"])),
        )
    )
    zero_edge_graph = build_periodic_graph(np.diag([10.0, 10.0, 10.0]), np.zeros((1, 3)), 0.1, "zero-edge")
    empty_structure_id = copy.deepcopy(zero_edge_graph)
    empty_structure_id["structure_id"] = ""
    t_d10_failures.append(_capture_failure("empty_structure_id", lambda: validate_graph(empty_structure_id)))
    float32_core = copy.deepcopy(zero_edge_graph)
    float32_core["cell"] = float32_core["cell"].astype(np.float32)
    float32_core["fractional"] = float32_core["fractional"].astype(np.float32)
    t_d10_failures.append(_capture_failure("float32_core_schema", lambda: validate_graph(float32_core)))
    bad_bounds = copy.deepcopy(zero_edge_graph)
    bad_bounds["bounds"] = np.asarray([-999, -999, -999], dtype=np.int64)
    t_d10_failures.append(_capture_failure("inconsistent_bounds", lambda: validate_graph(bad_bounds)))
    bad_candidate_count = copy.deepcopy(zero_edge_graph)
    bad_candidate_count["candidate_count"] = -1
    t_d10_failures.append(_capture_failure("inconsistent_candidate_count", lambda: validate_graph(bad_candidate_count)))
    accepted_condition = validate_cell(np.diag([1.0, 1.0, 2.0e-8]))[1]
    t_d10_pass = (
        len(t_d10_failures) == 16
        and accepted_condition < COND_LIMIT
    )

    benchmark_result: dict[str, Any]
    if benchmark:
        start = time.perf_counter()
        for repeat in range(10):
            build_periodic_graph(graph["cell"], graph["fractional"], graph["cutoff"], f"benchmark-{repeat}")
        construction_seconds = (time.perf_counter() - start) / 10.0
        start = time.perf_counter()
        for _ in range(100):
            forward_mpnn(node_features, edge_features, graph["receiver"], graph["sender"], parameters)
        forward_seconds = (time.perf_counter() - start) / 100.0
        benchmark_result = {
            "mode": "noncanonical_measured",
            "construction_seconds_per_call": construction_seconds,
            "forward_seconds_per_call": forward_seconds,
        }
    else:
        benchmark_result = {
            "mode": "disabled_in_canonical_json_for_byte_stability",
            "command": f"run_experiments.py --format json --config {config_name} --benchmark",
        }

    tests = {
        "T-D01": {
            "pass": t_d01_pass,
            **split,
            "failure": "random-frame split produces nonempty group intersections",
        },
        "T-D02": {
            "pass": t_d02_pass,
            "gradient_parameter_count": gradient_count,
            "max_relative_error": gradient_error,
            "threshold": 1.0e-5,
            "sign_flip_relative_error": sign_flip_error,
            "padding_gradient_max_abs": padding_gradient_max,
            "fault_matrix": fault_results,
        },
        "T-D03": {
            "pass": t_d03_pass,
            **regression,
            "test_mse_threshold": threshold,
            "frozen_steps": int(config["training_steps"]),
            "frozen_learning_rate": float(config["learning_rate"]),
        },
        "T-D04": {
            "pass": t_d04_pass,
            "node_max_abs_residual": node_residual,
            "edge_max_abs_residual": edge_residual,
            "threshold": 1.0e-12,
            "unmapped_edge_failure_residual": bad_permutation_residual,
            "prediction_row_mismatch_residual": misaligned_prediction_residual,
            "provenance_mapping_pass": provenance_mapping_pass,
            "edge_output_schema_version": OUTPUT_SCHEMA_VERSION,
            "captured_provenance_failure": misaligned_mask_failure,
        },
        "T-D05": {
            "pass": t_d05_pass,
            "common_translation": common_residuals,
            "per_atom_translation": individual_residuals,
            "wrong_fixed_shift_residual": wrong_fixed_shift_residual,
            "pair_only_collision_count": pair_collision_count,
            "complete_key_bijection_pass": representative_bijection_pass,
            "complete_key_count": len(canonical_lookup),
            "row_order_mismatch_residual": representative_row_mismatch_residual,
        },
        "T-D06": {
            "pass": t_d06_pass,
            "derived_edge_count": len(full_keys),
            "expanded_edge_count": len(expanded_keys),
            "fixed_small_box_missed_count": fixed_box_missed,
            "minimum_image_pair_count": multi_pair_count,
        },
        "T-D07": {
            "pass": t_d07_pass,
            "edge_count": len(multi_keys),
            "zero_self_count": zero_self_count,
            "nonzero_self_count": nonzero_self_count,
            "pair_deduplicated_count": deduplicated_pair_count,
        },
        "T-D08": {
            "pass": t_d08_pass,
            "affected_support_by_layers": support_results,
            "in_place_bad_support": sorted(in_place_bad_support),
        },
        "T-D09": {
            "pass": t_d09_pass,
            "node_count": node_count,
            "edge_count": int(graph["receiver"].shape[0]),
            "layers": int(config["layers"]),
            "hidden_dim": int(config["hidden_dim"]),
            "candidate_count": int(graph["candidate_count"]),
            "activation_bytes": activation_memory,
            "empty_incoming_zero_aggregate": empty_incoming_zero_aggregate,
            "intermediate_tensor_schema_validated": True,
            "batch_schema_version": BATCH_SCHEMA_VERSION,
            "concat_graph_count": concat_batch["graph_count"],
            "padded_prediction_max_abs_residual": padded_prediction_residual,
            "padded_nan_sentinel_count": padded_nan_sentinel_count,
            "padded_masked_losses": padded_execution["losses"],
            "padded_normalized_node_mean_max_abs": padded_execution["normalized_node_mean_max_abs"],
            "empty_aggregation_contract": empty_aggregation_contract,
            "max_empty_failure": max_empty_failure,
            "expected_failure_count": 36,
            "captured_failures": t_d09_failures,
            "benchmark": benchmark_result,
        },
        "T-D10": {
            "pass": t_d10_pass,
            "accepted_boundary_condition_number": accepted_condition,
            "condition_limit": COND_LIMIT,
            "expected_failure_count": 16,
            "captured_failures": t_d10_failures,
            "group_pollution_captured": any(item["name"] == "structure_group_pollution" for item in t_d10_failures),
        },
    }
    overall_pass = all(bool(test["pass"]) for test in tests.values())
    result = {
        "conventions_version": SCHEMA_VERSION,
        "backend": "synthetic_numpy",
        "config": config_name,
        "seed": seed,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "frozen_config": config,
        "tests": tests,
        "overall_pass": overall_pass,
        "authorization_boundary": {
            "deeph_installed": False,
            "formal_data_downloaded": False,
            "dft_labels_generated": False,
            "material_system": "UNRESOLVED_M8",
            "dft_backend": "UNRESOLVED_M8",
            "deeph_software_object": "UNRESOLVED_M8",
        },
    }
    if not overall_pass:
        failed = [test_id for test_id, value in tests.items() if not value["pass"]]
        raise AssertionError(f"stage D suite failed: {failed}")
    return _json_scalar(result)


def run_suite(config_name: str, benchmark: bool = False) -> dict[str, Any]:
    return _run_suite(config_name, benchmark=benchmark)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--config", choices=tuple(CONFIGS), default="A")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--benchmark", action="store_true")
    arguments = parser.parse_args()
    expected_seed = int(CONFIGS[arguments.config]["seed"])
    if arguments.seed is not None and arguments.seed != expected_seed:
        parser.error(f"config {arguments.config} requires seed {expected_seed}")
    try:
        result = run_suite(arguments.config, benchmark=arguments.benchmark)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False))
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(json.dumps({"overall_pass": False, "error": str(error)}, ensure_ascii=False, sort_keys=True))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
    parameter_gradient_relative_error,
