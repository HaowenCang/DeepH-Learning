"""Run the deterministic T-C01--T-C10 acceptance suite."""

from __future__ import annotations

import argparse
import json
import platform
from typing import Any

import numpy as np
import scipy

from teaching_scf import (
    BACKEND,
    CONVENTIONS_VERSION,
    REQUIRED_PATHS,
    SCHEMA_NEGATIVE_MUTATIONS,
    canonical_sha256,
    convergence_sequences,
    generalized_overlap_case,
    json_default,
    linear_problem,
    locality_case,
    missing_path_failures,
    projection_case,
    require,
    run_linear_scf,
    run_nonlinear_scf,
    sampling_case,
    scf_scan_record,
    schema_failure_witnesses,
    synthetic_label_record,
    validate_label_record,
)


DEFAULT_SEED = 20260805
DEFAULT_MODEL_SIZE = 12
DEFAULT_GRID_SIZE = 64


def _tc01() -> dict[str, Any]:
    jacobian, _, fixed_point = linear_problem()
    positive = run_linear_scf(0.8, 100, 1.0e-10)
    iteration_matrix = 0.2 * np.eye(3) + 0.8 * jacobian
    spectral_radius = float(np.max(np.abs(np.linalg.eigvals(iteration_matrix))))
    require(positive["converged"], "T-C01 positive run did not converge")
    require(positive["final_error"] < 1.0e-10, "T-C01 final error too large")
    require(positive["estimated_rate"] is not None, "T-C01 rate was not estimated")
    require(
        abs(positive["estimated_rate"] - spectral_radius) < 5.0e-3,
        "T-C01 estimated rate differs from spectral radius",
    )

    zero = run_linear_scf(
        0.8, 100, 1.0e-10, initial=fixed_point
    )
    require(zero["converged"] and zero["iterations"] == 0, "zero error not step 0")
    require(zero["final_residual"] < 1.0e-15, "zero error residual is not zero")
    require(zero["estimated_rate"] is None, "zero error rate must be null")

    failure = run_linear_scf(
        2.0, 12, 0.0, force_all_steps=True
    )
    unstable_matrix = -np.eye(3) + 2.0 * jacobian
    unstable_radius = float(np.max(np.abs(np.linalg.eigvals(unstable_matrix))))
    failure_ratio = failure["residuals"][-1] / failure["residuals"][0]
    require(unstable_radius == 1.8, "T-C01 unstable spectral radius changed")
    require(len(failure["residuals"]) == 13, "T-C01 must store x0 through x12")
    require(failure_ratio > 10.0, "T-C01 unstable run was not rejected")
    return {
        "status": "pass",
        "model_parameters": {
            "J_diagonal": [0.2, 0.5, -0.4],
            "b": [0.3, -0.2, 0.1],
            "positive_alpha": 0.8,
            "failure_alpha": 2.0,
            "failure_updates": 12,
        },
        "metrics": {
            "fixed_point": fixed_point.tolist(),
            "positive_final_error": positive["final_error"],
            "estimated_rate": positive["estimated_rate"],
            "spectral_radius": spectral_radius,
            "zero_initial_iterations": zero["iterations"],
        },
        "tolerances": {
            "final_error": 1.0e-10,
            "rate_difference": 5.0e-3,
        },
        "expected_failure": {
            "spectral_radius": unstable_radius,
            "residual_ratio_after_12_updates": failure_ratio,
            "detected": failure_ratio > 10.0,
        },
    }


