from __future__ import annotations

import unittest

import numpy as np

from experiment import (
    condition_scan,
    equal_norm_eigenprojector_perturbations,
    failure_samples,
    first_order_remainders,
    make_basis_transform,
    make_problem,
    run_experiment,
    solve_generalized,
    solver_diagnostics,
    transform_basis,
    two_orbital_closed_form_eigenvalues,
)


class GeneralizedEigenExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hamiltonian, self.overlap = make_problem(
            size=6, seed=20260803, overlap_condition=10.0
        )

    def test_solver_residual_and_s_orthogonality(self) -> None:
        eigenvalues, eigenvectors = solve_generalized(
            self.hamiltonian, self.overlap
        )
        diagnostics = solver_diagnostics(
            self.hamiltonian,
            self.overlap,
            eigenvalues,
            eigenvectors,
        )
        self.assertLess(diagnostics["maximum_normalized_residual"], 1.0e-13)
        self.assertLess(diagnostics["s_orthogonality_frobenius"], 1.0e-12)
        self.assertAlmostEqual(
            diagnostics["overlap_condition_number"], 10.0, places=10
        )

    def test_consistent_basis_change_preserves_spectrum(self) -> None:
        reference, _ = solve_generalized(self.hamiltonian, self.overlap)
        transform = make_basis_transform(size=6, seed=20260804, condition=3.0)
        transformed_h, transformed_s = transform_basis(
            self.hamiltonian, self.overlap, transform
        )
        transformed, _ = solve_generalized(transformed_h, transformed_s)
        self.assertLess(float(np.max(np.abs(reference - transformed))), 1.0e-12)

    def test_equal_norm_perturbations_have_different_target_effects(self) -> None:
        eigenvalues, eigenvectors = solve_generalized(
            self.hamiltonian, self.overlap
        )
        target, orthogonal = equal_norm_eigenprojector_perturbations(
            self.overlap,
            eigenvectors,
            target_index=0,
            orthogonal_index=5,
            frobenius_norm=0.02,
        )
        self.assertAlmostEqual(np.linalg.norm(target, ord="fro"), 0.02)
        self.assertAlmostEqual(np.linalg.norm(orthogonal, ord="fro"), 0.02)
        target_eigenvalues, _ = solve_generalized(
            self.hamiltonian + target, self.overlap
        )
        orthogonal_eigenvalues, _ = solve_generalized(
            self.hamiltonian + orthogonal, self.overlap
        )
        target_shift = float(target_eigenvalues[0] - eigenvalues[0])
        orthogonal_shift = float(orthogonal_eigenvalues[0] - eigenvalues[0])
        self.assertGreater(abs(target_shift), 1.0e-3)
        self.assertLess(abs(orthogonal_shift), 1.0e-12)

    def test_first_order_remainder_is_quadratic(self) -> None:
        rng = np.random.default_rng(20260805)
        raw_h = rng.normal(size=(6, 6)) + 1j * rng.normal(size=(6, 6))
        delta_h = (raw_h + raw_h.conj().T) / 2.0
        delta_h /= np.linalg.norm(delta_h, ord=2)
        raw_s = rng.normal(size=(6, 6)) + 1j * rng.normal(size=(6, 6))
        delta_s = (raw_s + raw_s.conj().T) / 2.0
        delta_s *= 0.1 / np.linalg.norm(delta_s, ord=2)
        result = first_order_remainders(
            self.hamiltonian,
            self.overlap,
            delta_h,
            delta_s,
            eigenvalue_index=2,
            steps=(1.0e-3, 5.0e-4, 2.5e-4),
        )
        for ratio in result["successive_remainder_ratios"]:
            self.assertGreater(ratio, 3.8)
            self.assertLess(ratio, 4.2)

    def test_requested_overlap_conditions_are_constructed(self) -> None:
        rows = condition_scan(
            seed=20260803,
            size=6,
            conditions=(1.0, 1.0e2, 1.0e4),
        )
        for row in rows:
            self.assertAlmostEqual(
                row["overlap_condition_number"],
                row["requested_condition"],
                delta=max(1.0e-9, row["requested_condition"] * 1.0e-10),
            )
            self.assertLess(row["maximum_normalized_residual"], 1.0e-10)

    def test_invalid_overlap_and_inconsistent_transform_are_detected(self) -> None:
        transform = make_basis_transform(size=6, seed=20260804, condition=3.0)
        failures = failure_samples(self.hamiltonian, self.overlap, transform)
        self.assertTrue(failures["indefinite_overlap_rejected"])
        self.assertIn("positive definite", failures["indefinite_overlap_message"])
        self.assertGreater(
            failures["h_only_transform_maximum_spectrum_error"], 1.0e-3
        )

    def test_nonhermitian_hamiltonian_is_rejected(self) -> None:
        invalid = self.hamiltonian.copy()
        invalid[0, 1] += 0.1
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            solve_generalized(invalid, self.overlap)

    def test_minimum_supported_and_unsupported_sizes(self) -> None:
        result = run_experiment(seed=20260803, size=2)
        self.assertEqual(result["metadata"]["size"], 2)
        self.assertEqual(
            result["first_order_check"]["eigenvalue_index"], 1
        )
        with self.assertRaisesRegex(ValueError, "at least 2"):
            run_experiment(seed=20260803, size=1)

    def test_two_orbital_closed_form_and_failures(self) -> None:
        epsilon_1 = -0.8
        epsilon_2 = 1.1
        hopping = 0.25 + 0.08j
        overlap_value = 0.18 - 0.04j
        hamiltonian = np.asarray(
            [
                [epsilon_1, hopping],
                [np.conj(hopping), epsilon_2],
            ],
            dtype=np.complex128,
        )
        overlap = np.asarray(
            [
                [1.0, overlap_value],
                [np.conj(overlap_value), 1.0],
            ],
            dtype=np.complex128,
        )
        closed = two_orbital_closed_form_eigenvalues(
            epsilon_1=epsilon_1,
            epsilon_2=epsilon_2,
            hopping=hopping,
            overlap_value=overlap_value,
        )
        numerical, _ = solve_generalized(hamiltonian, overlap)
        np.testing.assert_allclose(closed, numerical, atol=1.0e-12, rtol=0.0)

        transform = np.asarray(
            [[1.0, 0.2 + 0.1j], [-0.1 + 0.05j, 1.15]],
            dtype=np.complex128,
        )
        transformed_h, transformed_s = transform_basis(
            hamiltonian, overlap, transform
        )
        transformed, _ = solve_generalized(transformed_h, transformed_s)
        np.testing.assert_allclose(
            numerical, transformed, atol=1.0e-12, rtol=0.0
        )

        with self.assertRaisesRegex(ValueError, r"abs\(overlap_value\) < 1"):
            two_orbital_closed_form_eigenvalues(
                epsilon_1=epsilon_1,
                epsilon_2=epsilon_2,
                hopping=hopping,
                overlap_value=1.0,
            )

    def test_full_experiment_schema_and_core_thresholds(self) -> None:
        results = run_experiment(seed=20260803, size=6)
        self.assertEqual(results["metadata"]["seed"], 20260803)
        self.assertEqual(results["metadata"]["numpy_version"], "2.3.5")
        self.assertEqual(results["metadata"]["scipy_version"], "1.18.0")
        self.assertEqual(len(results["error_propagation"]), 2)
        self.assertEqual(len(results["condition_scan"]), 4)
        self.assertLess(
            results["basis_change"]["maximum_spectrum_difference"], 1.0e-12
        )
        self.assertTrue(
            results["failure_samples"]["indefinite_overlap_rejected"]
        )


if __name__ == "__main__":
    unittest.main()
