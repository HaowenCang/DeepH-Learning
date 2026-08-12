from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
from typing import Any

import numpy as np


EDGE_VERSION = "stageD-edge-v1"
SCHEMA_VERSION = "stageD-synthetic-v1"
OUTPUT_SCHEMA_VERSION = "stageD-edge-output-v1"
BATCH_SCHEMA_VERSION = "stageD-batch-v1"
EDGE_FEATURE_CONTRACT = "distance-displacement-prefix-zero-pad-v1"
COND_LIMIT = 1.0e8
DISPLACEMENT_ATOL = 1.0e-12


def _float64_array(value: Any, shape_tail: tuple[int, ...] | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if shape_tail is not None and (array.ndim < len(shape_tail) or array.shape[-len(shape_tail) :] != shape_tail):
        raise ValueError(f"expected trailing shape {shape_tail}, got {array.shape}")
    if not np.isfinite(array).all():
        raise ValueError("array must be finite")
    return array


def validate_cutoff(cutoff: Any) -> float:
    if isinstance(cutoff, (bool, np.bool_)) or not np.isscalar(cutoff):
        raise ValueError("cutoff must be a finite float64 scalar")
    value = float(np.float64(cutoff))
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError("cutoff must be finite and strictly positive")
    return value


def validate_cell(cell: Any) -> tuple[np.ndarray, float]:
    array = _float64_array(cell)
    if array.shape != (3, 3):
        raise ValueError("cell must have shape (3, 3)")
    singular_values = np.linalg.svd(array, compute_uv=False)
    if singular_values[-1] == 0.0:
        raise ValueError("cell is singular")
    condition = float(singular_values[0] / singular_values[-1])
    if not math.isfinite(condition) or condition >= COND_LIMIT:
        raise ValueError("cell is near-singular under stage D threshold")
    return array, condition


def canonicalize_fractional(fractional: Any) -> tuple[np.ndarray, np.ndarray]:
    raw = _float64_array(fractional)
    if raw.ndim != 2 or raw.shape[1] != 3:
        raise ValueError("fractional coordinates must have shape (N, 3)")
    representatives = np.floor(raw).astype(np.int64)
    canonical = raw - representatives
    if not ((canonical >= 0.0) & (canonical < 1.0)).all():
        raise ValueError("canonicalization failed")
    return canonical, representatives


def mirror_bounds(cell: Any, cutoff: Any) -> np.ndarray:
    array, _ = validate_cell(cell)
    radius = validate_cutoff(cutoff)
    inverse = np.linalg.inv(array)
    return np.ceil(radius * np.linalg.norm(inverse, axis=0) + 1.0).astype(np.int64)


def canonical_edge_payload(structure_id: str, receiver: int, sender: int, shift: Any) -> str:
    if not isinstance(structure_id, str) or not structure_id:
        raise ValueError("structure_id must be a non-empty string")
    n = np.asarray(shift)
    if n.shape != (3,) or not np.issubdtype(n.dtype, np.integer):
        raise ValueError("shift must be an integer vector of shape (3,)")
    payload = [EDGE_VERSION, structure_id, int(receiver), int(sender), *[int(x) for x in n]]
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def edge_instance_id(structure_id: str, receiver: int, sender: int, shift: Any) -> str:
    payload = canonical_edge_payload(structure_id, receiver, sender, shift)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def edge_features_from_geometry(graph: dict[str, Any], edge_dim: int) -> np.ndarray:
    if isinstance(edge_dim, (bool, np.bool_)) or not isinstance(edge_dim, (int, np.integer)) or int(edge_dim) <= 0:
        raise ValueError("edge_dim must be a positive integer")
    validate_graph(graph)
    base = np.concatenate([graph["distance"][:, None], graph["displacement"]], axis=1)
    if int(edge_dim) <= base.shape[1]:
        return base[:, : int(edge_dim)].copy()
    padding = np.zeros((base.shape[0], int(edge_dim) - base.shape[1]), dtype=np.float64)
    return np.concatenate([base, padding], axis=1)


def build_periodic_graph(
    cell: Any,
    fractional: Any,
    cutoff: Any,
    structure_id: str,
    *,
    extra_box: int = 0,
) -> dict[str, Any]:
    array, condition = validate_cell(cell)
    radius = validate_cutoff(cutoff)
    coordinates = _float64_array(fractional)
    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError("fractional coordinates must have shape (N, 3)")
    if not ((coordinates >= 0.0) & (coordinates < 1.0)).all():
        raise ValueError("serialized fractional coordinates must be canonical")
    if not isinstance(extra_box, int) or extra_box < 0:
        raise ValueError("extra_box must be a nonnegative integer")
    bounds = mirror_bounds(array, radius) + extra_box
    candidates = int(coordinates.shape[0] ** 2 * np.prod(2 * bounds + 1))
    records: list[tuple[int, int, tuple[int, int, int], np.ndarray, float, str]] = []
    ranges = [range(-int(bound), int(bound) + 1) for bound in bounds]
    for receiver in range(coordinates.shape[0]):
        for sender in range(coordinates.shape[0]):
            for shift_tuple in itertools.product(*ranges):
                shift = np.asarray(shift_tuple, dtype=np.int64)
                displacement = (coordinates[sender] + shift - coordinates[receiver]) @ array
                distance = float(np.linalg.norm(displacement))
                if 0.0 < distance <= radius:
                    identity = edge_instance_id(structure_id, receiver, sender, shift)
                    records.append((receiver, sender, tuple(int(x) for x in shift), displacement, distance, identity))
    records.sort(key=lambda item: (item[0], item[1], *item[2]))
    receivers = np.asarray([record[0] for record in records], dtype=np.int64)
    senders = np.asarray([record[1] for record in records], dtype=np.int64)
    shifts = np.asarray([record[2] for record in records], dtype=np.int64).reshape(-1, 3)
    displacements = np.asarray([record[3] for record in records], dtype=np.float64).reshape(-1, 3)
    distances = np.asarray([record[4] for record in records], dtype=np.float64)
    identities = np.asarray([record[5] for record in records], dtype="<U64")
    graph = {
        "schema_version": SCHEMA_VERSION,
        "structure_id": structure_id,
        "cell": array,
        "fractional": coordinates,
        "cutoff": radius,
        "condition_number": condition,
        "bounds": bounds.astype(np.int64),
        "candidate_count": candidates,
        "extra_box": extra_box,
        "receiver": receivers,
        "sender": senders,
        "shift": shifts,
        "displacement": displacements,
        "distance": distances,
        "edge_instance_id": identities,
    }
    validate_graph(graph)
    return graph


def graph_keys(graph: dict[str, Any]) -> list[tuple[int, int, int, int, int]]:
    return [
        (int(i), int(j), int(n[0]), int(n[1]), int(n[2]))
        for i, j, n in zip(graph["receiver"], graph["sender"], graph["shift"], strict=True)
    ]


def validate_graph(graph: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "structure_id",
        "cell",
        "fractional",
        "cutoff",
        "receiver",
        "sender",
        "shift",
        "displacement",
        "distance",
        "edge_instance_id",
        "condition_number",
        "bounds",
        "candidate_count",
        "extra_box",
    }
    missing = required.difference(graph)
    if missing:
        raise ValueError(f"missing graph fields: {sorted(missing)}")
    if graph["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported graph schema_version: {graph['schema_version']!r}; "
            f"expected {SCHEMA_VERSION!r}"
        )
    if not isinstance(graph["structure_id"], str) or not graph["structure_id"]:
        raise ValueError("structure_id must be a non-empty string")
    raw_cell = np.asarray(graph["cell"])
    raw_fractional = np.asarray(graph["fractional"])
    if raw_cell.dtype != np.float64 or raw_fractional.dtype != np.float64:
        raise ValueError("cell and fractional coordinates must be float64")
    cell, expected_condition = validate_cell(raw_cell)
    radius = validate_cutoff(graph["cutoff"])
    fractional = _float64_array(raw_fractional)
    if fractional.ndim != 2 or fractional.shape[1] != 3 or not ((fractional >= 0) & (fractional < 1)).all():
        raise ValueError("fractional coordinates violate canonical schema")
    receiver = np.asarray(graph["receiver"])
    sender = np.asarray(graph["sender"])
    shift = np.asarray(graph["shift"])
    displacement = np.asarray(graph["displacement"])
    distance = np.asarray(graph["distance"])
    identities = np.asarray(graph["edge_instance_id"])
    edge_count = receiver.shape[0]
    if receiver.dtype != np.int64 or sender.dtype != np.int64 or shift.dtype != np.int64:
        raise ValueError("receiver, sender, and shift must be int64")
    if displacement.dtype != np.float64 or distance.dtype != np.float64:
        raise ValueError("edge displacement and distance must be float64")
    if isinstance(graph["extra_box"], (bool, np.bool_)) or not isinstance(graph["extra_box"], (int, np.integer)):
        raise ValueError("extra_box must be a nonnegative integer")
    extra_box = int(graph["extra_box"])
    if extra_box < 0:
        raise ValueError("extra_box must be a nonnegative integer")
    bounds = np.asarray(graph["bounds"])
    expected_bounds = mirror_bounds(cell, radius) + extra_box
    if bounds.dtype != np.int64 or bounds.shape != (3,) or not np.array_equal(bounds, expected_bounds):
        raise ValueError("bounds do not match the cell, cutoff, and extra_box")
    candidate_count = graph["candidate_count"]
    expected_candidates = int(fractional.shape[0] ** 2 * np.prod(2 * expected_bounds + 1))
    if isinstance(candidate_count, (bool, np.bool_)) or not isinstance(candidate_count, (int, np.integer)) or int(candidate_count) != expected_candidates:
        raise ValueError("candidate_count is inconsistent with the enumeration box")
    condition_number = graph["condition_number"]
    if not isinstance(condition_number, (float, np.floating)) or not math.isfinite(float(condition_number)) or not math.isclose(float(condition_number), expected_condition, rel_tol=1.0e-12, abs_tol=0.0):
        raise ValueError("condition_number is inconsistent with the cell")
    if receiver.shape != (edge_count,) or sender.shape != (edge_count,) or shift.shape != (edge_count, 3):
        raise ValueError("edge index shapes are invalid")
    if displacement.shape != (edge_count, 3) or distance.shape != (edge_count,) or identities.shape != (edge_count,):
        raise ValueError("edge value shapes are invalid")
    if edge_count and (
        receiver.min() < 0
        or sender.min() < 0
        or receiver.max() >= fractional.shape[0]
        or sender.max() >= fractional.shape[0]
    ):
        raise ValueError("edge endpoint out of range")
    if not np.isfinite(displacement).all() or not np.isfinite(distance).all():
        raise ValueError("edge geometry must be finite")
    expected = (fractional[sender] + shift - fractional[receiver]) @ cell
    if not np.allclose(expected, displacement, rtol=0.0, atol=DISPLACEMENT_ATOL):
        raise ValueError("edge displacement does not match endpoints and shift")
    expected_distance = np.linalg.norm(displacement, axis=1)
    if not np.allclose(expected_distance, distance, rtol=0.0, atol=DISPLACEMENT_ATOL):
        raise ValueError("edge distance mismatch")
    if edge_count and (np.any(distance <= 0.0) or np.any(distance > radius)):
        raise ValueError("edge violates cutoff")
    keys = graph_keys(graph)
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise ValueError("edge keys must be unique and stably sorted")
    expected_ids = [
        edge_instance_id(graph["structure_id"], i, j, n)
        for i, j, n in zip(receiver, sender, shift, strict=True)
    ]
    if list(identities) != expected_ids or len(expected_ids) != len(set(expected_ids)):
        raise ValueError("edge_instance_id mismatch or collision")


def transformed_representatives(graph: dict[str, Any], q: Any) -> dict[str, Any]:
    validate_graph(graph)
    integer_q = np.asarray(q)
    if integer_q.dtype != np.int64 or integer_q.shape != graph["fractional"].shape:
        raise ValueError("q must be int64 with shape (N, 3)")
    receiver = graph["receiver"]
    sender = graph["sender"]
    shift_prime = graph["shift"] + integer_q[receiver] - integer_q[sender]
    unwrapped = graph["fractional"] + integer_q
    displacement = (unwrapped[sender] + shift_prime - unwrapped[receiver]) @ graph["cell"]
    canonical_shift = shift_prime - integer_q[receiver] + integer_q[sender]
    identities = np.asarray(
        [
            edge_instance_id(graph["structure_id"], i, j, n)
            for i, j, n in zip(receiver, sender, canonical_shift, strict=True)
        ],
        dtype="<U64",
    )
    return {
        "unwrapped_fractional": unwrapped,
        "shift_prime": shift_prime.astype(np.int64),
        "canonical_shift": canonical_shift.astype(np.int64),
        "displacement": displacement,
        "distance": np.linalg.norm(displacement, axis=1),
        "edge_instance_id": identities,
    }


def representative_residuals(graph: dict[str, Any], q: Any) -> dict[str, float]:
    transformed = transformed_representatives(graph, q)
    if not np.array_equal(transformed["canonical_shift"], graph["shift"]):
        raise AssertionError("canonical shifts do not match")
    if not np.array_equal(transformed["edge_instance_id"], graph["edge_instance_id"]):
        raise AssertionError("canonical edge IDs do not match")
    return {
        "displacement_max_abs": float(np.max(np.abs(transformed["displacement"] - graph["displacement"]), initial=0.0)),
        "distance_max_abs": float(np.max(np.abs(transformed["distance"] - graph["distance"]), initial=0.0)),
    }


def init_mpnn_parameters(
    rng: np.random.Generator,
    layers: int,
    hidden_dim: int,
    edge_dim: int,
    output_dim: int,
) -> dict[str, Any]:
    if layers not in (1, 2, 3) or min(hidden_dim, edge_dim, output_dim) <= 0:
        raise ValueError("invalid network dimensions")
    scale = 0.2
    layer_parameters = []
    for _ in range(layers):
        layer_parameters.append(
            {
                "Wr": rng.normal(scale=scale, size=(hidden_dim, hidden_dim)),
                "Ws": rng.normal(scale=scale, size=(hidden_dim, hidden_dim)),
                "Wf": rng.normal(scale=scale, size=(edge_dim, hidden_dim)),
                "bm": rng.normal(scale=scale, size=hidden_dim),
                "Uh": rng.normal(scale=scale, size=(hidden_dim, hidden_dim)),
                "Ua": rng.normal(scale=scale, size=(hidden_dim, hidden_dim)),
                "bu": rng.normal(scale=scale, size=hidden_dim),
            }
        )
    return {
        "layers": layer_parameters,
        "Wo": rng.normal(scale=scale, size=(2 * hidden_dim + edge_dim, output_dim)),
        "bo": rng.normal(scale=scale, size=output_dim),
    }


def forward_mpnn(
    node_features: Any,
    edge_features: Any,
    receiver: Any,
    sender: Any,
    parameters: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    h = _float64_array(node_features)
    edge = _float64_array(edge_features)
    receiver = np.asarray(receiver)
    sender = np.asarray(sender)
    if h.ndim != 2 or edge.ndim != 2 or receiver.shape != sender.shape or receiver.shape != (edge.shape[0],):
        raise ValueError("invalid MPNN input shapes")
    if receiver.dtype != np.int64 or sender.dtype != np.int64:
        raise ValueError("MPNN endpoints must be int64")
    if receiver.size and (receiver.min() < 0 or sender.min() < 0 or receiver.max() >= h.shape[0] or sender.max() >= h.shape[0]):
        raise ValueError("MPNN endpoint out of range")
    layer_cache = []
    for layer in parameters["layers"]:
        z_message = h[receiver] @ layer["Wr"] + h[sender] @ layer["Ws"] + edge @ layer["Wf"] + layer["bm"]
        message = np.tanh(z_message)
        aggregate = np.zeros_like(h)
        np.add.at(aggregate, receiver, message)
        z_update = h @ layer["Uh"] + aggregate @ layer["Ua"] + layer["bu"]
        h_next = np.tanh(z_update)
        layer_cache.append(
            {
                "h": h,
                "z_message": z_message,
                "message": message,
                "aggregate": aggregate,
                "z_update": z_update,
                "h_next": h_next,
            }
        )
        h = h_next
    head_input = np.concatenate([h[receiver], h[sender], edge], axis=1)
    prediction = head_input @ parameters["Wo"] + parameters["bo"]
    return prediction, {
        "layers": layer_cache,
        "final_h": h,
        "head_input": head_input,
        "edge_features": edge,
        "receiver": receiver,
        "sender": sender,
    }


def validate_mpnn_cache(
    cache: dict[str, Any],
    *,
    node_count: int,
    edge_count: int,
    hidden_dim: int,
    edge_dim: int,
    layers: int,
) -> None:
    required = {"layers", "final_h", "head_input", "edge_features", "receiver", "sender"}
    missing = required.difference(cache)
    if missing:
        raise ValueError(f"missing MPNN cache fields: {sorted(missing)}")
    receiver = np.asarray(cache["receiver"])
    sender = np.asarray(cache["sender"])
    edge_features = np.asarray(cache["edge_features"])
    final_h = np.asarray(cache["final_h"])
    head_input = np.asarray(cache["head_input"])
    if receiver.dtype != np.int64 or sender.dtype != np.int64:
        raise ValueError("cached endpoints must be int64")
    if receiver.shape != (edge_count,) or sender.shape != (edge_count,):
        raise ValueError("cached endpoint shape mismatch")
    expected_float_shapes = {
        "edge_features": (edge_features, (edge_count, edge_dim)),
        "final_h": (final_h, (node_count, hidden_dim)),
        "head_input": (head_input, (edge_count, 2 * hidden_dim + edge_dim)),
    }
    for name, (array, shape) in expected_float_shapes.items():
        if array.dtype != np.float64 or array.shape != shape or not np.isfinite(array).all():
            raise ValueError(f"cached {name} violates float64 finite schema")
    layer_cache = cache["layers"]
    if not isinstance(layer_cache, list) or len(layer_cache) != layers:
        raise ValueError("cached layer count mismatch")
    layer_shapes = {
        "h": (node_count, hidden_dim),
        "z_message": (edge_count, hidden_dim),
        "message": (edge_count, hidden_dim),
        "aggregate": (node_count, hidden_dim),
        "z_update": (node_count, hidden_dim),
        "h_next": (node_count, hidden_dim),
    }
    for layer_index, saved in enumerate(layer_cache):
        if not isinstance(saved, dict):
            raise ValueError(f"cached layer {layer_index} must be a mapping")
        missing_layer = set(layer_shapes).difference(saved)
        if missing_layer:
            raise ValueError(
                f"cached layer {layer_index} missing fields: {sorted(missing_layer)}"
            )
        for name, shape in layer_shapes.items():
            array = np.asarray(saved[name])
            if array.dtype != np.float64 or array.shape != shape or not np.isfinite(array).all():
                raise ValueError(
                    f"cached layer {layer_index}.{name} violates float64 finite schema"
                )


def masked_mse(prediction: Any, target: Any, mask: Any) -> tuple[float, np.ndarray]:
    prediction = _float64_array(prediction)
    target = _float64_array(target)
    boolean_mask = np.asarray(mask)
    if prediction.shape != target.shape or boolean_mask.shape != prediction.shape or boolean_mask.dtype != np.bool_:
        raise ValueError("prediction, target, and boolean mask shapes must match")
    valid = int(boolean_mask.sum())
    if valid <= 0:
        raise ValueError("mask must contain at least one valid element")
    residual = (prediction - target) * boolean_mask
    loss = float(np.sum(residual * residual) / valid)
    gradient = 2.0 * residual / valid
    return loss, gradient


def backward_mpnn(
    prediction: Any,
    target: Any,
    mask: Any,
    parameters: dict[str, Any],
    cache: dict[str, Any],
    *,
    fault: str | None = None,
) -> tuple[float, dict[str, Any]]:
    loss, d_prediction = masked_mse(prediction, target, mask)
    allowed_faults = {None, "omit_loss_average", "scatter_to_sender", "wrong_tanh_derivative", "padding_gradient_leak"}
    if fault not in allowed_faults:
        raise ValueError(f"unknown backward fault: {fault}")
    if fault == "omit_loss_average":
        d_prediction = d_prediction * int(np.asarray(mask).sum())
    elif fault == "padding_gradient_leak":
        d_prediction = 2.0 * (_float64_array(prediction) - _float64_array(target)) / int(np.asarray(mask).sum())
    receiver = cache["receiver"]
    sender = cache["sender"]
    hidden_dim = cache["final_h"].shape[1]
    gradients: dict[str, Any] = {
        "layers": [None] * len(parameters["layers"]),
        "Wo": cache["head_input"].T @ d_prediction,
        "bo": d_prediction.sum(axis=0),
    }
    d_head = d_prediction @ parameters["Wo"].T
    d_h = np.zeros_like(cache["final_h"])
    np.add.at(d_h, receiver, d_head[:, :hidden_dim])
    np.add.at(d_h, sender, d_head[:, hidden_dim : 2 * hidden_dim])
    d_edge = d_head[:, 2 * hidden_dim :]
    for layer_index in range(len(parameters["layers"]) - 1, -1, -1):
        layer = parameters["layers"][layer_index]
        saved = cache["layers"][layer_index]
        if fault == "wrong_tanh_derivative":
            d_z_update = d_h * (1.0 - saved["h_next"])
        else:
            d_z_update = d_h * (1.0 - saved["h_next"] * saved["h_next"])
        layer_gradient = {
            "Uh": saved["h"].T @ d_z_update,
            "Ua": saved["aggregate"].T @ d_z_update,
            "bu": d_z_update.sum(axis=0),
        }
        d_h_previous = d_z_update @ layer["Uh"].T
        d_aggregate = d_z_update @ layer["Ua"].T
        scatter_endpoint = sender if fault == "scatter_to_sender" else receiver
        d_message = d_aggregate[scatter_endpoint]
        if fault == "wrong_tanh_derivative":
            d_z_message = d_message * (1.0 - saved["message"])
        else:
            d_z_message = d_message * (1.0 - saved["message"] * saved["message"])
        layer_gradient.update(
            {
                "Wr": saved["h"][receiver].T @ d_z_message,
                "Ws": saved["h"][sender].T @ d_z_message,
                "Wf": cache["edge_features"].T @ d_z_message,
                "bm": d_z_message.sum(axis=0),
            }
        )
        np.add.at(d_h_previous, scatter_endpoint, d_z_message @ layer["Wr"].T)
        np.add.at(d_h_previous, sender, d_z_message @ layer["Ws"].T)
        d_edge = d_edge + d_z_message @ layer["Wf"].T
        gradients["layers"][layer_index] = layer_gradient
        d_h = d_h_previous
    gradients["node_features"] = d_h
    gradients["edge_features"] = d_edge
    return loss, gradients


def iter_parameter_arrays(parameters: dict[str, Any]):
    for layer_index, layer in enumerate(parameters["layers"]):
        for name in ("Wr", "Ws", "Wf", "bm", "Uh", "Ua", "bu"):
            yield ("layers", layer_index, name), layer[name]
    yield ("Wo",), parameters["Wo"]
    yield ("bo",), parameters["bo"]


def get_nested(mapping: dict[str, Any], path: tuple[Any, ...]) -> np.ndarray:
    value: Any = mapping
    for part in path:
        value = value[part]
    return value


def parameter_gradient_relative_error(
    reference: dict[str, Any],
    candidate: dict[str, Any],
    parameters: dict[str, Any],
) -> float:
    maximum = 0.0
    for path, _ in iter_parameter_arrays(parameters):
        reference_array = np.asarray(get_nested(reference, path))
        candidate_array = np.asarray(get_nested(candidate, path))
        denominator = np.maximum(1.0, np.maximum(np.abs(reference_array), np.abs(candidate_array)))
        maximum = max(maximum, float(np.max(np.abs(reference_array - candidate_array) / denominator, initial=0.0)))
    return maximum


def finite_difference_gradient_error(
    node_features: np.ndarray,
    edge_features: np.ndarray,
    receiver: np.ndarray,
    sender: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
    parameters: dict[str, Any],
    epsilon: float = 1.0e-6,
    *,
    fault: str | None = None,
) -> tuple[float, int]:
    prediction, cache = forward_mpnn(node_features, edge_features, receiver, sender, parameters)
    _, analytic = backward_mpnn(prediction, target, mask, parameters, cache, fault=fault)
    maximum = 0.0
    count = 0
    for path, array in iter_parameter_arrays(parameters):
        analytic_array = get_nested(analytic, path)
        for index in np.ndindex(array.shape):
            original = float(array[index])
            array[index] = original + epsilon
            plus = masked_mse(forward_mpnn(node_features, edge_features, receiver, sender, parameters)[0], target, mask)[0]
            array[index] = original - epsilon
            minus = masked_mse(forward_mpnn(node_features, edge_features, receiver, sender, parameters)[0], target, mask)[0]
            array[index] = original
            numerical = (plus - minus) / (2.0 * epsilon)
            denominator = max(1.0, abs(numerical), abs(float(analytic_array[index])))
            maximum = max(maximum, abs(numerical - float(analytic_array[index])) / denominator)
            count += 1
    return maximum, count


def predecessor_sets(receiver: Any, sender: Any, node_count: int, layers: int) -> list[set[int]]:
    receiver = np.asarray(receiver, dtype=np.int64)
    sender = np.asarray(sender, dtype=np.int64)
    supports = [{node} for node in range(node_count)]
    for _ in range(layers):
        previous = [set(values) for values in supports]
        updated = [set(values) for values in previous]
        for i, j in zip(receiver, sender, strict=True):
            updated[int(i)].update(previous[int(j)])
        supports = updated
    return supports


def linear_support_propagation(receiver: Any, sender: Any, values: Any, layers: int, *, in_place: bool = False) -> np.ndarray:
    receiver = np.asarray(receiver, dtype=np.int64)
    sender = np.asarray(sender, dtype=np.int64)
    state = np.asarray(values, dtype=np.float64).copy()
    for _ in range(layers):
        if in_place:
            for i, j in zip(receiver, sender, strict=True):
                state[int(i)] += state[int(j)]
        else:
            previous = state.copy()
            aggregate = np.zeros_like(state)
            np.add.at(aggregate, receiver, previous[sender])
            state = previous + aggregate
    return state


def make_orbital_provenance(
    graph: dict[str, Any],
    output_dim: int,
    *,
    node_orbitals: list[list[str]] | None = None,
) -> dict[str, Any]:
    validate_graph(graph)
    if node_orbitals is None:
        node_orbitals = [
            [f"syn:{node}:{orbital}" for orbital in range(1 + node % 2)]
            for node in range(graph["fractional"].shape[0])
        ]
    else:
        node_orbitals = copy.deepcopy(node_orbitals)
    required = [
        len(node_orbitals[int(i)]) * len(node_orbitals[int(j)])
        for i, j in zip(graph["receiver"], graph["sender"], strict=True)
    ]
    if required and output_dim < max(required):
        raise ValueError("output_dim is smaller than a block")
    edge_count = graph["receiver"].shape[0]
    block_shape = np.zeros((edge_count, 2), dtype=np.int64)
    mask = np.zeros((edge_count, output_dim), dtype=np.bool_)
    i_index = np.full((edge_count, output_dim), -1, dtype=np.int64)
    j_index = np.full((edge_count, output_dim), -1, dtype=np.int64)
    i_id = np.full((edge_count, output_dim), "", dtype="<U32")
    j_id = np.full((edge_count, output_dim), "", dtype="<U32")
    for edge_index, (i, j) in enumerate(zip(graph["receiver"], graph["sender"], strict=True)):
        orbitals_i = node_orbitals[int(i)]
        orbitals_j = node_orbitals[int(j)]
        block_shape[edge_index] = (len(orbitals_i), len(orbitals_j))
        for flat_index in range(len(orbitals_i) * len(orbitals_j)):
            alpha, beta = divmod(flat_index, len(orbitals_j))
            mask[edge_index, flat_index] = True
            i_index[edge_index, flat_index] = alpha
            j_index[edge_index, flat_index] = beta
            i_id[edge_index, flat_index] = orbitals_i[alpha]
            j_id[edge_index, flat_index] = orbitals_j[beta]
    result = {
        "schema_version": SCHEMA_VERSION,
        "node_orbitals": node_orbitals,
        "block_shape": block_shape,
        "mask": mask,
        "orbital_i_index": i_index,
        "orbital_j_index": j_index,
        "orbital_i_id": i_id,
        "orbital_j_id": j_id,
    }
    validate_orbital_provenance(graph, result)
    return result


def validate_orbital_provenance(graph: dict[str, Any], provenance: dict[str, Any]) -> None:
    validate_graph(graph)
    required = {
        "schema_version",
        "node_orbitals",
        "block_shape",
        "mask",
        "orbital_i_index",
        "orbital_j_index",
        "orbital_i_id",
        "orbital_j_id",
    }
    missing = required.difference(provenance)
    if missing:
        raise ValueError(f"missing provenance fields: {sorted(missing)}")
    if provenance["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported orbital-provenance schema_version: "
            f"{provenance['schema_version']!r}; expected {SCHEMA_VERSION!r}"
        )
    edge_count = graph["receiver"].shape[0]
    mask = np.asarray(provenance["mask"])
    if mask.dtype != np.bool_ or mask.ndim != 2 or mask.shape[0] != edge_count:
        raise ValueError("mask must be bool[E, Pmax]")
    output_dim = mask.shape[1]
    block_shape = np.asarray(provenance["block_shape"])
    i_index = np.asarray(provenance["orbital_i_index"])
    j_index = np.asarray(provenance["orbital_j_index"])
    i_id = np.asarray(provenance["orbital_i_id"])
    j_id = np.asarray(provenance["orbital_j_id"])
    if block_shape.dtype != np.int64 or block_shape.shape != (edge_count, 2):
        raise ValueError("block_shape must be int64[E,2]")
    if i_index.dtype != np.int64 or j_index.dtype != np.int64:
        raise ValueError("orbital indices must be int64")
    if i_index.shape != mask.shape or j_index.shape != mask.shape or i_id.shape != mask.shape or j_id.shape != mask.shape:
        raise ValueError("orbital component arrays must match mask")
    node_orbitals = provenance["node_orbitals"]
    if not isinstance(node_orbitals, list) or len(node_orbitals) != graph["fractional"].shape[0]:
        raise ValueError("node_orbitals must cover every node")
    for edge_index, (i, j) in enumerate(zip(graph["receiver"], graph["sender"], strict=True)):
        orbitals_i = node_orbitals[int(i)]
        orbitals_j = node_orbitals[int(j)]
        expected_count = len(orbitals_i) * len(orbitals_j)
        if output_dim < expected_count or tuple(block_shape[edge_index]) != (len(orbitals_i), len(orbitals_j)):
            raise ValueError("block shape or Pmax mismatch")
        expected_mask = np.arange(output_dim) < expected_count
        if not np.array_equal(mask[edge_index], expected_mask):
            raise ValueError("mask must be a right-padded contiguous prefix")
        for flat_index in range(output_dim):
            if flat_index < expected_count:
                alpha, beta = divmod(flat_index, len(orbitals_j))
                expected = (alpha, beta, orbitals_i[alpha], orbitals_j[beta])
            else:
                expected = (-1, -1, "", "")
            actual = (
                int(i_index[edge_index, flat_index]),
                int(j_index[edge_index, flat_index]),
                str(i_id[edge_index, flat_index]),
                str(j_id[edge_index, flat_index]),
            )
            if actual != expected:
                raise ValueError("orbital identity does not resolve from endpoint tables")


def make_edge_output(
    graph: dict[str, Any],
    prediction: Any,
    provenance: dict[str, Any],
    *,
    unit: str = "synthetic_dimensionless",
    row_order: Any | None = None,
) -> dict[str, Any]:
    validate_orbital_provenance(graph, provenance)
    prediction_array = np.asarray(prediction)
    if prediction_array.dtype != np.float64 or prediction_array.shape != provenance["mask"].shape or not np.isfinite(prediction_array).all():
        raise ValueError("prediction must be finite float64[E,Pmax]")
    if not isinstance(unit, str) or not unit:
        raise ValueError("unit must be a non-empty string")
    edge_count = graph["receiver"].shape[0]
    if row_order is None:
        order = np.arange(edge_count, dtype=np.int64)
    else:
        order = np.asarray(row_order)
        if order.dtype != np.int64 or order.shape != (edge_count,) or set(order.tolist()) != set(range(edge_count)):
            raise ValueError("row_order must be an int64 edge permutation")
    output = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "source_graph_schema_version": SCHEMA_VERSION,
        "structure_id": graph["structure_id"],
        "unit": unit,
        "receiver": graph["receiver"][order].copy(),
        "sender": graph["sender"][order].copy(),
        "shift": graph["shift"][order].copy(),
        "edge_instance_id": graph["edge_instance_id"][order].copy(),
        "prediction": prediction_array[order].copy(),
        "block_shape": provenance["block_shape"][order].copy(),
        "mask": provenance["mask"][order].copy(),
        "orbital_i_index": provenance["orbital_i_index"][order].copy(),
        "orbital_j_index": provenance["orbital_j_index"][order].copy(),
        "orbital_i_id": provenance["orbital_i_id"][order].copy(),
        "orbital_j_id": provenance["orbital_j_id"][order].copy(),
        "node_orbitals": copy.deepcopy(provenance["node_orbitals"]),
    }
    validate_edge_output(graph, provenance, output)
    return output


def validate_edge_output(
    graph: dict[str, Any],
    provenance: dict[str, Any],
    output: dict[str, Any],
) -> None:
    validate_orbital_provenance(graph, provenance)
    required = {
        "schema_version", "source_graph_schema_version", "structure_id", "unit",
        "receiver", "sender", "shift", "edge_instance_id", "prediction",
        "block_shape", "mask", "orbital_i_index", "orbital_j_index",
        "orbital_i_id", "orbital_j_id", "node_orbitals",
    }
    missing = required.difference(output)
    if missing:
        raise ValueError(f"missing edge-output fields: {sorted(missing)}")
    if output["schema_version"] != OUTPUT_SCHEMA_VERSION or output["source_graph_schema_version"] != SCHEMA_VERSION:
        raise ValueError("edge-output schema version mismatch")
    if output["structure_id"] != graph["structure_id"] or not isinstance(output["unit"], str) or not output["unit"]:
        raise ValueError("edge-output identity or unit mismatch")
    edge_count = graph["receiver"].shape[0]
    receiver = np.asarray(output["receiver"])
    sender = np.asarray(output["sender"])
    shift = np.asarray(output["shift"])
    prediction = np.asarray(output["prediction"])
    mask = np.asarray(output["mask"])
    block_shape = np.asarray(output["block_shape"])
    i_index = np.asarray(output["orbital_i_index"])
    j_index = np.asarray(output["orbital_j_index"])
    i_id = np.asarray(output["orbital_i_id"])
    j_id = np.asarray(output["orbital_j_id"])
    identities = np.asarray(output["edge_instance_id"])
    expected_component_shape = provenance["mask"].shape
    if receiver.dtype != np.int64 or sender.dtype != np.int64 or shift.dtype != np.int64:
        raise ValueError("edge-output endpoints and shift must be int64")
    if receiver.shape != (edge_count,) or sender.shape != (edge_count,) or shift.shape != (edge_count, 3):
        raise ValueError("edge-output key shapes mismatch")
    if prediction.dtype != np.float64 or prediction.shape != expected_component_shape or not np.isfinite(prediction).all():
        raise ValueError("edge-output prediction violates float64 finite schema")
    if mask.dtype != np.bool_ or mask.shape != expected_component_shape or block_shape.dtype != np.int64 or block_shape.shape != (edge_count, 2):
        raise ValueError("edge-output mask or block shape schema mismatch")
    if any(array.shape != expected_component_shape for array in (i_index, j_index, i_id, j_id)) or i_index.dtype != np.int64 or j_index.dtype != np.int64:
        raise ValueError("edge-output orbital component schema mismatch")
    if identities.shape != (edge_count,):
        raise ValueError("edge-output edge ID shape mismatch")
    keys = [(int(i), int(j), int(n[0]), int(n[1]), int(n[2])) for i, j, n in zip(receiver, sender, shift, strict=True)]
    if len(keys) != len(set(keys)):
        raise ValueError("edge-output keys must be unique")
    graph_lookup = {key: index for index, key in enumerate(graph_keys(graph))}
    if set(keys) != set(graph_lookup):
        raise ValueError("edge-output keys do not bijectively cover graph edges")
    if output["node_orbitals"] != provenance["node_orbitals"]:
        raise ValueError("edge-output node orbital table mismatch")
    for row, key in enumerate(keys):
        source = graph_lookup[key]
        if str(identities[row]) != str(graph["edge_instance_id"][source]):
            raise ValueError("edge-output edge ID does not match its complete key")
        for name, array, expected in (
            ("block_shape", block_shape, provenance["block_shape"]),
            ("mask", mask, provenance["mask"]),
            ("orbital_i_index", i_index, provenance["orbital_i_index"]),
            ("orbital_j_index", j_index, provenance["orbital_j_index"]),
            ("orbital_i_id", i_id, provenance["orbital_i_id"]),
            ("orbital_j_id", j_id, provenance["orbital_j_id"]),
        ):
            if not np.array_equal(array[row], expected[source]):
                raise ValueError(f"edge-output {name} is misaligned with its complete key")


def edge_output_by_key(output: dict[str, Any]) -> dict[tuple[str, int, int, int, int, int], dict[str, Any]]:
    records: dict[tuple[str, int, int, int, int, int], dict[str, Any]] = {}
    for row, (i, j, n) in enumerate(zip(output["receiver"], output["sender"], output["shift"], strict=True)):
        key = (output["structure_id"], int(i), int(j), int(n[0]), int(n[1]), int(n[2]))
        if key in records:
            raise ValueError("duplicate complete edge-output key")
        records[key] = {
            "edge_instance_id": str(output["edge_instance_id"][row]),
            "prediction": np.asarray(output["prediction"])[row].copy(),
            "block_shape": np.asarray(output["block_shape"])[row].copy(),
            "mask": np.asarray(output["mask"])[row].copy(),
            "orbital_i_index": np.asarray(output["orbital_i_index"])[row].copy(),
            "orbital_j_index": np.asarray(output["orbital_j_index"])[row].copy(),
            "orbital_i_id": np.asarray(output["orbital_i_id"])[row].copy(),
            "orbital_j_id": np.asarray(output["orbital_j_id"])[row].copy(),
            "unit": output["unit"],
        }
    return records


def _batch_components(
    graphs: list[dict[str, Any]],
    node_features: list[np.ndarray] | None,
    edge_features: list[np.ndarray] | None,
    provenances: list[dict[str, Any]] | None,
    predictions: list[np.ndarray] | None,
) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, Any]], list[np.ndarray]]:
    if not graphs:
        raise ValueError("batch must contain at least one graph")
    for graph in graphs:
        validate_graph(graph)
    if node_features is None:
        node_features = [graph["fractional"].copy() for graph in graphs]
    if edge_features is None:
        edge_features = [edge_features_from_geometry(graph, 3) for graph in graphs]
    if provenances is None:
        provenances = [make_orbital_provenance(graph, 4) for graph in graphs]
    if predictions is None:
        predictions = [np.zeros(provenance["mask"].shape, dtype=np.float64) for provenance in provenances]
    if not (len(node_features) == len(edge_features) == len(provenances) == len(predictions) == len(graphs)):
        raise ValueError("batch component list lengths mismatch")
    checked_nodes: list[np.ndarray] = []
    checked_edges: list[np.ndarray] = []
    checked_predictions: list[np.ndarray] = []
    for graph, node, edge, provenance, prediction in zip(graphs, node_features, edge_features, provenances, predictions, strict=True):
        validate_orbital_provenance(graph, provenance)
        node_array = np.asarray(node)
        edge_array = np.asarray(edge)
        prediction_array = np.asarray(prediction)
        if node_array.dtype != np.float64 or node_array.ndim != 2 or node_array.shape[0] != graph["fractional"].shape[0] or not np.isfinite(node_array).all():
            raise ValueError("node features must be finite float64[N,d]")
        if edge_array.dtype != np.float64 or edge_array.ndim != 2 or edge_array.shape[0] != graph["receiver"].shape[0] or not np.isfinite(edge_array).all():
            raise ValueError("edge features must be finite float64[E,de]")
        if prediction_array.dtype != np.float64 or prediction_array.shape != provenance["mask"].shape or not np.isfinite(prediction_array).all():
            raise ValueError("batch predictions must be finite float64[E,Pmax]")
        checked_nodes.append(node_array)
        checked_edges.append(edge_array)
        checked_predictions.append(prediction_array)
    if len({array.shape[1] for array in checked_nodes}) != 1 or len({array.shape[1] for array in checked_edges}) != 1 or len({array.shape[1] for array in checked_predictions}) != 1:
        raise ValueError("batch feature and output widths must agree")
    return checked_nodes, checked_edges, provenances, checked_predictions


