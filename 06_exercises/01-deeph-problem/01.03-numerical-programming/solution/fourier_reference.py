"""Executable reference for the one-dimensional discrete Fourier exercise."""

from __future__ import annotations

from typing import Mapping

import numpy as np
from numpy.typing import NDArray


ComplexMatrix = NDArray[np.complex128]


def forward(
    real_space: Mapping[int, ComplexMatrix],
    n_k: int,
    *,
    phase_sign: int = 1,
) -> NDArray[np.complex128]:
    """Return H(k)=sum_R exp(phase_sign*i*k*R) H(R)."""

    if n_k < 3:
        raise ValueError("n_k must be at least 3")
    if phase_sign not in (-1, 1):
        raise ValueError("phase_sign must be -1 or 1")
    if not real_space:
        raise ValueError("real_space must not be empty")
    blocks = [np.asarray(block, dtype=np.complex128) for block in real_space.values()]
    shape = blocks[0].shape
    if len(shape) != 2 or shape[0] != shape[1]:
        raise ValueError("blocks must be square matrices")
    if any(block.shape != shape for block in blocks):
        raise ValueError("all blocks must have the same shape")
    k_points = 2.0 * np.pi * np.arange(n_k) / n_k
    return np.stack(
        [
            sum(
                np.exp(phase_sign * 1j * k_point * translation) * block
                for translation, block in real_space.items()
            )
            for k_point in k_points
        ]
    )


def inverse(
    k_space: NDArray[np.complex128],
    *,
    phase_sign: int = -1,
) -> dict[int, ComplexMatrix]:
    """Return the finite-group inverse with an explicitly chosen phase sign."""

    k_space = np.asarray(k_space, dtype=np.complex128)
    if k_space.ndim != 3 or k_space.shape[1] != k_space.shape[2]:
        raise ValueError("k_space must have shape (n_k, n, n)")
    if phase_sign not in (-1, 1):
        raise ValueError("phase_sign must be -1 or 1")
    n_k = len(k_space)
    k_points = 2.0 * np.pi * np.arange(n_k) / n_k
    return {
        translation: np.asarray(
            sum(
                np.exp(phase_sign * 1j * k_point * translation) * block
                for k_point, block in zip(k_points, k_space, strict=True)
            )
            / n_k
        )
        for translation in range(n_k)
    }


def fixed_example() -> tuple[dict[int, ComplexMatrix], int]:
    """Return a fixed Hermitian real-space example on Z/n_k Z."""

    n_k = 8
    onsite = np.asarray(
        [[0.2, 0.1j], [-0.1j, -0.3]], dtype=np.complex128
    )
    hopping = np.asarray(
        [[0.05, 0.02 + 0.03j], [-0.01j, -0.04]],
        dtype=np.complex128,
    )
    return {0: onsite, 1: hopping, n_k - 1: hopping.conj().T}, n_k

