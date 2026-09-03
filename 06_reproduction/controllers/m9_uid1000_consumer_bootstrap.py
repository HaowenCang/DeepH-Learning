#!/usr/bin/env python3
"""Root bootstrap for the audited UID1000 consumer installer.

This file is executed only through the work-package single-FD SHA-256 loader.
It copies the frozen bootstrap, installer, adapter, verdict, and audit report
into a root-owned read-only directory before either module is imported.
"""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
from pathlib import Path
import stat
import sys


PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
REPRODUCTION = PROJECT_ROOT / "06_reproduction"
PROJECT_BOOTSTRAP = REPRODUCTION / "controllers/m9_uid1000_consumer_bootstrap.py"
PROJECT_INSTALLER = REPRODUCTION / "controllers/m9_uid1000_consumer_install.py"
PROJECT_ADAPTER = REPRODUCTION / "controllers/m9_budget_uid1000_consumer.py"
PROJECT_VERDICT = (
    PROJECT_ROOT
    / "08_audits/M9_source_prepare_py39_consumer_replacement_final_verdict.json"
)
PROJECT_REPORT = (
    PROJECT_ROOT
    / "08_audits/M9_source_prepare_py39_consumer_replacement_independent_audit.md"
)
FROZEN_HASHES = (
    REPRODUCTION
    / "manifests/m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json"
)
TRUSTED_ROOT = Path(
    "/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2-bootstrap"
)
STAGING_ROOT = TRUSTED_ROOT.with_name(TRUSTED_ROOT.name + ".staging")
TRUSTED_BOOTSTRAP = TRUSTED_ROOT / PROJECT_BOOTSTRAP.name
TRUSTED_INSTALLER = TRUSTED_ROOT / PROJECT_INSTALLER.name
TRUSTED_ADAPTER = TRUSTED_ROOT / PROJECT_ADAPTER.name
TRUSTED_VERDICT = TRUSTED_ROOT / PROJECT_VERDICT.name
TRUSTED_REPORT = TRUSTED_ROOT / PROJECT_REPORT.name
TRUSTED_RECEIPT = TRUSTED_ROOT / "bootstrap_receipt.json"
FROZEN_PYTHON = Path("/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9")
LOCK_PATH = Path("/home/evan-williams/deeph-m9/manifests/budget.lock")
RECOVERY_GATE = Path("/root/deeph-m9-control/source-prepare-py39-recovery-gate.json")
RECOVERY_TRANSACTION = Path(
    "/root/deeph-m9-control/source-prepare-py39-recovery-transaction.json"
)
RECOVERY_FAILURE_SNAPSHOT = Path(
    "/root/deeph-m9-control/source-prepare-py39-failure-transaction.json"
)
EXPECTED_RECOVERY_GATE_SHA256 = (
    "6a887aafc84ec6bbb558423159faac86f971265497ea79d5d9bd147a8263b73d"
)
EXPECTED_RECOVERY_TRANSACTION_SHA256 = (
    "75daebc349615fb9599120002f2df11a8acd01e630aa6a703cc9fe5aad1a6a8b"
)
EXPECTED_FAILURE_SHA256 = (
    "0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7"
)
FORBIDDEN_INSTALL_PATHS = (
    Path("/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2"),
    Path("/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_uid1000_consumer_gate.json"),
    Path("/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_single_run_authorization.json"),
    Path("/root/deeph-m9-control/source-prepare-py39-consumer-refresh.json"),
    Path("/home/evan-williams/deeph-m9/manifests/overlap_work_package_audit_gate.pre-py39-recovery.retired.json"),
    Path("/home/evan-williams/deeph-m9/manifests/overlap_work_package_audit_gate.py39-recovery.staging.json"),
)
SOURCE_PRODUCTS = (
    Path("/home/evan-williams/deeph-m9/software/openmx-overlap-src"),
    Path("/home/evan-williams/deeph-m9/software/openmx-overlap-build.staging"),
    Path("/home/evan-williams/deeph-m9/software/openmx-overlap-build"),
    Path("/home/evan-williams/deeph-m9/manifests/openmx_source_receipt.json"),
    Path("/home/evan-williams/deeph-m9/manifests/openmx_build_receipt.json"),
    Path("/home/evan-williams/deeph-m9/manifests/openmx_overlap_source_control_report.json"),
)