def make_concat_batch(
    graphs: list[dict[str, Any]],
    node_features: list[np.ndarray] | None = None,
    edge_features: list[np.ndarray] | None = None,
    provenances: list[dict[str, Any]] | None = None,
    predictions: list[np.ndarray] | None = None,
) -> dict[str, Any]:
    nodes, edges, provenances, predictions = _batch_components(graphs, node_features, edge_features, provenances, predictions)
    node_count = np.asarray([graph["fractional"].shape[0] for graph in graphs], dtype=np.int64)
    edge_count = np.asarray([graph["receiver"].shape[0] for graph in graphs], dtype=np.int64)
    offsets = np.concatenate([np.asarray([0], dtype=np.int64), np.cumsum(node_count[:-1])])
    batch = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "graph_count": len(graphs),
        "structure_id": [graph["structure_id"] for graph in graphs],
        "cell": np.stack([graph["cell"] for graph in graphs]),
        "cutoff": np.asarray([graph["cutoff"] for graph in graphs], dtype=np.float64),
        "edge_feature_contract": EDGE_FEATURE_CONTRACT,
        "node_count": node_count,
        "edge_count": edge_count,
        "node_graph_id": np.repeat(np.arange(len(graphs), dtype=np.int64), node_count),
        "edge_graph_id": np.repeat(np.arange(len(graphs), dtype=np.int64), edge_count),
        "receiver": np.concatenate([graph["receiver"] + offset for graph, offset in zip(graphs, offsets, strict=True)]),
        "sender": np.concatenate([graph["sender"] + offset for graph, offset in zip(graphs, offsets, strict=True)]),
        "fractional": np.concatenate([graph["fractional"] for graph in graphs]),
        "node_features": np.concatenate(nodes),
        "shift": np.concatenate([graph["shift"] for graph in graphs]),
        "displacement": np.concatenate([graph["displacement"] for graph in graphs]),
        "distance": np.concatenate([graph["distance"] for graph in graphs]),
        "edge_features": np.concatenate(edges),
        "edge_instance_id": np.concatenate([graph["edge_instance_id"] for graph in graphs]),
        "prediction": np.concatenate(predictions),
        "block_shape": np.concatenate([provenance["block_shape"] for provenance in provenances]),
        "component_mask": np.concatenate([provenance["mask"] for provenance in provenances]),
        "orbital_i_index": np.concatenate([provenance["orbital_i_index"] for provenance in provenances]),
        "orbital_j_index": np.concatenate([provenance["orbital_j_index"] for provenance in provenances]),
        "orbital_i_id": np.concatenate([provenance["orbital_i_id"] for provenance in provenances]),
        "orbital_j_id": np.concatenate([provenance["orbital_j_id"] for provenance in provenances]),
        "node_orbitals": [copy.deepcopy(provenance["node_orbitals"]) for provenance in provenances],
        "unit": ["synthetic_dimensionless"] * len(graphs),
    }
    validate_concat_batch(batch)
    return batch


