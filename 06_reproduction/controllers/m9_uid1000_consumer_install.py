#!/usr/bin/env python3
"""Root-only durable installer for the audited UID1000 consumer snapshot/gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import fcntl
import stat
import sys
import types


PROJECT_ADAPTER = Path(
    "/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/"
    "m9_budget_uid1000_consumer.py"
)
TRUSTED_BOOTSTRAP_ROOT = Path(
    "/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2-bootstrap"
)
TRUSTED_INSTALLER = TRUSTED_BOOTSTRAP_ROOT / "m9_uid1000_consumer_install.py"
TRUSTED_ADAPTER = TRUSTED_BOOTSTRAP_ROOT / "m9_budget_uid1000_consumer.py"
TRUSTED_BOOTSTRAP = TRUSTED_BOOTSTRAP_ROOT / "m9_uid1000_consumer_bootstrap.py"
TRUSTED_VERDICT = (
    TRUSTED_BOOTSTRAP_ROOT
    / "M9_source_prepare_py39_consumer_replacement_final_verdict.json"
)
TRUSTED_REPORT = (
    TRUSTED_BOOTSTRAP_ROOT
    / "M9_source_prepare_py39_consumer_replacement_independent_audit.md"
)
TRUSTED_RECEIPT = TRUSTED_BOOTSTRAP_ROOT / "bootstrap_receipt.json"
RUNNING_INSTALLER = Path(__file__).resolve(strict=True)
if (
    __name__ == "__main__"
    and RUNNING_INSTALLER != TRUSTED_INSTALLER.resolve(strict=False)
):
    raise SystemExit("consumer installer must run from the trusted bootstrap")
ADAPTER_IMPORT = (
    TRUSTED_ADAPTER
    if RUNNING_INSTALLER == TRUSTED_INSTALLER.resolve(strict=False)
    else PROJECT_ADAPTER
)
specification = importlib.util.spec_from_file_location("m9_uid1000_consumer", ADAPTER_IMPORT)
if specification is None or specification.loader is None:
    raise RuntimeError("cannot load consumer adapter")
consumer = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = consumer
specification.loader.exec_module(consumer)


STAGING_ROOT = consumer.SNAPSHOT_ROOT.with_name(consumer.SNAPSHOT_ROOT.name + ".staging")
FROZEN_PYTHON = Path("/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9")
REFRESH_JOURNAL = Path(
    "/root/deeph-m9-control/source-prepare-py39-consumer-refresh.json"
)
ACTIVE_GATE_RETIRED = consumer.MANIFESTS / (
    "overlap_work_package_audit_gate.pre-py39-recovery.retired.json"
)
ACTIVE_GATE_STAGING = consumer.MANIFESTS / (
    "overlap_work_package_audit_gate.py39-recovery.staging.json"
)
RECOVERY_GATE = Path(
    "/root/deeph-m9-control/source-prepare-py39-recovery-gate.json"
)
RECOVERY_TRANSACTION = Path(
    "/root/deeph-m9-control/source-prepare-py39-recovery-transaction.json"
)
RECOVERY_FAILURE_SNAPSHOT = Path(
    "/root/deeph-m9-control/source-prepare-py39-failure-transaction.json"
)
PRE_REPLACEMENT_ACTIVE_GATE_SHA256 = (
    "78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698"
)
FAILURE_TRANSACTION_SHA256 = (
    "0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7"
)


def verify_trusted_bootstrap(frozen_payload: bytes) -> tuple[str, bytes, bytes]:
    root_stat = os.lstat(TRUSTED_BOOTSTRAP_ROOT)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("trusted consumer bootstrap root metadata mismatch")
    members = {
        TRUSTED_BOOTSTRAP, TRUSTED_INSTALLER, TRUSTED_ADAPTER,
        TRUSTED_VERDICT, TRUSTED_REPORT, TRUSTED_RECEIPT,
    }
    if set(TRUSTED_BOOTSTRAP_ROOT.iterdir()) != members:
        raise SystemExit("trusted consumer bootstrap directory is not closed")
    frozen_sha = hashlib.sha256(frozen_payload).hexdigest()
    frozen = json.loads(frozen_payload.decode("utf-8"))
    files = frozen.get("files")
    source_mapping = {
        TRUSTED_BOOTSTRAP: consumer.REPRODUCTION / "controllers/m9_uid1000_consumer_bootstrap.py",
        TRUSTED_INSTALLER: consumer.REPRODUCTION / "controllers/m9_uid1000_consumer_install.py",
        TRUSTED_ADAPTER: consumer.PROJECT_ADAPTER,
        TRUSTED_VERDICT: consumer.CONSUMER_VERDICT,
        TRUSTED_REPORT: consumer.CONSUMER_REPORT,
    }
    expected_members: dict[str, object] = {}
    trusted_payloads: dict[Path, bytes] = {}
    for trusted, source in source_mapping.items():
        payload = stable_source_bytes(trusted)
        trusted_payloads[trusted] = payload
        observed = os.lstat(trusted)
        expected_sha = (
            files.get(source.as_posix())
            if isinstance(files, dict) and trusted not in {TRUSTED_VERDICT, TRUSTED_REPORT}
            else hashlib.sha256(payload).hexdigest()
        )
        if (
            observed.st_uid != 0
            or observed.st_gid != 1000
            or stat.S_IMODE(observed.st_mode) != 0o440
            or observed.st_nlink != 1
            or hashlib.sha256(payload).hexdigest() != expected_sha
        ):
            raise SystemExit(f"trusted consumer bootstrap member mismatch: {trusted}")
        expected_members[trusted.as_posix()] = {
            "sha256": expected_sha, "bytes": len(payload)
        }
    receipt_payload = stable_source_bytes(TRUSTED_RECEIPT)
    receipt_stat = os.lstat(TRUSTED_RECEIPT)
    receipt = json.loads(receipt_payload.decode("utf-8"))
    if (
        receipt_stat.st_uid != 0
        or receipt_stat.st_gid != 1000
        or stat.S_IMODE(receipt_stat.st_mode) != 0o440
        or receipt_stat.st_nlink != 1
        or receipt
        != {
            "schema_version": "m9-source-prepare-py39-consumer-bootstrap-v1",
            "decision_id": "D-018",
            "frozen_hashes_sha256": frozen_sha,
            "members": expected_members,
        }
    ):
        raise SystemExit("trusted consumer bootstrap receipt mismatch")
    return frozen_sha, trusted_payloads[TRUSTED_VERDICT], trusted_payloads[TRUSTED_REPORT]


def stable_source_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"consumer source is not a single-link regular file: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if any(getattr(before, key) != getattr(after, key) for key in stable):
            raise SystemExit(f"consumer source changed during read: {path}")
        payload = b"".join(chunks)
        if len(payload) != after.st_size:
            raise SystemExit(f"consumer source read was incomplete: {path}")
        return payload
    finally:
        os.close(descriptor)


def snapshot_name(source: Path, index: int) -> str:
    if source == consumer.PROJECT_ADAPTER:
        return "m9_budget_uid1000_consumer.py"
    if source == consumer.PROJECT_ORIGINAL_CONTROLLER:
        return "m9_budget.py"
    return f"{index:02d}-{source.name}"


def durable_snapshot_file(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o440)
    except FileExistsError:
        receipt, existing = consumer.read_snapshot_regular(path)
        if existing != payload or receipt["sha256"] != hashlib.sha256(payload).hexdigest():
            raise SystemExit(f"consumer staging member differs: {path}")
        return
    try:
        os.fchown(descriptor, 0, 1000)
        os.fchmod(descriptor, 0o440)
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("consumer snapshot write was short")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def verify_authorized_sources(
    expected_frozen_sha256: str,
    trusted_verdict_bytes: bytes,
    trusted_report_bytes: bytes,
) -> dict[Path, bytes]:
    frozen_bytes = stable_source_bytes(consumer.CONSUMER_FROZEN_HASHES)
    if hashlib.sha256(frozen_bytes).hexdigest() != expected_frozen_sha256:
        raise SystemExit("consumer frozen manifest differs from trusted bootstrap")
    frozen = json.loads(frozen_bytes.decode("utf-8"))
    files = frozen.get("files")
    if (
        frozen.get("schema_version")
        != "m9-source-prepare-py39-uid1000-consumer-frozen-v1"
        or not isinstance(files, dict)
        or {Path(str(path)).resolve(strict=False) for path in files}
        != {path.resolve(strict=False) for path in consumer.CONSUMER_CONTROL_FILES}
    ):
        raise SystemExit("consumer audit frozen closure mismatch")
    payloads: dict[Path, bytes] = {}
    for source in consumer.CONSUMER_CONTROL_FILES:
        payload = stable_source_bytes(source)
        if hashlib.sha256(payload).hexdigest() != files[source.as_posix()]:
            raise SystemExit(f"consumer audit source hash mismatch: {source}")
        payloads[source] = payload
    payloads[consumer.CONSUMER_FROZEN_HASHES] = frozen_bytes

    verdict_bytes = trusted_verdict_bytes
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    report_bytes = trusted_report_bytes
    work_bytes = payloads[consumer.CONSUMER_WORK_PACKAGE]
    if (
        verdict.get("schema_version")
        != "m9-source-prepare-py39-consumer-replacement-verdict-v1"
        or verdict.get("decision_id") != "D-018-PY39-CONSUMER-REPLACEMENT"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("report_path") != consumer.CONSUMER_REPORT.as_posix()
        or verdict.get("report_sha256") != hashlib.sha256(report_bytes).hexdigest()
        or verdict.get("work_package_path") != consumer.CONSUMER_WORK_PACKAGE.as_posix()
        or verdict.get("work_package_sha256") != hashlib.sha256(work_bytes).hexdigest()
    ):
        raise SystemExit("consumer independent verdict binding mismatch")
    payloads[consumer.CONSUMER_VERDICT] = verdict_bytes
    payloads[consumer.CONSUMER_REPORT] = report_bytes
    return payloads


def load_frozen_original_controller(payload: bytes) -> object:
    """Execute the already hashed controller bytes without a second project-path read."""
    name = "m9_budget_py39_consumer_installer_frozen"
    module = types.ModuleType(name)
    module.__file__ = consumer.PROJECT_ORIGINAL_CONTROLLER.as_posix()
    module.__package__ = ""
    sys.modules[name] = module
    exec(
        compile(payload, consumer.PROJECT_ORIGINAL_CONTROLLER.as_posix(), "exec"),
        module.__dict__,
        module.__dict__,
    )
    return module


def verify_sealed_staging(payloads: dict[Path, bytes]) -> dict[str, object]:
    root_stat = os.lstat(STAGING_ROOT)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("sealed consumer staging metadata mismatch")
    manifest_path = STAGING_ROOT / consumer.SNAPSHOT_MANIFEST.name
    manifest_payload = stable_source_bytes(manifest_path)
    manifest_stat = os.lstat(manifest_path)
    if (
        manifest_stat.st_uid != 0
        or manifest_stat.st_gid != 1000
        or stat.S_IMODE(manifest_stat.st_mode) != 0o440
        or manifest_stat.st_nlink != 1
    ):
        raise SystemExit("sealed consumer staging manifest metadata mismatch")
    manifest = json.loads(manifest_payload.decode("utf-8"))
    files = manifest.get("files")
    if (
        manifest.get("schema_version")
        != "m9-source-prepare-py39-consumer-snapshot-v1"
        or not isinstance(files, dict)
        or set(files) != {path.as_posix() for path in payloads}
    ):
        raise SystemExit("sealed consumer staging manifest closure mismatch")
    expected_names = {manifest_path.name}
    for source, payload in payloads.items():
        entry = files.get(source.as_posix())
        if not isinstance(entry, dict) or set(entry) != {
            "snapshot_path", "sha256", "bytes"
        }:
            raise SystemExit("sealed consumer staging entry mismatch")
        target = Path(str(entry["snapshot_path"]))
        if target.parent != consumer.SNAPSHOT_ROOT:
            raise SystemExit("sealed consumer staging target escaped final root")
        staged = STAGING_ROOT / target.name
        observed = stable_source_bytes(staged)
        staged_stat = os.lstat(staged)
        if (
            staged_stat.st_uid != 0
            or staged_stat.st_gid != 1000
            or stat.S_IMODE(staged_stat.st_mode) != 0o440
            or staged_stat.st_nlink != 1
            or observed != payload
            or entry["sha256"] != hashlib.sha256(payload).hexdigest()
            or int(entry["bytes"]) != len(payload)
        ):
            raise SystemExit("sealed consumer staging member mismatch")
        expected_names.add(staged.name)
    if {path.name for path in STAGING_ROOT.iterdir()} != expected_names:
        raise SystemExit("sealed consumer staging directory is not closed")
    return manifest


def install_snapshot(payloads: dict[Path, bytes]) -> dict[str, object]:
    parent = consumer.SNAPSHOT_ROOT.parent
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
        raise SystemExit("consumer control parent metadata mismatch")
    if os.path.lexists(consumer.SNAPSHOT_ROOT):
        receipt, manifest = consumer.read_snapshot_manifest()
        if set(manifest["files"]) != {path.as_posix() for path in payloads}:
            raise SystemExit("installed consumer snapshot closure mismatch")
        expected_names = {
            Path(str(entry["snapshot_path"])).name
            for entry in manifest["files"].values()
        } | {consumer.SNAPSHOT_MANIFEST.name}
        if {path.name for path in consumer.SNAPSHOT_ROOT.iterdir()} != expected_names:
            raise SystemExit("installed consumer snapshot directory is not closed")
        for source, payload in payloads.items():
            _, observed = consumer.snapshot_source_payload(manifest, source)
            if observed != payload:
                raise SystemExit("installed consumer snapshot source mismatch")
        return {"receipt": receipt, "manifest": manifest}

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
        verify_sealed_staging(payloads)
        os.replace(STAGING_ROOT, consumer.SNAPSHOT_ROOT)
        parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        receipt, installed = consumer.read_snapshot_manifest()
        return {"receipt": receipt, "manifest": installed}
    if (
        staging_stat.st_uid != 0
        or staging_stat.st_gid != 1000
        or stat.S_IMODE(staging_stat.st_mode) != 0o700
    ):
        raise SystemExit("consumer staging root metadata mismatch")
    entries: dict[str, object] = {}
    expected_staging_names = {consumer.SNAPSHOT_MANIFEST.name}
    for index, source in enumerate(sorted(payloads, key=lambda path: path.as_posix())):
        target = STAGING_ROOT / snapshot_name(source, index)
        if target.name in expected_staging_names:
            raise SystemExit("consumer snapshot target collision")
        expected_staging_names.add(target.name)
        durable_snapshot_file(target, payloads[source])
        entries[source.as_posix()] = {
            "snapshot_path": (consumer.SNAPSHOT_ROOT / target.name).as_posix(),
            "sha256": hashlib.sha256(payloads[source]).hexdigest(),
            "bytes": len(payloads[source]),
        }
    manifest = {
        "schema_version": "m9-source-prepare-py39-consumer-snapshot-v1",
        "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
        "issue_id": "M9-SP-PY39-B01",
        "files": entries,
    }
    manifest_payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    durable_snapshot_file(STAGING_ROOT / consumer.SNAPSHOT_MANIFEST.name, manifest_payload)
    if {path.name for path in STAGING_ROOT.iterdir()} != expected_staging_names:
        raise SystemExit("consumer staging directory is not closed")
    os.chmod(STAGING_ROOT, 0o550)
    directory = os.open(STAGING_ROOT, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    os.replace(STAGING_ROOT, consumer.SNAPSHOT_ROOT)
    parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)
    receipt, installed = consumer.read_snapshot_manifest()
    return {"receipt": receipt, "manifest": installed}


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def verify_budget_lock(lock_handle: object) -> dict[str, object]:
    m9 = consumer.original_controller()
    descriptor = lock_handle.fileno()  # type: ignore[attr-defined]
    opened = os.fstat(descriptor)
    linked = os.lstat(m9.LOCK_PATH)
    fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink")
    if (
        any(getattr(opened, key) != getattr(linked, key) for key in fields)
        or not stat.S_ISREG(opened.st_mode)
        or opened.st_uid != 1000
        or opened.st_gid != 1000
        or stat.S_IMODE(opened.st_mode) != 0o644
        or opened.st_nlink != 1
    ):
        raise SystemExit("budget lock identity differs during consumer installation")
    return {
        "path": m9.LOCK_PATH.as_posix(),
        "uid": opened.st_uid,
        "gid": opened.st_gid,
        "mode": stat.S_IMODE(opened.st_mode),
        "nlink": opened.st_nlink,
        "st_dev": opened.st_dev,
        "st_ino": opened.st_ino,
    }


def full_inode_receipt(path: Path) -> tuple[dict[str, object], bytes]:
    """Return a stable receipt in the recovery transaction's st_dev/st_ino form."""
    m9 = consumer.original_controller()
    receipt, payload = m9.read_d018_inode_regular_bytes(path)
    receipt = dict(receipt)
    receipt["st_dev"] = receipt.pop("dev")
    receipt["st_ino"] = receipt.pop("ino")
    return receipt, payload


