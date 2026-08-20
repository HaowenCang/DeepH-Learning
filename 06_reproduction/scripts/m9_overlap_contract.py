#!/usr/bin/env python3
"""Strictly validate one state-bound overlap-only OpenMX output."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import re

import h5py
import numpy as np

from m9_overlap_common import (
    expected_structure_ids,
    file_sha256,
    load_contract,
    load_json,
    runtime_path,
    verify_frozen_project_files,
)


def parse_key(text: str) -> tuple[int, int, int, int, int]:
    value = json.loads(text)
    if not isinstance(value, list) or len(value) != 5:
        raise ValueError(f"invalid matrix key: {text!r}")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise ValueError(f"matrix key is not five integers: {text!r}")
    key = tuple(value)
    if not (1 <= key[3] <= 72 and 1 <= key[4] <= 72):
        raise ValueError(f"matrix atom index is outside 1..72: {text!r}")
    return key  # type: ignore[return-value]


def load_hdf5(path: Path) -> dict[tuple[int, int, int, int, int], np.ndarray]:
    matrices: dict[tuple[int, int, int, int, int], np.ndarray] = {}
    with h5py.File(path, "r") as handle:
        def reject_nested(name: str, obj: h5py.Dataset | h5py.Group) -> None:
            if "/" in name or not isinstance(obj, h5py.Dataset):
                raise ValueError(f"nested group or non-dataset HDF5 object: {name!r}")

        handle.visititems(reject_nested)
        for key_text, dataset in handle.items():
            if not isinstance(dataset, h5py.Dataset):
                raise ValueError(f"top-level HDF5 object is not a dataset: {key_text!r}")
            key = parse_key(key_text)
            if key in matrices:
                raise ValueError(f"duplicate normalized key: {key}")
            matrix = np.asarray(dataset[...])
            if matrix.shape != (13, 13) or matrix.dtype != np.float64:
                raise ValueError(
                    f"{key_text}: expected float64 (13,13), got {matrix.dtype} {matrix.shape}"
                )
            if not np.isfinite(matrix).all():
                raise ValueError(f"{key_text}: non-finite overlap value")
            matrices[key] = matrix
    if not matrices:
        raise ValueError("overlap HDF5 contains no matrices")
    return matrices


def load_expected_keys(path: Path) -> set[tuple[int, int, int, int, int]]:
    with np.load(path, allow_pickle=False) as archive:
        return {parse_key(key_text) for key_text in archive.files}


def max_reverse_residual(
    matrices: dict[tuple[int, int, int, int, int], np.ndarray]
) -> float:
    residual = 0.0
    for key, value in matrices.items():
        reverse = (-key[0], -key[1], -key[2], key[4], key[3])
        if reverse not in matrices:
            raise ValueError(f"missing reverse overlap key for {key}: {reverse}")
        residual = max(residual, float(np.max(np.abs(value - matrices[reverse].T))))
    return residual


def validate_onsite_blocks(
    matrices: dict[tuple[int, int, int, int, int], np.ndarray], tolerance: float
) -> tuple[float, float]:
    max_symmetry_residual = 0.0
    min_eigenvalue = math.inf
    for atom_index in range(1, 73):
        key = (0, 0, 0, atom_index, atom_index)
        if key not in matrices:
            raise ValueError(f"missing onsite overlap block for atom {atom_index}")
        onsite = matrices[key]
        residual = float(np.max(np.abs(onsite - onsite.T)))
        if residual > tolerance:
            raise ValueError(
                f"atom-{atom_index} onsite symmetry residual {residual} > {tolerance}"
            )
        minimum = float(np.linalg.eigvalsh((onsite + onsite.T) / 2.0).min())
        if not math.isfinite(minimum) or minimum <= 0.0:
            raise ValueError(f"atom-{atom_index} onsite overlap block is not positive definite")
        max_symmetry_residual = max(max_symmetry_residual, residual)
        min_eigenvalue = min(min_eigenvalue, minimum)
    return max_symmetry_residual, min_eigenvalue


def max_abs_difference(path_a: Path, path_b: Path) -> float:
    a = np.loadtxt(path_a, dtype=np.float64, ndmin=1)
    b = np.loadtxt(path_b, dtype=np.float64, ndmin=1)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {path_a.name} {a.shape} != {path_b.name} {b.shape}")
    return float(np.max(np.abs(a - b))) if a.size else 0.0


def expected_command(contract: dict[str, object]) -> list[str]:
    execution = contract["execution"]
    assert isinstance(execution, dict)
    return [
        str(item)
        .replace("${OPENMX_BINARY}", runtime_path(contract, "openmx_binary").as_posix())
        .replace("${HDF5_PREFIX}", runtime_path(contract, "hdf5_prefix").as_posix())
        for item in execution["argv"]
    ]


def validate_allowlist(run_dir: Path, contract: dict[str, object]) -> list[str]:
    output_contract = contract["output_contract"]
    assert isinstance(output_contract, dict)
    actual: list[str] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in run directory: {path}")
        if path.is_file():
            actual.append(path.relative_to(run_dir).as_posix())
    allowed = sorted(str(item) for item in output_contract["run_file_allowlist_before_report"])
    if actual != allowed:
        missing = sorted(set(allowed) - set(actual))
        extra = sorted(set(actual) - set(allowed))
        raise ValueError(f"strict run allowlist mismatch: missing={missing}, extra={extra}")
    forbidden_tokens = [str(item).casefold() for item in output_contract["forbidden_filename_tokens_casefold"]]
    for relative in actual:
        folded = relative.casefold()
        if any(token in folded for token in forbidden_tokens):
            raise ValueError(f"forbidden DFT-output filename token: {relative}")
        suffix = Path(relative).suffix.casefold()
        if suffix in {".h5", ".hdf5", ".hdf", ".he5"} and relative not in {
            "output/overlaps_0.h5",
            "parsed/overlaps.h5",
        }:
            raise ValueError(f"additional HDF5-like output forbidden: {relative}")
    return actual


def validate_preparse_outputs(run_dir: Path, contract: dict[str, object]) -> list[str]:
    output_contract = contract["output_contract"]
    assert isinstance(output_contract, dict)
    actual: list[str] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in run directory: {path}")
        if path.is_file():
            actual.append(path.relative_to(run_dir).as_posix())
    expected = sorted(str(item) for item in output_contract["run_file_allowlist_before_parser"])
    if actual != expected:
        raise ValueError(f"pre-parser output allowlist mismatch: actual={actual}")
    validate_logs(run_dir, contract)
    return actual


def validate_logs(run_dir: Path, contract: dict[str, object]) -> dict[str, str]:
    output_contract = contract["output_contract"]
    assert isinstance(output_contract, dict)
    stdout = (run_dir / "openmx.std").read_text(encoding="utf-8", errors="strict")
    stderr = (run_dir / "openmx.err").read_text(encoding="utf-8", errors="strict")
    merged = (run_dir / "openmx.out").read_text(encoding="utf-8", errors="strict")
    for marker in output_contract["required_stdout_markers"]:
        if str(marker) not in stdout:
            raise ValueError(f"missing normal overlap-only stdout marker: {marker}")
    combined_folded = "\n".join((stdout, stderr, merged)).casefold()
    for marker in output_contract["forbidden_log_markers_casefold"]:
        if str(marker).casefold() in combined_folded:
            raise ValueError(f"forbidden special/SCF log marker: {marker}")
    if stderr.strip():
        raise ValueError("overlap-only stderr is not empty")
    return {
        "openmx.std": file_sha256(run_dir / "openmx.std"),
        "openmx.err": file_sha256(run_dir / "openmx.err"),
        "openmx.out": file_sha256(run_dir / "openmx.out"),
    }


def validate_receipt(
    run_dir: Path,
    source: Path,
    contract: dict[str, object],
    contract_hash: str,
) -> dict[str, object]:
    receipt = load_json(run_dir / "execution_receipt.json", "m9-overlap-execution-receipt-v1")
    mapping = load_json(run_dir / "structure_mapping.json", "m9-openmx-structure-mapping-v1")
    build_manifest_path = runtime_path(contract, "build_manifest")
    binary = runtime_path(contract, "openmx_binary")
    required = {
        "structure_id": source.name,
        "contract_sha256": contract_hash,
        "build_manifest_sha256": file_sha256(build_manifest_path),
        "binary_sha256": file_sha256(binary),
        "overlap_tree_manifest_sha256": file_sha256(
            runtime_path(contract, "overlap_tree_manifest")
        ),
        "input_sha256": file_sha256(run_dir / "openmx.dat"),
        "mapping_sha256": file_sha256(run_dir / "structure_mapping.json"),
        "argv": expected_command(contract),
        "mpi_ranks": 1,
        "openmp_threads": 1,
        "cpu_bucket": "overlap_smoke" if source.name == "500" else "overlap_batch",
        "budget_transaction_id": receipt.get("budget_transaction_id"),
        "exit_code": 0,
        "deeph_parser_commit": "66703c532a6f633f4bbc8f94f75c8698a7f89859",
        "stdout_sha256": file_sha256(run_dir / "openmx.std"),
        "stderr_sha256": file_sha256(run_dir / "openmx.err"),
        "merged_openmx_out_sha256": file_sha256(run_dir / "openmx.out"),
    }
    for field, expected in required.items():
        if receipt.get(field) != expected:
            raise ValueError(f"execution receipt mismatch for {field}: {receipt.get(field)!r}")
    if mapping.get("contract_sha256") != contract_hash:
        raise ValueError("mapping does not bind the frozen contract")
    if mapping.get("build_manifest_sha256") != required["build_manifest_sha256"]:
        raise ValueError("mapping does not bind the current build manifest")
    if mapping.get("openmx_input", {}).get("sha256") != required["input_sha256"]:
        raise ValueError("mapping does not bind the current OpenMX input")
    basis = contract["basis"]
    assert isinstance(basis, dict)
    if mapping.get("basis_sha256") != {
        "pao": basis["pao_sha256"],
        "vps": basis["vps_sha256"],
    }:
        raise ValueError("mapping does not bind the frozen PAO/VPS hashes")
    provenance = contract["dataset_provenance"]
    assert isinstance(provenance, dict)
    if mapping.get("dataset_inventory_sha256") != provenance["inventory_sha256"]:
        raise ValueError("mapping does not bind the frozen dataset inventory")
    if mapping.get("dataset_contract_sha256") != provenance["data_contract_sha256"]:
        raise ValueError("mapping does not bind the frozen dataset contract")
    source_hashes = mapping.get("source_sha256")
    if not isinstance(source_hashes, dict) or set(source_hashes) != {
        "element.dat",
        "info.json",
        "lat.dat",
        "orbital_types.dat",
        "rc.npz",
        "rh.npz",
        "rlat.dat",
        "site_positions.dat",
    }:
        raise ValueError("mapping does not bind all eight structure files")
    for name, expected in source_hashes.items():
        if file_sha256(source / name) != expected:
            raise ValueError(f"frozen structure file changed after input generation: {name}")
    exact_fields = {
        "schema_version",
        "structure_id",
        "contract_sha256",
        "build_manifest_sha256",
        "binary_sha256",
        "overlap_tree_manifest_sha256",
        "deeph_parser_commit",
        "input_sha256",
        "mapping_sha256",
        "argv",
        "mpi_ranks",
        "openmp_threads",
        "cpu_bucket",
        "budget_transaction_id",
        "forecast_bytes",
        "start_utc",
        "end_utc",
        "elapsed_seconds",
        "exit_code",
        "stdout_sha256",
        "stderr_sha256",
        "merged_openmx_out_sha256",
        "run_payload_increment_apparent_bytes",
        "run_payload_increment_allocated_bytes",
        "run_payload_vhdx_growth_bytes",
    }
    if set(receipt) != exact_fields:
        raise ValueError("execution receipt fields differ from the frozen schema")
    if not isinstance(receipt.get("budget_transaction_id"), str) or not re.fullmatch(
        r"[0-9a-f]{32}", str(receipt["budget_transaction_id"])
    ):
        raise ValueError("execution receipt has invalid budget transaction ID")
    for field in (
        "forecast_bytes",
        "run_payload_increment_apparent_bytes",
        "run_payload_increment_allocated_bytes",
        "run_payload_vhdx_growth_bytes",
    ):
        value = receipt.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"execution receipt has invalid non-negative field: {field}")
    elapsed = receipt.get("elapsed_seconds")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(
        elapsed
    ) or elapsed < 0:
        raise ValueError("execution receipt has invalid elapsed_seconds")
    try:
        start = dt.datetime.fromisoformat(str(receipt["start_utc"]).replace("Z", "+00:00"))
        end = dt.datetime.fromisoformat(str(receipt["end_utc"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("execution receipt timestamps are not ISO-8601") from exc
    if not str(receipt["start_utc"]).endswith("Z") or not str(receipt["end_utc"]).endswith("Z"):
        raise ValueError("execution receipt timestamps must be UTC Z values")
    if end < start:
        raise ValueError("execution receipt end precedes start")
    return receipt


def validate_structure(structure_id: str, contract: dict[str, object], contract_hash: str) -> dict[str, object]:
    if structure_id not in expected_structure_ids(contract):
        raise ValueError("structure ID is outside frozen set")
    verify_frozen_project_files(contract)
    source = runtime_path(contract, "processed_data") / structure_id
    run_dir = runtime_path(contract, "run_root") / structure_id
    parsed_dir = run_dir / "parsed"
    output_contract = contract["output_contract"]
    assert isinstance(output_contract, dict)

    files = validate_allowlist(run_dir, contract)
    logs = validate_logs(run_dir, contract)
    receipt = validate_receipt(run_dir, source, contract, contract_hash)
    raw_path = run_dir / str(output_contract["raw_relative_path"])
    raw = load_hdf5(raw_path)
    expected_keys = load_expected_keys(source / "rh.npz")
    if set(raw) != expected_keys:
        missing = sorted(expected_keys - set(raw))[:5]
        extra = sorted(set(raw) - expected_keys)[:5]
        raise ValueError(f"overlap/Hamiltonian key spaces differ: missing={missing}, extra={extra}")
    reverse_residual = max_reverse_residual(raw)
    reverse_tolerance = float(output_contract["reverse_absolute_tolerance"])
    if reverse_residual > reverse_tolerance:
        raise ValueError(f"reverse residual {reverse_residual} > {reverse_tolerance}")

    parsed_path = parsed_dir / str(output_contract["parsed_filename"])
    parsed = load_hdf5(parsed_path)
    if set(parsed) != set(raw):
        raise ValueError("parsed overlap keys differ from raw overlap keys")
    parsed_copy_residual = max(float(np.max(np.abs(raw[key] - parsed[key]))) for key in raw)
    if parsed_copy_residual != 0.0:
        raise ValueError(f"parsed overlap copy is not exact: {parsed_copy_residual}")

    coordinate_tolerance = float(output_contract["parsed_coordinate_absolute_tolerance_angstrom"])
    structure_residuals = {
        name: max_abs_difference(source / name, parsed_dir / name)
        for name in ("lat.dat", "rlat.dat", "site_positions.dat")
    }
    if max(structure_residuals.values()) > coordinate_tolerance:
        raise ValueError(f"parsed structure residual exceeds tolerance: {structure_residuals}")
    for name in ("element.dat", "orbital_types.dat"):
        source_array = np.loadtxt(source / name, dtype=np.int64)
        parsed_array = np.loadtxt(parsed_dir / name, dtype=np.int64)
        if not np.array_equal(source_array, parsed_array):
            raise ValueError(f"parsed {name} differs from frozen structure")

    onsite_tolerance = float(output_contract["onsite_symmetry_absolute_tolerance"])
    onsite_symmetry_residual, onsite_min_eigenvalue = validate_onsite_blocks(
        raw, onsite_tolerance
    )

    return {
        "schema_version": "m9-overlap-structure-report-v1",
        "structure_id": structure_id,
        "status": "PASS",
        "execution_receipt_sha256": file_sha256(run_dir / "execution_receipt.json"),
        "validated_files": files,
        "log_sha256": logs,
        "raw_overlap": {
            "path": raw_path.as_posix(),
            "bytes": raw_path.stat().st_size,
            "sha256": file_sha256(raw_path),
            "key_count": len(raw),
            "reverse_max_abs_residual": reverse_residual,
            "all_onsite_max_symmetry_residual": onsite_symmetry_residual,
            "all_onsite_min_eigenvalue": onsite_min_eigenvalue,
        },
        "parsed_overlap": {
            "path": parsed_path.as_posix(),
            "bytes": parsed_path.stat().st_size,
            "sha256": file_sha256(parsed_path),
            "copy_max_abs_residual": parsed_copy_residual,
        },
        "structure_max_abs_residuals": structure_residuals,
        "source_hamiltonian_key_count": len(expected_keys),
        "receipt_elapsed_seconds": receipt.get("elapsed_seconds"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-id", required=True)
    args = parser.parse_args()
    contract, contract_hash = load_contract()
    report = validate_structure(str(args.structure_id), contract, contract_hash)
    report_path = runtime_path(contract, "run_root") / str(args.structure_id) / "overlap_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
