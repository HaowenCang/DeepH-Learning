#!/usr/bin/env python3
"""Validate the frozen DeepH graphene processed-data contract."""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


REQUIRED_FILES = {
    "element.dat",
    "info.json",
    "lat.dat",
    "orbital_types.dat",
    "rc.npz",
    "rh.npz",
    "rlat.dat",
    "site_positions.dat",
}
EXPECTED_ORBITAL_ROW = [0, 0, 1, 1, 2]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def update_max(current: float, value: float) -> float:
    return max(current, float(value))


def parse_key(text: str, nsites: int) -> tuple[int, int, int, int, int]:
    raw = json.loads(text)
    if not isinstance(raw, list) or len(raw) != 5:
        raise ValueError(f"invalid matrix key: {text!r}")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in raw):
        raise ValueError(f"matrix key is not five integers: {text!r}")
    key = tuple(raw)
    if not (1 <= key[3] <= nsites and 1 <= key[4] <= nsites):
        raise ValueError(f"matrix key atom index is outside 1..{nsites}: {text!r}")
    return key  # type: ignore[return-value]


def validate_dataset(root: Path, official_config: Path) -> dict[str, object]:
    directories = sorted(
        (path for path in root.iterdir() if path.is_dir()), key=lambda path: int(path.name)
    )
    if not directories or any(not path.name.isdecimal() for path in directories):
        raise ValueError("structure directories must be a non-empty decimal-ID set")
    if any(path.is_file() for path in root.iterdir()):
        raise ValueError("processed root contains unexpected regular files")

    config = configparser.ConfigParser()
    config.read(official_config)
    ratios = {
        "train": config.getfloat("train", "train_ratio"),
        "validation": config.getfloat("train", "val_ratio"),
        "test": config.getfloat("train", "test_ratio"),
    }
    if not math.isclose(sum(ratios.values()), 1.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError(f"official split ratios do not sum to one: {ratios}")

    structure_ids: list[str] = []
    fermi_levels: list[float] = []
    nsites_values: set[int] = set()
    norbits_values: set[int] = set()
    spinful_values: set[bool] = set()
    orthogonal_values: set[bool] = set()
    matrix_key_counts: list[int] = []
    translation_components: list[set[int]] = [set(), set(), set()]
    missing_reverse_keys = 0
    max_lattice_reciprocal_residual = 0.0
    max_rotation_orthogonality_residual = 0.0
    max_rotation_det_residual = 0.0
    max_hamiltonian_reverse_residual_ev = 0.0
    hamiltonian_min_ev = math.inf
    hamiltonian_max_ev = -math.inf
    unexpected_files: dict[str, list[str]] = {}

    for index, directory in enumerate(directories, start=1):
        structure_id = directory.name
        structure_ids.append(structure_id)
        actual_files = {path.name for path in directory.iterdir() if path.is_file()}
        actual_dirs = [path.name for path in directory.iterdir() if path.is_dir()]
        if actual_dirs or actual_files != REQUIRED_FILES:
            unexpected_files[structure_id] = sorted(
                (actual_files - REQUIRED_FILES)
                | (REQUIRED_FILES - actual_files)
                | {f"directory:{name}" for name in actual_dirs}
            )
            continue

        info = json.loads((directory / "info.json").read_text(encoding="utf-8"))
        expected_info_keys = {"nsites", "fermi_level", "isorthogonal", "isspinful", "norbits"}
        if set(info) != expected_info_keys:
            raise ValueError(f"{structure_id}: unexpected info.json keys: {sorted(info)}")
        nsites = int(info["nsites"])
        norbits = int(info["norbits"])
        fermi_level = float(info["fermi_level"])
        if not math.isfinite(fermi_level):
            raise ValueError(f"{structure_id}: non-finite Fermi level")
        nsites_values.add(nsites)
        norbits_values.add(norbits)
        spinful_values.add(bool(info["isspinful"]))
        orthogonal_values.add(bool(info["isorthogonal"]))
        fermi_levels.append(fermi_level)

        elements = np.loadtxt(directory / "element.dat", dtype=np.int64, ndmin=1)
        positions = np.loadtxt(directory / "site_positions.dat", dtype=np.float64, ndmin=2)
        orbitals = np.loadtxt(directory / "orbital_types.dat", dtype=np.int64, ndmin=2)
        lattice = np.loadtxt(directory / "lat.dat", dtype=np.float64, ndmin=2)
        reciprocal = np.loadtxt(directory / "rlat.dat", dtype=np.float64, ndmin=2)
        if elements.shape != (nsites,) or not np.all(elements == 6):
            raise ValueError(f"{structure_id}: element.dat is not {nsites} carbon atoms")
        if positions.shape != (3, nsites) or not np.isfinite(positions).all():
            raise ValueError(f"{structure_id}: invalid site_positions.dat")
        if orbitals.shape != (nsites, len(EXPECTED_ORBITAL_ROW)):
            raise ValueError(f"{structure_id}: unexpected orbital_types.dat shape")
        if not np.all(orbitals == np.asarray(EXPECTED_ORBITAL_ROW)):
            raise ValueError(f"{structure_id}: inconsistent carbon orbital rows")
        orbital_count = int(np.sum(2 * orbitals + 1))
        if orbital_count != norbits:
            raise ValueError(f"{structure_id}: orbital count {orbital_count} != norbits {norbits}")
        if lattice.shape != (3, 3) or reciprocal.shape != (3, 3):
            raise ValueError(f"{structure_id}: lattice matrices must be 3x3")
        if not np.isfinite(lattice).all() or not np.isfinite(reciprocal).all():
            raise ValueError(f"{structure_id}: non-finite lattice data")
        if abs(float(np.linalg.det(lattice))) <= 1e-12:
            raise ValueError(f"{structure_id}: singular lattice")
        reciprocal_residual = np.max(np.abs(lattice.T @ reciprocal - 2 * np.pi * np.eye(3)))
        max_lattice_reciprocal_residual = update_max(
            max_lattice_reciprocal_residual, reciprocal_residual
        )

        with np.load(directory / "rc.npz", allow_pickle=False) as rotations_npz, np.load(
            directory / "rh.npz", allow_pickle=False
        ) as hamiltonian_npz:
            if set(rotations_npz.files) != set(hamiltonian_npz.files):
                raise ValueError(f"{structure_id}: rc/rh key spaces differ")
            matrix_key_counts.append(len(hamiltonian_npz.files))
            hamiltonians: dict[tuple[int, int, int, int, int], np.ndarray] = {}
            for key_text in hamiltonian_npz.files:
                key = parse_key(key_text, nsites)
                for axis in range(3):
                    translation_components[axis].add(key[axis])
                hamiltonian = np.asarray(hamiltonian_npz[key_text])
                rotation = np.asarray(rotations_npz[key_text])
                if hamiltonian.shape != (13, 13) or hamiltonian.dtype != np.float64:
                    raise ValueError(f"{structure_id}: invalid Hamiltonian block at {key_text}")
                if rotation.shape != (3, 3) or rotation.dtype != np.float64:
                    raise ValueError(f"{structure_id}: invalid local rotation at {key_text}")
                if not np.isfinite(hamiltonian).all() or not np.isfinite(rotation).all():
                    raise ValueError(f"{structure_id}: non-finite NPZ block at {key_text}")
                hamiltonians[key] = hamiltonian
                hamiltonian_min_ev = min(hamiltonian_min_ev, float(hamiltonian.min()))
                hamiltonian_max_ev = max(hamiltonian_max_ev, float(hamiltonian.max()))
                max_rotation_orthogonality_residual = update_max(
                    max_rotation_orthogonality_residual,
                    np.max(np.abs(rotation.T @ rotation - np.eye(3))),
                )
                max_rotation_det_residual = update_max(
                    max_rotation_det_residual, abs(float(np.linalg.det(rotation)) - 1.0)
                )

            for key, hamiltonian in hamiltonians.items():
                reverse = (-key[0], -key[1], -key[2], key[4], key[3])
                if reverse not in hamiltonians:
                    missing_reverse_keys += 1
                    continue
                max_hamiltonian_reverse_residual_ev = update_max(
                    max_hamiltonian_reverse_residual_ev,
                    np.max(np.abs(hamiltonian - hamiltonians[reverse].T)),
                )

        if index % 25 == 0:
            print(
                json.dumps(
                    {"validated_structures": index, "total_structures": len(directories)},
                    sort_keys=True,
                ),
                flush=True,
            )

    if unexpected_files:
        raise ValueError(f"structure file-set mismatches: {unexpected_files}")

    overlap_candidates = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ("overlap" in path.name.lower() or path.name.lower() in {"rs.npz", "s.npz"})
    )
    reference_physics_candidates = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and any(token in path.name.lower() for token in ("band", "eigen", "kpoint", "dos"))
    )

    structural_contract_pass = (
        len(directories) == 450
        and structure_ids == [str(value) for value in range(500, 5000, 10)]
        and nsites_values == {72}
        and norbits_values == {936}
        and spinful_values == {False}
        and orthogonal_values == {False}
        and min(matrix_key_counts) == max(matrix_key_counts) == 2880
        and missing_reverse_keys == 0
    )
    overlap_required = orthogonal_values == {False}
    overlap_present = bool(overlap_candidates)
    full_m9_physics_contract_pass = structural_contract_pass and (
        not overlap_required or overlap_present
    )
    gate_failures: list[dict[str, str]] = []
    if not structural_contract_pass:
        gate_failures.append(
            {
                "id": "M9-DATA-B00",
                "reason": "processed training-data structural contract failed",
            }
        )
    if overlap_required and not overlap_present:
        gate_failures.append(
            {
                "id": "M9-DATA-B01",
                "reason": (
                    "all structures declare isorthogonal=false, but the frozen archive contains no "
                    "overlap matrix; generalized eigenproblem and band validation are not defined"
                ),
            }
        )

    return {
        "schema_version": "m9-graphene-data-contract-v1",
        "dataset_root": str(root),
        "structure_count": len(directories),
        "structure_ids": structure_ids,
        "structure_id_rule": "decimal IDs 500..4990 inclusive, step 10",
        "species_atomic_numbers": [6],
        "nsites_values": sorted(nsites_values),
        "norbits_values": sorted(norbits_values),
        "spinful_values": sorted(spinful_values),
        "orthogonal_values": sorted(orthogonal_values),
        "orbital_types_per_atom": EXPECTED_ORBITAL_ROW,
        "orbitals_per_atom": 13,
        "coordinate_unit": "angstrom (DeepH OpenMX processed-data contract)",
        "hamiltonian_unit": "eV (DeepH training/error-reporting contract)",
        "fermi_level_unit": "eV",
        "fermi_level_range": [min(fermi_levels), max(fermi_levels)],
        "matrix_key_schema": "[R1,R2,R3,i,j], R integer, atom indices one-based",
        "matrix_key_count_range": [min(matrix_key_counts), max(matrix_key_counts)],
        "translation_components": [sorted(values) for values in translation_components],
        "hamiltonian_block_shape": [13, 13],
        "hamiltonian_dtype": "float64",
        "hamiltonian_value_range_ev": [hamiltonian_min_ev, hamiltonian_max_ev],
        "local_rotation_shape": [3, 3],
        "local_rotation_dtype": "float64",
        "max_lattice_reciprocal_residual": max_lattice_reciprocal_residual,
        "max_rotation_orthogonality_residual": max_rotation_orthogonality_residual,
        "max_rotation_det_residual": max_rotation_det_residual,
        "missing_reverse_keys": missing_reverse_keys,
        "max_hamiltonian_reverse_residual_ev": max_hamiltonian_reverse_residual_ev,
        "official_config": {
            "path": str(official_config),
            "sha256": file_sha256(official_config),
            "dataset_name": config.get("basic", "dataset_name"),
            "interface": config.get("basic", "interface"),
            "radius_angstrom": config.getfloat("graph", "radius"),
            "epochs": config.getint("train", "epochs"),
            "ratios": ratios,
            "batch_size": config.getint("hyperparameter", "batch_size"),
            "learning_rate": config.getfloat("hyperparameter", "learning_rate"),
        },
        "official_explicit_split_ids_present": False,
        "overlap_required": overlap_required,
        "overlap_candidates": overlap_candidates,
        "overlap_present": overlap_present,
        "reference_physics_candidates": reference_physics_candidates,
        "structural_training_contract_pass": structural_contract_pass,
        "full_m9_physics_contract_pass": full_m9_physics_contract_pass,
        "gate_failures": gate_failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--official-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-full-m9-contract", action="store_true")
    args = parser.parse_args()

    payload = validate_dataset(args.dataset_root, args.official_config)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    os.replace(temporary, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "bytes": args.output.stat().st_size,
                "structural_training_contract_pass": payload["structural_training_contract_pass"],
                "full_m9_physics_contract_pass": payload["full_m9_physics_contract_pass"],
                "gate_failures": payload["gate_failures"],
            },
            sort_keys=True,
        )
    )
    if args.require_full_m9_contract and not payload["full_m9_physics_contract_pass"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
