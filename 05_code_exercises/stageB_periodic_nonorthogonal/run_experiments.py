"""Deterministic T-B01--T-B10 acceptance suite with JSON output."""

from __future__ import annotations

import argparse
import json
import platform
from collections.abc import Callable
from typing import Any

import numpy as np
import scipy

from stageb_models import (
    CONVENTIONS_VERSION,
    definite_overlap,
    fourier_forward,
    fourier_inverse,
    generalized_bands,
    hermitian_residual,
    normalized_eigenpair_residuals,
    random_hermitian,
    random_unitary,
    s_orthogonality_residual,
    solve_generalized,
    transform_pencil,
)


DEFAULT_SEED = 20260803
DEFAULT_DIMENSION = 6
DEFAULT_NK = 64

TOLERANCES = {
    "normalized_residual_well_conditioned": 1.0e-12,
    "s_orthogonality_well_conditioned": 1.0e-11,
    "spectrum_invariance": 1.0e-11,
    "condition_scan_residual": 1.0e-10,
    "condition_scan_orthogonality": 1.0e-8,
    "fourier_reconstruction": 1.0e-12,
    "hermiticity": 1.0e-12,
    "band_residual": 1.0e-11,
    "minimum_band_overlap_eigenvalue": 1.0e-3,
    "failure_minimum_difference": 1.0e-4,
    "fourier_failure_minimum": 1.0e-6,
    "band_failure_minimum": 1.0e-3,
    "ill_conditioned_eigenvalue_threshold": 1.0e-7,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _captures_value_error(action: Callable[[], object], phrase: str) -> bool:
    try:
        action()
    except ValueError as error:
        return phrase.lower() in str(error).lower()
    return False


def _paired_random_blocks(
    rng: np.random.Generator, dimension: int
) -> dict[int, np.ndarray]:
    zero = random_hermitian(rng, dimension, scale=0.5)
    one = 0.12 * (
        rng.normal(size=(dimension, dimension))
        + 1j * rng.normal(size=(dimension, dimension))
    )
    two = 0.05 * (
        rng.normal(size=(dimension, dimension))
        + 1j * rng.normal(size=(dimension, dimension))
    )
    return {0: zero, 1: one, -1: one.conj().T, 2: two, -2: two.conj().T}


def _one_range_model() -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    h_blocks = {
        0: np.array([[0.2, 0.3], [0.3, 1.2]], dtype=np.complex128),
        1: np.array([[-0.4, 0.10], [0.05, -0.2]], dtype=np.complex128),
    }
    h_blocks[-1] = h_blocks[1].conj().T
    s_blocks = {
        0: np.eye(2, dtype=np.complex128),
        1: np.array([[0.08, 0.02], [0.01, 0.05]], dtype=np.complex128),
    }
    s_blocks[-1] = s_blocks[1].conj().T
    return h_blocks, s_blocks


def _two_range_model() -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    h_blocks, s_blocks = _one_range_model()
    h_blocks[2] = np.array(
        [[-0.06, 0.02j], [0.01, -0.03]], dtype=np.complex128
    )
    h_blocks[-2] = h_blocks[2].conj().T
    s_blocks[2] = np.array(
        [[0.01, 0.005j], [0.002, 0.008]], dtype=np.complex128
    )
    s_blocks[-2] = s_blocks[2].conj().T
    return h_blocks, s_blocks


def _tb01_tb02(
    rng: np.random.Generator, dimension: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    h_matrix = random_hermitian(rng, dimension)
    s_matrix = definite_overlap(rng, dimension, 1.0e3)
    values, vectors = solve_generalized(h_matrix, s_matrix)
    maximum_residual = float(
        np.max(normalized_eigenpair_residuals(h_matrix, s_matrix, values, vectors))
    )
    orthogonality = s_orthogonality_residual(s_matrix, vectors)

    non_positive = np.eye(dimension, dtype=np.complex128)
    non_positive[0, 0] = -0.1
    positive_definite_rejected = _captures_value_error(
        lambda: solve_generalized(h_matrix, non_positive), "positive definite"
    )

    non_hermitian = h_matrix.copy()
    non_hermitian[0, 1] += 0.2 + 0.1j
    non_hermitian_rejected = _captures_value_error(
        lambda: solve_generalized(non_hermitian, s_matrix), "Hermitian"
    )

    _require(
        maximum_residual <= TOLERANCES["normalized_residual_well_conditioned"],
        "T-B01 normalized residual exceeded tolerance",
    )
    _require(positive_definite_rejected, "T-B01 failed to reject indefinite overlap")
    _require(
        orthogonality <= TOLERANCES["s_orthogonality_well_conditioned"],
        "T-B02 S-orthogonality exceeded tolerance",
    )
    _require(non_hermitian_rejected, "T-B02 failed to reject non-Hermitian H")

    tb01 = {
        "status": "pass",
        "metrics": {
            "condition_number_S": float(np.linalg.cond(s_matrix)),
            "max_normalized_residual": maximum_residual,
        },
        "expected_failures": {
            "non_positive_definite_overlap_rejected": positive_definite_rejected
        },
    }
    tb02 = {
        "status": "pass",
        "metrics": {"S_orthogonality_fro": orthogonality},
        "expected_failures": {"non_Hermitian_H_rejected": non_hermitian_rejected},
    }
    return tb01, tb02


def _tb03(rng: np.random.Generator, dimension: int) -> dict[str, Any]:
    # Keep this invariance test moderately conditioned so its absolute spectral
    # tolerance measures the transform logic rather than an extreme scale.
    h_matrix = random_hermitian(rng, dimension)
    s_matrix = definite_overlap(rng, dimension, 10.0)
    left = random_unitary(rng, dimension)
    right = random_unitary(rng, dimension)
    scales = np.linspace(0.65, 1.35, dimension)
    transform = left @ np.diag(scales) @ right

    reference = solve_generalized(h_matrix, s_matrix)[0]
    transformed_h, transformed_s = transform_pencil(h_matrix, s_matrix, transform)
    transformed = solve_generalized(transformed_h, transformed_s)[0]
    spectrum_difference = float(np.max(np.abs(reference - transformed)))

    h_only = solve_generalized(transformed_h, s_matrix)[0]
    inconsistent_difference = float(np.max(np.abs(reference - h_only)))
    _require(
        spectrum_difference <= TOLERANCES["spectrum_invariance"],
        "T-B03 consistent transform changed the generalized spectrum",
    )
    _require(
        inconsistent_difference > TOLERANCES["failure_minimum_difference"],
        "T-B03 H-only transform did not trigger the expected spectrum failure",
    )
    return {
        "status": "pass",
        "metrics": {
            "consistent_spectrum_max_difference": spectrum_difference,
            "transform_condition_number": float(np.linalg.cond(transform)),
        },
        "expected_failures": {
            "H_only_spectrum_difference": inconsistent_difference,
            "H_only_failure_detected": True,
        },
    }


def _tb04(rng: np.random.Generator, dimension: int) -> dict[str, Any]:
    condition_numbers = [1.0, 1.0e2, 1.0e4, 1.0e6, 1.0e8]
    records: list[dict[str, Any]] = []
    for condition_number in condition_numbers:
        h_matrix = random_hermitian(rng, dimension)
        s_matrix = definite_overlap(rng, dimension, condition_number)
        values, vectors = solve_generalized(h_matrix, s_matrix)
        maximum_residual = float(
            np.max(
                normalized_eigenpair_residuals(
                    h_matrix, s_matrix, values, vectors
                )
            )
        )
        orthogonality = s_orthogonality_residual(s_matrix, vectors)
        minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(s_matrix)))
        ill_conditioned = (
            minimum_eigenvalue
            < TOLERANCES["ill_conditioned_eigenvalue_threshold"]
        )
        _require(
            np.isfinite(maximum_residual) and np.isfinite(orthogonality),
            "T-B04 produced a non-finite metric",
        )
        if condition_number <= 1.0e6:
            _require(
                maximum_residual <= TOLERANCES["condition_scan_residual"],
                "T-B04 residual exceeded the first-four-level tolerance",
            )
            _require(
                orthogonality <= TOLERANCES["condition_scan_orthogonality"],
                "T-B04 orthogonality exceeded the first-four-level tolerance",
            )
        records.append(
            {
                "target_condition_number": condition_number,
                "actual_condition_number": float(np.linalg.cond(s_matrix)),
                "minimum_S_eigenvalue": minimum_eigenvalue,
                "max_normalized_residual": maximum_residual,
                "S_orthogonality_fro": orthogonality,
                "ill_conditioned": ill_conditioned,
            }
        )

    diagnostic_triggered = records[-1]["ill_conditioned"] and not any(
        record["ill_conditioned"] for record in records[:-1]
    )
    _require(diagnostic_triggered, "T-B04 ill-conditioned diagnostic was not selective")
    return {
        "status": "pass",
        "metrics": {"scan": records},
        "expected_failures": {
            "small_eigenvalue_diagnostic_triggered": diagnostic_triggered
        },
    }