def verify_recovered_core(lock_handle: object) -> dict[str, object]:
    """Zero-write validation of the recovered immutable/runtime core under one lock."""
    m9 = consumer.original_controller()
    lock_receipt, lock_payload = full_inode_receipt(m9.LOCK_PATH)
    handle_receipt = verify_budget_lock(lock_handle)
    if (
        lock_payload != b""
        or any(
            handle_receipt[key] != lock_receipt[receipt_key]
            for key, receipt_key in (
                ("path", "path"), ("uid", "uid"), ("gid", "gid"),
                ("mode", "mode"), ("nlink", "nlink"),
                ("st_dev", "st_dev"), ("st_ino", "st_ino"),
            )
        )
    ):
        raise SystemExit("budget lock full receipt mismatch during installation preflight")

    recovery_gate_receipt, recovery_gate_payload = full_inode_receipt(RECOVERY_GATE)
    recovery_transaction_receipt, recovery_transaction_payload = full_inode_receipt(
        RECOVERY_TRANSACTION
    )
    failure_snapshot_receipt, failure_snapshot_payload = full_inode_receipt(
        RECOVERY_FAILURE_SNAPSHOT
    )
    if (
        recovery_gate_receipt.get("sha256") != consumer.EXPECTED_RECOVERY_GATE_SHA256
        or recovery_gate_receipt.get("uid") != 0
        or recovery_gate_receipt.get("gid") != 0
        or recovery_gate_receipt.get("mode") != 0o600
        or recovery_transaction_receipt.get("sha256")
        != consumer.EXPECTED_RECOVERY_TRANSACTION_SHA256
        or recovery_transaction_receipt.get("uid") != 0
        or recovery_transaction_receipt.get("gid") != 0
        or recovery_transaction_receipt.get("mode") != 0o600
        or failure_snapshot_receipt.get("sha256") != FAILURE_TRANSACTION_SHA256
        or failure_snapshot_receipt.get("uid") != 0
        or failure_snapshot_receipt.get("gid") != 0
        or failure_snapshot_receipt.get("mode") != 0o600
    ):
        raise SystemExit("fixed Python-3.9 recovery receipt mismatch")
    recovery_gate = json.loads(recovery_gate_payload.decode("utf-8"))
    transaction = json.loads(recovery_transaction_payload.decode("utf-8"))
    transaction_fields = {
        "schema_version", "decision_id", "recovery_id", "failure_transaction_id",
        "gate", "python_bootstrap", "pre_runtime", "staging_inventory",
        "retired_path", "recovery_utc", "state", "post_state", "post_workflow",
        "post_ledger", "ledger_event", "retired_inventory",
    }
    pre_runtime_fields = {
        "lock", "state", "workflow", "ledger", "failure_transaction",
        "consumed_capability", "launcher_receipt", "consumer_gate",
        "bootstrap_receipt", "snapshot_manifest", "d017_transaction", "d017_gate",
        "active_overlap_gate", "retired_overlap_gate", "d018_gate",
        "d018_transaction", "d018_execution_gate", "d018_journal", "d018_pre_state",
    }
    if (
        not isinstance(transaction, dict)
        or set(transaction) != transaction_fields
        or transaction.get("schema_version")
        != "m9-source-prepare-py39-recovery-transaction-v1"
        or transaction.get("decision_id") != "D-018"
        or transaction.get("state") != "SUCCESS_COMMITTED"
        or not isinstance(transaction.get("pre_runtime"), dict)
        or set(transaction["pre_runtime"]) != pre_runtime_fields
        or transaction.get("gate") != recovery_gate_receipt
        or recovery_gate.get("status") != "PASS"
        or int(recovery_gate.get("blocking", -1)) != 0
        or int(recovery_gate.get("non_blocking", -1)) != 0
    ):
        raise SystemExit("Python-3.9 recovery transaction closure mismatch")
    if transaction["pre_runtime"]["lock"] != lock_receipt:
        raise SystemExit("budget lock differs from the recovered transaction")

    current_receipts: dict[str, object] = {}
    current_payloads: dict[str, bytes] = {}
    for name, source_receipt in (
        ("state", transaction["post_state"]),
        ("workflow", transaction["post_workflow"]),
        ("ledger", transaction["post_ledger"]),
    ):
        path = Path(str(source_receipt["path"]))
        receipt, payload = full_inode_receipt(path)
        if receipt != source_receipt:
            raise SystemExit(f"recovered post-{name} receipt drift")
        current_receipts[name] = receipt
        current_payloads[name] = payload

    immutable_pre_runtime = pre_runtime_fields - {
        "lock", "state", "workflow", "ledger", "active_overlap_gate"
    }
    for name in sorted(immutable_pre_runtime):
        source_receipt = transaction["pre_runtime"][name]
        receipt, payload = full_inode_receipt(Path(str(source_receipt["path"])))
        if receipt != source_receipt:
            raise SystemExit(f"recovered immutable receipt drift: {name}")
        current_receipts[name] = receipt
        current_payloads[name] = payload
    if current_payloads["failure_transaction"] != failure_snapshot_payload:
        raise SystemExit("failure snapshot differs from the immutable failure transaction")

    state = json.loads(current_payloads["state"].decode("utf-8"))
    workflow = json.loads(current_payloads["workflow"].decode("utf-8"))
    if (
        m9.wall_clock_policy_mode(state) != "UNLIMITED"
        or state.get("hard_stopped")
        or state.get("active_overlap_transaction") is not None
        or workflow.get("stage") != "AUDIT_PASSED"
        or workflow.get("hard_stopped")
        or workflow.get("active_transaction") is not None
        or any(os.path.lexists(path) for path in m9.SOURCE_RECOVERY_PRODUCTS)
    ):
        raise SystemExit("recovered runtime semantics mismatch")
    result = {
        "lock": lock_receipt,
        "recovery_gate": recovery_gate_receipt,
        "recovery_transaction": recovery_transaction_receipt,
        "failure_snapshot": failure_snapshot_receipt,
        "pre_replacement_active_gate": transaction["pre_runtime"][
            "active_overlap_gate"
        ],
        "current": current_receipts,
    }
    return result


