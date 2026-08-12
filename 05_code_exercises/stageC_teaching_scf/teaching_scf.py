"""Deterministic synthetic primitives for the stage C acceptance suite."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from scipy.linalg import eigh
from scipy.special import iv


CONVENTIONS_VERSION = "stageC-v1"
BACKEND = "synthetic"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=json_default,
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def linear_problem() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    jacobian = np.diag([0.2, 0.5, -0.4]).astype(np.float64)
    offset = np.array([0.3, -0.2, 0.1], dtype=np.float64)
    fixed_point = np.linalg.solve(np.eye(3) - jacobian, offset)
    return jacobian, offset, fixed_point


def run_linear_scf(
    alpha: float,
    max_iter: int,
    tolerance: float,
    *,
    initial: np.ndarray | None = None,
    force_all_steps: bool = False,
) -> dict[str, Any]:
    jacobian, offset, fixed_point = linear_problem()
    state = (
        np.zeros(3, dtype=np.float64)
        if initial is None
        else np.asarray(initial, dtype=np.float64).copy()
    )
    require(state.shape == (3,), "linear initial state must have shape (3,)")
    errors: list[float] = []
    residuals: list[float] = []

    for iteration in range(max_iter + 1):
        output = jacobian @ state + offset
        residual = float(np.linalg.norm(output - state))
        error = float(np.linalg.norm(state - fixed_point))
        residuals.append(residual)
        errors.append(error)
        if not force_all_steps and error < tolerance:
            ratios = [
                errors[index + 1] / errors[index]
                for index in range(len(errors) - 1)
                if 1.0e-8 < errors[index] < 1.0e-3
            ]
            return {
                "converged": True,
                "iterations": iteration,
                "termination_reason": "error_tolerance",
                "final_state": state.tolist(),
                "final_error": error,
                "final_residual": residual,
                "errors": errors,
                "residuals": residuals,
                "estimated_rate": (
                    None if not ratios else float(np.median(np.asarray(ratios)))
                ),
            }
        if iteration < max_iter:
            state = state + alpha * (output - state)

    ratios = [
        errors[index + 1] / errors[index]
        for index in range(len(errors) - 1)
        if 1.0e-8 < errors[index] < 1.0e-3
    ]
    return {
        "converged": False,
        "iterations": max_iter,
        "termination_reason": "max_iterations",
        "final_state": state.tolist(),
        "final_error": errors[-1],
        "final_residual": residuals[-1],
        "errors": errors,
        "residuals": residuals,
        "estimated_rate": None if not ratios else float(np.median(ratios)),
    }


def nonlinear_density_map(
    density: np.ndarray,
    *,
    potential: np.ndarray | None = None,
    coupling: float = 4.0,
    beta: float = 1.0,
    electron_count: float = 1.0,
) -> np.ndarray:
    density = np.asarray(density, dtype=np.float64)
    potential = (
        np.array([-0.1, 0.1], dtype=np.float64)
        if potential is None
        else np.asarray(potential, dtype=np.float64)
    )
    require(density.shape == (2,), "density must have shape (2,)")
    require(potential.shape == (2,), "potential must have shape (2,)")
    logits = -beta * (potential + coupling * density)
    weights = np.exp(logits - np.max(logits))
    return electron_count * weights / np.sum(weights)


def teaching_energy(
    density: np.ndarray,
    *,
    potential: np.ndarray | None = None,
    coupling: float = 4.0,
) -> float:
    potential = (
        np.array([-0.1, 0.1], dtype=np.float64)
        if potential is None
        else np.asarray(potential, dtype=np.float64)
    )
    density = np.asarray(density, dtype=np.float64)
    return float(0.5 * coupling * np.dot(density, density) + potential @ density)


def run_nonlinear_scf(
    alpha: float,
    max_iter: int,
    residual_tolerance: float,
    energy_tolerance: float,
    *,
    force_all_steps: bool = False,
) -> dict[str, Any]:
    density = np.array([0.9, 0.1], dtype=np.float64)
    electron_count = 1.0
    trajectory: list[dict[str, Any]] = []
    previous_energy: float | None = None

    for iteration in range(max_iter + 1):
        output = nonlinear_density_map(density)
        residual = float(np.linalg.norm(output - density) / electron_count)
        energy = teaching_energy(density)
        energy_change = (
            None
            if previous_energy is None
            else abs(energy - previous_energy) / (1.0 + abs(energy))
        )
        require(density.shape == (2,), "density shape changed")
        require(np.all(np.isfinite(density)), "density became non-finite")
        require(
            abs(float(np.sum(density)) - electron_count) < 1.0e-12,
            "electron count was not preserved",
        )
        require(np.all(density > -1.0e-14), "density positivity failed")
        trajectory.append(
            {
                "iteration": iteration,
                "density": density.tolist(),
                "output_density": output.tolist(),
                "residual": residual,
                "energy": energy,
                "energy_change": energy_change,
            }
        )
        dual_pass = (
            residual < residual_tolerance
            and energy_change is not None
            and energy_change < energy_tolerance
        )
        if not force_all_steps and dual_pass:
            return {
                "converged": True,
                "iterations": iteration,
                "termination_reason": "dual_tolerance",
                "final_residual": residual,
                "final_energy_change": energy_change,
                "trajectory": trajectory,
            }
        previous_energy = energy
        if iteration < max_iter:
            density = density + alpha * (output - density)

    return {
        "converged": False,
        "iterations": max_iter,
        "termination_reason": "max_iterations",
        "final_residual": trajectory[-1]["residual"],
        "final_energy_change": trajectory[-1]["energy_change"],
        "trajectory": trajectory,
    }


def scf_scan_record(
    alphas: Sequence[float],
    *,
    max_iter: int = 80,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for alpha in alphas:
        result = run_nonlinear_scf(
            float(alpha),
            max_iter=max_iter,
            residual_tolerance=1.0e-9,
            energy_tolerance=1.0e-9,
        )
        records.append(
            {
                "alpha": float(alpha),
                "initial_density": [0.9, 0.1],
                "converged": result["converged"],
                "iterations": result["iterations"],
                "final_residual": result["final_residual"],
                "termination_reason": result["termination_reason"],
                "trajectory_summary": [
                    {
                        "iteration": item["iteration"],
                        "density": item["density"],
                        "residual": item["residual"],
                    }
                    for item in result["trajectory"]
                ],
            }
        )
    return {"max_iter": max_iter, "runs": records}


def canonical_qr(matrix: np.ndarray) -> np.ndarray:
    q_matrix, r_matrix = np.linalg.qr(matrix)
    diagonal = np.diag(r_matrix)
    phases = np.where(np.abs(diagonal) > 0, diagonal / np.abs(diagonal), 1.0)
    q_canonical = q_matrix @ np.diag(phases)
    r_canonical = np.diag(np.conj(phases)) @ r_matrix
    relative_reconstruction = np.linalg.norm(
        q_canonical @ r_canonical - matrix, ord="fro"
    ) / max(np.linalg.norm(matrix, ord="fro"), 1.0e-15)
    require(relative_reconstruction < 1.0e-12, "canonical QR reconstruction failed")
    require(
        np.max(np.abs(np.imag(np.diag(r_canonical)))) < 1.0e-12,
        "canonical R diagonal is not real",
    )
    require(
        np.min(np.real(np.diag(r_canonical))) > -1.0e-14,
        "canonical R diagonal is negative",
    )
    return q_canonical


def normalized_eigenpair_residuals(
    h_matrix: np.ndarray,
    s_matrix: np.ndarray,
    values: np.ndarray,
    vectors: np.ndarray,
) -> np.ndarray:
    h_norm = np.linalg.norm(h_matrix, 2)
    s_norm = np.linalg.norm(s_matrix, 2)
    results = []
    for energy, vector in zip(values, vectors.T):
        numerator = np.linalg.norm(h_matrix @ vector - energy * s_matrix @ vector)
        denominator = (
            (h_norm + abs(energy) * s_norm)
            * np.linalg.norm(vector)
        )
        results.append(numerator / max(denominator, 1.0e-15))
    return np.asarray(results)


def projection_case(seed: int, dimension: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    gaussian = (
        rng.normal(size=(dimension, dimension))
        + 1j * rng.normal(size=(dimension, dimension))
    )
    q_matrix = canonical_qr(gaussian)
    h_matrix = (
        q_matrix
        @ np.diag(np.linspace(-3.0, 3.0, dimension))
        @ q_matrix.conj().T
    )
    target_dimension = max(5, dimension // 3)
    offset = (dimension - target_dimension) // 2
    basis = q_matrix[:, offset : offset + target_dimension]
    projected = basis.conj().T @ h_matrix @ basis
    reconstructed = basis @ projected @ basis.conj().T
    orthogonality = float(
        np.linalg.norm(
            basis.conj().T @ basis - np.eye(target_dimension), ord="fro"
        )
    )
    idempotent = float(
        np.linalg.norm(
            reconstructed
            - basis @ (basis.conj().T @ reconstructed @ basis) @ basis.conj().T,
            ord="fro",
        )
        / max(np.linalg.norm(reconstructed, ord="fro"), 1.0e-15)
    )
    loss = float(
        np.linalg.norm(h_matrix - reconstructed, ord="fro")
        / np.linalg.norm(h_matrix, ord="fro")
    )
    angle = 0.37
    unitary = np.eye(dimension, dtype=np.complex128)
    unitary[:2, :2] = [
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ]
    rotated = unitary.conj().T @ h_matrix @ unitary
    spectrum_difference = float(
        np.max(
            np.abs(
                np.linalg.eigvalsh(rotated) - np.linalg.eigvalsh(h_matrix)
            )
        )
    )
    matrix_difference = float(
        np.linalg.norm(rotated - h_matrix, ord="fro")
        / np.linalg.norm(h_matrix, ord="fro")
    )
    return {
        "dimension": dimension,
        "target_dimension": target_dimension,
        "offset": offset,
        "window": [offset, offset + target_dimension],
        "orthogonality_fro": orthogonality,
        "idempotent_residual": idempotent,
        "relative_lost_norm": loss,
        "rotation_angle": angle,
        "rotation_plane": [0, 1],
        "spectral_difference": spectrum_difference,
        "matrix_difference": matrix_difference,
    }


PathPart = str | int


REQUIRED_PATHS: tuple[tuple[PathPart, ...], ...] = (
    ("schema_version",),
    ("generation_status",),
    ("backend", "name"),
    ("backend", "version"),
    ("backend", "commit"),
    ("artifacts", "inputs", 0, "uri_or_path"),
    ("artifacts", "inputs", 0, "sha256"),
    ("artifacts", "outputs", 0, "uri_or_path"),
    ("artifacts", "outputs", 0, "sha256"),
    ("structure", "id"),
    ("structure", "sha256"),
    ("structure", "lattice"),
    ("structure", "species"),
    ("structure", "positions"),
    ("structure", "boundary_conditions"),
    ("theory", "electronic_structure_level"),
    ("theory", "xc"),
    ("theory", "all_electron_or_pseudopotential"),
    ("theory", "potential_dataset", "id"),
    ("theory", "potential_dataset", "sha256"),
    ("theory", "relativistic_treatment"),
    ("basis", "type"),
    ("basis", "definition"),
    ("basis", "cutoff_or_grid"),
    ("basis", "id"),
    ("basis", "sha256"),
    ("spin", "polarization"),
    ("spin", "noncollinear"),
    ("spin", "soc"),
    ("sampling", "kind"),
    ("sampling", "k_mesh"),
    ("sampling", "k_shift"),
    ("sampling", "k_weights"),
    ("occupation", "electron_count"),
    ("occupation", "smearing_method"),
    ("occupation", "temperature"),
    ("occupation", "reported_energy_functional"),
    ("convergence", "scf_residual_definition"),
    ("convergence", "scf_residual_tolerance"),
    ("convergence", "energy_tolerance"),
    ("convergence", "eigensolver_tolerance"),
    ("convergence", "max_iterations"),
    ("convergence", "achieved_metrics"),
    ("representation", "output_object"),
    ("representation", "units"),
    ("representation", "orbital_ordering"),
    ("representation", "atom_orbital_index_map"),
    ("representation", "lattice_displacement_direction"),
    ("representation", "bra_ket_order"),
    ("representation", "fourier_forward"),
    ("representation", "fourier_inverse"),
    ("representation", "phase_or_gauge"),
    ("representation", "overlap_treatment"),
    ("projection", "method"),
    ("projection", "window"),
    ("projection", "source_dimension"),
    ("projection", "target_dimension"),
    ("projection", "loss_metric"),
    ("projection", "loss_value"),
    ("projection", "band_validation"),
    ("projection", "matrix_validation"),
    ("validation", "commands"),
    ("validation", "environment", "python"),
    ("validation", "environment", "numpy"),
    ("validation", "environment", "scipy"),
    ("validation", "seed"),
    ("validation", "audit_status"),
)


def display_path(path: Sequence[PathPart]) -> str:
    result = ""
    for part in path:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += ("." if result else "") + part
    return result


def _get_path(record: Any, path: Sequence[PathPart]) -> Any:
    current = record
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or len(current) <= part:
                raise ValueError(f"missing required path: {display_path(path)}")
            current = current[part]
        else:
            if not isinstance(current, dict) or part not in current:
                raise ValueError(f"missing required path: {display_path(path)}")
            current = current[part]
    return current


def _delete_path(record: Any, path: Sequence[PathPart]) -> None:
    parent = _get_path(record, path[:-1])
    final = path[-1]
    if isinstance(final, int):
        del parent[final]
    else:
        del parent[final]


def _set_path(record: Any, path: Sequence[PathPart], value: Any) -> None:
    parent = _get_path(record, path[:-1])
    final = path[-1]
    if isinstance(final, int):
        parent[final] = value
    else:
        parent[final] = value


def synthetic_label_record(seed: int) -> dict[str, Any]:
    unresolved = "UNRESOLVED_M8"
    input_content = f"synthetic-stageC-input-{seed}".encode()
    output_content = f"synthetic-stageC-output-{seed}".encode()
    structure_content = f"synthetic-structure-{seed}".encode()
    basis_content = b"synthetic-basis-stageC-v1"
    return {
        "schema_version": "stageC-label-v1",
        "generation_status": "SYNTHETIC_M5",
        "backend": {
            "name": unresolved,
            "version": unresolved,
            "commit": unresolved,
        },
        "artifacts": {
            "inputs": [{
                "uri_or_path": "synthetic/input.json",
                "sha256": hashlib.sha256(input_content).hexdigest(),
            }],
            "outputs": [{
                "uri_or_path": "synthetic/output.npz",
                "sha256": hashlib.sha256(output_content).hexdigest(),
            }],
        },
        "structure": {
            "id": "SYNTHETIC",
            "sha256": hashlib.sha256(structure_content).hexdigest(),
            "lattice": np.eye(3).tolist(),
            "species": ["X", "Y"],
            "positions": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
            "boundary_conditions": ["periodic", "periodic", "periodic"],
        },
        "theory": {
            "electronic_structure_level": unresolved,
            "xc": unresolved,
            "all_electron_or_pseudopotential": unresolved,
            "potential_dataset": {"id": unresolved, "sha256": unresolved},
            "relativistic_treatment": unresolved,
        },
        "basis": {
            "type": "SYNTHETIC",
            "definition": "two abstract orbitals",
            "cutoff_or_grid": {"kind": "synthetic", "value": 2},
            "id": "synthetic-basis-stageC-v1",
            "sha256": hashlib.sha256(basis_content).hexdigest(),
        },
        "spin": {
            "polarization": unresolved,
            "noncollinear": unresolved,
            "soc": unresolved,
        },
        "sampling": {
            "kind": "synthetic_equal_weight",
            "k_mesh": [1, 1, 1],
            "k_shift": [0.0, 0.0, 0.0],
            "k_weights": [1.0],
        },
        "occupation": {
            "electron_count": 1.0,
            "smearing_method": unresolved,
            "temperature": unresolved,
            "reported_energy_functional": "teaching_energy",
        },
        "convergence": {
            "scf_residual_definition": "l2_over_electron_count",
            "scf_residual_tolerance": 1.0e-9,
            "energy_tolerance": 1.0e-9,
            "eigensolver_tolerance": 1.0e-12,
            "max_iterations": 80,
            "achieved_metrics": {"scf_residual": 8.0e-10},
        },
        "representation": {
            "output_object": ["H", "S"],
            "units": "atomic_units",
            "orbital_ordering": ["X:s", "Y:s"],
            "atom_orbital_index_map": {"0": [0], "1": [1]},
            "lattice_displacement_direction": "ket_cell_minus_bra_cell",
            "bra_ket_order": "row_is_bra_column_is_ket",
            "fourier_forward": "sum_R A_R exp(+ikR)",
            "fourier_inverse": "mean_k A_k exp(-ikR)",
            "phase_or_gauge": "cell_phase",
            "overlap_treatment": "explicit_generalized_eigenproblem",
        },
        "projection": {
            "method": "synthetic_orthogonal_subspace",
            "window": [-1.0, 1.0],
            "source_dimension": 12,
            "target_dimension": 5,
            "loss_metric": "relative_frobenius",
            "loss_value": 0.95,
            "band_validation": {"status": "synthetic_pass"},
            "matrix_validation": {"status": "synthetic_pass"},
        },
        "validation": {
            "commands": ["python run_experiments.py --format json"],
            "environment": {
                "python": "3.12.13",
                "numpy": "2.3.5",
                "scipy": "1.18.0",
            },
            "seed": seed,
            "audit_status": "PENDING_M5_INDEPENDENT_AUDIT",
        },
    }


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(
        value, (bool, np.bool_)
    )


def _all_numeric_leaves(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0 and all(_all_numeric_leaves(item) for item in value)
    return _is_number(value)


def _require_path(
    record: dict[str, Any],
    path: Sequence[PathPart],
    predicate: Callable[[Any], bool],
    description: str,
) -> Any:
    value = _get_path(record, path)
    require(predicate(value), f"{description}: {display_path(path)}")
    return value


def _require_numeric_array(
    record: dict[str, Any],
    path: Sequence[PathPart],
    shape: tuple[int | None, ...],
) -> np.ndarray:
    value = _get_path(record, path)
    require(isinstance(value, list), f"expected array: {display_path(path)}")
    require(_all_numeric_leaves(value), f"non-numeric array: {display_path(path)}")
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError):
        raise AssertionError(f"non-numeric array: {display_path(path)}") from None
    require(array.ndim == len(shape), f"wrong array rank: {display_path(path)}")
    require(
        all(expected is None or actual == expected for actual, expected in zip(array.shape, shape)),
        f"wrong array shape: {display_path(path)}",
    )
    require(bool(np.all(np.isfinite(array))), f"non-finite array: {display_path(path)}")
    return array


M8_UNRESOLVED_PATHS: tuple[tuple[PathPart, ...], ...] = (
    ("backend", "name"),
    ("backend", "version"),
    ("backend", "commit"),
    ("theory", "electronic_structure_level"),
    ("theory", "xc"),
    ("theory", "all_electron_or_pseudopotential"),
    ("theory", "potential_dataset", "id"),
    ("theory", "potential_dataset", "sha256"),
    ("theory", "relativistic_treatment"),
    ("spin", "polarization"),
    ("spin", "noncollinear"),
    ("spin", "soc"),
    ("occupation", "smearing_method"),
    ("occupation", "temperature"),
)


SYNTHETIC_LOCKED_VALUES: tuple[tuple[tuple[PathPart, ...], Any], ...] = (
    (("structure", "id"), "SYNTHETIC"),
    (("structure", "species"), ["X", "Y"]),
    (("basis", "type"), "SYNTHETIC"),
    (("basis", "definition"), "two abstract orbitals"),
    (("basis", "id"), "synthetic-basis-stageC-v1"),
    (("sampling", "kind"), "synthetic_equal_weight"),
    (("projection", "method"), "synthetic_orthogonal_subspace"),
)


def validate_label_record(record: dict[str, Any]) -> None:
    require(isinstance(record, dict), "record must be a mapping: <root>")
    for path in REQUIRED_PATHS:
        _get_path(record, path)
    require(record["schema_version"] == "stageC-label-v1", "wrong schema version")
    require(record["generation_status"] == "SYNTHETIC_M5", "wrong generation status")

    nonempty_string_paths = (
        ("schema_version",),
        ("generation_status",),
        ("artifacts", "inputs", 0, "uri_or_path"),
        ("artifacts", "outputs", 0, "uri_or_path"),
        ("structure", "id"),
        ("basis", "type"),
        ("basis", "definition"),
        ("basis", "id"),
        ("sampling", "kind"),
        ("occupation", "reported_energy_functional"),
        ("convergence", "scf_residual_definition"),
        ("representation", "units"),
        ("representation", "lattice_displacement_direction"),
        ("representation", "bra_ket_order"),
        ("representation", "fourier_forward"),
        ("representation", "fourier_inverse"),
        ("representation", "phase_or_gauge"),
        ("representation", "overlap_treatment"),
        ("projection", "method"),
        ("projection", "loss_metric"),
        ("validation", "environment", "python"),
        ("validation", "environment", "numpy"),
        ("validation", "environment", "scipy"),
        ("validation", "audit_status"),
    )
    for path in nonempty_string_paths:
        _require_path(
            record,
            path,
            lambda value: isinstance(value, str) and bool(value),
            "expected nonempty string",
        )

    require(isinstance(record["artifacts"], dict), "expected mapping: artifacts")
    for group in ("inputs", "outputs"):
        artifacts = record["artifacts"][group]
        require(
            isinstance(artifacts, list) and len(artifacts) == 1,
            f"expected one-element array: artifacts.{group}",
        )
        require(isinstance(artifacts[0], dict), f"expected mapping: artifacts.{group}[0]")
        require(
            artifacts[0]["uri_or_path"].startswith("synthetic/"),
            f"non-synthetic artifact path: artifacts.{group}[0].uri_or_path",
        )

    lattice = _require_numeric_array(record, ("structure", "lattice"), (3, 3))
    require(abs(float(np.linalg.det(lattice))) > 1.0e-12, "singular lattice: structure.lattice")
    positions = _require_numeric_array(record, ("structure", "positions"), (None, 3))
    species = _require_path(
        record,
        ("structure", "species"),
        lambda value: isinstance(value, list)
        and len(value) > 0
        and all(isinstance(item, str) and bool(item) for item in value),
        "expected nonempty string array",
    )
    require(
        len(species) == positions.shape[0],
        "species and positions length differ: structure.species",
    )
    boundary = _require_path(
        record,
        ("structure", "boundary_conditions"),
        lambda value: isinstance(value, list)
        and len(value) == 3
        and all(isinstance(item, str) for item in value),
        "expected three-string array",
    )
    require(
        boundary == ["periodic", "periodic", "periodic"],
        "non-synthetic boundary choice: structure.boundary_conditions",
    )

    cutoff = _get_path(record, ("basis", "cutoff_or_grid"))
    require(isinstance(cutoff, dict), "expected mapping: basis.cutoff_or_grid")
    require(
        cutoff == {"kind": "synthetic", "value": 2},
        "non-synthetic basis choice: basis.cutoff_or_grid",
    )

    k_mesh = _require_path(
        record,
        ("sampling", "k_mesh"),
        lambda value: isinstance(value, list)
        and len(value) == 3
        and all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in value),
        "expected three positive integers",
    )
    k_shift = _require_numeric_array(record, ("sampling", "k_shift"), (3,))
    k_weights = _require_numeric_array(record, ("sampling", "k_weights"), (None,))
    require(k_mesh == [1, 1, 1], "non-synthetic sampling choice: sampling.k_mesh")
    require(
        bool(np.allclose(k_shift, np.zeros(3), atol=0.0, rtol=0.0)),
        "non-synthetic sampling choice: sampling.k_shift",
    )
    require(
        k_weights.shape == (1,) and abs(float(k_weights[0]) - 1.0) < 1.0e-12,
        "non-synthetic sampling choice: sampling.k_weights",
    )

    for path in (("occupation", "electron_count"),
                 ("convergence", "scf_residual_tolerance"),
                 ("convergence", "energy_tolerance"),
                 ("convergence", "eigensolver_tolerance"),
                 ("projection", "loss_value")):
        value = _require_path(record, path, _is_number, "expected numeric scalar")
        require(bool(np.isfinite(value)), f"non-finite scalar: {display_path(path)}")
    require(record["occupation"]["electron_count"] > 0.0, "nonpositive scalar: occupation.electron_count")
    for name in ("scf_residual_tolerance", "energy_tolerance", "eigensolver_tolerance"):
        require(record["convergence"][name] > 0.0, f"nonpositive scalar: convergence.{name}")
    max_iterations = _get_path(record, ("convergence", "max_iterations"))
    require(
        isinstance(max_iterations, int) and not isinstance(max_iterations, bool) and max_iterations > 0,
        "expected positive integer: convergence.max_iterations",
    )
    achieved = _get_path(record, ("convergence", "achieved_metrics"))
    require(isinstance(achieved, dict) and bool(achieved), "expected mapping: convergence.achieved_metrics")
    require("scf_residual" in achieved, "missing scalar: convergence.achieved_metrics.scf_residual")
    for name, value in achieved.items():
        require(_is_number(value), f"expected numeric scalar: convergence.achieved_metrics.{name}")
        require(bool(np.isfinite(value)), f"non-finite scalar: convergence.achieved_metrics.{name}")

    output_object = _get_path(record, ("representation", "output_object"))
    require(output_object == ["H", "S"], "wrong array value: representation.output_object")
    orbital_ordering = _get_path(record, ("representation", "orbital_ordering"))
    require(
        isinstance(orbital_ordering, list)
        and len(orbital_ordering) == 2
        and len(orbital_ordering) == len(set(orbital_ordering))
        and all(isinstance(item, str) and bool(item) for item in orbital_ordering),
        "invalid string array: representation.orbital_ordering",
    )
    index_map = _get_path(record, ("representation", "atom_orbital_index_map"))
    require(isinstance(index_map, dict) and bool(index_map), "expected mapping: representation.atom_orbital_index_map")
    flattened_indices: list[int] = []
    for atom, indices in index_map.items():
        require(isinstance(atom, str) and bool(atom), "invalid key: representation.atom_orbital_index_map")
        require(
            isinstance(indices, list)
            and all(isinstance(index, int) and not isinstance(index, bool) and index >= 0 for index in indices),
            f"invalid integer array: representation.atom_orbital_index_map.{atom}",
        )
        flattened_indices.extend(indices)
    require(
        sorted(flattened_indices) == list(range(len(orbital_ordering))),
        "orbital index coverage mismatch: representation.atom_orbital_index_map",
    )

    projection_window = _require_numeric_array(record, ("projection", "window"), (2,))
    require(projection_window[0] < projection_window[1], "unordered array: projection.window")
    source_dimension = _get_path(record, ("projection", "source_dimension"))
    target_dimension = _get_path(record, ("projection", "target_dimension"))
    for name, value in (("source_dimension", source_dimension), ("target_dimension", target_dimension)):
        require(
            isinstance(value, int) and not isinstance(value, bool) and value > 0,
            f"expected positive integer: projection.{name}",
        )
    require(target_dimension <= source_dimension, "dimension order invalid: projection.target_dimension")
    require(0.0 <= record["projection"]["loss_value"] <= 1.0, "loss range invalid: projection.loss_value")
    for name in ("band_validation", "matrix_validation"):
        value = record["projection"][name]
        require(
            isinstance(value, dict) and value == {"status": "synthetic_pass"},
            f"non-synthetic mapping: projection.{name}",
        )

    commands = _get_path(record, ("validation", "commands"))
    require(
        isinstance(commands, list)
        and len(commands) > 0
        and all(isinstance(command, str) and bool(command) for command in commands),
        "invalid command array: validation.commands",
    )
    seed = _get_path(record, ("validation", "seed"))
    require(isinstance(seed, int) and not isinstance(seed, bool), "expected integer: validation.seed")

    for path in (
        ("artifacts", "inputs", 0, "sha256"),
        ("artifacts", "outputs", 0, "sha256"),
        ("structure", "sha256"),
        ("basis", "sha256"),
    ):
        require(_is_sha256(_get_path(record, path)), f"invalid SHA-256: {display_path(path)}")
    expected_hashes = (
        (("artifacts", "inputs", 0, "sha256"), hashlib.sha256(f"synthetic-stageC-input-{seed}".encode()).hexdigest()),
        (("artifacts", "outputs", 0, "sha256"), hashlib.sha256(f"synthetic-stageC-output-{seed}".encode()).hexdigest()),
        (("structure", "sha256"), hashlib.sha256(f"synthetic-structure-{seed}".encode()).hexdigest()),
        (("basis", "sha256"), hashlib.sha256(b"synthetic-basis-stageC-v1").hexdigest()),
    )
    for path, expected_hash in expected_hashes:
        require(
            _get_path(record, path) == expected_hash,
            f"content hash mismatch: {display_path(path)}",
        )
    for path in M8_UNRESOLVED_PATHS:
        require(
            _get_path(record, path) == "UNRESOLVED_M8",
            f"M8 choice was resolved early: {display_path(path)}",
        )
    for path, expected in SYNTHETIC_LOCKED_VALUES:
        require(
            _get_path(record, path) == expected,
            f"M8 choice was resolved early: {display_path(path)}",
        )

    exact_values = (
        (("occupation", "reported_energy_functional"), "teaching_energy"),
        (("convergence", "scf_residual_definition"), "l2_over_electron_count"),
        (("representation", "units"), "atomic_units"),
        (("representation", "lattice_displacement_direction"), "ket_cell_minus_bra_cell"),
        (("representation", "bra_ket_order"), "row_is_bra_column_is_ket"),
        (("representation", "fourier_forward"), "sum_R A_R exp(+ikR)"),
        (("representation", "fourier_inverse"), "mean_k A_k exp(-ikR)"),
        (("representation", "phase_or_gauge"), "cell_phase"),
        (("representation", "overlap_treatment"), "explicit_generalized_eigenproblem"),
        (("projection", "loss_metric"), "relative_frobenius"),
        (("validation", "environment", "python"), "3.12.13"),
        (("validation", "environment", "numpy"), "2.3.5"),
        (("validation", "environment", "scipy"), "1.18.0"),
        (("validation", "audit_status"), "PENDING_M5_INDEPENDENT_AUDIT"),
    )
    for path, expected in exact_values:
        require(_get_path(record, path) == expected, f"wrong frozen value: {display_path(path)}")


SCHEMA_NEGATIVE_MUTATIONS: tuple[tuple[str, tuple[PathPart, ...], Any], ...] = (
    ("type", ("convergence", "max_iterations"), "eighty"),
    ("type", ("occupation", "electron_count"), "one"),
    ("type", ("validation", "seed"), 1.5),
    ("type", ("structure", "lattice"), [["x"] * 3 for _ in range(3)]),
    ("type", ("representation", "output_object"), "H,S"),
    ("type", ("convergence", "achieved_metrics"), []),
    ("type", ("basis", "cutoff_or_grid"), []),
    ("type", ("representation", "atom_orbital_index_map"), []),
    ("type", ("projection", "band_validation"), []),
    ("shape", ("structure", "lattice"), [[1.0, 0.0], [0.0, 1.0]]),
    ("shape", ("structure", "positions"), [[0.0, 0.0]]),
    ("shape", ("structure", "species"), ["X"]),
    ("shape", ("structure", "boundary_conditions"), ["periodic"]),
    ("shape", ("sampling", "k_mesh"), [1, 1]),
    ("shape", ("sampling", "k_shift"), [0.0, 0.0]),
    ("shape", ("sampling", "k_weights"), [0.5, 0.5]),
    ("shape", ("representation", "output_object"), ["H"]),
    ("shape", ("representation", "orbital_ordering"), ["X:s"]),
    ("shape", ("projection", "window"), [-1.0]),
    ("shape", ("validation", "commands"), []),
    ("hash", ("artifacts", "inputs", 0, "sha256"), "bad"),
    ("hash", ("artifacts", "outputs", 0, "sha256"), "bad"),
    ("hash", ("structure", "sha256"), "bad"),
    ("hash", ("basis", "sha256"), "bad"),
    ("hash", ("artifacts", "inputs", 0, "sha256"), "0" * 64),
    ("hash", ("artifacts", "outputs", 0, "sha256"), "0" * 64),
    ("hash", ("structure", "sha256"), "0" * 64),
    ("hash", ("basis", "sha256"), "0" * 64),
    *(("m8_choice", path, "FORBIDDEN_REAL_CHOICE") for path in M8_UNRESOLVED_PATHS),
    ("m8_choice", ("structure", "id"), "silicon"),
    ("m8_choice", ("structure", "species"), ["Si", "O"]),
    ("m8_choice", ("basis", "type"), "plane_wave"),
    ("m8_choice", ("sampling", "kind"), "monkhorst_pack"),
    ("m8_choice", ("projection", "method"), "HPRO"),
)


def mutated_label_record(
    record: dict[str, Any], path: Sequence[PathPart], value: Any
) -> dict[str, Any]:
    sample = copy.deepcopy(record)
    _set_path(sample, path, copy.deepcopy(value))
    return sample


def schema_failure_witnesses(record: dict[str, Any]) -> list[dict[str, str]]:
    witnesses: list[dict[str, str]] = []
    for category, path, value in SCHEMA_NEGATIVE_MUTATIONS:
        path_name = display_path(path)
        sample = mutated_label_record(record, path, value)
        try:
            validate_label_record(sample)
        except (AssertionError, ValueError) as error:
            require(path_name in str(error), f"schema failure not localized: {path_name}")
            witnesses.append({"category": category, "path": path_name, "error": str(error)})
        else:
            raise AssertionError(f"schema mutation was accepted: {path_name}")
    return witnesses


def missing_path_failures(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for path in REQUIRED_PATHS:
        sample = copy.deepcopy(record)
        _delete_path(sample, path)
        path_name = display_path(path)
        try:
            validate_label_record(sample)
        except ValueError as error:
            require(path_name in str(error), f"missing path not named: {path_name}")
            failures.append(path_name)
        else:
            raise AssertionError(f"missing path was accepted: {path_name}")
    return failures


def generalized_overlap_case() -> dict[str, Any]:
    s_matrix = np.diag([1.0, 2.0, 1.5, 2.3])
    h_matrix = np.diag([-1.2, -0.2, 1.2, 4.6])
    reference = np.array([-1.2, -0.1, 0.8, 2.0])
    transform = np.diag([1.2, 0.9, 1.1, 0.8]).astype(np.complex128)
    transform[0, 1] = 0.2 + 0.1j
    transform[1, 2] = -0.15j
    transform[2, 3] = 0.1
    transformed_h = transform.conj().T @ h_matrix @ transform
    transformed_s = transform.conj().T @ s_matrix @ transform
    values, vectors = eigh(transformed_h, transformed_s)
    residuals = normalized_eigenpair_residuals(
        transformed_h, transformed_s, values, vectors
    )
    wrong_values = np.linalg.eigvalsh(transformed_h)
    return {
        "reference_spectrum": reference.tolist(),
        "spectrum": values.tolist(),
        "spectrum_max_difference": float(np.max(np.abs(values - reference))),
        "maximum_normalized_residual": float(np.max(residuals)),
        "minimum_overlap_eigenvalue": float(
            np.min(np.linalg.eigvalsh(transformed_s))
        ),
        "wrong_ordinary_spectrum": wrong_values.tolist(),
        "overlap_ignored_max_difference": float(
            np.max(np.abs(wrong_values - reference))
        ),
    }


def convergence_sequences() -> dict[str, Any]:
    resolution = [8, 16, 32, 64, 128]
    positive = np.array([1.12, 1.03, 1.008, 1.002, 1.0005])
    negative = np.array([1.12, 1.03, 1.0020, 1.0015, 1.0080])
    return {
        "resolution": resolution,
        "positive": positive.tolist(),
        "positive_reference_errors": np.abs(positive - 1.0).tolist(),
        "positive_adjacent_differences": np.abs(np.diff(positive)).tolist(),
        "negative": negative.tolist(),
        "negative_reference_errors": np.abs(negative - 1.0).tolist(),
        "negative_adjacent_differences": np.abs(np.diff(negative)).tolist(),
    }


def sampling_case() -> dict[str, Any]:
    sizes = [4, 8, 16, 32, 64]
    reference = float(iv(0, 1))
    values = []
    for size in sizes:
        k_points = 2.0 * np.pi * np.arange(size) / size
        values.append(float(np.mean(np.exp(np.cos(k_points)))))
    values_array = np.asarray(values)
    biased = values_array + 1.0e-2
    return {
        "sizes": sizes,
        "reference": reference,
        "values": values,
        "sampling_errors": np.abs(values_array - reference).tolist(),
        "basis_bias": 1.0e-2,
        "biased_total_errors": np.abs(biased - reference).tolist(),
        "last_sampling_difference": float(abs(values_array[-1] - values_array[-2])),
    }


def locality_case(grid_size: int) -> dict[str, Any]:
    require(grid_size >= 48, "grid_size must be at least 48")
    index = np.arange(grid_size)
    distance = np.abs(index[:, None] - index[None, :])
    matrices = {
        "exponential": np.exp(-distance / 2.0),
        "algebraic": 1.0 / (1.0 + distance),
    }
    records: dict[str, list[dict[str, float | int]]] = {}
    for name, matrix in matrices.items():
        action = matrix @ np.ones(grid_size) / grid_size
        records[name] = []
        for cutoff in [2, 4, 8, 16]:
            truncated = matrix * (distance <= cutoff)
            truncated_action = truncated @ np.ones(grid_size) / grid_size
            records[name].append(
                {
                    "cutoff": cutoff,
                    "nonzero_fraction": float(
                        np.count_nonzero(truncated) / truncated.size
                    ),
                    "relative_frobenius_error": float(
                        np.linalg.norm(matrix - truncated, ord="fro")
                        / np.linalg.norm(matrix, ord="fro")
                    ),
                    "relative_action_error": float(
                        np.linalg.norm(action - truncated_action)
                        / np.linalg.norm(action)
                    ),
                }
            )
    fit_distance = np.arange(4, 13)
    exponential_mean = np.array([
        np.mean(matrices["exponential"][distance == value])
        for value in fit_distance
    ])
    slope = float(np.polyfit(fit_distance, np.log(exponential_mean), 1)[0])
    short_distance = np.arange(1, 9)
    short_mean = np.array([
        np.mean(matrices["algebraic"][distance == value])
        for value in short_distance
    ])
    fit = np.polyfit(short_distance, np.log(short_mean), 1)
    far_distance = np.arange(16, 32)
    far_true = np.array([
        np.mean(matrices["algebraic"][distance == value])
        for value in far_distance
    ])
    far_prediction = np.exp(np.polyval(fit, far_distance))
    extrapolation_error = float(
        np.linalg.norm(far_prediction - far_true) / np.linalg.norm(far_true)
    )
    return {
        "grid_size": grid_size,
        "cutoffs": [2, 4, 8, 16],
        "records": records,
        "exponential_fit_range": [4, 12],
        "exponential_fit_slope": slope,
        "algebraic_fit_range": [1, 8],
        "algebraic_extrapolation_range": [16, 31],
        "algebraic_extrapolation_relative_error": extrapolation_error,
    }
