from __future__ import annotations

import unittest

import numpy as np

from run_experiments import DEFAULT_SEED, run_suite
from stageb_models import (
    CONVENTIONS_VERSION,
    fourier_forward,
    fourier_inverse,
    normalized_eigenpair_residuals,
    solve_generalized,
    transform_pencil,
)


class StageBAcceptanceTests(unittest.TestCase):
    def test_full_acceptance_suite_default_seed(self) -> None:
        result = run_suite(seed=DEFAULT_SEED, dimension=6, nk=64)
        self.assertTrue(result["overall_pass"])
        self.assertEqual(result["conventions_version"], CONVENTIONS_VERSION)
        self.assertEqual(
            list(result["tests"]), [f"T-B{index:02d}" for index in range(1, 11)]
        )
        for test in result["tests"].values():
            self.assertEqual(test["status"], "pass")

    def test_full_acceptance_suite_second_seed_and_shape(self) -> None:
        result = run_suite(seed=20260804, dimension=4, nk=32)
        self.assertTrue(result["overall_pass"])
        self.assertEqual(result["seed"], 20260804)
        self.assertEqual(result["matrix_dimension"], 4)
        self.assertEqual(result["N_k"], 32)

    def test_fourier_pair_uses_opposite_sign_and_one_over_n(self) -> None:
        blocks = {
            0: np.array([[1.0, 0.2j], [-0.2j, 2.0]], complex),
            1: np.array([[0.1, 0.3], [-0.2j, -0.1]], complex),
        }
        blocks[-1] = blocks[1].conj().T
        grid = 2.0 * np.pi * np.arange(16) / 16
        recovered = fourier_inverse(fourier_forward(blocks, grid), grid, blocks)
        for translation, block in blocks.items():
            np.testing.assert_allclose(recovered[translation], block, atol=1.0e-12)

    def test_solver_rejects_invalid_pencils(self) -> None:
        h_matrix = np.diag([0.0, 1.0]).astype(complex)
        with self.assertRaisesRegex(ValueError, "positive definite"):
            solve_generalized(h_matrix, np.diag([1.0, -1.0]))
        h_bad = h_matrix.copy()
        h_bad[0, 1] = 0.2j
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            solve_generalized(h_bad, np.eye(2))

    def test_unitary_transform_preserves_frozen_residual(self) -> None:
        h_matrix = np.array([[0.2, 0.3j], [-0.3j, 1.1]], complex)
        s_matrix = np.array([[1.0, 0.05], [0.05, 0.9]], complex)
        values, vectors = solve_generalized(h_matrix, s_matrix)
        theta = 0.37
        unitary = np.array(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]],
            complex,
        )
        transformed_h, transformed_s = transform_pencil(
            h_matrix, s_matrix, unitary
        )
        original = normalized_eigenpair_residuals(
            h_matrix, s_matrix, values, vectors
        )
        transformed = normalized_eigenpair_residuals(
            transformed_h,
            transformed_s,
            values,
            unitary.conj().T @ vectors,
        )
        self.assertLess(float(np.max(original)), 1.0e-12)
        self.assertLess(float(np.max(transformed)), 1.0e-12)


if __name__ == "__main__":
    unittest.main()