def validate_concat_batch(batch: dict[str, Any]) -> None:
    required = {
        "schema_version", "graph_count", "structure_id", "cell", "cutoff", "edge_feature_contract", "node_count", "edge_count",
        "node_graph_id", "edge_graph_id", "receiver", "sender", "fractional", "node_features",
        "shift", "displacement", "distance", "edge_features", "edge_instance_id", "prediction",
        "block_shape", "component_mask", "orbital_i_index", "orbital_j_index", "orbital_i_id",
        "orbital_j_id", "node_orbitals", "unit",
    }
    missing = required.difference(batch)
    if missing:
        raise ValueError(f"missing concatenated batch fields: {sorted(missing)}")
    if batch["schema_version"] != BATCH_SCHEMA_VERSION or isinstance(batch["graph_count"], bool) or not isinstance(batch["graph_count"], int) or batch["graph_count"] <= 0:
        raise ValueError("invalid concatenated batch identity")
    graph_count = batch["graph_count"]
    if batch["edge_feature_contract"] != EDGE_FEATURE_CONTRACT:
        raise ValueError("concatenated edge feature contract mismatch")
    if not all(isinstance(batch[name], list) and len(batch[name]) == graph_count for name in ("structure_id", "node_orbitals", "unit")):
        raise ValueError("concatenated per-graph metadata length mismatch")
    if any(not isinstance(value, str) or not value for name in ("structure_id", "unit") for value in batch[name]):
        raise ValueError("concatenated per-graph strings must be non-empty")
    node_count = np.asarray(batch["node_count"])
    edge_count = np.asarray(batch["edge_count"])
    node_graph_id = np.asarray(batch["node_graph_id"])
    edge_graph_id = np.asarray(batch["edge_graph_id"])
    receiver = np.asarray(batch["receiver"])
    sender = np.asarray(batch["sender"])
    if any(array.dtype != np.int64 for array in (node_count, edge_count, node_graph_id, edge_graph_id, receiver, sender)):
        raise ValueError("concatenated counts and indices must be int64")
    if node_count.shape != (graph_count,) or edge_count.shape != (graph_count,) or np.any(node_count < 0) or np.any(edge_count < 0):
        raise ValueError("concatenated graph counts are invalid")
    expected_node_ids = np.repeat(np.arange(graph_count, dtype=np.int64), node_count)
    expected_edge_ids = np.repeat(np.arange(graph_count, dtype=np.int64), edge_count)
    if not np.array_equal(node_graph_id, expected_node_ids) or not np.array_equal(edge_graph_id, expected_edge_ids):
        raise ValueError("concatenated graph IDs do not match per-graph counts")
    total_nodes = int(node_count.sum())
    total_edges = int(edge_count.sum())
    cell = np.asarray(batch["cell"])
    cutoff = np.asarray(batch["cutoff"])
    if cell.dtype != np.float64 or cell.shape != (graph_count, 3, 3) or cutoff.dtype != np.float64 or cutoff.shape != (graph_count,) or not np.isfinite(cell).all() or not np.isfinite(cutoff).all() or np.any(cutoff <= 0.0):
        raise ValueError("concatenated cell/cutoff schema mismatch")
    for graph_id in range(graph_count):
        validate_cell(cell[graph_id])
        validate_cutoff(cutoff[graph_id])
    if receiver.shape != (total_edges,) or sender.shape != (total_edges,):
        raise ValueError("concatenated edge shapes mismatch")
    if total_edges and (receiver.min() < 0 or sender.min() < 0 or receiver.max() >= total_nodes or sender.max() >= total_nodes):
        raise ValueError("concatenated endpoint out of range")
    if total_edges and (not np.array_equal(node_graph_id[receiver], edge_graph_id) or not np.array_equal(node_graph_id[sender], edge_graph_id)):
        raise ValueError("cross-graph edge is forbidden")
    float_shapes = {
        "fractional": (total_nodes, 3),
        "node_features": (total_nodes, None),
        "displacement": (total_edges, 3),
        "distance": (total_edges,),
        "edge_features": (total_edges, None),
        "prediction": (total_edges, None),
    }
    for name, shape in float_shapes.items():
        array = np.asarray(batch[name])
        if array.dtype != np.float64 or not np.isfinite(array).all() or array.shape[0] != shape[0] or (len(shape) == 2 and shape[1] is not None and array.shape != shape) or (len(shape) == 1 and array.shape != shape) or (len(shape) == 2 and shape[1] is None and array.ndim != 2):
            raise ValueError(f"concatenated {name} violates float64 finite schema")
    shift = np.asarray(batch["shift"])
    block_shape = np.asarray(batch["block_shape"])
    component_mask = np.asarray(batch["component_mask"])
    if shift.dtype != np.int64 or shift.shape != (total_edges, 3) or block_shape.dtype != np.int64 or block_shape.shape != (total_edges, 2) or component_mask.dtype != np.bool_ or component_mask.shape != np.asarray(batch["prediction"]).shape:
        raise ValueError("concatenated shift/block/mask schema mismatch")
    for name in ("orbital_i_index", "orbital_j_index"):
        array = np.asarray(batch[name])
        if array.dtype != np.int64 or array.shape != component_mask.shape:
            raise ValueError(f"concatenated {name} schema mismatch")
    for name in ("orbital_i_id", "orbital_j_id"):
        if np.asarray(batch[name]).shape != component_mask.shape:
            raise ValueError(f"concatenated {name} shape mismatch")
    identities = np.asarray(batch["edge_instance_id"])
    i_index = np.asarray(batch["orbital_i_index"])
    j_index = np.asarray(batch["orbital_j_index"])
    i_id = np.asarray(batch["orbital_i_id"])
    j_id = np.asarray(batch["orbital_j_id"])
    if identities.shape != (total_edges,):
        raise ValueError("concatenated edge ID shape mismatch")
    offsets = np.concatenate([np.asarray([0], dtype=np.int64), np.cumsum(node_count[:-1])])
    fractional = np.asarray(batch["fractional"])
    displacement = np.asarray(batch["displacement"])
    distance = np.asarray(batch["distance"])
    edge_features = np.asarray(batch["edge_features"])
    if fractional.shape != (total_nodes, 3) or np.any(fractional < 0.0) or np.any(fractional >= 1.0):
        raise ValueError("concatenated fractional coordinates must be canonical float64[N,3]")
    expected_displacement = np.empty_like(displacement)
    for row in range(total_edges):
        graph_id = int(edge_graph_id[row])
        expected_displacement[row] = (
            fractional[sender[row]] + shift[row] - fractional[receiver[row]]
        ) @ cell[graph_id]
    if not np.allclose(displacement, expected_displacement, rtol=0.0, atol=DISPLACEMENT_ATOL):
        raise ValueError("concatenated displacement is misaligned with its complete key")
    if not np.allclose(distance, np.linalg.norm(displacement, axis=1), rtol=0.0, atol=DISPLACEMENT_ATOL):
        raise ValueError("concatenated distance is misaligned with displacement")
    if total_edges and (np.any(distance <= 0.0) or np.any(distance > cutoff[edge_graph_id])):
        raise ValueError("concatenated edge distance violates its graph cutoff")
    base_edge_features = np.concatenate([distance[:, None], displacement], axis=1)
    expected_edge_features = (
        base_edge_features[:, : edge_features.shape[1]]
        if edge_features.shape[1] <= base_edge_features.shape[1]
        else np.concatenate(
            [base_edge_features, np.zeros((total_edges, edge_features.shape[1] - base_edge_features.shape[1]), dtype=np.float64)],
            axis=1,
        )
    )
    if not np.array_equal(edge_features, expected_edge_features):
        raise ValueError("concatenated edge features violate the row-wise feature contract")
    for row in range(total_edges):
        graph_id = int(edge_graph_id[row])
        local_i = int(receiver[row] - offsets[graph_id])
        local_j = int(sender[row] - offsets[graph_id])
        orbitals_i = batch["node_orbitals"][graph_id][local_i]
        orbitals_j = batch["node_orbitals"][graph_id][local_j]
        expected_count = len(orbitals_i) * len(orbitals_j)
        expected_mask = np.arange(component_mask.shape[1]) < expected_count
        if tuple(block_shape[row]) != (len(orbitals_i), len(orbitals_j)) or not np.array_equal(component_mask[row], expected_mask):
            raise ValueError("concatenated block or component mask mismatch")
        expected_identity = edge_instance_id(batch["structure_id"][graph_id], local_i, local_j, shift[row])
        if str(identities[row]) != expected_identity:
            raise ValueError("concatenated edge ID mismatch")
        for component in range(component_mask.shape[1]):
            if component < expected_count:
                alpha, beta = divmod(component, len(orbitals_j))
                expected = (alpha, beta, orbitals_i[alpha], orbitals_j[beta])
            else:
                expected = (-1, -1, "", "")
            actual = (int(i_index[row, component]), int(j_index[row, component]), str(i_id[row, component]), str(j_id[row, component]))
            if actual != expected:
                raise ValueError("concatenated orbital provenance row mismatch")