def replacement_active_gate(snapshot: dict[str, object]) -> dict[str, object]:
    verdict_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_VERDICT
    )
    frozen_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.OVERLAP_RUNTIME_FROZEN_HASHES
    )
    work_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_WORK_PACKAGE
    )
    fact_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.RECOVERY_FACT_REPORT
    )
    return {
        "schema_version": "m9-overlap-audit-gate-v1",
        "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "work_package_path": consumer.CONSUMER_WORK_PACKAGE.as_posix(),
        "work_package_sha256": work_receipt["sha256"],
        "audit_report_path": consumer.CONSUMER_VERDICT.as_posix(),
        "audit_report_sha256": verdict_receipt["sha256"],
        "authorization_record_path": consumer.RECOVERY_FACT_REPORT.as_posix(),
        "authorization_record_sha256": fact_receipt["sha256"],
        "frozen_hashes_path": consumer.OVERLAP_RUNTIME_FROZEN_HASHES.as_posix(),
        "frozen_hashes_sha256": frozen_receipt["sha256"],
    }


def read_inode_gate(path: Path, expected_sha256: str) -> tuple[dict[str, object], dict]:
    m9 = consumer.original_controller()
    receipt, payload = m9.read_d018_inode_regular_bytes(path)
    if (
        receipt.get("sha256") != expected_sha256
        or receipt.get("uid") != 0
        or receipt.get("gid") != 1000
        or receipt.get("mode") != 0o640
        or receipt.get("nlink") != 1
    ):
        raise SystemExit(f"active-gate inode receipt mismatch: {path}")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"active-gate JSON mismatch: {path}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"active-gate JSON must be an object: {path}")
    return receipt, value


