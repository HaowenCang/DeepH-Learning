from __future__ import annotations

import unittest

import numpy as np

from fourier_reference import fixed_example, forward, inverse


class FourierReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.real_space, self.n_k = fixed_example()
        self.zero = np.zeros_like(self.real_space[0])

    def reconstruction_error(
        self, recovered: dict[int, np.ndarray]
    ) -> float:
        return max(
            float(
                np.linalg.norm(
                    recovered[translation]
                    - self.real_space.get(translation, self.zero)
                )
            )
            for translation in range(self.n_k)
        )

    def test_hermiticity_and_inverse_reconstruction(self) -> None:
        k_space = forward(self.real_space, self.n_k, phase_sign=1)
        hermiticity = max(
            float(np.linalg.norm(block - block.conj().T))
            for block in k_space
        )
        self.assertLess(hermiticity, 1.0e-12)
        self.assertLess(
            self.reconstruction_error(inverse(k_space, phase_sign=-1)),
            1.0e-12,
        )

    def test_missing_conjugate_pair_breaks_hermiticity(self) -> None:
        incomplete = {0: self.real_space[0], 1: self.real_space[1]}
        k_space = forward(incomplete, self.n_k, phase_sign=1)
        hermiticity = max(
            float(np.linalg.norm(block - block.conj().T))
            for block in k_space
        )
        self.assertGreater(hermiticity, 1.0e-6)

    def test_unsynchronized_phase_sign_breaks_reconstruction(self) -> None:
        k_space = forward(self.real_space, self.n_k, phase_sign=1)
        mismatched = inverse(k_space, phase_sign=1)
        self.assertGreater(self.reconstruction_error(mismatched), 1.0e-6)


if __name__ == "__main__":
    unittest.main()

