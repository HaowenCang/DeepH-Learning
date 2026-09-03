#!/usr/bin/env python3
"""Controlled source composition and build driver for overlap-only OpenMX."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import subprocess
import tarfile
from typing import Iterable

from m9_overlap_common import (
    atomic_json,
    file_sha256,
    hard_stop_workflow,
    load_contract,
    load_workflow_state,
    require_budget_context,
    runtime_path,
    save_workflow_state,
    tree_inventory,
    verify_frozen_project_files,
    write_utf8_lf,
    workflow_lock,
)


ACTIVE_ASSIGNMENT = {
    "CC": re.compile(r"^\s*CC\s*=.*$"),
    "FC": re.compile(r"^\s*FC\s*=.*$"),
    "LIB": re.compile(r"^\s*LIB\s*=.*$"),
}
BUILD_ARTIFACT_SUFFIXES = {".o", ".a", ".so", ".mod"}


def safe_member_name(name: str) -> str:
    if "\\" in name:
        raise ValueError(f"tar member contains backslash: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", "..") for part in path.parts):
        raise ValueError(f"unsafe tar member path: {name!r}")
    normalized = path.as_posix().lstrip("./")
    if not normalized or normalized == ".":
        raise ValueError(f"empty tar member path: {name!r}")
    return normalized


def validated_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    names: set[str] = set()
    for member in members:
        normalized = safe_member_name(member.name)
        if normalized in names:
            raise ValueError(f"duplicate normalized tar member: {normalized}")
        names.add(normalized)
        if not (member.isdir() or member.isreg()):
            raise ValueError(f"link or special tar member forbidden: {member.name!r}")
    return members


def verify_archive(path: Path, expected_bytes: int, expected_sha256: str) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size != expected_bytes:
        raise ValueError(f"archive byte-size mismatch: {path}")
    if file_sha256(path) != expected_sha256:
        raise ValueError(f"archive SHA-256 mismatch: {path}")


def safe_extract(archive_path: Path, destination: Path) -> list[str]:
    if destination.exists():
        raise ValueError(f"refusing to extract into existing path: {destination}")
    destination.mkdir(parents=True)
    extracted: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        members = validated_members(archive)
        for member in members:
            relative = safe_member_name(member.name)
            target = destination / relative
            if destination.resolve() not in (target.resolve(strict=False), *target.resolve(strict=False).parents):
                raise ValueError(f"tar member escapes destination: {member.name!r}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"cannot read tar member: {member.name!r}")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output, 8 * 1024 * 1024)
            os.chmod(target, stat.S_IMODE(member.mode) & 0o755)
            if target.stat().st_size != member.size:
                raise ValueError(f"extracted byte-size mismatch: {member.name!r}")
            extracted.append(relative)
    return extracted


def apply_official_patch(archive_path: Path, openmx_root: Path) -> list[str]:
    source_root = openmx_root / "source"
    work_root = openmx_root / "work"
    if not source_root.is_dir() or not work_root.is_dir():
        raise ValueError("OpenMX base tree lacks source/work directories")
    written: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        members = validated_members(archive)
        for member in members:
            if member.isdir():
                continue
            relative = safe_member_name(member.name)
            target = work_root / "kpoint.in" if relative == "kpoint.in" else source_root / relative
            allowed_root = work_root if relative == "kpoint.in" else source_root
            resolved = target.resolve(strict=False)
            if allowed_root.resolve() not in (resolved, *resolved.parents):
                raise ValueError(f"patch member escapes target root: {relative}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"cannot read patch member: {relative}")
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output, 8 * 1024 * 1024)
            os.chmod(target, stat.S_IMODE(member.mode) & 0o755)
            written.append(target.relative_to(openmx_root).as_posix())
    if "work/kpoint.in" not in written:
        raise ValueError("official patch did not place kpoint.in in work")
    return written


def render_makefile(text: str, hdf5_prefix: str, make_contract: dict[str, object]) -> str:
    replacements = {
        "CC": "CC = " + str(make_contract["cc"]).replace("${HDF5_PREFIX}", hdf5_prefix),
        "FC": "FC = " + str(make_contract["fc"]).replace("${HDF5_PREFIX}", hdf5_prefix),
        "LIB": "LIB = " + str(make_contract["lib"]).replace("${HDF5_PREFIX}", hdf5_prefix),
    }
    lines = text.splitlines()
    for name, pattern in ACTIVE_ASSIGNMENT.items():
        indices = [index for index, line in enumerate(lines) if pattern.fullmatch(line)]
        if len(indices) != 1:
            raise ValueError(f"makefile must have exactly one active {name}, found {len(indices)}")
        lines[indices[0]] = replacements[name]
    result = "\n".join(lines) + "\n"
    assert_makefile_contract(result, hdf5_prefix, make_contract)
    return result


def assert_makefile_contract(text: str, hdf5_prefix: str, make_contract: dict[str, object]) -> None:
    expected = {
        "CC": "CC = " + str(make_contract["cc"]).replace("${HDF5_PREFIX}", hdf5_prefix),
        "FC": "FC = " + str(make_contract["fc"]).replace("${HDF5_PREFIX}", hdf5_prefix),
        "LIB": "LIB = " + str(make_contract["lib"]).replace("${HDF5_PREFIX}", hdf5_prefix),
    }
    for name, pattern in ACTIVE_ASSIGNMENT.items():
        values = [line for line in text.splitlines() if pattern.fullmatch(line)]
        if values != [expected[name]]:
            raise ValueError(f"active {name} definition differs from frozen contract: {values}")
    if "-fcommon" not in expected["CC"]:
        raise ValueError("frozen CC must contain -fcommon")
    if "-fallow-argument-mismatch" not in expected["FC"]:
        raise ValueError("frozen FC must contain -fallow-argument-mismatch")


def tool_path(contract: dict[str, object], name: str) -> Path:
    toolchain = contract["software"]["toolchain"]
    assert isinstance(toolchain, dict)
    executables = toolchain["executables"]
    assert isinstance(executables, dict)
    item = executables[name]
    assert isinstance(item, dict)
    path = Path(str(item["path"]))
    resolved = path.resolve(strict=True)
    if resolved.as_posix() != item["resolved"] or not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f"frozen executable identity mismatch: {name} -> {resolved}")
    return path


def verify_tool_paths(contract: dict[str, object]) -> dict[str, object]:
    executables = contract["software"]["toolchain"]["executables"]
    assert isinstance(executables, dict)
    result: dict[str, object] = {}
    for name in executables:
        path = tool_path(contract, str(name))
        resolved = path.resolve(strict=True)
        result[str(name)] = {
            "path": path.as_posix(),
            "resolved": resolved.as_posix(),
            "bytes": resolved.stat().st_size,
            "sha256": file_sha256(resolved),
        }
    return result


def fixed_build_environment(contract: dict[str, object]) -> dict[str, str]:
    toolchain = contract["software"]["toolchain"]
    assert isinstance(toolchain, dict)
    return {
        "PATH": str(toolchain["fixed_path"]),
        "HOME": os.environ["HOME"],
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }


def verify_mpi_wrapper_compilers(contract: dict[str, object]) -> dict[str, object]:
    toolchain = contract["software"]["toolchain"]
    assert isinstance(toolchain, dict)
    fixed_path = str(toolchain["fixed_path"])
    if any(Path(part).as_posix().startswith("/usr/local") for part in fixed_path.split(":")):
        raise ValueError("frozen build PATH must not search /usr/local before system compilers")
    wrappers = toolchain["mpi_wrapper_compilers"]
    assert isinstance(wrappers, dict)
    result: dict[str, object] = {}
    for wrapper_name, raw_policy in wrappers.items():
        if not isinstance(raw_policy, dict):
            raise ValueError(f"invalid MPI wrapper policy: {wrapper_name}")
        output = subprocess.check_output(
            [tool_path(contract, str(wrapper_name)).as_posix(), "--showme:command"],
            text=True,
            encoding="utf-8",
            env=fixed_build_environment(contract),
        ).strip()
        if output != raw_policy["showme_command"]:
            raise ValueError(
                f"MPI wrapper compiler expansion mismatch: {wrapper_name}={output!r}"
            )
        tokens = shlex.split(output)
        if len(tokens) != 1 or Path(tokens[0]).name != tokens[0]:
            raise ValueError(f"MPI wrapper compiler command is not a single frozen name: {output!r}")
        resolved_text = shutil.which(tokens[0], path=fixed_path)
        if resolved_text is None:
            raise ValueError(f"MPI wrapper compiler cannot be resolved: {tokens[0]}")
        resolved = Path(resolved_text).resolve(strict=True)
        registered = str(raw_policy["registered_executable"])
        registered_path = tool_path(contract, registered)
        registered_resolved = registered_path.resolve(strict=True)
        if resolved != registered_resolved:
            raise ValueError(
                f"MPI wrapper compiler is shadowed: {wrapper_name} -> {resolved}, "
                f"expected {registered_resolved}"
            )
        result[str(wrapper_name)] = {
            "showme_command": output,
            "resolved": resolved.as_posix(),
            "registered_executable": registered,
            "bytes": resolved.stat().st_size,
            "sha256": file_sha256(resolved),
        }
    return result


def verify_packages(contract: dict[str, object]) -> dict[str, str]:
    software = contract["software"]
    assert isinstance(software, dict)
    packages = software["ubuntu_packages"]
    assert isinstance(packages, dict)
    actual: dict[str, str] = {}
    for package, expected in packages.items():
        output = subprocess.check_output(
            [tool_path(contract, "dpkg_query").as_posix(), "-W", "-f=${Version}", str(package)],
            text=True,
            encoding="utf-8",
            env=fixed_build_environment(contract),
        ).strip()
        if output != expected:
            raise ValueError(f"apt package version mismatch: {package}={output}, expected {expected}")
        actual[str(package)] = output
    toolchain = software["toolchain"]
    assert isinstance(toolchain, dict)
    commands = {
        "gcc_dumpversion": [tool_path(contract, "gcc").as_posix(), "-dumpfullversion", "-dumpversion"],
        "gfortran_dumpversion": [tool_path(contract, "gfortran").as_posix(), "-dumpfullversion", "-dumpversion"],
        "openmpi_showme_version": [tool_path(contract, "mpicc").as_posix(), "--showme:version"],
    }
    for name, command in commands.items():
        output = subprocess.check_output(
            command, text=True, encoding="utf-8", env=fixed_build_environment(contract)
        ).strip()
        if output != toolchain[name]:
            raise ValueError(f"toolchain version mismatch: {name}={output!r}")
        actual[name] = output
    runtime_packages = toolchain["required_runtime_packages"]
    assert isinstance(runtime_packages, dict)
    for package, expected in runtime_packages.items():
        output = subprocess.check_output(
            [tool_path(contract, "dpkg_query").as_posix(), "-W", "-f=${Version}", str(package)],
            text=True,
            encoding="utf-8",
            env=fixed_build_environment(contract),
        ).strip()
        if output != expected:
            raise ValueError(f"runtime package version mismatch: {package}={output}")
        actual[str(package)] = output
    actual["mpi_wrapper_compilers"] = json.dumps(
        verify_mpi_wrapper_compilers(contract), sort_keys=True
    )
    actual["tool_paths"] = json.dumps(verify_tool_paths(contract), sort_keys=True)
    return actual


def verify_static_sources(contract: dict[str, object]) -> dict[str, str]:
    software = contract["software"]
    assert isinstance(software, dict)
    source_manifest = runtime_path(contract, "source_manifest")
    if file_sha256(source_manifest) != software["source_manifest_sha256"]:
        raise ValueError("runtime overlap source manifest SHA-256 mismatch")
    repository = runtime_path(contract, "overlap_repository")
    patch_contract = software["overlap_only_patch"]
    assert isinstance(patch_contract, dict)
    commit = subprocess.check_output(
        [tool_path(contract, "git").as_posix(), "-C", os.fspath(repository), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
        env=fixed_build_environment(contract),
    ).strip()
    dirty = subprocess.check_output(
        [tool_path(contract, "git").as_posix(), "-C", os.fspath(repository), "status", "--porcelain=v1"],
        text=True,
        encoding="utf-8",
        env=fixed_build_environment(contract),
    ).strip()
    if commit != patch_contract["commit"] or dirty:
        raise ValueError("overlap-only repository commit/clean contract mismatch")
    return {"source_manifest_sha256": file_sha256(source_manifest), "overlap_commit": commit}


def source_files_for_manifest(openmx_root: Path) -> list[str]:
    ignored_names = {"openmx", "openmx.official-3.9.9"}
    result: list[str] = []
    for path in sorted(openmx_root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in combined OpenMX tree: {path}")
        if not path.is_file() or path.name in ignored_names or path.suffix in BUILD_ARTIFACT_SUFFIXES:
            continue
        result.append(path.relative_to(openmx_root).as_posix())
    return result


def verify_build_artifact_allowlist(openmx_root: Path, baseline_paths: set[str]) -> list[str]:
    new_paths: list[str] = []
    for path in sorted(openmx_root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in combined OpenMX tree: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(openmx_root).as_posix()
        if relative in baseline_paths:
            continue
        allowed = (
            path.suffix in BUILD_ARTIFACT_SUFFIXES
            or relative in {
                "source/openmx",
                "source/openmx.official-3.9.9",
                "work/openmx",
            }
        )
        if not allowed:
            raise ValueError(f"unregistered file created by OpenMX build: {relative}")
        new_paths.append(relative)
    return new_paths


def installed_tree_inventory(root: Path) -> dict[str, object]:
    inventory: dict[str, object] = {}
    resolved_root = root.resolve(strict=True)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if resolved_root not in (resolved, *resolved.parents):
                raise ValueError(f"installed-tree symlink escapes prefix: {path}")
            inventory[relative] = {
                "type": "symlink",
                "target": os.readlink(path),
                "resolved": resolved.as_posix(),
                "resolved_sha256": file_sha256(resolved) if resolved.is_file() else None,
            }
        elif path.is_file():
            inventory[relative] = {
                "type": "file",
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        elif not path.is_dir():
            raise ValueError(f"special object in installed tree: {path}")
    if not inventory:
        raise ValueError(f"installed tree is empty: {root}")
    return inventory


def parse_dynamic_libraries(
    contract: dict[str, object], binary: Path, ldd_text: str
) -> dict[str, object]:
    libraries: dict[str, object] = {}
    for raw_line in ldd_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("linux-vdso"):
            continue
        if "not found" in line:
            raise ValueError(f"unresolved dynamic library: {line}")
        if "=>" in line:
            soname, remainder = [part.strip() for part in line.split("=>", 1)]
            text_path = remainder.split(" ", 1)[0]
        elif line.startswith("/"):
            text_path = line.split(" ", 1)[0]
            soname = Path(text_path).name
        else:
            continue
        path = Path(text_path)
        resolved = path.resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"dynamic library is not a regular file: {resolved}")
        package = None
        package_version = None
        if not str(resolved).startswith(runtime_path(contract, "hdf5_prefix").as_posix() + "/"):
            owner_output = None
            for candidate in (path, resolved):
                completed = subprocess.run(
                    [tool_path(contract, "dpkg").as_posix(), "-S", candidate.as_posix()],
                    text=True,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    env=fixed_build_environment(contract),
                    check=False,
                )
                if completed.returncode == 0:
                    owner_output = completed.stdout.strip().splitlines()[0]
                    break
            if owner_output is None:
                raise ValueError(f"system dynamic library has no dpkg owner: {resolved}")
            package = owner_output.split(": ", 1)[0].split(":", 1)[0]
            package_version = subprocess.check_output(
                [tool_path(contract, "dpkg_query").as_posix(), "-W", "-f=${Version}", package],
                text=True,
                encoding="utf-8",
                env=fixed_build_environment(contract),
            ).strip()
        libraries[soname] = {
            "path": path.as_posix(),
            "resolved": resolved.as_posix(),
            "bytes": resolved.stat().st_size,
            "sha256": file_sha256(resolved),
            "dpkg_package": package,
            "dpkg_version": package_version,
        }
    required = contract["software"]["toolchain"]["required_ldd_soname_prefixes"]
    missing = [prefix for prefix in required if not any(name.startswith(prefix) for name in libraries)]
    if missing:
        raise ValueError(f"final OpenMX dynamic libraries lack required sonames: {missing}")
    hdf_entries = [
        value
        for name, value in libraries.items()
        if name.startswith("libhdf5.so") and isinstance(value, dict)
    ]
    hdf_prefix = runtime_path(contract, "hdf5_prefix").as_posix() + "/"
    if len(hdf_entries) != 1 or not str(hdf_entries[0]["resolved"]).startswith(hdf_prefix):
        raise ValueError("OpenMX does not bind exactly one frozen-prefix HDF5 library")
    soname_packages = contract["software"]["toolchain"]["required_soname_packages"]
    runtime_packages = contract["software"]["toolchain"]["required_runtime_packages"]
    for prefix, expected_package in soname_packages.items():
        matches = [
            value
            for name, value in libraries.items()
            if name.startswith(prefix) and isinstance(value, dict)
        ]
        if len(matches) != 1 or matches[0]["dpkg_package"] != expected_package:
            raise ValueError(f"dynamic library package mismatch for {prefix}")
        if matches[0]["dpkg_version"] != runtime_packages[expected_package]:
            raise ValueError(f"dynamic library package version mismatch for {prefix}")
    return libraries


def run_logged(
    command: list[str], cwd: Path, log_path: Path, env: dict[str, str]
) -> dict[str, object]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("wb") as log:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed with exit {completed.returncode}: {command}")
    return {
        "argv": command,
        "cwd": cwd.as_posix(),
        "exit_code": completed.returncode,
        "log_path": log_path.as_posix(),
        "log_sha256": file_sha256(log_path),
    }


def require_budget_wrapper(bucket: str) -> None:
    action = "source_prepare" if bucket == "overlap_build_prepare" else "source_build"
    require_budget_context("overlap_build", (action,))


def prepare_sources(contract: dict[str, object]) -> None:
    require_budget_wrapper("overlap_build_prepare")
    verify_frozen_project_files(contract)
    source_identity = verify_static_sources(contract)
    with workflow_lock():
        state = load_workflow_state(contract)
        if state.get("stage") != "AUDIT_PASSED" or state.get("hard_stopped"):
            raise ValueError(f"source preparation is not allowed at stage {state.get('stage')}")
        build_root = runtime_path(contract, "openmx_build_root")
        staging = build_root.with_name(build_root.name + ".staging")
        if build_root.exists() or staging.exists():
            raise ValueError("build root or staging root already exists")
        software = contract["software"]
        assert isinstance(software, dict)
        downloads = runtime_path(contract, "source_downloads")
        for name, filename in (
            ("openmx_base", "openmx3.9.tar.gz"),
            ("openmx_official_patch", "patch3.9.9.tar.gz"),
            ("hdf5", "hdf5-1.12.1.tar.gz"),
        ):
            item = software[name]
            assert isinstance(item, dict)
            verify_archive(downloads / filename, int(item["bytes"]), str(item["sha256"]))
        safe_extract(downloads / "openmx3.9.tar.gz", staging)
        hdf_stage = staging / "hdf5-source"
        safe_extract(downloads / "hdf5-1.12.1.tar.gz", hdf_stage)
        openmx_root = staging / "openmx3.9"
        written = apply_official_patch(downloads / "patch3.9.9.tar.gz", openmx_root)
        make_contract = software["openmx_makefile"]
        assert isinstance(make_contract, dict)
        makefile = openmx_root / "source/makefile"
        write_utf8_lf(
            makefile,
            render_makefile(
                makefile.read_text(encoding="utf-8"),
                runtime_path(contract, "hdf5_prefix").as_posix(),
                make_contract,
            ),
        )
        source_paths = source_files_for_manifest(openmx_root)
        official_manifest: dict[str, object] = {
            "schema_version": "m9-openmx-official-tree-manifest-v1",
            "application_order": [
                "openmx3.9_base",
                "patch3.9.9_all_regular_members_except_kpoint_to_source",
                "patch3.9.9_kpoint.in_to_work/kpoint.in",
                "frozen_makefile_CC_FC_LIB",
            ],
            "official_patch_written_paths": written,
            "source_identity": source_identity,
            "source_relative_paths": source_paths,
            "tree": tree_inventory(openmx_root, source_paths),
        }
        os.replace(staging, build_root)
        atomic_json(runtime_path(contract, "official_tree_manifest"), official_manifest)
        state["stage"] = "SOURCES_PREPARED"
        state["official_tree_manifest_sha256"] = file_sha256(
            runtime_path(contract, "official_tree_manifest")
        )
        save_workflow_state(contract, state)


def build_sources(contract: dict[str, object]) -> None:
    require_budget_wrapper("overlap_build")
    verify_frozen_project_files(contract)
    source_identity = verify_static_sources(contract)
    with workflow_lock():
        state = load_workflow_state(contract)
        if state.get("stage") != "SOURCES_PREPARED" or state.get("hard_stopped"):
            raise ValueError(f"build is not allowed at stage {state.get('stage')}")
        packages = verify_packages(contract)
        tool_paths = verify_tool_paths(contract)
        build_env = fixed_build_environment(contract)
        build_root = runtime_path(contract, "openmx_build_root")
        openmx_root = build_root / "openmx3.9"
        source_root = openmx_root / "source"
        hdf_source = build_root / "hdf5-source/hdf5-1.12.1"
        hdf_prefix = runtime_path(contract, "hdf5_prefix")
        if hdf_prefix.exists():
            raise ValueError("HDF5 prefix already exists")
        software = contract["software"]
        assert isinstance(software, dict)
        hdf = software["hdf5"]
        assert isinstance(hdf, dict)
        env = dict(build_env)
        env["CC"] = tool_path(contract, "gcc").as_posix()
        env["CFLAGS"] = str(hdf["cflags"])
        configure = [
            "./configure",
            f"--prefix={hdf_prefix.as_posix()}",
            *[str(item) for item in hdf["configure"]],
        ]
        log_root = runtime_path(contract, "linux_root") / "logs/overlap-build"
        build_steps: dict[str, object] = {}
        build_steps["hdf5_configure"] = run_logged(
            configure, hdf_source, log_root / "hdf5-configure.log", env
        )
        make = tool_path(contract, "make").as_posix()
        build_steps["hdf5_make"] = run_logged(
            [make, "-j2"], hdf_source, log_root / "hdf5-make.log", env
        )
        build_steps["hdf5_check"] = run_logged(
            [make, "check", "-j1"], hdf_source, log_root / "hdf5-check.log", env
        )
        build_steps["hdf5_install"] = run_logged(
            [make, "install"], hdf_source, log_root / "hdf5-install.log", env
        )
        hdf5_inventory = installed_tree_inventory(hdf_prefix)
        hdf5_libraries = {
            relative: value
            for relative, value in hdf5_inventory.items()
            if relative.startswith("lib/libhdf5.so")
        }
        if not hdf5_libraries:
            raise ValueError("HDF5 install inventory lacks libhdf5.so objects")

        official_manifest_path = runtime_path(contract, "official_tree_manifest")
        official_manifest = json.loads(official_manifest_path.read_text(encoding="utf-8"))
        source_paths = [str(item) for item in official_manifest["source_relative_paths"]]
        if tree_inventory(openmx_root, source_paths) != official_manifest["tree"]:
            raise ValueError("official source tree changed before build")
        baseline_paths = set(source_paths)
        build_steps["official_clean_before"] = run_logged(
            [make, "clean"], source_root, log_root / "official-clean-before.log", build_env
        )
        build_steps["official_make"] = run_logged(
            [make, "-j2", "all"], source_root, log_root / "official-make.log", build_env
        )
        build_steps["official_install"] = run_logged(
            [make, "install"], source_root, log_root / "official-install.log", build_env
        )
        official_binary = source_root / "openmx"
        if not official_binary.is_file():
            raise ValueError("official OpenMX binary was not produced")
        official_copy = source_root / "openmx.official-3.9.9"
        shutil.copy2(official_binary, official_copy)
        official_build_artifacts = verify_build_artifact_allowlist(openmx_root, baseline_paths)
        build_steps["official_clean_after"] = run_logged(
            [make, "clean"], source_root, log_root / "official-clean-after.log", build_env
        )
        official_after_paths = source_files_for_manifest(openmx_root)
        if set(official_after_paths) != baseline_paths:
            raise ValueError("official post-build controlled path set differs from pre-build tree")
        official_after_tree = tree_inventory(openmx_root, official_after_paths)
        if official_after_tree != official_manifest["tree"]:
            raise ValueError("official post-build controlled tree content changed")

        overlap_repository = runtime_path(contract, "overlap_repository")
        patch_contract = software["overlap_only_patch"]
        assert isinstance(patch_contract, dict)
        changed: dict[str, object] = {}
        for name, hash_field in (
            ("openmx.c", "openmx_c_sha256"),
            ("truncation.c", "truncation_c_sha256"),
        ):
            source = overlap_repository / "overlap_only_patch" / name
            if source.is_symlink() or not source.is_file() or file_sha256(source) != patch_contract[hash_field]:
                raise ValueError(f"overlap-only patch hash mismatch: {name}")
            destination = source_root / name
            shutil.copyfile(source, destination)
            changed[f"source/{name}"] = {
                "before": official_manifest["tree"][f"source/{name}"],
                "after": {"bytes": destination.stat().st_size, "sha256": file_sha256(destination)},
            }
        final_paths = source_files_for_manifest(openmx_root)
        if set(final_paths) != set(official_after_paths):
            raise ValueError("official/overlap controlled path sets differ")
        final_tree = tree_inventory(openmx_root, final_paths)
        differences = [key for key in final_paths if final_tree[key] != official_after_tree[key]]
        if differences != ["source/openmx.c", "source/truncation.c"]:
            raise ValueError(f"unexpected official-to-overlap source differences: {differences}")
        overlap_manifest: dict[str, object] = {
            "schema_version": "m9-openmx-overlap-tree-manifest-v1",
            "official_manifest_sha256": file_sha256(official_manifest_path),
            "only_changed_paths": differences,
            "changed": changed,
            "source_relative_paths": source_paths,
            "official_actual_relative_paths": official_after_paths,
            "final_actual_relative_paths": final_paths,
            "tree": final_tree,
        }
        atomic_json(runtime_path(contract, "overlap_tree_manifest"), overlap_manifest)

        build_steps["overlap_clean_before"] = run_logged(
            [make, "clean"], source_root, log_root / "overlap-clean-before.log", build_env
        )
        build_steps["overlap_make"] = run_logged(
            [make, "-j2", "all"], source_root, log_root / "overlap-make.log", build_env
        )
        build_steps["overlap_install"] = run_logged(
            [make, "install"], source_root, log_root / "overlap-install.log", build_env
        )
        binary = runtime_path(contract, "openmx_binary")
        if not binary.is_file():
            raise ValueError("overlap-only OpenMX binary was not produced")
        final_build_artifacts = verify_build_artifact_allowlist(openmx_root, baseline_paths)
        ldd = subprocess.check_output(
            [tool_path(contract, "ldd").as_posix(), os.fspath(binary)],
            text=True,
            encoding="utf-8",
            env=build_env,
        )
        dynamic_libraries = parse_dynamic_libraries(contract, binary, ldd)
        build_manifest: dict[str, object] = {
            "schema_version": "m9-openmx-overlap-build-manifest-v1",
            "packages": packages,
            "source_identity": source_identity,
            "tool_paths": tool_paths,
            "makefile_sha256": file_sha256(source_root / "makefile"),
            "makefile_contract": software["openmx_makefile"],
            "build_environment": build_env,
            "build_steps": build_steps,
            "official_build_artifacts": official_build_artifacts,
            "final_build_artifacts": final_build_artifacts,
            "hdf5_configure_summary": {
                "argv": configure,
                "cc": env["CC"],
                "cflags": env["CFLAGS"],
                "configure_log_sha256": build_steps["hdf5_configure"]["log_sha256"],
                "make_check_exit_code": build_steps["hdf5_check"]["exit_code"],
                "make_check_log_sha256": build_steps["hdf5_check"]["log_sha256"],
            },
            "hdf5_install_inventory": hdf5_inventory,
            "hdf5_library_objects": hdf5_libraries,
            "official_tree_manifest_sha256": file_sha256(official_manifest_path),
            "overlap_tree_manifest_sha256": file_sha256(
                runtime_path(contract, "overlap_tree_manifest")
            ),
            "hdf5_prefix": hdf_prefix.as_posix(),
            "official_binary_sha256": file_sha256(official_copy),
            "overlap_binary_sha256": file_sha256(binary),
            "ldd": ldd.splitlines(),
            "dynamic_libraries": dynamic_libraries,
            "logs": {
                path.name: file_sha256(path) for path in sorted(log_root.glob("*.log"))
            },
        }
        atomic_json(runtime_path(contract, "build_manifest"), build_manifest)
        state["stage"] = "BUILD_PASSED"
        state["build_manifest_sha256"] = file_sha256(runtime_path(contract, "build_manifest"))
        save_workflow_state(contract, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "build"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract, contract_hash = load_contract()
    try:
        if args.action == "prepare":
            prepare_sources(contract)
        else:
            build_sources(contract)
    except Exception as exc:
        hard_stop_workflow(contract, f"{type(exc).__name__}: {exc}")
        raise
    print(json.dumps({"action": args.action, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
