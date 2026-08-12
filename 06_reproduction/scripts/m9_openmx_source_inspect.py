#!/usr/bin/env python3
"""Inspect the frozen overlap-only OpenMX source objects without extracting them."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
from typing import BinaryIO


ARCHIVES = {
    "openmx_base": {
        "filename": "openmx3.9.tar.gz",
        "expected_sha256": "27bb56bd4d1582d33ad32108fb239b546bdd1bdffd6f5b739b4423da1ab93ae2",
        "required_members": [
            "openmx3.9/source/openmx.c",
            "openmx3.9/source/truncation.c",
            "openmx3.9/source/makefile",
            "openmx3.9/DFT_DATA19/PAO/C6.0.pao",
            "openmx3.9/DFT_DATA19/VPS/C_PBE19.vps",
        ],
    },
    "openmx_patch_3_9_9": {
        "filename": "patch3.9.9.tar.gz",
        "expected_sha256": "20cccc4e3412a814a53568f400260e90f79f0bfb7e2bed84447fe071b26edd38",
        "required_members": ["openmx.c", "truncation.c", "makefile"],
    },
    "hdf5_1_12_1": {
        "filename": "hdf5-1.12.1.tar.gz",
        "expected_sha256": "79c66ff67e666665369396e9c90b32e238e501f345afd2234186bfb8331081ca",
        "required_members": [
            "hdf5-1.12.1/configure",
            "hdf5-1.12.1/COPYING",
        ],
    },
}

REPOSITORY_FILES = [
    "README.md",
    "overlap_only_patch/openmx.c",
    "overlap_only_patch/truncation.c",
    "examples/MATBG.dat",
]


def sha256_stream(handle: BinaryIO) -> str:
    digest = hashlib.sha256()
    while block := handle.read(8 * 1024 * 1024):
        digest.update(block)
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return sha256_stream(handle)


def normalized_member_name(name: str) -> str:
    if "\\" in name:
        raise ValueError(f"tar member contains a backslash: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise ValueError(f"unsafe tar member path: {name!r}")
    normalized = path.as_posix().lstrip("./")
    if not normalized or normalized == ".":
        raise ValueError(f"empty tar member path: {name!r}")
    return normalized


def inspect_archive(path: Path, expected_sha256: str, required_members: list[str]) -> dict[str, object]:
    actual_sha256 = file_sha256(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(f"{path.name}: SHA-256 mismatch: {actual_sha256}")

    member_hashes: dict[str, dict[str, object]] = {}
    normalized_names: set[str] = set()
    member_count = 0
    regular_file_count = 0
    directory_count = 0
    link_count = 0
    special_count = 0
    uncompressed_regular_bytes = 0
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()
        member_count = len(members)
        for member in members:
            normalized = normalized_member_name(member.name)
            if normalized in normalized_names:
                raise ValueError(f"{path.name}: duplicate normalized member: {normalized}")
            normalized_names.add(normalized)
            if member.isdir():
                directory_count += 1
            elif member.isreg():
                regular_file_count += 1
                uncompressed_regular_bytes += member.size
            elif member.issym() or member.islnk():
                link_count += 1
                target = PurePosixPath(normalized).parent / member.linkname
                normalized_member_name(target.as_posix())
            else:
                special_count += 1

        for required in required_members:
            try:
                member = archive.getmember(required)
            except KeyError as exc:
                raise ValueError(f"{path.name}: missing required member {required!r}") from exc
            if not member.isreg():
                raise ValueError(f"{path.name}: required member is not regular: {required!r}")
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ValueError(f"{path.name}: could not read required member {required!r}")
            with extracted:
                member_hashes[required] = {
                    "bytes": member.size,
                    "sha256": sha256_stream(extracted),
                }

    return {
        "path": path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": actual_sha256,
        "member_count": member_count,
        "regular_file_count": regular_file_count,
        "directory_count": directory_count,
        "link_count": link_count,
        "special_count": special_count,
        "uncompressed_regular_bytes": uncompressed_regular_bytes,
        "safe_member_contract_pass": special_count == 0,
        "required_members": member_hashes,
    }


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", os.fspath(repo), *args], text=True, encoding="utf-8"
    ).strip()


def inspect_repository(repo: Path, expected_commit: str) -> dict[str, object]:
    commit = git_output(repo, "rev-parse", "HEAD")
    if commit != expected_commit:
        raise ValueError(f"overlap-only repository commit mismatch: {commit}")
    status = git_output(repo, "status", "--porcelain=v1")
    if status:
        raise ValueError(f"overlap-only repository is dirty: {status}")
    files: dict[str, dict[str, object]] = {}
    for relative in REPOSITORY_FILES:
        path = repo / relative
        if not path.is_file():
            raise ValueError(f"missing overlap-only repository file: {relative}")
        files[relative] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
    return {
        "path": repo.as_posix(),
        "remote": "https://github.com/mzjb/overlap-only-OpenMX.git",
        "commit": commit,
        "clean": True,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    archives: dict[str, object] = {}
    for object_id, contract in ARCHIVES.items():
        archives[object_id] = inspect_archive(
            args.source_dir / str(contract["filename"]),
            str(contract["expected_sha256"]),
            list(contract["required_members"]),
        )

    manifest = {
        "schema_version": "m9-overlap-source-manifest-v1",
        "scope": "source_identity_only_no_extraction_build_install_or_calculation",
        "archives": archives,
        "overlap_only_repository": inspect_repository(
            args.repository, "c8bd8f4e01f9f19868bf2928671c21b12272a6f7"
        ),
        "application_order": [
            "extract_openmx3.9_base",
            "apply_official_patch3.9.9_into_openmx3.9/source",
            "overwrite_openmx.c_and_truncation.c_from_overlap_only_commit",
            "apply_frozen_makefile_contract",
        ],
        "selected_basis": {
            "species": "C",
            "paos": "C6.0-s2p2d1",
            "vps": "C_PBE19",
            "radial_cutoff_bohr": 6.0,
            "orbital_functions_per_atom": 13,
            "source_archive": "openmx_base",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