def make_padded_batch(
    graphs: list[dict[str, Any]],
    node_features: list[np.ndarray] | None = None,
    edge_features: list[np.ndarray] | None = None,
    provenances: list[dict[str, Any]] | None = None,
    predictions: list[np.ndarray] | None = None,
) -> dict[str, Any]:
    nodes, edges, provenances, predictions = _batch_components(graphs, node_features, edge_features, provenances, predictions)
    batch_size = len(graphs)
    node_count = np.asarray([graph["fractional"].shape[0] for graph in graphs], dtype=np.int64)
    edge_count = np.asarray([graph["receiver"].shape[0] for graph in graphs], dtype=np.int64)
    node_max = int(node_count.max())
    edge_max = int(edge_count.max())
    hidden_dim = nodes[0].shape[1]
    edge_dim = edges[0].shape[1]
    output_dim = predictions[0].shape[1]
    batch: dict[str, Any] = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "graph_count": batch_size,
        "structure_id": [graph["structure_id"] for graph in graphs],
        "cell": np.stack([graph["cell"] for graph in graphs]),
        "cutoff": np.asarray([graph["cutoff"] for graph in graphs], dtype=np.float64),
        "edge_feature_contract": EDGE_FEATURE_CONTRACT,
        "node_count": node_count,
        "edge_count": edge_count,
        "node_mask": np.zeros((batch_size, node_max), dtype=np.bool_),
        "edge_mask": np.zeros((batch_size, edge_max), dtype=np.bool_),
        "receiver": np.full((batch_size, edge_max), -1, dtype=np.int64),
        "sender": np.full((batch_size, edge_max), -1, dtype=np.int64),
        "fractional": np.full((batch_size, node_max, 3), np.nan, dtype=np.float64),
        "node_features": np.full((batch_size, node_max, hidden_dim), np.nan, dtype=np.float64),
        "shift": np.zeros((batch_size, edge_max, 3), dtype=np.int64),
        "displacement": np.full((batch_size, edge_max, 3), np.nan, dtype=np.float64),
        "distance": np.full((batch_size, edge_max), np.nan, dtype=np.float64),
        "edge_features": np.full((batch_size, edge_max, edge_dim), np.nan, dtype=np.float64),
        "edge_instance_id": np.full((batch_size, edge_max), "", dtype="<U64"),
        "prediction": np.full((batch_size, edge_max, output_dim), np.nan, dtype=np.float64),
        "block_shape": np.full((batch_size, edge_max, 2), -1, dtype=np.int64),
        "component_mask": np.zeros((batch_size, edge_max, output_dim), dtype=np.bool_),
        "orbital_i_index": np.full((batch_size, edge_max, output_dim), -1, dtype=np.int64),
        "orbital_j_index": np.full((batch_size, edge_max, output_dim), -1, dtype=np.int64),
        "orbital_i_id": np.full((batch_size, edge_max, output_dim), "", dtype="<U32"),
        "orbital_j_id": np.full((batch_size, edge_max, output_dim), "", dtype="<U32"),
        "node_orbitals": [copy.deepcopy(provenance["node_orbitals"]) for provenance in provenances],
        "unit": ["synthetic_dimensionless"] * batch_size,
    }
    for index, (graph, node, edge, provenance, prediction) in enumerate(zip(graphs, nodes, edges, provenances, predictions, strict=True)):
        n = int(node_count[index])
        e = int(edge_count[index])
        batch["node_mask"][index, :n] = True
        batch["edge_mask"][index, :e] = True
        batch["receiver"][index, :e] = graph["receiver"]
        batch["sender"][index, :e] = graph["sender"]
        for name, value in (
            ("fractional", graph["fractional"]), ("node_features", node),
        ):
            batch[name][index, :n] = value
        for name, value in (
            ("shift", graph["shift"]), ("displacement", graph["displacement"]), ("distance", graph["distance"]),
            ("edge_features", edge), ("edge_instance_id", graph["edge_instance_id"]), ("prediction", prediction),
            ("block_shape", provenance["block_shape"]), ("component_mask", provenance["mask"]),
            ("orbital_i_index", provenance["orbital_i_index"]), ("orbital_j_index", provenance["orbital_j_index"]),
            ("orbital_i_id", provenance["orbital_i_id"]), ("orbital_j_id", provenance["orbital_j_id"]),
        ):
            batch[name][index, :e] = value
    validate_padded_batch(batch)
    return batch