def stable_bytes(path: Path, expected_sha256: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"bootstrap source metadata mismatch: {path}")
        payload = bytearray()
        while len(payload) < before.st_size:
            chunk = os.read(descriptor, before.st_size - len(payload))
            if not chunk:
                raise SystemExit(f"bootstrap source read was short: {path}")
            payload.extend(chunk)
        after = os.fstat(descriptor)
        linked = os.lstat(path)
        fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if (
            any(getattr(before, key) != getattr(after, key) for key in fields)
            or any(getattr(after, key) != getattr(linked, key) for key in fields)
            or stat.S_ISLNK(linked.st_mode)
            or hashlib.sha256(payload).hexdigest() != expected_sha256
        ):
            raise SystemExit(f"bootstrap source changed or hash mismatched: {path}")
        return bytes(payload)
    finally:
        os.close(descriptor)


def full_inode_receipt(path: Path) -> tuple[dict[str, object], bytes]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"bootstrap preflight object metadata mismatch: {path}")
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
            raise SystemExit(f"bootstrap preflight object changed: {path}")
    finally:
        os.close(descriptor)
    return ({
        "path": path.as_posix(), "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload), "uid": after.st_uid, "gid": after.st_gid,
        "mode": stat.S_IMODE(after.st_mode), "nlink": after.st_nlink,
        "st_dev": int(after.st_dev), "st_ino": int(after.st_ino),
    }, payload)


def verify_bootstrap_runtime(lock_handle: object) -> dict[str, object]:
    """Verify the recovered runtime before any trust-root staging write."""
    lock_receipt, lock_payload = full_inode_receipt(LOCK_PATH)
    opened = os.fstat(lock_handle.fileno())  # type: ignore[attr-defined]
    if (
        lock_payload != b""
        or (opened.st_dev, opened.st_ino) != (lock_receipt["st_dev"], lock_receipt["st_ino"])
    ):
        raise SystemExit("bootstrap budget lock identity mismatch")
    gate_receipt, gate_payload = full_inode_receipt(RECOVERY_GATE)
    transaction_receipt, transaction_payload = full_inode_receipt(RECOVERY_TRANSACTION)
    failure_receipt, failure_payload = full_inode_receipt(RECOVERY_FAILURE_SNAPSHOT)
    if (
        gate_receipt.get("sha256") != EXPECTED_RECOVERY_GATE_SHA256
        or transaction_receipt.get("sha256") != EXPECTED_RECOVERY_TRANSACTION_SHA256
        or failure_receipt.get("sha256") != EXPECTED_FAILURE_SHA256
        or any(
            receipt.get("uid") != 0 or receipt.get("gid") != 0
            or receipt.get("mode") != 0o600 or receipt.get("nlink") != 1
            for receipt in (gate_receipt, transaction_receipt, failure_receipt)
        )
    ):
        raise SystemExit("bootstrap fixed recovery receipt mismatch")
    gate = json.loads(gate_payload.decode("utf-8"))
    transaction = json.loads(transaction_payload.decode("utf-8"))
    if (
        transaction.get("schema_version")
        != "m9-source-prepare-py39-recovery-transaction-v1"
        or transaction.get("state") != "SUCCESS_COMMITTED"
        or transaction.get("gate") != gate_receipt
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
        or not isinstance(transaction.get("pre_runtime"), dict)
        or transaction["pre_runtime"].get("lock") != lock_receipt
    ):
        raise SystemExit("bootstrap recovery transaction binding mismatch")
    current: dict[str, object] = {}
    payloads: dict[str, bytes] = {}
    for name, expected in (
        ("state", transaction["post_state"]),
        ("workflow", transaction["post_workflow"]),
        ("ledger", transaction["post_ledger"]),
    ):
        receipt, payload = full_inode_receipt(Path(str(expected["path"])))
        if receipt != expected:
            raise SystemExit(f"bootstrap recovered post-{name} drift")
        current[name] = receipt; payloads[name] = payload
    for name, expected in transaction["pre_runtime"].items():
        if name in {"lock", "state", "workflow", "ledger"}:
            continue
        receipt, payload = full_inode_receipt(Path(str(expected["path"])))
        if receipt != expected:
            raise SystemExit(f"bootstrap immutable recovery drift: {name}")
        current[name] = receipt; payloads[name] = payload
    if payloads["failure_transaction"] != failure_payload:
        raise SystemExit("bootstrap failure snapshot mismatch")
    state = json.loads(payloads["state"].decode("utf-8"))
    workflow = json.loads(payloads["workflow"].decode("utf-8"))
    if (
        state.get("wall_clock_policy", {}).get("mode") != "UNLIMITED"
        or state.get("hard_stopped")
        or state.get("active_overlap_transaction") is not None
        or workflow.get("stage") != "AUDIT_PASSED"
        or workflow.get("hard_stopped")
        or workflow.get("active_transaction") is not None
        or any(os.path.lexists(path) for path in SOURCE_PRODUCTS)
        or any(os.path.lexists(path) for path in FORBIDDEN_INSTALL_PATHS)
    ):
        raise SystemExit("bootstrap recovered runtime semantics or namespace mismatch")
    return {
        "lock": lock_receipt, "gate": gate_receipt,
        "transaction": transaction_receipt, "failure": failure_receipt,
        "current": current,
    }


