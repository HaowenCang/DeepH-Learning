from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Iterable

import numpy as np


SCHEMA_VERSION = "stageE-synthetic-equivariance-v1"
EDGE_VERSION = "stageD-edge-v1"
FILTER_VERSION = "stageE-edge-filter-v1"
HAMILTONIAN_VERSION = "stageE-hamiltonian-edge-v1"
BATCH_VERSION = "stageE-irrep-batch-v1"
TIME_REVERSAL_VERSION = "stageE-time-reversal-v1"
TIME_REVERSAL_PAIR_VERSION = "stageE-time-reversal-pair-v1"
UNRESOLVED_M8 = "UNRESOLVED_M8"
CG_DLMF_TABLE_SHA256 = "fd40673f73059974962cf9b8b3c9152b9af1bd28bb87028b9e4bffe797fd1a04"

FLOAT_DTYPES = (np.dtype(np.float32), np.dtype(np.float64))
SEEDS = (20260809, 20260810)
SCAN_ROTATION_COUNTS = (1, 8, 64, 257)
SCAN_MULTIPLIERS = (1, 2, 4)
SCAN_SCALES = (1.0e-3, 1.0, 1.0e3)
CONFIG_CASES = {
    "A": {"seed": 20260809, "dtype": "float64", "n_rotations": 64, "multiplicity": (3, 2, 2), "scale": 1.0},
    "B": {"seed": 20260810, "dtype": "float32", "n_rotations": 257, "multiplicity": (5, 4, 3), "scale": 1.0e3},
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized_residual(left: np.ndarray, right: np.ndarray) -> float:
    if not isinstance(left, np.ndarray) or not isinstance(right, np.ndarray):
        raise TypeError("residual inputs must be numpy arrays")
    if left.shape != right.shape:
        raise ValueError("residual inputs must have identical shape")
    if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise ValueError("residual inputs must be finite")
    numerator = float(np.linalg.norm(left - right))
    denominator = max(1.0, float(np.linalg.norm(left)), float(np.linalg.norm(right)))
    return numerator / denominator


def _float_dtype(dtype: Any) -> np.dtype:
    result = np.dtype(dtype)
    if result not in FLOAT_DTYPES:
        raise TypeError("dtype must be exactly float32 or float64")
    return result


def _complex_dtype(dtype: Any) -> np.dtype:
    real = _float_dtype(dtype)
    return np.dtype(np.complex64 if real == np.dtype(np.float32) else np.complex128)


def _require_array(
    name: str,
    value: Any,
    *,
    shape: tuple[int, ...] | None = None,
    dtype: np.dtype | None = None,
    finite: bool = True,
) -> np.ndarray:
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a numpy array")
    if shape is not None and value.shape != shape:
        raise ValueError(f"{name} shape must be {shape}, got {value.shape}")
    if dtype is not None and value.dtype != dtype:
        raise TypeError(f"{name} dtype must be {dtype}, got {value.dtype}")
    if finite and not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be finite")
    return value


def tolerance(dtype: Any) -> float:
    return 5.0e-6 if _float_dtype(dtype) == np.dtype(np.float32) else 5.0e-12


def zero_tolerance(dtype: Any) -> float:
    return 1.0e-5 if _float_dtype(dtype) == np.dtype(np.float32) else 1.0e-12


def frame_tolerance(dtype: Any) -> float:
    return 1.0e-4 if _float_dtype(dtype) == np.dtype(np.float32) else 1.0e-8


def validate_rotation(rotation: np.ndarray) -> dict[str, float]:
    if not isinstance(rotation, np.ndarray):
        raise TypeError("rotation must be a numpy array")
    dtype = _float_dtype(rotation.dtype)
    _require_array("rotation", rotation, shape=(3, 3), dtype=dtype)
    identity = np.eye(3, dtype=dtype)
    epsilon_r = float(np.linalg.norm(rotation.T @ rotation - identity) / max(1.0, np.linalg.norm(identity)))
    epsilon_det = abs(float(np.linalg.det(rotation)) - 1.0)
    tau = tolerance(dtype)
    if epsilon_r > tau or epsilon_det > tau:
        raise ValueError("rotation fails SO(3) tolerance")
    return {"orthogonality_residual": epsilon_r, "determinant_residual": epsilon_det}


def validate_unit_quaternion(quaternion: np.ndarray) -> float:
    if not isinstance(quaternion, np.ndarray):
        raise TypeError("quaternion must be a numpy array")
    dtype = _float_dtype(quaternion.dtype)
    _require_array("quaternion", quaternion, shape=(4,), dtype=dtype)
    epsilon = abs(float(np.linalg.norm(quaternion)) - 1.0)
    if epsilon > tolerance(dtype):
        raise ValueError("quaternion is not unit within tolerance")
    return epsilon


def validate_canonical_unit_quaternion(quaternion: np.ndarray) -> float:
    epsilon = validate_unit_quaternion(quaternion)
    pivot_tolerance = 32.0 * np.finfo(quaternion.dtype).eps
    pivot = next((item for item in quaternion if abs(float(item)) > pivot_tolerance), None)
    if pivot is None or float(pivot) < 0:
        raise ValueError("unit quaternion does not use the canonical positive-pivot sign")
    return epsilon


def canonicalize_quaternions(quaternions: np.ndarray) -> np.ndarray:
    if not isinstance(quaternions, np.ndarray) or quaternions.ndim != 2 or quaternions.shape[1] != 4:
        raise ValueError("quaternions must have shape (n_R,4)")
    dtype = _float_dtype(quaternions.dtype)
    _require_array("quaternions", quaternions, dtype=dtype)
    output = np.array(quaternions, copy=True, order="C")
    pivot_tolerance = 32.0 * np.finfo(dtype).eps
    for row in output:
        pivot = next((index for index, item in enumerate(row) if abs(float(item)) > pivot_tolerance), None)
        if pivot is None:
            raise ValueError("unit quaternion has no canonical pivot")
        if row[pivot] < 0:
            row *= -1
    output[output == 0] = dtype.type(0.0)
    return output


def quaternions_to_rotations(quaternions: np.ndarray) -> np.ndarray:
    if not isinstance(quaternions, np.ndarray) or quaternions.ndim != 2 or quaternions.shape[1] != 4:
        raise ValueError("quaternions must have shape (n_R,4)")
    dtype = _float_dtype(quaternions.dtype)
    _require_array("quaternions", quaternions, dtype=dtype)
    for row in quaternions:
        validate_unit_quaternion(row)
    w, x, y, z = (quaternions[:, index] for index in range(4))
    rotations = np.empty((quaternions.shape[0], 3, 3), dtype=dtype, order="C")
    rotations[:, 0, 0] = 1 - 2 * (y * y + z * z)
    rotations[:, 0, 1] = 2 * (x * y - w * z)
    rotations[:, 0, 2] = 2 * (x * z + w * y)
    rotations[:, 1, 0] = 2 * (x * y + w * z)
    rotations[:, 1, 1] = 1 - 2 * (x * x + z * z)
    rotations[:, 1, 2] = 2 * (y * z - w * x)
    rotations[:, 2, 0] = 2 * (x * z - w * y)
    rotations[:, 2, 1] = 2 * (y * z + w * x)
    rotations[:, 2, 2] = 1 - 2 * (x * x + y * y)
    for rotation in rotations:
        validate_rotation(rotation)
    return rotations


def random_rotations(rng: np.random.Generator, n_rotations: int, dtype: Any) -> np.ndarray:
    target_dtype = _float_dtype(dtype)
    if type(n_rotations) is not int or n_rotations <= 0:
        raise ValueError("n_rotations must be a positive int")
    quaternion_gaussian_raw = np.asarray(rng.standard_normal((n_rotations, 4)), dtype=np.float64, order="C")
    if not np.all(np.isfinite(quaternion_gaussian_raw)):
        raise ValueError("raw Gaussian quaternions must be finite")
    norms = np.linalg.norm(quaternion_gaussian_raw, axis=1)
    if np.any(norms == 0):
        raise ValueError("raw Gaussian quaternion has zero norm")
    quaternion_unit_work = np.asarray(quaternion_gaussian_raw, dtype=target_dtype, order="C")
    quaternion_unit_work /= np.linalg.norm(quaternion_unit_work, axis=1, keepdims=True)
    quaternion_unit_work = canonicalize_quaternions(quaternion_unit_work)
    for quaternion in quaternion_unit_work:
        validate_canonical_unit_quaternion(quaternion)
    rotations = quaternions_to_rotations(quaternion_unit_work)
    del quaternion_gaussian_raw
    del quaternion_unit_work
    return rotations


def axis_angle_rotation(axis: Iterable[float], angle: float, dtype: Any = np.float64) -> np.ndarray:
    target_dtype = _float_dtype(dtype)
    vector = np.asarray(tuple(axis), dtype=target_dtype)
    _require_array("axis", vector, shape=(3,), dtype=target_dtype)
    if not math.isfinite(float(angle)):
        raise ValueError("angle must be finite")
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        raise ValueError("axis must be nonzero")
    x, y, z = vector / norm
    cosine = target_dtype.type(math.cos(float(angle)))
    sine = target_dtype.type(math.sin(float(angle)))
    one_minus = target_dtype.type(1.0) - cosine
    result = np.asarray(
        [
            [cosine + x * x * one_minus, x * y * one_minus - z * sine, x * z * one_minus + y * sine],
            [y * x * one_minus + z * sine, cosine + y * y * one_minus, y * z * one_minus - x * sine],
            [z * x * one_minus - y * sine, z * y * one_minus + x * sine, cosine + z * z * one_minus],
        ],
        dtype=target_dtype,
    )
    validate_rotation(result)
    return result


def _stf_basis(dtype: Any = np.float64) -> np.ndarray:
    target_dtype = _float_dtype(dtype)
    s2 = target_dtype.type(1.0 / math.sqrt(2.0))
    s6 = target_dtype.type(1.0 / math.sqrt(6.0))
    basis = np.asarray(
        [
            [[0, s2, 0], [s2, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, s2], [0, s2, 0]],
            [[0, 0, s2], [0, 0, 0], [s2, 0, 0]],
            [[s2, 0, 0], [0, -s2, 0], [0, 0, 0]],
            [[-s6, 0, 0], [0, -s6, 0], [0, 0, 2 * s6]],
        ],
        dtype=target_dtype,
    )
    validate_stf_basis(basis)
    return basis


def validate_stf_basis(basis: np.ndarray) -> None:
    if not isinstance(basis, np.ndarray):
        raise TypeError("STF basis must be a numpy array")
    dtype = _float_dtype(basis.dtype)
    _require_array("STF basis", basis, shape=(5, 3, 3), dtype=dtype)
    gram = np.einsum("aij,bij->ab", basis, basis)
    if normalized_residual(gram, np.eye(5, dtype=dtype)) > tolerance(dtype):
        raise ValueError("STF basis is not orthonormal")
    if max(float(np.linalg.norm(item - item.T)) for item in basis) > tolerance(dtype):
        raise ValueError("STF basis contains a nonsymmetric tensor")
    if max(abs(float(np.trace(item))) for item in basis) > tolerance(dtype):
        raise ValueError("STF basis contains a non-traceless tensor")


def d_representation(rotation: np.ndarray) -> np.ndarray:
    validate_rotation(rotation)
    basis = _stf_basis(rotation.dtype)
    transformed = np.einsum("ij,bjk,lk->bil", rotation, basis, rotation)
    result = np.einsum("aij,bij->ab", basis, transformed)
    return np.asarray(result, dtype=rotation.dtype, order="C")


def real_representation(rotation: np.ndarray, ell: int) -> np.ndarray:
    validate_rotation(rotation)
    if ell == 0:
        return np.ones((1, 1), dtype=rotation.dtype)
    if ell == 1:
        return np.array(rotation, copy=True, order="C")
    if ell == 2:
        return d_representation(rotation)
    raise ValueError("only ell=0,1,2 are supported")


def coefficient_bridge(ell: int, dtype: Any = np.float64) -> np.ndarray:
    real_dtype = _float_dtype(dtype)
    complex_dtype = _complex_dtype(real_dtype)
    s = 1.0 / math.sqrt(2.0)
    if ell == 0:
        return np.ones((1, 1), dtype=complex_dtype)
    if ell == 1:
        c = np.asarray([[s, -1j * s, 0], [0, 0, 1], [-s, -1j * s, 0]], dtype=complex_dtype)
        return np.conjugate(c)
    if ell == 2:
        c = np.asarray(
            [
                [-1j * s, 0, 0, s, 0],
                [0, -1j * s, s, 0, 0],
                [0, 0, 0, 0, 1],
                [0, -1j * s, -s, 0, 0],
                [1j * s, 0, 0, s, 0],
            ],
            dtype=complex_dtype,
        )
        return np.conjugate(c)
    raise ValueError("only ell=0,1,2 are supported")


def coefficient_bridge_payload(ell: int) -> str:
    if ell == 1:
        value = [
            "stageE-K-coeff-v1",
            1,
            ["px", "py", "pz"],
            [-1, 0, 1],
            [["1/sqrt2", "i/sqrt2", "0"], ["0", "0", "1"], ["-1/sqrt2", "i/sqrt2", "0"]],
        ]
    elif ell == 2:
        value = [
            "stageE-K-coeff-v1",
            2,
            ["dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"],
            [-2, -1, 0, 1, 2],
            [
                ["i/sqrt2", "0", "0", "1/sqrt2", "0"],
                ["0", "i/sqrt2", "1/sqrt2", "0", "0"],
                ["0", "0", "0", "0", "1"],
                ["0", "i/sqrt2", "-1/sqrt2", "0", "0"],
                ["-i/sqrt2", "0", "0", "1/sqrt2", "0"],
            ],
        ]
    else:
        raise ValueError("coefficient bridge payload is frozen only for ell=1,2")
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def coefficient_bridge_payload_hash(ell: int) -> str:
    return sha256_text(coefficient_bridge_payload(ell))


def complex_representation(rotation: np.ndarray, ell: int) -> np.ndarray:
    bridge = coefficient_bridge(ell, rotation.dtype)
    real = real_representation(rotation, ell)
    return np.asarray(bridge @ real @ bridge.conj().T, dtype=bridge.dtype, order="C")


def real_spherical_values(direction: np.ndarray, ell: int) -> np.ndarray:
    if not isinstance(direction, np.ndarray):
        raise TypeError("direction must be a numpy array")
    dtype = _float_dtype(direction.dtype)
    _require_array("direction", direction, shape=(3,), dtype=dtype)
    norm = float(np.linalg.norm(direction))
    if norm <= zero_tolerance(dtype):
        raise ValueError("direction is zero or below the frozen threshold")
    x, y, z = direction / norm
    if ell == 0:
        return np.asarray([1.0 / math.sqrt(4.0 * math.pi)], dtype=dtype)
    if ell == 1:
        return np.asarray(math.sqrt(3.0 / (4.0 * math.pi)) * np.asarray([x, y, z]), dtype=dtype)
    if ell == 2:
        return np.asarray(
            [
                math.sqrt(15.0 / (4.0 * math.pi)) * x * y,
                math.sqrt(15.0 / (4.0 * math.pi)) * y * z,
                math.sqrt(15.0 / (4.0 * math.pi)) * z * x,
                math.sqrt(15.0 / (16.0 * math.pi)) * (x * x - y * y),
                math.sqrt(5.0 / (16.0 * math.pi)) * (3.0 * z * z - 1.0),
            ],
            dtype=dtype,
        )
    raise ValueError("only ell=0,1,2 are supported")


def complex_spherical_values(direction: np.ndarray, ell: int) -> np.ndarray:
    bridge = coefficient_bridge(ell, direction.dtype)
    function_bridge = bridge.conj()
    return np.asarray(function_bridge @ real_spherical_values(direction, ell), dtype=bridge.dtype)


def coefficient_filter(direction: np.ndarray, ell: int) -> np.ndarray:
    return np.conjugate(complex_spherical_values(direction, ell))


def coefficient_filter_payload(ell: int) -> str:
    if ell not in (0, 1, 2):
        raise ValueError("filter payload is frozen only for ell=0,1,2")
    value = [
        FILTER_VERSION,
        "dlmf-cs-pointvalue-conjugate",
        ell,
        list(range(-ell, ell + 1)),
        "complex",
        "z=conjugate(y)",
    ]
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def coefficient_filter_payload_hash(ell: int) -> str:
    return sha256_text(coefficient_filter_payload(ell))


def _factorial(value: int) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("factorial argument must be a nonnegative int")
    return math.factorial(value)


def wigner_3j(j1: int, j2: int, j3: int, m1: int, m2: int, m3: int) -> float:
    values = (j1, j2, j3, m1, m2, m3)
    if any(type(value) is not int for value in values):
        raise TypeError("integer angular momenta are required")
    if min(j1, j2, j3) < 0 or m1 + m2 + m3 != 0:
        return 0.0
    if abs(m1) > j1 or abs(m2) > j2 or abs(m3) > j3:
        return 0.0
    if j3 < abs(j1 - j2) or j3 > j1 + j2:
        return 0.0
    delta = (
        _factorial(j1 + j2 - j3)
        * _factorial(j1 - j2 + j3)
        * _factorial(-j1 + j2 + j3)
        / _factorial(j1 + j2 + j3 + 1)
    )
    prefactor = (-1) ** (j1 - j2 - m3) * math.sqrt(delta)
    prefactor *= math.sqrt(
        _factorial(j1 + m1)
        * _factorial(j1 - m1)
        * _factorial(j2 + m2)
        * _factorial(j2 - m2)
        * _factorial(j3 + m3)
        * _factorial(j3 - m3)
    )
    lower = max(0, j2 - j3 - m1, j1 - j3 + m2)
    upper = min(j1 + j2 - j3, j1 - m1, j2 + m2)
    total = 0.0
    for z in range(lower, upper + 1):
        denominator = (
            _factorial(z)
            * _factorial(j1 + j2 - j3 - z)
            * _factorial(j1 - m1 - z)
            * _factorial(j2 + m2 - z)
            * _factorial(j3 - j2 + m1 + z)
            * _factorial(j3 - j1 - m2 + z)
        )
        total += (-1) ** z / denominator
    return float(prefactor * total)


def clebsch_gordan(j1: int, m1: int, j2: int, m2: int, total_j: int, total_m: int) -> float:
    if total_m != m1 + m2:
        return 0.0
    return float(
        (-1) ** (j1 - j2 + total_m)
        * math.sqrt(2 * total_j + 1)
        * wigner_3j(j1, j2, total_j, m1, m2, -total_m)
    )


def cg_matrix(j1: int, j2: int) -> tuple[np.ndarray, list[tuple[int, int]], list[tuple[int, int]]]:
    if type(j1) is not int or type(j2) is not int or min(j1, j2) < 0:
        raise ValueError("j1 and j2 must be nonnegative ints")
    inputs = [(m1, m2) for m1 in range(-j1, j1 + 1) for m2 in range(-j2, j2 + 1)]
    outputs = [
        (total_j, total_m)
        for total_j in range(abs(j1 - j2), j1 + j2 + 1)
        for total_m in range(-total_j, total_j + 1)
    ]
    matrix = np.asarray(
        [
            [clebsch_gordan(j1, m1, j2, m2, total_j, total_m) for m1, m2 in inputs]
            for total_j, total_m in outputs
        ],
        dtype=np.float64,
    )
    return matrix, outputs, inputs


def cg_couple(left: np.ndarray, right: np.ndarray, j1: int, j2: int) -> dict[int, np.ndarray]:
    complex_dtype = np.result_type(left.dtype, right.dtype)
    if complex_dtype not in (np.dtype(np.complex64), np.dtype(np.complex128)):
        raise TypeError("CG inputs must be complex64 or complex128")
    _require_array("left", left, shape=(2 * j1 + 1,), dtype=complex_dtype)
    _require_array("right", right, shape=(2 * j2 + 1,), dtype=complex_dtype)
    matrix, outputs, _ = cg_matrix(j1, j2)
    coupled = matrix.astype(complex_dtype) @ np.kron(left, right)
    result: dict[int, np.ndarray] = {}
    for total_j in range(abs(j1 - j2), j1 + j2 + 1):
        indices = [index for index, label in enumerate(outputs) if label[0] == total_j]
        result[total_j] = coupled[indices]
    return result


def block_diagonal(*blocks: np.ndarray) -> np.ndarray:
    if not blocks:
        raise ValueError("at least one block is required")
    dtype = np.result_type(*[block.dtype for block in blocks])
    rows = sum(block.shape[0] for block in blocks)
    columns = sum(block.shape[1] for block in blocks)
    output = np.zeros((rows, columns), dtype=dtype)
    row = 0
    column = 0
    for block in blocks:
        if not isinstance(block, np.ndarray) or block.ndim != 2:
            raise ValueError("each block must be a rank-2 numpy array")
        output[row : row + block.shape[0], column : column + block.shape[1]] = block
        row += block.shape[0]
        column += block.shape[1]
    return output


GRAPH_A_COORDINATES = np.asarray(
    [[0, 0, 0], [0.7, -0.2, 0.1], [1.1, 0.8, -0.3], [-0.4, 1.2, 0.6]],
    dtype=np.float64,
)
GRAPH_A_EDGES = ((0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3))
GRAPH_B_COORDINATES = np.asarray(
    [
        [0, 0, 0],
        [0.4, -0.7, 0.2],
        [1.3, 0.1, -0.5],
        [-0.2, 1.1, 0.7],
        [0.9, 1.4, -0.8],
        [-1.0, 0.3, 1.2],
        [0.2, -1.2, 0.9],
    ],
    dtype=np.float64,
)
GRAPH_B_PROTOTYPES = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (0, 6), (0, 3), (2, 5))