def _is_prefix(mask_row: np.ndarray) -> bool:
    false_positions = np.flatnonzero(~mask_row)
    return not false_positions.size or not mask_row[false_positions[0] :].any()


def validate_padded_batch(batch: dict[str, Any]) -> None:
    required = {
        "schema_version", "graph_count", "structure_id", "cell", "cutoff", "edge_feature_contract", "node_count", "edge_count", "node_mask", "edge_mask",
        "receiver", "sender", "fractional", "node_features", "shift", "displacement", "distance", "edge_features",
        "edge_instance_id", "prediction", "block_shape", "component_mask", "orbital_i_index", "orbital_j_index",
        "orbital_i_id", "orbital_j_id", "node_orbitals", "unit",
    }
    missing = required.difference(batch)
    if missing:
        raise ValueError(f"missing padded batch fields: {sorted(missing)}")
    if batch["schema_version"] != BATCH_SCHEMA_VERSION or isinstance(batch["graph_count"], bool) or not isinstance(batch["graph_count"], int) or batch["graph_count"] <= 0:
        raise ValueError("invalid padded batch identity")
    graph_count = batch["graph_count"]
    if batch["edge_feature_contract"] != EDGE_FEATURE_CONTRACT:
        raise ValueError("padded edge feature contract mismatch")
    if not all(isinstance(batch[name], list) and len(batch[name]) == graph_count for name in ("structure_id", "node_orbitals", "unit")):
        raise ValueError("padded per-graph metadata length mismatch")
    node_mask = np.asarray(batch["node_mask"])
    edge_mask = np.asarray(batch["edge_mask"])
    receiver = np.asarray(batch["receiver"])
    sender = np.asarray(batch["sender"])
    if node_mask.dtype != np.bool_ or edge_mask.dtype != np.bool_:
        raise ValueError("padding masks must be bool")
    if receiver.dtype != np.int64 or sender.dtype != np.int64 or receiver.shape != edge_mask.shape or sender.shape != edge_mask.shape:
        raise ValueError("padded endpoint schema mismatch")
    node_count_array = np.asarray(batch["node_count"])
    edge_count_array = np.asarray(batch["edge_count"])
    cell = np.asarray(batch["cell"])
    cutoff = np.asarray(batch["cutoff"])
    if cell.dtype != np.float64 or cell.shape != (graph_count, 3, 3) or cutoff.dtype != np.float64 or cutoff.shape != (graph_count,) or not np.isfinite(cell).all() or not np.isfinite(cutoff).all() or np.any(cutoff <= 0.0):
        raise ValueError("padded cell/cutoff schema mismatch")
    for graph_id in range(graph_count):
        validate_cell(cell[graph_id])
        validate_cutoff(cutoff[graph_id])
    if node_count_array.dtype != np.int64 or edge_count_array.dtype != np.int64 or node_count_array.shape != (graph_count,) or edge_count_array.shape != (graph_count,):
        raise ValueError("padded count schema mismatch")
    if node_mask.ndim != 2 or edge_mask.ndim != 2 or node_mask.shape[0] != graph_count or edge_mask.shape[0] != graph_count:
        raise ValueError("padded batch size mismatch")
    for batch_index in range(node_mask.shape[0]):
        if not _is_prefix(node_mask[batch_index]) or not _is_prefix(edge_mask[batch_index]):
            raise ValueError("padding masks must be left-contiguous prefixes")
        node_count = int(node_mask[batch_index].sum())
        edge_count = int(edge_mask[batch_index].sum())
        if node_count != int(node_count_array[batch_index]) or edge_count != int(edge_count_array[batch_index]):
            raise ValueError("padded masks do not match per-graph counts")
        active = edge_mask[batch_index]
        if active.any() and (
            receiver[batch_index, active].min() < 0
            or sender[batch_index, active].min() < 0
            or receiver[batch_index, active].max() >= node_count
            or sender[batch_index, active].max() >= node_count
        ):
            raise ValueError("active padded endpoint out of range")
        if np.any(receiver[batch_index, ~active] != -1) or np.any(sender[batch_index, ~active] != -1):
            raise ValueError("padding endpoints must use -1")
        for name in ("fractional", "node_features"):
            array = np.asarray(batch[name])
            if array.dtype != np.float64 or array.shape[:2] != node_mask.shape or not np.isfinite(array[batch_index, :node_count]).all():
                raise ValueError(f"active padded {name} violates float64 finite schema")
        fractional_array = np.asarray(batch["fractional"])
        node_feature_array = np.asarray(batch["node_features"])
        if fractional_array.shape != (*node_mask.shape, 3):
            raise ValueError("padded fractional coordinates must have shape (B,Nmax,3)")
        if node_feature_array.ndim != 3 or node_feature_array.shape[2] <= 0:
            raise ValueError("padded node features must have shape (B,Nmax,d)")
        if np.any(fractional_array[batch_index, :node_count] < 0.0) or np.any(fractional_array[batch_index, :node_count] >= 1.0):
            raise ValueError("active padded fractional coordinates must be canonical")
        for name in ("displacement", "distance", "edge_features", "prediction"):
            array = np.asarray(batch[name])
            if array.dtype != np.float64 or array.shape[:2] != edge_mask.shape or not np.isfinite(array[batch_index, active]).all():
                raise ValueError(f"active padded {name} violates float64 finite schema")
        displacement_array = np.asarray(batch["displacement"])
        distance_array = np.asarray(batch["distance"])
        edge_feature_array = np.asarray(batch["edge_features"])
        if displacement_array.shape != (*edge_mask.shape, 3) or distance_array.shape != edge_mask.shape or edge_feature_array.ndim != 3 or edge_feature_array.shape[2] <= 0:
            raise ValueError("padded edge tensors violate complete ndim/shape schema")
        shift = np.asarray(batch["shift"])
        component_mask = np.asarray(batch["component_mask"])
        block_shape = np.asarray(batch["block_shape"])
        if shift.dtype != np.int64 or shift.shape != (*edge_mask.shape, 3) or component_mask.dtype != np.bool_ or component_mask.ndim != 3 or component_mask.shape[:2] != edge_mask.shape or block_shape.dtype != np.int64 or block_shape.shape != (*edge_mask.shape, 2):
            raise ValueError("padded shift/block/component mask schema mismatch")
        prediction = np.asarray(batch["prediction"])
        if prediction.shape != component_mask.shape:
            raise ValueError("padded prediction and component mask must share (B,Emax,Pmax)")
        for name in ("orbital_i_index", "orbital_j_index"):
            array = np.asarray(batch[name])
            if array.dtype != np.int64 or array.shape != component_mask.shape:
                raise ValueError(f"padded {name} schema mismatch")
        if np.any(component_mask[batch_index, ~active]):
            raise ValueError("padding components must be excluded")
        fractional = np.asarray(batch["fractional"])
        displacement = np.asarray(batch["displacement"])
        distance = np.asarray(batch["distance"])
        edge_features = np.asarray(batch["edge_features"])
        expected_displacement = (
            fractional[batch_index, sender[batch_index, active]]
            + shift[batch_index, active]
            - fractional[batch_index, receiver[batch_index, active]]
        ) @ cell[batch_index]
        if not np.allclose(displacement[batch_index, active], expected_displacement, rtol=0.0, atol=DISPLACEMENT_ATOL):
            raise ValueError("padded displacement is misaligned with its complete key")
        if not np.allclose(distance[batch_index, active], np.linalg.norm(displacement[batch_index, active], axis=1), rtol=0.0, atol=DISPLACEMENT_ATOL):
            raise ValueError("padded distance is misaligned with displacement")
        if edge_count and (
            np.any(distance[batch_index, active] <= 0.0)
            or np.any(distance[batch_index, active] > cutoff[batch_index])
        ):
            raise ValueError("padded edge distance violates its graph cutoff")
        base_edge_features = np.concatenate(
            [distance[batch_index, active, None], displacement[batch_index, active]], axis=1
        )
        expected_edge_features = (
            base_edge_features[:, : edge_features.shape[2]]
            if edge_features.shape[2] <= base_edge_features.shape[1]
            else np.concatenate(
                [base_edge_features, np.zeros((edge_count, edge_features.shape[2] - base_edge_features.shape[1]), dtype=np.float64)],
                axis=1,
            )
        )
        if not np.array_equal(edge_features[batch_index, active], expected_edge_features):
            raise ValueError("padded edge features violate the row-wise feature contract")
        identities = np.asarray(batch["edge_instance_id"])
        i_index = np.asarray(batch["orbital_i_index"])
        j_index = np.asarray(batch["orbital_j_index"])
        i_id = np.asarray(batch["orbital_i_id"])
        j_id = np.asarray(batch["orbital_j_id"])
        if identities.shape != edge_mask.shape or i_id.shape != component_mask.shape or j_id.shape != component_mask.shape:
            raise ValueError("padded identity shape mismatch")
        for row in range(edge_count):
            local_i = int(receiver[batch_index, row])
            local_j = int(sender[batch_index, row])
            orbitals_i = batch["node_orbitals"][batch_index][local_i]
            orbitals_j = batch["node_orbitals"][batch_index][local_j]
            expected_count = len(orbitals_i) * len(orbitals_j)
            expected_mask = np.arange(component_mask.shape[2]) < expected_count
            if tuple(block_shape[batch_index, row]) != (len(orbitals_i), len(orbitals_j)) or not np.array_equal(component_mask[batch_index, row], expected_mask):
                raise ValueError("padded block or component mask mismatch")
            expected_identity = edge_instance_id(batch["structure_id"][batch_index], local_i, local_j, shift[batch_index, row])
            if str(identities[batch_index, row]) != expected_identity:
                raise ValueError("padded edge ID mismatch")
            for component in range(component_mask.shape[2]):
                if component < expected_count:
                    alpha, beta = divmod(component, len(orbitals_j))
                    expected = (alpha, beta, orbitals_i[alpha], orbitals_j[beta])
                else:
                    expected = (-1, -1, "", "")
                actual = (
                    int(i_index[batch_index, row, component]), int(j_index[batch_index, row, component]),
                    str(i_id[batch_index, row, component]), str(j_id[batch_index, row, component]),
                )
                if actual != expected:
                    raise ValueError("padded orbital provenance row mismatch")