def require_inode_receipt(
    path: Path, expected_sha256: str, inherited: dict[str, object] | None = None
) -> dict[str, object]:
    receipt, _ = read_inode_gate(path, expected_sha256)
    if inherited is not None:
        wanted = dict(inherited, path=path.as_posix())
        if receipt != wanted:
            raise SystemExit(f"active-gate inherited inode receipt mismatch: {path}")
    return receipt


def replacement_active_gate_payload(
    snapshot: dict[str, object],
) -> tuple[dict[str, object], bytes, str]:
    gate = replacement_active_gate(snapshot)
    payload = (json.dumps(gate, ensure_ascii=False, indent=2) + "\n").encode()
    return gate, payload, hashlib.sha256(payload).hexdigest()


def refresh_phase_fields() -> dict[str, set[str]]:
    base = {
        "schema_version", "decision_id", "state", "old_active",
        "old_active_sha256", "new_active_sha256", "retired_path",
        "staging_path", "budget_lock",
    }
    return {
        "PREPARED": base,
        "STAGED": base | {"staging"},
        "OLD_RETIRED": base | {"staging", "retired"},
        "ACTIVE_REPLACED": base | {"retired", "active"},
        "SUCCESS_COMMITTED": base | {"retired", "active"},
    }


def journal_inode_receipt(receipt: dict[str, object]) -> dict[str, object]:
    converted = dict(receipt)
    converted["dev"] = converted.pop("st_dev")
    converted["ino"] = converted.pop("st_ino")
    return converted


