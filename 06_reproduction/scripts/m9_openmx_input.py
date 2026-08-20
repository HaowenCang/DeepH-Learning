#!/usr/bin/env python3
"""Generate one deterministic, state-gated overlap-only OpenMX input."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from m9_overlap_common import (
    atomic_json,
    expected_structure_ids,
    file_sha256,
    load_contract,
    load_workflow_state,
    require_budget_context,
    runtime_path,
    save_workflow_state,
    verify_frozen_project_files,
    workflow_lock,
)


EXPECTED_ORBITALS = np.asarray([0, 0, 1, 1, 2], dtype=np.int64)
SOURCE_FILES = (
    "element.dat",
    "info.json",
    "lat.dat",
    "orbital_types.dat",
    "rc.npz",
    "rh.npz",
    "rlat.dat",
    "site_positions.dat",
)


def frozen_source_hashes(source: Path, contract: dict[str, object]) -> dict[str, str]:
    """Return the eight independently frozen hashes for one structure."""
    provenance = contract["dataset_provenance"]
    assert isinstance(provenance, dict)
    inventory_path = runtime_path(contract, "dataset_inventory")
    data_contract_path = runtime_path(contract, "dataset_contract")
    if file_sha256(inventory_path) != provenance["inventory_sha256"]:
        raise ValueError("dataset inventory SHA-256 mismatch")
    if file_sha256(data_contract_path) != provenance["data_contract_sha256"]:
        raise ValueError("dataset contract SHA-256 mismatch")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if (
        inventory.get("schema_version") != provenance["inventory_schema"]
        or inventory.get("root") != runtime_path(contract, "processed_data").as_posix()
        or int(inventory.get("file_count", -1)) != int(provenance["inventory_file_count"])
        or int(inventory.get("total_bytes", -1)) != int(provenance["inventory_total_bytes"])
    ):
        raise ValueError("dataset inventory header differs from the frozen contract")
    data_contract = json.loads(data_contract_path.read_text(encoding="utf-8"))
    if (
        data_contract.get("schema_version") != provenance["data_contract_schema"]
        or data_contract.get("dataset_root") != runtime_path(contract, "processed_data").as_posix()
    ):
        raise ValueError("dataset contract header differs from the frozen contract")
    prefix = source.name + "/"
    selected: dict[str, str] = {}
    for entry in inventory.get("files", []):
        if not isinstance(entry, dict) or not str(entry.get("path", "")).startswith(prefix):
            continue
        name = str(entry["path"])[len(prefix) :]
        if name in selected:
            raise ValueError(f"duplicate dataset inventory entry: {source.name}/{name}")
        if name in SOURCE_FILES:
            selected[name] = str(entry.get("sha256", ""))
    if set(selected) != set(SOURCE_FILES) or any(len(value) != 64 for value in selected.values()):
        raise ValueError(f"{source.name}: frozen inventory lacks the exact eight files")
    for name, expected in selected.items():
        path = source / name
        if path.is_symlink() or not path.is_file() or file_sha256(path) != expected:
            raise ValueError(f"{source.name}: source file differs from frozen inventory: {name}")
    return selected


def require_budget_wrapper(bucket: str) -> None:
    action = "smoke_prepare" if bucket == "overlap_smoke" else "batch_prepare"
    require_budget_context(bucket, (action,))


def load_structure(source: Path, contract: dict[str, object]) -> dict[str, object]:
    members = list(source.iterdir())
    if any(path.is_symlink() for path in members):
        raise ValueError(f"{source.name}: symlinks are forbidden")
    actual_files = {path.name for path in members if path.is_file()}
    if actual_files != set(SOURCE_FILES) or any(path.is_dir() for path in members):
        raise ValueError(f"{source.name}: frozen eight-file structure contract changed")
    source_hashes = frozen_source_hashes(source, contract)
    info = json.loads((source / "info.json").read_text(encoding="utf-8"))
    if set(info) != {"nsites", "fermi_level", "isorthogonal", "isspinful", "norbits"}:
        raise ValueError(f"{source.name}: unexpected info.json keys")
    if (
        int(info["nsites"]) != 72
        or int(info["norbits"]) != 936
        or bool(info["isorthogonal"])
        or bool(info["isspinful"])
        or not np.isfinite(float(info["fermi_level"]))
    ):
        raise ValueError(f"{source.name}: info.json differs from frozen contract")

    elements = np.loadtxt(source / "element.dat", dtype=np.int64, ndmin=1)
    orbitals = np.loadtxt(source / "orbital_types.dat", dtype=np.int64, ndmin=2)
    stored_lattice = np.loadtxt(source / "lat.dat", dtype=np.float64, ndmin=2)
    reciprocal = np.loadtxt(source / "rlat.dat", dtype=np.float64, ndmin=2)
    stored_positions = np.loadtxt(source / "site_positions.dat", dtype=np.float64, ndmin=2)
    if elements.shape != (72,) or not np.all(elements == 6):
        raise ValueError(f"{source.name}: expected 72 carbon atoms")
    if orbitals.shape != (72, 5) or not np.all(orbitals == EXPECTED_ORBITALS):
        raise ValueError(f"{source.name}: orbital rows differ from [0,0,1,1,2]")
    if stored_lattice.shape != (3, 3) or reciprocal.shape != (3, 3):
        raise ValueError(f"{source.name}: lattice matrices must be 3x3")
    if stored_positions.shape != (3, 72):
        raise ValueError(f"{source.name}: site_positions.dat must be 3x72")
    if not all(np.isfinite(value).all() for value in (stored_lattice, reciprocal, stored_positions)):
        raise ValueError(f"{source.name}: non-finite structure array")
    lattice = stored_lattice.T
    cartesian = stored_positions.T
    determinant = float(np.linalg.det(lattice))
    if determinant <= 1e-12:
        raise ValueError(f"{source.name}: lattice is not right-handed and nonsingular")
    reciprocal_residual = float(
        np.max(np.abs(stored_lattice.T @ reciprocal - 2.0 * np.pi * np.eye(3)))
    )
    if reciprocal_residual > 1e-10:
        raise ValueError(f"{source.name}: reciprocal lattice mismatch")
    fractional = cartesian @ np.linalg.inv(lattice)
    mapping = contract["input_mapping"]
    assert isinstance(mapping, dict)
    tolerance = float(mapping["round_trip_absolute_tolerance_angstrom"])
    residual = float(np.max(np.abs(fractional @ lattice - cartesian)))
    if residual > tolerance:
        raise ValueError(f"{source.name}: coordinate round-trip {residual} > {tolerance}")
    if np.min(fractional) < -1e-12 or np.max(fractional) >= 1.0 + 1e-12:
        raise ValueError(f"{source.name}: fractional coordinates outside [0,1)")
    return {
        "lattice": lattice,
        "cartesian": cartesian,
        "fractional": fractional,
        "round_trip_residual_angstrom": residual,
        "reciprocal_residual": reciprocal_residual,
        "lattice_determinant_angstrom_cubed": determinant,
        "source_sha256": source_hashes,
    }


def verify_basis(contract: dict[str, object]) -> dict[str, str]:
    data_root = runtime_path(contract, "openmx_data")
    basis = contract["basis"]
    assert isinstance(basis, dict)
    paths = {
        "pao": data_root / "PAO/C6.0.pao",
        "vps": data_root / "VPS/C_PBE19.vps",
    }
    expected = {"pao": str(basis["pao_sha256"]), "vps": str(basis["vps_sha256"])}
    actual: dict[str, str] = {}
    for name, path in paths.items():
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"frozen basis file is missing: {path}")
        actual[name] = file_sha256(path)
        if actual[name] != expected[name]:
            raise ValueError(f"frozen {name.upper()} SHA-256 mismatch")
    return actual


def render_input(
    structure_id: str,
    data_path: Path,
    lattice: np.ndarray,
    fractional: np.ndarray,
    contract: dict[str, object],
) -> str:
    mapping = contract["input_mapping"]
    assert isinstance(mapping, dict)
    decimals = int(mapping["input_decimal_places"])
    if decimals != 16:
        raise ValueError("input_decimal_places must remain 16")
    lines = [
        "System.CurrentDirectory         ./",
        f"DATA.PATH                       {data_path.as_posix()}",
        f"System.Name                     graphene-{structure_id}-overlap-only",
        "level.of.stdout                1",
        "level.of.fileout               1",
        "Species.Number                 1",
        "<Definition.of.Atomic.Species",
        " C  C6.0-s2p2d1  C_PBE19",
        "Definition.of.Atomic.Species>",
        "Atoms.Number                   72",
        "Atoms.SpeciesAndCoordinates.Unit  FRAC",
        "<Atoms.SpeciesAndCoordinates",
    ]
    for index, coordinate in enumerate(fractional, start=1):
        lines.append(
            f" {index:3d} C {coordinate[0]:.{decimals}f} {coordinate[1]:.{decimals}f} "
            f"{coordinate[2]:.{decimals}f} 2.0 2.0"
        )
    lines.extend(
        [
            "Atoms.SpeciesAndCoordinates>",
            "Atoms.UnitVectors.Unit       Ang",
            "<Atoms.UnitVectors",
        ]
    )
    for vector in lattice:
        lines.append(
            f" {vector[0]:.{decimals}f} {vector[1]:.{decimals}f} {vector[2]:.{decimals}f}"
        )
    lines.extend(
        [
            "Atoms.UnitVectors>",
            "scf.XcType                    GGA-PBE",
            "scf.energycutoff              300.0",
            "scf.maxIter                   1000",
            "scf.EigenvalueSolver          Band",
            "scf.Kgrid                     1 1 1",
            "scf.SpinPolarization          Off",
            "scf.SpinOrbit.Coupling        Off",
            "MD.Type                       Nomd",
            "",
        ]
    )
    return "\n".join(lines)


def verify_rendered_input(
    text: str,
    structure_id: str,
    data_path: Path,
    source_cartesian: np.ndarray,
    contract: dict[str, object],
) -> dict[str, float]:
    lines = text.splitlines()
    required_exact = {
        f"DATA.PATH                       {data_path.as_posix()}",
        f"System.Name                     graphene-{structure_id}-overlap-only",
        "Atoms.SpeciesAndCoordinates.Unit  FRAC",
        "Atoms.UnitVectors.Unit       Ang",
        "scf.energycutoff              300.0",
        "scf.Kgrid                     1 1 1",
        "scf.SpinPolarization          Off",
        "scf.SpinOrbit.Coupling        Off",
        "MD.Type                       Nomd",
        " C  C6.0-s2p2d1  C_PBE19",
    }
    if not required_exact.issubset(set(lines)):
        raise ValueError("rendered input lacks a frozen exact field")
    start = lines.index("<Atoms.SpeciesAndCoordinates") + 1
    end = lines.index("Atoms.SpeciesAndCoordinates>")
    atom_lines = lines[start:end]
    if len(atom_lines) != 72:
        raise ValueError("rendered input does not contain 72 atoms")
    fractional = np.empty((72, 3), dtype=np.float64)
    for expected_index, line in enumerate(atom_lines, start=1):
        fields = line.split()
        if len(fields) != 7 or fields[0] != str(expected_index) or fields[1] != "C":
            raise ValueError("rendered input atom order/species changed")
        if fields[5:] != ["2.0", "2.0"]:
            raise ValueError("rendered input spin populations changed")
        fractional[expected_index - 1] = [float(value) for value in fields[2:5]]
    lattice_start = lines.index("<Atoms.UnitVectors") + 1
    lattice_end = lines.index("Atoms.UnitVectors>")
    lattice_lines = lines[lattice_start:lattice_end]
    if len(lattice_lines) != 3:
        raise ValueError("rendered input does not contain three lattice rows")
    lattice = np.asarray([[float(value) for value in line.split()] for line in lattice_lines])
    if lattice.shape != (3, 3):
        raise ValueError("rendered input lattice shape changed")
    residual = float(np.max(np.abs(fractional @ lattice - source_cartesian)))
    tolerance = float(contract["input_mapping"]["round_trip_absolute_tolerance_angstrom"])
    if residual > tolerance:
        raise ValueError(f"rounded rendered input residual {residual} > {tolerance}")
    return {"rendered_round_trip_residual_angstrom": residual}


def prepare_structure(structure_id: str, contract: dict[str, object], contract_hash: str) -> dict[str, object]:
    ids = expected_structure_ids(contract)
    if structure_id not in ids:
        raise ValueError("structure ID is outside the frozen 450-ID set")
    verify_frozen_project_files(contract)
    basis_hashes = verify_basis(contract)
    with workflow_lock():
        state = load_workflow_state(contract)
        if state.get("hard_stopped"):
            raise ValueError("overlap workflow is hard-stopped")
        smoke_id = str(contract["execution"]["smoke_structure_id"])
        if structure_id == smoke_id:
            expected_stage = "BUILD_PASSED"
            bucket = "overlap_smoke"
        else:
            expected_stage = "PROJECTION_PASSED" if len(state["completed_structure_ids"]) == 1 else "BATCH_RUNNING"
            bucket = "overlap_batch"
        require_budget_wrapper(bucket)
        if state.get("stage") != expected_stage:
            raise ValueError(f"input generation is not allowed at stage {state.get('stage')}")
        if state.get("next_structure_id") != structure_id:
            raise ValueError(
                f"out-of-order structure: expected {state.get('next_structure_id')}, got {structure_id}"
            )

        processed_root = runtime_path(contract, "processed_data")
        source = processed_root / structure_id
        if processed_root.is_symlink() or source.is_symlink() or not source.is_dir():
            raise ValueError(f"missing frozen structure directory: {source}")
        loaded = load_structure(source, contract)
        run_root = runtime_path(contract, "run_root")
        run_dir = run_root / structure_id
        staging = run_root / f".{structure_id}.preparing"
        if run_dir.exists() or staging.exists():
            raise ValueError("run directory or input staging directory already exists")
        staging.mkdir(parents=True)
        input_path = staging / "openmx.dat"
        input_text = render_input(
            structure_id,
            runtime_path(contract, "openmx_data"),
            loaded["lattice"],  # type: ignore[arg-type]
            loaded["fractional"],  # type: ignore[arg-type]
            contract,
        )
        input_path.write_text(input_text, encoding="utf-8", newline="\n")
        rendered = verify_rendered_input(
            input_path.read_text(encoding="utf-8"),
            structure_id,
            runtime_path(contract, "openmx_data"),
            loaded["cartesian"],  # type: ignore[arg-type]
            contract,
        )
        build_manifest = runtime_path(contract, "build_manifest")
        mapping: dict[str, object] = {
            "schema_version": "m9-openmx-structure-mapping-v1",
            "structure_id": structure_id,
            "source_directory": source.as_posix(),
            "run_directory": run_dir.as_posix(),
            "atom_index_mapping": "source column k maps to OpenMX atom index k+1",
            "atom_count": 72,
            "basis": "C6.0-s2p2d1/C_PBE19",
            "basis_sha256": basis_hashes,
            "contract_sha256": contract_hash,
            "build_manifest_sha256": file_sha256(build_manifest),
            "coordinate_rule": "frac = site_positions.dat.T @ inverse(lat.dat.T)",
            "round_trip_residual_angstrom": loaded["round_trip_residual_angstrom"],
            "rendered_round_trip_residual_angstrom": rendered[
                "rendered_round_trip_residual_angstrom"
            ],
            "reciprocal_residual": loaded["reciprocal_residual"],
            "lattice_determinant_angstrom_cubed": loaded[
                "lattice_determinant_angstrom_cubed"
            ],
            "dataset_inventory_sha256": str(contract["dataset_provenance"]["inventory_sha256"]),
            "dataset_contract_sha256": str(contract["dataset_provenance"]["data_contract_sha256"]),
            "source_sha256": loaded["source_sha256"],
            "openmx_input": {
                "path": (run_dir / "openmx.dat").as_posix(),
                "bytes": input_path.stat().st_size,
                "sha256": file_sha256(input_path),
            },
        }
        mapping_path = staging / "structure_mapping.json"
        atomic_json(mapping_path, mapping)
        os.replace(staging, run_dir)
        state["stage"] = "SMOKE_INPUT_READY" if structure_id == smoke_id else "BATCH_INPUT_READY"
        state["active_structure_id"] = structure_id
        state["active_input_sha256"] = mapping["openmx_input"]["sha256"]
        state["active_mapping_sha256"] = file_sha256(run_dir / "structure_mapping.json")
        save_workflow_state(contract, state)
        mapping["mapping_sha256"] = state["active_mapping_sha256"]
        return mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-id", required=True)
    args = parser.parse_args()
    contract, contract_hash = load_contract()
    result = prepare_structure(str(args.structure_id), contract, contract_hash)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
