from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys
import unittest

import numpy as np

from run_experiments import CONFIGS, run_suite
from staged_models import (
    COND_LIMIT,
    SCHEMA_VERSION,
    build_periodic_graph,
    canonical_edge_payload,
    edge_instance_id,
    make_orbital_provenance,
    validate_cell,
    validate_cutoff,
    validate_graph,
    validate_orbital_provenance,
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def fixture_graph() -> dict[str, object]:
    return build_periodic_graph(
        np.asarray([[2.0, 0.0, 0.0], [0.3, 1.8, 0.0], [0.1, 0.2, 1.7]]),
        np.asarray([[0.05, 0.10, 0.15], [0.80, 0.70, 0.60]]),
        1.35,
        "unit-fixture",
    )


class StageDAcceptanceTests(unittest.TestCase):
    def test_both_frozen_configurations_pass_all_ten_gates(self) -> None:
        for config_name in ("A", "B"):
            with self.subTest(config=config_name):
                result = run_suite(config_name)
                self.assertTrue(result["overall_pass"])
                self.assertEqual(result["seed"], CONFIGS[config_name]["seed"])
                self.assertEqual(result["conventions_version"], SCHEMA_VERSION)
                self.assertEqual(
                    list(result["tests"]),
                    [f"T-D{index:02d}" for index in range(1, 11)],
                )
                self.assertTrue(all(test["pass"] for test in result["tests"].values()))

    def test_canonical_json_is_byte_deterministic(self) -> None:
        for config_name in ("A", "B"):
            with self.subTest(config=config_name):
                self.assertEqual(
                    canonical_bytes(run_suite(config_name)),
                    canonical_bytes(run_suite(config_name)),
                )

    def test_canonical_edge_identity_is_frozen(self) -> None:
        self.assertEqual(
            canonical_edge_payload("fixture", 1, 2, [0, -1, 3]),
            '["stageD-edge-v1","fixture",1,2,0,-1,3]',
        )
        self.assertEqual(
            edge_instance_id("fixture", 1, 2, [0, -1, 3]),
            "3b88233a229375fef60c1f1bb00349ae4913d2672eeedd9b2b4a739b665e2a96",
        )

    def test_graph_and_provenance_versions_are_enforced(self) -> None:
        graph = fixture_graph()
        provenance = make_orbital_provenance(graph, 4)
        wrong_graph = copy.deepcopy(graph)
        wrong_graph["schema_version"] = "wrong-version"
        with self.assertRaisesRegex(ValueError, "graph schema_version"):
            validate_graph(wrong_graph)
        wrong_provenance = copy.deepcopy(provenance)
        wrong_provenance["schema_version"] = "wrong-version"
        with self.assertRaisesRegex(ValueError, "orbital-provenance schema_version"):
            validate_orbital_provenance(graph, wrong_provenance)

    def test_cutoff_rejects_nonfinite_and_nonpositive_values(self) -> None:
        for value in (np.nan, np.inf, -np.inf, 0.0, -1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_cutoff(value)
        self.assertEqual(validate_cutoff(1.25), 1.25)

    def test_cell_condition_boundary_is_asymmetric(self) -> None:
        accepted = validate_cell(np.diag([1.0, 1.0, 2.0e-8]))[1]
        self.assertLess(accepted, COND_LIMIT)
        for scale in (1.0e-8, 5.0e-9):
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                validate_cell(np.diag([1.0, 1.0, scale]))

    def test_failure_matrix_includes_schema_mask_padding_and_cache(self) -> None:
        result = run_suite("A")["tests"]["T-D09"]
        names = {item["name"] for item in result["captured_failures"]}
        self.assertEqual(result["expected_failure_count"], 36)
        self.assertEqual(len(names), 36)
        self.assertTrue(
            {
                "wrong_mask_dtype",
                "wrong_mask_shape",
                "padding_mask_active",
                "padding_endpoint_leak",
                "missing_intermediate_tensor",
                "wrong_graph_schema_version",
                "negative_graph_id",
                "wrong_graph_count",
                "batch_provenance_row_mismatch",
                "noncontiguous_edge_padding",
                "missing_padded_shift",
                "edge_output_extra_component_row",
                "edge_output_missing_component_row",
                "concat_displacement_row_roll",
                "concat_distance_row_roll",
                "concat_edge_feature_row_roll",
                "padded_displacement_row_roll",
                "padded_distance_row_roll",
                "padded_edge_feature_row_roll",
                "padded_prediction_width_extra",
                "padded_prediction_width_missing",
                "concat_cutoff_too_small",
                "padded_cutoff_too_small",
                "concat_singular_cell",
                "padded_singular_cell",
                "concat_noncanonical_fractional",
                "padded_rank4_node_features",
            }.issubset(names)
        )
        self.assertTrue(result["empty_incoming_zero_aggregate"])
        self.assertTrue(result["empty_aggregation_contract"])
        self.assertTrue(result["intermediate_tensor_schema_validated"])
        self.assertLessEqual(result["padded_prediction_max_abs_residual"], 1.0e-12)
        self.assertGreater(result["padded_nan_sentinel_count"], 0)
        self.assertTrue(all(loss <= 1.0e-24 for loss in result["padded_masked_losses"]))

    def test_all_required_gradient_faults_are_executed_and_detected(self) -> None:
        result = run_suite("A")["tests"]["T-D02"]
        faults = result["fault_matrix"]
        self.assertEqual(
            set(faults),
            {
                "omit_loss_average",
                "scatter_to_sender",
                "wrong_tanh_derivative",
                "padding_gradient_leak",
                "output_sign_flip",
            },
        )
        self.assertTrue(all(fault["detected"] for fault in faults.values()))
        self.assertLessEqual(result["max_relative_error"], result["threshold"])
        self.assertEqual(result["padding_gradient_max_abs"], 0.0)

    def test_grouped_generator_and_frozen_mpnn_evaluation_are_exposed(self) -> None:
        for config_name in ("A", "B"):
            with self.subTest(config=config_name):
                result = run_suite(config_name)["tests"]["T-D03"]
                self.assertEqual(
                    result["generator"]["formula"],
                    "x=[u_g,tau_t]+xi; y=1.5*u_g-0.7*tau_t+b_g+epsilon",
                )
                self.assertEqual(result["group_intersections"], [[], [], []])
                self.assertGreater(len(result["trajectory"]), 2)
                self.assertEqual(result["trajectory"][0]["step"], 0)
                self.assertEqual(result["trajectory"][-1]["step"], CONFIGS[config_name]["training_steps"])
                self.assertLess(result["final_train_mse"], result["initial_train_mse"])
                self.assertLessEqual(result["test_mse"], result["test_mse_threshold"])
                self.assertLess(result["test_mse"], 0.25 * result["test_zero_baseline_mse"])
                self.assertGreater(result["corrupted_test_mse"], result["test_mse_threshold"])
                self.assertLess(result["frame_split_apparent_mse"], result["independent_group_linear_mse"])
                self.assertEqual(result["architecture"]["layers"], CONFIGS[config_name]["layers"])
                self.assertEqual(result["architecture"]["hidden_dim"], CONFIGS[config_name]["hidden_dim"])

    def test_complete_edge_output_mapping_and_representative_bijection(self) -> None:
        result = run_suite("A")["tests"]
        self.assertTrue(result["T-D04"]["provenance_mapping_pass"])
        self.assertLessEqual(result["T-D04"]["edge_max_abs_residual"], 1.0e-12)
        self.assertGreater(result["T-D04"]["prediction_row_mismatch_residual"], 1.0e-6)
        self.assertEqual(result["T-D04"]["captured_provenance_failure"]["name"], "misaligned_mask_row")
        self.assertTrue(result["T-D05"]["complete_key_bijection_pass"])
        self.assertGreater(result["T-D05"]["row_order_mismatch_residual"], 1.0e-6)

    def test_hard_validation_matrix_executes_group_and_schema_failures(self) -> None:
        result = run_suite("A")["tests"]["T-D10"]
        names = {item["name"] for item in result["captured_failures"]}
        self.assertEqual(result["expected_failure_count"], 16)
        self.assertEqual(len(names), 16)
        self.assertTrue(
            {
                "structure_group_pollution",
                "empty_structure_id",
                "float32_core_schema",
                "inconsistent_bounds",
                "inconsistent_candidate_count",
            }.issubset(names)
        )
        self.assertTrue(result["group_pollution_captured"])

    def test_cli_subprocess_is_byte_deterministic_and_rejects_wrong_seed(self) -> None:
        script = pathlib.Path(__file__).with_name("run_experiments.py")
        for config_name in ("A", "B"):
            seed = str(CONFIGS[config_name]["seed"])
            command = [sys.executable, str(script), "--format", "json", "--config", config_name, "--seed", seed]
            first = subprocess.run(command, check=True, capture_output=True).stdout
            second = subprocess.run(command, check=True, capture_output=True).stdout
            self.assertEqual(first, second)
            self.assertTrue(json.loads(first)["overall_pass"])
        rejected = subprocess.run(
            [sys.executable, str(script), "--format", "json", "--config", "A", "--seed", "0"],
            capture_output=True,
        )
        self.assertEqual(rejected.returncode, 2)

    def test_authorization_boundary_remains_unresolved_until_m8(self) -> None:
        boundary = run_suite("A")["authorization_boundary"]
        self.assertFalse(boundary["deeph_installed"])
        self.assertFalse(boundary["formal_data_downloaded"])
        self.assertFalse(boundary["dft_labels_generated"])
        self.assertEqual(boundary["material_system"], "UNRESOLVED_M8")
        self.assertEqual(boundary["dft_backend"], "UNRESOLVED_M8")
        self.assertEqual(boundary["deeph_software_object"], "UNRESOLVED_M8")


if __name__ == "__main__":
    unittest.main()
