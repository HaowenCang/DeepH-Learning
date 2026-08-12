"""Numerical primitives for the stage-B synthetic verification suite."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import eigh


CONVENTIONS_VERSION = "stageB-v1"
ComplexMatrix = NDArray[np.complex128]


def _as_square_matrix(value: ArrayLike, name: str) -> ComplexMatrix:
    matrix = np.asarray(value, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain only finite entries")
    return matrix


def hermitian_residual(matrix: ArrayLike) -> float:
    """Return the Frobenius norm of the anti-Hermitian part."""

    square = _as_square_matrix(matrix, "matrix")
    return float(np.linalg.norm(square - square.conj().T, ord="fro"))


def normalized_eigenpair_residuals(
    hamiltonian: ArrayLike,
    overlap: ArrayLike,
    eigenvalues: ArrayLike,
    eigenvectors: ArrayLike,
) -> NDArray[np.float64]:
    """Compute the frozen per-eigenpair normalized Euclidean residual."""

    h_matrix = _as_square_matrix(hamiltonian, "hamiltonian")
    s_matrix = _as_square_matrix(overlap, "overlap")
    values = np.asarray(eigenvalues, dtype=np.float64)
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    dimension = h_matrix.shape[0]
    if s_matrix.shape != h_matrix.shape:
        raise ValueError("hamiltonian and overlap must have the same shape")
    if values.shape != (dimension,) or vectors.shape != (dimension, dimension):
        raise ValueError("eigenvalue or eigenvector shape is inconsistent")

    h_norm = np.linalg.norm(h_matrix, ord=2)
    s_norm = np.linalg.norm(s_matrix, ord=2)
    residuals = np.empty(dimension, dtype=np.float64)
    for index, energy in enumerate(values):
        vector = vectors[:, index]
        numerator = np.linalg.norm(
            h_matrix @ vector - energy * (s_matrix @ vector), ord=2
        )
        denominator = (
            h_norm + abs(energy) * s_norm
        ) * np.linalg.norm(vector, ord=2)
        if denominator == 0.0:
            residuals[index] = 0.0 if numerator == 0.0 else np.inf
        else:
            residuals[index] = numerator / denominator
    return residuals


def s_orthogonality_residual(overlap: ArrayLike, eigenvectors: ArrayLike) -> float:
    s_matrix = _as_square_matrix(overlap, "overlap")
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    if vectors.shape != s_matrix.shape:
        raise ValueError("eigenvectors and overlap must have the same shape")
    identity = np.eye(s_matrix.shape[0], dtype=np.complex128)
    return float(
        np.linalg.norm(vectors.conj().T @ s_matrix @ vectors - identity, ord="fro")
    )


def solve_generalized(
    hamiltonian: ArrayLike,
    overlap: ArrayLike,
    *,
    hermitian_tolerance: float = 1.0e-12,
    positive_tolerance: float = 1.0e-12,
) -> tuple[NDArray[np.float64], ComplexMatrix]:
    """Solve a Hermitian-definite pencil after explicit input validation."""

    h_matrix = _as_square_matrix(hamiltonian, "hamiltonian")
    s_matrix = _as_square_matrix(overlap, "overlap")
    if s_matrix.shape != h_matrix.shape:
        raise ValueError("hamiltonian and overlap must have the same shape")

    h_scale = max(1.0, float(np.linalg.norm(h_matrix, ord="fro")))
    s_scale = max(1.0, float(np.linalg.norm(s_matrix, ord="fro")))
    if hermitian_residual(h_matrix) > hermitian_tolerance * h_scale:
        raise ValueError("hamiltonian must be Hermitian")
    if hermitian_residual(s_matrix) > hermitian_tolerance * s_scale:
        raise ValueError("overlap must be Hermitian and positive definite")

    overlap_eigenvalues = np.linalg.eigvalsh(s_matrix)
    largest = max(1.0, float(np.max(np.abs(overlap_eigenvalues))))
    if float(np.min(overlap_eigenvalues)) <= positive_tolerance * largest:
        raise ValueError("overlap must be positive definite")

    values, vectors = eigh(h_matrix, s_matrix, check_finite=True)
    return np.asarray(values, dtype=np.float64), np.asarray(vectors, dtype=np.complex128)


def random_unitary(rng: np.random.Generator, dimension: int) -> ComplexMatrix:
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    q_matrix, r_matrix = np.linalg.qr(raw)
    diagonal = np.diag(r_matrix)
    phases = np.ones_like(diagonal)
    nonzero = np.abs(diagonal) > 0.0
    phases[nonzero] = diagonal[nonzero] / np.abs(diagonal[nonzero])
    return np.asarray(q_matrix @ np.diag(phases.conj()), dtype=np.complex128)


def random_hermitian(
    rng: np.random.Generator, dimension: int, *, scale: float = 1.0
) -> ComplexMatrix:
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    return np.asarray(scale * (raw + raw.conj().T) / 2.0, dtype=np.complex128)


def definite_overlap(
    rng: np.random.Generator, dimension: int, condition_number: float
) -> ComplexMatrix:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if condition_number < 1.0:
        raise ValueError("condition_number must be at least one")
    unitary = random_unitary(rng, dimension)
    eigenvalues = np.geomspace(1.0, 1.0 / condition_number, dimension)
    return np.asarray(
        unitary @ np.diag(eigenvalues) @ unitary.conj().T,
        dtype=np.complex128,
    )


def transform_pencil(
    hamiltonian: ArrayLike, overlap: ArrayLike, transform: ArrayLike
) -> tuple[ComplexMatrix, ComplexMatrix]:
    h_matrix = _as_square_matrix(hamiltonian, "hamiltonian")
    s_matrix = _as_square_matrix(overlap, "overlap")
    a_matrix = _as_square_matrix(transform, "transform")
    if h_matrix.shape != s_matrix.shape or h_matrix.shape != a_matrix.shape:
        raise ValueError("hamiltonian, overlap, and transform shapes must agree")
    if np.linalg.matrix_rank(a_matrix) != a_matrix.shape[0]:
        raise ValueError("transform must be invertible")
    return (
        np.asarray(a_matrix.conj().T @ h_matrix @ a_matrix, dtype=np.complex128),
        np.asarray(a_matrix.conj().T @ s_matrix @ a_matrix, dtype=np.complex128),
    )


def fourier_forward(
    blocks: Mapping[int, ArrayLike], k_grid: ArrayLike
) -> NDArray[np.complex128]:
    """Assemble M(k)=sum_R exp(+ikR) M(R)."""

    if not blocks:
        raise ValueError("blocks must not be empty")
    converted = {int(r): _as_square_matrix(value, f"block[{r}]") for r, value in blocks.items()}
    shapes = {matrix.shape for matrix in converted.values()}
    if len(shapes) != 1:
        raise ValueError("all blocks must have the same shape")
    grid = np.asarray(k_grid, dtype=np.float64)
    if grid.ndim != 1 or grid.size == 0 or not np.all(np.isfinite(grid)):
        raise ValueError("k_grid must be a finite nonempty vector")
    dimension = next(iter(shapes))[0]
    result = np.zeros((grid.size, dimension, dimension), dtype=np.complex128)
    for translation, matrix in converted.items():
        result += np.exp(1j * grid * translation)[:, None, None] * matrix
    return result


def fourier_inverse(
    k_matrices: ArrayLike, k_grid: ArrayLike, translations: Iterable[int]
) -> dict[int, ComplexMatrix]:
    """Recover M(R)=N^-1 sum_k exp(-ikR) M(k) on a complete BvK grid."""

    matrices = np.asarray(k_matrices, dtype=np.complex128)
    grid = np.asarray(k_grid, dtype=np.float64)
    if matrices.ndim != 3 or matrices.shape[1] != matrices.shape[2]:
        raise ValueError("k_matrices must have shape (N, M, M)")
    if grid.shape != (matrices.shape[0],):
        raise ValueError("k_grid length must match k_matrices")
    recovered: dict[int, ComplexMatrix] = {}
    for translation in translations:
        phase = np.exp(-1j * grid * int(translation))[:, None, None]
        recovered[int(translation)] = np.asarray(
            np.sum(phase * matrices, axis=0) / grid.size,
            dtype=np.complex128,
        )
    return recovered


def generalized_bands(
    h_blocks: Mapping[int, ArrayLike],
    s_blocks: Mapping[int, ArrayLike],
    k_grid: ArrayLike,
) -> tuple[NDArray[np.float64], NDArray[np.complex128]]:
    h_k = fourier_forward(h_blocks, k_grid)
    s_k = fourier_forward(s_blocks, k_grid)
    values: list[NDArray[np.float64]] = []
    vectors: list[ComplexMatrix] = []
    for h_matrix, s_matrix in zip(h_k, s_k, strict=True):
        eigenvalues, eigenvectors = solve_generalized(h_matrix, s_matrix)
        values.append(eigenvalues)
        vectors.append(eigenvectors)
    return np.asarray(values), np.asarray(vectors)