def _tc02() -> dict[str, Any]:
    positive = run_nonlinear_scf(0.25, 80, 1.0e-9, 1.0e-9)
    require(positive["converged"], "T-C02 positive run did not converge")
    require(positive["final_residual"] < 1.0e-9, "T-C02 residual too large")
    final_density = np.asarray(positive["trajectory"][-1]["density"])
    require(abs(float(np.sum(final_density)) - 1.0) < 1.0e-12, "bad normalization")
    require(np.all(final_density > -1.0e-14), "bad positivity")

    failure = run_nonlinear_scf(
        1.0, 20, 1.0e-9, 1.0e-9, force_all_steps=True
    )
    require(not failure["converged"], "T-C02 failure run converged")
    require(failure["final_residual"] > 1.3, "T-C02 oscillation was not detected")
    return {
        "status": "pass",
        "model_parameters": {
            "electron_count": 1.0,
            "potential": [-0.1, 0.1],
            "coupling": 4.0,
            "beta": 1.0,
            "initial_density": [0.9, 0.1],
        },
        "metrics": {
            "positive_iterations": positive["iterations"],
            "positive_final_density": final_density.tolist(),
            "positive_final_residual": positive["final_residual"],
            "normalization_error": abs(float(np.sum(final_density)) - 1.0),
            "minimum_density": float(np.min(final_density)),
        },
        "tolerances": {
            "residual": 1.0e-9,
            "normalization": 1.0e-12,
            "minimum_density": -1.0e-14,
        },
        "expected_failure": {
            "kind": "oscillation_or_divergence",
            "alpha": 1.0,
            "iterations": 20,
            "final_residual": failure["final_residual"],
            "threshold": 1.3,
            "detected": failure["final_residual"] > 1.3,
        },
    }


def _tc03() -> dict[str, Any]:
    positive = run_nonlinear_scf(0.25, 80, 1.0e-9, 1.0e-9)
    require(positive["converged"], "T-C03 positive trajectory did not converge")
    require(
        positive["final_energy_change"] is not None
        and positive["final_energy_change"] < 1.0e-9,
        "T-C03 energy change too large",
    )
    for item in positive["trajectory"]:
        require(len(item["density"]) == 2, "T-C03 density shape failed")
        require(len(item["output_density"]) == 2, "T-C03 output shape failed")
        require(np.isfinite(item["residual"]), "T-C03 residual non-finite")
        require(np.isfinite(item["energy"]), "T-C03 energy non-finite")

    failure = run_nonlinear_scf(
        1.0, 20, 1.0e-9, 1.0e-9, force_all_steps=True
    )
    witness = None
    previous_fake = None
    for item in failure["trajectory"]:
        fake_energy = 1.0e-12 * item["energy"]
        if previous_fake is not None:
            fake_change = abs(fake_energy - previous_fake) / (1.0 + abs(fake_energy))
            if fake_change < 1.0e-10 and item["residual"] > 1.0:
                witness = {
                    "iteration": item["iteration"],
                    "fake_energy_change": fake_change,
                    "density_residual": item["residual"],
                }
                break
        previous_fake = fake_energy
    require(witness is not None, "T-C03 did not find fake-energy witness")
    energy_only_passes = witness["fake_energy_change"] < 1.0e-9
    dual_rejects = not (
        witness["fake_energy_change"] < 1.0e-9
        and witness["density_residual"] < 1.0e-9
    )
    require(energy_only_passes and dual_rejects, "T-C03 failure was not captured")
    return {
        "status": "pass",
        "model_parameters": {
            "energy_formula": "0.5*g*dot(n,n)+dot(v,n)",
            "fake_energy_scale": 1.0e-12,
        },
        "metrics": {
            "trajectory_length": len(positive["trajectory"]),
            "final_residual": positive["final_residual"],
            "final_energy_change": positive["final_energy_change"],
        },
        "tolerances": {"residual": 1.0e-9, "energy_change": 1.0e-9},
        "expected_failure": {
            "witness": witness,
            "energy_only_passes": energy_only_passes,
            "dual_criterion_rejects": dual_rejects,
            "detected": energy_only_passes and dual_rejects,
        },
    }


