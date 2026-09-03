#!/usr/bin/env python3
"""Hard-stop budget ledger for the frozen M9 reproduction.

This script has no third-party dependencies. It is intended to be invoked from
Ubuntu-22.04 through WSL for every mutating or GPU-using M9 command.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from typing import Iterable
from urllib.parse import unquote


LINUX_ROOT = Path("/home/evan-williams/deeph-m9")
MANIFESTS = LINUX_ROOT / "manifests"
STATE_PATH = MANIFESTS / "budget_state.json"
LEDGER_PATH = MANIFESTS / "budget_ledger.jsonl"
LOCK_PATH = MANIFESTS / "budget.lock"
PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
REPRODUCTION = PROJECT_ROOT / "06_reproduction"
AUDITS = PROJECT_ROOT / "08_audits"
CONTROL_FILES = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "decisions.md",
    PROJECT_ROOT / "00_scope/master_execution_plan.md",
    PROJECT_ROOT / "00_scope/M8_decision_package.md",
    PROJECT_ROOT / "02_source_ledger/version_registry.md",
    PROJECT_ROOT / "08_audits/progress_tracker.md",
)
HOST_VHDX = Path("/mnt/e/Laptop/WSL/ext4.vhdx")
OVERLAP_AUDIT_GATE = MANIFESTS / "overlap_work_package_audit_gate.json"
OVERLAP_CONTRACT = REPRODUCTION / "configs/m9_overlap_only_contract.json"
OVERLAP_FROZEN_HASHES = (
    REPRODUCTION / "manifests/m9_overlap_py39_recovery_frozen_hashes.json"
)
OVERLAP_WORK_PACKAGE = (
    AUDITS / "M9_source_prepare_py39_consumer_replacement_work_package.md"
)
OVERLAP_PYTHON = Path("/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9")
OVERLAP_SOURCE_LAUNCHER = REPRODUCTION / "scripts/m9_overlap_source_launcher.py"
OVERLAP_WORKFLOW_STATE = MANIFESTS / "overlap_workflow_state.json"
OVERLAP_TRANSACTION = MANIFESTS / "overlap_transaction.json"
OVERLAP_RECOVERY_TRANSACTION = MANIFESTS / "overlap_offline_recovery_transaction.json"
OVERLAP_RECOVERY_PARENT = MANIFESTS / "overlap_offline_recovery_parent.json"
OVERLAP_RECOVERY_GATE = MANIFESTS / "overlap_offline_recovery_gate.json"
OVERLAP_RECOVERY_AUTHORIZATION = AUDITS / "M9_offline_recovery_authorization.md"
SOURCE_CONTROL_RECOVERY_TRANSACTION = MANIFESTS / "overlap_source_control_recovery.json"
SOURCE_CONTROL_RECOVERY_PARENT = MANIFESTS / "overlap_source_control_recovery_parent.json"
SOURCE_CONTROL_RECOVERY_GATE = MANIFESTS / "overlap_source_control_recovery_gate.json"
SOURCE_CONTROL_RECOVERY_FROZEN_HASHES = REPRODUCTION / "manifests/m9_source_control_recovery_frozen_hashes.json"
SOURCE_CONTROL_RECOVERY_AUTHORIZATION = AUDITS / "M9_source_prepare_control_recovery_authorization.md"
SOURCE_CONTROL_GATE_DISPOSITION_VERDICT = AUDITS / "M9_source_control_gate_disposition_final_verdict.json"
SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT = AUDITS / "M9_source_control_recovery_replacement_final_verdict.json"
SOURCE_CONTROL_GATE_INVALID_RETIRED = MANIFESTS / "overlap_source_control_recovery_gate.closed-set-invalid.retired.json"
SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL = Path("/root/deeph-m9-control/source-control-gate-disposition.json")
SOURCE_CONTROL_GATE_LOCK_REFRESH_VERDICT = AUDITS / "M9_source_control_gate_lock_refresh_final_verdict.json"
SOURCE_CONTROL_RECOVERY_LOCK_REPLACEMENT_VERDICT = AUDITS / "M9_source_control_recovery_lock_replacement_final_verdict.json"
SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED = MANIFESTS / "overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json"
SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL = Path("/root/deeph-m9-control/source-control-gate-lock-refresh.json")
SOURCE_CONTROL_POST_FAILURE_MIGRATION_VERDICT = AUDITS / "M9_source_control_post_failure_migration_final_verdict.json"
SOURCE_CONTROL_POST_FAILURE_REPLACEMENT_VERDICT = AUDITS / "M9_source_control_post_failure_replacement_final_verdict.json"
SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED = MANIFESTS / "overlap_source_control_recovery_gate.pre-ledger-fix.retired.json"
SOURCE_CONTROL_POST_FAILURE_JOURNAL = Path("/root/deeph-m9-control/source-control-post-failure-migration.json")
SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT = Path("/root/deeph-m9-control/source-control-failed-recovery-original.json")
SOURCE_CONTROL_POST_FAILURE_CONTRACT = REPRODUCTION / "manifests/m9_source_control_post_failure_contract.json"
UNLIMITED_WALL_CLOCK_AUTHORIZATION = AUDITS / "M9_unlimited_wall_clock_authorization.md"
UNLIMITED_WALL_CLOCK_CONTRACT = REPRODUCTION / "manifests/m9_unlimited_wall_clock_contract.json"
UNLIMITED_WALL_CLOCK_FROZEN_HASHES = REPRODUCTION / "manifests/m9_unlimited_wall_clock_frozen_hashes.json"
UNLIMITED_WALL_CLOCK_VERDICT = AUDITS / "M9_unlimited_wall_clock_migration_final_verdict.json"
UNLIMITED_WALL_CLOCK_WORK_PACKAGE = AUDITS / "M9_unlimited_wall_clock_migration_work_package.md"
UNLIMITED_WALL_CLOCK_GATE = MANIFESTS / "overlap_unlimited_wall_clock_gate.json"
UNLIMITED_WALL_CLOCK_TRANSACTION = MANIFESTS / "overlap_unlimited_wall_clock_transaction.json"
UNLIMITED_WALL_CLOCK_EXECUTION_GATE = MANIFESTS / "overlap_unlimited_wall_clock_execution_gate.json"
UNLIMITED_WALL_CLOCK_EXECUTION_VERDICT = AUDITS / "M9_unlimited_wall_clock_migration_execution_final_verdict.json"
UNLIMITED_WALL_CLOCK_EXECUTION_REPORT = AUDITS / "M9_unlimited_wall_clock_migration_execution_independent_audit.md"
UNLIMITED_WALL_CLOCK_JOURNAL = Path("/root/deeph-m9-control/unlimited-wall-clock-migration.json")
UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT = Path("/root/deeph-m9-control/unlimited-wall-clock-pre-state.json")
OVERLAP_AUDIT_GATE_PRE_D018_RETIRED = MANIFESTS / "overlap_work_package_audit_gate.pre-d018.retired.json"
SOURCE_CONTROL_TEST_ARTIFACT = MANIFESTS / "overlap_source_control_recovery.json"
SOURCE_CONTROL_TEST_ARTIFACT_RETIRED = MANIFESTS / "overlap_source_control_recovery.test-artifact.retired.json"
SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT = MANIFESTS / "overlap_source_control_test_artifact_retirement.json"
SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL = MANIFESTS / "overlap_source_control_test_artifact_cleanup.json"
SOURCE_CONTROL_TEST_CLEANUP_GATE = MANIFESTS / "overlap_source_control_test_cleanup_gate.json"
SOURCE_CONTROL_TEST_TRUST_ROOT = Path("/root/deeph-m9-control/source-control-test-cleanup")
SOURCE_CONTROL_TEST_GATE_SNAPSHOT = SOURCE_CONTROL_TEST_TRUST_ROOT / "cleanup_gate.verified.json"
SOURCE_CONTROL_TEST_SECURITY_MIGRATION = SOURCE_CONTROL_TEST_TRUST_ROOT / "security_migration.json"
SOURCE_CONTROL_TEST_CLEANUP_FROZEN = REPRODUCTION / "manifests/m9_source_control_test_cleanup_frozen_hashes.json"
SOURCE_CONTROL_TEST_CLEANUP_AUTH = AUDITS / "M9_source_control_test_artifact_cleanup_authorization.md"
OVERLAP_CAPABILITY_ROOT = MANIFESTS / "overlap_capabilities"
OVERLAP_CONTROL_DIRECTORY = REPRODUCTION / "scripts"
OFFLINE_APT_MANIFEST = REPRODUCTION / "manifests/m9_offline_apt_manifest.json"
OFFLINE_APT_ARCHIVE_ROOT = LINUX_ROOT / "downloads/apt-offline"
OFFLINE_RECOVERY_FROZEN_HASHES = REPRODUCTION / "manifests/m9_offline_recovery_frozen_hashes.json"
BOOTSTRAP_MODULE_NAMES = ("argparse", "hashlib", "json", "pathlib")
INVALID_SOURCE_CONTROL_GATE_SHA256 = "6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821"
INVALID_SOURCE_CONTROL_GATE_BYTES = 1711
PRE_LOCK_REFRESH_GATE_SHA256 = "5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936"
PRE_LOCK_REFRESH_GATE_BYTES = 1723
RECOVERY_REQUIRED_FILES = {
    OVERLAP_RECOVERY_AUTHORIZATION,
    REPRODUCTION / "scripts/m9_budget.py",
    OFFLINE_APT_MANIFEST,
    REPRODUCTION / "manifests/budget_contract.json",
    OVERLAP_CONTRACT,
    REPRODUCTION / "tests/test_m9_overlap_controls.py",
    AUDITS / "M9_overlap_only_openmx_work_package.md",
    OFFLINE_RECOVERY_FROZEN_HASHES,
    REPRODUCTION / "scripts/m9_compatibility_smoke.py",
    REPRODUCTION / "scripts/m9_dataset_archive.py",
    REPRODUCTION / "scripts/m9_data_contract.py",
    REPRODUCTION / "scripts/m9_openmx_build.py",
    REPRODUCTION / "scripts/m9_openmx_input.py",
    REPRODUCTION / "scripts/m9_openmx_source_inspect.py",
    REPRODUCTION / "scripts/m9_overlap_common.py",
    REPRODUCTION / "scripts/m9_overlap_contract.py",
    REPRODUCTION / "scripts/m9_overlap_executor.py",
    REPRODUCTION / "scripts/m9_overlap_source_launcher.py",
    REPRODUCTION / "scripts/m9_range_download.py",
}
SOURCE_RECOVERY_PRODUCTS = (
    LINUX_ROOT / "software/openmx-overlap-build",
    LINUX_ROOT / "software/openmx-overlap-build.staging",
    LINUX_ROOT / "env/hdf5-1.12.1",
    LINUX_ROOT / "manifests/openmx_official_3.9.9_tree_manifest.json",
    LINUX_ROOT / "manifests/openmx_overlap_tree_manifest.json",
    LINUX_ROOT / "manifests/openmx_overlap_build_manifest.json",
)
SOURCE_RECOVERY_CONTROL_FILES = {
    REPRODUCTION / "scripts/m9_budget.py",
    REPRODUCTION / "tests/test_m9_overlap_controls.py",
    REPRODUCTION / "configs/m9_overlap_only_contract.json",
    REPRODUCTION / "scripts/m9_overlap_source_launcher.py",
    REPRODUCTION / "scripts/m9_overlap_common.py",
    REPRODUCTION / "scripts/m9_overlap_contract.py",
    REPRODUCTION / "scripts/m9_overlap_executor.py",
    REPRODUCTION / "scripts/m9_openmx_build.py",
    REPRODUCTION / "scripts/m9_openmx_input.py",
    REPRODUCTION / "scripts/m9_openmx_source_inspect.py",
    REPRODUCTION / "scripts/m9_data_contract.py",
    REPRODUCTION / "scripts/m9_dataset_archive.py",
    REPRODUCTION / "scripts/m9_compatibility_smoke.py",
    REPRODUCTION / "scripts/m9_range_download.py",
    REPRODUCTION / "manifests/budget_contract.json",
    REPRODUCTION / "manifests/m9_offline_apt_manifest.json",
    REPRODUCTION / "manifests/m9_offline_recovery_frozen_hashes.json",
    SOURCE_CONTROL_POST_FAILURE_CONTRACT,
    SOURCE_CONTROL_RECOVERY_AUTHORIZATION,
}

UNLIMITED_WALL_CLOCK_CONTROL_FILES = {
    REPRODUCTION / "scripts/m9_budget.py",
    REPRODUCTION / "tests/test_m9_overlap_controls.py",
    REPRODUCTION / "configs/m9_overlap_only_contract.json",
    REPRODUCTION / "scripts/m9_overlap_source_launcher.py",
    REPRODUCTION / "scripts/m9_overlap_common.py",
    REPRODUCTION / "scripts/m9_overlap_contract.py",
    REPRODUCTION / "scripts/m9_overlap_executor.py",
    REPRODUCTION / "scripts/m9_openmx_build.py",
    REPRODUCTION / "scripts/m9_openmx_input.py",
    REPRODUCTION / "scripts/m9_openmx_source_inspect.py",
    REPRODUCTION / "scripts/m9_data_contract.py",
    REPRODUCTION / "scripts/m9_dataset_archive.py",
    REPRODUCTION / "scripts/m9_compatibility_smoke.py",
    REPRODUCTION / "scripts/m9_range_download.py",
    REPRODUCTION / "manifests/budget_contract.json",
    REPRODUCTION / "manifests/openmx_overlap_source_manifest.json",
    REPRODUCTION / "manifests/m9_overlap_frozen_hashes.json",
    UNLIMITED_WALL_CLOCK_CONTRACT,
    UNLIMITED_WALL_CLOCK_AUTHORIZATION,
    OVERLAP_WORK_PACKAGE,
    UNLIMITED_WALL_CLOCK_WORK_PACKAGE,
    AUDITS / "M9_unlimited_wall_clock_migration_independent_audit.md",
    AUDITS / "M9_unlimited_wall_clock_migration_targeted_reaudit.md",
    AUDITS / "M9_source_control_recovery_resume_execution_independent_audit.md",
    PROJECT_ROOT / "decisions.md",
    PROJECT_ROOT / "00_scope/master_execution_plan.md",
    PROJECT_ROOT / "08_audits/progress_tracker.md",
}

HISTORICAL_WALL_LIMIT = 604800.0


class D018SimulatedPowerLoss(RuntimeError):
    """Test-only analogue of process death; callers must not convert it to a failure commit."""
GPU_LIMITS = {
    "compatibility": 7200.0,
    "training": 57600.0,
    "physical_validation": 21600.0,
}
GPU_TOTAL_LIMIT = 86400.0
CPU_LIMITS = {
    "overlap_build": 7200.0,
    "overlap_smoke": 1800.0,
    "overlap_batch": 21600.0,
}
OFFLINE_RECOVERY_LIMIT = 300.0
STORAGE_LIMIT = 107374182400
PROJECT_SUBLIMIT = 1073741824
OVERLAP_STORAGE_LIMIT = 10737418240
FROZEN_START = "2026-08-11T14:50:05.7533015Z"
FROZEN_DEADLINE = "2026-08-18T14:50:05.7533015Z"
FROZEN_VHDX_BASELINE = 1488977920
OVERLAP_APT_COMMAND = [
    "/usr/bin/apt-get",
    "install",
    "--yes",
    "--no-install-recommends",
    "openmpi-bin=4.1.2-2ubuntu1",
    "libopenmpi-dev=4.1.2-2ubuntu1",
    "libscalapack-openmpi-dev=2.1.0-4",
    "libfftw3-dev=3.3.8-2ubuntu8",
    "libblas-dev=3.10.0-2ubuntu1",
    "liblapack-dev=3.10.0-2ubuntu1",
    "gfortran=4:11.2.0-1ubuntu1",
    "make=4.3-4.1build1",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    normalized = re.sub(r"(\.\d{6})\d+(?=[+-]\d\d:\d\d$)", r"\1", normalized)
    return dt.datetime.fromisoformat(normalized)


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def isolated_bootstrap_provenance() -> dict[str, object]:
    actual_python = Path(sys.executable).resolve(strict=True)
    expected_python = OVERLAP_PYTHON.resolve(strict=True)
    if actual_python != expected_python:
        raise SystemExit(
            f"formal overlap entry requires frozen Python: {actual_python} != {expected_python}"
        )
    if not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise SystemExit("formal overlap entry requires frozen Python with -I -S -B")
    script_directory = Path(__file__).resolve().parent
    current_directory = Path.cwd().resolve()
    resolved_sys_path = []
    for raw in sys.path:
        if not raw:
            raise SystemExit("empty current-directory entry is forbidden on formal sys.path")
        resolved = Path(raw).resolve(strict=False)
        if resolved in (script_directory, current_directory):
            raise SystemExit("script/current directory is forbidden on formal sys.path")
        if "site-packages" in resolved.parts:
            raise SystemExit("site-packages is forbidden on formal bootstrap sys.path")
        resolved_sys_path.append(resolved.as_posix())
    stdlib_root = Path(sys.prefix) / f"lib/python{sys.version_info.major}.{sys.version_info.minor}"
    modules: dict[str, object] = {}
    for name in BOOTSTRAP_MODULE_NAMES:
        module = sys.modules.get(name)
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        loader = getattr(spec, "loader", None)
        if not isinstance(origin, str) or origin in ("built-in", "frozen"):
            raise SystemExit(f"bootstrap module lacks frozen stdlib source origin: {name}")
        resolved_origin = Path(origin).resolve(strict=True)
        if stdlib_root.resolve() not in resolved_origin.parents or "site-packages" in resolved_origin.parts:
            raise SystemExit(f"bootstrap module escaped frozen stdlib: {name} -> {resolved_origin}")
        modules[name] = {
            "loader": type(loader).__name__,
            "origin": resolved_origin.as_posix(),
            "sha256": hashlib.sha256(resolved_origin.read_bytes()).hexdigest(),
        }
    return {
        "isolated": True,
        "no_site": True,
        "dont_write_bytecode": True,
        "python_executable": actual_python.as_posix(),
        "sys_path": resolved_sys_path,
        "modules": modules,
    }


def verify_overlap_control_directory(frozen: dict[str, object]) -> None:
    files = frozen.get("files")
    if not isinstance(files, dict):
        raise SystemExit("overlap frozen hash manifest lacks files")
    allowed_python = {
        Path(str(path)).name
        for path in files
        if Path(str(path)).parent.resolve(strict=False) == OVERLAP_CONTROL_DIRECTORY.resolve(strict=False)
        and Path(str(path)).suffix == ".py"
    }
    actual_python: set[str] = set()
    for entry in OVERLAP_CONTROL_DIRECTORY.iterdir():
        if entry.is_symlink() or entry.is_dir() or entry.suffix in (".pyc", ".pyo"):
            raise SystemExit(f"cache, symlink, or subdirectory forbidden in control directory: {entry}")
        if entry.suffix != ".py" or entry.name not in allowed_python:
            raise SystemExit(f"unfrozen control-directory file: {entry}")
        actual_python.add(entry.name)
    if actual_python != allowed_python:
        raise SystemExit("frozen control-directory Python file set mismatch")


def path_usage(path: Path) -> tuple[int, int]:
    """Return apparent and allocated bytes without following symlinks."""
    if not path.exists() and not path.is_symlink():
        return 0, 0
    apparent = 0
    allocated = 0
    paths: Iterable[Path]
    if path.is_dir() and not path.is_symlink():
        paths = (Path(root) / name for root, dirs, files in os.walk(path, followlinks=False)
                 for name in files)
    else:
        paths = (path,)
    for item in paths:
        try:
            stat = item.lstat()
        except FileNotFoundError:
            continue
        apparent += stat.st_size
        allocated += stat.st_blocks * 512
    return apparent, allocated


def project_usage() -> tuple[int, int]:
    apparent, allocated = path_usage(REPRODUCTION)
    if AUDITS.exists():
        for item in AUDITS.iterdir():
            if item.is_file() and item.name.startswith("M9_"):
                a, b = path_usage(item)
                apparent += a
                allocated += b
    for item in CONTROL_FILES:
        a, b = path_usage(item)
        apparent += a
        allocated += b
    return apparent, allocated


def storage_snapshot(state: dict) -> dict:
    linux_a, linux_b = path_usage(LINUX_ROOT)
    project_a, project_b = project_usage()
    vhdx_size = None
    vhdx_growth = None
    try:
        vhdx_size = HOST_VHDX.stat().st_size
        vhdx_growth = max(0, vhdx_size - int(state["vhdx_baseline_bytes"]))
    except OSError:
        pass
    snapshot = {
        "linux_apparent_bytes": linux_a,
        "linux_allocated_bytes": linux_b,
        "project_audit_apparent_bytes": project_a,
        "project_audit_allocated_bytes": project_b,
        "combined_apparent_bytes": linux_a + project_a,
        "combined_allocated_bytes": linux_b + project_b,
        "host_vhdx_bytes": vhdx_size,
        "host_vhdx_growth_from_start_bytes": vhdx_growth,
    }
    baseline = state.get("overlap_storage_baseline")
    if isinstance(baseline, dict):
        snapshot["combined_apparent_bytes_since_overlap_baseline"] = max(
            0, snapshot["combined_apparent_bytes"] - int(baseline["combined_apparent_bytes"])
        )
        snapshot["combined_allocated_bytes_since_overlap_baseline"] = max(
            0, snapshot["combined_allocated_bytes"] - int(baseline["combined_allocated_bytes"])
        )
        current_vhdx = snapshot["host_vhdx_bytes"]
        baseline_vhdx = baseline.get("host_vhdx_bytes")
        snapshot["host_vhdx_growth_since_overlap_baseline_bytes"] = (
            None
            if current_vhdx is None or baseline_vhdx is None
            else max(0, int(current_vhdx) - int(baseline_vhdx))
        )
    return snapshot


def preserve_owner(path: Path) -> None:
    if os.geteuid() == 0:
        os.chown(path, 1000, 1000)


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preserve_owner(tmp)
    os.replace(tmp, path)
    preserve_owner(path)


def atomic_owned_durable_bytes(
    path: Path,
    payload: bytes,
    *,
    expected_uid: int = 1000,
    expected_gid: int = 1000,
    expected_mode: int = 0o644,
) -> None:
    """Durably replace one fixed-owner runtime file and resume a stale temp safely."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(tmp, flags, expected_mode)
        os.fchmod(descriptor, expected_mode)
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            os.fchown(descriptor, expected_uid, expected_gid)
    except FileExistsError:
        resume_flags = os.O_WRONLY | getattr(os, "O_CLOEXEC", 0)
        if hasattr(os, "O_NOFOLLOW"):
            resume_flags |= os.O_NOFOLLOW
        descriptor = os.open(tmp, resume_flags)
        current = os.fstat(descriptor)
        root_created_empty = (
            hasattr(os, "geteuid")
            and os.geteuid() == 0
            and current.st_uid == 0
            and current.st_gid == 0
            and current.st_size == 0
        )
        if (
            not stat.S_ISREG(current.st_mode)
            or current.st_nlink != 1
            or not root_created_empty
            and (
                current.st_uid != expected_uid
                or current.st_gid != expected_gid
                or stat.S_IMODE(current.st_mode) != expected_mode
            )
        ):
            os.close(descriptor)
            raise ValueError("owned atomic temporary metadata mismatch")
        if root_created_empty:
            os.fchmod(descriptor, expected_mode)
            os.fchown(descriptor, expected_uid, expected_gid)
    try:
        os.ftruncate(descriptor, 0)
        written = os.write(descriptor, payload)
        if written != len(payload):
            raise OSError("owned atomic write was short")
        os.fsync(descriptor)
        committed = os.fstat(descriptor)
        linked = os.lstat(tmp)
        stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if (
            any(getattr(committed, key) != getattr(linked, key) for key in stable)
            or committed.st_uid != expected_uid
            or committed.st_gid != expected_gid
            or stat.S_IMODE(committed.st_mode) != expected_mode
            or committed.st_nlink != 1
            or committed.st_size != len(payload)
        ):
            raise ValueError("owned atomic temporary changed during write")
    finally:
        os.close(descriptor)
    os.replace(tmp, path)
    final = os.lstat(path)
    if (
        not stat.S_ISREG(final.st_mode)
        or final.st_uid != expected_uid
        or final.st_gid != expected_gid
        or stat.S_IMODE(final.st_mode) != expected_mode
        or final.st_nlink != 1
        or final.st_size != len(payload)
        or hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(payload).digest()
    ):
        raise ValueError("owned atomic committed file mismatch")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def atomic_owned_json(path: Path, value: dict) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    atomic_owned_durable_bytes(path, payload)


def atomic_private_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    os.chmod(path, 0o600)
    preserve_owner(path)