def _tb05_tb06(
    rng: np.random.Generator, dimension: int, nk: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    h_blocks = _paired_random_blocks(rng, dimension)
    s_blocks = _paired_random_blocks(rng, dimension)
    k_grid = 2.0 * np.pi * np.arange(nk) / nk
    h_k = fourier_forward(h_blocks, k_grid)
    s_k = fourier_forward(s_blocks, k_grid)
    recovered_h = fourier_inverse(h_k, k_grid, h_blocks)
    recovered_s = fourier_inverse(s_k, k_grid, s_blocks)
    reconstruction_error = max(
        [
            float(np.max(np.abs(recovered_h[translation] - matrix)))
            for translation, matrix in h_blocks.items()
        ]
        + [
            float(np.max(np.abs(recovered_s[translation] - matrix)))
            for translation, matrix in s_blocks.items()
        ]
    )

    wrong_sign_errors: list[float] = []
    for blocks, k_matrices in ((h_blocks, h_k), (s_blocks, s_k)):
        for translation, matrix in blocks.items():
            wrong = np.sum(
                np.exp(1j * k_grid * translation)[:, None, None] * k_matrices,
                axis=0,
            ) / nk
            wrong_sign_errors.append(float(np.max(np.abs(wrong - matrix))))
    wrong_sign_error = max(wrong_sign_errors)
    _require(
        reconstruction_error <= TOLERANCES["fourier_reconstruction"],
        "T-B05 Fourier reconstruction exceeded tolerance",
    )
    _require(
        wrong_sign_error > TOLERANCES["fourier_failure_minimum"],
        "T-B05 same-sign inverse did not fail",
    )

    maximum_h_hermiticity = max(hermitian_residual(matrix) for matrix in h_k)
    maximum_s_hermiticity = max(hermitian_residual(matrix) for matrix in s_k)
    maximum_hermiticity = max(maximum_h_hermiticity, maximum_s_hermiticity)
    broken = dict(h_blocks)
    del broken[-2]
    broken_k = fourier_forward(broken, k_grid)
    broken_hermiticity = max(hermitian_residual(matrix) for matrix in broken_k)
    _require(
        maximum_hermiticity <= TOLERANCES["hermiticity"],
        "T-B06 Hermiticity exceeded tolerance",
    )
    _require(
        broken_hermiticity > TOLERANCES["fourier_failure_minimum"],
        "T-B06 missing conjugate block did not fail",
    )
    tb05 = {
        "status": "pass",
        "metrics": {"max_block_reconstruction_error": reconstruction_error},
        "expected_failures": {
            "same_sign_inverse_error": wrong_sign_error,
            "same_sign_inverse_failure_detected": True,
        },
    }
    tb06 = {
        "status": "pass",
        "metrics": {
            "max_H_k_Hermiticity_fro": maximum_h_hermiticity,
            "max_S_k_Hermiticity_fro": maximum_s_hermiticity,
            "max_k_Hermiticity_fro": maximum_hermiticity,
        },
        "expected_failures": {
            "missing_pair_Hermiticity_fro": broken_hermiticity,
            "missing_pair_failure_detected": True,
        },
    }
    return tb05, tb06


def _tb07(nk: int) -> tuple[dict[str, Any], dict[int, np.ndarray], dict[int, np.ndarray]]:
    h_blocks, s_blocks = _one_range_model()
    k_grid = 2.0 * np.pi * np.arange(nk) / nk
    h_k = fourier_forward(h_blocks, k_grid)
    s_k = fourier_forward(s_blocks, k_grid)
    maximum_residual = 0.0
    minimum_s_eigenvalue = np.inf
    ignore_s_difference = 0.0
    for h_matrix, s_matrix in zip(h_k, s_k, strict=True):
        values, vectors = solve_generalized(h_matrix, s_matrix)
        maximum_residual = max(
            maximum_residual,
            float(
                np.max(
                    normalized_eigenpair_residuals(
                        h_matrix, s_matrix, values, vectors
                    )
                )
            ),
        )
        minimum_s_eigenvalue = min(
            minimum_s_eigenvalue, float(np.min(np.linalg.eigvalsh(s_matrix)))
        )
        ignore_s_difference = max(
            ignore_s_difference,
            float(np.max(np.abs(values - np.linalg.eigvalsh(h_matrix)))),
        )
    _require(
        maximum_residual <= TOLERANCES["band_residual"],
        "T-B07 band residual exceeded tolerance",
    )
    _require(
        minimum_s_eigenvalue > TOLERANCES["minimum_band_overlap_eigenvalue"],
        "T-B07 overlap lost positive definiteness",
    )
    _require(
        ignore_s_difference > TOLERANCES["band_failure_minimum"],
        "T-B07 ignoring overlap did not trigger a band failure",
    )
    return (
        {
            "status": "pass",
            "metrics": {
                "max_normalized_band_residual": maximum_residual,
                "minimum_S_k_eigenvalue": minimum_s_eigenvalue,
            },
            "expected_failures": {
                "ignore_S_max_energy_difference": ignore_s_difference,
                "ignore_S_failure_detected": True,
            },
        },
        h_blocks,
        s_blocks,
    )


def _tb08(
    h_blocks: dict[int, np.ndarray], s_blocks: dict[int, np.ndarray], nk: int
) -> dict[str, Any]:
    k_grid = 2.0 * np.pi * np.arange(nk) / nk
    h_k = fourier_forward(h_blocks, k_grid)
    s_k = fourier_forward(s_blocks, k_grid)
    maximum_spectrum_difference = 0.0
    maximum_transformed_residual = 0.0
    one_sided_difference = 0.0
    centers = np.array([0.0, 0.37])
    for k_value, h_matrix, s_matrix in zip(k_grid, h_k, s_k, strict=True):
        values, vectors = solve_generalized(h_matrix, s_matrix)
        unitary = np.diag(np.exp(1j * k_value * centers))
        transformed_h, transformed_s = transform_pencil(
            h_matrix, s_matrix, unitary
        )
        transformed_values, _ = solve_generalized(transformed_h, transformed_s)
        transformed_vectors = unitary.conj().T @ vectors
        maximum_spectrum_difference = max(
            maximum_spectrum_difference,
            float(np.max(np.abs(values - transformed_values))),
        )
        maximum_transformed_residual = max(
            maximum_transformed_residual,
            float(
                np.max(
                    normalized_eigenpair_residuals(
                        transformed_h,
                        transformed_s,
                        values,
                        transformed_vectors,
                    )
                )
            ),
        )
        h_only_values = solve_generalized(transformed_h, s_matrix)[0]
        one_sided_difference = max(
            one_sided_difference,
            float(np.max(np.abs(values - h_only_values))),
        )
    _require(
        maximum_spectrum_difference <= TOLERANCES["spectrum_invariance"],
        "T-B08 center-gauge spectrum changed",
    )
    _require(
        maximum_transformed_residual <= TOLERANCES["band_residual"],
        "T-B08 center-gauge residual exceeded tolerance",
    )
    _require(
        one_sided_difference > TOLERANCES["failure_minimum_difference"],
        "T-B08 H-only gauge transform did not fail",
    )
    return {
        "status": "pass",
        "metrics": {
            "cell_to_center_gauge_spectrum_max_difference": maximum_spectrum_difference,
            "center_gauge_max_normalized_residual": maximum_transformed_residual,
        },
        "expected_failures": {
            "H_only_gauge_spectrum_difference": one_sided_difference,
            "H_only_gauge_failure_detected": True,
        },
    }


def _tb09() -> dict[str, Any]:
    h_blocks, s_blocks = _two_range_model()
    k_grid = 2.0 * np.pi * np.arange(64) / 64
    h_k = fourier_forward(h_blocks, k_grid)
    s_k = fourier_forward(s_blocks, k_grid)
    recovered_h = fourier_inverse(h_k, k_grid, h_blocks)
    recovered_s = fourier_inverse(s_k, k_grid, s_blocks)
    reconstruction_error = max(
        [
            float(np.max(np.abs(recovered_h[r] - block)))
            for r, block in h_blocks.items()
        ]
        + [
            float(np.max(np.abs(recovered_s[r] - block)))
            for r, block in s_blocks.items()
        ]
    )

    h_truncated = {r: block for r, block in h_blocks.items() if abs(r) <= 1}
    s_truncated = {r: block for r, block in s_blocks.items() if abs(r) <= 1}
    truncation_errors: dict[str, float] = {}
    for sample_count in (64, 128):
        grid = 2.0 * np.pi * np.arange(sample_count) / sample_count
        full_bands = generalized_bands(h_blocks, s_blocks, grid)[0]
        truncated_bands = generalized_bands(h_truncated, s_truncated, grid)[0]
        truncation_errors[str(sample_count)] = float(
            np.max(np.abs(full_bands - truncated_bands))
        )
    restored_h = dict(h_truncated)
    restored_s = dict(s_truncated)
    restored_h.update({2: h_blocks[2], -2: h_blocks[-2]})
    restored_s.update({2: s_blocks[2], -2: s_blocks[-2]})
    restored_bands = generalized_bands(restored_h, restored_s, k_grid)[0]
    reference_bands = generalized_bands(h_blocks, s_blocks, k_grid)[0]
    restoration_error = float(np.max(np.abs(restored_bands - reference_bands)))
    _require(
        reconstruction_error <= TOLERANCES["fourier_reconstruction"],
        "T-B09 full-block reconstruction exceeded tolerance",
    )
    _require(
        all(
            value > TOLERANCES["fourier_failure_minimum"]
            for value in truncation_errors.values()
        ),
        "T-B09 truncation error was hidden by k-point sampling",
    )
    _require(
        restoration_error <= TOLERANCES["fourier_reconstruction"],
        "T-B09 restoring the blocks did not restore the spectrum",
    )
    return {
        "status": "pass",
        "metrics": {
            "full_block_reconstruction_error": reconstruction_error,
            "restored_spectrum_error": restoration_error,
        },
        "expected_failures": {
            "truncation_band_errors_by_Nk": truncation_errors,
            "denser_sampling_did_not_remove_truncation": True,
        },
    }


def _tb10(rng: np.random.Generator) -> dict[str, Any]:
    h_blocks, s_blocks = _one_range_model()
    k_value = 1.234
    h_matrix = fourier_forward(h_blocks, [k_value])[0]
    s_matrix = fourier_forward(s_blocks, [k_value])[0]
    values, vectors = solve_generalized(h_matrix, s_matrix)
    transforms = {
        "orbital_permutation": np.array([[0.0, 1.0], [1.0, 0.0]], complex),
        "phase_flip": np.diag(np.array([1.0, -1.0], complex)),
        "unitary_subspace_mix": random_unitary(rng, 2),
    }
    maximum_spectrum_difference = 0.0
    maximum_residual = 0.0
    for transform in transforms.values():
        transformed_h, transformed_s = transform_pencil(
            h_matrix, s_matrix, transform
        )
        transformed_values = solve_generalized(transformed_h, transformed_s)[0]
        transformed_vectors = transform.conj().T @ vectors
        maximum_spectrum_difference = max(
            maximum_spectrum_difference,
            float(np.max(np.abs(values - transformed_values))),
        )
        maximum_residual = max(
            maximum_residual,
            float(
                np.max(
                    normalized_eigenpair_residuals(
                        transformed_h,
                        transformed_s,
                        values,
                        transformed_vectors,
                    )
                )
            ),
        )
    permutation = transforms["orbital_permutation"]
    row_only = permutation.conj().T @ h_matrix
    row_only_hermiticity = hermitian_residual(row_only)
    _require(
        maximum_spectrum_difference <= TOLERANCES["spectrum_invariance"],
        "T-B10 unitary transform changed the spectrum",
    )
    _require(
        maximum_residual <= TOLERANCES["band_residual"],
        "T-B10 unitary transform residual exceeded tolerance",
    )
    _require(
        row_only_hermiticity > TOLERANCES["failure_minimum_difference"],
        "T-B10 row-only permutation did not break Hermiticity",
    )
    return {
        "status": "pass",
        "metrics": {
            "unitary_transforms_spectrum_max_difference": maximum_spectrum_difference,
            "unitary_transforms_max_normalized_residual": maximum_residual,
        },
        "expected_failures": {
            "row_only_permutation_Hermiticity_fro": row_only_hermiticity,
            "row_only_permutation_failure_detected": True,
        },
    }


def run_suite(
    *, seed: int = DEFAULT_SEED, dimension: int = DEFAULT_DIMENSION, nk: int = DEFAULT_NK
) -> dict[str, Any]:
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if nk < 8:
        raise ValueError("nk must be at least eight")
    rng = np.random.default_rng(seed)
    tests: dict[str, Any] = {}
    tests["T-B01"], tests["T-B02"] = _tb01_tb02(rng, dimension)
    tests["T-B03"] = _tb03(rng, dimension)
    tests["T-B04"] = _tb04(rng, dimension)
    tests["T-B05"], tests["T-B06"] = _tb05_tb06(rng, dimension, nk)
    tests["T-B07"], h_blocks, s_blocks = _tb07(nk)
    tests["T-B08"] = _tb08(h_blocks, s_blocks, nk)
    tests["T-B09"] = _tb09()
    tests["T-B10"] = _tb10(rng)
    return {
        "conventions_version": CONVENTIONS_VERSION,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "seed": seed,
        "matrix_dimension": dimension,
        "N_k": nk,
        "tolerances": TOLERANCES,
        "tests": tests,
        "overall_pass": all(test["status"] == "pass" for test in tests.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dimension", type=int, default=DEFAULT_DIMENSION)
    parser.add_argument("--nk", type=int, default=DEFAULT_NK)
    parser.add_argument("--indent", type=int, default=2)
    parser.add_argument("--format", choices=("json",), default="json")
    arguments = parser.parse_args()
    result = run_suite(
        seed=arguments.seed, dimension=arguments.dimension, nk=arguments.nk
    )
    print(json.dumps(result, ensure_ascii=False, indent=arguments.indent))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