def _tc04() -> dict[str, Any]:
    alphas = [0.10, 0.25, 0.40, 0.60, 1.00]
    first = scf_scan_record(alphas, max_iter=80)
    second = scf_scan_record(alphas, max_iter=80)
    first_hash = canonical_sha256(first)
    second_hash = canonical_sha256(second)
    require(first_hash == second_hash, "T-C04 canonical JSON is not deterministic")
    for run in first["runs"]:
        for key in ("converged", "iterations", "final_residual", "termination_reason"):
            require(key in run, f"T-C04 missing run field: {key}")
    failure = run_nonlinear_scf(
        1.0, 20, 1.0e-9, 1.0e-9, force_all_steps=False
    )
    require(not failure["converged"], "T-C04 max iteration run converged")
    require(
        failure["termination_reason"] == "max_iterations",
        "T-C04 wrong failure reason",
    )
    return {
        "status": "pass",
        "model_parameters": {"alphas": alphas, "max_iter": 80},
        "metrics": {
            "canonical_sha256_first": first_hash,
            "canonical_sha256_second": second_hash,
            "runs": first["runs"],
        },
        "tolerances": {"hash_match": "exact"},
        "expected_failure": {
            "alpha": 1.0,
            "max_iter": 20,
            "converged": failure["converged"],
            "termination_reason": failure["termination_reason"],
            "detected": (
                not failure["converged"]
                and failure["termination_reason"] == "max_iterations"
            ),
        },
    }


def _tc05() -> dict[str, Any]:
    case = convergence_sequences()
    positive_error = np.asarray(case["positive_reference_errors"])
    positive_delta = np.asarray(case["positive_adjacent_differences"])
    negative_error = np.asarray(case["negative_reference_errors"])
    negative_delta = np.asarray(case["negative_adjacent_differences"])
    require(np.all(positive_error[-3:] < 1.0e-2), "T-C05 three levels failed")
    require(positive_error[-1] < 1.0e-3, "T-C05 final reference error failed")
    require(np.all(positive_delta[-2:] < 1.0e-2), "T-C05 adjacent deltas failed")
    single_pair_passes = negative_delta[2] < 1.0e-3
    multi_level_rejects = negative_error[-1] > 5.0e-3
    require(single_pair_passes and multi_level_rejects, "T-C05 failure not captured")
    return {
        "status": "pass",
        "model_parameters": {
            "reference": 1.0,
            "resolution": case["resolution"],
            "positive": case["positive"],
            "negative": case["negative"],
        },
        "metrics": case,
        "tolerances": {
            "last_three_reference": 1.0e-2,
            "final_reference": 1.0e-3,
            "last_two_adjacent": 1.0e-2,
        },
        "expected_failure": {
            "single_pair_passes": single_pair_passes,
            "final_reference_error": float(negative_error[-1]),
            "multi_level_rejects": multi_level_rejects,
            "detected": single_pair_passes and multi_level_rejects,
        },
    }


def _tc06() -> dict[str, Any]:
    case = sampling_case()
    sampling_errors = np.asarray(case["sampling_errors"])
    total_errors = np.asarray(case["biased_total_errors"])
    require(np.all(sampling_errors[-3:] < 1.0e-12), "T-C06 sampling failed")
    sampling_pair_passes = case["last_sampling_difference"] < 1.0e-12
    total_rejects = total_errors[-1] > 5.0e-3
    require(sampling_pair_passes and total_rejects, "T-C06 failure not captured")
    return {
        "status": "pass",
        "model_parameters": {
            "function": "exp(cos(k))",
            "sizes": case["sizes"],
            "reference_formula": "scipy.special.iv(0,1)",
            "basis_bias": case["basis_bias"],
        },
        "metrics": case,
        "tolerances": {"sampling": 1.0e-12, "total_failure": 5.0e-3},
        "expected_failure": {
            "sampling_pair_passes": sampling_pair_passes,
            "final_total_error": float(total_errors[-1]),
            "basis_axis_detected": total_rejects,
            "detected": sampling_pair_passes and total_rejects,
        },
    }


