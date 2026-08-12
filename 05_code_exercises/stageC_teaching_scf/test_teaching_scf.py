from __future__ import annotations

import copy
import unittest

from run_experiments import run_suite
from teaching_scf import (
    CONVENTIONS_VERSION,
    REQUIRED_PATHS,
    SCHEMA_NEGATIVE_MUTATIONS,
    canonical_sha256,
    display_path,
    missing_path_failures,
    mutated_label_record,
    run_linear_scf,
    run_nonlinear_scf,
    schema_failure_witnesses,
    synthetic_label_record,
    validate_label_record,
)


class StageCAcceptanceTests(unittest.TestCase):
    def test_default_acceptance_suite(self) -> None:
        result = run_suite(seed=20260805, model_size=12, grid_size=64)
        self.assertTrue(result["overall_pass"])
        self.assertEqual(result["conventions_version"], CONVENTIONS_VERSION)
        self.assertEqual(
            list(result["tests"]),
            [f"T-C{index:02d}" for index in range(1, 11)],
        )
        for test in result["tests"].values():
            self.assertEqual(test["status"], "pass")
            self.assertTrue(test["expected_failure"]["detected"])

    def test_second_frozen_acceptance_suite(self) -> None:
        result = run_suite(seed=20260806, model_size=16, grid_size=48)
        self.assertTrue(result["overall_pass"])
        self.assertEqual(result["seed"], 20260806)
        self.assertEqual(result["model_size"], 16)
        self.assertEqual(result["grid_size"], 48)
        self.assertGreater(
            result["tests"]["T-C08"]["metrics"]["relative_lost_norm"], 0.9
        )

    def test_suite_is_canonical_json_deterministic(self) -> None:
        first = run_suite(seed=20260805, model_size=12, grid_size=64)
        second = run_suite(seed=20260805, model_size=12, grid_size=64)
        self.assertEqual(canonical_sha256(first), canonical_sha256(second))

    def test_linear_zero_and_exact_twelve_update_failure(self) -> None:
        zero = run_linear_scf(
            0.8,
            100,
            1.0e-10,
            initial=[0.375, -0.4, 1.0 / 14.0],
        )
        self.assertTrue(zero["converged"])
        self.assertEqual(zero["iterations"], 0)
        self.assertIsNone(zero["estimated_rate"])

        failure = run_linear_scf(2.0, 12, 0.0, force_all_steps=True)
        self.assertEqual(len(failure["residuals"]), 13)
        self.assertGreater(
            failure["residuals"][-1], 10.0 * failure["residuals"][0]
        )

    def test_max_iterations_is_not_convergence(self) -> None:
        failure = run_nonlinear_scf(1.0, 20, 1.0e-9, 1.0e-9)
        self.assertFalse(failure["converged"])
        self.assertEqual(failure["iterations"], 20)
        self.assertEqual(failure["termination_reason"], "max_iterations")
        self.assertGreater(failure["final_residual"], 1.3)

    def test_every_required_label_path_has_a_deletion_failure(self) -> None:
        record = synthetic_label_record(20260805)
        validate_label_record(record)
        failures = missing_path_failures(record)
        self.assertEqual(len(failures), len(REQUIRED_PATHS))
        self.assertEqual(failures, [display_path(path) for path in REQUIRED_PATHS])

    def test_validator_rejects_early_m8_choice(self) -> None:
        record = synthetic_label_record(20260805)
        changed = copy.deepcopy(record)
        changed["backend"]["name"] = "forbidden-early-choice"
        with self.assertRaisesRegex(AssertionError, "resolved early"):
            validate_label_record(changed)

    def test_schema_type_shape_hash_and_m8_mutations_are_rejected(self) -> None:
        record = synthetic_label_record(20260805)
        expected_categories = {"type", "shape", "hash", "m8_choice"}
        self.assertEqual(
            {category for category, _, _ in SCHEMA_NEGATIVE_MUTATIONS},
            expected_categories,
        )
        for category, path, value in SCHEMA_NEGATIVE_MUTATIONS:
            path_name = display_path(path)
            with self.subTest(category=category, path=path_name):
                sample = mutated_label_record(record, path, value)
                with self.assertRaises((AssertionError, ValueError)) as context:
                    validate_label_record(sample)
                self.assertIn(path_name, str(context.exception))

        witnesses = schema_failure_witnesses(record)
        self.assertEqual(len(witnesses), len(SCHEMA_NEGATIVE_MUTATIONS))
        self.assertEqual(
            {witness["category"] for witness in witnesses}, expected_categories
        )
        witness_paths = {witness["path"] for witness in witnesses}
        for required_witness in {
            "convergence.max_iterations",
            "structure.lattice",
            "sampling.k_mesh",
            "sampling.k_shift",
            "structure.boundary_conditions",
            "representation.output_object",
            "structure.id",
            "basis.type",
            "sampling.kind",
            "projection.method",
        }:
            self.assertIn(required_witness, witness_paths)

    def test_invalid_dimensions_are_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "model_size"):
            run_suite(seed=1, model_size=11, grid_size=48)
        with self.assertRaisesRegex(AssertionError, "grid_size"):
            run_suite(seed=1, model_size=12, grid_size=47)


if __name__ == "__main__":
    unittest.main()
