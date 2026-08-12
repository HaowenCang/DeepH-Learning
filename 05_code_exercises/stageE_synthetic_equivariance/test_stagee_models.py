from __future__ import annotations

import copy
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import unittest
from unittest import mock

import numpy as np
import scipy

import run_experiments as experiments
from run_experiments import run_scan, run_suite
from stagee_models import (
    BATCH_VERSION,
    CG_DLMF_TABLE_SHA256,
    CONFIG_CASES,
    FILTER_VERSION,
    SCHEMA_VERSION,
    array_summary,
    canonical_json,
    cg_matrix,
    coefficient_bridge_payload_hash,
    coefficient_filter_payload_hash,
    edge_payload,
    frame_tolerance,
    make_config_case,
    make_hamiltonian_edge,
    make_irrep_batch,
    make_message_provenance,
    make_time_reversal_pair,
    masked_irrep_mse,
    message_layer,
    normalized_residual,
    padded_irrep_linear,
    reference_cost,
    time_reversal_payloads,
    tolerance,
    validate_case,
    validate_hamiltonian_edge,
    validate_irrep_batch,
    validate_message_provenance,
    validate_time_reversal_pair,
)


ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "run_experiments.py"


class StageEAcceptanceTests(unittest.TestCase):
    def assert_numeric_values_are_finite(self, value: object) -> None:
        if isinstance(value, float):
            self.assertTrue(math.isfinite(value))
        elif isinstance(value, dict):
            for item in value.values():
                self.assert_numeric_values_are_finite(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                self.assert_numeric_values_are_finite(item)

    def test_fixed_environment_and_requirements(self) -> None:
        self.assertEqual(sys.version_info[:3], (3, 12, 13))
        self.assertEqual(np.__version__, "2.3.5")
        self.assertEqual(scipy.__version__, "1.18.0")
        self.assertEqual(
            (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines(),
            ["numpy==2.3.5", "scipy==1.18.0"],
        )

    def test_both_frozen_configs_pass_all_twelve_gates(self) -> None:
        for config_id in ("A", "B"):
            with self.subTest(config=config_id):
                result = run_suite(config_id)
                self.assertTrue(result["overall_pass"])
                self.assertEqual(result["seed"], CONFIG_CASES[config_id]["seed"])
                self.assertEqual(result["schema_version"], SCHEMA_VERSION)
                self.assertEqual(list(result["tests"]), [f"T-E{index:02d}" for index in range(1, 13)])
                self.assertTrue(all(item["pass"] for item in result["tests"].values()))

    def test_complete_scan_has_all_144_unique_cases_and_frozen_anchors(self) -> None:
        scan = run_scan()
        self.assertTrue(scan["pass"])
        self.assertEqual(scan["case_count"], 144)
        case_ids = [item["case_id"] for item in scan["cases"]]
        self.assertEqual(len(set(case_ids)), 144)
        self.assertEqual(
            scan["anchors"],
            {
                "G_A": {
                    "mac_per_rotation": 168,
                    "aggregation_add_per_rotation": 52,
                    "array_bytes_total": 2728,
                    "array_bytes_peak": 2280,
                },
                "G_B": {
                    "mac_per_rotation": 378,
                    "aggregation_add_per_rotation": 143,
                    "array_bytes_total": 5584,
                    "array_bytes_peak": 4576,
                },
            },
        )
        self.assertLessEqual(scan["max_residual"], 5.0e-6)
        self.assertTrue(all(item["pass"] for item in scan["cases"]))
        self.assertTrue(
            all(
                item["threshold"] == (5.0e-12 if item["dtype"] == "float64" else 5.0e-6)
                and item["max_residual"] <= item["threshold"]
                and 0 <= item["worst_rotation"] < item["n_rotations"]
                and item["worst_ell"] in (0, 1, 2)
                for item in scan["cases"]
            )
        )

    def test_config_arrays_costs_and_rotations_match_schema(self) -> None:
        for config_id in ("A", "B"):
            case = make_config_case(config_id)
            validate_case(case)
            memory = array_summary(case)
            cost = reference_cost(case)
            self.assertEqual(case["rotations"].shape, (CONFIG_CASES[config_id]["n_rotations"], 3, 3))
            self.assertEqual(case["rotations"].dtype.name, CONFIG_CASES[config_id]["dtype"])
            self.assertEqual(set(memory["arrays"]), {
                "coordinates", "receiver", "sender", "shift", "rotations",
                "x_0", "x_1", "x_2", "W_0", "W_1", "W_2",
                "m_0", "m_1", "m_2", "h_0", "h_1", "h_2",
            })
            self.assertEqual(cost["flop_total"], 2 * cost["mac_total"])
            self.assertGreater(memory["array_bytes_total"], memory["array_bytes_peak"])

    def test_cli_config_and_scan_outputs_are_subprocess_byte_deterministic(self) -> None:
        commands = [
            [sys.executable, str(SCRIPT), "--config", "A", "--seed", "20260809"],
            [sys.executable, str(SCRIPT), "--config", "B", "--seed", "20260810"],
            [sys.executable, str(SCRIPT), "--scan"],
        ]
        for command in commands:
            with self.subTest(command=command):
                first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
                second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
                self.assertEqual(first, second)
                decoded = json.loads(first.decode("utf-8"))
                self.assertTrue(decoded["pass"] if "pass" in decoded else decoded["overall_pass"])
                self.assert_numeric_values_are_finite(decoded)

    def test_cli_rejects_mode_conflicts_and_wrong_seed(self) -> None:
        commands = [
            [sys.executable, str(SCRIPT), "--config", "A", "--seed", "20260810"],
            [sys.executable, str(SCRIPT), "--scan", "--seed", "20260809"],
            [sys.executable, str(SCRIPT), "--config", "A", "--scan"],
            [sys.executable, str(SCRIPT), "--scan", "--benchmark"],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=ROOT, capture_output=True)
                self.assertEqual(result.returncode, 2)

    def test_normative_payload_hashes_are_frozen(self) -> None:
        self.assertEqual(
            coefficient_bridge_payload_hash(1),
            "347e352605a3f4f3ccb078b6cedf5c755fdc6aa3527ea41a8ea3e93d076972a2",
        )
        self.assertEqual(
            coefficient_bridge_payload_hash(2),
            "5e783d9cdfe025238977f9e92d64d8b46e9a0e79eb8c9deba1af116aaafc7b82",
        )
        self.assertEqual(
            [coefficient_filter_payload_hash(ell) for ell in (0, 1, 2)],
            [
                "549a79b3656baa8736315f6d12f195013301c0fcdfe97bfdf3c73ecd85f58692",
                "55144adbd95056208733ab51ff2efb16789a95a855234641a4521c41fb577d06",
                "1a940f1cdcbc62b99ba56d6aa5e50619fb96c85fb0ddcc86913405cbaca97295",
            ],
        )
        self.assertEqual(
            {name: item["sha256"] for name, item in time_reversal_payloads().items()},
            {
                "spinless_real": "56342db661da6f8d9cc8c3bf6e241dcb9817f42e63a33cad9af9364bcc8df6ec",
                "spin_half": "f8b5e9591b791a2dbd9b262736718c8b391b75de6ce720335d1ad5b8f1aff444",
                "orbital_l1": "230aa31fc0201b4f2d7f8981a3244049c280f75cb2c753f38f9ce9d86a250980",
            },
        )

    def test_cg_tables_are_complete_and_partial_phase_is_detected(self) -> None:
        for pair, size in (((1, 1), 9), ((1, 2), 15)):
            matrix, outputs, inputs = cg_matrix(*pair)
            self.assertEqual(matrix.shape, (size, size))
            self.assertEqual(len(outputs), size)
            self.assertEqual(len(inputs), size)
            self.assertLess(np.linalg.norm(matrix @ matrix.T - np.eye(size)), 2.0e-15)
            self.assertLess(np.linalg.norm(matrix.T @ matrix - np.eye(size)), 2.0e-15)
        evidence = run_suite("A")["tests"]["T-E05"]
        self.assertEqual(evidence["canonical_table_sha256"], CG_DLMF_TABLE_SHA256)
        self.assertEqual(evidence["frozen_DLMF_table_sha256"], CG_DLMF_TABLE_SHA256)
        self.assertLessEqual(evidence["whole_channel_phase_intertwiner_residual"], 5.0e-12)
        self.assertGreater(evidence["fault_residuals"]["partial_M_phase"], 1.0e-4)
        self.assertGreater(evidence["fault_residuals"]["single_coefficient_orthogonality"], 1.0e-4)

    def test_frozen_directional_fault_oracles_are_executed(self) -> None:
        tests = run_suite("A")["tests"]
        self.assertEqual(len(tests["T-E01"]["captured_failures"]), 11)
        self.assertGreater(tests["T-E01"]["fault_residuals"]["wrong_composition_order"], 1.0e-4)
        self.assertEqual(tests["T-E03"]["captured_failures"][0]["name"], "stf_missing_normalization")
        self.assertGreater(tests["T-E04"]["fault_residuals"]["condon_shortley_local_phase"], 1.0e-4)
        self.assertEqual(tests["T-E04"]["captured_failures"][0]["name"], "euler_angles_used_as_rotation_matrix")
        self.assertGreater(tests["T-E05"]["fault_residuals"]["input_swap_without_exchange_phase"], 1.0e-4)
        self.assertLessEqual(tests["T-E08"]["inversion_residual"], tests["T-E08"]["threshold"])
        self.assertGreater(tests["T-E08"]["fault_residuals"]["wrong_output_parity"], 1.0e-4)
        self.assertEqual(
            {item["name"] for item in tests["T-E08"]["captured_failures"]},
            {
                "stale_direction_provenance", "direction_row_permutation", "wrong_cg_channel_metadata",
                "wrong_irrep_parity_metadata",
            },
        )

    def test_irrep_padding_is_cut_by_mask_and_active_nan_is_rejected(self) -> None:
        batch = make_irrep_batch(np.float64)
        validate_irrep_batch(batch)
        self.assertEqual(batch["schema_version"], BATCH_VERSION)
        self.assertTrue(np.isnan(batch["values"]["2"][~batch["component_mask"]["2"]]).all())
        mutated = copy.deepcopy(batch)
        mutated["component_mask"]["1"][0, 0, 0, 0] = False
        with self.assertRaises(ValueError):
            validate_irrep_batch(mutated)
        weights = {
            "0": np.eye(2, dtype=np.float64),
            "1": np.eye(2, dtype=np.float64),
            "2": np.eye(1, dtype=np.float64),
        }
        output = padded_irrep_linear(batch, weights)
        self.assertEqual(masked_irrep_mse(output, output, batch), 0.0)
        mutated = copy.deepcopy(batch)
        mutated["values"]["0"][0, 0, 0, 0] = np.nan
        with self.assertRaises(ValueError):
            validate_irrep_batch(mutated)

    def test_hamiltonian_and_message_provenance_reject_row_or_identity_drift(self) -> None:
        row = make_hamiltonian_edge(np.float64)
        validate_hamiltonian_edge(row)
        inverse_row = make_hamiltonian_edge(np.float64, reverse=True)
        validate_hamiltonian_edge(inverse_row)
        self.assertEqual((row["receiver"], row["sender"]), (inverse_row["sender"], inverse_row["receiver"]))
        self.assertTrue(np.array_equal(inverse_row["block"], row["block"].T))
        mutated = copy.deepcopy(row)
        mutated["sender_orbitals"] = list(reversed(mutated["sender_orbitals"]))
        with self.assertRaises(ValueError):
            validate_hamiltonian_edge(mutated)
        mutated = copy.deepcopy(row)
        mutated["edge_payload"] = "not-json-and-not-stageD-edge-v1"
        mutated["edge_id"] = hashlib.sha256(mutated["edge_payload"].encode("utf-8")).hexdigest()
        with self.assertRaises(ValueError):
            validate_hamiltonian_edge(mutated)
        case = make_config_case("A")
        graph = case["graph"]
        directions = graph["coordinates"][graph["sender"]] - graph["coordinates"][graph["receiver"]]
        provenance = make_message_provenance(graph, directions)
        self.assertEqual(provenance["schema_version"], FILTER_VERSION)
        self.assertEqual(provenance["input_irrep"], [1, -1])
        self.assertEqual(provenance["filter_irrep"], [1, -1])
        self.assertEqual(provenance["output_irreps_with_parity"], [[0, 1], [1, 1], [2, 1]])
        mutated_provenance = copy.deepcopy(provenance)
        mutated_provenance["receiver"] = np.roll(mutated_provenance["receiver"], 1)
        with self.assertRaises(ValueError):
            validate_message_provenance(graph, mutated_provenance)
        mutated_provenance = copy.deepcopy(provenance)
        mutated_provenance["output_irreps_with_parity"][2][1] = -1
        with self.assertRaises(ValueError):
            validate_message_provenance(graph, mutated_provenance)
        node_coefficients = np.ones((graph["coordinates"].shape[0], 3), dtype=np.complex128)
        message_layer(node_coefficients, graph, directions, provenance)
        with self.assertRaises(ValueError):
            message_layer(node_coefficients, graph, -directions, provenance)
        with self.assertRaises(ValueError):
            message_layer(node_coefficients, graph, np.roll(directions, 1, axis=0), provenance)

    def test_scan_enforces_each_dtype_threshold_and_rejects_nonfinite_residuals(self) -> None:
        def injected_residual(case: dict[str, object]) -> dict[str, object]:
            residual = 1.0e-6 if case["dtype"] == "float64" else 0.0
            return {"max_residual": residual, "worst": {"rotation": 0, "ell": 1}, "threshold": tolerance(case["dtype"])}

        try:
            experiments.run_scan.cache_clear()
            with mock.patch.object(experiments, "reference_equivariance", side_effect=injected_residual):
                result = experiments.run_scan()
            self.assertFalse(result["pass"])
            self.assertTrue(all(not item["pass"] for item in result["cases"] if item["dtype"] == "float64"))
            self.assertTrue(all(item["pass"] for item in result["cases"] if item["dtype"] == "float32"))
            self.assertTrue(all("threshold" in item and "worst_rotation" in item and "worst_ell" in item for item in result["cases"]))

            experiments.run_scan.cache_clear()
            with mock.patch.object(
                experiments,
                "reference_equivariance",
                side_effect=lambda case: {
                    "max_residual": tolerance(case["dtype"]),
                    "worst": {"rotation": 0, "ell": 0},
                    "threshold": tolerance(case["dtype"]),
                },
            ):
                self.assertTrue(experiments.run_scan()["pass"])

            experiments.run_scan.cache_clear()
            with mock.patch.object(
                experiments,
                "reference_equivariance",
                return_value={"max_residual": float("nan"), "worst": {"rotation": 0, "ell": 0}, "threshold": 5.0e-12},
            ):
                with self.assertRaises(ValueError):
                    experiments.run_scan()
        finally:
            experiments.run_scan.cache_clear()

    def test_time_reversal_uses_independent_h_and_s_partner_rows(self) -> None:
        pair = make_time_reversal_pair(np.float64)
        validate_time_reversal_pair(pair)
        self.assertFalse(np.shares_memory(pair["H_k"], pair["H_minus_k"]))
        self.assertFalse(np.shares_memory(pair["S_k"], pair["S_minus_k"]))
        mutated = copy.deepcopy(pair)
        mutated["minus_k_id"] = "wrong"
        with self.assertRaises(ValueError):
            validate_time_reversal_pair(mutated)
        evidence = run_suite("A")["tests"]["T-E11"]
        self.assertEqual(len(evidence["captured_failures"]), 6)
        self.assertEqual(evidence["pair_identity"]["partner_map"], [1, 0])
        self.assertTrue(evidence["general_k_is_not_trim"])
        self.assertLessEqual(evidence["trim_kramers_pair_gap"], evidence["threshold"])

    def test_failure_matrix_executes_all_63_rejections(self) -> None:
        for config_id in ("A", "B"):
            evidence = run_suite(config_id)["tests"]["T-E12"]
            self.assertEqual((evidence["rejected"], evidence["total"]), (63, 63))
            names = [item["name"] for item in evidence["captured_failures"]]
            self.assertEqual(len(set(names)), 63)
            self.assertTrue(all(item["error_type"] and item["message"] for item in evidence["captured_failures"]))
            self.assertEqual(evidence["padding_probe_max_active_residual"], 0.0)
            self.assertEqual(evidence["padding_probe_losses"], [0.0, 0.0, 0.0])
            self.assertTrue(
                {
                    "rotation_reflection",
                    "x_active_nan",
                    "W_dtype",
                    "partial_irrep_shell_mask",
                    "hamiltonian_orbital_order",
                    "filter_edge_row_mismatch",
                    "filter_stale_direction_provenance",
                    "filter_wrong_cg_channel",
                    "hamiltonian_forged_payload_rehash",
                    "time_pair_missing_conjugation",
                    "M8_material_selected",
                    "M8_backend_selected",
                    "M8_data_backend_selected",
                    "M8_software_selected",
                    "M8_budget_selected",
                    "M8_physics_selected",
                }.issubset(names)
            )

    def test_m8_boundaries_and_dependency_surface_remain_unresolved(self) -> None:
        for config_id in ("A", "B"):
            case = make_config_case(config_id)
            self.assertEqual(set(case["m8_boundary"].values()), {"UNRESOLVED_M8"})
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
        for forbidden in ("deeph", "e3nn", "pymatgen", "ase", "vasp", "abacus"):
            self.assertNotIn(forbidden, requirements)

    def test_canonical_edge_identity_and_summary_exclude_wall_time(self) -> None:
        payload = edge_payload("fixture", 1, 2, (0, -1, 3))
        self.assertEqual(payload, '["stageD-edge-v1","fixture",1,2,0,-1,3]')
        self.assertEqual(
            hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "3b88233a229375fef60c1f1bb00349ae4913d2672eeedd9b2b4a739b665e2a96",
        )
        result = run_suite("A")
        summary = canonical_json(result)
        self.assertNotIn("wall_time", summary)
        self.assertNotIn(str(ROOT), summary)
        self.assert_numeric_values_are_finite(result)

    def test_dtype_specific_thresholds_cover_float64_and_float32(self) -> None:
        self.assertEqual(tolerance(np.float64), 5.0e-12)
        self.assertEqual(tolerance(np.float32), 5.0e-6)
        self.assertEqual(frame_tolerance(np.float64), 1.0e-8)
        self.assertEqual(frame_tolerance(np.float32), 1.0e-4)
        for config_id in ("A", "B"):
            evidence = run_suite(config_id)["tests"]["T-E09"]
            self.assertTrue(evidence["pass"])
            self.assertGreater(evidence["fault_residuals"]["positive_negative_limit_jump"], 2.8)


if __name__ == "__main__":
    unittest.main()