def _tc07() -> dict[str, Any]:
    case = generalized_overlap_case()
    require(case["spectrum_max_difference"] < 1.0e-11, "T-C07 spectrum failed")
    require(
        case["maximum_normalized_residual"] < 1.0e-12,
        "T-C07 residual failed",
    )
    require(case["minimum_overlap_eigenvalue"] > 0.0, "T-C07 S not positive")
    rejected = case["overlap_ignored_max_difference"] > 1.0e-1
    require(rejected, "T-C07 overlap failure was not detected")
    return {
        "status": "pass",
        "model_parameters": {
            "S_diagonal": [1.0, 2.0, 1.5, 2.3],
            "H_diagonal": [-1.2, -0.2, 1.2, 4.6],
            "transform": "frozen_complex_upper_triangular",
        },
        "metrics": case,
        "tolerances": {
            "spectrum": 1.0e-11,
            "normalized_residual": 1.0e-12,
        },
        "expected_failure": {
            "kind": "overlap_ignored",
            "difference": case["overlap_ignored_max_difference"],
            "threshold": 1.0e-1,
            "detected": rejected,
        },
    }


def _tc08(seed: int, model_size: int) -> dict[str, Any]:
    require(model_size >= 12, "model_size must be at least 12")
    case = projection_case(seed, model_size)
    require(case["orthogonality_fro"] < 1.0e-12, "T-C08 B not orthonormal")
    require(case["idempotent_residual"] < 1.0e-12, "T-C08 return failed")
    require(case["relative_lost_norm"] > 0.9, "T-C08 lost norm too small")
    require(case["spectral_difference"] < 1.0e-12, "T-C08 spectrum changed")
    rejected = case["matrix_difference"] > 0.15
    require(rejected, "T-C08 matrix-label failure not detected")
    return {
        "status": "pass",
        "model_parameters": {
            "seed": seed,
            "dimension": model_size,
            "spectrum": "linspace(-3,3,d)",
            "rotation_angle": 0.37,
            "rotation_plane": [0, 1],
        },
        "metrics": case,
        "tolerances": {
            "orthogonality": 1.0e-12,
            "idempotent": 1.0e-12,
            "lost_norm_minimum": 0.9,
        },
        "expected_failure": {
            "kind": "equal_spectrum_does_not_imply_equal_matrix",
            "spectral_difference": case["spectral_difference"],
            "matrix_difference": case["matrix_difference"],
            "matrix_difference_threshold": 0.15,
            "detected": rejected,
        },
    }


def _tc09(seed: int) -> dict[str, Any]:
    record = synthetic_label_record(seed)
    validate_label_record(record)
    failures = missing_path_failures(record)
    require(len(failures) == len(REQUIRED_PATHS), "T-C09 deletion count mismatch")
    witnesses = schema_failure_witnesses(record)
    expected_counts = {
        category: sum(
            mutation_category == category
            for mutation_category, _, _ in SCHEMA_NEGATIVE_MUTATIONS
        )
        for category in ("type", "shape", "hash", "m8_choice")
    }
    captured_counts = {
        category: sum(witness["category"] == category for witness in witnesses)
        for category in expected_counts
    }
    require(
        captured_counts == expected_counts,
        "T-C09 schema failure matrix was not fully captured",
    )
    return {
        "status": "pass",
        "model_parameters": {
            "schema_version": "stageC-label-v1",
            "generation_status": "SYNTHETIC_M5",
        },
        "metrics": {
            "required_path_count": len(REQUIRED_PATHS),
            "schema_negative_case_count": len(SCHEMA_NEGATIVE_MUTATIONS),
            "record_sha256": canonical_sha256(record),
            "complete_record_valid": True,
        },
        "tolerances": {
            "all_required_paths_deleted_once": len(REQUIRED_PATHS),
            "all_schema_negative_cases_rejected": len(SCHEMA_NEGATIVE_MUTATIONS),
        },
        "expected_failure": {
            "kind": "required_path_deletions_and_schema_negative_matrix",
            "path_deletions": {
                "captured_count": len(failures),
                "missing_paths": failures,
            },
            "schema_negative_matrix": {
                "expected_counts": expected_counts,
                "captured_counts": captured_counts,
                "witnesses": witnesses,
            },
            "detected": (
                len(failures) == len(REQUIRED_PATHS)
                and captured_counts == expected_counts
            ),
        },
    }


