#!/usr/bin/env python3
"""Generate deterministic overlap-only OpenMX inputs from the frozen dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_ORBITALS = np.asarray([0, 0, 1, 1, 2], dtype=np.int64)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def expected_ids(contract: dict[str, object]) -> list[str]:
    scope = contract["scope"]
    assert isinstance(scope, dict)
    rule = scope["structure_ids"]
    assert isinstance(rule, dict)
    values = list(
        range(int(rule["start"]), int(rule["stop_inclusive"]) + 1, int(rule["step"]))
    )
    if len(values) != int(rule["count"]):
        raise ValueError("structure ID rule does not match the frozen count")
    return [str(value) for value in values]


def load_structure(source: Path, contract: dict[str, object]) -> dict[str, object]:
    info = json.loads((source / "info.json").read_text(encoding="utf-8"))
    if info != {
        "nsites": 72,
        "fermi_level": info.get("fermi_level"),
        "isorthogonal": False,
        "isspinful": False,
        "norbits": 936,
    }:
        raise ValueError(f"{source.name}: unexpected info.json contract")
    if not np.isfinite(float(info["fermi_level"])):
        raise ValueError(f"{source.name}: non-finite Fermi level")

    elements = np.loadtxt(source / "element.dat", dtype=np.int64, ndmin=1)
    orbitals = np.loadtxt(source / "orbital_types.dat", dtype=np.int64, ndmin=2)
    stored_lattice = np.loadtxt(source / "lat.dat", dtype=np.float64, ndmin=2)
    stored_positions = np.loadtxt(
        source / "site_positions.dat", dtype=np.float64, ndmin=2
    )
    if elements.shape != (72,) or not np.all(elements == 6):
        raise ValueError(f"{source.name}: expected 72 carbon atoms")
    if orbitals.shape != (72, 5) or not np.all(orbitals == EXPECTED_ORBITALS):
        raise ValueError(f"{source.name}: orbital rows do not match [0,0,1,1,2]")
    if stored_lattice.shape != (3, 3) or stored_positions.shape != (3, 72):
        raise ValueError(f"{source.name}: lattice/position shape mismatch")
    if not np.isfinite(stored_lattice).all() or not np.isfinite(stored_positions).all():
        raise ValueError(f"{source.name}: non-finite lattice or position")

    lattice = stored_lattice.T
    cartesian = stored_positions.T
    determinant = float(np.linalg.det(lattice))
    if determinant <= 1e-12:
        raise ValueError(f"{source.name}: lattice is not right-handed and nonsingular")
    fractional = cartesian @ np.linalg.inv(lattice)
    mapping = contract["input_mapping"]
    assert isinstance(mapping, dict)
    tolerance = float(mapping["round_trip_absolute_tolerance_angstrom"])
    residual = float(np.max(np.abs(fractional @ lattice - cartesian)))
    if residual > tolerance:
        raise ValueError(
            f"{source.name}: fractional round-trip {residual:.17g} > {tolerance:.17g}"
        )
    if np.min(fractional) < -1e-12 or np.max(fractional) >= 1.0 + 1e-12:
        raise ValueError(f"{source.name}: fractional coordinates are outside [0,1)")
    return {
        "info": info,
        "lattice": lattice,
        "cartesian": cartesian,
        "fractional": fractional,
        "round_trip_residual_angstrom": residual,
        "lattice_determinant_angstrom_cubed": determinant,
    }


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
        raise ValueError("this generator freezes input_decimal_places=16")
    lines = [
        f"System.CurrentDirectory         ./",
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


def prepare_structure(
    structure_id: str,
    processed_root: Path,
    output_root: Path,
    openmx_data_path: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    source = processed_root / structure_id
    if not source.is_dir():
        raise ValueError(f"missing source structure: {structure_id}")
    loaded = load_structure(source, contract)
    run_dir = output_root / structure_id
    if run_dir.exists() and any(run_dir.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty run directory: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = run_dir / "openmx.dat"
    input_text = render_input(
        structure_id,
        openmx_data_path,
        loaded["lattice"],  # type: ignore[arg-type]
        loaded["fractional"],  # type: ignore[arg-type]
        contract,
    )
    input_path.write_text(input_text, encoding="utf-8", newline="\n")
    source_files = [
        "element.dat",
        "info.json",
        "lat.dat",
        "orbital_types.dat",
        "rh.npz",
        "site_positions.dat",
    ]
    mapping = {
        "schema_version": "m9-openmx-structure-mapping-v1",
        "structure_id": structure_id,
        "source_directory": source.as_posix(),
        "run_directory": run_dir.as_posix(),
        "atom_index_mapping": "source column k maps to OpenMX atom index k+1",
        "atom_count": 72,
        "basis": "C6.0-s2p2d1/C_PBE19",
        "coordinate_rule": "frac = site_positions.dat.T @ inverse(lat.dat.T)",
        "round_trip_residual_angstrom": loaded["round_trip_residual_angstrom"],
        "lattice_determinant_angstrom_cubed": loaded[
            "lattice_determinant_angstrom_cubed"
        ],
        "source_sha256": {
            name: file_sha256(source / name) for name in source_files
        },
        "openmx_input": {
            "path": input_path.as_posix(),
            "bytes": input_path.stat().st_size,
            "sha256": file_sha256(input_path),
        },
    }
    mapping_path = run_dir / "structure_mapping.json"
    mapping_path.write_text(
        json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mapping["mapping_sha256"] = file_sha256(mapping_path)
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--processed-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--openmx-data-path", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--structure-id")
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    ids = expected_ids(contract)
    selected = ids if args.all else [str(args.structure_id)]
    if any(structure_id not in ids for structure_id in selected):
        raise ValueError("requested structure ID is outside the frozen 450-ID set")
    results = [
        prepare_structure(
            structure_id,
            args.processed_root,
            args.output_root,
            args.openmx_data_path,
            contract,
        )
        for structure_id in selected
    ]
    summary = {
        "schema_version": "m9-openmx-input-batch-v1",
        "count": len(results),
        "structure_ids": selected,
        "mapping_sha256": {
            result["structure_id"]: result["mapping_sha256"] for result in results
        },
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
