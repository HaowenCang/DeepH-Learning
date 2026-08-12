#!/usr/bin/env python3
"""Validate one frozen overlap-only OpenMX structure output."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py
import numpy as np


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


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


def load_hdf5(path: Path) -> tuple[dict[tuple[int, int, int, int, int], np.ndarray], dict[str, str]]:
    matrices: dict[tuple[int, int, int, int, int], np.ndarray] = {}
    spellings: dict[str, str] = {}
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
            spellings[json.dumps(list(key), separators=(",", ":"))] = key_text
    if not matrices:
        raise ValueError("overlap HDF5 contains no matrices")
    return matrices, spellings


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


def max_abs_difference(path_a: Path, path_b: Path) -> float:
    a = np.loadtxt(path_a, dtype=np.float64, ndmin=1)
    b = np.loadtxt(path_b, dtype=np.float64, ndmin=1)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {path_a.name} {a.shape} != {path_b.name} {b.shape}")
    return float(np.max(np.abs(a - b))) if a.size else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--source-structure", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    output_contract = contract["output_contract"]
    raw_path = args.run_dir / str(output_contract["raw_relative_path"])
    output_dir = raw_path.parent
    actual_rank_files = sorted(path.name for path in output_dir.glob("overlaps_*.h5"))
    if actual_rank_files != list(output_contract["raw_rank_files_allowed"]):
        raise ValueError(f"unexpected rank files: {actual_rank_files}")
    additional_hdf5 = sorted(
        path.relative_to(args.run_dir).as_posix()
        for path in args.run_dir.rglob("*.h5")
        if path != raw_path and path.parent != args.parsed_dir
    )
    if additional_hdf5:
        raise ValueError(f"forbidden additional run HDF5 outputs: {additional_hdf5}")

    raw, raw_spellings = load_hdf5(raw_path)
    expected_keys = load_expected_keys(args.source_structure / "rh.npz")
    if set(raw) != expected_keys:
        missing = sorted(expected_keys - set(raw))[:5]
        extra = sorted(set(raw) - expected_keys)[:5]
        raise ValueError(
            f"overlap/Hamiltonian key spaces differ: missing={missing}, extra={extra}"
        )
    reverse_residual = max_reverse_residual(raw)
    reverse_tolerance = float(output_contract["reverse_absolute_tolerance"])
    if reverse_residual > reverse_tolerance:
        raise ValueError(
            f"reverse residual {reverse_residual:.17g} > {reverse_tolerance:.17g}"
        )

    parsed_path = args.parsed_dir / str(output_contract["parsed_filename"])
    parsed, _ = load_hdf5(parsed_path)
    if set(parsed) != set(raw):
        raise ValueError("parsed overlap keys differ from raw overlap keys")
    parsed_copy_residual = max(
        float(np.max(np.abs(raw[key] - parsed[key]))) for key in raw
    )
    if parsed_copy_residual != 0.0:
        raise ValueError(f"parsed overlap copy is not exact: {parsed_copy_residual:.17g}")

    coordinate_tolerance = float(
        output_contract["parsed_coordinate_absolute_tolerance_angstrom"]
    )
    structure_residuals = {
        name: max_abs_difference(args.source_structure / name, args.parsed_dir / name)
        for name in ("lat.dat", "rlat.dat", "site_positions.dat")
    }
    if max(structure_residuals.values()) > coordinate_tolerance:
        raise ValueError(
            f"parsed structure residual exceeds {coordinate_tolerance}: {structure_residuals}"
        )
    source_elements = np.loadtxt(args.source_structure / "element.dat", dtype=np.int64)
    parsed_elements = np.loadtxt(args.parsed_dir / "element.dat", dtype=np.int64)
    source_orbitals = np.loadtxt(args.source_structure / "orbital_types.dat", dtype=np.int64)
    parsed_orbitals = np.loadtxt(args.parsed_dir / "orbital_types.dat", dtype=np.int64)
    if not np.array_equal(source_elements, parsed_elements):
        raise ValueError("parsed elements differ from the frozen structure")
    if not np.array_equal(source_orbitals, parsed_orbitals):
        raise ValueError("parsed orbital rows differ from the frozen basis")

    onsite_key = (0, 0, 0, 1, 1)
    if onsite_key not in raw:
        raise ValueError("missing atom-1 onsite overlap block")
    onsite_symmetry_residual = float(
        np.max(np.abs(raw[onsite_key] - raw[onsite_key].T))
    )
    onsite_min_eigenvalue = float(np.linalg.eigvalsh(raw[onsite_key]).min())
    if not math.isfinite(onsite_min_eigenvalue) or onsite_min_eigenvalue <= 0.0:
        raise ValueError("atom-1 onsite overlap block is not positive definite")

    report = {
        "schema_version": "m9-overlap-structure-report-v1",
        "structure_id": args.source_structure.name,
        "status": "PASS",
        "raw_overlap": {
            "path": raw_path.as_posix(),
            "bytes": raw_path.stat().st_size,
            "sha256": file_sha256(raw_path),
            "key_count": len(raw),
            "key_spelling_count": len(raw_spellings),
            "reverse_max_abs_residual": reverse_residual,
            "atom1_onsite_symmetry_residual": onsite_symmetry_residual,
            "atom1_onsite_min_eigenvalue": onsite_min_eigenvalue,
        },
        "parsed_overlap": {
            "path": parsed_path.as_posix(),
            "bytes": parsed_path.stat().st_size,
            "sha256": file_sha256(parsed_path),
            "copy_max_abs_residual": parsed_copy_residual,
        },
        "structure_max_abs_residuals": structure_residuals,
        "source_hamiltonian_key_count": len(expected_keys),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