def _tc10(grid_size: int) -> dict[str, Any]:
    case = locality_case(grid_size)
    index = np.arange(grid_size)
    distance = np.abs(index[:, None] - index[None, :])
    matrices = {
        "exponential": np.exp(-distance / 2.0),
        "algebraic": 1.0 / (1.0 + distance),
    }
    maximum_recompute_difference = 0.0
    for name, records in case["records"].items():
        matrix = matrices[name]
        action = matrix @ np.ones(grid_size) / grid_size
        for record in records:
            cutoff = record["cutoff"]
            truncated = matrix * (distance <= cutoff)
            recomputed = {
                "nonzero_fraction": np.count_nonzero(truncated) / truncated.size,
                "relative_frobenius_error": (
                    np.linalg.norm(matrix - truncated, ord="fro")
                    / np.linalg.norm(matrix, ord="fro")
                ),
                "relative_action_error": (
                    np.linalg.norm(
                        action - truncated @ np.ones(grid_size) / grid_size
                    )
                    / np.linalg.norm(action)
                ),
            }
            for key, value in recomputed.items():
                maximum_recompute_difference = max(
                    maximum_recompute_difference,
                    abs(float(record[key]) - float(value)),
                )
    require(
        maximum_recompute_difference < 1.0e-14,
        "T-C10 stored metric failed recomputation",
    )
    require(
        abs(case["exponential_fit_slope"] + 0.5) < 1.0e-12,
        "T-C10 exponential slope failed",
    )
    rejected = case["algebraic_extrapolation_relative_error"] > 0.8
    require(rejected, "T-C10 algebraic tail failure was not detected")
    return {
        "status": "pass",
        "model_parameters": {
            "grid_size": grid_size,
            "distance": "abs(i-j)",
            "families": ["exp(-R/2)", "1/(1+R)"],
            "cutoffs": [2, 4, 8, 16],
        },
        "metrics": {
            **case,
            "maximum_recomputed_metric_difference": maximum_recompute_difference,
        },
        "tolerances": {
            "recomputed_metric": 1.0e-14,
            "exponential_slope": 1.0e-12,
        },
        "expected_failure": {
            "kind": "short_exponential_fit_on_algebraic_tail",
            "relative_extrapolation_error": case[
                "algebraic_extrapolation_relative_error"
            ],
            "threshold": 0.8,
            "detected": rejected,
        },
    }


def run_suite(seed: int, model_size: int, grid_size: int) -> dict[str, Any]:
    require(model_size >= 12, "model_size must be at least 12")
    require(grid_size >= 48, "grid_size must be at least 48")
    tests = {
        "T-C01": _tc01(),
        "T-C02": _tc02(),
        "T-C03": _tc03(),
        "T-C04": _tc04(),
        "T-C05": _tc05(),
        "T-C06": _tc06(),
        "T-C07": _tc07(),
        "T-C08": _tc08(seed, model_size),
        "T-C09": _tc09(seed),
        "T-C10": _tc10(grid_size),
    }
    overall_pass = all(test["status"] == "pass" for test in tests.values())
    require(overall_pass, "stage C suite did not pass")
    return {
        "conventions_version": CONVENTIONS_VERSION,
        "backend": BACKEND,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "seed": seed,
        "model_size": model_size,
        "grid_size": grid_size,
        "tests": tests,
        "overall_pass": overall_pass,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json"], default="json")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--model-size", type=int, default=DEFAULT_MODEL_SIZE)
    parser.add_argument("--grid-size", type=int, default=DEFAULT_GRID_SIZE)
    arguments = parser.parse_args()
    result = run_suite(arguments.seed, arguments.model_size, arguments.grid_size)
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
            default=json_default,
        )
    )


if __name__ == "__main__":
    main()