def aggregate_messages(receiver: Any, messages: Any, node_count: int, mode: str) -> Any:
    receiver_array = np.asarray(receiver)
    message_array = np.asarray(messages)
    if receiver_array.dtype != np.int64 or receiver_array.ndim != 1 or message_array.dtype != np.float64 or message_array.ndim != 2 or message_array.shape[0] != receiver_array.size or not np.isfinite(message_array).all():
        raise ValueError("aggregation input schema mismatch")
    if receiver_array.size and (receiver_array.min() < 0 or receiver_array.max() >= node_count):
        raise ValueError("aggregation receiver out of range")
    count = np.bincount(receiver_array, minlength=node_count).astype(np.int64)
    has_incoming = count > 0
    if mode == "max" and not has_incoming.all():
        raise ValueError("max aggregation forbids empty incoming sets")
    if mode not in {"sum", "mean", "max"}:
        raise ValueError("unknown aggregation mode")
    if mode in {"sum", "mean"}:
        result = np.zeros((node_count, message_array.shape[1]), dtype=np.float64)
        np.add.at(result, receiver_array, message_array)
        if mode == "mean":
            result[has_incoming] /= count[has_incoming, None]
            return result, has_incoming
        return result
    result = np.full((node_count, message_array.shape[1]), -np.inf, dtype=np.float64)
    for edge, node in enumerate(receiver_array):
        result[int(node)] = np.maximum(result[int(node)], message_array[edge])
    return result