def atomic_private_durable_bytes(path: Path, payload: bytes, expected_uid: int, expected_gid: int) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(tmp, flags, 0o600)
    except FileExistsError:
        resume_flags = os.O_WRONLY
        if hasattr(os, "O_NOFOLLOW"):
            resume_flags |= os.O_NOFOLLOW
        try:
            fd = os.open(tmp, resume_flags)
        except OSError as exc:
            raise SystemExit("root-private atomic temporary file mismatch") from exc
        current = os.fstat(fd)
        if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1 or current.st_uid != expected_uid or current.st_gid != expected_gid or (current.st_mode & 0o7777) != 0o600:
            os.close(fd)
            raise SystemExit("root-private atomic temporary file mismatch")
    os.ftruncate(fd, 0)
    with os.fdopen(fd, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        written = os.fstat(handle.fileno())
    current = os.lstat(tmp)
    if (
        current.st_dev != written.st_dev
        or current.st_ino != written.st_ino
        or current.st_uid != expected_uid
        or current.st_gid != expected_gid
        or (current.st_mode & 0o7777) != 0o600
        or current.st_nlink != 1
        or tmp.read_bytes() != payload
    ):
        raise SystemExit("root-private atomic temporary metadata mismatch")
    os.replace(tmp, path)
    current = os.lstat(path)
    if current.st_uid != expected_uid or current.st_gid != expected_gid or (current.st_mode & 0o7777) != 0o600 or current.st_nlink != 1 or path.read_bytes() != payload:
        raise SystemExit("root-private atomic committed metadata mismatch")
    with path.open("rb") as handle:
        os.fsync(handle.fileno())
    directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def atomic_root_private_bytes(path: Path, payload: bytes) -> None:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("root-private atomic write requires root")
    atomic_private_durable_bytes(path, payload, 0, 0)


def atomic_root_private_json(path: Path, value: dict) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    atomic_root_private_bytes(path, payload)


def append_existing_regular_bytes(
    path: Path,
    payload: bytes,
    *,
    expected_uid: int = 1000,
    expected_gid: int = 1000,
    expected_mode: int = 0o644,
    expected_prefix_bytes: int | None = None,
    expected_prefix_sha256: str | None = None,
) -> None:
    """Append to one already-existing ledger inode without requesting O_CREAT."""
    try:
        linked_before = os.lstat(path)
    except OSError as exc:
        raise ValueError("append target must already exist") from exc
    if (
        not stat.S_ISREG(linked_before.st_mode)
        or stat.S_ISLNK(linked_before.st_mode)
        or linked_before.st_uid != expected_uid
        or linked_before.st_gid != expected_gid
        or stat.S_IMODE(linked_before.st_mode) != expected_mode
        or linked_before.st_nlink != 1
    ):
        raise ValueError("append target metadata mismatch")
    flags = os.O_RDWR | os.O_APPEND | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink")
        if any(getattr(opened, key) != getattr(linked_before, key) for key in stable):
            raise ValueError("append target changed before open")
        if expected_prefix_bytes is not None or expected_prefix_sha256 is not None:
            if expected_prefix_bytes is None or expected_prefix_sha256 is None:
                raise ValueError("append prefix binding is incomplete")
            if opened.st_size != expected_prefix_bytes:
                raise ValueError("append prefix size mismatch")
            offset = 0
            digest = hashlib.sha256()
            while offset < expected_prefix_bytes:
                chunk = os.pread(descriptor, min(1024 * 1024, expected_prefix_bytes - offset), offset)
                if not chunk:
                    raise ValueError("append prefix ended early")
                digest.update(chunk)
                offset += len(chunk)
            if digest.hexdigest() != expected_prefix_sha256:
                raise ValueError("append prefix SHA-256 mismatch")
        written = os.write(descriptor, payload)
        if written != len(payload):
            os.ftruncate(descriptor, opened.st_size)
            os.fsync(descriptor)
            raise OSError("ledger append was short")
        os.fsync(descriptor)
        if expected_prefix_bytes is not None and expected_prefix_sha256 is not None:
            offset = 0
            post_digest = hashlib.sha256()
            while offset < expected_prefix_bytes:
                chunk = os.pread(descriptor, min(1024 * 1024, expected_prefix_bytes - offset), offset)
                if not chunk:
                    raise ValueError("append prefix ended early after write")
                post_digest.update(chunk)
                offset += len(chunk)
            if post_digest.hexdigest() != expected_prefix_sha256:
                raise ValueError("append prefix changed during write")
        opened_after = os.fstat(descriptor)
        linked_after = os.lstat(path)
        if (
            any(getattr(opened_after, key) != getattr(opened, key) for key in stable)
            or any(getattr(linked_after, key) != getattr(opened_after, key) for key in stable)
            or opened_after.st_size != opened.st_size + len(payload)
            or linked_after.st_size != opened_after.st_size
        ):
            raise ValueError("append target changed during commit")
    finally:
        os.close(descriptor)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def create_initial_ledger(payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(LEDGER_PATH, flags, 0o644)
    try:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            os.fchown(descriptor, 1000, 1000)
        written = os.write(descriptor, payload)
        if written != len(payload):
            raise OSError("initial ledger write was short")
        os.fsync(descriptor)
        current = os.fstat(descriptor)
        if (
            not stat.S_ISREG(current.st_mode)
            or current.st_uid != 1000
            or current.st_gid != 1000
            or stat.S_IMODE(current.st_mode) != 0o644
            or current.st_nlink != 1
            or current.st_size != len(payload)
        ):
            raise ValueError("initial ledger metadata mismatch")
    finally:
        os.close(descriptor)


def resume_partial_existing_append(
    path: Path,
    *,
    prefix_bytes: int,
    prefix_sha256: str,
    expected_suffix: bytes,
    expected_uid: int = 1000,
    expected_gid: int = 1000,
    expected_mode: int = 0o644,
) -> bool:
    """Rollback only an exact proper prefix of the one frozen append payload."""
    flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_uid != expected_uid
            or opened.st_gid != expected_gid
            or stat.S_IMODE(opened.st_mode) != expected_mode
            or opened.st_nlink != 1
            or opened.st_size <= prefix_bytes
        ):
            return False
        payload = bytearray()
        offset = 0
        while offset < opened.st_size:
            chunk = os.pread(descriptor, min(1024 * 1024, opened.st_size - offset), offset)
            if not chunk:
                return False
            payload.extend(chunk)
            offset += len(chunk)
        prefix = bytes(payload[:prefix_bytes])
        suffix = bytes(payload[prefix_bytes:])
        if (
            hashlib.sha256(prefix).hexdigest() != prefix_sha256
            or not suffix
            or len(suffix) >= len(expected_suffix)
            or not expected_suffix.startswith(suffix)
        ):
            return False
        os.ftruncate(descriptor, prefix_bytes)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        linked = os.lstat(path)
        fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink")
        if (
            after.st_size != prefix_bytes
            or any(getattr(after, key) != getattr(opened, key) for key in fields)
            or any(getattr(linked, key) != getattr(after, key) for key in fields)
        ):
            raise ValueError("partial ledger append rollback metadata mismatch")
    finally:
        os.close(descriptor)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return True


def append_event(
    event: dict,
    *,
    allow_create: bool = False,
    expected_prefix_bytes: int | None = None,
    expected_prefix_sha256: str | None = None,
) -> None:
    payload = (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if not LEDGER_PATH.exists():
        if not allow_create:
            raise ValueError("budget ledger is missing")
        create_initial_ledger(payload)
        return
    append_existing_regular_bytes(
        LEDGER_PATH,
        payload,
        expected_prefix_bytes=expected_prefix_bytes,
        expected_prefix_sha256=expected_prefix_sha256,
    )


def ledger_event_ids_from_bytes(payload_bytes: bytes) -> dict[str, str]:
    ids: dict[str, str] = {}
    try:
        lines = payload_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("budget ledger is not UTF-8") from exc
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("budget ledger contains invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError("budget ledger event is not an object")
        if value.get("event_id"):
            event_id = str(value["event_id"])
            payload = dict(value)
            payload.pop("event_id", None)
            event_hash = canonical_hash(payload)
            if event_id in ids:
                raise ValueError("budget ledger contains duplicate event_id")
            ids[event_id] = event_hash
    return ids


def ledger_event_ids() -> dict[str, str]:
    if not LEDGER_PATH.exists():
        return {}
    return ledger_event_ids_from_bytes(LEDGER_PATH.read_bytes())


def append_event_once(
    event: dict,
    *,
    expected_prefix_bytes: int | None = None,
    expected_prefix_sha256: str | None = None,
) -> None:
    event_id = str(event.get("event_id", ""))
    if not event_id:
        raise ValueError("ledger event requires event_id")
    payload = dict(event)
    payload.pop("event_id", None)
    event_hash = canonical_hash(payload)
    existing = ledger_event_ids()
    if event_id in existing:
        if existing[event_id] != event_hash:
            raise ValueError("ledger event ID payload mismatch")
        return
    if event_id not in existing:
        append_event(
            event,
            expected_prefix_bytes=expected_prefix_bytes,
            expected_prefix_sha256=expected_prefix_sha256,
        )


def canonical_ledger_event_bytes(event: dict) -> bytes:
    return (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def commit_exact_existing_ledger_event(
    event: dict,
    *,
    prefix_bytes: int,
    prefix_sha256: str,
) -> dict[str, object]:
    """Commit one exact event after one frozen prefix, including partial-write recovery."""
    suffix = canonical_ledger_event_bytes(event)
    receipt, current = read_stable_regular_bytes(LEDGER_PATH)
    if len(current) < prefix_bytes:
        raise SystemExit("D-018 ledger is shorter than the frozen prefix")
    prefix = current[:prefix_bytes]
    tail = current[prefix_bytes:]
    if hashlib.sha256(prefix).hexdigest() != prefix_sha256:
        raise SystemExit("D-018 ledger prefix drift")
    if tail == b"":
        append_existing_regular_bytes(
            LEDGER_PATH,
            suffix,
            expected_prefix_bytes=prefix_bytes,
            expected_prefix_sha256=prefix_sha256,
        )
    elif tail == suffix:
        pass
    elif 0 < len(tail) < len(suffix) and suffix.startswith(tail):
        if not resume_partial_existing_append(
            LEDGER_PATH,
            prefix_bytes=prefix_bytes,
            prefix_sha256=prefix_sha256,
            expected_suffix=suffix,
        ):
            raise SystemExit("D-018 partial ledger event cannot be rolled back")
        append_existing_regular_bytes(
            LEDGER_PATH,
            suffix,
            expected_prefix_bytes=prefix_bytes,
            expected_prefix_sha256=prefix_sha256,
        )
    else:
        raise SystemExit("D-018 ledger tail is not the authorized event")
    final_receipt, final = read_stable_regular_bytes(LEDGER_PATH)
    expected = prefix + suffix
    if final != expected:
        raise SystemExit("D-018 ledger exact event commit mismatch")
    event_ids = ledger_event_ids_from_bytes(final)
    event_id = str(event.get("event_id", ""))
    payload = dict(event)
    payload.pop("event_id", None)
    if event_ids.get(event_id) != canonical_hash(payload):
        raise SystemExit("D-018 ledger event payload mismatch")
    return {
        "path": LEDGER_PATH.as_posix(),
        "prefix_bytes": prefix_bytes,
        "prefix_sha256": prefix_sha256,
        "event_bytes": len(suffix),
        "event_sha256": hashlib.sha256(suffix).hexdigest(),
        "final_bytes": len(final),
        "final_sha256": final_receipt["sha256"],
    }


def initial_state() -> dict:
    return {
        "schema_version": "m9-budget-state-v1",
        "start_utc": FROZEN_START,
        "deadline_utc": FROZEN_DEADLINE,
        "vhdx_baseline_bytes": FROZEN_VHDX_BASELINE,
        "gpu_seconds": {name: 0.0 for name in GPU_LIMITS},
        "cpu_seconds": {name: 0.0 for name in CPU_LIMITS},
        "cpu_adjustments": [],
        "offline_recovery_seconds": 0.0,
        "last_event_utc": FROZEN_START,
        "hard_stopped": False,
    }


def load_state() -> dict:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state.setdefault("cpu_seconds", {name: 0.0 for name in CPU_LIMITS})
    for name in CPU_LIMITS:
        state["cpu_seconds"].setdefault(name, 0.0)
    state.setdefault("cpu_adjustments", [])
    state.setdefault("offline_recovery_seconds", 0.0)
    return state


def effective_cpu_seconds(state: dict, bucket: str) -> float:
    raw = float(state["cpu_seconds"][bucket])
    credited = 0.0
    for adjustment in state.get("cpu_adjustments", []):
        if adjustment.get("bucket") == bucket:
            credited += float(adjustment.get("credited_seconds", 0.0))
    return max(0.0, raw - credited)


def wall_clock_policy_mode(state: dict) -> str:
    policy = state.get("wall_clock_policy")
    if policy is None:
        return "LIMITED"
    if not isinstance(policy, dict):
        return "INVALID"
    required = {
        "mode": "UNLIMITED",
        "decision_id": "D-018",
        "historical_limit_seconds": HISTORICAL_WALL_LIMIT,
        "historical_start_utc": FROZEN_START,
        "historical_deadline_utc": FROZEN_DEADLINE,
    }
    if any(policy.get(key) != value for key, value in required.items()):
        return "INVALID"
    for key in (
        "migration_transaction_id",
        "migration_event_id",
        "authorization_sha256",
        "contract_sha256",
        "gate_sha256",
    ):
        value = policy.get(key)
        if not isinstance(value, str) or not value:
            return "INVALID"
    for key in ("authorization_sha256", "contract_sha256", "gate_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(policy[key])):
            return "INVALID"
    if state.get("start_utc") != FROZEN_START or state.get("deadline_utc") != FROZEN_DEADLINE:
        return "INVALID"
    return "UNLIMITED"


def deadline_remaining(state: dict) -> float | None:
    if wall_clock_policy_mode(state) == "UNLIMITED":
        return None
    return (parse_utc(state["deadline_utc"]) - dt.datetime.now(dt.timezone.utc)).total_seconds()


def violations(state: dict, forecast_bytes: int = 0) -> list[str]:
    result: list[str] = []
    if forecast_bytes < 0:
        result.append("negative_forecast_bytes")
    if state.get("hard_stopped"):
        result.append("ledger_already_hard_stopped")
    mode = wall_clock_policy_mode(state)
    remaining = deadline_remaining(state)
    if mode == "INVALID":
        result.append("wall_clock_policy_invalid")
    elif remaining is not None and remaining <= 0:
        result.append("wall_clock_limit")
    snap = storage_snapshot(state)
    if snap["project_audit_apparent_bytes"] > PROJECT_SUBLIMIT:
        result.append("project_audit_sublimit")
    for key in ("combined_apparent_bytes", "combined_allocated_bytes"):
        if snap[key] + forecast_bytes > STORAGE_LIMIT:
            result.append(key)
    growth = snap["host_vhdx_growth_from_start_bytes"]
    if growth is not None and growth + forecast_bytes > STORAGE_LIMIT:
        result.append("host_vhdx_growth_from_start_bytes")
    if isinstance(state.get("overlap_storage_baseline"), dict):
        for key in (
            "combined_apparent_bytes_since_overlap_baseline",
            "combined_allocated_bytes_since_overlap_baseline",
        ):
            if int(snap[key]) + forecast_bytes > OVERLAP_STORAGE_LIMIT:
                result.append(key)
        overlap_vhdx = snap.get("host_vhdx_growth_since_overlap_baseline_bytes")
        if overlap_vhdx is not None and int(overlap_vhdx) + forecast_bytes > OVERLAP_STORAGE_LIMIT:
            result.append("host_vhdx_growth_since_overlap_baseline_bytes")
    for bucket, limit in GPU_LIMITS.items():
        if float(state["gpu_seconds"][bucket]) >= limit:
            result.append(f"gpu_bucket_{bucket}")
    if sum(float(x) for x in state["gpu_seconds"].values()) >= GPU_TOTAL_LIMIT:
        result.append("gpu_total")
    for bucket, limit in CPU_LIMITS.items():
        if effective_cpu_seconds(state, bucket) >= limit:
            result.append(f"cpu_bucket_{bucket}")
    return result


def hard_stop(state: dict, reasons: list[str], command_hash: str | None = None) -> None:
    state["hard_stopped"] = True
    state["last_event_utc"] = utc_now()
    atomic_json(STATE_PATH, state)
    append_event({
        "event": "HARD_STOP",
        "utc": state["last_event_utc"],
        "reasons": reasons,
        "command_sha256": command_hash,
        "storage": storage_snapshot(state),
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
    })


def command_init(_: argparse.Namespace) -> int:
    for name in ("software", "data/downloads", "data/graphene", "env", "runs", "manifests", "logs"):
        (LINUX_ROOT / name).mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists() or LEDGER_PATH.exists():
        raise SystemExit("budget state already exists; refusing to reinitialize")
    state = initial_state()
    atomic_json(STATE_PATH, state)
    snap = storage_snapshot(state)
    append_event({
        "event": "BUDGET_START",
        "utc": FROZEN_START,
        "deadline_utc": FROZEN_DEADLINE,
        "storage": snap,
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
    }, allow_create=True)
    print(json.dumps({"status": "initialized", "storage": snap}, sort_keys=True))
    return 0


def command_status(_: argparse.Namespace) -> int:
    state = load_state()
    payload = {
        "wall_clock_mode": wall_clock_policy_mode(state),
        "historical_deadline_utc": state.get("deadline_utc"),
        "deadline_remaining_seconds": deadline_remaining(state),
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
        "storage": storage_snapshot(state),
        "violations": violations(state),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if not payload["violations"] else 2


def verify_overlap_gate_and_hashes() -> tuple[dict, dict]:
    gate = json.loads(OVERLAP_AUDIT_GATE.read_text(encoding="utf-8"))
    if (
        gate.get("schema_version") != "m9-overlap-audit-gate-v1"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("overlap audit gate is not PASS with zero issues")
    frozen = json.loads(OVERLAP_FROZEN_HASHES.read_text(encoding="utf-8"))
    if hashlib.sha256(OVERLAP_FROZEN_HASHES.read_bytes()).hexdigest() != gate.get(
        "frozen_hashes_sha256"
    ):
        raise SystemExit("overlap audit gate does not bind frozen hashes")
    if hashlib.sha256(OVERLAP_WORK_PACKAGE.read_bytes()).hexdigest() != gate.get(
        "work_package_sha256"
    ):
        raise SystemExit("overlap audit gate does not bind the work package")
    audit_report = Path(str(gate.get("audit_report_path", "")))
    if (
        Path(str(gate.get("work_package_path", ""))).resolve(strict=False)
        != OVERLAP_WORK_PACKAGE.resolve(strict=False)
        or not audit_report.is_file()
        or hashlib.sha256(audit_report.read_bytes()).hexdigest()
        != gate.get("audit_report_sha256")
    ):
        raise SystemExit("overlap audit gate object paths or report hash differ")
    if hashlib.sha256(OVERLAP_CONTRACT.read_bytes()).hexdigest() != frozen.get(
        "contract_sha256"
    ):
        raise SystemExit("overlap contract does not match frozen hashes")
    files = frozen.get("files")
    if not isinstance(files, dict):
        raise SystemExit("overlap frozen hash manifest lacks files")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"frozen overlap project file mismatch: {path}")
    verify_overlap_control_directory(frozen)
    return gate, frozen


def verify_recovery_gate_and_hashes() -> dict:
    """Validate the post-audit recovery gate; the old overlap gate is insufficient."""
    if not OVERLAP_RECOVERY_GATE.is_file():
        raise SystemExit("offline recovery gate is missing; independent re-audit is required")
    gate = json.loads(OVERLAP_RECOVERY_GATE.read_text(encoding="utf-8"))
    if (
        gate.get("schema_version") != "m9-overlap-offline-recovery-gate-v1"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("offline recovery gate is not PASS with zero issues")
    report = Path(str(gate.get("audit_report_path", ""))).resolve(strict=False)
    audits_root = AUDITS.resolve(strict=False)
    if report.parent != audits_root or report.suffix.lower() != ".json":
        raise SystemExit("source-control audit report must be the frozen JSON report directly under 08_audits")
    if not report.is_file() or hashlib.sha256(report.read_bytes()).hexdigest() != gate.get("audit_report_sha256"):
        raise SystemExit("offline recovery gate audit report hash mismatch")
    if gate.get("decision_id") != "D-017-offline-recovery-v1":
        raise SystemExit("offline recovery gate decision ID mismatch")
    report = Path(str(gate.get("audit_report_path", ""))).resolve(strict=False)
    if AUDITS.resolve(strict=False) not in report.parents:
        raise SystemExit("offline recovery gate audit report must be inside the audit directory")
    report_payload = json.loads(report.read_text(encoding="utf-8")) if report.suffix == ".json" else None
    if not isinstance(report_payload, dict) or report_payload.get("verdict") != "PASS" or int(report_payload.get("blocking", -1)) != 0 or int(report_payload.get("non_blocking", -1)) != 0:
        raise SystemExit("offline recovery gate report lacks structured zero-issue PASS verdict")
    files = gate.get("files")
    if not isinstance(files, dict) or set(Path(str(p)).resolve(strict=False) for p in files) != {
        p.resolve(strict=False) for p in RECOVERY_REQUIRED_FILES
    }:
        raise SystemExit("offline recovery gate file set is not the required closed set")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != str(expected):
            raise SystemExit(f"offline recovery frozen file mismatch: {path}")
    auth_sha = hashlib.sha256(OVERLAP_RECOVERY_AUTHORIZATION.read_bytes()).hexdigest()
    if gate.get("authorization_record_path") != OVERLAP_RECOVERY_AUTHORIZATION.as_posix() or gate.get("authorization_record_sha256") != auth_sha:
        raise SystemExit("offline recovery authorization record is not bound by gate")
    frozen_path = OFFLINE_RECOVERY_FROZEN_HASHES.as_posix()
    if gate.get("frozen_hashes_path") != frozen_path or not OFFLINE_RECOVERY_FROZEN_HASHES.is_file():
        raise SystemExit("offline recovery gate lacks the complete frozen hash manifest")
    frozen = json.loads(OFFLINE_RECOVERY_FROZEN_HASHES.read_text(encoding="utf-8"))
    frozen_files = frozen.get("files")
    gate_files_without_manifest = {
        key: value for key, value in files.items()
        if Path(str(key)).resolve(strict=False) != OFFLINE_RECOVERY_FROZEN_HASHES.resolve(strict=False)
    }
    if gate.get("frozen_hashes_sha256") != hashlib.sha256(OFFLINE_RECOVERY_FROZEN_HASHES.read_bytes()).hexdigest() or frozen_files != gate_files_without_manifest:
        raise SystemExit("offline recovery gate frozen hash binding mismatch")
    return gate


def verify_recovered_overlap_gate_and_hashes() -> tuple[dict, dict]:
    gate = verify_recovery_gate_and_hashes()
    frozen = json.loads(OFFLINE_RECOVERY_FROZEN_HASHES.read_text(encoding="utf-8"))
    if frozen.get("schema_version") != "m9-overlap-recovery-frozen-hashes-v1":
        raise SystemExit("offline recovery frozen hash schema mismatch")
    files = frozen.get("files")
    if not isinstance(files, dict):
        raise SystemExit("offline recovery frozen hashes lack files")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != str(expected):
            raise SystemExit(f"recovered overlap file hash mismatch: {path}")
    if hashlib.sha256(OVERLAP_CONTRACT.read_bytes()).hexdigest() != frozen.get("contract_sha256"):
        raise SystemExit("recovered overlap contract hash mismatch")
    verify_overlap_control_directory(frozen)
    return gate, frozen


def verify_source_control_recovery_gate_and_hashes() -> dict:
    if not SOURCE_CONTROL_RECOVERY_GATE.is_file():
        raise SystemExit("source-control recovery gate is missing")
    gate = json.loads(SOURCE_CONTROL_RECOVERY_GATE.read_text(encoding="utf-8"))
    if (
        gate.get("schema_version") != "m9-source-control-recovery-gate-v1"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
        or gate.get("decision_id") != "D-017-source-control-recovery-v1"
    ):
        raise SystemExit("source-control recovery gate is not a zero-issue PASS")
    report = Path(str(gate.get("audit_report_path", ""))).resolve(strict=False)
    if report.parent != AUDITS.resolve(strict=False) or report.suffix.lower() != ".json":
        raise SystemExit("source-control audit report must be a JSON verdict directly under 08_audits")
    report_payload = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else None
    if (
        not isinstance(report_payload, dict)
        or report_payload.get("schema_version") != "m9-source-control-recovery-audit-verdict-v1"
        or report_payload.get("decision_id") != "D-017-source-control-recovery-v1"
        or report_payload.get("verdict") != "PASS"
        or int(report_payload.get("blocking", -1)) != 0
        or int(report_payload.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("source-control recovery gate lacks structured PASS verdict")
    if hashlib.sha256(report.read_bytes()).hexdigest() != gate.get("audit_report_sha256"):
        raise SystemExit("source-control recovery audit report hash mismatch")
    auth = SOURCE_CONTROL_RECOVERY_AUTHORIZATION
    if gate.get("authorization_record_path") != auth.as_posix() or not auth.is_file() or hashlib.sha256(auth.read_bytes()).hexdigest() != gate.get("authorization_record_sha256"):
        raise SystemExit("source-control recovery authorization binding mismatch")
    frozen = SOURCE_CONTROL_RECOVERY_FROZEN_HASHES
    if gate.get("frozen_hashes_path") != frozen.as_posix() or not frozen.is_file() or hashlib.sha256(frozen.read_bytes()).hexdigest() != gate.get("frozen_hashes_sha256"):
        raise SystemExit("source-control recovery frozen hash binding mismatch")
    manifest = json.loads(frozen.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, dict) or set(Path(str(p)).resolve(strict=False) for p in files) != {p.resolve(strict=False) for p in SOURCE_RECOVERY_CONTROL_FILES}:
        raise SystemExit("source-control recovery frozen file set mismatch")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != str(expected):
            raise SystemExit(f"source-control recovery frozen file mismatch: {path}")
    verify_overlap_control_directory(manifest)
    expected_failure = gate.get("expected_failed_transaction")
    if not isinstance(expected_failure, dict):
        raise SystemExit("source-control recovery gate lacks failed transaction binding")
    expected_capability = gate.get("expected_stale_capability")
    if not isinstance(expected_capability, dict):
        raise SystemExit("source-control recovery gate lacks stale capability binding")
    return gate


def source_control_gate_receipt(gate: dict) -> dict[str, object]:
    return {
        "decision_id": gate.get("decision_id"),
        "gate_sha256": hashlib.sha256(SOURCE_CONTROL_RECOVERY_GATE.read_bytes()).hexdigest(),
        "audit_report_path": gate.get("audit_report_path"),
        "audit_report_sha256": gate.get("audit_report_sha256"),
        "authorization_record_sha256": gate.get("authorization_record_sha256"),
        "frozen_hashes_sha256": gate.get("frozen_hashes_sha256"),
    }


def read_d018_control_json(path: Path) -> tuple[dict[str, object], dict, bytes]:
    receipt, value, payload = read_stable_regular_json(path)
    expected = {"uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1}
    if any(receipt.get(key) != wanted for key, wanted in expected.items()):
        raise SystemExit(f"D-018 control object metadata mismatch: {path}")
    return receipt, value, payload


def build_d018_overlap_gate(
    verdict_receipt: dict[str, object],
    frozen_receipt: dict[str, object],
    authorization_sha256: str,
) -> dict[str, object]:
    return {
        "schema_version": "m9-overlap-audit-gate-v1",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "work_package_path": OVERLAP_WORK_PACKAGE.as_posix(),
        "work_package_sha256": hashlib.sha256(OVERLAP_WORK_PACKAGE.read_bytes()).hexdigest(),
        "audit_report_path": UNLIMITED_WALL_CLOCK_VERDICT.as_posix(),
        "audit_report_sha256": verdict_receipt["sha256"],
        "frozen_hashes_path": OVERLAP_FROZEN_HASHES.as_posix(),
        "frozen_hashes_sha256": frozen_receipt["sha256"],
        "decision_id": "D-018",
        "authorization_record_path": UNLIMITED_WALL_CLOCK_AUTHORIZATION.as_posix(),
        "authorization_record_sha256": authorization_sha256,
    }


def verify_unlimited_wall_clock_gate_and_hashes() -> tuple[dict, dict[str, object], bytes]:
    gate_receipt, gate, _ = read_d018_control_json(UNLIMITED_WALL_CLOCK_GATE)
    required_gate = {
        "schema_version": "m9-unlimited-wall-clock-gate-v1",
        "decision_id": "D-018",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "scope": "MIGRATE_TO_UNLIMITED_WALL_CLOCK_AND_CONTINUE_M9",
    }
    if any(gate.get(key) != value for key, value in required_gate.items()):
        raise SystemExit("D-018 gate is not an exact zero-issue PASS")
    verdict_receipt, verdict, _ = read_stable_regular_json(UNLIMITED_WALL_CLOCK_VERDICT)
    if (
        verdict.get("schema_version") != "m9-unlimited-wall-clock-audit-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or gate.get("verdict_path") != UNLIMITED_WALL_CLOCK_VERDICT.as_posix()
        or gate.get("verdict_sha256") != verdict_receipt["sha256"]
    ):
        raise SystemExit("D-018 structured verdict binding mismatch")
    if (
        verdict.get("work_package_path") != UNLIMITED_WALL_CLOCK_WORK_PACKAGE.as_posix()
        or hashlib.sha256(UNLIMITED_WALL_CLOCK_WORK_PACKAGE.read_bytes()).hexdigest()
        != verdict.get("work_package_sha256")
    ):
        raise SystemExit("D-018 work-package binding mismatch")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    if (
        report.parent != AUDITS.resolve(strict=False)
        or not report.is_file()
        or hashlib.sha256(report.read_bytes()).hexdigest() != verdict.get("report_sha256")
    ):
        raise SystemExit("D-018 audit report binding mismatch")
    authorization_sha256 = hashlib.sha256(UNLIMITED_WALL_CLOCK_AUTHORIZATION.read_bytes()).hexdigest()
    contract_sha256 = hashlib.sha256(UNLIMITED_WALL_CLOCK_CONTRACT.read_bytes()).hexdigest()
    if (
        gate.get("authorization_path") != UNLIMITED_WALL_CLOCK_AUTHORIZATION.as_posix()
        or gate.get("authorization_sha256") != authorization_sha256
        or gate.get("contract_path") != UNLIMITED_WALL_CLOCK_CONTRACT.as_posix()
        or gate.get("contract_sha256") != contract_sha256
    ):
        raise SystemExit("D-018 authorization or contract binding mismatch")
    frozen_receipt, frozen, _ = read_stable_regular_json(UNLIMITED_WALL_CLOCK_FROZEN_HASHES)
    if (
        gate.get("frozen_hashes_path") != UNLIMITED_WALL_CLOCK_FROZEN_HASHES.as_posix()
        or gate.get("frozen_hashes_sha256") != frozen_receipt["sha256"]
        or frozen.get("schema_version") != "m9-unlimited-wall-clock-frozen-hashes-v1"
    ):
        raise SystemExit("D-018 frozen hash binding mismatch")
    files = frozen.get("files")
    if (
        not isinstance(files, dict)
        or {Path(str(path)).resolve(strict=False) for path in files}
        != {path.resolve(strict=False) for path in UNLIMITED_WALL_CLOCK_CONTROL_FILES}
    ):
        raise SystemExit("D-018 frozen file closure mismatch")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if (
            path.is_symlink()
            or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != str(expected)
        ):
            raise SystemExit(f"D-018 frozen member mismatch: {path}")
    verify_overlap_control_directory(frozen)
    overlap_frozen_receipt, _, _ = read_stable_regular_json(OVERLAP_FROZEN_HASHES)
    replacement = build_d018_overlap_gate(
        verdict_receipt, overlap_frozen_receipt, authorization_sha256
    )
    replacement_bytes = (
        json.dumps(replacement, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    if (
        gate.get("replacement_overlap_gate_sha256")
        != hashlib.sha256(replacement_bytes).hexdigest()
        or int(gate.get("replacement_overlap_gate_bytes", -1)) != len(replacement_bytes)
    ):
        raise SystemExit("D-018 replacement overlap gate binding mismatch")
    bindings = {
        "gate": gate_receipt,
        "verdict": verdict_receipt,
        "frozen": frozen_receipt,
        "overlap_frozen": overlap_frozen_receipt,
        "authorization_sha256": authorization_sha256,
        "contract_sha256": contract_sha256,
    }
    return gate, bindings, replacement_bytes


def d018_runtime_receipts() -> dict[str, object]:
    paths = {
        "state_sha256": STATE_PATH,
        "workflow_sha256": OVERLAP_WORKFLOW_STATE,
        "ledger_sha256": LEDGER_PATH,
        "overlap_transaction_sha256": OVERLAP_TRANSACTION,
        "source_control_recovery_transaction_sha256": SOURCE_CONTROL_RECOVERY_TRANSACTION,
        "source_control_recovery_gate_sha256": SOURCE_CONTROL_RECOVERY_GATE,
        "active_overlap_gate_sha256": OVERLAP_AUDIT_GATE,
    }
    observed: dict[str, object] = {}
    for key, path in paths.items():
        receipt, payload = read_stable_regular_bytes(path)
        observed[key] = receipt["sha256"]
        if key == "ledger_sha256":
            observed["ledger_bytes"] = len(payload)
    observed["source_products_present"] = [
        path.as_posix() for path in SOURCE_RECOVERY_PRODUCTS if path.exists()
    ]
    return observed


def d018_policy(gate: dict, bindings: dict[str, object]) -> dict[str, object]:
    transaction_id = str(gate["migration_transaction_id"])
    return {
        "mode": "UNLIMITED",
        "decision_id": "D-018",
        "historical_limit_seconds": HISTORICAL_WALL_LIMIT,
        "historical_start_utc": FROZEN_START,
        "historical_deadline_utc": FROZEN_DEADLINE,
        "migration_transaction_id": transaction_id,
        "migration_event_id": str(gate["migration_event_id"]),
        "authorization_sha256": str(bindings["authorization_sha256"]),
        "contract_sha256": str(bindings["contract_sha256"]),
        "gate_sha256": str(bindings["gate"]["sha256"]),
    }


def d018_journal_context(journal: dict) -> dict[str, object]:
    keys = {
        "schema_version",
        "transaction_id",
        "event_id",
        "python_bootstrap",
        "gate_receipt",
        "pre_runtime",
        "pre_state_snapshot",
        "old_overlap_gate",
        "replacement_overlap_gate_sha256",
        "replacement_overlap_gate_bytes",
        "migration_utc",
    }
    if not keys.issubset(journal):
        raise SystemExit("D-018 journal context is incomplete")
    return {key: journal[key] for key in sorted(keys)}


def d018_migration_event(
    journal: dict,
    gate: dict,
    bindings: dict[str, object],
) -> dict[str, object]:
    return {
        "event_id": str(gate["migration_event_id"]),
        "event": "M9_UNLIMITED_WALL_CLOCK_MIGRATION",
        "utc": journal["migration_utc"],
        "decision_id": "D-018",
        "transaction_id": str(gate["migration_transaction_id"]),
        "historical_start_utc": FROZEN_START,
        "historical_deadline_utc": FROZEN_DEADLINE,
        "historical_limit_seconds": HISTORICAL_WALL_LIMIT,
        "policy": d018_policy(gate, bindings),
        "pre_state_sha256": journal["pre_runtime"]["state_sha256"],
        "gate_sha256": bindings["gate"]["sha256"],
    }


def verify_d017_history_bound_by_d018(transaction: dict) -> None:
    runtime = transaction.get("pre_runtime")
    if not isinstance(runtime, dict):
        raise SystemExit("D-018 transaction lacks the D-017 runtime binding")
    source_receipt, source_bytes = read_stable_regular_bytes(
        SOURCE_CONTROL_RECOVERY_TRANSACTION
    )
    source_gate_receipt, _ = read_stable_regular_bytes(SOURCE_CONTROL_RECOVERY_GATE)
    if (
        source_receipt["sha256"]
        != runtime.get("source_control_recovery_transaction_sha256")
        or source_gate_receipt["sha256"]
        != runtime.get("source_control_recovery_gate_sha256")
    ):
        raise SystemExit("D-017 recovery evidence drift after D-018")
    recovery = json.loads(source_bytes.decode("utf-8"))
    event = recovery.get("event")
    migration = recovery.get("post_failure_migration")
    if (
        recovery.get("schema_version") != "m9-source-control-recovery-v1"
        or recovery.get("state") != "SUCCESS_COMMITTED"
        or recovery.get("ledger_phase") != "COMMITTED"
        or not isinstance(event, dict)
        or event.get("event") != "OVERLAP_SOURCE_CONTROL_FAILURE_RECOVERY"
        or event.get("transaction_id") != recovery.get("transaction_id")
        or not isinstance(migration, dict)
        or migration.get("status") != "PASS"
        or migration.get("recovery_transaction_id") != recovery.get("transaction_id")
        or migration.get("recovery_event_id") != event.get("event_id")
        or recovery.get("post_state_sha256") != runtime.get("state_sha256")
        or recovery.get("post_workflow_sha256") != runtime.get("workflow_sha256")
        or recovery.get("post_ledger_sha256") != runtime.get("ledger_sha256")
    ):
        raise SystemExit("D-017 recovery transaction closure mismatch")


def d018_execution_runtime_receipts() -> dict[str, object]:
    paths = {
        "state_sha256": STATE_PATH,
        "workflow_sha256": OVERLAP_WORKFLOW_STATE,
        "ledger_sha256": LEDGER_PATH,
        "overlap_transaction_sha256": OVERLAP_TRANSACTION,
        "source_control_recovery_transaction_sha256": SOURCE_CONTROL_RECOVERY_TRANSACTION,
        "source_control_recovery_gate_sha256": SOURCE_CONTROL_RECOVERY_GATE,
        "d018_gate_sha256": UNLIMITED_WALL_CLOCK_GATE,
        "d018_transaction_sha256": UNLIMITED_WALL_CLOCK_TRANSACTION,
        "d018_journal_sha256": UNLIMITED_WALL_CLOCK_JOURNAL,
        "d018_pre_state_snapshot_sha256": UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT,
        "retired_overlap_gate_sha256": OVERLAP_AUDIT_GATE_PRE_D018_RETIRED,
        "active_overlap_gate_sha256": OVERLAP_AUDIT_GATE,
    }
    receipts: dict[str, object] = {}
    for key, path in paths.items():
        receipt, _ = read_stable_regular_bytes(path)
        receipts[key] = receipt["sha256"]
    receipts["source_products_present"] = [
        path.as_posix() for path in SOURCE_RECOVERY_PRODUCTS if path.exists()
    ]
    return receipts


def verify_unlimited_wall_clock_execution_ready() -> dict:
    gate, bindings, replacement_bytes = verify_unlimited_wall_clock_gate_and_hashes()
    receipt, transaction, _ = read_d018_control_json(UNLIMITED_WALL_CLOCK_TRANSACTION)
    state = load_state()
    raw_state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    expected_policy = d018_policy(gate, bindings)
    required_transaction_fields = {
        "schema_version", "state", "transaction_id", "event_id", "decision_id",
        "policy", "gate_receipt", "pre_runtime", "pre_state_snapshot",
        "retired_overlap_gate", "replacement_overlap_gate", "ledger_commit", "ledger_sha256",
        "migrated_state_sha256", "journal_path", "journal_context_sha256",
        "completed_utc", "journal_sha256",
    }
    if (
        set(transaction) != required_transaction_fields
        or
        transaction.get("schema_version") != "m9-unlimited-wall-clock-transaction-v1"
        or transaction.get("state") != "SUCCESS_COMMITTED"
        or transaction.get("transaction_id") != gate.get("migration_transaction_id")
        or transaction.get("event_id") != gate.get("migration_event_id")
        or transaction.get("policy") != expected_policy
        or transaction.get("gate_receipt") != bindings["gate"]
        or state.get("wall_clock_policy") != expected_policy
        or wall_clock_policy_mode(state) != "UNLIMITED"
        or gate.get("replacement_overlap_gate_sha256")
        != hashlib.sha256(replacement_bytes).hexdigest()
    ):
        raise SystemExit("D-018 terminal migration receipt mismatch")
    journal_receipt, journal = strict_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL)
    required_journal_fields = {
        "schema_version", "state", "transaction_id", "event_id", "python_bootstrap",
        "gate_receipt", "pre_runtime", "pre_state_snapshot", "old_overlap_gate",
        "replacement_overlap_gate_sha256", "replacement_overlap_gate_bytes",
        "migration_utc", "context_sha256", "retired_overlap_gate",
        "replacement_overlap_gate", "ledger_commit", "ledger_sha256",
        "migrated_state_sha256", "completed_utc",
    }
    snapshot_receipt, snapshot_bytes = read_strict_root_private_bytes(
        UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT
    )
    retired_receipt, _ = read_d018_inode_regular_bytes(
        OVERLAP_AUDIT_GATE_PRE_D018_RETIRED
    )
    event = d018_migration_event(journal, gate, bindings)
    prefix_bytes = int(transaction.get("pre_runtime", {}).get("ledger_bytes", -1))
    ledger_receipt, ledger_bytes = read_stable_regular_bytes(LEDGER_PATH)
    event_bytes = canonical_ledger_event_bytes(event)
    expected_ledger_commit = {
        "path": LEDGER_PATH.as_posix(),
        "prefix_bytes": prefix_bytes,
        "prefix_sha256": transaction.get("pre_runtime", {}).get("ledger_sha256"),
        "event_bytes": len(event_bytes),
        "event_sha256": hashlib.sha256(event_bytes).hexdigest(),
        "final_bytes": len(ledger_bytes),
        "final_sha256": ledger_receipt["sha256"],
    }
    if (
        set(journal) != required_journal_fields
        or journal.get("schema_version") != "m9-unlimited-wall-clock-journal-v1"
        or journal.get("state") != "SUCCESS_COMMITTED"
        or canonical_hash(d018_journal_context(journal)) != journal.get("context_sha256")
        or transaction.get("journal_sha256") != journal_receipt["sha256"]
        or transaction.get("pre_state_snapshot") != snapshot_receipt
        or hashlib.sha256(snapshot_bytes).hexdigest()
        != transaction.get("pre_runtime", {}).get("state_sha256")
        or transaction.get("retired_overlap_gate") != retired_receipt
        or journal.get("retired_overlap_gate") != retired_receipt
        or ledger_bytes[:prefix_bytes] == b""
        or hashlib.sha256(ledger_bytes[:prefix_bytes]).hexdigest()
        != transaction.get("pre_runtime", {}).get("ledger_sha256")
        or ledger_bytes[prefix_bytes:] != event_bytes
        or journal.get("ledger_commit") != expected_ledger_commit
        or transaction.get("ledger_commit") != expected_ledger_commit
        or ledger_receipt["sha256"] != transaction.get("ledger_sha256")
        or journal.get("ledger_sha256") != ledger_receipt["sha256"]
    ):
        raise SystemExit("D-018 terminal historical evidence mismatch")
    active_receipt, active_payload, _ = read_d018_control_json(OVERLAP_AUDIT_GATE)
    if (
        active_receipt["sha256"] != gate.get("replacement_overlap_gate_sha256")
        or active_payload != json.loads(replacement_bytes.decode("utf-8"))
    ):
        raise SystemExit("D-018 active overlap gate mismatch")
    expected_state = json.loads(snapshot_bytes.decode("utf-8"))
    expected_state["wall_clock_policy"] = expected_policy
    expected_state["last_event_utc"] = journal["migration_utc"]
    if (
        active_receipt != transaction.get("replacement_overlap_gate")
        or active_receipt != journal.get("replacement_overlap_gate")
        or hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
        != transaction.get("migrated_state_sha256")
        or journal.get("migrated_state_sha256") != transaction.get("migrated_state_sha256")
        or raw_state != expected_state
        or transaction.get("journal_path") != UNLIMITED_WALL_CLOCK_JOURNAL.as_posix()
        or transaction.get("journal_context_sha256") != journal.get("context_sha256")
        or transaction.get("completed_utc") != journal.get("migration_utc")
    ):
        raise SystemExit("D-018 terminal transaction field mismatch")
    verify_d017_history_bound_by_d018(transaction)
    return transaction


def verify_unlimited_wall_clock_execution_fact_gate() -> dict:
    gate_receipt, gate, _ = read_d018_control_json(UNLIMITED_WALL_CLOCK_EXECUTION_GATE)
    if (
        gate.get("schema_version") != "m9-unlimited-wall-clock-execution-gate-v1"
        or gate.get("decision_id") != "D-018"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
        or gate.get("scope") != "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"
    ):
        raise SystemExit("D-018 execution fact gate is not an exact PASS")
    verdict_receipt, verdict, _ = read_stable_regular_json(
        UNLIMITED_WALL_CLOCK_EXECUTION_VERDICT
    )
    if (
        verdict.get("schema_version")
        != "m9-unlimited-wall-clock-execution-audit-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or gate.get("verdict_path") != UNLIMITED_WALL_CLOCK_EXECUTION_VERDICT.as_posix()
        or gate.get("verdict_sha256") != verdict_receipt["sha256"]
    ):
        raise SystemExit("D-018 execution verdict binding mismatch")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    if (
        report != UNLIMITED_WALL_CLOCK_EXECUTION_REPORT.resolve(strict=False)
        or not report.is_file()
        or hashlib.sha256(report.read_bytes()).hexdigest() != verdict.get("report_sha256")
    ):
        raise SystemExit("D-018 execution audit report binding mismatch")
    current = d018_execution_runtime_receipts()
    if gate.get("runtime") != current or current.get("source_products_present") != []:
        raise SystemExit("D-018 execution fact runtime drift")
    transaction = verify_unlimited_wall_clock_execution_ready()
    if gate.get("d018_transaction_sha256") != current["d018_transaction_sha256"]:
        raise SystemExit("D-018 execution gate transaction binding mismatch")
    return {"gate_receipt": gate_receipt, "gate": gate, "transaction": transaction}


def read_strict_root_private_bytes(path: Path) -> tuple[dict[str, object], bytes]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit(f"root-private control object is missing or not regular: {path}") from exc
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != 0
            or before.st_gid != 0
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_nlink != 1
        ):
            raise SystemExit(f"root-private control object metadata mismatch: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        try:
            linked = os.lstat(path)
        except OSError as exc:
            raise SystemExit(f"root-private control object path changed while reading: {path}") from exc
        stable_fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if (
            any(getattr(before, field) != getattr(after, field) for field in stable_fields)
            or any(getattr(after, field) != getattr(linked, field) for field in stable_fields)
            or stat.S_ISLNK(linked.st_mode)
            or len(payload) != after.st_size
        ):
            raise SystemExit(f"root-private control object path changed while reading: {path}")
    finally:
        os.close(descriptor)
    receipt = {
        "path": path.as_posix(),
        "bytes": after.st_size,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "uid": after.st_uid,
        "gid": after.st_gid,
        "mode": stat.S_IMODE(after.st_mode),
        "nlink": after.st_nlink,
    }
    return receipt, payload


def strict_root_private_receipt(path: Path) -> dict[str, object]:
    receipt, _ = read_strict_root_private_bytes(path)
    return receipt


def strict_root_private_json(path: Path) -> tuple[dict[str, object], dict]:
    receipt, payload = read_strict_root_private_bytes(path)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"root-private control object is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"root-private control object JSON must be an object: {path}")
    return receipt, value


def read_stable_regular_json(path: Path) -> tuple[dict[str, object], dict, bytes]:
    """Read one non-linked regular file through one descriptor and bind its bytes."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit(f"stable JSON object is missing: {path}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"stable JSON object metadata mismatch: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        linked = os.lstat(path)
        fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if (
            any(getattr(before, key) != getattr(after, key) for key in fields)
            or any(getattr(after, key) != getattr(linked, key) for key in fields)
            or stat.S_ISLNK(linked.st_mode)
            or len(payload) != after.st_size
        ):
            raise SystemExit(f"stable JSON object changed while reading: {path}")
    finally:
        os.close(descriptor)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"stable JSON object is invalid: {path}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"stable JSON object must be a mapping: {path}")
    receipt = {
        "path": path.as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "uid": after.st_uid,
        "gid": after.st_gid,
        "mode": stat.S_IMODE(after.st_mode),
        "nlink": after.st_nlink,
    }
    return receipt, value, payload


def read_stable_regular_bytes(path: Path) -> tuple[dict[str, object], bytes]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit(f"stable regular object is missing: {path}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"stable regular object metadata mismatch: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        linked = os.lstat(path)
        fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if (
            any(getattr(before, key) != getattr(after, key) for key in fields)
            or any(getattr(after, key) != getattr(linked, key) for key in fields)
            or stat.S_ISLNK(linked.st_mode)
            or len(payload) != after.st_size
        ):
            raise SystemExit(f"stable regular object changed while reading: {path}")
    finally:
        os.close(descriptor)
    return {
        "path": path.as_posix(), "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "uid": after.st_uid, "gid": after.st_gid,
        "mode": stat.S_IMODE(after.st_mode), "nlink": after.st_nlink,
    }, payload


def read_d018_inode_regular_bytes(path: Path) -> tuple[dict[str, object], bytes]:
    """Read a single-link regular file and bind the concrete inode used by D-018."""
    receipt, payload = read_stable_regular_bytes(path)
    linked = os.lstat(path)
    if stat.S_ISLNK(linked.st_mode) or linked.st_nlink != 1:
        raise SystemExit(f"D-018 inode object metadata mismatch: {path}")
    receipt["dev"] = int(linked.st_dev)
    receipt["ino"] = int(linked.st_ino)
    return receipt, payload


def rename_d018_gate_preserving_inode(
    active: Path,
    retired: Path,
    expected: dict[str, object],
) -> dict[str, object]:
    """Rename the exact opened inode and reject same-byte path substitution."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(active, flags)
    try:
        opened = os.fstat(descriptor)
        payload = bytearray()
        offset = 0
        while offset < opened.st_size:
            chunk = os.pread(descriptor, min(1024 * 1024, opened.st_size - offset), offset)
            if not chunk:
                raise SystemExit("D-018 old gate read was short")
            payload.extend(chunk)
            offset += len(chunk)
        opened_receipt = {
            "path": active.as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(bytes(payload)).hexdigest(),
            "uid": opened.st_uid,
            "gid": opened.st_gid,
            "mode": stat.S_IMODE(opened.st_mode),
            "nlink": opened.st_nlink,
            "dev": int(opened.st_dev),
            "ino": int(opened.st_ino),
        }
        linked = os.lstat(active)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened_receipt != expected
            or (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise SystemExit("D-018 old gate inode drift before retirement")
        os.replace(active, retired)
        directory = os.open(active.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        after = os.fstat(descriptor)
        retired_stat = os.lstat(retired)
        if (
            (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino)
            or (retired_stat.st_dev, retired_stat.st_ino) != (opened.st_dev, opened.st_ino)
            or after.st_nlink != 1
            or retired_stat.st_nlink != 1
        ):
            raise SystemExit("D-018 retired gate is not the authorized inode")
    finally:
        os.close(descriptor)
    retired_receipt, _ = read_d018_inode_regular_bytes(retired)
    wanted = dict(expected, path=retired.as_posix())
    if retired_receipt != wanted:
        raise SystemExit("D-018 retired overlap gate receipt mismatch")
    return retired_receipt


def verify_source_control_gate_disposition() -> tuple[dict, dict]:
    path = SOURCE_CONTROL_GATE_DISPOSITION_VERDICT
    if not path.is_file() or path.parent.resolve(strict=False) != AUDITS.resolve(strict=False):
        raise SystemExit("source-control gate disposition verdict is missing")
    verdict = json.loads(path.read_text(encoding="utf-8"))
    if (
        verdict.get("schema_version") != "m9-source-control-gate-disposition-audit-verdict-v1"
        or verdict.get("decision_id") != "D-017-source-control-gate-disposition-v1"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("scope") != "RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY"
        or verdict.get("old_gate_sha256") != INVALID_SOURCE_CONTROL_GATE_SHA256
        or int(verdict.get("old_gate_bytes", -1)) != INVALID_SOURCE_CONTROL_GATE_BYTES
    ):
        raise SystemExit("source-control gate disposition verdict is not an exact zero-issue PASS")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    if (
        report.parent != AUDITS.resolve(strict=False)
        or not report.is_file()
        or hashlib.sha256(report.read_bytes()).hexdigest() != verdict.get("report_sha256")
    ):
        raise SystemExit("source-control gate disposition report binding mismatch")
    replacement_path = SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT
    if (
        verdict.get("replacement_verdict_path") != replacement_path.as_posix()
        or not replacement_path.is_file()
        or hashlib.sha256(replacement_path.read_bytes()).hexdigest()
        != verdict.get("replacement_verdict_sha256")
    ):
        raise SystemExit("replacement source-control verdict binding mismatch")
    replacement = json.loads(replacement_path.read_text(encoding="utf-8"))
    if (
        replacement.get("schema_version") != "m9-source-control-recovery-audit-verdict-v1"
        or replacement.get("decision_id") != "D-017-source-control-recovery-v1"
        or replacement.get("verdict") != "PASS"
        or int(replacement.get("blocking", -1)) != 0
        or int(replacement.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("replacement source-control verdict is not an exact zero-issue PASS")
    current_frozen = hashlib.sha256(SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_bytes()).hexdigest()
    current_auth = hashlib.sha256(SOURCE_CONTROL_RECOVERY_AUTHORIZATION.read_bytes()).hexdigest()
    if (
        verdict.get("frozen_hashes_sha256") != current_frozen
        or verdict.get("authorization_record_sha256") != current_auth
    ):
        raise SystemExit("gate disposition frozen or authorization binding mismatch")
    manifest = json.loads(SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if (
        not isinstance(files, dict)
        or set(Path(str(path)).resolve(strict=False) for path in files)
        != {path.resolve(strict=False) for path in SOURCE_RECOVERY_CONTROL_FILES}
    ):
        raise SystemExit("gate disposition frozen file set mismatch")
    for text_path, expected in files.items():
        member = Path(str(text_path))
        if (
            member.is_symlink()
            or not member.is_file()
            or hashlib.sha256(member.read_bytes()).hexdigest() != str(expected)
        ):
            raise SystemExit(f"gate disposition frozen member mismatch: {member}")
    verify_overlap_control_directory(manifest)
    return verdict, replacement


def source_control_disposition_runtime_receipt() -> dict[str, object]:
    if (
        SOURCE_CONTROL_RECOVERY_TRANSACTION.exists()
        or SOURCE_CONTROL_RECOVERY_TRANSACTION.is_symlink()
        or SOURCE_CONTROL_RECOVERY_PARENT.exists()
        or SOURCE_CONTROL_RECOVERY_PARENT.is_symlink()
    ):
        raise SystemExit("gate disposition requires absent recovery transaction and parent")
    cap = OVERLAP_CAPABILITY_ROOT / "f7c3b060e19e37e6da03f461d754d38c.json"
    return {
        "state_sha256": hashlib.sha256(STATE_PATH.read_bytes()).hexdigest(),
        "workflow_sha256": hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest(),
        "transaction_sha256": hashlib.sha256(OVERLAP_TRANSACTION.read_bytes()).hexdigest(),
        "ledger_sha256": hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest(),
        "stale_capability_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
        "recovery_transaction_absent": True,
        "recovery_parent_absent": True,
    }


def replacement_source_control_gate(old_gate: dict, replacement_verdict: dict) -> dict:
    gate = dict(old_gate)
    gate["audit_report_path"] = SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT.as_posix()
    gate["audit_report_sha256"] = hashlib.sha256(
        SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT.read_bytes()
    ).hexdigest()
    gate["frozen_hashes_sha256"] = hashlib.sha256(
        SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_bytes()
    ).hexdigest()
    gate["scope"] = "ONE_TIME_SOURCE_CONTROL_RECOVERY"
    if replacement_verdict.get("decision_id") != gate.get("decision_id"):
        raise SystemExit("replacement gate decision mismatch")
    return gate


def verify_source_control_gate_lock_refresh() -> tuple[dict, dict, dict[str, str]]:
    path = SOURCE_CONTROL_GATE_LOCK_REFRESH_VERDICT
    if not path.is_file() or path.parent.resolve(strict=False) != AUDITS.resolve(strict=False):
        raise SystemExit("source-control gate lock-refresh verdict is missing")
    verdict_bytes = path.read_bytes()
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    if (
        verdict.get("schema_version") != "m9-source-control-gate-lock-refresh-audit-verdict-v1"
        or verdict.get("decision_id") != "D-017-source-control-gate-lock-refresh-v1"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("scope") != "RETIRE_PRE_LOCK_MODE_GATE_AND_CREATE_REPLACEMENT_ONLY"
        or verdict.get("old_gate_sha256") != PRE_LOCK_REFRESH_GATE_SHA256
        or int(verdict.get("old_gate_bytes", -1)) != PRE_LOCK_REFRESH_GATE_BYTES
    ):
        raise SystemExit("source-control gate lock-refresh verdict is not an exact zero-issue PASS")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    if (
        report.parent != AUDITS.resolve(strict=False)
        or not report.is_file()
        or hashlib.sha256(report.read_bytes()).hexdigest() != verdict.get("report_sha256")
    ):
        raise SystemExit("source-control gate lock-refresh report binding mismatch")
    replacement_path = SOURCE_CONTROL_RECOVERY_LOCK_REPLACEMENT_VERDICT
    replacement_bytes = replacement_path.read_bytes() if replacement_path.is_file() else b""
    if (
        verdict.get("replacement_verdict_path") != replacement_path.as_posix()
        or not replacement_bytes
        or hashlib.sha256(replacement_bytes).hexdigest()
        != verdict.get("replacement_verdict_sha256")
    ):
        raise SystemExit("lock-refresh replacement verdict binding mismatch")
    replacement = json.loads(replacement_bytes.decode("utf-8"))
    if (
        replacement.get("schema_version") != "m9-source-control-recovery-audit-verdict-v1"
        or replacement.get("decision_id") != "D-017-source-control-recovery-v1"
        or replacement.get("verdict") != "PASS"
        or int(replacement.get("blocking", -1)) != 0
        or int(replacement.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("lock-refresh replacement verdict is not an exact zero-issue PASS")
    frozen_bytes = SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_bytes()
    authorization_bytes = SOURCE_CONTROL_RECOVERY_AUTHORIZATION.read_bytes()
    current_frozen = hashlib.sha256(frozen_bytes).hexdigest()
    current_auth = hashlib.sha256(authorization_bytes).hexdigest()
    if (
        verdict.get("frozen_hashes_sha256") != current_frozen
        or verdict.get("authorization_record_sha256") != current_auth
    ):
        raise SystemExit("gate lock-refresh frozen or authorization binding mismatch")
    manifest = json.loads(frozen_bytes.decode("utf-8"))
    files = manifest.get("files")
    if (
        not isinstance(files, dict)
        or set(Path(str(member)).resolve(strict=False) for member in files)
        != {member.resolve(strict=False) for member in SOURCE_RECOVERY_CONTROL_FILES}
    ):
        raise SystemExit("gate lock-refresh frozen file set mismatch")
    for text_path, expected in files.items():
        member = Path(str(text_path))
        if (
            member.is_symlink()
            or not member.is_file()
            or hashlib.sha256(member.read_bytes()).hexdigest() != str(expected)
        ):
            raise SystemExit(f"gate lock-refresh frozen member mismatch: {member}")
    verify_overlap_control_directory(manifest)
    return verdict, replacement, {
        "refresh_verdict_sha256": hashlib.sha256(verdict_bytes).hexdigest(),
        "replacement_verdict_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
        "frozen_hashes_sha256": current_frozen,
        "authorization_record_sha256": current_auth,
    }


def source_control_lock_refresh_runtime_receipt() -> dict[str, object]:
    if (
        SOURCE_CONTROL_RECOVERY_TRANSACTION.exists()
        or SOURCE_CONTROL_RECOVERY_TRANSACTION.is_symlink()
        or SOURCE_CONTROL_RECOVERY_PARENT.exists()
        or SOURCE_CONTROL_RECOVERY_PARENT.is_symlink()
    ):
        raise SystemExit("gate lock refresh requires absent recovery transaction and parent")
    _, disposition = strict_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL)
    if disposition.get("state") != "SUCCESS_COMMITTED":
        raise SystemExit("gate lock refresh requires committed disposition evidence")
    invalid_retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_INVALID_RETIRED)
    if (
        invalid_retired.get("sha256") != INVALID_SOURCE_CONTROL_GATE_SHA256
        or invalid_retired.get("bytes") != INVALID_SOURCE_CONTROL_GATE_BYTES
    ):
        raise SystemExit("gate lock refresh invalid-retired evidence mismatch")
    cap = OVERLAP_CAPABILITY_ROOT / "f7c3b060e19e37e6da03f461d754d38c.json"
    return {
        "state_sha256": hashlib.sha256(STATE_PATH.read_bytes()).hexdigest(),
        "workflow_sha256": hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest(),
        "transaction_sha256": hashlib.sha256(OVERLAP_TRANSACTION.read_bytes()).hexdigest(),
        "ledger_sha256": hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest(),
        "stale_capability_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
        "disposition_journal_sha256": hashlib.sha256(
            SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL.read_bytes()
        ).hexdigest(),
        "invalid_retired_gate_sha256": invalid_retired["sha256"],
        "recovery_transaction_absent": True,
        "recovery_parent_absent": True,
    }


def lock_refresh_source_control_gate(
    old_gate: dict,
    replacement_verdict: dict,
    replacement_verdict_sha256: str,
    frozen_hashes_sha256: str,
) -> dict:
    gate = dict(old_gate)
    gate["audit_report_path"] = SOURCE_CONTROL_RECOVERY_LOCK_REPLACEMENT_VERDICT.as_posix()
    gate["audit_report_sha256"] = replacement_verdict_sha256
    gate["frozen_hashes_sha256"] = frozen_hashes_sha256
    gate["scope"] = "ONE_TIME_SOURCE_CONTROL_RECOVERY"
    if replacement_verdict.get("decision_id") != gate.get("decision_id"):
        raise SystemExit("lock-refresh replacement gate decision mismatch")
    return gate


def command_overlap_init(_: argparse.Namespace) -> int:
    bootstrap = isolated_bootstrap_provenance()
    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        if (
            state.get("overlap_storage_baseline") is not None
            or OVERLAP_WORKFLOW_STATE.exists()
            or OVERLAP_TRANSACTION.exists()
        ):
            raise SystemExit("overlap state already exists; refusing to reinitialize")
        verify_overlap_gate_and_hashes()
        baseline = storage_snapshot(state)
        transaction = {
            "schema_version": "m9-overlap-transaction-v1",
            "transaction_id": "INITIALIZATION",
            "state": "INITIALIZING",
            "utc": utc_now(),
        }
        atomic_json(OVERLAP_TRANSACTION, transaction)
        state["overlap_storage_baseline"] = {
            "utc": utc_now(),
            "combined_apparent_bytes": baseline["combined_apparent_bytes"],
            "combined_allocated_bytes": baseline["combined_allocated_bytes"],
            "host_vhdx_bytes": baseline["host_vhdx_bytes"],
        }
        state["active_overlap_transaction"] = None
        state["last_event_utc"] = state["overlap_storage_baseline"]["utc"]
        workflow = {
            "schema_version": "m9-overlap-workflow-state-v1",
            "stage": "AUDIT_PASSED",
            "contract_sha256": hashlib.sha256(OVERLAP_CONTRACT.read_bytes()).hexdigest(),
            "completed_structure_ids": [],
            "next_structure_id": "500",
            "active_structure_id": None,
            "active_transaction": None,
            "apt_install_completed": False,
            "hard_stopped": False,
        }
        atomic_json(STATE_PATH, state)
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
        OVERLAP_CAPABILITY_ROOT.mkdir(mode=0o700, parents=False, exist_ok=False)
        transaction["state"] = "IDLE"
        transaction["completed_utc"] = utc_now()
        atomic_json(OVERLAP_TRANSACTION, transaction)
        append_event(
            {
                "event": "OVERLAP_BUDGET_START",
                "utc": state["last_event_utc"],
                "storage_baseline": state["overlap_storage_baseline"],
                "cpu_seconds": state["cpu_seconds"],
                "storage_limit_bytes": OVERLAP_STORAGE_LIMIT,
                "python_bootstrap": bootstrap,
            }
        )
        print(json.dumps({"status": "initialized", "baseline": baseline}, sort_keys=True))
        return 0


def load_workflow_state_budget() -> dict:
    value = json.loads(OVERLAP_WORKFLOW_STATE.read_text(encoding="utf-8"))
    if value.get("schema_version") != "m9-overlap-workflow-state-v1":
        raise SystemExit("invalid overlap workflow state schema")
    return value


def overlap_status_payload(state: dict) -> dict:
    return {
        "wall_clock_mode": wall_clock_policy_mode(state),
        "historical_deadline_utc": state.get("deadline_utc"),
        "deadline_remaining_seconds": deadline_remaining(state),
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
        "effective_cpu_seconds": {
            bucket: effective_cpu_seconds(state, bucket) for bucket in CPU_LIMITS
        },
        "cpu_adjustments": state.get("cpu_adjustments", []),
        "storage": storage_snapshot(state),
        "violations": violations(state),
    }


def hard_stop_both(
    budget_state: dict,
    workflow: dict,
    reasons: list[str],
    transaction: dict,
    command_hash: str | None,
) -> None:
    now = utc_now()
    transaction["state"] = "FAILED_PENDING_COMMIT"
    transaction.setdefault("state_history", []).append({"state": "FAILED_PENDING_COMMIT", "utc": now})
    transaction["failure_utc"] = now
    transaction["reasons"] = sorted(set(reasons))
    atomic_json(OVERLAP_TRANSACTION, transaction)
    budget_state["hard_stopped"] = True
    budget_state["active_overlap_transaction"] = None
    budget_state["last_event_utc"] = now
    workflow["hard_stopped"] = True
    workflow["stage"] = "HARD_STOP"
    workflow["hard_stop_reason"] = sorted(set(reasons))
    workflow["hard_stop_utc"] = now
    workflow["active_transaction"] = None
    atomic_json(STATE_PATH, budget_state)
    atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
    transaction["state"] = "FAILED_COMMITTED"
    transaction.setdefault("state_history", []).append({"state": "FAILED_COMMITTED", "utc": now})
    atomic_json(OVERLAP_TRANSACTION, transaction)
    append_event(
        {
            "event": "OVERLAP_HARD_STOP",
            "utc": now,
            "transaction_id": transaction.get("transaction_id"),
            "reasons": sorted(set(reasons)),
            "command_sha256": command_hash,
            "storage": storage_snapshot(budget_state),
            "gpu_seconds": budget_state["gpu_seconds"],
            "cpu_seconds": budget_state["cpu_seconds"],
        }
    )


def hard_stop_recovery(
    budget_state: dict,
    workflow: dict,
    reasons: list[str],
    transaction: dict,
    command_hash: str | None,
) -> None:
    """Commit recovery failure without overwriting the immutable parent transaction."""
    now = utc_now()
    transaction["state"] = "FAILED_PENDING_COMMIT"
    transaction.setdefault("state_history", []).append({"state": "FAILED_PENDING_COMMIT", "utc": now})
    transaction["failure_utc"] = now
    transaction["reasons"] = sorted(set(reasons))
    atomic_json(OVERLAP_RECOVERY_TRANSACTION, transaction)
    budget_state["hard_stopped"] = True
    budget_state["active_overlap_transaction"] = None
    budget_state["last_event_utc"] = now
    workflow["hard_stopped"] = True
    workflow["stage"] = "HARD_STOP"
    workflow["hard_stop_reason"] = sorted(set(reasons))
    workflow["hard_stop_utc"] = now
    workflow["active_transaction"] = None
    atomic_json(STATE_PATH, budget_state)
    atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
    transaction["state"] = "FAILED_COMMITTED"
    transaction.setdefault("state_history", []).append({"state": "FAILED_COMMITTED", "utc": now})
    atomic_json(OVERLAP_RECOVERY_TRANSACTION, transaction)
    append_event({
        "event": "OVERLAP_OFFLINE_RECOVERY_HARD_STOP",
        "utc": now,
        "transaction_id": transaction.get("transaction_id"),
        "parent_transaction_id": transaction.get("parent_transaction_id"),
        "reasons": sorted(set(reasons)),
        "command_sha256": command_hash,
        "storage": storage_snapshot(budget_state),
        "gpu_seconds": budget_state["gpu_seconds"],
        "cpu_seconds": budget_state["cpu_seconds"],
    })


def validate_overlap_request(args: argparse.Namespace, workflow: dict) -> tuple[str, str, int]:
    action = str(args.overlap_action or "")
    structure_id = None if args.structure_id is None else str(args.structure_id)
    if args.cwd and Path(args.cwd).resolve(strict=False) != LINUX_ROOT.resolve(strict=False):
        raise SystemExit("overlap-only operations require the frozen Linux working root")
    if args.log:
        resolved_log = Path(args.log).resolve(strict=False)
        logs_root = (LINUX_ROOT / "logs").resolve(strict=False)
        if logs_root not in resolved_log.parents:
            raise SystemExit("overlap-only logs must stay below the frozen Linux log root")
    if args.command:
        raise SystemExit("overlap-only operations do not accept a child command or free argv")
    expected_bucket = {
        "apt_install": "overlap_build",
        "source_prepare": "overlap_build",
        "source_build": "overlap_build",
        "smoke_prepare": "overlap_smoke",
        "smoke_run": "overlap_smoke",
        "project": "overlap_smoke",
        "batch_prepare": "overlap_batch",
        "batch_run": "overlap_batch",
    }.get(action)
    if expected_bucket is None or args.cpu_bucket != expected_bucket:
        raise SystemExit("overlap action/CPU bucket mismatch")
    if action in ("smoke_prepare", "smoke_run") and structure_id != "500":
        raise SystemExit("smoke actions require structure 500")
    if action in ("batch_prepare", "batch_run"):
        if (
            structure_id is None
            or not structure_id.isdigit()
            or not 510 <= int(structure_id) <= 4990
            or int(structure_id) % 10
        ):
            raise SystemExit("batch action requires one frozen non-smoke structure ID")
    elif action not in ("smoke_prepare", "smoke_run") and structure_id is not None:
        raise SystemExit("this overlap action does not accept a structure ID")
    expected_stage = {
        "apt_install": "AUDIT_PASSED",
        "source_prepare": "AUDIT_PASSED",
        "source_build": "SOURCES_PREPARED",
        "smoke_prepare": "BUILD_PASSED",
        "smoke_run": "SMOKE_INPUT_READY",
        "project": "SMOKE_PASSED",
        "batch_prepare": ("PROJECTION_PASSED", "BATCH_RUNNING"),
        "batch_run": "BATCH_INPUT_READY",
    }[action]
    stage = workflow.get("stage")
    allowed_stages = expected_stage if isinstance(expected_stage, tuple) else (expected_stage,)
    if workflow.get("hard_stopped") or stage not in allowed_stages:
        raise SystemExit(f"overlap action {action} is forbidden at workflow stage {stage}")
    if action == "source_prepare" and not workflow.get("apt_install_completed"):
        raise SystemExit("source preparation requires successful pinned apt installation")
    if structure_id is not None and workflow.get("next_structure_id") != structure_id:
        raise SystemExit("overlap action violates the next frozen structure ID")
    if action.endswith("_run") and workflow.get("active_structure_id") != structure_id:
        raise SystemExit("overlap run does not match the active prepared structure")
    contract = json.loads(OVERLAP_CONTRACT.read_text(encoding="utf-8"))
    bounds = contract["budget"]["operation_forecast_lower_bounds_bytes"]
    if action in ("batch_prepare", "batch_run"):
        required_forecast = int(workflow.get("per_structure_forecast_bytes", -1))
        if required_forecast <= 0:
            raise SystemExit("batch action lacks a positive projected per-structure forecast")
    else:
        required_forecast = int(bounds[action])
    if args.forecast_bytes is None or args.forecast_bytes < required_forecast:
        raise SystemExit(
            f"forecast {args.forecast_bytes} is below frozen lower bound {required_forecast}"
        )
    return action, expected_bucket, required_forecast


def process_is_live(pid: object) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def process_matches_receipt(receipt: object) -> bool:
    if not isinstance(receipt, dict):
        return False
    try:
        pid = int(receipt["pid"])
        current = process_receipt(pid)
        return (
            current["pgid"] == int(receipt["pgid"])
            and current["starttime_ticks"] == int(receipt["starttime_ticks"])
            and current["cmdline_sha256"] == receipt["cmdline_sha256"]
        )
    except (OSError, KeyError, TypeError, ValueError, IndexError):
        return False


def file_stat_receipt(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "path": path.as_posix(),
        "bytes": stat.st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "uid": stat.st_uid,
        "gid": stat.st_gid,
        "mode": stat.st_mode & 0o777,
    }


def cleanup_assert_single_link(path: Path) -> None:
    if path.is_symlink():
        raise SystemExit("source-control test cleanup forbids symlink paths")
    if path.exists() and os.lstat(path).st_nlink != 1:
        raise SystemExit("source-control test cleanup requires single-link paths")


def cleanup_stat_receipt(path: Path) -> dict[str, object]:
    receipt = file_stat_receipt(path)
    cleanup_assert_single_link(path)
    receipt["nlink"] = int(os.lstat(path).st_nlink)
    return receipt


def assert_cleanup_gate_matches_verified_inode(gate: dict) -> None:
    verified_bytes = gate.get("_verified_gate_bytes")
    verified_sha = gate.get("_verified_gate_sha256")
    verified_stat = gate.get("_verified_gate_stat")
    if (
        not isinstance(verified_bytes, bytes)
        or hashlib.sha256(verified_bytes).hexdigest() != verified_sha
        or not isinstance(verified_stat, dict)
    ):
        raise SystemExit("cleanup verified gate snapshot is missing")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(SOURCE_CONTROL_TEST_CLEANUP_GATE, flags)
    except OSError as exc:
        raise SystemExit("cleanup verified gate path is unavailable") from exc
    with os.fdopen(fd, "rb") as handle:
        current = os.fstat(handle.fileno())
        current_bytes = handle.read()
        current_after = os.fstat(handle.fileno())
    current_receipt = {
        "dev": current.st_dev,
        "ino": current.st_ino,
        "bytes": current.st_size,
        "uid": current.st_uid,
        "gid": current.st_gid,
        "mode": current.st_mode & 0o7777,
        "nlink": current.st_nlink,
    }
    if (
        not stat.S_ISREG(current.st_mode)
        or current.st_nlink != 1
        or current_receipt != verified_stat
        or (current.st_dev, current.st_ino, current.st_size)
        != (current_after.st_dev, current_after.st_ino, current_after.st_size)
        or current_bytes != verified_bytes
    ):
        raise SystemExit("cleanup verified gate path drift")


def stage_cleanup_gate_snapshot(gate: dict) -> dict[str, object]:
    assert_cleanup_gate_matches_verified_inode(gate)
    SOURCE_CONTROL_TEST_TRUST_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    trust_stat = os.lstat(SOURCE_CONTROL_TEST_TRUST_ROOT)
    if (
        not stat.S_ISDIR(trust_stat.st_mode)
        or trust_stat.st_uid != 0
        or trust_stat.st_gid != 0
        or (trust_stat.st_mode & 0o7777) != 0o700
    ):
        raise SystemExit("cleanup trusted root owner/mode mismatch")
    verified_bytes = gate["_verified_gate_bytes"]
    if SOURCE_CONTROL_TEST_GATE_SNAPSHOT.exists():
        cleanup_assert_single_link(SOURCE_CONTROL_TEST_GATE_SNAPSHOT)
        metadata = cleanup_receipt_file_metadata(SOURCE_CONTROL_TEST_GATE_SNAPSHOT)
        if (
            SOURCE_CONTROL_TEST_GATE_SNAPSHOT.read_bytes() != verified_bytes
            or any(metadata.get(key) != value for key, value in {"uid": 0, "gid": 0, "mode": 0o600}.items())
        ):
            raise SystemExit("cleanup verified gate snapshot mismatch")
    else:
        atomic_root_private_bytes(SOURCE_CONTROL_TEST_GATE_SNAPSHOT, verified_bytes)
    assert_cleanup_gate_matches_verified_inode(gate)
    snapshot = cleanup_stat_receipt(SOURCE_CONTROL_TEST_GATE_SNAPSHOT)
    if snapshot.get("sha256") != gate["_verified_gate_sha256"] or any(snapshot.get(key) != value for key, value in {"uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}.items()):
        raise SystemExit("cleanup verified gate snapshot receipt mismatch")
    return snapshot


def cleanup_security_migration_binding(gate: dict) -> dict[str, object]:
    parent = MANIFESTS
    expected_before = {"path": parent.as_posix(), "uid": 1000, "gid": 1000, "mode": 0o755}
    expected_hardened = {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770}
    expected_parent = {
        "path": parent.as_posix(),
        "before": expected_before,
        "hardened": expected_hardened,
        "after": expected_hardened,
    }
    expected_artifact = {
        "active_path": SOURCE_CONTROL_TEST_ARTIFACT.as_posix(),
        "retired_path": SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.as_posix(),
        "before": {"uid": 1000, "gid": 1000, "mode": 0o644},
        "hardened": {"uid": 0, "gid": 0, "mode": 0o600},
    }
    security = gate.get("cleanup_parent_security")
    if not isinstance(security, dict) or security != {
        "before": expected_before,
        "hardened": expected_hardened,
        "after": expected_hardened,
    }:
        raise SystemExit("cleanup parent security contract mismatch")
    migration = gate.get("cleanup_security_migration")
    expected_migration = {
        "schema_version": "m9-source-control-test-security-migration-v1",
        "path": SOURCE_CONTROL_TEST_SECURITY_MIGRATION.as_posix(),
    }
    if migration != expected_migration:
        raise SystemExit("cleanup security migration binding mismatch")
    expected_trust_root = {"path": SOURCE_CONTROL_TEST_TRUST_ROOT.as_posix(), "uid": 0, "gid": 0, "mode": 0o700}
    expected_snapshot = {"path": SOURCE_CONTROL_TEST_GATE_SNAPSHOT.as_posix(), "uid": 0, "gid": 0, "mode": 0o600}
    if gate.get("cleanup_trust_root") != expected_trust_root or gate.get("cleanup_verified_gate_snapshot") != expected_snapshot:
        raise SystemExit("cleanup trusted snapshot gate binding mismatch")
    required_gate = {
        "decision_id": "D-017-source-control-test-cleanup-v1",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
    }
    if any(gate.get(key) != value for key, value in required_gate.items()):
        raise SystemExit("cleanup security migration gate verdict mismatch")
    snapshot = stage_cleanup_gate_snapshot(gate)
    expected_gate_binding = {
        "decision_id": required_gate["decision_id"],
        "gate_path": SOURCE_CONTROL_TEST_CLEANUP_GATE.as_posix(),
        "gate_sha256": gate["_verified_gate_sha256"],
        "gate_inode": gate["_verified_gate_stat"],
        "snapshot": snapshot,
        "authorization_sha256": gate.get("authorization_sha256"),
        "frozen_sha256": gate.get("frozen_sha256"),
        "audit_report_sha256": gate.get("audit_report_sha256"),
        "artifact_sha256": gate.get("artifact_sha256"),
        "runtime_sha256": gate.get("runtime_sha256"),
    }
    if any(
        not value or (key.endswith("sha256") and key != "runtime_sha256" and (not isinstance(value, str) or len(value) != 64))
        for key, value in expected_gate_binding.items()
    ) or not isinstance(expected_gate_binding["runtime_sha256"], dict):
        raise SystemExit("cleanup security migration gate evidence mismatch")
    return {
        "schema_version": expected_migration["schema_version"],
        "path": expected_migration["path"],
        "gate_binding": expected_gate_binding,
        "parent": expected_parent,
        "artifact": expected_artifact,
    }


def load_cleanup_security_migration(gate: dict) -> dict[str, object]:
    binding = cleanup_security_migration_binding(gate)
    try:
        journal = json.loads(SOURCE_CONTROL_TEST_SECURITY_MIGRATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("cleanup security migration journal invalid") from exc
    allowed_states = {
        "PREPARED", "PARENT_OWNER", "PARENT_HARDENED",
        "ARTIFACT_OWNER", "ARTIFACT_HARDENED", "SUCCESS_COMMITTED",
    }
    if (
        journal.get("schema_version") != binding["schema_version"]
        or journal.get("path") != binding["path"]
        or journal.get("gate_binding") != binding["gate_binding"]
        or journal.get("parent") != binding["parent"]
        or journal.get("artifact") != binding["artifact"]
        or journal.get("state") not in allowed_states
        or set(journal) - {"schema_version", "path", "state", "gate_binding", "parent", "artifact", "completed_utc"}
    ):
        raise SystemExit("cleanup security migration journal binding mismatch")
    cleanup_assert_single_link(SOURCE_CONTROL_TEST_SECURITY_MIGRATION)
    metadata = cleanup_receipt_file_metadata(SOURCE_CONTROL_TEST_SECURITY_MIGRATION)
    if any(metadata.get(key) != value for key, value in {"uid": 0, "gid": 0, "mode": 0o600}.items()):
        raise SystemExit("cleanup security migration journal owner/mode mismatch")
    if journal["state"] == "SUCCESS_COMMITTED":
        if not isinstance(journal.get("completed_utc"), str):
            raise SystemExit("cleanup security migration completion missing")
        try:
            parse_utc(str(journal["completed_utc"]))
        except (TypeError, ValueError):
            raise SystemExit("cleanup security migration completion invalid")
    elif "completed_utc" in journal:
        raise SystemExit("cleanup security migration premature completion")
    return journal


def write_cleanup_security_migration(journal: dict[str, object]) -> None:
    atomic_root_private_json(SOURCE_CONTROL_TEST_SECURITY_MIGRATION, journal)


def validate_cleanup_artifact_before_security(gate: dict) -> None:
    if gate.get("cleanup_parent_security") is None:
        return
    active_exists = SOURCE_CONTROL_TEST_ARTIFACT.is_file()
    retired_exists = SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file()
    if active_exists == retired_exists:
        raise SystemExit("cleanup security requires exactly one artifact path")
    path = SOURCE_CONTROL_TEST_ARTIFACT if active_exists else SOURCE_CONTROL_TEST_ARTIFACT_RETIRED
    receipt = cleanup_stat_receipt(path)
    if receipt.get("bytes") != 1644 or receipt.get("sha256") != "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74":
        raise SystemExit("cleanup security artifact content mismatch")
    actual = {key: receipt.get(key) for key in ("uid", "gid", "mode")}
    allowed = (
        {"uid": 1000, "gid": 1000, "mode": 0o644},
        {"uid": 0, "gid": 0, "mode": 0o644},
        {"uid": 0, "gid": 0, "mode": 0o600},
    )
    if actual not in allowed or receipt.get("nlink") != 1:
        raise SystemExit("cleanup security artifact owner/mode mismatch")
    if not SOURCE_CONTROL_TEST_SECURITY_MIGRATION.exists():
        if not active_exists or actual != allowed[0]:
            raise SystemExit("cleanup security initial artifact precondition mismatch")
        return
    journal = load_cleanup_security_migration(gate)
    rank = {
        "PREPARED": 0, "PARENT_OWNER": 1, "PARENT_HARDENED": 2,
        "ARTIFACT_OWNER": 3, "ARTIFACT_HARDENED": 4, "SUCCESS_COMMITTED": 5,
    }[str(journal["state"])]
    maximum_rank = {0: 2, 1: 3, 2: 5}[allowed.index(actual)]
    if rank > maximum_rank:
        raise SystemExit("cleanup security artifact journal is ahead of filesystem")


def prepare_cleanup_parent_security(gate: dict) -> dict[str, object] | None:
    security = gate.get("cleanup_parent_security")
    if security is None:
        return None
    parent = MANIFESTS
    binding = cleanup_security_migration_binding(gate)
    expected_before = binding["parent"]["before"]
    expected_hardened = binding["parent"]["hardened"]
    def actual_state() -> dict[str, object]:
        current = os.lstat(parent)
        return {"path": parent.as_posix(), "uid": current.st_uid, "gid": current.st_gid, "mode": current.st_mode & 0o7777}
    if SOURCE_CONTROL_TEST_SECURITY_MIGRATION.exists():
        journal = load_cleanup_security_migration(gate)
    else:
        if actual_state() != expected_before:
            raise SystemExit("cleanup parent security initial precondition mismatch")
        journal = dict(binding, state="PREPARED")
        write_cleanup_security_migration(journal)
        journal = load_cleanup_security_migration(gate)
    actual = actual_state()
    state_rank = {
        "PREPARED": 0, "PARENT_OWNER": 1, "PARENT_HARDENED": 2,
        "ARTIFACT_OWNER": 3, "ARTIFACT_HARDENED": 4, "SUCCESS_COMMITTED": 5,
    }
    if actual == expected_hardened:
        assert_cleanup_gate_matches_verified_inode(gate)
        if state_rank[str(journal["state"])] < state_rank["PARENT_HARDENED"]:
            journal["state"] = "PARENT_HARDENED"
            write_cleanup_security_migration(journal)
        return actual
    transitional_owner_only = {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o755}
    if actual not in (expected_before, transitional_owner_only):
        raise SystemExit("cleanup parent security precondition mismatch")
    if state_rank[str(journal["state"])] > state_rank["PARENT_OWNER"]:
        raise SystemExit("cleanup parent security journal is ahead of filesystem")
    if actual == expected_before:
        os.chown(parent, 0, 1000)
        assert_cleanup_gate_matches_verified_inode(gate)
        actual = actual_state()
        if actual != transitional_owner_only:
            raise SystemExit("cleanup parent security owner migration mismatch")
    if journal["state"] == "PREPARED":
        journal["state"] = "PARENT_OWNER"
        write_cleanup_security_migration(journal)
    os.chmod(parent, 0o1770)
    assert_cleanup_gate_matches_verified_inode(gate)
    actual = actual_state()
    if actual != expected_hardened:
        raise SystemExit("cleanup parent security hardening mismatch")
    journal["state"] = "PARENT_HARDENED"
    write_cleanup_security_migration(journal)
    return actual


def restore_cleanup_parent_security(gate: dict, enabled: bool) -> None:
    if not enabled:
        return
    security = gate.get("cleanup_parent_security")
    parent = MANIFESTS
    current = os.lstat(parent)
    hardened = security["hardened"]
    after = security["after"]
    actual = {"path": parent.as_posix(), "uid": current.st_uid, "gid": current.st_gid, "mode": current.st_mode & 0o7777}
    if actual != hardened:
        raise SystemExit("cleanup parent security restore precondition mismatch")
    if actual != after:
        raise SystemExit("cleanup parent security restore mismatch")


def commit_cleanup_security_migration(gate: dict, enabled: bool) -> None:
    if not enabled:
        return
    if not SOURCE_CONTROL_TEST_SECURITY_MIGRATION.is_file():
        raise SystemExit("cleanup security migration journal missing")
    journal = load_cleanup_security_migration(gate)
    parent = MANIFESTS
    current = os.lstat(parent)
    if current.st_uid != 0 or current.st_gid != 1000 or (current.st_mode & 0o7777) != 0o1770:
        raise SystemExit("cleanup security migration parent is not hardened")
    if SOURCE_CONTROL_TEST_ARTIFACT.exists() or not SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file():
        raise SystemExit("cleanup security migration artifact paths mismatch")
    retired = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
    if any(retired.get(key) != value for key, value in {"uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}.items()):
        raise SystemExit("cleanup security migration retired security mismatch")
    if not SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL.is_file() or not SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.is_file():
        raise SystemExit("cleanup security migration terminal evidence missing")
    cleanup_journal = json.loads(SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL.read_text(encoding="utf-8"))
    if cleanup_journal.get("state") != "SUCCESS_COMMITTED" or cleanup_journal.get("retired_receipt") != retired:
        raise SystemExit("cleanup security migration terminal journal mismatch")
    if journal["state"] == "SUCCESS_COMMITTED":
        return
    if journal["state"] != "ARTIFACT_HARDENED":
        raise SystemExit("cleanup security migration is not ready to commit")
    journal["state"] = "SUCCESS_COMMITTED"
    journal["completed_utc"] = utc_now()
    write_cleanup_security_migration(journal)


def harden_cleanup_artifact(path: Path, enabled: bool, gate: dict) -> None:
    if not enabled or not path.exists():
        return
    cleanup_assert_single_link(path)
    if path not in (SOURCE_CONTROL_TEST_ARTIFACT, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED):
        raise SystemExit("cleanup artifact security path mismatch")
    if not SOURCE_CONTROL_TEST_SECURITY_MIGRATION.is_file():
        raise SystemExit("cleanup security migration journal missing")
    journal = load_cleanup_security_migration(gate)
    state_rank = {
        "PREPARED": 0, "PARENT_OWNER": 1, "PARENT_HARDENED": 2,
        "ARTIFACT_OWNER": 3, "ARTIFACT_HARDENED": 4, "SUCCESS_COMMITTED": 5,
    }
    if state_rank[str(journal["state"])] < state_rank["PARENT_HARDENED"]:
        raise SystemExit("cleanup artifact security parent migration incomplete")
    current = os.lstat(path)
    actual = {"uid": current.st_uid, "gid": current.st_gid, "mode": current.st_mode & 0o7777}
    before = journal["artifact"]["before"]
    hardened = journal["artifact"]["hardened"]
    transitional_owner_only = {"uid": 0, "gid": 0, "mode": 0o644}
    if actual == hardened:
        if state_rank[str(journal["state"])] < state_rank["ARTIFACT_HARDENED"]:
            journal["state"] = "ARTIFACT_HARDENED"
            write_cleanup_security_migration(journal)
        return
    if actual not in (before, transitional_owner_only):
        raise SystemExit("cleanup artifact security precondition mismatch")
    if state_rank[str(journal["state"])] > state_rank["ARTIFACT_OWNER"]:
        raise SystemExit("cleanup artifact security journal is ahead of filesystem")
    if actual == before:
        os.chown(path, 0, 0)
        current = os.lstat(path)
        actual = {"uid": current.st_uid, "gid": current.st_gid, "mode": current.st_mode & 0o7777}
        if actual != transitional_owner_only:
            raise SystemExit("cleanup artifact security owner migration mismatch")
    if state_rank[str(journal["state"])] < state_rank["ARTIFACT_OWNER"]:
        journal["state"] = "ARTIFACT_OWNER"
        write_cleanup_security_migration(journal)
    os.chmod(path, 0o600)
    cleanup_assert_single_link(path)
    current = os.lstat(path)
    if {"uid": current.st_uid, "gid": current.st_gid, "mode": current.st_mode & 0o7777} != hardened:
        raise SystemExit("cleanup artifact security hardening mismatch")
    journal["state"] = "ARTIFACT_HARDENED"
    write_cleanup_security_migration(journal)


def cleanup_atomic_json(path: Path, value: dict, security_enabled: bool) -> None:
    if security_enabled:
        atomic_root_private_json(path, value)
    else:
        atomic_private_json(path, value)


def source_control_preflight(gate: dict) -> tuple[dict, Path, dict]:
    state = load_state()
    workflow = load_workflow_state_budget()
    if not state.get("hard_stopped") or not workflow.get("hard_stopped") or workflow.get("stage") != "HARD_STOP":
        raise SystemExit("source-control recovery requires dual HARD_STOP")
    if state.get("active_overlap_transaction") is not None or workflow.get("active_transaction") is not None or not workflow.get("apt_install_completed"):
        raise SystemExit("source-control recovery requires no active transaction and completed apt recovery")
    tx = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
    tx_bytes = OVERLAP_TRANSACTION.read_bytes()
    expected = gate["expected_failed_transaction"]
    if hashlib.sha256(tx_bytes).hexdigest() != expected.get("sha256") or tx.get("transaction_id") != expected.get("transaction_id"):
        raise SystemExit("failed source transaction binding mismatch")
    for key, value in {"state": "FAILED_COMMITTED", "action": "source_prepare", "bucket": "overlap_build", "exit_code": 1, "timed_out": False, "forecast_bytes": 1073741824, "required_forecast_bytes": 1073741824}.items():
        if tx.get(key) != value:
            raise SystemExit(f"failed source transaction field mismatch: {key}")
    if tx.get("reasons") != ["overlap_command_failed"] or tx.get("child_pid") is None or process_is_live(tx.get("child_pid")):
        raise SystemExit("failed source transaction outcome mismatch")
    if gate.get("expected_state_sha256") != hashlib.sha256(STATE_PATH.read_bytes()).hexdigest() or gate.get("expected_workflow_sha256") != hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest() or gate.get("expected_ledger_sha256") != hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest():
        raise SystemExit("source-control preflight state/workflow/ledger hash mismatch")
    recovery = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
    if recovery.get("state") != "SUCCESS_COMMITTED" or recovery.get("raw_overlap_build_seconds") != 7200.075310528:
        raise SystemExit("D-017 recovery success binding mismatch")
    manifest, _ = recovery_manifest()
    package_names = [str(item["package"]) for item in manifest["packages"]]
    post = recovery_dpkg_query(package_names)
    expected_target = {str(item["package"]): f"{item['version']}\tinstall ok installed" for item in manifest["packages"]}
    if post != expected_target:
        raise SystemExit("D-017 package post-state mismatch")
    live = sorted(p for p in OVERLAP_CAPABILITY_ROOT.glob("*.json") if not p.name.endswith(".retired.json"))
    if len(live) != 1:
        raise SystemExit("source-control recovery requires exactly one active stale capability")
    cap = live[0]
    cap_value = json.loads(cap.read_text(encoding="utf-8"))
    cap_stat = file_stat_receipt(cap)
    if cap_value.get("state") != "BOUND" or cap_value.get("transaction_id") != tx.get("transaction_id") or cap_value.get("action") != "source_prepare" or cap_stat["uid"] != 1000 or cap_stat["gid"] != 1000 or cap_stat["mode"] != 0o600:
        raise SystemExit("stale capability binding or ownership mismatch")
    if cap_value.get("child_pid") != tx.get("child_pid") or cap_value.get("budget_pid") is None or process_is_live(cap_value.get("child_pid")) or process_is_live(cap_value.get("budget_pid")):
        raise SystemExit("stale capability process binding mismatch")
    cap_id = cap_value.get("capability_id")
    expected_cap = gate.get("expected_stale_capability", {})
    for key, actual in {
        "path": cap.resolve(strict=False).as_posix(),
        "capability_id": cap_id,
        "bytes": cap_stat["bytes"],
        "sha256": cap_stat["sha256"],
        "uid": cap_stat["uid"],
        "gid": cap_stat["gid"],
        "mode": cap_stat["mode"],
    }.items():
        if expected_cap.get(key) != actual:
            raise SystemExit(f"stale capability gate binding mismatch: {key}")
    for suffix in (".consumed.json", ".launcher-receipt.json"):
        if (OVERLAP_CAPABILITY_ROOT / f"{cap_id}{suffix}").exists():
            raise SystemExit("source-control recovery refuses an already-consumed capability")
    if any(path.exists() for path in SOURCE_RECOVERY_PRODUCTS):
        raise SystemExit("source-control recovery refuses existing source/build products")
    return tx, cap, cap_stat


def source_control_hard_stop(recovery: dict, reasons: list[str]) -> None:
    state = load_state()
    workflow = load_workflow_state_budget()
    state["hard_stopped"] = True
    state["active_overlap_transaction"] = None
    workflow["hard_stopped"] = True
    workflow["stage"] = "HARD_STOP"
    workflow["active_transaction"] = None
    workflow["hard_stop_reason"] = sorted(set(reasons))
    workflow["hard_stop_utc"] = utc_now()
    if recovery.get("state") == "FAILED_COMMITTED" and recovery.get("failure_reasons"):
        history = recovery.setdefault("failure_history", [])
        prior = {
            "state": "FAILED_COMMITTED",
            "failure_reasons": recovery.get("failure_reasons"),
        }
        if not history or history[-1] != prior:
            history.append(prior)
    recovery["state"] = "FAILED_COMMITTED"
    recovery["failure_reasons"] = sorted(set(reasons))
    atomic_owned_json(STATE_PATH, state)
    atomic_owned_json(OVERLAP_WORKFLOW_STATE, workflow)
    atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)


def verify_source_control_test_cleanup_gate() -> dict:
    if not SOURCE_CONTROL_TEST_CLEANUP_GATE.is_file():
        raise SystemExit("source-control test cleanup gate is missing")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(SOURCE_CONTROL_TEST_CLEANUP_GATE, flags)
    except OSError as exc:
        raise SystemExit("source-control test cleanup gate cannot be opened safely") from exc
    with os.fdopen(fd, "rb") as handle:
        gate_stat = os.fstat(handle.fileno())
        gate_bytes = handle.read()
        gate_stat_after = os.fstat(handle.fileno())
    if (
        not stat.S_ISREG(gate_stat.st_mode)
        or gate_stat.st_nlink != 1
        or (gate_stat.st_dev, gate_stat.st_ino, gate_stat.st_size)
        != (gate_stat_after.st_dev, gate_stat_after.st_ino, gate_stat_after.st_size)
        or gate_stat.st_size != len(gate_bytes)
    ):
        raise SystemExit("source-control test cleanup gate inode is unstable")
    try:
        gate = json.loads(gate_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("source-control test cleanup gate is invalid JSON") from exc
    if gate.get("schema_version") != "m9-source-control-test-cleanup-gate-v1" or gate.get("decision_id") != "D-017-source-control-test-cleanup-v1" or gate.get("status") != "PASS" or int(gate.get("blocking", -1)) != 0 or int(gate.get("non_blocking", -1)) != 0:
        raise SystemExit("source-control test cleanup gate is not zero-issue PASS")
    report = Path(str(gate.get("audit_report_path", ""))).resolve(strict=False)
    if report.parent != AUDITS.resolve(strict=False) or report.suffix.lower() != ".json" or not report.is_file():
        raise SystemExit("cleanup audit report path is not bounded to 08_audits")
    if hashlib.sha256(report.read_bytes()).hexdigest() != gate.get("audit_report_sha256"):
        raise SystemExit("cleanup audit report hash mismatch")
    payload = json.loads(report.read_text(encoding="utf-8"))
    if payload.get("verdict") != "PASS" or int(payload.get("blocking", -1)) != 0 or int(payload.get("non_blocking", -1)) != 0:
        raise SystemExit("cleanup audit report is not zero-issue PASS")
    if gate.get("authorization_path") != SOURCE_CONTROL_TEST_CLEANUP_AUTH.as_posix() or not SOURCE_CONTROL_TEST_CLEANUP_AUTH.is_file() or hashlib.sha256(SOURCE_CONTROL_TEST_CLEANUP_AUTH.read_bytes()).hexdigest() != gate.get("authorization_sha256"):
        raise SystemExit("cleanup authorization binding mismatch")
    if gate.get("frozen_path") != SOURCE_CONTROL_TEST_CLEANUP_FROZEN.as_posix() or not SOURCE_CONTROL_TEST_CLEANUP_FROZEN.is_file() or hashlib.sha256(SOURCE_CONTROL_TEST_CLEANUP_FROZEN.read_bytes()).hexdigest() != gate.get("frozen_sha256"):
        raise SystemExit("cleanup frozen binding mismatch")
    frozen = json.loads(SOURCE_CONTROL_TEST_CLEANUP_FROZEN.read_text(encoding="utf-8"))
    if frozen.get("schema_version") != "m9-source-control-test-cleanup-frozen-hashes-v1" or frozen.get("decision_id") != "D-017-source-control-test-cleanup-v1":
        raise SystemExit("cleanup frozen schema/decision mismatch")
    if frozen.get("artifact_sha256") != "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74":
        raise SystemExit("cleanup artifact hash binding mismatch")
    required_runtime = set(cleanup_expected_runtime_hashes())
    if set(frozen.get("runtime_sha256", {})) != required_runtime:
        raise SystemExit("cleanup runtime closed set mismatch")
    expected_runtime = cleanup_expected_runtime_hashes()
    if frozen.get("runtime_sha256") != expected_runtime or gate.get("runtime_sha256") != expected_runtime:
        raise SystemExit("cleanup runtime hash values mismatch")
    expected_files = {REPRODUCTION / "scripts/m9_budget.py", REPRODUCTION / "tests/test_m9_overlap_controls.py", SOURCE_CONTROL_TEST_CLEANUP_AUTH, SOURCE_CONTROL_RECOVERY_FROZEN_HASHES}
    if set(Path(str(p)).resolve(strict=False) for p in frozen.get("files", {})) != {p.resolve(strict=False) for p in expected_files}:
        raise SystemExit("cleanup frozen file closed set mismatch")
    runtime = frozen.get("runtime_sha256")
    if not isinstance(runtime, dict) or gate.get("artifact_sha256") != frozen.get("artifact_sha256") or gate.get("runtime_sha256") != runtime:
        raise SystemExit("cleanup gate artifact/runtime binding mismatch")
    if gate.get("source_control_gate_absent") is not True or gate.get("source_control_parent_absent") is not True:
        raise SystemExit("cleanup gate source-control absence binding mismatch")
    expected_security = {
        "before": {"path": MANIFESTS.as_posix(), "uid": 1000, "gid": 1000, "mode": 0o755},
        "hardened": {"path": MANIFESTS.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770},
        "after": {"path": MANIFESTS.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770},
    }
    if gate.get("cleanup_parent_security") != expected_security:
        raise SystemExit("cleanup parent security binding mismatch")
    expected_migration = {"schema_version": "m9-source-control-test-security-migration-v1", "path": SOURCE_CONTROL_TEST_SECURITY_MIGRATION.as_posix()}
    if gate.get("cleanup_security_migration") != expected_migration:
        raise SystemExit("cleanup security migration gate binding mismatch")
    expected_trust_root = {"path": SOURCE_CONTROL_TEST_TRUST_ROOT.as_posix(), "uid": 0, "gid": 0, "mode": 0o700}
    expected_snapshot = {"path": SOURCE_CONTROL_TEST_GATE_SNAPSHOT.as_posix(), "uid": 0, "gid": 0, "mode": 0o600}
    if gate.get("cleanup_trust_root") != expected_trust_root or gate.get("cleanup_verified_gate_snapshot") != expected_snapshot:
        raise SystemExit("cleanup trusted snapshot binding mismatch")
    if gate.get("protected_hardlinks") != "1":
        raise SystemExit("cleanup protected_hardlinks binding mismatch")
    try:
        protected_hardlinks = Path("/proc/sys/fs/protected_hardlinks").read_text(encoding="ascii").strip()
    except OSError as exc:
        raise SystemExit("cleanup protected_hardlinks unavailable") from exc
    if protected_hardlinks != "1":
        raise SystemExit("cleanup requires fs.protected_hardlinks=1")
    for path_text, expected in frozen.get("files", {}).items():
        path = Path(path_text)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"cleanup frozen file mismatch: {path}")
    gate = dict(gate)
    gate["_verified_gate_bytes"] = gate_bytes
    gate["_verified_gate_sha256"] = hashlib.sha256(gate_bytes).hexdigest()
    gate["_verified_gate_stat"] = {
        "dev": gate_stat.st_dev,
        "ino": gate_stat.st_ino,
        "bytes": gate_stat.st_size,
        "uid": gate_stat.st_uid,
        "gid": gate_stat.st_gid,
        "mode": gate_stat.st_mode & 0o7777,
        "nlink": gate_stat.st_nlink,
    }
    return gate


def cleanup_runtime_receipt() -> dict[str, str]:
    expected = cleanup_expected_runtime_hashes()
    actual = {}
    for path_text, value in expected.items():
        path = Path(path_text)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != value:
            raise SystemExit(f"runtime evidence drift: {path}")
        actual[path.as_posix()] = value
    if SOURCE_CONTROL_RECOVERY_GATE.exists() or SOURCE_CONTROL_RECOVERY_PARENT.exists():
        raise SystemExit("source-control recovery objects must remain absent")
    return actual


def cleanup_expected_runtime_hashes() -> dict[str, str]:
    return {
        STATE_PATH.as_posix(): "1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc",
        OVERLAP_WORKFLOW_STATE.as_posix(): "2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d",
        OVERLAP_TRANSACTION.as_posix(): "12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309",
        LEDGER_PATH.as_posix(): "25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f",
        (OVERLAP_CAPABILITY_ROOT / "f7c3b060e19e37e6da03f461d754d38c.json").as_posix(): "0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e",
    }


def cleanup_receipt_file_metadata(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "path": path.as_posix(),
        "bytes": stat.st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "uid": stat.st_uid,
        "gid": stat.st_gid,
        "mode": stat.st_mode & 0o777,
    }


def validate_cleanup_receipt(
    receipt: object,
    original: dict[str, object],
    retired: dict[str, object],
    context: dict[str, object],
    bootstrap: dict[str, object],
    receipt_path: Path,
) -> None:
    if not isinstance(receipt, dict):
        raise SystemExit("cleanup receipt is not an object")
    if (
        receipt.get("schema_version") != "m9-source-control-test-artifact-retirement-v1"
        or receipt.get("status") != "PASS"
        or receipt.get("reason") != "test_isolation_failure_artifact"
        or receipt.get("original") != original
        or receipt.get("retired") != retired
        or receipt.get("context") != context
        or receipt.get("python_bootstrap") != bootstrap
        or not isinstance(receipt.get("utc"), str)
    ):
        raise SystemExit("cleanup receipt content mismatch")
    try:
        parse_utc(str(receipt["utc"]))
    except (TypeError, ValueError):
        raise SystemExit("cleanup receipt timestamp mismatch")
    expected_metadata = context.get("cleanup_file_security", {"uid": 1000, "gid": 1000, "mode": 0o600})
    metadata = cleanup_receipt_file_metadata(receipt_path)
    if any(metadata.get(key) != value for key, value in expected_metadata.items()):
        raise SystemExit("cleanup receipt owner/mode mismatch")


def command_retire_source_control_test_artifact(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("test-artifact retirement requires root")
    expected_sha = "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74"
    expected = {
        "bytes": 1644, "uid": 1000, "gid": 1000, "mode": 0o644,
    }
    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        bootstrap = isolated_bootstrap_provenance()
        gate = verify_source_control_test_cleanup_gate()
        fixed_runtime = cleanup_runtime_receipt()
        validate_cleanup_artifact_before_security(gate)
        parent_security = prepare_cleanup_parent_security(gate)
        security_enabled = parent_security is not None
        harden_cleanup_artifact(SOURCE_CONTROL_TEST_ARTIFACT, security_enabled, gate)
        harden_cleanup_artifact(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED, security_enabled, gate)
        if security_enabled:
            expected["uid"] = 0
            expected["gid"] = 0
            expected["mode"] = 0o600
        cleanup_paths = (SOURCE_CONTROL_TEST_ARTIFACT, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL)
        if security_enabled:
            cleanup_paths = cleanup_paths + (SOURCE_CONTROL_TEST_SECURITY_MIGRATION, SOURCE_CONTROL_TEST_GATE_SNAPSHOT)
        for path in cleanup_paths:
            cleanup_assert_single_link(path)
        if security_enabled:
            assert_cleanup_gate_matches_verified_inode(gate)
            gate_sha = gate["_verified_gate_sha256"]
            migration_journal = load_cleanup_security_migration(gate)
        else:
            gate_sha = hashlib.sha256(SOURCE_CONTROL_TEST_CLEANUP_GATE.read_bytes()).hexdigest()
            migration_journal = None
        cleanup_context = {
            "gate_sha256": gate_sha,
            "frozen_sha256": gate["frozen_sha256"],
            "authorization_sha256": gate["authorization_sha256"],
            "audit_report_sha256": gate["audit_report_sha256"],
            "artifact_sha256": gate["artifact_sha256"],
            "fixed_runtime_sha256": fixed_runtime,
        }
        if parent_security is not None:
            cleanup_context["cleanup_parent_security"] = parent_security
            cleanup_context["cleanup_file_security"] = {"uid": 0, "gid": 0, "mode": 0o600}
            cleanup_context["protected_hardlinks"] = "1"
            cleanup_context["verified_gate_snapshot"] = migration_journal["gate_binding"]["snapshot"]
        journal_path = SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL
        if journal_path.exists():
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            if journal.get("schema_version") != "m9-source-control-test-artifact-cleanup-v1":
                raise SystemExit("cleanup journal schema mismatch")
            if journal.get("original_path") != SOURCE_CONTROL_TEST_ARTIFACT.as_posix() or journal.get("retired_path") != SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.as_posix():
                raise SystemExit("cleanup journal path binding mismatch")
            if journal.get("context") != cleanup_context:
                raise SystemExit("cleanup journal binding mismatch")
            if journal.get("python_bootstrap") != bootstrap:
                raise SystemExit("cleanup journal bootstrap binding mismatch")
            if journal.get("state") == "SUCCESS_COMMITTED":
                if SOURCE_CONTROL_TEST_ARTIFACT.exists() or not SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file() or not SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.is_file():
                    raise SystemExit("cleanup terminal artifact paths mismatch")
                saved = json.loads(SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.read_text(encoding="utf-8"))
                retired_check = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
                validate_cleanup_receipt(saved, journal.get("original_receipt"), retired_check, cleanup_context, bootstrap, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT)
                if saved.get("context") != cleanup_context or saved.get("original") != journal.get("original_receipt") or saved.get("original", {}).get("path") != SOURCE_CONTROL_TEST_ARTIFACT.as_posix() or journal.get("retired_receipt") != retired_check or saved.get("retired") != retired_check or saved.get("status") != "PASS":
                    raise SystemExit("cleanup terminal receipt mismatch")
                if any(retired_check.get(k) != v for k, v in expected.items()) or retired_check.get("sha256") != expected_sha:
                    raise SystemExit("cleanup terminal retired receipt mismatch")
                commit_cleanup_security_migration(gate, security_enabled)
                restore_cleanup_parent_security(gate, security_enabled)
                print(json.dumps({"status": "test_artifact_already_retired", "sha256": expected_sha}, sort_keys=True))
                return 0
            if journal.get("state") not in {"PREPARED", "RENAMED"}:
                raise SystemExit("cleanup journal is not resumable")
            original_receipt = journal.get("original_receipt")
            if not isinstance(original_receipt, dict) or original_receipt.get("path") != SOURCE_CONTROL_TEST_ARTIFACT.as_posix() or original_receipt.get("sha256") != expected_sha or original_receipt.get("nlink") != 1 or any(original_receipt.get(k) != v for k, v in expected.items()):
                raise SystemExit("cleanup journal original receipt mismatch")
            if journal.get("state") == "PREPARED" and SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.exists():
                raise SystemExit("cleanup PREPARED receipt must be absent")
            if journal.get("state") == "PREPARED":
                active_exists = SOURCE_CONTROL_TEST_ARTIFACT.is_file()
                retired_exists = SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file()
                if active_exists and not retired_exists:
                    active_check = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT)
                    if active_check != original_receipt:
                        raise SystemExit("cleanup PREPARED original receipt drift")
                    cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT)
                    os.replace(SOURCE_CONTROL_TEST_ARTIFACT, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
                    retired_check = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
                    expected_retired = dict(original_receipt, path=SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.as_posix())
                    if retired_check != expected_retired:
                        raise SystemExit("cleanup PREPARED retired receipt drift")
                elif not active_exists and retired_exists:
                    retired_check = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
                    expected_retired = dict(original_receipt, path=SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.as_posix())
                    if retired_check != expected_retired:
                        raise SystemExit("cleanup PREPARED retired receipt drift")
                else:
                    raise SystemExit("cleanup PREPARED artifact paths mismatch")
            if SOURCE_CONTROL_TEST_ARTIFACT.exists() or not SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file():
                raise SystemExit("cleanup resumable artifact paths mismatch")
            retired = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
            if retired.get("sha256") != expected_sha or any(retired.get(k) != v for k, v in expected.items()):
                raise SystemExit("cleanup resumable retired receipt mismatch")
            if journal.get("state") == "RENAMED" and journal.get("retired_receipt") != retired:
                raise SystemExit("cleanup RENAMED journal receipt drift")
            if SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.exists():
                existing_receipt = json.loads(SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.read_text(encoding="utf-8"))
                validate_cleanup_receipt(existing_receipt, original_receipt, retired, cleanup_context, bootstrap, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT)
                if journal.get("state") == "RENAMED":
                    journal["state"] = "SUCCESS_COMMITTED"
                    journal["completed_utc"] = utc_now()
                    cleanup_atomic_json(journal_path, journal, security_enabled)
                    commit_cleanup_security_migration(gate, security_enabled)
                    restore_cleanup_parent_security(gate, security_enabled)
                    print(json.dumps({"status": "test_artifact_already_retired", "sha256": expected_sha}, sort_keys=True))
                    return 0
            journal["retired_receipt"] = retired
            journal["state"] = "RENAMED"
            cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
            cleanup_atomic_json(journal_path, journal, security_enabled)
            cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
            cleanup_atomic_json(SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT, {
                "schema_version": "m9-source-control-test-artifact-retirement-v1", "status": "PASS",
                "original": original_receipt, "retired": retired, "context": cleanup_context,
                "reason": "test_isolation_failure_artifact", "utc": utc_now(), "python_bootstrap": bootstrap,
            }, security_enabled)
            journal["state"] = "SUCCESS_COMMITTED"
            journal["completed_utc"] = utc_now()
            cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
            cleanup_atomic_json(journal_path, journal, security_enabled)
            commit_cleanup_security_migration(gate, security_enabled)
            restore_cleanup_parent_security(gate, security_enabled)
            print(json.dumps({"status": "test_artifact_recovered", "sha256": expected_sha}, sort_keys=True))
            return 0
        if SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT.exists():
            raise SystemExit("cleanup receipt exists without cleanup journal")
        if SOURCE_CONTROL_RECOVERY_GATE.exists() or SOURCE_CONTROL_RECOVERY_PARENT.exists():
            raise SystemExit("test-artifact retirement requires absent source-control gate and parent")
        artifact = SOURCE_CONTROL_TEST_ARTIFACT
        if artifact.exists() and SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.exists():
            raise SystemExit("both active and retired test-artifact exist")
        if not artifact.is_file() and not SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file():
            raise SystemExit("test-artifact is absent")
        if SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.is_file() and not artifact.exists():
            raise SystemExit("retired artifact without PREPARED cleanup journal")
        receipt = cleanup_stat_receipt(artifact)
        if receipt.get("sha256") != expected_sha or any(receipt.get(k) != v for k, v in expected.items()):
            raise SystemExit("test-artifact receipt mismatch")
        journal = {
            "schema_version": "m9-source-control-test-artifact-cleanup-v1",
            "state": "PREPARED", "original_path": artifact.as_posix(),
            "retired_path": SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.as_posix(),
            "original_receipt": receipt, "context": cleanup_context,
            "python_bootstrap": bootstrap,
            "prepared_utc": utc_now(),
        }
        cleanup_atomic_json(journal_path, journal, security_enabled)
        cleanup_assert_single_link(artifact)
        os.replace(artifact, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
        retired = cleanup_stat_receipt(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
        if retired.get("sha256") != expected_sha or any(retired.get(k) != v for k, v in expected.items()):
            raise SystemExit("retired test-artifact receipt mismatch")
        journal["state"] = "RENAMED"; journal["retired_receipt"] = retired
        cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
        cleanup_atomic_json(journal_path, journal, security_enabled)
        cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
        cleanup_atomic_json(SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT, {
            "schema_version": "m9-source-control-test-artifact-retirement-v1", "status": "PASS",
            "original": receipt, "retired": retired, "context": cleanup_context,
            "reason": "test_isolation_failure_artifact", "utc": utc_now(), "python_bootstrap": bootstrap,
        }, security_enabled)
        journal["state"] = "SUCCESS_COMMITTED"; journal["completed_utc"] = utc_now()
        cleanup_assert_single_link(SOURCE_CONTROL_TEST_ARTIFACT_RETIRED)
        cleanup_atomic_json(journal_path, journal, security_enabled)
        commit_cleanup_security_migration(gate, security_enabled)
        restore_cleanup_parent_security(gate, security_enabled)
        print(json.dumps({"status": "test_artifact_retired", "sha256": expected_sha}, sort_keys=True))
        return 0


def command_dispose_invalid_source_control_gate(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("source-control gate disposition requires root")
    bootstrap = isolated_bootstrap_provenance()
    disposition, replacement_verdict = verify_source_control_gate_disposition()
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        runtime = source_control_disposition_runtime_receipt()
        if runtime != disposition.get("runtime_sha256"):
            raise SystemExit("source-control gate disposition runtime drift")
        replacement_gate = replacement_source_control_gate(
            json.loads(
                (
                    SOURCE_CONTROL_RECOVERY_GATE
                    if SOURCE_CONTROL_RECOVERY_GATE.exists()
                    else SOURCE_CONTROL_GATE_INVALID_RETIRED
                ).read_text(encoding="utf-8")
            ),
            replacement_verdict,
        )
        replacement_bytes = (
            json.dumps(replacement_gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        context = {
            "disposition_verdict_sha256": hashlib.sha256(
                SOURCE_CONTROL_GATE_DISPOSITION_VERDICT.read_bytes()
            ).hexdigest(),
            "replacement_verdict_sha256": hashlib.sha256(
                SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT.read_bytes()
            ).hexdigest(),
            "frozen_hashes_sha256": hashlib.sha256(
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_bytes()
            ).hexdigest(),
            "authorization_record_sha256": hashlib.sha256(
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION.read_bytes()
            ).hexdigest(),
            "runtime_sha256": runtime,
            "old_gate_sha256": INVALID_SOURCE_CONTROL_GATE_SHA256,
            "old_gate_bytes": INVALID_SOURCE_CONTROL_GATE_BYTES,
            "replacement_gate_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
            "replacement_gate_bytes": len(replacement_bytes),
        }
        journal_present = (
            SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL.exists()
            or SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL.is_symlink()
        )
        if journal_present:
            _, journal = strict_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL)
            if (
                journal.get("schema_version")
                != "m9-source-control-gate-disposition-v1"
                or journal.get("context") != context
                or journal.get("python_bootstrap") != bootstrap
            ):
                raise SystemExit("source-control gate disposition journal drift")
            if journal.get("state") not in {
                "PREPARED",
                "INVALID_GATE_RETIRED",
                "REPLACEMENT_CREATED",
                "SUCCESS_COMMITTED",
            }:
                raise SystemExit("source-control gate disposition journal state mismatch")
            old_journal = journal.get("old_gate")
            if (
                not isinstance(old_journal, dict)
                or old_journal.get("path") != SOURCE_CONTROL_RECOVERY_GATE.as_posix()
                or old_journal.get("sha256") != INVALID_SOURCE_CONTROL_GATE_SHA256
                or old_journal.get("bytes") != INVALID_SOURCE_CONTROL_GATE_BYTES
                or any(old_journal.get(key) != value for key, value in {
                    "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1,
                }.items())
            ):
                raise SystemExit("source-control gate disposition old receipt drift")
        else:
            if (
                SOURCE_CONTROL_GATE_INVALID_RETIRED.exists()
                or SOURCE_CONTROL_GATE_INVALID_RETIRED.is_symlink()
            ):
                raise SystemExit("retired invalid gate exists without disposition journal")
            old = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
            if (
                old["sha256"] != INVALID_SOURCE_CONTROL_GATE_SHA256
                or old["bytes"] != INVALID_SOURCE_CONTROL_GATE_BYTES
            ):
                raise SystemExit("invalid source-control gate receipt mismatch")
            journal = {
                "schema_version": "m9-source-control-gate-disposition-v1",
                "state": "PREPARED",
                "context": context,
                "python_bootstrap": bootstrap,
                "old_gate": old,
                "prepared_utc": utc_now(),
            }
            atomic_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL, journal)

        state = str(journal.get("state"))
        if state == "SUCCESS_COMMITTED":
            retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_INVALID_RETIRED)
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
            if (
                retired != journal.get("retired_gate")
                or replacement != journal.get("replacement_gate")
            ):
                raise SystemExit("source-control gate disposition terminal receipt drift")
            verified_replacement = verify_source_control_recovery_gate_and_hashes()
            if verified_replacement != replacement_gate:
                raise SystemExit("terminal replacement gate verifier payload mismatch")
            return 0
        active_exists = (
            SOURCE_CONTROL_RECOVERY_GATE.exists()
            or SOURCE_CONTROL_RECOVERY_GATE.is_symlink()
        )
        retired_exists = (
            SOURCE_CONTROL_GATE_INVALID_RETIRED.exists()
            or SOURCE_CONTROL_GATE_INVALID_RETIRED.is_symlink()
        )
        if active_exists:
            active = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
        else:
            active = None
        if retired_exists:
            retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_INVALID_RETIRED)
            if (
                retired["sha256"] != INVALID_SOURCE_CONTROL_GATE_SHA256
                or retired["bytes"] != INVALID_SOURCE_CONTROL_GATE_BYTES
            ):
                raise SystemExit("retired invalid source-control gate drift")
        else:
            retired = None
        if retired is None:
            if active != journal.get("old_gate"):
                raise SystemExit("active invalid source-control gate drift")
            os.replace(SOURCE_CONTROL_RECOVERY_GATE, SOURCE_CONTROL_GATE_INVALID_RETIRED)
            retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_INVALID_RETIRED)
            expected_retired = dict(journal["old_gate"], path=SOURCE_CONTROL_GATE_INVALID_RETIRED.as_posix())
            if retired != expected_retired:
                raise SystemExit("invalid source-control gate retirement mismatch")
        journal["retired_gate"] = retired
        journal["state"] = "INVALID_GATE_RETIRED"
        atomic_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL, journal)

        if SOURCE_CONTROL_RECOVERY_GATE.exists():
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
            if (
                replacement["sha256"] != context["replacement_gate_sha256"]
                or replacement["bytes"] != context["replacement_gate_bytes"]
            ):
                raise SystemExit("replacement source-control gate drift")
        else:
            atomic_root_private_bytes(SOURCE_CONTROL_RECOVERY_GATE, replacement_bytes)
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
        verified_replacement = verify_source_control_recovery_gate_and_hashes()
        if verified_replacement != replacement_gate:
            raise SystemExit("replacement source-control gate verifier payload mismatch")
        journal["replacement_gate"] = replacement
        journal["state"] = "REPLACEMENT_CREATED"
        atomic_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL, journal)
        journal["state"] = "SUCCESS_COMMITTED"
        journal["completed_utc"] = utc_now()
        atomic_root_private_json(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL, journal)
        print(
            json.dumps(
                {
                    "status": "source_control_gate_replaced",
                    "replacement_sha256": replacement["sha256"],
                },
                sort_keys=True,
            )
        )
        return 0


def command_refresh_source_control_recovery_gate(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("source-control gate lock refresh requires root")
    bootstrap = isolated_bootstrap_provenance()
    refresh_verdict, replacement_verdict, verified_bindings = verify_source_control_gate_lock_refresh()
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        runtime = source_control_lock_refresh_runtime_receipt()
        if runtime != refresh_verdict.get("runtime_sha256"):
            raise SystemExit("source-control gate lock-refresh runtime drift")
        old_path = (
            SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED
            if SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.exists()
            else SOURCE_CONTROL_RECOVERY_GATE
        )
        old_receipt, old_gate = strict_root_private_json(old_path)
        if (
            old_receipt.get("sha256") != PRE_LOCK_REFRESH_GATE_SHA256
            or old_receipt.get("bytes") != PRE_LOCK_REFRESH_GATE_BYTES
        ):
            raise SystemExit("pre-lock-refresh source-control gate receipt mismatch")
        replacement_gate = lock_refresh_source_control_gate(
            old_gate,
            replacement_verdict,
            verified_bindings["replacement_verdict_sha256"],
            verified_bindings["frozen_hashes_sha256"],
        )
        replacement_bytes = (
            json.dumps(replacement_gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        context = {
            "refresh_verdict_sha256": verified_bindings["refresh_verdict_sha256"],
            "replacement_verdict_sha256": verified_bindings["replacement_verdict_sha256"],
            "frozen_hashes_sha256": verified_bindings["frozen_hashes_sha256"],
            "authorization_record_sha256": verified_bindings["authorization_record_sha256"],
            "runtime_sha256": runtime,
            "old_gate_sha256": PRE_LOCK_REFRESH_GATE_SHA256,
            "old_gate_bytes": PRE_LOCK_REFRESH_GATE_BYTES,
            "replacement_gate_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
            "replacement_gate_bytes": len(replacement_bytes),
        }
        journal_present = (
            SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL.exists()
            or SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL.is_symlink()
        )
        if journal_present:
            _, journal = strict_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL)
            if (
                journal.get("schema_version") != "m9-source-control-gate-lock-refresh-v1"
                or journal.get("context") != context
                or journal.get("python_bootstrap") != bootstrap
            ):
                raise SystemExit("source-control gate lock-refresh journal drift")
            if journal.get("state") not in {
                "PREPARED", "OLD_GATE_RETIRED", "REPLACEMENT_CREATED", "SUCCESS_COMMITTED"
            }:
                raise SystemExit("source-control gate lock-refresh journal state mismatch")
            old_journal = journal.get("old_gate")
            if (
                not isinstance(old_journal, dict)
                or old_journal.get("path") != SOURCE_CONTROL_RECOVERY_GATE.as_posix()
                or old_journal.get("sha256") != PRE_LOCK_REFRESH_GATE_SHA256
                or old_journal.get("bytes") != PRE_LOCK_REFRESH_GATE_BYTES
                or any(old_journal.get(key) != value for key, value in {
                    "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1,
                }.items())
            ):
                raise SystemExit("source-control gate lock-refresh old receipt drift")
        else:
            if (
                SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.exists()
                or SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.is_symlink()
            ):
                raise SystemExit("pre-lock retired gate exists without lock-refresh journal")
            if old_receipt.get("path") != SOURCE_CONTROL_RECOVERY_GATE.as_posix():
                raise SystemExit("pre-lock-refresh active gate path mismatch")
            journal = {
                "schema_version": "m9-source-control-gate-lock-refresh-v1",
                "state": "PREPARED",
                "context": context,
                "python_bootstrap": bootstrap,
                "old_gate": old_receipt,
                "prepared_utc": utc_now(),
            }
            atomic_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL, journal)

        state = str(journal.get("state"))
        if state == "SUCCESS_COMMITTED":
            retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED)
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
            if retired != journal.get("retired_gate") or replacement != journal.get("replacement_gate"):
                raise SystemExit("source-control gate lock-refresh terminal receipt drift")
            verified = verify_source_control_recovery_gate_and_hashes()
            if verified != replacement_gate:
                raise SystemExit("terminal lock-refresh replacement verifier payload mismatch")
            post_receipt, post_gate = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
            if post_receipt != replacement or post_gate != replacement_gate:
                raise SystemExit("terminal lock-refresh replacement path drift")
            return 0

        active_exists = SOURCE_CONTROL_RECOVERY_GATE.exists() or SOURCE_CONTROL_RECOVERY_GATE.is_symlink()
        retired_exists = (
            SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.exists()
            or SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.is_symlink()
        )
        active = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE) if active_exists else None
        retired = (
            strict_root_private_receipt(SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED)
            if retired_exists else None
        )
        if retired is not None and (
            retired.get("sha256") != PRE_LOCK_REFRESH_GATE_SHA256
            or retired.get("bytes") != PRE_LOCK_REFRESH_GATE_BYTES
        ):
            raise SystemExit("pre-lock retired source-control gate drift")
        if retired is None:
            if active != journal.get("old_gate"):
                raise SystemExit("active pre-lock source-control gate drift")
            os.replace(SOURCE_CONTROL_RECOVERY_GATE, SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED)
            retired = strict_root_private_receipt(SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED)
            expected_retired = dict(
                journal["old_gate"], path=SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED.as_posix()
            )
            if retired != expected_retired:
                raise SystemExit("pre-lock source-control gate retirement mismatch")
        journal["retired_gate"] = retired
        journal["state"] = "OLD_GATE_RETIRED"
        atomic_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL, journal)

        if SOURCE_CONTROL_RECOVERY_GATE.exists() or SOURCE_CONTROL_RECOVERY_GATE.is_symlink():
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
            if (
                replacement.get("sha256") != context["replacement_gate_sha256"]
                or replacement.get("bytes") != context["replacement_gate_bytes"]
            ):
                raise SystemExit("lock-refresh replacement source-control gate drift")
        else:
            atomic_root_private_bytes(SOURCE_CONTROL_RECOVERY_GATE, replacement_bytes)
            replacement = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
        verified = verify_source_control_recovery_gate_and_hashes()
        if verified != replacement_gate:
            raise SystemExit("lock-refresh replacement source-control gate verifier payload mismatch")
        post_receipt, post_gate = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
        if post_receipt != replacement or post_gate != replacement_gate:
            raise SystemExit("lock-refresh replacement source-control gate path drift")
        journal["replacement_gate"] = replacement
        journal["state"] = "REPLACEMENT_CREATED"
        atomic_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL, journal)
        final_receipt, final_gate = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
        if final_receipt != replacement or final_gate != replacement_gate:
            raise SystemExit("lock-refresh replacement changed before terminal commit")
        journal["state"] = "SUCCESS_COMMITTED"
        journal["completed_utc"] = utc_now()
        atomic_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL, journal)
        try:
            committed_receipt, committed_gate = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
            if committed_receipt != replacement or committed_gate != replacement_gate:
                raise SystemExit("lock-refresh replacement changed during terminal commit")
        except SystemExit:
            journal["state"] = "FAILED_COMMITTED"
            journal["failure_reason"] = "replacement_changed_during_terminal_commit"
            journal["failed_utc"] = utc_now()
            atomic_root_private_json(SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL, journal)
            raise
        print(json.dumps({
            "status": "source_control_gate_lock_refreshed",
            "replacement_sha256": replacement["sha256"],
        }, sort_keys=True))
        return 0


def verify_source_control_post_failure_migration() -> tuple[dict, dict, dict[str, object]]:
    verdict_receipt, verdict, _ = read_stable_regular_json(
        SOURCE_CONTROL_POST_FAILURE_MIGRATION_VERDICT
    )
    if (
        verdict.get("schema_version") != "m9-source-control-post-failure-migration-verdict-v1"
        or verdict.get("decision_id") != "D-017-source-control-post-failure-migration-v1"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("scope") != "MIGRATE_AND_RESUME_SAME_SOURCE_CONTROL_RECOVERY_TRANSACTION"
    ):
        raise SystemExit("post-failure migration verdict is not an exact zero-issue PASS")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    if (
        report.parent != AUDITS.resolve(strict=False)
        or not report.is_file()
        or hashlib.sha256(report.read_bytes()).hexdigest() != verdict.get("report_sha256")
    ):
        raise SystemExit("post-failure migration report binding mismatch")
    replacement_receipt, replacement, _ = read_stable_regular_json(
        SOURCE_CONTROL_POST_FAILURE_REPLACEMENT_VERDICT
    )
    if (
        replacement.get("schema_version") != "m9-source-control-recovery-audit-verdict-v1"
        or replacement.get("decision_id") != "D-017-source-control-recovery-v1"
        or replacement.get("verdict") != "PASS"
        or int(replacement.get("blocking", -1)) != 0
        or int(replacement.get("non_blocking", -1)) != 0
        or verdict.get("replacement_verdict_path") != SOURCE_CONTROL_POST_FAILURE_REPLACEMENT_VERDICT.as_posix()
        or verdict.get("replacement_verdict_sha256") != replacement_receipt["sha256"]
    ):
        raise SystemExit("post-failure replacement verdict binding mismatch")
    frozen_receipt, manifest, _ = read_stable_regular_json(
        SOURCE_CONTROL_RECOVERY_FROZEN_HASHES
    )
    files = manifest.get("files")
    if (
        verdict.get("frozen_hashes_sha256") != frozen_receipt["sha256"]
        or not isinstance(files, dict)
        or set(Path(str(path)).resolve(strict=False) for path in files)
        != {path.resolve(strict=False) for path in SOURCE_RECOVERY_CONTROL_FILES}
    ):
        raise SystemExit("post-failure frozen hash closure mismatch")
    for text_path, expected in files.items():
        member = Path(str(text_path))
        if (
            member.is_symlink()
            or not member.is_file()
            or hashlib.sha256(member.read_bytes()).hexdigest() != str(expected)
        ):
            raise SystemExit(f"post-failure frozen member mismatch: {member}")
    if (
        verdict.get("authorization_record_sha256")
        != hashlib.sha256(SOURCE_CONTROL_RECOVERY_AUTHORIZATION.read_bytes()).hexdigest()
    ):
        raise SystemExit("post-failure authorization binding mismatch")
    contract_receipt, contract, _ = read_stable_regular_json(
        SOURCE_CONTROL_POST_FAILURE_CONTRACT
    )
    if (
        contract.get("schema_version") != "m9-source-control-post-failure-contract-v1"
        or contract.get("decision_id") != "D-017-source-control-post-failure-migration-v1"
        or contract.get("scope") != "MIGRATE_AND_RESUME_SAME_SOURCE_CONTROL_RECOVERY_TRANSACTION"
        or verdict.get("contract_sha256") != contract_receipt["sha256"]
    ):
        raise SystemExit("post-failure contract binding mismatch")
    runtime = verdict.get("failed_runtime")
    required = {
        "recovery_transaction_sha256",
        "recovery_transaction_id",
        "recovery_event_id",
        "parent_snapshot_sha256",
        "parent_transaction_sha256",
        "state_sha256",
        "workflow_sha256",
        "ledger_sha256",
        "recovery_event_count",
        "retired_capability_path",
        "retired_capability_sha256",
        "active_gate_sha256",
    }
    if not isinstance(runtime, dict) or set(runtime) != required:
        raise SystemExit("post-failure runtime binding is incomplete")
    if runtime != contract.get("failed_runtime"):
        raise SystemExit("post-failure verdict and contract runtime differ")
    if any(
        not isinstance(runtime[key], str) or not re.fullmatch(r"[0-9a-f]{64}", runtime[key])
        for key in required - {"recovery_transaction_id", "recovery_event_id", "recovery_event_count", "retired_capability_path"}
    ):
        raise SystemExit("post-failure runtime SHA binding is invalid")
    if (
        runtime.get("recovery_transaction_id") != "4783a27441019358a0f15127f26d957d"
        or runtime.get("recovery_event_id")
        != "4783a27441019358a0f15127f26d957d:source-control-recovery"
        or int(runtime.get("recovery_event_count", -1)) != 0
        or runtime.get("retired_capability_path")
        != "/home/evan-williams/deeph-m9/manifests/overlap_capabilities/f7c3b060e19e37e6da03f461d754d38c.retired.json"
    ):
        raise SystemExit("post-failure transaction identity binding mismatch")
    bindings = {
        "verdict": verdict_receipt,
        "replacement_verdict": replacement_receipt,
        "frozen": frozen_receipt,
        "contract": contract_receipt,
        "authorization_sha256": verdict.get("authorization_record_sha256"),
        "runtime": runtime,
    }
    return verdict, replacement, bindings


def build_post_failure_replacement_gate(
    old_gate: dict,
    replacement_verdict_receipt: dict[str, object],
    frozen_receipt: dict[str, object],
    authorization_sha256: str,
    runtime: dict,
    contract_sha256: str | None = None,
) -> dict:
    gate = dict(old_gate)
    gate["audit_report_path"] = SOURCE_CONTROL_POST_FAILURE_REPLACEMENT_VERDICT.as_posix()
    gate["audit_report_sha256"] = replacement_verdict_receipt["sha256"]
    gate["authorization_record_path"] = SOURCE_CONTROL_RECOVERY_AUTHORIZATION.as_posix()
    gate["authorization_record_sha256"] = authorization_sha256
    gate["frozen_hashes_path"] = SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.as_posix()
    gate["frozen_hashes_sha256"] = frozen_receipt["sha256"]
    gate["post_failure_resume"] = {
        "decision_id": "D-017-source-control-post-failure-migration-v1",
        "recovery_transaction_id": runtime["recovery_transaction_id"],
        "recovery_event_id": runtime["recovery_event_id"],
        "failed_recovery_transaction_sha256": runtime["recovery_transaction_sha256"],
        "failed_workflow_sha256": runtime["workflow_sha256"],
        "ledger_sha256": runtime["ledger_sha256"],
        "recovery_event_count": runtime["recovery_event_count"],
        "contract_sha256": contract_sha256,
    }
    return gate


def post_failure_runtime_receipts(runtime: dict) -> tuple[dict[str, object], bytes]:
    paths = {
        "recovery_transaction_sha256": SOURCE_CONTROL_RECOVERY_TRANSACTION,
        "parent_snapshot_sha256": SOURCE_CONTROL_RECOVERY_PARENT,
        "parent_transaction_sha256": OVERLAP_TRANSACTION,
        "state_sha256": STATE_PATH,
        "workflow_sha256": OVERLAP_WORKFLOW_STATE,
        "ledger_sha256": LEDGER_PATH,
        "retired_capability_sha256": Path(str(runtime["retired_capability_path"])),
        "active_gate_sha256": SOURCE_CONTROL_RECOVERY_GATE,
    }
    observed: dict[str, object] = {}
    recovery_bytes: bytes | None = None
    for key, path in paths.items():
        receipt, payload = read_stable_regular_bytes(path)
        observed[key] = receipt["sha256"]
        if observed[key] != runtime[key]:
            raise SystemExit(f"post-failure runtime SHA mismatch: {key}")
        if key == "recovery_transaction_sha256":
            recovery_bytes = payload
    event_ids = ledger_event_ids()
    if int(runtime["recovery_event_id"] in event_ids) != int(runtime["recovery_event_count"]):
        raise SystemExit("post-failure ledger event closure mismatch")
    if recovery_bytes is None:
        raise SystemExit("post-failure recovery transaction bytes were not captured")
    recovery = json.loads(recovery_bytes.decode("utf-8"))
    if (
        recovery.get("state") != "FAILED_COMMITTED"
        or recovery.get("transaction_id") != runtime["recovery_transaction_id"]
        or recovery.get("event", {}).get("event_id") != runtime["recovery_event_id"]
        or recovery.get("ledger_phase") != "PENDING"
    ):
        raise SystemExit("post-failure recovery transaction state mismatch")
    return observed, recovery_bytes


def verify_post_failure_immutable_runtime(runtime: dict, journal: dict | None = None) -> None:
    immutable = {
        "parent_snapshot_sha256": SOURCE_CONTROL_RECOVERY_PARENT,
        "parent_transaction_sha256": OVERLAP_TRANSACTION,
        "state_sha256": STATE_PATH,
        "workflow_sha256": OVERLAP_WORKFLOW_STATE,
        "ledger_sha256": LEDGER_PATH,
        "retired_capability_sha256": Path(str(runtime["retired_capability_path"])),
    }
    for key, path in immutable.items():
        receipt, _ = read_stable_regular_bytes(path)
        if receipt["sha256"] != runtime[key]:
            raise SystemExit(f"post-failure immutable runtime drift: {key}")
    ledger_ids = ledger_event_ids()
    if int(runtime["recovery_event_id"] in ledger_ids) != int(runtime["recovery_event_count"]):
        raise SystemExit("post-failure recovery event count drift")
    if journal is None:
        return
    recovery_receipt, recovery_bytes = read_stable_regular_bytes(
        SOURCE_CONTROL_RECOVERY_TRANSACTION
    )
    journal_state = str(journal.get("state"))
    original_sha = runtime["recovery_transaction_sha256"]
    if journal_state in {"PREPARED", "GATE_RETIRED"}:
        if recovery_receipt["sha256"] != original_sha:
            raise SystemExit("post-failure original recovery transaction drift")
        return
    if journal_state == "REPLACEMENT_CREATED":
        if recovery_receipt["sha256"] == original_sha:
            return
        recovery = json.loads(recovery_bytes.decode("utf-8"))
        migration = recovery.get("post_failure_migration")
        active_gate = json.loads(SOURCE_CONTROL_RECOVERY_GATE.read_text(encoding="utf-8"))
        if (
            not isinstance(migration, dict)
            or migration.get("schema_version") != "m9-source-control-post-failure-migration-v1"
            or migration.get("status") != "PASS"
            or migration.get("original_failed_recovery_sha256") != original_sha
            or migration.get("original_failed_recovery_snapshot")
            != journal.get("context", {}).get("original_failed_recovery_snapshot")
            or migration.get("authorized_failed_state_sha256") != runtime["state_sha256"]
            or migration.get("authorized_failed_workflow_sha256") != runtime["workflow_sha256"]
            or migration.get("authorized_ledger_sha256") != runtime["ledger_sha256"]
            or migration.get("migration_context_sha256") != journal.get("context_sha256")
            or migration.get("migrated_utc") != journal.get("migration_utc")
            or recovery.get("transaction_id") != runtime["recovery_transaction_id"]
            or recovery.get("event", {}).get("event_id") != runtime["recovery_event_id"]
            or recovery.get("gate_receipt") != source_control_gate_receipt(active_gate)
        ):
            raise SystemExit("post-failure migrated recovery transaction drift")
        return
    if journal_state in {"RECOVERY_RECEIPT_MIGRATED", "SUCCESS_COMMITTED"}:
        if recovery_receipt["sha256"] != journal.get("migrated_recovery_sha256"):
            raise SystemExit("post-failure committed recovery transaction drift")
        return
    raise SystemExit("post-failure journal state is not auditable")


def validate_migrated_failed_recovery(
    recovery: dict,
    bootstrap: dict[str, object],
    gate_receipt: dict[str, object],
) -> dict:
    migration = recovery.get("post_failure_migration")
    if (
        not isinstance(migration, dict)
        or migration.get("schema_version") != "m9-source-control-post-failure-migration-v1"
        or migration.get("status") != "PASS"
        or recovery.get("transaction_id") != migration.get("recovery_transaction_id")
        or recovery.get("event", {}).get("event_id") != migration.get("recovery_event_id")
        or recovery.get("gate_receipt") != gate_receipt
        or recovery.get("python_bootstrap") != bootstrap
    ):
        raise ValueError("source_control_post_failure_migration_missing")
    snapshot_receipt, snapshot = strict_root_private_json(
        SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT
    )
    _, journal = strict_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL)
    if (
        journal.get("schema_version") != "m9-source-control-post-failure-migration-v1"
        or journal.get("state") != "SUCCESS_COMMITTED"
        or journal.get("python_bootstrap") != bootstrap
        or migration.get("original_failed_recovery_snapshot") != snapshot_receipt
        or migration.get("migration_journal_path") != SOURCE_CONTROL_POST_FAILURE_JOURNAL.as_posix()
        or migration.get("migration_context_sha256") != journal.get("context_sha256")
        or (
            recovery.get("state") == "FAILED_COMMITTED"
            and journal.get("migrated_recovery_sha256")
            != hashlib.sha256(SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()).hexdigest()
        )
        or snapshot.get("transaction_id") != recovery.get("transaction_id")
        or snapshot.get("state") != "FAILED_COMMITTED"
        or snapshot.get("event", {}).get("event_id")
        != recovery.get("event", {}).get("event_id")
        or migration.get("new_gate_receipt") != gate_receipt
    ):
        raise ValueError("source_control_post_failure_migration_receipt_drift")
    expected_workflow = migration.get("authorized_failed_workflow_sha256")
    if not isinstance(expected_workflow, str):
        raise ValueError("source_control_post_failure_workflow_binding_missing")
    return migration


def command_migrate_source_control_post_failure(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("post-failure source-control migration requires root")
    bootstrap = isolated_bootstrap_provenance()
    verdict, replacement_verdict, bindings = verify_source_control_post_failure_migration()
    runtime = bindings["runtime"]
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        journal: dict
        if SOURCE_CONTROL_POST_FAILURE_JOURNAL.exists():
            _, journal = strict_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL)
            if (
                journal.get("schema_version") != "m9-source-control-post-failure-migration-v1"
                or journal.get("python_bootstrap") != bootstrap
                or journal.get("verdict_receipt") != bindings["verdict"]
                or journal.get("replacement_verdict_receipt")
                != bindings["replacement_verdict"]
                or journal.get("frozen_receipt") != bindings["frozen"]
                or journal.get("contract_receipt") != bindings["contract"]
                or journal.get("runtime") != runtime
            ):
                raise SystemExit("post-failure migration journal binding mismatch")
        else:
            observed, original_bytes = post_failure_runtime_receipts(runtime)
            old_gate_receipt, old_gate = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
            if old_gate_receipt["sha256"] != runtime["active_gate_sha256"]:
                raise SystemExit("post-failure active gate binding mismatch")
            if SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED.exists():
                raise SystemExit("post-failure retired gate exists without journal")
            original = json.loads(original_bytes.decode("utf-8"))
            if SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT.exists():
                snapshot_receipt, snapshot = strict_root_private_json(
                    SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT
                )
                if snapshot != original:
                    raise SystemExit("failed recovery snapshot differs from runtime transaction")
            else:
                atomic_root_private_bytes(
                    SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT, original_bytes
                )
                snapshot_receipt, snapshot = strict_root_private_json(
                    SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT
                )
            replacement_gate = build_post_failure_replacement_gate(
                old_gate,
                bindings["replacement_verdict"],
                bindings["frozen"],
                str(bindings["authorization_sha256"]),
                runtime,
                str(bindings["contract"]["sha256"]),
            )
            replacement_bytes = (
                json.dumps(replacement_gate, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            context = {
                "decision_id": "D-017-source-control-post-failure-migration-v1",
                "old_gate": old_gate_receipt,
                "original_failed_recovery_snapshot": snapshot_receipt,
                "replacement_gate_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
                "replacement_gate_bytes": len(replacement_bytes),
                "observed_runtime": observed,
            }
            journal = {
                "schema_version": "m9-source-control-post-failure-migration-v1",
                "state": "PREPARED",
                "python_bootstrap": bootstrap,
                "verdict_receipt": bindings["verdict"],
                "replacement_verdict_receipt": bindings["replacement_verdict"],
                "frozen_receipt": bindings["frozen"],
                "contract_receipt": bindings["contract"],
                "runtime": runtime,
                "context": context,
                "context_sha256": canonical_hash(context),
                "prepared_utc": utc_now(),
            }
            atomic_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL, journal)

        verify_post_failure_immutable_runtime(runtime, journal)
        old_gate_receipt = journal["context"]["old_gate"]
        snapshot_receipt, snapshot = strict_root_private_json(
            SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT
        )
        if snapshot_receipt != journal["context"]["original_failed_recovery_snapshot"]:
            raise SystemExit("post-failure original recovery snapshot drift")
        if hashlib.sha256((json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n").encode("utf-8")).hexdigest() != snapshot_receipt["sha256"]:
            raise SystemExit("post-failure original recovery snapshot serialization drift")
        state = str(journal.get("state"))
        if state == "FAILED_COMMITTED":
            raise SystemExit("post-failure migration is terminally failed")
        if state == "SUCCESS_COMMITTED":
            active_receipt, _ = strict_root_private_json(SOURCE_CONTROL_RECOVERY_GATE)
            retired_receipt = strict_root_private_receipt(
                SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED
            )
            if (
                active_receipt != journal.get("replacement_gate")
                or retired_receipt != journal.get("retired_gate")
                or hashlib.sha256(SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()).hexdigest()
                != journal.get("migrated_recovery_sha256")
            ):
                raise SystemExit("post-failure migration terminal receipt drift")
            return 0

        active_exists = SOURCE_CONTROL_RECOVERY_GATE.exists()
        retired_exists = SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED.exists()
        if state == "PREPARED":
            if active_exists and not retired_exists:
                active = strict_root_private_receipt(SOURCE_CONTROL_RECOVERY_GATE)
                if active != old_gate_receipt:
                    raise SystemExit("post-failure active gate drift before retirement")
                os.replace(
                    SOURCE_CONTROL_RECOVERY_GATE,
                    SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED,
                )
            elif active_exists or not retired_exists:
                raise SystemExit("post-failure gate retirement path state mismatch")
            retired = strict_root_private_receipt(
                SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED
            )
            expected_retired = dict(
                old_gate_receipt, path=SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED.as_posix()
            )
            if retired != expected_retired:
                raise SystemExit("post-failure retired gate receipt mismatch")
            journal["retired_gate"] = retired
            journal["state"] = "GATE_RETIRED"
            atomic_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL, journal)
            state = "GATE_RETIRED"

        _, old_gate = strict_root_private_json(SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED)
        replacement_gate = build_post_failure_replacement_gate(
            old_gate,
            bindings["replacement_verdict"],
            bindings["frozen"],
            str(bindings["authorization_sha256"]),
            runtime,
            str(bindings["contract"]["sha256"]),
        )
        replacement_bytes = (
            json.dumps(replacement_gate, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        if (
            hashlib.sha256(replacement_bytes).hexdigest()
            != journal["context"]["replacement_gate_sha256"]
            or len(replacement_bytes) != journal["context"]["replacement_gate_bytes"]
        ):
            raise SystemExit("post-failure replacement gate construction drift")
        if state == "GATE_RETIRED":
            if SOURCE_CONTROL_RECOVERY_GATE.exists():
                replacement_receipt, current_gate = strict_root_private_json(
                    SOURCE_CONTROL_RECOVERY_GATE
                )
                if current_gate != replacement_gate:
                    raise SystemExit("post-failure replacement gate pre-exists with other bytes")
            else:
                atomic_root_private_bytes(SOURCE_CONTROL_RECOVERY_GATE, replacement_bytes)
                replacement_receipt, current_gate = strict_root_private_json(
                    SOURCE_CONTROL_RECOVERY_GATE
                )
            if current_gate != replacement_gate:
                raise SystemExit("post-failure replacement gate payload mismatch")
            verified = verify_source_control_recovery_gate_and_hashes()
            if verified != replacement_gate:
                raise SystemExit("post-failure replacement gate verifier mismatch")
            journal["replacement_gate"] = replacement_receipt
            journal["state"] = "REPLACEMENT_CREATED"
            journal["migration_utc"] = utc_now()
            atomic_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL, journal)
            state = "REPLACEMENT_CREATED"

        if state == "REPLACEMENT_CREATED":
            active_receipt, active_gate = strict_root_private_json(
                SOURCE_CONTROL_RECOVERY_GATE
            )
            if active_receipt != journal.get("replacement_gate") or active_gate != replacement_gate:
                raise SystemExit("post-failure replacement gate changed before receipt migration")
            current_bytes = SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()
            current_sha = hashlib.sha256(current_bytes).hexdigest()
            recovery = json.loads(current_bytes.decode("utf-8"))
            if current_sha == runtime["recovery_transaction_sha256"]:
                old_gate_binding = recovery.get("gate_receipt")
                new_gate_binding = source_control_gate_receipt(active_gate)
                migration = {
                    "schema_version": "m9-source-control-post-failure-migration-v1",
                    "status": "PASS",
                    "decision_id": "D-017-source-control-post-failure-migration-v1",
                    "recovery_transaction_id": runtime["recovery_transaction_id"],
                    "recovery_event_id": runtime["recovery_event_id"],
                    "original_failed_recovery_sha256": runtime["recovery_transaction_sha256"],
                    "original_failed_recovery_snapshot": snapshot_receipt,
                    "old_gate_receipt": old_gate_binding,
                    "new_gate_receipt": new_gate_binding,
                    "authorized_failed_state_sha256": runtime["state_sha256"],
                    "authorized_failed_workflow_sha256": runtime["workflow_sha256"],
                    "authorized_ledger_sha256": runtime["ledger_sha256"],
                    "migration_journal_path": SOURCE_CONTROL_POST_FAILURE_JOURNAL.as_posix(),
                    "migration_context_sha256": journal["context_sha256"],
                    "verdict_sha256": bindings["verdict"]["sha256"],
                    "migrated_utc": journal["migration_utc"],
                }
                recovery.setdefault("failure_history", []).append(
                    {
                        "state": "FAILED_COMMITTED",
                        "transaction_sha256": current_sha,
                        "failure_reasons": recovery.get("failure_reasons", []),
                    }
                )
                recovery["post_failure_migration"] = migration
                recovery["gate_receipt"] = new_gate_binding
                atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
                current_bytes = SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()
                current_sha = hashlib.sha256(current_bytes).hexdigest()
            else:
                migration = recovery.get("post_failure_migration", {})
                if (
                    migration.get("original_failed_recovery_sha256")
                    != runtime["recovery_transaction_sha256"]
                    or recovery.get("gate_receipt") != source_control_gate_receipt(active_gate)
                ):
                    raise SystemExit("post-failure migrated recovery transaction drift")
            journal["migrated_recovery_sha256"] = current_sha
            journal["state"] = "RECOVERY_RECEIPT_MIGRATED"
            atomic_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL, journal)
            state = "RECOVERY_RECEIPT_MIGRATED"

        if state == "RECOVERY_RECEIPT_MIGRATED":
            if (
                hashlib.sha256(SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()).hexdigest()
                != journal.get("migrated_recovery_sha256")
            ):
                raise SystemExit("post-failure migrated recovery transaction changed")
            journal["state"] = "SUCCESS_COMMITTED"
            journal["completed_utc"] = utc_now()
            atomic_root_private_json(SOURCE_CONTROL_POST_FAILURE_JOURNAL, journal)
            return 0
        raise SystemExit("post-failure migration journal state is unsupported")


def source_control_resume(
    recovery: dict,
    bootstrap: dict[str, object],
    gate_receipt: dict[str, object],
) -> int:
    try:
        migrated_failure = None
        if recovery.get("schema_version") != "m9-source-control-recovery-v1":
            raise ValueError("source_control_recovery_schema_mismatch")
        if recovery.get("python_bootstrap") != bootstrap:
            raise ValueError("source_control_python_bootstrap_drift")
        if recovery.get("gate_receipt") != gate_receipt:
            raise ValueError("source_control_gate_receipt_drift")
        if recovery.get("post_failure_migration") is not None:
            migrated_failure = validate_migrated_failed_recovery(
                recovery, bootstrap, gate_receipt
            )
        parent_tx = OVERLAP_TRANSACTION.read_bytes()
        if hashlib.sha256(parent_tx).hexdigest() != recovery.get("parent_transaction_sha256"):
            raise ValueError("source_control_parent_transaction_drift")
        parent_obj = json.loads(parent_tx.decode("utf-8"))
        if recovery.get("parent_transaction_id") != parent_obj.get("transaction_id"):
            raise ValueError("source_control_parent_transaction_id_drift")
        parent_snapshot = SOURCE_CONTROL_RECOVERY_PARENT
        if (not parent_snapshot.is_file() or parent_snapshot.read_bytes() != parent_tx
                or hashlib.sha256(parent_snapshot.read_bytes()).hexdigest() != recovery.get("parent_snapshot_sha256")
                or recovery.get("parent_snapshot_bytes") != len(parent_tx)):
            raise ValueError("source_control_parent_snapshot_mismatch")
        event = recovery.get("event")
        if not isinstance(event, dict) or not event.get("event_id"):
            raise ValueError("source_control_recovery_event_missing")
        parent_ledger = recovery.get("parent_ledger_event_hashes", {})
        if not isinstance(parent_ledger, dict):
            raise ValueError("source_control_parent_ledger_missing")
        _, ledger_bytes = read_stable_regular_bytes(LEDGER_PATH)
        parent_ledger_bytes = int(recovery.get("parent_ledger_bytes", -1))
        parent_ledger_sha256 = recovery.get("parent_ledger_sha256")
        if (
            parent_ledger_bytes < 0
            or len(ledger_bytes) < parent_ledger_bytes
            or hashlib.sha256(ledger_bytes[:parent_ledger_bytes]).hexdigest()
            != parent_ledger_sha256
        ):
            raise ValueError("source_control_parent_ledger_bytes_drift")
        event_hash = canonical_hash({k: v for k, v in event.items() if k != "event_id"})
        allowed_ledger = dict(parent_ledger)
        allowed_ledger[str(event["event_id"])] = event_hash
        expected_suffix = (
            json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n"
        ).encode("utf-8")
        suffix = ledger_bytes[parent_ledger_bytes:]
        parsed_parent = ledger_event_ids_from_bytes(ledger_bytes[:parent_ledger_bytes])
        if parsed_parent != parent_ledger:
            raise ValueError("source_control_parent_ledger_event_map_drift")
        if suffix == b"":
            current_ledger = parent_ledger
        elif suffix == expected_suffix:
            current_ledger = allowed_ledger
        elif resume_partial_existing_append(
            LEDGER_PATH,
            prefix_bytes=parent_ledger_bytes,
            prefix_sha256=str(parent_ledger_sha256),
            expected_suffix=expected_suffix,
        ):
            _, repaired = read_stable_regular_bytes(LEDGER_PATH)
            if repaired != ledger_bytes[:parent_ledger_bytes]:
                raise ValueError("source_control_partial_ledger_repair_drift")
            ledger_bytes = repaired
            suffix = b""
            current_ledger = parent_ledger
        else:
            raise ValueError("source_control_ledger_order_or_bytes_drift")
        retired = Path(str(recovery["retired_capability_path"]))
        cap = Path(str(recovery["stale_capability_path"]))
        if not retired.exists() and cap.exists():
            os.replace(cap, retired)
        if not retired.exists():
            raise ValueError("source_control_retired_capability_missing")
        receipt = file_stat_receipt(retired)
        expected = recovery.get("retired_capability", recovery.get("stale_capability_before", {}))
        if any(receipt.get(k) != expected.get(k) for k in ("sha256", "bytes", "uid", "gid", "mode")):
            raise ValueError("source_control_retired_capability_receipt_mismatch")
        recovery["retired_capability"] = receipt
        if recovery.get("state") == "SUCCESS_COMMITTED":
            state_hash = hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
            workflow_hash = hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest()
            ledger_hash = hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest()
            if (state_hash != recovery.get("post_state_sha256")
                    or workflow_hash != recovery.get("post_workflow_sha256")
                    or ledger_hash != recovery.get("post_ledger_sha256")
                    or current_ledger != allowed_ledger):
                raise ValueError("source_control_terminal_receipt_mismatch")
            return 0
        recovery["state"] = "SUCCESS_PENDING_COMMIT"
        recovery["ledger_phase"] = "PENDING"
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        append_event_once(
            event,
            expected_prefix_bytes=parent_ledger_bytes,
            expected_prefix_sha256=str(parent_ledger_sha256),
        )
        if ledger_event_ids() != allowed_ledger:
            raise ValueError("source_control_event_payload_mismatch")
        recovery["ledger_phase"] = "COMMITTED"
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        state = load_state()
        workflow = load_workflow_state_budget()
        txid = recovery.get("parent_transaction_id")
        state_recovered = state.get("recovered_from_source_prepare_control_failure") == txid and not state.get("hard_stopped")
        workflow_recovered = workflow.get("recovered_from_source_prepare_control_failure") == txid and not workflow.get("hard_stopped")
        expected_state_sha256 = (
            migrated_failure.get("authorized_failed_state_sha256")
            if migrated_failure is not None
            else recovery.get("parent_state_sha256")
        )
        if not state_recovered and hashlib.sha256(STATE_PATH.read_bytes()).hexdigest() != expected_state_sha256:
            raise ValueError("source_control_state_drift")
        expected_workflow_sha256 = (
            migrated_failure.get("authorized_failed_workflow_sha256")
            if migrated_failure is not None
            else recovery.get("parent_workflow_sha256")
        )
        if not workflow_recovered and hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest() != expected_workflow_sha256:
            raise ValueError("source_control_workflow_drift")
        if state.get("active_overlap_transaction") not in (None, txid) or workflow.get("active_transaction") not in (None, txid):
            raise ValueError("source_control_recovery_state_active_mismatch")
        if not state_recovered:
            state["hard_stopped"] = False; state["active_overlap_transaction"] = None
            state["recovered_from_source_prepare_control_failure"] = txid
            atomic_owned_json(STATE_PATH, state)
        recovery["state_commit_phase"] = "STATE_COMMITTED"
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        if not workflow_recovered:
            workflow["hard_stopped"] = False; workflow["stage"] = "AUDIT_PASSED"
            workflow["active_transaction"] = None
            workflow["recovered_from_source_prepare_control_failure"] = txid
            atomic_owned_json(OVERLAP_WORKFLOW_STATE, workflow)
        recovery["state_commit_phase"] = "WORKFLOW_COMMITTED"
        recovery["post_state_sha256"] = hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
        recovery["post_workflow_sha256"] = hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest()
        recovery["post_ledger_sha256"] = hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest()
        recovery["state"] = "SUCCESS_COMMITTED"
        recovery["completed_utc"] = utc_now()
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        return 0
    except Exception as exc:
        source_control_hard_stop(recovery, [f"source_control_recovery:{type(exc).__name__}:{exc}"])
        return 125


def validate_launcher_receipt(
    capability_id: str, transaction_id: str, budget_bootstrap: dict[str, object]
) -> str:
    receipt_path = OVERLAP_CAPABILITY_ROOT / f"{capability_id}.launcher-receipt.json"
    consumed_path = OVERLAP_CAPABILITY_ROOT / f"{capability_id}.consumed.json"
    if not receipt_path.is_file() or not consumed_path.is_file():
        raise ValueError("source launcher did not consume capability and produce a receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    consumed = json.loads(consumed_path.read_text(encoding="utf-8"))
    if (
        receipt.get("schema_version") != "m9-overlap-source-launcher-receipt-v1"
        or receipt.get("status") != "PASS"
        or receipt.get("transaction_id") != transaction_id
        or consumed.get("state") != "CONSUMED"
        or consumed.get("transaction_id") != transaction_id
        or receipt.get("budget_bootstrap") != budget_bootstrap
    ):
        raise ValueError("source launcher receipt/capability binding mismatch")
    sources = receipt.get("loaded_sources")
    if not isinstance(sources, dict) or "m9_overlap_common" not in sources:
        raise ValueError("source launcher receipt lacks loaded frozen modules")
    launcher_bootstrap = receipt.get("launcher_bootstrap")
    if (
        not isinstance(launcher_bootstrap, dict)
        or launcher_bootstrap.get("isolated") is not True
        or launcher_bootstrap.get("no_site") is not True
        or launcher_bootstrap.get("dont_write_bytecode") is not True
        or set(launcher_bootstrap.get("modules", {})) != set(BOOTSTRAP_MODULE_NAMES)
    ):
        raise ValueError("source launcher bootstrap provenance mismatch")
    dependency = receipt.get("dependency_path")
    if (
        not isinstance(dependency, dict)
        or dependency.get("path")
        != "/home/evan-williams/deeph-m9/env/deeph-v022/lib/python3.9/site-packages"
        or dependency.get("added_after_capability") is not True
        or dependency.get("method") != "sys.path.append"
        or dependency.get("site_addsitedir_called") is not False
        or dependency.get("pth_processed") is not False
    ):
        raise ValueError("source launcher dependency-path provenance mismatch")
    frozen = json.loads(OVERLAP_FROZEN_HASHES.read_text(encoding="utf-8"))["files"]
    for value in sources.values():
        if not isinstance(value, dict):
            raise ValueError("invalid loaded source receipt")
        path = str(value.get("path"))
        if (
            frozen.get(path) != value.get("sha256")
            or value.get("loader") != "FrozenSourceLoader"
            or value.get("origin") != path
            or value.get("bytecode_consulted") is not False
        ):
            raise ValueError(f"source-only loader provenance mismatch: {path}")
    return hashlib.sha256(receipt_path.read_bytes()).hexdigest()


def recovery_environment() -> dict[str, str]:
    return {
        "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
        "HOME": os.environ["HOME"],
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "DEBIAN_FRONTEND": "noninteractive",
        "HTTP_PROXY": "",
        "HTTPS_PROXY": "",
        "ALL_PROXY": "",
        "http_proxy": "",
        "https_proxy": "",
        "all_proxy": "",
    }


def recovery_manifest() -> tuple[dict[str, object], list[Path]]:
    if not OFFLINE_APT_MANIFEST.is_file():
        raise SystemExit("offline apt manifest is missing")
    manifest = json.loads(OFFLINE_APT_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "m9-offline-apt-manifest-v1":
        raise SystemExit("offline apt manifest schema mismatch")
    entries = manifest.get("packages")
    if not isinstance(entries, list) or len(entries) != 45:
        raise SystemExit("offline apt manifest must contain exactly 45 packages")
    paths: list[Path] = []
    names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("offline apt manifest entry is not an object")
        for field in ("depends", "pre_depends"):
            if not isinstance(entry.get(field), str):
                raise SystemExit(f"offline apt manifest lacks {field}: {entry}")
        if not isinstance(entry.get("source_url"), str) or not entry.get("source_url"):
            raise SystemExit(f"offline apt manifest lacks source_url: {entry}")
        filename = str(entry.get("filename", ""))
        if not filename or filename in names or Path(filename).name != filename:
            raise SystemExit("offline apt manifest filename set is invalid")
        names.add(filename)
        path = (OFFLINE_APT_ARCHIVE_ROOT / filename).resolve(strict=True)
        if path.parent != OFFLINE_APT_ARCHIVE_ROOT.resolve(strict=True) or path.is_symlink():
            raise SystemExit(f"offline apt archive escaped fixed root: {filename}")
        if path.stat().st_size != int(entry.get("bytes", -1)):
            raise SystemExit(f"offline apt archive size mismatch: {filename}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != str(entry.get("sha256")):
            raise SystemExit(f"offline apt archive SHA-256 mismatch: {filename}")
        control = subprocess.check_output(
            [
                "/usr/bin/dpkg-deb",
                "--showformat=${Package}\\n${Version}\\n${Architecture}\\n",
                "-W",
                path.as_posix(),
            ],
            env=recovery_environment(),
            text=True,
        ).splitlines()
        expected = [str(entry.get(key)) for key in ("package", "version", "architecture")]
        if control != expected:
            raise SystemExit(f"offline apt package identity mismatch: {filename}")
        paths.append(path)
    if len(names) != 45:
        raise SystemExit("offline apt manifest package filenames are not unique")
    return manifest, paths


def verify_recovery_source_indices(manifest: dict[str, object]) -> dict[str, str]:
    repository = manifest.get("repository")
    if not isinstance(repository, dict):
        raise SystemExit("offline apt manifest lacks repository provenance")
    keyring = Path(str(repository.get("keyring_path", ""))).resolve(strict=True)
    if hashlib.sha256(keyring.read_bytes()).hexdigest() != str(repository.get("keyring_sha256")):
        raise SystemExit("Ubuntu archive keyring hash mismatch")
    paths = repository.get("index_paths")
    index_hashes = repository.get("packages_index_sha256")
    inrelease = repository.get("inrelease")
    if not isinstance(paths, dict) or not isinstance(index_hashes, dict) or not isinstance(inrelease, dict):
        raise SystemExit("offline apt manifest source index contract is incomplete")
    expected = {
        "jammy_inrelease": str(inrelease.get("jammy")),
        "jammy_updates_inrelease": str(inrelease.get("jammy-updates")),
        "jammy_main_amd64": str(index_hashes.get("jammy-main-amd64")),
        "jammy_universe_amd64": str(index_hashes.get("jammy-universe-amd64")),
        "jammy_updates_main_amd64": str(index_hashes.get("jammy-updates-main-amd64")),
        "jammy_updates_universe_amd64": str(index_hashes.get("jammy-updates-universe-amd64")),
    }
    receipts: dict[str, str] = {"keyring": hashlib.sha256(keyring.read_bytes()).hexdigest()}
    for name, digest in expected.items():
        path = Path(str(paths.get(name, ""))).resolve(strict=True)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Ubuntu apt index hash mismatch: {name}")
        receipts[name] = digest
    for name in ("jammy_inrelease", "jammy_updates_inrelease"):
        path = Path(str(paths[name])).resolve(strict=True)
        result = subprocess.run(
            ["/usr/bin/gpgv", "--keyring", keyring.as_posix(), path.as_posix()],
            env=recovery_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or "Good signature" not in result.stderr:
            raise SystemExit(f"Ubuntu InRelease signature verification failed: {name}")
    inrelease_entries: dict[str, dict[str, tuple[int, str]]] = {}
    for name, path_key in (("jammy", "jammy_inrelease"), ("jammy-updates", "jammy_updates_inrelease")):
        in_text = Path(str(paths[path_key])).read_text(encoding="utf-8", errors="strict")
        suite_entries: dict[str, tuple[int, str]] = {}
        in_section = in_text.split("\nSHA256:\n", 1)[1].split("\nSHA1:\n", 1)[0] if "\nSHA256:\n" in in_text else ""
        for line in in_section.splitlines():
            match = re.fullmatch(r"\s*([0-9a-fA-F]{64})\s+(\d+)\s+(.+)", line)
            if match:
                suite_entries[match.group(3)] = (int(match.group(2)), match.group(1).lower())
        inrelease_entries[name] = suite_entries
    expected_index_paths = {
        "jammy_main_amd64": "main/binary-amd64/Packages",
        "jammy_universe_amd64": "universe/binary-amd64/Packages",
        "jammy_updates_main_amd64": "main/binary-amd64/Packages",
        "jammy_updates_universe_amd64": "universe/binary-amd64/Packages",
    }
    for index_name, relative in expected_index_paths.items():
        index_path = Path(str(paths[index_name]))
        suite = "jammy-updates" if index_name.startswith("jammy_updates_") else "jammy"
        record = inrelease_entries[suite].get(relative)
        if record is None or record != (index_path.stat().st_size, expected[index_name]):
            raise SystemExit(f"InRelease SHA256 record mismatch: {index_name}")
    index_records: dict[tuple[str, str, str], list[tuple[str, str]]] = {}
    for name in ("jammy_main_amd64", "jammy_universe_amd64", "jammy_updates_main_amd64", "jammy_updates_universe_amd64"):
        text = Path(str(paths[name])).read_text(encoding="utf-8", errors="strict")
        for paragraph in text.split("\n\n"):
            fields: dict[str, str] = {}
            for line in paragraph.splitlines():
                key, sep, value = line.partition(": ")
                if sep:
                    fields[key] = value
            if all(key in fields for key in ("Package", "Version", "Architecture", "Filename", "SHA256")):
                key = (fields["Package"], fields["Version"], fields["Architecture"])
                index_records.setdefault(key, [])
                index_records[key].append((fields["Filename"], fields["SHA256"]))
    for entry in manifest.get("packages", []):
        key = (str(entry["package"]), str(entry["version"]), str(entry["architecture"]))
        records = index_records.get(key, [])
        if not records:
            raise SystemExit(f"offline package is absent from frozen Packages records: {key}")
        expected_filename = unquote(str(entry["source_url"]).split("/ubuntu/", 1)[-1])
        expected_filename = re.sub(r"_(?:\d+:)", "_", expected_filename)
        if not any(record == (expected_filename, str(entry["sha256"])) for record in records):
            raise SystemExit(f"offline package index record mismatch: {key}")
    return receipts


def recovery_dpkg_query(packages: list[str]) -> dict[str, str]:
    if not packages:
        return {}
    result: dict[str, str] = {}
    completed = subprocess.run(
        ["/usr/bin/dpkg-query", "-W", "-f=${Package}\t${Version}\t${Status}\n", *packages],
        env=recovery_environment(), text=True, capture_output=True, check=False,
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(f"dpkg-query failed with exit code {completed.returncode}")
    missing = set(re.findall(r"dpkg-query: no packages found matching (\S+)", completed.stderr))
    if missing - set(packages) or any("no packages found matching" not in line for line in completed.stderr.splitlines() if line):
        raise SystemExit("dpkg-query returned an unexpected diagnostic")
    diagnostics = [line for line in completed.stderr.splitlines() if line]
    if len(diagnostics) != len(missing):
        raise SystemExit("dpkg-query returned duplicate or incomplete diagnostics")
    for line in completed.stdout.splitlines():
        fields = line.split("\t", 2)
        if len(fields) != 3 or fields[0] not in packages or fields[0] in result:
            raise SystemExit("dpkg-query returned malformed or duplicate output")
        result[fields[0]] = "\t".join(fields[1:])
    returned = set(result)
    requested = set(packages)
    if returned & missing or returned | missing != requested:
        raise SystemExit("dpkg-query result does not cover the requested package set")
    if completed.returncode == 0 and missing:
        raise SystemExit("dpkg-query returned missing diagnostics with success status")
    if completed.returncode == 1 and not missing:
        raise SystemExit("dpkg-query returned failure status without missing-package diagnostics")
    return result


def classify_recovery_preflight(statuses: dict[str, str], expected_packages: list[str] | None = None) -> dict[str, object]:
    installed: list[str] = []
    placeholders: list[str] = []
    unsafe: list[str] = []
    absent = sorted(set(expected_packages or []) - set(statuses))
    for name, value in statuses.items():
        version, _, status = value.partition("\t")
        if status == "unknown ok not-installed" and version == "":
            placeholders.append(name)
        elif status == "install ok installed":
            installed.append(name)
        else:
            unsafe.append(name)
    return {
        "installed": sorted(installed),
        "placeholder_unknown_not_installed": sorted(placeholders),
        "unsafe": sorted(unsafe),
        "installed_count": len(installed),
        "placeholder_count": len(placeholders),
        "unsafe_count": len(unsafe),
        "absent": absent,
        "absent_count": len(absent),
        "total_expected": len(expected_packages or statuses),
    }


def recovery_global_dpkg_status() -> dict[str, str]:
    completed = subprocess.run(
        ["/usr/bin/dpkg-query", "-W", "-f=${Package}\t${Version}\t${Status}\n"],
        env=recovery_environment(), text=True, capture_output=True, check=False,
    )
    if completed.returncode not in (0, 1):
        raise SystemExit("dpkg-query global status failed")
    lines = sorted(line for line in completed.stdout.splitlines() if line)
    payload = "\n".join(lines) + ("\n" if lines else "")
    records = {line.split("\t", 1)[0]: line.split("\t", 1)[1] for line in lines}
    return {
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "count": len(lines),
        "packages": [line.split("\t", 1)[0] for line in lines],
        "records": records,
        "text": payload,
    }


def recovery_updates_receipt() -> dict[str, object]:
    root = Path("/var/lib/dpkg/updates")
    names = sorted(p.name for p in root.iterdir()) if root.is_dir() else ["<missing>"]
    return {"path": root.as_posix(), "entries": names, "sha256": canonical_hash(names)}


def recovery_network_receipt(env: dict[str, str]) -> dict[str, object]:
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        raise SystemExit("offline recovery network receipt requires root")
    command = recovery_isolated_command(["/bin/cat", "/proc/net/route"])
    code, output, timed_out, pid = run_recovery_child(command, env, LINUX_ROOT.as_posix(), 10.0)
    lines = [line for line in output.splitlines() if line.strip()]
    non_loopback = [line for line in lines[1:] if line.split()[0] != "00000000" and line.split()[0] != "Iface"]
    if code != 0 or timed_out or non_loopback:
        raise SystemExit("offline recovery network namespace is not isolated")
    return {"argv": command, "pid": pid, "exit_code": code, "timed_out": timed_out,
            "stdout_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
            "non_loopback_routes": non_loopback}


def process_receipt(pid: int) -> dict[str, object]:
    proc_root = Path(f"/proc/{pid}")
    stat_fields = proc_root.joinpath("stat").read_text(encoding="utf-8").split()
    return {
        "pid": pid,
        "pgid": os.getpgid(pid),
        "starttime_ticks": int(stat_fields[21]),
        "cmdline_sha256": hashlib.sha256(proc_root.joinpath("cmdline").read_bytes()).hexdigest(),
    }


def resume_pending_recovery_commit(state: dict, workflow: dict, recovery: dict) -> int:
    events = recovery.get("commit_events")
    adjustment = recovery.get("commit_adjustment")
    if not isinstance(events, list) or not isinstance(adjustment, dict):
        hard_stop_recovery(state, workflow, ["offline_recovery_pending_commit_journal_invalid"], recovery, recovery.get("command_sha256"))
        return 125
    for event in events:
        append_event_once(event)
    ledger_hashes = ledger_event_ids()
    if not all(
        ledger_hashes.get(str(event.get("event_id"))) == canonical_hash({k: v for k, v in event.items() if k != "event_id"})
        for event in events
    ):
        hard_stop_recovery(state, workflow, ["offline_recovery_pending_ledger_missing"], recovery, recovery.get("command_sha256"))
        return 125
    existing = {str(item.get("adjustment_id")) for item in state.get("cpu_adjustments", [])}
    if str(adjustment.get("adjustment_id")) not in existing:
        state.setdefault("cpu_adjustments", []).append(adjustment)
    state["offline_recovery_seconds"] = float(recovery.get("elapsed_seconds", 0.0))
    state["hard_stopped"] = False
    state["active_overlap_transaction"] = None
    workflow["stage"] = "AUDIT_PASSED"
    workflow["active_transaction"] = None
    workflow["apt_install_completed"] = True
    workflow["hard_stopped"] = False
    workflow["recovered_from_hard_stop"] = recovery.get("parent_transaction_id")
    atomic_json(STATE_PATH, state)
    atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
    recovery["state"] = "SUCCESS_COMMITTED"
    recovery.setdefault("state_history", []).append({"state": "SUCCESS_COMMITTED", "utc": utc_now()})
    atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
    return 0


def recovery_isolated_command(command: list[str]) -> list[str]:
    return ["/usr/bin/unshare", "--net", "--", *command]


def run_recovery_child(
    command: list[str], env: dict[str, str], cwd: str, timeout: float, on_spawn=None
) -> tuple[int, str, bool, int]:
    proc = subprocess.Popen(
        command,
        env=env,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    if on_spawn is not None:
        try:
            on_spawn(proc.pid)
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.communicate(timeout=5)
            except BaseException:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
                try:
                    proc.communicate()
                except BaseException:
                    pass
            raise
    timed_out = False
    try:
        output, _ = proc.communicate(timeout=max(1.0, timeout))
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            output, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            output, _ = proc.communicate()
    return proc.returncode, output, timed_out, proc.pid


def command_overlap_recover_offline_apt(_: argparse.Namespace) -> int:
    bootstrap = isolated_bootstrap_provenance()
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        raise SystemExit("offline recovery requires root for dpkg and network namespace isolation")
    recovery_gate = verify_recovery_gate_and_hashes()
    env = recovery_environment()
    network_receipt = recovery_network_receipt(env)
    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        workflow = load_workflow_state_budget()
        if OVERLAP_RECOVERY_TRANSACTION.exists():
            existing_recovery = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
            if existing_recovery.get("state") == "SUCCESS_PENDING_COMMIT":
                result = resume_pending_recovery_commit(state, workflow, existing_recovery)
                if result != 0:
                    raise SystemExit("offline recovery pending commit was hard-stopped")
                print(json.dumps({"status": "offline_recovery_commit_resumed"}, sort_keys=True))
                return 0
            if existing_recovery.get("state") not in {"SUCCESS_COMMITTED", "FAILED_COMMITTED"}:
                child_pids = existing_recovery.get("child_pids", [])
                if existing_recovery.get("child_active") and process_matches_receipt(existing_recovery.get("child_process_receipt")):
                    raise SystemExit("offline recovery transaction has a live child; refusing concurrent replay")
                hard_stop_recovery(
                    state, workflow,
                    ["incomplete_offline_recovery_transaction_recovered"],
                    existing_recovery, existing_recovery.get("command_sha256"),
                )
                raise SystemExit("incomplete offline recovery was committed to HARD_STOP")
        parent = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
        if not state.get("hard_stopped") or workflow.get("stage") != "HARD_STOP":
            raise SystemExit("offline recovery requires the dual HARD_STOP state")
        if parent.get("state") != "FAILED_COMMITTED" or parent.get("action") != "apt_install":
            raise SystemExit("offline recovery parent transaction is not the failed apt transaction")
        reasons = set(parent.get("reasons", []))
        if "command_timeout" not in reasons or "overlap_command_failed" not in reasons:
            raise SystemExit("offline recovery requires a timed-out failed apt transaction")
        if OVERLAP_RECOVERY_TRANSACTION.exists():
            raise SystemExit("offline recovery transaction already exists; replay forbidden")
        if OVERLAP_RECOVERY_PARENT.exists():
            raise SystemExit("offline recovery parent snapshot already exists; replay forbidden")
        manifest, paths = recovery_manifest()
        source_index_receipts = verify_recovery_source_indices(manifest)
        package_names = [str(item["package"]) for item in manifest["packages"]]
        if len(set(package_names)) != 45:
            raise SystemExit("offline recovery package names are not unique")
        pre = recovery_dpkg_query(package_names)
        preflight = classify_recovery_preflight(pre, package_names)
        if preflight["total_expected"] != 45 or preflight["absent_count"] + preflight["placeholder_count"] + preflight["installed_count"] + preflight["unsafe_count"] != 45:
            raise SystemExit("offline recovery preflight package classification is not a complete 45-item partition")
        if preflight["installed"] or preflight["unsafe"]:
            raise SystemExit("offline recovery refuses installed or unsafe target package states")
        audit_pre = subprocess.run(
            ["/usr/bin/dpkg", "--audit"],
            env=recovery_environment(),
            cwd=LINUX_ROOT.as_posix(),
            capture_output=True,
            text=True,
            check=False,
        )
        if audit_pre.returncode != 0 or audit_pre.stdout or audit_pre.stderr:
            raise SystemExit("offline recovery requires a clean pre-install dpkg audit")
        updates_root = Path("/var/lib/dpkg/updates")
        if not updates_root.is_dir() or any(updates_root.iterdir()):
            raise SystemExit("offline recovery requires an empty dpkg updates directory")
        elapsed = float(parent.get("elapsed_seconds", 0.0))
        raw = float(state["cpu_seconds"]["overlap_build"])
        if elapsed <= 0 or elapsed > raw or elapsed > CPU_LIMITS["overlap_build"] + 1:
            raise SystemExit("offline recovery parent elapsed time is outside the approved credit bound")
        if float(state.get("offline_recovery_seconds", 0.0)) != 0.0:
            raise SystemExit("offline recovery wall budget has already been consumed")
        parent_bytes = OVERLAP_TRANSACTION.read_bytes()
        authorization_sha = hashlib.sha256(OVERLAP_RECOVERY_AUTHORIZATION.read_bytes()).hexdigest()
        pre_status = recovery_global_dpkg_status()
        pre_updates = recovery_updates_receipt()
        pre_ledger_bytes = LEDGER_PATH.read_bytes() if LEDGER_PATH.exists() else b""
        pre_ledger_lines = pre_ledger_bytes.splitlines()
        pre_ledger_last = hashlib.sha256(pre_ledger_lines[-1]).hexdigest() if pre_ledger_lines else None
        OVERLAP_RECOVERY_PARENT.write_bytes(parent_bytes)
        preserve_owner(OVERLAP_RECOVERY_PARENT)
        if OVERLAP_RECOVERY_PARENT.read_bytes() != parent_bytes:
            raise SystemExit("offline recovery parent snapshot is not byte-identical")
        recovery_id = secrets.token_hex(16)
        recovery = {
            "schema_version": "m9-offline-recovery-transaction-v1",
            "transaction_id": recovery_id,
            "state": "PREPARED",
            "state_history": [{"state": "PREPARED", "utc": utc_now()}],
            "parent_transaction_id": parent.get("transaction_id"),
            "parent_transaction_sha256": hashlib.sha256(parent_bytes).hexdigest(),
            "pre_state_sha256": hashlib.sha256(STATE_PATH.read_bytes()).hexdigest(),
            "pre_workflow_sha256": hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest(),
            "manifest_sha256": hashlib.sha256(OFFLINE_APT_MANIFEST.read_bytes()).hexdigest(),
            "authorization_record_id": "AUTH-M9-OFFLINE-RECOVERY-2026-08-13-01",
            "authorization_record_path": OVERLAP_RECOVERY_AUTHORIZATION.as_posix(),
            "authorization_record_sha256": authorization_sha,
            "recovery_gate_sha256": hashlib.sha256(OVERLAP_RECOVERY_GATE.read_bytes()).hexdigest(),
            "source_index_receipts": source_index_receipts,
            "pre_global_dpkg_status": {k: v for k, v in pre_status.items() if k != "text"},
            "preflight_package_classification": preflight,
            "pre_dpkg_updates": pre_updates,
            "pre_ledger_sha256": hashlib.sha256(pre_ledger_bytes).hexdigest(),
            "pre_ledger_bytes": len(pre_ledger_bytes),
            "pre_ledger_line_count": len(pre_ledger_lines),
            "pre_ledger_last_event_sha256": pre_ledger_last,
            "raw_overlap_build_seconds": raw,
            "approved_credit_seconds": elapsed,
            "recovery_wall_limit_seconds": OFFLINE_RECOVERY_LIMIT,
            "python_bootstrap": bootstrap,
            "prepared_utc": utc_now(),
        }
        workflow["stage"] = "RECOVERY_AUTHORIZED"
        workflow["active_transaction"] = recovery_id
        atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
        state["active_overlap_transaction"] = recovery_id
        atomic_json(STATE_PATH, state)

    start_ns = time.monotonic_ns()
    output_parts: list[str] = []
    command_paths = [path.as_posix() for path in paths]
    source_sandbox = Path(tempfile.mkdtemp(prefix="offline-apt-", dir=LINUX_ROOT))
    source_list = source_sandbox / "sources.list"
    source_parts = source_sandbox / "sources.list.d"
    source_list.write_bytes(b"")
    source_parts.mkdir()
    commands = [
        recovery_isolated_command([
            "/usr/bin/apt-get",
            "-o", f"Dir::Etc::sourcelist={source_list.as_posix()}",
            "-o", f"Dir::Etc::sourceparts={source_parts.as_posix()}",
            "-o", "Acquire::Retries=0",
            "-o", "Acquire::http::Proxy=false",
            "-o", "Acquire::https::Proxy=false",
            "--no-download", "--simulate", "--no-install-recommends", "install",
            *command_paths,
        ]),
        recovery_isolated_command(["/usr/bin/dpkg", "--unpack", "--no-act", *command_paths]),
        recovery_isolated_command(["/usr/bin/dpkg", "--unpack", *command_paths]),
        recovery_isolated_command(["/usr/bin/dpkg", "--configure", "-a"]),
        recovery_isolated_command(["/usr/bin/dpkg", "--audit"]),
        recovery_isolated_command([
            "/usr/bin/apt-get",
            "-o", f"Dir::Etc::sourcelist={source_list.as_posix()}",
            "-o", f"Dir::Etc::sourceparts={source_parts.as_posix()}",
            "-o", "Acquire::Retries=0",
            "-o", "Acquire::http::Proxy=false",
            "-o", "Acquire::https::Proxy=false",
            "check",
        ]),
    ]
    command_sha = canonical_hash(commands)
    exit_code = 0
    timed_out = False
    child_pids: list[int] = []
    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        recovery = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
        recovery["state"] = "OFFLINE_APT_RUNNING"
        recovery["start_utc"] = utc_now()
        recovery.setdefault("state_history", []).append({"state": "OFFLINE_APT_RUNNING", "utc": recovery["start_utc"]})
        atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
        workflow = load_workflow_state_budget()
        workflow["stage"] = "OFFLINE_APT_RUNNING"
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
    try:
        for command in commands:
            remaining = max(1.0, OFFLINE_RECOVERY_LIMIT - (time.monotonic_ns() - start_ns) / 1_000_000_000.0)
            def record_spawn(pid: int, command=command) -> None:
                with LOCK_PATH.open("a+") as lock_handle:
                    fcntl.flock(lock_handle, fcntl.LOCK_EX)
                    current = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
                    current["child_pid"] = pid
                    current["child_command_sha256"] = canonical_hash(command)
                    current["child_started_utc"] = utc_now()
                    current["child_active"] = True
                    current["child_process_receipt"] = process_receipt(pid)
                    atomic_json(OVERLAP_RECOVERY_TRANSACTION, current)
            code, output, command_timed_out, child_pid = run_recovery_child(
                command, env, LINUX_ROOT.as_posix(), remaining, on_spawn=record_spawn
            )
            child_pids.append(child_pid)
            with LOCK_PATH.open("a+") as lock_handle:
                fcntl.flock(lock_handle, fcntl.LOCK_EX)
                current = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
                current["child_active"] = False
                current["child_exit_code"] = code
                current["child_finished_utc"] = utc_now()
                atomic_json(OVERLAP_RECOVERY_TRANSACTION, current)
            timed_out = timed_out or command_timed_out
            output_parts.append("$ " + " ".join(command) + "\n" + output)
            if "/usr/bin/apt-get" in command and "--simulate" in command:
                recovery_solver_output = output
            if code != 0:
                exit_code = code
                break
    except BaseException as exc:
        timed_out = True
        exit_code = 125
        output_parts.append(f"recovery child exception: {type(exc).__name__}: {exc}")
    elapsed_recovery = (time.monotonic_ns() - start_ns) / 1_000_000_000.0
    shutil.rmtree(source_sandbox, ignore_errors=True)
    log_path = LINUX_ROOT / "logs/overlap_offline_apt_recovery.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(output_parts), encoding="utf-8")
    preserve_owner(log_path)

    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        workflow = load_workflow_state_budget()
        recovery = json.loads(OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
        recovery["state"] = "RUNNING"
        recovery.setdefault("state_history", []).append({"state": "RUNNING", "utc": utc_now()})
        recovery["start_utc"] = recovery.get("prepared_utc")
        recovery["end_utc"] = utc_now()
        recovery["elapsed_seconds"] = elapsed_recovery
        recovery["exit_code"] = exit_code
        recovery["timed_out"] = timed_out
        recovery["child_pids"] = child_pids
        recovery["command_sha256"] = command_sha
        recovery["network_receipt"] = network_receipt
        recovery["log_sha256"] = hashlib.sha256(log_path.read_bytes()).hexdigest()
        recovery["solver_output_sha256"] = hashlib.sha256(
            locals().get("recovery_solver_output", "").encode("utf-8")
        ).hexdigest()
        solver_text = locals().get("recovery_solver_output", "")
        if not re.search(r"0 upgraded, 45 newly installed, 0 to remove", solver_text) or solver_text.count("local-deb") < 45:
            post_reasons = ["offline_recovery_solver_contract_mismatch"]
        else:
            post_reasons = []
        if timed_out or elapsed_recovery > OFFLINE_RECOVERY_LIMIT:
            post_reasons.append("offline_recovery_timeout")
        if exit_code != 0:
            post_reasons.append("offline_recovery_command_failed")
        try:
            manifest, _ = recovery_manifest()
            package_names = [str(item["package"]) for item in manifest["packages"]]
            expected_target = {
                str(item["package"]): f"{item['version']}\tinstall ok installed"
                for item in manifest["packages"]
            }
            post = recovery_dpkg_query(package_names)
            if post != expected_target:
                post_reasons.append("offline_recovery_package_status_mismatch")
            audit_post = subprocess.run(
                ["/usr/bin/dpkg", "--audit"],
                env=recovery_environment(),
                cwd=LINUX_ROOT.as_posix(),
                capture_output=True,
                text=True,
                check=False,
            )
            if audit_post.returncode != 0 or audit_post.stdout or audit_post.stderr:
                post_reasons.append("offline_recovery_dpkg_audit_nonempty")
            post_status = recovery_global_dpkg_status()
            post_updates = recovery_updates_receipt()
            recovery["post_global_dpkg_status"] = {k: v for k, v in post_status.items() if k != "text"}
            recovery["post_dpkg_updates"] = post_updates
            pre_names = set(recovery["pre_global_dpkg_status"].get("packages", []))
            post_names = set(post_status.get("packages", []))
            target_names = set(package_names)
            if post_names - pre_names != target_names or pre_names & target_names:
                post_reasons.append("offline_recovery_global_status_set_mismatch")
            pre_records = recovery["pre_global_dpkg_status"].get("records", {})
            post_records = post_status.get("records", {})
            if any(post_records.get(name) != value for name, value in pre_records.items() if name not in target_names):
                post_reasons.append("offline_recovery_existing_status_changed")
            if post_updates["entries"]:
                post_reasons.append("offline_recovery_dpkg_updates_nonempty")
        except Exception as exc:
            post_reasons.append(f"offline_recovery_postcheck:{type(exc).__name__}:{exc}")
        if post_reasons:
            hard_stop_recovery(state, workflow, post_reasons, recovery, recovery.get("command_sha256"))
            recovery["state"] = "FAILED_COMMITTED"
            recovery.setdefault("state_history", []).append({"state": "FAILED_COMMITTED", "utc": utc_now()})
            atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
            return 125
        adjustment = {
            "adjustment_id": secrets.token_hex(16),
            "kind": "noncompute_apt_timeout",
            "bucket": "overlap_build",
            "parent_transaction_id": recovery.get("parent_transaction_id"),
            "parent_transaction_sha256": recovery.get("parent_transaction_sha256"),
            "raw_elapsed_seconds": float(recovery["raw_overlap_build_seconds"]),
            "credited_seconds": float(recovery["approved_credit_seconds"]),
            "effective_overlap_build_seconds": max(
                0.0,
                float(recovery["raw_overlap_build_seconds"])
                - float(recovery["approved_credit_seconds"]),
            ),
            "decision_id": "D-017-offline-recovery-v1",
            "utc": utc_now(),
        }
        recovery["state"] = "SUCCESS_PENDING_COMMIT"
        recovery.setdefault("state_history", []).append({"state": "SUCCESS_PENDING_COMMIT", "utc": utc_now()})
        recovery["commit_adjustment"] = adjustment
        recovery["completed_utc"] = utc_now()
        recovery["commit_events"] = [{
            "event_id": f"{recovery['transaction_id']}:cpu-adjustment",
            "event": "OVERLAP_OFFLINE_RECOVERY_CPU_ADJUSTMENT",
            "utc": adjustment["utc"],
            "transaction_id": recovery.get("transaction_id"),
            "parent_transaction_id": adjustment["parent_transaction_id"],
            "raw_overlap_build_seconds": adjustment["raw_elapsed_seconds"],
            "credited_seconds": adjustment["credited_seconds"],
            "effective_overlap_build_seconds": adjustment["effective_overlap_build_seconds"],
            "decision_id": adjustment["decision_id"],
        }, {
            "event_id": f"{recovery['transaction_id']}:recovery",
            "event": "OVERLAP_OFFLINE_APT_RECOVERY",
            "utc": recovery["completed_utc"],
            "transaction_id": recovery.get("transaction_id"),
            "elapsed_seconds": elapsed_recovery,
            "exit_code": exit_code,
            "manifest_sha256": recovery.get("manifest_sha256"),
            "log_sha256": recovery.get("log_sha256"),
        }]
        atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
        for event in recovery["commit_events"]:
            append_event_once(event)
        ledger_hashes = ledger_event_ids()
        if not all(
            ledger_hashes.get(event["event_id"]) == canonical_hash({k: v for k, v in event.items() if k != "event_id"})
            for event in recovery["commit_events"]
        ):
            hard_stop_recovery(state, workflow, ["offline_recovery_ledger_commit_incomplete"], recovery, command_sha)
            return 125
        state.setdefault("cpu_adjustments", []).append(adjustment)
        state["offline_recovery_seconds"] = elapsed_recovery
        state["hard_stopped"] = False
        state["active_overlap_transaction"] = None
        workflow["stage"] = "AUDIT_PASSED"
        workflow["active_transaction"] = None
        workflow["apt_install_completed"] = True
        workflow["hard_stopped"] = False
        workflow["recovered_from_hard_stop"] = recovery.get("parent_transaction_id")
        atomic_json(STATE_PATH, state)
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
        recovery["state"] = "SUCCESS_COMMITTED"
        recovery.setdefault("state_history", []).append({"state": "SUCCESS_COMMITTED", "utc": utc_now()})
        atomic_json(OVERLAP_RECOVERY_TRANSACTION, recovery)
        return 0


def _command_migrate_unlimited_wall_clock_once(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("D-018 wall-clock migration requires root")
    bootstrap = isolated_bootstrap_provenance()
    gate, bindings, replacement_bytes = verify_unlimited_wall_clock_gate_and_hashes()
    expected_runtime = gate.get("pre_runtime")
    required_runtime = {
        "state_sha256",
        "workflow_sha256",
        "ledger_sha256",
        "ledger_bytes",
        "overlap_transaction_sha256",
        "source_control_recovery_transaction_sha256",
        "source_control_recovery_gate_sha256",
        "active_overlap_gate_sha256",
        "source_products_present",
    }
    if not isinstance(expected_runtime, dict) or set(expected_runtime) != required_runtime:
        raise SystemExit("D-018 gate runtime closure mismatch")
    if expected_runtime.get("source_products_present") != []:
        raise SystemExit("D-018 gate does not bind a product-free pre-state")
    transaction_id = str(gate.get("migration_transaction_id", ""))
    event_id = str(gate.get("migration_event_id", ""))
    if (
        not re.fullmatch(r"[a-z0-9-]{16,96}", transaction_id)
        or event_id != f"{transaction_id}:unlimited-wall-clock"
    ):
        raise SystemExit("D-018 migration identity mismatch")
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        if UNLIMITED_WALL_CLOCK_JOURNAL.exists():
            _, journal = strict_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL)
            if (
                journal.get("schema_version") != "m9-unlimited-wall-clock-journal-v1"
                or journal.get("transaction_id") != transaction_id
                or journal.get("event_id") != event_id
                or journal.get("python_bootstrap") != bootstrap
                or journal.get("gate_receipt") != bindings["gate"]
                or journal.get("pre_runtime") != expected_runtime
            ):
                raise SystemExit("D-018 migration journal binding mismatch")
        else:
            if UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT.exists():
                raise SystemExit("D-018 state snapshot exists without journal")
            if UNLIMITED_WALL_CLOCK_TRANSACTION.exists():
                raise SystemExit("D-018 transaction exists without journal")
            if OVERLAP_AUDIT_GATE_PRE_D018_RETIRED.exists():
                raise SystemExit("D-018 retired overlap gate exists without journal")
            observed = d018_runtime_receipts()
            if observed != expected_runtime:
                raise SystemExit("D-018 formal runtime differs from gate")
            state_receipt, state_bytes = read_stable_regular_bytes(STATE_PATH)
            state = json.loads(state_bytes.decode("utf-8"))
            if (
                state_receipt["sha256"] != expected_runtime["state_sha256"]
                or wall_clock_policy_mode(state) != "LIMITED"
                or state.get("start_utc") != FROZEN_START
                or state.get("deadline_utc") != FROZEN_DEADLINE
                or state.get("hard_stopped")
                or state.get("active_overlap_transaction") is not None
            ):
                raise SystemExit("D-018 pre-state is not the authorized expired limited state")
            workflow = load_workflow_state_budget()
            if (
                workflow.get("hard_stopped")
                or workflow.get("active_transaction") is not None
                or workflow.get("stage") != "AUDIT_PASSED"
            ):
                raise SystemExit("D-018 workflow is not idle and audit-passed")
            old_gate_receipt, _ = read_d018_inode_regular_bytes(OVERLAP_AUDIT_GATE)
            if old_gate_receipt["sha256"] != expected_runtime["active_overlap_gate_sha256"]:
                raise SystemExit("D-018 old overlap gate receipt mismatch")
            snapshot_receipt = {
                "path": UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT.as_posix(),
                "bytes": len(state_bytes),
                "sha256": hashlib.sha256(state_bytes).hexdigest(),
                "uid": 0,
                "gid": 0,
                "mode": 0o600,
                "nlink": 1,
            }
            journal = {
                "schema_version": "m9-unlimited-wall-clock-journal-v1",
                "state": "PREPARED",
                "transaction_id": transaction_id,
                "event_id": event_id,
                "python_bootstrap": bootstrap,
                "gate_receipt": bindings["gate"],
                "pre_runtime": expected_runtime,
                "pre_state_snapshot": snapshot_receipt,
                "old_overlap_gate": old_gate_receipt,
                "replacement_overlap_gate_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
                "replacement_overlap_gate_bytes": len(replacement_bytes),
                "migration_utc": utc_now(),
            }
            journal["context_sha256"] = canonical_hash(d018_journal_context(journal))
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)

        immutable = {
            "workflow_sha256": OVERLAP_WORKFLOW_STATE,
            "overlap_transaction_sha256": OVERLAP_TRANSACTION,
            "source_control_recovery_transaction_sha256": SOURCE_CONTROL_RECOVERY_TRANSACTION,
            "source_control_recovery_gate_sha256": SOURCE_CONTROL_RECOVERY_GATE,
        }
        for key, path in immutable.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_runtime[key]:
                raise SystemExit(f"D-018 immutable runtime drift: {key}")
        if any(path.exists() for path in SOURCE_RECOVERY_PRODUCTS):
            raise SystemExit("D-018 forbids source/build products during migration")
        if not UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT.exists():
            current_state_bytes = STATE_PATH.read_bytes()
            if (
                hashlib.sha256(current_state_bytes).hexdigest()
                != expected_runtime["state_sha256"]
            ):
                raise SystemExit("D-018 state drift before snapshot recovery")
            atomic_root_private_bytes(
                UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT, current_state_bytes
            )
        snapshot_receipt, snapshot = strict_root_private_json(
            UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT
        )
        if (
            snapshot_receipt != journal.get("pre_state_snapshot")
            or snapshot_receipt["sha256"] != expected_runtime["state_sha256"]
        ):
            raise SystemExit("D-018 pre-state snapshot drift")
        state_name = str(journal.get("state"))
        allowed_states = {
            "PREPARED",
            "OLD_GATE_RETIRED",
            "NEW_GATE_CREATED",
            "LEDGER_COMMITTED",
            "STATE_COMMITTED",
            "SUCCESS_COMMITTED",
        }
        if state_name not in allowed_states:
            raise SystemExit("D-018 journal state is invalid")

        if state_name == "SUCCESS_COMMITTED":
            verify_unlimited_wall_clock_execution_ready()
            return 0

        if state_name == "PREPARED":
            active_exists = OVERLAP_AUDIT_GATE.exists()
            retired_exists = OVERLAP_AUDIT_GATE_PRE_D018_RETIRED.exists()
            if active_exists and not retired_exists:
                active_receipt, _ = read_d018_inode_regular_bytes(OVERLAP_AUDIT_GATE)
                if active_receipt != journal["old_overlap_gate"]:
                    raise SystemExit("D-018 old overlap gate drift before retirement")
                retired_receipt = rename_d018_gate_preserving_inode(
                    OVERLAP_AUDIT_GATE,
                    OVERLAP_AUDIT_GATE_PRE_D018_RETIRED,
                    journal["old_overlap_gate"],
                )
            elif active_exists or not retired_exists:
                raise SystemExit("D-018 old overlap gate retirement state mismatch")
            else:
                retired_receipt, _ = read_d018_inode_regular_bytes(
                    OVERLAP_AUDIT_GATE_PRE_D018_RETIRED
                )
            expected_retired = dict(
                journal["old_overlap_gate"],
                path=OVERLAP_AUDIT_GATE_PRE_D018_RETIRED.as_posix(),
            )
            if retired_receipt != expected_retired:
                raise SystemExit("D-018 retired overlap gate receipt mismatch")
            journal["retired_overlap_gate"] = retired_receipt
            journal["state"] = "OLD_GATE_RETIRED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "OLD_GATE_RETIRED"

        if state_name == "OLD_GATE_RETIRED":
            if OVERLAP_AUDIT_GATE.exists():
                active_receipt, _, active_bytes = read_d018_control_json(OVERLAP_AUDIT_GATE)
                if active_bytes != replacement_bytes:
                    raise SystemExit("D-018 replacement overlap gate pre-exists with other bytes")
            else:
                atomic_owned_durable_bytes(
                    OVERLAP_AUDIT_GATE,
                    replacement_bytes,
                    expected_uid=0,
                    expected_gid=1000,
                    expected_mode=0o640,
                )
                active_receipt, _, active_bytes = read_d018_control_json(OVERLAP_AUDIT_GATE)
            if (
                active_bytes != replacement_bytes
                or active_receipt["sha256"] != journal["replacement_overlap_gate_sha256"]
            ):
                raise SystemExit("D-018 replacement overlap gate mismatch")
            journal["replacement_overlap_gate"] = active_receipt
            journal["state"] = "NEW_GATE_CREATED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "NEW_GATE_CREATED"

        policy = d018_policy(gate, bindings)
        event = d018_migration_event(journal, gate, bindings)
        if state_name == "NEW_GATE_CREATED":
            ledger_commit = commit_exact_existing_ledger_event(
                event,
                prefix_bytes=int(expected_runtime["ledger_bytes"]),
                prefix_sha256=str(expected_runtime["ledger_sha256"]),
            )
            journal["ledger_commit"] = ledger_commit
            journal["ledger_sha256"] = ledger_commit["final_sha256"]
            journal["state"] = "LEDGER_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "LEDGER_COMMITTED"

        migrated_state = dict(snapshot)
        migrated_state["wall_clock_policy"] = policy
        migrated_state["last_event_utc"] = journal["migration_utc"]
        if state_name == "LEDGER_COMMITTED":
            current_sha = hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
            if current_sha == expected_runtime["state_sha256"]:
                atomic_owned_json(STATE_PATH, migrated_state)
            elif json.loads(STATE_PATH.read_text(encoding="utf-8")) != migrated_state:
                raise SystemExit("D-018 budget state drift before commit")
            if wall_clock_policy_mode(load_state()) != "UNLIMITED":
                raise SystemExit("D-018 budget state policy commit mismatch")
            journal["migrated_state_sha256"] = hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
            journal["state"] = "STATE_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "STATE_COMMITTED"

        transaction = {
            "schema_version": "m9-unlimited-wall-clock-transaction-v1",
            "state": "SUCCESS_COMMITTED",
            "transaction_id": transaction_id,
            "event_id": event_id,
            "decision_id": "D-018",
            "policy": policy,
            "gate_receipt": bindings["gate"],
            "pre_runtime": expected_runtime,
            "pre_state_snapshot": journal["pre_state_snapshot"],
            "retired_overlap_gate": journal["retired_overlap_gate"],
            "replacement_overlap_gate": journal["replacement_overlap_gate"],
            "ledger_commit": journal["ledger_commit"],
            "ledger_sha256": journal["ledger_sha256"],
            "migrated_state_sha256": journal["migrated_state_sha256"],
            "journal_path": UNLIMITED_WALL_CLOCK_JOURNAL.as_posix(),
            "journal_context_sha256": journal["context_sha256"],
            "completed_utc": journal["migration_utc"],
        }
        if state_name == "STATE_COMMITTED":
            terminal_journal = dict(journal)
            terminal_journal["state"] = "SUCCESS_COMMITTED"
            terminal_journal["completed_utc"] = journal["migration_utc"]
            terminal_journal_bytes = (
                json.dumps(terminal_journal, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            transaction["journal_sha256"] = hashlib.sha256(
                terminal_journal_bytes
            ).hexdigest()
            payload = (json.dumps(transaction, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            if UNLIMITED_WALL_CLOCK_TRANSACTION.exists():
                receipt, current, current_bytes = read_d018_control_json(
                    UNLIMITED_WALL_CLOCK_TRANSACTION
                )
                if current != transaction or current_bytes != payload:
                    raise SystemExit("D-018 transaction pre-exists with other bytes")
            else:
                atomic_owned_durable_bytes(
                    UNLIMITED_WALL_CLOCK_TRANSACTION,
                    payload,
                    expected_uid=0,
                    expected_gid=1000,
                    expected_mode=0o640,
                )
                receipt, current, current_bytes = read_d018_control_json(
                    UNLIMITED_WALL_CLOCK_TRANSACTION
                )
            if current != transaction or current_bytes != payload:
                raise SystemExit("D-018 transaction commit mismatch")
            atomic_root_private_json(
                UNLIMITED_WALL_CLOCK_JOURNAL, terminal_journal
            )
            verify_unlimited_wall_clock_execution_ready()
            print(json.dumps({"status": "unlimited_wall_clock_migrated", "transaction_id": transaction_id}, sort_keys=True))
            return 0
        raise SystemExit("D-018 migration journal cannot be resumed")


def commit_d018_failure(exc: BaseException) -> int:
    """Crash-resumably commit a deterministic D-018 failure without erasing history."""
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        _, journal = strict_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL)
        failure_states = {
            "FAILURE_PREPARED",
            "FAILURE_LEDGER_COMMITTED",
            "FAILURE_BUDGET_COMMITTED",
            "FAILURE_WORKFLOW_COMMITTED",
            "FAILED_COMMITTED",
        }
        state_name = str(journal.get("state"))
        if state_name not in failure_states:
            reason = f"D018_MIGRATION_FAILURE:{type(exc).__name__}:{exc}"
            state_before = load_state()
            workflow_before = load_workflow_state_budget()
            ledger_receipt, ledger_bytes = read_stable_regular_bytes(LEDGER_PATH)
            ledger_event_ids_from_bytes(ledger_bytes)
            failure_utc = utc_now()
            failed_state = dict(state_before)
            failed_state["hard_stopped"] = True
            failed_state["active_overlap_transaction"] = None
            failed_state["last_event_utc"] = failure_utc
            failed_state["d018_failure"] = {
                "transaction_id": journal["transaction_id"],
                "reason": reason,
                "utc": failure_utc,
            }
            failed_workflow = dict(workflow_before)
            failed_workflow["hard_stopped"] = True
            failed_workflow["stage"] = "HARD_STOP"
            failed_workflow["active_transaction"] = None
            failed_workflow["hard_stop_reason"] = [reason]
            failed_workflow["hard_stop_utc"] = failure_utc
            journal["failure"] = {
                "reason": reason,
                "utc": failure_utc,
                "event_id": f"{journal['transaction_id']}:failure",
                "ledger_prefix_bytes": len(ledger_bytes),
                "ledger_prefix_sha256": ledger_receipt["sha256"],
                "state_before_sha256": hashlib.sha256(STATE_PATH.read_bytes()).hexdigest(),
                "workflow_before_sha256": hashlib.sha256(
                    OVERLAP_WORKFLOW_STATE.read_bytes()
                ).hexdigest(),
                "failed_state": failed_state,
                "failed_workflow": failed_workflow,
                "original_journal_state": state_name,
            }
            journal["state"] = "FAILURE_PREPARED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "FAILURE_PREPARED"
        failure = journal.get("failure")
        if not isinstance(failure, dict):
            raise SystemExit("D-018 failure journal is incomplete")
        event = {
            "event_id": failure["event_id"],
            "event": "M9_UNLIMITED_WALL_CLOCK_MIGRATION_HARD_STOP",
            "utc": failure["utc"],
            "decision_id": "D-018",
            "transaction_id": journal["transaction_id"],
            "reason": failure["reason"],
            "original_journal_state": failure["original_journal_state"],
        }
        if state_name == "FAILURE_PREPARED":
            commit = commit_exact_existing_ledger_event(
                event,
                prefix_bytes=int(failure["ledger_prefix_bytes"]),
                prefix_sha256=str(failure["ledger_prefix_sha256"]),
            )
            journal["failure"]["ledger_commit"] = commit
            journal["state"] = "FAILURE_LEDGER_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "FAILURE_LEDGER_COMMITTED"
        if state_name == "FAILURE_LEDGER_COMMITTED":
            current_sha = hashlib.sha256(STATE_PATH.read_bytes()).hexdigest()
            target_state = failure["failed_state"]
            target_bytes = (json.dumps(target_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            if current_sha == failure["state_before_sha256"]:
                atomic_owned_json(STATE_PATH, target_state)
            elif STATE_PATH.read_bytes() != target_bytes:
                raise SystemExit("D-018 failure budget-state drift")
            journal["failure"]["failed_state_sha256"] = hashlib.sha256(
                STATE_PATH.read_bytes()
            ).hexdigest()
            journal["state"] = "FAILURE_BUDGET_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "FAILURE_BUDGET_COMMITTED"
        if state_name == "FAILURE_BUDGET_COMMITTED":
            current_sha = hashlib.sha256(OVERLAP_WORKFLOW_STATE.read_bytes()).hexdigest()
            target_workflow = failure["failed_workflow"]
            target_bytes = (
                json.dumps(target_workflow, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            if current_sha == failure["workflow_before_sha256"]:
                atomic_owned_json(OVERLAP_WORKFLOW_STATE, target_workflow)
            elif OVERLAP_WORKFLOW_STATE.read_bytes() != target_bytes:
                raise SystemExit("D-018 failure workflow drift")
            journal["failure"]["failed_workflow_sha256"] = hashlib.sha256(
                OVERLAP_WORKFLOW_STATE.read_bytes()
            ).hexdigest()
            journal["state"] = "FAILURE_WORKFLOW_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "FAILURE_WORKFLOW_COMMITTED"
        failure_transaction = {
            "schema_version": "m9-unlimited-wall-clock-transaction-v1",
            "state": "FAILED_COMMITTED",
            "transaction_id": journal["transaction_id"],
            "event_id": journal["event_id"],
            "failure_event_id": failure["event_id"],
            "decision_id": "D-018",
            "gate_receipt": journal["gate_receipt"],
            "pre_runtime": journal["pre_runtime"],
            "pre_state_snapshot": journal["pre_state_snapshot"],
            "failure": {
                "reason": failure["reason"],
                "utc": failure["utc"],
                "original_journal_state": failure["original_journal_state"],
                "ledger_commit": failure["ledger_commit"],
                "failed_state_sha256": failure["failed_state_sha256"],
                "failed_workflow_sha256": failure["failed_workflow_sha256"],
            },
        }
        if state_name == "FAILURE_WORKFLOW_COMMITTED":
            payload = (
                json.dumps(failure_transaction, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            atomic_owned_durable_bytes(
                UNLIMITED_WALL_CLOCK_TRANSACTION,
                payload,
                expected_uid=0,
                expected_gid=1000,
                expected_mode=0o640,
            )
            transaction_receipt, _, _ = read_d018_control_json(
                UNLIMITED_WALL_CLOCK_TRANSACTION
            )
            journal["failure_transaction_receipt"] = transaction_receipt
            journal["state"] = "FAILED_COMMITTED"
            atomic_root_private_json(UNLIMITED_WALL_CLOCK_JOURNAL, journal)
            state_name = "FAILED_COMMITTED"
        if state_name != "FAILED_COMMITTED":
            raise SystemExit("D-018 failure commit cannot be resumed")
        transaction_receipt, transaction, _ = read_d018_control_json(
            UNLIMITED_WALL_CLOCK_TRANSACTION
        )
        if (
            transaction != failure_transaction
            or transaction_receipt != journal.get("failure_transaction_receipt")
            or not load_state().get("hard_stopped")
            or not load_workflow_state_budget().get("hard_stopped")
        ):
            raise SystemExit("D-018 failed terminal evidence mismatch")
        return 125


def command_migrate_unlimited_wall_clock(args: argparse.Namespace) -> int:
    try:
        return _command_migrate_unlimited_wall_clock_once(args)
    except D018SimulatedPowerLoss:
        raise
    except (Exception, SystemExit) as exc:
        if not UNLIMITED_WALL_CLOCK_JOURNAL.exists():
            raise
        return commit_d018_failure(exc)


def command_overlap_run(args: argparse.Namespace) -> int:
    if hasattr(os, "geteuid") and os.geteuid() != 1000:
        raise SystemExit("ordinary overlap source operations require the project UID 1000")
    bootstrap = isolated_bootstrap_provenance()
    if args.bucket != "none":
        raise SystemExit("overlap-only operations must not use a GPU bucket")
    if Path(args.config or "").resolve(strict=False) != OVERLAP_CONTRACT.resolve(strict=False):
        raise SystemExit("overlap-only operations require the frozen contract path")
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        workflow = load_workflow_state_budget()
        active = state.get("active_overlap_transaction")
        transaction = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
        transaction_terminal = transaction.get("state") in {
            "IDLE",
            "SUCCESS_COMMITTED",
            "FAILED_COMMITTED",
        }
        if (
            active is not None
            or workflow.get("active_transaction") is not None
            or not transaction_terminal
        ):
            if process_is_live(transaction.get("child_pid")):
                raise SystemExit("another overlap operation is currently active")
            hard_stop_both(
                state,
                workflow,
                ["incomplete_overlap_transaction_recovered"],
                transaction,
                transaction.get("command_sha256"),
            )
            return 125
        action, bucket, required_forecast = validate_overlap_request(args, workflow)
        current_wall_mode = wall_clock_policy_mode(state)
        if current_wall_mode == "UNLIMITED":
            verify_unlimited_wall_clock_execution_ready()
            fact = verify_unlimited_wall_clock_execution_fact_gate()
            if (
                fact.get("gate", {}).get("scope")
                != "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"
                or action != "source_prepare"
            ):
                raise SystemExit("D-018 execution fact gate does not authorize this action")
            gate_runtime = fact["gate"]["runtime"]
            if d018_execution_runtime_receipts() != gate_runtime:
                raise SystemExit("D-018 runtime drift inside the budget lock")
        elif current_wall_mode == "INVALID":
            raise SystemExit("invalid D-018 wall-clock policy")
        elif workflow.get("recovered_from_source_prepare_control_failure"):
            verify_source_control_recovery_gate_and_hashes()
        elif workflow.get("recovered_from_hard_stop"):
            verify_recovered_overlap_gate_and_hashes()
        else:
            verify_overlap_gate_and_hashes()
        before_reasons = violations(state, int(args.forecast_bytes))
        if not isinstance(state.get("overlap_storage_baseline"), dict):
            before_reasons.append("overlap_storage_baseline_missing")
        used = effective_cpu_seconds(state, bucket)
        if used >= CPU_LIMITS[bucket]:
            before_reasons.append(f"cpu_bucket_{bucket}")
        if before_reasons:
            transaction = {
                "schema_version": "m9-overlap-transaction-v1",
                "transaction_id": secrets.token_hex(16),
                "state": "PRECHECK_FAILED",
                "action": action,
            }
            hard_stop_both(state, workflow, before_reasons, transaction, None)
            return 125
        transaction_id = secrets.token_hex(16)
        capability_id = secrets.token_hex(16)
        if action == "apt_install":
            command = list(OVERLAP_APT_COMMAND)
            capability_id = ""
        else:
            command = [
                OVERLAP_PYTHON.resolve(strict=True).as_posix(),
                "-I",
                "-S",
                "-B",
                OVERLAP_SOURCE_LAUNCHER.resolve(strict=True).as_posix(),
                "--capability-id",
                capability_id,
            ]
        command_hash = canonical_hash(command)
        transaction = {
            "schema_version": "m9-overlap-transaction-v1",
            "transaction_id": transaction_id,
            "state": "PREPARED",
            "action": action,
            "structure_id": args.structure_id,
            "bucket": bucket,
            "forecast_bytes": int(args.forecast_bytes),
            "required_forecast_bytes": required_forecast,
            "command_sha256": command_hash,
            "python_bootstrap": bootstrap,
            "prepared_utc": utc_now(),
        }
        state["active_overlap_transaction"] = transaction_id
        workflow["active_transaction"] = transaction_id
        atomic_json(OVERLAP_TRANSACTION, transaction)
        atomic_json(STATE_PATH, state)
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
        budget_status = overlap_status_payload(state)

    fixed_path = "/usr/sbin:/usr/bin:/sbin:/bin"
    child_env = {
        "PATH": fixed_path,
        "HOME": os.environ["HOME"],
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if action == "apt_install":
        child_env["DEBIAN_FRONTEND"] = "noninteractive"
    wall_remaining = deadline_remaining(state)
    cpu_remaining = CPU_LIMITS[bucket] - effective_cpu_seconds(state, bucket)
    timeout_seconds = (
        cpu_remaining
        if wall_remaining is None
        else min(wall_remaining, cpu_remaining)
    )
    start_utc = utc_now()
    start_ns = time.monotonic_ns()
    capture_output = args.log is not None
    proc = None
    try:
        proc = subprocess.Popen(
            command,
            cwd=args.cwd or str(LINUX_ROOT),
            env=child_env,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT if capture_output else None,
            start_new_session=True,
        )
        if action != "apt_install":
            capability = {
                "schema_version": "m9-overlap-capability-v1",
                "state": "BOUND",
                "capability_id": capability_id,
                "transaction_id": transaction_id,
                "child_pid": proc.pid,
                "budget_pid": os.getpid(),
                "budget_argv": [
                    item.decode("utf-8")
                    for item in Path(f"/proc/{os.getpid()}/cmdline").read_bytes().split(b"\0")
                    if item
                ],
                "action": action,
                "structure_id": args.structure_id,
                "bucket": bucket,
                "forecast_bytes": int(args.forecast_bytes),
                "required_forecast_bytes": required_forecast,
                "launcher_argv": command,
                "budget_status": budget_status,
                "budget_bootstrap": bootstrap,
                "issued_utc": utc_now(),
            }
        with LOCK_PATH.open("a+") as lock_handle:
            fcntl.flock(lock_handle, fcntl.LOCK_EX)
            transaction = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
            transaction["state"] = "RUNNING"
            transaction["child_pid"] = proc.pid
            transaction["start_utc"] = start_utc
            atomic_json(OVERLAP_TRANSACTION, transaction)
            if action != "apt_install":
                atomic_private_json(
                    OVERLAP_CAPABILITY_ROOT / f"{capability_id}.json", capability
                )
    except BaseException as exc:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        with LOCK_PATH.open("a+") as lock_handle:
            fcntl.flock(lock_handle, fcntl.LOCK_EX)
            state = load_state()
            workflow = load_workflow_state_budget()
            transaction = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
            hard_stop_both(
                state,
                workflow,
                [f"overlap_child_start_failed:{type(exc).__name__}:{exc}"],
                transaction,
                command_hash,
            )
        return 125

    timed_out = False
    output = b""
    try:
        if capture_output:
            output, _ = proc.communicate(timeout=max(1.0, timeout_seconds))
            exit_code = proc.returncode
        else:
            exit_code = proc.wait(timeout=max(1.0, timeout_seconds))
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            if capture_output:
                tail, _ = proc.communicate(timeout=30)
                output += tail or b""
                exit_code = proc.returncode
            else:
                exit_code = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            if capture_output:
                tail, _ = proc.communicate()
                output += tail or b""
                exit_code = proc.returncode
            else:
                exit_code = proc.wait()
    end_ns = time.monotonic_ns()
    end_utc = utc_now()
    elapsed = (end_ns - start_ns) / 1_000_000_000.0
    if capture_output:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_bytes(output)
        preserve_owner(log_path)
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()

    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        workflow = load_workflow_state_budget()
        transaction = json.loads(OVERLAP_TRANSACTION.read_text(encoding="utf-8"))
        state["cpu_seconds"][bucket] = float(state["cpu_seconds"][bucket]) + elapsed
        state["last_event_utc"] = end_utc
        transaction["end_utc"] = end_utc
        transaction["elapsed_seconds"] = elapsed
        transaction["exit_code"] = exit_code
        transaction["timed_out"] = timed_out
        reasons = []
        launcher_receipt_sha256 = None
        if timed_out:
            reasons.append("command_timeout")
        if exit_code != 0:
            reasons.append("overlap_command_failed")
        if not reasons and action != "apt_install":
            try:
                launcher_receipt_sha256 = validate_launcher_receipt(
                    capability_id, transaction_id, bootstrap
                )
            except Exception as exc:
                reasons.append(f"launcher_receipt_invalid:{type(exc).__name__}:{exc}")
        expected_success_stage = {
            "apt_install": "AUDIT_PASSED",
            "source_prepare": "SOURCES_PREPARED",
            "source_build": "BUILD_PASSED",
            "smoke_prepare": "SMOKE_INPUT_READY",
            "smoke_run": "SMOKE_PASSED",
            "project": "PROJECTION_PASSED",
            "batch_prepare": "BATCH_INPUT_READY",
            "batch_run": ("BATCH_RUNNING", "BATCH_COMPLETE"),
        }[action]
        allowed_success = (
            expected_success_stage
            if isinstance(expected_success_stage, tuple)
            else (expected_success_stage,)
        )
        if not reasons and workflow.get("stage") not in allowed_success:
            reasons.append("workflow_success_stage_mismatch")
        if not reasons and action == "apt_install":
            workflow["apt_install_completed"] = True
        after_reasons = violations(state)
        reasons.extend(after_reasons)
        if reasons:
            hard_stop_both(state, workflow, reasons, transaction, command_hash)
            return 124 if timed_out else 125
        state["active_overlap_transaction"] = None
        workflow["active_transaction"] = None
        atomic_json(STATE_PATH, state)
        atomic_json(OVERLAP_WORKFLOW_STATE, workflow)
        transaction["state"] = "SUCCESS_COMMITTED"
        transaction["launcher_receipt_sha256"] = launcher_receipt_sha256
        atomic_json(OVERLAP_TRANSACTION, transaction)
        event = {
            "event": "OVERLAP_COMMAND",
            "transaction_id": transaction_id,
            "action": action,
            "structure_id": args.structure_id,
            "cpu_bucket": bucket,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "elapsed_seconds": elapsed,
            "pid": proc.pid,
            "exit_code": exit_code,
            "command_sha256": command_hash,
            "config_sha256": hashlib.sha256(OVERLAP_CONTRACT.read_bytes()).hexdigest(),
            "forecast_bytes": int(args.forecast_bytes),
            "required_forecast_bytes": required_forecast,
            "python_bootstrap": bootstrap,
            "launcher_receipt_sha256": launcher_receipt_sha256,
            "cpu_seconds": state["cpu_seconds"],
            "storage": storage_snapshot(state),
        }
        append_event(event)
    return 0


def command_overlap_recover_source_control_failure(_: argparse.Namespace) -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("source-control recovery requires root")
    bootstrap = isolated_bootstrap_provenance()
    gate = verify_source_control_recovery_gate_and_hashes()
    gate_receipt = source_control_gate_receipt(gate)
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        existing = None
        if SOURCE_CONTROL_RECOVERY_TRANSACTION.exists():
            existing = json.loads(SOURCE_CONTROL_RECOVERY_TRANSACTION.read_text(encoding="utf-8"))
            if existing.get("state") == "SUCCESS_COMMITTED":
                result = source_control_resume(existing, bootstrap, gate_receipt)
                if result == 0:
                    print(json.dumps({"status": "source_control_already_recovered", "transaction_id": existing.get("transaction_id")}, sort_keys=True))
                return result
            if existing.get("state") in {"PREPARED", "CAPABILITY_RETIRED", "SUCCESS_PENDING_COMMIT"}:
                result = source_control_resume(existing, bootstrap, gate_receipt)
                if result == 0:
                    print(json.dumps({"status": "source_control_recovery_resumed", "transaction_id": existing.get("transaction_id")}, sort_keys=True))
                return result
            if existing.get("state") == "FAILED_COMMITTED" and existing.get("post_failure_migration") is not None:
                result = source_control_resume(existing, bootstrap, gate_receipt)
                if result == 0:
                    print(json.dumps({"status": "source_control_recovery_resumed_after_ledger_fix", "transaction_id": existing.get("transaction_id")}, sort_keys=True))
                return result
            raise SystemExit("source-control recovery transaction is terminal and cannot replay")
        gate = verify_source_control_recovery_gate_and_hashes()
        gate_receipt = source_control_gate_receipt(gate)
        tx, cap, cap_stat = source_control_preflight(gate)
        tx_bytes = OVERLAP_TRANSACTION.read_bytes()
        state_bytes = STATE_PATH.read_bytes()
        workflow_bytes = OVERLAP_WORKFLOW_STATE.read_bytes()
        ledger_bytes = LEDGER_PATH.read_bytes()
        cap_bytes = cap.read_bytes()
        retired = cap.with_name(cap.stem + ".retired.json")
        recovery_id = secrets.token_hex(16)
        event = {
            "event_id": f"{recovery_id}:source-control-recovery",
            "event": "OVERLAP_SOURCE_CONTROL_FAILURE_RECOVERY",
            "transaction_id": recovery_id,
            "parent_transaction_id": tx.get("transaction_id"),
            "utc": utc_now(),
            "stale_capability_sha256": hashlib.sha256(cap_bytes).hexdigest(),
            "stale_capability_path": cap.as_posix(),
            "retired_capability_path": retired.as_posix(),
        }
        recovery = existing or {
            "schema_version": "m9-source-control-recovery-v1",
            "transaction_id": recovery_id,
            "parent_transaction_id": tx.get("transaction_id"),
            "parent_transaction_sha256": hashlib.sha256(tx_bytes).hexdigest(),
            "parent_transaction_bytes": len(tx_bytes),
            "parent_state_sha256": hashlib.sha256(state_bytes).hexdigest(),
            "parent_state_bytes": len(state_bytes),
            "parent_workflow_sha256": hashlib.sha256(workflow_bytes).hexdigest(),
            "parent_workflow_bytes": len(workflow_bytes),
            "parent_ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
            "parent_ledger_bytes": len(ledger_bytes),
            "parent_ledger_event_hashes": ledger_event_ids(),
            "stale_capability_before": cap_stat,
            "stale_capability_path": cap.as_posix(),
            "retired_capability_path": retired.as_posix(),
            "stale_capability_sha256": hashlib.sha256(cap_bytes).hexdigest(),
            "event": event,
            "python_bootstrap": bootstrap,
            "gate_receipt": gate_receipt,
            "state": "PREPARED",
            "prepared_utc": utc_now(),
        }
        if existing is None:
            if SOURCE_CONTROL_RECOVERY_PARENT.exists():
                if SOURCE_CONTROL_RECOVERY_PARENT.read_bytes() != tx_bytes:
                    raise SystemExit("existing source-control parent snapshot differs")
            else:
                parent_tmp = SOURCE_CONTROL_RECOVERY_PARENT.with_suffix(SOURCE_CONTROL_RECOVERY_PARENT.suffix + ".tmp")
                parent_tmp.write_bytes(tx_bytes)
                preserve_owner(parent_tmp)
                os.replace(parent_tmp, SOURCE_CONTROL_RECOVERY_PARENT)
                preserve_owner(SOURCE_CONTROL_RECOVERY_PARENT)
            if SOURCE_CONTROL_RECOVERY_PARENT.read_bytes() != tx_bytes:
                raise SystemExit("source-control parent snapshot bytes differ")
            recovery["parent_snapshot_sha256"] = hashlib.sha256(SOURCE_CONTROL_RECOVERY_PARENT.read_bytes()).hexdigest()
            recovery["parent_snapshot_bytes"] = len(tx_bytes)
            atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        if not retired.exists():
            os.replace(cap, retired)
        retired_stat = file_stat_receipt(retired)
        if retired_stat["bytes"] != cap_stat["bytes"] or retired_stat["sha256"] != cap_stat["sha256"] or retired_stat["uid"] != cap_stat["uid"] or retired_stat["gid"] != cap_stat["gid"] or retired_stat["mode"] != cap_stat["mode"]:
            raise SystemExit("retired capability receipt mismatch")
        recovery["retired_capability"] = retired_stat
        recovery["state"] = "CAPABILITY_RETIRED"
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        recovery["event"] = event
        recovery["state"] = "SUCCESS_PENDING_COMMIT"
        atomic_owned_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)
        result = source_control_resume(recovery, bootstrap, gate_receipt)
        if result != 0:
            return result
        print(json.dumps({"status": "source_control_recovered", "transaction_id": recovery_id}, sort_keys=True))
        return 0


def command_run(args: argparse.Namespace) -> int:
    if args.overlap_operation:
        return command_overlap_run(args)
    if not args.command:
        raise SystemExit("missing command after --")
    if args.cpu_bucket != "none" or args.overlap_action or args.structure_id:
        raise SystemExit("non-overlap commands cannot use overlap CPU/action fields")
    if args.forecast_bytes is not None and args.forecast_bytes < 0:
        raise SystemExit("--forecast-bytes must be non-negative")
    forecast_bytes = 0 if args.forecast_bytes is None else args.forecast_bytes
    with LOCK_PATH.open("r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        locked_wall_mode = wall_clock_policy_mode(state)
        if locked_wall_mode == "INVALID":
            raise SystemExit("invalid D-018 wall-clock policy")
        if locked_wall_mode == "UNLIMITED":
            raise SystemExit(
                "D-018 forbids generic commands; use a separately audited action API"
            )
        command = args.command
        command_hash = canonical_hash(command)
        config_hash = None
        if args.config:
            config_hash = hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
        before_reasons = violations(state, forecast_bytes)
        if args.bucket != "none":
            used = float(state["gpu_seconds"][args.bucket])
            if used >= GPU_LIMITS[args.bucket]:
                before_reasons.append(f"gpu_bucket_{args.bucket}")
        if before_reasons:
            hard_stop(state, sorted(set(before_reasons)), command_hash)
            print(json.dumps({"status": "hard_stop", "reasons": before_reasons}), file=sys.stderr)
            return 125
        wall_remaining = deadline_remaining(state)
        timeout_seconds = wall_remaining
        if args.bucket != "none":
            gpu_remaining = GPU_LIMITS[args.bucket] - float(state["gpu_seconds"][args.bucket])
            timeout_seconds = (
                gpu_remaining
                if timeout_seconds is None
                else min(timeout_seconds, gpu_remaining)
            )
        start_utc = utc_now()
        start_ns = time.monotonic_ns()
        capture_output = args.log is not None
        child_env = dict(os.environ)
        proc = subprocess.Popen(
            command,
            cwd=args.cwd or str(LINUX_ROOT),
            env=child_env,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT if capture_output else None,
            start_new_session=True,
        )
        timed_out = False
        output = b""
        try:
            if capture_output:
                output, _ = proc.communicate(
                    timeout=None if timeout_seconds is None else max(1.0, timeout_seconds)
                )
                exit_code = proc.returncode
            else:
                exit_code = proc.wait(
                    timeout=None if timeout_seconds is None else max(1.0, timeout_seconds)
                )
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                if capture_output:
                    tail, _ = proc.communicate(timeout=30)
                    output += tail or b""
                    exit_code = proc.returncode
                else:
                    exit_code = proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                if capture_output:
                    tail, _ = proc.communicate()
                    output += tail or b""
                    exit_code = proc.returncode
                else:
                    exit_code = proc.wait()
        if capture_output:
            log_path = Path(args.log)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_bytes(output)
            preserve_owner(log_path)
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()
        end_ns = time.monotonic_ns()
        end_utc = utc_now()
        elapsed = (end_ns - start_ns) / 1_000_000_000.0
        if args.bucket != "none":
            state["gpu_seconds"][args.bucket] = float(state["gpu_seconds"][args.bucket]) + elapsed
        state["last_event_utc"] = end_utc
        atomic_json(STATE_PATH, state)
        event = {
            "event": "COMMAND",
            "bucket": args.bucket,
            "cpu_bucket": args.cpu_bucket,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "start_monotonic_ns": start_ns,
            "end_monotonic_ns": end_ns,
            "elapsed_seconds": elapsed,
            "pid": proc.pid,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "command_sha256": command_hash,
            "config_sha256": config_hash,
            "log_path": args.log,
            "log_sha256": hashlib.sha256(output).hexdigest() if capture_output else None,
            "forecast_bytes": forecast_bytes,
            "overlap_operation": args.overlap_operation,
            "gpu_seconds": state["gpu_seconds"],
            "cpu_seconds": state["cpu_seconds"],
            "storage": storage_snapshot(state),
        }
        append_event(event)
        after_reasons = violations(state)
        if timed_out or after_reasons:
            reasons = (
                (["command_timeout"] if timed_out else [])
                + after_reasons
            )
            hard_stop(state, sorted(set(reasons)), command_hash)
            return 124 if timed_out else 125
        return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init")
    init.set_defaults(func=command_init)
    status = sub.add_parser("status")
    status.set_defaults(func=command_status)
    overlap_init = sub.add_parser("overlap-init")
    overlap_init.set_defaults(func=command_overlap_init)
    recover = sub.add_parser("overlap-recover-offline-apt")
    recover.set_defaults(func=command_overlap_recover_offline_apt)
    source_recover = sub.add_parser("overlap-recover-source-control-failure")
    source_recover.set_defaults(func=command_overlap_recover_source_control_failure)
    gate_dispose = sub.add_parser("overlap-dispose-invalid-source-control-gate")
    gate_dispose.set_defaults(func=command_dispose_invalid_source_control_gate)
    gate_refresh = sub.add_parser("overlap-refresh-source-control-recovery-gate")
    gate_refresh.set_defaults(func=command_refresh_source_control_recovery_gate)
    post_failure_migration = sub.add_parser("overlap-migrate-source-control-post-failure")
    post_failure_migration.set_defaults(func=command_migrate_source_control_post_failure)
    unlimited_wall_clock = sub.add_parser("overlap-migrate-unlimited-wall-clock")
    unlimited_wall_clock.set_defaults(func=command_migrate_unlimited_wall_clock)
    retire_artifact = sub.add_parser("overlap-retire-source-control-test-artifact")
    retire_artifact.set_defaults(func=command_retire_source_control_test_artifact)
    run = sub.add_parser("run")
    run.add_argument("--bucket", choices=("none", *GPU_LIMITS), required=True)
    run.add_argument("--cpu-bucket", choices=("none", *CPU_LIMITS), default="none")
    run.add_argument("--forecast-bytes", type=int)
    run.add_argument("--overlap-operation", action="store_true")
    run.add_argument(
        "--overlap-action",
        choices=(
            "apt_install",
            "source_prepare",
            "source_build",
            "smoke_prepare",
            "smoke_run",
            "project",
            "batch_prepare",
            "batch_run",
        ),
    )
    run.add_argument("--structure-id")
    run.add_argument("--config")
    run.add_argument("--log")
    run.add_argument("--cwd")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=command_run)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