def durable_member(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o440)
    except FileExistsError:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            current = os.fstat(descriptor)
            existing = os.read(descriptor, current.st_size + 1)
        finally:
            os.close(descriptor)
        if (
            not stat.S_ISREG(current.st_mode)
            or current.st_uid != 0
            or current.st_gid != 1000
            or stat.S_IMODE(current.st_mode) != 0o440
            or current.st_nlink != 1
            or existing != payload
        ):
            raise SystemExit(f"bootstrap staging member differs: {path}")
        return
    try:
        os.fchown(descriptor, 0, 1000)
        os.fchmod(descriptor, 0o440)
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("bootstrap member write was short")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def trusted_member(path: Path, expected_sha256: str) -> dict[str, object]:
    payload = stable_bytes(path, expected_sha256)
    observed = os.lstat(path)
    if (
        observed.st_uid != 0
        or observed.st_gid != 1000
        or stat.S_IMODE(observed.st_mode) != 0o440
        or observed.st_nlink != 1
    ):
        raise SystemExit(f"trusted bootstrap member metadata mismatch: {path}")
    return {"sha256": expected_sha256, "bytes": len(payload)}


def verify_tree(
    root: Path, expected: dict[Path, str], frozen_sha256: str
) -> dict[str, object]:
    root_stat = os.lstat(root)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("trusted bootstrap tree metadata mismatch")
    expected_names = {path.name for path in expected} | {TRUSTED_RECEIPT.name}
    if {path.name for path in root.iterdir()} != expected_names:
        raise SystemExit("trusted bootstrap directory is not closed")
    members = {
        destination.as_posix(): trusted_member(root / destination.name, digest)
        for destination, digest in expected.items()
    }
    expected_receipt = {
        "schema_version": "m9-source-prepare-py39-consumer-bootstrap-v1",
        "decision_id": "D-018",
        "frozen_hashes_sha256": frozen_sha256,
        "members": members,
    }
    expected_receipt_payload = (
        json.dumps(expected_receipt, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    receipt_payload = stable_bytes(
        root / TRUSTED_RECEIPT.name,
        hashlib.sha256(expected_receipt_payload).hexdigest(),
    )
    receipt = json.loads(receipt_payload.decode("utf-8"))
    if (
        receipt.get("schema_version")
        != "m9-source-prepare-py39-consumer-bootstrap-v1"
        or receipt.get("decision_id") != "D-018"
        or receipt.get("frozen_hashes_sha256") != frozen_sha256
        or receipt != expected_receipt
    ):
        raise SystemExit("trusted bootstrap receipt mismatch")
    return receipt


def verify_installed(expected: dict[Path, str], frozen_sha256: str) -> dict[str, object]:
    return verify_tree(TRUSTED_ROOT, expected, frozen_sha256)


def _install_trust_root() -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("consumer bootstrap requires root")
    if (
        Path(sys.executable).resolve(strict=True) != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or len(sys.argv) != 7
    ):
        raise SystemExit("consumer bootstrap requires frozen Python -I -S -B and six hashes")
    bootstrap_sha, installer_sha, adapter_sha, frozen_sha, verdict_sha, report_sha = (
        sys.argv[1:]
    )
    expected_hashes = {
        PROJECT_BOOTSTRAP: bootstrap_sha,
        PROJECT_INSTALLER: installer_sha,
        PROJECT_ADAPTER: adapter_sha,
        PROJECT_VERDICT: verdict_sha,
        PROJECT_REPORT: report_sha,
    }
    frozen_payload = stable_bytes(FROZEN_HASHES, frozen_sha)
    frozen = json.loads(frozen_payload.decode("utf-8"))
    files = frozen.get("files")
    frozen_sources = {PROJECT_BOOTSTRAP, PROJECT_INSTALLER, PROJECT_ADAPTER}
    if not isinstance(files, dict) or any(
        files.get(path.as_posix()) != expected_hashes[path] for path in frozen_sources
    ):
        raise SystemExit("consumer bootstrap arguments are not frozen-manifest bound")
    payloads = {path: stable_bytes(path, digest) for path, digest in expected_hashes.items()}
    destination_hashes = {
        TRUSTED_BOOTSTRAP: bootstrap_sha,
        TRUSTED_INSTALLER: installer_sha,
        TRUSTED_ADAPTER: adapter_sha,
        TRUSTED_VERDICT: verdict_sha,
        TRUSTED_REPORT: report_sha,
    }

    parent = TRUSTED_ROOT.parent
    if not parent.exists():
        parent.mkdir(parents=True, mode=0o750)
        os.chown(parent, 0, 1000)
        os.chmod(parent, 0o750)
    parent_stat = os.lstat(parent)
    if (
        parent_stat.st_uid != 0
        or parent_stat.st_gid != 1000
        or stat.S_IMODE(parent_stat.st_mode) != 0o750
    ):
        raise SystemExit("consumer controls parent metadata mismatch")
    if os.path.lexists(TRUSTED_ROOT):
        receipt = verify_installed(destination_hashes, frozen_sha)
        print(json.dumps({"status": "consumer_bootstrap_exists", "receipt": receipt}, sort_keys=True))
        return 0

    if not os.path.lexists(STAGING_ROOT):
        STAGING_ROOT.mkdir(mode=0o700)
        os.chown(STAGING_ROOT, 0, 1000)
        os.chmod(STAGING_ROOT, 0o700)
    staging_stat = os.lstat(STAGING_ROOT)
    if (
        stat.S_ISDIR(staging_stat.st_mode)
        and staging_stat.st_uid == 0
        and staging_stat.st_gid == 1000
        and stat.S_IMODE(staging_stat.st_mode) == 0o550
    ):
        verify_tree(STAGING_ROOT, destination_hashes, frozen_sha)
        os.replace(STAGING_ROOT, TRUSTED_ROOT)
        parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        receipt = verify_installed(destination_hashes, frozen_sha)
        print(json.dumps({"status": "consumer_bootstrap_resumed", "receipt": receipt}, sort_keys=True))
        return 0
    if (
        not stat.S_ISDIR(staging_stat.st_mode)
        or staging_stat.st_uid != 0
        or staging_stat.st_gid != 1000
        or stat.S_IMODE(staging_stat.st_mode) != 0o700
    ):
        raise SystemExit("consumer bootstrap staging metadata mismatch")
    source_to_destination = {
        PROJECT_BOOTSTRAP: STAGING_ROOT / TRUSTED_BOOTSTRAP.name,
        PROJECT_INSTALLER: STAGING_ROOT / TRUSTED_INSTALLER.name,
        PROJECT_ADAPTER: STAGING_ROOT / TRUSTED_ADAPTER.name,
        PROJECT_VERDICT: STAGING_ROOT / TRUSTED_VERDICT.name,
        PROJECT_REPORT: STAGING_ROOT / TRUSTED_REPORT.name,
    }
    members: dict[str, object] = {}
    for source, target in source_to_destination.items():
        durable_member(target, payloads[source])
        digest = expected_hashes[source]
        members[(TRUSTED_ROOT / target.name).as_posix()] = {
            "sha256": digest, "bytes": len(payloads[source])
        }
    receipt = {
        "schema_version": "m9-source-prepare-py39-consumer-bootstrap-v1",
        "decision_id": "D-018",
        "frozen_hashes_sha256": frozen_sha,
        "members": members,
    }
    receipt_payload = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode()
    durable_member(STAGING_ROOT / TRUSTED_RECEIPT.name, receipt_payload)
    expected_names = {path.name for path in source_to_destination.values()} | {
        TRUSTED_RECEIPT.name
    }
    if {path.name for path in STAGING_ROOT.iterdir()} != expected_names:
        raise SystemExit("consumer bootstrap staging directory is not closed")
    os.chmod(STAGING_ROOT, 0o550)
    descriptor = os.open(STAGING_ROOT, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(STAGING_ROOT, TRUSTED_ROOT)
    parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)
    verify_installed(destination_hashes, frozen_sha)
    print(json.dumps({"status": "consumer_bootstrap_installed", "receipt": receipt}, sort_keys=True))
    return 0


def main() -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("consumer bootstrap requires root")
    if (
        Path(sys.executable).resolve(strict=True) != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or len(sys.argv) != 7
    ):
        raise SystemExit("consumer bootstrap requires frozen Python -I -S -B and six hashes")
    flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(LOCK_PATH, flags)
    with os.fdopen(descriptor, "r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        preflight = verify_bootstrap_runtime(lock_handle)
        result = _install_trust_root()
        if verify_bootstrap_runtime(lock_handle) != preflight:
            raise SystemExit("bootstrap runtime drift after trust-root installation")
        return result


if __name__ == "__main__":
    raise SystemExit(main())