def read_bound_refresh_journal(
    snapshot: dict[str, object],
    lock_handle: object,
    recovered_core: dict[str, object],
) -> tuple[dict[str, object] | None, str]:
    """Read and bind an existing refresh journal without writing any namespace."""
    _, _, new_sha = replacement_active_gate_payload(snapshot)
    if not os.path.lexists(REFRESH_JOURNAL):
        return None, new_sha
    m9 = consumer.original_controller()
    _, journal_bytes = m9.read_strict_root_private_bytes(REFRESH_JOURNAL)
    try:
        journal = json.loads(journal_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("active-gate refresh journal JSON mismatch") from exc
    if not isinstance(journal, dict):
        raise SystemExit("active-gate refresh journal must be an object")
    state = str(journal.get("state"))
    phase_fields = refresh_phase_fields()
    old_active = journal_inode_receipt(
        dict(recovered_core["pre_replacement_active_gate"])
    )
    if (
        state not in phase_fields
        or set(journal) != phase_fields[state]
        or journal.get("schema_version")
        != "m9-source-prepare-py39-consumer-refresh-v1"
        or journal.get("decision_id")
        != "D-018-PY39-CONSUMER-REPLACEMENT"
        or journal.get("old_active") != old_active
        or journal.get("old_active_sha256")
        != PRE_REPLACEMENT_ACTIVE_GATE_SHA256
        or journal.get("new_active_sha256") != new_sha
        or journal.get("retired_path") != ACTIVE_GATE_RETIRED.as_posix()
        or journal.get("staging_path") != ACTIVE_GATE_STAGING.as_posix()
        or journal.get("budget_lock") != verify_budget_lock(lock_handle)
    ):
        raise SystemExit("active-gate refresh journal binding mismatch")
    return journal, new_sha


def validate_refresh_namespace(
    journal: dict[str, object], new_sha: str
) -> dict[str, object]:
    """Accept only the two rename windows and the documented committed phases."""
    m9 = consumer.original_controller()
    state = str(journal["state"])
    active_exists = os.path.lexists(m9.OVERLAP_AUDIT_GATE)
    retired_exists = os.path.lexists(ACTIVE_GATE_RETIRED)
    staging_exists = os.path.lexists(ACTIVE_GATE_STAGING)
    active: dict[str, object] | None = None
    retired: dict[str, object] | None = None

    if state == "PREPARED":
        if not active_exists or retired_exists:
            raise SystemExit("PREPARED active-gate phase/path mismatch")
        active = require_inode_receipt(
            m9.OVERLAP_AUDIT_GATE,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["old_active"],
        )
        if staging_exists:
            require_inode_receipt(ACTIVE_GATE_STAGING, new_sha)
    elif state == "STAGED":
        if not staging_exists:
            raise SystemExit("STAGED replacement staging is missing")
        require_inode_receipt(
            ACTIVE_GATE_STAGING, new_sha, journal["staging"]
        )
        if active_exists and not retired_exists:
            active = require_inode_receipt(
                m9.OVERLAP_AUDIT_GATE,
                PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
                journal["old_active"],
            )
        elif not active_exists and retired_exists:
            retired = require_inode_receipt(
                ACTIVE_GATE_RETIRED,
                PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
                journal["old_active"],
            )
        else:
            raise SystemExit("STAGED active-gate phase/path mismatch")
    elif state == "OLD_RETIRED":
        if not retired_exists:
            raise SystemExit("OLD_RETIRED retired gate is missing")
        retired = require_inode_receipt(
            ACTIVE_GATE_RETIRED,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["retired"],
        )
        if not active_exists and staging_exists:
            require_inode_receipt(
                ACTIVE_GATE_STAGING, new_sha, journal["staging"]
            )
        elif active_exists and not staging_exists:
            active = require_inode_receipt(
                m9.OVERLAP_AUDIT_GATE, new_sha, journal["staging"]
            )
        else:
            raise SystemExit("OLD_RETIRED active-gate phase/path mismatch")
    elif state in {"ACTIVE_REPLACED", "SUCCESS_COMMITTED"}:
        if not active_exists or not retired_exists or staging_exists:
            raise SystemExit(f"{state} active-gate phase/path mismatch")
        active = require_inode_receipt(
            m9.OVERLAP_AUDIT_GATE, new_sha, journal["active"]
        )
        retired = require_inode_receipt(
            ACTIVE_GATE_RETIRED,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["retired"],
        )
    else:
        raise SystemExit("unsupported active-gate refresh state")
    return {"state": state, "active": active, "retired": retired}


def verify_installation_preflight(
    lock_handle: object,
    *,
    expected: dict[str, object] | None = None,
    snapshot: dict[str, object] | None = None,
    refresh: dict[str, object] | None = None,
) -> dict[str, object]:
    """Validate the recovered core plus pristine or resumable active-gate state."""
    core = verify_recovered_core(lock_handle)
    m9 = consumer.original_controller()
    if snapshot is None:
        if os.path.lexists(REFRESH_JOURNAL):
            raise SystemExit("refresh journal requires the sealed replacement snapshot")
        if os.path.lexists(ACTIVE_GATE_RETIRED) or os.path.lexists(ACTIVE_GATE_STAGING):
            raise SystemExit("active-gate refresh namespace is not pristine")
        active_receipt, _ = full_inode_receipt(m9.OVERLAP_AUDIT_GATE)
        if active_receipt != core["pre_replacement_active_gate"]:
            raise SystemExit("pre-replacement active gate inode drift")
    else:
        journal, new_sha = read_bound_refresh_journal(snapshot, lock_handle, core)
        if journal is None:
            if os.path.lexists(ACTIVE_GATE_RETIRED) or os.path.lexists(ACTIVE_GATE_STAGING):
                raise SystemExit("active-gate refresh namespace is not pristine")
            active_receipt, _ = full_inode_receipt(m9.OVERLAP_AUDIT_GATE)
            if active_receipt != core["pre_replacement_active_gate"]:
                raise SystemExit("pre-replacement active gate inode drift")
            if refresh is not None:
                raise SystemExit("terminal refresh receipt supplied before refresh")
        else:
            observed = validate_refresh_namespace(journal, new_sha)
            if refresh is not None and (
                journal.get("state") != "SUCCESS_COMMITTED"
                or refresh.get("journal") != journal
                or refresh.get("active") != observed["active"]
                or refresh.get("retired") != observed["retired"]
            ):
                raise SystemExit("terminal refresh receipt mismatch")
    if expected is not None and core != expected:
        raise SystemExit("immutable installation preflight receipt drift")
    return core


def prepare_snapshot_for_refresh(
    payloads: dict[Path, bytes], lock_handle: object
) -> tuple[dict[str, object], dict[str, object]]:
    """Choose pristine installation or a read-only journal-bound restart path."""
    if os.path.lexists(REFRESH_JOURNAL):
        core = verify_recovered_core(lock_handle)
        if not os.path.lexists(consumer.SNAPSHOT_ROOT):
            raise SystemExit("refresh journal exists without the sealed replacement snapshot")
        snapshot = install_snapshot(payloads)
        verify_installation_preflight(
            lock_handle, expected=core, snapshot=snapshot
        )
        return core, snapshot
    core = verify_installation_preflight(lock_handle)
    snapshot = install_snapshot(payloads)
    verify_installation_preflight(
        lock_handle, expected=core, snapshot=snapshot
    )
    return core, snapshot


def refresh_active_overlap_gate(
    snapshot: dict[str, object], lock_handle: object
) -> dict[str, object]:
    """Crash-resumable retirement of the pre-fix gate and activation of the new gate."""
    m9 = consumer.original_controller()
    _, new_payload, new_sha = replacement_active_gate_payload(snapshot)
    lock_receipt = verify_budget_lock(lock_handle)
    recovered_core = verify_recovered_core(lock_handle)

    def commit_journal(value: dict[str, object]) -> None:
        if verify_budget_lock(lock_handle) != lock_receipt:
            raise SystemExit("budget lock receipt drift before journal write")
        m9.atomic_root_private_json(REFRESH_JOURNAL, value)
        if verify_budget_lock(lock_handle) != lock_receipt:
            raise SystemExit("budget lock receipt drift after journal write")

    journal, bound_new_sha = read_bound_refresh_journal(
        snapshot, lock_handle, recovered_core
    )
    if bound_new_sha != new_sha:
        raise SystemExit("active-gate replacement payload changed during refresh")
    if journal is None:
        if os.path.lexists(ACTIVE_GATE_RETIRED) or os.path.lexists(ACTIVE_GATE_STAGING):
            raise SystemExit("active-gate refresh namespace is not pristine")
        old_receipt = require_inode_receipt(
            m9.OVERLAP_AUDIT_GATE, PRE_REPLACEMENT_ACTIVE_GATE_SHA256
        )
        journal = {
            "schema_version": "m9-source-prepare-py39-consumer-refresh-v1",
            "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
            "state": "PREPARED",
            "old_active": old_receipt,
            "old_active_sha256": PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            "new_active_sha256": new_sha,
            "retired_path": ACTIVE_GATE_RETIRED.as_posix(),
            "staging_path": ACTIVE_GATE_STAGING.as_posix(),
            "budget_lock": lock_receipt,
        }
        commit_journal(journal)
    else:
        validate_refresh_namespace(journal, new_sha)

    def namespace() -> tuple[bool, bool, bool]:
        return (
            os.path.lexists(m9.OVERLAP_AUDIT_GATE),
            os.path.lexists(ACTIVE_GATE_RETIRED),
            os.path.lexists(ACTIVE_GATE_STAGING),
        )

    state = str(journal.get("state"))
    active_exists, retired_exists, staging_exists = namespace()
    if state == "PREPARED":
        if not active_exists or retired_exists:
            raise SystemExit("PREPARED active-gate state mismatch")
        require_inode_receipt(
            m9.OVERLAP_AUDIT_GATE,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["old_active"],
        )
        if not staging_exists:
            if verify_budget_lock(lock_handle) != lock_receipt:
                raise SystemExit("budget lock drift before replacement staging write")
            m9.atomic_owned_durable_bytes(
                ACTIVE_GATE_STAGING,
                new_payload,
                expected_uid=0,
                expected_gid=1000,
                expected_mode=0o640,
            )
        staging_receipt = require_inode_receipt(ACTIVE_GATE_STAGING, new_sha)
        journal["staging"] = staging_receipt
        journal["state"] = "STAGED"
        commit_journal(journal)
        state = "STAGED"
    if state == "STAGED":
        active_exists, retired_exists, staging_exists = namespace()
        require_inode_receipt(ACTIVE_GATE_STAGING, new_sha, journal["staging"])
        if active_exists and not retired_exists:
            require_inode_receipt(
                m9.OVERLAP_AUDIT_GATE,
                PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
                journal["old_active"],
            )
            if verify_budget_lock(lock_handle) != lock_receipt:
                raise SystemExit("budget lock drift before old active-gate retirement")
            retired_receipt = m9.rename_d018_gate_preserving_inode(
                m9.OVERLAP_AUDIT_GATE, ACTIVE_GATE_RETIRED, journal["old_active"]
            )
            if verify_budget_lock(lock_handle) != lock_receipt:
                raise SystemExit("budget lock drift after old active-gate retirement")
        elif not active_exists and retired_exists:
            retired_receipt = require_inode_receipt(
                ACTIVE_GATE_RETIRED,
                PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
                journal["old_active"],
            )
        else:
            raise SystemExit("STAGED active-gate phase/path mismatch")
        journal["retired"] = retired_receipt
        journal["state"] = "OLD_RETIRED"
        commit_journal(journal)
        state = "OLD_RETIRED"
    if state == "OLD_RETIRED":
        active_exists, retired_exists, staging_exists = namespace()
        require_inode_receipt(
            ACTIVE_GATE_RETIRED,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["retired"],
        )
        if not active_exists and staging_exists:
            require_inode_receipt(ACTIVE_GATE_STAGING, new_sha, journal["staging"])
            if verify_budget_lock(lock_handle) != lock_receipt:
                raise SystemExit("budget lock drift before replacement activation")
            active_receipt = m9.rename_d018_gate_preserving_inode(
                ACTIVE_GATE_STAGING, m9.OVERLAP_AUDIT_GATE, journal["staging"]
            )
            if verify_budget_lock(lock_handle) != lock_receipt:
                raise SystemExit("budget lock drift after replacement activation")
        elif active_exists and not staging_exists:
            active_receipt = require_inode_receipt(
                m9.OVERLAP_AUDIT_GATE, new_sha, journal["staging"]
            )
        else:
            raise SystemExit("OLD_RETIRED active-gate phase/path mismatch")
        journal.pop("staging")
        journal["active"] = active_receipt
        journal["state"] = "ACTIVE_REPLACED"
        commit_journal(journal)
        state = "ACTIVE_REPLACED"
    if state == "ACTIVE_REPLACED":
        active_exists, retired_exists, staging_exists = namespace()
        if not active_exists or not retired_exists or staging_exists:
            raise SystemExit("ACTIVE_REPLACED active-gate phase/path mismatch")
        active_receipt = require_inode_receipt(
            m9.OVERLAP_AUDIT_GATE, new_sha, journal["active"]
        )
        retired_receipt = require_inode_receipt(
            ACTIVE_GATE_RETIRED,
            PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
            journal["retired"],
        )
        journal["state"] = "SUCCESS_COMMITTED"
        commit_journal(journal)
        state = "SUCCESS_COMMITTED"
    if state != "SUCCESS_COMMITTED":
        raise SystemExit("unsupported active-gate refresh state")
    if (
        not os.path.lexists(m9.OVERLAP_AUDIT_GATE)
        or not os.path.lexists(ACTIVE_GATE_RETIRED)
        or os.path.lexists(ACTIVE_GATE_STAGING)
    ):
        raise SystemExit("terminal active-gate namespace mismatch")
    active_receipt = require_inode_receipt(
        m9.OVERLAP_AUDIT_GATE, new_sha, journal["active"]
    )
    retired_receipt = require_inode_receipt(
        ACTIVE_GATE_RETIRED,
        PRE_REPLACEMENT_ACTIVE_GATE_SHA256,
        journal["retired"],
    )
    return {
        "active": active_receipt,
        "retired": retired_receipt,
        "journal": journal,
    }


def build_consumer_gate(
    snapshot: dict[str, object], refresh: dict[str, object],
    historical: dict[str, object],
) -> dict[str, object]:
    m9 = consumer.original_controller()
    execution_receipt, execution_gate, _ = m9.read_d018_control_json(consumer.EXECUTION_GATE)
    runtime = consumer.consumer_runtime_receipts()
    verdict_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_VERDICT
    )
    frozen_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_FROZEN_HASHES
    )
    fact_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.RECOVERY_FACT_REPORT
    )
    recovery_verdict_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.RECOVERY_IMPLEMENTATION_VERDICT
    )
    recovery_gate_receipt, recovery_gate_bytes = m9.read_strict_root_private_bytes(
        RECOVERY_GATE
    )
    recovery_transaction_receipt, recovery_transaction_bytes = (
        m9.read_strict_root_private_bytes(RECOVERY_TRANSACTION)
    )
    failure_snapshot_receipt, failure_snapshot_bytes = (
        m9.read_strict_root_private_bytes(RECOVERY_FAILURE_SNAPSHOT)
    )
    recovery_transaction = json.loads(recovery_transaction_bytes.decode("utf-8"))
    original_failure = m9.OVERLAP_TRANSACTION.read_bytes()
    if (
        recovery_transaction.get("state") != "SUCCESS_COMMITTED"
        or not isinstance(recovery_transaction.get("gate"), dict)
        or any(
            recovery_transaction["gate"].get(key) != recovery_gate_receipt[key]
            for key in ("path", "bytes", "sha256", "uid", "gid", "mode", "nlink")
        )
        or failure_snapshot_bytes != original_failure
        or failure_snapshot_receipt["sha256"]
        != hashlib.sha256(original_failure).hexdigest()
        or refresh.get("active") != runtime.get("active_overlap_gate_sha256")
    ):
        raise SystemExit("Python-3.9 recovery terminal evidence mismatch")
    return {
        "schema_version": "m9-source-prepare-py39-uid1000-consumer-gate-v1",
        "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "scope": "ALLOW_ONE_SOURCE_PREPARE_AFTER_PY39_RECOVERY",
        "verdict_path": consumer.CONSUMER_VERDICT.as_posix(),
        "verdict_sha256": verdict_receipt["sha256"],
        "frozen_hashes_path": consumer.CONSUMER_FROZEN_HASHES.as_posix(),
        "frozen_hashes_sha256": frozen_receipt["sha256"],
        "recovery_fact_report_path": consumer.RECOVERY_FACT_REPORT.as_posix(),
        "recovery_fact_report_sha256": fact_receipt["sha256"],
        "recovery_implementation_verdict_path": (
            consumer.RECOVERY_IMPLEMENTATION_VERDICT.as_posix()
        ),
        "recovery_implementation_verdict_sha256": (
            recovery_verdict_receipt["sha256"]
        ),
        "snapshot_manifest_path": consumer.SNAPSHOT_MANIFEST.as_posix(),
        "snapshot_manifest_sha256": snapshot["receipt"]["sha256"],
        "historical_execution_gate_path": consumer.EXECUTION_GATE.as_posix(),
        "historical_execution_gate_sha256": execution_receipt["sha256"],
        "historical_execution_runtime_sha256": consumer.canonical_hash(
            execution_gate["runtime"]
        ),
        "recovery_gate_sha256": recovery_gate_receipt["sha256"],
        "recovery_transaction_sha256": recovery_transaction_receipt["sha256"],
        "historical_consumer_gate_path": consumer.HISTORICAL_CONSUMER_GATE.as_posix(),
        "historical_consumer_gate_sha256": historical["consumer_gate"]["sha256"],
        "historical_bootstrap_receipt_path": (
            consumer.HISTORICAL_BOOTSTRAP_RECEIPT.as_posix()
        ),
        "historical_bootstrap_receipt_sha256": (
            historical["bootstrap_receipt"]["sha256"]
        ),
        "historical_snapshot_manifest_path": (
            consumer.HISTORICAL_SNAPSHOT_MANIFEST.as_posix()
        ),
        "historical_snapshot_manifest_sha256": (
            historical["snapshot_manifest"]["sha256"]
        ),
        "active_overlap_gate_sha256": refresh["active"]["sha256"],
        "runtime": runtime,
    }