def forward_padded_batch(
    batch: dict[str, Any],
    parameters: dict[str, Any],
    targets: Any,
) -> dict[str, Any]:
    validate_padded_batch(batch)
    target_array = np.asarray(targets)
    if target_array.dtype != np.float64 or target_array.shape != np.asarray(batch["prediction"]).shape:
        raise ValueError("padded targets must be float64[B,Emax,Pmax]")
    predictions: list[np.ndarray] = []
    losses: list[float] = []
    normalized_means: list[float] = []
    for graph_index in range(batch["graph_count"]):
        n = int(batch["node_count"][graph_index])
        e = int(batch["edge_count"][graph_index])
        nodes = batch["node_features"][graph_index, :n]
        edges = batch["edge_features"][graph_index, :e]
        node_mean = nodes.mean(axis=0)
        node_std = nodes.std(axis=0)
        safe_std = np.where(node_std > 0.0, node_std, 1.0)
        normalized_means.append(float(np.max(np.abs(((nodes - node_mean) / safe_std).mean(axis=0)), initial=0.0)))
        prediction, _ = forward_mpnn(nodes, edges, batch["receiver"][graph_index, :e], batch["sender"][graph_index, :e], parameters)
        loss, _ = masked_mse(prediction, target_array[graph_index, :e], batch["component_mask"][graph_index, :e])
        predictions.append(prediction)
        losses.append(loss)
    return {
        "prediction": predictions,
        "losses": losses,
        "normalized_node_mean_max_abs": normalized_means,
    }