def edge_payload(structure_id: str, receiver: int, sender: int, shift: Iterable[int]) -> str:
    shift_tuple = tuple(shift)
    if not isinstance(structure_id, str) or not structure_id:
        raise ValueError("structure_id must be nonempty")
    if type(receiver) is not int or type(sender) is not int:
        raise TypeError("edge endpoints must be ints")
    if len(shift_tuple) != 3 or any(type(item) is not int for item in shift_tuple):
        raise ValueError("shift must contain three ints")
    return json.dumps(
        [EDGE_VERSION, structure_id, receiver, sender, *shift_tuple],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def parse_edge_payload(payload: str) -> tuple[str, int, int, tuple[int, int, int]]:
    if not isinstance(payload, str):
        raise TypeError("edge payload must be a string")
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("edge payload is not valid JSON") from error
    if not isinstance(decoded, list) or len(decoded) != 7 or decoded[0] != EDGE_VERSION:
        raise ValueError("edge payload version or field count is invalid")
    structure_id, receiver, sender = decoded[1:4]
    shift = tuple(decoded[4:7])
    canonical = edge_payload(structure_id, receiver, sender, shift)
    if canonical != payload:
        raise ValueError("edge payload is not in canonical byte form")
    return structure_id, receiver, sender, shift


def make_graph(seed: int, dtype: Any, scale: float) -> dict[str, Any]:
    target_dtype = _float_dtype(dtype)
    if seed not in SEEDS or type(seed) is not int:
        raise ValueError("seed must be a frozen stage E seed")
    if not math.isfinite(float(scale)) or float(scale) <= 0:
        raise ValueError("scale must be finite and positive")
    if seed == SEEDS[0]:
        coordinates = GRAPH_A_COORDINATES
        edges = GRAPH_A_EDGES
        graph_name = "G_A"
    else:
        coordinates = GRAPH_B_COORDINATES
        edges = tuple(item for a, b in GRAPH_B_PROTOTYPES for item in ((a, b), (b, a)))
        graph_name = "G_B"
    receiver = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    sender = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    shift = np.zeros((len(edges), 3), dtype=np.int64)
    structure_id = f"stageE-{graph_name}"
    payloads = [edge_payload(structure_id, int(i), int(j), (0, 0, 0)) for i, j in edges]
    return {
        "graph_name": graph_name,
        "structure_id": structure_id,
        "coordinates": np.asarray(coordinates * float(scale), dtype=target_dtype, order="C"),
        "receiver": receiver,
        "sender": sender,
        "shift": shift,
        "edge_payload": payloads,
        "edge_id": [sha256_text(payload) for payload in payloads],
    }


def _representation_metadata() -> dict[str, Any]:
    return {
        "basis": {"0": "real-s", "1": "real-p-xyz", "2": "real-d-stf-xy-yz-zx-x2y2-3z2r2"},
        "component_order": {"0": ["s"], "1": ["px", "py", "pz"], "2": ["dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"]},
        "m_order": {"0": [0], "1": [-1, 0, 1], "2": [-2, -1, 0, 1, 2]},
        "parity": {"0": 1, "1": -1, "2": 1},
    }


def _m8_boundary() -> dict[str, str]:
    return {
        "material_system": UNRESOLVED_M8,
        "dft_backend": UNRESOLVED_M8,
        "data_backend": UNRESOLVED_M8,
        "deeph_software_object": UNRESOLVED_M8,
        "training_budget": UNRESOLVED_M8,
        "advanced_physics_scope": UNRESOLVED_M8,
    }


def _make_case(
    dtype: Any,
    seed: int,
    n_rotations: int,
    multiplicity: tuple[int, int, int],
    scale: float,
    *,
    mode: str,
    config_id: str | None,
    multiplier: int | None,
) -> dict[str, Any]:
    target_dtype = _float_dtype(dtype)
    if seed not in SEEDS or type(seed) is not int:
        raise ValueError("seed must be frozen")
    if type(n_rotations) is not int or n_rotations <= 0:
        raise ValueError("n_rotations must be a positive int")
    if len(multiplicity) != 3 or any(type(value) is not int or value <= 0 for value in multiplicity):
        raise ValueError("multiplicity must contain three positive ints")
    if not math.isfinite(float(scale)) or float(scale) <= 0:
        raise ValueError("scale must be finite and positive")
    graph = make_graph(seed, target_dtype, float(scale))
    rng = np.random.Generator(np.random.PCG64(seed))
    rotations = random_rotations(rng, n_rotations, target_dtype)
    node_count = graph["coordinates"].shape[0]
    edge_count = graph["receiver"].shape[0]
    features: dict[str, np.ndarray] = {}
    weights: dict[str, np.ndarray] = {}
    for ell, count in enumerate(multiplicity):
        raw = rng.standard_normal((node_count, count, 2 * ell + 1))
        features[str(ell)] = np.asarray(raw * float(scale), dtype=target_dtype, order="C")
    for ell, count in enumerate(multiplicity):
        raw = rng.standard_normal((edge_count, count, count))
        weights[str(ell)] = np.asarray(raw, dtype=target_dtype, order="C")
    case = {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "config_id": config_id,
        "seed": seed,
        "dtype": target_dtype.name,
        "n_rotations": n_rotations,
        "multiplier": multiplier,
        "multiplicity": multiplicity,
        "scale": float(scale),
        "graph": graph,
        "rotations": rotations,
        "x": features,
        "W": weights,
        "representation_metadata": _representation_metadata(),
        "m8_boundary": _m8_boundary(),
    }
    validate_case(case)
    return case


def make_scan_case(dtype: Any, seed: int, n_rotations: int, multiplier: int, scale: float) -> dict[str, Any]:
    if n_rotations not in SCAN_ROTATION_COUNTS or type(n_rotations) is not int:
        raise ValueError("n_rotations must be on the frozen scan axis")
    if multiplier not in SCAN_MULTIPLIERS or type(multiplier) is not int:
        raise ValueError("multiplier must be on the frozen scan axis")
    if float(scale) not in SCAN_SCALES:
        raise ValueError("scale must be on the frozen scan axis")
    return _make_case(
        dtype,
        seed,
        n_rotations,
        tuple(multiplier * item for item in (2, 2, 1)),
        float(scale),
        mode="stageE-scan-v1",
        config_id=None,
        multiplier=multiplier,
    )


def make_config_case(config_id: str) -> dict[str, Any]:
    if config_id not in CONFIG_CASES:
        raise ValueError("config_id must be A or B")
    config = CONFIG_CASES[config_id]
    return _make_case(
        config["dtype"],
        config["seed"],
        config["n_rotations"],
        config["multiplicity"],
        config["scale"],
        mode="stageE-config-v1",
        config_id=config_id,
        multiplier=None,
    )


def validate_case(case: dict[str, Any]) -> None:
    if not isinstance(case, dict):
        raise TypeError("case must be a dict")
    expected = {
        "schema_version", "mode", "config_id", "seed", "dtype", "n_rotations", "multiplier", "multiplicity",
        "scale", "graph", "rotations", "x", "W", "representation_metadata", "m8_boundary",
    }
    if set(case) != expected:
        raise ValueError("case fields do not match stage E schema")
    if case["schema_version"] != SCHEMA_VERSION or case["mode"] not in {"stageE-scan-v1", "stageE-config-v1"}:
        raise ValueError("case version or mode is invalid")
    dtype = _float_dtype(case["dtype"])
    seed = case["seed"]
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("case seed is invalid")
    n_rotations = case["n_rotations"]
    multiplier = case["multiplier"]
    scale = case["scale"]
    if case["mode"] == "stageE-scan-v1":
        if case["config_id"] is not None:
            raise ValueError("scan case cannot carry config_id")
        if type(n_rotations) is not int or n_rotations not in SCAN_ROTATION_COUNTS:
            raise ValueError("scan n_rotations is invalid")
        if type(multiplier) is not int or multiplier not in SCAN_MULTIPLIERS:
            raise ValueError("scan multiplier is invalid")
        if tuple(case["multiplicity"]) != tuple(multiplier * item for item in (2, 2, 1)):
            raise ValueError("scan multiplicity is inconsistent")
        if type(scale) is not float or scale not in SCAN_SCALES:
            raise ValueError("scan scale is invalid")
    else:
        config_id = case["config_id"]
        if config_id not in CONFIG_CASES or multiplier is not None:
            raise ValueError("config case identity is invalid")
        config = CONFIG_CASES[config_id]
        if (
            seed != config["seed"]
            or dtype.name != config["dtype"]
            or n_rotations != config["n_rotations"]
            or tuple(case["multiplicity"]) != config["multiplicity"]
            or scale != config["scale"]
        ):
            raise ValueError("config case fields conflict with frozen config")
    graph = case["graph"]
    if not isinstance(graph, dict) or set(graph) != {
        "graph_name", "structure_id", "coordinates", "receiver", "sender", "shift", "edge_payload", "edge_id"
    }:
        raise ValueError("graph fields are invalid")
    expected_graph = make_graph(seed, dtype, scale)
    for name in ("graph_name", "structure_id", "edge_payload", "edge_id"):
        if graph[name] != expected_graph[name]:
            raise ValueError(f"graph {name} is inconsistent")
    for name in ("coordinates", "receiver", "sender", "shift"):
        expected_array = expected_graph[name]
        _require_array(name, graph[name], shape=expected_array.shape, dtype=expected_array.dtype)
        if not np.array_equal(graph[name], expected_array):
            raise ValueError(f"graph {name} is inconsistent")
    rotations = _require_array("rotations", case["rotations"], shape=(n_rotations, 3, 3), dtype=dtype)
    for rotation in rotations:
        validate_rotation(rotation)
    node_count = graph["coordinates"].shape[0]
    edge_count = graph["receiver"].shape[0]
    if not isinstance(case["x"], dict) or not isinstance(case["W"], dict):
        raise TypeError("x and W must be dicts")
    if set(case["x"]) != {"0", "1", "2"} or set(case["W"]) != {"0", "1", "2"}:
        raise ValueError("x and W must contain ell=0,1,2 exactly")
    for ell, count in enumerate(case["multiplicity"]):
        _require_array(f"x_{ell}", case["x"][str(ell)], shape=(node_count, count, 2 * ell + 1), dtype=dtype)
        _require_array(f"W_{ell}", case["W"][str(ell)], shape=(edge_count, count, count), dtype=dtype)
    if case["representation_metadata"] != _representation_metadata():
        raise ValueError("representation metadata is inconsistent")
    if case["m8_boundary"] != _m8_boundary():
        raise ValueError("M8 boundary sentinels are inconsistent")


def reference_kernel(case: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    validate_case(case)
    receiver = case["graph"]["receiver"]
    sender = case["graph"]["sender"]
    node_count = case["graph"]["coordinates"].shape[0]
    messages: dict[str, np.ndarray] = {}
    outputs: dict[str, np.ndarray] = {}
    for ell in range(3):
        key = str(ell)
        x = case["x"][key]
        weight = case["W"][key]
        message = np.einsum("eab,ebk->eak", weight, x[sender], optimize=False)
        output = np.zeros((node_count, x.shape[1], x.shape[2]), dtype=x.dtype)
        for edge, node in enumerate(receiver):
            output[int(node)] += message[edge]
        messages[key] = np.asarray(message, dtype=x.dtype, order="C")
        outputs[key] = output
    return messages, outputs


def array_summary(case: dict[str, Any]) -> dict[str, Any]:
    messages, outputs = reference_kernel(case)
    arrays: dict[str, np.ndarray] = {
        "coordinates": case["graph"]["coordinates"],
        "receiver": case["graph"]["receiver"],
        "sender": case["graph"]["sender"],
        "shift": case["graph"]["shift"],
        "rotations": case["rotations"],
    }
    for ell in range(3):
        key = str(ell)
        arrays[f"x_{ell}"] = case["x"][key]
        arrays[f"W_{ell}"] = case["W"][key]
        arrays[f"m_{ell}"] = messages[key]
        arrays[f"h_{ell}"] = outputs[key]
    detail = {
        name: {"shape": list(array.shape), "dtype": array.dtype.name, "nbytes": int(array.nbytes)}
        for name, array in arrays.items()
    }
    total = sum(item["nbytes"] for item in detail.values())
    message_bytes = [detail[f"m_{ell}"]["nbytes"] for ell in range(3)]
    peak = total - sum(message_bytes) + max(message_bytes)
    return {"arrays": detail, "array_bytes_total": total, "array_bytes_peak": peak}


def reference_cost(case: dict[str, Any]) -> dict[str, int]:
    validate_case(case)
    edge_count = int(case["graph"]["receiver"].shape[0])
    multiplicity = tuple(int(value) for value in case["multiplicity"])
    mac_per_rotation = sum(edge_count * count * count * (2 * ell + 1) for ell, count in enumerate(multiplicity))
    indegree = np.bincount(case["graph"]["receiver"], minlength=case["graph"]["coordinates"].shape[0])
    aggregation_factor = int(np.maximum(indegree - 1, 0).sum())
    aggregation_per_rotation = sum(
        aggregation_factor * count * (2 * ell + 1) for ell, count in enumerate(multiplicity)
    )
    n_rotations = int(case["n_rotations"])
    return {
        "mac_per_rotation": mac_per_rotation,
        "mac_total": n_rotations * mac_per_rotation,
        "flop_total": 2 * n_rotations * mac_per_rotation,
        "aggregation_add_per_rotation": aggregation_per_rotation,
        "aggregation_add_total": n_rotations * aggregation_per_rotation,
    }


def reference_equivariance(case: dict[str, Any]) -> dict[str, Any]:
    _, base_outputs = reference_kernel(case)
    sender = case["graph"]["sender"]
    receiver = case["graph"]["receiver"]
    node_count = case["graph"]["coordinates"].shape[0]
    maximum = 0.0
    worst = {"rotation": 0, "ell": 0}
    for rotation_index, rotation in enumerate(case["rotations"]):
        for ell in range(3):
            key = str(ell)
            representation = real_representation(rotation, ell)
            rotated_x = np.einsum("nak,pk->nap", case["x"][key], representation, optimize=False)
            rotated_message = np.einsum("eab,ebk->eak", case["W"][key], rotated_x[sender], optimize=False)
            rotated_output = np.zeros((node_count, rotated_x.shape[1], rotated_x.shape[2]), dtype=rotated_x.dtype)
            for edge, node in enumerate(receiver):
                rotated_output[int(node)] += rotated_message[edge]
            expected = np.einsum("nak,pk->nap", base_outputs[key], representation, optimize=False)
            residual = normalized_residual(rotated_output, expected)
            if residual > maximum:
                maximum = residual
                worst = {"rotation": rotation_index, "ell": ell}
    return {"max_residual": maximum, "worst": worst, "threshold": tolerance(case["dtype"])}


def local_frame(u: np.ndarray, v: np.ndarray, scale: float) -> tuple[np.ndarray, dict[str, float]]:
    if not isinstance(u, np.ndarray) or not isinstance(v, np.ndarray):
        raise TypeError("local-frame vectors must be numpy arrays")
    if u.dtype != v.dtype:
        raise TypeError("local-frame vectors must have the same dtype")
    dtype = _float_dtype(u.dtype)
    _require_array("u", u, shape=(3,), dtype=dtype)
    _require_array("v", v, shape=(3,), dtype=dtype)
    if type(scale) is not float or not math.isfinite(scale) or scale <= 0:
        raise ValueError("local-frame scale must be a finite positive float")
    zeta_u = float(np.linalg.norm(u)) / scale
    zeta_v = float(np.linalg.norm(v)) / scale
    if zeta_u <= zero_tolerance(dtype) or zeta_v <= zero_tolerance(dtype):
        raise ValueError("local-frame vector is on the zero-length rejection side")
    u_hat = u / np.linalg.norm(u)
    v_hat = v / np.linalg.norm(v)
    eta = float(np.linalg.norm(np.cross(u_hat, v_hat)))
    if eta <= frame_tolerance(dtype):
        raise ValueError("local frame is on the collinear rejection side")
    e1 = u_hat
    raw_e2 = v_hat - np.dot(e1, v_hat) * e1
    e2 = raw_e2 / np.linalg.norm(raw_e2)
    e3 = np.cross(e1, e2)
    frame = np.column_stack((e1, e2, e3)).astype(dtype, copy=False)
    validate_rotation(frame)
    return frame, {"zeta_u": zeta_u, "zeta_v": zeta_v, "eta": eta}


def su2_from_quaternion(quaternion: np.ndarray) -> np.ndarray:
    validate_unit_quaternion(quaternion)
    complex_dtype = _complex_dtype(quaternion.dtype)
    w, x, y, z = (float(value) for value in quaternion)
    return np.asarray(
        [[w - 1j * z, -y - 1j * x], [y - 1j * x, w + 1j * z]],
        dtype=complex_dtype,
    )


def pauli_matrices(dtype: Any = np.float64) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    complex_dtype = _complex_dtype(dtype)
    return (
        np.asarray([[0, 1], [1, 0]], dtype=complex_dtype),
        np.asarray([[0, -1j], [1j, 0]], dtype=complex_dtype),
        np.asarray([[1, 0], [0, -1]], dtype=complex_dtype),
    )


def orbital_time_reversal(ell: int, dtype: Any = np.float64) -> np.ndarray:
    if type(ell) is not int or ell < 0:
        raise ValueError("ell must be a nonnegative int")
    complex_dtype = _complex_dtype(dtype)
    m_values = list(range(-ell, ell + 1))
    result = np.zeros((2 * ell + 1, 2 * ell + 1), dtype=complex_dtype)
    for column, m_value in enumerate(m_values):
        row = m_values.index(-m_value)
        result[row, column] = (-1) ** m_value
    return result


def spin_time_reversal(dtype: Any = np.float64) -> np.ndarray:
    return np.asarray([[0, 1], [-1, 0]], dtype=_complex_dtype(dtype))


def time_reversal_payloads() -> dict[str, dict[str, str]]:
    values = {
        "spinless_real": [
            TIME_REVERSAL_VERSION,
            "spinless-real",
            "real-orbital",
            "complex",
            "Theta=K",
            "Theta2=+I",
        ],
        "spin_half": [
            TIME_REVERSAL_VERSION,
            "spin-half",
            [0.5, -0.5],
            "complex128",
            "J=i*sigma_y",
            [[[0, 0], [1, 0]], [[-1, 0], [0, 0]]],
        ],
        "orbital_l1": [
            TIME_REVERSAL_VERSION,
            "orbital-l1",
            [-1, 0, 1],
            "complex128",
            "J=K1@K1.T",
            [
                [[0, 0], [0, 0], [-1, 0]],
                [[0, 0], [1, 0], [0, 0]],
                [[-1, 0], [0, 0], [0, 0]],
            ],
        ],
    }
    result: dict[str, dict[str, str]] = {}
    for name, value in values.items():
        payload = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        result[name] = {"payload": payload, "sha256": sha256_text(payload)}
    return result


def time_reverse(vector: np.ndarray, unitary_part: np.ndarray) -> np.ndarray:
    if not isinstance(vector, np.ndarray) or not isinstance(unitary_part, np.ndarray):
        raise TypeError("time-reversal inputs must be numpy arrays")
    if vector.ndim != 1 or unitary_part.shape != (vector.shape[0], vector.shape[0]):
        raise ValueError("time-reversal shapes are inconsistent")
    if vector.dtype != unitary_part.dtype or vector.dtype not in (np.dtype(np.complex64), np.dtype(np.complex128)):
        raise TypeError("time-reversal inputs must share a complex dtype")
    if not np.all(np.isfinite(vector)) or not np.all(np.isfinite(unitary_part)):
        raise ValueError("time-reversal inputs must be finite")
    return unitary_part @ vector.conj()


def make_time_reversal_pair(dtype: Any = np.float64) -> dict[str, Any]:
    real_dtype = _float_dtype(dtype)
    complex_dtype = _complex_dtype(real_dtype)
    pair = {
        "schema_version": TIME_REVERSAL_PAIR_VERSION,
        "dtype": real_dtype.name,
        "k_id": "stageE-k-general-001",
        "minus_k_id": "stageE-minus-k-general-001",
        "kpoint": np.asarray([0.2, -0.1, 0.3], dtype=real_dtype),
        "minus_kpoint": np.asarray([-0.2, 0.1, -0.3], dtype=real_dtype),
        "orbital_ids": ["spin+1/2", "spin-1/2"],
        "partner_orbital_ids": ["spin+1/2", "spin-1/2"],
        "partner_map": [1, 0],
        "active_mask": np.ones((2, 2), dtype=np.bool_),
        "H_k": np.asarray([[0.4, 0.2 + 0.3j], [0.2 - 0.3j, -0.1]], dtype=complex_dtype),
        "H_minus_k": np.asarray([[-0.1, -0.2 - 0.3j], [-0.2 + 0.3j, 0.4]], dtype=complex_dtype),
        "S_k": np.asarray([[1.2, 0.05 + 0.02j], [0.05 - 0.02j, 1.1]], dtype=complex_dtype),
        "S_minus_k": np.asarray([[1.1, -0.05 - 0.02j], [-0.05 + 0.02j, 1.2]], dtype=complex_dtype),
    }
    validate_time_reversal_pair(pair)
    return pair


def validate_time_reversal_pair(pair: dict[str, Any]) -> None:
    expected = {
        "schema_version", "dtype", "k_id", "minus_k_id", "kpoint", "minus_kpoint", "orbital_ids",
        "partner_orbital_ids", "partner_map", "active_mask", "H_k", "H_minus_k", "S_k", "S_minus_k",
    }
    if not isinstance(pair, dict) or set(pair) != expected:
        raise ValueError("time-reversal pair fields are invalid")
    if pair["schema_version"] != TIME_REVERSAL_PAIR_VERSION:
        raise ValueError("time-reversal pair version is invalid")
    real_dtype = _float_dtype(pair["dtype"])
    complex_dtype = _complex_dtype(real_dtype)
    if pair["k_id"] != "stageE-k-general-001" or pair["minus_k_id"] != "stageE-minus-k-general-001":
        raise ValueError("time-reversal partner identity is invalid")
    if pair["orbital_ids"] != ["spin+1/2", "spin-1/2"] or pair["partner_orbital_ids"] != pair["orbital_ids"]:
        raise ValueError("time-reversal orbital row identity is invalid")
    if pair["partner_map"] != [1, 0]:
        raise ValueError("time-reversal partner map is invalid")
    kpoint = _require_array("kpoint", pair["kpoint"], shape=(3,), dtype=real_dtype)
    minus_kpoint = _require_array("minus_kpoint", pair["minus_kpoint"], shape=(3,), dtype=real_dtype)
    if not np.array_equal(minus_kpoint, -kpoint) or np.array_equal(kpoint, np.zeros(3, dtype=real_dtype)):
        raise ValueError("time-reversal k/-k points are inconsistent or not a general-k fixture")
    mask = _require_array("time-reversal active mask", pair["active_mask"], shape=(2, 2), dtype=np.dtype(np.bool_), finite=False)
    if not np.all(mask):
        raise ValueError("time-reversal teaching pair must have a complete active mask")
    matrices = {
        name: _require_array(name, pair[name], shape=(2, 2), dtype=complex_dtype)
        for name in ("H_k", "H_minus_k", "S_k", "S_minus_k")
    }
    tau = tolerance(real_dtype)
    for name, matrix in matrices.items():
        if normalized_residual(matrix, matrix.conj().T) > tau:
            raise ValueError(f"{name} is not Hermitian")
    if min(float(np.min(np.linalg.eigvalsh(matrices[name]))) for name in ("S_k", "S_minus_k")) <= 0:
        raise ValueError("time-reversal overlap matrix is not positive definite")
    unitary = spin_time_reversal(real_dtype)
    for name in ("H", "S"):
        expected_partner = unitary @ matrices[f"{name}_k"].conj() @ unitary.conj().T
        if normalized_residual(matrices[f"{name}_minus_k"], expected_partner) > tau:
            raise ValueError(f"{name} k/-k time-reversal relation is invalid")


def make_irrep_batch(dtype: Any = np.float64) -> dict[str, Any]:
    target_dtype = _float_dtype(dtype)
    node_mask = np.asarray([[True, True, False], [True, False, False]], dtype=np.bool_)
    values: dict[str, np.ndarray] = {}
    component_mask: dict[str, np.ndarray] = {}
    for ell, count in enumerate((2, 2, 1)):
        array = np.full((2, 3, count, 2 * ell + 1), np.nan, dtype=target_dtype)
        mask = np.zeros(array.shape, dtype=np.bool_)
        for batch in range(2):
            for node in range(3):
                if node_mask[batch, node]:
                    array[batch, node] = target_dtype.type((batch + 1) * (node + 1) * (ell + 1))
                    mask[batch, node] = True
        values[str(ell)] = array
        component_mask[str(ell)] = mask
    batch = {
        "schema_version": BATCH_VERSION,
        "dtype": target_dtype.name,
        "node_mask": node_mask,
        "values": values,
        "component_mask": component_mask,
        "metadata": _representation_metadata(),
    }
    validate_irrep_batch(batch)
    return batch


def validate_irrep_batch(batch: dict[str, Any]) -> None:
    if not isinstance(batch, dict) or set(batch) != {
        "schema_version", "dtype", "node_mask", "values", "component_mask", "metadata"
    }:
        raise ValueError("irrep batch fields are invalid")
    if batch["schema_version"] != BATCH_VERSION:
        raise ValueError("irrep batch version is invalid")
    dtype = _float_dtype(batch["dtype"])
    node_mask = _require_array("node_mask", batch["node_mask"], shape=(2, 3), dtype=np.dtype(np.bool_), finite=False)
    for row in node_mask:
        if np.any(np.diff(row.astype(np.int8)) > 0):
            raise ValueError("node mask must be a left-contiguous prefix")
    if set(batch["values"]) != {"0", "1", "2"} or set(batch["component_mask"]) != {"0", "1", "2"}:
        raise ValueError("irrep batch must contain ell=0,1,2")
    for ell, count in enumerate((2, 2, 1)):
        shape = (2, 3, count, 2 * ell + 1)
        values = _require_array(f"values_{ell}", batch["values"][str(ell)], shape=shape, dtype=dtype, finite=False)
        mask = _require_array(
            f"component_mask_{ell}", batch["component_mask"][str(ell)], shape=shape, dtype=np.dtype(np.bool_), finite=False
        )
        shell_mask = np.broadcast_to(node_mask[:, :, None, None], shape)
        if not np.array_equal(mask, shell_mask):
            raise ValueError("complete irrep shell mask must be all true or all false")
        if not np.all(np.isfinite(values[mask])):
            raise ValueError("active irrep values must be finite")
    if batch["metadata"] != _representation_metadata():
        raise ValueError("irrep batch metadata is inconsistent")


def padded_irrep_linear(batch: dict[str, Any], weights: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    validate_irrep_batch(batch)
    dtype = _float_dtype(batch["dtype"])
    if not isinstance(weights, dict) or set(weights) != {"0", "1", "2"}:
        raise ValueError("padded linear weights must contain ell=0,1,2")
    outputs: dict[str, np.ndarray] = {}
    for ell, count in enumerate((2, 2, 1)):
        key = str(ell)
        weight = _require_array(f"padded_weight_{ell}", weights[key], shape=(count, count), dtype=dtype)
        values = batch["values"][key]
        output = np.zeros(values.shape, dtype=dtype)
        for batch_index in range(values.shape[0]):
            active_count = int(batch["node_mask"][batch_index].sum())
            active_values = values[batch_index, :active_count]
            output[batch_index, :active_count] = np.einsum("ab,nbk->nak", weight, active_values, optimize=False)
        outputs[key] = output
    return outputs


def masked_irrep_mse(
    prediction: dict[str, np.ndarray],
    target: dict[str, np.ndarray],
    batch: dict[str, Any],
) -> float:
    validate_irrep_batch(batch)
    if set(prediction) != {"0", "1", "2"} or set(target) != {"0", "1", "2"}:
        raise ValueError("prediction and target must contain ell=0,1,2")
    squared_sum = 0.0
    count = 0
    dtype = _float_dtype(batch["dtype"])
    for ell in range(3):
        key = str(ell)
        shape = batch["values"][key].shape
        predicted = _require_array(f"prediction_{ell}", prediction[key], shape=shape, dtype=dtype, finite=False)
        expected = _require_array(f"target_{ell}", target[key], shape=shape, dtype=dtype, finite=False)
        mask = batch["component_mask"][key]
        if not np.all(np.isfinite(predicted[mask])) or not np.all(np.isfinite(expected[mask])):
            raise ValueError("active loss entries must be finite")
        difference = predicted[mask] - expected[mask]
        squared_sum += float(np.dot(difference, difference))
        count += int(difference.size)
    if count == 0:
        raise ValueError("masked loss has no active entries")
    return squared_sum / count


def make_message_provenance(graph: dict[str, Any], directions: np.ndarray) -> dict[str, Any]:
    edge_count = len(graph["edge_id"])
    dtype = _float_dtype(directions.dtype)
    _require_array("directions", directions, shape=(edge_count, 3), dtype=dtype)
    provenance = {
        "schema_version": FILTER_VERSION,
        "edge_id": list(graph["edge_id"]),
        "receiver": np.array(graph["receiver"], copy=True),
        "sender": np.array(graph["sender"], copy=True),
        "shift": np.array(graph["shift"], copy=True),
        "direction": np.array(directions, copy=True),
        "m_order": [-1, 0, 1],
        "basis": "DLMF-CS-coefficient",
        "cg_table_sha256": CG_DLMF_TABLE_SHA256,
        "input_irrep": [1, -1],
        "filter_irrep": [1, -1],
        "output_irreps": [0, 1, 2],
        "output_irreps_with_parity": [[0, 1], [1, 1], [2, 1]],
    }
    validate_message_provenance(graph, provenance)
    return provenance


def validate_message_provenance(
    graph: dict[str, Any],
    provenance: dict[str, Any],
    directions: np.ndarray | None = None,
) -> None:
    expected_graph_fields = {
        "graph_name", "structure_id", "coordinates", "receiver", "sender", "shift", "edge_payload", "edge_id"
    }
    if not isinstance(graph, dict) or set(graph) != expected_graph_fields:
        raise ValueError("message graph fields are invalid")
    dtype = _float_dtype(graph["coordinates"].dtype)
    node_count = int(graph["coordinates"].shape[0])
    edge_count = len(graph["edge_id"])
    _require_array("message coordinates", graph["coordinates"], shape=(node_count, 3), dtype=dtype)
    _require_array("message receiver", graph["receiver"], shape=(edge_count,), dtype=np.dtype(np.int64))
    _require_array("message sender", graph["sender"], shape=(edge_count,), dtype=np.dtype(np.int64))
    _require_array("message shift", graph["shift"], shape=(edge_count, 3), dtype=np.dtype(np.int64))
    if np.any(graph["receiver"] < 0) or np.any(graph["receiver"] >= node_count) or np.any(graph["sender"] < 0) or np.any(graph["sender"] >= node_count):
        raise ValueError("message graph endpoints are out of range")
    if not isinstance(graph["edge_payload"], list) or len(graph["edge_payload"]) != edge_count:
        raise ValueError("message graph payload rows are invalid")
    if not isinstance(provenance, dict) or set(provenance) != {
        "schema_version", "edge_id", "receiver", "sender", "shift", "direction", "m_order", "basis",
        "cg_table_sha256", "input_irrep", "filter_irrep", "output_irreps", "output_irreps_with_parity",
    }:
        raise ValueError("message provenance fields are invalid")
    if provenance["schema_version"] != FILTER_VERSION or provenance["basis"] != "DLMF-CS-coefficient":
        raise ValueError("message provenance version or basis is invalid")
    if (
        provenance["m_order"] != [-1, 0, 1]
        or provenance["cg_table_sha256"] != CG_DLMF_TABLE_SHA256
        or provenance["input_irrep"] != [1, -1]
        or provenance["filter_irrep"] != [1, -1]
        or provenance["output_irreps"] != [0, 1, 2]
        or provenance["output_irreps_with_parity"] != [[0, 1], [1, 1], [2, 1]]
        or provenance["edge_id"] != graph["edge_id"]
    ):
        raise ValueError("message provenance identity is inconsistent")
    for name in ("receiver", "sender", "shift"):
        if not np.array_equal(provenance[name], graph[name]):
            raise ValueError(f"message provenance {name} is inconsistent")
    _require_array("direction", provenance["direction"], shape=(edge_count, 3), dtype=dtype)
    if np.any(np.linalg.norm(provenance["direction"], axis=1) <= zero_tolerance(dtype)):
        raise ValueError("message direction must be nonzero")
    for row in range(edge_count):
        structure_id, receiver, sender, shift = parse_edge_payload(graph["edge_payload"][row])
        if (
            structure_id != graph["structure_id"]
            or receiver != int(graph["receiver"][row])
            or sender != int(graph["sender"][row])
            or shift != tuple(int(item) for item in graph["shift"][row])
            or sha256_text(graph["edge_payload"][row]) != graph["edge_id"][row]
        ):
            raise ValueError("message graph edge identity is inconsistent")
    if directions is not None:
        _require_array("directions", directions, shape=(edge_count, 3), dtype=dtype)
        if not np.array_equal(directions, provenance["direction"]):
            raise ValueError("message directions are stale or row-misaligned relative to provenance")


def fixed_hamiltonian(dtype: Any = np.float64) -> np.ndarray:
    target_dtype = _float_dtype(dtype)
    return np.asarray([[0.1 * (8 * row + column + 1) for column in range(8)] for row in range(4)], dtype=target_dtype)


def make_hamiltonian_edge(dtype: Any = np.float64, *, reverse: bool = False) -> dict[str, Any]:
    target_dtype = _float_dtype(dtype)
    if type(reverse) is not bool:
        raise TypeError("reverse must be bool")
    forward_block = fixed_hamiltonian(target_dtype)
    if reverse:
        receiver, sender, shift = 1, 0, (0, 0, 0)
        block = np.asarray(
            [[0.1 * (8 * column + row + 1) for column in range(4)] for row in range(8)],
            dtype=target_dtype,
            order="C",
        )
        receiver_shells = ["p0", "d0"]
        sender_shells = ["s0", "p0"]
        receiver_orbitals = ["px", "py", "pz", "dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"]
        sender_orbitals = ["s", "px", "py", "pz"]
    else:
        receiver, sender, shift = 0, 1, (0, 0, 0)
        block = forward_block
        receiver_shells = ["s0", "p0"]
        sender_shells = ["p0", "d0"]
        receiver_orbitals = ["s", "px", "py", "pz"]
        sender_orbitals = ["px", "py", "pz", "dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"]
    structure_id = "stageE-H"
    result = {
        "schema_version": HAMILTONIAN_VERSION,
        "structure_id": structure_id,
        "receiver": receiver,
        "sender": sender,
        "shift": shift,
        "edge_payload": edge_payload(structure_id, receiver, sender, shift),
        "edge_id": "",
        "block": block,
        "mask": np.ones(block.shape, dtype=np.bool_),
        "receiver_shells": receiver_shells,
        "sender_shells": sender_shells,
        "receiver_orbitals": receiver_orbitals,
        "sender_orbitals": sender_orbitals,
        "basis": "real-s-p-d-frozen",
        "unit": "synthetic-arbitrary-unit",
    }
    result["edge_id"] = sha256_text(result["edge_payload"])
    validate_hamiltonian_edge(result)
    return result


def validate_hamiltonian_edge(row: dict[str, Any]) -> None:
    expected = {
        "schema_version", "structure_id", "receiver", "sender", "shift", "edge_payload", "edge_id", "block",
        "mask", "receiver_shells", "sender_shells", "receiver_orbitals", "sender_orbitals", "basis", "unit",
    }
    if not isinstance(row, dict) or set(row) != expected:
        raise ValueError("Hamiltonian edge fields are invalid")
    if row["schema_version"] != HAMILTONIAN_VERSION or row["basis"] != "real-s-p-d-frozen":
        raise ValueError("Hamiltonian edge version or basis is invalid")
    structure_id, receiver, sender, shift = parse_edge_payload(row["edge_payload"])
    if (
        row["structure_id"] != structure_id
        or type(row["receiver"]) is not int
        or type(row["sender"]) is not int
        or row["receiver"] != receiver
        or row["sender"] != sender
        or not isinstance(row["shift"], tuple)
        or row["shift"] != shift
        or row["edge_payload"] != edge_payload(structure_id, receiver, sender, shift)
        or row["edge_id"] != sha256_text(row["edge_payload"])
    ):
        raise ValueError("Hamiltonian edge identity hash is invalid")
    if structure_id != "stageE-H" or shift != (0, 0, 0) or (receiver, sender) not in {(0, 1), (1, 0)}:
        raise ValueError("Hamiltonian edge is outside the frozen teaching pair")
    forward = (receiver, sender) == (0, 1)
    expected_receiver_shells = ["s0", "p0"] if forward else ["p0", "d0"]
    expected_sender_shells = ["p0", "d0"] if forward else ["s0", "p0"]
    expected_receiver_orbitals = (
        ["s", "px", "py", "pz"]
        if forward
        else ["px", "py", "pz", "dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"]
    )
    expected_sender_orbitals = (
        ["px", "py", "pz", "dxy", "dyz", "dzx", "dx2-y2", "d3z2-r2"]
        if forward
        else ["s", "px", "py", "pz"]
    )
    if row["receiver_shells"] != expected_receiver_shells or row["sender_shells"] != expected_sender_shells:
        raise ValueError("Hamiltonian shell identity is invalid")
    if row["receiver_orbitals"] != expected_receiver_orbitals:
        raise ValueError("Hamiltonian receiver orbital identity is invalid")
    if row["sender_orbitals"] != expected_sender_orbitals:
        raise ValueError("Hamiltonian sender orbital identity is invalid")
    if not isinstance(row["block"], np.ndarray) or row["block"].dtype not in FLOAT_DTYPES:
        raise TypeError("Hamiltonian block must use float32 or float64")
    dtype = row["block"].dtype
    shape = (len(expected_receiver_orbitals), len(expected_sender_orbitals))
    _require_array("Hamiltonian block", row["block"], shape=shape, dtype=dtype)
    _require_array("Hamiltonian mask", row["mask"], shape=shape, dtype=np.dtype(np.bool_), finite=False)
    if not np.all(row["mask"]):
        raise ValueError("Hamiltonian teaching block must be a complete active shell grid")
    if row["unit"] != "synthetic-arbitrary-unit":
        raise ValueError("Hamiltonian unit is invalid")


def message_layer(
    node_coefficients: np.ndarray,
    graph: dict[str, Any],
    directions: np.ndarray,
    provenance: dict[str, Any],
) -> dict[int, np.ndarray]:
    validate_message_provenance(graph, provenance, directions)
    if node_coefficients.dtype not in (np.dtype(np.complex64), np.dtype(np.complex128)):
        raise TypeError("node coefficients must be complex64 or complex128")
    _require_array(
        "node_coefficients", node_coefficients, shape=(graph["coordinates"].shape[0], 3), dtype=node_coefficients.dtype
    )
    expected_real = np.dtype(np.float32 if node_coefficients.dtype == np.dtype(np.complex64) else np.float64)
    _require_array("directions", directions, shape=(len(graph["edge_id"]), 3), dtype=expected_real)
    outputs = {
        total_j: np.zeros((graph["coordinates"].shape[0], 2 * total_j + 1), dtype=node_coefficients.dtype)
        for total_j in (0, 1, 2)
    }
    for edge, (receiver, sender) in enumerate(zip(graph["receiver"], graph["sender"])):
        filter_value = coefficient_filter(directions[edge], 1).astype(node_coefficients.dtype)
        coupled = cg_couple(node_coefficients[int(sender)], filter_value, 1, 1)
        for total_j in outputs:
            outputs[total_j][int(receiver)] += coupled[total_j]
    return outputs


def forbidden_external_objects() -> tuple[str, ...]:
    return ("deeph", "e3nn", "pymatgen", "ase", "vasp", "quantum_espresso", "abacus", "formal_training_data", "dft_labels")
