"""Chapter 1 generalized Hermitian eigenproblem experiment.

This module uses synthetic matrices only. It does not install DeepH, read
training data, or make claims about a particular material.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray
from scipy import __version__ as scipy_version
from scipy.linalg import eigh


ComplexMatrix = NDArray[np.complex128]


def _complex_random_matrix(rng: np.random.Generator, n: int) -> ComplexMatrix:
    return rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))


def _unitary_matrix(rng: np.random.Generator, n: int) -> ComplexMatrix:
    q, r = np.linalg.qr(_complex_random_matrix(rng, n))
    phases = np.diag(r)
    phases = np.where(np.abs(phases) > 0.0, phases / np.abs(phases), 1.0)
    return np.asarray(q * phases.conj(), dtype=np.complex128)


def validate_problem(
    hamiltonian: ComplexMatrix,
    overlap: ComplexMatrix,
    *,
    hermitian_tolerance: float = 1.0e-11,
) -> None:
    """Validate shape, Hermiticity, finiteness, and positive definiteness."""

    hamiltonian = np.asarray(hamiltonian)
    overlap = np.asarray(overlap)
    if hamiltonian.ndim != 2 or hamiltonian.shape[0] != hamiltonian.shape[1]:
        raise ValueError("hamiltonian must be a square matrix")
    if overlap.shape != hamiltonian.shape:
        raise ValueError("overlap must have the same square shape as hamiltonian")
    if not np.isfinite(hamiltonian).all() or not np.isfinite(overlap).all():
        raise ValueError("matrices must contain only finite values")
    if not np.allclose(
        hamiltonian,
        hamiltonian.conj().T,
        atol=hermitian_tolerance,
        rtol=0.0,
    ):
        raise ValueError("hamiltonian must be Hermitian")
    if not np.allclose(
        overlap,
        overlap.conj().T,
        atol=hermitian_tolerance,
        rtol=0.0,
    ):
        raise ValueError("overlap must be Hermitian")
    minimum_overlap_eigenvalue = float(np.linalg.eigvalsh(overlap).min())
    if minimum_overlap_eigenvalue <= 0.0:
        raise ValueError(
            "overlap must be positive definite; "
            f"minimum eigenvalue is {minimum_overlap_eigenvalue:.6e}"
        )


def solve_generalized(
    hamiltonian: ComplexMatrix, overlap: ComplexMatrix
) -> tuple[NDArray[np.float64], ComplexMatrix]:
    """Solve H C = S C diag(E), returning S-orthonormal eigenvectors."""

    validate_problem(hamiltonian, overlap)
    eigenvalues, eigenvectors = eigh(hamiltonian, overlap, check_finite=True)
    return np.asarray(eigenvalues), np.asarray(eigenvectors)


def two_orbital_closed_form_eigenvalues(
    *,
    epsilon_1: float,
    epsilon_2: float,
    hopping: complex,
    overlap_value: complex,
) -> NDArray[np.float64]:
    """Return the closed generalized eigenvalues of the 2x2 model."""

    if abs(overlap_value) >= 1.0:
        raise ValueError("two-orbital overlap requires abs(overlap_value) < 1")
    a = 1.0 - abs(overlap_value) ** 2
    b = (
        float(epsilon_1)
        + float(epsilon_2)
        - 2.0 * np.real(hopping * np.conj(overlap_value))
    )
    d = float(epsilon_1) * float(epsilon_2) - abs(hopping) ** 2
    discriminant = float(b * b - 4.0 * a * d)
    tolerance = 64.0 * np.finfo(float).eps * max(
        b * b, abs(4.0 * a * d), 1.0
    )
    if discriminant < -tolerance:
        raise ValueError("two-orbital discriminant is unexpectedly negative")
    root = np.sqrt(max(discriminant, 0.0))
    return np.sort(
        np.asarray(
            ((b - root) / (2.0 * a), (b + root) / (2.0 * a)),
            dtype=np.float64,
        )
    )


def solver_diagnostics(
    hamiltonian: ComplexMatrix,
    overlap: ComplexMatrix,
    eigenvalues: NDArray[np.float64],
    eigenvectors: ComplexMatrix,
) -> dict[str, float]:
    """Return normalized residual, S-orthogonality, and overlap conditioning."""

    residual = hamiltonian @ eigenvectors - (
        overlap @ eigenvectors
    ) * eigenvalues[np.newaxis, :]
    h_norm = float(np.linalg.norm(hamiltonian, ord=2))
    s_norm = float(np.linalg.norm(overlap, ord=2))
    c_norms = np.linalg.norm(eigenvectors, axis=0)
    scales = (h_norm + np.abs(eigenvalues) * s_norm) * c_norms
    normalized = np.linalg.norm(residual, axis=0) / np.maximum(scales, 1.0)
    orthogonality = eigenvectors.conj().T @ overlap @ eigenvectors
    overlap_eigenvalues = np.linalg.eigvalsh(overlap)
    return {
        "maximum_normalized_residual": float(normalized.max()),
        "s_orthogonality_frobenius": float(
            np.linalg.norm(orthogonality - np.eye(len(eigenvalues)), ord="fro")
        ),
        "overlap_minimum_eigenvalue": float(overlap_eigenvalues.min()),
        "overlap_condition_number": float(np.linalg.cond(overlap, p=2)),
    }


def make_problem(
    *,
    size: int = 6,
    seed: int = 20260803,
    overlap_condition: float = 10.0,
) -> tuple[ComplexMatrix, ComplexMatrix]:
    """Create a deterministic complex Hermitian H and SPD S."""

    if size < 2:
        raise ValueError("size must be at least 2")
    if overlap_condition < 1.0:
        raise ValueError("overlap_condition must be at least 1")
    rng = np.random.default_rng(seed)
    raw_h = _complex_random_matrix(rng, size)
    hamiltonian = (raw_h + raw_h.conj().T) / 2.0
    hamiltonian /= np.linalg.norm(hamiltonian, ord=2)
    q = _unitary_matrix(rng, size)
    overlap_eigenvalues = np.geomspace(1.0, overlap_condition, size)
    overlap = q @ np.diag(overlap_eigenvalues) @ q.conj().T
    overlap = (overlap + overlap.conj().T) / 2.0
    return np.asarray(hamiltonian), np.asarray(overlap)


def make_basis_transform(
    *,
    size: int,
    seed: int = 20260804,
    condition: float = 3.0,
) -> ComplexMatrix:
    """Create a deterministic invertible, generally non-unitary basis transform."""

    if condition < 1.0:
        raise ValueError("condition must be at least 1")
    rng = np.random.default_rng(seed)
    left = _unitary_matrix(rng, size)
    right = _unitary_matrix(rng, size)
    singular_values = np.geomspace(1.0, condition, size)
    return np.asarray(
        left @ np.diag(singular_values) @ right.conj().T,
        dtype=np.complex128,
    )


def transform_basis(
    hamiltonian: ComplexMatrix,
    overlap: ComplexMatrix,
    transform: ComplexMatrix,
) -> tuple[ComplexMatrix, ComplexMatrix]:
    """Apply H' = A^dagger H A and S' = A^dagger S A."""

    if transform.shape != hamiltonian.shape:
        raise ValueError("transform must have the same shape as the matrices")
    if abs(np.linalg.det(transform)) <= np.finfo(float).eps:
        raise ValueError("transform must be invertible")
    return (
        transform.conj().T @ hamiltonian @ transform,
        transform.conj().T @ overlap @ transform,
    )


def equal_norm_eigenprojector_perturbations(
    overlap: ComplexMatrix,
    eigenvectors: ComplexMatrix,
    *,
    target_index: int,
    orthogonal_index: int,
    frobenius_norm: float,
) -> tuple[ComplexMatrix, ComplexMatrix]:
    """Construct equal-norm perturbations in two S-orthogonal eigendirections."""

    if target_index == orthogonal_index:
        raise ValueError("target and orthogonal indices must differ")
    if frobenius_norm <= 0.0:
        raise ValueError("frobenius_norm must be positive")
    perturbations: list[ComplexMatrix] = []
    for index in (target_index, orthogonal_index):
        vector = eigenvectors[:, index]
        projector = overlap @ np.outer(vector, vector.conj()) @ overlap
        projector = (projector + projector.conj().T) / 2.0
        perturbations.append(
            np.asarray(
                frobenius_norm * projector / np.linalg.norm(projector, ord="fro")
            )
        )
    return perturbations[0], perturbations[1]


def first_order_remainders(
    hamiltonian: ComplexMatrix,
    overlap: ComplexMatrix,
    delta_hamiltonian: ComplexMatrix,
    delta_overlap: ComplexMatrix,
    *,
    eigenvalue_index: int,
    steps: Iterable[float],
) -> dict[str, Any]:
    """Check the local first-order formula for a simple generalized eigenvalue."""

    eigenvalues, eigenvectors = solve_generalized(hamiltonian, overlap)
    if not 0 <= eigenvalue_index < len(eigenvalues):
        raise ValueError("eigenvalue_index is out of range")
    gaps = np.abs(eigenvalues - eigenvalues[eigenvalue_index])
    nonzero_gaps = gaps[gaps > 0.0]
    if len(nonzero_gaps) == 0 or float(nonzero_gaps.min()) < 1.0e-8:
        raise ValueError("target eigenvalue must be simple and well separated")
    vector = eigenvectors[:, eigenvalue_index]
    eigenvalue = eigenvalues[eigenvalue_index]
    derivative = float(
        np.real(
            vector.conj()
            @ (delta_hamiltonian - eigenvalue * delta_overlap)
            @ vector
        )
    )
    step_values = [float(step) for step in steps]
    if not step_values or any(step <= 0.0 for step in step_values):
        raise ValueError("steps must contain positive values")
    remainders: list[float] = []
    for step in step_values:
        perturbed_eigenvalues, _ = solve_generalized(
            hamiltonian + step * delta_hamiltonian,
            overlap + step * delta_overlap,
        )
        remainder = abs(
            perturbed_eigenvalues[eigenvalue_index]
            - eigenvalue
            - step * derivative
        )
        remainders.append(float(remainder))
    ratios = [
        remainders[index] / remainders[index + 1]
        for index in range(len(remainders) - 1)
    ]
    return {
        "derivative": derivative,
        "eigenvalue_index": eigenvalue_index,
        "steps": step_values,
        "remainders": remainders,
        "successive_remainder_ratios": ratios,
    }


def condition_scan(
    *, seed: int, size: int, conditions: Iterable[float]
) -> list[dict[str, float]]:
    """Solve deterministic problems across requested overlap condition numbers."""

    rows: list[dict[str, float]] = []
    for condition in conditions:
        hamiltonian, overlap = make_problem(
            size=size,
            seed=seed,
            overlap_condition=float(condition),
        )
        eigenvalues, eigenvectors = solve_generalized(hamiltonian, overlap)
        diagnostics = solver_diagnostics(
            hamiltonian, overlap, eigenvalues, eigenvectors
        )
        rows.append(
            {
                "requested_condition": float(condition),
                **diagnostics,
            }
        )
    return rows


def failure_samples(
    hamiltonian: ComplexMatrix,
    overlap: ComplexMatrix,
    transform: ComplexMatrix,
) -> dict[str, Any]:
    """Return detectable failures for inconsistent transforms and indefinite S."""

    reference_eigenvalues, _ = solve_generalized(hamiltonian, overlap)
    transformed_hamiltonian = transform.conj().T @ hamiltonian @ transform
    inconsistent_eigenvalues, _ = solve_generalized(
        transformed_hamiltonian, overlap
    )
    inconsistent_spectrum_error = float(
        np.max(np.abs(inconsistent_eigenvalues - reference_eigenvalues))
    )
    indefinite_overlap = np.eye(overlap.shape[0], dtype=np.complex128)
    indefinite_overlap[-1, -1] = -0.1
    rejected = False
    message = ""
    try:
        solve_generalized(hamiltonian, indefinite_overlap)
    except ValueError as error:
        rejected = True
        message = str(error)
    return {
        "h_only_transform_maximum_spectrum_error": inconsistent_spectrum_error,
        "indefinite_overlap_rejected": rejected,
        "indefinite_overlap_message": message,
    }


def run_experiment(*, seed: int = 20260803, size: int = 6) -> dict[str, Any]:
    """Run all chapter-1 numerical checks and return JSON-serializable results."""

    hamiltonian, overlap = make_problem(size=size, seed=seed)
    eigenvalues, eigenvectors = solve_generalized(hamiltonian, overlap)
    baseline = solver_diagnostics(
        hamiltonian, overlap, eigenvalues, eigenvectors
    )

    transform = make_basis_transform(size=size, seed=seed + 1)
    transformed_hamiltonian, transformed_overlap = transform_basis(
        hamiltonian, overlap, transform
    )
    transformed_eigenvalues, transformed_eigenvectors = solve_generalized(
        transformed_hamiltonian, transformed_overlap
    )
    basis_change = {
        "transform_condition_number": float(np.linalg.cond(transform)),
        "maximum_spectrum_difference": float(
            np.max(np.abs(transformed_eigenvalues - eigenvalues))
        ),
        **{
            f"transformed_{key}": value
            for key, value in solver_diagnostics(
                transformed_hamiltonian,
                transformed_overlap,
                transformed_eigenvalues,
                transformed_eigenvectors,
            ).items()
        },
    }

    target_index = 0
    high_index = size - 1
    target_perturbation, high_perturbation = (
        equal_norm_eigenprojector_perturbations(
            overlap,
            eigenvectors,
            target_index=target_index,
            orthogonal_index=high_index,
            frobenius_norm=0.02,
        )
    )
    propagation_rows: list[dict[str, Any]] = []
    for name, perturbation in (
        ("target_low_energy_subspace", target_perturbation),
        ("orthogonal_high_energy_subspace", high_perturbation),
    ):
        perturbed_eigenvalues, _ = solve_generalized(
            hamiltonian + perturbation, overlap
        )
        propagation_rows.append(
            {
                "direction": name,
                "matrix_frobenius_norm": float(
                    np.linalg.norm(perturbation, ord="fro")
                ),
                "full_spectrum_mae": float(
                    np.mean(np.abs(perturbed_eigenvalues - eigenvalues))
                ),
                "target_eigenvalue_shift": float(
                    perturbed_eigenvalues[target_index]
                    - eigenvalues[target_index]
                ),
                "low_two_maximum_error": float(
                    np.max(
                        np.abs(perturbed_eigenvalues[:2] - eigenvalues[:2])
                    )
                ),
            }
        )

    rng = np.random.default_rng(seed + 2)
    raw_delta_h = _complex_random_matrix(rng, size)
    delta_h = (raw_delta_h + raw_delta_h.conj().T) / 2.0
    delta_h /= np.linalg.norm(delta_h, ord=2)
    raw_delta_s = _complex_random_matrix(rng, size)
    delta_s = (raw_delta_s + raw_delta_s.conj().T) / 2.0
    delta_s *= 0.1 / np.linalg.norm(delta_s, ord=2)
    perturbation_check = first_order_remainders(
        hamiltonian,
        overlap,
        delta_h,
        delta_s,
        eigenvalue_index=min(2, size - 1),
        steps=(1.0e-3, 5.0e-4, 2.5e-4),
    )

    return {
        "metadata": {
            "seed": seed,
            "size": size,
            "numpy_version": np.__version__,
            "scipy_version": scipy_version,
        },
        "baseline": baseline,
        "basis_change": basis_change,
        "error_propagation": propagation_rows,
        "first_order_check": perturbation_check,
        "condition_scan": condition_scan(
            seed=seed,
            size=size,
            conditions=(1.0, 1.0e2, 1.0e4, 1.0e6),
        ),
        "failure_samples": failure_samples(
            hamiltonian, overlap, transform
        ),
    }


def _format_float(value: float) -> str:
    return f"{value:.6e}"


def format_markdown(results: dict[str, Any]) -> str:
    """Format the core experiment results as human-readable Markdown tables."""

    lines = [
        "# Generalized eigenproblem experiment",
        "",
        "## Baseline and basis change",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    baseline = results["baseline"]
    basis_change = results["basis_change"]
    for key in (
        "maximum_normalized_residual",
        "s_orthogonality_frobenius",
        "overlap_minimum_eigenvalue",
        "overlap_condition_number",
    ):
        lines.append(f"| {key} | {_format_float(baseline[key])} |")
    lines.append(
        "| basis_change_maximum_spectrum_difference | "
        f"{_format_float(basis_change['maximum_spectrum_difference'])} |"
    )
    lines.extend(
        [
            "",
            "## Equal-norm error propagation",
            "",
            "| direction | matrix Frobenius norm | full-spectrum MAE | "
            "target shift | low-two maximum error |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in results["error_propagation"]:
        lines.append(
            f"| {row['direction']} | "
            f"{_format_float(row['matrix_frobenius_norm'])} | "
            f"{_format_float(row['full_spectrum_mae'])} | "
            f"{_format_float(row['target_eigenvalue_shift'])} | "
            f"{_format_float(row['low_two_maximum_error'])} |"
        )
    lines.extend(
        [
            "",
            "## First-order remainder",
            "",
            "| step | absolute remainder |",
            "|---:|---:|",
        ]
    )
    first_order = results["first_order_check"]
    for step, remainder in zip(
        first_order["steps"], first_order["remainders"], strict=True
    ):
        lines.append(
            f"| {_format_float(step)} | {_format_float(remainder)} |"
        )
    lines.extend(
        [
            "",
            "## Failure samples",
            "",
            "| failure | detection |",
            "|---|---:|",
            "| H-only basis transform spectrum error | "
            f"{_format_float(results['failure_samples']['h_only_transform_maximum_spectrum_error'])} |",
            "| indefinite overlap rejected | "
            f"{results['failure_samples']['indefinite_overlap_rejected']} |",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--size", type=int, default=6)
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    arguments = parser.parse_args()
    results = run_experiment(seed=arguments.seed, size=arguments.size)
    if arguments.format == "json":
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(format_markdown(results))


if __name__ == "__main__":
    main()