def validate_group_split(split: dict[str, Any], group_count: int) -> None:
    required = {"train", "validation", "test"}
    missing = required.difference(split)
    if missing:
        raise ValueError(f"missing split fields: {sorted(missing)}")
    sets: dict[str, set[int]] = {}
    for name in ("train", "validation", "test"):
        values = np.asarray(split[name])
        if values.dtype != np.int64 or values.ndim != 1:
            raise ValueError(f"split {name} must be int64[G]")
        if values.size != np.unique(values).size:
            raise ValueError(f"split {name} contains duplicate groups")
        if values.size and (values.min() < 0 or values.max() >= group_count):
            raise ValueError(f"split {name} group ID out of range")
        sets[name] = set(int(value) for value in values)
    if sets["train"] & sets["validation"] or sets["train"] & sets["test"] or sets["validation"] & sets["test"]:
        raise ValueError("structure_group pollution across splits")
    if set.union(*sets.values()) != set(range(group_count)):
        raise ValueError("group split must cover every structure_group exactly once")


def grouped_regression(
    seed: int,
    group_count: int,
    frames_per_group: int,
    steps: int,
    learning_rate: float,
    *,
    layers: int,
    hidden_dim: int,
    edge_dim: int,
    output_dim: int,
) -> dict[str, Any]:
    """Train a frozen-message MPNN readout on the chapter-11 grouped family."""
    rng = np.random.default_rng(seed + 310)
    group_u = rng.uniform(-0.5, 0.5, size=group_count)
    group_bias = rng.normal(scale=0.03, size=group_count)
    tau = np.linspace(-0.5, 0.5, frames_per_group, dtype=np.float64)
    xi = rng.normal(scale=0.005, size=(group_count, frames_per_group, 2))
    epsilon = rng.normal(scale=0.002, size=(group_count, frames_per_group))
    x = np.empty((group_count, frames_per_group, 2), dtype=np.float64)
    x[:, :, 0] = group_u[:, None]
    x[:, :, 1] = tau[None, :]
    x += xi
    y = 1.5 * group_u[:, None] - 0.7 * tau[None, :] + group_bias[:, None] + epsilon

    train_stop = int(0.6 * group_count)
    validation_stop = int(0.8 * group_count)
    split = {
        "train": np.arange(0, train_stop, dtype=np.int64),
        "validation": np.arange(train_stop, validation_stop, dtype=np.int64),
        "test": np.arange(validation_stop, group_count, dtype=np.int64),
    }
    validate_group_split(split, group_count)
    group_ids = np.repeat(np.arange(group_count, dtype=np.int64), frames_per_group)
    flat_x = x.reshape(-1, 2)
    flat_y = y.reshape(-1)
    sample_count = flat_x.shape[0]

    node_features = np.zeros((2 * sample_count, hidden_dim), dtype=np.float64)
    node_features[0::2, 0] = flat_x[:, 0]
    node_features[1::2, 0] = flat_x[:, 0]
    if hidden_dim > 1:
        node_features[0::2, 1] = flat_x[:, 1]
        node_features[1::2, 1] = flat_x[:, 1]
    if hidden_dim > 2:
        node_features[:, 2:] = 0.25
    receiver = np.empty(2 * sample_count, dtype=np.int64)
    sender = np.empty(2 * sample_count, dtype=np.int64)
    receiver[0::2] = 2 * np.arange(sample_count)
    sender[0::2] = receiver[0::2] + 1
    receiver[1::2] = sender[0::2]
    sender[1::2] = receiver[0::2]
    edge_features = np.zeros((2 * sample_count, edge_dim), dtype=np.float64)
    edge_features[0::2, 0] = 1.0
    edge_features[1::2, 0] = -1.0
    if edge_dim > 1:
        edge_features[:, 1] = np.repeat(flat_x[:, 1], 2)
    if edge_dim > 2:
        edge_features[:, 2:] = 0.125

    parameters = init_mpnn_parameters(rng, layers, hidden_dim, edge_dim, output_dim)
    for layer in parameters["layers"]:
        for name in ("Wr", "Ws", "Wf", "bm", "Ua", "bu"):
            layer[name].fill(0.0)
        layer["Uh"] = np.eye(hidden_dim, dtype=np.float64)
    _, cache = forward_mpnn(node_features, edge_features, receiver, sender, parameters)
    head = cache["head_input"]
    output_scale = np.asarray([1.0, 0.5, -1.0, 0.25], dtype=np.float64)[:output_dim]
    target = np.repeat(flat_y, 2)[:, None] * output_scale[None, :]
    edge_group = np.repeat(group_ids, 2)

    def indices(groups: np.ndarray) -> np.ndarray:
        return np.flatnonzero(np.isin(edge_group, groups))

    train_index = indices(split["train"])
    validation_index = indices(split["validation"])
    test_index = indices(split["test"])

    def metrics(index: np.ndarray) -> tuple[float, float]:
        residual = head[index] @ parameters["Wo"] + parameters["bo"] - target[index]
        return float(np.mean(residual * residual)), float(np.mean(np.abs(residual)))

    checkpoints = sorted(set([0, steps, *range(max(1, steps // 10), steps, max(1, steps // 10))]))
    trajectory: list[dict[str, float | int]] = []
    initial_train_mse, _ = metrics(train_index)
    for step in range(steps + 1):
        if step in checkpoints:
            train_mse, _ = metrics(train_index)
            validation_mse, _ = metrics(validation_index)
            trajectory.append({"step": step, "train_mse": train_mse, "validation_mse": validation_mse})
        if step == steps:
            break
        residual = head[train_index] @ parameters["Wo"] + parameters["bo"] - target[train_index]
        scale = 2.0 / residual.size
        parameters["Wo"] -= learning_rate * scale * (head[train_index].T @ residual)
        parameters["bo"] -= learning_rate * scale * residual.sum(axis=0)

    final_train_mse, final_train_mae = metrics(train_index)
    validation_mse, validation_mae = metrics(validation_index)
    test_mse, test_mae = metrics(test_index)
    test_zero_baseline_mse = float(np.mean(target[test_index] * target[test_index]))
    corrupted = target[test_index] + 1.0
    corrupted_residual = head[test_index] @ parameters["Wo"] + parameters["bo"] - corrupted

    # Frame-wise leakage counterexample: group dummy variables estimate seen-group biases.
    frame_role = np.arange(frames_per_group) % 3
    frame_train = np.flatnonzero(np.tile(frame_role == 0, group_count))
    frame_test = np.flatnonzero(np.tile(frame_role == 2, group_count))
    design = np.column_stack([flat_x, np.ones(sample_count), np.eye(group_count)[group_ids]])
    leaked_weight = np.linalg.lstsq(design[frame_train], flat_y[frame_train], rcond=None)[0]
    leaked_residual = design[frame_test] @ leaked_weight - flat_y[frame_test]
    global_design = np.column_stack([flat_x, np.ones(sample_count)])
    global_weight = np.linalg.lstsq(global_design[np.isin(group_ids, split["train"])], flat_y[np.isin(group_ids, split["train"])], rcond=None)[0]
    new_group_residual = global_design[np.isin(group_ids, split["test"])] @ global_weight - flat_y[np.isin(group_ids, split["test"])]

    intersections = [
        sorted(set(split["train"]) & set(split["validation"])),
        sorted(set(split["train"]) & set(split["test"])),
        sorted(set(split["validation"]) & set(split["test"])),
    ]
    return {
        "generator": {
            "formula": "x=[u_g,tau_t]+xi; y=1.5*u_g-0.7*tau_t+b_g+epsilon",
            "xi_std": 0.005,
            "bias_std": 0.03,
            "epsilon_std": 0.002,
        },
        "architecture": {
            "layers": layers,
            "hidden_dim": hidden_dim,
            "edge_dim": edge_dim,
            "output_dim": output_dim,
            "trained_parameters": ["Wo", "bo"],
            "message_parameters": "frozen_deterministic_feature_extractor",
        },
        "group_ids": {name: values.tolist() for name, values in split.items()},
        "group_intersections": intersections,
        "counts": {
            name: {"groups": int(values.size), "samples": int(values.size * frames_per_group), "edge_outputs": int(values.size * frames_per_group * 2)}
            for name, values in split.items()
        },
        "trajectory": trajectory,
        "initial_train_mse": initial_train_mse,
        "final_train_mse": final_train_mse,
        "final_train_mae": final_train_mae,
        "validation_mse": validation_mse,
        "validation_mae": validation_mae,
        "test_mse": test_mse,
        "test_mae": test_mae,
        "test_zero_baseline_mse": test_zero_baseline_mse,
        "corrupted_test_mse": float(np.mean(corrupted_residual * corrupted_residual)),
        "frame_split_apparent_mse": float(np.mean(leaked_residual * leaked_residual)),
        "independent_group_linear_mse": float(np.mean(new_group_residual * new_group_residual)),
        "frame_split_group_intersections": [list(range(group_count))] * 3,
        "repeated_run_contract": "same seed, versions, config, and canonical JSON bytes",
    }


def group_split_evidence(group_count: int, frames_per_group: int) -> dict[str, Any]:
    groups = np.repeat(np.arange(group_count), frames_per_group)
    group_train = set(range(0, int(0.6 * group_count)))
    group_validation = set(range(int(0.6 * group_count), int(0.8 * group_count)))
    group_test = set(range(int(0.8 * group_count), group_count))
    disjoint_intersections = [
        sorted(group_train & group_validation),
        sorted(group_train & group_test),
        sorted(group_validation & group_test),
    ]
    frame_partition = np.arange(groups.size) % 3
    random_sets = [set(groups[frame_partition == split]) for split in range(3)]
    leakage_intersections = [
        sorted(random_sets[0] & random_sets[1]),
        sorted(random_sets[0] & random_sets[2]),
        sorted(random_sets[1] & random_sets[2]),
    ]
    return {
        "disjoint_intersections": disjoint_intersections,
        "leakage_intersections": leakage_intersections,
        "disjoint_pass": all(not values for values in disjoint_intersections),
        "random_frame_leakage_captured": all(bool(values) for values in leakage_intersections),
    }


def activation_bytes(node_count: int, edge_count: int, layers: int, hidden_dim: int) -> int:
    if min(node_count, edge_count, layers, hidden_dim) < 0:
        raise ValueError("complexity dimensions must be nonnegative")
    return int(8 * layers * (3 * node_count * hidden_dim + 2 * edge_count * hidden_dim))


def deep_copy_mapping(value: Any) -> Any:
    return copy.deepcopy(value)