def install_consumer_gate(gate: dict[str, object]) -> dict[str, object]:
    """Install only into a pristine path; any existing namespace is verified, not replaced."""
    m9 = consumer.original_controller()
    gate_payload = (
        json.dumps(gate, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    if os.path.lexists(consumer.CONSUMER_GATE):
        receipt, existing, existing_payload = m9.read_d018_control_json(
            consumer.CONSUMER_GATE
        )
        if existing != gate or existing_payload != gate_payload:
            raise SystemExit("existing consumer gate differs")
        return receipt
    m9.atomic_owned_durable_bytes(
        consumer.CONSUMER_GATE,
        gate_payload,
        expected_uid=0,
        expected_gid=1000,
        expected_mode=0o640,
    )
    receipt, _, _ = m9.read_d018_control_json(consumer.CONSUMER_GATE)
    return receipt


def verify_installation_guard(
    historical: dict[str, object], boundary: str
) -> None:
    """Keep full historical closure and authorization absence across every write."""
    if consumer.verify_historical_consumer_evidence() != historical:
        raise SystemExit(f"historical consumer evidence drift {boundary}")
    if os.path.lexists(consumer.SOURCE_PREPARE_AUTHORIZATION):
        raise SystemExit(f"source_prepare authorization namespace drift {boundary}")


def install_under_lock(
    payloads: dict[Path, bytes],
    historical: dict[str, object],
    lock_handle: object,
) -> dict[str, object]:
    """Run or resume the complete installer transaction under the budget lock."""
    verify_installation_guard(historical, "before snapshot installation")
    preflight, snapshot = prepare_snapshot_for_refresh(payloads, lock_handle)
    verify_installation_guard(historical, "after snapshot installation")
    verify_installation_preflight(
        lock_handle, expected=preflight, snapshot=snapshot
    )
    refresh = refresh_active_overlap_gate(snapshot, lock_handle)
    verify_installation_preflight(
        lock_handle, expected=preflight, snapshot=snapshot, refresh=refresh
    )
    verify_installation_guard(historical, "after active-gate refresh")
    gate = build_consumer_gate(snapshot, refresh, historical)
    verify_installation_preflight(
        lock_handle, expected=preflight, snapshot=snapshot, refresh=refresh
    )
    receipt = install_consumer_gate(gate)
    verify_installation_preflight(
        lock_handle, expected=preflight, snapshot=snapshot, refresh=refresh
    )
    verify_installation_guard(historical, "after consumer-gate installation")
    return receipt


def main() -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("consumer snapshot installation requires root")
    if (
        Path(sys.executable).resolve(strict=True) != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
    ):
        raise SystemExit("consumer snapshot installation requires frozen Python -I -S -B")
    try:
        trusted_installer = TRUSTED_INSTALLER.resolve(strict=True)
    except OSError as exc:
        raise SystemExit("trusted consumer bootstrap is not installed") from exc
    if RUNNING_INSTALLER != trusted_installer:
        raise SystemExit("consumer installer must run from the trusted bootstrap")
    frozen_payload = stable_source_bytes(consumer.CONSUMER_FROZEN_HASHES)
    frozen_sha256, verdict_bytes, report_bytes = verify_trusted_bootstrap(frozen_payload)
    payloads = verify_authorized_sources(frozen_sha256, verdict_bytes, report_bytes)
    consumer._M9 = load_frozen_original_controller(
        payloads[consumer.PROJECT_ORIGINAL_CONTROLLER]
    )
    if os.path.lexists(consumer.SOURCE_PREPARE_AUTHORIZATION):
        raise SystemExit("post-install source_prepare authorization must remain absent")
    historical = consumer.verify_historical_consumer_evidence()
    m9 = consumer.original_controller()
    lock_flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    lock_descriptor = os.open(m9.LOCK_PATH, lock_flags)
    with os.fdopen(lock_descriptor, "r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        receipt = install_under_lock(payloads, historical, lock_handle)
    print(json.dumps({"status": "consumer_gate_installed", "receipt": receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
